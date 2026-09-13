#!/usr/bin/env python3
"""
Dataset tooling for the LLM-as-a-Judge fine-tuning corpus.

Schéma unifié (2026-09-13) : verdict binaire strict, contrôles booléens atomiques nommés,
marqueur de tâche dans le message system. Aucune note graduée, aucun champ hérité.

Source files (data/seed/*.jsonl), one example per line:
  {"meta": {..., "task": "CODE_ANALYSIS"}, "messages": [system, user, assistant]}

Commands:
  validate  Format strict + alignement critères/contrôles + cohérence du verdict
  stats     Distribution vs. cibles (tâche, domaine, cas, verbosité)
  split     Split stratifié groupé par famille -> fichiers MLX + golden set annoté

Usage:
  python3 scripts/dataset_tools.py validate data/seed/*.jsonl
  python3 scripts/dataset_tools.py stats    data/seed/*.jsonl
  python3 scripts/dataset_tools.py split    data/seed/*.jsonl --out data --test-size 50

No third-party dependencies.
"""

import argparse
import json
import random
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

TASKS = ("CODE_ANALYSIS", "RAG_CONTEXT_RELEVANCE", "RAG_FAITHFULNESS")

SYSTEM_TEMPLATE = (
    "Tu es un juge IA ultra-rigoureux. TÂCHE: {task}. "
    "Analyse la situation pas à pas dans <thinking> avant de rendre ton verdict JSON."
)
USER_HEADERS = (
    "### CONTEXTE / RAG\n",
    "\n\n### ENTREE / REQUÊTE\n",
    "\n\n### SORTIE À ÉVALUER\n",
    "\n\n### CRITÈRES DE VALIDATION\n",
)
# `checks` avant `verdict` : la génération étant séquentielle, les contrôles doivent
# être posés avant la décision qu'ils justifient.
JUDGMENT_KEYS = ["checks", "verdict", "reason"]

META_ENUMS = {
    "task": set(TASKS),
    "domaine": {"code", "theorie", "rag"},
    "tache": {"generation", "refactoring", "debogage", "explication", "question_reponse", "retrieval", "synthese"},
    "cas": {"parfait", "defaillant", "limite"},
}
TARGETS = {
    "task": {"CODE_ANALYSIS": 0.75, "RAG_CONTEXT_RELEVANCE": 0.125, "RAG_FAITHFULNESS": 0.125},
    "cas": {"parfait": 0.40, "defaillant": 0.40, "limite": 0.20},
}
MIN_VERBOSE_FAIL_SHARE_IN_TEST = 0.10

ASSISTANT_RE = re.compile(r"\A<thinking>\n(?P<thinking>.+?)\n</thinking>\n(?P<json>\{.*\})\Z", re.DOTALL)
CRITERION_RE = re.compile(r"^(\d+)\. ([a-z0-9_]+): (\S.*)$")


# ── Parsing ───────────────────────────────────────────────────────────────────

def load(paths):
    examples = []
    for path in paths:
        with open(path, encoding="utf-8") as f:
            for lineno, line in enumerate(f, 1):
                if not line.strip():
                    continue
                try:
                    examples.append((f"{path}:{lineno}", json.loads(line)))
                except json.JSONDecodeError as e:
                    examples.append((f"{path}:{lineno}", e))
    return examples


def parse_assistant(content):
    """Returns (thinking, judgment). Raises ValueError on strict-format violation."""
    m = ASSISTANT_RE.match(content)
    if not m:
        raise ValueError("le message assistant doit être exactement '<thinking>\\n...\\n</thinking>\\n{json}'")
    return m.group("thinking"), json.loads(m.group("json"))


def parse_criteria(user_content):
    """Returns the ordered criterion names declared in the last section of the user message."""
    block = user_content.split(USER_HEADERS[3], 1)[-1]
    names = []
    for line in block.splitlines():
        m = CRITERION_RE.match(line.strip())
        if not m:
            raise ValueError(f"ligne de critère mal formée : {line.strip()[:60]!r}")
        names.append(m.group(2))
    return names


def gold_verdict(example):
    return parse_assistant(example["messages"][2]["content"])[1]["verdict"]


# ── validate ──────────────────────────────────────────────────────────────────

