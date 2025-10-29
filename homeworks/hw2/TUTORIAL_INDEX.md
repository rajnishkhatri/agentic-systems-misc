# Homework 2: Tutorial Index

## Overview

Homework 2 teaches **systematic error analysis** using qualitative research methods. You'll learn to identify failure patterns through open and axial coding, build comprehensive failure taxonomies, and use LLMs to generate synthetic test queries based on identified dimensions.

**Learning Time:** ~4-5 hours
**Difficulty:** Intermediate
**Prerequisites:** Completion of HW1 (basic prompt engineering)

---

## Learning Objectives

By completing these tutorials, you will be able to:
- ✅ Perform open coding to identify patterns in bot failures
- ✅ Apply axial coding to group observations into structured failure modes
- ✅ Build comprehensive failure mode taxonomies with clear definitions
- ✅ Use LLMs to generate dimension tuples and synthetic queries
- ✅ Understand qualitative evaluation methodology from research literature
- ✅ Create illustrative examples and edge cases for each failure mode

---

## Tutorials

### 1. Error Analysis Concepts
**File:** `error_analysis_concepts.md`
**Reading Time:** 20-25 minutes
**Topics:**
- Introduction to qualitative evaluation in AI systems
- Open coding: Identifying initial patterns and themes
- Axial coding: Grouping observations into categories
- From observations to actionable failure modes
- Documentation best practices for error analysis
- Balancing breadth vs. depth in failure identification

**When to use:** Start here to understand the methodology before analyzing your bot's outputs.

---

### 2. Dimension Generation Tutorial (Interactive)
**File:** `dimension_generation_tutorial.ipynb`
**Execution Time:** 10-15 minutes
**Topics:**
- Identifying key dimensions for query generation
- Using LLMs to generate dimension tuples
- Prompt engineering for tuple generation
- Converting tuples to natural language queries
- Validating and filtering generated queries
- Cost optimization for LLM-based generation

**When to use:** After identifying failure patterns, use this to systematically generate test queries.

**Interactive Features:**
- Live LLM API calls for tuple generation
- Query quality validation checks
- Cost estimation calculator
- Export to CSV functionality

---

### 3. Failure Mode Taxonomy Tutorial
**File:** `failure_mode_taxonomy_tutorial.md`
**Reading Time:** 20-25 minutes
**Topics:**
- Taxonomy structure: Title, Definition, Examples
- Writing clear, testable failure mode definitions
- Creating representative examples from real traces
- Handling hypothetical vs. observed failures
- Multi-dimensional failure classification
- Maintaining taxonomy consistency

**When to use:** After open/axial coding, use this to formalize your failure taxonomy.

---

### 4. Error Analysis Pipeline (Visual)
**File:** `diagrams/error_analysis_pipeline.mmd`
**Format:** Mermaid diagram (viewable on GitHub)
**Topics:**
- Complete workflow from dimensions to queries to analysis
- Decision points in the error analysis process
- Iteration loops and refinement cycles
- Integration with bulk testing scripts

**When to use:** Reference this to understand how all pieces fit together.

---

## Recommended Learning Path

```
┌──────────────────────────────────────────────────────────┐
│              HW2 Error Analysis Workflow                 │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  1. Read README.md & watch HW2 walkthrough videos       │
│     ↓                                                    │
│  2. Complete "Error Analysis Concepts" tutorial         │
│     ↓                                                    │
│  3. Run your bot on diverse queries (from HW1)          │
│     ↓                                                    │
│  4. Perform open coding on results                      │
│     (Review traces, take notes, identify patterns)      │
│     ↓                                                    │
│  5. Perform axial coding                                │
│     (Group patterns into failure modes)                 │
│     ↓                                                    │
│  6. Complete "Failure Mode Taxonomy" tutorial           │
│     ↓                                                    │
│  7. Formalize your taxonomy                             │
│     (Write definitions and examples)                    │
│     ↓                                                    │
│  8. Complete "Dimension Generation" tutorial            │
│     ↓                                                    │
│  9. Generate synthetic queries to test failure modes    │
│     ↓                                                    │
│ 10. Create error_analysis spreadsheet (optional)        │
│     ↓                                                    │
│ 11. Iterate: Test → Analyze → Refine                    │
└──────────────────────────────────────────────────────────┘
```

---

## Key Concepts

### Open Coding
**Open coding** is the initial analysis phase where you:
- Review interaction traces without preconceived categories
- Assign descriptive labels to interesting patterns
- Take detailed notes on observations
- Avoid forcing observations into predetermined buckets

**Example:**
```
Trace 42: Bot suggested honey for vegan recipe
  → Note: "Dietary restriction violation"
  → Note: "Knowledge gap: honey isn't vegan"

Trace 58: Bot provided 15-ingredient recipe for "quick meal"
  → Note: "Misalignment with user intent"
  → Note: "No time constraint interpretation"
```

### Axial Coding
**Axial coding** groups open codes into broader failure mode categories:
- Identify common themes across observations
- Create hierarchical structure (categories → sub-categories)
- Define relationships between failure modes
- Ensure categories are mutually exclusive and collectively exhaustive

**Example:**
```
Open codes:
  - "Honey in vegan recipe"
  - "Butter in dairy-free recipe"
  - "Wheat flour in gluten-free recipe"

Axial category:
  → FAILURE MODE: Dietary Restriction Violations
```

