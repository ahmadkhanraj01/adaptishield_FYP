"""
Phase 13's holdout corpus, and the ways a holdout stops being one.

WHY THIS SUITE. The capability-misuse lexicon scored 90.0% on InjecAgent's
address-free stratum, in-sample — 26 of the 27 distinct injections were in the
draw and the lexicon was written after reading all 27. This corpus exists to
answer whether that generalizes, which it can only do if three things hold:

  1. **The lexicon must not have been fitted to it.** The freeze is recorded in
     the payload as a commit hash and asserted here, so a future reader can check
     the claim rather than take it on trust.
  2. **The stratum must be the detector's own predicate**, not a regex that
     resembles it. That correction cost 135 mislabelled cases in Phase 12.
  3. **Layer 4 must not absorb the cases** before detection is consulted. Every
     tool the drawn cases touch has to be in scope, or every arm is equal by
     construction — the defect that withdrew Phase 7, laid a fourth time.

Plus the exclusion that keeps the corpus honest: AgentDojo's stronger jailbreak
wrappers are left out because an explicit hijack makes these attacks *easier*.

No network and no model: the vendored file is committed.

    python3 -m pytest tests/test_agentdojo_attacks.py -v
"""

import json
import os

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(REPO, "red_team", "data", "agentdojo_attacks.json")

pytestmark = pytest.mark.skipif(
    not os.path.exists(DATA),
    reason="run `python3 -m red_team.vendor_agentdojo_attacks --wheel-root ...` first")


@pytest.fixture(scope="module")
def payload():
    with open(DATA) as handle:
        return json.load(handle)


class TestProvenance:

    def test_source_and_citation_are_recorded(self, payload):
        assert "ethz-spylab/agentdojo" in payload["source"]
        assert "MIT" in payload["source"]
        assert "Debenedetti" in payload["citation"]

    def test_the_plain_attack_template_was_used(self, payload):
        """
        `direct`, not `important_instructions`.

        An explicit "<INFORMATION> this is an important message" hijack is what
        the masked probe is best at, so the stronger wrappers would make these
        attacks easier and flatter the detector — the same reason Phase 12
        excluded InjecAgent's `enhanced` splits.
        """
        assert payload["attack_template"] == "TODO: {goal}"
        assert "important_instructions" in payload["excluded"]

    def test_the_holdout_freeze_is_recorded(self, payload):
        """The pre-registration must be checkable, not merely claimed."""
        assert "46cfbfb" in payload["holdout_protocol"]

    def test_every_case_carries_the_attack(self, payload):
        for item in payload["items"]:
            assert item["mediator"].count("TODO:") >= 1, item["index"]

    def test_repetition_is_rare_and_is_agentdojos_own(self, payload):
        """
        A few records name the same slot twice — Slack's
        `External_{prompt_injection_channel}` appears in both `channels` and
        `user_channels`, so filling it fills both. That is what AgentDojo does,
        and it is left alone rather than deduplicated.

        It is pinned because repetition makes a case *easier*: the same
        instruction twice is a stronger signal to the probe. If this ever became
        common the corpus would be quietly drifting toward the easy end, which
        is the failure the `enhanced`-split exclusion exists to prevent.
        """
        repeated = [it for it in payload["items"]
                    if it["mediator"].count("TODO:") > 1]
        assert len(repeated) < 0.15 * len(payload["items"]), \
            f"{len(repeated)} of {len(payload['items'])} repeat the injection"

    def test_no_placeholder_survives_into_a_mediator(self, payload):
        """
        A leftover `{..._injection}` is an artifact no real tool response has,
        and a detector keying on curly braces would score well for the wrong
        reason.
        """
        import re
        placeholder = re.compile(r"\{[^}]*injection[^}]*\}")
        for item in payload["items"]:
            assert not placeholder.search(item["mediator"]), item["index"]

    def test_the_injection_sits_inside_real_content(self, payload):
        """
        The mediator must be AgentDojo's surrounding prose, not a bare attack
        string — a corpus of bare payloads measures something easier.
        """
        bare = [it for it in payload["items"]
                if len(it["mediator"]) <= len("TODO: " + it["goal"]) + 20]
        assert len(bare) < 0.2 * len(payload["items"]), \
            f"{len(bare)} of {len(payload['items'])} mediators are bare payloads"


class TestStratification:

    def test_stratum_matches_the_live_predicate(self, payload):
        """
        Phase 12's lesson: the recorded label must equal 3B's own predicate run
        now, not a regex resembling it.
        """
        from layer2.security_sublayer.causal_analyzer import CausalAnalyzer

        analyzer = CausalAnalyzer()
        for item in payload["items"]:
            assert item["target_match"] == analyzer._references_mediator_target(
                item["proposed_action"].lower(), item["mediator"]), item["index"]

    def test_both_strata_are_populated(self, payload):
        assert payload["with_target"] >= 30
        assert payload["without_target"] >= 30
        assert payload["with_target"] + payload["without_target"] == payload["count"]

    def test_the_split_is_more_even_than_injecagent(self, payload):
        """
        Not cosmetic: InjecAgent is 51/459, so its projection is dominated by one
        stratum. A near-even split here means both strata carry real weight.
        """
        share = payload["with_target"] / payload["count"]
        assert 0.3 < share < 0.7


class TestSampling:

    def test_draw_is_deterministic(self):
        from evaluation.agentdojo_attacks import sample
        assert [c["index"] for c in sample(30)] == [c["index"] for c in sample(30)]

    def test_draw_is_balanced(self):
        from evaluation.agentdojo_attacks import sample
        drawn = sample(30)
        assert sum(1 for d in drawn if d["target_match"]) == 30
        assert sum(1 for d in drawn if not d["target_match"]) == 30

    def test_draw_spreads_across_suites_and_goals(self):
        """
        Cases are generated suite by suite and goal by goal, so a head slice
        would draw one suite and confound the stratum with the attack family.
        """
        from evaluation.agentdojo_attacks import sample
        drawn = sample(30)
        assert len({d["suite"] for d in drawn}) >= 3
        assert len({d["goal"] for d in drawn}) >= 10


class TestLayer4CannotAbsorbTheCohort:
    """
    The Phase 7 defect, laid a fourth time. If the attacker's tool is absent from
    the registry the permission gate refuses every case before 3A or 3B runs, and
    every arm is equal by construction.
    """

    def test_every_tool_the_draw_touches_is_declared(self):
        from evaluation.agentdojo_attacks import required_servers, sample

        drawn = sample(30)
        _name, _url, _version, scopes = required_servers(drawn)[0]
        for item in drawn:
            assert item["user_tool"] in scopes
            for scope in item["scope"]:
                assert scope in scopes

    def test_destination_is_the_legitimate_host(self):
        """
        As with InjecAgent: the harm is a tool call, not exfiltration to a host,
        so pointing the destination at an attacker domain would hand Layer 4
        every case and measure the allowlist instead of detection.
        """
        from evaluation.agentdojo_attacks import as_cases
        from evaluation.vectors import LEGIT

        cases, _cohorts = as_cases(n_per_stratum=5)
        assert cases and all(c.destination_url == LEGIT for c in cases)

    def test_cases_are_marked_malicious_and_externally_authored(self):
        from evaluation.agentdojo_attacks import as_cases

        cases, cohorts = as_cases(n_per_stratum=5)
        assert all(c.expected_malicious for c in cases)
        assert set(cohorts.values()) == {"attack_external"}
