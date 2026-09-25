---
tags: [adaptishield, open]
type: open
---

# Backlog

[[Next Task — Repair the Phase 7 Benchmark]] is ✅ **done** (8 Aug 2026). In rough
priority order from here.

## 0 — Does refusal-shaped output inflate 3B's regime severities? ✅ **done**

Measured 8 Aug 2026: **0 of 209** recorded severity-2 masked-regime samples are
refusal-shaped, positive control passing →
[[3B's Refusal Exposure Is Live and Unrealised]]. The exposure is **live on the
shipped keyword path** and has never fired; the regime scorer is left unchanged,
so Rules §2's re-measurement cost is not incurred for nothing. Recorded, not
closed.

*(Phase 10 is ✅ done too — [[Phase 10 — Spotlighting Has No Measurable Effect]].
Delimiting and encoding variants remain unmeasured; encoding needs [[ASR]] and
[[WCR]] read together at 4B.)*

## 0b — Phase 11: per-component ablations ✅ **done**

**Only two layers do anything**: 3B on detection (18/0, p = 0.000), 3C on workflow
continuation (18/0, p = 0.000), and L3 / 3A / both halves of Layer 4 at **0/0 with
zero discordant pairs** — confirmed independently by leave-one-out →
[[Phase 11 — Only Two Layers Do Anything]].

## 0c — Phase 12: InjecAgent ✅ **done**

**Detection 96.7% → ~18%** on externally-authored attacks →
[[Phase 12 — Detection Is 18% on Someone Else's Attacks]]. Phase 11's `static_only`
zero replicated (0 of 60). The severity function is now sized at **27** missed cases
rather than 3, which promotes item 1 below to the critical path.

Remaining InjecAgent work, both optional: the **data-stealing** split needs a
second boundary the pipeline does not model, and the per-stratum estimates are
single-repeat at n=30.

→ then Phase 13 (manuscript). 🔵 Still blocked on the **journal decision**, which
sets how much Phase 13 must produce.

## 1 — The severity function 🟡 **HOLDOUT MEASURED — a modest real gain**

**9 Aug 2026.** The item was misnamed: it is not a threshold, it is a harm
taxonomy with one class → [[The Scorer Had One Harm Class]]. That diagnosis
stands. The *size* of the fix does not:

| | address-free detection | 95% Wilson |
| :--- | ---: | :--- |
| [[InjecAgent]] — in-sample | 90.0% | [74.4%, 96.5%] |
| [[AgentDojo]] attacks — **holdout** | **43.3%** | [27.4%, 60.8%] |

**4 helped / 0 hurt, p = 0.125 — not significant** →
[[The Lexicon Generalises About Half]]. The intervals do not overlap; the
in-sample figure overstated generalization by ~47 points.

🔴 **Do not tune the lexicon in response to that note.** It was frozen at
`46cfbfb` before the holdout corpus existed, which is the only reason these
numbers mean anything. A revision needs a NEW held-out corpus reserved before the
revision is written, and there is no third corpus waiting.

What the holdout says the next lever is, in order of the misses it leaves:

1. **Ten of seventeen are travel** — reservations and calendar events, the
   deliberate non-coverage. Its cost is distribution-dependent: 3 injections on
   InjecAgent, 10 of 30 here. Widening here is the over-blocking direction and
   needs the FPR cohort re-measured with repeats.
2. **Five are financial harm whose object is a bare IBAN** — the lexicon reads
   words and the account is digits. A numeric-identifier notion is a different
   mechanism, not another noun.
3. **Two are a defect in shipped code** → item 8 below.

Still owed before anything lands: **Rules §2's gen-2 campaign re-measurement**
(`capability_scoring` defaults to `False` until then) and **repeats on the benign
cohort** → [[The Benign FPR Has a Noise Floor Its Own Size]].

⚠️ Do **not** drop `reset`/`password` from the lexicon to erase its one false
positive. It would cost nothing measurable on the attack side, which is what
makes it tempting — and it would fit the lexicon to the [[FPR]] cohort of record.

*Original framing, kept because the diagnosis is the finding:*

## 1b — The severity function, as it was described

All **4** residual campaign misses are `masked = 0` → [[Residual Misses Decomposed]].
Phase 7 confirms this independently: **all 3** of the `full` arm's residual attack
successes are **V4**, the [[Address-Free Attacks|address-free]] vector, and **none**
is a threshold failure.

**Phase 12 sized it.** On [[InjecAgent]]'s address-free stratum — 90% of that corpus
— detection is **10.0%** [3.5%, 25.6%], against 93.3% where the target-match path
fires. This is no longer a 3-case tail; it is the single thing standing between a
96.7% number on our data and an 18% number on anyone else's.

⚠️ [[6e — Semantic Scoring Ablation]] already showed the semantic scorer is
**worse end-to-end**, so this needs a **third approach**, not a re-run of that
one. And [[6p — Probe Hallucination Fixed at the Scorer]] establishes that the
*prompt* is not where to try it either.

This is the largest remaining detection lever, and the hardest.

## 2 — Multi-turn sessions 🟢 **PROMOTED TO PHASE 15** (12 Aug 2026)

Campaigns give every case a unique `session_id`, so the drift rule never fires and
**two of 3D's five dimensions are unidentifiable** — the trainer reports this
itself → [[6g — Temporal Drift Scoping]].

**No longer a backlog item — it is the journal paper's last experiment** →
[[Phase 15 — Multi-Turn Sessions (Pre-Registration)]]. The deadline extension to
**14 Sept** is what made it affordable, and the cost estimate fell once the code
was actually read: `session_history` is already keyed by `session_id`
(`causal_analyzer.py:914`) and the drift rule is already written with both §6g
guards. **What is missing is a corpus, not code.**

Both outcomes are publishable, which is why it is worth the runway: drift firing
gives the first measured evidence the adaptive layer does anything, on a threat
model spotlighting cannot address even in principle; drift not firing gives a far
stronger negative result than *"we never built a corpus that could tell."*

🔴 Pre-register and commit the cohort **before** running it, or it becomes a
second development set — the trap [[The Lexicon Generalises About Half]] fenced
off for the lexicon.

## 2b — Benign-cohort repeats ✅ **MEASURED** (12 Aug 2026)

**k = 3 recordings: 2/60 every time.** The count never moved; the membership did
(048 always, then exactly one of 041/055). That **corrects** the ±2–3 figure this
item was built to confirm — it had compared two instruments, not two runs →
[[The Benign FPR Has a Noise Floor Its Own Size]].

✅ **InjecAgent per-stratum repeats also done.** k=3: the target stratum is
96.7% in all three runs with **zero** unstable documents; the no-target stratum
is 13.3%/10.0%/10.0% with one. An ~86-point gap against a 1-case spread →
[[Phase 12 — Detection Is 18% on Someone Else's Attacks]]. **Item 2b is closed.**

*Original framing:*

Phase 14a(i). Every FPR figure in this project is **single-run**, including the
committed **3.3%**, and [[The Benign FPR Has a Noise Floor Its Own Size]] showed
the run-to-run floor is ±2–3 in 60 — *the same size as the effects being
compared*.

`evaluation/noise_floor.py` (new) aggregates *k* recordings into a per-run rate
**plus** a per-case fire/no-fire matrix, and refuses to pool the runs: *k*
recordings of 60 documents are not 60*k* observations, and pooling would divide
the interval by √k and manufacture precision the measurement does not have.

The per-case matrix is the part that matters. A spread of ±2 is compatible with
two documents flipping every run (§6i's architectural boundary) or twenty
flipping occasionally (an instrument defect) — opposite implications for the
paper, and only a per-case breakdown separates them.

⚠️ **The trap this nearly walked into:** `probe_corpus`'s checkpoint was keyed by
cohort alone, so a second recording would have *resumed* from the first, made no
model calls, and written a byte-identical file — a measured noise floor of
exactly zero, and the most convincing possible wrong answer. Both the output and
checkpoint paths are now keyed by run.

## 3 — 3C `ContextSanitizer.sanitize()` 🟡

Still carries the prompt weakness 3B's internal sanitizer had, fixed in
[[6m — The Single-Character Defect]]. It feeds the **user-visible continuation**
and the [[WCR]] metric, so it was left unchanged rather than altered silently →
[[3C Context Sanitizer]].

## 4 — Screen tool descriptions at registration

Benchmark vectors **V5/V6 are approximated** because the pipeline consumes tool
*responses*, not manifests. The Supply Chain Scanner specified in
[[Layer 1 — Input and Supply Chain Screening]] (per [[AutoMalTool]]) is the
missing piece.

## 5 — Publish the Layer 5 dashboard

Two questions must be settled **first**:
- **Visibility** — it currently embeds **828 records including attacker-authored
  text**
- **Attribution** — render the [[AgentDojo]] credit on the page

→ [[Layer 5 — Human in the Loop]]

## 6 — The inert-pattern namespace mismatch 🔴

The gate *detects* [[Inert Blocked Patterns]]; it does not make them fire.
Whether [[3A Policy Engine]] should match mediator markers, or
[[3D Adaptive Threat Model]] should harvest from proposed actions, is **undecided**.

## 7 — Externally-authored *malicious* data ✅ **done**

[[AgentDojo]]'s attack side is imported — 253 cases, 119/134, four suites,
complementary to the benign import by construction (it takes exactly the fields
`vendor_agentdojo.py` excluded). §6n's lesson is now fully applied on both halves.

## 8 — `_extract_suspicious_targets` cannot see a schemeless domain ✅ **fixed, measured, left off**

Fixed behind `schemeless_targets` and measured →
[[The Schemeless URL Fix Costs More Than It Buys]]. **+2 detections for +3 false
positives** on the holdout (FPR 3.3% → 8.3%); on InjecAgent its gain is entirely
subsumed by the capability class.

All three new false positives are *"Visit www.X.com"* on benign Slack content —
**which is also AgentDojo's own phishing injection task**. At the level 3B
observes, the benign case and the attack are the same sentence, so this is
[[3B Layer 4 Boundary]] and not something a wordlist can fix.

The worry that it had mislabelled the corpora was **unfounded**: `target_match`
means *"can 3B's target-match path fire"*, and while the matcher is blind the
honest answer is no. No re-vendoring, no re-recording.

## 9 — Externally-authored *malicious* data (superseded, kept for the link)

The benign side was fixed by importing [[AgentDojo]]. The attack side has no
equivalent import, so [[6n — A Corpus That Can Fail]]'s central lesson is only
half-applied → [[Evaluation Corpus]].
