"""
Episode-dataset packager (LOCAL → Kaggle).

Phase 6 step 1 of the local↔Kaggle split (Phase.md §6): turn labeled red-team
`ExecutionResult`s into the JSONL dataset the GRPO trainer reads on the P100.
Training must live off-machine (the 4 GB card cannot host torch GRPO), but the
live pipeline cannot live on Kaggle (no Ollama/MCP there) — so the seam is the
serialized `LabeledEpisode`, enriched here with the causal diagnostics the
trainer needs to replay a verdict under a different `ie_threshold`
(see grpo_env.py for why that replay is exact on campaign episodes).

Sources of ground truth
────────────────────────
Red-team `ExecutionResult`s carry `expected_malicious`, so they are the labeled
source (raw telemetry has no label). This packager consumes them directly rather
than going through `AdaptiveThreatModel.from_execution_results()` because that
adapter keeps only the four `LabeledEpisode` core fields and drops the
`causal_verdict` — and the whole point of the dataset is to carry IE per episode
so the threshold is learnable. The core fields it emits are byte-identical to
that contract; the `causal` block is additive.

Marker enrichment (optional)
────────────────────────────
`ExecutionResult` doesn't carry the Layer-3 markers (those live in telemetry).
If a telemetry JSONL is present, we best-effort join on `proposed_action` to
recover `flagged_markers`, so the trainer can propose generalizable
blocked_patterns (never literal addresses — fix A). Absent telemetry, markers
are empty and the trainer simply proposes no patterns.

Usage
─────
  # Deterministic self-test — no Ollama, builds a synthetic labeled batch:
  python -m evaluation.kaggle.package_episodes --self-test

  # Live: run the expanded campaign and package everything it produced:
  python -m evaluation.kaggle.package_episodes --run-campaign \\
      --out evaluation/kaggle/dataset/episodes.jsonl

  # From an already-collected list (in code):
  from evaluation.kaggle.package_episodes import package
  package(results, "evaluation/kaggle/dataset/episodes.jsonl")
"""

import argparse
import json
import os
from typing import List, Optional, Dict, Any

DEFAULT_CAPTURE_THRESHOLD = 0.5   # CausalAnalyzer.ie_threshold default
MASKED_TAKEOVER_THRESHOLD = 2.0   # mirror of CausalAnalyzer.masked_takeover_threshold
DEFAULT_OUT = "evaluation/kaggle/dataset/episodes.jsonl"


# ── consistency inference ────────────────────────────────────────────
def _infer_ie_separation_consistent(cv: Dict[str, Any],
                                    capture_threshold: float) -> bool:
    """
    The IE rule needs `min(masked.samples) > max(masked_san.samples)` — a
    sample-level check the recorded verdict doesn't store. But on campaign
    episodes (unique session per case → no temporal drift) the ONLY reason the
    IE rule fires or not, given ie/masked, is this consistency flag, so it is
    exactly recoverable from the recorded outcome:

      • standalone fired (masked >= 2): consistency is irrelevant to the verdict
        (rule 2 dominates at every threshold); report the mean-separation proxy.
      • the IE rule *could* have fired at capture (ie >= capture_threshold and
        masked >= 1): it fired iff takeover was recorded → consistent == takeover.
      • the IE rule could NOT fire at capture (ie < capture_threshold): the
        outcome tells us nothing about consistency, so fall back to the
        mean-separation proxy (masked_severity > masked_san_severity), which is
        threshold-invariant and the best available estimate.
    """
    masked_sev = cv.get("masked_severity", 0.0)
    masked_san = cv.get("masked_san_severity", 0.0)
    ie         = cv.get("ie", masked_sev - masked_san)
    recorded_takeover = bool(cv.get("takeover"))
    mean_proxy = masked_sev > masked_san

    if masked_sev >= MASKED_TAKEOVER_THRESHOLD:
        return mean_proxy
    if ie >= capture_threshold and masked_sev >= 1:
        return recorded_takeover
    return mean_proxy


# ── ExecutionResult → training record ────────────────────────────────
def execution_result_to_record(r, capture_threshold: float = DEFAULT_CAPTURE_THRESHOLD,
                               markers: Optional[List[str]] = None) -> Dict[str, Any]:
    cv = r.causal_verdict
    causal = None
    if cv is not None:
        causal = {
            "ie":                      cv.get("ie"),
            "masked_severity":         cv.get("masked_severity"),
            "masked_san_severity":     cv.get("masked_san_severity"),
            "orig_severity":           cv.get("orig_severity"),
            "ie_separation_consistent": _infer_ie_separation_consistent(cv, capture_threshold),
            # Campaigns use a fresh session per case, so drift cannot fire; kept
            # explicit so telemetry-sourced records can set it True when it did.
            "drift_fired":             False,
            "capture_ie_threshold":    capture_threshold,
        }
    return {
        # --- LabeledEpisode core contract (byte-identical field set) ---
        "tool_name":       r.tool_name,
        "proposed_action": r.proposed_action,
        "final_status":    r.final_status,
        "is_malicious":    bool(r.expected_malicious),
        "causal_takeover": r.causal_takeover,
        "flagged_markers": list(markers or []),
        "mediator_snippet": None,
        # --- additive training features ---
        "causal":         causal,
        "causal_reached": cv is not None,
        # --- provenance (ignored by the trainer, handy for audits) ---
        "case_id":        getattr(r, "case_id", None),
        "family":         getattr(r, "family", None),
        "generation":     getattr(r, "generation", None),
    }


