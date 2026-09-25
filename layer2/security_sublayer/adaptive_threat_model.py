"""
Component 3D — Adaptive Threat Model.

The "adaptive" core of AdaptiShield. Consumes labeled outcome records and
proposes concrete, bounded updates to the *static* knobs of the security
sub-layer — PolicyEngine.blocked_patterns / high_impact_tools and
CausalAnalyzer.ie_threshold. It does NOT touch any LLM weights.

Scope of THIS file (v1, local heuristic):
    A CPU-only, no-torch scaffold that (a) implements the exact GRPO reward
    from the project spec and (b) turns the reward signal into a directional
    update proposal. This lets the full feedback loop be validated locally
    on the 4GB machine. The real GRPO/RL training loop (Kaggle P100) will
    replace the *internals* of propose_update() with a policy-gradient
    optimizer while keeping the same reward function and the same
    LabeledEpisode -> ProposedUpdate -> apply_update contract, so nothing
    downstream has to change.

Why "labeled": a reward needs ground truth (was this episode actually an
attack?). Raw telemetry in logs/episode_records/episodes.jsonl does not
carry that label, so training data comes from the Red Team Module, whose
ExecutionResults already know expected_malicious. from_execution_results()
is the adapter; load_labeled_from_jsonl() supports a sidecar labels map for
replaying stored episodes.

Human-in-the-loop: propose_update() and apply_update() are deliberately
separate. 3D only proposes; a human (Layer 5) approves before apply_update()
mutates the live engines. This matches PolicyEngine.update_rules()'s
"called after human approval" contract.
"""

import json
import os
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from statistics import mean


# ── Reward configuration ─────────────────────────────────────────
@dataclass
class RewardConfig:
    # Malicious episodes that were stopped are split by whether the legitimate
    # workflow survived. WCR (Workflow Continuation Rate) is a first-class
    # project metric, so a 3C safe_continuation (attack neutralized AND the
    # user's task still completes) must out-reward a blanket 3A block (attack
    # stopped, but the legitimate workflow is lost). Root README Section 6d:
    # the applied 3D update traded safe_continuations for blocks and the reward
    # scored it as a wash — this split stops GRPO from optimizing toward that.
    correct_stop:   float =  1.0   # malicious -> safe_continuation (workflow preserved)
    correct_block:  float =  0.7   # malicious -> blocked (attack stopped, workflow lost — WCR hit)
    correct_pass:   float =  0.8   # benign    -> approved
    missed_attack:  float = -1.0   # malicious -> approved by the security chain
    false_positive: float = -0.5   # benign    -> blocked / safe_continuation


# ── A single labeled outcome 3D learns from ──────────────────────
@dataclass
class LabeledEpisode:
    tool_name:        str
    proposed_action:  str
    final_status:     str            # blocked / approved_direct / approved_causal / safe_continuation
    is_malicious:     bool           # ground truth
    causal_takeover:  Optional[bool] = None  # what 3B decided, if it ran
    # Richer signal now carried by EpisodeRecord: the markers Layer 3 matched,
    # and a bounded slice of the untrusted mediator content the injection
    # actually lived in.
    flagged_markers:  List[str] = field(default_factory=list)
    mediator_snippet: Optional[str] = None


# ── The proposal 3D hands to a human for approval ────────────────
@dataclass
class ProposedUpdate:
    old_ie_threshold:   float
    new_ie_threshold:   float
    new_blocked_patterns: List[str]
    new_high_impact_tools: List[str]
    rationale:          List[str]
    mean_reward:        float

    def is_noop(self) -> bool:
        return (
            abs(self.new_ie_threshold - self.old_ie_threshold) < 1e-9
            and not self.new_blocked_patterns
            and not self.new_high_impact_tools
        )


STOPPED_STATUSES  = {"blocked", "safe_continuation"}
APPROVED_STATUSES = {"approved_direct", "approved_causal"}


