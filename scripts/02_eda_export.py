#!/usr/bin/env python
"""
Run full EDA analysis and save all outputs to outputs/P1_02_eda/.

Usage (from project root):
    my-notebook-project/.venv/bin/python scripts/02_eda_export.py

Claude runs this to regenerate all EDA outputs without the user opening Marimo.
Outputs: figures/*.png, tables/*.csv, metrics/*.json
"""
import sys
import warnings
warnings.filterwarnings('ignore')

import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent.parent))
from src.config import (
    SPEND_FILE,
    LTV_FILE,
    OUT_P1_EDA,
)

plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette('husl')
plt.rcParams['figure.figsize'] = (14, 6)
plt.rcParams['font.size'] = 10


def save_fig(name, dpi=150):
    plt.savefig(OUT_P1_EDA / "figures" / name, dpi=dpi, bbox_inches='tight')
    plt.close()
    print(f"  saved figures/{name}")


# --- Load data ---
print("Loading data...")
spend_df = pd.read_csv(SPEND_FILE, parse_dates=['DS'])
ltv_df = pd.read_csv(LTV_FILE, parse_dates=['DS'])
ltv_df = ltv_df[ltv_df['DS'] >= '2024-01-01'].copy()

# M1 LTV imputation — must run before any figure uses LTV_1YEAR
# First pass: z-score detection, replace |z| > 3 with 14-day rolling median
_roll = ltv_df['LTV_1YEAR'].rolling(window=30, center=True, min_periods=5).agg(['mean', 'std'])
_z = (ltv_df['LTV_1YEAR'] - _roll['mean']) / _roll['std']
_anomaly = _z.abs() > 3
if _anomaly.sum() > 0:
    _med14 = ltv_df['LTV_1YEAR'].rolling(window=14, center=True, min_periods=5).median()
    ltv_df.loc[_anomaly, 'LTV_1YEAR'] = _med14[_anomaly]
# Second pass: targeted patch for Oct 2025 window (first pass leaves z=2.81 residual)
_oct = (ltv_df['DS'] >= '2025-10-21') & (ltv_df['DS'] <= '2025-10-24')
_med14 = ltv_df['LTV_1YEAR'].rolling(window=14, center=True, min_periods=5).median()
ltv_df.loc[_oct, 'LTV_1YEAR'] = _med14[_oct]

daily_df = spend_df.groupby('DS')['TOTAL_SPEND'].sum().reset_index()
daily_df = daily_df.merge(ltv_df, on='DS', how='inner')
daily_df['REVENUE'] = daily_df['LTV_1YEAR']  # total cohort LTV per day, not per-customer

MODEL_START = pd.Timestamp('2024-07-01')
MODEL_END   = pd.Timestamp('2026-03-31')
mw_df = daily_df[(daily_df['DS'] >= MODEL_START) & (daily_df['DS'] <= MODEL_END)].copy()

print(f"Spend: {spend_df.shape} | LTV (2024+): {ltv_df.shape} | Daily combined: {daily_df.shape} | Modeling window: {mw_df.shape}")

# --- Key metrics (metrics/summary.json) ---
print("\nComputing key metrics...")
spend_by_channel = spend_df.groupby('SOURCE_GROUP')['TOTAL_SPEND'].sum().sort_values(ascending=False)
top3_pct = spend_by_channel.head(3).sum() / spend_by_channel.sum() * 100

lag_corrs_all = []
for lag in range(0, 22):
    if lag < len(daily_df):
        r = daily_df['TOTAL_SPEND'].iloc[:-lag if lag > 0 else None].reset_index(drop=True).corr(
            daily_df['CONVERSIONS'].iloc[lag:].reset_index(drop=True))
        lag_corrs_all.append((lag, r))
best_lag, best_r = max(lag_corrs_all, key=lambda x: x[1])
carryover_lags = [(lag, r) for lag, r in lag_corrs_all if lag >= 1]
best_carryover_lag, best_carryover_r = max(carryover_lags, key=lambda x: x[1])

