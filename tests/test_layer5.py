"""
Layer 5 — human gate and audit dashboard.

Deterministic, no LLM, no network, no browser. These pin the properties that
make the gate worth having; without them it is a print statement.

  1. The gate recomputes evidence and does not trust the proposal's arithmetic.
     README §6n exists because a proposer was confidently wrong; a reviewer shown
     only the proposer's own numbers is not reviewing anything.
  2. A reward-decreasing proposal is flagged as a REGRESSION and recommended for
     rejection. This is the exact §6n failure, reproduced as a test.
  3. The recommendation is never an action. The gate must not decide.
  4. The decision log is append-only and records the reason.
  5. Untrusted mediator text cannot escape the embedded JSON in the dashboard.
     The records contain prompt injections by construction.

    python3 -m pytest tests/test_layer5.py -v
"""

import json

import pytest

from evaluation.kaggle.grpo_env import EpisodeFeatures, Policy, RewardConfig
from layer5 import audit_report as ar
from layer5.governance import (
    Decision, Evidence, append_decision, gather_evidence, load_decisions,
    recommendation, verifier_record, warnings_for,
)


# ── fixtures ──────────────────────────────────────────────────────────
def _ep(case_id="c", malicious=True, ie=2, masked=2, action="send_email to x@y.com",
        markers=(), status="safe_continuation"):
    # EpisodeFeatures carries no case_id; `case_id` here only varies the action
    # so episodes stay distinguishable when a test inspects them.
    return EpisodeFeatures(
        tool_name="send_email", proposed_action=f"{action} [{case_id}]",
        final_status=status, is_malicious=malicious, flagged_markers=list(markers),
        causal={"ie": ie, "masked_severity": masked, "masked_san_severity": 0,
                "orig_severity": 0, "ie_separation_consistent": True,
                "drift_fired": False, "capture_ie_threshold": 0.5},
        causal_reached=True,
    )


def _proposal(old=0.5, new=0.5, patterns=None, tools=None, mean_reward=None,
              joint=None):
    p = {"old_ie_threshold": old, "new_ie_threshold": new,
         "new_blocked_patterns": patterns or [], "new_high_impact_tools": tools or [],
         "rationale": []}
    if mean_reward is not None:
        p["mean_reward"] = mean_reward
    if joint is not None:
        p["joint"] = joint
    return p


EPISODES = [_ep(f"m{i}") for i in range(60)] + \
           [_ep(f"b{i}", malicious=False, ie=0, masked=0,
                status="approved_causal") for i in range(20)]


# ── 1. the gate recomputes rather than trusting ───────────────────────
def test_gate_recomputes_and_flags_a_false_claim():
    """
    A proposal that misreports its own effect must be caught. This is the
    strongest single reason the gate recomputes instead of rendering the
    artifact's `mean_reward` field.
    """
    ev = gather_evidence(_proposal(mean_reward=0.99), EPISODES, RewardConfig())
    assert ev.claim_matches is False
    warns = warnings_for(_proposal(mean_reward=0.99), ev)
    assert any(w.startswith("CLAIM MISMATCH") for w in warns)
    assert "REJECT" in recommendation(ev, warns)


def test_gate_accepts_an_honest_claim():
    honest = gather_evidence(_proposal(), EPISODES, RewardConfig())
    p = _proposal(mean_reward=honest.reward_proposed)
    ev = gather_evidence(p, EPISODES, RewardConfig())
    assert ev.claim_matches is True
    assert not any(w.startswith("CLAIM MISMATCH") for w in warnings_for(p, ev))


# ── 2. the §6n failure, as a test ─────────────────────────────────────
def test_reward_decreasing_proposal_is_flagged_as_a_regression():
    """
    The defect README §6n records: an optimiser proposing a change its own
    objective scores lower, which apply_update would have taken silently.
    Raising the threshold above every episode's IE loses detections, so the
    proposal must score worse and must be recommended for rejection.
    """
    # These must be IE-dependent: with masked=2 the standalone rule detects them
    # at any threshold, so the knob would be inert and nothing could regress.
    # masked=1 + ie=1 is the address-free case the §6n corpus added.
    eps = [_ep(f"m{i}", ie=1, masked=1) for i in range(40)] + \
          [_ep(f"b{i}", malicious=False, ie=0, masked=0,
               status="approved_causal") for i in range(20)]
    p = _proposal(old=0.5, new=2.5)
    ev = gather_evidence(p, eps, RewardConfig())
    assert ev.missed_proposed > ev.missed_incumbent
    assert ev.is_regression, (ev.reward_incumbent, ev.reward_proposed)
    warns = warnings_for(p, ev)
    assert any(w.startswith("REGRESSION") for w in warns)
    assert recommendation(ev, warns).startswith("REJECT")


