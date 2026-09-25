# evaluation/kaggle — Phase 6 GRPO training (local ↔ Kaggle)

This folder is the Phase 6 seam (see [Phase.md](../../Phase.md) §6): it replaces
the v1 directional heuristic inside `AdaptiveThreatModel.propose_update()` with a
**real GRPO policy-gradient loop**, trained off-machine on Kaggle, while keeping
the exact `LabeledEpisode → ProposedUpdate → apply_update` contract. Nothing
about the live pipeline changes — the trained update comes back as a
`ProposedUpdate` JSON and is applied through the same human-gated seam.

> **Correction (2026-07-26, first real run).** This folder was written around
> "training on a free Kaggle P100". That premise is false and is kept here only
> because the code still carries its name. The P100 is compute capability
> **sm_60** and the PyTorch in the Kaggle image supports **sm_70 and above**, so
> `torch.cuda.is_available()` returns True and the first allocation dies with
> `CUDA error: no kernel image is available for execution on the device`.
> `_torch_device()` now probes with a real allocation and falls back to CPU.
>
> Nothing is lost. The joint search is a few thousand float operations over a
> 188-row table and completes in **~0.27 s on CPU**; the GPU was never
> load-bearing. The reason to run on Kaggle is that it is the only environment
> available here where `torch` is importable at all, so the torch backend can be
> **executed and cross-checked** against the pure-Python one.

## Why the split exists

The local 4 GB box has no torch at all; Kaggle does. Kaggle in turn cannot host
the live pipeline (no Ollama / MCP there). So the split is about *which code can
run where*, not about compute:

```
LOCAL (this machine)                       KAGGLE (P100, training only)
────────────────────                       ────────────────────────────
run pipeline + red-team campaigns          GRPO over the labeled episodes,
  → LABELED EPISODES  ──(package)──►         same reward, emits a
apply the trained ProposedUpdate  ◄──────    ProposedUpdate (ie_threshold,
  then re-run campaigns locally               patterns, tools)
```

## Files

| File | Role | Runs where |
| :--- | :--- | :--- |
| `grpo_env.py` | Self-contained reward + **threshold→verdict replay**. Recomputes `final_status` under a candidate `ie_threshold` from recorded causal diagnostics, scores it with the exact `RewardConfig`. No project imports — bundled into the Kaggle dataset. | both |
| `package_episodes.py` | **Packager.** Labeled red-team `ExecutionResult`s → training JSONL (LabeledEpisode fields + causal diagnostics + inferred `ie_separation_consistent`). Writes `dataset-metadata.json`. | local |
| `grpo_train.py` | **GRPO trainer.** Categorical policy, group-relative advantage + REINFORCE, implemented twice (torch + pure-Python stdlib). Two action spaces: `scalar` (the `ie_threshold` grid, enumerable, decided on the exact reward table) and `joint` (default — `ie_threshold` × `risk_threshold` × `window_size` × per-marker Policy Engine weights; 5 dims, 720 actions, sampled not enumerated, decided by **propose-and-verify** plus a minimality pass). `--compare-backends` runs both implementations on identical episodes and checks they agree; it auto-enables on Kaggle, since kernels receive no CLI arguments. Emits `proposed_update.json`. | Kaggle (or local) |
| `kernel-metadata.template.json` | Kaggle **kernel** config template (GPU on, internet off, attaches the dataset). `run_kaggle.sh` fills in your username → generated `kernel/`. | Kaggle |
| `.env.example` | Template for Kaggle credentials — copy to repo-root `.env` (git-ignored). | local |
| `run_kaggle.sh` | **Path A driver.** Resolves credentials (`.env`, or a `kaggle.json` in the repo root / `~/.kaggle`), stages and pushes the dataset, **waits for it to report `ready`**, pushes the kernel, polls to a terminal state, and pulls `proposed_update.json`. Fails loudly on a kernel error or a COMPLETE-with-no-output. | local |
| `test_credentials.py` | One authenticated API call, PASS/FAIL, secret never printed. Checks key *shape* before the network call (a legacy key is 32 hex chars; the newer "API Tokens" access tokens are longer and unusable by CLI 1.7.4.5). | local |
| `apply_and_validate.py` | Loads the trained `ProposedUpdate`, applies it to a **throwaway** `ExecutionAgent` to measure effect, and re-runs the campaign BEFORE/AFTER (caught_by_causal / ASR / WCR / FPR + held-out). Its `approved=True` is a *measurement* approval, not a governance one — nothing persists. The governance path is `python -m layer5.review`. | local |

