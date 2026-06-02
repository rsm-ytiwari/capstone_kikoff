# Presenter Script — Phase 2 Update (Meeting 7)

**Meeting:** Abheek sync · 2026-05-21
**Deck:** `deliverables/11_abheek_meeting7_results.qmd` / `.html`
**Estimated time:** 20 min walkthrough + 10–15 min Q&A on the decisions
**Audience:** Abheek Sinha (Kikoff project sponsor)

---

## Voice rules

- Lead with what's true now, then what got us there, then the open decisions.
- The +14.96% Model 2 bias, the TikTok iOS miss, and the 1.04x Meta Web concentration are honest findings — own them, don't bury and don't oversell.
- D-numbers, Q-numbers, milestone codes (D022, D027, D028, D029, M3.5b, M7, etc.) **stay out of the spoken deck**. They are listed here for your reference.
- If Abheek asks about something not in the deck, use the number cheat-sheet at the bottom for live lookups.

---

## Slide 1 — Title (10s)

Stand up the meeting. No preamble.

> "Phase 2 update. Calibration's settled, out-of-time validation is built, baseline got reframed. I want to walk through where we landed and end on the two questions that need your answer today."

---

## Slide 2 — Where we are (2:00)

The honest snapshot. Walk the table top to bottom.

> "Calibration: five of seven channels in band, was two of seven at our last meeting. Meta Web at $276 — inside your $275–$300 hunch, $69 above the lift-test upper. TikTok iOS at $288 versus truth $109 — that's a new miss the corrected gate surfaced; I'll come back to it."

> "Out-of-time: built. Model 1 MAPE 16.1%. Model 2 MAPE 15.1%, but with a +14.96% bias that's one-directional across all but one hold-out week. I'm not going to hide that — it's a real finding, and I'll explain why we kept Model 2 on canonical."

> "Baseline 67% globally. That number didn't move the way you expected. We worked through why; it decomposes into ~35% organic LTV plus ~32 points of paid attribution our regressors can't see — largely Meta Web view-through. On the attributed-revenue universe, baseline is closer to 50%."

> "Two blocking questions today. Three judgment calls. The blocking questions affect what the deliverable looks like at Phase 2 close."

**Internal map for this slide:**
- "5 of 7 in band" — D027 Fix-A result, `ltv_window_scaled.json` `windowed_icac` block
- "+14.96% one-directional, 12 of 13 weeks" — `oot_model2_ltv.json` computed from predicted vs actual; this is the corrected number (journey doc §2.6 said 13/13, that was an internal overstatement)
- "67% global / ~50% on attributed" — D029, `baseline_split.json` reference block

**Anticipated Abheek question:** *"Why isn't TikTok iOS in the band given we had a test on it?"*
**Prepared response:** *"That's the most interesting forensic on the table. TikTok iOS has an inverse concentration ratio — it contributes more outside its test window than during it. That pattern is consistent with pacing confound, not with the prior being too loose. If we tighten the prior to force iCAC down, we have evidence from Model 1 that it would shift other channels' iCACs by ~$30 — we'd be moving the problem rather than fixing it. I want your read on whether to document this as a structural limitation or attempt remediation anyway."*

---

## Slide 3 — Calibration journey (3:00)

The credibility moment. Slow down for Step 2 — the arithmetic-artifact story.

> "Two steps to get Meta Web from $652 to $276. First step is what you asked us to do at Meeting 6 — tighter Meta and TikTok priors, ~10% of point estimate instead of the 30% heuristic, re-include Meta Jan 2026, switch to a windowed gate. That moved Meta Web to $466. Convergence got much cleaner."

> "But $466 was still ~$260 above your hunch. We ran three independent diagnostics — prior strength ladder, alternative saturation curve, alternative saturation prior. All three landed at $466 plus or minus $7. The structural number under windowed priors was robust to those knobs. Prior tightness wasn't the residual driver."

> "Second step. We opened the question of what the windowed gate was actually comparing. The gate was running $508,038 of model spend — a 14-day weekly-rollup window — against 1,128 conversions from an 8-day lift test. Mechanically $450. The model had no degrees of freedom to disagree. On a consistent basis the implied true iCAC becomes $257. Most of the residual gap was an arithmetic basis error in our gate."

> "We scaled each lift test's Δy and σ by `(window days / test days)`. Meta Web moved to $281 and $276 across the two models. That's what closed it."

