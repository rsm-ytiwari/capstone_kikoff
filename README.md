# Kikoff Marketing Mix Model — MSBA Capstone

## Overview

Our team is building a Bayesian Marketing Mix Model (MMM) for Kikoff, a credit-building and financial wellness fintech company. The model estimates the incremental impact of each marketing channel on customer acquisition, identifies diminishing returns, and recommends budget allocations across seasonal scenarios.

## Project Scope

- **Client:** Kikoff (Sponsor: Abheek Sinha)
- **Timeline:** Mid-March to Mid-June 2026
- **Deliverables:** Channel contribution estimates, saturation curves, seasonal budget scenarios, budget optimization recommendations
- **Approach:** Bayesian MMM calibrated with incrementality test results

## Data

Our dataset includes:
- **Spend data:** Daily channel-level marketing spend (Jan 2024 – Apr 2026)
- **Outcome data:** Daily conversions and 1-year LTV predictions (Jan 2023 – Apr 2026)
- **Incrementality tests:** 4 lift studies across TikTok, Meta, and CTV channels
- **Channels:** ~13 marketing channels including Meta, TikTok, Apple, CTV, Linear TV, Influencers, and others

Data files are not stored in this repository. Contact the team for access.

## Repository Structure

```
notebooks/          Analysis notebooks (naming: P[phase]_[seq]_[topic].py — Marimo)
meetings/refined/   Structured meeting notes and extractions
deliverables/       Presentation slides, reports, and exports
project_brief.md    Original project scope document
requirements.txt    Python dependencies
```

## Notebooks

| Notebook | Description |
|----------|-------------|
| P1_01_data_audit.py | Initial data quality audit — completeness, nulls, outliers |
| P1_02_eda_CURRENT.py | Exploratory data analysis — spend patterns, channel distributions, time series |
| P1_03_others_trend_and_mapping.py | Others/Idle spend trend and channel mapping analysis |
| P2_01_pymc_marketing_setup_CURRENT.py | Phase 2 model build — PyMC-Marketing MMM, ICAC/ROAS POC |

## How to Contribute

1. Create a feature branch for your work (e.g., `eda/channel-analysis`)
2. Work in the `notebooks/` directory using the naming convention `P[phase]_[seq]_[topic].py`
   (Marimo notebooks — pure Python, clean git diffs)
3. Open a PR to main when your analysis reaches a milestone
4. Run `marimo check <file.py>` before committing to validate the notebook

## Team

MSBA Capstone Team — UC San Diego Rady School of Management, Spring 2026
