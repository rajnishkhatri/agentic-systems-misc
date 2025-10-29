# Homework 5: Tutorial Index

## Overview

Homework 5 focuses on **agent failure analysis** using state transition matrices. Given pre-labeled conversation traces where every conversation contains exactly one failure, you'll build transition matrices to visualize where agents succeed last and where they fail first, then interpret patterns to identify system bottlenecks.

**Learning Time:** ~3-4 hours
**Difficulty:** Intermediate
**Prerequisites:** Basic understanding of state machines, data visualization (HW2-4 concepts helpful)

---

## Learning Objectives

By completing these tutorials, you will be able to:
- ✅ Understand state-based modeling for conversational agents
- ✅ Build failure transition matrices from labeled traces
- ✅ Visualize transition patterns using seaborn heatmaps
- ✅ Interpret matrix patterns to identify system bottlenecks
- ✅ Distinguish tool execution failures from LLM argument generation failures
- ✅ Propose targeted improvements based on failure analysis
- ✅ Apply transition analysis to multi-agent or multi-step systems

---

## Tutorials

### 1. Transition Analysis Concepts
**File:** `transition_analysis_concepts.md`
**Reading Time:** 15-20 minutes
**Topics:**
- State-based modeling for agent pipelines
- What is a failure transition?
- Last successful state vs. first failing state
- Interpreting transition frequencies
- Common failure patterns (sequential, clustered, distributed)
- Bottleneck identification strategies
- When state-based analysis is appropriate

**When to use:** Start here to understand the theory before building matrices.

---

### 2. Heatmap Visualization Tutorial (Interactive)
**File:** `heatmap_visualization_tutorial.ipynb`
**Execution Time:** 15-20 minutes
**Topics:**
- Loading labeled trace data
- Building transition count matrices
- Seaborn heatmap configuration
- Choosing effective color schemes
- Interpreting rows (last success) and columns (first failure)
- Identifying high-frequency transitions
- Exporting publication-quality heatmaps

**When to use:** After understanding concepts, use this to build and visualize your matrix.

**Interactive Features:**
- Data loading and validation
- Matrix construction step-by-step
- Live heatmap rendering
- Annotation and styling options
- Export to PNG

---

### 3. Transition Matrix Concept Diagram (Visual)
**File:** `diagrams/transition_matrix_concept.mmd`
**Format:** Mermaid diagram (viewable on GitHub)
**Topics:**
- Visual representation of agent pipeline states
- Success paths vs. failure paths
- Edge weights showing transition frequencies
- Example transitions with interpretation

**When to use:** Reference this to understand how states connect and where failures occur.

---

## Recommended Learning Path

```
┌────────────────────────────────────────────────────────┐
│        HW5 Transition Analysis Workflow                │
├────────────────────────────────────────────────────────┤
│                                                        │
│  1. Read README.md                                     │
│     → Understand assignment scope and data format     │
│     ↓                                                  │
│  2. Inspect data/labeled_traces.json                   │
│     → Review trace structure and state fields         │
│     ↓                                                  │
│  3. Complete "Transition Analysis Concepts" tutorial   │
│     → Learn state-based failure modeling              │
│     ↓                                                  │
│  4. Review 10-state taxonomy                           │
│     → ParseRequest → PlanToolCalls → ... → Deliver    │
│     ↓                                                  │
│  5. Complete "Heatmap Visualization" tutorial          │
│     → Build matrix, create heatmap, interpret         │
│     ↓                                                  │
│  6. Run analysis/transition_heatmaps.py                │
│     → Generates results/failure_transition_heatmap.png│
│     ↓                                                  │
│  7. Analyze heatmap                                    │
│     → Which states fail most often?                   │
│     → Are failures clustered?                         │
│     → Any surprising transitions?                     │
│     ↓                                                  │
│  8. Write analysis summary                             │
│     → Document findings in README or markdown         │
│     ↓                                                  │
│  9. [Optional] Explore generation/ scripts             │
│     → See how synthetic data was created              │
└────────────────────────────────────────────────────────┘
```

