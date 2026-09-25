---
tags: [adaptishield, concept, foundation]
type: concept
---

# Research Gap

Derived from three papers reviewed on 18 March 2026 — [[MCP Security Survey]],
[[Du et al — Mobile LLM Agents]], and [[Adam — Stochastic Optimization]].

> Existing security approaches for LLM-based agent systems rely on **static and
> fragmented defenses**, lacking adaptive, real-time mechanisms capable of
> responding to evolving, multi-turn, and toolchain-based adversarial attacks.

## The four shortcomings that motivate it

1. **Threat models are simplistic and isolated** — they assume predefined
   adversarial behaviour and defend it with fixed heuristics.
2. **Defenses terminate rather than continue** — a detection stops the attack
   *and* the user's task. This is the [[WCR]] problem, and the reason
   [[Safe Continuation]] is a first-class goal.
3. **Red teaming is manual and unrealistic** — motivating the [[Red Team Module]].
4. **Backend and supply-chain surfaces are underexplored** — motivating
   [[Layer 0 — Transport and Server Trust]].

## The specific measured gap

Keyword filtering is defeated by phrasing alone. An injection can arrive as a
polite request, a described routine ("the standard step for threads like this
is…"), a note about how a tool works, or a hypothetical disclaimed with "no need
to actually do it". Before the defenses in this project, detection ran at
**0/4 on two entire attack families** whose only distinguishing feature was
softened wording — see [[6i — Masked Probe Rewrite]].

That measurement is what converts the gap from a literature claim into a
falsifiable one.

Leads to [[Research Question]] and [[Causal Measurement Approach]].
