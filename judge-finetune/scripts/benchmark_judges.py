#!/usr/bin/env python3
"""
Comparative benchmark of LLM-as-a-Judge variants on the golden set.

Variants (configs/variants.json): 14B baseline, 14B fine-tuned, 32B baseline, 32B fine-tuned.
Every variant is queried through an OpenAI-compatible /v1/chat/completions endpoint
(mlx_lm.server locally, vLLM or equivalent on the cloud GPU).

Metrics (see PROTOCOLE.md §4):
  1. Human alignment   Cohen's kappa + F1 (positive class = FAIL) vs. golden verdicts, bootstrap 95% CI
  2. Verbosity bias    false-PASS rate on verbose hidden-bug cases vs. concise FAIL cases (+ verbose PASS control)
  3. Repeatability     verdict / full-decision stability over N passes at temperature T
  4. Quality/resources latency, tokens, cost per 1000 judgments, paired bootstrap on kappa deltas

Usage:
  python3 scripts/benchmark_judges.py --config configs/variants.json --golden data/golden/test.jsonl
  python3 scripts/benchmark_judges.py ... --variants 14B-baseline,14B-finetuned   # run a subset
  python3 scripts/benchmark_judges.py ... --report-only                           # recompute from cached runs

Raw generations are cached in <out>/runs/<variant>.jsonl; re-running resumes where it stopped.
No third-party dependencies.
"""

import argparse
import json
import os
import random
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


# ── Inference ─────────────────────────────────────────────────────────────────

def chat_completion(variant, messages, temperature, max_tokens, timeout, retries=3):
    body = json.dumps({
        "model": variant["model"],
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }).encode("utf-8")
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


def run_variant(variant, golden, args, runs_dir):
    cache_path = runs_dir / f"{variant['name']}.jsonl"
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
    with cache_path.open("a", encoding="utf-8") as f:
        for n, (p, item) in enumerate(todo, 1):
            result = chat_completion(variant, item["prompt"], args.temperature, args.max_tokens, args.timeout)
            f.write(json.dumps({"pass": p, "id": item["id"], **result}, ensure_ascii=False) + "\n")
            f.flush()
            status = "ERR" if result["error"] else f"{result['latency_s']:.1f}s"
            print(f"  pass {p} {n}/{len(todo)} {item['id']} {status}", flush=True)


def load_runs(variant, golden, passes, runs_dir):
    """Returns {pass: {id: row}} keeping the last successful row per (pass, id)."""
    runs = {p: {} for p in range(1, passes + 1)}
    path = runs_dir / f"{variant['name']}.jsonl"
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
                pairs.append((gold_checks[k], (judgment.get("checks") or {}).get(k)))
        criteria_acc[k] = sum(a == b for a, b in pairs) / len(pairs) if pairs else float("nan")

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


def paired_delta(golden, runs_a, runs_b, iterations, rng):
    """Bootstrap over items of kappa(b) - kappa(a), same resampled items for both variants."""
    n = len(golden)
    full = mean_kappa(golden, runs_b, range(n)) - mean_kappa(golden, runs_a, range(n))
    lo, hi = bootstrap_ci(lambda idx: mean_kappa(golden, runs_b, idx) - mean_kappa(golden, runs_a, idx),
                          n, iterations, rng)
    return full, lo, hi


# ── Decision & report ─────────────────────────────────────────────────────────

def qualification(m, args):
    reasons = []
    if m["kappa_mean"] < args.min_kappa:
        reasons.append(f"κ {m['kappa_mean']:.2f} < {args.min_kappa}")
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


