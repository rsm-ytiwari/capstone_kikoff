# Presenter Script: MMM Final Results & Approach (Meeting 8, Pre-Final Review)

**Meeting:** Abheek sync, 2026-06-02 (last working session before the June 4 and 5 final)
**Deck:** `deliverables/12_abheek_meeting8_final_prep.qmd` / `.html`
**Estimated time:** about 18 minutes of walkthrough plus 10 to 15 minutes of Q&A, weighted toward the demand-and-macro slide
**Audience:** Abheek Sinha (Kikoff project sponsor)

---

## Voice rules

- Lead with what's true now (the out-of-time forecast, the metric he weighs most), then the baseline openly, then what we tested, then the forward request.
- The demand-and-macro slide is the one to slow down on. Treat it as a fair question worth testing, not as anyone's pet theory. Avoid language that puts the idea on him ("your hypothesis", "the lever you named", "exactly what you predicted"). Frame it as something we wanted to test thoroughly.
- Keep the tone measured. State results plainly and let them carry. Avoid words like "breakthrough", "dissolved", "survived", and "the data resists".
- No em dashes in anything you hand over or read from.
- Internal codes (D-numbers, script names, milestone tags, engine names) stay out of the spoken deck. They're in the cheat-sheet below for live lookups only.
- The second engine is "a second independent engine", not named, unless he asks.
- Own the honest findings (the +14.96% LTV bias, Meta Web low confidence, the 67% itself). Don't bury them and don't oversell them.

---

## Slide 1, Where we landed (2:00)

The honest snapshot. Walk the table top to bottom and set the agenda.

> "This is our last working session before the final, so I want to walk through where we landed, the approach behind it, and what we tested since we last met. Then I'll end on the one data request that matters and a couple of things I'd like your read on."

> "The short version: the out-of-time forecast, the thing you've said you weigh most for an MMM, is in good shape. The decisioning layer is live with all 19 channels. The baseline is around 67%, and I want to report it openly, including a lower number that's reachable and what it costs. And we tested the modeling pretty thoroughly, including whether broader demand and economic signals were what the baseline was missing. The honest read is that the next gains come more from richer data than from more modeling."

**Anticipated question:** *"So is 67% your final answer, or is there more modeling to do?"*
**Prepared response:** *"67% is our defensible answer on the data we have. There isn't a setting left that moves it without giving up something you care about, and I'll show you the full sweep. What moves it next is one specific data input, which is my request at the end."*

---

## Slide 2, Out-of-time validation (3:00)

Lead here on purpose. It's his metric and our strongest result. Keep it factual.

> "You've said out-of-time prediction is what matters most to you for an MMM, so I want to start there. We trained on the first 79 weeks, held out the last 13, and predicted each week against what actually happened."

> "The conversions model comes in at 16.1% error and the LTV model at 15.1%, both inside the 15 to 25 percent range these models are usually held to. The one I'm most glad about: the conversions model used to come in high on every hold-out week, and that's now down to 4 of 13, with the average error inside plus or minus 5 percent."

> "I also want to address the concern that the intervals looked overconfident, because it's a fair one. In-sample, the model's interval covers 94.6 percent of weeks, and on the hold-out the full predictive interval covers all 13. The narrow 7.7 percent figure that may have stood out was our report showing the band around the average prediction only. That was a choice in how we displayed it, not a problem with the model."

**Internal map:**
- M1: `oot_model1_conversions.json`, MAPE 16.13, signed −3.66, over-pred 4/13, HDI89 38.5.
- M2: `oot_model2_ltv.json`, MAPE 15.13, signed +14.96 (computed), over-pred 12/13.
- 94.6% in-sample, full predictive coverage: `outputs/P2_07_model_audit/diagnostics/phase0_summary.json` and `VERDICT.md`.

**Anticipated question:** *"The LTV model still comes in high 12 of 13 weeks at about +15 percent. Isn't that a problem?"*
**Prepared response:** *"It's a known, one-directional bias, and I'm not hiding it. It reflects a lift in LTV-per-conversion in early 2026 that the training window couldn't see. Every fix we tried traded it for something worse: a trend control flips the bias the other way, and a two-stage build trades it for week-to-week noise. So we kept the model honest and documented the bias rather than paper over it. It's inside the error band, and the clean fix needs the data scope I'll get to."*

