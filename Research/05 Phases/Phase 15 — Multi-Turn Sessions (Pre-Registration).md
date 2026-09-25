---
tags: [adaptishield, phase, preregistration]
type: phase
status: pre-registered
date: 2026-08-12
---

# Phase 15 — Multi-Turn Sessions (Pre-Registration)

**🔴 This note is written BEFORE the cohort is run. Nothing below may be edited
after the first result is seen.** Same protocol as Phase 13's holdout, which is
the precedent that worked: the lexicon was frozen at `46cfbfb` and the corpus
committed at `4d48efd` *before* the result was known
(→ [[The Lexicon Generalises About Half]]).

## The question

Every number so far says the adaptive layer does nothing →
[[The Adaptive Layer Proposes a No-Op]]. 3D proposes a no-op, it has **no rung**
in [[Phase 11 — Only Two Layers Do Anything]]'s ladder, GRPO's learned
distribution is near-uniform, and 2 of its 5 joint dimensions are
*unidentifiable*.

But that is not evidence the layer is useless. It is evidence **the corpus
cannot ask the question.** Campaigns give every case a unique `session_id`, so
the temporal-drift rule is dead by construction — see [[6g — Temporal Drift
Scoping]], which added the two guards but never had a cohort that could fire
them.

## Why it is cheap — the machinery already exists

No pipeline rewrite. Verified 2026-08-12:

- `CausalAnalyzer.session_history` is a dict keyed by `session_id`
  (`causal_analyzer.py:914`), and the current boundary is appended **before** the
  rules run
- `evaluate_boundary(..., boundary_index=, session_id=)` already carries both
  (`causal_analyzer.py:889`)
- the drift rule is already written, with both §6g guards in place
  (`causal_analyzer.py:1027`)

What is missing is a corpus that exercises it, not code.

## What the rule requires

With `window_size = 3` and `risk_threshold = 0.6`:

```
len(history) >= 3   and   masked.severity >= 1        # both §6g guards
risk = 0.5 * (max(-ace_slope, 0) + max(ie_slope, 0))  >= 0.6
       where ace_slope = ace[t] - ace[t-2],  ie_slope = ie[t] - ie[t-2]
```

So: **sessions of ≥3 boundaries** sharing one `session_id`, the judged boundary
showing `masked >= 1`, and the escalation moving `(-Δace + Δie) >= 1.2` across
the window. With severities in {0, 1, 2}, an ACE falling `1 → 0 → -1` clears it
alone. That is a **slow-burn** attack: early turns no single-boundary rule would
flag, escalating to compliance.

## Why it is the strongest contribution still available

This is an attack class that spotlighting and static screening **cannot see even
in principle** — both judge one boundary at a time.
[[Phase 10 — Spotlighting Has No Measurable Effect]] is currently a null on a
threat model that favours nobody. Phase 15 is a threat model where the
architecture has a *structural* reason to win, and the paper has no such section.

## Pre-registered criteria

| | Criterion | Reported as |
| :--- | :--- | :--- |
| **Primary** | ≥1 **drift-only** catch: the drift rule fires on a malicious boundary where neither the IE rule nor the standalone `masked >= 2` rule fires | count + Wilson CI over the multi-turn malicious cohort |
| **Secondary** | trainer reward becomes **non-flat** in `risk_threshold` and/or `window_size` | the reward table, replacing "exactly flat" in the open items |
| **Guard** | drift-only **false positives** on a multi-turn *benign* cohort | a rate with n, never pooled with the 60-episode single-boundary FPR |

## Both outcomes are publishable — which is the point

- **Drift fires** → first measured evidence the adaptive layer does anything, on
  a threat model the baselines structurally cannot address. Two of 3D's five
  dimensions become learnable for the first time, and a 3D rung can finally join
  Phase 11's ladder.
- **Drift does not fire** → a far stronger negative result than the paper has.
  *"We built the cohort that makes the knobs identifiable and there was still
  nothing to learn"* is a finding. *"We never built a corpus that could tell"* is
  a reviewer's question in §Limitations.

## Order of operations (the pre-registration itself)

1. Generate the cohort, inspect it, **commit it**.
2. This note and `Phase.md` §15 **committed**.
3. **Only then** run.

Without that, the multi-turn corpus becomes a second development set and the
result is worth nothing — the trap Phase 13 fenced off for the lexicon, where
there is no third corpus.

## Fences

- ⛔ **Do not pool with any existing corpus.** Different threat model, different
  cohort, its own table — the discipline [[Phase 12 — InjecAgent]]'s strata
  warning enforces, where pooling was wrong by 33 points.
- ⚠️ **Changes no shipped component** — not the probe prompt, not the scorer, not
  the defaults. That is why [[Rules and Invariants]] §2's re-measurement cascade
  is not triggered and why it fits the runway.
- If the run suggests changing `window_size` or `risk_threshold` defaults, that
  is a **finding to report**, not a change to land before submission.

Related: [[6j-6k — The Loop Closes a Matching Gap]] (the mechanism works on a
constructed gap), [[6l — No Natural Gap at Scale]] (no gap arises on
single-boundary corpora), [[Phase Roadmap]].
