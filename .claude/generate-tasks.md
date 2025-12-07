# Rule: Generating a Task List from a PRD (Pólya-Enhanced)

## Goal

To guide an AI assistant in creating a detailed, step-by-step task list in Markdown format based on an existing Product Requirements Document (PRD). This workflow applies **Pólya's problem-solving methodology** to ensure systematic understanding, strategic planning, and effective task decomposition.

## Related Documents

| Document | Purpose | When to Use |
|----------|---------|-------------|
| [@ai-dev-tasks/polya-analysis.md](../ai-dev-tasks/polya-analysis.md) | Full Pólya methodology research | Deep dive into theory and heuristics |
| [@.claude/create-prd.md](create-prd.md) | PRD creation workflow | **Upstream:** Creating the PRD this task list is based on |
| [@.claude/process-task-list.md](process-task-list.md) | Task execution workflow | **Downstream:** Executing the tasks this generates |

## Output

- **Format:** Markdown (`.md`)
- **Location:** `/tasks/`
- **Filename:** `tasks-[prd-file-name].md` (e.g., `tasks-0001-prd-user-profile-editing.md`)

---

## The 5-Phase Process (Pólya-Based)

### Phase 1: UNDERSTAND the Problem

*Core principle: "It is foolish to answer a question that you do not understand."*

**Actions:**
1. **Receive PRD Reference:** The user points the AI to a specific PRD file
2. **Read PRD Thoroughly:** Analyze functional requirements, user stories, acceptance criteria, and constraints

**Self-Interrogation Questions (ask yourself):**
- [ ] What specifically is being requested? What is the desired end state?
- [ ] What are the explicit requirements? What are the implicit expectations?
- [ ] What constraints exist (technical, time, resources, dependencies)?
- [ ] What is unclear or ambiguous? What assumptions must I make?
- [ ] Can I restate this problem in my own words?
- [ ] What would a successful outcome look like?
- [ ] Have I seen a similar problem/feature before?

**Validation Checkpoint:**
Before proceeding, confirm:
- [ ] Problem statement is clear and complete
- [ ] All constraints and requirements identified
- [ ] Ambiguities noted with reasonable assumptions stated
- [ ] Success criteria defined

---

### Phase 2: PLAN the Strategy

*Core principle: "We have a plan when we know which operations we must perform to obtain the unknown."*

**Actions:**
1. **Assess Current State:** Review the existing codebase to understand:
   - Existing infrastructure, architectural patterns, and conventions
   - Components or features that already exist and could be leveraged
   - Related files, components, and utilities that need modification

2. **Select Strategic Approach:** Choose the appropriate heuristic strategy

**Heuristic Selection Guide:**

| If the problem... | Apply this strategy |
|-------------------|---------------------|
| Is too large/complex | **Decomposition** - Break into independent components |
| Seems unfamiliar | **Analogy** - Find similar solved problems in codebase |
| Has clear goal but unclear path | **Working Backward** - Start from desired state |
| Has too many constraints | **Simplification** - Solve core case first, add constraints |
| Requires multiple approaches | **Variation** - Explore alternative solutions |

**Self-Interrogation Questions:**
- [ ] Have I solved something similar before? Can I use that method?
- [ ] What general pattern applies? (CRUD, pipeline, state machine, etc.)
- [ ] What are the major components or stages of the solution?
- [ ] What could go wrong? What are the risks?
- [ ] What tools, dependencies, or capabilities will I need?
- [ ] Should I solve a simpler version first?

**Validation Checkpoint:**
Before proceeding, confirm:
- [ ] Strategic approach selected with rationale
- [ ] Major components/stages identified
- [ ] Risks and contingencies considered
- [ ] Required resources identified

---

### Phase 3: Generate TASKS (Parent Tasks)

*Core principle: "Decompose the whole into its parts."*

**Actions:**
1. **Generate Parent Tasks:** Based on understanding and strategy, create 4-7 high-level tasks
2. **Present for Review:** Show tasks to user and wait for confirmation

