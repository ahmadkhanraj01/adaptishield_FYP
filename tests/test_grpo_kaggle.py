"""
Regression tests for the Phase 6 Kaggle GRPO pieces (evaluation/kaggle/).

Deterministic and fast — no Ollama, no torch, no GPU. They pin:

  • grpo_env: the threshold→verdict replay is exact, the reward mirrors the
    project RewardConfig, and evaluate_policy's counts are right.
  • package_episodes: the ie_separation_consistent flag is inferred correctly
    from a recorded verdict (the three cases in _infer_ie_separation_consistent).
  • grpo_train (pure-python backend): GRPO closes a knob-matching gap (1.5→1.0,
    the Phase 5b mechanism) with the minimal move, proposes a NO-OP when there is
    no gap, and never emits a literal exfil target as a pattern (fix A).
  • per-epoch metrics: the confusion matrix agrees with the reward's own catch
    predicate, the P/R/F1/support arithmetic is right (incl. the zero-denominator
    case), the held-out address split is pinned to attack_library, the hook fires
    on schedule WITHOUT changing the chosen action, and the CSV round-trips.

    python3 -m pytest tests/test_grpo_kaggle.py -v
"""

from evaluation.kaggle.grpo_env import (
    RewardConfig, Policy, EpisodeFeatures,
    status_under_policy, reward_of, evaluate_policy, ie_grid,
    confusion_counts, classification_metrics)
from evaluation.kaggle.package_episodes import (
    _infer_ie_separation_consistent, execution_result_to_record)
from evaluation.kaggle import grpo_train


# ── fixtures ──────────────────────────────────────────────────────────
def diag_miss(capture=1.5, consistent=True):
    """A diagnostic-style miss: IE=1.0, approved_causal above threshold 1.5."""
    return EpisodeFeatures(
        tool_name="send_email", proposed_action="send_email to attacker@evil.com",
        final_status="approved_causal", is_malicious=True, causal_reached=True,
        flagged_markers=["read and list every message"],
        causal={"ie": 1.0, "masked_severity": 1.0, "masked_san_severity": 0.0,
                "orig_severity": 1.0, "ie_separation_consistent": consistent,
                "drift_fired": False, "capture_ie_threshold": capture})


def benign():
    return EpisodeFeatures(
        tool_name="send_email", proposed_action="send_email confirming meeting",
        final_status="approved_causal", is_malicious=False, causal_reached=True,
        causal={"ie": 0.0, "masked_severity": 0.0, "masked_san_severity": 0.0,
                "orig_severity": 0.0, "ie_separation_consistent": False,
                "drift_fired": False, "capture_ie_threshold": 1.5})


def standalone_catch():
    """masked=2 → caught by the standalone rule at ANY threshold."""
    return EpisodeFeatures(
        tool_name="send_email", proposed_action="send_email exfil",
        final_status="safe_continuation", is_malicious=True, causal_reached=True,
        causal={"ie": 0.0, "masked_severity": 2.0, "masked_san_severity": 2.0,
                "orig_severity": 2.0, "ie_separation_consistent": False,
                "drift_fired": False, "capture_ie_threshold": 0.5})


# ── grpo_env: threshold replay ────────────────────────────────────────
def test_threshold_gap_flips_verdict():
    ep = diag_miss()
    assert status_under_policy(ep, Policy(ie_threshold=1.5)) == "approved_causal"  # missed
    assert status_under_policy(ep, Policy(ie_threshold=1.0)) == "safe_continuation"  # caught
    assert status_under_policy(ep, Policy(ie_threshold=0.5)) == "safe_continuation"


def test_standalone_rule_is_threshold_independent():
    ep = standalone_catch()
    for t in ie_grid():
        assert status_under_policy(ep, Policy(ie_threshold=t)) == "safe_continuation"


def test_inconsistent_separation_never_catches_via_ie_rule():
    ep = diag_miss(consistent=False)
    for t in ie_grid():
        assert status_under_policy(ep, Policy(ie_threshold=t)) == "approved_causal"


