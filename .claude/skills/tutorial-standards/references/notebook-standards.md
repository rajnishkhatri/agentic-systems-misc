# Jupyter Notebook Quality Standards

**Version:** 1.0
**Last Updated:** 2025-11-18

---

## Overview

This document defines the quality standards for all Jupyter notebooks in the tutorial system. These standards ensure notebooks are:
- **Executable** in <5 minutes (or provide DEMO mode option)
- **Cost-conscious** with clear API cost warnings
- **Defensive** with input validation and assertions
- **Student-friendly** with clear learning objectives and progress indicators

---

## Required Standards

### 1. Execution Time Requirement

**Standard:** All notebooks must execute in **<5 minutes** OR provide a **DEMO mode** that executes in <5 minutes.

**Rationale:** Students should be able to quickly validate notebooks work before committing to full execution.

**Implementation:**
- For API-based notebooks: Include DEMO_MODE toggle (see Cell 3 in template)
- For simulation notebooks: Limit default simulations to <5 min runtime
- For data processing notebooks: Provide sample dataset option

**Validation:** Run `jupyter nbconvert --execute [notebook].ipynb` and time execution.

**Reference:** CLAUDE.md:415 (Execution time: <5 minutes)

---

### 2. Setup Cell (Cell 2)

**Standard:** All notebooks must have a standardized setup cell with:
- Standard library imports
- Environment configuration (if needed)
- Random seed setting for reproducibility
- Success indicator (`print("✅ Setup complete")`)

**Reference:** `.notebook-template.md:65-103` for full template

**Example:**
```python
# Standard library imports
import os
import json
from pathlib import Path
from typing import List, Dict, Any

# Data manipulation
import pandas as pd
import numpy as np

# Set random seed for reproducibility
import random
random.seed(42)
np.random.seed(42)

print("✅ Setup complete")
```

---

### 3. Cost Warning (Cell 1)

**Standard:** Notebooks that use paid API calls **MUST** include a cost warning cell with:
- Estimated cost breakdown by mode (DEMO vs FULL)
- Recommendation to start with DEMO mode
- Link to API usage monitoring
- Clear explanation of cost control options

**Reference:** `.notebook-template.md:38-62` for template

**Skip this cell if:** Notebook is simulation-based (cost = $0)

**Example:**
```markdown
## ⚠️ Cost Warning

This notebook makes API calls to OpenAI. Estimated costs:

| Mode | API Calls | Estimated Cost |
|------|-----------|----------------|
| **DEMO** (recommended) | 10 queries × gpt-4o-mini | **$0.01-0.02** |
| **FULL** | 100 queries × gpt-4o | **$1.50-2.00** |

**💡 Recommendation:** Start with DEMO mode to understand the notebook before running FULL mode.
```

---

### 4. Validation Assertions

**Standard:** Notebooks must include assertions to:
- Validate data types and shapes
- Verify business logic assumptions
- Catch errors early with descriptive messages
- Confirm successful completion of critical steps

**Reference:** `.notebook-template.md:308-327` for patterns

**Examples:**
```python
# Validate data types
assert isinstance(df, pd.DataFrame), "df must be a DataFrame"

# Validate data shape
assert len(df) > 0, "DataFrame is empty"
assert 'query' in df.columns, "Missing 'query' column"

# Validate value ranges
assert 0.0 <= tpr <= 1.0, f"TPR must be in [0, 1], got {tpr}"

print("✅ All validations passed")
```

---

### 5. Environment Validation (Cell 4)

**Standard:** Notebooks requiring API keys **MUST** validate key presence with:
- Clear error message if key is missing
- Instructions for setting up .env file
- Optional API connectivity test
- **NEVER** print actual API keys

**Reference:** `.notebook-template.md:161-191` for template

**Skip this cell if:** Notebook doesn't use API calls

**Example:**
```python
if "OPENAI_API_KEY" not in os.environ or not os.environ["OPENAI_API_KEY"]:
    raise ValueError(
        "❌ OPENAI_API_KEY not found in environment.\n"
        "Please set it in your .env file:\n"
        "  OPENAI_API_KEY=sk-...\n"
        "Then restart the notebook kernel."
    )

print("✅ OpenAI API key found")
```

---

### 6. Progress Indicators

**Standard:** For loops that take >10 seconds, include progress indicators with:
- Clear indication of progress (X/Y examples)
- Incremental updates (every 10 items or 10%)
- Final completion message

**Reference:** `.notebook-template.md:329-347` for patterns

**Example:**
```python
results = []
for idx, row in enumerate(df.iterrows(), 1):
    result = process_row(row)
    results.append(result)

    # Progress indicator every 10 items
    if idx % 10 == 0:
        print(f"Processed {idx}/{len(df)} examples...")

print(f"\n✅ Processing complete! Processed {len(results)} examples")
```

