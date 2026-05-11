# Supervisor Meeting Study Guide

**Purpose:** This is your preparation guide for the meeting with the supervising data scientist. Read through each section before the meeting so you understand what we're presenting and why.

**Audience:** Team members new to Bayesian MMM. Jargon is explained before use.

---

## Slide 1: Data Overview

### What we're saying
We have clean data covering 828 aligned days (Jan 2024 — Apr 2026). We've loaded spend by channel, customer conversions, and lifetime value. We also have incrementality tests (small experiments that measure true causal effects) from 4 different campaigns.

### Why it matters
Before building any model, you need to know:
- Do we have enough historical data? (Yes, 828 days is good)
- Are the datasets aligned? (Yes, matched on dates)
- Do we have ground-truth causal data? (Yes, 4 incrementality tests)

If any of these were missing, we'd need to pause.

### What we expect to hear
The supervisor will probably:
- Ask about data quality (any obvious gaps or anomalies?)
- Confirm the date range is usable
- Mention if any of the incrementality tests are problematic

### What to do if corrected
If they say "drop data before X date" or "that test is unusable" — add it to the list and we adjust Phase 2 scope.

---

## Slide 2: Key EDA Findings

### What we're saying
We looked at the raw data and found 5 patterns:
1. **Spend concentration:** A few channels eat most of the budget
2. **Adstock:** There's a 7–21 day delay between when you spend money and when customers convert
3. **Tax season:** January–April spikes are real (tax filing season drives sign-ups for a fintech product)
4. **Revenue signal:** LTV-based revenue correlates with spend better than raw conversion counts
5. **Day-of-week:** Weekdays differ from weekends (affects timing interpretation)

### Why it matters (in order)
1. **Spend concentration:** Means our model needs to handle channels of very different sizes. We can't just fit one formula to all channels.
2. **Adstock:** Your ads don't work instantly. People see an ad on Day 1 but sign up on Day 8. The model needs to account for this carryover, or it will underestimate ad effectiveness.
3. **Tax season:** If we ignore seasonality, we'll think January ads are amazing when really it's the tax deadline. Seasonality must be a separate variable in the model.
4. **Revenue signal:** This suggests we should optimize for revenue (conversions × LTV) rather than just conversion count. If LTV varies by channel, optimizing for volume alone gives bad advice.
5. **Day-of-week:** Confirms our data is granular enough to need daily-level modeling.

### What we expect to hear
The supervisor might say:
- "Good catch on the adstock lag" or "that lag looks typical for fintech"
- Ask if we've checked for other seasonal patterns (holidays, school years, etc.)
- Confirm that revenue is indeed the right optimization target

### What to do if corrected
If they say "actually, the tax season effect is much stronger/weaker than that" — note it. If they point out we missed another pattern (e.g., post-IRS-refund lag) — add it to Phase 2 feature engineering.

---

## Slide 3: Incrementality Test Summary & Bayesian Priors

### What we're saying

**Incrementality tests:** These are controlled experiments (like A/B tests) where Kikoff ran ads in some regions/accounts and held them out in others, measuring the true causal effect.

**iCAC:** Incremental Cost per Acquisition. From the test, for every dollar spent on TikTok iOS, they got conversions that cost ~$108.83 each.

We have 3 high-quality tests:
- TikTok (Aug–Sep 2025): Clean data from all platforms
- Meta/Facebook (May 2025): Early termination but usable
- CTV (Oct–Nov 2025): Clean geo-based holdout

We also have 1 uncertain test:
- Meta (Jan 2026): Test was cancelled; data quality unknown

### Why it matters

**Bayesian MMM** = using prior beliefs to help fit the model. Instead of letting the model guess how effective each channel is, we give it anchors: "From the TikTok test, we know iOS conversions cost $108.83 — estimate around that range."

This prevents the model from fitting nonsensical channel effects (e.g., claiming a $0.50 CAC when incrementality says $80+).

### What we expect to hear

The supervisor will likely:
- Ask if any of the tests are "clean" (no confounds, test ran as planned)
- Confirm the Jan Meta test is truly unusable (we should probably exclude it)
- Suggest whether to use iCAC or ROAS (return on ad spend) for the prior

### What to do if corrected

If they say "the May Meta test has data quality issues, use TikTok and CTV only" — we note that and adjust our prior strategy.

If they mention additional test data you didn't know about — add it to the calendar for next meeting.

---

## Slide 3b: Data Dictionary — Variables & Their Meaning

### What we're saying

Every variable in our dataset has an interpretation. We want to confirm we've interpreted them the same way you have.

| Variable | What we think it means |
|----------|------------------------|
| TOTAL_SPEND | Real dollars Kikoff spent on that channel that day |
| SOURCE_GROUP | Channel name (tiktok, facebook, apple_search, etc.) |
| PLATFORM | Device type (iPhone, Android phone, web browser) |
| CONVERSIONS | Number of sign-ups or subscriptions that day |
| LTV_1YEAR | Predicted revenue per customer over their first year |
| iCAC | Cost to acquire 1 customer (from incrementality tests) |
| DS | The date |

