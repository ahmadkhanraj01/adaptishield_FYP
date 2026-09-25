# AdaptiShield — Session Handover

**Written:** 13 September 2026, end of session
**Last commit before this one:** `b046a54` on `origin/main` — eighteen commits
on 13–14 September, all pushed, all deployed, all linear
*(a handover cannot name its own SHA; check `git log --oneline -1` for the tip)*
**Read this first, then [README.md](README.md) §0 for what the research is.**

The previous handover (12 September) is superseded. Its durable decisions are
carried forward in §5; everything else it described is now in `results/`, the
manuscript, the site or the vault.

> **This file makes checkable claims.** The 12 September handover said HEAD was
> `02f4356` with nothing local, and it was six commits behind its own repo before
> anyone read it. Verify with `git log --oneline -1` before trusting the rest.

---

## 0. Research phase closed — 15 September 2026

The user declared the research complete. Nothing in §1 moved; every phase is
✅ on `Phase.md`'s board. The next work is **writing**, from a new folder:

- **`writeup/`** — eight bullet-point digests (abstract, introduction, related
  work, methodology, experiments and results, discussion, conclusion), each
  bullet carrying its number, its `results/` source, and a `[meaning …]` bracket
  in plain words, so the paper can be written in the authors' own words without
  losing a single sourced figure. Six figures copied in, Mermaid explainer
  diagrams added, and two rules files (`rules/`) for general and journal papers.
- **Fixed on the way:** the manuscript's Data and Code Availability statement
  said 494 tests in ~12 s; it now says 501 in ~8 s. The `.docx` was **not**
  rebuilt (it is byte-unstable and regenerates from the markdown on demand).
- **Still open, all administrative:** venue (🔵 parked), author block (🟡
  supervisor), the two human reads in §6, residency (🟡 procedure note).
- Vault: `04 Research Log/Entry XXVIII — The Research Is Complete.md`.

The sections below are the 13–14 September state and remain accurate.

## 1. Where the project stands

| | |
| :--- | :--- |
| **Detection** (campaign, ours) | **116/120 = 96.7%** [91.7%, 98.7%] — 4 misses, all address-free (`results/campaign/`) |
| **FPR** (AgentDojo benign, n=60) | **3.3%** [0.9%, 11.4%] — 2/60, stable across 3 recordings. n=60 is a **census**, not a sample |
| **FPR** (our 8 hand-written controls) | 4/8 — **a diagnostic, never a rate** |
| **Detection on InjecAgent** (`gemma3:4b`) | **96.7%** where the target-match path fires, **10.0%** where it cannot (median of 3) |
| **Detection on InjecAgent** (`llama3.2:3b`) | **100.0%** / **10.0%** — a **90.0-point gap**, 58/60 cases agree (Phase 16) |
| **Spotlighting** (ours) | 34.8% → 33.3% steered, McNemar *p* = 1.00 — a null |
| ✅ **Delimiting** (AgentDojo, published) | **57.69% → 41.65%** targeted ASR, non-overlapping intervals — **new today**, and the external calibration §VI lacked |
| **Lexicon generalisation** | in-sample 90.0% → holdout **43.3%** |
| **Multi-turn causal contrast** | zero on 24/30 turns; drift rule cannot fire |
| **Tests** | **501 deterministic**, ~7 s, no LLM / network / GPU |
| **Manuscript** | 16 sections, ~10,300 words, **13 tables**, 6 figures; `.docx` regenerates from markdown |
| **Site** | <https://ahmadkhanraj01.github.io/adaptishield/> — generated from the repo at every push |

## 2. What we are trying to achieve

A **journal paper** (target changed from conference on 3 Aug at the supervisor's
direction — `Rules.md` §7 is the evidentiary bar that follows). Every number
needs *n*, a Wilson interval, a named corpus and a committed command that
regenerates it.

**The one claim the whole paper reduces to:**

> The causal contrast carries discriminative signal when the injected content
> names a *liftable target* — an address or URL an action can name — and close
> to none otherwise.

Everything else is a consequence: detection collapses on external attacks because
they mostly carry no such target; the lexicon fix generalises about half because
it is nouns standing in for a mechanism; the adaptive layer proposes nothing
because the quantity it acts on is zero on most turns. **The negative results are
the contribution**, and the paper is defended on the precision of the boundary,
not on a headline accuracy.

