---
tags: [adaptishield, component]
type: component
date: 2026-08-08
---

# Per-Layer Attribution

`evaluation/attribution.py`. Given an `ExecutionResult`, name **which gate stopped
it** — and which later gates would also have stopped it.

## Why it exists

[[ASR]] is one bit, and one bit cannot distinguish *"3B caught it"* from *"the
allowlist caught it"*. [[Phase 7 Benchmark Withdrawn]] is what that costs: a
benchmark reporting only that bit produced a headline finding about its own
construction, and the invalidation had to be discovered by hand afterwards by
reading `egress_allowed=False` off every row.

Correcting the corpus stops the backstop from absorbing everything. Attribution
fixes the **instrument**, so the next time a backstop conceals a result the report
says so instead of leaving it to be noticed. → [[Backstops Mask Progress]]

## The contract

```
stopped_by       first gate in PIPELINE ORDER that refused
redundant_gates  the later gates that would ALSO have refused
reached_tool     nothing refused
```

Order follows `AdaptiShieldPipeline.process_request` exactly:

| Order | Gate | Detection? |
| :--- | :--- | :--- |
| 1 | `3A_block` — static pattern block | yes (but not novel — a `static_only` arm has it) |
| 2 | `3B_takeover` — causal takeover | **yes, and the novel one** |
| 3 | `L4_permission` — scope check | no |
| 4 | `L4_egress` — allowlist | no |
| — | `none` | reached the tool |

`backstop_share` = of the malicious cases a **detection** layer stopped, the
fraction a **static** gate would also have stopped. **1.0 means the detection
result is entirely concealed** — the condition that invalidated the first Phase 7
run. It returns `None` rather than 0 when no detection stop occurred, because a
share of nothing is not 0% and would read as good news.

## Two subtleties that are easy to get wrong

**3B before 3A, when reading a `blocked` status.** With 3C disabled, a *confirmed
takeover* surfaces as `final_status == "blocked"` — and
`ExecutionResult.causal_takeover` is inferred from `final_status`, so it reports
`None` there. Attributing that to 3A would credit the static layer with the causal
layer's work. Attribution consults the **verdict itself**, not the inference.

**A refused request must never read as `reached_tool`.** The first implementation
credited 3A only when no causal verdict existed, so `blocked` with a non-takeover
verdict fell through to `none` with `reached_tool=True` — a miscount in the
direction of "the attack succeeded". Unreachable in today's pipeline; pinned by a
test anyway, because that is the direction an evaluation cannot afford to be wrong
in latently.

## What it does not do

It reads the pipeline's own control flow, so it is **only as honest as that flow**.
It attributes the *first* gate that refused, **not a counterfactual** — it cannot
say what a disabled layer would have done. That is what the ablation arms are for,
and `redundant_gates` is the cheap approximation in between.

## Where it is used

[[Phase 7 — Eight-Vector Benchmark]] → [[Phase 7 Repaired — The Causal Sub-Layer's Marginal Detection]]. It found two defects on first use: **V7 could never fail the
permission check it existed to test**, and the `reached_tool` miscount above. →
[[Instruments Fail More Than Mechanisms]]

Phase 11's per-component ablations should reuse it rather than re-deriving
attribution per arm — the whole point is that every arm is scored by one function.
