---
tags: [adaptishield, meta]
type: meta
---

# Source Documents

Every note in this vault derives from one of these files in `~/adaptishield`.
Where they disagree, the repo wins — but note the repo files themselves have a
hierarchy of authority, recorded below.

| File | Authority | Feeds |
| :--- | :--- | :--- |
| `README.md` | Single source of truth for build state (v16) | [[Current Numbers]], [[Defensive Stack]], [[Findings Index]], [[How to Run]] |
| `handover.md` | Current numbers, next task, traps (written 26 Jul 2026 21:36) | [[Next Task — Repair the Phase 7 Benchmark]], [[Traps]], [[Backlog]] |
| `researchworksofar.md` | **Research log Volume I**, entries I–XIV — **closed, never edited** | [[Research Log Index]] entries I–XIV |
| `research_work_so_far.md` | **Research log Volume II**, entry XV onward | [[Entry XV — Where a Fix Belongs]] |
| `Architecture.md` | Structural map — what exists and where | [[Defensive Stack]], the Layer notes, [[Request Flow]] |
| `Design.md` | Rationale — why it is built this way | [[Takeover Rule Stack]], [[Design Lessons]] |
| `Rules.md` | Invariants that must not break | [[Rules and Invariants]] |
| `Phase.md` | Roadmap by phase | [[Phase Roadmap]] |
| per-folder `README.md` | File-by-file tables for each layer | the Layer notes |
| `AdaptiShield_Architecture_v3.drawio(.png)` | Diagram — **not author-written, unreviewed** | — |

## The two-volume rule

The research log is split deliberately. **Volume I (`researchworksofar.md`) is
closed and is not edited**, including the entries whose conclusions were later
contradicted. Volume II (`research_work_so_far.md`) continues the numbering from
XV. Leaving the superseded conclusions standing is intentional: see
[[Instruments Fail More Than Mechanisms]] for why the corrections carry more
weight than the results.

## Not yet in this vault

Log entries I–IX are summarised rather than reproduced — they are the proposal,
the literature review, and the architecture specification, and their *conclusions*
live in the `01 Foundations` and `02 Architecture` notes instead (start at
[[Research Question]] and [[Defensive Stack]]). The full prose is in
`researchworksofar.md`.
