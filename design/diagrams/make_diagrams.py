"""
Draws the Phase 1 design diagrams into this folder.

    python design/diagrams/make_diagrams.py
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, FancyBboxPatch, Rectangle

OUT = Path(__file__).resolve().parent
INK, MUTED, LINE = "#0E1726", "#56647A", "#56647A"
SOFT, ACCENT = "#E3E8FA", "#2446C8"
GREY, EDGE = "#F5F7FA", "#8995A8"
AMBER, AMBER_EDGE = "#FBEACB", "#A96400"


def canvas(w, h, xmax, ymax):
    fig, ax = plt.subplots(figsize=(w, h), dpi=200)
    ax.set_xlim(0, xmax)
    ax.set_ylim(0, ymax)
    ax.axis("off")
    return fig, ax


def box(ax, x, y, w, h, text, fill=SOFT, edge=ACCENT, size=8.5, bold=False, align="center"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.6",
                                fc=fill, ec=edge, lw=1.1, zorder=2))
    tx = x + w / 2 if align == "center" else x + 0.8
    ax.text(tx, y + h / 2, text, ha=align, va="center", fontsize=size, color=INK, zorder=3,
            linespacing=1.3, fontweight="bold" if bold else "normal")


def arrow(ax, a, b, style="-|>", dashed=False, color=LINE):
    ax.annotate("", xy=b, xytext=a, zorder=1,
                arrowprops=dict(arrowstyle=style, color=color, lw=1.1, shrinkA=0, shrinkB=0,
                                ls="--" if dashed else "-"))


def label(ax, x, y, text, size=7.5, ha="center", color=INK):
    ax.text(x, y, text, fontsize=size, ha=ha, va="center", color=color, zorder=4, linespacing=1.25,
            bbox=dict(fc="white", ec="none", pad=1.2))


def save(fig, name):
    fig.savefig(OUT / name, bbox_inches="tight", pad_inches=0.06, facecolor="white")
    plt.close(fig)


def architecture():
    fig, ax = canvas(9.8, 6.2, 100, 64)
    # Frontend
    ax.add_patch(FancyBboxPatch((14, 53), 72, 10, boxstyle="round,pad=0,rounding_size=0.8",
                                fc="white", ec=EDGE, lw=1, ls="--"))
    ax.text(50, 61.2, "React frontend, shown by role", ha="center", va="center", fontsize=8.5, fontweight="bold", color=INK)
    box(ax, 16, 54.3, 21, 5, "Live Monitor\n(module 4)", size=8)
    box(ax, 39.5, 54.3, 21, 5, "Attack Lab and\nDemo Agent pages", size=8)
    box(ax, 63, 54.3, 21, 5, "Admin Console and\nAnalytics (module 5)", size=8)
    # Backend
    box(ax, 14, 40, 72, 7, "FastAPI backend: REST, /ws/episodes, login and roles, one engine worker", bold=True)
    arrow(ax, (26.5, 53), (26.5, 47), style="<|-")
    label(ax, 26.5, 50, "live events")
    arrow(ax, (50, 53), (50, 47), style="<|-|>")
    label(ax, 50, 50, "REST")
    arrow(ax, (73.5, 53), (73.5, 47), style="<|-|>")
    label(ax, 73.5, 50, "REST")
    # Row
    box(ax, 1, 25, 18, 8, "Attack Lab\n(module 2)")
    box(ax, 1, 10, 18, 8, "Demo Agent\n(module 1)")
    arrow(ax, (10, 25), (10, 18))
    label(ax, 10, 21.5, "plants attack")
    box(ax, 34, 10, 32, 23, "", AMBER, AMBER_EDGE)
    ax.text(50, 30.2, "Defense Engine (module 3)", ha="center", va="center", fontsize=9, fontweight="bold", color=INK, zorder=3)
    ax.text(50, 19.5, "Provenance tagging\nTool-response screening\nStatic policy rules\nCausal check\nSanitizer\nPermission and egress limits",
            ha="center", va="center", fontsize=8, color=INK, zorder=3, linespacing=1.45)
    box(ax, 81, 10, 18, 8, "Tools (simulated)\nNot a module", GREY, EDGE)
    arrow(ax, (19, 14), (34, 14))
    label(ax, 26.5, 16.2, "proposed action")
    arrow(ax, (66, 14), (81, 14))
    label(ax, 73.5, 16.2, "only if allowed")
    arrow(ax, (50, 40), (50, 33), style="<|-|>")
    label(ax, 50, 36.5, "runs jobs, returns stage events")
    arrow(ax, (20, 40), (10, 33), style="<|-|>")
    box(ax, 41.5, 0.5, 17, 6, "Ollama on the host\nLocal models", GREY, EDGE, size=8)
    arrow(ax, (50, 10), (50, 6.5), style="<|-|>")
    box(ax, 81, 25, 18, 8, "PostgreSQL\nEpisodes, events,\nproposals, approvals", GREY, EDGE, size=8)
    arrow(ax, (86, 40), (90, 33), style="<|-|>")
    save(fig, "architecture.png")


def sequence():
    names = ["User", "Demo Agent", "Backend", "Defense\nEngine", "Local models\n(Ollama)", "PostgreSQL", "Live Monitor"]
    xs = [6, 21, 36, 51, 66, 81, 95]
    fig, ax = canvas(9.8, 8.3, 101, 86)
    for x, n in zip(xs, names):
        box(ax, x - 6, 79.5, 12, 6, n, size=8)
        ax.plot([x, x], [1, 79.5], color=EDGE, lw=0.9, zorder=0)
    steps = [
        (0, 1, "1  Summarise my latest email", False),
        (1, 1, "2  Reads the email, which hides an\n    instruction. Plans forward_email", False),
        (1, 2, "3  Send proposed action", False),
        (2, 3, "4  Queue job for the worker", False),
        (3, 2, "5  received, provenance", True),
        (2, 5, "6  Save each event first", False),
        (2, 6, "7  Then publish it live. Steps 6 and 7 repeat for every event below", True),
        (3, 4, "8  Screener call", False),
        (3, 2, "9  screener: flag  |  policy: route", True),
        (3, 4, "10  Causal check: four probes, two samples each", False),
        (4, 3, "11  Actions and severities", True),
        (3, 2, "12  causal_check: takeover, rule = standalone", True),
        (3, 4, "13  Remove the injection, plan the safe action", False),
        (3, 2, "14  sanitizer: strip  |  permission, egress: pass", True),
        (3, 2, "15  final: safe_continuation, tool_may_run = true", True),
        (2, 1, "16  Result with the safe action", True),
        (1, 0, "17  Summary delivered. Nothing forwarded", True),
    ]
    y = 76
    for a, b, text, back in steps:
        if a == b:
            ax.plot([xs[a], xs[a] + 4, xs[a] + 4, xs[a]], [y + 1, y + 1, y - 1.6, y - 1.6], color=LINE, lw=1, zorder=1)
            arrow(ax, (xs[a] + 1, y - 1.6), (xs[a], y - 1.6))
            ax.text(xs[a] + 5, y - 0.3, text, fontsize=7.2, ha="left", va="center", color=INK, zorder=4, linespacing=1.25,
                    bbox=dict(fc="white", ec="none", pad=1))
            y -= 5.4
            continue
        arrow(ax, (xs[a], y), (xs[b], y), dashed=back)
        ax.text(min(xs[a], xs[b]) + 0.8, y + 1.25, text, fontsize=7.2, ha="left", va="center", color=INK, zorder=4,
                bbox=dict(fc="white", ec="none", pad=0.8))
        y -= 4.3
    save(fig, "sequence.png")


def use_cases():
    fig, ax = canvas(9.8, 6.4, 100, 66)
    ax.add_patch(Rectangle((18, 1), 64, 64, fc="white", ec=EDGE, lw=1))
    ax.text(50, 63, "AdaptiShield", ha="center", va="center", fontsize=9, fontweight="bold", color=INK)

    def actor(x, y, name):
        ax.add_patch(plt.Circle((x, y + 4.6), 1.5, fc="white", ec=INK, lw=1.1, zorder=3))
        ax.plot([x, x], [y + 3.1, y - 0.2], color=INK, lw=1.1)
        ax.plot([x - 2.2, x + 2.2], [y + 2, y + 2], color=INK, lw=1.1)
        ax.plot([x, x - 1.9], [y - 0.2, y - 2.6], color=INK, lw=1.1)
        ax.plot([x, x + 1.9], [y - 0.2, y - 2.6], color=INK, lw=1.1)
        ax.text(x, y - 4.2, name, ha="center", va="center", fontsize=8.5, color=INK)

    def uc(x, y, text):
        ax.add_patch(Ellipse((x, y), 25, 6.6, fc=SOFT, ec=ACCENT, lw=1.1, zorder=2))
        ax.text(x, y, text, ha="center", va="center", fontsize=7.6, color=INK, zorder=3, linespacing=1.15)
        return (x, y)

    actor(8, 48, "Tester")
    actor(8, 18, "Analyst")
    actor(92, 35, "Admin")
    left = {
        "UC-2": uc(35, 55.5, "UC-2 Run an attack,\nprotection off and on"),
        "UC-3": uc(35, 46.5, "UC-3 Run a batch\nof attacks"),
        "UC-4": uc(35, 37.5, "UC-4 Use the\nDemo Agent"),
        "UC-5": uc(35, 25, "UC-5 Watch live\nverdicts"),
        "UC-6": uc(35, 16, "UC-6 Replay an\nepisode"),
        "UC-7": uc(35, 7, "UC-7 View\nanalytics"),
    }
    right = {
        "UC-8": uc(66, 46, "UC-8 Approve or reject\na proposal"),
        "UC-9": uc(66, 35, "UC-9 Review policy and\ndecision history"),
    }
    login = uc(66, 16, "UC-1 Sign in")
    for k in ("UC-2", "UC-3", "UC-4"):
        ax.plot([11, left[k][0] - 12.5], [48, left[k][1]], color=LINE, lw=1, zorder=1)
    for k in ("UC-5", "UC-6", "UC-7"):
        ax.plot([11, left[k][0] - 12.5], [18, left[k][1]], color=LINE, lw=1, zorder=1)
    for k in right:
        ax.plot([89, right[k][0] + 12.5], [35, right[k][1]], color=LINE, lw=1, zorder=1)
    ax.plot([89, 78.5], [34, 16], color=LINE, lw=1, zorder=1)
    label(ax, 66, 26, "Shows each role's main use cases.\nEvery role signs in first, and an\nAdmin can use every use case", size=7.2, color=MUTED)
    save(fig, "use_cases.png")


def er():
    fig, ax = canvas(9.8, 6.5, 100, 64)
    ax.set_ylim(3, 64)

    def table(x, y, w, name, cols):
        h = 2.6 + 2.2 * len(cols)
        ax.add_patch(Rectangle((x, y - h), w, h, fc="white", ec=ACCENT, lw=1.1, zorder=2))
        ax.add_patch(Rectangle((x, y - 2.6), w, 2.6, fc=SOFT, ec=ACCENT, lw=1.1, zorder=2))
        ax.text(x + w / 2, y - 1.3, name, ha="center", va="center", fontsize=8.2, fontweight="bold", color=INK, zorder=3)
        for i, c in enumerate(cols):
            ax.text(x + 0.8, y - 3.8 - 2.2 * i, c, ha="left", va="center", fontsize=6.8, color=INK, zorder=3, family="monospace")
        return (x, y - h, w, h)

    users = table(1, 62, 24, "users", ["PK id", "name", "UQ email", "role", "password_hash", "is_active", "created_at"])
    attacks = table(1, 37, 24, "attacks", ["PK id", "source, source_index (UQ)", "suite, attack_type", "user_task", "injected_text", "proposed_action", "target, target_match", "is_benign", "FK created_by"])
    episodes = table(38, 62, 25, "episodes", ["PK id", "FK attack_id", "FK created_by", "origin, config", "action_source", "state, error", "session_id, tool_name", "user_input", "tool_response", "proposed_action", "final_status", "tool_may_run", "created / started /", "  finished_at"])
    events = table(38, 25, 25, "stage_events", ["PK id", "FK episode_id", "seq (UQ with episode)", "stage, verdict", "detail (JSONB)", "timestamp"])
    proposals = table(75, 62, 24, "proposals", ["PK id", "change (JSONB)", "claimed_reward", "status", "source_file", "UQ source_hash", "created_at"])
    approvals = table(75, 40, 24, "approvals (append-only)", ["PK id", "FK, UQ proposal_id", "FK admin_id", "decision, reason", "evidence (JSONB)", "warnings (JSONB)", "decided_at"])
    table(75, 17, 24, "evaluation_runs", ["PK id", "corpus, config", "model_tags, metrics", "commit_sha, dirty"])

    def link(a, b, ta, tb, tpos):
        ax.plot([a[0], b[0]], [a[1], b[1]], color=LINE, lw=1, zorder=1)
        label(ax, *ta[:2], ta[2], size=7)
        label(ax, *tb[:2], tb[2], size=7)

    link((25, 55), (38, 55), (27, 56.5, "1"), (35.3, 56.5, "many"), None)
    link((25, 30), (38, 40), (27, 32.8, "0..1"), (35.6, 39.5, "many"), None)
    ax.plot([50.5, 50.5], [episodes[1], 25], color=LINE, lw=1, zorder=1)
    label(ax, 49.2, 26.8, "1", size=7)
    label(ax, 53.6, 26.8, "many", size=7)
    ax.plot([87, 87], [proposals[1], 40], color=LINE, lw=1, zorder=1)
    label(ax, 85.6, 42, "1", size=7)
    label(ax, 89.2, 42, "0..1", size=7)
    ax.plot([13, 13], [users[1], 37], color=LINE, lw=1, zorder=1)
    label(ax, 14.4, users[1] - 1.1, "1", size=7)
    label(ax, 15.3, 38.2, "many", size=7)
    # users to approvals runs below stage_events, so it cannot be read as linking to it
    ax.plot([25, 31, 31, 69, 69, 75], [46, 46, 5.5, 5.5, 30, 30], color=LINE, lw=1, zorder=0)
    label(ax, 27, 47.3, "1", size=7)
    label(ax, 72.4, 31.3, "many", size=7)
    save(fig, "er.png")


if __name__ == "__main__":
    architecture()
    sequence()
    use_cases()
    er()
