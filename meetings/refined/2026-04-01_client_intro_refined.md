# Client Meeting — Week 1 (April 1, 2026) — Refined Notes

**Attendees:** Abheek Sinha (client), MMM Capstone Team  
**Prepared by:** Yash (refinement: 2026-04-12)  
**Source:** meetings/raw/2026-04-01_client_intro.md  
**Purpose:** Clean reference of business context, objectives, and constraints for the Kikoff MMM capstone project.

---

## Confirmed Facts (High Confidence — Source: Client Statement)

| Fact | Client statement | Impact |
|------|------------------|--------|
| **Annual Marketing Spend** | ~$100M/year | Defines scale; budget allocation is a primary use case |
| **North Star Metric** | Purchase/subscription (NOT app installs, signups, landing page visits) | MMM must target conversions as the dependent variable |
| **Deliverable Role** | ~33% weighted input to Kikoff's internal model (client also builds their own) | Model credibility and interpretability > fit metrics |
| **Modeling Approach** | Bayesian MMM | Prefer Bayesian prior specification (especially for incrementality) |
| **Incrementality Integration** | Incrementality test results must be used as **model inputs (priors)**, not just post-hoc validation | Critical requirement; affects model architecture |
| **Expected Iterations** | 5–7 refinement cycles | Plan for revision; initial model is not final |
| **Seasonality Modeling** | Critical for fintech; example: baseline ~$9M/month, December ~$7M. Model must support budget scenario planning | Explicit seasonal component required |
| **Iteration Approach** | Business interpretation & domain refinement (not model fit competition) | Prioritize interpretability and business insight |
| **Accuracy Hierarchy** | Incrementality > MMM > Attribution | Incrementality tests are ground truth; MMM aligns to them |
| **Key Relationship** | MMM should be informed AND validated by incrementality | Bidirectional: priors from tests, validation against tests |
| **Meeting Cadence** | Likely Monday afternoons (not finalized at Week 1) | Plan for weekly check-ins |

---

## Open Questions Raised (Week 1)

| Question | Category | Status | Maps to `open_questions.md` |
|----------|----------|--------|----------------------------|
| **Primary Dependent Variable** | Modeling | Unresolved | Q1 (see note below) |
| **Exact Time Granularity** | Data | Resolved in Week 2 → **Daily** | Q2 |
| **Channel vs. Tactic Definitions** | Data | Partially resolved in Week 2 | Q3 |
| **Date Range of Historical Data** | Data | Resolved in Week 2 → 2024–Mar 2026 | Q4 |
| **Incrementality Test Format** | Data | Partially resolved in Week 2 → iCAC format | Q5 |
| **External Drivers (macro variables)** | Modeling | Not addressed in meetings yet | NEW |
| **Attribution Scope** | Modeling | Deferred; attribution modeling not required initially | Non-blocking |

---

## Key Concepts Emphasized

### 1. Media Mix Modeling (MMM)
- Aggregated time-series approach
- Estimates channel contribution to conversions
- Supports budget allocation decisions
- **Not** a pure ML or prediction problem

### 2. Incrementality Testing
- Gold-standard causality measurement (experimental, controlled)
- Most accurate but expensive and infrequent
- Used as priors and for validation in this project

### 3. Attribution
- User-level tracking and credit assignment
- Enables frequent comparisons
- Less accurate than incrementality
- Lower priority for MMM calibration in this project

### 4. Residual/Unexplained Variance
- Expected and normal
- Not just noise — a business signal worth investigating
- Should be analyzed for missing variables or external factors

---

## Expected Deliverables

The MMM should produce:
- Channel contribution (absolute and relative)
- Contribution trends over time
- Marginal response curves (diminishing returns by channel)
- ROI and efficiency metrics
- Cost per incremental conversion
- Seasonality insights and patterns
- Budget allocation recommendations
- Scenario simulations (e.g., ±10%, ±20%, ±30% budget changes)

---

## Critical Constraints & Framing

**This is NOT:**
- A pure machine learning problem
- A model accuracy competition
- A "run a package and report results" exercise

**This IS:**
- A business modeling and interpretation problem
- Iterative refinement (5–7 cycles)
- Grounded in domain understanding and incrementality validation

---

## Risks Flagged by Client

| Risk | Mitigation Strategy |
|------|---------------------|
| Overfocusing on technical metrics (R², AUC, etc.) | Anchor all work in business interpretation and incrementality alignment |
| Treating MMM as a black-box package (Robyn or other) | Deep customization and interpretation required |
| Ignoring incrementality data | Incorporate as priors AND validation |
| Misaligned KPI (signup vs. purchase) | Strict focus on purchase/subscription metric |
| Underestimating iteration scope | Plan 5–7 refinement cycles from the start |
| Poor seasonality modeling | Explicit seasonal component; test scenario planning |
| Lack of team structure | Assign clear ownership early |

---

## Immediate Action Items (Week 1)

- [ ] Create WhatsApp group for faster communication
- [ ] Confirm next meeting timing (target: Monday afternoon)
- [ ] Assign team roles and responsibilities
- [ ] Build foundational understanding of MMM concepts
- [ ] Research Bayesian MMM frameworks (Robyn/Meridian)
- [ ] Draft project roadmap and modeling approach outline

---

## Reliability Assessment

- **High confidence (95%):** Business framing, North Star metric, incrementality role, budget scale, expected outputs
- **Moderate confidence (80%):** Exact wording in places; some details inferred from context
- **Noted:** Detailed output expectations partially inferred (client spreadsheet not visible during meeting)

**Status:** Safe to use as primary reference; clarification questions should target Week 2 + supervisor meetings.

---

*(End of Refined Notes — Week 1)*