`dataset/`, `kernel/grpo_train.py`, `output/` and `proposed_update.json` are
generated artifacts (git-ignore them; the packager/scripts recreate them).

## Why the off-machine reward is exact

`grpo_env` replays `CausalAnalyzer`'s takeover verdict under a candidate
threshold. Of its three rules, only the IE rule depends on `ie_threshold`; its
sample-consistency input is threshold-invariant and captured once at packaging
time. The standalone (`masked≥2`) rule is threshold-independent, and temporal
drift **cannot fire on campaign episodes** because each case runs under a unique
`session_id` (never 3 boundaries in one session). So `takeover(T)` is exactly
reproducible from the recorded `ie`, `masked_severity`, and the inferred
`ie_separation_consistent` flag. (Details in `grpo_env.py`'s module docstring.)

## The GRPO loop (honest by construction)

The action is which IE-grid value to set `ie_threshold` to. Each step samples a
**group** of thresholds from the current policy, scores each on the full batch
with the exact reward, and uses the group mean as the baseline
(advantage = reward − group_mean — GRPO's defining move, no learned critic). A
tiny minimal-intervention penalty on `|T − current|` breaks ties toward the
smallest move. Consequences, both pinned by tests:

- **Gap exists** (Phase 5b mechanism): a diagnostic miss missed at `1.5` →
  learns `1.5 → 1.0` (the minimal move that closes it).
- **No gap** (Phase 5's natural-set finding): every threshold scores alike,
  advantages vanish, argmax stays at `current` → a **no-op** proposal, which
  `apply_update` refuses. "GRPO adds nothing when there's nothing to learn" is
  itself a valid Phase 6 result.

## Run it

### Local (no Kaggle, no torch — the whole loop is demonstrable here)
```bash
# 1. package a deterministic synthetic gap (no Ollama):
python -m evaluation.kaggle.package_episodes --self-test

# 2. GRPO over it (pure-python backend auto-selected without torch):
python -m evaluation.kaggle.grpo_train --episodes evaluation/kaggle/dataset/episodes.jsonl
#    → proposed_update.json : ie_threshold 1.5 → 1.0
```

### Real data → Kaggle P100 → apply
```bash
# 1. run the expanded campaign and package what it produced (needs Ollama):
python -m evaluation.kaggle.package_episodes --run-campaign

# 2. one manual prerequisite — credentials in a repo-root .env:
#    cp evaluation/kaggle/.env.example .env   &&   $EDITOR .env
#    (installed CLI is 1.7.4.5 → use the LEGACY username+key, NOT the new
#     "API Tokens" access token, which needs CLI >= 1.8.0 / kagglehub)

# 3. push dataset + kernel to a P100, poll, pull the trained ProposedUpdate:
bash evaluation/kaggle/run_kaggle.sh

# 4. apply it locally and validate BEFORE/AFTER (needs Ollama):
python -m evaluation.kaggle.apply_and_validate \
    --proposal evaluation/kaggle/output/proposed_update.json
```

## Tests

`tests/test_grpo_kaggle.py` (deterministic, no LLM/torch/GPU) pins the threshold
replay, the reward contract, the consistency inference, and GRPO's
gap-closing / no-op / no-literal-target (fix A) behavior.

## Status / open questions carried from Phase.md §6

- ✅ Built: env, packager, GRPO trainer (torch + pure-python), Path A scripts,
  apply-and-validate, tests (37 total pass).
- 🔲 **Credentials** — put a legacy `KAGGLE_USERNAME`/`KAGGLE_KEY` in repo-root
  `.env` (the installed CLI 1.7.4.5 can't use the new access token). The only
  thing gating a real P100 run.
- 🔲 **Natural-gap question:** run `package_episodes --run-campaign` on the
  expanded 6-family / 4-directive / held-out set. Phase 5 showed the small set
  had none; if the larger one also has none, GRPO's no-op is the answer.
- 🔲 **Learned vs heuristic:** does GRPO beat the directional heuristic? If the
  heuristic already closes every reachable gap, GRPO may match it — a valid
  finding.

---

## First real run (2026-07-26) — what it established, and the six attempts it took

The round-trip finally completed with `KernelWorkerStatus.COMPLETE`. The result
the run existed to produce:

```
  BACKEND AGREEMENT — torch vs pure-python, identical episodes
  incumbent reward agrees (<1e-9)              : True   (gap 0.000e+00)
  each backend's reported reward matches an
    independent recomputation of its choice    : True   (max gap 0.000e+00)
  accept/reject verdict agrees                 : True
  final chosen action agrees                   : True
  (policies picked the same argmax: False — different RNGs, not required)
  OK — the two implementations agree end to end.
```

**Why this mattered.** `train_torch` and `train_joint_torch` had never been
executed anywhere: there is no torch on the development box and
`tests/test_grpo_kaggle.py` is deliberately torch-free. Two implementations of
one algorithm that have never been compared are two algorithms. They now agree
to exactly zero on every quantity that must agree.

Note the last line. The two policies chose **different** argmaxes and still
reached the same final proposal — the stochastic search diverged, the
deterministic verification converged. That is propose-and-verify working, and it
is also why the policy's preference cannot be the decision rule: it is not stable
across RNGs.

**Propose-and-verify rejected the policy's own choice again** (+0.8330 incumbent
vs +0.8329 policy choice), a fourth independent occurrence, now on different
hardware. The no-op reproduced as predicted.

### The six attempts

Five real defects, each only visible once the previous was fixed:

| # | Defect | Where | Why it hid |
| :--- | :--- | :--- | :--- |
| 1 | Kernel status poll matched nothing — `case` is case-sensitive and the CLI reports `KernelWorkerStatus.ERROR` in **uppercase** against lowercase patterns | `run_kaggle.sh` | Neither branch could fire, so the loop ran all 60 iterations against a dead kernel, fell through, downloaded whatever existed, printed `done` and **exited 0**. A failed run reported as a successful one. |
| 2 | `grpo_env` import globbed `/kaggle/input/*` and `/kaggle/input/*/*`; the real mount is `/kaggle/input/datasets/<owner>/<slug>/` | `grpo_train.py` | Bare `ModuleNotFoundError` with no indication of what `/kaggle/input` contained — indistinguishable from a dataset that never attached. |
| 3 | `_find_episodes()` — identical fixed-depth bug | `grpo_train.py` | Masked by #2. |
| 4 | `torch.cuda.is_available()` returns True for the P100, which this torch cannot execute on | `grpo_train.py` | Masked by #3; and the failure lands on first *allocation*, after the trainer has already printed `backend=torch`. |
| 5 | Backend comparison compared `r_choice` across backends — the reward of *each backend's own* choice, i.e. two different actions | `grpo_train.py` | Produced a confident `FAIL` on a 6.6e-06 gap, accusing the trainer of a defect that lived in the checker. |

Two fixes are worth carrying elsewhere:

- **A remote kernel has to explain itself.** #2 and #3 were diagnosed in one
  attempt only after the import fallback was changed to walk the tree and, on
  failure, *print what is actually mounted*. Guessing the depth a third time
  would have cost another run.
- **Silence is not success.** #1 and #5 are the same species as
  `test_credentials.py` reporting PASS off `dataset_list(mine=True)`, an endpoint
  that returns an empty list instead of 401. In all three, code announced a
  verdict it had not actually tested. #1 is the most dangerous of them, because
  it converted every other failure in this table into a reported success.
