---
tags: [adaptishield, metric, corpus]
type: reference
---

# Evaluation Corpus

**188 episodes** — 120 malicious, 68 benign.

## Malicious (120)

| Source | Count |
| :--- | :--- |
| 6 families × 4 directives × 2 training targets | 48 gen-1 |
| gen-2 keyword-softened mutations | — |
| held-out generalization pass (2 unseen addresses) | — |
| [[Address-Free Attacks]] | 18 |

Built by the [[Red Team Module]]. 🔴 The train/held-out split is **enforced by
construction**, not by index slicing.

## Benign (68) — two cohorts, never pooled

| Cohort | n | Status |
| :--- | :--- | :--- |
| **[[AgentDojo]]**, externally authored (MIT, ETH SPY Lab v0.1.35) | **60** | ✅ The one worth quoting |
| Hand-written controls | 8 | ⚠️ **A diagnostic, never a rate** |

## The history of this corpus is the history of the project

Each version could not fail in a specific way, and fixing that changed a
conclusion:

| Version | Could not fail because | Fixed by |
| :--- | :--- | :--- |
| 4 families, 1 target | nothing held out — memorization looked like generalization | [[6d — Adaptive Loop Negative Result]] |
| 118 episodes, 4 benign | **no benign control contained an address or link**; severity was 0 *structurally* | [[6m — The Single-Character Defect]] §F |
| — | every family embedded the address inside the directive, so IE tracked severity **as arithmetic** | [[Address-Free Attacks]] |
| 128 episodes, self-authored benign | the screener marker GRPO learned to weight **fired on 0 of 8** of our documents | [[6n — A Corpus That Can Fail]] |
| **188 episodes (current)** | 60 external benign; 18 address-free; both cohorts separate | — |

> **A defense measured only against a corpus its author wrote measures the
> author's imagination.**

## What is still author-written

**The malicious side.** The benign side was fixed by importing external data; the
attack side has no equivalent import. That asymmetry is unaddressed →
[[Backlog]].

Pinned by `tests/test_corpus.py` (22 tests: corpus invariants, Wilson,
IE-ablation join).

## Externally-authored attacks (added 9 Aug 2026)

[[InjecAgent]]'s direct-harm split — 510 cases, MIT, cited — vendored by
`red_team/vendor_injecagent.py`. This closes the half of
[[6n — A Corpus That Can Fail]]'s lesson that had been left open: the benign side was
fixed by importing [[AgentDojo]], the attack side had no equivalent until now.

**Kept as its own cohort** (`attack_external`), never pooled with our campaign or
the taxonomy vectors, and **stratified** on whether 3B's target-match path can fire —
51/510 can, 459/510 cannot. That split is the whole finding →
[[Phase 12 — Detection Is 18% on Someone Else's Attacks]].
