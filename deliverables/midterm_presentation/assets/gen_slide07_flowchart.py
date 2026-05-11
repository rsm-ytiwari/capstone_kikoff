"""
Generate slide_07_output_flowchart.png
Horizontal 4-step pipeline flowchart for midterm presentation slide 7.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch

# ── Design tokens ──────────────────────────────────────────────────────────────
NAVY    = "#182B48"
GOLD    = "#FFCC00"
WHITE   = "#FFFFFF"
CHARCOAL = "#333333"
BG      = "#FFFFFF"

from pathlib import Path
OUT = str(Path(__file__).parent / "slide_07_output_flowchart.png")

# ── Content ────────────────────────────────────────────────────────────────────
steps = [
    {
        "title": "Daily Spend Data",
        "detail": "639 obs × 13 channels\n× 3 platforms\n2024-07-01 to 2026-03-31",
    },
    {
        "title": "PyMC-Marketing Model",
        "detail": "Adstock decay + Hill saturation\n+ time-limited incrementality\npriors (4 real tests)",
    },
    {
        "title": "ICAC & ROAS Curves",
        "detail": "Per channel × platform\nConversions + LTV\ndual dependent variables",
    },
    {
        "title": "Decisioning Table",
        "detail": "Spend signal · trend\n· saturation estimate\n→ recommended action",
    },
]

SUBTITLE = "~33% weighted input into Kikoff's internal budget allocation model"

# ── Layout constants (in data-units, axes spans 0→1 in y, 0→total_w in x) ────
FIG_W, FIG_H = 13, 5.5
DPI = 150

n_steps    = len(steps)
arrow_w    = 0.045       # fraction of total x for each arrow gap
box_w_frac = (1.0 - arrow_w * (n_steps - 1)) / n_steps   # box width fraction
box_h      = 0.52        # box height in axes y-units (axes runs 0→1)
box_y      = 0.28        # bottom of box in axes y-units
subtitle_y = 0.08        # subtitle centre y

fig, ax = plt.subplots(figsize=(FIG_W, FIG_H), dpi=DPI)
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis("off")

# ── Draw boxes + text ──────────────────────────────────────────────────────────
box_positions = []  # store (x_left, x_right) for arrow placement

for i, step in enumerate(steps):
    x_left = i * (box_w_frac + arrow_w)
    x_right = x_left + box_w_frac
    box_positions.append((x_left, x_right))
    cx = (x_left + x_right) / 2  # horizontal centre of box

    # Navy rounded rectangle
    fancy = FancyBboxPatch(
        (x_left, box_y),
        box_w_frac,
        box_h,
        boxstyle="round,pad=0.02",
        linewidth=0,
        facecolor=NAVY,
        zorder=2,
    )
    ax.add_patch(fancy)

    # Gold bold title — top portion of box
    ax.text(
        cx,
        box_y + box_h * 0.72,
        step["title"],
        ha="center",
        va="center",
        fontsize=12.5,
        fontweight="bold",
        color=GOLD,
        zorder=3,
        wrap=False,
    )

    # Thin gold separator line
    sep_y = box_y + box_h * 0.54
    ax.plot(
        [x_left + 0.012, x_right - 0.012],
        [sep_y, sep_y],
        color=GOLD,
        linewidth=0.8,
        zorder=3,
        alpha=0.6,
    )

    # White detail text — lower portion of box
    ax.text(
        cx,
        box_y + box_h * 0.28,
        step["detail"],
        ha="center",
        va="center",
        fontsize=9.8,
        color=WHITE,
        zorder=3,
        linespacing=1.55,
    )

# ── Draw gold arrows between boxes ────────────────────────────────────────────
arrow_y = box_y + box_h / 2  # vertical midpoint of boxes

for i in range(n_steps - 1):
    x_start = box_positions[i][1] + 0.004
    x_end   = box_positions[i + 1][0] - 0.004

    ax.annotate(
        "",
        xy=(x_end, arrow_y),
        xytext=(x_start, arrow_y),
        arrowprops=dict(
            arrowstyle="->,head_width=0.45,head_length=0.35",
            color=GOLD,
            lw=3.0,
        ),
        zorder=4,
    )

# ── Subtitle row ───────────────────────────────────────────────────────────────
ax.text(
    0.5,
    subtitle_y,
    SUBTITLE,
    ha="center",
    va="center",
    fontsize=11,
    color=CHARCOAL,
    style="italic",
    zorder=3,
)

# ── Save ───────────────────────────────────────────────────────────────────────
plt.tight_layout(pad=0)
fig.savefig(OUT, dpi=DPI, bbox_inches="tight", facecolor=BG)
plt.close(fig)
print(f"Saved: {OUT}")
