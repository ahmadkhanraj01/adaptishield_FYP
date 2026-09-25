---
tags: [adaptishield, finding]
type: finding
date: 2026-07-22
---

# Fixes A-D

The four independent defects diagnosed by [[6d — Adaptive Loop Negative Result]],
each corrected, each regression-tested, and **each a principle worth keeping**.
They were the prerequisites that had to land *before* any GRPO training, because
**training a policy over a broken measurement produces a confident no-op.**

| Fix | Defect | Principle |
| :--- | :--- | :--- |
| **A** | 3D harvested literal exfil addresses into `blocked_patterns` | **Generalize, don't memorize.** Proposals carry generalizable injection *phrasing* only; exact destinations are Layer 4's job |
| **B** | Reward scored a blanket block equal to a safe continuation | **The reward must respect [[WCR]].** `+1.0` vs `+0.7`, or the optimizer optimizes toward killing legitimate work |
| **C** | `threshold_step` finer than the IE grid (0.5 → 0.4) | **A tuning step finer than the metric's resolution is a provable no-op.** `threshold_step = ie_resolution` |
| **D** | The masked probe let the model reply `no_action` on softened attacks | **Measurement wording drives signal.** → [[6i — Masked Probe Rewrite]] |

## The result of D

`caught_by_causal` on gen-2 (softened) attacks: **1/4 → 3/4** at 0% [[FPR]], with
**no scorer or threshold change**. The single biggest gain in the project. Full
distribution in [[6i — Masked Probe Rewrite]].

## What A–D collectively establish

**The fixes that mattered all lay *outside* the knobs the adaptive loop
controls.** The measurement rewrite and the reward/proposal hygiene closed the
gap — not 3D. That is why [[6j-6k — The Loop Closes a Matching Gap]] found the
loop had nothing left to close, and it is the origin of
[[The Adaptive Layer Proposes a No-Op]].

Tests went 8 → **22 deterministic** (`test_takeover_rules.py`,
`test_adaptive_threat_model.py`). All four are pinned so training cannot silently
regress them. See [[Rules and Invariants]].
