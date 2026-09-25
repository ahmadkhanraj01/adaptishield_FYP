# Claude Code prompt: benign corpus expansion + final numbers/figures for the manuscript

Copy everything between the lines into Claude Code (`--model sonnet --advisor fable`,
per your usual setup for architecture-adjacent work). Run it from the repo root.

---

I need to close the last open evidence blocker before the manuscript's numbers and
figures can be called final: the AgentDojo benign corpus is currently 60 documents,
and I need it expanded to 50+ *additional* episodes (so the reported corpus is at
least 110, or replace-and-grow to whatever AgentDojo's benign pool actually supports)
with repeated recordings, so the FPR has a Wilson interval that isn't dominated by
small-n width. This must produce the numbers and figures Sections IV-C and IV-D of
the manuscript cite, and nothing else changes.

Read these first, in this order, before touching anything:
1. `Rules.md` (especially §7, Evidence & reporting — the journal evidentiary bar)
2. `evaluation/noise_floor.py` docstring (why runs are never pooled, per-run vs
   per-case reporting)
3. `evaluation/probe_corpus.py` docstring (recorded-probe / exact-re-scoring
   contract, and what invalidates a corpus: probe prompt, `_sanitize_mediator`,
   model tag, or temperature changes)
4. `results/noise_floor/agentdojo_benign.json` — the current 60-document, 3-run
   result this work extends
5. `paper/manuscript.md` §IV-C ("Table IV... the false-positive rate of record")
   and §IV-D ("The measurement has a floor its own size") — the exact prose and
   numbers that will need updating once this lands

Then do the following, stopping and asking me before any step marked ASK:

### 1. Corpus sourcing
Check what benign episode pool AgentDojo v0.1.35 actually exposes beyond the 60
already drawn. Confirm the exact task/suite identifiers of the currently-drawn 60
(they must be in the existing `results/noise_floor/agentdojo_benign.json` cases or
a linked manifest) so the new draw is verifiably disjoint, not overlapping.

ASK before drawing: tell me the total available benign pool size, how many are
currently used, and how many *new, disjoint* episodes you can draw to reach 50+
additional. If AgentDojo does not have enough disjoint benign episodes to reach
50 new ones, tell me the real ceiling and stop for my decision rather than
padding with anything synthetic or repeated.

### 2. Recording (follow the existing convention exactly)
Use `evaluation/probe_corpus.py` with `--cohort agentdojo_benign` to record the
expanded cohort. Do not write a new recording path. Preserve the existing 60 as
part of the corpus (don't discard prior data) unless step 1's disjointness check
says otherwise.

Record the full expanded cohort **three independent times** (`--run 0`, `--run 1`,
`--run 2`), matching the existing convention, so the noise-floor methodology in
`evaluation/noise_floor.py` applies unchanged. Confirm before each run that
`verify_unchanged()` passes, i.e. that the probe prompt, `_sanitize_mediator`,
model tag (`qwen2.5:3b` / `gemma3:4b` per the Rules.md split) and temperature are
identical to the ones that produced the original 60, so the two are the same
instrument and genuinely comparable.

### 3. Scoring and intervals
Run `evaluation/noise_floor.py --cohort agentdojo_benign` on the expanded corpus.
Report, per Rules.md §7 and the existing docstring convention:
- per-run Wilson interval over the full expanded n (this is the sampling
  uncertainty about the document draw)
- run-to-run spread (min/max/range over the 3 runs) reported *separately*, never
  combined into the per-run interval
- the per-case stability classification (always / never / unstable) across all
  three runs, same as the existing `stability` field

Do not pool the three runs into a single n×3 sample. If you are about to do that,
stop — it's the exact mistake the noise_floor docstring exists to prevent.

### 4. Comparison against the current committed number
Produce a short table: old (n=60, 3 runs, current committed rate) vs new (n=110+,
3 runs). State plainly whether the interval width actually improved and by how
much, and whether the point estimate moved outside the old interval. If the new
number changes the FPR materially, say so in plain terms — don't bury it.

### 5. Figures
Check `paper/make_figures.py` first. As of now, none of its four figure functions
(`fig1_ablation`, `fig2_stratified`, `fig3_generalisation`, `fig4_flat_contrast`)
read `results/noise_floor/agentdojo_benign.json` — `fig2_stratified` reads only
`results/noise_floor/injecagent.json`. So confirm that's still true after your
changes (grep the script for `agentdojo_benign` before and after any edit), and:

- If still true: **no figure regeneration is needed.** This expansion updates
  prose numbers and Table VI's benign-FPR column only. Say so explicitly in your
  final report rather than silently skipping the step.
- If you find a reason a figure *should* now include the benign-FPR result (e.g.
  you think §IV-C/IV-D would be clearer with one), stop and propose it to me
  before writing any new figure code — don't add a fifth figure or a new panel
  unilaterally.

### 6. Manifest and reproducibility
Write a run manifest for this work following the existing convention (commit SHA,
working-tree cleanliness, model tags, corpus version, GPU state) alongside the
new result JSON, same as every other `results/phaseN/` directory. Name the output
directory sensibly (e.g. `results/phase16_benign_expansion/` or extend
`results/noise_floor/` in place — your call, but say which and why).

### 7. Manuscript numbers
Do NOT edit `paper/manuscript.md` prose yet. Instead, produce a short diff-style
note listing every number/interval in §IV-C and §IV-D that changes as a result of
this work (the FPR, its interval, Table IV, Table VI's benign FPR column, and any
prose that states "3.3% [0.9%, 11.4%]" or similar). I'll review that note and
apply the manuscript edits myself, since some of the surrounding prose (e.g. "the
measurement has a floor its own size") may need rewriting rather than just a
number swap.

Also flag, in the same note, `Rules.md` line ~110: "the 8 hand-written benign
controls and the 60 externally-authored AgentDojo benigns are separate cohorts."
The rule itself (never pool these two cohorts) does not change, only the "60"
needs updating to the final count. Propose the one-line replacement text; don't
edit Rules.md yourself.

### Constraints throughout
- No pooling across runs (Rule from noise_floor.py).
- No new benign documents from any source other than AgentDojo v0.1.35, MIT
  license, same as every other external corpus in this project (Rules.md /
  Table I of the manuscript).
- Every number must be regenerable by one committed command (Rules.md §7 / the
  paper's methodology rule 5). Don't hand me a number that only exists in your
  terminal output.
- If anything about the existing 60-document draw looks inconsistent with what
  you find in AgentDojo v0.1.35 right now (e.g. task IDs that no longer resolve,
  a version drift), stop and tell me — don't silently work around it.

When done, give me: the final n, the three per-run Wilson intervals, the
run-to-run spread, the stability breakdown, the comparison table against the old
n=60 number, confirmation of which figures were regenerated, and the manifest
path. Then wait for me before touching the manuscript.
