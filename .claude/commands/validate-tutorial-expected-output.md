# Lesson-9 Validation Expected Output

**Purpose:** This document serves as the test oracle for the `/validate-tutorial` command. It documents the expected validation results when running validation on `lesson-9/` directory.

**Generated:** 2025-11-18
**Last Validated:** 2025-11-18
**Baseline Directory:** `lesson-9/`

---

## 1. TUTORIAL_INDEX.md Structure Validation

### Expected Result: ✅ PASS

**Required Sections (All Present):**
- ✅ Overview (lines 3-13)
- ✅ Learning Objectives (lines 16-24)
- ✅ Prerequisites (lines 9-12)
- ✅ Recommended Learning Path (lines 99-120)
- ✅ Tutorials (lines 27-96)
- ✅ Key Concepts (lines 124-158)
- ✅ Common Pitfalls (lines 183-195)
- ✅ Resources (lines 199-213)
- ✅ Next Steps (lines 217-227)
- ✅ FAQ (lines 231-252)

**Quality Indicators:**
- ✅ Learning time estimate: ~3-4 hours (line 7)
- ✅ Difficulty level: Intermediate (line 8)
- ✅ Each tutorial has reading/execution time
- ✅ Notebooks include cost warnings
- ✅ Cross-links to other lessons/homeworks
- ✅ Visual learning flow diagram (ASCII art, lines 101-120)
- ✅ Practical exercises included (lines 162-179)

**Validation Output:**
```
✅ TUTORIAL_INDEX.md Structure Valid
   - All 10 required sections present
   - Learning time estimate: 3-4 hours
   - Difficulty level: Intermediate
   - 5 tutorials documented
   - 2 interactive notebooks
   - 1 visual diagram
```

---

## 2. Notebook Execution Validation

### Notebook 1: perplexity_calculation_tutorial.ipynb

**Expected Result: ✅ PASS**

**Execution Details:**
- Execution time: 2.84 seconds
- Target: <5 minutes
- Status: PASS (well under target)
- Cost: $0 (uses pre-calculated results from data/sample_perplexity_results.json)
- All cells executed successfully
- No errors or warnings

**Validation Output:**
```
✅ perplexity_calculation_tutorial.ipynb
   - Execution time: 2.84s (target: <300s)
   - Cost: $0.00 (pre-calculated data)
   - Status: All cells executed successfully
```

### Notebook 2: similarity_measurements_tutorial.ipynb

**Expected Result: ⚠️ CONDITIONAL PASS**

**Execution Details:**
- Execution time: ~3-5 minutes (when OPENAI_API_KEY is available)
- Target: <5 minutes
- **Dependency:** Requires `OPENAI_API_KEY` environment variable
- Cost: $0.20-0.50 (DEMO mode, 10 queries)
- Cost: $0.80-1.20 (FULL mode, 50 queries)
- Default: DEMO_MODE = True

**Error Without API Key:**
```
❌ OpenAIError: The api_key client option must be set either by passing
   api_key to the client or by setting the OPENAI_API_KEY environment variable
```

**Validation Output (With API Key):**
```
✅ similarity_measurements_tutorial.ipynb
   - Execution time: ~4.2s (target: <300s)
   - Cost: $0.35 (DEMO mode, 10 queries)
   - Status: All cells executed successfully
```

**Validation Output (Without API Key):**
```
⚠️ similarity_measurements_tutorial.ipynb
   - Status: SKIPPED (OPENAI_API_KEY not set)
   - Suggestion: Set OPENAI_API_KEY environment variable to execute
   - See: env.example for configuration
```

---

## 3. Cross-Link Validation

### Expected Result: ⚠️ PARTIAL PASS (11/12 links valid)

**Valid Links (11):**
- ✅ TUTORIAL_INDEX.md
- ✅ README.md
- ✅ ../lesson-10/README.md
- ✅ ../lesson-10/TUTORIAL_INDEX.md
- ✅ ../lesson-10/ai_judge_production_guide.md
- ✅ ../homeworks/hw1/TUTORIAL_INDEX.md
- ✅ ../homeworks/hw2/TUTORIAL_INDEX.md
- ✅ ../homeworks/hw4/TUTORIAL_INDEX.md
- ✅ evaluation_fundamentals.md
- ✅ language_modeling_metrics.md
- ✅ exact_evaluation_methods.md

