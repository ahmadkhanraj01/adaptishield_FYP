# §8 — Negative results, and the case for a human gate

*Sources: `evaluation/kaggle/`, `logs/adaptive_loop/`, `results/phase11/`,
`results/severity/`.*

This section is not an appendix of things that failed. Three of these results are
the paper's argument for its own architecture, and each is visible only because
the instrumentation was built to see it.

## 1 — A reinforcement-learning policy proposed a security change its own reward scored lower

The adaptive component learns over a joint action space and emits a proposed
configuration change for human approval. On live data it proposed a change
scoring **+0.8683** against the incumbent's **+0.8688**, and the apply path would
have accepted it silently: the policy's argmax was trusted as the policy's
recommendation.

The repair is propose-and-verify — the proposal is re-scored against the
incumbent under the same reward before it is emitted, plus a minimality pass —
and an exact reward table in the one-dimensional case. **The guard has fired
three more times since**, most recently on different hardware with a different
random seed.

The general point is not that a bug existed. It is that **a learned policy's
argmax is not a guarantee about the objective**, and any system that applies a
learned security configuration without re-verifying it against its own reward can
degrade itself while every component behaves as designed.

## 2 — The only gain the trainer ever found was an artifact of our own benign corpus

The joint action space discovered a configuration improving reward from **+0.8688
to +0.9046**, verified and minimised over 128 episodes. Evaluated against
externally-authored benign documents, the same action produces **36 false
positives out of 68**.

The mechanism is mundane and that is the point: the learned marker fires on 30 of
60 external benign documents and 0 of 8 of ours. Our benign corpus was small,
hand-written, and — invisibly — unrepresentative in exactly the dimension being
optimised.

**Every trainer safeguard worked correctly. None could see outside the corpus.**
Propose-and-verify, the minimality pass and the reward table all functioned as
designed and all endorsed a change that would have made the system substantially
worse in deployment. Safeguards internal to an optimizer cannot detect that the
objective is measured on the wrong distribution.

## 3 — The adaptive layer's honest output is a no-op, and the reason is quantified

On every corpus measured, the adaptive component proposes no change. This is
correct behaviour, and the reason is specific rather than a shrug: the detector's
residual misses all score **0** on the masked probe, which is below both
detection rules simultaneously, and therefore **unreachable by the threshold the
adaptive layer controls**. A separate benchmark confirms it independently — all
of its residual attack successes are the address-free vector, none a threshold
failure.

We report the no-op as the result. The mechanism itself is not unproven: given a
gap its knob *can* close, the loop closes it and the fix generalizes to a
held-out attacker address it never saw — the exact pair an earlier version of
this system failed, where an apparent gain turned out to be memorization of a
training literal. What is unproven is that such a gap arises naturally, and §7
reports the first corpus built to ask.

*(§7 pending — Phase 15.)*

## What these three imply together

Each failure is invisible from inside the component that produced it. The policy
could not see that its argmax lowered its reward; the trainer could not see that
its corpus was unrepresentative; the adaptive layer cannot see that its knob does
not reach the failures it observes. In all three cases every internal check
passed.

That is the empirical argument for **a human gate that recomputes evidence rather
than trusting a proposal**. Our Layer 5 review console does exactly that, and it
found a live defect on its first run: every proposal's blocked-pattern field was
**inert**, because the policy engine matched those patterns against a different
string than the one the trainer harvested them from. A reviewer reading the
proposal would have seen a plausible security change. Recomputing the evidence
showed it could not fire.

## A note on how these were found

Three of the four results above surfaced from **instrumentation added to answer a
different question**: per-layer attribution (added to make an ablation
interpretable) exposed two benchmark defects on its first use; the recorded probe
corpus (added to make evaluation cheap) is what showed the scorer, not the probe,
was failing; the review console (added as a usability feature) found the inert
patterns.

We suggest this is not luck. Systems of this kind fail more often in their
*instruments* than in their mechanisms, and instruments are the part least likely
to be tested — because a broken instrument returns a plausible number rather than
an error.
