"""
Slide 13 — Project Timeline (Gantt-style)
Self-contained script. Run with project venv.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import matplotlib.dates as mdates
from datetime import date

# ── Design system ─────────────────────────────────────────────────────────────
NAVY      = "#182B48"
GOLD      = "#FFCC00"
WHITE     = "#FFFFFF"
CHARCOAL  = "#333333"
LGRAY     = "#F0F0F0"
RED_DLINE = "#E8372C"   # deadline accent

# ── Data ──────────────────────────────────────────────────────────────────────
# Each milestone: (label, start, end, status)
# status: "done" | "progress" | "pending"
milestones = [
    (
        "Phase 1: Business Understanding & Data Audit",
        date(2026, 3, 2),
        date(2026, 4, 25),
        "done",
    ),
    (
        "M1: Data Cleaning (LTV, Platform, DSP, Dates)",
        date(2026, 4, 1),
        date(2026, 4, 30),
        "done",
    ),
    (
        "M2: Time-Limited Prior Mechanism (Q19)",
        date(2026, 5, 1),
        date(2026, 5, 28),
        "progress",
    ),
    (
        "M3: Multi-Channel Model Build",
        date(2026, 5, 10),
        date(2026, 6, 5),
        "pending",
    ),
    (
        "M5: Decisioning Layer",
        date(2026, 6, 1),
        date(2026, 6, 6),
        "pending",
    ),
]

DEADLINE = date(2026, 6, 6)

# ── Style mapping ──────────────────────────────────────────────────────────────
STATUS_COLOR   = {"done": NAVY,  "progress": GOLD,  "pending": LGRAY}
STATUS_EDGE    = {"done": NAVY,  "progress": GOLD,   "pending": NAVY}
STATUS_BADGE   = {"done": "DONE",        "progress": "IN PROG",  "pending": ""}
BADGE_BG       = {"done": GOLD,          "progress": NAVY,        "pending": None}
BADGE_FG       = {"done": NAVY,          "progress": GOLD,        "pending": None}

# ── Figure ─────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(13, 5.5))
fig.patch.set_facecolor(WHITE)
ax.set_facecolor(WHITE)

# ── Axis limits ────────────────────────────────────────────────────────────────
x_min = date(2026, 3, 1)
x_max = date(2026, 6, 15)
ax.set_xlim(x_min, x_max)

n = len(milestones)
# Y: one row per milestone. Top row = index 0 → y = n-1 down to 0.
BAR_HEIGHT = 0.55
Y_SPACING  = 1.0   # centre-to-centre
y_centers  = [n - 1 - i for i in range(n)]   # [4,3,2,1,0]

ax.set_ylim(-0.8, n - 0.3)

# ── Grid ───────────────────────────────────────────────────────────────────────
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
ax.xaxis.set_minor_locator(mdates.WeekdayLocator(byweekday=0))

ax.grid(axis="x", which="major", color=LGRAY, linewidth=1.0, zorder=0)
ax.grid(axis="x", which="minor", color=LGRAY, linewidth=0.3, zorder=0)
ax.grid(axis="y", visible=False)

# Add a special tick for Jun 6
ax.xaxis.set_major_locator(
    mdates.DateLocator() if False else mdates.MonthLocator()
)

# ── Bars ───────────────────────────────────────────────────────────────────────
for i, (label, start, end, status) in enumerate(milestones):
    yc = y_centers[i]
    yb = yc - BAR_HEIGHT / 2

    start_f = mdates.date2num(start)
    end_f   = mdates.date2num(end)
    width_f = end_f - start_f

    color = STATUS_COLOR[status]
    edge  = STATUS_EDGE[status]
    lw    = 1.5 if status == "pending" else 0

    bar = FancyBboxPatch(
        (start_f, yb),
        width_f, BAR_HEIGHT,
        boxstyle="round,pad=0.3",
        facecolor=color,
        edgecolor=edge,
        linewidth=lw,
        zorder=3,
    )
    ax.add_patch(bar)

    # ── Badge pill — inside bar, right-aligned ────────────────────────────
    badge = STATUS_BADGE[status]
    if badge:
        bg_col = BADGE_BG[status]
        fg_col = BADGE_FG[status]
        # Place ~10% from bar right edge
        badge_x = start_f + width_f * 0.88
        ax.text(
            badge_x, yc, badge,
            ha="center", va="center",
            fontsize=7, color=fg_col,
            fontweight="bold", zorder=6,
            bbox=dict(
                facecolor=bg_col,
                edgecolor="none",
                boxstyle="round,pad=0.28",
            ),
        )

    # ── Label (left of bar) ────────────────────────────────────────────────
    ax.text(
        start_f - 0.5, yc, label,
        ha="right", va="center",
        fontsize=8.5, color=CHARCOAL,
        fontweight="semibold",
    )

# ── Deadline marker ────────────────────────────────────────────────────────────
dl_x = mdates.date2num(DEADLINE)
ax.axvline(dl_x, color=GOLD, linewidth=2, linestyle="--", zorder=7)
ax.text(
    dl_x, n - 0.1,
    "  Deadline: June 6",
    ha="left", va="top",
    fontsize=9, color=CHARCOAL,
    fontweight="bold",
    rotation=0,
    bbox=dict(facecolor=WHITE, edgecolor=GOLD, boxstyle="round,pad=0.25", linewidth=1.2),
    zorder=8,
)

# ── X-axis ticks: month labels + Jun 6 ────────────────────────────────────────
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
plt.setp(ax.get_xticklabels(), fontsize=9, color=CHARCOAL, rotation=0, ha="center")

# ── Y-axis: hide ticks, labels handled via text ───────────────────────────────
ax.set_yticks([])
ax.set_yticklabels([])

# ── Spines ────────────────────────────────────────────────────────────────────
for spine in ["top", "right", "left"]:
    ax.spines[spine].set_visible(False)
ax.spines["bottom"].set_color(LGRAY)

# ── Title ─────────────────────────────────────────────────────────────────────
ax.set_title(
    "Project Timeline",
    fontsize=14, fontweight="bold", color=NAVY,
    loc="left", pad=10,
)

# ── Legend ────────────────────────────────────────────────────────────────────
legend_patches = [
    mpatches.Patch(facecolor=NAVY,  edgecolor=NAVY,  label="Completed"),
    mpatches.Patch(facecolor=GOLD,  edgecolor=GOLD,  label="In Progress"),
    mpatches.Patch(facecolor=LGRAY, edgecolor=NAVY,  label="Not Started", linewidth=1.2),
]
ax.legend(
    handles=legend_patches,
    loc="lower center",
    bbox_to_anchor=(0.5, -0.22),
    ncol=3,
    frameon=False,
    fontsize=9,
    handlelength=1.5,
    handleheight=0.9,
)

plt.tight_layout(rect=[0.22, 0.05, 1.0, 1.0])

# ── Save ──────────────────────────────────────────────────────────────────────
from pathlib import Path
OUT = str(Path(__file__).parent / "slide_13_timeline.png")
fig.savefig(OUT, dpi=150, bbox_inches="tight", facecolor=WHITE)
print(f"Saved → {OUT}")
