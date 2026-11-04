---
tags: [adaptishield, architecture, layer]
type: component
status: built
---

# Layer 3 — Tool Execution Plane

APIs, databases and file systems — plus the **Tool Response Screener**, which
closes a gap the original architecture left open: tool responses flowed directly
back into agent context with no intermediate screening, creating an undefended
channel for [[Indirect Prompt Injection]].

[[AgentSentry]] establishes that this is the **highest-ASR delivery channel**
against undefended agents.

## Tool Response Screener

`layer3/tool_response_screener.py`

- Runs each tool response through **two independent checks**: an LLM-based
  semantic scanner and a **deterministic keyword backstop**
- Flags if **either** fires
- **Flagged responses are not blocked** — they are tagged and routed to
  [[3B Causal Analyzer]] for boundary-level evaluation, preserving workflow
  continuity

## Why the keyword backstop is permanent

Small local models sometimes write a **correct diagnosis in prose while emitting
the wrong structured verdict**. The backstop is not redundancy for its own sake;
it covers a specific, observed failure of structured output. Pinned in
[[Rules and Invariants]].

## Also provides

`ScreenResult.permissive()` — the no-screening path used by the `undefended` and
`static_only` arms in [[Phase 7 — Eight-Vector Benchmark]].

## A namespace hazard that came from here

The screener's `matched_markers` describe **untrusted mediator content**.
[[3A Policy Engine]]'s `blocked_patterns` are matched against the agent's
**proposed action**. [[3D Adaptive Threat Model]] harvests the former into the
latter — which is why every proposal it has produced carries an inert rule.
See [[Inert Blocked Patterns]].
