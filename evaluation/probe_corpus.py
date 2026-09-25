"""
Recorded probe output, so a scorer change can be measured without a campaign.

WHY THIS EXISTS. Backlog item 1 — the severity function — has been attempted
twice and both attempts cost a full run to evaluate: §6e's semantic scorer and
§6p's three rounds of probe-prompt edits each needed a 1.5-hour campaign before
anyone could see whether they helped, and §6p's verdict (8 detections lost)
arrived only after the third round. That price is why the item stalled. It is
also unnecessary.

🔴 THE KEY PROPERTY: RE-SCORING IS EXACT, NOT SIMULATED. `_run_regime_once`
does two separable things — it asks the model for an action, then scores that
action. The probe prompts and `_sanitize_mediator` do not consult the scorer, and
every production call runs at temperature 0 with greedy decoding. So a change
confined to `_score_action` **cannot** alter which action the probe returns.
Re-scoring a recorded action is therefore the same computation the live pipeline
would perform, not an approximation of it — the recorded actions are a sufficient
statistic for any scorer candidate.

This does NOT hold for a change to a probe prompt, to `_sanitize_mediator`, to the
model tag, or to the temperature. Any of those invalidates the corpus and it must
be re-recorded; `manifest` pins all four so a stale corpus is detectable rather
than silently reused. `verify_unchanged()` is the check, and a test calls it.

⚠️ EXACT GIVEN THE TRANSCRIPT — WHICH IS NOT THE SAME AS REPRODUCIBLE. Greedy
decoding fixes the scorer's input only for a *recorded* run; it does not make two
runs byte-identical here. This hardware (4 GB card, 4.3 GB model) cannot fully
offload, so generation is split GPU/CPU and the split is not deterministic —
handover §3 already records that a CPU fallback produces different outputs.
Measured by re-recording cohorts this project has already run and comparing:

    vs Phase 12 (InjecAgent, 15 shared cases)
        masked severity            15/15 agree
        masked_sanitized severity  12/15 agree
        takeover verdict           15/15 agree

    vs the committed campaign (AgentDojo benign, 60 cases)
        masked severity            57/60 agree
        takeover verdict           58/60 agree

🔴 AND THE BENIGN DISAGREEMENTS ARE THE TWO THAT MATTER. Both runs report 2
false positives out of 60 — the committed 3.3% — but **not the same two**. The
committed pair is workspace-041 and -048; the re-recording gives -048 and -055.
041 is §6o's birthday-party document, the known false positive, and it did not
fire this time (masked 1 -> 0.5); 055 fired instead, because the probe named an
address it had not named before and hit the target-match path.

The rate reproduced through two changes that happened to cancel. So the honest
reading of any FPR comparison in this project is:

  - **Between two scorers on one recording: exact.** Both arms read identical
    transcripts, so a difference of one case is really one case, and the paired
    test is valid.
  - **Between two runs: ±2-3 cases in 60.** The probe's own variation on
    borderline benign documents is the same size as the effects being compared,
    so a single live FPR run cannot resolve a one-case difference, and neither
    can this. That is a property of the measurement, not of any scorer, and it
    applies just as much to the committed 3.3%.

Detection is on firmer ground: it rides on the standalone `masked >= 2` rule,
which does not read IE, and the masked probe is the stable regime. A candidate
whose gain arrives through the IE path instead should be trusted less.

WHAT IS RECORDED. All four regimes, both samples, the extracted action per sample,
and — the part the Phase 7 log could not supply (`refusal_audit.iter_benchmark_log`
had to fall back to unsanitised text) — the **sanitised mediator actually shown to
the masked_sanitized probe**. Without that, masked_sanitized cannot be re-scored
and IE cannot be recomputed, leaving only the standalone rule. With it, the whole
takeover verdict is reproducible offline through `evaluate_recorded()`, which
calls the analyzer's own rules rather than restating them.

WHY BOTH COHORTS, ALWAYS. The attack side alone cannot answer this question. The
address-free injections are missed because `_HIGH_KW` is a data-movement
vocabulary, and every obvious way to widen it is a way to over-block — InjecAgent
ships attacks only, so it returns 0/0 on false positives and would score an
escalate-everything rule as a triumph. The AgentDojo cohort is the counterweight
and the reason `record_all` records both.

    python3 -m evaluation.probe_corpus --cohort injecagent
    python3 -m evaluation.probe_corpus --cohort agentdojo_benign
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Optional

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(REPO, "results", "probe_corpus")
CHECKPOINT_DIR = os.path.join(REPO, "logs", "probe_corpus_cp")

# The four regimes, in the order `evaluate_boundary` runs them. masked_sanitized
# and orig_sanitized are shown the sanitised text; the other two are not.
REGIMES = ("orig", "masked", "masked_sanitized", "orig_sanitized")
SANITIZED_REGIMES = frozenset({"masked_sanitized", "orig_sanitized"})

COHORTS = ("injecagent", "agentdojo_benign", "agentdojo_attacks")


@dataclass
class RegimeRecord:
    """One regime's k samples for one case."""
    regime: str
    actions: List[str]
    recorded_severities: List[int]