def check_example(ex):
    errors = []
    if set(ex) != {"meta", "messages"}:
        return [f"clés de premier niveau attendues meta + messages, reçu {sorted(ex)}"]

    meta = ex["meta"]
    for key in ("id", "famille", "task", "domaine", "tache", "cas", "verbeux", "langage"):
        if key not in meta:
            errors.append(f"meta.{key} manquant")
    for key, allowed in META_ENUMS.items():
        if key in meta and meta[key] not in allowed:
            errors.append(f"meta.{key}={meta[key]!r} hors de {sorted(allowed)}")
    if "verbeux" in meta and not isinstance(meta["verbeux"], bool):
        errors.append("meta.verbeux doit être un booléen")

    msgs = ex["messages"]
    if [m.get("role") for m in msgs] != ["system", "user", "assistant"]:
        return errors + ["les rôles doivent être exactement [system, user, assistant]"]

    if "task" in meta and msgs[0]["content"] != SYSTEM_TEMPLATE.format(task=meta["task"]):
        errors.append("le message system ne correspond pas au gabarit, marqueur de tâche compris")

    user = msgs[1]["content"]
    pos = 0
    for header in USER_HEADERS:
        idx = user.find(header, pos)
        if idx < 0:
            errors.append(f"en-tête manquant ou mal ordonné : {header.strip()[:40]!r}")
            break
        pos = idx + len(header)
    else:
        try:
            criteria = parse_criteria(user)
            if not criteria:
                errors.append("aucun critère déclaré dans la section CRITÈRES DE VALIDATION")
        except ValueError as e:
            criteria = None
            errors.append(str(e))
        if criteria is not None and len(set(criteria)) != len(criteria):
            errors.append("noms de critères dupliqués")
    criteria = locals().get("criteria")

    try:
        thinking, judgment = parse_assistant(msgs[2]["content"])
    except (ValueError, json.JSONDecodeError) as e:
        return errors + [f"assistant : {e}"]

    if not all(re.search(rf"^{i}\. ", thinking, re.MULTILINE) for i in (1, 2, 3)):
        errors.append("le <thinking> doit contenir les 3 étapes numérotées (1. / 2. / 3.)")
    if list(judgment) != JUDGMENT_KEYS:
        return errors + [f"clés JSON attendues {JUDGMENT_KEYS} dans cet ordre, reçu {list(judgment)}"]

    checks = judgment["checks"]
    if not isinstance(checks, dict) or not checks:
        errors.append("checks doit être un objet non vide")
        return errors
    for name, value in checks.items():
        if not isinstance(value, bool):
            errors.append(f"checks.{name} doit être un booléen")
    if criteria is not None and list(checks) != criteria:
        errors.append(f"checks {list(checks)} désaligné des critères déclarés {criteria}")
    if judgment["verdict"] not in ("PASS", "FAIL"):
        errors.append("verdict doit valoir PASS ou FAIL")
    if not isinstance(judgment["reason"], str) or not judgment["reason"].strip():
        errors.append("reason doit être une chaîne non vide")

    # Règle unique : PASS si et seulement si tous les contrôles sont vrais.
    expected = "PASS" if all(v is True for v in checks.values()) else "FAIL"
    if judgment["verdict"] != expected:
        errors.append(f"verdict {judgment['verdict']} incohérent avec les contrôles (attendu {expected})")
    if meta.get("cas") == "parfait" and judgment["verdict"] != "PASS":
        errors.append("cas=parfait impose verdict PASS")
    if meta.get("cas") == "defaillant" and judgment["verdict"] != "FAIL":
        errors.append("cas=defaillant impose verdict FAIL")
    if not re.search(rf"\b{judgment['verdict']}\.?\s*$", thinking):
        errors.append("la synthèse du <thinking> doit se terminer par le même verdict que le JSON")
    return errors


def cmd_validate(args):
    examples = load(args.files)
    n_err, ids = 0, Counter()
    for loc, ex in examples:
        if isinstance(ex, Exception):
            print(f"[ERROR] {loc}: ligne JSON invalide : {ex}")
            n_err += 1
            continue
        ids[ex.get("meta", {}).get("id")] += 1
        for err in check_example(ex):
            print(f"[ERROR] {loc} ({ex.get('meta', {}).get('id')}): {err}")
            n_err += 1
    for dup, count in ids.items():
        if count > 1:
            print(f"[ERROR] meta.id dupliqué {dup!r} ({count}x)")
            n_err += 1
    print(f"{len(examples)} examples checked, {n_err} error(s)")
    return 1 if n_err else 0


# ── stats ─────────────────────────────────────────────────────────────────────

def valid_examples(paths):
    out = []
    for loc, ex in load(paths):
        if isinstance(ex, Exception) or check_example(ex):
            sys.exit(f"[ERROR] {loc} est invalide, lance d'abord 'validate'")
        out.append(ex)
    return out


def distribution_report(examples, title):
    n = len(examples)
    lines = [f"── {title} (n={n})"]
    for field, targets in TARGETS.items():
        counts = Counter(ex["meta"][field] for ex in examples)
        for value, target in targets.items():
            share = counts[value] / n if n else 0
            flag = "" if abs(share - target) <= 0.05 else "  <-- hors cible"
            lines.append(f"  {field:<6} {value:<22} {counts[value]:>4}  {share:6.1%}  (cible {target:.1%}){flag}")
    verdicts = Counter(gold_verdict(ex) for ex in examples)
    lines.append(f"  verdict  PASS {verdicts['PASS']} / FAIL {verdicts['FAIL']}")
    verbose_fail = sum(1 for ex in examples if ex["meta"]["verbeux"] and gold_verdict(ex) == "FAIL")
    verbose_pass = sum(1 for ex in examples if ex["meta"]["verbeux"] and gold_verdict(ex) == "PASS")
    lines.append(f"  verbeux  FAIL (bug caché) {verbose_fail} ({verbose_fail / n:.1%})  |  PASS (contrôle) {verbose_pass}")
    lines.append(f"  domaines {dict(Counter(ex['meta']['domaine'] for ex in examples))}")
    lines.append(f"  tâches   {dict(Counter(ex['meta']['tache'] for ex in examples))}")
    lines.append(f"  langages {dict(Counter(ex['meta']['langage'] for ex in examples))}")
    return "\n".join(lines)


