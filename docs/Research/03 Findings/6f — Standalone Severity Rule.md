---
tags: [adaptishield, finding, positive]
type: finding
---

# 6f — Standalone Severity Rule

**The first change that improved the system rather than a component.**

## The problem it fixes

[[ACE IE DE]] — IE **silently inverts when [[3C Context Sanitizer]] fails**. If
the sanitizer leaves an injection intact, both the masked and masked-sanitized
regimes comply, the 2s cancel to `IE = 0`, and an attack that **survived**
sanitisation reads as **safe**.

A stronger attack therefore produced a *weaker* signal. That is the wrong sign.

## The rule

> Takeover fires if `masked ≥ masked_takeover_threshold` (2.0), **independent of
> IE**.

An attack robust enough to defeat the sanitizer is now **caught rather than
excused by it**.

## Why it is load-bearing

It carries the strong-evidence cases, which is precisely what allows rule 1 (the
IE contrast) to afford being conservative — and therefore what made
[[6h — IE Consistency Guard]] affordable at all.

🔴 **Invariant:** rule 2 must always be able to fire even when the consistency
guard suppresses the contrast. Never tighten the guard without it. Pinned in
`tests/test_takeover_rules.py`. See [[Takeover Rule Stack]] and
[[Rules and Invariants]].

## The generalizable form

> **Any detector built on "A minus B" must be paired with a standalone-evidence
> rule for the case where A and B both move together.**

## What this does not establish

That the standalone rule is sufficient. Until [[Address-Free Attacks]] existed,
it was in fact *dominant* — no case in the corpus was caught by IE that the
standalone rule missed (0/114). That changed to 14/116 only after the corpus was
extended → [[6n — A Corpus That Can Fail]].