**What "done" means:** every hardening item on `paper/handover.md` §4 closed (✅),
the manuscript current with the artifacts (✅), and a venue chosen (🔵 parked).

## 3. This session, in order

Opened as housekeeping; closed two of the three blockers.

| # | Commit | What landed |
| :--- | :--- | :--- |
| 1 | `e4a7132` | **Site nav follows the manuscript.** `90ab947` had merged the manuscript into one scrolling page and left seventeen dead nav entries uncommitted in the tree, plus `pymdownx.emoji` so status markers render. Verified with `mkdocs build --strict`. |
| 2 | `656d8b6` | **§XII says *exhausted*, not "adequate but wide".** "Adequate but wide" describes a sample, and a sample invites a deeper draw that does not exist. Now states the census, why the routes to n=110 are off-domain and would *lower* FPR for reasons unrelated to the defence, and that width comes from a rate near zero. The old concession survives verbatim. |
| 3 | `1215701`, `e81a3a6` | **Entry XXVII** in the vault, later extended to cover the session it turned into. |
| 4 | `db9a745` | 🔴 **The venv could not build the paper.** See §4 — the one with consequences beyond today. |
| 5 | `4f7d71d` | **AgentDojo's Delimiting row staged** held-back, so two rows waited on one human read of one table. |
| 6 | `5f4d787` | ✅ **Table 5 read by a human. Both rows `verbatim`.** Held-back test deleted (501). **§VI-D is new**; Tables VI–XII renumbered VII–XIII. |
| 7 | `39d76ae` | **This handover, rewritten**, and the home page gains the published attack-success figures — generated from `external_numbers.json`, `verbatim` as the gate, detector FPR rows deliberately excluded. |
| 8 | `4398fe3` | ✅ **Pipeline verified under `langchain-core` 1.6.3** — nothing broken. The demo had been hiding Test 2's verdict and doubling Test 3's; fixed. See §4. |
| 9 | `cf5ae66` | 🟡 **`The Model of Record Is 40% Resident`** — the finding, the vault entry, and the handover's model table corrected. |
| 10 | `fb36b6c` | ✅ **Site audited against `results/`.** Every generated number traces correctly; one hand-written label did not carry its scope. See §7. |
| 11 | `e099104` | The audit lands in the vault, with the trap that generalises. |
| 12 | `3023af2` | ✅ **`./venv` declared the runtime of record** in all three documents. The README's package list is flagged as a historical snapshot — it says `langchain==0.3.7`; the venv has 1.4.0. |
| 13 | `f91f0a4` | The declaration lands in the vault. |
| 14 | `e28a75b` | ✅ **The docs stop describing done work as pending.** `Phase.md` 14a/15 closed, Phase 16 added to the board, 501 everywhere. `gemma2:9b` removed from two files — never installed. The README's "`llama3.2:3b` rejected" corrected: it is the paper's second probe model. |
| 15 | `e140331`, `b046a54` | ✅ **Five unbuilt boxes removed from the implementation diagram** and the figure re-exported. Appendix A's caption and README's ASCII stack moved with them. |

## 4. Findings worth carrying

- 🔴 **A pin that lives only in prose pins nothing** (`07 Practice/Traps.md`).
  `Rules.md` §1 said `numpy==1.26.4` and named `requirements.txt` as the source of
  truth; `requirements.txt` said `numpy`. So `./venv` — what the README tells you
  to activate — had **no numpy at all** and could not regenerate a single figure or
  run the pipeline, while the interpreter that produced the figures ran **2.2.6**,
  the version §1 forbids. Nothing failed: the tests import no numpy. Now pinned and
  installed (89 packages, `pip check` clean). **All four figures regenerate
  byte-identical under the pin**, so the wrong numpy never moved one.
- ✅ **AgentDojo Table 5, released.** No defense 57.69% (±3.9), Delimiting 41.65%
  (±3.9). Delimiting is the only published prompt-level result carrying its own
  undefended row, so it is a *difference* rather than a level — which is why §VI-D
  uses it against our null. It also leaves 41.65% succeeding: the family reduces
  the exposure, it does not remove it. The superseded 45.8% is kept as
  `correction_note` (wrong by twelve points, and from Table 2).
