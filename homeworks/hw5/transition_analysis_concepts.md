# Transition Analysis Concepts Tutorial

## Learning Objectives

By completing this tutorial, you will be able to:
- ✅ Understand state-based modeling for multi-step agent systems
- ✅ Define failure transitions and identify them in conversation traces
- ✅ Distinguish between last successful state and first failing state
- ✅ Build transition count matrices from labeled failure data
- ✅ Interpret transition frequencies to identify bottlenecks
- ✅ Recognize common failure patterns (sequential, clustered, distributed)
- ✅ Propose targeted system improvements based on transition analysis

## Prerequisites

- Completed [HW2: Error Analysis](../hw2/error_analysis_concepts.md)
- Understanding of failure taxonomies and qualitative evaluation
- Basic familiarity with matrix interpretation
- Experience analyzing conversational AI systems

## Estimated Time

**Reading Time:** 18-22 minutes
**Hands-on Practice:** 30-40 minutes (when building your own matrices)

---

## Concepts

### What is State-Based Modeling?

**State-based modeling** represents complex systems as a sequence of discrete states with transitions between them.

**Traditional Error Analysis (HW2):**
```
Trace → Manual Review → "Recipe search failed" (qualitative)
```
**Problem:** Qualitative. Can't quantify which stages fail most often.

**State-Based Analysis (HW5):**
```
Trace → State Sequence → Identify Failure Transition → Count Frequencies → Heatmap
```
**Benefit:** Quantitative. See exactly where failures cluster.

### Agent Pipeline as a State Machine

Consider a recipe chatbot with a **10-state pipeline**:

```
┌─────────────────────────────────────────────────────┐
│            RECIPE BOT STATE PIPELINE                │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ParseRequest → PlanToolCalls → GenCustomerArgs    │
│  → GetCustomerProfile → GenRecipeArgs → GetRecipes │
│  → GenWebArgs → GetWebInfo → ComposeResponse       │
│  → DeliverResponse                                  │
│                                                     │
│  User Query ──────────────────────────> Answer      │
└─────────────────────────────────────────────────────┘
```

**Each state** represents either:
- **LLM operation**: Parse, plan, generate arguments, compose
- **Tool execution**: Call customer DB, recipe DB, web search
- **System operation**: Deliver response

**Key Insight:** Every conversation progresses through this pipeline until it hits a failure.

---

## Failure Transitions

### Definition

A **failure transition** is the directed edge from:
- **Last Successful State**: The final state that completed without error
- **First Failing State**: The immediate next state that encountered an error

**Visual Example:**

```
Successful Execution:
ParseRequest ✓ → PlanToolCalls ✓ → GenRecipeArgs ✓ → GetRecipes ✓ → ComposeResponse ✓

Failed Execution:
ParseRequest ✓ → PlanToolCalls ✓ → GenRecipeArgs ✓ → GetRecipes ✗
                                                    ↑              ↑
                                              Last Success   First Failure

Failure Transition: (GenRecipeArgs → GetRecipes)
```

### Why Failure Transitions Matter

**Traditional Logging:**
```
ERROR: Recipe search failed
```
**Question:** Was it the LLM that generated bad search arguments, or the search tool that failed to find results?

**Transition Analysis:**
```
Failure Transition: (GenRecipeArgs → GetRecipes)
Frequency: 22 occurrences out of 100 traces
```
**Answer:** The tool execution fails, not argument generation. The issue is likely:
- Empty search results (data quality problem)
- Search index configuration (retrieval problem)
- Query format mismatch (interface problem)

### Identifying Failure Transitions in Traces

**Example Trace Structure:**
```json
{
  "trace_id": "trace_042",
  "messages": [...],
  "last_successful_state": "GenRecipeArgs",
  "first_failing_state": "GetRecipes",
  "failure_mode": "tool_execution_error"
}
```

**Extraction:**
1. Read `last_successful_state`
2. Read `first_failing_state`
3. Record pair: `(last_successful_state, first_failing_state)`
4. This is your failure transition

---

## Transition Matrices

### What is a Transition Matrix?

A **transition matrix** counts how many times each `(last_success → first_failure)` pair occurs across all traces.

**Matrix Structure:**
```
               First Failing State →
            Parse  Plan  GenRec  GetRec  Compose
Last     ┌────────────────────────────────────┐
Success  │                                    │
  ↓      │                                    │
Parse    │   0      3      0       0       0  │
Plan     │   0      0      5       0       2  │
GenRec   │   0      0      0      22       0  │
GetRec   │   0      0      0       0       8  │
Compose  │   0      0      0       0       0  │
         └────────────────────────────────────┘
```

