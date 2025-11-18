# Task List: Claude Skills Configuration System

**Source PRD:** `tasks/0001-prd-claude-skills-configuration.md`
**Generated:** 2025-11-18
**Target:** Phase 1 Implementation (20-24 hours)

---

## Relevant Files

### Skills Directory Structure
- `.claude/skills/README.md` - Quick reference guide for all skills, activation contexts, troubleshooting
- `.claude/skills/tutorial-standards/SKILL.md` - Tutorial quality enforcement skill
- `.claude/skills/tutorial-standards/references/tutorial-index-template.md` - Required TUTORIAL_INDEX.md sections
- `.claude/skills/tutorial-standards/references/notebook-standards.md` - Jupyter notebook quality standards
- `.claude/skills/tutorial-standards/references/cross-linking-rules.md` - Relative path conventions for tutorials
- `.claude/skills/tutorial-standards/examples/lesson-9-tutorial-index.md` - Reference implementation (copy from lesson-9/)
- `.claude/skills/tdd-methodology/SKILL.md` - TDD workflow enforcement skill
- `.claude/skills/tdd-methodology/references/phase-rules.md` - RED/GREEN/REFACTOR phase constraints
- `.claude/skills/tdd-methodology/references/test-naming-guide.md` - Test naming convention documentation
- `.claude/skills/tdd-methodology/examples/good-tdd-session.md` - Example TDD workflow from codebase
- `.claude/skills/tdd-methodology/examples/common-violations.md` - Anti-patterns to avoid
- `.claude/skills/pattern-application/SKILL.md` - Pattern library application skill
- `.claude/skills/pattern-application/references/pattern-decision-tree.md` - When to use which pattern
- `.claude/skills/pattern-application/references/integration-checklist.md` - Steps for applying patterns

### Commands
- `.claude/commands/validate-tutorial.md` - Tutorial validation command (TUTORIAL_INDEX check, notebook execution, cross-links, Mermaid diagrams, reading time)
- `.claude/commands/tdd.md` - TDD phase tracker command (red/green/refactor state management)
- `.claude/commands/pattern.md` - Pattern discovery and application command

### Testing & Validation
- `tests/test_skills_activation.py` - Skill activation test scenarios (if needed for automation)
- `.claude/skills/TESTING_SCENARIOS.md` - Manual testing checklist for skill activation

