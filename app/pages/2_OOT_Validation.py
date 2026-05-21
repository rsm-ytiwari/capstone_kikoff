"""
2_OOT_Validation.py — Out-of-Time validation page (M7 + D028).

Anchor: Abheek 2026-05-12 (37:38): "for MMM, I largely care on the out of
time validation. Like how closely is it able to predict the conversion
numbers."

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
    page_title="OOT Validation — Kikoff MMM",
    page_icon="🎯",
    layout="wide",
)

st.markdown("# Out-of-Time Validation — 13-week Hold-out")
st.caption(
    "*Abheek 2026-05-12: \"for MMM, I largely care on the out of time validation. "
    "Like how closely is it able to predict the conversion numbers.\"* "
    f"Base canonical: `{CANONICAL_VERSION}` (Lever C lam Gamma(2,2) + HalfNormal(2) β, "
    "GeometricAdstock l_max=8, Fix-A windowed lift priors). "
    "**D028 (2026-05-20):** Model 1 OOT uses asymmetric D-γ linear trend control (`control_columns=['t']`); "
    "Model 2 OOT stays at base canonical. Per-model stamps in the Configuration & methodology footnote."
)

# ── Load both models ─────────────────────────────────────────────────────────
try:
    m1_metrics, m1_ts = load_oot("m1")
    m2_metrics, m2_ts = load_oot("m2")
except FileNotFoundError as e:
    st.error(
        "OOT outputs not found. Run `scripts/11_oot_validation.py` first to "
        "generate them. Expected at "
        "`outputs/P2_04_full_channel/metrics/oot_model{1,2}_*.json` + "
        "`outputs/P2_04_full_channel/charts/oot_model{1,2}_*_timeseries.csv`."
    )
    st.exception(e)
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
    f"M1 · Conversions MAPE {_mape_color(m1_oot['mape_pct'])}",
    f"{m1_oot['mape_pct']:.1f}%",
    help=(f"Posterior-mean weekly conversions vs actual, averaged across "
          f"{split['n_test_weeks']} hold-out weeks. sMAPE: {m1_oot['smape_pct']:.1f}%. "
          f"89% HDI coverage: {m1_oot['hdi_89_coverage_pct']:.0f}%."),
)
k2.metric(
    "M1 · MAE (conversions / week)",
    f"{m1_oot['mae']:,.0f}",
    help=f"RMSE: {m1_oot['rmse']:,.0f}",
)
k3.metric(
    f"M2 · LTV_3YEAR MAPE {_mape_color(m2_oot['mape_pct'])}",
    f"{m2_oot['mape_pct']:.1f}%",
    help=(f"Posterior-mean weekly LTV dollars vs actual, averaged across "
          f"{split['n_test_weeks']} hold-out weeks. sMAPE: {m2_oot['smape_pct']:.1f}%. "
          f"89% HDI coverage: {m2_oot['hdi_89_coverage_pct']:.0f}%."),
)
k4.metric(
    "M2 · MAE ($ / week)",
    f"${m2_oot['mae']:,.0f}",
    help=f"RMSE: ${m2_oot['rmse']:,.0f}",
)

st.caption(
    "🟢 < 15% MAPE (strong) · 🟡 15–25% (acceptable for MMM) · 🔴 > 25% (poor generalization)."
)

# ── Split summary ────────────────────────────────────────────────────────────
st.markdown(
    f"**Training:** `{split['train_start']}` → `{split['train_end']}` "
    f"({split['n_train_weeks']} W-MON weeks) · "
    f"**Hold-out:** `{split['test_start']}` → `{split['test_end']}` "
    f"({split['n_test_weeks']} W-MON weeks)"
)

# ── Model 1 chart ────────────────────────────────────────────────────────────
st.markdown("### Model 1 — Weekly conversions (predicted vs actual) · D-γ trend control (D028)")
fig_m1 = fig_oot_predicted_vs_actual(
    m1_ts,
    title=("Model 1 · y = CONVERSIONS · D-γ trend control (D028)<br>"
           "<sub>Posterior mean + 89% HDI vs actual, 13-week hold-out</sub>"),
    y_label="Weekly conversions",
    dollar_axis=False,
)
st.plotly_chart(fig_m1, use_container_width=True, config=CONFIG)

# ── Model 2 chart ────────────────────────────────────────────────────────────
st.markdown("### Model 2 — Weekly LTV_3YEAR (predicted vs actual) · base canonical")
fig_m2 = fig_oot_predicted_vs_actual(
    m2_ts,
    title=("Model 2 · y = LTV_3YEAR · M3.5b Fix-A base canonical<br>"
           "<sub>Posterior mean + 89% HDI vs actual, 13-week hold-out (dollars)</sub>"),
    y_label="Weekly LTV_3YEAR ($)",
    dollar_axis=True,
)
st.plotly_chart(fig_m2, use_container_width=True, config=CONFIG)

st.info(
    "**Model 2 documented limitation (D028 Option α, 2026-05-20):** Model 2 systematically "
    "over-predicts weekly LTV in all 13 hold-out weeks by ~5–25%/week (signed mean +14.96%). "
    "Two architectural remedies tested under Q34 — D-γ trend control (over-corrected M2 to −14%) "
    "and D-ε (asymmetric per-window lift priors + post-multiply; pushed M2 further over). "
    "Both ruled out as cleanly improving M2 without trade-off. M2 OOT MAPE 15.13% remains inside "
    "the industry-acceptable 15–25% MMM band; Model 2 is published with this documented bias rather "
    "than an architectural fix that trades systematic over-prediction for week-to-week noise."
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
        st.markdown("**Model 1 — Conversions**")
        df1 = _error_table(m1_ts, dollar=False)
        st.dataframe(df1, use_container_width=True, hide_index=True)
        st.download_button(
            label="📥 Download Model 1 OOT CSV",
            data=m1_ts.to_csv(index=False).encode("utf-8"),
            file_name=f"oot_model1_conversions_{CANONICAL_VERSION}.csv",
            mime="text/csv",
        )
    with c2:
        st.markdown("**Model 2 — LTV_3YEAR**")
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
    m1_canon_stamp = m1_metrics.get("canonical_version", CANONICAL_VERSION)
    m2_canon_stamp = m2_metrics.get("canonical_version", CANONICAL_VERSION)
    st.markdown(f"""
