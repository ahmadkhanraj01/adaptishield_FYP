"""
Phase 15 — the multi-turn cohort, the drift-only predicate, and the two-line
change that lets a corpus have sessions.

WHY THIS SUITE EXISTS AT ALL. Every failure mode in this phase produces a
*plausible number* rather than an error, and three of them produce the SAME
number — zero drift-only catches — for entirely different reasons:

  - the session never accumulated history (a fresh analyzer per case, or a turn
    that never reached 3B), so the window was never full
  - `drift_only` counted an ordinary standalone catch as a drift catch, or
    missed a real one
  - the content genuinely did not elicit the profile — the only one of the three
    that is a result

A null is half the point of this phase, so the other two have to be excluded by
construction rather than by inspecting the output afterwards.

THE REGRESSION THAT MATTERS MOST. `RedTeamCase.session_id` defaults to None and
`ExecutionAgent` falls back to `case_id`. If that default ever flips, every
corpus in this project silently starts sharing drift history across unrelated
attack families — which is precisely the §6g defect that fired takeover on
boundaries where nothing was measured, and it would inflate `caught_by_causal`
everywhere at once with no test failing anywhere else.

    python3 -m pytest tests/test_multiturn.py -v
"""

import pytest

from evaluation import multiturn
from layer2.security_sublayer.causal_analyzer import CausalAnalyzer
from red_team.attack_generator import RedTeamCase


@pytest.fixture
def analyzer():
    return CausalAnalyzer(semantic_scoring=False)


# ---------------------------------------------------------------------------
# The default that keeps every pre-Phase-15 number reproducible
# ---------------------------------------------------------------------------

def test_session_id_defaults_to_none():
    """
    🔴 The whole backward-compatibility guarantee is this default.

    None means "this case is its own conversation", the ExecutionAgent falls
    back to `case_id`, and every corpus recorded before Phase 15 behaves exactly
    as it did. A default of anything else would make unrelated red-team cases
    share a drift history — the §6g defect, reintroduced globally.
    """
    case = RedTeamCase(
        case_id="c1", family="f", expected_malicious=True, user_input="u",
        tool_response="t", tool_name="send_email", proposed_action="a",
        server_name="email-api", destination_url="https://x", description="d")
    assert case.session_id is None


def test_multiturn_cases_carry_their_session():
    cases = multiturn.as_cases()
    for case in cases:
        assert case.session_id is not None
        assert case.case_id.startswith(case.session_id)


def test_turns_of_one_session_share_a_session_id():
    """Three turns, one conversation — the property the drift rule needs."""
    session = multiturn.SESSIONS[0]
    cases = multiturn.as_cases([session])
    assert len({c.session_id for c in cases}) == 1
    assert len(cases) == len(session.turns) >= 3


def test_case_order_is_turn_order():
    """
    Order is load-bearing here and nowhere else in this project.

    Turn 3's verdict depends on turns 1 and 2 already sitting in the history, so
    a reordered or filtered run measures something different without erroring.
    """
    cases = multiturn.as_cases()
    expected = [f"{s.sid}-t{i}"
                for s in multiturn.all_sessions()
                for i in range(1, len(s.turns) + 1)]
    assert [c.case_id for c in cases] == expected


def test_every_session_has_enough_turns_to_fill_the_window(analyzer):
    """A session shorter than `window_size` cannot fire the rule at all."""
    for session in multiturn.all_sessions():
        assert len(session.turns) >= analyzer.window_size, session.sid


# ---------------------------------------------------------------------------
# The drift-only predicate, which is computed by differencing the shipped rule
# ---------------------------------------------------------------------------

def test_positive_controls(analyzer):
    """
    The four deterministic controls, which are what keep a null interpretable.

    If these pass and the live cohort fires nothing, the content did not elicit
    the profile. If these fail, the harness is broken and the live result means
    nothing either way.
    """
    for name, severities, expect in multiturn.control_sessions():
        rows = multiturn.trajectory(analyzer, severities, f"control-{name}")
        assert any(r["drift_only"] for r in rows) is expect, name


