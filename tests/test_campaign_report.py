"""
Structural tests for `evaluation/campaign_report.py`.

The campaign artifact is the paper's in-corpus headline — 116/120 = 96.7% — and
it is assembled from checkpoints that live in gitignored `logs/`. Two things
therefore have to be pinned by tests rather than by inspection.

  1. THE ARTIFACT MUST RECOMPUTE FROM ITSELF. Rules §7's scar is a statistic
     whose inputs existed only in a gitignored checkpoint. Committing `per_case`
     is the fix, and it is only a fix if every rate in `summary` can be derived
     from it. `test_summary_recomputes_from_per_case` is that proof, and it runs
     on a fresh clone with no logs, no models and no GPU.

  2. THE NEVER-POOL GUARD MUST ACTUALLY REFUSE. `4/8` was read as a
     false-positive rate once. `_assert_unpooled` exists so this file cannot
     reintroduce it, and a guard nobody tests is a guard that silently stops
     guarding.

    python3 -m pytest tests/test_campaign_report.py -v
"""

import json
import os

import pytest

from evaluation import campaign_report as cr

ARTIFACT = os.path.join(cr.OUT_DIR, "campaign.json")

pytestmark = pytest.mark.skipif(
    not os.path.exists(ARTIFACT),
    reason="results/campaign/campaign.json not built yet")


@pytest.fixture(scope="module")
def artifact():
    with open(ARTIFACT) as f:
        return json.load(f)


# ── the artifact recomputes from its own committed inputs ─────────────
def test_summary_recomputes_from_per_case(artifact):
    """Every headline rate, rebuilt from per_case alone — no logs, no models."""
    cases = artifact["per_case"]
    summary = artifact["summary"]

    malicious = [c for c in cases.values() if c["expected_malicious"]]
    detected = sum(1 for c in malicious if c["causal_takeover"])
    succeeded = sum(1 for c in malicious if c["attack_succeeded"])

    assert len(malicious) == summary["n_malicious"]
    assert detected == summary["detection"]["hits"]
    assert succeeded == summary["asr"]["hits"]

    for family, key in cr.BENIGN_COHORTS.items():
        cohort = [c for c in cases.values() if c["family"] == family]
        fired = sum(1 for c in cohort if c["false_positive"])
        assert len(cohort) == summary["benign"][key]["n"]
        assert fired == summary["benign"][key]["hits"]


def test_the_headline_is_the_one_the_paper_quotes(artifact):
    """116/120 with the interval §VII prints. A silent drift here is a wrong paper."""
    det = artifact["summary"]["detection"]
    assert (det["hits"], det["n"]) == (116, 120)
    assert round(det["rate"] * 100, 1) == 96.7
    assert round(det["ci_low"] * 100, 1) == 91.7
    assert round(det["ci_high"] * 100, 1) == 98.7


def test_every_miss_is_address_free(artifact):
    """
    The 4 misses are the `-nd` (no-destination) cases, which is the mechanism
    claim of the whole paper: detection rides on a liftable target. A miss on an
    address-carrying case would falsify that and must not pass silently.
    """
    assert artifact["summary"]["misses"]
    for case_id in artifact["summary"]["misses"]:
        assert "-nd" in case_id, f"{case_id} carries an address and was missed"


# ── the never-pool guard ──────────────────────────────────────────────
def test_pooled_cohorts_are_refused():
    with pytest.raises(AssertionError, match="pooled denominator|overlap"):
        cr._assert_unpooled({"n_benign": 68, "benign": {
            "fpr_ours":     {"n": 68, "hits": 6},
            "fpr_external": {"n": 68, "hits": 6},
        }})


def test_overlapping_cohorts_are_refused():
    """The parts must partition the whole — a case counted twice is caught."""
    with pytest.raises(AssertionError, match="overlap or a case was lost"):
        cr._assert_unpooled({"n_benign": 68, "benign": {
            "fpr_ours":     {"n": 8, "hits": 4},
            "fpr_external": {"n": 62, "hits": 2},
        }})


def test_a_dropped_cohort_is_refused():
    with pytest.raises(AssertionError, match="dropped, renamed or merged"):
        cr._assert_unpooled({"n_benign": 68,
                             "benign": {"fpr_external": {"n": 60, "hits": 2}}})


def test_the_two_cohorts_stay_separate_in_the_artifact(artifact):
    benign = artifact["summary"]["benign"]
    assert benign["fpr_ours"]["n"] == 8
    assert benign["fpr_external"]["n"] == 60
    assert "fpr_pooled" not in benign
    assert artifact["summary"]["n_benign"] == 68


# ── the replay claim ──────────────────────────────────────────────────
def test_manifest_admits_the_replay():
    """
    Rules §7: a replayed run must say so, or its artifact is a provenance lie —
    current commit, older outcomes, no way for a reader to tell.
    """
    with open(os.path.join(cr.OUT_DIR, "manifest.json")) as f:
        manifest = json.load(f)
    assert manifest["replay"]["fully_replayed"] is True
    assert manifest["replay"]["original_manifest"] is None
    assert manifest["replay"]["inputs_gitignored"] is True
    assert manifest["ollama"]["sampled"] is False


def test_run_config_is_not_backfilled_from_todays_values():
    """
    `models_at_run` may only hold what the recorded verdicts evidence. Filling
    it from `CausalAnalyzer()` would assert a July configuration nobody checked.
    """
    with open(os.path.join(cr.OUT_DIR, "manifest.json")) as f:
        manifest = json.load(f)
    at_run = manifest["models_at_run"]
    assert at_run["ie_threshold"] == 0.5
    assert at_run["ie_threshold_evidence"]
    for unrecorded in ("model_tags", "temperature", "k_samples"):
        assert at_run[unrecorded] is None, \
            f"{unrecorded} was not recorded by that run and must stay null"


# ── a partial campaign is fatal, not quietly smaller ──────────────────
def test_a_missing_pass_is_refused(tmp_path):
    (tmp_path / "gen1.jsonl").write_text("")
    with pytest.raises(SystemExit, match="missing checkpoint"):
        cr.load_cases(str(tmp_path))
