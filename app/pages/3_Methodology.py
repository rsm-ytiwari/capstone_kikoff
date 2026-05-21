"""
3_Methodology.py — Baseline decomposition + per-channel concentration diagnostic (D029).

Surfaces the M3.5e empirical findings that motivated deprecating D021's <20%
baseline gate. Five sections:
  1. Baseline decomposition (global / in-window / out-of-window + apples-to-apples band)
  2. Per-channel attribution concentration table
  3. View-through mechanism for Meta Web (Mtg 6 fact #13)
  4. Data-scope ask (Q36): attributed-revenue feed from Kikoff
  5. D029 supersession rationale

Reads `outputs/P2_04_full_channel/metrics/baseline_split.json` (produced by
`scripts/15_baseline_split.py`, read-only consumer of the canonical M2 trace).
"""
from pathlib import Path
import sys

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from app.data_loader import load_baseline_split, CANONICAL_VERSION  # noqa: E402


st.set_page_config(page_title="Kikoff MMM — Methodology", page_icon="📐", layout="wide")

st.markdown("# Methodology — Baseline Decomposition & Per-Channel Concentration (D029)")
st.caption(f"Canonical: `{CANONICAL_VERSION}` · D029 artifact stamp shown per section.")

split = load_baseline_split()
agg = split["aggregate"]
sanity = split["sanity"]
ref = split["reference"]
per_ch = split["per_channel"]

# ── Section 1: Baseline decomposition ────────────────────────────────────────
st.markdown("## 1 · Baseline decomposition")
st.caption(f"Artifact: `outputs/P2_04_full_channel/metrics/baseline_split.json` · "
           f"stamp `{split['stamp']}`")

c1, c2, c3 = st.columns(3)
c1.metric("Baseline (global)",        f"{sanity['global_baseline_pct']:.2f}%",
          help="Across all 93 weeks (cross-checks ltv_window_scaled.json — sanity PASS)")
c2.metric("Baseline (in-window)",     f"{agg['in_window_baseline_pct']:.2f}%",
          help=f"Across {split['n_weeks_in_window_union']} W-MON weeks overlapping any of the 7 lift-test windows")
c3.metric("Baseline (out-of-window)", f"{agg['out_window_baseline_pct']:.2f}%",
          help=f"Across the remaining {split['n_weeks_out_of_window']} weeks")

delta_pp = round(agg['out_window_baseline_pct'] - agg['in_window_baseline_pct'], 2)
st.markdown(
    f"**In-window vs out-of-window delta = {delta_pp}pp.** "
    "The original M3.5e hypothesis assumed windowed priors would produce a "
    "dramatic in/out split; empirically the effect is modest. The in-window "
    f"baseline ({agg['in_window_baseline_pct']:.1f}%) is still 41pp above D021's "
    "20% target — the gate is also unreachable on a within-window basis."
)

st.markdown("### Apples-to-apples baseline on the attributed-revenue universe")
st.markdown(
    f"Abheek's <20% baseline target (Mtg 6 fact #10) was framed against the "
    f"**attributed-revenue universe** Northbeam initially ran on, not against "
    f"total LTV (Mtg 6 fact #13: ~65% attributed / ~35% organic). On that "
    f"apples-to-apples universe:"
)
c4, c5, c6 = st.columns(3)
c4.metric("Organic anchor (Abheek-implied)",
          f"{ref['abheek_implied_organic_baseline_pct']:.0f}%",
          help="Mtg 6 fact #13: '~65% attributed, ~35% organic.' Approximate; ±5pp uncertainty.")
c5.metric("Apples-to-apples baseline (point)",
          f"{ref['baseline_pct_on_attributed_universe_apples_to_apples']:.2f}%",
          help="= (global − organic) / attributed_share. At anchor organic = 35%.")
c6.metric("Apples-to-apples band (±5pp)",
          f"{ref['baseline_pct_on_attributed_universe_range']}%",
          help="Organic 30%→~53.33%; organic 35% (anchor)→~49.74%; organic 40%→~45.55%. "
               "Communicate as band, not point.")

