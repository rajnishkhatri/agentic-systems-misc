# Error Analysis Concepts Tutorial

## Learning Objectives

By completing this tutorial, you will be able to:
- ✅ Understand qualitative vs. quantitative evaluation and when to use each
- ✅ Apply open coding methodology to identify patterns in AI system failures
- ✅ Perform axial coding to group observations into structured failure modes
- ✅ Build comprehensive failure mode taxonomies with clear definitions
- ✅ Know when to use error analysis vs. automated metrics
- ✅ Document failure patterns systematically for reproducible analysis

## Prerequisites

- Completed [HW1: System Prompt Engineering](../hw1/system_prompt_engineering_tutorial.md)
- Have collected diverse bot test results (from running [bulk_test.py](../../scripts/bulk_test.py))
- Basic understanding of your AI system's expected behavior

## Estimated Time

**Reading Time:** 25-30 minutes
**Hands-on Practice:** 30-45 minutes (if performing coding on your traces)

---

## Concepts

### Why Error Analysis Matters

After writing a good system prompt (HW1) and testing with diverse queries, you'll discover your AI system **still fails in unexpected ways**. This is normal and expected.

**The problem with informal evaluation:**
- 👀 "Hmm, this response looks wrong" → Not systematic
- 🤷 "I think it's working better now" → Not measurable
- 🔄 "Let me try a different prompt" → No understanding of *why* failures occur

**Error analysis provides:**
- 🔍 **Systematic failure identification** - Find patterns, not just isolated bugs
- 📊 **Categorization and taxonomy** - Organize failures into actionable categories
- 📝 **Documentation** - Reproducible analysis you can share and iterate on
- 🎯 **Prioritization** - Focus on high-frequency, high-impact failures

### Qualitative vs. Quantitative Evaluation

| Aspect | Qualitative Evaluation | Quantitative Evaluation |
|--------|------------------------|-------------------------|
| **Data** | Text descriptions, observations, notes | Numbers, metrics, percentages |
| **Focus** | Understanding *why* failures happen | Measuring *how often* failures happen |
| **Methods** | Open coding, axial coding, taxonomy building | Accuracy, F1-score, TPR/TNR, pass rates |
| **Output** | Failure taxonomies, patterns, insights | Statistical metrics, confidence intervals |
| **When to use** | Early exploration, unknown failure modes | After identifying failure modes, tracking improvements |
| **Example** | "Bot over-complicates simple recipes" | "32% of 'quick' queries result in >30-minute recipes" |

**Key Insight:** Start with **qualitative** (HW2) to understand failures, then move to **quantitative** (HW3+) to measure them at scale.

---

## The Error Analysis Process

### Overview

```
┌─────────────────────────────────────────────────────────┐
│           ERROR ANALYSIS WORKFLOW                       │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1. COLLECT TRACES                                      │
│     ↓                                                   │
│     Run bot on diverse queries (20-50+ traces)          │
│     Record full interactions                            │
│                                                         │
│  2. OPEN CODING (Exploratory)                           │
│     ↓                                                   │
│     Review traces without preconceived categories       │
│     Assign descriptive labels to observations           │
│     Note patterns, oddities, failures                   │
│                                                         │
│  3. AXIAL CODING (Organizational)                       │
│     ↓                                                   │
│     Group similar open codes together                   │
│     Create hierarchical categories                      │
│     Define broader failure modes                        │
│                                                         │
│  4. BUILD TAXONOMY                                      │
│     ↓                                                   │
│     Write formal failure mode definitions               │
│     Add 1-2 illustrative examples per mode              │
│     Document in structured format                       │
│                                                         │
│  5. (OPTIONAL) SPREADSHEET ANALYSIS                     │
│     ↓                                                   │
│     Track which traces exhibit which failures           │
│     Calculate frequency of each failure mode            │
│     Identify co-occurring failures                      │
│                                                         │
│  6. FROM TAXONOMY TO ACTION                             │
│     ↓                                                   │
│     Prioritize by frequency and severity                │
│     Design interventions (prompt updates, guardrails)   │
│     Re-test and measure improvement                     │
└─────────────────────────────────────────────────────────┘
```

---

## Open Coding Methodology

### What is Open Coding?

**Open coding** is an exploratory analysis technique where you:
- Review interaction traces **without preconceived categories**
- Assign **descriptive labels/notes** to interesting patterns
- Identify potential errors, oddities, or areas for improvement
- Avoid forcing observations into predetermined buckets

