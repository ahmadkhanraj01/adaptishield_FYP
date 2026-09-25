# Layer 5 — Human-in-the-Loop and Observability

**Status:** ✅ Built — all four planned components, stdlib only, 20 deterministic tests

Four components, split by whether they **read** or **write**:

| Component | Form | Entry point |
| :--- | :--- | :--- |
| Audit Dashboard | self-contained HTML | `python -m layer5.audit_report` |
| Policy Inspection Console | (same file) | ″ |
| Audit Logs | (same file) | ″ |
| **Manual Override** | **CLI + append-only log** | `python -m layer5.review` |

No dependencies outside the standard library. No server, no build step, no
network call at render time or view time.

---

## Why this layer is not decoration

The old version of this file said a dashboard is "presentation, not
proof-of-concept." That was right about dashboards and wrong about this layer.

README §6n records the failure Layer 5 exists to catch: the GRPO policy proposed
a change to a security threshold that **its own reward function scored lower**
(+0.8683 against the incumbent's +0.8688), and `apply_update` would have accepted
it silently. It has since done the same thing twice more — most recently
+0.8329 against +0.8330, on live data.

`AdaptiveThreatModel.apply_update()` already refused unless `approved=True`, so
the seam was correct from the start. What was missing was anything on the other
side of it: the only caller passed `approved=True` as a literal. The gate was a
rubber stamp, and no record survived of who approved what, or on what evidence.

## The design rule

**Never trust the proposal's own arithmetic.**

A proposal arrives carrying a `mean_reward` it computed about itself.
`governance.py` recomputes *both* sides — incumbent and proposal — from the
labeled episodes using the same reward config, and shows the reviewer its own
numbers next to the proposer's claim. If they disagree, that disagreement is the
most important thing on the screen: the artifact does not describe the change it
would make.

The gate **recommends and never decides**. A gate that auto-approves reintroduces
the original failure one level up, so `recommendation()` returns a string and
`review.py` requires a typed verdict *and* a reason. An approval with no recorded
reason cannot be audited later.

The console also surfaces the trainer's own propose-and-verify trace, because a
rejected proposal serialises as a no-op and looks like nothing happened. What
actually happened is that the learned policy wanted something, the verifier
scored it against the incumbent, and it lost — the reviewer should see the
machine disagreeing with itself, not a blank diff.

## What the reviewer is warned about

Ordered most-serious-first, because reviewers read the top of a list:

- **REGRESSION** — scores lower than doing nothing (the §6n failure).
- **CLAIM MISMATCH** — the proposal misreports its own effect.
- **FALSE POSITIVES INCREASE** — with a pointer to check whether they land in
  the externally-authored cohort (§6n: a marker weight that looked free on
  hand-written controls produced 36 FPs of 68 on AgentDojo data).
- **WORKFLOW LOST INCREASES** — a blanket block still scores positive, so a
  proposal can trade usability for detection and still look good.
- **NO MEASURED BENEFIT** — risk with no upside; the no-op is the safe outcome.
- **INERT PATTERN** — see below.
- **LITERAL TARGETS IN PATTERNS** — fix A removed literal harvesting; their
  reappearance means a regression.
- **THIN EVIDENCE** — under 50 episodes, differences are not distinguishable
  from noise.

### A defect the console found on its first run

Every proposal the trainer has produced includes
`new_blocked_patterns: ['ignore previous']`. That pattern **can never fire**: 3A
matches `blocked_patterns` against the **`proposed_action`**, but the trainer
harvests candidates from **`flagged_markers`**, which describe *mediator
content*. Different namespaces. The string appears as a marker on 48 of 188
episodes and in **0** proposed actions.

A rule that reads as protection and provides none is worse than no rule, so the
gate measures every proposed pattern against the batch and reports the inert
ones.

## Reading untrusted text safely

The records contain prompt-injection payloads by construction — `mediator_snippet`
is attacker-authored, and reading it is the point. Every value is HTML-escaped,
and the embedded JSON has `<`, `>` and `&` escaped so a payload containing
`</script>` cannot terminate the block and become live DOM. An audit tool that
could be attacked by the thing it audits would be an unusually poor one; pinned
by `tests/test_layer5.py`.

## Why one HTML file and not Flask/React

The whole record set is ~1.2 MB, which fits in the page. Embedding it means every
filter, sort and drill-down runs locally with **no request/response cycle** —
faster than a server, not slower. The artifact is one file: opens by
double-click, needs no process, no dependency and no build, and can be archived
next to the campaign that produced it.

Manual Override is the exception and gets a CLI, because it *writes*. A browser
button on a local server has nothing authenticating it, which is not a property
one wants in the approval path of a security system; a command with an
append-only decision log is simpler and more defensible.

## Files

| File | Role |
| :--- | :--- |
| `governance.py` | Evidence recomputation, warnings, recommendation, append-only decision log |
| `review.py` | The Manual Override CLI (`--list`, `--verdict/--reason`, `--apply`) |
| `audit_report.py` | Renders dashboard + console + logs to one HTML file |

Outputs land in `logs/layer5/` (`audit.html`, `decisions.jsonl`).

## Usage

```bash
python -m layer5.audit_report --open          # build + open the dashboard
python -m layer5.review                       # interactive review of a proposal
python -m layer5.review --list                # decision history
python -m layer5.review --verdict reject --reason "no measured benefit"
python -m layer5.review --verdict approve --reason "..." --apply   # commit
```

Tests: `python3 -m pytest tests/test_layer5.py -v` (20, deterministic, <0.1 s).
