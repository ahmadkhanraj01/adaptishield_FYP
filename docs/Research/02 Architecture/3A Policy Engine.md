---
tags: [adaptishield, architecture, component, sublayer]
type: component
status: built
---

# 3A Policy Engine

`layer2/security_sublayer/policy_engine.py` — the **first filter** applied to
every proposed action, and the entry point of the sequential sub-layer.

## What it does

Deterministic static triage returning one of three verdicts:

| Verdict | When |
| :--- | :--- |
| `block` | matches a known malicious pattern |
| `send_to_causal` | high-impact tool (`send_email`, `write_file`, `execute_code`, `make_payment`, …) or flagged by the screener |
| `approve_direct` | low-impact, unflagged |

Owns `blocked_patterns` and `high_impact_tools`, based on a STRIDE-derived rule
set, and exposes the update interface consumed by [[3D Adaptive Threat Model]].

Smoke test: `python3 layer2/security_sublayer/policy_engine.py`

## The known defect

🔴 **`blocked_patterns` are matched against the agent's `proposed_action`**,
while 3D harvests candidate patterns from the screener's `flagged_markers`, which
describe **mediator content**. Different namespaces. Every 3D proposal so far
carries a pattern that **cannot fire** — see [[Inert Blocked Patterns]].

## Its role in the argument

3A is the **static baseline**. The whole comparative question —
[[Research Question]] #2 — is whether [[3B Causal Analyzer]] detects anything 3A
cannot. That question is currently **unmeasured in either direction** because the
benchmark built to answer it could not →
[[Phase 7 Benchmark Withdrawn]].
