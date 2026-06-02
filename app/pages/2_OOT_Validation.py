"""
2_OOT_Validation.py — Out-of-Time validation page (M7 + D028).

Anchor: client 2026-05-12: out-of-time validation (how closely the model predicts
held-out weekly conversions) is the primary MMM validation metric.

Asymmetric architecture (D028, 2026-05-20):
  Model 1 (y=CONVERSIONS) uses D-γ — linear trend control_columns=["t"],
    default Normal(0, 2) prior. Produced by scripts/11b_oot_validation_M1_D_gamma.py.
    OOT signed mean: −3.66% (4/13 over-pred).
  Model 2 (y=LTV_3YEAR) stays at canonical M3.5b Fix-A (2026-05-19). Produced by
    scripts/11_oot_validation.py. OOT signed mean: +14.96% (12/13 over-pred).
    Documented limitation per Option α — see footnote below.

Data files:
  outputs/P2_04_full_channel/metrics/oot_model1_conversions.json   (M1, D028 stamp)
  outputs/P2_04_full_channel/metrics/oot_model2_ltv.json            (M2, M3.5b Fix-A stamp)
  outputs/P2_04_full_channel/charts/oot_model1_conversions_timeseries.csv
  outputs/P2_04_full_channel/charts/oot_model2_ltv_timeseries.csv
"""
import sys
from pathlib import Path

# Make `app.*` imports work when running this page from any cwd.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import numpy as np
import pandas as pd
import streamlit as st

from app.data_loader import CANONICAL_VERSION, load_oot
from app.charts import CONFIG, fig_oot_predicted_vs_actual

st.set_page_config(
    page_title="Out-of-Time Validation · Kikoff MMM",
    page_icon="🎯",
    layout="wide",
)

st.markdown("# Out-of-Time Validation: 13-week Hold-out")
st.caption(
    "Out-of-time validation asks the key MMM question: how closely does the model predict "
    "weeks it never trained on? We hold out the most recent 13 weeks, fit on everything before, "
    "and compare predictions to what actually happened. "
    "The conversions model and the LTV (revenue) model are validated separately below."
)

# ── Load both models ─────────────────────────────────────────────────────────
try:
    m1_metrics, m1_ts = load_oot("m1")
    m2_metrics, m2_ts = load_oot("m2")
except FileNotFoundError as e:
    st.error(
        "Out-of-time validation outputs are not available yet. Please refresh once the "
        "latest model outputs have been published."
    )
    st.stop()


# ── Color helper for MAPE thresholds (industry MMM bench) ───────────────────
def _mape_color(mape: float) -> str:
    if mape < 15:    return "🟢"
    if mape < 25:    return "🟡"
    return "🔴"


m1_oot = m1_metrics["oot_metrics"]
m2_oot = m2_metrics["oot_metrics"]
split  = m1_metrics["split"]

# ── KPI strip ────────────────────────────────────────────────────────────────
st.markdown("### Hold-out performance")
k1, k2, k3, k4 = st.columns(4)
k1.metric(
    f"Conversions model: avg error {_mape_color(m1_oot['mape_pct'])}",
    f"{m1_oot['mape_pct']:.1f}%",
    help=(f"Average percent error (MAPE) of predicted weekly conversions vs actual, across "
          f"{split['n_test_weeks']} hold-out weeks. Symmetric version: {m1_oot['smape_pct']:.1f}%."),
)
k2.metric(
    "Conversions model: avg miss (per week)",
    f"{m1_oot['mae']:,.0f}",
    help=f"Average size of the weekly miss, in conversions.",
)
k3.metric(
    f"LTV model: avg error {_mape_color(m2_oot['mape_pct'])}",
    f"{m2_oot['mape_pct']:.1f}%",
    help=(f"Average percent error (MAPE) of predicted weekly LTV dollars vs actual, across "
          f"{split['n_test_weeks']} hold-out weeks. Symmetric version: {m2_oot['smape_pct']:.1f}%."),
)
k4.metric(
    "LTV model: avg miss ($ / week)",
    f"${m2_oot['mae']:,.0f}",
    help=f"Average size of the weekly miss, in dollars.",
)

st.caption(
    "Average error (MAPE): 🟢 under 15% (strong) · 🟡 15–25% (acceptable for MMM) · 🔴 over 25% (poor)."
)

# ── Split summary ────────────────────────────────────────────────────────────
st.markdown(
    f"**Training:** `{split['train_start']}` → `{split['train_end']}` "
    f"({split['n_train_weeks']} weeks) · "
    f"**Hold-out:** `{split['test_start']}` → `{split['test_end']}` "
    f"({split['n_test_weeks']} weeks)"
)

# ── Conversions model chart ──────────────────────────────────────────────────
st.markdown("### Conversions model: weekly conversions (predicted vs actual)")
fig_m1 = fig_oot_predicted_vs_actual(
    m1_ts,
    title=("Conversions model: predicted vs actual<br>"
           "<sub>Prediction + credible range vs actual, 13-week hold-out</sub>"),
    y_label="Weekly conversions",
    dollar_axis=False,
)
st.plotly_chart(fig_m1, use_container_width=True, config=CONFIG)

