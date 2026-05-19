"""
1_Decisioning_Summary.py — 19-row decisioning table (M5 template, approved by
Abheek 2026-05-12).

Columns (per the M5 template Abheek approved):
  A · Channel               display name from CHANNEL_DISPLAY
  B · Spend Signal          Very High / High / Medium / Low from weekly spend share
  C · iCAC / Trend          windowed (tested) or aggregate (untested) + 5WK/26WK trend
  D · iROAS Trend           baseline iROAS + 5WK/26WK trend + % below break-even
  E · Confidence (Trust)    HIGH / CAUTION / LOW per D015 rule
  F · Saturation Read       Past sat / Approaching / Headroom from sat-curve slope
  G · Recommended Action    default "Hold pending guardrails or incrementality proof"
  H · Spend Move to Test    "Review pending" placeholder (NOT client-facing until approved)

Lift-tested channels (7) are listed first; untested (12) follow. Sortable.
Export as CSV via the button at the bottom.
"""
import sys
from pathlib import Path

# Make `app.*` imports work when running this page from any cwd.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import numpy as np
import pandas as pd
import streamlit as st

from app.data_loader import (
    CHANNELS_AVAILABLE, CHANNELS_LIFT_TESTED, CHANNEL_DISPLAY, CANONICAL_VERSION,
    load_baseline, load_icac_time, load_iroas_time, load_spend_weekly,
    load_icac_saturation, load_lift_metrics,
)

st.set_page_config(
    page_title="Decisioning Summary — Kikoff MMM",
    page_icon="📋",
    layout="wide",
)

st.markdown("# Decisioning Summary — 19 Channels")
st.caption(
    "8-column decisioning framework (M5 template, approved by Abheek 2026-05-12). "
    "Lift-tested channels are listed first (windowed iCAC vs experimental truth); "
    "untested channels follow (aggregate iCAC). "
    "Column G default: *Hold on to any changes unless documents and guardrails are in place or proved by incrementality.*"
)


# ── Helpers ──────────────────────────────────────────────────────────────────
def _spend_signal(share_pct: float) -> str:
    """Categorize a channel by its share of total weekly spend across all 19."""
    if share_pct >= 15: return "Very High"
    if share_pct >= 7:  return "High"
    if share_pct >= 2:  return "Medium"
    return "Low"


def _saturation_read(icac_sat_df: pd.DataFrame, median_spend: float, observed_max: float) -> str:
    """Compare median iCAC at observed_max vs at median_spend; flag the slope.

    Past saturation if iCAC at obs-max is > 1.5× iCAC at median spend.
    Approaching saturation between 1.2× and 1.5×.
    Headroom below 1.2×.
    """
    if icac_sat_df.empty or median_spend <= 0 or observed_max <= 0:
        return "Insufficient data"
    # Nearest-spend lookup
    def _nearest_icac(target: float) -> float:
        diffs = (icac_sat_df["spend"] - target).abs()
        idx = diffs.idxmin()
        return float(icac_sat_df.loc[idx, "icac_mean"])
    icac_at_median = _nearest_icac(median_spend)
    icac_at_max    = _nearest_icac(observed_max)
    if not (np.isfinite(icac_at_median) and np.isfinite(icac_at_max) and icac_at_median > 0):
        return "Insufficient data"
    ratio = icac_at_max / icac_at_median
    if ratio > 1.5:  return f"Past saturation (×{ratio:.1f} iCAC at obs-max vs median)"
    if ratio > 1.2:  return f"Approaching saturation (×{ratio:.1f})"
    return f"Headroom (×{ratio:.2f} — near-linear)"


def _confidence(is_tested: bool, gate_pass: bool, hdi_span_ratio: float) -> str:
    """D015-style confidence label."""
    if not is_tested:                       return "🔴 LOW — no lift test"
    if gate_pass and hdi_span_ratio < 0.5:  return "🟢 HIGH — gate PASS, tight posterior"
    if gate_pass:                            return "🟡 CAUTION — gate PASS, wide posterior"
    return "🔴 LOW — gate FAIL"


def _avg_last_weeks(df: pd.DataFrame, weeks: int) -> float:
    if df.empty: return float("nan")
    cutoff = df["date"].max() - pd.Timedelta(weeks=weeks)
    sub = df.loc[df["date"] >= cutoff, "mean"]
    return float(sub.mean()) if len(sub) else float("nan")


# ── First pass: total spend across all 19 channels (for B share calc) ────────
total_spend_all = 0.0
spend_per_channel: dict[str, float] = {}
for ch in CHANNELS_AVAILABLE:
    s_df = load_spend_weekly(ch, drop_partial_last=False)
    s = float(s_df[f"{ch}_spend"].sum()) if f"{ch}_spend" in s_df.columns else 0.0
    spend_per_channel[ch] = s
    total_spend_all += s