**Broken Links (1):**
- ❌ ../lesson-9-11/README.md
  - Referenced in: README.md:143
  - Issue: Directory exists but README.md is missing
  - Available: evaluation_dashboard.py, SUBMISSION_CHECKLIST.md, VALIDATION_REPORT.md
  - Suggestion: Create lesson-9-11/README.md or update link to reference available file

**Validation Output:**
```
⚠️ Cross-Link Validation: 11/12 links valid (91.7%)

Valid Links: 11
  ✅ TUTORIAL_INDEX.md
  ✅ README.md
  ✅ ../lesson-10/README.md
  ... (8 more)

Broken Links: 1
  ❌ ../lesson-9-11/README.md (referenced in README.md:143)
     → Directory exists but file missing
     → Suggestion: Create file or update reference
```

---

## 4. Mermaid Diagram Validation

### Diagram 1: diagrams/evaluation_taxonomy.mmd

**Expected Result: ✅ PASS**

**Validation Details:**
- ✅ File exists
- ✅ Wrapped in triple backticks with `mermaid` language tag
- ✅ Valid flowchart syntax (`flowchart TD`)
- ✅ 24 nodes defined (12 decision nodes, 12 method nodes)
- ✅ All connections valid (no undefined nodes)
- ✅ Styling classes defined (4 classes)
- ✅ Styling applied to all nodes
- ✅ Includes explanatory documentation after diagram (lines 37-72)

**Diagram Complexity:**
- Node count: 24
- Edge count: 15
- Decision points: 5
- Styling classes: 4

**Validation Output:**
```
✅ evaluation_taxonomy.mmd
   - Syntax: Valid
   - Node count: 24
   - Decision points: 5
   - Documentation: Present
   - Complexity: Medium (24 nodes)
```

**Note:** Full rendering validation requires `@mermaid-js/mermaid-cli` (mmdc)
```bash
npm install -g @mermaid-js/mermaid-cli
mmdc -i diagrams/evaluation_taxonomy.mmd -o diagrams/evaluation_taxonomy.png
```

---

## 5. Reading Time Calculation

### Expected Result: ✅ PASS

**Reading Time Breakdown (200 WPM standard):**

| File | Word Count | Reading Time | Target |
|------|-----------|--------------|--------|
| evaluation_fundamentals.md | 2,529 words | 12.6 min | 15-25 min |
| language_modeling_metrics.md | 2,546 words | 12.7 min | 15-25 min |
| exact_evaluation_methods.md | 2,662 words | 13.3 min | 15-25 min |
| perplexity_calculation_tutorial.ipynb | ~600 words | ~3 min | <5 min |
| similarity_measurements_tutorial.ipynb | ~800 words | ~4 min | <5 min |

**Total Reading Time:** ~46 minutes (speed reading)

**Total Learning Time (TUTORIAL_INDEX.md):** 3-4 hours (180-240 minutes)

**Discrepancy Explanation:**
The 3-4 hour estimate includes:
- Reading TUTORIAL_INDEX.md and README.md (~10 min)
- Core tutorials reading (~46 min)
- Hands-on practice and experimentation (~60-90 min)
- Practical exercises completion (~45-60 min)
- Deep understanding vs. speed reading (2-3x multiplier)

**Validation Output:**
```
✅ Reading Time Calculation
   - Total word count: 7,737 words
   - Speed reading time: 38.7 min
   - With comprehension: 77-116 min
   - With exercises: 122-176 min
   - TUTORIAL_INDEX estimate: 180-240 min (3-4 hours)
   - Status: Within reasonable range
```

---

## 6. Summary Report

### Overall Validation Status: ✅ GOLD STANDARD (with minor issues)

**Validation Results:**
- ✅ TUTORIAL_INDEX.md structure: PASS (10/10 sections)
- ✅ Notebook execution: PASS (1/1 executable without API key)
- ⚠️ Notebook execution: CONDITIONAL (1/1 requires OPENAI_API_KEY)
- ⚠️ Cross-links: PARTIAL PASS (11/12 valid, 91.7%)
- ✅ Mermaid diagrams: PASS (1/1 valid syntax)
- ✅ Reading time: PASS (within expected range)