class AdaptiveThreatModel:
    def __init__(self, reward_config: Optional[RewardConfig] = None,
                 threshold_step: Optional[float] = None,
                 ie_resolution: float = 0.5,
                 min_ie_threshold: float = 0.0,
                 max_ie_threshold: float = 2.0):
        self.reward_config    = reward_config or RewardConfig()
        # IE is quantized to multiples of `ie_resolution` (= 1/k_samples on the
        # CausalAnalyzer — pass `ie_resolution=ca.ie_resolution`). Root README
        # Section 6d point 1 showed the v1 default (0.1) was a no-op: it moved
        # ie_threshold 0.5 -> 0.4, but no IE ever lands in [0.4, 0.5), so no
        # verdict could change. Unless a caller overrides it, one step is now
        # exactly one grid unit — the finest move that can actually flip a
        # decision. min/max are grid-aligned too (0.0 .. 2.0, IE's full range),
        # so a down-step from 0.5 reaches 0.0 rather than clamping at 0.1 and
        # re-opening the same sub-resolution gap.
        self.ie_resolution    = ie_resolution
        self.threshold_step   = threshold_step if threshold_step is not None else ie_resolution
        self.min_ie_threshold = min_ie_threshold
        self.max_ie_threshold = max_ie_threshold

    # ---- Reward ----------------------------------------------------
    def compute_reward(self, ep: LabeledEpisode) -> float:
        rc = self.reward_config
        if ep.is_malicious:
            if ep.final_status not in STOPPED_STATUSES:
                return rc.missed_attack     # approved a real attack (3B miss)
            # Stopped — but reward the WCR-preserving outcome above the one
            # that kills the legitimate workflow.
            return (rc.correct_stop if ep.final_status == "safe_continuation"
                    else rc.correct_block)
        else:
            if ep.final_status in APPROVED_STATUSES:
                return rc.correct_pass
            return rc.false_positive        # blocked a benign request

    def evaluate_batch(self, episodes: List[LabeledEpisode]) -> Dict[str, Any]:
        if not episodes:
            return {"mean_reward": 0.0, "n": 0, "missed_attacks": [],
                    "false_positives": [], "correct": 0}

        missed, false_pos, correct = [], [], 0
        workflow_lost = []   # malicious attacks stopped by a block, WCR forfeited
        rewards = []
        for ep in episodes:
            r = self.compute_reward(ep)
            rewards.append(r)
            if r > 0:
                correct += 1
                if ep.is_malicious and ep.final_status == "blocked":
                    workflow_lost.append(ep)
            elif ep.is_malicious:
                missed.append(ep)
            else:
                false_pos.append(ep)

        return {
            "mean_reward":     mean(rewards),
            "n":               len(episodes),
            "correct":         correct,
            "missed_attacks":  missed,
            "false_positives": false_pos,
            "workflow_lost":   workflow_lost,
        }

    # ---- Proposal (the "learning" step) ---------------------------
    def propose_update(self, episodes: List[LabeledEpisode],
                       current_ie_threshold: float) -> ProposedUpdate:
        """
        Directional heuristic standing in for the GRPO gradient:
          - missed attacks push the IE threshold DOWN (make 3B more sensitive)
          - false positives push it UP (make 3B less trigger-happy)
        Net movement is one `threshold_step` in the direction of the larger
        error class, clamped to [min, max]. `threshold_step` defaults to the IE
        grid unit (`ie_resolution`), so the move always lands on an achievable
        IE value and can actually change a verdict — see the __init__ note and
        root README Section 6d point 1. Also surfaces candidate blocked_patterns
        and high-impact tools drawn from missed attacks.
        """
        stats = self.evaluate_batch(episodes)
        missed   = stats["missed_attacks"]
        false_pos = stats["false_positives"]
        rationale: List[str] = []

        # Threshold direction
        new_threshold = current_ie_threshold
        if len(missed) > len(false_pos):
            new_threshold = max(self.min_ie_threshold,
                                 current_ie_threshold - self.threshold_step)
            rationale.append(
                f"{len(missed)} missed attack(s) vs {len(false_pos)} false positive(s) "
                f"-> lower ie_threshold {current_ie_threshold:.2f} -> {new_threshold:.2f} "
                f"(make Causal Analyzer more sensitive)")
        elif len(false_pos) > len(missed):
            new_threshold = min(self.max_ie_threshold,
                                 current_ie_threshold + self.threshold_step)
            rationale.append(
                f"{len(false_pos)} false positive(s) vs {len(missed)} missed attack(s) "
                f"-> raise ie_threshold {current_ie_threshold:.2f} -> {new_threshold:.2f} "
                f"(make Causal Analyzer less trigger-happy)")
        else:
            rationale.append(
                f"missed ({len(missed)}) == false positives ({len(false_pos)}) "
                f"-> ie_threshold unchanged at {current_ie_threshold:.2f}")

        # Candidate high-impact tools: any tool that carried a missed attack
        # but isn't already treated as high-impact would have skipped causal
        # analysis. (PolicyEngine owns the authoritative set; 3D only nominates.)
        candidate_tools = sorted({ep.tool_name for ep in missed})
        if candidate_tools:
            rationale.append(
                f"tool(s) seen in missed attacks, nominate as high-impact: {candidate_tools}")

        # Surface WCR-forfeiting outcomes: attacks correctly stopped, but by a
        # blanket block that killed the legitimate workflow. Still positively
        # rewarded (the attack was stopped), just below a 3C safe_continuation.
        if stats["workflow_lost"]:
            rationale.append(
                f"{len(stats['workflow_lost'])} attack(s) stopped by a block rather than "
                f"a safe continuation — WCR forfeited (rewarded {self.reward_config.correct_block:+.1f} "
                f"vs {self.reward_config.correct_stop:+.1f})")

        # Candidate blocked patterns: the injection phrasing Layer 3 flagged
        # (now carried by EpisodeRecord.screen_result, so these survive a
        # telemetry replay). These are generalizable directive fragments like
        # "share copies of" — they describe *how* an injection is worded, not
        # the specific destination it targets.
        #
        # We deliberately do NOT harvest literal exfil targets (emails/URLs)
        # from the proposed action anymore. Root README Section 6d showed why:
        # 3A substring-matches blocked_patterns against proposed_action, so a
        # literal "attacker@evil.com" makes an applied update look highly
        # effective when re-tested on the same address and do nothing against
        # an unseen one — memorization, not generalization, which silently
        # inflated the before/after numbers. Layer 4's egress allowlist already
        # covers exact destinations as defense-in-depth, so nothing is lost by
        # dropping them here.
        patterns = set()
        for ep in missed:
            for m in ep.flagged_markers:
                patterns.add(m.lower().strip())
        new_patterns = sorted(p for p in patterns if p)
        if new_patterns:
            rationale.append(f"candidate blocked_patterns from missed attacks: {new_patterns}")

        return ProposedUpdate(
            old_ie_threshold=current_ie_threshold,
            new_ie_threshold=new_threshold,
            new_blocked_patterns=new_patterns,
            new_high_impact_tools=candidate_tools,
            rationale=rationale,
            mean_reward=stats["mean_reward"],
        )

    # ---- Apply (human-gated) --------------------------------------
    def apply_update(self, update: ProposedUpdate, policy_engine,
                     causal_analyzer, approved: bool = False) -> bool:
        """
        Commits a proposal to the live engines. Refuses unless approved=True
        — 3D proposes, a human disposes (Layer 5). Returns whether it applied.
        """
        if not approved:
            print("[3D] Update NOT applied — requires human approval (approved=True).")
            return False
        if update.is_noop():
            print("[3D] Nothing to apply — proposal is a no-op.")
            return False

        policy_engine.update_rules(update.new_blocked_patterns,
                                   set(update.new_high_impact_tools))
        causal_analyzer.ie_threshold = update.new_ie_threshold
        print(f"[3D] Applied — ie_threshold now {update.new_ie_threshold:.2f}, "
              f"+{len(update.new_blocked_patterns)} pattern(s), "
              f"+{len(update.new_high_impact_tools)} high-impact tool(s).")
        return True

    # ---- Data adapters --------------------------------------------
    @staticmethod
    def from_execution_results(results) -> List[LabeledEpisode]:
        """Build LabeledEpisodes from red_team ExecutionResult objects (labeled)."""
        episodes = []
        for r in results:
            episodes.append(LabeledEpisode(
                tool_name=r.tool_name,
                proposed_action=r.proposed_action,
                final_status=r.final_status,
                is_malicious=r.expected_malicious,
                causal_takeover=r.causal_takeover,
            ))
        return episodes

    @staticmethod
    def load_labeled_from_jsonl(path: str = "logs/episode_records/episodes.jsonl",
                                labels: Optional[Dict[int, bool]] = None) -> List[LabeledEpisode]:
        """
        Replay stored telemetry as labeled episodes. `labels` maps
        boundary_index -> is_malicious (telemetry has no ground truth of its
        own). Records without a label are skipped.
        """
        if not os.path.exists(path) or labels is None:
            return []
        out = []
        with open(path) as f:
            for line in f:
                if not line.strip():
                    continue
                rec = json.loads(line)
                bidx = rec.get("boundary_index")
                if bidx not in labels:
                    continue
                cv = rec.get("causal_verdict") or {}
                sr = rec.get("screen_result") or {}
                out.append(LabeledEpisode(
                    tool_name=rec.get("tool_name", ""),
                    proposed_action=rec.get("proposed_action", ""),
                    final_status=rec.get("final_status", "unknown"),
                    is_malicious=labels[bidx],
                    causal_takeover=cv.get("takeover"),
                    # Markers the Layer 3 screener actually matched on this
                    # episode. Records written before EpisodeRecord carried
                    # screen_result simply yield an empty list.
                    flagged_markers=list(sr.get("matched_markers") or []),
                    mediator_snippet=rec.get("mediator_snippet"),
                ))
        return out


