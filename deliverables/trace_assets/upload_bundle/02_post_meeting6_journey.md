# Post-Meeting-6 Modeling Journey (2026-05-12 → 2026-05-20)

**Purpose:** Honest reference document of what happened between Client Meeting 6 (2026-05-12) and 2026-05-20. Voice is factual, non-persuasive — where something didn't work, it is said so; where a recommendation has uncertainty, it is surfaced; where the model has scope limitations, they are named.

**Audience:** Yash (internal reference) and the TRACE + Abheek presentation chats tomorrow (handoff input). This document is **not** a client artifact and is **not** the source of any final client-facing language.

---

## §1 — Where we were after Meeting 6

After the 2026-05-12 walkthrough, the architectural shape of the model was validated by Abheek and the calibration was not. The deck and dashboard (`deliverables/10_abheek_phase2_results.qmd`, `app/dashboard.py:84–301`) showed: full-channel weekly Mechanism 2 windowed-prior architecture, two models (conversions + LTV_3YEAR), 8-column decisioning row format for Meta Web, and saturation curve format — all approved live. The numbers on top of that architecture missed: Meta Web Model 2 baseline iCAC = **$652** (94% HDI ~$570–$750) vs. Abheek's stated truth bracket of **$156 (lift) ≤ truth ≤ $300 (Abheek hunch); $200–$225 leadership prior**. Five of the seven lift-tested channels missed the benchmark uniformly **by being above it** under the aggregate-iCAC gate then in use.

Abheek's directives at meeting close, summarized:

