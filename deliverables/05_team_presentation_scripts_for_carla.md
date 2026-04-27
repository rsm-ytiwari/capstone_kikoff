# Kikoff MMM — Presentation Speaker Scripts

**Presentation:** Kikoff Media Mix Modeling — Progress Review  
**Program:** UC San Diego Rady MSBA — Capstone 2026  
**Team:** Yash Tiwari · Chunjiang Liu · Shivang Bhatt · Yoko He  
**Date:** [fill in before presenting]

---

## Slide Assignment + Difficulty Guide

| Slide | Topic | Difficulty | Speaker |
|---|---|---|---|
| 1 | Cover | 1/5 | Yash |
| 2 | Table of Contents | 1/5 | Yash |
| 3 | Team | 1/5 | Yash |
| 4 | Executive Summary | 4/5 | Yash |
| 5 | Business Problem | 2/5 | Chunjiang |
| 6 | Data Overview | 3/5 | Chunjiang |
| 7 | Deliverables | 2/5 | Shivang |
| 8 | Evaluation Criteria | 2/5 | Shivang |
| 9 | Solution Path | 3/5 | Shivang |
| 10 | Results & Findings | 4/5 | Yoko |
| 11 | Analytics Strategy | 5/5 | Yoko |
| 12 | Conclusion & Next Steps | 2/5 | Yoko |
| 13 | Q&A | — | All |
| 14+ | Appendix | — | Reference only |

**Difficulty scale:** 1 = read the slide aloud, 5 = requires deep project context and MMM knowledge to explain fluently.

**Swapping guidance:** Slides 5, 7, 8, and 12 are safe to swap if someone wants lower-difficulty material. Slides 4, 10, and 11 should stay with whoever is most comfortable with the full project arc and modeling concepts.

---

## Before You Present

- [ ] Fill in the presentation date on Slide 1
- [ ] Fill in one-line bios on Slide 3 (concentration, prior role, what you owned on this project)
- [ ] Coordinate live handoffs — each speaker ends by naming the next person explicitly
- [ ] Do a single run-through as a team to hit the 13–15 minute total target

---

## Yash Tiwari — Slides 1–4

**Covers:** Cover, Table of Contents, Team, Executive Summary  
**Difficulty:** 1/5 to 4/5 (opens easy, peaks at Executive Summary)  
**Estimated time:** ~3.5 minutes

---

*[Slide 1 — Cover]*

Hi everyone — thank you for being here. I'm Yash Tiwari, and I'm here with my teammates Chunjiang Liu, Shivang Bhatt, and Yoko He. We're the Kikoff capstone team from the UC San Diego Rady MSBA program, and today we'll be walking you through our progress on building a Media Mix Model for Kikoff.

*[Slide 2 — Table of Contents]*

Here's a quick roadmap of what we'll cover. We'll move from the business context and data foundation, through our methodology and deliverables, into our findings to date, and close with recommendations and next steps. Each of us will take a section — I'll start us off, then hand over to my teammates.

*[Slide 3 — Team]*

