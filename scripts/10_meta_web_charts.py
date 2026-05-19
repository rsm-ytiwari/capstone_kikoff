#!/usr/bin/env python
"""
Script 10: 6-chart Meta-Web output set from Script 09's idata (y=LTV_3YEAR model).

Charts saved to outputs/P2_04_full_channel/figures/meta_web_*.png:
  1. meta_web_icac_baseline.png    — baseline iCAC point + 95% HDI bar
  2. meta_web_iroas_baseline.png   — baseline iROAS point + 95% HDI bar
  3. meta_web_icac_over_time.png   — weekly iCAC time series + CI band
  4. meta_web_iroas_over_time.png  — weekly iROAS time series + CI band
  5. meta_web_spend_dist.png       — histogram of weekly meta_web spend
  6. meta_web_saturation_curve.png — Northbeam-style: spend X-axis, iCAC left,
                                     LTV revenue right, 95% CI band, median spend line

iROAS = ltv_contribution / spend  (LTV $ per $ spent)
iCAC  = spend / (ltv_contribution / avg_ltv)  ($ per implied conversion)

Run from repo root:
    my-notebook-project/.venv/bin/python scripts/10_meta_web_charts.py
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
import arviz as az
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

from src.config import SPEND_FILE, LTV_FILE, OUT_P2_04

TRACE_PATH = OUT_P2_04 / "traces" / "ltv_trace.nc"
CONV_JSON  = OUT_P2_04 / "metrics" / "ltv_convergence.json"
FIG_DIR    = OUT_P2_04 / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

print("=== Script 10: Meta-Web 6-Chart Set (Model 2 / y=LTV_3YEAR) ===\n")

# ---------------------------------------------------------------------------
# Reload preprocessing (fast — no MCMC)
# ---------------------------------------------------------------------------
spend_raw = pd.read_csv(SPEND_FILE, parse_dates=["DS"])
platform_map = {"iso": "ios", "web and app": "web", "iOS and android": "ios"}
spend_raw["PLATFORM"] = spend_raw["PLATFORM"].replace(platform_map)
channel_map = {
    "facebook": "meta", "google": "google", "applovin": "applovin",
    "tiktok": "tiktok", "apple_search": "apple_search", "Stackadapt": "dsp",
    "appvertiser": "dsp", "Inmobidsp": "dsp", "liftoff": "liftoff",
    "podcast": "podcast", "ctv": "ctv", "linear_tv": "linear_tv",
    "influencer": "influencer", "Others": "others",
}
spend_raw["CHANNEL"] = spend_raw["SOURCE_GROUP"].map(channel_map)
spend_filt = spend_raw[
    spend_raw["CHANNEL"].notna()
    & (spend_raw["DS"] >= "2024-07-01")
    & (spend_raw["DS"] <= "2026-03-31")
].copy()
col_rename = {
    "linear_tv_web": "linear_tv", "ctv_web": "ctv",
    "apple_search_ios": "apple_search", "podcast_web": "podcast",
    "influencer_web": "influencer", "liftoff_ios": "liftoff",
    "liftoff_android": "liftoff", "dsp_ios": "dsp", "dsp_android": "dsp",
    "dsp_web": "dsp", "others_ios": "others", "others_android": "others",
    "others_web": "others", "applovin_web": "applovin_android",
}
spend_filt["col"] = (spend_filt["CHANNEL"] + "_" + spend_filt["PLATFORM"]).replace(col_rename)
spend_weekly = (
    spend_filt.groupby([pd.Grouper(key="DS", freq="W-MON"), "col"])["TOTAL_SPEND"]
    .sum().unstack(fill_value=0.0).rename_axis(None, axis=1)
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

channel_columns = sorted(spend_weekly.columns.tolist())
spend_weekly = spend_weekly[channel_columns]
X_weekly = spend_weekly.reset_index().rename(columns={"DS": "date"})
week_dates = pd.to_datetime(X_weekly["date"])

avg_ltv = ltv_weekly["LTV_3YEAR"].sum() / ltv_weekly["CONVERSIONS"].sum()
print(f"avg_ltv_per_customer: ${avg_ltv:,.2f}")

meta_web_idx = channel_columns.index("meta_web")
mw_spend = X_weekly["meta_web"].values       # (n_weeks,) — weekly spend $
mw_spend_total = float(mw_spend.sum())
print(f"meta_web total spend (93 weeks): ${mw_spend_total:,.0f}")
print(f"meta_web median weekly spend:    ${np.median(mw_spend):,.0f}")

# ---------------------------------------------------------------------------
# Load idata trace
# ---------------------------------------------------------------------------
print(f"\nLoading trace: {TRACE_PATH}")
idata = az.from_netcdf(str(TRACE_PATH))
posterior_vars = list(idata.posterior.data_vars)
print(f"Posterior variables: {posterior_vars}")

# Per-draw channel contributions in original scale (LTV $) — prefer _original_scale variable
# channel_contribution is normalized; channel_contribution_original_scale is in y units.
contrib_key = (
    "channel_contribution_original_scale"
    if "channel_contribution_original_scale" in posterior_vars
    else "channel_contribution"
)
print(f"Using contribution variable: {contrib_key}")
contrib_da = idata.posterior[contrib_key]
# Stack chains and draws: (n_draws_total, n_weeks, n_channels)
n_chains, n_draws_per, n_weeks, n_chan = contrib_da.values.shape
contrib_all = contrib_da.values.reshape(n_chains * n_draws_per, n_weeks, n_chan)

# meta_web per-draw weekly contributions: (n_draws_total, n_weeks)
mw_contrib_draws = contrib_all[:, :, meta_web_idx]     # LTV $ per week per draw

# Verify scale against script 09 JSON
with open(CONV_JSON) as f:
    conv09 = json.load(f)
# M3.5: script 09 now exposes `icac_aggregate_diagnostic` (renamed from `icac`)
# alongside `windowed_icac`. Use aggregate for the scale-check (full-history
# Meta Web iCAC); windowed iCAC for gate evaluation lives in the JSON
# under `windowed_icac.meta_web`.
expected_total = conv09["icac_aggregate_diagnostic"]["meta_web"]
expected_mw_contrib = mw_spend_total / (expected_total * avg_ltv / avg_ltv)
print(f"Scale check — script 09 meta_web aggregate iCAC: ${expected_total:,.2f}  "
      f"(windowed iCAC: ${conv09['windowed_icac']['meta_web']:,.2f})")
print(f"Mean per-draw total contrib: ${mw_contrib_draws.sum(axis=1).mean():,.0f}")

# ---------------------------------------------------------------------------
# Derived per-draw metrics
# ---------------------------------------------------------------------------
# Baseline (aggregate over all weeks): per-draw scalar
mw_contrib_total_draws = mw_contrib_draws.sum(axis=1)     # (n_draws,)
baseline_iroas_draws = mw_contrib_total_draws / mw_spend_total   # LTV/$ per draw
baseline_icac_draws  = (
    mw_spend_total / (mw_contrib_total_draws / avg_ltv)    # $ per implied conv
)

# Weekly metrics — only for weeks with nonzero spend
spend_nonzero = mw_spend > 0
# Weekly iROAS: (n_draws, n_weeks_nonzero)
weekly_iroas_draws = mw_contrib_draws[:, spend_nonzero] / mw_spend[spend_nonzero]
# Weekly iCAC: (n_draws, n_weeks_nonzero)
weekly_icac_draws  = (
    mw_spend[spend_nonzero]
    / (mw_contrib_draws[:, spend_nonzero] / avg_ltv)
)
week_dates_nz = week_dates[spend_nonzero]

def hdi95(arr):
    """Return (lo, hi) 95% HDI for a 1D numpy array."""
    result = az.hdi(arr, hdi_prob=0.95)
    if hasattr(result, "values"):
        return float(result.values[0]), float(result.values[1])
    return float(result[0]), float(result[1])

hdi_iroas_preview = hdi95(baseline_iroas_draws)
print(f"\nBaseline iROAS: {baseline_iroas_draws.mean():.4f} "
      f"[{hdi_iroas_preview[0]:.4f}, {hdi_iroas_preview[1]:.4f}]")
print(f"Baseline iCAC:  ${baseline_icac_draws.mean():,.2f}")

# ---------------------------------------------------------------------------
# Saturation curve — parameter-based (Northbeam-style)
# Using posterior samples of adstock + saturation parameters
# ---------------------------------------------------------------------------
posterior_vars = list(idata.posterior.data_vars)
median_spend = float(np.median(mw_spend[mw_spend > 0]))
print(f"\nChecking saturation parameters in posterior...")

SAT_CURVE_OK = False
spend_range = np.linspace(0, mw_spend.max() * 1.3, 300)
icac_curve_draws = None
ltv_curve_draws  = None

# Try extracting saturation params (PyMC-Marketing v0.19.3 naming)
adstock_key  = "adstock_alpha"   if "adstock_alpha"   in posterior_vars else None
sat_lam_key  = "saturation_lam"  if "saturation_lam"  in posterior_vars else None
sat_beta_key = "saturation_beta" if "saturation_beta" in posterior_vars else None

if all([adstock_key, sat_lam_key]):
    print(f"  Found: {adstock_key}, {sat_lam_key}")
    alpha_vals = idata.posterior[adstock_key].values.reshape(-1, n_chan)[:, meta_web_idx]
    lam_vals   = idata.posterior[sat_lam_key].values.reshape(-1, n_chan)[:, meta_web_idx]

    # Sub-sample draws for speed (2000 should be enough for smooth CI)
    rng = np.random.default_rng(42)
    n_samp = min(2000, len(alpha_vals))
    sidx = rng.choice(len(alpha_vals), n_samp, replace=False)
    alpha_s = alpha_vals[sidx]
    lam_s   = lam_vals[sidx]

    # Vectorized saturation curve
    # saturation_beta is in PyMC's internal normalized scale — do NOT use it directly.
    # Instead, calibrate effective beta in LTV $ from the actual posterior contributions:
    #   beta_eff = total_ltv_contribution_per_draw / sum(logistic_sat(adstock(spend_t), lam))
    # This anchors the curve to the model's observed attribution while using the correct shape.

    # Steady-state adstock coeff per draw: (n_samp,)
    adstock_coeffs = (1 - alpha_s**5) / np.where(np.abs(1 - alpha_s) > 1e-9, 1 - alpha_s, 1e-9)

    # Normalize spend to [0, 1] range — lam was learned in PyMC's normalized spend units,
    # not dollar units. Without normalization, lam * dollar_spend >> 1 and the saturation
    # function collapses to 1.0 everywhere, making the curve appear linear.
    max_mw_spend = float(mw_spend.max())

    # Historical adstocked spend (normalized): (n_samp, n_weeks)
    adstocked_hist = adstock_coeffs[:, None] * (mw_spend[None, :] / max_mw_spend)

    # Historical saturation values: (n_samp, n_weeks)
    sat_hist = (
        (1 - np.exp(-lam_s[:, None] * adstocked_hist))
        / (1 + np.exp(-lam_s[:, None] * adstocked_hist))
    )
    sat_sum = sat_hist.sum(axis=1)                             # (n_samp,)

    # Posterior LTV contributions for these draws: (n_samp, n_weeks)
    contrib_samp = mw_contrib_draws[sidx, :]                   # (n_samp, n_weeks)
    contrib_total = contrib_samp.sum(axis=1)                    # (n_samp,)

    # Effective beta in LTV scale: (n_samp,)
    beta_eff = np.where(sat_sum > 0, contrib_total / sat_sum, 0.0)

    # Sweep spend range: (n_samp, n_spend_levels)
    x_arr = spend_range[spend_range > 0]                        # skip 0
    adstocked_sweep = adstock_coeffs[:, None] * (x_arr[None, :] / max_mw_spend)  # normalized
    sat_sweep = (
        (1 - np.exp(-lam_s[:, None] * adstocked_sweep))
        / (1 + np.exp(-lam_s[:, None] * adstocked_sweep))
    )
    ltv_sweep = beta_eff[:, None] * sat_sweep                   # (n_samp, n_x) — LTV $
    impl_conv_sweep = ltv_sweep / avg_ltv                       # implied conversions
    with np.errstate(divide="ignore", invalid="ignore"):
        icac_sweep = np.where(impl_conv_sweep > 0, x_arr[None, :] / impl_conv_sweep, np.nan)
        iroas_sweep = np.where(x_arr[None, :] > 0, ltv_sweep / x_arr[None, :], np.nan)

    # Pad back to full spend_range (including 0)
    n_full = len(spend_range)
    n_pos  = len(x_arr)
    icac_curves_full  = np.full((n_samp, n_full), np.nan)
    ltv_curves_full   = np.zeros((n_samp, n_full))
    iroas_curves_full = np.full((n_samp, n_full), np.nan)
    icac_curves_full[:, n_full - n_pos:]  = icac_sweep
    ltv_curves_full[:, n_full - n_pos:]   = ltv_sweep
    iroas_curves_full[:, n_full - n_pos:] = iroas_sweep

    icac_curve_mean  = np.nanmedian(icac_curves_full, axis=0)
    icac_curve_lo    = np.nanpercentile(icac_curves_full, 2.5, axis=0)
    icac_curve_hi    = np.nanpercentile(icac_curves_full, 97.5, axis=0)
    ltv_curve_mean   = np.nanmedian(ltv_curves_full, axis=0)
    iroas_curve_mean = np.nanmedian(iroas_curves_full, axis=0)
    iroas_curve_lo   = np.nanpercentile(iroas_curves_full, 2.5, axis=0)
    iroas_curve_hi   = np.nanpercentile(iroas_curves_full, 97.5, axis=0)
    SAT_CURVE_OK = True
    print(f"  Saturation curve computed. beta_eff range: ${beta_eff.min():,.0f}–${beta_eff.max():,.0f}")
    print(f"  iCAC at median spend (${median_spend:,.0f}): "
          f"${icac_curve_mean[np.searchsorted(spend_range, median_spend)]:,.0f}")
    print(f"  iROAS at median spend: "
          f"{iroas_curve_mean[np.searchsorted(spend_range, median_spend)]:.3f}x")
else:
    print(f"  WARNING: saturation keys not found in {posterior_vars}")
    print("  Falling back to observed spend-contribution scatter + smooth fit.")
    # Fallback: use observed weekly data + smooth
    obs_spend  = mw_spend[spend_nonzero]
    obs_contrib_mean = mw_contrib_draws[:, spend_nonzero].mean(axis=0)
    obs_contrib_lo   = np.percentile(mw_contrib_draws[:, spend_nonzero], 2.5, axis=0)
    obs_contrib_hi   = np.percentile(mw_contrib_draws[:, spend_nonzero], 97.5, axis=0)
    SAT_CURVE_OK = False  # will use scatter-based chart

# ---------------------------------------------------------------------------
# Plotting helpers
# ---------------------------------------------------------------------------
BLUE   = "#2563EB"
LBLUE  = "#BFDBFE"
ORANGE = "#EA580C"
GRAY   = "#6B7280"

def save_fig(name):
    p = FIG_DIR / name
    plt.savefig(p, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {p}")

def fmt_dollar(x, _):
    if x >= 1_000_000: return f"${x/1_000_000:.1f}M"
    if x >= 1_000:     return f"${x/1_000:.0f}K"
    return f"${x:.0f}"

# ---------------------------------------------------------------------------
# Chart 1: Baseline iCAC — point + 95% HDI
# ---------------------------------------------------------------------------
print("\n[Chart 1] Baseline iCAC...")
fig, ax = plt.subplots(figsize=(5, 4))
mean_icac = float(np.mean(baseline_icac_draws))  # kept for JSON output
median_icac = float(np.median(baseline_icac_draws))  # robust to right skew of iCAC posterior
hdi_icac  = hdi95(baseline_icac_draws)
point_icac = median_icac  # display median (mean is in tail for skewed iCAC)
ax.barh(0, point_icac, color=BLUE, alpha=0.85, height=0.4, label=f"Median: ${point_icac:,.0f}")
ax.errorbar(
    point_icac, 0,
    xerr=[[max(0.0, point_icac - hdi_icac[0])], [max(0.0, hdi_icac[1] - point_icac)]],
    fmt="none", color="black", capsize=6, linewidth=2,
)
ax.axvline(156.89, color=ORANGE, linestyle="--", linewidth=1.5, label="Benchmark $157")
ax.set_yticks([])
ax.set_xlabel("iCAC ($ per conversion)", fontsize=11)
ax.set_title("Meta Web — Baseline iCAC\n(Model 2: y = LTV_3YEAR)", fontsize=12, fontweight="bold")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(fmt_dollar))
ax.legend(fontsize=9)
ax.text(hdi_icac[0], 0.28, f"95% HDI\n[${hdi_icac[0]:,.0f}, ${hdi_icac[1]:,.0f}]",
        ha="center", va="bottom", fontsize=8, color=GRAY)
plt.tight_layout()
save_fig("meta_web_icac_baseline.png")

# ---------------------------------------------------------------------------
# Chart 2: Baseline iROAS — point + 95% HDI
# ---------------------------------------------------------------------------
print("[Chart 2] Baseline iROAS...")
fig, ax = plt.subplots(figsize=(5, 4))
mean_iroas = float(np.mean(baseline_iroas_draws))
hdi_iroas  = hdi95(baseline_iroas_draws)
ax.barh(0, mean_iroas, color=BLUE, alpha=0.85, height=0.4, label=f"Mean: {mean_iroas:.2f}x")
ax.errorbar(
    mean_iroas, 0,
    xerr=[[mean_iroas - hdi_iroas[0]], [hdi_iroas[1] - mean_iroas]],
    fmt="none", color="black", capsize=6, linewidth=2,
)
ax.axvline(1.0, color=ORANGE, linestyle="--", linewidth=1.5, label="Break-even 1.0x")
ax.set_yticks([])
ax.set_xlabel("iROAS (LTV $ per $ spent)", fontsize=11)
ax.set_title("Meta Web — Baseline iROAS\n(Model 2: y = LTV_3YEAR)", fontsize=12, fontweight="bold")
ax.legend(fontsize=9)
ax.text(hdi_iroas[0], 0.28, f"95% HDI\n[{hdi_iroas[0]:.2f}x, {hdi_iroas[1]:.2f}x]",
        ha="center", va="bottom", fontsize=8, color=GRAY)
plt.tight_layout()
save_fig("meta_web_iroas_baseline.png")

# ---------------------------------------------------------------------------
# Chart 3: iCAC over time — weekly line + CI band
# ---------------------------------------------------------------------------
print("[Chart 3] iCAC over time...")
icac_mean = np.mean(weekly_icac_draws, axis=0)
icac_lo   = np.percentile(weekly_icac_draws, 2.5, axis=0)
icac_hi   = np.percentile(weekly_icac_draws, 97.5, axis=0)

fig, ax = plt.subplots(figsize=(11, 4))
ax.plot(week_dates_nz, icac_mean, color=BLUE, linewidth=1.8, label="Posterior mean iCAC")
ax.fill_between(week_dates_nz, icac_lo, icac_hi, color=LBLUE, alpha=0.6, label="95% CI")
ax.axhline(156.89, color=ORANGE, linestyle="--", linewidth=1.2, label="Benchmark $157")
ax.set_xlabel("Week", fontsize=10)
ax.set_ylabel("iCAC ($ per conversion)", fontsize=10)
ax.set_title("Meta Web — iCAC Over Time (Model 2: y = LTV_3YEAR)", fontsize=12, fontweight="bold")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(fmt_dollar))
ax.legend(fontsize=9)
ax.grid(axis="y", alpha=0.3)
plt.tight_layout()
save_fig("meta_web_icac_over_time.png")

# ---------------------------------------------------------------------------
# Chart 4: iROAS over time — weekly line + CI band
# ---------------------------------------------------------------------------
print("[Chart 4] iROAS over time...")
iroas_mean = np.mean(weekly_iroas_draws, axis=0)
iroas_lo   = np.percentile(weekly_iroas_draws, 2.5, axis=0)
iroas_hi   = np.percentile(weekly_iroas_draws, 97.5, axis=0)

fig, ax = plt.subplots(figsize=(11, 4))
ax.plot(week_dates_nz, iroas_mean, color=BLUE, linewidth=1.8, label="Posterior mean iROAS")
ax.fill_between(week_dates_nz, iroas_lo, iroas_hi, color=LBLUE, alpha=0.6, label="95% CI")
ax.axhline(1.0, color=ORANGE, linestyle="--", linewidth=1.2, label="Break-even 1.0x")
ax.set_xlabel("Week", fontsize=10)
ax.set_ylabel("iROAS (LTV $ per $ spent)", fontsize=10)
ax.set_title("Meta Web — iROAS Over Time (Model 2: y = LTV_3YEAR)", fontsize=12, fontweight="bold")
ax.legend(fontsize=9)
ax.grid(axis="y", alpha=0.3)
plt.tight_layout()
save_fig("meta_web_iroas_over_time.png")

# ---------------------------------------------------------------------------
# Chart 5: Spend distribution (histogram)
# ---------------------------------------------------------------------------
print("[Chart 5] Spend distribution...")
fig, ax = plt.subplots(figsize=(7, 4))
spend_nonzero_vals = mw_spend[mw_spend > 0]
ax.hist(spend_nonzero_vals, bins=20, color=BLUE, alpha=0.8, edgecolor="white")
ax.axvline(np.median(spend_nonzero_vals), color=ORANGE, linestyle="--",
           linewidth=1.8, label=f"Median ${np.median(spend_nonzero_vals):,.0f}")
ax.set_xlabel("Weekly Spend ($)", fontsize=10)
ax.set_ylabel("Number of Weeks", fontsize=10)
ax.set_title("Meta Web — Weekly Spend Distribution", fontsize=12, fontweight="bold")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(fmt_dollar))
ax.legend(fontsize=9)
ax.grid(axis="y", alpha=0.3)
plt.tight_layout()
save_fig("meta_web_spend_dist.png")

# ---------------------------------------------------------------------------
# Chart 6: Saturation curve — Northbeam-style
# ---------------------------------------------------------------------------
print("[Chart 6] Saturation curve (Northbeam-style)...")

if SAT_CURVE_OK:
    fig, ax1 = plt.subplots(figsize=(9, 5))
    ax2 = ax1.twinx()

    # iCAC curve (left axis)
    valid = ~np.isnan(icac_curve_mean)
    ax1.plot(spend_range[valid], icac_curve_mean[valid],
             color=BLUE, linewidth=2, label="Posterior median iCAC")
    ax1.fill_between(spend_range[valid], icac_curve_lo[valid], icac_curve_hi[valid],
                     color=LBLUE, alpha=0.5, label="95% CI")
    ax1.axhline(156.89, color=ORANGE, linestyle="--", linewidth=1.2, label="Benchmark $157")

    # LTV revenue curve (right axis)
    ax2.plot(spend_range, ltv_curve_mean / 1e6, color=GRAY, linewidth=1.5,
             linestyle=":", alpha=0.8, label="Expected LTV (right)")
    ax2.set_ylabel("Estimated LTV Attribution ($M / week)", fontsize=9, color=GRAY)
    ax2.tick_params(axis="y", labelcolor=GRAY)

    # Vertical line at median historical spend
    ax1.axvline(median_spend, color="black", linestyle="-.", linewidth=1.5,
                label=f"Median hist. spend ${median_spend:,.0f}")

    ax1.set_xlabel("Weekly Spend ($)", fontsize=10)
    ax1.set_ylabel("iCAC ($ per conversion)", fontsize=10)
    ax1.set_title("Meta Web — Saturation Curve\n(Spend vs. iCAC, Model 2: y = LTV_3YEAR)",
                  fontsize=12, fontweight="bold")
    ax1.xaxis.set_major_formatter(mticker.FuncFormatter(fmt_dollar))
    ax1.yaxis.set_major_formatter(mticker.FuncFormatter(fmt_dollar))
    ax1.set_ylim(bottom=0)

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, fontsize=8, loc="upper left")
    ax1.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    save_fig("meta_web_saturation_curve.png")

else:
    # Fallback: observed spend-contribution scatter + smooth
    fig, ax1 = plt.subplots(figsize=(9, 5))
    obs_icac_mean = obs_spend / (obs_contrib_mean / avg_ltv)
    obs_icac_lo   = obs_spend / (obs_contrib_hi / avg_ltv)   # note: high contrib → low iCAC
    obs_icac_hi   = obs_spend / (obs_contrib_lo / avg_ltv)
    sort_idx = np.argsort(obs_spend)
    ax1.scatter(obs_spend[sort_idx], obs_icac_mean[sort_idx],
                color=BLUE, s=30, alpha=0.7, label="Weekly observed iCAC (posterior mean)")
    ax1.fill_between(obs_spend[sort_idx], obs_icac_lo[sort_idx], obs_icac_hi[sort_idx],
                     alpha=0.2, color=LBLUE)
    ax1.axvline(median_spend, color="black", linestyle="-.", linewidth=1.5,
                label=f"Median spend ${median_spend:,.0f}")
    ax1.axhline(156.89, color=ORANGE, linestyle="--", linewidth=1.2, label="Benchmark $157")
    ax1.set_xlabel("Weekly Spend ($)", fontsize=10)
    ax1.set_ylabel("iCAC ($ per conversion)", fontsize=10)
    ax1.set_title("Meta Web — Saturation Curve (Observed)\n(Model 2: y = LTV_3YEAR)",
                  fontsize=12, fontweight="bold")
    ax1.xaxis.set_major_formatter(mticker.FuncFormatter(fmt_dollar))
    ax1.yaxis.set_major_formatter(mticker.FuncFormatter(fmt_dollar))
    ax1.legend(fontsize=8)
    ax1.grid(alpha=0.3)
    plt.tight_layout()
    save_fig("meta_web_saturation_curve.png")

# ---------------------------------------------------------------------------
# Chart 8: iROAS Saturation Curve — Northbeam-style (spend vs. iROAS)
# Mirrors Chart 6 but shows diminishing iROAS (LTV per $ spent) as spend rises.
# ---------------------------------------------------------------------------
print("[Chart 8] iROAS Saturation curve...")

if SAT_CURVE_OK:
    fig, ax1 = plt.subplots(figsize=(9, 5))
    ax2 = ax1.twinx()

    # iROAS curve (left axis)
    valid = ~np.isnan(iroas_curve_mean)
    ax1.plot(spend_range[valid], iroas_curve_mean[valid],
             color=ORANGE, linewidth=2, label="Posterior median iROAS")
    ax1.fill_between(spend_range[valid], iroas_curve_lo[valid], iroas_curve_hi[valid],
                     color="#FED7AA", alpha=0.5, label="95% CI")
    ax1.axhline(1.0, color=GRAY, linestyle="--", linewidth=1.5, label="Break-even (1.0x)")

    # LTV revenue curve (right axis)
    ax2.plot(spend_range, ltv_curve_mean / 1e6, color=GRAY, linewidth=1.5,
             linestyle=":", alpha=0.8, label="Expected LTV (right)")
    ax2.set_ylabel("Estimated LTV Attribution ($M / week)", fontsize=9, color=GRAY)
    ax2.tick_params(axis="y", labelcolor=GRAY)

    # Vertical line at median historical spend
    ax1.axvline(median_spend, color="black", linestyle="-.", linewidth=1.5,
                label=f"Median hist. spend ${median_spend:,.0f}")

    ax1.set_xlabel("Weekly Spend ($)", fontsize=10)
    ax1.set_ylabel("iROAS (LTV $ per $ spent)", fontsize=10)
    ax1.set_title("Meta Web — iROAS Saturation Curve\n(Spend vs. iROAS, Model 2: y = LTV_3YEAR)",
                  fontsize=12, fontweight="bold")
    ax1.xaxis.set_major_formatter(mticker.FuncFormatter(fmt_dollar))
    ax1.set_ylim(bottom=0)

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, fontsize=8, loc="upper right")
    ax1.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    save_fig("meta_web_iroas_saturation_curve.png")
else:
    print("  Skipped — SAT_CURVE_OK is False (fallback saturation path has no iROAS curve).")

# ---------------------------------------------------------------------------
# Chart 7: LTV over time — weekly LTV_3YEAR contribution with 95% CI
# Model 2 only. Shows weekly LTV dollars attributed to Meta Web.
# ---------------------------------------------------------------------------
print("[Chart 7] LTV over time (weekly LTV_3YEAR contribution)...")

ltv_contrib_mean = mw_contrib_draws.mean(axis=0)           # (n_weeks,)
ltv_contrib_lo   = np.percentile(mw_contrib_draws, 2.5, axis=0)
ltv_contrib_hi   = np.percentile(mw_contrib_draws, 97.5, axis=0)

fig, ax = plt.subplots(figsize=(11, 4.5))
ax.plot(week_dates, ltv_contrib_mean / 1e6, color=BLUE, linewidth=1.5,
        label="Posterior mean LTV contribution")
ax.fill_between(week_dates, ltv_contrib_lo / 1e6, ltv_contrib_hi / 1e6,
                color=LBLUE, alpha=0.4, label="95% CI")
ax.set_xlabel("Week", fontsize=10)
ax.set_ylabel("LTV_3YEAR Contribution ($M / week)", fontsize=10)
ax.set_title("Meta Web — LTV Over Time\n(Weekly LTV_3YEAR Attributed, Model 2: y = LTV_3YEAR)",
             fontsize=12, fontweight="bold")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"${v:.1f}M"))
ax.legend(fontsize=9)
ax.grid(axis="y", alpha=0.3)
plt.tight_layout()
save_fig("meta_web_ltv_over_time.png")

# ---------------------------------------------------------------------------
# Export chart-ready CSVs for Streamlit dashboard (no trace dependency)
# Saved to outputs/P2_04_full_channel/charts/ — these are committed to the repo.
# ---------------------------------------------------------------------------
CHART_DIR = OUT_P2_04 / "charts"
CHART_DIR.mkdir(parents=True, exist_ok=True)
print("\n[Export] Saving chart-ready CSVs for dashboard...")

# 1. Weekly iCAC time series — use RATIO OF POSTERIOR MEANS (not mean of weekly
# iCAC draws). The mean-of-ratios is biased upward by Jensen's inequality and
# diverges from the aggregate iCAC reported by script 09; the ratio-of-means
# matches `spend / (mean_contribution / avg_ltv)` so the headline and the
# per-week series stay numerically consistent.
mw_contrib_nz_mean = mw_contrib_draws[:, spend_nonzero].mean(axis=0)
mw_contrib_nz_lo   = np.percentile(mw_contrib_draws[:, spend_nonzero], 2.5,  axis=0)
mw_contrib_nz_hi   = np.percentile(mw_contrib_draws[:, spend_nonzero], 97.5, axis=0)
sp_nz              = mw_spend[spend_nonzero]
icac_time_mean = sp_nz / (mw_contrib_nz_mean / avg_ltv)
icac_time_lo   = sp_nz / (mw_contrib_nz_hi   / avg_ltv)   # high contrib → low iCAC bound
icac_time_hi   = sp_nz / (mw_contrib_nz_lo   / avg_ltv)   # low contrib  → high iCAC bound
# Enforce D003 modeling cutoff (2026-03-31). Q29 fix — without this, the
# dashboard iCAC-over-time chart shows partial April weeks that misrepresent
# the trend. Source-side fix; app/data_loader.py also enforces this as defense in depth.
CUTOFF = "2026-03-31"

_df = pd.DataFrame({
    "date":  pd.DatetimeIndex(week_dates_nz).strftime("%Y-%m-%d"),
    "mean":  icac_time_mean,
    "lo95":  icac_time_lo,
    "hi95":  icac_time_hi,
})
_df = _df[_df["date"] <= CUTOFF]
_df.to_csv(CHART_DIR / "meta_web_icac_time.csv", index=False)

# 2. Weekly iROAS time series — ratio of posterior means (Jensen-consistent with aggregate)
iroas_time_mean = mw_contrib_nz_mean / sp_nz
iroas_time_lo   = mw_contrib_nz_lo   / sp_nz
iroas_time_hi   = mw_contrib_nz_hi   / sp_nz
_df = pd.DataFrame({
    "date":  pd.DatetimeIndex(week_dates_nz).strftime("%Y-%m-%d"),
    "mean":  iroas_time_mean,
    "lo95":  iroas_time_lo,
    "hi95":  iroas_time_hi,
})
_df = _df[_df["date"] <= CUTOFF]
_df.to_csv(CHART_DIR / "meta_web_iroas_time.csv", index=False)

# 3. Weekly LTV contribution
_df = pd.DataFrame({
    "date":  pd.DatetimeIndex(week_dates).strftime("%Y-%m-%d"),
    "mean":  ltv_contrib_mean,
    "lo95":  ltv_contrib_lo,
    "hi95":  ltv_contrib_hi,
})
_df = _df[_df["date"] <= CUTOFF]
_df.to_csv(CHART_DIR / "meta_web_ltv_time.csv", index=False)

# 4. iCAC saturation curve
if SAT_CURVE_OK:
    pd.DataFrame({
        "spend":     spend_range,
        "icac_mean": icac_curve_mean,
        "icac_lo95": icac_curve_lo,
        "icac_hi95": icac_curve_hi,
        "ltv_mean":  ltv_curve_mean,
    }).to_csv(CHART_DIR / "meta_web_icac_saturation.csv", index=False)

    # 5. iROAS saturation curve
    pd.DataFrame({
        "spend":      spend_range,
        "iroas_mean": iroas_curve_mean,
        "iroas_lo95": iroas_curve_lo,
        "iroas_hi95": iroas_curve_hi,
        "ltv_mean":   ltv_curve_mean,
    }).to_csv(CHART_DIR / "meta_web_iroas_saturation.csv", index=False)

# 6. Weekly spend distribution
_df = pd.DataFrame({
    "date":        pd.DatetimeIndex(week_dates).strftime("%Y-%m-%d"),
    "meta_web_spend": mw_spend,
})
_df = _df[_df["date"] <= CUTOFF]
_df.to_csv(CHART_DIR / "meta_web_spend_weekly.csv", index=False)

# 7. Baseline metrics JSON (iCAC + iROAS + HDI + model metadata from conv09)
import json as _json
# NOTE: iCAC posterior is right-skewed (ratio of two positives) — its mean sits in the
# right tail and is a poor headline. Export the MEDIAN as the canonical iCAC point estimate;
# preserve the mean as `icac_mean_skewed` for audit.
baseline_export = {
    "channel":           "meta_web",
    "model":             "Model 2 (y=LTV_3YEAR)",
    "last_updated":      pd.Timestamp.now().strftime("%Y-%m-%d"),
    "icac_median":       round(median_icac, 2),
    "icac_mean":         round(median_icac, 2),   # alias kept for dashboard backward-compat
    "icac_mean_skewed":  round(mean_icac, 2),     # right-tail mean — for audit only
    "icac_hdi_lo":       round(hdi_icac[0], 2),
    "icac_hdi_hi":       round(hdi_icac[1], 2),
    "iroas_mean":        round(mean_iroas, 4),
    "iroas_median":      round(float(np.median(baseline_iroas_draws)), 4),
    "iroas_hdi_lo":      round(hdi_iroas[0], 4),
    "iroas_hdi_hi":      round(hdi_iroas[1], 4),
    "iroas_below_breakeven_pct": round(float((baseline_iroas_draws < 1.0).mean() * 100), 1),
    "avg_ltv":           round(avg_ltv, 2),
    "median_weekly_spend": round(median_spend, 0),
    "rhat_max":          conv09["convergence"]["rhat_max"],
    "ess_min":           conv09["convergence"]["ess_min"],
    "baseline_pct":      round(conv09["baseline_pct"] * 100, 1),
    "northbeam_iroas_ref": 1.79,
    "northbeam_icac_ref":  274.0,
    "lift_test_benchmark": 156.89,
    "agg_iCAC_script09":   float(conv09["icac_aggregate_diagnostic"]["meta_web"]),
    "windowed_iCAC_script09": float(conv09["windowed_icac"]["meta_web"]),
}
with open(CHART_DIR / "meta_web_baseline.json", "w") as f:
    _json.dump(baseline_export, f, indent=2)

print(f"  Chart-ready CSVs saved to: {CHART_DIR}")
for fname in ["meta_web_icac_time.csv", "meta_web_iroas_time.csv", "meta_web_ltv_time.csv",
              "meta_web_icac_saturation.csv", "meta_web_iroas_saturation.csv",
              "meta_web_spend_weekly.csv", "meta_web_baseline.json"]:
    exists = "✓" if (CHART_DIR / fname).exists() else "✗ MISSING"
    print(f"    {exists} {fname}")

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
print("\n=== Script 10 Summary ===")
print(f"  avg_ltv:              ${avg_ltv:,.2f}")
print(f"  Baseline iCAC:        ${mean_icac:,.2f}  [95% HDI: ${hdi_icac[0]:,.0f}–${hdi_icac[1]:,.0f}]")
print(f"  Baseline iROAS:       {mean_iroas:.3f}x  [95% HDI: {hdi_iroas[0]:.3f}–{hdi_iroas[1]:.3f}x]")
print(f"  iROAS < 1 (all draws): {(baseline_iroas_draws < 1.0).mean()*100:.1f}% of posterior mass")
print(f"  Median weekly spend:  ${median_spend:,.0f}")
print(f"  Saturation curve:     {'parameter-based (proper)' if SAT_CURVE_OK else 'observed scatter (fallback)'}")
print(f"\n  Charts saved to: {FIG_DIR}")
for name in [
    "meta_web_icac_baseline.png", "meta_web_iroas_baseline.png",
    "meta_web_icac_over_time.png", "meta_web_iroas_over_time.png",
    "meta_web_spend_dist.png", "meta_web_saturation_curve.png",
    "meta_web_iroas_saturation_curve.png", "meta_web_ltv_over_time.png",
]:
    exists = (FIG_DIR / name).exists()
    print(f"    {'✓' if exists else '✗'} {name}")
