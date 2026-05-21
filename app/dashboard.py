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
    load_baseline, load_baseline_split, load_icac_time, load_iroas_time, load_ltv_time,
    load_icac_saturation, load_iroas_saturation, load_spend_weekly,
    load_convergence, CHANNEL_DISPLAY,
    CHANNELS_LIFT_TESTED, CHANNELS_UNTESTED, CANONICAL_VERSION,
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
# Two-radio pattern with mutual reset: selecting in one group clears the other.
# Source of truth = st.session_state.channel_key. The radios are mirrors that
# show "selected" only for the active group.
if "channel_key" not in st.session_state:
    st.session_state.channel_key = "meta_ios"
    st.session_state.ch_lift_tested = "meta_ios"
    st.session_state.ch_untested = None


def _on_tested_change():
    picked = st.session_state.ch_lift_tested
    if picked:
        st.session_state.channel_key = picked
        st.session_state.ch_untested = None  # reset the other group


def _on_untested_change():
    picked = st.session_state.ch_untested
    if picked:
        st.session_state.channel_key = picked
        st.session_state.ch_lift_tested = None  # reset the other group


with st.sidebar:
    st.markdown("## Kikoff MMM")
    st.markdown("**Model:** LTV_3YEAR (Model 2)")
    st.caption(f"Canonical: `{CANONICAL_VERSION}`")
    st.markdown("---")
    st.markdown("**Channel**")
    st.caption("Lift-tested (7) — windowed iCAC vs experimental truth")
    st.radio(
        "lift_tested",
        CHANNELS_LIFT_TESTED,
        format_func=lambda c: CHANNEL_DISPLAY[c],
        label_visibility="collapsed",
        key="ch_lift_tested",
        on_change=_on_tested_change,
        index=None,
    )
    st.caption("Untested (12) — aggregate iCAC, wider calibration uncertainty")
    st.radio(
        "untested",
        CHANNELS_UNTESTED,
        format_func=lambda c: CHANNEL_DISPLAY[c],
        label_visibility="collapsed",
        key="ch_untested",
        on_change=_on_untested_change,
        index=None,
    )
    channel_key = st.session_state.channel_key

    st.markdown("---")
    st.markdown("**About**")
    st.caption(
        "This dashboard shows the current state of the Kikoff Marketing Mix Model "
        "across all 19 channels. Lift-tested channels show **windowed iCAC** anchored "
        "to the experimental truth window (per D023); untested channels show "
        "**aggregate iCAC** with wider uncertainty. Charts update automatically as "
        "the model is recalibrated and outputs are pushed to GitHub."
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
is_lift_tested = baseline.get("is_lift_tested", False)
# Windowed truth band for tested channels (post-Fix-A); None for untested.
benchmark = baseline.get("windowed_iCAC_truth") if is_lift_tested else None
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
# D029 (2026-05-20): D021 <20% baseline gate DEPRECATED. Replaced single global
# Baseline metric (which used the stale <80% flag) with two-metric pair
# (in-window + global), neutral coloring, tooltip pointer to Methodology page.
baseline_split = load_baseline_split()
in_window_pct = baseline_split["aggregate"]["in_window_baseline_pct"]
global_pct    = baseline_split["sanity"]["global_baseline_pct"]
mc1, mc2, mc3, mc4, mc5 = st.columns(5)
rhat = conv["convergence"]["rhat_max"]
ess  = conv["convergence"]["ess_min"]
mc1.metric("R-hat (max)", f"{rhat:.3f}", delta="PASS" if rhat < 1.1 else "FAIL",
           delta_color="normal" if rhat < 1.1 else "inverse")
mc2.metric("ESS (min)", f"{int(ess)}", delta="PASS" if ess > 400 else "FAIL",
           delta_color="normal" if ess > 400 else "inverse")
mc3.metric(
    "Baseline (in-window)",
    f"{in_window_pct:.1f}%",
    delta="reported (D029)",
    delta_color="off",
    help=(
        "Mean baseline % across the 12 W-MON weeks that overlap any of the 7 "
        "lift-test windows. D029 (2026-05-20) deprecated D021's <20% threshold "
        "gate — see Methodology page for the full decomposition and the "
        "view-through mechanism for Meta Web."
    ),
)
mc4.metric(
    "Baseline (global)",
    f"{global_pct:.1f}%",
    delta="reported (D029)",
    delta_color="off",
    help=(
        "Global baseline % across all 93 weeks. Decomposes empirically into "
        "~35% irreducible organic LTV (Abheek/Northbeam per Mtg 6 fact #13) + "
        "~32pp missed paid attribution (largely Meta Web view-through). "
        "Apples-to-apples on the attributed-revenue universe ≈ 45–57% band. "
        "See Methodology page (D029)."
    ),
)
mc5.metric("Channels modeled", str(conv["n_channels"]))

st.markdown("---")

# ── Summary stats (filtered by active time-period toggle) ────────────────────
st.markdown(f"#### Channel Totals — {period}")
ltv_revenue_total = float(ltv_time_view["mean"].sum()) if not ltv_time_view.empty else 0.0
spend_col_name = f"{channel_key}_spend"
spend_total       = float(spend_view[spend_col_name].sum()) if not spend_view.empty else 0.0
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
display_name = CHANNEL_DISPLAY.get(channel_key, channel_key)
st.markdown(f"#### Baseline Performance — {display_name}")
if is_lift_tested:
    gate_label = "PASS" if baseline.get("windowed_gate_pass") else "FAIL"
    gate_color = "✅" if baseline.get("windowed_gate_pass") else "❌"
    st.caption(
        f"Headline iCAC = **windowed posterior median during the lift-test window** (D023). "
        f"Truth band: **${baseline['windowed_iCAC_truth']:.0f} ± ${baseline['windowed_iCAC_tol']:.0f}**. "
        f"Windowed gate: {gate_color} **{gate_label}**. "
        f"For audit, the full-history aggregate iCAC is ${baseline['agg_iCAC_script09']:.0f}."
    )
else:
    st.caption(
        "Headline iCAC = **full-history aggregate** (no lift test for this channel; "
        "calibration uncertainty is higher than for lift-tested channels). "
        "Tested channels can be compared to their experimental truth band; untested channels cannot."
    )
col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(fig_icac_baseline(baseline, channel=channel_key),
                    use_container_width=True, config=CONFIG)
    with st.expander("Reading this chart"):
        if is_lift_tested:
            st.caption(
                f"**Headline iCAC ${baseline['icac_mean']:,.0f}** (windowed posterior median; 94% HDI "
                f"${baseline['icac_hdi_lo']:,.0f}–${baseline['icac_hdi_hi']:,.0f}). "
                f"Truth band ${baseline['windowed_iCAC_truth']:.0f} ± ${baseline['windowed_iCAC_tol']:.0f} "
                f"comes from the lift-test point estimate; gate passes if the headline falls inside. "
                f"For context, full-history aggregate iCAC is ${baseline['agg_iCAC_script09']:.0f}."
            )
        else:
            st.caption(
                f"**Headline iCAC ${baseline['icac_mean']:,.0f}** (full-history aggregate posterior median; "
                f"94% HDI ${baseline['icac_hdi_lo']:,.0f}–${baseline['icac_hdi_hi']:,.0f}). "
                f"No lift test exists for {display_name} → no experimental truth band. "
                f"Compare against other channels with similar spend signal for relative ranking."
            )

with col2:
    st.plotly_chart(fig_iroas_baseline(baseline, channel=channel_key),
                    use_container_width=True, config=CONFIG)
    with st.expander("Reading this chart"):
        st.caption(
            f"**Baseline iROAS {baseline['iroas_mean']:.3f}x** (posterior mean; 94% HDI "
            f"{baseline['iroas_hdi_lo']:.3f}–{baseline['iroas_hdi_hi']:.3f}) — LTV dollars attributed per dollar of spend. "
            f"{baseline['iroas_below_breakeven_pct']:.0f}% of posterior mass sits below 1.0× break-even."
        )

# ── Row 2: Time series ───────────────────────────────────────────────────────
st.markdown("---")
st.markdown("#### Performance Over Time")
tab_icac, tab_iroas, tab_ltv = st.tabs(["iCAC over time", "iROAS over time", "LTV over time"])

with tab_icac:
    st.plotly_chart(
        fig_icac_time(icac_time_view, benchmark, spend_df=spend_view, channel=channel_key),
        use_container_width=True, config=CONFIG,
    )

with tab_iroas:
    st.plotly_chart(
        fig_iroas_time(iroas_time_view, spend_df=spend_view, channel=channel_key),
        use_container_width=True, config=CONFIG,
    )

with tab_ltv:
    st.plotly_chart(
        fig_ltv_time(ltv_time_view, channel=channel_key),
        use_container_width=True, config=CONFIG,
    )

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
    st.plotly_chart(
        fig_icac_saturation(icac_sat_df, median_spend, benchmark=benchmark,
                            spend_df=spend_df, channel=channel_key),
        use_container_width=True, config=CONFIG,
    )
with sat_col2:
    st.plotly_chart(
        fig_iroas_saturation(iroas_sat_df, median_spend,
                             spend_df=spend_df, channel=channel_key),
        use_container_width=True, config=CONFIG,
    )

# ── Row 4: Spend distribution ────────────────────────────────────────────────
st.markdown("---")
st.markdown("#### Weekly Spend Distribution")
st.plotly_chart(
    fig_spend_dist(spend_df, channel=channel_key),
    use_container_width=True, config=CONFIG,
)

# ── Pointer to the Decisioning Summary page ─────────────────────────────────
st.markdown("---")
st.info(
    "**Want a cross-channel comparison?** Open the **Decisioning Summary** page "
    "in the left sidebar — 19-row sortable table with the 8-column M5 decisioning "
    "framework Abheek approved on 2026-05-12."
)

# ── Footer ───────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption(
    f"**Data window:** {conv['weekly_obs']} weeks | "
    f"**Channels in model:** {conv['n_channels']} | "
    f"**avg LTV per customer:** ${baseline['avg_ltv']:,.2f} | "
    f"**Canonical:** `{CANONICAL_VERSION}`"
)
