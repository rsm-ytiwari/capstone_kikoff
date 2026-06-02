# Final Presentation — Draft Script
### Bayesian MMM for Kikoff

**Program:** UC San Diego Rady School · MSBA Capstone × Kikoff
**Status:** Working draft of our final presentation — tone and timing still being refined.
**Speakers (in order):** Yash → Chunjiang → Shivang → Yoko
**Runtime target:** ~15 minutes (11 main slides + intro; A1–A5 are backup for Q&A)

> Shared doc — find your name in the section headers below; your spoken lines live under your blocks. Transition lines are written so each handoff flows straight into the next person's first sentence.

---

## Slide Assignment

| # | Slide | Difficulty | Speaker | Est. |
|---|-------|:--:|---------|:--:|
| 01 | Title — Bayesian MMM for Kikoff | 1 | Yash | 0:20 |
| — | Who are we? (team) | 1 | All (each self-introduces) | 0:50 |
| 02 | The Business Problem — $72M | 2 | Yash | 1:00 |
| 03 | Five ways MMMs typically fail | 3 | Chunjiang | 1:30 |
| 04 | Approach — spend + experiments → decisions | 3 | Chunjiang | 1:20 |
| 05 | How a lift test becomes a prior | 4 | Chunjiang | 1:40 |
| 06 | 5 of 7 channels inside the truth band | 4 | Shivang | 1:40 |
| 07 | Both models inside the 15–25% MAPE band (OOT) | 4 | Shivang | 1:40 |
| 08 | ~33% modeled. The rest, surfaced. | 4 | Shivang | 1:20 |
| 09 | Only Meta Web shows the view-through fingerprint | 5 | Yoko | 1:40 |
| 10 | Decisioning framework — a directional read | 3 | Yoko | 1:20 |
| 11 | Explore the full model output (dashboard) + close | 2 | Yash | 0:50 |
| A1 | Why Bayesian: prior + data → posterior | 4 | any (Q&A) | — |
| A2 | All convergence gates pass | 3 | any (Q&A) | — |

*Rough pacing only — adjust freely in rehearsal. Each person carries one contiguous block so the handoffs stay clean.*

---

## Pre-presentation checklist

- [ ] Dashboard loaded and live in a browser tab (slide 11 ends on it — be ready to click into it if the room wants a closer look).
- [ ] One full run-through of the handoffs out loud — the talk only feels seamless if the name-passes are clean.
- [ ] Everyone knows the three core terms cold: **iCAC** (cost per customer acquired), **lift test** (a real on/off experiment), **MAPE** (average % prediction error). Slide 3's footer defines them on screen — lean on it.
- [ ] Shivang + Yoko: rehearse the two "honest limitation" beats (slide 7 M2 over-prediction; slide 9 TikTok iOS inverse). These are strengths — say them calmly, as evidence of rigor.
- [ ] Backup ready: A1 (why Bayesian) and A2 (diagnostics) for "how do you know it converged?" or "why Bayesian at all?"

---

## Yash — Slides 01–02 + lead the intro (~2 min)

*[Slide 01 — Bayesian MMM for Kikoff]*

Good [morning/afternoon], everyone, and thank you for being here. This is our capstone project with Kikoff: a Bayesian Media Mix Model. In one sentence, the question we set out to answer is — which marketing actually drives Kikoff's growth, and how honestly can we prove it? Before we get into the model, let's quickly introduce ourselves.

*[Slide — Who are we?]*

*(Each person says their own line, left to right on the slide.)*

- **Chunjiang:** Hi, I'm Chunjiang Liu — I led our exploratory analysis and the evaluation framework.
- **Shivang:** I'm Shivang Bhatt. I led channel mapping and ran our client meetings.
- **Yash:** I'm Yash Tiwari — I led project orchestration, the data audit, and client communication.
- **Yoko:** And I'm Yoko He. I led data cleaning and visualization, including the dashboard we'll finish on.

**Yash (continuing):** Let me set up the problem we were asked to solve.

*[Slide 02 — The Business Problem]*

In 2025, Kikoff spent **seventy-two million dollars** on paid customer acquisition, spread across **nineteen** channel-and-platform combinations — Meta, TikTok, Google, connected TV, podcast, and more.

