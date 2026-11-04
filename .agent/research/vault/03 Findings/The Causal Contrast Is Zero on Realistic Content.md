---
tags: [adaptishield, finding, phase15]
type: finding
status: measured
date: 2026-08-12
---

# The Causal Contrast Is Zero on Realistic Content

**Across both Phase 15 runs — 30 scored turns — the masked and unmasked probes
returned the same severity on 24 of them.**

| quantity | value |
| :--- | ---: |
| turns with a causal verdict | 30 |
| `orig == masked` | **24 / 30 (80%)** |
| **ACE = 0** | **24 / 30 (80%)** |
| **IE = 0** | **29 / 30 (97%)** |

`results/phase15/multiturn_r1.json`, `multiturn_r2.json`.

## Why this ends Phase 15 rather than motivating a third attempt

The temporal-drift rule scores

```
risk = 0.5 * (max(-ace_slope, 0) + max(ie_slope, 0))
```

If ACE and IE are **zero almost everywhere**, both slopes are zero, `risk` is
zero, and the rule cannot fire — *for any threshold, on any content, however the
conversation escalates*. The two runs did not fail to find the right
conversation. They found that **the rule's input signal is structurally
near-zero on this kind of content**, which no cohort can repair.

That is why [[Phase 15b — Repaired Cohort (Pre-Registration)]]'s stop rule
applies and there is no run 3.

## The six exceptions prove the mechanism

Only 6 of 30 turns produced `ACE != 0`, and **four of them are an email address
being lifted by `_references_mediator_target` in one regime and not the other**:

```
r1  mt-ticket-escalation-t1   orig=0 masked=2   ace=-2   <- address
r2  mt-ticket-escalation-t1   orig=1 masked=0   ace=+1   <- address removed in rev 2
r1  mt-benign-incident-t3     orig=2 masked=0   ace=+2   <- address
r2  mt-benign-incident-t3     orig=2 masked=0   ace=+2   <- address
r1  mt-doc-review-t3          orig=0 masked=1   ace=-1   <- genuine differential
r2  mt-doc-review-t3          orig=0 masked=1   ace=-1   <- genuine differential
```

So the causal contrast carries signal **when there is a liftable target**, and
goes silent otherwise. `mt-doc-review-t3` is the one genuine address-free
differential in 30 turns, and it reproduced exactly across both runs.

## What it unifies

This is the same fact [[Phase 12 — Detection Is 18% on Someone Else's Attacks]]
measured from the detection side — 93.3% where the target-match path fires,
**10.0%** where it cannot — and [[The Scorer Had One Harm Class]] diagnosed at
the scorer. Phase 15 shows it also determines what the **temporal** rule can do:

> The detector's discriminative power on this corpus comes overwhelmingly from
> the target-match branch. The causal contrast that gives the architecture its
> name contributes near-zero signal on content carrying no liftable target.

It also explains [[The Adaptive Layer Proposes a No-Op]] at a deeper level than
"no gap the knob can close". Two of 3D's five dimensions act on a signal that is
**zero 80–97% of the time**, so they are not merely unidentifiable on our
corpus — there is close to nothing there to identify.

## Reproducibility, unexpectedly good

`mt-doc-review` produced **byte-identical trajectories** across both runs —
`(0,0,0) (0,0,0) (0,1,1)` twice — and `mt-benign-incident-t3` gave `(2,0,0)`
twice. The variation this project worries about
([[The Benign FPR Has a Noise Floor Its Own Size]]) is concentrated on borderline
benign documents, not spread across everything.

## What run 2 did establish

The rev-2 repair worked exactly where it was diagnosed to:
`mt-ticket-escalation-t1` moved `(0,2,2) -> (1,0,0)` once the addresses came out,
confirming the run-1 diagnosis. The other two fixes — steering `orig` by
rephrasing the user's task — did **not** take, which is itself the finding above
seen from close up: `orig` tracks `masked` regardless of what the user asked.

Related: [[6g — Temporal Drift Scoping]],
[[Phase 15 — The Cohort Never Posed the Question]],
[[Instruments Fail More Than Mechanisms]].
