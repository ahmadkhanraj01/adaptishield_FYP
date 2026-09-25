---
tags: [adaptishield, reference]
type: reference
---

# Test Suite

**452 deterministic tests, ~9 seconds, no LLM / network / GPU.**

| File | n | Covers |
| :--- | :--- | :--- |
| `test_takeover_rules.py` | 9 | [[Takeover Rule Stack]] paths + IE resolution |
| `test_adaptive_threat_model.py` | 14 | 3D reward + proposal + step sizing; the [[6j-6k — The Loop Closes a Matching Gap]] demonstration |
| `test_target_match.py` | 21 | Normalized target match + keyword grounding ([[6m — The Single-Character Defect]], [[6p — Probe Hallucination Fixed at the Scorer]]) |
| `test_probe_diagnostic.py` | 11 | Root-cause tool **+ classifier ordering** (the instrument's own bug) |
| `test_corpus.py` | 22 | Corpus invariants, Wilson, IE-ablation join |
| `test_grpo_kaggle.py` | 23 | GRPO env/trainer + joint space + **no-op guard** |
| `test_layer5.py` | 20 | Human gate + dashboard escaping |
| `test_ablation.py` | 15 | Phase 7 arms + campaign checkpointing |
| `test_attribution.py` | 39 | [[Per-Layer Attribution]] ordering + the corpus invariants that keep the benchmark able to answer its own question |
| `test_spotlighting.py` | 25 | The external baseline's transforms; **no layer imports it** |
| `test_negation_scoring.py` | 24 | Negation handling for agent-chosen actions, clause-scoped; 3B's regime scorer untouched → [[The Scorer Cannot See Negation]] |
| `test_injecagent.py` | 33 | [[InjecAgent]]'s provenance, the stratum computed by 3B's **own** predicate, the sampler's determinism, and the two ways Layer 4 could absorb the whole corpus |
| `test_refusal_audit.py` | 35 | The regime-scorer exposure **asserted as-is** + the audit's parsers, guards and positive control → [[3B's Refusal Exposure Is Live and Unrealised]] |

## The division of labour

🟡 **Deterministic decision logic → `tests/`** — the four probe regimes are
patched out, so no Ollama, sub-second.

🟡 **LLM-dependent checks → `evaluation/`** — minutes, vary run-to-run. **Record
their numbers in the docs; never assert on them.**

## What the suite exists to protect

Every entry in [[Fixes A-D]] and every invariant in [[Rules and Invariants]] is
pinned here — explicitly **so that subsequent training work cannot silently
regress them**. The suite is torch-free by design so it can run on every edit,
which is also what let the torch backend go unexecuted for two entire phases →
[[6o — Phase 6 Executed on Kaggle]].

The 3 validated pipeline episodes are natural regression cases and were the seed
of Phase 9.

## Growth

8 → 22 (after [[Fixes A-D]]) → 23 → 37 → 110 → **135**.
