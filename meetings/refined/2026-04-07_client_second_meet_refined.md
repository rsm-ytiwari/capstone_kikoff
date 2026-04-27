# Client Meeting — Week 2 (April 7, 2026) — Refined Notes

**Attendees:** Abheek Sinha (client), MMM Capstone Team  
**Meeting Focus:** Data availability, data walkthrough, modeling approach clarification  
**Prepared by:** Yash (refinement: 2026-04-12)  
**Source:** meetings/raw/2026-04-07_client_second_meet.md  
**Purpose:** Detailed reference for data structure, confirmed facts, and next-step modeling decisions.

---

## 🚨 CRITICAL: Assumption Invalidated

**Current assumption in `project_state.md`:**
> "Data is at weekly granularity with no significant gaps" (Confidence: M)

**CONFIRMED IN THIS MEETING:**
> Data granularity is **DAILY** (spend, conversions, LTV all daily).

**Action:** This invalidates the weekly assumption and must trigger a state update proposal.

---

## Confirmed Facts: Media Spend Data

| Aspect | Detail |
|--------|--------|
| **Granularity** | Daily |
| **Date range** | 2024 — March 2026 (2023 data exists but should be dropped when merging) |
| **Type** | Actual spend (not attribution-based) |
| **Channels (12–13 total)** | Meta, TikTok, Apple, Influencers, CTV (Connected TV), Linear TV, Others, + possible sub-channels |
| **Platform splits** | iOS, Android, Web |
| **Data issues** | Some recent discrepancies may exist; unlikely to block modeling but should be flagged for context |
| **Important notes** | • CTV and Linear TV are SEPARATE channels — do not combine<br>• "Others" category exists — needs decision: model or drop?<br>• Platform-level splits may be available (e.g., Meta iOS vs. Meta Android) |

---

## Confirmed Facts: Conversion & LTV Data

| Aspect | Detail |
|--------|--------|
| **Granularity** | Daily |
| **Dependent variables** | Conversions (volume) + LTV (predicted) |
| **LTV types** | 1-year LTV (recommended) and 3-year LTV (~2x of 1-year) |
| **LTV source** | Model-based predictions (not actual observed revenue) |
| **LTV composition** | Includes first subscription + retention/churn modeling |
| **Data quality issues** | ~10 anomalous LTV values (outliers or errors) — need smoothing/imputation |
| **Date range** | Same as spend (2024–Mar 2026); drop 2023 when merging |

---

## Confirmed Facts: Incrementality Test Data

| Aspect | Detail |
|--------|--------|
| **Number of tests** | ~4–5 tests (primarily from 2025) |
| **Test structure** | Test period + channel tested + spend during test + lift (incremental impact) |
| **Key metric** | Incremental CAC (iCAC) — cost per incremental conversion |
| **Usage requirement** | **MUST be used for CALIBRATION** (not just post-hoc validation) |
| **Format** | Includes lift estimates (and ideally confidence intervals, though format issue flagged) |
| **Channels covered** | Primary tests: Meta, CTV (exact list of all 4–5 channels not fully specified — needs follow-up) |
| **Data issue** | Formatting issue on second sheet — needs resolution |

**Rationale for calibration use:**
> If incrementality shows a channel has iCAC=$X at spend level $Y, the MMM output during that period should be reasonably aligned. Large deviations indicate model issues.

---

## Critical Modeling Concepts Discussed

### Baseline vs. Scaling
- **Baseline:** Current spend level and efficiency
- **Scaling question:** What happens if spend increases/decreases?
- **Response curve:** Efficiency declines as spend increases (saturation/diminishing returns)

### ICAC (Incremental CAC) — Cost per Additional Acquisition
- Directly comparable to MMM-derived CAC
- Provides anchor for model calibration
- Different from average CAC (which can be misleading at different spend levels)

### Saturation Effects
- Expected across all channels
- Should be derived from the model, not pre-specified
- Captured via response curves (Hill function or similar)

---

## Modeling Approach Insights