> "The honest read: a meaningful chunk of what looked like a calibration miss was a measurement-basis error we owned. The fix is the kind of thing that takes a day to find and a minute to apply, but it's the day-of-finding work that's the value."

**Internal map:**
- Step 1 = M3.5 canonical close-out: D022 (σ Path B 10%), D023 (windowed gate), D019-rev (re-include Meta Jan 2026), D024 (drop iOS>Android gate), D025 (Lever C lam prior)
- Step 2 = Investigation I-7 + D027 Fix-A
- Per-test scaling factors: Meta May ×1.75, TikTok Aug ×1.1667, CTV Oct ×1.037, Meta Jan ×2.8
- Numbers $508,038 and 1,128 from `drafts/i7_window_reconciliation_2026-05-18.md`

**Anticipated Abheek question:** *"How did the basis error survive first-pass review?"*
**Prepared response:** *"Honest answer — we treated 'windowed' as a unit-conversion-free swap when we wrote the gate. Both inputs pointed to the same test, so we assumed the units were aligned. We didn't audit day counts because the conceptual story was clean. The reconciliation forced us to look at the arithmetic, and the gap revealed itself."*

---

## Slide 4 — Channel results (1:30)

Walk by status. Don't read every row.

> "5 of 7 in band — meta_ios at $137, meta_android at $85, tiktok_android at $111, tiktok_web at $135, CTV at $139. All inside their truth bands."

> "Two open misses. Meta Web at $276 — $69 above the upper, inside your safety band $107 to $300. TikTok iOS at $288 — a new failure the corrected gate surfaced. We didn't even see this one under the old aggregate gate."

> "The two misses are different in kind. Meta Web's residual lines up with the view-through mechanism — I'll walk through that in the baseline section. TikTok iOS has an *inverse* concentration ratio — contributes more outside its test window than during. That reads as pacing confound, which is a different problem from the prior being too loose."

> "Convergence is clean across the board — R-hat ≤ 1.005, ESS ≥ 2,094, zero divergences."

**Internal map:**
- All numbers from `ltv_window_scaled.json` `windowed_icac` block
- "Pre → Post" column values from journey doc §2.4 table (pre-Fix-A vs post-Fix-A)
- "Safety band $107–$300" = Abheek's verbal extension at Meeting 6 (lift lower + your $300 hunch upper)

---

## Slide 5 — OOT validation: architecture + Model 1 (2:30)

> "Out-of-time was your top ask from Meeting 6. Built it. Trained on 79 weeks, held out 13."

> "I want to surface the architecture choice before the numbers, because it's asymmetric and a reviewer can fairly push on it."

> "Model 1 has one drift in the hold-out: conversion volume plateaued in 2026 Q1 while the linear projection has it growing. One linear trend control fixes it cleanly."

> "Model 2 has two drifts: same plateau plus a sustained +4% elevation in LTV-per-conversion that *offsets* the plateau, not compounds it. We tested every remedy in the same class — single trend coefficient over-corrects in the opposite direction, two-stage architecture trades systematic bias for week-to-week noise. So: Model 1 gets the control, Model 2 stays canonical with bias documented."

> "Model 1 numbers: MAPE 16.13%, signed mean −3.66%, over-prediction in 4 of 13 weeks, HDI coverage 38.5%. Inside the industry 15–25% band. Sign flipped from the pre-fix +18.83%; magnitude inside ±5%."

> "One caveat we want to surface up front. Adding the trend control shifted Model 1's Meta Web iCAC by ~$33. That's 12% of the canonical $281. We've run a prior-strength sweep on the new term and the prior never bites — meaning, this isn't tunable through priors, it's a structural sensitivity of the model to spec choices. We treat published windowed iCACs as point estimates inside a ~±$30 band under realistic spec variation."

**Internal map:**
- Trend control = D-γ remedy, `scripts/11b_oot_validation_M1_D_gamma.py`
- Metrics: `oot_model1_conversions.json`
- "Prior never bites" finding = Q35 / the 4-config gamma sweep
- "±$30 spec-variation band" is the M1 meta_web canonical $280.60 → D-γ $247.70 movement

**Anticipated Abheek question:** *"Why isn't Model 1 fit-time using the trend control too?"*
**Prepared response:** *"Fair pushback. Applying the trend at training time would surface that $33 iCAC drift onto the Decisioning Summary you'll see in the dashboard. We chose not to pay that cost — the drift is calibration noise rather than signal, and surfacing it would mislead the spend-decision conversation. The control is an OOT-prediction tool that absorbs secular drift, not a calibration tool. A reviewer can fairly say we resolved this tension by scoping where the control applies; we'd say we resolved it intentionally rather than hidden it."*

