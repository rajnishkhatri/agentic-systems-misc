# Failure Mode Taxonomy Tutorial

## Learning Objectives

By completing this tutorial, you will be able to:
- ✅ Write clear, testable failure mode definitions
- ✅ Create representative examples from real interaction traces
- ✅ Distinguish between observed and hypothetical failures
- ✅ Build multi-dimensional failure classifications
- ✅ Maintain taxonomy consistency across iterations
- ✅ Use taxonomies to guide system improvements

## Prerequisites

- Completed [Error Analysis Concepts Tutorial](error_analysis_concepts.md)
- Performed open coding and axial coding on your bot traces
- Have identified 3-5 potential failure mode categories

## Estimated Time

**Reading + Exercises:** 25-30 minutes

---

## Concepts

### What is a Failure Mode Taxonomy?

A **failure mode taxonomy** is a structured documentation system that:
- **Categorizes** different types of AI system failures
- **Defines** each failure mode with precision
- **Illustrates** with concrete examples
- **Guides** targeted improvements

Think of it as a "field guide" to your bot's failure patterns - a reference you can use to:
- Identify which failure mode a new trace exhibits
- Track failure frequency over time
- Design specific interventions for each mode
- Communicate patterns to team members

### Taxonomy vs. Bug List

**❌ Bug List (Unstructured):**
```
- Bot gave wrong recipe
- Missing information
- Didn't follow time constraint
- Response was weird
- Another wrong recipe
```

**Problems:**
- No organization
- Vague descriptions
- Hard to track patterns
- Not actionable

**✅ Failure Taxonomy (Structured):**
```
Failure Mode 1: Missing Serving Size Information
  Definition: Bot fails to specify number of servings...
  Examples: [2 concrete examples]

Failure Mode 2: Inconsistent Time Estimates
  Definition: Bot provides recipes exceeding user's time constraint...
  Examples: [2 concrete examples]
```

**Benefits:**
- Organized by category
- Clear definitions
- Concrete examples
- Actionable

---

## Anatomy of a Failure Mode

### The Three Essential Components

Every failure mode must include:

1. **Title** (3-7 words)
   - Short, descriptive name
   - Immediately communicates the failure type
   - Examples: "Missing Serving Size Information", "Overcomplicated Simple Recipes"

2. **Definition** (1-2 sentences)
   - Precisely describes when this failure occurs
   - Testable: You can determine if a trace matches
   - Avoids vague terms like "sometimes" or "wrong"

3. **Examples** (1-3 instances)
   - Concrete examples from actual traces
   - Shows exactly what the failure looks like
   - Includes both user query and bot response issue

### Example: Well-Structured Failure Mode

From [`failure_mode_taxonomy.md`](failure_mode_taxonomy.md):

---

**Failure Mode: Missing Serving Size Information**

*Definition:* Bot fails to specify the number of servings or portion sizes in the recipe.

*Illustrative Examples:*

1. *User Query:* "Quick egg spinach cheese recipe pls"
   *Bot Response:* Provides recipe with ingredients like "2 large eggs, 1 cup fresh spinach" without specifying how many people this serves.

2. *User Query:* "What's a simple recipe using salmon lemon and fresh herbs"
   *Bot Response:* Lists "2 salmon fillets" without indicating if this is for one or multiple servings.

3. *User Query (SYN001):* "need easy dairy free curry recipes"
   *Bot Response:* Provides "Easy Dairy-Free Chicken Curry" with "1 lb (450g) boneless, skinless chicken breasts or thighs" without specifying the number of servings.

---

**Analysis:**
- ✅ **Title:** Clear and specific ("Missing Serving Size Information")
- ✅ **Definition:** Testable (either serving size is present or not)
- ✅ **Examples:** Three concrete instances showing exactly what's missing
- ✅ **Variation:** Examples show different recipes (eggs, salmon, curry) demonstrating this is a pattern

---

## Writing Testable Definitions

### What Makes a Definition "Testable"?

A testable definition allows you (or another person) to **consistently determine** whether a new trace exhibits the failure mode.

**Key question:** "Can I check this programmatically or manually without ambiguity?"

### Examples: Bad vs. Good Definitions

