#!/usr/bin/env python
"""
Script 10b: Scale and saturation diagnostic for Model 2 (y=LTV_3YEAR).

Reads pre-computed outputs only — no raw data files touched.
Answers four questions:
  1. Are channel contributions in the correct dollar scale?
  2. What is the meta_web attribution gap vs. Northbeam?
  3. What are the posterior saturation (lam) parameter values?
  4. Is the baseline absorbing too much LTV variation?

Run from repo root:
    .venv/bin/python scripts/10b_scale_diagnostic.py
"""
import json
import sys
import os
import warnings
warnings.filterwarnings("ignore")

if os.path.basename(os.getcwd()) == "scripts":
    os.chdir("..")
sys.path.insert(0, ".")

import numpy as np
import pandas as pd
import arviz as az
from pathlib import Path

from src.config import OUT_P2_04

OUT = Path(OUT_P2_04)
DIV = "=" * 65

# ── Load pre-computed outputs ───────────────────────────────────────────────
print(f"\n{DIV}\nSCALE DIAGNOSTIC — Model 2 (y=LTV_3YEAR)\n{DIV}")

ltv_weekly   = pd.read_csv(OUT / "tables" / "ltv_weekly.csv",  parse_dates=["DS"])
spend_weekly = pd.read_csv(OUT / "tables" / "spend_weekly.csv", parse_dates=["date"])

with open(OUT / "metrics" / "ltv_convergence.json") as f:
    conv = json.load(f)

trace_path = OUT / "traces" / "ltv_trace.nc"
if not trace_path.exists():
    print("ERROR: ltv_trace.nc not found. Run script 09 first.")
    sys.exit(1)

print("Loading trace (this may take ~30s)...")
idata = az.from_netcdf(str(trace_path))
print("Trace loaded.\n")

# ── 1. Observed data totals ─────────────────────────────────────────────────
total_ltv_obs   = float(ltv_weekly["LTV_3YEAR"].sum())
total_conv_obs  = float(ltv_weekly["CONVERSIONS"].sum())
avg_ltv         = total_ltv_obs / total_conv_obs

spend_cols = [c for c in spend_weekly.columns if c != "date"]
total_all_spend = float(spend_weekly[spend_cols].sum().sum())
meta_web_spend  = float(spend_weekly["meta_web"].sum())

print(f"[1] OBSERVED DATA TOTALS (93 weeks, 2024-07-01 → 2026-04-06)")
print(f"  Total LTV_3YEAR (y):             ${total_ltv_obs:>15,.0f}")
print(f"  Total conversions:               {total_conv_obs:>15,.0f}")
print(f"  avg_ltv (LTV/conv):              ${avg_ltv:>15,.2f}")
print(f"  Total meta_web spend:            ${meta_web_spend:>15,.0f}")
print(f"  Total all-channel spend:         ${total_all_spend:>15,.0f}")
print(f"  Meta web spend share:            {meta_web_spend/total_all_spend*100:>15.1f}%")

# ── 2. Contribution scale check ─────────────────────────────────────────────
baseline_pct   = conv["baseline_pct"]        # 0.5549
channel_pct    = 1.0 - baseline_pct          # 0.4451
expected_chan_total = total_ltv_obs * channel_pct

# Implied channel total from iROAS * spend (as recorded in convergence.json)
iroas_dict = conv["iroas"]
implied_chan_total = sum(
    iroas_dict.get(ch, 0) * float(spend_weekly[ch].sum())
    for ch in iroas_dict
    if ch in spend_weekly.columns
)
scale_ratio = implied_chan_total / expected_chan_total if expected_chan_total > 0 else 0

print(f"\n[2] CONTRIBUTION SCALE CHECK")
print(f"  Baseline from model:             {baseline_pct*100:>14.1f}%")
print(f"  Expected channel total (44.51%): ${expected_chan_total:>15,.0f}")
print(f"  Implied channel total (sum iROAS*spend): ${implied_chan_total:>9,.0f}")
print(f"  Scale ratio (implied / expected):{scale_ratio:>15.3f}")
print(f"  → 1.0 = perfect  |  <0.7 = likely scale error  |  >1.3 = inflated")
if scale_ratio < 0.7:
    print(f"  ⚠  SCALE ERROR LIKELY — contributions are under-stated by ~{1/scale_ratio:.1f}x")
elif scale_ratio > 1.3:
    print(f"  ⚠  CONTRIBUTIONS INFLATED — {scale_ratio:.1f}x above expected")
else:
    print(f"  ✓  Scale looks correct (within 30% of expected)")

# ── 3. Meta Web specific attribution ────────────────────────────────────────
meta_iroas    = conv["iroas"]["meta_web"]
meta_icac     = conv["icac"]["meta_web"]
meta_contrib  = meta_iroas * meta_web_spend
meta_bench_iroas = 1.79   # Northbeam 26WK LTV mode
meta_bench_icac  = 274.0  # Northbeam 52WK Conversions mode (reference)

