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


@st.cache_data(ttl=300)
def load_baseline(channel: str = "meta_web") -> dict:
    p = _CHART_DIR / f"{channel}_baseline.json"
    with open(p) as f:
        return json.load(f)


@st.cache_data(ttl=300)
def load_icac_time(channel: str = "meta_web") -> pd.DataFrame:
    df = pd.read_csv(_CHART_DIR / f"{channel}_icac_time.csv", parse_dates=["date"])
    return df


@st.cache_data(ttl=300)
def load_iroas_time(channel: str = "meta_web") -> pd.DataFrame:
    df = pd.read_csv(_CHART_DIR / f"{channel}_iroas_time.csv", parse_dates=["date"])
    return df


@st.cache_data(ttl=300)
def load_ltv_time(channel: str = "meta_web") -> pd.DataFrame:
    df = pd.read_csv(_CHART_DIR / f"{channel}_ltv_time.csv", parse_dates=["date"])
    return df


@st.cache_data(ttl=300)
def load_icac_saturation(channel: str = "meta_web") -> pd.DataFrame:
    return pd.read_csv(_CHART_DIR / f"{channel}_icac_saturation.csv")


@st.cache_data(ttl=300)
def load_iroas_saturation(channel: str = "meta_web") -> pd.DataFrame:
    return pd.read_csv(_CHART_DIR / f"{channel}_iroas_saturation.csv")


@st.cache_data(ttl=300)
def load_spend_weekly(channel: str = "meta_web") -> pd.DataFrame:
    df = pd.read_csv(_CHART_DIR / f"{channel}_spend_weekly.csv", parse_dates=["date"])
    return df


@st.cache_data(ttl=300)
def load_convergence() -> dict:
    p = _METRIC_DIR / "ltv_convergence.json"
    with open(p) as f:
        return json.load(f)
