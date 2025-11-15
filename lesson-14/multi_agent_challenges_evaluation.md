# Multi-Agent Challenges & Evaluation

**Reading Time:** 20-25 minutes
**Prerequisites:** Multi-agent fundamentals, multi-agent design patterns, basic agent evaluation concepts
**Learning Objectives:**
- Identify 6 core challenges in multi-agent systems and their solutions
- Understand multi-agent-specific evaluation dimensions
- Measure cooperation, planning, utilization, and scalability
- Extend single-agent trajectory evaluation to multi-agent systems
- Design comprehensive evaluation strategies for multi-agent applications
- Apply observability and debugging techniques to distributed agent systems

---

## Introduction: The Complexity Trade-Off

Multi-agent systems unlock powerful capabilities—**enhanced accuracy, parallel efficiency, and specialized expertise**—but they come with a price: **increased complexity**. Just as microservices architecture brought new challenges to software engineering (distributed debugging, network failures, service discovery), multi-agent systems introduce analogous challenges in the AI domain.

**Key Insight:**
The same factors that make multi-agent systems powerful (distribution, specialization, coordination) also make them **harder to build, debug, and evaluate** than single-agent systems.

This tutorial covers:
1. **Six fundamental challenges** every multi-agent system must address
2. **Multi-agent-specific evaluation dimensions** beyond single-agent metrics
3. **Practical strategies** for observability, debugging, and optimization

---

## Part 1: Six Challenges in Multi-Agent Systems

### Challenge 1: Task Communication

#### The Problem

Most multi-agent frameworks use **messages** for inter-agent communication, not **structured async tasks**.

**Message-based communication:**
```python
# Typical message-based approach
agent_a.send_message(agent_b, "Please analyze this document")
# ❌ No state tracking (is task pending? in-progress? completed?)
# ❌ No built-in retry or timeout handling
# ❌ Hard to resume tasks after failures
```

**Consequences:**
- **Difficult to track task state**: Is Agent B still working? Did it fail? Did it complete?
- **No built-in retry or timeout handling**: If Agent B crashes, the message is lost
- **Hard to resume tasks after failures**: No checkpoint/recovery mechanism

#### The Solution

Use **task-based communication** with structured task objects (see Topic 6: Contract-Based Agents for formal specifications).

**Task-based communication:**
```python
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
from typing import Any, Optional

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class Task:
    """Structured task for inter-agent communication."""
    task_id: str
    task_type: str
    payload: dict[str, Any]
    assigned_to: str
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = datetime.now()
    completed_at: Optional[datetime] = None
    result: Optional[dict[str, Any]] = None
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3

class TaskManager:
    """Manages task lifecycle with state tracking and retry logic."""

    def __init__(self):
        self.tasks: dict[str, Task] = {}

    def create_task(
        self,
        task_type: str,
        payload: dict[str, Any],
        assigned_to: str
    ) -> Task:
        """Create a new task with state tracking."""
        if not isinstance(payload, dict):
            raise TypeError("payload must be a dict")

        task = Task(
            task_id=f"task_{len(self.tasks)}",
            task_type=task_type,
            payload=payload,
            assigned_to=assigned_to
        )
        self.tasks[task.task_id] = task
        return task

    def update_task_status(
        self,
        task_id: str,
        status: TaskStatus,
        result: Optional[dict[str, Any]] = None,
        error: Optional[str] = None
    ) -> None:
        """Update task state with validation."""
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found")

        task = self.tasks[task_id]
        task.status = status

        if status == TaskStatus.COMPLETED:
            task.completed_at = datetime.now()
            task.result = result
        elif status == TaskStatus.FAILED:
            task.error = error
            # Retry logic
            if task.retry_count < task.max_retries:
                task.retry_count += 1
                task.status = TaskStatus.PENDING  # Retry

    def get_pending_tasks(self, agent_id: str) -> list[Task]:
        """Get all pending tasks for an agent."""
        return [
            task for task in self.tasks.values()
            if task.assigned_to == agent_id and task.status == TaskStatus.PENDING
        ]
```

**Benefits:**
- ✅ **State tracking**: Always know task status
- ✅ **Retry handling**: Built-in retry logic with max attempts
- ✅ **Resume capability**: Can restart failed tasks from checkpoints
- ✅ **Observability**: Full task history for debugging

---

### Challenge 2: Task Allocation

#### The Problem

Efficiently dividing complex tasks among agents requires answering:
1. **How to decompose the task optimally?** (monolithic vs. fine-grained subtasks)
2. **Which agent is best suited for each subtask?** (routing decision)
3. **How to implement feedback loops?** (continuous improvement based on performance)

