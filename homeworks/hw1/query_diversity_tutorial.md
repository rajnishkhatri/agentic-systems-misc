# Query Diversity Tutorial

## Learning Objectives

By completing this tutorial, you will be able to:
- ✅ Identify key dimensions that define the space of possible user queries
- ✅ Create dimension value matrices for systematic coverage
- ✅ Ensure balanced query coverage across all dimensions
- ✅ Detect and test edge cases and boundary conditions
- ✅ Avoid bias in query selection
- ✅ Evaluate coverage gaps in your test query set

## Prerequisites

- Basic understanding of your AI system's domain (e.g., recipe recommendations)
- Completed [System Prompt Engineering Tutorial](system_prompt_engineering_tutorial.md) (recommended)
- Familiarity with the homework assignment context

## Estimated Time

**Reading + Exercises:** 20-25 minutes

---

## Concepts

### What Are Query Dimensions?

**Query dimensions** are the key variables that define the space of possible user inputs to your AI system. They represent the different ways users can vary their requests.

For a recipe chatbot, dimensions might include:
- **Cuisine Type:** Italian, Thai, Mexican, Indian, French, Japanese
- **Dietary Restriction:** Vegan, vegetarian, gluten-free, keto, paleo, no restrictions
- **Meal Type:** Breakfast, lunch, dinner, snack, dessert, appetizer
- **Cooking Time:** <15 min, 15-30 min, 30-60 min, >60 min
- **Skill Level:** Beginner, intermediate, advanced
- **Available Ingredients:** Specific items the user has on hand

### Why Systematic Query Design Matters

**Without systematic query design:**
- ❌ **Blind spots** - You miss entire categories of user requests
- ❌ **Dimension bias** - Over-test one type of query (e.g., only dinner recipes)
- ❌ **No edge case coverage** - Conflicting or ambiguous queries aren't tested
- ❌ **False confidence** - Bot seems to work, but only on "happy path" queries

**With systematic query design:**
- ✅ **Complete coverage** - Test all meaningful combinations of dimensions
- ✅ **Balanced testing** - Equal representation across dimension values
- ✅ **Edge case discovery** - Intentionally test boundary conditions
- ✅ **Reproducible evaluation** - Can regenerate test sets systematically

### The Curse of Dimensionality

If you have 5 dimensions with 5 values each, that's **5^5 = 3,125 possible combinations**. You can't test all of them, so you need a strategy to select a representative subset.

**Key Insight:** The goal isn't to test *every* combination, but to ensure **diverse coverage** across all dimensions.

---

## Identifying Key Dimensions

### Step 1: Understand Your Domain

For the Recipe Chatbot, ask:
- What kinds of requests do users make?
- What constraints or preferences do they have?
- What contexts affect recipe recommendations?

### Step 2: Brainstorm Potential Dimensions

Based on the domain, potential dimensions include:

**User Preferences:**
- Cuisine type (Italian, Thai, Mexican, Indian, Chinese, etc.)
- Dietary restrictions (vegan, vegetarian, gluten-free, keto, paleo, halal, kosher)
- Flavor profiles (spicy, sweet, savory, tangy, mild)

**Practical Constraints:**
- Cooking time available (<15 min, 15-30 min, 30-60 min, >1 hour)
- Skill level (beginner, intermediate, advanced)
- Available equipment (oven, stovetop, microwave, air fryer, slow cooker)

**Context:**
- Meal type (breakfast, lunch, dinner, snack, dessert, appetizer)
- Occasion (weeknight, special occasion, meal prep, potluck, party)
- Number of servings (1, 2, 4, 6+)

**Input Specificity:**
- Available ingredients (user specifies what they have)
- Query style (short keywords, natural questions, detailed requests)

### Step 3: Prioritize Dimensions

You can't test all possible dimensions. Select **3-5 core dimensions** that:
1. **Most impact the response** - Dietary restrictions matter more than serving dish color
2. **Cover user diversity** - Different user types have different needs
3. **Align with failure modes** - Based on where you've seen the bot fail (from HW1 testing)

