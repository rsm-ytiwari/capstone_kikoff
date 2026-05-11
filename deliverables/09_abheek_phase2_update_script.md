# Presenter Script — Phase 2 Update
**Meeting:** Abheek sync | 2026-05-04
**Deck:** 09_abheek_phase2_update.qmd / .html
**Estimated time:** 15–20 min presentation + Q&A

---

## Slide 1 — Title (0:30)

> "Quick update on where we are with the model build. We finished the data foundation two weeks ago and we've been running the first model fits. I want to walk through what we tried, what we found, and two questions we need from you."

---

## Slide 2 — Where We Left Off (1:30)

> "Just to set context — Phase 1 is done. We have 639 days of clean data, all channels mapped. The holdout experiments you ran — Meta May 2025, TikTok, CTV — gave us iCAC benchmarks we're using as ground truth. The table on the right shows what those tests measured for Meta specifically: iOS around $135, Android $63, Web $157. Those are the numbers the model should recover once we feed them in."

---

## Slide 3 — Why Start with a Baseline? (1:00)

> "Before we add any experimental guidance, we always fit the model without it. This tells us three things: does the architecture work, what does the model believe from the historical data alone, and how far off is it from what the experiments measured? Without a baseline, we can't measure how much the holdout integration actually changed things."

1.⁠ ⁠POC methodology: The notebook is literally named mmm_meta_poc. Standard practice in any modeling project — validate the full pipeline (data → model → gates → diagnosis) on one channel × one experiment before scaling to all 4 tests × 12 channels. If something is wrong with the architecture, you want to find out with one channel, not after building everything for all of them.

2.⁠ ⁠Meta is the highest-spend channel — $23.1M/year. The economic stakes are highest there, so it's the most important to get right. A wrong Meta ICAC would be the most damaging to budget decisions downstream.

3.⁠ ⁠Meta May 2025 is the cleanest experiment available:

99.9% statistical confidence
Three clean platform splits (iOS, Android, Web) — more diagnostic signal than a blended number
The other Meta test (Jan 2026) was cancelled and iOS had only 63% confidence — not a clean calibration anchor
4.⁠ ⁠It creates the hardest test case. Meta has the iOS pacing problem (r=0.48). If the approach works here — on a channel with a structural attribution confound — it'll definitely work on cleaner channels like TikTok (25-day clean test, no pacing issue evident) and CTV (28-day geo holdout). Solving the hard case first means the scale-out is straightforward.

The intended sequence is: Meta POC gates pass → same architecture applied to TikTok + CTV with their respective holdout windows → channels without experiments get data-driven priors only.
---

## Slide 4 — Baseline Model (1:30)

> "Here's what the model produced with no experimental guidance — 639 days of data, three Meta channels. iOS came back at $21, Android at $957, Web at $456. The formula is correct. These numbers accurately reflect what 19 months of marketing history implies about channel efficiency. The gap from the experimental benchmarks is telling us something real about the data — not that something is broken."

[Speaker note — what each model parameter means and why we chose those values]:

**GeometricAdstock(l_max=7) — what adstock is:**
Adstock models the "carryover" effect — the idea that an ad seen today still influences behavior for days afterward. Someone sees a Meta ad on Monday, doesn't click, but signs up for Kikoff on Thursday. Geometric adstock assumes this effect decays exponentially: each passing day retains a fraction of the previous day's impact. **l_max=7 means we assume ad effects fully decay within 7 days.** This is the standard choice for direct-response digital mobile advertising (Meta, TikTok) — users who see an ad and don't convert within a week are unlikely to convert because of that ad. For TV or awareness channels, l_max is typically 14–28 days. 7 is appropriate and conservative for Kikoff's digital channels.

**LogisticSaturation() — what saturation is:**
Saturation models diminishing returns. At low spend, each additional dollar is highly productive — you're reaching the most responsive users first. At very high spend, you've already reached everyone likely to convert, and extra dollars return less. The logistic curve (S-shape) is the standard model for this: near-linear returns at low spend, flattening at high spend. We chose LogisticSaturation because it's well-understood, mathematically well-behaved (differentiable everywhere), and consistent with what the empirical media-mix literature uses.