---

## Slide 6 — OOT validation: Model 2, honest finding (2:30)

This is the most important honesty moment in the deck. Don't rush.

> "Model 2. MAPE 15.13%, signed mean +14.96%. 12 of 13 hold-out weeks predicted above actual. The model's 89% predictive interval doesn't contain its own bias most weeks — that's the more serious epistemic concern, not the MAPE number."

> "I want to walk through why we kept this as canonical, because the bias is real and the choice is intentional."

> "The same trend control that fixes Model 1 over-corrects Model 2 — signed bias flips sign, keeps the same magnitude. Same problem, wrong direction. A two-stage architecture — project Model 2 from Model 1's conversions times elevated LTV-per-conv — closes signed bias to −4.59%, but MAPE worsens to 16.5% and HDI coverage drops to 0%. Every remedy traded one problem for another."

> "The choice was between a known-direction bias inside the MAPE band and a noisier prediction with worse coverage. We picked the version that documents the bias openly and keeps Model 2's posterior-predictive intact."

> "Mechanistically, the +14.96% reflects an LTV-per-conversion elevation in 2026 Q1 that the training data couldn't see. Closing it cleanly needs the attribution scope from the asks."

> "Third judgment call on slide 11 — we have one more remediation slot held. Want your read on whether to use it."

**Internal map:**
- M2 OOT metrics: `oot_model2_ltv.json` (canonical M3.5b Fix-A)
- Remedy attempts: D-γ on M2 (scripts/13), D-ε on M2 (scripts/14), v2-A/v2-B algebra (journey §2.8)
- 12 of 13: computed from predicted_weekly vs actual_weekly; week 9 (2026-03-02) is the one under-prediction at −1.11%
- Decision: D028 Option α — M2 stays canonical, bias documented

**Anticipated Abheek question:** *"Is a one-directional bias inside the MAPE band really publishable for MMM?"*
**Prepared response:** *"Defensible but not ideal. The 15–25% industry band assumes some symmetry of error; a one-directional bias inside that band is still inside the band, but it's not random noise — it's a characterizable mechanism. We chose to surface the limitation rather than declare victory at 15% MAPE. If you'd like us to attempt the held remediation slot before freeze, that's the third judgment call on slide 11."*

**Anticipated Abheek question:** *"HDI89 at 7.7% means your own uncertainty doesn't contain your bias most weeks. Isn't that worse than a wide MAPE?"*
**Prepared response:** *"Yes — that's the sharper epistemic concern, and it's the second-order reason we're disclosing this as a limitation rather than declaring victory. Posterior under-dispersion for OOT prediction is a known MMM pathology — it's how PyMC-Marketing propagates uncertainty through adstock and saturation. We could widen the HDI by loosening MCMC, but that's cosmetic. The real fix is in the data scope."*

---

## Slide 7 — Baseline structural reframe (2:30)

The intellectually substantive slide. Walk it slowly.

> "Baseline didn't move the way you predicted at Meeting 6. We worked through why."

> "Global baseline is 67%. In-window 61%. Out-of-window 68%. Only 7 percentage points between in and out — the lift priors aren't materially redistributing attribution at the global level."

> "Where the 67% comes from. You mentioned at Meeting 6 that Northbeam's attributed-revenue universe is ~65% of total revenue, the other ~35% being organic. That decomposition explains the structure: ~35% of total LTV is irreducible organic that paid attribution can't reach — it lives in baseline by construction because our model is fit on total LTV. The other ~32 percentage points is missed paid attribution, largely Meta Web view-through. The lift prior shifted Meta Web's iCAC level from $466 to $281, but didn't redistribute attribution into the test window, because the spend-to-conversion coupling is view-through-mediated and invisible to our regressors."

> "The <20% target you set was framed against the attributed-revenue universe — different scope from total LTV. By construction the model can't reach it on the data scope it's fit on today. That's not a calibration problem; that's a data-scope question, which is the first blocking ask."

**Internal map:**
- Baseline decomposition: D029 / `baseline_split.json`
- 35%/65% split inferred from Meeting 6 fact #13 (Northbeam attributed-revenue universe)
- D021 (the <20% gate) was deprecated by D029

