---
tags: [adaptishield, finding, instrument, method]
type: finding
status: built
date: 2026-08-09
---

# Recorded Probe Output Makes Scorer Changes Cheap

**A scorer candidate used to cost a 1.5-hour campaign to evaluate. It now costs
seconds.** `evaluation/probe_corpus.py` + `evaluation/rescore.py`.

## Why [[Backlog]] item 1 stalled twice

Both previous attempts on the severity function shipped before anyone could see
the cost. [[6e — Semantic Scoring Ablation]] needed a full campaign to discover
the semantic scorer was worse end-to-end; [[6p — Probe Hallucination Fixed at the
Scorer]] needed three campaigns to discover the probe prompt had lost 8
detections. The price of a look was the reason the item sat.

## The property that makes it work

`_run_regime_once` does two separable things: it asks the model for an action,
then scores that action. **The probe prompts and the sanitizer never consult the
scorer.** So a change confined to `_score_action` cannot alter which action the
probe returns — re-scoring a recorded action is the same computation the live
pipeline performs, not an approximation. The recorded actions are a *sufficient
statistic* for any scorer candidate.

It records all four regimes, both samples, and — the part the Phase 7 log could
not supply, so [[3B's Refusal Exposure Is Live and Unrealised]] had to fall back
to unsanitised text — **the sanitised mediator actually shown to the
masked_sanitized probe**. Without that, IE cannot be recomputed at all.

## Three ways it was built not to lie

1. **Staleness is refused, not warned about.** The manifest pins the model tag,
   temperature, `k_samples` and a **content hash of every probe prompt**
   (`utils/hashing.py`, comments and docstrings stripped so prose edits do not
   invalidate it). A corpus recorded under an edited prompt re-scores perfectly
   happily and answers confidently about code that no longer exists — the
   [[Rules and Invariants|stale checkpoint]] trap wearing a new hat.
2. **The verdict comes from the shipped rules.** `_decide_takeover` was extracted
   from `evaluate_boundary` so both callers use one copy. A report that restates
   a threshold measures its own restatement — which is precisely how Phase 12's
   first stratum mislabelled 135 of 186 cases, and what the refusal audit had to
   correct.
3. **A model call is an exception, not a slowdown.** The analyzer's client is
   replaced with a stub that raises, so "no model calls" is enforced rather than
   asserted in a docstring.

## Validated against runs that already exist

| Against | Agreement |
| :--- | :--- |
| Phase 12 InjecAgent (15 shared cases) | masked 15/15, verdict **15/15** |
| Committed campaign, AgentDojo benign (60) | masked 57/60, verdict **58/60** |

⚠️ The benign disagreements are not noise to wave past — they are
[[The Benign FPR Has a Noise Floor Its Own Size]], and they bound what any single
run of this instrument can resolve.

## What it does NOT cover

A change to a **probe prompt**, the **sanitizer**, the **model tag** or the
**temperature** invalidates the corpus outright. No flag rescues it; re-record.
This makes scorer work cheap and leaves prompt work exactly as expensive as it
was — which, given [[6p]], is the right way round.

## Related

- [[The Scorer Had One Harm Class]] — the first result it produced
- [[Instruments Fail More Than Mechanisms]]
- [[Test Suite]] — 426 tests, +83 this session