**Origin:** Borrowed from **Grounded Theory** (qualitative research methodology by Glaser & Strauss, 1967)

**Key Principle:** Let the patterns emerge from the data, rather than imposing structure upfront.

### The Open Coding Process (4 Steps)

#### Step 1: Collect Traces

Run your bot on a diverse set of queries and record:
- User query (input)
- Bot response (output)
- Any intermediate steps (tool calls, retrieval results, etc.)
- Context (timestamp, model version, etc.)

**How many traces?** Start with 20-50. Look for **saturation** - the point where you stop seeing new patterns.

**How to collect:**
```bash
# Run bulk test on your queries
python scripts/bulk_test.py

# Results saved to outputs/ directory with:
# - query_id
# - query
# - bot_response
# - timestamp
```

Or use existing sample: [`results_20250518_215844.csv`](results_20250518_215844.csv)

#### Step 2: Initial Review

Read through each trace carefully:
- Don't judge or categorize yet
- Just observe what's happening
- Note anything that stands out (good or bad)
- Ask: "What is the bot doing here?"

**Mindset:** Be curious, not critical. You're exploring, not evaluating.

#### Step 3: Descriptive Labeling

For each trace, write **descriptive labels** (open codes) capturing observations:

**Example Trace:**
```
Query: "Quick egg spinach cheese recipe pls"

Response:
**Creamy Egg, Spinach, and Cheese Scramble**

A simple and satisfying scramble combining eggs, spinach, and cheese.

**Ingredients**
* 2 large eggs
* 1 cup fresh spinach (roughly chopped)
* Shredded cheese (amount to taste)
* Salt and pepper (to taste)
* Optional: a pinch of garlic powder or red pepper flakes

**Instructions**
1. Heat a non-stick skillet over medium heat
2. Add spinach and cook until wilted (about 2-3 minutes)
3. Crack eggs into bowl, whisk with salt and pepper
4. Add eggs to skillet, scramble gently
5. When eggs are nearly set, add shredded cheese
6. Continue cooking until cheese melts and eggs are fully cooked
7. Optionally season with garlic powder or red pepper flakes

**Tips**
Ensure the pan is hot but not smoking to prevent sticking
You can add a small amount of butter or oil if preferred
```

**Open Codes (Observations):**
- `no_serving_size` → Doesn't specify how many people this serves
- `vague_measurement` → "Shredded cheese (amount to taste)" - no quantity
- `optional_complexity` → Suggests optional ingredients (garlic powder, red pepper flakes) for a "quick" recipe
- `missing_cooking_time` → No total time estimate provided (user asked for "quick")
- `non_stick_assumption` → Specifies "non-stick skillet" without alternatives
- `good_structure` → [Positive note] Clear Markdown formatting with sections
- `step_by_step_clear` → [Positive note] Instructions are easy to follow

**Notice:**
- Labels are **descriptive**, not judgmental ("vague_measurement" vs. "bad ingredient list")
- Both **failures and successes** are noted
- Labels are **specific** ("no_serving_size" vs. "incomplete")

#### Step 4: Pattern Identification

After coding 10-20 traces, review your open codes:
- Which codes appear repeatedly?
- Are there themes or categories emerging?
- Which patterns seem most problematic?

**Example Pattern Recognition:**

Across 20 traces, you might see:
- `no_serving_size` appears in **14 traces** (70%)
- `vague_measurement` appears in **8 traces** (40%)
- `missing_cooking_time` appears in **12 traces** (60%)
- `optional_complexity` appears in **6 traces** (30%)

**Insight:** Serving size and time estimates are frequently missing → These are high-priority failures.

### Open Coding in Practice

**Visual Example:**

See the open coding process in action with spreadsheet analysis:

![Open Coding Dashboard](imgs/open_coding_dashboard.png)

This shows traces with multiple open codes assigned, allowing pattern identification across the dataset.

![Open Coding Notes](imgs/open_coding_notes.png)

Example of detailed notes taken during open coding, capturing observations in free-form text before formal categorization.

---

## Axial Coding: Building Taxonomies

### What is Axial Coding?

**Axial coding** takes your open codes and organizes them into **structured failure mode taxonomies**.

**Goal:** Group related observations into broader categories that:
- Are **mutually exclusive** (a failure fits in one category, not multiple)
- Are **collectively exhaustive** (cover all observed failures)
- Have **clear definitions** (you can determine if a new trace matches)

