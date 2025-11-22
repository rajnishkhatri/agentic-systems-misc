# Product Requirements Document: Claude Skills Configuration System

## Introduction/Overview

This PRD defines the implementation of a **Claude Skills Configuration System** for the LLM Evaluation Tutorial project. The system will enable Claude Code CLI to retain workspace knowledge across sessions, reducing repetitive explanations and improving development efficiency.

**Problem Statement:**
Currently, Claude Code CLI sessions are stateless. Each new session requires re-explaining project conventions (file placement, TDD workflow, tutorial standards, code patterns). This wastes time and reduces productivity for developers working on the LLM evaluation tutorial system and Bhagavad Gita chatbot.

**Solution:**
Implement Claude Skills (context-aware knowledge activated by LLM reasoning) that automatically enforce project conventions, quality standards, and development patterns. Skills are discovered from `.claude/skills/` directory and activate based on conversation context.

**Scope:**
Phase 1 implementation focusing on 3 highest-impact skills + 3 essential commands (~20-24 hours investment).

---

## Goals

1. **Reduce Session Overhead**: Eliminate 50%+ of repetitive instructions about project structure, workflow, and standards
2. **Improve Code Quality**: Automatically enforce TDD, defensive coding, and pattern usage without manual reminders
3. **Accelerate Tutorial Development**: Automate tutorial validation to catch errors before commit
4. **Preserve Workspace Knowledge**: Skills "remember" project conventions across all sessions
5. **Enable Self-Service**: Developers can discover and apply documented patterns without asking

---

## User Stories

### US-1: Automatic File Placement
**As a developer**, I want Claude to automatically place files in the correct directory structure
**So that** I don't waste time asking "where should this file go?" in every session
**Acceptance Criteria:**
- When creating tutorial files, Claude automatically uses `lesson-X/tutorials/`, `notebooks/`, `diagrams/` structure
- When creating tests, Claude automatically places them in `tests/` with `test_*.py` naming
- No file placement questions for standard file types (<10% of sessions require clarification)

### US-2: Enforced TDD Workflow
**As a developer following TDD**, I want Claude to enforce RED→GREEN→REFACTOR phases
**So that** I never accidentally write implementation before tests
**Acceptance Criteria:**
- When requesting new functionality, Claude writes failing test first (RED phase)
- Implementation only begins after test exists (GREEN phase)
- Code improvements happen after tests pass (REFACTOR phase)
- Test naming follows convention: `test_should_[result]_when_[condition]()`

### US-3: Automated Tutorial Validation
**As a tutorial author**, I want automatic validation before committing tutorials
**So that** I catch broken links, execution errors, and missing sections early
**Acceptance Criteria:**
- `/validate-tutorial` command checks TUTORIAL_INDEX.md structure
- Notebooks execute successfully without errors (<5 min execution time)
- Cross-links resolve correctly (no 404s)
- Mermaid diagram syntax is valid
- Reading time estimates are accurate (word count ÷ 200 WPM)

### US-4: Pattern Application Guidance
**As a developer**, I want Claude to suggest documented patterns from `/patterns/` directory
**So that** I use consistent, maintainable code without memorizing all patterns
**Acceptance Criteria:**
- When requesting parallel processing, Claude suggests ThreadPoolExecutor pattern
- When creating frameworks, Claude suggests Abstract Base Class pattern
- Pattern templates include defensive coding by default
- Claude references pattern documentation with file:line numbers

### US-5: Tutorial Standards Enforcement
**As a tutorial author**, I want Claude to automatically apply tutorial quality standards
**So that** all tutorials have consistent structure and quality
**Acceptance Criteria:**
- TUTORIAL_INDEX.md includes all required sections (objectives, prerequisites, paths, FAQs)
- Notebooks have setup cells, cost warnings, validation assertions
- Tutorials use relative paths for cross-linking
- Diagrams are included for complex workflows

### US-6: Explicit TDD Phase Control
**As a TDD practitioner**, I want manual control over TDD phases when needed
**So that** I can step through RED→GREEN→REFACTOR explicitly
**Acceptance Criteria:**
- `/tdd red` enters RED phase and enforces "no implementation" rule
- `/tdd green` enters GREEN phase and enforces "no test modification" rule
- `/tdd refactor` enters REFACTOR phase and runs pytest after changes
- `/tdd status` shows current phase

