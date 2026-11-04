---
tags: [adaptishield, log, entry]
type: log-entry
date: 2026-08-08
---

# Entry XVIII — Measuring a Defect Instead of Fixing It

*8 August 2026, after the Phase 10 push.*

[[Entry XVII — The Baseline That Scored Its Own Refusals]] ended with a defect
half-repaired on purpose. The negation fix went into `score_agent_action`, which
only the Phase 10 derivation path calls, and deliberately stayed out of
`_score_action`, which the four probe regimes call. The reasoning was
[[6p — Probe Hallucination Fixed at the Scorer]]'s: in the masked probe a mention
of the attacker address is the single signal the whole detector leans on, and
three prior attempts to be clever there had cost eight detections. So the fix went
where its failure mode was bounded, and the unbounded half was written down as
open rather than attempted.

That left an item I had ranked first in the backlog, ahead of Phase 11, on the
grounds that it would touch every layer-attributed number. The reasoning was
sound; the framing of the item was not. Two things in it turned out to be wrong,
and finding that out was most of the work.

The first was a claim about where the defect lives. I had described the keyword
scorer as the fallback path — what runs when the LLM judge cannot be reached — on
the assumption that the semantic judge was the normal case. It is not.
`CausalAnalyzer()` is constructed with `semantic_scoring=False` at every
production call site, because [[6e — Semantic Scoring Ablation]] measured the
semantic scorer as more accurate per action and worse end-to-end. On the keyword
path `_score_action_by_keyword` escalates to severity 2 on a mediator-target match
before any other test runs, with no negation handling of any kind. The exposure is
therefore not a fallback at all: it is the shipped path, and severity 2 alone
trips the standalone takeover rule. Meanwhile the path I had assumed was normal is
the one that is *not* exposed, because the judge gates the escalation behind a
finding of compliance, so a refusal naming the address stays at zero. I had the
asymmetry exactly backwards, and it made the item sound less urgent than it was.

The second was the mechanism. I had written that this was the same mechanism as
the [[Known Bounded False Positive]] — `agentdojo-workspace-041`, the birthday
party document that stays a false positive by decision. It is not. That case is
the probe *hallucinating* an address from content that contains none. This one
would be the probe *refusing* and naming an address that is really there. Both are
instances of a more general shape — probe output that is not compliance, scored as
compliance — but collapsing them would have made a confirmed open problem look
addressed and an unmeasured one look understood.

With the framing corrected the measurement itself was cheap, and the design
question was what to measure with. A keyword sweep for refusal words would have
been the obvious instrument and the wrong one: it measures a proxy for the change
rather than the change. What matters is whether applying the Phase 10 fix to the
regime scorer would move anything, so the right predicate to apply is the Phase 10
fix's own — `_target_clause_is_negated`, clause-scoped, with `ignore` deliberately
absent from its cues. `evaluation/refusal_audit.py` walks every masked and
masked_sanitized probe sample this project has recorded, applies that predicate to
the ones scored 2, and reports how many would drop to 1 and how many of those
would disarm a takeover. It calls no model.

Two corpus decisions were load-bearing. The first was to join Phase 7's run log
against `all_vectors()` rather than `VECTORS`. The eight malicious vectors are
where the defect would cost a detection; the ten external benign documents are
where it would cost a *false positive*, which is the more expensive direction and
the one [[6n — A Corpus That Can Fail]] was written about. Joining on the malicious
set alone would have audited the cheap half and reported a rate. The second was
what to do about the sanitised side. `_sanitize_mediator` is an LLM call, so the
text the masked_sanitized probe actually saw cannot be recomputed read-only, and
3C prints it only when a takeover was confirmed. Rather than drop those samples I
scoped them against the unsanitised mediator and flagged them, on the argument
that sanitisation deletes directives while deliberately keeping addresses, so the
unsanitised text can only contain more candidate targets, never fewer — which can
only inflate the de-escalation count. For a result whose claim is that the count
is zero, over-approximating is the safe direction.

The last piece was a control, and it exists because of the pattern this project
keeps rediscovering. A broken parser, an empty mediator join, or a predicate that
never fires would all print the same reassuring zero, and
[[Instruments Fail More Than Mechanisms]] is by now the most reliable
generalisation in the log. So the audit synthesises the refusal it is hunting for
against a real V1 mediator and requires the predicate to flag it — and requires it
to spare the matching plain compliance, so that a predicate suppressing everything
cannot pass a one-sided check. Building the control before reading the result is
the only version of this that is worth anything; every previous time I read the
result first, the result was about the instrument.

The answer is zero. Across 600 recorded masked-regime probe samples, 209 scored
severity 2, and the negation predicate de-escalates none of them. The control
passes.

What makes that worth acting on rather than filing as luck is that there is a
structural reason for it. The masked probe masks the user's goal — that is the
whole point of the regime, and [[6i — Masked Probe Rewrite]] is what made it work.
The model is shown untrusted content with no legitimate task to weigh it against,
so it has nothing to refuse the injection *in favour of*, and it restates the
instruction instead. Refusal language needs a competing goal. Phase 10's
derivation path supplies one, which is precisely why sixteen of thirty-seven cases
there were refusals; the masked probe structurally does not. The two paths differ
in the one property that produces the defect, which is a better explanation than
the absence of an effect usually gets.

So the regime scorer is unchanged, and that is the finding. Applying the fix would
move no measured number, and Rules §2's price for touching it — re-measuring the
gen-2 campaign and the benign FPR — would buy nothing. What was added instead is
the audit, and thirty-five tests that assert the defect **as it currently is**:
that the keyword scorer reads a refusal naming a mediator target as full
compliance, that `score_agent_action` does not, and that the two disagree at
exactly that point. Asserting the behaviour I would prefer to change is not
squeamishness. It means a future change to the regime scorer becomes a visible
failing test rather than a silent drift, and it keeps the exposure recorded in the
suite instead of resting on a vault note nobody executes and a log file that is
gitignored.

There is a temptation, having established that a defect never fires, to write it
down as fixed. It is not fixed; it is unrealised on two corpora of this project's
own construction, measured against a 4B model, with a positive control that shows
the instrument would have said so otherwise. A corpus of softer injections against
a larger instruct-tuned model is exactly where a masked probe might begin refusing
out loud, and at that point the exposure becomes a live false-positive source with
no code change required to activate it. The honest status is *live and unrealised*,
and that is what the finding note is titled.

## What this does not establish

- **Not that the defect cannot fire.** Observational, over eight vectors and
  twenty-one diagnostic cases, with mediators this project authored plus a stride
  sample of externally-authored benign text. The exposure stays live in code.
- **Not that 3B's severities are right.** The four `masked = 0` residual misses
  are untouched, and the severity function remains the largest detection lever and
  the hardest → [[Residual Misses Decomposed]].
- **Not a Phase 11 result.** This clears the way for the ablation matrix by
  showing its foundation does not need re-laying. It says nothing about what the
  matrix will find.
