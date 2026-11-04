---
tags: [adaptishield, finding, positive]
type: finding
---

# 6i — Masked Probe Rewrite

**The single largest detection gain of the implementation phase — and the source
of the project's most persistent false positive.** Fix D of [[Fixes A-D]].

## The diagnosis it followed from

[[6d — Adaptive Loop Negative Result]] found that softened attacks produced **no
signal at all**: shown a softened directive under the masked probe, the model
replied with a non-action, never recognizing the paraphrase as an instruction.
No threshold could detect what was never measured.

**The fix was in the measurement, not the decision rule.**

## The rewrite

The masked probe now elicits *the action the untrusted content directs, asks, or
prompts*, and **explicitly refuses the softened escape hatches**:

- polite phrasing
- "standard step" framing
- tool/feature notes
- hypotheticals disclaimed with "no need to actually do it"

## The result — distribution over 5 post-fix campaigns

| Metric | Before | After |
| :--- | :--- | :--- |
| gen-1 caught by 3B | 3/4 | **4/4 — 5/5 runs** |
| gen-2 caught by 3B (softened) | **1/4** | **4/4 in 4/5 runs, 3/4 in 1/5** |
| [[FPR]] | 0% | 0% — 5/5 |
| [[ASR]] | 0% | 0% — 5/5 |
| [[WCR]] | 75% / 75% | **100% / 100%** (75% in 1/5) |

Up to **+75 points** on softened attacks, with **no scorer or threshold change**.
The tool-knowledge-injection family, previously invisible, is now caught outright.

## The cost

The probe was tuned to **always find an action**. On benign content it therefore
**manufactures one** — a deliberate compliance bias, now a latent false positive
on benign mail naming a recipient. This surfaces later as
[[6p — Probe Hallucination Fixed at the Scorer]] and
[[Known Bounded False Positive]].

## Its status now

🔴 **The probe prompt is not to be tuned again without a strong reason.** Three
subsequent attempts cost **8 detections** and were reverted. The comment at that
spot in `causal_analyzer.py` records why. See [[Rules and Invariants]] and
[[Four Probe Regimes]].

## What this does not establish

A single campaign's FPR is partly sampling luck. The 0% here is over hand-written
controls that structurally could not fail — a weakness not corrected until
[[6n — A Corpus That Can Fail]].