**Example Selection for Recipe Bot:**
1. **Dietary Restrictions** - Critical for correctness
2. **Meal Type** - Affects recipe recommendations significantly
3. **Cooking Time** - Common user constraint
4. **Cuisine Preference** - Adds variety to testing
5. **Available Ingredients** - Tests bot's ability to work with constraints

---

## Creating Dimension Value Matrices

### Define Values for Each Dimension

For each selected dimension, list 3-7 concrete values:

**Dimension 1: Dietary Restrictions**
- No restrictions
- Vegan
- Vegetarian
- Gluten-free
- Keto
- Paleo
- Nut-free

**Dimension 2: Meal Type**
- Breakfast
- Lunch
- Dinner
- Snack
- Dessert
- Appetizer

**Dimension 3: Cooking Time**
- Quick (<15 minutes)
- Moderate (15-30 minutes)
- Standard (30-60 minutes)
- Long (>60 minutes)

**Dimension 4: Cuisine Preference**
- Italian
- Mexican
- Thai
- Indian
- Chinese
- Mediterranean
- American comfort food

**Dimension 5: Query Style**
- Short keywords ("vegan pasta")
- Natural question ("What's a good vegan pasta recipe?")
- Detailed request ("I want a vegan pasta dish with mushrooms that takes less than 30 minutes")
- Ingredient-based ("I have pasta, mushrooms, and garlic. What can I make?")

---

## Ensuring Balanced Coverage

### Calculating Total Combinations

With 5 dimensions:
- Dietary (7 values) × Meal Type (6) × Time (4) × Cuisine (7) × Style (4) = **4,704 combinations**

Clearly, you can't test all of them. Instead, use **sampling strategies**.

### Strategy 1: Full Factorial (Small Sets)

If you have 2-3 dimensions with few values, test **all combinations**.

**Example:** 2 dimensions with 3 values each = 9 total queries

| Dietary | Meal Type | Query |
|---------|-----------|-------|
| Vegan | Breakfast | "Vegan breakfast recipe" |
| Vegan | Lunch | "Vegan lunch ideas" |
| Vegan | Dinner | "Vegan dinner recipe" |
| Vegetarian | Breakfast | "Vegetarian breakfast" |
| Vegetarian | Lunch | "Vegetarian lunch recipe" |
| Vegetarian | Dinner | "Vegetarian dinner ideas" |
| No restrictions | Breakfast | "Quick breakfast recipe" |
| No restrictions | Lunch | "Easy lunch" |
| No restrictions | Dinner | "Simple dinner recipe" |

### Strategy 2: Latin Hypercube Sampling (Large Sets)

For many dimensions, use **Latin Hypercube Sampling** (LHS):
1. Ensure each dimension value appears at least once
2. Avoid over-representing any combination
3. Maximize coverage with minimal queries

**Example:** 10 queries covering 5 dimensions

| ID | Dietary | Meal Type | Time | Cuisine | Style | Query |
|----|---------|-----------|------|---------|-------|-------|
| 1 | Vegan | Breakfast | Quick | Mediterranean | Natural | "What's a quick vegan Mediterranean breakfast?" |
| 2 | Vegetarian | Lunch | Moderate | Indian | Detailed | "I want a vegetarian Indian lunch that takes about 20 minutes" |
| 3 | Gluten-free | Dinner | Standard | Italian | Ingredient | "I have gluten-free pasta and tomatoes. What can I make for dinner?" |
| 4 | Keto | Snack | Quick | American | Short | "keto snack ideas" |
| 5 | Paleo | Dessert | Long | Mexican | Natural | "What's a paleo-friendly Mexican dessert I can make?" |
| 6 | No restrictions | Appetizer | Moderate | Thai | Detailed | "I need a Thai appetizer for a party, something that takes 30 minutes" |
| 7 | Nut-free | Breakfast | Standard | Chinese | Natural | "Can you suggest a nut-free Chinese breakfast?" |
| 8 | Vegan | Dinner | Quick | Indian | Short | "quick vegan curry" |
| 9 | Vegetarian | Lunch | Long | Italian | Ingredient | "I have ricotta, spinach, and lasagna noodles. What can I make?" |
| 10 | Gluten-free | Snack | Moderate | Mediterranean | Natural | "What's a gluten-free Mediterranean snack?" |

