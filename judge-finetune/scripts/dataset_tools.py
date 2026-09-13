#!/usr/bin/env python3
"""
Dataset tooling for the LLM-as-a-Judge fine-tuning corpus.

Source files (data/seed/*.jsonl) hold one example per line:
  {"meta": {...}, "messages": [system, user, assistant]}

Commands:
  validate  Strict format + rubric coherence checks (exit 1 on any error)
  stats     Distribution vs. targets (60/40 code/theory, 40/40/20 parfait/defaillant/limite)
  split     Family-grouped stratified split -> MLX-ready files (messages only) + annotated golden set

Usage:
  python3 scripts/dataset_tools.py validate data/seed/*.jsonl
  python3 scripts/dataset_tools.py stats data/seed/*.jsonl
  python3 scripts/dataset_tools.py split data/seed/*.jsonl --out data --test-size 50 --valid-ratio 0.1
  python3 scripts/dataset_tools.py split data/seed/*.jsonl --out data --test-size 10   # POC 20/10

No third-party dependencies.
"""

import argparse
import json
import random
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

SYSTEM_PROMPT = (
    "Tu es un juge d'évaluation de code expert et impartial. Rédige d'abord ton analyse pas à pas "
    "dans une balise <thinking> en vérifiant l'exactitude technique, l'absence de bugs et le respect "
    "des consignes. Termine obligatoirement par un objet JSON strict contenant les critères booléens "
    "et le verdict final."
)
USER_HEADERS = (
    "### CONTEXTE ET CONSIGNE\n",
    "\n\n### RÉPONSE DE L'ASSISTANT À ÉVALUER\n",
    "\n\n### CRITÈRES D'ÉVALUATION\n1. Exactitude technique\n2. Absence de bugs ou d'erreurs conceptuelles\n3. Respect des consignes",
)
JUDGMENT_KEYS = ["exactitude_technique", "absence_de_bugs", "respect_consignes", "verdict", "raison_principale"]
CRITERIA = JUDGMENT_KEYS[:3]

META_ENUMS = {
    "domaine": {"code", "theorie"},
    "tache": {"generation", "refactoring", "debogage", "explication", "question_reponse"},
    "cas": {"parfait", "defaillant", "limite"},
}
TARGETS = {
    "domaine": {"code": 0.60, "theorie": 0.40},
    "cas": {"parfait": 0.40, "defaillant": 0.40, "limite": 0.20},
}
MIN_VERBOSE_FAIL_SHARE_IN_TEST = 0.10

ASSISTANT_RE = re.compile(r"\A<thinking>\n(?P<thinking>.+?)\n</thinking>\n(?P<json>\{.*\})\Z", re.DOTALL)


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
    """Returns (thinking, judgment_dict). Raises ValueError on strict-format violation."""
    m = ASSISTANT_RE.match(content)
    if not m:
        raise ValueError("assistant must be exactly '<thinking>\\n...\\n</thinking>\\n{json}' with nothing after the JSON")
    judgment = json.loads(m.group("json"))
    return m.group("thinking"), judgment


def gold_verdict(example):
    return parse_assistant(example["messages"][2]["content"])[1]["verdict"]


# ── validate ──────────────────────────────────────────────────────────────────

def check_example(ex):
    errors = []
    if set(ex) != {"meta", "messages"}:
        errors.append(f"top-level keys must be meta + messages, got {sorted(ex)}")
        return errors

    meta = ex["meta"]
    for key in ("id", "famille", "domaine", "tache", "cas", "verbeux", "langage"):
        if key not in meta:
            errors.append(f"meta.{key} missing")
    for key, allowed in META_ENUMS.items():
        if key in meta and meta[key] not in allowed:
            errors.append(f"meta.{key}={meta[key]!r} not in {sorted(allowed)}")
    if "verbeux" in meta and not isinstance(meta["verbeux"], bool):
        errors.append("meta.verbeux must be a boolean")

    msgs = ex["messages"]
    if [m.get("role") for m in msgs] != ["system", "user", "assistant"]:
        return errors + ["messages roles must be exactly [system, user, assistant]"]
    if msgs[0]["content"] != SYSTEM_PROMPT:
        errors.append("system prompt differs from the canonical one")

    user = msgs[1]["content"]
    pos = 0
    for header in USER_HEADERS:
        idx = user.find(header, pos)
        if idx < 0:
            errors.append(f"user template header missing or out of order: {header.strip()[:40]!r}")
            break
        pos = idx + len(header)
    if not user.endswith(USER_HEADERS[2]):
        errors.append("user content must end with the evaluation criteria block")

    try:
        thinking, judgment = parse_assistant(msgs[2]["content"])
    except (ValueError, json.JSONDecodeError) as e:
        return errors + [f"assistant: {e}"]

    if not all(re.search(rf"^{i}\. ", thinking, re.MULTILINE) for i in (1, 2, 3)):
        errors.append("thinking must contain the 3 numbered steps (1. / 2. / 3.)")
    if list(judgment) != JUDGMENT_KEYS:
        errors.append(f"judgment keys must be exactly {JUDGMENT_KEYS} in that order, got {list(judgment)}")
        return errors
    for key in CRITERIA:
        if not isinstance(judgment[key], bool):
            errors.append(f"{key} must be a boolean")
    if judgment["verdict"] not in ("PASS", "FAIL"):
        errors.append("verdict must be PASS or FAIL")
    if not isinstance(judgment["raison_principale"], str) or not judgment["raison_principale"].strip():
        errors.append("raison_principale must be a non-empty string")

    # Rubric: PASS <=> all three criteria are true (see PROTOCOLE.md §2)
    expected = "PASS" if all(judgment[k] is True for k in CRITERIA) else "FAIL"
    if judgment["verdict"] != expected:
        errors.append(f"verdict {judgment['verdict']} inconsistent with criteria (expected {expected})")
    if meta.get("cas") == "parfait" and judgment["verdict"] != "PASS":
        errors.append("cas=parfait requires verdict PASS")
    if meta.get("cas") == "defaillant" and judgment["verdict"] != "FAIL":
        errors.append("cas=defaillant requires verdict FAIL")
    if not re.search(rf"\b{judgment['verdict']}\.?\s*$", thinking):
        errors.append("thinking synthesis must end with the same verdict as the JSON")
    return errors