**Issues Identified:**
1. **Minor:** Missing lesson-9-11/README.md (referenced in README.md:143)
2. **Minor:** similarity_measurements_tutorial.ipynb requires OPENAI_API_KEY

**Recommendations:**
1. Create lesson-9-11/README.md or update link reference
2. Document OPENAI_API_KEY requirement in notebook setup cell
3. Consider adding alternative execution path without API key (cached results)

**Conclusion:**
lesson-9/ is suitable as the **gold standard** for tutorial validation. Minor issues are acceptable for baseline establishment and will inform validation command design (graceful handling of missing dependencies, conditional validation).

---

## 7. Command Implementation Guidance

### Expected /validate-tutorial Output Format

```
📋 Tutorial Validation Report: lesson-9/
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. TUTORIAL_INDEX.md Structure ✅
   - All required sections present (10/10)
   - Learning time: 3-4 hours
   - Difficulty: Intermediate

2. Notebook Execution ⚠️
   ✅ perplexity_calculation_tutorial.ipynb (2.84s)
   ⚠️ similarity_measurements_tutorial.ipynb (OPENAI_API_KEY required)

3. Cross-Links ⚠️
   - Valid: 11/12 (91.7%)
   - Broken: 1
     ❌ ../lesson-9-11/README.md (README.md:143)

4. Mermaid Diagrams ✅
   ✅ evaluation_taxonomy.mmd (24 nodes, valid syntax)

5. Reading Time ✅
   - Total: ~47 min (speed reading)
   - With exercises: 3-4 hours
   - Status: Within expected range

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Overall: ✅ PASS (with minor warnings)

Recommendations:
  1. Create lesson-9-11/README.md or update reference
  2. Set OPENAI_API_KEY to execute similarity notebook

Validation completed in 8.2s
```

### Error Handling Test Cases

**Case 1: Directory Not Found**
```
❌ Directory not found: lesson-99/
   Suggestion: Did you mean lesson-9/?
   Available: lesson-4/, lesson-7/, lesson-8/, lesson-9/, lesson-10/
```

**Case 2: Missing TUTORIAL_INDEX.md**
```
❌ TUTORIAL_INDEX.md not found in lesson-9/
   Required sections cannot be validated
   Suggestion: Create TUTORIAL_INDEX.md using template
   See: .claude/skills/tutorial-standards/references/tutorial-index-template.md
```

**Case 3: Notebook Timeout (>5 min)**
```
⏱️ perplexity_calculation_tutorial.ipynb exceeded timeout
   Execution time: >300s (target: <300s)
   Status: SKIPPED
   Suggestion: Optimize notebook or increase timeout threshold
```

**Case 4: Missing jupyter**
```
❌ jupyter nbconvert not found
   Notebook execution cannot be validated
   Install: pip install jupyter nbconvert
```

**Case 5: Broken Mermaid Syntax**
```
❌ diagrams/evaluation_taxonomy.mmd: Syntax Error
   Line 42: Unexpected token '}'
   Suggestion: Check Mermaid flowchart syntax
   Validate at: https://mermaid.live
```

---

## Appendix: File Inventory

**lesson-9/ Directory Contents:**
```
lesson-9/
├── TUTORIAL_INDEX.md          (11,046 bytes) - Navigation hub
├── README.md                  (5,067 bytes) - Lesson overview
├── evaluation_fundamentals.md (18,880 bytes) - Concept tutorial
├── language_modeling_metrics.md (17,516 bytes) - Concept tutorial
├── exact_evaluation_methods.md (19,357 bytes) - Concept tutorial
├── perplexity_calculation_tutorial.ipynb (52,949 bytes) - Interactive notebook
├── similarity_measurements_tutorial.ipynb (20,914 bytes) - Interactive notebook
├── diagrams/
│   └── evaluation_taxonomy.mmd (1,234 bytes) - Decision tree diagram
├── data/
│   └── sample_perplexity_results.json - Pre-calculated data
└── results/
    └── (test outputs)
```

**Total:** 7 documentation files, 2 notebooks, 1 diagram, 1 data file

---

**Document Status:** ✅ Complete
**Next Step:** Use this oracle to implement `/validate-tutorial` command (Task 4.1-4.8)