#### Example 1: Information Completeness

❌ **Bad Definition:**
> "Bot doesn't give enough information"

**Problems:**
- What counts as "enough"?
- Subjective judgment required
- Can't reproduce analysis

✅ **Good Definition:**
> "Bot fails to specify the number of servings or portion sizes in the recipe."

**Why it works:**
- Specific: "number of servings or portion sizes"
- Objective: Either it's there or it isn't
- Reproducible: Anyone can check

#### Example 2: Time Constraints

❌ **Bad Definition:**
> "Bot sometimes gives recipes that take too long"

**Problems:**
- "Sometimes" is vague
- "Too long" is undefined
- No threshold specified

✅ **Good Definition:**
> "Bot provides recipes that don't match the requested time constraints or includes preparation time inaccurately."

**Why it works:**
- Specific: Compares actual time to requested time
- Contextual: Depends on user's explicit constraint
- Checkable: Can verify if time estimate aligns with request

#### Example 3: Complexity

❌ **Bad Definition:**
> "Bot makes things too complicated"

**Problems:**
- "Too complicated" for whom?
- What defines "complicated"?
- No objective measure

✅ **Good Definition:**
> "Bot provides recipes with too many ingredients or steps for what should be a simple dish, based on user's explicit simplicity request ('quick', 'simple', 'easy')."

**Why it works:**
- Relative to user intent ("quick", "simple")
- Two concrete measures: ingredient count, step count
- Contextual: Only applies when user requests simplicity

### Definition Writing Template

Use this template to ensure testability:

```
Bot [fails to | incorrectly | provides] [SPECIFIC ACTION]
[WHEN | IF] [SPECIFIC CONDITION].
```

**Examples:**

"Bot **fails to** specify number of servings **when** providing recipe responses."

"Bot **incorrectly** suggests non-vegan ingredients (honey, dairy) **when** user specifies vegan dietary restriction."

"Bot **provides** recipes with >30-minute cooking time **when** user requests 'quick' (<30 min) recipes."

---

## Creating Illustrative Examples

### The Anatomy of a Good Example

Each example should include:

1. **User Query** - Exact query text
2. **Bot Response Issue** - Specific description of what went wrong
3. **(Optional) Trace ID** - Reference to actual trace for verification

**Format:**

```markdown
*User Query:* "[exact query text]"
*Bot Response:* [Description of the problematic behavior]
```

Or with more detail:

```markdown
*User Query (TRACE_ID):* "[exact query text]"
*Bot Response:* [Summary of response]
*Issue:* [Specific failure description]
```

### Example: Recipe Bot Failure Mode

**Failure Mode: Inconsistent Time Estimates**

*Definition:* Bot provides recipes that don't match the requested time constraints or includes preparation time inaccurately.

*Illustrative Examples:*

1. *User Query:* "Whatcha got for a 30 min eggs and cheese dinner?"
   *Bot Response:* Suggests a recipe that requires toasting, cooking meat, and multiple steps that would likely exceed 30 minutes.
   *Issue:* No explicit time estimate provided, and steps suggest >30 minutes despite "30 min" request.

2. *User Query:* "quick salmon dinner ideas"
   *Bot Response:* Includes 10-15 minute marination time in a "quick" recipe.
   *Issue:* Marination time makes total time inconsistent with "quick" expectation.

3. *User Query (SYN018):* "Looking for quick salmon dinner ideas with lemon and herbs pls!"
   *Bot Response:* For "Lemon Herb Salmon," states it can be enjoyed in "about 20 minutes" but includes a step to "Let it marinate for at least 10 minutes," which, combined with prep and cooking time, could make the "quick" estimate misleading.
   *Issue:* Stated time (20 min) doesn't account for marination, making actual time ~30+ minutes.

**Analysis:**
- ✅ Three examples show the pattern across different scenarios
- ✅ Each example explains exactly what's inconsistent
- ✅ Examples vary (implicit time request, explicit time, stated estimate vs. actual)

### Observed vs. Hypothetical Examples

#### Observed Examples (Preferred)

**Definition:** Examples taken directly from your actual traces.

**When to use:** Always, when possible.

