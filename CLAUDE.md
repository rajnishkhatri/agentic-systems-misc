# Claude Code Instructions for LLM Evals tutorial

This project combines the **AI Dev Tasks** workflow with **Compound Engineering** principles for building an intelligent LLM evaluation tutorial.

## Project Philosophy

"Stop thinking in terms of files and functions. Start thinking about outcomes and delegation."

We use a structured approach:
1. **AI Dev Tasks**: PRD → Task List → Implementation with checkpoints
2. **Compound Engineering**: Orchestrate AI agents for parallel execution
3. **TDD First**: Write tests before implementation
4. **Quality Gates**: Ruff, pytest, and clear documentation

## Available Workflows

### AI Dev Tasks Workflow
- Use `@create-prd.md` to generate Product Requirement Documents
- Use `@generate-tasks.md` to break PRDs into actionable tasks
- Use `@process-task-list.md` to execute tasks with approval checkpoints

### Compound Engineering Commands
- `/explore` - Analyze and understand codebases
- `/issue` - Create GitHub issues with proper templates
- `/work` - Execute tasks from GitHub project board
- `/review` - Code review and quality checks
- `/test` - Run comprehensive test suites
- `/docs` - Generate and update documentation
- `/reflect` - Post-implementation analysis

### Project Maintenance Commands
- `/compress-claude` - Optimize CLAUDE.md by extracting verbose sections to modular files with `@` imports
  - `analyze` - Scan for compression opportunities (sections >100 lines)
  - `extract [section]` - Move content to `.claude/instructions/` with summary + import
  - `validate` - Test all imports resolve correctly
  - `revert [section]` - Undo extraction and restore original content

## Development Principles

**TDD & Defensive Coding:** @.claude/instructions/tdd-principles.md

**Quick Reference:**
1. **TDD Always:** Follow RED → GREEN → REFACTOR cycle
2. **Defensive Function Template:** Type checking → Input validation → Edge cases → Main logic → Return
3. **Test Naming:** `test_should_[expected_result]_when_[condition]()`

**For full TDD & defensive coding details:** @.claude/instructions/tdd-principles.md

**Additional Development Principles:**
1. **Parallel Execution**: Use Claude's Task tool for independent operations
2. **Clear Specifications**: Document requirements thoroughly before coding
3. **Quality First**: Ruff formatting, type hints, comprehensive tests
4. **User-Centric**: Focus on outcomes that matter to users
5. **Pattern Library**: Use documented patterns from `/patterns/` directory for consistent, maintainable code

## Project Structure

```
├── .claude/commands/     # Custom slash commands
├── src/                 # Source code (Bhagavad Gita chatbot)
├── tests/               # Test suite
├── tasks/               # AI Dev Tasks (PRDs and task lists)
├── patterns/            # Reusable code patterns documentation
│   ├── README.md               # Pattern library catalog
│   ├── tdd-workflow.md         # TDD pattern (RED→GREEN→REFACTOR)
│   ├── threadpool-parallel.md  # ThreadPoolExecutor concurrency pattern
│   └── abstract-base-class.md  # Abstract Base Class OOP pattern
├── analysis/            # Design docs and decisions
├── Gita/                # Bhagavad Gita datasets
│   ├── Bhagwat-Gita-Infinity/  # 737 verse JSON files with commentaries
│   └── Bhagavad-Gita-QA/       # 3,500 Q&A pairs for evaluation
├── data/                # Vector database storage
├── logs/                # Application logs
├── outputs/             # Generated outputs
├── create-prd.md        # AI Dev Tasks: PRD creation
├── generate-tasks.md    # AI Dev Tasks: Task generation
├── process-task-list.md # AI Dev Tasks: Task execution
├── env.example          # Environment configuration template
└── pyproject.toml       # Project configuration with all dependencies
```

## Pattern Library

This project includes a comprehensive **Pattern Library** documenting reusable code patterns for building robust, maintainable AI evaluation systems.

### Available Patterns

**Location:** `/patterns/` directory

