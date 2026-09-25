---
tags: [adaptishield, architecture, layer]
type: component
status: built
---

# Layer 4 — Sandbox and Isolation

**Defense in depth.** Permission, egress and sandbox each gate **independently**
of the 3A/3B/3C verdict. The sandbox executes only when permission **and** egress
both pass. A detection miss upstream is therefore not a breach.

## Four gates

| Gate | File | Role |
| :--- | :--- | :--- |
| **Permission Control** | `layer4/permission_control.py` | MCP scope enforcement — each server gets only its declared capability scope; out-of-scope access is blocked and logged high-severity |
| **Network Egress Filter** | `layer4/network_egress_filter.py` | Destination allowlist derived from [[Layer 0 — Transport and Server Trust]]'s registry |
| **Docker Sandbox** | `layer4/sandbox.py` | Short-lived, memory/CPU-limited, network-disabled containers (gVisor/runsc supported once configured) |
| **Telemetry Stream** | `layer4/telemetry_stream.py` | One structured Episode Record per tool-return boundary, as JSON Lines |

## Why the egress filter is critical *and* is the project's biggest measurement trap

Process isolation does **not** prevent a compromised agent from sending data to
an attacker-controlled destination through an *approved* communication tool. The
egress filter closes that pathway, and it is why [[ASR]] has stayed at 0%.

It is also why ASR is nearly useless as a detection metric here: the allowlist
catches the exfiltration regardless of whether any detection layer noticed. See
[[Backstops Mask Progress]] — and [[Phase 7 Benchmark Withdrawn]], where this
exact effect invalidated a benchmark result.

## Telemetry handling

`logs/episode_records/episodes.jsonl` — includes `screen_result.matched_markers`,
a 500-char `mediator_snippet`, `sandbox_result`, and `causal_verdict`.

🔴 **Mediator text in telemetry is untrusted.** Treat it as untrusted input
anywhere it is displayed or replayed — including in the Layer 5 dashboard, which
escapes it so the audit tool cannot be attacked by what it audits.