**Strengths:**
- Grounded in real behavior
- Verifiable (you can show the trace)
- More convincing to stakeholders

**Example:**
```markdown
*User Query (Trace T042):* "vegan dessert recipe"
*Bot Response:* Suggested recipe includes honey as sweetener.
*Issue:* Honey is not vegan, violates dietary restriction.
```

**Note:** You can reference the trace ID for verification.

#### Hypothetical Examples (When Needed)

**Definition:** Examples you construct to illustrate a plausible failure mode.

**When to use:**
- Failure mode is plausible but not yet observed in traces
- Need to illustrate an edge case
- Observed examples are unclear or complex

**Strengths:**
- Can clarify boundary conditions
- Useful for forward-looking taxonomy (anticipating failures)

**How to mark them:**

```markdown
*Hypothetical Example:*
*User Query:* "keto-friendly pasta dish"
*Expected Issue:* Bot might suggest traditional pasta (high-carb), violating keto constraint.
```

**Best Practice:** Use hypothetical examples sparingly, and mark them clearly as hypothetical.

### Example Diversity

Your examples should show:
- **Different queries** - Don't repeat the same query
- **Different bot responses** - Show variation in how the failure manifests
- **Different severities** - Some minor, some major instances

**❌ Poor Example Diversity:**
```markdown
1. *User Query:* "vegan recipe"
   *Issue:* Missing serving size

2. *User Query:* "vegetarian recipe"
   *Issue:* Missing serving size

3. *User Query:* "keto recipe"
   *Issue:* Missing serving size
```

**Problem:** All examples show the same pattern (missing serving size), just different dietary restrictions. Not diverse.

**✅ Good Example Diversity:**
```markdown
1. *User Query:* "vegan recipe"
   *Issue:* Missing serving size (0 servings specified)

2. *User Query:* "salmon dinner for guests"
   *Issue:* Lists "2 salmon fillets" without indicating if serves 2 or 4

3. *User Query (SYN001):* "easy dairy free curry recipes"
   *Issue:* Provides ingredients for unclear number of servings
```

**Why better:** Examples show different contexts (dietary, occasion, ingredient-based) and different manifestations (no mention, ambiguous quantity, unclear scaling).

---

## Multi-Dimensional Classification

### Why Multiple Failure Modes Per Trace?

**Important insight:** One trace can exhibit **multiple failure modes simultaneously**.

**Example Trace:**
```
Query: "quick vegan pasta under 15 minutes"

Response:
[Provides 20-ingredient recipe with butter and cream, estimated time: 45 minutes]
```

**Failure Modes Present:**
1. ✅ **Dietary Restriction Violation** - Butter and cream are not vegan
2. ✅ **Inconsistent Time Estimates** - 45 minutes exceeds "15 minutes" request
3. ✅ **Overcomplicated Recipes** - 20 ingredients for a "quick" dish

This is **normal and expected**. Failure modes describe **conceptual categories**, not mutually exclusive trace labels.

### How to Handle Multi-Dimensional Failures

#### In Your Taxonomy

**Write definitions independently:**

Each failure mode definition should be self-contained:

```markdown
Failure Mode 1: Dietary Restriction Violations
  Definition: Bot fails to properly address or verify dietary restrictions.
  [Examples...]

Failure Mode 2: Inconsistent Time Estimates
  Definition: Bot provides recipes exceeding user's time constraint.
  [Examples...]
```

**Don't reference other failures in definitions:**

❌ Avoid:
```
"Bot violates dietary restrictions and also doesn't match time constraints"
```

✅ Instead:
```
"Bot violates dietary restrictions" (one failure mode)
"Bot doesn't match time constraints" (separate failure mode)
```

#### In Your Spreadsheet Analysis

If using spreadsheet analysis ([`error_analysis_template.csv`](error_analysis_template.csv)):

| Trace_ID | Query | Dietary_Violation | Time_Inconsistent | Overcomplicated |
|----------|-------|-------------------|-------------------|-----------------|
| T001 | "quick vegan pasta <15min" | 1 | 1 | 1 |

**Interpretation:** Trace T001 exhibits all three failure modes.