**Notice:**
- Each dietary restriction appears once or twice
- Each meal type is represented
- Varied time constraints
- Diverse cuisines
- Different query styles

### Strategy 3: Pairwise Testing

Test all **pairs** of dimension values, ensuring every pair appears at least once. This catches interactions between two dimensions while keeping test size manageable.

**Example:** Test these pairwise interactions:
- Vegan + Breakfast
- Vegan + Quick time
- Vegan + Italian
- Keto + Dinner
- Keto + Long time
- Gluten-free + Quick time
- Gluten-free + Thai
- etc.

---

## Edge Cases and Boundary Conditions

### What Are Edge Cases?

**Edge cases** are queries that:
- Combine **conflicting requirements** ("vegan cheeseburger")
- Use **ambiguous language** ("healthy dinner")
- Test **boundary limits** ("recipe in 1 minute")
- Include **unusual combinations** ("breakfast sushi")

### Types of Edge Cases to Test

#### 1. Conflicting Requirements
- "Vegan cheese pizza" - Can't use traditional cheese
- "Keto pasta dish" - Pasta is high-carb
- "Quick slow-cooked meal" - Contradictory time constraint
- "Beginner-friendly soufflé" - Soufflés are advanced

#### 2. Ambiguous Queries
- "Healthy dinner" - What does "healthy" mean?
- "Easy recipe" - Easy for whom?
- "Something with chicken" - Too vague
- "Make me food" - No useful constraints

#### 3. Extreme Values
- "Recipe in 2 minutes" - Unrealistically short
- "Gourmet 12-course meal" - Extremely complex
- "Serves 50 people" - Unusual scale
- "Using only salt" - Too constrained

#### 4. Unusual Combinations
- "Breakfast pizza" - Uncommon meal type for cuisine
- "Thai tacos" - Fusion cuisine
- "Dessert soup" - Unexpected category mix
- "Spicy ice cream" - Conflicting flavor profiles

#### 5. Null or Minimal Input
- Empty query: ""
- Single word: "recipe"
- Just ingredient: "chicken"
- Punctuation only: "???"

### Example Edge Case Test Set

```csv
id,query,edge_case_type
E1,"Vegan cheeseburger recipe",Conflicting requirement
E2,"Keto pasta dish",Conflicting requirement
E3,"Healthy dinner for tonight",Ambiguous
E4,"Easy recipe please",Ambiguous
E5,"Recipe in 90 seconds",Extreme time
E6,"Gourmet 10-course tasting menu",Extreme complexity
E7,"Breakfast tacos with Thai flavors",Unusual combination
E8,"Savory dessert with vegetables",Unusual combination
E9,"Recipe",Minimal input
E10,"chicken",Single word
E11,"Quick expensive meal for one",Conflicting priorities
E12,"Impress my date with beginner cooking",Conflicting skill/goal
```

---

## Coverage Analysis

### Evaluating Your Query Set

After creating your test queries, check for:

#### 1. Dimension Coverage
- Does each dimension value appear at least once?
- Are any values over-represented (>50% of queries)?
- Are any values completely missing?

**Example Analysis:**

| Dimension | Value | Count | Percentage |
|-----------|-------|-------|------------|
| Dietary | Vegan | 3 | 30% |
| Dietary | Vegetarian | 2 | 20% |
| Dietary | No restrictions | 5 | 50% ❌ Over-represented |
| Dietary | Gluten-free | 0 | 0% ❌ Missing |

**Fix:** Add gluten-free query, reduce "no restrictions" queries