- 🟡 **`The Model of Record Is 40% Resident`.** `/api/ps` says `gemma3:4b` holds
  1.71 GB of a 4.30 GB footprint in VRAM — **60% on CPU**, on a card with nothing
  else on it, and worse offload than the `qwen2.5:7b` this project disqualified for
  exactly that. Four runs of the pipeline: the **three warm runs are identical**,
  the **cold one differs** in a scored severity (DE moves by a point). Verdicts
  identical in all four, and no committed number is restated. But every previous
  non-determinism result here compared *warm* repeats, and the corpus contract pins
  prompt, sanitiser, model tag and temperature — **never residency**. Cheap fix
  suggested in the note: record `size_vram / size` in the manifest, warm the model
  before case 0. Neither is done.
- **`AgentDojo's Benign Pool Is Exhausted at 60`** — a census. The limitation
  relocates to *a second external benign corpus is needed*. §XII now says so.
- **`The Probe's Compliance Does Not Transfer`** — title corrected the same day,
  kept under its wrong name with a dated section, per vault convention.
- **`Phase 16 — The Stratification Survives a Second Model`** — the collapse is the
  mechanism's, not the model's. Scoped: one recording per model, nothing above ~4B.

## 5. Decisions taken — don't re-litigate

**Today:**
- **A human must read a primary source before a number is `verbatim`.** Asked to
  do the Table 5 read myself, the answer was no twice, for the reason the guard
  exists: an automated transcription is an intermediary, and this is the row that
  was already wrong by twelve points. Staging a row `located-pending-human-read`
  is the most an assistant may do.
- **`installed.txt` is evidence, not a lockfile.** ⛔ Never `pip freeze > installed.txt`.
- **External numbers live in `Published Numbers We Position Against`**, not
  `Current Numbers` — the latter is ours.
- 🔵 **Kaggle stays in the implementation diagram** (decided 14 Sep, asked and
  answered). It is **not** in the same category as the five unbuilt boxes removed
  the same day: Phase 6's GRPO training executed there, the torch backend agreed
  with pure-Python to **exactly zero**, and `evaluation/kaggle/` is committed code
  with a dataset and a `proposed_update.json`. What was retired is the **GPU
  premise** — P100 is sm_60 against a torch needing sm_70+, so training fell back
  to CPU at 0.27 s for the whole workload — not the environment. The panel
  documents a **negative result**, which this project reports rather than hides.
- **Entry XXVII keeps its now-partial title**, dated in place rather than renamed.

**Carried forward (still true):**
- **n = 60 for the benign cohort.** Not expanded; the reason is a finding.
- **`results/campaign/` is a replay and says so.** Do not backfill `models_at_run`.
- **The 7B model is not a candidate on this hardware**, and Kaggle cannot host Ollama.
- **Commits carry the user's name only.** No Claude co-author or session trailers.
- `agentdojo-workspace-041` stays a known bounded false positive.
- The probe prompt is not to be tuned again without a strong reason — three
  attempts cost 8 detections.
- 3D honestly proposes a no-op; the no-op is the result.
- Two research-log volumes: `researchworksofar.md` (I–XIV, **closed**),
  `research_work_so_far.md` (XV onward). Vault `04 Research Log` runs to **XXVII**.
- 🔴 Every session's work lands in the vault before the session ends (`Rules.md` §8).
- Do not "restore" the Phase 7 exfil destinations — a test fails if you do.
- **Venue decision parked** at the user's request. Do not raise it unprompted.

## 6. Open items

