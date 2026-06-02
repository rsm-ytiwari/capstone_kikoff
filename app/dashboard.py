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
    load_convergence, load_oot, CHANNEL_DISPLAY,
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
    st.session_state.channel_key = "meta_web"
    st.session_state.ch_lift_tested = "meta_web"
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
    st.markdown("**Model:** 3-year LTV (revenue model)")
    st.caption("Cost and value figures on this page come from the LTV model. "
               "Conversion-model accuracy is on the Out-of-Time page.")
    st.markdown("---")
    st.markdown("**Channel**")
    st.caption("Lift-tested (7): cost per acquired customer (iCAC) measured during "
               "each channel's experiment window, checked against the experiment result.")
    st.radio(
        "lift_tested",
        CHANNELS_LIFT_TESTED,
        format_func=lambda c: CHANNEL_DISPLAY[c],
        label_visibility="collapsed",
        key="ch_lift_tested",
        on_change=_on_tested_change,
        index=None,
    )
    st.caption("Untested (12): cost per acquired customer averaged over all history, "
               "with wider uncertainty (no experiment to anchor to).")
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
        "across all 19 channels. Lift-tested channels show cost per acquired customer "
        "measured during the channel's experiment window; untested channels show the "
        "all-history average, with wider uncertainty. Charts update automatically as "
        "the model is recalibrated."
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
st.markdown("# Kikoff MMM: Model Output Dashboard")
col_h1, col_h2, col_h3 = st.columns(3)
col_h1.metric("Channel", CHANNEL_DISPLAY.get(channel_key, channel_key))
col_h2.metric("Model", "3-year LTV (revenue)")
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

# ── Headline value cards (lead with value, not diagnostics) ───────────────────
st.markdown("---")
st.markdown(f"#### Channel Totals: {period}")
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
s3.metric("Total iROAS (LTV $ per $ spent)", f"{total_iroas:.3f}x")

# ── Out-of-time validation headline (the headline MMM accuracy metric) ────────
def _mape_dot(m: float) -> str:
    if m < 15: return "🟢"
    if m < 25: return "🟡"
    return "🔴"


m1_oot_metrics, _ = load_oot("m1")
m2_oot_metrics, _ = load_oot("m2")
m1_mape = m1_oot_metrics["oot_metrics"]["mape_pct"]
m2_mape = m2_oot_metrics["oot_metrics"]["mape_pct"]
st.success(
    f"**Out-of-time forecast accuracy** (on hold-out weeks the model never trained on; "
    f"MAPE = average percent error, lower is better): "
    f"conversions model {m1_mape:.1f}% {_mape_dot(m1_mape)} · "
    f"LTV model {m2_mape:.1f}% {_mape_dot(m2_mape)}. "
    f"This out-of-time check is the headline accuracy measure for MMM."
)
st.caption(
    "The cost and value figures on the rest of this page are from the **LTV model**. "
    "**Conversion-model** accuracy lives on the Out-of-Time page below."
)
st.page_link("pages/2_OOT_Validation.py", label="Open Out-of-Time Validation page", icon="📈")

# ── Model health & diagnostics (tucked into an expander) ──────────────────────
# D029 (2026-05-20): D021 <20% baseline gate DEPRECATED. Two-metric pair
# (in-window + global), neutral coloring; global baseline now shown with the
# apples-to-apples band inline (not tooltip-only) so the bare 67% doesn't read
# as "two-thirds unexplained" on a shared screen.
baseline_split = load_baseline_split()
in_window_pct = baseline_split["aggregate"]["in_window_baseline_pct"]
global_pct    = baseline_split["sanity"]["global_baseline_pct"]
with st.expander("Model health & diagnostics (convergence checks + baseline breakdown)"):
    mc1, mc2, mc3, mc4, mc5 = st.columns(5)
    rhat = conv["convergence"]["rhat_max"]
    ess  = conv["convergence"]["ess_min"]
    mc1.metric("R-hat (convergence, want < 1.1)", f"{rhat:.3f}",
               delta="PASS" if rhat < 1.1 else "FAIL",
               delta_color="normal" if rhat < 1.1 else "inverse",
               help="Did the model's estimates settle? Values near 1.0 mean yes.")
    mc2.metric("Effective samples (want > 400)", f"{int(ess)}",
               delta="PASS" if ess > 400 else "FAIL",
               delta_color="normal" if ess > 400 else "inverse",
               help="How much independent information the estimates rest on. Higher is better.")
    mc3.metric(
        "Baseline (lift-test weeks)",
        f"{in_window_pct:.1f}%",
        delta="reported",
        delta_color="off",
        help=(
            "Baseline = demand not attributed to measured paid spend. This is the "
            "average across the weeks that overlap the channel experiments. "
            "See the Methodology page for the full breakdown."
        ),
    )
    mc4.metric(
        "Baseline (all weeks)",
        f"{global_pct:.1f}%",
        delta="reported",
        delta_color="off",
        help=(
            "Baseline across all weeks in the data. See the note below for the "
            "like-for-like comparison against the attributed-revenue universe."
        ),
    )
    mc5.metric("Channels modeled", str(conv["n_channels"]))
    st.caption(
        f"**Baseline (all weeks) {global_pct:.1f}%** is not 'unexplained.' It breaks down into "
        f"~35% organic LTV that no paid channel can claim (consistent with Northbeam's "
        f"~65%-attributed / ~35%-organic split) plus ~32 points of paid demand the model "
        f"can't yet credit to a channel (largely Meta Web, where conversions are driven by "
        f"ad views rather than clicks). On a like-for-like attributed-revenue basis this is a "
        f"**~45–57% band**, comparable to Northbeam. See the Methodology page for the full breakdown."
    )

