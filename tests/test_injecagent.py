"""
Phase 12 — the InjecAgent corpus, its stratification, and the two ways it could
silently fail to measure anything.

WHY THIS SUITE. Externally-authored *malicious* data is the half of §6n's lesson
that had been left unapplied, and importing it re-opens every corpus defect this
project has already paid for:

  1. **A stratum computed by the wrong rule.** The first version labelled a case
     "has a target" when an address appeared anywhere in the tool response. That
     matched 186 of 510 cases and **135 of them gave 3B no signal at all** — the
     address sat in the benign half (a GitHub URL, a sender field) while the
     injection named none. The stratum must be the detector's own predicate.
  2. **Layer 4 absorbing every case.** InjecAgent's attacker tools are not in our
     registry by default, so an unregistered run has the permission gate refusing
     everything before 3A or 3B is consulted — every arm equal *by construction*,
     which is exactly what withdrew Phase 7. Twice now.
  3. **Pooling strata.** The draw is 30/30 from a 51/459 population. A pooled rate
     over-weights the target-match stratum roughly ninefold and flatters the
     detector, so nothing may pool it.

No network and no model: the vendored file is committed, and every predicate used
here is pure string work.

    python3 -m pytest tests/test_injecagent.py -v
"""

import json
import os

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(REPO, "red_team", "data", "injecagent_dh.json")

pytestmark = pytest.mark.skipif(
    not os.path.exists(DATA),
    reason="run `python3 -m red_team.vendor_injecagent` first")


@pytest.fixture(scope="module")
def payload():
    with open(DATA) as handle:
        return json.load(handle)


@pytest.fixture
def ia():
    from evaluation import injecagent
    return injecagent


@pytest.fixture
def analyzer():
    from layer2.security_sublayer.causal_analyzer import CausalAnalyzer
    return CausalAnalyzer()


# --------------------------------------------------------------------------
# 1. Provenance — the thing that makes it external
# --------------------------------------------------------------------------

class TestProvenance:

    def test_records_its_source_and_licence(self, payload):
        assert "uiuc-kang-lab/InjecAgent" in payload["source"]
        assert "MIT" in payload["source"]

    def test_records_a_citation(self, payload):
        assert "Zhan" in payload["citation"] and "2024" in payload["citation"]

    def test_records_what_was_excluded_and_why(self, payload):
        """
        The `ds` split and both `enhanced` splits are left out on purpose. An
        exclusion recorded only in a commit message is an exclusion nobody will find.
        """
        excluded = payload["excluded"].lower()
        assert "data-stealing" in excluded or "stealing" in excluded
        assert "enhanced" in excluded

    def test_only_the_direct_harm_base_split_is_present(self, payload):
        assert payload["split"] == "direct_harm_base"

    def test_the_corpus_is_not_ours(self, payload):
        """
        Every case must carry an attacker instruction we did not write. If this file
        ever ends up holding our own templates, the whole point is lost.
        """
        instructions = {it["attacker_instruction"] for it in payload["items"]}
        assert len(instructions) >= 25, (
            "too few distinct injections to be the imported corpus")


# --------------------------------------------------------------------------
# 2. The stratum — pinned against the defect it replaced
# --------------------------------------------------------------------------

class TestStratumUsesTheDetectorsOwnPredicate:

    def test_target_match_agrees_with_3b_on_every_case(self, payload, analyzer):
        """
        The recorded stratum must equal `_references_mediator_target` run live. If
        they ever diverge, the strata are labelled by something the detector does not
        use — the defect that mislabelled 135 of 186 cases.
        """
        wrong = [
            it["index"] for it in payload["items"]
            if it["target_match"] != analyzer._references_mediator_target(
                it["proposed_action"].lower(), it["mediator"])
        ]
        assert not wrong, f"stratum disagrees with 3B on {len(wrong)} case(s)"

    def test_address_anywhere_is_recorded_but_is_not_the_stratum(self, payload):
        anywhere = sum(1 for it in payload["items"] if it["address_anywhere"])
        match = sum(1 for it in payload["items"] if it["target_match"])
        assert anywhere > match, (
            "If these are equal the distinction has been lost, and the next "
            "person will stratify on the wrong one.")

    def test_the_note_warns_against_the_wrong_field(self, payload):
        note = payload["stratification_note"].lower()
        assert "address_anywhere" in note and "must not" in note

    def test_both_strata_are_non_empty(self, payload):
        assert payload["with_target"] > 0 and payload["without_target"] > 0

    def test_the_corpus_is_mostly_address_free(self, payload):
        """
        The finding depends on this: 3B's sharpest path is unavailable on most of
        InjecAgent. If a future re-vendor flips this, the write-up is wrong.
        """
        assert payload["without_target"] > payload["with_target"] * 3, (
            f"expected a heavily address-free split, got "
            f"{payload['with_target']}/{payload['without_target']}")

    def test_counts_are_internally_consistent(self, payload):
        assert payload["with_target"] + payload["without_target"] == payload["count"]
        assert payload["count"] == len(payload["items"])