metrics = {
    'date_range': {
        'spend_start': str(spend_df['DS'].min().date()),
        'spend_end': str(spend_df['DS'].max().date()),
        'ltv_start': str(ltv_df['DS'].min().date()),
        'ltv_end': str(ltv_df['DS'].max().date()),
    },
    'spend': {
        'total': float(spend_by_channel.sum()),
        'daily_avg': float(daily_df['TOTAL_SPEND'].mean()),
        'top3_channels': spend_by_channel.head(3).index.tolist(),
        'top3_pct': float(top3_pct),
    },
    'conversions': {
        'mean_daily': float(ltv_df['CONVERSIONS'].mean()),
        'peak': float(ltv_df['CONVERSIONS'].max()),
        'peak_date': str(ltv_df.loc[ltv_df['CONVERSIONS'].idxmax(), 'DS'].date()),
        'ltv_nulls': int(ltv_df['LTV_1YEAR'].isna().sum()),
    },
    'lag_analysis': {
        'best_lag_days': int(best_lag),
        'peak_correlation': float(best_r),
        'best_carryover_lag_days': int(best_carryover_lag),
        'best_carryover_correlation': float(best_carryover_r),
    },
}
json.dump(metrics, open(OUT_P1_EDA / "metrics" / "summary.json", 'w'), indent=2)
print(f"  saved metrics/summary.json")

# --- Tables ---
print("\nSaving tables...")
spend_by_channel.reset_index().rename(columns={'TOTAL_SPEND': 'total_spend'}).to_csv(
    OUT_P1_EDA / "tables" / "spend_by_channel.csv", index=False)
print(f"  saved tables/spend_by_channel.csv")

channel_taxonomy = pd.DataFrame([
    {'SOURCE_GROUP': 'facebook',    'Channel': 'Meta',           'Model treatment': 'Separate — iOS / Android / Web'},
    {'SOURCE_GROUP': 'google',      'Channel': 'Google Search',  'Model treatment': 'Separate — iOS / Android / Web'},
    {'SOURCE_GROUP': 'tiktok',      'Channel': 'TikTok',         'Model treatment': 'Separate — iOS / Android / Web'},
    {'SOURCE_GROUP': 'applovin',    'Channel': 'DSP: Applovin',  'Model treatment': 'Separate (D004)'},
    {'SOURCE_GROUP': 'liftoff',     'Channel': 'DSP: Liftoff',   'Model treatment': 'Separate (D004)'},
    {'SOURCE_GROUP': 'Inmobidsp',   'Channel': 'DSP: InMobi',    'Model treatment': 'Separate (D004)'},
    {'SOURCE_GROUP': 'Stackadapt',  'Channel': 'DSP: Combined',  'Model treatment': 'Grouped with Appvertiser (D004)'},
    {'SOURCE_GROUP': 'appvertiser', 'Channel': 'DSP: Combined',  'Model treatment': 'Grouped with StackAdapt (D004)'},
    {'SOURCE_GROUP': 'linear_tv',   'Channel': 'Linear TV',      'Model treatment': 'Separate'},
    {'SOURCE_GROUP': 'ctv',         'Channel': 'CTV',            'Model treatment': 'Separate'},
    {'SOURCE_GROUP': 'podcast',     'Channel': 'Podcast / Audio','Model treatment': 'Separate'},
    {'SOURCE_GROUP': 'apple_search','Channel': 'Apple Search Ads','Model treatment': 'Separate'},
    {'SOURCE_GROUP': 'influencer',  'Channel': 'Influencers',    'Model treatment': 'Separate'},
    {'SOURCE_GROUP': 'bing',        'Channel': '(excluded)',     'Model treatment': 'Dropped — too small (D004)'},
    {'SOURCE_GROUP': 'Others',      'Channel': 'Idle / Others',  'Model treatment': 'Excluded — Q18 resolved (erroneous data removed 2026-04-27)'},
])
channel_taxonomy.to_csv(OUT_P1_EDA / "tables" / "channel_taxonomy.csv", index=False)
print(f"  saved tables/channel_taxonomy.csv")

