# Baseline & Modeling-Engine Findings — Kikoff MMM

*Prepared by our team · 2026-05-31 · for the June 4–5 review*

---

## The one-paragraph version

Our model attributes roughly **two-thirds of LTV to a baseline** — the portion not explained
by measured paid spend. We tested this hard — across every modeling approach we tried and two
independent engines — and the result holds: the baseline stays in the same range regardless of how
we configure the model, so it reflects **your data and attribution, not one tool's settings**. We
can push it down to about **41%**, but
only by loosening the discipline that ties the model to your incrementality tests — and that
trade comes at a real cost to out-of-time accuracy and to the per-channel numbers you care
about. The honest picture is a **trade-off between two defensible endpoints**, and our
recommendation is to stay on the incrementality-faithful end while reading the baseline
correctly: most of it is genuine organic demand plus paid credit the spend-only model cannot
place on a specific channel.

---

## 1. What we set out to resolve

Two questions were open going into this review:

1. **Which modeling engine should anchor the deliverable** — the one we built the dashboard
   and decisioning layer on, or an alternative?
2. **Can the baseline be brought into the 30–40% range** you flagged as the target?

We answered both with a deliberate test rather than a single run.

---

## 2. The engine decision

**We are anchoring on the engine that powers the dashboard and the 8-column decisioning page
you already reviewed and approved.** It is fully fitted, converges cleanly, and is validated
out-of-time end to end. Every client-facing surface — saturation curves, the per-channel
iCAC/iROAS views, the decisioning rows — reads from it.

We also built a **second, independent engine** and ran it on the same data. We did this not to
replace the first, but to **stress-test the baseline finding** — if two different modeling
approaches disagree, the number is an artifact; if they agree, it is real.

**They agree.** The second engine lands at essentially the same baseline (within a couple of
points). That is the most important corroboration in this document: the ~two-thirds baseline
is a property of *your data and attribution*, not of any one tool's settings.

On the accuracy check you weight most — how closely the model predicts held-out **conversion
volumes** — the two engines are essentially tied (a fraction of a percentage point apart). The
alternative has a small edge only on held-out LTV dollars. We're not resting the engine choice
on either: both predict within the acceptable range, and the recommendation stands on the
validated pipeline and the surfaces you've already approved.

A note on the second engine's smoother saturation curves: those come from a **built-in
curvature assumption** applied uniformly across all channels, not from a channel-by-channel
discovery in the data. We are flagging that explicitly so the comparison is read fairly — the
smoother shape is an input, not a finding.

---

## 3. The baseline: an honest trade-off, not a single number

We could not bring the baseline into the 30–40% band without giving up something you value
more. Here is the trade-off in plain terms.

| | **Incrementality-faithful** *(recommended)* | **Blended-efficiency alternative** |
|---|---|---|
| **Baseline** | ~66–67% | ~41% |
| **Out-of-time accuracy** | ~13–16% error (strong) | ~23–28% error (materially worse) |
| **Meta Web efficiency** | In / near your truth range | Re-inflates back toward the high pre-calibration level |
| **CTV** | Calibrated to its lift test | Falls outside its tested range |
| **Tie to your incrementality tests** | Fully honored | Largely abandoned |

The lower baseline is **reachable but not free**. Getting to 41% means loosening the link to
your incrementality tests — and the moment we do that, the model predicts held-out weeks
**worse** (the metric you told us matters most for an MMM), CTV drifts off its tested value,
and Meta Web's cost-per-acquisition climbs back toward the number we spent the last several
weeks correcting. A 41% baseline that mis-predicts and de-calibrates your channels is a weaker
deliverable than a 67% baseline that predicts well and keeps the channels honest.

**Two things we want to be precise about, because both are easy to overstate:**

- **41% is the floor the data allows, not a dial.** Even when we pushed the model hard toward
  a 35% baseline, it settled back near 60% on its own. The data resists going lower; 41% is as
  far down as the blended-efficiency approach can honestly reach.
- **41% is still above genuine organic demand (~35%).** So the lower number is not "organic
  explained away." Reaching the ~35% range you've seen elsewhere is achievable — but on a **richer
  input set than we have here.** A model fed channel-level impressions and reach, plus dated
  product and pricing events, can place that credit on the paid channels directly; a model that
  sees only spend cannot, so on
  spend-only data the incrementality-faithful floor lands at ~66–67%. The gap to 35% is a
  difference in **what the model can see**, not a difference in rigor — we're not in a position to
  judge another model's number, and we won't guess at it.

---

## 4. Why the baseline is high — and why that is a data story, not a model flaw

The two-thirds (~67%) baseline decomposes into two understandable pieces:

- **About 35 points is genuine organic demand** — customers who would have subscribed without the
  measured paid channels. This is consistent with your own read that the attributed-revenue
  universe is roughly two-thirds of total LTV, leaving about a third as organic. It is a real
  floor, and it is not recoverable by any model that only sees paid spend.
- **The remaining ~32 points is missed paid attribution** — credit the spend-only model cannot
  place on a specific channel, so it lands in the baseline instead. This credit is spread across
  channels that are under-instrumented, lift-tested less heavily or not at all, where the model
  has weaker information to attribute against. Several mechanisms contribute, including activity
  the spend-only inputs simply cannot resolve to a channel. One identifiable example shows up in
  the diagnostics: when we tightened Meta Web's calibration, the change pulled its *efficiency
  level* into range but did **not** move *where* the model assigned its credit, the signature of
  effect that spend-only data cannot place. We are deliberately **not** naming a single channel as
  the explanation; the model is built to capture these effects in aggregate, and the missing piece
  is the data that would let it split that credit across channels.

Put on a like-for-like footing against your attributed-revenue universe, the baseline is closer
to a **45–57% range**. The gap to a 30–40% target is therefore a **data-scope ceiling** — it
would require richer inputs to close, channel-level impressions and reach plus dated product and
pricing events — **not** a modeling defect we can tune away.

---

## 5. What this does *not* change

The baseline height does **not** weaken the decisioning layer. The recommendations you act on
— marginal cost-per-acquisition, marginal return, saturation read, and the spend-move
guidance per channel — are driven by each channel's *marginal* behavior, which is robust to the
overall baseline level. A high baseline tells you how much demand is organic; it does not blur
which channels to lean into or pull back from.

---

## 6. Our recommendation

1. **Anchor on the incrementality-faithful model** (the engine behind the approved dashboard
   and decisioning page). It honors your incrementality tests, predicts held-out weeks well,
   and keeps Meta Web and CTV in their tested ranges.
2. **Read the ~two-thirds baseline correctly:** roughly half is genuine organic demand, and
   the remainder is paid credit that spend-only data cannot place on a specific channel. It is a
   data-scope ceiling, corroborated by a second independent engine — not a tuning failure.
3. **Treat the 41% figure as a documented option with a price**, not a target to chase. We can
   produce it on request, with the accuracy and calibration costs stated above made explicit.

We would value your steer on one point: whether to invest, in a future iteration, in richer
inputs — channel-level impressions and reach, plus dated product and pricing events — that would
let the model split the credit currently sitting in the baseline across the paid channels. That
is the single change that would move the floor.
