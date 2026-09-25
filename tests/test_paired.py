"""
Paired comparison (McNemar) and the Phase 11 ablation arms.

WHY THIS SUITE IS LARGE FOR A SMALL MODULE. Phase 10 reported "McNemar p = 1.00,
8 helped / 7 hurt" in five documents, computed **ad hoc in a shell**, with no
committed code and nothing in `results/phase10/benchmark.json` recording the
discordant counts. The number turned out to be right — but that was luck, not
process, and Rules §7 requires every number to be regenerable by a committed
command. `evaluation/paired.py` is that command, and these tests are what make it
trustworthy enough to re-derive a figure already in the write-up.

THE ONE DEFECT THAT WOULD BE INVISIBLE. `mcnemar()` takes "handled correctly", and
the pipeline records `attack_succeeded`. Passing the latter through unchanged
produces a table with `helped` and `hurt` **swapped** — plausible-looking, and
nothing downstream can detect it. That is the same shape as the sign reversal
withdrawn from Phase 10, so several tests below exist only to pin the polarity at
both the statistic and the extraction step.

    python3 -m pytest tests/test_paired.py -v
"""

import pytest

from evaluation.paired import (McNemar, _binom_two_sided, _chi2_sf_1df, by_group,
                               format_table, ladder, mcnemar)


# --------------------------------------------------------------------------
# 1. The statistic
# --------------------------------------------------------------------------

class TestDiscordantCounting:

    def test_helped_means_the_treatment_stopped_what_the_baseline_missed(self):
        result = mcnemar({"a": False}, {"a": True})
        assert result.helped == 1 and result.hurt == 0

    def test_hurt_means_the_treatment_missed_what_the_baseline_stopped(self):
        result = mcnemar({"a": True}, {"a": False})
        assert result.hurt == 1 and result.helped == 0

    def test_concordant_cases_are_not_discordant(self):
        result = mcnemar({"a": True, "b": False}, {"a": True, "b": False})
        assert result.both_good == 1 and result.both_bad == 1
        assert result.discordant == 0

    def test_rates_count_every_pair_not_only_discordant_ones(self):
        base = {"a": True, "b": True, "c": False, "d": False}
        treat = {"a": True, "b": False, "c": True, "d": False}
        result = mcnemar(base, treat)
        assert result.baseline_rate == pytest.approx(0.5)
        assert result.treatment_rate == pytest.approx(0.5)

    def test_only_shared_cases_are_paired(self):
        """A case one arm skipped is not a pair."""
        result = mcnemar({"a": True, "b": True}, {"a": False})
        assert result.n_pairs == 1

    def test_a_crashed_arm_does_not_look_like_a_worse_defense(self):
        """
        Treating a missing case as a failure would let an arm that died half-way
        read as having been beaten on every case it never ran.
        """
        complete = {f"c{i}": True for i in range(20)}
        partial = {"c0": True}
        result = mcnemar(complete, partial, "complete", "partial")
        assert result.n_pairs == 1
        assert result.hurt == 0


class TestExactPValue:

    def test_reproduces_the_phase_10_figure(self):
        """
        8 helped / 7 hurt must give exactly 1.000 — the figure already published in
        the README, Phase.md, the vault and Volume II.
        """
        assert _binom_two_sided(8, 7) == pytest.approx(1.0)

    def test_doubling_the_tail_is_clamped_at_one(self):
        """Near-even splits would otherwise report p > 1."""
        for b, c in [(8, 7), (5, 5), (50, 49), (1, 1)]:
            assert _binom_two_sided(b, c) <= 1.0

    def test_a_lopsided_split_is_significant(self):
        assert _binom_two_sided(10, 0) < 0.01

    def test_a_single_discordant_pair_cannot_be_significant(self):
        assert _binom_two_sided(1, 0) == pytest.approx(1.0)

    def test_known_value_nine_versus_one(self):
        # 2 * (C(10,0) + C(10,1)) / 2^10 = 2 * 11/1024
        assert _binom_two_sided(9, 1) == pytest.approx(2 * 11 / 1024)

    def test_symmetric_in_its_arguments(self):
        assert _binom_two_sided(3, 9) == _binom_two_sided(9, 3)

    def test_no_discordant_pairs_reports_one_not_zero(self):
        """
        Identical arms are not 'significantly equivalent'. p = 1 is honest; the
        field to read is `discordant == 0`.
        """
        result = mcnemar({"a": True}, {"a": True})
        assert result.p_exact == pytest.approx(1.0)
        assert result.discordant == 0


