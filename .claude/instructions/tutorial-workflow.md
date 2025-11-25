# Extracted from CLAUDE.md - Tutorial Workflow

## Tutorial Workflow

### Using the Tutorial System

This project includes comprehensive tutorials for systematic AI evaluation learning. Each homework and lesson has a `TUTORIAL_INDEX.md` file with:

- **Learning objectives** and prerequisites
- **Recommended learning paths** with step-by-step guidance
- **Links to concept tutorials**, interactive notebooks, and visual diagrams
- **Common pitfalls** and troubleshooting
- **FAQs** and real-world applications

### Tutorial Navigation

**Homework Tutorials:**
- [HW1: Prompt Engineering](homeworks/hw1/TUTORIAL_INDEX.md)
- [HW2: Error Analysis](homeworks/hw2/TUTORIAL_INDEX.md)
- [HW3: LLM-as-Judge](homeworks/hw3/TUTORIAL_INDEX.md)
- [HW4: RAG Evaluation](homeworks/hw4/TUTORIAL_INDEX.md)
- [HW5: Agent Failure Analysis](homeworks/hw5/TUTORIAL_INDEX.md)

**Lesson Tutorials:**
- [Lesson 4: Substantiation Evaluation](lesson-4/TUTORIAL_INDEX.md)
- [Lesson 7: Trace Inspection](lesson-7/TUTORIAL_INDEX.md)
- [Lesson 8: Model Cascades](lesson-8/TUTORIAL_INDEX.md)
- [Lesson 9: Evaluation Fundamentals & Exact Methods](lesson-9/TUTORIAL_INDEX.md)
- [Lesson 10: AI-as-Judge Mastery & Production Patterns](lesson-10/TUTORIAL_INDEX.md)
- [Lesson 11: Comparative Evaluation & Leaderboards](lesson-11/TUTORIAL_INDEX.md)

**Cross-Lesson Resources:**
- [Evaluation Dashboard (Lessons 9-11)](lesson-9-11/README.md) - Unified metrics visualization
- [Tutorial Changelog](TUTORIAL_CHANGELOG.md) - Track tutorial updates after code changes

### Recommended Learning Paths

**Path 1: Foundation → Advanced Evaluation (Lessons 9→10→11)**
1. Complete Lesson 9 (Evaluation Fundamentals & Exact Methods) - ~3-4 hours
2. Complete Lesson 10 (AI-as-Judge Mastery) - ~4-5 hours
3. Complete Lesson 11 (Comparative Evaluation) - ~3-4 hours
4. Launch Evaluation Dashboard: `python lesson-9-11/evaluation_dashboard.py`

**Path 2: Homework-First Approach**
1. Complete HW1-2 (Prompt Engineering, Error Analysis)
2. Complete HW3 (LLM-as-Judge) → Then study Lesson 10 for deeper understanding
3. Complete HW4 (RAG Evaluation) → Then study Lesson 9 for metric selection
4. Complete HW5 (Agent Failure Analysis)
5. Complete Lessons 9-11 for comprehensive evaluation methodology

**Path 3: Quick Start (Dashboard-First)**
1. Launch dashboard: `python lesson-9-11/evaluation_dashboard.py`
2. Explore sample metrics from HW3, HW4, Lessons 9-11
3. Read TUTORIAL_INDEX.md for each lesson to understand metrics
4. Deep dive into specific tutorials as needed

### Tutorial Development Workflow

When creating or updating tutorials:

1. **Start with TUTORIAL_INDEX.md** - Navigation hub for all tutorials in a directory
2. **Write concept tutorials (.md)** - Theory and methodology explanations
3. **Create interactive notebooks (.ipynb)** - Hands-on exercises with live code
4. **Design visual diagrams (.mmd)** - Mermaid diagrams for workflow/architecture visualization
5. **Cross-link tutorials** - Ensure students can navigate between related topics
6. **Update TUTORIAL_CHANGELOG.md** - Track when tutorials need updates after code changes

### Tutorial Quality Standards

- **Reading time:** 15-30 minutes per tutorial
- **Execution time:** <5 minutes for notebooks (or provide "Quick Run" option)
- **Diagrams:** Understandable without reading code
- **Examples:** Use real course datasets, not toy data
- **Maintenance:** Use relative paths for stability

### Tutorial Types

1. **Concept Tutorials (.md)**
   - Explain theory and methodology
   - Target: 15-25 minute reading time
   - Include practical exercises at the end

2. **Interactive Notebooks (.ipynb)**
   - Hands-on implementation with live code
   - Include setup cells, cost warnings, validation assertions
   - Target: Execute in <5 minutes

3. **Visual Diagrams (.mmd / .png)**
   - Mermaid syntax for GitHub rendering
   - Export to PNG for complex diagrams (>10 nodes)
   - Show workflow, architecture, or decision trees

