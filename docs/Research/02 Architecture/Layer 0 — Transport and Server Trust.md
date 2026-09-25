---
tags: [adaptishield, architecture, layer]
type: component
status: built
---

# Layer 0 — Transport and Server Trust

**Entirely absent from prior MCP-aware architectures.** It defends the protocol
and supply-chain surfaces *before* any user input or tool output reaches the
agent. Justified by [[MCPSecBench]]'s finding of 100% ASR for protocol-level
attacks with no existing countermeasure.

## Specified components

| Component | Role | Addresses |
| :--- | :--- | :--- |
| Transport Integrity Verifier | TLS enforcement, authenticated peer, payload integrity | MitM, DNS rebinding |
| **Server Trust Registry** | Signed registry per [[ETDI]]; identity bound to declared capabilities + version | rug pull |
| Schema Validator | Tool definitions vs expected protocol schema | schema inconsistency DoS |
| Name Squatting Guard | Lexical + semantic similarity to existing registry entries | package name squatting |

## Built

`layer0/server_trust_registry.py` — SHA-256 signatures binding server identity to
declared tool capabilities and version. Re-verification detects rug-pull by
signature mismatch. **Exposes the allowlist consumed by the Network Egress Filter**
in [[Layer 4 — Sandbox and Isolation]].

Smoke test: `python3 layer0/server_trust_registry.py` → legit `True`, rug-pull `False`.

## Scoping

Layer 0 is **present in both the baseline and the full system** — transport
security is infrastructure, not the variable under evaluation. It therefore
cannot account for any measured difference between arms.

Output to [[Layer 1 — Input and Supply Chain Screening]]: validated,
authenticated, schema-conformant tool definitions.
