"""
Apply a Kaggle-trained ProposedUpdate locally and validate it (Phase 6 step 3).

Closes the local↔Kaggle loop: reads the `proposed_update.json` the P100 emitted,
applies it to a *fresh* pipeline through the existing human-gated
`AdaptiveThreatModel.apply_update(..., approved=True)` seam, and re-runs the
red-team campaign BEFORE vs AFTER — reporting `caught_by_causal`, ASR, WCR and
FPR on the same protocol as README §6i/§6k. Nothing about training touched the
live pipeline; only this validated proposal does.

The proposal is applied exactly as the local heuristic's would be — same
`ProposedUpdate` dataclass, same `apply_update` contract — so a GRPO-trained
proposal and a heuristic one are interchangeable here by construction.

LLM-dependent (runs the pipeline → needs Ollama + gemma3:4b). Because a single
run is noisy at the 3B layer (README §6h), treat one invocation as one sample;
run it a few times for a distribution before drawing conclusions.

Usage:
  python -m evaluation.kaggle.apply_and_validate \\
      --proposal evaluation/kaggle/output/proposed_update.json
"""

import argparse
import json
import os
from dataclasses import replace

from layer2.security_sublayer.adaptive_threat_model import (
    AdaptiveThreatModel, ProposedUpdate)


def load_proposal(path: str) -> ProposedUpdate:
    """Read the Kaggle-trained JSON into the live ProposedUpdate contract."""
    with open(path) as f:
        d = json.load(f)
    return ProposedUpdate(
        old_ie_threshold=d["old_ie_threshold"],
        new_ie_threshold=d["new_ie_threshold"],
        new_blocked_patterns=list(d.get("new_blocked_patterns") or []),
        new_high_impact_tools=list(d.get("new_high_impact_tools") or []),
        rationale=list(d.get("rationale") or []),
        mean_reward=d.get("mean_reward", 0.0),
    )


def _caught(results):
    attacks = [r for r in results if r.expected_malicious]
    return sum(1 for r in attacks if r.causal_takeover is True), len(attacks)


