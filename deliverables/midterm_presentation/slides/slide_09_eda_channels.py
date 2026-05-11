import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from templates import add_content_slide, _add_textbox, NAVY, GOLD, CHARCOAL
from pptx.util import Inches

_HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.abspath(os.path.join(_HERE, '..', '..'))
EDA_FIGS = os.path.join(PROJECT_ROOT, 'outputs', 'P1_02_eda', 'figures')

CHART = os.path.join(EDA_FIGS, 'channel_composition_monthly.png')
FALLBACK = os.path.join(EDA_FIGS, 'top_10_channels_spend.png')

CALLOUTS = [
    'Facebook: $41.5M (37%)   TikTok: $23.4M (21%)   Google: $17.6M (16%)',
    'Top 3 channels = 73% of $113M total spend   |   10 channels share remaining 27%',
]


def build(prs):
    slide = add_content_slide(
        prs,
        'Results & Findings to Date — Channel Spend Concentration',
        page_num=9
    )

    chart = CHART if os.path.exists(CHART) else FALLBACK
    if os.path.exists(chart):
        slide.shapes.add_picture(chart,
                                  Inches(0.40), Inches(1.58),
                                  Inches(12.40), Inches(4.90))

    for i, callout in enumerate(CALLOUTS):
        _add_textbox(slide, callout,
                     left=0.50, top=6.60 + i * 0.40, width=12.20, height=0.38,
                     font_size=12, bold=(i == 0), color=NAVY)