def test_blocked_pattern_pre_empts_with_3a_block():
    ep = diag_miss()
    pol = Policy(ie_threshold=1.5, blocked_patterns=["read and list every message"])
    # pattern isn't in the action string, so no 3A block here:
    assert status_under_policy(ep, pol) == "approved_causal"
    pol2 = Policy(ie_threshold=1.5, blocked_patterns=["attacker@evil.com"])
    assert status_under_policy(ep, pol2) == "blocked"


def test_blocked_pattern_on_benign_is_a_false_positive():
    ep = benign()
    pol = Policy(ie_threshold=0.5, blocked_patterns=["confirming meeting"])
    status = status_under_policy(ep, pol)
    assert status == "blocked"
    assert reward_of(ep, status, RewardConfig()) == RewardConfig().false_positive


# ── grpo_env: reward mirrors the project contract ─────────────────────
def test_reward_matches_reward_config():
    rc = RewardConfig()
    mal = diag_miss()
    assert reward_of(mal, "safe_continuation", rc) == rc.correct_stop
    assert reward_of(mal, "blocked", rc) == rc.correct_block
    assert reward_of(mal, "approved_causal", rc) == rc.missed_attack
    ben = benign()
    assert reward_of(ben, "approved_causal", rc) == rc.correct_pass
    assert reward_of(ben, "blocked", rc) == rc.false_positive


def test_evaluate_policy_counts():
    batch = [diag_miss(), benign()]
    missed = evaluate_policy(batch, Policy(ie_threshold=1.5))
    assert missed["missed"] == 1 and missed["false_pos"] == 0
    caught = evaluate_policy(batch, Policy(ie_threshold=1.0))
    assert caught["missed"] == 0 and caught["false_pos"] == 0
    assert caught["mean_reward"] > missed["mean_reward"]


# ── package_episodes: consistency inference ───────────────────────────
def test_infer_consistency_below_capture_uses_mean_proxy():
    # IE (1.0) < capture (1.5): outcome says nothing → mean-separation proxy True.
    cv = {"ie": 1.0, "masked_severity": 1.0, "masked_san_severity": 0.0, "takeover": False}
    assert _infer_ie_separation_consistent(cv, capture_threshold=1.5) is True


def test_infer_consistency_at_capture_reads_takeover():
    # IE (1.0) >= capture (0.5) and masked>=1: fired iff takeover was recorded.
    fired = {"ie": 1.0, "masked_severity": 1.0, "masked_san_severity": 0.0, "takeover": True}
    suppressed = {"ie": 1.0, "masked_severity": 1.0, "masked_san_severity": 0.0, "takeover": False}
    assert _infer_ie_separation_consistent(fired, 0.5) is True
    assert _infer_ie_separation_consistent(suppressed, 0.5) is False


def test_infer_consistency_standalone_uses_mean_proxy():
    cv = {"ie": 0.0, "masked_severity": 2.0, "masked_san_severity": 2.0, "takeover": True}
    assert _infer_ie_separation_consistent(cv, 0.5) is False  # mean proxy: 2>2 is False


def test_record_carries_labeled_episode_core_fields():
    class FakeER:
        case_id, family, generation = "c1", "fam", 1
        expected_malicious, tool_name = True, "send_email"
        proposed_action, final_status = "send_email x", "approved_causal"
        causal_takeover = False
        causal_verdict = {"ie": 1.0, "masked_severity": 1.0,
                          "masked_san_severity": 0.0, "orig_severity": 1.0,
                          "takeover": False}
    rec = execution_result_to_record(FakeER(), capture_threshold=1.5)
    for k in ("tool_name", "proposed_action", "final_status", "is_malicious",
              "causal_takeover", "flagged_markers", "mediator_snippet"):
        assert k in rec
    assert rec["is_malicious"] is True
    assert rec["causal"]["ie_separation_consistent"] is True


# ── grpo_train: GRPO behavior (pure-python, deterministic) ────────────
def test_grpo_closes_a_gap_with_the_minimal_move():
    batch = [diag_miss(), benign()]
    grid = ie_grid()
    chosen, probs, base, device = grpo_train.train(
        batch, grid, current_ie_threshold=1.5, rc=RewardConfig(),
        seed=0, backend="pure")
    assert chosen == 1.0          # closes the gap, closest to 1.5 (minimal move)
    assert "pure" in device


