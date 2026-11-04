---
tags: [adaptishield, log, current]
type: log
date: 2026-07-26
---

# Entry XV — Where a Fix Belongs

**26 July 2026, 21:30 PKT** · **Volume II, entry 1** ·
*"Where a Fix Belongs, a Benchmark That Could Not Measure What It Was Built For,
and the Human Gate in Operation"*

> *"A session with an unusual shape: almost every substantive result came from an
> attempt that failed, and the failures were more informative than the successes."*

## Sections

- **A** — the hallucination, and **the question of where a fix belongs** →
  [[6p — Probe Hallucination Fixed at the Scorer]]
- **B** — the false positive **survived, and that is the finding** →
  [[Known Bounded False Positive]]
- **C** — the trainer executed, and the hardware premise retired →
  [[6o — Phase 6 Executed on Kaggle]]
- **D** — the human gate, and what it found immediately →
  [[Inert Blocked Patterns]]
- **E** — **a benchmark that could not measure what it was built for** →
  [[Phase 7 Benchmark Withdrawn]]
- **F** — the pattern, restated → [[Instruments Fail More Than Mechanisms]]
- **G** — state, and what this does not establish

## The general principle, which cost two campaigns to learn

> **Prefer the fix whose failure mode you can bound.**
>
> A prompt that is load-bearing for detection trades one *measured* false positive
> against an unknown number of *unmeasured* false negatives — **and that trade
> cannot be evaluated from the thing you were trying to fix.**

The fix that shipped is **one layer down**, in the severity function, where the
check is **monotone**: it can only ever withhold an escalation, never create one.
Its failure mode is bounded and its effect is covered by unit tests rather than a
90-minute campaign.

## State at the close

Detection **116/120**, 4 residual failures, **none threshold-reachable**. FPR
**3.3%** against externally-authored benign content. **135 deterministic tests**
requiring no language model, no network and no accelerator. → [[Current Numbers]]

## What this entry does not establish

> Whether the causal sub-layer detects attacks that static defenses miss remains
> **untested in either direction**, because the only benchmark built to answer it
> could not. **We do not claim the answer is negative; we claim we have not yet
> measured it.**

The [[WCR]] result survives as a mechanism claim but came from the same flawed run
and should be re-derived. And the benchmark's FPR column rests on **a single
benign vector** — the very weakness [[6n — A Corpus That Can Fail]] spent an entire
section correcting.

Previous: [[Entry XIV — The Human Gate]] · Next task:
[[Next Task — Repair the Phase 7 Benchmark]].
