---
tags: [adaptishield, concept, foundation, threat]
type: concept
---

# Threat Taxonomy

Four categories, from the unified taxonomy of [[MCP Security Survey]] (150+
papers, 30+ attack techniques), mapped onto the layer that answers each.

| Category | Examples | Answered by |
| :--- | :--- | :--- |
| **Input Manipulation** | direct and [[Indirect Prompt Injection]] | [[Layer 1 — Input and Supply Chain Screening]], [[Layer 3 — Tool Execution Plane]], [[3B Causal Analyzer]] |
| **Model Compromise** | context poisoning, memory manipulation | [[Layer 1 — Input and Supply Chain Screening]] provenance, [[3C Context Sanitizer]] |
| **System and Privacy** | data leakage, unauthorized access | [[Layer 4 — Sandbox and Isolation]] |
| **Protocol-Level** | rug pull, MitM, DNS rebinding, schema inconsistency, name squatting | [[Layer 0 — Transport and Server Trust]] |

## The specific MCP attacks named

Prompt injection · tool poisoning · shadowing · **rug pull** · context poisoning ·
malicious tool manipulation · unauthorized tool execution · multi-turn context
takeover.

## Where AdaptiShield's contribution actually sits

The taxonomy is wide; the **experimentally validated** contribution is narrow and
deliberately so: the Security and Adaptive Sub-layer (3A–3D) and its feedback
loops. Layers 0, 3, 4 and 5 are literature-grounded infrastructure — built and
wired, but not the variable under evaluation.

The eight attack vectors used for the comparative benchmark are drawn from
[[Du et al — Mobile LLM Agents]] and [[MCPSecBench]] → [[Phase 7 — Eight-Vector Benchmark]].
