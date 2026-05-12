"""
data_loader.py — Load pre-computed chart data for the Kikoff MMM dashboard.

Reads only outputs/P2_04_full_channel/charts/ and metrics/ — no raw data,
no trace files. All files here are committed to the repo and available on
Streamlit Community Cloud.
"""
import json
from pathlib import Path

import pandas as pd
import streamlit as st

_REPO_ROOT = Path(__file__).resolve().parent.parent
_CHART_DIR  = _REPO_ROOT / "outputs" / "P2_04_full_channel" / "charts"
_METRIC_DIR = _REPO_ROOT / "outputs" / "P2_04_full_channel" / "metrics"

CHANNEL_DISPLAY = {
    "meta_web": "Meta Web (Facebook)",
}

CHANNELS_AVAILABLE   = list(CHANNEL_DISPLAY.keys())
CHANNELS_COMING_SOON = [
    "meta_ios", "meta_android",
    "tiktok_web", "tiktok_ios", "tiktok_android",
    "google_web", "google_ios", "google_android",
    "ctv", "linear_tv", "apple_search",
]


def _drop_partial_last_week(df: pd.DataFrame, spend_col: str, ref_spend_df: pd.DataFrame,
                            min_ratio: float = 0.5) -> pd.DataFrame:
    """Drop the trailing row if it is a partial week.

    A partial week is defined as the final row whose channel spend is < min_ratio
    of the median of all prior nonzero-spend weeks. Used to suppress data-cutoff
    artifacts (e.g. 2026-04-06 in the current pull has only 29% of typical spend).
    """
    if ref_spend_df.empty or df.empty:
        return df
    spend_series = ref_spend_df.loc[ref_spend_df[spend_col] > 0, spend_col]
    if spend_series.empty:
        return df
    median_spend = spend_series.iloc[:-1].median() if len(spend_series) > 1 else spend_series.median()
    last_spend = float(ref_spend_df[spend_col].iloc[-1])
    if last_spend < min_ratio * median_spend:
        return df.iloc[:-1].copy()
    return df


@st.cache_data(ttl=300)
def load_baseline(channel: str = "meta_web") -> dict:
    p = _CHART_DIR / f"{channel}_baseline.json"
    with open(p) as f:
        return json.load(f)


@st.cache_data(ttl=300)
def load_spend_weekly(channel: str = "meta_web", drop_partial_last: bool = True) -> pd.DataFrame:
    df = pd.read_csv(_CHART_DIR / f"{channel}_spend_weekly.csv", parse_dates=["date"])
    if drop_partial_last:
        df = _drop_partial_last_week(df, f"{channel}_spend", df)
    return df


@st.cache_data(ttl=300)
def load_icac_time(channel: str = "meta_web", drop_partial_last: bool = True) -> pd.DataFrame:
    df = pd.read_csv(_CHART_DIR / f"{channel}_icac_time.csv", parse_dates=["date"])
    if drop_partial_last:
        spend_df = pd.read_csv(_CHART_DIR / f"{channel}_spend_weekly.csv", parse_dates=["date"])
        df = _drop_partial_last_week(df, f"{channel}_spend", spend_df)
    return df


@st.cache_data(ttl=300)
def load_iroas_time(channel: str = "meta_web", drop_partial_last: bool = True) -> pd.DataFrame:
    df = pd.read_csv(_CHART_DIR / f"{channel}_iroas_time.csv", parse_dates=["date"])
    if drop_partial_last:
        spend_df = pd.read_csv(_CHART_DIR / f"{channel}_spend_weekly.csv", parse_dates=["date"])
        df = _drop_partial_last_week(df, f"{channel}_spend", spend_df)
    return df


@st.cache_data(ttl=300)
def load_ltv_time(channel: str = "meta_web", drop_partial_last: bool = True) -> pd.DataFrame:
    df = pd.read_csv(_CHART_DIR / f"{channel}_ltv_time.csv", parse_dates=["date"])
    if drop_partial_last:
        spend_df = pd.read_csv(_CHART_DIR / f"{channel}_spend_weekly.csv", parse_dates=["date"])
        df = _drop_partial_last_week(df, f"{channel}_spend", spend_df)
    return df


@st.cache_data(ttl=300)
def load_icac_saturation(channel: str = "meta_web") -> pd.DataFrame:
    return pd.read_csv(_CHART_DIR / f"{channel}_icac_saturation.csv")


@st.cache_data(ttl=300)
def load_iroas_saturation(channel: str = "meta_web") -> pd.DataFrame:
    return pd.read_csv(_CHART_DIR / f"{channel}_iroas_saturation.csv")


@st.cache_data(ttl=300)
def load_convergence() -> dict:
    p = _METRIC_DIR / "ltv_convergence.json"
    with open(p) as f:
        return json.load(f)
