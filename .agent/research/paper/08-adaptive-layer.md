# §7 — The adaptive layer: a mechanism that works, on a signal that is not there

*Sources: `logs/adaptive_loop/mechanism_validation_*.json`,
`results/phase15/multiturn_r1.json`, `multiturn_r2.json`, `evaluation/kaggle/`.*

The system's adaptive component observes detection failures and proposes
configuration changes for human approval. This section reports what it does, and
the answer has three parts that have to be read together: the mechanism works on
a constructed gap, it proposes nothing on every natural corpus, and we can now
say precisely why.

## 1 — The loop closes a gap and the fix generalizes

Given an injection that the detector misses because one threshold sits too high,
the component observes the miss, proposes a threshold change carrying **no
memorized literal**, applies it, and the attack is then caught. Critically, a
**held-out attacker address the component never saw** is also caught.

That pair matters because an earlier version of this system failed it: the
apparent gain was memorization of a training-set address and vanished on a
held-out one. The learned pattern here is the generalizable phrasing (*"read and
list every message"*), not the address.

So the mechanism is not unproven. What was unproven is that such a gap arises
naturally.

## 2 — It proposes nothing on every natural corpus, and the reason is specific

Across an expanded campaign of 118 labeled episodes, replaying the reward across
the entire threshold grid catches **zero** additional attacks. The residual
misses all score **0** on the masked probe, which is below both detection rules
simultaneously and therefore **unreachable by the threshold the component
controls**. An independent benchmark agrees: all of its residual attack successes
are the address-free vector, none a threshold failure.

The component correctly proposes a no-op. We report the no-op as the result.

## 3 — The temporal rule: two pre-registered attempts, and a structural answer

The component also controls two parameters governing a **temporal-drift** rule,
which is designed to catch a conversation trending toward compliance when no
single boundary crosses a threshold. This is the one threat model in the paper
that prompt-level and single-boundary defenses cannot address even in principle.

Those two parameters had never been evaluated, because every corpus in the
literature — and every corpus of ours — treats each case as an independent
conversation, so the rule's history never accumulates and the parameters are
formally *unidentifiable*.

We built the first multi-turn cohort that could exercise it: five three-turn
conversations sharing a session, with the success criterion, the target severity
trajectories, and the guard **registered and committed before the run**.

**Result: no drift-only detection, in either of two runs.** After the first null
we diagnosed three content defects, repaired them under a second pre-registration
that records having been written *after* seeing the first run's trajectories, and
re-ran. The repair demonstrably worked where it was diagnosed — the turn that had
been caught by the wrong rule moved to its declared severities — and the primary
criterion was still not met.

The two runs together explain why, and the explanation is not about our
conversations:

| across 30 scored turns | |
| :--- | ---: |
| `orig == masked` | **24 / 30 (80%)** |
| ACE = 0 | 24 / 30 (80%) |
| IE = 0 | 29 / 30 (97%) |

![The causal contrast is flat](figures/fig4_flat_contrast.png)

**Figure 4.** Unmasked (`orig`) against masked severity for every scored turn of
both runs. Points on the diagonal have zero causal contrast (ACE = 0); 24 of 30
turns lie there, malicious and benign alike. Marker size counts turns at a point;
the two classes are offset horizontally so neither hides the other. *Source:
`results/phase15/multiturn_{r1,r2}.json`.*

The drift score is `0.5 × (max(−Δ ACE, 0) + max(Δ IE, 0))`. **With both
quantities zero almost everywhere, the score is zero for any threshold, on any
content, however the conversation escalates.** The masked and unmasked probes
*agree with each other* on realistic content, so the causal contrast that gives
the architecture its name produces no signal to accumulate.

Only 6 of 30 turns produced a non-zero contrast, and **four of those are an
address being lifted from the content in one regime and not the other**. This is
the same fact §5 measured from the detection side — 93.3% detection where the
target-match path fires against 10.0% where it cannot — now shown to govern the
temporal rule as well.

## What we therefore claim

**The causal contrast carries discriminative signal when the injected content
contains a liftable target, and close to none otherwise.** Every consequence in
this paper follows from that one property: detection collapsing on
externally-authored attacks (§5), a harm taxonomy generalizing about half (§6),
and an adaptive layer whose knobs act on a quantity that is zero 80–97% of the
time.

Two of its five dimensions are not merely unidentifiable on our corpus —
**there is close to nothing there to identify.** We report this as the phase's
result and stopped after two attempts, as pre-registered, because a third would
have been indistinguishable from tuning a corpus until it fired.

## Threats to validity, stated plainly

- **n = 3 malicious sessions per run.** This is an existence question — *can the
  mechanism fire on a realistic conversation* — and not a rate. It is not quoted
  as one.
- **The second cohort was written after seeing the first run's trajectories.** A
  reader cannot verify from outside that the edits followed the pre-declared
  targets rather than the direction of the miss. The mitigations are that no
  target changed, the criteria were identical, and both runs are reported. That
  is weaker than the first run's guarantee and we do not claim otherwise.
- **One model, one scorer.** The zero-contrast result is a property of this
  probe-and-scorer combination. A scorer producing graded severities on
  address-free content might restore the signal; we have not built one, and §6
  is evidence that doing so is harder than it looks.