**Task Quality Criteria:**
- Each task represents a **complete, deployable unit** when possible
- Tasks are **independent enough** to be worked on without blocking others
- Tasks follow a **logical dependency order**
- Each task has a **clear deliverable**

**Self-Interrogation Questions:**
- [ ] Does each task have a single, clear objective?
- [ ] Are tasks ordered by dependency (what must come first)?
- [ ] Are there any missing tasks that would leave gaps?
- [ ] Can each task be verified as complete?
- [ ] Is the granularity appropriate (not too large, not too small)?

**User Checkpoint:**
Present tasks and inform the user:
> "I have generated the high-level tasks based on the PRD using [decomposition/analogy/other] strategy. Ready to generate the sub-tasks? Respond with 'Go' to proceed, or provide feedback to adjust."

**Wait for user confirmation before proceeding.**

---

### Phase 4: Generate SUB-TASKS

*Core principle: "Check each step. Can you see clearly that the step is correct?"*

**Actions:**
1. **Decompose Each Parent Task:** Break into 2-5 actionable sub-tasks
2. **Apply Task Specification Template** for clarity

**Sub-Task Specification Template:**
```
- [ ] N.M [Clear action verb] [specific outcome]
      Input: What this needs to start
      Output: What this produces
      Verification: How to confirm success
```

**Sub-Task Quality Criteria:**
- **Actionable:** Starts with a verb (Create, Implement, Add, Configure, Test)
- **Specific:** Clear deliverable, not vague
- **Verifiable:** Has explicit success criteria
- **Independent:** Minimal coupling with sibling sub-tasks
- **Appropriately sized:** Completable in 1-4 hours typically

**Self-Interrogation Questions:**
- [ ] For each sub-task: What is the input? What is the output? What tool or action?
- [ ] What is the correct order? What depends on what?
- [ ] Is each sub-task small enough to verify easily?
- [ ] Are there validation/testing sub-tasks after implementation sub-tasks?
- [ ] How will I know each sub-task succeeded?

**Patterns for Sub-Task Types:**

| Task Type | Typical Sub-Tasks |
|-----------|-------------------|
| **New Feature** | Design interface → Write tests → Implement core → Handle edge cases → Document |
| **Bug Fix** | Reproduce issue → Identify root cause → Write failing test → Fix → Verify regression |
| **Refactor** | Identify scope → Write characterization tests → Refactor incrementally → Verify behavior preserved |
| **Integration** | Review API/schema → Create adapter → Implement connection → Error handling → Integration test |

---

### Phase 5: REFLECT and Finalize

*Core principle: "By looking back at the completed solution, they could consolidate their knowledge."*

**Actions:**
1. **Identify Relevant Files:** List files to create or modify with test files
2. **Check for Completeness:** Review against PRD requirements
3. **Generate Final Output:** Combine into final Markdown structure
4. **Save Task List:** Save to `/tasks/` directory

**Self-Interrogation Questions:**
- [ ] Does the task list cover ALL requirements from the PRD?
- [ ] Are there any edge cases or error scenarios not addressed?
- [ ] Are test files included for all implementation files?
- [ ] Is the dependency order logical and achievable?
- [ ] Would a junior developer understand what to do?

**Final Validation Checklist:**
- [ ] Every PRD requirement maps to at least one task
- [ ] Tasks follow TDD pattern where appropriate (test before implementation)
- [ ] Relevant files section is complete with descriptions
- [ ] Notes section includes any assumptions or special instructions

---

## Handling Uncertainty and Ambiguity

When encountering unclear requirements:

1. **Identify specifically** what is ambiguous
2. **Generate reasonable interpretations** (2-3 options)
3. **State chosen interpretation explicitly** in the task list
4. **Design tasks to be adaptable** if interpretation was wrong
5. **Flag for user clarification** when impact is high

**Template for documenting assumptions:**
```markdown
### Assumptions Made
- [Assumption]: [Rationale for this interpretation]
- [Assumption]: [Rationale for this interpretation]
```

---

## When to Return to Earlier Phases

Non-linear progress is expected. Return to earlier phases when:

