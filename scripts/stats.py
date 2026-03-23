#!/usr/bin/env python3
"""
Statistical significance analysis for the RAG benchmark.

Tests:
  - Mann-Whitney U between Lucene and Neo4j latency distributions (per scenario/fileCount)
  - Mann-Whitney U between judge scores (per scenario/fileCount/difficulty)
  - Benjamini-Hochberg FDR correction for multiple comparisons

Usage:
  python3 scripts/stats.py
  python3 scripts/stats.py --jmh target/jmh-results.json --judge target/jmh-judge.jsonl
  python3 scripts/stats.py --alpha 0.05 --no-latency
"""

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path


# ── Dependencies check ────────────────────────────────────────────────────────

def check_deps():
    missing = []
    try:
        import scipy.stats  # noqa: F401
    except ImportError:
        missing.append("scipy")
    try:
        import numpy  # noqa: F401
    except ImportError:
        missing.append("numpy")
    if missing:
        print(f"[ERROR] Missing dependencies: {', '.join(missing)}")
        print(f"  Install with: pip install {' '.join(missing)}")
        sys.exit(1)

check_deps()

import numpy as np
from scipy.stats import mannwhitneyu


# ── Benjamini-Hochberg FDR correction ────────────────────────────────────────

def benjamini_hochberg(p_values: list[float], alpha: float = 0.05) -> list[bool]:
    """
    Apply Benjamini-Hochberg FDR correction.
    Returns a boolean mask: True = significant after correction.
    Less conservative than Bonferroni, appropriate for exploratory analysis.
    """
    n = len(p_values)
    if n == 0:
        return []

    # Sort p-values with original indices
    indexed = sorted(enumerate(p_values), key=lambda x: x[1])
    rejected = [False] * n

    # BH procedure: find largest k where p(k) <= k/n * alpha
    last_reject = -1
    for rank, (orig_idx, pval) in enumerate(indexed, start=1):
        if pval <= (rank / n) * alpha:
            last_reject = rank

    for rank, (orig_idx, pval) in enumerate(indexed, start=1):
        if rank <= last_reject:
            rejected[orig_idx] = True

    return rejected


def bh_corrected_alpha(rank: int, n: int, alpha: float) -> float:
    """BH threshold for rank k out of n tests."""
    return (rank / n) * alpha


# ── JMH JSON parser ──────────────────────────────────────────────────────────

def load_jmh_results(path: Path) -> dict:
    """
    Parse JMH JSON output into:
      { (strategy, scenario, fileCount): [latency_ms, ...] }

    strategy = 'lucene' or 'neo4j' (inferred from benchmark method name).
    """
    with open(path) as f:
        data = json.load(f)

    groups = defaultdict(list)
    for entry in data:
        benchmark = entry.get("benchmark", "")
        params = entry.get("params", {})
        scenario = params.get("scenario", "unknown")
        file_count = int(params.get("fileCount", 0))

        # Infer strategy from benchmark name
        if "lucene" in benchmark.lower():
            strategy = "lucene"
        elif "neo4j" in benchmark.lower():
            strategy = "neo4j"
        else:
            continue

        # Raw data is nested: [[iter1_val1, iter1_val2, ...], [iter2_val1, ...], ...]
        raw_data = entry.get("primaryMetric", {}).get("rawData", [])
        latencies = [v for iteration in raw_data for v in iteration]
        if latencies:
            groups[(strategy, scenario, file_count)].extend(latencies)

    return dict(groups)


# ── Judge JSONL parser ────────────────────────────────────────────────────────

def load_judge_results(path: Path) -> dict:
    """
    Parse jmh-judge.jsonl into:
      { (strategy, scenario, fileCount, difficulty): { avgScore, n, ... } }

    Each line in the JSONL is a summary for one (strategy, scenario, fileCount, difficulty).
    Note: we use avgScore as a proxy; per-question scores are in jmh-judge-detail.jsonl.
    """
    groups = defaultdict(list)
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                strategy   = entry.get("strategy", "").lower()
                scenario   = entry.get("scenario", "unknown")
                file_count = int(entry.get("fileCount", 0))
                difficulty = entry.get("difficulty", "ALL")
                avg_score  = entry.get("avgScore", -1)
                n          = entry.get("n", 0)
                if avg_score >= 0 and n > 0:
                    groups[(strategy, scenario, file_count, difficulty)].append(
                        (avg_score, n)
                    )
            except (json.JSONDecodeError, ValueError):
                continue
    return dict(groups)