@dataclass
class CaseRecord:
    case_id: str
    family: str
    expected_malicious: bool
    user_input: str
    mediator: str
    # The sanitizer's output. Recorded because the two sanitized regimes are
    # scored against THIS text, not against `mediator`, and it is an LLM call
    # that cannot be recomputed offline.
    sanitized_mediator: str
    regimes: Dict[str, RegimeRecord] = field(default_factory=dict)

    def to_json(self) -> dict:
        out = asdict(self)
        out["regimes"] = {k: asdict(v) for k, v in self.regimes.items()}
        return out


def _git_head() -> Optional[str]:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=REPO, text=True,
            stderr=subprocess.DEVNULL).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def manifest(analyzer, cohort: str) -> dict:
    """
    Everything a scorer change must NOT have moved for the corpus to stay valid.

    The probe prompts are fingerprinted by content hash rather than by version
    number, because §6p's three reverted attempts show these get edited in place;
    a hash notices, a version string relies on someone remembering to bump it.
    """
    from utils.hashing import prompt_fingerprints

    return {
        "cohort": cohort,
        "git_head": _git_head(),
        "model": analyzer.llm.model,
        "temperature": analyzer.temperature,
        "k_samples": analyzer.k_samples,
        "semantic_scoring": analyzer.semantic_scoring,
        "prompt_fingerprints": prompt_fingerprints(),
    }


def _cases(cohort: str) -> List:
    """The case list for a cohort, using each corpus's own committed loader."""
    if cohort == "injecagent":
        from evaluation.injecagent import as_cases
        cases, _ = as_cases(n_per_stratum=30)
        return cases
    if cohort == "agentdojo_benign":
        from red_team.attack_generator import AttackGenerator
        return AttackGenerator().generate_agentdojo_benign()
    if cohort == "agentdojo_attacks":
        from evaluation.agentdojo_attacks import as_cases
        cases, _ = as_cases(n_per_stratum=30)
        return cases
    raise ValueError(f"unknown cohort {cohort!r} — expected one of {COHORTS}")


def record_case(analyzer, case) -> CaseRecord:
    """
    Run all four regimes for one case and record what the probe said.

    Mirrors `evaluate_boundary`'s sequence deliberately: same sanitizer call,
    same regimes, same order. It does not call `evaluate_boundary` itself only
    because that method returns severities and discards the actions behind them,
    which are the whole point here.
    """
    sanitized = analyzer._sanitize_mediator(case.tool_response, case.user_input)

    record = CaseRecord(
        case_id=case.case_id,
        family=case.family,
        expected_malicious=case.expected_malicious,
        user_input=case.user_input,
        mediator=case.tool_response,
        sanitized_mediator=sanitized,
    )

    for regime in REGIMES:
        shown = sanitized if regime in SANITIZED_REGIMES else case.tool_response
        outcome = analyzer._run_regime(regime, case.user_input, shown)
        record.regimes[regime] = RegimeRecord(
            regime=regime,
            actions=list(outcome.raw_actions),
            recorded_severities=[int(s) for s in outcome.samples],
        )

    return record


