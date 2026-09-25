---
tags: [adaptishield, architecture, layer]
type: component
status: built
---

# Layer 1 — Input and Supply Chain Screening

**This layer is what makes [[3B Causal Analyzer]] possible.** The
trusted/mediator partition is what gives 3B something to mask; without it there
is no counterfactual and therefore no [[Causal Measurement Approach]] at all.

## Components

| Component | Role |
| :--- | :--- |
| **Input Parser** *(+ provenance tagging)* | Labels every segment by origin: user-originated, tool-returned, memory-retrieved, system-generated |
| **Supply Chain Scanner** | LLM oracle over tool metadata before registration — imperative language, priority overrides, hidden instructions, capability directives (per [[AutoMalTool]]) |
| **Context Builder** *(+ trusted/mediator split)* | Partitions into a **trusted prefix** (user goals, prior agent outputs) and an **untrusted mediator view** (tool returns, retrieved content) — replacing a flat concatenated context |
| **Provenance Memory Store** | Labels persist across turns; without persistence, IE degrades as conversation length grows |

## Built

`layer1/provenance.py` — tags trusted vs mediator content, partitions context per
`session_id`, with a **context-reset guarantee** so state does not leak across
unrelated requests.

Smoke test: `python3 layer1/provenance.py` → trusted + mediator partitions.

## Why the partition is load-bearing rather than tidy

Every quantity in [[ACE IE DE]] is a difference between a regime that sees the
mediator content and one that does not. If the two streams are not separable,
none of the four regimes in [[Four Probe Regimes]] can be constructed.

Output to [[Layer 2 — Agent Control Plane]]: provenance-partitioned,
supply-chain-screened context.