| Signal | Action |
|--------|--------|
| Sub-tasks reveal missing parent task | Return to Phase 3 |
| Strategy doesn't fit problem structure | Return to Phase 2 |
| New information changes requirements | Return to Phase 1 |
| User feedback invalidates approach | Return to appropriate phase |

---

## Output Format

The generated task list _must_ follow this structure:

```markdown
## Relevant Files

- `path/to/potential/file1.ts` - Brief description of why this file is relevant
- `path/to/file1.test.ts` - Unit tests for `file1.ts`
- `path/to/another/file.tsx` - Brief description
- `path/to/another/file.test.tsx` - Unit tests for `another/file.tsx`

### Notes

- Unit tests should be placed alongside the code files they test
- Use `pytest [path]` or `npx jest [path]` to run tests
- [Any assumptions made during task generation]

### Assumptions Made

- [Assumption 1]: [Rationale]
- [Assumption 2]: [Rationale]

## Tasks

- [ ] 1.0 Parent Task Title
  - [ ] 1.1 [Sub-task with clear action verb and outcome]
  - [ ] 1.2 [Sub-task with clear action verb and outcome]
  - [ ] 1.3 Write tests for [component] - validates [specific behavior]
- [ ] 2.0 Parent Task Title
  - [ ] 2.1 [Sub-task description]
  - [ ] 2.2 [Sub-task description]
- [ ] 3.0 Testing and Validation
  - [ ] 3.1 Run full test suite and fix failures
  - [ ] 3.2 Manual testing of [key user flows]
```

---

## Interaction Model

The process requires **two user checkpoints**:

1. **After Phase 3 (Parent Tasks):** User confirms high-level approach
2. **After Phase 5 (Final Output):** User reviews complete task list

This ensures alignment before investing effort in detailed decomposition.

---

## Target Audience

Assume the primary reader is a **junior developer** who:
- Has awareness of the existing codebase context
- Benefits from explicit success criteria
- Needs clear dependency ordering
- Appreciates actionable, specific instructions

---

## Quick Reference: Pólya's Questions

**Understanding:** What is unknown? What are the data? What is the condition?

**Planning:** Have I seen this before? What pattern applies? Should I solve a simpler version first?

**Decomposing:** What are the parts? What depends on what? Is each part verifiable?

**Executing:** Can I see clearly that each step is correct? Am I still on track?

**Reflecting:** Does output satisfy requirements? What would I do differently? What's reusable?

---

## Quick Reference Card

### Phase Checklist (Copy-Paste Ready)

```markdown
### Phase Checklist

- [ ] **Phase 1: UNDERSTAND** — Read PRD, identify requirements, constraints, unknowns
- [ ] **Phase 2: PLAN** — Select heuristic strategy, assess codebase, identify components
- [ ] **Phase 3: TASKS** — Generate 4-7 parent tasks, present for user approval
- [ ] **Phase 4: SUB-TASKS** — Decompose into 2-5 actionable sub-tasks per parent
- [ ] **Phase 5: REFLECT** — Validate against PRD, list files, save to `/tasks/`
```

### Heuristic Selection Matrix

| Problem Characteristic | Strategy | Action |
|------------------------|----------|--------|
| Too large/complex | **Decomposition** | Break into independent components |
| Seems unfamiliar | **Analogy** | Find similar solved problem in codebase |
| Clear goal, unclear path | **Working Backward** | Start from desired end state |
| Too many constraints | **Simplification** | Solve core case first |
| Multiple possible approaches | **Variation** | Explore 2-3 alternatives |

### Task Quality Quick Check

| ✅ Good Task | ❌ Poor Task |
|-------------|--------------|
| "Create user authentication service with JWT" | "Build login" |
| "Write unit tests for payment validation" | "Add tests" |
| "Implement error handling for API timeouts" | "Handle errors" |
| Clear deliverable, verifiable outcome | Vague, no success criteria |

### Sub-Task Patterns by Type

| Task Type | Pattern |
|-----------|---------|
| **New Feature** | Design → Test → Implement → Edge cases → Document |
| **Bug Fix** | Reproduce → Root cause → Failing test → Fix → Verify |
| **Refactor** | Characterization test → Refactor → Verify behavior |
| **Integration** | Review API → Adapter → Connection → Error handling → Test |

