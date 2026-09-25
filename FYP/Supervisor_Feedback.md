# AdaptiShield — Supervisor's Points from the First FYP Presentation

For the first FYP presentation (28 Sep 2026), the supervisor asked us to prepare four things:

1. The dataset
2. The questions (the research questions the project will answer)
3. The literature review
4. Whether the dataset is actually usable

Each section below answers one of them. Every published number is taken from the paper's own text. The source quotes are in `paper/external_numbers.json`.

---

## 1. Dataset

We use two public benchmarks and nothing we collected ourselves. A small set of attacks we wrote is used **only during development**, and its results are reported separately and never mixed with the external numbers.

| | InjecAgent | AgentDojo |
| :--- | :--- | :--- |
| **Paper** | Zhan et al., *Findings of ACL* 2024 | Debenedetti et al., *NeurIPS* Datasets & Benchmarks 2024 |
| **Source** | github.com/uiuc-kang-lab/InjecAgent | github.com/ethz-spylab/agentdojo (v0.1.35) |
| **Licence** | MIT | MIT |
| **Full size** | 1,054 test cases, 17 user tools, 62 attacker instructions | 97 user tasks, 629 security test cases |
| **Role in AdaptiShield** | External **attack** corpus | **Benign** documents (false-alarm rate) + held-out **attack** set |
| **Part we use** | Direct-harm split, base setting: **510 cases** | **60** benign documents (workspace + Slack suites); **253** attack cases |
| **Stored at** | `red_team/data/injecagent_dh.json` | `red_team/data/agentdojo_benign.json`, `red_team/data/agentdojo_attacks.json` |

### What each case looks like

- **InjecAgent.** The user asks the agent for something ordinary, such as "read my latest review". A tool returns a response with an attacker instruction hidden inside it, such as "grant the guest access to the smart lock". The attack succeeds if the agent calls the attacker's tool.
- **AgentDojo benign.** Real-looking emails, files and messages that contain **no** attack. If the defense flags one of these, that counts as a false alarm.
- **AgentDojo attacks.** An attacker goal placed inside a document the agent reads during a normal task.

### What we leave out, and why (so the numbers aren't inflated)

- **InjecAgent's data-stealing split.** It is a two-step attack (read the data, then send it out). Our single checkpoint cannot model it, so we would just be adding cases that fail for the wrong reason.
- **InjecAgent's "enhanced" split, and AgentDojo's `important_instructions` / `ignore_previous` / `system_message` wrappers.** These add an obvious "ignore your instructions" line. That makes attacks *easier* to catch and would make our detection rate look better than it is.
- **AgentDojo benign fields that contain injection placeholders.** We removed them so the benign set really is clean (63 harvested, 3 duplicates and 10 injection fields dropped, 60 kept).

### What we measure on it

| Metric | Meaning | Measured on |
| :--- | :--- | :--- |
| Attack success rate (ASR) | Share of attacks where the harmful action ran | InjecAgent, AgentDojo attacks |
| Detection rate (TPR) | Share of attacks the defense caught | InjecAgent, AgentDojo attacks |
| False-alarm rate (FPR) | Share of **clean** documents wrongly flagged | AgentDojo benign |
| Workflow continuation rate (WCR) | Share of flagged cases where the user's real task still finished | both |

Every metric is reported **per attack type**, not as one overall number, because an overall number hides the attack types where the defense fails. We compare three setups on the same data: no defense, a prompt-level defense (Spotlighting, re-implemented in our pipeline), and the full AdaptiShield system.

---

## 2. Research Questions

- **RQ1: Detection.** Does the causal check (running the decision with and without the suspicious text) catch indirect prompt injection better than a prompt-level defense on the same attacks?
  *Answered by:* detection rate and ASR on InjecAgent, per attack type, for no defense vs Spotlighting vs AdaptiShield.
- **RQ2: False alarms.** How often does it wrongly flag clean content?
  *Answered by:* false-alarm rate on the 60 AgentDojo benign documents.
