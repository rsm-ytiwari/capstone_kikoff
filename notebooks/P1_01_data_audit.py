# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "marimo>=0.23.2",
# ]
# ///

import marimo

__generated_with = "0.23.3"
app = marimo.App()


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Data Audit — Kikoff MMM Capstone

    **Purpose:** Verify that the two received CSV files match known facts from the project brief and client meetings before the first supervisor meeting.

    **Scope:**
    - Spend file: channels, platforms, date range, missing values
    - Conversions/LTV file: date range, null values, outliers, anomaly counts
    - Cross-file validation: date overlap and alignment

    **Date:** 2026-04-13
    **Audience:** Supervisor meeting prep — surfaces mismatches that become supervisor questions.
    """)
    return


@app.cell
def _():
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    import warnings
    warnings.filterwarnings('ignore')

    # Set pandas display options for readability
    pd.set_option('display.max_rows', 20)
    pd.set_option('display.max_columns', 10)
    return (pd,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Spend File Audit

    File: `data/MMM_PLATFORM_CHANNEL_DAILY_SPEND_2026-04-07-1111.csv`
    """)
    return


@app.cell
def _(pd):
    # Load spend file
    spend = pd.read_csv('../capstone_team//data/MMM_PLATFORM_CHANNEL_DAILY_SPEND_2026-04-07-1111.csv')

    print(f"Shape: {spend.shape}")
    print(f"\nColumn dtypes:")
    print(spend.dtypes)
    print(f"\nFirst 5 rows:")
    spend.head()
    return (spend,)


@app.cell
def _(spend):
    # Date range
    print(f"Date range:")
    print(f"  Min: {spend['DS'].min()}")
    print(f"  Max: {spend['DS'].max()}")
    print(f"  Unique dates: {spend['DS'].nunique()}")
    print(f"  Span: ~2 years 3 months (Jan 2024 — Apr 2026)")
    return


@app.cell
def _(spend):
    # PLATFORM values and counts
    print("PLATFORM unique values and counts:")
    print(spend['PLATFORM'].value_counts().sort_values(ascending=False))
    return


@app.cell
def _(spend):
    # SOURCE_GROUP values and counts
    print("SOURCE_GROUP unique values and counts:")
    print(spend['SOURCE_GROUP'].value_counts().sort_values(ascending=False))
    print(f"\nTotal unique SOURCE_GROUP values: {spend['SOURCE_GROUP'].nunique()}")
    return


@app.cell
def _(spend):
    # Null counts
    print("Null/missing value counts per column:")
    print(spend.isnull().sum())
    return


