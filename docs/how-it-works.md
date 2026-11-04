---
hide: [navigation]
---

# How it works

AdaptiShield sits between an AI agent and its tools. The agent proposes, the engine decides, and tools run only what the engine allows.

## The stages

| Stage | What it does |
| :--- | :--- |
| **Provenance** | Separates trusted content (the user's request) from untrusted content (anything a tool returned) |
| **Screener** | Looks for suspicious instructions in tool output, using a model check and a keyword backstop |
| **Policy** | Blocks known patterns. Sends high-impact actions or flagged content to the causal check, and approves the rest |
| **Causal check** | Tests whether the untrusted content caused the action |
| **Sanitizer** | If it did, removes the injection and plans a safe action, so the user's task can continue |
| **Permission and egress** | Limits which tools and destinations are allowed, whatever the earlier stages decided |

## The causal check

Instead of only judging how the text looks, the causal check runs the model on four views of the input, and scores the action each view produces.

| View | The model sees | The question it helps answer |
| :--- | :--- | :--- |
| Normal | The user's goal and the content | What would the agent do? |
| Content only | The content, with no task | Does the content push toward an action on its own? |
| Sanitized content only | The cleaned content, with no task | Does that push go away once the injection is removed? |
| Goal and sanitized content | The user's goal and the cleaned content | What is the task's decision after cleaning? |

A **takeover** is declared if any of three rules fires:

1. **Sanitizing clearly reduced compliance**, consistently across samples.
2. **The content alone produced a harmful action**, whatever else was seen.
3. **Compliance is rising** over the same conversation.

!!! note "Where it is strong and where it is weak"
    The check works best when the injected action copies a target from the content, such as an email address or URL. It is much weaker when the attack names no such target. This is why results are reported by attack type and target rather than as one overall number. See [Evaluation](evaluation.md).

## The three outcomes

| Outcome | When | What happens |
| :--- | :--- | :--- |
| **Approved** | Nothing suggests the content caused the action | The action continues to the permission and egress limits |
| **Injection removed, task continued** | The content took over, and it can be cleaned | The user still gets a safe result |
| **Blocked** | A blocked pattern matched, or the content cannot be cleaned | The action is refused |

Even an approved action can be stopped by the permission and egress limits. So the engine reports separately whether the tool may run.

## One request, end to end

![Sequence of one injected email from the user through the agent, backend, engine, local models, database and monitor](assets/diagrams/sequence.png)

## People stay in control

The system can suggest changes to its own rules and thresholds, but it cannot apply them. An Admin sees evidence that the server recomputes from data, not the suggestion's own claims. Each decision needs a reason and is stored permanently with who made it and when.
