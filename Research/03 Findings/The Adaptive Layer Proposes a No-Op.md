---
tags: [adaptishield, finding, negative, principal]
type: finding
---

# The Adaptive Layer Proposes a No-Op

**The honest headline of the adaptive component**, at every scale tested.

## The chain of evidence

| Scale | Result |
| :--- | :--- |
| 4 families, post-[[Fixes A-D]] | [[6j-6k — The Loop Closes a Matching Gap]] — nothing left to close; 3D proposed nothing and `apply_update` refused |
| 118 episodes, 6 families | [[6l — No Natural Gap at Scale]] — reward **flat across the entire IE grid**; GRPO converges to a no-op |
| 114/114 detection | [[6m — The Single-Character Defect]] — with no residual failures, no threshold improves anything |
| 188 episodes, 5-dim joint space | [[6n — A Corpus That Can Fail]] — the one gain found was a corpus artifact |

## Why, quantified

**All 4 residual misses are `masked = 0`** — severity-function failures. **None
is reachable by the threshold 3D controls.** That is not an opinion about the
adaptive layer; it is a decomposition → [[Residual Misses Decomposed]].

The remaining detection leverage is in **the probe and the severity function**
([[3B Causal Analyzer]]) and **the sanitizer** ([[3C Context Sanitizer]]) — *not
in the adaptive layer at all.*

## Two further reasons not to dress it up

1. **The learned distribution is near-uniform.** The argmax comes from the
   **minimal-intervention tie-breaker**, not from the data. *A tie broken by a
   tie-breaker is not a learned policy and should not be presented as one.*
2. **Two of five dimensions are unidentifiable** — reward is exactly flat in
   `risk_threshold` and `window_size` because campaigns never share a
   `session_id` → [[6g — Temporal Drift Scoping]]. The trainer **reports this
   itself**, which is preferable to learning a spurious preference over knobs the
   data cannot constrain.

## Why this is the right thing to report

> **A defense that reports "no gain" when there is no gain is more useful than
> one tuned until it shows one.**

🔴 **Do not tune 3D until it shows a gain. The no-op is the result.** See
[[Rules and Invariants]].

## What this does not establish

That the adaptive mechanism does not work — [[6j-6k — The Loop Closes a Matching Gap]]
shows it closes *and generalizes* a gap its knob matches. And it does not
establish that a learned policy is no better than the heuristic: with no reachable
gap **neither can improve detection**, so their agreement is not a comparison.