### Why it matters

If we're wrong about even one variable, the model is wrong.

Example: If CONVERSIONS actually means "clicks" not "subscriptions," then our entire model is optimizing for the wrong thing.

This is why we ask you to fill in the "Confirm?" column on the slide.

### What we expect to hear

The supervisor will either:
- Confirm all definitions (best case)
- Correct one or more (e.g., "LTV_1YEAR is actually 18-month LTV, not 12-month")
- Add nuance (e.g., "CONVERSIONS includes free trials, not paid conversions")

### What to do if corrected

If definitions are wrong:
- Note the correction in our data dictionary
- Add a proposal to state/open_questions.md if it affects modeling
- Re-run any EDA that depended on the old definition

---

## Slide 4: Data Quality Issues — Flagged for Supervisor Input

### What we're saying

When we loaded and inspected the data, we found 5 issues that need your guidance to fix:

1. **Platform values are messy:** Some rows say "iOS", some say "iOS and Android", some say "web and app". We can't model a row that combines platforms.

2. **SOURCE_GROUP names don't match:** We have 15 different channel names in the data, but you told us 12–13 channels. The names also don't match what we expected (e.g., "facebook" instead of "Meta"). We need a translation table.

3. **Missing LTV on 2 specific days:** March 9 and 10, 2024 have thousands of conversions but LTV is blank. How should we fill in the blanks?

4. **LTV outliers:** You mentioned ~10 "bad" LTV points. We found 2 that are completely null, but where are the other ~8? What makes a value "bad"?

5. **"Others" channel is huge:** 9% of spend is labeled "others". Is that a real channel to model, or should we try to break it down further?

### Why it matters

Each of these affects what data we feed into the model. If we use bad data, the model learns the wrong relationships.

- **Platform mess:** If we model "web and app" as a single unit, we can't tell which device type drove the conversions.
- **SOURCE_GROUP mismatch:** We can't assign priors from incrementality tests to channels if we don't know which SOURCE_GROUP is which channel.
- **Missing LTV:** 2 days of missing data might not sound bad, but if the model can't learn what those days mean, it creates instability.
- **Outliers:** Bad data points can pull the model's estimates in nonsensical directions.
- **"Others":** If it's real spend, we should model it. If it's miscategorized spend, we should fix the root cause.

### What we expect to hear

The supervisor might say:
- "Just drop rows with combined platforms" or "Disaggregate them like this: ..."
- Provide a SOURCE_GROUP → channel mapping table
- "For missing LTV, use the rolling average" or "These 2 days are anomalies, just fill with 0"
- "Bad LTV is anything outside this range: $X to $Y" or "Here's the list of dates with known issues"
- "Others is real; we'll leave it as-is" or "Others is garbage; let's disaggregate"

### What to do if corrected

Create a data cleaning/preprocessing script in Phase 2 that implements the supervisor's guidance. Document it in state/decisions_log.md so future work knows why we cleaned it this way.

---

## Slide 5: Blocking Decision 1 — Channel Taxonomy Mapping

### What we're saying

Your operational data system uses one set of channel names (SOURCE_GROUP: facebook, tiktok, apple_search, applovin, etc.).

Your business talks about channels differently (Meta, TikTok, Google, Mobile DSP, CTV, Linear TV, etc.).

We need a translation table before we can build the model.

### Why it matters

**Example problem:** Suppose the supervisor says "Model these 5 channels: Meta, TikTok, Google, DSP, CTV." But our data has 15 SOURCE_GROUPs. Which ones map to DSP? Is applovin a separate channel from liftoff, or are they both "DSP"?

If we guess wrong, we'll assign the wrong incrementality prior to the wrong channel. TikTok iCAC might get assigned to applovin.

### What we expect to hear

The supervisor will provide (or reference) a mapping:
- "facebook + instagram → Meta"
- "applovin + liftoff + appvertiser → Mobile DSP"
- "tiktok → TikTok"
- etc.

### What to do if corrected

Create a mapping table in our codebase (probably a CSV or Python dict). Use it to aggregate SOURCE_GROUP rows into business-defined channels before building the model.

---

## Slide 6: Blocking Decisions 2 & 3

### Decision 2: Platform Data Handling

#### What we're asking

Should we model each channel separately by device type (iPhone, Android, Web)?

**Option A: Yes, model separately (Disaggregate)**
- iOS-TikTok, Android-TikTok, Web-TikTok are 3 separate variables
- Pro: We learn if iPhone users respond differently to TikTok than Android users
- Con: More parameters; noisier estimates; need more data per segment

**Option B: No, combine platforms per channel (Aggregate)**
- All TikTok (iPhone + Android + Web) is one variable
- Pro: Simpler, more stable; less risk of overfitting
- Con: Can't optimize budget separately by platform; miss platform-specific insights

#### Why it matters

