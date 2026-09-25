# AdaptiShield — Architecture

**What this file is:** the structural map of the system: the five modules, the Defense Engine's internal stages, which file owns each part, how a request flows through them, and the design of the backend API, live event stream, database and frontend. For *why* it is built this way see [Design.md](Design.md); for rules that must not be broken see [Rules.md](Rules.md); for the build plan see [Phase.md](Phase.md).

Components marked **(planned)** are designed here and built in the phase named in [Phase.md](Phase.md).

---

## 1. System overview

Five modules share one backend. The **Tools** box is not a module; it is the email, file and API actions being protected.

```
                        ┌──────────────────────────── React Frontend (planned) ─────────────────────────────┐
                        │  Live Defense Monitor (4) │ Attack Lab UI (2) │ Admin Console & Analytics (5)     │
                        └──────────────▲────────────────────────▲─────────────────────────▲─────────────────┘
                                WebSocket events           REST (JSON)                REST (JSON)
                        ┌──────────────┴────────────────────────┴─────────────────────────┴─────────────────┐
                        │                          FastAPI Backend (planned)                                │
                        │   /ws/episodes   /api/episodes   /api/attacks   /api/proposals   /api/analytics   │
                        └──────┬──────────────────────┬────────────────────────────┬──────────────────────┬─┘
                               │                      │                            │                      │
 ┌─────────────────────┐   proposed action   ┌────────▼──────────────────┐   allowed action   ┌───────────┴──┐
 │ (1) Protected Demo  │ ──────────────────▶ │   (3) DEFENSE ENGINE      │ ─────────────────▶ │    Tools     │
 │     Agent (planned) │                     │   adaptishield_pipeline   │                    │ mail · files │
 └──────────▲──────────┘                     │   layer0 … layer4         │                    │ · APIs (sim) │
            │ planted attack                 └────────┬──────────────────┘                    └──────────────┘
 ┌──────────┴──────────┐                              │ episodes, stage verdicts, proposals
 │ (2) Attack Lab      │                     ┌────────▼──────────┐        ┌──────────────────────┐
 │     (planned)       │                     │   PostgreSQL      │        │ Ollama (local host)  │
 └─────────────────────┘                     │   (planned)       │        │ gemma3:4b qwen2.5:3b │
                                             └───────────────────┘        └──────────────────────┘
```

| # | Module | Location | Status |
| :-: | :--- | :--- | :--- |
| 1 | Protected Demo Agent | `agent/` | planned (Phase 3) |
| 2 | Attack Lab | `attack_lab/` + frontend page | planned (Phase 3–4); attack data and runner exist in `red_team/` |
| 3 | Defense Engine | `adaptishield_pipeline.py`, `layer0/`–`layer4/`, `layer2/security_sublayer/` | **built**; service wrapper planned (Phase 2) |
| 4 | Live Defense Monitor | `frontend/` + `/ws/episodes` | planned (Phase 2 stream, Phase 4 UI) |
| 5 | Admin Console & Analytics | `layer5/` + `frontend/` | approval logic **built** in `layer5/`; web UI planned (Phase 4) |

---

## 2. The Defense Engine: layered stack

Every proposed action passes top to bottom through independent layers. Each layer can stop or change the request, and **no layer trusts another layer's verdict**.

```
Layer 5  Human-in-the-loop & oversight   (governance · review gate · audit)        [built — web UI planned]
Layer 4  Sandbox & isolation              (permission · egress · sandbox · telemetry)[built]
Layer 3  Tool execution plane             (tool-response screener)                   [built]
Layer 2  Agent control plane
         └─ Security sub-layer            3A policy → 3B causal → 3C sanitize → 3D adapt   [built]
Layer 1  Input screening & provenance     (trusted vs untrusted content)             [built]
Layer 0  Transport & server trust         (server allowlist · rug-pull detection)    [built]
```

### Components and their files