### US-7: Pattern Discovery
**As a developer**, I want to browse available patterns with `/pattern` command
**So that** I can discover reusable solutions for common problems
**Acceptance Criteria:**
- `/pattern` lists all patterns from `/patterns/README.md`
- `/pattern [name]` shows pattern details, complexity, use cases
- Pattern examples include file:line references to codebase
- Pattern templates can be applied inline

---

## Functional Requirements

### FR-1: Skills Infrastructure
1.1. Create `.claude/skills/` directory in project root
1.2. Each skill is a folder containing `SKILL.md` file with YAML frontmatter
1.3. Skills include optional subdirectories: `references/`, `examples/`, `templates/`
1.4. Skills are automatically discovered by Claude Code CLI at conversation start
1.5. Skills activate based on `activation_context` keywords in conversation

### FR-2: Tutorial Standards Skill
2.1. **Activation Context:** "create tutorial", "TUTORIAL_INDEX", "add notebook", "write lesson"
2.2. Enforce TUTORIAL_INDEX.md structure (objectives, prerequisites, paths, FAQs)
2.3. Validate notebook standards (setup cell, cost warning, validation assertions, <5min execution)
2.4. Enforce cross-linking with relative paths
2.5. Validate reading time estimates (word count ÷ 200 WPM = 15-30 min)
2.6. Check Mermaid diagram syntax validity
2.7. Reference `lesson-9/TUTORIAL_INDEX.md` as template example

### FR-3: Pattern Application Skill
3.1. **Activation Context:** "parallel processing", "batch", "concurrent", "abstract base class", "interface", "framework"
3.2. Read patterns from `/patterns/README.md` for catalog
3.3. Suggest appropriate pattern based on use case:
   - I/O-bound batch processing → ThreadPoolExecutor pattern
   - Framework with multiple implementations → Abstract Base Class pattern
   - Any new feature → TDD Workflow pattern
3.4. Apply pattern template from documentation with defensive coding
3.5. Reference original pattern file with file:line notation
3.6. Validate pattern structure matches template

### FR-4: TDD Methodology Skill
4.1. **Activation Context:** "write test", "implement function", "add feature", "refactor", "TDD"
4.2. Enforce RED phase: Write failing test before implementation
4.3. Enforce GREEN phase: Minimal code to pass test, no test modification
4.4. Enforce REFACTOR phase: Improve code quality while keeping tests passing
4.5. Apply test naming convention: `test_should_[result]_when_[condition]()`
4.6. Reference CLAUDE.md:33-115 for detailed TDD guidance
4.7. Run pytest automatically after each phase

### FR-5: `/validate-tutorial` Command
5.1. Accept directory path or specific file path as argument
5.2. Check TUTORIAL_INDEX.md exists and has required sections
5.3. Execute all notebooks with `jupyter nbconvert --execute`
5.4. Verify execution time <5 minutes per notebook
5.5. Validate cross-links resolve correctly (check relative paths)
5.6. Test Mermaid diagram syntax (parse .mmd files)
5.7. Calculate reading time from word count
5.8. Output ✅/❌ report with actionable fixes

### FR-6: `/tdd` Command
6.1. Track current TDD phase state (RED/GREEN/REFACTOR)
6.2. `/tdd red` - Enter RED phase, display guidance reminder: "Write failing test. No implementation code."
6.3. `/tdd green` - Enter GREEN phase, display guidance reminder: "Minimal code to pass test. No test modifications."
6.4. `/tdd refactor` - Enter REFACTOR phase, run pytest after changes, display reminder: "Improve code quality. Keep tests passing."
6.5. `/tdd status` - Display current phase and phase-specific guidance
6.6. Auto-run pytest after phase transitions
6.7. Validate test naming convention

**Note:** `/tdd` command provides **guidance** (helpful reminders). TDD Methodology Skill (FR-4) provides **enforcement** (blocks violations). Command is manual "what should I do?", Skill is automatic workflow enforcement.

### FR-7: `/pattern` Command
7.1. `/pattern` - List all patterns from `/patterns/README.md`
7.2. `/pattern [name]` - Show pattern details (complexity, use case, examples)
7.3. `/pattern [name] apply` - Copy template to clipboard or apply inline
7.4. Display file:line references to codebase examples
7.5. Show pattern complexity rating (⭐⭐⭐)

### FR-8: Skill Isolation & Testing
8.1. Create skills one at a time with full testing before activation
8.2. Test each skill with scenarios from Configuration Plan
8.3. Validate activation context triggers correctly
8.4. Ensure skills don't duplicate CLAUDE.md content (reference instead)
8.5. Confirm skills provide correct guidance for edge cases

