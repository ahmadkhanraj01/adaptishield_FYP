# Handoff — per-epoch training metrics + trained classifier baseline

Orientation for whoever picks this up: what exists, how to run it, what the
numbers say, and **which numbers must never be quoted without their caveat**.

- **Status:** committed on `feature/trained-baseline-and-epoch-metrics`
  (`5ad53d9`), **538 tests passing**, PR not yet opened.
- **The ask:** the supervisor wanted the classic supervised-learning table —
  precision, recall, F1, support, accuracy *per epoch* — for a model we
  actually train. Two routes were built, A and B, because GRPO's "training"
  and a real trained model are different claims.

---

## TL;DR

```bash
python3 -m pytest tests/ -q                 # 538 pass, ~10 s, no Ollama/GPU
python3 -m evaluation.kaggle.grpo_train \
    --episodes evaluation/kaggle/dataset/episodes.jsonl   # Route A table
python3 -m evaluation.train_classifier                     # Route B table
```

| Route | What trains | Table | The honest sentence |
|---|---|---|---|
| **A** GRPO trainer | policy over a 720-action joint grid | `evaluation/kaggle/epoch_metrics.csv` (90 rows: 30 checkpoints × train/holdout) | Curves are **flat** — Phase 5/6 found no reachable threshold gap, so propose-and-verify rejects a no-op. Flat is the correct result, not a bug |
| **B** text classifier | TF-IDF + logistic regression (numpy) | `results/classifier/epoch_metrics.csv` + `epoch_metrics_confound_controlled.csv` (60 rows each: 30 epochs × train/val) | Curves rise to 1.000 — but the *cross-corpus* 1.000 is source recognition. Quote the **confound-controlled** one |

---

## 1. Route A — per-epoch metrics inside the GRPO trainer

- **"Epoch" = a checkpoint**, every `--metrics-every` steps (default 10,
  Kaggle-safe), because GRPO scores every step on the full batch — a data pass
  is not a meaningful unit here. Documented at `evaluation/kaggle/grpo_train.py:624`.
- Columns: `epoch, step, split, n, support_attack, support_benign, tp, fp, fn,
  tn, precision, recall, f1, accuracy, action` — the `action` column is the
  policy's joint action at that checkpoint, so each row can be tied back to a
  concrete configuration.
- Splits are the **address-level holdout**: `HOLDOUT_TARGET_ADDRESSES`
  (`leaker@shadow-mail.net`, `siphon@nullroute.org`) inlined because the Kaggle
  bundle cannot import `red_team`; a test pins it to `attack_library.holdout_targets()`.
- The recorder is wired through an **observational `on_step` hook** in all four
  trainers (`train_torch`, `train_pure`, `train_joint_pure`, `train_joint_torch`).
  `test_epoch_metrics_hook_does_not_change_the_proposal` proves the chosen
  action is identical with and without it.
- Last checkpoint per split is copied into `proposed_update.json` under
  `joint.epoch_metrics` (`{file, checkpoints, every_steps, final{train,holdout}}`).

**Measured result** (188 episodes, torch/cuda, 30 checkpoints):

| split | n | support | first checkpoint (step 10) | last (step 300) |
|---|---|---|---|---|
| train | 140 | 72 attack / 68 benign | P 0.919 · R 0.944 · F1 0.931 · acc 0.929 | identical |
| holdout | 48 | 48 attack / **0 benign** | 1.000 across the board | identical |

> ⚠️ **Do not quote holdout precision.** That split is attack-only, so FP is
> structurally 0 and precision is trivially 1.0 — it is a *recall* split. The
> false-alarm estimate lives in `evaluation/fpr_report.py` (Wilson, per cohort).

Also from that run: `risk_threshold` and `window_size` are **unidentifiable**
(reward exactly flat — campaigns use a unique `session_id` per case, so the
temporal-drift rule never fires), and propose-and-verify **rejected the policy
choice as a no-op** (+0.8436 vs +0.8436).

---

## 2. Route B — the trained text-classifier baseline

`baselines/text_classifier.py` (model) + `evaluation/train_classifier.py`
(driver). **A comparison baseline, not the defense** — consistent with
`FYP/Supervisor_Feedback.md:70`: a classifier judges *wording*, so rewording
moves it; the causal gate judges the *action*.

- Corpus: 510 InjecAgent injections vs 68 benign (AgentDojo 60 + our 8 controls).
  Stratified, seeded (seed 0), disjoint split — 406/86/86; vectorizer fitted on
  **train only**; epochs 30, `min_df` 2, balanced class weights.
- Reports: per-epoch train+val P/R/F1/macro-F1/accuracy, per-attack-type recall,
  per-source benign FPR (never pooled), rephrasing probe, optional matplotlib
  curve.
