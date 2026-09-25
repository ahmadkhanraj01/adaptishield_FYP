"""
False-positive rate with a Wilson score interval, by benign cohort.

A point estimate off 8 episodes is not a rate. The Wilson interval on 4/8 spans
roughly 17-83%, which is the whole usable range — reporting "50% FPR" from it
would be reporting noise with a decimal point. This script prints the interval
alongside every estimate so the width is impossible to overlook, and it keeps the
two benign cohorts separate because they answer different questions:

  ours (8)        hand-written. Four contain no address at all and four were
                  written specifically to trip the mediator-target escalation.
                  This cohort is a DIAGNOSTIC — it locates an architectural
                  boundary (README §6m). It is not a sample from any
                  distribution and its "rate" means nothing.

  agentdojo (60)  environment content from AgentDojo (MIT, ETH SPY Lab),
                  authored for a different benchmark by people who never saw
                  this pipeline. This cohort is the ESTIMATE.

Wilson is used rather than the normal approximation because at small n and
proportions near 0 the normal interval is badly wrong — it can extend below zero
and its coverage collapses exactly where our numbers sit.

    python -m evaluation.fpr_report
"""

import argparse
import json
import math
import os
from typing import Dict, List, Tuple

DEFAULT_EPISODES = "evaluation/kaggle/dataset/episodes.jsonl"


def wilson(successes: int, n: int, z: float = 1.96) -> Tuple[float, float]:
    """Wilson score interval for a binomial proportion. Returns (low, high)."""
    if n == 0:
        return (0.0, 1.0)
    p = successes / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = (z / denom) * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (max(0.0, centre - half), min(1.0, centre + half))


def cohort_of(ep: Dict) -> str:
    return "agentdojo" if ep["case_id"].startswith("agentdojo-") else "ours"


def freshness(episodes_path: str,
              records_path: str = "logs/episode_records/episodes.jsonl") -> str:
    """
    Say how old the dataset is, and shout if the live record log is newer.

    This script reads whatever file is at `--episodes` and cannot tell whether it
    reflects the code currently on disk. A campaign that dies part-way leaves the
    previous dataset in place, so re-running this after a failed campaign prints
    the OLD numbers with no indication anything is wrong — which is exactly what
    happened after the probe-grounding fix (§6o): the campaign crashed on a
    transient CUDA fault at case 43 of 134, never wrote the dataset, and this
    report cheerfully reproduced the pre-fix false-positive rate.

    The record log is appended by the live pipeline on every boundary crossing,
    so if it is materially newer than the packaged dataset, a campaign has run
    since the dataset was built and the dataset is stale.
    """
    import time

    if not os.path.exists(episodes_path):
        return f"  !! {episodes_path} does not exist"
    ds = os.path.getmtime(episodes_path)
    age_h = (time.time() - ds) / 3600
    line = (f"  dataset: {episodes_path}\n"
            f"           built {time.strftime('%Y-%m-%d %H:%M', time.localtime(ds))} "
            f"({age_h:.1f}h ago)")

    if os.path.exists(records_path):
        rec = os.path.getmtime(records_path)
        if rec > ds + 60:
            gap = (rec - ds) / 3600
            line += (f"\n  !! STALE — the live record log is {gap:.1f}h NEWER than "
                     f"this dataset.\n"
                     f"     A campaign has run since it was built. If that campaign "
                     f"failed part-way,\n"
                     f"     these numbers describe the PREVIOUS run, not the current "
                     f"code.\n"
                     f"     Re-package before quoting them: "
                     f"python -m evaluation.kaggle.package_episodes --run-campaign")
    return line


def report(episodes: List[Dict]) -> Dict:
    benign = [e for e in episodes if not e["is_malicious"]]
    mal = [e for e in episodes if e["is_malicious"]]

    cohorts: Dict[str, List[Dict]] = {}
    for e in benign:
        cohorts.setdefault(cohort_of(e), []).append(e)

    print("=" * 78)
    print("  FALSE-POSITIVE RATE — by benign cohort, Wilson 95% interval")
    print("=" * 78)
    print(f"  {'cohort':<14}{'FP':>5}{'n':>6}{'point':>9}{'95% Wilson':>20}")

    out = {}
    for name in ("ours", "agentdojo"):
        group = cohorts.get(name, [])
        if not group:
            continue
        fp = sum(1 for e in group if e["causal_takeover"])
        lo, hi = wilson(fp, len(group))
        print(f"  {name:<14}{fp:>5}{len(group):>6}{fp / len(group):>8.1%}"
              f"{f'[{lo:.1%}, {hi:.1%}]':>20}")
        out[name] = {"fp": fp, "n": len(group), "point": fp / len(group),
                     "wilson_low": lo, "wilson_high": hi}

    if benign:
        fp = sum(1 for e in benign if e["causal_takeover"])
        lo, hi = wilson(fp, len(benign))
        print(f"  {'-' * 54}")
        print(f"  {'pooled':<14}{fp:>5}{len(benign):>6}{fp / len(benign):>8.1%}"
              f"{f'[{lo:.1%}, {hi:.1%}]':>20}")
        print("  (pooled is reported for completeness only — the two cohorts are "
              "not\n   draws from one distribution, and 'ours' is not a draw from any)")
        out["pooled"] = {"fp": fp, "n": len(benign), "point": fp / len(benign),
                         "wilson_low": lo, "wilson_high": hi}

    if mal:
        caught = sum(1 for e in mal if e["causal_takeover"])
        lo, hi = wilson(caught, len(mal))
        print(f"\n  {'detection':<14}{caught:>5}{len(mal):>6}{caught / len(mal):>8.1%}"
              f"{f'[{lo:.1%}, {hi:.1%}]':>20}   (caught_by_causal)")
        out["detection"] = {"caught": caught, "n": len(mal),
                            "wilson_low": lo, "wilson_high": hi}

    fps = [e for e in benign if e["causal_takeover"]]
    if fps:
        print(f"\n  the {len(fps)} false positive(s):")
        for e in fps:
            c = e["causal"]
            print(f"    {e['case_id']:<28} masked={c['masked_severity']:<4} "
                  f"san={c['masked_san_severity']:<4} ie={c['ie']}")
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--episodes", default=DEFAULT_EPISODES)
    ap.add_argument("--json-out", default=None)
    args = ap.parse_args()

    print(freshness(args.episodes))

    with open(args.episodes) as f:
        episodes = [json.loads(line) for line in f if line.strip()]
    out = report(episodes)

    if args.json_out:
        with open(args.json_out, "w") as f:
            json.dump(out, f, indent=2)
        print(f"\n[fpr] wrote {args.json_out}")


if __name__ == "__main__":
    main()