**Quick Reference:**

| Pattern | Complexity | Use Case |
|---------|-----------|----------|
| [TDD Workflow](patterns/tdd-workflow.md) | ⭐⭐ | Testing & development methodology (RED→GREEN→REFACTOR) |
| [ThreadPoolExecutor Parallel](patterns/threadpool-parallel.md) | ⭐⭐⭐ | Concurrent batch processing for I/O-bound tasks |
| [Abstract Base Class](patterns/abstract-base-class.md) | ⭐⭐⭐ | OOP interface enforcement & polymorphism |

**When to use patterns:**

1. **TDD Workflow** - When building new features, refactoring code, or fixing bugs
   - Write tests BEFORE implementation
   - Follow RED (failing test) → GREEN (minimal code) → REFACTOR (improve quality)
   - Use test naming convention: `test_should_[result]_when_[condition]()`

2. **ThreadPoolExecutor Parallel** - When batch processing I/O-bound tasks
   - Processing multiple API calls, database queries, or file operations in parallel
   - Use `future_to_index` mapping to preserve result order
   - Include exception handling with fallbacks and `tqdm` progress tracking

3. **Abstract Base Class** - When creating frameworks with multiple implementations
   - Define common interface with `ABC` and `@abstractmethod`
   - Share functionality (retry logic, validation) in base class
   - Enforce contract: subclasses must call `super().__init__()` and implement abstract methods

**For AI Assistants (Claude Code):**

When generating code, check if a pattern applies and use the template from the pattern documentation. All patterns include:
- Copy-paste code templates with defensive coding
- Real examples from codebase with file:line references
- Common pitfalls and how to avoid them
- Integration with defensive coding principles

**See:** [Pattern Library README](patterns/README.md) for full documentation and contribution guidelines.

---

## Quality Standards

- **Line Length**: 120 characters (Ruff configuration)
- **Type Hints**: Required for all functions
- **Async/Await**: Preferred for I/O operations
- **Test Coverage**: Aim for 90%+ coverage
- **Documentation**: Keep CLAUDE.md updated with project patterns
- **Code Patterns**: Follow documented patterns from `/patterns/` directory

---

## Context Engineering Principles

**Full Documentation:** @.claude/instructions/context-engineering.md

**Core Thesis:** Intelligence emerges from orchestration, not just bigger models.

**Quick Reference:**
1. **Session History vs. Context Window:** Full conversation log (50K) vs. curated subset (8K)
2. **Memory vs. RAG:** User-specific facts vs. general knowledge retrieval
3. **Protected Context:** Turn 0, constraints, auth checkpoints must survive compression
4. **Memory Provenance:** Track source_session_id, confidence_score, validation_status
5. **PII Redaction:** Redact identifiers, preserve domain-specific terms (whitelist)

**Implementation Checklist:**
- [ ] Sessions pattern: Compress at 95% threshold, protect turn 0
- [ ] Memory provenance: Full lineage tracking with confidence evolution
- [ ] PII redaction: Email, phone, names → preserve Gita characters
- [ ] Token efficiency: Target 6x reduction (50K → 8K)
- [ ] Test coverage: ≥90% for sessions and memory modules

**For full context engineering details:** @.claude/instructions/context-engineering.md

## Tutorial Workflow

**Full Documentation:** @.claude/instructions/tutorial-workflow.md

**Quick Reference:**
Each homework/lesson has `TUTORIAL_INDEX.md` with learning objectives, recommended paths, and troubleshooting.

**Available Tutorials:**
- Homeworks: HW1-5 (Prompt Engineering → Agent Failure Analysis)
- Lessons: 4, 7-11 (Substantiation → Comparative Evaluation)
- Dashboard: `python lesson-9-11/evaluation_dashboard.py`

**Tutorial Quality Standards:**
- Reading time: 15-30 min per tutorial
- Execution time: <5 min for notebooks
- Real course datasets, not toy data

**For full tutorial workflow and development guidelines:** @.claude/instructions/tutorial-workflow.md