---

## Worked Example: PRD Decomposition

This example demonstrates the 5-phase process using PRD `0013-prd-polya-enhanced-prd-creation.md`.

### Phase 1: UNDERSTAND

**Self-interrogation:**
- **What is requested?** Enhance PRD creation with Pólya methodology — two deliverables: skill file + template update
- **Key constraints?** <500 lines for skill file, must remain compatible with existing workflow
- **Success criteria?** 50% more specific questions, >90% gate confirmation rate, <10% follow-up clarifications
- **Assumptions?** Using Claude Code skill format, English only, no external dependencies

**Understanding Summary:**
> Create a structured problem-solving enhancement for PRD creation using Pólya's 5-phase methodology. Requires a reusable skill file and an updated template with validation gates.

### Phase 2: PLAN

**Strategic approach assessment:**
- **Similar problem?** Yes — existing `create-prd.md` provides base template pattern
- **Applicable heuristic:** **Decomposition** — Two distinct deliverables (skill file + template)
- **Secondary heuristic:** **Progressive Disclosure** — Core template imports detailed methodology
- **Major components:** Skill file, template update, question sets, gate templates
- **Risk:** Import syntax must work with Claude Code skill loading

**Selected Strategy:** Decomposition + Progressive Disclosure
> Develop skill file first (complete methodology), then update template to import it. Keep template under 100 lines.

### Phase 3: TASKS (Parent Tasks)

```markdown
## Tasks

- [ ] 1.0 Create Pólya Planning Skill File Structure
- [ ] 2.0 Implement 5-Phase Methodology Documentation
- [ ] 3.0 Build Heuristic Strategy Catalog
- [ ] 4.0 Create Validation Gate Templates
- [ ] 5.0 Update create-prd.md Template
- [ ] 6.0 Testing and Validation
```

**User Checkpoint:**
> "I have generated 6 high-level tasks using the Decomposition strategy. Ready to generate sub-tasks? Respond with 'Go' to proceed."

### Phase 4: SUB-TASKS (After User Approval)

```markdown
## Tasks

- [ ] 1.0 Create Pólya Planning Skill File Structure
  - [ ] 1.1 Create `.claude/skills/polya-planning/` directory
        Input: None | Output: Directory created | Verify: `ls` confirms path
  - [ ] 1.2 Create SKILL.md with YAML frontmatter (name, version, description)
        Input: Skill spec | Output: Valid YAML header | Verify: Skill loads without error
  - [ ] 1.3 Write overview section mapping Pólya to 5-phase workflow
        Input: polya-analysis.md | Output: ~50 line overview | Verify: Covers all 5 phases

- [ ] 2.0 Implement 5-Phase Methodology Documentation
  - [ ] 2.1 Document Phase 1 (UNDERSTAND) with question sets for Simple/Medium/Complex
        Input: FR-2 requirements | Output: Question sets | Verify: 3-4/5-7/8-10+ questions per level
  - [ ] 2.2 Document Phase 2 (PLAN) with strategic questions and heuristic triggers
        Input: FR-3 requirements | Output: Planning section | Verify: All 5 heuristics documented
  - [ ] 2.3 Document Phase 3 (TASKS) with decomposition patterns
        Input: Task type patterns | Output: Task section | Verify: 4 task types covered
  - [ ] 2.4 Document Phase 4 (EXECUTE) with step verification prompts
        Input: Pólya Phase 3 | Output: Execute section | Verify: Check-as-you-go pattern
  - [ ] 2.5 Document Phase 5 (REFLECT) with validation structure
        Input: Pólya Phase 4 | Output: Reflect section | Verify: Includes generalization

- [ ] 3.0 Build Heuristic Strategy Catalog
  - [ ] 3.1 Document each heuristic (Decomposition, Analogy, Working Backward, Simplification, Auxiliary)
        Input: FR-3.2 table | Output: 5 heuristic entries | Verify: Each has When/Method/Watch-for
  - [ ] 3.2 Add trigger conditions for heuristic selection
        Input: polya-analysis.md | Output: Decision matrix | Verify: Clear selection criteria

- [ ] 4.0 Create Validation Gate Templates
  - [ ] 4.1 Design Gate template format (summary + confirmation options)
        Input: FR-4.2 | Output: Template | Verify: Includes ✅/🔄/⬅️ options
  - [ ] 4.2 Create Gate 1 (Understanding), Gate 2 (Approach), Gate 3 (PRD Review) templates
        Input: Gate template | Output: 3 gates | Verify: Each has phase-specific summary points

- [ ] 5.0 Update create-prd.md Template
  - [ ] 5.1 Add `@polya-planning` import reference at top
        Input: Skill file path | Output: Import statement | Verify: Skill loads when referenced
  - [ ] 5.2 Update conversation flow to include 3 validation gates
        Input: Gate templates | Output: Flow diagram | Verify: Gates at correct transitions
  - [ ] 5.3 Update PRD output structure with new sections (Problem Understanding, Strategic Approach)
        Input: FR-7 | Output: Template sections | Verify: All required fields present

- [ ] 6.0 Testing and Validation
  - [ ] 6.1 Test skill file loads correctly with `@polya-planning` syntax
        Input: Skill file | Output: Load confirmation | Verify: No syntax errors
  - [ ] 6.2 Validate against PRD requirements (all FRs covered)
        Input: PRD FRs | Output: Coverage checklist | Verify: 100% FR coverage
  - [ ] 6.3 Run through example PRD creation to test workflow
        Input: Sample feature request | Output: Complete PRD | Verify: All gates trigger correctly
```

