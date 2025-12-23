# Phase 3: Tasks - The Audit Checklist

## "Show Me The Data"

In this phase, we execute the specific tasks required to validate our suspicion. We stop listening to the sales pitch and start looking at the JSON.

Here is your checklist for detecting Cherry-Picked Benchmarks.

---

## 📋 Verification Checklist

### Task 1: Check Dataset Volume
- [ ] Count the total records in the test set.
- [ ] **Heuristic:** If $N < 50$ for a production system, it's anecdotal, not statistical.
- [ ] **Heuristic:** If $N$ is a perfect round number (e.g., 10, 100), suspect manual curation.

### Task 2: Analyze Class Distribution
- [ ] Group by the target label (e.g., `Reason Code`).
- [ ] Calculate the percentage of the most frequent class.
- [ ] **Red Flag:** If the top class is $>80\%$ of the data, the dataset is imbalanced.
- [ ] **Red Flag:** If the top class is $100\%$ of the data, it's a "Unit Test", not a "Benchmark".

### Task 3: Compare with Training Data
- [ ] Load the training set distribution.
- [ ] **Heuristic:** The Test Set distribution should roughly mirror the Production distribution, not necessarily the Training distribution (if training was oversampled).

### Task 4: The "Naive Baseline" Test
- [ ] Calculate the accuracy of a "Dummy Classifier" that just predicts the most frequent class.
- [ ] **Comparison:** If your sophisticated AI gets 99% accuracy, but guessing "Visa" also gets 99% accuracy, your AI has learned nothing.

---

## 🛠️ Data Queries (Python/Pandas)

Here is the code to run these checks on our `classification_labels.json`.

```python
import pandas as pd
import json

# Load the suspicious dataset
with open('classification_labels.json', 'r') as f:
    data = json.load(f)
df = pd.DataFrame(data)

# 1. Volume Check
print(f"Total Records: {len(df)}")

# 2. Distribution Check
print("\n--- Network Distribution ---")
print(df['network'].value_counts(normalize=True))

print("\n--- Reason Code Distribution ---")
print(df['true_reason_code'].value_counts(normalize=True))

# 3. Naive Baseline Calculation
most_common_class = df['true_reason_code'].mode()[0]
baseline_acc = (df['true_reason_code'] == most_common_class).mean()
print(f"\nNaive Baseline Accuracy: {baseline_acc:.2%}")
```

### Expected Output (The "Smoking Gun")

When you run this on the "Golden Set", you will see:

```text
Total Records: 100

--- Network Distribution ---
visa    1.0
Name: network, dtype: float64

--- Reason Code Distribution ---
10.4    1.0
Name: true_reason_code, dtype: float64

Naive Baseline Accuracy: 100.00%
```

**Conclusion:** The AI is adding **0% value** over a hard-coded "return 'Visa 10.4'" function. This is the definition of a cherry-picked benchmark.

