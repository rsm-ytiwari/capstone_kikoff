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
    # P2_01 — PyMC-Marketing MMM Setup: Meta POC

    **Phase 2 | First model build**

    Goal: produce ICAC + ROAS curves for Meta (facebook_ios, facebook_android, facebook_web) as a proof-of-concept. Once this works, replicate for all other channels.

    **Decisions driving this notebook:**
    - D004 (2026-04-21): PyMC-Marketing selected; DSP taxonomy finalized; time-limited priors; Q3 2024+ start
    - D003 (2026-04-14): `LTV_1YEAR` as single target for POC — this is the total 1-year portfolio LTV for each day's acquired cohort (~$117/customer × ~1,712 customers/day); data cutoff March 2026

    **Guardrails:**
    - Adstock/saturation parameters marked *illustrative* — not final
    - Others/Idle excluded (Q18 still open)
    - Priors for channels without incrementality tests not set here
    """)
    return


@app.cell
def _():
    import sys
    import warnings
    warnings.filterwarnings('ignore')

    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates

    import pymc as pm
    import pymc_marketing
    from pymc_marketing.mmm import MMM, GeometricAdstock, LogisticSaturation
    from pymc_marketing.mmm.scaling import Scaling, DataDerivedScaling
    from pymc_marketing.prior import Prior
    import arviz as az

    print(f'pymc-marketing: {pymc_marketing.__version__}')
    print(f'pymc: {pm.__version__}')
    print(f'arviz: {az.__version__}')

    import os
    if os.path.basename(os.getcwd()) == 'notebooks':
        os.chdir('..')
    DATA_DIR = 'data'
    print(f'Working directory: {os.getcwd()}')
    return (
        DATA_DIR,
        DataDerivedScaling,
        GeometricAdstock,
        LogisticSaturation,
        MMM,
        Prior,
        Scaling,
        az,
        mdates,
        np,
        pd,
        plt,
        pm,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 1. Data Preprocessing

    All cleaning steps are new code — decisions were made in D003/D004 but not previously implemented.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 1a. Spend data
    """)
    return


@app.cell
def _(DATA_DIR, pd):
    spend_raw = pd.read_csv(
        f'{DATA_DIR}/MMM_PLATFORM_CHANNEL_DAILY_SPEND_2026-04-07-1111.csv',
        parse_dates=['DS']
    )
    print(f'Raw spend shape: {spend_raw.shape}')
    print(f'Columns: {spend_raw.columns.tolist()}')
    print(f'PLATFORM unique: {sorted(spend_raw["PLATFORM"].unique())}')
    print(f'SOURCE_GROUP unique: {sorted(spend_raw["SOURCE_GROUP"].unique())}')
    print(f'Date range: {spend_raw["DS"].min()} to {spend_raw["DS"].max()}')
    return (spend_raw,)


@app.cell
def _(pd, spend_raw):
    spend = spend_raw.copy()
    spend['PLATFORM'] = spend['PLATFORM'].replace({'iso': 'ios', 'web and app': 'web'})
    ios_android_mask = spend['PLATFORM'] == 'iOS and android'
    # 'iOS and android' rows: split 50/50 into separate ios + android rows.
    # NOTE: 50/50 split is an assumption — flag if Abheek has a better breakdown.
    if ios_android_mask.sum() > 0:
        ios_rows = spend[ios_android_mask].copy()
        android_rows = spend[ios_android_mask].copy()
        ios_rows['PLATFORM'] = 'ios'
        ios_rows['TOTAL_SPEND'] = ios_rows['TOTAL_SPEND'] / 2
        android_rows['PLATFORM'] = 'android'
        android_rows['TOTAL_SPEND'] = android_rows['TOTAL_SPEND'] / 2
        spend = pd.concat([spend[~ios_android_mask], ios_rows, android_rows], ignore_index=True)
        print(f'Split {ios_android_mask.sum()} iOS+Android rows 50/50 into ios + android')
    print(f"PLATFORM after recoding: {sorted(spend['PLATFORM'].unique())}")
    return (spend,)


@app.cell
def _(spend):
    # DSP mapping per D004: combine StackAdapt+Appvertiser, drop Bing, normalise Inmobidsp
    dsp_map = {'Stackadapt': 'dsp_combined', 'appvertiser': 'dsp_combined', 'Inmobidsp': 'inmobidsp'}
    spend['SOURCE_GROUP'] = spend['SOURCE_GROUP'].replace(dsp_map)
    spend_1 = spend[~spend['SOURCE_GROUP'].isin(['bing', 'Others'])]
    print(f"SOURCE_GROUP after mapping: {sorted(spend_1['SOURCE_GROUP'].unique())}")  # drop Bing (D004); Others (Q18 pending)
    return (spend_1,)


@app.cell
def _(pd, spend_1):
    # --- Date filter: Q3 2024 to March 2026 (per Abheek D004) ---
    MODEL_START = pd.Timestamp('2024-07-01')
    MODEL_END = pd.Timestamp('2026-03-31')
    spend_2 = spend_1[(spend_1['DS'] >= MODEL_START) & (spend_1['DS'] <= MODEL_END)]
    print(f"Date range after filter: {spend_2['DS'].min()} to {spend_2['DS'].max()}")
    print(f'Spend rows after filter: {len(spend_2)}')
    return MODEL_END, MODEL_START, spend_2


@app.cell
def _(spend_2):
    # --- Null spend rows ---
    null_spend = spend_2['TOTAL_SPEND'].isna().sum()
    print(f'Null TOTAL_SPEND rows: {null_spend}')
    spend_2['TOTAL_SPEND'] = spend_2['TOTAL_SPEND'].fillna(0.0)  # treat missing spend as zero
    # --- Aggregate: if DSP combine created duplicates, sum them ---
    spend_3 = spend_2.groupby(['DS', 'PLATFORM', 'SOURCE_GROUP'], as_index=False)['TOTAL_SPEND'].sum()
    return (spend_3,)


