# LLM Evaluation Procedural Memory Map

**Purpose**: AI-assistant-friendly decision support system for selecting and implementing LLM evaluation techniques based on use case, resources, and requirements.

**Audience**: AI coding assistants helping developers implement evaluation workflows for LLM-based systems.

---

## Quick Start for AI Assistants

### Common Queries

**"I need to evaluate [system prompts / retrieval / agents / response quality]"**
→ See [decision-trees.md](decision-trees.md) for problem-type-specific recommendations

**"What evaluation technique should I use?"**
→ See [QUICK_REFERENCE.md](QUICK_REFERENCE.md) for one-page decision matrix

**"How do I implement [specific technique]?"**
→ See [techniques-catalog.md](techniques-catalog.md) for detailed implementation guidance

**"What libraries do I need?"**
→ See [tools-index.yaml](tools-index.yaml) for library → technique mappings

**"What are common evaluation patterns?"**
→ See [patterns.md](patterns.md) for cross-cutting implementation patterns

---

## Navigation Guide

### Entry Points by Need

#### 🎯 **I have a specific problem to solve**
Start here: [decision-trees.md](decision-trees.md)
- Organized by problem type (prompts, retrieval, agents, quality)
- Filtered by constraints (budget, time, data availability)
- Tailored by accuracy requirements (exploratory, production, safety-critical)

#### 📚 **I want to understand all available techniques**
Start here: [techniques-catalog.md](techniques-catalog.md)
- 25+ techniques with detailed descriptions
- When to use / when NOT to use
- Prerequisites, costs, time estimates
- Step-by-step implementation guidance

