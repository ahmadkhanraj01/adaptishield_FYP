---
tags: [adaptishield, log]
type: log
date: 2026-03-05
---

# Entry I — Research Proposal

**5 March 2026** · Volume I

The founding document. Establishes the [[Research Question]], the
[[Research Gap]], and the methodology as a **comparative experimental framework**:
a baseline static model against a proposed adaptive one.

## The proposed system, as first drawn

- LLM Orchestrator · Tool Execution Layer · Context Memory Module · Policy
  Enforcement Layer · Sandboxed Execution Environment

## The static baseline

STRIDE-inspired threat categorization, rule-based prompt filtering, fixed tool
access controls, deterministic refusal policies. **It does not update at runtime
and serves as the control condition.**

## The adaptive system's three components

- **A — Multi-Agent Autonomous Red Teaming**: Attack Generator, Execution,
  Evaluator, Optimizer → became [[Red Team Module]]
- **B — Temporal Causal Diagnostics** at tool-return boundaries, to avoid
  premature workflow termination → became [[3B Causal Analyzer]]
- **C — Reinforcement-learning policy adaptation** → became
  [[3D Adaptive Threat Model]]

## Metrics fixed from day one

[[ASR]] · [[FPR]] · [[WCR]], plus long-term robustness under dynamic adversarial
conditions. **These never changed**, which is worth noting: the metric definitions
survived every reversal in the project intact.

## The four shortcomings it names

Threat models simplistic and isolated · defenses terminate rather than continue ·
red teaming manual and unrealistic · backend and supply-chain surfaces
underexplored.

Next: [[Entry II — Core Theory]].
