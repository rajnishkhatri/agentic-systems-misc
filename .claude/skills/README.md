# Claude Skills System

**Status:** Under Development (Phase 1)

This directory contains the Claude Skills Configuration System - a framework for providing context-aware guidance to Claude Code based on conversation patterns.

## Overview

Skills are automatically activated based on conversation context (keywords, phrases) to provide:
- Best practice reminders
- Template recommendations
- References to existing documentation
- Quality enforcement

## Directory Structure

```
.claude/skills/
├── README.md                          # This file - quick reference guide
├── TESTING_SCENARIOS.md               # Skill activation test cases
├── tutorial-standards/                # Tutorial quality enforcement skill
│   ├── SKILL.md                      # Skill definition with YAML frontmatter
│   ├── references/                   # Reference documentation
│   └── examples/                     # Real examples from codebase
├── tdd-methodology/                   # TDD workflow enforcement skill
│   ├── SKILL.md
│   ├── references/
│   └── examples/
└── pattern-application/               # Pattern library application skill
    ├── SKILL.md
    ├── references/
    └── examples/
```

## Available Skills (Phase 1)

| Skill Name | Activation Context | Purpose | Status |
|------------|-------------------|---------|--------|
| Tutorial Standards | "create tutorial", "TUTORIAL_INDEX", "add notebook" | Enforce tutorial quality standards | Planned |
| TDD Methodology | "write test", "implement function", "TDD" | Enforce TDD workflow (RED→GREEN→REFACTOR) | Planned |
| Pattern Application | "parallel processing", "batch", "abstract base class" | Suggest patterns from `/patterns/` directory | Planned |

## How Skills Work

1. **Automatic Activation**: Skills activate based on conversation keywords
2. **Context-Aware**: Multiple skills can activate simultaneously
3. **Reference-Based**: Skills link to existing docs (CLAUDE.md, patterns/) instead of duplicating content
4. **Non-Blocking**: Provide guidance, not hard blocks (except where safety critical)

## Troubleshooting

### Skill Not Activating
- Check activation keywords in SKILL.md frontmatter
- Verify YAML frontmatter is valid
- Check `.claude/skills/TESTING_SCENARIOS.md` for test cases

### Wrong Guidance
- Review skill references section
- Check if multiple skills activated (potential conflict)
- Validate examples point to correct file:line references

### Skill Conflicts
- Disable temporarily: `mv .claude/skills/skill-name .claude/skills/_DISABLED_skill-name`
- Check activation contexts for overlap
- See rollback documentation in Task 6.8

## Usage Examples

### Example 1: Tutorial Creation
```
User: "I need to create a tutorial for evaluation metrics"
→ Tutorial Standards skill activates
→ Provides TUTORIAL_INDEX.md template reference
→ Links to lesson-9/TUTORIAL_INDEX.md example
→ Reminds about notebook execution time <5min
```

### Example 2: TDD Workflow
```
User: "Write test for the calculate_total function"
→ TDD Methodology skill activates
→ Enters RED phase
→ Provides test naming guidance: test_should_[result]_when_[condition]
→ Reminds: No implementation code in RED phase
```

### Example 3: Pattern Application
```
User: "I need to process 100 API calls in parallel"
→ Pattern Application skill activates
→ Suggests ThreadPoolExecutor pattern
→ References patterns/threadpool-parallel.md
→ Provides template with exception handling
```

## Skill Versioning

Skills use semantic versioning in YAML frontmatter:
- `version: 1.0.0` - Initial release
- `version: 1.1.0` - New references or examples added
- `version: 2.0.0` - Breaking changes to activation context

## Related Documentation

- [CLAUDE.md](../../CLAUDE.md) - Project instructions and TDD methodology
- [Pattern Library](../../patterns/README.md) - Reusable code patterns
- [Tutorial Workflow](../../CLAUDE.md#tutorial-workflow) - Tutorial creation guidelines
- [AI Dev Tasks](../../tasks/) - PRD and task management

## Phase 2 Candidates

Deferred to Phase 2 after validation:
- Architecture Skill (when to use agents vs. tools)
- Defensive Coding Skill (type hints, validation, error handling)
- Bhagavad Gita Domain Skill (cultural sensitivity, source faithfulness)

---

**Last Updated:** 2025-11-18
**Phase 1 Target:** 3 skills, 3 commands, comprehensive testing
