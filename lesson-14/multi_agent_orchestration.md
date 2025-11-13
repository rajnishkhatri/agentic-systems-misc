# Multi-Agent Orchestration: Coordinating Specialized Agents

**Reading Time:** 18-22 minutes
**Prerequisites:** [ReAct & Reflexion Patterns](./react_reflexion_patterns.md), [Agent Planning Evaluation](./agent_planning_evaluation.md)
**Next Steps:** [ReAct Agent Implementation Notebook](./react_agent_implementation.ipynb), [Agent Failure Analysis](./agent_failure_analysis.ipynb)

---

## Table of Contents

1. [Introduction](#introduction)
2. [Why Multi-Agent Systems?](#why-multi-agent-systems)
3. [Multi-Agent Architecture Patterns](#multi-agent-architecture-patterns)
4. [Planner-Validator-Executor Pattern](#planner-validator-executor-pattern)
5. [Communication Protocols](#communication-protocols)
6. [Memory Management in Multi-Agent Systems](#memory-management-in-multi-agent-systems)
7. [Memory Strategies: FIFO, Summarization, Reflection](#memory-strategies-fifo-summarization-reflection)
8. [Orchestration Evaluation Metrics](#orchestration-evaluation-metrics)
9. [When to Use Multi-Agent vs Single-Agent](#when-to-use-multi-agent-vs-single-agent)
10. [Common Pitfalls](#common-pitfalls)
11. [Real-World Applications](#real-world-applications)

---

## Introduction

A single ReAct agent can handle many tasks, but complex problems often benefit from **specialization**. Just as software systems use microservices, AI systems can decompose tasks across multiple specialized agents that collaborate.

**Multi-agent orchestration** is the design pattern where multiple LLM agents work together, each with distinct responsibilities, coordinated by an orchestrator that manages communication and memory.

In this tutorial, you'll learn:
- When and why to decompose tasks across multiple agents
- Common multi-agent architecture patterns (Planner-Validator-Executor, Hierarchical, Collaborative)
- Communication protocols for inter-agent messaging
- Memory management strategies (short-term vs long-term, FIFO, summarization, reflection)
- How to evaluate multi-agent system performance
- Trade-offs between single-agent and multi-agent approaches

---

## Why Multi-Agent Systems?

### Problem: Single Agent Complexity

As single agents handle more responsibilities, they become:
- **Overloaded prompts:** "You are a planner AND executor AND validator AND..." (context bloat)
- **Role confusion:** Agent switches between conflicting personas (creative brainstormer ↔ critical validator)
- **Difficult to debug:** Hard to identify which role caused the failure
- **Hard to optimize:** Can't tune prompts for specific sub-tasks independently

### Solution: Specialized Agents

**Decompose** a complex task into specialized agents:

```
Complex Task: "Plan a week of dinners and generate shopping list"

Single Agent:
┌──────────────────────────────────────────┐
│   MegaAgent                              │
│   - Understand user preferences          │
│   - Generate meal ideas                  │
│   - Validate nutrition balance           │
│   - Extract ingredients                  │
│   - Check inventory                      │
│   - Create shopping list                 │
│   - Format output                        │
└──────────────────────────────────────────┘
Prompt: 5000 tokens (overloaded)

Multi-Agent:
┌─────────────┐   ┌──────────────┐   ┌────────────┐   ┌───────────┐
│ PlannerAgent│──▶│ValidatorAgent│──▶│ExecutorAgent──▶│FormatterAgent│
│ (meal ideas)│   │(nutrition OK)│   │(get recipes)│   │(shopping) │
└─────────────┘   └──────────────┘   └────────────┘   └───────────┘
Each Prompt: 800-1500 tokens (focused)
```

**Benefits:**
1. **Specialization:** Each agent optimized for one task (better prompts, fewer tokens)
2. **Modularity:** Replace/upgrade agents independently
3. **Debuggability:** Know which agent failed
4. **Parallel execution:** Independent agents run concurrently
5. **Testability:** Test each agent in isolation

---

## Multi-Agent Architecture Patterns

### Pattern 1: Sequential Pipeline

**Description:** Agents execute in fixed order, each passing output to next.

**Structure:**
```
Input → Agent A → Agent B → Agent C → Output
```

**Example: Recipe Research Pipeline**
```
User Query → [QueryClassifier] → [RetrieverAgent] → [SynthesisAgent] → [ValidatorAgent] → Answer
```

**When to use:**
- ✅ Clear, sequential workflow
- ✅ Each agent depends on previous agent's output
- ✅ No need for backtracking or iteration

**Limitations:**
- ❌ No error recovery (if Agent B fails, can't restart from Agent A)
- ❌ Fixed order (can't adapt pipeline based on intermediate results)

### Pattern 2: Planner-Validator-Executor (PVE)

**Description:** Planner generates plan, Validator checks quality, Executor runs validated plan.

**Structure:**
```
┌─────────┐     ┌───────────┐     ┌──────────┐
│ Planner │────▶│ Validator │────▶│ Executor │
└─────────┘     └─────┬─────┘     └──────────┘
                      │
                 ┌────▼────┐
                 │ REJECT  │
                 │ (retry) │
                 └─────────┘
```

**When to use:**
- ✅ Planning errors are common and costly to execute
- ✅ Plan validation can catch errors before execution
- ✅ Plans have clear correctness criteria

**Example:** See [Planner-Validator-Executor Pattern](#planner-validator-executor-pattern) section below.

### Pattern 3: Hierarchical (Manager-Worker)

**Description:** Manager agent delegates sub-tasks to specialized worker agents.

**Structure:**
```
                ┌─────────────┐
                │ManagerAgent │
                └──────┬──────┘
                       │
         ┌─────────────┼─────────────┐
         │             │             │
    ┌────▼───┐   ┌────▼───┐   ┌────▼───┐
    │Worker A│   │Worker B│   │Worker C│
    │(search)│   │(analyze)│   │(format)│
    └────────┘   └────────┘   └────────┘
```

**When to use:**
- ✅ Task has clear sub-tasks that can be delegated
- ✅ Workers are independent (can run in parallel)
- ✅ Manager needs to coordinate multiple workers

**Example: Research Task**
```
Manager: "Research nutritional comparison of quinoa vs rice"
├─ Worker 1: Get quinoa nutrition data
├─ Worker 2: Get rice nutrition data (parallel)
└─ Worker 3: Generate comparison report (after 1&2 complete)
```

### Pattern 4: Collaborative (Peer-to-Peer)

**Description:** Agents collaborate as equals, contributing different perspectives.

**Structure:**
```
    ┌───────┐
    │Agent A│◀──┐
    └───┬───┘   │
        │       │
    ┌───▼───┐   │
    │Agent B│───┤
    └───┬───┘   │
        │       │
    ┌───▼───┐   │
    │Agent C│───┘
    └───────┘
```

**When to use:**
- ✅ Task benefits from multiple perspectives (e.g., creative brainstorming)
- ✅ No clear hierarchy or fixed order
- ✅ Agents critique and refine each other's outputs

**Example: Recipe Creation**
```
Creative Agent: Proposes novel flavor combinations
Practical Agent: Ensures ingredients are accessible and affordable
Nutrition Agent: Validates nutritional balance
Final Recipe: Consensus from all three perspectives
```

---

## Planner-Validator-Executor Pattern

The **Planner-Validator-Executor (PVE)** pattern separates planning, validation, and execution into specialized agents.

### Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    Orchestrator                          │
└───────┬──────────────────────────┬───────────────────────┘
        │                          │
    ┌───▼──────┐            ┌──────▼──────┐
    │  Planner │            │  Validator  │
    │  Agent   │            │   Agent     │
    └───┬──────┘            └──────┬──────┘
        │                          │
        │  Plan                    │  Validation
        │  ┌─────────────────┐     │  Result
        └─▶│  Shared Memory  │◀────┘
           └────────┬────────┘
                    │
             ┌──────▼──────┐
             │  Executor   │
             │   Agent     │
             └─────────────┘
```

### Agent Responsibilities

**1. Planner Agent**

**Role:** Generate high-level plan to achieve user goal.

**Input:**
- User query
- Available tools
- Conversation history

**Output:**
- Structured plan with steps and tool calls

**Implementation:**
```python
class PlannerAgent:
    """Generates execution plans for user queries."""

    def __init__(self, llm_model: str = "gpt-4o-mini"):
        """Initialize planner agent.

        Args:
            llm_model: LLM for planning

        Raises:
            TypeError: If llm_model is not a string
        """
        if not isinstance(llm_model, str):
            raise TypeError("llm_model must be a string")

        self.llm_model = llm_model

    def plan(self, query: str, tools: list[dict], context: dict) -> dict:
        """Generate execution plan.

        Args:
            query: User query
            tools: Available tools
            context: Conversation context

        Returns:
            Plan with steps and tool calls

        Raises:
            ValueError: If query is empty
        """
        if not query or not query.strip():
            raise ValueError("query cannot be empty")

        prompt = f"""
You are a planning agent. Generate a step-by-step plan to answer this query.

Query: {query}

Available Tools:
{self._format_tools(tools)}

Context:
{context}

Generate a plan with these steps:
1. What information do we need?
2. Which tools to call and in what order?
3. How to synthesize results into final answer?

Output format (JSON):
{{
  "goal": "brief goal description",
  "steps": [
    {{"step": 1, "action": "tool_name", "args": {{}}, "rationale": "why"}},
    ...
  ]
}}

Plan:
"""
        response = self._call_llm(prompt)
        plan = json.loads(response)

        return {
            "plan": plan,
            "planner": "PlannerAgent",
            "timestamp": time.time()
        }
```

**2. Validator Agent**

**Role:** Verify plan correctness before execution.

**Input:**
- Plan from Planner
- Tool schemas
- Validation criteria

**Output:**
- APPROVED or REJECTED with feedback

**Implementation:**
```python
class ValidatorAgent:
    """Validates execution plans before running."""

    def __init__(self, llm_model: str = "gpt-4o-mini"):
        """Initialize validator agent."""
        self.llm_model = llm_model

    def validate(self, plan: dict, tools: list[dict], goal: str) -> dict:
        """Validate plan correctness.

        Args:
            plan: Plan from PlannerAgent
            tools: Available tools with schemas
            goal: User's objective

        Returns:
            Validation result with status and feedback

        Raises:
            TypeError: If plan is not a dict
        """
        if not isinstance(plan, dict):
            raise TypeError("plan must be a dictionary")

        # 1. Schema validation (types, required args)
        schema_result = self._validate_schemas(plan, tools)

        # 2. Goal alignment (will plan achieve goal?)
        goal_result = self._validate_goal_alignment(plan, goal)

        # 3. Tool dependencies (correct ordering?)
        dependency_result = self._validate_dependencies(plan)

        # 4. Efficiency check (unnecessary steps?)
        efficiency_result = self._check_efficiency(plan)

        # Overall validation
        all_valid = all([
            schema_result["valid"],
            goal_result["valid"],
            dependency_result["valid"]
        ])

        status = "APPROVED" if all_valid else "REJECTED"

        return {
            "status": status,
            "schema_validation": schema_result,
            "goal_alignment": goal_result,
            "dependencies": dependency_result,
            "efficiency": efficiency_result,
            "feedback": self._generate_feedback(
                all_valid, schema_result, goal_result, dependency_result
            ),
            "validator": "ValidatorAgent",
            "timestamp": time.time()
        }

    def _validate_goal_alignment(self, plan: dict, goal: str) -> dict:
        """Check if plan will achieve the goal using LLM judge."""
        prompt = f"""
Goal: {goal}

Plan Steps:
{json.dumps(plan['steps'], indent=2)}

Will executing this plan achieve the goal? Consider:
1. Are all sub-goals addressed?
2. Is the plan complete?
3. Are there missing steps?

Response: VALID or INVALID (with reasons)
"""
        response = self._call_llm(prompt)
        is_valid = "VALID" in response.upper()

        return {
            "valid": is_valid,
            "feedback": response,
            "criterion": "goal_alignment"
        }
```

**3. Executor Agent**

**Role:** Execute validated plan and return results.

**Input:**
- Validated plan
- Tool implementations

**Output:**
- Execution results for each step

**Implementation:**
```python
class ExecutorAgent:
    """Executes validated plans."""

    def __init__(self, tools: dict[str, callable]):
        """Initialize executor with available tools.

        Args:
            tools: Dictionary mapping tool names to callable functions

        Raises:
            TypeError: If tools is not a dict
        """
        if not isinstance(tools, dict):
            raise TypeError("tools must be a dictionary")

        self.tools = tools

    def execute(self, plan: dict) -> dict:
        """Execute validated plan.

        Args:
            plan: Validated plan from ValidatorAgent

        Returns:
            Execution results with outcomes for each step

        Raises:
            ValueError: If plan is empty
        """
        if not plan.get("steps"):
            raise ValueError("plan must contain steps")

        results = []
        execution_state = {}

        for step in plan["steps"]:
            step_number = step["step"]
            tool_name = step["action"]
            tool_args = step["args"]

            try:
                # Execute tool
                tool_func = self.tools.get(tool_name)
                if not tool_func:
                    raise ValueError(f"Tool {tool_name} not found")

                result = tool_func(**tool_args)

                results.append({
                    "step": step_number,
                    "status": "success",
                    "result": result,
                    "tool": tool_name
                })

                # Update execution state
                execution_state[f"step_{step_number}_result"] = result

            except Exception as e:
                results.append({
                    "step": step_number,
                    "status": "error",
                    "error": str(e),
                    "tool": tool_name
                })

                # Stop on error (can be made configurable)
                break

        success = all(r["status"] == "success" for r in results)

        return {
            "success": success,
            "results": results,
            "state": execution_state,
            "executor": "ExecutorAgent",
            "timestamp": time.time()
        }
```

### Orchestrator

**Role:** Coordinate agents and manage workflow.

```python
class MultiAgentOrchestrator:
    """Orchestrates Planner-Validator-Executor workflow."""

    def __init__(
        self,
        planner: PlannerAgent,
        validator: ValidatorAgent,
        executor: ExecutorAgent,
        max_retries: int = 2
    ):
        """Initialize orchestrator with agents.

        Args:
            planner: Planning agent
            validator: Validation agent
            executor: Execution agent
            max_retries: Max planning retries on rejection

        Raises:
            ValueError: If max_retries < 1
        """
        if max_retries < 1:
            raise ValueError("max_retries must be at least 1")

        self.planner = planner
        self.validator = validator
        self.executor = executor
        self.max_retries = max_retries
        self.memory = SharedMemory()

    def run(self, query: str, tools: list[dict], context: dict) -> dict:
        """Run PVE workflow.

        Args:
            query: User query
            tools: Available tools
            context: Conversation context

        Returns:
            Final result with plan, validation, execution

        Raises:
            ValueError: If query is empty
        """
        if not query or not query.strip():
            raise ValueError("query cannot be empty")

        attempt = 0
        plan = None
        validation = None

        # Planning loop with validation
        while attempt < self.max_retries:
            # Step 1: Plan
            plan_result = self.planner.plan(query, tools, context)
            plan = plan_result["plan"]
            self.memory.store("plan", plan)

            # Step 2: Validate
            validation = self.validator.validate(plan, tools, query)
            self.memory.store("validation", validation)

            if validation["status"] == "APPROVED":
                break  # Plan approved, proceed to execution

            # Plan rejected, provide feedback for retry
            context["validation_feedback"] = validation["feedback"]
            attempt += 1

        if validation["status"] == "REJECTED":
            return {
                "success": False,
                "error": "Plan validation failed after max retries",
                "validation": validation,
                "plan": plan
            }

        # Step 3: Execute approved plan
        execution = self.executor.execute(plan)
        self.memory.store("execution", execution)

        return {
            "success": execution["success"],
            "plan": plan,
            "validation": validation,
            "execution": execution,
            "memory": self.memory.get_all()
        }
```

---

## Communication Protocols

Agents need to communicate. Common protocols:

### 1. Message Passing

**Description:** Agents send structured messages to each other.

**Message Format:**
```python
{
    "from": "agent_id",
    "to": "agent_id",
    "type": "request" | "response" | "notification",
    "content": {...},
    "timestamp": 1234567890
}
```

**Example:**
```python
# Planner → Validator
{
    "from": "planner_001",
    "to": "validator_001",
    "type": "request",
    "content": {
        "action": "validate_plan",
        "plan": {...}
    }
}

# Validator → Planner
{
    "from": "validator_001",
    "to": "planner_001",
    "type": "response",
    "content": {
        "status": "REJECTED",
        "feedback": "Missing step for user preference retrieval"
    }
}
```

### 2. Shared Memory

**Description:** Agents read/write to common memory store.

**Advantages:**
- ✅ No explicit routing (agents query memory)
- ✅ Asynchronous (agents work at own pace)
- ✅ Persistent (survives agent restarts)

**Example:**
```python
class SharedMemory:
    """Shared memory for multi-agent communication."""

    def __init__(self):
        self.store: dict[str, Any] = {}

    def write(self, key: str, value: Any) -> None:
        """Write value to memory."""
        self.store[key] = {
            "value": value,
            "timestamp": time.time()
        }

    def read(self, key: str) -> Any:
        """Read value from memory."""
        return self.store.get(key, {}).get("value")

    def query(self, pattern: str) -> dict[str, Any]:
        """Query memory with pattern matching."""
        return {k: v for k, v in self.store.items() if pattern in k}
```

### 3. Event Bus

**Description:** Publish-subscribe pattern where agents subscribe to events.

**Example:**
```python
class EventBus:
    """Event bus for agent communication."""

    def __init__(self):
        self.subscribers: dict[str, list[callable]] = {}

    def subscribe(self, event_type: str, callback: callable) -> None:
        """Subscribe to event type."""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)

    def publish(self, event_type: str, data: dict) -> None:
        """Publish event to subscribers."""
        for callback in self.subscribers.get(event_type, []):
            callback(data)

# Usage
bus = EventBus()

# Validator subscribes to "plan_generated" events
bus.subscribe("plan_generated", validator.validate)

# Planner publishes event
bus.publish("plan_generated", {"plan": plan})
```

---

## Memory Management in Multi-Agent Systems

### Memory Types

**1. Short-Term Memory (Working Memory)**

**Lifespan:** Current task/conversation
**Content:** Intermediate results, current plan, recent observations
**Storage:** In-memory dictionary or cache

```python
class ShortTermMemory:
    """Ephemeral memory for current task."""

    def __init__(self, max_items: int = 50):
        self.memory: dict[str, Any] = {}
        self.max_items = max_items

    def store(self, key: str, value: Any) -> None:
        """Store item in short-term memory."""
        if len(self.memory) >= self.max_items:
            # FIFO eviction
            oldest_key = next(iter(self.memory))
            del self.memory[oldest_key]

        self.memory[key] = value

    def retrieve(self, key: str) -> Any:
        """Retrieve item from short-term memory."""
        return self.memory.get(key)

    def clear(self) -> None:
        """Clear short-term memory (end of task)."""
        self.memory.clear()
```

**2. Long-Term Memory (Persistent Memory)**

**Lifespan:** Across tasks/sessions
**Content:** User preferences, learned patterns, historical successes/failures
**Storage:** Database (SQLite, PostgreSQL) or vector store

```python
class LongTermMemory:
    """Persistent memory across sessions."""

    def __init__(self, db_path: str):
        self.db = self._connect_db(db_path)

    def store(self, key: str, value: Any, metadata: dict = None) -> None:
        """Store item in long-term memory with metadata."""
        self.db.execute(
            "INSERT INTO memory (key, value, metadata, timestamp) VALUES (?, ?, ?, ?)",
            (key, json.dumps(value), json.dumps(metadata or {}), time.time())
        )
        self.db.commit()

    def retrieve(self, key: str) -> Any:
        """Retrieve item from long-term memory."""
        cursor = self.db.execute("SELECT value FROM memory WHERE key = ?", (key,))
        row = cursor.fetchone()
        return json.loads(row[0]) if row else None

    def search(self, query: str, limit: int = 10) -> list[dict]:
        """Search memory with semantic similarity."""
        # Use embedding-based search for semantic retrieval
        query_embedding = embed(query)
        results = self.db.search_by_embedding(query_embedding, limit)
        return results
```

**3. Episodic Memory (Task History)**

**Lifespan:** Historical record of past tasks
**Content:** Task traces, outcomes, reflections
**Storage:** Time-indexed logs or event store

```python
class EpisodicMemory:
    """Memory of past task executions."""

    def __init__(self):
        self.episodes: list[dict] = []

    def record_episode(self, task: str, trajectory: list[dict], outcome: dict) -> None:
        """Record completed task episode."""
        self.episodes.append({
            "task": task,
            "trajectory": trajectory,
            "outcome": outcome,
            "timestamp": time.time()
        })

    def retrieve_similar_episodes(self, current_task: str, k: int = 5) -> list[dict]:
        """Retrieve similar past episodes."""
        # Semantic search for similar tasks
        task_embedding = embed(current_task)
        similarities = []

        for episode in self.episodes:
            episode_embedding = embed(episode["task"])
            similarity = cosine_similarity(task_embedding, episode_embedding)
            similarities.append((similarity, episode))

        # Return top k most similar
        similarities.sort(reverse=True, key=lambda x: x[0])
        return [ep for _, ep in similarities[:k]]
```

---

## Memory Strategies: FIFO, Summarization, Reflection

### Strategy 1: FIFO (First-In-First-Out)

**Description:** Keep only N most recent items, discard oldest.

**Use Case:** Short-term memory with limited capacity.

**Implementation:**
```python
from collections import deque

class FIFOMemory:
    """FIFO memory with fixed capacity."""

    def __init__(self, capacity: int = 10):
        """Initialize FIFO memory.

        Args:
            capacity: Maximum items to store

        Raises:
            ValueError: If capacity < 1
        """
        if capacity < 1:
            raise ValueError("capacity must be positive")

        self.memory = deque(maxlen=capacity)

    def add(self, item: dict) -> None:
        """Add item (auto-evicts oldest if full)."""
        self.memory.append(item)

    def get_recent(self, n: int = 5) -> list[dict]:
        """Get n most recent items."""
        return list(self.memory)[-n:]

    def get_all(self) -> list[dict]:
        """Get all items in memory."""
        return list(self.memory)
```

**Pros:**
- ✅ Simple to implement
- ✅ Bounded memory usage
- ✅ Fast retrieval

**Cons:**
- ❌ Loses old but potentially important information
- ❌ No semantic prioritization

### Strategy 2: Summarization

**Description:** Compress old memories into summaries to save space.

**Use Case:** Long conversations where recent details matter but historical context is useful.

**Implementation:**
```python
class SummarizationMemory:
    """Memory with automatic summarization of old items."""

    def __init__(self, recent_count: int = 10, summary_interval: int = 20):
        """Initialize summarization memory.

        Args:
            recent_count: Number of recent items to keep verbatim
            summary_interval: Summarize when this many items accumulate
        """
        self.recent = deque(maxlen=recent_count)
        self.summaries: list[str] = []
        self.summary_interval = summary_interval
        self.pending_for_summary: list[dict] = []

    def add(self, item: dict) -> None:
        """Add item to memory."""
        self.recent.append(item)
        self.pending_for_summary.append(item)

        # Summarize if threshold reached
        if len(self.pending_for_summary) >= self.summary_interval:
            self._create_summary()

    def _create_summary(self) -> None:
        """Create summary of pending items."""
        summary = self._summarize_items(self.pending_for_summary)
        self.summaries.append(summary)
        self.pending_for_summary.clear()

    def _summarize_items(self, items: list[dict]) -> str:
        """Generate summary using LLM."""
        prompt = f"""
Summarize these conversation/task items concisely:

Items:
{json.dumps(items, indent=2)}

Summary (3-5 sentences capturing key information):
"""
        return self._call_llm(prompt).strip()

    def get_context(self) -> str:
        """Get full context (summaries + recent items)."""
        context_parts = []

        # Add historical summaries
        if self.summaries:
            context_parts.append("Historical Summary:")
            context_parts.extend(self.summaries)

        # Add recent items
        context_parts.append("\nRecent Items:")
        for item in self.recent:
            context_parts.append(json.dumps(item))

        return "\n".join(context_parts)
```

**Pros:**
- ✅ Retains historical context
- ✅ Bounded memory usage
- ✅ Recent details preserved

**Cons:**
- ❌ LLM cost for summarization
- ❌ Information loss in summaries
- ❌ Latency when creating summaries

### Strategy 3: Reflection-Based Memory

**Description:** Store reflections and learnings from past experiences.

**Use Case:** Agent improvement over time (similar to Reflexion pattern).

**Implementation:**
```python
class ReflectionMemory:
    """Memory storing reflections for learning."""

    def __init__(self, max_reflections: int = 50):
        """Initialize reflection memory."""
        self.reflections: list[dict] = []
        self.max_reflections = max_reflections

    def add_reflection(self, task: str, outcome: str, reflection: str) -> None:
        """Add reflection from task experience.

        Args:
            task: Task description
            outcome: Success or failure
            reflection: Analysis and learning
        """
        self.reflections.append({
            "task": task,
            "outcome": outcome,
            "reflection": reflection,
            "timestamp": time.time()
        })

        # Keep only recent reflections
        if len(self.reflections) > self.max_reflections:
            self.reflections = self.reflections[-self.max_reflections:]

    def get_relevant_reflections(self, current_task: str, k: int = 3) -> list[str]:
        """Retrieve reflections relevant to current task."""
        # Semantic similarity search
        task_embedding = embed(current_task)
        similarities = []

        for reflection in self.reflections:
            reflection_embedding = embed(reflection["task"])
            similarity = cosine_similarity(task_embedding, reflection_embedding)
            similarities.append((similarity, reflection["reflection"]))

        # Return top k
        similarities.sort(reverse=True, key=lambda x: x[0])
        return [refl for _, refl in similarities[:k]]

    def format_for_prompt(self, reflections: list[str]) -> str:
        """Format reflections for agent prompt."""
        if not reflections:
            return ""

        formatted = "Relevant Past Learnings:\n"
        for i, reflection in enumerate(reflections, 1):
            formatted += f"\n{i}. {reflection}\n"

        return formatted
```

**Pros:**
- ✅ Agents learn from experience
- ✅ Semantic retrieval finds relevant learnings
- ✅ Improves over time

**Cons:**
- ❌ Requires reflection generation (LLM cost)
- ❌ Quality depends on reflection quality
- ❌ Retrieval latency (embedding search)

---

## Orchestration Evaluation Metrics

### 1. Agent-Level Metrics

**Per-agent success rate:**
```python
def calculate_agent_success_rate(agent_results: list[dict]) -> dict[str, float]:
    """Calculate success rate per agent."""
    agent_stats = {}

    for result in agent_results:
        agent_id = result["agent"]
        success = result["success"]

        if agent_id not in agent_stats:
            agent_stats[agent_id] = {"total": 0, "success": 0}

        agent_stats[agent_id]["total"] += 1
        if success:
            agent_stats[agent_id]["success"] += 1

    # Calculate rates
    rates = {}
    for agent_id, stats in agent_stats.items():
        rates[agent_id] = stats["success"] / stats["total"]

    return rates
```

### 2. System-Level Metrics

**End-to-end success rate:**
```python
def calculate_system_success_rate(orchestration_results: list[dict]) -> float:
    """Calculate overall system success rate."""
    successes = sum(1 for r in orchestration_results if r["success"])
    return successes / len(orchestration_results)
```

**Average execution time:**
```python
def calculate_avg_execution_time(orchestration_results: list[dict]) -> float:
    """Calculate mean execution time."""
    times = [r["execution_time"] for r in orchestration_results]
    return sum(times) / len(times)
```

### 3. Communication Efficiency

**Message count per task:**
```python
def calculate_message_efficiency(orchestration_results: list[dict]) -> dict:
    """Measure inter-agent communication."""
    total_messages = sum(len(r["messages"]) for r in orchestration_results)
    avg_messages = total_messages / len(orchestration_results)

    return {
        "total_messages": total_messages,
        "avg_messages_per_task": avg_messages,
        "efficiency_score": 1.0 / avg_messages if avg_messages > 0 else 0.0
    }
```

### 4. Memory Utilization

**Memory growth rate:**
```python
def track_memory_growth(memory_snapshots: list[dict]) -> dict:
    """Track memory usage over time."""
    sizes = [snapshot["size_bytes"] for snapshot in memory_snapshots]

    return {
        "initial_size": sizes[0],
        "final_size": sizes[-1],
        "growth_rate": (sizes[-1] - sizes[0]) / sizes[0],
        "peak_size": max(sizes)
    }
```

---

## When to Use Multi-Agent vs Single-Agent

### Use Single Agent When:

- ✅ Task is simple and well-defined
- ✅ No clear specialization needed
- ✅ Cost/latency critical (fewer LLM calls)
- ✅ Task requires tight reasoning loop (single context)

**Example:** "Find vegan recipes" → Simple search, no need for multiple agents

### Use Multi-Agent When:

- ✅ Task has distinct sub-tasks requiring different skills
- ✅ Separation of concerns improves reliability (e.g., planning validation)
- ✅ Sub-tasks can run in parallel (performance gain)
- ✅ Debugging requires isolating which component failed

**Example:** "Plan a week of meals with nutrition validation and shopping list generation" → Clear specialization (planning, validation, execution)

### Decision Matrix

| Factor | Single Agent | Multi-Agent |
|--------|-------------|-------------|
| **Task Complexity** | Simple | Complex |
| **Specialization** | Generalist | Specialists |
| **Cost** | $ | $$-$$$ |
| **Latency** | Fast | Slower (coordination overhead) |
| **Debuggability** | Hard (monolithic) | Easy (modular) |
| **Testability** | End-to-end only | Per-agent + integration |
| **Scalability** | Limited | High (add agents) |
| **Maintainability** | Hard (large prompts) | Easy (focused agents) |

---

## Common Pitfalls

### Pitfall 1: Over-Decomposition

**Problem:** Creating too many agents for simple tasks.

**Bad:**
```
Task: "Find Italian recipes"

Agents: QueryParser → IntentClassifier → ToolSelector → ParameterExtractor → Executor → Formatter
(6 agents for a 1-step task!)
```

**Good:**
```
Task: "Find Italian recipes"

Agent: SingleSearchAgent (handles entire task)
```

**Fix:** Use multi-agent only when specialization provides clear benefit.

### Pitfall 2: Communication Bottlenecks

**Problem:** Agents spend more time communicating than working.

**Symptom:**
```
Agent A: Sends plan to Agent B
Agent B: Requests clarification from Agent A
Agent A: Sends clarification to Agent B
Agent B: Requests additional info from Agent A
... (more messages than actual work)
```

**Fix:** Use shared memory to reduce message passing overhead.

### Pitfall 3: Memory Leaks

**Problem:** Memory grows unbounded without cleanup.

**Symptom:**
```python
# Memory grows indefinitely
for task in tasks:
    orchestrator.run(task)
    # NEVER clears short-term memory!
```

**Fix:** Clear short-term memory after each task.

```python
for task in tasks:
    orchestrator.run(task)
    orchestrator.memory.clear_short_term()  # ✅ Clean up
```

### Pitfall 4: Agent Conflicts

**Problem:** Agents make conflicting decisions.

**Example:**
```
Creative Agent: "Use truffle oil for luxury flavor"
Budget Agent: "Truffle oil is $50, too expensive"
Nutrition Agent: "Truffle oil adds no nutritional value"

Result: Deadlock (no consensus)
```

**Fix:** Define clear authority hierarchy or arbitration mechanism.

```python
# Prioritize budget constraints
if budget_agent.rejects(ingredient):
    return "rejected"  # Budget veto power
```

---

## Real-World Applications

### Application 1: Recipe Meal Planning System

**Task:** Plan a week of dinners with shopping list.

**Multi-Agent Architecture:**

```
PlannerAgent: Generate 7 dinner ideas based on user preferences
     ↓
ValidatorAgent: Check nutrition balance (protein, variety, no repeats)
     ↓
RecipeRetrieverAgent: Fetch full recipes for approved meals
     ↓
IngredientExtractorAgent: Extract ingredients from all recipes
     ↓
InventoryCheckerAgent: Compare with user's current pantry
     ↓
ShoppingListAgent: Generate shopping list for missing items
     ↓
FormatterAgent: Create formatted meal plan + shopping list
```

**Why Multi-Agent:**
- Each agent specialized (nutrition knowledge ≠ inventory management)
- Validation catches bad plans before expensive retrieval
- Parallel execution possible (recipe retrieval for all 7 meals concurrently)

### Application 2: Research Paper Summarization

**Task:** Summarize academic paper with citation verification.

**Multi-Agent Architecture:**

```
    ┌─────────────────┐
    │ ManagerAgent    │
    └────────┬────────┘
             │
   ┌─────────┼─────────┐
   │         │         │
┌──▼──┐  ┌───▼───┐  ┌──▼──────┐
│PDF  │  │Claim  │  │Citation │
│Parse│  │Extract│  │Validator│
└──┬──┘  └───┬───┘  └──┬──────┘
   │         │         │
   └─────────┼─────────┘
             ▼
      ┌─────────────┐
      │Synthesizer  │
      │   Agent     │
      └─────────────┘
```

**Parallel Workers:**
- PDF Parser: Extract text sections
- Claim Extractor: Identify key claims
- Citation Validator: Verify claim support

**Sequential Synthesizer:**
- Combines results into coherent summary

---

## Summary

**Key Takeaways:**

1. **Multi-agent = Specialization** - Decompose complex tasks across focused agents
2. **Patterns exist** - PVE, hierarchical, collaborative, sequential
3. **Communication matters** - Message passing, shared memory, event bus
4. **Memory strategies** - FIFO, summarization, reflection for different needs
5. **Evaluate holistically** - Agent-level + system-level + communication metrics

**Multi-Agent Orchestration Checklist:**

- ✅ Task complexity justifies multiple agents
- ✅ Clear agent responsibilities defined
- ✅ Communication protocol chosen (messages/memory/events)
- ✅ Memory management strategy selected
- ✅ Orchestrator coordinates workflow
- ✅ Metrics track per-agent and system performance
- ✅ Memory cleanup prevents leaks

**Next Steps:**
- Practice with [ReAct Agent Implementation Notebook](./react_agent_implementation.ipynb)
- Analyze failures in [Agent Failure Analysis Notebook](./agent_failure_analysis.ipynb)
- Review [Agent Planning Evaluation](./agent_planning_evaluation.md) for validation techniques

---

## Further Reading

- **Multi-Agent Papers:** AutoGen, MetaGPT, ChatDev
- **Agent Frameworks:** LangGraph (state-based), CrewAI (role-based), AutoGPT
- **Memory Systems:** MemGPT (memory management), Mem0 (persistent memory)
- **Communication Patterns:** Actor Model, Message Queues, Shared Memory
- **Orchestration:** Workflow engines, DAG schedulers, State machines
