---
tags: [adaptishield, open]
type: open
---

# Open Questions

Things **not known**, as distinct from things not yet built ([[Backlog]]).

## 1 — Does the causal sub-layer detect what static defenses miss? ⛔ UNMEASURED

**Untested in either direction.** The only benchmark built to answer it could not
→ [[Phase 7 Benchmark Withdrawn]]. **We do not claim the answer is negative; we
claim we have not measured it.**

This is [[Research Question]] #2, and it is the thesis's central comparative
claim. → [[Next Task — Repair the Phase 7 Benchmark]]

## 2 — Does a learned policy beat the directional heuristic?

**Moot for this knob, unanswered in general.** With no reachable gap, neither can
improve detection, so they agree on the no-op. That agreement is a valid finding
but **is not a comparison** → [[6l — No Natural Gap at Scale]].

It becomes answerable only if a gap exists that the knobs can reach — which
requires either multi-turn sessions (making two dead dimensions live) or a
different action space.

## 3 — How do you detect a corpus artifact in general?

> **We have no general procedure for detecting corpus artifacts, and we do not
> claim one.**

The reversal in [[6n — A Corpus That Can Fail]] was caught **because external
benign data happened to be available.** Every automated guard functioned correctly
and none could have seen it. This is the deepest open question in the project and
is not specific to it.

## 4 — Can the probe stop hallucinating without losing detection?

Three prompt attempts cost 8 detections → [[6p — Probe Hallucination Fixed at the Scorer]].
The grounding fix bounded the damage but the false positive survived via a second
route → [[Known Bounded False Positive]]. **Whether the compliance bias and the
fabrication are separable at all is unknown.**

## 5 — Is the 3B/Layer 4 boundary optimal?

[[3B Layer 4 Boundary]] is a *consequence* of refusing to duplicate the allowlist
inside 3B. A different architecture could place the discrimination elsewhere. **We
have not shown ours is the right place** — only that it is coherent.

## 6 — Does drift detection work?

The rule is correct-by-construction and **has never been exercised end-to-end**,
because no corpus shares a `session_id` → [[6g — Temporal Drift Scoping]].

## 7 — Does any of this generalize past 60 benign episodes?

> Sixty benign episodes drawn from two suites of a single benchmark **do not
> constitute the real world**, and the width of the reported interval is the
> honest part of that figure rather than an embarrassment to it.
