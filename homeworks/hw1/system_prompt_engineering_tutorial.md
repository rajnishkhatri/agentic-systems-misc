# System Prompt Engineering Tutorial

## Learning Objectives

By completing this tutorial, you will be able to:
- ✅ Write effective system prompts with clear role definition and constraints
- ✅ Set behavioral rules using "always" and "never" instructions
- ✅ Control LLM agency and creativity levels appropriately
- ✅ Structure outputs with Markdown formatting for better user experience
- ✅ Implement safety clauses and ethical considerations
- ✅ Apply iterative prompt refinement strategies

## Prerequisites

- Basic understanding of Large Language Models (LLMs)
- Familiarity with chatbot interactions
- No prior homework completion needed

## Estimated Time

**Reading + Exercises:** 25-30 minutes

---

## Concepts

### What is a System Prompt?

The **system prompt** is the foundational instruction that defines your AI system's behavior. It acts as the "instruction manual" for the LLM, telling it:

- **What** the AI system is (its role and identity)
- **How** it should behave (rules and constraints)
- **What format** its outputs should follow
- **What** it should never do (safety boundaries)

Think of the system prompt as the difference between hiring a chef and a nutritionist. Both might talk about food, but their roles, expertise, and communication styles are completely different.

### Why System Prompts Matter

Without a well-crafted system prompt:
- ❌ **Inconsistent behavior** - LLM responses vary wildly across similar queries
- ❌ **Missing structure** - Outputs are hard to read or parse
- ❌ **Violated constraints** - LLM ignores dietary restrictions or time limits
- ❌ **Safety issues** - No guardrails for inappropriate requests

With a good system prompt:
- ✅ **Predictable behavior** - Consistent responses aligned with requirements
- ✅ **Structured output** - Easy-to-read, well-formatted responses
- ✅ **Constraint adherence** - Respects limitations and user preferences
- ✅ **Safe operations** - Handles edge cases gracefully

---

## Anatomy of an Effective System Prompt

Let's analyze the production system prompt from our Recipe Chatbot (see [`backend/utils.py:33-62`](../../backend/utils.py)):

```python
SYSTEM_PROMPT = (
    "You are an expert chef recommending delicious and useful recipes. "

    "Present only one recipe at a time. If the user doesn't specify what ingredients "
    "they have available, assume only basic ingredients are available."
    "Be descriptive in the steps of the recipe, so it is easy to follow."
    "Have variety in your recipes, don't just recommend the same thing over and over."
    "You MUST suggest a complete recipe; don't ask follow-up questions."
    "Mention the serving size in the recipe. If not specified, assume 2 people."
    "Structure all recipe responses clearly using Markdown for formatting."
    # ... formatting instructions omitted for brevity
)
```

### Breakdown of Components

#### 1. Role Definition
```
"You are an expert chef recommending delicious and useful recipes."
```

**Purpose:** Sets the persona and expertise level
- Defines authority ("expert chef")
- Clarifies primary function ("recommending recipes")
- Sets tone expectations ("delicious and useful")

**Why this matters:** The role shapes how the LLM interprets ambiguous queries. An "expert chef" will provide culinary techniques; a "cooking instructor" would emphasize teaching.

#### 2. Core Constraints
```
"Present only one recipe at a time."
"You MUST suggest a complete recipe; don't ask follow-up questions."
```

**Purpose:** Prevents undesirable behaviors
- Stops overwhelming users with multiple recipes
- Forces complete responses instead of asking clarifying questions
- Uses strong language ("MUST") for critical requirements

**Why this matters:** LLMs tend to be conversational and ask follow-up questions. This constraint ensures direct, actionable responses.

#### 3. Behavioral Guidelines
```
"Be descriptive in the steps of the recipe, so it is easy to follow."
"Have variety in your recipes, don't just recommend the same thing over and over."
"If the user doesn't specify what ingredients they have available, assume only basic ingredients are available."
```

**Purpose:** Shapes quality and decision-making
- **Quality requirement:** "Be descriptive"
- **Variety requirement:** Prevents repetitive suggestions
- **Default assumption:** Handles missing information gracefully

**Why this matters:** These guidelines make the bot more useful in real-world scenarios where users provide incomplete information.

#### 4. Output Requirements
```
"Mention the serving size in the recipe. If not specified, assume 2 people."
"Structure all recipe responses clearly using Markdown for formatting."
```

**Purpose:** Ensures completeness and consistency
- **Completeness:** Always include serving size
- **Format:** Use Markdown for structure

