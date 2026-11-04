---
tags: [adaptishield, finding, external-validity, models, phase16]
type: finding
status: measured
date: 2026-09-12
---

# Phase 16 — The Stratification Survives a Second Model

**The collapse is a property of the mechanism, not of `gemma3:4b`.** On a second
probe model the gap is 90.0 points against the incumbent's 83.3, over the same
[[InjecAgent]] draw, the same prompts and the same shipped rules.

## The result

| stratum | `gemma3:4b` | `llama3.2:3b` |
| :--- | :--- | :--- |
| target-match path **can** fire | 29/30 = **96.7%** [83.3%, 99.4%] | 30/30 = **100.0%** [88.6%, 100.0%] |
| target-match path **cannot** | 4/30 = **13.3%** [5.3%, 29.7%] | 3/30 = **10.0%** [3.5%, 25.6%] |
| gap | **83.3 points** | **90.0 points** |

Paired over all 60 shared cases: **1 helped, 1 hurt, 2 discordant** — `IA105` the
incumbent catches and the candidate misses, `IA258` the reverse. They agree on 58
of 60.

⚠️ The exact *p* is 1.0 on two discordant pairs. **That is near-zero power, not
equivalence** — the report prints the warning itself. The stratum gap is the
result; the paired test is not evidence of anything here.

## Why this is the objection that mattered

[[Rules and Invariants]] §7 requires a named external baseline, and the paper has
two. It could not answer a different question: every number rested on **one**
model behind the probe, so the central claim — that the causal contrast carries
signal only when the injected span names a liftable target — might have been a
fact about `gemma3:4b`. §XII conceded exactly that, first in its list.

It now has a repeat behind it. A different lineage, a smaller parameter count and
a different instruct-tuning recipe reproduce the shape, and reproduce it slightly
more sharply.

## What made it hard, and what that is worth separately

Three candidates were needed, and the two failures are their own finding →
[[The Probe's Compliance Does Not Transfer]]. `qwen2.5:7b` complies faithfully
but at 53% CPU offload does not return the same answer twice at temperature 0.
`qwen2.5:3b` is byte-identical across repeats and answers `no_action` on both
cases the incumbent detects. Under a 4 GB ceiling the two failure modes bracket
the usable range from either side, and only the third candidate sat between them.

Every candidate was pre-flighted for masked-probe compliance on 11 cases before
any cohort recording, per §2 — a transfer run on a reticent model measures the
model's reticence, not the mechanism.

## The trap this uncovered in the recorder

`probe_corpus._out_path` was keyed by cohort and run alone. Recording a second
model would have **overwritten the committed `gemma3:4b` corpus in place**, and
`verify_unchanged` could not have caught it: that check runs when a corpus is
*read*, long after the file it protects was replaced. A transfer is not a repeat.
Paths are model-keyed now, the default is byte-identical to before, and the
filename follows the analyzer's own tag so a recording cannot be filed under a
model it was not made with. → [[Traps]]

## Related

- [[Phase 12 — Detection Is 18% on Someone Else's Attacks]] — the result this repeats
- [[The Probe's Compliance Does Not Transfer]] — the two candidates that failed
- [[Address-Free Attacks]], [[Models in Use]], [[InjecAgent]]

## What this does not establish

**Not a rate on a second model.** One recording per model, so there is no
run-to-run spread here and none should be quoted. The incumbent's own spread is
measured over three recordings; the candidate has one.

**Not equivalence of the two models.** Two discordant pairs cannot support that,
and the high *p* is low power rather than agreement. The claim is about the
**shape** of the stratification, not that the models score alike.

**Not transfer beyond ~3–4B on one machine.** Both models that work here are
small and locally hosted. Nothing was measured about a frontier model, and the
one 7B candidate available could not be measured at all on this hardware — so
whether the mechanism holds at scale is still open.

**Not a claim about the incumbent's committed figure.** This compares run 0 to
run 0. The paper quotes the *median of three* recordings for `gemma3:4b`, which
is 10.0% on the no-target stratum where run 0 alone reads 13.3%.
