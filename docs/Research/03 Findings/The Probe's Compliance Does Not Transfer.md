---
tags: [adaptishield, finding, instrument, models, negative]
type: finding
status: measured
date: 2026-09-12
---

# The Probe's Compliance Does Not Transfer

**The masked probe's compliance is a property of `gemma3:4b`, not of the probe.**
Both alternative models available on this machine fail it — and they fail in
*opposite* ways, with the 4 GB card forcing the choice between them. §XII already
asserted this; it is now measured.

## Why it was tested

The hardening pass's highest-value item is a second model family: *one model, one
scorer* is the objection a reviewer reaches for first. Before spending hours on a
transfer campaign, Rules §2 says to check the candidate **complies** under the
masked probe, because a refusal-prone model on 3B destroys the causal signal.
Both candidates were checked against the **committed** `gemma3:4b` recordings,
case for case, on the target-bearing case, an [[AgentDojo]] benign control, and
nine address-free [[InjecAgent]] cases.

## Two candidates, two opposite failures

| | `qwen2.5:7b` | `qwen2.5:3b` |
| :--- | :--- | :--- |
| fits the 4 GB card | ✗ — 2.74 of 5.18 GB, **53% GPU / 47% CPU** | ✓ — 2.16 of 2.16 GB, **100% GPU** |
| complies under the masked probe | ✓ 8/8 faithful transcriptions | ✗ **6/11 `no_action`** |
| same answer twice at temperature 0 | ✗ **varied across runs** | ✓ identical across 4 fresh instances |
| the two cases `gemma3:4b` detects | kept 1 of 2 | **lost both** |

`qwen2.5:7b` transcribes injections faithfully and grounds 0.75–1.00 of its
reported action in the mediator. It is disqualified on **determinism**: the same
input at temperature 0 returned a different answer in a later session, which is
the split GPU/CPU load showing up as instrument noise exactly as
[[Recorded Probe Output Makes Scorer Changes Cheap]] warns. An effect of two or
three cases cannot be measured with an instrument that moves by two or three
cases.

`qwen2.5:3b` is the mirror image: fully GPU-resident, byte-identical across
repeats, three times faster — and it returns `no_action` on **IA238 and IA105,
both of the cases `gemma3:4b` scores 2**. IA238 is the address-bearing attack,
the one stratum where this detector works at all. Severity 0 there is not a lower
score; it is no signal.

## The refusal does not look like a refusal

Nothing in `qwen2.5:3b`'s output says *"I can't help with that"*. There is no
apology, no policy language, nothing a refusal-string matcher would catch. It
simply answers `no_action` and scores 0 — indistinguishable, to every downstream
rule, from a document that genuinely directs nothing.

That is why Rules §2 states the requirement as *compliance under the masked
probe* rather than as *not refusing*, and it is why
[[3B's Refusal Exposure Is Live and Unrealised]]'s keyword-based refusal check
would have reported this model as clean. A second instance of the same shape:
**the reassuring output and the broken output are the same string.**

## The card is what forces the choice

This is not a statement about Qwen. It is a statement about a 4 GB GTX 1650 Ti:

- a model big enough to comply reliably does not fit, so it runs split to CPU and
  stops being reproducible
- a model that fits is either the incumbent or tuned for the resistance that
  makes it useless here — `qwen2.5:3b` is in this project *because* of that
  resistance ([[Models in Use]]: 3C/L3/planner want it, 3B must not have it)

And there is no second environment. Kaggle cannot host Ollama at all, so the
`Phase 6` escape hatch for "anything too big for the card" does not apply to
anything requiring a live probe. → [[Compute Strategy]]

## 🔴 CORRECTED, same day — and the title of this note is wrong

`llama3.2:3b` was unreachable when the above was written (the pull kept dying on
intermittent DNS), and the note said so in its own scoping section. It landed a
few hours later, and it **passes both bars**:

| | `qwen2.5:7b` | `qwen2.5:3b` | **`llama3.2:3b`** |
| :--- | :--- | :--- | :--- |
| fits the 4 GB card | ✗ 53% GPU / 47% CPU | ✓ 100% GPU | **✓ 100% GPU (2.55 GB)** |
| complies under the masked probe | ✓ 8/8 | ✗ 6/11 `no_action` | **✓ 11/11** |
| same answer twice at temperature 0 | ✗ | ✓ | **✓ identical over 4 instances** |
| detects the address-bearing case | ✓ | ✗ | **✓** |

The cohort was then recorded under it in full, and
[[Phase 16 — The Stratification Survives a Second Model]] reports the result:
**100.0% [88.6%, 100.0%]** where the target-match path can fire against
**10.0% [3.5%, 25.6%]** where it cannot. A **90.0-point** gap, against the
incumbent's 83.3 on the same draw. The models agree on 58 of 60 cases.

**So compliance does transfer, and the claim above was drawn too wide.** What
does not transfer is *arbitrary* model choice:

- ❌ **Wrong as titled.** Compliance is not a property of `gemma3:4b`. A second
  lineage, a smaller parameter count and a different instruct-tuning recipe all
  comply, and the stratification comes out slightly *sharper* on the new model.
- ✅ **Still true, and it is the useful half.** Two of three candidates failed,
  in opposite directions, and the 4 GB card is why: a model large enough to be
  reliably compliant does not fit, and one that fits may be tuned for exactly the
  resistance that makes it useless in this role. The constraint is real. It makes
  the **search** hard, not the transfer impossible.
- ✅ **Untouched.** `qwen2.5:3b` refuses without a refusal string, which is why
  Rules §2 asks for compliance under the masked probe rather than absence of
  refusal, and why a keyword-based refusal check would have called it clean.

The corrected statement is **"the probe needs a compliant model, and finding one
under a 4 GB ceiling took three tries"** — weaker than the title, and more useful,
because it tells the next person what to test rather than what to give up on.

The note keeps its name. Renaming it would break every link and, worse, erase the
half-day where the evidence said otherwise — and the corrections are the most
transferable part of this work.

## Related

- [[Models in Use]], [[Four Probe Regimes]], [[Rules and Invariants]] §2
- [[3B's Refusal Exposure Is Live and Unrealised]] — the refusal check this evades
- [[Instruments Fail More Than Mechanisms]]
- [[Phase 12 — Detection Is 18% on Someone Else's Attacks]] — what a transfer run would have repeated
- [[Entry XXV — The Number That Could Not Be Checked]]

## What this does not establish

**Not that the finding fails to transfer.** Nothing was measured about detection
on another model, because neither candidate produced an instrument capable of
measuring it. The stratification result stands exactly where §VII leaves it: on
one model.

**Not that these two models are bad.** `qwen2.5:3b`'s resistance is a *virtue*
everywhere else in this pipeline and is why it runs 3C, L3 and the planner.
"Unusable as 3B" is a statement about the role, not the model.

**Not a measurement, at 11 cases and `k_samples=1`.** This is a pre-flight that
disqualified two candidates. It is enough to decide not to spend hours on a
campaign; it is not enough to characterise either model's behaviour, and no rate
from it should be quoted.

**Not final on the third candidate.** `llama3.2:3b` is a different lineage again
and was not reachable when this was written — the pull failed on intermittent DNS.
If it both complies and is deterministic, the transfer campaign is back on and
this note's table gains a column.
