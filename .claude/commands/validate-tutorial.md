# /validate-tutorial Command

**Version:** 1.0.0
**Category:** Tutorial Quality Assurance
**Related Skill:** `.claude/skills/tutorial-standards/SKILL.md`

---

## Purpose

Validates tutorial directories against quality standards by checking TUTORIAL_INDEX.md structure, notebook execution, cross-links, Mermaid diagrams, and reading time estimates.

## Usage

```
/validate-tutorial [directory]
```

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| directory | string | Yes | - | Path to tutorial directory (e.g., `lesson-9/`, `homeworks/hw3/`) |

### Examples

```bash
# Validate a lesson
/validate-tutorial lesson-9/

# Validate a homework
/validate-tutorial homeworks/hw3/

# Validate with relative path
/validate-tutorial ../lesson-10/
```

---

## Validation Checks

### 1. TUTORIAL_INDEX.md Structure Validation
**What it checks:**
- ✅ File exists in target directory
- ✅ Required sections present (10 sections):
  - Overview
  - Learning Objectives
  - Prerequisites
  - Tutorials
  - Recommended Learning Path
  - Key Concepts
  - Common Pitfalls
  - Resources
  - Next Steps
  - FAQ
- ✅ Quality indicators:
  - Learning time estimate present
  - Difficulty level specified
  - Tutorial reading/execution times documented
  - Cross-links to related lessons/homeworks

**Output format:**
```
✅ TUTORIAL_INDEX.md Structure Valid
   - All required sections present (10/10)
   - Learning time: 3-4 hours
   - Difficulty: Intermediate
   - 5 tutorials documented

❌ TUTORIAL_INDEX.md Structure Invalid
   - Missing sections: FAQ, Common Pitfalls
   - Recommendation: Add missing sections using template
```

### 2. Notebook Execution Validation
**What it checks:**
- ✅ All `.ipynb` files in directory
- ✅ Execute each notebook with `jupyter nbconvert --execute`
- ✅ Execution time < 5 minutes (300 seconds)
- ✅ No execution errors
- ⚠️ Graceful handling of missing dependencies (API keys, packages)

**Output format:**
```
✅ perplexity_calculation_tutorial.ipynb
   - Execution time: 2.84s (target: <300s)
   - Cost: $0.00 (pre-calculated data)
   - Status: All cells executed successfully

⚠️ similarity_measurements_tutorial.ipynb
   - Status: SKIPPED (OPENAI_API_KEY not set)
   - Suggestion: Set OPENAI_API_KEY to execute
   - See: env.example for configuration

❌ failing_notebook.ipynb
   - Execution time: 15.3s
   - Error: NameError: name 'undefined_variable' is not defined
   - Cell: 7
   - Suggestion: Define 'undefined_variable' before use
```

### 3. Cross-Link Validation
**What it checks:**
- ✅ All relative links in `.md` files
- ✅ Links resolve to existing files
- ✅ No broken references to other lessons/homeworks
- ⚠️ Reports broken links with suggestions

**Output format:**
```
✅ Cross-Links Valid: 12/12 (100%)

⚠️ Cross-Links: 11/12 valid (91.7%)
   Broken Links: 1
   ❌ ../lesson-9-11/README.md (referenced in README.md:143)
      → Directory exists but file missing
      → Suggestion: Create file or update reference
```

### 4. Mermaid Diagram Validation
**What it checks:**
- ✅ All `.mmd` files in `diagrams/` subdirectory
- ✅ Valid Mermaid syntax (flowchart, graph, sequence, etc.)
- ✅ No undefined nodes or connections
- ✅ Wrapped in triple backticks with `mermaid` language tag

**Output format:**
```
✅ evaluation_taxonomy.mmd
   - Syntax: Valid
   - Node count: 24
   - Decision points: 5
   - Documentation: Present

❌ broken_diagram.mmd
   - Syntax Error: Line 42: Unexpected token '}'
   - Suggestion: Check Mermaid syntax at https://mermaid.live
```

### 5. Reading Time Calculation
**What it checks:**
- ✅ Word count for all `.md` tutorial files
- ✅ Calculate reading time (200 WPM standard)
- ✅ Compare with TUTORIAL_INDEX.md time estimate
- ✅ Validate reading time is within target range (15-30 min per tutorial)

**Output format:**
```
✅ Reading Time Calculation
   - Total word count: 7,737 words
   - Speed reading: 38.7 min
   - With exercises: 3-4 hours
   - TUTORIAL_INDEX estimate: 3-4 hours
   - Status: Within reasonable range

⚠️ Reading Time Exceeds Target
   - evaluation_fundamentals.md: 45 min (target: 15-30 min)
   - Suggestion: Split into multiple tutorials or reduce content
```

---

## Output Format

### Success Report

```
📋 Tutorial Validation Report: lesson-9/
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. TUTORIAL_INDEX.md Structure ✅
   - All required sections present (10/10)
   - Learning time: 3-4 hours
   - Difficulty: Intermediate

2. Notebook Execution ✅
   ✅ perplexity_calculation_tutorial.ipynb (2.84s)
   ✅ similarity_measurements_tutorial.ipynb (4.2s)

3. Cross-Links ✅
   - Valid: 12/12 (100%)

4. Mermaid Diagrams ✅
   ✅ evaluation_taxonomy.mmd (24 nodes, valid syntax)

5. Reading Time ✅
   - Total: ~47 min (speed reading)
   - With exercises: 3-4 hours
   - Status: Within expected range

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Overall: ✅ PASS

Validation completed in 8.2s
```

### Report with Warnings

