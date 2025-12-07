# PRD: Pólya-Enhanced PRD Creation Skill

**Document ID:** 0013-prd-polya-enhanced-prd-creation
**Version:** 1.0.0
**Created:** 2025-12-05
**Status:** Draft

---

## 1. Introduction/Overview

This PRD defines an enhancement to Claude's PRD creation workflow by integrating George Pólya's problem-solving methodology from "How to Solve It" (1945). The enhancement transforms the existing linear PRD creation process into a structured 5-phase workflow with adaptive questioning depth, explicit validation gates, and heuristic strategy recommendations.

### Problem Statement

The current `create-prd.md` provides basic clarifying questions but lacks:
- **Systematic self-interrogation** techniques that drive deep problem understanding
- **Adaptive depth** based on problem complexity
- **Explicit phase transitions** with validation gates
- **Heuristic strategy recommendations** for implementation guidance
- **Non-linear phase support** (returning to earlier phases when stuck)

### Solution

Create a two-part enhancement:
1. **Enhanced `create-prd.md`** — Updated template integrating Pólya phases with complexity assessment and validation gates
2. **`polya-planning.md` skill file** — Reusable skill with full methodology, question sets, and heuristic catalog

---

## 2. Goals

| # | Goal | Success Indicator |
|---|------|-------------------|
| G1 | Improve requirement elicitation quality | 50% more specific questions asked per PRD |
| G2 | Adapt to problem complexity | Lightweight for simple, comprehensive for complex |
| G3 | Establish validation gates | User confirms understanding at each phase transition |
| G4 | Surface heuristic strategies | PRD includes implementation approach guidance |
| G5 | Enable non-linear workflows | Support returning to earlier phases when needed |
| G6 | Maintain junior developer accessibility | PRDs remain clear and actionable |

---

## 3. User Stories

### US-1: Development Team Lead
**As a** development team lead,
**I want** Claude to ask deeper, more structured questions when creating PRDs,
**So that** requirements are thoroughly understood before implementation begins.

**Acceptance Criteria:**
- Claude uses Pólya's systematic questioning (What is unknown? What are constraints? What does success look like?)
- Questions adapt based on problem complexity
- Problem understanding is validated before moving to requirements

### US-2: Product Manager
**As a** product manager,
**I want** explicit confirmation points during PRD creation,
**So that** I can validate Claude's understanding at each phase before proceeding.

**Acceptance Criteria:**
- 3 explicit gates: after understanding, after planning, before saving
- Each gate shows a summary and asks for confirmation
- Option to return to earlier phase at each gate

### US-3: Developer
**As a** developer receiving PRDs,
**I want** the PRD to include recommended problem-solving strategies,
**So that** I have guidance on how to approach implementation.

**Acceptance Criteria:**
- PRD Technical Considerations includes applicable heuristics
- Each heuristic has rationale for why it applies
- Strategies like decomposition, analogy, working backward are included

### US-4: Team Member (Simple Feature)
**As a** team member requesting a simple feature,
**I want** Claude to recognize simplicity and ask only essential questions,
**So that** PRD creation doesn't take unnecessarily long.

**Acceptance Criteria:**
- Claude assesses complexity (Simple/Medium/Complex)
- Simple features: 3-4 focused questions per phase
- User confirms complexity assessment

### US-5: Team Member (Complex System)
**As a** team member requesting a complex system,
**I want** Claude to thoroughly explore all aspects,
**So that** nothing is missed in the requirements.

**Acceptance Criteria:**
- Complex systems: 8-10+ questions with sub-questions
- Multiple strategic approaches explored
- Heuristic strategies explicitly recommended

---

## 4. Functional Requirements

### FR-1: Complexity Assessment

**FR-1.1** Claude MUST assess problem complexity after initial prompt using these criteria:

| Complexity | Characteristics |
|------------|-----------------|
| **Simple** | Single component, clear outcome, <2 day implementation |
| **Medium** | Multiple components, some ambiguity, 1-2 week implementation |
| **Complex** | System-level, significant ambiguity, multi-week implementation |

**FR-1.2** Claude MUST explicitly state assessed complexity and ask user to confirm or adjust before proceeding.