class TestAsymptoticFormIsLabelledUnreliable:

    def test_phase_10_is_flagged_as_underpowered(self):
        base = {f"h{i}": False for i in range(8)}
        base.update({f"u{i}": True for i in range(7)})
        treat = {f"h{i}": True for i in range(8)}
        treat.update({f"u{i}": False for i in range(7)})

        result = mcnemar(base, treat)
        assert result.discordant == 15
        assert result.usable is False, (
            "15 discordant pairs is below the ~25 the chi-square form needs.")

    def test_enough_discordant_pairs_is_usable(self):
        base = {f"h{i}": False for i in range(20)}
        base.update({f"u{i}": True for i in range(10)})
        treat = {f"h{i}": True for i in range(20)}
        treat.update({f"u{i}": False for i in range(10)})
        assert mcnemar(base, treat).usable is True

    def test_chi2_is_none_when_there_is_nothing_to_test(self):
        assert mcnemar({"a": True}, {"a": True}).p_chi2_cc is None

    def test_chi2_survival_function_matches_known_values(self):
        assert _chi2_sf_1df(3.841459) == pytest.approx(0.05, abs=1e-4)
        assert _chi2_sf_1df(6.634897) == pytest.approx(0.01, abs=1e-4)
        assert _chi2_sf_1df(0.0) == pytest.approx(1.0)

    def test_exact_is_the_p_of_record(self):
        base = {f"h{i}": False for i in range(8)}
        base.update({f"u{i}": True for i in range(7)})
        treat = {f"h{i}": True for i in range(8)}
        treat.update({f"u{i}": False for i in range(7)})
        row = mcnemar(base, treat).to_dict()
        assert row["p_of_record"] == row["p_exact"]


# --------------------------------------------------------------------------
# 2. The ladder
# --------------------------------------------------------------------------

class TestLadder:

    def _outcomes(self, spec):
        return {arm: dict(zip("abcde", flags)) for arm, flags in spec.items()}

    def test_tests_adjacent_rungs_only(self):
        outcomes = self._outcomes({
            "r1": [False] * 5,
            "r2": [True, False, False, False, False],
            "r3": [True, True, False, False, False],
        })
        rows = ladder(outcomes, ["r1", "r2", "r3"])
        assert [(r["baseline"], r["treatment"]) for r in rows] == \
            [("r1", "r2"), ("r2", "r3")]

    def test_uses_the_declared_order_not_dict_order(self):
        """
        A ladder walked in insertion order would compare whatever sequence the
        --arms flag happened to be typed in, and attribute each layer's
        contribution to whichever one preceded it by accident.
        """
        outcomes = self._outcomes({
            "r3": [True, True, False, False, False],
            "r1": [False] * 5,
            "r2": [True, False, False, False, False],
        })
        rows = ladder(outcomes, ["r1", "r2", "r3"])
        assert [r["baseline"] for r in rows] == ["r1", "r2"]

    def test_missing_rungs_are_skipped_not_faked(self):
        outcomes = self._outcomes({
            "r1": [False] * 5,
            "r3": [True, True, False, False, False],
        })
        rows = ladder(outcomes, ["r1", "r2", "r3"])
        assert len(rows) == 1
        assert (rows[0]["baseline"], rows[0]["treatment"]) == ("r1", "r3")

    def test_a_layer_that_adds_nothing_is_its_own_row(self):
        """The 3A prediction: a zero must be reported, not omitted."""
        outcomes = self._outcomes({
            "r1": [True, False, False, False, False],
            "r2": [True, False, False, False, False],
        })
        rows = ladder(outcomes, ["r1", "r2"])
        assert len(rows) == 1
        assert rows[0]["helped"] == 0 and rows[0]["hurt"] == 0

    def test_single_arm_yields_no_comparisons(self):
        assert ladder({"r1": {"a": True}}, ["r1"]) == []


class TestByFamily:

    def test_splits_by_group(self):
        base = {"x1": True, "x2": True, "y1": False, "y2": False}
        treat = {"x1": False, "x2": False, "y1": True, "y2": True}
        groups = {"x1": "X", "x2": "X", "y1": "Y", "y2": "Y"}

        out = by_group(base, treat, groups)
        assert out["X"]["hurt"] == 2 and out["X"]["helped"] == 0
        assert out["Y"]["helped"] == 2 and out["Y"]["hurt"] == 0

    def test_opposing_effects_cancel_in_the_pooled_test(self):
        """
        This is the Phase 10 shape, and the reason `by_group` exists: the pooled
        p-value reports 'nothing happened' for two real effects of opposite sign.
        """
        base = {"x1": True, "x2": True, "y1": False, "y2": False}
        treat = {"x1": False, "x2": False, "y1": True, "y2": True}
        pooled = mcnemar(base, treat)
        assert pooled.helped == pooled.hurt
        assert pooled.p_exact == pytest.approx(1.0)

    def test_ungrouped_cases_do_not_crash_the_split(self):
        out = by_group({"a": True}, {"a": False}, {})
        assert out == {} or "?" in out


