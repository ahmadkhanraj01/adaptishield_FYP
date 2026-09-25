"""
Layer 5 — Manual Override, command-line flow.

    python -m layer5.review                        # review the default proposal
    python -m layer5.review --proposal p.json
    python -m layer5.review --list                 # decision history
    python -m layer5.review --verdict reject --reason "..."   # non-interactive

Presents a proposal alongside evidence this module recomputed itself, records the
human's verdict in an append-only log, and — only on approval — hands the
proposal to `AdaptiveThreatModel.apply_update(..., approved=True)`.

The command never approves on the operator's behalf. It prints a recommendation
and requires a typed verdict and a reason, because an approval with no recorded
reason cannot be audited afterwards, and because the failure this whole layer
exists to catch (README §6n) is precisely a machine deciding confidently and
wrongly with nobody watching.

Non-interactive use is supported for scripting, but `--verdict approve` still
requires `--reason`, and the recorded decision is marked as non-interactive so a
later reader can tell a considered approval from an automated one.
"""

import argparse
import json
import os
import sys
from typing import Any, Dict, List, Optional

from layer5.governance import (
    DEFAULT_LOG, Decision, Evidence, append_decision, gather_evidence,
    load_decisions, recommendation, verifier_record, warnings_for,
)

DEFAULT_PROPOSAL = "evaluation/kaggle/proposed_update.json"
DEFAULT_EPISODES = "evaluation/kaggle/dataset/episodes.jsonl"

BAR = "=" * 76
RULE = "-" * 76


def _fmt_action(d: Optional[Dict[str, Any]]) -> str:
    if not d:
        return "(none)"
    return "  ".join(f"{k}={v}" for k, v in d.items())


def render(proposal: Dict[str, Any], ev: Evidence, warns: List[str],
           vr: Optional[Dict[str, Any]]) -> None:
    print(BAR)
    print("  LAYER 5 — MANUAL OVERRIDE: review a Component 3D proposal")
    print(BAR)

    print("\n  PROPOSED CHANGE")
    old, new = proposal["old_ie_threshold"], proposal["new_ie_threshold"]
    mark = "" if abs(new - old) < 1e-9 else "   <-- CHANGE"
    print(f"    ie_threshold           {old} -> {new}{mark}")
    for label, key in (("blocked_patterns", "new_blocked_patterns"),
                       ("high_impact_tools", "new_high_impact_tools")):
        vals = proposal.get(key) or []
        print(f"    {label:<22} {vals if vals else '(none)'}"
              f"{'   <-- CHANGE' if vals else ''}")

    joint = proposal.get("joint") or {}
    if joint.get("chosen") and joint.get("incumbent"):
        changed = {k: v for k, v in joint["chosen"].items()
                   if joint["incumbent"].get(k) != v}
        print(f"    joint action           "
              f"{_fmt_action(changed) if changed else '(identical to incumbent)'}")

    # The propose-and-verify trace. A rejected proposal serialises as a no-op, so
    # without this the reviewer sees a blank diff and learns nothing about what
    # the policy actually wanted.
    if vr:
        print(f"\n  {RULE}")
        print("  WHAT THE POLICY WANTED, AND WHAT THE VERIFIER SAID")
        print(f"    policy's argmax        {_fmt_action(vr['policy_wanted'])}")
        if vr["reward_incumbent"] is not None:
            print(f"    reward: incumbent      {vr['reward_incumbent']:+.6f}")
            print(f"            policy choice  {vr['reward_policy_choice']:+.6f}"
                  f"{'   <-- LOWER THAN DOING NOTHING' if vr['policy_choice_was_worse'] else ''}")
        print(f"    verifier verdict       "
              f"{'ACCEPTED' if vr['accepted'] else 'REJECTED -> no-op'}")
        if vr["reverted_as_unnecessary"]:
            print(f"    minimality pass reverted {vr['reverted_as_unnecessary']} "
                  f"(moved for no reward)")
        if vr["flat_dimensions"]:
            print(f"    unidentifiable on this batch: {vr['flat_dimensions']} "
                  f"(reward exactly flat — the data cannot constrain these)")
        if vr["actions_evaluated"]:
            print(f"    searched               {vr['actions_evaluated']} of "
                  f"{vr['space_cardinality']} joint actions (sampled)")

    print(f"\n  {RULE}")
    print(f"  EVIDENCE — recomputed here from {ev.n_episodes} episodes, "
          f"not taken from the proposal")
    print(f"    {'':<22}{'incumbent':>12}{'proposed':>12}{'delta':>12}")
    print(f"    {'mean_reward':<22}{ev.reward_incumbent:>+12.6f}"
          f"{ev.reward_proposed:>+12.6f}{ev.delta:>+12.6f}")
    for label, a, b in (("missed", ev.missed_incumbent, ev.missed_proposed),
                        ("false_positives", ev.false_pos_incumbent, ev.false_pos_proposed),
                        ("workflow_lost", ev.workflow_lost_incumbent, ev.workflow_lost_proposed)):
        print(f"    {label:<22}{a:>12}{b:>12}{b - a:>+12}")

    if ev.claimed_reward is not None:
        verdict = "agrees" if ev.claim_matches else "DISAGREES"
        print(f"    proposal claims mean_reward={ev.claimed_reward:+.6f} "
              f"-> {verdict} with the recomputation")

    if warns:
        print(f"\n  {RULE}")
        print(f"  WARNINGS ({len(warns)})")
        for w in warns:
            first, *rest = w.split(" — ", 1)
            print(f"    * {first}")
            if rest:
                for line in _wrap(rest[0], 68):
                    print(f"        {line}")

    print(f"\n  {RULE}")
    print(f"  RECOMMENDATION: {recommendation(ev, warns)}")
    print("  (a recommendation only — this command will not decide for you)")


