"""
Structural tests for Phase 16 — the probe-model transfer.

Three things need pinning, and none of them is the detection rate.

  1. THE TWO RECORDINGS MUST NOT BE THE SAME INSTRUMENT. The whole comparison is
     "same prompts, same scorer, different probe model". If the prompt
     fingerprints ever diverge, the arms differ in two ways at once and the
     result means nothing — the §6p trap, one level up.

  2. THE STRATA MUST NOT BE POOLED, and a pooled rate must not be derivable by
     accident from the artifact.

  3. A RECORDING MUST NOT BE FILED UNDER THE WRONG MODEL. `_out_path` was keyed
     by cohort and run alone; a second model would have overwritten the committed
     gemma3:4b corpus in place. These pin the model-keyed paths that fixed it.

    python3 -m pytest tests/test_model_transfer.py -v
"""

import json
import os

import pytest

from evaluation import model_transfer as mt
from evaluation import probe_corpus

ARTIFACT = os.path.join(mt.OUT_DIR, "transfer.json")

pytestmark = pytest.mark.skipif(
    not os.path.exists(ARTIFACT),
    reason="results/phase16_model_transfer/transfer.json not built yet")


@pytest.fixture(scope="module")
def artifact():
    with open(ARTIFACT) as fh:
        return json.load(fh)


# ── the model-keyed paths, which is what protects the committed corpus ──
def test_the_default_model_keeps_the_original_filenames():
    """A path change here silently orphans every committed result and test."""
    assert probe_corpus._out_path("injecagent").endswith("/injecagent.json")
    assert probe_corpus._out_path("injecagent", 1).endswith("/injecagent.run1.json")
    # Naming the default explicitly must resolve to the SAME file, not a new one.
    assert (probe_corpus._out_path("injecagent", None, probe_corpus.DEFAULT_3B_MODEL)
            == probe_corpus._out_path("injecagent"))


def test_a_second_model_gets_its_own_file_and_checkpoint():
    out = probe_corpus._out_path("injecagent", None, "llama3.2:3b")
    cp = probe_corpus._cp_path("injecagent", None, "llama3.2:3b")
    assert out != probe_corpus._out_path("injecagent")
    assert cp != probe_corpus._cp_path("injecagent")
    assert "llama3_2-3b" in out and "llama3_2-3b" in cp


def test_a_recording_tagged_with_another_model_is_refused(tmp_path, monkeypatch):
    """The filename follows the analyzer's tag; reading enforces it again."""
    path = tmp_path / "wrong.json"
    path.write_text(json.dumps({"manifest": {"model": "some-other-model"},
                                "cases": []}))
    monkeypatch.setattr(probe_corpus, "_out_path", lambda *a, **k: str(path))
    with pytest.raises(SystemExit, match="refusing to report it as that model"):
        mt._load("llama3.2:3b")


# ── same instrument apart from the model ──
def test_both_recordings_used_identical_prompts():
    with open(os.path.join(mt.OUT_DIR, "manifest.json")) as fh:
        manifest = json.load(fh)
    assert manifest["identical_prompts"] is True, (
        "the two arms differ in more than the probe model — the comparison is "
        "confounded and the result cannot be attributed to the model")
    tags = {r["model"] for r in manifest["recordings"].values()}
    assert len(tags) == 2, "both arms were recorded under the same model tag"


# ── the strata stay apart ──
def test_strata_are_reported_separately_and_never_pooled(artifact):
    for model in artifact["per_model"].values():
        assert set(model) == set(mt.STRATA)
        for stratum in mt.STRATA:
            assert model[stratum]["n"] == 30
    assert "pooled" not in json.dumps(artifact["per_model"]).lower()


def test_the_gap_survives_on_both_models(artifact):
    """
    The paper's claim is the SHAPE, not the rate: near the ceiling where the
    target-match path can fire, near the floor where it cannot. If a future
    recording collapses that gap on either model, this fails and the claim needs
    rewriting rather than restating.
    """
    for model, gap in artifact["gap"].items():
        assert gap > 0.5, f"{model}: stratum gap {gap:.1%} — the shape is gone"


def test_the_paired_test_is_the_exact_one(artifact):
    """2 discordant pairs is far below the ~25 where the asymptotic test applies."""
    t = artifact["paired_overall"]
    assert t["discordant"] < 25
    assert t["asymptotic_usable"] is False
    assert t["p_of_record"] == t["p_exact"]


def test_per_case_covers_every_pair(artifact):
    assert len(artifact["per_case"]) == sum(
        s["n"] for s in artifact["per_model"][mt.INCUMBENT].values())
