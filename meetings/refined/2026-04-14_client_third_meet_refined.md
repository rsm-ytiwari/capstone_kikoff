# Refined Meeting Notes — 2026-04-14 Client Meeting (Week 3)
**Attendees:** Yash Tiwari, Chunjiang Liu, Shivang Bhatt, Yoko He, Abheek Sinha (Kikoff sponsor), additional Kikoff team member(s)

---

## Facts Learned (confirmed information)

1. **"iso" is a typo for "iOS"** — treat those 4 rows as iOS. (Source: Abheek, ~32:14)

2. **"web and app" rows should be treated as "web"** — Abheek said platform disaggregation is not needed for those rows; treat as web for now, will confirm if needed. (Source: Abheek, ~33:22)

3. **Platform-level modeling is required (not channel-level aggregation)** — Different tactics, different scale by platform; channel-level aggregation would not be consumable from an implementation standpoint. (Source: Abheek/Chunjiang, ~45:37)

4. **Model should produce TWO outputs: conversion count AND revenue (LTV)** — Different channels drive different conversion volumes but also different revenue/LTV profiles (e.g., Meta may drive higher-premium users). Both outputs needed. (Source: Abheek, ~46:23)

5. **Total LTV is already pre-computed** — No need to multiply conversions by LTV. Average LTV = total LTV / conversions. (Source: Abheek, ~46:30)

6. **SPEND column is actual ad spend on the platform, not conversion values.** (Source: Abheek, ~28:43)

7. **SUBSCRIPTION_COUNT is volumetric (count), not a rate or dollar amount.** (Source: Abheek, ~29:53)

8. **LTV anomaly dates identified:**
   - 2024-02-29 through 2024-03-11: average LTV significantly below trend (backfilling error on data engineering side)
   - 2025-10-21 through 2025-10-24: average LTV way off
   - Recommended fix: average the LTV from the day before and after the bad window, apply uniformly across affected days. (Source: Abheek, ~35:20–37:58)

9. **LTV model has ~15-20% under-prediction bias** — predicted ~$117, actual ~$140. Driven by not accounting for plan upgrades within 30 days. Team does not need to model LTV internals; treat predicted LTV as given. (Source: Abheek, ~39:56)

10. **Choose either 1-year or 3-year LTV, but be consistent** — prorated; either works. (Source: Abheek/Shivang, ~31:17)

11. **Incrementality test details:**
    - **TikTok & Meta May 2025:** High confidence, narrow confidence range. These were platform-level conversion lift studies (user-level holdout). (Source: Abheek, ~13:44)
    - **Meta May 2025 design flaw:** Meta implemented a 3-cell strategy incorrectly — divided users into 3 cells of 33% each (by platform: Android/iOS/Web), then applied 10% holdout within each, then eligibility criteria. This severely restricted reach. iCAC results are still high-conviction, but conversion volume dipped during the test period and recovery took time. (Source: Abheek, ~15:00–20:00)
    - **Meta Jan 2026 (cancelled):** Same design flaw repeated. Reach impacted >50%. Paused within 3 days. Results still significant but should be included with wider confidence range (not excluded). (Source: Abheek, ~18:13–19:18)
    - **CTV:** Geo-based holdout (not user-level). Lower conviction than platform tests because IP/household-level mapping is imprecise — cannot control for household members seeing ads elsewhere. (Source: Abheek, ~23:48–26:34)

12. **Include Jan 2026 Meta test with high uncertainty / wider confidence range** — do not exclude it. (Source: Abheek, ~48:32)

13. **Channel taxonomy guidance from Abheek:**
    - Meta/Instagram → bucket under "Meta"; sub-split by platform (web, iOS, Android)
    - Programmatic DSPs → model separately (do not combine)
    - Apple → keep separate; do not bucket under mobile DSP (at least initially)
    - Audio/Spotify → separate from others
    - "Others" → check trend over time; if 9% is consistent across all years, treat as "Others"; if skewed toward 2024, less concern; if still ~9% recently, Abheek will advise further
    (Source: Abheek, ~44:01)

14. **Exclude April 2026 data** — only use complete months through March 2026. (Source: Abheek/Shivang, ~28:27)

15. **Abheek recommends against simple linear regression** — it won't capture diminishing returns. Bayesian approach important for incorporating priors (incrementality); without priors, iCAC estimates could be 2-3x off. (Source: Abheek, ~52:44–54:25)

16. **Next milestone from sponsor:** Spend ~2 weeks exploring different model types (pros/cons), rule out data discrepancies. Meridian is acceptable if team decides to use it. (Source: Abheek, ~55:33–56:34)

17. **Project submission: ~June 6, 2026.** (Source: Yash, ~55:45)

18. **Abheek available for async feedback** — tag him on weekends; he'll review Monday morning. Open to flexible meeting scheduling; may need to reschuffle last-minute due to hiring/onsites. (Source: Abheek, ~57:31–1:01:08)

19. **On-site visit possible** — team can visit Kikoff office when progress warrants it; Abheek may also visit campus. (Source: Abheek, ~1:01:16)

