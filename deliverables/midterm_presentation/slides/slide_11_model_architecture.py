import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from templates import add_content_slide, _add_rect, _add_textbox, NAVY, GOLD, CHARCOAL, WHITE
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN

ASSET = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                     'assets', 'slide_11_model_architecture.png')

STEPS = [
    ('Raw Spend',       'Daily channel × platform spend\n(639 obs, 2024-07-01 to 2026-03-31)'),
    ('Adstock Decay',   'Geometric carryover (alpha per channel)\nCaptures lagged media effects'),
    ('Hill Saturation', 'Diminishing returns (lam + beta)\nModels spend efficiency curve'),
    ('Priors',          'Incrementality test iCAC injected\nas time-limited Bayesian priors'),
    ('Outcome Model',   'Conversions (primary) + LTV\nDual DV → ICAC + ROAS per channel'),
]


def build(prs):
    slide = add_content_slide(
        prs,
        'Analytics Strategy: PyMC-Marketing Pipeline',
        page_num=11
    )

    if os.path.exists(ASSET):
        slide.shapes.add_picture(ASSET, Inches(0.40), Inches(1.55),
                                 Inches(12.40), Inches(5.30))
        return

    # Fallback: vertical pipeline left side + annotation right side
    stage_h = 0.90
    gap     = 0.18
    lx      = 1.00
    top     = 1.70
    box_w   = 3.80

    for i, (stage, detail) in enumerate(STEPS):
        st = top + i * (stage_h + gap)
        _add_rect(slide, lx, st, box_w, stage_h, fill_rgb=NAVY)
        _add_textbox(slide, stage,
                     left=lx + 0.10, top=st + 0.05,
                     width=box_w - 0.20, height=0.40,
                     font_size=14, bold=True, color=GOLD)
        _add_textbox(slide, detail,
                     left=lx + 0.10, top=st + 0.47,
                     width=box_w - 0.20, height=0.40,
                     font_size=11, color=WHITE)
        # Arrow
        if i < len(STEPS) - 1:
            _add_textbox(slide, '↓',
                         left=lx + box_w / 2 - 0.15,
                         top=st + stage_h + 0.01,
                         width=0.30, height=0.18,
                         font_size=12, bold=True, color=GOLD,
                         align=PP_ALIGN.CENTER)

    # Annotation: where priors enter
    ann_lx = 5.50
    from pptx.dml.color import RGBColor as _RGB
    _LGRAY = _RGB(0xF8, 0xF8, 0xF8)
    _add_rect(slide, ann_lx, 1.70, 6.80, 5.40, fill_rgb=_LGRAY)

    annotations = [
        ('Time-limited priors',
         'Incrementality priors apply ONLY within the test time window\n'
         '(e.g., TikTok Aug–Sep 2025, Meta May 2025) — not across full history.\n'
         'This prevents over-generalizing test results.'),
        ('4 calibration tests',
         'TikTok: iOS $108.83, Android $81.68, Web $112.12 iCAC\n'
         'Meta May 2025: iOS $135.48, Android $63.06, Web $156.89\n'
         'CTV (geo holdout): $135 (wider CI — lower conviction)\n'
         'Meta Jan 2026: included with high uncertainty (cancelled test)'),
        ('Dual DV',
         'Conversions = primary model (directly observed)\n'
         'LTV = supplementary (inherits Kikoff internal model bias)\n'
         'If ICAC diverges between models → surface to sponsor'),
    ]

    at = 1.85
    for hdr, body in annotations:
        _add_textbox(slide, hdr,
                     left=ann_lx + 0.20, top=at,
                     width=6.40, height=0.40,
                     font_size=13, bold=True, color=NAVY)
        _add_textbox(slide, body,
                     left=ann_lx + 0.20, top=at + 0.42,
                     width=6.40, height=0.80,
                     font_size=11, color=CHARCOAL)
        at += 1.55
