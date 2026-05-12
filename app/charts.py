"""
charts.py — Plotly figure builders for the Kikoff MMM dashboard.

Each function accepts pre-loaded DataFrames/dicts and returns a go.Figure.
Style conventions match Northbeam's dashboard aesthetic.
"""
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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
def fig_icac_baseline(baseline: dict) -> go.Figure:
    mean_v    = baseline["icac_mean"]
    lo, hi    = baseline["icac_hdi_lo"], baseline["icac_hdi_hi"]
    benchmark = baseline["lift_test_benchmark"]
    northbeam = baseline["northbeam_icac_ref"]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=[mean_v], y=["Meta Web"],
        orientation="h",
        marker_color=BLUE,
        name=f"Mean: {_dollar_fmt(mean_v)}",
        hovertemplate=f"iCAC: {_dollar_fmt(mean_v)}<br>94% HDI: [{_dollar_fmt(lo)}, {_dollar_fmt(hi)}]<extra></extra>",
    ))
    fig.add_shape(type="line", x0=lo, x1=lo, y0=-0.4, y1=0.4,
                  line=dict(color=GRAY, width=2))
    fig.add_shape(type="line", x0=hi, x1=hi, y0=-0.4, y1=0.4,
                  line=dict(color=GRAY, width=2))
    fig.add_shape(type="line", x0=lo, x1=hi, y0=0, y1=0,
                  line=dict(color=GRAY, width=2))
    fig.add_vline(x=benchmark, line_dash="dash", line_color=ORANGE,
                  annotation_text=f"Lift test ${benchmark:.0f}", annotation_position="top right")
    fig.add_vline(x=northbeam, line_dash="dot", line_color=GRAY,
                  annotation_text=f"Northbeam ${northbeam:.0f}", annotation_position="top left")

    fig.update_layout(
        **LAYOUT_BASE,
        title=dict(text="Baseline iCAC — Meta Web<br><sub>Model 2: y = LTV_3YEAR | 94% HDI error bar</sub>",
                   font=dict(size=14)),
        xaxis_title="iCAC ($ per implied conversion)",
        height=280,
        showlegend=True,
    )
    fig.update_xaxes(tickprefix="$", tickformat=",.0f")
    return fig


# ── Chart 2: Baseline iROAS ─────────────────────────────────────────────────
def fig_iroas_baseline(baseline: dict) -> go.Figure:
    mean_v    = baseline["iroas_mean"]
    lo, hi    = baseline["iroas_hdi_lo"], baseline["iroas_hdi_hi"]
    northbeam = baseline["northbeam_iroas_ref"]
    pct_below = baseline["iroas_below_breakeven_pct"]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=[mean_v], y=["Meta Web"],
        orientation="h",
        marker_color=ORANGE,
        name=f"Mean: {mean_v:.3f}x",
        hovertemplate=f"iROAS: {mean_v:.3f}x<br>94% HDI: [{lo:.3f}x, {hi:.3f}x]<br>{pct_below:.0f}% of posterior below break-even<extra></extra>",
    ))
    fig.add_shape(type="line", x0=lo, x1=lo, y0=-0.4, y1=0.4,
                  line=dict(color=GRAY, width=2))
    fig.add_shape(type="line", x0=hi, x1=hi, y0=-0.4, y1=0.4,
                  line=dict(color=GRAY, width=2))
    fig.add_shape(type="line", x0=lo, x1=hi, y0=0, y1=0,
                  line=dict(color=GRAY, width=2))
    fig.add_vline(x=1.0, line_dash="dash", line_color=GRAY,
                  annotation_text="Break-even (1.0x)", annotation_position="top right")
    fig.add_vline(x=northbeam, line_dash="dot", line_color=BLUE,
                  annotation_text=f"Northbeam {northbeam:.2f}x", annotation_position="top left")

    fig.update_layout(
        **LAYOUT_BASE,
        title=dict(text="Baseline iROAS — Meta Web<br><sub>Model 2: y = LTV_3YEAR | 94% HDI error bar</sub>",
                   font=dict(size=14)),
        xaxis_title="iROAS (LTV $ per $ spent)",
        height=280,
        showlegend=True,
    )
    return fig