**Anticipated Abheek question:** *"Where exactly did the 35% organic number come from?"*
**Prepared response:** *"Your Meeting 6 comment — that Northbeam initially used 'attributed revenue only, ~65% of total revenue, since ~35% is organic / unattributed.' We're inferring the organic share from that quote rather than from a precise Northbeam statistic. The qualitative conclusion — that the gap to your target is well above 20 points at either end of the range — holds whether the true organic is 30%, 35%, or 40%. The attribution-feed ask is partly about replacing this inference with data."*

---

## Slide 8 — Concentration diagnostic + apples-to-apples band (2:00)

> "Two things on this slide. First the diagnostic that surfaces what each channel's lift prior is doing. Second the band on the apples-to-apples baseline."

> "For each lift-tested channel, in-window dollars-per-week divided by out-of-window dollars-per-week. meta_ios at 2.35x — well-fit, the prior bites and redistributes attribution. tiktok_web, meta_android, ctv — moderate. **meta_web at 1.04x — flat.** The level shifted, the attribution didn't redistribute. That's the view-through fingerprint we expected from your Meeting 6 diagnosis. tiktok_ios at 0.79x — inverse — confirms the pacing-confound read on that channel."

> "Reviewer challenge worth surfacing: a flat ratio at meta_web is also consistent with a saturation effect or with the prior shape itself. View-through is the most likely mechanism but not the only one consistent with 1.04x. We're not asserting it's the only story."

> "Apples-to-apples baseline. If you accept the ~35% organic anchor, on the attributed-revenue universe — the scope your target was framed against — baseline is 49.74%. Under organic between 30% and 40%, the range is 45 to 53%. We cite it as a band, not a point. Still above 20% — the gap is the missed-paid-attribution component, which is what the data-scope ask resolves."

**Internal map:**
- Concentration ratios: `baseline_split.json` `per_channel` block
- Apples-to-apples math: `baseline_split.json` `reference` block; range 45.55–53.33% under organic ∈ {30%, 35%, 40%}
- Meeting 6 fact #13 verbatim (21:02–25:35): "a large portion of view-through attribution flows from Meta Web. Every time Meta Web spend is scaled up, attributed conversions don't spike in dashboards (because of view-through), but blended numbers grow consistently."

---

## Slides 9–12 — Dashboard live demo + 3 fallbacks (4:00)

Switch to the dashboard at `http://localhost:8501`. The next 3 slides are static fallbacks if anything breaks.

**Walkthrough sequence:**

1. **Home page on meta_ios** (90s). "Baseline iCAC card — blue bar is posterior median, whiskers are 94% CI, orange dashed band is the lift-test truth ± $50. meta_ios sits comfortably inside its truth band. Switch to meta_web — you can see the $276 posterior just above the upper bound." Click iROAS card briefly, then click time-series tabs to show iCAC over time and spend overlay.
2. **Decisioning Summary** (60s). "All 19 channels in one view. Lift-tested seven on top with PASS/FAIL on the windowed gate, untested twelve below with aggregate iCAC. Sortable on every column. CSV download for your team's own slicing."
3. **OOT Validation** (60s). "Model 1 left, Model 2 right. The +14.96% disclosure I just walked through is right there at the bottom of the Model 2 chart."
4. **Methodology** (45s). "Baseline decomposition, the per-channel concentration table with the 1.04x meta_web row, view-through explanation, and the data-scope ask in plain English."

**If anything breaks:** "Let me pull this up as a screenshot" — flip to the fallback slides and talk the same way.

**Live-demo watch-out — internal codes visible on the dashboard:**
- OOT Validation page title: "Model 1 OOT — D-γ trend control (D028)"
- Methodology page title: "Methodology — Baseline Decomposition & Per-Channel Concentration (D029)"

If Abheek points at these: *"Those are our internal version stamps for the canonical specification. The page content below the title is what they actually changed."*

---

## Slide 13 — The two blocking questions (3:00)

This is the headline ask of the meeting. Slow down here.

**Question 1 — attribution-feed.**

> "Can Kikoff share a Northbeam attributed-revenue CSV — weekly attributed LTV by channel, for our 2024-07 to 2026-03 window? Daily would also work."

> "Why this matters: it refits the model on the same universe your <20% baseline target was framed against. Today's deck reports a global 67% baseline because the model is fit on total LTV. With the attributed feed, we fit on the attributed-revenue universe directly, and the baseline conversation tightens to the apples-to-apples ~50%, with the option to reinstate a tighter threshold on that scope."

