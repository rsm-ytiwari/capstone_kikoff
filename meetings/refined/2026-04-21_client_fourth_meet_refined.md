# Refined Meeting Notes — 2026-04-21 Client Meeting (Week 4)
**Attendees:** Yash Tiwari, Shivang Bhatt, Abheek Sinha (Kikoff sponsor)

---

## Facts Learned (confirmed information)

1. **PyMC-Marketing selected as modeling framework** — Team presented evaluation of Meridian, PyMC-Marketing, LightweightMMM (archived/deprecated), Robin (non-Bayesian), and custom PyMC. Recommended PyMC-Marketing for best balance of flexibility and complexity. Abheek approved: "I think that makes sense. I trust your judgment here." (Source: Abheek, ~11:08–12:33)

2. **LightweightMMM is archived/deprecated** — Meridian is its successor. (Source: team presentation, ~8:31)

3. **Custom PyMC rejected as too complex/risky** — PyMC-Marketing serves as a bridge between custom PyMC and out-of-box frameworks. (Source: team, ~11:18–11:47)

4. **DSP taxonomy locked:**
   - **Applovin, Liftoff, InMobi DSP:** Keep as separate channels
   - **StackAdapt + Appvertiser:** Combine into one channel
   - **Influencer:** Keep as "Influencer" (not combined with anything)
   - **Bing:** Drop from model — Kikoff no longer advertising on Bing
   (Source: Abheek, ~13:08–14:11, ~19:08–19:23)

5. **"Others" category is primarily "Idle"** — Abheek identified this after checking. Spend share jumped from ~1% (Q1 2025) to ~14%. This is concerning. Abheek investigating internally. (Source: Abheek, ~15:02–17:10)

6. **Spend data has errors** — The spend file (MMM_platform_channel_daily_spend, 260407) has issues. Facebook and other channels should show spend starting from 2024, but data appears incomplete for earlier periods. Abheek will have data engineering fix and re-upload. (Source: Abheek, ~26:43–29:28)

7. **Updated LTV numbers coming** — Previous LTV numbers not accurately capturing all predicted LTVs. Will be "more inflated." Abheek needs data submission link re-shared (via Anshul). Won't change modeling approach. (Source: Abheek, ~5:17–5:45)

8. **Time-limited priors (major modeling guidance)** — Incrementality priors should ONLY apply within the test time period, NOT to the entire model history. "If you're applying priors, you only apply priors within that time period and not to the entire history of the model time period." Otherwise, priors generalize the entire model for Meta/TikTok/CTV incorrectly. (Source: Abheek, ~32:50–33:51)

9. **Start modeling with Q3 2024 onwards** — Data from Q3 2024 appears to have proper channel spend populated. If data engineering can provide earlier data, just change the timeline in code. Don't wait for the fix — build logic in the interim. (Source: Abheek, ~34:50–35:56)

10. **Each incrementality test had a different purpose:**
    - **Meta May 2025:** Understand saturation level (not meant for scale decisions)
    - **TikTok Aug-Sep 2025:** Promising results led to TikTok spend scaling post-August
    - **Meta Jan 2026:** Test whether incrementality changed given growth headwinds. Didn't land as intended.
    (Source: Abheek, ~22:30–25:30)

11. **Jan 2026 Meta test still valuable as prior** — "That represents some actuals of that particular season... the closest source of truth in the month of January." (Source: Abheek, ~22:30)

