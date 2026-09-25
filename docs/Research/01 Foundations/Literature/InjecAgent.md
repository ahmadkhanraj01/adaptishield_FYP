---
tags: [adaptishield, literature]
type: literature
---

# InjecAgent

A published benchmark for **indirect prompt injection in tool-integrated LLM
agents**, MIT-licensed, from UIUC. Vendored by `red_team/vendor_injecagent.py` into
`red_team/data/injecagent_dh.json`.

> Zhan, Liang, Ying & Kang. *InjecAgent: Benchmarking Indirect Prompt Injections in
> Tool-Integrated Large Language Model Agents.* Findings of ACL 2024.
> https://github.com/uiuc-kang-lab/InjecAgent

## Why it is the right second corpus

[[AgentDojo]] fixed the **benign** side, and [[6n — A Corpus That Can Fail]]'s
lesson — *a defense measured only against a corpus its author wrote measures the
author's imagination* — was left half-applied, because the **attack** side had no
equivalent import. Every malicious case measured before this one was written here.

It also fits **without approximation**: InjecAgent delivers its injection inside a
**tool response** — an attacker instruction embedded in a product review, a calendar
entry, a repository description — which is the one boundary this pipeline models
end to end. That is a better fit than our own V5 and V6, which are approximated
because the pipeline consumes tool responses rather than manifests.

## The mapping

| InjecAgent | Ours |
| :--- | :--- |
| User Instruction | `user_input` (trusted) |
| Tool Response | `mediator` (untrusted, carries the injection) |
| Attacker Tools + Instruction | `proposed_action` — **their** ground truth, not ours |

Writing the harmful action ourselves would put back the imagination this import
exists to remove.

## What was taken

**Taken:** `test_cases_dh_base.json` — the **direct-harm** split, 510 cases, a
complete 17 × 30 cross of user instructions against attacker instructions.

**Not taken, and why:**

- The **data-stealing** split. Its harm is a two-step exfiltration and this pipeline
  models one boundary, so those cases would fail for a structural reason rather than
  a detection one.
- Both **`enhanced`** splits. They prepend a hand-written *"IMPORTANT!!!"* hijack
  prompt, which makes them **easier** — and a harder-looking corpus that is
  actually easier is worse than no corpus.

## The property that produced the finding

**Only 51 of 510 cases — 10% — give 3B its sharpest signal**, a target lifted out of
the mediator and named in the proposed action. The other 90% are address-free by
nature: *"grant permanent access to guest_amy01"* names nothing to match.

That is why [[Phase 12 — Detection Is 18% on Someone Else's Attacks]] reports the
two strata separately and never pools them, and why the stratum is computed by
`_references_mediator_target` itself rather than by a regex resembling it — the
first attempt counted addresses anywhere in the response and mislabelled **135 of
186** cases.

## Handling

The vendored file contains **attacker-authored instructions by construction**, like
the rest of `red_team/data/`. The repository is public; the licence and citation are
recorded in the payload itself, not only here.

Used by: [[Phase 12 — Detection Is 18% on Someone Else's Attacks]],
[[Evaluation Corpus]], [[Address-Free Attacks]].