| Directive | Source (meeting fact #) | What it asked us to change |
|---|---|---|
| Tighten Meta + TikTok lift-test σ (stop using the 30%-heuristic; use a CLS-appropriate σ) | #15, #16 | Replace the 30% heuristic; CTV σ stays |
| Use a **windowed-iCAC gate** during the test window, not full-history aggregate | #11 | Drop the aggregate gate; compute model-iCAC during the test weeks and compare to truth band |
| Re-include Meta Jan 2026 cancelled test as a windowed prior | #17 | Reverses prior decision to exclude |
| Drop the iOS > Android iCAC ordering gate (do not flip it) | #18 | Neither direction is a remediation target |
| Set Kikoff-specific baseline target **< 20%** | #10, #20 | Replaces industry 30–70% and code's <80% |
| Run the full thing on **all channels**, not Meta Web only | #26 | All-channel replication before next meeting |
| Build out-of-time validation (Abheek's stated primary MMM metric) | #25 | Not yet built |
| Acknowledge view-through: pulling Meta Web spend causes both attributed and blended numbers to drop within a week → Meta Web sits in a saturated, **high-marginal-efficiency** regime | #12, #13 | Model's $652 implies the opposite |

The two big substantive corrections — windowed gate and σ tightening — were targeted directly at the $652 number, and Abheek's framing made it explicit that the right calibration check is the **model's iCAC during the May 2025 test window** falling inside $156 ± $50 = **$106–$206**.

---

## §2 — What we tried, in order

The work between 2026-05-12 and 2026-05-20 is best described as a chain of attempts, not a single fix. Some moved the model. Some did not. Some changed the framing of the problem.

### 2.1 — M3.5 (σ recalibration + Lever C lam prior, 2026-05-18)

What we did: dropped the 30%-of-δ_y σ heuristic in favor of a **σ Path B literature default ≈ 10% of point estimate** (D022) for Meta + TikTok lift-test priors; kept CTV's CI-derived σ = 373 (D020) untouched; re-included Meta Jan 2026 as a wide-σ windowed prior (D019-rev); replaced the aggregate-iCAC gate with a windowed-iCAC gate (D023); dropped the iOS > Android ordering gate (D024); set baseline gate to <20% (D021); and promoted **Lever C** — LogisticSaturation with `lam ~ Gamma(2,2)` + `beta ~ HalfNormal(2)` priors — as the M3.5 canonical saturation specification (D025).

What worked: Lever C produced dramatically cleaner Bayesian diagnostics at the same iCAC story — **R-hat 1.011 → 1.003, ESS 268 → 2,218, divergences 35 → 0 (Model 2)**. The lift priors no longer needed a slow-mixing posterior to read against. Three independent diagnostics (σ ladder 30%→10%→5%, alternative HillSigmoid saturation, tighter Lever C lam prior) all landed Meta Web at $465 ± $7 — i.e., the structural iCAC under windowed priors was robust to these knobs.

What did **not** work: the Meta Web windowed iCAC did not collapse to truth band. It moved from $652 (M3 aggregate) to **$466 (M3.5 windowed)** — better, but still ~$260 above the truth-band upper.

What we learned: σ slackness was not the dominant driver of the gap. The original "the 30% heuristic is loose" hypothesis from Abheek (M6 fact #15, #18a) was empirically refuted by the σ ladder. Convergence got dramatically better at the same iCAC, but the calibration miss was structural to something else.

### 2.2 — Investigation I-7 (window-basis reconciliation, 2026-05-18)

What we did: opened the question "what is the model's windowed gate actually comparing?" Worked through the basis arithmetic by hand in `drafts/i7_window_reconciliation_2026-05-18.md`.

What we found: the windowed-iCAC gate was comparing the model's **14-day W-MON window spend** ($508,038 over the two W-MON weeks overlapping Meta May 2025) against the lift-test's **8-day δ_y** (1,128 conversions). Mechanically: $508,038 / 1,128 = **$450** — almost exactly the $466 the model was reporting. The model had no degrees of freedom to disagree because the prior was forcing it onto the wrong basis. CSV truth iCAC ($156.89) is on a consistent 8-day basis. On a corrected 14-day basis, the implied truth becomes ~$257. The "$300 gap" we had been calling a calibration miss collapsed to ~$10–$70 on consistent basis.

What we learned: a chunk of the residual was an arithmetic artifact of the windowing math, not a model problem.

### 2.3 — Investigation I-5 (direct posterior saturation extraction, 2026-05-18)

What we did: extracted the posterior iCAC curve from the canonical Model 2 trace at two spend levels.

What we found (`outputs/diagnostics/meta_web_saturation_summary.json`):
- At TEST-cohort weekly spend ($154k/wk): iCAC = $469 [HDI 398, 565]
- At FULL-channel typical weekly spend ($323k/wk): iCAC = $492 [HDI 414, 599]
- Change across test → typical (a 2× spend range): **+4.8%**

What we learned: the "saturation at scale" framing we had drafted in `proposals/2026-05-18_m3_5_calibration_result.md` (i.e., "the test ran at marginal spend, the model reports steady-state at typical spend") was **refuted**. A steep saturation curve would have produced a much larger iCAC difference across that 2× spend range. The framing was dropped (D026, drafted-and-dropped 2026-05-19). Whatever was producing the $466 was not saturation-at-scale.

### 2.4 — D027 Fix-A (window-basis correction, 2026-05-19)

What we did: scaled each lift-test row's δ_y and σ by `(W-MON window days / test days inclusive)` so the prior and the model both speak in the same weekly cadence. Per-test factors: Meta May ×1.75, TikTok Aug ×1.1667, CTV Oct ×1.037, Meta Jan ×2.8. Wide-σ rule preserved for Meta Jan. Applied in `scripts/08b_mechanism2_more_tune.py` and `scripts/09_ltv_model.py`.

What worked, by channel (Model 2 windowed iCAC, truth ± $50):

| Channel | Truth | Pre-Fix-A | Post-Fix-A (M2) | Pass? |
|---|---:|---:|---:|:---:|
| meta_ios | $135 | $230 | $137.19 | PASS |
| meta_android | $63 | $147 | $85.18 | PASS |
| meta_web | $156.89 | $466 | $276.45 | **FAIL** ($73 above upper) |
| tiktok_ios | $109 | n/a | $287.93 | **FAIL** ($129 above upper) |
| tiktok_android | $82 | n/a | $111.24 | PASS |
| tiktok_web | $112 | $155 | $134.64 | PASS |
| ctv | $135 | n/a | $138.64 | PASS |

5/7 channels in band (was 3/7). Meta Web moved $466 → $281 (M1) / $276 (M2) — a **40% drop**. Diagnostics: R-hat ≤1.005, ESS ≥2,094, divergences 0 (M2).

What did **not** work as Abheek had predicted: baseline % did **not** drop materially. Abheek (M6 #20) had said calibrated Meta Web priors should pull spend out of baseline into the channel. Post-Fix-A baseline went from 73.1% → 69.4% (M1) and 70.4% → 67.3% (M2) — a **small decrease (3.1–3.7pp), not the "material" drop predicted**. The mechanism appeared to be that the prior had shifted Meta Web's level but had not redistributed attribution. The reason for that was not yet visible at this point in the journey.

D027 was APPROVED with a **working assumption (Option 1)** on the spend basis — that the CSV's $176,972 cell is channel-level Meta Web spend with 88% treatment / 12% holdout. Empirically supported by the ratio of 8-day actual Meta Web spend ($214,096) to CSV cell ($176,972) of 1.21, which is consistent with the 88%-treatment interpretation (expected 1/0.88 ≈ 1.14) and inconsistent with the alternative 33%-of-platform-cell interpretation (expected 3.0). If Abheek later confirms Option 2, additional ×3 scaling is required and Meta Web drops to ~$86 — D027 re-opens. The 2026-05-19 client meeting was POSTPONED, so this is open.

### 2.5 — M5 + M6 (decisioning + full-channel dashboard, complete 2026-05-19)

What we did: Completed the all-channel rollout Abheek asked for (M6 fact #26). `app/dashboard.py` now loops over all 19 channels (`CHANNELS_LIFT_TESTED` + `CHANNELS_UNTESTED`); `app/pages/1_Decisioning_Summary.py` produces a 19-row 8-column decisioning table with the D015 confidence-derivation rule (HIGH/CAUTION/LOW from posterior signals, not copied from Abheek's trust intuitions); CSV export available; all 19 channels' `*_baseline.json` stamped `canonical_version: M3.5b_fix_a_2026-05-19`.

No additional substantive findings here — this was a replication of the Meta Web template that Abheek had already approved.

### 2.6 — M7 Out-of-time validation (2026-05-19)

What we did: trained canonical M3.5b Fix-A on the first 79 W-MON weeks (2024-07-01 → 2025-12-29) and held out the last 13 (2026-01-05 → 2026-03-30). Ran via `scripts/11_oot_validation.py`. Computed weekly posterior-predictive vs. actuals.

What we found (the headline number) — Model 1 (y=conversions) **OOT MAPE 18.83%**; Model 2 (y=LTV_3YEAR) **OOT MAPE 15.13%**. Both inside the industry 15–25% MMM band. Convergence clean on both: R-hat ≤1.0036, ESS ≥2,098, 0 divergences.

What we found (the catch): **predicted mean exceeded actual in all 13 of 13 hold-out weeks for both models**. Signed mean residual: M1 +18.83%, M2 +14.96%. HDI89 coverage 7.7% (1 of 13 weeks covered) — the posterior was underdispersed for out-of-sample prediction. The over-prediction was 100% one-directional, not symmetric noise around zero. We documented this as **Q34** and raised it as a structural finding rather than a fitting failure.

### 2.7 — Q34 remedy attempt #1 (D-γ linear trend control, 2026-05-20)

What we did: added a linear week-index control `t = (week − first_week).days / 7` to the MMM via PyMC-Marketing's `control_columns`. Hypothesis was that the all-13-weeks over-prediction was secular drift the model could not absorb through baseline (constant) or channels (grow with spend). Scripts: `scripts/12_q34_diagnostic.py`, `scripts/12b_q34_structural_diag.py`, `scripts/13_oot_remediation_v1.py`.

What worked for M1: clean improvement.
- MAPE 18.83% → 16.13% (−2.70pp)
- Signed mean +18.83% → −3.66% (sign flipped, magnitude inside ±5%)
- Over-pred 13/13 → 4/13
- HDI89 coverage 7.7% → 38.5%
- Convergence still clean.

What did **not** work for M2: over-correction.
- MAPE 15.13% → 15.00% (−0.13pp — virtually no change)
- Signed mean +14.96% → **−14.00%** (sign flipped, **same magnitude** in the wrong direction)
- Over-pred 12/13 → 1/13
- HDI89 coverage 7.7% → 38.5%

What we also found: a single channel iCAC moved by $32.90 (Model 1 meta_web canonical $280.60 → D-γ $247.70). All channel iCACs moved DOWN under D-γ (channels absorbed residual that trend control had taken out of baseline). This breached the ±$30 gate-c threshold we had set for iCAC regression.

What we then did: a 4-config prior-strength sweep on the new `gamma_control` term (σ ∈ {2.0, 0.10, 0.05, 0.02}). Script: `scripts/13c_q34_gamma_sweep.py`.

What that produced: posteriors **identical across all 4 configs** to 3 decimals (M1 |gamma| ≈ 0.014, M2 |gamma| ≈ 0.011). Even at σ=0.02 the prior never bites — 3σ = 0.06 is far outside the posterior's |gamma| ≈ 0.014. The model is informative-enough that the prior on the new term contributes essentially nothing.

What we learned (a methodological surprise): **a single added control variable in the MMM rebounded a channel iCAC by $33, and we have no prior we can use to dampen the rebound**. This was raised as **Q35 — lift-prior σ=10% (Path B) calibration ceiling** — independent of whether D-γ is adopted. The implication is that publishing windowed iCAC as a single point estimate understates true uncertainty under realistic spec variation. (See §4 below.)

What we learned (the M2 mechanism): we computed training-vs-OOT means by hand (no MCMC needed).
- Mean weekly conversions: training 18,462 / OOT 18,429 → effectively flat (training OLS slope projects OOT week 85 at 20,055 → trend **overshoots actual by 8%**, i.e., conversion volume plateaued in OOT).
- Mean weekly LTV-per-conv: training $206.93 / OOT $215.20 → **+4.0% sustained elevation** in OOT.

M1 has ONE drift to absorb (conv-volume plateau) → trend captures it cleanly. M2 has TWO drifts that diverge from training joint pattern in OOT (conv-volume plateau + LTV-per-conv elevation) → a single `gamma_control` coefficient cannot disentangle them and **over-corrects** by extrapolating the conv-volume drift too steeply when OOT conversions plateaued but LTV-per-conv stayed elevated. This was the **asymmetric-driver hypothesis** — and it was refined (and partially refuted) by the next attempt.

D-γ was ruled out as a symmetric (both-model) remedy. The result was documented as a negative result (`proposals/archived/2026-05-20_q34_d_gamma_negative_result.md`).

### 2.8 — Q34 remedy attempt #2 (D-ε asymmetric, 2026-05-20)

What we did: tested an explicitly asymmetric architecture. M1 stays at D-γ. M2 gets three combined adjustments: DP-1A (data-driven weekly `avg_ltv_t` series); DP-2α (per-test-window lift-prior rescaling using window-mean `avg_ltv_t`); DP-3γ (post-multiply OOT predictions by `avg_ltv_oot_extrap / avg_ltv_train_mean` ratio, ~1.029). Script: `scripts/14_oot_remediation_v2.py`. The hypothesis was that M2 had two drifts compounding, and DP-3 γ would scale predictions up to "account for" the LTV-per-conv elevation in OOT.

What did **not** work: M2 was made **worse** than the canonical baseline.
- M2 MAPE: 15.13% → **18.46%** (worse)
- M2 signed mean: +14.96% → **+18.46%** (worse than baseline; wrong direction from D-γ M2)
- M2 over-pred: 12/13 → **13/13** (worse)
- M2 HDI89: 7.7% → 7.7% (no improvement)

Why DP-3 γ failed (refined mechanism, **directionally backwards** from the previous attempt's premise): the channel-beta × spend product at OOT already predicts more conversions (because spend keeps growing +14% Q4→Q1) → more LTV. Actual OOT: conversions plateaued, LTV-per-conv elevated. The implicit decomposition the model is doing is `actual_LTV = lower_conv × higher_LTV_per_conv`. The model's implicit decomposition is `extrapolated_higher_conv × training_avg_LTV_per_conv`. The LTV-per-conv elevation in OOT **partially offsets** the conv-volume drift in M2's baseline — it does NOT compound it. That's why M2's baseline bias (+14.96%) is **smaller** than M1's (+18.83%) by ~4pp. Multiplying M2 UP by +2.9% adds more bias on top of an already over-correcting prediction.

What we then tested (no MCMC, just algebra): a v2-A arithmetic projection `M2_v2A_pred = M1-D-γ_pred × (avg_ltv_oot / avg_ltv_train)`, mathematically equivalent to a two-stage `M2 = M1-D-γ_conv × extrapolated_avg_ltv` architecture (v2-B).

What v2-A/v2-B produced:
- M2 signed mean: −4.59% (passes ±5% threshold — barely)
- M2 MAPE: 16.47% (**+1.34pp WORSE** than baseline 15.13%)
- M2 HDI89: 0.0% (vs. baseline 7.7% — also worse)
- Per-week multiplier range across 13 weeks: 0.6520–1.0967; per-week errors swing from −24.6% to +32.6%. Signed mean centers near zero by averaging large opposite-sign errors, not by reducing per-week error.

What we learned: every architectural M2 remedy in the class we tested **trades systematic bias for week-to-week noise OR pushes M2 in the wrong direction**. Both compromises are publication-defensible problems but different ones. The cleanest M2 remedy (two-stage v2-B) discards M2's posterior-predictive entirely at OOT — significant disclosure cost.

### 2.9 — D028 resolution (asymmetric ship, 2026-05-20)

Decision (`proposals/archived/2026-05-20_d028_M1_D_gamma_promotion.md`):
- **Path 2:** M1 OOT canonical = D-γ trend control. New canonical script `scripts/11b_oot_validation_M1_D_gamma.py`. M1 fit-time outputs (saturation, gate-c iCAC, decisioning page) **unchanged**; D-γ applies only to the OOT-validation fit.
- **Option α:** M2 stays canonical M3.5b Fix-A. The +14.96% OOT over-prediction is accepted as a **documented limitation** in the deliverables (methodology slide + appendix). M2 MAPE 15.13% sits inside the industry-acceptable 15–25% band — defensible to publish with the disclosed bias.
- **Accepted-cost:** M1 meta_web windowed iCAC drift of −$32.90 (canonical $280.60 → D-γ $247.70). This is treated as Q35-bounded calibration noise. It is **internal-only** — the Decisioning Summary and main dashboard both read M2-derived files (`app/pages/1_Decisioning_Summary.py:144-149`, `app/dashboard.py:85,141`), so M1 iCAC is never client-visible. The drift exists only on the OOT Validation page, where the D-γ improvement story is itself the disclosure.

Q34 RESOLVED.

### 2.10 — M3.5e baseline gate redesign (2026-05-20)

What we did: empirically split global baseline into in-window (12 union weeks across all 7 lift-test windows) and out-of-window (81 weeks) components. Hypothesis was: windowed priors push attribution into windows, so baseline is structurally elevated outside them; the right gate is "in-window baseline < X%." Script: `scripts/15_baseline_split.py` (fit-untouched; reads the canonical M2 trace only).

What we found (`outputs/P2_04_full_channel/metrics/baseline_split.json`):
- Global baseline = 67.33%
- In-window baseline = 61.32%
- Out-of-window baseline = 68.32%
- Δ (in vs out) = **7pp only** — modest concentration effect, not the dramatic split the hypothesis assumed
- The in-window 61% is still **41pp above the D021 <20% target**, so the "within-window <20%" reframe is also architecturally unreachable

We then computed per-channel attribution **concentration ratios** = (in-window $/wk) / (out-of-window $/wk):

| Channel | Concentration ratio | Reading |
|---|---:|---|
| meta_ios | 2.35x | Concentrated (prior bites) |
| tiktok_web | 1.61x | Moderate |
| meta_android | 1.56x | Moderate |
| ctv | 1.11x | Slight |
| **meta_web** | **1.04x** | **Flat — prior shifted level, did NOT redistribute attribution** |
| tiktok_android | 0.96x | Flat |
| **tiktok_ios** | **0.79x** | **INVERSE — channel contributes more outside its window than during** |

What we learned: cross-referencing the meta_web 1.04x against Meeting 6 fact #13 (verbatim from raw, 21:02–25:35): *"a large portion of view-through attribution flows from Meta Web. Every time Meta Web spend is scaled up, attributed conversions don't spike in dashboards (because of view-through), but blended numbers grow consistently."* Our model's X carries no view-through proxy, so the Fix-A lift-prior can only shift Meta Web's mean level ($466→$281) — it cannot redistribute attribution into the test window because the true coupling between Meta Web spend and conversions is **view-through-mediated and invisible to X**. The 1.04x ratio is the in-model fingerprint of that mechanism.

Connection back to Meeting 6: the same fact #13 also revealed that Abheek's "baseline <20%" target was framed against the **attributed-revenue universe** (~65% of total revenue per Northbeam's initial run) — not the total-LTV universe our model is fit on. The 65/35 split is approximate (Abheek's number, not a precise statistic). On the apples-to-apples attributed-revenue universe, our baseline ≈ **49.74%** (point estimate at organic = 35%), with a ±5–10pp uncertainty band of **45–57%** depending on whether the true organic share is 30%, 35%, or 40%. The gap to D021's target is ~30pp at the anchor and materially > 20pp at either end of the band.

### 2.11 — D029 resolution (deprecate baseline gate, 2026-05-20)

Decision (`proposals/archived/2026-05-20_d029_baseline_gate_redesign.md`):
- D021's <20% baseline gate **deprecated** (not retuned). The DP-C decision tree would have landed on a retune to `max(in-window) × 1.1 ≈ 67%`, which reads as a goalpost-move dressed as methodology and provides no actionable signal.
- **Per-channel concentration ratio** adopted as the new attribution-confidence diagnostic. ≥1.5x = concentrated (prior bites); 1.1x–1.5x = moderate; ≤1.1x = level-shifted but not attribution-redistributed; <1.0x = inverse (diagnostic-only).
- Baseline % still **reported** (global, in-window, out-of-window) on the main dashboard model-health bar, with neutral coloring and a tooltip pointer to the new Methodology page — but no PASS/FAIL flag.
- **Q36 surfaced as data-scope ask:** "Can Kikoff provide an attributed-revenue LTV feed (Northbeam attributed-revenue CSV or equivalent)?" For Client. If yes, the model can be re-fit on the attributed universe and a tighter baseline threshold can be reinstated on that universe.
- New page `app/pages/3_Methodology.py` covers baseline decomposition, per-channel concentration, view-through mechanism, data-scope ask, and the D029 supersession rationale.

Both D028 and D029 landed on 2026-05-20.

---

## §3 — Where we are now (current model state)

Be precise. These are the numbers as of 2026-05-20.

### Lift-test calibration (windowed iCAC, post-Fix-A, M2 unless noted)

| Channel | Truth ± $50 | M2 windowed iCAC | Status |
|---|---|---:|---|
| meta_ios | $85–$185 | $137.19 | PASS |
| meta_android | $13–$113 | $85.18 | PASS |
| meta_web | $107–$207 | $276.45 | **$73 above truth-band upper; inside user safety band $107–$300** |
| tiktok_ios | $59–$159 | $287.93 | **$129 above truth-band upper** |
| tiktok_android | $32–$132 | $111.24 | PASS |
| tiktok_web | $62–$162 | $134.64 | PASS |
| ctv | $120–$150 | $138.64 | PASS |

5/7 in band (was 3/7 pre-Fix-A).

### OOT validation (after D028)

- **Model 1 (y=conversions), D-γ trend control:** MAPE **16.13%**, signed mean **−3.66%**, over-pred 4/13, HDI89 cov 38.5%, R-hat 1.0056, ESS 1208, divergences 0. Stamp: `M3.5b_fix_a_2026-05-20_oot_M1_D_gamma_v1`.
- **Model 2 (y=LTV_3YEAR), canonical M3.5b Fix-A:** MAPE **15.13%**, signed mean **+14.96%** (documented limitation), over-pred 12/13, HDI89 cov 7.7%. Stamp: `M3.5b_fix_a_2026-05-19_oot_v1`.

### Baseline (after D029)

- Global baseline = **67.33%** (M2).
- In-window baseline = 61.32% (12 union weeks); out-of-window = 68.32% (81 weeks); Δ = 7pp only.
- Decomposition (approximate): **~35% irreducible organic LTV** (per Abheek/Northbeam, Mtg 6 #13) + **~32pp missed paid attribution** (largely Meta Web view-through; mechanistically confirmed by meta_web 1.04x concentration).
- Apples-to-apples baseline on attributed-revenue universe ≈ **45–57% band** (point estimate 49.74% at organic = 35%). D021 <20% gate deprecated; per-channel concentration is the new attribution-confidence diagnostic. Threshold gate is gone.

### Per-channel concentration diagnostic

meta_ios 2.35x · tiktok_web 1.61x · meta_android 1.56x · ctv 1.11x · meta_web **1.04x** · tiktok_android 0.96x · tiktok_ios **0.79x**.

### Bayesian diagnostics (canonical M3.5b Fix-A, M2)

R-hat ≤ 1.005 PASS; ESS ≥ 2,094 PASS; divergences = 0 PASS.

### Decisions that landed 2026-05-20

- **D028** — M1 D-γ canonical for OOT; M2 stays canonical with +14.96% documented limitation; Q34 RESOLVED.
- **D029** — D021 deprecated; per-channel concentration diagnostic + data-scope disclosure; M3.5e CLOSED.

---

## §4 — Open items (honest — solvable vs. data-scope)

The items below are distinguished by whether they could be closed by in-session work or whether they require something external (Abheek data, a client meeting decision).

### Solvable in-session if we choose to spend the cycles

- **M3.5c TikTok iOS new failure ($289 vs truth $109, gap +$180).** The largest post-Fix-A residual; surfaced only because the gate was fixed. The concentration ratio of 0.79x (inverse — channel contributes more outside its window than during) suggests this is likely a **pacing-confound analog to Q23** (campaigns paced toward high-conversion periods → time-series signal dominates the lift prior). Diagnostic plan exists in sprint.md M3.5c sub-tasks (`scripts/12_tiktok_ios_diagnostic.py` planned; filename collides with the existing `scripts/12_q34_diagnostic.py`, will need renaming). Remediation risk: tightening TikTok iOS σ in isolation may cross-contaminate other channel iCACs through the same gate-c mechanism Q35 surfaced. Worth doing as a **diagnostic** (to characterize the failure); whether to remediate depends on whether the cross-channel cost is acceptable. **Realistically, this looks structural — likely cannot be cleanly fixed; documenting it is the more defensible outcome.**

- **M3.5d Meta Web $73 residual above truth-band upper.** Inside the user safety band ($107–$300); outside truth band by 35% of the upper. Diagnostic plan in sprint.md M3.5d. Lower priority than M3.5c because the channel is at least inside the user safety band. Three interpretations on the table (OVB from 12 untested channels with weakly-informative defaults; cross-channel σ tension from TikTok iOS; saturation curve shape via Lever C lam prior). Branch flips entirely if Option 2 (33%-cell spend basis, see below) is confirmed by Abheek.

### Data-scope / disclosure items, not in-session fixable

- **Q35 — lift-prior σ=10% Path B fragility (~$30/channel iCAC drift per spec change).** Empirically: adding a single control variable to the MMM shifted M1 meta_web iCAC by $33 (12% of canonical), invariant to the new term's prior strength. The prior on `gamma_control` never bit. This is **not a calibration tunable** — the channel iCAC has a ~$30 ceiling of stability under realistic spec variation. Implication for deliverables: publishing windowed iCAC as a **point estimate** understates uncertainty. The defensible publication form is **iCAC ± a band**, where the band is informed by spec variation (~$30 at the σ=10% Path B level). Q35 sub-questions remain owner-decisions (Yash): (a) retighten priors to Path C (σ=5%) — risks reintroducing convergence issues seen at the σ=5% diagnostic (R-hat 1.107); (b) publish as a band. Not solvable in-session; this is a **disclosure issue**.

- **Q36 — attribution-feed ask.** For Client. Whether Kikoff can provide a Northbeam attributed-revenue CSV (or equivalent) at weekly or daily granularity. Our `data/MMM_UPDATED_LTV.csv` columns are [DS, CONVERSIONS, LTV_1YEAR, LTV_3YEAR] — total LTV only, no organic/paid attribution flag. Without this feed, D021's <20% target stays architecturally unreachable; baseline conversation stays anchored to the global 67% number rather than the apples-to-apples ~45–57% band. Requires data Abheek would need to source. **Not solvable in-session.**

- **D027 spend-basis confirmation (Option 1 vs Option 2).** Working assumption is Option 1 (channel-level / 88% treatment). Empirically supported by the 1.21 ratio of 8-day actual Meta Web spend to CSV cell. If Abheek confirms Option 2 (cell = 33% of platform) at the next meeting, additional ×3 scaling required, Meta Web drops to ~$86, and D027 re-opens. Clarification message `drafts/abheek_spend_basis_clarification_2026-05-18.md` exists; raise live at next meeting. The 2026-05-19 meeting was POSTPONED — date TBD.

### Held but not currently scoped

- **M3.5g — held remediation slot for M2 OOT.** Available if Yash reopens before deliverable freeze (~2026-06-06). Candidate remedies (all carrying significant cost): v2-C M2 `control_columns=["t", "avg_ltv_t"]` (carries Q35 calibration-ceiling risk on client-facing M2 iCAC); v2-B two-stage `M2_pred_oot = M1-D-γ × extrapolated avg_ltv` (carries disclosure cost that M2 posterior-predictive is discarded at OOT, HDI89 → 0%); Path C σ tightening (Q35 direct remediation; may reintroduce convergence issues). Not currently scoped.

---

## §5 — Things to verify or push back on

This section is the "second-opinion reviewer" pass on the work above. The intended use is to make sure these get pressure-tested before any client-facing language is produced.

### Point 1 — The 49.74% apples-to-apples baseline depends on Abheek's "~35%" organic being approximately right

The decomposition `total LTV = ~35% organic + ~65% attributed paid` is taken from Meeting 6 fact #13. That fact does not quote an exact number — Abheek says Northbeam's initial run "used attributed revenue only, ~65% of total revenue, since ~35% is organic / unattributed." We have built a +30pp gap-to-target story on top of that approximate split. The ±5–10pp band (45–57%) reflects the uncertainty (organic ∈ {30%, 35%, 40%}); we communicate it as a band, not a point. But there are three things a critical reader should flag:

1. We never asked Abheek for the **precise** Northbeam organic share. We inferred it from a verbatim quote in a meeting transcript. The qualitative conclusion ("gap > 20pp at either end of the band") is robust, but anyone questioning the methodology should be told: this is **Abheek's number from a meeting, not a quoted Northbeam statistic**.
2. The relationship `total_baseline_pct_our_model → attributed_baseline_pct_apples_to_apples` requires the assumption that the ~32pp "missed paid attribution" component is entirely paid (not also organic). If a chunk of that 32pp is actually organic LTV our model misclassified as baseline (rather than as a missed paid signal), the 49.74% point estimate moves accordingly. We have not done the sensitivity on this.
3. **An attributed-revenue feed (Q36) is the only way to actually settle this.** Until we have it, the 49.74% is a defensible reframe of an unverifiable point.

### Point 2 — meta_web 1.04x concentration: is "view-through" the only mechanism that explains it?

The story in D029 is: "the prior shifted Meta Web's level but did not redistribute attribution **because** the true coupling is view-through, which is invisible to X." That's mechanistically clean and Abheek's own diagnosis. But other mechanisms can produce a 1.04x concentration ratio too:

1. **Saturation curve doing the level work.** Under Lever C, the lam prior is tight (Gamma(2,2) — pulling toward small lam → steeper curve). A tighter saturation curve can produce a "drop the level, don't redistribute" pattern under a windowed prior, independent of any view-through. We have not isolated this. The M3.5d diagnostic plan (lam-prior sensitivity) is meant to test this.
2. **Mechanism-2 itself.** Our lift prior is a `pm.Normal` on the **sum of channel contribution inside the test window**. It anchors the in-window total but does nothing about the out-of-window total. A flat concentration ratio is mechanically what we would expect from this prior shape for any channel where the lift-test δ_y is small relative to the channel's full-history total — view-through or not. **This is the most important reviewer challenge.** We have asserted a mechanistic story (view-through) where the in-model artifact (Mechanism 2 prior shape) may be sufficient on its own.
3. **OVB from 12 untested channels.** If untested-channel contributions absorb some of what Meta Web should have, Meta Web's level drops but its distribution stays. Distinguishable from view-through only with a sensitivity test.

The view-through story is **directionally consistent** with both the data (1.04x) and Abheek's stated mechanism (Mtg 6 #13), but it is not the only story consistent with 1.04x. The conservative framing is: "1.04x is the in-model fingerprint of a level-shift without attribution-redistribution; the most likely mechanisms are view-through credit invisible to X (Abheek's hypothesis), the saturation curve doing the level work under Lever C, or Mechanism 2's prior shape itself."

### Point 3 — D028 asymmetric architecture: is the methodological inconsistency justifiable?

D028 publishes M1 OOT with a linear trend control and M2 OOT without one, using the same training data. There is a real methodological tension here. Two perspectives:

1. **Defense:** the asymmetry follows the data — M1 has one OOT drift, M2 has two divergent drifts. Applying the same remedy to both would over-correct M2 (we showed this empirically). A reviewer who cares about methodological consistency might still object that "the model should be the model, the OOT validation should not change the model spec asymmetrically."
2. **Challenge:** if the asymmetric architecture is right for OOT prediction, why is it not also right for the training-time fit? Why does M1 fit-time use no trend, but M1 OOT use a trend? The internal answer is: the training-time fit feeds the Decisioning Summary iCAC values, and applying D-γ at training time would surface a $32.90 drift on Meta Web iCAC into the client-visible dashboard — we chose not to pay that cost. A reviewer might fairly call this "we picked the architecture that produces the prettiest numbers in each viewport." The accepted-cost framing in D028 is honest about it, but a critical reader should see this as a **tension we resolved by hiding it**, not a tension we eliminated.

The most defensible thing to say in client materials is: "M1 OOT uses a linear trend control to absorb a secular conversion-volume drift that did not appear in training; M2 OOT does not, because the same control over-corrects M2's joint drift. M2's resulting +14.96% over-prediction is documented as a known limitation."

### Point 4 — The decision to ship-and-document M2 instead of further remediation — is that the right call?

The case for the call: every architectural M2 remedy we tested either (a) over-corrected, (b) traded systematic bias for week-to-week noise, or (c) discarded M2's posterior-predictive entirely. MAPE 15.13% is inside the industry-acceptable 15–25% band. The bias is one-directional and characterizable.

The case against: we have not exhausted the M2 remedy space. We have not tested Path C σ tightening on lift priors (Q35 direct), v2-C (M2 with both `t` and `avg_ltv_t` regressors), or a Fourier seasonality alternative. We have not tested any of these because the test cost is one MCMC fit each (~25 minutes) and they have known costs (Q35 risk on iCAC; convergence risk from σ=5%) that motivated deferring them. **A reviewer can fairly ask: did we ship M2 because the remaining remedies were all worse, or because we ran out of time?** The honest answer is partly both — we ran out of time to test them with confidence, **and** the ones we did test (D-γ M2, D-ε M2, v2-A/B projection) all had worse trade-offs.

A second sharper version of this: the v2-A/v2-B finding (that the cleanest path to fixing M2 OOT bypasses M2's posterior-predictive entirely) is a structural statement about our current architecture. It hints that **M2 may simply be the wrong unit to OOT-validate at weekly resolution under windowed priors with a fixed `avg_ltv_train`**. We are publishing M2 because Abheek asked for an LTV model, and OOT-validating it because Abheek asked for OOT validation. We are documenting the limitation because the architecture-as-fit cannot do both simultaneously without trade-offs we judge worse than the documented bias.

### Point 5 — Other things a critical reader might flag

- **Mechanism 2 windowing math** ("scale δ_y by W-MON_days / test_days") collapses one calibration miss but assumes the prior should be a flat scaling of the lift test. A reviewer who knows CLS literature may push on whether a per-day rate prior would be cleaner than a per-window total prior. We have not done that comparison.
- **The σ=10% Path B is not derived from CLS literature in any rigorous way.** It is "a defensible default" that we adopted because Abheek directed us away from the CSV's "confidence score" and we did not get raw control counts (Q30 still open). A reviewer who has done CLS work may know a tighter empirical anchor.
- **M1 fit-time vs M1 OOT-fit conceptual unity.** A reviewer may ask why we don't just publish both M1s — fit-time canonical for decisioning and D-γ for OOT — as **the same model** with the trend term present and let the gate-c drift hit the decisioning page transparently. The argument against doing that is precisely the Q35 surface-area cost; the argument for it is methodological clarity.
- **Decisioning Column E for Meta Web is currently HIGH (per D015 rule).** D029 flagged that the 1.04x concentration suggests CAUTION. We have not propagated this. This was flagged as a watch item for D030 but is not currently in scope.
- **The "5 of 7 channels in band" headline survives a pretty-far walk back if Option 2 is the right spend basis (Meta Web would drop to ~$86 and become OVER-corrected).** We have not stress-tested this scenario; the empirical evidence for Option 1 is strong but not dispositive.
- **The OOT under-coverage (HDI89 = 7.7%) for M2** is a well-known pattern in MMM (posterior underdispersed for out-of-sample prediction) but it means the +14.96% bias is **outside** the 89% predictive interval most weeks. We say it's a "documented limitation"; a reviewer might say "your model's stated uncertainty does not contain its own bias — that is a more serious epistemic failure than the MAPE number suggests."

---

## §6 — Files referenced

State files (private — gitignored):
- `state/decisions_log.md` (D021–D029)
- `state/decisions_index.md`
- `state/model_approach.md` (M3.5 close-out; M3.5b Fix-A; M3.5e close-out; M3.5f close-out; Q34 history)
- `state/sprint.md`
- `state/project_state.md`
- `state/open_questions.md` (Q27–Q37)

Proposals (archived):
- `proposals/archived/2026-05-19_d027_window_basis_correction.md`
- `proposals/archived/2026-05-19_post_fix_a_state_sync.md`
- `proposals/archived/2026-05-20_q34_d_gamma_negative_result.md`
- `proposals/archived/2026-05-20_d028_M1_D_gamma_promotion.md`
- `proposals/archived/2026-05-20_d029_baseline_gate_redesign.md`

Drafts (private):
- `drafts/session_closeout_2026-05-20_d028.md`
- `drafts/i7_window_reconciliation_2026-05-18.md`
- `drafts/abheek_spend_basis_clarification_2026-05-18.md`

Canonical scripts:
- `scripts/08b_mechanism2_more_tune.py` — Model 1 fit, M3.5b Fix-A
- `scripts/09_ltv_model.py` — Model 2 fit, M3.5b Fix-A
- `scripts/11_oot_validation.py` — M7 baseline OOT (still canonical for M2)
- `scripts/11b_oot_validation_M1_D_gamma.py` — D028 canonical M1 OOT
- `scripts/15_baseline_split.py` — D029 baseline decomposition

Diagnostic scripts (Q34 remedy work):
- `scripts/12_q34_diagnostic.py`, `12b_q34_structural_diag.py`
- `scripts/13_oot_remediation_v1.py`, `13b_q34_remedy_icac_check.py`, `13c_q34_gamma_sweep.py`
- `scripts/14_oot_remediation_v2.py` (D-ε attempt)

Outputs (committed):
- `outputs/P2_04_full_channel/metrics/mechanism2b_window_scaled.json` (M1 canonical)
- `outputs/P2_04_full_channel/metrics/ltv_window_scaled.json` (M2 canonical)
- `outputs/P2_04_full_channel/metrics/oot_model1_conversions.json` (D028 canonical M1 OOT)
- `outputs/P2_04_full_channel/metrics/oot_model2_ltv.json` (M2 OOT, canonical M3.5b Fix-A)
- `outputs/P2_04_full_channel/metrics/baseline_split.json` (D029 canonical)
- `outputs/diagnostics/meta_web_saturation_summary.json` (I-5)

Streamlit:
- `app/dashboard.py` — main dashboard with model-health bar (D029 update)
- `app/pages/1_Decisioning_Summary.py` — 19-row 8-column decisioning page
- `app/pages/2_OOT_Validation.py` — D028 asymmetric M1/M2 OOT page
- `app/pages/3_Methodology.py` — D029 new methodology page (5 sections)

Meeting:
- `meetings/refined/2026-05-12_client_sixth_meet_refined.md` — the reference point for this document

---

This document is for verification by other chats before client-facing artifacts are produced. Read this entire document before producing TRACE materials or Abheek qmd content.
