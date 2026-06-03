# What We Tried: Full Modeling Record, Kikoff MMM

*Prepared by our team for handover to the Kikoff team*

---

## 1. Purpose and how to read this

This document is the complete record of every modeling approach our team tried on the Kikoff
marketing mix model, what each one showed, and why it did or did not make it into the model we
are handing over. It is written for the next person who picks this up, so they do not have to
re-run experiments we already ran.

**The one-line headline:** the model assigns roughly two-thirds (about 67%) of value to a
baseline that paid spend does not explain. We tested that number hard, across every modeling
lever we could reasonable turn and across two independent modeling engines, and it held in the
same range every time. The baseline is a property of the data and the attribution available to
us, not of any one tool's settings. The honest path to a lower, better-attributed baseline is
**richer data inputs, not more model tuning.** The modeling levers are exhausted.

A companion document, the model and engine findings summary, covers the final model and the
baseline trade-off at a higher level. This document is the exhaustive version: it lists the
approaches that did not work alongside the ones that did, because both are useful to the next
iteration.

---

## 2. The final model in one page

**Two separate models, not one.** We built two models because the business needs two different
answers:

- **Conversions model:** weekly count of new subscribers as the outcome. This is the primary
  model and answers volume efficiency (cost per conversion).
- **Lifetime-value model:** weekly sum of predicted three-year customer value as the outcome.
  This answers value efficiency (return on spend in dollars).

These are genuinely separate models. The lifetime-value answer cannot be produced by transforming
the conversions answer, because each one is fit against a different outcome.

**How the model is built.** All nineteen channels enter the model together (a model that left
channels out would mis-assign their effect). Each channel's spend passes through a carryover
(adstock) transform and a diminishing-returns (saturation) curve. Channels that had an
incrementality test are calibrated to that test over the test window. The model converges cleanly
and is validated out-of-time on a held-out tail of the data.

**What we are delivering.** The agreed output is a **relative ranking of channels by marginal cost
per acquisition and marginal return on spend, over the last 26 weeks, each with a point estimate
and a confidence range.** The absolute magnitudes run roughly 1.5 to 1.6 times higher than the
client's real-world read, which is accepted; the value is in the **relative ordering** of channels
under the current baseline, which is what the decisioning framework runs on.

**The accepted limitation.** The baseline sits near 67%. We treat this as a documented limitation
of a spend-only model, not a defect to keep tuning. The next iteration's job is to redistribute
that baseline across channels with better data.

---

## 3. Everything we tried

Each approach below is recorded as what we tried, what we found, and why it did or did not make it
into the final model.

### 3.1 The two-model split (conversions and lifetime value)

- **What we tried:** two separate models, one with weekly conversions as the outcome and one with
  weekly three-year lifetime value as the outcome.
- **What we found:** the two outcomes carry different information. Some channels drive conversion
  volume; others drive higher-value customers. A single model cannot serve both, and converting one
  model's output into the other is not valid because each is fit against its own outcome.
- **Outcome:** both models are in the final deliverable. Conversions is primary; lifetime value is
  the supplementary value lens.

### 3.2 Incrementality-test calibration and confidence-width sweeps

- **What we tried:** the channels that had lift tests (the Meta, TikTok, and connected-TV tests) are
  pinned to those test results over their test windows. We then swept how tightly we hold the model
  to those tests, from a tight 10% confidence width out to 30%, to see whether a looser tie would
  bring the baseline down.
- **What we found:** the baseline and the per-channel cost move **in the same direction**, not
  against each other. Tightening the tie to the tests pulls channel effects up in the test windows,
  which pushes residual value into the baseline and **also** raises the per-channel cost numbers.
  Loosening the tie lowers both together. There is no confidence width that delivers a 30 to 40%
  baseline; loosening only makes the channel cost numbers worse while barely moving the baseline
  (about a fifth of a point of baseline per point of loosening).
- **Outcome:** we kept the disciplined tight calibration. The sweep is documented as evidence that
  confidence width is not the lever that lowers the baseline.

### 3.3 Informative priors on untested channels

- **What we tried:** twelve channels have no incrementality test. We gave the most under-credited of
  them informative starting points based on the blended portfolio cost per conversion, to see whether
  crediting them more would pull value out of the baseline.
- **What we found:** the baseline moved only about 1.5 points. The data itself does not support those
  channels absorbing five to ten times more value; the likelihood overruled the informative starting
  points. Pushing harder would manufacture attribution the data rejects, and the out-of-time accuracy
  ticked slightly worse.
- **Outcome:** not adopted as a baseline fix. The untested channels keep weakly-informative defaults.

### 3.4 Saturation-curve (diminishing-returns) settings

- **What we tried:** two settings for the curvature of the diminishing-returns curve, a looser
  default and a tighter one, to check whether the curve shape was inflating the baseline.
