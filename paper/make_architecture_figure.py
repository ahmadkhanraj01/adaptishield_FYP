#!/usr/bin/env python3
"""
The architecture figure for the manuscript — print-ready, and deliberately NOT
the implementation diagram.

`AdaptiShield_Architecture_v3.drawio.png` is the engineering diagram: every
module, every feedback path, ~10,000 px wide. It is unreadable at one column and
it shows components the evaluation reports as inert with the same weight as the
two that carry the system. This figure is the paper's version — the same
pipeline, drawn so that the reader can see the finding in it: 3B and 3C are the
only components that move an outcome (§V), and everything else is drawn muted.

It is a *structural schematic*, so unlike `make_figures.py` it reads nothing from
`results/` and asserts nothing numeric. It lives in a separate script for exactly
that reason: make_figures.py's contract is that every figure it produces is
traceable to a committed measurement, and this one is not.

    python3 paper/make_architecture_figure.py
"""

import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIGDIR = os.path.join(REPO, "paper", "figures")

BLUE   = "#0072B2"
ORANGE = "#D55E00"
INK    = "#14202E"
MUTED  = "#59667A"
HAIR   = "#C9D2DC"
SUNK   = "#EDF1F5"
WHITE  = "#FFFFFF"

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["DejaVu Serif", "Times New Roman"],
    "font.size": 7.4,
    "text.color": INK,
    "figure.dpi": 400,
})


def box(ax, x, y, w, h, label, sub=None, edge=HAIR, face=WHITE, lw=0.8,
        bold=False, tcol=INK, fs=7.4, subfs=6.2, subcol=MUTED):
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h, boxstyle="round,pad=0,rounding_size=0.012",
        linewidth=lw, edgecolor=edge, facecolor=face, zorder=2))
    ty = y + h / 2 + (0.018 if sub else 0)
    ax.text(x + w / 2, ty, label, ha="center", va="center", zorder=3,
            fontsize=fs, color=tcol, fontweight="bold" if bold else "normal")
    if sub:
        ax.text(x + w / 2, y + h / 2 - 0.026, sub, ha="center", va="center",
                zorder=3, fontsize=subfs, color=subcol)


def arrow(ax, x1, y1, x2, y2, color=MUTED, lw=0.8, style="-|>", dashed=False):
    ax.add_patch(FancyArrowPatch(
        (x1, y1), (x2, y2), arrowstyle=style, mutation_scale=6,
        linewidth=lw, color=color, zorder=4,
        linestyle=(0, (2.2, 1.6)) if dashed else "solid",
        shrinkA=0, shrinkB=0))


