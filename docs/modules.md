---
hide: [navigation]
---

# Modules

Five modules share one backend. The tools the agent uses are what is being protected, so they are not a module.

![Architecture of the five modules](assets/diagrams/architecture.png)

## 1. Protected Demo Agent

A small email and document assistant with a mock mailbox. It reads content and proposes actions such as sending, forwarding, deleting and uploading. Its tools are simulated: they log what would have happened and never touch real mail or files.

## 2. Attack Lab

A tester picks an attack from InjecAgent or AgentDojo, or writes one, then runs it with protection off and on. Batch runs cover a whole attack type, with live progress.

## 3. Defense Engine

The core of the system, described in [How it works](how-it-works.md). No tool runs without its verdict.

## 4. Live Defense Monitor

A dashboard that lights up each stage as its verdict arrives. It shows what was flagged, what the causal check found, which rule fired and the final decision. Replay shows any stored request exactly as it appeared live, even with no model running.

## 5. Admin Console and Analytics

The Admin Console lists proposed configuration changes with evidence recomputed by the server, and requires a reason for each decision. Analytics reports attack success, detection, false alarms and task completion by attack type, each with its sample size and confidence interval.

## Who uses it

| Role | Goal | Can do |
| :--- | :--- | :--- |
| **Tester** | Check the defense by attacking it | Run the Demo Agent, Attack Lab and batches, and view episodes |
| **Analyst** | Understand what the defense does and how well | Use the Monitor, Replay and Analytics, and read current policy |
| **Admin** | Keep a person in control | Everything above, plus decide on proposals and read decision history |

The server enforces these roles on every request.

![Use cases for each role](assets/diagrams/use_cases.png)