- **What we found:** the tighter setting dramatically improved how cleanly the model samples (far
  more effective samples, no divergences) while leaving the per-channel cost estimates essentially
  unchanged. The looser setting cut the baseline only about 2 points but degraded convergence to the
  point of unreliability.
- **Outcome:** we kept the tighter setting. It is a convergence aid, not a source of bias, and the
  baseline is not a curvature artifact.

### 3.5 Intercept and baseline specification

- **What we tried:** we forced the model's intercept toward a roughly 35% baseline to see whether the
  model could be made to hold a low baseline directly.
- **What we found:** the model rejected it. Even pushed hard toward 35%, the fitted baseline settled
  back near 60% on its own. The freed value flowed to out-of-window weeks and untested channels rather
  than to the tested channels, and the fit did not improve. **The data structurally resists a baseline
  below about 60%.**
- **Outcome:** not adopted. This is one of the strongest pieces of evidence that the high baseline is
  real and not a modeling choice.

### 3.6 A second, independent modeling engine

- **What we tried:** we rebuilt the model from scratch in a second, independent engine (Google's
  Meridian) on the same data, with the same channels, the same carryover limit, and the same
  incrementality-test calibration. The point was to stress-test the baseline: if two different
  mathematical approaches disagree, the number is an artifact; if they agree, it is real.
- **What we found:** they agree. The second engine lands at essentially the same baseline, about
  66 to 67% with matched calibration and about 69 to 70% with broader calibration. The same two
  channels that fail their benchmarks in our primary engine fail them in the second engine too. The
  out-of-time accuracy is statistically tied on conversions, with the second engine slightly ahead on
  lifetime value. The smoother-looking curves in the second engine come from a built-in curvature
  assumption applied uniformly to every channel, not from a finding in the data.
- **Outcome:** the primary engine stays the anchor (it powers the approved dashboard and decisioning
  page and is validated end to end). The second engine is kept as corroboration. Its key contribution
  is proof that the **baseline is engine-agnostic** and not a quirk of one tool's math.

### 3.7 Synthetic-data recovery test

- **What we tried:** we generated a synthetic dataset with a **known** baseline built in (30%) and ran
  it through the exact same pipeline, to check whether the method recovers a baseline it was given or
  inflates it.
- **What we found:** the pipeline recovered a baseline of about **30.3%**, within a third of a point of
  the truth. We repeated the check at a known 50% baseline and recovered about 49.8%, and at a 30%
  baseline with extra delayed channel effect and recovered about 29.9%.
- **Outcome:** this is decisive. The method is unbiased; it does not manufacture a high baseline. The
  real 67% is therefore a genuine property of the Kikoff data, not a fitting artifact.

### 3.8 Macro / economic demand controls

- **What we tried:** we added public economic indicators (a Treasury interest-rate series and a
  consumer-sentiment series, later also unemployment) as demand controls, on the theory that broad
  demand swings were being mis-credited to the baseline.
- **What we found:** at first this looked like the breakthrough. The baseline dropped from about 67%
  to 49%, and the out-of-time forecast error fell from the mid-teens to about 7%. But when we stress-
  tested it by removing the simple time trend from those economic series, the entire gain vanished:
  the baseline went back to about 62% and the error back to about 17%. The economic indicators were
  acting as a stand-in for the time trend, not capturing real demand.

  The clean way to see this: imagine predicting drownings from ice-cream sales. Both rise in summer,
  so without stripping out the season, ice cream looks like a great predictor of drownings. It is not;
  summer drives both. The economic series were the ice cream here. They moved with the trend, so they
  looked like they explained the baseline, but once the trend was removed there was nothing left.
- **Outcome:** not in the final model. It is documented as a sensitivity that did not survive its
  stress test. The lesson for the next iteration: a real demand control must be checked against the
  time trend before it can be trusted.

### 3.9 Search-interest demand index

- **What we tried:** a weekly external search-interest index (Google Trends terms for the brand and
  for credit-building) as a demand control.
- **What we found:** it improves the out-of-time narrative by about 5 to 6 points and shaves a few
  points off the baseline, and unlike the economic indicators it is not purely a trend stand-in. But
  it is a rescaling-prone proxy that would need to be re-sourced and vetted before it goes into a
  client-facing model, and it does not fix the two channels that miss their benchmarks.
- **Outcome:** kept as a documented sensitivity that strengthens the demand story, not promoted into
  the shipped model this cycle. A vetted version is a reasonable thing for the next iteration to revisit.

### 3.10 Alternative likelihood and pooled priors

- **What we tried:** two structural alternatives. First, a count-style likelihood (negative binomial)
  better suited to conversion counts. Second, a hierarchical (partial-pooling) structure that lets
  channels borrow strength from one another.
- **What we found:** the count-style likelihood is not supported in the modeling library we used, and
  the nearest substitute changed essentially nothing. The hierarchical structure failed to converge
  (severe sampling pathology) and did not tighten the untested channels' estimates.
- **Outcome:** both rejected. The likelihood family and pooling are not the lever here.