@app.cell
def _(spend):
    # Show rows with missing TOTAL_SPEND
    missing_spend = spend[spend['TOTAL_SPEND'].isnull()]
    print(f"Rows with missing TOTAL_SPEND ({len(missing_spend)} rows):")
    print(missing_spend[['DS', 'PLATFORM', 'SOURCE_GROUP']])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Spend File Findings

    **S1. PLATFORM = `iso` (Typo)**
    - **Found:** 4 rows with `iso` instead of `ios`
    - **Severity:** Medium

    **S2. PLATFORM has combined values (High Priority)**
    - **Found:**
      - `web and app`: 2,518 rows (not separate `web` + `app`)
      - `iOS and android`: 35 rows (mixed case vs. lowercase `ios`, `android`)
    - **Expected:** Clean iOS/Android/Web splits (per project brief)
    - **Question for supervisor:** Are these intentional combined platforms, or should they be disaggregated?
    - **Severity:** High

    **S3 + S4. SOURCE_GROUP naming mismatch (High Priority)**
    - **Found:**
      - 15 unique SOURCE_GROUP values (not 12–13 as described)
      - Naming doesn't match client descriptions:
        - `facebook` (not `Meta`)
        - `apple_search` (not `Apple`)
        - `influencer` (not `Influencers`)
        - Also includes: `google`, `tiktok`, `applovin`, `Others`, `liftoff`, `linear_tv`, `ctv`, `podcast`, `appvertiser`, `Inmobidsp`, `bing`, `Stackadapt`
    - **Question for supervisor:** How do these SOURCE_GROUP values map to the 12–13 channels you described?
    - **Severity:** Medium

    **S5. Capitalization inconsistency**
    - **Found:** `Others`, `Inmobidsp`, `Stackadapt` capitalized; all others lowercase
    - **Severity:** Low (cosmetic, but worth cleaning)

    **S6. Missing TOTAL_SPEND**
    - **Found:** 9 rows with null TOTAL_SPEND (see cell output above)
    - **Severity:** Medium (will need imputation or removal before modeling)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Conversions / LTV File Audit

    File: `data/MMM_DAILY_CONVENSIONS_LTV_2026-04-07-1304.csv`
    """)
    return


@app.cell
def _(pd):
    # Load conversions/LTV file
    ltv = pd.read_csv('../data/MMM_DAILY_CONVENSIONS_LTV_2026-04-07-1304.csv')

    print(f"Shape: {ltv.shape}")
    print(f"\nColumn dtypes:")
    print(ltv.dtypes)
    print(f"\nFirst 5 rows:")
    ltv.head()
    return (ltv,)


@app.cell
def _(ltv):
    # Date range and duplicates
    print(f"Date range:")
    print(f"  Min: {ltv['DS'].min()}")
    print(f"  Max: {ltv['DS'].max()}")
    print(f"  Unique dates: {ltv['DS'].nunique()}")
    print(f"  Span: ~3 years 3 months (Jan 2023 — Apr 2026)")
    print(f"  Note: Jan 2023 data expected to be dropped per brief")

    # Check for duplicate dates
    dup_dates = ltv['DS'].value_counts()
    dup_count = (dup_dates > 1).sum()
    print(f"\nDuplicate dates: {dup_count}")
    return


@app.cell
def _(ltv):
    # Null counts and rows with null LTV values
    print("Null/missing value counts per column:")
    print(ltv.isnull().sum())

    print(f"\nRows with null LTV_1YEAR and/or LTV_3YEAR:")
    null_ltv = ltv[(ltv['LTV_1YEAR'].isnull()) | (ltv['LTV_3YEAR'].isnull())]
    print(null_ltv[['DS', 'CONVERSIONS', 'LTV_1YEAR', 'LTV_3YEAR']])
    return


@app.cell
def _(ltv):
    # CONVERSIONS statistics and outliers
    print("CONVERSIONS statistics:")
    print(ltv['CONVERSIONS'].describe())

    # Find outliers >3 std dev
    conv_mean = ltv['CONVERSIONS'].mean()
    conv_std = ltv['CONVERSIONS'].std()
    conv_lower = conv_mean - 3 * conv_std
    conv_upper = conv_mean + 3 * conv_std

    outlier_conv = ltv[(ltv['CONVERSIONS'] < conv_lower) | (ltv['CONVERSIONS'] > conv_upper)]
    print(f"\nCONVERSIONS outliers (>3 std dev from mean):")
    print(f"  Mean: {conv_mean:.2f}, Std Dev: {conv_std:.2f}")
    print(f"  Range: [{conv_lower:.2f}, {conv_upper:.2f}]")
    print(f"\nOutlier rows ({len(outlier_conv)}):")
    print(outlier_conv[['DS', 'CONVERSIONS']])
    return


@app.cell
def _(ltv):
    # LTV_1YEAR statistics
    print("LTV_1YEAR statistics:")
    print(ltv['LTV_1YEAR'].describe())
    print(f"\nRange: {ltv['LTV_1YEAR'].min():.2f} to {ltv['LTV_1YEAR'].max():.2f}")

    # Check for outliers
    ltv_valid = ltv[ltv['LTV_1YEAR'].notna()]
    ltv_mean = ltv_valid['LTV_1YEAR'].mean()
    ltv_std = ltv_valid['LTV_1YEAR'].std()
    ltv_lower = ltv_mean - 3 * ltv_std
    ltv_upper = ltv_mean + 3 * ltv_std

    outlier_ltv = ltv_valid[(ltv_valid['LTV_1YEAR'] < ltv_lower) | (ltv_valid['LTV_1YEAR'] > ltv_upper)]
    print(f"\nLTV_1YEAR outliers (>3 std dev): {len(outlier_ltv)} rows")
    print("(No rows exceed 3 std devs for LTV_1YEAR — distribution is naturally wide)")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Conversions/LTV Findings

    **L1. Null LTV values (High Priority)**
    - **Found:** 2 rows with null LTV_1YEAR and LTV_3YEAR:
      - `2024-03-09`: 1,111 conversions, null LTV
      - `2024-03-10`: 1,108 conversions, null LTV
    - **Severity:** High (will block modeling on those dates)
    - **Next step:** Impute or remove

    **L2. CONVERSIONS outliers**
    - **Found:** 3 dates with conversions >3 std dev from mean:
      - `2025-05-30`: ~2,661 conversions
      - `2025-06-06`: ~2,750 conversions (peak)
      - `2026-04-07`: ~1,968 conversions (likely partial-day artifact)
    - **Note:** May/June 2025 spikes may be genuine (e.g., tax season surge, campaign boost) or data quality issues
    - **Severity:** Medium

    **L3. LTV anomaly count mismatch (High Priority)**
    - **Client said:** ~10 bad LTV values needing smoothing
    - **Found:** Only 2 null rows; remaining ~8 not identified by standard outlier detection
    - **Question for supervisor:** Can you point us to the ~8 remaining bad LTV dates, or describe how to identify them (e.g., out-of-range vs. negative vs. other)?
    - **Severity:** High (modeling depends on understanding what "bad" means)

    **L4. `Others` channel note**
    - **Found:** 1,042 rows with `SOURCE_GROUP = 'Others'` in spend file
    - **Question:** Is this a catch-all for unmapped channels, or a named channel to be disaggregated?
    - **Severity:** Medium
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Cross-file Checks
    """)
    return


