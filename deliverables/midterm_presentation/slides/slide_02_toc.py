import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from templates import add_content_slide, _add_textbox, NAVY, GOLD, CHARCOAL
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN


ITEMS = [
    'Who are we?',
    'Executive Summary',
    'Business Problem & Organization',
    'Data Overview',
    'Deliverables & Evaluation Criteria',
    'Solution Path',
    'Results & Findings to Date',
    'Analytics Strategy',
    'Recommendations',
    'Conclusion & Next Steps',
    'Q&A',
    'Appendix',
]


def _circle_badge(slide, num, left, top, diam=0.38):
    shape = slide.shapes.add_shape(
        9,  # OVAL
        Inches(left), Inches(top), Inches(diam), Inches(diam)
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = GOLD
    shape.line.fill.background()
    _add_textbox(slide, str(num),
                 left=left, top=top + 0.03,
                 width=diam, height=diam - 0.04,
                 font_size=11, bold=True, color=NAVY,
                 align=PP_ALIGN.CENTER)


def build(prs):
    slide = add_content_slide(prs, 'Overview', page_num=2)

    diam = 0.38
    gap = 0.14          # space between circle right edge and label
    row_spacing = 0.82
    row_start = 1.72
    left_col_x = 0.55
    right_col_x = 6.85
    label_w = 5.50

    for i, label in enumerate(ITEMS):
        col = i // 6
        row = i % 6
        x = left_col_x if col == 0 else right_col_x
        y = row_start + row * row_spacing

        _circle_badge(slide, i + 1, x, y, diam)

        _add_textbox(slide, label,
                     left=x + diam + gap, top=y + 0.05,
                     width=label_w, height=0.36,
                     font_size=14, bold=False, color=CHARCOAL,
                     align=PP_ALIGN.LEFT)
