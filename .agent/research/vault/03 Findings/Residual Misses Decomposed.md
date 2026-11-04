---
tags: [adaptishield, finding]
type: finding
---

# Residual Misses Decomposed

**4 of 120 malicious cases remain undetected.** Reporting them as an aggregate
[[ASR]] would conceal what is actually broken.

## The decomposition

| Failure kind | Count | Mechanism |
| :--- | :--- | :--- |
| **Severity function** | **4** | `masked = 0`. The probe rephrased the action into wording the keyword scorer does not match, and with **no address in the content** the target rule cannot fire either. **No signal exists for any threshold to act on.** |
| Sanitizer | (1, at the 5-miss point) | The analyzer's internal sanitizer did not remove the material that was scoring, so masked and sanitized severities coincide and the contrast collapses |
| **Threshold** | **0** | — |

All are [[Address-Free Attacks]] carrying the **legitimate** destination, so the
egress allowlist cannot mask them → [[Backstops Mask Progress]]. All exhibit
`IE = 0` with inconsistent separation across samples.

## Why the empty threshold column is the substantive point

> It is a **quantified statement** of why the knob [[3D Adaptive Threat Model]]
> controls cannot close this gap — and consequently why the honest output of the
> adaptive layer is a **no-operation** rather than a tuned improvement.

The remaining work lies in the **severity function** ([[3B Causal Analyzer]]) and
the **sanitizer** ([[3C Context Sanitizer]]) — **not in the adaptive layer at
all.** → [[The Adaptive Layer Proposes a No-Op]]

## A structural note

All of them fall **outside** the join used in the IE-redundancy analysis, for the
same reason discussed there: [[3C Context Sanitizer]] never executed on them,
because 3C is gated on the takeover they failed to trigger →
[[6n — A Corpus That Can Fail]] §A.

## The repair is not obvious

The natural move is a better scorer. [[6e — Semantic Scoring Ablation]] already
showed the semantic scorer is **worse end-to-end**, so this needs a **third
approach**, not a re-run of that one → [[Backlog]].

## What this does not establish

That 4 is a stable figure. It is one campaign's residual at
`temperature = 0` — where 2 of 564 regime severities were still non-integral, so
the boundary cases are not perfectly reproducible → [[ACE IE DE]].
