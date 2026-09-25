"""
The positioning table, and the two ways it could lie.

WHY THIS SUITE EXISTS. §10 is the only table in the paper that prints numbers we
did not measure, beside numbers we did. Both of its failure modes are silent and
both are the kind a reviewer checks first:

  - **Rendering a second-hand number about someone else's system.** A published
    figure that reached us through a search result, a summary or a memory reads
    identically to one read out of the paper. `external_numbers.json` therefore
    carries the verbatim quote and a `verified` flag, and the generator must
    drop anything not marked `verbatim` — silently rendering it would put a
    number we never checked into the manuscript under someone else's name.
  - **Filling a cell that has no artifact behind it.** Our column is computed
    from `results/`. A missing artifact must stop the run, not print a blank or
    a stale value, because a hole in a positioning table is indistinguishable
    from a measurement.

Also pinned: every published row carries a quote, `display` beats `value_pct` so
a bound stays a bound, and regeneration is idempotent.

    python3 -m pytest tests/test_positioning_table.py -v
"""

import importlib.util
import json
import os

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(REPO, "paper", "make_positioning_table.py")
EXTERNAL = os.path.join(REPO, "paper", "external_numbers.json")
SECTION = os.path.join(REPO, "paper", "10-positioning.md")


def _load_module():
    spec = importlib.util.spec_from_file_location("make_positioning_table", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


mod = _load_module()


# ---------------------------------------------------------------------------
# An unverified number about someone else's system never renders
# ---------------------------------------------------------------------------

def test_unverified_rows_are_dropped_not_rendered():
    kept, dropped = mod.external()
    for src in kept.values():
        for row in src["rows"]:
            assert row["verified"] == "verbatim"
    rendered = mod.render(mod.ours(), kept)
    for held in dropped:
        system = held.split(": ", 1)[1].split(" — ")[0]
        assert system not in rendered



def test_every_published_row_carries_a_quote():
    with open(EXTERNAL) as fh:
        data = json.load(fh)
    for src in data["sources"]:
        assert src["url"] and src["citation"]
        for row in src["rows"]:
            assert row.get("quote", "").strip(), f"{src['key']}: {row['system']}"


# ---------------------------------------------------------------------------
# A missing artifact stops the run
# ---------------------------------------------------------------------------

def test_missing_artifact_raises_rather_than_blanking_a_cell():
    with pytest.raises(SystemExit) as excinfo:
        mod.load("results/does_not_exist/benchmark.json")
    assert "missing artifact" in str(excinfo.value)


def test_missing_markers_refuse_to_guess_where_the_table_goes():
    text = open(SECTION).read()
    assert text.count(mod.BEGIN) == 1 and text.count(mod.END) == 1


# ---------------------------------------------------------------------------
# A bound stays a bound
# ---------------------------------------------------------------------------

def test_display_overrides_the_point_estimate():
    assert mod.shown({"value_pct": 80.0, "display": ">80%"}) == ">80%"
    assert mod.shown({"value_pct": 24.0}) == "24.0%"


# ---------------------------------------------------------------------------
# Our column is arithmetic on the artifacts, not typing
# ---------------------------------------------------------------------------

def test_our_cells_match_the_committed_artifacts():
    o = mod.ours()
    p12 = json.load(open(os.path.join(REPO, "results/phase12/benchmark.json")))
    asr = p12["summaries"]["undefended"]["asr"]
    assert f"{asr['k']}/{asr['n']}" in o["p12_undef"]

    nf = json.load(open(os.path.join(REPO, "results/noise_floor/injecagent.json")))
    runs = sorted(r["hits"] for r in nf["summary"]["by_family"]["IA-target"]["per_run"])
    assert f"{runs[len(runs) // 2]}/30" in o["ia_target"]


def test_strata_are_reported_separately():
    """The 30/30 draw over a 51/459 population makes any pooled InjecAgent cell
    wrong by 33 points. There must be no pooled detection row."""
    o = mod.ours()
    assert o["ia_target"] != o["ia_notarget"]
    rendered = mod.render(o, mod.external()[0])
    assert "target-bearing stratum" in rendered and "no-target stratum" in rendered
    assert "60/60" not in rendered.split("### B.")[1].split("### C.")[0]


def test_wilson_matches_the_committed_intervals():
    """Our helper must agree with the intervals evaluation/ already computed —
    two interval implementations disagreeing is how a table drifts from a figure."""
    nf = json.load(open(os.path.join(REPO, "results/noise_floor/injecagent.json")))
    run = nf["summary"]["by_family"]["IA-notarget"]["per_run"][0]
    _, lo, hi = mod.wilson(run["hits"], run["n"])
    assert lo == pytest.approx(run["ci_low"], abs=1e-9)
    assert hi == pytest.approx(run["ci_high"], abs=1e-9)


# ---------------------------------------------------------------------------
# Regeneration is idempotent
# ---------------------------------------------------------------------------

def test_regeneration_is_idempotent():
    before = open(SECTION).read()
    mod.main()
    after = open(SECTION).read()
    assert before == after, "the table changed without an artifact changing"
