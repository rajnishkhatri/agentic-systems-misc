# Tutorial Index Template

## Purpose

The `TUTORIAL_INDEX.md` file serves as the **navigation hub** for a tutorial directory (homework/lesson). It helps students understand what they'll learn, how to navigate the content, and where to get help.

## Required Sections

Every `TUTORIAL_INDEX.md` must include the following sections:

### 1. Overview

**Purpose:** Provide a concise summary of the tutorial's focus

**Required Elements:**
- Brief description of what the tutorial covers (2-3 sentences)
- Estimated learning time
- Difficulty level (Beginner/Intermediate/Advanced)
- Prerequisites with links to prior tutorials

**Example:**
```markdown
## Overview

Lesson 9 introduces the **foundational principles of LLM evaluation** and **exact measurement techniques**. You'll learn why evaluating foundation models is challenging, how to interpret language modeling metrics like perplexity, and when to use exact vs. lexical vs. semantic similarity measurements.

**Learning Time:** ~3-4 hours
**Difficulty:** Intermediate
**Prerequisites:**
- [HW1: Prompt Engineering](../homeworks/hw1/TUTORIAL_INDEX.md) - Understanding of LLM behavior
- [HW2: Error Analysis](../homeworks/hw2/TUTORIAL_INDEX.md) - Systematic failure detection
- Basic understanding of probability and information theory
```

---

### 2. Learning Objectives

**Purpose:** Define clear, measurable outcomes students will achieve

**Required Elements:**
- Checkbox list (✅) of 3-5 specific learning outcomes
- Use action verbs: "Understand", "Implement", "Apply", "Choose", "Debug"

**Example:**
```markdown
## Learning Objectives

By completing these tutorials, you will be able to:
- ✅ Understand the unique challenges of evaluating foundation models
- ✅ Interpret perplexity, cross-entropy, BPC, and BPB metrics
- ✅ Implement and apply exact match, fuzzy match, BLEU score, and semantic similarity
- ✅ Choose the appropriate evaluation method based on task characteristics
- ✅ Debug evaluation failures and detect data contamination
```

---

### 3. Tutorials

**Purpose:** List all tutorial materials with metadata

**Required Elements for Each Tutorial:**
- File name
- Reading/execution time
- Cost estimate (for notebooks that call APIs)
- Topics covered
- "When to use" guidance

**Example:**
```markdown
## Tutorials

### 1. Evaluation Fundamentals
**File:** `evaluation_fundamentals.md`
**Reading Time:** 20-25 minutes
**Topics:**
- Challenges of evaluating foundation models
- Open-ended vs. close-ended evaluation trade-offs
- Benchmark evolution (GLUE → SuperGLUE → MMLU → MMLU-Pro)

**When to use:** Start here to understand why LLM evaluation is fundamentally different from traditional ML evaluation.

---

### 2. Perplexity Calculation Tutorial (Interactive Notebook)
**File:** `perplexity_calculation_tutorial.ipynb`
**Execution Time:** <3 minutes
**Cost:** $0 (uses pre-calculated results)
**Topics:**
- Calculate perplexity from cross-entropy
- Visualize perplexity vs. model size

**When to use:** Hands-on practice with perplexity calculations.
```

---

### 4. Recommended Learning Path

**Purpose:** Provide a structured sequence for completing tutorials

**Required Elements:**
- Visual diagram (ASCII or Mermaid) showing tutorial flow
- Clear sequential steps (1 → 2 → 3)
- Final outcome/next steps

**Example:**
```markdown
## Recommended Learning Path

┌─────────────────────────────────────────────────────┐
│              Lesson 9 Learning Flow                 │
├─────────────────────────────────────────────────────┤
│                                                     │
│  1. Read README.md                                  │
│     ↓                                               │
│  2. Complete Evaluation Fundamentals Tutorial      │
│     ↓                                               │
│  3. Run Perplexity Calculation Notebook            │
│     ↓                                               │
│  4. Apply learnings to your own evaluation tasks   │
└─────────────────────────────────────────────────────┘
```

---

### 5. Common Pitfalls

**Purpose:** Warn students about frequent mistakes

**Required Elements:**
- List of 3-5 common mistakes
- Use ❌ emoji for anti-patterns
- Provide brief explanation of why it's a pitfall

**Example:**
```markdown
## Common Pitfalls

### Perplexity
- ❌ **Comparing perplexity across different tokenizers** → Tokenizer design affects perplexity significantly
- ❌ **Using perplexity alone for instruction-following models** → RLHF reduces perplexity correlation with quality

### Similarity Measurements
- ❌ **Using exact match for natural language** → Too strict, penalizes valid paraphrases
- ❌ **Not normalizing text before comparison** → Case sensitivity, whitespace differences cause false negatives
```

---

### 6. FAQ

**Purpose:** Answer common student questions

**Required Elements:**
- 3-5 frequently asked questions
- Use **Q:** and **A:** format
- Provide actionable, specific answers

**Example:**
```markdown
## FAQ

**Q: When should I use perplexity vs. task-specific metrics?**
A: Use perplexity for comparing base language models (pre-training quality). Use task-specific metrics for instruction-following or fine-tuned models.

**Q: Should I use BLEU for chatbot evaluation?**
A: No. BLEU is designed for translation where there's a reference answer. Use semantic similarity or AI-as-judge for open-ended responses.

**Q: How do I choose a threshold for fuzzy matching?**
A: Analyze precision-recall curves on a validation set. Common thresholds: 0.8-0.9 for Levenshtein similarity ratio.
```

---

## Optional Sections

### Key Concepts
Summary of core concepts with formulas, tables, or definitions

### Practical Exercises
Hands-on exercises for students to apply learnings

### Resources
Links to reference files, diagrams, external documentation

### Next Steps
What students should do after completing this tutorial (link to next lesson)

---

## Writing Guidelines

### Reading Time Target
- **Concept tutorials (.md):** 15-30 minutes
- **Interactive notebooks (.ipynb):** <5 minutes execution time

### Tone
- Direct, instructional, student-focused
- Use second person ("you will learn", "try this exercise")
- Avoid marketing language ("amazing", "revolutionary")

### Links
- Use **relative paths** for stability (see `cross-linking-rules.md`)
- Link to prerequisites, next lessons, reference implementations
- Ensure all links are valid (use `/validate-tutorial` command)

### Maintenance
- Include "Last Updated" date at bottom
- Mark status (✅ Complete, ⏳ In Development, 🚧 Under Revision)
- Update when tutorial content changes (track in `TUTORIAL_CHANGELOG.md`)

---

## Gold Standard Example

See `.claude/skills/tutorial-standards/examples/lesson-9-tutorial-index.md` for a complete reference implementation.

---

## Validation

Use `/validate-tutorial` command to check:
- ✅ All required sections present
- ✅ Links resolve correctly
- ✅ Reading time targets met
- ✅ Notebooks execute successfully