**Reading the Matrix:**
- **Rows**: Where the system last succeeded
- **Columns**: Where the system first failed
- **Cell value**: Number of traces with that transition

**Example Interpretation:**
- Cell `(GenRecipe, GetRecipe) = 22`: 22 traces failed at recipe search after successfully generating search arguments
- Cell `(Plan, GenRec) = 5`: 5 traces failed when generating recipe arguments after successfully planning tool calls
- Cell `(Plan, Compose) = 2`: 2 traces skipped intermediate states and failed at composition

### Building a Transition Matrix

**Algorithm:**
```python
import pandas as pd
from collections import Counter

def build_transition_matrix(traces):
    # Extract all failure transitions
    transitions = [
        (trace['last_successful_state'], trace['first_failing_state'])
        for trace in traces
    ]

    # Count frequencies
    transition_counts = Counter(transitions)

    # Get all unique states
    all_states = sorted(set(
        [t[0] for t in transitions] + [t[1] for t in transitions]
    ))

    # Build matrix
    matrix = pd.DataFrame(0, index=all_states, columns=all_states)

    for (last_success, first_fail), count in transition_counts.items():
        matrix.loc[last_success, first_fail] = count

    return matrix
```

---

## Interpreting Transition Patterns

### Pattern 1: Single High-Frequency Cell (Clustered Failure)

**Matrix:**
```
              GenRec  GetRec  Compose
GenRec           0      35       2
GetRec           0       0      12
Compose          0       0       0
```

**Interpretation:**
- **35 failures** at `GetRecipes` after `GenRecipeArgs` succeeds
- This is a **bottleneck**: Recipe search tool fails frequently
- **Root cause likely**: Tool execution issue, not LLM generation issue

**Action Items:**
- Investigate `GetRecipes` tool: Why does it return empty results?
- Review search index quality
- Check if LLM-generated queries are too specific
- Add fallback handling for empty results

### Pattern 2: Column-Heavy (State Fails Across Predecessors)

**Matrix:**
```
              Compose
GenRec          8
GetRec         12
GenWeb          6
GetWeb          9
```

**Interpretation:**
- `ComposeResponse` fails from **multiple** prior states
- **Root cause likely**: LLM composition failures, not tool issues
- The composition prompt may be brittle when context varies

**Action Items:**
- Review composition prompt robustness
- Test with diverse context inputs
- Add error handling for missing context fields

### Pattern 3: Row-Heavy (After State, Multiple Failures)

**Matrix:**
```
              GenRec  GetRec  GenWeb  GetWeb
Plan            12       8       5       3
```

**Interpretation:**
- After `PlanToolCalls`, failures scatter across next states
- **Root cause likely**: Planning step is flaky
- Sometimes plans work, sometimes they don't

**Action Items:**
- Improve planning prompt clarity
- Add validation logic after planning
- Ensure tool call plans are executable

### Pattern 4: Distributed Failures (No Clear Pattern)

**Matrix:**
```
              Plan  GenRec  GetRec  Compose
Parse           2      3       1       2
Plan            0      4       2       3
GenRec          0      0       5       1
GetRec          0      0       0       6
```

**Interpretation:**
- Failures distributed across many transitions
- **Root cause likely**: Data quality issues or diverse failure modes
- No single bottleneck to fix

**Action Items:**
- Drill into individual traces for qualitative analysis (return to HW2 methods)
- Group traces by customer persona or query type
- Consider if state definitions are too coarse

---

## LLM Failures vs. Tool Failures

### Why This Distinction Matters

**State Types:**
1. **LLM States**: `ParseRequest`, `PlanToolCalls`, `GenRecipeArgs`, `ComposeResponse`
2. **Tool States**: `GetCustomerProfile`, `GetRecipes`, `GetWebInfo`
3. **System States**: `DeliverResponse`

**Different Solutions:**
- **LLM failures** → Fix prompts, add examples, improve model
- **Tool failures** → Fix APIs, improve data quality, add retries
- **System failures** → Fix infrastructure, add monitoring

### Example Analysis

**Scenario:** High failure count at `(GenRecipeArgs → GetRecipes)`

**Question:** Is the LLM generating bad arguments, or is the tool failing?

**Investigation:**
1. **Examine failing traces**:
   - Look at `GenRecipeArgs` output (LLM-generated search query)
   - Look at `GetRecipes` output (tool results)

