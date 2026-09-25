---
tags: [adaptishield, finding, lesson]
type: finding
---

# Backstops Mask Progress

**The measurement trap this project has fallen into twice.**

## The mechanism

[[Layer 4 — Sandbox and Isolation]]'s egress allowlist gates **independently** of
every detection layer. That is the correct security design — a detection miss is
not a breach — and it is why [[ASR]] has stayed at 0% on address-carrying attacks.

It is also why **ASR is nearly useless as a detection metric here**: the allowlist
catches the exfiltration regardless of whether any detection layer noticed. ASR
was 0% before *and* after every [[3B Causal Analyzer]] fix.

> **Judge detection by the layer under test (`caught_by_causal`), not by the
> end-to-end ASR the backstop guarantees.**

## Occurrence 1 — diagnosed in 6n

Every attack family embedded the exfil address inside its directive and pointed
at an attacker-controlled host, so Layer 4 absorbed every failure.
[[Address-Free Attacks]] were added **precisely** to make a 3A/3B failure visible
in the outcome: they carry the **legitimate** destination deliberately, so the
allowlist passes them.

## Occurrence 2 — the same mistake, repeated

[[Phase 7 Benchmark Withdrawn]]. **Six of the eight benchmark vectors were
written to point at an exfiltration host.** In the `static_only` arm *nothing was
blocked by any detection layer* — every stop came from the allowlist. The `full`
arm scored identically for the same reason.

The two arms were **equal by construction rather than by measurement.**

> The remedy is the same as before: point the malicious vectors at the
> **legitimate** destination so that a detection failure becomes visible, and
> **record which layer stopped each case** rather than only whether it was
> stopped.

## The lesson, stated generally

A backstop that guarantees your headline metric also guarantees that your
headline metric cannot measure the thing above it. **Any evaluation of layer *n*
must be run in a configuration where layer *n+1* does not absorb its failures.**

The corollary is per-layer attribution: binary "was it stopped?" cannot answer
"which layer stopped it?" → [[Next Task — Repair the Phase 7 Benchmark]].

See also [[Design Lessons]].
