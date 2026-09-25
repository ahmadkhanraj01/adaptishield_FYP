# §3 — Per-component ablations: only two components do anything

*Source: `results/phase11/benchmark.json`, `results/phase11_loo/`. Statistic:
`evaluation/paired.py`. 54 cases per arm (21 malicious, 33 benign).*

## Why this section leads

A layered architecture invites the assumption that each layer contributes. We
tested that assumption directly and it is largely false on our corpus. Reporting
it first is what licenses every claim that follows: a reader who has already seen
which components are inert will read the remaining numbers as measurements rather
than as advocacy.

## Design

Two ablations, run independently and compared:

- **Cumulative ladder** — seven arms, each adding exactly one component in
  pipeline order: `undefended → screener_only → plus_policy → plus_causal →
  plus_sanitizer → plus_permission → full`.
- **Leave-one-out** — six arms, each removing one component from the complete
  system.

The two disagree precisely when components are redundant with one another, so
running both is not duplication — it is the test for redundancy. They did not
disagree on a single row.

Outcomes are **paired** (McNemar, exact binomial below ~25 discordant pairs)
rather than compared as two intervals, because the arms see identical cases.

## Result

| Outcome | The only rung that moves | helped / hurt | p (exact) |
| :--- | :--- | ---: | ---: |
| attack stopped | `plus_policy → plus_causal` (**3B**, causal analyzer) | 18 / 0 | 7.6 × 10⁻⁶ |
| workflow continued | `plus_causal → plus_sanitizer` (**3C**, sanitizer) | 18 / 0 | 7.6 × 10⁻⁶ |

Every other rung — the L3 tool-response screener, the 3A policy engine, Layer 4
permission control, Layer 4 egress allowlist — is **0 helped / 0 hurt with zero
discordant pairs**. Not a weak effect: an identical outcome on all 21 malicious
cases, confirmed from both directions.

![Cumulative component ablation](figures/fig1_ablation.png)

**Figure 1.** Cumulative ablation over the seven-arm ladder (21 attacks, 33 benign).
Attack-stopped rate rises only at the causal analyzer (3B, +85.7 pts) and
workflow-continued rate only at the sanitiser (3C, +85.7 pts); every other rung —
screener, policy engine, and both halves of Layer 4 — is flat. *Source:
`results/phase11/benchmark.json`.*

**Predictions were registered before the run and all four held**: 3B's rung
large, 3A's `helped == 0`, 3C flat on ASR but large on WCR, and Layer 4 egress
`helped == 0`. That is what makes this evidence rather than post-hoc
rationalisation.

## Two results that cut against the architecture

**Layer 4 is redundant, not contributing.** `backstop_share` — the fraction of
3B's stops that a static allowlist would also have caught — climbs 0% → 17% →
**33%** as Layer 4 is added. Six of 18 stops are double-covered. This is
defensible as defence-in-depth, but it is not evidence *for* the layer, and we do
not present it as such.

**False positives moved where no p-value could see it.** On our own hand-written
benign controls, false positives went **0/3 → 3/3** the moment 3B switched on.
No paired test in either table detects this, because paired tests exclude benign
cases by construction: an arm that blocks a benign document is *worse*, so
pairing at the same polarity would let over-blocking read as a win. We report it
as a separate diagnostic at n = 3 and never as a rate.

## A measurement defect worth reporting

The first pass of this analysis reported *"the sanitizer adds nothing
detectable"* for a rung that moves workflow-continuation from 0% to 85.7%. The
statement was true of the outcome variable tested (ASR) and false of the
component. 3C runs only after a takeover is confirmed and converts a blanket
block into a safe continuation, so its entire contribution is usability, and an
ASR-only ablation is structurally incapable of seeing it.

This is the same failure as judging a defense by end-to-end ASR while a backstop
absorbs every case: **the wrong outcome variable makes a real effect invisible.**
The ladder now runs on both outcomes and calls a rung inert only when it moves
neither. We report the defect because the corrected table is only trustworthy in
light of what the first one got wrong.

## Scope

This establishes that L3, 3A and Layer 4 have nothing to do **on this corpus**,
not that they are useless in general. All 21 malicious cases are tool-response
injections converging on one action shape. A rug pull or a poisoned tool manifest
is what the screener and registry exist for, and two of the eight benchmark
vectors are approximated precisely because the pipeline consumes tool *responses*
rather than manifests. §5 is the test of that boundary.
