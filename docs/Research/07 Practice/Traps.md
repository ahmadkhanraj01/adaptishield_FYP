---
tags: [adaptishield, rule]
type: reference
---

# Traps

**Things that have already cost time.** Every one of these produced a wrong number
or a wasted campaign at least once.

| Trap | What happens | Guard |
| :--- | :--- | :--- |
| **Stale dataset** | A campaign that dies part-way leaves the old `episodes.jsonl`; `fpr_report` prints **pre-fix numbers as if current** | It now prints the dataset age and shouts **`STALE`**. **Read that header.** |
| **Stale checkpoint** | Cached per-case results describe the **old** pipeline | `rm -rf logs/campaign_checkpoint` **and** `logs/benchmark_checkpoint` after **any** pipeline change |
| **A subsample that omits the hard cases** | The benchmark's external benign cohort is a stride subsample (indices 0, 6, …, 54) that **excludes campaign documents 41 and 55 — both known false positives**. Its 0/30 reads as an improvement on 3.3% and is not | The report prints the caveat itself. [[FPR]] of record comes from `fpr_report` at n=60 → [[Current Numbers]] |
| **Idle Ollama reads as "no GPU"** | `/api/ps` lists only *resident* models, so checking before a run reports no GPU on every clean start | The run manifest samples Ollama **after** the arms run |
| **Ollama falls back to CPU** | After a CUDA fault it silently runs CPU-only: ~11 GB RAM, slower, more non-determinism, and **different outputs** | `curl -s localhost:11434/api/ps` → **`size_vram` must be > 0**. If 0: `sudo systemctl restart ollama` |
| **Two variables at once** | A campaign changing code **and** backend cannot attribute a regression | **Change one thing per campaign** |
| **Kaggle credentials** | Needs a **legacy 32-hex key** (Settings → API → *Create New Token*). The newer "API Tokens" page issues a longer token CLI 1.7.4.5 cannot use — and 1.7.4.5 is the newest on PyPI | `python3 evaluation/kaggle/test_credentials.py` |
| **`kaggle.json`** | Holds a live key in **plaintext in the repo root** | Already git-ignored — **keep it that way**. `origin` is now a **public** repo |
| **A defense's own output inflating the metric** | Spotlighting's instruction induces refusals *naming* the attacker address, and the keyword scorer escalates on any target mention. It reported the defense as **17 points worse** when it was neutral | `score_agent_action` scopes negation to the clause naming the target → [[The Scorer Cannot See Negation]] |
| **A zero with no positive control** | A broken parser, an empty join, or a predicate that never fires all print the same reassuring zero | `refusal_audit` synthesises the case it is hunting against a real mediator and **withholds the result** if the control fails → [[3B's Refusal Exposure Is Live and Unrealised]] |
| **Auditing only the malicious half** | The attacks are where a detection defect costs a miss; the **benign** cohort is where it costs a false positive — the expensive direction | Join `all_vectors()`, never `VECTORS`. Pinned by a test |

## The one that nearly cost a conclusion

The CPU-fallback and one-variable traps fired **together** in
[[6p — Probe Hallucination Fixed at the Scorer]]: a campaign testing a prompt
change also happened to run on CPU, so the observed regression could not be
attributed. Restoring the GPU and reverting **only** the prompt isolated it — the
prompt was the cause. Without that isolation the wrong component would have been
blamed.

## Campaigns are resumable

They checkpoint **per case** to `logs/campaign_checkpoint/`, so a crash costs the
case in flight, **not 1.5 hours**. This absorbed three interruptions on 26 July.
Just re-run the same command.

## The one that has not fired yet

Every other trap on this page has already cost something. This one is **latent**,
recorded before it fires rather than after, which is the only entry here written
in that order.

**AgentDojo benign case IDs are positional.** `attack_generator` builds them as
`f"agentdojo-{item['suite']}-{i:03d}"`, where `i` is the index into the vendored
items list — not a property of the document. The list is built suite by suite, so
it currently runs `workspace-000` … `-055`, then `slack-056` … `-059`.

**What happens if anyone re-vendors with a wider filter.** Adding a single
`workspace` item shifts every later `workspace` index by one and pushes the whole
`slack` block off 056–059. Nothing errors. The corpus re-records cleanly, the
noise-floor matrix rebuilds, and `workspace-041`, `-048` and `-055` quietly come
to mean **different documents** — the three cited by name in the manuscript's
§IV-D, in the README, in [[Known Bounded False Positive]], and in
[[The Benign FPR Has a Noise Floor Its Own Size]]'s per-case breakdown. The
per-case stability claim would then be comparing two different sets of documents
under one set of labels, and every guard in this project is a guard against wrong
*numbers* — none of them checks that a label still names what it named before.

**Guard.** Re-key `case_id` to a content hash of `item["text"]` **before** any
re-vendoring, not after, and keep a committed map from the old positional IDs to
the new ones so the three cited documents stay traceable. `verify_unchanged()`
does not cover this: it pins the probe prompt, `_sanitize_mediator`, the model tag
and the temperature — the *instrument* — and this is a change to the *corpus
index*, which it was never built to see.

Found while counting the pool for
[[AgentDojo's Benign Pool Is Exhausted at 60]]; not triggered, because the
expansion it would have fired on was not run.

## A pin that lives only in prose pins nothing

*13 Sep 2026 → [[Entry XXVII — The Prose Catches Up With the Finding]]*

`Rules.md` §1 says `numpy==1.26.4` **and** names `requirements.txt` as the source
of truth. `requirements.txt` said `numpy`. Two documents agreeing that a pin
exists, and no file anywhere that applies it — so the environment the README tells
you to activate had no numpy at all, while the interpreter actually producing the
figures had **2.2.6**, the version §1 forbids on 3.10.12.

Nothing failed. The 502 tests import no numpy, so they passed in the venv; the
figures were generated from the other interpreter, so they existed and looked
right. The split was only visible by asking each interpreter what it could import.

**Guard.** A rule that names a version belongs in the file that installs it, in
the same edit — §8's "change one, change the other" applies to `requirements.txt`
as much as to the two rule documents. And when an environment claim is repaired,
regenerate the artifacts and diff them: all four figures came back byte-identical
under the pin, which is the only thing that could retire the question of whether
the wrong numpy had ever moved one.

⛔ **`installed.txt` is evidence, not a lockfile.** It records the *drift*. Running
`pip freeze > installed.txt` to "fix" it destroys the only record of how the two
interpreters diverged.

## Generating a number guarantees it is correct, not that it is scoped

*13 Sep 2026 → [[Entry XXVII — The Prose Catches Up With the Finding]]*

The site generates every number from a tracked artifact, which is the guard
against the review deck's failure — a hand-typed number drifting from the repo.
It worked: 10 tiles, 80 manuscript percentages, 48 progress figures, all exact.

It cannot guard the **label**. Two tiles read *96.7% vs 13.3%* from
`phase16_model_transfer`, which is one recording per model — its manifest says so
and says no spread may be quoted from it. The paper's headline for the same
stratum is **10.0%**, the median of three recordings in a *different* artifact.
Both correct; nothing on the page said which was which, so the site appeared to
contradict the paper.

**Guard.** When an artifact's manifest constrains how its numbers may be quoted —
*one recording*, *run 0 only*, *strata must not be pooled*, *this is a replay* —
that constraint is part of the number and has to travel with it into every
rendering. A value pulled from JSON arrives without its caveat; the caveat is in
prose a human wrote once, in a file nobody re-reads. Prefer putting the scope in
the artifact's own field so the generator can render it, rather than in a label
beside the call site.

⚠️ **The corollary for audits.** Checking that every displayed number matches its
source will pass while this defect is present. The check that catches it is
holding two renderings of the *same quantity* side by side and asking whether a
reader could tell them apart.

## The general form

Most of these are instances of [[Instruments Fail More Than Mechanisms]] — a tool
that reads whatever is present and reports a verdict it did not test.