def build_report(metrics, golden, args, rng):
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
    pairs = []
    for size in ("14B", "32B"):
        base = next((m for m in metrics if m["size"] == size and not m["fine_tuned"]), None)
        tuned = next((m for m in metrics if m["size"] == size and m["fine_tuned"]), None)
        if base and tuned:
            pairs.append((base["name"], tuned["name"]))
    for tuned_flag in (True, False):
        small = next((m for m in metrics if m["size"] == "14B" and m["fine_tuned"] == tuned_flag), None)
        large = next((m for m in metrics if m["size"] == "32B" and m["fine_tuned"] == tuned_flag), None)
        if small and large:
            pairs.append((small["name"], large["name"]))
    if pairs:
        lines += ["", "Écarts de κ appariés (bootstrap sur les items, B − A) :", "",
                  "| A | B | Δκ | IC95 | Significatif |", "|---|---|---|---|---|"]
        deltas = {}
        for a, b in pairs:
            d, lo, hi = paired_delta(golden, by_name[a]["_runs"], by_name[b]["_runs"], args.bootstrap, rng)
            deltas[(a, b)] = (d, lo, hi)
            lines.append(f"| {a} | {b} | {d:+.3f} | [{lo:+.3f}, {hi:+.3f}] | {'oui' if lo > 0 or hi < 0 else 'non'} |")
    else:
        deltas = {}

    lines += ["", "## Décision", ""]
    qualified = []
    for m in metrics:
        reasons = qualification(m, args)
        lines.append(f"- **{m['name']}** : " + ("qualifié" if not reasons else "non qualifié — " + "; ".join(reasons)))
        if not reasons:
            qualified.append(m)
    lines.append("")
    if not qualified:
        lines.append("Aucune variante ne passe les seuils de qualification. Le gagnant au κ brut est donné à titre indicatif.")
        qualified = metrics
    winner = max(qualified, key=lambda m: m["kappa_mean"])
    lines.append(f"**Gagnant (κ maximal parmi les variantes qualifiées) : {winner['name']}** (κ = {fmt(winner['kappa_mean'])})")

    if winner["size"] == "32B":
        best_14b = max((m for m in qualified if m["size"] == "14B"), key=lambda m: m["kappa_mean"], default=None)
        if best_14b is None:
            lines.append("Aucune variante 14B qualifiée : le 32B est recommandé par défaut.")
        else:
            d, lo, hi = paired_delta(golden, best_14b["_runs"], winner["_runs"], args.bootstrap, rng)
            cost_ratio = (winner["cost_per_1k_judgments_usd"] / best_14b["cost_per_1k_judgments_usd"]
                          if best_14b["cost_per_1k_judgments_usd"] else float("inf"))
            justified = lo > 0 and d >= args.min_kappa_gain
            lines.append(f"Face au meilleur 14B qualifié ({best_14b['name']}) : Δκ = {d:+.3f} [IC95 {lo:+.3f}, {hi:+.3f}], "
                         f"coût ×{fmt(cost_ratio, digits=1)}, latence p50 ×"
                         f"{fmt(winner['latency_p50_s'] / best_14b['latency_p50_s'], digits=1)}.")
            if justified:
                lines.append(f"→ **Le 32B est justifié** : gain significatif et ≥ {args.min_kappa_gain} point de κ.")
            else:
                lines.append(f"→ **Recommandation : {best_14b['name']}**. Le gain de κ du 32B n'est pas significatif "
                             f"ou reste < {args.min_kappa_gain}, ce qui ne justifie pas son surcoût.")
    else:
        lines.append(f"→ Le gagnant est un modèle {winner['size']} : aucun surcoût 32B à justifier.")
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
    parser.add_argument("--bootstrap", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--min-kappa", type=float, default=0.60, help="qualification: substantial agreement")
    parser.add_argument("--min-stability", type=float, default=0.95, help="qualification: verdict stability over passes")
    parser.add_argument("--min-format", type=float, default=0.95, help="qualification: strict output format rate")
    parser.add_argument("--max-verbose-fpr", type=float, default=0.20, help="qualification: false PASS on verbose buggy answers")
    parser.add_argument("--min-kappa-gain", type=float, default=0.05, help="minimum kappa gain that justifies the 32B")
    parser.add_argument("--report-only", action="store_true", help="skip inference, recompute metrics from cached runs")
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

    if not args.report_only:
        for variant in variants:
            run_variant(variant, golden, args, runs_dir)

    rng = random.Random(args.seed)
    metrics = []
    for variant in variants:
        runs = load_runs(variant, golden, args.passes, runs_dir)
        if not any(runs.values()):
            print(f"[WARN] no cached runs for {variant['name']}, skipped")
            continue
        metrics.append(evaluate(variant, golden, runs, args, rng))
    if not metrics:
        sys.exit("[ERROR] nothing to report")

    report = build_report(metrics, golden, args, rng)
    (out / "report.md").write_text(report, encoding="utf-8")
    serializable = [{k: v for k, v in m.items() if k != "_runs"} for m in metrics]
    (out / "metrics.json").write_text(json.dumps(serializable, indent=2, ensure_ascii=False), encoding="utf-8")
    print(report)
    print(f"Wrote {out / 'report.md'} and {out / 'metrics.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
