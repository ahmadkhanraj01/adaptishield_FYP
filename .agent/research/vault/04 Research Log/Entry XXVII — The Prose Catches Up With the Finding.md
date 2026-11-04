---
tags: [adaptishield, log, entry, manuscript, site, environment, external-baseline]
type: log-entry
date: 2026-09-13
---

# Entry XXVII — The Prose Catches Up With the Finding

*13 September 2026.*

The session began as housekeeping and did not stay that way. It opened with two
items that were the last unlanded consequences of work already done — the
published site stopped contradicting the manuscript's structure, and §XII stopped
contradicting [[AgentDojo's Benign Pool Is Exhausted at 60]]. It then closed two
of the three things blocking the paper: **the runtime split**, and **AgentDojo's
Table 5**, which had been waiting four weeks on thirty seconds of a human.

*The title was written when this was a prose-only session. It is kept — the
entry is linked from three places and renaming would break them — and the
sections below are where it stopped being true.*

## The gap this entry also closes

The [[Entry XXVI — The Objection Closes, on the Third Candidate]] session ended in
the afternoon of 12 September. Six commits landed that evening — a MkDocs site,
a Pages Actions deploy path, a phase board parsed from `Phase.md`, and the
manuscript collapsed from seventeen paginated pages to one that scrolls — and
**none of them reached the vault**, which §8 requires. They are recorded here as
context, reconstructed from `git log` rather than lived, and this entry does not
attempt to narrate decisions it did not witness:

    9525ad0  site that cannot drift, and the session handover
    0cc5026  Actions workflow for static content
    2afb940  deploy through the Pages Actions path
    637003d  progress page gets a phase board
    90ab947  manuscript is one page that scrolls

The handover written at the end of that session states HEAD is `02f4356` with
nothing local. It was six commits behind its own repo before it was read. A
handover that reports a SHA is making a checkable claim, and this one failed the
check — worth knowing before trusting the next one's "nothing local".

## The nav outlived the page it described

`90ab947` merged the manuscript into a single scrolling page but left
`mkdocs.yml` listing seventeen per-section entries, sitting uncommitted in the
working tree along with a `pymdownx.emoji` extension. So the published nav
offered a table of contents to files the build no longer produced, and the
🔴 / 🟡 status markers this vault uses everywhere rendered as literal text.

Committed as `e4a7132`, verified with `mkdocs build --strict` before pushing,
deployed clean in 46 s. Nothing here is a finding; it is recorded because the
site is now the artifact a supervisor or reviewer is most likely to open first,
and *the site cannot drift* is a claim the repo makes about itself.

## §XII said "adequate", the evidence said "exhausted"

The real item. The limitations bullet read:

> **The benign corpus is 60 external documents,** adequate for the reported
> [0.9%, 11.4%] interval but wide enough that a two-point FPR difference is
> unresolvable.

Every word of that is true and the framing is wrong. "Adequate but wide" describes
a **sample** — and a sample invites the obvious remedy, which is to draw more.
[[AgentDojo's Benign Pool Is Exhausted at 60]] established the day before that
there is nothing to draw: the 60 are the complete benign content of the
`workspace` and `slack` suites under our own filter, re-harvested item-for-item
from a fresh wheel, zero disjoint episodes left. A reader who accepted the old
bullet would reach for a remedy that does not exist.

The rewritten bullet says census rather than sample, and carries the two
consequences that actually bind:

- the only routes reaching *n*=110 admit off-domain `travel` prose, which carries
  **no liftable target** — so it would *lower* the measured [[FPR]] for a reason
  belonging to the denominator, not the defense;
- the width comes from a rate near zero, not from *n*. Tripling the corpus buys
  about 3.3 points of interval, marked in the prose as a projection at an assumed
  rate because that is what it is — nothing was recorded.

The old bullet's concession survives verbatim in the final sentence. The finding
is explicit that it does **not** establish 60 is enough, and an edit that quietly
upgraded a limitation into a defence of the corpus would be the failure mode
[[6n — A Corpus That Can Fail]] warns about, pointed inward.

The limitation relocates rather than disappears: **a second external benign
corpus is needed, not more of this one.** There is no third corpus waiting.

## The venv could not build the paper it is told to build

`README` says activate `./venv`. `Rules.md` §1 says `numpy==1.26.4` is pinned and
names `requirements.txt` as the source of truth. Both were true statements about
an environment nobody had checked:

| | `./venv` | system `python3` |
| :--- | :--- | :--- |
| numpy / pandas / matplotlib | ✗ | ✓ (**2.2.6** — the version §1 forbids) |
| langchain / chromadb | ✗ | ✓ |
| mkdocs | ✓ | ✗ |

So the venv could run the 502 tests and build the site, and **could not
regenerate a single figure or run the pipeline**; the system interpreter could do
those, at the forbidden numpy, and could not build the site. The paper's
artifacts were being produced by two interpreters and nothing failed loudly about
it. `requirements.txt` said `numpy`, unpinned — **the pin existed only in prose**,
which is why nothing caught this.

Pinned it where §1 already says it lives, installed the file into the venv: 89
packages, `pip check` clean, 502 tests still passing.

Then the check that mattered. **All four figures regenerate byte-identical** under
1.26.4 — same PNG md5s — so the numpy major version never silently moved a
figure, and the committed figures' system-interpreter provenance is harmless.
This was the live worry behind the item and it comes back clean. The PDFs differ
by exactly 8 bytes, all inside `/CreationDate`; reverted rather than committed, so
the diff does not imply a figure changed.

`installed.txt` is deliberately untouched. It is the evidence of the drift, not a
lockfile, and `pip freeze` over it would erase the only record of how the two
interpreters diverged → [[Traps]].

## Table 5, and the rule that made it wait

[[Entry XXVI — The Objection Closes, on the Third Candidate]] left AgentDojo's
undefended ASR located but held back, because it had been read through an
automated fetch and an automated transcription is the intermediary the guard
exists to refuse. Asked to do the read myself today, the answer was the same as
yesterday's and for the same reason: **certifying my own fetch would make the
`verified` field mean nothing**, on the one row that has already been wrong by
twelve points.

What could be done without certifying was done — Table 5's delimiting row staged
on the same held-back footing, so that *two* rows waited on *one* read of *one*
table. A human then read it, and both flipped to `verbatim`.

The 45.8% correction is kept on the row as `correction_note` rather than deleted
now that it is resolved: a withdrawn number is marked, never removed.

### What it bought §VI

Our spotlighting result is a null, and a bare null invites the reading that the
whole family is inert — a reading the evidence does not support and we are not
entitled to. Delimiting is the closest published analogue: a prompt-level
transform, a tool-calling agent, and **an undefended row measured in the same
table**, which makes it a *difference* rather than a level.

57.69% → 41.65%, non-overlapping intervals, no benign-utility cost. And 41.65%
of targeted attacks still succeed, which §VI-D says plainly — the family reduces
the exposure, it does not remove it. Both halves belong to the claim, exactly as
[[Phase 10 — Spotlighting Has No Measurable Effect]]'s four qualifiers do.

`test_the_agentdojo_baseline_is_currently_held_back` is deleted, as its own
docstring instructed. It was a to-do wearing a test's clothing, and it did its
job: four weeks of refusing to render a number that turned out to be wrong.

## The post-install check, and what it found instead

`langchain-core` moved 1.4.9 → 1.6.3 in the venv install, and the 501 tests
import no LLM and no network, so they could not have caught a break. Ran
`adaptishield_pipeline.py` — the check the handover prescribes — to close that.

**Nothing was broken.** All three cases behave as their docstrings specify:
`approved_direct` on the benign low-impact call, `safe_continuation` on the
injected one (ACE=−1, IE=2, mediator purified, permission out-of-scope, egress
blocked on `attacker-c2.evil.com`), `approved_causal` on the benign high-impact
call. Layers 0–4 all fire; the LLM screener returns a real judgement.

Two things came out of running it that were not what it was run for.

**The demo was hiding its most important verdict.** Test 2 — the attack case —
had no `>>> Result` line at all, and Test 3's was pasted twice. A reader running
the documented health check saw the benign case appear to run twice and got no
verdict for the attack. Behaviour was never wrong; only the reporting. Fixed.

**And [[The Model of Record Is 40% Resident]].** `/api/ps` says `gemma3:4b` holds
1.71 GB of a 4.30 GB footprint in VRAM — **60% on CPU**, on a card with nothing
else on it. That is worse offload than the `qwen2.5:7b`
[[The Probe's Compliance Does Not Transfer]] disqualified for offloading, and the
handover's model table had been calling the incumbent GPU-resident.

The temptation was to write that up as *the incumbent is non-deterministic too*.
Checking first killed that: four runs, and the **three warm ones are identical on
every field**. Only the cold run — the first call after load — differs, and it
differs in `orig_sanitized`'s severity, moving DE by a point. Verdicts identical
in all four. So the honest claim is much narrower than the one the observation
first suggested, and it is a new one: every previous non-determinism result here
compared warm repeats, and a corpus whose first case runs cold has that case
drawn from somewhere the contract cannot see. The contract pins prompt,
sanitiser, model tag and temperature — never residency.

## The site audit, and the defect a generator cannot prevent

The site's docstring makes a strong claim — *nothing here is a second copy of
anything* — written against the review deck, which was hand-coded and drifted
into contradicting the repo in five places while rendering perfectly. Nobody had
ever tested the claim. Four pages fetched live and checked against their sources,
mechanically rather than by eye:

| Checked | Result |
| :--- | :--- |
| 10 home-page tile values against `results/*.json` | ✅ rates, Wilson bounds, gaps, miss IDs all exact |
| 8 external rows against `external_numbers.json` | ✅ present; the 9 detector FPR rows correctly excluded |
| 80 distinct percentages in `manuscript.md` | ✅ all 80 on the page |
| 16 headings, 13 table captions | ✅ present, numbering intact |
| `Phase.md` → progress; `Architecture.md` → architecture | ✅ complete |
| 6 figure assets, 6 repo links | ✅ all resolve |

**The rule held.** Everything a program typed traced back correctly. The one
defect was in the half a human wrote.

The two InjecAgent tiles read *96.7% vs 13.3%* and *100.0% vs 10.0%* with nothing
saying they were **run 0**. They come from `phase16_model_transfer`, whose own
manifest says in as many words that it is one recording per model and that no
run-to-run spread may be quoted from it. But the manuscript's headline for the
incumbent's no-target stratum is **10.0%** — the *median of three* recordings from
`results/noise_floor/`, a different artifact. Both numbers are right. A reader
holding the site beside the paper saw 13.3% against 10.0% for what looked like one
quantity, and nothing on the page said otherwise.

That is the form worth carrying. Generating a number from a tracked artifact
guarantees it is *correct*; it does nothing to guarantee it is *scoped*, and the
scope lives in a label some human wrote once. [[Traps]] has it now. The tiles
carry `run 0`, with an admonition saying why and noting that the two-model
comparison is only valid run-0-against-run-0.

## The runtime of record, declared

The item the 12 September handover raised as *which interpreter is the runtime of
record?* is closed, and closed in the direction the evidence pointed: `./venv`,
now that it satisfies `requirements.txt` in full and the figures are proven
byte-identical under the pin.

Declared in all three places it has to be — `Rules.md` §1, its twin
`07 Practice/Rules and Invariants.md`, and `README.md` §8 — with system `python3`
named as **not** the runtime, since it carries the numpy §1 forbids. The phrasing
that matters is the last clause: *if something only works outside the venv, that
is a bug in the venv, not a licence to switch interpreter.* Reaching for whichever
interpreter had the package is how the split happened in the first place.

Both rule documents now also carry the lesson rather than only the rule: the
version must be **written in** `requirements.txt`, not merely asserted in prose,
and `installed.txt` is evidence of drift, never a lockfile.

**Flagged, not fixed:** `README.md` §8's package list is stale — it reads
`langchain==0.3.7` where the venv has 1.4.0. Rewriting it would be inventing a
lockfile nobody verified, on the day this project learned what an unverified
version claim costs. It is labelled a historical snapshot instead, with
`requirements.txt` named authoritative.

### A handover cannot name its own SHA

Small, and worth recording because it wasted two amends. The handover's header
quotes the last commit; writing the handover *is* a commit, so any SHA put there
is a prediction, and amending to correct it changes the SHA again. It now names
the commit it sits **on top of** (`e099104`) and points the reader at
`git log --oneline -1` for the tip — which also fits the warning already at the
top of that file about its own claims being checkable.

## The documentation pass, and a figure that described work that did not exist

The last stretch was bookkeeping the repo could not defend. Four documents were
describing a different project than the one in `results/`.

**`Phase.md`** still marked **14a** and **15** as not started. Both have committed
artifacts: the repeat measurements are 2/60 in all three recordings with range 0,
and Phase 15 ran *twice* — PRIMARY not met both times, closing structurally
because `orig == masked` on 24/30 turns and IE = 0 on 29/30, so the drift rule's
input is zero and no cohort reaches it at any threshold. **Phase 16 was not on the
board at all.** Test counts corrected to 501 in six places across three files.

**`Architecture.md`** described the future rather than the result: GRPO was
"pending", and Kaggle "will replace `propose_update()` internals". Both already
happened. The tense was the defect, not the content → see below.

**Two claims removed because they were never true.** `gemma2:9b` was listed in the
architecture *and* the README as 3B's fallback and has never been installed or
measured. And the README called `llama3.2:3b` **rejected for poor security
reasoning** — it is the paper's second probe model in §VII-E, where it passed the
compliance pre-flight 11/11 and detects a case `qwen2.5:3b` misses. A README
contradicting the manuscript about a published result is the worst of the three,
and it is what a supervisor opening the repo would have hit first.

### The five boxes

The implementation diagram carried five components with dashed borders meaning
*specified, not yet implemented*: Transport Integrity Verifier, Schema Validator,
Name Squatting Guard, Supply Chain Scanner, Provenance Memory Store. The legend
disclosed it and Appendix A's caption explained the convention, so this was
**honest rather than wrong** — and it was still removed, at the user's direction,
on the reasoning that an *implementation* diagram should show the implementation.

The knock-on edits are the point. Appendix A's caption described the dashed
convention, so it had to be rewritten or it would contradict its own figure;
README's ASCII stack listed `Provenance Memory Store` under a `[built]` header.
A box in a diagram is never only in the diagram.

⚠️ **And for one commit the repo was knowingly inconsistent.** There is no drawio
CLI on this machine, so the XML lost the boxes while the two committed PNG
exports — which are what the `.docx` and the site actually render — still had
them. That was recorded in the commit message rather than left to be discovered.
The user re-exported by hand; the new image was verified **by reading it**, not by
trusting its filename, and the published PNG's md5 now matches the local file
byte-for-byte.

### Why Kaggle stays

Worth writing down, because it was asked and the answer is not obvious from the
repo. Kaggle is **not** in the same category as the five boxes. The five were
specified and never built. Kaggle was used: Phase 6's GRPO training executed
there, the torch backend agreed with the pure-Python implementation to **exactly
zero**, and `evaluation/kaggle/` is committed code with a dataset and a
`proposed_update.json` to show for it. What was retired is the *GPU premise* — the
P100 is sm_60 against a torch needing sm_70+, so the trainer fell back to CPU and
the whole workload costs 0.27 s. The panel earned its place by being executed, and
what it documents is a **negative result**, which this project reports rather than
hides → [[The Adaptive Layer Proposes a No-Op]].

## The tool filter does not reconcile, and that is the answer

The last open number. AgentDojo's body text gives its tool filter **7.5%**; its
own Table 5 gives the same defense **6.84% (±2.0)**. The obvious explanations were
checked and all fail — not a different model, not untargeted ASR, not an average.
0.66 points is not rounding.

The tempting move was to pick the table, since the other two AgentDojo rows come
from it and consistency would look tidier. That would have been a **new verbatim
claim certified off my own fetch**, on the same paper whose number was already
wrong by twelve points once. So: the row keeps 7.5%, stays `verbatim` because the
quote is real and matches it, and gains a `discrepancy_note`. The manuscript
quotes the prose figure and *names the table figure beside it* in both places it
appears. Reporting an irreducible discrepancy is a better state than a tidy
paragraph that hides one → [[Published Numbers We Position Against]].

**A guard fired correctly on the way.** The first test run came back 1 failed:
`test_positioning_table` caught `paper/10-positioning.md` going stale against
`external_numbers.json` before it was regenerated. The generated table cannot
drift from its source the way the review deck did, and this is the first time
that has been demonstrated rather than asserted.

## What moved, and what did not

| | |
| :--- | :--- |
| **Our** numbers | **none moved** — 96.7%, 3.3%, [0.9%, 11.4%], the 1/57/2 stability split all untouched |
| **Published** numbers | two released to `verbatim` — 57.69% and 41.65%, both AgentDojo Table 5 → [[Published Numbers We Position Against]] |
| Tests | **501** passed, 7.3 s — one fewer, by deletion, not by failure |
| Manuscript | §VI-D new; Tables VI–XII renumbered VII–XIII; 13 tables, ~10,301 words |
| Environment | `./venv` satisfies `requirements.txt` and is now **the declared runtime of record**; figures byte-identical under the pin; pipeline verified end-to-end under `langchain-core` 1.6.3 |
| Commits | twenty-one, `e4a7132` onward — all pushed, all deployed |

[[Current Numbers]] needs no edit to **our** figures, and saying so is the point:
nothing measured here moved. What moved is what we quote from other people, and
that lives in [[Published Numbers We Position Against]] instead.

## What this entry does not establish

**Not that the benign-corpus limitation is closed.** Only that the manuscript now
describes it correctly. The interval is still wide, a two-point difference is
still unresolvable, and the second external corpus does not exist.

**The site *is* now checked against the repo** — see the audit above, which
closes the item this section opened with when the entry was written. Scoped:
it compares published pages against `results/` and the markdown sources as they
stand **today**. It is not a standing guarantee, nothing re-runs it, and the
defect it found was in a hand-written label rather than in any generated value —
so the next one will be too.

**Nothing about the 12 September evening commits beyond what `git log` says.**
Their reasoning was not recorded at the time and is not reconstructed here.

**The pipeline now *has* run** under the repaired venv and the bumped
`langchain-core` — three cases, all verdicts correct. That closes the item this
section opened with when the entry was first written. What it does **not** cover
is the campaign or benchmark paths, which are the ones that take hours.

**`./venv` *is* now the runtime of record**, declared in all three documents —
which closes the question this section was opened to keep honest. Scoped: the
declaration says what should be used, and the venv was verified to satisfy
`requirements.txt` on 13 Sep. Nothing enforces it. No test fails if someone runs
`python3` outside the venv, and the README's package list still names versions
that are not installed.

**Not that AgentDojo's tool-filter row is settled.** It quotes the paper's prose
at 7.5% and is marked `verbatim`; Table 5's cell says 6.84% (±2.0). Left as
found — deciding which the manuscript means is a judgement, not a transcription
fix.

## Related

- [[AgentDojo's Benign Pool Is Exhausted at 60]] — the finding this landed
- [[The Benign FPR Has a Noise Floor Its Own Size]] — the other limit on the number
- [[Entry XXIV — The Corpus Was Already Complete]] — where the census was found
- [[The Model of Record Is 40% Resident]] — found by the post-install check
- [[Published Numbers We Position Against]] — where the two released rows live
- [[Phase 10 — Spotlighting Has No Measurable Effect]] — the null §VI-D calibrates
- [[Entry XXVI — The Objection Closes, on the Third Candidate]] — the session before, which held Table 5 back