- **RQ3: Keeping the task alive.** When an injection is caught, can the system remove it and still finish the user's task, rather than simply blocking?
  *Answered by:* workflow continuation rate.
- **RQ4: Where it fails.** Which kinds of attack does the causal check miss, and why?
  *Answered by:* per-type and per-stratum results. For example, attacks that name a target, such as an email address or a URL, are compared with attacks that don't.
- **RQ5: Generalisation.** Does it hold up on attacks it was never tuned on?
  *Answered by:* the AgentDojo attack set, which is kept as a holdout. The detection rules were frozen before this set was imported.
- **RQ6: Oversight.** Can a person see why each action was allowed or blocked, and stay in control of automatic configuration changes?
  *Answered by:* the Live Defense Monitor and the Admin Console. This is a system requirement shown in the demo, not a benchmark number.

### Questions the panel may ask, with short answers

- **"Why not just use a classifier that detects injection text?"** A classifier judges the *wording*, so rephrasing the attack can get past it. The causal check judges whether the text *changed the action*, and rephrasing doesn't change that.
- **"Isn't running the model twice slow?"** Only high-impact actions (send, forward, delete, upload) go to the causal check. Cheaper layers handle everything else first.
- **"Why local models?"** There is no paid API, no data leaves the machine, and it runs on a 4 GB GPU (Gemma 3 4B and Qwen 2.5 3B via Ollama).
- **"What is new compared with existing work?"** Most published defenses report one pooled number. We report results by attack type, including where detection is weak. We also wrap the engine in a monitor and an approval console so a person can see and supervise it.

---

## 3. Literature Review

The review is grouped by the idea behind each line of work, not paper by paper.

### 3.1 The attack

- **Greshake et al. (2023), *"Not What You've Signed Up For"*.** The first description of **indirect prompt injection**. An attacker who can put text where an AI will read it can steer the AI without ever touching the user's prompt.
- **Liu et al. (2023), *Prompt Injection Attacks and Defenses in LLM-Integrated Applications*.** Formalises prompt injection and evaluates attacks and defenses systematically.
- **OWASP** ranks prompt injection the **No. 1** risk for LLM applications.

### 3.2 Benchmarks (how the field measures the problem)

- **InjecAgent (Zhan et al., 2024).** A ReAct-prompted **GPT-4 followed injected instructions in 24%** of cases in the base setting and **47%** with a hacking prompt added. A prompted **Llama2-70B went above 80%**. Even strong models are vulnerable.
- **AgentDojo (Debenedetti et al., 2024).** A dynamic environment that measures both attacks and defenses. Its delimiting defense lowered GPT-4o's targeted attack success from **57.69% to 41.65%**, so prompt-level defenses help but many attacks still succeed. Its tool filter reached **7.5%** (the body text says 7.5%, while the paper's Table 5 gives 6.84%).
- **ToolEmu (Ruan et al., ICLR 2024).** Uses an LLM to emulate tools so agent risks can be tested without real side effects.
- **Agent Security Bench (Zhang et al., ICLR 2025)** and **HarmBench (Mazeika et al., ICML 2024).** Broader benchmarks for attacking and defending LLM agents and for automated red teaming.

### 3.3 Defenses, in three families

| Family | Example | What it looks at | Where it breaks |
| :--- | :--- | :--- | :--- |
| **Prompt-level** | Spotlighting (Hines et al., 2024): marks untrusted text so the model knows where it came from. Reports attack success cut "from greater than 50% to below 2%" on GPT models | the **text** | relies on the model respecting the marking |
| **Training-level** | StruQ (Chen et al., USENIX Security 2025): separates instructions from data with structured queries. Instruction Hierarchy (Wallace et al., 2024): trains the model to rank system > user > tool instructions | the **model** | needs retraining; not available for an off-the-shelf local model |
| **Gate-level** | Permission scopes, egress allowlists, AgentDojo's tool filter | the **action** | fails when the attack needs the same permission the real task needs |
| **Causal (this project)** | Re-run the decision with the suspicious text shown vs hidden | the **link between text and action** | weak when the injected text names no target the action can copy |

