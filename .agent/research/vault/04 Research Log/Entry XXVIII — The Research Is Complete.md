---
tags: [adaptishield, log, entry, closure, writeup]
type: log-entry
date: 2026-09-15
---

# Entry XXVIII — The Research Is Complete

*15 September 2026.*

The session opened with a scan of the whole repository and a health check, and
the user then said the sentence this log has been working toward since
[[Entry I — Research Proposal]]: **the research is complete.** This entry records
what that means, what was done to mark it, and what it does not mean.

## What "complete" is measured against

The repo has its own definition of done, written in the 13 September handover:
every hardening item on `paper/handover.md` §4 closed, the manuscript current
with the artifacts, a venue chosen. The first two were already ✅. The third is
🔵 parked at the user's request and is a decision, not research. Against that
definition, and against `Phase.md`'s board where every measurement phase from 0
to 16 is ✅, the declaration is consistent with the evidence.

The health check run before the declaration, under `./venv`:

| | |
| :--- | :--- |
| `pytest tests/` | 501 passed, 7.6 s |
| `evaluation.campaign_report` | ran clean, no model calls |
| `evaluation.model_transfer` | ran clean |
| Ollama | reachable, no model loaded |
| Tree | `main` level with `origin/main`; one untracked superseded PNG |

Both analysis commands rewrote their manifests with a new timestamp and commit
stamp and nothing else; both were reverted, per [[Traps]] — regenerated artifacts
churn on timestamps, and a diff that implies a number moved when none did is
worse than no diff.

## What was done to mark it

**A `writeup/` folder at the repo root.** The user's next task is to write the
paper in their own words, and asked for a study guide: one markdown file per
section, in bullets, with the figures embedded, and the meaning of each point in
the simplest possible words. Eight files — abstract, introduction, related work,
methodology, experiments and results, discussion, conclusion, and a README —
each bullet in the form *plain statement · exact number with n, interval and
`results/` source · `[meaning …]` in plain words*. Six figures copied in from
`paper/figures/` and the root diagram (md5-identical), and six Mermaid explainer
diagrams drawn for the folder only: the threat model, the four defense families,
the request flow, the four regimes and their contrasts, the corpus-to-section
map, and the double gate on adaptive proposals. Two rules files under
`writeup/rules/`, one for a professional research paper in general and one for
what a journal adds, both written so that every rule that has already bitten this
project names the scar.

The design choice worth recording: the folder **does not replace the
manuscript**. `paper/manuscript.md` stays the version an examiner reads. The
digests are what the authors read *before* writing, so the numbers survive
paraphrase and the reasoning survives translation into their own voice. Every
number in the folder traces to a `results/` file, which is `Rules.md` §7 applied
to a document that will never be submitted.

**The docs stop describing an active project.** `Phase.md` gains a closing
notice above its two governing dates and its Phase 14 row and heading read
"drafted; research closed". `handover.md` gains a §0. `README.md` moves to v24
and §13 is rewritten from a stale next-steps list — it still carried two items
numbered 2 and a "blocked on the journal decision" the manuscript had outgrown —
into the five administrative items that remain and the list of things
deliberately not to re-open. The hub and [[Current Numbers]] correct a test
count that had sat at 452 since 9 August while the suite grew to 501.

**One manuscript fix.** The Data and Code Availability statement said *494 tests
in approximately 12 seconds*. The suite is 501 in about 8. Corrected in the
markdown; the `.docx` deliberately not rebuilt, since it is byte-unstable and
regenerates on demand, and a rebuild would stage a diff for a one-word change.
This is the same class of defect [[Entry XXVII — The Prose Catches Up With the
Finding]] fixed six times over: a count stated in prose, drifting from the thing
it counts, with nothing to catch it.

## What remains, and why none of it is research

| | Item | Needs |
| :--- | :--- | :--- |
| ✍️ | The write-up itself, from `writeup/` | the authors |
| 🔵 | Venue — parked, do not raise unprompted | user + supervisor |
| 🟡 | Author block: ORCIDs, grades, order, funding | supervisor |
| 🟡 | Two human reads: AgentDojo Table 5 (6.84% vs 7.5%); §XI as prose | a human |
| 🟡 | Residency unrecorded in manifests | only if anything is ever re-recorded |

## What this entry does not establish

**Not that the paper is finished.** A manuscript exists; the authors' own
version does not yet. The digests are scaffolding, and scaffolding is not a
building.

**Not that the numbers are final in the sense of being beyond revision.** They
are final in the sense that no further run is planned. A reviewer may ask for
one, and the residency note above is the first thing to fix if that happens.

**Not that the writeup folder is a second copy of the manuscript that can
drift.** It is, in the same way the review deck was, and [[Entry XXVII — The
Prose Catches Up With the Finding]] showed what that costs. The mitigation is
that every bullet names its `results/` file, so a drifted number is a number
whose source disagrees with it, which is checkable. Nothing re-runs that check.

**Not that "complete" was verified against anything beyond the repo's own
definition.** The supervisor has not said so; the user has. The declaration is
recorded as the user's, on 15 September 2026, and the docs say the same.

## Related

- [[Entry XXVII — The Prose Catches Up With the Finding]] — the session before,
  where the last two blockers closed
- [[Phase Roadmap]] — every phase ✅
- [[Current Numbers]] — unchanged, except the test count
- [[Traps]] — the timestamp-churn revert, applied again today
- [[Rules and Invariants]] — §7, which the writeup folder inherits
