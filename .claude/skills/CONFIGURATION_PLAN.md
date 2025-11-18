# Claude Skills Configuration Plan v2.0

**Status:** 🚀 Ready for Implementation (Phase 1: 20-24h | Full Vision: 48-62h)
**Last Updated:** 2025-11-18
**Phase 1 Investment:** 20-24 hours (3 skills + 3 commands)
**Full Vision Investment:** 48-62 hours (6 skills + 4-5 commands)
**Success Criteria:** Improved Claude Code CLI session efficiency through workspace knowledge retention

---

## ⚠️ IMPORTANT: Phase 1 vs. Full Vision

This document describes the **FULL VISION** (6 skills, 5 phases, 48-62 hours) for the Claude Skills system.

**IMPLEMENTATION STRATEGY:**
- **Phase 1 (PRD Scope):** 3 highest-impact skills + 3 commands (20-24 hours) ← **START HERE**
- **Phase 2 (Future PRD):** 3 additional skills + 2 commands (16-20 hours) ← **After Phase 1 validation**

**Current Implementation:** See `tasks/tasks-0001-prd-claude-skills-configuration.md` for **Phase 1 ONLY** task breakdown.

---

## Executive Summary

### User Goals
1. **Workspace Knowledge Retention** - Skills learn project rules, architecture, patterns over time
2. **Session Efficiency** - Reduce repetitive explanations across sessions
3. **Command Exploration** - Discover useful workflow automations
4. **Phased Implementation** - Phase 1 (20-24h) validates approach before Phase 2 (16-20h)

### Implementation Approach
Based on official Claude Skills documentation, this plan implements **Skills for Claude Code CLI** (NOT Claude.ai/Desktop upload). Skills are discovered automatically from `.claude/skills/` directory.

**Key Insight from Docs:**
> "Skills in Claude Code are automatically discovered from the `.claude/skills/` directory in your project. Each skill is a folder containing a `SKILL.md` file with YAML frontmatter and markdown instructions."

---

## Current State Analysis

- **Existing Setup:** 10 slash commands in `.claude/commands/` directory
- **Missing:** No Skills directory (`.claude/skills/`) configured yet
- **Project Context:** LLM Evaluation Tutorial System with Bhagavad Gita Chatbot
- **Documentation:** Comprehensive CLAUDE.md (473 lines), Pattern Library (3 patterns)
- **Git Status:** Active development on Lesson 14 (Memory Systems)

---

## Understanding: Skills vs Commands (Claude Code CLI)

### Claude Skills (for Claude Code CLI)
- **Format:** Folders in `.claude/skills/` with `SKILL.md` file
- **Discovery:** Automatic - Claude reads all skills at conversation start
- **Activation:** LLM reasoning based on conversation context (NOT manual trigger)
- **Purpose:** Specialized knowledge and behaviors for recurring tasks
- **Persistence:** Skills provide consistent guidance across ALL sessions
- **Structure:**
  ```
  .claude/skills/skill-name/
  ├── SKILL.md           # Mandatory: YAML frontmatter + markdown instructions
  ├── references/        # Optional: supporting documentation
  ├── examples/          # Optional: code examples
  └── templates/         # Optional: file templates
  ```

