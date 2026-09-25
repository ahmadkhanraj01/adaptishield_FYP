# results — Tracked Numbers and Their Provenance

**Status:** ✅ Active — one subdirectory per phase whose numbers are quotable

> Unlike `logs/` (gitignored working output), **this tree is tracked**. Rules.md §7
> requires that *every number in the paper is regenerable by one committed command
> whose artifact is committed here with a run manifest*. A table that cannot be
> regenerated cannot be claimed.

## Purpose

`logs/` is where a run writes; `results/` is where a run's **conclusions** live
once they are worth citing. The distinction matters because `logs/` is
append-only, machine-local and easily stale — the §6n staleness trap is exactly a
crashed run leaving an old dataset that reports pre-fix numbers as current.
Copying a result here is the act of saying *this one is the number of record*.

## Contents

| Path | Produced by | Holds |
| :--- | :--- | :--- |
| `phase7/benchmark.json` | `python3 -m evaluation.benchmark --repeats 3` | Per-arm ASR / FPR / WCR with Wilson intervals, per-layer attribution counts, per-vector breakdown |
| `phase7/manifest.json` | same run | Commit SHA + dirty flag, corpus provenance and version, model tags, 3B's knobs, Ollama VRAM state, Python/platform, seeding statement |
| `phase10/benchmark.json` | `python3 -m evaluation.benchmark --corpus campaign --arms derived_control spotlighting` | Per-arm `steer_rate` with Wilson intervals and the paired McNemar table. **`steer_rate`, not ASR, is the outcome** — ASR is 0/66 in both arms because the allowlist absorbs every address-carrying attack |
| `phase10/manifest.json` | same run | As above, plus the spotlighting variant and the separate `agent_llm` tag — the derived-action agent runs at temperature 0 to match 3B's probe, and a mismatch here is a confound, not a detail |
| `phase11/benchmark.json` | `python3 -m evaluation.benchmark --preset ladder --repeats 3` | The cumulative ladder: per-rung ASR/WCR, per-layer attribution, and **paired McNemar on two outcomes** — an ASR-only ladder reports 3C as inert |
| `phase11/manifest.json` | same run | As above. `replay.fully_replayed: true` — the outcomes are the original run's cached results; the commit describes the reporting code that added the WCR ladder |
| `phase11_loo/benchmark.json` | `python3 -m evaluation.benchmark --preset loo --repeats 3` | Leave-one-out against `full`. Its `full` arm is the **same 54 results** as the ladder's top rung, reused from that checkpoint, which is what makes the two tables comparable rather than merely similar |
| `phase11_loo/manifest.json` | same run | `replay.fully_replayed: false` — only `full` was cached |
| `phase12/benchmark.json` | `python3 -m evaluation.benchmark --corpus injecagent --arms undefended,static_only,full` | InjecAgent direct-harm, **reported per stratum and never pooled**. Detection 93.3% where 3B's target-match fires, 10.0% where it cannot |
| `phase12/manifest.json` | same run | Plus `corpus.injecagent` — source, licence, citation, what was excluded, the 51/459 population, and the 60 `sampled_indices` drawn |
| `campaign/campaign.json` | `python3 -m evaluation.campaign_report` | **The in-corpus headline.** Layer-attributed detection 116/120 = 96.7% [91.7%, 98.7%] with per-family and per-pass breakdowns, end-to-end ASR beside it, and the two benign cohorts **kept apart** — `fpr_ours` 4/8 (a diagnostic at n=8) and `fpr_external` 2/60 (the rate). Carries `per_case` for all 188 episodes, so every rate recomputes from the file alone |
| `campaign/manifest.json` | same command | `replay.fully_replayed: true` — the outcomes are the 26 July campaign's cached per-case results and nothing was re-executed. Records what the original run **did not** leave behind: `original_manifest: null`, the run config reconstructed only as far as its own verdicts evidence it (`ie_threshold = 0.5`, model tags null), and the SHA-256 of every checkpoint consumed |
| `probe_corpus/injecagent.json`<br>`probe_corpus/agentdojo_benign.json` | `python3 -m evaluation.probe_corpus --cohort all` | **What the probe said**, per case: all four regimes, both samples, and the sanitised mediator the sanitized regimes were scored against. Its manifest pins the model tag, temperature, `k_samples` and a content hash of every probe prompt — a corpus recorded under an edited prompt is **refused**, not warned about |
| `severity/rescore_holdout.json` | `python3 -m evaluation.rescore --cohort agentdojo_attacks --json ...` | **The holdout.** AgentDojo's attack side, imported after the lexicon was frozen at `46cfbfb` and committed at `4d48efd` before the result was known. Address-free **30.0% → 43.3%**, 4/0, p = 0.125 — against 90.0% in-sample, intervals non-overlapping. 🔴 **This is the figure of record**, not `rescore.json`'s |
| `probe_corpus/agentdojo_attacks.json` | `python3 -m evaluation.probe_corpus --cohort agentdojo_attacks` | Recorded probe output for the holdout, same manifest discipline as the others |
| `severity/rescore.json` | `python3 -m evaluation.rescore --json results/severity/rescore.json` | **Four arms** — `baseline`, `capability`, `schemeless` (backlog item 8) and `both` — over every recorded cohort, re-scored offline from the corpus above. Per-stratum rates with Wilson intervals, paired McNemar, and the population projection. ⚠️ **The detection figure is in-sample** (26 of 27 distinct injections are in the draw); `capability_scoring` still defaults to `False` |
| `phase16_model_transfer/transfer.json` | `python3 -m evaluation.model_transfer` | **Does the stratification hold on a second probe model?** Per-stratum detection for `gemma3:4b` and `llama3.2:3b` over the same InjecAgent draw, same prompts, same scorer. The gap survives: **83.3 points** on the incumbent, **90.0** on the candidate. Paired over all 60 cases — 1 helped, 1 hurt, 2 discordant, exact *p* = 1.0, which is **near-zero power, not equivalence** |
| `phase16_model_transfer/manifest.json` | same command | Both recordings' model tags, temperatures, `k_samples` and prompt fingerprints, plus `identical_prompts` — if that is false the arms differ in two ways at once. Records the pre-flight that disqualified `qwen2.5:7b` (non-deterministic at 53% CPU offload) and `qwen2.5:3b` (`no_action` on both cases the incumbent detects) |
| `refusal_audit/audit.json` | `python3 -m evaluation.refusal_audit` | **An instrument check, not a result.** Per-source counts of masked-regime probe samples whose severity the Phase 10 negation predicate would lower, plus the positive control's verdict |

