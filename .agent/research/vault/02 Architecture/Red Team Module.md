---
tags: [adaptishield, architecture, component]
type: component
status: built
---

# Red Team Module

Four agents, running **against** the [[Defensive Stack]] in dry-run mode (no
external side effects), following [[AutoMalTool]]'s optimization loop.

| Agent | File | Role |
| :--- | :--- | :--- |
| Attack Generator | `red_team/attack_generator.py` | Builds `RedTeamCase`s; enforces the train/held-out split |
| Execution Agent | `red_team/execution_agent.py` | Runs each case through the live pipeline; **per-case checkpointing** |
| Evaluator | `red_team/evaluator.py` | [[ASR]] / [[FPR]] / [[WCR]] with per-family and per-layer breakdown |
| Optimizer | `red_team/optimizer.py` | Keyword-softening mutator producing **gen-2** attacks |

Library: `red_team/attack_library.py`. Wiring: `red_team/run_campaign.py`.

## The attack grid

- **6 families**: blunt override, AgentDojo-style "important instructions",
  tool-knowledge injection, masked-hypothetical framing, `authority_citation`,
  `delegated_followup`
- **4 directives**, including two subtle single-recipient "bcc / add a recipient"
  phrasings with **no "forward all" keyword**
- **4 targets, split first-class**:
  `training_targets()` = {attacker@evil.com, exfil@darkpost.io} ·
  `holdout_targets()` = {leaker@shadow-mail.net, siphon@nullroute.org}

Training grid = 6 × 4 × 2 = **48 gen-1 attacks**, plus gen-2 mutations and a
held-out pass.

🔴 The held-out split is **enforced by construction**
(`generate_training_attacks()` / `generate_holdout_attacks()`), not by index
slicing, with a `__main__` assertion proving no held-out address enters training.
The reason this rule exists is [[6d — Adaptive Loop Negative Result]]: nothing
was held out, and memorization looked like generalization.

## Plus

- **18 [[Address-Free Attacks]]** — 3 reconnaissance/disclosure directives × 6
  families, carrying the **legitimate** destination deliberately
- **8 hand-written benign controls** — a *diagnostic*, never a rate
- **60 [[AgentDojo]] benign episodes** via `red_team/vendor_agentdojo.py`

Total corpus: **188 episodes** → [[Evaluation Corpus]].

## Its founding result

Keyword-softening collapsed causal detection from **2/4 families to 0/4** while
[[ASR]] stayed at 0% because the egress filter caught the exfiltration. That is
simultaneously the motivation for [[3D Adaptive Threat Model]] and the first
instance of [[Backstops Mask Progress]].
