# Notebook Authoring Guide - Lesson 16

This guide provides comprehensive instructions for creating high-quality interactive notebooks for Lesson 16: Agent Reliability.

## Quick Start

1. **Copy the template**: Start with `notebooks/NOTEBOOK_TEMPLATE.ipynb`
2. **Fill in metadata**: Update title, learning objectives, prerequisites
3. **Implement steps**: Follow the 12-section structure
4. **Validate**: Run `python scripts/validate_notebook.py notebooks/your_notebook.ipynb`
5. **Test execution**: Run with `--execute` flag to verify timing

## Standard 12-Section Structure

Every notebook MUST follow this structure for consistency:

### Section 1: Title + Metadata
```markdown
# [Notebook Title]

**Execution Time:** <5 minutes (DEMO mode) | <10 minutes (FULL mode)
**Cost:** $0 (DEMO mode with mocks) | $X.XX-X.XX (FULL mode with real LLM)

## Learning Objectives

By the end of this tutorial, you will:

1. [Objective 1 - use action verbs: understand, implement, demonstrate, evaluate]
2. [Objective 2]
3. [Objective 3]
4. [Objective 4]
5. [Objective 5]

## Prerequisites

- Completed [Tutorial Name](../tutorials/XX_tutorial_name.md)
- Understanding of [Concept]
- Basic Python and [Library] knowledge
```

**Guidelines:**
- Use clear, specific learning objectives with action verbs
- List 3-5 prerequisites (tutorials, concepts, skills)
- Provide accurate time/cost estimates for both modes
- Title should match notebook purpose (e.g., "08_sequential_orchestration_baseline.ipynb")

### Section 2: Setup and Configuration
```python
# Mode configuration
DEMO_MODE = True  # Set to False for full execution with real LLM
NUM_SAMPLES = 5 if DEMO_MODE else 100

print(f"Running in {'DEMO' if DEMO_MODE else 'FULL'} mode")
print(f"Processing {NUM_SAMPLES} samples")
```

```python
# Import libraries
import os
import sys
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import List, Dict, Any
from dotenv import load_dotenv

# Add backend to path
sys.path.insert(0, str(Path.cwd().parent))

# Import from lesson-16 backend
from lesson_16.backend.orchestrators import SequentialOrchestrator
from lesson_16.backend.reliability import RetryLogic, CircuitBreaker

# Load environment variables (if needed for FULL mode)
if not DEMO_MODE:
    load_dotenv()
    assert os.getenv("OPENAI_API_KEY"), "OPENAI_API_KEY not found for FULL mode"
    print("✅ API key verified")
else:
    print("✅ DEMO mode - using mock agents")

print("✅ Setup complete")
```

**Guidelines:**
- ALWAYS provide DEMO_MODE toggle for $0 learning
- Import lesson-16 backend modules to demonstrate integration
- Only require API keys in FULL mode
- Use defensive coding (assertions, error messages)

### Sections 3-6: Steps 1-4
```markdown
## Step N: [Step Title]

[Brief explanation of what this step accomplishes and why it's important]
```

```python
# Step N implementation
# [Code with comments explaining key parts]

# Validation assertion
assert condition, "Descriptive error message"
print("✅ Step N complete")
```

