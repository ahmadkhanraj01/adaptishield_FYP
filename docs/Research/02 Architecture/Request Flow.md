---
tags: [adaptishield, architecture]
type: architecture
---

# Request Flow

`process_request(user_input, mediator_content, tool_name, command, session_id)`

```
  │
  ├─ L1  provenance tagging (trusted vs mediator partition, per session_id)
  ├─ L3  Tool Response Screener  → flagged? (LLM OR keyword backstop)
  ├─ 3A  Policy Engine           → approve_direct | send_to_causal | block
  │        └─ if high-impact / flagged → send_to_causal
  ├─ 3B  Causal Analyzer.evaluate_boundary(...) → Takeover? (per-session history)
  │        └─ if Takeover → 3C
  ├─ 3C  Context Sanitizer       → safe_continuation (injection stripped)
  ├─ L4  permission → egress → sandbox  (each gates independently of 3A/3B/3C)
  └─ Telemetry → logs/episode_records/episodes.jsonl  (Episode Record)
```

## Final statuses

`approved_direct` · `approved_causal` · `safe_continuation` · `blocked`

## Two gates worth naming explicitly

1. **3C is gated on takeover.** The early return on the negative branch precedes
   the sanitizer call by fifteen lines in `adaptishield_pipeline.py`. This is why
   3C's `instructions_removed` self-report **cannot substitute** for
   [[ACE IE DE]] — the signal comes into existence only *after* the decision it
   would have to replace. Established in [[6n — A Corpus That Can Fail]].

2. **The sandbox is gated on both permission and egress.** It executes only when
   *both* pass, which preserves defense-in-depth: a command approved upstream is
   independently re-gated at execution time.

## Ablation arms

`PipelineConfig` implements the arms **inside** the pipeline rather than in the
runner, so every arm shares one code path and differs only in flags:
`undefended` · `static_only` · `full` · `no_egress`. See
[[Phase 7 — Eight-Vector Benchmark]].

Structure: [[Defensive Stack]].