st.markdown("---")

# ── Row 1: Baseline metrics ──────────────────────────────────────────────────
display_name = CHANNEL_DISPLAY.get(channel_key, channel_key)
st.markdown(f"#### Headline Cost & Return: {display_name}")
if is_lift_tested:
    gate_label = "in band" if baseline.get("windowed_gate_pass") else "outside band"
    gate_color = "✅" if baseline.get("windowed_gate_pass") else "❌"
    st.caption(
        f"Headline cost per acquired customer (iCAC) = the model's best estimate **during this "
        f"channel's experiment window**. Experiment result to match: "
        f"**${baseline['windowed_iCAC_truth']:.0f} ± ${baseline['windowed_iCAC_tol']:.0f}**. "
        f"Model vs experiment: {gate_color} **{gate_label}**. "
        f"For reference, the all-history average iCAC is ${baseline['agg_iCAC_script09']:.0f}."
    )
else:
    st.caption(
        "Headline cost per acquired customer (iCAC) = **all-history average** (no experiment for "
        "this channel, so uncertainty is higher than for lift-tested channels). "
        "Tested channels can be checked against their experiment result; untested channels cannot."
    )
col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(fig_icac_baseline(baseline, channel=channel_key),
                    use_container_width=True, config=CONFIG)
    with st.expander("Reading this chart"):
        if is_lift_tested:
            st.caption(
                f"**Headline iCAC ${baseline['icac_mean']:,.0f}** (best estimate during the experiment "
                f"window; credible range ${baseline['icac_hdi_lo']:,.0f}–${baseline['icac_hdi_hi']:,.0f}). "
                f"The experiment result to match is ${baseline['windowed_iCAC_truth']:.0f} ± "
                f"${baseline['windowed_iCAC_tol']:.0f}; the model is in band if the headline falls inside. "
                f"For context, the all-history average iCAC is ${baseline['agg_iCAC_script09']:.0f}."
            )
        else:
            st.caption(
                f"**Headline iCAC ${baseline['icac_mean']:,.0f}** (all-history average best estimate; "
                f"credible range ${baseline['icac_hdi_lo']:,.0f}–${baseline['icac_hdi_hi']:,.0f}). "
                f"No experiment exists for {display_name}, so there is no result to check against. "
                f"Compare against other channels with similar spend for relative ranking."
            )

with col2:
    st.plotly_chart(fig_iroas_baseline(baseline, channel=channel_key),
                    use_container_width=True, config=CONFIG)
    with st.expander("Reading this chart"):
        st.caption(
            f"**Baseline iROAS {baseline['iroas_mean']:.3f}x** (best estimate; credible range "
            f"{baseline['iroas_hdi_lo']:.3f}–{baseline['iroas_hdi_hi']:.3f}): LTV dollars attributed per dollar of spend. "
            f"There is a {baseline['iroas_below_breakeven_pct']:.0f}% chance this channel is below the 1.0x break-even line."
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
    "These curves show how the cost and return of the **next** dollar of spend (marginal "
    "efficiency) change at different spend levels. The vertical line marks the typical (median) "
    "weekly spend. Moving right means more spend and diminishing returns: higher cost per "
    "customer (iCAC), lower return (iROAS)."
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
    "in the left sidebar: a 19-row sortable table with the 8-column decisioning "
    "framework your team approved on 2026-05-12."
)

# ── Footer ───────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption(
    f"**Data window:** {conv['weekly_obs']} weeks | "
    f"**Channels in model:** {conv['n_channels']} | "
    f"**avg LTV per customer:** ${baseline['avg_ltv']:,.2f} | "
    f"**Model version:** May 2026 calibration"
)
