# Phase 4: Execute - The "Gotcha" Moment

## The Boardroom Breakdown

It's 2 PM. The vendor is presenting their "Next-Gen Dispute Classifier". The VP of Operations is nodding along. They just flashed a slide saying:

> **"99.0% Accuracy on Standard Benchmark"**

This is the moment. You've done your **Plan** and your **Tasks**. Now you **Execute**.

---

## 1. The Claim (Annotated)

Let's break down exactly what they just said vs. what they meant.

> "We validated this on a **curated set** [1] of **high-volume dispute types** [2] to ensure **reliability** [3]."

- **[1] Curated Set:** "We removed the hard ones." (Cherry-Picking)
- **[2] High-Volume:** "We only included Visa 10.4 because that's 60% of traffic." (Selection Bias)
- **[3] Reliability:** "We wanted to show a high number to get the contract." (Outcome Bias)

---

## 2. The Evidence Reveal

You open your laptop and project the analysis from Phase 3.

**You:** "I ran your model on our 'Diverse' dataset (`diverse_classification_labels.json`). This dataset mirrors our actual Amex and Discover traffic."

**The Slide:**

| Metric | Vendor Claim (Golden Set) | Reality (Diverse Set) |
|:-------|:--------------------------|:----------------------|
| **Accuracy** | **99.0%** | **25.7%** |
| **Visa Acc** | 100.0% | 98.0% |
| **Amex Acc** | N/A | **0.0%** |
| **Discover Acc**| N/A | **0.0%** |

**You:** "The model isn't learning 'Disputes'. It's memorizing 'Visa'. It has zero capability on 40% of our network volume."

---

## 3. The Counter-Move

The vendor will try to pivot. Here is the script to shut it down.

**Vendor:** "Well, Amex uses different reason codes. We can tune that later. Visa is the priority."

**You (The Counter):**
> "If it requires tuning for each network, then the '99% Accuracy' claim is misleading. We need to evaluate the **Generalization Capability**, not just the **Recall on Training Data**.
>
> Let's agree to benchmark on a stratified sample of **all** networks before we sign. Can we run that test today?"

**The Result:**
They usually can't. You just saved the company from a 12-month contract for a system that would have failed on Day 1.

---

## 🛠️ The Metric That Matters

Instead of **Accuracy**, we should have used **Macro-F1 Score**.

- **Accuracy:** $(99 + 0 + 0 + 0) / 4 \approx 25\%$ (if weighted by volume, maybe 60%).
- **Macro-F1:** Averages the performance of EACH class equally.
  - Visa F1: 1.0
  - Amex F1: 0.0
  - **Macro F1:** 0.25

**Lesson:** Cherry-Pickers love Accuracy. Honest evaluators use F1.

