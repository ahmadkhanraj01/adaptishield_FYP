---
tags: [adaptishield, metric]
type: metric
---

# ASR

**Attack Success Rate** — the fraction of adversarial trials in which the injected
objective is **fully executed end-to-end**. Lower is better.

Specified in the original proposal ([[Entry I — Research Proposal]]) and never
changed.

## Why it is nearly useless as a *detection* metric here

[[Layer 4 — Sandbox and Isolation]]'s egress allowlist gates independently of
every detection layer, so it catches address-carrying exfiltration **regardless of
whether any detector noticed**. ASR was 0% before *and* after every
[[3B Causal Analyzer]] fix.

> 🟡 **Judge detection by the layer under test (`caught_by_causal`), not by the
> end-to-end ASR the backstop guarantees.** → [[Backstops Mask Progress]]

This has bitten the project **twice** — [[6n — A Corpus That Can Fail]] and
[[Phase 7 Benchmark Withdrawn]].

## Where ASR *is* meaningful

On [[Address-Free Attacks]], which carry the **legitimate** destination
deliberately, so the allowlist passes them. A campaign showing **non-zero ASR on
address-free cases is expected behaviour, not a regression** — Layer 4 is not a
backstop there.

## Reporting

Aggregating the residual failures into a single ASR figure **conceals what is
actually broken**. Report the decomposition instead →
[[Residual Misses Decomposed]].

Companions: [[FPR]] · [[WCR]] · [[Wilson Score Interval]].
