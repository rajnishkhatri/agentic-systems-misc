# Example Scenarios Draft: Cherry-Picked Benchmarks

## Data Analysis

We analyzed two datasets from the dispute-chatbot project to identify potential sources of selection bias.

### Dataset A: `classification_labels.json` (The "Golden" Set)
- **Total Records:** 100
- **Network Distribution:** 100% Visa
- **Reason Code Distribution:** 100% "10.4" (Other Fraud - Card-Absent Environment)
- **Insight:** This dataset represents a single, narrow slice of the problem space. It is highly uniform.

### Dataset B: `diverse_classification_labels.json` (The "Diverse" Set)
- **Total Records:** 101
- **Network Distribution:** 
  - Amex: 28.7%
  - Visa: 24.8%
  - Discover: 22.8%
  - Mastercard: 20.8%
  - Others: 3.0%
- **Reason Code Distribution:** Highly fragmented (mostly 1 instance per code)
- **Category Distribution:**
  - General: 44.6%
  - Fraudulent: 22.8%
  - Credit Not Processed: 6.9%
  - Product Not Received: 6.9%
- **Insight:** This dataset represents the messy reality of production data with long-tail distributions.

---

## Draft Scenarios

These scenarios will be used to illustrate the "Cherry-Picked Benchmarks" fallacy in the tutorial.

### Scenario 1: The "99% Accuracy" Claim (The Primary Example)
**The Pitch:** "Our dispute classifier achieves 99% accuracy on the golden test set!"
**The Reality:** The model was trained and evaluated ONLY on Dataset A (Visa 10.4).
**The Failure:** When deployed to production (represented by Dataset B), accuracy drops to 25% because it classifies everything as "Visa 10.4".
**Why it works for the tutorial:** It's a stark, binary contrast. The "cherry-picked" nature is undeniable (single class).

### Scenario 2: The "Fraud Expert" Fallacy
**The Pitch:** "Our system catches 100% of fraud cases."
**The Reality:** Evaluated only on the "Fraudulent" category from Dataset B, ignoring false positives on "General" disputes.
**The Failure:** It flags legitimate disputes as fraud (high recall, low precision), causing customer friction.
**metric:** Precision is the missing metric here.

### Scenario 3: The "Major Networks Only" Bias
**The Pitch:** "Works across all major card networks."
**The Reality:** Evaluated on a subset excluding "openapi_gateway_response" or "paypal" (the edge cases in Dataset B).
**The Failure:** The system crashes or defaults to "Unknown" for these integration points, which often require specific handling.

### Scenario 4: The "Easy Cases" Filter
**The Pitch:** "We handle the most common disputes automatically."
**The Reality:** The evaluation dataset excluded "Credit Not Processed" and "Product Not Received" (complex disputes requiring evidence) and focused only on "General" inquiries.
**The Failure:** The system claims high automation rates but only handles the trivial queries, leaving the expensive/hard ones for humans, inflating the ROI calculation.