---

## Assumptions Changed or Created

| Assumption | Status | Detail |
|------------|--------|--------|
| Single dependent variable | **CHANGED** | Two model outputs needed: conversions AND revenue (LTV). Not a single DV. |
| Channels/tactics hierarchy unclear | **PARTIALLY RESOLVED** | Abheek provided initial channel taxonomy mapping. "Others" handling still TBD pending trend analysis. |
| Jan 2026 Meta test usability uncertain | **RESOLVED** | Include it with wider confidence range / high uncertainty. Do not exclude. |
| Platform-level modeling required | **NEW** | Abheek confirmed: model at channel × platform level, not aggregated channel level. |
| No major structural breaks | **UPDATE NEEDED** | Meta incrementality tests caused conversion dips during test windows (May 2025, Jan 2026). These are known structural disruptions that need handling. |
| Data cutoff | **RESOLVED** | Exclude April 2026; use through March 2026. |

---

## Decisions Made or Implied

1. **Model at channel × platform granularity** — not channel-level aggregates. This increases parameter space ~3x.
2. **Two model outputs: conversions + revenue (LTV)** — both needed for different insights (volume vs. value per channel).
3. **Include Jan 2026 Meta test as a prior with wider confidence** — do not drop it.
4. **LTV imputation approach for bad dates:** average surrounding good days and apply uniformly across affected window.
5. **"iso" → iOS; "web and app" → web** for data cleaning.
6. **Exclude April 2026 data from modeling** — cutoff is March 2026.
7. **Channel taxonomy:** Meta (by platform), separate programmatic DSPs, separate Apple, separate Audio/Spotify, Others TBD.
8. **Next 2 weeks: explore model types** (Meridian, other Bayesian MMM approaches), document pros/cons.

---

## Open Questions Surfaced

1. **"Others" category final disposition:** Need to analyze trend over time. If ~9% consistent, keep as-is. If concentrated in 2024, less concern. Abheek will advise further if needed.
2. **Which SOURCE_GROUP values map to "Programmatic DSP"?** Abheek said model them separately but didn't enumerate which of the 15 values are DSPs. Likely candidates: liftoff, Inmobidsp, Stackadapt, appvertiser, applovin(?).
3. **Specific SOURCE_GROUP → channel mapping table** — Abheek gave directional guidance but we need to draft a concrete mapping and get confirmation.
4. **How to handle conversion dips during Meta incrementality test windows** in the model? These are known structural disruptions.
5. **Model framework decision:** Meridian vs. PyMC-Marketing vs. other Bayesian MMM tools — pros/cons exploration needed.

---

## Answers Received to Prior Open Questions

### Q1: What is the primary dependent variable?
**Classification: FULLY ANSWERED**
**Answer:** Two outputs required: (1) conversion count and (2) revenue (LTV). Different channels drive different volume vs. value profiles. Both are needed.
**Proposed action:** Move to resolved_questions.md.

### Q3: How are "channels" and "tactics" defined?
**Classification: PARTIALLY ANSWERED**
**Update:** Abheek provided directional channel taxonomy: Meta (by platform), separate programmatic DSPs, separate Apple, separate Audio/Spotify, Others TBD. Platform-level modeling confirmed as required.
**Still open:** Need concrete SOURCE_GROUP → channel mapping table confirmed by Abheek. "Others" disposition depends on trend analysis. DSP grouping members unclear.

### Q9: What is the "Others" category?
**Classification: PARTIALLY ANSWERED**
**Update:** If 9% share is consistent across 2024-2026, keep as "Others" in model. If skewed to 2024, less concern. Abheek will get back if it's persistent at 9%.
**Still open:** Team needs to run the trend analysis and share with Abheek.

### Q10: Should platform splits be in the model?
**Classification: FULLY ANSWERED**
**Answer:** Yes. Model at channel × platform level. Aggregation would not be useful from implementation standpoint — different tactics and scale by platform.
**Proposed action:** Move to resolved_questions.md.

### Q11: Final data cutoff date?
**Classification: FULLY ANSWERED**
**Answer:** Exclude April 2026. Use through March 2026 (complete months only).
**Proposed action:** Move to resolved_questions.md.

### Q13 (Blocking): Is the Jan 2026 Meta lift study usable as a prior?
**Classification: FULLY ANSWERED**
**Answer:** Yes, include it but with wider confidence range / high uncertainty. Do not exclude.
**Proposed action:** Move to resolved_questions.md.

### Q8: Are there channels with known data quality issues?
**Classification: PARTIALLY ANSWERED**
**Update:** Meta tests caused conversion dips during test windows due to reach restriction. This is a known data quality / structural disruption, not a data error.
**Still open:** Are there other channels with similar issues?

### Q7: Are there known structural breaks in the time series?
**Classification: PARTIALLY ANSWERED**
**Update:** Meta incrementality test windows (May 2025, Jan 2026) caused material conversion dips. Jan 2026 had >50% reach impact.
**Still open:** Are there other breaks beyond incrementality test periods?