The trouble is that every platform reports its own results, in its own favor, and last-click attribution hands full credit to whoever the customer happened to touch last. So in the dashboards, *every channel looks like a winner.* The question Kikoff genuinely can't answer today is the one on screen: which channels actually **cause** growth — versus which just **look** good in an attribution dashboard but aren't really driving it? Until you can answer that, you can't confidently move a single dollar. The reason that's so hard to answer well is exactly where Chunjiang picks up.

---

## Chunjiang — Slides 03–05 (~4.5 min)

*(Picks up from Yash.)*

> **Before Slide 05 — terms worth setting up for the room:**
> - **iCAC** — incremental cost to acquire one customer. Lower is better.
> - **Lift test** — a real experiment: turn a channel's spend up or down and measure the change in customers. Ground truth, not a dashboard estimate.
> - **Prior** — what we believed *before* seeing the time-series. In our model, the lift test *is* the prior.

*[Slide 03 — Five ways MMMs typically fail]*

Thanks, Yash. Media Mix Models are the standard tool for this question — and they're notoriously easy to get wrong. So we started by naming the five most common ways they fail, on the left, and we built the project specifically to answer each one, on the right.

MMMs tend to overclaim precision with a single number; we report a full range of uncertainty instead. They skip a real held-out test; we ran one on thirteen weeks the model never saw. They model a handful of channels; we modeled all nineteen together. They bury the organic baseline; we broke it out in the open. And they hand-wave saturation; we estimated it per channel. That right-hand column is really the rest of this talk — so let me show you how the model is put together.

*[Slide 04 — From spend and experiments to channel-level decisions]*

Here's the whole model in one picture.

Three things go in: nineteen channels of weekly spend over ninety-three weeks; seven channels' worth of real lift-test experiments — ten tests in all; and the business outcomes that matter, weekly conversions and three-year customer value. Those feed one Bayesian model. And three things come out that leadership can act on: a cost-per-customer and a saturation curve for every channel, a thirteen-week out-of-time prediction, and concrete decisioning recommendations.

The phrase to hold onto is in the model box — *lift tests applied within their test windows.* That idea is the core of our method, so let me make it concrete.

*[Slide 05 — How a lift test becomes a prior]*

This is the heart of the approach, and it's simpler than it sounds.

When Meta ran a lift test on its Web channel — for two weeks in May 2025 — that experiment told us the true cost per customer was about **a hundred fifty-six dollars.** So *inside those two weeks*, we hold the model to the experiment. It isn't allowed to argue with a real test.

*Outside* that window — the other ninety-one weeks — the model is free to learn from the time-series on its own. That's the whole trick: the experiment and the time-series never argue over the same week. Each one speaks where it's strongest. Now — whether that actually lands the model on the experimental truth is the real test, and that's what Shivang will show you.

---

## Shivang — Slides 06–08 (~4.5 min)

*(Picks up from Chunjiang.)*

> **Before Slide 07 — terms worth setting up:**
> - **Truth band** — the lift-test answer, give or take fifty dollars. Land in the band and the model agrees with the experiment.
> - **Out-of-time (OOT)** — hide the most recent weeks, train on the rest, then test on weeks the model has *never seen*.
> - **MAPE** — average percent prediction error; the industry-acceptable band is fifteen to twenty-five percent.

*[Slide 06 — 5 of 7 lift-tested channels land inside the truth band]*

Thanks, Chunjiang. So — does it work? Here's the honest scorecard.

Each gray box is a channel's truth band from its lift test; each dot is what our model produced. **Five of the seven** land squarely inside the band — Meta iOS, Meta Android, TikTok Android, TikTok Web, and CTV. That's the model independently agreeing with five separate real-world experiments.

Two miss, and we show them in yellow rather than hide them — Meta Web sits about seventy-three dollars above its band, and TikTok iOS about a hundred twenty-nine above. We'll come back to *why* Meta Web misses, because it turns out to be the most interesting finding in the project. But first, the question that has to come before any of this: does the model actually predict?

*[Slide 07 — Both models hold inside the 15–25% MAPE band]*

This is the test most MMMs quietly skip, so we ran it head-on.

We trained on seventy-nine weeks — July 2024 through December 2025 — then held out the last thirteen and asked the model to predict them blind. The conversions model came in at **sixteen percent** error, the customer-value model at **fifteen.** Both inside the industry band — for a genuinely held-out test, that's a strong result.

