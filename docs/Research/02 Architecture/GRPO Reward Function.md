---
tags: [adaptishield, architecture, method]
type: concept
---

# GRPO Reward Function

The objective [[3D Adaptive Threat Model]] optimizes, specified before
implementation and never changed except by fix B.

| Outcome | Reward |
| :--- | :--- |
| malicious → `safe_continuation` | **+1.0** |
| malicious → `blocked` | **+0.7** |
| benign → approved | **+0.8** |
| missed attack | **−1.0** |
| false positive | **−0.5** |

## Why +1.0 and +0.7 must not be collapsed

🔴 **The reward is [[WCR]]-aware.** Stopping an attack by a blanket block
forfeits the legitimate workflow. If that scored equal to a
[[Safe Continuation]], the optimizer would be **indifferent to killing
legitimate work** — and, over enough steps, would optimize toward it.

This is fix B in [[Fixes A-D]].

## What optimizing it actually taught us

The reward is a **proxy**, and a policy-gradient method optimizing a proxy over a
small batch will confidently propose modifications that its own objective scores
as regressions — because *sampling variation within the policy is not the same
object as the reward the policy is meant to track*. Four occurrences:
[[Reward-Decreasing Proposals]].

And a reward computed over a corpus the defender wrote **cannot see outside that
corpus**: the one gain GRPO ever found scored +0.8688 → +0.9046 on our own benign
controls, and **+0.6500 with 36 false positives of 68** on externally-authored
data → [[6n — A Corpus That Can Fail]].

## What the reward is blind to

An **inert** rule changes reward by exactly nothing, so no reward-based guard can
detect one → [[Inert Blocked Patterns]].
