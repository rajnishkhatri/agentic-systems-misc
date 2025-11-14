# Lesson 14: Agent Planning & Orchestration - Tutorial Index

## Overview

Lesson 14 covers **agent system evaluation** with focus on **planning validation**, **ReAct patterns**, and **multi-agent orchestration**. You'll learn to evaluate agent reasoning quality, detect and classify failure modes, implement ReAct agents with dynamic replanning, and design multi-agent systems for complex task decomposition.

**Learning Time:** ~5-6 hours
**Difficulty:** Advanced
**Prerequisites:**
- [Lesson 10: AI-as-Judge](../lesson-10/TUTORIAL_INDEX.md) - LLM judge patterns and prompt engineering
- [Lesson 13: RAG Generation](../lesson-13/TUTORIAL_INDEX.md) - Understanding LLM generation evaluation
- [HW5: Agent Failure Analysis](../homeworks/hw5/TUTORIAL_INDEX.md) - Agent debugging fundamentals
- Familiarity with function calling and tool use

---

## Learning Objectives

By completing these tutorials, you will be able to:
- ✅ Validate agent plans for correctness, completeness, and efficiency before execution
- ✅ Implement ReAct (Reasoning + Acting) agents with Thought-Action-Observation loops
- ✅ Apply Reflexion patterns for learning from failures and iterative improvement
- ✅ Classify agent failures into Planning, Execution, and Efficiency categories
- ✅ Design multi-agent systems with role separation (Planner, Validator, Executor)
- ✅ Measure agent performance with planning accuracy, tool call accuracy, and efficiency metrics
- ✅ Debug agent failures using systematic root cause analysis and targeted remediations
- ✅ Understand AgentOps evolution and agent observability architecture ⚡ NEW
- ✅ Apply 6 trajectory metrics (Exact Match, In-Order, Any-Order, Precision, Recall, Single-Tool) ⚡ NEW
- ✅ Select appropriate trajectory metrics based on use case requirements ⚡ NEW
- ✅ Visualize agent performance with multi-dimensional radar charts ⚡ NEW

---

## Tutorials

### 1. Agent Planning Evaluation
**File:** `agent_planning_evaluation.md`
**Reading Time:** 22-25 minutes
**Topics:**
- Why evaluate plans before execution (cost savings, error prevention, debugging)
- Planning validation dimensions: correctness, tool selection, argument quality, completeness, efficiency
- Tool call validation (schema checking, semantic validation, argument constraints)
- Plan completeness checking (goal decomposition, missing steps, dependency validation)
- Efficiency scoring (step count optimization, redundancy detection, ordering analysis)
- Real-world examples from recipe agent planning tasks

**When to use:** Essential foundation before building agent evaluation systems.

---

### 2. ReAct & Reflexion Patterns
**File:** `react_reflexion_patterns.md`
**Reading Time:** 20-25 minutes
**Topics:**
- ReAct pattern: Thought-Action-Observation loop for dynamic reasoning
- Implementing iterative replanning based on observations
- Reflexion pattern: Learning from failures with self-critique
- Memory management for agent trajectories
- When to use ReAct vs. chain-of-thought vs. fixed planning
- Error handling and recovery strategies
- Real implementations with code examples

**When to use:** Learn before implementing dynamic agent systems with runtime replanning.

---

### 3. Multi-Agent Orchestration
**File:** `multi_agent_orchestration.md`
**Reading Time:** 18-22 minutes
**Topics:**
- Why multi-agent systems? (Separation of concerns, debuggability, scalability)
- Planner-Validator-Executor (PVE) pattern
- Role-based agent design (specialized vs. general-purpose agents)
- Communication protocols between agents (shared state, message passing)
- Orchestration strategies (sequential, parallel, hierarchical)
- Abstract base class pattern for agent implementations
- Concrete examples: Recipe planning agent with validation

**When to use:** Design complex agent systems with multiple specialized components.

---

### 4. Agent Evaluation Fundamentals ⚡ NEW
**File:** `agent_evaluation_fundamentals.md`
**Reading Time:** 25-30 minutes
**Topics:**
- DevOps → MLOps → GenAIOps → AgentOps evolution
- Agent success metrics (business KPIs, goals, telemetry)
- Observability architecture (high-level KPIs + detailed traces)
- Three pillars of agent evaluation (trajectory, final response, HITL)
- Public benchmarks (BFCL, τ-bench, PlanBench, AgentBench)
- Metrics-driven development for agents
- Production readiness framework

**When to use:** Essential foundation before implementing trajectory evaluation or agent monitoring.

