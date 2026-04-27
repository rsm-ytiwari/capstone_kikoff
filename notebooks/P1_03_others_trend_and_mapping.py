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
    # Channel Analysis: Others Trend & SOURCE_GROUP Mapping
    **Date:** 2026-04-21 | **Phase 1 EDA** | **Kikoff MMM Capstone**

    Prepared for client meeting with Abheek. Three analyses:
    1. **Others category trend** — is the ~9% spend share stable or growing?
    2. **Full channel spend breakdown** — all 15 SOURCE_GROUP values ranked
    3. **SOURCE_GROUP → channel mapping** — draft based on April 14 guidance, for confirmation
    """)
    return


@app.cell
def _():
    import pandas as pd
    import matplotlib.pyplot as plt

    spend = pd.read_csv('../data/MMM_PLATFORM_CHANNEL_DAILY_SPEND_2026-04-07-1111.csv', parse_dates=['DS'])
    spend = spend[(spend['DS'] >= '2024-01-01') & (spend['DS'] <= '2026-03-31')]
    spend['quarter'] = spend['DS'].dt.to_period('Q').astype(str)
    print(f'Loaded {len(spend):,} rows | Date range: {spend.DS.min().date()} to {spend.DS.max().date()}')
    print(f'SOURCE_GROUP unique values: {spend.SOURCE_GROUP.nunique()}')
    return pd, plt, spend


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 1. Others Category Trend

    **Context:** Abheek said (April 14) — *"If ~9% share is consistent across 2024–2026, keep as Others. If skewed, less concern."*

    **Finding: Others is NOT consistent — it grew from <1% to 14% in 4 quarters (15x increase).**
    """)
    return


@app.cell
def _(plt, spend):
    # Others share trend by quarter
    quarterly = spend.groupby(['quarter', 'SOURCE_GROUP'])['TOTAL_SPEND'].sum().reset_index()
    quarterly_total = spend.groupby('quarter')['TOTAL_SPEND'].sum().reset_index()
    quarterly_total.columns = ['quarter', 'total_quarterly_spend']
    quarterly = quarterly.merge(quarterly_total, on='quarter')
    quarterly['share_pct'] = quarterly['TOTAL_SPEND'] / quarterly['total_quarterly_spend'] * 100
    others = quarterly[quarterly['SOURCE_GROUP'] == 'Others'].sort_values('quarter')
    _fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    ax1.bar(others['quarter'], others['share_pct'], color='#e74c3c', alpha=0.8)
    ax1.set_title('"Others" Share of Total Spend by Quarter', fontweight='bold')
    ax1.set_ylabel('Share (%)')
    ax1.tick_params(axis='x', rotation=45)
    for _, r in others.iterrows():
        ax1.annotate(f"{r['share_pct']:.1f}%", xy=(r['quarter'], r['share_pct']), ha='center', va='bottom', fontweight='bold')
    ax2.bar(others['quarter'], others['TOTAL_SPEND'] / 1000000.0, color='#e74c3c', alpha=0.8)
    ax2.set_title('"Others" Absolute Spend ($M)', fontweight='bold')
    ax2.set_ylabel('Spend ($M)')
    ax2.tick_params(axis='x', rotation=45)
    for _, r in others.iterrows():
        ax2.annotate(f"${r['TOTAL_SPEND'] / 1000000.0:.1f}M", xy=(r['quarter'], r['TOTAL_SPEND'] / 1000000.0), ha='center', va='bottom', fontweight='bold')
    plt.tight_layout()
    plt.show()
    print('Others grew from 0.95% ($137K) in 2025-Q1 to 14.01% ($4.4M) in 2026-Q1.')
    print('This is now the 4th largest channel by spend.')
    return (quarterly,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 2. Full Channel Spend Breakdown

    All 15 SOURCE_GROUP values ranked by total spend share (Jan 2024 – Mar 2026).
    """)
    return


@app.cell
def _(plt, spend):
    total = spend.groupby('SOURCE_GROUP')['TOTAL_SPEND'].sum().reset_index()
    grand_total = total['TOTAL_SPEND'].sum()
    total['share_pct'] = (total['TOTAL_SPEND'] / grand_total * 100).round(2)
    total = total.sort_values('share_pct', ascending=False)
    _fig, _ax = plt.subplots(figsize=(12, 6))
    colors = ['#3498db' if sg != 'Others' else '#e74c3c' for sg in total['SOURCE_GROUP']]
    _ax.barh(total['SOURCE_GROUP'][::-1], total['share_pct'][::-1], color=colors[::-1], alpha=0.85)
    _ax.set_title('SOURCE_GROUP Share of Total Spend', fontweight='bold')
    _ax.set_xlabel('Share (%)')
    plt.tight_layout()
    plt.show()
    print(f'Total spend: $128.5M')
    print(f'Top 3 (facebook + tiktok + google): 66.8%')
    print(f'Bottom 5 combined: 1.7%')
    return (total,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 3. Quarterly Channel Mix Heatmap

    How channel mix shifted over time. Key patterns:
    - Linear TV dominated early 2024, then Facebook/TikTok/Google took over
    - Others emerged in 2025-Q2 and is accelerating
    - InMobi DSP appeared in 2025-Q3 and is growing
    """)
    return