And here's an honest note, because honesty is our theme throughout. The value model runs about fifteen percent high in twelve of those thirteen weeks. We tested two different fixes; both improved one thing and broke another. So instead of forcing a fix that hides the problem elsewhere, we document the bias openly. A known, characterized limitation is worth more than a buried one. Now — where does all of Kikoff's customer value actually come from? Let's take the baseline apart.

*[Slide 08 — ~33% modeled. The rest, surfaced.]*

A lot of MMMs sweep everything they can't explain into one big "baseline" number. We refused to, and split it into three honest pieces.

About **a third** of customer value, our model explains and attributes to channels, anchored to those real experiments. About **35%** is irreducible organic — customers who would have come anyway, genuinely outside what a media model should claim. And the middle piece — about **32%** — is paid impact we *know* we're missing. Most of it is Meta Web view-through: people who saw a Meta ad, didn't click, and converted later. Kikoff's attribution vendor, Northbeam, can see those conversions; our spend inputs can't. We surfaced that gap instead of burying it — and it leaves a very specific fingerprint inside the model, which Yoko will show you.

---

## Yoko — Slides 09–10 (~3 min)

*(Picks up from Shivang.)*

> **Before Slide 09 — terms worth setting up:**
> - **Concentration ratio** — how much more a channel contributes *during* its test window than outside it. High means the experiment "bit"; flat means it didn't move the attribution.
> - **View-through** — a customer *sees* an ad but doesn't click, then converts later. The platform's vendor can see it; raw spend data cannot.

*[Slide 09 — Only Meta Web shows the view-through fingerprint]*

Thanks, Shivang. This chart is where that gap clicks into place.

For each channel, it asks one thing: when the lift test fired, did the channel's contribution actually concentrate into that window? For most channels, yes — Meta iOS more than doubles, so the experiment clearly redistributes attribution to where it belongs. But look at Meta Web, in yellow: **1.04 times** — essentially flat. The lift prior pulled Meta Web's cost-per-customer down from $466 to $276, but it *couldn't* move the attribution into the window. Why not? Because Meta Web's real effect is view-through, and view-through is invisible to the spend data the model sees. That flat bar *is* the in-model signature of the 32% gap Shivang just showed you. And one more honest flag — TikTok iOS sits below one, an inverse pattern that points to campaign pacing, which we document as a separate known limitation. So — how does a marketer actually act on all this? Here's one channel, end to end.

*[Slide 10 — A directional read with confidence]*

This is one of nineteen channel cards — Meta iOS.

We give four reads. The cost-per-customer, $137, sitting right on its lift-test truth of $135. The return, above break-even. The concentration, showing the experiment bit cleanly. And the saturation, showing there's still headroom to spend more. Put together, the recommendation is plain and confidence-rated: **scale modestly — raise weekly spend ten to twenty percent and watch the response.** And to be clear about scope, this is a directional read with stated confidence — not a single optimal-budget number we'd pretend to know to the dollar. Every one of the nineteen channels gets the same honest treatment. And all of it lives somewhere you can actually use — Yash will take you there to close.

---

## Yash — Slide 11 + close (~1 min)

*(Picks up from Yoko.)*

*[Slide 11 — Explore the full model output]*

Thanks, Yoko. Because none of this should live only in slides. Everything you've seen — all nineteen channels, the calibration, the out-of-time validation, the methodology — is live in an interactive dashboard. Scan the code and you can explore it yourself.

As the slide says: the deck is the headline; the dashboard is the work. What we set out to build was honest attribution at scale — five of seven channels validated against real experiments, a model that predicts on weeks it never saw, and every limitation named out loud rather than hidden. Thank you, all of us — and we'd be glad to take your questions.

---

## Appendix (backup — pull only if asked)

*[A1 — Prior + data → posterior]*
If asked *"why Bayesian?"*: a lift test is "what we knew," ninety-three weeks of spend is "what we observed," and combining them gives "what we believe now" — a full probability distribution over each channel's cost-per-customer, with an 89% credible interval, not a single point. The windowed prior is what keeps experiment and time-series from disagreeing about the same weeks.

*[A2 — All convergence gates pass]*
If asked *"how do you know the model is trustworthy?"*: three standard convergence checks all pass on the canonical fit — R-hat 1.005 (the chains agree), effective sample size 2,094 (well above the 400 floor), and zero divergences. The conversions model passes all three as well. These gates pass *before* we trust any number the model reports.