### Bayesian vs. Non-Bayesian
- **Meridian:** Bayesian framework, supports prior specification directly
- **Robyn (Facebook MMM):** Open-source, widely used, but prior incorporation may require customization

**Direction stated:** Will explore both; may favor Bayesian approach if priors (incrementality) are central to the design.

### Incrementality Integration Strategy
- **NOT:** Use incrementality only for post-hoc validation
- **YES:** Feed incrementality into the model as Bayesian priors (channel effectiveness ranges, confidence intervals)
- **Result:** MMM outputs constrained to align with ground-truth causality

---

## Seasonality Patterns Confirmed

| Period | Pattern |
|--------|---------|
| Tax season (likely Q1 + April) | Higher demand; budget should increase |
| November–December | Holiday period; lower demand; budget typically decreases |
| Rest of year | Baseline patterns |

**Implication:** Model must capture and forecast these patterns for scenario planning.

---

## Success Criteria for the MMM (Aligned in Week 2)

1. **Explain variation:** Model captures how spend changes across channels relate to conversion changes
2. **Channel confidence:** Output includes confidence levels per channel (some high, some moderate, some low due to limited variation)
3. **Scenario capability:** Support "what-if" simulations (+10%, +20%, +30% budget scenarios)

**Note:** If most channels have low confidence, the model is not actionable — this is a red flag to flag immediately.

---

## Open Questions — Partially Answered (Week 2)

| Original Question | Week 1 Status | Week 2 Update | Still Open? |
|-------------------|---------------|---------------|------------|
| Q1: Primary DV (conversions vs. revenue)? | Unresolved | "Model conversions OR revenue via LTV — either works" | ⚠️ **Partially** — client confirmed both viable; team must choose optimization target |
| Q2: Data completeness & granularity? | Unresolved | **Daily granularity, 2024–Mar 2026, ~10 LTV anomalies, drop 2023** | ✅ **Mostly resolved** |
| Q3: Channel/tactic definitions? | Unresolved | **12–13 channels listed; CTV/Linear TV separate** | ⚠️ **Partially** — list exists but "Others" needs decision; platform splits unclear |
| Q4: Date range? | Unresolved | **2024–Mar 2026 (validate final cutoff: Feb vs. Mar)** | ⚠️ **Mostly resolved** — exact cutoff date TBD |
| Q5: Incrementality format? | Unresolved | **iCAC available, ~4–5 tests, calibration use confirmed** | ⚠️ **Mostly resolved** — formatting issue needs resolution |

---

## Open Questions — Still Unresolved

| Question | Category | Why It Matters |
|----------|----------|----------------|
| **Q1 (refined):** Should the model optimize for conversions or revenue? | Modeling | Determines dependent variable and interpretation of ROI/efficiency |
| **Q6:** Are there known structural breaks (budget shifts, product launches, platform outages)? | Data | Requires explicit handling; affects model assumptions |
| **Q7:** Are there data quality issues beyond the ~10 LTV anomalies? | Data | Affects data cleaning strategy |

---

## New Open Questions (Not Yet in `open_questions.md`)

| Question | Category | Why It Matters |
|----------|----------|----------------|
| **Which channels were covered by the 4–5 incrementality tests?** | Data | Determines which channels have hard priors vs. soft estimates |
| **What is the "Others" category — which channels does it include?** | Data | Affects channel-level modeling; may need to be dropped or disaggregated |
| **Should the model operate at the channel level or platform level (iOS/Android/Web)?** | Modeling | Changes the number of parameters and interpretation granularity |
| **Final cutoff date: Feb 2026 or Mar 2026?** | Data | Affects usable data volume |
| **Is the incrementality file formatting issue resolved?** | Data | Affects ability to load test data cleanly |

---

## Modeling Challenges Highlighted

| Challenge | Impact | Mitigation Strategy |
|-----------|--------|---------------------|
| **Low-variation channels** | Limited signal for estimation; leads to low confidence | Accept lower confidence where data is weak; flag in results |
| **Channel collinearity** | If channels move together, hard to separate impact | Use incrementality priors to anchor separate estimates |
| **Scale imbalance** | Large channels (Meta) dominate; small channels (CTV) harder to detect | Consider standardization or Bayesian hierarchical structure |
| **Unexplained residuals** | Expected 20–60% of variance unaccounted for | Investigate via residual analysis; consider external factors |
| **Data quality anomalies** | ~10 bad LTV points, recent spend discrepancies | Clean/impute before modeling; document decisions |

