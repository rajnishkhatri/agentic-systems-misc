# Cross-Cutting Implementation Patterns

**Purpose**: Reusable code patterns that appear across multiple techniques

---

## Pattern 1: Parallel LLM Processing

**Appears in**: HW2 (query generation), HW4 (salient facts), Lesson 4 (labeling)

**Use when**: Processing 50+ items with LLM API calls

### Basic Pattern
```python
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

def process_single_item(item):
    """Process one item (LLM API call)"""
    response = litellm.completion(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": f"Process: {item}"}],
        timeout=30
    )
    return response.choices[0].message.content

items = [...]  # List of items to process

# Parallel execution
with ThreadPoolExecutor(max_workers=10) as executor:
    results = list(tqdm(
        executor.map(process_single_item, items),
        total=len(items),
        desc="Processing"
    ))
```

### Advanced Pattern (with error handling)
```python
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import time

def process_with_retry(item, max_retries=3):
    """Process with exponential backoff retry"""
    for attempt in range(max_retries):
        try:
            response = litellm.completion(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": f"Process: {item}"}],
                timeout=30
            )
            return {"item": item, "result": response.choices[0].message.content, "error": None}
        except Exception as e:
            if attempt == max_retries - 1:
                return {"item": item, "result": None, "error": str(e)}
            time.sleep(2 ** attempt)  # Exponential backoff

def parallel_process_with_errors(items, max_workers=10):
    """Parallel processing with error tracking"""
    results = []
    errors = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_with_retry, item): item for item in items}

        for future in tqdm(as_completed(futures), total=len(items), desc="Processing"):
            result = future.result()
            if result["error"]:
                errors.append(result)
            else:
                results.append(result)

    return results, errors
```

### Worker Count Guidelines
- **Start with 10 workers**: Safe for most API rate limits
- **Increase to 20-64**: If no rate limit errors
- **Monitor**: Track API error rates, reduce workers if needed

### Cost Warning Pattern
```python
def estimate_cost(num_items, cost_per_call=0.0002):
    """Estimate total cost before processing"""
    total_cost = num_items * cost_per_call
    print(f"Estimated cost: ${total_cost:.2f} for {num_items} items")
    user_input = input("Proceed? (yes/no): ")
    return user_input.lower() == "yes"

if estimate_cost(len(items)):
    results = parallel_process(items)
```

---

## Pattern 2: Train/Dev/Test Splitting

**Appears in**: HW3, Lesson 4

**Use when**: Building LLM-as-Judge or ML-style evaluation

### Deterministic Hash-Based Splitting
```python
import hashlib

def get_split_category(record_id: str, train_pct=15, dev_pct=40) -> str:
    """Deterministically assign record to train/dev/test.

    Args:
        record_id: Unique identifier for record
        train_pct: Percentage for training set (default 15)
        dev_pct: Percentage for dev set (default 40)
        test_pct: Remaining percentage (45 with defaults)

    Returns:
        "train", "dev", or "test"
    """
    hash_val = int(hashlib.sha256(record_id.encode()).hexdigest(), 16)
    bucket = hash_val % 100

    if bucket < train_pct:
        return "train"
    elif bucket < train_pct + dev_pct:
        return "dev"
    else:
        return "test"

# Usage
import pandas as pd

df = pd.read_csv("labeled_data.csv")
df["split"] = df["id"].apply(get_split_category)

train_df = df[df["split"] == "train"]
dev_df = df[df["split"] == "dev"]
test_df = df[df["split"] == "test"]

print(f"Train: {len(train_df)} ({len(train_df)/len(df)*100:.1f}%)")
print(f"Dev: {len(dev_df)} ({len(dev_df)/len(df)*100:.1f}%)")
print(f"Test: {len(test_df)} ({len(test_df)/len(df)*100:.1f}%)")
```

### Stratified Splitting (Balanced Labels)
```python
from sklearn.model_selection import train_test_split

def stratified_split(df, label_column="label", train_size=0.15, dev_size=0.4):
    """Split with balanced label distribution across splits"""
    # First split: separate train from (dev+test)
    train_df, temp_df = train_test_split(
        df,
        train_size=train_size,
        stratify=df[label_column],
        random_state=42
    )

    # Second split: separate dev from test
    dev_size_adjusted = dev_size / (1 - train_size)
    dev_df, test_df = train_test_split(
        temp_df,
        train_size=dev_size_adjusted,
        stratify=temp_df[label_column],
        random_state=42
    )

    return train_df, dev_df, test_df
```

