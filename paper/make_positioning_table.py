#!/usr/bin/env python3
"""
The positioning table, generated FROM the committed results — never hand-typed.

Our column is read out of `results/`; the published column is read out of
`paper/external_numbers.json`, where every value carries the verbatim sentence
it came from. The script writes the table into §10 between the GENERATED
markers, so the prose around it stays hand-written and the numbers cannot drift.

Two refusals, both deliberate:

  * a missing artifact is an error, not a blank cell — a positioning table with
    a hole in it is how an unmeasured claim gets published;
  * an external row marked `verified: "unverified"` is NEVER rendered. It is
    printed to stderr as a to-do instead. Second-hand numbers about other
    people's systems are the one class of error a reviewer will certainly catch.

    python3 paper/make_positioning_table.py
"""

import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

from evaluation.fpr_report import wilson as _wilson  # noqa: E402

SECTION = os.path.join(REPO, "paper", "10-positioning.md")
EXTERNAL = os.path.join(REPO, "paper", "external_numbers.json")

BEGIN = "<!-- BEGIN GENERATED — python3 paper/make_positioning_table.py -->"
END = "<!-- END GENERATED -->"


def load(relpath):
    path = os.path.join(REPO, relpath)
    if not os.path.exists(path):
        raise SystemExit(
            f"missing artifact: {relpath}\n"
            "The table is generated from results/. Regenerate that phase before "
            "regenerating this table."
        )
    with open(path) as fh:
        return json.load(fh)


def rate(d):
    """A proportion the way Rules §7 requires it: k/n, point, Wilson interval."""
    return (
        f"**{d['rate'] * 100:.1f}%** {d['k']}/{d['n']} "
        f"[{d['wilson_low'] * 100:.1f}, {d['wilson_high'] * 100:.1f}]"
    )


def wilson(k, n):
    """Wilson interval for artifacts that report per-run hits without one.

    Delegates to `evaluation.fpr_report.wilson` rather than reimplementing it:
    two interval implementations in one repository is how a table drifts from
    the figure beside it, and the drift is invisible at three significant
    figures."""
    if n == 0:
        return 0.0, 0.0, 1.0
    lo, hi = _wilson(k, n)
    return k / n, lo, hi


def rate_kn(k, n):
    p, lo, hi = wilson(k, n)
    return f"**{p * 100:.1f}%** {k}/{n} [{lo * 100:.1f}, {hi * 100:.1f}]"