---

### 5. Trajectory Evaluation Techniques ⚡ NEW
**File:** `trajectory_evaluation_techniques.md`
**Reading Time:** 20-25 minutes
**Topics:**
- Understanding agent trajectories and ground-truth requirements
- Six trajectory metrics: Exact Match, In-Order Match, Any-Order Match, Precision, Recall, Single-Tool Use
- Metric selection framework based on use case (compliance, efficiency, completeness)
- Visualization with radar charts for multi-dimensional analysis
- Limitations of ground-truth evaluation
- Future direction: Agent-as-a-Judge for flexible trajectory assessment
- Practical exercises with payment processing, e-commerce, and security workflows

**When to use:** Learn before implementing trajectory-based agent evaluation or debugging agent behavior.

---

### 6. ReAct Agent Implementation (Interactive Notebook)
**File:** [`react_agent_implementation.ipynb`](react_agent_implementation.ipynb)
**Execution Time:** ~10 minutes
**Cost:** $0.30-0.50 (DEMO mode, 3 tasks), $2.00-3.00 (FULL mode, 15 tasks)
**Topics:**
- Implement complete ReAct agent with Thought-Action-Observation loop
- Tool definitions for recipe search and shopping list management
- Dynamic plan generation based on observations
- Cost and token tracking for agent executions
- Performance metrics (completion rate, avg steps, error rate, tool usage)
- Results generation for dashboard integration (`planning_validation.json`)

**When to use:** Hands-on practice building production-ready ReAct agents.

---

### 7. Agent Failure Analysis (Interactive Notebook)
**File:** [`agent_failure_analysis.ipynb`](agent_failure_analysis.ipynb)
**Execution Time:** ~7 minutes
**Cost:** $0.30-0.40 (DEMO mode, 7 cases), $1.50-2.00 (FULL mode, 20 cases)
**Topics:**
- Classify failures into Planning, Execution, Efficiency categories
- Diagnose specific failure types (wrong tools, invalid args, timeouts, redundant actions)
- Severity assessment (LOW, MEDIUM, HIGH, CRITICAL)
- Root cause analysis for each failure category
- Automated remediation suggestions
- Performance metrics and failure rate analysis
- Results generation for dashboard (`agent_performance.json`)

**When to use:** Debug agent failures and improve system reliability.

---

## Visual Diagrams

### 1. ReAct Agent Workflow
**File:** `diagrams/react_agent_workflow.mmd`
**Description:** Flowchart showing Thought-Action-Observation loop with decision points for task completion vs. replanning.

### 2. Multi-Agent Orchestration
**File:** `diagrams/multi_agent_orchestration.mmd`
**Description:** Architecture diagram of Planner-Validator-Executor pattern with communication flows.

### 3. Agent Failure Modes Taxonomy
**File:** `diagrams/agent_failure_modes_taxonomy.mmd`
**Description:** Comprehensive taxonomy of 15 failure types across 3 categories (Planning, Execution, Efficiency) with examples and remediation strategies.

---

## Recommended Learning Path

```
┌─────────────────────────────────────────────────────┐
│ FOUNDATION: Understanding Agent Evaluation          │
│                                                     │
│ 1. Read: agent_planning_evaluation.md (25 min)     │
│    → Learn validation dimensions and metrics       │
│                                                     │
│ 2. Study: diagrams/agent_failure_modes_taxonomy.mmd│
│    → Understand 15 failure types and fixes         │
└─────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────┐
│ PATTERNS: ReAct & Multi-Agent Design                │
│                                                     │
│ 3. Read: react_reflexion_patterns.md (20 min)      │
│    → Learn dynamic reasoning patterns              │
│                                                     │
│ 4. Read: multi_agent_orchestration.md (20 min)     │
│    → Learn PVE pattern and role separation         │
│                                                     │
│ 5. Study: diagrams/react_agent_workflow.mmd        │
│    → Visualize Thought-Action-Observation loop     │
└─────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────┐
│ HANDS-ON: Implementation & Debugging                │
│                                                     │
│ 6. Run: react_agent_implementation.ipynb (DEMO)    │
│    → Build ReAct agent, test on 3 tasks           │
│    → Analyze planning accuracy and tool usage      │
│                                                     │
│ 7. Run: agent_failure_analysis.ipynb (DEMO)        │
│    → Classify 7 failure cases into categories      │
│    → Generate remediation recommendations          │
│                                                     │
│ 8. Review: lesson-14/results/*.json                │
│    → Examine planning_validation.json metrics      │
│    → Analyze agent_performance.json breakdown      │
└─────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────┐
│ MASTERY: Production Agent Systems                   │
│                                                     │
│ 9. Implement: Multi-agent system for your domain   │
│    → Apply PVE pattern with specialized agents     │
│    → Add validation before execution               │
│                                                     │
│ 10. Deploy: Failure monitoring and alerting        │
│     → Track planning/execution/efficiency rates    │
│     → Set up automated remediation triggers        │
└─────────────────────────────────────────────────────┘
```