@app.cell
def _(spend_3):
    # --- Pivot to wide format: one column per channel_platform combo ---
    spend_3['col'] = spend_3['SOURCE_GROUP'] + '_' + spend_3['PLATFORM']
    spend_wide = spend_3.pivot_table(index='DS', columns='col', values='TOTAL_SPEND', aggfunc='sum', fill_value=0)
    spend_wide.columns.name = None
    spend_wide = spend_wide.reset_index().rename(columns={'DS': 'date'})
    print(f'Wide spend shape: {spend_wide.shape}')
    print(f'Columns (first 20): {spend_wide.columns.tolist()[:20]}')
    print(f"Date range: {spend_wide['date'].min()} to {spend_wide['date'].max()}")
    return (spend_wide,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 1b. Conversions + LTV data
    """)
    return


@app.cell
def _(DATA_DIR, pd):
    ltv_raw = pd.read_csv(
        f'{DATA_DIR}/MMM_DAILY_CONVENSIONS_LTV_2026-04-07-1304.csv',
        parse_dates=['DS']
    )
    print(f'LTV raw shape: {ltv_raw.shape}')
    print(f'Columns: {ltv_raw.columns.tolist()}')
    print(f'Date range: {ltv_raw["DS"].min()} to {ltv_raw["DS"].max()}')
    print(f'Null LTV_1YEAR rows: {ltv_raw["LTV_1YEAR"].isna().sum()}')
    return (ltv_raw,)


@app.cell
def _(MODEL_END, MODEL_START, ltv_raw):
    # --- Date filter ---
    ltv = ltv_raw[(ltv_raw['DS'] >= MODEL_START) & (ltv_raw['DS'] <= MODEL_END)].copy()
    ltv = ltv.rename(columns={'DS': 'date'})

    # Null imputation (known dates: 2024-03-09 / 2024-03-10 are outside Q3 2024+ window)
    null_ltv = ltv['LTV_1YEAR'].isna()
    if null_ltv.sum() > 0:
        print(f'Null LTV_1YEAR in model window: {ltv.loc[null_ltv, "date"].tolist()}')
        ltv['LTV_1YEAR'] = ltv['LTV_1YEAR'].interpolate(method='linear', limit=5)
        print(f'After imputation, nulls remaining: {ltv["LTV_1YEAR"].isna().sum()}')
    else:
        print('No null LTV_1YEAR in model window — no imputation needed')

    # Anomaly detection: z-score relative to 30-day rolling window
    rolling_stats = ltv['LTV_1YEAR'].rolling(window=30, center=True, min_periods=5).agg(['mean', 'std'])
    z_score    = (ltv['LTV_1YEAR'] - rolling_stats['mean']) / rolling_stats['std']
    anomaly_mask = z_score.abs() > 3
    anomalies  = ltv[anomaly_mask]
    print(f'\nAnomalous LTV rows (|z| > 3): {len(anomalies)}')
    if len(anomalies) > 0:
        print(anomalies[['date', 'CONVERSIONS', 'LTV_1YEAR']])
    return anomaly_mask, ltv


@app.cell
def _(anomaly_mask, ltv):
    if anomaly_mask.sum() > 0:
        rolling_median = ltv['LTV_1YEAR'].rolling(window=14, center=True, min_periods=5).median()
        ltv.loc[anomaly_mask, 'LTV_1YEAR'] = rolling_median[anomaly_mask]
        print('Smoothed anomalous LTV values with 14-day rolling median')

    # LTV_1YEAR = total predicted 1-year LTV for all customers acquired on that day.
    # Do NOT multiply by CONVERSIONS — it is already an aggregate (~$117/customer × ~1,712/day).
    ltv['LTV_PER_CUSTOMER'] = ltv['LTV_1YEAR'] / ltv['CONVERSIONS']

    print(f'\nConversions: mean={ltv["CONVERSIONS"].mean():.0f}/day')
    print(f'LTV_1YEAR (total cohort): mean=${ltv["LTV_1YEAR"].mean():.0f}/day')
    print(f'Per-customer LTV: mean=${ltv["LTV_PER_CUSTOMER"].mean():.2f}')
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 1c. Merge spend + conversions
    """)
    return


