# AdaptiShield — Motion Spec

Every animation in the AdaptiShield UI, what triggers it, and how to rebuild it in React. The values are the ones in [`mockups/live-monitor-attack-lab.html`](mockups/live-monitor-attack-lab.html).

---

## 1. The rule: motion = an event happened

Every animation must stand for something the system actually did. In the real app, **a stage animates only when its WebSocket stage event arrives** (see [Architecture.md](../Architecture.md) §7). Nothing moves for decoration.

That gives three benefits:
1. **The motion explains the system.** A viewer who knows nothing about prompt injection can watch the packet stop at the causal check, see the two runs disagree, and understand what happened.
2. **Slow steps become something to watch.** The causal check takes seconds on a 4 GB GPU; the thinking dots and typed actions turn that wait into part of the explanation.
3. **Replay is exact.** Replay feeds stored events through the same animation code, so a replayed episode looks exactly like the live one.

Three kinds of motion are used, each with a fixed purpose:

| Kind | Purpose | Examples |
| :--- | :--- | :--- |
| **Travel** | Where the request is now | Packet moving, track filling |
| **Work** | Something is being computed | Spinning ring, thinking dots, typing, blinking LIVE |
| **Arrival** | A result just appeared | Pop, land, highlight sweep, strike-through, shake |

---

## 2. Easing and duration tokens

| Token | Value | Use |
| :--- | :--- | :--- |
| `ease-move` | `cubic-bezier(.4, 0, .2, 1)` | Travel: packet and track fill |
| `ease-pop` | `cubic-bezier(.3, 1.6, .5, 1)` | Arrival with a slight overshoot: stage verdict, ≠/=, "removed" tag |
| `ease-land` | `cubic-bezier(.3, 1.4, .5, 1)` | Softer arrival: outcome card |
| `ease` / linear | CSS defaults | Fades, highlight sweep, spinner |
| `dur-fast` | 300–350ms | Fades, log lines, tags |
| `dur-base` | 380–450ms | Pops, run cards, verdict box |
| `dur-move` | 550ms | Packet travel |
| `dur-slow` | 700ms | Highlight sweep across the injected text |

Keep new animations inside these tokens so the whole app feels like one system.

---

## 3. Animation catalogue: Live Monitor

| # | Animation | Trigger (real event) | What moves | Timing |
| :-: | :--- | :--- | :--- | :--- |
| M1 | **Packet travel** | A stage starts | Packet slides to the next node; blue fill grows behind it. Driven by one CSS variable `--p` (0 → 1). | `left`/`width` 550ms `ease-move` |
| M2 | **Stage working** | Stage started, no verdict yet | 2px ring spins around the node; node border turns accent | 800ms per turn, linear, infinite |
| M3 | **Verdict pop** | Stage event with a verdict | Node scales 0.7 → 1 and changes to its verdict color, glyph and word | 380ms `ease-pop` |
| M4 | **Caption flash** | Any verdict | Caption text changes; background flashes accent-soft and fades | 500ms |
| M5 | **Trust tags** | `provenance` verdict | "trusted" tag fades in, then "untrusted" 250ms later; email border turns dashed amber | fade + 3px rise 350ms; border 400ms |
| M6 | **Highlight sweep** | `screener` = flagged | Amber highlight sweeps left-to-right across the injected sentence (`background-size` 0% → 100%) | 700ms ease |
| M7 | **Blocked text** | `policy` = block | Injected sentence turns red with a red highlight | 300ms |
| M8 | **Probe cards appear** | `causal_check` started | Run A card fades up 8px; Run B follows 250ms later | 400ms each |
| M9 | **Thinking dots** | Waiting for a probe result | Three dots bob in sequence (0, 0.15s, 0.3s delay) | 1s loop |
| M10 | **Typed action** | Probe result arrives | The chosen action types out character by character; Run A gets a red border if the action is harmful | 22ms per character |
| M11 | **Comparator** | Both probe results in | Dashed "?" pops into a red ≠ (changed) or green = (same) | 400ms `ease-pop` |
| M12 | **Causal verdict** | After the comparator | Verdict box fades in with the rule that fired | 400ms |
| M13 | **Strike-through** | `sanitizer` = stripped | Injected sentence gets a 2px amber strike-through and turns muted; a "removed" tag pops in 450ms later; the proposed action updates to the safe one | strike instant; tag 350ms `ease-pop` |
| M14 | **Outcome lands** | `final` event | Packet fades out; outcome card scales 0.96 → 1 and fills with the final color | 500ms `ease-land` |
| M15 | **Log line** | Every event | New line slides in 6px from the left; log auto-scrolls | 350ms |
| M16 | **LIVE chip** | Episode running | Red dot blinks; changes to "DONE" at the end | 1s loop |
| M17 | **Connection pulse** | WebSocket connected | Green dot emits a fading ring | 1.8s loop |

### Timeline of the main scenario at 1× speed

The "injected email: forward to outsider" episode lasts about 13 seconds. Each stage gets about 620ms of "working" before its verdict so the viewer can follow; in the real app the time comes from the engine instead.

