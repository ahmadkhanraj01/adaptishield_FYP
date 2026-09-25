# AdaptiShield — Phases & Progress

**What this file is:** the FYP build plan: what each phase delivers, when, and who checks it off. Dates follow the Gantt chart in [`FYP/gantt_chart.png`](FYP/gantt_chart.png). For the structure being built see [Architecture.md](Architecture.md); for the rules every phase must respect see [Rules.md](Rules.md).

**Legend:** ✅ done · 🟡 in progress · ⬜ not started

---

## Overview

| Phase | Name | Period | Duration | Status |
| :-: | :--- | :--- | :-: | :-: |
| 0 | Proposal & First Presentation | Sep 2026 | — | 🟡 |
| 1 | Requirements & System Design | 18 Sep – 31 Oct 2026 | 44 days | 🟡 |
| 2 | Defense Engine & Backend | 1 Nov – 31 Dec 2026 | 61 days | ⬜ |
| 3 | Protected Demo Agent & Attack Lab | 1 Jan – 28 Feb 2027 | 59 days | ⬜ |
| 4 | React Frontend: Live Monitor, Admin Console & Analytics | 1 Mar – 30 Apr 2027 | 61 days | ⬜ |
| 5 | Integration & Security Testing | 1 May – 20 May 2027 | 20 days | ⬜ |
| 6 | Deployment, Documentation & Final Presentation | 21 May – 3 Jun 2027 | 14 days | ⬜ |

```
            Sep   Oct   Nov   Dec   Jan   Feb   Mar   Apr   May   Jun
Phase 1     ███████████
Phase 2                ████████████
Phase 3                            ████████████
Phase 4                                        ████████████
Phase 5                                                    ████
Phase 6                                                        ███
```

**Starting point.** The Defense Engine's detection core already exists and is tested: `layer0`–`layer5`, `adaptishield_pipeline.py` and 501 passing tests. The FYP work turns it into a complete system: a service, a demo agent, an attack lab, a React web app, a database and a deployment. The engine's decision logic is reused, not rewritten.

---

## Phase 0 — Proposal & First Presentation 🟡

**Goal:** get the project approved and presented.

