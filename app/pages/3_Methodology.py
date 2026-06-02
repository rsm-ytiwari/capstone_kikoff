"""
3_Methodology.py — Baseline decomposition + per-channel concentration diagnostic.

Explains why the <20% baseline target was replaced with a per-channel
concentration diagnostic + data-scope disclosure. Five sections:
  1. Baseline decomposition (all-weeks / lift-test-weeks / other-weeks + like-for-like band)
  2. Per-channel attribution concentration table
  3. View-through mechanism for Meta Web
  4. Data-scope ask: attributed-revenue feed from Kikoff
  5. Why the <20% target was replaced

Reads the baseline-decomposition artifact (read-only consumer of the LTV trace).
"""
from pathlib import Path
import sys

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from app.data_loader import load_baseline_split  # noqa: E402


st.set_page_config(page_title="Kikoff MMM · Methodology", page_icon="📐", layout="wide")

st.markdown("# Methodology: Baseline Decomposition & Per-Channel Concentration")
st.caption(
    "Baseline = the share of LTV the model can't attribute to measured paid spend "
    "(organic demand plus any paid demand the model can't yet credit to a channel)."
)

split = load_baseline_split()
agg = split["aggregate"]
sanity = split["sanity"]
ref = split["reference"]
per_ch = split["per_channel"]

# ── Section 1: Baseline decomposition ────────────────────────────────────────
st.markdown("## 1 · Baseline decomposition")

c1, c2, c3 = st.columns(3)
c1.metric("Baseline (all weeks)",        f"{sanity['global_baseline_pct']:.2f}%",
          help="Across all 93 weeks in the data.")
c2.metric("Baseline (lift-test weeks)",  f"{agg['in_window_baseline_pct']:.2f}%",
          help=f"Across the {split['n_weeks_in_window_union']} weeks that overlap any of the 7 channel experiments.")
c3.metric("Baseline (other weeks)",      f"{agg['out_window_baseline_pct']:.2f}%",
          help=f"Across the remaining {split['n_weeks_out_of_window']} weeks.")

delta_pp = round(agg['out_window_baseline_pct'] - agg['in_window_baseline_pct'], 2)
st.markdown(
    f"**Lift-test weeks vs other weeks: a {delta_pp}pp difference.** "
    "We expected the experiment-window priors to pull a lot of attribution into those weeks; "
    f"in practice the effect is modest. The lift-test-week baseline ({agg['in_window_baseline_pct']:.1f}%) "
    "is still far above a 20% target, so that target is out of reach even on a lift-test-week basis."
)

st.markdown("### Like-for-like baseline on the attributed-revenue universe")
st.markdown(
    "The original <20% baseline target was framed against the **attributed-revenue universe** "
    "Northbeam ran on, not against total LTV. Northbeam's universe is roughly 65% attributed / "
    "35% organic. Putting our baseline on that same like-for-like universe:"
)
c4, c5, c6 = st.columns(3)
c4.metric("Organic share (anchor)",
          f"{ref['abheek_implied_organic_baseline_pct']:.0f}%",
          help="Client-implied: '~65% attributed, ~35% organic.' Approximate; ±5pp uncertainty.")
c5.metric("Like-for-like baseline (point)",
          f"{ref['baseline_pct_on_attributed_universe_apples_to_apples']:.2f}%",
          help="= (all-weeks baseline − organic share) / attributed share, at organic = 35%.")
c6.metric("Like-for-like band (±5pp)",
          f"{ref['baseline_pct_on_attributed_universe_range']}%",
          help="Organic 30% → ~53%; organic 35% (anchor) → ~50%; organic 40% → ~46%. "
               "Communicate as a band, not a point.")

st.info(
    f"**Gap to the 20% target ≈ {ref['gap_to_d021_target_pp']:.1f}pp at the anchor**, and well over "
    "20pp at either end of the organic band. The takeaway holds across the uncertainty: the 20% "
    "target is not reachable on the current data scope (total LTV) without an attributed-revenue feed."
)