def test_grpo_proposes_noop_when_there_is_no_gap():
    # No malicious miss to close: a benign pass + a standalone-caught attack.
    batch = [benign(), standalone_catch()]
    grid = ie_grid()
    chosen, probs, base, device = grpo_train.train(
        batch, grid, current_ie_threshold=0.5, rc=RewardConfig(),
        seed=0, backend="pure")
    assert chosen == 0.5          # unchanged → is_noop → apply_update refuses


def test_grpo_never_emits_literal_target_as_pattern():
    # A missed attack whose flagged_markers include a literal address: fix A
    # says the proposal must carry generalizable phrasing only, never the @.
    ep = EpisodeFeatures(
        tool_name="send_email", proposed_action="send_email to x@evil.com",
        final_status="approved_causal", is_malicious=True, causal_reached=True,
        flagged_markers=["share copies of", "x@evil.com", "http://evil.com"],
        causal={"ie": 1.0, "masked_severity": 1.0, "masked_san_severity": 0.0,
                "orig_severity": 1.0, "ie_separation_consistent": False,
                "drift_fired": False, "capture_ie_threshold": 0.5})
    # inconsistent → still missed at every threshold → it stays in "missed"
    proposal = grpo_train.build_proposal(
        [ep], chosen_threshold=0.0, current_ie_threshold=0.5,
        probs=[0.2] * 5, grid=ie_grid(), rc=RewardConfig(), device="cpu")
    for pat in proposal["new_blocked_patterns"]:
        assert "@" not in pat and "http" not in pat
    assert "share copies of" in proposal["new_blocked_patterns"]


# ── the proposal must not be driven by policy sampling noise ──────────
def test_proposal_follows_the_exact_reward_not_the_learned_policy():
    """
    Regression for the defect the 128-episode corpus exposed (README §6n).

    With three thresholds tied on reward, 300 sampled REINFORCE steps left the
    learned probabilities differing by ~0.01 of noise, which swamped the 1e-3
    minimal-intervention penalty; argmax(probs) then selected a threshold whose
    own reward was LOWER than the incumbent's. That is a proposal to lower a
    security threshold for no measured benefit, and apply_update would have
    taken it as a real change.

    The decision must come from the exact reward table, which is computable here
    because the env is deterministic in the threshold.
    """
    # Tied on catch outcome across the low thresholds; only the intervention
    # penalty separates them, so a noisy policy argmax could pick any of them.
    episodes = [standalone_catch() for _ in range(8)]
    grid = ie_grid()
    chosen, probs, base_rewards, _ = grpo_train.train(
        episodes, grid, current_ie_threshold=0.5, rc=RewardConfig(), backend="pure")

    assert chosen == grid[max(range(len(grid)), key=lambda i: base_rewards[i])]
    assert chosen == 0.5, "tied rewards must resolve to the incumbent (no-op)"


# ── joint action space (§6n) ──────────────────────────────────────────
def _marked(marker, is_malicious=True, masked=2.0, ie=2.0, status="safe_continuation"):
    return EpisodeFeatures(
        tool_name="send_email", proposed_action="send_email reply to sender",
        final_status=status, is_malicious=is_malicious, causal_reached=True,
        flagged_markers=[marker],
        causal={"ie": ie, "masked_severity": masked, "masked_san_severity": 0.0,
                "orig_severity": 0.0, "ie_separation_consistent": True,
                "drift_fired": False, "capture_ie_threshold": 0.5})


def test_marker_weight_below_threshold_changes_nothing():
    """Default weights are 0, so 3A's boolean behaviour is preserved exactly."""
    ep = _marked("ignore previous")
    assert status_under_policy(ep, Policy(ie_threshold=0.5)) == "safe_continuation"
    assert status_under_policy(
        ep, Policy(ie_threshold=0.5,
                   marker_weights={"ignore previous": 0.5})) == "safe_continuation"


def test_marker_weight_at_threshold_blocks():
    ep = _marked("ignore previous")
    assert status_under_policy(
        ep, Policy(ie_threshold=0.5,
                   marker_weights={"ignore previous": 1.0})) == "blocked"


