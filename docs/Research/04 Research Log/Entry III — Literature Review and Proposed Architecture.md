---
tags: [adaptishield, log]
type: log
date: 2026-03-18
---

# Entry III — Literature Review and Proposed Architecture

**18 March 2026** (review) and **27 March 2026** (architecture) · Volume I

## The three papers

| Paper | Contribution |
| :--- | :--- |
| [[MCP Security Survey]] | The threat landscape; the absence of a unified framework |
| [[Du et al — Mobile LLM Agents]] | Empirical real-world vulnerability; the **eight-vector** structure |
| [[Adam — Stochastic Optimization]] | Adaptive-parameter framing for dynamic defense |

**Derived gap** → [[Research Gap]].

## The first architecture (27 March)

Five layers plus supporting modules:

1. **Interaction and Data Plane** — Input Parser, Context Builder, Memory Store
2. **LLM Agent Control Plane** — Planner, Tool Selector, Execution Agent,
   Feedback Analyzer
3. **Security and Adaptive Layer** *(the primary contribution)* — Policy Engine,
   Causal Analyzer, Threat Model, Context Sanitizer
4. **Tool and Execution Plane**
5. **Sandbox and Isolation Layer** — gVisor, Permission Control, Telemetry
6. Human-in-the-Loop and Observability

## What this version got wrong — and what fixed it

[[Entry IV-IX — AdaptiShield Specification]] is best read as a **critique** of
this one. The five defects it names:

- **No protocol/supply-chain layer at all** → [[Layer 0 — Transport and Server Trust]]
- **No screening of tool responses** — an undefended IPI channel →
  [[Layer 3 — Tool Execution Plane]]
- **The four security components were labelled but not related to one another** —
  no ordering, no interfaces
- **The Feedback Analyzer floated outside the layer structure** with no defined
  output format → Episode Records
- **The Red Team Module had one connection and no path to the learner** — so the
  "adaptive" claim had no closed loop

Previous: [[Entry II — Core Theory]].
