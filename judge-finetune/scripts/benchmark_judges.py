#!/usr/bin/env python3
"""
Comparative benchmark of LLM-as-a-Judge variants on the golden set.

Variants and comparison pairs are DECLARED in configs/variants.json, never inferred
from the variant list. Every variant is queried through an OpenAI-compatible
/v1/chat/completions endpoint (mlx_lm.server locally, one variant at a time).

Primary metric (PREENREGISTREMENT §4): strict verdict accuracy on the golden set,
one verdict per item by majority vote over the passes. The primary comparison
(§5) is tested by exact McNemar with a paired percentile bootstrap on the
accuracy difference, and the conclusion follows §7's table -- nothing else in
this report concludes anything.

Secondary, all declared as such in §6 and powerless over the decision:
  1. Cohen's kappa + F1 (positive class = FAIL), descriptive since the 2026-09-21 amendment
  2. Verbosity bias    false-PASS rate on verbose hidden-bug cases vs. concise FAIL cases (+ verbose PASS control)
  3. Repeatability     verdict / full-decision stability over N passes at temperature T
  4. Quality/resources latency, tokens, cost per 1000 judgments

Usage:
  python3 scripts/benchmark_judges.py --config configs/variants.json --golden data/golden/test.jsonl
  python3 scripts/benchmark_judges.py ... --variants 14B-baseline,14B-finetuned   # run a subset
  python3 scripts/benchmark_judges.py ... --report-only                           # recompute from cached runs

Raw generations are cached in <out>/runs/<variant>.jsonl; re-running resumes where it stopped.
No third-party dependencies.
"""

import argparse
import json
import math
import os
import random
import re
import statistics
import sys
import time
import urllib.error
import urllib.request
from collections import Counter
from pathlib import Path

LABELS = ("PASS", "FAIL")
INVALID = "INVALID"


def check_names(judgment):
    """Noms des contrôles atomiques d'un jugement. Ils varient selon la tâche."""
    checks = judgment.get("checks") if isinstance(judgment, dict) else None
    return list(checks) if isinstance(checks, dict) else []


# ── Golden set ────────────────────────────────────────────────────────────────

def extract_judgment(text):
    """Lenient parse: last JSON object in the text that carries a verdict. Returns dict or None."""
    decoder = json.JSONDecoder()
    idx = text.rfind("{")
    while idx >= 0:
        try:
            obj, _ = decoder.raw_decode(text[idx:])
            if isinstance(obj, dict) and obj.get("verdict") in LABELS:
                return obj
        except json.JSONDecodeError:
            pass
        idx = text.rfind("{", 0, idx)
    return None


def is_strict_format(text):
    """Thinking block first, then exactly one JSON object with the expected keys and types."""
    text = text.strip()
    if not text.startswith("<thinking>") or "</thinking>" not in text:
        return False
    tail = text.split("</thinking>", 1)[1].strip()
    try:
        obj = json.loads(tail)
    except json.JSONDecodeError:
        return False
    return (
        isinstance(obj, dict)
        and list(obj) == ["checks", "verdict", "reason"]
        and isinstance(obj["checks"], dict)
        and bool(obj["checks"])
        and all(isinstance(v, bool) for v in obj["checks"].values())
        and obj["verdict"] in LABELS
        and isinstance(obj["reason"], str)
    )


def load_golden(path):
    items = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            ex = json.loads(line)
            system, user, assistant = ex["messages"]
            gold = extract_judgment(assistant["content"])
            if gold is None:
                sys.exit(f"[ERROR] golden example {ex['meta']['id']} has no parseable judgment")
            items.append({
                "id": ex["meta"]["id"],
                "meta": ex["meta"],
                "prompt": [system, user],
                "gold": gold,
            })
    return items


# ── Passe « format normalisé » (PREENREGISTREMENT, amendement du 2026-09-19) ──
#
# Le benchmark est rejoué sur des réponses dépouillées de leur Markdown, et
# l'écart entre les deux passes mesure la part de forme dans le score du juge.
# C'est une mesure de la fuite résiduelle, publiée telle quelle plutôt que
# poursuivie par un nettoyage sans fin du corpus.

DEB_SORTIE = "### SORTIE À ÉVALUER"
FIN_SORTIE = "### CRITÈRES DE VALIDATION"

# L'amendement nomme quatre constructions, et le dépouillement s'y tient :
# titres, puces, gras, tableaux. Sont délibérément CONSERVÉS — les retirer
# dépasserait le transformation déclarée, et pour les deux derniers altérerait
# ce qui est jugé plutôt que sa forme :
#   listes numérotées, italiques, blocs de code délimités, code inline.
# Le code inline marque des identifiants dans 41 des 50 sorties du golden : il
# relève du fond.
FENCE = re.compile(r"^```.*?^```", re.M | re.S)
TITRE = re.compile(r"^#{1,6}[ \t]+", re.M)
PUCE = re.compile(r"^[ \t]*[-*][ \t]+", re.M)
GRAS = re.compile(r"\*\*([^*\n]+)\*\*")
LIGNE_TABLEAU = re.compile(r"^[ \t]*\|.*\|[ \t]*$")
SEP_TABLEAU = re.compile(r"^[ \t]*\|[\s:|-]+\|[ \t]*$")


def _depouille_segment(texte):
    lignes = []
    for ligne in texte.split("\n"):
        if SEP_TABLEAU.match(ligne):
            continue  # la ligne de séparation n'a pas de contenu
        if LIGNE_TABLEAU.match(ligne):
            cellules = [c.strip() for c in ligne.strip().strip("|").split("|")]
            ligne = " ; ".join(c for c in cellules if c)
        lignes.append(ligne)
    texte = "\n".join(lignes)
    texte = TITRE.sub("", texte)
    texte = PUCE.sub("", texte)
    return GRAS.sub(r"\1", texte)