@app.cell
def _(MODEL_END, MODEL_START, ltv, pd, spend_wide):
    df = pd.merge(spend_wide, ltv[['date', 'CONVERSIONS', 'LTV_1YEAR', 'LTV_PER_CUSTOMER']], on='date', how='inner')
    df = df.sort_values('date').reset_index(drop=True)

    expected_days = (MODEL_END - MODEL_START).days + 1
    print(f'Merged rows: {len(df)} (expected ~{expected_days} days)')
    print(f'Date range: {df["date"].min().date()} to {df["date"].max().date()}')
    print(f'Missing dates: {expected_days - len(df)}')
    print(f'Null LTV_1YEAR: {df["LTV_1YEAR"].isna().sum()}')
    print(f'\nLTV_1YEAR stats: mean=${df["LTV_1YEAR"].mean():.0f}/day, min=${df["LTV_1YEAR"].min():.0f}, max=${df["LTV_1YEAR"].max():.0f}')
    return (df,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 2. Incrementality Priors

    **What this is:** Incrementality tests gave us iCAC (incremental customer acquisition cost) for specific channels during specific test windows. We use these to inform the saturation curve scale — how much revenue the model assigns to each channel.

    **Why it matters:** Without this calibration, the model might assign too much or too little credit to Meta vs. other channels. The incrementality tests are our most reliable ground truth.
    """)
    return


@app.cell
def _(pd):
    # Incrementality test windows and iCAC values (extracted from Kikoff_data_incrementality.csv)
    # Source: data audit 2026-04-26
    # KPI1 = incremental conversions, KPI2 = iCAC (spend / incremental conversions)
    incrementality_tests = {'tiktok': {'window': ('2025-08-22', '2025-09-15'), 'confidence': 'high', 'icac': {'ios': 108.83, 'android': 81.68, 'web': 112.12}, 'incremental_conversions': {'ios': 569, 'android': 651, 'web': 6215}}, 'facebook_may2025': {'channel': 'facebook', 'window': ('2025-05-06', '2025-05-14'), 'confidence': 'high', 'icac': {'ios': 135.48, 'android': 63.06, 'web': 156.89}, 'incremental_conversions': {'ios': 1156, 'android': 1405, 'web': 1128}}, 'facebook_jan2026': {'channel': 'facebook', 'window': ('2026-01-03', '2026-01-08'), 'confidence': 'low', 'icac': {'ios': 1350.0, 'android': 154.52, 'web': None}, 'note': 'Cancelled test — use very wide priors or skip iOS/web cells'}, 'ctv': {'window': ('2025-10-06', '2025-11-02'), 'confidence': 'medium', 'icac': {'all': 135.05}, 'incremental_conversions': {'all': 1840}, 'note': 'Half life = 6 (adstock hint for CTV)'}}
    META_ICAC = incrementality_tests['facebook_may2025']['icac']
    META_WINDOW_START = pd.Timestamp(incrementality_tests['facebook_may2025']['window'][0])
    META_WINDOW_END = pd.Timestamp(incrementality_tests['facebook_may2025']['window'][1])
    print('Meta May 2025 iCAC by platform:')  # clean holdout, 3-cell
    for _plat, val in META_ICAC.items():
        print(f'  {_plat}: ${val}')
    # For the Meta POC, use May 2025 test (high confidence) as primary prior calibration
    print(f'Test window: {META_WINDOW_START.date()} to {META_WINDOW_END.date()}')  # 99.9% confidence, 12% holdout  # CANCELLED; iOS 63% confidence; web iCAC missing  # iOS suspicious (10x vs May)  # 95% CI geo lift
    return META_ICAC, META_WINDOW_END, META_WINDOW_START


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 3. Time-Limited Priors — Approach (Q19)

    **The constraint from Abheek (2026-04-21):** Incrementality priors should apply ONLY within the test time window, not the entire model history.

    **Why this matters:** If we apply a tight prior globally, we're saying the model behaves like the test for all 21 months. But the test was 9 days in May 2025 — conditions may differ elsewhere.

    **PyMC-Marketing limitation:** The standard `MMM` class uses global priors on `saturation_beta` (the channel contribution scale). There is no built-in mechanism to constrain priors to a time window only.

    **Three options investigated:**
    1. `time_varying_media=True` — uses a Hilbert Space Gaussian Process that changes over time. Captures temporal variation but doesn't target specific test windows.
    2. **Two-stage / auxiliary model** — fit a mini-model on test-window data only, use posterior as prior in full model. Cleanest Bayesian interpretation but adds complexity.
    3. **Global informative prior calibrated from test window (POC approach)** — use the test iCAC to set `saturation_beta` prior. This is globally applied but calibrated from the test period. Less precise but practical for POC.

    **Decision for this POC:** Use option 3 (globally-applied informative prior). Mark parameters as *illustrative*.

    > ⚠️ **Decision Point:** The full model build should use option 2 (two-stage auxiliary model) for true time-limited priors. Flag for Keith at Monday 2026-04-27 meeting.
    """)
    return


