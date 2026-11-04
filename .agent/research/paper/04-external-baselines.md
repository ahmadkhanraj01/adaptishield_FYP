# §4 — External baselines: the published defense has no measurable effect

*Source: `results/phase10/benchmark.json`. Implementation: `baselines/spotlighting.py`.
86 cases per arm; 66 malicious pairs on the primary outcome.*

## Why an ablation is not a baseline

Our `static_only` arm — screener, policy engine and Layer 4 with the causal
sub-layer removed — is an **ablation of our own system**, and a reviewer is
entitled to reject it as the comparison. A defense must be measured against
something someone else published. Two baselines, both on the same model tags and
the same corpus:

**The undefended floor.** ASR **100%** [84.5%, 100%] over 21 malicious cases
(§3's corpus). Necessary and rarely reported: if the attacks do not succeed
against an undefended agent, no downstream difference means anything. Phase 7's
first result had to be withdrawn for exactly this reason in the opposite
direction.

**A published prompt-level defense.** Spotlighting (datamarking) after Hines et
al., implemented as a `PipelineConfig` arm so it shares one code path with every
other arm, and deliberately kept outside the layer tree with a test that fails if
any layer imports it.

## Result: a null

| Arm | steered | rate | 95% Wilson |
| :--- | ---: | ---: | :--- |
| `derived_control` | 23/66 | 34.8% | [24.5%, 46.9%] |
| `spotlighting` | 22/66 | 33.3% | [23.2%, 45.3%] |

Paired McNemar **p = 1.00**, 8 helped / 7 hurt.

**The null is not indifference.** It decomposes into two per-family effects of
opposite sign: `important_instructions` improves 8 → 5 while `blunt_override`
degrades 0 → 3. A transform that makes a thin payload more *legible* can increase
compliance with it. We report the decomposition rather than the pooled null,
because the pooled number invites the wrong conclusion.

## Three qualifiers that must travel with this number

1. **`steer_rate` is the outcome, not ASR.** ASR is 0/66 in *both* arms because
   the egress allowlist absorbs every address-carrying attack. Steering is judged
   before any gate, so no backstop can absorb it. Reporting ASR here would report
   the allowlist, not the baseline.
2. **These arms derive their own action.** Spotlighting defends action
   *selection*; our pipeline is normally handed a proposed action, leaving
   nothing to defend. These arms therefore are **not comparable** with §3's, and
   the two never appear in one table.
3. **Both arms run the agent at temperature 0.** The planner had inherited the
   inference server's default of 0.8 while the analyzer ran at 0, so a
   deliberately byte-identical prompt was not the same agent. Fixing it moved the
   undefended floor on its own.

## The defect that had reversed the sign

The first run reported spotlighting as **17 points worse** (39.4% → 56.1%). It
was not. Sixteen of 37 apparently-steered cases were *refusals* that named the
attacker's address while declining to act, and the keyword scorer had no negation
handling. Spotlighting's own instruction inflated the metric judging it, **in
proportion to how clearly it worked**.

The fix is clause-scoped negation detection in the action scorer. We report the
withdrawn figure because the failure is general: a defense that changes the
*shape* of model output can corrupt any keyword-based metric measuring it, and
the corruption is sign-preserving with the defense's effectiveness. Any evaluation
of a prompt-level defense using lexical scoring is exposed to it.

## A hypothesis withdrawn

Seeing `blunt_override` at 0/11 steered, we proposed that the model was tuned to
resist obvious overrides. Inspecting the derived actions showed **no refusal
language at all**: four asked for the email's contents and the rest replied to
the greeting. The family is both blunt *and* thin, so those 11 cases cannot
separate the two explanations. Recorded because the appealing interpretation was
available and wrong.
