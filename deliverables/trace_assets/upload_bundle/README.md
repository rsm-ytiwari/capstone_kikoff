# TRACE Submission — Claude Design Upload Bundle

**For:** TRACE Awards presentation, due 2026-05-21 EOD
**Use:** Upload all files in this folder to a fresh claude.ai chat,
then paste the TRACE prompt.

---

## File inventory

### Content sources (authoritative for facts)
- **01_project_brief.md** — original business framing (Kikoff context, project goals). Authoritative for slides 2–5.
- **02_post_meeting6_journey.md** — modeling journey + current state + numbers. Authoritative for slides 6–11 + appendix. Every model/result number cited in the deck must come from here.

### Visual templates (honor these — UCSD branding built in)
- **03_template_white_content.svg** — WHITE template for body slides, data viz, info-dense content.
- **04_template_dark_transition.svg** — DARK template for title (slide 1), Vincent preemption (slide 3), closing (slide 11).
- **05_ucsd_wordmark.png** — UCSD wordmark backup (likely already embedded in templates).

### Chart data (use to build native charts, not screenshots)
- **06_oot_model1_conversions_timeseries.csv** — per-week M1 OOT data for slide 7 chart.
- **07_oot_model2_ltv_timeseries.csv** — per-week M2 OOT data for slide 7 chart.
- **08_baseline_split.json** — per-channel concentration ratios + baseline decomposition for slides 8 + 9.

### Dashboard screenshots
- **09_dashboard_main.png** — main dashboard with Meta Web selected (USE for slide 11 embed).
- **10_dashboard_decisioning.png** — 19-row decisioning table (REFERENCE only — slide 10 should render natively from project content).
- **11_dashboard_oot.png** — OOT charts page (REFERENCE only — slide 7 should render charts natively from CSV data).
- **12_dashboard_methodology.png** — methodology page (REFERENCE only — slide 9 should render concentration table natively from JSON).

**Rule for screenshots:** only `09_dashboard_main.png` should be embedded in the deck (slide 11, dashboard CTA). The other three are visual references so Claude Design knows what the dashboard looks like, but slides 7, 8, 9, 10 should render charts/tables natively from the underlying data — this matches the deck's visual style and avoids embedding tall screenshots.

---

## Upload workflow

1. Open claude.ai in browser → start a new chat
2. Drag all 12 files (excluding this README) into the chat
3. Paste the TRACE prompt (provided separately)
4. Answer the 3 setup questions Claude Design will ask (team names, dashboard URL, anything ambiguous)
5. Iterate through 4 batches: slides 1–3 (with gate at slide 3), 4–7, 8–11, A1–A5
6. Export to PDF via browser print

Total bundle size: ~4.4 MB. Well within claude.ai upload limits.
