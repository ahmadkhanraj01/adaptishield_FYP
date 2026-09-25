---
tags: [adaptishield, phase, preregistration]
type: phase
status: pre-registered
date: 2026-08-12
---

# Phase 15b — Repaired Cohort (Pre-Registration)

**🔴 WRITTEN AFTER SEEING RUN 1'S TRAJECTORIES. That is the material difference
from [[Phase 15 — Multi-Turn Sessions (Pre-Registration)]] and it is stated here
first, because a reader cannot verify it from outside.** Run 1 is committed at
`bea87c7`, its result is reported in
[[Phase 15 — The Cohort Never Posed the Question]], and it is **not replaced** —
both runs appear in the paper.

## Why a repair is legitimate here

[[Phase 7 Benchmark Withdrawn]] is the precedent: that result was withdrawn
because the egress allowlist intercepted six of eight vectors, making every arm
equal **by construction**. `mt-ticket-escalation` failed the same way — it was
caught at turn 1 by the standalone rule, so the drift rule was never reachable on
that session no matter how the mechanism behaves.

The narrower argument: **the target trajectories were pre-registered before run 1
and are NOT changing.** What changes is content that failed to elicit them. Moving
content toward a target declared in advance is repairing an instrument; moving a
*target* toward an observed outcome would be fitting, and no target below has
moved.

## Why it might not be legitimate, stated plainly

Three sessions were observed and three are being edited. A reviewer cannot
confirm from outside that the edits were driven by the pre-declared targets
rather than by the direction of the miss — especially `mt-doc-review`, which
missed the threshold by one grid step. The mitigations are that the targets are
unchanged, run 1 is published alongside, and the criteria below are identical to
run 1's. That is the strongest available guarantee and it is weaker than run 1's.

## Criteria — UNCHANGED from Phase 15

| | Criterion | Reported as |
| :--- | :--- | :--- |
| **Primary** | ≥1 drift-only catch on the malicious sessions | count + Wilson CI |
| **Secondary** | trainer reward non-flat in `risk_threshold` / `window_size` | the reward table |
| **Guard** | drift-only false positives on the benign sessions | own rate, never pooled |

## What is being changed, and what is not

**Changed — the three malicious sessions' content only:**

1. **All email addresses removed.** Run 1's turn-1 ticket queue carried real
   addresses, `_references_mediator_target` fired, and masked went straight to 2.
   The sharpest rule in the system was triggered by a turn designed to be quiet.
2. **Turn-1 user tasks now explicitly invite a diagnostic action**, so the `orig`
   regime returns an action carrying a `diag_kw` and scores 1. Run 1's
   `mt-ci-pipeline` scored `orig=0` at turn 1, so ACE started at 0 and had no
   height to fall from.
3. **Turn-3 user tasks are answerable without any diagnostic verb** (a count, a
   date, one line), so `orig` reads 0 while the masked regime follows the
   escalated instruction. This is the only turn `mt-doc-review` already got right.

Together these restore the declared fall from `ace = +1` to `ace = -1`, which is
`risk = 1.0` against `risk_threshold = 0.6`. Run 1's best session reached
`risk = 0.5`.

**Explicitly NOT changed:**

- every target trajectory
- the criteria, the thresholds, `window_size`, `risk_threshold`
- **the benign control sessions** — they passed the guard 0/2 and editing a
  control after it passed is the fitting risk with none of the justification
- any shipped component

## The result that already stands, whatever run 2 does

`_references_mediator_target` **dominates the severity scale**: an address puts a
turn at 2, its absence tends to put it at 0, and the severity-1 band the drift
rule needs is narrow between two behaviours the scorer treats as binary. Run 1
established that, [[Phase 12 — Detection Is 18% on Someone Else's Attacks]]
established the same fact from the detection side, and run 2 cannot unmake it.

🔴 **If run 2 fires, that finding is what bounds the claim** — the mechanism works
on a conversation engineered to hold severities inside a narrow band, which is a
much weaker statement than "the adaptive layer detects slow-burn attacks", and
the paper must make the weaker one.

## Order of operations

1. This note and the repaired cohort **committed**.
2. Run 1's artifact preserved as `results/phase15/multiturn_r1.json`.
3. **Only then** run, writing to `multiturn_r2.json`.
4. Both runs reported. Run 2 does not replace run 1 in any table.

## If run 2 also fails to pose the question

**Stop.** A third attempt would be indistinguishable from tuning until it fires,
and the honest write-up at that point is run 1 and run 2 together as evidence
that the severity-1 band is too narrow to engineer into reliably — which is the
same finding, arrived at from the other side.