### From Open Codes to Failure Modes

#### Example: Grouping Open Codes

**Open codes observed:**
- `no_serving_size`
- `missing_cooking_time`
- `vague_measurement` ("cheese to taste", no quantity)
- `no_prep_time_breakdown`

**Axial grouping:**
These all relate to **missing or incomplete information** → Failure Mode: **"Missing Recipe Information"**

**Another set of open codes:**
- `optional_complexity` (suggests optional ingredients for "quick" recipes)
- `too_many_steps` (15-step recipe for "simple" request)
- `advanced_technique` (suggests sous vide for "beginner" query)

**Axial grouping:**
These relate to **recipes that don't match the user's skill/time constraints** → Failure Mode: **"Overcomplicated Recipes"**

### Taxonomy Structure

Each failure mode in your taxonomy should include:

1. **Title** - Short, descriptive name (3-7 words)
2. **Definition** - One-sentence explanation of when this failure occurs
3. **Examples** - 1-2 concrete instances from your traces (real or hypothetical)

**Template:**
```markdown
## Failure Mode: [Title]

**Definition:** [One sentence describing the failure condition]

**Illustrative Examples:**
1. *User Query*: "[query text]"
   *Bot Response Issue*: [Description of what went wrong]

2. *User Query*: "[query text]"
   *Bot Response Issue*: [Description of what went wrong]
```

### Example: Recipe Bot Failure Taxonomy

See the complete worked example in [`failure_mode_taxonomy.md`](failure_mode_taxonomy.md). Here are two failure modes for reference:

---

#### Failure Mode 1: Missing Serving Size Information

**Definition:** Bot fails to specify the number of servings or portion sizes in the recipe.

**Illustrative Examples:**
1. *User Query*: "Quick egg spinach cheese recipe pls"
   *Bot Response Issue*: Provides recipe with "2 large eggs, 1 cup fresh spinach" without specifying how many people this serves.

2. *User Query*: "What's a simple recipe using salmon lemon and fresh herbs"
   *Bot Response Issue*: Lists "2 salmon fillets" without indicating if this is for one or multiple servings.

---

#### Failure Mode 2: Overcomplicated Simple Recipes

**Definition:** Bot provides recipes with too many ingredients or steps for what should be a simple dish.

**Illustrative Examples:**
1. *User Query*: "quick egg spinach cheese recipe pls"
   *Bot Response Issue*: Includes optional ingredients like garlic powder, red pepper flakes, and multiple preparation steps that could be simplified for a "quick" request.

2. *User Query*: "simple recipe using salmon lemon and fresh herbs"
   *Bot Response Issue*: Provides complex marinade preparation and multiple cooking methods (baking and pan-frying) when a simpler approach would suffice for a "simple" request.

---

### Building Your Taxonomy

**Process:**

1. **Review all open codes** from your traces
2. **Group similar codes** into 3-5 broad categories
3. **Name each category** with a clear, descriptive title
4. **Write a one-sentence definition** for each
5. **Select 1-2 examples** from your traces that best illustrate the failure
6. **Test definitions** by checking if new traces clearly fit or don't fit

**How many failure modes?**
- **Too few (<3):** Likely too broad, not actionable
- **Too many (>10):** Dilutes focus, hard to track
- **Sweet spot (3-8):** Specific enough to act on, manageable to track

---

## Taxonomy Writing Best Practices

### Writing Clear Definitions

**❌ Bad Definition:**
> "Bot makes mistakes with recipes"

**Problems:**
- Too vague
- Not testable (what counts as a "mistake"?)
- No clear boundary

**✅ Good Definition:**
> "Bot fails to specify the number of servings or portion sizes in the recipe."

**Why it works:**
- Specific: "number of servings or portion sizes"
- Testable: You can check if serving size is present
- Clear boundary: Either it's there or it isn't

### Creating Illustrative Examples

**Two types of examples:**

1. **Observed Examples** - Actual failures from your traces
   - **When to use:** You have a clear instance in your test data
   - **Strength:** Grounded in real behavior

2. **Hypothetical Examples** - Plausible scenarios you construct
   - **When to use:** Failure mode is plausible but not directly observed
   - **Strength:** Can illustrate edge cases

**Best practice:** Use **observed examples** when possible, hypothetical when necessary to clarify the failure mode.

### Multi-Dimensional Classification