> "Roughly one sprint to refit and re-report. Inside Phase 2 deadline if data lands in the next ~5 days."

> "If the answer is no, we publish the 45–53% reframe as our defensible band, and a reviewer can fairly push back that the reframe rests on the approximate ~35% organic split."

**Question 2 — May 2025 Meta Web spend-basis.**

> "Two interpretations of the lift-test CSV cell. Option 1: channel-level Meta Web spend with an 88% / 12% treatment-vs-holdout split — our current working assumption. The Meta Web $276 number stands."

> "Option 2: one cell of a 3-cell platform test, so 33% of platform spend — would require ×3 scaling. Meta Web would drop to ~$86. The whole calibration story changes — we'd be over-corrected."

> "Empirical evidence favors Option 1. Actual 8-day Meta Web spend was $214,096. The CSV cell is $176,972. Ratio 1.21 — matches 1/0.88. Doesn't match the 3.0 we'd expect under Option 2."

> "But this is your data. We need confirmation to lock it before Phase 2 close."

**Internal map:**
- Question 1 = Q36 (For Client) — `state/open_questions.md`
- Question 2 = D027 open spend-basis (postponed from 2026-05-19 meeting)
- Clarification draft: `drafts/abheek_spend_basis_clarification_2026-05-18.md`

**Anticipated Abheek question:** *"How much of a lift is the Northbeam pull for our team?"*
**Prepared response:** *"That's your read. If Northbeam stores attributed-revenue at weekly granularity it should be a CSV export. We'd ideally want the same channel taxonomy as the spend CSV we already have, so we can join cleanly. If column mapping is hard, we can do it on our side."*

**Anticipated Abheek question:** *"What if the Northbeam pull lands at 7+ days from today?"*
**Prepared response:** *"At ~5 days from today we can refit and ship inside the Phase 2 deadline. At 10+ days we'd publish the 45–53% reframe and treat the attributed refit as Phase 3 scope. Both are defensible; the first is tighter on your target."*

---

## Slide 14 — Three judgment calls (2:30)

> "Three places where your judgment shapes the deliverable. None are blocking; all affect what we ship at Phase 2 close."

**Judgment 1 — Meta Web $69 above the truth band.**

> "Inside your safety range. Diagnostic plans on file — we could chase a saturation curve sensitivity or check OVB from the 12 untested channels. Want us to pursue, or document this as a narrow miss and ship?"

**Judgment 2 — TikTok iOS $288 vs truth $109.**

> "0.79x inverse concentration reads as pacing confound, not a prior-tightness problem. Tightening TikTok iOS σ in isolation risks contaminating other channels' iCACs — we have evidence the ±$30 spec-variation band is real. Document as structural limitation, or attempt remediation knowing the cross-channel risk?"

**Judgment 3 — Model 2 +14.96% OOT bias.**

> "We have one held remediation slot — Model 2 with both a linear trend and an LTV-per-conv regressor. ~25 minutes of MCMC. Same calibration-noise risk on Model 2 iCACs that we surfaced for Model 1 — it could shift channel numbers on the Decisioning Summary. Try before freeze, or ship Model 2 with the bias openly documented?"

**Internal map:**
- Judgment 1 = M3.5d diagnostic in sprint.md
- Judgment 2 = M3.5c diagnostic + the Q35 cross-channel risk
- Judgment 3 = M3.5g held slot, v2-C architecture

---

## Slide 15 — Path to Phase 2 final (1:00)

Walk the table. Don't over-explain.

> "Phase 2 freeze 2026-06-06. If both blocking questions resolve today, we have about 9 working days of headroom. Order matters — attribution-feed answer drives the biggest piece of work; spend-basis confirmation drives whether the Meta Web story changes shape."

> "Independent of your answers, we still need: saturation diagnostics for the 12 untested channels, the Decisioning Summary 'Spend Move to Test' column populated, and the executive summary deliverable. Each is a 2–3 day item."

**Internal map:**
- M3.5c TikTok iOS diagnostic in sprint.md
- M3.5d Meta Web residual diagnostic in sprint.md
- M3.5g held remediation slot for M2 OOT — available if reopened before freeze
- Phase 2 freeze date: 2026-06-06

---

## Slide 16 — Reference files (0:30)