@app.cell
def _(META_ICAC, META_WINDOW_END, META_WINDOW_START, df):
    # --- Translating iCAC to saturation_beta prior ---
    #
    # PyMC-Marketing LogisticSaturation: contribution = beta * (1 / (1 + exp(-lam * x)))
    # where x is adstocked spend (normalized).
    test_window_mask = (df['date'] >= META_WINDOW_START) & (df['date'] <= META_WINDOW_END)
    # At low saturation (x << 0): contribution ≈ beta * lam * x  (linear region)
    # iCAC = spend / incremental_conversions
    # ROAS ≈ 1 / iCAC  (if target = conversions; we use REVENUE so ROAS = LTV / iCAC)
    if test_window_mask.sum() > 0:
    # For POC: set saturation_beta priors using ROAS derived from iCAC.
    # This is an ILLUSTRATIVE approximation — not the final prior spec.
        avg_ltv_test = df.loc[test_window_mask, 'LTV_1YEAR'].mean()
    # Approximate LTV_1YEAR during test window for prior translation
        print(f'Average LTV_1YEAR during Meta May 2025 test window: ${avg_ltv_test:.2f}')
    else:
        avg_ltv_test = df['LTV_1YEAR'].mean()
        print(f'Test window not in model data — using overall avg LTV: ${avg_ltv_test:.2f}')
    print('\nImplied ROAS from May 2025 test (ROAS = LTV / iCAC):')
    for _plat, icac in META_ICAC.items():
        roas = avg_ltv_test / icac
    # Implied ROAS (revenue per $1 spend) from iCAC
        print(f'  facebook_{_plat}: ROAS ≈ {roas:.2f}x  (iCAC=${icac}, LTV=${avg_ltv_test:.0f}')
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 4. Meta POC Model

    Single-channel model: Meta only (facebook_ios, facebook_android, facebook_web).
    Target: REVENUE (LTV-weighted conversions) — single DV for POC.

    All adstock/saturation parameters are **illustrative** — final values pending corrected data and full prior spec.
    """)
    return


@app.cell
def _(df):
    # --- Feature matrix: Meta channels only ---
    META_CHANNELS = [c for c in df.columns if c.startswith('facebook_')]
    print(f'Meta channel columns: {META_CHANNELS}')

    # Verify these columns exist and have data
    for col in META_CHANNELS:
        nonzero = (df[col] > 0).sum()
        print(f'  {col}: {nonzero}/{len(df)} days with spend, mean=${df[col].mean():.0f}')
    return (META_CHANNELS,)


@app.cell
def _(META_CHANNELS, df):
    X = df[['date'] + META_CHANNELS].copy()
    y = df['LTV_1YEAR'].copy()

    print(f'X shape: {X.shape},  y shape: {y.shape}')
    print(f'y (LTV_1YEAR) stats: mean={y.mean():.0f}, std={y.std():.0f}, min={y.min():.0f}, max={y.max():.0f}')
    return X, y


@app.cell
def _(
    DataDerivedScaling,
    GeometricAdstock,
    LogisticSaturation,
    META_CHANNELS,
    MMM,
    Prior,
    Scaling,
):
    # --- Model configuration ---
    # ILLUSTRATIVE priors — not final.
    #
    # scaling: DataDerivedScaling(method="max") scales target and channels to [0,1] at fit time.
    # This makes the default prior range (intercept ~N(0,2), saturation_beta ~HalfNormal(2))
    # meaningful without needing data-specific prior adjustment.
    #
    # adstock_alpha: Beta(1,2) — modest carryover (EDA: 1-day optimal lag)
    # saturation_lam: Gamma(3,1) — moderate saturation shape (ILLUSTRATIVE)
    # saturation_beta: HalfNormal(2) — channel scale on unit-normalized data (ILLUSTRATIVE)
    # yearly_seasonality=2: 2 Fourier modes for tax-season peak (Jan-Apr ~1.7x baseline)

    adstock    = GeometricAdstock(l_max=14)
    saturation = LogisticSaturation()

    scaling = Scaling(
        target=DataDerivedScaling(method='max', dims=()),
        channel=DataDerivedScaling(method='max', dims=()),
    )

    model_config = {
        'intercept':       Prior('Normal', mu=0, sigma=2),
        'likelihood':      Prior('Normal', sigma=Prior('HalfNormal', sigma=2)),
        'adstock_alpha':   Prior('Beta', alpha=1, beta=2),      # ILLUSTRATIVE
        'saturation_lam':  Prior('Gamma', alpha=3, beta=1),     # ILLUSTRATIVE
        'saturation_beta': Prior('HalfNormal', sigma=2),        # ILLUSTRATIVE — calibrate from iCAC in full build
        'gamma_fourier':   Prior('Laplace', mu=0, b=1),
    }

    mmm = MMM(
        date_column='date',
        channel_columns=META_CHANNELS,
        adstock=adstock,
        saturation=saturation,
        yearly_seasonality=2,
        scaling=scaling,
        model_config=model_config,
    )

    print('MMM object created successfully')
    print(f'Channel columns: {mmm.channel_columns}')
    return (mmm,)


@app.cell
def _(X, df, mdates, mmm, np, plt, pm, y):
    # --- Prior predictive check (sanity check before inference) ---
    # build_model sets mmm.model; then use mmm.model as the PyMC context.
    mmm.build_model(X, y)
    with mmm.model:
        prior_pred = pm.sample_prior_predictive(samples=200, random_seed=42)
    target_max = y.max()
    prior_y_scaled = prior_pred.prior_predictive['y'].values.squeeze()
    # On scaled data: prior predictive 'y' is in [0,1] scale.
    # We scale back to original units for the plot.
    prior_y = prior_y_scaled * target_max
    _fig, _ax = plt.subplots(figsize=(12, 4))
    _ax.plot(df['date'], y.values, color='black', linewidth=1.5, label='Observed LTV_1YEAR', zorder=3)
    _ax.fill_between(df['date'], np.percentile(prior_y, 5, axis=0), np.percentile(prior_y, 95, axis=0), alpha=0.3, color='steelblue', label='Prior predictive 90% CI')
    _ax.set_title('Prior Predictive Check — LTV_1YEAR\n(ILLUSTRATIVE priors — CI should loosely bracket observed)', fontsize=12)
    _ax.set_ylabel('Daily Cohort LTV ($)')
    _ax.legend()
    _ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    plt.tight_layout()
    plt.show()
    print(f'Observed range: [{y.min():.0f}, {y.max():.0f}]')
    print(f'Prior predictive 5-95% range: [{np.percentile(prior_y, 5).min():.0f}, {np.percentile(prior_y, 95).max():.0f}]')
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 5. Model Inference

    Running NUTS sampler. Tune=1000, draws=1000. This will take 10-20 minutes.

    50% accuracy bar is acceptable (per Abheek, 2026-04-21) — focus is on ROAS direction and relative channel rankings, not precise fit.
    """)
    return