# ── Chart 3: iCAC over time ─────────────────────────────────────────────────
def fig_icac_time(df: pd.DataFrame, benchmark: float,
                  spend_df: pd.DataFrame | None = None,
                  spend_col: str = "meta_web_spend") -> go.Figure:
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
    fig.add_hline(y=benchmark, line_dash="dash", line_color=ORANGE,
                  annotation_text=f"Lift test ${benchmark:.0f}", annotation_position="bottom right")

    if spend_df is not None and not spend_df.empty and spend_col in spend_df.columns:
        fig.add_trace(go.Scatter(
            x=spend_df["date"], y=spend_df[spend_col], mode="lines",
            line=dict(color=GRAY, width=1.5, dash="dash"),
            name="Weekly spend (right)",
            hovertemplate="Week: %{x|%Y-%m-%d}<br>Spend: $%{y:,.0f}<extra></extra>",
        ), secondary_y=True)

    fig.update_layout(
        **LAYOUT_BASE,
        title=dict(text="iCAC Over Time — Meta Web<br><sub>Weekly posterior mean + 95% CI · spend overlay</sub>",
                   font=dict(size=14)),
        xaxis_title="Week",
        height=380,
    )
    fig.update_yaxes(title_text="iCAC ($ per conversion)", tickprefix="$",
                     tickformat=",.0f", secondary_y=False)
    fig.update_yaxes(title_text="Weekly Spend ($)", tickprefix="$",
                     tickformat=",.0f", secondary_y=True, showgrid=False)
    return fig


# ── Chart 4: iROAS over time ────────────────────────────────────────────────
def fig_iroas_time(df: pd.DataFrame,
                   spend_df: pd.DataFrame | None = None,
                   spend_col: str = "meta_web_spend") -> go.Figure:
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
        title=dict(text="iROAS Over Time — Meta Web<br><sub>Weekly posterior mean + 95% CI · spend overlay</sub>",
                   font=dict(size=14)),
        xaxis_title="Week",
        height=380,
    )
    fig.update_yaxes(title_text="iROAS (LTV $ per $ spent)", secondary_y=False)
    fig.update_yaxes(title_text="Weekly Spend ($)", tickprefix="$",
                     tickformat=",.0f", secondary_y=True, showgrid=False)
    return fig


# ── Chart 5: LTV over time ──────────────────────────────────────────────────
def fig_ltv_time(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["date"], y=df["hi95"] / 1e6, mode="lines",
        line=dict(width=0), showlegend=False, hoverinfo="skip",
    ))
    fig.add_trace(go.Scatter(
        x=df["date"], y=df["lo95"] / 1e6, mode="lines",
        line=dict(width=0), fill="tonexty", fillcolor=BLUE_FILL,
        name="95% CI", hoverinfo="skip",
    ))
    fig.add_trace(go.Scatter(
        x=df["date"], y=df["mean"] / 1e6, mode="lines",
        line=dict(color=BLUE, width=2),
        name="LTV contribution",
        hovertemplate="Week: %{x|%Y-%m-%d}<br>LTV contrib: $%{y:.2f}M<extra></extra>",
    ))
    fig.update_layout(
        **LAYOUT_BASE,
        title=dict(text="LTV Contribution Over Time — Meta Web<br><sub>Weekly LTV_3YEAR attributed to Meta Web (posterior mean + 95% CI)</sub>",
                   font=dict(size=14)),
        xaxis_title="Week",
        yaxis_title="LTV_3YEAR Contribution ($M / week)",
        height=380,
    )
    fig.update_yaxes(tickprefix="$", ticksuffix="M", tickformat=".2f")
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


