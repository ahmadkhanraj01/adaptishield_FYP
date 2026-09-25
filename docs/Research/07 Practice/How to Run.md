---
tags: [adaptishield, reference]
type: reference
---

# How to Run

## Deterministic — no LLM, no network, no GPU

```bash
python3 -m pytest tests/ -q                       # 343 tests, ~7s
python3 -m evaluation.mechanism_validation        # causal regimes + takeover rules, <1s
python3 -m layer2.security_sublayer.adaptive_threat_model   # 3D reward + proposal demo
python3 -m evaluation.vectors                     # Phase 7 vector coverage map
```

## Per-component smoke tests

```bash
python3 layer0/server_trust_registry.py           # legit True, rug-pull False
python3 layer1/provenance.py                      # trusted + mediator partitions
python3 layer2/security_sublayer/policy_engine.py # approve_direct / send_to_causal / block
python3 layer3/tool_response_screener.py          # clean vs FLAGGED
python3 layer4/permission_control.py              # in-scope True, out-of-scope False
python3 layer4/network_egress_filter.py           # allowlisted True, else False
python3 layer4/telemetry_stream.py                # episode appended to JSONL
```

## Needs Ollama + `gemma3:4b`

```bash
python3 adaptishield_pipeline.py                  # full pipeline, 3 validated cases
python3 -m red_team.run_campaign                  # red-team campaign (gen1 + gen2)
python3 -m evaluation.adaptive_loop_experiment    # before/after applying a 3D proposal
python3 -m evaluation.holdout_generalization_test # same update vs an unseen address
python3 -m evaluation.score_action_ablation       # keyword vs semantic 3B scoring

python3 -m evaluation.kaggle.package_episodes --run-campaign   # 1.5-2h; resumable

# Phase 7 — 216 cases (18 vectors x 3 repeats x 4 arms), ~40 min. Resumable.
rm -rf logs/benchmark_checkpoint
python3 -m evaluation.benchmark --repeats 3
python3 -m evaluation.benchmark --arms undefended,full --repeats 1   # quick subset
python3 -m evaluation.benchmark --corpus campaign \
        --arms derived_control,spotlighting --repeats 1               # Phase 10, ~12 min
python3 -m evaluation.benchmark --preset ladder --repeats 3            # Phase 11, ~1.5 h
python3 -m evaluation.benchmark --preset loo    --repeats 3            # Phase 11 LOO, ~1.5 h
python3 -m red_team.vendor_injecagent                                  # once, needs network
python3 -m evaluation.benchmark --corpus injecagent \
        --arms undefended,static_only,full --repeats 1                 # Phase 12, ~30 min
```

⚠️ **Delete `logs/campaign_checkpoint/` and `logs/benchmark_checkpoint/` after
changing the pipeline** — cached results describe the old code → [[Traps]].

The two 3B arms (`full`, `no_egress`) carry ~96% of the benchmark's runtime, at
~25 s per case against ~1–3 s for `undefended` / `static_only`. Results land in
`logs/benchmark/benchmark.json` with provenance in `manifest.json`.

## Analysis — reads existing results, no LLM

```bash
python3 -m evaluation.fpr_report      # FPR by cohort + Wilson intervals — READ THE STALE HEADER
python3 -m evaluation.ie_ablation     # is IE redundant with 3C's self-report?
python3 -m evaluation.probe_diagnostic # root-cause a 3B miss
python3 -m evaluation.refusal_audit   # does refusal-shaped output inflate 3B's severities? 0/209
```

`refusal_audit` needs `logs/benchmark/run.log` and `logs/probe_diagnostic/*.json`,
which are **gitignored** — a fresh clone reports nothing until [[Phase 7 — Eight-Vector Benchmark|Phase 7]]
or the probe diagnostic has been run. Re-run it after any change to the regime
scorer, the negation cues, or the vector mediators →
[[3B's Refusal Exposure Is Live and Unrealised]].

## Layer 5 — human in the loop

```bash
python3 -m layer5.audit_report --open  # build + open the audit dashboard
python3 -m layer5.review               # review a 3D proposal (interactive gate)
python3 -m layer5.review --list        # decision history
```

## GRPO training

```bash
python3 evaluation/kaggle/test_credentials.py     # secret never printed
bash evaluation/kaggle/run_kaggle.sh              # push dataset + kernel, poll, pull
python3 -m evaluation.kaggle.grpo_train --episodes <path>
```

Needs a **legacy 32-hex Kaggle key** in a git-ignored `.env` or `kaggle.json` →
[[Traps]].

## Quick health check

```bash
python3 -m pytest tests/ -q          # expect 135 passed, ~2s
python3 -m evaluation.fpr_report     # check the STALE header first
curl -s localhost:11434/api/ps       # size_vram must be > 0
```
