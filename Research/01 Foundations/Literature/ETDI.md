---
tags: [adaptishield, literature]
type: literature
---

# ETDI

The framework the **Server Trust Registry** follows in
[[Layer 0 — Transport and Server Trust]].

Every MCP server registration requires a cryptographic signature binding the
server identity to its **declared tool capabilities and version**. Before any
tool list is accepted from a server, the registry verifies the server's current
identity against the registered signature; a version mismatch is flagged as a
potential **rug-pull attack** and quarantined for review.

## As implemented

`layer0/server_trust_registry.py` uses SHA-256 signatures binding identity to
declared capabilities and version. Re-verification detects rug-pull by signature
mismatch, and the registry exposes the allowlist consumed by the
**Network Egress Filter** in [[Layer 4 — Sandbox and Isolation]].

That coupling matters more than it looks: the egress allowlist derived from this
registry is the backstop that keeps [[ASR]] at 0%, and therefore also the thing
that **conceals detection failures** unless attacks are deliberately pointed at
legitimate destinations. See [[Backstops Mask Progress]].