**Example Challenge:**
```
User Query: "Plan a 7-day trip to Japan with $3000 budget"

Decomposition Options:
Option A: [research_destinations, book_flights, book_hotels, create_itinerary]
Option B: [analyze_budget, find_flights, find_hotels, find_activities, optimize_schedule]
Option C: [get_recommendations, compare_options, finalize_bookings]

Which is optimal? Depends on:
- Available agents and their capabilities
- Budget constraints (API costs)
- Latency requirements (parallel vs. sequential)
```

#### The Solution

Use **planner agents** with task allocation algorithms and feedback loops.

```python
from typing import Protocol

class Agent(Protocol):
    """Protocol for all agents."""
    agent_id: str
    capabilities: list[str]
    cost_per_call: float
    avg_latency: float

class TaskAllocationStrategy:
    """Intelligent task allocation with feedback loops."""

    def __init__(self):
        self.performance_history: dict[str, dict[str, float]] = {}

    def decompose_task(self, task: str, context: dict[str, Any]) -> list[dict[str, Any]]:
        """Decompose complex task into subtasks."""
        # Example: Use LLM-based planner to decompose
        subtasks = []

        if "trip planning" in task.lower():
            subtasks = [
                {"type": "budget_analysis", "description": "Analyze budget constraints"},
                {"type": "research", "description": "Find flights and hotels"},
                {"type": "itinerary", "description": "Create day-by-day schedule"},
                {"type": "booking", "description": "Finalize reservations"}
            ]

        return subtasks

    def select_agent(
        self,
        subtask: dict[str, Any],
        available_agents: list[Agent]
    ) -> Agent:
        """Select best agent for subtask based on capabilities and performance history."""
        subtask_type = subtask["type"]

        # Filter agents by capability
        capable_agents = [
            agent for agent in available_agents
            if subtask_type in agent.capabilities
        ]

        if not capable_agents:
            raise ValueError(f"No agent found for subtask type: {subtask_type}")

        # Rank by historical performance (if available)
        if subtask_type in self.performance_history:
            scores = self.performance_history[subtask_type]
            capable_agents.sort(
                key=lambda agent: scores.get(agent.agent_id, 0.5),
                reverse=True
            )

        # Return best agent (considering cost and latency)
        return capable_agents[0]

    def update_performance(
        self,
        agent_id: str,
        subtask_type: str,
        success: bool
    ) -> None:
        """Update agent performance history for future allocation decisions."""
        if subtask_type not in self.performance_history:
            self.performance_history[subtask_type] = {}

        # Exponential moving average
        current_score = self.performance_history[subtask_type].get(agent_id, 0.5)
        new_score = 1.0 if success else 0.0
        alpha = 0.3  # Learning rate

        self.performance_history[subtask_type][agent_id] = (
            alpha * new_score + (1 - alpha) * current_score
        )
```

**Benefits:**
- ✅ **Optimal decomposition**: Planner agent considers context and constraints
- ✅ **Intelligent routing**: Select agents based on capabilities AND historical performance
- ✅ **Continuous improvement**: Feedback loops adjust allocation over time

---

### Challenge 3: Coordinating Reasoning

#### The Problem

Getting agents to **debate and reason together** effectively is challenging:
- **Conflicting outputs**: Agent A says "high risk", Agent B says "low risk"
- **No built-in consensus mechanisms**: How to resolve disagreements?
- **Requires sophisticated coordination**: Simple majority voting may not capture nuance

#### The Solution

Implement **collaborative patterns** with evaluator agents, voting mechanisms, or weighted averaging.

**Consensus Mechanisms:**