| Layer | Component | File | Role |
| :--- | :--- | :--- | :--- |
| 0 | Server Trust Registry | `layer0/server_trust_registry.py` | Server allowlist and rug-pull (tool definition changed) detection |
| 1 | Provenance / Context | `layer1/provenance.py` | Tags content as trusted (user) or untrusted (mediator: email, file, tool response) |
| 2·3A | Policy Engine | `layer2/security_sublayer/policy_engine.py` | Static rules → `approve_direct`, `send_to_causal` or `block`; owns blocked patterns and the high-impact tool list |
| 2·3B | Causal Analyzer | `layer2/security_sublayer/causal_analyzer.py` | The causal check: runs the decision with the untrusted content shown vs hidden or sanitized, and decides whether it took over the action |
| 2·3C | Context Sanitizer | `layer2/security_sublayer/context_sanitizer.py` | Strips injected instructions and derives a safe continuation of the user's task |
| 2·3D | Adaptive Threat Model | `layer2/security_sublayer/adaptive_threat_model.py` | Learns from labeled episodes and **proposes** bounded rule/threshold changes; cannot apply them without approval |
| 3 | Tool Response Screener | `layer3/tool_response_screener.py` | Flags suspicious instructions in tool output (LLM check plus a keyword backstop) |
| 4 | Permission Control | `layer4/permission_control.py` | Is this tool in scope for this task? |
| 4 | Network Egress Filter | `layer4/network_egress_filter.py` | Is this destination on the allowlist? |
| 4 | Sandbox | `layer4/sandbox.py` | Isolated command execution, only after permission **and** egress pass |
| 4 | Telemetry Stream | `layer4/telemetry_stream.py` | Writes one Episode Record per request |
| 5 | Governance | `layer5/governance.py` | Recomputes the evidence for a proposal (incumbent vs proposed) from data, never trusting the proposal's own numbers |
| 5 | Review gate | `layer5/review.py` | Approve or reject a proposal; append-only decision log |
| 5 | Audit report | `layer5/audit_report.py` | Self-contained HTML audit dashboard (to be replaced by the web Admin Console) |
| — | Pipeline | `adaptishield_pipeline.py` | `AdaptiShieldPipeline` wires the layers; `PipelineConfig` switches layers on and off |
| — | Spotlighting baseline | `baselines/spotlighting.py` | Prompt-level comparison defense, run as a `PipelineConfig` arm |
| — | Shared helpers | `utils/parsing.py`, `utils/hashing.py` | Action extraction; prompt fingerprints |

---

## 3. Request flow

```
AdaptiShieldPipeline.process_request(user_input, tool_response, tool_name,
                                     proposed_action, server_name, destination_url,
                                     command, session_id)
  │
  ├─ L1  Provenance tagging         trusted (user) vs untrusted (tool_response)
  ├─ L3  Tool-response screener     flagged?  (LLM verdict OR keyword backstop)
  ├─ 3A  Policy engine              block ──────────────────────────────▶ BLOCKED
  │                                 approve_direct (low impact, not flagged) ─▶ L4
  │                                 send_to_causal (high impact or flagged)
  ├─ 3B  Causal check               no takeover ────────────────────────▶ L4 (approved_causal)
  │                                 takeover
  ├─ 3C  Sanitizer                  strip injection → safe continuation ─▶ L4 (safe_continuation)
  │                                 (if sanitizer is disabled → BLOCKED)
  ├─ L4  Permission → Egress → Sandbox   each gates independently
  └─ Telemetry                      Episode Record written (and, planned, a DB row + WebSocket events)
```

**Final statuses:** `approved_direct`, `approved_causal`, `safe_continuation`, `blocked`.

---

## 4. Inside the causal check (3B)

The causal check does not ask "does this text look dangerous?". It asks **"did the untrusted text cause this action?"** It runs the model under four views of the input, each sampled `k_samples` times (default 2), and scores each proposed action 0 (harmless), 1 (suspicious) or 2 (harmful).

