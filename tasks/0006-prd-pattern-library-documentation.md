# PRD: Reusable Pattern Library for Tutorial System

## Introduction/Overview

This PRD defines a lightweight pattern library to accelerate tutorial development by documenting reusable code patterns discovered in Lessons 12-13. The library will consist of markdown documentation files providing copy-paste ready templates for common patterns (TDD workflow, ThreadPoolExecutor parallel processing, and Abstract Base Classes), targeting both AI assistants and junior developers.

**Problem**: Tutorial implementation requires repeatedly explaining and implementing the same code patterns (TDD cycles, parallel processing, inheritance hierarchies). This leads to:
- Inconsistent implementations across lessons
- Longer development time (AI re-learns patterns)
- Higher cognitive load for junior developers

**Solution**: A `/patterns/` directory with 3-5 markdown documents cataloging battle-tested patterns from Lessons 12-13, each with: when to use, code templates, defensive coding integration, and real examples from the codebase.

## Goals

1. **Reduce Implementation Time**: Junior developers can implement new lessons in 50% less time by referencing pattern templates
2. **Ensure Consistency**: All tutorials follow the same TDD workflow, error handling, and concurrency patterns
3. **Enable Self-Service**: Developers can find and apply patterns without senior dev intervention
4. **AI-Friendly**: Claude Code can reference patterns to generate consistent, defensive code

## User Stories

### Story 1: Junior Developer Implements New Lesson
**As a** junior developer implementing Lesson 14,
**I want to** reference TDD workflow documentation,
**So that** I can write tests following the `test_should_[result]_when_[condition]` convention without asking for code review feedback.

**Acceptance Criteria**:
- Can find TDD pattern in `/patterns/README.md` index within 1 minute
- Pattern doc explains RED→GREEN→REFACTOR cycle with code example
- Can copy defensive function template and adapt to my use case in 5 minutes

### Story 2: AI Assistant Generates Consistent Code
**As an** AI assistant (Claude Code) working on a new tutorial,
**I want to** reference established patterns from `/patterns/` directory,
**So that** I generate code matching the project's quality standards (type hints, input validation, test naming) without human correction.

**Acceptance Criteria**:
- Pattern docs are in markdown (easily parseable by AI)
- Each pattern includes "When to Use" section for context selection
- Code examples are complete and executable (not pseudocode)

### Story 3: Developer Optimizes Batch Processing
**As a** developer optimizing batch evaluation in Lesson 15,
**I want to** reference ThreadPoolExecutor pattern with `future_to_index` mapping,
**So that** I can parallelize 500 test cases while preserving result order and handling exceptions gracefully.

**Acceptance Criteria**:
- Pattern doc shows exact code from `query_rewrite_agent.py:187-208`
- Includes exception handling and progress bar integration (tqdm)
- Explains trade-offs (max_workers selection, memory usage)

### Story 4: Tech Lead Onboards New Team Member
**As a** tech lead onboarding a new developer,
**I want to** point them to `/patterns/README.md` as required reading,
**So that** they understand project conventions before their first commit.

**Acceptance Criteria**:
- README.md has quick reference table (pattern → use case → complexity)
- Takes 10 minutes to read through all patterns
- New dev's first PR follows conventions without code review comments

## Functional Requirements

### FR-1: Pattern Library Directory Structure
The system **must** create `/patterns/` directory containing:
- `README.md` - Master catalog with pattern index table
- `tdd-workflow.md` - Test-Driven Development pattern
- `threadpool-parallel.md` - Concurrent execution pattern
- `abstract-base-class.md` - Inheritance pattern
- (Optional) 1-2 bonus pattern docs (e.g., defensive function template, notebook structure)

### FR-2: TDD Workflow Pattern Documentation
The `tdd-workflow.md` **must** include:
- RED→GREEN→REFACTOR cycle explanation (3 steps with examples)
- Test naming convention: `test_should_[result]_when_[condition]()`
- Integration with defensive coding 5-step template
- Code example from `tests/test_rag_generation_eval.py:1-40`
- "When to Use" section: All new features, refactoring existing code
- Common pitfalls: Writing implementation before test, testing too much at once

### FR-3: ThreadPoolExecutor Parallel Pattern Documentation
The `threadpool-parallel.md` **must** include:
- `future_to_index` mapping for order preservation
- Exception handling in thread workers
- Progress bar integration with tqdm
- Code example from `backend/query_rewrite_agent.py:187-208`
- "When to Use" section: Batch processing, independent I/O operations
- Trade-offs: max_workers selection, memory usage, GIL limitations

### FR-4: Abstract Base Class Pattern Documentation
The `abstract-base-class.md` **must** include:
- Python `abc` module usage with `@abstractmethod` decorator
- Base class design with defensive initialization
- Concrete implementation template
- Code example from `backend/ai_judge_framework.py:64-100` (BaseJudge class)
- "When to Use" section: Multiple implementations sharing interface (e.g., BaseJudge → BinaryJudge, LikertJudge)
- Common pitfalls: Forgetting `ABC` inheritance, missing abstractmethod decorator

