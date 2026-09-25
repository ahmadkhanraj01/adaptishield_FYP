---
tags: [adaptishield, architecture, hub]
type: architecture
---

# Defensive Stack

A request from an MCP-orchestrated LLM agent passes top-to-bottom through
layered, **independent** defenses. Each layer can stop or transform the request;
**no layer trusts the verdict of another.**

```
Layer 5  Human-in-the-loop & Observability                              [built]
Layer 4  Sandbox & Isolation  (permission · egress · docker · telemetry) [built]
Layer 3  MCP Tool Execution Plane + Tool Response Screener               [built]
Layer 2  LLM Agent Control Plane
         └─ Security & Adaptive Sub-layer   3A → 3B → 3C → 3D           [built]
Layer 1  Input & Supply-chain Screening (parser · context · provenance)  [built]
Layer 0  MCP Transport & Server Trust (rug-pull detection · allowlist)   [built]
```

The [[Red Team Module]] runs *against* this stack in dry-run mode to measure
[[ASR]] / [[FPR]] / [[WCR]].

## The layers

- [[Layer 0 — Transport and Server Trust]]
- [[Layer 1 — Input and Supply Chain Screening]] — *load-bearing for the whole method*
- [[Layer 2 — Agent Control Plane]] — contains the primary contribution
- [[Layer 3 — Tool Execution Plane]]
- [[Layer 4 — Sandbox and Isolation]] — *defense-in-depth backstop*
- [[Layer 5 — Human in the Loop]]

## The sub-layer that is the contribution

[[3A Policy Engine]] → [[3B Causal Analyzer]] → [[3C Context Sanitizer]] →
[[3D Adaptive Threat Model]]

## Component-to-file map

| Layer | Component | File |
| :--- | :--- | :--- |
| 0 | Server Trust Registry | `layer0/server_trust_registry.py` |
| 1 | Provenance / Context | `layer1/provenance.py` |
| 2·3A | Policy Engine | `layer2/security_sublayer/policy_engine.py` |
| 2·3B | Causal Analyzer | `layer2/security_sublayer/causal_analyzer.py` |
| 2·3C | Context Sanitizer | `layer2/security_sublayer/context_sanitizer.py` |
| 2·3D | Adaptive Threat Model | `layer2/security_sublayer/adaptive_threat_model.py` |
| 3 | Tool Response Screener | `layer3/tool_response_screener.py` |
| 4 | Permission Control | `layer4/permission_control.py` |
| 4 | Network Egress Filter | `layer4/network_egress_filter.py` |
| 4 | Docker Sandbox | `layer4/sandbox.py` |
| 4 | Telemetry Stream | `layer4/telemetry_stream.py` |
| 5 | Governance / gate | `layer5/governance.py`, `layer5/review.py` |
| 5 | Audit dashboard | `layer5/audit_report.py` |
| — | Shared parsing | `utils/parsing.py` |
| — | Full pipeline | `adaptishield_pipeline.py` |

## The property that defines the design

**Layered, independent defenses.** [[Layer 4 — Sandbox and Isolation]] gates
independently of 3A/3B/3C, so a detection *miss* is not a *breach*. ASR has
stayed 0% on address-carrying attacks precisely because the egress allowlist sits
under everything.

That same property is a measurement hazard → [[Backstops Mask Progress]].

Flow: [[Request Flow]].