icroas_df = pd.DataFrame([
    {'Channel': 'TikTok',     'Platform': 'iOS',     'iCAC': 108.83},
    {'Channel': 'TikTok',     'Platform': 'Android', 'iCAC': 81.68},
    {'Channel': 'TikTok',     'Platform': 'Web',     'iCAC': 112.12},
    {'Channel': 'Meta (May)', 'Platform': 'iOS',     'iCAC': 135.48},
    {'Channel': 'Meta (May)', 'Platform': 'Android', 'iCAC': 63.06},
    {'Channel': 'Meta (May)', 'Platform': 'Web',     'iCAC': 156.89},
    {'Channel': 'CTV',        'Platform': 'All',     'iCAC': 135.00},
])
icroas_df.to_csv(OUT_P1_EDA / "tables" / "icac_by_channel_platform.csv", index=False)
print(f"  saved tables/icac_by_channel_platform.csv")

# --- Figures ---
print("\nGenerating figures...")

# 1. Total daily spend
fig, ax = plt.subplots(figsize=(14, 6))
daily_spend = spend_df.groupby('DS')['TOTAL_SPEND'].sum()
ax.plot(daily_spend.index, daily_spend.values, alpha=0.5, color='gray', label='Daily spend')
ax.plot(daily_spend.index, daily_spend.rolling(30).mean(), linewidth=2.5, color='navy', label='30-day avg')
ax.set_title('Total Daily Spend Over Time', fontsize=13, fontweight='bold')
ax.set_ylabel('Daily Spend ($)')
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
save_fig("total_daily_spend.png")

# 2. Channel composition (monthly stacked bar) — explicit distinct color map
CHANNEL_COLORS = {
    'facebook':    '#1877F2',  # Meta blue
    'tiktok':      '#FF004F',  # TikTok red-pink
    'google':      '#34A853',  # Google green
    'linear_tv':   '#FF8C00',  # Dark orange
    'ctv':         '#8B5CF6',  # Purple
    'Others':      '#DC2626',  # Alert red — flagged category
    'applovin':    '#0EA5E9',  # Sky blue
    'liftoff':     '#06B6D4',  # Cyan
    'podcast':     '#F59E0B',  # Amber
    'apple_search':'#6B7280',  # Gray
    'Stackadapt':  '#10B981',  # Emerald
    'appvertiser': '#A78BFA',  # Lavender
    'influencer':  '#EC4899',  # Pink
    'Inmobidsp':   '#14B8A6',  # Teal
    'bing':        '#94A3B8',  # Slate (excluded, rarely visible)
}
spend_monthly = spend_df.groupby([pd.Grouper(key='DS', freq='ME'), 'SOURCE_GROUP'])['TOTAL_SPEND'].sum().unstack(fill_value=0)
spend_monthly_pct = spend_monthly.div(spend_monthly.sum(axis=1), axis=0) * 100
# Reorder columns: top channels first, Others last for visual clarity
col_order = spend_df.groupby('SOURCE_GROUP')['TOTAL_SPEND'].sum().sort_values(ascending=False).index.tolist()
col_order = [c for c in col_order if c != 'Others'] + (['Others'] if 'Others' in spend_monthly_pct.columns else [])
spend_monthly_pct = spend_monthly_pct[[c for c in col_order if c in spend_monthly_pct.columns]]
colors = [CHANNEL_COLORS.get(c, '#CCCCCC') for c in spend_monthly_pct.columns]
fig, ax = plt.subplots(figsize=(16, 6))
spend_monthly_pct.plot(kind='bar', stacked=True, ax=ax, width=0.85, color=colors)
ax.set_title('Channel Composition Over Time (% of Monthly Spend)', fontsize=13, fontweight='bold')
ax.set_ylabel('% of Monthly Spend')
ax.legend(title='Channel', bbox_to_anchor=(1.01, 1), loc='upper left', fontsize=8,
          ncol=1, framealpha=0.9)
