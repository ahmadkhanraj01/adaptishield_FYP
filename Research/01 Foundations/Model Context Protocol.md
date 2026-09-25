---
tags: [adaptishield, concept, foundation]
type: concept
---

# Model Context Protocol

MCP is an architectural framework for structured communication between an LLM and
external tools, services and data sources. It defines how contextual information,
tool requests and system responses are exchanged inside an agent environment.

## The canonical layers

| Layer | Role |
| :--- | :--- |
| Client | Where the user interacts |
| LLM Orchestrator | Reasons, decides which tools to call |
| Tool Execution | APIs, databases, web services |
| Context Memory | Conversation history, multi-step state |
| Policy and Security | Access control and enforcement |

AdaptiShield's own stack ([[Defensive Stack]]) is a hardened elaboration of this,
with the security layer split into [[3A Policy Engine]] → [[3B Causal Analyzer]]
→ [[3C Context Sanitizer]] → [[3D Adaptive Threat Model]].

## Why MCP enlarges the attack surface

Because the model *acts*, the attack surface spans the client, the protocol, the
server and the toolchain simultaneously. [[MCPSecBench]] demonstrates
protocol-level attacks reaching 100% ASR against every evaluated platform with no
existing countermeasure — which is the entire architectural justification for
[[Layer 0 — Transport and Server Trust]].

The specific attacks named in the 15 May survey: prompt injection, tool
poisoning, shadowing, **rug pull**, context poisoning, malicious tool
manipulation, unauthorized tool execution, and multi-turn context takeover. See
[[Threat Taxonomy]].

## The hard operational boundary

MCP needs a live server. That is why **Kaggle cannot host the pipeline** and the
split in [[Compute Strategy]] is fixed rather than convenient.

Related: [[Tool-Orchestrated LLM]], [[Indirect Prompt Injection]].
