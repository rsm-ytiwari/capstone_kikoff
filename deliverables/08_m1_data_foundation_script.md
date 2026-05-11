# Presenter Script — Phase 1: Data Foundation
**Audience:** Abheek (Kikoff)  
**Date:** 2026-04-28  
**Deck:** 08_m1_data_foundation.qmd (17 slides — numbers match in-browser counter)

> **How to use this script:** The talking points are what you'd naturally say — not word-for-word. Read them a few times, then present from memory. The anticipated questions are ones we've actually thought through, so answer them in your own words.

---

## Slide 1 — Title slide

"Thanks for making the time. We're excited to show you where Phase 1 landed — we'll walk through the data, the cleaning decisions we made, and why we think it's ready to model."

*Move quickly. Don't spend more than 15 seconds here.*

---

## Slide 2 — We're building two parallel models

"Before we get into the data itself, we want to quickly explain the setup — because it shapes everything we did in Phase 1.

We're building two models. One tracks how many customers each channel drives. The other tracks how valuable those customers are — using Kikoff's own LTV predictions. The conversion model is the main one. The LTV model is more of a quality check.

This structure came out of our conversations with you — the idea that raw conversion counts can be misleading if you don't also look at customer value."

*This is Abheek's framing from Meeting 3. Acknowledge it came from him — it'll land well.*

**If asked — Why not one model?**
"Because two channels can drive the same number of signups but completely different customers. One might bring people who stay for years; the other might bring people who churn in a month. A single model would treat those as equal. We want to surface that difference."

---

## Slide 3 — Channels that look equal on conversions can differ sharply on customer value

"Here's the concrete version of that. Say a DSP channel drives a lot of signups — but those customers churn fast. Meta drives fewer signups, but those customers stick around. If you only look at conversion counts, the DSP looks better. The LTV model is what catches that.

So the two models work together — conversions tell you volume, LTV tells you quality."

**If asked — Is this a standard approach?**
"It's pretty common in performance marketing. The alternative is to blend LTV into a single metric, but that tends to hide the quality difference rather than surface it."

---

## Slide 4 — How we use both models — and what to do if they disagree

"We want to be honest about what happens when the two models don't agree — because they will sometimes.

The conversion model is our anchor. It's directly observed data. If the LTV model agrees, we have high confidence. If they disagree on a specific channel, we don't average them together — we flag it and bring it to you. A disagreement is actually informative: it suggests something about that channel's customers that's worth understanding.

One thing to keep in mind: LTV_1YEAR is Kikoff's own prediction, not a direct observation. We're attributing variation in that prediction to channels. So whatever assumptions Kikoff's LTV model makes, our model inherits. We just want to be upfront about that."

**If asked — What if they give conflicting budget recommendations?**
"We'd present both and be transparent about the conflict. The conversion model gets more weight, but a persistent divergence on one channel is a signal worth investigating — not something to paper over."

---

## Slide 5 — 639 days of clean data

"This is the dataset. Top panel is daily conversions, bottom is daily LTV — the total predicted revenue from customers acquired that day.

We start in Q3 2024 — that was your guidance, the point where channel-level spend data is complete and consistent. We end in March 2026 because April was a partial month at export time.

What we want to point out here: both series look clean. No gaps, no weird spikes. That's after the fixes we'll show in a few slides."

**If asked — Why does LTV look noisier than conversions?**
"LTV is a model prediction, not a direct count. Some of that noise is real variation in customer cohort quality day to day. Some is estimation uncertainty from Kikoff's LTV model. Both are expected."

---

## Slide 6 — Top 3 channels account for 73% of total spend

"Quick overview of the channel landscape. $112.9 million total across the dataset. Meta, TikTok, and Google together are about 73% of that.

The rest — CTV, linear TV, Apple Search Ads, podcast, the DSP channels — each sit somewhere between $1M and $8M. They're smaller, but there's enough data on each one to estimate channel-level effects in the model."

**If asked — Why is linear TV included if it's hard to attribute?**
"Because it's in the spend data and we want the model to account for it. The attribution will have wider uncertainty than digital channels — but that's the honest answer, not a reason to exclude it. We'll flag that in the results."

---

## Slide 7 — Channel grouping decisions — and why "Others" is no longer a concern

"Three decisions went into the final channel list.

First, StackAdapt and Appvertiser got combined into one DSP channel — they're both programmatic buyers, and you confirmed that makes sense.

Second, Bing is out. Kikoff isn't advertising there anymore, so there's nothing to attribute.

