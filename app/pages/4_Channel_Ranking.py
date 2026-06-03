"""
4_Channel_Ranking.py — channel rank-ordering by next-dollar cost per customer
and next-dollar return (LOCKED Meeting-8 deliverable, 2026-06-02).

Reads outputs/P2_09_ranking/metrics/channel_ranking.csv (scripts/24). The ORDER
is the signal; dollar magnitudes carry a known upward bias and tighten in a later
iteration. No outside-source comparison shown here.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import pandas as pd
import streamlit as st

from app.data_loader import (
    CHANNEL_DISPLAY, CANONICAL_VERSION, CHANNELS_LIFT_TESTED, load_channel_ranking,
)

st.set_page_config(
    page_title="Channel Ranking · Kikoff MMM",
    page_icon="🏁",
    layout="wide",
)

st.markdown("# Channel Ranking: Where the Next Dollar Works Hardest")
st.caption(
    "One ranking of the 19 channels, measured at each channel's recent typical weekly spend "
    "(the median of the last 26 weeks it was active). Each row shows two views of the same fact: "
    "the cost of the next acquired customer (lower is better) and the return on the next dollar "
    "(higher is better). The return is simply the average customer value divided by that cost, so "
    "the two columns place the channels in exactly the same order. They are shown side by side as "
    "one list, not as two separate checks. "
    "**Read the order, not the exact dollars.** The order is the durable signal; the dollar "
    "amounts run about 1.5 to 1.6 times high and will tighten in a later iteration. "
    "All figures come from the LTV model."
)

df = load_channel_ranking()
df = df.copy()
df["display"] = df["channel"].map(lambda c: CHANNEL_DISPLAY.get(c, c))

active = df[df["rank_icac"].notna()].copy()
excluded = df[df["rank_icac"].isna()]["display"].tolist()


def _spend(v: float) -> str:
    return f"${v:,.0f}"


def _money(v: float) -> str:
    return f"${v:,.0f}"


def _money_range(lo: float, hi: float) -> str:
    return f"${lo:,.0f} to ${hi:,.0f}"


def _x(v: float) -> str:
    return f"{v:.2f}x"


def _x_range(lo: float, hi: float) -> str:
    return f"{lo:.2f}x to {hi:.2f}x"


# ── One combined ranked view (both columns rank channels the same way) ───────
def _combined_view(sub: pd.DataFrame) -> pd.DataFrame:
    sub = sub.sort_values("rank_icac")
    return pd.DataFrame({
        "Rank": sub["rank_icac"].astype(int),
        "Channel": sub["display"],
        "Recent typical weekly spend": sub["recent_median_spend"].map(_spend),
        "Cost per next customer": sub["marg_icac_point"].map(_money),
        "Cost likely range (95%)": sub.apply(
            lambda r: _money_range(r["icac_lo95"], r["icac_hi95"]), axis=1
        ),
        "Return on next dollar": sub["marg_iroas_point"].map(_x),
        "Return likely range (95%)": sub.apply(
            lambda r: _x_range(r["iroas_lo95"], r["iroas_hi95"]), axis=1
        ),
    })


col_cfg = {
    "Rank": st.column_config.NumberColumn(width="small"),
    "Channel": st.column_config.TextColumn(width="medium"),
    "Recent typical weekly spend": st.column_config.TextColumn(width="small"),
    "Cost per next customer": st.column_config.TextColumn(width="small"),
    "Cost likely range (95%)": st.column_config.TextColumn(width="medium"),
    "Return on next dollar": st.column_config.TextColumn(width="small"),
    "Return likely range (95%)": st.column_config.TextColumn(width="medium"),
}

tested_set = set(CHANNELS_LIFT_TESTED)
tested = active[active["channel"].isin(tested_set)]
untested = active[~active["channel"].isin(tested_set)]

st.caption(
    "Rank is across all 19 channels. Untested channels can sort high purely on a wide, "
    "prior-driven estimate, so they are listed in a separate tier below the measured channels "
    "rather than mixed in. Because of that, the measured list does not start at rank 1."
)

# ── Measured tier (lift-tested incrementality) ───────────────────────────────
st.markdown("### Measured channels (lift-tested incrementality)")
st.caption(
    "These seven channels were validated with an incrementality experiment, so their position "
    "is the most trustworthy part of this exhibit. Lead your decisions with this tier."
)
st.dataframe(
    _combined_view(tested), use_container_width=True, hide_index=True, column_config=col_cfg,
)
st.caption(
    "**Two measured channels read lower here than their experiments suggest: TikTok iOS and "
    "Meta Web.** Both are already at high recent weekly spend, so the next dollar is expensive "
    "even though each has been efficient historically. This is a read on the cost of the next "
    "dollar at today's spend, not a verdict on the channel's overall efficiency."
)

# ── Directional tier (no incrementality test) ────────────────────────────────
st.markdown("### Directional only (no incrementality test)")
st.caption(
    "These channels were not lift-tested, so their position comes from the model alone and "
    "carries wide uncertainty (the same LOW-confidence flag shown on the Decisioning Summary "
    "page). A high rank here can come purely from a wide, prior-driven estimate, so treat this "
    "tier as directional and lean on the measured channels above."
)
st.dataframe(
    _combined_view(untested), use_container_width=True, hide_index=True, column_config=col_cfg,
)

st.markdown("---")
st.caption(
    "**How to use this:** the relative order tells you where added budget tends to work hardest "
    "and where it is closer to running out of room. Channels with a wide likely range are measured "
    "with less certainty (often lower-spend or untested channels), so lean on the well-measured "
    "channels when the ranges are tight. The exact dollar levels will move as the model is refined; "
    "the ordering is what to plan against."
)

if excluded:
    st.caption(
        "Not shown (no spend in the last 26 weeks, so there is no recent level to measure): "
        + ", ".join(excluded) + "."
    )

# ── CSV export ───────────────────────────────────────────────────────────────
export = active.sort_values("rank_icac")[[
    "channel", "recent_median_spend",
    "marg_icac_point", "icac_lo95", "icac_hi95", "rank_icac",
    "marg_iroas_point", "iroas_lo95", "iroas_hi95", "rank_iroas",
]]
st.download_button(
    label="📥 Download ranking as CSV",
    data=export.to_csv(index=False).encode("utf-8"),
    file_name=f"kikoff_mmm_channel_ranking_{CANONICAL_VERSION}.csv",
    mime="text/csv",
)