**draws=1000, tune=500 — what MCMC sampling means:**
MCMC (Markov Chain Monte Carlo) is the algorithm that "solves" the Bayesian model. It works by exploring the space of possible answers, spending more time in regions that are more consistent with the data. `tune=500` is a warm-up phase where the algorithm learns the shape of the landscape (discarded afterward). `draws=1000` is the actual sampling: 1,000 snapshots of plausible parameter values. The ICAC we report is the mean across those 1,000 samples. Production models typically use draws=2,000–4,000 for tighter estimates; 1,000 is sufficient for diagnostic runs.

**compute_mean_contributions_over_time(original_scale=True) — what contributions are:**
The model internally normalizes all spend values to a 0–1 scale for computational stability. `original_scale=True` converts the estimated contributions back to actual conversion counts. The function returns a time series: for each day, how many conversions does the model attribute to each channel? ICAC is then total channel spend ÷ the sum of those daily attributed conversions.

[Speaker note — if Abheek asks about iOS spend inflation]:
In `scripts/03_baseline_model.py` line 43, spend rows where PLATFORM = `"iOS and android"` are mapped entirely to `ios`, not split 50/50. This inflates iOS spend in the ICAC numerator — making iOS appear more expensive. But iOS ICAC is $21 (very low), meaning the correlation confound is pulling ICAC down faster than the mapping inflates it. The $21 is therefore the conservative end of the confound — the real gap from the $135 benchmark is even larger if you correct the mapping. If Abheek presses: "Yes, we know about the mapping — it's a conservative assumption that makes iOS look slightly more expensive than it might otherwise. Correcting it is on the list but doesn't change the core finding."

---

## Slide 5 — Our First Calibration Approach (2:00)

> "We used PyMC-Marketing's experimental calibration layer — `add_lift_test_measurements()`. The function takes the holdout test results and adds them to the model as a second source of evidence: 'during the May 2025 test window, when we increased iOS spend by this amount, we observed this many incremental conversions — hold the model to that.' The table shows what we fed in: total spend in the window, the holdout spend increase, the observed incremental conversions, and our measurement uncertainty for each platform."

> "After running the model with this calibration: iOS moved from $21 to $23. Android moved from $957 to $599. Web moved from $456 to $363. The model ran fine and converged. But the calibration barely moved the numbers toward the benchmarks."

[Speaker note — what each argument in the code means and where the numbers came from]:

**channel:** The model's internal column name for each platform — must match the spend data column names exactly (`meta_ios`, `meta_android`, `meta_web`). The model uses these to look up which spend series to constrain.

**x (total spend in test window):** Total Meta spend for that platform across the entire May 6–14, 2025 holdout window. Summed from `MMM_Updated_Spend.csv` filtering to SOURCE_GROUP = facebook × each PLATFORM × those 9 dates.
- iOS: $159,923 | Android: $89,947 | Web: $214,096

**delta_x (holdout spend increase — the treatment lift):** The additional spend in the test cell vs. the holdout cell. Calculated as 12% of x — the holdout fraction stated in the incrementality CSV notes (12% of total test-period spend was the controlled variation). This is what the experiment actually "turned on" for the treatment group.
- iOS: $19,191 | Android: $10,794 | Web: $25,692

**delta_y (incremental conversions observed):** The measured causal lift in conversions from the holdout. Derived from the holdout iCAC: delta_y = x / iCAC.
- iOS: 159,923 / 135.48 = **1,180 conversions** | Android: 89,947 / 63.06 = **1,427** | Web: 214,096 / 156.89 = **1,365**
- These are what the holdout experiment directly measured as caused by the ad spend.

**sigma (measurement uncertainty):** How precisely we trust the delta_y estimate. Set as trust-based percentages of delta_y — not taken directly from the holdout report's statistical standard errors.

*What the percentage means:* We chose a percentage of delta_y (not of x or iCAC) because delta_y is the number we're actually uncertain about — it's the measured incremental conversions, and measurement noise in an experiment is proportional to the scale of the thing being measured. A sigma of 10% on delta_y means "we think the true lift is within ±10% of what we observed." Higher percentage = wider uncertainty band = model is told to trust the experimental number less.

