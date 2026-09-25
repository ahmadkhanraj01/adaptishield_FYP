---
tags: [adaptishield, literature]
type: literature
---

# MCPSecBench

**The finding that justifies [[Layer 0 — Transport and Server Trust]] existing at all.**

> Protocol-level attacks achieve **100% ASR** against all evaluated platforms,
> with no existing countermeasure.

Layer 0 is the architectural response to precisely this: a layer entirely absent
from prior MCP-aware architectures, defending the protocol and supply-chain
surfaces *before* any user input or tool output reaches the agent.

## Also supplies

- Attack identifiers referenced throughout the architecture spec (ATT-3 schema
  inconsistency, ATT-5 DNS rebinding, ATT-6 MitM, ATT-9/ATT-11 name squatting,
  ATT-13 rug pull) → [[Threat Taxonomy]]
- Half of the eight vectors in [[Phase 7 — Eight-Vector Benchmark]] (with
  [[Du et al — Mobile LLM Agents]])
- Part of the metric protocol for [[ASR]] / [[FPR]] / [[WCR]]

## Honest scoping

Layer 0 in this project is built and tested (`server_trust_registry.py`:
allowlist + rug-pull detection via SHA-256 signature binding), but it is
**infrastructure, not the variable under evaluation** — it is present in both the
baseline and the full system, so it cannot account for any measured difference.
