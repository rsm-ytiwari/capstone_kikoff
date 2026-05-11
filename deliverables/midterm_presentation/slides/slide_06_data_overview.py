import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from templates import add_content_slide, _add_rect, _add_textbox, NAVY, GOLD, CHARCOAL, WHITE
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

LGRAY = RGBColor(0xF0, 0xF0, 0xF0)

STATS = [
    ('639', 'Daily observations\n2024-07-01 to 2026-03-31'),
    ('13', 'Modeled channels\nMeta, TikTok, Google + 10 more'),
    ('$132K', 'Avg daily spend\n($0–$300K+ range)'),
    ('2,560', 'Mean daily conversions\n(peak: 4,354 on 2025-05-30)'),
]

QUALITY_ROWS = [
    ('LTV anomalies',        'Imputation for 2025-10-21–24 window',  '✓ |z| max = 0.85'),
    ('Platform typos',       '"iso"→iOS; "web and app"→web',          '✓ PASS'),
    ('DSP channel mapping',  '15 SOURCE_GROUPs → 13 canonical ch.',   '✓ PASS'),
    ('StackAdapt row count', '341 rows in window (threshold: >30)',    '✓ PASS'),
    ('Date filter',          '2024-07-01 to 2026-03-31 enforced',     '✓ PASS'),
]


def _stat_card(slide, value, label, left, top, width=2.80, height=1.50):
    _add_rect(slide, left, top, width, height, fill_rgb=NAVY)
    _add_textbox(slide, value, left=left + 0.10, top=top + 0.10,
                 width=width - 0.20, height=0.70,
                 font_size=26, bold=True, color=GOLD, align=PP_ALIGN.CENTER)
    _add_textbox(slide, label, left=left + 0.10, top=top + 0.82,
                 width=width - 0.20, height=0.60,
                 font_size=11, color=WHITE, align=PP_ALIGN.CENTER)


def build(prs):
    slide = add_content_slide(
        prs,
        'Daily Spend and Outcomes Across 13 Channels — 5 Quality Issues Resolved',
        page_num=6
    )

    # Stat cards row
    for i, (val, lbl) in enumerate(STATS):
        _stat_card(slide, val, lbl, left=0.50 + i * 3.20, top=1.72)

    # Quality table
    tbl_top = 3.58
    col_w = [2.80, 5.20, 3.60]
    col_x = [0.60, 3.60, 9.00]

    _add_rect(slide, 0.50, tbl_top, 12.20, 0.38, fill_rgb=NAVY)
    for h, lx in zip(['Data Issue', 'Action Taken', 'Result'], col_x):
        _add_textbox(slide, h, left=lx, top=tbl_top + 0.05,
                     width=2.50, height=0.28, font_size=12, bold=True, color=WHITE)

    for ri, (issue, action, result) in enumerate(QUALITY_ROWS):
        rt = tbl_top + 0.40 + ri * 0.60
        if ri % 2 == 0:
            _add_rect(slide, 0.50, rt, 12.20, 0.58, fill_rgb=LGRAY)
        for val, lx, w in zip([issue, action, result], col_x, col_w):
            _add_textbox(slide, val, left=lx, top=rt + 0.08,
                         width=w, height=0.44, font_size=11, color=CHARCOAL)