**Time Breakdown:**
- Reading tutorials: ~1.5 hours
- Interactive notebooks: ~30 minutes (DEMO mode)
- Backend implementation review: ~1 hour
- Practice projects: ~2-3 hours

---

## Backend Implementation

### Core Modules

**1. Agent Evaluation (`backend/agent_evaluation.py`)**
- `PlanValidator` class - Validates plan correctness and completeness
- `ToolCallValidator` class - Schema and semantic validation for tool calls
- `PlanEvaluator` class - Orchestrates all validation checks
- Functions: `validate_tool_call()`, `validate_plan_correctness()`, `validate_plan_completeness()`, `calculate_plan_efficiency()`
- **Tests:** `tests/test_agent_evaluation.py` (40+ tests)

**2. Multi-Agent Framework (`backend/multi_agent_framework.py`)**
- `BaseAgent` abstract class - Common interface for all agents
- `PlannerAgent` class - Generates task plans
- `ValidatorAgent` class - Validates plans before execution
- `ExecutorAgent` class - Executes validated plans
- `MemoryManager` class - Tracks conversation history and agent state
- `MultiAgentOrchestrator` class - Coordinates workflow execution
- **Tests:** `tests/test_multi_agent_framework.py` (30+ tests)

**Code Quality:**
- ✅ 100% type hints with mypy validation
- ✅ Defensive coding with input validation
- ✅ Comprehensive error handling
- ✅ >90% test coverage
- ✅ Abstract base class pattern for extensibility

---

## Benchmarks and Test Data

### 1. Planning Validation Benchmark
**File:** `data/agent_planning_benchmark.json`
**Size:** 100 test cases
**Categories:**
- Goal-Plan Alignment: 30 cases (correct plans, goal mismatches)
- Tool Selection: 30 cases (correct tools, wrong tools)
- Plan Completeness: 25 cases (complete, missing steps)
- Efficiency: 15 cases (optimal, suboptimal, excessive steps)

**Labels:**
- `goal_achieved`: Boolean
- `correct_tools`: Boolean
- `complete_plan`: Boolean
- `optimal_efficiency`: Boolean (0.0-1.0)

### 2. Tool Call Validation Benchmark
**File:** `data/tool_call_benchmark.json`
**Size:** 150 test cases
**Categories:**
- Correct calls: 50 cases
- Wrong tool selection: 30 cases
- Missing required args: 25 cases
- Invalid arg types: 25 cases
- Invalid arg values: 20 cases

**Labels:**
- `is_valid`: Boolean
- `tool_selection`: CORRECT | WRONG_TOOL
- `args_validation`: VALID | MISSING_REQUIRED | TYPE_ERROR | VALUE_ERROR

### 3. Efficiency Benchmark
**File:** `data/agent_efficiency_benchmark.json`
**Size:** 100 test cases
**Categories:**
- Optimal plans (40 cases)
- Suboptimal with redundancy (30 cases)
- Suboptimal with unnecessary steps (20 cases)
- Suboptimal with wrong ordering (10 cases)

**Metrics:**
- `optimal_step_count`: int
- `actual_step_count`: int
- `efficiency_score`: float (0.0-1.0)
- `inefficiency_type`: REDUNDANT_CALLS | UNNECESSARY_STEPS | WRONG_ORDER

---

## FAQ

### Q1: What's the difference between ReAct and chain-of-thought prompting?

**Chain-of-thought (CoT):** All reasoning happens in a single LLM call before action. Static, no feedback from environment.

**ReAct:** Iterative loop with reasoning → action → observation → reasoning. Dynamic, adapts based on observations.

**When to use:**
- CoT: Simple tasks with no external actions (math, reasoning problems)
- ReAct: Complex tasks with tool use, multi-step retrieval, or environment interaction

---

### Q2: Why separate planning and execution validation?

**Reason:** Planning validation catches errors **before** expensive execution.

