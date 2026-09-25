---
tags: [adaptishield, architecture, component, sublayer]
type: component
status: built
---

# 3B Causal Analyzer

`layer2/security_sublayer/causal_analyzer.py` — **the detector, and the core of
the contribution.** Current detection: **116/120 = 96.7%**, 95% CI [91.7%, 98.7%].

Fires at every tool-return boundary. Runs [[Four Probe Regimes]], computes
[[ACE IE DE]], and emits a takeover verdict per [[Takeover Rule Stack]].

## Configuration that matters

| Setting | Value | Why |
| :--- | :--- | :--- |
| model | `gemma3:4b` | It **complies** under the masked probe → measurable signal. `qwen2.5:3b` refuses so completely that no divergence is observable. See [[Models in Use]] |
| `k_samples` | 2 | IE resolution is `1/k_samples`; never drop below 2 without re-validating |
| `temperature` | 0 | Every reported quantity is a *difference*, so decoding variance enters the measurement directly |
| target match | punctuation-normalized, with a length floor | [[6m — The Single-Character Defect]] |
| keyword scoring | **grounded** | [[6p — Probe Hallucination Fixed at the Scorer]] |

## Three detection routes — and why that matters for false positives

A takeover can be reached by (1) a target lifted from the content, (2) standalone
severity, or (3) the causal contrast. **A false positive is eliminated only when
every route has been considered.** Closing one route simply routes the same case
through another — demonstrated in [[Known Bounded False Positive]].

## What it deliberately cannot do

3B has **no allowlist and should not have one**. It cannot distinguish an
authorised recipient from an attacker-controlled one; that determination belongs
to [[Layer 4 — Sandbox and Isolation]]. This bounds what any purely causal
detector at this layer can deliver → [[3B Layer 4 Boundary]].

## Its remaining failures

All 4 residual misses are `masked = 0` — **severity-function** failures, **none
threshold-reachable**. See [[Residual Misses Decomposed]].

## Its history

[[6f — Standalone Severity Rule]] · [[6g — Temporal Drift Scoping]] ·
[[6h — IE Consistency Guard]] · [[6i — Masked Probe Rewrite]] ·
[[6m — The Single-Character Defect]] · [[6p — Probe Hallucination Fixed at the Scorer]]