---

## Pattern 3: Synthetic Data Generation

**Appears in**: HW2 (dimension tuples), HW4 (salient facts)

**Use when**: Need diverse test queries, cold-start evaluation

### Dimension Tuple Generation (HW2)
```python
def generate_dimension_tuples(dimensions: dict, num_tuples: int = 20) -> list[dict]:
    """Generate dimension tuples using LLM.

    Args:
        dimensions: {"cuisine": [...], "dietary": [...], ...}
        num_tuples: Number of tuples to generate

    Returns:
        List of dimension tuples
    """
    dimension_str = "\n".join([f"- {k}: {', '.join(v)}" for k, v in dimensions.items()])

    prompt = f"""Generate {num_tuples} diverse dimension tuples for recipe queries.

Dimensions:
{dimension_str}

Output format (JSON array):
[
  {{"cuisine": "Thai", "dietary": "vegan", "meal_type": "dinner"}},
  ...
]

Ensure diversity across all dimensions."""

    response = litellm.completion(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )

    import json
    return json.loads(response.choices[0].message.content)

def tuple_to_query(tuple_dict: dict) -> str:
    """Convert dimension tuple to natural language query"""
    prompt = f"""Convert this dimension tuple to a natural language query:
{tuple_dict}

Output only the query, no explanation."""

    response = litellm.completion(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip()
```

### Salient Fact Extraction (HW4)
```python
def extract_salient_facts(document: str, num_facts: int = 3) -> list[str]:
    """Extract key facts from document"""
    prompt = f"""Extract {num_facts} salient facts from this document:

{document}

Return as JSON array: ["fact1", "fact2", "fact3"]"""

    response = litellm.completion(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )

    import json
    return json.loads(response.choices[0].message.content)

def fact_to_query(fact: str) -> str:
    """Convert fact to natural language question"""
    prompt = f"""Convert this fact to a natural language question:
Fact: {fact}

Output only the question."""

    response = litellm.completion(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip()
```

---

## Pattern 4: Cost-Accuracy Optimization

**Appears in**: HW3 (cheaper judge), Lesson 8 (cascades)

**Use when**: Need to balance quality with cost constraints

### Model Comparison Framework
```python
from dataclasses import dataclass

@dataclass
class ModelPerformance:
    model_name: str
    accuracy: float
    cost_per_1k: float
    latency_ms: float

def evaluate_model(model_name: str, test_set: list) -> ModelPerformance:
    """Evaluate model on test set"""
    import time

    start = time.time()
    correct = 0

    for example in test_set:
        response = litellm.completion(
            model=model_name,
            messages=[{"role": "user", "content": example["query"]}]
        )
        predicted = response.choices[0].message.content
        if predicted == example["ground_truth"]:
            correct += 1

    latency = (time.time() - start) * 1000 / len(test_set)
    accuracy = correct / len(test_set)

    # Cost lookup (example values)
    costs = {
        "gpt-4o-mini": 0.0002,
        "gpt-4o": 0.00325,
    }

    return ModelPerformance(
        model_name=model_name,
        accuracy=accuracy,
        cost_per_1k=costs.get(model_name, 0),
        latency_ms=latency
    )

def compare_models(models: list[str], test_set: list):
    """Compare multiple models"""
    results = [evaluate_model(model, test_set) for model in models]

    print(f"{'Model':<15} {'Accuracy':>10} {'Cost/1K':>10} {'Latency':>10}")
    print("-" * 50)
    for r in results:
        print(f"{r.model_name:<15} {r.accuracy:>9.1%} ${r.cost_per_1k:>8.4f} {r.latency_ms:>8.0f}ms")

    return results
```

