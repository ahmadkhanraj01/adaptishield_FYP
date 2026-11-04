---
tags: [adaptishield, metric]
type: metric
---

# WCR

**Workflow Continuation Rate** — the fraction of **adversarial** trials in which
the user's legitimate task still completes despite the adversarial content.
Higher is better.

**This is the metric that distinguishes AdaptiShield from termination-based
defenses.** It directly captures [[Safe Continuation]].

## Why it exists

Without [[3C Context Sanitizer]], a confirmed takeover can only be answered by a
blanket block — which stops the attack **and** the user's task: [[ASR]] 0% at WCR
**0%**. That is shortcoming #2 in [[Research Gap]].

The comparison the original specification framed itself against:

| Pattern | Profile |
| :--- | :--- |
| MELON-style | low ASR, **low WCR** (terminate on detection) |
| Task Shield-style | moderate ASR, moderate WCR |
| **Target** | near-zero ASR at **WCR > 70%** |

## Measured

**71.4%** in the full arm vs 0% without the causal sub-layer.

🟡 The target was met — but the figure came from the run invalidated in
[[Phase 7 Benchmark Withdrawn]]. **The mechanism claim survives** (removing the
sanitiser genuinely converts safe continuations into blanket blocks) **but the
number should be re-derived.**

## Where WCR is enforced structurally

🔴 In [[GRPO Reward Function]]: malicious → `safe_continuation` (**+1.0**) must
out-reward malicious → `blocked` (**+0.7**). Collapse them and the optimizer
becomes indifferent to killing legitimate work — fix B of [[Fixes A-D]].

## Known risk to it

[[3C Context Sanitizer]]'s `sanitize()` still carries the old prompt weakness and
**feeds the user-visible continuation and this metric**. It was left unchanged
rather than altered silently → [[Backlog]].

Companions: [[ASR]] · [[FPR]].
