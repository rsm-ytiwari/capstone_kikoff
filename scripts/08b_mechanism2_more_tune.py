#!/usr/bin/env python
"""
Script 08b: Mechanism 2 — Option A retry with tune=2000, target_accept=0.98.
Same as 08 but with extended tuning to resolve 376 divergences and ESS=64.
Saves to outputs/P2_04_full_channel/metrics/mechanism2b_convergence.json.

Script 08: Mechanism 2 — pm.math windowed priors for channels with lift test data.

Mechanism 2 adds lift test evidence ONLY during the weeks overlapping the
experimental test window (not globally). This avoids the iOS pacing confound
(r=0.48) that caused Mechanism 3 to fail Gate 2 across all three variants.

Implementation:
    1. Build full-channel MMM (same setup as script 07)
    2. Enter model context post-build_model()
    3. For each tested channel: find overlapping weeks, sum
       channel_contribution_original_scale in those weeks, add
       pm.Normal observation targeting the lift test delta_y

Lift tests used:
    - Meta May 2025 (Kikoff_LiftStudy_0525):    iOS, Android, Web
    - TikTok Aug-Sep 2025:                       iOS, Android, Web
    - CTV Oct-Nov 2025:                          combined (no platform split)

Meta Jan 2026 excluded: study cancelled, iOS lift implausible ($1,350 iCAC),
only 10 conversions — data insufficient for reliable prior.

Run from repo root:
    my-notebook-project/.venv/bin/python scripts/08_mechanism2_windowed.py
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

print("=== Script 08b: Mechanism 2 — Windowed Lift Priors (tune=2000, accept=0.98) ===")
print(f"SPEND_FILE: {SPEND_FILE}")
print(f"LTV_FILE:   {LTV_FILE}")
print(f"OUT_P2_04:  {OUT_P2_04}\n")

# ---------------------------------------------------------------------------
# Lift test reference table (from Kikoff_data_incrementality.csv)
# Format: (label, channel_col, test_start_inclusive, test_end_inclusive,
#           delta_y_conversions, sigma_conversions)
# sigma: Meta/TikTok = 30% of delta_y (heuristic — no CI in CSV, per D020).
# CTV = 373, CI-derived from 95% CI [1109, 2570]: (2570-1109)/2/1.96 ≈ 373 (per D020).
# Test ends are inclusive (end_exclusive - 1 day from the CSV)
# ---------------------------------------------------------------------------
LIFT_TESTS = [
    # Meta May 2025 — Kikoff_LiftStudy_0525 (99.9% confidence, completed)
    ("meta_ios_may25",     "meta_ios",      "2025-05-06", "2025-05-13",  1_156.0,  347.0),
    ("meta_android_may25", "meta_android",  "2025-05-06", "2025-05-13",  1_405.0,  422.0),
    ("meta_web_may25",     "meta_web",      "2025-05-06", "2025-05-13",  1_128.0,  338.0),
    # TikTok Aug-Sep 2025 (holdout 3-cell study)
    ("tiktok_ios_aug25",     "tiktok_ios",     "2025-08-22", "2025-09-14",    569.0,  171.0),
    ("tiktok_android_aug25", "tiktok_android", "2025-08-22", "2025-09-14",    651.0,  195.0),
    ("tiktok_web_aug25",     "tiktok_web",     "2025-08-22", "2025-09-14",  6_215.0, 1_865.0),
    # CTV Oct-Nov 2025 (geo lift test, 50% holdout, 95% CI); sigma CI-derived per D020
    ("ctv_oct25",          "ctv",           "2025-10-06", "2025-11-01",  1_840.0,  373.0),
]

# ---------------------------------------------------------------------------
# M1 cleaning (identical to script 07)
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

col_rename = {
    "linear_tv_web":    "linear_tv",
    "ctv_web":          "ctv",
    "apple_search_ios": "apple_search",
    "podcast_web":      "podcast",
    "influencer_web":   "influencer",
    "liftoff_ios":      "liftoff",
    "liftoff_android":  "liftoff",
    "dsp_ios":          "dsp",
    "dsp_android":      "dsp",
    "dsp_web":          "dsp",
    "others_ios":       "others",
    "others_android":   "others",
    "others_web":       "others",
    "applovin_web":     "applovin_android",
}
spend_filt["col"] = (spend_filt["CHANNEL"] + "_" + spend_filt["PLATFORM"]).replace(col_rename)

# ---------------------------------------------------------------------------
# Weekly rollup
# ---------------------------------------------------------------------------
spend_weekly = (
    spend_filt.groupby([pd.Grouper(key="DS", freq="W-MON"), "col"])["TOTAL_SPEND"]
    .sum()
    .unstack(fill_value=0.0)
    .rename_axis(None, axis=1)
)

ltv_raw = pd.read_csv(LTV_FILE, parse_dates=["DS"])
ltv = ltv_raw.set_index("DS").sort_index()
rolling_med = ltv["LTV_1YEAR"].rolling(window=14, center=True, min_periods=5).median()
patch_dates = pd.date_range("2025-10-21", "2025-10-24", freq="D")
ltv.loc[patch_dates, "LTV_1YEAR"] = rolling_med.loc[patch_dates]
ltv_window = ltv.loc["2024-07-01":"2026-03-31"]
ltv_weekly  = ltv_window.resample("W-MON").agg({"CONVERSIONS": "sum", "LTV_3YEAR": "sum"})

common_start = max(spend_weekly.index.min(), ltv_weekly.index.min())
common_end   = min(spend_weekly.index.max(), ltv_weekly.index.max())
spend_weekly = spend_weekly.loc[common_start:common_end]
ltv_weekly   = ltv_weekly.loc[common_start:common_end]

assert spend_weekly.shape[0] == ltv_weekly.shape[0], "Week count mismatch"
assert spend_weekly.isna().sum().sum() == 0, "NaN in X"

channel_columns = sorted(spend_weekly.columns.tolist())
spend_weekly = spend_weekly[channel_columns]

X_weekly = spend_weekly.reset_index().rename(columns={"DS": "date"})
y_weekly  = ltv_weekly["CONVERSIONS"].reset_index(drop=True)

week_starts = pd.to_datetime(X_weekly["date"])  # Monday labels

print(f"X_weekly: {X_weekly.shape}  |  y_weekly: {y_weekly.shape}")
print(f"Channels ({len(channel_columns)}): {channel_columns}")
print(f"Date range: {X_weekly['date'].iloc[0].date()} → {X_weekly['date'].iloc[-1].date()}\n")

# ---------------------------------------------------------------------------
# Pre-compute window indices for each lift test
# A W-MON week labeled `w` covers [w, w+6]. It overlaps [t_start, t_end] iff:
#     w <= t_end  AND  w >= t_start - 6 days
# ---------------------------------------------------------------------------
window_index_map = {}   # label → np.array of integer indices
print("Lift test window mapping:")
for label, ch, t_start_str, t_end_str, delta_y, sigma in LIFT_TESTS:
    t_start = pd.Timestamp(t_start_str)
    t_end   = pd.Timestamp(t_end_str)
    overlap = (week_starts <= t_end) & (week_starts >= t_start - pd.Timedelta(days=6))
    idx = np.where(overlap)[0]
    window_index_map[label] = idx
    week_dates = week_starts[overlap].dt.date.tolist()
    print(f"  {label:<26}: {len(idx)} week(s)  {week_dates}  delta_y={delta_y:.0f}  σ={sigma:.0f}")

# ---------------------------------------------------------------------------
# Build MMM (same hyperparameters as script 07)
# ---------------------------------------------------------------------------
mmm = MMM(
    adstock=GeometricAdstock(l_max=8),  # D018: l_max=8 globally; CTV needs >=6 (half-life=6)
    saturation=LogisticSaturation(),
    date_column="date",
    channel_columns=channel_columns,
)
mmm.build_model(X_weekly, y_weekly)
print("\nModel built.")

# ---------------------------------------------------------------------------
# Mechanism 2: add windowed lift observations inside the model context
#
# channel_contribution_original_scale is an XTensorVariable with
# dims=('date', 'channel'), shape=(n_weeks, n_channels).
# Calling .values converts it to a plain TensorVariable for PyTensor ops.
# We index [week_indices, channel_index] to get contributions for the test
# window only, then sum and compare to the experimental delta_y.
# ---------------------------------------------------------------------------
print("\nAdding windowed lift observations (Mechanism 2)...")
with mmm.model:
    ocs = mmm.model["channel_contribution_original_scale"].values  # (n_weeks, n_channels)

    for label, ch, t_start_str, t_end_str, delta_y, sigma in LIFT_TESTS:
        chan_idx    = channel_columns.index(ch)
        window_idx  = window_index_map[label]

        if len(window_idx) == 0:
            print(f"  WARNING: no overlapping weeks for {label} — skipping")
            continue

        # Sum model's predicted causal contributions in test window weeks
        windowed_contrib = ocs[window_idx, chan_idx].sum()

        # Normal observation: model's windowed sum ≈ lift test delta_y ± sigma
        pm.Normal(
            f"lift_{label}",
            mu=windowed_contrib,
            sigma=sigma,
            observed=delta_y,
        )
        print(f"  Added lift_{label}  (chan_idx={chan_idx}, n_weeks={len(window_idx)})")

print("All windowed observations added.\n")

# ---------------------------------------------------------------------------
# Fit — more draws and tuning than script 07 for proper convergence
# ---------------------------------------------------------------------------
print("Starting MCMC (draws=1000, tune=2000, target_accept=0.98)...")
idata = mmm.fit(
    X_weekly, y_weekly,
    draws=1000,
    tune=2000,
    target_accept=0.98,
    random_seed=42,
)
print("Sampling complete.\n")

# ---------------------------------------------------------------------------
# Convergence diagnostics
# ---------------------------------------------------------------------------
summary  = az.summary(idata, var_names=["~likelihood"], round_to=3)
rhat_max = float(summary["r_hat"].max())
ess_min  = float(summary["ess_bulk"].min())
rhat_gate = rhat_max < 1.05
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
# ICAC extraction — three-API fallback
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
chan_sum       = contributions[channel_columns].sum()
total_contrib  = float(chan_sum.sum())
total_y        = float(y_weekly.sum())
baseline_pct   = 1.0 - (total_contrib / total_y)

print(f"Total y (conversions):  {total_y:.0f}")
print(f"Total channel contrib:  {total_contrib:.0f}  ({total_contrib/total_y*100:.1f}% of y)")
print(f"Baseline %:             {baseline_pct*100:.1f}%  → {'PASS' if baseline_pct < 0.8 else 'WARN: >80%'}")

icac = {}
for ch in channel_columns:
    sp = float(X_weekly[ch].sum())
    co = float(chan_sum[ch])
    icac[ch] = round(sp / co, 2) if co > 0 else None

# ---------------------------------------------------------------------------
# Gate evaluation — tested channels with benchmarks from lift tests
# ---------------------------------------------------------------------------
benchmarks = {
    "meta_ios":       135.48,
    "meta_android":   63.06,
    "meta_web":       156.89,
    "tiktok_ios":     108.83,
    "tiktok_android": 81.68,
    "tiktok_web":     112.12,
    "ctv":            135.05,
}

gates = {}
print(f"\n{'Channel':<22} {'iCAC':>8}  {'Benchmark':>10}  {'±50%':>6}  {'Gate'}")
print("-" * 60)
for ch, bench in benchmarks.items():
    v = icac.get(ch)
    if v is not None:
        in50 = bench * 0.5 <= v <= bench * 1.5
        gates[f"gate_icac_{ch}"] = in50
        print(f"  {ch:<20} ${v:>7.2f}  ${bench:>9.2f}  {'PASS' if in50 else 'FAIL':>6}")
    else:
        gates[f"gate_icac_{ch}"] = False
        print(f"  {ch:<20} {'None':>8}  ${bench:>9.2f}  {'FAIL':>6}")

# Ordering gate: for Meta, iOS iCAC should exceed Android (iOS users more expensive)
ios_icac = icac.get("meta_ios") or 0.0
and_icac = icac.get("meta_android") or 0.0
ordering_gate = ios_icac > and_icac
gates["gate_ordering_meta_ios_gt_android"] = ordering_gate
print(f"\n  Meta iOS > Android iCAC: {'PASS' if ordering_gate else 'FAIL'}  "
      f"(iOS=${ios_icac:.2f}, Android=${and_icac:.2f})")
print(f"\n  Rhat < 1.05:   {'PASS' if rhat_gate else 'FAIL'}  ({rhat_max:.4f})")
print(f"  ESS > 400:     {'PASS' if ess_gate else 'FAIL'}  ({ess_min:.0f})")
print(f"  Baseline <80%: {'PASS' if baseline_pct < 0.8 else 'WARN'}  ({baseline_pct*100:.1f}%)")

gates["gate_rhat_pass"]     = rhat_gate
gates["gate_ess_pass"]      = ess_gate
gates["gate_baseline_pass"] = baseline_pct < 0.8

all_pass = all(gates.values())
print(f"\nAll M3 gates passed: {all_pass}")

# ---------------------------------------------------------------------------
# Save
# ---------------------------------------------------------------------------
result = {
    "script": "08b_mechanism2_more_tune",
    "weekly_obs": int(X_weekly.shape[0]),
    "n_channels": len(channel_columns),
    "channel_columns": channel_columns,
    "lift_tests_applied": [
        {"label": label, "channel": ch, "start": ts, "end": te,
         "delta_y": dy, "sigma": sg, "n_weeks": int(len(window_index_map[label]))}
        for label, ch, ts, te, dy, sg in LIFT_TESTS
    ],
    "convergence": {
        "rhat_max":       round(rhat_max, 4),
        "ess_min":        round(ess_min, 1),
        "rhat_gate_pass": rhat_gate,
        "ess_gate_pass":  ess_gate,
    },
    "baseline_pct": round(baseline_pct, 4),
    "icac": icac,
    "benchmarks": benchmarks,
    "gates": gates,
    "all_gates_pass": all_pass,
    "contribution_api_used": api_used,
    "notes": (
        "Mechanism 2 windowed priors. Lift test evidence restricted to weeks "
        "overlapping with experimental test windows (not global). "
        "Meta Jan 2026 excluded: study cancelled, only 10 iOS conversions."
    ),
}

out_path = OUT_P2_04 / "metrics" / "mechanism2b_convergence.json"
with open(out_path, "w") as f:
    json.dump(result, f, indent=2)

print(f"\nSaved: {out_path}")

print("\n=== Script 08 Gate Summary ===")
print(f"  Rhat < 1.05:               {'PASS' if rhat_gate else 'FAIL'}  ({rhat_max:.4f})")
print(f"  ESS > 400:                 {'PASS' if ess_gate else 'FAIL'}  ({ess_min:.0f})")
print(f"  Baseline < 80%:            {'PASS' if baseline_pct < 0.8 else 'WARN'}  ({baseline_pct*100:.1f}%)")
for ch, bench in benchmarks.items():
    g = gates.get(f"gate_icac_{ch}", False)
    v = icac.get(ch)
    print(f"  iCAC {ch:<22}: {'PASS' if g else 'FAIL'}  "
          f"(${v:.2f} vs benchmark ${bench:.2f})" if v else f"  iCAC {ch:<22}: FAIL  (None)")
print(f"  Meta iOS > Android iCAC:   {'PASS' if ordering_gate else 'FAIL'}")
print(f"\nAll M3 gates passed: {all_pass}")
if all_pass:
    print("\nREADY: Proceed to Phase B (Meta-Web output charts) after user APPROVED.")
else:
    print("\nSTOP: Surface failing gates to user before proceeding.")
