---
tags: [adaptishield, finding, corpus, fpr, measurement]
type: finding
status: measured
date: 2026-09-12
---

# AgentDojo's Benign Pool Is Exhausted at 60

**The 60 benign documents are not a draw from a larger pool — they are the
complete benign content of [[AgentDojo]]'s two in-domain suites.** There are zero
disjoint episodes left to add. Every route to a larger *n* is a change to the
sourcing policy, not a deeper draw, and each one buys interval width with
provenance.

✅ **Landed in the manuscript 13 Sep 2026** (`656d8b6`): §XII's benign-corpus
bullet now says census rather than sample → [[Entry XXVII — The Prose Catches Up With the Finding]].

## What was checked

The wheel for v0.1.35 was fetched fresh and the committed
`red_team/vendor_agentdojo.py` re-run against it. The harvest reproduces
**item-for-item and in the same order** as `red_team/data/agentdojo_benign.json`:

```
harvested=63  duplicates_dropped=3  excluded_injection_fields=10  vendored=60
```

No version drift, no task identifier that fails to resolve, no silent edit
upstream. The corpus contract in [[Recorded Probe Output Makes Scorer Changes Cheap]]
holds against the package as published today.

The committed policy is: suites `workspace` + `slack`, fields `body` / `content` /
`description`, ≥ 40 characters, every `{*_injection}`-bearing field excluded,
deduplicated. Under that policy AgentDojo contains exactly 63 strings. **All 63
were already looked at. 60 survived. Nothing remains.**

## The whole pool, counted

New, unique, injection-free strings beyond the committed 60, across all four
suites and every field name in the environment YAML:

| Route | New | *n* | What it costs |
| :--- | ---: | ---: | :--- |
| Keep the policy exactly | **0** | 60 | nothing — and no expansion |
| `workspace`+`slack`, all field names ≥ 40 | 8 | 68 | `filename`, `participants` — not prose a `send_email` flow reads |
| `workspace`+`slack`, current fields ≥ 20 | 14 | 74 | admits fragments: *"Catch up over lunch."* |
| both of the above | 22 | 82 | both |
| + `travel` prose (`reviews` 53, +2) | 55 | 115 | off-domain |
| everything ≥ 40, all suites, all fields | 103 | 163 | `address`, `operating_hours`, `contact_information` — structured strings, not prose |

`banking` contributes **zero**: it has no non-injection string of 40 characters or
more anywhere in the suite.

## Why the two routes that clear 110 are the wrong ones

Only the `travel` routes reach the 110 that was wanted, and `vendor_agentdojo.py`
already refuses them in a comment written before this question was asked: *a
review is not something a `send_email` flow reads, and padding n with off-domain
content buys a tighter interval around a less meaningful quantity.*

There is a sharper reason now. Detection here rides on the target-match path, and
travel reviews carry **no address or URL an action could name**. Adding 55 of them
would almost certainly *lower* the measured [[FPR]] — for a reason that has
nothing to do with the defense and everything to do with what was added to the
denominator. A better-looking number produced by changing the distribution under
it is the failure mode of [[6n — A Corpus That Can Fail]] pointed the other way.

**And the width does not arrive anyway.** Holding the rate at ~3.3%, the projected
[[Wilson Score Interval]] goes 10.5 points wide at *n*=60, 9.0 at 82, 7.2 at 115,
5.7 at the maximally impure 163. *(Projection at an assumed rate — not a measured
result; the real counts would have to be recorded.)* The interval is wide because
the rate sits near zero, not mainly because *n* is 60. Tripling the corpus and
surrendering its provenance does not halve the width.

## 🔴 A latent trap this uncovered

Case identifiers are **positional**: `case_id=f"agentdojo-{item['suite']}-{i:03d}"`
over the vendored items list. Adding any `workspace` item shifts every later
`workspace` index *and* pushes the `slack` block off 056–059. `workspace-041`,
`-048` and `-055` would silently come to mean different documents — and those three
are cited by name in the manuscript, the README and
[[The Benign FPR Has a Noise Floor Its Own Size]]'s per-case matrix. Any future
re-vendoring needs a content-hash key **before** it runs, or the stability matrix
stops being comparable to the runs it is being compared against. → [[Traps]]

## The reframing this earns

"The benign corpus is 60 documents, which is small" understates what is true.
**It is a census, not a sample** — the complete in-domain benign content of a
published benchmark, verified exhaustive against the shipped package. That is a
stronger sentence, and it relocates the limitation: a tighter benign interval
needs a **second external benign corpus**, not more of this one. There is no third
corpus waiting, exactly as [[Backlog]] already records for the attack side.

## Related

- [[AgentDojo]] — what was taken and what deliberately was not
- [[The Benign FPR Has a Noise Floor Its Own Size]] — the other limit on this number
- [[FPR]], [[Wilson Score Interval]], [[Evaluation Corpus]]
- [[6n — A Corpus That Can Fail]] — why externally-authored benign data exists here
- [[Entry XXIV — The Corpus Was Already Complete]]

## What this does not establish

**Not that 60 is enough.** The interval is genuinely wide and a two-point FPR
difference remains unresolvable. The finding is that *this* corpus cannot fix it,
not that it needs no fixing.

**Not that AgentDojo is small.** It is exhausted *under this project's own
in-domain filter*. The suite contains 103 further strings; the judgement that
reviews, addresses and opening hours do not belong in a `send_email` false-positive
denominator is ours, and a reader who disagrees would reach a different ceiling.

**Not a statement about the rate.** Nothing was recorded or re-scored. Every
committed number — 3.3%, [0.9%, 11.4%], the 1/57/2 stability split — stands
untouched, and this note moves none of them.
