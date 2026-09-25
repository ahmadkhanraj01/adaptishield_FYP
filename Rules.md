# AdaptiShield — Rules & Invariants

**What this file is:** the hard constraints that must hold for anyone (human or
AI) changing this codebase. Breaking one of these has silently broken a result
before — most of them are scars, not preferences. For the reasoning behind them
see [Design.md](Design.md); for structure see [Architecture.md](Architecture.md).

*Last aligned: 2026-08-08 (adds the §8 vault-update invariant). Previously
2026-08-03 (journal target adopted; adds §7 Evidence & reporting).*

> **Publication target changed (2026-08-03, supervisor).** The paper goes to a
> **journal**, not a conference. That does not change the architecture, but it
> raises the evidentiary bar on every number that leaves this repo: reviewers
> will ask *compared to what*, *over how many episodes*, and *with what
> interval*. §7 below is the new hard constraint set that follows from it.

> **Legend:** 🔴 hard invariant (breaking it invalidates results or breaks the
> build) · 🟡 strong convention (break only with measurement + a doc update).

---

## 1. Environment

- 🔴 **`./venv` is the runtime of record.** Every command in this repo — the
  pipeline, the tests, the figures, the paper build, the site build — runs under
  it, and it satisfies `requirements.txt` in full (verified 13 Sep 2026). System
  `python3` is **not** the runtime: it carries numpy 2.2.6, which this section
  forbids. If something only works outside the venv, that is a bug in the venv,
  not a licence to switch interpreter.
- 🔴 **`numpy==1.26.4` is pinned.** numpy 2.x breaks on Python 3.10.12.
  `requirements.txt` is the source of truth and **states the pin literally** — a
  version named here but not written there pins nothing. `installed.txt` records
  the historical drift and is **evidence, not a lockfile**: never
  `pip freeze > installed.txt`.
- 🔴 **Python 3.10.12**, Ubuntu 24.04, **4 GB VRAM is a hard ceiling** for local
  GPU inference. Anything needing torch or a 7B+ model goes to **Kaggle P100**.
- 🟡 The pipeline runs locally; Kaggle is for training/evaluation only (it
  cannot host a live MCP server).

## 2. Models & probes

- 🔴 **Do not drop `CausalAnalyzer.k_samples` below 2** without re-validating
  3B end-to-end. IE resolution is `1/k_samples`; fewer samples = coarser metric.
- 🔴 **Keep the per-component model split.** 3B = `gemma3:4b` (it complies under
  the masked probe → real signal); 3C/L3/planner = `qwen2.5:3b`. A more
  refusal-prone model on 3B *destroys* the causal signal.
- 🔴 **The masked-probe prompt is calibrated (fix D / README 6i).** It must keep
  refusing the softened escape hatches (polite phrasing, "standard step",
  tool/feature notes, hypotheticals, "no need to actually do it"). Re-measure
  the gen-2 campaign + benign FPR if you touch it.
- 🟡 If `semantic_scoring` is ever revisited, run the judge at **temperature 0**
  (it disagrees with itself across paraphrases, causing flaky FPR).

## 3. 3B takeover-rule invariants (`tests/test_takeover_rules.py` pins these)

- 🔴 **The standalone `masked ≥ 2` rule (6f) must always be able to fire**, even
  when the IE consistency guard suppresses the contrast. Do **not** tighten the
  guard (6h) without the standalone rule in place — on its own the guard turns
  a strong-evidence attack into a false negative.
- 🔴 **"Nothing observed" must never mean takeover.** The drift rule is gated on
  `masked ≥ 1`; the IE rule on `masked ≥ 1` + consistent separation.
- 🔴 **Drift history is per `session_id`.** Never revert to one flat list —
  slopes across unrelated red-team cases are noise, not a trend.
- 🟡 IE rule requires `min(masked) > max(masked_san)` (consistent across
  samples). `require_consistent_ie=False` exists only for ablation.

## 4. Component 3D invariants

- 🔴 **3D never touches LLM weights.** It tunes only 3A `blocked_patterns` /
  `high_impact_tools` and 3B `ie_threshold`.