### FR-9: Documentation
9.1. Create `.claude/skills/README.md` with quick reference for all skills
9.2. Update `CLAUDE.md` with "Claude Skills System" section (concise, link to skills README)
9.3. Create skill activation test suite with expected behaviors
9.4. Update `.claude/commands/README.md` with new command documentation
9.5. Include troubleshooting guide for skill activation issues

### FR-10: Quality Validation
10.1. All skill SKILL.md files have valid YAML frontmatter
10.2. All reference files exist and are linked correctly
10.3. All examples have file:line references to real codebase files
10.4. Skills reference CLAUDE.md/patterns/ instead of duplicating content
10.5. Test scenarios pass before skill activation

---

## Non-Goals (Out of Scope)

### Phase 1 Exclusions (Deferred to Phase 2)

The following skills and commands are **explicitly deferred** to Phase 2 implementation:

#### Deferred Skills (3 skills, 16-20 hours)

1. **Architecture Skill** (file placement guidance)
   - **Why deferred:** Need Phase 1 metrics to validate file placement is a real bottleneck
   - **Phase 2 implementation:** 6-8 hours
   - **Dependencies:** Phase 1 baseline metrics on "file placement questions per session"

2. **Defensive Coding Skill** (5-step pattern enforcement)
   - **Why deferred:** TDD Methodology Skill covers most defensive coding cases
   - **Phase 2 implementation:** 4-5 hours
   - **Dependencies:** Phase 1 analysis of defensive coding violations in code reviews

3. **Bhagavad Gita Domain Skill** (cultural sensitivity)
   - **Why deferred:** Domain-specific; lower priority than universal development skills
   - **Phase 2 implementation:** 6-8 hours
   - **Dependencies:** Phase 1 chatbot response audit for cultural sensitivity issues

#### Deferred Commands (2 commands, 5-8 hours)

1. **`/skill-test` command** (skill activation validation)
   - **Why deferred:** Manual testing sufficient for Phase 1; automation is nice-to-have
   - **Phase 2 implementation:** 3-4 hours
   - **Dependencies:** Phase 1 skill activation patterns documented

2. **Additional command slots** (TBD based on Phase 1 learnings)
   - **Phase 2 implementation:** 2-4 hours
   - **Dependencies:** Phase 1 feedback on workflow gaps

#### Phase 2 Initiation Criteria

Phase 2 PRD will be created **AFTER** Phase 1 validation (2-week usage period) IF:
- ✅ Phase 1 skills activate correctly (>80% of expected scenarios)
- ✅ Measurable improvement in session efficiency (>30% reduction in repetitive explanations)
- ✅ No critical issues with Phase 1 skills (activation accuracy >90%)
- ✅ User feedback indicates value in expanding skills system

**Phase 2 Timeline:** 3-4 weeks after Phase 1 completion (contingent on validation results)

---

### Permanent Non-Goals
- ❌ Skills for Claude.ai or Claude Desktop (this is CLI-only)
- ❌ Automated skill generation (skills are manually created and curated)
- ❌ Skills that duplicate CLAUDE.md content (must reference, not replicate)
- ❌ Complex AI-driven skill activation logic (use simple keyword matching)
- ❌ Metrics tracking infrastructure (Phase 1 uses qualitative feedback only)

---

## Design Considerations

### Skill Structure
```
.claude/skills/tutorial-standards/
├── SKILL.md                          # YAML frontmatter + markdown instructions
├── references/
│   ├── tutorial-index-template.md    # Required sections for TUTORIAL_INDEX.md
│   ├── notebook-standards.md         # Setup cells, cost warnings, <5min execution
│   └── cross-linking-rules.md        # Relative path conventions
└── examples/
    ├── lesson-9-tutorial-index.md    # Reference implementation
    └── good-notebook.ipynb           # Example with all required elements
```

### SKILL.md Frontmatter Format
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

### Activation Logic
- Skills use **keyword matching** in conversation context
- Activation is **automatic** (not manually triggered like commands)
- Multiple skills can activate simultaneously
- Skills can reference each other (e.g., TDD skill + Pattern Application skill)

### Reference Strategy
Skills **reference** existing documentation instead of duplicating:
- TDD Methodology Skill → References CLAUDE.md:33-115
- Pattern Application Skill → References /patterns/README.md
- Tutorial Standards Skill → References CLAUDE.md:347-435

---

## Technical Considerations

### Dependencies
- **Claude Code CLI**: Skills feature (available in latest version)
- **Existing Infrastructure**:
  - CLAUDE.md (project philosophy)
  - /patterns/ directory (pattern library)
  - lesson-9/TUTORIAL_INDEX.md (tutorial template)
