# Extracted from CLAUDE.md - Context Engineering

2. Review visual diagrams (session_vs_context.svg, memory_vs_rag.svg)
3. Study Bhagavad Gita chatbot case study

**Implementation (2-3 hours):**
1. [Sessions Pattern](patterns/sessions-tutorial.md) ([Quick Ref](patterns/sessions-quickref.md)) - Multi-turn conversations
2. [Memory Pattern](patterns/memory-tutorial.md) ([Quick Ref](patterns/memory-quickref.md)) - Long-term persistence
3. Run tests: `pytest tests/sessions/ tests/memory/ -v --cov`

**Full Mastery (4-6 hours):**
1. Complete implementation path above
2. Study advanced topics (performance optimization, conflict resolution)
3. Analyze case studies (Bhagavad Gita, Banking Fraud, Healthcare Triage)

**Navigation Hub:** [google-context/TUTORIAL_INDEX.md](google-context/TUTORIAL_INDEX.md)

---

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

## Working with GitHub

This project uses GitHub Issues and Project Boards for task management:
- Create issues using `/issue` command with proper templates
- Use `/work` command to execute tasks from the project board
- Link issues to PRs for traceability

## Bhagavad Gita Chatbot Specific Guidelines

### Data Sources
- **Bhagwat-Gita-Infinity**: 737 verse JSON files with multiple scholarly commentaries
- **Bhagavad-Gita-QA**: 3,500 Q&A pairs for evaluation and validation
- **Multilingual Support**: English and Hindi queries and responses

### Agent Architecture
- **Query Classifier**: Categorizes queries (verse lookup vs. thematic vs. philosophical)
- **Retrieval Agent**: Semantic search and exact verse lookup
- **Synthesis Agent**: Combines multiple sources into coherent responses
- **Validator Agent**: Ensures faithfulness to original texts and detects hallucinations

### Quality Requirements
- **Accuracy**: ≥90% correct verse retrieval
- **Faithfulness**: ≥95% responses contain only information from source texts
- **Response Time**: <10 seconds for complex philosophical queries
- **Test Coverage**: ≥90% code coverage
- **Cultural Sensitivity**: Respectful handling of religious and philosophical content

## AI Dev Tasks Integration

When using AI Dev Tasks workflow:
1. Start with `@create-prd.md` for feature planning
2. Generate tasks with `@generate-tasks.md`
3. Execute with `@process-task-list.md` for systematic implementation
4. Use Compound Engineering commands for parallel execution within tasks

Remember: The goal is not just faster coding, but better software that serves real user needs through clear specification and systematic execution. For this project, that means creating a trustworthy, accurate, and culturally sensitive Bhagavad Gita chatbot.
