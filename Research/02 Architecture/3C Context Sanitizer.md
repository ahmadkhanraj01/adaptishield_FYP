---
tags: [adaptishield, architecture, component, sublayer]
type: component
status: partial
---

# 3C Context Sanitizer

`layer2/security_sublayer/context_sanitizer.py` — **the mechanism that makes the
system usable**, by implementing [[Safe Continuation]].

Triggered **exclusively** on a positive takeover verdict from
[[3B Causal Analyzer]].

## Three properties it must satisfy (per [[AgentSentry]])

1. **Factual fidelity** — task-relevant entities, timestamps and structured data
   preserved in full
2. **Non-actionability** — imperative spans, priority-overriding language,
   tool-capability directives and goal-extraneous commitments removed
3. **Task alignment** — only factual content whose downstream influence is
   consistent with the user goal is retained

After purification the agent **re-derives its next action** from the corrected
state. The workflow resumes rather than terminating.

## The three failure modes found in 6m

The diagnostic showed 3B's *internal* sanitizer failing in three distinct ways:

- rewriting a directive into a **milder but still live imperative** rather than
  deleting it
- occasionally returning its input **unchanged**, including the override marker
- because its prompt asked it to preserve material relevant to the reader's goal,
  **copying the reader's own task into its output** — so the sanitized probe
  reported that task as the action the content directed, establishing a floor
  that suppressed the contrast

Fixed by rewriting the prompt to delete whole clauses, forbid adding any sentence
not already present, and keep the reader's goal out of the returned text — then
extended to cover directives phrased **declaratively** rather than as commands.

## What was deliberately *not* done

Addresses are **not** stripped from sanitized content wholesale. If every address
were removed, the sanitized probe could never reach high severity through the
target path, IE would exceed zero whenever masked severity was high **as a matter
of arithmetic**, and the causal rule would degenerate into a restatement of the
standalone rule. Addresses merely *mentioned* are preserved; an address inside a
deleted directive departs with it.

## Still open

🟡 The fixes above landed in 3B's `_sanitize_mediator`. The **separate**
`ContextSanitizer.sanitize()` still carries the old prompt weakness, and it feeds
the user-visible continuation and the [[WCR]] metric. It was left unchanged
rather than altered silently → [[Backlog]].

## Its self-report cannot replace IE

3C runs only *after* takeover is declared, so `instructions_removed` is generated
downstream of the decision it would have to replace →
[[6n — A Corpus That Can Fail]] §B.
