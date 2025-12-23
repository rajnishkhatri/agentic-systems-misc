# Phase 2: Plan - Detection Strategy

## "Trust but Verify"

In the **Understand** phase, we saw how easy it is to be fooled by a high score on a biased test. Now, we need a plan to expose that bias. We can't just accept the number; we have to audit the exam itself.

Our strategy is simple: **Interrogate the Denominator.**
(The denominator is the total set of cases used for evaluation).

---

## Detection Steps

### 1. The Distribution Check
**Question:** Does the test set match the real world?
**Action:** Plot the histogram of categories in the test set vs. production logs.
- If Production has 50 categories and Test Set has 1, you have a problem.
- *Tool:* `pandas.value_counts()` is your best friend here.

### 2. The "Hard Class" Identification
**Question:** Where does the system traditionally fail?
**Action:** Explicitly look for known "hard" examples.
- For our Dispute Chatbot: "Credit Not Processed" is hard (requires math). "General Inquiry" is easy.
- If the test set is 90% "General Inquiry", it's a softball exam.

### 3. The Leakage Audit
**Question:** Has the model seen the test questions before?
**Action:** Check for overlap between Training Data and Test Data.
- In the LLM era, this is common. If you test on questions from the internet, and the model was trained on the internet, it's just reciting memory, not reasoning.

---

## Related Fallacies to Watch

While looking for Cherry-Picking, you'll often find its cousins:

### 🕸️ Survivorship Bias
**The Trap:** Counting only the systems or requests that succeeded.
**Example:** "Average latency is 200ms!" (for the requests that didn't time out or crash). The crashed ones (infinite latency) are excluded from the average.

### 🎭 Demo-to-Production Leap
**The Trap:** Assuming a curated demo represents system capability.
**Detection:** Ask for the "Outtakes Reel". If they can't show you failure modes, they haven't tested them.

---

## Data Sources for Verification

To build a **Robust Benchmark** (the antidote to cherry-picking), we need:

1.  **Production Logs:** The raw, messy feed of what users actually ask.
2.  **Customer Tickets:** The specific cases where users complained (these are the hardest negatives).
3.  **Adversarial Examples:** Inputs specifically designed to break the system (e.g., typos, ambiguous phrasing).

## The Plan in Action

For our Dispute Chatbot, we will:
1.  Load the "Golden Set" (the cherry-picked one).
2.  Load the "Diverse Set" (the real one).
3.  Compare their distributions side-by-side.
4.  Run the model on BOTH and measure the **Delta**.

The size of that Delta is the measure of the Cherry-Picking Fallacy.

