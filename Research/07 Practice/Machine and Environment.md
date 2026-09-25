---
tags: [adaptishield, reference, environment]
type: reference
---

# Machine and Environment

| Component | Detail |
| :--- | :--- |
| Machine | Dell Vostro 7500 |
| OS | Ubuntu 24.04.4 LTS |
| Python | **3.10.12** |
| GPU | NVIDIA GTX 1650 Ti |
| **VRAM** | **4 GB — a hard limit for GPU inference** |
| RAM | 16 GB |
| CPU | Intel i7-10750H (6 cores) |

## The constraint that shaped the architecture

**4 GB VRAM** is why:

- Models are ≤4b and split per component → [[Models in Use]]
- 7B+ models are rejected outright
- torch/GRPO training goes off-machine → [[Compute Strategy]]
- The 3D v1 heuristic exists at all — so the closed loop could be validated
  locally before any GPU work

It is also, indirectly, why [[6o — Phase 6 Executed on Kaggle]] happened: with no
local torch, half the trainer had never run.

## Packages

🔴 **`numpy==1.26.4` is a hard pin** — numpy 2.x breaks on Python 3.10.12.
`requirements.txt` is the source of truth; `installed.txt` shows drift.

```text
fastapi==0.115.5        uvicorn==0.32.1         langchain==0.3.7
langchain-community==0.3.7   langgraph==0.2.53   langchain-ollama==0.2.1
httpx==0.27.2           pydantic==2.10.3        python-dotenv==1.0.1
chromadb==0.5.23        sqlalchemy==2.0.36      psycopg2-binary==2.9.10
prometheus-client==0.21.1    cryptography==44.0.0    numpy==1.26.4
pandas==2.2.3           matplotlib==3.9.3       pytest==8.3.4
pytest-asyncio==0.24.0  rich==13.9.4            docker
```

```bash
cd ~/adaptishield && source venv/bin/activate
pip install --upgrade pip && pip install -r requirements.txt
```

## Serving

Ollama, locally. ⚠️ Verify `size_vram > 0` before trusting any campaign →
[[Traps]].

## Logs (all gitignored)

- `logs/episode_records/episodes.jsonl` — one Episode Record per request
- `logs/red_team_runs/campaign_*.json` — ASR/FPR/WCR per campaign
- `logs/campaign_checkpoint/*.jsonl` — per-case resume state
- `logs/adaptive_loop/*.json` — before/after + holdout reports
- `logs/benchmark/benchmark.json` — Phase 7 arm results
- `logs/layer5/` — `audit.html` + `decisions.jsonl`
