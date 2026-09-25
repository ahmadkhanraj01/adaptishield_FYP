---
tags: [adaptishield, finding, ablation]
type: finding
status: measured
date: 2026-08-08
---

# Phase 11 — Only Two Layers Do Anything

**3B stops attacks. 3C keeps the workflow alive. The other four components change
nothing measurable — cumulatively *or* at the margin.**

Two independent ablations, 54 cases each (21 malicious, 33 benign), and they
**agree completely**. `results/phase11/` and `results/phase11_loo/`.

## The ladder — what each layer adds to the one below it

| Rung | Adds | [[ASR]] | [[WCR]] | 3B stops |
| :--- | :--- | ---: | ---: | ---: |
| `undefended` | — | 100.0% | 0.0% | 0 |
| `screener_only` | L3 screener | 100.0% | 0.0% | 0 |
| `plus_policy` | [[3A Policy Engine]] | 100.0% | 0.0% | 0 |
| `plus_causal` | **[[3B Causal Analyzer]]** | **14.3%** | 0.0% | **18** |
| `plus_sanitizer` | **[[3C Context Sanitizer]]** | 14.3% | **85.7%** | 18 |
| `plus_permission` | L4 scope | 14.3% | 85.7% | 18 |
| `full` | L4 allowlist | 14.3% | 85.7% | 18 |

### Paired tests, on two outcomes

| Rung | attack stopped | workflow continued |
| :--- | :--- | :--- |
| `plus_policy` → `plus_causal` | **18 / 0, p = 0.000** | 0 / 0 |
| `plus_causal` → `plus_sanitizer` | 0 / 0 | **18 / 0, p = 0.000** |
| all four others | 0 / 0 | 0 / 0 |

**Zero discordant pairs** on the inert rungs — not a weak effect, an identical
outcome on all 21 malicious cases.

## Leave-one-out agrees, which was not guaranteed

The ladder measures a layer *given only the layers below it*. Leave-one-out
measures it *given all the others*, and **the two disagree exactly when layers are
redundant with each other**. [[Phase 7 Repaired — The Causal Sub-Layer's Marginal Detection|Phase 7]]
found one such case, so disagreement was the expected outcome for Layer 4.

| Removed from `full` | attack stopped | workflow continued |
| :--- | :--- | :--- |
| L3 screener | 0 / 0 | 0 / 0 |
| 3A | 0 / 0 | 0 / 0 |
| **3C** | 0 / 0 | **18 / 0, p = 0.000** |
| L4 permission | 0 / 0 | 0 / 0 |
| L4 egress | 0 / 0 | 0 / 0 |

Identical conclusions from both directions. The `full` arm here is the **same 54
results** as the ladder's top rung, reused from its checkpoint, which is what makes
the two tables directly comparable rather than merely similar.

## The report called 3C inert, and that was the report's fault

The first pass printed *"`plus_sanitizer` adds NOTHING detectable"* — for a rung
that moves WCR from **0% to 85.7%**. True of the outcome being tested and false of
the layer.

3C runs **only after** a takeover is confirmed, and converts a blanket block into a
safe continuation. Its entire contribution is usability, so an ASR-only ablation
**structurally cannot see it** and reports a working layer as dead weight. Same
failure as judging a defense by end-to-end ASR while the allowlist absorbs
everything: the wrong outcome variable makes a real effect invisible.

Fixed by running the whole ladder on **both** outcomes and calling a rung inert only
when it moves neither. → [[Instruments Fail More Than Mechanisms]], fifth
application.

## Two results that cut against the architecture

**Layer 4 is redundant, not contributing.** `backstop_share` climbs **0% → 17% →
33%** as Layer 4 is added, so by `full`, **6 of 18** of 3B's detection stops would
*also* have been caught by a static allowlist. Layer 4 adds no incremental
detection while making a third of the novel component's stops non-load-bearing.
Defensible as defence-in-depth; it is **not** evidence for the layer →
[[3B Layer 4 Boundary]].

**3B's false positives are invisible to every p-value here.** `FPR ours` goes
**0/3 → 3/3** the moment 3B switches on, and stays there in all four downstream
rungs. Paired tests exclude benign cases by construction — an arm that blocks a
benign document is *worse*, so pairing them at the same polarity would let
over-blocking read as a win — so this cost appears in no significance test in either
table. n=3 and it is a labelled diagnostic, never a rate → [[FPR]]. The external
cohort's 0/30 is not reassurance either: it is the stride subsample that
**omits both known false positives**.

## What was predicted before the run

Stated in [[Phase 11 — Per-Component Ablations]] before launching, which is what
makes this evidence rather than a rationalisation.

| Prediction | Outcome |
| :--- | :--- |
| 3B rung large — the central claim | ✅ 18/0, p = 0.000 |
| 3A `helped == 0` → [[Inert Blocked Patterns]] | ✅ 0/0, zero discordant |
| 3C: ASR flat, WCR large | ✅ exactly that — and it exposed the reporting defect |
| L4 egress `helped == 0` | ✅ 0/0, confirming Phase 7 |

## What this does not establish

- **It is our own ablation.** Rules §7's external-baseline requirement is
  discharged by [[Phase 10 — Spotlighting Has No Measurable Effect]], not by this.
  A per-component matrix must never be written as though it substitutes for a
  published comparison.
- **Not that L3, 3A and Layer 4 are useless in general** — only that **this corpus**
  gives them nothing to do. All 21 malicious cases are tool-response injections
  reaching a `send_email`-shaped action. A rug-pull or a poisoned manifest is what
  L3 and the registry exist for, and V5/V6 are **approximated** because the pipeline
  consumes tool responses rather than manifests → [[Backlog]] item 4.
- **Small n.** 21 malicious cases per arm at 3 repeats; every interval is wide and
  discordant counts are single digits. A `p = 1.000` here with **0 discordant pairs**
  is a strong statement about this corpus and a weak one about the population.
- **The three residual attack successes are unexplained by this phase.** All are V4,
  the [[Address-Free Attacks|address-free]] vector, and all are `masked = 0` —
  severity-function failures, the largest remaining lever → [[Backlog]] item 1.