### Phase 5: REFLECT

**Validation against PRD:**
- [x] FR-1 (Complexity Assessment) → Covered in Phase 1 understanding
- [x] FR-2 (UNDERSTAND Questions) → Task 2.1
- [x] FR-3 (PLAN Questions + Heuristics) → Tasks 2.2, 3.0
- [x] FR-4 (Validation Gates) → Task 4.0
- [x] FR-5 (Heuristic Documentation) → Task 3.0
- [x] FR-6 (Non-Linear Support) → Documented in skill file
- [x] FR-7 (PRD Output Structure) → Task 5.3
- [x] FR-8 (Skill File Structure) → Task 1.0

**Relevant Files:**
```markdown
## Relevant Files

- `.claude/skills/polya-planning/SKILL.md` - Main skill file with 5-phase methodology
- `.claude/create-prd.md` - Enhanced PRD template with validation gates
- `.claude/create-prd.md.test.md` - (Optional) Test scenarios for workflow validation

### Notes
- Skill file should stay under 500 lines; use references/ if needed
- Template imports skill via `@.claude/skills/polya-planning/SKILL.md`
- Test by creating a sample PRD after implementation
```

**Lessons for Future:**
- Decomposition + Progressive Disclosure combination works well for "framework + implementation" patterns
- Validation gates map naturally to phase transitions
- Sub-task Input/Output/Verify format improves clarity

---

## Reusable Pattern: Pólya-Enhanced Workflow

The 5-phase structure (Understand → Plan → Tasks → Execute → Reflect) with self-interrogation questions and validation checkpoints is **generalizable** beyond task generation:

| Application Domain | Understand | Plan | Tasks | Execute | Reflect |
|--------------------|------------|------|-------|---------|---------|
| **Task Generation** | Parse PRD | Select heuristic | Decompose to tasks | Generate sub-tasks | Validate coverage |
| **Code Review** | Read PR diff | Identify review focus | Create checklist | Review each file | Summarize findings |
| **Debugging** | Reproduce bug | Form hypothesis | Plan investigation | Test hypothesis | Document fix |
| **Architecture Design** | Gather requirements | Evaluate patterns | Define components | Design interfaces | Review trade-offs |
| **Documentation** | Identify audience | Structure content | Outline sections | Write content | Review completeness |

**Key Transferable Elements:**
1. **Self-interrogation prompts** at each phase
2. **Validation checkpoints** between phases
3. **Heuristic strategies** for when stuck
4. **Non-linear phase support** (return to earlier phases)
5. **User confirmation gates** at critical transitions
