# Homework 1: Tutorial Index

## Overview

Homework 1 introduces the foundational skills of **prompt engineering** and **test query design** for AI system evaluation. You'll learn to craft effective system prompts that define bot behavior and create diverse test queries that systematically stress-test your AI system.

**Learning Time:** ~2-3 hours
**Difficulty:** Beginner
**Prerequisites:** Basic understanding of LLMs and chatbots

---

## Learning Objectives

By completing these tutorials, you will be able to:
- ✅ Write clear, effective system prompts with proper role definition and constraints
- ✅ Design diverse test query sets that cover multiple dimensions of user behavior
- ✅ Structure prompts with appropriate formatting instructions for user experience
- ✅ Identify key dimensions for systematic query generation
- ✅ Evaluate query coverage and identify gaps in test sets

---

## Tutorials

### 1. System Prompt Engineering Tutorial
**File:** `system_prompt_engineering_tutorial.md`
**Reading Time:** 15-20 minutes
**Topics:**
- Defining bot role and objective clearly
- Setting behavioral rules (always/never instructions)
- Controlling LLM agency and creativity levels
- Structuring output with Markdown formatting
- Safety clauses and ethical considerations
- Iterative prompt refinement strategies

**When to use:** Start here if you're new to prompt engineering or need to write a system prompt from scratch.

---

### 2. Query Diversity Tutorial
**File:** `query_diversity_tutorial.md`
**Reading Time:** 15-20 minutes
**Topics:**
- Identifying key dimensions for query variation
- Dimension examples: cuisine type, dietary restrictions, meal type, cooking time
- Creating dimension value matrices
- Ensuring query coverage across dimensions
- Testing edge cases and boundary conditions
- Avoiding bias in query selection

**When to use:** Use this after writing your system prompt to create a comprehensive test query set.

---

## Recommended Learning Path

```
┌─────────────────────────────────────────────────────┐
│                  HW1 Learning Flow                  │
├─────────────────────────────────────────────────────┤
│                                                     │
│  1. Read README.md                                  │
│     ↓                                               │
│  2. Complete System Prompt Engineering Tutorial    │
│     ↓                                               │
│  3. Write your system prompt (backend/utils.py)    │
│     ↓                                               │
│  4. Complete Query Diversity Tutorial              │
│     ↓                                               │
│  5. Expand data/sample_queries.csv                 │
│     ↓                                               │
│  6. Run bulk test (scripts/bulk_test.py)           │
│     ↓                                               │
│  7. Evaluate results and iterate                   │
└─────────────────────────────────────────────────────┘
```

---

## Key Concepts

### System Prompt
A **system prompt** is the foundational instruction that defines:
- **What** the AI system is (its role and identity)
- **How** it should behave (rules and constraints)
- **What format** its outputs should follow
- **What** it should never do (safety boundaries)

**Example:**
```
You are a friendly culinary assistant specializing in easy-to-follow recipes.
Always provide precise ingredient measurements using standard units.
Never suggest recipes requiring extremely rare ingredients without alternatives.
```

### Query Dimensions
**Dimensions** are the key variables that define the space of possible user inputs. For a recipe chatbot:
- **Cuisine Type:** Italian, Thai, Mexican, Indian, French
- **Dietary Restriction:** Vegan, vegetarian, gluten-free, keto, paleo
- **Meal Type:** Breakfast, lunch, dinner, snack, dessert
- **Cooking Time:** <15 min, 15-30 min, 30-60 min, >60 min
- **Skill Level:** Beginner, intermediate, advanced

Systematically varying these dimensions ensures comprehensive test coverage.

---

## Practical Exercises

After completing the tutorials, try these exercises:

1. **Prompt Iteration Exercise**
   - Write 3 different system prompts for the same chatbot
   - Test each with identical queries
   - Compare outputs and identify which prompt works best

2. **Dimension Mapping Exercise**
   - Identify 4-5 dimensions for your recipe bot
   - List 3-5 values for each dimension
   - Calculate total possible combinations
   - Select 10-15 representative combinations

3. **Edge Case Discovery**
   - Identify queries that combine conflicting requirements
   - Test ambiguous or vague queries
   - Explore boundary conditions (e.g., "vegan cheeseburger")

---

## Common Pitfalls

### System Prompts
- ❌ **Too vague:** "Be helpful" → Doesn't guide specific behavior
- ❌ **Too restrictive:** "Only provide recipes with exactly 5 ingredients" → Limits useful responses
- ❌ **Contradictory rules:** "Be creative" + "Never deviate from known recipes"
- ❌ **Missing output format:** Users receive unstructured, hard-to-read responses

### Query Design
- ❌ **Insufficient diversity:** Only testing "happy path" queries
- ❌ **Missing edge cases:** Not testing contradictory or ambiguous requests
- ❌ **Dimension bias:** Over-representing one cuisine or dietary preference
- ❌ **Unrealistic queries:** Testing queries no real user would ask

---

## Resources

### Reference Files
- [`README.md`](readme.md) - Assignment instructions
- [`backend/utils.py`](../../backend/utils.py) - Where system prompts are defined
- [`data/sample_queries.csv`](../../data/sample_queries.csv) - Query dataset
- [`scripts/bulk_test.py`](../../scripts/bulk_test.py) - Bulk testing script

### External Resources
- [OpenAI Prompt Engineering Guide](https://platform.openai.com/docs/guides/prompt-engineering)
- [Anthropic Prompt Engineering Guide](https://docs.anthropic.com/claude/docs/prompt-engineering)
- [LangChain Prompt Templates](https://python.langchain.com/docs/modules/model_io/prompts/)

---

## Next Steps

After completing HW1, you'll have:
- ✅ A well-crafted system prompt
- ✅ A diverse set of 10+ test queries
- ✅ Baseline evaluation results

**Move on to Homework 2** to learn systematic error analysis and failure mode identification.

👉 [Homework 2 Tutorial Index](../hw2/TUTORIAL_INDEX.md)

---

## FAQ

**Q: How long should my system prompt be?**
A: Typically 100-300 words. Long enough to be specific, short enough to be clear.

**Q: How many test queries should I create?**
A: Minimum 10 for HW1. Aim for 20-30 for comprehensive coverage.

**Q: Should I use an LLM to generate queries?**
A: Optional for HW1, but recommended for HW2. Manual curation ensures diversity initially.

**Q: What if my queries produce unexpected results?**
A: Perfect! This is the foundation for error analysis in HW2.

---

**Tutorial Status:** ⏳ In Development
**Last Updated:** 2025-10-29
**Maintainer:** AI Evaluation Course Team