st.info(
    f"**Gap to D021 target ≈ {ref['gap_to_d021_target_pp']:.1f}pp at anchor.** "
    "Materially > 20pp at either end of the ±5pp organic band. The qualitative "
    "conclusion — D021's target is architecturally unreachable on the current "
    "data scope — survives the uncertainty band."
)


# ── Section 2: Per-channel attribution concentration ────────────────────────
st.markdown("## 2 · Per-channel attribution concentration (D029 diagnostic)")
st.caption(
    "Concentration ratio = (in-window $/wk) ÷ (out-of-window $/wk) for each "
    "channel's OWN lift-test window. Replaces D021's threshold gate as the "
    "new attribution-confidence diagnostic."
)

rows = []
for ch, d in per_ch.items():
    rows.append({
        "Channel": ch,
        "Own-window weeks": d["own_window_weeks"],
        "In-window $/wk": d["in_window_$_per_week"],
        "Out-of-window $/wk": d["out_window_$_per_week"],
        "Concentration ratio": d["concentration_ratio_in_over_out"],
        "In-window share of own total": (
            f"{d['in_window_share_of_own_total']*100:.1f}%"
            if d["in_window_share_of_own_total"] is not None else "—"
        ),
    })

df = pd.DataFrame(rows).sort_values("Concentration ratio", ascending=False)
st.dataframe(
    df,
    hide_index=True,
    column_config={
        "In-window $/wk":         st.column_config.NumberColumn(format="$%.0f"),
        "Out-of-window $/wk":     st.column_config.NumberColumn(format="$%.0f"),
        "Concentration ratio":    st.column_config.NumberColumn(format="%.2fx"),
    },
)

st.markdown(
    """
**Reading guide:**

| Range | Reading |
|---|---|
| ≥ 1.5x | Prior meaningfully concentrates attribution in the test window (well-fit) |
| 1.1x – 1.5x | Moderate concentration |
| ≤ 1.1x | Prior shifted the channel's level but did NOT redistribute attribution into the window. Suggests view-through credit invisible to X, or saturation curve doing the level work |
| < 1.0x | INVERSE — channel contributes more outside its window than during. Diagnostic-only flag, not a gate failure |

Diagnostic-only; no PASS/FAIL gate. Channels in the ≤ 1.1x band are candidates
for closer inspection — see Section 3 for the Meta Web mechanism.
"""
)


# ── Section 3: View-through mechanism for Meta Web ──────────────────────────
st.markdown("## 3 · View-through mechanism for Meta Web (Mtg 6 fact #13)")
meta_web_ratio = per_ch["meta_web"]["concentration_ratio_in_over_out"]

st.markdown(
    f"Meta Web's in-window vs out-of-window concentration ratio is **{meta_web_ratio}x** "
    "— essentially flat, despite Fix-A (D027) pulling its windowed iCAC from "
    "$466 → $281. The lift-prior shifted Meta Web's mean level but did NOT "
    "redistribute its attribution into the test window."
)

st.markdown(
    """
**Why** — from Abheek 2026-05-12 (Mtg 6 fact #13, verbatim):

> *"A large portion of view-through attribution flows from Meta Web. Every
> time Meta Web spend is scaled up, attributed conversions don't spike in
> dashboards (because of view-through), but blended numbers grow consistently.
> Every time spend is pulled back, both numbers degrade within a week.
> Northbeam's MMM picked this up correctly; our model has not."*

Our model's X carries no view-through proxy. The true coupling between Meta
Web spend and conversions is view-through-mediated, so the lift-prior can
only shift Meta Web's level — it cannot redistribute attribution into the
test window because the test-window weeks don't capture the lagged
view-through conversions either. The 1.04x concentration is the **in-model
fingerprint** of this mechanism.
"""
)
st.warning(
    "This is qualitatively different from a generic calibration miss. Adding "
    "more channels or tightening more priors will not close the gap; only an "
    "attributed-revenue feed (Q36) addresses the root cause."
)