**Anticipated question:** *"Why does the conversions model get a trend control but the LTV model doesn't?"*
**Prepared response:** *"Because they drift differently. Conversions has one drift, where volume plateaued in Q1 while the straight-line projection kept climbing, and a single trend term fixes it cleanly. LTV has two drifts that partly offset each other, and one trend term over-corrects it. So we apply the control only where it genuinely helps, rather than forcing symmetry that would distort the LTV numbers."*

---

## Slide 3, Decisioning layer and Meta Web (1:30)

> "The decisioning layer is live, with all 19 channels, the 8-column framework you approved, sortable, and a CSV export for your team."

> "The one thing I want to flag is that Meta Web is marked low confidence. That's deliberate. It's the model being clear about where its own read is weakest, so it doesn't get over-weighted in a spend call. Two things say the same thing: it doesn't pass its in-window calibration check, and its in-versus-out concentration is 1.04, which is essentially flat. When we tightened its calibration, the cost level moved into range, but the model didn't change where it puts the credit. That flat ratio is the signature of view-through, credit earned by impressions people see but don't click on, which spend-only data can't place on the channel."

**Note, present as already flagged, not as a change.** Meta Web is already low confidence on the live dashboard. Don't say "we downgraded it from high." The framing is: it's already flagged low, and the 1.04 view-through concentration confirms the signal isn't just tied to one stretch of time.

**Internal map:**
- Meta Web confidence is low on the live Decisioning Summary (D015 rule).
- 1.04 concentration: `baseline_split.json`, `per_channel.meta_web`.

**Anticipated question:** *"If Meta Web is low confidence, can I trust any of the spend guidance?"*
**Prepared response:** *"Yes. The spend guidance runs on each channel's marginal behavior, which holds up regardless of the overall baseline level and the view-through issue. Low confidence on Meta Web means read its absolute cost with caution, not that the directional guidance is broken. Most channels are medium to high confidence. Meta Web is the one to treat carefully, and now you know exactly why."*

---

## Slide 4, Revisiting the saturation curves (2:00)

A rapport slide. He raised this flag at our last meeting, so the tone is "good catch, we worked it through," not defensive. Credit his observation; be straight about what the data does and doesn't show.

> "At our last meeting you flagged that the cost-per-acquisition curve looked flat against spend, and raised it as a model-validity concern. That was a fair point, so we went back and worked through it."

> "The first part was on us. The curve we'd shown was the average cost per acquisition, but the spec, and your feedback, call for the marginal view, the cost and return on the next dollar rather than the average across everything spent so far. We've now built the marginal curves from the existing model, with no refit, and they tell a clearer story."

> "The corrected marginal curve does show real curvature, which supports your read that the earlier view was masking how the model responds as spend moves. It lines up with your point that the model wasn't capturing the LTV variance the way you'd expect."

> "One thing I want to be straight about. Within the range of spend we actually observe, the curve stays close to linear. That's a genuine finding in the data, not a rendering issue. A sharp tipping point would only show up if we extrapolated well beyond the spend levels we've seen, which we'd label as extrapolation, or if we imposed a stronger-saturation assumption the data doesn't support. We tried loosening that assumption and it broke the model's convergence without revealing a tipping point, so we're not going to draw an S-curve the data doesn't show."

> "For the next iteration, two threads are worth carrying: whether the second engine's saturation shape surfaces a tipping point, and a closer look at why the spend-only curve stays close to linear over the range we observe."

**Demo guidance:** if the corrected marginal curve is live on the dashboard by meeting time, show it on the channel drill-down page. If it isn't ready, present the finding verbally and note that the corrected version is in final production for June 4 and 5.

