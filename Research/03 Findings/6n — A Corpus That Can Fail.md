---
tags: [adaptishield, finding, negative, principal]
type: finding
date: 2026-07-26
---

# 6n — A Corpus That Can Fail

**The principal negative result of the project.**

> The single improvement the adaptive layer ever discovered — verified by every
> safeguard built into it — was an **artifact of a benign corpus we had written
> ourselves**, and it reversed on contact with benign data authored by someone
> else.

## What was added, and why each was necessary

**18 [[Address-Free Attacks]].** Every family had embedded the exfil address
inside its directive, so removing the directive removed the address and IE
tracked severity *as arithmetic rather than mechanism*. The new attacks name **no
recipient at all** and carry the **legitimate** destination deliberately, so the
Layer 4 allowlist passes them and cannot conceal a failure of the earlier layers.
That is the only construction under which a 3A/3B failure becomes visible in the
outcome → [[Backstops Mask Progress]].

**60 externally-authored benign episodes** from [[AgentDojo]]. A false-positive
rate over 8 hand-written controls is **not a rate** — the Wilson interval on 4/8
spans ~22–79%, nearly the entire usable range, and 4 of those 8 were written
specifically to defeat the detector. More fundamentally, *a rate measured against
a distribution the defender constructed measures the defender's imagination*.

## A — Is the causal measurement redundant with 3C's self-report?

**No, and the reason is structural rather than statistical.** The pipeline
invokes [[3C Context Sanitizer]] **only after** takeover is declared — the early
return precedes the sanitizer call by 15 lines. The self-report is generated
**downstream of the very decision it would have to replace.**

> A signal that comes into existence only after one has decided cannot be the
> thing with which one decides.

Confirmed empirically: the set of episodes carrying a sanitisation decision is
**identical, element for element**, to the takeover set.

**And a methodological correction we are obliged to state, because we initially
failed to state it.** Any contingency table over these two quantities is
**conditioned on the outcome** — a selection effect, not a sample. A previous
comparison scoring IE against the self-report "as competing detectors" was
**invalid irrespective of its arithmetic** (and its arithmetic was also wrong in
the FP column). Retained only as a description of how they relate *among
detections*, where both off-diagonals are substantial: on 30 episodes behaviour
changed while the sanitizer reported nothing; on 14 the sanitizer believed it had
deleted an instruction whose deletion moved the probe not at all. *That is the
signature of a self-report and a measurement, not of one quantity computed twice.*

## B — Does the causal mechanism earn its cost?

**Yes — for the first time.** With address-free attacks in place, **13 of 115**
malicious takeovers are caught by `IE ≥ 1` where the standalone rule would have
missed. The previous entry reported this as **0 of 114**.

All 13 are address-free and span all 6 families — exactly the discrimination the
corpus extension was built to produce. (Now 14/116 after
[[6p — Probe Hallucination Fixed at the Scorer]].)

## C — The false-positive rate

**3.3%, 95% Wilson CI [0.9%, 11.4%]** against the 60 external episodes, at
detection 115/120 (95.8%) — the new cohort cost nothing in recall. Cohorts are
**never pooled**; the 4/8 figure is now always labelled a *diagnostic that located
an architectural boundary*, never a rate. See [[Wilson Score Interval]].

The two false positives arise by different mechanisms and **only one is a
defect** → [[3B Layer 4 Boundary]] and [[Known Bounded False Positive]].

## D — The reversal

The joint action space (5 dims / 720 actions) located and accepted a **genuine**
improvement no scalar threshold could express: weighting one screener marker,
mean reward **+0.8688 → +0.9046**, with the minimality pass correctly stripping an
accompanying threshold movement that contributed nothing. **Every safeguard
functioned as designed.**

Evaluated against the corpus containing the 60 external benign episodes, **that
identical action produces 36 false positives of 68 benign, destroys 18 workflows,
and lowers mean reward to +0.6500.** (It does close all 5 residual detection
failures.)

The mechanism is not subtle: the marker fires on **30 of 60** external benign
documents and on **0 of the 8** we wrote ourselves. Weighting it appeared costless
on a corpus in which nothing triggered it. Worse, on this data the marker is
**anti-informative** — 30/68 benign vs only 18/120 malicious.

> The improvement was real, reproducible, correctly verified against the
> incumbent, and correctly minimised. **Every guard operated properly, and none
> of them could have detected the problem, because none of them can see beyond
> the evaluation set.** The only instrument that detected it was benign data
> authored by someone with no knowledge of the system.

This is a general caution about RL applied to security controls, and it applies
with equal force to work whose reward signal is better designed than ours.

## Also established here

[[Reward-Decreasing Proposals]] (occurrences 1–3) and the residual-failure
decomposition → [[Residual Misses Decomposed]].

## What this does not establish

- 60 benign episodes from two suites of **one** benchmark are not the real world;
  the width of the interval is the honest part of the figure.
- Two of 3D's five dimensions remain unidentifiable until campaigns share a
  `session_id` → [[6g — Temporal Drift Scoping]].
- The detection figure rests on a probe demonstrated to hallucinate an address on
  at least one benign document, so **the present FPR should be read as an upper
  bound** on what this architecture can achieve, not its steady state.
- **The reversal was detected because external benign data happened to be
  available. We have no general procedure for detecting corpus artifacts, and we
  do not claim one.**
