---
tags: [adaptishield, phase, hub]
type: hub
---

# Phase Roadmap

*Last updated in the repo: 2026-08-09. Rough completion: **~93% build, ~70% evidence**.*

| Phase | Scope | State |
| :--- | :--- | :--- |
| **0** | Defensive pipeline (Layers 0–4, gated sandbox, telemetry) | ✅ Done |
| **1** | Security sub-layer [[3A Policy Engine]] / [[3B Causal Analyzer]] / [[3C Context Sanitizer]] | ✅ Done |
| **2** | [[Red Team Module]] (generator → agent → evaluator → optimizer) | ✅ Done |
| **3** | 3D v1 + adaptive-loop experiment | ✅ Done — **negative result** → [[6d — Adaptive Loop Negative Result]] |
| **4** | Measurement [[Fixes A-D]] | ✅ Done |
| **5** | Re-run the loop on the fixed measurement | ✅ Done — **nothing to close** |
| **5b** | Prove the loop *can* close a knob-matching gap | ✅ Done — closes **and** generalizes → [[6j-6k — The Loop Closes a Matching Gap]] |
| **6** | 3D real GRPO training | ✅ **Executed** → [[Phase 6 — GRPO on Kaggle]] |
| **6b** | Diagnose the 15 residual 3B misses | ✅ Done — one defect, **114/114** → [[6m — The Single-Character Defect]] |
| **6c** | Fix the evaluation corpus | ✅ Done → [[6n — A Corpus That Can Fail]] |
| **6d** | Joint GRPO action space + propose-and-verify | ✅ Done — the one gain was a **corpus artifact** |
| **7** | Eight-vector benchmark | 🟡 **Built & run — first result withdrawn** → [[Phase 7 — Eight-Vector Benchmark]] |
| **8** | [[Layer 5 — Human in the Loop]] | ✅ Done — found [[Inert Blocked Patterns]] on its first run |
| **9** | Grow the pytest suite | 🟡 Ongoing — **452** tests → [[Test Suite]] |
| **10** | External baseline (spotlighting) | ✅ Done — **no measurable effect** → [[Phase 10 — Spotlighting Has No Measurable Effect]] |
| **11** | Per-component ablations | ✅ Done — **only two layers do anything** → [[Phase 11 — Only Two Layers Do Anything]] |
| **12** | [[InjecAgent]] — external attacks | ✅ Done — detection **96.7% → ~18%** → [[Phase 12 — Detection Is 18% on Someone Else's Attacks]] |
| **13** | The severity function | 🟡 Diagnosed + **held out**, not landed — in-sample 90.0%, holdout **43.3%** → [[The Lexicon Generalises About Half]] |
| **14a** | Repeat measurements — noise floor + stratum power | 🟡 **Half done (12 Aug)** — FPR count stable at 2/60 across k=3, membership churns → [[The Benign FPR Has a Noise Floor Its Own Size]]. InjecAgent strata still single-repeat |
| **15** | **Multi-turn sessions** — is the adaptive layer measurable at all? | 🔴 **First run: primary not met, 0/3 — and no session posed the question** → [[Phase 15 — The Cohort Never Posed the Question]] |
| **14** | Manuscript + reproducibility artifact | 🔲 Drafting from week 1; 🔵 journal decision still open |

## The shape of the roadmap

Phases 0–2 are construction. **Phase 3 is where the project's character changes**:
the headline experiment returned a negative, and everything from Phase 4 onward is
either repairing the *measurement* that negative exposed, or discovering that
another instrument was lying.

Phases 4, 6b, 6c and 6d are all, in effect, *"fix the thing that was supposed to
tell us whether the thing worked."* → [[Instruments Fail More Than Mechanisms]]

## What is actually left

Phase 7's repair is ✅ done, and so are 10, 11 and 12. **Phase 13 is measured but
not landed**: two scorer flags ship off, and landing either owes Rules §2's gen-2
campaign re-measurement → [[Backlog]] item 1.

**Updated 12 Aug 2026 — the deadline moved to 14 September**, which changes what
is affordable. Under the old one-week deadline the plan was to write up the
evidence in hand and put the adaptive layer's no-op in §Limitations. With ~4.5
weeks, [[Phase 15 — Multi-Turn Sessions (Pre-Registration)]] is reachable, and it
is the one experiment that can turn *"the adaptive layer does nothing"* from an
untested assumption into a measured result — in either direction. Phase 14a's
repeats run first because they harden the two most attackable numbers and cost
compute only.

The one methodological rule carried out of Phase 13: **any further lexicon revision
needs a new held-out corpus reserved before the revision is written.** Both external
attack corpora are now spent as measurement sets.