@app.cell
def _(X, mmm, y):
    idata = mmm.fit(
        X, y,
        tune=1000,
        draws=1000,
        chains=2,
        target_accept=0.9,
        random_seed=42,
        progressbar=True,
    )
    print('Sampling complete')
    return (idata,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 6. Diagnostics

    Pass criteria:
    - R-hat < 1.05 for all parameters
    - ESS > 400 for all parameters
    - Posterior predictive coverage looks reasonable
    """)
    return


@app.cell
def _(az, idata):
    # R-hat and ESS
    summary = az.summary(idata, var_names=['intercept', 'adstock_alpha', 'saturation_lam', 'saturation_beta'])
    print('=== Posterior Summary ===')
    print(summary[['mean', 'sd', 'hdi_3%', 'hdi_97%', 'r_hat', 'ess_bulk']].to_string())

    rhat_max = summary['r_hat'].max()
    ess_min  = summary['ess_bulk'].min()
    print(f'\nMax R-hat: {rhat_max:.3f}  (pass if < 1.05)')
    print(f'Min ESS:   {ess_min:.0f}  (pass if > 400)')
    print('PASS' if rhat_max < 1.05 and ess_min > 400 else 'REVIEW NEEDED — check trace plots')
    return


@app.cell
def _(az, idata, plt):
    # Trace plots for key parameters
    az.plot_trace(idata, var_names=['adstock_alpha', 'saturation_beta'], compact=True)
    plt.suptitle('Trace Plots — Meta POC (ILLUSTRATIVE)', y=1.02)
    plt.tight_layout()
    plt.show()
    return


@app.cell
def _(X, df, idata, mdates, mmm, np, plt, y):
    mmm.sample_posterior_predictive(X, extend_idata=True, combined=True)
    post_y = idata.posterior_predictive['y'].values.reshape(-1, len(y))
    p5, _p50, p95 = np.percentile(post_y, [5, 50, 95], axis=0)
    _fig, _ax = plt.subplots(figsize=(14, 4))
    _ax.plot(df['date'], y.values, color='black', linewidth=1.5, label='Observed', zorder=3)
    _ax.fill_between(df['date'], p5, p95, alpha=0.3, color='steelblue', label='Posterior predictive 90% CI')
    _ax.plot(df['date'], _p50, color='steelblue', linewidth=1, alpha=0.7, label='Posterior median')
    _ax.set_title('Posterior Predictive Check — LTV_1YEAR\n(Meta POC, ILLUSTRATIVE priors)', fontsize=12)
    _ax.set_ylabel('Daily Cohort LTV ($)')
    _ax.legend()
    _ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    plt.tight_layout()
    plt.show()
    return


@app.cell
def _(mmm, plt):
    # Channel contributions over time
    _fig = mmm.plot_components_contributions()
    _fig.suptitle('Channel Contributions Over Time — Meta POC (ILLUSTRATIVE)', fontsize=12, y=1.01)
    plt.tight_layout()
    plt.show()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 7. ICAC + ROAS Response Curves

    These are the key deliverables per Abheek (2026-04-21):
    - ICAC and ROAS **at different spend levels** (response curves)
    - ICAC and ROAS **over time**

    > ⚠️ All curves are **ILLUSTRATIVE** — priors not yet calibrated from incrementality tests. Direction of curves (saturation shape, relative ordering) is the meaningful output at this stage.
    """)
    return


@app.cell
def _(META_CHANNELS, mmm, plt):
    # --- Response curves: ROAS vs. spend level ---
    # PyMC-Marketing built-in: plots contribution (revenue) vs. spend
    # We derive ROAS = contribution / spend
    _fig = mmm.plot_direct_contribution_curves(show_fit=False, channels=META_CHANNELS)
    _fig.suptitle('Meta Channel Contribution Curves (ILLUSTRATIVE)\nHigher spend → diminishing returns', y=1.02)
    plt.tight_layout()
    plt.show()
    return


@app.cell
def _(idata, mmm):
    import inspect

    # Reveal the exact saturation formula (needed to build curves manually)
    print('=== LogisticSaturation.function source ===')
    print(inspect.getsource(type(mmm.saturation).function))

    # Confirm posterior variable names and shapes
    print('\n=== Posterior variables ===')
    for _var in list(idata.posterior.data_vars):
        print(f'  {_var}: {idata.posterior[_var].dims}  shape={idata.posterior[_var].values.shape}')

    # Confirm channel coordinate name in saturation_beta
    print('\n=== saturation_beta dims/coords ===')
    print(idata.posterior['saturation_beta'].dims)
    print(idata.posterior['saturation_beta'].coords)
    return


@app.cell
def _(META_CHANNELS, df, idata, mmm, np, y):
    _y_max = float(y.max())

    _spend_daily = df.set_index('date')
    weekly_spend = {
        ch: _spend_daily[ch].resample('W').sum()
        for ch in META_CHANNELS
    }
    median_52wk_weekly_spend = {
        ch: weekly_spend[ch].median()
        for ch in META_CHANNELS
    }

    avg_per_customer_ltv = float(df['LTV_PER_CUSTOMER'].mean())
    print(f'Avg per-customer LTV: ${avg_per_customer_ltv:.2f}')
    print(f'Target y_max (inverse transform scale): ${_y_max:.0f}')

    # Confirmed from pre-flight: beta * (1 - exp(-lam*x)) / (1 + exp(-lam*x))
    def _sat_fn(x_norm, lam, beta):
        return beta * (1 - np.exp(-lam * x_norm)) / (1 + np.exp(-lam * x_norm))

    forward_pass_cache = {}
    for _ch in META_CHANNELS:
        _ch_max_daily = float(df[_ch].max())
        _x_daily = np.linspace(0, _ch_max_daily * 2, 200)
        _x_weekly = _x_daily * 7
        _x_norm = _x_daily / _ch_max_daily

        def _curve_at_q(_q, _ch=_ch, _x_norm=_x_norm, _x_daily=_x_daily):
            _lam_s = idata.posterior['saturation_lam'].sel(channel=_ch).values.ravel()
            _beta_s = idata.posterior['saturation_beta'].sel(channel=_ch).values.ravel()
            _lam_q  = float(np.quantile(_lam_s, _q))
            _beta_q = float(np.quantile(_beta_s, _q))
            return _sat_fn(_x_norm, _lam_q, _beta_q) * _y_max

        _c_p10, _c_p50, _c_p90 = _curve_at_q(0.10), _curve_at_q(0.50), _curve_at_q(0.90)

        _roas_p50 = np.where(_x_daily > 0, _c_p50 / _x_daily, np.nan)
        _roas_p10 = np.where(_x_daily > 0, _c_p10 / _x_daily, np.nan)
        _roas_p90 = np.where(_x_daily > 0, _c_p90 / _x_daily, np.nan)

        _icac_p50 = _x_daily / np.maximum(_c_p50 / avg_per_customer_ltv, 1e-9)
        _icac_p10 = _x_daily / np.maximum(_c_p90 / avg_per_customer_ltv, 1e-9)  # flipped
        _icac_p90 = _x_daily / np.maximum(_c_p10 / avg_per_customer_ltv, 1e-9)  # flipped

        forward_pass_cache[_ch] = {
            'x_fit_daily': _x_daily,
            'x_fit_weekly': _x_weekly,
            'roas': (_roas_p10, _roas_p50, _roas_p90),
            'icac': (_icac_p10, _icac_p50, _icac_p90),
        }
        print(f'{_ch}: cache built | 52-wk median weekly spend ${median_52wk_weekly_spend[_ch]:,.0f}')

    _contribs_ts = mmm.compute_mean_contributions_over_time(original_scale=True)
    _ts = df[['date'] + META_CHANNELS].copy()
    for _ch in META_CHANNELS:
        _ts[f'{_ch}_contrib'] = _contribs_ts[_ch].values
    _ts = _ts.set_index('date')

    weekly_ts = _ts.resample('W').sum()
    for _ch in META_CHANNELS:
        weekly_ts[f'{_ch}_roas'] = np.where(
            weekly_ts[_ch] > 0,
            weekly_ts[f'{_ch}_contrib'] / weekly_ts[_ch],
            np.nan
        )
        weekly_ts[f'{_ch}_icac'] = np.where(
            weekly_ts[f'{_ch}_contrib'] > 0,
            weekly_ts[_ch] / (weekly_ts[f'{_ch}_contrib'] / avg_per_customer_ltv),
            np.nan
        )
    print(f'weekly_ts: {len(weekly_ts)} weeks ({weekly_ts.index.min().date()} to {weekly_ts.index.max().date()})')
    return (
        forward_pass_cache,
        median_52wk_weekly_spend,
        weekly_spend,
        weekly_ts,
    )


