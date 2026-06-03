# Final Model Handover: Kikoff Marketing-Mix Model

*Prepared by our team for the Kikoff team and our academic supervisor*

## The short version

We built a Bayesian marketing-mix model that measures how Kikoff's paid channels drive
subscriptions and long-term value, using only aggregate weekly spend and outcomes. It runs at
weekly granularity across 19 channels and produces two outputs: a conversions model and a
3-year LTV model. The headline deliverable is a channel rank-ordering by marginal efficiency,
so you can see which channels earn the next dollar best. The model is privacy-robust by design,
which means it keeps working even as user-level tracking continues to disappear. This summary is
the one-read overview. The full account of what we tested and why lives in the companion
document.

## What the model is

- **A Bayesian marketing-mix model.** It learns how much of each week's outcome is attributable
  to each channel's spend, while accounting for saturation (the point where more spend stops
  paying back at the same rate) and carryover (spend that keeps working for a few weeks after it
  runs).
- **Two outputs, one engine.** The conversions model tracks how many customers each channel
  drives. The 3-year LTV model tracks how valuable those customers are. The conversions model is
  the primary one. The LTV model is the value-weighted companion.
- **Weekly, 19 channels, privacy-robust.** It is built entirely on aggregate weekly spend and
  outcomes. It uses no user-level tracking and no multi-touch attribution data, so it is durable
  against the loss of cookies and device identifiers.

## The headline deliverable: a channel ranking

The core output is a rank-ordering of every channel by **marginal iCAC** (the cost of the next
incremental customer) and **marginal iROAS** (the return on the next incremental dollar),
measured over the recent 26-week window. Each channel carries a point estimate and a confidence
range.

**Read the relative order, not the exact dollar figures.** The magnitudes run roughly 1.5 to
1.6 times inflated, so treat them as directional. What is trustworthy is the order: which
channels are more efficient than which.

The channels we lift-tested are the trustworthy core. Of seven channels tested against Kikoff's
incrementality results, five landed inside their tested range, and these five carry tight
confidence bands. Untested channels are directional only and show very wide bands.

| Channel | Marginal iCAC | iROAS | Rank | Confidence |
|---|---|---|---|---|
| Meta Android | $97 ($75 to $131) | 2.14 | 4 | Validated core, tight band |
| TikTok Android | $126 ($93 to $190) | 1.66 | 5 | Validated core, tight band |
| Meta iOS | $132 ($104 to $160) | 1.58 | 6 | Validated core, tight band |
| TikTok Web | $146 ($110 to $214) | 1.43 | 7 | Validated core, tight band |
| CTV | $152 ($91 to $325) | 1.37 | 8 | Validated core |
| Google Android | $1,001 ($71 to $14,061) | 0.21 | 18 | Untested, directional only |

The contrast in the last row is the point. The validated core has narrow ranges you can act on.
A directional channel like Google Android spans from $71 to over $14,000, which is the model
telling you it does not have enough information to pin that channel down. The full ranking for
all 19 channels is in the dashboard.

## How to make budget decisions

The decisioning rule is simple: **move budget on relative channel order.**

- Lean into channels that rank high on marginal efficiency. Pull back from channels that rank
  low.
- Trust the validated core most. Treat untested channels as directional signals, not firm
  numbers.
- Watch each channel's confidence band. A tight band is a confident call. A wide band is a
  "needs more evidence" flag.

This framework holds even though most measured outcome sits in a baseline (see below). Budget
decisions ride on each channel's **marginal** behavior, which is robust to the overall baseline
level. A high baseline tells you how much demand is organic. It does not blur which channels to
lean into or pull back from.

## One honest limitation: the baseline

About two-thirds of measured outcome sits in a **baseline**, the portion not explained by
measured paid spend. The LTV model puts it near 67 percent and the conversions model near 69
percent. We want to be direct about this, because it is the model's main limitation, and it is
genuine rather than a defect.

Three things make it credible:

- **It is high-normal for a retention and subscription business.** Spend-only data cannot
  recover organic demand or view-through credit, so a large baseline is expected here.
- **It is engine-agnostic.** We built a second, independent model and ran it on the same data.
  It lands within a couple of points of the same baseline, so the number reflects your data and
  attribution, not one tool's settings.
- **It holds under stress.** Across configurations and on synthetic data where we know the true
  answer, the baseline stays in the same range.

The baseline decomposes into roughly 35 points of genuine organic demand (customers who would
have subscribed without the measured paid channels) and roughly 32 points of paid credit the
spend-only model cannot place on a channel. A meaningful share of that second piece is Meta Web
view-through, which is invisible to a model that sees spend but not the downstream conversions
it drives.

**What the next iteration does about it.** The job ahead is to decode that baseline and
redistribute it onto the channels that actually earned it, bringing it down toward the 25 to 40
percent range. Reaching the lower end requires richer inputs, specifically a view-through or
attributed-revenue feed, not more tuning. The single change that would move the floor is giving
the model the view-through signal it cannot currently see.

## How to use this handover

1. **The dashboard** is the live interface to the model. It carries the full channel ranking and
   a decisioning page. Its pages are Decisioning Summary, Out-of-Time Validation, Methodology,
   and Channel Ranking. Launch it locally with `streamlit run app/dashboard.py`, or open the
   deployed version on Streamlit Cloud.
2. **The companion document** is `deliverables/baseline_engine_findings.md`. It is the
   exhaustive account of what we tested: the engine decision, the baseline trade-off, and why we
   landed where we did. Read it when you need the full reasoning behind any number in this
   summary.

Start with this page for the what. Open the dashboard for the numbers. Read the companion for
the why.