A quick introduction. [Coordinate live — each person introduces themselves in one sentence as they're named: name, concentration or prior role, and what they owned on this project.]

*[Slide 4 — Executive Summary]*

Let me give you the big picture before we go deeper.

Kikoff spends roughly $100 million annually across more than ten marketing channels. The challenge is that their current approach relies heavily on last-touch and platform-reported attribution — meaning they know someone converted, but not which combination of marketing activity actually caused it. That makes it very hard to confidently answer: "If we shift budget from Meta to TikTok, do we grow faster or slower?"

Our goal is to build a Bayesian Media Mix Model that gives Kikoff a causal, holistic view of what each channel contributes — one that supports confident budget reallocation and seasonal planning.

A few important pivots happened along the way. Originally we were scoping at the channel level — just "Meta" or "TikTok." After our first sponsor meeting, we realigned to model at the channel-by-platform level — so "Meta iOS," "Meta Web," and so on — and to produce two outputs: conversion volume and customer lifetime value. These behave differently and require separate treatment.

We also evaluated five modeling frameworks — Meridian, LightweightMMM, Robyn, a custom PyMC build, and PyMC-Marketing. We selected PyMC-Marketing for its flexibility, its native support for incrementality priors, and a clean fallback path to raw PyMC if needed. That decision is now locked and sponsor-approved.

On the data side: we completed a full audit of 15 raw source groups, reconciled them to the sponsor's expected channel taxonomy, and identified five data quality issues — including one significant anomaly where a category called "Idle/Others" grew from roughly 1% to 14% of total spend. That's now under investigation by the sponsor.

In short: we've completed Phase 1 ahead of schedule, with a locked taxonomy, a selected framework, and a clear path into modeling. Chunjiang will now take us through the business problem and data in more detail.

---

## Chunjiang Liu — Slides 5–6

**Covers:** Business Problem, Data Overview  
**Difficulty:** 2/5 then 3/5  
**Estimated time:** ~3 minutes

**Transition cue:** Yash has just finished the executive summary and named you.

---

*[Slide 5 — Business Problem]*

Thanks, Yash. Let me give you a bit more texture on the business context.

Kikoff is a fintech company focused on credit-building and financial wellness subscriptions — primarily mobile-first, based in the Bay Area. Our sponsor is Abheek Sinha, their Head of Growth and Marketing.

The problem they're trying to solve is one that many consumer brands face at scale: as marketing spend grows, traditional attribution methods break down. Last-touch attribution gives all the credit to the final ad someone clicked before converting. Platform-reported attribution — what Meta or TikTok tells you — tends to be self-serving and doesn't account for the fact that users saw multiple ads across multiple channels.

What Kikoff needs is a way to assess diminishing returns — the point at which spending more on a channel stops generating proportional growth. They also need to understand how different channels perform across seasons: tax season and the holiday period behave very differently from mid-year, and budget planning needs to reflect that.

A few constraints worth noting. The sponsor explicitly ruled out simple linear regression — the methodology needs to be Bayesian. The incrementality test priors we incorporate have to be time-limited to the actual test windows, not applied retroactively to the full history. And our deliverable feeds roughly one-third of Kikoff's internal planning model — it's a key input, not the sole decision-maker.

*[Slide 6 — Data Overview]*

Here's what we're actually working with.

We have three datasets. First: daily spend broken down by source group and platform — iOS, Android, and Web. Second: daily outcomes — conversion counts and model-predicted lifetime value. Third: a CSV of historical incrementality tests covering TikTok, two Meta tests, and a CTV test — each with an incremental cost-per-acquisition estimate and a confidence interval.

The usable modeling window runs from Q3 2024 through March 2026 — roughly 21 months of clean daily data. The pre-Q3 2024 spend file has known gaps for several channels, so we're starting there and may extend backward if a corrected file arrives.

We reconciled 15 raw source groups down to the sponsor's expected channel structure — Meta, TikTok, Google, Apple Search, Linear TV, CTV, Podcast and Audio, Influencer, AppLovin, Liftoff, InMobi, a combined DSP bucket, and an Others/Idle category. Bing was dropped due to negligible spend.

We also found and resolved several data quality issues: platform typos in the raw data, two LTV anomaly windows that need imputation, a handful of null rows, and the Idle/Others growth anomaly Yash mentioned. Full details are in the appendix.

I'll hand it over to Shivang to walk through what we're delivering and how we're building it.

---

## Shivang Bhatt — Slides 7–9

**Covers:** Deliverables, Evaluation Criteria, Solution Path  
**Difficulty:** 2/5, 2/5, 3/5  
**Estimated time:** ~3 minutes

**Transition cue:** Chunjiang has just finished the data overview and named you.

---

*[Slide 7 — Deliverables]*

Thanks, Chunjiang. Now that you understand the data we're working with, let me walk through what we're actually building.

Our primary outputs are all at the channel-by-platform level. First: incremental contribution estimates — for each channel-platform combination, how much of observed conversions and LTV is attributable to that spend, net of everything else. Second: saturation and response curves — visuals that show at what spend level a channel hits diminishing returns. Third: ICAC and ROAS estimates at varying spend levels over time — so the sponsor can see not just current performance, but how efficiency changes if budgets shift.

On top of that, we're delivering seasonal budget allocation scenarios for three distinct periods — tax season, holiday, and steady-state — along with budget optimization recommendations that come with marginal-ROI guardrails.

We're also delivering a clean, documented, reproducible codebase so that future teams — or Kikoff internally — can refresh this model as new data comes in. No dashboard is required per the sponsor; notebooks and markdown reports are the target format.

*[Slide 8 — Evaluation Criteria]*

How do we know if the model is good enough to act on?

The sponsor's bar is directional stability — channel contribution estimates that don't flip wildly between runs and that clearly distinguish high-conviction channels from low-conviction ones. The model needs to tell a coherent story about which channels are saturated, which have room to scale, and how seasonal timing affects performance.

One number worth anchoring on: the sponsor said roughly 50% directional accuracy is acceptable for a model like this. MMM is a decision-support tool, not a forecast. The point isn't to predict next week's conversions precisely — it's to make better bets about where to put the next dollar and to sequence the right incrementality tests for Q3 and Q4. Transparency and reproducibility matter as much as point estimates.

*[Slide 9 — Solution Path]*

Here's how we get there.

We're working in five phases. Phase 1 — business understanding and data audit — is essentially complete. We've locked the taxonomy, selected the framework, and addressed the data quality issues.

Phase 2, which we're starting now, is data preparation and feature engineering. That means applying LTV imputation, standardizing platform labels, building the channel-by-platform spend variables, and engineering seasonality and holiday control features.

Phase 3 is the core modeling work — building the Bayesian MMM in PyMC-Marketing, starting with a baseline model and then layering in the incrementality priors within their specific test windows. The first milestone is producing ICAC and ROAS curves for a single channel-platform pair, then replicating across the full set.

Phase 4 moves into scenario planning — simulating alternative budget allocations and computing marginal ROI and CPA at different spend levels, with season-specific recommendations.

Phase 5 is synthesis: translating the model outputs into an executive narrative, final deck, and technical appendix.

I'll hand over to Yoko to cover what we've found so far and where the analytics is heading.

---

## Yoko He — Slides 10–12

**Covers:** Results & Findings, Analytics Strategy, Conclusion & Next Steps  
**Difficulty:** 4/5, 5/5, 2/5  
**Estimated time:** ~3.5 minutes

**Transition cue:** Shivang has just finished the solution path and named you.

**Note on Slide 11:** This is the most technically demanding section. Key terms to be comfortable explaining before presenting:
- **Adstock** — carry-over effect of advertising across days
- **Hill saturation / diminishing returns** — the curve that flattens as spend increases
- **Bayesian priors** — starting beliefs (from incrementality tests) that get updated by the historical data
- **Posterior predictive checks** — a way of asking: does the model reproduce what we already observed?

---

*[Slide 10 — Results & Findings to Date]*

Thanks, Shivang. We haven't run the model yet — Phase 2 starts this week — but Phase 1 produced substantial findings that directly shaped how we'll build.

On the data review: spend and outcome data are now merged at daily granularity, and the modeling window is confirmed as Q3 2024 through March 2026. The taxonomy reconciliation wasn't trivial — roughly 16% of spend sat in ambiguous source groups where the mapping to the sponsor's channel structure wasn't obvious. Getting that right matters because a misattributed 16% of spend would meaningfully distort every channel contribution estimate downstream.

The most important EDA finding is the Idle/Others anomaly. Spend in that bucket climbed from roughly 1% of total in early 2025 to about 14% recently. The sponsor has identified the driver as a category called "Idle" and is investigating internally. Until that's resolved, there's a real risk to the interpretability of every other channel — because if 14% of spend isn't tagged to a real channel, the model is partially blind.

Beyond that: Meta, TikTok, and Google account for roughly two-thirds of total spend. Seasonality is clear in the data — tax season shows a lift, late-year shows a dip. And the incrementality tests vary in confidence: the TikTok and Meta tests are user-level holdouts with tighter uncertainty ranges; the CTV test is a geo-based design, which is noisier by nature. The January 2026 Meta test was cancelled partway through, so we'll incorporate it with wider uncertainty bounds.

*[Slide 11 — Analytics Strategy]*

Let me walk through the modeling approach.

We're running two parallel models — one for daily conversion count, one for daily LTV — at the channel-by-platform level. That gives us roughly 20-plus channel-platform combinations, though we'll start with one end-to-end to validate the full pipeline before scaling.

Two transformations happen before the data enters the model. First, adstock — advertising has a carry-over effect. An ad someone sees today doesn't just influence today's decision; some fraction of that influence carries into tomorrow and the day after. We'll estimate that decay rate as a model parameter. Second, saturation — also called the Hill transformation — captures diminishing returns. Doubling your TikTok spend doesn't double your conversions; the curve flattens at higher spend levels. We'll estimate that shape per channel.

The Bayesian approach means we're not just fitting a curve to historical data. We're encoding prior beliefs — specifically the incrementality test estimates for Meta, TikTok, and CTV — as starting points, and then updating them with what the full historical record says. Critically, those priors are time-limited to the actual test windows, not applied across the whole history. That was an explicit requirement from the sponsor.

The framework is PyMC-Marketing. We'll evaluate fit using posterior predictive checks — essentially, does the model reproduce what we actually observed within reasonable uncertainty bounds — along with hold-out validation and prior sensitivity analysis.

*[Slide 12 — Conclusion & Next Steps]*

To close: we came in with a broad mandate to measure causal channel contribution. Over the past several weeks, we refined that into a concrete specification — channel-by-platform, dual outcomes, Bayesian with time-limited incrementality priors — completed the data foundation, and selected the framework. All of that is locked and sponsor-approved, ahead of schedule.

In the next two to three weeks: we apply data cleaning in the notebook, build the full feature set, and produce the first end-to-end ICAC and ROAS curves for a single channel-platform pair. From there we replicate across the remaining channels and consolidate into recommendations.

The downstream impact for Kikoff: a defensible, repeatable model that can anchor quarterly and annual budget discussions — with clearer visibility into where channels are saturating, and a prioritized roadmap for which incrementality tests to run next. The goal is that the next hundred million dollars of spend is better informed than the last.

Thank you. We're happy to take questions.

---

## Q&A — All Speakers

Open floor. If the room is quiet, use these to start discussion:

- Where is our biggest modeling risk right now?
- How do we know the model is "right enough" to act on?
- What would change our recommendations the most?
- Why Bayesian instead of a simpler regression approach?
- How do the incrementality tests actually feed into the model?

---

## Appendix Reference

Appendix slides cover:

- A1. Full SOURCE_GROUP to channel mapping with spend shares
- A2. DSP vendor spend distribution
- A3. Others/Idle share growth chart
- A4. Channel mix heatmap over time
- A5. Source group spend rank and concentration
- A6. Framework comparison matrix (Meridian vs PyMC-Marketing vs LightweightMMM vs Robyn vs custom PyMC)
- A7. Incrementality test summary (test, window, platform, iCAC, CI, conviction level)
- A8. Data quality register (findings and resolutions)
- A9. MMM concept primer — adstock, saturation, Bayesian priors, marginal vs average ROAS
- A10. Glossary and data dictionary