def build():
    fig, ax = plt.subplots(figsize=(6.9, 3.75))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    # ── left: the six layers ────────────────────────────────────────────────
    lx, lw = 0.035, 0.315
    layers = [
        ("Layer 5", "human review and observability"),
        ("Layer 4", "permission scope · egress allowlist · sandbox"),
        ("Layer 3", "tool execution + response screener"),
        ("Layer 2", "agent control plane + security sub-layer"),
        ("Layer 1", "input parsing · provenance · context assembly"),
        ("Layer 0", "transport and server trust"),
    ]
    h, gap = 0.108, 0.036
    y = 0.075
    ys = {}
    for name, desc in reversed(layers):          # draw bottom-up: L0 lowest
        hot = name == "Layer 2"
        box(ax, lx, y, lw, h, name, desc,
            edge=BLUE if hot else HAIR,
            face="#F2F7FC" if hot else WHITE,
            lw=1.3 if hot else 0.8, bold=hot,
            tcol=BLUE if hot else INK)
        ys[name] = y
        y += h + gap

    ax.text(lx + lw / 2, y + 0.012, "A REQUEST TRAVERSES THE STACK · EACH LAYER MAY REFUSE",
            ha="center", va="bottom", fontsize=5.9, color=MUTED, fontweight="bold")

    for i in range(len(layers) - 1):
        yy = 0.075 + i * (h + gap)
        arrow(ax, lx + lw * 0.30, yy + h + gap, lx + lw * 0.30, yy + h,
              color=HAIR, lw=0.7)
        arrow(ax, lx + lw * 0.70, yy + h, lx + lw * 0.70, yy + h + gap,
              color=HAIR, lw=0.7)

    # untrusted mediator enters at the tool-response boundary
    ax.text(lx - 0.012, ys["Layer 3"] + h / 2, "untrusted\nmediator",
            ha="right", va="center", fontsize=6.0, color=ORANGE, fontweight="bold")
    arrow(ax, lx - 0.012, ys["Layer 3"] + h / 2, lx, ys["Layer 3"] + h / 2,
          color=ORANGE, lw=1.0)

    # ── the callout from Layer 2 to the detail panel ────────────────────────
    px, pw = 0.435, 0.53
    py, ph = 0.075, 0.775
    ax.add_patch(FancyBboxPatch(
        (px, py), pw, ph, boxstyle="round,pad=0,rounding_size=0.012",
        linewidth=0.9, edgecolor=BLUE, facecolor="#FAFCFE", zorder=1))
    arrow(ax, lx + lw, ys["Layer 2"] + h * 0.5, px, ys["Layer 2"] + h * 0.5,
          color=BLUE, lw=0.9)

    ax.text(px + 0.018, py + ph - 0.032, "SECURITY SUB-LAYER (INSIDE LAYER 2)",
            fontsize=6.1, color=BLUE, fontweight="bold", va="center")

    # ── the four components ─────────────────────────────────────────────────
    bx, bw, bh = px + 0.018, pw - 0.036, 0.082
    comp = [
        ("3A — policy engine", "static triage; routes high-impact calls", False),
        ("3B — causal analyzer", "four regimes · ACE and IE contrasts", True),
        ("3C — context sanitiser", "runs after takeover → safe continuation", True),
        ("3D — adaptive tuner", "proposes config changes for human approval", False),
    ]
    cy = py + ph - 0.145
    centers = {}
    for label, desc, live in comp:
        box(ax, bx, cy - bh, bw, bh, label, desc,
            edge=ORANGE if live else HAIR,
            face="#FDF4F0" if live else SUNK,
            lw=1.2 if live else 0.8, bold=live,
            tcol=ORANGE if live else MUTED,
            subcol=MUTED, fs=7.2)
        centers[label.split(" ")[0]] = cy - bh / 2
        if cy - bh > py + 0.30:
            arrow(ax, bx + bw / 2, cy - bh, bx + bw / 2, cy - bh - 0.030,
                  color=HAIR, lw=0.7)
        cy -= bh + 0.030

    # ── what 3B actually computes ───────────────────────────────────────────
    ry = py + 0.040
    ax.text(bx, ry + 0.128, "THE FOUR REGIMES 3B RUNS PER BOUNDARY",
            fontsize=5.9, color=MUTED, fontweight="bold", va="center")
    chips = ["orig", "masked", "masked_san", "orig_san"]
    cw = (bw - 3 * 0.012) / 4
    for i, name in enumerate(chips):
        x = bx + i * (cw + 0.012)
        box(ax, x, ry + 0.062, cw, 0.048, name, edge=HAIR, face=WHITE, fs=6.3)
    ax.text(bx, ry + 0.026,
            "ACE = orig − masked        IE = masked − masked_san",
            fontsize=6.4, color=INK, va="center", family="monospace")
    ax.text(bx, ry - 0.006,
            "takeover ⇐ IE rule · standalone rule · temporal-drift rule",
            fontsize=6.1, color=MUTED, va="center")

    # ── legend ──────────────────────────────────────────────────────────────
    ly = 0.020
    ax.add_patch(FancyBboxPatch((lx, ly), 0.016, 0.016,
                                boxstyle="round,pad=0,rounding_size=0.004",
                                linewidth=1.2, edgecolor=ORANGE,
                                facecolor="#FDF4F0", zorder=3))
    ax.text(lx + 0.024, ly + 0.008, "moves a measured outcome (§V)",
            fontsize=6.2, color=INK, va="center")
    ax.add_patch(FancyBboxPatch((lx + 0.30, ly), 0.016, 0.016,
                                boxstyle="round,pad=0,rounding_size=0.004",
                                linewidth=0.8, edgecolor=HAIR,
                                facecolor=SUNK, zorder=3))
    ax.text(lx + 0.324, ly + 0.008,
            "no measured effect on either outcome, on our corpus",
            fontsize=6.2, color=MUTED, va="center")

    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    os.makedirs(FIGDIR, exist_ok=True)
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(FIGDIR, f"fig0_architecture.{ext}"),
                    bbox_inches="tight", pad_inches=0.02,
                    facecolor="white")
    plt.close(fig)
    print(f"wrote {FIGDIR}/fig0_architecture.{{png,pdf}}")


if __name__ == "__main__":
    build()
