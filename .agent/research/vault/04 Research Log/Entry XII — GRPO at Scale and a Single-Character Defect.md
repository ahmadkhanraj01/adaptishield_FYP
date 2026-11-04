---
tags: [adaptishield, log]
type: log
date: 2026-07-25
---

# Entry XII — GRPO at Scale and a Single-Character Defect

**25 July 2026** · Volume I

Three things: the training pipeline completed, the negative result it returned,
and **the investigation that negative result licensed** — which found the cause of
every residual detection failure in a single character of string comparison.

## Sections

- **A** — the training pipeline and the natural-gap question →
  [[6l — No Natural Gap at Scale]]
- **B** — the diagnostic instrument, and the cross-tabulation that constrained the
  hypothesis before it ran
- **C** — the defect: a hyphen, in 57 of 57 mentions
- **D** — three corrections
- **E** — result: **99/114 → 114/114**
- **F** — what it does not establish
- **G** — consequent work

Full detail: [[6m — The Single-Character Defect]].

## The methodological point of the entry

> *Rather than act on that conclusion by intuition, we built a read-only
> diagnostic.*

A quantified negative ("the reward is flat across the entire grid") **licensed**
looking one layer down. An unquantified hunch would not have. This is the
strongest argument in the project for measuring a negative precisely rather than
recording it as a disappointment.

## The turn at the end

The binding constraint **moved from detection to evaluation**:

> Complete detection coverage had been measured against a **false-positive test
> that cannot fail**, and no case existed which the causal contrast detected and
> a simpler severity rule did not. **Until both are fixed, the corpus is at its
> ceiling and cannot discriminate between defensive configurations — including
> whether any subsequent change is an improvement or a regression.**

That paragraph is what makes [[Entry XIII — A Corpus That Can Fail]] necessary.

Previous: [[Entry XI — The Adaptive-Loop Negative Result]].