#### 2. Interaction Coverage
- Are important dimension pairs tested? (e.g., "Vegan + Quick time")
- Are high-risk combinations included? (e.g., "Gluten-free + Italian")

#### 3. Edge Case Coverage
- Do you have queries with conflicting requirements?
- Do you test ambiguous inputs?
- Do you test extreme values?

### Coverage Checklist

- [ ] Each dimension value appears ≥1 time
- [ ] No dimension value represents >40% of queries
- [ ] At least 3 edge cases included
- [ ] Mix of query styles (short, detailed, natural, ingredient-based)
- [ ] Realistic user scenarios represented
- [ ] Both common and uncommon combinations tested

---

## Practical Exercises

### Exercise 1: Dimension Mapping

**Task:** Identify 4 dimensions for the Recipe Chatbot and list 4-5 values for each.

**Template:**
```
Dimension 1: _________________
Values:
  - _______________
  - _______________
  - _______________
  - _______________

Dimension 2: _________________
Values:
  - _______________
  - _______________
  - _______________
  - _______________

[Continue for Dimensions 3-4]
```

### Exercise 2: Query Generation

Using your dimensions from Exercise 1, create **10 diverse test queries** that:
- Cover all dimension values
- Include at least 2 edge cases
- Use varied query styles

**CSV Format:**
```csv
id,query,dimensions_covered
1,"[your query]","[list dimensions]"
2,"[your query]","[list dimensions]"
...
```

Save to [`data/sample_queries.csv`](../../data/sample_queries.csv)

### Exercise 3: Coverage Analysis

Review the existing sample queries in [`data/sample_queries.csv`](../../data/sample_queries.csv):

```csv
id,query
1,Suggest a quick vegan breakfast recipe
2,I have chicken and rice. what can I cook?
3,Give me a dessert recipe with chocolate
4,I want to eat gulab jamun.
5,Lets make pizza.
6,Sahi paneer recipe.
7,Make gajar ka halwa in 5 minutes.
8,Gajar ka halwa in 3 hours.minimise the calories.
```

**Questions:**
1. What dimensions are represented?
2. What dimensions are missing?
3. Are there any edge cases?
4. What 5 queries would you add to improve coverage?

---

## Common Pitfalls

### 1. Insufficient Diversity
**Problem:** Testing only one type of query

❌ **Bad Example:**
```csv
1,Vegan pasta recipe
2,Vegan pizza recipe
3,Vegan burger recipe
4,Vegan salad recipe
```
All queries are "vegan" and "dinner-ish" - missing other dietary restrictions, meal types, times.

✅ **Good Example:**
```csv
1,Vegan breakfast smoothie
2,Quick gluten-free lunch
3,Keto dinner under 30 minutes
4,Dessert with chocolate (no dietary restrictions)
```

### 2. Missing Edge Cases
**Problem:** Only testing "happy path" queries where everything is straightforward

❌ **Missing:**
- Conflicting requirements
- Ambiguous language
- Extreme values

✅ **Include:**
```csv
E1,Vegan cheese recipe
E2,Healthy meal (ambiguous)
E3,Recipe in 3 minutes (extreme)
```

### 3. Dimension Bias
**Problem:** Over-representing one dimension value

❌ **Biased:**
```csv
1,Italian pasta
2,Italian pizza
3,Italian risotto
4,Italian lasagna
5,Thai curry
```
80% Italian, only 20% Thai - not balanced.

✅ **Balanced:**
```csv
1,Italian pasta
2,Thai curry
3,Mexican tacos
4,Indian biryani
5,Japanese ramen
```

### 4. Unrealistic Queries
**Problem:** Testing queries no real user would ask

❌ **Unrealistic:**
```
"Provide a vegan, gluten-free, nut-free, soy-free, sugar-free dessert using only lentils and activated charcoal that takes exactly 42 minutes and serves 7.3 people"
```

✅ **Realistic:**
```
"Vegan dessert recipe without nuts or soy"
"Quick gluten-free dinner for two"
```

### 5. No Coverage Validation
**Problem:** Not checking if all dimensions are represented