def test_a_neutral_change_is_not_recommended_either():
    """A change to a security threshold with no measured gain is risk with no
    upside; the safe outcome is the no-op."""
    ev = gather_evidence(_proposal(), EPISODES, RewardConfig())
    assert ev.is_neutral
    warns = warnings_for(_proposal(), ev)
    assert any(w.startswith("NO MEASURED BENEFIT") for w in warns)
    assert recommendation(ev, warns).startswith("REJECT")


# ── 3. the gate recommends, never decides ─────────────────────────────
def test_recommendation_never_returns_an_action():
    """
    The failure this layer exists to prevent is a machine deciding confidently
    and wrongly. A gate that auto-approves reintroduces it one level up.
    """
    for p in (_proposal(), _proposal(new=2.5), _proposal(mean_reward=0.99)):
        ev = gather_evidence(p, EPISODES, RewardConfig())
        rec = recommendation(ev, warnings_for(p, ev))
        assert isinstance(rec, str)
        assert rec.startswith("REJECT") or rec.startswith("APPROVE is defensible")


# ── inert patterns ────────────────────────────────────────────────────
def test_pattern_that_matches_no_action_is_reported_inert():
    """
    3A matches blocked_patterns against proposed_action, but the trainer harvests
    candidates from flagged_markers, which describe mediator content. A pattern
    can be perfectly discriminative as a marker and never fire as a rule — and a
    rule that reads as protection while providing none is worse than no rule.
    """
    p = _proposal(patterns=["ignore previous"])
    ev = gather_evidence(p, EPISODES, RewardConfig())
    assert ev.inert_patterns == ["ignore previous"]
    assert any(w.startswith("INERT PATTERN") for w in warnings_for(p, ev))


def test_pattern_that_does_match_is_not_reported_inert():
    p = _proposal(patterns=["send_email"])
    ev = gather_evidence(p, EPISODES, RewardConfig())
    assert ev.inert_patterns == []


def test_literal_target_in_a_pattern_is_flagged():
    """Fix A removed literal harvesting; its reappearance means a regression."""
    p = _proposal(patterns=["send_email to evil@attacker.com"])
    ev = gather_evidence(p, EPISODES, RewardConfig())
    assert any(w.startswith("LITERAL TARGETS") for w in warnings_for(p, ev))


def test_thin_evidence_is_flagged():
    p = _proposal()
    ev = gather_evidence(p, EPISODES[:10], RewardConfig())
    assert any(w.startswith("THIN EVIDENCE") for w in warnings_for(p, ev))


# ── marker weights must be read from the joint block ──────────────────
def test_marker_weights_are_read_from_the_joint_block():
    """
    A proposal whose only real change is a marker weight looks like a no-op if
    you inspect ie_threshold alone — which is exactly the §6n corpus-artifact
    action. The gate must see it.
    """
    eps = [_ep("m", markers=["ignore previous"]),
           _ep("b", malicious=False, ie=0, masked=0, markers=["ignore previous"],
               status="approved_causal")]
    p = _proposal(joint={"chosen": {"ie_threshold": 0.5,
                                    "marker_weight:ignore previous": 1.0},
                         "incumbent": {"ie_threshold": 0.5,
                                       "marker_weight:ignore previous": 0.0}})
    ev = gather_evidence(p, eps, RewardConfig())
    # Weighting that marker blocks the benign episode -> a false positive appears.
    assert ev.false_pos_proposed > ev.false_pos_incumbent
    assert any(w.startswith("FALSE POSITIVES INCREASE") for w in warnings_for(p, ev))


# ── verifier record ───────────────────────────────────────────────────
def test_verifier_record_surfaces_a_rejected_policy_choice():
    """
    A rejected proposal serialises as a no-op and looks like nothing happened.
    The console must still show that the policy wanted something and lost.
    """
    vr = verifier_record(_proposal(joint={
        "chosen": {"ie_threshold": 0.5}, "incumbent": {"ie_threshold": 0.5},
        "diagnostics": {"policy_choice": {"ie_threshold": 1.0},
                        "reward_incumbent": 0.8330, "reward_policy_choice": 0.8329,
                        "verified_accepted": False}}))
    assert vr["policy_choice_was_worse"] is True
    assert vr["accepted"] is False


