"""
charts.py — Plotly figure builders for the Kikoff MMM dashboard.

Each function accepts pre-loaded DataFrames/dicts and returns a go.Figure.
Style conventions match Northbeam's dashboard aesthetic.

All builders are channel-parametric: pass `channel="meta_web"`, `"ctv"`, etc.
Titles + axis labels are built from CHANNEL_DISPLAY (imported below).
Spend column defaults are derived as f"{channel}_spend".
"""
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from app.data_loader import CHANNEL_DISPLAY

# ── Style constants ─────────────────────────────────────────────────────────
BLUE        = "#2563EB"
BLUE_FILL   = "rgba(37,99,235,0.15)"
ORANGE      = "#EA580C"
ORANGE_FILL = "rgba(234,88,12,0.15)"
GRAY        = "#6B7280"
GRAY_LIGHT  = "#E5E7EB"

LAYOUT_BASE = dict(
    plot_bgcolor="white",
    paper_bgcolor="white",
    font=dict(family="Arial", size=12, color="#111827"),
    margin=dict(l=60, r=60, t=60, b=50),
    legend=dict(bgcolor="rgba(255,255,255,0.9)", bordercolor=GRAY_LIGHT, borderwidth=1),
    xaxis=dict(gridcolor=GRAY_LIGHT, linecolor=GRAY_LIGHT),
    yaxis=dict(gridcolor=GRAY_LIGHT, linecolor=GRAY_LIGHT),
)

CONFIG = dict(displayModeBar=True, toImageButtonOptions=dict(format="png", scale=2))


def _dollar_fmt(x: float) -> str:
    if abs(x) >= 1_000_000:
        return f"${x/1_000_000:.1f}M"
    if abs(x) >= 1_000:
        return f"${x/1_000:.0f}K"
    return f"${x:.0f}"


# ── Chart 1: Baseline iCAC ──────────────────────────────────────────────────
def fig_icac_baseline(baseline: dict, channel: str = "meta_web") -> go.Figure:
    """Baseline iCAC bar + HDI whiskers.

    Headline (`baseline["icac_mean"]`) is:
      - windowed iCAC for lift-tested channels (D023, post-Fix-A)
      - aggregate iCAC for untested channels
    HDI is computed on the matching basis (windowed for tested, full-history
    for untested) by scripts/10_channel_charts.py.
    """
    point_v   = baseline["icac_mean"]
    lo, hi    = baseline["icac_hdi_lo"], baseline["icac_hdi_hi"]
    is_tested = baseline.get("is_lift_tested", False)
    display   = CHANNEL_DISPLAY.get(channel, channel)
    benchmark = baseline.get("windowed_iCAC_truth") if is_tested else None
    benchmark_label = "Truth" if is_tested else None
    # Meta-Web-only Northbeam reference, preserved from prior dashboard.
    northbeam = baseline.get("northbeam_icac_ref")

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=[point_v], y=[display],
        orientation="h",
        marker_color=BLUE,
        name=f"Median: {_dollar_fmt(point_v)}",
        hovertemplate=(
            f"Posterior median iCAC: {_dollar_fmt(point_v)}<br>"
            f"94% HDI: [{_dollar_fmt(lo)}, {_dollar_fmt(hi)}]<extra></extra>"
        ),
    ))
    fig.add_shape(type="line", x0=lo, x1=lo, y0=-0.4, y1=0.4,
                  line=dict(color=GRAY, width=2))
    fig.add_shape(type="line", x0=hi, x1=hi, y0=-0.4, y1=0.4,
                  line=dict(color=GRAY, width=2))
    fig.add_shape(type="line", x0=lo, x1=hi, y0=0, y1=0,
                  line=dict(color=GRAY, width=2))
    if benchmark is not None and np.isfinite(benchmark):
        fig.add_vline(x=benchmark, line_dash="dash", line_color=ORANGE,
                      annotation_text=f"{benchmark_label} ${benchmark:.0f}",
                      annotation_position="bottom left")
    if northbeam is not None and np.isfinite(northbeam):
        fig.add_vline(x=northbeam, line_dash="dot", line_color=GRAY,
                      annotation_text=f"Northbeam ${northbeam:.0f}",
                      annotation_position="top right")

    candidates = [point_v, hi]
    if benchmark is not None and np.isfinite(benchmark): candidates.append(benchmark)
    if northbeam is not None and np.isfinite(northbeam): candidates.append(northbeam)
    x_max = max(candidates) * 1.20

    sub = ("windowed posterior median during lift-test window"
           if is_tested else "full-history aggregate posterior")
    fig.update_layout(
        **LAYOUT_BASE,
        title=dict(text=f"Baseline iCAC — {display}<br><sub>Model 2 · y=LTV_3YEAR · {sub} + 94% HDI</sub>",
                   font=dict(size=14)),
        xaxis_title="iCAC (USD per implied conversion)",
        height=280,
        showlegend=True,
    )
    fig.update_xaxes(tickprefix="$", tickformat=",.0f", range=[0, x_max])
    return fig