```python
from typing import Literal
from statistics import mean, stdev

ConsensusMechanism = Literal["majority_vote", "weighted_average", "evaluator_judge"]

class ConsensusBuilder:
    """Build consensus from multiple agent outputs."""

    def __init__(self, mechanism: ConsensusMechanism = "weighted_average"):
        if mechanism not in ["majority_vote", "weighted_average", "evaluator_judge"]:
            raise ValueError(f"Invalid consensus mechanism: {mechanism}")
        self.mechanism = mechanism

    def build_consensus(
        self,
        agent_outputs: dict[str, Any],
        agent_weights: Optional[dict[str, float]] = None
    ) -> dict[str, Any]:
        """Build consensus from multiple agent outputs."""
        if not agent_outputs:
            raise ValueError("agent_outputs cannot be empty")

        if self.mechanism == "majority_vote":
            return self._majority_vote(agent_outputs)
        elif self.mechanism == "weighted_average":
            return self._weighted_average(agent_outputs, agent_weights or {})
        elif self.mechanism == "evaluator_judge":
            return self._evaluator_judge(agent_outputs)

        return {}

    def _majority_vote(self, agent_outputs: dict[str, Any]) -> dict[str, Any]:
        """Majority voting for categorical outputs."""
        # Count votes
        votes: dict[str, int] = {}
        for output in agent_outputs.values():
            decision = output.get("decision", "unknown")
            votes[decision] = votes.get(decision, 0) + 1

        # Return majority decision
        majority_decision = max(votes.items(), key=lambda x: x[1])

        return {
            "decision": majority_decision[0],
            "vote_count": majority_decision[1],
            "total_votes": len(agent_outputs),
            "confidence": majority_decision[1] / len(agent_outputs)
        }

    def _weighted_average(
        self,
        agent_outputs: dict[str, Any],
        agent_weights: dict[str, float]
    ) -> dict[str, Any]:
        """Weighted averaging for numerical outputs."""
        # Extract numerical values
        values = []
        weights = []

        for agent_id, output in agent_outputs.items():
            if "score" in output:
                values.append(output["score"])
                weights.append(agent_weights.get(agent_id, 1.0))

        if not values:
            raise ValueError("No numerical scores found in agent outputs")

        # Compute weighted average
        weighted_avg = sum(v * w for v, w in zip(values, weights)) / sum(weights)

        # Compute confidence based on agreement
        std_dev = stdev(values) if len(values) > 1 else 0.0
        confidence = 1.0 - min(std_dev / (max(values) - min(values) + 1e-6), 1.0)

        return {
            "score": weighted_avg,
            "confidence": confidence,
            "std_dev": std_dev,
            "num_agents": len(values)
        }

    def _evaluator_judge(self, agent_outputs: dict[str, Any]) -> dict[str, Any]:
        """Use evaluator agent to judge between conflicting outputs."""
        # In production, this would call an LLM-based evaluator agent
        # For now, return a placeholder
        return {
            "selected_output": "agent_1",  # Placeholder: evaluator selects best output
            "reasoning": "Agent 1 provided the most comprehensive analysis",
            "mechanism": "evaluator_judge"
        }
```

**Benefits:**
- ✅ **Conflict resolution**: Multiple mechanisms for different use cases
- ✅ **Confidence scoring**: Know when consensus is strong vs. weak
- ✅ **Flexibility**: Choose mechanism based on output type (categorical, numerical, free-text)

---

### Challenge 4: Managing Context

#### The Problem