- The AgentDojo **attack** holdout (`red_team/data/agentdojo_attacks.json`, 253
  records, frozen at `46cfbfb`) is read **only** behind `--agentdojo-holdout`,
  which prints that it is spent for looking and never for tuning. **Not spent.**

**Cross-corpus test set (n = 86: 76 attacks / 10 benign)** — all 1.000:
detection 76/76 [0.952, 1.000]; false alarms 0/10 [0.000, 0.278]; recall by
type 1.000 for Data Security Harm (27), Financial Harm (23), Physical Harm (26);
benign FPR `agentdojo_benign` 0/9 [0.00, 0.30], `ours_benign` 0/1 [0.00, 0.79].

**Confound-controlled cohort (the one to quote)** — InjecAgent vs its own
**de-injected twins**: each original with its `attacker_instruction` span
deleted (510 pairs, 0 dropped; split by *pair* so an original never sits beside
its own copy — 358/76/76). Twin test n = 152 (76/76), all 1.000. A twin is its
original minus the imperative, so the only features left that separate the
classes **are the injection's own words** — this 1.000 means detection, not
source.

**Rephrasing probe** (same attacks, rewritten; `kept` = share of clean tokens
surviving):

| row | cross-corpus recall (kept) | twin recall (kept) |
|---|---|---|
| clean | 1.000 (1.000) | 1.000 (1.000) |
| paraphrase — hand-built synonym rewrite | 1.000 (0.869) → **+0.000** | 0.921 (0.886) → **−0.079** |
| datamarking | 1.000 (1.000) | 1.000 (1.000) |
| delimiting | 1.000 (1.000) | 1.000 (1.000) |
| encoding | 1.000 (0.000) | 1.000 (0.000) |
| **empty-input control** | 1.000 (0.000) | 1.000 (0.000) |

Read it as: the first table never looks at the words (reword 13% of them and
nothing moves → source recognition); the twin model does, and rewording costs it
0.079; spotlighting's character transforms cost **0.000** because a
character-class tokenizer re-derives every token — they change the surface a
*reader* sees, not the words this model sees; and `encoding` scoring like an
empty input is the **intercept** (`b = +0.096 > 0`, so content-free input
defaults to "attack"), not a detection.

---

## 3. Findings that changed the code — read before quoting anything

1. **Three test failures were my hand-arithmetic, not the code.**
   `support_attack = tp+fn`, `support_benign = tn+fp`; the classifier test's
   vectors counted (2,1,2,5); `macro_f1 = 0.5` on an all-benign-correct
   `[0,0]/[0,0]` (which is exactly why macro-F1 must not be quoted when a class
   is absent). All corrected with exact fractions in the assertions.
2. **The twin cohort had its own label leak.** Deleting the instruction left
   `''` behind, and the tokenizer kept apostrophes — so `''` was the strongest
   feature in the model (**−1.07**): it had learned *how the twins were built*.
   Fixed by a punctuation-blind tokenizer (`[a-z0-9]+`), with the reasoning in
   `baselines/text_classifier.py` and recorded in the manifest. Chosen from
   train/val inspection; **the frozen attack holdout was never read to make the
   choice.**
3. **The probe's prose contradicted its own table** — a sentence claiming
   rewording moves the model printed directly above a table showing `0.000`,
   twice. Fixed by `print_probe_verdict()`, which recomputes every printed
   number from the rows above it, pinned by
   `test_probe_verdict_prints_the_numbers_it_was_given`.
4. **`encoding = 1.000` was the intercept, not detection** (zero features left,
   positive bias). Fixed by the empty-input control row.

---

## 4. How to run / regenerate

| Command | Output | Cost |
|---|---|---|
| `python3 -m pytest tests/ -q` | 538 pass | ~10 s, no LLM/network/GPU |
| `python3 -m evaluation.train_classifier` | `results/classifier/*` (5 files) | <1 min CPU |
| `python3 -m evaluation.train_classifier --epochs 40 --seed 1` | same, varied | idem |
| `python3 -m evaluation.train_classifier --agentdojo-holdout` | spends the holdout — **requires a decision, not a routine flag** | idem |
| `python3 -m evaluation.kaggle.grpo_train --episodes evaluation/kaggle/dataset/episodes.jsonl` | `evaluation/kaggle/epoch_metrics.csv` + `proposed_update.json` | ~1 min (torch/cuda if present) |
| `python3 -m baselines.text_classifier` | tiny self-test on synthetic data | instant |

`evaluation/kaggle/epoch_metrics.csv` is **gitignored** (regenerated); the
`results/classifier/` artifacts are **committed** with their manifest.

> The committed `manifest.json` stamps `commit 44adf79, dirty: true` because it
> records HEAD *at run time* — the work was committed afterwards as `5ad53d9`.
> Re-running the driver after the merge will stamp the real commit.

---

## 5. Tests

