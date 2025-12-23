# Phase 1: Understand - Cherry-Picked Benchmarks

## The Trap: "It Works perfectly (on my machine)"

Imagine a student who claims to be a math genius. To prove it, they give you a test they wrote themselves, containing only questions they know the answers to. They score 100%. Are they a genius? Or did they just **cherry-pick** the benchmark?

In AI evaluation, **Cherry-Picked Benchmarks** occur when a model's performance is reported using a specific subset of data that flatters the system, while ignoring edge cases, failures, or more representative datasets.

It is a statistical version of the **Hasty Generalization** fallacy.

---

## Real-World Example: The "Hands-On" Illusion

In December 2023, a major tech company released a breathtaking demo of their new multimodal AI model. The video showed the AI interacting with a user in real-time, responding instantly to voice and video cues with zero latency. It seemed like magic.

**The Reality:**
Later, the company admitted the video was not real-time. It was stitched together from still image frames and text prompts, edited to look seamless. They had "cherry-picked" the successful interactions and the presentation format to imply a capability (real-time video reasoning) that didn't actually exist in that form.

**Why this is dangerous:**
If you bought that API expecting to build a real-time robot controller based on that video, your product would fail immediately.

---

## Domain Scenario: The "99% Accuracy" Dispute Classifier

Let's look at a concrete example from our **Dispute Resolution Chatbot**.

**The Pitch:**
> "Our new `ReasonCodeClassifier` achieves **99% accuracy** on the golden test set! It's ready for production."

**The Hidden Data:**
The "golden test set" (`classification_labels.json`) contains **100 records**.
- **100%** of them are **Visa** transactions.
- **100%** of them are Reason Code **10.4**.

**The Production Reality:**
When we deployed this model to a diverse environment (`diverse_classification_labels.json`), we saw:
- **Amex, Mastercard, Discover** transactions (which the model never saw).
- **Reason Codes A01, C02, F29** (which the model never saw).

The model blindly classified everything as "Visa 10.4". In the real world, its accuracy wasn't 99% — it was **~25%** (only getting the actual Visa 10.4s right by accident).

---

## 🚩 Red Flags: How to Spot It

When evaluating AI claims, vendors, or internal research, look for these warning signs:

### 1. The "Single Metric" Flex
"We have 95% Accuracy."
**Ask:** Accuracy on *what*? Accuracy is meaningless without the denominator (the dataset). If they don't link to the dataset distribution, be suspicious.

### 2. The "Internal" Test Set
"Tested on our proprietary internal benchmark."
**Translation:** "We made the test, so we know we pass it." Standard benchmarks (like MMLU, SWE-bench) are flawed, but at least they are public.

### 3. "Best of N" Reporting
"Our best run achieved X."
**The Catch:** If they ran the experiment 100 times with different random seeds and only reported the best one, they aren't reporting performance; they are reporting **luck**. This is known as "Seed Hacking" (see *Dodge et al., 2019*).

### 4. Perfect Round Numbers
"100% success rate."
Real AI is messy. It makes probabilistic errors. 100% usually means the test was too easy, or the data leaked into the training set.

---

## The Concept: Evaluation Bias

This fallacy relies on **Evaluation Bias** — the mismatch between the *evaluation* environment (the test) and the *target* environment (production).

- **Selection Bias:** Choosing data that aligns with the hypothesis.
- **Survivorship Bias:** Reporting only the models that finished training without crashing.

## Next Steps

Now that we **Understand** the fallacy, how do we **Plan** to detect it in our own work? We need a strategy to audit the "Cherry" before we bite.