@app.cell
def _(
    META_CHANNELS,
    forward_pass_cache,
    median_52wk_weekly_spend,
    np,
    plt,
    weekly_spend,
):
    _fig, _axes = plt.subplots(1, len(META_CHANNELS), figsize=(6 * len(META_CHANNELS), 5))
    _axes = np.atleast_1d(_axes)

    for _ax, _ch in zip(_axes, META_CHANNELS):
        _cache = forward_pass_cache[_ch]
        _x_wk  = _cache['x_fit_weekly']
        _r10, _r50, _r90 = _cache['roas']
        _med_wk = median_52wk_weekly_spend[_ch]

        _ax.plot(_x_wk, _r50, color='steelblue', linewidth=2, label='Median iROAS', zorder=3)
        _ax.fill_between(_x_wk, _r10, _r90, alpha=0.2, color='steelblue', label='80% CI', zorder=2)
        _ax.axvline(_med_wk, color='navy', linestyle='--', linewidth=1.5,
                   label=f'52-wk median (${_med_wk:,.0f}/wk)')

        _ax_hist = _ax.twinx()
        _ax_hist.hist(weekly_spend[_ch].values, bins=np.linspace(0, _x_wk.max(), 25),
                     color='lightgray', alpha=0.5, zorder=1, edgecolor='none')
        _ax_hist.set_ylabel('Weeks observed', color='gray', fontsize=7)
        _ax_hist.tick_params(axis='y', labelcolor='gray', labelsize=6)
        _ax_hist.set_ylim(0, _ax_hist.get_ylim()[1] * 5)
        _ax.set_zorder(_ax_hist.get_zorder() + 1)
        _ax.patch.set_visible(False)
        _ax.set_xlabel('Weekly Spend ($)')
        _ax.set_ylabel('iROAS')
        _ax.set_title(f'iROAS Response Curve — {_ch}\n(ILLUSTRATIVE)', fontsize=10)
        _ax.legend(fontsize=7, loc='upper right')

    plt.suptitle('Meta iROAS Response Curves — Weekly Spend Basis (ILLUSTRATIVE)', y=1.02)
    plt.tight_layout()
    plt.savefig('data/debug_roas_response_curves.png', bbox_inches='tight', dpi=100)
    plt.show()
    return


@app.cell
def _(
    META_CHANNELS,
    META_ICAC,
    forward_pass_cache,
    median_52wk_weekly_spend,
    np,
    plt,
    weekly_spend,
):
    _fig, _axes = plt.subplots(1, len(META_CHANNELS), figsize=(6 * len(META_CHANNELS), 5))
    _axes = np.atleast_1d(_axes)

    for _ax, _ch in zip(_axes, META_CHANNELS):
        _cache = forward_pass_cache[_ch]
        _x_wk  = _cache['x_fit_weekly']
        _i10, _i50, _i90 = _cache['icac']
        _med_wk = median_52wk_weekly_spend[_ch]
        _plat   = _ch.replace('facebook_', '')

        _ax.plot(_x_wk, _i50, color='darkorange', linewidth=2, label='Median iCAC', zorder=3)
        _ax.fill_between(_x_wk, _i10, _i90, alpha=0.2, color='darkorange', label='80% CI', zorder=2)
        _ax.axvline(_med_wk, color='navy', linestyle='--', linewidth=1.5,
                   label=f'52-wk median (${_med_wk:,.0f}/wk)')

        _test_icac = META_ICAC.get(_plat)
        if _test_icac:
            _ax.axhline(_test_icac, color='green', linestyle=':', linewidth=1.5,
                       label=f'May 2025 test iCAC (${_test_icac})')

        _ax_hist = _ax.twinx()
        _ax_hist.hist(weekly_spend[_ch].values, bins=np.linspace(0, _x_wk.max(), 25),
                     color='lightgray', alpha=0.5, zorder=1, edgecolor='none')
        _ax_hist.set_ylabel('Weeks observed', color='gray', fontsize=7)
        _ax_hist.tick_params(axis='y', labelcolor='gray', labelsize=6)
        _ax_hist.set_ylim(0, _ax_hist.get_ylim()[1] * 5)
        _ax.set_zorder(_ax_hist.get_zorder() + 1)
        _ax.patch.set_visible(False)
        _ax.set_xlabel('Weekly Spend ($)')
        _ax.set_ylabel('iCAC ($)')
        _ax.set_title(f'iCAC Response Curve — {_ch}\n(ILLUSTRATIVE)', fontsize=10)
        _ax.legend(fontsize=7, loc='upper right')

    plt.suptitle('Meta iCAC Response Curves — Weekly Spend Basis (ILLUSTRATIVE)', y=1.02)
    plt.tight_layout()
    plt.savefig('data/debug_icac_response_curves.png', bbox_inches='tight', dpi=100)
    plt.show()
    print('Gap between curve and green benchmark = prior calibration needed before final build.')
    return


