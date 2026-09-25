# Layer 3 — MCP Tool Execution Plane

**Status:** ✅ Tool Response Screener built, wired and ablation-ready · the
tool-execution surface itself is still simulated

## Purpose

Where tool calls execute (APIs, databases, file systems) and, critically, where
every **tool response is screened for indirect prompt injection before it is
trusted as clean context.**

The Screener deliberately **does not block**. It tags a response as flagged and
lets it flow on to the Causal Analyzer, which forces causal evaluation even on
tools 3A would otherwise fast-path as low-impact. Blocking here would destroy the
evidence 3B needs — you cannot measure how content changed behaviour if the
content never reaches the model.

## Files

| File | Purpose | Status |
| :--- | :--- | :--- |
| `tool_response_screener.py` | Two independent checks: an LLM semantic scanner **and** a deterministic keyword backstop (`KEYWORD_MARKERS`). Flagged if *either* fires. Also provides `ScreenResult.permissive()` for the Phase 7 ablation arms. | ✅ Built & wired |
| `__init__.py` | Package marker | ✅ |

## Why two independent checks

The keyword backstop exists because small local models sometimes write a correct
diagnosis *in prose* while emitting the wrong structured verdict. The LLM check
exists because a keyword list cannot see a paraphrase. Neither is reliable alone,
and their **disagreements are logged** (`checks disagreed: llm=True keyword=False`)
because that disagreement is itself informative — it usually means the phrasing
has drifted away from `KEYWORD_MARKERS`.

`ScreenResult.matched_markers` reports **every** marker that hit, not just the
first, and the pipeline forwards the full set into `EpisodeRecord`. A flagged
response with an *empty* marker list is the signal that the injection's wording
has moved beyond the keyword list entirely.

## A finding about the markers themselves

Component 3D harvests `matched_markers` as candidate `blocked_patterns` — and
**that pairing does not work**, for two reasons found in §6n/§6p:

1. **Wrong namespace.** 3A matches `blocked_patterns` against the *proposed
   action*, while markers describe *mediator content*. The string
   `'ignore previous'` appears as a marker on 48 of 188 episodes and in **0**
   proposed actions, so every pattern 3D has ever proposed is **inert**. Layer 5's
   gate now detects this.
2. **The markers are not discriminative on real content.** `'ignore previous'`
   fires on **30 of 60** externally-authored *benign* AgentDojo documents and only
   18 of 120 malicious ones — it is worse than uninformative there. This is why
   the one gain GRPO ever found (weighting that marker) reversed on external data.

Neither is a defect in the screener: as a *flagging* signal that routes content to
3B, it works. It is a defect in treating a flag as a blocking rule.

## Ablation support

`ScreenResult.permissive()` returns a real `ScreenResult` — not `None` — with
`is_flagged=False` and `source="disabled"`. Returning a real verdict matters: if
a disabled layer changed the telemetry shape, the Phase 7 arms would no longer be
comparable. Pinned in `tests/test_ablation.py`.

## What's pending

- The tool-execution surface (APIs / DBs / file systems) is simulated. Real
  command execution happens in the gated sandbox at **Layer 4**
  (`layer4/sandbox.py`), not here.
- **Screening tool *descriptions* at registration.** The pipeline consumes tool
  *responses*, not manifests, so two Phase 7 vectors (tool poisoning, rug pull)
  are modelled at the nearest boundary that exists and flagged **APPROXIMATED**
  in the benchmark. A real defense would screen the manifest when the server
  registers.

## Run standalone

```bash
python3 layer3/tool_response_screener.py   # clean vs FLAGGED test cases
```
