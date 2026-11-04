---
tags: [adaptishield, hub, moc]
type: hub
---

# AdaptiShield

> **Adaptive Threat Modeling for Tool-Orchestrated LLM Systems in MCP Architectures**
> Muhammad Ahmad Khan (23JZBCS0238) · Aleena Khan (23JZBCS0229)
> Supervisor: Dr. Laeeq Ahmed · UET Peshawar (Jalozai Campus)

This vault is the **network view** of the project. Every claim, component,
finding and decision is one note, linked to the notes it depends on. Start here.

---

## Where it stands right now

**The research phase closed on 15 September 2026** →
[[Entry XXVIII — The Research Is Complete]]. What remains is the write-up in the
authors' own words (repo `writeup/`) and administration.

See [[Current Numbers]] for the live figures. In one line: **detection 96.7%
(116/120), FPR 3.3% against externally-authored benign data, 501 deterministic
tests, ~93% built, evidence complete for the paper as drafted**, and the adaptive
layer honestly proposes a **no-op**.

**Phase 7 is done (8 Aug 2026)** — the comparative claim the thesis was framed
around is measured: [[ASR]] `static_only` **71.4%** → `full` **14.3%**, with
**18/21** stops attributed to 3B and **zero** detection stops possible without it →
[[Phase 7 Repaired — The Causal Sub-Layer's Marginal Detection]].

**Phase 10 is done too** — the external baseline a reviewer will demand, because
`static_only` is *our* ablation. Spotlighting (datamarking) has **no measurable
effect**: 34.8% → 33.3% steered, McNemar **p = 1.00** →
[[Phase 10 — Spotlighting Has No Measurable Effect]].

And the last instrument question behind it is closed: refusal-shaped output does
**not** inflate 3B's regime severities — 0 of 209 recorded severity-2 masked samples,
positive control passing → [[3B's Refusal Exposure Is Live and Unrealised]].

**Phases 11 and 12 are done too.** Phase 11: **only two layers do anything** — 3B on
detection, 3C on workflow continuation, four components at 0/0 →
[[Phase 11 — Only Two Layers Do Anything]]. Phase 12: **detection falls 96.7% → ~18%**
on externally-authored attacks, because 90% of [[InjecAgent]] is address-free →
[[Phase 12 — Detection Is 18% on Someone Else's Attacks]].

The immediate task is **the severity function** → [[Backlog]] item 1. Phase 12 turned
it from a 3-case tail into the one thing separating our number from anyone else's.

---

## The four ways in

| If you want… | Go to |
| :--- | :--- |
| The idea and why it is a research problem | [[Research Question]] |
| What is built and how a request flows | [[Defensive Stack]] |
| What has actually been established | [[Findings Index]] |
| The chronological story | [[Research Log Index]] |

---

## The core argument, as a chain

1. A tool-using LLM cannot separate instructions from data → [[Indirect Prompt Injection]]
2. Keyword filtering fails on softened phrasing → [[Research Gap]]
3. So ask a causal question instead of a lexical one → [[Causal Measurement Approach]]
4. Which requires a trusted/untrusted partition to have anything to mask → [[Layer 1 — Input and Supply Chain Screening]]
5. Measured across four counterfactual runs → [[Four Probe Regimes]] → [[ACE IE DE]]
6. Detection is not one threshold but three layered rules → [[Takeover Rule Stack]]
7. A confirmed takeover is answered by repair, not termination → [[Safe Continuation]]
8. And the defense tunes its own knobs under a human gate → [[3D Adaptive Threat Model]] → [[Layer 5 — Human in the Loop]]

---

## The three results that matter most

- **A measured negative beats an unmeasured positive** — [[6l — No Natural Gap at Scale]], [[The Adaptive Layer Proposes a No-Op]]
- **A defense measured only against its author's corpus measures the author's imagination** — [[6n — A Corpus That Can Fail]]
- **The instruments failed more often than the mechanisms** — [[Instruments Fail More Than Mechanisms]]

And the positive one, now that it is measured: **the causal sub-layer stops what
the static layers cannot** — 57 points of ASR, and the static allowlist turns out
to contribute *nothing incremental* once 3B is on →
[[Phase 7 Repaired — The Causal Sub-Layer's Marginal Detection]]

---

## Sections

- [[Vault Map]] — conventions, folder layout, how to extend this vault
- [[Source Documents]] — which repo file each note came from
- [[Phase Roadmap]] — the 10 phases and their state
- [[Open Questions]] · [[Backlog]] · [[Rules and Invariants]] · [[Traps]]
- [[How to Run]] · [[Test Suite]] · [[Machine and Environment]]
