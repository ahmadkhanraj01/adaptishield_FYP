---
tags: [adaptishield, finding, lesson]
type: finding
---

# Design Lessons

The transferable ones — each paid for by a measured failure.

## On measurement

**Component accuracy ≠ contrast accuracy.**
Making `_score_action` more accurate per action made the *system* worse. IE is a
difference; scoring both regimes correctly cancelled the gap the detector reads.
**Optimize the contrast, not the component.** → [[6e — Semantic Scoring Ablation]]

**A difference metric can invert.**
Any detector built on "A minus B" must be paired with a **standalone-evidence
rule** for the case where A and B move together. → [[6f — Standalone Severity Rule]]

**Resolution before tuning.**
Never tune a knob finer than the metric it moves can resolve. **Fix the
measurement before training a policy on it.** → [[Fixes A-D]] (C)

**Measurement wording drives signal.**
The largest detection gain in the project came from rewriting a *prompt*, with no
scorer or threshold change. → [[6i — Masked Probe Rewrite]]

**Single-run metrics are partly luck.**
FPR has been observed flapping 0% ↔ 25% on identical inputs. **Report
distributions over repeated runs, not one figure.** → [[Wilson Score Interval]]

## On evaluation

**Backstops mask progress.**
Judge detection by the layer under test, not by the end-to-end metric a lower
layer guarantees. → [[Backstops Mask Progress]]

**A defense measured only against a corpus its author wrote measures the author's
imagination.** → [[6n — A Corpus That Can Fail]]

**A point estimate off 8 samples is not a rate.** → [[Wilson Score Interval]]

## On fixing things

**Prefer the fix whose failure mode you can bound.**
A **monotone** check in the severity function can only ever *withhold* an
escalation — so it is covered by unit tests. A prompt load-bearing for detection
trades one *measured* false positive against an unknown number of *unmeasured*
false negatives. → [[6p — Probe Hallucination Fixed at the Scorer]]

**A false positive is eliminated only when every route has been considered.**
Closing one route to a verdict routes the same case through another. →
[[Known Bounded False Positive]]

**Change one thing per campaign.** A run that changes code *and* backend cannot
attribute a regression. → [[Traps]]

## On automation

**Code that reports an untested verdict is more hazardous than code that fails.**
→ [[Instruments Fail More Than Mechanisms]]

**A policy's preference is not a decision rule.** It is not stable across random
seeds, let alone across implementations. → [[Reward-Decreasing Proposals]]

**Reward-based guards are blind to inert rules**, because an inert rule changes
reward by exactly nothing. → [[Inert Blocked Patterns]]

**A more-refusing model makes a worse detector.** → [[Models in Use]]

## On reporting

**A measured negative beats an unmeasured positive.** →
[[The Adaptive Layer Proposes a No-Op]]

**State what a result does not establish.** Every finding note here ends that way,
and it is the single habit that has caught the most overclaiming.