This allows you to:
- Calculate individual failure mode frequencies
- Identify co-occurring failures (correlation analysis)
- Track each mode separately over time

---

## Taxonomy Maintenance

### Iterative Refinement

Your taxonomy is **not static**. As you:
- Test more queries
- Discover new failure patterns
- Implement fixes

You should **refine your taxonomy**.

### When to Add a New Failure Mode

Add a new failure mode when:
1. ✅ You observe a **pattern** (≥3 instances) that doesn't fit existing modes
2. ✅ The pattern represents a **distinct failure mechanism**
3. ✅ You can write a **testable definition**

**Example:**
```
After 50 more traces, you notice:
- Bot specifies equipment (non-stick pan, air fryer) without alternatives
- Appears in 8 traces
- Doesn't fit "Missing Information" (it's not missing, it's too specific)
```

**New Failure Mode:**
```markdown
Failure Mode: Missing Equipment Alternatives

Definition: Bot specifies necessary cooking equipment without suggesting alternatives if the user doesn't have the specific tool.

Examples:
1. *User Query:* "quick egg scramble"
   *Bot Response:* Specifies "non-stick skillet" without alternatives.

2. *User Query:* "crispy chicken wings"
   *Bot Response:* Requires "air fryer" without providing oven or stovetop alternative.
```

### When to Merge Failure Modes

Merge failure modes when:
1. ❌ Two modes have **significant overlap** (>70% of traces with Mode A also have Mode B)
2. ❌ Definitions are **too similar**
3. ❌ Same **root cause** and **same intervention**

**Example:**
```
Failure Mode 1: Missing Serving Size
Failure Mode 2: Missing Portion Information

These are essentially the same failure - merge them into:

Failure Mode: Missing Serving Size Information
  Definition: Bot fails to specify number of servings or portion sizes.
```

### When to Split a Failure Mode

Split a failure mode when:
1. ✅ The mode is **too broad** (covers many distinct failures)
2. ✅ Requires **different interventions** for different sub-types
3. ✅ Sub-types have **different frequencies or severities**

**Example:**
```
Original (Too Broad):
Failure Mode: Missing Information
  Definition: Bot fails to provide necessary recipe details.

Split into:
Failure Mode 1: Missing Serving Size Information
Failure Mode 2: Missing Time Estimates
Failure Mode 3: Missing Equipment Requirements
```

**Why split:** Each requires different prompt interventions and has different severity.

### Testing Definitions with New Traces

After defining your taxonomy, test it:

1. **Get new traces** (from additional queries or new model version)
2. **Apply taxonomy** - Determine which failure modes each trace exhibits
3. **Check inter-rater reliability** (if working with team):
   - Two people independently code same traces
   - Calculate agreement percentage
   - Refine definitions if agreement <80%

4. **Look for edge cases:**
   - Traces that don't fit any category → Potential new failure mode
   - Traces that fit multiple categories ambiguously → Definitions need refinement

---

## Practical Exercises

### Exercise 1: Critique Failure Mode Definitions

For each definition below, identify what's wrong and rewrite it:

**1. "Bot makes errors"**

**Problems:**
- [Your analysis]

**Rewrite:**
- [Your improved definition]

---

**2. "Bot sometimes doesn't include enough details in recipes"**

**Problems:**
- [Your analysis]

**Rewrite:**
- [Your improved definition]

---

**3. "Recipes are too complex for beginners occasionally"**

**Problems:**
- [Your analysis]

**Rewrite:**
- [Your improved definition]

### Exercise 2: Build a Failure Mode from Scratch

You've performed open coding and found these open codes appearing frequently:

- `ingredient_substitution_missing` (appears in 12/30 traces)
- `no_dairy_alternative` (appears in 5/30 traces)
- `no_gluten_free_option` (appears in 7/30 traces)
- `vague_substitution` ("use milk substitute" without specifying which)

**Task:** Create a failure mode following the template:

```markdown
Failure Mode: [Your Title]

Definition: [Your one-sentence definition]

Illustrative Examples:
1. *User Query:* [Example query]
   *Bot Response:* [What went wrong]

2. *User Query:* [Example query]
   *Bot Response:* [What went wrong]
```

