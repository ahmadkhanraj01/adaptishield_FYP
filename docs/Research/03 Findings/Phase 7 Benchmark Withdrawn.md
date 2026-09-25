---
tags: [adaptishield, finding, withdrawn]
type: finding
status: withdrawn
date: 2026-07-26
---

# ⛔ Phase 7 Benchmark Withdrawn

**The first result of the eight-vector benchmark is withdrawn. Do not quote it.**

> **✅ SUPERSEDED (2026-08-08).** The repair is done and the benchmark has been
> re-run: → [[Phase 7 Repaired — The Causal Sub-Layer's Marginal Detection]].
> ASR `static_only` **71.4%** → `full` **14.3%**, with **18/21** stops attributed
> to 3B and **zero** detection stops in `static_only`. This note is kept, not
> deleted — the contrast between the two runs is itself a result, and the reason
> the attribution column exists.

## What was built

`evaluation/vectors.py` + `evaluation/benchmark.py`. Four configurations of the
same pipeline over a fixed vector set drawn from the published threat taxonomies
— **undefended**, **static_only**, **full**, **no_egress** — with the ablation
implemented **inside** the pipeline (`PipelineConfig`) rather than in the runner,
so the arms share one code path and differ only in flags.

It was built to answer the question the campaign cannot: not *"does the system
work"* but **"which layer is doing the work"**.

## The withdrawn result

Attack success fell from **100% undefended** to **14.3% under static defenses
alone**, and the complete system matched that figure **exactly** while raising
[[WCR]] from **0% to 71.4%**.

The apparent finding: *the causal sub-layer contributes no additional detection,
and instead contributes usability.*

## Why it is invalid

Inspecting **which component actually stopped each case**:

```
static_only — every single case:
  V1..V3, V5..V7   approved_direct   egress_allowed=False   ← the ALLOWLIST stopped it
```

**Nothing was blocked by any detection layer.** Six of eight vectors point at an
exfiltration host, so [[Layer 4 — Sandbox and Isolation]] intercepts them before
3A/3B are consulted. The `full` arm scores identically for the same reason.

> The benchmark **cannot distinguish detection layers**, because a static
> allowlist intercepts almost every vector before any detection layer is
> consulted. The two arms are **equal by construction rather than by
> measurement.**

## This is a repeat, not a new mistake

[[6n — A Corpus That Can Fail]] added [[Address-Free Attacks]] *precisely because*
the allowlist was concealing detection failures — and then a vector set was
designed in which the allowlist conceals everything.
→ [[Backstops Mask Progress]].

## The repair

→ [[Next Task — Repair the Phase 7 Benchmark]]

## What survives, and what does not

- ⛔ **Withdrawn:** the ASR comparison between `static_only` and `full`, and any
  claim about the causal sub-layer's marginal detection.
- 🟡 **Survives as a mechanism claim, but should be re-derived:** removing the
  sanitiser genuinely converts safe continuations into blanket blocks, so the
  WCR 0% → 71.4% result reflects a real effect. But it came from the same flawed
  run.
- 🔴 **Never was valid:** the FPR column rests on **a single benign vector** ×3
  repeats — the very weakness [[6n — A Corpus That Can Fail]] spent a section
  correcting for the campaign corpus.

## The open question

> **Whether the causal sub-layer detects attacks that static defenses miss is
> untested *in either direction*.** We do **not** claim the answer is negative.
> We claim we have not yet measured it.

Another entry in [[Instruments Fail More Than Mechanisms]]: a benchmark that
produced a headline result which measured its own construction.