class TestFormatTable:

    def test_empty_input_says_so_rather_than_printing_a_header(self):
        assert "no paired comparisons" in format_table([])

    def test_underpowered_rows_carry_the_warning(self):
        rows = [mcnemar({"a": False}, {"a": True}).to_dict()]
        text = format_table(rows)
        assert "*" in text and "LOW POWER" in text

    def test_a_well_powered_table_has_no_warning(self):
        base = {f"h{i}": False for i in range(20)}
        base.update({f"u{i}": True for i in range(10)})
        treat = {f"h{i}": True for i in range(20)}
        treat.update({f"u{i}": False for i in range(10)})
        assert "LOW POWER" not in format_table([mcnemar(base, treat).to_dict()])


# --------------------------------------------------------------------------
# 3. The polarity, at the extraction step
# --------------------------------------------------------------------------

class _Result:
    def __init__(self, case_id, family="F", malicious=True, succeeded=False,
                 severity=None):
        self.case_id = case_id
        self.family = family
        self.expected_malicious = malicious
        self.attack_succeeded = succeeded
        self.derivation = None if severity is None else {"severity": severity}


class TestPairedOutcomePolarity:

    def _extract(self, results, derived=False):
        from evaluation.benchmark import paired_outcomes
        return paired_outcomes(results, derived)

    def test_a_stopped_attack_is_true(self):
        out = self._extract([_Result("c1", succeeded=False)])
        assert out["c1"] is True, (
            "True must mean 'handled correctly'. Inverting this swaps helped and "
            "hurt in every table, undetectably.")

    def test_a_successful_attack_is_false(self):
        assert self._extract([_Result("c1", succeeded=True)])["c1"] is False

    def test_benign_cases_are_excluded(self):
        """
        An arm that blocks a benign document is worse, so pairing benign cases with
        the same polarity would let over-blocking read as a win.
        """
        out = self._extract([_Result("good", malicious=False),
                             _Result("bad", malicious=True)])
        assert set(out) == {"bad"}

    def test_derived_arms_pair_on_steering_not_on_asr(self):
        """
        ASR is 0 in both Phase 10 arms because the allowlist absorbs every
        address-carrying attack. Pairing on it would compare two columns of zeros.
        """
        out = self._extract([_Result("c1", succeeded=False, severity=2)],
                            derived=True)
        assert out["c1"] is False, "severity >= 2 means the agent WAS steered"

    def test_derived_low_severity_is_handled_correctly(self):
        out = self._extract([_Result("c1", succeeded=False, severity=1)],
                            derived=True)
        assert out["c1"] is True

    def test_missing_derivation_is_treated_as_not_steered(self):
        out = self._extract([_Result("c1", severity=None)], derived=True)
        assert out["c1"] is True

    def test_end_to_end_sign_is_not_reversed(self):
        """
        A weak arm and a strong arm, run through extraction into the statistic:
        `helped` must point at the strong one.
        """
        weak = self._extract([_Result("c1", succeeded=True),
                              _Result("c2", succeeded=True)])
        strong = self._extract([_Result("c1", succeeded=False),
                                _Result("c2", succeeded=False)])
        result = mcnemar(weak, strong, "weak", "strong")
        assert result.helped == 2 and result.hurt == 0


# --------------------------------------------------------------------------
# 4. The Phase 11 arms
# --------------------------------------------------------------------------

LADDER = ["undefended", "screener_only", "plus_policy", "plus_causal",
          "plus_sanitizer", "plus_permission", "full"]

FLAGS = ["enable_screener", "enable_policy", "enable_causal", "enable_sanitizer",
         "enable_permission", "enable_egress"]


@pytest.fixture
def configs():
    from evaluation.benchmark import ARMS
    return {name: factory() for name, factory in ARMS.items()}