def test_standalone_catch_is_not_counted_as_drift(analyzer):
    """
    An ordinary catch must not be credited to drift.

    This is the failure that would manufacture the headline: turn 3 scores
    masked=2, the standalone rule fires, and a predicate that merely asked "was
    it caught, and was the history full?" would report a drift-only catch.
    """
    rows = multiturn.trajectory(
        analyzer, [(1, 0, 0), (1, 1, 1), (0, 2, 2)], "standalone")
    assert rows[-1]["takeover"] is True
    assert rows[-1]["single_boundary_takeover"] is True
    assert rows[-1]["drift_only"] is False


def test_drift_only_requires_history(analyzer):
    """
    The same boundary, with and without its history — only one is a catch.

    This is the differencing that `drift_only` relies on, asserted directly:
    with `history=[]` the drift branch cannot fire because `len(history) >=
    window_size` is false, so any difference is attributable to drift alone.
    """
    severities = [(1, 0, 0), (1, 1, 1), (0, 1, 1)]
    with_history = multiturn.trajectory(analyzer, severities, "s")
    assert with_history[-1]["drift_only"] is True
    assert with_history[-1]["single_boundary_takeover"] is False

    # The judged turn alone, no history: nothing fires.
    alone = multiturn.trajectory(analyzer, severities[-1:], "s")
    assert alone[-1]["takeover"] is False


def test_nothing_observed_never_means_takeover(analyzer):
    """
    §6g's regression, re-pinned on the path that can now actually reach it.

    A steeply falling ACE with every severity at zero was the original defect —
    the slope came from unrelated cases and nothing was measured on the boundary
    being judged. `masked >= 1` is the guard, and Phase 15 is the first cohort
    where a legitimate falling slope exists to test it against.
    """
    rows = multiturn.trajectory(
        analyzer, [(2, 0, 0), (1, 0, 0), (0, 0, 0)], "nothing")
    assert not any(r["takeover"] for r in rows)


def test_flat_trajectory_does_not_fire(analyzer):
    """A longer conversation must not be mistaken for an escalating one."""
    rows = multiturn.trajectory(
        analyzer, [(1, 0, 0)] * 5, "flat")
    assert not any(r["drift_only"] for r in rows)


# ---------------------------------------------------------------------------
# The cohort's design intent, pinned so an edit to the content is visible
# ---------------------------------------------------------------------------

def test_design_check_holds(analyzer):
    """
    Every malicious session's TARGET trajectory yields a drift-only catch, and
    every benign one does not.

    Pinned so that editing a session's declared target — which is a change to a
    pre-registered artifact — fails a test rather than passing quietly.
    """
    for session in multiturn.all_sessions():
        rows = multiturn.trajectory(
            analyzer, [t.target for t in session.turns], session.sid)
        assert any(r["drift_only"] for r in rows) is session.expected_malicious, \
            session.sid


def test_malicious_targets_stay_below_the_standalone_rule(analyzer):
    """
    No malicious turn may target `masked >= 2`.

    A data-movement verb would trip the standalone rule on turn 3 alone and the
    session would say nothing about drift — Phase 7's "equal by construction"
    failure, in a new place.
    """
    for session in multiturn.SESSIONS:
        for turn in session.turns:
            assert turn.target[1] < analyzer.masked_takeover_threshold, session.sid


def test_malicious_targets_keep_ie_below_threshold(analyzer):
    """
    IE must stay under the threshold at the judged turn, or the IE rule catches
    it and drift is untested. Holding IE at 0 with masked=1 is what forces
    masked_san=1 — the injection surviving sanitisation.
    """
    for session in multiturn.SESSIONS:
        for turn in session.turns:
            _, masked, masked_san = turn.target
            assert masked - masked_san < analyzer.ie_threshold, session.sid


def test_cohort_has_both_polarities():
    """
    Benign controls are the guard criterion and cannot be dropped.

    Phase 11 showed FPR can move where no p-value looks — `FPR ours` went 0/3 to
    3/3 the moment 3B switched on, invisible to every paired test because they
    exclude benign cases by construction.
    """
    assert any(s.expected_malicious for s in multiturn.all_sessions())
    assert any(not s.expected_malicious for s in multiturn.all_sessions())