> "All canonical scripts, metric files, and the dashboard are listed here. Happy to walk through any implementation detail after the meeting."

---

## Pre-meeting actions

- [ ] Confirm dashboard launches: `my-notebook-project/.venv/bin/streamlit run app/dashboard.py`
- [ ] Click through all 3 pages once to warm Streamlit caches before the call
- [ ] Verify fallback screenshots render correctly in the HTML deck
- [ ] Have `outputs/P2_04_full_channel/metrics/ltv_window_scaled.json` open in a tab for live number lookup
- [ ] Decide *before* the meeting how you want to handle the Decisioning Summary "Spend Move to Test" column — Abheek will probably ask

## Post-meeting actions

- [ ] Document attribution-feed answer + spend-basis confirmation in `state/supervisor_qa.md`
- [ ] If attribution-feed confirmed: open sprint task for refit on attributed universe
- [ ] If Option 2 confirmed: re-open D027 + redo Meta Web calibration story
- [ ] If any judgment call answered: update sprint.md milestones accordingly
- [ ] Refresh `state/sprint.md` with new sequencing

---

## Live demo watch-out — dashboard has visible internal codes

The dashboard pages themselves contain internal-code references that will be visible during live demo:
- OOT Validation chart title: "Model 1 OOT — D-γ trend control (D028)"
- OOT Validation footer: "Base canonical: M3.5b_Fix_A_2026-05-19 (Lever C lam Gamma(2,2) + HalfNormal(β), GeometricAdstock l_max=8, Fix-A windowed lift priors)"
- Methodology page title: "Methodology — Baseline Decomposition & Per-Channel Concentration (D029)"

If Abheek asks what D028 / D029 / M3.5b mean: *"Those are our internal version stamps for the decisions and the canonical specification — the page content below the title is what they actually changed."*

If you want to scrub these before the meeting: edit titles in `app/pages/2_OOT_Validation.py` and `app/pages/3_Methodology.py`.

---

## Number cheat-sheet (live lookups)

| Question | Answer | Source |
|---|---|---|
| Meta Web Model 2 windowed iCAC | $276.45 | `ltv_window_scaled.json` |
| Meta Web Model 1 windowed iCAC | $280.60 (canonical) / $247.70 (with trend control) | `mechanism2b_window_scaled.json` |
| Model 1 OOT MAPE | 16.13% | `oot_model1_conversions.json` |
| Model 1 OOT sMAPE | 16.41% | `oot_model1_conversions.json` |
| Model 1 OOT signed mean | −3.66% | `oot_model1_conversions.json` |
| Model 1 OOT over-pred | 4 of 13 | `oot_model1_conversions.json` |
| Model 2 OOT MAPE | 15.13% | `oot_model2_ltv.json` |
| Model 2 OOT sMAPE | 13.84% | `oot_model2_ltv.json` |
| Model 2 OOT signed mean | +14.96% | computed from predicted_weekly vs actual_weekly |
| Model 2 OOT over-pred | 12 of 13 (week 9 / 2026-03-02 under by −1.11%) | computed |
| Global baseline | 67.33% | `baseline_split.json` |
| In-window baseline | 61.32% | `baseline_split.json` |
| Out-of-window baseline | 68.32% | `baseline_split.json` |
| Apples-to-apples point estimate | 49.74% (at organic = 35%) | `baseline_split.json` reference block |
| Apples-to-apples band | 45.55%–53.33% (organic ∈ {30%, 35%, 40%}) | `baseline_split.json` reference block |
| meta_ios concentration | 2.35x | `baseline_split.json` |
| meta_web concentration | 1.04x | `baseline_split.json` |
| tiktok_ios concentration | 0.79x (inverse) | `baseline_split.json` |
| Convergence (M2 canonical) | R-hat ≤ 1.004, ESS ≥ 2,096, divergences 0 | `ltv_window_scaled.json` `convergence` |
| Channels in band post-Fix-A | 5 of 7 (was 2 of 7) | `ltv_window_scaled.json` `windowed_icac` + `gates` |
| Per-test scaling factors (Fix-A) | Meta May ×1.75, TikTok Aug ×1.1667, CTV Oct ×1.037, Meta Jan ×2.8 | journey doc §2.4 |
| Window-basis arithmetic | $508,038 (14-day) ÷ 1,128 (8-day) = $450 | `i7_window_reconciliation_2026-05-18.md` |
| Phase 2 freeze date | 2026-06-06 | sprint.md |