**FR-1.3** Complexity assessment MUST influence question depth in subsequent phases.

### FR-2: UNDERSTAND Phase Questioning

**FR-2.1** Claude MUST ask questions from these Pólya categories:
- What is the unknown/desired outcome?
- What are the data/constraints/given information?
- What is unclear or ambiguous?
- Can you restate the problem in your own words?
- What would success look like?
- Have you seen a similar problem before?

**FR-2.2** Question depth MUST adapt to complexity:

| Complexity | Questions | Format |
|------------|-----------|--------|
| Simple | 3-4 focused | Single list |
| Medium | 5-7 covering core categories | Grouped by category |
| Complex | 8-10+ with sub-questions | Multiple rounds possible |

**FR-2.3** Questions MUST be offered as numbered/lettered lists for easy response.

### FR-3: PLAN Phase Questioning

**FR-3.1** Claude MUST explore:
- Similar problems or patterns that apply
- Strategic approaches (and alternatives for complex problems)
- Major components or stages of the solution
- Potential risks and mitigation strategies

**FR-3.2** For Medium/Complex problems, Claude MUST suggest applicable heuristic strategies:

| Heuristic | When to Apply | Agent Application |
|-----------|---------------|-------------------|
| **Decomposition** | Problem too large to solve directly | Break into independent sub-problems |
| **Analogy** | Problem seems unfamiliar | Pattern-match to previously solved problems |
| **Working Backward** | Goal is clear but path is not | Start from desired end state |
| **Simplification** | Too many constraints | Solve simpler version first, add constraints |
| **Auxiliary Problem** | Stuck on main problem | Solve helper problem to unblock |

**FR-3.3** Each heuristic suggestion MUST include:
- Strategy name
- Why it applies to this specific problem
- Suggested approach outline

### FR-4: Validation Gates

**FR-4.1** Claude MUST pause for user confirmation at these transitions:

| Gate | After Phase | Purpose |
|------|-------------|---------|
| GATE 1 | Understand | "Confirm I understand the problem correctly before planning" |
| GATE 2 | Plan | "Confirm the strategic approach before detailing requirements" |
| GATE 3 | Draft PRD | "Confirm this PRD captures our discussions before saving" |

**FR-4.2** Gate format MUST include:
- Summary of current phase conclusions (3-5 bullet points)
- Explicit confirmation request: "Does this accurately capture [understanding/approach/requirements]?"
- Option to return to earlier phase: "If anything needs adjustment, we can revisit [earlier phase]."

**FR-4.3** Claude MUST NOT proceed to next phase without explicit user confirmation.

### FR-5: Heuristic Strategy Documentation in PRD

**FR-5.1** PRD Technical Considerations section MUST include a "Recommended Implementation Strategies" subsection.

**FR-5.2** Each strategy recommendation MUST include:
```markdown
**Strategy: [Name]**
- **Why it applies:** [Specific reason for this problem]
- **Suggested approach:** [1-3 sentence outline]
- **Watch for:** [Common pitfall to avoid]
```

**FR-5.3** At least 2 strategies MUST be included for Medium/Complex problems.

### FR-6: Non-Linear Phase Support

**FR-6.1** Claude MUST recognize when to suggest returning to an earlier phase:
- New information contradicts previous understanding
- Current approach isn't working after reasonable exploration
- User indicates confusion or misalignment

**FR-6.2** When suggesting phase regression, Claude MUST:
- Explain why (what new information or issue triggered the regression)
- Specify which phase to return to
- Summarize what needs reconsideration

**FR-6.3** User MAY explicitly request returning to any previous phase at any time.

### FR-7: Enhanced PRD Output Structure

**FR-7.1** Enhanced PRD MUST include standard sections plus:

| New Section | Location | Content |
|-------------|----------|---------|
| **Problem Understanding** | After Introduction | Summary of UNDERSTAND phase conclusions |
| **Strategic Approach** | After Goals | Summary of PLAN phase including heuristics |
| **Validation Checkpoints** | In Technical Considerations | Suggested verification points during implementation |

**FR-7.2** Problem Understanding section MUST include:
- Restated problem in Claude's words
- Key constraints identified
- Assumptions made (if any)
- Success criteria