#### ⚡ **I need a quick recommendation**
Start here: [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
- One-page decision matrix
- Problem → Technique → Tutorial mapping
- Difficulty and cost at a glance

#### 🔧 **I'm implementing and need technical details**
Use these resources:
- [patterns.md](patterns.md) - Reusable implementation patterns
- [tools-index.yaml](tools-index.yaml) - Library documentation and usage
- [techniques-catalog.yaml](techniques-catalog.yaml) - Machine-readable technique specs

#### 🧭 **I want to understand methodology families**
Browse by family:
- [families/qualitative-methods.md](families/qualitative-methods.md) - Open coding, taxonomies
- [families/quantitative-metrics.md](families/quantitative-metrics.md) - Recall@k, TPR/TNR, MRR
- [families/automated-evaluation.md](families/automated-evaluation.md) - LLM-as-Judge, substantiation
- [families/optimization-techniques.md](families/optimization-techniques.md) - Cascades, cost optimization
- [families/debugging-methods.md](families/debugging-methods.md) - Transition matrices, trace inspection

---

## File Structure

```
procedural-memory-map/
├── README.md                              # This file - navigation hub
├── QUICK_REFERENCE.md                     # One-page decision matrix
├── decision-trees.md                      # Use case → technique mapping
├── techniques-catalog.yaml                # Machine-readable technique index
├── techniques-catalog.md                  # Human-readable technique guide
├── patterns.md                            # Cross-cutting patterns
├── tools-index.yaml                       # Library → technique mapping
├── families/
│   ├── qualitative-methods.md
│   ├── quantitative-metrics.md
│   ├── automated-evaluation.md
│   ├── optimization-techniques.md
│   └── debugging-methods.md
└── diagrams/
    ├── technique-relationship-graph.mmd   # Technique dependencies
    ├── decision-tree-by-problem.mmd       # Problem type flowchart
    └── evaluation-workflow-overview.mmd   # Complete evaluation lifecycle
```

---

## How AI Assistants Should Use This System

### Pattern 1: Problem-Driven Query
```
User: "I need to evaluate my RAG retrieval system"

Assistant reasoning:
1. Consult decision-trees.md → RAG section
2. Identifies: Recall@k, MRR (HW4)
3. Checks prerequisites in techniques-catalog.yaml
4. Verifies user has: processed documents, synthetic queries
5. Recommends: "Use BM25 + Recall@k evaluation from HW4"
6. Provides: Link to homeworks/hw4/TUTORIAL_INDEX.md
```

### Pattern 2: Resource-Constrained Query
```
User: "I have $2 budget and 1 hour. Need to evaluate 100 examples"

Assistant reasoning:
1. Consult decision-trees.md → Resource Constraints section
2. Budget: <$5 → use gpt-4o-mini, avoid GPT-4o bulk labeling
3. Time: <2 hours → prioritize parallel processing, sampling
4. Recommends: "Manual labeling (free) OR gpt-4o-mini judge ($0.50)"
5. Provides: Cost breakdown from techniques-catalog.yaml
```

### Pattern 3: Technique Detail Query
```
User: "How does LLM-as-Judge work?"

Assistant reasoning:
1. Lookup in techniques-catalog.md → llm_as_judge entry
2. Extracts: when_to_use, prerequisites, key_steps, outputs
3. Cross-references: families/automated-evaluation.md for context
4. Links to: homeworks/hw3/TUTORIAL_INDEX.md for implementation
5. Warns: Anti-patterns from "when_not_to_use" section
```

### Pattern 4: Implementation Pattern Query
```
User: "I need to process 200 items with LLM API calls"

Assistant reasoning:
1. Recognizes: Bulk LLM processing pattern
2. Consults patterns.md → Parallel LLM Processing
3. Extracts: ThreadPoolExecutor code snippet
4. Provides: Rate limiting guidance, cost warning
5. References: Similar implementations in HW2, HW4, Lesson 4
```

---

## Content Sources

All techniques, workflows, and recommendations are extracted from:
- **HW1**: Prompt engineering, query diversity
- **HW2**: Error analysis, open/axial coding, synthetic query generation
- **HW3**: LLM-as-Judge, bias correction, TPR/TNR
- **HW4**: RAG evaluation, Recall@k, MRR, query rewrite agents
- **HW5**: Transition matrix analysis, state-based modeling
- **Lesson 4**: Substantiation evaluation, parallel labeling, tool grounding
- **Lesson 7**: Trace inspection, manual annotation workflows
- **Lesson 8**: Model cascades, confidence thresholding, cost optimization

See individual TUTORIAL_INDEX.md files in `homeworks/` and lesson directories for detailed implementations.

---

## Design Principles

### For AI Assistant Consumption

1. **Machine-Readable + Human-Readable**: YAML for parsing, Markdown for context
2. **Reasoning Emphasis**: Every recommendation includes WHY, not just WHAT
3. **Anti-Patterns Included**: Explicit "when NOT to use" guidance
4. **Cost-Aware**: All techniques include cost estimates
5. **Prerequisite Chains**: Clear dependency mapping
6. **Use-Case Driven**: Start with problem, suggest solution path

### For Developer Experience

1. **Junior-Dev Friendly**: Assumes minimal evaluation knowledge
2. **Implementation-Ready**: Links to working code and tutorials
3. **Decision Support**: Helps choose between alternatives
4. **Real Constraints**: Accounts for budget, time, data availability
5. **Production-Focused**: Includes scaling and optimization guidance

---

## Maintenance

When tutorials are updated:
1. Update corresponding entries in `techniques-catalog.yaml`
2. Verify decision trees in `decision-trees.md` remain accurate
3. Check cross-references in family guides
4. Update cost estimates if pricing changes
5. Add new techniques to appropriate family files

---

## Example Usage Scenarios

### Scenario 1: New Project - System Prompt Evaluation
**User**: "I'm building a recipe chatbot. How do I evaluate my system prompt?"

**Path**:
1. decision-trees.md → "Prompts & System Instructions"
2. Recommends: Prompt Engineering (HW1) → Query Diversity Testing
3. techniques-catalog.md shows prerequisites: None (beginner-friendly)
4. QUICK_REFERENCE.md shows: Difficulty=Beginner, Cost=Free
5. Links to: homeworks/hw1/TUTORIAL_INDEX.md

### Scenario 2: Production Monitoring - Response Quality
**User**: "I need automated evaluation for 1000+ daily conversations"

**Path**:
1. decision-trees.md → "Response Quality" + "Accuracy Requirements → Production"
2. Recommends: LLM-as-Judge (HW3) with Bias Correction
3. techniques-catalog.yaml shows: cost=$1-2 per 150, TPR/TNR required
4. patterns.md provides: Parallel processing pattern for scale
5. families/automated-evaluation.md explains: When automation is appropriate

### Scenario 3: Debugging - Agent Failures
**User**: "My agent pipeline is failing. How do I find the bottleneck?"

**Path**:
1. decision-trees.md → "Agent Pipelines" → "Identify bottlenecks"
2. Recommends: Transition Matrix Analysis (HW5)
3. techniques-catalog.md shows: Prerequisite = labeled failure traces
4. families/debugging-methods.md provides: Workflow from symptom to root cause
5. Links to: homeworks/hw5/TUTORIAL_INDEX.md

---

## Quick Command Reference

### For AI Assistants (Pseudocode)

```python
# Query: "What technique for [problem]?"
def recommend_technique(problem_description, constraints=None):
    # 1. Parse problem type from decision-trees.md
    problem_type = classify_problem(problem_description)

    # 2. Get candidate techniques
    candidates = decision_trees[problem_type]

    # 3. Filter by constraints
    if constraints:
        candidates = filter_by_constraints(candidates, constraints)

    # 4. Lookup details
    for technique in candidates:
        details = techniques_catalog[technique]

        # 5. Return recommendation with reasoning
        return {
            "technique": technique,
            "reasoning": details["when_to_use"],
            "prerequisites": details["prerequisites"],
            "cost": details["cost_estimate"],
            "tutorial": details["source_tutorial"]
        }
```

---

## Getting Started

**For AI Assistants**: Start with [decision-trees.md](decision-trees.md) to understand the decision framework, then consult specific files based on user queries.

**For Developers**: Start with [QUICK_REFERENCE.md](QUICK_REFERENCE.md) for an overview, then dive into [techniques-catalog.md](techniques-catalog.md) for detailed guidance.

**For Researchers**: Review [families/](families/) directory to understand methodology organization and relationships between techniques.

---

## Version
- **Created**: 2025-11-08
- **Content Sources**: HW1-5, Lessons 4,7,8 (as of 2025-10-29)
- **Total Techniques**: 25+
- **Total Libraries**: 10+

---

**Ready to assist with LLM evaluation decisions!** 🚀