- [x] FYP proposal written and submitted (`FYP/AdaptiShield_FYP_Proposal_BSCS2.pdf`)
- [x] Gantt chart (`FYP/gantt_chart.png`)
- [x] Supervisor's four points prepared: dataset, research questions, literature review, dataset feasibility (`FYP/Supervisor_Feedback.md`)
- [x] First presentation slides and speaker notes (`FYP/AdaptiShield_FirstPresentation.pptx`, `FYP/Presentation_Notes.md`)
- [ ] First presentation delivered (**Mon 28 Sep 2026, 9:00 a.m., Chairman's office**)
- [ ] Panel feedback recorded in `FYP/` and applied to this plan

---

## Phase 1 — Requirements & System Design 🟡

**18 Sep – 31 Oct 2026.** **Goal:** freeze *what* is being built before building it.

### 1.1 Requirements
- [ ] Software Requirements Specification (SRS): functional and non-functional requirements for all 5 modules
- [ ] User roles: **Tester** (Attack Lab), **Analyst** (Monitor, Analytics), **Admin** (approvals)
- [ ] Use-case diagram and main use cases (run attack, watch live verdicts, approve proposal, view analytics, replay episode)
- [ ] Acceptance criteria per module

### 1.2 System design
- [ ] High-level architecture diagram updated for the 5 modules (see [Architecture.md](Architecture.md) §1)
- [ ] Sequence diagram: one injected email from agent → engine → tools → dashboard
- [ ] **REST API contract** (OpenAPI draft) for every endpoint in [Architecture.md](Architecture.md) §6
- [ ] **WebSocket event schema** for per-stage verdicts ([Architecture.md](Architecture.md) §7)
- [ ] **Database schema** (ER diagram) for episodes, stage verdicts, attacks, proposals, approvals, users ([Architecture.md](Architecture.md) §8)
- [ ] UI wireframes for every page (Figma or hand-drawn): Monitor, Replay, Attack Lab, Admin Console, Analytics, Login

### 1.3 Project setup
- [ ] Repository structure created: `backend/`, `agent/`, `attack_lab/`, `frontend/`
- [ ] Branching and pull-request workflow agreed ([Rules.md](Rules.md) §8)
- [ ] GitHub Actions CI running `pytest` on every push
- [ ] Task split among the three team members

**Deliverable:** SRS + design document, reviewed by the supervisor.

---

## Phase 2 — Defense Engine & Backend ⬜

**1 Nov – 31 Dec 2026.** **Goal:** the engine runs as a web service that every other module talks to.

### 2.1 Engine as a service
- [ ] `backend/services/engine.py`: wraps `AdaptiShieldPipeline` with no change to its decision logic
- [ ] Engine emits a **stage event** after each stage (provenance, screener, policy, causal check, sanitizer, permission, egress, final decision)
- [ ] Remove `print()` output from the request path; use `logging` instead
- [ ] Run engine calls off the event loop (worker thread or task queue), since each LLM probe takes seconds
- [ ] Engine configuration (protection on/off, which layers enabled) is selectable per request via `PipelineConfig`

### 2.2 FastAPI backend
- [ ] `backend/main.py` app, settings from `.env` (`pydantic-settings`)
- [ ] REST endpoints: episodes, attacks, proposals, analytics, health ([Architecture.md](Architecture.md) §6)
- [ ] WebSocket endpoint `/ws/episodes` that streams stage events live
- [ ] Authentication (JWT) with the three roles; only **Admin** can approve proposals
- [ ] Auto-generated API docs at `/docs`

### 2.3 Database
- [ ] PostgreSQL schema with SQLAlchemy models and Alembic migrations
- [ ] Every episode and every stage verdict persisted (replaces JSONL-only telemetry; JSONL kept as a fallback)
- [ ] Layer 5 approval history moved from an append-only file to a database table (still append-only)

### 2.4 Containers
- [ ] `Dockerfile` for the backend
- [ ] `docker-compose.yml`: backend + PostgreSQL (Ollama runs on the host)

### 2.5 Tests
- [ ] API tests with FastAPI `TestClient` and the LLM stubbed out
- [ ] Existing engine test suite still passes unchanged

**Deliverable:** `docker compose up` starts the backend; a request through `/api/episodes` returns a verdict and streams stage events over the WebSocket.

---

## Phase 3 — Protected Demo Agent & Attack Lab ⬜

**1 Jan – 28 Feb 2027.** **Goal:** a realistic agent to protect, and a way to attack it on demand.

### 3.1 Module 1: Protected Demo Agent (`agent/`)
- [ ] Mock mailbox and document store (seeded from AgentDojo benign documents)
- [ ] Agent tools: `read_email`, `send_email`, `forward_email`, `delete_file`, `upload_file`
- [ ] Planner on `qwen2.5:3b` that reads content and **proposes** an action
- [ ] Every proposed action goes through the Defense Engine before any tool runs. The agent has no path that bypasses the engine.
- [ ] Tools are simulated: nothing is really sent or deleted; outcomes are logged
- [ ] End-to-end scenario: one injected email → blocked or sanitized → user's summary still delivered

### 3.2 Module 2: Attack Lab (`attack_lab/`)
- [ ] Attack catalogue loaded from InjecAgent and AgentDojo (`red_team/data/`), browsable by attack type
- [ ] Custom attack editor: write your own injection and choose where it is planted (email body, file, tool response)
- [ ] **On/off comparison:** same attack run with protection off and on, results side by side
- [ ] Batch runs over a whole attack type, with progress streamed over WebSocket
- [ ] Results saved to the database for Analytics

### 3.3 Backend and frontend foundation
- [ ] Endpoints for the agent and the Attack Lab
- [ ] **Frontend scaffold** (so Phase 4 starts on a working base): Vite + React + Tailwind project in `frontend/`, routing, layout, API client, login page
- [ ] Minimal Attack Lab page to drive this phase's demos

**Deliverable:** from the browser, run an InjecAgent attack against the demo agent with protection on and off and see the difference.

---

## Phase 4 — React Frontend: Live Monitor, Admin Console & Analytics ⬜

**1 Mar – 30 Apr 2027.** **Goal:** a complete web app where a person can see, test and supervise the defense.

### 4.1 Frontend foundation
- [ ] Stack: **React + Vite**, **Tailwind CSS**, **Recharts**, React Router, TanStack Query (REST), native WebSocket client with auto-reconnect
- [ ] Shared components: stage badge, verdict chip, episode card, data table, chart card
- [ ] Role-based navigation (Tester / Analyst / Admin)
- [ ] Light and dark theme; usable on a laptop screen and a projector
- [ ] **Untrusted content is always rendered as plain text**, never as HTML ([Rules.md](Rules.md) §5)

### 4.2 Module 4: Live Defense Monitor
- [ ] Live feed of requests as they arrive
- [ ] **Pipeline view:** each stage lights up as its verdict arrives (pass, flag, block)
- [ ] Causal-check panel: Run A (content visible) vs Run B (content hidden), the two actions, and whether they differ
- [ ] Details: which rule fired, what the screener flagged, the sanitized text, the final decision
- [ ] **Replay:** pick a recorded episode and play its stage events back step by step
- [ ] Filters: status, attack type, time range

### 4.3 Module 5: Admin Console
- [ ] List of pending configuration proposals from the adaptive component
- [ ] Proposal view: what changes, and the evidence **recomputed by the server** (incumbent vs proposed reward), never the proposal's own numbers
- [ ] Approve or reject, with a required reason; every decision recorded with who, when and why
- [ ] Decision history and audit log
- [ ] Current policy view: blocked patterns, high-impact tools, thresholds

### 4.4 Module 5: Analytics
- [ ] Detection rate, false-alarm rate, workflow continuation rate and attack success rate **per attack type**
- [ ] Comparison of no defense vs Spotlighting vs AdaptiShield
- [ ] Trends over time
- [ ] 95% confidence intervals shown on rates
- [ ] Export results as CSV

### 4.5 Attack Lab UI (completed)
- [ ] Attack browser, custom attack editor, side-by-side on/off results, batch runs with a progress bar

### 4.6 Frontend tests
- [ ] Component tests (Vitest + React Testing Library)
- [ ] End-to-end tests of the main flows (Playwright): login, run an attack, watch it in the Monitor, approve a proposal

**Deliverable:** the full web app working against the real backend.

---

## Phase 5 — Integration & Security Testing ⬜

**1 May – 20 May 2027.** **Goal:** prove the whole system works, and measure it.

### 5.1 Integration
- [ ] All five modules running together through Docker Compose
- [ ] End-to-end tests: agent → engine → tools → database → dashboard

### 5.2 Benchmark evaluation
- [ ] InjecAgent (510 cases) and AgentDojo (60 benign, 253 attacks) run through **three setups**: no defense, Spotlighting, full AdaptiShield
- [ ] ASR, detection rate, FPR and WCR reported **per attack type** with 95% Wilson intervals
- [ ] AgentDojo attacks kept as a **holdout**: no rule tuning after looking at them ([Rules.md](Rules.md) §6)
- [ ] Results committed under `results/` and shown in Analytics

### 5.3 Application security testing
- [ ] Injection content cannot run script in the dashboard (XSS tests with malicious payloads)
- [ ] Authorization: non-admins cannot approve proposals; the API rejects them, not just the UI
- [ ] Input validation, CORS and rate limiting on the API
- [ ] Dependency audit (`pip-audit`, `npm audit`)

### 5.4 Performance
- [ ] Latency per stage and end to end; the causal check only runs on high-impact actions
- [ ] Dashboard stays responsive during a batch run

**Deliverable:** test report + evaluation results.

---

## Phase 6 — Deployment, Documentation & Final Presentation ⬜

**21 May – 3 Jun 2027.** **Goal:** hand over a deployable system and present it.

- [ ] One-command deployment: `docker compose up` (backend, frontend, PostgreSQL; Ollama on the host)
- [ ] Seed data and a recorded demo set for the Replay feature, so the demo works even if the model is slow
- [ ] User manual (Tester, Analyst, Admin)
- [ ] Developer guide: setup, architecture, API reference
- [ ] Final FYP report
- [ ] Demo video (backup for the live demo)
- [ ] Final presentation slides and speaker notes
- [ ] Final presentation delivered

**Deliverable:** deployable prototype, documentation, test suite, final report and presentation.

---

## Risks and mitigations

| Risk | Mitigation |
| :--- | :--- |
| LLM calls are slow on a 4 GB GPU | Causal check only on high-impact actions; Replay of recorded episodes for demos |
| Model output varies between runs | Temperature 0, repeated runs, results reported with intervals |
| Frontend work is compressed into two months | Frontend scaffold starts in Phase 3; the Phase 1 wireframes are settled early |
| Ollama not available on the demo machine | Replay mode works without a model; demo video as a backup |
| Tuning rules on the holdout set by accident | Holdout rule in [Rules.md](Rules.md) §6; rules frozen before Phase 5 evaluation |