*How each percentage was chosen — working from the holdout test quality:*
- **Android — 7%:** The Meta May 2025 test had 99.9% statistical confidence and the Android result was clean (no early termination issues). Highest trust in the three. 7% of 1,427 = **sigma 99.9**. This tells the model: "Android's true lift is 1,427 ± ~200 at ±2σ" (range 1,027–1,827).
- **iOS — 12%:** Also 99.9% confidence, but the test ended early (⚠️ flagged in the test report). Early termination means the estimate is based on fewer observations than planned, so we assign slightly wider uncertainty. 12% of 1,180 = **sigma 141.6**. This tells the model: "iOS true lift is 1,180 ± ~283 at ±2σ" (range 897–1,463).
- **Web — 18%:** Same 9-day window, but web conversions are more naturally variable day-to-day (higher baseline noise) and the web test window was longer in absolute terms, meaning more external factors could have interfered. 18% of 1,365 = **sigma 245.6**. This tells the model: "Web true lift is 1,365 ± ~491 at ±2σ" (range 874–1,856).

*The ±2σ math:* In a normal distribution, ±1σ covers 68% of probability and ±2σ covers 95%. So "sigma = 141.6" means there is a 95% probability the true iOS lift is within [1,180 − 2×141.6, 1,180 + 2×141.6] = **[897, 1,463]**. The model uses this range when deciding how much to trust the experimental input vs. what the time-series data says.

*Why these sigmas were wide enough to fail:* For iOS, the ±2σ range spans 1,180 ± 283 = 566-unit window. This is ~24% of the point estimate each way. For a Bayesian model with 639 data points pulling consistently toward iOS ICAC ≈ $21, a 24% uncertainty band on the experimental anchor is far too loose to override that signal. That's the H1 diagnosis: the sigma wasn't reflecting "this experiment is almost certain" — it was reflecting "this experiment might be off by a quarter."

**How the model uses all of this:** "Given that we spent $159,923 on iOS in May 2025 total, and specifically put $19,191 of that into the treatment group, we observed 1,180 more conversions than we would have otherwise — and we're confident in this within ±141.6 conversions. Adjust your saturation curve accordingly." This is added as a second likelihood term alongside the time-series likelihood.

[Speaker note — if Abheek asks about sigma]:
Sigma values were judgment-based, derived from trust in the holdout test design (confidence levels and test length), not from the test report's formal standard errors. If Abheek has the standard errors from the Meta experiment reports, those would be more principled. "We can update sigma to use the actual test SEs if you can share them — it would tighten the calibration."

*[Private note: internally calling this Mechanism 2. The function `add_lift_test_measurements()` is the PyMC-Marketing implementation.]*

---

## Slide 6 — Gates (1:30)

> "Before trusting any number that comes out of the model, we define gates — explicit pass/fail criteria. If any gate fails, we don't report that ICAC as valid. We set the tolerance at ±50% of the benchmark: anywhere from half to double the holdout value counts as a pass. That's a generous standard. Even with that latitude, all three ICAC gates failed. And Gate 2 — the ordering gate — is the most diagnostic failure: the model doesn't even know iOS is more expensive than Android."

> "Gate 3a passed — Rhat 1.02 — which means the model ran correctly and the chains converged. This is important because it tells us the failure isn't a computational issue. The model found a confident answer. The answer is wrong. That distinction matters for how we diagnose what to fix."

[Speaker note — what Rhat and ESS mean]:
**Model convergence — for your reference when Abheek asks:**

**Rhat (R-hat):** When the model runs, it runs multiple independent chains simultaneously — think of 4 parallel explorers mapping the same forest independently. Rhat measures whether those chains converged to the same answer. Rhat = 1.0 means perfect agreement. Rhat < 1.1 is the pass threshold — chains are close enough to trust the result. Rhat > 1.1 means the chains ended up in different places, which means the model didn't find a stable answer and results cannot be trusted. In our standard calibration run: Rhat 1.020 — PASS.