**Example:**
```python
# Without validation
plan = planner.generate(query)
result = executor.execute(plan)  # ❌ Expensive API calls, then fails

# With validation
plan = planner.generate(query)
validation = validator.validate(plan)
if validation["valid"]:
    result = executor.execute(plan)  # ✅ Only execute valid plans
else:
    # Retry planning with feedback
    plan = planner.retry_with_feedback(validation["issues"])
```

**Benefits:**
- Cost savings (avoid bad execution)
- Faster debugging (catch errors early)
- Better user experience (fewer failures)

---

### Q3: How do I choose between single-agent and multi-agent systems?

**Single Agent (ReAct):**
- ✅ Simpler implementation
- ✅ Lower latency (no inter-agent communication)
- ✅ Good for straightforward tasks
- ❌ Hard to debug complex failures
- ❌ Difficult to parallelize

**Multi-Agent (PVE Pattern):**
- ✅ Separation of concerns (easier debugging)
- ✅ Role specialization (better performance)
- ✅ Parallel execution possible
- ✅ Easier to add new capabilities
- ❌ More complex implementation
- ❌ Higher communication overhead

**Rule of thumb:** Use single-agent for <5 step tasks, multi-agent for complex workflows.

---

### Q4: What are the most common agent planning failures?

**Top 5 from our benchmarks:**

1. **Wrong tool selection (35%)** - Uses external tool when internal tool available
   - Fix: Add tool selection examples to prompt

2. **Missing required arguments (25%)** - Forgets to specify required parameters
   - Fix: Schema validation before execution

3. **Goal misalignment (20%)** - Plan doesn't achieve stated goal
   - Fix: LLM-as-judge validation of goal-plan alignment

4. **Incomplete plans (15%)** - Missing critical steps (e.g., forgets user preferences)
   - Fix: Completeness checklist based on goal decomposition

5. **Excessive steps (5%)** - Takes 10+ steps when 2-3 sufficient
   - Fix: Add step count budget to prompt

---

### Q5: How do I handle execution failures in agents?

**Strategy:** Implement retry logic with different strategies per failure type.

```python
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def execute_tool(tool_name, args):
    try:
        return tools[tool_name](**args)
    except RateLimitError:
        # Wait and retry (handled by @retry decorator)
        raise
    except ServiceUnavailableError:
        # Try fallback tool
        return execute_fallback_tool(tool_name, args)
    except TimeoutError:
        # Reduce workload and retry
        args["max_results"] = args.get("max_results", 100) // 2
        return tools[tool_name](**args)
    except ValidationError:
        # Planning error, don't retry execution
        raise PlanningError("Invalid plan") from e
```

