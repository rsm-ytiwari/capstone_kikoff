#!/usr/bin/env python
"""
Script 07: Full-channel baseline — weekly rollup, all channels, no lift priors.
Validates model structure before applying Mechanism 2 windowed priors.
Saves to outputs/P2_04_full_channel/metrics/baseline_convergence.json.

Run from repo root:
    my-notebook-project/.venv/bin/python scripts/07_full_channel_baseline.py
"""
import sys
import os
import json
import warnings

warnings.filterwarnings("ignore")

if os.path.basename(os.getcwd()) == "scripts":
    os.chdir("..")
sys.path.insert(0, ".")

import numpy as np
import pandas as pd
import pymc as pm
import arviz as az
from pymc_marketing.mmm import MMM, GeometricAdstock, LogisticSaturation

from src.config import SPEND_FILE, LTV_FILE, OUT_P2_04

print("=== Script 07: Full-Channel Baseline (Weekly Rollup, No Priors) ===")
print(f"SPEND_FILE: {SPEND_FILE}")
print(f"LTV_FILE:   {LTV_FILE}")
print(f"OUT_P2_04:  {OUT_P2_04}\n")

# ---------------------------------------------------------------------------
# M1 cleaning — mirrors prior scripts (Cells 3-6 equivalent)
# ---------------------------------------------------------------------------
spend_raw = pd.read_csv(SPEND_FILE, parse_dates=["DS"])
print(f"Raw spend: {spend_raw.shape}")

platform_map = {"iso": "ios", "web and app": "web", "iOS and android": "ios"}
spend_raw["PLATFORM"] = spend_raw["PLATFORM"].replace(platform_map)

channel_map = {
    "facebook":     "meta",
    "google":       "google",
    "applovin":     "applovin",
    "tiktok":       "tiktok",
    "apple_search": "apple_search",
    "Stackadapt":   "dsp",
    "appvertiser":  "dsp",
    "Inmobidsp":    "dsp",
    "liftoff":      "liftoff",
    "podcast":      "podcast",
    "ctv":          "ctv",
    "linear_tv":    "linear_tv",
    "influencer":   "influencer",
    "Others":       "others",
}
spend_raw["CHANNEL"] = spend_raw["SOURCE_GROUP"].map(channel_map)

spend_filt = spend_raw[
    spend_raw["CHANNEL"].notna()
    & (spend_raw["DS"] >= "2024-07-01")
    & (spend_raw["DS"] <= "2026-03-31")
].copy()

# Build column name = CHANNEL_PLATFORM, then collapse single-platform / tiny channels
col_rename = {
    "linear_tv_web":  "linear_tv",
    "ctv_web":        "ctv",
    "apple_search_ios": "apple_search",
    "podcast_web":    "podcast",
    "influencer_web": "influencer",
    "liftoff_ios":    "liftoff",
    "liftoff_android": "liftoff",
    "dsp_ios":        "dsp",
    "dsp_android":    "dsp",
    "dsp_web":        "dsp",
    "others_ios":     "others",
    "others_android": "others",
    "others_web":     "others",
    "applovin_web":   "applovin_android",  # <$100K total — collapse into android
}
spend_filt = spend_filt.copy()
spend_filt["col"] = (spend_filt["CHANNEL"] + "_" + spend_filt["PLATFORM"]).replace(col_rename)

# ---------------------------------------------------------------------------
# Weekly rollup — sum spend per (week, channel_col)
# ---------------------------------------------------------------------------
spend_weekly = (
    spend_filt.groupby([pd.Grouper(key="DS", freq="W-MON"), "col"])["TOTAL_SPEND"]
    .sum()
    .unstack(fill_value=0.0)
    .rename_axis(None, axis=1)
)

# ---------------------------------------------------------------------------
# LTV weekly rollup — sum conversions and LTV_3YEAR per week
# ---------------------------------------------------------------------------
ltv_raw = pd.read_csv(LTV_FILE, parse_dates=["DS"])
ltv = ltv_raw.set_index("DS").sort_index()