12. **Expected deliverable outputs — concrete chart specification:**
    Each channel+tactic produces a single-channel view with two sections:

    **Top — Response curve ("Incremental Spend vs [KPI]"):**
    - X-axis: weekly spend ($0 to ~$955K for high-spend channels)
    - Left Y-axis: iROAS (0–1.5x) or iCAC ($0–$400), switchable between KPI objectives (LTV Revenue / New Customer Transactions)
    - Overlaid elements: response curve with confidence bands; observed weekly spend histogram (gray bars); vertical marker for last-52-week median historical spend (e.g., $437K for Facebook Web — this is the "$437K" Abheek referenced during the call)

    **Bottom — "Incremental performance over time" (time series):**
    - X-axis: date range (e.g., Apr 2025–Mar 2026 for 52WK view)
    - Left Y-axis: iROAS or iCAC; Right Y-axis: weekly spend
    - Two lines: solid = iROAS or iCAC; dashed = spend
    - Tooltip shows exact weekly values (example: Feb 3–9 2026 — iROAS = 0.81x, Spend = $448K)

    **Time period toggle:** 5WK, 26WK, 52WK, LAST YEAR, ALL TIME — replicate at minimum 52WK and ALL TIME views per channel.

    **Observed pattern for Facebook Ads - Web Campaigns (LTV Revenue KPI):** iROAS started ~1.0x (Apr 2025), trended down to ~0.35–0.5x by Feb–Mar 2026 at spend levels of $400–600K/wk. iCAC relatively stable at ~$200–250. This pattern reflects saturation as spend remained elevated.

    Granularity: channel + tactic. Format: notebook/markdown — no live dashboard needed.
    (Source: Abheek, ~36:12–43:31)

13. **Northbeam MMM+ is the third-party tool Kikoff uses; team replicates outputs in notebook format:**
    The platform Abheek's data science team uses is **Northbeam MMM+** ("MMM+ View Incremental ROAS/CAC"), which runs on a continuous processing cadence for Kikoff's account. It provides a multi-channel summary card grid (sortable by spend, switchable by KPI) alongside the single-channel views described in Fact #12. Our team does not build or replicate a live dashboard. Abheek confirmed: "you don't need to think about creating a dashboard... what you would be creating is more sort of like the markdown sort of thing." The multi-channel summary — showing iCAC and total spend across all channel+tactic pairs — should eventually be replicated as a static summary table. Abheek noted there are two systems: Northbeam (the third-party platform shown during the call) and Kikoff's internal data science dashboard (referenced verbally; not shown during the call). Our outputs are analogous to what Northbeam provides, delivered in notebook form.
    (Source: Abheek, ~43:05–43:31)

14. **MMM Decisioning layer is the downstream final deliverable:**
    Abheek's data science team translates model output into a structured decisioning table — a Google Sheet — after producing the charts. This is the "narrative" Abheek referenced: "create that narrative and then go to marketing team." Structure per channel+tactic:
    - **Current spend signal** (low / moderate / high / very high)
    - **iCAC trend** (absolute value and directional trend)
    - **iROAS trend** (absolute at current spend, directional)
    - **Trust/confidence** (green = high, yellow = use with caution, red = low — derived from model confidence intervals)
    - **Saturation read** (e.g., "marginal efficiency intact," "early saturation," "saturated")
    - **Recommended action** (Scale & Test / Maintain / Hold / Scale back)
    - **Spend move to test %** (directional spend change to experiment with)

    **Milestone sequencing:** Charts (response curves + time series per channel) = first milestone. Decisioning table fed by those charts = second milestone. Both are within team scope.
    (Source: Abheek, ~36:12–43:31)

15. **First milestone: start with Facebook Ads - Web Campaigns, then replicate across all channels** — Facebook Ads - Web Campaigns is the confirmed starting channel: highest spend ($23.1M/52WK) and the channel Abheek walked through in detail. If the team can produce iCAC/iROAS charts for this channel+tactic, replicate for all other channel+tactic pairs. Then consolidate into the summarized decisioning view (~1 week after charts complete). (Source: Abheek, ~42:34–43:31)

16. **MMM accuracy expectations:** Model output can be "only 50% accurate" and that's fine. No nuance called "accurate" in marketing. High ambiguity, requires intuition. Focus is on making better recommendations and testing the right things in the right order. (Source: Abheek, ~43:49–45:38)

17. **Downstream use of model:** Recommendations lead to prioritized incrementality tests (scale +20%, +40% systematically). Tests scheduled Q3–Q4 2026. Team provides recommendations; won't see test results within project timeline. (Source: Abheek, ~45:56–47:59)

