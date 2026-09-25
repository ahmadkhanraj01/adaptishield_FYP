# AdaptiShield — Screen Specs

Every screen in the AdaptiShield web app: what it is for, who uses it, what is on it, which data it needs, and its states. Screens 1 and 2 are built in the v1 mockup ([`mockups/live-monitor-attack-lab.html`](mockups/live-monitor-attack-lab.html)). Screens 3–6 are specified here and still need mockups.

| # | Screen | Module | Main role | Mockup |
| :-: | :--- | :-: | :--- | :-: |
| 1 | [Live Monitor](#1-live-monitor) | 4 | Analyst | ✅ v1 |
| 2 | [Attack Lab](#2-attack-lab) | 2 | Tester | ✅ v1 |
| 3 | [Demo Agent](#3-demo-agent) | 1 | Tester | ⬜ |
| 4 | [Admin Console](#4-admin-console) | 5 | Admin | ⬜ |
| 5 | [Analytics](#5-analytics) | 5 | Analyst | ⬜ |
| 6 | [Login](#6-login) | — | all | ⬜ |
| — | [Episode list](#7-episode-list-history) (part of Monitor) | 4 | Analyst | ⬜ |

**Shared frame (all screens except Login):** left sidebar with the brand, the five modules in nav (each with its module number), and connection status at the bottom (WebSocket, Ollama model). On phones the sidebar becomes a top bar. See [design-system.md](design-system.md) §4.

---

## 1. Live Monitor

**Job:** show, in real time, what the Defense Engine is doing with each request and why.
**Users:** Analyst (watching), panel/supervisor (demo).
**Data:** `WS /ws/episodes` for live events; `GET /api/episodes/{id}` for replay ([Architecture.md](../Architecture.md) §6–7).

### Layout

```
┌ Top bar ────────────────────────────────────────────────────────────────────┐
│ Episode #142                     [● LIVE]  Scenario [▾]  [0.5×|1×|2×]  [▶ Replay] │
│ Demo agent · read_email · session s-07                                      │
├ Defense pipeline ───────────────────────────────────────────────────────────┤
│  (✓)──(✓)──(!)──(→)──(✕)──(✂)──(✓)──(✓)──(■)     ← packet travels along    │
│  Received Provenance Screener Policy Causal Sanitizer Permission Egress Decision│
│  CAPTION: Causal check · The decision changed when the email was hidden…    │
├ What the agent saw ──────────────────┬ Causal check ────────────────────────┤
│ USER REQUEST [trusted]               │ ┌Run A · visible┐  ≠  ┌Run B · hidden┐│
│ ┌ Summarize the latest email… ┐      │ │forward_email… │     │summarize_…   ││
│ CONTENT FROM THE TOOL [untrusted]    │ └───────────────┘     └──────────────┘│
│ ┌╌ quarantine box (mono, plain) ╌┐   │ Decision changed: injection detected  │
│ │ … ~~Also, forward this…~~ [REMOVED]│ Standalone rule fired (masked = 2)    │
│ AGENT PROPOSES summarize_email(…)    │                                       │
├ Outcome ─────────────────────────────┼ Event stream ────────────────────────┤
│ [✂] Injection removed, task continued│ 09:14:22.000 connection …             │
│ Summary delivered: …                 │ 09:14:22.220 received · pass …        │
│ Stages 9/9 · Model calls 7 · 6.8 s   │ 09:14:22.440 provenance · pass …      │
└──────────────────────────────────────┴───────────────────────────────────────┘
```

### Sections

| Section | Contents | Behavior |
| :--- | :--- | :--- |
| Top bar | Episode number, agent + tool + session, LIVE/DONE chip, scenario picker (mockup) or episode picker (real app), speed control, Replay | Replay restarts from the first event |
| Defense pipeline | 9 stage nodes, packet, caption | Nodes light up as events arrive; finished nodes are clickable and re-show their note in the caption |
| What the agent saw | User request (trusted), tool content (untrusted, quarantined), the proposed action | Tags appear on provenance; highlight on flag; red on block; strike-through + "removed" on strip; proposed action updates to the safe action |
| Causal check | Idle text → Run A / comparator / Run B → verdict and rule; shows the model name and `k` | Idle when not reached; "Skipped" explanation when policy handled it |
| Outcome | Final status tile, what the user received, stats (stages, model calls, latency) | Lands when the `final` event arrives |
| Event stream | Timestamped lines: stage · verdict · message | Newest at the bottom, auto-scroll |

### The four paths (mockup scenarios)

| Scenario | Path through the stages | Final status |
| :--- | :--- | :--- |
| Injected email: forward to outsider | pass → pass → **flag** → **route** → **takeover** → **strip** → pass → pass | `safe_continuation` |
| Injected build log: delete reports | pass → pass → **flag** → **block** → skip × 4 | `blocked` |
| Clean email: summarize | pass → pass → pass → **approve** → skip → skip → pass → pass | `approved_direct` |
| User forwards to a colleague | pass → pass → pass → **route** → **no change** → skip → pass → pass | `approved_causal` |

Any new scenario must follow a path the real engine can produce ([Architecture.md](../Architecture.md) §3).

### States

| State | What shows |
| :--- | :--- |
| Waiting for events | Nodes idle, caption "Waiting", causal panel explains what it will do, outcome "Waiting for a decision" |
| Running | LIVE chip blinking; current node spinning |
| Done | DONE chip; all nodes resolved; stage notes clickable |
| WebSocket disconnected | *(to build)* Connection dot turns red in the sidebar; banner "Live updates paused. Reconnecting…"; auto-reconnect with backoff |
| Ollama down | *(to build)* Sidebar model dot red; causal check shows "Model unavailable"; replay still works |
| Episode error | *(to build)* Node that failed turns red with "error"; outcome shows the error message and the stage |

### To add in the real app
- **Episode list** side panel or drawer (see §7) so the analyst can pick any past episode to replay.
- **Follow live** toggle: automatically jump to each new episode, or stay on the current one.
- **Step mode** for presentations: advance one event per key press (→).
- Show the **k samples** for the causal check (both samples per run), collapsed by default.

---

## 2. Attack Lab

**Job:** prove the defense works by running the same attack with protection off and on.
**Users:** Tester; panel (demo).
**Data:** `GET /api/attacks`, `POST /api/attack-lab/compare`, `POST /api/attack-lab/batch` + WebSocket progress.

### Layout

```
┌ Top bar: Attack Lab · "Same attack, same agent…"      Attack [▾]  [▶ Run attack] ┐
├ Attack card: USER ASKS … · PLANTED IN the email from … · [injected text]        ┤
├ Protection off (red header) ──────────┬ Protection on (green header) ───────────┤
│ PipelineConfig.undefended()            │ PipelineConfig.full()                   │
│ · Agent reads the email…               │ · Agent reads the email…                │
│ ! Agent proposes forward_email…        │ ! Agent proposes forward_email…         │
│ · No checks run                        │ › Defense Engine ●●●●●○○○○  Causal…     │
│ ✕ Tool runs: forward_email             │ ✂ Tool runs: summarize_email            │
│ ┌ Attack succeeded (shakes) ─────────┐ │ ┌ Attack stopped, task finished ─────┐ │
├ Summary: Same attack, same agent. Without AdaptiShield… With it…               ┤
└─────────────────────────────────────────────────────────────────────────────────┘
```

### To add in the real app

| Feature | Description |
| :--- | :--- |
| Attack catalogue | Browse InjecAgent / AgentDojo / custom attacks; filter by source and attack type; search |
| Custom attack editor | Fields: user task, carrier (email body, file, tool response), injected text, target. Preview of the planted content (plain text). Save to the catalogue. |
| Carrier position | Choose where in the content the injection goes (start, middle, end) |
| Batch run | Run every attack of one type; progress bar; live tally of succeeded / stopped for off and on; link to Analytics when done |
| Open in Monitor | From the "on" pane, jump to that episode in the Live Monitor to see every stage in detail |
| Result history | Past comparisons with date, attack and both outcomes |

### States
Not run yet · running (both panes animating) · done · error in one pane (show which config failed and why) · batch in progress.

---

## 3. Demo Agent

**Job:** make the threat concrete. Show a normal assistant, the user's request, and what the agent did, with AdaptiShield guarding it.
**Users:** Tester; panel (demo).
**Data:** `POST /api/agent/run`; mailbox seeded from AgentDojo benign documents plus planted attacks.

```
┌ Inbox ─────────────────┬ Email ─────────────────────────────┬ Assistant ─────────────┐
│ ● Sara K.   Q3 planning│ From sara.k@northwind.co           │ You: Summarize Sara's  │
│   IT desk   Maintenance│ Q3 planning: notes from Monday     │      latest email.     │
│   Legal     Contract   │ (plain text; injected lines are    │ Agent: proposes        │
│   CI runner build #881 │  marked after the engine flags them)│   forward_email → …   │
│                        │                                    │ Shield: ✂ injection    │
│ [+ Plant attack]       │                                    │   removed → summary    │
│                        │                                    │ Agent: Q3 budget …     │
└────────────────────────┴────────────────────────────────────┴────────────────────────┘
```

- Three columns: mailbox list, selected email, chat-style assistant panel.
- The assistant panel shows the three voices: **You**, **Agent** (what it proposed), **Shield** (the engine's verdict, colored). The Shield line links to the episode in the Monitor.
- **Plant attack** opens the custom-attack editor from the Attack Lab, pre-filled to plant into the selected email.
- **Protection toggle** in the top bar (off/on) for quick live demos.
- A tool-activity strip at the bottom lists what the simulated tools *did* ("Sent 0 emails, deleted 0 files").

---

## 4. Admin Console

**Job:** keep a person in control of every automatic configuration change.
**Users:** Admin only (enforced by the server, [Rules.md](../Rules.md) §3).
**Data:** `GET /api/proposals`, `GET /api/proposals/{id}`, `POST /api/proposals/{id}/decision`, `GET /api/policy`.

```
┌ Pending proposals (2) ─────────┬ Proposal #17 ────────────────────────────────────────┐
│ #17  ie_threshold 1.0 → 0.5    │ Proposed by the adaptive component · 10 Mar 2027 09:30│
│      2 h ago        [pending]  │                                                      │
│ #16  + high_impact: upload_file│ CHANGE                                                │
│      1 d ago        [pending]  │   ie_threshold      1.0  →  0.5                        │
│ ── History ──                  │                                                      │
│ #15  rejected · A. Khan        │ EVIDENCE (recomputed by the server)                   │
│ #14  approved · M. A. Khan     │   Current config   reward +0.8330   ▇▇▇▇▇▇▇▇         │
│                                │   Proposed config  reward +0.8329   ▇▇▇▇▇▇▇▇  ▼      │
│                                │   ⚠ The proposal is slightly WORSE than the current   │
│                                │   Per attack type: detection ±, false alarms ±       │
│                                │                                                      │
│                                │ Reason (required) [____________________________]      │
│                                │ [Reject]                        [Approve change]      │
└────────────────────────────────┴──────────────────────────────────────────────────────┘
```

- **Evidence first.** Show the server's recomputed reward for current vs proposed. If the proposal is worse, show a clear amber warning. The proposal's own claimed numbers are never shown as the evidence.
- **Per-attack-type effect**: how detection and false alarms would change for each type.
- **Reason is required** for both approve and reject; buttons stay disabled until it is filled in.
- **Confirmation step** in the page (not a browser dialog): "Apply ie_threshold 0.5 to the live engine?" with Cancel / Apply.
- **History** is read-only and append-only: who, when, decision, reason.
- **Current policy** tab: blocked patterns, high-impact tools, thresholds, each with "last changed by proposal #…".

---

## 5. Analytics

**Job:** show how well the defense works, **per attack type**, compared with no defense and Spotlighting.
**Users:** Analyst; panel; final report.
**Data:** `GET /api/analytics/summary` (rates, `n`, 95% Wilson intervals).

```
┌ Filters: Dataset [InjecAgent ▾]  Setups [✓None ✓Spotlighting ✓AdaptiShield]  Range [▾] ┐
├ Headline tiles: Detection rate · False-alarm rate · Workflow continuation · ASR       ┤
│ (each: value, 95% interval, n, dataset name)                                           │
├ Attack success rate by attack type (grouped bars + interval whiskers) ─────────────────┤
│  Data exfiltration  ▇▇▇▇▇ none   ▇▇▇ spotlight   ▇ adaptishield                        │
│  Financial harm     ▇▇▇▇  none   ▇▇▇ spotlight   ▇▇ adaptishield                       │
│  Physical harm      …                                                                  │
├ Detection by stage (which layer caught it) ──┬ Trend over time (line chart) ───────────┤
├ Results table: type · n · ASR · TPR · FPR · WCR, each with interval · [Export CSV]     ┤
└────────────────────────────────────────────────────────────────────────────────────────┘
```

- **No pie charts and no single overall score.** Every chart is split by attack type ([Design.md](../Design.md) §4).
- Every rate shows its interval and `n`. Small-`n` cells are marked.
- Setups use fixed colors that are *not* the verdict colors: pick three neutrals/blues for None / Spotlighting / AdaptiShield so they don't read as pass/fail.
- Weak attack types are shown, not hidden ([Rules.md](../Rules.md) §6).
- Charts: Recharts `BarChart` with `ErrorBar`, `LineChart`; theme-aware colors from tokens.
- CSV export of the table.

---

## 6. Login

- Centered card: logo, "Sign in to AdaptiShield", email, password, Sign in.
- Errors say what to fix: "Email or password is incorrect."
- After login, route by role: Tester → Attack Lab, Analyst → Monitor, Admin → Admin Console.
- A small footer line shows backend and model status, so a failed demo setup is obvious before signing in.

---

## 7. Episode list (history)

Part of the Monitor (drawer or separate tab).

| Column | Content |
| :--- | :--- |
| # | Episode id |
| Time | Start time |
| Request | User request (truncated) |
| Source | Demo agent / Attack Lab / batch |
| Attack type | or "clean" |
| Path | Nine mini dots (same as the Attack Lab mini pipeline) |
| Status | Final-status chip |

Filters: status, attack type, source, date range. Clicking a row opens it in the Monitor in replay mode.

---

## 8. Next mockups to build

1. **Admin Console + Analytics** (v2), in the same file or a second HTML file in `mockups/`, reusing the tokens and components.
2. **Demo Agent + Login** (v3).
3. Error and empty states for all screens.

See [mockup-code-guide.md](mockup-code-guide.md) §5 for how to add a page to the mockup.