def test_drift_knobs_cannot_move_a_campaign_verdict():
    """
    risk_threshold / window_size are modelled, but campaign episodes record
    drift_fired=False with no drift inputs (unique session per case), so no
    setting of either can change the outcome. This is the unidentifiability the
    trainer reports rather than pretending to train.
    """
    ep = _marked("forward all")
    base = status_under_policy(ep, Policy(ie_threshold=0.5))
    for risk in grpo_train.RISK_THRESHOLD_GRID:
        for window in grpo_train.WINDOW_SIZE_GRID:
            assert status_under_policy(
                ep, Policy(ie_threshold=0.5, risk_threshold=risk,
                           window_size=window)) == base


def test_joint_trainer_reports_flat_dimensions():
    episodes = [_marked("forward all") for _ in range(6)]
    space = grpo_train.ActionSpace(ie_grid(), grpo_train.discover_markers(episodes))
    _, _, _, _, _, diag = grpo_train.train_joint(
        episodes, space, Policy(ie_threshold=0.5), RewardConfig(),
        steps=40, group_size=4, backend="pure")
    assert "risk_threshold" in diag["flat_dimensions"]
    assert "window_size" in diag["flat_dimensions"]


def test_joint_proposal_is_a_noop_when_rewards_are_tied():
    """
    The requirement this task was set to guarantee: a tied-reward joint proposal
    must return the incumbent. Nothing here is improvable — every episode is
    already caught, and blocking any of them would only forfeit the workflow.
    """
    episodes = [_marked("forward all") for _ in range(10)]
    space = grpo_train.ActionSpace(ie_grid(), grpo_train.discover_markers(episodes))
    base = Policy(ie_threshold=0.5)
    chosen, _, incumbent, _, _, diag = grpo_train.train_joint(
        episodes, space, base, RewardConfig(), steps=60, group_size=4, backend="pure")
    assert chosen == incumbent, f"expected a no-op, got {space.describe(chosen)}"
    assert diag["verified_accepted"] is False


def test_joint_trainer_finds_a_gain_only_the_marker_dimension_can_express():
    """
    The corpus result (§6n): the missed attacks all carry one marker that the
    caught ones and the benign controls do not, so weighting that marker
    converts misses into blocks. No ie_threshold can express this.
    """
    missed = [_marked("ignore previous", status="approved_causal", masked=0.0, ie=0.0)
              for _ in range(5)]
    caught = [_marked("forward all") for _ in range(20)]
    space = grpo_train.ActionSpace(ie_grid(),
                                   grpo_train.discover_markers(missed + caught))
    base = Policy(ie_threshold=0.5)
    chosen, _, incumbent, _, _, diag = grpo_train.train_joint(
        missed + caught, space, base, RewardConfig(),
        steps=300, group_size=8, backend="pure")
    assert diag["verified_accepted"] is True
    picked = space.describe(chosen)
    assert picked["marker_weight:ignore previous"] == 1.0
    assert picked["marker_weight:forward all"] == 0.0, "must not over-block"


def test_minimality_pass_reverts_a_free_riding_dimension():
    """
    A dimension that moved for no reward must not ride along inside an otherwise
    justified proposal — that is the 1-D defect wearing a disguise.
    """
    missed = [_marked("ignore previous", status="approved_causal", masked=0.0, ie=0.0)
              for _ in range(5)]
    caught = [_marked("forward all") for _ in range(20)]
    space = grpo_train.ActionSpace(ie_grid(),
                                   grpo_train.discover_markers(missed + caught))
    chosen, _, incumbent, _, _, _ = grpo_train.train_joint(
        missed + caught, space, Policy(ie_threshold=0.5), RewardConfig(),
        steps=300, group_size=8, backend="pure")
    ie_dim = space.names.index("ie_threshold")
    assert chosen[ie_dim] == incumbent[ie_dim], \
        "ie_threshold is flat on this batch and must stay at the incumbent"


def test_intervention_eps_stays_below_the_smallest_real_gain():
    """
    Raising eps to 'dominate' ~1e-2 probability noise would mask every
    improvement smaller than four episodes. It must sit below the smallest gain
    a single episode can produce.
    """
    episodes = [_marked("forward all") for _ in range(128)]
    rc = RewardConfig()
    eps = grpo_train._auto_intervention_eps(episodes, rc)
    smallest_real_gain = 0.3 / 128          # correct_stop +1.0 -> correct_block +0.7
    assert 0 < eps < smallest_real_gain


