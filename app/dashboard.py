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
    st.plotly_chart(fig_icac_time(icac_time_df, benchmark),
                    use_container_width=True, config=CONFIG)

with tab_iroas:
    st.plotly_chart(fig_iroas_time(iroas_time_df),
                    use_container_width=True, config=CONFIG)

with tab_ltv:
    st.plotly_chart(fig_ltv_time(ltv_time_df),
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
    st.plotly_chart(fig_icac_saturation(icac_sat_df, median_spend, benchmark),
                    use_container_width=True, config=CONFIG)
with sat_col2:
    st.plotly_chart(fig_iroas_saturation(iroas_sat_df, median_spend),
                    use_container_width=True, config=CONFIG)

# ── Row 4: Spend distribution ────────────────────────────────────────────────
st.markdown("---")
st.markdown("#### Weekly Spend Distribution")
st.plotly_chart(fig_spend_dist(spend_df, channel_col="meta_web_spend"),
                use_container_width=True, config=CONFIG)

# ── Footer ───────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption(
    f"**Data window:** {conv['weekly_obs']} weeks | "
    f"**Channels in model:** {conv['n_channels']} | "
    f"**avg LTV per customer:** ${baseline['avg_ltv']:,.2f} | "
    f"Northbeam references: iROAS {baseline['northbeam_iroas_ref']}x (26WK LTV mode), "
    f"iCAC ${baseline['northbeam_icac_ref']:.0f} (52WK Conversions mode)"
)
