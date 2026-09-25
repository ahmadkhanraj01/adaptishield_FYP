# From Mockup to React

How to turn the v1 mockup into the real frontend (Phase 3 scaffold, Phase 4 build in [Phase.md](../Phase.md)). The mockup is the visual and behavioral reference. The React app keeps its look and motion, but gets its data from the backend instead of hard-coded scenarios.

---

## 1. Stack

| Concern | Choice | Why |
| :--- | :--- | :--- |
| Build tool | **Vite** + React 18 + **TypeScript** | Fast dev server; types catch event-schema mistakes early |
| Styling | **Tailwind CSS**, with the design tokens as CSS variables | Tokens stay in one place; Tailwind utilities reference them |
| Components | **shadcn/ui** (Radix) for dialogs, tabs, select, tooltip | Accessible primitives; styled with our tokens |
| Motion | **Framer Motion** + CSS keyframes | See [motion.md](motion.md) §7 |
| Server data | **TanStack Query** | Caching, loading and error states for REST |
| Live data | Native `WebSocket` in a custom hook + **Zustand** store | Small, fast, easy to test |
| Charts | **Recharts** | Bar charts with error bars, line charts |
| Routing | **React Router** | One route per screen |
| Fonts | `@fontsource/ibm-plex-sans`, `-sans-condensed`, `-mono` | Works offline on demo day |
| Tests | **Vitest** + React Testing Library; **Playwright** for end-to-end | |

---

## 2. Project structure

```
frontend/
  index.html
  vite.config.ts
  tailwind.config.ts
  src/
    main.tsx                  app root, router, QueryClient, MotionConfig
    styles/
      tokens.css              :root tokens + dark blocks (copied from the mockup)
      globals.css             base styles, keyframes (spin, bob, blink, pulse)
    api/
      client.ts               fetch wrapper with JWT
      types.ts                StageEvent, Episode, Attack, Proposal, … (mirror backend Pydantic models)
      episodes.ts  attacks.ts  proposals.ts  analytics.ts
    stream/
      useEpisodeStream.ts     WebSocket hook: connect, reconnect, push events to the store
      episodeStore.ts         Zustand: episodes by id, events by episode, current episode
      replay.ts               replay player: feeds stored events into the store with delays
    lib/
      verdicts.ts             V and FINAL tables (from the mockup)
      stages.ts               STAGES table
      useTypewriter.ts
    components/
      layout/   AppShell  Sidebar  NavItem  TopBar  LiveChip  ConnectionStatus
      ui/       Card  Button  Segmented  Code  StatTile  TrustTag
      pipeline/ PipelineTrack  StageNode  StageCaption
      content/  RequestBubble  QuarantineBox  InjectedSpan
      causal/   CausalPanel  ProbeRun  Comparator  CausalVerdict
      outcome/  OutcomeStatus  EventLog
      lab/      LabPane  LabStep  MiniPipeline  LabResult  AttackPicker  AttackEditor
      admin/    ProposalList  ProposalDetail  EvidenceBars  DecisionForm
      charts/   RateByTypeChart  TrendChart  ResultsTable
    pages/
      MonitorPage.tsx  AttackLabPage.tsx  AgentPage.tsx
      AdminPage.tsx    AnalyticsPage.tsx  LoginPage.tsx
```

---

## 3. Mockup → component map

| Mockup (class / function) | React component | Props (main) |
| :--- | :--- | :--- |
| `.side`, `.nav` | `Sidebar`, `NavItem` | `module`, `to`, `disabled` |
| `.chip.live` | `LiveChip` | `running: boolean` |
| `.track`, `setRunning`, `setDone` | `PipelineTrack` | `events: StageEvent[]`, `onSelectStage` |
| `.node` | `StageNode` | `stage`, `state: 'idle'|'running'|'done'`, `verdict?` |
| `.caption`, `setCaption` | `StageCaption` | `stage`, `text` |
| `.bubble` | `RequestBubble` | `text`, `trusted: boolean` |
| `.mail`, `renderMail` | `QuarantineBox` | `subject`, `from`, `segments: {text, injected?}[]`, `state` |
| `.inj` | `InjectedSpan` | `state: 'none'|'flag'|'blocked'|'cut'` |
| `runCausal` | `CausalPanel` → 2× `ProbeRun` + `Comparator` + `CausalVerdict` | `runA?`, `runB?`, `changed?`, `rule?` |
| `.status` | `OutcomeStatus` | `finalStatus?`, `delivered?` |
| `.stat` | `StatTile` | `label`, `value` |
| `.log`, `log()` | `EventLog` | `events` |
| `playLab` panes | `LabPane` (×2) → `LabStep`, `MiniPipeline`, `LabResult` | `mode: 'off'|'on'`, `result` |