### Documentation Updates
- `CLAUDE.md` - Add "Claude Skills System" section (concise, link to skills README)
- `.claude/commands/README.md` - Update with new command documentation (create if doesn't exist)

### Notes

- Skills use YAML frontmatter in SKILL.md files for metadata (name, description, version, activation_context, references)
- All skills should **reference** existing documentation (CLAUDE.md, patterns/) rather than duplicating content
- Commands are invoked manually with `/command-name` syntax
- Skills activate automatically based on conversation context (LLM reasoning)
- Test each skill in isolation before moving to next skill
- Use lesson-9/TUTORIAL_INDEX.md as the gold standard tutorial example

---

## Tasks

### 1.0 Skills Infrastructure & Foundation Setup
- [x] 1.0 Skills Infrastructure & Foundation Setup
  - [x] 1.1 Create `.claude/skills/` directory structure with README.md placeholder
  - [x] 1.2 Document SKILL.md YAML frontmatter format (name, description, version, activation_context, references)
  - [x] 1.3 Create `.claude/skills/TESTING_SCENARIOS.md` with activation testing template
  - [x] 1.4 Set up skill isolation testing workflow (test one skill at a time before activation)
  - [x] 1.5 Create quality validation checklist for skills (YAML validity, reference existence, no content duplication)
  - [x] 1.6 **BASELINE SNAPSHOT** - Quick qualitative snapshot before implementing skills (2 hours)
    - Review git log from last 2 weeks: Count instances of "where should I create" questions in commit messages/PRs
    - Scan recent commits: Identify 3-5 examples where tests were written AFTER implementation (TDD violations)
    - Manually validate lesson-9/ once: Time the validation process (TUTORIAL_INDEX check, notebook execution, cross-links)
    - Review last 5 merged tutorials: Count broken links, execution errors, missing sections
    - Quick code review of 2-3 recent functions: Note if they use patterns from `/patterns/` directory
    - Document snapshot in `.claude/skills/BASELINE_SNAPSHOT.md` (1-page summary, not comprehensive metrics)
    - **Rationale:** Lightweight "before state" sufficient for qualitative Phase 1 validation; detailed metrics deferred to Phase 2

### 2.0 Tutorial Standards Skill Implementation
- [x] 2.0 Tutorial Standards Skill Implementation
  - [x] 2.1 Create `.claude/skills/tutorial-standards/` directory structure
  - [x] 2.2 Write SKILL.md with YAML frontmatter (activation_context: "create tutorial", "TUTORIAL_INDEX", "add notebook", "write lesson")
  - [x] 2.3 Create `references/tutorial-index-template.md` documenting required TUTORIAL_INDEX.md sections (objectives, prerequisites, learning paths, FAQs)
  - [x] 2.4 Create `references/notebook-standards.md` documenting Jupyter notebook requirements (setup cell, cost warning, <5min execution, validation assertions)
  - [x] 2.5 Create `references/cross-linking-rules.md` documenting relative path conventions for tutorial navigation
  - [x] 2.6 Copy `lesson-9/TUTORIAL_INDEX.md` to `examples/lesson-9-tutorial-index.md` as reference implementation
  - [x] 2.7 Add reference to CLAUDE.md:347-435 (Tutorial Workflow section) in SKILL.md
  - [x] 2.8 Test skill activation with scenarios: "create tutorial", "add notebook", "missing TUTORIAL_INDEX"
  - [x] 2.9 Validate skill provides correct guidance without duplicating CLAUDE.md content

### 3.0 TDD Methodology & Pattern Application Skills
- [ ] 3.0 TDD Methodology & Pattern Application Skills
  - [ ] 3.1 Create `.claude/skills/tdd-methodology/` directory structure
  - [ ] 3.2 Write TDD SKILL.md with YAML frontmatter (activation_context: "write test", "implement function", "add feature", "refactor", "TDD")
  - [ ] 3.3 Create `references/phase-rules.md` documenting RED/GREEN/REFACTOR phase constraints
  - [ ] 3.4 Create `references/test-naming-guide.md` documenting `test_should_[result]_when_[condition]()` convention
  - [ ] 3.5 Create `examples/good-tdd-session.md` with real TDD workflow from codebase (reference tests/test_*.py)
  - [ ] 3.6 Create `examples/common-violations.md` documenting anti-patterns (implementation before test, modifying tests during GREEN phase)
  - [ ] 3.7 Add reference to CLAUDE.md:33-115 (TDD Mode section) in SKILL.md
  - [ ] 3.8 Test TDD skill activation with scenarios: "write test", "implement feature", "refactor code"
  - [ ] 3.9 Create `.claude/skills/pattern-application/` directory structure
  - [ ] 3.10 Write Pattern SKILL.md with YAML frontmatter (activation_context: "parallel processing", "batch", "concurrent", "abstract base class", "interface", "framework")
  - [ ] 3.11 Create `references/pattern-decision-tree.md` mapping use cases to patterns (I/O-bound → ThreadPoolExecutor, framework → ABC, new feature → TDD)
  - [ ] 3.12 Create `references/integration-checklist.md` documenting steps for applying pattern templates (copy template, add defensive coding, reference pattern file)
  - [ ] 3.13 Add reference to patterns/README.md in Pattern SKILL.md
  - [ ] 3.14 Test Pattern skill activation with scenarios: "batch processing", "create framework", "parallel API calls"
  - [ ] 3.15 **INTEGRATION TESTING** - Validate TDD + Pattern skills work together without conflicts
    - Test scenario 1: "Implement parallel processing for API calls" → Both TDD skill (test-first) AND Pattern skill (ThreadPoolExecutor) should activate
    - Test scenario 2: "Refactor this code using Abstract Base Class" → Pattern skill activates, TDD skill allows REFACTOR phase
    - Test scenario 3: "Write test for batch processing function" → TDD skill activates (RED phase), Pattern skill does NOT interfere
    - Validate activation contexts don't overlap incorrectly (e.g., "test" keyword shouldn't trigger Pattern skill)
    - Document expected multi-skill activation behavior in `.claude/skills/TESTING_SCENARIOS.md`
    - **Rationale:** Prevents skill conflicts that would confuse Claude or provide contradictory guidance

