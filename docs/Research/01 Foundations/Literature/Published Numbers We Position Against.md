---
tags: [adaptishield, literature, metric]
type: literature
date: 2026-08-17
---

# Published Numbers We Position Against

*The quantitative half of related work. Source of record is
`paper/external_numbers.json`; the table in §10 (`paper/10-positioning.md`) is
generated from it by `paper/make_positioning_table.py` and cannot be hand-edited.*

Every value below was read out of the primary source and stored with its verbatim
sentence. **A number without a quote does not go in the manuscript** — the
generator drops any row not marked `verified: "verbatim"` and prints it to stderr
as a to-do. This is the same discipline [[Wilson Score Interval]] and
[[Current Numbers]] apply to our own figures, extended to other people's.

## Attack success — [[InjecAgent]]

Zhan et al., Findings of ACL 2024. 1,054 test cases.

| Agent | ASR-valid | Setting |
| :--- | ---: | :--- |
| ReAct-prompted GPT-4 | 24% | base |
| ReAct-prompted GPT-4 | 47% | enhanced (hacking prompt) |
| ReAct-prompted Llama2-70B | >80% | both |
| Fine-tuned GPT-4 / GPT-3.5 | 3.8% / 6.6% | base |

**Ours on the same corpus is 100% undefended** (60/60, `direct_harm_base`). That
is a *floor check*, not a result: our agent is 3–4B local, so it is more
compliant than anything they measured. It earns the right to report a downstream
difference and nothing more.

## Defenses — [[AgentDojo]] and spotlighting

- **Tool filter** (Debenedetti et al., NeurIPS D&B 2024): *"lowering the attack
  success rate to 7.5%"* — verbatim.
- **Spotlighting** (Hines et al., arXiv:2403.14720): *"spotlighting reduces the
  attack success rate from greater than 50% to below 2%"*, GPT-family — verbatim.
  **We measure 34.8% → 33.3%, McNemar p = 1.00** on our harness
  → [[Phase 10 — Spotlighting Has No Measurable Effect]]. Almost certainly a gap in
  setting, not a contradiction, and §4 carries the per-family decomposition.
- ✅ **AgentDojo's undefended baseline and delimiting arm, both released
  13 Sep 2026** after a human read Table 5 in the primary source. From one table,
  one model (GPT-4o), with the paper's own 95% intervals:

  | Table 5 row | Benign utility | Utility w. attack | Targeted [[ASR]] |
  | :--- | ---: | ---: | ---: |
  | No defense | 69.0% (±3.6) | 50.01% (±3.9) | **57.69%** (±3.9) |
  | Delimiting | 72.66% (±3.5) | 55.64% (±3.9) | **41.65%** (±3.9) |

  **Delimiting removes 16.04 points, intervals non-overlapping, at no cost in
  benign utility** — and still leaves 41.65% of targeted attacks succeeding. It is
  the only published prompt-level result here carrying its own undefended row, so
  it is a *difference* rather than a level, which is why §VI-D uses it against our
  own null rather than the spotlighting quote above.
  ⛔ **The 45.8% this supersedes was wrong twice over**: twelve points off, and
  taken from Table 2's attacker-knowledge ablation rather than the undefended
  headline. It sat in `external_numbers.json` from August to 12 September →
  [[A Published p-Value With No Committed Source]] is the same failure with a
  different number.
- 🟡 **The tool filter is two numbers, and the paper gives both.** The body text
  says *"lowering the attack success rate to 7.5%"*; Table 5's tool-filter cell
  reads **6.84% (±2.0)**. Checked 14 Sep against the surrounding paragraph: it is
  **not** a different model (the paper focuses on GPT-4o from that point), not
  untargeted ASR, and not an average across models. Same defense, same model, same
  metric, **0.66 points apart** — larger than rounding and not resolvable from the
  text.

  **Neither is chosen.** The row keeps 7.5% and stays `verbatim` — the quote is
  real and the value matches it — and carries a `discrepancy_note` plus a setting
  saying *stated in the body text, not read off Table 5*. §II quotes the prose
  figure and names the table figure beside it; §XI reports the discrepancy rather
  than resolving it.

  ⛔ **6.84% was deliberately not promoted to a row.** That is a new `verbatim`
  claim, and the 13 Sep read confirmed the *No defense* and *Delimiting* rows, not
  this cell. To resolve: a human reads both, then the row is re-scoped or a Table 5
  row is added → the same rule that held [[A Published p-Value With No Committed Source]]
  back for four weeks and was right to.

## Detectors — the FPR/FNR landscape

From PIShield's Tables 1 and 2 (Zou et al., arXiv:2510.14005), averaged over OPI,
Dolly, MMLU, BoolQ, Musique, NarrativeQA. Detection = 100 − FNR.

| Detector | Detection | [[FPR]] |
| :--- | ---: | ---: |
| PIShield | 98.6% | 0.5% |
| PromptGuard | 91.3% | 40.3% |
| DataSentinel | 89.6% | 33.6% |
| TaskTracker | 68.3% | 27.4% |
| PromptArmor | 54.1% | 1.3% |
| AttentionTracker | 44.7% | 32.8% |
| InjecGuard | 33.7% | 8.2% |
| PIGuard | 29.8% | 0.7% |
| ProtectAI-deberta | 24.1% | 10.1% |

## Why this table earns its place

Those detectors sit on an FPR/FNR curve; a contribution is a better point on it.
**Ours does not sit on that curve.** At one fixed FPR (3.3%) it is 96.7% on the
target-bearing stratum and 10.0% on the no-target one — the split is the presence
of a liftable target, not a threshold
→ [[Phase 12 — Detection Is 18% on Someone Else's Attacks]].

None of the nine reports its numbers stratified this way. That is not a claim
they share the failure; it is a claim their evaluations **as reported** could not
show it either way, which is a related-work observation with an experiment behind
it.

## What has no comparator

- **Our campaign detection (96.7%)** — an attack set we wrote is not comparable
  with anyone's published number, and it is still the one headline without an
  artifact under `results/` → [[Current Numbers]].
- **Utility under attack.** Every agent-benchmark paper here reports it; our
  corpus has no benign task-completion metric of comparable construction, so
  there is no honest row. Carried in §9 as a limitation.
