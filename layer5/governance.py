"""
Layer 5 — Manual Override: the human gate on Component 3D's proposals.

WHY THIS EXISTS, CONCRETELY. `AdaptiveThreatModel.apply_update()` already refuses
unless `approved=True`, so the seam was correct from the start. What was missing
is anything on the other side of it: `evaluation/kaggle/apply_and_validate.py`
passes `approved=True` as a literal, so in practice the gate has been a rubber
stamp, and no record survives of who approved what or on what evidence.

That is not a hypothetical exposure. README §6n records that the GRPO policy
proposed a change to a security threshold that its own reward function scored
LOWER (+0.8683 against the incumbent's +0.8688), and that the un-guarded apply
path would have taken it silently. It has since done the same thing twice more.
A proposer that is confidently wrong is the normal case, not the pathological
one.

THE DESIGN RULE THAT FOLLOWS: never trust the proposal's own arithmetic.

A proposal arrives carrying a `mean_reward` and a rationale that the proposer
computed about itself. This module recomputes both sides — incumbent and
proposal — from the labeled episodes, using the same reward configuration, and
shows the human its own numbers next to the proposer's claim. If the two
disagree, that disagreement is the single most important thing on the screen: it
means the artifact under review does not describe the change it would make.

The decision log is append-only JSONL, one record per human decision, capturing
the proposal, the independently recomputed evidence, the verdict and the
reason. An approval with no recorded reason is not an approval anyone can audit
later.
"""

import getpass
import json
import os
import socket
from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import Any, Dict, List, Optional

DEFAULT_LOG = "logs/layer5/decisions.jsonl"

# How close two reward computations must be before we call them the same number.
# The reward is a mean over a fixed episode list, so agreement should be exact up
# to floating-point summation order; anything larger is a real disagreement.
REWARD_TOLERANCE = 1e-9


@dataclass
class Evidence:
    """What the gate computed for itself, independently of the proposal."""
    n_episodes: int
    reward_incumbent: float
    reward_proposed: float
    delta: float
    missed_incumbent: int
    missed_proposed: int
    false_pos_incumbent: int
    false_pos_proposed: int
    workflow_lost_incumbent: int
    workflow_lost_proposed: int
    claimed_reward: Optional[float] = None
    claim_matches: Optional[bool] = None
    inert_patterns: List[str] = field(default_factory=list)

    @property
    def is_regression(self) -> bool:
        """The §6n case: the proposal scores worse than leaving things alone."""
        return self.delta < -REWARD_TOLERANCE

    @property
    def is_neutral(self) -> bool:
        return abs(self.delta) <= REWARD_TOLERANCE


@dataclass
class Decision:
    verdict: str                      # approved | rejected
    reason: str
    proposal: Dict[str, Any]
    evidence: Dict[str, Any]
    warnings: List[str] = field(default_factory=list)
    operator: str = field(default_factory=lambda: _whoami())
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    episodes_path: Optional[str] = None


def _whoami() -> str:
    try:
        return f"{getpass.getuser()}@{socket.gethostname()}"
    except Exception:                                   # noqa: BLE001
        return "unknown"


def gather_evidence(proposal: Dict[str, Any], episodes, rc,
                    episodes_path: Optional[str] = None) -> Evidence:
    """
    Recompute both sides from the episodes. `episodes` are EpisodeFeatures and
    `rc` a RewardConfig; both come from evaluation.kaggle.grpo_env, which is the
    same replay machinery the trainer used — using a *different* implementation
    here would test the implementation rather than the proposal.
    """
    from evaluation.kaggle.grpo_env import Policy, evaluate_policy

    old = float(proposal["old_ie_threshold"])
    new = float(proposal["new_ie_threshold"])

    # The incumbent carries no learned patterns; the proposal carries whatever it
    # is asking to add. When the joint trainer ran, the marker weights it chose
    # live in the top-level `joint` block — reading them matters, because a
    # proposal whose only real change is a marker weight looks like a no-op if
    # you inspect the ie_threshold alone. That is precisely the §6n case.
    chosen = ((proposal.get("joint") or {}).get("chosen") or {})
    marker_weights = {k.split("marker_weight:", 1)[1]: float(v)
                      for k, v in chosen.items()
                      if isinstance(k, str) and k.startswith("marker_weight:")}

    incumbent = Policy(ie_threshold=old)
    proposed = Policy(
        ie_threshold=new,
        blocked_patterns=list(proposal.get("new_blocked_patterns") or []),
        high_impact_tools=list(proposal.get("new_high_impact_tools") or []),
        marker_weights=marker_weights,
    )

    a = evaluate_policy(episodes, incumbent, rc)
    b = evaluate_policy(episodes, proposed, rc)

    claimed = proposal.get("mean_reward")
    claim_matches = (None if claimed is None
                     else abs(float(claimed) - b["mean_reward"]) <= 1e-6)

    # A blocked_pattern that matches nothing is not harmless — it is a change to
    # a security control that reads as protection and provides none. 3A matches
    # blocked_patterns against the *proposed_action*, but the trainer harvests
    # candidates from *flagged_markers*, which describe mediator content. The two
    # are different namespaces, so a pattern can be highly discriminative as a
    # marker and still never fire as a rule.
    inert = []
    for pat in (proposal.get("new_blocked_patterns") or []):
        p = str(pat).lower().strip()
        if p and not any(p in ep.proposed_action.lower() for ep in episodes):
            inert.append(pat)

    return Evidence(
        n_episodes=len(episodes),
        reward_incumbent=a["mean_reward"],
        reward_proposed=b["mean_reward"],
        delta=b["mean_reward"] - a["mean_reward"],
        missed_incumbent=a["missed"], missed_proposed=b["missed"],
        false_pos_incumbent=a["false_pos"], false_pos_proposed=b["false_pos"],
        workflow_lost_incumbent=a["workflow_lost"],
        workflow_lost_proposed=b["workflow_lost"],
        claimed_reward=None if claimed is None else float(claimed),
        claim_matches=claim_matches,
        inert_patterns=inert,
    )