### FR-8: Skill File Structure

**FR-8.1** Separate `polya-planning.md` skill file MUST include:
- YAML frontmatter (name, version, description, activation_context)
- Overview of 5-phase methodology
- Complete question sets for each phase (Simple/Medium/Complex variants)
- Heuristic strategy catalog with triggers and methods
- Phase transition criteria
- Validation gate templates
- Error handling patterns (ambiguity, failure, uncertainty)

**FR-8.2** Skill file MUST follow Claude Code SKILL.md best practices:
- < 500 lines for core file
- Reference separate files for detailed content (if needed)
- Clear activation_context for skill discovery
- No duplication of content from other docs (reference instead)

---

## 5. Non-Goals (Out of Scope)

| Non-Goal | Rationale |
|----------|-----------|
| Automated complexity detection | User confirms complexity; no ML-based assessment |
| Integration with external tools | Claude-internal skill enhancement only |
| Retrospective analysis | Focus is on PRD creation, not post-implementation reflection |
| Multi-language support | English only for initial implementation |
| Visual diagram generation | Text-based PRD only (diagrams can be added later) |
| Remembering question effectiveness | No cross-session learning in v1 |

---

## 6. Design Considerations

### Conversation Flow

```
User: Initial feature request
    ↓
Claude: [COMPLEXITY ASSESSMENT]
        "This appears to be a [Simple/Medium/Complex] feature because..."
        "Do you agree with this assessment? (Y/adjust)"
    ↓
User: Confirms or adjusts complexity
    ↓
Claude: [UNDERSTAND PHASE]
        Adaptive questions based on complexity
    ↓
User: Answers
    ↓
Claude: [GATE 1]
        "Here's my understanding: [summary]"
        "Is this correct before I suggest approaches?"
    ↓
User: Confirms or corrects
    ↓
Claude: [PLAN PHASE]
        Strategic questions + heuristic suggestions
    ↓
User: Answers
    ↓
Claude: [GATE 2]
        "Here's the proposed approach: [summary]"
        "Does this direction make sense?"
    ↓
User: Confirms or corrects
    ↓
Claude: [GENERATE]
        Draft complete PRD with all enhanced sections
    ↓
Claude: [GATE 3]
        "Here's the draft PRD. Please review."
        "Ready to save, or any changes needed?"
    ↓
User: Confirms or requests changes
    ↓
Claude: [FINALIZE]
        Save PRD to /tasks/[NNNN]-prd-[feature-name].md
```

### Question Format Standards

Questions MUST be:
- Numbered or lettered for easy reference (e.g., "1a, 1b, 2, 3...")
- Grouped by category with clear headers for Medium/Complex
- Include examples where helpful
- Offer "skip if not applicable" option for optional questions

**Example Format:**
```markdown
### Understanding Your Feature Request

**Core Problem (Required):**
1. What problem does this feature solve for users?
2. What would users be able to do that they can't do now?

**Constraints (Answer what applies):**
3. Are there technical constraints we should know about?
   a) Performance requirements?
   b) Integration with existing systems?
   c) Security considerations?
4. Are there business constraints (timeline, budget, team size)?

**Clarifications (Optional):**
5. Have you seen this implemented elsewhere? (skip if N/A)
6. Any specific non-goals to exclude from scope?
```

### Gate Format Standards

Each gate MUST follow this template:
```markdown
---
**[GATE N: Phase Name Validation]**

Here's my understanding from our discussion:
• [Key point 1]
• [Key point 2]
• [Key point 3]

**Confirmation needed:** Does this accurately capture [the problem/our approach/the requirements]?
- ✅ **Yes, proceed** — Move to [next phase]
- 🔄 **Adjust** — Tell me what to change
- ⬅️ **Go back** — Return to [previous phase]
---
```

---

## 7. Technical Considerations

### Recommended Implementation Strategies

**Strategy 1: Decomposition**
- **Why it applies:** This enhancement has two distinct deliverables (skill file + template update)
- **Suggested approach:** Develop skill file first (complete methodology), then update template to import it
- **Watch for:** Ensure template imports align with skill file structure

