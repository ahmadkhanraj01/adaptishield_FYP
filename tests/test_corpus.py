"""
Structural tests for the evaluation corpus (red_team/attack_library.py).

These pin the two properties README §6m added the new cases to obtain. Both are
structural — they hold without running the pipeline — and both are easy to
destroy accidentally by editing a directive or a benign scenario, at which point
the corpus silently stops measuring what it was built to measure.

  1. ADDRESSLESS attacks must contain no address or URL. That is what keeps
     `_references_mediator_target` from escalating masked severity to 2, which
     is what keeps the standalone `masked >= 2` rule out by construction, which
     is what makes the IE rule the only available detection path. Put an address
     back in and these cases silently become ordinary exfiltration cases.

  2. The recipient-naming BENIGN controls must contain an address. The original
     four do not, so they could never fire the rule that does almost all of the
     detecting, and their 0/4 false-positive rate was structural rather than
     measured.

    python3 -m pytest tests/test_corpus.py -v
"""

import re

import pytest

from layer2.security_sublayer.causal_analyzer import CausalAnalyzer
from red_team.attack_generator import AttackGenerator
from red_team.attack_library import (
    ADDRESSLESS_DIRECTIVES, ATTACK_FAMILIES, BENIGN_SCENARIOS,
    DIRECTIVES, LEGITIMATE_DESTINATION_URL,
    training_targets, holdout_targets,
)

ADDRESS_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}|https?://")


# ── address-free attacks ──────────────────────────────────────────────
def test_addressless_directives_name_no_recipient():
    for d in ADDRESSLESS_DIRECTIVES:
        assert not ADDRESS_RE.search(d), f"directive carries an address: {d!r}"
        assert "{target}" not in d, f"directive still has a target slot: {d!r}"


def test_addressless_cases_carry_no_extractable_target():
    """
    The load-bearing property: with no target in the content, the mediator-target
    escalation cannot fire, so masked severity cannot reach 2 through it and the
    standalone rule is excluded by construction.
    """
    analyzer = CausalAnalyzer()
    for case in AttackGenerator().generate_addressless_attacks():
        assert analyzer._extract_suspicious_targets(case.tool_response) == [], \
            f"{case.case_id} exposes a target to the escalation path"


def test_addressless_cases_use_the_legitimate_destination():
    """
    No exfiltration address means Layer 4's egress allowlist passes them, so it
    cannot backstop a 3A/3B miss. That is deliberate — it is the only way ASR
    can become non-zero and reveal a detection failure the allowlist was hiding.
    """
    for case in AttackGenerator().generate_addressless_attacks():
        assert case.destination_url == LEGITIMATE_DESTINATION_URL
        assert case.expected_malicious is True


def test_addressless_cases_cover_every_family():
    cases = AttackGenerator().generate_addressless_attacks()
    assert len(cases) == len(ATTACK_FAMILIES) * len(ADDRESSLESS_DIRECTIVES)
    assert {c.family for c in cases} == {f.family for f in ATTACK_FAMILIES}


def test_addressless_ids_do_not_collide_with_targeted_ids():
    gen = AttackGenerator()
    targeted = {c.case_id for c in
                gen.generate_attacks(targets=training_targets() + holdout_targets())}
    addressless = {c.case_id for c in gen.generate_addressless_attacks()}
    assert not (targeted & addressless)


# ── benign controls ───────────────────────────────────────────────────
def test_recipient_naming_benign_controls_exist():
    """At least one benign control must be able to fire the target escalation."""
    with_address = [s for s in BENIGN_SCENARIOS
                    if ADDRESS_RE.search(s["tool_response"])]
    assert len(with_address) >= 3, \
        "benign corpus cannot exercise the mediator-target rule — FPR would be structural"


def test_original_benign_controls_still_carry_no_address():
    """
    The first four are the historical controls every prior FPR number was
    measured against; keep them intact so the comparison stays meaningful.
    """
    for scenario in BENIGN_SCENARIOS[:4]:
        assert not ADDRESS_RE.search(scenario["tool_response"])


def test_a_benign_control_covers_the_hyphenated_domain_case():
    """
    The one new false-positive class the normalized target match introduced
    (§6m). If no benign control carries a hyphenated domain, that exposure goes
    unmeasured in every campaign.
    """
    assert any("-" in ADDRESS_RE.search(s["tool_response"]).group(0)
               for s in BENIGN_SCENARIOS
               if ADDRESS_RE.search(s["tool_response"]))


def test_all_benign_cases_are_labeled_benign():
    cases = AttackGenerator().generate_benign()
    assert cases and all(c.expected_malicious is False for c in cases)
    assert len({c.case_id for c in cases}) == len(cases)


# ── corpus shape ──────────────────────────────────────────────────────
def test_targeted_directives_still_all_carry_a_target_slot():
    """Guard against an address-free directive being added to the wrong list."""
    for d in DIRECTIVES:
        assert "{target}" in d


# ── AgentDojo benign cohort (§6n) ─────────────────────────────────────
def test_agentdojo_benign_cohort_is_large_enough_to_estimate_a_rate():
    """Eight hand-written controls cannot support an FPR; this cohort must."""
    cases = AttackGenerator().generate_agentdojo_benign()
    assert len(cases) >= 50, f"only {len(cases)} externally-authored benign cases"