def _wrap(text: str, width: int) -> List[str]:
    words, lines, cur = text.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > width:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    if cur:
        lines.append(cur)
    return lines


def show_history(path: str) -> None:
    rows = load_decisions(path)
    if not rows:
        print(f"[layer5] no decisions recorded at {path}")
        return
    print(f"{BAR}\n  DECISION LOG — {path} ({len(rows)} record(s))\n{BAR}")
    for r in rows:
        ev = r.get("evidence", {})
        print(f"\n  {r['timestamp']}  {r['verdict'].upper():<9} by {r['operator']}")
        print(f"    ie_threshold {r['proposal'].get('old_ie_threshold')} -> "
              f"{r['proposal'].get('new_ie_threshold')}   "
              f"delta_reward={ev.get('delta', float('nan')):+.6f}")
        print(f"    reason: {r['reason']}")
        if r.get("warnings"):
            print(f"    ({len(r['warnings'])} warning(s) were shown at review time)")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--proposal", default=DEFAULT_PROPOSAL)
    ap.add_argument("--episodes", default=DEFAULT_EPISODES)
    ap.add_argument("--log", default=DEFAULT_LOG)
    ap.add_argument("--list", action="store_true", help="print the decision log and exit")
    ap.add_argument("--verdict", choices=["approve", "reject"], default=None,
                    help="non-interactive verdict (requires --reason)")
    ap.add_argument("--reason", default=None)
    ap.add_argument("--apply", action="store_true",
                    help="on approval, also commit via apply_update(approved=True)")
    args = ap.parse_args()

    if args.list:
        show_history(args.log)
        return 0

    if not os.path.exists(args.proposal):
        print(f"[layer5] no proposal at {args.proposal} — run the GRPO trainer first.")
        return 2
    if not os.path.exists(args.episodes):
        print(f"[layer5] no episodes at {args.episodes} — the gate recomputes "
              f"evidence itself and will not review a proposal it cannot check.")
        return 2

    from evaluation.kaggle.grpo_env import RewardConfig, load_episodes

    with open(args.proposal) as f:
        proposal = json.load(f)
    episodes = load_episodes(args.episodes)

    ev = gather_evidence(proposal, episodes, RewardConfig(), args.episodes)
    warns = warnings_for(proposal, ev)
    vr = verifier_record(proposal)
    render(proposal, ev, warns, vr)

    # ---- verdict ----
    interactive = args.verdict is None
    if interactive:
        if not sys.stdin.isatty():
            print("\n[layer5] stdin is not a terminal — pass --verdict and "
                  "--reason to record a decision non-interactively.")
            return 3
        print()
        verdict = ""
        while verdict not in ("approve", "reject"):
            verdict = input("  verdict [approve/reject]: ").strip().lower()
        reason = ""
        while not reason:
            reason = input("  reason (recorded, required): ").strip()
    else:
        verdict, reason = args.verdict, (args.reason or "")
        if not reason:
            print("\n[layer5] --reason is required; an approval with no recorded "
                  "reason cannot be audited later.")
            return 3

    decision = Decision(
        verdict="approved" if verdict == "approve" else "rejected",
        reason=reason + ("" if interactive else "  [non-interactive]"),
        proposal=proposal, evidence=ev.__dict__.copy(),
        warnings=warns, episodes_path=args.episodes,
    )
    path = append_decision(decision, args.log)
    print(f"\n[layer5] recorded {decision.verdict.upper()} -> {path}")

    if decision.verdict == "approved" and args.apply:
        return _commit(proposal)
    if decision.verdict == "approved":
        print("[layer5] not committed — re-run with --apply to hand this to "
              "apply_update(approved=True).")
    return 0


def _commit(proposal: Dict[str, Any]) -> int:
    """
    Hand an approved proposal to the live engines through the existing seam.

    The approval flag passed here is the human's, carried from the decision log;
    it is the one place in the codebase where `approved=True` is legitimate,
    because a person typed it and a record exists saying so.
    """
    from layer2.security_sublayer.adaptive_threat_model import (
        AdaptiveThreatModel, ProposedUpdate,
    )
    from layer2.security_sublayer.causal_analyzer import CausalAnalyzer
    from layer2.security_sublayer.policy_engine import PolicyEngine

    update = ProposedUpdate(
        old_ie_threshold=proposal["old_ie_threshold"],
        new_ie_threshold=proposal["new_ie_threshold"],
        new_blocked_patterns=proposal.get("new_blocked_patterns") or [],
        new_high_impact_tools=proposal.get("new_high_impact_tools") or [],
        rationale=proposal.get("rationale") or [],
        mean_reward=proposal.get("mean_reward", 0.0),
    )
    applied = AdaptiveThreatModel().apply_update(
        update, PolicyEngine(), CausalAnalyzer(), approved=True)
    print(f"[layer5] apply_update returned {applied}")
    return 0 if applied else 1


if __name__ == "__main__":
    sys.exit(main())
