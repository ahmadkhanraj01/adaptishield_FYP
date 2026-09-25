---
tags: [adaptishield, log, entry]
type: log-entry
date: 2026-09-12
---

# Entry XXV — The Number That Could Not Be Checked

*12 September 2026, later.*

The handover's hardening pass has three items and I took the second, because it
was the only one reachable in the time left before the submission date: build
`results/campaign/` so the paper's in-corpus headline — the causal sub-layer
detecting 116 of 120 injections — can be checked by someone who is not me. Every
other table in the manuscript has a `results/` entry with a manifest beside it.
This one lived in `logs/`, which is gitignored, machine-local, and exactly what
the §6n staleness trap eats.

## It reproduced, which was not guaranteed

The campaign of 26 July left three checkpoint files — gen-1, gen-2 and the
holdout pass — and they still hold 188 rows between them. Reading the outcome
flags straight out of them gives 116/120 for [[3B Causal Analyzer]]'s causal takeover, 4/120 for
end-to-end ASR, 2/60 on the external benign cohort and 4/8 on our own. All four
are the numbers the manuscript prints, to the decimal, including the Wilson
interval [91.7%, 98.7%] that §VII quotes.

The four misses are `blunt_override-nd1`, `delegated_followup-nd0` and both
`masked_hypothetical-nd` cases. Every one is address-free. That is the paper's
whole mechanism claim — detection rides on a liftable target — falling out of the
artifact rather than being asserted over it, so I pinned it as a test:
[[Residual Misses Decomposed]] is now something the suite will defend rather than
something a reader has to take on trust. A miss on an address-carrying case fails
the build.

## The part worth writing down is what was *not* recorded

Two things this run never left behind, and the interesting work was deciding what
to do about them.

**There is no original manifest.** `run_campaign.py` predates `build_manifest`
entirely, and the newest record in `logs/red_team_runs/` is 22 July — four days
before these checkpoints. Rules §7 asks that a replay keep the original run's
manifest alongside the analysis one. There is not one to keep, so
`original_manifest` is `null` with the reason attached.

**The run's configuration was never written down either**, and this is where the
temptation sat. `CausalAnalyzer()` will tell me the model tags, the temperature
and `k_samples` in one line, and dropping those into a field called
`models_at_run` would have produced a manifest that looks complete. It would also
have asserted a July configuration nobody checked, using September's code as the
source. That is the same move as stamping the current commit on an older run,
which is the precise thing `replay.fully_replayed` was added to prevent. So those
fields are `null`, and the only configuration value claimed is
`ie_threshold = 0.5` — because the analyzer writes it into every takeover reason
string and it is sitting there in 116 of them. Evidence rather than recall.

The general form: *a manifest's job is to record what was known, and a blank is
information*. A filled-in blank that came from somewhere else is worse than the
blank, because nothing downstream can tell them apart. Related in spirit to
[[A Published p-Value With No Committed Source]] — that one was a statistic with
no committed source, this would have been a provenance field with no source at
all.

## The guard, and the guard's own bug

The two benign cohorts must never be pooled — 8 hand-written controls, half of
which I wrote specifically to break the detector, against 60 documents someone
else wrote. `4/8` was read as a false-positive rate once and that is the scar the
rule comes from. So the report prints them apart, labels the 4/8 a diagnostic in
the output itself, and `_assert_unpooled` fails the run rather than letting a
pooled `6/68` appear.

My first version of that guard did not work. It checked whether any cohort's *n*
equalled the sum of both cohorts' *n*, which for a genuine merge (68 and 68) is
136 and never matches. The test I had written for it failed immediately, which is
the only reason I know. A guard against the project's most-repeated mistake,
silently inert on the case it exists for. [[Instruments Fail More Than Mechanisms]]
would have had a sixth entry if I had shipped it and checked the output by eye. The working version asserts the cohorts *partition* the benign
set: their counts must sum to exactly the number of benign episodes, and none may
carry the whole denominator.

## What the artifact is, and is not

`per_case` for all 188 episodes goes into the committed file, which is the actual
repair rather than a nicety. The Phase 10 failure was a statistic whose inputs
existed only in a gitignored checkpoint, and the fix there was to commit the
per-case data beside the rate. Same fix here, and the test rebuilds every headline
from `per_case` alone — no logs, no models, no GPU, so it runs on a fresh clone.

It is still a **replay**. Nothing was re-executed, no model was called, and the
numbers cannot move; the manifest says so in a field, not in a comment. And the
inputs themselves are gitignored, so a fresh clone cannot rebuild the checkpoints
without re-running the campaign — roughly an hour and a half on this card. That
is the same departure [[Recorded Probe Output Makes Scorer Changes Cheap]]'s
audit sibling records, and committing `per_case` mitigates it rather than curing
it. I considered re-running the campaign live instead, and did not: a fresh run
would produce *different* numbers, because
[[The Benign FPR Has a Noise Floor Its Own Size]] is exactly about that, and
replacing the headline two days before a submission date is not a
reproducibility fix.

494 tests pass, up from 484.

## What this entry does not establish

**Not that the campaign is reproducible from a clean clone.** It is reproducible
from a committed artifact, which is a weaker and more honest claim. The
distinction is in the manifest and in `results/README.md`, and it should stay
there rather than being rounded up in conversation.

**Not that 116/120 is a stable figure.** It is a single run. The benign side has
three recordings and a measured floor; the attack side has one pass and no
spread, and nothing here changes that.

**Nothing about the second model family**, which is the hardening item that
actually answers the objection a reviewer reaches for first, and which remains
untouched.

## Related

- [[A Published p-Value With No Committed Source]]
- [[The Benign FPR Has a Noise Floor Its Own Size]]
- [[Residual Misses Decomposed]], [[Address-Free Attacks]]
- [[Instruments Fail More Than Mechanisms]]
- [[Entry XXIV — The Corpus Was Already Complete]]