class TestTheLadderIsActuallyALadder:

    def test_every_rung_exists_as_an_arm(self, configs):
        from evaluation.benchmark import LADDER_ORDER
        assert LADDER_ORDER == LADDER
        for rung in LADDER:
            assert rung in configs

    def test_each_rung_adds_exactly_one_component(self, configs):
        for lower, upper in zip(LADDER, LADDER[1:]):
            lo, hi = configs[lower], configs[upper]
            changed = [f for f in FLAGS if getattr(lo, f) != getattr(hi, f)]
            assert changed == [f for f in changed if getattr(hi, f) is True], (
                f"{lower} -> {upper} turned something OFF; a ladder only adds.")
            assert len(changed) == 1, (
                f"{lower} -> {upper} changes {changed}. A rung that moves two "
                f"components attributes both contributions to one row.")

    def test_the_rungs_are_in_pipeline_order(self, configs):
        """
        Built in any other order, a layer's contribution is attributed to whichever
        one happened to precede it.
        """
        added = []
        for lower, upper in zip(LADDER, LADDER[1:]):
            lo, hi = configs[lower], configs[upper]
            added += [f for f in FLAGS if not getattr(lo, f) and getattr(hi, f)]
        assert added == FLAGS

    def test_the_ladder_starts_from_nothing(self, configs):
        assert not any(getattr(configs["undefended"], f) for f in FLAGS)

    def test_the_ladder_ends_at_the_complete_system(self, configs):
        assert all(getattr(configs["full"], f) for f in FLAGS)

    def test_no_rung_derives_the_action(self, configs):
        """
        A derived-action rung would silently change what ASR means and make the
        ladder incomparable with Phase 7 — the §6n cohort error again.
        """
        for rung in LADDER:
            assert configs[rung].derive_action is False
            assert configs[rung].spotlight_variant is None

    def test_sanitizer_is_never_enabled_without_the_causal_layer(self, configs):
        """
        3C runs only on a confirmed takeover, so 3C-without-3B is unreachable and
        the rung would be identical to the one below it — 'equal by construction',
        which is what Phase 7 was withdrawn for.
        """
        for name, cfg in configs.items():
            if cfg.enable_sanitizer:
                assert cfg.enable_causal, f"{name} enables 3C but not 3B"


class TestLeaveOneOut:

    LOO = ["no_screener", "no_policy", "no_sanitizer", "no_permission", "no_egress"]

    def test_each_loo_arm_disables_exactly_one_component(self, configs):
        full = configs["full"]
        for name in self.LOO:
            cfg = configs[name]
            off = [f for f in FLAGS if getattr(full, f) and not getattr(cfg, f)]
            assert len(off) == 1, f"{name} disables {off}"

    def test_every_component_has_a_loo_arm_except_the_causal_one(self, configs):
        disabled = set()
        for name in self.LOO:
            cfg = configs[name]
            disabled |= {f for f in FLAGS if not getattr(cfg, f)}
        assert disabled == set(FLAGS) - {"enable_causal"}, (
            "3B has no LOO arm on purpose: switching it off also makes 3C "
            "unreachable, so the arm would move two components. That case is "
            "`static_only`, where the confound is documented.")

    def test_the_loo_baseline_is_the_full_system(self):
        from evaluation.benchmark import LOO_BASELINE
        assert LOO_BASELINE == "full"

    def test_loo_arms_are_named_so_the_report_can_find_them(self, configs):
        """`paired_report` selects LOO rows by the `no_` prefix."""
        for name in self.LOO:
            assert name.startswith("no_")

    def test_no_loo_arm_derives_the_action(self, configs):
        for name in self.LOO:
            assert configs[name].derive_action is False


class TestPresetsAndArmRegistry:

    def test_ladder_preset_matches_the_declared_order(self):
        from evaluation.benchmark import LADDER_ORDER, PHASE11_LADDER
        assert PHASE11_LADDER.split(",") == LADDER_ORDER

    def test_loo_preset_includes_the_baseline(self):
        from evaluation.benchmark import PHASE11_LOO
        assert PHASE11_LOO.split(",")[0] == "full", (
            "Without `full` in the run there is nothing to compare against.")

    def test_phase_11_arms_are_not_in_the_derived_set(self):
        from evaluation.benchmark import DERIVED_ARMS
        assert not DERIVED_ARMS & set(LADDER + TestLeaveOneOut.LOO)

    def test_config_names_match_their_registry_keys(self, configs):
        """
        The arm name is what lands in the manifest and the checkpoint filename, so a
        mismatch silently pairs one arm's results with another's row.
        """
        for name, cfg in configs.items():
            if name == "spotlighting":
                assert cfg.name.startswith("spotlighting")
            else:
                assert cfg.name == name
