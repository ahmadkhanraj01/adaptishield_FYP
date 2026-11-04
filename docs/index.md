---
hide: [navigation, toc]
---

<div class="as-hero" markdown="0">
<h1>Every action an AI agent proposes is checked before any tool runs</h1>
<p>AdaptiShield is a security gateway and live dashboard that protects AI agents from instructions hidden in the emails, files and tool results they read. It runs entirely on local models.</p>
</div>

## One injected email, stage by stage

A user asks for a summary. Hidden in the email is a line telling the agent to forward the thread to an outside address.

<ol class="as-pipe" markdown="0">
<li class="ok"><i>✓</i><b>Received</b><span>Request arrives</span></li>
<li class="ok"><i>✓</i><b>Provenance</b><span>Email marked untrusted</span></li>
<li class="warn"><i>!</i><b>Screener</b><span>Instruction found in the email</span></li>
<li class="route"><i>→</i><b>Policy</b><span>Sent to the causal check</span></li>
<li class="bad"><i>✕</i><b>Causal check</b><span>The content took over</span></li>
<li class="warn"><i>✂</i><b>Sanitizer</b><span>Injection removed</span></li>
<li class="ok"><i>✓</i><b>Permission, egress</b><span>Safe action allowed</span></li>
<li class="warn"><i>■</i><b>Decision</b><span>Task continues</span></li>
</ol>

<div class="as-outcome" markdown="0"><b>Outcome:</b> the user receives the summary, and nothing is forwarded. An administrator can watch every stage live and replay it later.</div>

## Why it matters

The user's request and the content an agent reads arrive in the same context, so the model cannot reliably tell data from commands. An attacker who can get text in front of the agent may be able to steer what it does, without ever contacting the user. This is **indirect prompt injection**, and OWASP lists prompt injection first among the risks for LLM applications.

## What we are building

| Module | What it does |
| :--- | :--- |
| **1. Protected Demo Agent** | A small email and document assistant, so an injected email can be shown end to end |
| **2. Attack Lab** | Runs the same attack with protection off and on, and compares the results |
| **3. Defense Engine** | Checks each proposed action, then allows it, blocks it, or removes the injection and continues the task |
| **4. Live Defense Monitor** | Shows each stage's verdict as it happens, with replay |
| **5. Admin Console and Analytics** | Keeps a person in charge of configuration changes, and reports results by attack type |

[See how it works](how-it-works.md){ .md-button .md-button--primary } [Open the screens](screens.md){ .md-button }

## Project status

The Defense Engine's core is built and tested. Requirements and system design are written and awaiting the supervisor's review, and the backend is next. See the [roadmap](roadmap.md).

## Team

| Item | Details |
| :--- | :--- |
| **Team** | Muhammad Ahmad Khan (23JZBCS0238), Aleena Khan (23JZBCS0229), Amna Noor (23JZBCS0230) |
| **Supervisor** | Abdullah Burhan |
| **Department** | Computer Science & Information Technology, University of Engineering & Technology, Peshawar |
| **Degree** | Final Year Project, BS Computer Science |
