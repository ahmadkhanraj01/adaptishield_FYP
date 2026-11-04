---
tags: [adaptishield, finding, hub]
type: hub
---

# Findings Index

Every result the project has produced, positive and negative. **Negatives are
first-class** — several of them are the contribution.

## The numbered findings (§6d–§6p)

| § | Subject | Outcome |
| :--- | :--- | :--- |
| 6d | [[6d — Adaptive Loop Negative Result]] | **Negative** — the apparent gain was memorisation of a training address |
| 6e | [[6e — Semantic Scoring Ablation]] | More accurate per action, **worse end-to-end**; ships off |
| 6f | [[6f — Standalone Severity Rule]] | First change that improved the *system* rather than a component |
| 6g | [[6g — Temporal Drift Scoping]] | Fixed — history scoped per session |
| 6h | [[6h — IE Consistency Guard]] | Fixed — requires consistent separation across samples |
| 6i | [[6i — Masked Probe Rewrite]] | **Largest detection gain**; introduced a latent false positive |
| 6j–6k | [[6j-6k — The Loop Closes a Matching Gap]] | Yes when its knob matches one — **and it generalises** |
| 6l | [[6l — No Natural Gap at Scale]] | **No gap** — GRPO converges to a no-op |
| 6m | [[6m — The Single-Character Defect]] | **One defect** — a single character of string comparison |
| 6n | [[6n — A Corpus That Can Fail]] | **GRPO's only gain was an artifact of our own benign corpus** |
| 6o | [[6o — Phase 6 Executed on Kaggle]] | Backends agree to exactly zero; **the P100 cannot run PyTorch** |
| 6p | [[6p — Probe Hallucination Fixed at the Scorer]] | Detection 96.7%; the false positive **survived via a second route** |

## Cross-cutting results

- [[Fixes A-D]] — the four measurement corrections that had to land before training
- [[The Adaptive Layer Proposes a No-Op]] — the honest headline
- [[Reward-Decreasing Proposals]] — four times, on different hardware
- [[Inert Blocked Patterns]] — a rule that presents as protection while providing none
- [[Instruments Fail More Than Mechanisms]] — the pattern across the whole project
- [[Backstops Mask Progress]] — why ASR is nearly useless here
- [[Residual Misses Decomposed]] — where the remaining 4 failures actually live
- [[Known Bounded False Positive]] — deliberately left open, and why
- [[3B Layer 4 Boundary]] — a scoping result, not a defect
- [[Address-Free Attacks]] — the corpus change that made IE non-redundant
- [[Design Lessons]] — the ones that generalize beyond this project

## Phase 7 — the comparative claim