def cmd_validate(args):
    examples = load(args.files)
    n_err, ids = 0, Counter()
    for loc, ex in examples:
        if isinstance(ex, Exception):
            print(f"[ERROR] {loc}: invalid JSON line: {ex}")
            n_err += 1
            continue
        ids[ex.get("meta", {}).get("id")] += 1
        for err in check_example(ex):
            print(f"[ERROR] {loc} ({ex.get('meta', {}).get('id')}): {err}")
            n_err += 1
    for dup, count in ids.items():
        if count > 1:
            print(f"[ERROR] duplicate meta.id {dup!r} ({count}x)")
            n_err += 1
    print(f"{len(examples)} examples checked, {n_err} error(s)")
    return 1 if n_err else 0


# ── stats ─────────────────────────────────────────────────────────────────────

def valid_examples(paths):
    out = []
    for loc, ex in load(paths):
        if isinstance(ex, Exception) or check_example(ex):
            sys.exit(f"[ERROR] {loc} is invalid, run 'validate' first")
        out.append(ex)
    return out


def distribution_report(examples, title):
    n = len(examples)
    lines = [f"── {title} (n={n})"]
    for field, targets in TARGETS.items():
        counts = Counter(ex["meta"][field] for ex in examples)
        for value, target in targets.items():
            share = counts[value] / n if n else 0
            flag = "" if abs(share - target) <= 0.05 else "  <-- off target"
            lines.append(f"  {field:<8} {value:<11} {counts[value]:>4}  {share:6.1%}  (cible {target:.0%}){flag}")
    verdicts = Counter(gold_verdict(ex) for ex in examples)
    lines.append(f"  verdict  PASS {verdicts['PASS']} / FAIL {verdicts['FAIL']}")
    verbose_fail = sum(1 for ex in examples if ex["meta"]["verbeux"] and gold_verdict(ex) == "FAIL")
    verbose_pass = sum(1 for ex in examples if ex["meta"]["verbeux"] and gold_verdict(ex) == "PASS")
    lines.append(f"  verbeux  FAIL (bug caché) {verbose_fail} ({verbose_fail / n:.1%})  |  PASS (contrôle) {verbose_pass}")
    lines.append(f"  tâches   {dict(Counter(ex['meta']['tache'] for ex in examples))}")
    lines.append(f"  langages {dict(Counter(ex['meta']['langage'] for ex in examples))}")
    return "\n".join(lines)


def cmd_stats(args):
    print(distribution_report(valid_examples(args.files), "corpus"))
    return 0


# ── split ─────────────────────────────────────────────────────────────────────

def stratum(ex):
    return (ex["meta"]["domaine"], ex["meta"]["cas"], ex["meta"]["verbeux"] and gold_verdict(ex) == "FAIL")


def pick_families(families, rng, size, strata_targets):
    """Greedy family-level selection that fills per-stratum quotas without splitting a family."""
    order = list(families)
    rng.shuffle(order)
    chosen, taken, filled = [], Counter(), 0
    for fam in order:
        members = families[fam]
        if filled + len(members) > size:
            continue
        gain = sum(1 for ex in members if taken[stratum(ex)] < strata_targets[stratum(ex)])
        if gain * 2 >= len(members):  # at least half of the family fills an open quota
            chosen.append(fam)
            filled += len(members)
            taken.update(stratum(ex) for ex in members)
        if filled == size:
            break
    for fam in order:  # top up if quotas could not be met exactly
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
        sys.exit(f"[ERROR] test-size {args.test_size} >= corpus size {len(examples)}")

    families = defaultdict(list)
    for ex in examples:
        families[ex["meta"]["famille"]].append(ex)

    strata_counts = Counter(stratum(ex) for ex in examples)
    test_targets = {s: round(args.test_size * c / len(examples)) for s, c in strata_counts.items()}
    verbose_fail_key = [s for s in strata_counts if s[2]]
    min_verbose = -(-int(args.test_size * 100 * MIN_VERBOSE_FAIL_SHARE_IN_TEST) // 100)
    if verbose_fail_key:  # over-sample hidden-bug verbose cases so the bias metric is measurable
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
        print(f"[WARN] golden set has {verbose_fail} verbose hidden-bug cases, protocol requires >= {min_verbose} "
              f"({MIN_VERBOSE_FAIL_SHARE_IN_TEST:.0%}). Generate more such cases.")
    if len(test) != args.test_size:
        print(f"[WARN] golden set size is {len(test)} (requested {args.test_size}) because families are not split.")
    print(f"\nWrote {out / 'mlx'}/{{train,valid,test}}.jsonl and {out / 'golden' / 'test.jsonl'}")
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
    p.add_argument("--valid-ratio", type=float, default=0.1, help="share of the non-test examples kept for mlx valid.jsonl")
    p.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    return {"validate": cmd_validate, "stats": cmd_stats, "split": cmd_split}[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
