---
tags: [adaptishield, architecture, layer]
type: component
status: built
---

# Layer 5 — Human in the Loop

Human governance over the adaptive system. Built in Phase 8; stdlib only; 20
tests.

## Four components

| Component | File | Role |
| :--- | :--- | :--- |
| **Audit Dashboard** | `layer5/audit_report.py` | Boundary-indexed causal-effect trajectories, takeover events with localized boundary indices, policy update history — one self-contained HTML file |
| **Policy Inspection Console** | `layer5/audit_report.py` | Visibility into and control over 3D's current rule set, via a *governed* update channel back to [[3A Policy Engine]] |
| **Manual Override** | `layer5/review.py` | The interactive gate; append-only decision log |
| **Audit Logs** | `layer5/governance.py` | Immutable record of events, policy updates, detection decisions, overrides |

Run: `python3 -m layer5.audit_report --open` · `python3 -m layer5.review`

## The one rule the gate operates on

**It does not trust the proposal's arithmetic.**

A proposal arrives carrying a figure of merit *the proposer computed about
itself*. The gate **recomputes** both the incumbent and the proposed
configuration from the labelled episodes using the same reward definition, and
displays its own numbers beside the proposer's claim. Where the two disagree,
that disagreement is the most prominent item on the display — because it means
the artifact under review does not describe the change it would make.

It also surfaces the trainer's propose-and-verify trace, since a *rejected*
proposal serialises as a null change and presents to a reviewer as though nothing
happened.

## It recommends and never decides

A gate that approves automatically reintroduces, at one level of remove, exactly
the failure it was built to prevent. The recommendation is returned as text, and
recording a decision requires **both an explicit verdict and a stated reason** —
an approval with no recorded reason cannot be audited afterwards, which makes it
indistinguishable from no approval at all.

## Why it is load-bearing rather than ceremonial

[[Reward-Decreasing Proposals]] — four times the learned policy proposed a change
its own reward scored lower, and the unguarded commit path would have accepted
each silently.

## What it found on its first run

[[Inert Blocked Patterns]] — a defect present in **every proposal the trainer had
ever produced**, invisible to the trainer, the reward function, the verification
step and the minimality pass.

## Handling caveat

The dashboard escapes untrusted mediator text so the audit tool cannot be
attacked by what it audits. Publishing it still requires settling visibility and
[[AgentDojo]] attribution — see [[Backlog]].
