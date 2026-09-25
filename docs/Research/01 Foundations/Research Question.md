---
tags: [adaptishield, concept, foundation]
type: concept
---

# Research Question

**Title:** Adaptive Threat Modeling for Tool-Orchestrated Large Language Model
Systems in Model Context Protocol Architectures.

## The two questions as posed (5 March 2026)

1. Can **adaptive adversarial training** improve the robustness of MCP-based LLM
   agents against evolving toolchain-based attacks?
2. How does **adaptive** threat modeling compare with **static** threat modeling
   on [[ASR]], [[FPR]], [[WCR]], and long-term robustness under dynamic
   adversarial conditions?

## What the project can now answer

| Question | Answer as of 26 Jul 2026 |
| :--- | :--- |
| Does causal measurement detect softened injections keyword filtering misses? | **Yes** — 96.7% detection, [[6i — Masked Probe Rewrite]] |
| Does it catch attacks a simpler severity rule cannot? | **Yes** — 14/116, but only once [[Address-Free Attacks]] existed to show it |
| Does the *adaptive* layer improve detection on natural attacks? | **No** — [[The Adaptive Layer Proposes a No-Op]] |
| Is an automated apply-loop safe without a human gate? | **No** — [[Reward-Decreasing Proposals]] |
| Adaptive vs static, per layer? | **Unmeasured** — [[Phase 7 Benchmark Withdrawn]] |

Question 2 is therefore still partly open, and the honest statement is that it is
*untested in either direction*, not that the answer is negative.

## Why the negative answers are the contribution

A defense that reports "no gain" when there is no gain is more useful than one
tuned until it shows one. The adaptive layer's honest output has been a no-op at
every scale tested, and it is reported rather than tuned away. See
[[Design Lessons]].

Follows from [[Research Gap]]. Method: [[Causal Measurement Approach]].