**Important:** One trace can exhibit **multiple failure modes** simultaneously.

**Example Trace:**
```
Query: "quick low FODMAP recipe"
Response: [15-ingredient recipe that takes 45 minutes and includes garlic and onions]
```

**Failure modes present:**
1. ✅ **Inconsistent Time Estimates** (45 minutes for "quick")
2. ✅ **Missing Dietary Restriction Verification** (garlic and onions are high FODMAP)
3. ✅ **Overcomplicated Simple Recipes** (15 ingredients)

This is normal and expected. Failure modes are **not mutually exclusive** at the trace level, only at the conceptual level.

---

## Optional: Spreadsheet Analysis

### Why Use a Spreadsheet?

Spreadsheets help you:
- Track which traces have which failures
- Calculate failure mode frequencies
- Identify co-occurring failures
- Prioritize improvement efforts

### Spreadsheet Structure

Use the template: [`error_analysis_template.csv`](error_analysis_template.csv)

**Columns:**

| Column Name | Purpose | Example |
|-------------|---------|---------|
| `Trace_ID` | Unique identifier | T001, T002, T003 |
| `User_Query` | Original query | "quick vegan breakfast" |
| `Bot_Response_Summary` | Brief summary | "Scramble with tofu, no time estimate" |
| `Open_Code_Notes` | Your observations | "missing_time, vague_serving_size" |
| `Failure_Mode_1` | Binary (0 or 1) | 1 (if "Missing Serving Size" present) |
| `Failure_Mode_2` | Binary (0 or 1) | 0 |
| `Failure_Mode_3` | Binary (0 or 1) | 1 (if "Missing Time" present) |
| ... | Additional failure modes | ... |

**Example Row:**
```csv
Trace_ID,User_Query,Bot_Response_Summary,Open_Code_Notes,Missing_Serving,Overcomplicated,Time_Inconsistent,Dietary_Violation
T001,"quick egg recipe","Scramble with optional extras","no serving size; too many optional ingredients",1,1,0,0
T002,"vegan breakfast","Tofu scramble, honey suggested","includes honey (not vegan)",1,0,0,1
T003,"30-min salmon dinner","45-min recipe with marinade","exceeds time constraint",0,0,1,0
```

### Analyzing Frequency

After coding all traces, calculate:

```python
import pandas as pd

df = pd.read_csv('error_analysis.csv')

# Failure mode frequencies
frequencies = {
    'Missing_Serving': df['Missing_Serving'].sum(),
    'Overcomplicated': df['Overcomplicated'].sum(),
    'Time_Inconsistent': df['Time_Inconsistent'].sum(),
    'Dietary_Violation': df['Dietary_Violation'].sum(),
}

# Percentages
total_traces = len(df)
for mode, count in frequencies.items():
    print(f"{mode}: {count}/{total_traces} ({100*count/total_traces:.1f}%)")
```

**Output:**
```
Missing_Serving: 14/20 (70.0%)
Overcomplicated: 6/20 (30.0%)
Time_Inconsistent: 12/20 (60.0%)
Dietary_Violation: 3/20 (15.0%)
```

**Insight:** "Missing Serving Size" and "Time Inconsistent" are highest priority (affect >60% of traces).

### Co-Occurrence Analysis

Identify which failures tend to appear together:

```python
# Which failures co-occur?
df[['Missing_Serving', 'Overcomplicated', 'Time_Inconsistent']].corr()
```

**Insight:** If "Overcomplicated" and "Time_Inconsistent" have high correlation (e.g., 0.8), fixing one might help the other.

---

## Common Pitfalls

### Open Coding Pitfalls

#### 1. Premature Categorization
**❌ Problem:** Forcing observations into predefined buckets before exploring

**Example:**
- You start with categories: "Formatting Errors", "Content Errors", "Logic Errors"
- You try to fit every observation into these buckets
- You miss patterns that don't fit (e.g., "Tone inconsistencies")

**✅ Solution:** Start with **no categories**. Let patterns emerge naturally from open codes.

#### 2. Insufficient Detail
**❌ Problem:** Notes like "bad response" or "wrong" aren't actionable

**Example:**
- Open code: `bad_response`
- What's bad about it? Missing information? Incorrect facts? Poor formatting?

**✅ Solution:** Be specific: `no_serving_size`, `incorrect_cooking_temp`, `missing_markdown_headers`

#### 3. Confirmation Bias
**❌ Problem:** Only noting failures, missing successful patterns

