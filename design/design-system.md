# AdaptiShield — Design System

The visual rules for every AdaptiShield screen. The values here are the ones in [`mockups/live-monitor-attack-lab.html`](mockups/live-monitor-attack-lab.html). When you change one, change it in both places, and later in the Tailwind config ([react-migration.md](react-migration.md) §4).

**The look:** a calm, cool-gray security console. Color is reserved for meaning. At rest the page is mostly neutral, so when something turns red, the viewer sees it immediately.

---

## 1. Color tokens

All colors are CSS custom properties on `:root`. Components use only tokens, never raw hex values, so light and dark mode switch in one place.

### Neutrals and brand

| Token | Light | Dark | Used for |
| :--- | :--- | :--- | :--- |
| `--bg` | `#EDF0F5` | `#090E18` | Page background |
| `--surface` | `#FFFFFF` | `#111A29` | Cards, sidebar, inputs |
| `--surface-2` | `#F5F7FA` | `#0D1421` | Inset areas: email header, event log, run cards, captions |
| `--ink` | `#0E1726` | `#E4EAF3` | Main text |
| `--muted` | `#56647A` | `#93A1B7` | Secondary text, labels, timestamps |
| `--line` | `#D5DCE7` | `#233047` | Borders, idle pipeline track, dividers |
| `--accent` | `#2446C8` | `#7F97FF` | Brand blue: primary button, active nav, packet, "routed to causal check" |
| `--accent-soft` | `#E3E8FA` | `#1A2448` | Active nav background, user request bubble, caption flash |

The neutrals lean slightly blue on purpose. A pure gray would look unconsidered next to the blue accent.

### Verdict (semantic) colors

These are the most important colors in the system. **Each one has exactly one meaning, and it means the same thing on every screen.**

| Meaning | Token | Light | Dark | Soft background token | Light | Dark |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Pass / approved | `--ok` | `#0E8A5F` | `#3CD398` | `--ok-soft` | `#DCF2E8` | `#0E2C22` |
| Flagged / sanitized and continued | `--warn` | `#A96400` | `#F2A83A` | `--warn-soft` | `#FBEACB` | `#32230A` |
| Blocked / takeover / attack succeeded | `--bad` | `#C62F2C` | `#FF6C66` | `--bad-soft` | `#F9DFDE` | `#3A1715` |
| Routed to the causal check | `--accent` | (brand) | (brand) | `--accent-soft` | (brand) | (brand) |
| Skipped / not reached | `--skip` | `#9AA5B5` | `#56637A` | — | — | — |

**Pattern:** a verdict element uses the soft color as its fill, the strong color as its border, and the strong color for its text or glyph. Example: a flagged stage dot is `background: --warn-soft; border: --warn; color: --warn`.

**Never** use a verdict color for decoration, and never show a verdict by color alone. Every verdict also has a glyph and a word (§5), so it stays readable for color-blind viewers and in grayscale printouts.

### Dark mode

Dark mode works at the token level, in three blocks:

```css
:root { /* complete light palette */ }
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) { color-scheme: dark; /* dark tokens */ }
}
:root[data-theme="dark"] { color-scheme: dark; /* dark tokens again */ }
```

- With no `data-theme` attribute, the page follows the OS setting.
- `data-theme="light"` or `"dark"` on `<html>` forces a theme, which a future theme toggle can use.
- In dark mode, the text on the primary button switches to `#0A1024`, because the light accent needs dark text.

---

## 2. Typography

One family, the IBM Plex superfamily, in three roles. It reads as technical and precise, and the mono and condensed cuts match the sans exactly.

| Role | Family | Weights | Used for |
| :--- | :--- | :--- | :--- |
| Interface | **IBM Plex Sans** | 400, 500, 600 | Body text, headings, buttons |
| Labels | **IBM Plex Sans Condensed** | 500, 600 | Uppercase card titles, stage names, verdict words, chips |
| Data | **IBM Plex Mono** | 400, 500 | Untrusted content, actions (`forward_email(...)`), event log, timestamps, numbers |

Fallback stacks: `system-ui, -apple-system, "Segoe UI", sans-serif` for the sans faces, and `ui-monospace, SFMono-Regular, Menlo, Consolas, monospace` for mono.

Loaded from Google Fonts:
```html
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans+Condensed:wght@500;600&family=IBM+Plex+Sans:wght@400;500;600&display=swap">
```
In the React app, self-host these with `@fontsource/ibm-plex-sans` etc. so the app works offline on demo day.

### Type scale

