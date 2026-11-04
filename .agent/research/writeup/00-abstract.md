# 00 — Abstract

**Write this last.** An abstract is a summary of a paper that exists. Draft the
six other sections first, then come back here.

**Length target:** 200 to 250 words for an IEEE journal. One paragraph. No
citations, no figures, no undefined abbreviations.

---

## The recipe (one sentence per line, in this order)

1. **The problem, in one sentence.** Tool-using LLM agents read untrusted text
   and cannot tell content-to-process from a command-to-follow.
   `[meaning: an AI that reads emails or documents to do a job can be tricked by instructions hidden inside those emails]`
2. **What existing defenses do.** They either mark the untrusted text
   (prompt-level) or restrict what the agent may do afterwards (gate-level).
   `[meaning: today's fixes either label the suspicious text or put a fence around the agent's actions]`
3. **Our different question.** Did the agent's proposed action *change because of*
   the untrusted text? That is a causal question.
   `[meaning: instead of asking "does this text look bad", we ask "did this text change what the agent decided to do"]`
4. **What we built.** A six-layer pipeline whose distinguishing element is a
   causal detector, plus an adaptive component that proposes configuration
   changes for a human to approve.
5. **How we evaluated it.** Against externally-authored attacks, against a
   published prompt-level defense, and component by component.
6. **The honest framing.** The evaluation is largely negative, and the negative
   results are the contribution.
   `[meaning: most of what we found is "this does not work as hoped", and that is the useful part]`
7. **Result 1 — ablation.** Four of six components change no outcome on our
   corpus; ladder and leave-one-out ablations agree.
8. **Result 2 — baseline.** Spotlighting is a null on our harness: steered
   34.8% → 33.3%, McNemar *p* = 1.00, decomposing into two opposite per-family effects.
9. **Result 3 — external validity.** Detection falls from 96.7% (our attacks) to
   about 18% (InjecAgent), and the split is the finding: 96.7% where the
   target-match path can fire, 10.0% where it cannot, which is about 90% of that corpus.
10. **Result 4 — the repair.** Widening the harm taxonomy scores 90.0% in-sample
    and 43.3% on a corpus frozen beforehand; intervals do not overlap; not significant.
11. **Result 5 — multi-turn.** Two pre-registered experiments found the
    temporal-drift rule cannot fire: masked and unmasked regimes return the same
    severity on 24 of 30 turns, so the causal contrast is zero.
12. **The one claim.** The causal contrast carries signal when the injected content
    names a *liftable target* (an address or URL an action can name) and close
    to none otherwise.
13. **Reproducibility.** Every number regenerates from a committed command over a
    released artifact; the two headline experiments were pre-registered.

## Every number the abstract may use

| Number | Exact form | Source |
| :--- | :--- | :--- |
| Spotlighting null | 34.8% → 33.3% steered, paired McNemar *p* = 1.00 | `results/phase10/benchmark.json` |
| In-corpus detection | 116/120 = 96.7% [91.7%, 98.7%] | `results/campaign/campaign.json` |
| External detection, projected | ≈18% | `results/phase12/benchmark.json` |
| Target-bearing stratum | 96.7% (median of 3 runs) | `results/noise_floor/injecagent.json` |
| Address-free stratum | 10.0% (median of 3 runs) | `results/noise_floor/injecagent.json` |
| Share of InjecAgent that is address-free | 459/510 ≈ 90% | `results/phase12/manifest.json` |
| Taxonomy in-sample vs holdout | 90.0% vs 43.3%, *p* = 0.125 | `results/severity/rescore.json`, `rescore_holdout.json` |
| Flat contrast | `orig` = `masked` on 24/30 turns | `results/phase15/multiturn_r1.json`, `_r2.json` |
| Components that do nothing | 4 of 6 | `results/phase11/benchmark.json` |

## Index terms (keywords)

indirect prompt injection · LLM agents · causal detection · security evaluation
· negative results · tool-integrated language models · reproducibility

## What not to put in the abstract

- The architecture layer names (3A, 3B …). Say "a causal detector".
- Any number without its comparison. "96.7%" alone means nothing; "96.7% on our
  attacks, about 18% on someone else's" is the finding.
- The word "novel". Let the contributions show it.
- Anything from the limitations. The abstract states what was found, not what
  was not.

## The current draft, for reference

The manuscript's abstract is at the top of `paper/manuscript.md`. It follows the
recipe above at 330 words, which is long for IEEE Access. When you write yours,
aim shorter: cut sentences 4 and 5 to one sentence, and merge results 1 and 2.
