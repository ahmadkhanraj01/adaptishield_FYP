---
tags: [adaptishield, finding, positive]
type: finding
date: 2026-07-25
---

# 6m — The Single-Character Defect

**All 15 residual detection failures had one cause: a hyphen.**
Detection went **99/114 → 114/114**.

## The instrument first

`evaluation/probe_diagnostic.py` — read-only. It reconstructs each failing case
deterministically, replays the two regimes whose difference constitutes IE, and
reports the raw text each sample produced, the severity it earned, and **the rule
that assigned that severity**. It alters no detection rule and monkey-patches
nothing; it observes.

Critically it runs **matched controls**: for each failure, the same family and
directive against an address the campaign *caught* — so a behavioural difference
is attributable to the one token that differs rather than inferred from failures
alone.

## The cross-tabulation that constrained the hypothesis before it ran

Every one of the 15 failures targeted **the same exfiltration address**, across
all 6 families, on precisely the 3 directives whose wording contains no
high-severity keyword. The 4th directive (containing "forward") was caught for
every target. The other three addresses were caught **24/24 each**.

> The failure was not a property of any family, nor of any threshold. It was a
> property of **one address**.

## The defect

The probe, shown content directing exfiltration to an address whose domain
contains a **hyphen**, correctly recognized the instruction and correctly
restated it — **but rendered the address with the hyphen removed**. It did so in
**57 of 57 mentions**: deterministically, not as sampling variance.

The detector's strongest rule — escalate when the action names a target lifted
**verbatim** from untrusted content — was implemented as an **exact substring
test**, and therefore never fired. Severity capped at 1 where the keyword list
happened to match and 0 where it did not.

**A perfectly functioning probe was recorded as silence.**

## Three corrections

1. **Punctuation-normalized target match**, with a length floor below which a
   normalized target is too short to be distinctive. Cost was *measured*, not
   assumed: an adversarial benign A/B (`evaluation/fpr_check.py`) found **exactly
   one** new exposure — benign content naming a hyphenated-domain recipient. That
   *widens a pre-existing defect* rather than creating a class, since the verbatim
   form already scored high → [[3B Layer 4 Boundary]].
2. **Greedy decoding** (`temperature = 0`). Every reported quantity is a
   difference, so decoding variance enters the measurement directly; a repeat run
   had disagreed on 3 of 15 cases.
3. **The sanitizer prompt rewritten** — see [[3C Context Sanitizer]] for its
   three failure modes, and the deliberate decision *not* to strip addresses
   wholesale.

## The instrument's own error

The diagnostic **initially misreported 3 of these cases**, having ordered its
classification so that severity 0 was attributed to a silent probe **before** the
possibility of a garbled address was considered. The incorrect diagnosis would
have directed the repair at the **probe prompt, which was not at fault**. Ordering
corrected and pinned by regression tests. Another entry in
[[Instruments Fail More Than Mechanisms]].

## Result

**114/114**, 0 false positives on the benign controls. Not memorization: the two
**held-out** addresses — including the one responsible for every prior failure —
are detected **24/24 each**. IE now exceeds the threshold on **86%** of malicious
cases where it previously did so on 17%.

## What this does not establish

Three limits, stated at the time and all consequential:

1. **The adaptive loop is further than ever from having work to do.** With no
   residual failures, no threshold improves anything.
2. **The causal contrast is redundant, not independent** — 0/114 cases detected
   by IE that the standalone rule missed. This follows from corpus construction:
   every family embeds the address inside the directive, so removing the
   directive removes the address and the contrast tracks severity mechanically.
3. **Complete coverage was measured against an FPR test that cannot fail.** None
   of the 4 benign controls contains an address or link of any kind; their
   severity is zero *structurally*, not as a finding. **The FPR of this
   configuration is not zero — it is unmeasured.**

All three are what [[6n — A Corpus That Can Fail]] was built to address.
