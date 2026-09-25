"""
The run-to-run noise floor, measured rather than inferred.

WHY THIS EXISTS. Phase 13 re-recorded the AgentDojo benign cohort and found the
committed 3.3% FPR reproduces *as a rate* while firing on **different documents**
(041/048 -> 048/055). One known false positive stopped firing and a new one
started. The rate survived by coincidence — two changes that happened to cancel.

That makes ±2-3 cases in 60 the observed run-to-run variation, which is **the
same size as every effect this project compares**: the schemeless arm costs 3
false positives, the capability arm 1, and Phase 13's holdout gain is 4 cases.
A single run cannot resolve any of them, and the caveat attaches just as much to
the committed 3.3% as to any candidate.

So the honest object is not a rate but a rate *with the spread of the process
that produced it*. This module records that spread from k independent recordings
of the same cohort (`probe_corpus.py --run 1`, `--run 2`, ...).

🔴 WHAT MUST NOT BE DONE WITH THESE RUNS: POOL THEM. k recordings of 60
documents are not 60k independent observations — they are 60 documents observed
k times, and the between-run correlation is enormous (most documents are stable
by construction). Pooling would divide the interval by sqrt(k) and manufacture a
precision the measurement does not have. So:

  - the Wilson interval is reported PER RUN, over that run's n documents, which
    is the sampling uncertainty about the DOCUMENT DRAW
  - the run-to-run spread is reported SEPARATELY, as min/max/range over runs,
    which is the instrument's own variation
  - the two are different uncertainties and are never combined into one number

WHAT THE PER-CASE MATRIX ADDS. A spread of ±2 is compatible with two very
different worlds: two documents flipping every run (a boundary that is genuinely
ambiguous), or twenty documents each flipping occasionally (a scorer that is
unstable everywhere). Those have opposite implications for the paper — the first
is §6i's architectural boundary, the second would be an instrument defect — and
only a per-case breakdown separates them. So every case is classified:

    always   fired in every run          -> stable positive
    never    fired in no run             -> stable negative
    unstable fired in some but not all   -> the noise floor, by name

RE-SCORING IS EXACT; RECORDING IS NOT. Each run is re-scored through the shipped
rules via `rescore.verdict`, so the arm comparison within a run is exact (see
probe_corpus's docstring). What varies between runs is what the probe *said*,
which is the thing being measured here.

    python3 -m evaluation.probe_corpus --cohort agentdojo_benign --run 1
    python3 -m evaluation.probe_corpus --cohort agentdojo_benign --run 2
    python3 -m evaluation.noise_floor --cohort agentdojo_benign
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Dict, List, Optional

from evaluation import probe_corpus, rescore
from evaluation.fpr_report import wilson

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(REPO, "results", "noise_floor")

ALWAYS, NEVER, UNSTABLE = "always", "never", "unstable"


def load_runs(cohort: str) -> List[dict]:
    """
    Every recording of `cohort`, with staleness checked before any of it counts.

    `verify_unchanged` is applied per run and a stale run is DROPPED rather than
    reported alongside the others: a recording made under a different probe
    prompt or model tag would show up here as instrument noise, when it is
    actually a different instrument. That is the one way this module could
    manufacture a floor out of nothing.
    """
    payloads = []
    for run in probe_corpus.available_runs(cohort):
        payload = probe_corpus.load(cohort, run)
        if payload is None:
            continue
        stale = probe_corpus.verify_unchanged(payload)
        if stale:
            print(f"[noise_floor] DROPPED run {run or 0} — recorded under "
                  f"different conditions: {'; '.join(stale)}")
            continue
        payload["_run"] = run or 0
        payloads.append(payload)
    return payloads


def matrix(payloads: List[dict], arm: str = "baseline") -> Dict[str, dict]:
    """
    {case_id: {run: takeover}} plus a stability class, over the shared cases.

    Restricted to cases present in EVERY run. A case recorded in only some runs
    cannot be classified — it would land in `unstable` purely for having been
    interrupted, which would read as instrument noise and is not.
    """
    per_run = {p["_run"]: rescore.run_arm(p, arm) for p in payloads}
    if not per_run:
        return {}

    shared = set.intersection(*(set(results) for results in per_run.values()))
    dropped = set().union(*(set(r) for r in per_run.values())) - shared
    if dropped:
        print(f"[noise_floor] {len(dropped)} case(s) not present in all runs, "
              f"excluded from the matrix: {sorted(dropped)[:5]}"
              f"{' ...' if len(dropped) > 5 else ''}")

    out = {}
    for case_id in sorted(shared):
        fired = {run: results[case_id]["takeover"]
                 for run, results in per_run.items()}
        any_fired, all_fired = any(fired.values()), all(fired.values())
        out[case_id] = {
            "fired": fired,
            "n_fired": sum(1 for v in fired.values() if v),
            "n_runs": len(fired),
            "stability": ALWAYS if all_fired else (NEVER if not any_fired
                                                   else UNSTABLE),
            # Carried so the report can keep malicious and benign apart without
            # re-deriving the label from the cohort name.
            "family": next(r[case_id]["family"] for r in per_run.values()),
            "expected_malicious": next(r[case_id]["expected_malicious"]
                                       for r in per_run.values()),
        }
    return out


def summarize(cells: Dict[str, dict]) -> dict:
    """
    Per-run rates with their own intervals, the run-to-run spread apart, and
    **the same breakdown per family**.

    🔴 THE PER-FAMILY SPLIT IS NOT OPTIONAL FOR EVERY COHORT. For InjecAgent the
    family IS the stratum, and the corpus draws 30 cases from each of two strata
    whose population split is 51/459. A pooled figure over that draw is wrong for
    the population by 33 points (Phase 12) — it reports the sampling design
    rather than the system. `by_family` exists so a stratified cohort cannot be
    read off the pooled row by accident, and the report prints the strata first.

    For a single-stratum cohort (the AgentDojo benign set) the family split is
    degenerate and the pooled row is the answer; nothing is lost by computing
    both.
    """
    if not cells:
        return {}

    out = _summarize_subset(cells)
    families = sorted({cell["family"] for cell in cells.values()})
    out["by_family"] = {
        family: _summarize_subset(
            {cid: cell for cid, cell in cells.items()
             if cell["family"] == family})
        for family in families
    }
    out["stratified"] = len(families) > 1
    return out


def _summarize_subset(cells: Dict[str, dict]) -> dict:
    """The per-run / spread / stability triple for any set of cases."""
    if not cells:
        return {}

    runs = sorted(next(iter(cells.values()))["fired"])
    n = len(cells)

    per_run = []
    for run in runs:
        hits = sum(1 for cell in cells.values() if cell["fired"][run])
        low, high = wilson(hits, n)
        per_run.append({"run": run, "hits": hits, "n": n,
                        "rate": hits / n, "ci_low": low, "ci_high": high})

    rates = [row["rate"] for row in per_run]
    hits = [row["hits"] for row in per_run]
    classes = [cell["stability"] for cell in cells.values()]

    return {
        "n_runs": len(runs),
        "n_cases": n,
        "families": sorted({cell["family"] for cell in cells.values()}),
        "per_run": per_run,
        "spread": {
            "min_hits": min(hits), "max_hits": max(hits),
            "range_hits": max(hits) - min(hits),
            "min_rate": min(rates), "max_rate": max(rates),
            "range_rate": max(rates) - min(rates),
        },
        "stability": {
            ALWAYS: classes.count(ALWAYS),
            NEVER: classes.count(NEVER),
            UNSTABLE: classes.count(UNSTABLE),
        },
        "unstable_cases": sorted(
            (cid for cid, cell in cells.items()
             if cell["stability"] == UNSTABLE),
            key=lambda cid: -cells[cid]["n_fired"]),
    }


def report(cohort: str, cells: Dict[str, dict], summary: dict) -> None:
    if not summary:
        print(f"[noise_floor] nothing to report for {cohort}")
        return

    print(f"\n=== noise floor — {cohort} "
          f"({summary['n_runs']} runs x {summary['n_cases']} cases) ===\n")

    if summary["n_runs"] < 2:
        print("⚠️  ONE RUN ONLY — this reports a rate, not a floor. Record a "
              "repeat with `--run 1` before quoting any spread.\n")

    # Strata first, and the pooled row explicitly labelled as not-the-answer,
    # because Phase 12's pooled figure was wrong for the population by 33 points
    # and the only defence against that is to make the split the default reading.
    if summary.get("stratified"):
        print("--- BY STRATUM (the reportable figures) ---")
        for family, sub in summary["by_family"].items():
            spread = sub["spread"]
            rates = "  ".join(f"{row['hits']}/{row['n']}"
                              for row in sub["per_run"])
            print(f"\n  {family}  (n={sub['n_cases']})")
            print(f"    per run: {rates}"
                  f"   -> {spread['min_rate']:.1%}-{spread['max_rate']:.1%}"
                  f"  (range {spread['range_hits']} cases)")
            for row in sub["per_run"]:
                print(f"      run {row['run']}: {row['rate']:>6.1%}  "
                      f"[{row['ci_low']:.1%}, {row['ci_high']:.1%}]")
            stab = sub["stability"]
            print(f"    stability: {stab[ALWAYS]} always, {stab[NEVER]} never, "
                  f"{stab[UNSTABLE]} unstable")
        print("\n--- pooled (⛔ NOT the reportable figure for a stratified "
              "cohort) ---")

    print(f"{'run':>5} {'fired':>7} {'rate':>8}   95% Wilson")
    for row in summary["per_run"]:
        print(f"{row['run']:>5} {row['hits']:>3}/{row['n']:<3} "
              f"{row['rate']:>7.1%}   [{row['ci_low']:.1%}, {row['ci_high']:.1%}]")

    spread = summary["spread"]
    print(f"\nrun-to-run spread: {spread['min_hits']}-{spread['max_hits']} "
          f"cases ({spread['range_hits']} wide), "
          f"{spread['min_rate']:.1%}-{spread['max_rate']:.1%}")
    print("  ^ compare any effect size against THIS before believing it.")

    stab = summary["stability"]
    print(f"\nstability: {stab[ALWAYS]} always, {stab[NEVER]} never, "
          f"{stab[UNSTABLE]} UNSTABLE")

    if summary["unstable_cases"]:
        print("\nthe floor, by name:")
        for case_id in summary["unstable_cases"]:
            cell = cells[case_id]
            pattern = "".join("X" if cell["fired"][r] else "."
                              for r in sorted(cell["fired"]))
            print(f"  {case_id:<40} {cell['n_fired']}/{cell['n_runs']}  {pattern}")
    else:
        print("\nno unstable cases — every case agrees across all runs.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cohort", choices=probe_corpus.COHORTS, required=True)
    parser.add_argument("--arm", choices=sorted(rescore.ARMS), default="baseline",
                        help="scorer arm to re-score every run through "
                             "(default: baseline — the committed numbers)")
    parser.add_argument("--json", default=None,
                        help="write the full matrix here "
                             "(default: results/noise_floor/<cohort>.json)")
    args = parser.parse_args()

    payloads = load_runs(args.cohort)
    if not payloads:
        print(f"[noise_floor] no usable recordings for {args.cohort}")
        return 1

    cells = matrix(payloads, args.arm)
    summary = summarize(cells)
    report(args.cohort, cells, summary)

    out_path = args.json or os.path.join(OUT_DIR, f"{args.cohort}.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as handle:
        json.dump({"cohort": args.cohort, "arm": args.arm,
                   "summary": summary, "cases": cells}, handle, indent=1)
    print(f"\n[noise_floor] wrote {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