| View | The model sees | Purpose |
| :--- | :--- | :--- |
| `orig` | user goal + untrusted content | the normal decision |
| `masked` | untrusted content only, no task | does the content on its own push toward an action? |
| `masked_sanitized` | sanitized content only | same, after the injection is stripped |
| `orig_sanitized` | user goal + sanitized content | the task's decision after sanitizing |

Contrasts between the views: `ACE = orig − masked`, `IE = masked − masked_sanitized`, `DE = orig_sanitized − masked_sanitized`.

An action scores **2 (harmful)** when it copies a target (email address or URL) from the untrusted content, or when it moves data in a way the untrusted content suggested.

**Takeover** is declared if any of these fire:
1. **IE rule:** sanitizing clearly reduced compliance (`IE ≥ threshold`), consistently across every sample.
2. **Standalone rule:** the content alone produced a harmful action (`masked ≥ 2`), whatever IE says.
3. **Drift rule:** compliance is rising over the same conversation (`session_id`), and something was actually observed (`masked ≥ 1`).

The rules live in `_decide_takeover` and are pinned by `tests/test_takeover_rules.py`.

---

## 5. The adaptive component and the human gate (3D + Layer 5)

```
labeled episodes ─▶ reward ─▶ evaluate batch ─▶ propose_update ─▶ governance recomputes evidence ─▶ ADMIN ─▶ apply_update
                                                  (bounded change)                                    approve/    (approved=True
                                                                                                      reject      required)
```

- 3D only tunes **static settings**: 3A blocked patterns and high-impact tools, and 3B's IE threshold. It never touches model weights.
- The reward favors **stripping the injection and continuing** (+1.0) over **blocking** (+0.7), so the system prefers keeping the user's task alive.
- `apply_update` refuses to run without `approved=True`. In the FYP, that approval comes from an Admin in the web console (Module 5), and every decision is stored with who, when and why.

---

## 6. Backend API (planned, Phase 2)

FastAPI service in `backend/`. All endpoints are JSON; interactive docs are at `/docs`.

| Method & path | Role | Purpose |
| :--- | :--- | :--- |
| `POST /api/auth/login` | any | Get a JWT |
| `POST /api/episodes` | Tester | Send one request through the engine (protection on/off selectable) |
| `GET /api/episodes` | Analyst | List episodes (filters: status, attack type, date) |
| `GET /api/episodes/{id}` | Analyst | One episode with all stage verdicts (used by Replay) |
| `POST /api/agent/run` | Tester | Run the demo agent on a mailbox scenario |
| `GET /api/attacks` | Tester | Browse the attack catalogue (InjecAgent, AgentDojo, custom) |
| `POST /api/attacks` | Tester | Save a custom attack |
| `POST /api/attack-lab/compare` | Tester | Run one attack with protection off and on |
| `POST /api/attack-lab/batch` | Tester | Run all attacks of a type; progress over WebSocket |
| `GET /api/proposals` | Admin | Pending and past configuration proposals |
| `GET /api/proposals/{id}` | Admin | Proposal with recomputed evidence |
| `POST /api/proposals/{id}/decision` | Admin | Approve or reject, with a reason |
| `GET /api/policy` | Analyst | Current rules and thresholds |
| `GET /api/analytics/summary` | Analyst | ASR, TPR, FPR, WCR per attack type and per setup, with intervals |
| `GET /api/health` | any | Backend, database and Ollama status |

---

## 7. Live event stream (planned, Phase 2)

`WS /ws/episodes` pushes one event per stage as the engine runs, so the Monitor can light each stage up in order.

```json
{
  "episode_id": "b7e2…",
  "seq": 4,
  "stage": "causal_check",
  "verdict": "takeover",
  "detail": {
    "run_a_action": "forward_email to attacker@example.com",
    "run_b_action": "summarize_thread",
    "changed": true,
    "rule": "standalone"
  },
  "timestamp": "2027-03-10T09:14:22Z"
}
```