def fig_icac_saturation(df: pd.DataFrame, median_spend: float, benchmark: float,
                        spend_df: pd.DataFrame | None = None,
                        spend_col: str = "meta_web_spend") -> go.Figure:
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    valid = df["icac_mean"].notna()
    x  = df.loc[valid, "spend"]
    m  = df.loc[valid, "icac_mean"]
    lo = df.loc[valid, "icac_lo95"]
    hi = df.loc[valid, "icac_hi95"]
    ltv = df.loc[valid, "ltv_mean"] / 1e6

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
        customdata=ltv,
    ), secondary_y=False)
    fig.add_trace(go.Scatter(
        x=x, y=ltv, mode="lines",
        line=dict(color=GRAY, width=1.5, dash="dot"),
        name="Expected LTV ($M, right axis)",
        hovertemplate="LTV: $%{y:.3f}M<extra></extra>",
    ), secondary_y=True)

    fig.add_vline(x=median_spend, line_dash="dashdot", line_color="black",
                  annotation_text=f"Median spend {_dollar_fmt(median_spend)}",
                  annotation_position="top right")
    fig.add_hline(y=benchmark, line_dash="dash", line_color=ORANGE,
                  annotation_text=f"Lift test {_dollar_fmt(benchmark)}", annotation_position="bottom right")

    fig.update_layout(
        **LAYOUT_BASE,
        title=dict(text="iCAC Saturation Curve — Meta Web<br><sub>Spend vs. marginal iCAC · histogram = observed weeks per spend bin</sub>",
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
    fig.update_xaxes(tickprefix="$", tickformat=",.0f")
    fig.update_yaxes(title_text="iCAC ($ per conversion)", tickprefix="$",
                     tickformat=",.0f", secondary_y=False, rangemode="tozero")
    fig.update_yaxes(title_text="Expected LTV ($M/week)",
                     tickprefix="$", ticksuffix="M", tickformat=".3f", secondary_y=True)
    return fig


# ── Chart 7: iROAS Saturation Curve ────────────────────────────────────────
def fig_iroas_saturation(df: pd.DataFrame, median_spend: float,
                         spend_df: pd.DataFrame | None = None,
                         spend_col: str = "meta_web_spend") -> go.Figure:
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    valid = df["iroas_mean"].notna()
    x   = df.loc[valid, "spend"]
    m   = df.loc[valid, "iroas_mean"]
    lo  = df.loc[valid, "iroas_lo95"]
    hi  = df.loc[valid, "iroas_hi95"]
    ltv = df.loc[valid, "ltv_mean"] / 1e6

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
            "Expected LTV: $%{customdata:.3f}M<br>"
            "<extra></extra>"
        ),
        customdata=ltv,
    ), secondary_y=False)
    fig.add_trace(go.Scatter(
        x=x, y=ltv, mode="lines",
        line=dict(color=GRAY, width=1.5, dash="dot"),
        name="Expected LTV ($M, right axis)",
        hovertemplate="LTV: $%{y:.3f}M<extra></extra>",
    ), secondary_y=True)

    fig.add_vline(x=median_spend, line_dash="dashdot", line_color="black",
                  annotation_text=f"Median spend {_dollar_fmt(median_spend)}",
                  annotation_position="top right")
    fig.add_hline(y=1.0, line_dash="dash", line_color=GRAY,
                  annotation_text="Break-even (1.0x)", annotation_position="top left")

    fig.update_layout(
        **LAYOUT_BASE,
        title=dict(text="iROAS Saturation Curve — Meta Web<br><sub>Spend vs. marginal iROAS · histogram = observed weeks per spend bin</sub>",
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
    fig.update_xaxes(tickprefix="$", tickformat=",.0f")
    fig.update_yaxes(title_text="iROAS (LTV $ per $ spent)", rangemode="tozero", secondary_y=False)
    fig.update_yaxes(title_text="Expected LTV ($M/week)",
                     tickprefix="$", ticksuffix="M", tickformat=".3f", secondary_y=True)
    return fig


# ── Chart 8: Spend Distribution ─────────────────────────────────────────────
def fig_spend_dist(df: pd.DataFrame, channel_col: str = "meta_web_spend") -> go.Figure:
    spend_vals = df.loc[df[channel_col] > 0, channel_col].values
    median_v   = float(np.median(spend_vals))

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
        title=dict(text="Weekly Spend Distribution — Meta Web",
                   font=dict(size=14)),
        xaxis_title="Weekly Spend ($)",
        yaxis_title="Number of Weeks",
        height=350,
        showlegend=False,
    )
    fig.update_xaxes(tickprefix="$", tickformat=",.0f")
    return fig