**Why this matters:** Structured output is easier to parse, display, and understand.

---

## System Prompt Design Patterns

### Pattern 1: Role + Rules + Format

This is the most common pattern for task-oriented chatbots.

```python
PROMPT = """
You are a [ROLE] specializing in [DOMAIN].

RULES:
- Always [REQUIREMENT_1]
- Never [PROHIBITION_1]
- If [CONDITION], then [ACTION]

OUTPUT FORMAT:
[Specific formatting instructions using Markdown]
"""
```

**Example:**
```python
NUTRITION_BOT_PROMPT = """
You are a certified nutritionist specializing in meal planning and dietary advice.

RULES:
- Always provide macronutrient breakdown (protein, carbs, fats)
- Never provide medical advice or diagnose health conditions
- If the user has specific dietary restrictions, verify all ingredients against those constraints

OUTPUT FORMAT:
Structure all responses using Markdown:
## [Food/Meal Name]
### Nutritional Information
* Calories: [amount]
* Protein: [g]
* Carbs: [g]
* Fats: [g]

### Health Benefits
- [Benefit 1]
- [Benefit 2]
"""
```

### Pattern 2: Persona + Constraints + Examples

This pattern is useful when you want to show the LLM exactly how to respond.

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

**Example:**
```python
CODING_TUTOR_PROMPT = """
You are a patient coding tutor helping beginners learn Python programming.

CONSTRAINTS:
1. Never provide complete solutions; guide students with hints
2. Always explain *why* something works, not just *what* to do
3. Use analogies and real-world examples to clarify concepts
4. If a student asks about advanced topics, acknowledge their curiosity but redirect to foundational concepts

EXAMPLE OUTPUT:
**Question:** How do I create a list in Python?

**Response:**
Think of a list like a shopping list you'd write on paper - it's a collection of items in order.

To create one:
```python
fruits = ["apple", "banana", "orange"]
```

Notice the square brackets `[]` - they tell Python "this is a list." Each item is separated by a comma.

Try creating a list of your favorite colors! What happens when you print it?
"""
```

### Pattern 3: Task + Guidelines + Safety

This pattern emphasizes safety and handles edge cases explicitly.

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

**Example:**
```python
FINANCIAL_ADVISOR_PROMPT = """
TASK: Provide general financial literacy information and budgeting advice.

GUIDELINES:
- Focus on principles like saving, budgeting, and understanding interest rates
- Use examples with realistic numbers ($50/week savings, etc.)
- Encourage users to consult licensed financial advisors for investment decisions

SAFETY:
- If the user asks for specific stock picks or investment advice, respond: "I can explain general investment concepts, but I can't recommend specific stocks or investments. Please consult a licensed financial advisor for personalized advice."
- If the user mentions financial distress, provide resources: "If you're experiencing financial hardship, consider reaching out to a non-profit credit counseling service like NFCC (nfcc.org)."
"""
```

---

## Markdown Formatting in System Prompts

### Why Markdown?

Markdown provides:
- ✅ **Consistent, readable output** - Professional appearance across platforms
- ✅ **Easy to parse programmatically** - Can extract sections for processing
- ✅ **Clear structure for users** - Headers, lists, and emphasis guide attention
- ✅ **Universal rendering** - Works in Slack, Discord, GitHub, documentation, etc.

### Specifying Markdown Structure

From our Recipe Bot example:

```python
"Structure all recipe responses clearly using Markdown for formatting."
"Strictly follow the format below:"
"**Title of recipe**"
"Summary of recipe"
"**Ingredients**"
"* ingredient 1 with quantity"
"* ingredient 2 with quantity"
"**Instructions**"
"1. Step 1"
"2. Step 2"
"**Tips**"
"Tip 1"
"Tip 2"
```

**Expected Output:**
```markdown
**Golden Pan-Fried Salmon**

A quick and delicious way to prepare salmon with crispy skin and moist interior.

**Ingredients**
* 2 salmon fillets (6oz each, skin-on)
* 1 tbsp olive oil
* Salt and pepper to taste
* 1 lemon (for serving)

**Instructions**
1. Pat salmon completely dry with paper towel
2. Season both sides with salt and pepper
3. Heat oil in skillet over medium-high heat
4. Place salmon skin-side down, cook 4-6 minutes
5. Flip and cook 2-4 more minutes
6. Serve with lemon wedges

**Tips**
Ensure pan is hot before adding salmon for best sear
Press down gently during first minute for crispy skin
```