# ── Chart 2: Baseline iROAS ─────────────────────────────────────────────────
def fig_iroas_baseline(baseline: dict, channel: str = "meta_web") -> go.Figure:
    mean_v    = baseline["iroas_mean"]
    lo, hi    = baseline["iroas_hdi_lo"], baseline["iroas_hdi_hi"]
    northbeam = baseline.get("northbeam_iroas_ref")  # Meta-Web-only
    pct_below = baseline["iroas_below_breakeven_pct"]
    display   = CHANNEL_DISPLAY.get(channel, channel)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=[mean_v], y=[display],
        orientation="h",
        marker_color=ORANGE,
        name=f"Mean: {mean_v:.3f}x",
        hovertemplate=(
            f"iROAS: {mean_v:.3f}x<br>94% HDI: [{lo:.3f}x, {hi:.3f}x]<br>"
            f"{pct_below:.0f}% of posterior below break-even<extra></extra>"
        ),
    ))
    fig.add_shape(type="line", x0=lo, x1=lo, y0=-0.4, y1=0.4,
                  line=dict(color=GRAY, width=2))
    fig.add_shape(type="line", x0=hi, x1=hi, y0=-0.4, y1=0.4,
                  line=dict(color=GRAY, width=2))
    fig.add_shape(type="line", x0=lo, x1=hi, y0=0, y1=0,
                  line=dict(color=GRAY, width=2))
    fig.add_vline(x=1.0, line_dash="dash", line_color=GRAY,
                  annotation_text="Break-even (1.0x)", annotation_position="top right")
    if northbeam is not None and np.isfinite(northbeam):
        fig.add_vline(x=northbeam, line_dash="dot", line_color=BLUE,
                      annotation_text=f"Northbeam {northbeam:.2f}x",
                      annotation_position="top left")

    candidates = [mean_v, hi, 1.0]
    if northbeam is not None and np.isfinite(northbeam): candidates.append(northbeam)
    x_max = max(candidates) * 1.15
    fig.update_layout(
        **LAYOUT_BASE,
        title=dict(text=f"Baseline iROAS — {display}<br><sub>Model 2 · y=LTV_3YEAR · posterior mean + 94% HDI</sub>",
                   font=dict(size=14)),
        xaxis_title="iROAS (LTV dollars per dollar spent)",
        height=280,
        showlegend=True,
    )
    fig.update_xaxes(range=[0, x_max])
    return fig


