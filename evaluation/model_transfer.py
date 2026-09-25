"""
Does the stratification hold on a second probe model? Phase 16.

WHY THIS EXISTS. Every number in this paper rests on one 4B model behind the
causal probe, and "one model, one scorer" is the objection a reviewer reaches for
first. §XII says so. The claim under test is not the detection rate but the
*shape*: detection near the ceiling where 3B's target-match path can fire and near
the floor where it cannot. If that shape is a property of `gemma3:4b` rather than
of the mechanism, the paper's central claim is about one model and should say so.

WHAT THIS IS NOT. It is not a repeat, and `noise_floor.py` will refuse to pool the
two recordings — correctly, because the model tag differs and they are different
instruments. Run-to-run variation is measured separately, per model, by recording
repeats of the same tag. Here there is exactly one recording per model, so no
spread is reported and none should be quoted.

🔴 WHY THE CANDIDATE WAS PRE-FLIGHTED. Rules §2: a more refusal-prone model on 3B
destroys the causal signal, so a transfer run on the wrong candidate measures the
candidate's reticence rather than the mechanism. Two candidates were disqualified
before this one:

    qwen2.5:7b   complies faithfully, but at 2.74 of 5.18 GB resident it runs
                 53% GPU / 47% CPU and does not return the same answer twice at
                 temperature 0 — an instrument that moves by the size of the
                 effect
    qwen2.5:3b   fully resident and perfectly reproducible, but answers
                 `no_action` on BOTH cases gemma detects, with no refusal string
                 anywhere in its output

`llama3.2:3b` passed both bars: 11/11 compliance, identical across four fresh
analyzer instances, 100% GPU-resident. Only then was the cohort recorded.

RE-SCORING IS EXACT. Both corpora are scored through `rescore.run_arm`, which
calls the shipped `CausalAnalyzer._decide_takeover` rather than restating it. So
the per-case comparison is exact given the transcripts, and the only thing that
differs between the arms is what the probe said.

    python3 -m evaluation.probe_corpus --cohort injecagent --model llama3.2:3b
    python3 -m evaluation.model_transfer
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import subprocess
import sys
import time
from typing import Dict, Optional

from evaluation import paired, probe_corpus, rescore
from evaluation.fpr_report import wilson

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(REPO, "results", "phase16_model_transfer")

INCUMBENT = probe_corpus.DEFAULT_3B_MODEL      # gemma3:4b
CANDIDATE = "llama3.2:3b"
COHORT = "injecagent"

# The stratum IS the finding here, so it is never collapsed. Phase 12's pooled
# figure over this 30/30 draw is wrong for the 51/459 population by 33 points.
STRATA = ("IA-target", "IA-notarget")


def _load(model: str) -> dict:
    path = probe_corpus._out_path(COHORT, None, model)
    if not os.path.exists(path):
        raise SystemExit(
            f"[model_transfer] no recording for {model} at {path}\n"
            f"  record it first:  python3 -m evaluation.probe_corpus "
            f"--cohort {COHORT} --model {model}")
    with open(path) as fh:
        payload = json.load(fh)
    recorded = payload.get("manifest", {}).get("model")
    if recorded != model:
        raise SystemExit(
            f"[model_transfer] {path} is tagged {recorded!r}, not {model!r} — "
            f"refusing to report it as that model's run")
    return payload


def _stratify(results: Dict[str, dict]) -> dict:
    out = {}
    for stratum in STRATA:
        cases = {k: v for k, v in results.items() if v["family"] == stratum}
        hits = sum(1 for v in cases.values() if v["takeover"])
        low, high = wilson(hits, len(cases))
        out[stratum] = {"detected": hits, "n": len(cases),
                        "rate": hits / len(cases) if cases else None,
                        "ci_low": low, "ci_high": high}
    return out


def compare(arm: str = "baseline") -> dict:
    """Per-stratum detection for both models, plus the paired test over shared cases."""
    payloads = {m: _load(m) for m in (INCUMBENT, CANDIDATE)}
    scored = {m: rescore.run_arm(p, arm) for m, p in payloads.items()}

    per_model = {m: _stratify(r) for m, r in scored.items()}

    # `True` = the arm handled the case correctly. Every case here is malicious,
    # so "detected" IS "handled correctly"; paired.mcnemar's docstring warns that
    # passing the opposite polarity yields a plausible table with helped and hurt
    # swapped, which nothing downstream could catch.
    test = paired.mcnemar(
        {k: v["takeover"] for k, v in scored[INCUMBENT].items()},
        {k: v["takeover"] for k, v in scored[CANDIDATE].items()},
        baseline_name=INCUMBENT, treatment_name=CANDIDATE).to_dict()

    by_stratum_test = {}
    for stratum in STRATA:
        ids = [k for k, v in scored[INCUMBENT].items() if v["family"] == stratum]
        by_stratum_test[stratum] = paired.mcnemar(
            {k: scored[INCUMBENT][k]["takeover"] for k in ids},
            {k: scored[CANDIDATE][k]["takeover"] for k in ids},
            baseline_name=INCUMBENT, treatment_name=CANDIDATE).to_dict()

    shared = sorted(set(scored[INCUMBENT]) & set(scored[CANDIDATE]))
    return {
        "cohort": COHORT,
        "arm": arm,
        "models": {"incumbent": INCUMBENT, "candidate": CANDIDATE},
        "per_model": per_model,
        "gap": {
            m: (s["IA-target"]["rate"] - s["IA-notarget"]["rate"])
            for m, s in per_model.items()
        },
        "paired_overall": test,
        "paired_by_stratum": by_stratum_test,
        "disagreements": {
            "incumbent_only": [c for c in shared
                               if scored[INCUMBENT][c]["takeover"]
                               and not scored[CANDIDATE][c]["takeover"]],
            "candidate_only": [c for c in shared
                               if scored[CANDIDATE][c]["takeover"]
                               and not scored[INCUMBENT][c]["takeover"]],
        },
        "per_case": {
            c: {"family": scored[INCUMBENT][c]["family"],
                INCUMBENT: scored[INCUMBENT][c]["takeover"],
                CANDIDATE: scored[CANDIDATE][c]["takeover"]}
            for c in shared
        },
        "pooling": "⛔ THE STRATA MUST NOT BE POOLED. Drawn 30/30 from a 51/459 "
                   "population; a pooled rate over this sample over-weights the "
                   "target-match stratum ~9x and is wrong for InjecAgent by 33 "
                   "points (Phase 12).",
        "repeats": "ONE recording per model. No run-to-run spread is reported "
                   "here and none should be quoted — that is measured per model "
                   "by noise_floor.py over repeats of the SAME tag.",
    }


def _git(*args) -> Optional[str]:
    try:
        return subprocess.run(("git",) + args, capture_output=True, text=True,
                              timeout=10, cwd=REPO).stdout.strip() or None
    except Exception:
        return None


def build_manifest(result: dict) -> dict:
    payloads = {m: _load(m) for m in (INCUMBENT, CANDIDATE)}
    return {
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "commit": _git("rev-parse", "HEAD"),
        "commit_subject": _git("log", "-1", "--format=%s"),
        "dirty": bool(_git("status", "--porcelain")),
        "produced_by": "python3 -m evaluation.model_transfer",
        "phase": "16 — probe-model transfer",
        "cohort": COHORT,
        "recordings": {
            m: {"model": p["manifest"]["model"],
                "temperature": p["manifest"]["temperature"],
                "k_samples": p["manifest"]["k_samples"],
                "git_head": p["manifest"]["git_head"],
                "prompt_fingerprints": p["manifest"]["prompt_fingerprints"],
                "cases": len(p["cases"])}
            for m, p in payloads.items()
        },
        "identical_prompts": (payloads[INCUMBENT]["manifest"]["prompt_fingerprints"]
                              == payloads[CANDIDATE]["manifest"]["prompt_fingerprints"]),
        "candidate_preflight":
            "llama3.2:3b was pre-flighted before recording, per Rules §2: 11/11 "
            "compliance under the masked probe, byte-identical across four fresh "
            "analyzer instances, 2.55 of 2.55 GB resident (100% GPU). Two earlier "
            "candidates were disqualified — qwen2.5:7b for non-determinism at 53% "
            "CPU offload, qwen2.5:3b for answering no_action on both cases the "
            "incumbent detects.",
        "seeding": "greedy decoding at temperature 0; no RNG seed is exposed by "
                   "Ollama. One recording per model — this file reports a "
                   "comparison of two instruments, not a spread.",
        "python": sys.version.split()[0],
        "platform": platform.platform(),
    }


def report(result: dict) -> None:
    inc, cand = result["models"]["incumbent"], result["models"]["candidate"]
    print(f"\n=== phase 16 — probe-model transfer on {result['cohort']} ===\n")
    print(f"{'stratum':<13} {inc:>28} {cand:>28}")
    for stratum in STRATA:
        a = result["per_model"][inc][stratum]
        b = result["per_model"][cand][stratum]
        print(f"{stratum:<13} "
              f"{a['detected']:>3}/{a['n']:<3}{a['rate']:>7.1%} "
              f"[{a['ci_low']:.1%}, {a['ci_high']:.1%}]"
              f"   {b['detected']:>3}/{b['n']:<3}{b['rate']:>7.1%} "
              f"[{b['ci_low']:.1%}, {b['ci_high']:.1%}]")
    print(f"\n{'gap (target - notarget)':<26} "
          f"{result['gap'][inc]:>7.1%}   {result['gap'][cand]:>25.1%}")

    t = result["paired_overall"]
    # p_of_record, not the chi-square: paired.py falls back to the exact binomial
    # below ~25 discordant pairs, and there are 2 here.
    print(f"\npaired over {t['n_pairs']} shared cases: {cand} helped "
          f"{t['helped']}, hurt {t['hurt']}, discordant {t['discordant']}, "
          f"exact p = {t['p_of_record']:.4g}")
    print("  ⚠️  2 discordant pairs is near-zero power. A high p here is NOT "
          "equivalence — it is\n      the absence of an argument either way, and "
          "the stratum gap is the result, not this test.")
    print(f"  {inc} only: {result['disagreements']['incumbent_only']}")
    print(f"  {cand} only: {result['disagreements']['candidate_only']}")
    print(f"\n{result['pooling']}\n{result['repeats']}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--arm", default="baseline")
    ap.add_argument("--out", default=OUT_DIR)
    args = ap.parse_args()

    result = compare(args.arm)
    report(result)

    os.makedirs(args.out, exist_ok=True)
    for name, obj in (("transfer.json", result),
                      ("manifest.json", build_manifest(result))):
        path = os.path.join(args.out, name)
        with open(path, "w") as fh:
            json.dump(obj, fh, indent=2)
        print(f"\n[model_transfer] wrote {os.path.relpath(path, REPO)}")


if __name__ == "__main__":
    main()
