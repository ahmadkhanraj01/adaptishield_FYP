---
tags: [adaptishield, finding, corpus]
type: finding
---

# Address-Free Attacks

**18 attacks whose harmful action names no recipient at all** — 3 reconnaissance
and disclosure directives across each of the 6 families in the
[[Red Team Module]].

They are the corpus change that made two things measurable for the first time.

## Deficiency 1 they fix — the contrast was arithmetic, not mechanism

Every earlier family embedded the exfil address **inside** its directive. So
removing the directive removed the address, and IE tracked masked severity **as a
matter of arithmetic rather than of mechanism** → 0/114 cases where IE detected
what the standalone rule missed.

With address-free attacks: **13/115**, and now **14/116**. All are address-free
and they **span all six families**.

> This is the **first evidence in the work that the causal mechanism performs
> detection unavailable to a simpler rule.**

That claim is the entire justification for [[Causal Measurement Approach]] costing
two extra LLM probes per boundary, so it is not a small result.

## Deficiency 2 they fix — the allowlist concealed everything

They carry the **legitimate** destination, **deliberately**, so
[[Layer 4 — Sandbox and Isolation]]'s allowlist passes them.

> This is the **only construction under which a detection failure at 3A or 3B
> becomes visible in the outcome.**

→ [[Backstops Mask Progress]]. A campaign is therefore *expected* to show non-zero
[[ASR]] on address-free cases **by design** — Layer 4 is not a backstop there.

## Where they now dominate

All **4 residual misses** are address-free, and all are `masked = 0` severity
failures — with no address present, the target rule cannot fire as a fallback →
[[Residual Misses Decomposed]].

That is the correct outcome of adding them: they moved the hard cases from
*invisible* to *countable*.

## What this does not establish

That the corpus is now sufficient. 18 attacks across 6 families is a small,
author-written set, and [[6n — A Corpus That Can Fail]]'s central lesson is
precisely that author-written data cannot bound its own blind spots. The
*benign* side was fixed by importing [[AgentDojo]]; the malicious side has no
equivalent import.
