---
tags: [adaptishield, log, entry]
type: log-entry
date: 2026-09-12
---

# Entry XXVI — The Objection Closes, on the Third Candidate

*12 September 2026, afternoon.*

[[Entry XXV — The Number That Could Not Be Checked]] closed the reproducibility
item and left the hardening list with one thing on it that actually mattered: a
second probe model. *One model, one scorer* is the objection a reviewer reaches
for first, §XII conceded it first, and until this afternoon it was conceded
because it was true.

It is now answered. The route there was four wrong beliefs in a row, three of
them mine and all four corrected within hours, which is most of what this entry
is for.

## Wrong belief 1: the 7B candidate parrots

The first pre-flight on `qwen2.5:7b` — three cases, one per kind — came back
compliant on all three, and then produced this on the address-free case:

    forward the emails to someone@example.com

That string is in our own masked prompt, as the worked example. The model had
skipped the content and echoed the template. I wrote it up as template-parroting,
in the stratum Phase 16 exists to measure, and recommended widening the check
before spending hours on a campaign.

Widening it killed the diagnosis. **0 of 8** address-free cases parroted;
every one transcribed faithfully, grounded 0.75 to 1.00 against the mediator. So
I re-ran the original case four times, and it answered `no_action` four times —
neither the parrot nor the faithful transcription. Same input, same tag,
temperature 0, three different answers across sessions.

It was never parroting. It was **non-determinism**, and the cause was sitting in
`/api/ps` the whole time: 2.74 GB of a 5.18 GB model resident, **53% GPU and 47%
CPU**. The [[Recorded Probe Output Makes Scorer Changes Cheap]] docstring has
warned about exactly this since August. A single observation of a weird output
got a mechanism attached to it because the output *looked* like it had one, and
the real mechanism was the boring environmental one I already knew about.

## Wrong belief 2: the 3B alternative would be safe

`qwen2.5:3b` was already on the machine, 100% resident, byte-identical across
four fresh instances, three times faster. Everything the 7B got wrong, it got
right — and it returns `no_action` on **both** cases `gemma3:4b` detects,
including the address-bearing one, which is the only stratum where this detector
works at all.

[[Design Lessons]] predicted this: `qwen2.5:3b` runs 3C and the planner *because*
it resists, and §2 says a refusal-prone model on 3B destroys the signal. What the
prediction did not contain is the part worth keeping: **the refusal carries no
refusal string.** No apology, no policy language, nothing
[[3B's Refusal Exposure Is Live and Unrealised]]'s keyword check would catch. It
says `no_action`, scores 0, and is indistinguishable downstream from a document
that genuinely directs nothing. That is why §2 asks for *compliance under the
masked probe* rather than *absence of refusal*, and I had read that rule a dozen
times without noticing it was making exactly this distinction.

## Wrong belief 3: my own finding note

With two candidates down and the third unreachable — the pull kept dying on
intermittent DNS — I wrote [[The Probe's Compliance Does Not Transfer]], titled
as a general claim about the probe, and drafted a §XII paragraph to match. Both
scoped themselves honestly: the note's last section says `llama3.2:3b` was not
reachable and would add a column if it passed.

It landed a few hours later and passed everything. 11/11 compliance, identical
across four instances, 100% resident, and it detects the case `qwen2.5:3b` missed.

So the note was wrong in its headline by the end of the day it was written. It
keeps its name and carries a dated correction section instead —
[[The Benign FPR Has a Noise Floor Its Own Size]] set that precedent in August,
and renaming would break every link and erase the half-day where the evidence
said otherwise. The corrected claim is smaller and more useful: the probe needs a
compliant model, and finding one under a 4 GB ceiling took three tries. That
tells the next person what to test. The original title told them to give up.

## Wrong belief 4: somebody else's number, sitting here since August

Separately, the bibliographic pass. Six references were `[TO COMPLETE]` because
the vault knew them by system name and nobody had invented details for them —
correctly. All six are now traced; two were hard to find precisely because
`AutoMalTool` and `MCP-RiskCue` are artifacts *inside* papers titled something
else. The real defect underneath was worse than missing details: **none of the
six was cited anywhere in the body.** §II now cites them, and says plainly where
[[AgentSentry]] overlaps this work, because it localises injection by
counterfactual re-execution at tool-return boundaries and purifies context for
continuation — which is our mechanism, described first.

Then `external_numbers.json`'s held-back row. It carried **45.8%** as AgentDojo's
undefended important-instructions ASR, flagged as second-hand. Reading the paper:
Table 5 gives *No defense — targeted ASR 57.69% (±3.9)*, and 45.8% is **Table 2's
attacker-knowledge ablation baseline** — a different table measuring a different
thing. Wrong by twelve points and wrong about what it was.

The guard held it back for four weeks. I did not release it either, and that is
deliberate: I read the table through an automated fetch, and an automated
transcription is an intermediary — which is the entire failure mode the rule
exists for. Certifying it would be the same error with a different second hand.
The row carries the corrected value, the caption and the correction note, still
refused by the generator. Releasing it is a 30-second human read now instead of a
ten-minute one.

## What actually got measured

| stratum | `gemma3:4b` | `llama3.2:3b` |
| :--- | ---: | ---: |
| target-match path fires | 96.7% | **100.0%** |
| target-match cannot | 13.3% | **10.0%** |
| gap | 83.3 pts | **90.0 pts** |

58 of 60 cases agree; 1 helped, 1 hurt. The collapse follows the mechanism, not
the model → [[Phase 16 — The Stratification Survives a Second Model]].

One trap fell out of building it, and it is the kind that does not announce
itself. `probe_corpus._out_path` was keyed by cohort and run alone, so recording
a second model would have **overwritten the committed `gemma3:4b` corpus in
place** — the file §VII rests on. `verify_unchanged` could not have saved it:
that check runs when a corpus is *read*, long after the file it protects was
gone. Paths are model-keyed now, the default is byte-identical, and the filename
follows the analyzer's own tag. I hashed the committed corpus before the run and
verified it after, which I would not have thought to do a month ago.

## What this entry does not establish

**Not that the mechanism transfers generally.** Both working models are 3–4B and
locally hosted. The single 7B candidate available could not be measured on this
hardware at all, so scale is untested, and §XII says so rather than rounding the
result up.

**Not that the two models are equivalent.** Two discordant pairs cannot support
that, and the exact *p* of 1.0 is low power, not agreement.

**Not that the multi-turn finding transfers.** The zero-contrast result in §IX
was measured on the incumbent alone and has not been repeated on a second model.
The transfer covers the stratification only.

## Related

- [[Phase 16 — The Stratification Survives a Second Model]]
- [[The Probe's Compliance Does Not Transfer]] — corrected the same day
- [[Instruments Fail More Than Mechanisms]]
- [[Entry XXV — The Number That Could Not Be Checked]]