- ✅ [[Phase 7 Repaired — The Causal Sub-Layer's Marginal Detection]] — **ASR
  71.4% → 14.3%**, 18/21 stops attributed to 3B, **zero** detection stops in
  `static_only`, and Layer 4 contributes **nothing incremental** once 3B is on

## Phase 12 — external validity

- ✅ [[Phase 12 — Detection Is 18% on Someone Else's Attacks]] — **96.7% on our
  campaign, ~18% projected on [[InjecAgent]]'s direct-harm split.** One mechanism:
  3B's detection rides on the target-match path, and 90% of InjecAgent is
  address-free (93.3% detected where it fires, **10.0%** where it cannot). Phase 11's
  `static_only` zero **replicates externally** — 0 of 60

## Phase 13 — the severity function

- ⚠️ [[The Schemeless URL Fix Costs More Than It Buys]] — a real one-line defect
  (`https?://` only, so a bare host is invisible), fixed and left **off**: **+2
  detections for +3 false positives** on the holdout, FPR 3.3% → 8.3%. All three
  FPs are *"visit www.X.com"*, which is also AgentDojo's own phishing injection —
  the [[3B Layer 4 Boundary]], not a tuning problem
- 🔴 [[The Lexicon Generalises About Half]] — the **holdout**. In-sample 90.0%,
  holdout **43.3%** [27.4%, 60.8%], 4 helped / 0 hurt, p = 0.125. Intervals do not
  overlap: the in-sample figure overstated generalization by ~47 points. Also
  found a **schemeless-URL gap** in `_extract_suspicious_targets`
- 🟡 [[The Scorer Had One Harm Class]] — the address-free gap was **not a
  threshold**: the probe transcribes those injections correctly and `_HIGH_KW`
  has no word for them. A grounded verb+resource class takes the address-free
  stratum **13.3% → 90.0%** (23/0, p = 0.0000) with no measurable FPR change —
  but the figure is **in-sample** and the default is still off
- ✅ [[Recorded Probe Output Makes Scorer Changes Cheap]] — a scorer candidate
  went from a **1.5-hour campaign** to seconds, because the probe never consults
  the scorer. Verdict agreement **15/15** vs Phase 12, **58/60** vs the campaign
- ⚠️ [[The Benign FPR Has a Noise Floor Its Own Size]] — the committed **3.3%**
  reproduces as a *rate* but not as the same two cases. Run-to-run variation is
  ±2–3 in 60, the same size as the effects being compared

## Phase 11 — the per-component matrix

- ✅ [[Phase 11 — Only Two Layers Do Anything]] — **3B stops attacks (18/0,
  p = 0.000), 3C keeps the workflow alive (18/0 on WCR, p = 0.000), and the other
  four components change nothing measurable** — cumulatively *and* at the margin,
  with **zero discordant pairs**. Layer 4 turns out to be *redundant* rather than
  contributing: 6 of 18 of 3B's stops would also have been caught by the allowlist

## Phase 10 — the external baseline

- ✅ [[Phase 10 — Spotlighting Has No Measurable Effect]] — datamarking 34.8% →
  33.3% steered, McNemar **p = 1.00**; the null is two opposing per-family effects
  cancelling, not indifference
- 🔴 [[The Scorer Cannot See Negation]] — a refusal naming the attacker address
  scored as compliance, which **reversed the sign** of the result above. Fixed for
  agent-chosen actions; measured absent for 3B's regimes ↓
- ✅ [[3B's Refusal Exposure Is Live and Unrealised]] — **0 of 209** recorded
  severity-2 masked-regime samples are refusal-shaped, with a passing positive
  control. The defect is live on the shipped keyword path and has never fired,
  because the masked probe gives the model no competing goal to refuse in favour
  of. Regime scorer left unchanged
- 🟡 [[Phase 10 Floor — The Injections Do Not Steer a 4B Planner]] — why the
  benchmark vectors could not power the comparison (ASR 1/7) and the campaign
  corpus was used instead

- ⚠️ [[The Probe's Compliance Does Not Transfer]] — **title corrected the same day.**
  Two of three candidates fail, in opposite ways: `qwen2.5:7b` complies but is
  **non-deterministic** at 53% CPU offload, `qwen2.5:3b` is deterministic at 100% GPU
  but returns `no_action` on **both** cases gemma detects, with no refusal string
  anywhere. The third, `llama3.2:3b`, passes both bars — so the 4 GB ceiling makes the
  **search** hard rather than the transfer impossible. Kept under its wrong title, marked
- ✅ [[Phase 16 — The Stratification Survives a Second Model]] — **100.0% vs 10.0%** on
  `llama3.2:3b` against the incumbent's 96.7% vs 13.3% on the same draw: a **90.0-point**
  gap against 83.3, agreeing on 58 of 60 cases. The collapse is a property of the
  **mechanism**, not of one model — which is the objection §XII conceded first

## Process findings — about the evidence, not the defense

- ✅ [[A Published p-Value With No Committed Source]] — Phase 10's `McNemar p = 1.00`
  reached **five documents** with no committed implementation and no discordant
  counts in the artifact. The figure was **right**, which is luck rather than
  process. Fixed by `evaluation/paired.py` + per-case outcomes in the tracked
  artifact, and by a manifest that admits when a run was **replayed**

- ✅ [[AgentDojo's Benign Pool Is Exhausted at 60]] — the 60 benign documents are a
  **census, not a sample**: the complete in-domain benign content of AgentDojo
  v0.1.35, re-verified item-for-item against the shipped package. Reaching n=110
  needs off-domain text that would pull the [[FPR]] down for reasons unrelated to
  the defense. **Not expanded**, and the limitation relocates to *a second external
  corpus is needed, not more of this one*

- 🟡 [[The Model of Record Is 40% Resident]] — `gemma3:4b` runs **60% on CPU**,
  worse offload than the `qwen2.5:7b` this project disqualified for exactly that.
  Of four runs of the same cases, the three warm ones are identical and **the cold
  one differs** in a scored severity. Verdicts unaffected and no committed number
  restated — but every prior non-determinism result here compared warm repeats
  only, and the corpus contract pins the instrument without ever pinning residency

## ⛔ Withdrawn

- [[Phase 7 Benchmark Withdrawn]] — a headline result that measured its own
  construction. **Superseded**, kept for the contrast

## Three patterns worth carrying forward

1. **A measured negative beats an unmeasured positive.**
2. **The instruments failed more often than the mechanisms.** Five times now: the
   benchmark ([[Phase 7 Benchmark Withdrawn]]), the scorer
   ([[The Scorer Cannot See Negation]]), the missing control
   ([[3B's Refusal Exposure Is Live and Unrealised]]), the uncommitted statistic
   ([[A Published p-Value With No Committed Source]]), and the wrong outcome variable
   ([[Phase 11 — Only Two Layers Do Anything]], where the report called 3C inert).
3. **A defense measured only against a corpus its author wrote measures the
   author's imagination.** Measured twice now: 36 false positives on external benign
   data ([[6n — A Corpus That Can Fail]]), and detection 96.7% → 18% on external
   attacks ([[Phase 12 — Detection Is 18% on Someone Else's Attacks]]).
4. **A single rate over cases that are not alike explains nothing.** The 4/8 benign
   controls, the withdrawn Phase 7 arms, and Phase 12's strata — where the pooled
   figure is wrong for the population by 33 points.
