# AdaptiShield — Frontend Design

This folder holds the frontend design for AdaptiShield: working mockups and the specs needed to turn them into the real React app (Phase 4 in [Phase.md](../Phase.md)).

**Status:** mockups are done for every planned screen, and they are waiting for the supervisor's review.

---

## Open the mockup

There are two self-contained HTML files, linked from each other's sidebars. There is no build step, and they need no server or backend.

```bash
# Linux
xdg-open design/mockups/live-monitor-attack-lab.html
xdg-open design/mockups/admin-analytics-agent-login.html
# or drag a file into any browser
```

They need an internet connection only for Google Fonts (IBM Plex). Without one, it falls back to system fonts and still works.

**What to try:**
1. The Monitor plays an injected-email episode automatically about a second after loading.
2. Change **Scenario** to see the other three paths: blocked by policy, approved directly, and approved after the causal check.
3. Change the speed (**0.5× / 1× / 2×**), then press **Replay episode**.
4. After a run, click any stage in the pipeline to read its explanation again.
5. Open **Attack Lab** in the sidebar to see the same attack run with protection off and on.
6. Switch your OS to dark mode. The whole palette follows.
7. In the second file, write a reason to enable the Admin Console's buttons, change **Preview as** to see each role's navigation, and use **Preview state** to see empty and error states. Plant `<script>` text in a Demo Agent email to see it stay as plain text.

---

## Files

| File | What it covers |
| :--- | :--- |
| [mockups/live-monitor-attack-lab.html](mockups/live-monitor-attack-lab.html) | Live Monitor and Attack Lab mockup (HTML + CSS + vanilla JS, one file) |
| [mockups/admin-analytics-agent-login.html](mockups/admin-analytics-agent-login.html) | Admin Console, Analytics, Demo Agent, Episode history and Login mockup. Analytics uses real committed results; other data is labeled sample |
| [diagrams/](diagrams/) | Architecture, sequence, use-case and ER diagrams, with the script that draws them |
| [design-system.md](design-system.md) | Colors (light and dark), verdict colors, typography, spacing, radii, shadows, the component catalogue |
| [motion.md](motion.md) | Every animation: what triggers it, duration, easing, reduced-motion behavior, and how to rebuild it in Framer Motion |
| [screens.md](screens.md) | Screen-by-screen spec: the two mocked-up screens in detail, plus wireframes and requirements for the remaining screens |
| [mockup-code-guide.md](mockup-code-guide.md) | How the mockup's code is organized and how to extend it: add a scenario, a stage, an animation or a page |
| [react-migration.md](react-migration.md) | Plan for porting the mockup to React + Vite + Tailwind: component tree, hooks, state, WebSocket wiring, build order |

---

## Design principles

These are the decisions everything else follows from. Keep them when expanding the design.

1. **Tell the demo story.** One injected email arrives, the engine catches it, and the user's task still finishes. Every screen should make some part of that story visible.
2. **Every animation stands for a real event.** A stage animates only when its verdict arrives. Nothing moves just for decoration, so the motion itself explains what the system is doing. See [motion.md](motion.md).
3. **Color means verdict, and only verdict.** Green = approved/pass, amber = flagged/sanitized and continued, red = blocked/takeover, blue = routed to the causal check, gray = skipped. The brand blue is also the "routed" color and appears nowhere else as decoration. See [design-system.md](design-system.md).
4. **The causal check gets the most space.** It is the project's core idea, so Run A vs Run B is always shown side by side with a clear ≠ or =.
5. **Untrusted content is quarantined and shown as plain text.** Monospace, dashed amber border, never rendered as HTML. This is a security rule ([Rules.md](../Rules.md) §5), made visible.
6. **Readable on a projector.** Light theme by default, high contrast, large type. Dark mode is fully supported for everyday use.
7. **Replay works without a model.** Replay uses the same event format as live mode, so the demo works even if Ollama is slow.

---

## How this maps to the architecture

| Mockup element | Real source (see [Architecture.md](../Architecture.md)) |
| :--- | :--- |
| Pipeline stages | The engine's stages: provenance (L1), screener (L3), policy (3A), causal check (3B), sanitizer (3C), permission and egress (L4), final decision |
| Event stream lines | `WS /ws/episodes` stage events (Architecture §7) |
| Run A / Run B | 3B's `orig` view vs a hidden/sanitized view (Architecture §4) |
| Outcome statuses | `approved_direct`, `approved_causal`, `safe_continuation`, `blocked` |
| Protection off / on | `PipelineConfig.undefended()` vs `PipelineConfig.full()` |
| Scenario data | Hard-coded samples today; `GET /api/episodes/{id}` and the attack catalogue later |

---

## Roadmap for the design

| Step | Deliverable | Phase |
| :--- | :--- | :--- |
| ✅ v1 | Live Monitor + Attack Lab mockup | 1 |
| ✅ v2 | Admin Console + Analytics mockup in the same style | 1 |
| ✅ v2 | Demo Agent inbox + Login mockup, plus Episode history | 1 |
| ⬜ | Supervisor review of all screens | 1 |
| ⬜ | Port to React (see [react-migration.md](react-migration.md)) | 3–4 |
