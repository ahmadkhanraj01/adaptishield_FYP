---
tags: [adaptishield, phase]
type: phase
status: done
date: 2026-08-08
---

# Phase 7 — Eight-Vector Benchmark

**The comparative experiment the whole thesis was framed around**: static
baseline vs full AdaptiShield vs AdaptiShield+3D, over eight attack vectors drawn
from [[Du et al — Mobile LLM Agents]] and [[MCPSecBench]].

It exists to answer the question the campaign cannot: **not "does the system
work" but "which layer is doing the work".**

## Design

Four arms of the same pipeline, with `PipelineConfig` implementing the ablation
**inside** `adaptishield_pipeline.py` rather than in the runner — so every arm
shares one code path and differs only in flags:

| Arm | Configuration |
| :--- | :--- |
| `undefended` | no defenses |
| `static_only` | [[3A Policy Engine]] + [[Layer 4 — Sandbox and Isolation]], no causal sub-layer |
| `full` | complete pipeline |
| `no_egress` | complete, minus the egress allowlist |

Files: `evaluation/vectors.py` (the 8 taxonomy vectors + coverage map + the
external benign cohort), `evaluation/attribution.py`
([[Per-Layer Attribution]]), `evaluation/benchmark.py` (the runner). Tested by
`tests/test_ablation.py` (15) + `tests/test_attribution.py` (26).

Run — **delete the checkpoint first**, cached results describe the old pipeline:

```bash
rm -rf logs/benchmark_checkpoint
python3 -m evaluation.benchmark --repeats 3     # 216 cases, ~40 min
```

## Status: ✅ done (8 Aug 2026)

**First result ⛔ withdrawn** → [[Phase 7 Benchmark Withdrawn]]: six of eight
vectors pointed at an exfiltration host, so the allowlist stopped them in **every**
arm and no detection layer could be distinguished — the arms were **equal by
construction rather than by measurement**.

**Repaired and re-run** → [[Phase 7 Repaired — The Causal Sub-Layer's Marginal Detection]]:

| Arm | [[ASR]] | 3B stops |
| :--- | ---: | ---: |
| `undefended` | 100.0% | 0 |
| `static_only` | 71.4% | **0** |
| `full` | **14.3%** | **18/21** |
| `no_egress` | 14.3% | 18/21 |

ASR **71.4% → 14.3%**, [[WCR]] 0% → 85.7%, and Layer 4 contributes **nothing
incremental** once 3B is on. Absorbable vectors went **6 of 7 → 1 of 7**.

## Known approximations

**V5 and V6 are flagged APPROXIMATED** in the coverage map, because the pipeline
consumes tool **responses**, not tool **manifests**. Screening tool descriptions
at registration ([[AutoMalTool]]'s Oracle, the Supply Chain Scanner in
[[Layer 1 — Input and Supply Chain Screening]]) would make them measurable →
[[Backlog]].

## The repair (done)

→ [[Next Task — Repair the Phase 7 Benchmark]] records the four steps and the two
defects the repair surfaced — **V7 could never fail the permission check it existed
to test**, and a `blocked` case could report `reached_tool=True`.

## ⚠️ What Phase 7 does NOT discharge

`static_only` is **our own ablation, not an external baseline**. Rules §7 requires a
published prompt-level defense (spotlighting / data-marking) on the same corpus,
seeds and model tags — that is **Phase 10**, the next task → [[Backlog]].