| Use | Size | Weight | Notes |
| :--- | :--- | :--- | :--- |
| Page title (`h1`) | 20px | 600 | `text-wrap: balance` |
| Outcome status title | 16px | 600 | |
| Pane title (Attack Lab) | 15px | 600 | |
| Body | 14px | 400 | line-height 1.5 |
| Secondary text | 13px | 400 | `--muted` |
| Untrusted content, actions | 12.5px | 400 | mono, line-height 1.65 |
| Card title | 12.5px | 600 | condensed, uppercase, letter-spacing 0.08em |
| Stage name | 12.5px | 600 | condensed |
| Event log, meta | 11.5px | 400 | mono, `tabular-nums` |
| Verdict word, chips | 11–11.5px | 600 | condensed, uppercase, letter-spacing 0.05–0.06em |

**Rules:** uppercase labels always get letter-spacing. Numbers that line up in columns (timestamps, stats) use `font-variant-numeric: tabular-nums`.

---

## 3. Space, shape and depth

| Property | Values |
| :--- | :--- |
| Spacing | Gaps of 6, 8, 10, 12, 16, 18 px. Card padding 16px. Card-to-card gap 18px. |
| Page gutter | 28px on desktop, 16px on phones |
| Radius | 12px cards · 10px inner panels (email, run cards, outcome) · 8px buttons, inputs, captions · 5–7px small tags · 999px pills · 50% stage dots |
| Shadow (light) | `0 1px 2px rgba(14,23,38,.06), 0 4px 16px rgba(14,23,38,.05)`, on cards only |
| Shadow (dark) | `0 1px 2px rgba(0,0,0,.4)` |
| Borders | 1px `--line` by default. 1.5px for the email box and results. 2px for stage dots and ≠/= circles. |

**Cards only for real objects.** Border, radius and shadow mark a separate object. Don't wrap every block in a card; nested inset areas use `--surface-2` without a shadow.

---

## 4. Layout

```
┌──────────┬──────────────────────────────────────────────────┐
│ Sidebar  │ Top bar: title · status chip · controls          │
│ 216px    ├──────────────────────────────────────────────────┤
│          │ Pipeline card (full width)                       │
│ brand    ├───────────────────────┬──────────────────────────┤
│ nav (5)  │ What the agent saw    │ Causal check             │
│          ├───────────────────────┼──────────────────────────┤
│ status   │ Outcome               │ Event stream             │
└──────────┴───────────────────────┴──────────────────────────┘
```

| Breakpoint | Change |
| :--- | :--- |
| ≤ 1100px | Two-column grids become one column |
| ≤ 760px | Sidebar becomes a horizontal, scrollable nav bar at the top; footer status hidden; gutter 16px; Run A / ≠ / Run B stack vertically; stats become 2 columns |
| Any width | The pipeline track keeps a 700px minimum and scrolls sideways inside its own container. The page itself never scrolls sideways. |

The nav numbers (4, 2, 1, 5, 5) are the **module numbers** from the proposal, so the sidebar itself shows the five-module architecture.

---

## 5. Verdict vocabulary

Every verdict has a key, a color, a glyph and a word. This table is the `V` object in the mockup's code. Use it everywhere a verdict appears: pipeline nodes, the Attack Lab dots, the event log, and later the Analytics tables.

| Key | Color | Glyph | Word | Meaning |
| :--- | :--- | :-: | :--- | :--- |
| `pass` | ok | ✓ | pass | Stage checked and found nothing |
| `flag` | warn | ! | flagged | Suspicious content noticed; not a decision yet |
| `route` | accent | → | to causal | Policy sent the action to the causal check |
| `approve` | ok | ✓ | approved | Policy approved directly |
| `takeover` | bad | ✕ | takeover | Causal check: the content caused the action |
| `nochange` | ok | = | no change | Causal check: same action with and without the content |
| `strip` | warn | ✂︎ | stripped | Sanitizer removed the injection |
| `block` | bad | ✕ | blocked | Action refused |
| `skip` | skip | – | skipped | Stage not needed or not reached |

Final statuses (the `FINAL` object):

| `final_status` | Color | Glyph | Label |
| :--- | :--- | :-: | :--- |
| `safe_continuation` | warn | ✂︎ | Injection removed, task continued |
| `approved_direct` | ok | ✓ | Approved directly |
| `approved_causal` | ok | ✓ | Approved after causal check |
| `blocked` | bad | ✕ | Action blocked |

> The ✂ glyph is written as `✂︎`. The `︎` forces the text version instead of a colored emoji.

---

## 6. Component catalogue

Each entry names the CSS class in the mockup and its planned React component ([react-migration.md](react-migration.md)).