`stage` is one of `received`, `provenance`, `screener`, `policy`, `causal_check`, `sanitizer`, `permission`, `egress`, `sandbox`, `final`. The `final` event carries the status (`approved_direct`, `approved_causal`, `safe_continuation`, `blocked`). Replay re-emits a stored episode's events in the same format.

---

## 8. Database (planned, Phase 2)

PostgreSQL, SQLAlchemy models, Alembic migrations.

| Table | Key columns |
| :--- | :--- |
| `users` | id, name, email, role (`tester`, `analyst`, `admin`), password_hash |
| `attacks` | id, source (`injecagent`, `agentdojo`, `custom`), attack_type, user_task, injected_text, target, is_benign |
| `episodes` | id, attack_id, config (`none`, `spotlighting`, `full`), user_input, final_status, started_at, finished_at, session_id |
| `stage_events` | id, episode_id, seq, stage, verdict, detail (JSONB), timestamp |
| `proposals` | id, created_at, change (JSONB), proposal_reward, incumbent_reward (recomputed), status |
| `approvals` | id, proposal_id, admin_id, decision, reason, decided_at (**append-only**) |
| `evaluation_runs` | id, corpus, config, model_tags, commit_sha, metrics (JSONB), created_at |

Untrusted text (injected emails, tool responses) is stored as data and is never interpreted.

---

## 9. Frontend (planned, Phases 3–4)

React + Vite, Tailwind CSS, Recharts, React Router, TanStack Query. Lives in `frontend/`.

| Page | Module | Shows |
| :--- | :--- | :--- |
| Login | — | Role-based sign-in |
| Live Monitor | 4 | Live feed; pipeline view that lights up stage by stage; causal-check panel (Run A vs Run B) |
| Episode Detail / Replay | 4 | All stage verdicts for one episode; step-by-step replay |
| Attack Lab | 2 | Attack catalogue, custom attack editor, on/off side-by-side result, batch runs |
| Demo Agent | 1 | Mock inbox; what the user asked, what the agent proposed, what actually ran |
| Admin Console | 5 | Pending proposals, recomputed evidence, approve/reject, decision history, current policy |
| Analytics | 5 | ASR / TPR / FPR / WCR per attack type and per setup, trends, CSV export |

```
frontend/src/
  api/          REST client, WebSocket hook
  components/   StageBadge, VerdictChip, EpisodeCard, PipelineView, ChartCard …
  pages/        Monitor, Replay, AttackLab, Agent, Admin, Analytics, Login
  hooks/        useEpisodeStream, useAuth
```

---

## 10. Deployment (planned, Phase 6)

```
docker compose up
  ├─ frontend   (Nginx serving the Vite build)      :80
  ├─ backend    (FastAPI + Uvicorn)                 :8000
  └─ postgres                                        :5432
Ollama runs on the host (GPU access): gemma3:4b, qwen2.5:3b   :11434
```

---

## 11. Models

| Model | Role | Why |
| :--- | :--- | :--- |
| `gemma3:4b` | Causal check (3B) | It follows injected instructions when shown the content alone, which is exactly what makes the with/without difference measurable |
| `qwen2.5:3b` | Sanitizer (3C), screener (L3), agent planner | More resistant to injections as a planner; good at rewriting |

Both run locally through Ollama on a 4 GB GPU. There is no cloud API.

---

## 12. Evaluation and data

| Folder | Contents |
| :--- | :--- |
| `red_team/data/` | InjecAgent (510 attacks), AgentDojo (253 attacks, 60 benign documents) |
| `red_team/` | Attack library, execution agent, evaluator, campaign runner, dataset import scripts |
| `evaluation/` | Benchmark runner (setups as `PipelineConfig` arms), metrics (ASR, TPR, FPR, WCR), confidence intervals, paired tests |
| `results/` | Committed evaluation outputs with run manifests |
| `logs/` | Local run logs and Episode Records (git-ignored) |