@app.cell
def _(plt, quarterly, total):
    pivot = quarterly.pivot_table(index='SOURCE_GROUP', columns='quarter', values='share_pct', fill_value=0)
    pivot = pivot.reindex(total['SOURCE_GROUP'].values)
    _fig, _ax = plt.subplots(figsize=(14, 8))
    im = _ax.imshow(pivot.values, cmap='YlOrRd', aspect='auto')
    _ax.set_xticks(range(len(pivot.columns)))
    _ax.set_xticklabels(pivot.columns, rotation=45, ha='right')
    _ax.set_yticks(range(len(pivot.index)))
    _ax.set_yticklabels(pivot.index)
    for i in range(len(pivot.index)):
        for j in range(len(pivot.columns)):
            val = pivot.values[i, j]
            if val > 0:
                _ax.text(j, i, f'{val:.1f}%', ha='center', va='center', fontsize=8, color='white' if val > 15 else 'black')
    _ax.set_title('Channel Spend Share by Quarter (%)', fontweight='bold')
    plt.colorbar(im, ax=_ax, label='Share %', shrink=0.8)
    plt.tight_layout()
    plt.show()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 4. Proposed SOURCE_GROUP → Channel Mapping

    Based on Abheek's guidance (April 14):
    - Meta → keep as Meta, split by platform (iOS, Android, Web)
    - Programmatic DSPs → model separately
    - Apple → separate (not under mobile DSP)
    - Audio/Podcast → separate from others
    - Others → needs breakdown (see trend above)

    **Status:** Draft — needs Abheek's confirmation.
    """)
    return


@app.cell
def _(pd):
    # Proposed mapping table
    mapping = pd.DataFrame({
        'SOURCE_GROUP': ['facebook','tiktok','google','Others','linear_tv','applovin','ctv',
                         'apple_search','podcast','liftoff','Inmobidsp','influencer',
                         'appvertiser','bing','Stackadapt'],
        'Proposed_Channel': ['Meta','TikTok','Google','NEEDS BREAKDOWN','Linear TV',
                             'AppLovin (DSP)','CTV','Apple Search','Audio/Podcast',
                             'Liftoff (DSP)','InMobi (DSP)','Influencer',
                             'Appvertiser (DSP)','Bing/Microsoft','StackAdapt (DSP)'],
        'Category': ['Major','Major','Major','REVIEW','Traditional','Programmatic DSP',
                     'Traditional','App Store','Audio','Programmatic DSP','Programmatic DSP',
                     'Influencer','Programmatic DSP','Search','Programmatic DSP'],
        'Spend_Share_%': [35.36,18.37,13.04,9.08,5.62,4.30,4.24,4.15,2.39,1.78,1.15,0.42,0.05,0.05,0.02],
        'Has_Incrementality_Test': ['Yes (May25, Jan26)','Yes (Aug-Sep25)','No','No','No',
                                    'No','Yes (Oct-Nov25)','No','No','No','No','No','No','No','No']
    })
    print(mapping.to_string(index=False))
    print()
    print('QUESTIONS FOR ABHEEK:')
    print('1. What channels are inside "Others"? (14% of spend and growing fast)')
    print('2. Confirm: model each DSP separately or group as "Programmatic"?')
    print('3. Tiny channels (appvertiser 0.05%, bing 0.05%, Stackadapt 0.02%): drop or keep?')
    print('4. Does this mapping look correct for the remaining channels?')
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## Summary & Questions for This Meeting

    ### Key Finding
    **Others is not a stable residual** — it grew from <1% to 14% of total spend in 4 quarters (now $4.4M/quarter). Modeling it as a single channel would hide real signal.

    ### Confirmations Needed
    1. **What's inside Others?** Which channels/sources does this category contain? Can we get a breakdown?
    2. **Channel mapping review** — does our proposed mapping above look correct?
    3. **DSP treatment** — model AppLovin, Liftoff, InMobi, etc. each as separate channels, or group?
    4. **Tiny channels** — appvertiser (0.05%), bing (0.05%), Stackadapt (0.02%) — drop, keep, or fold into Others?

    ### Status Update
    - Data cleaning rules defined (LTV imputation, platform fixes, April 2026 exclusion) — applying this week
    - Framework exploration started (Meridian vs PyMC-Marketing) — recommendation by ~April 28
    - Channel mapping is the remaining blocker before we can finalize data preprocessing
    """)
    return


if __name__ == "__main__":
    app.run()