def strip_markdown(texte):
    """Dépouille titres, puces, gras et tableaux, hors blocs de code délimités.

    Les blocs ``` sont recopiés verbatim : une ligne commençant par `-` ou `|`
    y est du code, pas une puce ni un tableau. Le golden set n'en contient
    aucun cas aujourd'hui — vérifié, 0 bloc sur 24 — mais la garantie ne doit
    pas dépendre de cette vérification.
    """
    morceaux, fin = [], 0
    for m in FENCE.finditer(texte):
        morceaux.append(_depouille_segment(texte[fin:m.start()]))
        morceaux.append(m.group(0))
        fin = m.end()
    morceaux.append(_depouille_segment(texte[fin:]))
    return "".join(morceaux)


def normalise_golden(golden):
    """Golden dépouillé, moins les items dont la requête impose un format.

    L'exclusion est définie par un **prédicat vérifiable** — porter le contrôle
    `format_impose` — et non par un décompte écrit à la main : l'amendement du
    2026-09-19 en annonçait 5, le corpus en porte 6 (correction du 2026-09-21).
    Sur ces items la forme *est* le critère, et les dépouiller les rendrait
    injugeables.
    """
    exclus = sorted(g["id"] for g in golden if "format_impose" in (g["gold"].get("checks") or {}))
    hors = set(exclus)
    out = []
    for g in golden:
        if g["id"] in hors:
            continue
        system, user = g["prompt"]
        avant, reste = user["content"].split(DEB_SORTIE, 1)
        corps, apres = reste.split(FIN_SORTIE, 1)
        contenu = avant + DEB_SORTIE + strip_markdown(corps) + FIN_SORTIE + apres
        out.append({**g, "prompt": [system, {**user, "content": contenu}]})
    return out, exclus


# ── Inference ─────────────────────────────────────────────────────────────────