def cmd_stats(args):
    print(distribution_report(valid_examples(args.files), "corpus"))
    return 0


# ── split ─────────────────────────────────────────────────────────────────────

def stratum(ex):
    return (ex["meta"]["task"], ex["meta"]["cas"], ex["meta"]["verbeux"] and gold_verdict(ex) == "FAIL")


def pick_families(families, rng, size, strata_targets):
    """Sélection gloutonne au niveau des familles : remplit les quotas sans jamais couper une famille."""
    order = list(families)
    rng.shuffle(order)
    chosen, taken, filled = [], Counter(), 0
    for fam in order:
        members = families[fam]
        if filled + len(members) > size:
            continue
        gain = sum(1 for ex in members if taken[stratum(ex)] < strata_targets[stratum(ex)])
        if gain * 2 >= len(members):
            chosen.append(fam)
            filled += len(members)
            taken.update(stratum(ex) for ex in members)
        if filled == size:
            break
    for fam in order:
        if filled >= size:
            break
        if fam not in chosen and filled + len(families[fam]) <= size:
            chosen.append(fam)
            filled += len(families[fam])
    return chosen


def write_jsonl(path, examples, keep_meta):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for ex in examples:
            row = ex if keep_meta else {"messages": ex["messages"]}
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def cmd_split(args):
    examples = valid_examples(args.files)
    rng = random.Random(args.seed)
    if args.test_size >= len(examples):
        sys.exit(f"[ERROR] test-size {args.test_size} >= taille du corpus {len(examples)}")

    families = defaultdict(list)
    for ex in examples:
        families[ex["meta"]["famille"]].append(ex)

    strata_counts = Counter(stratum(ex) for ex in examples)
    test_targets = {s: round(args.test_size * c / len(examples)) for s, c in strata_counts.items()}
    verbose_fail_key = [s for s in strata_counts if s[2]]
    min_verbose = -(-int(args.test_size * 100 * MIN_VERBOSE_FAIL_SHARE_IN_TEST) // 100)
    if verbose_fail_key:
        per_key = -(-min_verbose // len(verbose_fail_key))
        for s in verbose_fail_key:
            test_targets[s] = max(test_targets[s], min(per_key, strata_counts[s]))

    test_fams = set(pick_families(families, rng, args.test_size, Counter(test_targets)))
    rest = {f: m for f, m in families.items() if f not in test_fams}
    n_valid = max(1, round(sum(len(m) for m in rest.values()) * args.valid_ratio))
    valid_fams = set(pick_families(rest, rng, n_valid, Counter({s: n_valid for s in strata_counts})))

    test = [ex for f in test_fams for ex in families[f]]
    valid = [ex for f in valid_fams for ex in rest[f]]
    train = [ex for f, members in rest.items() if f not in valid_fams for ex in members]
    for part in (train, valid, test):
        rng.shuffle(part)

    out = Path(args.out)
    write_jsonl(out / "mlx" / "train.jsonl", train, keep_meta=False)
    write_jsonl(out / "mlx" / "valid.jsonl", valid, keep_meta=False)
    write_jsonl(out / "mlx" / "test.jsonl", test, keep_meta=False)
    write_jsonl(out / "golden" / "test.jsonl", test, keep_meta=True)

    for name, part in (("train", train), ("valid", valid), ("test / golden", test)):
        print(distribution_report(part, name))
    verbose_fail = sum(1 for ex in test if stratum(ex)[2])
    if verbose_fail < min_verbose:
        print(f"[WARN] le golden set contient {verbose_fail} cas verbeux à bug caché, le protocole en exige "
              f"{min_verbose} ({MIN_VERBOSE_FAIL_SHARE_IN_TEST:.0%}).")
    if len(test) != args.test_size:
        print(f"[WARN] golden set de {len(test)} exemples (demandé {args.test_size}) : les familles ne sont pas coupées.")
    print(f"\nÉcrit {out / 'mlx'}/{{train,valid,test}}.jsonl et {out / 'golden' / 'test.jsonl'}")
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("validate", "stats"):
        p = sub.add_parser(name)
        p.add_argument("files", nargs="+")
    p = sub.add_parser("split")
    p.add_argument("files", nargs="+")
    p.add_argument("--out", default="data")
    p.add_argument("--test-size", type=int, default=50)
    p.add_argument("--valid-ratio", type=float, default=0.1)
    p.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    return {"validate": cmd_validate, "stats": cmd_stats, "split": cmd_split}[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