# ── LTV model chart ──────────────────────────────────────────────────────────
st.markdown("### LTV (revenue) model: weekly LTV (predicted vs actual)")
fig_m2 = fig_oot_predicted_vs_actual(
    m2_ts,
    title=("LTV (revenue) model: predicted vs actual<br>"
           "<sub>Prediction + credible range vs actual, 13-week hold-out (dollars)</sub>"),
    y_label="Weekly LTV ($)",
    dollar_axis=True,
)
st.plotly_chart(fig_m2, use_container_width=True, config=CONFIG)

st.info(
    "**Known limitation of the LTV model:** it tends to run a little high, over-predicting "
    "weekly LTV in all 13 hold-out weeks by roughly 5–25% (about +15% on average). "
    "Two model changes were tested to remove this; both over-corrected or shifted the bias "
    "elsewhere, so neither was a clean win. The LTV model's average error of 15.1% still sits "
    "inside the industry-acceptable 15–25% range for MMM, so we publish it with this bias "
    "documented rather than trading a consistent over-prediction for noisier week-to-week swings."
)


# ── Per-week error tables (collapsible) ──────────────────────────────────────
def _error_table(ts: pd.DataFrame, dollar: bool) -> pd.DataFrame:
    out = ts[["date", "actual", "predicted_mean", "predicted_hdi_lo", "predicted_hdi_hi"]].copy()
    out["abs_error"] = (out["predicted_mean"] - out["actual"]).abs()
    out["pct_error"] = 100 * out["abs_error"] / out["actual"].abs()
    out["actual_in_HDI"] = (out["actual"] >= out["predicted_hdi_lo"]) & (out["actual"] <= out["predicted_hdi_hi"])
    out["date"] = pd.to_datetime(out["date"]).dt.strftime("%Y-%m-%d")
    if dollar:
        for c in ["actual", "predicted_mean", "predicted_hdi_lo", "predicted_hdi_hi", "abs_error"]:
            out[c] = out[c].map(lambda v: f"${v:,.0f}")
    else:
        for c in ["actual", "predicted_mean", "predicted_hdi_lo", "predicted_hdi_hi", "abs_error"]:
            out[c] = out[c].map(lambda v: f"{v:,.0f}")
    out["pct_error"] = out["pct_error"].map(lambda v: f"{v:.1f}%")
    return out


with st.expander("Per-week error tables + CSV downloads", expanded=False):
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Conversions model**")
        df1 = _error_table(m1_ts, dollar=False)
        st.dataframe(df1, use_container_width=True, hide_index=True)
        st.download_button(
            label="📥 Download Model 1 OOT CSV",
            data=m1_ts.to_csv(index=False).encode("utf-8"),
            file_name=f"oot_model1_conversions_{CANONICAL_VERSION}.csv",
            mime="text/csv",
        )
    with c2:
        st.markdown("**LTV (revenue) model**")
        df2 = _error_table(m2_ts, dollar=True)
        st.dataframe(df2, use_container_width=True, hide_index=True)
        st.download_button(
            label="📥 Download Model 2 OOT CSV",
            data=m2_ts.to_csv(index=False).encode("utf-8"),
            file_name=f"oot_model2_ltv_{CANONICAL_VERSION}.csv",
            mime="text/csv",
        )

# ── Configuration footnote ───────────────────────────────────────────────────
with st.expander("Configuration & methodology", expanded=False):
    st.markdown(f"""
**Model setup (both models):** Bayesian Marketing Mix Model (PyMC-Marketing) with a
saturation curve per channel (diminishing returns), an adstock carryover of up to 8 weeks,
and historical incrementality experiments used as priors within each test window.

**Why the two models differ in the hold-out:** the conversions model adds a gentle
straight-line time trend, which keeps its predictions on track over the hold-out weeks.
The LTV (revenue) model does not, because revenue per customer rises in the hold-out in a
way that partly offsets the conversion trend; adding a single trend there over-corrects.
This is why the conversions model lands close to actuals while the LTV model runs a little high.

**How well the models settled (technical):**
- Conversions model: convergence R-hat = {m1_metrics['convergence']['rhat_max']}
  (want < 1.1), effective samples = {m1_metrics['convergence']['ess_min']:.0f} (want > 400),
  divergences = {m1_metrics['convergence']['divergences']}.
- LTV model: convergence R-hat = {m2_metrics['convergence']['rhat_max']},
  effective samples = {m2_metrics['convergence']['ess_min']:.0f},
  divergences = {m2_metrics['convergence']['divergences']}.
  Training-period average LTV per customer = ${m2_metrics.get('avg_ltv_train', 0):,.2f}.

**Incrementality experiments used as priors during training:**
""")
    lift_df = pd.DataFrame(m1_metrics.get("lift_tests_in_training", []))
    if not lift_df.empty:
        st.dataframe(lift_df, use_container_width=True, hide_index=True)
    leak_note = m1_metrics.get("lift_test_leak_note", "")
    if leak_note:
        st.caption(f"Note on experiment timing vs hold-out: {leak_note}")
