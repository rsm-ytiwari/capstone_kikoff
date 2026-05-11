# Kikoff MMM — Midterm Presentation Speaker Scripts

**Presentation:** Kikoff Media Mix Modeling — Midterm Progress Review
**Program:** UC San Diego Rady MSBA — Capstone 2026
**Team:** Yash Tiwari · Chunjiang Liu · Shivang Bhatt · Yoko He
**Date:** [fill in before presenting]
**Target runtime:** 15 minutes

---

## Slide Assignment

| Slide | Topic | Difficulty | Speaker | Time |
|---|---|---|---|---|
| 1 | Cover | 1/5 | Yash | |
| 2 | Overview | 1/5 | Yash | |
| 3 | Who are we? | 1/5 | Yash | ~4.5 min |
| 4 | Executive Summary | 4/5 | Yash | |
| 5 | Business Problem & Organization | 2/5 | Chunjiang | ~3 min |
| 6 | Data Overview | 3/5 | Chunjiang | |
| 7 | Deliverables | 2/5 | Shivang | |
| 8 | Evaluation Criteria | 2/5 | Shivang | ~3.5 min |
| 9 | Results & Findings — Channels | 3/5 | Shivang | |
| 10 | Results & Findings — Outcomes | 3/5 | Yoko | |
| 11 | Analytics Strategy | 5/5 | Yoko | ~4 min |
| 12 | Recommendations | 3/5 | Yoko | |
| 13 | Conclusion & Next Steps | 2/5 | Yash | |
| 14 | Q&A | — | All | |
| 14–19 | Appendix | — | Reference | |

**Difficulty scale:** 1 = read the slide, 5 = requires deep project context.

**Swapping guidance:** Slides 5, 7, 8, and 13 are safe to swap. Slides 4, 11, and 12 stay with whoever knows the project arc best.

---

## Before You Present

- [ ] Fill in the date on Slide 1
- [ ] Confirm role descriptions on Slide 3 match the photo slide
- [ ] Each speaker ends by naming the next person explicitly
- [ ] One full run-through as a team before presenting

---

## Yash Tiwari — Slides 1–4 (~4.5 min)

---

*[Slide 1 — Cover]*

Hi everyone — I'm Yash Tiwari. With me are Chunjiang Liu, Shivang Bhatt, and Yoko He. We're the Kikoff capstone team from UC San Diego's Rady MSBA program. Today we'll walk you through where we are on Kikoff's Media Mix Model and where we're headed.

*[Slide 2 — Overview]*

Twelve sections, four speakers. We'll start with the business problem and data, walk through the methodology and findings, and close with recommendations and next steps.

*[Slide 3 — Who Are We?]*

Quick intros. [Each person: name, concentration or prior role, what you owned on this project — one sentence each.]

*[Slide 4 — Executive Summary]*

Let me start with the core problem.

Kikoff spends roughly $113 million a year across thirteen marketing channels — Meta, TikTok, Google, TV, podcast, and more. Right now, they can't confidently say which of those channels is actually responsible for new customers. The tools they use — last-click attribution, platform-reported ROAS — give every channel full credit for every conversion. Each platform reports its own numbers in its own favor. So every channel looks like a winner, and the question "if we shift spend from Meta to TikTok, do we grow faster or slower?" has no defensible answer today.

What we're building is a Bayesian Media Mix Model. That's a statistical framework that looks across all channels simultaneously, estimates the true contribution of each one, models where spend starts to saturate, and uses Kikoff's own controlled experiments to calibrate.

We made two early decisions that shaped the whole scope. First: we're modeling at the channel-and-platform level — not just "Meta" as a single number, but Meta iOS, Meta Web, and Meta Android as separate inputs — because each behaves differently, and Kikoff ran their incrementality tests at exactly that level. Second: we're producing two separate outputs — conversion volume and customer lifetime value — because the same campaign can look great on volume and weak on value. Kikoff needs to see both.

For the framework, we evaluated five options and there was one clear answer: PyMC-Marketing. It's the only active framework that meets all three non-negotiable requirements — time-limited incrementality priors, saturation modeling, and dual dependent variables. Sponsor sign-off came April 21st. That's locked.

Phase 1 is done. We reconciled fifteen raw source groups into thirteen canonical channels, resolved five data quality issues, and confirmed a clean modeling window: 639 daily observations from Q3 2024 through March 2026. We came in ahead of schedule. Chunjiang will take you through the business context and walk you through a data quality issue that, left unfixed, would have broken the model.

---

## Chunjiang Liu — Slides 5–6 (~3 min)

**Transition cue:** Yash has named you.

---

*[Slide 5 — Business Problem & Organization]*

Thanks, Yash. Let me make the attribution problem concrete.

Kikoff is a mobile-first fintech based in the Bay Area, focused on credit-building subscriptions. Our day-to-day sponsor is Abheek Sinha, their Head of Growth and Marketing.

