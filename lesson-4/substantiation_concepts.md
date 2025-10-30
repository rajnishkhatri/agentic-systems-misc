# Substantiation Concepts Tutorial

## Learning Objectives

By completing this tutorial, you will be able to:
- ✅ Define substantiation and explain why it matters for AI safety
- ✅ Distinguish substantiated claims from hallucinations and fabrications
- ✅ Understand tool grounding as a source of verifiable evidence
- ✅ Apply verifiability criteria to conversational AI outputs
- ✅ Identify when substantiation evaluation is critical
- ✅ Recognize common substantiation failure modes
- ✅ Design systems that minimize unsubstantiated claims

## Prerequisites

- Understanding of conversational AI systems with function calling (tools)
- Completed [HW3: LLM-as-Judge](../homeworks/hw3/llm_judge_concepts.md) (recommended)
- Familiarity with JSON data structures
- Experience with LLM APIs

## Estimated Time

**Reading Time:** 18-22 minutes
**Hands-on Practice:** 30-40 minutes (when applying to your own system)

---

## Concepts

### What is Substantiation?

**Substantiation** is the property of an AI system's output where every factual claim can be verified by available evidence.

**Formal Definition:**

A response is **SUBSTANTIATED** if every factual claim can be verified by:
1. **User-provided information**: Facts explicitly stated by the user in the conversation
2. **Tool outputs**: Results from function calls (database queries, API responses, etc.)
3. **Tool metadata**: Available tools, their parameters, and capabilities
4. **Derivable information**: Facts that could be obtained by calling available tools with arguments from the conversation

A response is **UNSUBSTANTIATED** if it contains factual claims that cannot be verified from these sources.

### Why Substantiation Matters

**The Hallucination Problem:**

LLMs are trained to generate plausible text, not necessarily factual text. Without grounding, they will:
- ✗ Make up product details not in the database
- ✗ Fabricate appointment times not in the calendar
- ✗ Invent feature specifications not in documentation
- ✗ Create false citations and references

**Real-World Impact:**

```
User: "Does apartment A11 have a balcony?"

BAD Response (Unsubstantiated):
"Yes! Apartment A11 has a beautiful balcony with garden views and space
for outdoor furniture. Perfect for your morning coffee!"

Tool Output (Reality):
{"id": "A11", "price": 1200, "available": true}
  ↑
  Tool says nothing about balconies!

GOOD Response (Substantiated):
"Based on the available information, apartment A11 is listed at $1200/month
and is currently available. I don't have details about balcony features in
the database. Would you like me to contact the property manager for
clarification?"
```

**Why this is critical:**
- ❌ User makes decision based on false information
- ❌ Trust in AI system is broken
- ❌ Legal/regulatory issues for making false claims
- ❌ Operational problems when expectations don't match reality

---

## Substantiation vs. Hallucination vs. Fabrication

### Terminology Clarification

**Hallucination** (Broad Term):
- Any factually incorrect output from an LLM
- Includes both substantiation failures and knowledge errors
- Example: Saying Paris is in Germany (factual error)

**Unsubstantiated Claim** (Specific):
- Claim that cannot be verified from available sources
- Focus on **verifiability**, not factual correctness
- Example: Claiming balcony when database has no balcony field

**Fabrication** (Intentional-sounding):
- Often used for unsubstantiated claims that seem "made up"
- Example: Inventing a confirmation number that doesn't exist

**Key Distinction:**

```
┌──────────────────────────────────────────────────────┐
│            SUBSTANTIATION FOCUS                      │
├──────────────────────────────────────────────────────┤
│                                                      │
│  "Can I verify this claim from available sources?"  │
│                                                      │
│  ✅ SUBSTANTIATED: "Apartment is $1200/mo"          │
│     → Database says: price = 1200                    │
│                                                      │
│  ❌ UNSUBSTANTIATED: "Has beautiful balcony"        │
│     → Database doesn't mention balconies            │
│                                                      │
│  ⚠️  POSSIBLY CORRECT but UNVERIFIABLE:            │
│     "Located near subway"                            │
│     → Might be true, but not in tool outputs        │
└──────────────────────────────────────────────────────┘
```

