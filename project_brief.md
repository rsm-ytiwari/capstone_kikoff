# Kikoff <> Rady MSBA Capstone Project

## Organization Overview

**Organization Name:** Kikoff
**Project Sponsor Name:** Abheek Sinha
**Project Sponsor Email Address:** abheek.sinha@kikoff.com
**Project Sponsor Office Address:** 132 Hawthorne St. San Francisco, CA 94107
**Industry:** Fintech / Consumer Financial Services (Subscription-based)
**Primary Location(s):** Bay Area, United States
**Primary Products/Services:**
● Credit-building and financial wellness subscription products
● Mobile-first consumer financial services

## Current Situation

The organization invests materially across multiple marketing channels to drive
customer acquisition and subscription growth. While channel-level performance
metrics are available through platform reporting and internal attribution systems,
leadership lacks a **holistic, causal understanding of true incremental impact**
across channels.
Current challenges include:
● Heavy reliance on last-touch or platform-reported attribution
● Limited visibility into diminishing returns and channel saturation
● Difficulty optimizing budgets across peak vs. non-peak seasons
● Inability to reliably simulate alternative budget allocation scenarios
As marketing costs increase and growth efficiency becomes more critical, the
business needs a **robust Media Mix Model (MMM)** to support data-driven planning,
investment decisions, and executive discussions.


## Project Goals

The primary goal of this capstone project is to **design, build, and operationalize a
Media Mix Model that informs strategic marketing investment decisions**.
The project will balance academic rigor with practical business applicability, ensuring
outputs are both analytically sound and decision-ready.

## Business Outcomes

```
● Quantify the incremental impact of each marketing channel on key
business outcomes (e.g., conversions and revenue), separating true causal lift
from baseline demand.
● Estimate diminishing returns and saturation curves for each channel across:
○ Current spend levels
○ Historical spend ranges to identify under-invested and over-saturated
channels.
● Enable budget optimization and reallocation scenarios , allowing leadership
to evaluate tradeoffs across channels under fixed or flexible budget
constraints.
● Develop season-specific budget scenarios , enabling differentiated media
strategies across:
○ Tax season (March–April)
○ Holiday periods (Thanksgiving / Black Friday through Christmas & New
Year)
○ Non-peak, steady-state periods
● Identify and quantify seasonality effects on both baseline demand and paid
media effectiveness, distinguishing structural seasonality from
marketing-driven lift.
● Improve confidence in marketing ROI and long-term planning by providing
a transparent, repeatable modeling framework suitable for quarterly and
annual planning.
```

## Academic & Learning Outcomes

```
● Apply advanced time-series and regression-based modeling techniques ,
including:
○ Bayesian Media Mix Models
○ Trend and seasonality decomposition
○ Adstock and saturation transformations
● Incorporate causal inference into observational models by:
○ Applying incrementality-informed priors for selected channels
○ Leveraging historical incrementality or lift test results where available
○ Comparing model performance with and without causal priors
● Bridge descriptive, predictive, and prescriptive analytics in a real-world
business context:
○ Descriptive: historical performance and seasonality
○ Predictive: modeled response curves and forecasts
○ Prescriptive: budget optimization and allocation recommendations
● Translate complex analytical findings into executive-ready insights ,
focusing on clarity, limitations, and decision relevance rather than purely
technical outputs.
```
## Scope of Work Steps / Project Milestones

_(Project Timeline: Mid-March to Mid-June)_

### Phase 1: Business Understanding & Data Audit

```
● Align on business objectives, KPIs, and success metrics
● Define dependent variable(s) and modeling granularity
● Audit available datasets and data quality
● Identify seasonality patterns, structural breaks, and data gaps
```
### Phase 2: Data Preparation & Feature Engineering


```
● Aggregate data to an appropriate time granularity (e.g., weekly)
● Engineer channel + Tactics -level spend and exposure variables
● Create control variables (seasonality, holidays, macro trends)
● Apply adstock and saturation transformations
```
### Phase 3: Model Development (Bayesian MMM)

```
● Build baseline Bayesian MMM
● Incorporate incrementality priors for selected channels and time periods
● Evaluate model fit, stability, and interpretability
● Conduct sensitivity and robustness checks
```
### Phase 4: Scenario Planning & Optimization

```
● Simulate alternative budget allocation scenarios
● Evaluate marginal ROI , Marginal CPA and diminishing returns
● Develop season-specific optimization recommendations
● Identify practical investment guardrails
```
### Phase 5: Synthesis, Validation & Storytelling

```
● Translate model outputs into business insights
● Create visualizations for executive consumption
● Prepare final presentation and documentation
● Review findings with sponsor and refine recommendations
```
## Project Deliverables

```
● Fully documented Media Mix Model
● Channel-level incremental contribution estimates
● Saturation and response curves by channel
● Seasonal budget allocation scenarios
● Budget optimization recommendations
● Executive presentation deck/Notion Doc
● Technical appendix detailing methodology, assumptions, and limitations
● Robust, well-documented, and scalable codebase that enables reproducibility
of results and future model refreshes.
```

## Descriptive, Predictive, and Prescriptive

## Components

### Descriptive Analytics

```
● Historical spend, performance, and seasonality trends
● Baseline vs. marketing-driven demand decomposition
```
### Predictive Analytics

```
● Modeled response curves by channel
● Forecasted outcomes under alternative spend levels
```
### Prescriptive Analytics

```
● Budget optimization recommendations
● Channel scaling and pullback guidance
● Season-specific media strategies
```
## Available Data

**Nature & Time Period**
● Weekly channel and Tactics -level marketing spend (12–24 months)
● Weekly business outcomes (e.g., conversions, revenue/ltv)
● Control variables (holidays, seasonality indicators, macro trends)
● Historical incrementality test results for select channels (when available) to be
used as Priors
**Link to Analytics Components**
● Descriptive: trend and variance analysis
● Predictive: MMM coefficients and forecasts
● Prescriptive: optimization and scenario simulation

## Success Criteria / How the Client Will Use This


### Success Criteria

The project will be considered successful if it:
● Produces directionally stable and interpretable channel and Tactics(platform)
contribution estimates
● Clearly identifies channels/tactics with diminishing returns vs. scalable upside
● Enables credible budget reallocation discussions with leadership
● Differentiates seasonal vs. non-seasonal media strategies
● Is transparent, reproducible, and defensible in executive settings

### How the Client Will Use This

```
● Inform quarterly and annual marketing budget planning
● Support channel investment and scaling decisions
● Provide a benchmark to triangulate against attribution and incrementality
tests
● Enable scenario-based discussions during peak seasons (Tax, Holidays)
● Serve as a foundation for future measurement maturity (MMM refreshes,
experimentation roadmap)
```