print(f"\n[3] META WEB ATTRIBUTION")
print(f"  iROAS (model):                   {meta_iroas:>15.4f}x")
print(f"  iROAS (Northbeam 26WK LTV):      {meta_bench_iroas:>15.2f}x")
print(f"  iROAS gap:                       {meta_iroas/meta_bench_iroas:>15.3f}  (1.0 = match)")
print(f"  iCAC (model, LTV scale):         ${meta_icac:>15,.2f}")
print(f"  iCAC (Northbeam Conversions):    ${meta_bench_icac:>15.2f}")
print(f"  Implied meta_web LTV contrib:    ${meta_contrib:>15,.0f}")
print(f"  Meta contrib as % of total LTV:  {meta_contrib/total_ltv_obs*100:>14.1f}%")
print(f"  Meta spend as % of total spend:  {meta_web_spend/total_all_spend*100:>14.1f}%")
if meta_iroas / meta_bench_iroas < 0.5:
    print(f"  ⚠  iROAS is >2x below Northbeam — likely attribution under-counting")
    print(f"     Root cause: weak lift test (2 weeks, ${conv['lift_tests_applied'][2]['delta_y_ltv']:,.0f})")
    print(f"     OR: model spreading credit to other channels / baseline")

# ── 4. Posterior saturation parameters ─────────────────────────────────────
print(f"\n[4] POSTERIOR SATURATION PARAMETERS")
posterior_vars = list(idata.posterior.data_vars)
print(f"  All posterior vars: {posterior_vars}\n")

# Find saturation/lam variables (PyMC-Marketing naming conventions vary by version)
sat_keywords = ["lam", "sat", "saturation", "logistic", "alpha", "slope", "rate"]
sat_vars = [v for v in posterior_vars
            if any(k in v.lower() for k in sat_keywords)
            and "channel" not in v.lower()]
adstock_vars = [v for v in posterior_vars
                if any(k in v.lower() for k in ["adstock", "decay", "alpha_adstock"])
                and "channel" not in v.lower()]

print(f"  Saturation-related vars: {sat_vars}")
print(f"  Adstock-related vars:    {adstock_vars}")

for v in sat_vars:
    arr = idata.posterior[v].values
    flat = arr.flatten()
    print(f"\n  Variable: {v}  shape={arr.shape}")
    print(f"    mean={flat.mean():.4f}  std={flat.std():.4f}")
    print(f"    min={flat.min():.4f}   p5={np.percentile(flat, 5):.4f}  "
          f"median={np.median(flat):.4f}  p95={np.percentile(flat, 95):.4f}  max={flat.max():.4f}")

    # If it has a channel dimension, show per-channel
    if len(arr.shape) == 3:  # (chain, draw, channel)
        channel_columns = conv["channel_columns"]
        n_channels = arr.shape[2]
        print(f"    Per-channel means (n={n_channels}):")
        ch_means = arr.mean(axis=(0, 1))  # mean across chain, draw
        for i, ch in enumerate(channel_columns[:n_channels]):
            flag = " ← near-linear" if ch_means[i] < 0.01 else ""
            print(f"      {ch:<22} {ch_means[i]:.4f}{flag}")

# ── 5. Channel contributions from posterior (direct check) ─────────────────
print(f"\n[5] CHANNEL CONTRIBUTIONS FROM POSTERIOR (direct)")
contrib_vars = [v for v in posterior_vars if "contribution" in v.lower()]
print(f"  Contribution vars: {contrib_vars}")

for cv in contrib_vars[:3]:
    arr = idata.posterior[cv].values
    print(f"\n  {cv}  shape={arr.shape}")
    mean_contrib = arr.mean(axis=(0, 1))  # mean across chain, draw
    if mean_contrib.ndim == 2:  # (weeks, channels)
        total_from_posterior = mean_contrib.sum()
        print(f"    Sum of all channel contributions: ${total_from_posterior:,.0f}")
        print(f"    Total observed LTV:               ${total_ltv_obs:,.0f}")
        print(f"    Ratio (posterior/observed):       {total_from_posterior/total_ltv_obs:.3f}")
        if total_from_posterior / total_ltv_obs < 0.3:
            print(f"    ⚠  CONTRIBUTIONS ARE NORMALIZED (not dollar-scale) — back-transform missing!")
        elif total_from_posterior / total_ltv_obs > 0.8:
            print(f"    ⚠  Baseline appears very low from posterior direct read")
        else:
            print(f"    ✓  Posterior contributions in approximate dollar scale")
    elif mean_contrib.ndim == 1:  # just channels, already aggregated
        print(f"    Per-channel totals: {mean_contrib[:5]}...")

# ── 6. Summary and recommended fix ─────────────────────────────────────────
print(f"\n{DIV}")
print("DIAGNOSTIC SUMMARY")
print(f"{DIV}")
print(f"  API used:    {conv['contribution_api_used']}")
print(f"  Scale ratio: {scale_ratio:.3f}  (target: 0.7–1.3)")
print(f"  iROAS gap:   {meta_iroas/meta_bench_iroas:.2f}x  (target: >0.5x match)")
print()

if scale_ratio < 0.5:
    print("ROOT CAUSE: Scale error — contributions appear normalized, not dollar-scale.")
    print("  FIX: Force posterior_direct path in script 09; apply manual back-transform.")
elif meta_iroas / meta_bench_iroas < 0.3:
    print("ROOT CAUSE: Attribution problem — model under-weights meta_web vs. baseline.")
    print("  FIX: Tighten saturation lam prior; check if lift test window is correctly matched.")
    print("       Consider: the 2-week lift window may be too short to anchor meta_web.")
else:
    print("No critical scale error detected. Gap may be genuine model attribution difference.")
    print("  Abheek expects directional alignment, not exact match.")
    print("  Recommend: document the gap in deliverable, show Northbeam reference alongside model.")

print(f"\n{DIV}\n")
