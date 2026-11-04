---
tags: [adaptishield, concept, foundation, method]
type: concept
---

# Causal Measurement Approach

**The methodological core of the project.**

Rather than asking *"does this text look dangerous?"*, AdaptiShield asks:

> **Did the untrusted content change what the agent decided to do?**

## How the question is made answerable

The agent's proposed action is probed under several conditions — with the
untrusted content present, with it masked out, and with it sanitised — and the
*differences* between those runs are treated as the measurement. See
[[Four Probe Regimes]] and [[ACE IE DE]].

The key quantity is the **Indirect Effect**: how much the agent's behaviour
shifts when the suspect content is removed. A high IE means the content, not the
user, drove the action.

## Why this evades paraphrase attacks

It is **behavioural evidence rather than a judgement about wording**. Softening
the phrasing does not reduce the influence, so it does not reduce the signal.
That is the property [[Indirect Prompt Injection]] defeats keyword filters with,
and the reason this approach exists.

## What it depends on

- **A trusted/untrusted partition** — without it there is nothing to mask and
  therefore no counterfactual. [[Layer 1 — Input and Supply Chain Screening]] is
  load-bearing for the whole method.
- **A model that complies under the masked probe** — a maximally refusal-prone
  model produces *no* divergence and therefore no signal. This is why
  [[Models in Use]] splits models per component rather than picking the "safest".

## Where it is fragile

- **A difference metric can invert.** If the sanitizer fails, both regimes comply,
  the scores cancel, and a surviving attack reads as safe →
  [[Takeover Rule Stack]] rule 2 exists for exactly this.
- **Component accuracy ≠ contrast accuracy.** Scoring each action *more*
  accurately made the system *worse* → [[6e — Semantic Scoring Ablation]].
- **The probe can hallucinate an action on benign content** →
  [[6p — Probe Hallucination Fixed at the Scorer]].

Implemented by [[3B Causal Analyzer]].
