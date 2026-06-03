"""
4_Channel_Ranking.py — channel rank-ordering by next-dollar cost per customer
and next-dollar return (LOCKED Meeting-8 deliverable).

Reads outputs/P2_09_ranking/metrics/channel_ranking.csv (scripts/24). The ORDER
is the signal; dollar magnitudes carry a known upward bias and tighten in a later
version. No outside-source comparison shown here.
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
    page_icon="📊",
    layout="wide",
)

st.markdown("# Channel Ranking: Where the Next Dollar Works Hardest")
st.caption(
    "Channels ranked by how hard the next dollar works, measured at each channel's recent typical "
    "weekly spend (the median of its last 26 active weeks). Each row shows the same result two ways, "
    "not two separate checks: the cost of the next customer (lower is better) and the return on the "
    "next dollar (higher is better). "
    "**Read the order, not the exact dollars.** The order is the durable signal; the dollar amounts "
    "run roughly 1.5 to 1.6 times high and will tighten in a later version. All figures come from the "
    "revenue (LTV) model."
)

df = load_channel_ranking()
df = df.copy()
df["display"] = df["channel"].map(lambda c: CHANNEL_DISPLAY.get(c, c))

active = df[df["rank_icac"].notna()].copy()
excluded = df[df["rank_icac"].isna()]["display"].tolist()

tested_set = set(CHANNELS_LIFT_TESTED)
tested = active[active["channel"].isin(tested_set)]
untested = active[~active["channel"].isin(tested_set)]


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


# ── Combined view (cost and return are one reciprocal number, same order) ─────
def _combined_view(sub: pd.DataFrame, with_rank: bool) -> pd.DataFrame:
    sub = sub.sort_values("marg_icac_point").reset_index(drop=True)
    cols: dict = {}
    if with_rank:
        cols["Rank"] = pd.Series(range(1, len(sub) + 1))
    cols["Channel"] = sub.apply(
        lambda r: f"🧪 {r['display']}" if r["channel"] in tested_set else r["display"],
        axis=1,
    )
    cols["Recent weekly spend"] = sub["recent_median_spend"].map(_spend)
    cols["Cost per next customer"] = sub["marg_icac_point"].map(_money)
    cols["Cost range (95%)"] = sub.apply(
        lambda r: _money_range(r["icac_lo95"], r["icac_hi95"]), axis=1
    )
    cols["Return per dollar"] = sub["marg_iroas_point"].map(_x)
    cols["Return range (95%)"] = sub.apply(
        lambda r: _x_range(r["iroas_lo95"], r["iroas_hi95"]), axis=1
    )
    return pd.DataFrame(cols)


col_cfg = {
    "Rank": st.column_config.NumberColumn(
        width="small", help="Rank within the lift-tested tier (1 = best)."),
    "Channel": st.column_config.TextColumn(width="medium"),
    "Recent weekly spend": st.column_config.TextColumn(
        width="medium", help="Typical weekly spend over the channel's last 26 active weeks."),
    "Cost per next customer": st.column_config.TextColumn(
        width="medium", help="Estimated cost to acquire one more customer at recent spend."),
    "Cost range (95%)": st.column_config.TextColumn(
        width="medium", help="95% likely range for the cost per next customer."),
    "Return per dollar": st.column_config.TextColumn(
        width="medium", help="Lifetime value returned for one more dollar spent, at recent spend."),
    "Return range (95%)": st.column_config.TextColumn(
        width="medium", help="95% likely range for the return per dollar."),
}

# ── View filter + plain-English callout ───────────────────────────────────────
view = st.segmented_control(
    "View",
    options=["All channels", "With incrementality test", "Without incrementality test"],
    default="All channels",
)
if view is None:  # segmented_control allows deselecting the active option
    view = "All channels"
show_measured = view in ("All channels", "With incrementality test")
show_directional = view in ("All channels", "Without incrementality test")

with st.popover("What do these views mean?"):
    st.markdown(
        "**Why two groups.** Some channels have a lift test on record and some do not. "
        "We keep them apart so the most trustworthy results are not mixed with the rest."
    )
    st.markdown(
        "**What a lift test is.** A lift test (also called an incrementality test) is an "
        "experiment that measures the customers a channel actually caused, by comparing "
        "similar audiences who did and did not see the ads."
    )
    st.markdown(
        "**Which order to trust.** The lift-tested order is the most trustworthy part of "
        "this page. Channels without a lift test are directional only and carry wide "
        "uncertainty, so use them as a hint rather than a verdict."
    )
    st.markdown(
        "**One caveat.** A lift test reflects one specific past experiment window, not a "
        "permanent guarantee. As spend and audiences shift, a test can go stale and may "
        "need refreshing, so the 🧪 marker means a test exists, not that it is true forever."
    )

if view == "All channels":
    st.caption(
        "The seven lift-tested channels are ranked 1 to 7. The remaining channels follow as a "
        "directional group with no rank, because without an experiment their order is too uncertain "
        "to trust."
    )

# ── Measured tier (lift-tested) ───────────────────────────────────────────────
if show_measured:
    st.markdown("### Measured channels (lift-tested)")
    st.caption(
        "These seven channels were each validated with a lift test, an experiment that measures the "
        "customers a channel actually caused. That makes their order the most trustworthy part of this "
        "page, so lead your decisions with this tier."
    )
    st.dataframe(
        _combined_view(tested, with_rank=True),
        use_container_width=True, hide_index=True, column_config=col_cfg,
    )
    st.caption("🧪 = this channel has a lift test on record.")
    st.caption(
        "**One gap to pre-empt: TikTok iOS.** It sits near the bottom of this tier (about \\$305 for "
        "the next customer) even though its lift test came in around \\$109. TikTok iOS is at high "
        "recent weekly spend, so the next dollar costs far more than its tested average; the same effect "
        "pushes Meta Web lower. We are looking into this gap for the next version. Both readings describe "
        "the cost of the next dollar at today's spend, not the channel's overall efficiency."
    )

# ── Directional tier (not lift-tested) ────────────────────────────────────────
if show_directional:
    st.markdown("### Directional only (not lift-tested)")
    st.caption(
        "These channels were not lift-tested, so their position comes from the model alone and carries "
        "wide uncertainty (the same low-confidence note shown elsewhere in this dashboard). A high rank "
        "here can reflect a wide, uncertain estimate rather than measured evidence, so treat this group "
        "as directional and lean on the measured channels above."
    )
    st.dataframe(
        _combined_view(untested, with_rank=False),
        use_container_width=True, hide_index=True, column_config=col_cfg,
    )

st.markdown("---")
st.caption(
    "**How to use this:** the relative order shows where added budget tends to work hardest and "
    "where a channel is closer to running out of room. Where the likely range is wide, the estimate "
    "is less certain, so lean on the measured channels with tighter ranges."
)

if excluded:
    st.caption(
        "Not shown (no spend in the last 26 weeks, so there is no recent level to measure): "
        + ", ".join(excluded) + "."
    )


# ── CSV export (matches the on-page tiers: measured 1-7, directional unranked) ─
def _export_frame() -> pd.DataFrame:
    t = tested.sort_values("marg_icac_point").copy()
    t.insert(0, "rank", range(1, len(t) + 1))
    t["tier"] = "Measured (lift-tested)"
    u = untested.sort_values("marg_icac_point").copy()
    u["rank"] = pd.NA
    u["tier"] = "Directional (not lift-tested)"
    both = pd.concat([t, u], ignore_index=True)
    return both[[
        "tier", "rank", "display", "recent_median_spend",
        "marg_icac_point", "icac_lo95", "icac_hi95",
        "marg_iroas_point", "iroas_lo95", "iroas_hi95",
    ]].rename(columns={
        "display": "channel",
        "recent_median_spend": "recent_weekly_spend",
        "marg_icac_point": "cost_per_next_customer",
        "icac_lo95": "cost_lo95", "icac_hi95": "cost_hi95",
        "marg_iroas_point": "return_per_dollar",
        "iroas_lo95": "return_lo95", "iroas_hi95": "return_hi95",
    })


st.download_button(
    label="📥 Download ranking as CSV",
    data=_export_frame().to_csv(index=False).encode("utf-8"),
    file_name=f"kikoff_mmm_channel_ranking_{CANONICAL_VERSION}.csv",
    mime="text/csv",
)