ax.set_xticklabels([d.strftime('%Y-%m') for d in spend_monthly_pct.index], rotation=45, ha='right')
ax.axvline(spend_monthly_pct.index.get_loc(pd.Timestamp('2024-07-31')), color='black',
           linestyle='--', linewidth=1.5, alpha=0.6, label='_nolegend_')
ax.text(spend_monthly_pct.index.get_loc(pd.Timestamp('2024-07-31')) + 0.3,
        101, '← Modeling window', fontsize=8, color='black', alpha=0.7)
plt.tight_layout()
save_fig("channel_composition_monthly.png")

# 3. Top 10 channels by spend
top_channels = spend_df.groupby('SOURCE_GROUP')['TOTAL_SPEND'].sum().sort_values(ascending=True).tail(10)
fig, ax = plt.subplots(figsize=(10, 6))
top_channels.plot(kind='barh', ax=ax, color='steelblue')
ax.set_title('Top 10 Channels by Total Spend', fontsize=13, fontweight='bold')
for i, v in enumerate(top_channels.values):
    ax.text(v, i, f' ${v:,.0f}', va='center', fontsize=9)
plt.tight_layout()
save_fig("top_10_channels_spend.png")

# 4. Daily conversions
fig, ax = plt.subplots(figsize=(14, 6))
ax.plot(ltv_df['DS'], ltv_df['CONVERSIONS'], alpha=0.5, color='gray', label='Daily')
ax.plot(ltv_df['DS'], ltv_df['CONVERSIONS'].rolling(30).mean(), linewidth=2.5, color='darkgreen', label='30-day avg')
outlier_threshold = ltv_df['CONVERSIONS'].mean() + 3 * ltv_df['CONVERSIONS'].std()
for _, row in ltv_df[ltv_df['CONVERSIONS'] > outlier_threshold].iterrows():
    ax.plot(row['DS'], row['CONVERSIONS'], 'ro', markersize=8)
ax.set_title('Daily Conversions Over Time (red = >3σ outlier)', fontsize=13, fontweight='bold')
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
save_fig("daily_conversions.png")

# 5. LTV per conversion
fig, ax = plt.subplots(figsize=(14, 6))
ax.plot(ltv_df['DS'], ltv_df['LTV_1YEAR'], alpha=0.6, color='darkorange', label='LTV_1YEAR')
ax.plot(ltv_df['DS'], ltv_df['LTV_1YEAR'].rolling(30).mean(), linewidth=2.5, color='darkred', label='30-day avg')
for _, row in ltv_df[ltv_df['LTV_1YEAR'].isna()].iterrows():
    ax.axvline(row['DS'], color='red', linestyle='--', alpha=0.5, linewidth=2)
ax.set_title('Daily Cohort LTV_1YEAR Over Time (red dashes = nulls)', fontsize=13, fontweight='bold')
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
save_fig("ltv_per_conversion.png")

# 6. Conversions & revenue (modeling window only)
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
ax1.plot(mw_df['DS'], mw_df['CONVERSIONS'], alpha=0.6, color='green')
ax1.plot(mw_df['DS'], mw_df['CONVERSIONS'].rolling(30).mean(), linewidth=2.5, color='darkgreen')
ax1.set_title('Conversions Over Time (Q3 2024 – Mar 2026)', fontsize=12, fontweight='bold')
ax1.grid(True, alpha=0.3)
ax2.plot(mw_df['DS'], mw_df['REVENUE'], alpha=0.6, color='purple')
ax2.plot(mw_df['DS'], mw_df['REVENUE'].rolling(30).mean(), linewidth=2.5, color='indigo')
ax2.set_title('Daily Cohort LTV — total 1-year LTV of customers acquired that day', fontsize=12, fontweight='bold')
ax2.set_ylabel('Daily LTV ($)')
ax2.grid(True, alpha=0.3)
plt.tight_layout()
save_fig("conversions_and_revenue.png")

