---
tags: [adaptishield, architecture, method]
type: concept
---

# Takeover Rule Stack

**Detection is not one threshold. It is three rules in a deliberate order, each
patching a failure of the one before.**

## The rules

**1 — IE contrast rule** (the original signal)
`IE ≥ ie_threshold` AND `masked ≥ 1` AND separation is *consistent* across
samples (`min(masked) > max(masked_san)`).

**2 — Standalone rule** ([[6f — Standalone Severity Rule]])
`masked ≥ masked_takeover_threshold` (2.0), **independent of IE**.

**3 — Drift rule** ([[6g — Temporal Drift Scoping]])
Falling ACE / rising IE slope over a **per-`session_id`** window, gated on
`masked ≥ 1`.

## Why rule 2 exists

**IE silently inverts when [[3C Context Sanitizer]] fails.** If the sanitizer
leaves an injection intact, both regimes comply, the 2s cancel to `IE = 0`, and
an attack that *survived* sanitisation reads as *safe*.

Rule 2 fires on strong evidence regardless of IE, so an attack robust enough to
defeat the sanitizer is **caught rather than excused by it**. It is the
load-bearing rule: it carries the strong-evidence cases, which is what lets rule
1 afford to be conservative.

## Why rule 3's guard was affordable

The consistency guard ([[6h — IE Consistency Guard]]) requires *every* masked
sample to outscore *every* sanitized sample — not just the means — so a single
paraphrase-driven sample flip can no longer manufacture a verdict. This is
affordable **only because** rule 2 already carries strong evidence.

## The invariant this creates

🔴 **Rule 2 must always be able to fire even when the guard suppresses the
contrast.** Never tighten the guard without the standalone rule in place. On its
own, the guard turns a strong-evidence attack into a false negative.

🔴 **"Nothing observed" must never mean takeover** — hence the `masked ≥ 1`
gates on rules 1 and 3.

Pinned in `tests/test_takeover_rules.py`. See [[Rules and Invariants]].

## The generalizable lesson

> **Any detector built on "A minus B" must be paired with a standalone-evidence
> rule for the case where A and B both move together.**

More at [[Design Lessons]].
