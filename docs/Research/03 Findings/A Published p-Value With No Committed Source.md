---
tags: [adaptishield, finding, instrument, process]
type: finding
status: fixed
date: 2026-08-08
---

# A Published p-Value With No Committed Source

**Phase 10's `McNemar p = 1.00, 8 helped / 7 hurt` appeared in five documents and
no committed code computed it.** Found while building Phase 11, which needs the
same test.

The number turned out to be **right** — `evaluation/paired.py` reproduces it
exactly. That is luck, not process, and the distinction is the finding.

## What was actually missing

| | |
| :--- | :--- |
| Quoted in | root README §1.2, `Phase.md`, [[Current Numbers]], [[Phase 10 — Spotlighting Has No Measurable Effect]], Volume II entry XVII |
| Committed code that computes it | **none** — `grep -rn mcnemar --include=*.py` returned nothing |
| Recorded in `results/phase10/benchmark.json` | **no** — no discordant counts, no p-value, no per-case outcomes |
| How it was produced | an ad-hoc shell computation in the session that ran the arms |

Rules §7: *every number in the paper is regenerable by one committed command whose
artifact is committed*. This one was not regenerable at all — the paired data lived
only in a **gitignored** checkpoint.

## Why it survived review

Because the *arms* were rigorous. The corpus was chosen for power, the two arms
differ in exactly one flag, the temperature confound was found and fixed, and a
scorer defect that reversed the sign was caught and corrected. All of that
attention went to the measurement, and none to the **statistic computed on top of
it** — which felt like arithmetic rather than a result.

Same shape as [[Phase 7 Benchmark Withdrawn]] and
[[3B's Refusal Exposure Is Live and Unrealised]]: the mechanism was fine and the
instrument around it was not → [[Instruments Fail More Than Mechanisms]], now on
its fourth application.

## What was built

`evaluation/paired.py`, plus `per_case` outcomes written into the tracked artifact
so **any** paired test is recomputable from the committed file alone.

- **Exact binomial is the p-value of record.** The chi-square form of McNemar is
  asymptotic and unreliable below ~25 discordant pairs. Phase 10 has **15**. The
  chi-square figure is reported beside it only because reviewers expect it, flagged
  `asymptotic_usable: false`.
- **`helped` / `hurt`, not `b` / `c`.** Named by direction because a reversed sign
  is the error [[The Scorer Cannot See Negation|already withdrawn once]] from this
  very comparison, and a swapped table is plausible-looking and undetectable
  downstream.
- **Benign cases are excluded from pairing.** An arm that blocks a benign document
  is *worse*; folding those in at the same polarity would let over-blocking read as
  a win. [[FPR]] reports that instead.
- **`by_group` exists because the null is not indifference.** Pooled p = 1.00 hides
  `important_instructions` 3 helped / 0 hurt against `blunt_override` 0 helped /
  3 hurt. Exploratory and **unadjusted** for six comparisons.

## The regenerated result

*From the same cached per-case outcomes, now through committed code:*

| | |
| :--- | :--- |
| steer rate | 34.8% → 33.3% |
| helped / hurt | **8 / 7**, 15 discordant of 66 pairs |
| exact two-sided p | **1.000** |

Identical to the published figure.

## A second provenance defect, found while fixing the first

Re-deriving an old result with new reporting code produces a report
indistinguishable from a fresh run, stamped with the **current** commit — a
provenance lie in the artifact that Rules §7 exists to prevent. So the manifest now
carries `replay.fully_replayed`, and `results/phase10/` keeps the original run's
`manifest.json` **alongside** `manifest_analysis.json` for the replay. The commit
that computed the p-value is not the commit that produced the outcomes, and the
artifact now says so.

## The lesson

> **A statistic is a result, not arithmetic.** Anything quoted in the write-up needs
> a committed command and a committed artifact — including the parts that feel too
> small to be worth a module.

🔴 Recorded in [[Rules and Invariants]]: **no p-value, interval or rate enters a
document before the code that computes it is committed.**