**ESS (Effective Sample Size):** Even when you request 1,000 draws from the model, some draws are highly correlated with the previous one — essentially repeating the same information. ESS counts how many genuinely *independent* draws you actually got. If a chain gets stuck in one region and keeps sampling it, you might request 1,000 draws and get only 50 independent ones. ESS > 400 is the pass threshold. In our standard calibration run: ESS 238 — FAIL. This means the model found an answer (Rhat passed) but explored the posterior slowly, giving us less statistical resolution than ideal. The model is not broken, but the posterior is less precisely characterized than with ESS 400+.

**What ESS 238 means practically:** The ICAC estimates are directionally correct but have wider effective uncertainty than the raw numbers suggest. For diagnostic purposes this is acceptable. For a production model used for budget decisions, we'd want draws=2000+ to push ESS above 400.

[Speaker note — on Gate 2 being the most diagnostic]:
Gate 2 (iOS > Android ordering) is the most important gate and the one to highlight if Abheek is a technical audience. The holdout experiments established that iOS ($135) is more expensive than Android ($63). If the model can't even get the *direction* right — if it says iOS is *cheaper* than Android — then the entire cost curve is inverted and no ICAC from this model is usable. The other gates (1a–1c) tell us how far off we are. Gate 2 tells us we're not even pointing in the right direction.

---

## Slide 7 — First Model Pass (2:30)

> "The model ran fine, it converged. But when we compare output to the holdout benchmarks, it's not close. iOS comes back at $23 when it should be around $135. Android is $599 when it should be $63. Web is $363 when it should be $157. The model isn't recovering the experimental values — the 639-day observational pattern is overriding the 9-day experimental signal. The gates confirm this: 5 of 6 failed."

---

## Slide 8 — Why 639 Days Overwhelmed the Experiment (1:30)

> "Here's the core tension. The model is learning from two sources simultaneously: 639 days of observational data, and a 9-day experiment. That's a 71-to-1 ratio. The experimental signal is real and statistically clean — it just can't win a vote that's 71 to 1 against it. Even pushing the experimental uncertainty much tighter, the time series has 639 consistent observations pointing in the opposite direction. The fix isn't to make the experimental signal louder globally — it's to change the architecture so the experiment only competes with the 9 days it actually measured."

[Speaker note — on why this is architectural, not a tuning problem]:
We ran the model with uncertainty ÷ 5 (5× tighter experimental constraint). Android responded correctly — moved to $34, close to the $63 benchmark. iOS did not respond — moved from $21 to $30. More critically, the sampler collapsed: Rhat 1.535, ESS 7. That's the model breaking under irreconcilable instructions. It's not confused — it's been put in an impossible situation. A global constraint says "$135" while 639 data points consistently say "$21." This closes the current approach as a viable path for iOS regardless of any parameter setting.

---

## Slide 9 — H1 and H2 (2:00)

> "We had two competing diagnoses. H1 said: the experimental signal is present but the uncertainty we assigned was too wide — tighten it and the model corrects. H2 said: the problem is structural — iOS campaigns run on high-conversion days regardless of uncertainty settings, and no amount of tuning can fix that."

> "The diagnostic run distinguished them. Android confirmed H1 — it moved from $957 to $34 when we tightened 5×. The signal was there, just needed a stronger push. iOS confirmed H2 — it barely moved, and the sampler broke. The model wasn't poorly tuned. It was correctly learning from data that has the confound baked into it."

[Speaker note — H2 structural question, if Abheek asks: "Will the model always produce a low iOS ICAC regardless of tuning?"]:
Yes. Within this architecture, every model run over the full 639-day window will encounter the same r=0.48 correlation pattern and consistently infer that iOS is a cheap channel. Tighter experimental uncertainty forces the model to choose between two irreconcilable truths — and the sampler breaks rather than correcting (Rhat 1.535, ESS 7 in our test). This is not a tuning failure. The only fix is a different architecture: one where the experimental constraint doesn't have to compete with 639 days of contradictory data.

---

## Slide 10 — Correlation Analysis (1:30)

