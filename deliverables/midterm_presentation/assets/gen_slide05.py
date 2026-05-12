"""
Slide 5 — Attribution Comparison chart generator.
Run with the project venv Python.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch

# ── Design tokens ──────────────────────────────────────────────────────────
NAVY    = "#182B48"
GOLD    = "#FFCC00"
WHITE   = "#FFFFFF"
CHARCOAL= "#333333"

OUT = (
    "/Users/yashtiwari/MSBA/Quarters/Spring_2026/capstone_team"
    "/deliverables/midterm_presentation/assets/slide_05_attribution_comparison.png"
)

# ── Figure ─────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(13, 5.5))
fig.patch.set_facecolor(WHITE)
ax.set_facecolor(WHITE)
ax.axis("off")
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)

# ── Box geometry ───────────────────────────────────────────────────────────
BOX_Y      = 0.13   # bottom of both boxes
BOX_H      = 0.79   # height
LEFT_X     = 0.01   # left box left edge
BOX_W      = 0.42   # width of each box
RIGHT_X    = 0.57   # right box left edge
RADIUS     = 0.02

def draw_box(x, y, w, h):
    patch = FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad=0,rounding_size={RADIUS}",
        linewidth=0,
        facecolor=NAVY,
        transform=ax.transAxes,
        zorder=2,
    )
    ax.add_patch(patch)

draw_box(LEFT_X,  BOX_Y, BOX_W, BOX_H)
draw_box(RIGHT_X, BOX_Y, BOX_W, BOX_H)

# ── Headers ────────────────────────────────────────────────────────────────
HEADER_Y = 0.865

ax.text(
    LEFT_X + BOX_W / 2, HEADER_Y,
    "Today: Last-Touch Attribution",
    color=GOLD, fontsize=13.5, fontweight="bold",
    ha="center", va="center",
    transform=ax.transAxes, zorder=3,
)

ax.text(
    RIGHT_X + BOX_W / 2, HEADER_Y,
    "With Our MMM: Incremental Attribution",
    color=GOLD, fontsize=13.5, fontweight="bold",
    ha="center", va="center",
    transform=ax.transAxes, zorder=3,
)

# ── Bullet points ──────────────────────────────────────────────────────────
LEFT_BULLETS = [
    "Platform-reported ROAS double-counts\nconversions across channels",
    "No baseline demand separation —\nall conversions attributed to ads",
    "No saturation modeling — spend keeps\nscaling past the knee",
    "Budget decisions based on Meta/TikTok\nself-reported numbers",
]

RIGHT_BULLETS = [
    "Causal ICAC and ROAS curves per\nchannel × platform",
    "Baseline demand separated from\npaid media lift",
    "Saturation curves reveal diminishing\nreturns and scaling headroom",
    "Budget decisions grounded in 4 real\nincrementality tests",
]

BULLET_TOP   = 0.775   # y of first bullet (axes fraction)
BULLET_STEP  = 0.155   # vertical spacing between bullets
BULLET_PAD_X = 0.025   # horizontal inset from box edge

def draw_bullets(bullets, box_x, box_w):
    text_x = box_x + BULLET_PAD_X
    for i, line in enumerate(bullets):
        y = BULLET_TOP - i * BULLET_STEP
        ax.text(
            text_x, y,
            f"• {line}",
            color=WHITE, fontsize=10.5,
            ha="left", va="top",
            transform=ax.transAxes, zorder=3,
            linespacing=1.35,
        )

draw_bullets(LEFT_BULLETS,  LEFT_X,  BOX_W)
draw_bullets(RIGHT_BULLETS, RIGHT_X, BOX_W)

# ── Callout stats (below boxes) ────────────────────────────────────────────
STAT_Y = 0.055

ax.text(
    LEFT_X + BOX_W / 2, STAT_Y,
    "$113M allocated without holistic causal signal",
    color=GOLD, fontsize=10, fontweight="bold",
    ha="center", va="center",
    transform=ax.transAxes, zorder=3,
)

ax.text(
    RIGHT_X + BOX_W / 2, STAT_Y,
    "~33% input into Kikoff's internal budget allocation model",
    color=GOLD, fontsize=10, fontweight="bold",
    ha="center", va="center",
    transform=ax.transAxes, zorder=3,
)

# ── Center arrow ───────────────────────────────────────────────────────────
ARROW_X = LEFT_X + BOX_W + (RIGHT_X - LEFT_X - BOX_W) / 2   # midpoint of gap
ARROW_Y = BOX_Y + BOX_H / 2

ax.text(
    ARROW_X, ARROW_Y,
    "→",
    color=GOLD, fontsize=42, fontweight="bold",
    ha="center", va="center",
    transform=ax.transAxes, zorder=3,
)

# ── Save ───────────────────────────────────────────────────────────────────
plt.tight_layout(pad=0)
fig.savefig(OUT, dpi=150, bbox_inches="tight", facecolor=WHITE)
plt.close(fig)
print(f"Saved: {OUT}")
