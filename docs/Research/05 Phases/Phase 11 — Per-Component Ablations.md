---
tags: [adaptishield, phase]
type: phase
status: done
date: 2026-08-08
---

# Phase 11 — Per-Component Ablations

**Without this, seven layers read as unjustified complexity.**
[[Phase 7 — Eight-Vector Benchmark|Phase 7]] answered *"is the whole system better
than a static one"*. It cannot answer *"is each layer pulling its weight"*, and a
journal reviewer will ask.

Unblocked by [[3B's Refusal Exposure Is Live and Unrealised]] — 3B's attributions
rest on the four regime severities, so measuring that afterwards would have meant
re-running this matrix.

## Design — a ladder, not a list of arms

Each rung adds **exactly one** component to the one below it, in **pipeline
order**, and the informative quantity is the difference between *adjacent* rungs. A
layer contributing nothing then appears as a rung with zero improvement rather than
as prose.

| Rung | Adds | Flag |
| :--- | :--- | :--- |
| `undefended` | — | nothing on |
| `screener_only` | Layer 3's tool-response screener → [[Layer 3 — Tool Execution Plane]] | `enable_screener` |
| `plus_policy` | [[3A Policy Engine]] | `enable_policy` |
| `plus_causal` | [[3B Causal Analyzer]] | `enable_causal` |
| `plus_sanitizer` | [[3C Context Sanitizer]] | `enable_sanitizer` |
| `plus_permission` | Layer 4 scope check | `enable_permission` |
| `full` | Layer 4 allowlist | `enable_egress` |

`tests/test_paired.py` asserts each step changes exactly one flag, that it only
ever turns things **on**, and that the additions come in pipeline order — built in
any other order, a layer's contribution is attributed to whichever one happened to
precede it.

### Two arms that deliberately do not exist

**No `full_plus_3d` rung.** [[3D Adaptive Threat Model]] proposes a **no-op**
(§6d / §6l / §6n), so an arm applying its proposal *is* `full` by construction.
Running it would manufacture a row whose null is arithmetic rather than empirical.
The no-op is the result → [[The Adaptive Layer Proposes a No-Op]].

**No `no_causal` leave-one-out arm.** Switching 3B off also makes 3C unreachable —
3C runs only on a confirmed takeover — so the arm would move two components at
once. That case already exists as `static_only`, where the confound is documented
instead of being hidden inside a row claiming to move one thing. For the same
reason no rung enables 3C without 3B: it would be identical to the rung below it,
which is the "equal by construction" defect that caused the withdrawal →
[[Phase 7 Benchmark Withdrawn]].

## Leave-one-out, as a robustness check

The ladder measures each layer *given only the layers below it*. Leave-one-out
measures it *given all the others*. **The two disagree exactly when layers are
redundant with each other** — and Phase 7 already found one such case: Layer 4
looked like the ASR backstop until 3B was present, at which point it added nothing.
So a disagreement here is the finding, not noise.

Arms: `no_screener`, `no_policy`, `no_sanitizer`, `no_permission`, `no_egress`,
each compared against `full`.

## The statistic

Two overlapping [[Wilson Score Interval|Wilson intervals]] are **not a test** when
both arms ran the same cases — the **discordant** pairs are the evidence.
`evaluation/paired.py` reports `helped` / `hurt` / `discordant` with an exact
binomial p-value, because these counts are single digits and the chi-square form of
McNemar is unreliable below ~25 discordant pairs.

That module exists because of [[A Published p-Value With No Committed Source]].

## Predictions, stated before the run

Stating them first is what makes the outcome evidence rather than a
rationalisation of whatever came out.

| Rung | Prediction | Basis |
| :--- | :--- | :--- |
| `plus_policy` → `plus_causal` | **large**, the paper's central claim | Phase 7: 18/21 stops by 3B |
| `screener_only` → `plus_policy` | **`helped == 0`** | Phase 7: 3A produced **zero** detection stops in every arm → [[Inert Blocked Patterns]] |
| `plus_causal` → `plus_sanitizer` | ASR flat, **[[WCR]] large** | 3C buys usability, not detection |
| `plus_permission` → `full` | **`helped == 0`** | Phase 7: `full` → `no_egress` left ASR unchanged |

**All four predictions held** → [[Phase 11 — Only Two Layers Do Anything]]. 3B's
rung is 18/0 at p = 0.000; 3A, L3 and both halves of Layer 4 are 0/0 with **zero
discordant pairs**; 3C is ASR-flat and WCR 18/0. Leave-one-out agrees on every row,
so no layer turned out to be redundant with another — which was the outcome Phase 7
had made likely.

One thing the predictions did **not** anticipate: the report called 3C inert,
because it tested only the "attack stopped" outcome. That was the report's defect,
not 3C's, and the ladder now runs on both outcomes.

## How to run

```bash
rm -rf logs/phase11_cp
python3 -m evaluation.benchmark --preset ladder --repeats 3 \
        --checkpoint-dir logs/phase11_cp --out logs/phase11    # ~1.5-2 h
python3 -m evaluation.benchmark --preset loo --repeats 3 \
        --checkpoint-dir logs/phase11_loo_cp --out logs/phase11_loo
```

Four of the seven rungs have 3B on and carry almost all the runtime — Phase 7
measured a 3B arm at ~22 min per 54 cases against ~3 min without.

## What this will not establish

- **It is our own ablation.** Rules §7's external-baseline requirement is
  discharged by [[Phase 10 — Spotlighting Has No Measurable Effect|Phase 10]], not
  by this. A per-component matrix must never be written as though it substitutes
  for a published comparison.
- **Two rungs rest on approximated vectors.** V5 and V6 are modelled at the
  nearest boundary the pipeline has, because it consumes tool *responses* rather
  than manifests.
- **n is small.** 21 malicious cases per arm at 3 repeats. Expect wide intervals
  and single-digit discordant counts; a high p is **low power**, not equivalence.