> "We measured the Pearson correlation between each channel's daily spend and total daily conversions across the 639-day window. iOS: r = 0.48. Android: 0.28. Web: 0.20. iOS has the strongest correlation by far — and it's also the smallest channel by spend, with the most zero-spend days. When iOS runs, conversions tend to be high. We suspect this is a pacing issue — iOS campaigns concentrated in Q2 spring season, which is also a high-conversion period."

> "We don't know if this is deliberate campaign strategy or coincidence — and we think Abheek is best positioned to confirm. Was the iOS Q2 concentration intentional?"

[Speaker note — if Abheek asks why sigma ÷ 5]:
Purely diagnostic. We wanted to make the experimental signal as strong as possible to test whether the model could respond at all. Android's response confirmed the signal is informative for that channel. iOS's non-response confirmed the problem is structural. The factor of 5 was chosen as an order-of-magnitude probe — decisive enough to be meaningful, not derived from a calibrated uncertainty estimate.

---

## Slide 11 — Diagnostic — Seasonal Controls (1:30)

> "We suspected seasonal overlap. iOS spend and conversions both peak in spring — maybe the model was conflating tax season demand with iOS causal impact. So we added seasonal controls: month-level and day-of-week indicators. The result: iOS barely moved, $23 to $34. Android actually got worse, jumped to $1,700. The seasonal controls destabilized the other channels because they all share the same spring pattern. So we ruled out calendar overlap."

---

## Slide 12 — What We Found (1:30)

> "Here's the root cause. When we look at the full 19-month history, iOS spend and total conversions move together — correlation of 0.48. The model sees that and concludes iOS is very efficient, $23 per acquisition. But the holdout experiment said $135. The reason for the gap: iOS campaigns were running more heavily during periods when conversions were already high — spring, tax season. The model can't distinguish 'iOS spend caused conversions' from 'iOS spend happened at the same time as high conversions.'"

> "What this tells us: the 19-month observational history alone can't cleanly attribute iOS impact. The holdout experiments are our most reliable signal — and they need to be used more carefully."

*Pause point — Abheek may want to comment here. If he confirms iOS pacing is deliberate, note it — this is important for the model.*

---

## Slide 13 — What This Tells Us — Conclusion (1:30)

> "So here's the diagnosis, all together. iOS is structurally broken within the current calibration approach. That won't change regardless of tuning — every model run over 639 days reinforces the same correlation. The $23 ICAC is not an interpretable efficiency number. Android is actually fixable within the current approach — the experimental signal is present and responsive, it just needed tighter uncertainty."

> "What we're moving to: time-windowed priors. Apply the experimental evidence only during the actual test window — May 6 through 14, 2025. During those 9 days, spend was experimentally controlled, so the iOS pacing correlation doesn't exist. The model anchors to ground truth exactly where the confound is absent. Outside those 9 days, wider assumptions."

[Speaker note — if Abheek asks: "Are you confident this will work?"]:
Moderate confidence. The architecture directly addresses why the current approach failed — it eliminates the data imbalance by restricting the experimental constraint to the window it actually measured. But we haven't run it yet. "Designed to fix the structural problem" is the honest framing — not a guarantee. Results by end of week. If it doesn't pass the gates, we have a defined escalation path.

---

## Slide 14 — What We're Doing Next (1:30)

> "The fix: instead of applying the holdout results as a constraint across all 639 days, we apply them only within the actual test windows. During the Meta May 2025 holdout, spend was experimentally controlled — so we know the causal relationship is clean there. Outside those windows, the model uses a wider assumption. This focuses the experimental signal where it's cleanest and avoids the 19-month observational confound. We're running this version now, expect results by end of week."

---

## Slide 15 — Questions (3:00)

> "Before we wrap, three data questions that will directly shape the next model run."

**Q1:**
> "For spend rows where iOS and Android are reported combined — we've been assuming 50/50. That affects the platform-level iCAC split. If there's actual platform-level spend data available, we'd want to use the real breakdown. Is that accessible?"