`python3 -m pytest tests/ -q` → **538 passed** (478 pre-existing + 33 in
`tests/test_grpo_kaggle.py` + 27 in `tests/test_text_classifier.py`).

New coverage worth knowing about:

- confusion matrix agrees with the reward's own catch predicate; the two
  `classification_metrics` copies (`grpo_env` vs `text_classifier`) agree on the
  same matrix (they must — two copies of one formula is how drift starts);
- the epoch hook is **observational** (same chosen action with and without);
- address split pinned to `attack_library`; the holdout file is not opened on
  the default code path (a `builtins.open` spy);
- the twin corpus really removes the injection (a twin still carrying it is a
  label error) and its pair-split keeps originals beside their twins;
- tokenizer is punctuation-blind; `paraphrase` substitutes rather than deletes;
  the probe reports all six rows with token-retention;
- the printed verdict is derived from the rows it prints.

---

## 6. File map

| File | Role |
|---|---|
| `evaluation/kaggle/grpo_train.py` | Route A: `HOLDOUT_TARGET_ADDRESSES`, `episode_split`, `epoch_metrics`, `_epoch_recorder`, `write_epoch_metrics`, `print_epoch_summary`, `on_step` hooks, `--metrics-every` |
| `evaluation/kaggle/grpo_env.py` | `confusion_counts` / `classification_metrics` (stdlib-only) |
| `baselines/text_classifier.py` | `TfidfVectorizer`, `LogisticClassifier` (balanced weights, `eval_set` → per-epoch rows), `classification_metrics`, punctuation-blind `tokenize` |
| `evaluation/train_classifier.py` | Driver: loaders, `load_injecagent_twin_corpus`, `split_pairs`, `twin_docs`, `REPHRASE_MAP`/`paraphrase`, `rephrasing_probe`, `print_probe_verdict`, report + manifest writers |
| `tests/test_grpo_kaggle.py` | 33 tests (10 new) |
| `tests/test_text_classifier.py` | 27 tests, new file |
| `results/classifier/` | Committed artifacts: 2 metric CSVs, report JSON, manifest JSON, curve PNG |
| Docs updated | `README.md`, `Architecture.md`, `evaluation/README.md`, `evaluation/kaggle/README.md`, `results/README.md`, `tests/README.md`, `.gitignore` |

---

## 7. Rules compliance (docs/Rules.md)

- **§6** — every rate carries `n` + Wilson interval; recall reported per attack
  type; the two benign cohorts never pooled; cross-corpus vs twin results
  reported as separate tables, never blended; corpus–label confound stated in
  the report itself, not left for a reader to find.
- **Holdout** — `agentdojo_attacks.json` unopened by default, guarded by a test;
  scoring it is opt-in and announces that it is spent for looking.
- **§8** — branch + PR, never straight to `main`.
- **§159** — never describe the GRPO policy as "trained"; "epoch" is defined as
  a checkpoint and labelled as such.

---

## 8. Git state & next actions

```
branch: feature/trained-baseline-and-epoch-metrics   commit 5ad53d9
main:   44adf79 (Add frontend design…)
```

Committed: 15 files (code, tests, docs, `results/classifier/`).
Deliberately **left uncommitted in the working tree — yours, not mine**:
`FYP/*.pptx`, `FYP/ppt skills/`, the `.drawio` move to `docs/`.

Next:

```bash
git push -u origin feature/trained-baseline-and-epoch-metrics
gh pr create --title "Add per-epoch metrics to the GRPO trainer and a trained classifier baseline" \
  --body "Supervisor's supervised-learning table: per-epoch P/R/F1/support/accuracy for both the GRPO trainer and a trained TF-IDF + logistic-regression baseline. 538 tests pass."
```

---

## 9. Known limitations & open decisions

1. **Twin negatives are synthetic** (instruction span deleted). Deletion is
   span-level and verbatim (0 of 510 dropped), but a future reader should know
   the twins are constructed, not naturally benign documents.
2. **The paraphrase map is hand-built and partial** (~13% of tokens touched) —
   read `−0.079` as a **lower bound** on a real rephraser. An LLM paraphrase
   probe would be the stronger test and needs an offline/deterministic plan to
   stay inside the test rules.
3. **Encoding/empty-input rows are the intercept.** If `b` ever flips negative,
   those rows flip too — the control row is what keeps them honest.
4. **GRPO's holdout split is attack-only** (see §1) — precision there is
   decorative; do not report it.
5. **Spending the attack holdout** (`--agentdojo-holdout`) is a one-way door.
   Decide with the supervisor, run once, record the number with its `n` +
   Wilson, and never tune after seeing it.
6. **`risk_threshold` / `window_size` are unidentifiable on this data** (flat
   reward) — if anyone wants those learned, the campaign needs a reused
   `session_id` so the temporal-drift rule can fire; that is a data change, not
   a trainer change.