- **Tools**:
  - `jupyter nbconvert` for notebook validation
  - `pytest` for TDD workflow
  - Mermaid CLI for diagram validation (optional)

### File System Integration
- Skills directory: `.claude/skills/` (auto-discovered)
- Commands directory: `.claude/commands/` (slash command invocation)
- No code changes required (configuration-only system)

### Testing Strategy
**For Each Skill:**
1. Create test scenarios (e.g., "create tutorial without TUTORIAL_INDEX")
2. Verify activation context triggers
3. Validate guidance provided matches expected behavior
4. Test edge cases (e.g., broken cross-links, missing sections)
5. Confirm no duplication of CLAUDE.md content

**For Commands:**
1. Test with valid inputs (e.g., `/validate-tutorial lesson-9/`)
2. Test with invalid inputs (e.g., missing directory)
3. Verify error messages are actionable
4. Test execution time <30 seconds for typical workloads

### Rollback Strategy
- Skills can be disabled by renaming folder: `_DISABLED_skill-name/`
- All skills versioned in git (can revert to previous version)
- Incremental rollout: one skill at a time with validation

### Integration with Existing Workflow
- Skills complement existing slash commands (don't replace)
- TDD Methodology Skill works with existing pytest infrastructure
- Pattern Application Skill integrates with /patterns/ directory
- Tutorial Standards Skill uses existing TUTORIAL_INDEX.md format

---

## Success Metrics

### Qualitative Assessment (Developer Feedback)

**After 2 weeks of usage, collect feedback on:**

1. **Session Efficiency**
   - Question: "Are you repeating yourself less across sessions?"
   - Target: "Yes, significantly less repetition" from primary developers

2. **Tutorial Quality**
   - Question: "Are tutorials breaking less often?"
   - Target: "Zero broken tutorials merged in 2-week period"

3. **Pattern Usage**
   - Question: "Are you using documented patterns more consistently?"
   - Target: "90%+ of applicable code uses patterns"

4. **TDD Compliance**
   - Question: "Are you writing tests before implementation?"
   - Target: "100% of new functions have tests first" (validated via git log)

5. **Skill Activation Quality**
   - Question: "Do skills activate at the right times?"
   - Target: "Skills provide helpful guidance without over-activating"

6. **Command Utility**
   - Question: "Are the new commands useful?"
   - Target: "`/validate-tutorial` used before every tutorial commit"

7. **Overall Experience**
   - Question: "Has the Skills system improved your workflow?"
   - Target: "Yes, measurable productivity gain" from developers

### Quantitative Metrics (Optional, Phase 2)
- Tutorial validation time: <5 minutes (down from ~30 minutes manual) - measured via `/validate-tutorial` command timing
- File placement questions: <10% of sessions - tracked if Architecture skill implemented in Phase 2
- Skill activation frequency: Track which skills activate most - deferred to Phase 2 instrumentation

**Note:** Phase 1 uses qualitative feedback (PRD:328-358) instead of quantitative metrics to reduce implementation overhead. Baseline snapshot (not comprehensive metrics) establishes "before state" for comparison.

---

## Open Questions

### Q1: Skill Activation Tuning
- **Question**: What if skills activate too frequently or not frequently enough?
- **Answer**: Start with broad activation contexts, then refine based on 2-week feedback. Can adjust keywords in YAML frontmatter.

### Q2: Skill Conflict Resolution
- **Question**: What if multiple skills give conflicting guidance?
- **Answer**: Skills should be orthogonal (non-overlapping). If conflicts arise, prioritize TDD Methodology > Tutorial Standards > Pattern Application.

### Q3: Documentation Drift
- **Question**: How do we keep skills synced with CLAUDE.md and /patterns/ updates?
- **Answer**: Monthly review (out of Phase 1 scope). Document sync process in `.claude/skills/README.md`.

### Q4: Phase 2 Prioritization
- **Question**: After Phase 1, which remaining skills should we implement?
- **Answer**: Depends on Phase 1 feedback. Likely candidates: Architecture Skill (if file placement questions persist) or Defensive Coding Skill (if code quality issues arise).

### Q5: Command Execution Performance
- **Question**: What if `/validate-tutorial` takes too long on large tutorial directories?
- **Answer**: Add `--quick` flag to skip notebook execution for fast validation. Full validation only before commits.

### Q6: Skill Versioning Strategy
- **Question**: How do we handle breaking changes to skills?
- **Answer**: Use semantic versioning in YAML frontmatter. Document changes in `.claude/skills/CHANGELOG.md` (create as needed).

---

## Implementation Checklist

### Phase 1: Core Skills & Commands (20-24 hours)

**Week 1: Tutorial Standards Skill (5-6 hours)**
- [ ] Create `.claude/skills/tutorial-standards/` directory structure
- [ ] Write SKILL.md with activation context and instructions
- [ ] Create references/tutorial-index-template.md
- [ ] Create references/notebook-standards.md
- [ ] Create references/cross-linking-rules.md
- [ ] Copy lesson-9/TUTORIAL_INDEX.md as example
- [ ] Test activation with scenarios
- [ ] Validate guidance quality

**Week 1-2: Pattern Application Skill (4-5 hours)**
- [ ] Create `.claude/skills/pattern-application/` directory structure
- [ ] Write SKILL.md referencing /patterns/README.md
- [ ] Create references/pattern-decision-tree.md
- [ ] Create references/integration-checklist.md
- [ ] Test pattern suggestion logic
- [ ] Validate pattern templates applied correctly

**Week 2: TDD Methodology Skill (4-5 hours)**
- [ ] Create `.claude/skills/tdd-methodology/` directory structure
- [ ] Write SKILL.md referencing CLAUDE.md:33-115
- [ ] Create references/phase-rules.md
- [ ] Create references/test-naming-guide.md
- [ ] Create examples/good-tdd-session.md
- [ ] Create examples/common-violations.md
- [ ] Test RED→GREEN→REFACTOR enforcement

**Week 2: `/validate-tutorial` Command (5-6 hours)**
- [ ] Create `.claude/commands/validate-tutorial.md`
- [ ] Implement TUTORIAL_INDEX.md structure check
- [ ] Implement notebook execution check (jupyter nbconvert)
- [ ] Implement cross-link validation
- [ ] Implement Mermaid diagram syntax validation
- [ ] Implement reading time calculation
- [ ] Test with lesson-9/ tutorials
- [ ] Create error message templates

**Week 2: `/tdd` Command (2-4 hours)**
- [ ] Create `.claude/commands/tdd.md`
- [ ] Implement phase state tracking
- [ ] Implement phase transition rules
- [ ] Implement pytest auto-run after transitions
- [ ] Implement test naming validation
- [ ] Test phase enforcement

**Week 2: `/pattern` Command (3-4 hours)**
- [ ] Create `.claude/commands/pattern.md`
- [ ] Implement pattern catalog reader
- [ ] Implement pattern detail display
- [ ] Implement inline template application
- [ ] Test with all 3 patterns (TDD, ThreadPoolExecutor, ABC)

**Week 2-3: Documentation (4-6 hours)**
- [ ] Create `.claude/skills/README.md` (quick reference)
- [ ] Update CLAUDE.md with "Claude Skills System" section
- [ ] Create skill activation test suite
- [ ] Update `.claude/commands/README.md` (if exists, create if not)
- [ ] Document troubleshooting guide
- [ ] Create testing scenarios document

---

## Timeline

**Flexible Implementation (Target: 3-4 weeks)**

- **Week 1**: Tutorial Standards Skill + start Pattern Application Skill
- **Week 2**: Complete Pattern Application Skill + TDD Methodology Skill + `/validate-tutorial` command
- **Week 2-3**: `/tdd` command + `/pattern` command + Documentation
- **Week 3-4**: Testing, iteration, feedback collection

**Total Effort:** 20-24 hours (can be spread across 3-4 weeks based on availability)

---

## Approval Criteria

This PRD is approved when:
1. ✅ All functional requirements are clearly defined
2. ✅ User stories have measurable acceptance criteria
3. ✅ Success metrics are qualitative (developer feedback)
4. ✅ Non-goals explicitly exclude Phase 2 skills
5. ✅ Implementation checklist is actionable
6. ✅ Rollback strategy is documented
7. ✅ Open questions have preliminary answers

**Next Step:** Use `@generate-tasks.md` to break this PRD into actionable tasks with sub-tasks and acceptance criteria.

---

## References

- [Configuration Plan v2.0](.claude/skills/CONFIGURATION_PLAN.md)
- [CLAUDE.md Project Philosophy](../CLAUDE.md)
- [Pattern Library](../patterns/README.md)
- [Tutorial Example: Lesson 9](../lesson-9/TUTORIAL_INDEX.md)
- [Claude Code Skills Documentation](https://code.claude.com/docs/en/skills)
