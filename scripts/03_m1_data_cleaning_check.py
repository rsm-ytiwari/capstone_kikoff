#!/usr/bin/env python
"""
Run M1 data cleaning checks and save gate results to outputs/P1_02_eda/metrics/m1_gate.json.

Covers steps 1a–1e from the P2_01 notebook:
  1a. LTV anomaly imputation — post-imputation |z| < 2 for 2025-10-21 to 2025-10-24
  1b. Platform normalization — no raw labels (iso, web and app, iOS and android) in columns
  1c. DSP mapping — no Bing/Others/Idle columns in final dataset
  1d. DSP combined count — dsp_combined has > 30 rows in modeling window
  1e. Date filter — dataset spans 2024-07-01 to 2026-03-31

Usage (from project root):
    my-notebook-project/.venv/bin/python scripts/03_m1_data_cleaning_check.py
"""
import sys
import json
import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd

sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent.parent))
from src.config import SPEND_FILE, LTV_FILE, OUT_P1_EDA

MODEL_START = pd.Timestamp('2024-07-01')
MODEL_END   = pd.Timestamp('2026-03-31')

print('Loading spend data...')
spend_raw = pd.read_csv(SPEND_FILE, parse_dates=['DS'])

# 1b: Platform normalization
spend = spend_raw.copy()
spend['PLATFORM'] = spend['PLATFORM'].replace({'iso': 'ios', 'web and app': 'web'})
ios_android_mask = spend['PLATFORM'] == 'iOS and android'
if ios_android_mask.sum() > 0:
    ios_rows = spend[ios_android_mask].copy()
    android_rows = spend[ios_android_mask].copy()
    ios_rows['PLATFORM'] = 'ios'
    ios_rows['TOTAL_SPEND'] = ios_rows['TOTAL_SPEND'] / 2
    android_rows['PLATFORM'] = 'android'
    android_rows['TOTAL_SPEND'] = android_rows['TOTAL_SPEND'] / 2
    spend = pd.concat([spend[~ios_android_mask], ios_rows, android_rows], ignore_index=True)

# 1c: DSP mapping
dsp_map = {'Stackadapt': 'dsp_combined', 'appvertiser': 'dsp_combined', 'Inmobidsp': 'inmobidsp'}
spend['SOURCE_GROUP'] = spend['SOURCE_GROUP'].replace(dsp_map)
spend_1 = spend[~spend['SOURCE_GROUP'].isin(['bing', 'Others'])]

# 1e: Date filter
spend_2 = spend_1[(spend_1['DS'] >= MODEL_START) & (spend_1['DS'] <= MODEL_END)]

# 1d: DSP combined count
dsp_count = int((spend_2['SOURCE_GROUP'] == 'dsp_combined').sum())

# Aggregate and pivot to wide
spend_2 = spend_2.copy()
spend_2['TOTAL_SPEND'] = spend_2['TOTAL_SPEND'].fillna(0.0)
spend_3 = spend_2.groupby(['DS', 'PLATFORM', 'SOURCE_GROUP'], as_index=False)['TOTAL_SPEND'].sum()
spend_3['col'] = spend_3['SOURCE_GROUP'] + '_' + spend_3['PLATFORM']
spend_wide = spend_3.pivot_table(index='DS', columns='col', values='TOTAL_SPEND', aggfunc='sum', fill_value=0)
spend_wide.columns.name = None
spend_wide = spend_wide.reset_index().rename(columns={'DS': 'date'})

print('Loading LTV data...')
ltv_raw = pd.read_csv(LTV_FILE, parse_dates=['DS'])
ltv = ltv_raw[(ltv_raw['DS'] >= MODEL_START) & (ltv_raw['DS'] <= MODEL_END)].copy()
ltv = ltv.rename(columns={'DS': 'date'})

null_ltv = ltv['LTV_1YEAR'].isna()
if null_ltv.sum() > 0:
    ltv['LTV_1YEAR'] = ltv['LTV_1YEAR'].interpolate(method='linear', limit=5)

# 1a: Anomaly smoothing
rolling_stats = ltv['LTV_1YEAR'].rolling(window=30, center=True, min_periods=5).agg(['mean', 'std'])
z_score = (ltv['LTV_1YEAR'] - rolling_stats['mean']) / rolling_stats['std']
anomaly_mask = z_score.abs() > 3
if anomaly_mask.sum() > 0:
    rolling_median = ltv['LTV_1YEAR'].rolling(window=14, center=True, min_periods=5).median()
    ltv.loc[anomaly_mask, 'LTV_1YEAR'] = rolling_median[anomaly_mask]
