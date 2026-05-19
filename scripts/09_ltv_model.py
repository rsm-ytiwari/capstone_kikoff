#!/usr/bin/env python
"""
Script 09: Model 2 — y = LTV_3YEAR (weekly sum).

Identical Mechanism 2 structure to 08b except:
- y = ltv_weekly["LTV_3YEAR"] (dollars) instead of ltv_weekly["CONVERSIONS"]
- Lift test delta_y scaled to LTV dollars: delta_y_ltv = delta_y_conv * avg_ltv
  (avg_ltv = total LTV_3YEAR / total CONVERSIONS, computed from data)
- iCAC computed via implied_conv = ltv_contribution / avg_ltv, then spend / implied_conv
- iROAS added: ltv_contribution_sum / spend_sum
- Output: outputs/P2_04_full_channel/metrics/ltv_convergence.json
- Trace saved to outputs/P2_04_full_channel/traces/ltv_trace.nc (for script 10)

Caveats carried forward from Model 1 (08b):
  Q22: iOS/Android spend split is imputed 50/50 — unconfirmed by Abheek.
  Q23: iOS pacing confound (r=0.48 with conversions); LTV inherits this risk
       since LTV = f(conversions). Mechanism 2 windowed priors mitigate for
       tested channels, but structural risk is not eliminated.

Run from repo root:
    my-notebook-project/.venv/bin/python scripts/09_ltv_model.py
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
from pymc_extras.prior import Prior

from src.config import SPEND_FILE, LTV_FILE, OUT_P2_04

print("=== Script 09: Model 2 — y=LTV_3YEAR (tune=2000, accept=0.98) ===")
print(f"SPEND_FILE: {SPEND_FILE}")
print(f"LTV_FILE:   {LTV_FILE}")
print(f"OUT_P2_04:  {OUT_P2_04}\n")

# ---------------------------------------------------------------------------
# Lift test reference table (same windows and channels as 08b).
# delta_y and sigma are in CONVERSIONS here; scaled to LTV dollars below
# via `* avg_ltv` (existing scaling logic at lines ~160).
#
# M3.5b 2026-05-19: lift δ_y and σ scaled to W-MON window basis (Fix-A) —
# see proposals/2026-05-19_d027_window_basis_correction.md. I-7 reconciliation
# (drafts/i7_window_reconciliation_2026-05-18.md) found the windowed-iCAC
# gate compared N-day model spend to k-day lift-test δ_y, mechanically
# inflating iCAC by ~N/k. Fix-A scales each row's δ_y and σ by
# (W-MON window days / test days inclusive). LTV-unit scaling via `* avg_ltv`
# preserves the same factor through to the LTV-model prior automatically.
#
# Per-test scaling factors (mirror 08b):
#   Meta May 2025:   8d  → 14d  × 1.75
#   TikTok Aug 2025: 24d → 28d  × 1.1667
#   CTV Oct 2025:    27d → 28d  × 1.037
#   Meta Jan 2026:   5d  → 14d  × 2.8
#
# σ:
#   Meta May 2025 + TikTok Aug 2025: σ = 10% of (scaled δ_y) (Path B per D022).
#   CTV: σ scales with δ_y (CI-derived 373 → 386.8); D020 unchanged in spirit.
#   Meta Jan 2026: σ = 3 × max(scaled δ_y, 30) (D019-rev — wide-σ).
# Originals (pre-Fix-A) preserved in ltv_convergence.json + ltv_trace.nc
# (canonical M3.5 reference snapshots — do not overwrite).
# ---------------------------------------------------------------------------
LIFT_TESTS_CONV = [
    # (label, channel_col, test_start, test_end, delta_y_conv, sigma_conv)
    # Meta May 2025 — 8d test, W-MON window 14d → scale 1.75.
    ("meta_ios_may25",     "meta_ios",      "2025-05-06", "2025-05-13",  2_023.0,   202.3),
    ("meta_android_may25", "meta_android",  "2025-05-06", "2025-05-13",  2_459.0,   245.9),
    ("meta_web_may25",     "meta_web",      "2025-05-06", "2025-05-13",  1_974.0,   197.4),
    # TikTok Aug-Sep 2025 — 24d test, W-MON window 28d → scale 1.1667.
    ("tiktok_ios_aug25",     "tiktok_ios",     "2025-08-22", "2025-09-14",     663.8,    66.4),
    ("tiktok_android_aug25", "tiktok_android", "2025-08-22", "2025-09-14",     759.5,    75.95),
    ("tiktok_web_aug25",     "tiktok_web",     "2025-08-22", "2025-09-14",   7_250.8,  725.08),
    # CTV Oct-Nov 2025 — 27d test, W-MON window 28d → scale 1.037 (σ scales too).
    ("ctv_oct25",          "ctv",           "2025-10-06", "2025-11-01",   1_908.0,   386.8),
    # Meta Jan 2026 — 5d test, W-MON window 14d → scale 2.8.
    # Wide σ rule preserved: σ = 3 × max(scaled δ_y, 30).
    ("meta_ios_jan26",     "meta_ios",      "2026-01-03", "2026-01-07",      28.0,     90.0),
    ("meta_android_jan26", "meta_android",  "2026-01-03", "2026-01-07",   1_022.0,  3_066.0),
    ("meta_web_jan26",     "meta_web",      "2026-01-03", "2026-01-07",   3_142.0,  9_426.0),
]

# ---------------------------------------------------------------------------
# M1 cleaning (identical to 08b)
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
# Model 2: y = LTV_3YEAR (weekly sum, dollars)
y_weekly = ltv_weekly["LTV_3YEAR"].reset_index(drop=True)

week_starts = pd.to_datetime(X_weekly["date"])

print(f"X_weekly: {X_weekly.shape}  |  y_weekly (LTV_3YEAR $): {y_weekly.shape}")
print(f"Channels ({len(channel_columns)}): {channel_columns}")
print(f"Date range: {X_weekly['date'].iloc[0].date()} → {X_weekly['date'].iloc[-1].date()}\n")

# ---------------------------------------------------------------------------
# avg_ltv: convert conversion-count lift evidence to LTV-dollar units.
# Using full window totals keeps the scale consistent with y.
# ---------------------------------------------------------------------------
total_ltv_sum  = float(ltv_weekly["LTV_3YEAR"].sum())
total_conv_sum = float(ltv_weekly["CONVERSIONS"].sum())
avg_ltv = total_ltv_sum / total_conv_sum
print(f"avg_ltv_per_customer: ${avg_ltv:,.2f}  "
      f"(total LTV ${total_ltv_sum:,.0f} / total conv {total_conv_sum:,.0f})")

# Scale lift tests to LTV dollars
LIFT_TESTS = [
    (label, ch, ts, te, dy * avg_ltv, sg * avg_ltv)
    for label, ch, ts, te, dy, sg in LIFT_TESTS_CONV
]
print("\nLift tests scaled to LTV units (delta_y * avg_ltv):")
for (label, ch, ts, te, dy_ltv, sg_ltv), (_, _, _, _, dy_conv, _) in zip(LIFT_TESTS, LIFT_TESTS_CONV):
    print(f"  {label:<26}: delta_y_conv={dy_conv:.0f}  →  delta_y_ltv=${dy_ltv:,.0f}  σ_ltv=${sg_ltv:,.0f}")

# ---------------------------------------------------------------------------
# Pre-compute window indices (identical logic to 08b)
# ---------------------------------------------------------------------------
window_index_map = {}
print("\nLift test window mapping:")
for label, ch, t_start_str, t_end_str, delta_y_ltv, sigma_ltv in LIFT_TESTS:
    t_start = pd.Timestamp(t_start_str)
    t_end   = pd.Timestamp(t_end_str)
    overlap = (week_starts <= t_end) & (week_starts >= t_start - pd.Timedelta(days=6))
    idx = np.where(overlap)[0]
    window_index_map[label] = idx
    week_dates = week_starts[overlap].dt.date.tolist()
    print(f"  {label:<26}: {len(idx)} week(s)  {week_dates}  delta_y_ltv=${delta_y_ltv:,.0f}")

# ---------------------------------------------------------------------------
# Build MMM (same hyperparameters as 08b)
# ---------------------------------------------------------------------------
mmm = MMM(
    adstock=GeometricAdstock(l_max=8),  # D018: l_max=8 globally; CTV needs >=6 (half-life=6)
    # M3.5 canonical: mirror 08b's Lever C lam prior — Gamma(α=2, β=2)
    # for cleaner posterior (Model 1 ESS jumped 687 → 2218 with this prior).
    saturation=LogisticSaturation(
        priors={
            "lam":  Prior("Gamma",      alpha=2, beta=2, dims="channel"),
            "beta": Prior("HalfNormal", sigma=2,         dims="channel"),
        }
    ),
    date_column="date",
    channel_columns=channel_columns,
)
mmm.build_model(X_weekly, y_weekly)
print("\nModel built (y=LTV_3YEAR).")

# ---------------------------------------------------------------------------
# Mechanism 2: windowed lift observations (LTV-scaled)
# ---------------------------------------------------------------------------
print("\nAdding windowed lift observations (Mechanism 2, LTV-scaled)...")
with mmm.model:
    ocs = mmm.model["channel_contribution_original_scale"].values

    for label, ch, t_start_str, t_end_str, delta_y_ltv, sigma_ltv in LIFT_TESTS:
        chan_idx   = channel_columns.index(ch)
        window_idx = window_index_map[label]

        if len(window_idx) == 0:
            print(f"  WARNING: no overlapping weeks for {label} — skipping")
            continue

        windowed_contrib = ocs[window_idx, chan_idx].sum()

        pm.Normal(
            f"lift_{label}",
            mu=windowed_contrib,
            sigma=sigma_ltv,
            observed=delta_y_ltv,
        )
        print(f"  Added lift_{label}  (chan_idx={chan_idx}, n_weeks={len(window_idx)}, "
              f"delta_y_ltv=${delta_y_ltv:,.0f})")

print("All windowed observations added.\n")

# ---------------------------------------------------------------------------
# Fit
# ---------------------------------------------------------------------------
print("Starting MCMC (draws=1000, tune=2000, target_accept=0.98, seed=42)...")
idata = mmm.fit(
    X_weekly, y_weekly,
    draws=1000,
    tune=2000,
    target_accept=0.98,
    random_seed=42,
)
print("Sampling complete.\n")

# ---------------------------------------------------------------------------
# Save trace for script 10 (best-effort — skip if too large)
# ---------------------------------------------------------------------------
trace_path = OUT_P2_04 / "traces" / "ltv_trace_window_scaled.nc"
try:
    idata.to_netcdf(str(trace_path))
    print(f"Trace saved: {trace_path}")
except Exception as e:
    print(f"Trace save skipped ({e}) — script 10 must run in same process if needed.")

# ---------------------------------------------------------------------------
# Convergence diagnostics
# ---------------------------------------------------------------------------
summary  = az.summary(idata, var_names=["~likelihood"], round_to=3)
rhat_max = float(summary["r_hat"].max())
ess_min  = float(summary["ess_bulk"].min())
rhat_gate = rhat_max < 1.05
ess_gate  = ess_min > 400

try:
    divs = int(idata.sample_stats["diverging"].sum().item())
except Exception:
    divs = None

print(f"Rhat max:    {rhat_max:.4f}  → {'PASS' if rhat_gate else 'FAIL'}")
print(f"ESS min:     {ess_min:.0f}   → {'PASS' if ess_gate else 'FAIL'}")
print(f"Divergences: {divs}")

# ---------------------------------------------------------------------------
# Contribution extraction — three-API fallback (same as 08b)
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
chan_sum      = contributions[channel_columns].sum()
total_contrib = float(chan_sum.sum())
total_y       = float(y_weekly.sum())
baseline_pct  = 1.0 - (total_contrib / total_y)

print(f"Total y (LTV_3YEAR $):  ${total_y:,.0f}")
print(f"Total channel contrib:  ${total_contrib:,.0f}  ({total_contrib/total_y*100:.1f}% of y)")
print(f"Baseline %:             {baseline_pct*100:.1f}%  → {'PASS (<20% Kikoff)' if baseline_pct < 0.20 else 'FAIL (>20%)'}")

# Aggregate iCAC / iROAS (full-history) — retained as diagnostic only.
# D023 deprecated aggregate iCAC as a gate.
icac_aggregate = {}
iroas = {}
for ch in channel_columns:
    sp = float(X_weekly[ch].sum())
    co = float(chan_sum[ch])           # LTV dollars attributed to this channel
    implied_conv = co / avg_ltv        # back-convert to implied conversions
    icac_aggregate[ch] = round(sp / implied_conv, 2) if implied_conv > 0 else None
    iroas[ch] = round(co / sp, 4)     if sp > 0            else None

# ---------------------------------------------------------------------------
# Windowed-iCAC helper (D023): apples-to-apples comparison to lift-test
# point estimate. For Model 2, contributions are in LTV dollars — convert
# back via avg_ltv to get implied conversions, then divide spend by that.
# ---------------------------------------------------------------------------
contributions.index = pd.to_datetime(week_starts.values)

def windowed_icac(channel: str, start: str, end: str) -> float | None:
    """LTV-model iCAC within a date window:
       iCAC = spend / implied_conversions,
       implied_conversions = ltv_contribution / avg_ltv.

    Uses the same week-overlap convention as the lift-test prior (start - 6d
    to end) so the gate and the prior measure the same week range.
    """
    start_ts = pd.Timestamp(start) - pd.Timedelta(days=6)
    end_ts   = pd.Timestamp(end)
    mask_X = (week_starts >= start_ts) & (week_starts <= end_ts)
    spend_w = float(X_weekly.loc[mask_X.values, channel].sum())
    ltv_contrib_w = float(contributions.loc[start_ts:end_ts, channel].sum())
    if ltv_contrib_w <= 0:
        return None
    implied_conv = ltv_contrib_w / avg_ltv
    return round(spend_w / implied_conv, 2) if implied_conv > 0 else None

# ---------------------------------------------------------------------------
# Gate evaluation (D023 windowed gate; D021 baseline <20%; D024 no ordering)
# ---------------------------------------------------------------------------
benchmarks = {
    # channel: (point_estimate, test_start, test_end)
    "meta_ios":       (135.48, "2025-05-06", "2025-05-13"),
    "meta_android":   ( 63.06, "2025-05-06", "2025-05-13"),
    "meta_web":       (156.89, "2025-05-06", "2025-05-13"),
    "tiktok_ios":     (108.83, "2025-08-22", "2025-09-14"),
    "tiktok_android": ( 81.68, "2025-08-22", "2025-09-14"),
    "tiktok_web":     (112.12, "2025-08-22", "2025-09-14"),
    "ctv":            (135.05, "2025-10-06", "2025-11-01"),
}

# Truth-band tolerance per channel (D023). CTV uses ±$15 (CI-derived);
# all others ±$50 (Abheek 45:13–45:36 truth band).
TOLERANCE = {"ctv": 15.0}
DEFAULT_TOLERANCE = 50.0

windowed_icac_map = {}
gates = {}
print(f"\n{'Channel':<22} {'Win iCAC':>9}  {'Bench':>7}  {'Band':>15}  {'iROAS':>8}  {'Gate'}")
print("-" * 80)
for ch, (bench, t_start, t_end) in benchmarks.items():
    tol = TOLERANCE.get(ch, DEFAULT_TOLERANCE)
    v = windowed_icac(ch, t_start, t_end)
    r = iroas.get(ch, 0.0)
    windowed_icac_map[ch] = v
    in_band = (v is not None) and (bench - tol <= v <= bench + tol)
    gates[f"gate_icac_windowed_{ch}"] = in_band
    v_str = f"${v:>8.2f}" if v is not None else "    None "
    print(f"  {ch:<20} {v_str}  ${bench:>6.2f}  ${bench-tol:>5.0f}-${bench+tol:<5.0f}  {r:>8.4f}  {'PASS' if in_band else 'FAIL'}")

# D024: ordering gate REMOVED.
# D021: baseline threshold tightened from <80% to <20%.
print(f"\n  Rhat < 1.05:   {'PASS' if rhat_gate else 'FAIL'}  ({rhat_max:.4f})")
print(f"  ESS > 400:     {'PASS' if ess_gate else 'FAIL'}  ({ess_min:.0f})")
print(f"  Baseline <20%: {'PASS' if baseline_pct < 0.20 else 'FAIL'}  ({baseline_pct*100:.1f}%)")
if divs is not None:
    print(f"  Divergences:   {divs}  → {'PASS (0)' if divs == 0 else 'FAIL (>0)'}")

gates["gate_rhat_pass"]     = rhat_gate
gates["gate_ess_pass"]      = ess_gate
gates["gate_baseline_pass"] = baseline_pct < 0.20

all_pass = all(gates.values())
print(f"\nAll M3 gates passed: {all_pass}")

# ---------------------------------------------------------------------------
# Save
# ---------------------------------------------------------------------------
result = {
    "script": "09_ltv_model",
    "model": "Model 2 (y=LTV_3YEAR)",
    "weekly_obs": int(X_weekly.shape[0]),
    "n_channels": len(channel_columns),
    "channel_columns": channel_columns,
    "avg_ltv_per_customer": round(avg_ltv, 4),
    "lift_tests_applied": [
        {
            "label": label, "channel": ch, "start": ts, "end": te,
            "delta_y_conv": dy_conv, "sigma_conv": sg_conv,
            "delta_y_ltv": round(dy_conv * avg_ltv, 2),
            "sigma_ltv": round(sg_conv * avg_ltv, 2),
            "n_weeks": int(len(window_index_map[label])),
        }
        for (label, ch, ts, te, _, _), (_, _, _, _, dy_conv, sg_conv)
        in zip(LIFT_TESTS, LIFT_TESTS_CONV)
    ],
    "convergence": {
        "rhat_max":       round(rhat_max, 4),
        "ess_min":        round(ess_min, 1),
        "divergences":    divs,
        "rhat_gate_pass": rhat_gate,
        "ess_gate_pass":  ess_gate,
    },
    "baseline_pct": round(baseline_pct, 4),
    "windowed_icac": windowed_icac_map,
    "icac_aggregate_diagnostic": icac_aggregate,
    "iroas": iroas,
    "benchmarks": {ch: {"point_estimate": be, "window_start": ts, "window_end": te,
                        "tolerance": TOLERANCE.get(ch, DEFAULT_TOLERANCE)}
                   for ch, (be, ts, te) in benchmarks.items()},
    "gates": gates,
    "all_gates_pass": all_pass,
    "contribution_api_used": api_used,
    "caveats": [
        "Q22: iOS/Android 50/50 spend split unconfirmed by Abheek — iOS vs. Android LTV attribution may shift if actual allocation differs.",
        "Q23: iOS pacing confound (r=0.48 with total conversions) carries into LTV model since LTV=f(conversions). Mechanism 2 windowed priors mitigate for tested channels but structural risk is not eliminated.",
    ],
    "notes": (
        "Model 2 — y=LTV_3YEAR (weekly sum, dollars). Mechanism 2 windowed priors. "
        "M3.5 calibration: D019-rev, D021, D022, D023, D024. M3.5b 2026-05-19 "
        "Fix-A (D027 pending APPROVED): lift δ_y and σ scaled by (W-MON window "
        "days / test days inclusive) to align prior basis with model's weekly "
        "cadence; LTV-unit scaling propagates the factor via `* avg_ltv`. See "
        "drafts/i7_window_reconciliation_2026-05-18.md and "
        "proposals/2026-05-19_d027_window_basis_correction.md. Canonical M3.5 "
        "(pre-Fix-A) snapshot preserved at ltv_convergence.json + ltv_trace.nc. "
        "iCAC = spend / (ltv_contribution / avg_ltv). iROAS = ltv_contribution / spend."
    ),
}

out_path = OUT_P2_04 / "metrics" / "ltv_window_scaled.json"
with open(out_path, "w") as f:
    json.dump(result, f, indent=2)

print(f"\nSaved: {out_path}")

print("\n=== Script 09 Gate Summary (M3.5: D019-rev / D021 / D022 / D023 / D024) ===")
print(f"  Model:         Model 2 (y=LTV_3YEAR)")
print(f"  avg_ltv:       ${avg_ltv:,.2f}")
print(f"  Rhat < 1.05:   {'PASS' if rhat_gate else 'FAIL'}  ({rhat_max:.4f})")
print(f"  ESS > 400:     {'PASS' if ess_gate else 'FAIL'}  ({ess_min:.0f})")
print(f"  Divergences:   {divs}")
print(f"  Baseline <20%: {'PASS' if baseline_pct < 0.20 else 'FAIL'}  ({baseline_pct*100:.1f}%)")
for ch, (bench, t_start, t_end) in benchmarks.items():
    g = gates.get(f"gate_icac_windowed_{ch}", False)
    v = windowed_icac_map.get(ch)
    r = iroas.get(ch, 0.0)
    tol = TOLERANCE.get(ch, DEFAULT_TOLERANCE)
    if v is not None:
        print(f"  iCAC_windowed {ch:<18}: {'PASS' if g else 'FAIL'}  "
              f"(${v:.2f} vs benchmark ${bench:.2f} ± ${tol:.0f})  iROAS={r:.4f}")
    else:
        print(f"  iCAC_windowed {ch:<18}: FAIL  (None)")
print(f"\nAll M3.5 gates passed: {all_pass}")
if all_pass:
    print("\nREADY: Proceed to Script 10 (Meta-Web charts) and Task 11 (state log + promotion proposal).")
else:
    print("\nFailing gates surfaced above. Decision point if Meta Web windowed iCAC outside $106–$206.")