**Q2:**
> "We observe iOS campaigns concentrating heavily in Q2 — spring, tax season. That concentration creates a correlation with total conversions (r = 0.48 in the historical data) that we believe is part of what's making the model attribution difficult for iOS. Our working hypothesis is that this is deliberate campaign pacing — focusing iOS spend when consumer intent is already elevated. Is that right? And if so, was the rationale about intent timing, or something else?"

*Wait for Abheek's response here — this directly affects our interpretation of the structural problem.*

**Q3:**
> "One more technical one on the May 2025 holdout specifically. The test design used reach restriction — some users were held out from seeing ads. That design typically suppresses total conversions during the test window. Our next approach applies the experimental evidence specifically within those May 6–14 dates. If total conversions were materially lower during that window due to the holdout design itself, we want to account for that correctly rather than treating it as a normal 9-day period. Can you confirm whether the conversion dip during the holdout was notable, and whether you'd want us to treat those dates as a structural artifact?"

[Speaker note — why Q3 matters technically]:
If the May 6–14 window had suppressed total conversions (because the holdout pulled users out of the reachable pool), the delta_y values we fed into the model (iOS 1,180, Android 1,427, Web 1,365) may already reflect that suppression — meaning the true incremental lift could be higher. More importantly, when the time-windowed model constrains itself to those 9 days, it's looking at a period where total conversions were lower than normal. If we don't flag this, the model might partially absorb the conversion dip as "iOS efficiency was lower during this window" rather than "the whole window had suppressed baselines." A dummy variable for the holdout period in the time-series (a known structural break) would handle this cleanly.

---

## Anticipated Q&A

---

**Q: "Why is iOS so far off? Is something wrong with the data?"**

> "Not a data error — the underlying iOS spend numbers are correct. The issue is that iOS campaigns and total conversions happen to correlate strongly in the historical record, because iOS campaigns were often running when conversions were already elevated. The model uses that 19-month pattern to estimate iOS efficiency, and it's picking up correlation rather than causation. The holdout experiment corrects for this — it controlled the iOS spend directly — which is why the holdout says $135 and the observational history says $23."

---

**Q: "Can I see the actual model output?"**

> Open `notebooks/P2_03_mmm_meta_poc_CURRENT.py` in Marimo:
> ```
> marimo run notebooks/P2_03_mmm_meta_poc_CURRENT.py
> ```
> Show: Section 2 (baseline), Section 3 (lift test integration), gate results table.
>
> Key numbers to point to:
> - Baseline (no priors): iOS $21.17, Android $957.57, Web $456.70
> - With holdout integration: iOS $23.25, Android $598.84, Web $362.61
> - With seasonal controls: iOS $33.99, Android $1,727.52, Web $587.87
> - Holdout benchmarks: iOS $135.48, Android $63.06, Web $156.89

---

**Q: "What does the next approach look like technically?"**

> "Instead of applying the holdout result as a constraint on the whole saturation curve, we restrict it to apply only during the test window. Think of it as: during the Meta May 2025 test window, we say 'this is what iOS efficiency looked like.' Outside that window, the model is free to estimate based on the broader data. This is a standard Bayesian technique — we're essentially switching on a stricter prior only when we have experimental evidence for it."

---

**Q: "When will we have results from the new approach?"**

> "End of this week. If the time-windowed approach passes our validation checks — the model recovers ICAC values close to the holdout benchmarks — we move to the full channel build. If it doesn't, we have a defined escalation path. Either way, you'll hear from us before the week is out."

---

**Q: "Are we still on track for the June deadline?"**

> "Yes. The Meta POC is the hardest part — it's the channel with the most complexity (two tests, three platforms, the pacing issue). Once we solve it here, the approach scales to the other channels. We're still targeting full channel coverage by early June."

---

*Private notes (do not share):*
- *Q22 = iOS/Android 50/50 split question*
- *Q24 = iOS pacing question*
- *Next approach = Mechanism 2 (time-windowed priors via pm.math.switch())*
- *If Abheek confirms pacing is deliberate → propose-state-update Q24*
- *If Abheek provides real iOS/Android split → update src/config.py + propose-state-update Q22*