@app.cell
def _(META_CHANNELS, mdates, np, plt, weekly_ts):
    _fig, _axes = plt.subplots(len(META_CHANNELS), 1, figsize=(14, 4 * len(META_CHANNELS)), sharex=True)
    _axes = np.atleast_1d(_axes)

    for _ax, _ch in zip(_axes, META_CHANNELS):
        _roas_wk = weekly_ts[f'{_ch}_roas']
        _spend_wk = weekly_ts[_ch]
        _med_r = _roas_wk.median(skipna=True)

        _ax.plot(_roas_wk.index, _roas_wk.values, color='steelblue', linewidth=1.5, label='Weekly iROAS')
        _ax.axhline(_med_r, color='steelblue', linestyle='--', linewidth=1, alpha=0.7,
                   label=f'Median {_med_r:.2f}x')
        _ax.set_ylabel('iROAS', color='steelblue')
        _ax.tick_params(axis='y', labelcolor='steelblue')

        _ax2 = _ax.twinx()
        _ax2.plot(_spend_wk.index, _spend_wk.values / 1e3, color='gray', linewidth=1.2,
                 linestyle='--', alpha=0.7, label='Weekly Spend ($K)')
        _ax2.set_ylabel('Weekly Spend ($K)', color='gray')
        _ax2.tick_params(axis='y', labelcolor='gray')

        _ax.set_title(f'iROAS Over Time — {_ch} (ILLUSTRATIVE, Weekly)', fontsize=10)
        _lines_l, _labs_l = _ax.get_legend_handles_labels()
        _lines_r, _labs_r = _ax2.get_legend_handles_labels()
        _ax.legend(_lines_l + _lines_r, _labs_l + _labs_r, fontsize=7, loc='upper right')

    _axes[-1].xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    plt.suptitle('Meta iROAS Over Time — Weekly Basis (ILLUSTRATIVE)', y=1.01)
    plt.tight_layout()
    plt.savefig('data/debug_roas_over_time.png', bbox_inches='tight', dpi=100)
    plt.show()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 8. iCAC Over Time

    Weekly iCAC = weekly_spend / (weekly_contribution / avg_LTV_per_customer).
    Dual-axis: left = iCAC ($), right = weekly spend ($K).
    Green dotted line = May 2025 incrementality test benchmark.

    > ⚠️ ILLUSTRATIVE — priors not yet calibrated.
    """)
    return


@app.cell
def _(META_CHANNELS, META_ICAC, mdates, np, plt, weekly_ts):
    _fig, _axes = plt.subplots(len(META_CHANNELS), 1, figsize=(14, 4 * len(META_CHANNELS)), sharex=True)
    _axes = np.atleast_1d(_axes)

    for _ax, _ch in zip(_axes, META_CHANNELS):
        _icac_wk  = weekly_ts[f'{_ch}_icac']
        _spend_wk = weekly_ts[_ch]
        _med_i    = _icac_wk.median(skipna=True)
        _icac_plot = _icac_wk.clip(upper=_icac_wk.quantile(0.95) * 2)

        _ax.plot(_icac_plot.index, _icac_plot.values, color='darkorange', linewidth=1.5, label='Weekly iCAC')
        _ax.axhline(_med_i, color='darkorange', linestyle='--', linewidth=1, alpha=0.7,
                   label=f'Median ${_med_i:,.0f}')

        _plat = _ch.replace('facebook_', '')
        _test_icac = META_ICAC.get(_plat)
        if _test_icac:
            _ax.axhline(_test_icac, color='green', linestyle=':', linewidth=1.5,
                       label=f'May 2025 test ${_test_icac}')

        _ax.set_ylabel('iCAC ($)', color='darkorange')
        _ax.set_ylim(bottom=0)
        _ax.tick_params(axis='y', labelcolor='darkorange')

        _ax2 = _ax.twinx()
        _ax2.plot(_spend_wk.index, _spend_wk.values / 1e3, color='gray', linewidth=1.2,
                 linestyle='--', alpha=0.7, label='Weekly Spend ($K)')
        _ax2.set_ylabel('Weekly Spend ($K)', color='gray')
        _ax2.tick_params(axis='y', labelcolor='gray')

        _ax.set_title(f'iCAC Over Time — {_ch} (ILLUSTRATIVE, Weekly)', fontsize=10)
        _lines_l, _labs_l = _ax.get_legend_handles_labels()
        _lines_r, _labs_r = _ax2.get_legend_handles_labels()
        _ax.legend(_lines_l + _lines_r, _labs_l + _labs_r, fontsize=7, loc='upper right')

    _axes[-1].xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    plt.suptitle('Meta iCAC Over Time — Weekly Basis (ILLUSTRATIVE)', y=1.01)
    plt.tight_layout()
    plt.savefig('data/debug_icac_over_time.png', bbox_inches='tight', dpi=100)
    plt.show()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 9. Decisioning Table (Milestone 2)

    Translates model outputs into structured channel recommendations.

    | Column | Derivation |
    |---|---|
    | Current Spend Signal | Last 4-week avg vs 52-week median (ratio: <0.5=low, 0.5–0.85=moderate, 0.85–1.15=high, >1.15=very high) |
    | iCAC Trend | Last 5-week median vs 52-week median iCAC (direction + %) |
    | iROAS Trend | iROAS at current spend from response curve; direction from 5-week vs 52-week |
    | Trust/Confidence | CI width (p90–p10)/p50 at current spend: <0.5=green, 0.5–1.0=yellow, >1.0=red |
    | Saturation Read | ROAS(current)/ROAS(50% current): >0.85=intact, 0.70–0.85=early, <0.70=saturated |
    | Recommended Action | Rule table combining spend signal + saturation + trust |
    | Spend Move to Test % | Directional from recommended action |

    > ⚠️ ILLUSTRATIVE — thresholds are starting points, not calibrated benchmarks.
    """)
    return


