---
tags: [adaptishield, concept, foundation]
type: concept
---

# Safe Continuation

**The property that distinguishes AdaptiShield from termination-based defenses.**

When a takeover is confirmed, the alternative to blocking is to *repair the
context* — strip the injected directive, preserve the factual content, and let
the agent re-derive its next action from the corrected state. The user's task
completes; the attacker's does not.

## Why it is a first-class goal

Without it a confirmed takeover can only be answered by a blanket block, which
stops the attack **and** the user's task: [[ASR]] 0% at [[WCR]] 0%. That is the
second of the four shortcomings in [[Research Gap]] — defenses that terminate
prematurely.

Measured: removing [[3B Causal Analyzer]] / [[3C Context Sanitizer]] takes WCR
from **71.4% to 0% at identical ASR**. (This figure survives the withdrawal in
[[Phase 7 Benchmark Withdrawn]] as a mechanism claim, but it came from the same
flawed run and should be re-derived.)

## How it is enforced in the reward

[[GRPO Reward Function]] scores malicious → `safe_continuation` at **+1.0** and
malicious → `blocked` at **+0.7**. If they were collapsed, the optimizer would be
indifferent to killing legitimate work. This is fix B in [[Fixes A-D]].

## Implemented by

[[3C Context Sanitizer]], which is gated on a positive takeover verdict — a
gating decision with a consequence explored in [[6n — A Corpus That Can Fail]]:
3C's self-report cannot substitute for [[ACE IE DE]] because it is generated
*downstream of the decision it would have to replace*.

Its own remaining weakness is tracked in [[Backlog]]: `ContextSanitizer.sanitize()`
still carries the prompt weakness that 3B's internal sanitizer had.