Keeping track of information, tasks, and conversations across agents is challenging:
- **Context can grow large**: Token limits (e.g., GPT-4's 128k context window)
- **What context is relevant for each agent?**: Avoid passing unnecessary information
- **How to maintain context across handoffs?**: Preserve critical information when transferring between agents

**Example:**
```
Travel Planning System:
- User preferences (destinations, budget, dates) → Relevant to ALL agents
- Flight search results (100+ options) → Relevant only to booking agent
- Hotel amenities details (pools, gyms, etc.) → Relevant only if user asked
- Previous conversation history (20+ turns) → Selectively relevant
```

#### The Solution

Implement **shared memory systems**, **context summarization**, and **selective context passing**.

```python
from collections import defaultdict

class ContextManager:
    """Manage context across multi-agent interactions."""

    def __init__(self, max_context_tokens: int = 8000):
        if max_context_tokens <= 0:
            raise ValueError("max_context_tokens must be positive")

        self.max_context_tokens = max_context_tokens
        self.shared_memory: dict[str, Any] = {}  # Global context
        self.agent_memory: dict[str, dict[str, Any]] = defaultdict(dict)  # Per-agent context

    def add_to_shared_memory(self, key: str, value: Any) -> None:
        """Add information to shared memory (accessible to all agents)."""
        self.shared_memory[key] = value

    def add_to_agent_memory(self, agent_id: str, key: str, value: Any) -> None:
        """Add information to agent-specific memory."""
        if not agent_id:
            raise ValueError("agent_id cannot be empty")
        self.agent_memory[agent_id][key] = value

    def get_context_for_agent(
        self,
        agent_id: str,
        include_shared: bool = True
    ) -> dict[str, Any]:
        """Get relevant context for a specific agent."""
        context = {}

        # Include shared memory
        if include_shared:
            context.update(self.shared_memory)

        # Include agent-specific memory
        if agent_id in self.agent_memory:
            context.update(self.agent_memory[agent_id])

        # Check token limit and summarize if needed
        context_size = self._estimate_tokens(context)
        if context_size > self.max_context_tokens:
            context = self._summarize_context(context, self.max_context_tokens)

        return context

    def _estimate_tokens(self, context: dict[str, Any]) -> int:
        """Estimate token count (rough approximation: 4 chars = 1 token)."""
        import json
        context_str = json.dumps(context)
        return len(context_str) // 4

    def _summarize_context(
        self,
        context: dict[str, Any],
        max_tokens: int
    ) -> dict[str, Any]:
        """Summarize context to fit within token limit."""
        # Strategy 1: Remove least recently used entries
        # Strategy 2: Compress verbose entries
        # Strategy 3: Keep only critical fields

        # Placeholder: Return high-priority fields only
        critical_fields = ["user_query", "user_preferences", "current_task"]
        summarized = {
            k: v for k, v in context.items()
            if k in critical_fields
        }

        return summarized

    def transfer_context(
        self,
        from_agent: str,
        to_agent: str,
        keys: list[str]
    ) -> None:
        """Transfer specific context from one agent to another (handoff)."""
        if not keys:
            raise ValueError("keys cannot be empty")

        for key in keys:
            if key in self.agent_memory[from_agent]:
                value = self.agent_memory[from_agent][key]
                self.agent_memory[to_agent][key] = value
```

**Benefits:**
- ✅ **Shared memory**: Global context accessible to all agents
- ✅ **Agent-specific memory**: Avoid passing irrelevant information
- ✅ **Token limit enforcement**: Automatic summarization when context grows too large
- ✅ **Clean handoffs**: Explicit context transfer between agents

---

### Challenge 5: Time and Cost

#### The Problem

Multi-agent interactions are computationally **expensive**:
- **Higher runtime costs**: Multiple LLM calls per user query (3-10x cost of single-agent)
- **Increased user latency**: Sequential dependencies can add 10-30 seconds

**Cost Example:**
```
Single-Agent System:
- 1 LLM call × $0.03 = $0.03 per query

Multi-Agent System (Sequential):
- Classifier: $0.01
- Retrieval: $0.02
- Synthesis: $0.03
- Validator: $0.01
Total: $0.07 per query (2.3x more expensive)

Multi-Agent System (Parallel):
- Orchestrator: $0.01
- 3 parallel experts: 3 × $0.03 = $0.09
- Synthesizer: $0.02
Total: $0.12 per query (4x more expensive)
```

#### The Solution

Optimize for **parallelization**, use **cheaper models for simple tasks**, and **cache results**.

```python
import asyncio
from functools import lru_cache

class CostOptimizer:
    """Optimize multi-agent system for cost and latency."""

    def __init__(self):
        self.cost_tracking: dict[str, float] = {}

    async def execute_parallel(
        self,
        agents: list[tuple[str, callable]],
        query: str
    ) -> dict[str, Any]:
        """Execute agents in parallel to reduce latency."""
        if not agents:
            raise ValueError("agents list cannot be empty")

        # Launch all agents concurrently
        tasks = [
            asyncio.create_task(self._execute_agent(agent_id, agent_fn, query))
            for agent_id, agent_fn in agents
        ]

        # Wait for all to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Aggregate results
        return {
            agents[i][0]: result
            for i, result in enumerate(results)
            if not isinstance(result, Exception)
        }

    async def _execute_agent(
        self,
        agent_id: str,
        agent_fn: callable,
        query: str
    ) -> Any:
        """Execute single agent and track cost."""
        result = await agent_fn(query)

        # Track cost (assumes result has "cost" field)
        if isinstance(result, dict) and "cost" in result:
            self.cost_tracking[agent_id] = result["cost"]

        return result

    def select_model_by_complexity(self, task_complexity: str) -> str:
        """Select appropriate model based on task complexity."""
        model_mapping = {
            "simple": "gpt-3.5-turbo",  # $0.001 per 1k tokens
            "medium": "gpt-4o-mini",    # $0.015 per 1k tokens
            "complex": "gpt-4o",         # $0.03 per 1k tokens
        }

        return model_mapping.get(task_complexity, "gpt-4o-mini")

    @lru_cache(maxsize=1000)
    def cached_retrieval(self, query: str) -> dict[str, Any]:
        """Cache retrieval results to avoid redundant API calls."""
        # In production, this would call a retrieval agent
        # For now, return placeholder
        return {"documents": [], "cached": True}

    def get_total_cost(self) -> float:
        """Get total cost across all agents."""
        return sum(self.cost_tracking.values())
```

**Optimization Strategies:**
- ✅ **Parallelization**: Run independent agents concurrently (reduce latency by 50-70%)
- ✅ **Model selection**: Use GPT-3.5 for simple tasks, GPT-4 only when needed (reduce cost by 30-50%)
- ✅ **Caching**: Store frequent queries/results (reduce redundant API calls by 20-40%)

---

### Challenge 6: Complexity

#### The Problem

System-level complexity increases (analogous to microservices):
- **More components to develop and maintain**: Each agent is a separate module
- **Distributed debugging is harder**: Failures can occur anywhere in the agent graph
- **Inter-agent communication can fail**: Network issues, timeouts, malformed messages

**Debugging Example:**
```
User reports: "Travel booking failed"

Single-Agent System:
- Check logs for one agent → Find error in 5 minutes

Multi-Agent System:
- Which agent failed? (Classifier? Retrieval? Booking? Validator?)
- Was it a failure or incorrect routing?
- Did context get lost during handoff?
- Check logs for 5+ agents → Find error in 30 minutes
```

#### The Solution

Implement **strong observability** (see Topic 1: AgentOps), **clear interfaces**, and **comprehensive testing**.

```python
import logging
from datetime import datetime
from typing import Callable

class ObservabilityLayer:
    """Comprehensive observability for multi-agent systems."""

    def __init__(self):
        self.logger = logging.getLogger("multi_agent_system")
        self.traces: list[dict[str, Any]] = []

    def trace_agent_call(
        self,
        agent_id: str,
        input_data: dict[str, Any],
        agent_fn: Callable
    ) -> dict[str, Any]:
        """Trace agent execution with detailed logging."""
        trace_id = f"trace_{len(self.traces)}"
        start_time = datetime.now()

        self.logger.info(f"[{trace_id}] Agent {agent_id} started")

        try:
            # Execute agent
            result = agent_fn(input_data)

            # Log success
            duration = (datetime.now() - start_time).total_seconds()
            self.logger.info(
                f"[{trace_id}] Agent {agent_id} completed in {duration:.2f}s"
            )

            # Store trace
            self.traces.append({
                "trace_id": trace_id,
                "agent_id": agent_id,
                "status": "success",
                "duration": duration,
                "timestamp": start_time.isoformat()
            })

            return result

        except Exception as e:
            # Log failure with full context
            duration = (datetime.now() - start_time).total_seconds()
            self.logger.error(
                f"[{trace_id}] Agent {agent_id} failed after {duration:.2f}s: {e}"
            )

            # Store failure trace
            self.traces.append({
                "trace_id": trace_id,
                "agent_id": agent_id,
                "status": "failed",
                "error": str(e),
                "duration": duration,
                "timestamp": start_time.isoformat()
            })

            raise

    def get_agent_performance_summary(self) -> dict[str, Any]:
        """Get performance summary for all agents."""
        summary = defaultdict(lambda: {"success": 0, "failed": 0, "total_duration": 0.0})

        for trace in self.traces:
            agent_id = trace["agent_id"]
            summary[agent_id][trace["status"]] += 1
            summary[agent_id]["total_duration"] += trace.get("duration", 0.0)

        # Compute success rate and average duration
        for agent_id, stats in summary.items():
            total_calls = stats["success"] + stats["failed"]
            stats["success_rate"] = stats["success"] / total_calls if total_calls > 0 else 0.0
            stats["avg_duration"] = stats["total_duration"] / total_calls if total_calls > 0 else 0.0

        return dict(summary)

    def debug_failed_query(self, query_id: str) -> list[dict[str, Any]]:
        """Get full trace for a failed query to debug."""
        # In production, correlate traces by query_id
        failed_traces = [
            trace for trace in self.traces
            if trace["status"] == "failed"
        ]

        return failed_traces
```

**Benefits:**
- ✅ **Detailed logging**: Every agent call is traced with timing and status
- ✅ **Performance insights**: Identify slow or failing agents
- ✅ **Debugging support**: Reconstruct full execution path for failed queries

---

## Part 2: Multi-Agent Evaluation

### Extending Single-Agent Evaluation

**Good News**: Multi-agent evaluation is a **clear progression** from single-agent evaluation (see Topic 2: Agent Evaluation Methodology).

#### What Stays the Same

**1. Agent Success Metrics** (from Topic 1: AgentOps)
- Business KPIs (conversion rate, user satisfaction)
- Goal completion rate
- Critical task accuracy

**2. Application Telemetry**
- Latency (p50, p95, p99)
- Error rates
- API usage and costs

**3. Trace Instrumentation**
- Debugging complex interactions
- Identifying bottlenecks
- Monitoring system health

#### What Changes

**Trajectory Evaluation** now includes actions across **multiple agents**:
```
Single-Agent Trajectory:
[tool_call_1, tool_call_2, tool_call_3, response]

Multi-Agent Trajectory:
[
    (agent_classifier, tool_call_1),
    (agent_retrieval, tool_call_2),
    (agent_synthesis, tool_call_3),
    (agent_validator, tool_call_4),
    response
]
```

**Evaluation Scalability**:
- Drill down and evaluate **each agent in isolation** (unit testing)
- Evaluate **system as a whole** (integration testing)

---

### Multi-Agent-Specific Evaluation Dimensions

#### Dimension 1: Cooperation and Coordination

**Question**: How well do agents work together to achieve common goals?

**Metrics:**

```python
class CooperationMetrics:
    """Metrics for measuring agent cooperation."""

    def task_completion_rate(
        self,
        successful_tasks: int,
        total_tasks: int
    ) -> float:
        """% of tasks where all agents successfully collaborated."""
        if total_tasks == 0:
            raise ValueError("total_tasks must be > 0")
        return successful_tasks / total_tasks

    def coordination_efficiency(
        self,
        communication_rounds: int,
        minimum_rounds: int
    ) -> float:
        """Measure efficiency as ratio of actual to minimum rounds needed."""
        if minimum_rounds == 0:
            raise ValueError("minimum_rounds must be > 0")

        # Efficiency = 1.0 means optimal (no extra communication)
        # Efficiency < 1.0 means inefficient (extra rounds)
        return minimum_rounds / communication_rounds

    def conflict_resolution_success(
        self,
        conflicts_resolved: int,
        total_conflicts: int
    ) -> float:
        """% of disagreements successfully resolved through consensus."""
        if total_conflicts == 0:
            return 1.0  # No conflicts = perfect success
        return conflicts_resolved / total_conflicts
```

**Example Evaluation:**
```
Travel Booking System:
- Task: Book round-trip flight + hotel for 3-day trip

Agents:
- Planner: Created valid itinerary? ✅
- Search: Found flight and hotel options? ✅
- Booking: Completed reservations? ✅
- Validator: Confirmed all details match user preferences? ✅

Result:
- Task Completion Rate: 100% (1/1 tasks completed)
- Coordination Efficiency: 0.8 (5 communication rounds, 4 minimum)
- Conflict Resolution: 100% (1 conflict resolved: flight time overlap)
```

---

#### Dimension 2: Planning and Task Assignment

**Questions:**
1. Did we come up with the **right plan**?
2. Did we **stick to the plan**?
3. Did child agents **deviate** from the main plan?
4. Did agents get **stuck in a loop** (cul-de-sac)?

**Metrics:**

```python
class PlanningMetrics:
    """Metrics for evaluating multi-agent planning."""

    def plan_adherence(
        self,
        planned_tasks: list[str],
        executed_tasks: list[str]
    ) -> float:
        """% of planned tasks that were actually executed."""
        if not planned_tasks:
            raise ValueError("planned_tasks cannot be empty")

        executed_set = set(executed_tasks)
        adhered_tasks = [task for task in planned_tasks if task in executed_set]

        return len(adhered_tasks) / len(planned_tasks)

    def deviation_analysis(
        self,
        planned_tasks: list[str],
        executed_tasks: list[str]
    ) -> dict[str, Any]:
        """Identify unplanned actions (deviations from plan)."""
        planned_set = set(planned_tasks)
        unplanned_actions = [task for task in executed_tasks if task not in planned_set]

        return {
            "unplanned_actions": unplanned_actions,
            "deviation_count": len(unplanned_actions),
            "deviation_rate": len(unplanned_actions) / len(executed_tasks) if executed_tasks else 0.0
        }

    def detect_deadlock(self, execution_trace: list[tuple[str, str]]) -> bool:
        """Detect if agents are stuck in a loop (cul-de-sac)."""
        # Check if same (agent, action) pair appears 3+ times consecutively
        if len(execution_trace) < 3:
            return False

        for i in range(len(execution_trace) - 2):
            if execution_trace[i] == execution_trace[i+1] == execution_trace[i+2]:
                return True

        return False
```

**Example Evaluation:**
```
Planned Workflow:
1. Search for hotels
2. Search for flights
3. Book hotel
4. Book flight

Actual Execution:
1. Search for hotels
2. Search for flights
3. Search for flights (retry due to price change) ← DEVIATION
4. Book flight
5. Book hotel (swapped order) ← DEVIATION

Metrics:
- Plan Adherence: 75% (3/4 planned tasks executed in correct order)
- Deviation Count: 2 (one retry, one reordering)
- Deadlock Detected: False
```

---

#### Dimension 3: Agent Utilization

**Questions:**
1. How effectively do agents **select the right agent** for each task?
2. Do they choose the correct **mode** (tool use, delegation, transfer)?

**Metrics:**

```python
class UtilizationMetrics:
    """Metrics for evaluating agent utilization."""

    def agent_selection_accuracy(
        self,
        expected_agents: list[str],
        actual_agents: list[str]
    ) -> float:
        """% of tasks routed to the correct agent."""
        if not expected_agents:
            raise ValueError("expected_agents cannot be empty")

        correct_selections = sum(
            1 for exp, act in zip(expected_agents, actual_agents) if exp == act
        )

        return correct_selections / len(expected_agents)

    def mode_selection_accuracy(
        self,
        expected_modes: list[str],
        actual_modes: list[str]
    ) -> float:
        """% of interactions using the correct mode (tool/delegate/transfer)."""
        if not expected_modes:
            raise ValueError("expected_modes cannot be empty")

        correct_modes = sum(
            1 for exp, act in zip(expected_modes, actual_modes) if exp == act
        )

        return correct_modes / len(expected_modes)

    def resource_utilization(
        self,
        agent_busy_time: dict[str, float],
        total_time: float
    ) -> dict[str, float]:
        """% of time each agent is busy vs. idle."""
        if total_time <= 0:
            raise ValueError("total_time must be positive")

        return {
            agent_id: busy_time / total_time
            for agent_id, busy_time in agent_busy_time.items()
        }
```

**Example Evaluation:**
```
Query: "What's the weather in Tokyo?"

Expected Routing:
- Agent: weather_agent
- Mode: tool_use

Actual Routing:
- Agent: weather_agent ✅
- Mode: tool_use ✅

Query: "Find hotels near Tokyo Tower"

Expected Routing:
- Agent: search_agent
- Mode: tool_use

Actual Routing (Incorrect):
- Agent: general_knowledge_agent ❌ (should have used search_agent)
- Mode: delegation ❌ (should have used tool_use)

Metrics:
- Agent Selection Accuracy: 50% (1/2 correct)
- Mode Selection Accuracy: 50% (1/2 correct)
```

---

#### Dimension 4: Scalability

**Questions:**
1. Does **quality improve** as more agents are added?
2. Does **latency decrease** (is parallelization working)?
3. Are we being **more efficient** or less efficient?

**Metrics:**

```python
class ScalabilityMetrics:
    """Metrics for evaluating multi-agent scalability."""

    def quality_vs_agent_count(
        self,
        num_agents: int,
        accuracy: float
    ) -> dict[str, Any]:
        """Measure quality improvement with more agents."""
        # Baseline: single agent accuracy
        baseline_accuracy = 0.80

        improvement = (accuracy - baseline_accuracy) / baseline_accuracy

        return {
            "num_agents": num_agents,
            "accuracy": accuracy,
            "improvement_over_baseline": improvement,
            "quality_scales": improvement > 0
        }

    def latency_vs_agent_count(
        self,
        num_agents: int,
        latency: float,
        baseline_latency: float
    ) -> dict[str, Any]:
        """Measure latency reduction with parallelization."""
        if baseline_latency <= 0:
            raise ValueError("baseline_latency must be positive")

        reduction = (baseline_latency - latency) / baseline_latency

        return {
            "num_agents": num_agents,
            "latency": latency,
            "baseline_latency": baseline_latency,
            "latency_reduction": reduction,
            "parallelization_working": reduction > 0
        }

    def cost_efficiency(
        self,
        num_agents: int,
        cost_per_task: float,
        baseline_cost: float
    ) -> dict[str, Any]:
        """Measure cost efficiency vs. number of agents."""
        if baseline_cost <= 0:
            raise ValueError("baseline_cost must be positive")

        cost_ratio = cost_per_task / baseline_cost

        return {
            "num_agents": num_agents,
            "cost_per_task": cost_per_task,
            "cost_ratio": cost_ratio,
            "efficient": cost_ratio < 1.5  # Acceptable if <1.5x baseline cost
        }
```

**Example Evaluation:**
```
Experiment: Add more agents and measure quality/latency/cost

1 Agent (Baseline):
- Latency: 10s
- Accuracy: 80%
- Cost: $0.03

3 Agents (Parallel):
- Latency: 6s ✅ (40% reduction)
- Accuracy: 90% ✅ (12.5% improvement)
- Cost: $0.07 (2.3x baseline) ⚠️

3 Agents (Sequential):
- Latency: 25s ❌ (150% increase)
- Accuracy: 90% ✅
- Cost: $0.07 ⚠️

Conclusion:
- Parallel agents improve quality AND reduce latency ✅
- Sequential agents improve quality but INCREASE latency ❌
- Cost increases 2.3x (acceptable if quality/latency gains justify)
```

---

### Multi-Agent Trajectory Evaluation

**Same metrics as single-agent** (see Topic 2: Trajectory Evaluation Techniques):
- Exact match
- In-order match
- Any-order match
- Precision
- Recall
- Single-tool use

**Difference**: Trajectory now spans **multiple agents**.

**Example Multi-Agent Trajectory:**
```python
# Reference trajectory (ground truth)
reference_trajectory = [
    ("orchestrator_agent", "classify_query"),
    ("planner_agent", "decompose_task"),
    ("search_agent", "retrieve_flights"),
    ("user_selection_agent", "present_options"),
    ("booking_agent", "complete_reservation"),
    ("validator_agent", "confirm_booking")
]

# Actual trajectory (system execution)
actual_trajectory = [
    ("orchestrator_agent", "classify_query"),
    ("planner_agent", "decompose_task"),
    ("search_agent", "retrieve_flights"),
    ("search_agent", "retrieve_hotels"),  # ← EXTRA STEP (not in reference)
    ("user_selection_agent", "present_options"),
    ("booking_agent", "complete_reservation"),
    # ← MISSING: validator_agent
]

# Evaluation
from backend.trajectory_evaluation import TrajectoryEvaluator

evaluator = TrajectoryEvaluator()

results = {
    "exact_match": evaluator.exact_match(reference_trajectory, actual_trajectory),
    # → False (trajectories don't match exactly)

    "in_order_match": evaluator.in_order_match(reference_trajectory, actual_trajectory),
    # → 4/6 = 0.67 (4 actions in correct order, 2 missing/extra)

    "precision": evaluator.precision(reference_trajectory, actual_trajectory),
    # → 5/7 = 0.71 (5 correct actions out of 7 executed)

    "recall": evaluator.recall(reference_trajectory, actual_trajectory),
    # → 5/6 = 0.83 (5 correct actions out of 6 expected)
}
```

**Evaluation Questions:**
1. **Did each agent perform the expected action?** → Check exact match
2. **Were handoffs clean?** (context preserved) → Check if next agent received correct input
3. **Was the sequence optimal?** (no unnecessary steps) → Check precision (fewer extra steps = higher precision)

---

## Practical Exercise: Design a Multi-Agent Evaluation Strategy

**Scenario**: You are building a **customer support chatbot** with multiple specialized agents:
- **Classifier Agent**: Routes queries to appropriate department
- **FAQ Agent**: Answers common questions from knowledge base
- **Technical Support Agent**: Handles complex technical issues
- **Escalation Agent**: Transfers to human support when needed

**Your Task**: Design a comprehensive evaluation strategy that covers:

**1. Which challenges apply to your system?**
- Task Communication: How do agents communicate (messages vs. tasks)?
- Task Allocation: How does the classifier decide which agent to use?
- Managing Context: How do you preserve conversation history across handoffs?
- Time and Cost: How can you optimize for latency and API costs?

**2. What metrics will you measure?**
- Cooperation: Task completion rate, conflict resolution
- Planning: Plan adherence (did we route to the right agent?)
- Utilization: Agent selection accuracy, mode selection accuracy
- Scalability: Does adding more specialized agents improve quality?

**3. How will you evaluate trajectories?**
- Define reference trajectories for common queries
- Measure exact match, precision, recall
- Identify handoff failures (context lost between agents)

**4. What observability will you implement?**
- Trace every agent call with timing and status
- Track failure modes (which agent failed most often?)
- Monitor escalation rate (% queries requiring human support)

---

## Summary

### Six Challenges

| Challenge | Problem | Solution |
|-----------|---------|----------|
| **Task Communication** | Messages lack state tracking | Use structured task objects with retry/timeout |
| **Task Allocation** | Optimal task decomposition | Planner agents + feedback loops |
| **Coordinating Reasoning** | Conflicting outputs | Consensus mechanisms (voting, evaluator agents) |
| **Managing Context** | Token limits, relevance | Shared memory + selective passing |
| **Time and Cost** | Multi-agent is expensive | Parallelization, model selection, caching |
| **Complexity** | Distributed debugging | Strong observability + comprehensive testing |

### Multi-Agent Evaluation Dimensions

| Dimension | Key Questions | Metrics |
|-----------|---------------|---------|
| **Cooperation** | Do agents collaborate effectively? | Task completion rate, coordination efficiency |
| **Planning** | Right plan? Stuck to plan? | Plan adherence, deviation analysis |
| **Utilization** | Right agent? Right mode? | Agent selection accuracy, resource utilization |
| **Scalability** | Quality improves? Latency decreases? | Quality vs. # agents, latency vs. # agents |

### Key Takeaways

1. **Multi-agent systems are powerful but complex**: Every advantage (parallelization, specialization) comes with a cost (coordination, debugging)
2. **Evaluation extends single-agent practices**: Same principles (trajectory evaluation, autoraters), but now across multiple agents
3. **Observability is critical**: Without strong logging and tracing, debugging multi-agent systems is nearly impossible
4. **Optimize for your constraints**: Choose patterns and optimizations based on your priorities (cost vs. latency vs. quality)

---

## Cross-References

**Related Topics:**
- **Topic 1: AgentOps & Operations** - Observability strategies for multi-agent systems
- **Topic 2: Agent Evaluation Methodology** - Trajectory evaluation metrics (exact match, precision, recall)
- **Topic 3: Multi-Agent Architectures** - Design patterns (sequential, hierarchical, collaborative, competitive)
- **Topic 6: Contract-Based Agents** - Formal task specifications for robust communication

**Related Tutorials:**
- [Multi-Agent Fundamentals](./multi_agent_fundamentals.md) - Introduction to multi-agent systems
- [Multi-Agent Design Patterns](./multi_agent_design_patterns.md) - When to use each coordination pattern
- [Trajectory Evaluation Techniques](./trajectory_evaluation_techniques.md) - Single-agent trajectory metrics
- [Agent Evaluation Fundamentals](./agent_evaluation_fundamentals.md) - AgentOps evolution and observability

---

**Next Steps:**
1. Read **Topic 3: Multi-Agent Architectures** (full whitepaper section)
2. Implement one of the code examples in your own multi-agent system
3. Design an evaluation strategy for your use case using the practical exercise as a template
4. Explore **Topic 6: Contract-Based Agents** for formal task specifications

**Estimated Time Investment:**
- Reading this tutorial: 20-25 minutes ✅
- Implementing code examples: 1-2 hours
- Designing custom evaluation strategy: 1-2 hours
- Total: 3-5 hours for full mastery
