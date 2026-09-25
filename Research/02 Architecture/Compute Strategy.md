---
tags: [adaptishield, architecture, environment]
type: reference
---

# Compute Strategy

| Task | Platform | Reason |
| :--- | :--- | :--- |
| Pipeline logic, debugging, red-team campaigns | **Local** | Fast, free, offline |
| GRPO / RL training (3D) | **Kaggle** | Needs torch |
| Red-team dataset generation at scale | Kaggle | Speed |
| Full benchmark | Kaggle | Reproducible, logged |

## The hard boundary

```
LOCAL (this machine)                     KAGGLE (training/eval only)
────────────────────                     ───────────────────────────
run pipeline + red-team campaigns        GRPO training (torch) over the
  → generate LABELED EPISODES     ──►      labeled episodes, same reward
apply the trained ProposedUpdate   ◄──   → emits a ProposedUpdate
  via existing apply_update()               (ie_threshold, patterns, tools)
  then re-run campaigns locally
```

**Kaggle cannot host the pipeline** — no Ollama, no MCP server. The
`LabeledEpisode → ProposedUpdate → apply_update` seam is exactly what lets
training live elsewhere and the result come back. Nothing about the local
pipeline changes.

## The premise that turned out to be false

The phase was framed throughout as *training on a free P100*. It is not possible:
the **P100 is compute capability sm_60** and the Kaggle torch build requires
sm_70+, so the first tensor allocation fails. Worse, `torch.cuda.is_available()`
returns **True** — it answers whether a driver and visible device exist, not
whether the build can execute on them — so the failure arrives at allocation
rather than at the capability check.

`_torch_device()` now probes with a **real allocation** and falls back to CPU,
reporting why.

**Nothing of substance is lost.** The joint search is a few thousand
floating-point operations over a 188-row table and completes in **~0.27 s on one
core**. Kaggle's value here is that *torch is importable there* — not compute.
See [[6o — Phase 6 Executed on Kaggle]].

## Path A

Kaggle is driven by API from the session (decided 2026-07-24), not by manual
notebook upload. ⚠️ The CLI needs a **legacy 32-hex key** — see [[Traps]].