# M1a: LTV imputation (Option B — patch 2025-10-21:24)
rolling_med = ltv["LTV_1YEAR"].rolling(window=14, center=True, min_periods=5).median()
patch_dates = pd.date_range("2025-10-21", "2025-10-24", freq="D")
ltv.loc[patch_dates, "LTV_1YEAR"] = rolling_med.loc[patch_dates]

ltv_window = ltv.loc["2024-07-01":"2026-03-31"]
ltv_weekly  = ltv_window.resample("W-MON").agg({"CONVERSIONS": "sum", "LTV_3YEAR": "sum"})

# Align to common date range
common_start = max(spend_weekly.index.min(), ltv_weekly.index.min())
common_end   = min(spend_weekly.index.max(), ltv_weekly.index.max())
spend_weekly = spend_weekly.loc[common_start:common_end]
ltv_weekly   = ltv_weekly.loc[common_start:common_end]

assert spend_weekly.shape[0] == ltv_weekly.shape[0], (
    f"Week count mismatch: spend={spend_weekly.shape[0]}, ltv={ltv_weekly.shape[0]}"
)
assert spend_weekly.isna().sum().sum() == 0, "NaN in X"

channel_columns = sorted(spend_weekly.columns.tolist())
spend_weekly = spend_weekly[channel_columns]

X_weekly = spend_weekly.reset_index().rename(columns={"DS": "date"})
y_weekly  = ltv_weekly["CONVERSIONS"].reset_index(drop=True)

print(f"X_weekly: {X_weekly.shape}  |  y_weekly: {y_weekly.shape}")
print(f"Channels ({len(channel_columns)}): {channel_columns}")
print(f"Date range: {X_weekly['date'].iloc[0].date()} → {X_weekly['date'].iloc[-1].date()}")
print(f"y stats: min={y_weekly.min():.0f}  max={y_weekly.max():.0f}  mean={y_weekly.mean():.0f}\n")

# Save weekly dataset for script 08 reuse
ltv_weekly.reset_index().to_csv(OUT_P2_04 / "tables" / "ltv_weekly.csv", index=False)
X_weekly.to_csv(OUT_P2_04 / "tables" / "spend_weekly.csv", index=False)
print(f"Saved weekly tables to {OUT_P2_04 / 'tables'}/\n")

# ---------------------------------------------------------------------------
# Build and fit baseline MMM — no lift priors
# l_max=8 globally per D018: CTV half-life=6 weeks (CSV); other channels have
# alpha prior mean=0.25 so lag-8 weight ≈ 0 — no meaningful impact on them.
# PyMC-Marketing 0.19.3 does not support per-channel adstock dicts.
# ---------------------------------------------------------------------------
mmm = MMM(
    adstock=GeometricAdstock(l_max=8),
    saturation=LogisticSaturation(),
    date_column="date",
    channel_columns=channel_columns,
)
mmm.build_model(X_weekly, y_weekly)
print(f"Model built.  Starting MCMC (draws=500, tune=500, target_accept=0.90)...")

idata = mmm.fit(
    X_weekly, y_weekly,
    draws=500,
    tune=500,
    target_accept=0.90,
    random_seed=42,
)
print("Sampling complete.\n")

# ---------------------------------------------------------------------------
# Convergence diagnostics
# ---------------------------------------------------------------------------
summary  = az.summary(idata, var_names=["~likelihood"], round_to=3)
rhat_max = float(summary["r_hat"].max())
ess_min  = float(summary["ess_bulk"].min())
rhat_gate = rhat_max < 1.1
ess_gate  = ess_min > 400

print(f"Rhat max: {rhat_max:.4f}  → {'PASS' if rhat_gate else 'FAIL'}")
print(f"ESS min:  {ess_min:.0f}   → {'PASS' if ess_gate else 'FAIL'}")

if not (rhat_gate and ess_gate):
    try:
        divs = int(idata.sample_stats["diverging"].sum().item())
        print(f"Divergences: {divs}")
    except Exception:
        pass

