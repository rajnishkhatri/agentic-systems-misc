---
name: tutorial-standards
description: Enforce tutorial quality standards and TUTORIAL_INDEX.md structure for educational content
version: 1.0.0
activation_context:
  - create tutorial
  - TUTORIAL_INDEX
  - add notebook
  - write lesson
  - tutorial structure
  - learning path
references:
  - references/tutorial-index-template.md
  - references/notebook-standards.md
  - references/cross-linking-rules.md
  - examples/lesson-9-tutorial-index.md
  - ../../CLAUDE.md#tutorial-workflow
---

# Tutorial Standards Skill

## Purpose

This skill activates when creating or maintaining educational tutorials to ensure consistent quality, structure, and user experience across all learning materials.

## When This Skill Activates

This skill provides guidance when you:
- Create new tutorials or lessons
- Write or update TUTORIAL_INDEX.md files
- Add Jupyter notebooks to tutorials
- Structure learning paths
- Cross-link between tutorials

## Key Principles

### 1. TUTORIAL_INDEX.md is Required

Every tutorial directory (homework/lesson) must have a `TUTORIAL_INDEX.md` file that serves as the navigation hub. See `references/tutorial-index-template.md` for required sections.

**Gold Standard Example:** `examples/lesson-9-tutorial-index.md`

### 2. Tutorial Quality Standards

- **Reading time:** 15-30 minutes per concept tutorial
- **Execution time:** <5 minutes for notebooks (or provide "Quick Run" option)
- **Visual clarity:** Diagrams should be understandable without reading code
- **Real examples:** Use actual course datasets, not toy data

### 3. Three Tutorial Types

1. **Concept Tutorials (.md)** - Theory and methodology
2. **Interactive Notebooks (.ipynb)** - Hands-on implementation
3. **Visual Diagrams (.mmd/.png)** - Workflow/architecture visualization

See `references/notebook-standards.md` for notebook requirements.

### 4. Cross-Linking

Use **relative paths** for stability. See `references/cross-linking-rules.md` for conventions.

## What This Skill Does

When activated, this skill will:

✅ **Remind** you to create/update TUTORIAL_INDEX.md
✅ **Reference** the tutorial-index-template for required sections
✅ **Guide** notebook structure (setup cell, cost warning, validation)
✅ **Ensure** cross-links use relative paths
✅ **Validate** reading/execution time targets
✅ **Point** to lesson-9 as the gold standard example

## What This Skill Does NOT Do

❌ Duplicate content from CLAUDE.md (references it instead)
❌ Replace validation commands (use `/validate-tutorial` for automated checks)
❌ Override user preferences on tutorial structure

## Integration with Other Tools

- **CLAUDE.md Tutorial Workflow** (CLAUDE.md:347-435): Comprehensive tutorial development process including:
  - Tutorial system overview and navigation structure
  - Recommended learning paths (Foundation → Advanced, Homework-First, Dashboard-First)
  - Tutorial development workflow (5-step process)
  - Tutorial quality standards (reading time, execution time, diagrams, examples)
  - Tutorial types (Concept, Interactive Notebooks, Visual Diagrams)
- **/validate-tutorial command**: Automated quality checks (TUTORIAL_INDEX structure, notebook execution, cross-links, diagrams, reading time)
- **Pattern Library**: Apply TDD pattern when creating tutorial code examples

## Quick Reference

**Creating a new tutorial?**
1. Create TUTORIAL_INDEX.md with all required sections (see template)
2. Write concept tutorials (.md files) with 15-30 min reading time
3. Add interactive notebooks with setup cell, cost warning, <5min execution
4. Create Mermaid diagrams for complex workflows
5. Cross-link using relative paths
6. Use lesson-9 as reference example

**For detailed workflow:** See CLAUDE.md:347-435 (Tutorial Workflow section)
