# AdaptiShield — Supervisor Brief

**What was achieved, why it is different, and why it is a defendable journal paper.**

*Prepared 13 August 2026 · **updated 12 September 2026** · every figure below is regenerable from a committed command (`results/` + the deterministic test suite).*

> **What changed since the August brief.** All three items on the hardening list are closed. The in-corpus headline is now a committed artifact; the single-model exposure has been tested and the finding replicates on a second model; the related-work pass is done and one published number we had been holding back turned out to be wrong. **The only thing still blocking submission is the journal decision in §7** — and the 14 September target is now two days away, so it needs either confirming or moving.

---

## 1. In one paragraph

We built a six-layer defence against **prompt injection** — the attack where an AI agent reads attacker-written text (an email, a ticket, a tool result) and follows it as if it were a user instruction. Its distinguishing element is a *causal* detector: rather than asking "does this text look dangerous", it runs the agent's decision with and without the suspect text and treats a change in behaviour as evidence. We then did what most work in this area does not: **we measured the defence against externally-authored attacks, against a published baseline, and component by component — and we report honestly where it stops working.** The result is a rigorous negative-leaning systems paper with a single, precisely-bounded finding, backed by pre-registered experiments and a fully reproducible artifact.

---

## 2. What was built

A complete, working pipeline (≈93% built, **502 automated tests, ~8 s, no model/network/GPU required**):

| Layer | Function |
| :--- | :--- |
| 0–1 | Server-trust and input/provenance screening |
| 2 | Agent control plane with the security sub-layer (**3A** policy, **3B** causal detector, **3C** sanitiser, **3D** adaptive tuner) |
| 3 | Tool-execution plane + response screener |
| 4 | Permission scope, egress allow-list, sandbox, telemetry |
| 5 | Human-in-the-loop review console |

The system runs locally on small open models and is entirely self-contained.

---

## 3. What was measured — the evidence

Every number carries its source, and cohorts are never pooled where the population is stratified.

| # | Finding | Number | Source |
| :--- | :--- | :--- | :--- |
| 1 | **Only 2 of 6 components change any outcome** on our corpus (ladder + leave-one-out ablation agree on every row) | 3B: 18/0, *p* = 7.6×10⁻⁶ · 3C: 18/0 | Phase 11 |
| 2 | **A published prompt-level defence (spotlighting) has no measurable effect** | 34.8% → 33.3% steered, McNemar *p* = 1.00 | Phase 10 |
| 3 | **Detection collapses on externally-authored attacks**, and the split is the finding | 96.7% → ~18%; **96.7%** where a target is named vs **10.0%** where not | Phase 12 |
| 4 | Collapse is **stable across 3 recordings** — an ~86-point gap against a 1-case wobble | target 96.7%×3 (0 unstable); no-target 13/10/10% | Phase 14a |
| 5 | The obvious fix (widen the harm vocabulary) **generalises about half** | in-sample 90.0% → holdout **43.3%**, intervals non-overlapping | Phase 13 |
| 6 | **The adaptive layer's contrast is zero on 80% of realistic turns** — why self-tuning has nothing to learn (2 pre-registered runs) | `orig == masked` on 24/30 turns | Phase 15 |
| 7 | An overnight follow-up measured *why*: the blunt scorer destroys signal, but a continuous replacement saturates on a small model | 35/45 forced choices saturated | logprob probe |
| 8 | **The collapse is not a property of our model.** Repeated on a second probe model of a different lineage — the gap comes out *wider* | 96.7%/13.3% → **100.0%/10.0%**; 58 of 60 cases agree | Phase 16 |

**The whole paper reduces to one defendable claim:** *the causal contrast carries discriminative signal when the injected content names a liftable target (an address or link), and close to none otherwise.* Findings 3, 5 and 6 are all consequences of that one property.

---

## 4. How this is different from a typical student project

This is the part worth emphasising to reviewers, because it is what makes the work publishable rather than merely competent.

