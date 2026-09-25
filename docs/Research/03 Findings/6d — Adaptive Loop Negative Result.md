---
tags: [adaptishield, finding, negative]
type: finding
date: 2026-07-22
---

# 6d — Adaptive Loop Negative Result

**The headline experiment, and it failed.** Reorients the project's central
claim, and is the most scientifically valuable finding of the implementation
phase *precisely because* it is negative and reproducible.

## What was tested

Apply a [[3D Adaptive Threat Model]] proposal derived from the softened-attack
campaign, re-run the red-team evaluation on a fresh pipeline, and measure the
change in detection.

## Result

**Applying the update did not recover the softened attacks 3B had missed.**

The apparent improvement reported in the previous entry was an artifact of two
distinct defects:

1. **The threshold adjustment was inert.** With `k_samples = 2`, IE is quantized
   to multiples of 0.5, so a proposed step from **0.5 → 0.4 could not in
   principle change any verdict**. The step was finer than the metric's
   resolution → [[ACE IE DE]].

2. **The detections that appeared came from [[3A Policy Engine]], not
   [[3B Causal Analyzer]].** 3D had harvested the **literal attacker address**
   out of the training episodes into `blocked_patterns`. Against a held-out
   address the effect vanished entirely — a held-out generalization test
   confirmed a **0/4** block rate on the unseen address.

   That is **memorization, not generalization.**

## The deeper cause

The missed attacks produced **no signal whatsoever**. Shown a softened directive
under the masked probe, `gemma3:4b` replied with a non-action, never recognizing
the paraphrase as an instruction. **No threshold, however tuned, had anything to
detect.**

That diagnosis is what made [[6i — Masked Probe Rewrite]] the right next move
rather than more tuning.

## What it produced

[[Fixes A-D]] — four independent corrections, each regression-tested, and each a
principle worth keeping. Also the invariant that at least one attacker
address/target is **always held out** → [[Rules and Invariants]].

## What this does not establish

That the adaptive mechanism is broken. Fixes A–D plus
[[6j-6k — The Loop Closes a Matching Gap]] show the loop works when its knob
matches a real gap. What 6d establishes is that **the gap it was pointed at was
not knob-shaped**, and that an unheld-out corpus cannot tell memorization from
generalization.