**Key difference from the mockup:** components **do not run timers**. They render whatever state the store holds. Motion happens because new events change that state ([motion.md](motion.md) §7).

---

## 4. Tokens in Tailwind

Copy the `:root` and dark blocks from the mockup into `src/styles/tokens.css` unchanged, then point Tailwind at them:

```ts
// tailwind.config.ts
export default {
  darkMode: ['selector', '[data-theme="dark"]'],
  theme: {
    extend: {
      colors: {
        bg: 'var(--bg)', surface: 'var(--surface)', 'surface-2': 'var(--surface-2)',
        ink: 'var(--ink)', muted: 'var(--muted)', line: 'var(--line)',
        accent: { DEFAULT: 'var(--accent)', soft: 'var(--accent-soft)' },
        ok:   { DEFAULT: 'var(--ok)',   soft: 'var(--ok-soft)' },
        warn: { DEFAULT: 'var(--warn)', soft: 'var(--warn-soft)' },
        bad:  { DEFAULT: 'var(--bad)',  soft: 'var(--bad-soft)' },
        skip: 'var(--skip)',
      },
      fontFamily: {
        sans: ['"IBM Plex Sans"', 'system-ui', 'sans-serif'],
        cond: ['"IBM Plex Sans Condensed"', '"IBM Plex Sans"', 'sans-serif'],
        mono: ['"IBM Plex Mono"', 'ui-monospace', 'monospace'],
      },
      borderRadius: { card: '12px', panel: '10px' },
    },
  },
}
```

Then `className="bg-ok-soft border-ok text-ok"` gives the same result as the mockup's `.v-ok`. Dark mode needs no `dark:` variants, because the variables already switch.

---

## 5. Types (mirror the backend)

```ts
// src/api/types.ts
export type StageKey =
  | 'received' | 'provenance' | 'screener' | 'policy' | 'causal_check'
  | 'sanitizer' | 'permission' | 'egress' | 'sandbox' | 'final';

export type Verdict =
  | 'pass' | 'flag' | 'route' | 'approve' | 'takeover' | 'nochange'
  | 'strip' | 'block' | 'skip' | 'running' | 'error';

export type FinalStatus = 'approved_direct' | 'approved_causal' | 'safe_continuation' | 'blocked';

export interface StageEvent {
  episode_id: string;
  seq: number;
  stage: StageKey;
  verdict: Verdict;
  detail: {
    note?: string;
    run_a_action?: string;
    run_b_action?: string;
    changed?: boolean;
    rule?: string;
    injected_spans?: [number, number][];   // character ranges in the untrusted content
    safe_action?: string;
    final_status?: FinalStatus;
    delivered?: string;
  };
  timestamp: string;                        // ISO 8601
}
```

The backend must send `running` events when a stage *starts* as well as when it finishes, so the spinner (M2) and the thinking dots (M9) show real work. Agree on this list with the backend in Phase 1 and keep it in [Architecture.md](../Architecture.md) §7. Note that the mockup's `causal` key becomes `causal_check` here.

**`injected_spans`** replaces the mockup's hand-marked `{inj: …}`: the engine reports which character ranges it flagged or stripped, and `QuarantineBox` splits the text on those ranges, still as plain text.

---

## 6. Live data and replay

```ts
// src/stream/useEpisodeStream.ts  (sketch)
export function useEpisodeStream() {
  const push = useEpisodeStore(s => s.pushEvent);
  const setStatus = useEpisodeStore(s => s.setConnection);
  useEffect(() => {
    let ws: WebSocket, retry = 0, stop = false;
    const connect = () => {
      ws = new WebSocket(`${WS_BASE}/ws/episodes?token=${getToken()}`);
      ws.onopen = () => { retry = 0; setStatus('connected'); };
      ws.onmessage = e => push(JSON.parse(e.data) as StageEvent);
      ws.onclose = () => {
        setStatus('reconnecting');
        if (!stop) setTimeout(connect, Math.min(1000 * 2 ** retry++, 15000));
      };
    };
    connect();
    return () => { stop = true; ws?.close(); };
  }, []);
}
```

```ts
// src/stream/replay.ts  (sketch)
export async function replay(events: StageEvent[], speed: number, signal: AbortSignal) {
  const store = useEpisodeStore.getState();
  store.clearEpisode(events[0].episode_id);
  for (let i = 0; i < events.length; i++) {
    if (signal.aborted) return;
    store.pushEvent(events[i]);
    const next = events[i + 1];
    if (next) {
      const gap = Date.parse(next.timestamp) - Date.parse(events[i].timestamp);
      await wait(Math.max(MIN_GAP, gap) / speed, signal);   // MIN_GAP ≈ 400ms so fast stages stay visible
    }
  }
}
```

