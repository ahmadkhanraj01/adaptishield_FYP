---
tags: [adaptishield, finding, negative]
type: finding
date: 2026-07-25
---

# 6l — No Natural Gap at Scale

**The natural-gap question, answered: no.**

## Setup

The expanded campaign: **6 families × 4 directives × 2 training targets**, plus
gen-2 mutations and a held-out pass → **118 labelled episodes** (114 malicious,
4 benign), packaged from the live pipeline by
`evaluation/kaggle/package_episodes.py`.

The [[Red Team Module]] grid had been widened first, precisely so the question
could be asked at scale rather than on four families.

## Result

- `caught_by_causal` = **99/114 (87%)**, 15 missed by [[3B Causal Analyzer]]
- **0/4** benign false positives
- Replaying [[GRPO Reward Function]] across the **whole IE grid**: lowering
  `ie_threshold` below 0.5 catches **zero** more attacks (missed flat at 15);
  raising it loses one.

> **Mean reward is flat across the entire threshold grid.** The real GRPO trainer
> therefore converges to a **no-op.**

## Why the 15 were unreachable

They are **measurement-layer** failures, not threshold failures: 14/15 had
inconsistent IE separation, some had `masked = 0` or negative IE. No setting of
the knob [[3D Adaptive Threat Model]] controls recovers any of them.

That is a *quantified* statement of why the adaptive layer's honest output is a
no-op → [[The Adaptive Layer Proposes a No-Op]].

## What it licensed

Precisely because the negative was quantified rather than assumed, it justified
looking one layer down — which produced [[6m — The Single-Character Defect]],
where all 15 turned out to share a single cause.

## What this does not establish

That the knob is useless — [[6j-6k — The Loop Closes a Matching Gap]] shows it
closes a matching gap. And it does not establish that a *learned* policy beats
the heuristic: with no reachable gap, neither can improve detection, so they
agree on the no-op. That agreement is itself the valid finding, but it is not a
comparison.
