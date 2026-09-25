---
tags: [adaptishield, log, entry]
type: log-entry
date: 2026-09-12
---

# Entry XXIV — The Corpus Was Already Complete

*12 September 2026.*

The session had one job, written out in advance as a task brief: expand the
[[AgentDojo]] benign cohort from 60 documents to 110 or more, re-record it three
times, and give §IV-C an [[FPR]] whose [[Wilson Score Interval]] is not dominated
by small-*n* width. It was framed as the last open evidence blocker before the
manuscript's numbers could be called final. The brief was careful — a stop-and-ask
gate before any draw, an instruction not to pad with anything synthetic, an
instruction to halt if the existing 60 no longer resolved against v0.1.35.

The gate fired on the first question, and the answer closed the task rather than
scoping it.

## There was nothing to draw

I had been thinking of the 60 as a sample. `vendor_agentdojo.py` does not take a
sample. It walks `workspace` and `slack`, takes every `body` / `content` /
`description` string of 40 characters or more, drops the ten carrying an injection
placeholder and three duplicates, and keeps what is left. That is 63 candidates
and 60 survivors — **the entire benign content of those two suites**. Asking for
50 more disjoint episodes was asking for documents that do not exist.

First I checked the corpus had not moved under us, because the brief said to stop
if it had. Fresh wheel, committed vendoring script, re-run: `harvested=63
duplicates_dropped=3 excluded_injection_fields=10 vendored=60`, item-for-item and
in the same order as the tracked file. No drift. The one thing that could have
made this session expensive was fine.

Then I counted the whole package rather than just our slice, because *"you cannot"*
is only useful with a number attached: 8 more strings if we take every field name
in the two suites, 14 if we drop the length floor to 20, 55 if we admit the
`travel` suite's reviews, 103 if we take everything ≥ 40 characters anywhere.
`banking` has nothing at all. Only the `travel` routes reach 110 →
[[AgentDojo's Benign Pool Is Exhausted at 60]].

## Why I recommended not taking them

`vendor_agentdojo.py` already argues against off-domain padding in a comment, and
the comment turned out to be sharper than when it was written. Detection here
rides on the target-match path. Travel reviews carry no address or URL an action
could name, so 55 of them in the denominator would very likely pull the measured
FPR *down* — a better number produced by changing the distribution underneath it.
That is [[6n — A Corpus That Can Fail]] running in reverse: there, external data
exposed an improvement that was an artifact of our corpus; here, the temptation
was to manufacture one the same way.

The width does not even arrive. At a held rate of ~3.3% the projected interval
goes 10.5 points at *n*=60 to 7.2 at 115 — and only 5.7 at the maximally impure
163. The interval is wide because the rate is near zero. I nearly did not run that
arithmetic, having already decided; running it is what turned the recommendation
from a preference into an argument.

The decision: **keep n=60.** Nothing was recorded, re-scored, or re-vendored. No
figure reads `results/noise_floor/agentdojo_benign.json` — only `fig2_stratified`
reads the InjecAgent file — so no figure regenerates, and no number in §IV-C or
§IV-D moves.

## The part that was already wrong before I started

`Rules.md` had an uncommitted edit in the working tree changing *"the 60
externally-authored AgentDojo benigns"* to **"the 110"** — the target number,
written into the rule that forbids pooling cohorts, before a single document had
been recorded. The same edit reflowed the bullet and introduced a typo.

This is [[A Published p-Value With No Committed Source]] in miniature and caught
earlier: a figure entering a document ahead of the evidence for it, in a file
whose §7 says in as many words that a statistic is a result and not arithmetic.
Reverted. It is worth recording that the rule was edited to match the plan without
the plan having been executed — that the number was *aspirational* is exactly what
makes it dangerous, because six weeks later nothing about the sentence looks wrong.

## What I am taking from it

The blocker was never the corpus size. It was a sentence in §XII — *"the benign
corpus is 60 external documents"* — that reads as an apology and invites the
reviewer's question. The honest version is stronger and is now available: it is a
**census, not a sample**, the complete in-domain benign content of a published
benchmark, verified exhaustive against the shipped package. The limitation
relocates to where it belongs: a tighter benign interval needs a *second* external
benign corpus, not more of this one, and there is no third corpus waiting — the
same shape as the attack-side gap [[Backlog]] already records.

One trap fell out of the counting. Case identifiers are positional, so any future
re-vendoring silently relabels `workspace-041` / `-048` / `-055` — the three
documents the per-case stability matrix and the manuscript both cite by name. That
needs a content-hash key before anyone re-vendors, not after →
[[The Benign FPR Has a Noise Floor Its Own Size]].

The manuscript prose is untouched; §IV-D's reframing is mine to write and has not
been written yet.

*(Numbering: Volume II's last entry is XXIII, 9 Aug. The paper-production sessions
between then and now are not logged — a gap in the ritual, not in the work.)*

## What this entry does not establish

Nothing was measured this session. The 3.3%, its interval, and the 1 always / 57
never / 2 unstable split are unchanged and uninspected. The claim is about the
**corpus**, not the rate: that it cannot be grown from this source without
changing what the source is. Whether 60 is *sufficient* is a separate question,
and the answer is still no.

## Related

- [[AgentDojo's Benign Pool Is Exhausted at 60]]
- [[The Benign FPR Has a Noise Floor Its Own Size]]
- [[6n — A Corpus That Can Fail]]
- [[A Published p-Value With No Committed Source]]