### FR-5: Master Catalog (README.md)
The `patterns/README.md` **must** include:
- Quick reference table with columns: Pattern Name, Complexity (1-3 stars), Use Case, Source File
- "How to Use This Library" section explaining navigation
- Cross-links to each pattern document
- Contribution guidelines for adding new patterns

### FR-6: Code Examples Quality Standards
All code examples **must**:
- Be executable (copy-paste ready, no pseudocode)
- Include type hints and defensive coding (input validation)
- Show both correct usage and common mistakes
- Reference actual files in the codebase with line numbers

### FR-7: Versioning and Maintenance
The pattern library **must**:
- Include creation date in each pattern doc
- Note source lesson/homework (e.g., "Extracted from Lesson 13")
- Link back to original implementation file with line numbers
- Update `CLAUDE.md` with reference to `/patterns/` directory

## Non-Goals (Out of Scope)

1. **No Code Generation Tools**: This is documentation only, not a code generator or CLI tool
2. **No Refactoring Existing Code**: Will not refactor Lessons 1-13 to use patterns (only document existing patterns)
3. **No Comprehensive Coverage**: Will only document 3-5 most critical patterns, not all patterns in codebase
4. **No Interactive Tutorials**: Pattern docs are reference material, not step-by-step tutorials with exercises
5. **No Framework/Library**: Not building a Python package or reusable library, just markdown docs

## Design Considerations

### Directory Structure
```
patterns/
├── README.md                    # Master catalog (300-400 lines)
├── tdd-workflow.md             # TDD pattern (400-500 lines)
├── threadpool-parallel.md      # Concurrency pattern (350-450 lines)
└── abstract-base-class.md      # OOP pattern (350-450 lines)
```

### Markdown Template Structure (Each Pattern Doc)
```markdown
# [Pattern Name]

## Overview
Brief description (2-3 sentences)

## When to Use
- Use case 1
- Use case 2
- Use case 3

## When NOT to Use
- Anti-pattern 1
- Anti-pattern 2

## Code Template
```python
# Minimal copy-paste template
```

## Real Example from Codebase
```python
# Actual code with file:line reference
```

## Integration with Defensive Coding
How this pattern follows the 5-step defensive function template

## Common Pitfalls
- Pitfall 1 with example
- Pitfall 2 with example

## Related Patterns
Links to other patterns in library

## Source
- Lesson/Homework: Lesson 13
- Original File: backend/rag_generation_eval.py:45-78
- Created: 2025-11-11
```

## Technical Considerations

1. **No Dependencies**: Pattern library requires no additional Python packages
2. **GitHub Rendering**: All markdown must render correctly on GitHub (use fenced code blocks, no custom extensions)
3. **IDE Integration**: Developers can search patterns with Ctrl+F in IDE
4. **AI Parsing**: Markdown structure must be consistent for Claude Code to parse
5. **Future Extensibility**: README.md index table allows adding patterns without restructuring

## Success Metrics

1. **Adoption Rate**: ≥80% of Lesson 14-20 implementations reference pattern library
2. **Comprehension**: New team member can explain TDD workflow after 10-minute reading
3. **Code Quality**: ≥50% reduction in code review comments about test naming, error handling, and concurrency
4. **Development Speed**: Junior dev implements new lesson 30-50% faster with pattern reference

## Timeline

**Minimal Scope: 2-3 hours**

**Hour 1: Setup & First Pattern**
- Create `/patterns/` directory structure
- Write `README.md` catalog with index table
- Document **TDD Workflow Pattern** (FR-2) - most critical, frequently used

**Hour 2: Concurrency & OOP Patterns**
- Document **ThreadPoolExecutor Pattern** (FR-3) - high complexity, battle-tested in query_rewrite_agent
- Document **Abstract Base Class Pattern** (FR-4) - foundational for judge framework

**Hour 3 (Optional): Polish & Bonus**
- Add defensive function template pattern (bonus)
- Add notebook structure pattern (bonus)
- Cross-link patterns in README
- Update `CLAUDE.md` with pattern library reference

## Open Questions

### Q1: Should pattern docs include anti-patterns section?
**Answer**: YES (1A) - Include "Common Pitfalls" sections in FR-2, FR-3, FR-4

### Q2: How to handle pattern evolution when codebase changes?
**Answer**: YES (2A) - Each pattern doc includes "Source" section with file:line reference and creation date for tracking

### Q3: Should we version pattern docs (v1.0, v2.0)?
**Answer**: NO (3) - Creation date sufficient for now, revisit if patterns diverge significantly

### Q4: Should patterns include video walkthroughs or diagrams?
**Answer**: NO (4) - Code examples sufficient, can add Mermaid diagrams in future iterations

---

**Deliverables:**
- `/tasks/0006-prd-pattern-library-documentation.md` (this file)
- Next: Use `@.claude/generate-tasks.md` to create task list
- Implementation target: 2-3 hours for core patterns

**Version**: 1.0
**Created**: 2025-11-11
**Status**: APPROVED - Ready for task generation
