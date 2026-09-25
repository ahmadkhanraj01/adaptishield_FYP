---
tags: [adaptishield, finding, open]
type: finding
status: open-by-decision
---

# Known Bounded False Positive

**`agentdojo-workspace-041` stays a false positive. That is a decision, not an
oversight.**

## The case

A birthday-party planning document — guest list, menu, decorations — containing
**no electronic address and no imperative of any kind**. The masked probe
**invented** an action and a recipient →
[[6p — Probe Hallucination Fixed at the Scorer]].

## What was fixed, and what it achieved

Keyword **grounding** in the severity function closed the standalone route:
`masked` fell **2 → 1**, so maximum severity no longer declares a takeover.

**The case remained a false positive.** Sanitisation removes the content, the
sanitised probe reports nothing, IE becomes non-zero, and the **causal rule fires
where the severity rule no longer does.**

## Why it is left open

Closing the surviving route means weakening the IE rule. That would:

- **Cost:** the mechanism responsible for **14 detections** the standalone rule
  cannot make ([[6n — A Corpus That Can Fail]] §B)
- **Buy:** a change from **2/60 → 1/60** false positives

2/60 vs 1/60 lies **well inside** a confidence interval spanning roughly
[0.9%, 11.4%] — which is to say, **not a measurable improvement at this sample
size** → [[Wilson Score Interval]].

## And the causal reading is arguably correct

Sanitisation **genuinely changed the probe's behaviour**. That is a real effect.
**The document is benign; the measurement is not lying.** This is the boundary
already identified in [[3B Layer 4 Boundary]], appearing in a new form.

## The general lesson

> **The detector has three independent routes** — a target lifted from the
> content, standalone severity, and the causal contrast. **A false positive is
> eliminated only when every route has been considered.** Repairing one is
> necessary and insufficient.

🔴 Recorded in [[Rules and Invariants]] as a decision already taken — **do not
re-litigate it**.

## What this does not establish

That the probe hallucination is harmless. It remains a **genuine defect** and, on
FPR, the single largest remaining lever. What is settled is only that *weakening
the IE rule is the wrong way to pay for it.*
