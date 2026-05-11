# Design System — Kikoff MMM Midterm Presentation

## Colors

| Name | Hex | RGB | Use |
|------|-----|-----|-----|
| Navy | `#182B48` | 24, 43, 72 | All headings, body text, footer bar, title slide background |
| Gold | `#FFCC00` | 255, 204, 0 | Header tab, page numbers, chart accent/highlight bars |
| White | `#FFFFFF` | 255, 255, 255 | Content slide background, reversed text on navy slides |
| Charcoal | `#333333` | 51, 51, 51 | Secondary body text on white slides |
| Light Gray | `#F0F0F0` | 240, 240, 240 | Chart gridlines, secondary bars only |

## Slide Dimensions

- Canvas: **13.333" × 7.5"** (standard 16:9 widescreen)
- python-pptx: `Inches(13.333)` width, `Inches(7.5)` height

## Template Files (pre-built composites in assets/)

| File | Layout | Notes |
|------|--------|-------|
| `assets/content.png` | Content slide | White bg, gold tab top-right, navy footer bottom-left, UCSD wordmark baked in, page "2" baked in |
| `assets/main_background.png` | Title/section slide | Full navy bg, gold tab top-right, UCSD wordmark baked in |

Both images are rendered at 1920×1080px and inserted as full-slide backgrounds (0, 0, 13.333", 7.5").

## Layout Geometry (all in inches, relative to slide top-left)

### Content Slide
| Element | Left | Top | Width | Height | Notes |
|---------|------|-----|-------|--------|-------|
| Background | 0 | 0 | 13.333 | 7.5 | `content.png` |
| Page# cover | 0.15 | 7.15 | 0.30 | 0.32 | Navy rect over baked-in "2" |
| Page# text | 0.16 | 7.16 | 0.28 | 0.28 | Gold, 9pt, left-aligned |
| Slide title | 0.50 | 0.87 | 9.50 | 0.65 | Navy, 22pt bold |
| Content body | 0.50 | 1.60 | 12.20 | 5.20 | Safe zone for text/charts |
| Chart (full-width) | 0.40 | 1.55 | 12.40 | 5.30 | For single full-width charts |
| Chart (left half) | 0.40 | 1.55 | 5.90 | 5.30 | For 2-panel charts |
| Chart (right half) | 6.50 | 1.55 | 5.80 | 5.30 | For 2-panel charts |

### Title/Section Slide
| Element | Left | Top | Width | Height | Notes |
|---------|------|-----|-------|--------|-------|
| Background | 0 | 0 | 13.333 | 7.5 | `main_background.png` |
| Main title | 1.00 | 2.00 | 9.50 | 2.00 | White, 36pt bold |
| Subtitle | 1.00 | 4.10 | 9.50 | 0.70 | Gold, 20pt, not bold |
| Detail lines | 1.00 | 4.90 | 9.50 | 1.80 | White, 16pt |

## Typography

| Role | Font | Size | Weight | Color |
|------|------|------|--------|-------|
| Content slide title | Calibri | 22pt | Bold | Navy `#182B48` |
| Title slide main | Calibri | 36pt | Bold | White `#FFFFFF` |
| Title slide subtitle | Calibri | 20pt | Normal | Gold `#FFCC00` |
| Body bullet | Calibri | 16pt | Normal | Charcoal `#333333` |
| Body emphasis | Calibri | 16pt | Bold | Navy `#182B48` |
| Page number | Calibri | 9pt | Normal | Gold `#FFCC00` |
| Table header | Calibri | 13pt | Bold | White on Navy |
| Table body | Calibri | 12pt | Normal | Charcoal `#333333` |

## Chart Styling (matplotlib)

```python
CHART_STYLE = {
    'figure.facecolor': 'white',
    'axes.facecolor': 'white',
    'axes.edgecolor': '#182B48',
    'axes.labelcolor': '#182B48',
    'xtick.color': '#182B48',
    'ytick.color': '#182B48',
    'text.color': '#182B48',
    'grid.color': '#F0F0F0',
    'grid.linewidth': 0.5,
}
PRIMARY_COLOR = '#FFCC00'     # gold — main bars / lines
SECONDARY_COLOR = '#182B48'   # navy — secondary bars / annotations
ACCENT_COLOR = '#F0F0F0'      # light gray — background bars / gridlines
```

All charts: `dpi=150`, `transparent=False`, white background. Size: 12"×5" for full-width, 6"×5" for half-width.

## Rules (non-negotiable)

1. Every slide uses `add_content_slide()` or `add_title_section_slide()` from `templates.py` — never hand-position the background image per slide
2. UCSD wordmark is in both template PNGs — do not add a separate wordmark shape
3. Navy and gold are the only brand colors; use `#333333` only for body text, `#F0F0F0` only for chart gridlines
4. No code screenshots anywhere
5. Slide titles must be takeaways/insights, not descriptive labels
6. All axis labels, legends, and tick marks must be visible at slide scale (min 11pt equivalent)
