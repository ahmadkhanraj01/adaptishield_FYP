# Layer 2 — LLM Agent Control Plane

**Status:** ✅ Security Sub-layer 3A/3B/3C built & validated · 🟡 3D built,
trained, and honestly proposing a **no-op**

## Purpose

The decision-making layer. In the full architecture this hosts the Planner Agent,
Tool Selector, Execution Agent and Feedback Analyzer — but the part that actually
exists, and the part this research contributes, is the **Security and Adaptive
Sub-layer** (`security_sublayer/`).

**This is where the project's novel work lives.** Everything else in the stack is
conventional defense-in-depth: allowlists, scope checks, sandboxing. Layer 2 is
where the causal question is asked.

## Contents

| Path | Purpose | Status |
| :--- | :--- | :--- |
| `security_sublayer/` | The 3A→3B→3C→3D defense chain — see its own README for the detailed breakdown | ✅ 3A/3B built · 🟡 3C prompt rewrite pending · 🟡 3D proposes a no-op |
| `__init__.py` | Package marker | ✅ |

## The chain, and why each link exists

```
  3A  Policy Engine        cheap deterministic triage — block the obvious,
                           route high-impact tools onward
        │
  3B  Causal Analyzer      the measurement: four probe regimes → ACE / IE / DE
                           "did the untrusted content change the decision?"
        │  takeover
  3C  Context Sanitizer    strip the directive, keep the user's task alive
        │
  3D  Adaptive Threat Model   observe outcomes, propose bounded updates.
                              Never self-applies — Layer 5 gates it.
```

- **3A is first because it is cheap.** 3B costs several LLM calls per boundary
  crossing; anything a static rule can settle should not reach it.
- **3B is the contribution.** It measures *influence*, not appearance, so a
  paraphrase does not evade it. It depends on Layer 1's trusted/mediator
  partition: without that there is nothing to mask, and no counterfactual.
- **3C is what makes the system usable.** Without it a confirmed takeover can
  only be answered by a blanket block — ASR 0% at WCR 0%, which is a useless
  system. The Phase 7 ablation shows exactly this: removing 3B/3C takes WCR from
  71.4% to 0%.
- **3D proposes only.** See below.

## Current numbers

| | |
| :--- | :--- |
| Detection (3B) | **116/120 = 96.7%**, 95% CI [91.7%, 98.7%] |
| Residual misses | 4 — all `masked = 0`, i.e. **severity-function** failures |
| Threshold-reachable misses | **0** — which is why 3D's knob cannot close them |
| Catches only IE makes | **14/116** (the standalone rule would miss these) |
| FPR (external, n=60) | 3.3%, 95% CI [0.9%, 11.4%] |

## Why 3D's no-op is a result, not a failure

3D is fully built: a real GRPO trainer with a joint action space over
`ie_threshold`, `risk_threshold`, `window_size` and Policy Engine marker weights,
implemented twice (torch + pure-Python) and verified to agree exactly. It runs,
it trains, and it proposes **no change**.

That is the honest answer, for a reason the table above states precisely: **none
of the residual misses is reachable by any threshold.** They are `masked = 0` —
no signal exists for a threshold to act on. Tuning 3D until it showed a gain
would be reporting noise.

The one time it *did* find a gain, on the pre-§6n corpus, that gain reversed on
externally-authored benign data — it had learned a marker weight that looked free
only because nothing in our own benign corpus triggered it.

## What's pending

- **3C `ContextSanitizer.sanitize()`** still carries the prompt weakness 3B's
  internal sanitizer had (§6m). It feeds the user-visible safe continuation and
  the WCR metric, so it was left unchanged rather than altered silently.
- **The severity function** — diagnosed in Phase 13 and it was **not** a threshold.
  The masked probe transcribes address-free injections correctly; `_HIGH_KW` is a
  data-movement vocabulary with no word for *unlock a door* or *move money*, so the
  score is 0 — below both takeover rules at once. A grounded verb+resource
  **capability-misuse** class (`capability_scoring`, default **off**) takes the
  InjecAgent address-free stratum 13.3% → 90.0%, but only 30.0% → 43.3% on a
  held-out corpus (p = 0.125): the in-sample figure was fitting. A second flag,
  `schemeless_targets` (also **off**), fixes a real blind spot in
  `_extract_suspicious_targets` — `https?://` only, so bare hosts were invisible —
  and is left off because it buys 2 detections for 3 false positives. Both default
  off, so every committed number here reproduces.

See [`security_sublayer/README.md`](security_sublayer/README.md) for the
per-component detail.
