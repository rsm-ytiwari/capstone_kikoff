import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from templates import add_title_section_slide, _add_textbox, GOLD, WHITE
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN


def build(prs):
    slide = add_title_section_slide(prs, title='Questions?')
