# Tutorial Cross-Linking Rules

**Version:** 1.0
**Last Updated:** 2025-11-18

---

## Overview

This document defines the **relative path conventions** for tutorial cross-linking in the LLM Evals Tutorial System. Proper cross-linking ensures students can navigate between related topics and tutorials remain maintainable when directories are moved or renamed.

**Core Principle:** Always use **relative paths** for internal links, never absolute paths.

**Reference:** CLAUDE.md:418 (Maintenance: Use relative paths for stability)

---

## Relative Path Conventions

### 1. Same Directory Links

**Rule:** When linking to files in the **same directory**, use `./` prefix or no prefix.

**Examples:**

```markdown
<!-- TUTORIAL_INDEX.md linking to tutorial in same directory -->
- [Evaluation Fundamentals](./evaluation_fundamentals.md)
- [Language Modeling Metrics](language_modeling_metrics.md)

<!-- TUTORIAL_INDEX.md linking to notebook in same directory -->
- [Perplexity Calculation](./perplexity_calculation_tutorial.ipynb)
- [Similarity Measurements](similarity_measurements_tutorial.ipynb)
```

**Best Practice:** Use `./` prefix for clarity, but both forms are acceptable.

---

### 2. Parent Directory Links

**Rule:** When linking to files in the **parent directory**, use `../` prefix.

**Examples:**

```markdown
<!-- lesson-9/TUTORIAL_INDEX.md linking to homeworks/ -->
- [HW1: Prompt Engineering](../homeworks/hw1/TUTORIAL_INDEX.md)
- [HW2: Error Analysis](../homeworks/hw2/TUTORIAL_INDEX.md)
```

**Pattern from lesson-9/TUTORIAL_INDEX.md:10-11:**
```markdown
**Prerequisites:**
- [HW1: Prompt Engineering](../homeworks/hw1/TUTORIAL_INDEX.md)
- [HW2: Error Analysis](../homeworks/hw2/TUTORIAL_INDEX.md)
```

---

### 3. Sibling Directory Links

**Rule:** When linking to files in a **sibling directory** (same level), use `../sibling-dir/` pattern.

**Examples:**

```markdown
<!-- lesson-10/TUTORIAL_INDEX.md linking to lesson-9/ -->
- [Lesson 9: Evaluation Fundamentals](../lesson-9/TUTORIAL_INDEX.md)

<!-- lesson-10/TUTORIAL_INDEX.md linking to homeworks/hw3/ -->
- [HW3: LLM-as-Judge](../homeworks/hw3/TUTORIAL_INDEX.md)
```

**Pattern from lesson-10/TUTORIAL_INDEX.md:10-11:**
```markdown
**Prerequisites:**
- [HW3: LLM-as-Judge](../homeworks/hw3/TUTORIAL_INDEX.md)
- [Lesson 9: Evaluation Fundamentals](../lesson-9/TUTORIAL_INDEX.md)
```

---

### 4. Cross-Lesson Resources Links

**Rule:** When linking to **shared resources** across lessons, use full relative path from current location.

**Examples:**

```markdown
<!-- lesson-9/TUTORIAL_INDEX.md linking to lesson-9-11/ shared resources -->
- [Evaluation Dashboard](../lesson-9-11/README.md)
- [Tutorial Changelog](../TUTORIAL_CHANGELOG.md)
```

**Pattern from lesson-10/TUTORIAL_INDEX.md:301:**
```markdown
👉 [Lesson 11 Tutorial Index](../lesson-11/TUTORIAL_INDEX.md)
```

---

### 5. README Links within Lessons

**Rule:** When linking to local README.md from TUTORIAL_INDEX.md, use relative path.

**Examples:**

```markdown
<!-- TUTORIAL_INDEX.md linking to README.md in same directory -->
- [`README.md`](README.md) - Lesson setup and overview
```

**Pattern from lesson-10/TUTORIAL_INDEX.md:270:**
```markdown
- [`README.md`](README.md) - Lesson setup and overview
```

---

## Link Patterns by Context

### Prerequisites Section

**Location:** TUTORIAL_INDEX.md, near the top
**Purpose:** Help students understand what to complete before starting

**Pattern:**
```markdown
**Prerequisites:**
- [HW1: Topic Name](../homeworks/hw1/TUTORIAL_INDEX.md) - Brief description
- [Lesson X: Topic Name](../lesson-X/TUTORIAL_INDEX.md) - Brief description
- Basic knowledge of [concept]
```

**Real Example (lesson-9/TUTORIAL_INDEX.md:10-12):**
```markdown
**Prerequisites:**
- [HW1: Prompt Engineering](../homeworks/hw1/TUTORIAL_INDEX.md) - Understanding of LLM behavior
- [HW2: Error Analysis](../homeworks/hw2/TUTORIAL_INDEX.md) - Systematic failure detection
- Basic understanding of probability and information theory
```

---

### Tutorials Section