**Why we focus on substantiation:**
- We can **measure** it objectively (verifiable vs. not)
- We can **control** it through prompt engineering
- We can **prevent** it by constraining outputs to tool-grounded facts

---

## Tool Grounding

### What is Tool Grounding?

**Tool grounding** means using function call results as the authoritative source of truth for factual claims.

**Architecture:**

```
User Query → Agent → Tool Call → Tool Output → Agent → Response
                                      ↑
                         Source of Truth for Response
```

**Example:**

```python
# User Query
"What recipes use tofu and take under 30 minutes?"

# Tool Call
search_recipes(ingredients=["tofu"], max_cook_time=30)

# Tool Output
{
  "results": [
    {"name": "Tofu Stir-Fry", "time": 20, "servings": 4},
    {"name": "Miso Soup with Tofu", "time": 15, "servings": 2}
  ],
  "total": 2
}

# ✅ SUBSTANTIATED Response:
"I found 2 recipes: Tofu Stir-Fry (20 minutes, serves 4) and Miso Soup
with Tofu (15 minutes, serves 2)."

# ❌ UNSUBSTANTIATED Response:
"I found 2 delicious recipes that are both vegan, gluten-free, and
high in protein. They're perfect for meal prep and will keep for 5 days
in the fridge."
  ↑
  Tool output doesn't mention: vegan, gluten-free, protein, meal prep, storage
```

### What Counts as Substantiated?

**✅ Directly Substantiated:**
- **Verbatim citation**: Tool says "20 minutes", response says "20 minutes"
- **Paraphrasing**: Tool says "cook_time: 20", response says "takes 20 minutes"
- **Aggregation**: Tool returns 2 items, response says "2 recipes"

**✅ Derivable from Tools:**
- **Metadata**: "I can search our recipe database" (tool is available)
- **Tool capabilities**: "I can filter by cooking time" (tool has `max_cook_time` parameter)
- **Obtainable**: "I can check ingredient details" (could call `get_recipe_details()`)