---

## Common Pitfalls and Solutions

| Pitfall | Problem | Example (Bad) | Solution (Good) |
|---------|---------|---------------|-----------------|
| **Too Vague** | LLM doesn't know what to do | "Be helpful" | "Always provide ingredient measurements in both metric and imperial units" |
| **Too Restrictive** | LLM can't handle edge cases | "Only suggest recipes from 'Classic Cookbook Vol. 1'" | "Suggest recipes based on available ingredients, using creative combinations when needed" |
| **Conflicting Rules** | LLM gets confused | "Be concise" + "Be very detailed" | "Be concise in descriptions (2-3 sentences), but detailed in instructions (step-by-step)" |
| **No Safety Clause** | Handles inappropriate requests | No mention of unsafe content | "If asked for unsafe recipes (raw meat, harmful substances), politely decline and explain why" |
| **Unclear Output** | Inconsistent formatting | "Provide recipe information" | "Use Markdown with ## for recipe title, ### for sections (Ingredients, Instructions, Tips)" |
| **Missing Defaults** | LLM asks too many questions | No handling of missing info | "If serving size not specified, assume 2 people" |

### Example: Improving a Vague Prompt

❌ **Bad Prompt:**
```python
"You are a recipe bot. Help users with recipes."
```

**Problems:**
- No behavioral constraints
- No output format
- No handling of edge cases
- No safety considerations

✅ **Good Prompt:**
```python
"""
You are an expert home chef specializing in accessible, easy-to-follow recipes.

RULES:
- Present exactly one recipe per response
- If ingredients aren't specified, assume pantry staples (flour, eggs, oil, salt, pepper, etc.)
- Always include serving size (default: 2 servings)
- Provide cooking time estimates
- Use precise measurements (cups, tablespoons, grams)

SAFETY:
- If asked for recipes with raw meat, raw eggs, or unsafe food combinations, explain food safety concerns
- If asked about allergen substitutions, always remind users to verify all ingredient labels

OUTPUT FORMAT:
## [Recipe Title]
[1-2 sentence description]

### Ingredients
* [ingredient with quantity]

### Instructions
1. [detailed step]

### Time
Prep: [X] min | Cook: [Y] min | Total: [Z] min

### Tips (optional)
* [helpful tip]
"""
```

---

## Testing System Prompts

### Creating a Diverse Test Suite

Your test queries should cover multiple dimensions to stress-test your prompt. For a recipe chatbot:

**1. Cuisine Types**
- "Italian pasta dish with tomatoes"
- "Spicy Thai curry recipe"
- "Japanese ramen with pork"

**2. Dietary Restrictions**
- "Vegan chocolate dessert"
- "Gluten-free breakfast ideas"
- "Keto-friendly dinner under 10g carbs"

**3. Available Ingredients**
- "What can I make with chicken, rice, and broccoli?"
- "Recipe using eggs, cheese, and spinach"
- "Something with leftover rotisserie chicken"

**4. Time Constraints**
- "Quick lunch under 15 minutes"
- "30-minute weeknight dinner"
- "Recipe I can make in 5 minutes"

**5. Skill Levels**
- "Beginner-friendly baking recipe"
- "Advanced French cooking technique"
- "Simple recipe for kids to make"

**6. Ambiguous Queries (Edge Cases)**
- "Something healthy for dinner"
- "Easy recipe please"
- "Help me cook"

**7. Conflicting Requirements**
- "Vegan cheeseburger recipe"
- "Quick recipe that's also impressive"
- "Cheap gourmet meal"

### Bulk Testing Workflow

You can test your system prompt systematically using the bulk testing script at [`scripts/bulk_test.py`](../../scripts/bulk_test.py):

```bash
# 1. Add queries to data/sample_queries.csv
# 2. Update system prompt in backend/utils.py
# 3. Run bulk test
python scripts/bulk_test.py
# 4. Review results in outputs/
```

This generates a CSV with all bot responses, which you can review for:
- Consistency across similar queries
- Adherence to formatting rules
- Handling of edge cases
- Completeness of responses

---

## Iterative Refinement Strategy

System prompt engineering is **iterative**. Follow this cycle:

```
┌─────────────────────────────────────────────────┐
│ 1. Write initial prompt                         │
│    ↓                                            │
│ 2. Test with diverse queries                    │
│    ↓                                            │
│ 3. Identify failure patterns                    │
│    ↓                                            │
│ 4. Add/refine constraints                       │
│    ↓                                            │
│ 5. Test again                                   │
│    ↓                                            │
│ 6. Repeat until satisfactory                    │
└─────────────────────────────────────────────────┘
```

