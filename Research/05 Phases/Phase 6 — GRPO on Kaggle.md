---
tags: [adaptishield, phase]
type: phase
status: done
---

# Phase 6 — GRPO on Kaggle

Replace the v1 heuristic inside `propose_update()` with a real policy-gradient
loop, keeping the **same reward and the same
`LabeledEpisode → ProposedUpdate → apply_update` contract** — already pinned by
deterministic tests, so training cannot silently regress it.

## Why it was unblocked when it was

All four prerequisites from [[Fixes A-D]] had landed: the measurement carries
signal (D), the knob is non-inert (C), the reward is honest (A/B), and the loop
demonstrably closes a knob-matching gap ([[6j-6k — The Loop Closes a Matching Gap]]).

**Training a policy over a broken measurement produces a confident no-op**, so
none of this could have come first.

## The two questions it had to answer

1. **Does a knob-matching gap arise *naturally* on a larger held-out attack set?**
   → **No.** [[6l — No Natural Gap at Scale]]
2. **Does a *learned* GRPO policy beat the directional heuristic?**
   → **Moot for this knob.** With no reachable gap neither can improve detection,
   so they agree on the no-op. *That agreement is itself the valid finding — but
   it is not a comparison.*

## What was built — `evaluation/kaggle/`

| File | Role |
| :--- | :--- |
| `grpo_env.py` | Self-contained reward + threshold→verdict replay, **no project imports** (bundled into the Kaggle dataset) |
| `package_episodes.py` | Campaign `ExecutionResult`s → training JSONL; `--self-test` / `--run-campaign`; resumable via `--checkpoint-dir` |
| `grpo_train.py` | GRPO — scalar **and** joint action spaces, propose-and-verify, `--compare-backends`. Torch **and** pure-Python |
| `run_kaggle.sh` | Path A: stage + push dataset & kernel, poll, pull the `ProposedUpdate` |
| `apply_and_validate.py` | Apply via `apply_update(approved=True)`, re-run before/after + held-out |
| `test_credentials.py` | One authenticated call; **the secret is never printed** |

Pinned by `tests/test_grpo_kaggle.py` (23 tests).

## Execution

→ [[6o — Phase 6 Executed on Kaggle]]. Six attempts, five defects. Both backends
agree to **exactly zero**. **The P100 cannot run PyTorch** — the GPU premise is
retired, and it costs nothing because the workload is 0.27 s on CPU.

The honest restatement: **validated as an off-machine cross-check of two
implementations, not as accelerated training.** → [[Compute Strategy]]
