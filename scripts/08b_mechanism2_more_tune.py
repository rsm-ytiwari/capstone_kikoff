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
    - Meta Jan 2026 (Kick Off January CLS-BLS): iOS, Android, Web — wide σ

Meta Jan 2026 RE-INCLUDED per D019-reversal (2026-05-18, meeting 6).
Cancelled 3-day study; iOS had only 10 conversions (implausible $1,350 iCAC),
but Android (365 conv, 99.9%) and Web (1,122 conv, 99.9%) had real data.
Per Abheek 34:21 ("It messed up growth strategies, but whatever it was,
it was the truth that happened during those three days"), included as a
wide-σ windowed prior (3× max(δ_y, 30)) so the data is present but barely
constrains the model — for completeness, not as a tight constraint.

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
from pymc_extras.prior import Prior

from src.config import SPEND_FILE, LTV_FILE, OUT_P2_04

print("=== Script 08b: Mechanism 2 — Windowed Lift Priors (tune=2000, accept=0.98) ===")
print(f"SPEND_FILE: {SPEND_FILE}")
print(f"LTV_FILE:   {LTV_FILE}")
print(f"OUT_P2_04:  {OUT_P2_04}\n")

# ---------------------------------------------------------------------------
# Lift test reference table (from Kikoff_data_incrementality.csv)
# Format: (label, channel_col, test_start_inclusive, test_end_inclusive,
#           delta_y_conversions, sigma_conversions)
#
# M3.5b 2026-05-19: lift δ_y and σ scaled to W-MON window basis (Fix-A)
# — see proposals/2026-05-19_d027_window_basis_correction.md.
# Background: I-7 reconciliation (drafts/i7_window_reconciliation_2026-05-18.md)
# found the windowed-iCAC gate was comparing N-day model spend (full W-MON
# weeks overlapping a test) against k-day lift-test conversions, mechanically
# inflating iCAC by ~N/k. Fix-A scales each row's δ_y and σ by (W-MON window
# days / test days inclusive) so the prior speaks in the same temporal basis
# as the model's weekly contributions.
#
# Per-test scaling factors:
#   Meta May 2025:   8-day test  → 14-day window (2 W-MON weeks)   × 14/8  = 1.75
#   TikTok Aug 2025: 24-day test → 28-day window (4 W-MON weeks)   × 28/24 ≈ 1.167
#   CTV Oct 2025:    27-day test → 28-day window (4 W-MON weeks)   × 28/27 ≈ 1.037
#   Meta Jan 2026:   5-day test  → 14-day window (2 W-MON weeks)   × 14/5  = 2.8
#
# sigma:
#   Meta May 2025 + TikTok Aug 2025: σ = 10% of (scaled δ_y) (Path B per D022,
#     literature-aligned default). σ-ladder 2026-05-18 (pre-Fix-A): 30% → 10%
#     → 5%; 5% degraded convergence (R-hat 1.107 / ESS 27 FAIL), 10% retained.
#   CTV: σ scaled proportionally from CI-derived 373 → 386.8 (D020 unchanged
#     in spirit; magnitude scales with δ_y).
#   Meta Jan 2026: σ = 3 × max(scaled δ_y, 30) — deliberately wide (D019-rev,
#     cancelled study; include for completeness, not as a tight constraint).
# Test ends are inclusive (end_exclusive - 1 day from the CSV).
# Originals (pre-Fix-A) preserved in mechanism2b_convergence.json (canonical
# M3.5 reference snapshot — do not overwrite).
# ---------------------------------------------------------------------------
LIFT_TESTS = [
    # Meta May 2025 — 8d test, W-MON window 14d → scale 1.75 (δ_y and σ).
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
    # M3.5 canonical: tighter prior on lam (saturation rate) per Lever C
    # diagnostic 2026-05-18. Default LogisticSaturation lam prior left the
    # posterior weakly informed (ESS 687); Gamma(α=2, β=2) (mean=1, mode=0.5)
    # discourages aggressive saturation and dramatically improves convergence
    # (ESS 2218, R-hat 1.003). Meta Web iCAC essentially unchanged ($466
    # → $470) — confirming the structural finding: saturation prior is not
    # the lever; the data drives Meta Web's full-scale iCAC to ~$470.
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
print(f"Baseline %:             {baseline_pct*100:.1f}%  (D029: gate deprecated; reported only — see baseline_split.json + Methodology page)")

# Aggregate iCAC (full-history) — retained as a diagnostic only.
# D023 deprecated this as a gate: aggregate compares full-history average
# to a test-window measurement, which is methodologically wrong.
icac_aggregate = {}
for ch in channel_columns:
    sp = float(X_weekly[ch].sum())
    co = float(chan_sum[ch])
    icac_aggregate[ch] = round(sp / co, 2) if co > 0 else None

# ---------------------------------------------------------------------------
# Windowed-iCAC helper (D023): the model's implied iCAC restricted to the
# lift-test weeks only. Compares apples-to-apples with the lift-test point
# estimate (itself a test-window measurement). Replaces the aggregate gate.
# ---------------------------------------------------------------------------
# Align contributions to a date index (required for .loc[start:end] slicing).
# The contribution APIs return either a date-indexed or integer-indexed
# DataFrame; overwrite with week_starts to be safe.
contributions.index = pd.to_datetime(week_starts.values)

def windowed_icac(channel: str, start: str, end: str) -> float | None:
    """iCAC within a date window: spend_sum / contribution_sum.

    Uses the same week-overlap convention as the lift-test prior (see lines
    ~191): any W-MON-labelled week whose Monday is within [start - 6d, end]
    overlaps the test period. Without the -6d adjustment, a test starting
    Tue/Wed would miss its containing week label.
    """
    start_ts = pd.Timestamp(start) - pd.Timedelta(days=6)
    end_ts   = pd.Timestamp(end)
    mask_X = (week_starts >= start_ts) & (week_starts <= end_ts)
    spend_w = float(X_weekly.loc[mask_X.values, channel].sum())
    contrib_w = float(contributions.loc[start_ts:end_ts, channel].sum())
    return round(spend_w / contrib_w, 2) if contrib_w > 0 else None

# ---------------------------------------------------------------------------
# Gate evaluation (D023 windowed gate; D029 baseline gate DEPRECATED — see baseline_disposition; D024 no ordering)
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
print(f"\n{'Channel':<22} {'Win iCAC':>9}  {'Bench':>7}  {'Band':>15}  {'Gate'}")
print("-" * 70)
for ch, (bench, t_start, t_end) in benchmarks.items():
    tol = TOLERANCE.get(ch, DEFAULT_TOLERANCE)
    v = windowed_icac(ch, t_start, t_end)
    windowed_icac_map[ch] = v
    in_band = (v is not None) and (bench - tol <= v <= bench + tol)
    gates[f"gate_icac_windowed_{ch}"] = in_band
    v_str = f"${v:>8.2f}" if v is not None else "    None "
    print(f"  {ch:<20} {v_str}  ${bench:>6.2f}  ${bench-tol:>5.0f}-${bench+tol:<5.0f}  {'PASS' if in_band else 'FAIL'}")

# D024: ordering gate REMOVED. Neither iOS>Android nor Android>iOS is a
# remediation target (Abheek 36:56: σ explains deviation OR Android-heavy
# customer base + saturation explains it; either direction acceptable).

# D029 (2026-05-20): D021's <20% baseline gate DEPRECATED. Baseline % still
# REPORTED (global + in-window/out-of-window split via scripts/15_baseline_split.py)
# but no PASS/FAIL flag. See state/decisions_log.md D029 + app/pages/3_Methodology.py.
print(f"\n  Rhat < 1.05:   {'PASS' if rhat_gate else 'FAIL'}  ({rhat_max:.4f})")
print(f"  ESS > 400:     {'PASS' if ess_gate else 'FAIL'}  ({ess_min:.0f})")
print(f"  Baseline %:    {baseline_pct*100:.1f}%  (D029: reported only; per-channel concentration is the new attribution-confidence diagnostic)")

gates["gate_rhat_pass"]     = rhat_gate
gates["gate_ess_pass"]      = ess_gate
baseline_disposition = (
    "D029 (2026-05-20): D021's <20% threshold gate DEPRECATED. Baseline % "
    "reported only (no PASS/FAIL). Per-channel attribution concentration ratio "
    "is the new diagnostic — see outputs/P2_04_full_channel/metrics/"
    "baseline_split.json (script: scripts/15_baseline_split.py). Reframe: "
    "Abheek's <20% target was framed against the attributed-revenue universe "
    "(~65% of total LTV per Mtg 6 #13); architecturally unreachable on the "
    "total-LTV universe without an attributed-revenue feed (Q36)."
)

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
    "baseline_disposition": baseline_disposition,
    "windowed_icac": windowed_icac_map,
    "icac_aggregate_diagnostic": icac_aggregate,
    "benchmarks": {ch: {"point_estimate": be, "window_start": ts, "window_end": te,
                        "tolerance": TOLERANCE.get(ch, DEFAULT_TOLERANCE)}
                   for ch, (be, ts, te) in benchmarks.items()},
    "gates": gates,
    "all_gates_pass": all_pass,
    "contribution_api_used": api_used,
    "notes": (
        "Mechanism 2 windowed priors. M3.5 calibration: D019-rev, D021, D022, "
        "D023, D024. M3.5b 2026-05-19 Fix-A (D027 pending APPROVED): lift δ_y "
        "and σ scaled by (W-MON window days / test days inclusive) to align "
        "prior basis with model's weekly cadence. See "
        "drafts/i7_window_reconciliation_2026-05-18.md and "
        "proposals/2026-05-19_d027_window_basis_correction.md. Canonical M3.5 "
        "(pre-Fix-A) snapshot preserved at mechanism2b_convergence.json."
    ),
}

out_path = OUT_P2_04 / "metrics" / "mechanism2b_window_scaled.json"
with open(out_path, "w") as f:
    json.dump(result, f, indent=2)

print(f"\nSaved: {out_path}")

print("\n=== Script 08b Gate Summary (M3.5: D019-rev / D022 / D023 / D024; D021 SUPERSEDED by D029 2026-05-20) ===")
print(f"  Rhat < 1.05:               {'PASS' if rhat_gate else 'FAIL'}  ({rhat_max:.4f})")
print(f"  ESS > 400:                 {'PASS' if ess_gate else 'FAIL'}  ({ess_min:.0f})")
print(f"  Baseline %:                {baseline_pct*100:.1f}%  (D029: reported only; gate deprecated)")
for ch, (bench, t_start, t_end) in benchmarks.items():
    g = gates.get(f"gate_icac_windowed_{ch}", False)
    v = windowed_icac_map.get(ch)
    tol = TOLERANCE.get(ch, DEFAULT_TOLERANCE)
    if v is not None:
        print(f"  iCAC_windowed {ch:<18}: {'PASS' if g else 'FAIL'}  "
              f"(${v:.2f} vs benchmark ${bench:.2f} ± ${tol:.0f})")
    else:
        print(f"  iCAC_windowed {ch:<18}: FAIL  (None)")
# D024: iOS > Android ordering gate removed; no print line here.
print(f"\nAll M3.5 gates passed: {all_pass}")
if all_pass:
    print("\nREADY: Proceed to Script 10 (Meta-Web charts) and Task 11 (state log + promotion proposal).")
else:
    print("\nFailing gates surfaced above. Decision point if Meta Web windowed iCAC outside $106–$206.")
