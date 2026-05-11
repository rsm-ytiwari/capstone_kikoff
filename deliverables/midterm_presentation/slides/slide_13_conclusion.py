import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from templates import add_content_slide, _add_rect, _add_textbox, NAVY, GOLD, CHARCOAL, WHITE
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN

ASSET = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                     'assets', 'slide_13_timeline.png')

DONE = [
    'Phase 1 complete — data audit, EDA, 5 quality issues resolved',
    'M1 complete — LTV imputation, platform normalization, DSP mapping, date filter',
    'Facebook POC in progress — pipeline validated, model run underway',
]

NEXT = [
    'M2: Approve time-limited prior mechanism (Q19) → decisions_log.md',
    'M3: Multi-channel model — replicate for all 13 channels × platforms',
    'M5: Decisioning layer — signal, trend, saturation → recommended action',
    'Delivery: Full ICAC + ROAS + decisioning package by June 6, 2026',
]


def build(prs):
    slide = add_content_slide(
        prs,
        'Phase 2 Is Running — Full Decisioning Package Delivered by June 6',
        page_num=13
    )

    if os.path.exists(ASSET):
        slide.shapes.add_picture(ASSET, Inches(0.40), Inches(1.55),
                                 Inches(12.40), Inches(5.30))
        return

    # Fallback: two-column done / next
    col_top = 1.75
    col_h   = 4.80
    col_w   = 5.70

    # Done column
    _add_rect(slide, 0.50, col_top, col_w, 0.48, fill_rgb=NAVY)
    _add_textbox(slide, '✓  Completed',
                 left=0.60, top=col_top + 0.06, width=col_w - 0.20,
                 height=0.38, font_size=15, bold=True, color=GOLD)
    bt = col_top + 0.60
    for b in DONE:
        _add_textbox(slide, '• ' + b, left=0.60, top=bt,
                     width=col_w - 0.20, height=0.75,
                     font_size=13, color=CHARCOAL)
        bt += 0.90

    # Next column
    lx = 7.00
    _add_rect(slide, lx, col_top, col_w, 0.48, fill_rgb=GOLD)
    _add_textbox(slide, '→  Next 5 Weeks',
                 left=lx + 0.10, top=col_top + 0.06, width=col_w - 0.20,
                 height=0.38, font_size=15, bold=True, color=NAVY)
    bt = col_top + 0.60
    for b in NEXT:
        _add_textbox(slide, '• ' + b, left=lx + 0.10, top=bt,
                     width=col_w - 0.20, height=0.75,
                     font_size=13, color=CHARCOAL)
        bt += 0.90

    # Deadline callout
    _add_rect(slide, 0.50, 6.58, 12.20, 0.52, fill_rgb=NAVY)
    _add_textbox(slide,
                 'Project deadline: June 6, 2026  ·  ~5 weeks remaining  ·  '
                 'Scope: ICAC + ROAS + decisioning table for all 13 channels',
                 left=0.60, top=6.62, width=12.00, height=0.40,
                 font_size=12, bold=False, color=WHITE,
                 align=PP_ALIGN.CENTER)