# ---------------------------------------------------------------------------
# ICAC extraction — three-API fallback (same pattern as scripts 03-06)
# ---------------------------------------------------------------------------
api_used = None

try:
    contributions = mmm.compute_mean_contributions_over_time(original_scale=True)
    api_used = "compute_mean_contributions_over_time"
except Exception:
    pass

if api_used is None:
    try:
        _xr = mmm.compute_channel_contribution_original_scale()
        contributions = pd.DataFrame(
            _xr.mean(("chain", "draw")).values,
            columns=channel_columns,
        )
        api_used = "compute_channel_contribution_original_scale"
    except Exception:
        pass

if api_used is None:
    _raw = idata.posterior["channel_contribution"].mean(("chain", "draw"))
    contributions = pd.DataFrame(_raw.values, columns=channel_columns)
    api_used = "posterior_direct"

print(f"\nContribution API: {api_used}")
chan_sum   = contributions[channel_columns].sum()
total_contrib = float(chan_sum.sum())
total_y       = float(y_weekly.sum())
baseline_pct  = 1.0 - (total_contrib / total_y)

print(f"Total y (conversions):  {total_y:.0f}")
print(f"Total channel contrib:  {total_contrib:.0f}  ({total_contrib/total_y*100:.1f}% of y)")
print(f"Baseline %:             {baseline_pct*100:.1f}%  → {'PASS' if baseline_pct < 0.8 else 'WARN: >80%'}")

icac = {}
for ch in channel_columns:
    sp  = float(X_weekly[ch].sum())
    co  = float(chan_sum[ch])
    icac[ch] = round(sp / co, 2) if co > 0 else None

benchmarks = {
    "meta_ios":      135.48,
    "meta_android":  63.06,
    "meta_web":      156.89,
    "tiktok_ios":    108.83,
    "tiktok_android": 81.68,
    "tiktok_web":    112.12,
    "ctv":           135.05,
}

print("\niCAC vs benchmarks (tested channels — expect FAIL without priors):")
for ch, bench in benchmarks.items():
    v = icac.get(ch)
    if v is not None:
        in50 = bench * 0.5 <= v <= bench * 1.5
        print(f"  {ch:<22} ${v:>8.2f}  benchmark ${bench:.2f}  {'PASS' if in50 else 'FAIL (expected)'}")

# ---------------------------------------------------------------------------
# Save outputs
# ---------------------------------------------------------------------------
result = {
    "script": "07_full_channel_baseline",
    "weekly_obs": int(X_weekly.shape[0]),
    "n_channels": len(channel_columns),
    "channel_columns": channel_columns,
    "convergence": {
        "rhat_max":       round(rhat_max, 4),
        "ess_min":        round(ess_min, 1),
        "rhat_gate_pass": rhat_gate,
        "ess_gate_pass":  ess_gate,
    },
    "baseline_pct":       round(baseline_pct, 4),
    "baseline_gate_pass": baseline_pct < 0.8,
    "icac": icac,
    "benchmarks": benchmarks,
    "contribution_api_used": api_used,
    "notes": (
        "Baseline without lift priors. iCAC expected to deviate from benchmarks. "
        "This run validates model structure and weekly rollup pipeline."
    ),
}

out_path = OUT_P2_04 / "metrics" / "baseline_convergence.json"
with open(out_path, "w") as f:
    json.dump(result, f, indent=2)

print(f"\nSaved: {out_path}")

print("\n=== Script 07 Gate Summary ===")
print(f"  Rhat < 1.1:     {'PASS' if rhat_gate else 'FAIL'}  ({rhat_max:.4f})")
print(f"  ESS > 400:      {'PASS' if ess_gate else 'FAIL'}  ({ess_min:.0f})")
print(f"  Baseline < 80%: {'PASS' if baseline_pct < 0.8 else 'WARN'}  ({baseline_pct*100:.1f}%)")
print(f"\n07 ready for 08: {rhat_gate and ess_gate}")