@app.cell
def _(META_CHANNELS, forward_pass_cache, np, weekly_ts):
    _L52 = min(52, len(weekly_ts))
    _L5  = min(5,  len(weekly_ts))
    _L4  = min(4,  len(weekly_ts))

    channel_stats = {}
    for _ch in META_CHANNELS:
        _roas_wk  = weekly_ts[f'{_ch}_roas'].dropna()
        _icac_wk  = weekly_ts[f'{_ch}_icac'].dropna()
        _spend_wk = weekly_ts[_ch]
        _cache    = forward_pass_cache[_ch]
        _x_wk     = _cache['x_fit_weekly']
        _r10, _r50, _r90 = _cache['roas']

        _avg_4wk = _spend_wk.iloc[-_L4:].mean()
        channel_stats[_ch] = dict(
            avg_spend_4wk  = _avg_4wk,
            med_spend_52wk = _spend_wk.iloc[-_L52:].median(),
            med_roas_52wk  = _roas_wk.iloc[-_L52:].median(),
            med_icac_52wk  = _icac_wk.iloc[-_L52:].median(),
            med_roas_5wk   = _roas_wk.iloc[-_L5:].median(),
            med_icac_5wk   = _icac_wk.iloc[-_L5:].median(),
            roas_curr_p50  = float(np.interp(_avg_4wk, _x_wk, _r50)),
            roas_curr_p10  = float(np.interp(_avg_4wk, _x_wk, _r10)),
            roas_curr_p90  = float(np.interp(_avg_4wk, _x_wk, _r90)),
            roas_half_p50  = float(np.interp(_avg_4wk * 0.5, _x_wk, _r50)),
        )
        print(f'{_ch}: 4wk avg spend ${_avg_4wk:,.0f} | curr iROAS p50={channel_stats[_ch]["roas_curr_p50"]:.2f}x')
    return (channel_stats,)


@app.cell
def _(META_CHANNELS, channel_stats, pd):
    def _spend_signal(avg, med):
        r = avg / med if med else 0
        return 'low' if r < 0.50 else 'moderate' if r < 0.85 else 'high' if r < 1.15 else 'very high'

    def _icac_trend(now, hist):
        pct = (now - hist) / hist * 100 if hist else 0
        return f'${now:,.0f} ({"up" if pct > 0 else "down"} {abs(pct):.0f}% vs 52wk)'

    def _iroas_trend(curr_p50, roas_5wk, roas_52wk):
        pct = (roas_5wk - roas_52wk) / roas_52wk * 100 if roas_52wk else 0
        return f'{curr_p50:.2f}x ({"improving" if pct > 0 else "declining"} {abs(pct):.0f}% vs 52wk)'

    def _trust(p10, p50, p90):
        ratio = (p90 - p10) / p50 if p50 else 99
        return 'green' if ratio < 0.5 else 'yellow' if ratio < 1.0 else 'red'

    def _saturation(curr, half):
        r = curr / half if half else 0
        return 'marginal efficiency intact' if r > 0.85 else 'early saturation' if r > 0.70 else 'saturated'

    def _action(sig, sat, tr):
        if tr == 'red': return 'Hold'
        if sat == 'saturated' or sig == 'very high': return 'Scale back'
        if sat == 'early saturation': return 'Maintain'
        if sig in ('low', 'moderate') and sat == 'marginal efficiency intact': return 'Scale & Test'
        return 'Maintain'

    def _spend_move(act, sig):
        return {
            'Scale & Test': '+15%' if sig == 'moderate' else '+20%',
            'Scale back':   '-10% to -20%',
            'Hold':         '0% (insufficient confidence)',
            'Maintain':     '0% (+/-5% test)',
        }.get(act, '0%')

    _rows = []
    for _ch in META_CHANNELS:
        _s  = channel_stats[_ch]
        _sg = _spend_signal(_s['avg_spend_4wk'], _s['med_spend_52wk'])
        _it = _icac_trend(_s['med_icac_5wk'], _s['med_icac_52wk'])
        _rt = _iroas_trend(_s['roas_curr_p50'], _s['med_roas_5wk'], _s['med_roas_52wk'])
        _tr = _trust(_s['roas_curr_p10'], _s['roas_curr_p50'], _s['roas_curr_p90'])
        _sa = _saturation(_s['roas_curr_p50'], _s['roas_half_p50'])
        _ac = _action(_sg, _sa, _tr)
        _sm = _spend_move(_ac, _sg)
        _rows.append({
            'Channel': _ch, 'Current Spend Signal': _sg, 'iCAC Trend': _it,
            'iROAS Trend': _rt, 'Trust/Confidence': _tr, 'Saturation Read': _sa,
            'Recommended Action': _ac, 'Spend Move to Test %': _sm,
        })

    decisioning_table = pd.DataFrame(_rows).set_index('Channel')
    decisioning_table.to_csv('data/debug_decisioning_table.csv')
    print('> ⚠️ ILLUSTRATIVE — thresholds are starting points, not calibrated benchmarks.')
    print(decisioning_table.to_string())
    return (decisioning_table,)


@app.cell
def _(decisioning_table):
    # .map() not .applymap() — applymap deprecated in pandas >= 2.1
    styled = (decisioning_table.style
        .map(lambda v: {
            'green':  'background-color:#d4edda',
            'yellow': 'background-color:#fff3cd',
            'red':    'background-color:#f8d7da',
        }.get(v, ''), subset=['Trust/Confidence'])
        .map(lambda v: {
            'Scale & Test': 'background-color:#d4edda;font-weight:bold',
            'Scale back':   'background-color:#f8d7da;font-weight:bold',
            'Hold':         'background-color:#fff3cd',
        }.get(v, ''), subset=['Recommended Action'])
        .set_caption('Decisioning Table — Meta POC (ILLUSTRATIVE)')
    )
    styled
    return


if __name__ == "__main__":
    app.run()
