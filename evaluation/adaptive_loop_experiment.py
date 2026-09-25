"""
Adaptive Loop Experiment — does applying a 3D proposal actually close the gap?

This is the experiment root README Section 13 calls "the single most valuable
next experiment": the red-team campaign found that keyword-softened
(generation-2) injections drop 3B's causal-detection rate to 0/4, and
Component 3D responds by proposing a lower ie_threshold. Nobody had yet
checked whether *applying* that proposal recovers the missed detections.

Design — four phases, each attack phase on a FRESH pipeline:

  1. gen-1   : original attacks + benign controls. Feeds the Optimizer.
  2. before  : gen-2 (keyword-softened) attacks on a pristine pipeline.
               This is the baseline the update has to beat.
  3. propose : 3D consumes the labeled gen-2 results and proposes an update.
  4. after   : the SAME gen-2 cases, plus the benign controls, on a fresh
               pipeline with the proposal applied.

Why a fresh pipeline per phase: CausalAnalyzer's temporal-drift rule can
independently flip `takeover` once three boundaries accumulate. Reusing one
pipeline across before/after would let drift, not the applied update, explain
a difference. A fresh instance per phase makes the update the only variable.

Drift history is now scoped per `session_id` and the ExecutionAgent passes one
per case, so cases no longer contaminate each other *within* a phase either
(root README Section 6g). The fresh-pipeline-per-phase discipline is still
worth keeping — it also isolates 3A/3B state mutated by an applied update.

Why benign cases are re-run in phase 4: an adaptive update that catches
attacks by making 3B hair-trigger is not a win. FPR before vs after is the
control that keeps the headline number honest.
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any

from red_team.attack_generator import AttackGenerator, RedTeamCase
from red_team.execution_agent import ExecutionAgent, ExecutionResult
from red_team.evaluator import Evaluator
from red_team.optimizer import MutationOptimizer, SOFTENERS
from layer2.security_sublayer.adaptive_threat_model import (
    AdaptiveThreatModel, LabeledEpisode,
)

LOG_DIR = "logs/adaptive_loop"


def derive_flagged_markers(case: RedTeamCase) -> List[str]:
    """
    Which softened phrasings the Optimizer actually injected into this case.

    3D cannot yet recover these from telemetry — the softened wording lives in
    mediator content, which EpisodeRecord doesn't store (root README Sec. 6,
    "Limitation"). The red team knows them because it authored the mutation,
    so it hands them over explicitly. This is the `flagged_markers` channel
    described in adaptive_threat_model.py.
    """
    text = case.tool_response.lower()
    return sorted({s.lower() for s in SOFTENERS.values() if s.lower() in text})


def to_labeled(results: List[ExecutionResult],
               markers_by_case: Dict[str, List[str]]) -> List[LabeledEpisode]:
    episodes = AdaptiveThreatModel.from_execution_results(results)
    for ep, r in zip(episodes, results):
        ep.flagged_markers = markers_by_case.get(r.case_id, [])
    return episodes


def causal_summary(results: List[ExecutionResult]) -> List[Dict[str, Any]]:
    """Per-case 3B detail — the IE and the regime severities behind it."""
    rows = []
    for r in results:
        cv = r.causal_verdict or {}
        rows.append({
            "case_id":        r.case_id,
            "family":         r.family,
            "final_status":   r.final_status,
            "takeover":       cv.get("takeover"),
            "ie":             cv.get("ie"),
            "masked":         cv.get("masked_severity"),
            "masked_san":     cv.get("masked_san_severity"),
            "attack_succeeded": r.attack_succeeded,
            "false_positive":   r.false_positive,
        })
    return rows


def print_causal_table(title: str, rows: List[Dict[str, Any]]) -> None:
    print(f"\n  {title}")
    print(f"  {'case_id':<34} {'status':<18} {'IE':>5} {'masked':>7} {'m_san':>7}  takeover")
    print(f"  {'-'*34} {'-'*18} {'-'*5} {'-'*7} {'-'*7}  --------")
    for row in rows:
        def fmt(v):
            return f"{v:.2f}" if isinstance(v, (int, float)) else "n/a"
        print(f"  {row['case_id']:<34} {row['final_status']:<18} "
              f"{fmt(row['ie']):>5} {fmt(row['masked']):>7} {fmt(row['masked_san']):>7}  "
              f"{row['takeover']}")


def run_experiment(max_directives: int = 1, max_targets: int = 1,
                    max_benign: int = None, run_gen1: bool = True) -> Dict[str, Any]:
    os.makedirs(LOG_DIR, exist_ok=True)
    timestamp = datetime.now().isoformat()
    gen = AttackGenerator()
    evaluator = Evaluator()
    optimizer = MutationOptimizer()
    record: Dict[str, Any] = {"timestamp": timestamp}

    attacks = gen.generate_attacks(max_directives=max_directives, max_targets=max_targets)
    benign  = gen.generate_benign(max_scenarios=max_benign)

    # ── Phase 1: generation 1 ────────────────────────────────────
    if run_gen1:
        print(f"\n{'#'*64}\n# PHASE 1 — generation 1 (original attacks + benign)\n{'#'*64}")
        agent1 = ExecutionAgent()
        results_gen1 = agent1.run_batch(attacks + benign)
        report_gen1 = evaluator.evaluate(results_gen1)
        evaluator.print_report(report_gen1)
        record["generation_1"] = evaluator.to_dict(report_gen1)
        record["generation_1_causal"] = causal_summary(results_gen1)
        mutated = optimizer.propose_next_generation(report_gen1, attacks)
    else:
        # Skip the gen-1 run and soften every attack directly. The Optimizer
        # only mutates fully-defended families, and gen-1 has been ASR=0
        # across all four families on every run so far — so this produces the
        # same gen-2 set at half the LLM cost.
        from dataclasses import replace
        mutated = [
            replace(c,
                    case_id=f"{c.case_id}-gen2",
                    tool_response=optimizer._soften(c.tool_response),
                    generation=2,
                    description=c.description + " [mutated: keyword-softened by Optimizer]")
            for c in attacks
            if optimizer._soften(c.tool_response) != c.tool_response
        ]
        print(f"[Experiment] Skipped gen-1; softened {len(mutated)} attack case(s) directly.")

    if not mutated:
        print("[Experiment] Nothing was mutated — cannot run the before/after comparison.")
        return record

    markers_by_case = {c.case_id: derive_flagged_markers(c) for c in mutated}

    # ── Phase 2: BEFORE ──────────────────────────────────────────
    print(f"\n{'#'*64}\n# PHASE 2 — BEFORE: gen-2 softened attacks, pristine pipeline\n{'#'*64}")
    agent_before = ExecutionAgent()
    before_threshold = agent_before.pipeline.causal_analyzer.ie_threshold
    results_before = agent_before.run_batch(mutated)
    report_before = evaluator.evaluate(results_before)
    evaluator.print_report(report_before)

    # ── Phase 3: 3D proposes ─────────────────────────────────────
    print(f"\n{'#'*64}\n# PHASE 3 — Component 3D proposes an update\n{'#'*64}")
    # Size 3D's threshold step to 3B's IE grid so a proposed move is at least
    # one grid unit — otherwise it is a provable no-op (root README Sec. 6d).
    model = AdaptiveThreatModel(
        ie_resolution=agent_before.pipeline.causal_analyzer.ie_resolution)
    episodes = to_labeled(results_before, markers_by_case)
    stats = model.evaluate_batch(episodes)
    print(f"  mean_reward={stats['mean_reward']:+.3f}  correct={stats['correct']}/{stats['n']}  "
          f"missed={len(stats['missed_attacks'])}  false_pos={len(stats['false_positives'])}")
    proposal = model.propose_update(episodes, current_ie_threshold=before_threshold)
    for line in proposal.rationale:
        print(f"  - {line}")
    print(f"\n  threshold: {proposal.old_ie_threshold:.2f} -> {proposal.new_ie_threshold:.2f}")
    print(f"  patterns : {proposal.new_blocked_patterns}")
    print(f"  tools    : {proposal.new_high_impact_tools}")

    # ── Phase 4: AFTER ───────────────────────────────────────────
    print(f"\n{'#'*64}\n# PHASE 4 — AFTER: same gen-2 cases + benign, update applied\n{'#'*64}")
    agent_after = ExecutionAgent()
    applied = model.apply_update(proposal,
                                 agent_after.pipeline.policy_engine,
                                 agent_after.pipeline.causal_analyzer,
                                 approved=True)
    print(f"  applied={applied}  "
          f"ie_threshold now {agent_after.pipeline.causal_analyzer.ie_threshold}")
    results_after = agent_after.run_batch(mutated + benign)
    report_after = evaluator.evaluate(results_after)
    evaluator.print_report(report_after)

    # ── Comparison ───────────────────────────────────────────────
    caught_before = sum(1 for r in results_before if r.causal_takeover is True)
    n_attacks_before = sum(1 for r in results_before if r.expected_malicious)
    after_attacks = [r for r in results_after if r.expected_malicious]
    caught_after = sum(1 for r in after_attacks if r.causal_takeover is True)

    print(f"\n{'='*64}\n[Experiment] BEFORE vs AFTER — did the adaptive loop close?\n{'='*64}")
    print(f"  ie_threshold          {proposal.old_ie_threshold:.2f}  ->  "
          f"{proposal.new_ie_threshold:.2f}")
    print(f"  caught_by_causal      {caught_before}/{n_attacks_before}  ->  "
          f"{caught_after}/{len(after_attacks)}")
    print(f"  ASR                   {report_before.asr:.0%}  ->  {report_after.asr:.0%}")
    print(f"  WCR                   {report_before.wcr:.0%}  ->  {report_after.wcr:.0%}")
    print(f"  FPR (benign control)  n/a  ->  {report_after.fpr:.0%}")

    print_causal_table("BEFORE — per-case 3B detail:", causal_summary(results_before))
    print_causal_table("AFTER  — per-case 3B detail:", causal_summary(results_after))

    record.update({
        "before": evaluator.to_dict(report_before),
        "after": evaluator.to_dict(report_after),
        "before_causal": causal_summary(results_before),
        "after_causal": causal_summary(results_after),
        "proposal": {
            "old_ie_threshold": proposal.old_ie_threshold,
            "new_ie_threshold": proposal.new_ie_threshold,
            "new_blocked_patterns": proposal.new_blocked_patterns,
            "new_high_impact_tools": proposal.new_high_impact_tools,
            "rationale": proposal.rationale,
            "mean_reward": proposal.mean_reward,
        },
        "applied": applied,
        "caught_by_causal_before": f"{caught_before}/{n_attacks_before}",
        "caught_by_causal_after": f"{caught_after}/{len(after_attacks)}",
    })

    out_path = os.path.join(LOG_DIR, f"adaptive_loop_{timestamp.replace(':', '-')}.json")
    with open(out_path, "w") as f:
        json.dump(record, f, indent=2)
    print(f"\n[Experiment] Report saved to {out_path}")
    return record


if __name__ == "__main__":
    run_experiment()
