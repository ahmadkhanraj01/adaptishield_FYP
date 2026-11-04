# §1 — Introduction

## The problem

An LLM agent that reads tool output is reading untrusted text. When that text
contains instructions, the model has no reliable way to distinguish *content it
was asked to process* from *a command it was asked to follow*. This is indirect
prompt injection, and unlike a jailbreak it needs no access to the user: the
attacker writes an email, a ticket, a build log, and waits for an agent to read
it.

Proposed defenses cluster into two families. **Prompt-level** defenses mark the
untrusted span and instruct the model to disregard instructions inside it.
**Gate-level** defenses constrain what the agent may do afterwards — permission
scopes, egress allowlists, sandboxes. A third and less-explored family asks a
different question: not *does this text look dangerous*, but **did the model's
proposed action change because of it?**

That third framing is causal, and it is the one this paper evaluates. The
appeal is clear — it targets the mechanism of the attack rather than its
surface — and to our knowledge it has not previously been measured against
external corpora, ablated component by component, or tested for whether its
adaptive parameters are identifiable at all.

## What we built and what we asked

We implement a six-layer defensive pipeline whose distinguishing element is a
causal sub-layer: it runs the model's action selection under four regimes that
differ in what the model can see, and treats *differences between those regimes*
as evidence that untrusted content is driving the action. A separate adaptive
component observes detection failures and proposes configuration changes for
human approval.

We then set out to measure it honestly, which turned out to mean measuring the
instruments first. The paper's results are, in order of how much they cost us:

## Contributions

**1. A component-wise ablation showing that four of six components do nothing on
our own corpus.** Ladder and leave-one-out ablations agree on every row: the
causal analyzer moves detection (18/0 discordant, exact *p* = 7.6 × 10⁻⁶), the
sanitizer moves workflow continuation (18/0), and the tool-response screener, the
policy engine, and both halves of the permission/egress layer are 0/0 with zero
discordant pairs. Layer 4 is *redundant* rather than contributing. (§3)

**2. A measured comparison against a published prompt-level defense, which is a
null.** Spotlighting moves the steering rate from 34.8% to 33.3%, McNemar
*p* = 1.00 — and the null decomposes into two per-family effects of opposite
sign, because a transform that makes a thin payload more *legible* can increase
compliance with it. (§4)

**3. External validity, measured, at a cost.** Detection falls from **96.7% on
our corpus to ~18%** on externally-authored attacks, and the stratification is
the finding: 93.3% where the detector's target-match path can fire, **10.0%**
where it cannot — which is 90% of that corpus. (§5)

**4. A held-out test of the obvious repair, which generalizes about half.**
Widening the harm taxonomy scores 90.0% in-sample and **43.3%** on a corpus
reserved before the widening was written — non-overlapping intervals, and not
statistically significant. A harm taxonomy assembled from one corpus's nouns is
substantially that corpus's nouns. (§6)

**5. The first evaluation of a temporal-drift rule whose parameters were
formally unidentifiable — and a structural explanation of why it cannot fire.**
Two pre-registered multi-turn experiments returned no detection. Across 30 scored
turns the masked and unmasked regimes returned *the same severity* on 24, so the
causal contrast is zero 80% of the time and the drift score is zero for any
threshold, on any content. (§7)

**6. Three negative results about adaptive security configuration**, each
invisible from inside the component that produced it: a policy proposing a change
its own reward scored lower; the single gain a trainer ever found being an
artifact of a hand-written benign corpus (36 false positives of 68 on external
data); and every internal safeguard working correctly while none could see
outside the corpus. Together they are the argument for a human gate that
*recomputes* evidence rather than trusting a proposal. (§8)

## The claim these converge on

> **The causal contrast carries discriminative signal when the injected content
> contains a liftable target — an address or URL the action can name — and close
> to none otherwise.**

Every result above is a consequence of that one property. Detection collapses
externally because externally-authored attacks mostly carry no such target. The
harm taxonomy generalizes about half because it is a list of nouns standing in
for a mechanism. And the adaptive layer proposes nothing because two of its five
parameters act on a quantity we measure at zero in 80–97% of turns.

We think this is the most useful thing a first evaluation of causal
injection-detection can report, and it is not what we expected to find. The
approach is not refuted — it detects real attacks that a static allowlist and a
prompt-level defense both miss — but its operating envelope is far narrower than
the framing suggests, and it is bounded by a property of the *scorer* rather than
of the causal idea.

## On negative results and instruments

Six of the results above are negative, and three surfaced from instrumentation
built to answer a different question. That is not incidental. Systems of this
kind fail more often in their **instruments** than in their mechanisms, and
instruments are the least-tested part of any evaluation, because a broken
instrument returns a plausible number rather than an error. We report the
withdrawn measurements alongside the corrected ones throughout — a benchmark
whose first result was invalid by construction, a baseline whose sign was
reversed by its own scorer, an ablation that called a working component inert —
because in each case the corrected number is only trustworthy in light of what
the first one got wrong.

All figures are regenerable by committed commands over a released artifact
(§Availability), and the deterministic test suite runs in ~10 s with no model, no
network and no GPU.