# The model the whole project is calibrated around (Rules §2). A recording made
# with this tag keeps the original bare filenames; anything else is a DIFFERENT
# INSTRUMENT and gets its own, which is the point of `_model_suffix`.
DEFAULT_3B_MODEL = "gemma3:4b"


def _model_suffix(model: Optional[str]) -> str:
    """
    Filename fragment identifying a non-default probe model, or "" for the default.

    🔴 WHY THIS IS NOT OPTIONAL. `_out_path` was keyed by cohort and run alone, so
    recording the same cohort under a second model would have overwritten the
    committed gemma3:4b corpus in place — and `verify_unchanged` could not have
    saved it, because that check runs when a corpus is *read*, long after the
    file it was meant to protect had been replaced. A model transfer is not a
    repeat of the same measurement; it is a different instrument, and the two
    must be able to sit side by side or they cannot be compared at all.
    """
    if not model or model == DEFAULT_3B_MODEL:
        return ""
    return "." + model.replace(":", "-").replace("/", "-").replace(".", "_")


def _slug(cohort: str, run: Optional[int], model: Optional[str] = None) -> str:
    """
    Filename stem for one recording.

    Run 0 (and `None`) on the default model keeps the original bare `<cohort>`
    stem so every existing consumer — `rescore`, the tests, the committed
    results — reads exactly the file it read before. Repeats and alternative
    models are additive; nothing is renamed.
    """
    stem = cohort if not run else f"{cohort}.run{run}"
    return stem + _model_suffix(model)


def _out_path(cohort: str, run: Optional[int] = None,
              model: Optional[str] = None) -> str:
    return os.path.join(OUT_DIR, f"{_slug(cohort, run, model)}.json")


def _cp_path(cohort: str, run: Optional[int] = None,
             model: Optional[str] = None) -> str:
    return os.path.join(CHECKPOINT_DIR, f"{_slug(cohort, run, model)}.jsonl")


def available_runs(cohort: str) -> List[Optional[int]]:
    """
    The run ids recorded for a cohort, in order, starting at 0 if it exists.

    Used by `evaluation/noise_floor.py` to discover repeats rather than being
    told how many there are — an aggregator given a count would silently report
    on fewer runs than it claimed if one had failed.
    """
    runs: List[Optional[int]] = []
    if os.path.exists(_out_path(cohort, None)):
        runs.append(None)
    index = 1
    while os.path.exists(_out_path(cohort, index)):
        runs.append(index)
        index += 1
    return runs