- 🔴 **`apply_update` requires `approved=True`.** 3D proposes; a human disposes.
- 🔴 **Train on labeled data only** (red-team `ExecutionResult`s or labeled
  telemetry replay). Never infer the attack label from the outcome — it is
  circular.
- 🔴 **No literal exfil targets in proposals (fix A).** `propose_update` must not
  emit raw addresses/URLs into `blocked_patterns` — that is memorization and
  inflates before/after numbers. Layer 4's allowlist covers exact destinations.
- 🔴 **`threshold_step` = `CausalAnalyzer.ie_resolution` (fix C).** A step finer
  than the IE grid is a provable no-op.
- 🔴 **The reward is WCR-aware (fix B).** malicious→`safe_continuation` (+1.0)
  must out-reward malicious→`blocked` (+0.7). Do not collapse them.

## 5. Security & handling

- 🔴 **Layer 4 is defense-in-depth.** Permission, egress, and sandbox each gate
  *independently* of the 3A/3B/3C verdict. The sandbox executes only when
  permission **and** egress both pass.
- 🔴 **Mediator text is untrusted everywhere — including in telemetry.** Episode
  Records now store mediator snippets; treat them as untrusted input anywhere
  they are displayed or replayed.
- 🔴 **Always hold out at least one attacker address/target from training.**
  README Section 6d exists because nothing was held out and memorization looked
  like generalization.

## 6. Testing & measurement