# 7. Spend vs conversions scatter (modeling window only — removes pre-Q3 2024 organic baseline cluster)
fig, ax = plt.subplots(figsize=(10, 8))
ax.scatter(mw_df['TOTAL_SPEND'] / 1e6, mw_df['CONVERSIONS'], alpha=0.5, s=30, color='navy')
r = mw_df['TOTAL_SPEND'].corr(mw_df['CONVERSIONS'])
ax.text(0.05, 0.95, f'Pearson r = {r:.3f}', transform=ax.transAxes, fontsize=12,
        verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
ax.set_title('Same-Day Spend vs. Conversions (Q3 2024 – Mar 2026)', fontsize=13, fontweight='bold')
ax.set_xlabel('Daily Spend ($M)')
ax.set_ylabel('Daily Conversions')
ax.grid(True, alpha=0.3)
plt.tight_layout()
save_fig("spend_vs_conversions_scatter.png")

# 8. Lag analysis
lag_results = []
for lag in range(0, 22):
    if lag < len(daily_df):
        r = daily_df['TOTAL_SPEND'].iloc[:-lag if lag > 0 else None].reset_index(drop=True).corr(
            daily_df['CONVERSIONS'].iloc[lag:].reset_index(drop=True))
        lag_results.append({'lag': lag, 'correlation': r})
lag_df = pd.DataFrame(lag_results)
best = lag_df.loc[lag_df['correlation'].idxmax()]
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(lag_df['lag'], lag_df['correlation'], marker='o', linewidth=2.5, markersize=8, color='steelblue')
ax.axvline(best['lag'], color='red', linestyle='--', linewidth=2, alpha=0.7)
ax.text(best['lag'] + 0.5, best['correlation'],
        f"Peak: {best['lag']:.0f}d\nr={best['correlation']:.3f}", fontsize=11,
        bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))
ax.set_title('Spend-to-Conversion Lag Analysis', fontsize=13, fontweight='bold')
ax.set_xlabel('Lag (days)')
ax.set_ylabel('Pearson r')
ax.grid(True, alpha=0.3)
plt.tight_layout()
save_fig("spend_conversion_lag.png")
lag_df.to_csv(OUT_P1_EDA / "tables" / "lag_correlations.csv", index=False)
print(f"  saved tables/lag_correlations.csv")

# 9. Monthly seasonality — computed on modeling window only (mw_df) so the
# chart reflects the same period the model trains on, not pre-scale-up 2024 data.
mw_df['MONTH'] = mw_df['DS'].dt.month
mw_df['MONTH_NAME'] = mw_df['DS'].dt.strftime('%B')
monthly_stats = mw_df.groupby(['MONTH', 'MONTH_NAME']).agg(
    {'TOTAL_SPEND': 'mean', 'CONVERSIONS': 'mean'}).reset_index()
fig, ax = plt.subplots(figsize=(12, 6))
x = np.arange(len(monthly_stats))
width = 0.35
spend_norm = monthly_stats['TOTAL_SPEND'] / monthly_stats['TOTAL_SPEND'].max() * 1000
ax.bar(x - width/2, spend_norm, width, label='Avg Daily Spend (normalized)', color='steelblue', alpha=0.8)
ax.bar(x + width/2, monthly_stats['CONVERSIONS'], width, label='Avg Daily Conversions', color='darkgreen', alpha=0.8)
ax.set_title('Month-of-Year Seasonality: Spend & Conversions', fontsize=13, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels([m[:3] for m in monthly_stats['MONTH_NAME']])
ax.legend()
ax.grid(True, alpha=0.3, axis='y')
plt.tight_layout()
save_fig("monthly_seasonality.png")

print("\nEDA export complete.")
print(f"  Figures: {len(list((OUT_P1_EDA / 'figures').glob('*.png')))} PNGs")
print(f"  Tables:  {len(list((OUT_P1_EDA / 'tables').glob('*.csv')))} CSVs")
print(f"  Metrics: {len(list((OUT_P1_EDA / 'metrics').glob('*.json')))} JSONs")
print(f"\nOutputs at: {OUT_P1_EDA}")