# ── telemetry marker join (best-effort) ──────────────────────────────
def _load_markers_by_action(telemetry_path: str) -> Dict[str, List[str]]:
    if not telemetry_path or not os.path.exists(telemetry_path):
        return {}
    out: Dict[str, List[str]] = {}
    with open(telemetry_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            sr = rec.get("screen_result") or {}
            markers = list(sr.get("matched_markers") or [])
            if markers:
                out[rec.get("proposed_action", "")] = markers
    return out


# ── package ──────────────────────────────────────────────────────────
def package(results, out_path: str = DEFAULT_OUT,
            capture_threshold: float = DEFAULT_CAPTURE_THRESHOLD,
            telemetry_path: Optional[str] = "logs/episode_records/episodes.jsonl",
            write_metadata: bool = True) -> List[Dict[str, Any]]:
    """Serialize labeled ExecutionResults to a Kaggle-ready JSONL dataset."""
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    markers_map = _load_markers_by_action(telemetry_path) if telemetry_path else {}

    records = [
        execution_result_to_record(
            r, capture_threshold,
            markers=markers_map.get(r.proposed_action))
        for r in results
    ]
    with open(out_path, "w") as f:
        for rec in records:
            f.write(json.dumps(rec) + "\n")

    if write_metadata:
        _write_dataset_metadata(os.path.dirname(out_path) or ".")

    n_mal = sum(1 for r in records if r["is_malicious"])
    n_causal = sum(1 for r in records if r["causal"] is not None)
    print(f"[packager] wrote {len(records)} episode(s) -> {out_path}")
    print(f"[packager]   malicious={n_mal}  benign={len(records)-n_mal}  "
          f"with_causal_diagnostics={n_causal}")
    return records


def _write_dataset_metadata(dataset_dir: str) -> None:
    """
    Kaggle Dataset metadata (Path A). Edit the `id` owner slug to your Kaggle
    username before the first `kaggle datasets create`.
    """
    meta_path = os.path.join(dataset_dir, "dataset-metadata.json")
    if os.path.exists(meta_path):
        return   # never clobber an id the user already customized
    meta = {
        "title": "AdaptiShield 3D labeled episodes",
        "id": "YOUR_KAGGLE_USERNAME/adaptishield-episodes",
        "licenses": [{"name": "CC0-1.0"}],
    }
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)
    print(f"[packager] wrote {meta_path} — set 'id' to <your-username>/adaptishield-episodes")


# ── live campaign collection (LLM-dependent) ─────────────────────────
def collect_results(max_directives=None, max_train_targets=None,
                    max_holdout_targets=None, run_gen2=True, run_holdout=True,
                    checkpoint_dir=None):
    """
    Run the expanded red-team campaign and return the LABELED ExecutionResults
    (gen-1 + gen-2 mutations + held-out pass). Mirrors run_campaign.py but
    returns raw results instead of aggregate reports, because the packager needs
    per-episode records. Requires Ollama + gemma3:4b (each high-impact case is
    several LLM calls, ~15-20s locally).
    """
    from red_team.attack_generator import AttackGenerator
    from red_team.attack_library import training_targets, holdout_targets
    from red_team.execution_agent import ExecutionAgent
    from red_team.evaluator import Evaluator
    from red_team.optimizer import MutationOptimizer

    gen, agent, evaluator = AttackGenerator(), ExecutionAgent(), Evaluator()
    train = training_targets()[:max_train_targets] if max_train_targets else training_targets()
    attacks = gen.generate_attacks(max_directives=max_directives, targets=train)
    # Address-free recon directives: the only cases where the IE rule can fire
    # without the standalone masked>=2 rule already having fired, and the only
    # ones where Layer 4's egress allowlist is not a backstop (README §6m).
    attacks += gen.generate_addressless_attacks()
    # Benign = our 8 hand-written controls (a diagnostic: half were written to
    # break the detector, so they locate a boundary rather than estimate a rate)
    # PLUS AgentDojo's externally authored benign content, which is what an FPR
    # is actually measured against (§6n).
    benign = gen.generate_benign() + gen.generate_agentdojo_benign()
    # Checkpoint each pass separately. A single file would work, but gen-2
    # mutations reuse their parent's family and the holdout pass reuses directive
    # indices, so keeping the passes in distinct files makes it obvious which
    # stage a resume is picking up from — and makes it possible to invalidate one
    # pass without discarding the other two.
    def cp(stage):
        return os.path.join(checkpoint_dir, f"{stage}.jsonl") if checkpoint_dir else None

    results = agent.run_batch(attacks + benign, checkpoint=cp("gen1"))

    if run_gen2:
        report = evaluator.evaluate(results)
        mutated = MutationOptimizer().propose_next_generation(report, attacks)
        if mutated:
            results += agent.run_batch(mutated, checkpoint=cp("gen2"))

    if run_holdout:
        hold = holdout_targets()[:max_holdout_targets] if max_holdout_targets else holdout_targets()
        results += agent.run_batch(
            gen.generate_attacks(max_directives=max_directives, targets=hold),
            checkpoint=cp("holdout"))

    return results


