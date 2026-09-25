# AdaptiShield — Rules & Invariants

**What this file is:** the rules everyone on the team (and any AI assistant) must follow when changing this codebase. For the reasoning behind them see [Design.md](Design.md); for structure see [Architecture.md](Architecture.md).

**Legend:** 🔴 hard rule (breaking it breaks the build, the security model or the results) · 🟡 strong convention (break only with a good reason, written down)

---

## 1. Environment

- 🔴 **Python 3.10.12, inside `./venv`.** Every command (engine, backend, tests, evaluation) runs in the virtual environment. If something only works outside the venv, fix the venv.
- 🔴 **`numpy==1.26.4` is pinned** in `requirements.txt`. numpy 2.x breaks on Python 3.10.12.
- 🔴 **`requirements.txt` is the source of truth** for Python dependencies; `frontend/package.json` + lockfile for the frontend. Add a dependency there in the same commit that first uses it.
- 🔴 **4 GB VRAM is the ceiling.** Models larger than ~4B parameters do not fit. Everything runs locally through Ollama.
- 🔴 **No secrets in git.** `.env`, API keys and database passwords stay out of the repository (see `.gitignore`). Commit a `.env.example` with placeholder values instead.

## 2. Defense Engine

- 🔴 **Every tool call goes through the engine.** No module (agent, Attack Lab, backend) may run a tool without the engine's verdict. There is no bypass path, even for testing; use `PipelineConfig.undefended()` to run without protection.
- 🔴 **The backend wraps the engine; it does not reimplement it.** Decision logic stays in `layer*/` and `adaptishield_pipeline.py`. The API layer calls it and records what it did.
- 🔴 **Keep the model split.** Causal check (3B) = `gemma3:4b`; sanitizer, screener and planner = `qwen2.5:3b`. A more refusal-prone model on 3B destroys the causal signal.
- 🔴 **Do not lower `CausalAnalyzer.k_samples` below 2.** Fewer samples make the causal measurement too coarse.
- 🔴 **Do not change the masked-probe prompt** without re-running the benchmark and the false-alarm check.
- 🔴 **Takeover-rule invariants** (pinned by `tests/test_takeover_rules.py`):
  - The standalone `masked ≥ 2` rule must always be able to fire, even when the IE guard suppresses the contrast.
  - "Nothing observed" must never mean takeover: the drift and IE rules both require `masked ≥ 1`.
  - Drift history is kept **per `session_id`**, never in one shared list.
- 🔴 **Layer 4 gates independently.** Permission, egress and sandbox check every action regardless of the 3A/3B/3C verdict. The sandbox runs only when permission **and** egress both pass.

## 3. Adaptive component & human gate

- 🔴 **3D never touches model weights.** It tunes only 3A blocked patterns and high-impact tools, and the 3B IE threshold.
- 🔴 **`apply_update` requires `approved=True`, and only an Admin can supply it.** The approve endpoint checks the Admin role on the **server**; hiding a button in the UI is not access control.
- 🔴 **The server recomputes the evidence.** Governance recomputes the current and proposed rewards from data. Never display or trust a proposal's self-reported numbers as the evidence.
- 🔴 **Approval history is append-only.** Decisions are never edited or deleted. Each records who, when, the decision and the reason.
- 🔴 **Train on labeled data only.** Never infer "was this an attack?" from the outcome.
- 🔴 **No literal attacker addresses or URLs in proposed blocked patterns.** That is memorization, not learning. Exact destinations are Layer 4's allowlist's job.
- 🔴 **The reward prefers continuing over blocking:** malicious→`safe_continuation` (+1.0) must out-reward malicious→`blocked` (+0.7).

## 4. Backend (FastAPI)

- 🔴 **Validate every request with Pydantic models.** No raw `dict` input on public endpoints.
- 🔴 **Authenticate every endpoint except `/api/auth/login` and `/api/health`**, and authorize by role on the server.
- 🔴 **Never block the event loop.** Engine calls take seconds; run them in a worker thread or task queue, not directly in an `async` handler.
- 🔴 **Every stage verdict is both persisted and streamed.** The database row and the WebSocket event come from the same source, so Replay shows exactly what the Monitor showed live.
- 🟡 Use `logging`, not `print()`, in anything the backend imports.
- 🟡 Database schema changes go through Alembic migrations, never manual edits.

## 5. Handling untrusted content

- 🔴 **Injected content is untrusted everywhere**: in the engine, in the database, in logs, in the API and in the dashboard. It is attacker-written text.
- 🔴 **The frontend renders untrusted content as plain text only.** Never use `dangerouslySetInnerHTML`, and never render it as Markdown or HTML. An injection that runs script in the admin's browser would defeat the whole system.
- 🔴 **Never pass untrusted content to a shell, `eval`, or a SQL string.** Use SQLAlchemy parameters; the sandbox is the only place commands run.
- 🔴 **Demo agent tools are simulated.** They log what would have happened; they never send real mail or touch real files.

## 6. Evaluation & reporting

- 🔴 **Report every metric per attack type**, not only as one overall number.
- 🔴 **Every rate comes with `n`, the dataset name and a 95% Wilson interval.** A bare percentage is a rough indication and must be labeled as one.
- 🔴 **All setups share one code path.** No defense, Spotlighting and full AdaptiShield are `PipelineConfig` values run through the same pipeline, on the same cases, with the same models.
- 🔴 **Never mix datasets of different origin.** Our own development attacks, InjecAgent and AgentDojo are reported separately.
- 🔴 **The AgentDojo attack set is a holdout.** Do not tune rules or thresholds after looking at its results. If that happens, say so, because it is no longer a holdout.
- 🔴 **Every reported number is reproducible** from one committed command, with its output committed under `results/` alongside a manifest (models, dataset version, commit, date).
- 🔴 **Report weak results too.** Attack types the system misses are shown in Analytics and in the final report, not hidden.
- 🟡 Model output varies slightly even at temperature 0; report false-alarm rates over repeated runs, not a single run.

## 7. Testing

- 🔴 **`python -m pytest tests/ -q` passes before every merge** into `main`. CI runs it on every push.
- 🔴 **Unit tests do not call Ollama.** Stub the model out so tests are deterministic and fast. Model-dependent checks belong in `evaluation/`.
- 🟡 New backend endpoints get API tests (`TestClient`); new frontend components get Vitest tests; main user flows get a Playwright end-to-end test.
- 🟡 After changing engine code, delete `logs/*_checkpoint/` before re-running evaluations; cached results describe the old code.

## 8. Team workflow

- 🔴 **Never commit directly to `main`.** Create a branch (`feature/attack-lab`, `fix/ws-reconnect`), open a pull request, and have at least one teammate review it.
- 🟡 Commit messages say what changed and why, in the present tense ("Add replay endpoint").
- 🟡 **Keep the docs in sync.** A change to structure updates [Architecture.md](Architecture.md); a finished task is ticked in [Phase.md](Phase.md); a new rule goes here; each folder's `README.md` describes that folder.
- 🟡 Supervisor meetings and decisions are recorded in `FYP/`.