## Reading a manifest before trusting a result

Four fields decide whether a number is usable:

- **`commit` + `dirty`** — `dirty: true` means the tree had uncommitted changes, so
  the result is **not** reproducible from the recorded commit alone. Phase 7's
  first manifest carries `dirty: true`; the code landed in the commit that added
  this directory.
- **`ollama.on_gpu`** — after a CUDA fault Ollama silently falls back to CPU, which
  changes *outputs* as well as speed. Sampled **after** the arms run, because
  `/api/ps` lists only resident models and an idle server reports no GPU.
- **`corpus.external_benign.sampled_indices`** — which documents the external
  cohort actually contains. Phase 7's stride subsample **excludes indices 41 and 55,
  both known false positives**, which is why its FPR column is a
  catastrophic-over-blocking check and not a rate.
- **`seeding`** — there is no RNG seed. Ollama exposes none, so determinism comes
  from greedy decoding at temperature 0, and that is *not* literally deterministic
  (§6n measured 2 of 564 regime severities disagreeing). Repeats exist for this
  reason.

## Regenerating

```bash
rm -rf logs/benchmark_checkpoint          # cached results describe the OLD pipeline
python3 -m evaluation.benchmark --repeats 3
cp logs/benchmark/{benchmark.json,manifest.json} results/phase7/
```

Raw run logs stay in `logs/benchmark/run.log` and are **not** tracked — they are
large and contain attacker-authored text verbatim.

## `phase12/` carries a number that must not be pooled

The two strata are drawn 30/30 from a **51/459** population, so adding the columns
together gives 51.7% — wrong for InjecAgent by **33 points**. The manifest records the
population, the per-stratum draw and the sampled indices precisely so the projection
can be recomputed rather than guessed. There is also **no FPR** in that file:
InjecAgent ships attacks only, and 0/0 is an empty denominator.

## One entry here is not a result

`refusal_audit/` records that a defect **does not fire**, which is why it has no
row in any results table. Read it before quoting any layer-attributed number: 3B's
attributions rest on the four regime severities, and this is the check that those
severities are not inflated by refusal-shaped probe output (0 of 209 severity-2
samples, positive control passing).

It is the only artifact here that depends on **gitignored** inputs —
`logs/benchmark/run.log` and `logs/probe_diagnostic/*.json` — so a fresh clone
cannot regenerate it until Phase 7 or the probe diagnostic has been run. That is a
genuine departure from Rules §7's regenerability requirement, and it is recorded
rather than papered over: the committed `audit.json` carries the commit SHA and
per-source sample counts so the claim can at least be located, and the
non-log-dependent half of the finding is pinned by `tests/test_refusal_audit.py`,
which needs neither logs nor a model.

## What's pending

- **Phase 13's reproducibility artifact is this tree** plus the deterministic test
  suite. Every phase now has a subdirectory.
- ✅ **The campaign's own numbers now have one** — `campaign/`, added 12 Sep 2026.
  Detection 116/120 and the external FPR 2/60 both reproduce from the committed
  artifact, and `tests/test_campaign_report.py` pins the headline, the
  address-free shape of all four misses, and the refusal to pool the two benign
  cohorts.

  ⚠️ **It is a replay over gitignored inputs, and that is a real limitation.**
  The per-case outcomes come from `logs/campaign_checkpoint/`, so a fresh clone
  cannot rebuild them without re-running the campaign (~1.5 h, local GPU) — the
  same departure `refusal_audit/` records. It is mitigated rather than cured by
  committing `per_case` into the artifact: every rate in `summary` is recomputable
  from the tracked file alone, which is the half Rules §7 actually cares about.
  The original run left **no manifest** (the campaign runner predates
  `build_manifest`); the absence is recorded, not reconstructed.