# ── Chart 3: iCAC over time ─────────────────────────────────────────────────
def fig_icac_time(df: pd.DataFrame, benchmark: float | None,
                  spend_df: pd.DataFrame | None = None,
                  spend_col: str | None = None,
                  channel: str = "meta_web") -> go.Figure:
    spend_col = spend_col or f"{channel}_spend"
    display = CHANNEL_DISPLAY.get(channel, channel)

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(
        x=df["date"], y=df["hi95"], mode="lines",
        line=dict(width=0), showlegend=False, hoverinfo="skip",
    ), secondary_y=False)
    fig.add_trace(go.Scatter(
        x=df["date"], y=df["lo95"], mode="lines",
        line=dict(width=0), fill="tonexty", fillcolor=BLUE_FILL,
        name="95% CI", hoverinfo="skip",
    ), secondary_y=False)
    fig.add_trace(go.Scatter(
        x=df["date"], y=df["mean"], mode="lines",
        line=dict(color=BLUE, width=2),
        name="Posterior mean iCAC",
        hovertemplate="Week: %{x|%Y-%m-%d}<br>iCAC: $%{y:,.0f}<extra></extra>",
    ), secondary_y=False)
    if benchmark is not None and np.isfinite(benchmark):
        fig.add_hline(y=benchmark, line_dash="dash", line_color=ORANGE,
                      annotation_text=f"Lift-test truth ${benchmark:.0f}",
                      annotation_position="bottom right")

    if spend_df is not None and not spend_df.empty and spend_col in spend_df.columns:
        fig.add_trace(go.Scatter(
            x=spend_df["date"], y=spend_df[spend_col], mode="lines",
            line=dict(color=GRAY, width=1.5, dash="dash"),
            name="Weekly spend (right)",
            hovertemplate="Week: %{x|%Y-%m-%d}<br>Spend: $%{y:,.0f}<extra></extra>",
        ), secondary_y=True)

    fig.update_layout(
        **LAYOUT_BASE,
        title=dict(text=f"iCAC Over Time — {display}<br><sub>Weekly posterior mean + 95% CI · spend overlay</sub>",
                   font=dict(size=14)),
        xaxis_title="Week",
        height=380,
    )
    fig.update_yaxes(title_text="iCAC (USD per implied conversion)", tickprefix="$",
                     tickformat=",.0f", secondary_y=False)
    fig.update_yaxes(title_text="Weekly Spend ($)", tickprefix="$",
                     tickformat=",.0f", secondary_y=True, showgrid=False)
    return fig


# ── Chart 4: iROAS over time ────────────────────────────────────────────────
def fig_iroas_time(df: pd.DataFrame,
                   spend_df: pd.DataFrame | None = None,
                   spend_col: str | None = None,
                   channel: str = "meta_web") -> go.Figure:
    spend_col = spend_col or f"{channel}_spend"
    display = CHANNEL_DISPLAY.get(channel, channel)

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(
        x=df["date"], y=df["hi95"], mode="lines",
        line=dict(width=0), showlegend=False, hoverinfo="skip",
    ), secondary_y=False)
    fig.add_trace(go.Scatter(
        x=df["date"], y=df["lo95"], mode="lines",
        line=dict(width=0), fill="tonexty", fillcolor=ORANGE_FILL,
        name="95% CI", hoverinfo="skip",
    ), secondary_y=False)
    fig.add_trace(go.Scatter(
        x=df["date"], y=df["mean"], mode="lines",
        line=dict(color=ORANGE, width=2),
        name="Posterior mean iROAS",
        hovertemplate="Week: %{x|%Y-%m-%d}<br>iROAS: %{y:.3f}x<extra></extra>",
    ), secondary_y=False)
    fig.add_hline(y=1.0, line_dash="dash", line_color=GRAY,
                  annotation_text="Break-even (1.0x)", annotation_position="bottom right")

    if spend_df is not None and not spend_df.empty and spend_col in spend_df.columns:
        fig.add_trace(go.Scatter(
            x=spend_df["date"], y=spend_df[spend_col], mode="lines",
            line=dict(color=GRAY, width=1.5, dash="dash"),
            name="Weekly spend (right)",
            hovertemplate="Week: %{x|%Y-%m-%d}<br>Spend: $%{y:,.0f}<extra></extra>",
        ), secondary_y=True)

    fig.update_layout(
        **LAYOUT_BASE,
        title=dict(text=f"iROAS Over Time — {display}<br><sub>Weekly posterior mean + 95% CI · spend overlay</sub>",
                   font=dict(size=14)),
        xaxis_title="Week",
        height=380,
    )
    fig.update_yaxes(title_text="iROAS (LTV dollars per dollar spent)", secondary_y=False)
    fig.update_yaxes(title_text="Weekly Spend ($)", tickprefix="$",
                     tickformat=",.0f", secondary_y=True, showgrid=False)
    return fig