Here's what attribution actually looks like in practice. A customer sees a TikTok ad on Monday, a Google search result on Wednesday, a Meta retargeting ad on Friday — and signs up on Saturday. Last-click attribution gives Meta 100% of the credit. Every platform's own reporting does the same, just in its own favor. So you end up with every channel claiming to be a winner. No way to tell which combination of activity actually caused the conversion. No visibility into where you're spending money on something that's already saturated.

What Kikoff actually needs is two things those tools can't give them. First: diminishing returns curves — at what point does adding more budget to a channel stop paying off? Second: seasonality awareness, because a dollar during tax season behaves very differently from a dollar in August.

Three constraints from the sponsor shaped our approach: the model must be Bayesian, the priors from our incrementality tests can only apply during the windows when those tests ran, and our output feeds roughly one-third of Kikoff's internal budget planning model. What we build has real downstream consequences.

*[Slide 6 — Data Overview]*

Three data sources. Daily spend broken down by channel and platform. Daily outcomes — conversions and predicted lifetime value. And results from four controlled experiments Kikoff has run, each measuring the true incremental impact of a specific channel against a holdout group that wasn't shown the ad — TikTok, two Meta tests, and CTV.

We came in with fifteen differently-named source groups and reconciled them into thirteen canonical channels. Along the way we resolved five data quality issues. The most significant: a category called Idle/Others had grown from 1% to 14% of total spend — 942 erroneous rows, removed by data engineering. That category is now clean.

That gives us a clean modeling window: 639 daily observations from Q3 2024 through March 2026. Shivang will walk you through what we're actually building — and why the framework choice turned out to be less obvious than it looks.

---

## Shivang Bhatt — Slides 7–9 (~3.5 min)

**Transition cue:** Chunjiang has named you.

---

*[Slide 7 — Deliverables]*

Thanks, Chunjiang. So what does the finished product actually look like?

For each channel-platform combination, we produce two things. A response curve showing efficiency at current spend levels and what happens when you move budget up or down by 20%. And a saturation curve showing exactly where that channel's returns start to flatten out. On top of that: seasonal budget recommendations for three distinct periods — tax season, the holiday window, and the steady state between them.

The table on the right makes it concrete — one row per channel-platform pair, with iCAC (the incremental cost to acquire one customer), iROAS (return for every dollar spent), a saturation read, and a plain recommended action. Meta channels are first — that's Phase 2, running now. All other channel groups follow in Phase 3. Full package, all 13 channels, delivered by June 6. Reproducible and refreshable as new data arrives.

*[Slide 8 — Evaluation Criteria]*

Getting to that output required choosing the right modeling framework. Five serious options — and it wasn't an obvious call.

We scored them against three requirements we couldn't compromise on: the ability to incorporate Kikoff's controlled experiment results as model inputs; saturation modeling at the channel level; and the ability to run conversion count and lifetime value as separate outputs from the same model.

PyMC-Marketing is the only active framework that clears all three. Meridian and Robyn don't support dual dependent variables. LightweightMMM is deprecated. Custom PyMC would meet the criteria but adds timeline risk we can't absorb. Those controlled experiments are the highest-signal data in the project — a framework that can't use them leaves the strongest prior we own on the table.

*[Slide 9 — Results & Findings: Channels]*

Three channels absorb nearly three-quarters of the spend: Meta at $41.5 million, TikTok at $23.4 million, Google at $17.6 million — 73% of the $113 million total. The remaining ten channels split the rest.

That concentration has two implications. The top three drive most of the model's variance, so they'll largely define how the model behaves. And for the smaller channels, we may not have enough daily history to reliably separate signal from noise on their own — which is exactly why the incrementality experiments matter as anchors. The channel mix has also shifted over the 21-month window. The model has to capture time-varying performance, not just overall averages. Yoko will show you what the outcome data revealed and how those findings shaped the model's design.

---

## Yoko He — Slides 10–12 (~3 min)

**Transition cue:** Shivang has named you.

**Before Slide 11 — know these terms:**
- **Adstock** — advertising carry-over effect across days
- **Hill saturation** — the diminishing returns curve
- **Bayesian priors** — incrementality test estimates encoded as starting beliefs, updated by history
- **Time-limited priors** — priors active only within the actual test window, not the full history

---

*[Slide 10 — Results & Findings: Outcomes]*

Thanks, Shivang. Phase 1 was mostly groundwork — but it surfaced findings that directly shaped how the model gets built.

The first is seasonality. Conversions spike sharply in March and April — tax season, when people are actively engaged with their financial health — and drop off in late summer. Without explicit seasonality controls, the model might credit TikTok for a lift that was really just the calendar pulling in more financially motivated customers. We can't have that.

The second is timing. We measured the lag between spend and conversions: correlation peaks same-day at r = 0.45, with only slight carry-over into the next day. That's what short adstock decay looks like — media effects in this category are essentially immediate. We still estimate the decay rate per channel rather than assuming it, but the data gives us a strong prior on what to expect.

*[Slide 11 — Analytics Strategy]*

Let me walk through how the model works — as plainly as I can.

Two models run in parallel: one predicts how many new customers sign up on a given day, the other predicts what those customers are worth over the following year. They share the same inputs but produce separate outputs, because what drives volume doesn't always drive value.

