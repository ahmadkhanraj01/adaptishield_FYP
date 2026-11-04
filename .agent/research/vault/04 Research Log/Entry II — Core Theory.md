---
tags: [adaptishield, log]
type: log
date: 2026-03-11
---

# Entry II — Core Theory

**11 March 2026** · Volume I · *"Task 2 — Understanding the Core Theory"*

Vocabulary-building. Three concepts defined before any implementation:

1. **[[Adaptive Threat Modeling]]** — dynamically updating defense strategy from
   evolving attack patterns and system behaviour, rather than fixed rules.
2. **[[Tool-Orchestrated LLM]]** — agentic AI where the LLM is the central
   decision-maker: interpret → plan → select tools → execute → respond. Named
   ChatGPT and Microsoft Copilot as the real-world instances.
3. **[[Model Context Protocol]]** — the structured communication layer, its five
   canonical components, and the new risks it introduces.

## The framing established here that survived

> The attack surface becomes significantly larger **because the LLM interacts
> with external tools**. Attackers exploit these interactions through prompt
> injection, malicious tool manipulation, and context hijacking.

That sentence is the seed of [[Indirect Prompt Injection]] — the observation that
*action capability* is what converts a text-level manipulation into a real
consequence.

## What it committed to

Integrating adaptive threat modeling with **automated adversarial testing** and
**reinforcement learning** — the two-loop structure that later became
[[Closed-Loop Adaptive Learning]].

Previous: [[Entry I — Research Proposal]] · Next:
[[Entry III — Literature Review and Proposed Architecture]].
