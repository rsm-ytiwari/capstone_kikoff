import marimo

__generated_with = "0.23.3"
app = marimo.App()


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Exploratory Data Analysis: Kikoff MMM
    ## Quick Start

    **Note:** Run the setup cell below first to ensure correct file paths.
    """)
    return


@app.cell
def _():
    # SETUP CELL - Run this first
    import os
    from pathlib import Path

    # Ensure we're in the project root with access to data/
    current = Path.cwd()

    # Navigate to project root if needed
    if not (current / 'data').exists():
        # Try parent directory
        if (current.parent / 'data').exists():
            os.chdir(current.parent)
        else:
            # Try to find capstone_team
            for ancestor in current.parents:
                if 'capstone_team' in str(ancestor) and (ancestor / 'data').exists():
                    os.chdir(ancestor)
                    break

    print(f"Working directory: {Path.cwd()}")
    print(f"Data files available:")
    for f in sorted(Path.cwd().glob('data/*.csv')):
        print(f"  {f.name}")
    return


@app.cell
def _():
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    import seaborn as sns
    from scipy import stats
    import warnings

    warnings.filterwarnings('ignore')
    plt.style.use('seaborn-v0_8-darkgrid')
    sns.set_palette('husl')
    plt.rcParams['figure.figsize'] = (14, 6)

    print("Libraries loaded.")
    return (pd,)


@app.cell
def _(pd):
    # Load data
    spend_df = pd.read_csv('data/MMM_PLATFORM_CHANNEL_DAILY_SPEND_2026-04-07-1111.csv')
    ltv_df = pd.read_csv('data/MMM_DAILY_CONVENSIONS_LTV_2026-04-07-1304.csv')

    # Convert dates
    spend_df['DS'] = pd.to_datetime(spend_df['DS'])
    ltv_df['DS'] = pd.to_datetime(ltv_df['DS'])

    # Filter LTV to 2024+
    ltv_df = ltv_df[ltv_df['DS'] >= '2024-01-01'].copy()

    # Create combined daily dataset
    daily_df = spend_df.groupby('DS')['TOTAL_SPEND'].sum().reset_index()
    daily_df = daily_df.merge(ltv_df, on='DS', how='inner')

    print(f"Data loaded successfully!")
    print(f"  Spend: {spend_df.shape}")
    print(f"  LTV: {ltv_df.shape}")
    print(f"  Combined: {daily_df.shape}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---

    If the above cells run successfully, you can now run the full 02_eda.ipynb notebook.

    **If you get a FileNotFoundError:**

    1. Click the folder icon in Jupyter/IDE to navigate to `/Users/yashtiwari/MSBA/Quarters/Spring_2026/capstone_team/`
    2. Open the notebook from there
    3. Run the setup cell above (first cell in the notebook)

    The setup cell ensures the notebook can find the data files regardless of where it's opened from.
    """)
    return


if __name__ == "__main__":
    app.run()
