---
tags: [adaptishield, finding]
type: finding
---

# 6g — Temporal Drift Scoping

## The bug

The drift rule — falling ACE / rising IE slope across recent boundaries — was
computed over **one flat list** of history, so slopes were being taken **across
unrelated red-team cases**. That is noise, not a trend.

It also fired on **empty boundaries**, where nothing had been observed at all.

## The fixes

1. 🔴 **Drift history is scoped per `session_id`.** Never revert to one flat
   list.
2. 🔴 **"Nothing observed" must never mean takeover.** The drift rule is gated on
   `masked ≥ 1`.

Both pinned in `tests/test_takeover_rules.py` → [[Rules and Invariants]].

## The consequence nobody anticipated

Scoping drift per session made the rule correct — and **unreachable in
evaluation**. Campaigns assign a **unique `session_id` to every case**, so the
drift rule never accumulates the history it requires and therefore never fires.

That in turn makes two of [[3D Adaptive Threat Model]]'s five dimensions
(`risk_threshold`, `window_size`) **unidentifiable**: the trainer reports reward
exactly flat in both, and says so itself.

Multi-turn sessions would make the temporal-drift rule learnable for the first
time → [[Backlog]].

## What this does not establish

Anything about whether drift detection *works*. It has never been exercised
end-to-end on a multi-turn corpus. It is correct-by-construction and untested by
measurement.

Part of [[Takeover Rule Stack]].