# ── Section 2: Per-channel attribution concentration ────────────────────────
st.markdown("## 2 · Per-channel attribution concentration")
st.caption(
    "Concentration ratio = (attribution per week during the channel's own experiment window) "
    "÷ (attribution per week outside it). This is our attribution-confidence diagnostic: it "
    "tells us whether the experiment prior actually concentrated credit in the test window."
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
            if d["in_window_share_of_own_total"] is not None else "n/a"
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
| ≤ 1.1x | Prior shifted the channel's overall level but did NOT move attribution into the window. Suggests credit driven by ad views rather than clicks, or the saturation curve doing the level work |
| < 1.0x | Inverse: channel contributes more outside its window than during. A flag for inspection, not a failure |

This is a diagnostic, not a pass/fail gate. Channels in the ≤ 1.1x band are candidates
for closer inspection: see Section 3 for the Meta Web mechanism.
"""
)


# ── Section 3: View-through mechanism for Meta Web ──────────────────────────
st.markdown("## 3 · View-through mechanism for Meta Web")
meta_web_ratio = per_ch["meta_web"]["concentration_ratio_in_over_out"]

st.markdown(
    f"Meta Web's concentration ratio is **{meta_web_ratio}x**: essentially flat, even though an "
    "earlier calibration step pulled its experiment-window cost per customer from $466 down to $281. "
    "The experiment prior shifted Meta Web's overall level but did NOT move its attribution into "
    "the test window."
)

st.markdown(
    """
**Why** (in the client's own words, 2026-05-12):

> *"A large portion of view-through attribution flows from Meta Web. Every
> time Meta Web spend is scaled up, attributed conversions don't spike in
> dashboards (because of view-through), but blended numbers grow consistently.
> Every time spend is pulled back, both numbers degrade within a week.
> Northbeam's MMM picked this up correctly; our model has not."*

View-through means a customer sees a Meta ad, doesn't click, but converts later;
the conversion is never linked back to the ad. Our model's inputs are paid spend
only, with no signal for these view-driven conversions. So the experiment prior
can shift Meta Web's level but can't move attribution into the test window, because
those weeks don't capture the delayed view-through conversions either. The flat
1.04x ratio is the in-model fingerprint of this mechanism.
"""
)
st.warning(
    "This is different from a generic calibration miss. Adding more channels or tightening "
    "more priors will not close the gap; only an attributed-revenue feed (see Section 4) "
    "addresses the root cause."
)


# ── Section 4: Data-scope ask (Q36) ─────────────────────────────────────────
st.markdown("## 4 · Discussable extension: an attributed-revenue feed")
st.markdown(
    "**Current data scope:** the model's target is total LTV (the data has conversions plus "
    "1-year and 3-year LTV, with no organic-vs-paid flag), and its inputs are paid spend only. "
    "So the ~35% organic-LTV slice has nowhere to go but baseline, by construction."
)
st.markdown(
    """
**Ask for Kikoff:** Can Kikoff provide an attributed-revenue LTV feed (a Northbeam
attributed-revenue export or equivalent), so the model can run on the same revenue
universe the <20% baseline target was framed against?

**Cost of no answer:** the <20% target stays out of reach, and the baseline
conversation stays anchored to the all-weeks ~67% number rather than the like-for-like
~45–57% band. The per-channel concentration diagnostic works without this feed, but the
data-scope ask is the cleanest path to actually closing the gap.

**Possible answers:**
- **Yes** (attributed-revenue export, weekly or daily): re-fit the model on attributed
  revenue and reinstate a tighter baseline target on that universe.
- **Partial** (one-time snapshot or an aggregate ratio): use it as a scaling factor and
  sanity check; no re-fit.
- **No** (Kikoff doesn't have this): per-channel concentration remains the diagnostic, and
  we document this as a permanent data-scope limitation in the deliverables.
"""
)


# ── Section 5: why the <20% gate was replaced ───────────────────────────────
st.markdown("## 5 · Why the <20% baseline target was replaced")
st.markdown(
    """
We initially set a baseline target of <20%, reading the client's number as a target on
the **total-revenue** universe. On closer reading, that <20% was framed against the
**attributed-revenue universe** Northbeam runs on (~65% of total LTV, ~35% organic), not
against total LTV.

- On the total-LTV universe the model fits, the equivalent target would be roughly 13%.
- On the like-for-like attributed universe, our model's baseline is a **~45–57% band**
  (about 50% at the 35%-organic anchor), not the headline 67%.

The remaining gap to <20% comes from two things:

1. **Missed paid attribution from view-driven channels** (largely Meta Web; confirmed by
   the flat 1.04x concentration ratio in Section 3).
2. **Other unmodeled organic / brand demand** absorbed by the 12 untested channels, which
   carry weak default assumptions.

Closing the gap requires an **attributed-revenue feed** (Section 4), not more model tuning.
A target that's technically met but carries no actionable signal would be cosmetic; the
per-channel concentration diagnostic, which separates a well-calibrated channel from one
whose level shifted without attribution moving into its window, is the information the
client can actually act on.
"""
)