# ── Chart 5: LTV over time ──────────────────────────────────────────────────
def fig_ltv_time(df: pd.DataFrame, channel: str = "meta_web") -> go.Figure:
    """Plot weekly LTV_3YEAR attribution in $K (avoids cramped $0.10M ticks)."""
    display = CHANNEL_DISPLAY.get(channel, channel)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["date"], y=df["hi95"] / 1_000, mode="lines",
        line=dict(width=0), showlegend=False, hoverinfo="skip",
    ))
    fig.add_trace(go.Scatter(
        x=df["date"], y=df["lo95"] / 1_000, mode="lines",
        line=dict(width=0), fill="tonexty", fillcolor=BLUE_FILL,
        name="95% CI", hoverinfo="skip",
    ))
    fig.add_trace(go.Scatter(
        x=df["date"], y=df["mean"] / 1_000, mode="lines",
        line=dict(color=BLUE, width=2),
        name="LTV contribution",
        hovertemplate="Week: %{x|%Y-%m-%d}<br>LTV contrib: $%{y:,.0f}K<extra></extra>",
    ))
    fig.update_layout(
        **LAYOUT_BASE,
        title=dict(text=f"LTV Contribution Over Time — {display}<br><sub>Weekly LTV_3YEAR attributed to {display} (posterior mean + 95% CI)</sub>",
                   font=dict(size=14)),
        xaxis_title="Week",
        yaxis_title="LTV_3YEAR Contribution ($K / week)",
        height=380,
    )
    fig.update_yaxes(tickprefix="$", ticksuffix="K", tickformat=",.0f")
    return fig


# ── Chart 6: iCAC Saturation Curve ─────────────────────────────────────────
def _spend_histogram(spend_df: pd.DataFrame | None, spend_col: str, x_max: float):
    """Return (centers, widths, counts) for a 10-bin histogram of observed weekly spend."""
    if spend_df is None or spend_df.empty or spend_col not in spend_df.columns:
        return None, None, None
    weekly = spend_df.loc[spend_df[spend_col] > 0, spend_col].to_numpy()
    if len(weekly) == 0:
        return None, None, None
    edges = np.linspace(0, x_max, 11)
    counts, _ = np.histogram(weekly, bins=edges)
    centers = (edges[:-1] + edges[1:]) / 2
    widths = np.diff(edges)
    return centers, widths, counts