### Failure Taxonomy
A **failure taxonomy** is a structured documentation of failure modes with:
- **Title:** Short, descriptive name (e.g., "Ingredient Substitution Failure")
- **Definition:** One-sentence explanation of when this failure occurs
- **Examples:** 1-2 concrete instances from your testing

**Template:**
```markdown
### Failure Mode: [Title]

**Definition:** [One sentence describing the failure condition]

**Examples:**
1. [Real example from trace X]
2. [Real or hypothetical example]
```

---

## Practical Exercises

After completing the tutorials, try these exercises:

1. **Open Coding Practice**
   - Take 10 bot traces from HW1
   - Spend 5 minutes per trace identifying patterns
   - Write at least 3 observations per trace
   - Look for recurring themes

2. **Taxonomy Building Exercise**
   - Group your open codes into 3-5 broad categories
   - Write formal definitions for each category
   - Find 2 examples for each failure mode
   - Test definitions with new traces

3. **Synthetic Query Generation**
   - Identify 3 dimensions relevant to recipe queries
   - Generate 15-20 tuples using the dimension generation tutorial
   - Convert 5-7 tuples to natural language queries
   - Test queries on your bot

---

## Common Pitfalls

### Open Coding
- ❌ **Premature categorization:** Forcing observations into predefined buckets
- ❌ **Insufficient detail:** Notes like "bad response" aren't actionable
- ❌ **Confirmation bias:** Only noting failures, missing successful patterns
- ❌ **Inconsistent granularity:** Some notes are too specific, others too vague

### Axial Coding
- ❌ **Overlapping categories:** Failure modes aren't mutually exclusive
- ❌ **Too broad:** "Bot makes mistakes" isn't a useful category
- ❌ **Too narrow:** Having 20+ failure modes dilutes focus
- ❌ **Missing hierarchy:** No organization of related failure modes

### Taxonomy Writing
- ❌ **Vague definitions:** "Bot sometimes gives wrong answers"
- ❌ **No examples:** Definitions without concrete instances
- ❌ **Hypothetical-only examples:** No grounding in real observations
- ❌ **Untestable definitions:** Can't determine if a new trace matches

---

## Reference Files

### Assignment Materials
- [`README.md`](README.md) - Assignment instructions
- [`hw2_solution_walkthrough.ipynb`](hw2_solution_walkthrough.ipynb) - Complete worked example
- [`failure_mode_taxonomy.md`](failure_mode_taxonomy.md) - Example taxonomy
- [`error_analysis_template.csv`](error_analysis_template.csv) - Spreadsheet template
- [`results_20250518_215844.csv`](results_20250518_215844.csv) - Sample bot traces

### Code References
- [`generate_synthetic_queries.py`](generate_synthetic_queries.py) - LLM-based query generation
- [`scripts/bulk_test.py`](../../scripts/bulk_test.py) - Bulk testing script

### Video Walkthroughs
- [HW2 Code Walkthrough](https://youtu.be/h9oAAAYnGx4?si=fWxN3NtpSbdD55cW)
- [Open & Axial Coding Walkthrough](https://youtu.be/AKg27L4E0M8)

---

## Tools & Libraries

**Required:**
- `pandas` - Data manipulation for trace analysis
- `litellm` - LLM API calls for query generation
- Any spreadsheet software (Excel, Google Sheets) for error analysis

**Optional:**
- `tqdm` - Progress bars for bulk operations
- Qualitative coding software (ATLAS.ti, NVivo) for advanced analysis

---

## Expected Outputs

After completing HW2, you should have:
- ✅ 3-5 clearly defined failure modes
- ✅ Formal taxonomy with titles, definitions, and examples
- ✅ 15-20 synthetic test queries covering identified dimensions
- ✅ (Optional) Error analysis spreadsheet tracking failure modes
- ✅ Documented observations from open and axial coding

---

## Connection to Literature

This assignment is based on qualitative research methods from:
- **Grounded Theory** (Glaser & Strauss, 1967)
- **Open/Axial Coding** from qualitative data analysis
- **Failure Mode and Effects Analysis (FMEA)** from reliability engineering
- Applied to AI system evaluation by course instructors

**Key Insight:** Systematic qualitative methods prevent "vibes-based" evaluation and enable reproducible analysis.

---

## Next Steps

After completing HW2, you'll have:
- ✅ Identified specific failure modes in your bot
- ✅ Systematic taxonomy for categorizing errors
- ✅ Test query generation capabilities

**Move on to Homework 3** to learn automated evaluation using LLM-as-Judge.

👉 [Homework 3 Tutorial Index](../hw3/TUTORIAL_INDEX.md)

---

## FAQ

**Q: How many traces should I analyze for open coding?**
A: Start with 10-20 traces. Look for saturation (no new patterns emerging).

**Q: Can I use LLMs to help with open coding?**
A: Yes, but validate all LLM-generated codes. Human judgment is essential.

**Q: How specific should failure mode definitions be?**
A: Specific enough to determine if a new trace matches, but broad enough to cover multiple instances.

**Q: Should all failure modes have observed examples?**
A: Ideally yes. Hypothetical examples are acceptable if well-reasoned.

**Q: How do I choose dimensions for query generation?**
A: Look at what varied in your failure examples. Common dimensions: cuisine, dietary restrictions, meal type, time constraints.

---

**Tutorial Status:** ⏳ In Development
**Last Updated:** 2025-10-29
**Maintainer:** AI Evaluation Course Team
