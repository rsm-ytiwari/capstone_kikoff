import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from templates import add_content_slide, _add_rect, _add_textbox, NAVY, GOLD, CHARCOAL, WHITE
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN

ASSET = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                     'assets', 'slide_05_attribution_comparison.png')


def build(prs):
    slide = add_content_slide(
        prs,
        'Kikoff Invests $113M Annually With No Holistic Attribution',
        page_num=5
    )

    if os.path.exists(ASSET):
        slide.shapes.add_picture(ASSET, Inches(0.40), Inches(1.55),
                                 Inches(12.40), Inches(5.30))
        return

    # Fallback: two-box comparison
    box_w, box_h = 5.60, 4.50
    box_top = 1.80

    # Left box — "Today"
    _add_rect(slide, 0.50, box_top, box_w, box_h, fill_rgb=NAVY)
    _add_textbox(slide, 'Today: Last-Touch Attribution',
                 left=0.70, top=box_top + 0.20, width=5.20, height=0.55,
                 font_size=16, bold=True, color=GOLD)
    today_bullets = [
        'Platform-reported ROAS double-counts conversions',
        'No visibility into diminishing returns or saturation',
        'Budget allocation based on platform metrics, not causal lift',
        'Heavy reliance on Meta and TikTok self-reported data',
    ]
    body = box_top + 0.90
    for b in today_bullets:
        _add_textbox(slide, '• ' + b, left=0.70, top=body, width=5.20,
                     height=0.60, font_size=13, color=WHITE)
        body += 0.70

    # Arrow divider
    _add_textbox(slide, '→', left=6.20, top=box_top + 1.80, width=0.80,
                 height=0.80, font_size=36, bold=True, color=GOLD,
                 align=PP_ALIGN.CENTER)

    # Right box — "With MMM"
    _add_rect(slide, 7.10, box_top, box_w, box_h, fill_rgb=NAVY)
    _add_textbox(slide, 'With MMM: Incremental Attribution',
                 left=7.30, top=box_top + 0.20, width=5.20, height=0.55,
                 font_size=16, bold=True, color=GOLD)
    mmm_bullets = [
        'Causal ICAC and ROAS per channel × platform',
        'Saturation curves reveal where to scale vs. pull back',
        'Baseline demand separated from paid media lift',
        'Budget recommendations grounded in real incrementality tests',
    ]
    body = box_top + 0.90
    for b in mmm_bullets:
        _add_textbox(slide, '• ' + b, left=7.30, top=body, width=5.20,
                     height=0.60, font_size=13, color=WHITE)
        body += 0.70