| Component | Mockup class | React name | Anatomy and states |
| :--- | :--- | :--- | :--- |
| Sidebar nav item | `.nav button` | `NavItem` | Module number badge + label. States: default, hover, `aria-current="page"` (accent-soft background), disabled (55% opacity). |
| Status chip | `.chip.live` / `.chip.done` | `LiveChip` | Pill, uppercase condensed. Live = red with blinking dot; Done = muted. |
| Card | `.card`, `.card-h`, `.card-b` | `Card` | Header with uppercase title on the left and mono metadata on the right; body padded 16px. |
| Pipeline track | `.track`, `.line`, `.fill`, `.packet` | `PipelineTrack` | 9-column grid; gray base line; blue fill grows to the current stage; packet rides the fill. |
| Stage node | `.node`, `.dot`, `.nlabel`, `.nlayer`, `.nverdict` | `StageNode` | 44px circle + name + layer code + verdict word. States: idle, running (spinning ring), done + verdict class `v-ok`/`v-warn`/`v-bad`/`v-route`/`v-skip`. Clickable once done. |
| Caption | `.caption` | `StageCaption` | One line under the track: stage name + plain-language explanation. Flashes accent-soft on change. `aria-live="polite"`. |
| Trust tag | `.tag.trusted` / `.tag.untrusted` | `TrustTag` | Small uppercase tag; fades in when provenance runs. |
| User request bubble | `.bubble` | `RequestBubble` | Accent-soft rounded box. |
| Quarantine box | `.mail`, `.mail.quarantine` | `QuarantineBox` | Header (subject, from) + mono body. Dashed amber border once tagged untrusted. **Plain text only.** |
| Injected span | `.inj` + `.flag` / `.blocked` / `.cut` | `InjectedSpan` | Highlight sweep (amber), red when blocked, strike-through + "removed" tag when stripped. |
| Code chip | `.code` | `Code` | Mono, inset background, for actions and config names. |
| Run card | `.run` (+ `.harm`) | `ProbeRun` | Title, "sees" line, mini diagram of what the model sees (solid bars = visible, hatched = hidden, dashed amber = untrusted), action box with thinking dots or typed action. Red border when the action is harmful. |
| Comparator | `.cmp` + `.ne` / `.eq` | `Comparator` | Dashed "?" circle that pops into a red ≠ or green =. |
| Causal verdict | `.verdict.bad` / `.verdict.ok` | `CausalVerdict` | Bold headline + rule explanation. |
| Outcome status | `.status` + `ok`/`warn`/`bad` | `OutcomeStatus` | Large glyph tile + title + `final_status` code. |
| Stat tile | `.stat` | `StatTile` | Label + mono value (stages run, model calls, latency). |
| Event log | `.log`, `.e` | `EventLog` | Mono lines: timestamp · stage · verdict · message. New lines slide in; auto-scrolls. |
| Lab pane | `.card.off` / `.card.on`, `.pane-h` | `LabPane` | Tinted header (red for off, green for on), config code chip, step list, result card. |
| Lab step | `.steps li`, `.ic` | `LabStep` | Icon tile + title + small explanation. |
| Mini pipeline | `.dots i` | `MiniPipeline` | Nine 16px dots filled with verdict colors; the current one blinks. |
| Lab result | `.result` + `bad`/`ok`/`warn` | `LabResult` | Bold result + one sentence. The failed case shakes; the success case lands. |
| Buttons | `.btn`, `.btn.primary` | `Button` | Primary = accent fill. All have a visible focus ring. |
| Segmented control | `.seg` | `Segmented` | Speed selector; `aria-pressed` marks the active option. |

---

## 7. Writing style for UI text

- Name things by what the user recognizes: "What the agent saw", not "mediator context".
- Explain verdicts in one short sentence: "forward_email is a high-impact action, so it goes to the causal check."
- Buttons say exactly what they do: "Replay episode", "Run attack".
- Technical names (`final_status`, `PipelineConfig.full()`) appear in mono as secondary detail, never as the only explanation.
- No exclamation marks, no emoji.

---

## 8. Accessibility checklist

- [x] Every verdict has a glyph and a word, not only a color
- [x] Visible focus ring on every interactive element (`outline: 2px solid var(--accent)`)
- [x] Stage nodes are real `<button>`s with an `aria-label` once done
- [x] Caption is `aria-live="polite"` so screen readers hear each verdict
- [x] `prefers-reduced-motion` turns off animation (see [motion.md](motion.md) §6)
- [x] Works at 400px width
- [ ] Contrast check of every token pair with a tool (WebAIM) before the final build
- [ ] Keyboard-only walkthrough of the React app