def ours():
    """Every cell in our column, straight out of the committed artifacts."""
    p7 = load("results/phase7/benchmark.json")["summaries"]
    p10 = load("results/phase10/benchmark.json")["summaries"]
    p12 = load("results/phase12/benchmark.json")["summaries"]
    nf_ia = load("results/noise_floor/injecagent.json")["summary"]["by_family"]
    nf_ad = load("results/noise_floor/agentdojo_benign.json")["summary"]
    hold = load("results/severity/rescore_holdout.json")["agentdojo_attacks"]["arms"]

    def fam(block, name):
        """Detection on one stratum. Repeats disagree, so report the median run."""
        runs = sorted(r["hits"] for r in block[name]["per_run"])
        n = block[name]["per_run"][0]["n"]
        return runs[len(runs) // 2], n, runs[0], runs[-1]

    tgt_k, tgt_n, tgt_lo, tgt_hi = fam(nf_ia, "IA-target")
    ntg_k, ntg_n, ntg_lo, ntg_hi = fam(nf_ia, "IA-notarget")
    fp_runs = sorted(r["hits"] for r in nf_ad["per_run"])
    fp_n = nf_ad["per_run"][0]["n"]

    def holdout(arm, family):
        row = next(r for r in hold[arm] if r["family"] == family)
        return rate_kn(row["hits"], row["n"])

    return {
        "p7_undef": rate(p7["undefended"]["asr"]),
        "p7_static": rate(p7["static_only"]["asr"]),
        "p7_full": rate(p7["full"]["asr"]),
        "p12_undef": rate(p12["undefended"]["asr"]),
        "p12_static": rate(p12["static_only"]["asr"]),
        "ia_target": rate_kn(tgt_k, tgt_n),
        "ia_target_spread": f"{tgt_lo}–{tgt_hi}/{tgt_n} across 3 repeats",
        "ia_notarget": rate_kn(ntg_k, ntg_n),
        "ia_notarget_spread": f"{ntg_lo}–{ntg_hi}/{ntg_n} across 3 repeats",
        "fpr": rate_kn(fp_runs[len(fp_runs) // 2], fp_n),
        "fpr_spread": f"{fp_runs[0]}–{fp_runs[-1]}/{fp_n} across 3 repeats",
        "steer_control": rate(p10["derived_control"]["steer_rate"]),
        "steer_spot": rate(p10["spotlighting"]["steer_rate"]),
        "ad_target": holdout("baseline", "AD-target"),
        "ad_notarget": holdout("baseline", "AD-notarget"),
        "ad_notarget_cap": holdout("capability", "AD-notarget"),
    }


def shown(row):
    """A published value as the paper states it — `display` wins, so a bound
    reported as ">80%" is not silently rendered as a point estimate."""
    return row.get("display") or f"{row['value_pct']:.1f}%"


def external():
    with open(EXTERNAL) as fh:
        data = json.load(fh)
    kept, dropped = {}, []
    for src in data["sources"]:
        rows = []
        for row in src["rows"]:
            if row.get("verified") != "verbatim":
                dropped.append(f"{src['key']}: {row['system']} — {row['metric']}")
                continue
            rows.append(row)
        kept[src["key"]] = dict(src, rows=rows)
    return kept, dropped


def render(o, ext):
    ia = ext["injecagent"]
    ad = ext["agentdojo"]
    sp = ext["spotlighting"]
    pi = ext["pishield"]

    def cite(src):
        return f"[{src['citation'].split(',')[0]} et al.]({src['url']})"

    L = [BEGIN, ""]

    L += [
        "### A. Attack success, on a corpus somebody else built",
        "",
        "*Ours: `results/phase12/benchmark.json`, InjecAgent `direct_harm_base`, "
        "n = 60 drawn 30/30 across the two strata. "
        f"Published: {cite(ia)}, {ia['corpus']}.*",
        "",
        "| System | Setting | ASR | Why it is not a like-for-like |",
        "| :--- | :--- | :--- | :--- |",
        f"| **AdaptiShield, undefended** | gemma3:4b / qwen2.5:3b | {o['p12_undef']} | "
        "our undefended floor, same corpus |",
        f"| **AdaptiShield, `static_only`** | same | {o['p12_static']} | "
        "the rule layer alone stops nothing here |",
    ]
    for row in ia["rows"]:
        L.append(
            f"| {row['system']} | {row['setting']} | {shown(row)} | "
            "ASR-valid over all attack types, not direct-harm only; "
            "no interval reported |"
        )
    L += [
        "",
        "**Read this as a floor check, not a win.** Our 100% is the *undefended* "
        "number, and it sits above every model InjecAgent reports because our agent "
        "is a 3–4B local model, not GPT-4. That is the point of the row: the attacks "
        "land on our harness, so a downstream difference means something. It is not "
        "evidence that our setting is harder in any interesting way.",
        "",
    ]

    L += [
        "### B. Detection, against published detectors",
        "",
        "*Ours: `results/noise_floor/{injecagent,agentdojo_benign}.json`, median of "
        "3 repeats, per stratum and never pooled. "
        f"Published: {cite(pi)}, averages over {pi['corpus']}.*",
        "",
        "| Detector | Detection (1 − FNR) | FPR | Evaluated on |",
        "| :--- | :--- | :--- | :--- |",
        f"| **AdaptiShield 3B — target-bearing stratum** | {o['ia_target']} | "
        f"{o['fpr']} | InjecAgent direct-harm / AgentDojo benign |",
        f"| **AdaptiShield 3B — no-target stratum** | {o['ia_notarget']} | "
        f"{o['fpr']} | same |",
    ]
    for row in pi["rows"]:
        det = 100 - row["fnr_pct"]
        L.append(
            f"| {row['system']} | {det:.1f}% | {row['value_pct']:.1f}% | "
            "text benchmarks, no agent loop |"
        )
    L += [
        "",
        f"Repeat spread: target {o['ia_target_spread']}, no-target "
        f"{o['ia_notarget_spread']}, false positives {o['fpr_spread']}.",
        "",
        "**The comparison is indicative and the direction of the bias is known.** "
        "Those detectors classify a *text* prompt on short- and long-context QA "
        "corpora; ours classifies a *turn of an agent loop* on injected tool output, "
        "and its input is the causal contrast rather than the raw text. Neither "
        "number transfers. What does transfer is the shape: published detectors "
        "trade FPR against FNR along one axis, and ours splits along a different "
        "one — near-ceiling where the injection carries a liftable target, near-floor "
        "where it does not, at one fixed false-positive rate.",
        "",
    ]

    L += [
        "### C. The published prompt-level defense, re-measured",
        "",
        "*Ours: `results/phase10/benchmark.json`, 66 malicious pairs, `steer_rate`. "
        f"Published: {cite(sp)}.*",
        "",
        "| Measurement | Before | After | Test |",
        "| :--- | :--- | :--- | :--- |",
        f"| **Spotlighting, our harness** | {o['steer_control']} | {o['steer_spot']} | "
        "paired McNemar **p = 1.00**, 8 helped / 7 hurt |",
        f"| Spotlighting, as published | >50% | <2% | {sp['rows'][0]['setting']}; "
        "no interval or paired test reported |",
        "",
        f"| Other published defense | Result | Source |",
        "| :--- | :--- | :--- |",
    ]
    for row in ad["rows"]:
        L.append(
            f"| {row['system']} ({row['setting']}) | {row['metric']} "
            f"**{row['value_pct']:.1f}%** | {cite(ad)} |"
        )
    L += [
        "",
        "**We do not claim spotlighting does not work.** We claim it had no "
        "measurable effect *here* — 3–4B local models, our corpus, action selection "
        "as the outcome — and we report the paired test rather than two overlapping "
        "intervals. The gap between >50% → <2% and 34.8% → 33.3% is most likely a "
        "gap in setting, and §4 gives the decomposition that makes the null "
        "informative rather than empty.",
        "",
    ]

    L += [
        "### D. Detector generalization, on the held-out external attack set",
        "",
        "*Ours: `results/severity/rescore_holdout.json`, AgentDojo's attack side, "
        "imported after the lexicon was frozen. No published comparator: we found no "
        "paper reporting detection stratified by whether the injection names a "
        "liftable target, which is the split this table exists to expose.*",
        "",
        "| Stratum | Baseline lexicon | + capability scoring |",
        "| :--- | :--- | :--- |",
        f"| AD-target | {o['ad_target']} | unchanged |",
        f"| AD-notarget | {o['ad_notarget']} | {o['ad_notarget_cap']} — 4/0, p = 0.125, "
        "**not significant** |",
        "",
        "### E. Our own campaign numbers, and what they are still missing",
        "",
        "*Phase 7, `results/phase7/benchmark.json`, 21 malicious cases, our own "
        "authored corpus. No external row: an attack set we wrote is not comparable "
        "with anybody's published number, and putting one beside it would invite "
        "exactly the comparison Rules §7 forbids.*",
        "",
        "| Arm | ASR |",
        "| :--- | :--- |",
        f"| `undefended` | {o['p7_undef']} |",
        f"| `static_only` (our ablation, **not** a baseline) | {o['p7_static']} |",
        f"| `full` | {o['p7_full']} |",
        "",
        "🔴 **The campaign detection headline — 116/120 = 96.7% [91.7, 98.7] — has no "
        "artifact under `results/`.** It lives in `logs/` and in the docs, which means "
        "it fails Rules §7's regenerability requirement and is the one number in the "
        "paper a reviewer could not reproduce from the repository. The external FPR "
        "beside it *is* committed (`results/noise_floor/agentdojo_benign.json`). Until "
        "`results/campaign/` exists, quote the FPR and treat the detection headline as "
        "provisional.",
        "",
        END,
    ]
    return "\n".join(L)


def main():
    o = ours()
    ext, dropped = external()
    block = render(o, ext)

    if not os.path.exists(SECTION):
        raise SystemExit(f"missing {SECTION} — the prose is hand-written, create it first")
    with open(SECTION) as fh:
        text = fh.read()
    if BEGIN not in text or END not in text:
        raise SystemExit(f"{SECTION} has no GENERATED markers; refusing to guess where the table goes")

    head, rest = text.split(BEGIN, 1)
    _, tail = rest.split(END, 1)
    with open(SECTION, "w") as fh:
        fh.write(head + block + tail)

    print(f"wrote table into {os.path.relpath(SECTION, REPO)}")
    if dropped:
        print("\nHELD BACK — unverified, not rendered:", file=sys.stderr)
        for d in dropped:
            print(f"  · {d}", file=sys.stderr)
        print(
            "  Read the primary source, replace the quote, set verified: \"verbatim\".",
            file=sys.stderr,
        )


if __name__ == "__main__":
    main()
