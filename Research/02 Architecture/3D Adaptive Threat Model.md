---
tags: [adaptishield, architecture, component, sublayer]
type: component
status: partial
---

# 3D Adaptive Threat Model

`layer2/security_sublayer/adaptive_threat_model.py` — the adaptive component.
Trainer in `evaluation/kaggle/grpo_train.py`.

```
labeled episodes ─▶ compute_reward ─▶ evaluate_batch ─▶ propose_update ─▶ [HUMAN] ─▶ apply_update
```

## Four hard invariants

1. 🔴 **Never touches LLM weights.** Tunes only [[3A Policy Engine]]
   `blocked_patterns` / `high_impact_tools` and [[3B Causal Analyzer]]
   `ie_threshold`.
2. 🔴 **`apply_update` requires `approved=True`.** 3D proposes;
   [[Layer 5 — Human in the Loop]] disposes.
3. 🔴 **Trains on labelled data only** — red-team `ExecutionResult`s or labelled
   telemetry replay. Inferring the label from the outcome is circular.
4. 🔴 **No literal exfil targets in proposals** — that is memorization, and it
   inflated the before/after comparison in [[6d — Adaptive Loop Negative Result]].

Reward: [[GRPO Reward Function]]. Algorithm: [[MCP-RiskCue]].

## The action space

Widened from a scalar to **5 dimensions / 720 joint actions** (IE threshold,
drift risk threshold, drift window size, screener marker weights), of which 668
were sampled rather than enumerated.

🟡 **Two dimensions are unidentifiable** — reward is exactly flat in
`risk_threshold` and `window_size`, because campaigns assign a unique
`session_id` per case so the temporal-drift rule never accumulates history. The
trainer **reports this itself**, which is preferable to learning a spurious
preference over knobs the data cannot constrain. Multi-turn sessions would make
them learnable for the first time → [[Backlog]].

## Propose-and-verify

Because the policy repeatedly proposed regressions ([[Reward-Decreasing Proposals]]),
three guards were added:

- **1-D:** the grid is 5 points, so the decision is taken from the **exact reward
  table** (a regression guard for the scalar case only — explicitly *not* the
  decision rule in the joint space)
- **Joint:** the policy proposes, the trainer **verifies**, accepting only when
  reward **strictly exceeds** the incumbent
- **Minimality pass:** each altered dimension is reverted independently and the
  reversion retained wherever reward does not fall

## The honest output

[[The Adaptive Layer Proposes a No-Op]]. Its learned distribution is
**near-uniform** — the argmax comes from the minimal-intervention tie-breaker,
not from data. It should not be presented as a trained policy while the corpus
leaves it nothing to learn.
