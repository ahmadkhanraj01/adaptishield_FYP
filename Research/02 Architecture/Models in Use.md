---
tags: [adaptishield, architecture, environment]
type: reference
---

# Models in Use

| Model | VRAM | Used by |
| :--- | :--- | :--- |
| **`gemma3:4b`** | ~3.5 GB | [[3B Causal Analyzer]] |
| **`qwen2.5:3b`** | ~2 GB | [[3C Context Sanitizer]], [[Layer 3 — Tool Execution Plane]] screener, planner |
| `gemma2:9b` | CPU | Fallback for 3B at scale |

Rejected: `llama3.2:3b` (poor security reasoning); any 7B+ GPU model (exceeds the
4 GB ceiling — see [[Machine and Environment]]).

## The counter-intuitive decision

🔴 **The per-component model split is an invariant.**

3B runs `gemma3:4b` **because it complies** with injections under the masked
probe, producing a measurable causal signal. `qwen2.5:3b` refuses injected
instructions so completely — even under the hypothetical masked probe — that
**no causal divergence is observable and there is no detection signal at all.**

> **A model that refuses everything makes a *worse* detector.**

The more injection-resistant model is retained where resistance is what you want:
the sanitizer, the screener, and the planner. This is a deliberate per-component
assignment, **not** a global swap, and swapping in a more refusal-prone model on
3B destroys the mechanism.

Related: [[Causal Measurement Approach]], [[Four Probe Regimes]].

## Serving

Ollama, locally. ⚠️ After a CUDA fault Ollama silently falls back to **CPU-only**:
~11 GB RAM, slower, more non-determinism, and **different outputs**. Check
`curl -s localhost:11434/api/ps` → `size_vram` must be > 0. See [[Traps]].
