---
tags: [adaptishield, finding, principal, lesson]
type: finding
---

# Instruments Fail More Than Mechanisms

**The pattern that runs through the entire project.**

> The instruments built to *judge* this system have failed more often than the
> system itself. In each case the code **announced a conclusion it had not
> tested.**

## The roll-call

| Instrument | What it reported | What was true |
| :--- | :--- | :--- |
| Kaggle credential check | **PASS** | It exercised an endpoint returning an *empty collection* rather than an auth error, and read emptiness as health. The credentials could not upload a byte |
| Orchestration status poll | **Success, exit 0** | Case-sensitive patterns could match neither `SUCCESS` nor `ERROR`. It ran to its iteration limit against an already-dead job, downloaded whatever was present, and printed completion. **It converted every other failure in the sequence into a reported success** |
| Cross-implementation backend check | **Confident FAILURE**, accusing the trainer | It compared the reward of *the action each implementation chose*; different RNGs choose different actions, so it reported failure exactly when the policies diverged — expected behaviour. The correct evidence sat adjacent and unread |
| `fpr_report` | Current FPR | It served figures from a **campaign that had crashed part-way**, because it reads whatever file is present and cannot tell whether it is current |
| `probe_diagnostic` | Silent probe (3 cases) | Its classifier ordering attributed severity 0 to a silent probe **before** considering a garbled address — and would have directed the repair at the probe prompt, **which was not at fault** ([[6m — The Single-Character Defect]]) |
| AgentDojo exclusion filter | 0 injections found | It **searched for the wrong string**, and would have admitted 10 pieces of attack scaffolding into the benign denominator ([[AgentDojo]]) |
| Phase 7 benchmark | Clean 4-arm ablation | It **measured its own construction** → [[Phase 7 Benchmark Withdrawn]] |

**None of these was part of the defended system.** All were written to establish
confidence.

## The generalisation

> **Code that reports an untested verdict is more hazardous than code that fails
> outright** — because a crash is self-reporting, whereas a false pass is
> indistinguishable from success **and is trusted precisely because it was
> written to be trustworthy.**

Two of these had already been recorded in the project's documentation as
*working* before they were examined.

## The same structure appears in the results themselves

[[6n — A Corpus That Can Fail]] has this shape exactly: a policy-gradient method
confidently proposed a security regression its own objective scored lower, and
**every safeguard functioned correctly while none could detect that the
improvement it had verified was an artifact of a corpus the defender wrote.**

In both cases the failure was **not in the mechanism but in the apparatus for
judging the mechanism.**

## Guards adopted

- `fpr_report` now **prints the dataset age and shouts `STALE`** → [[Traps]]
- The backend comparison now asserts what actually holds: the **incumbent** must
  agree exactly, and each implementation's reported figure must match an
  independent recomputation of *the action it chose*
- The diagnostic's classifier ordering is pinned by regression tests
- [[Layer 5 — Human in the Loop]] recomputes rather than trusting

## What this does not establish

That the problem is solved. The gate is **a partial answer and should be
understood as such** — it addresses a proposer that misreports, and it found a
defect four automated checks had missed. **It cannot detect an error in its own
recomputation, and we make no claim that it could.**
