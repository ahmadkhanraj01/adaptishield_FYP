---
tags: [adaptishield, literature]
type: literature
---

# AgentDojo

A published agent-security benchmark from **ETH SPY Lab**, MIT-licensed, v0.1.35.
Vendored into this project by `red_team/vendor_agentdojo.py` into
`red_team/data/agentdojo_benign.json`.

## What was taken, and what deliberately was not

**Taken:** the **benign** environment content only — inboxes, documents and
calendar entries composed for an unrelated purpose by people who had never seen
this pipeline. 63 candidate fields harvested, **60 retained** after excluding 10
carrying an injection placeholder and discarding 3 duplicates.

**Not taken:** the attack side. Only the true negatives are used.

## Why this mattered more than anything else in the corpus work

A false-positive rate measured against a distribution **the defender constructed**
measures the defender's imagination. Externally-authored benign data is the only
instrument that detected the reversal in [[6n — A Corpus That Can Fail]]:
the single improvement the adaptive layer ever found produced **36 false
positives out of 68 benign** cases on contact with data someone else wrote.

## A note on the exclusion filter

The first attempt at the injection-placeholder filter **searched for the wrong
string and matched nothing**, which would have admitted 10 pieces of attack
scaffolding into the benign denominator — one of them embedded in otherwise
ordinary prose. Another entry in [[Instruments Fail More Than Mechanisms]].

## Open handling issue

The Layer 5 dashboard embeds 828 records including attacker-authored text, and
the AgentDojo attribution is not yet rendered on the page. Both must be settled
before publishing it — see [[Backlog]].

Used by: [[Evaluation Corpus]], [[FPR]], [[Known Bounded False Positive]],
[[3B Layer 4 Boundary]].