### Example Iteration Log

**Version 1:**
```python
"You are a recipe bot. Provide recipes."
```
**Test Results:** Responses too vague, no structure, asks follow-up questions

---

**Version 2:**
```python
"You are an expert chef. Provide recipes in Markdown format with ingredients and instructions."
```
**Test Results:** Better structure, but missing serving sizes, inconsistent time estimates

---

**Version 3:**
```python
"You are an expert chef. Provide recipes with ingredients, instructions, serving size (default: 2), and cooking time. Use Markdown formatting."
```
**Test Results:** Good structure, but still asks follow-up questions instead of providing complete recipes

---

**Version 4 (Final):**
```python
"You are an expert chef. You MUST provide complete recipes without asking follow-up questions. Include: ingredients with quantities, step-by-step instructions, serving size (default: 2), and cooking time. Use Markdown formatting."
```
**Test Results:** ✅ Complete, structured, consistent responses

---

## Practical Exercise

### Exercise 1: Analyze the Recipe Bot Prompt

Review the full system prompt in [`backend/utils.py:33-62`](../../backend/utils.py) and answer:

1. What role is defined? How specific is it?
2. List all "always" constraints (explicit or implied)
3. List all "never" constraints (explicit or implied)
4. What default assumptions are made?
5. How is the output format specified?
6. Are there any safety clauses?

### Exercise 2: Write a System Prompt

Create a system prompt for a **"Workout Recommendation Bot"** that:

**Requirements:**
- Recommends exercises based on fitness level and available equipment
- Never provides medical advice
- Always includes safety warnings for high-intensity exercises
- Uses structured Markdown output with exercise name, instructions, sets/reps, and difficulty level
- Defaults to bodyweight exercises if no equipment specified

**Template to fill:**
```python
WORKOUT_BOT_PROMPT = """
You are [DEFINE ROLE].

RULES:
- Always [REQUIREMENT_1]
- Always [REQUIREMENT_2]
- Never [PROHIBITION_1]
- If [CONDITION], then [ACTION]

SAFETY:
- [SAFETY_CLAUSE_1]
- [SAFETY_CLAUSE_2]

OUTPUT FORMAT:
[Specify Markdown structure]
"""
```

### Exercise 3: Test and Iterate

1. Write your workout bot prompt
2. Test it with these queries:
   - "I want to get stronger"
   - "Quick morning workout, no equipment"
   - "Advanced chest exercises with dumbbells"
   - "Exercises for my injured knee"
   - "Help me lose weight"
3. Identify where it fails or behaves unexpectedly
4. Refine your prompt and test again

---

## Key Takeaways

- ✅ **System prompts are foundational** - They define all behavior, so invest time crafting them
- ✅ **Be specific, not vague** - "Always include serving size" beats "be helpful"
- ✅ **Use patterns** - Role + Rules + Format works for most task-oriented bots
- ✅ **Markdown enables structure** - Specify exact output format for consistency
- ✅ **Test iteratively** - Write prompt → test → refine → repeat
- ✅ **Handle edge cases explicitly** - "If X, then Y" prevents confusion
- ✅ **Safety first** - Always include clauses for inappropriate or harmful requests

---

## Further Reading

### Official Guides
- [OpenAI Prompt Engineering Guide](https://platform.openai.com/docs/guides/prompt-engineering) - Best practices from OpenAI
- [Anthropic Prompt Engineering Guide](https://docs.anthropic.com/claude/docs/prompt-engineering) - Claude-specific techniques
- [LangChain Prompt Templates](https://python.langchain.com/docs/modules/model_io/prompts/) - Reusable prompt patterns

### Related Tutorials
- [Query Diversity Tutorial](query_diversity_tutorial.md) - Designing comprehensive test query sets
- [HW2: Error Analysis Concepts](../hw2/error_analysis_concepts.md) - Identifying failure patterns systematically

### Course Materials
- [AI Evaluation Complete Guide](../../AI_EVALUATION_COMPLETE_GUIDE.md) - Section 2: Prompt Engineering Fundamentals
- [HW1 Assignment README](readme.md) - Full homework instructions

---

**Tutorial Status:** ✅ Complete
**Last Updated:** 2025-10-29
**Maintainer:** AI Evaluation Course Team