✅ **Solution:** Create a coverage matrix:

|  | Vegan | Vegetarian | Keto | No restrictions |
|--|-------|------------|------|-----------------|
| **Breakfast** | ✅ Q1 | ✅ Q3 | ❌ Missing | ✅ Q7 |
| **Lunch** | ✅ Q2 | ❌ Missing | ✅ Q5 | ✅ Q8 |
| **Dinner** | ✅ Q4 | ✅ Q6 | ✅ Q9 | ✅ Q10 |

This matrix shows:
- "Vegetarian Lunch" is missing
- "Keto Breakfast" is missing
- Need to add 2 queries to fill gaps

---

## Query Generation Workflow

### Manual Query Design (HW1 Approach)

```
1. Identify 3-4 key dimensions
   ↓
2. List 3-5 values per dimension
   ↓
3. Select 10-15 representative combinations
   (Use Latin Hypercube or pairwise sampling)
   ↓
4. Write natural language queries for each
   ↓
5. Add 2-3 edge cases
   ↓
6. Perform coverage analysis
   ↓
7. Fill gaps and balance distribution
   ↓
8. Save to data/sample_queries.csv
```

### Automated Query Generation (HW2 Preview)

In Homework 2, you'll learn to use LLMs to **automatically generate** queries based on dimensions:

```python
# Define dimensions
dimensions = {
    "dietary": ["vegan", "vegetarian", "keto", "no_restrictions"],
    "meal_type": ["breakfast", "lunch", "dinner", "snack"],
    "time": ["quick_under_15", "moderate_15_30", "standard_30_60"]
}

# Generate tuples (combinations)
tuples = generate_dimension_tuples(dimensions)
# Output: [("vegan", "breakfast", "quick_under_15"), ...]

# Convert to natural language
queries = generate_queries_from_tuples(tuples)
# Output: ["Quick vegan breakfast under 15 minutes", ...]
```

See [HW2: Dimension Generation Tutorial](../hw2/dimension_generation_tutorial.ipynb) for details.

---

## Key Takeaways

- ✅ **Dimensions define query space** - Identify 3-5 key dimensions that vary in your domain
- ✅ **Coverage beats quantity** - 10 diverse queries > 50 similar queries
- ✅ **Edge cases reveal failures** - Test conflicting, ambiguous, and extreme queries
- ✅ **Systematic sampling** - Use strategies (Latin Hypercube, pairwise) for large dimension spaces
- ✅ **Validate coverage** - Check that all dimension values are represented
- ✅ **Balance distribution** - Avoid over-representing any single dimension value
- ✅ **Keep it realistic** - Test queries that real users would actually ask

---

## Further Reading

### Related Tutorials
- [System Prompt Engineering Tutorial](system_prompt_engineering_tutorial.md) - Write effective prompts before testing
- [HW2: Dimension Generation Tutorial](../hw2/dimension_generation_tutorial.ipynb) - Automate query generation with LLMs
- [HW2: Error Analysis Concepts](../hw2/error_analysis_concepts.md) - Analyze failures from diverse queries

### Testing Strategies
- [Pairwise Testing](https://en.wikipedia.org/wiki/All-pairs_testing) - Combinatorial testing technique
- [Latin Hypercube Sampling](https://en.wikipedia.org/wiki/Latin_hypercube_sampling) - Efficient sampling for high dimensions
- [Boundary Value Analysis](https://en.wikipedia.org/wiki/Boundary-value_analysis) - Testing edge cases and limits

### Course Materials
- [AI Evaluation Complete Guide](../../AI_EVALUATION_COMPLETE_GUIDE.md) - Section 2.5: Testing System Prompts
- [HW1 Assignment README](readme.md) - Full homework instructions
- [Bulk Test Script](../../scripts/bulk_test.py) - Automated testing workflow

---

**Tutorial Status:** ✅ Complete
**Last Updated:** 2025-10-29
**Maintainer:** AI Evaluation Course Team
