"""
Paired comparison between two arms — McNemar's test, on the same cases.

WHY THIS FILE EXISTS, AND WHY IT IS LATE. Phase 10 reported "McNemar p = 1.00, 8
helped / 7 hurt" in the root README, `Phase.md`, the vault and Volume II. That
number was computed **ad hoc in a shell** and never committed: nothing in
`results/phase10/benchmark.json` records the discordant counts, and no committed
code recomputed the p-value. Rules §7 requires every number in the paper to be
regenerable by one committed command whose artifact is committed. It was not.

This is the same class of defect as the Phase 7 withdrawal and the refusal audit's
missing control — not a wrong number, but a number whose provenance could not be
checked. The p-value happens to be right; that is luck, not process.

WHY PAIRED RATHER THAN TWO INTERVALS. Comparing two Wilson intervals for overlap
is the wrong test when both arms ran **the same cases**. Overlapping intervals do
not imply no effect, and non-overlapping ones overstate the evidence, because the
comparison discards the pairing. What carries information is the **discordant**
cases: those one arm stopped and the other did not. Concordant cases — both
stopped, or neither — tell you nothing about which arm is better, however many
there are.

WHY THE EXACT TEST. The discordant counts here are single digits (8 and 7 for
Phase 10). The chi-square form of McNemar, with or without continuity correction,
is an asymptotic approximation that is unreliable below roughly 25 discordant
pairs. So the exact binomial is the p-value of record and the chi-square figure is
reported beside it only because reviewers expect to see it.

WHAT A NULL FROM THIS DOES NOT MEAN. `p = 1.00` with 8 versus 7 discordant pairs is
not "the two arms are equivalent". It is "at n=15 discordant pairs this design
cannot distinguish them", which is a statement about power. Phase 10's null further
decomposes into two per-family effects of opposite sign, which a single p-value
cannot show — so `by_group` exists to make that visible.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Tuple


@dataclass
class McNemar:
    """
    `b` = cases the baseline failed and the treatment stopped (**treatment helped**).
    `c` = cases the baseline stopped and the treatment failed (**treatment hurt**).

    Naming them by direction rather than by cell index is deliberate: every time
    this table is written as b/c someone eventually reads the sign backwards, and
    a reversed sign is exactly the error that had to be withdrawn from Phase 10.
    """
    baseline: str
    treatment: str
    n_pairs: int              # cases present in both arms
    both_bad: int             # neither stopped it
    both_good: int            # both stopped it
    helped: int               # b — treatment stopped what baseline missed
    hurt: int                 # c — treatment missed what baseline stopped
    p_exact: float            # two-sided exact binomial on the discordant pairs
    p_chi2_cc: Optional[float]  # chi-square with continuity correction, or None
    baseline_rate: float
    treatment_rate: float

    @property
    def discordant(self) -> int:
        return self.helped + self.hurt

    @property
    def usable(self) -> bool:
        """Enough discordant pairs for the asymptotic form to mean anything."""
        return self.discordant >= 25

    def to_dict(self) -> dict:
        out = asdict(self)
        out["discordant"] = self.discordant
        out["asymptotic_usable"] = self.usable
        out["p_of_record"] = self.p_exact
        return out


def _binom_two_sided(b: int, c: int) -> float:
    """
    Exact two-sided binomial test on the discordant pairs, H0: p = 0.5.

    Doubling the smaller tail is the standard construction for the symmetric
    p = 0.5 case and is what "exact McNemar" means in the literature. Clamped at
    1.0 because doubling can exceed it when the split is near-even — which is
    precisely Phase 10's situation (8 vs 7 gives exactly 1.00, not 1.03).
    """
    n = b + c
    if n == 0:
        # No discordant pairs at all. The arms behaved identically on every case,
        # which is not evidence of equivalence — it is a design that cannot
        # distinguish them. p = 1 is the honest report; `discordant == 0` is the
        # field to actually read.
        return 1.0

    k = min(b, c)
    tail = sum(math.comb(n, i) for i in range(k + 1)) / (2 ** n)
    return min(1.0, 2 * tail)


def _chi2_sf_1df(x: float) -> float:
    """
    Survival function of chi-square with 1 df = erfc(sqrt(x/2)).

    Implemented directly rather than pulling in scipy: this project keeps its
    dependency set to what `requirements.txt` already pins, and `fpr_report`'s
    Wilson interval sets the same precedent.
    """
    if x <= 0:
        return 1.0
    return math.erfc(math.sqrt(x / 2.0))


def mcnemar(baseline: Dict[str, bool], treatment: Dict[str, bool],
            baseline_name: str = "baseline",
            treatment_name: str = "treatment") -> McNemar:
    """
    `True` means **the arm handled the case correctly** — the attack was stopped,
    or the agent was not steered.

    Callers must not pass "attack succeeded" directly. The polarity is stated here
    because a silently inverted input produces a plausible table with `helped` and
    `hurt` swapped, and nothing downstream can detect it.

    Only case ids present in **both** dicts are used. A case that one arm skipped
    is not a pair, and quietly treating a missing entry as a failure would let a
    crashed arm look like a worse defense.
    """
    shared = sorted(set(baseline) & set(treatment))

    both_bad = both_good = helped = hurt = 0
    for case_id in shared:
        base_ok, treat_ok = bool(baseline[case_id]), bool(treatment[case_id])
        if base_ok and treat_ok:
            both_good += 1
        elif not base_ok and not treat_ok:
            both_bad += 1
        elif treat_ok:
            helped += 1
        else:
            hurt += 1

    n = len(shared)
    p_exact = _binom_two_sided(helped, hurt)

    discordant = helped + hurt
    if discordant:
        stat = (abs(helped - hurt) - 1) ** 2 / discordant
        p_chi2 = _chi2_sf_1df(stat)
    else:
        p_chi2 = None

    return McNemar(
        baseline=baseline_name, treatment=treatment_name, n_pairs=n,
        both_bad=both_bad, both_good=both_good, helped=helped, hurt=hurt,
        p_exact=p_exact, p_chi2_cc=p_chi2,
        baseline_rate=(both_good + hurt) / n if n else 0.0,
        treatment_rate=(both_good + helped) / n if n else 0.0)


def by_group(baseline: Dict[str, bool], treatment: Dict[str, bool],
             groups: Dict[str, str]) -> Dict[str, dict]:
    """
    The same comparison split by attack family.

    This exists because Phase 10's overall null was **two opposing effects
    cancelling** — `important_instructions` improved while `blunt_override` got
    worse — and a single p-value reports that as "nothing happened". A null that is
    really two effects is a different finding from a null that is indifference, and
    only the split can tell them apart.

    ⚠️ These are exploratory and **unadjusted for multiple comparisons**. With six
    families, one nominally significant result is what chance produces. Read them
    as directions, never as claims.
    """
    out: Dict[str, dict] = {}
    for group in sorted(set(groups.get(cid, "?") for cid in
                            set(baseline) & set(treatment))):
        members = {cid for cid, g in groups.items() if g == group}
        sub_base = {k: v for k, v in baseline.items() if k in members}
        sub_treat = {k: v for k, v in treatment.items() if k in members}
        if not (set(sub_base) & set(sub_treat)):
            continue
        out[group] = mcnemar(sub_base, sub_treat, "baseline", "treatment").to_dict()
    return out


def ladder(outcomes: Dict[str, Dict[str, bool]],
           order: List[str]) -> List[dict]:
    """
    Adjacent-pair tests along a cumulative ablation ladder.

    Phase 11's question is not "is the full system better than nothing" — Phase 7
    answered that. It is **what does each layer add on top of the one before it**,
    which is the comparison that either justifies the layering or does not. So the
    test that matters runs between *consecutive* rungs, and a layer contributing
    nothing shows up as its own row with `helped == 0`.

    Arms named in `order` but absent from `outcomes` are skipped, so a partial run
    still reports the rungs it has.
    """
    present = [a for a in order if a in outcomes]
    return [mcnemar(outcomes[lo], outcomes[hi], lo, hi).to_dict()
            for lo, hi in zip(present, present[1:])]


def format_table(rows: List[dict]) -> str:
    """Fixed-width rendering for the benchmark report."""
    if not rows:
        return "  (no paired comparisons — need at least two arms)\n"

    lines = [
        f"  {'baseline -> treatment':<40}{'n':>5}{'helped':>8}{'hurt':>6}"
        f"{'disc':>6}{'p (exact)':>11}",
        f"  {'-' * 40}{'-' * 5}{'-' * 8}{'-' * 6}{'-' * 6}{'-' * 11}",
    ]
    for row in rows:
        pair = f"{row['baseline']} -> {row['treatment']}"
        flag = "" if row["asymptotic_usable"] else " *"
        lines.append(
            f"  {pair:<40}{row['n_pairs']:>5}{row['helped']:>8}{row['hurt']:>6}"
            f"{row['discordant']:>6}{row['p_exact']:>10.3f}{flag}")

    if any(not r["asymptotic_usable"] for r in rows):
        lines.append("")
        lines.append("  * fewer than 25 discordant pairs — the exact binomial is the")
        lines.append("    p-value of record; the chi-square form would not be reliable.")
        lines.append("    A high p here means LOW POWER, not equivalence. Read `disc`.")
    return "\n".join(lines) + "\n"
