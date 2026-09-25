---
tags: [adaptishield, finding, instrument, negative-result]
type: finding
status: measured
date: 2026-08-08
---

# 3B's Refusal Exposure Is Live and Unrealised

**0 of 209** recorded severity-2 masked-regime probe samples are refusal-shaped.
The defect [[The Scorer Cannot See Negation]] left open in the four probe regimes
is **real, live, and has never fired.** So the regime scorer stays as it is.

This closes [[Backlog]] item 0, which was blocking [[Phase 11 — Per-Component Ablations|Phase 11]].

## The question, and why it blocked Phase 11

Phase 10's negation fix went into `score_agent_action` and **deliberately not**
into `_score_action`, which the four probe regimes call. That left the obvious
worry unanswered: if the *masked* probe ever answers *"do not forward anything to
collector@attacker-drop.net"*, the address mention escalates it to 2, and 2 alone
trips the standalone takeover rule → [[6f — Standalone Severity Rule]].

Phase 11 attributes every stop to a layer, and 3B's attributions are built on
those severities. Measuring this **after** the ablation matrix would mean
re-running the matrix.

## The exposure is on the shipped path, not a fallback

Worth being precise, because the first framing of this item was wrong.
`CausalAnalyzer()` is constructed with `semantic_scoring=False` at **every**
production call site — [[6e — Semantic Scoring Ablation]] measured the semantic
scorer as worse end-to-end. On that path `_score_action_by_keyword` escalates on
`_references_mediator_target` **before any other test**, with no negation handling
of any kind.

The semantic path is not exposed the same way: the judge gates the escalation
behind a finding of compliance at all, so *"I cannot send anything to
attacker@evil.com"* stays 0. But that path is not the one that ships. The
exposure is live.

## Method

`evaluation/refusal_audit.py` — read-only, **no model calls**. For every masked
and masked_sanitized probe sample this project has recorded, apply the Phase 10
fix's **own** predicate, `_target_clause_is_negated`, and ask whether it would
de-escalate the sample from 2 to 1.

Using the real predicate rather than a keyword sweep for refusal words matters:
it measures the change that would actually be made, not a proxy for it.

| Source | samples | sev ≥ 2 | tested | de-escalated |
| :--- | ---: | ---: | ---: | ---: |
| `logs/benchmark/run.log` (Phase 7, 216 cases) | 432 | 132 | 132 | **0** |
| `logs/probe_diagnostic/after_fix.json` | 84 | 48 | 48 | **0** |
| `logs/probe_diagnostic/full_run.json` | 84 | 29 | 29 | **0** |
| **total** | **600** | **209** | **209** | **0** |

Both the eight malicious vectors **and** the B01–B10 external benign cohort are
in the denominator — the benign side is where an inflated severity would be a
false positive, so auditing only the attacks would have skipped the half that
costs something.

## The zero has a positive control

A broken parser, an empty mediator join, or a predicate that never fires would
all print the same reassuring zero. So the audit synthesises the refusal it is
hunting for against a **real** V1 mediator and requires the predicate to flag it
— and requires it to *spare* the matching plain compliance, so a predicate that
suppressed everything could not pass one-sided. The control passes.

That is the [[Instruments Fail More Than Mechanisms]] lesson applied before the
result rather than after it.

## Why it never fires — the mechanism

**The masked probe masks the user's goal.** The model is shown untrusted content
with no legitimate task to weigh it against, so it has nothing to refuse the
injection *in favour of*. It restates the instruction instead.

Refusal language needs a competing goal. Phase 10's derivation path had one —
which is exactly why **16 of 37** cases there were refusals — and the masked
probe structurally does not. The two paths differ in the one property that
produces the defect.

This is a structural argument, not luck, which is what makes the zero worth
acting on.

## And it is not the Known Bounded False Positive mechanism

The backlog claimed it was. It is not.
[[Known Bounded False Positive|`agentdojo-workspace-041`]] is the probe
**hallucinating** an address from a birthday-party document. Both are "probe
output that is not compliance, scored as compliance", but hallucination is
**confirmed and open** while refusal is now **measured absent**. Collapsing them
would have made a fixed problem look open and an open one look addressed.

## What was done, and what was not

- ✅ `evaluation/refusal_audit.py` — the audit, with its control
- ✅ `tests/test_refusal_audit.py` — **35 tests**, no LLM, no dependence on
  gitignored `logs/`; they assert the defect **as it currently is**, so a future
  change to the regime scorer is a visible act rather than a silent one
- ❌ **No change to `_score_action`.** Applying the fix would move no measured
  number, and Rules §2's re-measurement of the gen-2 campaign and benign FPR
  would buy nothing.

## What this does not establish

- **Not that the defect cannot fire.** Observational over 8 vectors and 21
  diagnostic cases, with mediators this project authored plus a stride sample of
  [[AgentDojo]] benign text. A corpus with softer injections against a larger
  instruct-tuned model is precisely where a masked probe might start refusing.
  The exposure stays recorded as **live** in code and in the test suite.
- **Not that 3B's severities are correct** — [[Residual Misses Decomposed]]'s four
  `masked = 0` misses are untouched, and the severity function remains the
  largest detection lever → [[Backlog]] item 1.
- **48 of the tested samples** were scoped against the *unsanitised* mediator,
  because `run.log` prints sanitised text only when 3C ran and
  `_sanitize_mediator` is an LLM call that cannot be recomputed read-only. That
  over-approximates the target list, so it can only **inflate** the
  de-escalation count — the safe direction for a zero.