def fig_icac_saturation(df: pd.DataFrame, median_spend: float,
                        benchmark: float | None = None,
                        spend_df: pd.DataFrame | None = None,
                        spend_col: str | None = None,
                        channel: str = "meta_web") -> go.Figure:
    spend_col = spend_col or f"{channel}_spend"
    display = CHANNEL_DISPLAY.get(channel, channel)
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Crop to within ~15% above observed-spend max so we don't show deep extrapolation
    observed_max = float(spend_df[spend_col].max()) if (spend_df is not None and not spend_df.empty) else float(df["spend"].max())
    x_cap = observed_max * 1.15

    valid = df["icac_mean"].notna() & (df["spend"] <= x_cap)
    x  = df.loc[valid, "spend"]
    m  = df.loc[valid, "icac_mean"]
    lo = df.loc[valid, "icac_lo95"]
    hi = df.loc[valid, "icac_hi95"]
    ltv_k = df.loc[valid, "ltv_mean"] / 1_000  # use $K not $M

    centers, widths, counts = _spend_histogram(spend_df, spend_col, x_max=float(x.max()))
    if counts is not None:
        fig.add_trace(go.Bar(
            x=centers, y=counts, width=widths,
            marker=dict(color="rgba(107,114,128,0.25)", line=dict(width=0)),
            name="Observed weeks (right)",
            yaxis="y3",
            hovertemplate="Spend bin center: $%{x:,.0f}<br>Weeks: %{y}<extra></extra>",
        ))

    fig.add_trace(go.Scatter(
        x=x, y=hi, mode="lines", line=dict(width=0),
        showlegend=False, hoverinfo="skip",
    ), secondary_y=False)
    fig.add_trace(go.Scatter(
        x=x, y=lo, mode="lines", line=dict(width=0),
        fill="tonexty", fillcolor=BLUE_FILL, name="95% CI", hoverinfo="skip",
    ), secondary_y=False)
    fig.add_trace(go.Scatter(
        x=x, y=m, mode="lines", line=dict(color=BLUE, width=2.5),
        name="Posterior median iCAC",
        hovertemplate=(
            "Spend: $%{x:,.0f}<br>"
            "iCAC: $%{y:,.0f}<br>"
            "<extra></extra>"
        ),
        customdata=ltv_k,
    ), secondary_y=False)
    fig.add_trace(go.Scatter(
        x=x, y=ltv_k, mode="lines",
        line=dict(color=GRAY, width=1.5, dash="dot"),
        name="Expected LTV ($K, right axis)",
        hovertemplate="LTV: $%{y:,.0f}K<extra></extra>",
    ), secondary_y=True)

    fig.add_vline(x=median_spend, line_dash="dashdot", line_color="black",
                  annotation_text=f"Median spend {_dollar_fmt(median_spend)}",
                  annotation_position="top left")
    # Mark where observed data ends — anything past this line is model extrapolation
    fig.add_vline(x=observed_max, line_dash="dot", line_color="rgba(107,114,128,0.6)",
                  annotation_text=f"Observed max {_dollar_fmt(observed_max)}",
                  annotation_position="bottom left")
    # NOTE: removed the horizontal "Lift test" line — the test was a single spend
    # point (~$4.5K weekly equivalent), not a benchmark at every spend level.

    fig.update_layout(
        **LAYOUT_BASE,
        title=dict(text=f"iCAC Saturation Curve — {display}<br><sub>Spend vs. marginal iCAC · histogram = observed weeks per spend bin · curve right of dashed line is extrapolation</sub>",
                   font=dict(size=14)),
        xaxis_title="Weekly Spend ($)",
        height=420,
        bargap=0.05,
    )
    if counts is not None:
        fig.update_layout(yaxis3=dict(
            title=dict(text="Observed spend (weeks)", font=dict(color="rgba(107,114,128,0.7)", size=11)),
            overlaying="y", side="right", position=0.96,
            range=[0, float(counts.max()) * 4],
            showgrid=False, anchor="free",
            tickfont=dict(color="rgba(107,114,128,0.7)", size=10),
        ))
    fig.update_xaxes(tickprefix="$", tickformat=",.0f", range=[0, x_cap])
    fig.update_yaxes(title_text="iCAC (USD per implied conversion)", tickprefix="$",
                     tickformat=",.0f", secondary_y=False, rangemode="tozero")
    fig.update_yaxes(title_text="Expected LTV ($K/week)",
                     tickprefix="$", ticksuffix="K", tickformat=",.0f", secondary_y=True)
    return fig