---

## Key Concepts

### Agent Pipeline States
The recipe bot agent has a **10-state pipeline**:

| State | Description | Type |
|-------|-------------|------|
| `ParseRequest` | LLM interprets user message | LLM |
| `PlanToolCalls` | LLM decides which tools to invoke | LLM |
| `GenCustomerArgs` | LLM constructs customer DB arguments | LLM |
| `GetCustomerProfile` | Executes customer profile tool | Tool |
| `GenRecipeArgs` | LLM constructs recipe DB arguments | LLM |
| `GetRecipes` | Executes recipe search tool | Tool |
| `GenWebArgs` | LLM constructs web search arguments | LLM |
| `GetWebInfo` | Executes web search tool | Tool |
| `ComposeResponse` | LLM drafts final answer | LLM |
| `DeliverResponse` | Agent sends answer to user | System |

**Every trace** proceeds successfully through some states, then fails at exactly one state.

### Failure Transition
A **failure transition** is the directed edge from:
- **Last Successful State:** The final state that completed without error
- **First Failing State:** The immediate next state that encountered an error

**Example:**
```
Trace A:
  ParseRequest ✓ → PlanToolCalls ✓ → GenRecipeArgs ✓ → GetRecipes ✗

Last Success: GenRecipeArgs
First Failure: GetRecipes
Transition: (GenRecipeArgs → GetRecipes)
```

### Transition Matrix
A **transition matrix** counts how many times each (last success → first failure) pair occurs:

```
               First Failure →
            Parse  Plan  GenRec  GetRec  Compose
Last     ┌─────────────────────────────────────┐
Success  │                                     │
  ↓      │                                     │
Parse    │   0      3      0       0       0   │
Plan     │   0      0      5       0       2   │
GenRec   │   0      0      0      12       0   │
GetRec   │   0      0      0       0       8   │
Compose  │   0      0      0       0       0   │
         └─────────────────────────────────────┘
```

**Interpretation:**
- **High value (GenRec → GetRec: 12):** Recipe search tool fails frequently
- **Row cluster:** Failures concentrated after a specific state
- **Column cluster:** Specific state fails across many predecessors

---

## Practical Exercises

After completing the tutorials, try these exercises:

1. **Manual Trace Analysis**
   - Read 5 random traces from labeled_traces.json
   - Manually extract (last_success, first_failure) for each
   - Plot these 5 transitions on paper
   - Hypothesize why each failure occurred

2. **Pattern Identification**
   - Look at your heatmap's highest-frequency cell
   - Read all traces with that transition
   - Identify common themes (similar user queries, tool issues, etc.)
   - Write a 2-3 sentence explanation

3. **Bottleneck Hypothesis**
   - Identify which state(s) fail most often (sum of column)
   - Propose 2-3 reasons why (LLM error, tool API issue, data quality)
   - Suggest specific improvements for each

---

## Common Pitfalls

### Data Interpretation
- ❌ **Confusing rows and columns:** Row = where it came from, Column = where it failed
- ❌ **Ignoring state types:** LLM failures vs. tool failures have different solutions
- ❌ **Missing the forest:** Focusing on one cell without seeing overall patterns
- ❌ **No hypothesis:** Describing "what" without explaining "why"

### Visualization
- ❌ **Poor color scheme:** Rainbow colors obscure patterns
- ❌ **No annotations:** Not labeling axes or values
- ❌ **Wrong normalization:** Percentages can hide raw counts
- ❌ **Cluttered display:** 10×10 matrix with tiny font is unreadable

### Analysis
- ❌ **Surface-level:** "GetRecipes fails a lot" without investigating why
- ❌ **No action items:** Identifying problems without proposing solutions
- ❌ **Ignoring frequency:** Focusing on rare transitions instead of common ones
- ❌ **Confirmation bias:** Only looking for expected patterns

---

## Reference Files