### 4.0 Slash Commands Suite Implementation
- [ ] 4.0 Slash Commands Suite Implementation
  - [ ] 4.0.5 **BASELINE VALIDATION** - Establish lesson-9/ as gold standard before implementing /validate-tutorial
    - Manually validate lesson-9/TUTORIAL_INDEX.md structure (verify has all required sections)
    - Execute all lesson-9/ notebooks manually (jupyter nbconvert --execute) and document expected execution time
    - Check all cross-links in lesson-9/ tutorials manually (verify relative paths resolve correctly)
    - Validate all Mermaid diagrams in lesson-9/ (parse .mmd files, confirm valid syntax)
    - Calculate current reading time for lesson-9/ tutorials (word count ÷ 200 WPM)
    - Document expected outputs in `.claude/commands/validate-tutorial-expected-output.md` (this becomes test oracle)
    - **Dependency:** This MUST complete before Task 4.8 (testing /validate-tutorial command)
  - [ ] 4.1 Create `.claude/commands/validate-tutorial.md` with command structure (usage, parameters, output format)
  - [ ] 4.2 Implement TUTORIAL_INDEX.md structure validation (check required sections: objectives, prerequisites, learning paths, FAQs)
  - [ ] 4.3 Implement notebook execution check using `jupyter nbconvert --execute` with <5min timeout
  - [ ] 4.4 Implement cross-link validation (verify relative paths resolve correctly)
  - [ ] 4.5 Implement Mermaid diagram syntax validation (parse .mmd files for syntax errors)
  - [ ] 4.6 Implement reading time calculation (word count ÷ 200 WPM, target 15-30 min)
  - [ ] 4.7 Create ✅/❌ report template with actionable fix suggestions
  - [ ] 4.7.1 **ERROR HANDLING** - Graceful failure for /validate-tutorial edge cases
    - Handle missing directory: Return actionable error "Directory not found: [path]. Did you mean lesson-9/?"
    - Handle timeout during notebook execution (>5min): Skip notebook with warning "⏱️ Notebook exceeded timeout, skipping execution check"
    - Handle missing jupyter dependency: Return "❌ jupyter nbconvert not found. Install with: pip install jupyter nbconvert"
    - Handle broken Mermaid syntax: Report specific line number and syntax error from parser
    - Handle permission errors: Return "❌ Permission denied reading [file]. Check file permissions."
    - Create error handling test suite in `tests/test_validate_tutorial_errors.py`
    - **Rationale:** Commands must never crash; users need actionable error messages to fix issues
  - [ ] 4.8 Test `/validate-tutorial` command with lesson-9/ as reference (should pass all checks)
  - [ ] 4.9 Create `.claude/commands/tdd.md` with phase state tracking (RED/GREEN/REFACTOR)
  - [ ] 4.10 Implement `/tdd red` - Enter RED phase, provide guidance reminder: "Write failing test. No implementation code."
  - [ ] 4.11 Implement `/tdd green` - Enter GREEN phase, provide guidance reminder: "Minimal code to pass test. No test modifications."
  - [ ] 4.12 Implement `/tdd refactor` - Enter REFACTOR phase, auto-run pytest after changes, remind: "Improve code quality. Keep tests passing."
  - [ ] 4.13 Implement `/tdd status` - Display current phase and phase-specific guidance (NOT enforcement rules)
  - [ ] 4.14 Test `/tdd` command phase transitions with pytest integration
  - [ ] 4.14.1 **CLARIFICATION** - /tdd command provides GUIDANCE, tdd-methodology skill provides ENFORCEMENT
    - Command behavior: Displays phase-specific reminders and best practices when user invokes `/tdd [phase]`
    - Skill behavior: Automatically activates during development to enforce TDD workflow (blocks violations)
    - Relationship: Command is manual "what should I do now?", Skill is automatic "you must follow this rule"
    - Update command documentation to clarify it's a guidance tool, not a blocker
    - **Rationale:** Commands should help users, not restrict them; skills handle enforcement
  - [ ] 4.15 Create `.claude/commands/pattern.md` for pattern discovery and application
  - [ ] 4.16 Implement `/pattern` - List all patterns from patterns/README.md with complexity ratings
  - [ ] 4.17 Implement `/pattern [name]` - Show pattern details (use case, complexity, examples, file:line references)
  - [ ] 4.18 Implement `/pattern [name] apply` - Copy template to inline application with defensive coding
  - [ ] 4.19 Test `/pattern` command with all 3 patterns (TDD, ThreadPoolExecutor, ABC)

### 5.0 Testing & Quality Validation
- [ ] 5.0 Testing & Quality Validation
  - [ ] 5.1 Populate `.claude/skills/TESTING_SCENARIOS.md` with test cases for each skill (tutorial-standards, tdd-methodology, pattern-application)
  - [ ] 5.2 Test tutorial-standards skill: activation on "create tutorial", guidance includes TUTORIAL_INDEX template, references CLAUDE.md correctly
  - [ ] 5.3 Test TDD skill: activation on "write test", enforces RED→GREEN→REFACTOR phases, provides test naming guidance
  - [ ] 5.4 Test Pattern skill: activation on "batch processing", suggests correct pattern (ThreadPoolExecutor), references patterns/README.md
  - [ ] 5.5 Validate all SKILL.md files have valid YAML frontmatter (parse with YAML parser)
  - [ ] 5.6 Validate all reference files exist and are linked correctly in SKILL.md
  - [ ] 5.7 Validate all examples have file:line references to real codebase files
  - [ ] 5.8 Validate skills reference CLAUDE.md/patterns/ instead of duplicating content (manual review)
  - [ ] 5.9 Test edge cases: skill conflicts (multiple skills activating), missing references, broken activation contexts
  - [ ] 5.10 Run full quality checklist from PRD FR-10 (YAML validity, reference existence, no duplication, passing test scenarios)