**Key patterns:**
- Rate limits → Exponential backoff
- Service unavailable → Fallback tools
- Timeout → Reduce workload
- Validation errors → Replan (don't retry execution)

---

### Q6: What metrics should I track for agent systems in production?

**Essential Metrics:**

**Planning Quality:**
- Planning accuracy: % of valid plans
- Tool selection accuracy: % correct tool choices
- Argument validation pass rate: % valid arguments

**Execution Reliability:**
- Execution success rate: % successful executions
- Failure rate by type (timeout, service unavailable, etc.)
- Mean time to recovery (MTTR)

**Efficiency:**
- Average steps per task (lower is better)
- Redundancy rate: % duplicate actions
- Cost per task (tokens + API calls)
- Latency (p50, p95, p99)

**User Experience:**
- Task completion rate: % tasks achieving goal
- User satisfaction score (optional survey)
- Retry rate: % tasks requiring replanning

**Target thresholds (from our benchmarks):**
- Planning accuracy: >85%
- Execution success: >95%
- Task completion: >90%
- Avg steps: <5 for simple tasks, <10 for complex

---

## Common Pitfalls

### ❌ Pitfall 1: Not Validating Plans Before Execution

**Problem:** Executing invalid plans wastes resources and confuses users.

**Example:**
```python
# BAD: No validation
plan = agent.generate_plan(query)
result = agent.execute(plan)  # Might fail with confusing errors
```

**Fix:**
```python
# GOOD: Validate first
plan = agent.generate_plan(query)
validation = validator.validate(plan, tools, query)

if not validation["valid"]:
    # Retry with feedback
    plan = agent.retry_with_feedback(validation["issues"])

result = agent.execute(plan)
```

---

### ❌ Pitfall 2: Evaluating Execution Success Instead of Planning Quality

**Problem:** Focusing on whether tools ran successfully rather than whether the plan was logically correct.

**Example:**
```python
# BAD: Plan executes but achieves wrong goal
User: "Find vegan recipes"
Plan: search_recipes(meal_type="breakfast")  # Executes ✓, wrong goal ✗
Evaluation: "Success (200 OK)" ❌
```

**Fix:** Evaluate plan **before** execution using goal-plan alignment checks.

```python
# GOOD: Check goal alignment
def evaluate_plan(plan, goal):
    return llm_judge(
        prompt=f"Does this plan achieve the goal?\nGoal: {goal}\nPlan: {plan}"
    )
```

---

### ❌ Pitfall 3: Ignoring Conversation Context

**Problem:** Agent doesn't use conversation history or user preferences.

**Example:**
```python
User: "Find Italian recipes"
Agent: [finds recipes]
User: "Show me more like those"
Agent: search_recipes(meal_type="dinner")  # ❌ Ignores "like those"
```

**Fix:** Pass conversation context to planner.

```python
def plan_with_context(query, conversation_history, user_profile):
    context = {
        "previous_queries": conversation_history[-3:],
        "user_preferences": user_profile,
        "previous_results": get_last_results()
    }
    return planner.generate(query, context=context)
```

---

## Real-World Applications

### 1. Customer Support Agent
- **Planning:** Classify issue → Retrieve knowledge → Generate response → Escalate if needed
- **Validation:** Check knowledge base coverage, verify escalation criteria
- **Metrics:** Resolution rate, avg handling time, customer satisfaction

### 2. Data Analysis Agent
- **Planning:** Parse question → Select datasets → Query data → Visualize results
- **Validation:** Check data availability, validate SQL queries, verify visualization types
- **Metrics:** Query success rate, result accuracy, time to insight

### 3. Research Assistant Agent
- **Planning:** Understand topic → Search papers → Extract insights → Synthesize report
- **Validation:** Check search query quality, verify paper relevance, validate citations
- **Metrics:** Paper relevance, citation accuracy, report completeness

### 4. Code Review Agent
- **Planning:** Parse code → Run linters → Check patterns → Generate feedback
- **Validation:** Verify linter configs, check pattern relevance, validate suggestions
- **Metrics:** Bug detection rate, false positive rate, developer acceptance

---

## Integration with Dashboard

The evaluation dashboard (`lesson-9-11/evaluation_dashboard.py`) integrates Lesson 14 results:

**Agent Metrics Section:**
- Planning accuracy (from `planning_validation.json`)
- Tool call accuracy (from `agent_performance.json`)
- Failure breakdown by category (Planning, Execution, Efficiency)
- Efficiency metrics (avg steps, redundancy rate)
- Top failure types and remediation recommendations

**Usage:**
```bash
python lesson-9-11/evaluation_dashboard.py
```

Navigate to **Agent Metrics** tab to view Lesson 14 results.

---

## Next Steps

After completing Lesson 14:

1. **Apply to your domain:**
   - Identify agent tasks in your application
   - Design PVE multi-agent architecture
   - Implement validation before execution

2. **Build production monitoring:**
   - Track planning/execution/efficiency rates
   - Set up alerts for high failure rates
   - Create automated remediation workflows

3. **Explore advanced topics:**
   - Hierarchical agent systems (agents managing agents)
   - Agent memory systems (long-term storage, retrieval)
   - Multi-modal agents (vision, audio, code execution)
   - Agent fine-tuning (training agents on trajectories)

4. **Continue learning:**
   - Task 4.0: Dashboard Integration & Cross-Lesson Testing
   - Explore agent benchmarks: AgentBench, GAIA, WebArena
   - Study production agent systems: LangChain Agents, AutoGPT, BabyAGI

---

## Resources

**Papers:**
- ReAct: Synergizing Reasoning and Acting in Language Models (Yao et al., 2023)
- Reflexion: Language Agents with Verbal Reinforcement Learning (Shinn et al., 2023)
- Generative Agents: Interactive Simulacra of Human Behavior (Park et al., 2023)

**Code Examples:**
- `backend/agent_evaluation.py` - Complete evaluation implementation
- `backend/multi_agent_framework.py` - PVE pattern implementation
- `tests/test_agent_evaluation.py` - TDD test examples

**Related Lessons:**
- [Lesson 10: AI-as-Judge](../lesson-10/TUTORIAL_INDEX.md) - Judge prompt engineering
- [Lesson 13: RAG Generation](../lesson-13/TUTORIAL_INDEX.md) - Attribution evaluation
- [HW5: Agent Failure Analysis](../homeworks/hw5/TUTORIAL_INDEX.md) - Agent debugging

---

**Questions or issues?** Open a discussion in the course repository or review the [Tutorial Changelog](../TUTORIAL_CHANGELOG.md) for updates.
