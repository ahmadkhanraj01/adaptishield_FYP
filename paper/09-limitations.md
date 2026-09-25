# §9 — Limitations

Stated at the granularity a replicator would need, and separated by whether they
bound the *result* or the *system*.

## Limits on what we measured

**Single model, single scorer.** Every number rests on one 4B model behind the
causal probe and one keyword scorer. The central finding — the causal contrast
being zero on 80% of turns — is a property of *that pair*, not of causal
detection in general. A scorer producing graded severities on address-free
content might restore the signal. We did not build one, and §6 is evidence that
doing so is harder than it looks: the obvious attempt generalized about half.

**Model choice is constrained, not free.** The probe needs a model that complies
under the masked regime. A more refusal-prone model produces no signal at all, so
the approach cannot simply be moved to a stronger, better-aligned model — the
property being exploited to *measure* the attack is the same property that makes
the model vulnerable to it.

**The benign corpus is 60 external documents.** Adequate for the reported
[0.9%, 11.4%] interval, but a reviewer may reasonably ask for more, and that
interval is wide enough that a two-point FPR difference is unresolvable.

**FPR reproduces as a rate, not per-document.** Three independent recordings of
the same 60 documents give 2/60 every time, but *which* documents fire changes:
one stable false positive, plus exactly one of two borderline documents per run.
Rate-level claims are safe; per-case attributions and one-case differences
between arms are not. This bounds several comparisons in §6 to "no measurable
change".

**Phase-15 sample size.** Three malicious sessions per run. This is an existence
question — *can the mechanism fire on a realistic conversation* — and is not a
rate. The negative result is strong not because n is large but because the
mechanism's *input* was measured at zero across all 30 turns.

**The second multi-turn cohort was written after seeing the first run's
trajectories.** No target trajectory changed and the criteria were identical, but
a reader cannot verify from outside that the content edits followed the
pre-declared targets rather than the direction of the miss. Both runs are
reported. This is a weaker guarantee than the first run's and we do not claim
otherwise.

**Single-repeat strata in §5.** The 96.7% → 18% collapse — the paper's flagship
negative result — rests on single-repeat estimates at n = 30 per stratum.

**Greedy decoding is not literally deterministic.** A fixed prompt returns
identical output in repeated trials, but across a full campaign 2 of 564 regime
severities were non-integral, concentrated on long unstructured benign documents.

## Limits on what the system can do

**The detector cannot separate an authorised recipient from an
attacker-controlled one.** A benign document containing a real action item naming
a real address is, at the level the causal analyzer observes, the same object as
an injection. This is not a defect to fix at that layer — it is what the egress
allowlist exists for — but it bounds what any purely causal detector at this
position can deliver, and it is one of our two persistent false positives.

**The probe fabricates actions on directionless benign content.** Shown a
document that instructs nothing, the model still proposes *an* action, because
the probe was deliberately tuned toward always finding one. On benign content it
invents. This is the largest single lever on FPR and remains open: three rounds
of prompt engineering aimed at it cost eight detections and were reverted.

**Schemeless hosts are invisible by default.** Target extraction requires a URL
scheme, so `www.attacker-host.com` in body text is not lifted. The fix exists,
is measured, and is switched off: it buys two detections for three false
positives, and all three are ordinary workplace chat containing a bare host —
which is also a real phishing injection in the benchmark. At the level observed,
the benign case and the attack are the same sentence.

**The drift rule requires a wholly high-impact conversation.** Session history
accumulates only on boundaries routed to causal evaluation, so a conversation of
low-impact turns punctuated by one high-impact call can never fill the window.
This is a scoping limit on the mechanism, not on our harness.

**Two components are evaluated by approximation.** Tool-poisoning and rug-pull
vectors are modelled at the nearest reachable point, because the pipeline
consumes tool *responses* rather than server manifests. §3's finding that the
screening layers are inert therefore holds for our corpus and does not generalize
to the attacks those layers exist for.

**The adaptive component's learned distribution is near-uniform.** Its argmax
comes from a minimal-intervention tie-breaker rather than from data. We do not
present it as a trained policy, because on every corpus we have it has nothing to
learn.

## What would change the conclusions

We list these because a negative result should say what would overturn it:

1. **A scorer with graded severities on address-free content.** The central
   finding is downstream of a two-valued scorer. If the contrast could be made
   non-zero on content lacking a liftable target, the IE and drift rules become
   testable for the first time and this paper's main claim would need re-testing
   rather than extending.

   *We ran a preliminary read-only test of this (`evaluation/logprob_probe.py`,
   `results/phase15/logprob_probe.json`): a forced-choice log-probability probe
   over the 15 Phase-15 turns, bypassing the integer scorer. Three results. (i)
   The quantisation does destroy signal — all 5 integer-flat turns showed a
   continuous contrast above 0.5 nats. (ii) But the dominant contrast (ACE) is
   as large on benign turns as on attacks — mean |ACE| 7.1 vs 7.5 nats, the
   largest of all on a benign turn — because it measures task-relevance, not
   attack. (iii) The sanitisation contrast (IE) is the only measure that
   separated the classes — exactly 0 on all 6 benign turns, non-zero on 3 of 9
   attacks — but those signals are 0.85–3.2 nats riding on saturated ~20-nat
   pedestals (35/45 forced choices saturated at >10 nats). So on a 4B model the
   naive continuous replacement does not cleanly separate; the sanitisation
   contrast in probability space is the one surviving thread, and pursuing it
   needs a larger, better-calibrated model. This moves the item from conjecture
   to a measured, bounded next step.*
2. **A larger multi-turn corpus with genuinely differential regimes.** If
   conversations exist where `orig` and `masked` reliably diverge without an
   address present, the drift rule's parameters become identifiable.
3. **A model whose masked-regime compliance is high but whose unmasked
   compliance is low.** That gap is precisely what ACE measures, and we observed
   it in 2 of 30 turns.
