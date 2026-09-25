"""
The run-to-run noise floor, and the two ways it could lie.

WHY THIS SUITE EXISTS. `noise_floor.py` produces a number whose whole purpose is
to tell a reader how much to trust other numbers. Both of its failure modes are
silent:

  - **Pooling k runs as independent observations.** k recordings of 60 documents
    are not 60k observations. Pooling divides the interval by sqrt(k) and
    manufactures precision the measurement does not have — and it would look
    like a *better* result, which is why nothing downstream would question it.
  - **Pooling strata.** For InjecAgent the family IS the stratum, and the 30/30
    draw over a 51/459 population gives a pooled figure wrong for that corpus by
    33 points (Phase 12). A report that prints only the pooled row reports the
    sampling design rather than the system.

Both are pinned below. The stability classification is pinned too, because a
spread of ±2 means something different if two documents flip every run than if
twenty flip occasionally, and the classifier is what separates those.

    python3 -m pytest tests/test_noise_floor.py -v
"""

import pytest

from evaluation import noise_floor
from evaluation.noise_floor import ALWAYS, NEVER, UNSTABLE


def cell(fired, family="f", malicious=False):
    """One case's row: {run: fired} plus the fields the summary reads."""
    return {
        "fired": dict(enumerate(fired)),
        "n_fired": sum(1 for v in fired if v),
        "n_runs": len(fired),
        "stability": (ALWAYS if all(fired)
                      else (NEVER if not any(fired) else UNSTABLE)),
        "family": family,
        "expected_malicious": malicious,
    }


# ---------------------------------------------------------------------------
# Runs are never pooled
# ---------------------------------------------------------------------------

def test_interval_is_per_run_not_pooled():
    """
    🔴 The Wilson interval must be computed over n CASES, not n*k observations.

    Three runs of 60 documents with 2 firing each is not 6/180. Pooling would
    report [1.5%, 5.9%] instead of [0.9%, 11.4%] — a tighter interval that the
    measurement does not support, and one that would make a one-case difference
    between arms look resolvable when it is not.
    """
    cells = {f"c{i}": cell([i < 2, i < 2, i < 2]) for i in range(60)}
    summary = noise_floor.summarize(cells)

    assert summary["n_runs"] == 3
    assert summary["n_cases"] == 60
    for row in summary["per_run"]:
        assert row["n"] == 60, "interval denominator must be cases, not cases*runs"
        assert row["hits"] == 2
    # The committed AgentDojo interval, which pooling would tighten.
    assert summary["per_run"][0]["ci_high"] == pytest.approx(0.114, abs=0.005)


def test_spread_is_reported_separately_from_the_interval():
    """The two uncertainties are different and must not be merged."""
    cells = {f"c{i}": cell([i < 2, i < 4, i < 3]) for i in range(60)}
    summary = noise_floor.summarize(cells)
    assert summary["spread"]["min_hits"] == 2
    assert summary["spread"]["max_hits"] == 4
    assert summary["spread"]["range_hits"] == 2
    assert "ci_low" not in summary["spread"]


# ---------------------------------------------------------------------------
# Strata are never pooled
# ---------------------------------------------------------------------------

def test_strata_are_reported_separately():
    """
    ⛔ Phase 12's rule, enforced in code.

    A balanced 30/30 draw over a 51/459 population pools to a figure wrong for
    the population by 33 points. `by_family` must carry each stratum's own rate.
    """
    cells = {}
    for i in range(30):                       # target stratum: 29/30 detected
        cells[f"t{i}"] = cell([i < 29], family="IA-target", malicious=True)
    for i in range(30):                       # no-target stratum: 4/30
        cells[f"n{i}"] = cell([i < 4], family="IA-notarget", malicious=True)

    summary = noise_floor.summarize(cells)

    assert summary["stratified"] is True
    by_family = summary["by_family"]
    assert by_family["IA-target"]["per_run"][0]["rate"] == pytest.approx(29 / 30)
    assert by_family["IA-notarget"]["per_run"][0]["rate"] == pytest.approx(4 / 30)

    # And the pooled row is a long way from both — which is the whole point.
    pooled = summary["per_run"][0]["rate"]
    assert pooled == pytest.approx(33 / 60)
    assert abs(pooled - 4 / 30) > 0.30


def test_single_stratum_cohort_is_not_marked_stratified():
    """The benign cohort is one family; the pooled row IS its answer."""
    cells = {f"c{i}": cell([i < 2], family="benign") for i in range(60)}
    summary = noise_floor.summarize(cells)
    assert summary["stratified"] is False
    assert list(summary["by_family"]) == ["benign"]


def test_per_family_denominators_are_the_family_size():
    cells = {}
    for i in range(30):
        cells[f"t{i}"] = cell([True], family="A")
    for i in range(10):
        cells[f"n{i}"] = cell([False], family="B")
    summary = noise_floor.summarize(cells)
    assert summary["by_family"]["A"]["per_run"][0]["n"] == 30
    assert summary["by_family"]["B"]["per_run"][0]["n"] == 10


# ---------------------------------------------------------------------------
# Stability: the classification that makes a spread interpretable
# ---------------------------------------------------------------------------

def test_stability_classes():
    cells = {
        "always": cell([True, True, True]),
        "never": cell([False, False, False]),
        "unstable": cell([True, False, True]),
    }
    summary = noise_floor.summarize(cells)
    assert summary["stability"] == {ALWAYS: 1, NEVER: 1, UNSTABLE: 1}
    assert summary["unstable_cases"] == ["unstable"]


def test_a_stable_count_can_hide_churning_membership():
    """
    🔴 The measured AgentDojo result, pinned.

    Every run fires exactly twice, so the count looks perfectly reproducible —
    and two of the three documents involved are unstable. A report that showed
    only the rate would call this noise-free. The distinction is the finding.
    """
    cells = {
        "stable-fp": cell([True, True, True]),
        "borderline-a": cell([False, True, True]),
        "borderline-b": cell([True, False, False]),
    }
    cells.update({f"quiet{i}": cell([False, False, False]) for i in range(57)})

    summary = noise_floor.summarize(cells)
    assert summary["spread"]["range_hits"] == 0, "the count does not move"
    assert summary["stability"][UNSTABLE] == 2, "but two documents do"


def test_empty_input_is_not_a_crash():
    assert noise_floor.summarize({}) == {}
