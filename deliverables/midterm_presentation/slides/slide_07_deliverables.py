import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from templates import add_content_slide, _add_rect, _add_textbox, NAVY, GOLD, CHARCOAL, WHITE
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN

ASSET = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                     'assets', 'slide_07_output_flowchart.png')

STEPS = [
    ('Daily Spend Data', '639 obs × 13 channels × 3 platforms\n2024-07-01 to 2026-03-31'),
    ('PyMC-Marketing Model', 'Adstock decay + Hill saturation\n+ incrementality priors (time-limited)'),
    ('ICAC & ROAS Curves', 'Per channel × platform\nConversions + LTV dual outputs'),
    ('Decisioning Table', 'Spend signal · trend · saturation\n→ recommended action'),
]


def build(prs):
    slide = add_content_slide(
        prs,
        'We\'re Building ICAC and ROAS Curves That Turn Spend Into Decisions',
        page_num=7
    )

    if os.path.exists(ASSET):
        slide.shapes.add_picture(ASSET, Inches(0.40), Inches(1.55),
                                 Inches(12.40), Inches(5.30))
        return

    # Fallback: horizontal 4-step flow
    step_w = 2.70
    gap    = 0.40
    arrow_w = 0.40
    top    = 2.50
    box_h  = 2.80
    left   = 0.50

    for i, (title, detail) in enumerate(STEPS):
        # Box
        _add_rect(slide, left, top, step_w, box_h, fill_rgb=NAVY)
        _add_textbox(slide, title,
                     left=left + 0.10, top=top + 0.20,
                     width=step_w - 0.20, height=0.60,
                     font_size=14, bold=True, color=GOLD,
                     align=PP_ALIGN.CENTER)
        _add_textbox(slide, detail,
                     left=left + 0.10, top=top + 0.90,
                     width=step_w - 0.20, height=1.70,
                     font_size=12, color=WHITE,
                     align=PP_ALIGN.CENTER)
        left += step_w

        if i < len(STEPS) - 1:
            # Arrow
            _add_textbox(slide, '→', left=left + 0.05,
                         top=top + box_h / 2 - 0.25,
                         width=arrow_w, height=0.50,
                         font_size=24, bold=True, color=GOLD,
                         align=PP_ALIGN.CENTER)
            left += gap + arrow_w

    # Business impact note
    _add_textbox(slide,
                 '~33% weighted input into Kikoff\'s internal budget allocation model',
                 left=0.50, top=5.60, width=12.20, height=0.50,
                 font_size=13, bold=False, color=CHARCOAL,
                 align=PP_ALIGN.CENTER)
