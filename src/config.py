from pathlib import Path

ROOT = Path(__file__).parent.parent
DATA_DIR = ROOT / "data"

# --- Data files (corrected files received 2026-04-27) ---
SPEND_FILE = DATA_DIR / "MMM_Updated_Spend.csv"
LTV_FILE = DATA_DIR / "MMM_UPDATED_LTV.csv"
INCREMENTALITY_FILE = DATA_DIR / "Kikoff_data_incrementality.csv"

# Legacy files (original 2026-04-07 versions — kept for reference)
SPEND_FILE_LEGACY = DATA_DIR / "MMM_PLATFORM_CHANNEL_DAILY_SPEND_2026-04-07-1111.csv"
LTV_FILE_LEGACY = DATA_DIR / "MMM_DAILY_CONVENSIONS_LTV_2026-04-07-1304.csv"

# --- Output paths (notebook-scoped) ---
OUT = ROOT / "outputs"
OUT_P1_EDA = OUT / "P1_02_eda"
OUT_P1_OTHERS = OUT / "P1_03_others"
OUT_P2_PYMC = OUT / "P2_01_pymc"      # legacy — broken ICAC run, kept as reference
OUT_P2_03 = OUT / "P2_03_mmm_meta_poc"  # active — Meta POC with lift test integration
OUT_P2_04 = OUT / "P2_04_full_channel"   # M3 — full-channel model, all channels, weekly rollup

# Create all output subdirs on import
for _d in [
    OUT_P1_EDA / "figures",
    OUT_P1_EDA / "tables",
    OUT_P1_EDA / "metrics",
    OUT_P1_OTHERS / "figures",
    OUT_P2_PYMC / "figures",
    OUT_P2_PYMC / "tables",
    OUT_P2_PYMC / "metrics",
    OUT_P2_PYMC / "traces",
    OUT_P2_03 / "figures",
    OUT_P2_03 / "tables",
    OUT_P2_03 / "metrics",
    OUT_P2_03 / "traces",
    OUT_P2_04 / "figures",
    OUT_P2_04 / "tables",
    OUT_P2_04 / "metrics",
    OUT_P2_04 / "traces",
]:
    _d.mkdir(parents=True, exist_ok=True)
