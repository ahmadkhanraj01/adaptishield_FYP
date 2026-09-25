---
tags: [adaptishield, log, negative]
type: log
date: 2026-07-22
---

# Entry XI — The Adaptive-Loop Negative Result

**22 July 2026** · Volume I

> *"The most scientifically valuable finding of the implementation phase
> precisely because it is negative and reproducible."*

The headline experiment proposed at the close of
[[Entry X — From Architecture to Working Prototype]] — apply a 3D proposal and
re-measure — **failed**, and the previous entry's "confirmation" is retracted.

## Sections

- **A** — the negative result → [[6d — Adaptive Loop Negative Result]]
- **B** — four corrective fixes → [[Fixes A-D]]
- **C** — the measurement fix's result → [[6i — Masked Probe Rewrite]]
- **D** — re-running the loop: it had nothing to close →
  [[6j-6k — The Loop Closes a Matching Gap]]
- **E** — demonstrating the loop *can* close a matching gap, **and generalize**
- **F** — implication for the thesis

## What the entry establishes

The corrected picture is **more defensible than the one it replaces**:

- ASR held at 0% across repeated campaigns
- the causal detector, after the measurement fix, catches softened injections it
  previously missed
- the adaptive loop is now **honest** — it neither memorizes nor operates an
  inert control — and is **demonstrably capable of closing a gap its knobs match**

## What it leaves open — and this framing is the important part

> What remains open is **whether such a gap arises naturally**, rather than by
> construction, on a larger held-out attack set; and whether a **learned** GRPO
> policy improves on the directional heuristic.

Both questions are handed forward with their prerequisites explicitly satisfied:
a signal-bearing measurement, a non-inert control, an honest reward, and a
demonstrated closing loop. All four are pinned by deterministic regression tests
**so that subsequent training work cannot silently regress them.**

Answer to the first question: [[6l — No Natural Gap at Scale]] — **no**.

Previous: [[Entry X — From Architecture to Working Prototype]] · Next:
[[Entry XII — GRPO at Scale and a Single-Character Defect]].
