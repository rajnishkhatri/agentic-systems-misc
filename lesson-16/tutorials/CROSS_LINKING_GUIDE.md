# Cross-Linking Guide for Lesson 16 Tutorials

This guide defines the cross-linking structure for all Lesson 16 tutorials to ensure seamless navigation and knowledge discovery.

---

## Cross-Linking Principles

### 1. **Stable Relative Paths**
- ✅ Use relative paths: `../notebooks/08_sequential_orchestration_baseline.ipynb`
- ❌ Avoid absolute paths: `/Users/username/Documents/recipe-chatbot/lesson-16/...`
- **Why:** Relative paths work across different environments and repositories

### 2. **File:Line References for Code**
- Format: `` `backend/reliability/retry.py:42-67` ``
- Include line ranges for context
- Update references after major refactors

### 3. **Bidirectional Navigation**
- Every tutorial links to previous/next tutorial
- Tutorials reference notebooks that demonstrate concepts
- Notebooks reference tutorials that explain theory

### 4. **Learning Path Coherence**
- Link to prerequisites at the top
- Link to advanced topics at the bottom
- Maintain logical progression

---

## Tutorial Linking Structure

### Tutorial Sequence (Sequential Navigation)

```
01_agent_reliability_fundamentals.md
    ↓
02_orchestration_patterns_overview.md
    ↓
03_deterministic_execution_strategies.md
    ↓
04_error_propagation_analysis.md
    ↓
05_agentarch_benchmark_methodology.md
    ↓
06_financial_workflow_reliability.md
    ↓
07_production_deployment_considerations.md
```

**Template for sequential navigation:**

```markdown
**Navigation:**
- **← Previous:** [Tutorial 01: Agent Reliability Fundamentals](01_agent_reliability_fundamentals.md)
- **↑ Index:** [Tutorial Index](../TUTORIAL_INDEX.md)
- **→ Next:** [Tutorial 03: Deterministic Execution Strategies](03_deterministic_execution_strategies.md)
```

---

## Cross-Reference Map

### Tutorial 01: Agent Reliability Fundamentals

**Links TO this tutorial FROM:**
- `README.md` - Lesson overview
- `TUTORIAL_INDEX.md` - Foundation track
- Tutorial 02 - Prerequisites reference
- Notebook 13 - Reliability framework context

**Links FROM this tutorial TO:**
- Tutorial 03 - Deterministic execution (deep dive on FR2.5)
- Tutorial 04 - Error propagation (deep dive on FR2.2)
- Notebook 13 - Hands-on reliability framework
- Diagram: `reliability_failure_modes_taxonomy.mmd`
- Backend: `backend/reliability/*.py` - All 7 components

---

### Tutorial 02: Orchestration Patterns Overview

**Links TO this tutorial FROM:**
- `TUTORIAL_INDEX.md` - Pattern Explorer track
- Tutorial 01 - Next steps
- Notebooks 08-12 - Pattern context
- Tutorial 05 - AgentArch benchmark uses these patterns

**Links FROM this tutorial TO:**
- Tutorial 03-07 - Pattern-specific deep dives
- Notebooks 08-12 - Each pattern notebook
- Diagram: `orchestration_pattern_selection.mmd` - Decision tree
- Backend: `backend/orchestrators/*.py` - 5 patterns

---

### Tutorial 03: Deterministic Execution Strategies

**Links TO this tutorial FROM:**
- Tutorial 01 - Deep dive on FR2.5 non-determinism
- Tutorial 02 - State machine pattern uses this
- Notebook 11 - State machine example
- Notebook 13 - Reliability framework

**Links FROM this tutorial TO:**
- Tutorial 04 - Error isolation complements determinism
- Notebook 13 - Hands-on checkpoint/validation
- Backend: `backend/reliability/checkpoint.py:15-89`
- Backend: `backend/reliability/validation.py:12-134`

---

### Tutorial 04: Error Propagation Analysis

**Links TO this tutorial FROM:**
- Tutorial 01 - Deep dive on FR2.2 error propagation
- Tutorial 02 - Sequential pattern vulnerability
- Notebook 08 - Sequential orchestration example
- Notebook 13 - Error isolation demonstration

**Links FROM this tutorial TO:**
- Tutorial 05 - Error Propagation Index metric
- Notebook 13 - Hands-on error isolation
- Diagram: `error_propagation_cascade.mmd` - Visualization
- Backend: `backend/reliability/isolation.py:18-145`

---

### Tutorial 05: AgentArch Benchmark Methodology

**Links TO this tutorial FROM:**
- Tutorial 02 - Pattern comparison context
- Notebook 14 - Benchmark reproduction
- `TUTORIAL_INDEX.md` - Research validation track