**Official Documentation:**
- [Claude Code Skills Reference](https://code.claude.com/docs/en/skills)
- [Using Skills in Claude](https://support.claude.com/en/articles/12512180-using-skills-in-claude)

### Claude Code Commands (CLI)
- **Format:** Markdown files in `.claude/commands/` directory
- **Invocation:** Manual trigger with `/command-name` slash syntax
- **Purpose:** Predefined workflows for systematic development
- **Current Commands:** explore, issue, work, review, test, docs, reflect, create-prd, generate-tasks, process-task-list

**Key Difference:**
- **Skills** = Context-aware knowledge activated by LLM reasoning
- **Commands** = Manual workflows invoked by user with `/command-name`

---

## Skills vs Commands: When to Use Which

### Use Skills When:
- ✅ Knowledge needs to be consistent across ALL sessions
- ✅ Behavior should activate automatically based on context
- ✅ Guidance applies to recurring patterns (TDD, defensive coding, architecture)
- ✅ You want Claude to "remember" project conventions

**Examples:**
- Enforce TDD workflow when writing tests
- Apply defensive coding patterns when creating functions
- Follow tutorial structure when creating documentation
- Validate domain knowledge (Bhagavad Gita cultural sensitivity)

### Use Commands When:
- ✅ User wants explicit control over invocation
- ✅ Workflow has multiple variants/options
- ✅ Task requires user input during execution
- ✅ Action is infrequent or situational

**Examples:**
- `/explore` - Analyze codebase on demand
- `/create-prd` - Start new feature planning
- `/review` - Manual code review trigger
- `/test` - Run test suite with options



## Proposed Implementation Strategy

### Design Principles

1. **Avoid Duplication:** Skills should NOT duplicate CLAUDE.md or patterns/ - instead, they should **reference** and **enforce** existing documentation
2. **Workspace Knowledge:** Skills encode project-specific conventions (file structure, naming patterns, quality gates)
3. **Session Efficiency:** Skills eliminate need to repeat instructions across sessions
4. **Measurable Impact:** Each skill must improve specific workflow metric

### Skill Categories

| Category | Purpose | Impact Metric |
|----------|---------|---------------|
| **Development Methodology** | Enforce TDD, defensive coding | % of code with tests, type hint coverage |
| **Architecture Knowledge** | Understand project structure, dependencies | Fewer incorrect file placements |
| **Domain Knowledge** | Bhagavad Gita chatbot conventions | Cultural sensitivity compliance |
| **Quality Gates** | Tutorial validation, documentation standards | Reduced broken links, execution failures |
| **Pattern Application** | Apply documented patterns from patterns/ | Pattern usage rate, consistency |

---

## Skill Implementations

### 🚀 PHASE 1 SKILLS (PRD Scope - 20-24 hours)

The following 3 skills are implemented in Phase 1 (see tasks/tasks-0001-prd-claude-skills-configuration.md):

1. **Tutorial Standards Skill** (`tutorial-standards/`) - See section 3 below
2. **TDD Methodology Skill** (`tdd-methodology/`) - See section 2 below
3. **Pattern Application Skill** (`pattern-application/`) - See section 5 below

### 🔮 PHASE 2 SKILLS (Future PRD - 16-20 hours)

The following 3 skills are **DEFERRED** to Phase 2 after Phase 1 validation:

1. **Project Architecture Skill** (`architecture/`) - See section 1 below
2. **Defensive Coding Skill** (`defensive-coding/`) - See section 6 below
3. **Bhagavad Gita Domain Skill** (`gita-domain/`) - See section 4 below

**Why Phase 2?**
- Architecture Skill: Need Phase 1 metrics to validate file placement is a real bottleneck
- Defensive Coding Skill: TDD Methodology Skill covers most cases; validate need for additional skill
- Bhagavad Gita Domain Skill: Domain-specific; lower priority than universal skills

---

## Full Skill Catalog

### 1. Project Architecture Skill (`architecture/`) - **⏳ PHASE 2**

**Purpose:** Encode workspace structure knowledge to eliminate repeated questions about "where should this file go?"

**Problem Solved:** Claude currently asks "Where should I create this file?" or places files incorrectly → wastes time

**Structure:**
```
.claude/skills/architecture/
├── SKILL.md
├── references/
│   ├── directory-structure.md      # Full project tree with explanations
│   ├── file-naming-conventions.md  # Naming patterns (e.g., test_should_*.py)
│   └── dependency-map.md           # What imports what
└── examples/
    ├── lesson-structure-example.md  # How lesson-X/ directories are organized
    └── tutorial-placement-example.md
```

**SKILL.md Frontmatter:**
```yaml
name: project-architecture
description: Workspace structure, file placement rules, and naming conventions for LLM Evals Tutorial System
version: 1.0.0
activation_context:
  - "create file"
  - "where should"
  - "file structure"
  - "organize code"
  - "directory layout"
```

**Key Instructions in SKILL.md:**
- When creating files in `lesson-X/`, follow structure: `tutorials/`, `notebooks/`, `diagrams/`, `backend/`
- Test files go in `tests/` with naming: `test_[module_name].py`
- Tutorial index is always `TUTORIAL_INDEX.md` (uppercase)
- Backend code goes in `lesson-X/backend/` if lesson-specific, `src/` if shared
- Never create files in project root unless explicitly infrastructure (e.g., `pyproject.toml`)
- Reference: Read `references/directory-structure.md` for full tree

**Success Metric:** Reduce "file placement questions" from ~40% of sessions to <10%

---

### 2. TDD Methodology Skill (`tdd-methodology/`) - **🚀 PHASE 1**

**Purpose:** Automatically enforce RED→GREEN→REFACTOR workflow **without** duplicating CLAUDE.md guidance

**Problem Solved:** Claude sometimes skips tests or writes implementation before tests → violates TDD principle

**Structure:**
```
.claude/skills/tdd-methodology/
├── SKILL.md
├── references/
│   ├── phase-rules.md              # RED/GREEN/REFACTOR constraints
│   └── test-naming-guide.md        # test_should_[result]_when_[condition]
└── examples/
    ├── good-tdd-session.md          # Example from lesson-9 Task 2.3
    └── common-violations.md         # Anti-patterns to avoid
```

**SKILL.md Frontmatter:**
```yaml
name: tdd-methodology
description: Enforce Test-Driven Development (RED→GREEN→REFACTOR) workflow
version: 1.0.0
activation_context:
  - "write test"
  - "implement function"
  - "add feature"
  - "refactor"
  - "TDD"
references:
  - CLAUDE.md:33-115  # TDD Mode section (single source of truth)
```

**Key Instructions in SKILL.md:**
```markdown
## Activation Logic

When user requests new functionality or code changes:

1. **Check:** Does test exist for this behavior?
   - ❌ NO → Enter RED phase (write failing test first)
   - ✅ YES → Proceed to GREEN phase

2. **RED Phase Rules:**
   - NEVER write implementation code
   - Write ONE failing test using pattern: `test_should_[result]_when_[condition]()`
   - Run pytest to confirm failure
   - Show test output to user
   - Reference: CLAUDE.md:33-67 for detailed TDD guidance

3. **GREEN Phase Rules:**
   - Write MINIMAL code to make test pass
   - Apply 5-step defensive function template from CLAUDE.md:117-199
   - Run pytest to confirm pass
   - NEVER modify test

4. **REFACTOR Phase Rules:**
   - Improve code quality (DRY, readability, performance)
   - Keep all tests passing
   - Run pytest after each change

## Do NOT Duplicate
This skill enforces workflow, it does NOT replace CLAUDE.md TDD documentation.
Always reference CLAUDE.md for detailed defensive coding patterns.
```

**Success Metric:** 100% of new functions have tests written first (track via git commits)

---

### 3. Tutorial Standards Skill (`tutorial-standards/`) - **🚀 PHASE 1**

**Purpose:** Ensure all tutorials meet quality standards WITHOUT manual validation

**Problem Solved:** Tutorials sometimes have broken links, wrong reading time, or missing sections → discovered late

**Structure:**
```
.claude/skills/tutorial-standards/
├── SKILL.md
├── references/
│   ├── tutorial-index-template.md   # Required sections for TUTORIAL_INDEX.md
│   ├── notebook-standards.md        # Setup cells, cost warnings, <5min execution
│   └── cross-linking-rules.md       # Relative path conventions
└── examples/
    ├── lesson-9-tutorial-index.md   # Reference implementation
    └── good-notebook.ipynb          # Example with all required elements
```

**SKILL.md Frontmatter:**
```yaml
name: tutorial-standards
description: Enforce tutorial quality standards (reading time, cross-links, notebook execution)
version: 1.0.0
activation_context:
  - "create tutorial"
  - "TUTORIAL_INDEX"
  - "add notebook"
  - "write lesson"
references:
  - CLAUDE.md:347-435  # Tutorial Workflow section
```

**Key Instructions in SKILL.md:**
- Before creating tutorial, read `lesson-9/TUTORIAL_INDEX.md` as reference
- Required sections: Learning Objectives, Prerequisites, Recommended Paths, Tutorials, FAQs
- Concept tutorials: 15-30 min reading time (validate with word count ÷ 200 WPM)
- Notebooks: Must have setup cell, cost warning, validation assertions, <5min execution
- Cross-links: Use relative paths (`../lesson-10/tutorial.md`), not absolute
- After creating tutorial, validate:
  - Run: `jupyter nbconvert --execute [notebook].ipynb`
  - Check all cross-links resolve
  - Verify Mermaid diagrams render (test syntax)

**Success Metric:** Zero broken tutorials merged (validate before commit)

---

### 4. Bhagavad Gita Domain Skill (`gita-domain/`) - **⏳ PHASE 2**

**Purpose:** Encode cultural sensitivity, theological accuracy, and domain conventions

**Problem Solved:** Generic LLM may not understand Hindu philosophy nuances → risk of inappropriate responses

**Structure:**
```
.claude/skills/gita-domain/
├── SKILL.md
├── references/
│   ├── verse-format.md              # Chapter.Verse notation (e.g., BG 2.47)
│   ├── commentary-sources.md        # Valid commentators (Swami Sivananda, etc.)
│   └── cultural-guidelines.md       # Respectful language, avoiding stereotypes
└── examples/
    ├── good-responses.md            # Examples of appropriate chatbot responses
    └── bad-responses.md             # Common mistakes to avoid
```

**SKILL.md Frontmatter:**
```yaml
name: bhagavad-gita-domain
description: Cultural sensitivity and theological accuracy for Bhagavad Gita chatbot
version: 1.0.0
activation_context:
  - "Gita"
  - "verse"
  - "Krishna"
  - "Arjuna"
  - "dharma"
  - "yoga"
  - "Hindu"
  - "Sanskrit"
```

**Key Instructions in SKILL.md:**
- Verse references: Use "BG Chapter.Verse" format (e.g., "BG 2.47")
- When quoting verses: Always cite source and translation/commentary author
- Avoid: Appropriation language, stereotypes, "exotic" framing
- Use: Respectful academic tone, acknowledge multiple interpretations
- Validation: Does response cite specific verse + commentary? If NO → add citation
- Dataset sources:
  - Bhagwat-Gita-Infinity: 737 JSON files with commentaries
  - Bhagavad-Gita-QA: 3,500 Q&A pairs
- Quality standard: ≥95% faithfulness to source texts (no hallucinations)

**Success Metric:** Zero cultural sensitivity violations in chatbot responses

---

### 5. Pattern Application Skill (`pattern-application/`) - **🚀 PHASE 1**

**Purpose:** Automatically apply documented patterns from `patterns/` directory

**Problem Solved:** Developers forget to use patterns or apply them inconsistently → code duplication

**Structure:**
```
.claude/skills/pattern-application/
├── SKILL.md
└── references/
    ├── pattern-decision-tree.md     # When to use which pattern
    └── integration-checklist.md     # Steps for applying each pattern
```

**SKILL.md Frontmatter:**
```yaml
name: pattern-application
description: Apply documented code patterns (TDD, ThreadPoolExecutor, ABC) from pattern library
version: 1.0.0
activation_context:
  - "parallel processing"
  - "batch"
  - "concurrent"
  - "abstract base class"
  - "interface"
  - "framework"
references:
  - patterns/README.md
  - patterns/tdd-workflow.md
  - patterns/threadpool-parallel.md
  - patterns/abstract-base-class.md
```

**Key Instructions in SKILL.md:**
```markdown
## Pattern Selection Logic

When user requests functionality:

1. **Identify Use Case:**
   - Batch processing I/O-bound tasks (API calls, DB queries) → ThreadPoolExecutor pattern
   - Framework with multiple implementations → Abstract Base Class pattern
   - Any new feature → TDD Workflow pattern

2. **Check Pattern Library:**
   - Read `patterns/README.md` for full catalog
   - Find matching pattern by use case
   - Copy template from pattern documentation

3. **Apply Pattern:**
   - Follow copy-paste template exactly
   - Include defensive coding from pattern examples
   - Reference pattern file: `patterns/[pattern-name].md:line_number`

4. **Validate Application:**
   - Does code match pattern structure?
   - Are defensive coding principles applied?
   - Is error handling included?

## Available Patterns

| Pattern | Complexity | Use Case |
|---------|-----------|----------|
| TDD Workflow | ⭐⭐ | All development |
| ThreadPoolExecutor | ⭐⭐⭐ | Concurrent I/O-bound batch processing |
| Abstract Base Class | ⭐⭐⭐ | Polymorphic frameworks |

## Do NOT Duplicate
Read patterns from `patterns/` directory - do not recreate patterns inline.
Always reference original pattern documentation.
```

**Success Metric:** 90% of applicable code uses documented patterns

---

### 6. Defensive Coding Skill (`defensive-coding/`) - **⏳ PHASE 2**

**Purpose:** Automatically apply 5-step defensive function design pattern

**Problem Solved:** Functions missing type hints, input validation, or error handling → runtime bugs

**Structure:**
```
.claude/skills/defensive-coding/
├── SKILL.md
├── references/
│   └── 5-step-template.py           # Copy-paste template
└── examples/
    ├── good-examples.py             # Functions from lesson-9, hw3
    └── bad-examples.py              # Common mistakes
```

**SKILL.md Frontmatter:**
```yaml
name: defensive-coding
description: Apply 5-step defensive function design (type check → validate → edge cases → logic → return)
version: 1.0.0
activation_context:
  - "create function"
  - "implement"
  - "def "
  - "add method"
references:
  - CLAUDE.md:117-199  # 5-Step Defensive Template section
```

**Key Instructions in SKILL.md:**
```markdown
## 5-Step Pattern

When creating any function, follow this exact pattern:

### Step 1: Type Checking
- Add type hints to ALL parameters and return value
- Use `isinstance()` for runtime type validation if needed
- Raise `TypeError` with descriptive message

### Step 2: Input Validation
- Check ranges, non-null, non-empty
- Raise `ValueError` with descriptive message

### Step 3: Edge Case Handling
- Empty lists, zero division, missing keys
- Handle gracefully with defaults or specific exceptions

### Step 4: Main Logic
- The actual work of the function
- Keep this section clean and readable

### Step 5: Type-Safe Return
- Always return declared type
- Use explicit return statement

## Template
```python
def function_name(arg: Type, optional: Type = default) -> ReturnType:
    """Brief description.

    Args:
        arg: Description
        optional: Description

    Returns:
        Description

    Raises:
        TypeError: When type validation fails
        ValueError: When value validation fails
    """
    # Step 1: Type checking
    if not isinstance(arg, ExpectedType):
        raise TypeError("arg must be ExpectedType")

    # Step 2: Input validation
    if arg < 0:
        raise ValueError("arg must be non-negative")

    # Step 3: Edge case handling
    if len(arg) == 0:
        return default_value

    # Step 4: Main logic
    result = process(arg)

    # Step 5: Return
    return result
```

## Examples from Codebase
- Good: `workflow.py:301-344` (check_performance_alert)
- Good: `lesson-9/backend/exact_evaluation.py:45-78` (calculate_perplexity)
```

**Success Metric:** 100% of functions follow 5-step pattern (enforce in code reviews)

---

## Complementary CLI Commands

While Skills activate automatically, some workflows benefit from manual triggers:

### Command 1: `/skill-test` - Validate Skill Effectiveness

**Purpose:** Test if skills are activating correctly in conversations

**File:** `.claude/commands/skill-test.md`

**Usage:**
```bash
/skill-test               # Run all skill validation checks
/skill-test architecture  # Test specific skill
```

**What it does:**
- Lists all discovered skills from `.claude/skills/`
- Runs test scenarios to verify skill activation
- Reports success/failure metrics
- Suggests improvements if activation fails

**Implementation Priority:** Phase 2 (after initial skills are created)

---

### Command 2: `/validate-tutorial` - Tutorial Quality Gate

**Purpose:** Manual validation before committing tutorials

**File:** `.claude/commands/validate-tutorial.md`

**Usage:**
```bash
/validate-tutorial lesson-9/              # Validate all tutorials
/validate-tutorial lesson-9/perplexity.ipynb  # Validate specific file
```

**What it does:**
- Checks TUTORIAL_INDEX.md structure
- Validates reading time estimates
- Runs notebooks to ensure execution
- Verifies cross-links aren't broken
- Tests Mermaid diagram syntax
- Reports: ✅ Pass / ❌ Fail with actionable fixes

**Implementation Priority:** Phase 1 (high value, frequently needed)

---

### Command 3: `/pattern` - Pattern Application Helper

**Purpose:** Browse and apply patterns from patterns/ directory

**File:** `.claude/commands/pattern.md`

**Usage:**
```bash
/pattern                    # List available patterns
/pattern tdd               # Show TDD pattern details
/pattern threadpool apply  # Apply ThreadPoolExecutor template
```

**What it does:**
- Reads `patterns/README.md` for catalog
- Displays pattern complexity, use case, examples
- Copies template to clipboard or applies inline
- Shows file:line references from codebase

**Implementation Priority:** Phase 2 (nice-to-have, pattern-application skill covers most use cases)

---

### Command 4: `/tdd` - Explicit TDD Phase Tracker

**Purpose:** Manual TDD workflow control for when user wants step-by-step guidance

**File:** `.claude/commands/tdd.md`

**Usage:**
```bash
/tdd red           # Enter RED phase (write failing test)
/tdd green         # Enter GREEN phase (minimal implementation)
/tdd refactor      # Enter REFACTOR phase (improve code)
/tdd status        # Show current phase
```

**What it does:**
- Tracks current TDD phase
- Enforces phase rules (no code in RED, no test changes in GREEN)
- Auto-runs pytest after each phase transition
- Validates test naming convention
- Blocks phase skipping

**Relationship to tdd-methodology Skill:**
- **Skill:** Automatic activation when writing code
- **Command:** Explicit control when user wants guided workflow

**Implementation Priority:** Phase 2 (skill handles most cases)

---

## Implementation Checklist

### Phase 1: Core Skills (Week 1-2) - 20-24 hours

**Priority 1: Workspace Knowledge**
- [ ] Create `.claude/skills/` directory
- [ ] Implement `architecture/` skill (6-8 hours)
  - [ ] Create SKILL.md with activation context
  - [ ] Document directory structure in references/directory-structure.md
  - [ ] Add file naming conventions reference
  - [ ] Create lesson structure examples
  - [ ] Test: Ask "where should I create a tutorial?" → verify correct guidance
- [ ] Implement `tdd-methodology/` skill (4-5 hours)
  - [ ] Create SKILL.md referencing CLAUDE.md:33-115
  - [ ] Add phase rules reference document
  - [ ] Add test naming guide
  - [ ] Create good/bad TDD session examples
  - [ ] Test: Write code without test → verify RED phase enforced

**Priority 2: Quality Automation**
- [ ] Implement `tutorial-standards/` skill (5-6 hours)
  - [ ] Create SKILL.md referencing CLAUDE.md:347-435
  - [ ] Add TUTORIAL_INDEX template
  - [ ] Document notebook standards
  - [ ] Add cross-linking rules
  - [ ] Copy lesson-9/TUTORIAL_INDEX.md as example
  - [ ] Test: Create tutorial → verify validation runs
- [ ] Create `/validate-tutorial` command (5-6 hours)
  - [ ] Implement TUTORIAL_INDEX.md structure check
  - [ ] Add reading time validation (word count ÷ 200 WPM)
  - [ ] Implement notebook execution check
  - [ ] Add cross-link resolver
  - [ ] Add Mermaid diagram syntax validator
  - [ ] Test with lesson-9/ tutorials

**Phase 1 Deliverables:**
- 3 skills (architecture, tdd-methodology, tutorial-standards)
- 1 command (/validate-tutorial)
- Test results documented
- Success metrics baseline established

---

### Phase 2: Domain & Pattern Skills (Week 3-4) - 16-20 hours

**Priority 3: Pattern Enforcement**
- [ ] Implement `defensive-coding/` skill (4-5 hours)
  - [ ] Create SKILL.md referencing CLAUDE.md:117-199
  - [ ] Add 5-step template.py
  - [ ] Extract good examples from lesson-9, hw3
  - [ ] Document common mistakes
  - [ ] Test: Create function → verify 5-step pattern applied
- [ ] Implement `pattern-application/` skill (4-5 hours)
  - [ ] Create SKILL.md referencing patterns/README.md
  - [ ] Add pattern decision tree
  - [ ] Create integration checklist
  - [ ] Test: Request parallel processing → verify ThreadPoolExecutor suggested

**Priority 4: Domain Knowledge**
- [ ] Implement `gita-domain/` skill (6-8 hours)
  - [ ] Create SKILL.md with Sanskrit/Hindu context keywords
  - [ ] Document verse format (BG Chapter.Verse)
  - [ ] List valid commentary sources
  - [ ] Create cultural sensitivity guidelines
  - [ ] Add good/bad chatbot response examples
  - [ ] Test: Ask about Gita verse → verify citation format

**Phase 2 Deliverables:**
- 3 additional skills (defensive-coding, pattern-application, gita-domain)
- Total: 6 skills operational
- Pattern usage metrics collected

---

### Phase 3: CLI Commands (Week 5) - 8-12 hours

**Optional Commands (implement as needed)**
- [ ] Create `/skill-test` command (3-4 hours)
  - [ ] List all skills in `.claude/skills/`
  - [ ] Run activation test scenarios
  - [ ] Report metrics
  - [ ] Suggest improvements
- [ ] Create `/pattern` command (3-4 hours)
  - [ ] Read patterns/README.md
  - [ ] Display pattern details
  - [ ] Apply template inline
  - [ ] Show codebase examples
- [ ] Create `/tdd` command (2-4 hours)
  - [ ] Track TDD phase state
  - [ ] Enforce phase rules
  - [ ] Auto-run pytest
  - [ ] Validate test names

**Phase 3 Deliverables:**
- 2-3 additional commands
- Command usage metrics
- Total: 6 skills + 4-5 commands

---

### Phase 4: Documentation (Week 6) - 4-6 hours

- [ ] Create `.claude/skills/README.md`
  - [ ] Quick reference guide for all skills
  - [ ] Activation context catalog
  - [ ] Testing scenarios
  - [ ] Troubleshooting guide
- [ ] Update `CLAUDE.md`
  - [ ] Add "Claude Skills System" section (concise, not 200+ lines)
  - [ ] Link to .claude/skills/README.md for details
  - [ ] Update project structure diagram
  - [ ] Add success metrics section
- [ ] Create skill activation test suite
  - [ ] Test scenarios for each skill
  - [ ] Expected activation criteria
  - [ ] Validation checklist
- [ ] Update `.claude/commands/README.md` (if exists)
  - [ ] Document new commands
  - [ ] Explain skill vs command usage

---

### Phase 5: Validation & Iteration (Ongoing)

**Week 7-8: Measure Effectiveness**
- [ ] Track success metrics:
  - [ ] File placement questions: Target <10% of sessions
  - [ ] TDD compliance: Target 100% of new functions
  - [ ] Tutorial validation failures: Target 0 broken tutorials merged
  - [ ] Pattern usage: Target 90% of applicable code
  - [ ] Cultural sensitivity: Target 0 violations
- [ ] Collect feedback:
  - [ ] Which skills activate too frequently?
  - [ ] Which skills never activate?
  - [ ] Which activation contexts are missing?
  - [ ] Which instructions are unclear?

**Week 9-12: Iteration**
- [ ] Refine activation contexts based on metrics
- [ ] Update skill instructions for clarity
- [ ] Add missing examples
- [ ] Deprecate unused skills
- [ ] Add new skills for discovered patterns

---

## Success Metrics Dashboard

**Phase 1 Approach:** Qualitative snapshot + feedback (not comprehensive quantitative tracking)

### Baseline Snapshot (Before Skills) - 2 hours collection time
- **File placement questions:** Quick count from last 2 weeks git log/PRs
- **TDD compliance:** Scan recent commits for 3-5 examples of tests written AFTER implementation
- **Tutorial validation time:** Manually validate lesson-9/ once, time the process
- **Broken tutorials:** Review last 5 merged tutorials for broken links, execution errors
- **Pattern usage:** Quick code review of 2-3 recent functions
- **Document:** 1-page summary in `.claude/skills/BASELINE_SNAPSHOT.md`

### Phase 1 Target (After Skills) - Qualitative feedback assessment
- **Session efficiency:** "Are you repeating yourself less?" (qualitative survey, PRD:328-358)
- **Tutorial quality:** "Are tutorials breaking less often?" (track post-Phase 1)
- **Pattern usage:** "Using documented patterns more consistently?" (developer perception)
- **TDD compliance:** "Writing tests before implementation?" (self-reported)
- **Skill activation:** "Do skills activate at right times?" (user feedback)
- **Overall value:** "Has Skills system improved workflow?" (yes/somewhat/no)

**Note:** Detailed quantitative metrics deferred to Phase 2. Phase 1 uses lightweight qualitative assessment to validate approach before investing in instrumentation.

---

## Testing Strategy

### Skill Activation Testing

For each skill, test these scenarios:

**Architecture Skill**
```
Test 1: File creation without location specified
User: "Create a new tutorial about perplexity"
Expected: Skill suggests lesson-X/tutorials/ directory
Validation: File created in correct location without user prompt

Test 2: Incorrect file placement attempt
User: "Put the test in src/"
Expected: Skill corrects to tests/ directory
Validation: File created in tests/ directory

Test 3: No activation when location is clear
User: "Update lesson-9/TUTORIAL_INDEX.md"
Expected: Skill does NOT activate (location already specified)
Validation: No redundant architecture guidance
```

**TDD Methodology Skill**
```
Test 1: Function implementation without test
User: "Implement calculate_rouge_l function"
Expected: Skill enforces RED phase - request test first
Validation: No implementation until test exists

Test 2: Test modification during GREEN phase
User: "Change the test to expect different output"
Expected: Skill blocks test modification in GREEN phase
Validation: Test remains unchanged

Test 3: No activation when refactoring
User: "Refactor this function for readability"
Expected: Skill allows refactoring with tests passing
Validation: REFACTOR phase rules applied
```

**Tutorial Standards Skill**
```
Test 1: Tutorial creation without TUTORIAL_INDEX
User: "Create a tutorial about BLEU scores"
Expected: Skill prompts for TUTORIAL_INDEX.md creation
Validation: TUTORIAL_INDEX.md exists with required sections

Test 2: Notebook without cost warning
User: "Add a notebook calling GPT-4"
Expected: Skill adds cost warning cell
Validation: Notebook has "⚠️ Cost Warning" cell

Test 3: Broken cross-link
User: "Link to ../lesson-99/nonexistent.md"
Expected: Skill validates link and reports broken
Validation: Link validation error shown
```

### Command Testing

**`/validate-tutorial` Command**
```bash
# Test 1: Valid tutorial
/validate-tutorial lesson-9/
Expected: ✅ All checks pass

# Test 2: Missing TUTORIAL_INDEX
mkdir lesson-test && /validate-tutorial lesson-test/
Expected: ❌ TUTORIAL_INDEX.md not found

# Test 3: Broken notebook
# Create notebook with syntax error
/validate-tutorial lesson-test/broken.ipynb
Expected: ❌ Notebook execution failed with error details
```

---

## Rollback Plan

If a skill causes problems:

1. **Disable Skill Temporarily**
   ```bash
   # Rename skill folder to deactivate
   mv .claude/skills/problematic-skill .claude/skills/_DISABLED_problematic-skill
   ```

2. **Identify Issue**
   - Check activation logs
   - Review recent sessions where skill activated
   - Identify incorrect guidance or over-activation

3. **Fix or Remove**
   - Update activation_context to be more specific
   - Refine instructions for clarity
   - Remove skill if not providing value

4. **Version Control**
   - All skills versioned in git
   - Can revert to previous working version
   - Document changes in skill CHANGELOG

---

## Maintenance Strategy

### Monthly Review

- Audit skill activation frequency
- Review session transcripts for skill quality
- Update examples with new codebase patterns
- Sync with CLAUDE.md and patterns/ updates

### Quarterly Deep Dive

- Measure all success metrics
- Identify skills with low activation → deprecate
- Identify new patterns → create new skills
- Refactor skills with duplication

### Skill Versioning

Follow semantic versioning (MAJOR.MINOR.PATCH):

```yaml
version: 1.0.0  # Initial release
version: 1.1.0  # Added new activation context
version: 1.0.1  # Fixed typo in instructions
version: 2.0.0  # Breaking change: restructured skill
```

---

## Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Skills never activate | MEDIUM | HIGH | Test activation thoroughly in Phase 5 |
| Skills activate too frequently | MEDIUM | MEDIUM | Refine activation_context keywords |
| Skills give incorrect guidance | LOW | HIGH | Include references/ with source of truth |
| Skills duplicate CLAUDE.md | HIGH | MEDIUM | Reference, don't replicate - enforce in reviews |
| Documentation drift | HIGH | HIGH | Monthly sync with CLAUDE.md and patterns/ |
| Maintenance burden | MEDIUM | MEDIUM | Deprecate unused skills quarterly |

---

## Effort Summary

**Phase 1 (PRD Scope):**
| Component | Hours | Deliverables | Timeline |
|-----------|-------|--------------|----------|
| Skills Infrastructure | 3-4h | `.claude/skills/` setup, testing framework | Week 1 |
| Tutorial Standards Skill | 5-6h | Skill + references + examples + testing | Week 1 |
| TDD + Pattern Skills | 8-10h | 2 skills + integration testing | Week 2 |
| Commands Suite | 10-12h | /validate-tutorial + /tdd + /pattern + error handling | Week 2-3 |
| Documentation & Validation | 8-10h | README, CLAUDE.md, rollback plan, feedback template | Week 3 |
| **Phase 1 Total** | **21-25h** | **3 skills + 3 commands + docs** | **3-4 weeks** |

**Full Vision (Phase 1 + Phase 2):**
| Phase | Hours | Deliverables | Timeline |
|-------|-------|--------------|----------|
| Phase 1: PRD Scope | 21-25h | 3 skills + 3 commands | Week 1-4 |
| Phase 2: Additional Skills | 16-20h | 3 skills + 2 commands | Week 5-8 (if Phase 1 validation passes) |
| **TOTAL** | **37-45h** | 6 skills + 5 commands | 8-10 weeks |

**Note:** Phase 1 effort increased from 20-24h to 21-25h due to critical gap fixes (integration testing, error handling, feedback template). Phase 2 timeline contingent on Phase 1 go/no-go decision.

---

## Usage Examples (After Implementation)

### Example 1: Automatic Architecture Guidance

**Before Skills:**
```
User: I want to add a new evaluation metric for ROUGE-L
Claude: Where would you like me to create this? Should it go in lesson-9/backend/?
User: Yes, lesson-9/backend/exact_evaluation.py
Claude: Should I also create tests?
User: Yes, in tests/
Claude: What should I name the test file?
User: test_exact_evaluation.py
```
**3 back-and-forth exchanges**

**After Skills (architecture + tdd-methodology):**
```
User: I want to add a new evaluation metric for ROUGE-L
Claude: [architecture skill: knows to use lesson-9/backend/exact_evaluation.py]
Claude: [tdd-methodology skill: knows to write test first]
Claude: I'll add ROUGE-L to lesson-9/backend/exact_evaluation.py following TDD.

**RED Phase**: Writing failing test in tests/test_exact_evaluation.py...
[Creates test_should_calculate_rouge_l_when_valid_input()]
Running pytest... ❌ FAILED (expected - function doesn't exist yet)

**GREEN Phase**: Implementing calculate_rouge_l()...
[Implements with 5-step defensive pattern]
Running pytest... ✅ PASSED

**REFACTOR Phase**: Code quality looks good, moving to next feature.
```
**0 back-and-forth - fully autonomous**

---

### Example 2: Tutorial Creation with Automatic Validation

**Before Skills:**
```
User: Create a tutorial for Lesson 14 on agent evaluation
Claude: [Creates tutorial files]
User: Can you add the TUTORIAL_INDEX?
Claude: [Creates TUTORIAL_INDEX.md]
User: I think the cross-link is broken
Claude: Let me check... yes, fixing it
User: Does the notebook run without errors?
Claude: Let me test... [runs notebook] ... yes it works
```
**4 back-and-forth exchanges**

**After Skills (tutorial-standards):**
```
User: Create a tutorial for Lesson 14 on agent evaluation
Claude: [tutorial-standards skill activates]
Creating comprehensive tutorial with validation...

✅ Created lesson-14/TUTORIAL_INDEX.md (required sections verified)
✅ Created lesson-14/tutorials/agent_evaluation_fundamentals.md (reading time: 22 min ✓)
✅ Created lesson-14/notebooks/agent_evaluation.ipynb
   - Setup cell ✓
   - Cost warning ✓
   - Validation assertions ✓
   - Execution time: 3m 42s ✓
✅ Created lesson-14/diagrams/agent_architecture.mmd (syntax valid ✓)
✅ Cross-linked with lesson-13/TUTORIAL_INDEX.md (link verified ✓)

All validation checks passed. Tutorial ready for use.
```
**0 back-and-forth - fully validated automatically**

---

### Example 3: Pattern Application

**Before Skills:**
```
User: I need to process 1000 LLM-as-Judge evaluations in parallel
Claude: You could use ThreadPoolExecutor for that
User: Can you show me how?
Claude: [Writes basic ThreadPoolExecutor code]
User: This doesn't have error handling
Claude: [Adds try/except]
User: How do I preserve order?
Claude: [Adds future_to_index mapping]
```
**4 back-and-forth exchanges**

**After Skills (pattern-application):**
```
User: I need to process 1000 LLM-as-Judge evaluations in parallel
Claude: [pattern-application skill: recognizes I/O-bound batch processing]
I'll use the ThreadPoolExecutor pattern from patterns/threadpool-parallel.md.

[Applies complete template with:]
- Concurrent futures with future_to_index mapping (order preserved)
- Exception handling with fallbacks
- tqdm progress tracking
- Defensive coding (type hints, validation, edge cases)
- Based on pattern: patterns/threadpool-parallel.md:87-152

Code ready. Pattern correctly applied with all defensive safeguards.
```
**0 back-and-forth - complete pattern applied first time**

---

## Next Steps

**Immediate Actions:**
1. ✅ Review and approve this plan
2. Create `.claude/skills/` directory
3. Start Phase 1: Implement `architecture/` skill (highest impact)
4. Test with real scenarios
5. Measure baseline metrics

**First Milestone (Week 2):**
- 3 skills operational
- `/validate-tutorial` command working
- Baseline metrics established
- First iteration based on feedback

**Success Criteria (Week 12):**
- 6 skills + 4-5 commands
- Measurable improvement in all success metrics
- Documentation complete
- Skills system is self-sustaining

---

## Resources

**Official Documentation:**
- [Claude Code Skills](https://code.claude.com/docs/en/skills)
- [Using Skills in Claude](https://support.claude.com/en/articles/12512180-using-skills-in-claude)
- [Claude Skills Deep Dive](https://leehanchung.github.io/blogs/2025/10/26/claude-skills-deep-dive/)

**Project-Specific:**
- [CLAUDE.md](../CLAUDE.md) - Project philosophy
- [Pattern Library](../../patterns/README.md) - Documented patterns
- [TUTORIAL_INDEX Examples](../../lesson-9/TUTORIAL_INDEX.md) - Tutorial structure

---

## Revision History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0.0 | 2025-11-18 | Initial configuration plan | Research-based proposal |
| 2.0.0 | 2025-11-18 | Complete revision based on official docs, user goals, removed duplication | Final implementation plan |

---

**Status:** 📋 Ready for Implementation
**Approval Required:** Yes
**Next Action:** Create `.claude/skills/` directory and start Phase 1

