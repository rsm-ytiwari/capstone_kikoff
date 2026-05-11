"""
Entry point for building the Kikoff MMM midterm deck.
Run from the project root:
    .venv/bin/python deliverables/midterm_presentation/build_deck.py
"""

import os
import sys

# Ensure local imports work regardless of working directory
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)

from pptx import Presentation
from pptx.util import Inches

from slides import (
    slide_01_cover,
    slide_02_toc,
    slide_03_team,
    slide_04_exec_summary,
    slide_05_business_problem,
    slide_06_data_overview,
    slide_07_deliverables,
    slide_08_method_selection,
    slide_09_eda_channels,
    slide_10_eda_outcomes,
    slide_11_model_architecture,
    slide_12_model_results,
    slide_13_conclusion,
    slide_14_qa,
    slide_15_appendix,
)

OUTPUT = os.path.join(_HERE, 'midterm_deck.pptx')


def build():
    prs = Presentation()
    prs.slide_width  = Inches(13.333)
    prs.slide_height = Inches(7.5)

    slide_01_cover.build(prs)
    slide_02_toc.build(prs)
    slide_03_team.build(prs)
    slide_04_exec_summary.build(prs)
    slide_05_business_problem.build(prs)
    slide_06_data_overview.build(prs)
    slide_07_deliverables.build(prs)
    slide_08_method_selection.build(prs)
    slide_09_eda_channels.build(prs)
    slide_10_eda_outcomes.build(prs)
    slide_11_model_architecture.build(prs)
    slide_12_model_results.build(prs)
    slide_13_conclusion.build(prs)
    slide_14_qa.build(prs)
    slide_15_appendix.build(prs)

    prs.save(OUTPUT)
    print(f'Saved: {OUTPUT}  ({len(prs.slides)} slides)')


if __name__ == '__main__':
    build()