```
📋 Tutorial Validation Report: lesson-9/
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. TUTORIAL_INDEX.md Structure ✅
   - All required sections present (10/10)

2. Notebook Execution ⚠️
   ✅ perplexity_calculation_tutorial.ipynb (2.84s)
   ⚠️ similarity_measurements_tutorial.ipynb (OPENAI_API_KEY required)

3. Cross-Links ⚠️
   - Valid: 11/12 (91.7%)
   - Broken: 1
     ❌ ../lesson-9-11/README.md (README.md:143)

4. Mermaid Diagrams ✅
   ✅ evaluation_taxonomy.mmd (24 nodes)

5. Reading Time ✅
   - Within expected range

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Overall: ⚠️ PASS (with warnings)

Recommendations:
  1. Create lesson-9-11/README.md or update reference
  2. Set OPENAI_API_KEY to execute similarity notebook

Validation completed in 8.2s
```

---

## Error Handling

### Error: Directory Not Found
```
❌ Directory not found: lesson-99/
   Suggestion: Did you mean lesson-9/?
   Available: lesson-4/, lesson-7/, lesson-8/, lesson-9/, lesson-10/
```

### Error: Missing TUTORIAL_INDEX.md
```
❌ TUTORIAL_INDEX.md not found in lesson-9/
   Required sections cannot be validated
   Suggestion: Create TUTORIAL_INDEX.md using template
   See: .claude/skills/tutorial-standards/references/tutorial-index-template.md
```

### Error: Notebook Timeout
```
⏱️ perplexity_calculation_tutorial.ipynb exceeded timeout
   Execution time: >300s (target: <300s)
   Status: SKIPPED
   Suggestion: Optimize notebook or increase timeout threshold
```

### Error: Missing jupyter Dependency
```
❌ jupyter nbconvert not found
   Notebook execution cannot be validated
   Install: pip install jupyter nbconvert
```

### Error: Broken Mermaid Syntax
```
❌ diagrams/evaluation_taxonomy.mmd: Syntax Error
   Line 42: Unexpected token '}'
   Suggestion: Check Mermaid flowchart syntax
   Validate at: https://mermaid.live
```

### Error: Permission Denied
```
❌ Permission denied reading lesson-9/TUTORIAL_INDEX.md
   Check file permissions
   Suggestion: chmod +r lesson-9/TUTORIAL_INDEX.md
```

---

## Implementation Details

### Dependencies
- `jupyter nbconvert` - Notebook execution
- Python `pathlib` - Path handling
- Python `re` - Markdown parsing and link extraction
- Optional: `@mermaid-js/mermaid-cli` - Full Mermaid rendering validation

### Validation Sequence
1. **Pre-flight checks** (directory exists, TUTORIAL_INDEX.md present)
2. **TUTORIAL_INDEX.md structure** (section validation)
3. **Notebook execution** (parallel execution with timeout)
4. **Cross-link validation** (parse all .md files, check links)
5. **Mermaid diagram validation** (syntax parsing)
6. **Reading time calculation** (word count analysis)
7. **Generate report** (formatted output with recommendations)

### Performance Targets
- Validation completes in <30 seconds for typical tutorials
- Notebook execution timeout: 5 minutes per notebook
- Graceful degradation if optional dependencies missing

---

## Integration with Tutorial Standards Skill

This command works with `.claude/skills/tutorial-standards/SKILL.md`:

**Command role:** Manual validation and quality assurance
**Skill role:** Automatic guidance during tutorial creation

**Workflow:**
1. User creates tutorial → Skill provides guidance
2. User runs `/validate-tutorial` → Command validates quality
3. User fixes issues → Skill ensures standards compliance
4. User re-runs validation → Command confirms fixes

---

## Examples

### Example 1: Validate lesson-9 (Gold Standard)
```bash
/validate-tutorial lesson-9/

# Expected: ✅ PASS (with minor warnings)
# - TUTORIAL_INDEX.md: ✅ Complete
# - Notebooks: ✅ Execute successfully
# - Cross-links: ⚠️ 1 broken link
# - Mermaid: ✅ Valid syntax
# - Reading time: ✅ Within range
```

### Example 2: Validate incomplete homework
```bash
/validate-tutorial homeworks/hw3/

# Expected: ❌ FAIL
# - TUTORIAL_INDEX.md: ❌ Missing sections (FAQ, Common Pitfalls)
# - Notebooks: ⚠️ 1 notebook exceeds timeout
# - Cross-links: ✅ All valid
# - Mermaid: N/A (no diagrams)
# - Reading time: ✅ Within range
```

### Example 3: Validate with missing dependencies
```bash
/validate-tutorial lesson-10/

# Expected: ⚠️ CONDITIONAL PASS
# - TUTORIAL_INDEX.md: ✅ Complete
# - Notebooks: ⚠️ SKIPPED (jupyter not installed)
# - Cross-links: ✅ All valid
# - Mermaid: ✅ Valid syntax
# - Reading time: ✅ Within range
```

---

## Reference Files

- **Expected Output:** `.claude/commands/validate-tutorial-expected-output.md` (lesson-9 baseline)
- **Tutorial Standards:** `.claude/skills/tutorial-standards/SKILL.md`
- **TUTORIAL_INDEX Template:** `.claude/skills/tutorial-standards/references/tutorial-index-template.md`
- **Notebook Standards:** `.claude/skills/tutorial-standards/references/notebook-standards.md`
- **Cross-linking Rules:** `.claude/skills/tutorial-standards/references/cross-linking-rules.md`

---

## Version History

- **1.0.0** (2025-11-18): Initial command specification
  - TUTORIAL_INDEX.md structure validation
  - Notebook execution with timeout
  - Cross-link validation
  - Mermaid diagram syntax validation
  - Reading time calculation
  - Comprehensive error handling
