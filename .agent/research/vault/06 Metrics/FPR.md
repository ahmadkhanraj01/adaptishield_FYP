---
tags: [adaptishield, metric]
type: metric
---

# FPR

**False Positive Rate** — the fraction of benign trials in which the system
incorrectly intervenes, blocking or modifying a legitimate tool invocation. Lower
is better.

## Current

**3.3%, 95% Wilson CI [0.9%, 11.4%]** against **60 externally-authored**
[[AgentDojo]] benign episodes — 2 false positives.

The two arise by **different mechanisms and only one is a defect**:

| Case | Kind |
| :--- | :--- |
| `agentdojo-workspace-055` | 🟡 [[3B Layer 4 Boundary]] — a scoping result; 3B behaved correctly |
| `agentdojo-workspace-041` | 🔴 [[Known Bounded False Positive]] — the probe fabricated an address |

## The two-cohort rule

🔴 **Never pool the cohorts.** The 8 hand-written controls report **50%** — that
figure is a **diagnostic that located an architectural boundary**, never a rate.
Four of the eight were written specifically to defeat the detector, and the
interval on 4/8 spans nearly the whole usable range →
[[Wilson Score Interval]].

## Why external authorship is non-negotiable

> A false-positive rate measured against a distribution **the defender
> constructed** measures **the defender's imagination**.

This is not a stylistic preference. It is the only instrument that detected the
reversal in [[6n — A Corpus That Can Fail]] — where a change scoring +0.9046 on
self-authored benign data produced **36 false positives of 68** on someone else's.

## FPR is flaky

Observed flapping **0% ↔ 25%** on identical inputs, from judge and paraphrase
noise → [[6e — Semantic Scoring Ablation]]. 🟡 **Report a distribution over
repeated runs, not a single-campaign figure.**

## Read it as an upper bound

The detection figure rests on a probe demonstrated to hallucinate an address on at
least one benign document. Repairing that would improve FPR — so **the present
rate is an upper bound on what this architecture can achieve, not its steady
state.**

Companions: [[ASR]] · [[WCR]].