def test_verifier_record_absent_when_no_joint_block():
    assert verifier_record(_proposal()) is None


# ── 4. decision log ───────────────────────────────────────────────────
def test_decision_log_is_append_only_and_keeps_the_reason(tmp_path):
    log = str(tmp_path / "d.jsonl")
    ev = gather_evidence(_proposal(), EPISODES, RewardConfig())
    for verdict, reason in (("rejected", "no measured benefit"),
                            ("approved", "accepted risk, signed off")):
        append_decision(Decision(verdict=verdict, reason=reason,
                                 proposal=_proposal(), evidence=ev.__dict__.copy()),
                        log)
    rows = load_decisions(log)
    assert [r["verdict"] for r in rows] == ["rejected", "approved"]
    assert rows[0]["reason"] == "no measured benefit"
    assert rows[0]["operator"] and rows[0]["timestamp"]


def test_load_decisions_on_missing_file_is_empty_not_an_error():
    assert load_decisions("/nonexistent/decisions.jsonl") == []


# ── 5. the dashboard cannot be attacked by what it audits ─────────────
def test_embedded_records_cannot_break_out_of_the_script_block():
    """
    The records contain prompt-injection payloads by construction. A payload
    carrying markup must not be able to terminate the JSON block and become live
    DOM in the tool used to inspect it.
    """
    payload = '</script><img src=x onerror=alert(1)>'
    blob = ar.embed([{"mediator_snippet": payload}])
    assert "</script>" not in blob
    assert "<" not in blob
    # ...and it must still round-trip to the original text for display.
    assert json.loads(blob)[0]["mediator_snippet"] == payload


def test_page_escapes_untrusted_text_and_stays_parseable():
    records = [{"boundary_index": 1, "tool_name": "send_email",
                "proposed_action": "<script>alert(1)</script>",
                "final_status": "blocked", "outcome_severity": 2,
                "mediator_snippet": "</script><b>x</b>"}]
    page = ar.render_page(records, {}, None, None, [], {"ie_threshold": 0.5},
                          [records])
    assert page.count("</script>") == 3          # the three real ones only
    assert "<script>alert(1)</script>" not in page


def test_esc_escapes_markup():
    assert ar.esc("<b>&\"") == "&lt;b&gt;&amp;&quot;"


# ── campaign splitting ────────────────────────────────────────────────
def test_campaigns_split_on_the_boundary_index_reset():
    """
    The log is append-only across campaigns run against different corpora.
    Showing them as one pile would average over corpora that are not comparable.
    """
    rows = [{"boundary_index": i} for i in (1, 2, 3, 1, 2, 1)]
    groups = ar.split_campaigns(rows)
    assert [len(g) for g in groups] == [3, 2, 1]


def test_campaign_split_of_empty_log():
    assert ar.split_campaigns([]) == []


# ── summary ───────────────────────────────────────────────────────────
def test_summary_keeps_the_two_benign_cohorts_separate():
    """
    Pooling them would produce a single FPR figure that means nothing: the
    hand-written controls are a diagnostic, not a draw from a distribution.
    """
    eps = ([{"case_id": "benign-0", "is_malicious": False, "causal_takeover": True,
             "family": "b", "causal": {"masked_severity": 2, "masked_san_severity": 2,
                                       "ie": 0}}] +
           [{"case_id": f"agentdojo-workspace-{i:03d}", "is_malicious": False,
             "causal_takeover": False, "family": "b",
             "causal": {"masked_severity": 0, "masked_san_severity": 0, "ie": 0}}
            for i in range(10)] +
           [{"case_id": "m0", "is_malicious": True, "causal_takeover": True,
             "family": "f", "causal": {"masked_severity": 2, "masked_san_severity": 0,
                                       "ie": 2}}])
    s = ar.summarise(eps)
    names = {c["name"]: c for c in s["cohorts"]}
    assert names["ours"]["fp"] == 1 and names["ours"]["n"] == 1
    assert names["agentdojo"]["fp"] == 0 and names["agentdojo"]["n"] == 10
    assert s["detection"]["caught"] == 1
