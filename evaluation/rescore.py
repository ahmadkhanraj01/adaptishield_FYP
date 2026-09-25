"""
Re-score a recorded probe corpus under a scorer variant, without model calls.

WHAT THIS IS FOR. Backlog item 1 needs a scorer change measured on both an
attack cohort and a benign one. Doing that live costs a campaign per candidate,
which is why §6e and §6p each shipped a change before anyone could see its cost.
`evaluation/probe_corpus.py` records what the probe said; this re-scores those
recordings and recomputes the takeover verdict, so a candidate is evaluated in
seconds and the expensive run is spent once, at the end, on confirmation.

🔴 EXACT, NOT SIMULATED — AND ONLY FOR SCORER CHANGES. The probe prompts and the
sanitizer never consult the scorer, and production runs at temperature 0, so a
change confined to `_score_action` cannot alter which action the probe returns.
Re-scoring recorded actions is therefore the same computation the pipeline would
do. `verify_unchanged()` is what keeps that claim true: it refuses to report if
the model tag, temperature, k_samples or any probe prompt has moved since the
corpus was recorded. A change to a PROMPT invalidates the corpus outright; no
flag here can rescue it, and the corpus must be re-recorded.

THE VERDICT COMES FROM THE SHIPPED RULES. Severities are re-derived with
`_score_action`, then handed to `CausalAnalyzer._decide_takeover` — the same
method `evaluate_boundary` calls. Nothing here restates a threshold. That is a
direct response to how the two most recent measurement defects happened: Phase
12's first stratum was a regex that *resembled* `_references_mediator_target`
and mislabelled 135 of 186 cases, and the refusal audit needed the same
correction. A report that paraphrases the rule measures the paraphrase.

DRIFT IS INERT HERE, AS IT IS LIVE. Each case is re-scored with an empty
history, because campaigns and benchmarks give every case its own `session_id`
and the drift rule needs `window_size` boundaries in one session before it can
fire (§6g, backlog item 2). Sharing a history across these cases would invent a
signal the live pipeline does not have.

    python3 -m evaluation.rescore
    python3 -m evaluation.rescore --json results/severity/rescore.json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from statistics import mean
from typing import Dict, List, Optional, Tuple

from evaluation.fpr_report import wilson
from evaluation.paired import mcnemar
from evaluation.probe_corpus import COHORTS, load, verify_unchanged

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_JSON = os.path.join(REPO, "results", "severity", "rescore.json")

# The two arms. `baseline` is every committed number in the project; `capability`
# is the candidate. Both run the identical code path apart from the one flag.
ARMS = {
    "baseline": dict(capability_scoring=False, schemeless_targets=False),
    "capability": dict(capability_scoring=True, schemeless_targets=False),
    # Backlog item 8. Kept as its own arm rather than folded into `capability`
    # because the two change different things: the harm class widens what counts
    # as a high-impact ACTION, while this widens what counts as a TARGET — and
    # the target predicate is also the stratification, so a combined arm would
    # confound a detection gain with a re-labelling of the strata.
    "schemeless": dict(capability_scoring=False, schemeless_targets=True),
    "both": dict(capability_scoring=True, schemeless_targets=True),
}


def _analyzer(**kwargs):
    """
    An analyzer for scoring only.

    Constructing one instantiates an `OllamaLLM` client, but no request is made
    unless a prompt is invoked, and nothing on this path invokes one —
    `semantic_scoring` is off, so `_score_action` never reaches `_judge_action`.
    Asserted rather than assumed, because a silent LLM call here would make the
    "no model calls" claim false and the results non-deterministic.
    """
    from layer2.security_sublayer.causal_analyzer import CausalAnalyzer

    analyzer = CausalAnalyzer(semantic_scoring=False, **kwargs)
    analyzer.llm = _NoModel()
    return analyzer


class _NoModel:
    """Stands in for the LLM client so an accidental call is loud, not silent."""

    def invoke(self, *_args, **_kwargs):
        raise AssertionError(
            "rescore made a model call — this path is meant to be offline, and "
            "a live call would make the results non-deterministic. Check "
            "semantic_scoring.")


def verdict(analyzer, case: dict) -> Tuple[bool, dict]:
    """
    Recompute one case's takeover verdict from its recorded probe actions.

    Returns (takeover, detail). `detail` carries the per-regime severities so a
    changed verdict can be traced to the regime that moved, which is the thing
    a bare boolean would hide.
    """
    from layer2.security_sublayer.causal_analyzer import BoundaryOutcome

    outcomes = {}
    for regime, record in case["regimes"].items():
        shown = (case["sanitized_mediator"]
                 if regime in ("masked_sanitized", "orig_sanitized")
                 else case["mediator"])
        samples = [analyzer._score_action(action, shown)
                   for action in record["actions"]]
        outcomes[regime] = BoundaryOutcome(
            severity=mean(samples) if samples else 0.0,
            proposed_action=record["actions"][0] if record["actions"] else "",
            regime=regime,
            samples=samples,
            raw_actions=list(record["actions"]),
        )

    masked, masked_san = outcomes["masked"], outcomes["masked_sanitized"]
    ie = masked.severity - masked_san.severity

    takeover, reason = analyzer._decide_takeover(
        ie, masked, masked_san, history=[], session_id=case["case_id"])

    return takeover, {
        "ie": ie,
        "reason": reason,
        **{f"{regime}_severity": outcome.severity
           for regime, outcome in outcomes.items()},
        "capability_class": analyzer._capability_misuse(
            masked.raw_actions[0].lower(), case["mediator"])
        if masked.raw_actions else None,
    }


def run_arm(payload: dict, arm: str) -> Dict[str, dict]:
    """{case_id: detail} for one arm, with `takeover` folded into the detail."""
    analyzer = _analyzer(**ARMS[arm])
    out = {}
    for case in payload["cases"]:
        takeover, detail = verdict(analyzer, case)
        detail["takeover"] = takeover
        detail["family"] = case["family"]
        detail["expected_malicious"] = case["expected_malicious"]
        out[case["case_id"]] = detail
    return out


def _rate_rows(results: Dict[str, dict]) -> List[dict]:
    """
    Per-family rates with Wilson intervals.

    Reported per family and never pooled. For InjecAgent the family IS the
    stratum, and the 30/30 draw over-samples the target-match stratum ninefold
    against a 51/459 population, so a pooled figure is wrong for that corpus by
    33 points (Phase 12). The same discipline keeps benign and malicious apart.
    """
    families = sorted({d["family"] for d in results.values()})
    rows = []
    for family in families:
        members = [d for d in results.values() if d["family"] == family]
        malicious = members[0]["expected_malicious"]
        # For attacks the event is a detection; for benign it is a false positive.
        hits = sum(1 for d in members if d["takeover"])
        low, high = wilson(hits, len(members))
        rows.append({
            "family": family,
            "malicious": malicious,
            "event": "detected" if malicious else "false positive",
            "hits": hits,
            "n": len(members),
            "rate": hits / len(members) if members else 0.0,
            "ci_low": low,
            "ci_high": high,
        })
    return rows


def compare(payload: dict) -> dict:
    """Both arms over one cohort, plus the paired test per family."""
    arms = {arm: run_arm(payload, arm) for arm in ARMS}

    def correct(results, family):
        # "Correct" is detection on attacks and NOT flagging on benign, so the
        # sign is right for both cohorts. `mcnemar` requires this polarity
        # explicitly and cannot detect an inverted input.
        return {cid: (d["takeover"] if d["expected_malicious"]
                      else not d["takeover"])
                for cid, d in results.items() if d["family"] == family}

    paired = []
    for family in sorted({d["family"] for d in arms["baseline"].values()}):
        # Every arm against baseline, never against each other: these are
        # nested changes measured on one recording, and a chain of pairwise
        # tests between them would invite reading a difference of differences
        # that no single comparison supports.
        for arm in ARMS:
            if arm == "baseline":
                continue
            test = mcnemar(correct(arms["baseline"], family),
                           correct(arms[arm], family), "baseline", arm)
            paired.append({"family": family, "arm": arm, **test.to_dict()})

    rows = {arm: _rate_rows(results) for arm, results in arms.items()}

    return {
        "manifest": payload["manifest"],
        "arms": rows,
        "projection": {arm: projection(arm_rows) for arm, arm_rows in rows.items()},
        "paired": paired,
        "per_case": {
            cid: {
                "family": arms["baseline"][cid]["family"],
                "capability_class": arms["capability"][cid]["capability_class"],
                **{arm: arms[arm][cid]["takeover"] for arm in ARMS},
                **{f"masked_{arm}": arms[arm][cid]["masked_severity"]
                   for arm in ARMS},
            }
            for cid in arms["baseline"]
        },
    }


def projection(rows: List[dict]) -> Optional[dict]:
    """
    Stratum rates weighted by the InjecAgent POPULATION, or None off that cohort.

    🔴 THIS IS NOT A POOLED RATE, AND THE DIFFERENCE IS 30-ODD POINTS. The draw
    is 30/30 from a 51/459 split, so pooling the sample over-weights the
    target-match stratum ninefold: Phase 12's pooled figure was 51.7%, wrong for
    InjecAgent by 33 points and for our own corpus by 45, and belonging to
    neither. Weighting by the real shares is the only figure that describes the
    corpus, and it is derived from the per-stratum rates that are always
    reported beside it.

    Returns None rather than guessing when the families are not the InjecAgent
    strata, so this can never quietly average two cohorts that are not alike.
    """
    from evaluation import agentdojo_attacks, injecagent

    by_family = {row["family"]: row for row in rows}
    # Each stratified attack corpus declares its own pair of family labels, so a
    # cohort is recognised by its labels rather than by a name passed in — which
    # keeps a benign cohort, or a mix of two corpora, from ever matching.
    for module in (injecagent, agentdojo_attacks):
        with_label, without_label = module.WITH_TARGET, module.NO_TARGET
        if set(by_family) == {with_label, without_label}:
            break
    else:
        return None

    available = module.provenance()
    if not available.get("present"):
        return None
    with_target = available["available_with_target"]
    without_target = available["available_without_target"]
    total = with_target + without_target
    if not total:
        return None

    share = {with_label: with_target / total, without_label: without_target / total}
    return {
        "population": {"with_target": with_target,
                       "without_target": without_target},
        "rate": sum(by_family[f]["rate"] * share[f] for f in share),
        "shares": share,
    }


def report(results: Dict[str, dict]) -> None:
    for cohort, result in results.items():
        print(f"\n=== {cohort} "
              f"(recorded at {result['manifest'].get('git_head', '?')[:8]}, "
              f"model {result['manifest'].get('model')}) ===")
        for arm in ARMS:
            print(f"\n  {arm}")
            for row in result["arms"][arm]:
                print(f"    {row['family']:<16} {row['event']:<15} "
                      f"{row['hits']:>3}/{row['n']:<3} = "
                      f"{row['rate']:6.1%}   95% CI "
                      f"[{row['ci_low']:.1%}, {row['ci_high']:.1%}]")
            projected = result.get("projection", {}).get(arm)
            if projected:
                pop = projected["population"]
                print(f"    {'-> projected':<16} {'on population':<15} "
                      f"{projected['rate']:>13.1%}   "
                      f"({pop['with_target']}/{pop['with_target'] + pop['without_target']}"
                      f" target-match; NOT the pooled sample rate)")
        print("\n  paired (baseline -> arm)")
        for row in result["paired"]:
            print(f"    {row['family']:<16} {row['arm']:<12} "
                  f"helped {row['helped']:>3}  hurt {row['hurt']:>3}  "
                  f"discordant {row['discordant']:>3}  "
                  f"p_exact = {row['p_exact']:.4f}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cohort", choices=COHORTS + ("all",), default="all")
    parser.add_argument("--json", nargs="?", const=DEFAULT_JSON, default=None)
    parser.add_argument("--allow-stale", action="store_true",
                        help="report even if the corpus predates a code change "
                             "(prints the reasons; never silent)")
    args = parser.parse_args()

    cohorts = COHORTS if args.cohort == "all" else (args.cohort,)
    results = {}
    for cohort in cohorts:
        payload = load(cohort)
        if not payload:
            continue
        stale = verify_unchanged(payload)
        if stale:
            print(f"[rescore] 🔴 STALE corpus for {cohort}:")
            for reason in stale:
                print(f"    {reason}")
            if not args.allow_stale:
                print("    refusing to report — re-record, or pass --allow-stale")
                continue
        results[cohort] = compare(payload)

    if not results:
        print("[rescore] nothing to report.")
        return 1

    report(results)

    if args.json:
        os.makedirs(os.path.dirname(args.json), exist_ok=True)
        with open(args.json, "w") as handle:
            json.dump(results, handle, indent=1)
        print(f"\n[rescore] wrote {args.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
