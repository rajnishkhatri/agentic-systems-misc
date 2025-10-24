# The Complete Guide to AI System Evaluation
### From Prompt Engineering to Production-Ready Evaluation Pipelines

**A comprehensive, hands-on tutorial for systematically evaluating and improving AI systems**

---

## Table of Contents

1. [Foundation: Why Systematic Evaluation Matters](#1-foundation-why-systematic-evaluation-matters)
2. [Prompt Engineering Fundamentals](#2-prompt-engineering-fundamentals)
3. [Error Analysis & Failure Taxonomies](#3-error-analysis--failure-taxonomies)
4. [LLM-as-Judge Evaluation](#4-llm-as-judge-evaluation)
5. [RAG & Retrieval Evaluation](#5-rag--retrieval-evaluation)
6. [Agent Failure Analysis](#6-agent-failure-analysis)
7. [Advanced Topics](#7-advanced-topics)
8. [Best Practices & Production Patterns](#8-best-practices--production-patterns)
9. [Practical Exercises & Challenges](#9-practical-exercises--challenges)
10. [Reference Materials](#10-reference-materials)

---

## 1. Foundation: Why Systematic Evaluation Matters

### 1.1 The Problem with "Vibes-Based" Evaluation

When building AI systems, it's tempting to rely on informal testing:
- "I tried a few queries and it seems to work"
- "The responses look pretty good to me"
- "We fixed that bug, so it should be better now"

**This approach fails at scale.** Without systematic evaluation:
- ❌ You can't measure real performance
- ❌ You can't track improvements over time
- ❌ You can't identify specific failure modes
- ❌ You can't confidently deploy to production
- ❌ You can't justify decisions to stakeholders

### 1.2 The Systematic Evaluation Philosophy

This course teaches a **systematic, data-driven approach** to AI evaluation:

```
┌─────────────────────────────────────────────────────────┐
│                 THE EVALUATION LOOP                     │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1. DEFINE  → What should the system do?               │
│     ↓         (Write clear specifications)             │
│                                                         │
│  2. TEST    → How does it actually behave?             │
│     ↓         (Run systematic tests)                   │
│                                                         │
│  3. MEASURE → What's the performance?                  │
│     ↓         (Calculate metrics)                      │
│                                                         │
│  4. ANALYZE → Where does it fail?                      │
│     ↓         (Identify failure modes)                 │
│                                                         │
│  5. IMPROVE → How can we fix it?                       │
│     ↓         (Implement changes)                      │
│                                                         │
│  6. REPEAT  → Start the loop again                     │
│               (Continuous improvement)                 │
└─────────────────────────────────────────────────────────┘
```

### 1.3 Course Learning Path

This tutorial follows a **progressive curriculum**:

| Stage | Focus | Key Skills |
|-------|-------|------------|
| **HW1** | Prompt Engineering | Writing effective system prompts, testing strategies |
| **HW2** | Error Analysis | Open/axial coding, failure taxonomies |
| **HW3** | LLM-as-Judge | Automated evaluation, bias correction, TPR/TNR |
| **HW4** | RAG Evaluation | Retrieval metrics, synthetic data, query optimization |
| **HW5** | Agent Analysis | State machines, transition matrices, pattern identification |

### 1.4 What You'll Build

Throughout this guide, you'll work with a **Recipe Chatbot** system that:
- Takes natural language cooking queries
- Generates personalized recipe recommendations
- Uses RAG (Retrieval-Augmented Generation) for specific queries
- Follows dietary restrictions and preferences

You'll learn to:
✅ Systematically identify failure modes
✅ Build automated evaluation pipelines
✅ Measure performance with statistical rigor
✅ Create production-ready evaluation systems
✅ Apply bias correction techniques
✅ Optimize retrieval systems

---

## 2. Prompt Engineering Fundamentals

### 2.1 The Power of the System Prompt

The **system prompt** is the foundation of your AI system's behavior. It defines:
- **Role**: What is the AI supposed to be?
- **Constraints**: What should it always/never do?
- **Output Format**: How should responses be structured?
- **Agency**: How much creative freedom does it have?

### 2.2 Anatomy of an Effective System Prompt

Let's analyze a production-ready system prompt from the Recipe Chatbot:

```python
SYSTEM_PROMPT = (
    "You are an expert chef recommending delicious and useful recipes. "
    "Present only one recipe at a time. If the user doesn't specify what ingredients "
    "they have available, assume only basic ingredients are available."
    "Be descriptive in the steps of the recipe, so it is easy to follow."
    "Have variety in your recipes, don't just recommend the same thing over and over."
    "You MUST suggest a complete recipe; don't ask follow-up questions."
    "Mention the serving size in the recipe. If not specified, assume 2 people."
)
```

**Breakdown:**

1. **Role Definition**
   - `"You are an expert chef"`
   - Sets the persona and expertise level

2. **Core Constraints**
   - `"Present only one recipe at a time"` → Prevents overwhelming users
   - `"You MUST suggest a complete recipe"` → Forces complete responses
   - `"don't ask follow-up questions"` → Prevents conversational loops

3. **Behavioral Guidelines**
   - `"Be descriptive in the steps"` → Ensures quality
   - `"Have variety"` → Prevents repetitive responses
   - `"assume only basic ingredients"` → Sets reasonable defaults

4. **Output Requirements**
   - `"Mention the serving size"` → Ensures completeness

### 2.3 System Prompt Design Patterns

#### Pattern 1: Role + Rules + Format

```python
PROMPT = """
You are a [ROLE] specializing in [DOMAIN].

RULES:
- Always [REQUIREMENT_1]
- Never [PROHIBITION_1]
- If [CONDITION], then [ACTION]

OUTPUT FORMAT:
[Specific formatting instructions]
"""
```

#### Pattern 2: Persona + Constraints + Examples

```python
PROMPT = """
You are [PERSONA_DESCRIPTION].

CONSTRAINTS:
1. [CONSTRAINT_1]
2. [CONSTRAINT_2]

EXAMPLE OUTPUT:
[Show desired output format]
"""
```

#### Pattern 3: Task + Guidelines + Safety

```python
PROMPT = """
TASK: [Clear task description]

GUIDELINES:
- [GUIDELINE_1]
- [GUIDELINE_2]

SAFETY:
- If the user asks for [UNSAFE_THING], [SAFE_RESPONSE]
"""
```

### 2.4 Markdown Formatting in System Prompts

**Why Markdown?** It provides:
- ✅ Consistent, readable output
- ✅ Easy to parse programmatically
- ✅ Professional appearance
- ✅ Clear structure for users

**Example prompt with Markdown instructions:**

```python
PROMPT = """
Structure all recipe responses using Markdown:

## [Recipe Name]

[Brief description 1-3 sentences]

### Ingredients
* [ingredient 1]
* [ingredient 2]

### Instructions
1. [Step 1]
2. [Step 2]

### Tips (optional)
* [Tip 1]
"""
```

### 2.5 Testing System Prompts

#### Create a Diverse Test Suite

Your test queries should cover:

1. **Cuisine Types**
   - "Italian pasta dish"
   - "Spicy Thai curry"
   - "Japanese ramen recipe"

2. **Dietary Restrictions**
   - "Vegan dessert recipe"
   - "Gluten-free breakfast ideas"
   - "Keto dinner options"

3. **Available Ingredients**
   - "What can I make with chicken, rice, and broccoli?"
   - "Recipe using eggs, cheese, and spinach"

4. **Time Constraints**
   - "Quick lunch under 15 minutes"
   - "30-minute dinner recipe"

5. **Skill Levels**
   - "Beginner-friendly baking"
   - "Advanced cooking techniques"

6. **Ambiguous Queries**
   - "Something healthy for dinner"
   - "Easy recipe please"

#### Bulk Testing Script Pattern

```python
import csv
import litellm
from dotenv import load_dotenv

load_dotenv()

def test_query(query: str, system_prompt: str) -> str:
    """Test a single query against the system prompt."""
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": query}
    ]

    response = litellm.completion(
        model="gpt-4o-mini",
        messages=messages
    )

    return response.choices[0].message.content

def bulk_test(queries_csv: str, system_prompt: str, output_csv: str):
    """Run bulk testing and save results."""
    results = []

    with open(queries_csv, 'r') as f:
        reader = csv.DictReader(f)
        queries = list(reader)

    for query_data in queries:
        query = query_data['query']
        response = test_query(query, system_prompt)

        results.append({
            'query_id': query_data['id'],
            'query': query,
            'response': response
        })

    # Save results
    with open(output_csv, 'w') as f:
        writer = csv.DictWriter(f, fieldnames=['query_id', 'query', 'response'])
        writer.writeheader()
        writer.writerows(results)

# Usage
bulk_test('data/sample_queries.csv', SYSTEM_PROMPT, 'results/responses.csv')
```

### 2.6 Common Pitfalls and Solutions

| Pitfall | Problem | Solution |
|---------|---------|----------|
| **Too Vague** | "Be helpful" | "Always provide ingredient measurements in both metric and imperial units" |
| **Too Restrictive** | "Only suggest recipes from cookbook X" | "Suggest recipes based on available ingredients, using creative combinations when needed" |
| **Conflicting Rules** | "Be concise" + "Be very detailed" | Define when to be concise vs. detailed |
| **No Safety Clause** | Handles all requests | "If asked for unsafe recipes, politely decline" |
| **Unclear Output** | Free-form responses | Specify exact Markdown structure |

### 2.7 Exercise: Write Your Own System Prompt

**Task:** Create a system prompt for a "Nutrition Advisor Bot" that:
- Explains nutritional content of foods
- Provides dietary recommendations
- Never provides medical advice
- Uses structured output with sections

**Requirements:**
1. Define the role clearly
2. Specify at least 3 constraints
3. Include a safety clause
4. Specify output format
5. Test with 10 diverse queries

---

## 3. Error Analysis & Failure Taxonomies

### 3.1 Why Error Analysis Matters

After deploying your AI system with a good prompt, you'll discover it still fails in unexpected ways. **Error analysis** is the systematic process of:
- 🔍 Identifying failure patterns
- 📊 Categorizing failure types
- 📝 Documenting failure modes
- 🎯 Prioritizing improvements

### 3.2 The Open Coding Method

**Open coding** is an exploratory analysis technique where you:
1. Review interaction traces without preconceived categories
2. Assign descriptive labels/notes to observations
3. Identify patterns and themes
4. Group similar failures together

#### Open Coding Process

```
┌─────────────────────────────────────────────────────┐
│ Step 1: Collect Traces                              │
│ - Run bot on diverse queries                        │
│ - Record full conversations                         │
│ - Aim for 20-50+ traces                            │
└─────────────────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────────────────┐
│ Step 2: Initial Review                              │
│ - Read each trace carefully                         │
│ - Note anything unexpected                          │
│ - Don't categorize yet, just observe               │
└─────────────────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────────────────┐
│ Step 3: Descriptive Labeling                        │
│ - Add open codes to each trace                      │
│ - "missing serving size"                            │
│ - "time estimate seems wrong"                       │
│ - "doesn't verify dietary restriction"              │
└─────────────────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────────────────┐
│ Step 4: Pattern Identification                      │
│ - Look for recurring themes                         │
│ - Group similar observations                        │
│ - This feeds into axial coding                      │
└─────────────────────────────────────────────────────┘
```

#### Example: Open Coding a Recipe Bot Trace

**Trace:**
```
User: "Quick egg spinach cheese recipe pls"

Bot: "Here's a quick scramble:
- 2 eggs
- 1 cup spinach
- Shredded cheese
- Optional: garlic powder, red pepper flakes

Instructions:
1. Heat pan, add spinach until wilted
2. Add eggs, scramble
3. Add cheese, mix until melted
4. Optionally season with garlic powder or red pepper"
```

**Open Codes:**
- `no_serving_size` → Doesn't say how many people this serves
- `vague_measurement` → "Shredded cheese" has no quantity
- `optional_complexity` → Suggests optional ingredients for "quick" recipe
- `missing_cooking_time` → No time estimate provided

### 3.3 Axial Coding: Building Taxonomies

**Axial coding** takes your open codes and organizes them into structured **failure mode taxonomies**.

#### Taxonomy Structure

Each failure mode should include:
1. **Title** - Clear, concise name
2. **Definition** - One sentence explaining the failure
3. **Examples** - 2-3 real instances from your traces

#### Example Failure Taxonomy: Recipe Chatbot

**Failure Mode 1: Missing Serving Size Information**
- **Definition**: Bot fails to specify the number of servings or portion sizes in the recipe.
- **Examples**:
  1. *Query*: "Quick egg spinach cheese recipe pls"
     *Issue*: Provides "2 large eggs, 1 cup fresh spinach" without specifying servings
  2. *Query*: "Simple salmon recipe"
     *Issue*: Lists "2 salmon fillets" without indicating if this serves 1 or 2 people

**Failure Mode 2: Overcomplicated Simple Recipes**
- **Definition**: Bot provides recipes with too many ingredients or steps for what should be a simple dish.
- **Examples**:
  1. *Query*: "quick egg spinach cheese recipe pls"
     *Issue*: Includes optional garlic powder, red pepper flakes, and multiple preparation steps
  2. *Query*: "simple salmon recipe"
     *Issue*: Provides complex marinade and multiple cooking methods instead of simple approach

**Failure Mode 3: Inconsistent Time Estimates**
- **Definition**: Bot provides recipes that don't match the requested time constraints.
- **Examples**:
  1. *Query*: "30 min dinner"
     *Issue*: Suggests recipe requiring toasting, cooking meat, and multiple steps exceeding 30 min
  2. *Query*: "quick salmon dinner ideas"
     *Issue*: Includes 10-15 minute marination in a "quick" recipe

**Failure Mode 4: Missing Dietary Restriction Verification**
- **Definition**: Bot fails to properly address or verify dietary restrictions.
- **Examples**:
  1. *Query*: "low FODMAP recipe"
     *Issue*: Suggests "gluten-free wrap" without verifying if it's actually low FODMAP
  2. *Query*: "pescatarian dishes"
     *Issue*: Uses store-bought pesto without checking for animal rennet in cheese

**Failure Mode 5: Inadequate Safety Information**
- **Definition**: Bot fails to provide important safety information or cooking temperatures.
- **Examples**:
  1. *Query*: "quick salmon dinner"
     *Issue*: Doesn't mention safe internal temperature for cooked salmon
  2. *Query*: "beef casserole"
     *Issue*: Instructs to cook ground beef "until browned" without specifying 160°F (71°C)

### 3.4 Systematic Analysis Spreadsheet

Create a structured analysis spreadsheet:

| Column | Purpose |
|--------|---------|
| `Trace_ID` | Unique identifier |
| `User_Query` | Original query |
| `Bot_Response_Summary` | Brief summary of response |
| `Open_Code_Notes` | Your observations |
| `Failure_Mode_1` | Binary (0/1) if this failure present |
| `Failure_Mode_2` | Binary (0/1) |
| ... | Continue for each failure mode |

**Example Row:**
```csv
Trace_ID,User_Query,Bot_Response_Summary,Open_Code_Notes,Missing_Serving,Overcomplicated,Time_Inconsistent
T001,"quick egg recipe","Scramble with optional extras","no serving size; too many optional ingredients",1,1,0
```

### 3.5 From Taxonomy to Action

Once you have your failure taxonomy:

1. **Prioritize** by frequency and severity
2. **Design interventions**:
   - Update system prompt
   - Add retrieval/RAG
   - Implement guardrails
   - Create validation rules

3. **Measure improvement**:
   - Re-run tests
   - Calculate failure rate reduction
   - Track specific failure modes

### 3.6 Exercise: Build Your Own Taxonomy

**Task:** Analyze 20 AI system traces and build a failure taxonomy

**Steps:**
1. Choose an AI system (chatbot, code generator, etc.)
2. Generate 20+ diverse test cases
3. Perform open coding on all traces
4. Identify 5-8 distinct failure modes
5. Document with title, definition, examples
6. Create analysis spreadsheet

---

## 4. LLM-as-Judge Evaluation

### 4.1 The Problem: Evaluating at Scale

Manual evaluation doesn't scale:
- 👤 1 human can label ~50-100 examples/hour
- 📊 You need 1000s of evaluations for confidence
- 💰 Manual labeling is expensive
- 🔄 Re-evaluation after changes is tedious

**Solution:** Use an LLM to evaluate another LLM (LLM-as-Judge)

### 4.2 LLM-as-Judge Methodology

The core idea:
```
┌──────────────────────────────────────────────────────┐
│  LLM System (being evaluated)                        │
│  ↓                                                   │
│  Output to evaluate                                  │
│  ↓                                                   │
│  Judge LLM (with evaluation prompt)                  │
│  ↓                                                   │
│  PASS or FAIL + reasoning                            │
└──────────────────────────────────────────────────────┘
```

**Key Insight:** Judges aren't perfect! They have bias:
- False Positives (saying PASS when it's FAIL)
- False Negatives (saying FAIL when it's PASS)

But we can **measure and correct** this bias.

### 4.3 The Complete Pipeline

```
1. Generate or Collect Traces
   ↓
2. Manually Label Subset (150-200 examples)
   [This is your ground truth]
   ↓
3. Split Data: Train (15%) / Dev (40%) / Test (45%)
   ↓
4. Develop Judge Prompt
   - Use few-shot examples from Train set
   - Test on Dev set
   - Iterate until satisfactory
   ↓
5. Evaluate Judge Performance
   - Calculate TPR and TNR on Test set
   - These metrics measure judge bias
   ↓
6. Apply to Large Dataset
   - Run judge on 1000s of examples
   - Get raw pass rate (p_obs)
   ↓
7. Bias Correction
   - Use TPR/TNR to correct p_obs
   - Calculate true pass rate (θ)
   - Compute 95% confidence interval
```

### 4.4 Key Metrics: TPR and TNR

#### True Positive Rate (TPR) - Sensitivity

**Definition:** Of all the PASS cases, how many does the judge correctly identify as PASS?

```
TPR = True Positives / (True Positives + False Negatives)
    = Correct PASS / All actual PASS
```

**Example:**
- 60 traces labeled PASS by humans
- Judge says PASS on 54 of them
- TPR = 54/60 = 0.90 (90%)

**Interpretation:**
- High TPR (>0.90) = Judge rarely misses good responses
- Low TPR (<0.70) = Judge is too strict, rejects good responses

#### True Negative Rate (TNR) - Specificity

**Definition:** Of all the FAIL cases, how many does the judge correctly identify as FAIL?

```
TNR = True Negatives / (True Negatives + False Positives)
    = Correct FAIL / All actual FAIL
```

**Example:**
- 40 traces labeled FAIL by humans
- Judge says FAIL on 36 of them
- TNR = 36/40 = 0.90 (90%)

**Interpretation:**
- High TNR (>0.90) = Judge rarely misses failures
- Low TNR (<0.70) = Judge is too lenient, passes bad responses

### 4.5 Confusion Matrix

```
                    HUMAN LABELS (Ground Truth)
                    ┌──────────┬──────────┐
                    │   PASS   │   FAIL   │
JUDGE      ┌────────┼──────────┼──────────┤
PREDICTION │  PASS  │    TP    │    FP    │  ← Precision = TP/(TP+FP)
           │        │ (Correct)│ (Lenient)│
           ├────────┼──────────┼──────────┤
           │  FAIL  │    FN    │    TN    │
           │        │ (Strict) │ (Correct)│
           └────────┴──────────┴──────────┘
                         ↓          ↓
              TPR = TP/(TP+FN)  TNR = TN/(TN+FP)
              (Sensitivity)     (Specificity)
```

### 4.6 Building an Effective Judge Prompt

#### Judge Prompt Structure

```python
JUDGE_PROMPT = """
TASK: Evaluate if a Recipe Bot response adheres to dietary restrictions.

CRITERION: Dietary Preference Adherence
When a user requests a recipe with specific dietary restrictions, the bot
MUST provide a recipe that actually meets those restrictions.

PASS DEFINITION:
- All ingredients comply with the dietary restriction
- No hidden non-compliant ingredients (e.g., honey in vegan, wheat in gluten-free)
- If substitutions are needed, they are appropriate

FAIL DEFINITION:
- Any ingredient violates the restriction
- Ambiguous ingredients without verification (e.g., "gluten-free soy sauce")
- Missing critical information about compliance

EXAMPLES:

Example 1 (PASS):
Query: "vegan pasta recipe"
Dietary Restriction: vegan
Response: "Pasta with Tomato Basil Sauce
- 8 oz pasta
- 2 cups tomatoes
- Fresh basil
- Olive oil
- Nutritional yeast (for parmesan flavor)"

Reasoning: All ingredients are vegan. Nutritional yeast is a vegan parmesan substitute.
Answer: PASS

Example 2 (FAIL):
Query: "vegan pasta recipe"
Dietary Restriction: vegan
Response: "Pasta Carbonara
- 8 oz pasta
- 2 eggs
- Parmesan cheese
- Bacon"

Reasoning: Recipe contains eggs, cheese, and bacon, all non-vegan.
Answer: FAIL

Example 3 (FAIL):
Query: "vegan dessert"
Dietary Restriction: vegan
Response: "Honey Sweetened Fruit Salad
- Mixed fruits
- 2 tbsp honey
- Coconut flakes"

Reasoning: Honey is not vegan (produced by bees). This fails the criterion.
Answer: FAIL

NOW EVALUATE:
Query: __QUERY__
Dietary Restriction: __DIETARY_RESTRICTION__
Response: __RESPONSE__

Provide your reasoning, then answer PASS or FAIL.

Output as JSON:
{
  "reasoning": "your step-by-step reasoning",
  "answer": "PASS or FAIL"
}
"""
```

#### Few-Shot Example Selection

**Strategy:** Use diverse, representative examples from your training set

```python
def select_few_shot_examples(train_data, num_positive=1, num_negative=3):
    """Select balanced few-shot examples."""

    # Separate by label
    pass_examples = [ex for ex in train_data if ex['label'] == 'PASS']
    fail_examples = [ex for ex in train_data if ex['label'] == 'FAIL']

    # Select diverse examples
    selected = []
    selected.extend(random.sample(pass_examples, num_positive))
    selected.extend(random.sample(fail_examples, num_negative))

    return selected
```

**Why 1:3 ratio?**
- Most systems have more failure cases than successes
- Judge needs to learn failure patterns well
- Helps prevent overly lenient judging

### 4.7 Iterative Judge Development

```
1. Start with Base Prompt
   ↓
2. Add 1-3 Few-Shot Examples from Train Set
   ↓
3. Test on Dev Set (40% of labeled data)
   ↓
4. Calculate TPR and TNR on Dev
   ↓
5. Analyze Errors:
   - Which cases does judge get wrong?
   - Are definitions clear enough?
   - Do examples cover edge cases?
   ↓
6. Refine Prompt:
   - Clarify definitions
   - Add edge case examples
   - Adjust reasoning structure
   ↓
7. Repeat until Dev performance is satisfactory
   ↓
8. Final Evaluation on Test Set (never touched before)
```

### 4.8 Bias Correction with Judgy Library

The `judgy` library corrects judge bias using TPR and TNR:

```python
import judgy

# After evaluating judge on test set
TPR = 0.85  # Judge catches 85% of actual PASS
TNR = 0.90  # Judge catches 90% of actual FAIL

# Run judge on large dataset (1000+ examples)
# Get observed pass rate
p_obs = 0.857  # 85.7% judged as PASS

# Correct for bias
corrected_result = judgy.correct_binary(
    p_obs=p_obs,      # Observed pass rate from judge
    TPR=TPR,          # True positive rate from test set
    TNR=TNR,          # True negative rate from test set
    n=1000            # Number of evaluated examples
)

print(f"Raw Observed: {p_obs:.3f}")
print(f"Corrected: {corrected_result.theta:.3f}")
print(f"95% CI: [{corrected_result.ci_lower:.3f}, {corrected_result.ci_upper:.3f}]")
```

**Output:**
```
Raw Observed: 0.857
Corrected: 0.926
95% CI: [0.817, 1.000]
Correction Applied: 0.069 (6.9 percentage points)
```

### 4.9 Understanding the Correction

**Why does correction matter?**

Imagine your judge has:
- TPR = 0.85 (misses 15% of good responses)
- TNR = 0.95 (misses 5% of bad responses)

If judge says 80% PASS:
- Some of those PASS are false positives (actually FAIL)
- Some actual PASS were missed (false negatives)

The correction formula accounts for both types of errors to estimate the **true pass rate**.

### 4.10 Complete Implementation Example

```python
#!/usr/bin/env python3
"""LLM-as-Judge evaluation pipeline."""

import json
import litellm
from typing import List, Dict
import judgy

def load_labeled_data(path: str) -> List[Dict]:
    """Load human-labeled ground truth."""
    with open(path, 'r') as f:
        return json.load(f)

def split_data(data: List[Dict], train=0.15, dev=0.40, test=0.45):
    """Split into train/dev/test sets."""
    n = len(data)
    train_end = int(n * train)
    dev_end = int(n * (train + dev))

    return {
        'train': data[:train_end],
        'dev': data[train_end:dev_end],
        'test': data[dev_end:]
    }

def build_judge_prompt(base_prompt: str, few_shot: List[Dict]) -> str:
    """Add few-shot examples to base prompt."""
    examples = []
    for ex in few_shot:
        examples.append(f"""
Example ({ex['label']}):
Query: {ex['query']}
Response: {ex['response']}
Reasoning: {ex['reasoning']}
Answer: {ex['label']}
""")

    return base_prompt.replace("__EXAMPLES__", "\n".join(examples))

def evaluate_with_judge(query: str, response: str, judge_prompt: str) -> str:
    """Use LLM judge to evaluate a response."""
    prompt = judge_prompt.replace("__QUERY__", query).replace("__RESPONSE__", response)

    result = litellm.completion(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    # Parse JSON response
    output = json.loads(result.choices[0].message.content)
    return output['answer']  # "PASS" or "FAIL"

def calculate_tpr_tnr(predictions: List[str], ground_truth: List[str]):
    """Calculate TPR and TNR."""
    tp = sum(1 for pred, true in zip(predictions, ground_truth)
             if pred == "PASS" and true == "PASS")
    fn = sum(1 for pred, true in zip(predictions, ground_truth)
             if pred == "FAIL" and true == "PASS")
    tn = sum(1 for pred, true in zip(predictions, ground_truth)
             if pred == "FAIL" and true == "FAIL")
    fp = sum(1 for pred, true in zip(predictions, ground_truth)
             if pred == "PASS" and true == "FAIL")

    TPR = tp / (tp + fn) if (tp + fn) > 0 else 0
    TNR = tn / (tn + fp) if (tn + fp) > 0 else 0

    return TPR, TNR

# Main pipeline
if __name__ == "__main__":
    # Load and split data
    data = load_labeled_data("labeled_traces.json")
    splits = split_data(data)

    # Build judge prompt with few-shot from train
    judge_prompt = build_judge_prompt(BASE_PROMPT, splits['train'][:4])

    # Evaluate on test set
    test_predictions = []
    test_labels = []

    for trace in splits['test']:
        pred = evaluate_with_judge(trace['query'], trace['response'], judge_prompt)
        test_predictions.append(pred)
        test_labels.append(trace['label'])

    # Calculate TPR and TNR
    TPR, TNR = calculate_tpr_tnr(test_predictions, test_labels)
    print(f"Judge Performance:")
    print(f"  TPR: {TPR:.3f}")
    print(f"  TNR: {TNR:.3f}")

    # Apply to large dataset
    large_dataset = load_unlabeled_traces("production_traces.json")
    predictions = [evaluate_with_judge(t['query'], t['response'], judge_prompt)
                   for t in large_dataset]

    p_obs = sum(1 for p in predictions if p == "PASS") / len(predictions)

    # Bias correction
    result = judgy.correct_binary(p_obs=p_obs, TPR=TPR, TNR=TNR, n=len(predictions))

    print(f"\nResults:")
    print(f"  Raw Pass Rate: {p_obs:.3f}")
    print(f"  Corrected Pass Rate: {result.theta:.3f}")
    print(f"  95% CI: [{result.ci_lower:.3f}, {result.ci_upper:.3f}]")
```

### 4.11 Exercise: Build Your Own Judge

**Task:** Create an LLM-as-Judge for "Recipe Time Accuracy"

**Criterion:** If a user asks for a "quick" or time-bounded recipe, the bot should provide a recipe that actually meets that time constraint.

**Requirements:**
1. Define PASS/FAIL criteria clearly
2. Create judge prompt with 3-4 few-shot examples
3. Label 100 test cases manually
4. Calculate TPR and TNR
5. Apply to 500 traces with bias correction

---

## 5. RAG & Retrieval Evaluation

### 5.1 Introduction to RAG

**RAG (Retrieval-Augmented Generation)** enhances LLM responses by:
1. Retrieving relevant documents from a knowledge base
2. Including retrieved context in the LLM prompt
3. Generating responses grounded in retrieved information

### 5.2 When to Use RAG

RAG is ideal for:
- ✅ Specific factual questions ("What temperature for crispy vegetables?")
- ✅ Domain-specific knowledge (recipes, technical docs)
- ✅ Up-to-date information (recent data)
- ✅ Reducing hallucinations (grounding in facts)

RAG is NOT needed for:
- ❌ General conversation
- ❌ Creative tasks
- ❌ Simple queries LLM already knows

### 5.3 BM25: The Retrieval Algorithm

**BM25** (Best Matching 25) is a ranking function for information retrieval.

#### How BM25 Works

```
┌──────────────────────────────────────────────────────┐
│ BM25 Score Components                                │
├──────────────────────────────────────────────────────┤
│                                                      │
│ 1. Term Frequency (TF)                               │
│    → How often does query term appear in document?   │
│    → More appearances = higher score                 │
│                                                      │
│ 2. Inverse Document Frequency (IDF)                  │
│    → How rare is the term across all documents?      │
│    → Rare terms = more discriminative = higher score │
│                                                      │
│ 3. Document Length Normalization                     │
│    → Longer documents get penalized                  │
│    → Prevents bias toward lengthy documents          │
└──────────────────────────────────────────────────────┘
```

#### BM25 Formula (Simplified)

```
score(Q, D) = Σ IDF(qi) × (f(qi, D) × (k1 + 1)) / (f(qi, D) + k1 × (1 - b + b × |D| / avgdl))

Where:
- Q = query
- D = document
- qi = query term i
- f(qi, D) = frequency of qi in D
- |D| = document length
- avgdl = average document length
- k1, b = tuning parameters (typically k1=1.5, b=0.75)
```

**Key Insight:** BM25 balances term importance, frequency, and document length.

### 5.4 Building a Retrieval System

#### Step 1: Data Processing

```python
import json
import re
from pathlib import Path
from typing import List, Dict

def preprocess_text(text: str) -> List[str]:
    """Tokenize and normalize text for BM25."""
    # Lowercase
    text = text.lower()

    # Remove special characters
    text = re.sub(r'[^\w\s]', ' ', text)

    # Tokenize
    tokens = text.split()

    # Remove empty strings
    tokens = [t for t in tokens if t]

    return tokens

def process_recipes(raw_recipes: List[Dict]) -> List[Dict]:
    """Process raw recipe data for retrieval."""
    processed = []

    for recipe in raw_recipes:
        # Combine searchable fields
        searchable_text = ' '.join([
            recipe.get('name', ''),
            recipe.get('description', ''),
            ' '.join(recipe.get('ingredients', [])),
            ' '.join(recipe.get('steps', [])),
            ' '.join(recipe.get('tags', []))
        ])

        # Tokenize
        tokens = preprocess_text(searchable_text)

        processed.append({
            'id': recipe['id'],
            'name': recipe['name'],
            'tokens': tokens,
            'original': recipe
        })

    return processed
```

#### Step 2: Build BM25 Index

```python
from rank_bm25 import BM25Okapi
import pickle

class RecipeRetriever:
    """BM25-based recipe retrieval system."""

    def __init__(self):
        self.recipes = []
        self.bm25_index = None
        self.is_indexed = False

    def load_recipes(self, recipes_path: Path):
        """Load recipes from JSON file."""
        with open(recipes_path, 'r') as f:
            raw_recipes = json.load(f)

        self.recipes = process_recipes(raw_recipes)
        print(f"Loaded {len(self.recipes)} recipes")

    def build_index(self):
        """Build BM25 index."""
        # Extract token lists
        documents = [recipe['tokens'] for recipe in self.recipes]

        # Create BM25 index
        self.bm25_index = BM25Okapi(documents)
        self.is_indexed = True

        print("BM25 index built successfully")

    def save_index(self, path: Path):
        """Save index to disk for reuse."""
        with open(path, 'wb') as f:
            pickle.dump(self.bm25_index, f)

    def load_index(self, path: Path):
        """Load pre-built index."""
        with open(path, 'rb') as f:
            self.bm25_index = pickle.load(f)
        self.is_indexed = True

    def retrieve(self, query: str, top_k: int = 5) -> List[Dict]:
        """Retrieve top-k recipes for query."""
        # Tokenize query
        query_tokens = preprocess_text(query)

        # Get BM25 scores
        scores = self.bm25_index.get_scores(query_tokens)

        # Get top-k indices
        top_indices = sorted(range(len(scores)),
                           key=lambda i: scores[i],
                           reverse=True)[:top_k]

        # Build results
        results = []
        for idx in top_indices:
            recipe = self.recipes[idx].copy()
            recipe['bm25_score'] = float(scores[idx])
            recipe['rank'] = len(results) + 1
            results.append(recipe)

        return results

# Usage
retriever = RecipeRetriever()
retriever.load_recipes("data/processed_recipes.json")
retriever.build_index()
retriever.save_index("data/bm25_index.pkl")

# Retrieve
results = retriever.retrieve("air fryer chicken crispy", top_k=5)
for i, recipe in enumerate(results):
    print(f"{i+1}. {recipe['name']} (Score: {recipe['bm25_score']:.2f})")
```

### 5.5 Evaluating Retrieval Systems

#### Key Metrics

**1. Recall@k**
- What fraction of queries have the target document in top k results?
- Most important metric for retrieval

```python
def recall_at_k(retrieved_ids: List[int], target_id: int, k: int) -> float:
    """Calculate recall@k."""
    return 1.0 if target_id in retrieved_ids[:k] else 0.0

# Example
retrieved = [42, 17, 93, 8, 51]  # Retrieved recipe IDs
target = 93                       # Target recipe ID

recall_1 = recall_at_k(retrieved, target, 1)  # 0.0 (not rank 1)
recall_3 = recall_at_k(retrieved, target, 3)  # 1.0 (in top 3)
recall_5 = recall_at_k(retrieved, target, 5)  # 1.0 (in top 5)
```

**2. Mean Reciprocal Rank (MRR)**
- Average of 1/rank across all queries
- Measures ranking quality

```python
def reciprocal_rank(retrieved_ids: List[int], target_id: int) -> float:
    """Calculate reciprocal rank for a query."""
    try:
        rank = retrieved_ids.index(target_id) + 1  # 1-indexed
        return 1.0 / rank
    except ValueError:
        return 0.0  # Not found

# Example
retrieved = [42, 17, 93, 8, 51]
target = 93

rr = reciprocal_rank(retrieved, target)  # 1/3 = 0.333

# MRR across multiple queries
reciprocal_ranks = [0.5, 1.0, 0.333, 0.0, 0.25]  # From 5 queries
mrr = sum(reciprocal_ranks) / len(reciprocal_ranks)  # 0.417
```

### 5.6 Synthetic Query Generation

To evaluate retrieval, you need query-document pairs. Generate them synthetically:

```python
import litellm
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

def generate_query_for_recipe(recipe: Dict) -> Dict:
    """Generate a realistic query that should retrieve this recipe."""

    # Extract salient facts
    salient_prompt = f"""
Given this recipe, extract 1-2 specific, unique facts that would help
someone find it (e.g., cooking method, temperature, timing, unique ingredient).

Recipe: {recipe['name']}
Ingredients: {', '.join(recipe['ingredients'][:10])}
Steps: {' '.join(recipe['steps'][:3])}

Salient facts (brief):
"""

    salient_response = litellm.completion(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": salient_prompt}],
        temperature=0.3
    )

    salient_fact = salient_response.choices[0].message.content.strip()

    # Generate query based on salient facts
    query_prompt = f"""
Generate a realistic user query that someone would ask to find this recipe.
The query should include these specific details: {salient_fact}

Make it natural, conversational, and question-like.

Query:
"""

    query_response = litellm.completion(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": query_prompt}],
        temperature=0.5
    )

    query = query_response.choices[0].message.content.strip()

    return {
        'query': query,
        'source_recipe_id': recipe['id'],
        'source_recipe_name': recipe['name'],
        'salient_fact': salient_fact
    }

def batch_generate_queries(recipes: List[Dict], max_workers: int = 10) -> List[Dict]:
    """Generate queries in parallel."""
    queries = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(generate_query_for_recipe, recipe)
                   for recipe in recipes]

        for future in tqdm(futures, desc="Generating queries"):
            try:
                query_data = future.result()
                queries.append(query_data)
            except Exception as e:
                print(f"Error: {e}")

    return queries

# Usage
recipes = load_recipes("data/processed_recipes.json")
synthetic_queries = batch_generate_queries(recipes[:100])  # Generate 100

# Save
with open("data/synthetic_queries.json", 'w') as f:
    json.dump(synthetic_queries, f, indent=2)
```

### 5.7 Complete Evaluation Pipeline

```python
def evaluate_retrieval(retriever, queries: List[Dict], top_k: int = 5) -> Dict:
    """Evaluate retrieval system on query set."""
    results = []

    for query_data in tqdm(queries, desc="Evaluating"):
        query = query_data['query']
        target_id = query_data['source_recipe_id']

        # Retrieve
        retrieved = retriever.retrieve(query, top_k=10)
        retrieved_ids = [r['id'] for r in retrieved]

        # Calculate metrics
        result = {
            'query': query,
            'target_id': target_id,
            'target_name': query_data['source_recipe_name'],
            'recall_1': recall_at_k(retrieved_ids, target_id, 1),
            'recall_3': recall_at_k(retrieved_ids, target_id, 3),
            'recall_5': recall_at_k(retrieved_ids, target_id, 5),
            'recall_10': recall_at_k(retrieved_ids, target_id, 10),
            'reciprocal_rank': reciprocal_rank(retrieved_ids, target_id),
            'target_rank': retrieved_ids.index(target_id) + 1 if target_id in retrieved_ids else None
        }

        results.append(result)

    # Aggregate metrics
    metrics = {
        'recall_at_1': sum(r['recall_1'] for r in results) / len(results),
        'recall_at_3': sum(r['recall_3'] for r in results) / len(results),
        'recall_at_5': sum(r['recall_5'] for r in results) / len(results),
        'recall_at_10': sum(r['recall_10'] for r in results) / len(results),
        'mrr': sum(r['reciprocal_rank'] for r in results) / len(results),
        'total_queries': len(results)
    }

    return metrics, results

# Run evaluation
retriever = RecipeRetriever()
retriever.load_recipes("data/processed_recipes.json")
retriever.load_index("data/bm25_index.pkl")

queries = load_queries("data/synthetic_queries.json")
metrics, detailed_results = evaluate_retrieval(retriever, queries)

print("Retrieval Performance:")
print(f"  Recall@1:  {metrics['recall_at_1']:.3f}")
print(f"  Recall@3:  {metrics['recall_at_3']:.3f}")
print(f"  Recall@5:  {metrics['recall_at_5']:.3f}")
print(f"  Recall@10: {metrics['recall_at_10']:.3f}")
print(f"  MRR:       {metrics['mrr']:.3f}")
```

### 5.8 Query Optimization with LLM

Sometimes user queries don't match well with document text. Use an LLM to rewrite queries:

```python
def rewrite_query(query: str) -> str:
    """Rewrite query to be more effective for BM25 search."""
    prompt = f"""
Rewrite this cooking query to be more effective for recipe search.
Focus on terms that would appear in recipe titles, ingredients, and instructions.

Guidelines:
- Use specific cooking terms
- Include equipment names if mentioned
- Add related cooking techniques
- Remove question words (what, how, when)
- Keep it concise but descriptive

Original: "{query}"

Optimized search query:
"""

    response = litellm.completion(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    return response.choices[0].message.content.strip()

# Example
original = "What air fryer settings for frozen chicken tenders?"
rewritten = rewrite_query(original)
# Output: "air fryer frozen chicken tenders temperature time crispy"

# Use in retrieval
results_original = retriever.retrieve(original)
results_rewritten = retriever.retrieve(rewritten)

# Compare
print(f"Original query recall: {calculate_recall(results_original)}")
print(f"Rewritten query recall: {calculate_recall(results_rewritten)}")
```

### 5.9 Exercise: Build Your Own RAG System

**Task:** Create a RAG system for a domain of your choice

**Requirements:**
1. Collect/create 100+ documents
2. Build BM25 retrieval system
3. Generate 50 synthetic queries
4. Evaluate with Recall@k and MRR
5. Implement query rewriting
6. Compare baseline vs. rewritten performance
7. Analyze failure cases

---

## 6. Agent Failure Analysis

### 6.1 Understanding Agent Architectures

**Agents** are AI systems that follow multi-step reasoning patterns:

```
User Input
   ↓
Parse Request (LLM)
   ↓
Plan Tool Calls (LLM)
   ↓
Generate Arguments (LLM)
   ↓
Execute Tool
   ↓
Compose Response (LLM)
   ↓
Deliver Response
```

Each step can fail, and failures propagate through the pipeline.

### 6.2 Agent Pipeline State Taxonomy

For Recipe Chatbot agent, we define 10 canonical states:

| # | State | Description | Failure Examples |
|---|-------|-------------|------------------|
| 1 | `ParseRequest` | LLM interprets user message | Misunderstands intent |
| 2 | `PlanToolCalls` | LLM decides which tools | Wrong tool selection |
| 3 | `GenCustomerArgs` | LLM constructs customer DB args | Malformed query |
| 4 | `GetCustomerProfile` | Executes customer-profile tool | DB error, timeout |
| 5 | `GenRecipeArgs` | LLM constructs recipe DB args | Wrong parameters |
| 6 | `GetRecipes` | Executes recipe-search tool | No results, error |
| 7 | `GenWebArgs` | LLM constructs web search args | Bad search terms |
| 8 | `GetWebInfo` | Executes web-search tool | Network error, no results |
| 9 | `ComposeResponse` | LLM drafts final answer | Incomplete, incorrect |
| 10 | `DeliverResponse` | Agent sends answer | Formatting error |

### 6.3 Failure Transition Analysis

**Goal:** Understand where the agent succeeds last and where it fails first.

Each conversation trace has:
- `last_success_state`: The last state that succeeded
- `first_failure_state`: The first state that failed

This forms a **directed edge** in a transition matrix.

### 6.4 Building the Transition Matrix

```python
import json
import numpy as np
from typing import List, Dict

def build_transition_matrix(traces: List[Dict], states: List[str]) -> np.ndarray:
    """Build failure transition matrix from labeled traces."""
    n_states = len(states)
    state_to_idx = {state: i for i, state in enumerate(states)}

    # Initialize matrix
    matrix = np.zeros((n_states, n_states))

    # Count transitions
    for trace in traces:
        last_success = trace['last_success_state']
        first_failure = trace['first_failure_state']

        i = state_to_idx[last_success]
        j = state_to_idx[first_failure]

        matrix[i, j] += 1

    return matrix

# Load data
with open('data/labeled_traces.json', 'r') as f:
    traces = json.load(f)

# Define state order
states = [
    'ParseRequest',
    'PlanToolCalls',
    'GenCustomerArgs',
    'GetCustomerProfile',
    'GenRecipeArgs',
    'GetRecipes',
    'GenWebArgs',
    'GetWebInfo',
    'ComposeResponse',
    'DeliverResponse'
]

# Build matrix
transition_matrix = build_transition_matrix(traces, states)
```

### 6.5 Visualizing Failure Patterns

```python
import matplotlib.pyplot as plt
import seaborn as sns

def plot_failure_heatmap(matrix: np.ndarray, states: List[str], output_path: str):
    """Create heat-map visualization of failure transitions."""

    plt.figure(figsize=(12, 10))

    # Create heatmap
    sns.heatmap(
        matrix,
        xticklabels=states,
        yticklabels=states,
        annot=True,
        fmt='.0f',
        cmap='YlOrRd',
        cbar_kws={'label': 'Number of Failures'}
    )

    plt.xlabel('First Failure State')
    plt.ylabel('Last Success State')
    plt.title('Agent Failure Transition Heat-Map')
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    print(f"Heat-map saved to {output_path}")

# Visualize
plot_failure_heatmap(
    transition_matrix,
    states,
    'results/failure_transition_heatmap.png'
)
```

### 6.6 Analyzing Failure Patterns

**Questions to ask:**

1. **Which states fail most often?**
   - Sum columns to see most common first failures
   - High-frequency failures → prioritize fixing these

2. **Which transitions are most common?**
   - Look for hot spots in the matrix
   - Common transitions reveal systemic issues

3. **Do failures cluster by type?**
   - LLM reasoning failures (Parse, Plan, Compose)
   - Tool execution failures (Get*, Execute*)
   - Argument generation failures (Gen*Args)

4. **Are there surprising transitions?**
   - Unexpected transitions may reveal edge cases
   - Zero-frequency transitions might be worth testing

```python
def analyze_failure_patterns(matrix: np.ndarray, states: List[str]):
    """Analyze and report failure patterns."""

    # Most common first failures
    first_failure_counts = matrix.sum(axis=0)
    top_failures = sorted(enumerate(first_failure_counts),
                         key=lambda x: x[1],
                         reverse=True)

    print("Most Common First Failures:")
    for idx, count in top_failures[:5]:
        print(f"  {states[idx]}: {count:.0f} failures")

    # Most common transitions
    transitions = []
    for i in range(len(states)):
        for j in range(len(states)):
            if matrix[i, j] > 0:
                transitions.append((states[i], states[j], matrix[i, j]))

    transitions.sort(key=lambda x: x[2], reverse=True)

    print("\nMost Common Failure Transitions:")
    for last_success, first_failure, count in transitions[:5]:
        print(f"  {last_success} → {first_failure}: {count:.0f}")

    # Failure clustering
    llm_failures = sum(first_failure_counts[i] for i, state in enumerate(states)
                      if 'Gen' in state or 'Parse' in state or 'Plan' in state or 'Compose' in state)
    tool_failures = sum(first_failure_counts[i] for i, state in enumerate(states)
                       if 'Get' in state)

    print(f"\nFailure Type Distribution:")
    print(f"  LLM Reasoning: {llm_failures:.0f}")
    print(f"  Tool Execution: {tool_failures:.0f}")

# Run analysis
analyze_failure_patterns(transition_matrix, states)
```

### 6.7 From Analysis to Action

Once you identify failure patterns:

**High-frequency failures:**
1. Add input validation
2. Improve error handling
3. Add retry logic
4. Enhance prompts

**LLM reasoning failures:**
1. Refine system prompts
2. Add few-shot examples
3. Use chain-of-thought
4. Add validation steps

**Tool execution failures:**
1. Improve error messages
2. Add fallback tools
3. Implement timeouts
4. Add caching

### 6.8 Exercise: Agent Failure Analysis

**Task:** Analyze failure patterns in an agent system

**Requirements:**
1. Collect 50+ agent conversation traces
2. Label each with last_success_state and first_failure_state
3. Build transition matrix
4. Create heat-map visualization
5. Write analysis report:
   - Top 5 failure states
   - Top 5 transitions
   - Failure clustering patterns
   - Recommended improvements

---

## 7. Advanced Topics

### 7.1 Parallel Processing with ThreadPoolExecutor

**Why parallel processing?**
- LLM API calls are I/O-bound (waiting for response)
- CPU sits idle during network requests
- Process 10x-100x faster with parallelism

#### Basic Pattern

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

def process_single_item(item):
    """Process one item (e.g., call LLM API)."""
    # Do work
    result = expensive_operation(item)
    return result

def process_batch_parallel(items: List, max_workers: int = 10):
    """Process items in parallel."""
    results = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        futures = [executor.submit(process_single_item, item) for item in items]

        # Collect results with progress bar
        for future in tqdm(as_completed(futures), total=len(items)):
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                print(f"Error: {e}")
                results.append(None)

    return results
```

#### Maintaining Order

```python
def process_batch_ordered(items: List, max_workers: int = 10):
    """Process in parallel but maintain input order."""
    results = [None] * len(items)  # Pre-allocate

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Map each future to its index
        future_to_index = {
            executor.submit(process_single_item, item): i
            for i, item in enumerate(items)
        }

        for future in as_completed(future_to_index):
            index = future_to_index[future]
            try:
                results[index] = future.result()
            except Exception as e:
                print(f"Error at index {index}: {e}")
                results[index] = None

    return results
```

#### With Retry Logic

```python
import time

def process_with_retry(item, max_retries: int = 3):
    """Process with exponential backoff retry."""
    for attempt in range(max_retries):
        try:
            return process_single_item(item)
        except Exception as e:
            if attempt == max_retries - 1:
                print(f"Failed after {max_retries} attempts: {e}")
                return None
            wait_time = 0.5 * (2 ** attempt)  # Exponential backoff
            time.sleep(wait_time)

    return None

def process_batch_resilient(items: List, max_workers: int = 10):
    """Process with retry logic."""
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(process_with_retry, item) for item in items]
        results = [f.result() for f in tqdm(as_completed(futures), total=len(items))]

    return results
```

### 7.2 Query Rewrite Strategies

Three approaches to optimizing queries for retrieval:

#### Strategy 1: Keyword Extraction

```python
def extract_keywords(query: str) -> str:
    """Extract the most important search keywords."""
    prompt = f"""
Extract the most important keywords from this cooking query for recipe search.

Focus on:
- Cooking methods (air fry, bake, grill)
- Equipment (air fryer, oven, pressure cooker)
- Key ingredients (chicken, vegetables, pasta)
- Cooking specifics (temperature, time, texture)

Query: "{query}"

Keywords (space-separated):
"""

    response = litellm.completion(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )

    return response.choices[0].message.content.strip()
```

#### Strategy 2: Query Rewriting

```python
def rewrite_query(query: str) -> str:
    """Rewrite query to be more effective for search."""
    prompt = f"""
Rewrite this cooking query for better recipe search results.

Guidelines:
1. Use specific cooking terms
2. Include equipment names if mentioned
3. Add related techniques
4. Use common recipe vocabulary
5. Keep concise but descriptive
6. Remove question words

Original: "{query}"

Optimized query:
"""

    response = litellm.completion(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    return response.choices[0].message.content.strip()
```

#### Strategy 3: Query Expansion

```python
def expand_query(query: str) -> str:
    """Expand query with synonyms and related terms."""
    prompt = f"""
Expand this cooking query with relevant synonyms and related terms
that might appear in recipes.

Add:
1. Synonyms for cooking methods
2. Alternative ingredient names
3. Related cooking techniques
4. Equipment alternatives

Keep focused on cooking domain.

Original: "{query}"

Expanded query:
"""

    response = litellm.completion(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4
    )

    return response.choices[0].message.content.strip()
```

#### Comparing Strategies

```python
def compare_strategies(query: str, retriever, target_id: int):
    """Compare all three strategies."""

    # Baseline
    results_baseline = retriever.retrieve(query)

    # Strategy 1: Keywords
    query_keywords = extract_keywords(query)
    results_keywords = retriever.retrieve(query_keywords)

    # Strategy 2: Rewrite
    query_rewritten = rewrite_query(query)
    results_rewritten = retriever.retrieve(query_rewritten)

    # Strategy 3: Expand
    query_expanded = expand_query(query)
    results_expanded = retriever.retrieve(query_expanded)

    # Compare
    def check_recall(results, target_id):
        return 1 if target_id in [r['id'] for r in results[:5]] else 0

    print(f"Original: {query}")
    print(f"  Keywords: {query_keywords}")
    print(f"    Recall@5: {check_recall(results_keywords, target_id)}")
    print(f"  Rewritten: {query_rewritten}")
    print(f"    Recall@5: {check_recall(results_rewritten, target_id)}")
    print(f"  Expanded: {query_expanded}")
    print(f"    Recall@5: {check_recall(results_expanded, target_id)}")
```

### 7.3 Multi-Provider LLM Integration

Use **LiteLLM** for provider-agnostic LLM calls:

```python
import litellm
import os

# Set API keys
os.environ['OPENAI_API_KEY'] = 'your-key'
os.environ['ANTHROPIC_API_KEY'] = 'your-key'

# OpenAI
response = litellm.completion(
    model="openai/gpt-4o-mini",
    messages=[{"role": "user", "content": "Hello"}]
)

# Anthropic
response = litellm.completion(
    model="anthropic/claude-3-haiku-20240307",
    messages=[{"role": "user", "content": "Hello"}]
)

# Together AI
response = litellm.completion(
    model="together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1",
    messages=[{"role": "user", "content": "Hello"}]
)

# Generic interface
def call_llm(prompt: str, model: str = "gpt-4o-mini", provider: str = "openai"):
    """Provider-agnostic LLM call."""
    model_string = f"{provider}/{model}" if provider else model

    response = litellm.completion(
        model=model_string,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content
```

### 7.4 Caching and Performance Optimization

#### Response Caching

```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=1000)
def cached_llm_call(prompt: str, model: str) -> str:
    """Cache LLM responses to avoid duplicate calls."""
    response = litellm.completion(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# Usage
result1 = cached_llm_call("What is 2+2?", "gpt-4o-mini")  # Makes API call
result2 = cached_llm_call("What is 2+2?", "gpt-4o-mini")  # Returns cached result
```

#### Persistent Caching

```python
import json
from pathlib import Path

class PersistentCache:
    """Disk-based cache for LLM responses."""

    def __init__(self, cache_dir: str = ".cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)

    def _get_cache_key(self, prompt: str, model: str) -> str:
        """Generate cache key from prompt and model."""
        combined = f"{model}:{prompt}"
        return hashlib.md5(combined.encode()).hexdigest()

    def get(self, prompt: str, model: str):
        """Get cached response if exists."""
        key = self._get_cache_key(prompt, model)
        cache_file = self.cache_dir / f"{key}.json"

        if cache_file.exists():
            with open(cache_file, 'r') as f:
                return json.load(f)['response']
        return None

    def set(self, prompt: str, model: str, response: str):
        """Cache response."""
        key = self._get_cache_key(prompt, model)
        cache_file = self.cache_dir / f"{key}.json"

        with open(cache_file, 'w') as f:
            json.dump({'prompt': prompt, 'model': model, 'response': response}, f)

    def call_with_cache(self, prompt: str, model: str) -> str:
        """Call LLM with caching."""
        # Check cache first
        cached = self.get(prompt, model)
        if cached:
            return cached

        # Make API call
        response = litellm.completion(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )

        result = response.choices[0].message.content

        # Cache result
        self.set(prompt, model, result)

        return result

# Usage
cache = PersistentCache()
response = cache.call_with_cache("What is AI?", "gpt-4o-mini")
```

### 7.5 Progress Tracking and Monitoring

```python
from tqdm import tqdm
import time

# Basic progress bar
for item in tqdm(items, desc="Processing"):
    process(item)

# Nested progress bars
for batch in tqdm(batches, desc="Batches"):
    for item in tqdm(batch, desc="Items", leave=False):
        process(item)

# Custom progress tracking
class ProgressTracker:
    """Track multiple metrics during processing."""

    def __init__(self, total: int):
        self.total = total
        self.processed = 0
        self.successful = 0
        self.failed = 0
        self.start_time = time.time()

    def update(self, success: bool):
        """Update progress."""
        self.processed += 1
        if success:
            self.successful += 1
        else:
            self.failed += 1

        # Print progress every 10%
        if self.processed % (self.total // 10) == 0:
            self.print_status()

    def print_status(self):
        """Print current status."""
        elapsed = time.time() - self.start_time
        rate = self.processed / elapsed if elapsed > 0 else 0
        eta = (self.total - self.processed) / rate if rate > 0 else 0

        print(f"Progress: {self.processed}/{self.total} "
              f"({self.processed/self.total*100:.1f}%) "
              f"| Success: {self.successful} | Failed: {self.failed} "
              f"| Rate: {rate:.1f}/s | ETA: {eta:.0f}s")

# Usage
tracker = ProgressTracker(len(items))
for item in items:
    success = process(item)
    tracker.update(success)
```

---

## 8. Best Practices & Production Patterns

### 8.1 Trace Collection and Storage

**Why collect traces?**
- Enable reproducible evaluation
- Support failure analysis
- Debug production issues
- Track improvements over time

#### Automatic Trace Saving

```python
from pathlib import Path
import datetime
import json

def save_conversation_trace(request, response, traces_dir="traces"):
    """Automatically save every conversation."""
    traces_path = Path(traces_dir)
    traces_path.mkdir(parents=True, exist_ok=True)

    # Generate unique filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    trace_file = traces_path / f"trace_{timestamp}.json"

    # Save trace
    trace_data = {
        "timestamp": timestamp,
        "request": request,
        "response": response,
        "metadata": {
            "model": os.environ.get("MODEL_NAME"),
            "session_id": get_session_id()
        }
    }

    with open(trace_file, 'w') as f:
        json.dump(trace_data, f, indent=2)

    return trace_file

# Integrate into API endpoint
@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    # Process request
    response = get_agent_response(request.messages)

    # Save trace automatically
    save_conversation_trace(
        request=request.dict(),
        response=response
    )

    return response
```

### 8.2 Environment Configuration

```python
# .env file
MODEL_NAME=openai/gpt-4o-mini
MODEL_NAME_JUDGE=openai/gpt-4.1-nano
OPENAI_API_KEY=your-key-here
ANTHROPIC_API_KEY=your-key-here
LOG_LEVEL=INFO
ENABLE_CACHING=true
CACHE_DIR=.cache
MAX_RETRIES=3

# Load and use
from dotenv import load_dotenv
import os

load_dotenv()

MODEL_NAME = os.environ.get("MODEL_NAME", "gpt-4o-mini")
ENABLE_CACHING = os.environ.get("ENABLE_CACHING", "false").lower() == "true"
MAX_RETRIES = int(os.environ.get("MAX_RETRIES", "3"))
```

### 8.3 Error Handling Patterns

#### Graceful Degradation

```python
def get_llm_response(prompt: str, max_retries: int = 3):
    """Call LLM with fallback strategy."""

    # Try primary model
    try:
        return call_llm(prompt, model="gpt-4o")
    except Exception as e:
        print(f"Primary model failed: {e}")

    # Fallback to cheaper model
    try:
        return call_llm(prompt, model="gpt-4o-mini")
    except Exception as e:
        print(f"Fallback model failed: {e}")

    # Last resort: return error message
    return "I apologize, but I'm experiencing technical difficulties. Please try again later."
```

#### Timeout Handling

```python
from concurrent.futures import TimeoutError as FuturesTimeoutError
from concurrent.futures import ThreadPoolExecutor

def call_with_timeout(func, args, timeout_seconds=30):
    """Call function with timeout."""
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(func, *args)
        try:
            return future.result(timeout=timeout_seconds)
        except FuturesTimeoutError:
            print(f"Function timed out after {timeout_seconds}s")
            return None
        except Exception as e:
            print(f"Function failed: {e}")
            return None

# Usage
result = call_with_timeout(
    expensive_llm_call,
    args=["complex prompt"],
    timeout_seconds=30
)
```

### 8.4 Logging and Monitoring

```python
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Log important events
def process_query(query: str):
    logger.info(f"Processing query: {query}")

    try:
        result = call_llm(query)
        logger.info(f"Query processed successfully")
        return result
    except Exception as e:
        logger.error(f"Query processing failed: {e}", exc_info=True)
        return None

# Track metrics
class MetricsLogger:
    """Log evaluation metrics over time."""

    def __init__(self, log_file="metrics.jsonl"):
        self.log_file = log_file

    def log_metrics(self, metrics: dict):
        """Append metrics to log file."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics
        }

        with open(self.log_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')

    def get_history(self):
        """Load metrics history."""
        metrics = []
        with open(self.log_file, 'r') as f:
            for line in f:
                metrics.append(json.loads(line))
        return metrics

# Usage
metrics_logger = MetricsLogger()
metrics_logger.log_metrics({
    "recall_at_5": 0.75,
    "mrr": 0.82,
    "eval_date": "2024-01-15"
})
```

### 8.5 Evaluation Workflow Automation

```python
#!/usr/bin/env python3
"""Automated evaluation pipeline."""

from pathlib import Path
import subprocess
import sys

class EvaluationPipeline:
    """Orchestrate complete evaluation workflow."""

    def __init__(self, project_dir: Path):
        self.project_dir = project_dir
        self.results_dir = project_dir / "results"
        self.results_dir.mkdir(exist_ok=True)

    def run_step(self, script_path: str, description: str):
        """Run a pipeline step."""
        print(f"\n{'='*60}")
        print(f"STEP: {description}")
        print(f"{'='*60}\n")

        try:
            subprocess.run(
                [sys.executable, script_path],
                check=True,
                cwd=self.project_dir
            )
            print(f"✅ {description} completed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ {description} failed: {e}")
            return False

    def run_complete_pipeline(self):
        """Run entire evaluation pipeline."""
        steps = [
            ("scripts/generate_queries.py", "Generate Synthetic Queries"),
            ("scripts/label_data.py", "Label Ground Truth Data"),
            ("scripts/split_data.py", "Split Train/Dev/Test"),
            ("scripts/develop_judge.py", "Develop LLM Judge"),
            ("scripts/evaluate_judge.py", "Evaluate Judge Performance"),
            ("scripts/run_evaluation.py", "Run Full Evaluation"),
        ]

        for script, description in steps:
            success = self.run_step(script, description)
            if not success:
                print(f"\n❌ Pipeline failed at: {description}")
                return False

        print(f"\n{'='*60}")
        print("✅ PIPELINE COMPLETED SUCCESSFULLY")
        print(f"{'='*60}\n")
        return True

# Usage
if __name__ == "__main__":
    pipeline = EvaluationPipeline(Path.cwd())
    pipeline.run_complete_pipeline()
```

### 8.6 Testing Best Practices

#### Unit Tests for Evaluation Functions

```python
import unittest

class TestEvaluationMetrics(unittest.TestCase):
    """Test evaluation metric calculations."""

    def test_recall_at_k(self):
        """Test recall@k calculation."""
        retrieved = [1, 2, 3, 4, 5]

        # Target in top-1
        self.assertEqual(recall_at_k(retrieved, 1, 1), 1.0)

        # Target in top-3 but not top-1
        self.assertEqual(recall_at_k(retrieved, 3, 1), 0.0)
        self.assertEqual(recall_at_k(retrieved, 3, 3), 1.0)

        # Target not in results
        self.assertEqual(recall_at_k(retrieved, 99, 5), 0.0)

    def test_reciprocal_rank(self):
        """Test reciprocal rank calculation."""
        retrieved = [1, 2, 3, 4, 5]

        # Different ranks
        self.assertEqual(reciprocal_rank(retrieved, 1), 1.0)
        self.assertEqual(reciprocal_rank(retrieved, 2), 0.5)
        self.assertEqual(reciprocal_rank(retrieved, 3), 1/3)

        # Not found
        self.assertEqual(reciprocal_rank(retrieved, 99), 0.0)

    def test_tpr_tnr_calculation(self):
        """Test TPR/TNR calculation."""
        predictions = ["PASS", "PASS", "FAIL", "FAIL"]
        labels =      ["PASS", "FAIL", "PASS", "FAIL"]

        tpr, tnr = calculate_tpr_tnr(predictions, labels)

        # TPR = 1/2 = 0.5 (1 correct PASS out of 2 actual PASS)
        self.assertEqual(tpr, 0.5)

        # TNR = 1/2 = 0.5 (1 correct FAIL out of 2 actual FAIL)
        self.assertEqual(tnr, 0.5)

if __name__ == '__main__':
    unittest.main()
```

---

## 9. Practical Exercises & Challenges

### Exercise 1: Complete Prompt Engineering Workflow

**Goal:** Design, test, and iterate on a system prompt

**Task:**
1. Choose an AI assistant domain (medical, legal, education, etc.)
2. Write initial system prompt
3. Create 20 diverse test queries
4. Run bulk test
5. Analyze responses
6. Identify 3-5 failure modes
7. Revise prompt
8. Re-test and measure improvement

**Deliverables:**
- Initial prompt
- Test queries
- Failure analysis
- Revised prompt
- Comparison of results

---

### Exercise 2: Build a Failure Taxonomy

**Goal:** Systematically identify and categorize failures

**Task:**
1. Run an AI system on 50+ diverse queries
2. Perform open coding on all traces
3. Group into 8-10 failure modes
4. Document each with:
   - Title
   - Definition (1 sentence)
   - 3 real examples
5. Create analysis spreadsheet
6. Prioritize by frequency and severity

**Deliverables:**
- 50+ interaction traces
- Open coding notes
- Failure taxonomy document
- Analysis spreadsheet
- Prioritization rationale

---

### Exercise 3: LLM-as-Judge Implementation

**Goal:** Build and validate an LLM judge with bias correction

**Task:**
1. Choose evaluation criterion (e.g., "accuracy", "helpfulness", "safety")
2. Manually label 150+ examples
3. Split: Train (15%) / Dev (40%) / Test (45%)
4. Develop judge prompt with few-shot examples
5. Iterate on Dev set until TPR > 0.85 and TNR > 0.85
6. Evaluate on Test set
7. Apply to 500+ unlabeled traces
8. Calculate corrected pass rate with 95% CI

**Deliverables:**
- 150+ labeled examples
- Judge prompt with few-shot examples
- Test set performance (TPR, TNR, confusion matrix)
- Large-scale evaluation results
- Bias correction analysis

---

### Exercise 4: RAG System with Evaluation

**Goal:** Build complete RAG pipeline with retrieval evaluation

**Task:**
1. Collect/create 200+ documents in a domain
2. Implement BM25 retrieval system
3. Generate 100 synthetic queries
4. Evaluate baseline retrieval (Recall@k, MRR)
5. Implement query rewriting strategy
6. Re-evaluate with rewriting
7. Compare baseline vs. enhanced
8. Analyze failure cases

**Deliverables:**
- 200+ processed documents
- BM25 retrieval implementation
- 100 synthetic queries
- Baseline evaluation results
- Query rewriting implementation
- Enhanced evaluation results
- Comparison analysis
- Failure case study

---

### Exercise 5: Agent Failure Analysis

**Goal:** Analyze and visualize agent failure patterns

**Task:**
1. Define 8-10 agent pipeline states
2. Collect 100+ agent conversation traces
3. Label each with last_success and first_failure states
4. Build failure transition matrix
5. Create heat-map visualization
6. Analyze patterns:
   - Top 5 failure states
   - Top 5 transitions
   - Failure clustering
7. Propose 3-5 concrete improvements

**Deliverables:**
- State taxonomy
- 100+ labeled traces
- Transition matrix
- Heat-map visualization
- Analysis report
- Improvement recommendations

---

### Challenge 1: Multi-Metric Dashboard

**Goal:** Build comprehensive evaluation dashboard

**Requirements:**
- Track 5+ metrics over time
- Visualize trends
- Compare A/B test variants
- Export reports

---

### Challenge 2: Automated Evaluation Pipeline

**Goal:** Create end-to-end automation

**Requirements:**
- Generate synthetic data
- Run evaluations
- Calculate metrics
- Generate reports
- Schedule regular runs

---

### Challenge 3: Production Monitoring System

**Goal:** Monitor AI system in production

**Requirements:**
- Log all interactions
- Track key metrics
- Alert on degradation
- Support debugging
- Dashboard for stakeholders

---

## 10. Reference Materials

### 10.1 Metrics Glossary

#### Retrieval Metrics

**Recall@k**
- **Definition:** Fraction of queries where target is in top-k results
- **Range:** [0, 1]
- **Interpretation:** Higher is better
- **Use case:** Primary metric for retrieval systems

**Mean Reciprocal Rank (MRR)**
- **Definition:** Average of 1/rank across all queries
- **Formula:** MRR = (1/n) Σ (1/rank_i)
- **Range:** [0, 1]
- **Interpretation:** Measures ranking quality
- **Use case:** When ranking matters, not just presence

**Precision@k**
- **Definition:** Fraction of top-k results that are relevant
- **Formula:** Precision@k = (relevant in top-k) / k
- **Range:** [0, 1]
- **Use case:** When multiple relevant documents exist

**NDCG (Normalized Discounted Cumulative Gain)**
- **Definition:** Ranking metric with position-based discounting
- **Range:** [0, 1]
- **Use case:** When relevance is graded (not binary)

#### Classification Metrics

**True Positive Rate (TPR) / Sensitivity / Recall**
- **Definition:** TP / (TP + FN)
- **Meaning:** Of all actual positives, fraction correctly identified
- **Range:** [0, 1]

**True Negative Rate (TNR) / Specificity**
- **Definition:** TN / (TN + FP)
- **Meaning:** Of all actual negatives, fraction correctly identified
- **Range:** [0, 1]

**Precision**
- **Definition:** TP / (TP + FP)
- **Meaning:** Of predicted positives, fraction actually positive
- **Range:** [0, 1]

**F1 Score**
- **Definition:** 2 × (Precision × Recall) / (Precision + Recall)
- **Meaning:** Harmonic mean of precision and recall
- **Range:** [0, 1]

**Accuracy**
- **Definition:** (TP + TN) / (TP + TN + FP + FN)
- **Meaning:** Overall fraction correct
- **Range:** [0, 1]
- **Caution:** Misleading with imbalanced classes

### 10.2 Statistical Concepts

**Confidence Interval**
- Range likely to contain true value
- 95% CI means 95% probability of containing true value
- Narrower CI = more confidence in estimate

**Standard Error**
- Measure of uncertainty in estimate
- SE = σ / √n (for means)
- Smaller sample = larger SE

**Bias vs. Variance**
- **Bias:** Systematic error in predictions
- **Variance:** Random error, inconsistency
- **Trade-off:** Lower bias often means higher variance

**Statistical Significance**
- p-value < 0.05 typically considered significant
- Means result unlikely due to chance
- Important for A/B tests

### 10.3 Code Pattern Library

#### Pattern: Config-Driven Evaluation

```python
import yaml

# config.yaml
"""
evaluation:
  model: gpt-4o-mini
  test_queries: data/queries.csv
  metrics:
    - recall_at_5
    - mrr
  output: results/eval.json
"""

def run_evaluation_from_config(config_path: str):
    """Run evaluation based on config file."""
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    eval_config = config['evaluation']

    # Load components
    model = eval_config['model']
    queries = load_queries(eval_config['test_queries'])

    # Run evaluation
    results = evaluate(queries, model)

    # Calculate requested metrics
    metrics = {}
    for metric_name in eval_config['metrics']:
        metrics[metric_name] = calculate_metric(results, metric_name)

    # Save
    save_results(metrics, eval_config['output'])
```

#### Pattern: Batch API Calls with Rate Limiting

```python
import time
from collections import deque

class RateLimiter:
    """Rate limit API calls."""

    def __init__(self, max_calls: int, time_window: float):
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = deque()

    def wait_if_needed(self):
        """Wait if rate limit would be exceeded."""
        now = time.time()

        # Remove old calls outside time window
        while self.calls and self.calls[0] < now - self.time_window:
            self.calls.popleft()

        # If at limit, wait
        if len(self.calls) >= self.max_calls:
            sleep_time = self.calls[0] + self.time_window - now
            if sleep_time > 0:
                time.sleep(sleep_time)
            self.wait_if_needed()  # Check again

        # Record this call
        self.calls.append(now)

# Usage
limiter = RateLimiter(max_calls=10, time_window=60)  # 10 calls per minute

for item in items:
    limiter.wait_if_needed()
    result = call_api(item)
```

#### Pattern: Versioned Results Storage

```python
import json
from pathlib import Path
import datetime

class VersionedResults:
    """Store evaluation results with versioning."""

    def __init__(self, base_dir: str = "results"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)

    def save(self, results: dict, experiment_name: str):
        """Save results with timestamp."""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        version_dir = self.base_dir / experiment_name
        version_dir.mkdir(exist_ok=True)

        # Save with timestamp
        versioned_file = version_dir / f"{timestamp}.json"
        with open(versioned_file, 'w') as f:
            json.dump(results, f, indent=2)

        # Also save as "latest"
        latest_file = version_dir / "latest.json"
        with open(latest_file, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"Results saved: {versioned_file}")

    def load_latest(self, experiment_name: str):
        """Load most recent results."""
        latest_file = self.base_dir / experiment_name / "latest.json"
        with open(latest_file, 'r') as f:
            return json.load(f)

    def list_versions(self, experiment_name: str):
        """List all versions."""
        version_dir = self.base_dir / experiment_name
        return sorted(version_dir.glob("*.json"))

# Usage
results_store = VersionedResults()
results_store.save(metrics, "retrieval_v2")
latest = results_store.load_latest("retrieval_v2")
```

### 10.4 Common Pitfalls and Solutions

| Pitfall | Why It's Bad | Solution |
|---------|-------------|----------|
| **Small test set** | Low statistical power, unreliable metrics | Use 100+ examples minimum |
| **No train/test split** | Overfitting, inflated metrics | Always split data |
| **Imbalanced classes** | Misleading accuracy | Use TPR/TNR or F1 instead |
| **Testing on training data** | Overfitting, not representative | Strict train/test separation |
| **Ignoring edge cases** | Production failures | Explicitly test edge cases |
| **Manual evaluation at scale** | Doesn't scale, expensive | Use LLM-as-Judge with validation |
| **No confidence intervals** | Can't assess reliability | Always report CIs |
| **Single metric focus** | Incomplete picture | Track multiple metrics |
| **No failure analysis** | Can't improve systematically | Always analyze failures |
| **Forgetting to cache** | Wasted API calls, slow | Implement caching |

### 10.5 Further Reading

**Evaluation Methodology**
- "Holistic Evaluation of Language Models" (Liang et al., 2022)
- "Judging LLM-as-a-Judge" (Zheng et al., 2023)
- "How to Evaluate Your Chatbot" (Gao et al., 2020)

**Retrieval & RAG**
- "Okapi BM25" (Robertson & Zaragoza, 2009)
- "Retrieval-Augmented Generation" (Lewis et al., 2020)
- "Dense Passage Retrieval" (Karpukhin et al., 2020)

**Error Analysis**
- "Error Analysis in Natural Language Processing" (Smith, 2011)
- "Beyond Accuracy: Error Analysis" (Derczynski et al., 2016)

**Statistical Methods**
- "Practical Statistics for Data Scientists" (Bruce & Bruce, 2017)
- "Statistical Significance Testing" (Cohen, 1994)

### 10.6 Tool Recommendations

**LLM Libraries**
- **LiteLLM** - Multi-provider LLM calls
- **OpenAI Python SDK** - OpenAI models
- **Anthropic Python SDK** - Claude models

**Evaluation**
- **judgy** - LLM-as-Judge bias correction
- **ragas** - RAG evaluation metrics
- **phoenix** - LLM observability

**Retrieval**
- **rank-bm25** - BM25 implementation
- **chromadb** - Vector database
- **faiss** - Fast similarity search

**Utilities**
- **tqdm** - Progress bars
- **rich** - Beautiful terminal output
- **pandas** - Data manipulation
- **matplotlib/seaborn** - Visualization

### 10.7 Quick Reference: Evaluation Checklist

**Before Evaluation**
- [ ] Define success criteria clearly
- [ ] Create diverse test set (100+ examples)
- [ ] Split data (train/dev/test)
- [ ] Document evaluation protocol

**During Evaluation**
- [ ] Run on test set (never trained on)
- [ ] Calculate multiple metrics
- [ ] Analyze failure cases
- [ ] Document surprising results

**After Evaluation**
- [ ] Report metrics with confidence intervals
- [ ] Include failure mode analysis
- [ ] Document methodology
- [ ] Save all traces for reproducibility
- [ ] Version results

**For Production**
- [ ] Set up automated evaluation
- [ ] Monitor key metrics
- [ ] Alert on degradation
- [ ] Maintain trace collection
- [ ] Regular re-evaluation

---

## Conclusion

This guide has covered the complete journey of AI system evaluation:

1. **Foundation** - Why systematic evaluation matters
2. **Prompt Engineering** - Building effective system prompts
3. **Error Analysis** - Identifying failure modes systematically
4. **LLM-as-Judge** - Scaling evaluation with bias correction
5. **RAG Evaluation** - Measuring retrieval performance
6. **Agent Analysis** - Understanding complex failure patterns
7. **Advanced Topics** - Production-ready optimization techniques
8. **Best Practices** - Building maintainable evaluation systems

**Key Takeaways:**

✅ **Systematic beats ad-hoc** - Always use structured evaluation
✅ **Metrics matter** - Choose appropriate metrics for your use case
✅ **Failures are data** - Analyze failures to improve systematically
✅ **Scale with automation** - Use LLM-as-Judge when possible
✅ **Measure uncertainty** - Always report confidence intervals
✅ **Production thinking** - Design evaluation for continuous monitoring

**Your Next Steps:**

1. Complete the exercises in Section 9
2. Apply these techniques to your own AI systems
3. Build automated evaluation pipelines
4. Share learnings with your team
5. Contribute to the evaluation community

**Remember:** The goal isn't perfect evaluation—it's continuous improvement through systematic measurement.

---

**About This Guide**

This tutorial was created from the Recipe Chatbot AI Evaluations Course. For more resources:
- Course Repository: [github.com/ai-evals-course/recipe-chatbot](https://github.com/ai-evals-course/recipe-chatbot)
- Issues & Questions: Open an issue on GitHub
- Community: Join the discussion

**License:** Educational use encouraged. Attribution appreciated.

**Version:** 1.0 (2024)

---

*"You can't improve what you don't measure. You can't measure what you don't define. Start defining, start measuring, start improving."*