18. **Meeting time moving back to 2-3 PM** — Abheek's Tuesday commute conflicts with current slot. (Source: Abheek, ~50:07–50:33)

---

## Assumptions Changed or Created

| Assumption | Status | Detail |
|------------|--------|--------|
| Framework: 2-week exploration window | **RESOLVED EARLY** | PyMC-Marketing selected. Abheek approved. No further exploration needed. |
| "Others" ≈9% share, disposition TBD | **UPDATED** | "Others" is primarily "Idle"; share jumped 1%→14%. Abheek investigating. More concerning than previously thought. |
| Incrementality priors apply to full model period | **NEW/CHANGED** | Priors apply ONLY within the test time window, not the full model history. Major modeling constraint. |
| Usable data start date: Jan 2024 | **UPDATED** | Start with Q3 2024 onwards due to spend data issues. May extend back once data engineering fixes upload. |

---

## Decisions Made or Implied

1. **PyMC-Marketing is the modeling framework** — sponsor approved; exploration period ended early.
2. **DSP grouping finalized:** Applovin / Liftoff / InMobi separate; StackAdapt + Appvertiser combined; Bing dropped.
3. **Channel mapping updates:** Influencer stays as "Influencer." StackAdapt + Appvertiser → combined DSP channel.
4. **Time-limited prior application:** Incrementality priors constrained to their test time windows only.

---

## Open Questions Surfaced

1. **What is "Idle" in the Others category and why did spend jump 1%→14%?** Abheek investigating internally. May affect Others channel definition.
   _Tagged: For Supervisor_

2. **How to implement time-limited priors in PyMC-Marketing?** Abheek gave the guidance (priors only within test window); team needs to research PyMC-Marketing's mechanism for this.
   _Tagged: For Team_

3. **What are "diffused priors" and should we use them?** Professors suggested exploring this concept — using incrementality as partial hints rather than full prior values. Abheek unfamiliar with the term. Team needs to research.
   _Tagged: For Team_

4. **What is the earliest reliable data date?** Depends on data engineering fix. Q3 2024 is safe fallback; may extend back to Jan 2024.
   _Tagged: For Supervisor_

---

## Answers Received to Prior Open Questions

### Q17: Which Bayesian MMM framework to use?
**Classification: FULLY ANSWERED**
**Answer:** PyMC-Marketing. Team evaluated Meridian, PyMC-Marketing, LightweightMMM (deprecated), Robin, and custom PyMC. PyMC-Marketing chosen for best flexibility/complexity balance. Abheek approved.
**Proposed action:** Move to resolved_questions.md.

### Q15: Which SOURCE_GROUP values map to "Programmatic DSP"?
**Classification: FULLY ANSWERED**
**Answer:** Applovin, Liftoff, InMobi DSP = separate channels. StackAdapt + Appvertiser = combined. Bing = dropped (no longer advertising). Influencer = keep separate.
**Proposed action:** Move to resolved_questions.md.

### Q9: What is the "Others" category?
**Classification: PARTIALLY ANSWERED**
**Update:** Others is primarily "Idle." Spend share jumped from 1% to 14%, which is more concerning than the previous ~9% estimate. Abheek investigating internally.
**Still open:** Root cause of the spend jump. Whether Idle should be modeled, excluded, or reclassified.

### Q3: How are "channels" and "tactics" defined?
**Classification: PARTIALLY ANSWERED**
**Update:** DSP grouping now resolved. StackAdapt + Appvertiser combined. Bing dropped. Remaining mapping mostly locked.
**Still open:** Others/Idle disposition pending Abheek's investigation.

### Q2: What is the actual data completeness?
**Classification: PARTIALLY ANSWERED**
**Update:** Spend data file has errors — missing channel data for pre-Q3 2024. Data engineering will fix and re-upload. Start with Q3 2024+ in interim.
**Still open:** When will corrected data be available? Will it extend back to Jan 2024?
