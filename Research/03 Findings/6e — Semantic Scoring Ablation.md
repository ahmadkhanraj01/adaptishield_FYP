---
tags: [adaptishield, finding, negative]
type: finding
---

# 6e — Semantic Scoring Ablation

`evaluation/score_action_ablation.py` — keyword vs semantic scoring for
[[3B Causal Analyzer]]'s `_score_action`.

## Result

The semantic (LLM-judge) scorer is **more accurate per action** and **worse
end-to-end**. It ships **off by default**.

## Why

> **Component accuracy ≠ contrast accuracy.**

IE is a **difference** ([[ACE IE DE]]). Scoring *both* regimes correctly
cancelled the gap the detector reads. Improving the component destroyed the
signal the system depends on.

> **Optimize the contrast, not the component.**

This is the most counter-intuitive lesson in the project and is recorded in
[[Design Lessons]].

## Secondary finding

The judge **disagrees with itself across paraphrases**, causing flaky [[FPR]] —
observed flapping 0% ↔ 25% on identical inputs. 🟡 If semantic scoring is ever
revisited, run the judge at **temperature 0**. See [[Rules and Invariants]].

## Why it still matters

All 4 residual detection failures are **severity-function** failures
([[Residual Misses Decomposed]]). The obvious repair is a better scorer — and 6e
is the reason that repair needs a **third approach**, not a re-run of this one.
See [[Backlog]].

## What this does not establish

That semantic scoring is unusable in principle — only that a per-action accuracy
gain does not survive being differenced, in this architecture, at this sample
count.