**Strategy 2: Progressive Disclosure**
- **Why it applies:** Need to balance conciseness (template) with comprehensiveness (methodology)
- **Suggested approach:** `create-prd.md` imports `@polya-planning.md` for full question sets; keeps main template under 100 lines
- **Watch for:** Import syntax must work with Claude Code skill loading

**Strategy 3: Template Pattern**
- **Why it applies:** Gate format, question format should be consistent
- **Suggested approach:** Define reusable templates in skill file, reference from main workflow
- **Watch for:** Templates should be copy-paste ready

### File Structure

```
.claude/
├── create-prd.md              # Enhanced template (imports skill)
└── skills/
    └── polya-planning/
        ├── SKILL.md           # Main skill file with methodology
        └── references/
            └── question-sets.md   # Detailed question sets (optional, if >400 lines)
```

### Integration Points

- **Existing workflow:** Must remain compatible with `@generate-tasks.md` and `@process-task-list.md`
- **Other skills:** No conflicts with tutorial-standards, tdd-methodology, pattern-application
- **Activation context:** Distinct triggers ("create PRD", "write PRD", "Pólya", "structured planning")

### Dependencies

- No external dependencies
- Relies on Claude's built-in skill loading (`@` import syntax)
- Compatible with existing AI Dev Tasks workflow

---

## 8. Success Metrics

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| **Question specificity** | 50% more specific questions per PRD | Compare before/after PRD transcripts |
| **Gate confirmation rate** | >90% proceed without major corrections | Track "Adjust" vs "Proceed" at gates |
| **PRD completeness** | <10% follow-up clarifications needed | Count post-PRD questions in implementation |
| **Complexity accuracy** | User agrees with assessment 80%+ | Track adjustment rate at complexity gate |
| **Developer clarity** | PRDs rated "clear" or "very clear" | Developer feedback survey |
| **Implementation alignment** | <15% scope changes during implementation | Post-implementation review |
| **Time efficiency** | <5 min increase for simple, <15 min for complex | Track PRD creation time |

---

## 9. Open Questions

| # | Question | Options | Decision Owner |
|---|----------|---------|----------------|
| Q1 | Skill file location | `.claude/skills/polya-planning/SKILL.md` vs `.claude/skills/polya-planning.md` | Tech Lead |
| Q2 | Backward compatibility | Opt-in (user triggers) vs default behavior | Product Owner |
| Q3 | Gate strictness | Require explicit "Yes" vs accept partial confirmation | UX Lead |
| Q4 | Question memory | Track useful questions across sessions (future v2)? | Product Owner |
| Q5 | Multi-PRD projects | When to suggest splitting vs keeping as one PRD? | Tech Lead |

---

## Appendix A: Pólya Phase Mapping

| 5-Phase Workflow | Original Pólya Phase | PRD Section Generated |
|------------------|---------------------|----------------------|
| **Understand** | Phase 1: Understanding the Problem | Problem Understanding, Goals |
| **Plan** | Phase 2a: Devising a Plan (Strategy) | Strategic Approach, Technical Considerations |
| **Tasks** | Phase 2b: Devising a Plan (Tactics) | Functional Requirements |
| **Execute** | Phase 3: Carrying Out the Plan | (PRD generation itself) |
| **Reflect** | Phase 4: Looking Back | Validation Checkpoints, Success Metrics |

---

## Appendix B: Heuristic Quick Reference

| Heuristic | Trigger Condition | Example Application |
|-----------|-------------------|---------------------|
| **Decomposition** | "Too large to solve directly" | Break auth system into: login, registration, password reset |
| **Analogy** | "Seems unfamiliar" | "This is like a shopping cart, but for course enrollments" |
| **Working Backward** | "Goal clear, path unclear" | Start from deployed feature, trace back to requirements |
| **Simplification** | "Too many constraints" | Build for single user first, then add multi-tenancy |
| **Auxiliary Problem** | "Stuck on main problem" | Can't design API? First define data models. |
| **Specialization** | "Too general" | Test with specific user persona, specific scenario |
| **Generalization** | "Solution too narrow" | Extract pattern that works for all entity types |

---

**Document End**
