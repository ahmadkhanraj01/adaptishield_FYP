---
tags: [adaptishield, finding, principal]
type: finding
---

# Reward-Decreasing Proposals

**An RL policy proposed a security change that its own reward function scored
lower. Four times.** Recorded as a **finding**, not as a bug fix — it is the most
direct empirical support [[Layer 5 — Human in the Loop]] has received.

## The occurrences

| # | Proposed vs incumbent | Context |
| :--- | :--- | :--- |
| 1 | **+0.8683 vs +0.8688** | Scalar IE threshold, 0.5 → 0.0 |
| 2 | — | Joint space; caught by the **minimality pass**, which found the bundled threshold move contributed nothing while a marker weight carried the whole gain |
| 3 | **+0.8329 vs +0.8330** | Live data, fired unprompted |
| 4 | **+0.8329 vs +0.8330** | [[6o — Phase 6 Executed on Kaggle]] — **different hardware, different RNG** |

In occurrence 1, **nothing in the loop compared the proposal against the
incumbent before accepting it**, and `apply_update` would have taken the change
silently. *The policy's confidence was, in effect, the decision rule.*

## Why it happens

On the corpus, three candidate thresholds were **tied on reward**; sampling
variation across groups was ~1 part in 100, and the minimal-intervention term
meant to separate them was ~1 part in 1000. The noise was two orders of magnitude
larger than the signal it was meant to break ties with.

> The generalisation is **not** that a particular implementation contained an
> error. It is that **a policy-gradient method optimising a proxy reward over a
> small batch will confidently and repeatedly propose modifications to a security
> control that its own objective scores as regressions** — because *sampling
> variation within the policy is not the same object as the reward the policy is
> meant to track*.
>
> **An automatic application loop without a verification step degrades the
> control it is tuning.**

## Three corrections

1. **1-D:** the grid is 5 points and therefore enumerable, so the decision is
   taken directly from the **exact reward table**. Retained as a regression guard
   for the scalar case **only** — explicitly *not* the decision rule in the joint
   space, whose non-enumerability is the entire reason for adopting it.
2. **Joint space:** the policy **proposes**, the trainer **verifies**, accepting
   only when reward **strictly exceeds** the incumbent.
3. **Minimality pass:** each altered dimension is reverted independently and the
   reversion retained wherever reward does not fall.

## Corroborating evidence from a different direction

In [[6o — Phase 6 Executed on Kaggle]] the torch and pure-Python policies selected
**different preferred actions** and produced the **same final proposal** — the
stochastic search diverged while deterministic verification converged. A learned
policy's preference is **not stable across random seeds, let alone across
implementations**, so it cannot be the decision rule.

## Why the human gate is load-bearing

This is the concrete reason [[Layer 5 — Human in the Loop]] recomputes rather than
trusts, and recommends rather than decides.

## What this does not establish

That verification is sufficient. Every one of these guards reasons about
**reward** — and is therefore blind to [[Inert Blocked Patterns]] and to
[[6n — A Corpus That Can Fail]].
