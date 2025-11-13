# Agent Planning Evaluation: Validating Reasoning Before Execution

**Reading Time:** 22-25 minutes
**Prerequisites:** [Lesson 13: RAG Generation](../lesson-13/TUTORIAL_INDEX.md), [HW5: Agent Failure Analysis](../homeworks/hw5/TUTORIAL_INDEX.md)
**Next Steps:** [ReAct & Reflexion Patterns](./react_reflexion_patterns.md), [Multi-Agent Orchestration](./multi_agent_orchestration.md)

---

## Table of Contents

1. [Introduction](#introduction)
2. [What is Agent Planning?](#what-is-agent-planning)
3. [The Planning Evaluation Challenge](#the-planning-evaluation-challenge)
4. [Planning vs Execution Failures](#planning-vs-execution-failures)
5. [Evaluating Plan Quality](#evaluating-plan-quality)
6. [Goal Decomposition Validation](#goal-decomposition-validation)
7. [Tool Selection Correctness](#tool-selection-correctness)
8. [Argument Generation Quality](#argument-generation-quality)
9. [Plan Completeness and Efficiency](#plan-completeness-and-efficiency)
10. [Practical Implementation](#practical-implementation)
11. [Common Pitfalls](#common-pitfalls)
12. [Real-World Applications](#real-world-applications)

---

## Introduction

Modern AI agents don't just execute predefined workflows—they **plan sequences of actions** to achieve user goals. A recipe chatbot might need to: (1) parse the user's dietary restrictions, (2) search the recipe database, (3) check ingredient availability, and (4) format a response. Each step requires the LLM to reason about what to do next.

**Agent planning evaluation** answers a critical question: *Does the agent generate high-quality plans that will successfully achieve the goal?*

In this tutorial, you'll learn:
- How to distinguish planning failures from execution failures
- Techniques for validating goal decomposition, tool selection, and argument generation
- How to measure plan completeness, correctness, and efficiency
- When to evaluate planning vs. when to evaluate outcomes
- How planning evaluation differs from traditional LLM evaluation

---

## What is Agent Planning?

**Agent planning** is the process by which an LLM decomposes a user goal into a sequence of executable actions (tool calls, API requests, database queries) that will achieve that goal.

### Formal Definition

Given:
- **User Goal** `g`: High-level objective (e.g., "Find vegan pasta recipes")
- **Available Tools** `T = {t₁, t₂, ..., tₙ}`: Set of executable actions
- **Tool Schemas** `S(tᵢ)`: Function signatures with required/optional arguments
- **Current Context** `C`: Conversation history, user profile, system state

The agent must generate a **plan** `P = [a₁, a₂, ..., aₖ]` where each action `aᵢ` is:
1. A valid tool call with correct arguments
2. Executable given current context
3. Contributes to achieving goal `g`

### Example: Recipe Agent Planning

**User Goal:** "I need gluten-free dessert recipes using chocolate and no nuts"

**Available Tools:**
```python
search_recipes(
    ingredients: list[str],
    dietary_restrictions: list[str],
    meal_type: str,
    max_results: int = 10
) -> list[Recipe]

get_user_preferences() -> UserProfile

check_ingredient_availability(ingredient: str) -> bool
```

**Good Plan:**
```python
[
    Action 1: get_user_preferences()
    # Rationale: Check if user has nut allergies or other dietary restrictions

    Action 2: search_recipes(
        ingredients=["chocolate"],
        dietary_restrictions=["gluten-free", "nut-free"],
        meal_type="dessert",
        max_results=5
    )
    # Rationale: Search with all specified constraints

    Action 3: format_response(recipes)
    # Rationale: Present results to user
]
```

**Bad Plan (Planning Failure):**
```python
[
    Action 1: search_recipes(
        ingredients=["chocolate", "nuts"],  # ❌ User said NO nuts
        dietary_restrictions=[],             # ❌ Missing gluten-free constraint
        meal_type="main dish",               # ❌ Wrong meal type (dessert requested)
        max_results=10
    )
]
```

**Why is this a planning failure?**
- Incorrect argument values (included nuts, wrong meal type)
- Missing critical constraint (gluten-free)
- Plan will execute successfully but achieve the wrong goal
- This is **not** a tool execution failure—it's a reasoning failure at the planning stage

---

## The Planning Evaluation Challenge

Unlike traditional LLM evaluation where we compare output text to ground truth, **agent planning evaluation** faces unique challenges:

### Challenge 1: Multiple Valid Plans

**Problem:** Many different plans can achieve the same goal.

**Example:** For "Find Italian recipes," these are all valid:
```python
Plan A: [search_recipes(cuisine="Italian")]

Plan B: [
    get_user_location(),
    search_recipes(cuisine="Italian", region=user_location)
]

Plan C: [
    get_trending_cuisines(),
    search_recipes(cuisine="Italian", sort_by="popularity")
]
```

**Implication:** We can't use exact match—we need criteria-based evaluation.

### Challenge 2: Plan Quality is Contextual

**Problem:** A "good" plan depends on user preferences, system state, and conversation history.

**Example:** Should the agent call `get_user_preferences()` first?
- **If new user:** Yes, essential to understand dietary restrictions
- **If returning user:** Maybe not, preferences already cached
- **If user explicitly stated restrictions:** No, preferences are already known

**Implication:** Planning evaluation must be **context-aware**.

### Challenge 3: Execution Success ≠ Plan Quality

**Problem:** A plan might execute successfully but achieve the wrong goal.

**Example:**
```python
User: "Find recipes I can make with leftover chicken"
Agent Plan: search_recipes(ingredients=["chicken"], meal_type="dessert")
# Executes successfully, but chicken desserts are not what user wanted!
```

**Implication:** We need to evaluate **plan correctness**, not just execution success.

---

## Planning vs Execution Failures

Understanding the distinction between planning and execution failures is critical for targeted improvements.

### Planning Failures (Reasoning Errors)

**Characteristics:**
- Plan is logically incorrect or incomplete
- Agent misunderstands the goal
- Wrong tools selected or wrong arguments generated
- Plan would not achieve goal even if executed perfectly

**Examples:**
- Selecting `search_web()` when `search_recipes()` was available and appropriate
- Forgetting to include user's dietary restriction in search arguments
- Generating invalid JSON that doesn't match tool schema
- Creating a plan with circular dependencies (Action B needs result of Action C, which needs result of Action B)

**Detection Method:** Evaluate plan **before execution** using validation logic or judge LLMs.

### Execution Failures (External Errors)

**Characteristics:**
- Plan is logically sound
- External system error or resource unavailable
- Network timeout, database error, API rate limit

**Examples:**
- Recipe database is down (service unavailable)
- API key expired or invalid credentials
- Search query is valid but returns 0 results (not an error, but unexpected)
- Timeout waiting for web scraping tool

**Detection Method:** Monitor execution status codes, exceptions, timeouts.

### Why This Distinction Matters

**For System Improvement:**
- **Planning failures → Improve prompts, few-shot examples, model reasoning**
- **Execution failures → Improve error handling, retry logic, tool robustness**

**For Evaluation Metrics:**
- **Planning accuracy:** % of plans that are logically correct before execution
- **Execution success rate:** % of logically correct plans that execute successfully
- **End-to-end success rate:** Planning accuracy × Execution success rate

### Real-World Example from HW5

In HW5's agent failure analysis, the 10-state pipeline separates planning states (LLM reasoning) from execution states (tool calls):

**Planning States (LLM reasoning):**
- `PlanToolCalls`: LLM decides which tools to invoke
- `GenCustomerArgs`: LLM constructs customer DB arguments
- `GenRecipeArgs`: LLM constructs recipe search arguments
- `GenWebArgs`: LLM constructs web search arguments

**Execution States (Tool calls):**
- `GetCustomerProfile`: Execute customer DB query
- `GetRecipes`: Execute recipe search
- `GetWebInfo`: Execute web search

**Insight:** If failures cluster in `GenRecipeArgs`, that's a **planning failure** (LLM generates bad arguments). If failures cluster in `GetRecipes`, that's an **execution failure** (database errors or malformed queries).

---

## Evaluating Plan Quality

Plan quality assessment requires multiple evaluation criteria:

### 1. Correctness (Does the plan achieve the goal?)

**Definition:** Will executing this plan achieve the user's stated objective?

**Evaluation Approaches:**

**A. Goal-Plan Alignment (LLM-as-Judge)**
```python
prompt = f"""
User Goal: {user_query}
Agent Plan: {generated_plan}
Available Tools: {tool_schemas}

Does this plan correctly achieve the user's goal?

Scoring Rubric:
- CORRECT (1.0): Plan will achieve goal with all constraints satisfied
- PARTIAL (0.5): Plan achieves main goal but misses constraints or sub-goals
- INCORRECT (0.0): Plan will not achieve goal or achieves wrong goal

Score: [CORRECT/PARTIAL/INCORRECT]
Reasoning: [Explain why]
"""
```

**B. Constraint Satisfaction Check**
```python
def validate_constraints(plan: Plan, user_constraints: list[str]) -> bool:
    """Check if plan satisfies all user-specified constraints."""
    for constraint in user_constraints:
        if not constraint_satisfied(plan, constraint):
            return False
    return True

# Example
user_constraints = ["gluten-free", "dessert", "no nuts"]
plan_satisfies = validate_constraints(agent_plan, user_constraints)
```

### 2. Tool Selection Validity (Are the right tools chosen?)

**Definition:** Did the agent select appropriate tools from the available set?

**Evaluation Approaches:**

**A. Tool Necessity Check**
```python
def validate_tool_selection(plan: Plan, goal: str, tools: list[Tool]) -> dict:
    """Validate that selected tools are necessary and sufficient."""
    selected_tools = [action.tool for action in plan]

    # Check 1: Are all selected tools necessary?
    unnecessary_tools = [t for t in selected_tools if not is_necessary(t, goal)]

    # Check 2: Are any essential tools missing?
    missing_tools = [t for t in tools if is_essential(t, goal) and t not in selected_tools]

    return {
        "valid": len(unnecessary_tools) == 0 and len(missing_tools) == 0,
        "unnecessary": unnecessary_tools,
        "missing": missing_tools
    }
```

**B. Tool Dependency Resolution**
```python
def check_tool_dependencies(plan: Plan) -> bool:
    """Ensure tools are called in valid order respecting dependencies."""
    for i, action in enumerate(plan):
        dependencies = action.tool.requires  # Tools this action depends on
        completed_tools = [plan[j].tool for j in range(i)]

        if not all(dep in completed_tools for dep in dependencies):
            return False  # Dependency not satisfied

    return True
```

**Example:**
```python
# BAD: Tries to search recipes before getting user preferences
Plan: [search_recipes(...), get_user_preferences()]

# GOOD: Gets preferences first, then searches
Plan: [get_user_preferences(), search_recipes(...)]
```

### 3. Argument Quality (Are tool arguments correct?)

**Definition:** Do tool arguments have valid types, values, and satisfy tool schemas?

**Evaluation Approaches:**

**A. Schema Validation**
```python
def validate_arguments(action: Action, schema: ToolSchema) -> dict:
    """Validate action arguments against tool schema."""
    errors = []

    # Check required arguments
    for required_arg in schema.required:
        if required_arg not in action.args:
            errors.append(f"Missing required argument: {required_arg}")

    # Check argument types
    for arg_name, arg_value in action.args.items():
        expected_type = schema.types[arg_name]
        if not isinstance(arg_value, expected_type):
            errors.append(f"{arg_name}: expected {expected_type}, got {type(arg_value)}")

    # Check value constraints
    for arg_name, arg_value in action.args.items():
        constraints = schema.constraints.get(arg_name, [])
        for constraint in constraints:
            if not constraint.validate(arg_value):
                errors.append(f"{arg_name}: constraint violation - {constraint}")

    return {
        "valid": len(errors) == 0,
        "errors": errors
    }
```

**B. Semantic Argument Validation (LLM-as-Judge)**
```python
prompt = f"""
Tool: search_recipes
Schema:
  - ingredients: list[str] (foods to include)
  - dietary_restrictions: list[str] (allergies/diets to respect)
  - meal_type: str (breakfast/lunch/dinner/dessert/snack)

User Query: "{user_query}"
Generated Arguments: {action.args}

Are these arguments semantically correct for the user's intent?

Check:
1. Do ingredient values make sense?
2. Are dietary restrictions correctly extracted from user query?
3. Is meal_type appropriate?
4. Are there any contradictions or missing constraints?

Score: [CORRECT/INCORRECT]
Issues: [List any problems]
"""
```

---

## Goal Decomposition Validation

For complex goals, agents must decompose the goal into sub-goals. This decomposition quality affects overall plan success.

### What is Goal Decomposition?

**Definition:** Breaking a complex goal into smaller, achievable sub-goals that can be accomplished sequentially or in parallel.

**Example:**
```
User Goal: "Plan a week of dinner meals with grocery list"

Sub-Goals:
1. Identify user's dietary preferences and restrictions
2. Generate 7 diverse dinner recipes
3. Extract ingredients from all recipes
4. Consolidate ingredients into shopping list
5. Check for ingredient availability at user's preferred store
6. Format meal plan and grocery list
```

### Evaluating Decomposition Quality

**Criterion 1: Completeness**
- Does the decomposition cover all aspects of the original goal?
- Are any sub-goals missing that would leave the goal partially unachieved?

**Criterion 2: Logical Ordering**
- Are sub-goals ordered correctly with dependencies respected?
- Can sub-goals be executed in the specified order?

**Criterion 3: Non-Redundancy**
- Are there duplicate or overlapping sub-goals?
- Is work being repeated unnecessarily?

**Criterion 4: Granularity**
- Are sub-goals at appropriate level of abstraction?
- Too coarse: Sub-goals are still too complex to execute
- Too fine: Over-decomposition creates unnecessary steps

### Implementation: Decomposition Validator

```python
def validate_goal_decomposition(
    original_goal: str,
    sub_goals: list[str],
    llm_judge: bool = True
) -> dict:
    """Validate quality of goal decomposition.

    Args:
        original_goal: User's high-level objective
        sub_goals: Agent's decomposed sub-goals
        llm_judge: Use LLM for semantic validation

    Returns:
        Validation results with scores and feedback
    """
    results = {
        "completeness_score": 0.0,
        "ordering_score": 0.0,
        "redundancy_score": 0.0,
        "granularity_score": 0.0,
        "issues": []
    }

    # Check completeness using LLM judge
    if llm_judge:
        prompt = f"""
Original Goal: {original_goal}
Sub-Goals: {sub_goals}

Are these sub-goals sufficient to fully achieve the original goal?
List any missing sub-goals.

Response: [YES/NO (missing sub-goals)]
"""
        response = call_llm(prompt)
        results["completeness_score"] = 1.0 if "YES" in response else 0.5
        if "NO" in response:
            results["issues"].append(f"Missing sub-goals: {response}")

    # Check logical ordering (dependency validation)
    for i in range(len(sub_goals) - 1):
        if depends_on(sub_goals[i+1], sub_goals[i]):
            results["ordering_score"] += 1.0
    results["ordering_score"] /= max(len(sub_goals) - 1, 1)

    # Check redundancy (semantic similarity between sub-goals)
    redundant_pairs = []
    for i, sg1 in enumerate(sub_goals):
        for j, sg2 in enumerate(sub_goals[i+1:], i+1):
            similarity = semantic_similarity(sg1, sg2)
            if similarity > 0.85:  # High similarity threshold
                redundant_pairs.append((i, j))

    results["redundancy_score"] = 1.0 - (len(redundant_pairs) / max(len(sub_goals), 1))
    if redundant_pairs:
        results["issues"].append(f"Redundant sub-goals: {redundant_pairs}")

    # Check granularity (sub-goal complexity)
    avg_complexity = sum(estimate_complexity(sg) for sg in sub_goals) / len(sub_goals)
    if 2 <= avg_complexity <= 5:  # Ideal range
        results["granularity_score"] = 1.0
    else:
        results["granularity_score"] = 0.5
        if avg_complexity > 5:
            results["issues"].append("Sub-goals too coarse (high complexity)")
        else:
            results["issues"].append("Sub-goals too fine (over-decomposition)")

    return results
```

---

## Tool Selection Correctness

Selecting the right tools is a critical planning step. Incorrect tool selection leads to plan failure even if arguments are perfect.

### Tool Selection Error Types

**1. Wrong Tool (Alternative Available)**
```python
User: "Find Italian recipes"
Wrong: search_web(query="Italian recipes")  # External web search
Right: search_recipes(cuisine="Italian")     # Internal recipe DB
```

**2. Missing Tool (Required Action Not Taken)**
```python
User: "Find recipes I can make with my allergies"
Wrong: search_recipes(meal_type="dinner")
Right: [
    get_user_allergies(),
    search_recipes(dietary_restrictions=user_allergies)
]
```

**3. Unnecessary Tool (Adds No Value)**
```python
User: "Show me chocolate cake recipes"
Wrong: [
    get_trending_cuisines(),  # ❌ Not relevant to query
    search_recipes(ingredients=["chocolate"], meal_type="dessert")
]
Right: search_recipes(ingredients=["chocolate"], meal_type="dessert")
```

### Implementation: Tool Selection Validator

```python
def validate_tool_selection(
    plan: Plan,
    available_tools: list[Tool],
    goal: str
) -> dict:
    """Evaluate tool selection correctness.

    Args:
        plan: Agent's generated plan
        available_tools: All tools agent could have used
        goal: User's objective

    Returns:
        Validation results with correctness scores
    """
    selected_tools = [action.tool_name for action in plan.actions]

    # 1. Check for wrong tool (better alternative exists)
    wrong_tools = []
    for action in plan.actions:
        better_alternative = find_better_tool(action, available_tools, goal)
        if better_alternative:
            wrong_tools.append({
                "used": action.tool_name,
                "better": better_alternative.name,
                "reason": better_alternative.reason
            })

    # 2. Check for missing essential tools
    essential_tools = identify_essential_tools(goal, available_tools)
    missing_tools = [t for t in essential_tools if t.name not in selected_tools]

    # 3. Check for unnecessary tools
    unnecessary_tools = []
    for action in plan.actions:
        if not contributes_to_goal(action, goal):
            unnecessary_tools.append({
                "tool": action.tool_name,
                "reason": "Does not contribute to goal achievement"
            })

    # Calculate score
    total_issues = len(wrong_tools) + len(missing_tools) + len(unnecessary_tools)
    correctness_score = 1.0 - (total_issues / max(len(selected_tools), 1))

    return {
        "correctness_score": max(correctness_score, 0.0),
        "wrong_tools": wrong_tools,
        "missing_tools": [t.name for t in missing_tools],
        "unnecessary_tools": unnecessary_tools,
        "selected_tools": selected_tools
    }
```

---

## Argument Generation Quality

Even with correct tool selection, bad arguments lead to plan failure.

### Argument Error Types

**1. Type Errors**
```python
search_recipes(max_results="five")  # ❌ Should be int, not str
search_recipes(max_results=5)       # ✅ Correct
```

**2. Value Constraint Violations**
```python
search_recipes(max_results=-10)     # ❌ Must be positive
search_recipes(max_results=5)       # ✅ Valid value
```

**3. Semantic Errors (Valid type, wrong meaning)**
```python
User: "Find vegan recipes"
search_recipes(dietary_restrictions=["vegetarian"])  # ❌ Vegetarian ≠ Vegan
search_recipes(dietary_restrictions=["vegan"])      # ✅ Correct
```

**4. Missing Context**
```python
User: "Find recipes with my saved ingredients"
search_recipes(ingredients=["pasta"])  # ❌ Hardcoded, ignores user context
search_recipes(ingredients=get_user_saved_ingredients())  # ✅ Uses context
```

### Implementation: Argument Quality Evaluator

```python
def evaluate_argument_quality(
    action: Action,
    schema: ToolSchema,
    context: dict
) -> dict:
    """Evaluate quality of generated arguments.

    Args:
        action: Tool call with arguments
        schema: Tool's expected schema
        context: User context and conversation history

    Returns:
        Quality scores and identified issues
    """
    issues = []

    # 1. Schema validation (type and constraints)
    schema_result = validate_arguments(action, schema)
    if not schema_result["valid"]:
        issues.extend(schema_result["errors"])

    # 2. Semantic validation (meaning correctness)
    semantic_issues = validate_semantic_correctness(action, context)
    issues.extend(semantic_issues)

    # 3. Context utilization (uses available context)
    context_issues = check_context_utilization(action, context)
    issues.extend(context_issues)

    # Calculate scores
    type_score = 1.0 if schema_result["valid"] else 0.0
    semantic_score = 1.0 - (len(semantic_issues) / max(len(action.args), 1))
    context_score = 1.0 - (len(context_issues) / max(len(action.args), 1))

    overall_quality = (type_score + semantic_score + context_score) / 3.0

    return {
        "overall_quality": overall_quality,
        "type_score": type_score,
        "semantic_score": semantic_score,
        "context_score": context_score,
        "issues": issues
    }
```

---

## Plan Completeness and Efficiency

### Plan Completeness

**Definition:** A plan is **complete** if executing all actions in sequence will fully achieve the user's goal with all constraints satisfied.

**Incompleteness Examples:**
```python
User: "Find vegan pasta recipes and add ingredients to my shopping list"

Incomplete Plan: [
    search_recipes(ingredients=["pasta"], dietary_restrictions=["vegan"])
]
# ❌ Finds recipes but doesn't add to shopping list

Complete Plan: [
    search_recipes(ingredients=["pasta"], dietary_restrictions=["vegan"]),
    extract_ingredients(recipes),
    add_to_shopping_list(ingredients)
]
# ✅ Achieves both sub-goals
```

### Plan Efficiency

**Definition:** A plan is **efficient** if it achieves the goal with minimal actions and avoids redundant steps.

**Inefficiency Examples:**
```python
# Inefficient: Makes redundant calls
Plan A: [
    get_user_preferences(),
    get_user_dietary_restrictions(),  # ❌ Redundant, already in preferences
    search_recipes(...)
]

# Efficient: Single call gets all needed data
Plan B: [
    get_user_preferences(),  # Includes dietary restrictions
    search_recipes(...)
]
```

### Evaluation Metrics

**1. Completeness Score**
```python
def calculate_completeness(plan: Plan, goal: str) -> float:
    """Calculate plan completeness score."""
    required_sub_goals = extract_sub_goals(goal)
    achieved_sub_goals = [sg for sg in required_sub_goals if plan_achieves(plan, sg)]

    return len(achieved_sub_goals) / len(required_sub_goals)
```

**2. Efficiency Score**
```python
def calculate_efficiency(plan: Plan, goal: str) -> float:
    """Calculate plan efficiency score."""
    optimal_plan_length = estimate_optimal_length(goal)
    actual_plan_length = len(plan.actions)

    # Penalty for longer-than-optimal plans
    if actual_plan_length <= optimal_plan_length:
        return 1.0
    else:
        return optimal_plan_length / actual_plan_length
```

---

## Practical Implementation

### Complete Planning Evaluation Pipeline

```python
from typing import Any
from dataclasses import dataclass

@dataclass
class PlanEvaluationResult:
    """Results from planning evaluation."""
    correctness_score: float
    tool_selection_score: float
    argument_quality_score: float
    completeness_score: float
    efficiency_score: float
    overall_score: float
    issues: list[str]

class PlanningValidator:
    """Validates agent planning quality before execution."""

    def __init__(self, tools: list[Tool], use_llm_judge: bool = True):
        """Initialize planning validator.

        Args:
            tools: Available tools for agent
            use_llm_judge: Use LLM for semantic validation

        Raises:
            TypeError: If tools is not a list
        """
        if not isinstance(tools, list):
            raise TypeError("tools must be a list")

        self.tools = tools
        self.use_llm_judge = use_llm_judge

    def evaluate_plan(
        self,
        plan: Plan,
        goal: str,
        context: dict[str, Any]
    ) -> PlanEvaluationResult:
        """Evaluate a generated plan before execution.

        Args:
            plan: Agent's generated plan
            goal: User's objective
            context: Conversation and user context

        Returns:
            Evaluation results with scores and issues

        Raises:
            TypeError: If inputs are invalid types
            ValueError: If plan or goal is empty
        """
        # Input validation
        if not isinstance(goal, str) or not goal.strip():
            raise ValueError("goal must be a non-empty string")

        if not plan or not plan.actions:
            raise ValueError("plan must contain at least one action")

        issues = []

        # 1. Evaluate correctness (goal-plan alignment)
        correctness = self._evaluate_correctness(plan, goal)
        issues.extend(correctness.get("issues", []))

        # 2. Evaluate tool selection
        tool_selection = validate_tool_selection(plan, self.tools, goal)
        issues.extend([f"Tool: {issue}" for issue in tool_selection.get("wrong_tools", [])])

        # 3. Evaluate argument quality
        arg_quality_scores = []
        for action in plan.actions:
            schema = self._get_tool_schema(action.tool_name)
            arg_result = evaluate_argument_quality(action, schema, context)
            arg_quality_scores.append(arg_result["overall_quality"])
            issues.extend(arg_result["issues"])

        argument_quality = sum(arg_quality_scores) / len(arg_quality_scores)

        # 4. Evaluate completeness
        completeness = calculate_completeness(plan, goal)

        # 5. Evaluate efficiency
        efficiency = calculate_efficiency(plan, goal)

        # Calculate overall score (weighted average)
        overall_score = (
            0.30 * correctness.get("score", 0.0) +
            0.25 * tool_selection["correctness_score"] +
            0.25 * argument_quality +
            0.15 * completeness +
            0.05 * efficiency
        )

        return PlanEvaluationResult(
            correctness_score=correctness.get("score", 0.0),
            tool_selection_score=tool_selection["correctness_score"],
            argument_quality_score=argument_quality,
            completeness_score=completeness,
            efficiency_score=efficiency,
            overall_score=overall_score,
            issues=issues
        )
```

---

## Common Pitfalls

### Pitfall 1: Evaluating Execution Instead of Planning

**Problem:** Focusing on whether tools executed successfully rather than whether the plan was logically correct.

**Example:**
```python
# This plan executes successfully but achieves wrong goal
User: "Find vegan recipes"
Plan: search_recipes(meal_type="breakfast")  # Executes ✓, but wrong goal ✗

# Bad evaluation: "Plan succeeded (200 OK status)"
# Good evaluation: "Plan incorrect - missing vegan constraint"
```

**Fix:** Evaluate plan **before execution** using validation logic.

### Pitfall 2: Ignoring Context

**Problem:** Evaluating plans in isolation without considering conversation history or user profile.

**Example:**
```python
User: "Find more recipes like those"  # Refers to previous conversation
Agent Plan: search_recipes(meal_type="dinner")  # ❌ Ignores "like those"

# Context-aware evaluation should flag: "Plan doesn't use conversation history"
```

**Fix:** Pass conversation context to evaluation functions.

### Pitfall 3: Over-Penalizing Valid Alternatives

**Problem:** Marking plans as incorrect when they're just different from expected plan.

**Example:**
```python
User: "Find Italian recipes"

Plan A: search_recipes(cuisine="Italian")
Plan B: search_recipes(tags=["Italian", "Mediterranean"])

# Both are valid! Don't penalize Plan B just because it's different.
```

**Fix:** Use criteria-based evaluation (correctness, completeness, efficiency) rather than exact matching.

### Pitfall 4: Not Separating Planning from Execution Metrics

**Problem:** Mixing planning accuracy with execution success rate, making it hard to identify root causes.

**Example:**
```python
# Bad: Combined metric
success_rate = successful_executions / total_queries  # 65%
# Is this low because of bad plans or bad execution?

# Good: Separate metrics
planning_accuracy = correct_plans / total_queries      # 85%
execution_success = successful_executions / correct_plans  # 76%
overall_success = planning_accuracy * execution_success  # 65%

# Now we know: Planning is good, execution needs improvement
```

**Fix:** Track planning and execution metrics separately.

---

## Real-World Applications

### Application 1: Recipe Chatbot Agent

**Scenario:** User asks "Find healthy dinner recipes I can make quickly"

**Planning Evaluation:**
```python
User Goal: Find healthy, quick dinner recipes

Agent Plan:
1. search_recipes(
     meal_type="dinner",
     tags=["healthy", "quick"],
     max_cook_time=30
   )

Evaluation Results:
- Correctness: 1.0 (achieves goal)
- Tool Selection: 1.0 (correct tool)
- Argument Quality: 1.0 (all constraints captured)
- Completeness: 1.0 (single-step plan sufficient)
- Efficiency: 1.0 (minimal actions)
Overall: 1.0 (excellent plan)
```

### Application 2: Multi-Step Research Agent

**Scenario:** User asks "Compare nutritional value of quinoa vs rice"

**Planning Evaluation:**
```python
User Goal: Compare nutritional profiles of two ingredients

Agent Plan:
1. search_ingredient_nutrition(ingredient="quinoa")
2. search_ingredient_nutrition(ingredient="rice")
3. compare_nutrients(ingredient_a="quinoa", ingredient_b="rice")
4. format_comparison_table(comparison_result)

Evaluation Results:
- Correctness: 1.0 (achieves goal)
- Tool Selection: 1.0 (all tools necessary)
- Argument Quality: 0.9 (minor: "rice" is ambiguous - white/brown?)
- Completeness: 1.0 (covers all sub-goals)
- Efficiency: 1.0 (no redundant steps)
Overall: 0.98 (near-perfect plan, clarify rice type)
```

### Application 3: Conversational Shopping Assistant

**Scenario:** User asks "Add ingredients for those pasta recipes to my cart"

**Planning Evaluation:**
```python
User Goal: Add ingredients from previously discussed recipes to shopping cart

Agent Plan:
1. get_conversation_history(turns=5)
2. extract_recipes_from_history(history)
3. extract_ingredients(recipes)
4. add_to_cart(ingredients)

Evaluation Results:
- Correctness: 1.0 (achieves goal with context)
- Tool Selection: 1.0 (correct tools, respects dependencies)
- Argument Quality: 1.0 (uses context correctly)
- Completeness: 1.0 (handles all sub-goals)
- Efficiency: 1.0 (necessary context retrieval)
Overall: 1.0 (excellent context-aware plan)
```

---

## Summary

**Key Takeaways:**

1. **Planning evaluation validates reasoning before execution** - Catch errors at planning stage, not execution stage
2. **Separate planning from execution failures** - Different root causes require different fixes
3. **Use multiple criteria** - Correctness, tool selection, arguments, completeness, efficiency
4. **Context matters** - Plans must be evaluated with conversation history and user profile
5. **Multiple valid plans exist** - Use criteria-based evaluation, not exact matching
6. **Track metrics separately** - Planning accuracy × Execution success = Overall success

**Planning Evaluation Checklist:**

- ✅ Correctness: Does plan achieve the goal?
- ✅ Tool Selection: Are the right tools chosen?
- ✅ Arguments: Are tool arguments valid and semantically correct?
- ✅ Completeness: Does plan achieve all sub-goals?
- ✅ Efficiency: Is plan optimal (no redundant steps)?
- ✅ Context-Aware: Does plan use available context correctly?
- ✅ Dependencies: Are tool calls ordered correctly?

**Next Steps:**
- Learn [ReAct & Reflexion Patterns](./react_reflexion_patterns.md) for iterative planning with self-correction
- Explore [Multi-Agent Orchestration](./multi_agent_orchestration.md) for coordinating multiple planning agents
- Practice with [Agent Planning Interactive Notebook](./react_agent_implementation.ipynb)

---

## Further Reading

- **HW5: Agent Failure Analysis** - State-based transition analysis for agents
- **ReAct Paper** (Yao et al., 2022) - Reasoning + Acting in LLM agents
- **LangGraph Documentation** - Agent planning with state machines
- **AutoGPT/BabyAGI** - Autonomous agent planning systems
- **Tool-Augmented LLMs** - ToolFormer, Gorilla, ToolLLM papers