### Assignment Materials
- [`README.md`](README.md) - Assignment instructions
- [`hw5_walkthrough.py`](hw5_walkthrough.py) - Marimo notebook walkthrough
- [`data/labeled_traces.json`](data/labeled_traces.json) - 100 pre-labeled traces
- [`data/raw_traces.json`](data/raw_traces.json) - Original unlabeled traces (reference)

### Scripts
- [`analysis/transition_heatmaps.py`](analysis/transition_heatmaps.py) - Heatmap generation script

### Expected Outputs
- [`results/failure_transition_heatmap.png`](results/failure_transition_heatmap.png) - Your final visualization

### Optional: Synthetic Data Generation (Not Graded)
- [`generation/`](generation/) - Scripts used to create labeled_traces.json

### Video Walkthroughs
- [HW5 Solution Walkthrough](https://youtu.be/z1oISsDUKLA)

---

## Tools & Libraries

**Required:**
- `pandas` - Data manipulation
- `seaborn` - Heatmap visualization
- `matplotlib` - Plot configuration
- `json` - Loading trace data

**Installation:**
```bash
pip install pandas seaborn matplotlib
```

---

## Expected Outputs

After completing HW5, you should have:
- ✅ Transition matrix built from labeled traces
- ✅ Heatmap visualization (results/failure_transition_heatmap.png)
- ✅ Analysis summary documenting:
  - Which states fail most often
  - Whether failures cluster around tool execution or argument generation
  - Any surprising low-frequency transitions
  - Proposed improvements based on bottleneck analysis

**Example Analysis:**
```
Findings:
- GetRecipes fails most frequently (35% of all failures)
- Failures cluster after GenRecipeArgs → GetRecipes (22 occurrences)
- Likely cause: Recipe search tool returns empty results
- Proposed fix: Improve query fallback handling

Surprising observation:
- Very few failures in ComposeResponse (only 3%)
- Suggests LLM is good at drafting responses when retrieval succeeds
- Focus improvement efforts on retrieval, not generation
```

---

## Connection to Systems Engineering

This assignment applies techniques from:
- **Markov Chains:** State transition probability analysis
- **Failure Mode and Effects Analysis (FMEA):** Systematic failure identification
- **System Reliability Engineering:** Bottleneck analysis for complex systems

**Real-World Applications:**
- Debugging multi-stage ML pipelines
- Optimizing microservice architectures
- Analyzing customer journey drop-off points
- Evaluating autonomous agent systems

---

## Next Steps

After completing HW5, you'll have:
- ✅ State-based failure analysis skills
- ✅ Visualization techniques for agent debugging
- ✅ Bottleneck identification strategies

**Explore advanced lessons** to learn specialized evaluation techniques:

👉 [Lesson 4: Substantiation Evaluation](../../lesson-4/TUTORIAL_INDEX.md)
👉 [Lesson 7: Trace Inspection Tools](../../lesson-7/TUTORIAL_INDEX.md)
👉 [Lesson 8: Model Cascades](../../lesson-8/TUTORIAL_INDEX.md)

---

## FAQ

**Q: Why are all traces guaranteed to have exactly one failure?**
A: This is synthetic data designed for learning. Real-world traces may have 0, 1, or multiple failures.

**Q: Can I apply this to multi-agent systems?**
A: Yes! Add states for each agent. Transitions show handoffs and failures.

**Q: What if my heatmap shows no clear pattern?**
A: Distributed failures might indicate data quality issues or overly broad state definitions.

**Q: Should I normalize the matrix (percentages)?**
A: For interpretation, show raw counts. For comparison across datasets, use percentages.

**Q: How do I decide if a bottleneck is worth fixing?**
A: Consider: (1) Frequency of failure, (2) Impact on user experience, (3) Difficulty of fix.

**Q: Can I modify the provided transition_heatmaps.py script?**
A: Yes! The script is a starting point. Customize styling, annotations, etc.

---

**Tutorial Status:** ⏳ In Development
**Last Updated:** 2025-10-29
**Maintainer:** AI Evaluation Course Team
