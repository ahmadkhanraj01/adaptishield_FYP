---
tags: [adaptishield, architecture, method]
type: concept
---

# Four Probe Regimes

[[3B Causal Analyzer]] runs four controlled dry-run re-executions at each
tool-return boundary, using **cached** tool responses so nothing is re-invoked.
Each is sampled `k_samples` times and scored `{0, 1, 2}`.

| Regime | Sees | Isolates |
| :--- | :--- | :--- |
| `orig` | user goal + mediator | baseline behaviour |
| `masked` | **mediator only, no task** | pure compliance tendency |
| `masked_sanitized` | sanitized mediator only | compliance after [[3C Context Sanitizer]] |
| `orig_sanitized` | user goal + sanitized mediator | task behaviour after sanitisation |

Contrasts → [[ACE IE DE]].

## The masked probe is the core

Shown **only** untrusted content and no task, if the model proposes moving data
or contacting a new recipient, **that is takeover on its own terms**. There is no
user goal that could have motivated it.

This is also the most delicate object in the system:

- Its wording was rewritten to refuse softened escape hatches — the single
  largest detection gain in the project ([[6i — Masked Probe Rewrite]])
- That deliberate **compliance bias** then caused it to fabricate an action on a
  benign document ([[6p — Probe Hallucination Fixed at the Scorer]])
- 🔴 Three attempts to fix the fabrication *in the prompt* cost **8 detections**
  and were reverted. The prompt is **not to be tuned again** without a strong
  reason → [[Rules and Invariants]]

## The general lesson from that

> **Prefer the fix whose failure mode you can bound.**

A prompt that is load-bearing for detection trades one *measured* false positive
against an unknown number of *unmeasured* false negatives — and that trade cannot
be evaluated from the thing you were trying to fix. The repair shipped one layer
down, in the severity function, where the check is **monotone**: it can only ever
withhold an escalation, never create one.
