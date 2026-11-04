---
tags: [adaptishield, log]
type: log
date: 2026-07-26
---

# Entry XIV — The Human Gate

**26 July 2026 (later)** · Volume I · *the close of Volume I*

> *"Two pieces of work that turned out to be the same piece of work."*

The construction of [[Layer 5 — Human in the Loop]], and the first genuine
execution of the policy-gradient trainer on remote hardware. Both arrived at the
same observation.

## Sections

- **A** — the gate, and why it does not trust the artifact it reviews →
  [[Inert Blocked Patterns]]
- **B** — a trainer half of which had never executed →
  [[6o — Phase 6 Executed on Kaggle]]
- **C** — the hardware premise was false: **the P100 cannot run PyTorch**
- **D** — five defects, and the one that concealed the others
- **E** — the pattern, stated plainly →
  [[Instruments Fail More Than Mechanisms]]
- **F** — state and consequent work

## The substantive contribution

> **In this system the instruments built to establish confidence have been
> consistently less trustworthy than the mechanisms they were built to check.**

Three false verdicts of a single kind **within one working session**: a credential
check that passed without authenticating, a status poll that could detect neither
outcome, and a comparison that compared the wrong pair. *In each case the code
announced a conclusion it had not tested.* **Two had already been recorded in the
project documentation as working before they were examined.**

## Where Volume I ends

Detection **115/120**, [[FPR]] **3.3%** against externally-authored benign
content, and the binding constraint identified as **the masked probe** — which had
fabricated an email address on a benign document — together with the **severity
function**, accounting for four of the five residual failures. **None of the five
was reachable by the threshold the adaptive component controls.**

Volume I is now **closed and is not edited further**.

Previous: [[Entry XIII — A Corpus That Can Fail]] · Next:
[[Entry XV — Where a Fix Belongs]] (Volume II).