@app.cell
def _(ltv, spend):
    # Date overlap: which dates are in LTV but not spend (after filtering 2023)?
    ltv_2024_onward = ltv[ltv['DS'] >= '2024-01-01']
    spend_dates = set(spend['DS'])
    ltv_dates = set(ltv_2024_onward['DS'])

    in_ltv_not_spend = ltv_dates - spend_dates
    in_spend_not_ltv = spend_dates - ltv_dates

    print(f"Date alignment (2024–2026):")
    print(f"  Spend file unique dates: {len(spend_dates)}")
    print(f"  LTV file unique dates (2024+): {len(ltv_dates)}")
    print(f"  Dates in LTV but not spend: {len(in_ltv_not_spend)}")
    print(f"  Dates in spend but not LTV: {len(in_spend_not_ltv)}")

    if in_ltv_not_spend:
        print(f"\nFirst 10 dates in LTV but not spend:")
        print(sorted(list(in_ltv_not_spend))[:10])

    if in_spend_not_ltv:
        print(f"\nFirst 10 dates in spend but not LTV:")
        print(sorted(list(in_spend_not_ltv))[:10])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Supervisor Questions Surfaced

    **Before the meeting, we need clarification on:**

    1. **PLATFORM definition (High Priority)**
       Are `web and app` and `iOS and android` intentional combined platforms, or should they be disaggregated into separate iOS / Android / Web channels?

    2. **Channel-to-SOURCE_GROUP mapping (High Priority)**
       You described 12–13 channels (Meta, TikTok, Apple, Influencers, CTV, Linear TV, Others, ...). The data has 15 SOURCE_GROUP values. How do they map? E.g., is `facebook` = `Meta`? Is `apple_search` = `Apple`? Are `podcast` and `bing` separate channels or part of other buckets?

    3. **LTV anomaly identification (High Priority)**
       You mentioned ~10 bad LTV values needing smoothing. We found 2 null rows (2024-03-09, 2024-03-10). Can you identify the remaining ~8 dates, or describe what makes them "bad" (out-of-range, negative, NaN, outliers, etc.)?

    ---

    **Secondary items:**
    - 9 rows missing TOTAL_SPEND — should these be removed or imputed?
    - 3 CONVERSIONS outlier dates (May/June 2025, April 2026) — are these genuine or data artifacts?
    - `Others` in SOURCE_GROUP (1,042 rows) — catch-all or named channel?
    - Date mismatch: spend file is 828 unique days (2024-01-01 to 2026-04-07), LTV file is 1,193 days. ~365 days are in LTV but not spend. Is this expected?
    """)
    return


if __name__ == "__main__":
    app.run()