**❌ Unsubstantiated:**
- **New facts**: Adding details not in tool output
- **Assumptions**: "This is perfect for beginners" (tool doesn't rate difficulty)
- **Descriptive qualifiers**: "Delicious", "popular", "healthy" (not in data)
- **Temporal claims**: "This is currently trending" (unless tool provides trend data)

**⚠️ Edge Cases (Context-Dependent):**

**Courtesy Statements:**
```
✅ "How can I help you?"
✅ "Let me search for that."
✅ "I don't have information on X."

These are conversational moves, not factual claims → PASS
```

**Domain Knowledge:**
```
User: "Is tofu vegan?"
Response: "Yes, tofu is made from soybeans and is vegan."

If tools don't provide this info:
- Lenient: Common knowledge → PASS
- Strict: Not in tools → FAIL
→ Define in your evaluation criteria!
```

---

## Verifiability Criteria

### The Substantiation Checklist

For every factual claim in the response, ask:

**1. Is it from the user's messages?**
```
User: "I'm allergic to peanuts"
Response: "I'll exclude peanut-based recipes since you're allergic"
✅ Substantiated by user input
```

**2. Is it in a tool output?**
```
Tool: {"name": "Pad Thai", "calories": 450}
Response: "Pad Thai has 450 calories"
✅ Substantiated by tool data
```

**3. Is it tool metadata?**
```
Available tool: search_recipes(ingredients, dietary_filter)
Response: "I can filter by dietary restrictions"
✅ Substantiated by tool capabilities
```

**4. Could it be obtained by calling a tool?**
```
User: "What's in Pad Thai?"
Response: "I can look up the ingredient list for you"
✅ Obtainable via get_recipe_details(name="Pad Thai")
```

**5. Is it a courtesy statement (not a factual claim)?**
```
Response: "Great question! Let me search for that."
✅ Not a factual claim → PASS
```

**If none of the above:**
```
Response: "Pad Thai is one of our most popular dishes"
❌ Unsubstantiated → FAIL
```

### Common Failure Modes

#### 1. Descriptive Embellishment
**Problem:** Adding adjectives not in tool outputs

```
Tool: {"name": "Chocolate Cake", "price": 25}
❌ "Our delicious chocolate cake for just $25"
     ↑
     "delicious" is unsubstantiated
✅ "Chocolate cake for $25"
```

#### 2. Assumed Attributes
**Problem:** Inferring properties not explicitly provided

```
Tool: {"name": "Tofu Bowl", "ingredients": ["tofu", "rice", "vegetables"]}
❌ "This vegan tofu bowl..."
     ↑
     "vegan" is assumed (tofu could be cooked in fish sauce)
✅ "Tofu bowl with rice and vegetables"
```

#### 3. Invented Details
**Problem:** Adding specifics not in data

```
Tool: {"appointment": "2024-01-15 14:00"}
❌ "Your appointment is Jan 15 at 2pm in Room 302 with Dr. Smith"
     ↑
     Room number and doctor name not in tool output
✅ "Your appointment is January 15 at 2:00 PM"
```

#### 4. Outdated Cache
**Problem:** Using stale information not from current tool call

```
Previous Tool Call (5 min ago): {"stock": 10}
Current Tool Call: {"stock": 0}
❌ "We have 10 in stock" (using cached result)
✅ "Currently out of stock" (using current result)
```

#### 5. Cross-Conversation Leakage
**Problem:** Using information from other conversations

```
Other User's Conversation: "I love spicy food"
Current User: "Recommend a recipe"
❌ "Since you love spicy food, try this curry"
     ↑
     Current user never said they like spicy food
```

---

## When Substantiation Evaluation is Critical

### ✅ High-Priority Use Cases

**1. Customer-Facing Systems**
- Product recommendations
- Appointment scheduling
- Account information lookup
- Order status updates

**Why:** False information damages trust and creates operational issues

**2. Regulated Industries**
- Healthcare: Medical information must be from approved sources
- Finance: Investment advice must be from verified data
- Legal: Case information must be from actual case law

**Why:** Legal/regulatory compliance requires verifiable claims

**3. High-Stakes Decisions**
- Real estate: Property details affect major financial decisions
- Travel: Booking information must be accurate
- E-commerce: Product specs affect purchase decisions

**Why:** Users make important decisions based on AI output

**4. Production Monitoring**
- Continuous evaluation of deployed systems
- Detecting prompt regression after updates
- Ensuring consistent quality at scale

**Why:** Early detection of unsubstantiated responses prevents user harm

### ❌ Lower-Priority Use Cases

**1. Creative/Generative Tasks**
- Story writing
- Brainstorming
- Casual conversation

**Why:** Factual grounding is not the primary goal

**2. Opinion/Subjective Tasks**
- Product reviews synthesis
- Sentiment analysis
- Recommendation explanations

**Why:** Subjective judgments don't have ground truth

**3. Internal Tools (Low Risk)**
- Development assistants
- Internal documentation search
- Code completion

**Why:** Lower risk if incorrect (human validates anyway)

---

## Implementation Strategies

### Prevention: Design for Substantiation

**Strategy 1: Constrain to Tool Outputs**

```
Bad Prompt:
"Answer the user's question about the recipe."

Good Prompt:
"Answer ONLY using information from the tool output below.
Do not add descriptions, adjectives, or assumptions.

Tool Output: {tool_result}

If the tool output doesn't contain the information needed,
say 'I don't have that information available.'"
```

**Strategy 2: Explicit Citation**

```
Prompt:
"For each fact you state, include [Source: tool_name] to show where it came from.

Example:
'The recipe takes 20 minutes [Source: recipe_database] and serves 4 people
[Source: recipe_database].'"
```

**Strategy 3: Structured Outputs**

```python
from pydantic import BaseModel

class RecipeResponse(BaseModel):
    name: str
    cook_time_minutes: int
    servings: int
    # Only fields from tool schema = only substantiated facts
```

### Detection: Evaluate Substantiation

**Manual Evaluation:**
1. Read conversation with tool outputs
2. For each factual claim, check if it's in tool output
3. Label PASS (substantiated) or FAIL (unsubstantiated)
4. Use for ground truth creation (see Lesson 4 pipeline)

**Automated Evaluation (LLM-as-Judge):**
1. Create ground truth labels (manual or GPT-4o)
2. Develop judge prompt for substantiation detection
3. Measure TPR/TNR on test set
4. Apply to production logs with bias correction

**See:** [Judge Evaluation Pipeline Tutorial](judge_evaluation_pipeline_tutorial.ipynb)

---

## Common Pitfalls

### Evaluation Pitfalls

#### 1. Too Strict (False Negatives)
**❌ Problem:** Marking valid paraphrases as unsubstantiated

```
Tool: {"cook_time": 20}
Response: "Takes about 20 minutes"
Overly Strict Judge: FAIL (says "about", not exact)
Correct: PASS (paraphrase is substantiated)
```

**✅ Solution:** Define acceptable paraphrasing in judge prompt

#### 2. Too Lenient (False Positives)
**❌ Problem:** Accepting embellishments as substantiated

```
Tool: {"name": "Pasta"}
Response: "Delicious homemade pasta"
Overly Lenient Judge: PASS (pasta is mentioned)
Correct: FAIL ("delicious" and "homemade" unsubstantiated)
```

**✅ Solution:** Explicitly list unacceptable additions (adjectives, assumptions)

#### 3. Ignoring Tool Metadata
**❌ Problem:** Failing to recognize tool capabilities as substantiated

```
Available tools: search_recipes(), get_nutrition_info()
Response: "I can look up nutritional information"
Wrong Judge: FAIL (not in tool outputs)
Correct: PASS (tool capability exists)
```

**✅ Solution:** Include tool metadata in evaluation context

#### 4. Inconsistent Courtesy Handling
**❌ Problem:** Treating courtesy differently across examples

```
"How can I help?" → PASS
"Let me search for that" → FAIL
Both are courtesy statements, should be consistent
```

**✅ Solution:** Define courtesy statement rules in judge prompt

---

## Key Takeaways

- ✅ **Substantiation = verifiability from available sources** - Not just factual correctness
- ✅ **Tool grounding prevents hallucination** - Constrain responses to tool outputs
- ✅ **Four substantiation sources** - User input, tool outputs, tool metadata, derivable information
- ✅ **Descriptive embellishment is the #1 failure mode** - LLMs love adding adjectives
- ✅ **Prevention > Detection** - Design prompts to constrain to substantiated facts
- ✅ **LLM-as-Judge scales substantiation evaluation** - Use Lesson 4 pipeline for automation
- ✅ **Critical for customer-facing systems** - False claims damage trust and create legal risk
- ✅ **Define courtesy rules upfront** - Decide how to handle conversational statements

---

## Further Reading

### Related Tutorials
- [Data Preprocessing Tutorial](data_preprocessing_tutorial.md) - Convert logs to structured format
- [Parallel Labeling Tutorial](parallel_labeling_tutorial.ipynb) - Create ground truth at scale
- [Judge Evaluation Pipeline](judge_evaluation_pipeline_tutorial.ipynb) - Automated substantiation detection
- [Lesson 4 Explanation](EXPLANATION.md) - Comprehensive lesson overview

### Methodological Background
- **Retrieval-Augmented Generation (RAG)**: Grounding LLM outputs in retrieved documents
- **Fact-Checking**: Verifying claims against trusted sources
- **Hallucination Detection**: Broader research on LLM factual errors

### Course Materials
- [Lesson 4 Tutorial Index](TUTORIAL_INDEX.md) - Complete learning path
- [HW3: LLM-as-Judge](../homeworks/hw3/llm_judge_concepts.md) - Judge evaluation methodology
- [AI Evaluation Complete Guide](../AI_EVALUATION_COMPLETE_GUIDE.md) - Section on substantiation

### Code References
- [clean_logs.py](clean_logs.py) - Data preprocessing for substantiation evaluation
- [label_substantiation.py](label_substantiation.py) - Ground truth creation with GPT-4o
- [judge_substantiation.py](judge_substantiation.py) - Judge evaluation with TPR/TNR metrics

---

**Tutorial Status:** ✅ Complete
**Last Updated:** 2025-10-30
**Maintainer:** AI Evaluation Course Team