# ── deterministic self-test (no LLM) ─────────────────────────────────
def _synthetic_results():
    """
    Build labeled ExecutionResults by hand (no pipeline / no Ollama) so the
    serialization + grpo_env round-trip can be exercised anywhere. Models the
    Phase 5b gap: a diagnostic-style miss (IE=1.0, approved_causal at
    ie_threshold=1.5), a standalone-caught attack (masked=2), and two benigns.
    """
    from red_team.execution_agent import ExecutionResult

    def er(case_id, malicious, status, cv, family="synthetic"):
        return ExecutionResult(
            case_id=case_id, family=family, generation=1,
            expected_malicious=malicious, tool_name="send_email",
            proposed_action=f"send_email ({case_id})", final_status=status,
            outcome_severity=0, permission_allowed=True, egress_allowed=True,
            causal_takeover=(status == "safe_continuation"),
            attack_succeeded=None, false_positive=None,
            task_completed=(status == "safe_continuation"),
            raw_result={}, causal_verdict=cv)

    return [
        er("diag_miss", True, "approved_causal",
           {"ie": 1.0, "masked_severity": 1.0, "masked_san_severity": 0.0,
            "orig_severity": 1.0, "takeover": False}),
        er("standalone_catch", True, "safe_continuation",
           {"ie": 0.0, "masked_severity": 2.0, "masked_san_severity": 2.0,
            "orig_severity": 2.0, "takeover": True}),
        er("benign_pass", False, "approved_causal",
           {"ie": 0.0, "masked_severity": 0.0, "masked_san_severity": 0.0,
            "orig_severity": 0.0, "takeover": False}),
        er("benign_direct", False, "approved_direct", None),
    ]


def main():
    ap = argparse.ArgumentParser(description="Package labeled episodes → Kaggle JSONL")
    ap.add_argument("--out", default=DEFAULT_OUT)
    ap.add_argument("--capture-threshold", type=float, default=DEFAULT_CAPTURE_THRESHOLD,
                    help="ie_threshold in effect when episodes were captured (default 0.5)")
    ap.add_argument("--telemetry", default="logs/episode_records/episodes.jsonl",
                    help="telemetry JSONL to join for flagged_markers (best-effort)")
    ap.add_argument("--run-campaign", action="store_true",
                    help="run the expanded red-team campaign live (needs Ollama)")
    ap.add_argument("--self-test", action="store_true",
                    help="package a deterministic synthetic batch (no LLM)")
    ap.add_argument("--checkpoint-dir", default="logs/campaign_checkpoint",
                    help="resume a crashed campaign from per-case results here; "
                         "pass '' to disable. DELETE IT after changing the "
                         "pipeline — cached results describe the old code.")
    args = ap.parse_args()

    if args.run_campaign:
        results = collect_results(checkpoint_dir=args.checkpoint_dir or None)
        capture_threshold = args.capture_threshold
    elif args.self_test:
        results = _synthetic_results()
        # The synthetic batch models the Phase 5b gap, which only exists at a
        # RAISED threshold (IE=1.0 is missed at 1.5, catchable at <=1.0). Package
        # it as captured at 1.5 so the miss reads as a threshold gap, not an
        # inconsistent-separation suppression (see _infer_ie_separation_consistent).
        capture_threshold = 1.5
    else:
        ap.error("pass --run-campaign (live) or --self-test (deterministic)")

    records = package(results, args.out, capture_threshold, args.telemetry)

    if args.self_test:
        # Prove the round-trip: reload and score across the IE grid.
        from evaluation.kaggle.grpo_env import load_episodes, evaluate_policy, Policy, ie_grid
        eps = load_episodes(args.out)
        print("\n[self-test] reward vs ie_threshold on the packaged batch:")
        for t in ie_grid():
            s = evaluate_policy(eps, Policy(ie_threshold=t))
            print(f"  ie_threshold={t:.1f}  mean_reward={s['mean_reward']:+.2f}  "
                  f"missed={s['missed']}  false_pos={s['false_pos']}")


if __name__ == "__main__":
    main()