### 3.11 The saturation-curve display correction

- **What we tried:** in an earlier review, the saturation curves looked suspiciously flat at high
  spend, which raised a model-validity concern. We traced it.
- **What we found:** it was a charting bug, not a model problem. The charts were plotting **average**
  cost per unit, which flattens at high spend by construction, instead of **marginal** cost, which is
  the quantity the model actually estimates. Once corrected, the curves rise as expected, with wider
  confidence at the high-spend end where we have little history.
- **Outcome:** the display is fixed. This was a reporting correction, not a change to the model, and it
  retired the earlier "flat curve" concern.

### 3.12 Seasonality

- **What we tried:** we measured seasonality in both outcomes and tested adding flexible trend and
  seasonal terms to the model.
- **What we found:** seasonality is real but modest, a swing of roughly 30 to 35% around the weekly
  average, with weak underlying trend. Crucially, seasonality explains **out-of-time over-prediction**
  (the model over-predicts in the slow winter weeks), not the baseline **level**. Adding flexible trend
  or seasonal knots did not lower the baseline; in the more aggressive settings it destabilized the
  decomposition entirely.
- **Outcome:** not used as a baseline fix. The honest place to handle seasonality in a future iteration
  is an orthogonal seasonal control to improve forecast accuracy, with the expectation that it will not
  move the baseline down.

---

## 4. Where the baseline comes from

The roughly 67% baseline decomposes into two understandable pieces.

- **About a third is genuine organic demand:** customers who would have subscribed without the measured
  paid channels. This is consistent with the client's own read that the attributed-revenue universe is
  roughly two-thirds of total value, leaving about a third as organic. For a subscription product with
  recurring billing and word-of-mouth referral, a high organic share is normal, and it is not
  recoverable by any model that only sees paid spend.
- **The remainder is paid credit the spend-only model cannot place on a specific channel,** so it lands
  in the baseline instead. This credit is spread across channels that are under-instrumented, lift-tested
  lightly or not at all, where the model has weaker information to attribute against. Several mechanisms
  contribute here, including activity that the spend-only inputs simply cannot resolve to a channel. We
  are deliberately not naming a single channel as the explanation; the model is designed to capture these
  effects in aggregate, and the missing piece is the **data that would let it split that credit across
  channels.**

Put on a like-for-like footing against the attributed-revenue universe, the baseline is closer to a
**45 to 57% range.** The gap to a 30 to 40% target is a data-scope ceiling, not a tuning failure.

---

## 5. Why Northbeam shows a lower baseline

Northbeam reports a much lower baseline for Kikoff. It is worth being precise about why, because the
explanation is not the obvious one.

Northbeam **runs on the same data we have.** For this engagement it does not have multi-touch or
user-level click access either. Its lower baseline comes from **proprietary models applied to the same
data,** not from a richer attribution feed. So the gap between our number and theirs is a modeling-and-
philosophy difference, not a data-access difference.

The honest read is that the truth sits between the two numbers. Click-based and multi-touch methods tend
to over-credit the trackable paid channels, while a marketing mix model can leave genuine paid credit in
the baseline when it only sees spend. Neither number is "right." Part of the gap is also an expectations
difference: a 30 to 40% baseline is a one-time-purchase intuition, and a retention-heavy subscription
product legitimately runs higher.

---

## 6. The real frontier: richer data, not more modeling

We have exhausted the modeling levers. Every lever we turned, confidence width, untested-channel priors,
curvature, intercept, a second engine, economic and search-interest controls, landed the baseline in the
same 41 to 67% band, and the only way to reach the low end abandons the discipline that keeps the channels
honest and the forecast accurate. The next iteration's leverage is **data we did not have**, ranked by
expected payoff:

1. **Channel-level impressions, reach, and frequency** (especially for the channels whose effect runs
   through views rather than clicks). Spend-only inputs structurally cannot resolve that kind of activity
   to a channel. This is the single most promising input for redistributing the baseline.
2. **Product, pricing, and feature-launch event dates.** Real demand-shifting events, dated, let the model
   absorb level changes legitimately instead of leaving them in the baseline.
3. **A vetted external demand index** to replace the proxy we tested, checked against the time trend so it
   does not repeat the economic-indicator trap.

These inputs are what would let the model split the 67% across channels and move toward the client's
stated next-iteration goal of a 20 to 25% baseline. More modeling tricks will not get there; better data
will.

---

## 7. Handover checklist

What the next person picks up:

- **The two fitted models** (conversions and lifetime value), the validated pipeline, and the
  out-of-time validation.
- **The dashboard and the decisioning page,** including the per-channel marginal cost and return views
  and the relative channel ranking over the last 26 weeks.
- **The documented sensitivities** that did not ship but are worth revisiting with better data: the
  search-interest demand index and the seasonal control.
- **The ranked data asks** in Section 6, in priority order, as the concrete inputs that would move the
  baseline.
- **This record,** so no experiment here needs to be re-run from scratch.