# ── Build 19 rows ────────────────────────────────────────────────────────────
rows: list[dict] = []
# Lift-tested first (already the order in CHANNELS_AVAILABLE per data_loader).
for ch in CHANNELS_AVAILABLE:
    base    = load_baseline(ch)
    icac_t  = load_icac_time(ch)
    iroas_t = load_iroas_time(ch)
    sat_df  = load_icac_saturation(ch)
    s_df    = load_spend_weekly(ch, drop_partial_last=False)
    spend_col = f"{ch}_spend"
    nonzero_spend = s_df.loc[s_df[spend_col] > 0, spend_col] if spend_col in s_df.columns else pd.Series([])
    median_spend = float(np.median(nonzero_spend)) if len(nonzero_spend) else 0.0
    observed_max = float(s_df[spend_col].max()) if spend_col in s_df.columns else 0.0

    # B: weekly share
    share_pct = (100.0 * spend_per_channel[ch] / total_spend_all) if total_spend_all > 0 else 0.0
    sig = _spend_signal(share_pct)

    # C: 5WK vs 26WK trend (iCAC)
    icac_5  = _avg_last_weeks(icac_t, 5)
    icac_26 = _avg_last_weeks(icac_t, 26)
    icac_delta = (icac_5 / icac_26 - 1.0) * 100.0 if (icac_26 and np.isfinite(icac_26) and icac_26 != 0) else 0.0

    # D: 5WK vs 26WK trend (iROAS)
    iroas_5  = _avg_last_weeks(iroas_t, 5)
    iroas_26 = _avg_last_weeks(iroas_t, 26)
    iroas_delta = (iroas_5 / iroas_26 - 1.0) * 100.0 if (iroas_26 and np.isfinite(iroas_26) and iroas_26 != 0) else 0.0

    # E: confidence per D015
    hdi_span = base["icac_hdi_hi"] - base["icac_hdi_lo"]
    hdi_ratio = (hdi_span / base["icac_mean"]) if base["icac_mean"] else 1.0
    conf = _confidence(base["is_lift_tested"], base.get("windowed_gate_pass", False), hdi_ratio)

    # F: saturation read
    sat = _saturation_read(sat_df, median_spend, observed_max)

    # C string
    if base["is_lift_tested"]:
        truth = base["windowed_iCAC_truth"]
        tol   = base["windowed_iCAC_tol"]
        c_str = (
            f"Windowed ${base['windowed_iCAC']:.0f} "
            f"(truth ${truth:.0f}±${tol:.0f}, {'PASS' if base['windowed_gate_pass'] else 'FAIL'}) · "
            f"5WK ${icac_5:,.0f} vs 26WK ${icac_26:,.0f} ({icac_delta:+.0f}%)"
        )
    else:
        c_str = (
            f"Aggregate ${base['agg_iCAC_script09']:.0f} (no lift test) · "
            f"5WK ${icac_5:,.0f} vs 26WK ${icac_26:,.0f} ({icac_delta:+.0f}%)"
        )

    d_str = (
        f"Baseline {base['iroas_mean']:.3f}x · "
        f"5WK {iroas_5:.3f}x vs 26WK {iroas_26:.3f}x ({iroas_delta:+.0f}%) · "
        f"{base['iroas_below_breakeven_pct']:.0f}% below 1.0×"
    )

    rows.append({
        "A · Channel":              CHANNEL_DISPLAY[ch],
        "B · Spend Signal":         f"{sig} ({share_pct:.1f}% of total)",
        "C · iCAC / Trend":         c_str,
        "D · iROAS Trend":          d_str,
        "E · Confidence (Trust)":   conf,
        "F · Saturation Read":      sat,
        "G · Recommended Action":   "Hold pending guardrails or incrementality proof",
        "H · Spend Move to Test":   "Review pending",
    })


df = pd.DataFrame(rows)

# ── Render ───────────────────────────────────────────────────────────────────
st.dataframe(
    df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "A · Channel":            st.column_config.TextColumn(width="small"),
        "B · Spend Signal":       st.column_config.TextColumn(width="small"),
        "C · iCAC / Trend":       st.column_config.TextColumn(width="large"),
        "D · iROAS Trend":        st.column_config.TextColumn(width="large"),
        "E · Confidence (Trust)": st.column_config.TextColumn(width="medium"),
        "F · Saturation Read":    st.column_config.TextColumn(width="medium"),
        "G · Recommended Action": st.column_config.TextColumn(width="medium"),
        "H · Spend Move to Test": st.column_config.TextColumn(width="small"),
    },
)

# ── CSV export ───────────────────────────────────────────────────────────────
csv_bytes = df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="📥 Download summary as CSV",
    data=csv_bytes,
    file_name=f"kikoff_mmm_decisioning_summary_{CANONICAL_VERSION}.csv",
    mime="text/csv",
)

# ── Footer ───────────────────────────────────────────────────────────────────
st.markdown("---")
n_tested = sum(1 for r in rows if "Windowed" in r["C · iCAC / Trend"])
n_passing = sum(
    1 for r in rows
    if "Windowed" in r["C · iCAC / Trend"] and "PASS)" in r["C · iCAC / Trend"]
)
st.caption(
    f"**Canonical:** `{CANONICAL_VERSION}` · "
    f"**Total channels:** {len(rows)} · "
    f"**Lift-tested:** {n_tested} ({n_passing}/{n_tested} windowed gates PASS) · "
    f"**Untested:** {len(rows) - n_tested}. "
    f"Columns G and H are placeholders pending review — not client-facing assertions."
)
