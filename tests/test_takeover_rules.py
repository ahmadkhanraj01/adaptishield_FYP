"""
Regression tests for 3B's takeover rules (root README Sections 6f-6h).

Fast and deterministic — the four probe regimes are patched out, so no Ollama
and no GPU. This is the kind of test the rest of `tests/` should look like:
the LLM-dependent checks live in `evaluation/` because they cost minutes and
vary run to run, while the decision logic they wrap is pure and can be pinned
exactly.

The bug: drift fired `Takeover=True` on a boundary where every regime scored
0. Two independent causes, one test each below —

  1. `boundary_history` was a single flat list, so the slope was computed
     across unrelated red-team cases from different attack families.
  2. Nothing required the *current* boundary to show any signal, so "nothing
     observed" could mean takeover.

    python3 -m pytest tests/test_takeover_rules.py -v
"""

from unittest.mock import patch

from layer2.security_sublayer.causal_analyzer import CausalAnalyzer, BoundaryOutcome

# Severity per regime. `masked` is the one the guard reads.
ALL_ZERO = {"orig": 0.0, "masked": 0.0, "masked_sanitized": 0.0, "orig_sanitized": 0.0}
MASKED_1 = {"orig": 0.0, "masked": 1.0, "masked_sanitized": 1.0, "orig_sanitized": 0.0}

# ace 1.5 -> 1.0 -> (current), i.e. the falling slope observed in the wild
# when three unrelated campaign cases ran through one analyzer.
FALLING_ACE = [(1.5, 0.0), (1.0, 0.0)]


def _analyzer_with(severities, history, session_id):
    """A CausalAnalyzer whose regimes return fixed severities, no LLM."""
    ca = CausalAnalyzer()
    ca.session_history[session_id] = list(history)

    def fake_regime(regime, user_input, mediator):
        return BoundaryOutcome(severity=severities[regime], proposed_action="x",
                               regime=regime, samples=[severities[regime]],
                               raw_actions=["x"])

    ca._sanitize_mediator = lambda mediator, user_goal: "sanitised"
    ca._run_regime = fake_regime
    return ca


def test_empty_boundary_does_not_fire_drift():
    """The Section 6g bug: nothing measured must never mean takeover."""
    ca = _analyzer_with(ALL_ZERO, FALLING_ACE, "s1")
    diag = ca.evaluate_boundary("u", "m", boundary_index=4, session_id="s1")

    assert diag.masked_severity == 0.0
    assert diag.takeover is False, (
        "drift fired on a boundary where every regime scored 0 — a falling ACE "
        "slope alone must not be sufficient")


def test_genuine_drift_still_fires():
    """The guard must not disable the rule when there IS signal."""
    ca = _analyzer_with(MASKED_1, FALLING_ACE, "s1")
    diag = ca.evaluate_boundary("u", "m", boundary_index=4, session_id="s1")

    assert diag.takeover is True
    assert "Temporal drift" in diag.reason


def test_drift_does_not_leak_across_sessions():
    """
    Campaign cases are unrelated conversations. A slope accumulated under one
    session must not influence another, or caught_by_causal is inflated by
    coincidence.
    """
    ca = _analyzer_with(MASKED_1, FALLING_ACE, "other-case")
    diag = ca.evaluate_boundary("u", "m", boundary_index=4, session_id="my-case")

    assert diag.takeover is False, "drift leaked from an unrelated session"


def test_history_is_recorded_per_session():
    ca = _analyzer_with(ALL_ZERO, [], "case-a")
    ca.evaluate_boundary("u", "m", boundary_index=1, session_id="case-a")
    ca.evaluate_boundary("u", "m", boundary_index=2, session_id="case-b")

    assert len(ca.session_history["case-a"]) == 1
    assert len(ca.session_history["case-b"]) == 1


# ── IE-rule sample consistency (root README Section 6h) ──────────

def _analyzer_with_samples(samples, session_id="s"):
    """
    CausalAnalyzer whose regimes return explicit per-sample scores, so the
    mean-vs-consistency distinction is testable. `samples` maps regime -> list.
    """
    from statistics import mean as _mean
    ca = CausalAnalyzer()

    def fake_regime(regime, user_input, mediator):
        s = samples[regime]
        return BoundaryOutcome(severity=_mean(s), proposed_action="x",
                               regime=regime, samples=list(s), raw_actions=["x"] * len(s))

    ca._sanitize_mediator = lambda mediator, user_goal: "sanitised"
    ca._run_regime = fake_regime
    return ca


def test_inconsistent_ie_separation_is_suppressed():
    """
    The Section 6h false positive: masked=[1,1] vs masked_san=[1,0] gives
    IE=0.5, which clears the threshold on the mean while one sample disagrees.
    Paraphrase noise must not manufacture a takeover.
    """
    ca = _analyzer_with_samples({
        "orig": [0, 0], "masked": [1, 1],
        "masked_sanitized": [1, 0], "orig_sanitized": [0, 0],
    })
    diag = ca.evaluate_boundary("u", "m", boundary_index=1, session_id="s")

    assert diag.ie == 0.5, "precondition: IE still clears the threshold on the mean"
    assert diag.takeover is False
    assert "inconsistent" in diag.reason


def test_consistent_ie_separation_still_fires():
    """A real contrast — every masked sample outscores every sanitized one."""
    ca = _analyzer_with_samples({
        "orig": [0, 0], "masked": [2, 2],
        "masked_sanitized": [0, 0], "orig_sanitized": [0, 0],
    })
    diag = ca.evaluate_boundary("u", "m", boundary_index=1, session_id="s")

    assert diag.takeover is True
    assert "mediator-driven" in diag.reason


def test_partial_sanitisation_still_fires():
    """masked=[2,2] vs masked_san=[1,0]: still a consistent separation."""
    ca = _analyzer_with_samples({
        "orig": [0, 0], "masked": [2, 2],
        "masked_sanitized": [1, 0], "orig_sanitized": [0, 0],
    })
    diag = ca.evaluate_boundary("u", "m", boundary_index=1, session_id="s")

    assert diag.takeover is True


def test_standalone_masked_rule_survives_ie_suppression():
    """
    Full compliance in both regimes: IE=0 and the separation is inconsistent,
    but masked=2 must still fire the standalone rule (Section 6f). The
    consistency guard must not be able to suppress strong evidence.
    """
    ca = _analyzer_with_samples({
        "orig": [0, 0], "masked": [2, 2],
        "masked_sanitized": [2, 2], "orig_sanitized": [0, 0],
    })
    diag = ca.evaluate_boundary("u", "m", boundary_index=1, session_id="s")

    assert diag.ie == 0.0
    assert diag.takeover is True
    assert "masked severity" in diag.reason


# ── IE resolution the grid 3D steps on (root README Section 6d) ──

def test_ie_resolution_tracks_k_samples():
    """IE is quantized to 1/k_samples; 3D reads this to size its step so a move
    is never finer than the metric can resolve (Section 6d point 1)."""
    assert CausalAnalyzer(k_samples=2).ie_resolution == 0.5
    assert CausalAnalyzer(k_samples=4).ie_resolution == 0.25
