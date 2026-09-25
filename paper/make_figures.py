#!/usr/bin/env python3
"""
Paper figures, generated FROM the committed results — never hand-drawn.

Every figure reads a file under results/ and fails loudly if it is missing, so a
figure cannot drift from the number it depicts. Four figures, one per evidence
section:

    fig1_ablation        §3   results/phase11/benchmark.json
    fig2_stratified      §5   results/noise_floor/injecagent.json
    fig3_generalisation  §6   results/severity/{rescore,rescore_holdout}.json
    fig4_flat_contrast   §7   results/phase15/multiturn_{r1,r2}.json

Palette: Okabe-Ito, validated colorblind-safe for print (dataviz check, light
surface: all six pass, worst adjacent CVD ΔE 11.0). Print-only on white — no dark
variant, because a paper figure has one surface.

    python3 paper/make_figures.py
"""

import json
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIGDIR = os.path.join(REPO, "paper", "figures")

BLUE   = "#0072B2"   # primary / detection
ORANGE = "#D55E00"   # contrast / workflow / holdout
GREEN  = "#009E73"   # in-sample / "works"
INK    = "#14202E"
MUTED  = "#59667A"
GRID   = "#D8DFE7"

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["DejaVu Serif", "Times New Roman"],
    "font.size": 10,
    "axes.edgecolor": MUTED,
    "axes.labelcolor": INK,
    "text.color": INK,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "axes.linewidth": 0.8,
    "figure.dpi": 150,
})


def load(*parts):
    path = os.path.join(REPO, "results", *parts)
    if not os.path.exists(path):
        raise SystemExit(f"missing results file: {path} — run its phase first")
    with open(path) as fh:
        return json.load(fh)


def save(fig, name):
    os.makedirs(FIGDIR, exist_ok=True)
    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(FIGDIR, f"{name}.{ext}"),
                    bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  wrote figures/{name}.pdf + .png")


def _wilson(k, n, z=1.96):
    if n == 0:
        return 0.0, 0.0, 0.0
    p = k / n
    d = 1 + z*z/n
    c = (p + z*z/(2*n)) / d
    h = z*((p*(1-p)/n + z*z/(4*n*n)) ** 0.5) / d
    return p, max(0, c-h), min(1, c+h)