This choice affects:
- **Model complexity:** Option A = ~3× more parameters
- **Budget recommendations:** Option B can only tell you "spend more on TikTok"; Option A can say "spend more on TikTok-iOS, less on TikTok-Android"
- **Data requirements:** Option A needs more data to estimate 3 separate effects; Option B needs less

#### What we expect to hear

The supervisor might ask:
- "Do you have enough data per platform-channel combo?" (This is a hint about feasibility)
- "What's your use case? Do we need platform-specific budget allocation?"

#### What to do if corrected

If they choose Option A: We'll need to handle the combined platform rows (disaggregate or drop them).

If they choose Option B: We aggregate all platforms per channel before modeling.

---

### Decision 3: Primary Optimization Target

#### What we're asking

What should the model optimize for?

- **Option A: Conversion volume** (count of sign-ups)
  - Simpler; focuses on customer acquisition
  - But ignores customer quality (high-LTV vs. low-LTV customers)

- **Option B: Revenue** (conversions × lifetime value)
  - Better for bottom-line business impact
  - But requires accurate LTV estimates
  - If choosing this: 1-year LTV or 3-year?

#### Why it matters

This becomes the model's objective function. Example:

- If you optimize for conversions, the model might say: "Spend $100M on TikTok; it's the cheapest CAC"
- If you optimize for revenue, the model might say: "Spend $70M on TikTok, $30M on Linear TV; TikTok is cheap but converts low-value customers; Linear TV gets fewer conversions but higher-LTV customers"

The second recommendation is better for business bottom-line.

#### What we expect to hear

The supervisor will likely say: "Revenue is the right target" (common in fintech).

Then they'll clarify: "Use 1-year LTV" or "Use 3-year LTV, but we're uncertain about out-year retention."

#### What to do if corrected

We set the model's objective function to whatever they choose and document it in the code and in state/decisions_log.md.

---

## Slide 6 (continued): Bonus Question — Jan 2026 Meta Test

### What we're asking

One of the incrementality tests was cancelled mid-run (January 2026 Meta test). Do we use it as a weak prior, or exclude it entirely?

### Why it matters

If we include it: "We weakly believe Meta CAC is around [uncertain value], but we're not confident."

If we exclude it: "We have no prior for Meta; let the data speak" (riskier, less stable).

### What we expect to hear

The supervisor will likely say: "The data is too messy; exclude it" or "Include it with very high uncertainty."

### What to do if corrected

We note their preference and adjust our Bayesian prior strategy in Phase 2.

---

## Slide 7: What Happens After This Meeting

### What we're saying

Once you give us answers to the 3 blocking decisions + 5 data quality questions, we have everything we need to build the model.

### The next steps (Phase 2)

1. **Data preprocessing** (1–2 days)
   - Apply channel mapping
   - Aggregate/disaggregate platforms per decision
   - Fix LTV anomalies per your guidance
   - Clean SOURCE_GROUP names

2. **Feature engineering** (2–3 days)
   - **Adstock transformation:** Convert daily spend into a decaying effect (7–21 day halflife)
   - **Seasonality terms:** Month-of-year, day-of-week indicators
   - **Control variables:** Things like incrementality test indicators (so the model doesn't mis-learn during test periods)

3. **Bayesian calibration** (2–3 days)
   - Translate iCAC values into prior distributions for each channel
   - Set up the model to respect those priors

4. **Model fitting** (3–5 days)
   - Choose architecture (Meridian vs. Robyn vs. custom)
   - Fit the model; check convergence
   - Validate against incrementality tests

5. **Scenario simulation** (1–2 days)
   - "What if we increase TikTok spend by 20%?"
   - "What if we move $5M from TikTok to Linear TV?"

### Why we're doing this in order

Each step depends on the previous one. We can't feature-engineer until we've decided on aggregation. We can't calibrate priors until we've engineered features. We can't fit until priors are set.

### What happens if decisions aren't made

We're blocked. Without channel mapping, we can't assign priors. Without platform decision, we don't know the feature space size. Without optimization target, we don't know what to maximize.

### What to do if new info surfaces

After the meeting, if you discover:
- "Oh, we have another incrementality test we forgot about"
- "Actually, CONVERSIONS means free trials, not paid"
- "The data feed has an error; exclude dates X–Y"

Tell us immediately. We incorporate it into Phase 2 planning (sometimes it's fast, sometimes it requires re-planning).

---

## How to Use This Guide

**Before the meeting:**
- Read this entire document
- For each slide, understand:
  - What question we're asking
  - What the answer will affect
  - What a good answer looks like

**During the meeting:**
- Listen for surprises (things the supervisor corrects or adds)
- Take detailed notes on the 3 blocking decisions
- Ask for clarification if an answer is ambiguous
- Note any new information (new test data, other data issues, constraints)

**After the meeting:**
- Compare supervisor's answers to what you expected
- Identify any surprises in state/open_questions.md with tag "From Supervisor"
- Begin Phase 2 data preprocessing per their guidance

---

*Study guide | Kikoff MMM Capstone | 2026-04-14*