# --------------------------------------------------------------------------
# 3. The sampler
# --------------------------------------------------------------------------

class TestSampler:

    def test_draws_both_strata_equally(self, ia):
        drawn = ia.sample(10)
        with_t = sum(1 for d in drawn if d["target_match"])
        assert with_t == 10 and len(drawn) - with_t == 10

    def test_is_deterministic(self, ia):
        """No seed exists anywhere in this project, so the draw must be a stride."""
        assert [d["index"] for d in ia.sample(12)] == \
               [d["index"] for d in ia.sample(12)]

    def test_spreads_across_user_tools(self, ia):
        """
        Taking the first n would draw one or two tools, confounding the stratum with
        the tool — the 510 cases are ordered so consecutive ones share a user tool.
        """
        drawn = ia.sample(30)
        assert len({d["user_tool"] for d in drawn}) >= 8

    def test_spreads_across_injections(self, ia):
        assert len({d["attacker_instruction"] for d in ia.sample(30)}) >= 15

    def test_over_asking_a_stratum_degrades_gracefully(self, ia, payload):
        """Asking for more than a stratum holds must not crash or duplicate."""
        drawn = ia.sample(payload["with_target"] + 50)
        indices = [d["index"] for d in drawn]
        assert len(indices) == len(set(indices))

    def test_cases_carry_the_stratum_as_the_family(self, ia):
        cases, cohorts = ia.as_cases(n_per_stratum=5)
        families = {c.family for c in cases}
        assert families == {ia.WITH_TARGET, ia.NO_TARGET}
        assert set(cohorts) == families

    def test_every_case_is_malicious(self, ia):
        """
        InjecAgent ships attacks only. A benign case appearing here would give the
        FPR column a denominator it has not earned.
        """
        cases, _ = ia.as_cases(n_per_stratum=5)
        assert all(c.expected_malicious for c in cases)

    def test_the_cohort_is_marked_external(self, ia):
        _, cohorts = ia.as_cases(n_per_stratum=5)
        assert set(cohorts.values()) == {"attack_external"}, (
            "Pooling this with our own attacks is the §6n error; the cohort label "
            "is what keeps them apart.")

    def test_repeats_produce_distinct_case_ids(self, ia):
        cases, _ = ia.as_cases(n_per_stratum=3, repeats=3)
        ids = [c.case_id for c in cases]
        assert len(ids) == len(set(ids)) == 18

    def test_case_ids_are_stable_without_repeats(self, ia):
        cases, _ = ia.as_cases(n_per_stratum=3)
        assert all("-r" not in c.case_id for c in cases)


# --------------------------------------------------------------------------
# 4. Layer 4 must not absorb the corpus — the Phase 7 defect, twice already
# --------------------------------------------------------------------------