# ── Chart 7: iROAS Saturation Curve ────────────────────────────────────────
def fig_iroas_saturation(df: pd.DataFrame, median_spend: float,
                         spend_df: pd.DataFrame | None = None,
                         spend_col: str | None = None,
                         channel: str = "meta_web") -> go.Figure:
    spend_col = spend_col or f"{channel}_spend"
    display = CHANNEL_DISPLAY.get(channel, channel)
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    observed_max = float(spend_df[spend_col].max()) if (spend_df is not None and not spend_df.empty) else float(df["spend"].max())
    x_cap = observed_max * 1.15

    valid = df["iroas_mean"].notna() & (df["spend"] <= x_cap)
    x   = df.loc[valid, "spend"]
    m   = df.loc[valid, "iroas_mean"]
    lo  = df.loc[valid, "iroas_lo95"]
    hi  = df.loc[valid, "iroas_hi95"]
    ltv_k = df.loc[valid, "ltv_mean"] / 1_000

    centers, widths, counts = _spend_histogram(spend_df, spend_col, x_max=float(x.max()))
    if counts is not None:
        fig.add_trace(go.Bar(
            x=centers, y=counts, width=widths,
            marker=dict(color="rgba(107,114,128,0.25)", line=dict(width=0)),
            name="Observed weeks (right)",
            yaxis="y3",
            hovertemplate="Spend bin center: $%{x:,.0f}<br>Weeks: %{y}<extra></extra>",
        ))

    fig.add_trace(go.Scatter(
        x=x, y=hi, mode="lines", line=dict(width=0),
        showlegend=False, hoverinfo="skip",
    ), secondary_y=False)
    fig.add_trace(go.Scatter(
        x=x, y=lo, mode="lines", line=dict(width=0),
        fill="tonexty", fillcolor=ORANGE_FILL, name="95% CI", hoverinfo="skip",
    ), secondary_y=False)
    fig.add_trace(go.Scatter(
        x=x, y=m, mode="lines", line=dict(color=ORANGE, width=2.5),
        name="Posterior median iROAS",
        hovertemplate=(
            "Spend: $%{x:,.0f}<br>"
            "iROAS: %{y:.3f}x<br>"
            "Expected LTV: $%{customdata:,.0f}K<br>"
            "<extra></extra>"
        ),
        customdata=ltv_k,
    ), secondary_y=False)
    fig.add_trace(go.Scatter(
        x=x, y=ltv_k, mode="lines",
        line=dict(color=GRAY, width=1.5, dash="dot"),
        name="Expected LTV ($K, right axis)",
        hovertemplate="LTV: $%{y:,.0f}K<extra></extra>",
    ), secondary_y=True)

    fig.add_vline(x=median_spend, line_dash="dashdot", line_color="black",
                  annotation_text=f"Median spend {_dollar_fmt(median_spend)}",
                  annotation_position="top left")
    fig.add_vline(x=observed_max, line_dash="dot", line_color="rgba(107,114,128,0.6)",
                  annotation_text=f"Observed max {_dollar_fmt(observed_max)}",
                  annotation_position="bottom left")
    fig.add_hline(y=1.0, line_dash="dash", line_color=GRAY,
                  annotation_text="Break-even (1.0x)", annotation_position="top right")

    fig.update_layout(
        **LAYOUT_BASE,
        title=dict(text=f"iROAS Saturation Curve — {display}<br><sub>Spend vs. marginal iROAS · histogram = observed weeks per spend bin · curve right of dashed line is extrapolation</sub>",
                   font=dict(size=14)),
        xaxis_title="Weekly Spend ($)",
        height=420,
        bargap=0.05,
    )
    if counts is not None:
        fig.update_layout(yaxis3=dict(
            title=dict(text="Observed spend (weeks)", font=dict(color="rgba(107,114,128,0.7)", size=11)),
            overlaying="y", side="right", position=0.96,
            range=[0, float(counts.max()) * 4],
            showgrid=False, anchor="free",
            tickfont=dict(color="rgba(107,114,128,0.7)", size=10),
        ))
    fig.update_xaxes(tickprefix="$", tickformat=",.0f", range=[0, x_cap])
    fig.update_yaxes(title_text="iROAS (LTV dollars per dollar spent)", rangemode="tozero", secondary_y=False)
    fig.update_yaxes(title_text="Expected LTV ($K/week)",
                     tickprefix="$", ticksuffix="K", tickformat=",.0f", secondary_y=True)
    return fig


# ── Chart 8: Spend Distribution ─────────────────────────────────────────────
def fig_spend_dist(df: pd.DataFrame,
                   channel_col: str | None = None,
                   channel: str = "meta_web") -> go.Figure:
    channel_col = channel_col or f"{channel}_spend"
    display = CHANNEL_DISPLAY.get(channel, channel)
    spend_vals = df.loc[df[channel_col] > 0, channel_col].values
    if len(spend_vals) == 0:
        fig = go.Figure()
        fig.update_layout(
            **LAYOUT_BASE,
            title=dict(text=f"Weekly Spend Distribution — {display}<br><sub>No nonzero spend weeks</sub>",
                       font=dict(size=14)),
            height=350,
        )
        return fig
    median_v = float(np.median(spend_vals))

    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=spend_vals,
        nbinsx=20,
        marker_color=BLUE,
        opacity=0.85,
        name="Weekly spend",
        hovertemplate="Spend range: $%{x:,.0f}<br>Weeks: %{y}<extra></extra>",
    ))
    fig.add_vline(x=median_v, line_dash="dash", line_color=ORANGE,
                  annotation_text=f"Median {_dollar_fmt(median_v)}",
                  annotation_position="top right")

    fig.update_layout(
        **LAYOUT_BASE,
        title=dict(text=f"Weekly Spend Distribution — {display}",
                   font=dict(size=14)),
        xaxis_title="Weekly Spend ($)",
        yaxis_title="Number of Weeks",
        height=350,
        showlegend=False,
    )
    fig.update_xaxes(tickprefix="$", tickformat=",.0f")
    return fig