- **Live and replay share one path:** both push `StageEvent`s into the store, and the components can't tell the difference. That's what makes replay exact ([motion.md](motion.md) §1).
- **Cancel** with an `AbortController`, just like the mockup's `runner.cancelled`.
- **MIN_GAP** keeps very fast stages (a few ms in reality) on screen long enough to follow. Show real latency in the stats, not in the animation.
- **Demo mode:** a "Presentation" setting that forces the mockup's comfortable pacing (≈620ms per stage) for the panel.

---

## 7. Security checklist for the frontend

From [Rules.md](../Rules.md) §4–5:

- [ ] Untrusted content is rendered with `{text}` in JSX, **never** `dangerouslySetInnerHTML`, and never through a Markdown renderer.
- [ ] `QuarantineBox` splits text by `injected_spans` and renders every segment as text.
- [ ] JWT is kept in memory or an httpOnly cookie, not `localStorage`.
- [ ] Admin actions are checked by the server; hiding buttons is only for convenience.
- [ ] Playwright test: plant `<img src=x onerror=alert(1)>` and `<script>` in an email, and assert that it shows up as text and nothing runs.
- [ ] Content Security Policy header from the frontend server (no inline scripts in production).

---

## 8. Build order

| Step | What | Result |
| :-: | :--- | :--- |
| 1 | Scaffold: Vite + TS + Tailwind + tokens + fonts + router + `AppShell`/`Sidebar` | Empty app that already looks like the mockup |
| 2 | `lib/stages.ts`, `lib/verdicts.ts`, `api/types.ts` | Shared vocabulary |
| 3 | Monitor components against a **fixture file** of events (the mockup scenarios converted to `StageEvent[]`) + `replay.ts` | Monitor works with no backend |
| 4 | `useEpisodeStream` against the real `/ws/episodes` | Live Monitor |
| 5 | Attack Lab: picker, compare call, two panes, result cards | Module 2 UI |
| 6 | Admin Console: proposals, evidence, decision form, history | Module 5 (approval) |
| 7 | Analytics: summary endpoint, charts, table, CSV | Module 5 (analytics) |
| 8 | Demo Agent, Login, error and empty states | Remaining screens |
| 9 | Tests: Vitest components, Playwright main flows, XSS test | Phase 4.6 |

Step 3 is the most important: converting the mockup's four scenarios into event fixtures gives the team a Monitor that runs in the browser **before the backend exists**, and later becomes the offline demo backup.

---

## 9. Converting mockup scenarios to fixtures

Each mockup scenario becomes a list of events. For the "injected email" scenario:

```json
[
  {"seq":0,"stage":"received","verdict":"pass","detail":{"note":"Request #142 arrived from the demo agent."}},
  {"seq":1,"stage":"provenance","verdict":"pass","detail":{"note":"User request tagged trusted. Email body tagged untrusted."}},
  {"seq":2,"stage":"screener","verdict":"flag","detail":{"note":"Instruction-like text found inside the email body.","injected_spans":[[187,289]]}},
  {"seq":3,"stage":"policy","verdict":"route","detail":{"note":"forward_email is a high-impact action, so it goes to the causal check."}},
  {"seq":4,"stage":"causal_check","verdict":"running","detail":{}},
  {"seq":5,"stage":"causal_check","verdict":"takeover","detail":{"run_a_action":"forward_email(to=\"archive@mail-backup.net\")","run_b_action":"summarize_email(for=\"user\")","changed":true,"rule":"Standalone rule fired: the email on its own produced a harmful action (masked = 2)."}},
  {"seq":6,"stage":"sanitizer","verdict":"strip","detail":{"note":"Removed 1 injected instruction.","safe_action":"summarize_email(for=\"user\")"}},
  {"seq":7,"stage":"permission","verdict":"pass","detail":{"note":"summarize_email is in scope for this task."}},
  {"seq":8,"stage":"egress","verdict":"pass","detail":{"note":"No outbound destination."}},
  {"seq":9,"stage":"final","verdict":"pass","detail":{"final_status":"safe_continuation","delivered":"Summary delivered to the user: …"}}
]
```

(`episode_id` and `timestamp` omitted here for brevity; the span range is illustrative.) Store fixtures in `frontend/src/fixtures/` and keep them in sync with the mockup's `SC` data.
