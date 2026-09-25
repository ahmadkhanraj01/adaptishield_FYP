# AdaptiShield — Design Rationale

**What this file is:** the *why* behind the architecture: the main design decisions, the reasoning for each, and the trade-offs accepted. For the *what and where* see [Architecture.md](Architecture.md); for the rules that follow from these decisions see [Rules.md](Rules.md).

---

## 1. Core defense decisions

| Decision | Rationale |
| :--- | :--- |
| **Check cause, not wording** | A classifier that judges the *text* can be beaten by rephrasing the attack. The causal check judges whether the untrusted text *changed the action*. However the attack is worded, if it is what makes the agent forward the email, the with/without runs will disagree. |
| **Cheap checks first, causal check only for high-impact actions** | Running the model several times is slow on a 4 GB GPU. Provenance, screening and static policy handle most requests quickly; only send, forward, delete and upload go to the causal check. The cost is paid only where the risk is. |
| **Layered, independent defenses** | No layer trusts another layer's verdict. Layer 4 (permission, egress, sandbox) gates every action regardless of what the causal check decided, so a detection miss is not automatically a breach. |
| **Strip and continue, not just block** | Blocking stops the attack but also stops the user's real task. When the injection can be removed, the sanitizer produces a safe continuation so the task still finishes. This is measured as the workflow continuation rate (WCR). |
| **Keyword backstop in the screener** | Small models sometimes describe an attack correctly in prose but return the wrong structured verdict. The screener flags if *either* the LLM or a deterministic keyword check fires. |
| **Different models for different jobs** | The causal check uses `gemma3:4b` because it *follows* injected instructions when shown the content alone, which makes the with/without difference visible. The planner, sanitizer and screener use `qwen2.5:3b`, which resists injections better. A model that refuses everything would make a *worse* causal detector. |
| **The adaptive component proposes; a human decides** | 3D can suggest changes to rules and thresholds, but it cannot apply them. An automatic tuner can propose a change that is worse than the current setting; the Admin Console exists to catch that. |
| **The server recomputes the evidence** | A proposal arrives with its own claimed improvement. Governance recomputes both sides (current vs proposed) from the data, so the admin decides on verified numbers, not the proposal's own claim. |
| **Tune settings, never model weights** | 3D only adjusts blocked patterns, high-impact tools and the IE threshold. Every change is small, readable and reversible. |
| **Learn from labeled data only** | A reward needs ground truth. Deciding "was this an attack?" from the outcome would be circular, so 3D learns only from labeled benchmark episodes. |

---

## 2. Why three takeover rules

The causal check is not one threshold. It is three rules, each covering a weakness of the one before.

1. **IE rule** (with a consistency guard). IE measures how much sanitizing reduced compliance. Weakness: if the sanitizer *fails* to remove an injection, both views comply equally, IE is 0, and a strong attack looks safe.
2. **Standalone rule** (`masked ≥ 2`). If the untrusted content on its own produces a harmful action, that is a takeover no matter what IE says. This catches attacks strong enough to survive the sanitizer.
3. **Drift rule.** Watches compliance rising across one conversation (`session_id`). It only fires when something was actually observed (`masked ≥ 1`), because "nothing observed" must never mean "attack".

The consistency guard (every masked sample must beat every sanitized sample) stops one random sample from creating a false verdict. The guard can be strict only because the standalone rule already catches the strong cases.

---

## 3. System-level decisions (FYP)

| Decision | Choice | Rationale |
| :--- | :--- | :--- |
| Engine as a library behind a service | `backend/services/engine.py` wraps `AdaptiShieldPipeline` | The tested decision logic stays unchanged; the web layer only calls it and records what it does. |
| Backend framework | **FastAPI** | Python, like the engine; async; built-in WebSockets; automatic OpenAPI docs; Pydantic validation. |
| Live updates | **WebSockets** | Stage verdicts arrive one at a time over several seconds. Pushing each one as it happens lets the Monitor light up stage by stage; polling would be slower and heavier. |
| Frontend | **React + Vite + Tailwind + Recharts** | Component model suits a dashboard of reusable stage/verdict widgets; Vite gives fast builds; Tailwind keeps styling consistent; Recharts covers the analytics charts. |
| Database | **PostgreSQL** | Relational data (episodes → stage events, proposals → approvals) with JSONB for variable stage details; reliable and free. |
| Models | **Ollama, local** | No paid API, no data leaves the machine, runs on a 4 GB GPU. |
| Packaging | **Docker Compose** | One command starts backend, frontend and database the same way on any machine. Ollama stays on the host for GPU access. |
| Replay mode | Stored stage events re-emitted in order | Live LLM runs take seconds; replay shows recorded attacks instantly and makes the demo reliable. |
| Simulated tools | The demo agent's tools log instead of acting | Attacks can be run safely and repeatedly without sending real mail or deleting real files. |
| Roles | Tester, Analyst, Admin | Only an Admin can change the defense. Separating roles keeps the human gate meaningful. |

---

## 4. Evaluation design

| Decision | Rationale |
| :--- | :--- |
| **Public benchmarks only** for reported numbers | InjecAgent and AgentDojo are public and MIT-licensed, so results can be checked by others. Our own hand-written attacks are for development only and are reported separately. |
| **Per-attack-type reporting** | One overall number hides the attack types where the defense fails. Showing each type separately, including the weak ones, is more honest and more useful. |
| **Three setups on the same data** | No defense, Spotlighting (a published prompt-level defense) and full AdaptiShield, all run on the same cases through the same code path, so differences come from the defense and nothing else. |
| **AgentDojo attacks kept as a holdout** | The detection rules were frozen before this set was imported, so it tests attacks the system was never tuned on. |
| **Confidence intervals on every rate** | The benign set is small (60 documents), so a single percentage would overstate precision. Wilson intervals show the real uncertainty. |
| **Excluded splits** | InjecAgent's two-step data-stealing split and "enhanced" wrappers are left out: the first cannot be modeled by one checkpoint, and the second makes attacks easier to catch and would inflate detection. |

---

## 5. Known limitations and trade-offs

- **Attacks that name no target are harder to catch.** The causal check is strongest when the injected action copies something from the content (an address or URL). Attacks with no such target are a weaker case, and results by attack type will show it.
- **Small local models.** A 4 GB GPU limits us to ~4B-parameter models. Larger models may behave differently.
- **Simulated tools.** Benchmark tool calls are emulated. The demo agent shows one injected email end to end, but it is not a production mail system.
- **Latency.** The causal check needs several model calls. This is acceptable for high-impact actions only, and is the reason for the cheap-checks-first design.
- **Direct-harm attacks only.** Two-step data-stealing attacks are out of scope for this version.
