# AdaptiShield: context for agents

Read this first. It tells you what the project is, where everything is and what you must not do.

## The project

AdaptiShield is a Final Year Project at UET Peshawar: a security gateway and live dashboard that protects AI agents from indirect prompt injection. Every action an agent proposes passes through a Defense Engine before any tool runs. The team is Muhammad Ahmad Khan, Aleena Khan and Amna Noor, and the supervisor is Abdullah Burhan.

## Current state (4 November 2026)

| Phase | Status |
| :--- | :--- |
| 0 Proposal and first presentation | Done |
| 1 Requirements and system design | Written. Waiting on supervisor review, the task split and agreement on the PR workflow |
| 2 Backend, 1 Nov to 31 Dec 2026 | Next. No service code exists yet |
| 3 to 6 | Not started. The final deadline is 3 June 2027 |

The engine (`layer0/` to `layer5/`, `adaptishield_pipeline.py`) is built and tested. `backend/`, `agent/`, `attack_lab/` and `frontend/` are scaffolds, apart from `backend/contracts/`. The live checklist is `project/Phase.md`.

## Reading order

1. `project/Rules.md`: hard rules. Breaking them can invalidate results.
2. `project/Phase.md`: what is done and what comes next.
3. `project/Architecture.md` and `project/Design.md`: the structure and why it is this way.
4. `project/AGENT_MAP.md`: a detailed map of the code.
5. The README for any folder before you edit it. They are all linked in `modules/`.
6. `research/`: only when you need the history or evidence behind a decision.

## What is in this folder

| Path | Contents |
| :--- | :--- |
| `project/` | `Rules`, `Phase`, `Architecture`, `Design`, `AGENT_MAP`, `Handoff`, plus links to the root `README` and `CLAUDE` |
| `modules/` | Links to the README of every code folder |
| `design/` | Links to the frontend design system, motion, screen and React plans |
| `fyp/` | Links to the presentation notes and the supervisor's points |
| `research/` | The research behind the engine. See below |

Files in `modules/`, `design/`, `fyp/` and two in `project/` are symlinks, so edit the real file beside the code. Some search tools skip hidden folders and symlinks. With ripgrep, use `rg --hidden --follow <pattern> .agent`.

## Other sources of truth

| Path | Contents |
| :--- | :--- |
| `backend/contracts/` | The API, live event and database design. `tests/test_contracts.py` checks them against the engine |
| `FYP/` | Proposal, SRS, System Design, Phase 2 plan and literature review (Word and PDF) |
| `docs/` and `mkdocs.yml` | The public project website |
| `design/mockups/` | Working screen mockups |
| `results/` | Committed measurements. Evaluation code and tests read this path, so do not move it |
| `evaluation/`, `red_team/` | Benchmarks and attack data. Runtime code and tests import them, so do not move them |

## Research material

`research/` holds the study this project grew out of. It is the evidence for many design decisions, and it is hidden to keep the repository focused on the FYP.

| Path | Contents |
| :--- | :--- |
| `research/vault/` | Obsidian vault: foundations, architecture, findings, log, phases, metrics, practice and open questions. Start with `vault/AdaptiShield.md` and `vault/06 Metrics/Current Numbers.md` |
| `research/paper/` | Manuscript, sections, figures, decks, and the verified `external_numbers.json` |
| `research/writeup/` | Study guides for writing the paper |
| `research/README_research.md`, `Phase.md`, `Architecture.md`, `Design.md`, `Rules.md` | The research-era documents. **Where these differ from `project/`, `project/` wins** |
| `research/handover.md`, `research_work_so_far.md`, `researchworksofar.md`, `Classifier_Training.md` | Handovers and history |
| `research/old_site/` | The old research website source |

Notes in code such as `§6n` or `Phase 12` refer to this material. Search `research/vault/03 Findings/` for them.

## Working rules

- Commit as `ahmadkhanraj01`. Never mention Claude in Git history or PRs, and never create or switch branches. Commit or push only when asked. See `CLAUDE.md`.
- Never tune detection rules after looking at AgentDojo attack results. 60 of the 253 cases have already been scored, and that must be disclosed in the final report.
- Tests never call a model: `python -m pytest tests/ -q`.
- **The website is FYP-only.** Do not add research material to `docs/`. `tests/test_site.py` enforces this. Ask before linking anything in `research/` from a human-facing document.
- Hiding this folder is about focus, not honesty. If someone asks where the engine or its results came from, tell them. The proposal itself says the engine came from earlier studies, and the final report must say so too.

## Open decisions

These are recorded in `FYP/AdaptiShield_SRS.docx`, Section 8. Check their status before relying on them.

1. `forward_email` is missing from the engine's high-impact tool list.
2. The policy check reads `tool_name`, and benchmark runs pass the tool that returned the content.
3. Docs and manifests name `qwen2.5:3b` for the sanitizer and screener, but the code defaults to `gemma3:4b`.
4. `capability_scoring` is off by default, and its setting for Phase 5 needs the supervisor's agreement.