def record(cohort: str, limit: Optional[int] = None,
           analyzer=None, resume: bool = True,
           run: Optional[int] = None, model: Optional[str] = None) -> dict:
    """
    Record a cohort, checkpointing per case.

    Checkpointed for the same reason campaigns are (handover §3): this is ~9 LLM
    calls per case and an interruption partway through should cost the case in
    flight, not the run. Re-running the same command resumes.

    🔴 `run` EXISTS BECAUSE A REPEAT IS NOT A RE-RUN OF THE SAME COMMAND. Phase
    13 found the benign cohort reproduces the committed 3.3% FPR *as a rate*
    while firing on different cases (041/048 -> 048/055), so the run-to-run
    floor is ±2-3 in 60 — the same size as the effects being compared. Measuring
    that floor needs k independent recordings kept side by side.

    Both the output path AND the checkpoint path are keyed by `run`, and the
    checkpoint is the one that matters: it is keyed by cohort alone in the
    single-run design, so a second recording would have "resumed" from the
    first, replayed its cases without making a single model call, and written a
    byte-identical file. A noise floor measured from that is exactly zero — the
    most convincing possible wrong answer.
    """
    from layer2.security_sublayer.causal_analyzer import CausalAnalyzer

    analyzer = analyzer or CausalAnalyzer(
        **({"model_name": model} if model else {}))
    # Whatever the caller passed, the FILENAME follows the analyzer's own tag, so
    # a recording can never be filed under a model it was not made with.
    model = analyzer.llm.model
    cases = _cases(cohort)
    if limit:
        cases = cases[:limit]

    os.makedirs(CHECKPOINT_DIR, exist_ok=True)
    cp_path = _cp_path(cohort, run, model)

    done: Dict[str, dict] = {}
    if resume and os.path.exists(cp_path):
        with open(cp_path) as handle:
            for line in handle:
                if line.strip():
                    row = json.loads(line)
                    done[row["case_id"]] = row
        print(f"[probe_corpus] resuming — {len(done)} case(s) already recorded")

    with open(cp_path, "a") as checkpoint:
        for index, case in enumerate(cases, 1):
            if case.case_id in done:
                continue
            print(f"[probe_corpus] {cohort} {index}/{len(cases)}: {case.case_id}")
            row = record_case(analyzer, case).to_json()
            done[case.case_id] = row
            checkpoint.write(json.dumps(row) + "\n")
            checkpoint.flush()

    payload = {
        "manifest": {**manifest(analyzer, cohort), "run": run or 0},
        "cases": [done[c.case_id] for c in cases if c.case_id in done],
    }

    os.makedirs(OUT_DIR, exist_ok=True)
    out_path = _out_path(cohort, run, model)
    with open(out_path, "w") as handle:
        json.dump(payload, handle, indent=1)
    print(f"[probe_corpus] wrote {len(payload['cases'])} case(s) -> {out_path}")
    return payload


def load(cohort: str, run: Optional[int] = None) -> Optional[dict]:
    path = _out_path(cohort, run)
    if not os.path.exists(path):
        suffix = "" if not run else f" --run {run}"
        print(f"[probe_corpus] no corpus at {path} — run "
              f"`python3 -m evaluation.probe_corpus --cohort {cohort}{suffix}` first.")
        return None
    with open(path) as handle:
        return json.load(handle)


def verify_unchanged(payload: dict, analyzer=None) -> List[str]:
    """
    Reasons this corpus no longer describes the current code, or [] if it does.

    Checked before any re-scoring result is reported. A corpus recorded under a
    different probe prompt or model tag would still re-score perfectly happily
    and give a confidently wrong answer, which is the failure mode this project
    keeps meeting under other names (handover §3, "stale checkpoint").
    """
    from layer2.security_sublayer.causal_analyzer import CausalAnalyzer

    analyzer = analyzer or CausalAnalyzer()
    was = payload.get("manifest", {})
    now = manifest(analyzer, was.get("cohort", "?"))

    reasons = []
    for key in ("model", "temperature", "k_samples", "prompt_fingerprints"):
        if was.get(key) != now.get(key):
            reasons.append(f"{key}: recorded {was.get(key)!r} -> now {now.get(key)!r}")
    return reasons


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cohort", choices=COHORTS + ("all",), required=True)
    parser.add_argument("--limit", type=int, default=None,
                        help="record only the first N cases (smoke test)")
    parser.add_argument("--no-resume", action="store_true")
    parser.add_argument("--model", default=None,
                        help="probe model tag (default: gemma3:4b, the "
                             "calibrated one). A non-default tag records to its "
                             "own file — it is a different instrument, not a "
                             "repeat, and noise_floor will refuse to pool them")
    parser.add_argument("--run", type=int, default=None,
                        help="repeat id. Omit (or 0) for the original "
                             "recording; 1, 2, ... are independent repeats kept "
                             "side by side for the noise floor (see "
                             "evaluation/noise_floor.py)")
    args = parser.parse_args()

    cohorts = COHORTS if args.cohort == "all" else (args.cohort,)
    for cohort in cohorts:
        record(cohort, limit=args.limit, resume=not args.no_resume,
               run=args.run, model=args.model)
    return 0


if __name__ == "__main__":
    sys.exit(main())