2. **Pattern A: LLM generates invalid arguments**
   ```json
   GenRecipeArgs output: {"query": "xyzabc123", "limit": -5}
   GetRecipes error: "Invalid query format"
   ```
   **Diagnosis:** LLM failure. Fix prompt to generate valid queries.

3. **Pattern B: LLM generates valid arguments, tool returns empty**
   ```json
   GenRecipeArgs output: {"query": "vegan pasta gluten-free", "limit": 10}
   GetRecipes output: {"results": [], "total": 0}
   ```
   **Diagnosis:** Tool failure (data quality). Add more recipes or improve search.

**Takeaway:** Transition analysis identifies **where** failures happen. Trace inspection identifies **why**.

---

## Bottleneck Identification Strategies

### Strategy 1: Sum by Column (Which State Fails Most?)

**Calculation:**
```
Sum failures by column = "How often does each state fail?"
```

**Example:**
```
              Parse  GenRec  GetRec  Compose  Total Failures
Total Fails      5      12      35       8         60
```

**Interpretation:** `GetRecipes` fails 35/60 times (58%). This is your **primary bottleneck**.

**Action:** Prioritize fixing `GetRecipes` tool.

### Strategy 2: Sum by Row (After Which State Do Failures Occur?)

**Calculation:**
```
Sum failures by row = "After which state do we see the most failures?"
```

**Example:**
```
              Failures After This State
GenRec                  40
Plan                    15
GetRec                   5
```

**Interpretation:** 40/60 failures happen immediately after `GenRecipeArgs`.

**Hypothesis:** `GenRecipeArgs` output is often incorrect, causing downstream failures.

**Action:** Improve `GenRecipeArgs` prompt or add validation.

### Strategy 3: Diagonal Analysis (Same State Success → Fail)

**Matrix:**
```
              Parse  Plan  GenRec
Parse           12      0      0
Plan             0      8      0
GenRec           0      0      5
```

**Interpretation:** Failures on the **diagonal** mean a state succeeds, then immediately fails on re-execution.

**Diagnosis:** Flaky LLM or non-deterministic tool behavior.

**Action:** Add temperature=0 for determinism, or investigate tool intermittency.

---

## When State-Based Analysis is Appropriate

### ✅ Good Use Cases

**1. Multi-Step Agent Systems**
- Recipe bots with planning → retrieval → composition pipeline
- Customer support agents with intent → lookup → response flow
- Code generation with parse → plan → generate → validate stages

**Why it works:** Clear state boundaries, failures occur at specific steps.

**2. Production Debugging at Scale**
- 1000s of conversation traces to analyze
- Need to identify systemic bottlenecks quickly
- Complement qualitative error analysis (HW2) with quantitative metrics

**Why it works:** Transition matrices surface patterns invisible in individual traces.

**3. Iterative System Improvement**
- Fix the highest-frequency failure transition
- Re-run evaluation and rebuild matrix
- Verify that bottleneck has shifted or disappeared

**Why it works:** Provides clear before/after comparison.

### ❌ When to Avoid State-Based Analysis

**1. Ambiguous State Boundaries**
- System has no clear pipeline stages
- States overlap or are ill-defined
- Difficult to label "last success" vs. "first failure"

**Problem:** Garbage in, garbage out. Bad state labels → meaningless matrices.

**2. Very Small Datasets**
- <30 failure traces
- Matrix will be sparse and unreliable

**Problem:** Can't identify statistically significant patterns.

**3. Extremely Diverse Failure Modes**
- Every trace fails differently
- No clustering in transition matrix

**Problem:** Transition analysis won't reveal bottlenecks. Use HW2 qualitative methods instead.

---

## Common Pitfalls

### Data Labeling Pitfalls

#### 1. Mislabeling Last Success / First Failure
**❌ Problem:** Ambiguous state boundaries lead to inconsistent labeling

**Example:**
```
Trace: GenRecipeArgs generates invalid JSON, GetRecipes throws error
Mislabel: Last success = GenRecipeArgs, First failure = GetRecipes
Correct: Last success = PlanToolCalls, First failure = GenRecipeArgs
```

**Why it's wrong:** If `GenRecipeArgs` produced invalid output, it didn't actually succeed.

**✅ Solution:** Define "success" as "state produced valid output accepted by next state."

#### 2. Skipping Intermediate States
**❌ Problem:** Labeling transitions that skip stages