**Guidelines:**
- Each step should be self-contained and build on previous steps
- Use clear markdown headers (## Step 1, ## Step 2, etc.)
- Include inline comments explaining complex logic
- Add validation assertions to catch errors early
- Print success messages for user feedback
- Aim for 4-6 major steps total

### Section 7: Visualization
```markdown
## Visualization: [Chart Title]

[Explanation of what the visualization shows and key insights to look for]
```

```python
# Create visualization
fig, ax = plt.subplots(figsize=(10, 6))

# [Plotting code]

ax.set_xlabel('[X-axis label]', fontsize=12)
ax.set_ylabel('[Y-axis label]', fontsize=12)
ax.set_title('[Chart Title]', fontsize=14, fontweight='bold')
ax.grid(axis='y', alpha=0.3)
ax.legend()

plt.tight_layout()
plt.show()

print("📊 Visualization complete")
```

**Guidelines:**
- Use matplotlib/seaborn for consistency
- Set figure size for readability (10-12 inches wide)
- Label axes clearly with units
- Add grid for easier reading
- Use color-blind friendly palettes
- Include legend when showing multiple series
- Verify renders in GitHub notebook viewer, JupyterLab, and VS Code

### Section 8: Validation
```markdown
## Validation: Check Results

[Explanation of validation checks and success criteria]
```

```python
print("\n" + "="*80)
print("VALIDATION RESULTS")
print("="*80 + "\n")

# Check 1
check_1 = condition  # Boolean check
print(f"{'✅' if check_1 else '❌'} Check 1: [Description]")

# Check 2
check_2 = condition
print(f"{'✅' if check_2 else '❌'} Check 2: [Description]")

# Overall validation
all_checks_passed = check_1 and check_2
assert all_checks_passed, "Some validation checks failed"
print("\n🎉 All validation checks passed!")
```

**Guidelines:**
- Validate all key results (success rates, metrics, expectations)
- Use ✅/❌ emojis for visual feedback
- Provide descriptive messages for each check
- Use assertions to fail fast on errors
- Compare against expected values from PRD (e.g., ≥95% success rate)

### Section 9: Cost Summary
```python
print("\n" + "="*80)
print("COST SUMMARY")
print("="*80 + "\n")

if DEMO_MODE:
    print("Mode: DEMO (mocked agents)")
    print("Total cost: $0.00")
    print("LLM API calls: 0")
else:
    # Track costs from orchestrator/agents
    total_cost = cost_tracker.get_total_cost()
    total_calls = cost_tracker.get_total_calls()

    print(f"Mode: FULL (real LLM)")
    print(f"Total cost: ${total_cost:.2f}")
    print(f"LLM API calls: {total_calls}")
    print(f"Average cost per sample: ${total_cost / NUM_SAMPLES:.4f}")

print("\n💡 Tip: Use DEMO_MODE=True for free learning, then switch to FULL mode for experiments")
```

**Guidelines:**
- Always show cost summary, even if $0 in DEMO mode
- Integrate with backend CostTracker if available
- Show breakdown (total, per-sample, per-agent)
- Remind users about DEMO mode option

### Section 10: Summary and Key Takeaways
```markdown
## Summary and Key Takeaways

✅ **What we learned:**

1. **[Takeaway 1]** - [Brief explanation with evidence from results]
2. **[Takeaway 2]** - [Brief explanation with evidence from results]
3. **[Takeaway 3]** - [Brief explanation with evidence from results]

### Key Insights

- **[Insight 1]**: [Specific finding from notebook execution]
- **[Insight 2]**: [Specific finding from notebook execution]

### Production Recommendations

1. **[Recommendation 1]** - [Rationale based on results]
2. **[Recommendation 2]** - [Rationale based on results]

### Common Pitfalls

⚠️ **Pitfall 1**: [What to avoid and why]
⚠️ **Pitfall 2**: [What to avoid and why]
```

**Guidelines:**
- Tie takeaways to learning objectives from Section 1
- Use evidence from notebook execution (metrics, charts)
- Provide actionable production recommendations
- Warn about common mistakes observed in results
- Keep concise (3-5 key takeaways, 2-3 insights, 3-5 recommendations)

### Section 11: Next Steps
```markdown
## Next Steps

### Related Tutorials

**Prerequisites** (complete these first):
- [Tutorial Name](../tutorials/XX_tutorial_name.md) - [Brief description]

**Next in sequence**:
- [Next Notebook](XX_next_notebook.ipynb) - [Brief description]

**Advanced topics**:
- [Advanced Tutorial](../tutorials/YY_advanced_topic.md) - [Brief description]

### Learning Paths

**Path 1: Pattern Explorer** (Quick Start)
1. Tutorial 02 → Notebook 08 → Notebook 09 → Notebook 10

**Path 2: Reliability Engineer** (Production Focus)
1. Tutorial 01 → Tutorial 03 → Notebook 13 → Notebook 15

### Further Exploration

- **Experiment**: Try [specific experiment suggestion]
- **Compare**: Benchmark against [alternative approach]
- **Extend**: Add [suggested feature/modification]

👉 **Next**: [Next Notebook Title](XX_next_notebook.ipynb)
```

**Guidelines:**
- Cross-link to related tutorials and notebooks
- Show learning paths for different goals
- Suggest experiments to deepen understanding
- Use relative paths (../tutorials/, ../notebooks/)
- Verify all links exist using validation script

### Section 12: Notebook Metadata
```json
{
  "metadata": {
    "kernelspec": {
      "display_name": "Python 3",
      "language": "python",
      "name": "python3"
    },
    "language_info": {
      "codemirror_mode": {"name": "ipython", "version": 3},
      "file_extension": ".py",
      "mimetype": "text/x-python",
      "name": "python",
      "nbconvert_exporter": "python",
      "pygments_lexer": "ipython3",
      "version": "3.11.0"
    }
  },
  "nbformat": 4,
  "nbformat_minor": 4
}
```

**Guidelines:**
- Use Python 3.11+ for type hint compatibility
- Standard kernelspec for consistency
- nbformat 4 for modern Jupyter features

## Quality Standards

### Execution Time Targets
- **Notebooks 08-12, 15**: <5 minutes
- **Notebooks 13-14**: <10 minutes (benchmark/comprehensive)
- Use `time jupyter nbconvert --execute` to measure
- Optimize slow cells (caching, sampling, mocking)

### Code Quality
- **Type hints**: Use for all function signatures
- **Defensive coding**: Input validation, error handling
- **Comments**: Explain WHY, not WHAT (code should be self-documenting)
- **Assertions**: Validate assumptions and results
- **Ruff compliance**: Run `nbqa ruff check notebooks/` before committing

### Documentation Quality
- **Reading level**: Accessible to intermediate Python developers
- **Completeness**: All steps explained, no gaps in logic
- **Accuracy**: Code matches explanations, results match descriptions
- **Cross-linking**: All references to tutorials/code verified

### Visual Quality
- **Charts**: Clear labels, legends, titles
- **Rendering**: Test in GitHub, JupyterLab, VS Code
- **Accessibility**: Color-blind friendly palettes
- **Export**: Save PNG for complex diagrams

## Validation Workflow

1. **During development**:
   ```bash
   python scripts/validate_notebook.py notebooks/your_notebook.ipynb
   ```

2. **Before committing**:
   ```bash
   # Validate structure and links
   python scripts/validate_notebook.py notebooks/your_notebook.ipynb

   # Execute and time
   time jupyter nbconvert --execute --to notebook \
     --ExecutePreprocessor.timeout=600 \
     --output=/tmp/executed.ipynb \
     notebooks/your_notebook.ipynb

   # Check code quality
   nbqa ruff check notebooks/your_notebook.ipynb
   ```

3. **Integration with tests**:
   ```bash
   pytest lesson-16/tests/test_notebook_validation.py -v
   ```

## Common Patterns

### Mock Agents for DEMO Mode
```python
class MockAgent:
    """Mock agent that returns deterministic results for DEMO mode."""

    def __init__(self, name: str, success_rate: float = 1.0):
        self.name = name
        self.success_rate = success_rate

    async def execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Simulate agent execution with mock data."""
        import random
        if random.random() < self.success_rate:
            return {"status": "success", "output": f"Mock result from {self.name}"}
        else:
            raise ValueError(f"Mock failure from {self.name}")

# Usage
if DEMO_MODE:
    agent = MockAgent("extraction_agent", success_rate=0.95)
else:
    from lesson_16.backend.agents import RealAgent
    agent = RealAgent("extraction_agent", model="gpt-4o")
```

### Progress Tracking
```python
from tqdm import tqdm

results = []
for sample in tqdm(samples, desc="Processing samples"):
    result = process(sample)
    results.append(result)
```

### Error Handling
```python
from typing import Optional

def safe_process(data: dict[str, Any]) -> Optional[dict[str, Any]]:
    """Process data with error handling."""
    try:
        result = process(data)
        return result
    except ValueError as e:
        print(f"⚠️  Validation error: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None

# Use with list comprehension
results = [r for r in (safe_process(d) for d in data) if r is not None]
```

### Cost Tracking Integration
```python
from lesson_16.backend.reliability import CostTracker

cost_tracker = CostTracker()

# Track costs during execution
with cost_tracker.track("workflow_1"):
    result = orchestrator.execute(task)

# Report costs
print(f"Total cost: ${cost_tracker.get_total_cost():.2f}")
print(f"Breakdown: {cost_tracker.get_breakdown()}")
```

## Troubleshooting

### Issue: Notebook execution times out
**Solution**:
- Reduce sample size (NUM_SAMPLES)
- Use cached results for expensive operations
- Mock LLM calls in DEMO mode
- Increase timeout: `--ExecutePreprocessor.timeout=1200`

### Issue: Imports fail in notebook
**Solution**:
- Check `sys.path.insert(0, str(Path.cwd().parent))` is present
- Verify backend modules exist: `ls lesson-16/backend/`
- Test imports in Python REPL from notebook directory

### Issue: Cross-links broken
**Solution**:
- Use relative paths: `../tutorials/` not `/absolute/path/`
- Run validation script to find broken links
- Verify target files exist in repository

### Issue: Charts don't render in GitHub
**Solution**:
- Use `plt.show()` not `plt.savefig()` for inline display
- Test rendering: View notebook on GitHub web interface
- Export to PNG if Mermaid diagrams needed

## Examples

### Good: Clear, Focused Step
```python
# Step 2: Calculate Success Rate
# --------------------------------

# Count successful vs failed tasks
successes = sum(1 for r in results if r["status"] == "success")
total = len(results)
success_rate = successes / total if total > 0 else 0.0

print(f"\nSuccess Rate Analysis:")
print(f"  Successes: {successes}/{total}")
print(f"  Rate: {success_rate:.1%}")

# Validate against target
TARGET_SUCCESS_RATE = 0.95
assert success_rate >= TARGET_SUCCESS_RATE, \
    f"Success rate {success_rate:.1%} below target {TARGET_SUCCESS_RATE:.1%}"

print(f"✅ Step 2 complete - Success rate: {success_rate:.1%}")
```

### Bad: Unclear, Monolithic Step
```python
# Do everything
data = load_data()
for d in data:
    r = process(d)  # What does this do?
    results.append(r)
# Did it work? Who knows!
```

## Checklist

Before submitting a notebook, verify:

- [ ] Uses NOTEBOOK_TEMPLATE.ipynb as starting point
- [ ] All 12 sections present and complete
- [ ] Title, learning objectives, prerequisites accurate
- [ ] DEMO_MODE toggle implemented
- [ ] All imports work (test with fresh kernel)
- [ ] All steps have markdown headers and validation assertions
- [ ] Visualization renders correctly
- [ ] Cost summary shows both DEMO and FULL estimates
- [ ] Summary ties back to learning objectives
- [ ] Next steps includes 3+ cross-links
- [ ] Execution time <5-10 min (measured)
- [ ] Validation script passes
- [ ] Code quality checks pass (Ruff, mypy)
- [ ] All cross-links verified
- [ ] Tested in GitHub notebook viewer

## Getting Help

- **Structure questions**: Review `NOTEBOOK_TEMPLATE.ipynb`
- **Validation issues**: Run `python scripts/validate_notebook.py --help`
- **Backend integration**: See `lesson-16/backend/README.md`
- **Tutorial cross-linking**: See `TUTORIAL_INDEX.md`

---

**Last Updated**: Task 5.1 - Notebook Infrastructure & Template Setup
**Maintainer**: Lesson 16 Development Team
