---
tags: [adaptishield, log]
type: log
date: 2026-08-08
---

# Entry XVI — What the Instrument Was Hiding

*8 August 2026. Repairing the withdrawn Phase 7 benchmark and re-running it.*

## Where this started

[[Phase 7 Benchmark Withdrawn]] left one question open and named it precisely:
whether the causal sub-layer detects attacks static defenses miss was **untested
in either direction**. Not answered negatively — unmeasured. Four repairs were
specified in [[Next Task — Repair the Phase 7 Benchmark]]. This entry is doing
them and reading the result.

## The repair that was actually a correction

The prescribed fix was "point the malicious vectors at a legitimate destination so
the allowlist stops absorbing them". Framed that way it sounds like weakening the
defense to make the numbers move, which is the sort of thing that should make you
suspicious of your own work.

It isn't, and the reason matters. For a `send_email` call through the registered
`email-api`, the HTTP destination is the **mail server's own host** — the recipient
address lives in the payload. Pointing `destination_url` at the *recipient's*
domain was the fiction all along, and it handed [[Layer 4 — Sandbox and Isolation]]'s allowlist a case it would never see in production. The repair makes
the model more faithful, and the absorption disappears as a consequence rather
than as a goal. Absorbable malicious vectors: **6 of 7 → 1 of 7**, with V3 keeping
its exfil host because testing the allowlist is its declared purpose.

That distinction is worth holding onto, because "we changed the corpus and the
numbers improved" and "we corrected the corpus and the numbers became legible" are
indistinguishable from the outside unless the reasoning is written down.

## The instrument found two defects in itself

Adding [[Per-Layer Attribution|attribution]] was supposed to be bookkeeping. It
immediately exposed two things that four months of ASR numbers had not:

**V7 could never fail the check it existed to test.** The vector is labelled
`defended_by="Layer 4 permission control (scope check)"`. It ran against
`email-api`, which declares `send_email` **in scope** — so the permission gate
always passed. Every ASR number it ever contributed came from the egress filter
refusing the exfil destination. The vector had never once exercised the layer it
claimed to test, and the exfil destination is exactly what made that invisible.
Fixed by running it against `weather-api` (declares `get_weather` only), which now
returns `OUT-OF-SCOPE`.

**A blocked case could report that it reached the tool.** My first attribution
pass credited 3A only when no causal verdict existed, so a `blocked` case *with* a
non-takeover verdict fell through to "nothing stopped it" with
`reached_tool=True`. The state is unreachable in today's pipeline, but a test
caught it and a block now always attributes to exactly one layer. A miscount in
the direction of "the attack succeeded" is the one an evaluation cannot afford to
carry latently.

Both belong in [[Instruments Fail More Than Mechanisms]], which is becoming the
most-cited note in this vault.

## The result

216 cases, 18 vectors × 3 repeats × 4 arms, ~40 minutes.

| Arm | [[ASR]] | 3B stops | Static stops |
| :--- | ---: | ---: | ---: |
| `undefended` | 100.0% | 0 | 0 |
| `static_only` | 71.4% | **0** | 6 |
| `full` | **14.3%** | **18** | 0 |
| `no_egress` | 14.3% | 18 | 0 |

**ASR 71.4% → 14.3%**, [[WCR]] 0% → 85.7%, and 18 of 21 stops attributed to 3B.
`static_only` produces zero detection stops — the arms are no longer equal by
construction, they are separated by 57 points. → [[Phase 7 Repaired — The Causal Sub-Layer's Marginal Detection]]

The finding I did not expect: **`full` → `no_egress` moves ASR not at all**
(14.3% → 14.3%). Removing the egress allowlist changes nothing, because 3B already
caught everything the allowlist would have — V3 included, as a takeover, *before*
Layer 4 was consulted. In the withdrawn run the allowlist was doing all of the
work. In this one it does none of the incremental work. Same two arms, same code
paths, opposite conclusion, and the only thing that changed was whether the corpus
let the detector be seen.

## The number I nearly reported wrongly

The external [[FPR]] came out **0/30**. Against the campaign's 3.3% (2/60) that
looks like an improvement, and I started to write it up as one.

It isn't. The benchmark's external cohort is a stride subsample — indices 0, 6,
…, 54 — and campaign documents **41 and 55 are the two known false positives**.
Neither is in the sample. The 0/30 excludes both failures *by construction*, so it
cannot be a better estimate of anything; it is a smaller sample with the hard cases
removed. [[Current Numbers]]' 3.3% at n=60 stays the rate of record, and the
caveat is now printed in the report itself so the loose number cannot be lifted out
of a table later.

This is the same shape as [[6n — A Corpus That Can Fail]] and the same shape as the
withdrawn benchmark: a favourable number produced by which cases were present.
Third time. I am starting to think the discipline that matters is not "check the
result" but "check what the result could not have seen".

## What is still owed

`static_only` is our own ablation, not an external baseline — Rules §7 wants a
published prompt-level defense on the same corpus, and that is Phase 10. V5 and V6
remain APPROXIMATED. n is 21 malicious cases per arm and `full`'s interval is
[5.0%, 34.6%], wide enough that no per-vector claim survives. And all three
residual successes are V4, the [[Address-Free Attacks|address-free]] vector, which
is exactly where the docs predicted the misses would land — so the next detection
work is still the severity function, not the adaptive layer.