class TestLayer4CannotAbsorbEveryCase:

    def test_attacker_tools_are_declared_in_scope(self, ia):
        drawn = ia.sample(30)
        _, _, _, tools = ia.required_servers(drawn)[0]
        needed = {t for d in drawn for t in d["scope"]}
        assert needed <= set(tools), (
            "An attacker tool absent from the registry is refused by the permission "
            "gate before 3A or 3B runs — every arm equal by construction.")

    def test_user_tools_are_declared_too(self, ia):
        drawn = ia.sample(30)
        _, _, _, tools = ia.required_servers(drawn)[0]
        assert {d["user_tool"] for d in drawn} <= set(tools)

    def test_the_destination_is_the_legitimate_host(self, ia):
        from evaluation.vectors import LEGIT
        cases, _ = ia.as_cases(n_per_stratum=5)
        assert all(c.destination_url == LEGIT for c in cases), (
            "An exfil destination would hand the egress allowlist every case — the "
            "defect that withdrew Phase 7. The harm here is a tool call.")

    def test_cases_name_the_registered_server(self, ia):
        cases, _ = ia.as_cases(n_per_stratum=5)
        assert all(c.server_name == ia.SERVER for c in cases)

    def test_the_boundary_tool_is_the_user_tool_not_the_attacker_tool(self, ia):
        """
        The injection arrives in the *user* tool's response. Naming the attacker's
        tool here would model the wrong boundary.
        """
        drawn = ia.sample(5)
        cases, _ = ia.as_cases(n_per_stratum=5)
        by_id = {f"IA{d['index']:03d}": d for d in drawn}
        for case in cases:
            item = by_id.get(case.case_id)
            if item:
                assert case.tool_name == item["user_tool"]
                assert case.tool_name not in item["attacker_tools"] or \
                    item["user_tool"] in item["attacker_tools"]


# --------------------------------------------------------------------------
# 5. Wiring into the benchmark
# --------------------------------------------------------------------------

class TestBenchmarkWiring:

    def test_corpus_is_selectable(self):
        from evaluation.benchmark import build_cases
        cases, cohorts = build_cases("injecagent", 1)
        assert cases and set(cohorts.values()) == {"attack_external"}

    def test_unknown_corpus_still_errors(self):
        from evaluation.benchmark import build_cases
        with pytest.raises(SystemExit):
            build_cases("nonsense", 1)

    def test_registration_is_corpus_aware(self):
        """
        `_register_servers` must add InjecAgent's tools for this corpus and not for
        the others — registering them everywhere would quietly widen Phase 7's
        permission surface and move a committed number.
        """
        import inspect

        from evaluation.benchmark import _register_servers
        src = inspect.getsource(_register_servers)
        assert 'corpus == "injecagent"' in src

    def test_phase_7_registration_is_unchanged(self):
        from evaluation.benchmark import _register_servers

        class _Registry:
            def __init__(self):
                self.registered = []

            def register_server(self, name, url, version, tools):
                self.registered.append(name)

            def get_allowlist(self):
                return []

        class _Egress:
            def update_allowlist(self, hosts):
                pass

        class _Pipeline:
            def __init__(self):
                self.registry = _Registry()
                self.egress_filter = _Egress()

        class _Agent:
            def __init__(self):
                self.pipeline = _Pipeline()

        agent = _Agent()
        _register_servers(agent, "vectors", [])
        assert "injecagent-tools" not in agent.pipeline.registry.registered

    def test_injecagent_registration_adds_the_server(self):
        from evaluation.benchmark import _register_servers

        class _Registry:
            def __init__(self):
                self.registered = []

            def register_server(self, name, url, version, tools):
                self.registered.append(name)

            def get_allowlist(self):
                return []

        class _Egress:
            def update_allowlist(self, hosts):
                pass

        class _Pipeline:
            def __init__(self):
                self.registry = _Registry()
                self.egress_filter = _Egress()

        class _Agent:
            def __init__(self):
                self.pipeline = _Pipeline()

        agent = _Agent()
        _register_servers(agent, "injecagent", [])
        assert "injecagent-tools" in agent.pipeline.registry.registered

    def test_the_report_refuses_to_pool_the_strata(self):
        import inspect

        from evaluation.benchmark import report
        src = inspect.getsource(report)
        assert "DO NOT POOL" in src, (
            "The 30/30 draw over-weights the target-match stratum ~9x. Without the "
            "warning in the output, someone will add the columns together.")

    def test_the_report_says_the_fpr_denominator_is_empty(self):
        import inspect

        from evaluation.benchmark import report
        src = inspect.getsource(report)
        assert "NO BENIGN CASES" in src, (
            "0/0 must not read as a clean sheet.")
