---
tags: [adaptishield, literature]
type: literature
---

# Adam — Stochastic Optimization

*"Adam: A Method for Stochastic Optimization"* · **Reviewed:** 18 March 2026

## Why a 2015 optimizer paper is in a security review

It supplies the *adaptive* half of the thesis vocabulary. Its gap — that fixed
optimization schemes require manual tuning and handle sparse, non-stationary data
badly — is structurally the same complaint the project makes about **static
threat models**: a predefined rule set cannot track a moving adversary.

## Method

Adaptive learning rates from first-moment (mean) and second-moment (variance)
gradient estimates, with bias-corrected estimates; combines AdaGrad and RMSProp
advantages.

## What was actually borrowed

Not the algorithm — [[3D Adaptive Threat Model]] uses GRPO, not Adam. What was
borrowed is the **framing**: parameters that adjust themselves from observed
data. The concrete descendant is [[GRPO Reward Function]] and the group-relative
advantage with no learned critic.

The connection is honest but loose, and worth stating as such.
