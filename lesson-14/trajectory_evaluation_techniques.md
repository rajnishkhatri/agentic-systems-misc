# Trajectory Evaluation Techniques

**Reading Time:** 20-25 minutes
**Prerequisites:** Understanding of AI agents, agent workflows, [Agent Evaluation Fundamentals](agent_evaluation_fundamentals.md)
**Learning Outcomes:** Master 6 trajectory-based metrics, create ground-truth references, visualize multi-dimensional agent performance, understand metric selection trade-offs

---

## Table of Contents

1. [Introduction: Why Evaluate Trajectories?](#1-introduction-why-evaluate-trajectories)
2. [Understanding Agent Trajectories](#2-understanding-agent-trajectories)
3. [Ground-Truth Requirements](#3-ground-truth-requirements)
4. [The Six Trajectory Metrics](#4-the-six-trajectory-metrics)
5. [Metric Selection Framework](#5-metric-selection-framework)
6. [Visualization with Radar Charts](#6-visualization-with-radar-charts)
7. [Limitations and Future Directions](#7-limitations-and-future-directions)
8. [Practical Exercises](#8-practical-exercises)
9. [Common Pitfalls](#9-common-pitfalls)
10. [FAQ](#10-faq)

---

## 1. Introduction: Why Evaluate Trajectories?

### The Problem with Final Response Evaluation

Imagine asking an agent to "Book a flight to Paris and notify my team." The agent successfully completes the task, but you later discover:

- It called the flight API 10 times (should have been once)
- It never checked the user's calendar for conflicts
- It sent notifications before confirming the booking
- It cost $5 in API calls when $0.50 would have sufficed

**Final response evaluation** tells you the outcome was correct. **Trajectory evaluation** reveals *how* the agent achieved it—exposing inefficiencies, security risks, and opportunities for optimization.

### What You'll Learn

By the end of this tutorial, you'll be able to:

1. **Define and capture agent trajectories** for evaluation
2. **Apply 6 trajectory metrics** (Exact Match, In-Order Match, Any-Order Match, Precision, Recall, Single-Tool Use)
3. **Create reference trajectories** as ground-truth benchmarks
4. **Select appropriate metrics** based on use case requirements
5. **Visualize multi-dimensional performance** with radar charts
6. **Identify when trajectory evaluation is insufficient** and explore alternatives
7. **Implement trajectory evaluation** in production agent systems

---

## 2. Understanding Agent Trajectories

### 2.1 Definition

**Agent Trajectory**: The complete sequence of actions an agent takes from receiving a user query to producing a final response.

**Example Trajectory** (Customer Support Agent):
```
User Query: "I can't access my account after the password reset"

Agent Trajectory:
1. disambiguate_query(session_history)      # Check if this is a follow-up
2. search_knowledge_base("password reset")  # Look for known issues
3. lookup_user_policy(user_id=12345)        # Check account status
4. call_reset_api(user_id=12345)            # Trigger password reset
5. create_support_ticket(priority="high")   # Escalate to human
6. generate_response()                      # Synthesize answer
```

### 2.2 Components of a Trajectory

Each **action** in a trajectory typically includes:

- **Tool/Function Name**: What the agent called (e.g., `search_knowledge_base`)
- **Parameters**: Arguments passed to the tool (e.g., `"password reset"`)
- **Timestamp**: When the action occurred
- **Result**: Output from the tool (optional for evaluation)

**Simplified Representation** (used in evaluation):
```python
trajectory = [
    "disambiguate_query",
    "search_knowledge_base",
    "lookup_user_policy",
    "call_reset_api",
    "create_support_ticket",
    "generate_response"
]
```

### 2.3 Why Trajectories Matter

**For Developers**:
- **Debug agent behavior**: Identify where the agent goes wrong
- **Optimize performance**: Reduce unnecessary tool calls
- **Ensure correctness**: Verify agent uses the right tools in the right order

**For Business**:
- **Cost control**: Minimize expensive API calls
- **Latency reduction**: Shorter trajectories = faster responses
- **Compliance**: Audit trails for regulated industries

**Example**: A financial services agent that skips `verify_identity` before `process_transaction` is a **security risk**—even if the final response is correct.

---

## 3. Ground-Truth Requirements

### 3.1 Reference Trajectories

All six trajectory metrics require a **reference trajectory** (also called "ideal trajectory" or "ground truth").

**Reference Trajectory**: The expected sequence of actions an agent *should* take for a given query.

**Example**:
```python
# Query: "What's the weather in Paris tomorrow?"
reference_trajectory = [
    "parse_location",      # Extract "Paris"
    "parse_timeframe",     # Extract "tomorrow"
    "call_weather_api",    # Fetch forecast
    "format_response"      # Present to user
]
```

### 3.2 Creating Reference Trajectories

**Method 1: Expert Annotation**
- Domain experts manually define ideal workflows
- **Pros**: High quality, captures nuanced requirements
- **Cons**: Time-consuming, doesn't scale

**Method 2: Trace Collection**
- Capture successful agent executions and label as references
- **Pros**: Faster than manual creation
- **Cons**: May perpetuate suboptimal patterns

**Method 3: Hybrid Approach** (Recommended)
- Start with expert-defined "golden paths"
- Augment with successful traces reviewed by experts
- Iterate based on production insights

### 3.3 Coverage Considerations

**Challenge**: A single query may have multiple valid trajectories.

**Example**:
```
Query: "Find the cheapest flight to Tokyo"

Valid Trajectory A:
[search_flights, filter_by_price, return_cheapest]

Valid Trajectory B:
[search_flights, check_loyalty_discounts, filter_by_price, return_cheapest]
```

**Best Practice**: Create reference sets with:
- **Primary reference**: Most direct path
- **Alternative references**: Valid variations
- **Invalid references**: Common failure patterns (for negative testing)

---

## 4. The Six Trajectory Metrics

### 4.1 Metric 1: Exact Match

#### Definition
Agent's trajectory must **perfectly mirror** the reference trajectory—no extra steps, no missing steps, no reordering.

#### Formula
```python
def exact_match(agent_trajectory: list[str], reference: list[str]) -> bool:
    """Returns True if trajectories are identical."""
    return agent_trajectory == reference
```

#### When to Use
- **Critical workflows** with strict compliance requirements
- **Financial transactions** (e.g., payment processing)
- **Medical diagnosis** workflows
- **Security protocols** (e.g., authentication flows)

#### Example: Payment Processing
```python
# Reference: Compliant payment workflow
reference = [
    "authenticate_user",
    "validate_payment_method",
    "check_fraud_rules",
    "process_payment",
    "send_receipt"
]

# Agent A: Perfect compliance
agent_a = [
    "authenticate_user",
    "validate_payment_method",
    "check_fraud_rules",
    "process_payment",
    "send_receipt"
]
exact_match(agent_a, reference)  # ✅ True

# Agent B: Extra logging step
agent_b = [
    "authenticate_user",
    "log_attempt",  # ❌ Extra step
    "validate_payment_method",
    "check_fraud_rules",
    "process_payment",
    "send_receipt"
]
exact_match(agent_b, reference)  # ❌ False
```

#### Trade-offs
- **Pros**: Highest precision, clear pass/fail criteria
- **Cons**: Inflexible, may penalize harmless optimizations

---

### 4.2 Metric 2: In-Order Match

#### Definition
Agent must complete **core steps in the correct sequence**, but additional actions are permitted.

#### Formula
```python
def in_order_match(agent_trajectory: list[str], reference: list[str]) -> bool:
    """Returns True if reference steps appear in order (extras allowed)."""
    ref_index = 0
    for action in agent_trajectory:
        if ref_index < len(reference) and action == reference[ref_index]:
            ref_index += 1
    return ref_index == len(reference)
```

#### When to Use
- **Workflows with required sequence** but optional intermediate steps
- **Debugging scenarios** where extra logging is acceptable
- **Research agents** that explore multiple sources

#### Example: E-commerce Checkout
```python
reference = ["search_product", "add_to_cart", "checkout"]

# Agent A: Added stock validation
agent_a = ["search_product", "log_search", "add_to_cart", "validate_stock", "checkout"]
in_order_match(agent_a, reference)  # ✅ True
# Core steps: search → add → checkout (in order)
# Extra steps: log_search, validate_stock (permitted)

# Agent B: Reordered steps
agent_b = ["add_to_cart", "search_product", "checkout"]
in_order_match(agent_b, reference)  # ❌ False
# Core steps out of order (add before search)
```

#### Trade-offs
- **Pros**: More flexible than exact match, tolerates agent exploration
- **Cons**: Doesn't penalize inefficient extra steps

---

### 4.3 Metric 3: Any-Order Match

#### Definition
Agent must include **all necessary actions**, but order is irrelevant.

#### Formula
```python
def any_order_match(agent_trajectory: list[str], reference: list[str]) -> bool:
    """Returns True if all reference actions are present (order ignored)."""
    return set(reference).issubset(set(agent_trajectory))
```

#### When to Use
- **Parallel execution** scenarios (actions can run concurrently)
- **Independent task completion** (order doesn't affect outcome)
- **Data aggregation** from multiple sources

#### Example: Multi-Source Data Fetch
```python
reference = ["fetch_weather", "fetch_news", "fetch_calendar"]

# Agent A: Different order + extra step
agent_a = ["fetch_calendar", "check_network", "fetch_weather", "fetch_news"]
any_order_match(agent_a, reference)  # ✅ True
# All reference actions present (order doesn't matter)

# Agent B: Missing action
agent_b = ["fetch_calendar", "fetch_weather"]
any_order_match(agent_b, reference)  # ❌ False
# Missing: fetch_news
```

#### Trade-offs
- **Pros**: Ideal for parallel/concurrent workflows
- **Cons**: Ignores efficiency (doesn't penalize redundant calls)

---

### 4.4 Metric 4: Precision

#### Definition
Percentage of agent's tool calls that are **correct/relevant** according to the reference trajectory.

#### Formula
```python
def precision(agent_trajectory: list[str], reference: list[str]) -> float:
    """Returns precision score [0.0, 1.0]."""
    if not agent_trajectory:
        return 0.0
    correct_calls = sum(1 for action in agent_trajectory if action in reference)
    return correct_calls / len(agent_trajectory)
```

#### When to Use
- **Cost-sensitive applications** (minimize expensive API calls)
- **Latency optimization** (reduce unnecessary steps)
- **Agent efficiency benchmarking**

#### Example: Document Search
```python
reference = ["search_docs", "summarize"]

# Agent A: Added irrelevant steps
agent_a = ["search_docs", "search_web", "summarize", "log_result"]
precision(agent_a, reference)  # 2 correct / 4 total = 0.50 (50%)
# Correct: search_docs, summarize
# Incorrect/extra: search_web, log_result

# Agent B: Perfect precision
agent_b = ["search_docs", "summarize"]
precision(agent_b, reference)  # 2 correct / 2 total = 1.00 (100%)
```

#### Interpretation
- **High Precision (≥0.9)**: Agent is focused, minimal noise
- **Low Precision (<0.5)**: Agent is making many irrelevant calls

#### Trade-offs
- **Pros**: Quantifies efficiency, easy to compare agents
- **Cons**: Doesn't penalize missing actions (use with Recall)

---

### 4.5 Metric 5: Recall

#### Definition
Percentage of essential tool calls from the reference trajectory that the agent **successfully captured**.

#### Formula
```python
def recall(agent_trajectory: list[str], reference: list[str]) -> float:
    """Returns recall score [0.0, 1.0]."""
    if not reference:
        return 1.0
    captured = sum(1 for action in reference if action in agent_trajectory)
    return captured / len(reference)
```

#### When to Use
- **Safety-critical applications** (all steps must be completed)
- **Compliance workflows** (complete audit trail required)
- **Security protocols** (missing steps = vulnerabilities)

#### Example: User Authentication
```python
reference = ["validate_user", "check_permissions", "execute_action", "log_audit"]

# Agent A: Skipped permission check
agent_a = ["validate_user", "execute_action", "log_audit"]
recall(agent_a, reference)  # 3 captured / 4 essential = 0.75 (75%)
# Missing: check_permissions ❌ Security risk!

# Agent B: Complete coverage
agent_b = ["validate_user", "check_permissions", "execute_action", "log_audit", "send_notification"]
recall(agent_b, reference)  # 4 captured / 4 essential = 1.00 (100%)
# Extra step (send_notification) doesn't hurt recall
```

#### Interpretation
- **High Recall (≥0.9)**: Agent covers all essential steps
- **Low Recall (<0.7)**: Agent is missing critical actions

#### Trade-offs
- **Pros**: Ensures completeness, critical for safety
- **Cons**: Doesn't penalize extra steps (use with Precision)

---

### 4.6 Metric 6: Single-Tool Use

#### Definition
Binary check: Did the agent use a **specific tool** at least once?

#### Formula
```python
def single_tool_use(agent_trajectory: list[str], tool_name: str) -> bool:
    """Returns True if tool appears in trajectory."""
    return tool_name in agent_trajectory
```

#### When to Use
- **Tool adoption monitoring** (verify agents use new tools)
- **A/B testing** (compare tool usage across variants)
- **Feature validation** (ensure critical tools are called)

#### Example: Notification Tool
```python
agent_a = ["process_request", "update_database", "send_notification"]
single_tool_use(agent_a, "send_notification")  # ✅ True

agent_b = ["process_request", "update_database"]
single_tool_use(agent_b, "send_notification")  # ❌ False
```

#### Use Case: A/B Testing
```python
# Test if new RAG tool is being used
control_group = ["search_faq", "generate_response"]
treatment_group = ["search_faq", "search_vector_db", "generate_response"]

assert single_tool_use(treatment_group, "search_vector_db")  # ✅ True
```

#### Trade-offs
- **Pros**: Simple, actionable for tool adoption
- **Cons**: Binary (doesn't measure quality of tool use)

---

## 5. Metric Selection Framework

### 5.1 Decision Tree

```
┌─────────────────────────────────────────────────────────────┐
│          TRAJECTORY METRIC SELECTION GUIDE                  │
└─────────────────────────────────────────────────────────────┘

START: What is your primary evaluation goal?

├─ [Goal 1] Strict compliance / Safety-critical workflow
│   ├─ Order matters? YES → Exact Match
│   └─ Order matters? NO  → Any-Order Match + Recall = 1.0
│
├─ [Goal 2] Optimize efficiency / Reduce costs
│   └─ Use: Precision (minimize unnecessary calls)
│
├─ [Goal 3] Ensure completeness / Avoid missing steps
│   └─ Use: Recall (capture all essential actions)
│
├─ [Goal 4] Balance efficiency + completeness
│   └─ Use: Precision + Recall (or F1-Score)
│
├─ [Goal 5] Allow flexibility but maintain sequence
│   └─ Use: In-Order Match
│
└─ [Goal 6] Monitor specific tool adoption
    └─ Use: Single-Tool Use
```

### 5.2 Multi-Metric Analysis

**Best Practice**: Use multiple metrics to get a comprehensive view.

**Example Scenario**:
```python
reference = ["auth", "check_balance", "process_payment", "send_receipt"]
agent = ["auth", "process_payment", "send_receipt", "log_transaction"]

# Results:
# Exact Match:     ❌ False (reordered, missing check_balance)
# In-Order Match:  ❌ False (check_balance missing from sequence)
# Any-Order Match: ❌ False (missing check_balance)
# Precision:       0.75 (3 correct / 4 total)
# Recall:          0.75 (3 captured / 4 essential)
# Single-Tool Use: ✅ True (for "process_payment")
```

**Interpretation**:
- **High Precision + Low Recall** → Agent is accurate but incomplete (missing steps)
- **Low Precision + High Recall** → Agent is thorough but inefficient (extra steps)
- **Both Low** → Agent is both incomplete and inefficient (needs redesign)

---

## 6. Visualization with Radar Charts

### 6.1 Why Radar Charts?

**Radar charts** (also called spider charts) display multiple metrics simultaneously, making it easy to:
- **Compare agent versions** at a glance
- **Identify strengths and weaknesses** across dimensions
- **Track improvements** over iterations

### 6.2 Example Radar Chart

```
                  Exact Match (0.2)
                        /\
                       /  \
                      /    \
         Precision   /      \   Recall
            (0.85)  /        \  (0.70)
                   /          \
                  /     ●      \
                 /    Agent A   \
                /________________\
      In-Order Match         Any-Order Match
          (0.50)                 (0.60)

Legend:
● Agent A: High precision, moderate recall, low exact match
○ Agent B: Balanced performance (not shown)
```

### 6.3 Implementation

```python
import matplotlib.pyplot as plt
import numpy as np

def plot_trajectory_metrics(metrics: dict[str, float], title: str):
    """Create radar chart for trajectory metrics.

    Args:
        metrics: Dictionary of metric names to scores [0.0, 1.0]
        title: Chart title (e.g., "Agent A vs. Reference")
    """
    categories = list(metrics.keys())
    values = list(metrics.values())

    # Number of metrics
    N = len(categories)

    # Compute angle for each metric
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    values += values[:1]  # Close the plot
    angles += angles[:1]

    # Initialize plot
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))

    # Draw the chart
    ax.plot(angles, values, 'o-', linewidth=2, label=title)
    ax.fill(angles, values, alpha=0.25)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories)
    ax.set_ylim(0, 1)
    ax.legend(loc='upper right')

    plt.show()

# Usage
metrics = {
    "Exact Match": 0.2,
    "In-Order": 0.5,
    "Any-Order": 0.6,
    "Precision": 0.85,
    "Recall": 0.70
}
plot_trajectory_metrics(metrics, "Agent A Performance")
```

### 6.4 Comparative Analysis

**Scenario**: Comparing two agent versions

```python
# Agent A (original): High precision, low recall
agent_a_metrics = {
    "Exact Match": 0.1,
    "Precision": 0.9,
    "Recall": 0.6,
    "In-Order": 0.4
}

# Agent B (improved): Balanced precision/recall
agent_b_metrics = {
    "Exact Match": 0.3,
    "Precision": 0.8,
    "Recall": 0.85,
    "In-Order": 0.7
}
```

**Visual Insight**: Agent B's radar chart shows more balanced coverage → better for production.

---

## 7. Limitations and Future Directions

### 7.1 Limitations of Ground-Truth Trajectory Evaluation

**Challenge 1: Manual Effort**
- Creating reference trajectories is time-consuming
- Doesn't scale to thousands of queries
- May not cover all valid approaches

**Challenge 2: Assumes Single "Correct" Path**
- Real-world queries often have multiple valid solutions
- Penalizes creative but effective approaches
- Rigid evaluation may stifle agent innovation

**Challenge 3: Doesn't Evaluate Reasoning Quality**
- Focuses on *what* tools were called, not *why*
- Agent may call correct tools for wrong reasons
- Trajectory match ≠ correct reasoning

### 7.2 Future Direction: Agent-as-a-Judge

**Research Advancement**: LLMs can evaluate whether a trajectory is **reasonable**, not just matching a reference.

**Key Paper**: Mingchen Zhuge et al., 2024. "Agent-as-a-Judge: Evaluate Agents with Agents"

**How It Works**:
```python
# Instead of comparing to reference trajectory:
reference = ["search", "summarize"]
agent_trajectory = ["search", "validate_sources", "summarize"]
# Traditional: ❌ Fails (extra step)

# Agent-as-a-Judge approach:
judge_prompt = f"""
Evaluate if this agent trajectory is reasonable for the query.

Query: "Summarize the latest research on climate change"
Trajectory: {agent_trajectory}

Criteria:
1. Are all steps relevant to the task?
2. Are critical steps missing?
3. Is the sequence logical?
"""
# LLM Judge: ✅ Passes (validate_sources is prudent for research task)
```

**Benefits**:
- **Flexible evaluation**: Accepts multiple valid paths
- **Reasoning-aware**: Can assess *why* tools were called
- **Scalable**: No need for exhaustive reference sets

**Limitations**:
- **Cost**: LLM calls for every evaluation
- **Reliability**: Judge LLM can be inconsistent
- **Calibration**: Requires validation against human judgment

---

## 8. Practical Exercises

### Exercise 1: Metric Calculation

**Scenario**: E-commerce agent processing "Cancel my order #12345"

```python
reference = ["authenticate", "lookup_order", "check_cancellation_policy", "cancel_order", "send_confirmation"]

agent_a = ["authenticate", "lookup_order", "cancel_order", "send_confirmation"]
agent_b = ["authenticate", "lookup_order", "check_cancellation_policy", "cancel_order", "send_confirmation", "log_cancellation"]
agent_c = ["lookup_order", "cancel_order", "send_confirmation"]
```

**Tasks**:
1. Calculate **Precision** and **Recall** for each agent
2. Which agent has the highest **Exact Match** score?
3. Which agent has the highest **F1-Score** (harmonic mean of Precision and Recall)?
4. Which agent would you deploy to production? Why?

**Answers**:
```python
# Agent A:
# Precision: 4/4 = 1.00
# Recall: 4/5 = 0.80 (missing: check_cancellation_policy)
# Exact Match: False

# Agent B:
# Precision: 5/6 = 0.83
# Recall: 5/5 = 1.00
# Exact Match: False

# Agent C:
# Precision: 3/3 = 1.00
# Recall: 3/5 = 0.60 (missing: authenticate, check_cancellation_policy)
# Exact Match: False

# Recommendation: Agent B (complete coverage, minor efficiency cost acceptable)
```

---

### Exercise 2: Metric Selection

For each scenario, select the **most appropriate** trajectory metric:

1. **Medical diagnosis agent**: Must follow FDA-approved diagnostic protocol exactly
2. **Research agent**: Gathers information from 5 independent sources (order doesn't matter)
3. **Payment processing**: Must authenticate → validate → process (in order), but can add fraud checks
4. **Cost optimization**: Minimize API calls to reduce cloud expenses
5. **Security audit**: Ensure agent never skips the "verify_credentials" step

**Answers**:
1. **Exact Match** (strict compliance)
2. **Any-Order Match** (parallel execution)
3. **In-Order Match** (required sequence, extras allowed)
4. **Precision** (penalizes extra calls)
5. **Single-Tool Use** ("verify_credentials") + **Recall** (ensure completeness)

---

### Exercise 3: Debugging with Trajectories

**Scenario**: Agent is slow and expensive.

```python
reference = ["search_docs", "generate_response"]
agent_trajectory = [
    "search_docs",
    "search_docs",  # Duplicate!
    "search_web",
    "search_docs",  # Triplicate!
    "generate_response"
]
```

**Questions**:
1. What is the **Precision** score?
2. What is the **Recall** score?
3. What optimization would you recommend?

**Answers**:
```python
# Precision: 4/5 = 0.80 (search_web is extra)
# Recall: 2/2 = 1.00 (all essential steps covered)
# Recommendation: Add deduplication logic to prevent redundant tool calls
```

---

## 9. Common Pitfalls

### Pitfall 1: Over-Reliance on Exact Match

**Mistake**: Using Exact Match for all workflows.

**Why It's Wrong**: Penalizes harmless improvements (e.g., adding caching, logging).

**Fix**: Use In-Order Match or Any-Order Match for flexible workflows.

---

### Pitfall 2: Ignoring Precision-Recall Trade-off

**Mistake**: Optimizing for Precision alone.

**Example**:
```python
# High precision, low recall
agent = ["authenticate"]  # Skips everything else!
precision = 1.0  # ✅ Perfect!
recall = 0.25    # ❌ Terrible!
```

**Fix**: Monitor **both** Precision and Recall, or use **F1-Score**.

---

### Pitfall 3: Not Validating Reference Trajectories

**Mistake**: Assuming reference trajectories are always correct.

**Reality**: Production insights may reveal better paths.

**Fix**: Periodically review and update references based on:
- Agent performance data
- User feedback
- Domain expert input

---

### Pitfall 4: Treating All Tools Equally

**Mistake**: Counting `log_debug` and `process_payment` with equal weight.

**Fix**: Use **weighted metrics** for critical tools:
```python
def weighted_recall(agent_traj, reference, weights):
    """Recall with tool importance weights."""
    total_weight = sum(weights.values())
    captured_weight = sum(
        weights[tool] for tool in reference if tool in agent_traj
    )
    return captured_weight / total_weight
```

---

### Pitfall 5: No Negative Test Cases

**Mistake**: Only testing successful trajectories.

**Fix**: Create reference sets for **failure modes**:
```python
# Expected behavior when user is unauthorized
reference_unauthorized = ["authenticate"]  # Should stop here
agent = ["authenticate", "process_payment"]  # ❌ Security violation!
```

---

## 10. FAQ

### Q1: How many reference trajectories do I need?

**A**: Depends on query diversity:
- **Simple workflows**: 10-20 references
- **Complex agents**: 100+ references covering edge cases
- **Rule of thumb**: Cover 80% of production query types

---

### Q2: Can I combine trajectory metrics with final response evaluation?

**A**: Yes! Recommended approach:
1. **Trajectory metrics**: Ensure correct process
2. **Final response metrics**: Ensure correct output
3. **Composite score**: `0.5 * trajectory_score + 0.5 * response_score`

---

### Q3: What if my agent uses tools in parallel?

**A**: Use **Any-Order Match** or modify metrics to account for concurrency:
```python
# Group parallel actions as sets
reference = [{"fetch_weather", "fetch_news"}, "summarize"]
# Order matters between groups, not within groups
```

---

### Q4: How do I handle stochastic tool calls (e.g., retries)?

**A**: Normalize trajectories:
```python
# Before evaluation
agent_trajectory = ["search", "search", "search", "summarize"]
normalized = list(dict.fromkeys(agent_trajectory))  # Remove duplicates
# Result: ["search", "summarize"]
```

---

### Q5: Can I use trajectory metrics for multi-agent systems?

**A**: Yes, with modifications:
- **Per-agent trajectories**: Evaluate each agent's path separately
- **System-level trajectory**: Track inter-agent handoffs
- **See also**: [Multi-Agent Orchestration](multi_agent_orchestration.md)

---

## Key Takeaways

1. **Trajectory evaluation reveals *how* agents work**, not just *what* they produce
2. **Six metrics serve different purposes**: Choose based on your use case (compliance, efficiency, completeness)
3. **Ground-truth references are essential** but require maintenance and validation
4. **Multi-metric analysis** provides comprehensive insights (use radar charts)
5. **Precision-Recall trade-off** is critical: optimize for both, not just one
6. **Future directions**: Agent-as-a-Judge will reduce manual reference creation
7. **Production workflow**: Trajectory metrics → identify issues → optimize → re-evaluate

---

## Related Resources

**Prerequisites**:
- [Agent Evaluation Fundamentals](agent_evaluation_fundamentals.md) - AgentOps evolution, success metrics

**Next Steps**:
- [Autorater & Final Response Evaluation](autorater_final_response_eval.md) - LLM-as-Judge for agent outputs
- [Human-in-the-Loop Evaluation](human_in_the_loop_evaluation.md) - HITL workflows

**Interactive Practice**:
- [Trajectory Evaluation Tutorial (Notebook)](trajectory_evaluation_tutorial.ipynb) - Hands-on implementation

**Visual Aids**:
- `diagrams/trajectory_metrics_comparison.mmd` - Radar chart examples
- `diagrams/agent_evaluation_components.mmd` - Evaluation architecture

**Code Examples**:
- `backend/trajectory_evaluation.py` - Production-ready implementation
- `tests/test_trajectory_evaluation.py` - Comprehensive test suite

---

**Reading Time Checkpoint**: If you've reached this point, you've completed a 20-25 minute deep dive into trajectory evaluation techniques. You're now equipped to implement ground-truth-based agent evaluation in production systems.

**Next Action**: Proceed to [Task 4.3: Autorater & Final Response Evaluation](autorater_final_response_eval.md) to learn how LLMs can evaluate agent outputs without ground-truth references.