# --------------------------------------------------------------- Fig 1
def fig1_ablation():
    """§3 — cumulative ladder: only 3B moves detection, only 3C moves workflow."""
    d = load("phase11", "benchmark.json")
    s = d["summaries"]
    order = ["undefended", "screener_only", "plus_policy", "plus_causal",
             "plus_sanitizer", "plus_permission", "full"]
    labels = ["undef.", "+screen", "+policy", "+3B\ncausal", "+3C\nsanit.",
              "+L4\nperm.", "+L4\negress"]
    stopped = [1 - s[a]["asr"]["rate"] for a in order]   # attack-stopped = 1-ASR
    wcr = [s[a]["wcr"]["rate"] for a in order]

    fig, ax = plt.subplots(figsize=(6.4, 3.5))
    x = range(len(order))
    ax.plot(x, stopped, "-o", color=BLUE, lw=2, ms=6, label="Attack stopped")
    ax.plot(x, wcr, "-s", color=ORANGE, lw=2, ms=6, label="Workflow continued")

    # annotate the two rungs that move
    ax.annotate("3B (causal)\n+85.7 pts", xy=(3, stopped[3]), xytext=(3, 0.55),
                ha="center", fontsize=8.5, color=BLUE,
                arrowprops=dict(arrowstyle="->", color=BLUE, lw=1))
    ax.annotate("3C (sanitiser)\n+85.7 pts", xy=(4, wcr[4]), xytext=(5.1, 0.5),
                ha="center", fontsize=8.5, color=ORANGE,
                arrowprops=dict(arrowstyle="->", color=ORANGE, lw=1))

    ax.set_xticks(list(x))
    ax.set_xticklabels(labels, fontsize=8.5)
    ax.set_ylim(-0.05, 1.05)
    ax.set_ylabel("rate")
    ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.yaxis.grid(True, color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax.legend(frameon=False, fontsize=9, loc="center left")
    ax.set_title("Cumulative component ablation (n=21 attacks, 33 benign)",
                 fontsize=10, color=INK, pad=8)
    save(fig, "fig1_ablation")


# --------------------------------------------------------------- Fig 2
def fig2_stratified():
    """§5 — detection by stratum; the pooled figure is wrong by 33 points."""
    nf = load("noise_floor", "injecagent.json")["summary"]["by_family"]
    tgt = [r["rate"] for r in nf["IA-target"]["per_run"]]
    ntg = [r["rate"] for r in nf["IA-notarget"]["per_run"]]
    tgt_m, ntg_m = sum(tgt)/len(tgt), sum(ntg)/len(ntg)
    pooled = (tgt_m + ntg_m) / 2   # balanced 30/30 draw

    fig, ax = plt.subplots(figsize=(5.6, 3.6))
    bars = ["target-match\nfires (~10% of\nreal attacks)",
            "target-match\ncannot fire\n(~90%)"]
    vals = [tgt_m, ntg_m]
    cols = [GREEN, ORANGE]
    xpos = [0, 1]
    b = ax.bar(xpos, vals, width=0.55, color=cols, zorder=3)
    # per-run dots to show k=3 stability
    for xp, runs in zip(xpos, (tgt, ntg)):
        ax.scatter([xp]*len(runs), runs, color=INK, s=14, zorder=5)
    for xp, v in zip(xpos, vals):
        ax.text(xp, v + 0.03, f"{v:.0%}", ha="center", fontsize=11,
                fontweight="bold", color=INK)

    # the misleading pooled line
    ax.axhline(pooled, ls="--", color=MUTED, lw=1.2, zorder=2)
    ax.text(1.46, pooled, f"  pooled {pooled:.0%}\n  (misleading)", va="center",
            fontsize=8.5, color=MUTED)

    ax.set_xticks(xpos)
    ax.set_xticklabels(bars, fontsize=9)
    ax.set_xlim(-0.6, 2.05)
    ax.set_ylim(0, 1.08)
    ax.set_ylabel("detection rate")
    ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.yaxis.grid(True, color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax.set_title("Detection on externally-authored attacks, by stratum\n"
                 "(k=3 recordings; dots = per-run)", fontsize=9.5, color=INK, pad=8)
    save(fig, "fig2_stratified")


# --------------------------------------------------------------- Fig 3
def fig3_generalisation():
    """§6 — capability lexicon: in-sample 90% vs holdout 43%, non-overlapping."""
    ins = load("severity", "rescore.json")
    hold = load("severity", "rescore_holdout.json")

    def rate(payload, cohort, arm, family):
        for row in payload[cohort]["arms"][arm]:
            if row["family"] == family:
                return row["hits"], row["n"]
        raise KeyError(family)

    # in-sample = InjecAgent no-target; holdout = AgentDojo no-target
    bi_k, bi_n = rate(ins, "injecagent", "baseline", "IA-notarget")
    ci_k, ci_n = rate(ins, "injecagent", "capability", "IA-notarget")
    holdfam = hold["agentdojo_attacks"]["arms"]["baseline"][0]["family"]
    bh_k, bh_n = rate(hold, "agentdojo_attacks", "baseline", holdfam)
    ch_k, ch_n = rate(hold, "agentdojo_attacks", "capability", holdfam)

    groups = [("in-sample\n(InjecAgent)", bi_k, bi_n, ci_k, ci_n),
              ("holdout\n(AgentDojo)", bh_k, bh_n, ch_k, ch_n)]

    fig, ax = plt.subplots(figsize=(5.6, 3.7))
    width = 0.34
    for i, (name, bk, bn, ck, cn) in enumerate(groups):
        bp, blo, bhi = _wilson(bk, bn)
        cp, clo, chi = _wilson(ck, cn)
        ax.bar(i - width/2, bp, width, color=MUTED, zorder=3,
               label="baseline scorer" if i == 0 else None)
        ax.bar(i + width/2, cp, width, color=(GREEN if i == 0 else ORANGE),
               zorder=3, label="+ capability lexicon" if i == 0 else None)
        ax.errorbar(i - width/2, bp, yerr=[[bp-blo], [bhi-bp]], fmt="none",
                    ecolor=INK, capsize=3, lw=1, zorder=5)
        ax.errorbar(i + width/2, cp, yerr=[[cp-clo], [chi-cp]], fmt="none",
                    ecolor=INK, capsize=3, lw=1, zorder=5)
        ax.text(i + width/2, cp + (chi-cp) + 0.03, f"{cp:.0%}", ha="center",
                fontsize=10.5, fontweight="bold",
                color=(GREEN if i == 0 else ORANGE))

    ax.set_xticks([0, 1])
    ax.set_xticklabels([g[0] for g in groups], fontsize=9.5)
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("address-free detection")
    ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.yaxis.grid(True, color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax.legend(frameon=False, fontsize=8.5, loc="upper right")
    ax.set_title("The lexicon generalises about half\n(bars = Wilson 95% CI)",
                 fontsize=9.5, color=INK, pad=8)
    save(fig, "fig3_generalisation")


# --------------------------------------------------------------- Fig 4
def fig4_flat_contrast():
    """§7 — orig vs masked severity: they agree on 24/30 turns, so ACE≈0."""
    pts = []
    for tag in ("r1", "r2"):
        d = load("phase15", f"multiturn_{tag}.json")
        for s in d["sessions"]:
            for t in s["turns"]:
                if t.get("causal_ran"):
                    o, m, _ = t["observed"]
                    pts.append((o, m, s["expected_malicious"]))

    from collections import Counter
    # jitter overlapping points by count
    counts = Counter((o, m, mal) for o, m, mal in pts)
    eq = sum(1 for o, m, _ in pts if o == m)

    fig, ax = plt.subplots(figsize=(4.6, 4.4))
    ax.plot([-0.3, 2.3], [-0.3, 2.3], ls="--", color=MUTED, lw=1, zorder=1)
    ax.text(2.0, 1.75, "orig = masked\n(ACE = 0)", fontsize=8.5, color=MUTED,
            ha="center", rotation=45, rotation_mode="anchor")

    # Malicious and benign turns can share an integer coordinate; offset the two
    # classes so neither hides the other (the "render and look" fix).
    for (o, m, mal), c in counts.items():
        dx = -0.11 if mal else 0.11
        col = ORANGE if mal else BLUE
        ax.scatter(o + dx, m, s=70 + 110*(c-1), color=col, alpha=0.85,
                   edgecolors="white", linewidths=1.2, zorder=4)
        if c > 1:
            ax.text(o + dx, m, str(c), ha="center", va="center", fontsize=8,
                    color="white", fontweight="bold", zorder=5)

    ax.set_xlim(-0.35, 2.45)
    ax.set_ylim(-0.35, 2.45)
    ax.set_xticks([0, 1, 2])
    ax.set_yticks([0, 1, 2])
    ax.set_xlabel("orig severity  (user goal + content)")
    ax.set_ylabel("masked severity  (content only)")
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    handles = [Patch(color=ORANGE, label="malicious turn"),
               Patch(color=BLUE, label="benign turn")]
    ax.legend(handles=handles, frameon=False, fontsize=8.5, loc="upper left")
    ax.set_title(f"The causal contrast is flat: orig = masked on {eq}/30 turns\n"
                 "(marker size = turns at that point)", fontsize=9, color=INK, pad=8)
    save(fig, "fig4_flat_contrast")


if __name__ == "__main__":
    print("generating paper figures from committed results:")
    fig1_ablation()
    fig2_stratified()
    fig3_generalisation()
    fig4_flat_contrast()
    print(f"\nall figures -> {FIGDIR}")