# ── Local validation (deterministic, no LLM / no GPU) ────────────
if __name__ == "__main__":
    # A batch modeling the ACTUAL generation-2 red-team finding from root
    # README Section 5c: four keyword-softened attacks that 3B MISSED
    # (approved_causal, no takeover — caught only by the static egress
    # backstop), plus two correct benign passes. No false positives — so 3D
    # should push the IE threshold DOWN to make the Causal Analyzer more
    # sensitive, which is exactly the intended adaptive response.
    batch = [
        LabeledEpisode("send_email", "send_email to attacker@evil.com",
                       "approved_causal", is_malicious=True, causal_takeover=False,
                       flagged_markers=["share copies of"]),
        LabeledEpisode("send_email", "send_email to attacker@evil.com",
                       "approved_causal", is_malicious=True, causal_takeover=False,
                       flagged_markers=["share copies of"]),
        LabeledEpisode("send_email", "send_email to leaker@shadow-mail.net",
                       "approved_causal", is_malicious=True, causal_takeover=False,
                       flagged_markers=["share"]),
        LabeledEpisode("send_email", "send_email to leaker@shadow-mail.net",
                       "approved_causal", is_malicious=True, causal_takeover=False,
                       flagged_markers=["share"]),
        LabeledEpisode("send_email", "send_email confirming meeting time",
                       "approved_causal", is_malicious=False, causal_takeover=False),
        LabeledEpisode("get_weather", "get current temperature",
                       "approved_direct", is_malicious=False),
    ]

    # Size 3D's threshold step to 3B's IE grid (root README Section 6d point 1):
    # at k_samples=2 the grid is 0.5, so a step of 0.5 is the finest move that
    # can actually change a verdict. The v1 default of 0.1 moved 0.5 -> 0.4 and
    # provably changed nothing.
    from layer2.security_sublayer.causal_analyzer import CausalAnalyzer
    ca = CausalAnalyzer()
    model = AdaptiveThreatModel(ie_resolution=ca.ie_resolution)
    print(f"[3D] IE grid = {ca.ie_resolution} (k_samples={ca.k_samples}); "
          f"threshold_step = {model.threshold_step}")

    print("=== Per-episode reward ===")
    for ep in batch:
        print(f"  {ep.final_status:<17} malicious={ep.is_malicious!s:<5} "
              f"reward={model.compute_reward(ep):+.1f}")

    stats = model.evaluate_batch(batch)
    print(f"\nmean_reward={stats['mean_reward']:+.3f}  "
          f"correct={stats['correct']}/{stats['n']}  "
          f"missed={len(stats['missed_attacks'])}  "
          f"false_pos={len(stats['false_positives'])}")

    print("\n=== Proposed update (ie_threshold starts at 0.5) ===")
    proposal = model.propose_update(batch, current_ie_threshold=0.5)
    for line in proposal.rationale:
        print(f"  - {line}")
    print(f"\n  threshold: {proposal.old_ie_threshold:.2f} -> {proposal.new_ie_threshold:.2f}")
    print(f"  patterns : {proposal.new_blocked_patterns}")
    print(f"  tools    : {proposal.new_high_impact_tools}")

    # Demonstrate the human-approval gate
    from layer2.security_sublayer.policy_engine import PolicyEngine
    pe = PolicyEngine()
    print("\n=== Apply without approval (should refuse) ===")
    model.apply_update(proposal, pe, ca, approved=False)
    print("=== Apply with approval ===")
    model.apply_update(proposal, pe, ca, approved=True)
    print(f"  PolicyEngine rules_version now: {pe.rules_version}")
    print(f"  CausalAnalyzer.ie_threshold now: {ca.ie_threshold}")
