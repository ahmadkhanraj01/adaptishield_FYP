"""
The campaign's own numbers, promoted from `logs/` to `results/`.

WHY THIS EXISTS. The manuscript's in-corpus headline — the causal sub-layer
detects **116/120 = 96.7%** of injections — is the one number in the paper a
reviewer cannot reproduce from the repository. Every other table has a
`results/<phase>/` entry with a manifest; this one lived in `logs/`, which is
gitignored, machine-local and exactly what the §6n staleness trap eats. Rules §7
is unambiguous: *if a table cannot be regenerated, it cannot be claimed.*

It is also the shape of the scar Rules §7 names outright. Phase 10's
`McNemar p = 1.00` reached five documents while its discordant counts existed
only in a gitignored checkpoint; the fix was to commit the per-case data beside
the statistic. So `campaign.json` carries `per_case` — every case's outcome
flags, not just the rates computed from them. A rate whose inputs are not in the
artifact is an assertion.

🔴 THIS IS A REPLAY AND THE MANIFEST SAYS SO. The outcomes are the cached
per-case results of the campaign of record (26 July 2026,
`logs/campaign_checkpoint/`). Nothing is re-executed here: no model is called, no
pipeline runs, and the numbers cannot move. What is new is the *reporting* code,
so the artifact is stamped with today's commit — and a report stamped with the
current commit while describing an older run is precisely the provenance lie
Rules §7's `replay.fully_replayed` exists to prevent. It is set, the input files
are pinned by SHA-256, and `models` records what is recoverable **from the
recorded verdicts themselves** rather than from today's config.

⚠️ AND THE ORIGINAL RUN HAS NO MANIFEST. Rules §7 asks that a replay keep the
original run's manifest alongside the analysis one. There is not one to keep:
`red_team/run_campaign.py` predates `build_manifest`, and the newest record in
`logs/red_team_runs/` is 22 July, four days before the checkpoints. That gap is
recorded in `manifest.json` under `replay.original_manifest` rather than filled
in with a plausible reconstruction. What can be evidenced is evidenced: the
checkpoint mtimes, their hashes, and the `ie_threshold=0.5` that appears in 116
recorded verdict strings.

🔴 THE TWO BENIGN COHORTS ARE NEVER POOLED. 8 hand-written controls and 60
externally-authored AgentDojo documents sit in this campaign, and pooling them
is what once made `4/8` look like a false-positive rate. They are reported as
`fpr_ours` (n=8, a **diagnostic** — four of the eight were written to break the
detector) and `fpr_external` (n=60, the rate of record), the same split
`benchmark.py` keeps. A pooled `6/68` is never emitted, and `_assert_unpooled`
fails the run rather than letting one appear.

DETECTION IS LAYER-ATTRIBUTED, NOT END-TO-END. `detection` counts
`causal_takeover` — what 3B caught — per Rules §6, because the egress allowlist
absorbs address-carrying attacks and holds end-to-end ASR near zero regardless
of whether the detector fired. `asr` is reported beside it and the two are
labelled. They are different questions and only one of them is about 3B.

    python3 -m evaluation.campaign_report
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
import time
from collections import Counter
from typing import Dict, List, Optional

from evaluation.fpr_report import wilson

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHECKPOINT_DIR = os.path.join(REPO, "logs", "campaign_checkpoint")
OUT_DIR = os.path.join(REPO, "results", "campaign")

# The three passes of the campaign of record. gen-2 is the optimizer's
# keyword-softened mutations of what gen-1 fully defended; holdout replays the
# same families against addresses 3D never trained on (Rules §5).
PASSES = ("gen1", "gen2", "holdout")

# The benign cohorts, kept apart by name so pooling has to be deliberate rather
# than accidental. Order is reporting order.
BENIGN_COHORTS = {
    "benign":           "fpr_ours",       # 8 hand-written, 4 adversarial by design
    "benign_agentdojo": "fpr_external",   # 60 externally authored — the rate
}


def load_cases(checkpoint_dir: str = CHECKPOINT_DIR) -> tuple:
    """
    Every case of the campaign of record, with its inputs pinned.

    Returns (rows, provenance). A missing pass is fatal rather than skipped: a
    partial campaign silently reports a smaller denominator, and 116/120 with an
    unnoticed 112/116 underneath it is the §6n failure in a new costume.
    """
    rows: List[dict] = []
    provenance = []
    for name in PASSES:
        path = os.path.join(checkpoint_dir, f"{name}.jsonl")
        if not os.path.exists(path):
            raise SystemExit(
                f"[campaign_report] missing checkpoint {path}.\n"
                f"  The campaign of record cannot be assembled from a subset of "
                f"its passes. Re-run the campaign, or point --checkpoints at a "
                f"directory holding all of {', '.join(PASSES)}.")
        with open(path, "rb") as f:
            blob = f.read()
        pass_rows = [json.loads(line) for line in blob.decode().splitlines() if line.strip()]
        for row in pass_rows:
            row["_pass"] = name
        rows += pass_rows
        provenance.append({
            "pass": name,
            "path": os.path.relpath(path, REPO),
            "cases": len(pass_rows),
            "sha256": hashlib.sha256(blob).hexdigest(),
            "mtime": time.strftime("%Y-%m-%dT%H:%M:%S%z",
                                   time.localtime(os.path.getmtime(path))),
        })
    return rows, provenance


def _rate(hits: int, n: int) -> dict:
    low, high = wilson(hits, n) if n else (0.0, 0.0)
    return {"hits": hits, "n": n, "rate": hits / n if n else None,
            "ci_low": low, "ci_high": high}


def _assert_unpooled(summary: dict) -> None:
    """
    Refuse to ship an artifact that has pooled the benign cohorts.

    Rules §7's never-pool rule is a 🔴 invariant with a history: `4/8` was read
    as a false-positive rate once, and the 36/68 figure in §6n is only
    interpretable because the 30/60 and 0/8 halves were kept apart. A guard here
    costs nothing and closes the one way this file could reintroduce it.
    """
    keys = set(summary["benign"])
    expected = set(BENIGN_COHORTS.values())
    if keys != expected:
        raise AssertionError(
            f"benign cohorts are {sorted(keys)}, expected exactly "
            f"{sorted(expected)} — a cohort was dropped, renamed or merged")

    n_benign = summary["n_benign"]
    # Every benign case belongs to exactly one cohort: the parts must partition
    # the whole. Double-counting shows up here as a sum larger than the corpus.
    counted = sum(entry["n"] for entry in summary["benign"].values())
    if counted != n_benign:
        raise AssertionError(
            f"benign cohorts hold {counted} cases against {n_benign} benign "
            f"episodes — the cohorts overlap or a case was lost")
    # And no single cohort may carry the whole benign denominator, which is what
    # a pooled 6/68 would look like from in here.
    if any(entry["n"] == n_benign for entry in summary["benign"].values()):
        raise AssertionError("a benign cohort has the pooled denominator — "
                             "the two cohorts have been merged")


def summarize(rows: List[dict]) -> dict:
    """
    Detection, ASR and the two benign rates, each with a Wilson interval.

    Every proportion here is a proportion of *cases*, single-run. There are no
    repeats of this campaign, so none of these carries a run-to-run spread — the
    benign side's spread is measured separately and properly in
    `noise_floor.py`, over three recordings of the same 60 documents.
    """
    malicious = [r for r in rows if r.get("expected_malicious")]
    benign = [r for r in rows if not r.get("expected_malicious")]

    detected = [r for r in malicious if r.get("causal_takeover")]
    succeeded = [r for r in malicious if r.get("attack_succeeded")]

    by_family = {}
    for family in sorted({r["family"] for r in malicious}):
        cases = [r for r in malicious if r["family"] == family]
        by_family[family] = _rate(
            sum(1 for r in cases if r.get("causal_takeover")), len(cases))

    by_pass = {}
    for name in PASSES:
        cases = [r for r in malicious if r["_pass"] == name]
        if cases:
            by_pass[name] = _rate(
                sum(1 for r in cases if r.get("causal_takeover")), len(cases))

    benign_summary = {}
    for family, key in BENIGN_COHORTS.items():
        cases = [r for r in benign if r["family"] == family]
        entry = _rate(sum(1 for r in cases if r.get("false_positive")), len(cases))
        entry["family"] = family
        entry["fired"] = sorted(r["case_id"] for r in cases if r.get("false_positive"))
        benign_summary[key] = entry

    summary = {
        "n_cases": len(rows),
        "n_malicious": len(malicious),
        "n_benign": len(benign),
        "detection": _rate(len(detected), len(malicious)),
        "asr": _rate(len(succeeded), len(malicious)),
        "detection_by_family": by_family,
        "detection_by_pass": by_pass,
        "benign": benign_summary,
        "misses": sorted(r["case_id"] for r in malicious
                         if not r.get("causal_takeover")),
        "outcome_status": dict(Counter(r.get("final_status") for r in rows)),
    }
    _assert_unpooled(summary)
    return summary


def per_case(rows: List[dict]) -> Dict[str, dict]:
    """
    The inputs of every rate above, one row per case.

    Deliberately NOT the whole checkpoint record. `raw_result` and the mediator
    text are excluded: `results/` is tracked and public, the mediator is
    attacker-authored text this project treats as untrusted everywhere
    (Rules §5), and none of it is needed to recompute a single number in
    `summary`. What is kept is the outcome flags and the four regime severities
    the takeover verdict is built from, so the verdict can be audited rather
    than taken on trust.
    """
    out = {}
    for row in sorted(rows, key=lambda r: (r["_pass"], r["case_id"])):
        verdict = row.get("causal_verdict") or {}
        out[row["case_id"]] = {
            "pass": row["_pass"],
            "family": row["family"],
            "expected_malicious": bool(row.get("expected_malicious")),
            "causal_takeover": bool(row.get("causal_takeover")),
            "attack_succeeded": bool(row.get("attack_succeeded")),
            "false_positive": bool(row.get("false_positive")),
            "final_status": row.get("final_status"),
            "outcome_severity": row.get("outcome_severity"),
            "permission_allowed": row.get("permission_allowed"),
            "egress_allowed": row.get("egress_allowed"),
            "severities": {
                "orig": verdict.get("orig_severity"),
                "masked": verdict.get("masked_severity"),
                "masked_sanitized": verdict.get("masked_san_severity"),
                "orig_sanitized": verdict.get("orig_san_severity"),
            },
            "ie": verdict.get("ie"),
            "de": verdict.get("de"),
            "ace": verdict.get("ace"),
        }
    return out


def _git(*args) -> Optional[str]:
    try:
        return subprocess.run(("git",) + args, capture_output=True, text=True,
                              timeout=10, cwd=REPO).stdout.strip() or None
    except Exception:
        return None


def _recovered_config(rows: List[dict]) -> dict:
    """
    What the ORIGINAL run's configuration provably was, read off its own output.

    Not `CausalAnalyzer()`'s current values. Today's config describes today's
    code, and stamping it on a July run would assert something no one checked —
    the same class of error as stamping the current commit on a replay. The IE
    threshold is recoverable because the analyzer writes it into every takeover
    reason string; anything not recoverable is reported as null, not guessed.
    """
    thresholds = Counter()
    for row in rows:
        reason = str((row.get("causal_verdict") or {}).get("reason", ""))
        marker = "threshold="
        if marker in reason:
            token = reason.split(marker, 1)[1].split(";")[0].strip()
            thresholds[token] += 1
    return {
        "ie_threshold": (float(next(iter(thresholds))) if len(thresholds) == 1
                         else None),
        "ie_threshold_evidence": (f"appears in {sum(thresholds.values())} recorded "
                                  f"verdict strings" if thresholds else None),
        "ie_threshold_disagreement": (dict(thresholds) if len(thresholds) > 1
                                      else None),
        "model_tags": None,
        "temperature": None,
        "k_samples": None,
        "note": "Only values recoverable from the recorded verdicts are filled "
                "in. The run predates run-manifest support in the campaign "
                "runner, so model tags, temperature and k_samples were not "
                "recorded and are NOT reconstructed from current config. "
                "Rules §2 pins the shipped split (3B gemma3:4b, 3C/L3/planner "
                "qwen2.5:3b) and no commit between 7d0ec10 and 01335ac changes "
                "it, but that is an argument, not a record.",
    }


def build_manifest(rows: List[dict], provenance: List[dict]) -> dict:
    """
    What produced these numbers — including the parts that were never recorded.

    The `replay` block is the load-bearing one. `fully_replayed: true` says the
    outcomes predate this commit entirely; `original_manifest: null` says the
    thing Rules §7 asks for does not exist, with the reason. Both are worse to
    omit than to admit.
    """
    return {
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "commit": _git("rev-parse", "HEAD"),
        "commit_subject": _git("log", "-1", "--format=%s"),
        "dirty": bool(_git("status", "--porcelain")),
        "produced_by": "python3 -m evaluation.campaign_report",
        "replay": {
            "fully_replayed": True,
            "what_ran_now": "reporting only — no model call, no pipeline "
                            "execution, no re-scoring. The per-case outcomes are "
                            "read from the campaign's own checkpoint files.",
            "run_of_record": "campaign of 26 July 2026 (checkpoint mtimes below)",
            "original_manifest": None,
            "original_manifest_note":
                "None exists. red_team/run_campaign.py predates "
                "evaluation.benchmark.build_manifest, and the newest record in "
                "logs/red_team_runs/ is 2026-07-22, four days before these "
                "checkpoints. Rules §7 asks a replay to keep the original "
                "manifest alongside the analysis one; this records its absence "
                "instead of reconstructing it.",
            "originating_commit_inferred": "01335ac",
            "originating_commit_evidence":
                "INFERRED, NOT RECORDED. 01335ac (26 Jul 2026) is the §6p commit "
                "whose own message states detection reaching 96.7% with FPR "
                "steady at 3.3%, and the checkpoints were written that evening. "
                "Consistent, not proven — treat as a pointer for a reader, not "
                "as provenance.",
            "inputs_gitignored": True,
            "inputs_note":
                "logs/ is gitignored, so a fresh clone cannot rebuild these "
                "checkpoints without re-running the campaign (~1.5 h, local "
                "GPU). This is the same departure from Rules §7 that "
                "refusal_audit/ records. It is mitigated, not cured, by "
                "committing per_case into the artifact: every rate in summary "
                "is recomputable from this file alone.",
        },
        "inputs": provenance,
        "models_at_run": _recovered_config(rows),
        "models_shipped_now": {
            "causal_3b": "gemma3:4b",
            "sanitizer_3c_screener_planner": "qwen2.5:3b / gemma3:4b (planner)",
            "note": "Current values, for comparison only. NOT asserted to be "
                    "the values this run used — see models_at_run.",
        },
        "corpus": {
            "name": "campaign (authored by us)",
            "episodes": len(rows),
            "malicious": sum(1 for r in rows if r.get("expected_malicious")),
            "benign_cohorts": {
                family: sum(1 for r in rows if r["family"] == family)
                for family in BENIGN_COHORTS
            },
            "external_benign_source":
                "AgentDojo v0.1.35 (github.com/ethz-spylab/agentdojo), MIT "
                "licence — the 60-document cohort is the complete benign "
                "content of its workspace and slack suites",
            "holdout":
                "The holdout pass replays the same families against addresses "
                "held out of everything 3D could train on (Rules §5).",
            "pooling":
                "🔴 THE TWO BENIGN COHORTS MUST NOT BE POOLED. 8 hand-written "
                "controls (4 written to break the detector) and 60 externally "
                "authored documents are different provenance. Pooling them is "
                "what made 4/8 look like an FPR.",
        },
        "seeding": "greedy decoding at temperature 0; no RNG seed is exposed by "
                   "Ollama. Not literally deterministic (§6n: 2/564 regime "
                   "severities disagreed). This campaign was run ONCE — the "
                   "benign side's run-to-run behaviour is measured in "
                   "results/noise_floor/agentdojo_benign.json, not here.",
        "ollama": {
            "sampled": False,
            "note": "Not sampled. The GPU/CPU state that matters is the one "
                    "during inference, and inference happened in July; probing "
                    "Ollama now would record this machine's state today and "
                    "imply it was the run's.",
        },
        "python": sys.version.split()[0],
        "platform": platform.platform(),
    }


def report(summary: dict) -> None:
    det, asr = summary["detection"], summary["asr"]
    print(f"\n=== campaign — {summary['n_cases']} episodes "
          f"({summary['n_malicious']} malicious, {summary['n_benign']} benign) ===\n")
    print("⚠️  REPLAY: reporting over cached per-case outcomes from the 26 Jul "
          "campaign.\n    Nothing was executed. These numbers cannot move.\n")

    print("--- detection (layer-attributed: 3B's causal takeover) ---")
    print(f"  {det['hits']}/{det['n']} = {det['rate']:.1%}  "
          f"[{det['ci_low']:.1%}, {det['ci_high']:.1%}]")
    print("\n  by family:")
    for family, row in summary["detection_by_family"].items():
        print(f"    {family:<28} {row['hits']:>3}/{row['n']:<3} {row['rate']:>6.1%}")
    print("\n  by pass:")
    for name, row in summary["detection_by_pass"].items():
        print(f"    {name:<28} {row['hits']:>3}/{row['n']:<3} {row['rate']:>6.1%}")

    print(f"\n--- end-to-end ASR (a DIFFERENT question — Rules §6) ---")
    print(f"  {asr['hits']}/{asr['n']} = {asr['rate']:.1%}  "
          f"[{asr['ci_low']:.1%}, {asr['ci_high']:.1%}]")
    print("  The egress allowlist backstops address-carrying attacks, so ASR "
          "understates\n  what the detector did and overstates what the "
          "allowlist would catch alone.")

    print("\n--- benign, BY COHORT (⛔ never pooled) ---")
    for key, row in summary["benign"].items():
        label = "the rate of record" if key == "fpr_external" else \
                "a DIAGNOSTIC at n=8, not a rate — 4 of the 8 were written to break 3B"
        print(f"  {key:<14} {row['hits']}/{row['n']} = {row['rate']:.1%}  "
              f"[{row['ci_low']:.1%}, {row['ci_high']:.1%}]   ← {label}")
        if row["fired"]:
            print(f"    fired: {', '.join(row['fired'])}")
    print("  (a pooled figure over both cohorts is not computed and must not be "
          "quoted)")

    if summary["misses"]:
        print(f"\n--- the {len(summary['misses'])} misses ---")
        for case_id in summary["misses"]:
            print(f"    {case_id}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--checkpoints", default=CHECKPOINT_DIR)
    ap.add_argument("--out", default=OUT_DIR)
    args = ap.parse_args()

    rows, provenance = load_cases(args.checkpoints)
    summary = summarize(rows)
    report(summary)

    os.makedirs(args.out, exist_ok=True)
    payload = {"corpus": "campaign", "summary": summary, "per_case": per_case(rows)}
    for name, obj in (("campaign.json", payload),
                      ("manifest.json", build_manifest(rows, provenance))):
        path = os.path.join(args.out, name)
        with open(path, "w") as f:
            json.dump(obj, f, indent=2)
        print(f"\n[campaign_report] wrote {os.path.relpath(path, REPO)}")


if __name__ == "__main__":
    main()