# ── Section 4: Data-scope ask (Q36) ─────────────────────────────────────────
st.markdown("## 4 · Discussable extension — attributed-revenue feed (Q36)")
st.markdown(
    f"**Current data scope:** y = total LTV "
    f"(`data/MMM_UPDATED_LTV.csv` columns = [DS, CONVERSIONS, LTV_1YEAR, "
    f"LTV_3YEAR] — no organic/paid attribution flag). X = paid spend only. "
    f"The ~35% organic-LTV slice has nowhere to go but baseline by construction."
)
st.markdown(
    """
**Ask for Kikoff (Q36, For Client):** Can Kikoff provide an attributed-revenue
LTV feed (Northbeam attributed-revenue CSV or equivalent) so the model can be
run on the same revenue universe Abheek's <20% target was framed against?

**Cost of no-answer:** D021's <20% target stays architecturally out-of-reach.
The baseline conversation stays anchored to the global 67% number rather than
the apples-to-apples ~45–57% band. Per-channel concentration diagnostic
(D029) is the active replacement and works without this feed — but the data-scope
ask is the cleanest path to actually closing the gap.

**Possible client answers:**
- **YES** (Northbeam attributed-revenue CSV, weekly or daily granularity) → re-fit
  model on attributed-revenue y; reinstate tighter baseline threshold (TBD) on that
  universe; potentially supersede D029.
- **PARTIAL** (one-time snapshot or aggregated ratio) → use as scaling factor and
  sanity check; don't refit.
- **NO** (Kikoff doesn't have this) → D029 stays canonical; per-channel
  concentration remains the diagnostic; document as a permanent data-scope
  limitation in deliverables.
"""
)


# ── Section 5: D029 supersession rationale ──────────────────────────────────
st.markdown("## 5 · D029 supersession of D021")
st.markdown(
    f"""
**D021 (2026-05-18)** set Kikoff's baseline gate at < 20%, citing Abheek
2026-05-12 (13:03 + 44:14). At the time we interpreted this as a target on
the *total-revenue* universe.

**D029 (2026-05-20)** supersedes D021 because Mtg 6 fact #13 (which D021 under-weighted)
reveals Abheek's <20% number was framed against the **attributed-revenue universe**
Northbeam ran on (~65% of total LTV, ~35% organic). On the total-LTV universe
the model fits, the equivalent target would be ~13%; on the apples-to-apples
attributed universe our model's baseline is **~45–57% band** (point 49.74% at
organic = 35%), not 67%. The remaining ~30pp gap to <20% reflects:

1. **Missed paid attribution from view-through-mediated channels** (largely
   Meta Web; mechanistically confirmed by the 1.04x concentration ratio).
2. **Other unmodeled organic/brand acquisition** absorbed by 12 untested
   channels with weakly-informative defaults.

Closing the gap requires an **attributed-revenue feed** (Q36), not further
model-spec calibration. A passable gate without an actionable signal would be a
face-saver; a diagnostic that distinguishes "well-calibrated channel" (high
concentration) from "level-shifted but not attribution-redistributed channel"
(low concentration) is the information Abheek can act on at the next meeting.

**Decisions superseded:** D021 (entry retained with `[SUPERSEDED → D029]` suffix).
**Decisions companion:** D025 (Lever C lam prior) and D027 (Fix-A) UNCHANGED;
D028 (M1 D-γ OOT + M2 Option α) orthogonal.

**Audit trail:**
- Script: `scripts/15_baseline_split.py` (read-only; canonical M2 trace consumer)
- Output: `outputs/P2_04_full_channel/metrics/baseline_split.json`
- Decision log: `state/decisions_log.md` D029 entry
- Proposal (archived): `proposals/archived/2026-05-20_d029_baseline_gate_redesign.md`
- Open questions: Q33 RESOLVED via D029; Q36 NEW (attribution-feed ask, For Client);
  Q37 NEW (future-iteration placeholder; NOT a re-open of DP-B)
"""
)
