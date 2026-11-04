---
tags: [adaptishield, finding]
type: finding
---

# 6h — IE Consistency Guard

## The bug

The IE rule compared **means**. With `k_samples = 2`, a single paraphrase-driven
sample flip was enough to manufacture a takeover verdict from noise.

## The fix

> The IE rule requires `min(masked) > max(masked_san)` — **every** masked sample
> must outscore **every** sanitized sample.

Consistent separation across samples, not just on average.

## Why it was affordable

**Only because [[6f — Standalone Severity Rule]] was already in place.**
Tightening a contrast rule turns strong-evidence attacks into false negatives
unless something else is catching them. Rule 2 carries the strong evidence; that
is what lets rule 1 be conservative.

🔴 This ordering is an invariant — see [[Takeover Rule Stack]] and
[[Rules and Invariants]]. `require_consistent_ie=False` exists **only for
ablation**.

## The caveat added later

At `temperature = 0` the samples are otherwise identical, so the consistency
requirement **reduces to a comparison of means** and the IE grid coarsens to
whole numbers. `k_samples = 2` is retained only for schema comparability.

Except it is not perfectly deterministic: **2 of 564** regime severities across a
full campaign were non-integral — the samples disagreed 0.35% of the time,
concentrated on long unstructured benign documents. See [[ACE IE DE]].

## What this does not establish

That paraphrase noise is eliminated. It is suppressed at k=2 under greedy
decoding. Reintroducing sampling diversity — which is the only way `k_samples`
does real work again — would reopen the question.