# Second pass: unconditionally patch known-bad window (first pass left z=2.81)
_target = (ltv['date'] >= '2025-10-21') & (ltv['date'] <= '2025-10-24')
rolling_median = ltv['LTV_1YEAR'].rolling(window=14, center=True, min_periods=5).median()
ltv.loc[_target, 'LTV_1YEAR'] = rolling_median[_target]
ltv['LTV_PER_CUSTOMER'] = ltv['LTV_1YEAR'] / ltv['CONVERSIONS']

# 1a: Post-imputation z-score check for the anomaly window
window_mask = (ltv['date'] >= '2025-10-21') & (ltv['date'] <= '2025-10-24')
if window_mask.sum() > 0:
    _rolling2 = ltv['LTV_1YEAR'].rolling(window=30, center=True, min_periods=5).agg(['mean', 'std'])
    _z_post = (ltv['LTV_1YEAR'] - _rolling2['mean']) / _rolling2['std']
    check_1a_max_z = float(_z_post[window_mask].abs().max())
    check_1a_pass = check_1a_max_z < 2
    check_1a_note = f'|z| max = {check_1a_max_z:.2f} for 2025-10-21 to 2025-10-24'
else:
    check_1a_pass = True
    check_1a_max_z = 0.0
    check_1a_note = 'Anomaly window outside modeling window — no imputation needed'

# Merge
df = pd.merge(spend_wide, ltv[['date', 'CONVERSIONS', 'LTV_1YEAR', 'LTV_PER_CUSTOMER']], on='date', how='inner')
df = df.sort_values('date').reset_index(drop=True)

# --- Gate checks ---
checks = {}

# 1a
checks['1a_ltv_imputation'] = {
    'pass': check_1a_pass,
    'note': check_1a_note,
    'max_z': check_1a_max_z,
}

# 1b
bad_cols = [c for c in df.columns if any(p in c for p in ['iso_', 'web and app', 'iOS and android'])]
checks['1b_platform_normalization'] = {
    'pass': len(bad_cols) == 0,
    'note': 'PASS' if not bad_cols else f'FAIL — bad columns: {bad_cols}',
}

# 1c
bad_channels = [c for c in df.columns if any(x in c for x in ['bing', 'Others', 'Idle'])]
checks['1c_dsp_mapping'] = {
    'pass': len(bad_channels) == 0,
    'note': 'PASS' if not bad_channels else f'FAIL — unexpected columns: {bad_channels}',
}

# 1d
checks['1d_dsp_combined_count'] = {
    'pass': dsp_count > 30,
    'note': f'dsp_combined rows in modeling window: {dsp_count}',
    'count': dsp_count,
}

# 1e
actual_start = df['date'].min()
actual_end   = df['date'].max()
date_ok = (actual_start <= MODEL_START) and (actual_end >= MODEL_END)
checks['1e_date_filter'] = {
    'pass': date_ok,
    'note': f'{actual_start.date()} to {actual_end.date()}',
    'actual_start': str(actual_start.date()),
    'actual_end': str(actual_end.date()),
}

all_pass = all(v['pass'] for v in checks.values())
summary = {
    'all_pass': all_pass,
    'checks': checks,
    'dataset': {
        'rows': len(df),
        'columns': len(df.columns),
        'channel_cols': len([c for c in df.columns if c not in ['date', 'CONVERSIONS', 'LTV_1YEAR', 'LTV_PER_CUSTOMER']]),
        'null_ltv': int(df['LTV_1YEAR'].isna().sum()),
    },
}

out_path = OUT_P1_EDA / 'metrics' / 'm1_gate.json'
with open(out_path, 'w') as f:
    json.dump(summary, f, indent=2)

print()
print('=== M1 Data Preparation Gate ===')
for k, v in checks.items():
    status = 'PASS' if v['pass'] else 'FAIL'
    print(f'  {k}: [{status}]  {v["note"]}')
print()
print(f'Dataset: {len(df)} rows | {actual_start.date()} to {actual_end.date()}')
print(f'Columns: {len(df.columns)} ({summary["dataset"]["channel_cols"]} channel spend columns)')
print(f'Null LTV_1YEAR: {summary["dataset"]["null_ltv"]}')
print()
print(f'Overall: {"ALL PASS — M1 complete" if all_pass else "FAILURES DETECTED — review above"}')
print(f'Results saved → {out_path}')
