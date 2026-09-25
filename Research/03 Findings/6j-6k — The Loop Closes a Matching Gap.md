---
tags: [adaptishield, finding, positive]
type: finding
---

# 6j-6k — The Loop Closes a Matching Gap

Two results: the re-run after [[Fixes A-D]] (Phase 5), and the controlled
demonstration that followed (Phase 5b).

## 6j — the loop had nothing to close

Re-running `evaluation/adaptive_loop_experiment.py` with A–D in place:
`caught_by_causal` BEFORE = **4/4** (was 1/4 in [[6d — Adaptive Loop Negative Result]]).
[[3D Adaptive Threat Model]] therefore saw reward +1.0, 0 missed, 0 false
positives → proposed a **no-op**, and `apply_update` refused. AFTER = 4/4.

- **Good:** 3D no longer fabricates a phantom update. Given nothing to fix, it
  correctly proposes nothing.
- **Unsatisfying:** the loop's *value* is unproven. The base fixes closed the
  gap, not 3D's knobs. **Every failure mode that mattered lay outside those
  knobs.**

## 6k — the controlled demonstration

`evaluation/mechanism_validation.py` constructs a gap the IE threshold **can**
close, without disabling any detection rule:

- a diagnostic-style injection with `masked = 1` → so
  [[6f — Standalone Severity Rule]] is **out by construction**
- a deliberately over-conservative `ie_threshold = 1.5`
- **both** a training attack and a **held-out** attack (different attacker
  address) are initially missed

3D observes the training miss, proposes `1.5 → 1.0` with **no memorized address**
(fix A), applies it under approval, and **both** the training attack **and the
previously unseen held-out attack** are then caught.

**The loop closes a gap *and* generalizes** — the exact pairing 6d failed to
achieve. Because the fix is a global threshold plus generalizable phrasing rather
than a memorized literal address, it transfers; a memorizing proposal provably
does not.

Deterministic, pinned in `tests/test_adaptive_threat_model.py`.

## What this does not establish

**That such a gap arises naturally.** 6j already showed it does not on the
then-current attack set, and [[6l — No Natural Gap at Scale]] confirms it at ~6×
scale. 6k proves the **mechanism**, on a gap built by construction. That
distinction is load-bearing and must not be blurred when presenting the result.