**Links FROM this tutorial TO:**
- Tutorial 02 - Pattern descriptions
- Tutorial 04 - Error Propagation Index metric
- Notebook 14 - Hands-on benchmark
- Diagram: `agentarch_benchmark_results.mmd` - Expected results
- Backend: `backend/benchmarks/*.py` - Full framework
- Paper: [arXiv:2509.10769](https://arxiv.org/abs/2509.10769)

---

### Tutorial 06: Financial Workflow Reliability

**Links TO this tutorial FROM:**
- Tutorial 01 - Real-world application
- Tutorial 07 - Production context
- Notebooks 08-12 - Financial use cases
- `TUTORIAL_INDEX.md` - Domain-specific track

**Links FROM this tutorial TO:**
- Tutorial 07 - Production deployment
- Notebooks 08-12 - Invoice/fraud/reconciliation examples
- Backend: `backend/reliability/audit_log.py:22-178` - Compliance logging
- Data: `data/*.json` - Financial datasets

---

### Tutorial 07: Production Deployment Considerations

**Links TO this tutorial FROM:**
- Tutorial 06 - Financial workflows ready for production
- Notebook 15 - Production tutorial
- `TUTORIAL_INDEX.md` - Production Focus track

**Links FROM this tutorial TO:**
- Notebook 15 - Hands-on production deployment
- Backend: `backend/reliability/circuit_breaker.py:28-156`
- Backend: `backend/reliability/fallback.py:19-124`
- Tutorial 02 - Pattern selection for production constraints

---

## Notebook Cross-Linking

### Notebooks → Tutorials

Each notebook should reference relevant tutorials in the "Prerequisites" section:

```markdown
## Prerequisites

**Required knowledge:**
- [Tutorial 01: Agent Reliability Fundamentals](../tutorials/01_agent_reliability_fundamentals.md)
- [Tutorial 02: Orchestration Patterns Overview](../tutorials/02_orchestration_patterns_overview.md)

**Recommended reading:**
- [Tutorial 03: Deterministic Execution Strategies](../tutorials/03_deterministic_execution_strategies.md)
```

### Tutorials → Notebooks

Tutorials should reference notebooks in "Hands-On Exercises" and "Further Reading":

```markdown
## Hands-On Exercises

### Interactive Practice

**Notebook 13: Reliability Framework Implementation**
- File: [`notebooks/13_reliability_framework_implementation.ipynb`](../notebooks/13_reliability_framework_implementation.ipynb)
- What you'll build: Complete invoice processing workflow with all 7 reliability components
- Execution time: <10 minutes
- Demonstrates: Concepts from Sections 2-4 of this tutorial
```

---

## Diagram Cross-Linking

### Referencing Diagrams in Tutorials

**Inline Mermaid (for simple diagrams <10 nodes):**

```markdown
### Decision Tree

graph TD
    A[Error Detected] --> B{Transient?}
    B -->|Yes| C[Retry with Backoff]
    B -->|No| D[Circuit Breaker]
```

**External Diagram Reference (for complex diagrams):**

```markdown
### Architecture Overview

See the [Reliability Framework Architecture diagram](../diagrams/reliability_framework_architecture.mmd) for a visual representation of all 7 components and their interactions.

![Reliability Framework Architecture](../diagrams/reliability_framework_architecture.png)
```

---

## Backend Code Cross-Linking

### Format for Code References

**Single function:**
```markdown
See the `retry_with_backoff` function in `backend/reliability/retry.py:42-67` for the implementation.
```

**Multiple related functions:**
```markdown
The circuit breaker implementation spans three methods in `backend/reliability/circuit_breaker.py`:
- `call()` method: Lines 78-112 - Main entry point
- `_check_state()`: Lines 115-134 - State transition logic
- `_record_failure()`: Lines 137-156 - Failure tracking
```

**Full module reference:**
```markdown
All 7 reliability components are implemented in `backend/reliability/`:
- `retry.py` - Exponential backoff retry logic
- `circuit_breaker.py` - Circuit breaker pattern
- `checkpoint.py` - Deterministic checkpointing
- `validation.py` - Pydantic schema validation
- `isolation.py` - Error isolation with Result types
- `audit_log.py` - Compliance logging
- `fallback.py` - Fallback strategies
```

---

## Research Paper Cross-Linking

### Citing Papers

**Full citation format:**
```markdown
**AgentArch: Agent-First Architecture for Large-Scale Systems**
- Authors: [Names]
- arXiv: [2509.10769](https://arxiv.org/abs/2509.10769)
- Published: September 2024
- Relevant sections:
  - Section 3.2: Orchestration Pattern Comparison (pp. 7-12)
  - Section 4.1: Error Propagation Metrics (pp. 15-18)
- Key insight: Hierarchical delegation reduces error propagation by 15-25% vs sequential baseline
```

**Quick reference:**
```markdown
The Error Propagation Index metric is defined in [AgentArch (arXiv:2509.10769)](https://arxiv.org/abs/2509.10769), Section 4.1.
```

---

## Dataset Cross-Linking

### Referencing Datasets

**Full dataset reference:**
```markdown
### Financial Datasets

This tutorial uses three synthetic financial datasets:

1. **Invoice Processing** (`data/invoices_100.json`)
   - 100 synthetic invoices
   - Challenges: OCR errors (15%), missing fields (10%), duplicates (8%)
   - Schema: See `backend/data_generation/invoices.py:12-34`

2. **Fraud Detection** (`data/transactions_100.json`)
   - 100 transactions with 10% fraud rate
   - Challenges: Ambiguous patterns (20%), high-value subset (>$10K)
   - Schema: See `backend/data_generation/transactions.py:18-42`

3. **Account Reconciliation** (`data/reconciliation_100.json`)
   - 100 reconciliation tasks
   - Challenges: Date mismatches (25%), rounding errors (20%)
   - Schema: See `backend/data_generation/reconciliation.py:15-38`
```

---

## Quality Checklist for Cross-Links

### Before Committing Tutorial

- [ ] All file paths use relative paths (no absolute paths)
- [ ] All code references include file:line numbers
- [ ] Sequential navigation (prev/next) links are correct
- [ ] Links to notebooks include execution time estimates
- [ ] Links to diagrams specify .mmd source and .png export if available
- [ ] Backend code references point to existing files
- [ ] Research paper links use correct arXiv format
- [ ] Dataset references include schema information
- [ ] All links tested in GitHub markdown preview
- [ ] No broken links (404s)

### Automated Link Checking

```bash
# Check all markdown files for broken internal links
find lesson-16/tutorials/ -name "*.md" -exec grep -o '\[.*\](.*\.md)' {} \; | sort -u
```

---

## Cross-Linking Automation

### Template Variables

When creating a new tutorial, replace these placeholders:

- `[TUTORIAL_NUMBER]` → 01, 02, 03, etc.
- `[TUTORIAL_TITLE]` → Full tutorial title
- `[PREV_TUTORIAL]` → Link to previous tutorial
- `[NEXT_TUTORIAL]` → Link to next tutorial
- `[RELATED_NOTEBOOKS]` → List of notebook links
- `[BACKEND_MODULES]` → List of implementation files

### Script for Validation

Create `lesson-16/scripts/validate_cross_links.py`:

```python
"""Validate all cross-links in tutorials."""
import re
from pathlib import Path

def check_links(tutorial_path: Path) -> list[str]:
    """Check all markdown links in a tutorial."""
    errors = []
    content = tutorial_path.read_text()

    # Find all markdown links
    links = re.findall(r'\[([^\]]+)\]\(([^\)]+)\)', content)

    for link_text, link_path in links:
        if link_path.startswith('http'):
            continue  # Skip external links

        # Resolve relative path
        target = (tutorial_path.parent / link_path).resolve()

        if not target.exists():
            errors.append(f"Broken link: [{link_text}]({link_path})")

    return errors
```

---

## Example: Complete Cross-Linking in Tutorial 01

```markdown
# Tutorial 01: Agent Reliability Fundamentals

**Prerequisites:**
- Lesson 9-11 evaluation fundamentals (optional)
- Basic Python programming
- Understanding of async/await patterns

**Related Resources:**
- **Next Tutorial:** [Tutorial 02: Orchestration Patterns Overview](02_orchestration_patterns_overview.md)
- **Interactive Notebooks:**
  - [Notebook 13: Reliability Framework Implementation](../notebooks/13_reliability_framework_implementation.ipynb) - <10 min
- **Backend Code:**
  - `backend/reliability/retry.py` - Retry with exponential backoff
  - `backend/reliability/circuit_breaker.py` - Circuit breaker pattern
- **Diagrams:**
  - [Failure Modes Taxonomy](../diagrams/reliability_failure_modes_taxonomy.mmd)

---

[Tutorial content...]

---

## Further Reading

### Related Tutorials
- **Tutorial 03:** Deterministic Execution Strategies - Deep dive on non-determinism (FR2.5)
- **Tutorial 04:** Error Propagation Analysis - Deep dive on cascade failures (FR2.2)

### Interactive Practice
- **Notebook 13:** Reliability Framework Implementation
  - Demonstrates all 5 failure modes and mitigations
  - File: `notebooks/13_reliability_framework_implementation.ipynb`

### Backend Code References
- `lesson-16/backend/reliability/` - All 7 reliability components
  - Key functions: `retry_with_backoff()`, `CircuitBreaker.call()`, `ErrorIsolator.safe_call()`
  - Tests: `lesson-16/tests/test_reliability_components.py`

---

**Navigation:**
- **← Previous:** None (this is the first tutorial)
- **↑ Index:** [Tutorial Index](../TUTORIAL_INDEX.md)
- **→ Next:** [Tutorial 02: Orchestration Patterns Overview](02_orchestration_patterns_overview.md)
```

---

**Last Updated:** 2025-11-22
**Version:** 1.0