def validate(proposal_path: str, max_directives=1, max_train_targets=1,
             run_holdout=True, out_path=None):
    from red_team.attack_generator import AttackGenerator
    from red_team.attack_library import training_targets, holdout_targets
    from red_team.execution_agent import ExecutionAgent
    from red_team.evaluator import Evaluator
    from red_team.optimizer import MutationOptimizer

    proposal = load_proposal(proposal_path)
    print(f"[apply] loaded proposal: ie_threshold "
          f"{proposal.old_ie_threshold:.2f} -> {proposal.new_ie_threshold:.2f}, "
          f"+{len(proposal.new_blocked_patterns)} pattern(s), "
          f"+{len(proposal.new_high_impact_tools)} tool(s)")
    if proposal.is_noop():
        print("[apply] proposal is a NO-OP — GRPO found nothing to change "
              "(a valid Phase 6 result: no natural gap for this knob).")

    gen, evaluator, optimizer = AttackGenerator(), Evaluator(), MutationOptimizer()
    train = training_targets()[:max_train_targets] if max_train_targets else training_targets()
    attacks = gen.generate_attacks(max_directives=max_directives, targets=train)
    benign = gen.generate_benign()

    # Soften every attack directly (README §6k: gen-1 is ASR=0 across families,
    # so this is the same gen-2 set at half the LLM cost).
    mutated = [
        replace(c, case_id=f"{c.case_id}-gen2",
                tool_response=optimizer._soften(c.tool_response), generation=2,
                description=c.description + " [mutated: keyword-softened]")
        for c in attacks if optimizer._soften(c.tool_response) != c.tool_response
    ]
    if not mutated:
        print("[apply] nothing softened — cannot run before/after.")
        return

    # ── BEFORE ───────────────────────────────────────────────────────
    print(f"\n{'#'*60}\n# BEFORE — pristine pipeline\n{'#'*60}")
    agent_before = ExecutionAgent()
    before_threshold = agent_before.pipeline.causal_analyzer.ie_threshold
    results_before = agent_before.run_batch(mutated + benign)
    report_before = evaluator.evaluate(results_before)
    evaluator.print_report(report_before)

    # ── APPLY + AFTER ────────────────────────────────────────────────
    print(f"\n{'#'*60}\n# AFTER — apply Kaggle proposal, re-run\n{'#'*60}")
    agent_after = ExecutionAgent()
    model = AdaptiveThreatModel(
        ie_resolution=agent_after.pipeline.causal_analyzer.ie_resolution)
    # `approved=True` here is a MEASUREMENT approval, not a governance one.
    #
    # This script exists to answer "what would this proposal do to the metrics?",
    # which requires applying it to a throwaway ExecutionAgent. That is a
    # different act from committing a change to a live control, and conflating
    # the two is what made the human gate a rubber stamp: for a long time this
    # literal was the only thing standing where Layer 5 belongs.
    #
    # The governance path is `python -m layer5.review`, which recomputes the
    # evidence independently, shows the reviewer what the policy wanted versus
    # what the verifier said, and records a reason in an append-only log before
    # anything is committed. Nothing here is persisted, so no approval is being
    # granted — but say so out loud, because a reader who finds `approved=True`
    # in a diff is right to be suspicious of it.
    print("[apply] NOTE: applying to a throwaway agent to measure the effect. "
          "This is not an approval — use `python -m layer5.review` to approve, "
          "which records who decided and why (Layer 5).")
    applied = model.apply_update(proposal,
                                 agent_after.pipeline.policy_engine,
                                 agent_after.pipeline.causal_analyzer,
                                 approved=True)
    print(f"[apply] applied={applied}  "
          f"ie_threshold now {agent_after.pipeline.causal_analyzer.ie_threshold}")
    results_after = agent_after.run_batch(mutated + benign)
    report_after = evaluator.evaluate(results_after)
    evaluator.print_report(report_after)

    caught_before, n_before = _caught(results_before)
    caught_after, n_after = _caught(results_after)

    holdout_line = None
    if run_holdout:
        print(f"\n{'#'*60}\n# HELD-OUT generalization (same applied pipeline)\n{'#'*60}")
        hold = holdout_targets()[:1]
        holdout_attacks = gen.generate_attacks(max_directives=max_directives, targets=hold)
        holdout_mutated = [
            replace(c, case_id=f"{c.case_id}-gen2-holdout",
                    tool_response=optimizer._soften(c.tool_response), generation=2)
            for c in holdout_attacks if optimizer._soften(c.tool_response) != c.tool_response
        ]
        results_holdout = agent_after.run_batch(holdout_mutated)
        c_h, n_h = _caught(results_holdout)
        report_holdout = evaluator.evaluate(results_holdout)
        holdout_line = (c_h, n_h, report_holdout.asr)

    # ── report ───────────────────────────────────────────────────────
    print(f"\n{'='*60}\n[apply] BEFORE vs AFTER\n{'='*60}")
    print(f"  ie_threshold          {before_threshold:.2f}  ->  "
          f"{agent_after.pipeline.causal_analyzer.ie_threshold:.2f}")
    print(f"  caught_by_causal      {caught_before}/{n_before}  ->  {caught_after}/{n_after}")
    print(f"  ASR                   {report_before.asr:.0%}  ->  {report_after.asr:.0%}")
    print(f"  WCR                   {report_before.wcr:.0%}  ->  {report_after.wcr:.0%}")
    print(f"  FPR (benign control)  {report_before.fpr:.0%}  ->  {report_after.fpr:.0%}")
    if holdout_line:
        c_h, n_h, asr_h = holdout_line
        print(f"  held-out caught       {c_h}/{n_h}   (ASR {asr_h:.0%}) "
              f"— addresses 3D/GRPO never trained on")

    summary = {
        "proposal": proposal_path,
        "ie_threshold_before": before_threshold,
        "ie_threshold_after": agent_after.pipeline.causal_analyzer.ie_threshold,
        "caught_before": [caught_before, n_before],
        "caught_after": [caught_after, n_after],
        "asr_before": report_before.asr, "asr_after": report_after.asr,
        "wcr_before": report_before.wcr, "wcr_after": report_after.wcr,
        "fpr_before": report_before.fpr, "fpr_after": report_after.fpr,
        "holdout": holdout_line,
    }
    if out_path:
        os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
        with open(out_path, "w") as f:
            json.dump(summary, f, indent=2)
        print(f"\n[apply] summary saved to {out_path}")
    return summary


def main():
    ap = argparse.ArgumentParser(description="Apply + validate a Kaggle ProposedUpdate")
    ap.add_argument("--proposal", default="evaluation/kaggle/output/proposed_update.json")
    ap.add_argument("--max-directives", type=int, default=1)
    ap.add_argument("--max-train-targets", type=int, default=1)
    ap.add_argument("--no-holdout", action="store_true")
    ap.add_argument("--out", default="evaluation/kaggle/output/validation_summary.json")
    args = ap.parse_args()

    if not os.path.exists(args.proposal):
        ap.error(f"proposal not found: {args.proposal} "
                 "(run run_kaggle.sh, or grpo_train.py locally, first)")
    validate(args.proposal, args.max_directives, args.max_train_targets,
             run_holdout=not args.no_holdout, out_path=args.out)


if __name__ == "__main__":
    main()