**Location:** TUTORIAL_INDEX.md, main content area
**Purpose:** Link to concept tutorials and notebooks in the same directory

**Pattern:**
```markdown
### 1. Tutorial Title
**File:** `tutorial_name.md` or [`tutorial_name.ipynb`](tutorial_name.ipynb)
**Reading Time:** X-Y minutes
**Topics:**
- Topic 1
- Topic 2

**When to use:** Description of when to read/run this tutorial.
```

**Real Example (lesson-10/TUTORIAL_INDEX.md:47-50):**
```markdown
### 1. Judge Prompt Engineering Tutorial (Interactive Notebook)
**File:** [`judge_prompt_engineering_tutorial.ipynb`](judge_prompt_engineering_tutorial.ipynb)
**Execution Time:** 15-20 minutes
**Cost:** $0.50-1.00 (DEMO mode), $2.50-4.00 (FULL mode)
```

---

### Related Resources Section

**Location:** TUTORIAL_INDEX.md, near the end
**Purpose:** Connect students to previous/next lessons and related homeworks

**Pattern:**
```markdown
## Related Resources

### Previous Content
- [Lesson X: Topic](../lesson-X/TUTORIAL_INDEX.md) - What was covered
- [HWY: Topic](../homeworks/hwY/TUTORIAL_INDEX.md) - Related assignment

### Next Steps
- [Lesson Z: Topic](../lesson-Z/TUTORIAL_INDEX.md) - What comes next
```

**Real Example (lesson-10/TUTORIAL_INDEX.md:280-281, 301):**
```markdown
- [HW3: LLM-as-Judge](../homeworks/hw3/TUTORIAL_INDEX.md) - Dietary adherence judge development
- [Lesson 4: Substantiation Evaluation](../lesson-4/TUTORIAL_INDEX.md) - Judge for unsupported claims

...

👉 [Lesson 11 Tutorial Index](../lesson-11/TUTORIAL_INDEX.md)
```

---

## Anti-Patterns (DO NOT USE)

### ❌ Absolute Paths
```markdown
<!-- WRONG: Breaks when repository is cloned to different location -->
[HW1](/Users/username/Documents/recipe-chatbot/homeworks/hw1/TUTORIAL_INDEX.md)
[Lesson 9](/home/user/project/lesson-9/TUTORIAL_INDEX.md)
```

**Why wrong:** Absolute paths only work on the author's machine and break for all other users.

---

### ❌ GitHub URLs
```markdown
<!-- WRONG: Breaks for offline viewing and private repositories -->
[HW1](https://github.com/username/repo/blob/main/homeworks/hw1/TUTORIAL_INDEX.md)
```

**Why wrong:** GitHub URLs require internet connection and don't work in cloned repositories or when viewing locally.

---

### ❌ Root-Relative Paths
```markdown
<!-- WRONG: May break depending on how markdown is rendered -->
[HW1](/homeworks/hw1/TUTORIAL_INDEX.md)
```

**Why wrong:** Root-relative paths (starting with `/`) may be interpreted differently by different markdown renderers.

---

### ❌ Inconsistent Path Separators
```markdown
<!-- WRONG: Backslashes don't work on Unix/macOS -->
[HW1](..\homeworks\hw1\TUTORIAL_INDEX.md)
```

**Why wrong:** Always use forward slashes `/` for cross-platform compatibility, even on Windows.

---

## Path Calculation Reference

Use this table to calculate relative paths between common locations:

| From Location | To Location | Relative Path |
|--------------|-------------|---------------|
| `lesson-9/TUTORIAL_INDEX.md` | `lesson-9/evaluation_fundamentals.md` | `./evaluation_fundamentals.md` |
| `lesson-9/TUTORIAL_INDEX.md` | `lesson-10/TUTORIAL_INDEX.md` | `../lesson-10/TUTORIAL_INDEX.md` |
| `lesson-9/TUTORIAL_INDEX.md` | `homeworks/hw1/TUTORIAL_INDEX.md` | `../homeworks/hw1/TUTORIAL_INDEX.md` |
| `lesson-10/TUTORIAL_INDEX.md` | `lesson-9/TUTORIAL_INDEX.md` | `../lesson-9/TUTORIAL_INDEX.md` |
| `lesson-10/TUTORIAL_INDEX.md` | `lesson-11/TUTORIAL_INDEX.md` | `../lesson-11/TUTORIAL_INDEX.md` |
| `homeworks/hw3/TUTORIAL_INDEX.md` | `lesson-10/TUTORIAL_INDEX.md` | `../../lesson-10/TUTORIAL_INDEX.md` |
| `lesson-9/TUTORIAL_INDEX.md` | `lesson-9-11/README.md` | `../lesson-9-11/README.md` |
| `lesson-14/TUTORIAL_INDEX.md` | `lesson-14/section-a-foundation/tutorials/01_tutorial.md` | `./section-a-foundation/tutorials/01_tutorial.md` |

