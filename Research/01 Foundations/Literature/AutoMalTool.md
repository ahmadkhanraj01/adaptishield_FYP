---
tags: [adaptishield, literature]
type: literature
---

# AutoMalTool

Source of two things in AdaptiShield.

## 1. The detection oracle

The **Supply Chain Scanner** in [[Layer 1 — Input and Supply Chain Screening]]
implements an LLM-based detection oracle modelled on AutoMalTool's Oracle
component: it statically analyses MCP tool metadata — name, description, input
schema — for tool-poisoning indicators *before* the tool is registered, looking
for imperative language, priority overrides, hidden instructions, and
tool-capability directives.

This is the check that would have to run for benchmark vectors V5/V6 to be
measured rather than approximated — see [[Backlog]], "screen tool descriptions at
registration". The pipeline currently consumes tool **responses**, not manifests.

## 2. The red-team optimization loop

The four-agent structure of the [[Red Team Module]] — Generator → Execution →
Evaluator → **Optimizer** — follows AutoMalTool's loop, in which the Evaluator's
scores feed back to refine attack strategies into progressively harder examples.

In this project the Optimizer is the keyword-softening mutator that produces
gen-2 attacks, and it is the component that produced the project's founding
empirical result: softening collapsed causal detection from 2/4 families to
**0/4**. See [[Entry X — From Architecture to Working Prototype]].