**Example:**
- You only code: `missing_time`, `vague_ingredients`, `no_serving`
- You ignore: `good_structure`, `clear_instructions`, `helpful_tips`

**✅ Solution:** Note both **failures and successes**. Successes show what's working and shouldn't be changed.

#### 4. Inconsistent Granularity
**❌ Problem:** Some codes are too specific, others too vague

**Example:**
- `missing_teaspoon_measurement_for_salt` ← Too specific
- `bad_ingredients` ← Too vague
- `no_serving_size` ← Just right

**✅ Solution:** Aim for **medium granularity** - specific enough to be useful, broad enough to apply to multiple traces.

### Axial Coding Pitfalls

#### 1. Overlapping Categories
**❌ Problem:** Failure modes aren't mutually exclusive (at conceptual level)

**Example:**
- Failure Mode 1: "Missing Information"
- Failure Mode 2: "Incomplete Recipes"
- These overlap significantly

**✅ Solution:** Ensure categories are **conceptually distinct**. "Missing Information" could include "Missing Serving Size", "Missing Time", "Missing Equipment".

#### 2. Too Broad
**❌ Problem:** Categories are so broad they're not actionable

**Example:**
- Failure Mode: "Bot makes errors"
- What kind of errors? How to fix?

**✅ Solution:** Be specific enough to **design targeted interventions**.

#### 3. Too Narrow
**❌ Problem:** Having 20+ failure modes dilutes focus

**Example:**
- Failure Mode 1: "Missing serving size"
- Failure Mode 2: "Missing prep time"
- Failure Mode 3: "Missing cook time"
- Failure Mode 4: "Missing total time"
- ... (too many)

**✅ Solution:** Group related failures: "Missing Time Information" (covers prep, cook, total).

#### 4. Missing Hierarchy
**❌ Problem:** No organization of related failure modes

**Example:**
- Flat list of 10 failure modes with no grouping

**✅ Solution:** Create **hierarchical taxonomy**:

```
Category: Information Completeness
  ├─ Missing Serving Size
  ├─ Missing Time Estimates
  └─ Vague Measurements

Category: User Intent Alignment
  ├─ Overcomplicated Recipes
  ├─ Inconsistent Time Constraints
  └─ Missing Dietary Verification
```

### Taxonomy Writing Pitfalls

#### 1. Vague Definitions
**❌ Problem:** Can't determine if a new trace matches the failure mode

**Example:**
- Definition: "Bot sometimes gives wrong answers"
- When is an answer "wrong"? How do you test this?

**✅ Solution:** **Testable definitions**:
- "Bot provides recipes that exceed the user's specified time constraint by >50%"

#### 2. No Examples
**❌ Problem:** Definitions without concrete instances

**Example:**
- Failure Mode: "Dietary Restriction Violations"
- Definition: "Bot fails to respect dietary constraints"
- Examples: [none provided]

**✅ Solution:** Always include **1-2 examples** showing exactly what the failure looks like.

#### 3. Hypothetical-Only Examples
**❌ Problem:** All examples are made up, not grounded in actual traces

**Example:**
- All examples start with "If a user asked..." or "The bot might..."

**✅ Solution:** Use **observed examples** from your traces whenever possible. Hypothetical examples are OK for edge cases not yet observed.

#### 4. Untestable Definitions
**❌ Problem:** Can't programmatically or manually check if failure is present

**Example:**
- "Bot doesn't seem helpful enough"
- How do you measure "helpfulness"?

**✅ Solution:** Make definitions **concrete and checkable**:
- "Bot provides recipes without ingredient substitutions when dietary restrictions are specified"

---

## From Taxonomy to Action

### Prioritization

After building your taxonomy, prioritize failures by:

1. **Frequency** - How often does this happen?
   - Use spreadsheet analysis to calculate percentages

2. **Severity** - How bad is this failure?
   - **Critical**: Safety issues, completely wrong responses
   - **High**: Major user frustration (dietary violations, time misestimates)
   - **Medium**: Inconvenient but not broken (missing serving size)
   - **Low**: Nice-to-have improvements (formatting inconsistencies)

3. **Effort to Fix** - How hard is this to solve?
   - **Easy**: Update system prompt (add "always include serving size")
   - **Medium**: Add validation logic or guardrails
   - **Hard**: Requires retrieval, external tools, or model fine-tuning

**Prioritization Matrix:**