---

## Residuals & Unexplained Variance

**Expected range:** 20–60% of total variance  
**Interpretation:** Normal and expected; not pure noise  
**Action:** Investigate residuals for:
- Missing variables (e.g., product changes, macro factors)
- External drivers (e.g., competitor activity, macroeconomic shocks)
- Data quality issues (e.g., reporting lags, measurement error)

**Note from client:** Higher residuals reduce interpretability; lower is better. Since brand spend is minimal, more variation should ideally be explained by channel activity.

---

## External Factors NOT in Current Data

| Factor | Status | Notes |
|--------|--------|-------|
| **Macroeconomic variables** | Not in data | Interest rates, unemployment, etc. — may be added if useful |
| **Product changes** | Not in data | Pricing changes, new features, UX redesigns |
| **Competitor activity** | Not in data | Not currently available |

**Next step:** Clarify with Abheek if any of these should be added.

---

## Metric Relationships

```
Conversions (Y)
  ↓
Revenue = Conversions × LTV
  ↓
CAC = Spend / Conversions
ICAC = iSpend / iConversions (from incrementality tests)
ROI = Revenue / Spend
```

**Model options:**
1. Model conversions → derive CAC
2. Model revenue (via LTV) → derive CAC and ROI

---

## Immediate Action Items (Before Next Meeting)

- [ ] Validate all 3 datasets (spend, conversions, incrementality)
- [ ] Align time ranges: drop 2023, confirm 2026 cutoff (Feb vs. Mar)
- [ ] Fix ~10 LTV anomalies (smooth or impute)
- [ ] Decide channel grouping (especially "Others")
- [ ] Gain clarity on incrementality test channels (all 4–5 tests)
- [ ] Prepare structured questions on unresolved items (see above)
- [ ] Map incrementality tests to calibration inputs (priors)
- [ ] Evaluate tool options: Meridian vs. Robyn vs. hybrid

---

## Implied Modeling Decisions (Noted, Not Yet Approved)

⚠️ **These are derived from the meeting but NOT yet formally decided:**

1. **Preferred tool direction:** Meridian (Bayesian) or Robyn with Bayesian extensions
2. **Incrementality as priors:** Use test results to constrain channel effectiveness ranges
3. **LTV choice:** Use 1-year LTV (drop 3-year)
4. **Time granularity for modeling:** Daily is raw; can aggregate to weekly if helpful
5. **Saturation modeling:** Derive from data (Hill function or similar); not pre-specified

These should be formalized in a proposal after data validation.

---

## Reliability Assessment

- **High confidence (95%):** Data structure, granularity, date range, channel list, incrementality requirement, seasonality patterns
- **Moderate confidence (85%):** Exact test details, "Others" scope, platform-level splits availability
- **Needs follow-up (70%):** Exact channels in incrementality tests, final cutoff date, external factors to include

**Status:** Data walkthrough is complete and trustworthy. Immediate next step is data audit to validate structure + confirm open questions.

---

## Summary: Before Phase 2 Data Audit

**Go/No-Go Checklist:**
- ✅ Data is available (on shared server)
- ✅ Granularity is clear (daily)
- ✅ Date range is clear (2024–Mar 2026; drop 2023)
- ✅ Channel list is known (12–13 channels)
- ✅ Incrementality tests exist (~4–5 tests)
- ✅ LTV format is known (model-based, 1-year preferred)
- ⚠️ Data quality issues flagged (~10 LTV anomalies, recent spend discrepancies) — need validation
- ⚠️ Some channel definitions need clarification ("Others", platform splits)
- ⚠️ Incrementality format issue (second sheet) — needs resolution

**Recommend:** Proceed with data audit; resolve open questions in parallel with supervisor.

---

*(End of Refined Notes — Week 2)*