**Base canonical:** `{CANONICAL_VERSION}` (M3.5b Fix-A, post-D027). Lever C lam
Gamma(2,2) + HalfNormal(2) β, GeometricAdstock l_max=8.

**Asymmetric OOT architecture (D028, 2026-05-20):**
- **Model 1 OOT stamp:** `{m1_canon_stamp}` — D-γ trend control `control_columns=["t"]`
  with default `Normal(0, 2)` prior on gamma_control. Produced by
  `scripts/11b_oot_validation_M1_D_gamma.py`. Accepted-cost: M1 meta_web windowed
  iCAC drifts $32.90 internally — NOT surfaced on Decisioning Summary or main
  dashboard (those read Model 2 only).
- **Model 2 OOT stamp:** `{m2_canon_stamp}` — base canonical, no trend control.
  Produced by `scripts/11_oot_validation.py`. +14.96% one-directional OOT
  over-prediction accepted as documented limitation per Option α.

**Model 1 convergence:** R-hat={m1_metrics['convergence']['rhat_max']},
ESS={m1_metrics['convergence']['ess_min']:.0f},
divergences={m1_metrics['convergence']['divergences']}.

**Model 2 convergence:** R-hat={m2_metrics['convergence']['rhat_max']},
ESS={m2_metrics['convergence']['ess_min']:.0f},
divergences={m2_metrics['convergence']['divergences']}.
Training-period avg LTV/customer = ${m2_metrics.get('avg_ltv_train', 0):,.2f}.

**OOS prediction API** (PyMC-Marketing 0.19.x canonical):
`mmm.sample_posterior_predictive(X_test, extend_idata=False,
include_last_observations=True, var_names=["y_original_scale"], random_seed=42)`.

**Lift tests in training** (per Fix-A LIFT_TESTS_CONV table, DP-D Option 3
APPROVED 2026-05-19):
""")
    lift_df = pd.DataFrame(m1_metrics.get("lift_tests_in_training", []))
    if not lift_df.empty:
        st.dataframe(lift_df, use_container_width=True, hide_index=True)
    st.markdown(f"""
**DP-D leak note:** {m1_metrics.get("lift_test_leak_note", "")}
""")
