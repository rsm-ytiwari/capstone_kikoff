import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from templates import add_content_slide
from pptx.util import Inches

ASSET = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'assets', 'Draft_MMM_kikoff.pptx.png'
)


def build(prs):
    slide = add_content_slide(prs, '', page_num=3)
    if os.path.exists(ASSET):
        slide.shapes.add_picture(ASSET,
                                  Inches(0.40), Inches(1.40),
                                  Inches(12.50), Inches(5.70))
