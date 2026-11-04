# AGENT_MAP.md — AdaptiShield Codebase Map

> Read this file first. It is a complete orientation map of the repository for
> AI coding agents (Claude Code, OpenCode, etc.). Human-oriented docs live in
> `README.md`, `Architecture.md`, `Design.md`, `Phase.md`, `Rules.md`.

## What this project is

**AdaptiShield** — a security gateway that sits between an LLM agent and its tools and
inspects every proposed action for **indirect prompt injection** (attacker text hidden in
tool output that hijacks the agent). FYP, UET Peshawar. Core claim: instead of judging the
*wording* of an action, run the agent's decision twice (content visible vs. masked) and
attribute the action **causally** to the untrusted content (Components 3A–3D in
`layer2/security_sublayer/`).

- Runs 100% locally: Ollama models `gemma3:4b` (causal probe — chosen because it *obeys*
  injections) and `qwen2.5:3b` (screener / sanitizer / planner). 4 GB VRAM ceiling.
- The **detection engine is built and tested** (layers 0–5 + pipeline, 561 deterministic
  tests). The FYP deliverable (FastAPI backend, React dashboard, demo agent, attack lab —
  `Phase.md` FYP phases 2–6) is **not built yet**. `backend/`, `agent/`, `attack_lab/` and
  `frontend/` exist as scaffolds with READMEs; `backend/contracts/` holds the agreed API, event
  and database design. Do not add service code until asked.

## Read-first order for a new agent

1. `AGENT_MAP.md` (this file)
2. `Rules.md` — hard rules; violating them breaks experiments (holdout, git identity, etc.)
3. `README.md` → `Architecture.md` → `Design.md` (why it is built this way)
4. `Phase.md` (what exists vs. what is planned) and `handof.md` / `docs/handover.md`
   (current session state, latest numbers, known traps)
5. A directory's own `README.md` before editing anything in it

## Git rules (hard, from `CLAUDE.md` + `Rules.md`)

- Commits authored as **ahmadkhanraj01**; never mention "Claude" or add AI co-author trailers.
- **Never create or switch branches**; work on the current branch, commit/push only on request.
- `pytest tests/ -q` must pass before any merge. Tests never call Ollama.
- Delete `logs/*_checkpoint/` after any engine change (stale checkpoints silently resume).

## Core architecture: the pipeline

`adaptishield_pipeline.py` (root) is the orchestrator. Key API:

- `PipelineConfig` — enable flags per component + ~20 preset arms for benchmarking
  (`full()`, `undefended()`, `screener_only()`, `plus_*()` ladder, `no_*()` leave-one-out,
  `spotlighting(variant)`). A disabled layer becomes *permissive* so every arm shares one
  code path and one telemetry schema.
- `AdaptiShieldPipeline.process_request(user_input, tool_response, tool_name,
  proposed_action, ...) -> dict` — the single entry point. Status: `blocked` |
  `approved_direct` | `approved_causal` | `safe_continuation`.
- No CLI; `python adaptishield_pipeline.py` runs 3 self-test cases. Needs Ollama.

Request flow: Layer 1 provenance split (trusted vs. mediator) → Layer 3 screener (flag
forces causal) → **3A** policy triage (block / fast-path / escalate) → **3B** causal
analyzer (4 probe regimes: orig, masked, masked_sanitized, orig_sanitized; ACE/IE/DE;
takeover on `IE ≥ threshold`) → **3C** sanitizer + planner picks safe continuation →
Layer 4 (permission scope → egress allowlist → optional Docker sandbox) → telemetry
`EpisodeRecord` to `logs/episode_records/episodes.jsonl`.

## Directory map

### Source (what you may edit)

