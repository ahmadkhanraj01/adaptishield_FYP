---
tags: [adaptishield, rule]
type: reference
---

# Rules and Invariants

The hard constraints for anyone — human or AI — changing this codebase. **Most of
these are scars, not preferences**: breaking one has silently broken a result
before.

🔴 hard invariant (breaking it invalidates results or the build) ·
🟡 strong convention (break only with measurement + a doc update)

## Environment

- 🔴 **`./venv` is the runtime of record** — pipeline, tests, figures, paper and
  site all run under it, and it satisfies `requirements.txt` in full (13 Sep 2026).
  System `python3` carries numpy 2.2.6 and is not the runtime
- 🔴 **`numpy==1.26.4` is pinned** — numpy 2.x breaks on Python 3.10.12, and the
  pin must be written in `requirements.txt`, not only asserted here →
  [[Traps]] (*a pin that lives only in prose pins nothing*). ⛔ `installed.txt` is
  evidence of drift, never a lockfile
- 🔴 Python 3.10.12, Ubuntu 24.04, **4 GB VRAM is a hard ceiling**. Anything
  needing torch or a 7B+ model goes off-machine → [[Machine and Environment]]
- 🟡 The pipeline runs locally; Kaggle is training/eval only — it cannot host a
  live MCP server → [[Compute Strategy]]

## Models and probes

- 🔴 **Do not drop `k_samples` below 2** without re-validating 3B end-to-end
- 🔴 **Keep the per-component model split.** A more refusal-prone model on 3B
  **destroys the causal signal** → [[Models in Use]]
- 🔴 **The masked-probe prompt is calibrated.** It must keep refusing the softened
  escape hatches. Re-measure the gen-2 campaign + benign FPR if you touch it —
  and note that three attempts already **cost 8 detections** →
  [[6i — Masked Probe Rewrite]], [[6p — Probe Hallucination Fixed at the Scorer]]
- 🟡 If `semantic_scoring` is revisited, run the judge at **temperature 0**

## 3B takeover rules — pinned by `tests/test_takeover_rules.py`

- 🔴 **The standalone `masked ≥ 2` rule must always be able to fire**, even when
  the IE consistency guard suppresses the contrast. **Do not tighten the guard
  without it** → [[Takeover Rule Stack]]
- 🔴 **"Nothing observed" must never mean takeover** — drift gated on
  `masked ≥ 1`; IE gated on `masked ≥ 1` + consistent separation
- 🔴 **Drift history is per `session_id`.** Never revert to one flat list
- 🟡 `require_consistent_ie=False` exists **only for ablation**

## 3D

- 🔴 **Never touches LLM weights** — only 3A patterns/tools and 3B `ie_threshold`
- 🔴 **`apply_update` requires `approved=True`**
- 🔴 **Train on labelled data only** — inferring the label from the outcome is
  circular
- 🔴 **No literal exfil targets in proposals** — that is memorization
- 🔴 **`threshold_step` = `ie_resolution`** — a finer step is a provable no-op
- 🔴 **The reward is WCR-aware** — `+1.0` must beat `+0.7`. Do not collapse them

## Security and handling

- 🔴 **Layer 4 is defense-in-depth.** Permission, egress and sandbox gate
  *independently* of the 3A/3B/3C verdict. The sandbox executes only when
  permission **and** egress both pass
- 🔴 **Mediator text is untrusted everywhere — including in telemetry**
- 🔴 **Always hold out at least one attacker address from training** →
  [[6d — Adaptive Loop Negative Result]] exists because nothing was held out

## Testing and measurement

- 🟡 Deterministic decision logic → `tests/`; LLM-dependent checks →
  `evaluation/` (record numbers in docs, **don't assert on them**)
- 🟡 **Judge detection by the layer under test**, not end-to-end ASR
- 🟡 **Report flaky metrics as distributions** over repeated runs
- 🔴 **A statistic is a result, not arithmetic.** No p-value, interval or rate enters
  a document before the code computing it is committed and its inputs are in the
  tracked artifact. Violated once → [[A Published p-Value With No Committed Source]]
- 🔴 **Paired arms get a paired test.** Two overlapping [[Wilson Score Interval]]
  estimates are not a test when both arms ran the same cases — the **discordant**
  pairs are the evidence. Exact binomial below ~25 discordant pairs; a high p is
  **low power**, never equivalence
- 🔴 **A replayed run says so in its manifest** (`replay.fully_replayed`).
  Recomputing an old result with new code otherwise stamps it with a commit that
  never produced those outcomes
- 🔴 **A zero needs a positive control.** An instrument that cannot produce a
  non-zero has not measured anything → [[3B's Refusal Exposure Is Live and Unrealised]]

## Decisions already taken — do not re-litigate

- **`agentdojo-workspace-041` stays a known bounded false positive** →
  [[Known Bounded False Positive]]
- **The probe prompt is not to be tuned again** without a strong reason
- **3D honestly proposes a no-op. Do not tune it until it shows a gain — the
  no-op is the result** → [[The Adaptive Layer Proposes a No-Op]]
- **Two research-log volumes**; Volume I is **closed** → [[Source Documents]]

## Workflow

- 🔴 **Every session's work lands in this vault before the session ends.** Applies
  to *anything* an AI assistant does in the repo — code changed, a campaign run, a
  number moved, a decision taken, a result withdrawn. The repo is the source of
  truth for code and numbers; **this vault is the source of truth for how the
  pieces relate**, and it is only useful if it is never behind → [[Vault Map]]

  | Did | Write |
  | :--- | :--- |
  | New result, positive **or** negative | `03 Findings` note, linked from [[Findings Index]] |
  | Any session of work | dated `04 Research Log` note, linked from [[Research Log Index]] |
  | A number moved | [[Current Numbers]] — with `n`, corpus and interval |
  | Phase state changed | `05 Phases` **and** the repo's `Phase.md` |
  | New/closed open item | [[Backlog]], and the next-task note if the top priority moved |
  | New trap, rule or procedure | `07 Practice` — [[Traps]], this note, [[How to Run]] |
  | Architectural change | `02 Architecture` |

  Conventions are binding: **one idea per note**, frontmatter `tags` + `type`,
  `[[wikilinks]]` over prose references, status markers (✅ 🟡 🔴 ⛔), and every
  finding note ends with `## What this does not establish`. A withdrawn result is
  **marked, never deleted** → [[Phase 7 Benchmark Withdrawn]]
- 🔴 **This note and the repo's `Rules.md` are two views of one thing.** Change
  one, change the other in the same edit
- 🟡 **Keep the docs in sync** — root `README.md`, the relevant per-folder
  `README.md`, and where affected `Architecture.md` / `Design.md` / `Rules.md` /
  `Phase.md`
- 🟡 **Commits and pushes only when asked.** Branch off `main` first