```
t(s)  0.0  received ── working 0.6 ── ✓ pass
      0.9  provenance ── tags fade in ── ✓ pass
      2.1  screener ── working ── highlight sweep ── ! flagged
      3.5  policy ── → to causal
      4.4  causal check ── Run A / Run B appear ── thinking 1.1 s
      6.3      Run A types forward_email(...) (red) ── Run B types summarize_email(...)
      8.9      ≠ pops ── verdict "Decision changed: injection detected"
      9.3  sanitizer ── strike-through ── "removed" tag ── ✂ stripped
     10.6  permission ✓ ── egress ✓
     12.4  decision ── packet fades ── outcome lands at ~13.3 s (amber, "Injection removed, task continued")
```

Shorter paths are faster: the policy-block scenario skips its stages at 420ms each, and the clean-email scenario never opens the causal check.

---

## 4. Animation catalogue: Attack Lab

Both panes run **at the same time**, so the viewer compares them live.

| # | Animation | Pane | What moves | Timing |
| :-: | :--- | :--- | :--- | :--- |
| L1 | **Step appears** | both | Each step slides in; icon tile colored by outcome (gray, amber "!", red "✕") | 400ms; next step after 900ms (off) or 700–900ms (on) |
| L2 | **Mini pipeline** | on | Nine dots fill one by one with verdict colors; the current dot blinks accent; the step's small text names the stage | 300ms per stage, 1300ms for the causal check; blink 600ms loop |
| L3 | **Attack succeeded** | off | Result card turns red and **shakes** horizontally (−6, +6, −4, +3 px) | 500ms |
| L4 | **Attack stopped** | on | Result card turns green and lands (scale 0.96 → 1) | 500ms |
| L5 | **Summary** | below | Comparison sentence appears once both panes finish | instant |

The shake (L3) is used **only** for a successful attack. It is the one "alarm" motion in the system; don't reuse it for ordinary errors.

---

## 5. Playback controls

| Control | Behavior |
| :--- | :--- |
| **Replay episode** | Cancels any running episode, resets the screen, plays again from the first event |
| **Scenario** change | Same as Replay, with the new scenario |
| **Speed 0.5× / 1× / 2×** | Divides every *wait between events*. CSS durations stay the same, so 2× plays faster but each individual animation still reads correctly. |
| **Click a finished stage** | Shows that stage's explanation in the caption again |
| **Page load** | The finished episode is drawn instantly (so the first frame is complete), then the live animation starts after 1.2s |

Playing the finished state first is deliberate: a screenshot, a thumbnail or someone who glances away never sees an empty screen.

---

## 6. Reduced motion

When the OS has "reduce motion" turned on (`prefers-reduced-motion: reduce`):

- All CSS animations and transitions shrink to 0.01ms, so every state change still happens, just without movement.
- Typing is skipped; actions appear in full at once.
- The order of events and the waits between stages stay, so the story still unfolds step by step.

In React with Framer Motion, use `useReducedMotion()` and pass `transition={{ duration: 0 }}` when it returns `true`, or wrap the app in `<MotionConfig reducedMotion="user">`.

---

## 7. Rebuilding the motion in React

Recommended: **Framer Motion** for arrivals and presence, **plain CSS** for loops and the track. Suggested mapping:

| Mockup | React approach |
| :--- | :--- |
| M1 packet/fill (`--p` variable) | Keep as CSS: set `style={{'--p': progress}}` on the track; transitions stay in CSS |
| M2 spinner, M9 dots, M16/M17 loops | Keep as CSS keyframes (Tailwind `animate-spin` or custom keyframes) |
| M3 verdict pop, M11 comparator | `<motion.span key={verdict} initial={{scale:.7}} animate={{scale:1}} transition={{type:'spring', stiffness:500, damping:18}} />` (the changing `key` replays the pop) |
| M8 run cards, M15 log lines, L1 steps | `<AnimatePresence>` + `initial={{opacity:0, y:8}} animate={{opacity:1, y:0}}` |
| M6 highlight, M13 strike-through | Keep as CSS classes toggled from state (`flag`, `blocked`, `cut`) |
| M10 typing | A `useTypewriter(text, msPerChar)` hook that returns the growing substring |
| M14 outcome, L3/L4 results | `motion.div` with `animate` variants: `land` and `shake` (`x: [0,-6,6,-4,3,0]`) |

**Sequencing in React:** don't chain animations with timers. Each component animates when *its* data arrives. For example, `ProbeRun` shows thinking dots while `action` is `undefined` and types it out when it arrives. For Replay, a small player pushes stored events into the same store with delays taken from their timestamps (see [react-migration.md](react-migration.md) §6).

---

## 8. Adding a new animation: checklist

- [ ] Which real event triggers it? If none, don't add it.
- [ ] Which kind is it: travel, work or arrival?
- [ ] Uses the easing and duration tokens from §2
- [ ] Still makes sense at 2× speed
- [ ] Has a reduced-motion version (usually: no movement, same end state)
- [ ] Doesn't reuse the shake (reserved for "attack succeeded")
- [ ] Added to the catalogue in this file