### 3.4 The gap AdaptiShield fills

1. **No causal check in deployable form.** Existing defenses judge either the text or the action. Few ask whether the untrusted text *caused* the decision, and those that do are research prototypes, not supervised systems.
2. **Pooled reporting hides failures.** Published results are mostly one overall number, which can hide the attack types where a defense collapses. We report by attack type.
3. **No visibility or human control.** The defenses surveyed here report aggregate numbers. They don't show *why* a particular action was blocked, and they don't keep a person in charge of automatic defense changes. The Live Defense Monitor and Admin Console address this.

---

## 4. Is the Dataset Feasible?

**Yes.** The data is public, free to use, already downloaded, and has already been run through the detection engine in our earlier work.

| Check | Status | Evidence |
| :--- | :--- | :--- |
| Publicly available | ✅ | Both on GitHub, no sign-up or request needed |
| Licence allows academic use | ✅ | Both MIT |
| Already downloaded and converted | ✅ | `red_team/data/`: 510 InjecAgent, 253 AgentDojo attack and 60 AgentDojo benign cases |
| Reproducible | ✅ | `red_team/vendor_injecagent.py` and `red_team/vendor_agentdojo_attacks.py` re-fetch from the source and record the source, citation and exclusions in each file |
| Runs on our hardware | ✅ | Small local models via Ollama on a 4 GB GPU; no paid API |
| Used before | ✅ | Our previous studies ran the detection engine on these same corpora |
| Development and test data kept apart | ✅ | Detection rules frozen (commit `46cfbfb`) before the AgentDojo attack set was imported, so it is a real holdout |

### Limitations to state honestly

- **Small benign set (60).** False-alarm rates will have wide confidence intervals, so we report them with intervals rather than as one exact figure.
- **Direct-harm only.** Data-stealing (two-step) attacks from InjecAgent are out of scope for this version.
- **Benchmarks are simulated.** Tool calls are emulated, not sent to real mail servers. The Demo Agent in the project closes this gap by showing one injected email end to end.
- **Single holdout.** If we tune the detection rules on AgentDojo results, it stops being a holdout, and there is no third corpus to fall back on.

---

## References

1. K. Greshake et al., "Not What You've Signed Up For: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection," arXiv:2302.12173, 2023.
2. Y. Liu et al., "Prompt Injection Attacks and Defenses in LLM-Integrated Applications," arXiv:2310.12815, 2023.
3. Y. Ruan et al., "Identifying the Risks of LM Agents with an LM-Emulated Sandbox," ICLR, 2024.
4. S. Chen et al., "StruQ: Defending Against Prompt Injection with Structured Queries," USENIX Security, 2025.
5. E. Wallace et al., "The Instruction Hierarchy: Training LLMs to Prioritize Privileged Instructions," arXiv:2404.13208, 2024.
6. K. Hines et al., "Defending Against Indirect Prompt Injection Attacks With Spotlighting," arXiv:2403.14720, 2024.
7. Q. Zhan et al., "InjecAgent: Benchmarking Indirect Prompt Injections in Tool-Integrated Large Language Model Agents," Findings of ACL, 2024.
8. E. Debenedetti et al., "AgentDojo: A Dynamic Environment to Evaluate Prompt Injection Attacks and Defenses for LLM Agents," NeurIPS, 2024.
9. H. Zhang et al., "Agent Security Bench (ASB): Formalizing and Benchmarking Attacks and Defenses in LLM-based Agents," ICLR, 2025.
10. M. Mazeika et al., "HarmBench: A Standardized Evaluation Framework for Automated Red Teaming and Robust Refusal," ICML, 2024.
