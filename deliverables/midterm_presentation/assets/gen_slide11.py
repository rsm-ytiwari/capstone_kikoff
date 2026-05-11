"""
Slide 11 — Model Architecture Pipeline
Self-contained. Run with project venv.

Layout: figure is 13 × 5.5 in.
  Left 62%  (0 → 8.06): 5-stage pipeline
  Right 38% (8.2 → 13): Key Design Decisions panel
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import os

# ── Design tokens ──────────────────────────────────────────────────────────
NAVY     = "#182B48"
GOLD     = "#FFCC00"
WHITE    = "#FFFFFF"
CHARCOAL = "#333333"
LGRAY    = "#F2F2F2"

FIG_W, FIG_H = 13, 5.5
OUT = os.path.join(os.path.dirname(__file__), "slide_11_model_architecture.png")

fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))
fig.patch.set_facecolor(WHITE)
ax.set_facecolor(WHITE)
ax.set_xlim(0, FIG_W)
ax.set_ylim(0, FIG_H)
ax.axis("off")

# ── Pipeline geometry ──────────────────────────────────────────────────────
# We use a two-subplot approach via nested axes so text clips cleanly.
# Pipeline occupies x ∈ [0.2, 8.0], right panel x ∈ [8.2, 12.85]

PIPE_X0   = 0.20
PIPE_X1   = 8.00
PIPE_Y0   = 0.55          # bottom of pipeline area
PIPE_Y1   = 5.10          # top of pipeline area
BOX_H     = PIPE_Y1 - PIPE_Y0   # full height = 4.55
BOX_Y     = PIPE_Y0

N_STAGES  = 5
ARROW_W   = 0.28          # gap between boxes used for arrow
PIPE_W    = PIPE_X1 - PIPE_X0
TOTAL_ARROW = (N_STAGES - 1) * ARROW_W
BOX_W     = (PIPE_W - TOTAL_ARROW) / N_STAGES   # ≈ 1.264

BAND_H    = 0.78          # gold title band height

stages = [
    {
        "title": "Raw Spend",
        "body":  ["Daily spend per", "channel × platform", "639 rows", "2024-07-01 →", "2026-03-31"],
        "highlight": False,
    },
    {
        "title": "Adstock\nDecay",
        "body":  ["Geometric carryover", "(alpha per channel)", "", "Captures lagged", "media effects"],
        "highlight": False,
    },
    {
        "title": "Hill\nSaturation",
        "body":  ["Diminishing returns", "(lambda + beta)", "", "Models efficiency", "curve shape"],
        "highlight": False,
    },
    {
        "title": "Priors",
        "body":  ["Incrementality", "test iCAC", "", "injected as", "time-limited priors"],
        "highlight": True,
    },
    {
        "title": "ICAC + ROAS\nOutput",
        "body":  ["Per channel", "× platform", "", "Conversions +", "LTV dual models"],
        "highlight": False,
    },
]

box_rights = []

for i, stage in enumerate(stages):
    xl = PIPE_X0 + i * (BOX_W + ARROW_W)
    xr = xl + BOX_W
    xc = xl + BOX_W / 2

    edge_c = GOLD  if stage["highlight"] else NAVY
    edge_w = 3.0   if stage["highlight"] else 0.0

    # Navy box
    ax.add_patch(FancyBboxPatch(
        (xl, BOX_Y), BOX_W, BOX_H,
        boxstyle="round,pad=0.05",
        facecolor=NAVY, edgecolor=edge_c, linewidth=edge_w,
        zorder=3, clip_on=False,
    ))

    # Gold title band
    band_top = BOX_Y + BOX_H - 0.06
    band_bot = band_top - BAND_H
    ax.add_patch(FancyBboxPatch(
        (xl + 0.05, band_bot), BOX_W - 0.10, BAND_H,
        boxstyle="round,pad=0.04",
        facecolor=GOLD, edgecolor="none",
        zorder=4, clip_on=False,
    ))

    # Title text (navy on gold, multi-line OK)
    ax.text(
        xc, band_bot + BAND_H / 2,
        stage["title"],
        ha="center", va="center",
        fontsize=8.2, fontweight="bold",
        color=NAVY, zorder=5,
        multialignment="center",
        clip_on=False,
    )

    # Body text — draw each line individually, stacked downward from mid-box
    body_lines = stage["body"]
    n_lines    = len(body_lines)
    LINE_H     = 0.28           # vertical space per line (figure units)
    lower_region_h = BOX_H - BAND_H - 0.12
    lower_mid      = BOX_Y + lower_region_h / 2 + 0.06
    # start top line so block is centred
    y_top = lower_mid + (n_lines - 1) * LINE_H / 2

    for j, line in enumerate(body_lines):
        ly = y_top - j * LINE_H
        ax.text(
            xc, ly, line,
            ha="center", va="center",
            fontsize=6.0, color=WHITE, zorder=5,
            clip_on=False,
        )

    box_rights.append(xr)

# ── Arrows ─────────────────────────────────────────────────────────────────
arrow_y = BOX_Y + BOX_H / 2
for i in range(N_STAGES - 1):
    xs = box_rights[i]
    xe = xs + ARROW_W
    ax.annotate(
        "",
        xy=(xe, arrow_y), xytext=(xs, arrow_y),
        arrowprops=dict(
            arrowstyle="-|>",
            color=GOLD, lw=2.2, mutation_scale=17,
        ),
        zorder=6,
    )

# ── Right annotation panel ─────────────────────────────────────────────────
PX = 8.20
PW = 12.85 - PX
PY = 0.35
PH = FIG_H - PY - 0.25

ax.add_patch(FancyBboxPatch(
    (PX, PY), PW, PH,
    boxstyle="round,pad=0.07",
    facecolor=LGRAY, edgecolor="#CCCCCC", linewidth=1,
    zorder=2,
))

# Panel title
ax.text(
    PX + PW / 2, PY + PH - 0.28,
    "Key Design Decisions",
    ha="center", va="top",
    fontsize=9.5, fontweight="bold", color=NAVY, zorder=5,
)

# Divider
ax.plot(
    [PX + 0.12, PX + PW - 0.12],
    [PY + PH - 0.65, PY + PH - 0.65],
    color="#C0C0C0", lw=0.9, zorder=5,
)

bullets = [
    (
        "Time-limited priors",
        "Incrementality data applies ONLY within test\n"
        "windows (e.g. TikTok Aug–Sep 2025), not\n"
        "across full model history.",
    ),
    (
        "4 real tests",
        "TikTok ($81–$112 iCAC), Meta May 2025\n"
        "($63–$157), CTV ($135), Meta Jan 2026\n"
        "(high uncertainty).",
    ),
    (
        "Dual DV",
        "Conversions = primary; LTV = supplementary.\n"
        "Divergence → surface to sponsor.",
    ),
]

BULLET_TOP = PY + PH - 0.82
BULLET_GAP = (PH - 1.05) / len(bullets)

for k, (label, detail) in enumerate(bullets):
    by = BULLET_TOP - k * BULLET_GAP

    # Gold dot
    ax.plot(PX + 0.18, by, "o", color=GOLD, markersize=5.5, zorder=5)

    # Bold label
    ax.text(
        PX + 0.34, by + 0.07,
        f"{label}:",
        ha="left", va="bottom",
        fontsize=7.8, fontweight="bold", color=CHARCOAL, zorder=5,
    )

    # Detail body
    ax.text(
        PX + 0.34, by - 0.05,
        detail,
        ha="left", va="top",
        fontsize=6.8, color=CHARCOAL, zorder=5,
        linespacing=1.45,
    )

# ── Save ───────────────────────────────────────────────────────────────────
fig.savefig(OUT, dpi=150, bbox_inches="tight", facecolor=WHITE)
plt.close(fig)
print(f"Saved → {OUT}")
