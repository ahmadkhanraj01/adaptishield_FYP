---
tags: [adaptishield, metric, method]
type: metric
---

# Wilson Score Interval

**All rates in this project are reported with Wilson score intervals**, never the
normal approximation.

## Why

At n = 60 with a proportion near zero, the normal approximation **extends below
zero and its coverage collapses exactly where our numbers sit.** Using it would
produce intervals that are both impossible and wrong in the same place.

## The rule this enforces

> **A point estimate off 8 samples is not a rate.**

The interval on **4/8** spans **[21.5%, 78.5%]** — nearly the entire usable range.
That is why the 8 hand-written benign controls are reported as a **diagnostic that
located an architectural boundary**, and **never pooled** into a headline figure →
[[FPR]].

## Where it settles arguments

[[Known Bounded False Positive]]: closing the surviving route would move
**2/60 → 1/60** — a difference lying well inside an interval spanning roughly
[0.9%, 11.4%]. **That is not a measurable improvement at this sample size**, so
the trade (weakening the mechanism that catches 14 attacks) is not worth making.

The interval is what converts "should we fix this?" from a matter of taste into a
matter of arithmetic.

## Current intervals

| Quantity | Estimate | 95% Wilson CI |
| :--- | :--- | :--- |
| Detection | 116/120 = 96.7% | [91.7%, 98.7%] |
| FPR (external, n=60) | 3.3% | [0.9%, 11.4%] |

Implemented in `evaluation/fpr_report.py`. Tested by `tests/test_corpus.py`.

> **The width of the reported interval is the honest part of the figure rather
> than an embarrassment to it.**