def verifier_record(proposal: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    The trainer's own propose-and-verify trace, if the joint trainer produced it.

    This is the most informative thing in the artifact and the easiest to miss,
    because a rejected proposal serialises as a no-op and looks like nothing
    happened. What actually happened is that the learned policy wanted one thing,
    the verifier scored it against the incumbent, and it lost. Surfacing that is
    the point of the Policy Inspection Console: the reviewer should see the
    machine disagreeing with itself, not a blank diff.
    """
    joint = proposal.get("joint") or {}
    diag = joint.get("diagnostics") or {}
    if not diag:
        return None
    r_inc = diag.get("reward_incumbent")
    r_pol = diag.get("reward_policy_choice")
    return {
        "policy_wanted": diag.get("policy_choice"),
        "incumbent": joint.get("incumbent"),
        "chosen": joint.get("chosen"),
        "reward_incumbent": r_inc,
        "reward_policy_choice": r_pol,
        "accepted": diag.get("verified_accepted"),
        "reverted_as_unnecessary": diag.get("reverted_as_unnecessary") or [],
        "flat_dimensions": diag.get("flat_dimensions") or [],
        "actions_evaluated": diag.get("joint_actions_evaluated"),
        "space_cardinality": diag.get("joint_space_cardinality"),
        "policy_choice_was_worse": (
            None if r_inc is None or r_pol is None else r_pol < r_inc),
    }


def warnings_for(proposal: Dict[str, Any], ev: Evidence) -> List[str]:
    """
    Everything a reviewer should be told without having to ask. Ordered most
    serious first, because a reviewer reads the top of a list and skims the rest.
    """
    out: List[str] = []

    if ev.is_regression:
        out.append(
            f"REGRESSION — this proposal scores LOWER than doing nothing "
            f"({ev.reward_proposed:+.6f} vs {ev.reward_incumbent:+.6f}, "
            f"delta {ev.delta:+.6f}). This is the §6n failure mode: an optimiser "
            f"proposing a change its own objective scores as worse. Approving it "
            f"degrades the control.")

    if ev.claim_matches is False:
        out.append(
            f"CLAIM MISMATCH — the proposal reports mean_reward="
            f"{ev.claimed_reward:+.6f}, but recomputing it here over "
            f"{ev.n_episodes} episodes gives {ev.reward_proposed:+.6f}. The "
            f"artifact does not describe the change it would make. Do not "
            f"approve until this is explained.")

    if ev.false_pos_proposed > ev.false_pos_incumbent:
        out.append(
            f"FALSE POSITIVES INCREASE — {ev.false_pos_incumbent} -> "
            f"{ev.false_pos_proposed}. Check these are not concentrated in the "
            f"externally-authored benign cohort (§6n: a marker weight that looked "
            f"free on hand-written controls produced 36 FPs of 68 on AgentDojo "
            f"data).")

    if ev.workflow_lost_proposed > ev.workflow_lost_incumbent:
        out.append(
            f"WORKFLOW LOST INCREASES — {ev.workflow_lost_incumbent} -> "
            f"{ev.workflow_lost_proposed}. The reward scores a blanket block "
            f"below a safe continuation, but it still scores it positive, so a "
            f"proposal can trade usability for detection and still look good.")

    if ev.is_neutral:
        out.append(
            "NO MEASURED BENEFIT — reward is unchanged to within tolerance. A "
            "change to a security threshold with no measurable gain is a change "
            "with only risk attached.")

    if ev.inert_patterns:
        out.append(
            f"INERT PATTERN — {ev.inert_patterns} matches no proposed_action in "
            f"the {ev.n_episodes}-episode batch, so adding it changes nothing. "
            f"3A matches blocked_patterns against the proposed_action, but the "
            f"trainer harvests candidates from flagged_markers, which describe "
            f"mediator content — different namespaces. A rule that reads as "
            f"protection and provides none is worse than no rule.")

    literals = [p for p in (proposal.get("new_blocked_patterns") or []) if "@" in p]
    if literals:
        out.append(
            f"LITERAL TARGETS IN PATTERNS — {literals}. Fix A removed literal "
            f"harvesting because it inflates before/after numbers by memorising "
            f"the training set. Their reappearance means something regressed.")

    if ev.n_episodes < 50:
        out.append(
            f"THIN EVIDENCE — {ev.n_episodes} episodes. Reward differences on a "
            f"batch this small are not distinguishable from sampling noise.")

    return out


def recommendation(ev: Evidence, warnings: List[str]) -> str:
    """
    A recommendation, never an action. The gate exists because an automated
    decision was the problem; it would be self-defeating for the gate to make
    one.
    """
    if ev.is_regression:
        return "REJECT — scores worse than the incumbent."
    if any(w.startswith("CLAIM MISMATCH") for w in warnings):
        return "REJECT — the proposal misreports its own effect."
    if ev.is_neutral:
        return "REJECT — no measured benefit; a no-op is the safe outcome."
    return "APPROVE is defensible — but read the warnings above first."


def append_decision(decision: Decision, path: str = DEFAULT_LOG) -> str:
    """Append-only. Decisions are never rewritten; a reversal is a new record."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "a") as f:
        f.write(json.dumps(asdict(decision)) + "\n")
    return path


def load_decisions(path: str = DEFAULT_LOG) -> List[Dict[str, Any]]:
    if not os.path.exists(path):
        return []
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]
