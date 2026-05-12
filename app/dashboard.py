"""
dashboard.py — Kikoff MMM Model Output Dashboard (Streamlit).

Live view of model outputs. Updates automatically when new outputs are pushed.
Reads only committed pre-computed files — no raw data, no trace files.

Run locally:
    my-notebook-project/.venv/bin/streamlit run app/dashboard.py

Deploy: Streamlit Community Cloud → connect GitHub repo → set main file to app/dashboard.py
"""
import streamlit as st

st.set_page_config(
    page_title="Kikoff MMM Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd

from app.data_loader import (
    load_baseline, load_icac_time, load_iroas_time, load_ltv_time,
    load_icac_saturation, load_iroas_saturation, load_spend_weekly,
    load_convergence, CHANNEL_DISPLAY, CHANNELS_AVAILABLE, CHANNELS_COMING_SOON,
)
from app.charts import (
    fig_icac_baseline, fig_iroas_baseline,
    fig_icac_time, fig_iroas_time, fig_ltv_time,
    fig_icac_saturation, fig_iroas_saturation, fig_spend_dist,
    CONFIG,
)


TIME_PERIODS = ["5WK", "26WK", "52WK", "LAST YEAR", "ALL TIME"]


def filter_by_period(df: pd.DataFrame, period: str, date_col: str = "date") -> pd.DataFrame:
    """Filter a time-series DataFrame to the selected Northbeam-style window.

    Anchors to the max date in the frame so 5WK/26WK/52WK mean "last N weeks of data."
    LAST YEAR = previous full calendar year (year(max) - 1).
    """
    if period == "ALL TIME" or df.empty:
        return df
    max_date = df[date_col].max()
    if period == "LAST YEAR":
        return df[df[date_col].dt.year == (max_date.year - 1)]
    weeks_map = {"5WK": 5, "26WK": 26, "52WK": 52}
    cutoff = max_date - pd.Timedelta(weeks=weeks_map[period])
    return df[df[date_col] >= cutoff]

# ── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## Kikoff MMM")
    st.markdown("**Model:** LTV_3YEAR (Model 2)")
    st.markdown("---")
    st.markdown("**Channel**")
    channel = st.radio(
        label="Select channel",
        options=CHANNELS_AVAILABLE + [f"🔒 {c} (coming soon)" for c in CHANNELS_COMING_SOON],
        label_visibility="collapsed",
    )
    if "coming soon" in channel:
        st.info("Additional channels are validated and added as the model improves.")
        st.stop()

    channel_key = channel  # e.g. "meta_web"

    st.markdown("---")
    st.markdown("**About**")
    st.caption(
        "This dashboard shows the current state of the Kikoff Marketing Mix Model. "
        "Charts update automatically as the model is recalibrated and new outputs are pushed to GitHub. "
        "Currently showing Meta Web (Facebook). Other channels will be added as they are validated."
    )

# ── Load data ────────────────────────────────────────────────────────────────
baseline     = load_baseline(channel_key)
icac_time_df = load_icac_time(channel_key)
iroas_time_df= load_iroas_time(channel_key)
ltv_time_df  = load_ltv_time(channel_key)
icac_sat_df  = load_icac_saturation(channel_key)
iroas_sat_df = load_iroas_saturation(channel_key)
spend_df     = load_spend_weekly(channel_key)
conv         = load_convergence()

median_spend = baseline["median_weekly_spend"]
benchmark    = baseline["lift_test_benchmark"]
last_updated = baseline["last_updated"]

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown(f"# Kikoff MMM — Model Output Dashboard")
col_h1, col_h2, col_h3 = st.columns(3)
col_h1.metric("Channel", CHANNEL_DISPLAY.get(channel_key, channel_key))
col_h2.metric("Model", "LTV_3YEAR (Model 2)")
col_h3.metric("Last updated", last_updated)

# ── Time-period toggle (Northbeam-style) ─────────────────────────────────────
st.markdown("")
period = st.radio(
    "Time period",
    options=TIME_PERIODS,
    index=TIME_PERIODS.index("26WK"),
    horizontal=True,
    label_visibility="collapsed",
    key="time_period",
)

icac_time_view  = filter_by_period(icac_time_df, period)
iroas_time_view = filter_by_period(iroas_time_df, period)
ltv_time_view   = filter_by_period(ltv_time_df, period)
spend_view      = filter_by_period(spend_df, period)

# ── Model health status bar ──────────────────────────────────────────────────
st.markdown("---")
st.markdown("#### Model Health")
mc1, mc2, mc3, mc4 = st.columns(4)
rhat = conv["convergence"]["rhat_max"]
ess  = conv["convergence"]["ess_min"]
mc1.metric("R-hat (max)", f"{rhat:.3f}", delta="PASS" if rhat < 1.1 else "FAIL",
           delta_color="normal" if rhat < 1.1 else "inverse")
mc2.metric("ESS (min)", f"{int(ess)}", delta="PASS" if ess > 400 else "FAIL",
           delta_color="normal" if ess > 400 else "inverse")
mc3.metric("Baseline", f"{baseline['baseline_pct']:.1f}%",
           delta="PASS" if baseline["baseline_pct"] < 80 else "HIGH",
           delta_color="normal" if baseline["baseline_pct"] < 80 else "inverse")
mc4.metric("Channels modeled", str(conv["n_channels"]))

st.markdown("---")

# ── Summary stats (filtered by active time-period toggle) ────────────────────
st.markdown(f"#### Channel Totals — {period}")
ltv_revenue_total = float(ltv_time_view["mean"].sum()) if not ltv_time_view.empty else 0.0
spend_total       = float(spend_view["meta_web_spend"].sum()) if not spend_view.empty else 0.0
total_iroas       = (ltv_revenue_total / spend_total) if spend_total > 0 else 0.0


def _fmt_money(x: float) -> str:
    if abs(x) >= 1_000_000:
        return f"${x/1_000_000:.2f}M"
    if abs(x) >= 1_000:
        return f"${x/1_000:.1f}K"
    return f"${x:.0f}"


s1, s2, s3 = st.columns(3)
s1.metric("LTV Revenue (attributed)", _fmt_money(ltv_revenue_total))
s2.metric("Spend", _fmt_money(spend_total))
s3.metric("Total iROAS", f"{total_iroas:.3f}x")

st.markdown("---")

# ── Row 1: Baseline metrics ──────────────────────────────────────────────────
st.markdown("#### Baseline Performance")
col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(fig_icac_baseline(baseline), use_container_width=True, config=CONFIG)
    with st.expander("Reading this chart"):
        st.caption(
            f"Baseline iCAC: **${baseline['icac_mean']:,.0f}** — the average cost to generate one "
            f"implied customer conversion, attributed to Meta Web, across the full 93-week model window. "
            f"The lift test benchmark (${benchmark:.0f}) is from the May 2025 Meta lift experiment. "
            f"The Northbeam reference (${baseline['northbeam_icac_ref']:.0f}) is their 52-week "
            f"Conversions mode average. Our model measures marginal attribution at observed spend levels, "
            f"which is typically higher than Northbeam's volume-weighted average."
        )

with col2:
    st.plotly_chart(fig_iroas_baseline(baseline), use_container_width=True, config=CONFIG)
    with st.expander("Reading this chart"):
        st.caption(
            f"Baseline iROAS: **{baseline['iroas_mean']:.3f}x** — for each dollar spent on Meta Web, "
            f"the model attributes this much in 3-year LTV. The Northbeam reference ({baseline['northbeam_iroas_ref']}x) "
            f"is from their 26-week LTV mode view. The gap reflects two factors: (1) the May 2025 lift "
            f"test was conducted at above-median spend ($628K/week vs $444K median), measuring diminishing-returns "
            f"efficiency; (2) with 19 channels competing, credit is spread across the full spend portfolio. "
            f"Abheek's MMM uses this model as one of three signals — directional alignment matters more than "
            f"exact match."
        )

# ── Row 2: Time series ───────────────────────────────────────────────────────
st.markdown("---")
st.markdown("#### Performance Over Time")
tab_icac, tab_iroas, tab_ltv = st.tabs(["iCAC over time", "iROAS over time", "LTV over time"])

with tab_icac:
    st.plotly_chart(fig_icac_time(icac_time_view, benchmark, spend_df=spend_view),
                    use_container_width=True, config=CONFIG)

with tab_iroas:
    st.plotly_chart(fig_iroas_time(iroas_time_view, spend_df=spend_view),
                    use_container_width=True, config=CONFIG)

with tab_ltv:
    st.plotly_chart(fig_ltv_time(ltv_time_view),
                    use_container_width=True, config=CONFIG)

# ── Row 3: Saturation curves ─────────────────────────────────────────────────
st.markdown("---")
st.markdown("#### Saturation & Spend Efficiency")
st.caption(
    "These curves show how marginal efficiency (iCAC / iROAS) changes at different spend levels. "
    "The vertical line marks the historical median weekly spend. Moving right means more spend → "
    "diminishing returns (higher iCAC, lower iROAS)."
)

sat_col1, sat_col2 = st.columns(2)
with sat_col1:
    st.plotly_chart(fig_icac_saturation(icac_sat_df, median_spend, benchmark, spend_df=spend_df),
                    use_container_width=True, config=CONFIG)
with sat_col2:
    st.plotly_chart(fig_iroas_saturation(iroas_sat_df, median_spend, spend_df=spend_df),
                    use_container_width=True, config=CONFIG)

# ── Row 4: Spend distribution ────────────────────────────────────────────────
st.markdown("---")
st.markdown("#### Weekly Spend Distribution")
st.plotly_chart(fig_spend_dist(spend_df, channel_col="meta_web_spend"),
                use_container_width=True, config=CONFIG)

# ── Row 5: Decisioning framework (Meta Web mock) ─────────────────────────────
st.markdown("---")
st.markdown("#### Decisioning Framework — Meta Web")
st.caption(
    "8-column decisioning layer matching the Meeting 5 specification. "
    "One row shown for Meta Web as a working template; remaining 18 channel × platform combinations populate post-presentation. "
    "Header above column G: *Hold on to any changes unless documents and guardrails are in place or proved by Incrementality.*"
)


def _mean_in_window(df: pd.DataFrame, weeks: int, value_col: str) -> float:
    if df.empty:
        return float("nan")
    cutoff = df["date"].max() - pd.Timedelta(weeks=weeks)
    sub = df[df["date"] >= cutoff]
    return float(sub[value_col].mean()) if len(sub) else float("nan")


icac_5w  = _mean_in_window(icac_time_df, 5,  "mean")
icac_26w = _mean_in_window(icac_time_df, 26, "mean")
iroas_5w  = _mean_in_window(iroas_time_df, 5,  "mean")
iroas_26w = _mean_in_window(iroas_time_df, 26, "mean")
icac_delta_pct  = (icac_5w / icac_26w - 1.0) * 100  if icac_26w  else 0.0
iroas_delta_pct = (iroas_5w / iroas_26w - 1.0) * 100 if iroas_26w else 0.0

# Model 1 (Conversions) iCAC point estimate from 08b-v2 (see state/model_approach.md)
MODEL1_ICAC_META_WEB = 759
NORTHBEAM_ICAC_52WK  = baseline["northbeam_icac_ref"]   # 274
LIFT_BENCH_WEB       = benchmark                         # 156.89

decisioning_rows = [{
    "A · Channel": "Meta Web",
    "B · Spend Signal": "Very High (largest single channel; ~30% share of total weekly spend)",
    "C · iCAC / Trend": (
        f"Model 1 (Conv): ${MODEL1_ICAC_META_WEB} · "
        f"5WK avg ${icac_5w:,.0f} vs 26WK avg ${icac_26w:,.0f} "
        f"({icac_delta_pct:+.0f}% vs 26WK)"
    ),
    "D · iROAS Trend": (
        f"5WK avg {iroas_5w:.3f}x vs 26WK avg {iroas_26w:.3f}x "
        f"({iroas_delta_pct:+.0f}% vs 26WK); 100% of posterior below break-even"
    ),
    "E · Confidence (Trust)": "🔴 Low — under saturation confound; gates lifted to PASS only for meta_ios + ctv",
    "F · Saturation Read": (
        f"Past saturation. Model iCAC ${MODEL1_ICAC_META_WEB} vs Northbeam 52WK ${NORTHBEAM_ICAC_52WK:.0f} "
        f"({MODEL1_ICAC_META_WEB/NORTHBEAM_ICAC_52WK:.1f}× separation) and lift test ${LIFT_BENCH_WEB:.0f} "
        f"({MODEL1_ICAC_META_WEB/LIFT_BENCH_WEB:.1f}× separation). Lift test ran at ~1/70th typical spend — measures marginal efficiency, "
        "not full-scale; model fits full-scale spend → saturation regime."
    ),
    "G · Recommended Action": (
        "Hold on to any changes unless documents and guardrails are in place or proved by incrementality."
    ),
    "H · Spend Move to Test": "−15 to −20% (saturation test) — geo holdout at scaled-down spend to verify diminishing-returns finding",
}]

decisioning_df = pd.DataFrame(decisioning_rows)
st.dataframe(decisioning_df, use_container_width=True, hide_index=True)

# ── Footer ───────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption(
    f"**Data window:** {conv['weekly_obs']} weeks | "
    f"**Channels in model:** {conv['n_channels']} | "
    f"**avg LTV per customer:** ${baseline['avg_ltv']:,.2f} | "
    f"Northbeam references: iROAS {baseline['northbeam_iroas_ref']}x (26WK LTV mode), "
    f"iCAC ${baseline['northbeam_icac_ref']:.0f} (52WK Conversions mode)"
)