### 6.0 Documentation, Integration & Rollout
- [ ] 6.0 Documentation, Integration & Rollout
  - [ ] 6.1 Write `.claude/skills/README.md` with quick reference table (skill name, activation context, purpose, file path)
  - [ ] 6.2 Document skill activation logic (keyword matching, automatic vs manual, multiple skills can activate)
  - [ ] 6.3 Create troubleshooting guide for skill activation issues (not activating, wrong guidance, conflicts)
  - [ ] 6.4 Add usage examples for each skill ("When you say X, skill Y activates and provides Z guidance")
  - [ ] 6.5 Update CLAUDE.md with "Claude Skills System" section (concise overview, link to .claude/skills/README.md)
  - [ ] 6.6 Create `.claude/commands/README.md` if doesn't exist, or update existing with new commands (validate-tutorial, tdd, pattern)
  - [ ] 6.7 Document command usage examples, parameters, output formats, integration with existing tools (pytest, jupyter)
  - [ ] 6.8 **ROLLBACK STRATEGY DOCUMENTATION** - Comprehensive plan for disabling/reverting skills if issues arise
    - Document immediate skill disabling: `mv .claude/skills/skill-name .claude/skills/_DISABLED_skill-name` (skill stops activating immediately)
    - Document git-based rollback: `git revert <commit>` or `git checkout <previous-version>` for skill files
    - Create troubleshooting decision tree: "When to disable vs. fix vs. rollback"
    - Document skill conflict resolution: if multiple skills activate incorrectly, which to disable first (priority order)
    - Create skill activation log format: how to capture which skills activated in session (for debugging)
    - Add version control best practices: semantic versioning in YAML frontmatter, CHANGELOG per skill
    - Document testing after rollback: verification checklist to ensure system returns to stable state
    - Reference Configuration Plan:856-879 for detailed rollback procedures
  - [ ] 6.9 Create skill versioning strategy documentation (semantic versioning in YAML frontmatter)
  - [ ] 6.10 Test full workflow: start new Claude session, verify skills activate correctly, test all 3 commands
  - [ ] 6.11 Document success metrics collection plan (qualitative feedback template for 2-week assessment)
    - Create `.claude/skills/PHASE1_FEEDBACK_TEMPLATE.md` with structured questions
    - Include questions from PRD:328-358:
      - "Are you repeating yourself less across sessions?" (Session Efficiency)
      - "Are tutorials breaking less often?" (Tutorial Quality)
      - "Are you using documented patterns more consistently?" (Pattern Usage)
      - "Are you writing tests before implementation?" (TDD Compliance)
      - "Do skills activate at the right times?" (Skill Activation Quality)
      - "Are the new commands useful?" (Command Utility)
      - "Has the Skills system improved your workflow?" (Overall Experience)
    - Add qualitative response scale: "Yes, significantly" / "Somewhat" / "No change" / "Worse"
    - Include open-ended section: "What would make skills more useful?"
    - Set collection timeline: 2 weeks after Phase 1 completion
    - **Rationale:** Concrete feedback questions ensure actionable insights for Phase 2 go/no-go decision
  - [ ] 6.12 **PHASE 2 INITIATION CHECKLIST** - Minimal go/no-go criteria (30 min task, not detailed planning)
    - Create `.claude/skills/PHASE2_INITIATION.md` with single-page checklist
    - List 3 deferred skills: Architecture, Defensive Coding, Bhagavad Gita Domain (reference Configuration Plan for details)
    - List 2 deferred commands: /skill-test, Additional slots (reference Configuration Plan for details)
    - Define go/no-go criteria: ✅ Skills activate correctly (>80%), ✅ User feedback positive, ✅ No critical Phase 1 issues
    - Note: Detailed Phase 2 PRD will be created AFTER Phase 1 validation, not during Phase 1
    - **Rationale:** Avoid cognitive overhead of detailed Phase 2 planning during Phase 1 implementation; focus on current work

---

## Phase 1 Deliverables

**Skills:** 3 core skills (tutorial-standards, tdd-methodology, pattern-application)
**Commands:** 3 slash commands (validate-tutorial, tdd, pattern)
**Documentation:** Skills README, updated CLAUDE.md, testing scenarios, commands README
**Validation:** All skills tested with activation scenarios, quality checklist passed (FR-10)
**Total Sub-Tasks:** 66 actionable items across 6 parent tasks (updated with critical gap fixes)

---

## Implementation Sequence

**Week 1 (Tasks 1.0-2.0):** Infrastructure + Tutorial Standards Skill (10-12 hours)
**Week 2 (Tasks 3.0-4.0):** TDD/Pattern Skills + All Commands (12-14 hours)
**Week 3 (Tasks 5.0-6.0):** Testing, Validation, Documentation (8-10 hours)

**Total Effort:** 30-36 hours (flexible timeline, can be spread across 3-4 weeks)
