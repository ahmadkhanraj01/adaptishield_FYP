---
tags: [adaptishield, concept, foundation]
type: concept
---

# Tool-Orchestrated LLM

An agentic AI system in which the LLM is the central decision-maker: it
interprets a query, plans a sequence of actions, selects external tools, executes
them, and composes the result.

The distinction that matters for security is that such a system **stops being a
text generator and becomes something that acts**. It can send, delete, upload and
disclose. That is what converts a wording-level manipulation into a real-world
consequence, and it is the premise of [[Indirect Prompt Injection]].

## The five-step loop

1. Interpret the user query
2. Plan a sequence of actions
3. Select external tools (APIs, databases)
4. Execute the tools
5. Process the results and generate the final response

Step 5 feeding back into step 2 is the vulnerable seam: the tool's *output*
re-enters the context as text, indistinguishable from the user's instruction.
This is the **tool-return boundary**, and it is exactly where
[[3B Causal Analyzer]] fires.

Realised over [[Model Context Protocol]]. Defended by [[Defensive Stack]].
