---
tags: [adaptishield, open, done]
type: open
priority: 0
status: done
---

# ✅ Done — Repair the Phase 7 Benchmark

**Completed 8 August 2026.** All four steps done, benchmark re-run (216 cases),
result recorded → [[Phase 7 Repaired — The Causal Sub-Layer's Marginal Detection]].

**The question it had to answer is answered.** *Does the causal sub-layer detect
attacks static defenses miss?* — **yes, and by a wide margin**: ASR
`static_only` **71.4%** → `full` **14.3%**, with **18 of 21** stops attributed to
3B and **zero** detection stops possible in `static_only`.

## What was done

1. ✅ **Destinations** — malicious vectors moved to `LEGIT`; absorbable vectors
   **6 of 7 → 1 of 7**. V3 kept on `EXFIL` deliberately. This turned out to be a
   *correction*, not a workaround: the HTTP destination of a `send_email` call is
   the mail host, not the recipient's domain.
2. ✅ **Per-layer attribution** — `evaluation/attribution.py`. Names the first gate
   that refused **and** the later gates that would also have refused, so
   [[Backstops Mask Progress]] is visible in the output instead of inferred
   afterwards.
3. ✅ **Ten external benign vectors** (stride-sampled AgentDojo), a **separate
   cohort** from V8.
4. ✅ **Re-run** — plus a run manifest, which was not in the original four steps
   but is required by Rules §7.

Two defects surfaced during the repair, both hidden by the old exfil destinations:
**V7 could never fail the permission check it existed to test**, and **a `blocked`
case could report `reached_tool=True`**. Both fixed and pinned by tests
(135 → **161**).

## ➡️ The next task is now Phase 10

→ [[Backlog]]. The evidence chain is 7 → **10** → 11 → 12 → 13, and Phase 7 is
closed. Phase 10 is an **external baseline** (spotlighting / data-marking) on the
same corpus, seeds and model tags — because `static_only` is our own ablation and
a reviewer will not accept it as the comparison (Rules §7).

The infrastructure this repair built makes Phase 10 much cheaper: a new arm is a
`PipelineConfig` value plus a `defended_by` label, and the attribution table will
say what the new arm actually does rather than what it is supposed to do.
