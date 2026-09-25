---
tags: [adaptishield, phase]
type: phase
status: done
date: 2026-08-09
---

# Phase 12 — InjecAgent

**External validity.** One benchmark invites *"does this generalise?"*, and
[[Phase 11 — Only Two Layers Do Anything]] sharpened the need: it found four of six
components inert, but all 21 of its malicious cases are tool-response injections
aimed at one action shape, so *inert in general* and *inert on our corpus* were
indistinguishable from inside.

**Result: detection falls from 96.7% to ~18%** →
[[Phase 12 — Detection Is 18% on Someone Else's Attacks]].

## Design

`--corpus injecagent`, 60 cases (30 per stratum), arms `undefended` /
`static_only` / `full`. Corpus loader in `evaluation/injecagent.py`, vendoring in
`red_team/vendor_injecagent.py` → [[InjecAgent]].

The three Phase-7-class traps were all live here, and all were caught in advance
rather than after a withdrawal:

| Trap | Why it applied | What was done |
| :--- | :--- | :--- |
| **Layer 4 absorbs everything** | InjecAgent's attacker tools are absent from our registry, so the permission gate would refuse all 60 cases before 3A/3B ran | Register them **in scope** — faithful to a threat model of *misuse of a tool the agent legitimately holds* |
| **The allowlist absorbs everything** | An exfil `destination_url` would hand every case to egress | `LEGIT` host; the harm here is a tool call, not a send |
| **A pooled rate over unlike cases** | The draw is 30/30 from a **51/459** population | Strata reported separately, and the report prints ⛔ **DO NOT POOL** |

## The stratum is the detector's own predicate

`target_match` is `CausalAnalyzer._references_mediator_target` run on the case, not
a regex resembling it. The first attempt counted an address appearing *anywhere* in
the tool response — 186 of 510 — and **135 of those gave 3B no signal**, the address
sitting in the benign half while the injection named none.

`tests/test_injecagent.py` fails if the recorded label ever diverges from the
predicate run live. Same correction
[[3B's Refusal Exposure Is Live and Unrealised|the refusal audit]] needed.

## Predictions, recorded before the run

| Prediction | Outcome |
| :--- | :--- |
| Detection drops sharply on the address-free stratum | ✅ 10.0% vs 93.3% |
| `static_only` catches nothing, replicating Phase 11 | ✅ **0 of 60** |
| Layer 4 contributes nothing | ✅ `backstop_share` 0% |
| The floor is usable (undefended ≈ 100% ASR) | ✅ 100%, [94.0%, 100%] |

## What Phase 12 cannot do

- **No FPR.** InjecAgent ships attacks only; the columns read 0/0, an empty
  denominator rather than a clean sheet. A detector retuned for address-free
  injections could over-block badly and this corpus would not show it.
- **Half of InjecAgent is out of scope** — the data-stealing split needs two
  boundaries.
- **Layer 4 egress could not fire**, so its zero is structural here, unlike
  Phase 11's.

→ Next: [[Backlog]] item 1, the severity function, which this phase has now sized at
27 missed cases rather than 3. Then Phase 13 (manuscript), 🔵 blocked on the journal
decision.