| Path | What it is | Key files / symbols |
| :--- | :--- | :--- |
| `adaptishield_pipeline.py` | Engine orchestrator + ablation harness | `PipelineConfig`, `AdaptiShieldPipeline` |
| `layer0/` | MCP server trust: SHA-256 signatures, rug-pull detection, egress allowlist source | `server_trust_registry.py` → `ServerTrustRegistry`, `ServerRecord` (note: `__init__.py` duplicates the code — known wart) |
| `layer1/` | Provenance tagging: partitions context into trusted (user) vs mediator (tool/memory) | `provenance.py` → `ContextBuilder`, `InputParser`, `ProvenanceLabel` |
| `layer2/security_sublayer/` | **The core contribution.** 3A policy, 3B causal analyzer, 3C sanitizer, 3D adaptive learner | `policy_engine.py` (`PolicyEngine`, `blocked_patterns`), `causal_analyzer.py` (`CausalAnalyzer.evaluate_boundary`, `_decide_takeover`, `score_agent_action`), `context_sanitizer.py` (`ContextSanitizer.sanitize`), `adaptive_threat_model.py` (`AdaptiveThreatModel.propose_update`/`apply_update(approved=)`) |
| `layer3/` | Tool-response screener: LLM semantic scan + `KEYWORD_MARKERS` backstop; flags, never blocks | `tool_response_screener.py` → `ToolResponseScreener`, `ScreenResult.permissive()` |
| `layer4/` | Enforcement + telemetry: `permission_control.py`, `network_egress_filter.py`, `sandbox.py` (Docker, network off), `telemetry_stream.py` (`EpisodeRecord` → JSONL) | each module has a `__main__` self-test |
| `layer5/` | Human-in-the-loop (stdlib only). Recomputes evidence independently of 3D's proposal | `governance.py` (`gather_evidence`, `append_decision` → `logs/layer5/decisions.jsonl`), `review.py` (CLI: `python -m layer5.review`), `audit_report.py` (→ self-contained `logs/layer5/audit.html`) |
| `utils/` | `parsing.py` (`extract_next_action` — the only NEXT: parser), `hashing.py` (prompt fingerprints used to refuse stale probe corpora) | |
| `baselines/` | External comparison baselines. **Never imported by any `layer*/` module** (a test enforces this) | `spotlighting.py` (Hines et al. 2024: delimit/datamark/encode), `text_classifier.py` (numpy TF-IDF + logistic regression) |
| `red_team/` | Attack campaign loop: Generator → Execution Agent → Evaluator → Optimizer | `attack_library.py` (6 attack families), `attack_generator.py`, `execution_agent.py` (checkpoints per case!), `evaluator.py` (ASR/FPR/WCR), `optimizer.py`, `run_campaign.py`; vendored corpora in `red_team/data/` (`injecagent_dh.json`, `agentdojo_benign.json`, `agentdojo_attacks.json`) + `vendor_*.py` importers |
| `tests/` | 561 deterministic tests, ~15 s, no Ollama. Read `tests/README.md` — many tests **pin specific shipped bugs** (§6d–§6p), do not "fix" a test without understanding why | one `test_*.py` per phase/instrument; `test_paired.py`, `test_capability_scoring.py` are the biggest |
| `evaluation/` | All model-dependent experiments live here, never in `tests/` | `benchmark.py` (Phases 7/10/11/12 arms), `probe_corpus.py` (record probe output for offline rescoring), `rescore.py`, `campaign_report.py`, `train_classifier.py`, `multiturn.py`, `model_transfer.py`, `noise_floor.py`, `paired.py` (McNemar), `fpr_report.py` (Wilson CIs, refuses to pool), `kaggle/` (Phase 6 GRPO training: `grpo_env.py`, `grpo_train.py`, `package_episodes.py`, run via `run_kaggle.sh`) |

### Data & outputs

| Path | What it holds | Tracked? |
| :--- | :--- | :--- |
| `results/` | **Figures of record.** `phase7/`, `phase10/`–`phase16_model_transfer/`, `campaign/`, `probe_corpus/`, `severity/`, `noise_floor/`, `classifier/`, `refusal_audit/`. Every dir has `manifest.json` (commit, GPU state, sample indices) | yes (git) |
| `logs/` | Machine-local working output: `episode_records/episodes.jsonl`, `*_checkpoint/` resume state (delete after engine changes), `red_team_runs/`, `adaptive_loop/`, `layer5/` | **no** (gitignored) |
| `docs/Research/` | Obsidian research vault: `00 Meta`, `01 Foundations` (literature notes), `02 Architecture`, `03 Findings` (one note per finding 6d–6p), `04 Research Log`, `05 Phases`, `06 Metrics`, `07 Practice` (traps), `08 Open` | yes (vault UI state ignored) |
| `docs/paper/`, `docs/writeup/` | Manuscript + section files, `make_figures.py`, positioning table, deck/docx builders | yes (generated site ignored) |
| `docs/` (top level) | Mirrors of root docs + `Classifier_Training.md`, `handover.md`, `research_work_so_far.md`, `mkdocs.yml`, `timeline.html`, architecture drawio | yes |
| `design/` | Frontend design for the planned React app: `design-system.md`, `motion.md`, `screens.md`, `react-migration.md`, working mockup `mockups/live-monitor-attack-lab.html` | yes |
| `FYP/` | Admin artifacts: proposal PDFs, presentations, `gantt_chart.png`, `Supervisor_Feedback.md`, `Presentation_Notes.md`. `FYP/ppt skills/` is a large vendored PPT-generation skill — **gitignored, ignore it** | partly |