- 🟡 **Deterministic decision logic → `tests/`** (patch the four probe regimes
  out, no Ollama, sub-second). **LLM-dependent checks → `evaluation/`** (minutes,
  vary run-to-run; record numbers in docs, don't assert on them).
- 🟡 **Judge detection by the layer under test** (`caught_by_causal`), not by
  end-to-end ASR — the egress backstop keeps ASR at 0% regardless. Report both:
  layer-attributed detection *and* end-to-end ASR, and say which is which.
- 🔴 **Report FPR (and any flaky metric) as a distribution over repeated runs**,
  not a single-campaign figure. Greedy decoding is *not* literally deterministic
  (2/564 regime severities disagreed), so a single run is a sample, not a value.

---

## 7. Evidence & reporting (journal-grade claims)

*These exist because a journal reviewer sees only the numbers, not the repo.
Anything violating one of these is a desk-reject risk or a correction later.*

- 🔴 **No headline number without `n`, the named corpus, and a 95% interval.**
  Proportions use **Wilson** intervals (small `n`, near-boundary rates — normal
  approximation is wrong here). A bare point estimate is a *diagnostic*, and
  must be labelled as one in text and in tables.
- 🔴 **Never pool cohorts of different provenance.** The 8 hand-written benign
  controls and the 60 externally-authored AgentDojo benigns are separate
  cohorts, always. Pooling them is what made `4/8` look like an FPR. State
  provenance and version for every external corpus (AgentDojo v0.1.35, MIT).
- 🔴 **Every arm shares one code path.** Ablation arms are `PipelineConfig`
  values inside the pipeline, never a forked script. An "ablation" that runs
  different code is a different system, and the comparison means nothing.
- 🔴 **At least two comparison arms besides the full system**: (1) **undefended**
  and (2) a **published prompt-level defense** (spotlighting / data-marking),
  run on the *same* corpus, *same* seeds, *same* model tags. "Static rule
  baseline" is our own ablation, not an external baseline — it does not
  discharge this requirement.
- 🔴 **Held-out splits are enforced by construction, not by slicing.** As in
  `generate_training_attacks()` / `generate_holdout_attacks()`, with an
  assertion proving no held-out target leaks into training (see §5).
- 🔴 **Every number in the paper is regenerable by one committed command** whose
  artifact is committed under `results/` with a run manifest (seeds, model tags,
  corpus version, commit SHA, date). If a table cannot be regenerated, it cannot
  be claimed.
- 🔴 **A statistic is a result, not arithmetic.** No p-value, interval or rate
  enters any document before the code computing it is committed and its inputs are
  in the tracked artifact. Violated once already: Phase 10's `McNemar p = 1.00,
  8 helped / 7 hurt` reached **five documents** with no committed implementation and
  no discordant counts in `results/phase10/benchmark.json` — the paired data existed
  only in a **gitignored** checkpoint. The figure happened to be right, which is
  luck rather than process. Fixed by `evaluation/paired.py` + `paired.per_case` in
  the artifact.
- 🔴 **A replayed run must say so in its manifest.** Recomputing an old result with
  new reporting code produces a report indistinguishable from a fresh run, stamped
  with the *current* commit — a provenance lie in the artifact. `replay.fully_replayed`
  records it, and the original run's manifest is kept alongside the analysis one.
- 🔴 **Paired arms get a paired test.** Two Wilson intervals overlapping is not a
  test when both arms ran the same cases; the **discordant** pairs are the evidence.
  Report `helped` / `hurt` / `discordant`, use the exact binomial below ~25
  discordant pairs, and never read a high p as equivalence — it is low power.
- 🔴 **Negative results are reported, not quietly dropped.** The §6d
  memorization, the §6n corpus artifact (36 FP/68 benign), the policy proposing
  a reward-*decreasing* change, and the near-uniform learned distribution are
  **contributions** about generalization gaps in adaptive defense learning. They
  are the reason the Layer 5 human gate exists. Removing them to make the system
  look cleaner also removes the paper's most defensible claim.
- 🟡 **Do not describe the GRPO policy as "trained"** while the corpus leaves it
  nothing to learn — the argmax comes from the minimal-intervention tie-breaker.
  Say what it is: a policy over a knob whose reward is flat on this data.
- 🟡 **Language discipline in the manuscript:** "detected by 3B" ≠ "blocked";
  "no gap the knob can close" ≠ "no gap"; "unidentifiable on this batch" ≠
  "irrelevant". Each of these has already been confused once in these docs.
- 🟡 **Known bounded false positives stay documented, with the trade priced**
  (`workspace-041`, `workspace-055`). A reviewer finding an unlisted FP is worse
  than a listed one with a rationale.

## 8. Workflow

- 🔴 **Every session's work lands in the Obsidian vault before the session ends.**
  This applies to *anything* an AI assistant (Claude Code or otherwise) does in
  this repo — code changes, a campaign run, a number that moved, a decision
  taken, a result withdrawn. The repo stays the source of truth for code and
  numbers; **`Research/` is the source of truth for how the pieces relate**, and
  it is only useful if it is never behind. The ritual, per
  `Research/00 Meta/Vault Map.md`:

  | Did | Write |
  | :--- | :--- |
  | New result (positive **or** negative) | a note in `03 Findings`, linked from `Findings Index` |
  | Any session of work | a dated note in `04 Research Log`, linked from `Research Log Index` |
  | A number moved | `06 Metrics/Current Numbers.md` — with `n`, corpus and interval (§7) |
  | Phase state changed | `05 Phases` **and** `Phase.md` |
  | New/closed open item | `08 Open/Backlog.md`, and the next-task note if the top priority moved |
  | New trap, rule or run procedure | `07 Practice` (`Traps`, `Rules and Invariants`, `How to Run`) |
  | An architectural change | `02 Architecture` |

  Vault conventions are binding: **one idea per note**, frontmatter `tags` +
  `type`, `[[wikilinks]]` rather than prose references, status markers
  (✅ 🟡 🔴 ⛔), and **every finding note ends with `## What this does not
  establish`**. A withdrawn result is **marked, never deleted** — the corrections
  are the most transferable part of this work.
- 🔴 **`Rules.md` and `Research/07 Practice/Rules and Invariants.md` are two
  views of one thing.** Change one, change the other in the same edit.
- 🟡 **Keep the docs in sync.** On any change, update the root `README.md`, the
  relevant per-folder `README.md`, and — where affected — `Architecture.md`,
  `Design.md`, `Rules.md`, `Phase.md`.
- 🟡 **The root `README.md` lags reality.** Per-folder READMEs are the more
  reliable source of truth; when they disagree, trust the folder and fix the root.
- 🟡 **Any change that moves a reported metric also updates `results/`** and the
  affected table in the manuscript draft — a metric that changed in code but not
  in the paper is how a submission acquires a wrong number.
- 🟡 **Commits/pushes only when the user asks.** Branch off `main` first.