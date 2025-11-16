# ReAct & Reflexion: Self-Correcting Agent Patterns

**Reading Time:** 20-25 minutes
**Prerequisites:** [Agent Planning Evaluation](./agent_planning_evaluation.md), [HW5: Agent Failure Analysis](../homeworks/hw5/TUTORIAL_INDEX.md)
**Next Steps:** [Multi-Agent Orchestration](./multi_agent_orchestration.md), [ReAct Agent Implementation Notebook](./react_agent_implementation.ipynb)

---

## Table of Contents

1. [Introduction](#introduction)
2. [The ReAct Pattern: Reasoning + Acting](#the-react-pattern-reasoning--acting)
3. [ReAct Loop: Thought → Action → Observation](#react-loop-thought--action--observation)
4. [Implementing ReAct Agents](#implementing-react-agents)
5. [The Reflexion Pattern: Learning from Failures](#the-reflexion-pattern-learning-from-failures)
6. [Self-Reflection and Memory](#self-reflection-and-memory)
7. [Evaluating ReAct Agent Performance](#evaluating-react-agent-performance)
8. [Measuring Reflection Quality](#measuring-reflection-quality)
9. [When to Use ReAct vs Reflexion](#when-to-use-react-vs-reflexion)
10. [Cost and Latency Trade-offs](#cost-and-latency-trade-offs)
11. [Common Pitfalls](#common-pitfalls)
12. [Real-World Applications](#real-world-applications)

---

## Introduction

Traditional LLM agents generate a complete plan upfront, then execute all steps sequentially. But what if step 3 reveals that step 1's assumption was wrong? The agent is stuck with an invalid plan.

**ReAct (Reasoning + Acting)** and **Reflexion** are agent design patterns that interleave reasoning with execution, allowing agents to:
- Adapt plans dynamically based on intermediate results
- Self-correct when actions fail or produce unexpected outputs
- Learn from past failures through structured reflection
- Improve success rates through iterative refinement

In this tutorial, you'll learn:
- How the ReAct loop (Thought → Action → Observation) enables dynamic planning
- When ReAct outperforms static planning approaches
- How Reflexion adds self-reflection and memory to agents
- Techniques for evaluating ReAct agent performance and reflection quality
- Trade-offs between plan-then-execute vs iterative execution patterns

---

## The ReAct Pattern: Reasoning + Acting

**ReAct** is an agent pattern that interleaves **reasoning traces** (thoughts) with **action execution** in a loop, allowing the agent to dynamically adjust its behavior based on observations.

### Core Concept

Instead of:
```
Plan → Execute All Actions → Observe Final Result
```

ReAct does:
```
Think → Act → Observe → Think → Act → Observe → ... → Answer
```

### Why ReAct Works

**Problem with Static Planning:**
```python
# Agent generates full plan upfront
User: "Find Italian recipes with ingredients I have"

Plan:
1. search_recipes(cuisine="Italian")
2. get_user_pantry()
3. filter_by_ingredients(recipes, pantry_items)

# Problem: Step 1 might return 500 recipes
# Much better to get pantry first, then search with constraints!
```

**ReAct Approach:**
```python
Thought 1: "I need to know what ingredients the user has first"
Action 1: get_user_pantry()
Observation 1: pantry = ["tomatoes", "pasta", "garlic", "basil"]

Thought 2: "Now I can search for Italian recipes using these ingredients"
Action 2: search_recipes(cuisine="Italian", ingredients=["tomatoes", "pasta", "garlic", "basil"])
Observation 2: Found 12 recipes matching constraints

Thought 3: "I have manageable results, let me format and return them"
Action 3: format_response(recipes)
Observation 3: Response formatted

Answer: [12 Italian recipes using user's ingredients]
```

**Key Advantage:** Agent adapts plan based on what it learns at each step.

---

## ReAct Loop: Thought → Action → Observation

The ReAct loop consists of three repeating phases:

### 1. Thought (Reasoning Trace)

**Definition:** Internal reasoning about what to do next based on current state.

**Example Thoughts:**
```
"I need to check if the user has dietary restrictions before searching"
"The search returned 0 results, I should try a broader query"
"I have the recipe details, now I need to check ingredient availability"
"This tool call failed, I should try an alternative approach"
```

**Implementation:**
```python
def generate_thought(self, state: dict) -> str:
    """Generate reasoning trace for next action.

    Args:
        state: Current agent state (history, observations)

    Returns:
        Reasoning trace explaining next step
    """
    prompt = f"""
You are a recipe search agent. Based on the conversation so far, what should you do next?

Conversation History:
{state['history']}

Previous Observations:
{state['observations']}

Think step-by-step:
1. What information do I have?
2. What information do I need?
3. What action should I take next?
4. Why is this the right next step?

Your reasoning:
"""
    response = self.llm.complete(prompt)
    return response.strip()
```

### 2. Action (Tool Execution)

**Definition:** Execute a single tool call based on the thought.

**Action Types:**
- **Information gathering:** `get_user_preferences()`, `search_recipes()`
- **State modification:** `add_to_cart()`, `save_recipe()`
- **External queries:** `check_ingredient_availability()`, `get_nutrition_info()`
- **Termination:** `provide_answer()`, `request_clarification()`

**Implementation:**
```python
def select_and_execute_action(self, thought: str, state: dict) -> dict:
    """Select action based on thought and execute it.

    Args:
        thought: Reasoning trace
        state: Current agent state

    Returns:
        Action result with observation
    """
    # Generate action from thought
    action = self._thought_to_action(thought, state)

    # Validate action
    if not self._validate_action(action):
        return {
            "action": action,
            "status": "invalid",
            "observation": f"Action validation failed: {action}"
        }

    # Execute action
    try:
        result = self._execute_tool(action["tool"], action["args"])
        return {
            "action": action,
            "status": "success",
            "observation": result
        }
    except Exception as e:
        return {
            "action": action,
            "status": "error",
            "observation": f"Execution failed: {str(e)}"
        }
```

### 3. Observation (Action Result)

**Definition:** Outcome of the action execution, which informs the next thought.

**Observation Types:**
- **Success with data:** `Found 15 recipes`, `User prefers vegan diet`
- **Success with no results:** `0 recipes found`, `Ingredient not in stock`
- **Partial success:** `Found 2 recipes, but missing nutrition data for 1`
- **Failure:** `Database connection timeout`, `Invalid search parameters`

**Implementation:**
```python
def process_observation(self, observation: dict, state: dict) -> dict:
    """Process observation and update state.

    Args:
        observation: Result from action execution
        state: Current agent state

    Returns:
        Updated state with observation integrated
    """
    # Add observation to history
    state["observations"].append({
        "step": state["step_count"],
        "action": observation["action"],
        "result": observation["observation"],
        "status": observation["status"]
    })

    # Update state based on observation
    if observation["status"] == "success":
        state["data"].update(observation.get("data", {}))
    elif observation["status"] == "error":
        state["errors"].append(observation["observation"])

    state["step_count"] += 1

    # Check termination conditions
    if self._should_terminate(state):
        state["done"] = True

    return state
```

---

## Implementing ReAct Agents

### Complete ReAct Agent Template

```python
from typing import Any, Optional
from dataclasses import dataclass, field

@dataclass
class ReActState:
    """State for ReAct agent execution."""
    query: str
    history: list[dict] = field(default_factory=list)
    observations: list[dict] = field(default_factory=list)
    data: dict = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    step_count: int = 0
    max_steps: int = 10
    done: bool = False

class ReActAgent:
    """ReAct agent with Thought-Action-Observation loop.

    Implements the ReAct pattern for dynamic agent planning
    with iterative refinement based on observations.
    """

    def __init__(
        self,
        llm_model: str = "gpt-4o-mini",
        max_steps: int = 10,
        tools: list[dict] = None
    ):
        """Initialize ReAct agent.

        Args:
            llm_model: LLM model for reasoning
            max_steps: Maximum iterations before timeout
            tools: Available tools for agent

        Raises:
            TypeError: If tools is not a list
            ValueError: If max_steps < 1
        """
        if tools is not None and not isinstance(tools, list):
            raise TypeError("tools must be a list")
        if max_steps < 1:
            raise ValueError("max_steps must be positive")

        self.llm_model = llm_model
        self.max_steps = max_steps
        self.tools = tools or []

    def run(self, query: str) -> dict[str, Any]:
        """Run ReAct loop until completion or max steps.

        Args:
            query: User query

        Returns:
            Final result with trajectory and answer

        Raises:
            ValueError: If query is empty
        """
        # Input validation
        if not query or not query.strip():
            raise ValueError("query cannot be empty")

        # Initialize state
        state = ReActState(query=query, max_steps=self.max_steps)

        # ReAct loop
        while not state.done and state.step_count < state.max_steps:
            # Phase 1: Generate Thought
            thought = self._generate_thought(state)
            state.history.append({"type": "thought", "content": thought})

            # Check if agent wants to terminate
            if self._is_final_answer(thought):
                answer = self._extract_answer(thought)
                state.done = True
                state.history.append({"type": "answer", "content": answer})
                break

            # Phase 2: Select and Execute Action
            action_result = self._execute_action(thought, state)
            state.history.append({
                "type": "action",
                "tool": action_result["tool"],
                "args": action_result["args"]
            })

            # Phase 3: Process Observation
            observation = action_result["observation"]
            state.observations.append({
                "step": state.step_count,
                "observation": observation,
                "status": action_result["status"]
            })
            state.history.append({"type": "observation", "content": observation})

            # Update state
            state.step_count += 1

            # Check for errors
            if action_result["status"] == "error":
                state.errors.append(observation)
                # Agent can recover from errors in next iteration

        # Return final result
        return {
            "query": query,
            "answer": self._get_final_answer(state),
            "trajectory": state.history,
            "steps": state.step_count,
            "success": state.done and len(state.errors) == 0,
            "errors": state.errors
        }

    def _generate_thought(self, state: ReActState) -> str:
        """Generate reasoning trace for next action."""
        prompt = f"""
You are a helpful recipe assistant using ReAct (Reasoning + Acting) pattern.

Query: {state.query}

Available Tools:
{self._format_tools()}

Previous Steps:
{self._format_history(state.history)}

Think step-by-step about what to do next:
1. What have I learned so far?
2. What do I still need to know?
3. What action should I take next?
4. OR, do I have enough information to answer?

If you can answer, start with "Final Answer:"
Otherwise, explain your reasoning and propose the next action.

Your thought:
"""
        response = self._call_llm(prompt)
        return response.strip()

    def _execute_action(self, thought: str, state: ReActState) -> dict:
        """Select action from thought and execute it."""
        # Parse action from thought
        action = self._parse_action_from_thought(thought)

        if not action:
            return {
                "tool": "none",
                "args": {},
                "status": "error",
                "observation": "Failed to parse valid action from thought"
            }

        # Execute tool
        try:
            result = self._call_tool(action["tool"], action["args"])
            return {
                "tool": action["tool"],
                "args": action["args"],
                "status": "success",
                "observation": result
            }
        except Exception as e:
            return {
                "tool": action["tool"],
                "args": action["args"],
                "status": "error",
                "observation": f"Tool execution failed: {str(e)}"
            }

    def _is_final_answer(self, thought: str) -> bool:
        """Check if thought contains final answer."""
        return thought.lower().startswith("final answer:")

    def _extract_answer(self, thought: str) -> str:
        """Extract answer from final thought."""
        return thought.split("Final Answer:", 1)[1].strip()

    def _get_final_answer(self, state: ReActState) -> str:
        """Get final answer from state history."""
        for item in reversed(state.history):
            if item["type"] == "answer":
                return item["content"]

        # If no answer found, agent hit max steps
        return "Unable to complete task within maximum steps"
```

### Example ReAct Trajectory

**User Query:** "Find vegan pasta recipes I can make in 30 minutes"

```
Step 1:
Thought: "I need to search for recipes matching: vegan, pasta, quick cooking time"
Action: search_recipes(ingredients=["pasta"], dietary_restrictions=["vegan"], max_cook_time=30)
Observation: Found 8 recipes

Step 2:
Thought: "I found 8 recipes. Let me check if any have high ratings"
Action: get_recipe_ratings(recipe_ids=[1,2,3,4,5,6,7,8])
Observation: Ratings: [4.5, 3.2, 4.8, 4.1, 3.9, 4.6, 4.2, 3.5]

Step 3:
Thought: "Recipes 3 and 6 have the highest ratings (4.8 and 4.6). I have enough information to answer."
Final Answer: "I found 8 vegan pasta recipes under 30 minutes. The top-rated ones are:
1. Creamy Tomato Basil Pasta (4.8★, 25 min)
2. Garlic Spinach Penne (4.6★, 22 min)
Would you like the full recipes?"
```

**Key Observation:** Agent adapted its plan after seeing search results—it didn't pre-plan to check ratings, but decided to after observing 8 results.

---

## The Reflexion Pattern: Learning from Failures

**Reflexion** extends ReAct by adding:
1. **Evaluator:** Assesses agent performance after execution
2. **Self-Reflection:** Analyzes failures and generates improvement strategies
3. **Memory:** Stores reflections for future iterations

### Reflexion Architecture

```
┌─────────────────────────────────────────────┐
│              User Query                     │
└──────────────┬──────────────────────────────┘
               │
               ▼
       ┌───────────────┐
       │  ReAct Agent  │
       │  (Attempt 1)  │
       └───────┬───────┘
               │
               ▼
       ┌───────────────┐
       │   Evaluator   │
       │  (Success?)   │
       └───────┬───────┘
               │
        ┌──────┴──────┐
        │             │
     Success       Failure
        │             │
        ▼             ▼
    ┌────────┐   ┌─────────────┐
    │ Return │   │ Self-Reflect│
    │ Answer │   │  on Failure │
    └────────┘   └──────┬──────┘
                        │
                        ▼
                 ┌──────────────┐
                 │ Store Reflection│
                 │   in Memory    │
                 └──────┬─────────┘
                        │
                        ▼
                 ┌──────────────┐
                 │  ReAct Agent │
                 │  (Attempt 2) │
                 │ + Reflection │
                 └──────────────┘
```

### Key Components

**1. Evaluator**

Determines if agent's answer is correct and satisfies the user's goal.

```python
class ReflexionEvaluator:
    """Evaluates agent performance for Reflexion."""

    def evaluate(self, query: str, answer: str, trajectory: list[dict]) -> dict:
        """Evaluate agent's answer and execution.

        Args:
            query: User query
            answer: Agent's answer
            trajectory: Agent's thought-action-observation history

        Returns:
            Evaluation result with success flag and feedback
        """
        # Evaluate answer correctness
        correctness_score = self._evaluate_answer(query, answer)

        # Evaluate trajectory efficiency
        efficiency_score = self._evaluate_trajectory(trajectory)

        # Overall success
        success = correctness_score >= 0.8 and efficiency_score >= 0.6

        return {
            "success": success,
            "correctness_score": correctness_score,
            "efficiency_score": efficiency_score,
            "feedback": self._generate_feedback(
                success, correctness_score, efficiency_score, trajectory
            )
        }

    def _evaluate_answer(self, query: str, answer: str) -> float:
        """Evaluate answer correctness using LLM judge."""
        prompt = f"""
Query: {query}
Agent Answer: {answer}

Is this answer correct and helpful? Score 0.0-1.0.

Score:
"""
        response = self._call_llm(prompt)
        return float(response.strip())

    def _evaluate_trajectory(self, trajectory: list[dict]) -> float:
        """Evaluate execution efficiency."""
        thought_count = sum(1 for item in trajectory if item["type"] == "thought")
        action_count = sum(1 for item in trajectory if item["type"] == "action")
        error_count = sum(1 for item in trajectory if "error" in str(item).lower())

    # Penalize errors, excessive actions beyond 5, and unacted thoughts
    penalty = (error_count * 0.2)
    + max(0, (action_count - 5) * 0.05) 
    + max(0, (thought_count - action_count) * 0.05)
    efficiency = 1.0 - penalty
    return max(0.0, min(1.0, efficiency))
```

**2. Self-Reflection Generator**

Analyzes failures and generates actionable improvements.

```python
class SelfReflectionGenerator:
    """Generates self-reflections for failed agent attempts."""

    def generate_reflection(
        self,
        query: str,
        trajectory: list[dict],
        evaluation: dict
    ) -> str:
        """Generate reflection on agent failure.

        Args:
            query: User query
            trajectory: Agent's execution history
            evaluation: Evaluator feedback

        Returns:
            Reflection text with failure analysis and improvement strategy
        """
        prompt = f"""
You are analyzing a failed agent execution to learn from mistakes.

Query: {query}

Agent Trajectory:
{self._format_trajectory(trajectory)}

Evaluation Feedback:
{evaluation['feedback']}

Analyze the failure:
1. What went wrong?
2. Which action or thought was incorrect?
3. What should the agent have done instead?
4. Concrete improvement for next attempt

Reflection:
"""
        reflection = self._call_llm(prompt)
        return reflection.strip()

    def _format_trajectory(self, trajectory: list[dict]) -> str:
        """Format trajectory for reflection prompt."""
        formatted = []
        for i, item in enumerate(trajectory):
            if item["type"] == "thought":
                formatted.append(f"Thought {i}: {item['content']}")
            elif item["type"] == "action":
                formatted.append(f"Action {i}: {item['tool']}({item['args']})")
            elif item["type"] == "observation":
                formatted.append(f"Observation {i}: {item['content']}")
        return "\n".join(formatted)
```

**3. Memory Integration**

Stores reflections and provides them to agent in future attempts.

```python
class ReflexionMemory:
    """Memory system for Reflexion pattern."""

    def __init__(self, max_reflections: int = 5):
        """Initialize memory with capacity limit."""
        self.reflections: list[dict] = []
        self.max_reflections = max_reflections

    def add_reflection(
        self,
        query: str,
        reflection: str,
        attempt_number: int
    ) -> None:
        """Store reflection from failed attempt."""
        self.reflections.append({
            "query": query,
            "reflection": reflection,
            "attempt": attempt_number,
            "timestamp": time.time()
        })

        # Keep only recent reflections
        if len(self.reflections) > self.max_reflections:
            self.reflections = self.reflections[-self.max_reflections:]

    def get_relevant_reflections(self, query: str, k: int = 3) -> list[str]:
        """Retrieve reflections relevant to current query."""
        # Simple approach: return k most recent
        # Advanced: semantic similarity search
        recent = self.reflections[-k:] if len(self.reflections) >= k else self.reflections
        return [r["reflection"] for r in recent]

    def format_for_prompt(self, reflections: list[str]) -> str:
        """Format reflections for inclusion in agent prompt."""
        if not reflections:
            return ""

        formatted = "Past Reflections (learn from these):\n"
        for i, reflection in enumerate(reflections, 1):
            formatted += f"\n{i}. {reflection}\n"
        return formatted
```

---

## Self-Reflection and Memory

### How Reflections Improve Agent Performance

**Example: Recipe Search Agent**

**Attempt 1 (Failure):**
```
Thought: "I'll search for recipes first"
Action: search_recipes(cuisine="Italian")
Observation: Found 500 recipes
Thought: "Too many results, I can't process these"
Final Answer: "Sorry, search returned too many results"

Evaluation: FAIL (didn't ask about user preferences first)
Reflection: "I should have checked user preferences and dietary restrictions
before searching. Starting with a broad search led to overwhelming results.
Next time: get_user_preferences() FIRST, then search with constraints."
```

**Attempt 2 (Success with Reflection):**
```
Memory provides: "Get user preferences FIRST before searching"

Thought: "Based on past reflection, I should check user preferences first"
Action: get_user_preferences()
Observation: User prefers vegetarian, Italian cuisine, <30 min cook time

Thought: "Now I can search with specific constraints"
Action: search_recipes(
    cuisine="Italian",
    dietary_restrictions=["vegetarian"],
    max_cook_time=30
)
Observation: Found 12 recipes

Thought: "Manageable results! I can provide these to the user"
Final Answer: "I found 12 vegetarian Italian recipes under 30 minutes..."

Evaluation: SUCCESS
```

### Memory Strategies

**1. Short-Term Memory (Current Session)**
```python
# Store only reflections from current query execution
short_term = []
for attempt in range(max_attempts):
    result = agent.run(query)
    if not result["success"]:
        reflection = generate_reflection(result)
        short_term.append(reflection)
        # Use in next attempt
```

**2. Long-Term Memory (Cross-Session)**
```python
# Persist reflections to database for future sessions
class PersistentMemory:
    def __init__(self, db_path: str):
        self.db = connect(db_path)

    def store(self, reflection: dict) -> None:
        self.db.insert("reflections", reflection)

    def retrieve_similar(self, query: str, k: int = 3) -> list[str]:
        # Semantic search for relevant past reflections
        query_embedding = embed(query)
        similar = self.db.search_by_embedding(query_embedding, k)
        return [r["reflection"] for r in similar]
```

**3. Episodic Memory (Task-Specific)**
```python
# Store reflections grouped by task type
memory = {
    "recipe_search": [...],
    "nutrition_lookup": [...],
    "ingredient_substitution": [...]
}

def get_task_reflections(task_type: str) -> list[str]:
    return memory.get(task_type, [])
```

---

## Evaluating ReAct Agent Performance

### Key Metrics

**1. Success Rate**
```python
def calculate_success_rate(results: list[dict]) -> float:
    """Calculate percentage of successful task completions."""
    successes = sum(1 for r in results if r["success"])
    return successes / len(results)
```

**2. Average Steps to Success**
```python
def calculate_avg_steps(results: list[dict]) -> float:
    """Calculate mean steps taken for successful completions."""
    successful = [r for r in results if r["success"]]
    if not successful:
        return 0.0
    return sum(r["steps"] for r in successful) / len(successful)
```

**3. First-Attempt Success Rate** (for Reflexion)
```python
def calculate_first_attempt_rate(results: list[dict]) -> float:
    """Calculate success rate on first attempt (no reflection needed)."""
    first_attempts = [r for r in results if r["attempt"] == 1]
    successes = sum(1 for r in first_attempts if r["success"])
    return successes / len(first_attempts) if first_attempts else 0.0
```

**4. Reflection Utility**
```python
def calculate_reflection_improvement(results: list[dict]) -> float:
    """Measure improvement from attempt 1 to attempt 2+ with reflection."""
    first_attempt_success = [r for r in results if r["attempt"] == 1 and r["success"]]
    later_attempt_success = [r for r in results if r["attempt"] > 1 and r["success"]]

    first_rate = len(first_attempt_success) / len([r for r in results if r["attempt"] == 1])
    later_rate = len(later_attempt_success) / len([r for r in results if r["attempt"] > 1])

    return later_rate - first_rate  # Positive = reflection helps
```

**5. Efficiency Score**
```python
def calculate_efficiency(trajectory: list[dict]) -> float:
    """Measure agent efficiency (fewer steps = better)."""
    action_count = sum(1 for item in trajectory if item["type"] == "action")
    error_count = sum(1 for item in trajectory if "error" in str(item).lower())
    redundant_count = count_redundant_actions(trajectory)

    # Penalty for errors and redundancy
    efficiency = 1.0 - (error_count * 0.2) - (redundant_count * 0.1)
    return max(0.0, efficiency)
```

---

## Measuring Reflection Quality

### Criteria for Good Reflections

**1. Specificity**
```
Bad:  "The agent made a mistake"
Good: "The agent should have called get_user_preferences() before search_recipes()
       to avoid returning 500 irrelevant results"
```

**2. Actionability**
```
Bad:  "The search was too broad"
Good: "Next time: (1) Get user preferences first, (2) Add dietary_restrictions
       parameter to search, (3) Limit max_results to 20"
```

**3. Causal Analysis**
```
Bad:  "The agent failed to complete the task"
Good: "The failure occurred because search_recipes() returned 0 results.
       This happened because the agent used ingredients=['quinoa', 'kale']
       which are too restrictive. The agent should try broader terms or
       suggest ingredient substitutions."
```

### Reflection Quality Evaluator

```python
class ReflectionQualityEvaluator:
    """Evaluates quality of self-reflections."""

    def evaluate_reflection(self, reflection: str, trajectory: list[dict]) -> dict:
        """Evaluate reflection quality.

        Args:
            reflection: Generated reflection text
            trajectory: Agent's execution history

        Returns:
            Quality scores and feedback
        """
        # 1. Specificity: Does it identify concrete actions?
        specificity = self._measure_specificity(reflection)

        # 2. Actionability: Does it provide clear improvements?
        actionability = self._measure_actionability(reflection)

        # 3. Causal reasoning: Does it explain WHY failure occurred?
        causality = self._measure_causality(reflection, trajectory)

        # 4. Relevance: Is it relevant to actual failure?
        relevance = self._measure_relevance(reflection, trajectory)

        overall = (specificity + actionability + causality + relevance) / 4.0

        return {
            "overall_quality": overall,
            "specificity": specificity,
            "actionability": actionability,
            "causality": causality,
            "relevance": relevance
        }

    def _measure_specificity(self, reflection: str) -> float:
        """Check if reflection mentions specific actions/tools."""
        # Count tool/function mentions
        tool_mentions = len(re.findall(r'\w+\([^)]*\)', reflection))
        # Count specific parameter names
        param_mentions = len(re.findall(r'(\w+)=', reflection))

        score = min(1.0, (tool_mentions + param_mentions) / 3.0)
        return score

    def _measure_actionability(self, reflection: str) -> float:
        """Check if reflection contains actionable next steps."""
        actionable_keywords = [
            "next time", "should", "instead", "use", "call", "try",
            "step 1", "first", "then", "before", "after"
        ]
        matches = sum(1 for keyword in actionable_keywords if keyword.lower() in reflection.lower())
        return min(1.0, matches / 3.0)

    def _measure_causality(self, reflection: str, trajectory: list[dict]) -> float:
        """Check if reflection explains causal relationship."""
        causal_keywords = [
            "because", "caused by", "led to", "resulted in",
            "this happened when", "the reason", "root cause"
        ]
        matches = sum(1 for keyword in causal_keywords if keyword.lower() in reflection.lower())
        return min(1.0, matches / 2.0)
```

---

## When to Use ReAct vs Reflexion

### ReAct (Thought-Action-Observation)

**Use When:**
- ✅ Tasks require dynamic adaptation based on intermediate results
- ✅ Static planning is insufficient (search results unknown upfront)
- ✅ Agent needs to handle unexpected tool outputs gracefully
- ✅ Single attempt is sufficient (no need for retry with learning)

**Don't Use When:**
- ❌ Task has clear, deterministic steps (use static planning)
- ❌ All information available upfront (no need for iterative observation)
- ❌ Cost/latency sensitive (ReAct uses more LLM calls)

### Reflexion (ReAct + Self-Reflection + Memory)

**Use When:**
- ✅ Tasks are complex and failure is expected on first attempt
- ✅ Learning from failures improves success rate significantly
- ✅ Similar tasks repeat across sessions (memory reuse valuable)
- ✅ Cost of reflection is justified by success rate improvement

**Don't Use When:**
- ❌ Tasks are simple (high first-attempt success rate already)
- ❌ Every query is unique (no memory reuse)
- ❌ Cost/latency critical (reflection adds overhead)
- ❌ Failure rate is already <10% (diminishing returns)

### Comparison Table

| Aspect | Static Planning | ReAct | Reflexion |
|--------|----------------|-------|-----------|
| **Planning** | Upfront, complete plan | Iterative, step-by-step | Iterative + learning |
| **Adaptation** | None | Based on observations | Based on observations + past failures |
| **Memory** | None | Short-term (current session) | Short + long-term (cross-session) |
| **LLM Calls** | 1-2 | 3-10 per task | 5-15 per task (includes reflection) |
| **Cost** | $ | $$ | $$$ |
| **Latency** | Fast | Medium | Slower (reflection overhead) |
| **Success Rate** | Baseline | +10-20% | +20-40% |
| **Best For** | Simple, deterministic tasks | Dynamic, uncertain tasks | Complex, repeated tasks |

---

## Cost and Latency Trade-offs

### Cost Analysis

**Static Planning:**
```
Cost = 1 LLM call (plan generation) + tool execution costs
Example: $0.002 per query (GPT-4o-mini)
```

**ReAct:**
```
Cost = N LLM calls (thoughts) + tool execution costs
Where N = number of steps (typically 3-10)
Example: 5 steps × $0.002 = $0.01 per query
5× more expensive than static
```

**Reflexion:**
```
Cost = (Attempt 1 cost) + (Reflection generation) + (Attempt 2 cost with memory)
Example:
  Attempt 1: $0.01 (ReAct with 5 steps)
  Reflection: $0.003 (analysis + learning)
  Attempt 2: $0.008 (fewer steps with reflection guidance)
  Total: $0.021 per query
10× more expensive than static, but succeeds where static fails
```

### Latency Analysis

**Sequential Latency:**
```python
# Static Planning
latency = plan_generation_time + sum(tool_execution_times)
# Example: 0.5s + 2.0s = 2.5s

# ReAct
latency = sum(thought_time + action_time for each step)
# Example: (0.4s + 0.5s) × 5 steps = 4.5s

# Reflexion
latency = attempt_1_time + reflection_time + attempt_2_time
# Example: 4.5s + 1.0s + 3.0s = 8.5s
```

### When Extra Cost is Worth It

**ROI Calculation:**
```python
def calculate_reflexion_roi(
    static_success_rate: float,
    reflexion_success_rate: float,
    static_cost: float,
    reflexion_cost: float,
    task_value: float
) -> float:
    """Calculate ROI of using Reflexion over static planning.

    Args:
        static_success_rate: Success rate with static planning (e.g., 0.6)
        reflexion_success_rate: Success rate with Reflexion (e.g., 0.9)
        static_cost: Cost per query for static planning (e.g., $0.002)
        reflexion_cost: Cost per query for Reflexion (e.g., $0.021)
        task_value: Value of successful task completion (e.g., $1.00)

    Returns:
        ROI multiplier (>1.0 means Reflexion is worth it)
    """
    static_expected_value = static_success_rate * task_value - static_cost
    reflexion_expected_value = reflexion_success_rate * task_value - reflexion_cost

    roi = reflexion_expected_value / static_expected_value
    return roi

# Example
roi = calculate_reflexion_roi(
    static_success_rate=0.65,
    reflexion_success_rate=0.92,
    static_cost=0.002,
    reflexion_cost=0.021,
    task_value=1.00
)
# roi = 1.42 → Reflexion provides 42% better value
```

**Use Reflexion when:**
```
(reflexion_success_rate - static_success_rate) * task_value > (reflexion_cost - static_cost)
```

---

## Common Pitfalls

### Pitfall 1: Infinite Thought Loops

**Problem:** Agent gets stuck thinking without taking action.

**Example:**
```
Thought 1: "I should search for recipes"
Thought 2: "But first I need to know user preferences"
Thought 3: "Actually, maybe I should search first to see what's available"
Thought 4: "No wait, preferences first makes more sense"
... (never executes action)
```

**Fix:** Enforce action after every thought.

```python
if item["type"] == "thought":
    # MUST be followed by action or final answer
    next_item_must_be_action = True
```

### Pitfall 2: Ignoring Observations

**Problem:** Agent generates new thought without incorporating previous observation.

**Example:**
```
Action: search_recipes(cuisine="Italian")
Observation: Found 0 results

Thought: "Now I'll filter by cooking time" ← IGNORES 0 results!
Action: filter_by_cook_time(recipes)  ← Will fail, no recipes to filter
```

**Fix:** Include observations prominently in next thought prompt.

```python
prompt = f"""
IMPORTANT: Your last action returned this observation:
{last_observation}

You MUST acknowledge this observation in your next thought.
What does this mean for your plan?
"""
```

### Pitfall 3: Generic Reflections

**Problem:** Reflections are too vague to improve future attempts.

**Bad Reflection:**
```
"The agent should be more careful and think harder about the problem."
```

**Good Reflection:**
```
"The agent failed because it called search_recipes() with ingredients=['quinoa', 'kale']
which are too restrictive (0 results). Next time:
1. Start with broader search using only cuisine or meal_type
2. If results > 50, THEN add ingredient filters progressively
3. If results = 0, suggest ingredient substitutions rather than failing"
```

**Fix:** Use structured reflection template.

```python
reflection_template = """
FAILURE ANALYSIS:
- Which step failed? {step_number}
- What was the action? {action}
- Why did it fail? {root_cause}

IMPROVEMENT STRATEGY:
1. What should agent do instead? {alternative_action}
2. What information was missing? {missing_info}
3. How to prevent this in future? {prevention_strategy}
"""
```

### Pitfall 4: Not Terminating

**Problem:** Agent doesn't recognize when it has enough information to answer.

**Example:**
```
Step 8: Found recipes, checked ratings, verified ingredients
Step 9: "Let me also check nutritional information"
Step 10: "And also get user reviews"
Step 11: "And also check seasonal availability"
... (keeps adding unnecessary steps)
```

**Fix:** Add termination condition checks.

```python
def should_terminate(state: ReActState) -> bool:
    """Check if agent has sufficient information to answer."""
    # Check if max steps reached
    if state.step_count >= state.max_steps:
        return True

    # Check if goal is achievable with current data
    if has_sufficient_info(state):
        return True

    # Check if stuck (same action repeated)
    if is_looping(state.history):
        return True

    return False
```

---

## Real-World Applications

### Application 1: Recipe Search with Dynamic Constraints

**Scenario:** User asks "Find dinner recipes with what I have"

**ReAct Execution:**
```
Thought 1: "I need to know what ingredients the user has"
Action 1: get_user_pantry()
Observation 1: ["chicken", "rice", "bell peppers", "onion"]

Thought 2: "Good ingredients for dinner. Let me search recipes using these"
Action 2: search_recipes(ingredients=["chicken", "rice", "bell peppers"], meal_type="dinner")
Observation 2: Found 15 recipes

Thought 3: "Manageable results. Let me check cook times since user might want quick meal"
Action 3: get_recipe_details(recipe_ids=[...])
Observation 3: Cook times range from 20-60 minutes

Thought 4: "I'll recommend the 3 quickest recipes"
Final Answer: "I found 15 dinner recipes using your ingredients. Here are the 3 quickest..."
```

**Why ReAct Succeeds:** Agent discovered user had 4 ingredients AFTER first action, then adapted search accordingly. Static planning would have failed (no ingredient knowledge upfront).

### Application 2: Reflexion for Complex Research Tasks

**Scenario:** "Compare nutritional value of quinoa vs rice for diabetics"

**Attempt 1 (Failure):**
```
Action: get_nutrition(food="quinoa")
Observation: Calories: 120, Protein: 4g, Carbs: 21g, Fiber: 3g

Action: get_nutrition(food="rice")
Observation: Calories: 130, Protein: 3g, Carbs: 28g, Fiber: 0.5g

Final Answer: "Quinoa has more protein and fiber than rice"

Evaluation: FAIL (didn't address "for diabetics" - glycemic index crucial!)

Reflection: "I failed because I only compared basic nutrients but ignored glycemic index,
which is critical for diabetics. The query specifically mentioned diabetes, so I should have:
1. Retrieved glycemic index data for both foods
2. Explained impact of GI on blood sugar
3. Mentioned fiber's role in slowing glucose absorption
Next time: look for diabetes-specific metrics when query mentions health conditions."
```

**Attempt 2 (Success with Reflection):**
```
[Memory provides diabetes-specific reflection]

Action: get_glycemic_index(food="quinoa")
Observation: GI = 53 (low)

Action: get_glycemic_index(food="rice")
Observation: GI = 73 (high, white rice)

Action: get_nutrition(food="quinoa")
Action: get_nutrition(food="rice")

Final Answer: "For diabetics, quinoa is significantly better than white rice:
- Quinoa: Low GI (53), high fiber (3g), slower blood sugar rise
- Rice: High GI (73), low fiber (0.5g), rapid blood sugar spike
Quinoa's fiber content helps regulate glucose absorption."

Evaluation: SUCCESS
```

---

## Summary

**Key Takeaways:**

1. **ReAct enables dynamic planning** - Agents adapt based on what they observe
2. **Reflexion adds learning** - Agents improve from failures via self-reflection
3. **Trade-offs exist** - ReAct/Reflexion cost more but succeed more often
4. **Memory is powerful** - Storing reflections improves future performance
5. **Evaluation is essential** - Track success rate, steps, reflection quality

**ReAct Pattern Checklist:**

- ✅ Thought generates reasoning trace before action
- ✅ Action executes single tool call
- ✅ Observation processes result and informs next thought
- ✅ Loop continues until final answer or max steps
- ✅ Agent adapts plan based on observations

**Reflexion Pattern Checklist:**

- ✅ Evaluator assesses attempt success
- ✅ Self-reflection analyzes failures with specificity
- ✅ Memory stores reflections for future attempts
- ✅ Reflections are actionable and causal
- ✅ Performance improves across attempts

**Next Steps:**
- Learn [Multi-Agent Orchestration](./multi_agent_orchestration.md) for coordinating multiple ReAct agents
- Practice with [ReAct Agent Implementation Notebook](./react_agent_implementation.ipynb)
- Explore [Agent Failure Analysis](./agent_failure_analysis.ipynb) to identify improvement opportunities

---

## Further Reading

- **ReAct Paper:** Yao et al., "ReAct: Synergizing Reasoning and Acting in Language Models" (2022)
- **Reflexion Paper:** Shinn et al., "Reflexion: Language Agents with Verbal Reinforcement Learning" (2023)
- **LangChain ReAct:** https://python.langchain.com/docs/modules/agents/agent_types/react
- **Agent Memory Systems:** Vector stores, episodic memory, semantic memory
- **Self-Correction in LLMs:** Constitutional AI, self-refinement techniques