### Root files

| File | Purpose |
| :--- | :--- |
| `CLAUDE.md` | Git identity + branching rules for AI agents (hard rules) |
| `README.md` | Project overview, setup, repository layout, metrics definitions |
| `Architecture.md` | Modules, components, request flow, API and data design |
| `Design.md` | Design rationale (causal not wording, cheap-first, strip-and-continue, model split) |
| `Rules.md` | Every hard rule: env, defense invariants, 3D/human-gate, backend, untrusted content, evaluation/§6, testing, workflow |
| `Phase.md` | FYP delivery plan: FYP phases 0–6 (2026-09 → 2027-06) with status legend |
| `handof.md`, `docs/handover.md` | Session handoffs: current numbers, next task, known limitations |
| `requirements.txt` | Dependency source of truth (numpy pinned 1.26.4); Python 3.10 in `venv/` |
| `kaggle.json` | Kaggle API credentials (plaintext, gitignored — do not commit) |
| `session.txt` | A `claude --resume` command (gitignored, noise) |
| `.env` | Local env vars (gitignored) |

## Two numbering systems (do not confuse them)

1. **Research phases** (7, 10–16): closed, measured experiments. `results/phase10/` etc.
2. **FYP delivery phases 0–6** in `Phase.md`: proposal → design → backend → demo agent →
   React frontend → integration → deployment.

## Key invariants (from `Rules.md`, violating invalidates results)

- **AgentDojo attack set (`red_team/data/agentdojo_attacks.json`, 253 cases) is a frozen
  holdout** — never tune against it; spending it via `--agentdojo-holdout` is a one-way
  door requiring a supervisor decision.
- Never pool datasets of different origin; report per attack type with `n` + 95% Wilson CI.
- 3D only proposes bounded changes (patterns / high-impact tools / IE threshold) — never
  model weights; `apply_update` requires Layer-5-approved human verdict and independently
  recomputed evidence.
- No literal attacker addresses/URLs in learned patterns; attacker text is untrusted
  everywhere (no HTML/markdown rendering, no shell/eval/SQL).
- Every published number must be regenerable from one committed command with a `results/`
  manifest; report negative/null results too.

## Current state (as of the last handoff)

- 561 tests passing; engine + Layer 5 built; paper/writeup drafted in `docs/`.
- Headline numbers: in-corpus detection 116/120 = 96.7% [91.7%, 98.7%]; external FPR
  3.3% [0.9%, 11.4%] (AgentDojo benign n=60); InjecAgent reported **per stratum, never
  pooled** (93.3% where the target-match fires vs 10.0% where it cannot).
- Known honest negatives: 3D adaptive loop is a no-op (residual misses are not
  threshold-reachable); GRPO per-epoch curves are flat by construction; address-free
  attacks remain the hardest class.
- Open bugs documented in READMEs: temporal-drift rule can fire on empty boundaries;
  3A's `blocked_patterns` match the wrong namespace (Layer 5 detects this "inert pattern").

## Conventions

- Python 3.10, stdlib-first; `langchain_ollama` only where an LLM is genuinely needed.
- Dataclasses for every decision/result type (`*Result`, `*Decision`, `*Record`).
- Every component has a `permissive()`/disabled mode so ablation arms share one code path.
- Modules run as self-tests under `python -m <module>` where applicable.
- Per-directory `README.md` files document status, defects, and traps — read them before
  editing that directory.
