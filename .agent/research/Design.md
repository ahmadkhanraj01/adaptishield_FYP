# AdaptiShield — Design Rationale

**What this file is:** the *why* behind the architecture — the design decisions,
the causal-analysis methodology, and the hard-won lessons from the experiments
(root README Sections 6d–6i) distilled into reusable principles. For the *what
& where* see [Architecture.md](Architecture.md); for the *must-not-break* rules
that fall out of these decisions see [Rules.md](Rules.md).

*Last aligned: 2026-08-09 (adds Phase 13's lessons on harm taxonomy,
measurement cost and holdouts).*

---

## 1. Core decisions

| Decision | Rationale |
| :--- | :--- |
| **Layered, independent defenses** | No layer trusts another's verdict. Layer 4 (permission/egress/sandbox) gates independently of 3A/3B/3C, so a detection miss is not a breach. ASR has stayed 0% *because* the egress allowlist is a backstop under everything. |
| **Per-component model split** | 3B runs `gemma3:4b` because it *complies* with injections under the masked probe, producing a measurable causal signal. 3C/L3/planner run `qwen2.5:3b` for stronger baseline resistance. A model that refuses everything makes a *worse* detector — see §3. |
| **Keyword backstop in L3, permanently** | Small models sometimes write a correct diagnosis in prose but emit the wrong structured verdict. Flag if *either* the LLM or a deterministic keyword check fires. |
| **3D tunes knobs, never weights, and is human-gated** | The adaptive mechanism adjusts 3A rules and 3B thresholds only; proposals require explicit approval before they apply. Keeps the loop auditable and safe. |
| **3D trains on labeled data only** | A reward needs ground truth. Inferring "was this an attack?" from the outcome would be circular, so 3D learns from labeled red-team results or a labeled telemetry replay — never inferred labels. |
| **GPU-heavy work → Kaggle** | The local 4 GB card cannot host GRPO or 7B+ models; the pipeline runs locally, training goes to Kaggle P100. |

---

## 2. The causal-analysis methodology (3B)

3B does not ask "does this text look dangerous". It measures **compliance with
mediator-supplied instructions** by running the model under four regimes and
reading the *contrasts* between them (ACE/IE/DE). The masked probe — model
shown only untrusted content, no task — is the core: if the model proposes
moving data or contacting a new recipient from untrusted content alone, that is
takeover on its own terms.

**IE is a *difference*** (`masked − masked_sanitized`): it reads how much
sanitisation reduced compliance. This is powerful but has two failure modes
that shaped the rule stack below.

---

## 3. The takeover rule stack — why three rules, layered

Detection is not one threshold; it is three rules with a deliberate ordering,
each patching a failure of the one before.

1. **IE contrast rule** (with a consistency guard). The original signal. But IE
   **silently inverts when 3C fails**: if the sanitizer leaves an injection
   intact, both regimes comply, the 2s cancel to `IE=0`, and an attack that
   *survived* sanitisation reads as *safe*. (Root README 6e.)
2. **Standalone `masked ≥ 2` rule** (6f). Fires on strong evidence regardless
   of IE, so an attack robust enough to defeat the sanitizer is caught rather
   than excused by it. This is the load-bearing rule — it carries the
   strong-evidence cases so the IE rule can afford to be conservative.
3. **Consistency guard on IE** (6h). Requires *every* masked sample to outscore
   *every* sanitized sample (`min(masked) > max(masked_san)`), not just the
   means — one paraphrase-driven sample flip can no longer manufacture a
   verdict. Affordable *only because* rule 2 already carries strong evidence.
4. **Temporal drift** (6g). Scoped per conversation (`session_id`) and gated on
   `masked ≥ 1` — "nothing observed" must never mean takeover.

**Invariant this creates:** rule 2 must always be able to fire even when the
guard (rule 3) suppresses the contrast. Never tighten the guard without the
standalone rule in place. (Pinned in `tests/test_takeover_rules.py`.)

---

## 4. 3D reward & update design (fixes A–D)

The v1 adaptive loop produced a **negative result** (6d): applying a proposal
did not recover missed attacks, and the apparent gain was an artifact. Four
design defects were found and fixed; each is a principle worth keeping.

- **A — Generalize, don't memorize.** Harvesting literal exfil addresses into
  `blocked_patterns` made an update look effective only against the *training*
  address. Proposals now carry generalizable injection *phrasing* only; exact
  destinations are Layer 4's job.