Third — and this is the one we want to highlight — Others. In the original file, Others was 9.2% of modeling-window spend. That's a real problem: if nearly 10% of budget is going to an untracked bucket, every other channel's attribution gets distorted. In the updated file from data engineering, Others is down to $33.9K — basically zero. Every dollar is now tied to a real channel."

*The Others fix matters a lot. Make sure it lands — it's one of the bigger data quality wins.*

**If asked — What were those 942 rows?**
"Data engineering identified them as erroneous spend entries — no valid source attribution. They were either reclassified or removed. The named channels aren't materially affected."

---

## Slide 8 — Platform label corrections

"The spend file had three inconsistent platform labels. Two were easy: 'iso' was a typo for iOS everywhere, and 'web and app' you told us in Meeting 3 should just be web.

The third one was rows logged as 'iOS and android' combined. We split those 50/50 between platforms — that's our working assumption. If you have data on the actual split, we'd love to update it before the final results. It doesn't change the channel totals, just how the iOS vs. Android breakdown looks within mobile."

**If asked — How much spend is this?**
"35 rows in the raw file. Not large enough to shift the channel-level picture, but worth getting right for the platform breakdown."

---

## Slide 9 — Four days had artificially suppressed LTV

"This was the most important data issue we found in Phase 1.

LTV_1YEAR gets estimated when a customer is acquired, then revised as behavioral signals come in. If the export happens before that revision is complete, some days show artificially low LTV — not because those customers were actually less valuable, just because the data wasn't finalized yet.

We found two windows where this happened. The first is in early 2024, before our modeling window starts — so the model never sees it. The second is four days in October 2025 — and that one is inside our training data, so it needed to be fixed."

**If asked — How did you know it was a data timing issue and not real behavior?**
"Two things. You mentioned in Meeting 3 that this is a known artifact of the LTV export process. And statistically, those four days were nearly three standard deviations below their surrounding context — that kind of drop is extremely unlikely to be genuine customer behavior."

---

## Slide 10 — Choosing the right imputation method

"Once we found the window, we had to figure out how to fill it in. We looked at a few options and want to be transparent about why we landed where we did.

Linear interpolation just draws a straight line between the start and end — but LTV has day-of-week patterns, so a straight line isn't realistic. Forward or backward fill copies the last known value, which is biased if LTV is trending. A global mean ignores that October and January are very different months.

We went with a 14-day rolling median centered on each flagged day. It draws from the surrounding two weeks, adapts to the local seasonal context, and the median is robust to edge cases where nearby days might themselves be slightly unusual.

We also noted your suggestion — averaging the boundary days on either side — is totally valid and would give similar results here. Ours handles unusual boundary days a little better, but the two approaches are close."

**If asked — Why not just drop those 4 days?**
"It would leave gaps in the time series, and there are channels with concentrated October spend. A clean imputed estimate is simpler for the model to work with than missing data."

---

## Slide 11 — The fix worked

"Here's the before-and-after. Blue is the raw data as received, green is post-imputation. The pink band marks the four-day window.

On the left, the raw values drop to near zero inside the window — then the imputed values fill back to a level consistent with what the surrounding days look like. On the right, the z-score panel is the quantitative check: raw data hits −2.8, well outside the ±2σ band. After the fix: 0.85 — solidly within normal range.

Those four days now look like any other October days. The model won't try to explain that dip with marketing spend."

**If asked — Does this change the overall LTV totals?**
"Not meaningfully. It's 4 days out of 639. The aggregate numbers barely move — what matters is that those days no longer look like anomalies to the model."

---

## Slide 12 — Spend and conversions move together

"Before building anything, we ran a basic check: do spend and conversions actually correlate in this dataset? If they didn't, the model would have nothing to learn from.

The correlation is 0.445 — positive and real. It's not super tight, but that's expected. Seasonality, brand awareness, and day-of-week effects all add noise. The MMM's job is to separate those out from the actual channel signal. We just needed to confirm there's something learnable here, and there is."

**If asked — Why isn't the correlation higher?**
"When everything is in the same seasonal period — tax season, for example — spend and conversions both go up together regardless of channel mix. A 0.45 correlation is actually healthy for this context. If it were 0.9+, it might mean the model would just be picking up seasonality, not channel effects."

---

## Slide 13 — Tax season demand

"This chart shows average daily conversions by month over our modeling window. April is the clear peak — around 3,350 per day. December is the lowest at about 2,250. That's roughly a 1.5× swing from trough to peak.

The pattern makes intuitive sense for a credit-building product — tax season gets people thinking about their finances. Spring and early summer stay elevated. Things cool off in fall and winter.

