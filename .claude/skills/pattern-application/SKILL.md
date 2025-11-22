---
name: Pattern Application
description: Guides application of documented code patterns from pattern library for consistent, maintainable implementations
version: 1.0.0
activation_context:
  - parallel processing
  - batch
  - concurrent
  - abstract base class
  - interface
  - framework
  - pattern
  - threadpool
  - ABC
  - polymorphism
  - concurrent.futures
references:
  - patterns/README.md
  - patterns/tdd-workflow.md
  - patterns/threadpool-parallel.md
  - patterns/abstract-base-class.md
  - .claude/skills/pattern-application/references/pattern-decision-tree.md
  - .claude/skills/pattern-application/references/integration-checklist.md
---

# Pattern Application Skill

## Purpose

This skill activates when you mention pattern-related keywords to guide you in applying documented code patterns from the project's pattern library (`/patterns/`). It ensures consistent, maintainable implementations using proven templates with defensive coding.

## When This Skill Activates

This skill automatically activates when you use keywords like:
- **Concurrency**: "parallel processing", "batch", "concurrent", "threadpool"
- **OOP Design**: "abstract base class", "interface", "framework", "ABC", "polymorphism"
- **General**: "pattern", "apply pattern", "use pattern"

## What This Skill Provides

### 1. Pattern Discovery
When you describe a problem, this skill helps identify which pattern(s) apply:
- **TDD Workflow** - For test-driven development
- **ThreadPoolExecutor Parallel** - For concurrent I/O-bound batch processing
- **Abstract Base Class** - For OOP interfaces with multiple implementations

### 2. Pattern Selection Guidance
See `references/pattern-decision-tree.md` for detailed decision logic:
- I/O-bound batch tasks? → **ThreadPoolExecutor Parallel**
- Multiple implementations of same interface? → **Abstract Base Class**
- Building new feature or fixing bug? → **TDD Workflow**

### 3. Integration Checklist
See `references/integration-checklist.md` for step-by-step application:
1. Identify pattern from decision tree
2. Read full pattern documentation
3. Copy template from pattern file
4. Apply defensive coding (type hints, validation, error handling)
5. Add pattern reference comment in code
6. Test using TDD workflow

## Pattern Library Quick Reference

| Pattern | Complexity | Use When |
|---------|-----------|----------|
| TDD Workflow | ⭐⭐ | Testing, new features, refactoring |
| ThreadPoolExecutor Parallel | ⭐⭐⭐ | I/O-bound batch processing with order preservation |
| Abstract Base Class | ⭐⭐⭐ | Multiple implementations sharing common interface |

**Detailed documentation:** `patterns/README.md`

## Integration with Other Skills

- **TDD Methodology Skill**: Enforces test-first workflow for pattern implementations
- **Tutorial Standards Skill**: Pattern examples in notebooks follow tutorial quality standards

## Common Scenarios

### Scenario 1: Batch API Processing
**You say:** "I need to call an API for 100 queries in parallel"

**This skill provides:**
1. Suggests **ThreadPoolExecutor Parallel** pattern
2. References `patterns/threadpool-parallel.md`
3. Highlights key concepts:
   - `future_to_index` mapping for order preservation
   - Exception handling with fallbacks
   - `tqdm` progress tracking
   - `max_workers` tuning (5-20 for I/O tasks)
4. Provides copy-paste template with defensive coding

### Scenario 2: Building Evaluation Framework
**You say:** "I need to create multiple judge implementations with a common interface"

**This skill provides:**
1. Suggests **Abstract Base Class** pattern
2. References `patterns/abstract-base-class.md`
3. Highlights key concepts:
   - `ABC` inheritance and `@abstractmethod` decorator
   - Defensive validation in base `__init__`
   - Shared functionality (retry logic, helpers)
   - Subclass contract (`super().__init__()` requirement)
4. Provides copy-paste template with defensive coding

### Scenario 3: Implementing New Feature
**You say:** "I want to add a new feature for query classification"

**This skill provides:**
1. Suggests **TDD Workflow** pattern
2. References `patterns/tdd-workflow.md`
3. Highlights RED → GREEN → REFACTOR cycle:
   - **RED**: Write ONE failing test first
   - **GREEN**: Minimal code to pass test
   - **REFACTOR**: Improve quality, keep tests green
4. Test naming convention: `test_should_[result]_when_[condition]()`

## References

**Primary documentation:**
- `patterns/README.md` - Pattern library catalog
- `patterns/tdd-workflow.md` - TDD methodology pattern
- `patterns/threadpool-parallel.md` - Concurrent batch processing pattern
- `patterns/abstract-base-class.md` - OOP interface pattern

**Skill-specific references:**
- `references/pattern-decision-tree.md` - When to use which pattern
- `references/integration-checklist.md` - Steps for applying patterns

## Quality Standards

All pattern applications must include:
- ✅ Type hints on all functions
- ✅ Defensive coding (input validation, error handling)
- ✅ Docstrings with Args/Returns/Raises
- ✅ Pattern reference comment: `# Pattern: [Name] (patterns/[file].md)`
- ✅ Tests following TDD workflow

## Notes

- **This skill provides GUIDANCE**, not enforcement
- Patterns are templates - customize for your specific use case
- All patterns include defensive coding by default
- Cross-reference pattern files for detailed examples and pitfalls
- When in doubt, read the full pattern documentation before applying