| Failure Mode | Frequency | Severity | Effort | Priority |
|--------------|-----------|----------|--------|----------|
| Missing Serving Size | 70% | Medium | Easy | **High** |
| Time Inconsistent | 60% | High | Medium | **High** |
| Dietary Violation | 15% | Critical | Hard | **High** |
| Overcomplicated | 30% | Low | Easy | Medium |

**Action:** Focus on high-priority failures first.

### Designing Interventions

For each high-priority failure, brainstorm interventions:

**Failure Mode:** Missing Serving Size

**Possible Interventions:**
1. **Update system prompt:**
   ```python
   "Always include serving size (e.g., 'Serves 2') at the beginning of each recipe."
   ```

2. **Add validation:**
   ```python
   def validate_response(response):
       if "Serves" not in response and "servings" not in response:
           return "ERROR: Missing serving size"
   ```

3. **Post-processing:**
   ```python
   if "Serves" not in response:
       response = f"Serves 2\n\n{response}"
   ```

**Failure Mode:** Dietary Restriction Violations

**Possible Interventions:**
1. **Update system prompt:**
   ```python
   "If user specifies dietary restrictions (vegan, gluten-free, etc.),
   verify ALL ingredients comply. Never suggest honey for vegan recipes."
   ```

2. **Add retrieval (RAG):**
   - Retrieve dietary restriction guidelines
   - Check ingredients against restrictions before responding

3. **Use LLM-as-Judge (HW3):**
   - Automated verification of dietary compliance

### Measuring Improvement

After implementing interventions:

1. **Re-run tests** on the same query set
2. **Re-code traces** with your taxonomy
3. **Calculate new failure rates**
4. **Compare before/after**

**Example:**

| Failure Mode | Before | After | Improvement |
|--------------|--------|-------|-------------|
| Missing Serving Size | 70% | 5% | **-65%** ✅ |
| Time Inconsistent | 60% | 48% | **-12%** ⚠️ |
| Dietary Violation | 15% | 15% | **0%** ❌ |

**Insights:**
- ✅ Serving size intervention worked!
- ⚠️ Time intervention helped but needs more work
- ❌ Dietary violation intervention didn't work - need different approach

---

## Key Takeaways

- ✅ **Error analysis is systematic** - Use open and axial coding for reproducible analysis
- ✅ **Start qualitative, then quantitative** - Understand failures (HW2) before measuring at scale (HW3+)
- ✅ **Open coding is exploratory** - No preconceived categories, let patterns emerge
- ✅ **Axial coding organizes** - Group open codes into structured failure modes
- ✅ **Taxonomies are actionable** - Each mode should suggest clear interventions
- ✅ **Prioritize strategically** - Frequency × Severity ÷ Effort to fix
- ✅ **Measure improvement** - Re-test after interventions to validate fixes

---

## Further Reading

### Related Tutorials
- [Failure Mode Taxonomy Tutorial](failure_mode_taxonomy_tutorial.md) - Detailed taxonomy writing guide
- [Dimension Generation Tutorial](dimension_generation_tutorial.ipynb) - Generate systematic test queries
- [HW3: LLM-as-Judge Concepts](../hw3/llm_judge_concepts.md) - Scale up evaluation with automation

### Methodological Background
- **Grounded Theory** - Glaser & Strauss (1967), foundation of open/axial coding
- **Qualitative Data Analysis** - Miles & Huberman (1994), systematic analysis techniques
- **Failure Mode and Effects Analysis (FMEA)** - Engineering approach to failure classification

### Course Materials
- [AI Evaluation Complete Guide](../../AI_EVALUATION_COMPLETE_GUIDE.md) - Section 3: Error Analysis & Failure Taxonomies
- [HW2 Assignment README](README.md) - Full homework instructions
- [HW2 Walkthrough Video](https://youtu.be/h9oAAAYnGx4) - Code walkthrough
- [Open & Axial Coding Video](https://youtu.be/AKg27L4E0M8) - Methodology walkthrough

### Code References
- [failure_mode_taxonomy.md](failure_mode_taxonomy.md) - Example taxonomy with 8 failure modes
- [error_analysis_template.csv](error_analysis_template.csv) - Spreadsheet template
- [results_20250518_215844.csv](results_20250518_215844.csv) - Sample bot traces for analysis

---

**Tutorial Status:** ✅ Complete
**Last Updated:** 2025-10-29
**Maintainer:** AI Evaluation Course Team
