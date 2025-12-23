# Phase 6: Counter - Building a Robust Benchmark

## The Antidote to Cherry-Picking

If the poison is "Selection Bias", the antidote is **Stratified Sampling**.

To prevent Cherry-Picked Benchmarks, we must ensure our evaluation set represents the **True Distribution** of the problem space, not just the easy parts.

---

## 🔗 Connection to Homework

In **HW3 (Dispute Classification)**, you didn't just calculate accuracy. You generated a **Confusion Matrix**.
Why? Because the Confusion Matrix shows you exactly *where* the model is failing. It forces you to look at the off-diagonal elements (the errors).

If you had a "Cherry-Picked" model in HW3, your confusion matrix would have looked like a single bright square (100% correct on one class) and empty everywhere else.

---

## 💻 The Code: Stratified Sampling

Here is how you guarantee a fair test using Python. This code ensures that if your production data is 1% "Fraud", your test set is also 1% "Fraud".

```python
from sklearn.model_selection import train_test_split
import pandas as pd

# Assume df is your full "Diverse" dataset
df = pd.read_json('diverse_classification_labels.json')

# The Wrong Way (Random Split might miss the rare class)
train_bad, test_bad = train_test_split(df, test_size=0.2, random_state=42)

# The Right Way (Stratified Split preserves distribution)
train_good, test_good = train_test_split(
    df, 
    test_size=0.2, 
    random_state=42, 
    stratify=df['category']  # <--- The Magic Word
)

print("Test Set Distribution:")
print(test_good['category'].value_counts(normalize=True))
```

### Why `stratify` matters
It ensures that even the smallest minority class (the "edge case") is represented in your test set. You can't hide the failure if the failure case is guaranteed to be on the exam.

---

## Application Scenario

**Vendor:** "We can't run on your data yet, we need to ingest it."

**You (The Counter-Move):**
> "No problem. I will provide you with a **Stratified Sample** of 100 anonymized records. It contains:
> - 60 Visa (Standard)
> - 20 Amex (Different Reason Codes)
> - 10 Fraud (Adversarial)
> - 10 Incomplete (Edge Cases)
>
> If you can score >80% F1 on *this* set, we can talk."

By forcing the **distribution** of the test, you remove their ability to cherry-pick. You have defined the playing field.

