---
tags: [adaptishield, architecture, method]
type: concept
---

# Closed-Loop Adaptive Learning

Two feedback loops plus a governance loop. The original architecture *claimed*
adaptive behaviour but had **no complete feedback path** — no defined episode
format and no connection from the red team to the learner.

## A — Reactive loop (from live telemetry)

Live executions → Episode Records via the Telemetry Stream in
[[Layer 4 — Sandbox and Isolation]] → [[3D Adaptive Threat Model]]'s training
buffer → GRPO updates to [[3A Policy Engine]] rules and
[[3B Causal Analyzer]] thresholds → subsequent boundary evaluations.

*The system improves in response to attacks observed in deployment.*

## B — Proactive loop (from red teaming)

The [[Red Team Module]]'s Evaluator scores attempts against current defenses;
**successful** attacks are packaged as high-priority Episode Records and injected
into the same buffer alongside live telemetry.

*The system learns from adversarial examples before real attackers arrive.*
Together the two loops give the learner a curriculum of real behaviour **and**
adversarially optimized patterns.

## C — Human governance loop

The Policy Inspection Console in [[Layer 5 — Human in the Loop]] connects to 3A
via a **governed** update channel: review, edit, or override before anything
takes effect. This prevents policy drift from a miscalibrated reward and
maintains human accountability.

## Status, honestly

The **plumbing is complete and validated**; the *learning* has nothing to learn.
On every corpus tested, the reactive and proactive loops deliver episodes over
which the reward is flat in every knob 3D controls →
[[The Adaptive Layer Proposes a No-Op]].

The governance loop, by contrast, has done real work on its first run —
[[Inert Blocked Patterns]] and [[Reward-Decreasing Proposals]].