---

## Validation

### Manual Validation

To verify links work correctly:

1. **Clone repository to a different location** on your machine
2. **Open TUTORIAL_INDEX.md** in VS Code or GitHub preview
3. **Click all links** and verify they resolve correctly
4. **Test on different platforms** (macOS, Linux, Windows)

### Automated Validation

Use markdown link checker tools:

```bash
# Install markdown-link-check
npm install -g markdown-link-check

# Check a specific file
markdown-link-check lesson-9/TUTORIAL_INDEX.md

# Check all TUTORIAL_INDEX.md files
find . -name "TUTORIAL_INDEX.md" -exec markdown-link-check {} \;
```

---

## Special Cases

### Linking to Files in Subdirectories

**Scenario:** `lesson-14/TUTORIAL_INDEX.md` linking to `lesson-14/section-a-foundation/tutorials/01_agent_planning_evaluation.md`

**Pattern:**
```markdown
- [Agent Planning Evaluation](./section-a-foundation/tutorials/01_agent_planning_evaluation.md)
```

**Key:** Use `./subdirectory/file.md` pattern for clarity.

---

### Linking Between Subdirectories

**Scenario:** `lesson-14/section-a-foundation/TUTORIAL_INDEX.md` linking to `lesson-14/section-b-multi-agent/TUTORIAL_INDEX.md`

**Pattern:**
```markdown
- [Multi-Agent Systems](../section-b-multi-agent/TUTORIAL_INDEX.md)
```

**Key:** Go up to parent (`..`), then into sibling directory.

---

### Linking from Subdirectory to Root

**Scenario:** `lesson-14/section-a-foundation/tutorials/01_tutorial.md` linking to `lesson-9/TUTORIAL_INDEX.md`

**Pattern:**
```markdown
- [Lesson 9: Evaluation Fundamentals](../../../lesson-9/TUTORIAL_INDEX.md)
```

**Key:** Count directory levels up: `tutorials/` → `section-a-foundation/` → `lesson-14/` → root (3 levels = `../../../`)

---

## Checklist for Tutorial Cross-Links

Use this checklist when creating or reviewing tutorials:

- [ ] All links use **relative paths**, not absolute paths
- [ ] All links use **forward slashes** `/`, not backslashes `\`
- [ ] Prerequisites section links to **TUTORIAL_INDEX.md** files, not README.md
- [ ] Tutorial section links to **files in same directory** use `./` prefix
- [ ] Links to **sibling lessons/homeworks** use `../sibling-dir/` pattern
- [ ] All links **tested by clicking** in markdown preview
- [ ] No links to **external GitHub URLs** for internal files
- [ ] Path separators are **consistent** throughout the file

---

## Real-World Examples

### Example 1: lesson-9/TUTORIAL_INDEX.md
**Line 10-11:**
```markdown
**Prerequisites:**
- [HW1: Prompt Engineering](../homeworks/hw1/TUTORIAL_INDEX.md) - Understanding of LLM behavior
- [HW2: Error Analysis](../homeworks/hw2/TUTORIAL_INDEX.md) - Systematic failure detection
```

**Analysis:**
- ✅ Uses relative paths (`../homeworks/hw1/`)
- ✅ Links to TUTORIAL_INDEX.md (navigation hub)
- ✅ Includes descriptive text after link

---

### Example 2: lesson-10/TUTORIAL_INDEX.md
**Line 47:**
```markdown
**File:** [`judge_prompt_engineering_tutorial.ipynb`](judge_prompt_engineering_tutorial.ipynb)
```

**Analysis:**
- ✅ Links to file in same directory (no `./` prefix, but acceptable)
- ✅ Uses inline code formatting for filename
- ✅ Links directly to .ipynb file

---

### Example 3: lesson-10/TUTORIAL_INDEX.md
**Line 301:**
```markdown
👉 [Lesson 11 Tutorial Index](../lesson-11/TUTORIAL_INDEX.md)
```

**Analysis:**
- ✅ Links to sibling directory using `../lesson-11/`
- ✅ Clear call-to-action emoji
- ✅ Links to TUTORIAL_INDEX.md for next lesson

---

## Summary

**Golden Rules:**
1. **Always use relative paths** for maintainability
2. **Link to TUTORIAL_INDEX.md** for lesson/homework navigation (not README.md)
3. **Link to actual files** (.md, .ipynb) for tutorials in same directory
4. **Test all links** by clicking in markdown preview
5. **Use forward slashes** `/` for cross-platform compatibility

**Reference Documentation:**
- CLAUDE.md:359 - Tutorial Navigation
- CLAUDE.md:405-409 - Tutorial Development Workflow (cross-linking step)
- CLAUDE.md:418 - Maintenance (relative paths for stability)

---

**Document Status:** ✅ Active
**Skill Reference:** `.claude/skills/tutorial-standards/SKILL.md`