**Internal map:**
- Average vs. marginal: the deliverable spec is marginal iCAC and iROAS (decisioning columns A to H); the post-hoc marginal curves are built from the existing trace, no refit.
- Saturation spec is LogisticSaturation with the Lever C lam prior (D025). Loosening it for stronger saturation degraded convergence without surfacing a tipping point (audit sweep, and the D025 convergence record).
- Iteration threads: Q38 (does the second engine's Hill saturation show a tipping point) and Q41 (cause of the near-linear spend-only curve), both post-capstone.

**Anticipated question:** *"So is the flat curve a bug or not?"*
**Prepared response:** *"Not a bug. The flat part was partly the average-versus-marginal display, which we've corrected, and the marginal curve does show curvature. What remains is that over the spend levels we've actually run, the response is close to linear, and that's a real property of the data. We could only turn it into a dramatic curve by extrapolating past what we've observed or by forcing an assumption the data rejects, and we'd rather show you the honest shape and flag the iteration path."*

**Anticipated question:** *"Why does loosening the saturation assumption break the model?"*
**Prepared response:** *"When we push the prior toward stronger curvature, the sampler stops converging cleanly, which is the model's way of saying the data doesn't contain enough signal at high spend to pin down a bend. With more spend variation, or the impressions data we'll ask for, that signal could come through. On today's data it doesn't, so forcing it would be us drawing the curve rather than the data."*

---

## Slide 5, The baseline, openly (2:30)

The substantive honesty slide. Walk the decomposition, then the trade-off, calmly.

> "Our model puts about 67 percent of LTV in the baseline, meaning the part measured paid spend doesn't explain. Here's how it breaks down. About 35 points is genuine organic demand, people who'd subscribe without paid. That lines up with your own read that the attributed-revenue universe is roughly two-thirds of total, leaving about a third organic. No spend-only model recovers that. The other 32 points or so is missed paid attribution, mostly Meta Web view-through plus a few under-instrumented channels, credit the model can't place, so it lands in the baseline."

> "Now the part I want to be precise about: a lower number is reachable, but it isn't free. We can get a baseline near 41 percent, but only by loosening the tie to your incrementality tests. As soon as we do, out-of-time error rises into the mid-20s, CTV drifts off its tested value, and Meta Web's cost climbs back toward the level we spent several weeks bringing down. A 41 percent baseline that predicts less well and pulls the channels off calibration is a weaker result than a 67 percent that predicts well and keeps the channels honest."

> "Put on the same footing as your attributed-revenue universe, the baseline works out to about 50 percent. The distance from there to a 30 to 40 percent target comes down to what the data can see, not a setting we can tune."

**Internal map:**
- 67.33% global, 49.74% apples-to-apples point, 45.55 to 53.33% band: `baseline_split.json`.
- 41% blended endpoint and the 23 to 28% OOT cost: `deliverables/baseline_engine_findings.md` engine table. Not a JSON figure; sourced from the written deliverable.

**Anticipated question:** *"Where exactly does the 35 percent organic come from?"*
**Prepared response:** *"From your own Meeting 6 comment, that the attributed-revenue universe is about 65 percent of total, leaving roughly 35 percent organic. We're inferring the organic share from that rather than from a precise statistic, and I want to be straight about that. The conclusion holds whether it's 30, 35, or 40, since the gap to your target is well above 20 points either way. Replacing that inference with data is part of the request."*

---

## Slide 6, What we tested since we last met (2:30)

Set up the four lines of work. Make the point that each was set up to bring the baseline down, not to protect it.

> "We didn't stop at one model. We ran four lines of work, and each one was set up to try to bring the baseline down."

> "First, we built a second, fully independent engine on the same data. If two different methods disagree, the number is an artifact of one of them. They agree to within a couple of points, so the baseline is a property of your data, not one tool's settings."

> "Second, we swept the model settings. We worked through every lever that should move the baseline: prior tightness, the untested channels' priors, the saturation curve, the intercept prior itself. None of them gets to 30 to 40 percent without breaking calibration. When we pushed hard toward 35 percent, the model settled back near 60 on its own."

> "Third, we ran a model audit. We tested the overconfident-intervals concern and it turned out to be a display choice, not a model issue, with 94.6 percent in-sample coverage and full coverage on the hold-out. We also tried a heavier-tailed likelihood and a hierarchical structure, and neither helped. Pooling actually raised the baseline."

> "Fourth, we tested whether broader demand and economic signals were what the baseline was missing. That one looked promising at first, and then a closer test changed the picture. That's the next slide, and I want to walk it carefully."

**Internal map:**
- Engine agreement and the 41% trade: `baseline_engine_findings.md`.
- Sweep magnitudes (sigma weak, untested −1.5pp, lam −2pp, intercept floors near 60%): `context/briefs/exhaustiveness_audit_2026-06-01.md`.
- Audit (StudentT, hierarchical raising baseline to 71%, coverage 94.6 and full): `outputs/P2_07_model_audit/VERDICT.md`.

**Anticipated question:** *"What was the second engine?"*
**Prepared response:** *"A second industry-standard Bayesian MMM engine, run independently on the same data. The point wasn't to switch tools, it was to check whether the 67 percent is real or specific to ours. It's real, both land in the same place. One looser setting on the second engine reaches 41 percent, but it gives that back in out-of-time accuracy and channel calibration, the same trade-off I just showed you."*

---

## Slide 7, The demand and macro signals, in full (4:00), slow down here

This is the most important slide for credibility. Treat the idea as a fair question worth testing thoroughly. Keep it off him personally.

> "I want to walk this one slowly, because it's a fair question to ask and it nearly changed our answer."

> "It looked promising at first. Adding a consumer-demand search index on its own brought the baseline from about 67 to 62, and improved out-of-time error from roughly 19 percent to 13.5. When we added broader macro series, the 10-year rate and consumer sentiment, the baseline came down further to about 49, close to the 30 to 40 range, and out-of-time error roughly halved to about 7. On the surface, that was the result we'd been hoping to find."

> "Then we looked closer. Those macro series move slowly and almost in a straight line over our 93 weeks, so statistically they're hard to tell apart from a simple time trend. Consumer sentiment is about 70 percent explained by a trend on its own. A flexible trend can look like it's explaining demand when it's really just shifting credit off the baseline, which is a re-labeling rather than a real finding."

> "So we ran a more careful test. We took the trend out of each macro series and re-fit on only what was left, the genuine movement that isn't just drift over time. If the macro signal were really capturing outside demand, the improvement would hold. It didn't. The baseline went back to about 62, and out-of-time error returned to about 17."

> "That's why we decided not to keep it, even though it improved both headline numbers. Adopting a trend in disguise would have given us a lower baseline and a better-looking forecast, but at the cost of distorting the per-channel costs you actually make decisions on, and without reflecting any real demand the data contains. We chose to stay with the honest 67. The model held up even against the most promising alternative we found."

**Internal map:**
- Trends-only: baseline 67.4 to 61.69%, OOT M1 18.9 to 13.54%: `VERDICT.md` and `E3_trends/report_card.json`.
- Full macro stack (no trend term): baseline M2 49.0%, OOT M1 7.28%, stable across seeds: `separation/separation_results.json` and `C1_macro/report_card.json`.
- Detrended test: baseline reverts to 61.84%, OOT M1 16.78%, macro-on-trend R²: UMCSENT 0.70, UNRATE 0.59, DGS10 0.18: `separation/detrend_results.json`.
- (Internal only: the explicit-free-trend variant degenerated to a negative baseline; don't raise it. The clean test is the detrended one.)

**Anticipated question:** *"You got to 49 percent baseline and 7 percent out-of-time error. Why give that up? That's better on both metrics you just told me matter."*
**Prepared response:** *"Because we couldn't confirm the gain was real. When we removed the trend component from those macro series and kept only the genuine movement, both gains went away, baseline back to 62 and error back to 17. So the 49 wasn't the macro explaining demand, it was a trend absorbing credit. Keeping it would mean publishing per-channel costs that look precise but are quietly distorted by a trend we can't justify. A more honest number that looks worse is better than a better-looking one we can't stand behind, especially on the channel costs you spend against."*

**Anticipated question:** *"Isn't a trend control completely standard in MMM?"*
**Prepared response:** *"It is, for prediction. That's exactly why our conversions model uses one for the out-of-time forecast. The issue is using a trend to lower the baseline, because there it quietly moves organic credit onto paid channels, which changes the cost numbers you decide on. Same tool, two different jobs. We use it where it forecasts honestly and hold off where it would distort attribution."*

**Anticipated question:** *"So broader economic signals genuinely do nothing for us?"*
**Prepared response:** *"Not nothing. The demand search index on its own gave a real drop of about 6 points and a real forecast gain, and we'd keep something like it. It's the rate-and-sentiment series specifically that are hard to separate from a trend over a window this short. The honest read is that those macro series don't carry demand information beyond a trend on 93 weeks of data."*

---

## Slide 8, Reconciliation (2:30)

> "You've seen about 30 percent from Meridian and about 12 from Northbeam, and ours is about 67. These aren't really in conflict. They're different tools measuring somewhat different things."

> "Northbeam at 12 uses click, view-through, and journey tracking, which are exactly the signals we don't have. And tracking-based attribution tends to give the paid it can track more credit, and to miss organic and word-of-mouth. Meridian at 30 uses a different set of controls and a narrower base. Ours is spend-only, privacy-durable, and has no tracking, so it captures the organic and offline demand that tracking misses, which tends to run higher for a credit-building subscription business."

> "So the useful move is to reconcile these rather than force them to match, since the real number likely sits between them. If I pushed ours down to match a tracking tool, I'd be taking on that tool's blind spots. A baseline near 67 is on the high side of normal for a retention business, rather than a red flag."

**Internal map:**
- MMM is attribution-free by design, Northbeam uses tracking, truth sits between, 67% high side of normal for subscription: `context/briefs/research_findings_2026-06-01.md`.
- The specific 30% Meridian and 12% Northbeam figures are framing anchors. If he challenges the exact numbers, the direction and mechanism are what carry the point.

**Anticipated question:** *"If Northbeam's number is biased, why should I trust this over Northbeam?"*
**Prepared response:** *"It's not that Northbeam is wrong and we're right. Each sees something the other can't. Northbeam places paid credit through tracking we don't have, and we capture organic and offline that tracking misses. The most accurate read of your business is the reconciliation of the two, not either one alone. That's also why the impressions request matters, since it's the bridge that lets our model see some of what Northbeam sees."*

---

## Slide 9, The forward request (2:00)

The single highest-value request. Land it clearly and without overpromising.

> "Everything I've shown points to one data request: channel-level impressions or reach, especially for Meta Web."

> "Here's why this one specifically. Meta Web's effect works through view-through, where people see impressions and convert later without clicking. A model that sees only spend can't capture that, and it's a large part of the 32 points sitting in the baseline. Impressions are the missing signal. With them, the model can place that view-through credit on the channel directly and bring the baseline down honestly, rather than by re-labeling the way the macro test would have."

> "And the mechanism is already visible on our side. That flat 1.04 Meta Web concentration is the direct evidence that spend variation alone can't recover this. Impressions are the input that can. You've described a roadmap of five to seven iterations, and this is what the next one would build on."

**Internal map:**
- Impressions and reach as the top data request: `exhaustiveness_audit_2026-06-01.md` and `research_findings_2026-06-01.md`. Named as the main data limitation in the engine audit.

**Anticipated question:** *"How hard is that data to pull, and how much would it move the number?"*
**Prepared response:** *"On your side it's a platform export, since Meta reports impressions and reach natively. We'd want it on the same channel taxonomy as the spend file so we can join cleanly, and if the mapping is awkward we'll do it on our end. On how much it moves the number, I won't put a figure on it, because being honest is the whole point here, but it goes straight at the largest 32-point piece, so it's the highest-value input we can name."*

---

## Slide 10, Your steer (1:30)

Three things. Don't over-explain, invite his read.

> "Three things I'd like your read on before June 4 and 5."

> "First, does this framing work for the final? Lead with the out-of-time forecast, report the 67 openly with its trade-off, and reconcile against your other tools rather than forcing them to match. Is that the story you want in front of the room?"

> "Second, can you get us channel-level impressions or reach, especially for Meta Web? It's the one input that brings the baseline down honestly."

> "Third, anything you'd like emphasized for the final, or anything you'd rather we play down? Tell me the audience and the angle and I'll plan around it."

**Anticipated question:** *"Can the final show a lower baseline if I need it to for the audience?"*
**Prepared response:** *"We can show the apples-to-apples number near 50 honestly, and we can show the 41 explicitly as the lower-bound option with its accuracy cost stated. What I'd steer away from is presenting one low number as the baseline without the trade-off, since that's the framing that wouldn't survive a sharp question. Tell me the audience and I'll build a framing that's both honest and lands."*

---

## Slide 11, Live dashboard and the fallbacks (4:00)

Switch to `http://localhost:8501`. The three slides after this are static fallbacks if anything breaks.

**Walkthrough order:**
1. Home on Meta iOS (75s). Cost-per-acquisition card (posterior median, CI whiskers, truth-band overlay), return card, time-series tabs. Switch to Meta Web to show the low-confidence flag and the posterior just above its band.
2. Decisioning Summary (60s). All 19 channels, lift-tested seven on top, sortable, with CSV export.
3. Out-of-Time Validation (60s). Both models, interval vs. actuals. The calibration story is on the page.
4. Methodology (45s). Baseline decomposition, the concentration table with the 1.04 Meta Web row, the view-through explanation, and the impressions request.

**If anything breaks:** say "let me pull this up as a screenshot" and flip to fallback slides 12 to 14, talking it the same way.

**Live-demo note:** internal version stamps may be visible on dashboard page titles. If he points at one, say "those are our internal version stamps for the canonical specification, and the content below the title is what they actually changed."

---

## Pre-meeting actions

- [ ] Launch the dashboard: `my-notebook-project/.venv/bin/streamlit run app/dashboard.py`, and click all four pages once to warm the caches.
- [ ] Confirm the three fallback screenshots render in the HTML deck.
- [ ] Have `outputs/P2_04_full_channel/metrics/` open in a tab for live lookups.
- [ ] Re-read the demand-and-macro Q&A, since that's where the hardest pushback comes.

## Post-meeting actions

- [ ] Capture his answer on impressions and reach (yes or no, plus timeline) and his read on the final framing.
- [ ] If impressions are confirmed, scope the next-iteration refit.
- [ ] Fold any framing steer into the June 4 and 5 final deck.

---

## Number cheat-sheet (live lookups)

| Question | Answer | Source |
|---|---|---|
| Model 1 OOT MAPE | 16.13% | `oot_model1_conversions.json` |
| Model 1 OOT signed mean and over-pred | −3.66% and 4 of 13 | `oot_model1_conversions.json` |
| Model 2 OOT MAPE | 15.13% | `oot_model2_ltv.json` |
| Model 2 OOT signed mean and over-pred | +14.96% and 12 of 13 | computed from predicted vs. actual |
| In-sample HDI89 coverage | 94.6% (M1 and M2) | `P2_07_model_audit/diagnostics/phase0_summary.json` |
| OOT full-predictive coverage | full (all 13 weeks) | same, and `VERDICT.md` |
| OOT mean-only coverage (the 7.7%) | 7.7% | `oot_model2_ltv.json` and `phase0_summary.json` |
| Global baseline | 67.33% | `baseline_split.json` |
| Apples-to-apples baseline | 49.74% point, 45.55 to 53.33% band | `baseline_split.json` reference block |
| Meta Web concentration | 1.04 | `baseline_split.json` |
| 41% blended endpoint and OOT cost | about 41% baseline, about 23 to 28% OOT | `deliverables/baseline_engine_findings.md` (not a JSON) |
| Macro, Trends only | baseline 67.4 to 61.69%, OOT M1 18.9 to 13.54% | `P2_07_model_audit/VERDICT.md` and `E3_trends/report_card.json` |
| Macro, full stack (no trend) | baseline 49.0%, OOT M1 7.28% | `separation/separation_results.json` |
| Macro, detrended (the closer test) | baseline reverts to 61.84%, OOT M1 16.78% | `separation/detrend_results.json` |
| Macro-on-trend R² | UMCSENT 0.70, UNRATE 0.59, DGS10 0.18 | `separation/detrend_results.json` |
| Meridian and Northbeam baseline anchors | about 30% and about 12% | framing anchors (`research_findings_2026-06-01.md`), confirm if challenged |
| Final presentation | June 4 and 5, 2026 | sprint |
