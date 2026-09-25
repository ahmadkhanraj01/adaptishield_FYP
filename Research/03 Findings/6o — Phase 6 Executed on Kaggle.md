---
tags: [adaptishield, finding]
type: finding
date: 2026-07-26
---

# 6o — Phase 6 Executed on Kaggle

**Half the trainer had never been run.**

## The gap being closed

The policy-gradient loop is implemented **twice** — once in torch, once in the
standard library — and *every result in the project came from the second*, because
the development machine has no torch and the regression suite is deliberately
torch-free.

> **Two implementations of one algorithm that have never been compared are two
> algorithms.**

The claim that the project contains a real policy-gradient trainer rested on the
half that had never executed anywhere, by anything.

**Closing that gap was the sole purpose of running on Kaggle. It was never the
compute** — the joint search is ~0.27 s on one core over a 188-row table. What
the remote environment provides is not speed but the mere **importability of
torch**.

## Result — the comparison succeeded

The two implementations agree to **exactly zero** on:

- the incumbent's reward
- each implementation's reported reward, independently recomputed
- the accept-or-reject verdict
- the final proposed action

**One difference is worth recording:** the two policies selected **different
preferred actions** and nonetheless produced the **same proposal**, because the
stochastic search diverged while the deterministic verification converged.

That is the verification step performing exactly its function — and independent
evidence that **a learned policy's preference cannot serve as a decision rule**,
since it is not stable across random streams, let alone across implementations.
The verifier rejected the policy's preferred action for a **fourth** time
(+0.8330 vs +0.8329), on different hardware with a different RNG →
[[Reward-Decreasing Proposals]].

## The hardware premise was false

🔴 **The P100 cannot run PyTorch.** It is compute capability **sm_60**; the Kaggle
torch build requires **sm_70+**. And `torch.cuda.is_available()` returns **True**
— it answers whether a driver and visible device exist, not whether the build can
execute on them — so the trainer announced its torch backend, loaded its episodes,
and **only then died**.

`_torch_device()` now probes with a real allocation and falls back to CPU,
reporting why. Nothing of substance is lost; no prior result depended on the
accelerator. **The honest restatement:** this phase is validated as an off-machine
**cross-check of two implementations**, not as accelerated training. See
[[Compute Strategy]].

## Six attempts, five defects

Each visible only once its predecessor was repaired:

1. module import searched 2 directory levels below the mount point; the dataset
   appears 4 levels down
2. the episode locator repeated that error identically
3. the device predicate reported a device the build could not use
4. the backend comparison compared **incommensurable quantities**
5. the orchestration script's status poll **matched nothing at all**

**Defect 5 is the important one.** Its patterns were case-sensitive while the
remote status is upper case, so **neither the success branch nor the failure
branch could ever be taken**. The loop ran to its iteration limit against an
already-dead job, downloaded whatever was present, printed a completion message
and **exited zero**. It converted every other failure in this list into a
reported success.

**Defect 4 is a methodological error, not a slip.** The instrument built to
validate the trainer produced a *confident failure verdict accusing the trainer of
a defect that resided in the instrument*: it compared the reward of *the action
each implementation chose*, and since the two draw on different random streams
they generally choose different actions — so it would report failure precisely
when the policies diverged, which is expected behaviour. The correct evidence sat
adjacent and unread: the **incumbent's** reward, one action evaluated by one
function, agreed exactly. Both feed [[Instruments Fail More Than Mechanisms]].

## What this does not establish

That GRPO training was ever run at a scale where an accelerator matters. It was
not, and cannot be on this workload.