# ── per-epoch metrics (precision / recall / F1 / support / accuracy) ──
def test_confusion_matrix_uses_the_reward_own_catch_predicate():
    """
    The epoch table and the reward must never disagree about which episodes
    were caught: the predicted-positive predicate here is the SAME
    `status in STOPPED_STATUSES` reward_of() scores on.
    """
    batch = [diag_miss(), benign(), standalone_catch()]
    counts = confusion_counts(batch, Policy(ie_threshold=1.0))
    # diag_miss caught at 1.0, standalone caught at ANY threshold, benign passes.
    assert (counts["tp"], counts["fn"], counts["fp"], counts["tn"]) == (2, 0, 0, 1)
    stats = evaluate_policy(batch, Policy(ie_threshold=1.0))
    assert stats["missed"] == counts["fn"] and stats["false_pos"] == counts["fp"]


def test_classification_metrics_arithmetic():
    """Hand-computed: tp=1 fp=1 fn=2 tn=0 -> P=0.5, R=1/3, F1=0.4, acc=0.25.
    support_attack = tp+fn = 3, support_benign = tn+fp = 1.
    The benign class reads precision 0/(0+2)=0, recall 0/(0+1)=0 -> F1 0,
    macro 0.2."""
    m = classification_metrics({"n": 4, "tp": 1, "fp": 1, "fn": 2, "tn": 0})
    assert round(m["precision"], 6) == 0.5
    assert round(m["recall"], 6) == round(1 / 3, 6)
    assert round(m["f1"], 6) == 0.4
    assert round(m["accuracy"], 6) == 0.25
    assert (m["support_attack"], m["support_benign"]) == (3, 1)
    assert round(m["macro_f1"], 6) == 0.2


def test_classification_metrics_on_an_empty_split_reads_zero_not_a_crash():
    """An empty holdout is a real run; a metric that raises on it would hide
    the run it was asked to describe."""
    counts = confusion_counts([], Policy(ie_threshold=0.5))
    assert counts == {"n": 0, "tp": 0, "fp": 0, "fn": 0, "tn": 0}
    m = classification_metrics(counts)
    for k in ("precision", "recall", "f1", "accuracy", "macro_f1"):
        assert m[k] == 0.0


def test_holdout_addresses_are_pinned_to_the_attack_library():
    """
    The Kaggle bundle cannot import red_team, so HOLDOUT_TARGET_ADDRESSES is
    inlined. If the split moves there and this tuple does not, held-out
    attacks silently become training data — the §6d memorisation defect with
    different clothes. This is the tripwire.
    """
    from red_team.attack_library import holdout_targets
    pinned = set(grpo_train.HOLDOUT_TARGET_ADDRESSES)
    assert pinned == {t["email"] for t in holdout_targets()}
    assert len(pinned) == 2, "the split must keep at least one target held out"


def test_episode_split_recovers_the_address_level_split():
    """from_dict drops case_id, so the split is recovered from the action
    string — the one field that must name the address for the attack to mean
    anything. Addressless attacks carry neither and are training data."""
    train_attack = EpisodeFeatures(
        tool_name="send_email", proposed_action="send_email to attacker@evil.com",
        final_status="approved_causal", is_malicious=True)
    held_attack = EpisodeFeatures(
        tool_name="send_email", proposed_action="send_email to leaker@shadow-mail.net",
        final_status="approved_causal", is_malicious=True)
    addressless = EpisodeFeatures(
        tool_name="send_email", proposed_action="send_email the summary to the team",
        final_status="approved_causal", is_malicious=True)
    assert grpo_train.episode_split(train_attack) == "train"
    assert grpo_train.episode_split(held_attack) == "holdout"
    assert grpo_train.episode_split(addressless) == "train"
    assert grpo_train.episode_split(benign()) == "benign"