**Example:**
```
Actual sequence: Parse ✓ → Plan ✓ → GenRec ✗ → GetRec (never called)
Mislabel: Transition (Plan → GetRec)
Correct: Transition (Plan → GenRec)
```

**✅ Solution:** Only label **consecutive** states. Failure happens at the first state attempted that fails.

### Interpretation Pitfalls

#### 3. Focusing on Rare Transitions
**❌ Problem:** Investigating a transition with 1 occurrence when another has 30

**Example:**
```
(Plan → GetWeb) = 1 occurrence → Spend hours debugging
(GenRec → GetRec) = 30 occurrences → Ignore
```

**✅ Solution:** Prioritize by frequency. Fix the 30-occurrence bottleneck first.

#### 4. Ignoring State Type (LLM vs Tool)
**❌ Problem:** Applying wrong fix because didn't check state type

**Example:**
```
High failures at GetRecipes (a tool state)
Wrong fix: Improve LLM prompt
Correct fix: Fix tool data quality or API
```

**✅ Solution:** Always check if failing state is LLM or Tool before proposing solutions.

#### 5. Not Validating Hypotheses
**❌ Problem:** Making assumptions without inspecting actual traces

**Example:**
```
Matrix shows (GenRec → GetRec) = 25 failures
Assumption: "Recipe search is broken"
Reality: LLM generates queries in wrong language
```

**✅ Solution:** After identifying high-frequency transition, **read the traces** to validate hypothesis.

### Visualization Pitfalls

#### 6. Poor Color Scheme
**❌ Problem:** Rainbow heatmap obscures patterns

**Bad:**
```python
sns.heatmap(matrix, cmap="jet")  # Rainbow = confusing
```

**✅ Solution:**
```python
sns.heatmap(matrix, cmap="YlOrRd", annot=True, fmt="d")  # Sequential = clear
```

#### 7. No Annotations
**❌ Problem:** Heatmap shows colors but no numbers

**Bad:** Can't tell if cell is 5 or 50.

**✅ Solution:** Always use `annot=True, fmt="d"` in seaborn to show counts.

#### 8. Unordered States
**❌ Problem:** States appear in random order, hiding pipeline flow

**Bad:**
```
Matrix rows: [Compose, Parse, GetRec, Plan, GenRec]
```

**✅ Solution:** Order states by pipeline sequence:
```
Matrix rows: [Parse, Plan, GenRec, GetRec, Compose]
```

---

## Key Takeaways

- ✅ **State-based modeling quantifies failure locations** - Complements HW2 qualitative analysis with metrics
- ✅ **Failure transitions = (last success → first failure)** - Pinpoint exactly where in the pipeline failures occur
- ✅ **Transition matrices reveal bottlenecks** - High-frequency cells indicate systemic problems
- ✅ **LLM vs Tool failures need different fixes** - Analyze state type before proposing solutions
- ✅ **Column sums = how often a state fails** - Identifies primary bottleneck
- ✅ **Row sums = after which state failures occur** - Identifies upstream causes
- ✅ **Always validate with trace inspection** - Matrices show "where," traces show "why"
- ✅ **Iterate: fix top bottleneck, rebuild matrix** - Quantify improvement after each fix

---

## Further Reading

### Related Tutorials
- [Heatmap Visualization Tutorial](heatmap_visualization_tutorial.ipynb) - Build and visualize transition matrices
- [Transition Matrix Diagram](diagrams/transition_matrix_concept.mmd) ([PNG version](diagrams/transition_matrix_concept.png)) - Visual reference for state pipeline
- [Error Analysis Concepts](../hw2/error_analysis_concepts.md) - Prerequisite qualitative methodology
- [HW5 Tutorial Index](TUTORIAL_INDEX.md) - Complete HW5 learning path

### Methodological Background
- **State Machine Theory**: Formal models of computation with discrete states
- **Markov Chains**: Probabilistic state transition models
- **Failure Mode and Effects Analysis (FMEA)**: Engineering methodology for failure identification

### Course Materials
- [HW5 README](README.md) - Complete assignment instructions
- [HW5 Walkthrough Notebook](hw5_walkthrough.py) - Marimo interactive notebook

### Code References
- [analysis/transition_heatmaps.py](analysis/transition_heatmaps.py) - Reference implementation for matrix construction and visualization
- [data/labeled_traces.json](data/labeled_traces.json) - Example labeled trace dataset

---

**Tutorial Status:** ✅ Complete
**Last Updated:** 2025-10-30
**Maintainer:** AI Evaluation Course Team
