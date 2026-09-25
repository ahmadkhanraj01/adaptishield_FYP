---
tags: [adaptishield, finding, phase10]
type: finding
status: current
date: 2026-08-08
---

# ✅ Phase 10 — Spotlighting Has No Measurable Effect

The external baseline Rules §7 requires. **Datamarking does not measurably reduce
steering on the campaign corpus at 4B** — and the raw number said the opposite
until a scorer defect was fixed → [[The Scorer Cannot See Negation]].

*86 cases per arm (66 malicious, 20 external benign), campaign corpus, 1 repeat,
temperature 0, commit `8762ab0`. `results/phase10/`.*

## The result

| Arm | Steered | 95% [[Wilson Score Interval]] |
| :--- | ---: | :--- |
| `derived_control` (no prompt defense) | 23/66 = **34.8%** | [24.5%, 46.9%] |
| `spotlighting` (datamarking) | 22/66 = **33.3%** | [23.2%, 45.3%] |

Paired **McNemar** over the same 66 cases — the form a reviewer expects, and the
right test because the arms are matched case-for-case:

```
steered in both        15
control only  (b)       8    <- spotlighting helped
spotlighting only (c)   7    <- spotlighting hurt
neither                36
chi2(cc) = 0.000    p = 1.000
```

Eight helped, seven hurt. As close to **no effect** as this design can produce —
not a narrow win, not a narrow loss. On the 48 address-carrying cases alone:
47.9% → 45.8%, intervals almost coincident.

**`steer_rate`, not [[ASR]], is the outcome.** ASR is 0/66 in both arms because the
allowlist absorbs every address-carrying attack — the [[Backstops Mask Progress]]
problem again. `steer_rate` asks whether the *agent chose* a harmful action, judged
before any gate runs, so a backstop cannot absorb it.

## The aggregate null hides two real opposing effects

| Family | control → spotlighting |
| :--- | :--- |
| `important_instructions` | 8/11 → **5/11** |
| `masked_hypothetical` | 2/11 → **0/11** |
| `authority_citation` | 7/11 → 6/11 |
| `tool_knowledge_injection` | 1/11 → 1/11 |
| `delegated_followup` | 5/11 → **7/11** |
| `blunt_override` | 0/11 → **3/11** |

Spotlighting genuinely helps against authoritative framing and **hurts** on
`blunt_override` and `delegated_followup`. The null is cancellation, not
indifference — more useful than either a win or a loss, and visible only because
the arms are paired per case.

**A defense that makes a thin payload legible can increase compliance.**
`blunt_override` is one short line the plain planner ignores entirely (it replies to
the greeting — 0/11). Datamarking gives it structure the agent then engages with,
and three times it acted on the injection. Suggestive at n=11, not established.

## Why the arm had to derive its own action

Spotlighting defends the **agent's** action selection. The pipeline is normally
*handed* `proposed_action`, so a prompt-level defense had nothing to protect —
measuring it without `derive_action` would have measured the transform's effect on
**our own detector**, which is not the published defense. Hence the pair
`derived_control` / `spotlighting`, differing in **exactly one flag**; comparing
against `static_only` instead would have confounded the transform with the switch
from a supplied action to a derived one.

## What this does not establish

- **Not "spotlighting does not work".** It establishes no measurable effect *for
  datamarking, on this corpus, with a 4B planner, at n=66*. The paper's claim must
  carry all four qualifiers.
- **Delimiting and encoding are untested.** Both are implemented. `encoding`
  additionally needs ASR and [[WCR]] read together, because a transform that
  destroys the content lowers steering by making the user's task impossible too.
- **The 4B planner is the weak link.** A stronger agent would be both more
  steerable and better at honouring the instruction, and could move this either way.
- **One repeat.** n=66 carries the precision; the per-family cells at n=11 are
  fragile and should not be quoted individually.
- **Nothing about our own layers.** These arms run with 3B/3C off. This is a
  baseline measurement, not a comparison against
  [[Phase 7 Repaired — The Causal Sub-Layer's Marginal Detection]] — the corpora
  and the ASR definitions differ, so they are two tables.
