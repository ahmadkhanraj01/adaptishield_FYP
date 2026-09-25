---
tags: [adaptishield, concept, foundation]
type: concept
---

# Adaptive Threat Modeling

A security approach that **updates its own defense strategy** from observed
attack patterns and system behaviour, rather than enforcing a fixed rule set
authored in advance.

## In this project, concretely

[[3D Adaptive Threat Model]] observes labelled outcomes, computes a
[[GRPO Reward Function]], and proposes a **bounded** update to the defense's own
knobs. Three constraints define what "adaptive" is allowed to mean here:

1. **It tunes knobs, never weights.** Only [[3A Policy Engine]] patterns/tools
   and [[3B Causal Analyzer]]'s `ie_threshold`. The foundation model is untouched,
   which makes the mechanism deployable behind a black-box inference API.
2. **It trains on labelled data only.** Inferring "was this an attack?" from the
   outcome would be circular. Labels come from the [[Red Team Module]] or a
   labelled telemetry replay.
3. **It proposes; a human disposes.** `apply_update` refuses without explicit
   approval → [[Layer 5 — Human in the Loop]].

## The honest result

On every corpus tested at every scale, the adaptive layer's correct output has
been **no change at all** → [[The Adaptive Layer Proposes a No-Op]]. The single
improvement it ever found reversed against externally-authored benign data →
[[6n — A Corpus That Can Fail]].

That is not a failure of the implementation. Every safeguard functioned; the
residual failures simply lie in components the knobs cannot reach — see
[[Residual Misses Decomposed]].

## The two loops it was specified to close

[[Closed-Loop Adaptive Learning]] — reactive (from live telemetry) and proactive
(from red-team episodes), both gated by the human governance loop.