def chat_completion(variant, messages, temperature, max_tokens, timeout, retries=3):
    requete = {
        "model": variant["model"],
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    # L'adaptateur voyage dans le corps de la requête, pas seulement par
    # `--adapter-path` au lancement du serveur. Constaté le 2026-09-24 : le banc
    # des trois variantes 14B a tourné avec `--adapter-path adapters/14b-judge-ckpt200`
    # et mlx_lm.server a néanmoins répondu avec le modèle de base — sans erreur,
    # sans avertissement. `14B-finetuned` a donc rendu 0 % de JSON exploitable et le
    # rapport a conclu « le fine-tuning dégrade la justesse de -76 % », qui ne
    # mesurait rien. Chargé en processus via mlx_lm.load(adapter_path=...), le même
    # adaptateur rend le format d'entraînement exact. Le même piège avait déjà été
    # corrigé côté Java (RagContextJudge) sans être reporté ici.
    if variant.get("serve_adapter"):
        requete["adapters"] = variant["serve_adapter"]
    body = json.dumps(requete).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if variant.get("api_key_env"):
        key = os.environ.get(variant["api_key_env"])
        if not key:
            sys.exit(f"[ERROR] env var {variant['api_key_env']} is not set for variant {variant['name']}")
        headers["Authorization"] = f"Bearer {key}"
    url = variant["base_url"].rstrip("/") + "/chat/completions"

    for attempt in range(1, retries + 1):
        start = time.perf_counter()
        try:
            req = urllib.request.Request(url, data=body, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                payload = json.loads(resp.read())
            latency = time.perf_counter() - start
            usage = payload.get("usage") or {}
            return {
                "text": payload["choices"][0]["message"]["content"] or "",
                "latency_s": latency,
                "prompt_tokens": usage.get("prompt_tokens"),
                "completion_tokens": usage.get("completion_tokens"),
                "error": None,
            }
        except (urllib.error.URLError, TimeoutError, KeyError, json.JSONDecodeError) as e:
            if attempt == retries:
                return {"text": "", "latency_s": time.perf_counter() - start,
                        "prompt_tokens": None, "completion_tokens": None, "error": repr(e)}
            time.sleep(2 ** attempt)


def messages_for(variant, item):
    """Invite envoyée à une variante : celle du corpus, éventuellement suffixée.

    `14B-baseline-conventions` ne diffère de `14B-baseline-nu` que par ce suffixe,
    les conventions de PROTOCOLE.md reprises mot pour mot. Le corps de l'invite
    reste celui du corpus — qui est aussi celui vu à l'entraînement : le remplacer
    ferait mesurer un changement d'invite autant qu'un fine-tuning.
    """
    system, user = item["prompt"]
    suffix = variant.get("system_suffix") or ""
    if not suffix and variant.get("system_suffix_file"):
        suffix = Path(variant["system_suffix_file"]).read_text(encoding="utf-8")
    if not suffix.strip():
        return [system, user]
    fondu = system["content"].rstrip() + "\n\n" + suffix.strip()
    return [{"role": system["role"], "content": fondu}, user]


def sonde_adaptateur(variant, golden, args):
    """Preuve positive que l'adaptateur est bien en vigueur, avant de dépenser une heure.

    Une variante fine-tunée servie sans son adaptateur ne produit pas d'erreur : elle
    répond en modèle de base, avec des clés plates dans une clôture markdown, et le
    banc la note 0 % en la présentant comme un effet du fine-tuning. Le contrôle est
    donc une sonde et non une assertion de style : le format imbriqué
    `{"checks": {...}, "verdict": ...}` n'apparaît jamais chez le modèle de base et
    toujours chez l'adaptateur, ce qui en fait un discriminant fiable sur un seul appel.
    """
    if not variant.get("serve_adapter"):
        return
    item = golden[0]
    r = chat_completion(variant, messages_for(variant, item),
                        args.temperature, args.max_tokens, args.timeout)
    texte = r.get("text") or ""
    if r.get("error"):
        sys.exit(f"[ERREUR] {variant['name']} : la sonde d'adaptateur a échoué — {r['error']}")
    if '"checks"' not in texte or '"verdict"' not in texte:
        sys.exit(
            f"[ERREUR] {variant['name']} : l'adaptateur {variant['serve_adapter']} n'est pas en vigueur.\n"
            f"  La sonde a rendu une sortie sans `checks` ni `verdict` imbriqués, c'est-à-dire du modèle de base.\n"
            f"  Le banc s'arrête : le laisser tourner produirait un 0 % attribué à tort au fine-tuning.\n"
            f"  Sortie reçue (200 premiers caractères) : {texte[:200]!r}"
        )
    print(f"[{variant['name']}] sonde d'adaptateur : format d'entraînement confirmé", flush=True)


def run_variant(variant, golden, args, runs_dir, suffixe=""):
    # Le suffixe sépare les caches des deux passes : la passe « format normalisé »
    # interroge les mêmes items avec des sorties dépouillées, et mélanger les deux
    # dans un même fichier rendrait l'écart mesuré incohérent sans rien signaler.
    cache_path = runs_dir / f"{variant['name']}{suffixe}.jsonl"
    done = set()
    if cache_path.exists():
        with cache_path.open(encoding="utf-8") as f:
            for line in f:
                row = json.loads(line)
                if row["error"] is None:
                    done.add((row["pass"], row["id"]))

    todo = [(p, item) for p in range(1, args.passes + 1) for item in golden if (p, item["id"]) not in done]
    if not todo:
        print(f"[{variant['name']}] cached, nothing to run")
        return
    print(f"[{variant['name']}] {len(todo)} generations to run ({len(done)} cached)")
    sonde_adaptateur(variant, golden, args)
    with cache_path.open("a", encoding="utf-8") as f:
        for n, (p, item) in enumerate(todo, 1):
            result = chat_completion(variant, messages_for(variant, item),
                                     args.temperature, args.max_tokens, args.timeout)
            f.write(json.dumps({"pass": p, "id": item["id"], **result}, ensure_ascii=False) + "\n")
            f.flush()
            status = "ERR" if result["error"] else f"{result['latency_s']:.1f}s"
            print(f"  pass {p} {n}/{len(todo)} {item['id']} {status}", flush=True)


def load_runs(variant, golden, passes, runs_dir, suffixe=""):
    """Returns {pass: {id: row}} keeping the last successful row per (pass, id)."""
    runs = {p: {} for p in range(1, passes + 1)}
    path = runs_dir / f"{variant['name']}{suffixe}.jsonl"
    if not path.exists():
        return runs
    ids = {item["id"] for item in golden}
    with path.open(encoding="utf-8") as f:
        for line in f:
            row = json.loads(line)
            if row["pass"] in runs and row["id"] in ids and (row["error"] is None or row["id"] not in runs[row["pass"]]):
                judgment = extract_judgment(row["text"]) if row["error"] is None else None
                row["judgment"] = judgment
                row["verdict"] = judgment["verdict"] if judgment else INVALID
                row["strict_format"] = row["error"] is None and is_strict_format(row["text"])
                runs[row["pass"]][row["id"]] = row
    return runs


# ── Metrics ───────────────────────────────────────────────────────────────────

def cohen_kappa(gold, pred):
    """Unweighted Cohen's kappa. INVALID predictions are a third category (always a disagreement)."""
    n = len(gold)
    if n == 0:
        return float("nan")
    categories = set(gold) | set(pred)
    observed = sum(g == p for g, p in zip(gold, pred)) / n
    gc, pc = Counter(gold), Counter(pred)
    expected = sum(gc[c] * pc[c] for c in categories) / (n * n)
    if expected == 1.0:
        return 1.0 if observed == 1.0 else 0.0
    return (observed - expected) / (1 - expected)


def f1(gold, pred, positive):
    tp = sum(g == positive and p == positive for g, p in zip(gold, pred))
    fp = sum(g != positive and p == positive for g, p in zip(gold, pred))
    fn = sum(g == positive and p != positive for g, p in zip(gold, pred))
    return 0.0 if tp == 0 else 2 * tp / (2 * tp + fp + fn)


def majority(verdicts):
    top, count = Counter(verdicts).most_common(1)[0]
    return top if count > len(verdicts) / 2 else INVALID


def percentile(values, q):
    if not values:
        return float("nan")
    ordered = sorted(values)
    k = (len(ordered) - 1) * q
    lo, hi = int(k), min(int(k) + 1, len(ordered) - 1)
    return ordered[lo] + (ordered[hi] - ordered[lo]) * (k - lo)


def mean_kappa(golden, runs, indices):
    gold = [golden[i]["gold"]["verdict"] for i in indices]
    kappas = []
    for rows in runs.values():
        pred = [rows[golden[i]["id"]]["verdict"] if golden[i]["id"] in rows else INVALID for i in indices]
        kappas.append(cohen_kappa(gold, pred))
    return statistics.fmean(kappas)


def bootstrap_ci(stat, n, iterations, rng):
    samples = sorted(stat([rng.randrange(n) for _ in range(n)]) for _ in range(iterations))
    return percentile(samples, 0.025), percentile(samples, 0.975)


def false_pass_rate(golden, runs, selector):
    """Share of judgments (over all passes) that output PASS on gold-FAIL items matching selector."""
    items = [g for g in golden if g["gold"]["verdict"] == "FAIL" and selector(g)]
    judged = [rows[g["id"]]["verdict"] for rows in runs.values() for g in items if g["id"] in rows]
    return (sum(v == "PASS" for v in judged) / len(judged) if judged else float("nan")), len(items)


def evaluate(variant, golden, runs, args, rng):
    ids = [g["id"] for g in golden]
    gold = [g["gold"]["verdict"] for g in golden]
    missing = sum(1 for rows in runs.values() for i in ids if i not in rows)

    per_pass = []
    for p, rows in sorted(runs.items()):
        pred = [rows[i]["verdict"] if i in rows else INVALID for i in ids]
        per_pass.append({
            "pass": p,
            "kappa": cohen_kappa(gold, pred),
            "f1_fail": f1(gold, pred, "FAIL"),
            "macro_f1": (f1(gold, pred, "FAIL") + f1(gold, pred, "PASS")) / 2,
            "accuracy": sum(g == q for g, q in zip(gold, pred)) / len(gold),
        })

    all_rows = [rows[i] for rows in runs.values() for i in ids if i in rows]
    verdicts_by_item = [[runs[p][i]["verdict"] if i in runs[p] else INVALID for p in runs] for i in ids]
    majority_pred = [majority(v) for v in verdicts_by_item]

    def decision(row):
        j = row.get("judgment")
        if j is None:
            return None
        return tuple(sorted((j.get("checks") or {}).items())) + (j["verdict"],)

    verdict_stable = sum(1 for v in verdicts_by_item if INVALID not in v and len(set(v)) == 1)
    decision_stable = 0
    for i in ids:
        decisions = [decision(runs[p][i]) if i in runs[p] else None for p in runs]
        if None not in decisions and len(set(decisions)) == 1:
            decision_stable += 1

    criteria_acc = {}
    all_names = []
    for g in golden:
        for name in check_names(g["gold"]):
            if name not in all_names:
                all_names.append(name)
    for k in all_names:
        pairs = []
        for rows in runs.values():
            for g in golden:
                gold_checks = g["gold"].get("checks") or {}
                if k not in gold_checks or g["id"] not in rows:
                    continue
                judgment = rows[g["id"]]["judgment"]
                if judgment is None:
                    continue
                prediction = (judgment.get("checks") or {}).get(k)
                # Un contrôle que la variante n'a pas émis n'est pas un désaccord : il n'y a
                # rien à comparer. Compter la paire quand même faisait rendre 0 % sur les
                # treize contrôles à `14B-baseline-conventions`, qui rend un verdict valide
                # mais des clés plates, sans objet `checks` (0 sur 150 générations). Lu dans
                # un tableau, ce zéro se confond avec un désaccord total alors qu'il ne
                # mesure qu'une absence — déjà dite par `format strict = 0 %`.
                if not isinstance(prediction, bool):
                    continue
                pairs.append((gold_checks[k], prediction))
        criteria_acc[k] = sum(a == b for a, b in pairs) / len(pairs) if pairs else float("nan")

    # Posture monde fermé, en comptes bruts. Le golden set ne porte qu'une dizaine d'items RAG :
    # un κ calculé dessus aurait un IC95 couvrant presque tout le domaine. On rapporte donc le
    # nombre de verdicts corrects et on nomme les items ratés, ce qui reste lisible à cette taille.
    rag_idx = [i for i, g in enumerate(golden) if g["meta"]["task"].startswith("RAG_")]
    rag_missed = [{"id": golden[i]["id"], "task": golden[i]["meta"]["task"],
                   "gold": gold[i], "pred": majority_pred[i]}
                  for i in rag_idx if majority_pred[i] != gold[i]]

    # PREENREGISTREMENT §6.4 : justesse sur la seule strate `limite`, où se concentre
    # la difficulté. Secondaire déclarée, sans pouvoir de décision. L'effectif est
    # publié avec le chiffre : le golden n'en porte qu'une dizaine, donc il indique
    # une tendance et ne départage rien.
    limite_idx = [i for i, g in enumerate(golden) if g["meta"]["cas"] == "limite"]
    limite_correct = sum(1 for i in limite_idx if majority_pred[i] == gold[i])

    verbose_fpr, n_verbose_fail = false_pass_rate(golden, runs, lambda g: g["meta"]["verbeux"])
    concise_fpr, n_concise_fail = false_pass_rate(golden, runs, lambda g: not g["meta"]["verbeux"])
    verbose_pass_items = [g for g in golden if g["gold"]["verdict"] == "PASS" and g["meta"]["verbeux"]]
    verbose_pass_judged = [rows[g["id"]]["verdict"] for rows in runs.values() for g in verbose_pass_items if g["id"] in rows]
    verbose_false_fail = (sum(v == "FAIL" for v in verbose_pass_judged) / len(verbose_pass_judged)
                          if verbose_pass_judged else float("nan"))

    latencies = [r["latency_s"] for r in all_rows if r["error"] is None]
    completion_tokens = [r["completion_tokens"] for r in all_rows if r.get("completion_tokens")]
    mean_latency = statistics.fmean(latencies) if latencies else float("nan")

    n = len(golden)
    kappa_ci = bootstrap_ci(lambda idx: mean_kappa(golden, runs, idx), n, args.bootstrap, rng)
    kappas = [p["kappa"] for p in per_pass]

    return {
        "name": variant["name"],
        "size": variant["size"],
        "fine_tuned": variant["fine_tuned"],
        "n_items": n,
        "missing_generations": missing,
        "kappa_mean": statistics.fmean(kappas),
        "kappa_sd": statistics.stdev(kappas) if len(kappas) > 1 else 0.0,
        "kappa_ci95": kappa_ci,
        "kappa_majority": cohen_kappa(gold, majority_pred),
        "f1_fail_mean": statistics.fmean(p["f1_fail"] for p in per_pass),
        "macro_f1_mean": statistics.fmean(p["macro_f1"] for p in per_pass),
        "accuracy_mean": statistics.fmean(p["accuracy"] for p in per_pass),
        "per_pass": per_pass,
        "criteria_accuracy": criteria_acc,
        "rag_n": len(rag_idx),
        "rag_correct": len(rag_idx) - len(rag_missed),
        "rag_by_task": dict(Counter(golden[i]["meta"]["task"] for i in rag_idx)),
        "rag_missed": rag_missed,
        "limite_n": len(limite_idx),
        "limite_correct": limite_correct,
        "limite_accuracy": limite_correct / len(limite_idx) if limite_idx else float("nan"),
        "json_parse_rate": sum(r["judgment"] is not None for r in all_rows) / len(all_rows) if all_rows else 0.0,
        "strict_format_rate": sum(r["strict_format"] for r in all_rows) / len(all_rows) if all_rows else 0.0,
        "verdict_stability": verdict_stable / n,
        "decision_stability": decision_stable / n,
        "verbose_fail_false_pass_rate": verbose_fpr,
        "concise_fail_false_pass_rate": concise_fpr,
        "verbosity_bias_gap": verbose_fpr - concise_fpr,
        "n_verbose_fail": n_verbose_fail,
        "n_concise_fail": n_concise_fail,
        "verbose_pass_false_fail_rate": verbose_false_fail,
        "n_verbose_pass": len(verbose_pass_items),
        "latency_p50_s": percentile(latencies, 0.5),
        "latency_p95_s": percentile(latencies, 0.95),
        "completion_tokens_mean": statistics.fmean(completion_tokens) if completion_tokens else float("nan"),
        "tokens_per_s": (statistics.fmean(completion_tokens) / mean_latency
                         if completion_tokens and mean_latency else float("nan")),
        "ram_gb": variant.get("ram_gb"),
        "cost_per_1k_judgments_usd": mean_latency * 1000 / 3600 * variant.get("cost_per_hour_usd", 0.0),
        "_runs": runs,
    }


# NOTE : `paired_delta`, l'écart apparié sur le κ, a été supprimé le 2026-09-21.
# C'était la statistique de décision que l'amendement du même jour a destituée.
# La laisser en place, inutilisée, aurait suffi à la rebrancher par inadvertance.
# Le κ reste rapporté comme descriptif ; il ne sert plus à comparer deux variantes.


# ── Métrique principale : justesse stricte du verdict (PREENREGISTREMENT §4) ──
#
# Un verdict par item, obtenu par vote majoritaire sur les passes. Ce choix n'est
# pas cosmétique : McNemar exige un résultat binaire apparié par item, et la §6.5
# mesure déjà la répétabilité séparément. Moyenner la justesse sur les passes
# mélangerait les deux. Un item sans majorité est INVALID, donc compté faux.

def majority_verdicts(golden, runs):
    out = []
    for g in golden:
        votes = [runs[p][g["id"]]["verdict"] if g["id"] in runs[p] else INVALID for p in runs]
        out.append(majority(votes))
    return out


def strict_accuracy(gold, pred):
    return sum(g == p for g, p in zip(gold, pred)) / len(gold) if gold else float("nan")


def mcnemar_exact(gold, pred_a, pred_b):
    """McNemar exact bilatéral (PREENREGISTREMENT §5), α = 0,05.

    b = items où A a juste et B faux ; c = l'inverse. Seules ces paires
    discordantes portent de l'information — à n = 50, leur nombre est le vrai
    déterminant de la puissance, et il est publié avec le p.
    """
    b = sum(1 for g, a, x in zip(gold, pred_a, pred_b) if a == g and x != g)
    c = sum(1 for g, a, x in zip(gold, pred_a, pred_b) if a != g and x == g)
    n = b + c
    if n == 0:
        return b, c, 1.0
    queue = sum(math.comb(n, i) for i in range(min(b, c) + 1)) / (2 ** n)
    return b, c, min(1.0, 2 * queue)


def paired_accuracy_delta(golden, runs_a, runs_b, iterations, rng):
    """Bootstrap apparié par percentiles sur la différence de justesse (B − A)."""
    gold = [g["gold"]["verdict"] for g in golden]
    pa, pb = majority_verdicts(golden, runs_a), majority_verdicts(golden, runs_b)
    full = strict_accuracy(gold, pb) - strict_accuracy(gold, pa)

    def stat(idx):
        return (strict_accuracy([gold[i] for i in idx], [pb[i] for i in idx])
                - strict_accuracy([gold[i] for i in idx], [pa[i] for i in idx]))

    lo, hi = bootstrap_ci(stat, len(golden), iterations, rng)
    return full, lo, hi


# ── Decision & report ─────────────────────────────────────────────────────────

def qualification(m, args):
    """Recevabilité opérationnelle — PAS une règle de conclusion.

    La §7 du pré-enregistrement ne déclare aucun seuil : elle tranche sur la seule
    comparaison principale. Ce filtre dit autre chose, et de purement pratique —
    une variante qui ne rend pas du JSON exploitable n'est pas utilisable en
    production, quelle que soit sa justesse. Aucun seuil en κ : le κ est descriptif
    depuis l'amendement du 2026-09-21.
    """
    reasons = []
    if m["verdict_stability"] < args.min_stability:
        reasons.append(f"stabilité {m['verdict_stability']:.0%} < {args.min_stability:.0%}")
    if m["strict_format_rate"] < args.min_format:
        reasons.append(f"format strict {m['strict_format_rate']:.0%} < {args.min_format:.0%}")
    if m["n_verbose_fail"] and m["verbose_fail_false_pass_rate"] > args.max_verbose_fpr:
        reasons.append(f"faux PASS verbeux {m['verbose_fail_false_pass_rate']:.0%} > {args.max_verbose_fpr:.0%}")
    return reasons


def fmt(x, pct=False, digits=2):
    if isinstance(x, float) and x != x:
        return "n/a"
    return f"{x:.0%}" if pct else f"{x:.{digits}f}"


def build_report(metrics, golden, args, rng, config, selected_names, passe_format=None):
    lines = ["# Benchmark LLM-as-a-Judge — 14B vs 32B", ""]
    lines.append(f"Golden set : {len(golden)} items | passes : {args.passes} | température : {args.temperature} | "
                 f"bootstrap : {args.bootstrap}")
    verdicts = Counter(g["gold"]["verdict"] for g in golden)
    lines.append(f"Répartition gold : PASS {verdicts['PASS']} / FAIL {verdicts['FAIL']}")
    lines.append("")

    lines += ["## 1. Alignement humain", "",
              "| Variante | κ moyen ± sd | IC95 κ | κ vote majoritaire | F1 (FAIL) | Macro-F1 | Exactitude | JSON parsable |",
              "|---|---|---|---|---|---|---|---|"]
    for m in metrics:
        lines.append(f"| {m['name']} | {fmt(m['kappa_mean'])} ± {fmt(m['kappa_sd'])} | "
                     f"[{fmt(m['kappa_ci95'][0])}, {fmt(m['kappa_ci95'][1])}] | {fmt(m['kappa_majority'])} | "
                     f"{fmt(m['f1_fail_mean'])} | {fmt(m['macro_f1_mean'])} | {fmt(m['accuracy_mean'], pct=True)} | "
                     f"{fmt(m['json_parse_rate'], pct=True)} |")
    crit_names = list(metrics[0]["criteria_accuracy"]) if metrics else []
    if crit_names:
        lines += ["", "Accord par contrôle atomique (sur les jugements parsables) :", "",
                  "| Variante | " + " | ".join(crit_names) + " |", "|---|" + "---|" * len(crit_names)]
        for m in metrics:
            lines.append(f"| {m['name']} | "
                         + " | ".join(fmt(m["criteria_accuracy"].get(k, float("nan")), pct=True) for k in crit_names)
                         + " |")

    if metrics and metrics[0].get("rag_n"):
        n_rag = metrics[0]["rag_n"]
        ventil = ", ".join(f"{k} {v}" for k, v in sorted(metrics[0]["rag_by_task"].items()))
        lines += ["", f"Posture monde fermé — {n_rag} items RAG du golden set ({ventil}), en comptes bruts.",
                  "Pas de κ sur ce sous-ensemble : à cette taille son IC95 couvrirait presque tout le "
                  "domaine (voir PROTOCOLE.md, section Métriques).", "",
                  "| Variante | Verdicts corrects (vote majoritaire) | Items ratés |",
                  "|---|---|---|"]
        for m in metrics:
            missed = m.get("rag_missed") or []
            detail = ", ".join(f"{x['id']} ({x['gold']} → {x['pred']})" for x in missed) or "—"
            lines.append(f"| {m['name']} | {m['rag_correct']}/{n_rag} | {detail} |")

    if metrics and metrics[0].get("limite_n"):
        n_lim = metrics[0]["limite_n"]
        lines += ["", f"Justesse sur la seule strate `limite` — {n_lim} items du golden set, là où se "
                  "concentre la difficulté (PREENREGISTREMENT §6.4). Secondaire déclarée, **sans pouvoir "
                  "de décision** ; à cet effectif elle indique une tendance et ne départage rien.", "",
                  "| Variante | Justesse sur `limite` |", "|---|---|"]
        for m in metrics:
            lines.append(f"| {m['name']} | {m['limite_correct']}/{n_lim} = {fmt(m['limite_accuracy'], pct=True)} |")

    if passe_format:
        gn, mn, exclus = passe_format["golden"], passe_format["metrics"], passe_format["exclus"]
        par_nom = {m["name"]: m for m in mn}
        ids_com = [g["id"] for g in gn]
        or_com = [g["gold"]["verdict"] for g in gn]
        # La clause d'exclusion disparaît quand il n'y a rien à exclure : sans ce
        # garde, un corpus sans `format_impose` produisait « 0 exclus car leur requête
        # impose un format — la forme y *est* le critère : . », scorie d'une liste vide
        # dans un rapport publié.
        clause = ("" if not exclus else
                  f", {len(exclus)} exclus car leur requête impose un format — la forme y *est* "
                  f"le critère : {', '.join(exclus)}")
        lines += ["", "### Passe « format normalisé » — part de forme dans le score", "",
                  f"Mêmes items, sorties dépouillées de leur Markdown (titres, puces, gras, tableaux). "
                  f"**{len(ids_com)} items comparés des deux côtés**{clause}.", "",
                  "La justesse de la passe normale est **recalculée sur ces mêmes items**, sans quoi "
                  "l'écart confondrait l'exclusion avec l'effet de forme.", "",
                  "| Variante | Formaté | Dépouillé | Écart |", "|---|---|---|---|"]
        for m in metrics:
            n = par_nom.get(m["name"])
            if not n:
                lines.append(f"| {m['name']} | — | — | passe absente |")
                continue
            # Les deux passes portent exactement les mêmes items : le golden
            # dépouillé sert donc d'index dans les deux jeux de runs, et la passe
            # formatée est bien recalculée sur ces items-là, pas sur les 50.
            pf = majority_verdicts(gn, m["_runs"])
            pn = majority_verdicts(gn, n["_runs"])
            af, an = strict_accuracy(or_com, pf), strict_accuracy(or_com, pn)
            # L'écart est annoncé en POINTS : af et an sont des fractions, donc
            # sans le facteur 100 la colonne afficherait des centièmes de point.
            lines.append(f"| {m['name']} | {af:.1%} | {an:.1%} | {(an - af) * 100:+.1f} pt |")
        lines += ["", "Un écart proche de zéro est une **preuve positive** que le juge a appris autre "
                  "chose que la forme ; un écart marqué mesure la fuite résiduelle, publiée telle "
                  "quelle plutôt que poursuivie par un nettoyage sans fin du corpus."]

        # Limite calculée sur les données présentes, jamais recopiée : l'exclusion
        # n'est pas un tirage quelconque. Un item dont la requête impose un format
        # est presque par construction un cas `limite`, la contrainte de forme
        # étant souvent le seul contrôle qui sépare PASS de FAIL.
        lim_t = sum(1 for g in golden if g["meta"]["cas"] == "limite")
        lim_c = sum(1 for g in gn if g["meta"]["cas"] == "limite")
        fail_t = sum(1 for g in golden if g["gold"]["verdict"] == "FAIL")
        fail_c = sum(1 for g in gn if g["gold"]["verdict"] == "FAIL")
        if lim_t and lim_c < lim_t:
            lines += ["", f"⚠️ **L'exclusion corrèle avec la difficulté.** La strate `limite` passe de "
                      f"{lim_t} à {lim_c} items, soit {(lim_t - lim_c) / lim_t:.0%} de la strate la plus "
                      f"difficile retirée, et la part de FAIL de {fail_t / len(golden):.0%} à "
                      f"{fail_c / len(gn):.0%}. La comparaison reste appariée sur des items identiques "
                      f"des deux côtés, donc l'écart est interprétable ; mais il est mesuré sur un "
                      f"sous-ensemble **amputé des items où la forme compte le plus**, et son niveau "
                      f"absolu porte sur un golden plus facile que le complet."]

    lines += ["", "## 2. Résistance au biais de verbosité", "",
              "| Variante | Faux PASS verbeux+bug (n) | Faux PASS concis+bug (n) | Écart (biais) | Faux FAIL verbeux corrects (n) |",
              "|---|---|---|---|---|"]
    for m in metrics:
        lines.append(f"| {m['name']} | {fmt(m['verbose_fail_false_pass_rate'], pct=True)} ({m['n_verbose_fail']}) | "
                     f"{fmt(m['concise_fail_false_pass_rate'], pct=True)} ({m['n_concise_fail']}) | "
                     f"{fmt(m['verbosity_bias_gap'] * 100, digits=0)} pts | "
                     f"{fmt(m['verbose_pass_false_fail_rate'], pct=True)} ({m['n_verbose_pass']}) |")

    lines += ["", f"## 3. Répétabilité ({args.passes} passe{'s' if args.passes > 1 else ''}, T={args.temperature})", "",
              "| Variante | Stabilité verdict | Stabilité décision complète | Format strict | Générations manquantes |",
              "|---|---|---|---|---|"]
    for m in metrics:
        ok = "✅" if m["verdict_stability"] >= args.min_stability else "❌"
        lines.append(f"| {m['name']} | {fmt(m['verdict_stability'], pct=True)} {ok} | "
                     f"{fmt(m['decision_stability'], pct=True)} | {fmt(m['strict_format_rate'], pct=True)} | "
                     f"{m['missing_generations']} |")

    lines += ["", "## 4. Qualité / ressources", "",
              "| Variante | RAM modèle | Latence p50 | Latence p95 | Tokens générés | Débit | Temps pour 1000 jugements | Coût |",
              "|---|---|---|---|---|---|---|---|"]
    for m in metrics:
        ram = f"{m['ram_gb']:.1f} Go" if m.get("ram_gb") else "n/a"
        hours = m["latency_p50_s"] * 1000 / 3600
        lines.append(f"| {m['name']} | {ram} | {fmt(m['latency_p50_s'], digits=1)} s | {fmt(m['latency_p95_s'], digits=1)} s | "
                     f"{fmt(m['completion_tokens_mean'], digits=0)} | {fmt(m['tokens_per_s'], digits=1)} tok/s | "
                     f"{fmt(hours, digits=1)} h | ${fmt(m['cost_per_1k_judgments_usd'])} |")

    by_name = {m["name"]: m for m in metrics}
    gold = [g["gold"]["verdict"] for g in golden]
    comparaisons = config.get("comparisons") or {}

    # Les paires sont DÉCLARÉES, jamais inférées. L'inférence précédente prenait
    # `next(... not fine_tuned ...)`, donc la première venue dans le JSON : avec
    # deux 14B non fine-tunées elle pouvait opposer le fine-tune à la variante nue,
    # l'homme de paille que la §3 interdit — et le biais allait dans le sens
    # favorable au fine-tuning. Voir l'amendement du 2026-09-21.
    principale = comparaisons.get("primary")
    lines += ["", "## Comparaison principale (PREENREGISTREMENT §5)", ""]

    # Deux situations distinctes, et une seule est une erreur.
    #
    #   aucune déclaration du tout  -> aucune conclusion, et le rapport le dit.
    #   paire déclarée incalculable -> sortie en erreur.
    #
    # L'amendement du 2026-09-21 vise « une paire DÉCLARÉE absente des métriques » :
    # une configuration qui ne déclare rien n'exécute pas l'étude. C'est le cas de
    # configs/variants.smoke.json, qui valide serveur, adaptateur et client sur un
    # 0.5B sans rien conclure. Refuser de conclure y préserve les deux garanties —
    # ne jamais inférer une paire, ne jamais conclure sur une paire amputée — là où
    # sortir en erreur ne protégerait rien et casserait la passe de fumée.
    if not principale:
        lines += ["⚠️ **Aucune comparaison déclarée dans cette configuration : aucune conclusion "
                  "n'est émise.** Les sections qui suivent sont purement descriptives.", ""]
        a = b = None
        absents = []
    else:
        a, b = principale["a"], principale["b"]
        absents = [n for n in (a, b) if n not in by_name]

    if principale and absents:
        attendus = [n for n in absents if n in selected_names]
        if attendus:
            sys.exit(f"[ERROR] paire principale incomplète : {attendus} sans métriques exploitables. "
                     "Le rapport refuse de conclure sur une paire amputée.")
        lines += [f"⚠️ **Non calculée** : {absents} hors de la sélection `--variants`. "
                  "Aucune conclusion n'est émise.", ""]
    elif principale:
        pa = majority_verdicts(golden, by_name[a]["_runs"])
        pb = majority_verdicts(golden, by_name[b]["_runs"])
        acc_a, acc_b = strict_accuracy(gold, pa), strict_accuracy(gold, pb)
        n_b, n_c, p = mcnemar_exact(gold, pa, pb)
        d, lo, hi = paired_accuracy_delta(golden, by_name[a]["_runs"], by_name[b]["_runs"],
                                          args.bootstrap, rng)
        if principale.get("claim"):
            lines += [f"Affirmation testée : {principale['claim']}.", ""]
        lines += ["| Variante | Justesse stricte du verdict (vote majoritaire) |", "|---|---|",
                  f"| {a} | {acc_a:.1%} |", f"| {b} | {acc_b:.1%} |", "",
                  f"**Δ justesse = {d:+.1%}**, IC95 bootstrap apparié [{lo:+.1%}, {hi:+.1%}] "
                  f"({args.bootstrap} rééchantillonnages).",
                  f"**McNemar exact bilatéral : p = {p:.4f}** sur {n_b + n_c} paires discordantes "
                  f"(*{a}* seul juste {n_b}, *{b}* seul juste {n_c}).", ""]
        contient_zero = lo <= 0 <= hi
        if contient_zero:
            lines.append(f"→ **Non concluant.** L'intervalle [{lo:+.1%}, {hi:+.1%}] contient zéro, "
                         f"pour une largeur de {hi - lo:.1%}. À n = {len(golden)} items, l'étude ne "
                         f"pouvait pas détecter une différence inférieure à ~15 points : cette limite "
                         f"était énoncée en §5 avant les résultats.")
        elif p < args.alpha and d > 0:
            lines.append(f"→ **Le fine-tuning améliore la justesse de {d:+.1%}**, IC95 [{lo:+.1%}, {hi:+.1%}].")
        elif p < args.alpha and d < 0:
            lines.append(f"→ **Le fine-tuning dégrade la justesse de {d:+.1%}**, IC95 [{lo:+.1%}, {hi:+.1%}]. "
                         f"Publié tel quel, sans atténuation (§7).")
        else:
            lines.append(f"→ L'intervalle exclut zéro mais p = {p:.4f} ≥ {args.alpha} : les deux critères "
                         f"de la §7 ne sont pas réunis, aucune amélioration n'est revendiquée.")

    autres = comparaisons.get("secondary") or []
    calculables = [c for c in autres if c["a"] in by_name and c["b"] in by_name]
    if calculables:
        lines += ["", "## Comparaisons secondaires, descriptives", "",
                  "Aucune ne porte de conclusion : la §7 ne tranche que la comparaison principale.", "",
                  "| A | B | Δ justesse (B − A) | IC95 | McNemar p | Paires discordantes |",
                  "|---|---|---|---|---|---|"]
        for c in calculables:
            x, y = c["a"], c["b"]
            px = majority_verdicts(golden, by_name[x]["_runs"])
            py = majority_verdicts(golden, by_name[y]["_runs"])
            nb2, nc2, p2 = mcnemar_exact(gold, px, py)
            d2, lo2, hi2 = paired_accuracy_delta(golden, by_name[x]["_runs"], by_name[y]["_runs"],
                                                 args.bootstrap, rng)
            lines.append(f"| {x} | {y} | {d2:+.1%} | [{lo2:+.1%}, {hi2:+.1%}] | {p2:.4f} | {nb2 + nc2} |")

    lines += ["", "## Recevabilité opérationnelle", "",
              "Filtre pratique, **sans pouvoir de décision** : une variante qui ne rend pas du JSON "
              "exploitable n'est pas utilisable en production, quelle que soit sa justesse. La §7 ne "
              "déclare aucun seuil de ce genre, et la conclusion de l'étude reste la seule comparaison "
              "principale ci-dessus.", ""]
    for m in metrics:
        reasons = qualification(m, args)
        lines.append(f"- **{m['name']}** : " + ("recevable" if not reasons else "non recevable — " + "; ".join(reasons)))
    if len(golden) < 100:
        lines.append("")
        lines.append(f"⚠️ Avec n = {len(golden)} items, les IC95 de κ sont larges (±0,15 à ±0,25 dès n ≈ 50, bien plus en dessous). "
                     f"Ne concluez qu'à partir des écarts appariés significatifs, pas des classements bruts.")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--config", required=True)
    parser.add_argument("--golden", required=True)
    parser.add_argument("--out", default="results")
    parser.add_argument("--variants", help="comma-separated subset of variant names")
    parser.add_argument("--passes", type=int, default=3)
    parser.add_argument("--temperature", type=float, default=0.2)
    parser.add_argument("--max-tokens", type=int, default=1024)
    parser.add_argument("--timeout", type=float, default=300)
    parser.add_argument("--bootstrap", type=int, default=10000,
                        help="PREENREGISTREMENT §5 : 10 000 rééchantillonnages déclarés")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--alpha", type=float, default=0.05,
                        help="PREENREGISTREMENT §5 : seuil du McNemar exact")
    # Recevabilité opérationnelle, sans pouvoir de décision : voir qualification().
    parser.add_argument("--min-stability", type=float, default=0.95, help="recevabilité : stabilité du verdict")
    parser.add_argument("--min-format", type=float, default=0.95, help="recevabilité : taux de format strict")
    parser.add_argument("--max-verbose-fpr", type=float, default=0.20,
                        help="recevabilité : faux PASS sur réponses verbeuses buguées")
    parser.add_argument("--report-only", action="store_true", help="skip inference, recompute metrics from cached runs")
    parser.add_argument("--format-normalise", action="store_true",
                        help="ajoute la passe « format normalisé » (amendement du 2026-09-19) : "
                             "les mêmes items, sorties dépouillées de leur Markdown, dans la même "
                             "invocation donc sous un seul démarrage de serveur")
    args = parser.parse_args()

    config = json.loads(Path(args.config).read_text(encoding="utf-8"))
    variants = config["variants"]
    if args.variants:
        wanted = set(args.variants.split(","))
        variants = [v for v in variants if v["name"] in wanted]
        if not variants:
            sys.exit(f"[ERROR] no variant matches {args.variants}")

    golden = load_golden(args.golden)
    out = Path(args.out)
    runs_dir = out / "runs"
    runs_dir.mkdir(parents=True, exist_ok=True)

    SUFFIXE_NORM = "--format-normalise"
    golden_norm, exclus = (normalise_golden(golden) if args.format_normalise else (None, []))
    if golden_norm is not None:
        print(f"[format normalisé] {len(golden_norm)} items dépouillés, "
              f"{len(exclus)} exclus (format imposé) : {', '.join(exclus)}")

    if not args.report_only:
        for variant in variants:
            run_variant(variant, golden, args, runs_dir)
            if golden_norm is not None:
                run_variant(variant, golden_norm, args, runs_dir, SUFFIXE_NORM)

    rng = random.Random(args.seed)
    metrics, metrics_norm = [], []
    for variant in variants:
        runs = load_runs(variant, golden, args.passes, runs_dir)
        if not any(runs.values()):
            print(f"[WARN] no cached runs for {variant['name']}, skipped")
            continue
        metrics.append(evaluate(variant, golden, runs, args, rng))
        if golden_norm is not None:
            runs_n = load_runs(variant, golden_norm, args.passes, runs_dir, SUFFIXE_NORM)
            if any(runs_n.values()):
                metrics_norm.append(evaluate(variant, golden_norm, runs_n, args, rng))
            else:
                print(f"[WARN] passe « format normalisé » absente pour {variant['name']}")
    if not metrics:
        sys.exit("[ERROR] nothing to report")

    passe_format = ({"golden": golden_norm, "metrics": metrics_norm, "exclus": exclus}
                    if golden_norm is not None and metrics_norm else None)
    report = build_report(metrics, golden, args, rng, config, [v["name"] for v in variants],
                          passe_format)
    (out / "report.md").write_text(report, encoding="utf-8")
    serializable = [{k: v for k, v in m.items() if k != "_runs"} for m in metrics]
    (out / "metrics.json").write_text(json.dumps(serializable, indent=2, ensure_ascii=False), encoding="utf-8")
    print(report)
    print(f"Wrote {out / 'report.md'} and {out / 'metrics.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