### Exercise 3: Multi-Dimensional Classification

Given this trace:

```
User Query: "quick keto breakfast under 10 minutes"

Bot Response:
**Pancakes with Maple Syrup**

Fluffy pancakes perfect for weekend breakfast.

**Ingredients**
* 2 cups all-purpose flour
* 2 eggs
* 1.5 cups milk
* 1/4 cup sugar
* Maple syrup for serving

**Instructions**
1. Mix flour, eggs, milk, and sugar in bowl
2. Heat griddle to medium heat
3. Pour 1/4 cup batter per pancake
4. Cook until bubbles form, flip, cook 2 more minutes
5. Serve hot with maple syrup

**Estimated Time:** 25 minutes
```

**Task:** Using the failure modes from [`failure_mode_taxonomy.md`](failure_mode_taxonomy.md), identify which failure modes this trace exhibits. Explain why for each.

**Failure Modes to Consider:**
1. Missing Serving Size Information
2. Overcomplicated Simple Recipes
3. Inconsistent Time Estimates
4. Missing Dietary Restriction Information
5. Inadequate Safety Information

---

## Common Pitfalls

### 1. Definitions Too Broad

**❌ Problem:**
```markdown
Failure Mode: Recipe Errors
Definition: Bot makes mistakes in recipes.
```

**Why it's bad:**
- Doesn't specify *what* mistakes
- Not testable
- Not actionable

**✅ Solution:** Be specific
```markdown
Failure Mode: Incorrect Cooking Temperatures
Definition: Bot provides cooking temperatures that are unsafe or incorrect for the specified ingredient (e.g., undercooking chicken, overcooking vegetables).
```

### 2. Definitions Too Narrow

**❌ Problem:**
```markdown
Failure Mode: Missing Teaspoon Measurements for Salt
Definition: Bot doesn't specify teaspoon measurements when listing salt in ingredients.
```

**Why it's bad:**
- Too specific to be useful
- Won't generalize to other ingredients or measurements

**✅ Solution:** Broaden appropriately
```markdown
Failure Mode: Vague Ingredient Measurements
Definition: Bot provides ingredient quantities without specific measurements (e.g., "salt to taste", "some cheese", "a bit of oil").
```

### 3. Examples Without Context

**❌ Problem:**
```markdown
Example: Bot suggested honey.
```

**Why it's bad:**
- No user query
- No explanation of why this is a problem
- Can't reproduce or verify

**✅ Solution:** Full context
```markdown
Example:
*User Query:* "vegan dessert recipe"
*Bot Response:* Suggested recipe uses honey as sweetener.
*Issue:* Honey is not vegan, violates dietary restriction.
```

### 4. Hypothetical-Only Examples

**❌ Problem:**
```markdown
All 3 examples start with: "If a user asked..."
```

**Why it's bad:**
- Not grounded in actual behavior
- Less convincing
- Might not reflect real failures

**✅ Solution:** Use observed examples when possible
```markdown
Example 1: [Real trace T042]
Example 2: [Real trace T058]
Example 3 (Hypothetical): "If a user asked for..."
```

Mark hypothetical examples clearly, use sparingly.

### 5. Overlapping Failure Modes

**❌ Problem:**
```markdown
Failure Mode 1: Incomplete Recipes
  Definition: Bot doesn't provide all necessary information.

Failure Mode 2: Missing Information
  Definition: Bot fails to include important details.
```

**Why it's bad:**
- Essentially the same failure mode
- Causes confusion in classification
- Dilutes taxonomy

**✅ Solution:** Merge or clarify distinction
```markdown
Failure Mode: Missing Recipe Information
  Definition: Bot fails to provide essential recipe details (serving size, cooking time, equipment, or safety information).

  Sub-categories:
  - Missing serving size
  - Missing time estimates
  - Missing equipment requirements
  - Missing safety information
```

Or split into distinct, non-overlapping modes if they have different interventions.

---

## Using Taxonomies to Guide Improvements

### From Taxonomy to Prompt Engineering

Once you have a clear taxonomy, use it to **update your system prompt**.

**Example:**

**Failure Mode:** Missing Serving Size Information (70% of traces)