The reason this matters for modeling: if we don't explicitly account for seasonality, the model might credit channels that happen to run heavy in April with conversions that are actually calendar-driven. We're building that seasonal adjustment in so the channel estimates reflect real incremental impact."

**If asked — Are there other seasonal patterns worth modeling?**
"The chart shows some lift in October and the summer months are steady. We're modeling the full monthly pattern, not just the spring peak."

---

## Slide 14 — Four holdout tests anchor our Bayesian priors

"A Bayesian prior is basically a starting assumption — something the model holds before it looks at the data. Four of your holdout tests give us actual data to anchor those assumptions instead of just guessing.

Three of the four we'd call high confidence. TikTok and Meta's May 2025 tests are platform-level conversion lift studies — clean experimental design with clear results. CTV is a geo-based holdout, which inherently has wider uncertainty because you can't match individual users the same way you can on a platform.

The fourth — Meta January 2026 — you asked us to include and we did. The test got cancelled after three days because of a cell design issue that compressed reach too much. The results are still directionally meaningful, but we're treating it as a loose, wide prior rather than a tight one. We're not going to over-index on those specific iCAC numbers — they're unusually high, partly because of the design flaw and partly because January is just a harder acquisition period. We're including it to keep the model grounded in that time period, not to treat those numbers as precise anchors."

*Be straightforward about the Jan 2026 test — Abheek knows the context, he asked us to include it. Don't over-explain.*

**If asked — Why is the January 2026 iCAC so much higher than May 2025?**
"Probably two things: the test ended before it stabilized, which tends to inflate the estimate, and January acquisition is genuinely harder than May. We're using it as a wide constraint — directionally informative, not precisely trusted."

**If asked — What about the May 2025 test ending early?**
"May 2025 is a different situation. The reach was affected by the cell design, but the conversion lift measurement itself held up. We distinguish it from January: May is informative and reasonably tight; January is informative but diffuse."

---

## Slide 15 — All 5 data quality checks passed

"To close Phase 1 formally, we ran five gate checks. All five passed.

LTV imputation: z-score from 2.81 down to 0.85 — within normal range. Platform labels: clean. Channel taxonomy: applied. DSP combined coverage: 341 days in the modeling window, which is enough to estimate reliably. Date filter: 2024-07-01 to 2026-03-31, confirmed.

One open item: the iOS/Android 50/50 split. That doesn't block the model build, but we'll follow up to get a confirmed number before final results."

**If asked — What if the iOS/Android split is different?**
"It's a preprocessing update — we change the split, re-run the cleaning step, and the rest flows through. It won't require rebuilding the model from scratch."

---

## Slide 16 — Phase 2: What comes next

"We want to be transparent about one methodological question we're still working through.

The holdout tests each ran for 9 to 28 days inside a 639-day history. We want the model to use those experimental results — but only for the periods they actually cover. We don't want Meta's May 2025 iCAC to be applied to July 2024 data, for example.

We looked at three approaches. One — letting channel effectiveness drift over time as a smooth curve — turned out to be too coarse for our setup because it forces all channels to share the same drift pattern. That breaks per-channel precision.

Another — a precise window switch where the model uses a tight assumption during the test window and a loose one everywhere else — is the cleanest option technically. But it requires more custom code, so it's our backup.

We're starting with what the tool we're using is built for: using the holdout results to calibrate the shape of each channel's spend-outcome curve. It's not perfectly windowed to the test dates, but it's principled and well-tested. After we run the model, we'll check whether the holdout results are actually showing up in the output — and if not, we'll move to the more precise approach.

After that's settled: model run, response curves per channel and platform, then the decisioning layer."

*The key thing to communicate here: we've thought this through, we have a clear plan, and we're not pretending to have more certainty than we do.*

**If asked — Why not just use the more precise approach from the start?**
"More custom code means more things that could break quietly. We want to validate the baseline first — and honestly, running the simpler version first tells us whether the more complex one would even change the results."

**If asked — Does this mean the May 2025 result gets applied to all of 2024?**
"Technically yes in the starting approach — the calibration shapes the spend-outcome curve for the full history. The May result anchors the shape, not the level. The shape of how a channel responds to spend is more stable than the absolute iCAC. If we see evidence it shifted significantly, that's when we move to windowed priors."

**If asked — Do you need anything from us before the model runs?**
"The iOS/Android split would help. And if data engineering has any further file corrections, please send them before we kick off — easier to incorporate now than after the model is fit."

---

## Slide 17 — Closing

*Footer slide — no talking points. Either open for questions or close the meeting.*

---

*End of presenter script — Phase 1 Data Foundation | 2026-04-28*