---

### 7. DEMO/FULL Mode Toggle (Cell 3)

**Standard:** API-based notebooks **MUST** provide a configuration cell with:
- Boolean `DEMO_MODE` toggle (default: True)
- Clear output indicating which mode is active
- Cost and time estimates for each mode
- Instructions for switching modes

**Reference:** `.notebook-template.md:107-158` for template

**Example:**
```python
# ========================================
# CONFIGURATION: Demo vs Full Mode
# ========================================

# Set DEMO_MODE = False to run on full dataset
DEMO_MODE = True  # Default: Quick demo for tutorial

if DEMO_MODE:
    SAMPLE_SIZE = 10  # Sample size for demo
    MODEL = "gpt-4o-mini"  # Cheaper model for demo
    print("🚀 DEMO MODE: Running on sample dataset")
    print(f"   Sample size: {SAMPLE_SIZE} examples")
    print(f"   Model: {MODEL}")
    print(f"   Estimated cost: $0.01-0.02 | Time: ~2-3 minutes")
else:
    SAMPLE_SIZE = None  # Use full dataset
    MODEL = "gpt-4o"  # Production model
    print("📊 FULL MODE: Running on complete dataset")
    print(f"   Full dataset: 100 examples")
    print(f"   Model: {MODEL}")
    print(f"   Estimated cost: $1.50-2.00 | Time: ~15-20 minutes")

print("\n💡 To switch modes, change DEMO_MODE in this cell and re-run notebook")
```

---

## Defensive Coding Requirements

All notebook functions must follow the **5-step defensive function pattern**:

1. **Type checking** - Validate argument types
2. **Input validation** - Check value constraints
3. **Edge case handling** - Handle empty inputs, None, etc.
4. **Main logic** - The actual computation
5. **Return** - Return validated result

**Reference:** CLAUDE.md:117-202 for full defensive coding pattern

**Example:**
```python
def calculate_similarity(text1: str, text2: str) -> float:
    """Calculate semantic similarity between two texts.

    Args:
        text1: First text string
        text2: Second text string

    Returns:
        Similarity score between 0.0 and 1.0

    Raises:
        TypeError: If inputs are not strings
        ValueError: If inputs are empty
    """
    # Step 1: Type checking
    if not isinstance(text1, str) or not isinstance(text2, str):
        raise TypeError("text1 and text2 must be strings")

    # Step 2: Input validation
    if not text1.strip() or not text2.strip():
        raise ValueError("Inputs cannot be empty strings")

    # Step 3: Edge case handling (if needed)

    # Step 4: Main logic
    similarity = compute_embedding_similarity(text1, text2)

    # Step 5: Return
    return similarity
```

---

## Error Handling

**Standard:** API calls and external dependencies must use try-except with:
- Specific exception types (not bare `except:`)
- Clear error messages
- Graceful fallback behavior
- Continue processing remaining examples

**Reference:** `.notebook-template.md:349-364` for patterns

**Example:**
```python
try:
    result = call_llm_api(query)
except Exception as e:
    print(f"❌ API call failed: {e}")
    result = None  # Fallback

# Defensive: Handle None results
if result is None:
    print("⚠️ Skipping example due to API error")
    continue
```

---

## Summary Cell Structure

**Standard:** All notebooks must end with a summary cell (markdown) containing:
- ✅ What was accomplished
- 📊 Key metrics/findings
- 🎯 Next steps for students
- 💡 Key takeaways

**Reference:** `.notebook-template.md:267-302` for template

---

## Template Reference

**Full Template:** See `.notebook-template.md` in project root for complete cell-by-cell structure.

**CLAUDE.md References:**
- CLAUDE.md:401-435 - Tutorial Development Workflow
- CLAUDE.md:412-418 - Tutorial Quality Standards
- CLAUDE.md:420-435 - Tutorial Types (Notebooks section: 427-430)

---

## Validation Checklist

Use this checklist when creating or reviewing notebooks:

- [ ] **Execution Time:** Executes in <5 minutes OR has DEMO mode
- [ ] **Setup Cell:** Includes all required imports and random seed
- [ ] **Cost Warning:** Present if notebook uses paid APIs
- [ ] **Environment Validation:** API key checking if needed
- [ ] **Configuration Cell:** DEMO/FULL mode toggle if API-based
- [ ] **Assertions:** Data validation assertions throughout
- [ ] **Progress Indicators:** For loops >10 seconds
- [ ] **Error Handling:** Try-except for API calls
- [ ] **Summary Cell:** Final summary with accomplishments and next steps
- [ ] **Defensive Functions:** All functions follow 5-step pattern

---

**Document Status:** ✅ Active
**Skill Reference:** `.claude/skills/tutorial-standards/SKILL.md`