**Prompt Intervention:**
```python
SYSTEM_PROMPT = """
You are an expert chef recommending delicious recipes.

IMPORTANT: Always include serving size information at the beginning of each recipe.
Use format: "Serves [number]" or "Makes [number] [units]" (e.g., "Serves 4", "Makes 12 cookies").
If serving size isn't specified in the query, assume 2 servings.
"""
```

**Failure Mode:** Dietary Restriction Violations (15% of traces, but high severity)

**Prompt Intervention:**
```python
SYSTEM_PROMPT = """
...
DIETARY RESTRICTIONS:
- If user specifies dietary restrictions (vegan, gluten-free, keto, etc.), verify ALL ingredients comply.
- Common violations to avoid:
  - Vegan: No honey, dairy, eggs, gelatin
  - Gluten-free: No wheat, barley, rye
  - Keto: No high-carb ingredients (pasta, bread, sugar)
- When in doubt, provide ingredient substitutions or alternatives.
"""
```

### From Taxonomy to Validation Logic

Some failure modes require **post-processing or validation**, not just prompt engineering.

**Example:**

**Failure Mode:** Inconsistent Time Estimates

**Validation Code:**
```python
def validate_time_consistency(query: str, response: str) -> bool:
    """Check if response time matches query time constraint."""

    # Extract time constraint from query
    if "quick" in query.lower() or "<15" in query or "under 15" in query.lower():
        max_time = 15
    elif "30 min" in query.lower():
        max_time = 30
    else:
        return True  # No explicit time constraint

    # Extract stated time from response
    import re
    time_match = re.search(r'(\d+)\s*min', response.lower())

    if time_match:
        stated_time = int(time_match.group(1))
        if stated_time > max_time:
            return False  # Inconsistent

    return True  # Consistent or no time found
```

### From Taxonomy to Automated Evaluation (Preview)

In **HW3**, you'll learn to use **LLM-as-Judge** to automatically detect failure modes at scale.

**Example Judge Prompt:**

```python
JUDGE_PROMPT = """
Given a user query and bot response, determine if the response exhibits the failure mode:
"Missing Serving Size Information".

Failure Mode Definition: Bot fails to specify the number of servings or portion sizes in the recipe.

User Query: {query}
Bot Response: {response}

Does this response exhibit the failure mode? (YES/NO)
Reasoning: [Explain why]
"""
```

This allows you to test 1000s of traces and track failure mode frequencies over time.

---

## Key Takeaways

- ✅ **Taxonomies organize failures** - Structured categorization beats unstructured bug lists
- ✅ **Three components required** - Title, Definition, Examples for each failure mode
- ✅ **Testable definitions are critical** - You must be able to check if a trace matches
- ✅ **Use observed examples** - Grounded in real traces when possible
- ✅ **Multi-dimensional classification is normal** - One trace can have multiple failures
- ✅ **Iterate and refine** - Taxonomies evolve as you discover new patterns
- ✅ **Taxonomies guide action** - Each mode should suggest specific interventions

---

## Further Reading

### Related Tutorials
- [Error Analysis Concepts](error_analysis_concepts.md) - Open and axial coding methodology
- [Dimension Generation Tutorial](dimension_generation_tutorial.ipynb) - Generate targeted test queries
- [HW3: LLM-as-Judge Development](../hw3/judge_development_tutorial.ipynb) - Automate failure detection

### Reference Materials
- [failure_mode_taxonomy.md](failure_mode_taxonomy.md) - Complete example taxonomy with 8 failure modes
- [error_analysis_template.csv](error_analysis_template.csv) - Spreadsheet template for tracking failures
- [AI Evaluation Complete Guide](../../AI_EVALUATION_COMPLETE_GUIDE.md) - Section 3.3: Axial Coding & Taxonomies

### Methodological Background
- **Failure Mode and Effects Analysis (FMEA)** - Engineering approach to failure classification
- **Grounded Theory** - Qualitative research methodology (Glaser & Strauss, 1967)
- **Root Cause Analysis** - Systematic failure investigation techniques

---

**Tutorial Status:** ✅ Complete
**Last Updated:** 2025-10-29
**Maintainer:** AI Evaluation Course Team
