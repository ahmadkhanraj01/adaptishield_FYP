---
tags: [adaptishield, finding]
type: finding
---

# Inert Blocked Patterns

🔴 **Every proposal the trainer has ever produced carries a blocking pattern that
cannot fire.**

Found by [[Layer 5 — Human in the Loop]] **on its first execution against a real
proposal**.

## The mechanism — a namespace mismatch

- [[3A Policy Engine]] matches `blocked_patterns` against the agent's **proposed
  action**
- [[3D Adaptive Threat Model]] harvests candidates from the screener's
  **`matched_markers`**, which describe **untrusted mediator content**
  ([[Layer 3 — Tool Execution Plane]])

**These are different namespaces.** The string in question appears as a marker on
**48 of 188** episodes and in **none** of the proposed actions.

> **A rule that presents as protection while providing none is worse than no
> rule.**

## Why four automated guards missed it

The trainer, its reward function, the verification step and the minimality pass
**all reason about reward** — and **an inert rule changes reward by exactly
nothing.** It is invisible to every reward-based check by construction.

This is the sharpest available demonstration that
[[Reward-Decreasing Proposals]]' propose-and-verify machinery, while necessary,
is **not sufficient**.

## The fix

The gate now evaluates **every proposed pattern against the batch** and reports
those that are inert.

## Status

The namespace mismatch in [[3A Policy Engine]] itself is **still open** — the gate
*detects* inert patterns; it does not make them fire. Whether 3A should match
mediator markers, or 3D should harvest from proposed actions, is undecided.

## What this does not establish

That the gate can catch this class in general. It caught **this** inertness by
replaying patterns against a batch. A rule inert for a reason the batch does not
exercise would still pass. The gate **cannot detect an error in its own
recomputation**, and no claim is made that it could.

Part of [[Instruments Fail More Than Mechanisms]].