def load_judge_detail(path: Path) -> dict:
    """
    Parse jmh-judge-detail.jsonl into per-question scores:
      { (strategy, scenario, fileCount, difficulty): [score, ...] }
    """
    groups = defaultdict(list)
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                strategy   = entry.get("strategy", "").lower()
                scenario   = entry.get("scenario", "unknown")
                file_count = int(entry.get("fileCount", 0))
                difficulty = entry.get("difficulty", "ALL")
                score      = entry.get("score", -1)
                if score >= 0:
                    groups[(strategy, scenario, file_count, difficulty)].append(score)
            except (json.JSONDecodeError, ValueError):
                continue
    return dict(groups)


# ── Statistical tests ─────────────────────────────────────────────────────────

def run_mannwhitney(a: list, b: list, label_a: str, label_b: str) -> dict:
    """
    Two-sided Mann-Whitney U test between two independent samples.
    Uses 'auto' method (exact for small samples, asymptotic otherwise).
    Returns stat, p-value, and effect size r = Z / sqrt(N).
    """
    if len(a) < 2 or len(b) < 2:
        return {"stat": None, "pvalue": None, "effect_r": None, "skipped": True,
                "reason": f"Too few samples ({len(a)} vs {len(b)})"}

    stat, pvalue = mannwhitneyu(a, b, alternative="two-sided")

    # Effect size: rank-biserial correlation r = 1 - 2U / (n1 * n2)
    n1, n2 = len(a), len(b)
    effect_r = 1 - (2 * stat) / (n1 * n2)

    return {
        "stat": float(stat),
        "pvalue": float(pvalue),
        "effect_r": float(effect_r),
        "n_a": n1,
        "n_b": n2,
        "mean_a": float(np.mean(a)),
        "mean_b": float(np.mean(b)),
        "median_a": float(np.median(a)),
        "median_b": float(np.median(b)),
        "skipped": False
    }


# ── Report printer ────────────────────────────────────────────────────────────

def print_header(title: str):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print('='*70)