Before data goes into either model, two adjustments happen. The first is adstock — an ad someone sees today doesn't only influence them today. Some of that effect carries forward. Rather than assuming the same decay rate for every channel, we estimate it per channel from the data. Our Phase 1 lag analysis told us to expect short decay in this category: correlation between spend and conversions peaks same-day at r = 0.45. Same-day response. We still estimate it per channel — the data just gives us a strong prior on what to expect.

The second is Hill saturation — the diminishing returns curve. Doubling spend on a channel doesn't double your customers. The relationship flattens, and the shape of that flattening differs by channel. We estimate that per channel too.

Then the Bayesian layer. Instead of fitting the model purely to historical observations, we give it a head start using what we already know from our experiments. Kikoff ran four controlled tests — TikTok, two Meta tests, and CTV — each measuring true incremental impact against a holdout group. Those results become starting beliefs that the model then updates against 21 months of observed data. Critically: those priors are active only during the windows when the tests actually ran — applying them across the full history would claim more than the experiments actually showed. That was a deliberate design decision.

We'll share convergence diagnostics and the first ICAC and ROAS curves at the final presentation.

*[Slide 12 — Recommendations]*

Every model output maps to one of four plain signals. Scale: iCAC declining, iROAS above threshold, room before saturation — move budget in. Hold: efficiency marginal, near diminishing returns — stay where you are. Investigate: iCAC rising or iROAS below 1x — something's off, find out what before committing more spend. Test: no incrementality data exists for this channel — run a holdout before moving budget.

The decisioning table — iCAC and ROAS curves per channel-platform pair, with seasonal modifiers — is what we're building now. All 13 channels, full package, by June 6. The model is running; results at the final presentation.

Now, Yash will walk us through the conclusion and what it all means.

## Yash— Slides 13 (~1 min)
*[Slide 13 — Conclusion & Next Steps]*

We came in with a mandate to measure causal contribution and turned it into a precise, working specification. Phase 1 is done: the taxonomy is locked, the framework is selected and approved, the data is clean, the modeling window is confirmed.

From here: the model run completes, we produce curves for the first channel-platform pair, replicate across all thirteen channels, and build the decisioning layer on top.

The end goal is a model Kikoff can run quarterly — one that tells them not just what worked last year, but where the next dollar should go. Not a perfect model — there's no such thing in marketing measurement. But a defensible one that surfaces which channels to scale, which experiments to run, and where a hundred million dollars in spend is actually going. Thank you.

---

## Appendix Reference

**Slides 14–19 in the deck. Pull up on demand during Q&A.**

### Roadmap (most likely to be asked)
- **A-R1 (slide 15).** Project phases — Phase 1 complete, Phase 2 in progress, Phase 3–4 queued. Scope and key outputs per phase.
- **A-R2 (slide 16).** Phase 2 milestones — M1 and M2 complete (data cleaning + prior mechanism decided), M3 active (Meta POC fit), M4–M6 queued.

### EDA Charts
- **A-EDA-1 (slide 17).** Top 10 channels by spend — Meta, TikTok, Google drive 73% of $113M.
- **A-EDA-2 (slide 18).** Spend vs. conversions scatter (r = 0.45) + LTV per conversion over time.
- **A-EDA-3 (slide 19).** Monthly seasonality index + total daily spend trend.

### Reference (not in deck — verbal only if asked)
- A1. Full SOURCE_GROUP → channel mapping with spend shares
- A2. DSP vendor spend distribution (StackAdapt + Appvertiser)
- A3. Framework comparison matrix — full criteria and scoring
- A4. Incrementality test summary — window, platform, iCAC estimate, CI, conviction
- A5. Data quality register — all 5 issues and resolutions
- A6. MMM concept primer — adstock, saturation, Bayesian priors, marginal vs average ROAS

---

## Q&A Prep — Likely Keith Questions

- **"Where is your biggest modeling risk?"** → Time-limited prior mechanism (Q19a) — whether the saturation curve assumption holds across the full window. We've selected the mechanism; Abheek confirmation pending.
- **"How do you know the model is good enough to act on?"** → Convergence checks (R-hat < 1.1, ESS > 400), ICAC ordering validation against incrementality experiments, posterior predictive check. No ground-truth for final ROAS — model value is in surfacing the right experiments to run next.
- **"Why Bayesian instead of a simpler regression?"** → Incrementality tests give us real experimental data to inject as priors. A frequentist regression can't use that information. Bayesian also gives uncertainty estimates — we can say "we're 80% confident ICAC is in this range" rather than a single point.
- **"How do incrementality tests feed into the model?"** → We use `add_lift_test_measurements()` in PyMC-Marketing. Each test (TikTok, two Meta, CTV) contributes a lift estimate and a confidence interval. The model's posterior updates those estimates against 21 months of observational data. Critically: the prior is only active within the test window, not the full history.
- **"What happens after June 6?"** → Handoff package to Kikoff: reproducible model code, decisioning table, seasonal scenarios. Model is designed to be re-run quarterly as new data comes in.