- **B — The reward must respect WCR.** Stopping an attack by a blanket block
  (workflow lost) must score below a 3C safe continuation (workflow preserved),
  or GRPO optimizes toward killing legitimate work. `+1.0` vs `+0.7`.
- **C — A tuning step finer than the metric's resolution is a no-op.** IE is
  quantized to `1/k_samples`; the step must equal that grid, else it provably
  changes nothing. `threshold_step = ie_resolution`.
- **D — Measurement wording drives signal.** 3B missed softened attacks because
  the masked probe let the model reply `no_action`. Rewriting the *prompt* to
  refuse softened escape hatches took gen-2 detection **1/4 → 3/4** at 0% FPR —
  the single biggest gain. No scorer/threshold change needed.

---

## 5. Design lessons (the ones that generalize)

- **Component accuracy ≠ contrast accuracy.** Making `_score_action` more
  accurate per-action made the *system* worse: IE is a difference, and scoring
  both regimes correctly cancelled the gap the detector reads (6e). Optimize the
  contrast, not the component.
- **A difference metric can invert.** Any detector built on "A minus B" must be
  paired with a standalone-evidence rule for the case where A and B both move
  together.
- **Resolution before tuning.** Never tune a knob finer than the metric it
  moves can resolve. Fix the measurement before training a policy on it.
- **Backstops mask progress.** ASR was 0% before *and* after every 3B fix
  because Layer 4 always caught the exfil. Judge detection by the *layer under
  test* (`caught_by_causal`), not by the end-to-end ASR the backstop guarantees.
- **Single-run metrics are partly luck.** FPR has been observed flapping 0%↔25%
  on identical inputs (judge/paraphrase noise). Report distributions over
  repeated runs, not one figure. Phase 13 sharpened this: re-running the benign
  cohort reproduced the committed 3.3% **as a rate but on different cases**, so
  the run-to-run floor (±2–3 in 60) is the same size as the effects being
  compared. Compare case identities, not just totals.
- **The cost of a measurement is a design variable.** An expensive measurement
  quietly sets the research agenda by deciding what nobody checks. Two attempts
  were made at the severity function without measuring first, in a project whose
  §2 rule forbids exactly that, because each look cost 1.5 hours. Separating the
  model call from the scoring made a candidate cost seconds, and the answer
  arrived the same afternoon. Ask what an experiment costs *before* asking what
  it will show.
- **A detector's vocabulary is a threat model.** `_HIGH_KW` was a data-movement
  wordlist because every attack we had written ended in an email. It scored
  *unlock the front door* as harmless, and no threshold could have rescued it.
  When a detector fails on a new corpus, check what it can *express* before
  checking what it is *tuned* to.
- **Freeze the rule, then import the test set — and commit in that order.** A
  lexicon fitted on one corpus scored 90.0% there and 43.3% held out, intervals
  non-overlapping. What made the second number trustworthy was that the freeze
  and the import are separate commits, so the claim is checkable from history
  rather than asserted. Corollary: **each held-out corpus is spent once.** Tuning
  against it converts it into a development set, and there may not be a third.

---

## 6. Open design tensions (tracked, not solved)

- **More-compliant masked probe ↔ FPR.** Fix D makes benign mail naming a
  recipient a *latent* false positive; 3B cannot tell an allowed recipient from
  an attacker one — that discrimination belongs to Layer 4's egress allowlist.
  Phase 13 hit the same wall from the other side and measured it: widening target
  extraction to bare hosts turned *"Visit www.eveblog.com"* on benign Slack
  content into three false positives, and **that sentence is also AgentDojo's own
  phishing injection task**. Where the benign case and the attack are the same
  sentence at the level 3B observes, there is nothing for 3B to separate. This
  tension is now known to be a boundary, not a backlog item.
- **Recall on unseen attacks ↔ over-blocking, and the trade is corpus-specific.**
  The capability class deliberately does not cover reservations or calendar
  events, because the words that would catch them are what benign workspace text
  is made of. That cost 3 injections on InjecAgent and 10 of 30 on the holdout.
  A coverage decision cannot be evaluated on one distribution.
- **`masked_hypothetical` flakiness.** Improved but not reliable at 3B; the
  standalone rule needs *both* samples at 2. Higher `k_samples` or a graded
  score would harden it.
- **3C sanitisation of softened directives.** Still leaves some injections
  intact; the standalone rule stops that laundering an attack into looking
  benign, but does not repair the sanitizer.