### Cascade Decision Logic
```python
def cascade_predict(query: str, threshold: float = 0.90):
    """Route query based on cheap model confidence"""
    # Cheap model with logprobs
    cheap_response = litellm.completion(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": query}],
        logprobs=True,
        max_tokens=1
    )

    # Extract confidence
    logprobs = cheap_response.choices[0].logprobs.content[0].top_logprobs
    probs = {token: math.exp(data.logprob) for token, data in logprobs.items()}
    total = sum(probs.values())
    confidence = max(probs.values()) / total

    if confidence >= threshold:
        # High confidence: use cheap model
        return cheap_response.choices[0].message.content, "cheap"
    else:
        # Low confidence: route to expensive model
        expensive_response = litellm.completion(
            model="gpt-4o",
            messages=[{"role": "user", "content": query}]
        )
        return expensive_response.choices[0].message.content, "expensive"
```

---

## Pattern 5: Few-Shot Example Selection

**Appears in**: HW3 (judge prompts), Lesson 4 (substantiation)

**Use when**: Engineering prompts for LLM-as-Judge or classification

### Balanced Selection
```python
def select_few_shot_examples(train_df, num_pass=1, num_fail=3):
    """Select balanced few-shot examples from train set

    Args:
        train_df: DataFrame with 'label' column
        num_pass: Number of PASS examples
        num_fail: Number of FAIL examples

    Returns:
        List of example dictionaries
    """
    pass_examples = train_df[train_df["label"] == "PASS"].sample(n=num_pass, random_state=42)
    fail_examples = train_df[train_df["label"] == "FAIL"].sample(n=num_fail, random_state=42)

    examples = []

    # Add PASS examples
    for _, row in pass_examples.iterrows():
        examples.append({
            "input": row["input"],
            "output": row["output"],
            "verdict": "PASS",
            "reasoning": row.get("reasoning", "Meets all criteria")
        })

    # Add FAIL examples
    for _, row in fail_examples.iterrows():
        examples.append({
            "input": row["input"],
            "output": row["output"],
            "verdict": "FAIL",
            "reasoning": row.get("reasoning", "Violates criteria")
        })

    return examples

def format_few_shot_prompt(examples: list) -> str:
    """Format examples into prompt string"""
    formatted = []

    for i, ex in enumerate(examples, 1):
        formatted.append(f"""Example {i}:
Input: {ex['input']}
Output: {ex['output']}
Verdict: {ex['verdict']}
Reasoning: {ex['reasoning']}""")

    return "\n\n".join(formatted)
```

---

## Pattern 6: Structured LLM Output (Pydantic)

**Appears in**: HW3, Lesson 4

**Use when**: Need reliable parsing of LLM responses

### Pydantic Models
```python
from pydantic import BaseModel, Field

class JudgmentResult(BaseModel):
    """Structured output for LLM-as-Judge"""
    verdict: str = Field(..., description="PASS or FAIL")
    reasoning: str = Field(..., description="Brief explanation")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")

def get_structured_judgment(query: str, response: str) -> JudgmentResult:
    """Get judgment with structured output"""
    prompt = f"""Evaluate this response:
Query: {query}
Response: {response}

Return JSON with verdict (PASS/FAIL), reasoning, and confidence (0-1)."""

    llm_response = litellm.completion(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )

    import json
    data = json.loads(llm_response.choices[0].message.content)
    return JudgmentResult(**data)
```

---

## Pattern 7: Progress Tracking & Checkpointing

**Appears in**: Lesson 4 (parallel labeling)

**Use when**: Long-running operations that might fail

### Checkpoint Pattern
```python
import json
import os

def process_with_checkpoints(items, output_file="results.jsonl", checkpoint_every=10):
    """Process items with periodic checkpointing"""
    # Load existing results if file exists
    processed_ids = set()
    if os.path.exists(output_file):
        with open(output_file, "r") as f:
            for line in f:
                result = json.loads(line)
                processed_ids.add(result["id"])
        print(f"Resuming from checkpoint: {len(processed_ids)} items already processed")

    # Filter to unprocessed items
    remaining_items = [item for item in items if item["id"] not in processed_ids]

    # Process with checkpointing
    with open(output_file, "a") as f:
        for i, item in enumerate(tqdm(remaining_items, desc="Processing")):
            result = process_single_item(item)
            f.write(json.dumps(result) + "\n")

            # Flush every N items
            if (i + 1) % checkpoint_every == 0:
                f.flush()

    return output_file
```

---

## Pattern 8: Demo vs Full Mode

**Appears in**: HW2, HW4, Lesson 4 notebooks

