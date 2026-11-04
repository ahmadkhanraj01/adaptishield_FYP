---
tags: [adaptishield, log]
type: log
date: 2026-05-15
---

# Entry — Single-Machine Implementation Guide

**15 May 2026** · Volume I · *"Adaptive MCP Security Framework — Single-Machine
Implementation Guide for Research"*

The bridge between specification and code: a survey of **state-of-the-art MCP
protection**, followed by the concrete technology choices that make the whole
system runnable on one laptop.

## SOTA static MCP protection, surveyed

| Technique | Purpose | Became |
| :--- | :--- | :--- |
| **RSA-based manifest signing** | Prevent tool/descriptor tampering; detect rug pull | [[Layer 0 — Transport and Server Trust]] (SHA-256 in practice) |
| **LLM-on-LLM semantic vetting** | A secondary model analyses tool descriptions before use | Supply Chain Scanner + [[Layer 3 — Tool Execution Plane]] screener |
| **Runtime heuristic guardrails** | Detect abnormal commands, block dangerous execution | [[3A Policy Engine]] |
| **Sandboxed execution** | Protect the host, prevent lateral movement | [[Layer 4 — Sandbox and Isolation]] |
| **Zero Trust MCP architecture** | Trust nothing by default | The "no layer trusts another's verdict" property of [[Defensive Stack]] |

## The eight MCP attacks named

Prompt injection · tool poisoning · shadowing · rug pull · context poisoning ·
malicious tool manipulation · unauthorized tool execution · multi-turn context
takeover → [[Threat Taxonomy]].

## The stack chosen

Docker + Linux containers for isolation · Stable-Baselines3 for RL ·
Prometheus/Grafana/ELK for monitoring · ChromaDB + PostgreSQL for memory.

Notable divergences in the built system: **RL is hand-implemented GRPO, not
Stable-Baselines3** ([[MCP-RiskCue]]), and the monitoring stack was replaced by
JSONL telemetry plus a self-contained HTML dashboard
([[Layer 5 — Human in the Loop]]) — because everything must run offline on one
machine.

## The criterion that drove every choice

**Completely free · offline execution · privacy-safe · no API cost.** That
constraint is why models are local ([[Models in Use]]) and why GPU-heavy work goes
to Kaggle ([[Compute Strategy]]).

Next: [[Entry X — From Architecture to Working Prototype]].