- **It measures its own defence against outside attacks and an outside baseline.** Most injection-defence papers report only on attacks their own authors wrote. We show — with numbers — that this is exactly why such results look strong, and what happens when you stop doing it.
- **The negative results are the contribution, not an embarrassment.** We found a precise, general boundary line for a whole class of defence. That tells the next research team where to dig, which a "97% accuracy" paper does not.
- **Every experiment that could fool us was pre-registered.** The generalisation test froze its rules and committed the holdout corpus *before* the result was known; the adaptive experiment committed its success criteria and cohort before running, and honoured its own stop rule after two attempts.
- **Instruments are treated as first-class.** Three findings were caught by measurement tools we built to check something else, and we report the *withdrawn* versions alongside the corrected ones — a benchmark whose first result was invalid by construction, a baseline whose sign its own scorer had reversed, an ablation that called a working component inert. This is the methodological spine of the paper.
- **It is fully reproducible.** The `results/` tree, run manifests, and a 502-test deterministic suite are the artifact. No number in the paper exists without a committed command that regenerates it.

---

## 5. Why it is defendable

A viva or a reviewer will push on these, and each has a prepared, evidence-backed answer:

| Likely challenge | Answer |
| :--- | :--- |
| *"Isn't a negative result just a failed project?"* | No — the boundary is a general finding about causal injection detection, backed by three independent phases. Venues like IEEE Access and Computers & Security explicitly accept rigorous negative and systems results. |
| *"Is the 96.7% → 18% drop just noise?"* | No — measured 3× per stratum; ~86-point gap against a ≤1-case run-to-run spread. |
| *"Did you tune your way to the generalisation number?"* | No — the lexicon was frozen and the holdout committed before the result was seen (verifiable from commit history). |
| *"The system is called *Adaptive* but you say it doesn't adapt."* | The adaptive mechanism works on a constructed gap and generalises; we measured that no such gap arises naturally, and (overnight) *why*. We recommend the paper title claim only what is proven — see §7. |
| *"One model, one scorer — is this general?"* | **Now partly answered by measurement.** The stratification replicates on a second model (`llama3.2:3b`): a 90.0-point gap against the incumbent's 83.3, agreeing on 58 of 60 cases. What remains stated as a limitation: both models are 3–4B and locally hosted, one scorer sits behind every number, and the multi-turn result was not repeated. Two further candidates were disqualified on a compliance pre-flight, which is itself reported. |

---

## 6. Publication readiness

| Piece | Status |
| :--- | :--- |
| System + 502-test artifact | ✅ complete |
| All 16 experimental phases | ✅ complete, all numbers frozen |
| Manuscript — 13 numbered sections (~9,800 words), 12 tables, 6 figures | ✅ complete in draft |
| Figures — 4 core, generated from results, embedded in text | ✅ complete |
| Related-work section | ✅ done — six missing references traced, and §2 now places the three defence families by what each takes as evidence |
| Author block — ORCIDs, membership grades, author order, funding | ⏳ **needs your input** (author order is yours to set) |
| **Journal choice** | 🔵 **needs your decision** |

**Recommended venue: IEEE Access** — first decision in ~4–6 weeks (fits the deadline), and explicitly tolerant of systems work with negative results, which is what this is. *Computers & Security* is a stronger topical fit but its 3–6 month timeline likely misses the degree deadline; *IEEE TDSC* is out of reach on time.

---

## 7. Two decisions I would like your view on

1. **Journal choice, and the date** (above) — the only item genuinely blocking submission. It sets page limits, the artifact-availability requirement, and author order (with Aleena Khan and Dr. Laeeq Ahmed). **The 14 September target is two days away.** Everything measurable is finished; what is not finished is this decision and the author block that depends on it. I would rather move the date deliberately than submit against it by default — but if IEEE Access is confirmed, the remaining work is a day.

2. **Paper title.** Keep *AdaptiShield* as the system's name, but I would argue the paper's *title* should claim what the evidence supports — the operating envelope and limits of a causal injection defence — rather than lead with "adaptive", which the paper itself reports as a measured no-op. Over-claiming is punished harder by reviewers than an honest negative result.

---

## 8. The one-line summary for the abstract

> We did not build a defence that failed. We built one, measured precisely where and why it stops working, and turned that boundary into the contribution — with every number reproducible and every headline experiment pre-registered.
