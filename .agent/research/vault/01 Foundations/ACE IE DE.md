---
tags: [adaptishield, concept, method, metric]
type: concept
---

# ACE IE DE

The three causal quantities [[3B Causal Analyzer]] computes from
[[Four Probe Regimes]]. Each regime is sampled `k_samples` times (default 2) and
scored `{0, 1, 2}` by the severity function.

| Quantity | Definition | Reads |
| :--- | :--- | :--- |
| **ACE** — Average Causal Effect | `orig − masked` | contribution of the user channel |
| **IE** — Indirect Effect | `masked − masked_sanitized` | **how much sanitisation reduced compliance** |
| **DE** — Direct Effect | `orig_sanitized − masked_sanitized` | task behaviour after sanitisation |

**IE is the detector's primary signal.**

## Resolution

IE is quantized to `1/k_samples` — 0.5 at k=2. This is not a detail; it produced
one of the four corrective fixes:

> **A tuning step finer than the metric's resolution is a provable no-op.**

A proposed threshold move of 0.5 → 0.4 could not, in principle, change any
verdict. [[3D Adaptive Threat Model]]'s `threshold_step` is therefore pinned to
`CausalAnalyzer.ie_resolution` — see [[Fixes A-D]] (fix C).

## The caveat added in 6m and corrected in 6n

At `temperature = 0` the `k_samples` are otherwise identical, so the consistency
requirement reduces to a comparison of means and the IE grid coarsens to whole
numbers. `k_samples = 2` is retained only for schema comparability.

But **greedy decoding is not literally deterministic**: across a full campaign
**2 of 564** regime severities were non-integral — the two samples disagreed
about 0.35% of the time, concentrated on long unstructured benign documents.
The property is stated as measured, not as absolute. See
[[6n — A Corpus That Can Fail]].

## Failure mode

IE **silently inverts when [[3C Context Sanitizer]] fails**: both regimes comply,
the scores cancel to `IE = 0`, and an attack that *survived* sanitisation reads as
*safe*. That is what [[Takeover Rule Stack]] rule 2 is for.