**Use when**: Want to test on small sample before full run

### Configuration Pattern
```python
class Config:
    """Centralized configuration"""
    DEMO_MODE = True  # Set to False for full run

    # Demo settings
    DEMO_SAMPLE_SIZE = 10
    DEMO_MAX_WORKERS = 5

    # Full settings
    FULL_SAMPLE_SIZE = 200
    FULL_MAX_WORKERS = 64

def get_config():
    """Get configuration based on mode"""
    if Config.DEMO_MODE:
        return {
            "sample_size": Config.DEMO_SAMPLE_SIZE,
            "max_workers": Config.DEMO_MAX_WORKERS,
            "description": "DEMO MODE"
        }
    else:
        return {
            "sample_size": Config.FULL_SAMPLE_SIZE,
            "max_workers": Config.FULL_MAX_WORKERS,
            "description": "FULL MODE"
        }

# Usage
config = get_config()
print(f"Running in {config['description']}")
items = data[:config["sample_size"]]
results = parallel_process(items, max_workers=config["max_workers"])
```

---

## Pattern 9: Confidence Interval Reporting

**Appears in**: HW3 (bias correction)

**Use when**: Reporting evaluation metrics with uncertainty

### Confidence Interval Calculation
```python
import math

def binomial_confidence_interval(successes: int, total: int, confidence=0.95):
    """Calculate binomial proportion confidence interval (normal approximation)"""
    if total == 0:
        return 0.0, 0.0, 0.0

    p = successes / total
    z = 1.96  # 95% confidence
    se = math.sqrt(p * (1 - p) / total)
    margin = z * se

    return p, max(0, p - margin), min(1, p + margin)

def report_with_ci(successes: int, total: int, metric_name="Success Rate"):
    """Report metric with 95% CI"""
    rate, lower, upper = binomial_confidence_interval(successes, total)

    print(f"{metric_name}: {rate:.1%}")
    print(f"95% CI: [{lower:.1%}, {upper:.1%}]")
    print(f"Margin of error: ±{(rate-lower):.1%}")

# Usage
report_with_ci(successes=85, total=100, metric_name="Accuracy")
```

---

## Pattern 10: Error Handling for LLM APIs

**Appears in**: All techniques using LLM APIs

**Use when**: Making LLM API calls (always!)

### Robust API Call Pattern
```python
import time
from typing import Optional

def robust_llm_call(prompt: str, max_retries=3, timeout=30) -> Optional[str]:
    """Call LLM with retry logic and error handling"""
    for attempt in range(max_retries):
        try:
            response = litellm.completion(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                timeout=timeout
            )
            return response.choices[0].message.content

        except litellm.exceptions.RateLimitError:
            wait_time = 2 ** attempt
            print(f"Rate limit hit. Waiting {wait_time}s...")
            time.sleep(wait_time)

        except litellm.exceptions.Timeout:
            print(f"Timeout on attempt {attempt + 1}")
            if attempt == max_retries - 1:
                return None

        except Exception as e:
            print(f"Error on attempt {attempt + 1}: {str(e)}")
            if attempt == max_retries - 1:
                return None
            time.sleep(1)

    return None
```

---

## Quick Reference: When to Use Each Pattern

| Pattern | Use Case |
|---------|----------|
| **Parallel Processing** | Processing 50+ items with LLM |
| **Train/Dev/Test Split** | Building LLM-as-Judge |
| **Synthetic Data Generation** | Expanding test coverage |
| **Cost-Accuracy Optimization** | Model selection, cascades |
| **Few-Shot Selection** | Judge prompt engineering |
| **Structured Output (Pydantic)** | Reliable LLM response parsing |
| **Checkpointing** | Long-running operations |
| **Demo/Full Mode** | Testing before full run |
| **Confidence Intervals** | Reporting metrics with uncertainty |
| **Error Handling** | All LLM API calls (always!) |

---

## Further Reading

**Implementation examples**:
- HW2: `dimension_generation_tutorial.ipynb`
- HW4: `synthetic_query_generation_tutorial.ipynb`
- Lesson 4: `parallel_labeling_tutorial.ipynb`

**Best practices**:
- Always add progress tracking (tqdm)
- Always handle errors gracefully
- Always estimate costs before running
- Always checkpoint long operations