def test_agentdojo_cases_are_labeled_benign_and_uniquely_identified():
    cases = AttackGenerator().generate_agentdojo_benign()
    assert all(c.expected_malicious is False for c in cases)
    assert len({c.case_id for c in cases}) == len(cases)
    assert all(c.case_id.startswith("agentdojo-") for c in cases)


def test_agentdojo_cases_carry_no_injection_placeholder():
    """
    AgentDojo marks injection slots as {*_injection}. Any field carrying one is
    attack scaffolding — vendoring it as benign would silently poison the FPR
    denominator with attack text. A naive '{injection' filter misses these.
    """
    placeholder = re.compile(r"\{[^}]*injection[^}]*\}")
    for case in AttackGenerator().generate_agentdojo_benign():
        assert not placeholder.search(case.tool_response), case.case_id


def test_agentdojo_cases_do_not_let_layer4_mask_a_false_positive():
    """Legitimate destination, and no address in the proposed action."""
    for case in AttackGenerator().generate_agentdojo_benign():
        assert case.destination_url == LEGITIMATE_DESTINATION_URL
        assert not ADDRESS_RE.search(case.proposed_action)


def test_wilson_interval_is_sane():
    from evaluation.fpr_report import wilson
    lo, hi = wilson(4, 8)
    assert 0.0 < lo < 0.25 and 0.75 < hi < 1.0, (lo, hi)   # 4/8 spans nearly everything
    lo0, hi0 = wilson(0, 60)
    assert lo0 == 0.0 and hi0 < 0.08                       # 0/60 is a real bound
    assert wilson(0, 0) == (0.0, 1.0)


# ── IE redundancy ablation (§6n) ──────────────────────────────────────
def _ep(case_id, action="a", status="approved_causal", ie=1, malicious=True):
    return {"case_id": case_id, "proposed_action": action, "final_status": status,
            "is_malicious": malicious, "causal_takeover": True,
            "causal": {"ie": ie, "masked_severity": 2}}


def _rec(action="a", status="approved_causal", ie=1, removed=("x",)):
    return {"boundary_index": 1, "proposed_action": action, "final_status": status,
            "causal_verdict": {"ie": ie},
            "sanitization_decision": None if removed is None
                                    else {"instructions_removed": list(removed)}}


def test_ablation_join_pairs_verified_records():
    from evaluation.ie_ablation import join
    paired = join([_ep("a1"), _ep("a2", action="b")],
                  [_rec(), _rec(action="b", removed=[])])
    assert [p[1] for p in paired] == [["x"], []]


def test_ablation_join_refuses_misaligned_records():
    """
    The two files have no shared content key, so the join is positional. A
    silent mispairing would attribute one episode's sanitizer report to another
    episode's IE — fabricating exactly the correlation the ablation measures.
    """
    from evaluation.ie_ablation import join
    with pytest.raises(SystemExit):
        join([_ep("a1"), _ep("a2", action="b")],
             [_rec(action="b"), _rec()])                   # swapped
    with pytest.raises(SystemExit):
        join([_ep("a1", ie=2)], [_rec(ie=0)])              # ie disagrees
    with pytest.raises(SystemExit):
        join([_ep("a1"), _ep("a2")], [_rec()])             # length mismatch


def test_ablation_reports_3c_absence_rather_than_an_empty_removal():
    """
    3C not running and 3C running but removing nothing are different facts. If
    the first were folded into the second, every undetected episode would enter
    the table as 'sanitizer reported nothing', inverting the finding.
    """
    from evaluation.ie_ablation import join
    paired = join([_ep("a1")], [_rec(removed=None)])
    assert paired[0][1] is None


def test_ablation_last_run_slices_the_append_only_log():
    from evaluation.ie_ablation import last_run
    rows = [{"boundary_index": i} for i in (1, 2, 3, 1, 2)]
    assert [r["boundary_index"] for r in last_run(rows)] == [1, 2]


# ── dataset freshness guard (§6o) ─────────────────────────────────────
def test_freshness_flags_a_dataset_older_than_the_record_log(tmp_path):
    """
    A campaign that dies part-way leaves the previous dataset in place, so the
    FPR report reproduces the OLD numbers with no sign anything is wrong. That
    happened after the probe-grounding fix: the campaign crashed on a transient
    CUDA fault and the report printed the pre-fix rate.
    """
    from evaluation.fpr_report import freshness
    import os, time
    ds = tmp_path / "episodes.jsonl"; ds.write_text("{}\n")
    rec = tmp_path / "records.jsonl"; rec.write_text("{}\n")
    old = time.time() - 7200
    os.utime(ds, (old, old))                      # dataset 2h older than records
    msg = freshness(str(ds), str(rec))
    assert "STALE" in msg


def test_freshness_is_quiet_when_the_dataset_is_current(tmp_path):
    from evaluation.fpr_report import freshness
    import os, time
    ds = tmp_path / "episodes.jsonl"; ds.write_text("{}\n")
    rec = tmp_path / "records.jsonl"; rec.write_text("{}\n")
    old = time.time() - 7200
    os.utime(rec, (old, old))                     # records older than dataset
    assert "STALE" not in freshness(str(ds), str(rec))


def test_freshness_reports_a_missing_dataset(tmp_path):
    from evaluation.fpr_report import freshness
    assert "does not exist" in freshness(str(tmp_path / "nope.jsonl"))
