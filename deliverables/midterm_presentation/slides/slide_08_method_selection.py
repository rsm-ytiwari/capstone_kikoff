import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from templates import add_content_slide, _add_rect, _add_textbox, NAVY, GOLD, CHARCOAL, WHITE
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN

ASSET = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                     'assets', 'slide_08_framework_comparison.png')

# rows: (framework, incrementality_priors, saturation_curves, dual_dv, maintained)
FRAMEWORKS = [
    ('PyMC-Marketing ✓', 'Yes', 'Yes', 'Yes', 'Active — selected'),
    ('Meridian (Google)',  'Limited', 'Yes', 'No', 'Active'),
    ('Robyn (Meta)',       'No',      'Yes', 'No', 'Active'),
    ('LightweightMMM',    'Yes',     'Yes', 'No', 'Deprecated'),
    ('Custom PyMC',       'Yes',     'Yes', 'Yes', 'N/A — too risky'),
]
HEADERS = ['Framework', 'Incr. Priors', 'Saturation', 'Dual DV', 'Status']
COL_W = [3.50, 1.90, 1.70, 1.50, 3.00]


def build(prs):
    slide = add_content_slide(
        prs,
        'Evaluation Criteria: How We Selected Our Modeling Framework',
        page_num=8
    )

    if os.path.exists(ASSET):
        slide.shapes.add_picture(ASSET, Inches(0.40), Inches(1.55),
                                 Inches(12.40), Inches(5.30))
        return

    # Context line
    _add_textbox(slide,
                 'Key constraints: (1) incorporate 4 incrementality tests as priors, '
                 '(2) model saturation, (3) dual dependent variable (conversions + LTV)',
                 left=0.50, top=1.65, width=12.20, height=0.55,
                 font_size=13, color=CHARCOAL)

    # Table header
    tbl_top = 2.35
    _add_rect(slide, 0.50, tbl_top, 12.20, 0.42, fill_rgb=NAVY)
    lx = 0.60
    for h, w in zip(HEADERS, COL_W):
        _add_textbox(slide, h, left=lx, top=tbl_top + 0.05,
                     width=w, height=0.32, font_size=12, bold=True, color=WHITE)
        lx += w + 0.10

    # Table rows
    for ri, row in enumerate(FRAMEWORKS):
        row_top = tbl_top + 0.44 + ri * 0.70
        is_selected = ri == 0
        bg = GOLD if is_selected else (NAVY if ri % 2 == 1 else None)
        if bg:
            _add_rect(slide, 0.50, row_top, 12.20, 0.68, fill_rgb=bg)
        lx = 0.60
        for cell, w in zip(row, COL_W):
            tc = NAVY if is_selected else (WHITE if ri % 2 == 1 else CHARCOAL)
            _add_textbox(slide, cell, left=lx, top=row_top + 0.08,
                         width=w, height=0.52, font_size=12,
                         bold=is_selected, color=tc)
            lx += w + 0.10

    # Rationale note
    _add_textbox(slide,
                 'PyMC-Marketing selected by consensus with sponsor (Abheek Sinha) '
                 'on 2026-04-21 — best balance of flexibility and timeline risk.',
                 left=0.50, top=6.90, width=12.20, height=0.45,
                 font_size=11, color=CHARCOAL)
