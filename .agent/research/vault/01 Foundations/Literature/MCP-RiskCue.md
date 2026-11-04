---
tags: [adaptishield, literature]
type: literature
---

# MCP-RiskCue

The training approach [[3D Adaptive Threat Model]] follows: Episode Records
formatted as `(state, action, reward)` tuples optimized with **Group Relative
Policy Optimization (GRPO)**.

## What GRPO means here concretely

- The trainer samples **groups** of candidate actions (thresholds, or joint
  configurations)
- Computes a **group-relative advantage** against the group mean
- Applies a REINFORCE update — **no learned critic**
- A **minimal-intervention term** breaks ties toward the action nearest the
  incumbent, so that the absence of a gap yields a no-op rather than an arbitrary
  move

Implemented twice — torch (for accelerated hardware) and pure standard library
(so it runs on the 4 GB development box). The two were finally compared in
[[6o — Phase 6 Executed on Kaggle]] and agree to **exactly zero**.

## The critical divergence from the source approach

GRPO here **never updates model weights**. It updates [[3A Policy Engine]] rules
and [[3B Causal Analyzer]] thresholds only. That makes the mechanism deployable
in black-box settings where the LLM is reached only through an inference API —
and it is a hard invariant, see [[Rules and Invariants]].

The reward is specified in [[GRPO Reward Function]]. The thing the method taught
us that the source did not: [[Reward-Decreasing Proposals]].