def print_result(label: str, result: dict, significant: bool, alpha_threshold: float):
    if result.get("skipped"):
        print(f"  {label:50s}  SKIPPED ({result.get('reason', '')})")
        return

    sig_marker = "** SIGNIFICANT **" if significant else "  not significant"
    direction = ""
    if result["mean_a"] < result["mean_b"]:
        direction = "  ← lucene better"
    elif result["mean_a"] > result["mean_b"]:
        direction = "  ← neo4j better"

    print(f"  {label:50s}  p={result['pvalue']:.4f}  r={result['effect_r']:+.3f}"
          f"  [{result['mean_a']:.1f} vs {result['mean_b']:.1f}]"
          f"  {sig_marker}{direction}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="RAG Benchmark Statistical Analysis")
    parser.add_argument("--jmh",    default="target/jmh-results.json",
                        help="JMH JSON results file")
    parser.add_argument("--judge",  default="target/jmh-judge.jsonl",
                        help="Judge JSONL summary file")
    parser.add_argument("--detail", default="target/jmh-judge-detail.jsonl",
                        help="Judge JSONL detail file (per-question scores)")
    parser.add_argument("--alpha",  type=float, default=0.05,
                        help="FDR alpha level (default: 0.05)")
    parser.add_argument("--no-latency", action="store_true",
                        help="Skip latency analysis")
    parser.add_argument("--no-judge",   action="store_true",
                        help="Skip judge score analysis")
    args = parser.parse_args()

    all_labels   = []
    all_pvalues  = []
    all_results  = []

    # ── Latency analysis ──────────────────────────────────────────────────
    if not args.no_latency and Path(args.jmh).exists():
        print_header("LATENCY ANALYSIS (Lucene vs Neo4j, Mann-Whitney U)")
        print(f"  Source: {args.jmh}")

        jmh_data = load_jmh_results(Path(args.jmh))

        # Collect unique (scenario, fileCount) pairs
        scenarios = sorted({(s, fc) for (_, s, fc) in jmh_data.keys()})
        lat_labels   = []
        lat_pvalues  = []
        lat_results  = []

        for scenario, file_count in scenarios:
            lucene_lat = jmh_data.get(("lucene", scenario, file_count), [])
            neo4j_lat  = jmh_data.get(("neo4j",  scenario, file_count), [])
            label = f"scenario={scenario}  fileCount={file_count:5d}"
            result = run_mannwhitney(lucene_lat, neo4j_lat, "lucene", "neo4j")
            lat_labels.append(label)
            lat_pvalues.append(result.get("pvalue") or 1.0)
            lat_results.append(result)

        # BH correction on latency comparisons
        lat_significant = benjamini_hochberg(lat_pvalues, args.alpha)

        print(f"\n  {'Comparison':50s}  {'p-value':>8}  {'effect r':>9}  "
              f"{'[lucene vs neo4j]':>20}  Result")
        print(f"  {'-'*50}  {'-'*8}  {'-'*9}  {'-'*20}  {'-'*20}")
        for label, result, significant, pval in zip(lat_labels, lat_results,
                                                    lat_significant, lat_pvalues):
            bh_thresh = bh_corrected_alpha(sorted(lat_pvalues).index(pval) + 1,
                                           len(lat_pvalues), args.alpha)
            print_result(label, result, significant, bh_thresh)

        all_labels.extend(lat_labels)
        all_pvalues.extend(lat_pvalues)
        all_results.extend(lat_results)

        n_sig = sum(lat_significant)
        print(f"\n  → {n_sig}/{len(lat_results)} latency comparisons significant "
              f"after BH correction (α={args.alpha})")
    elif not args.no_latency:
        print(f"\n[WARN] JMH results not found at {args.jmh} — skipping latency analysis")

    # ── Judge score analysis ──────────────────────────────────────────────
    if not args.no_judge:
        detail_path = Path(args.detail)
        judge_path  = Path(args.judge)

        if detail_path.exists():
            print_header("JUDGE SCORE ANALYSIS (Lucene vs Neo4j, Mann-Whitney U)")
            print(f"  Source: {args.detail}")

            detail_data = load_judge_detail(detail_path)

            # Collect unique (scenario, fileCount, difficulty) triples
            combos = sorted({(s, fc, d)
                             for (_, s, fc, d) in detail_data.keys()
                             if d != "ALL"})
            # Also include ALL
            combos_all = sorted({(s, fc, "ALL")
                                  for (_, s, fc, _) in detail_data.keys()})
            all_combos = list(combos_all) + [c for c in combos]

            jdg_labels  = []
            jdg_pvalues = []
            jdg_results = []

            for scenario, file_count, difficulty in all_combos:
                lucene_scores = detail_data.get(("lucene", scenario, file_count, difficulty), [])
                neo4j_scores  = detail_data.get(("neo4j",  scenario, file_count, difficulty), [])
                label = f"scenario={scenario}  fc={file_count:5d}  diff={difficulty}"
                result = run_mannwhitney(lucene_scores, neo4j_scores, "lucene", "neo4j")
                jdg_labels.append(label)
                jdg_pvalues.append(result.get("pvalue") or 1.0)
                jdg_results.append(result)

            # BH correction on judge score comparisons
            jdg_significant = benjamini_hochberg(jdg_pvalues, args.alpha)

            print(f"\n  {'Comparison':56s}  {'p-value':>8}  {'effect r':>9}  "
                  f"{'[lucene vs neo4j]':>20}  Result")
            print(f"  {'-'*56}  {'-'*8}  {'-'*9}  {'-'*20}  {'-'*20}")
            for label, result, significant, pval in zip(jdg_labels, jdg_results,
                                                         jdg_significant, jdg_pvalues):
                print_result(label, result, significant, args.alpha)

            all_labels.extend(jdg_labels)
            all_pvalues.extend(jdg_pvalues)
            all_results.extend(jdg_results)

            n_sig = sum(jdg_significant)
            print(f"\n  → {n_sig}/{len(jdg_results)} judge-score comparisons significant "
                  f"after BH correction (α={args.alpha})")

        elif judge_path.exists():
            print(f"\n[INFO] Per-question detail not found ({args.detail}).")
            print(f"       Using summary JSONL ({args.judge}) — less statistical power.")
        else:
            print(f"\n[WARN] Judge results not found — skipping judge analysis")

    # ── Global summary ────────────────────────────────────────────────────
    if all_pvalues:
        print_header("GLOBAL SUMMARY")
        total      = len(all_pvalues)
        sig_global = benjamini_hochberg(all_pvalues, args.alpha)
        n_sig      = sum(sig_global)
        n_skip     = sum(1 for r in all_results if r.get("skipped"))

        print(f"  Total comparisons : {total}")
        print(f"  Skipped (too few) : {n_skip}")
        print(f"  Significant (BH)  : {n_sig} / {total - n_skip} testable  "
              f"(FDR α={args.alpha})")

        if n_sig == 0:
            print("\n  ⚠  No statistically significant differences found.")
            print("     Possible causes: corpus too small, high variance, insufficient")
            print("     JMH iterations, or genuinely equivalent strategies.")
        else:
            print(f"\n  ✓  {n_sig} significant difference(s) detected.")
            print("     Interpret effect size r: |r|<0.1 negligible, 0.1–0.3 small,")
            print("     0.3–0.5 medium, >0.5 large (Cohen 1988).")

    print()


if __name__ == "__main__":
    main()
