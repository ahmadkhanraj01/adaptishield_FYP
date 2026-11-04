---
tags: [adaptishield, log]
type: log
date: 2026-07-20
---

# Entry X — From Architecture to Working Prototype

**20 July 2026** · Volume I

The transition from specification to running code. Layers 0–4, the sub-layer
3A–3D, and the [[Red Team Module]] are all operational on the local machine.

## What was built

- **Full pipeline** (`adaptishield_pipeline.py`) → [[Request Flow]]
- **Layer 0** — SHA-256 signature binding, rug-pull detection, allowlist
- **Layer 1** — provenance tagging + trusted/mediator partition, with a
  **context-reset guarantee** so state does not leak across requests
- **Layer 3** — screener with LLM **and** deterministic keyword backstop
- **Layer 4** — four independent gates; sandbox executes only when permission
  *and* egress both pass
- **3A–3D** → [[Layer 2 — Agent Control Plane]]

## The model-choice finding

`qwen2.5:3b` refuses injected instructions so completely — **even under the
hypothetical masked probe** — that no causal divergence is observable and there
is **no detection signal**. `gemma3:4b` complies, producing genuine
mediator-driven divergence.

Hence the deliberate **per-component assignment** rather than a global swap →
[[Models in Use]].

## The principal empirical finding — and the project's pivot

The first autonomous campaign: **2 of 4 families caught by 3B**, 2 only by the
static egress filter. When the Optimizer applied **keyword-softening
paraphrases**, causal detection **collapsed from 2/4 to 0/4** — every softened
attack evaded 3B.

**[[ASR]] remained 0% only because the egress filter caught the exfiltration as a
backstop.** The first instance of [[Backstops Mask Progress]].

> A fixed-threshold causal detector **does not generalize to paraphrased
> injections** — precisely the failure mode the adaptive layer was designed to
> close.

3D, fed the labelled outcomes, produced a negative mean reward and proposed
lowering the IE threshold while recovering the softened phrasing that had evaded
detection — *"confirming the closed adaptive loop behaves as intended."*

**That confirmation was wrong**, and the next entry says so.

## Validated end to end

A true positive (injection → takeover → sanitised → independently blocked at L4),
a true negative (benign high-impact email), and a benign low-impact case executed
in a real isolated container.

Next: [[Entry XI — The Adaptive-Loop Negative Result]].
