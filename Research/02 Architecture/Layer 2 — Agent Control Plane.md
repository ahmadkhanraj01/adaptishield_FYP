---
tags: [adaptishield, architecture, layer]
type: component
status: built
---

# Layer 2 — Agent Control Plane

The agent's reasoning and execution core — **and the home of the Security and
Adaptive Sub-layer, which is the primary contribution of this work.**

## Control-plane components

| Component | Role |
| :--- | :--- |
| Planner Agent | Decomposes the request into sub-tasks |
| Tool Selector *(+ Registry Auth Check)* | Verifies the tool's version and capability against [[Layer 0 — Transport and Server Trust]] before every invocation — catches rug-pulls that succeed *after* registration |
| Execution Agent | Carries out approved invocations |
| Feedback Analyzer *(+ Episode Records)* | Emits a **structured Episode Record** per tool-return boundary: boundary context, proposed next action, takeover verdict, sanitisation decision, realised outcome severity |

The Episode Record format is the interface consumed by
[[3D Adaptive Threat Model]]. Formalising it is what turned the original
architecture's "adaptive" claim into a closed loop —
[[Closed-Loop Adaptive Learning]].

## The Security and Adaptive Sub-layer

Four sequentially ordered components:

1. [[3A Policy Engine]] — static triage
2. [[3B Causal Analyzer]] — the causal probe
3. [[3C Context Sanitizer]] — [[Safe Continuation]]
4. [[3D Adaptive Threat Model]] — bounded, human-gated updates

## The tool-return boundary

Defined as the moment immediately **after** a tool response has been incorporated
into the agent context and immediately **before** the next action is emitted.
Every causal evaluation is indexed to a boundary, which is what lets a takeover
verdict carry the **localized boundary index** identifying the earliest
contaminated tool-return.
