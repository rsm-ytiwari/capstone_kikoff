import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from templates import add_content_slide, _add_rect, _add_textbox, NAVY, GOLD, CHARCOAL, WHITE
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN

COL_W = 3.80
COL_GAP = 0.23
COL_STARTS = [0.50, 0.50 + COL_W + COL_GAP, 0.50 + 2 * (COL_W + COL_GAP)]

COLUMNS = [
    {
        'header': 'Signal',
        'header_bg': NAVY,
        'header_fg': GOLD,
        'bullets': [
            'Is iCAC improving, flat, or declining over time?',
            'Is current spend approaching the saturation point?',
            'Is iROAS above or below the efficiency threshold?',
            'How does performance vary across iOS / Web / Android?',
        ],
    },
    {
        'header': 'Action',
        'header_bg': NAVY,
        'header_fg': GOLD,
        'bullets': [
            '✓ Scale — iCAC declining, iROAS > 1.5x, below saturation',
            '⏸ Hold — iCAC flat or marginal, near saturation',
            '⚠ Investigate — iCAC rising rapidly or iROAS < 1x',
            '🔬 Test — no incrementality data; run holdout before scaling',
        ],
    },
    {
        'header': "What We're Building",
        'header_bg': GOLD,
        'header_fg': NAVY,
        'bullets': [
            'ICAC + ROAS response curves per channel × platform',
            'Saturation read: where diminishing returns kick in',
            'Seasonal modifiers: tax season / holiday / steady-state',
            'Full decisioning table — all 13 channels by June 6',
        ],
    },
]


def build(prs):
    slide = add_content_slide(
        prs,
        'How Model Outputs Become Budget Decisions — The Decisioning Framework',
        page_num=12
    )

    col_top = 1.70
    hdr_h = 0.46
    body_top = col_top + hdr_h + 0.10
    bullet_h = 0.72

    for col_i, col in enumerate(COLUMNS):
        lx = COL_STARTS[col_i]

        _add_rect(slide, lx, col_top, COL_W, hdr_h, fill_rgb=col['header_bg'])
        _add_textbox(slide, col['header'],
                     left=lx + 0.12, top=col_top + 0.09,
                     width=COL_W - 0.24, height=0.32,
                     font_size=14, bold=True, color=col['header_fg'],
                     align=PP_ALIGN.LEFT)

        for bi, bullet in enumerate(col['bullets']):
            bt = body_top + bi * bullet_h
            _add_textbox(slide, '• ' + bullet,
                         left=lx + 0.10, top=bt,
                         width=COL_W - 0.20, height=bullet_h - 0.06,
                         font_size=12, color=CHARCOAL, word_wrap=True)

    _add_rect(slide, 0.50, 6.62, 12.20, 0.52, fill_rgb=NAVY)
    _add_textbox(slide,
                 'Model run in progress — full ICAC/ROAS results will be presented at the final presentation',
                 left=0.60, top=6.66, width=12.00, height=0.40,
                 font_size=12, bold=False, color=WHITE,
                 align=PP_ALIGN.CENTER)