def test_epoch_metrics_reports_one_row_per_split():
    # benign joins the train cohort (a false positive there is charged to the
    # cohort the policy was fitted on); the holdout row exists but is empty.
    rows = grpo_train.epoch_metrics(
        10, 1, Policy(ie_threshold=1.0), "ie_threshold=1.0",
        grpo_train._metrics_splits([diag_miss(), benign()]))
    assert [r["split"] for r in rows] == ["train", "holdout", "all"]
    train = rows[0]
    assert (train["tp"], train["fn"], train["fp"], train["tn"]) == (1, 0, 0, 1)
    assert train["precision"] == 1.0 and train["recall"] == 1.0
    assert train["f1"] == 1.0 and train["accuracy"] == 1.0
    assert (train["support_attack"], train["support_benign"]) == (1, 1)
    assert rows[1]["n"] == 0 and rows[1]["accuracy"] == 0.0


def test_epoch_recorder_checkpoints_on_schedule_and_always_at_the_last_step():
    rows, on_step = grpo_train._epoch_recorder(
        lambda probs: (Policy(ie_threshold=1.0), "ie_threshold=1.0"),
        [diag_miss(), benign()], metrics_every=2, steps=5)
    for i in range(5):
        on_step(i, [0.2] * 5)
    steps = [r["step"] for r in rows if r["split"] == "train"]
    assert steps == [2, 4, 5], "checkpoints every N steps, plus the final one"
    assert [r["epoch"] for r in rows if r["split"] == "train"] == [1, 2, 3]
    assert len(rows) == 9          # 3 checkpoints x 3 splits


def test_epoch_recorder_disabled_by_zero():
    rows, on_step = grpo_train._epoch_recorder(
        lambda probs: (Policy(ie_threshold=1.0), "x"),
        [diag_miss()], metrics_every=0, steps=5)
    on_step(0, [0.2] * 5)
    assert rows == []


def test_epoch_metrics_hook_does_not_change_the_proposal():
    """
    A metrics hook that perturbed the search would be a worse defect than no
    metrics at all. The hook reads the probabilities; it must not write to
    them — identical seed, identical chosen action, with and without it.
    """
    missed = [_marked("ignore previous", status="approved_causal", masked=0.0, ie=0.0)
              for _ in range(5)]
    caught = [_marked("forward all") for _ in range(20)]
    episodes = missed + caught

    def run(with_hook):
        space = grpo_train.ActionSpace(ie_grid(), grpo_train.discover_markers(episodes))
        base = Policy(ie_threshold=0.5)

        def resolve(probs_):
            action = [max(range(len(p)), key=lambda i: p[i]) for p in probs_]
            return space.to_policy(action, base), "argmax"

        rows, on_step = grpo_train._epoch_recorder(
            resolve, episodes, metrics_every=100, steps=300)
        chosen, _, incumbent, _, _, diag = grpo_train.train_joint(
            episodes, space, base, RewardConfig(),
            steps=300, group_size=8, backend="pure",
            on_step=on_step if with_hook else None)
        return chosen, diag, rows

    chosen_a, diag_a, _ = run(False)
    chosen_b, diag_b, rows = run(True)
    assert chosen_a == chosen_b
    assert diag_a["reward_policy_choice"] == diag_b["reward_policy_choice"]
    assert rows, "the hook must actually have recorded something"
    # And the marker-dimension gain must be visible IN the table: the train
    # split's recall rises as the policy learns to weight the miss marker.
    train_rows = [r for r in rows if r["split"] == "train"]
    assert train_rows[-1]["recall"] >= train_rows[0]["recall"]


def test_epoch_metrics_csv_round_trips(tmp_path):
    rows = grpo_train.epoch_metrics(
        10, 1, Policy(ie_threshold=1.0), "ie_threshold=1.0",
        grpo_train._metrics_splits([diag_miss(), benign()]))
    path = grpo_train.write_epoch_metrics(rows, str(tmp_path / "epoch_metrics.csv"))
    import csv as _csv
    with open(path) as f:
        got = list(_csv.DictReader(f))
    assert len(got) == len(rows)
    assert list(got[0].keys()) == grpo_train.CSV_FIELDS
    assert got[0]["split"] == "train"
    assert got[0]["recall"] == "1.0"      # written as text, read as text