| | Item | Needs |
| :--- | :--- | :--- |
| 🔵 | **Venue** — parked | the user + supervisor. `paper/supervisor-brief.md` and the 34-slide deck are ready to send |
| 🟡 | **Author block `CONFIRM` bracket** — ORCIDs, IEEE grades, author order, funding | the supervisor |
| 🟡 | **Residency is unpinned.** `gemma3:4b` is 40% resident and a cold first call differs from warm ones. No manifest records residency; no recording warms the model first | a decision, then a small change to the run procedure |
| — | ~~Declare the runtime of record~~ — ✅ **done 13 Sep.** `./venv` is the runtime of record in `Rules.md` §1, its vault twin, and `README.md` §8. System `python3` is explicitly not it | — |
| 🟡 | **Tool filter: 6.84% is named but not citable.** The discrepancy is checked and reported (14 Sep) — prose 7.5% against Table 5's 6.84% (±2.0), not a model, metric or aggregation difference. The row keeps 7.5%; 6.84% was **not** promoted to a `verbatim` row off an automated fetch | a human reading both, then re-scope the row or add a Table 5 row |
| — | ~~Read the published site against `results/`~~ — ✅ done 13 Sep. 10 tiles, 80 percentages, 13 captions, 6 assets, 6 links all trace. One labelling defect found and fixed | — |
| 🟡 | §XI's positioning table now renders five AgentDojo rows; check it still reads as calibration rather than a scoreboard | a prose read |

## 7. Traps found today (`Research/07 Practice/Traps.md`)

- **A pin that lives only in prose pins nothing** — §4 above. The general guard:
  a rule naming a version belongs in the file that installs it, in the same edit;
  and when you repair an environment claim, regenerate the artifacts and diff them.
- **Inserting a table renumbers the paper.** Tables VI–XII became VII–XIII for
  §VI-D. Only one reference lives in prose (§VIII's bound on the holdout table);
  the rest are captions. Grep `Table [IVX]` before and after, every time.
- **Generating a number guarantees it is correct, not that it is scoped.** The
  site pulls every figure from a tracked artifact, and that caught nothing wrong —
  but two tiles rendered `phase16_model_transfer`'s **run 0** numbers with no
  "run 0" on them, beside a paper whose headline for the same stratum is the
  *median of three* from a different artifact. When a manifest constrains how its
  numbers may be quoted, that constraint is part of the number.
- **Regenerated artifacts churn on timestamps.** The four figure PDFs differ by
  exactly 8 bytes inside `/CreationDate`, and the `.docx` is byte-unstable too.
  Revert them rather than commit a diff that implies a figure changed.

## 8. Orientation

| Question | File |
| :--- | :--- |
| What is this research? | `README.md` §0 |
| The paper | `paper/manuscript.md` (edit this; the `.docx` regenerates) |
| Paper status and hardening list | `paper/handover.md` §4–§5 |
| What to send the supervisor | `paper/supervisor-brief.md` + `paper/AdaptiShield-Full-Review.pptx` |
| Why a decision was made | vault `04 Research Log` (through XXVII), `03 Findings` |
| Numbers we quote from other people | vault `01 Foundations/Literature/Published Numbers We Position Against.md` |
| Every quotable number of ours | `results/<phase>/` with its manifest; `results/README.md` is the index |
| Rules that must hold | `Rules.md` — §7 for evidence, §8 for the vault ritual |

**Health check:**

```bash
source venv/bin/activate
python3 -m pytest tests/ -q                       # expect 501 passed, ~7 s
python3 -m evaluation.campaign_report             # 116/120, 2/60, 4/8 — no model calls
python3 -m evaluation.model_transfer              # 96.7/13.3 vs 100.0/10.0 — no model calls
python3 paper/make_positioning_table.py           # nothing held back any more
python3 paper/make_figures.py                     # PNGs must come back byte-identical
python3 adaptishield_pipeline.py                  # 3 cases: approved_direct / safe_continuation / approved_causal
curl -s localhost:11434/api/ps                    # size_vram/size is the residency — currently 40% for gemma3:4b
```

**Models on this machine:** `gemma3:4b` (3B of record — ⚠️ **40% GPU-resident**,
measured 13 Sep, not the "fully resident" earlier handovers claimed),
`qwen2.5:3b` (3C/L3/planner — *not* usable as 3B), `llama3.2:3b` (Phase 16
candidate), `qwen2.5:7b` (does not fit — 53% resident, non-deterministic).
**Residency is not recorded by any manifest.** Read it with
`curl -s localhost:11434/api/ps` before trusting a repeat.

---

*Handover written 13 September 2026, extended 14 September, on top of `b046a54`.
Nothing local except a superseded `…drawio old.png`, deliberately untracked.*
