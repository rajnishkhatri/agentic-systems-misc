# Rule: Generating a Product Requirements Document (PRD)

## Goal

To guide an AI assistant in creating a detailed Product Requirements Document (PRD) in Markdown format, using Pólya's structured problem-solving methodology. The PRD should be clear, actionable, and suitable for a junior developer to understand and implement the feature.

**Methodology Reference:** @.claude/skills/polya-planning/SKILL.md

---

## Process Overview

```
1. Receive → 2. Assess Complexity → 3. UNDERSTAND Phase → [GATE 1]
    → 4. PLAN Phase → [GATE 2] → 5. Generate PRD → [GATE 3] → 6. Save
```

### Step 1: Receive Initial Prompt
The user provides a brief description or request for a new feature.

### Step 2: Assess Complexity
Before asking questions, assess and confirm complexity:

| Complexity | Indicators | Question Depth |
|------------|------------|----------------|
| **Simple** | Single component, clear outcome, <2 days | 3-4 focused questions |
| **Medium** | Multiple components, some ambiguity, 1-2 weeks | 5-7 grouped questions |
| **Complex** | System-level, significant ambiguity, multi-week | 8-10+ with sub-questions |

**Say:** "This appears to be a [LEVEL] request because [reasons]. Do you agree? (Yes / Adjust)"

### Step 3: UNDERSTAND Phase (Pólya Phase 1)
Ask questions to understand the problem. Adapt depth to complexity.

**Core Questions (Always Ask):**
1. What problem does this feature solve for the user?
2. What is the desired outcome/end state?
3. What constraints should I know about?
4. What does success look like?

**Additional Questions (Medium/Complex):**
5. Who are the primary users? Secondary?
6. Have you seen this implemented elsewhere?
7. What should this explicitly NOT do (non-goals)?
8. Are there technical constraints (performance, integrations, security)?
9. Are there business constraints (timeline, team, budget)?
10. What's the simplest version that would be valuable?

**Format:** Provide questions as numbered lists with letter sub-options for easy response.

### GATE 1: Understanding Validation
Before proceeding to planning, summarize understanding and get confirmation:

```markdown
---
**GATE 1: Understanding Validation**

Here's my understanding:
• **Goal:** [Restated goal]
• **Users:** [Who benefits]
• **Key constraint:** [Most important constraint]
• **Success looks like:** [Measurable outcome]

**Confirmation needed:** Does this capture the problem correctly?
- Yes, proceed to planning
- Adjust [tell me what's different]
- Ask more questions
---
```

### Step 4: PLAN Phase (Pólya Phase 2)
Explore strategic approach and identify applicable heuristics.

**Strategic Questions:**
1. Have we solved something similar before?
2. What are 2-3 possible approaches?
3. What could go wrong? How to mitigate?
4. What must exist before this can work?

**Heuristic Selection (for Technical Considerations):**
Select applicable strategies to recommend in the PRD:

| Heuristic | Use When |
|-----------|----------|
| **Decomposition** | Problem too large to solve directly |
| **Analogy** | Problem seems unfamiliar; find similar solved problem |
| **Working Backward** | Goal is clear but path is not |
| **Simplification** | Too many constraints; solve simpler version first |
| **Auxiliary Problem** | Stuck; solve a helper problem to unblock |

### GATE 2: Approach Validation
Before generating PRD, confirm approach:

```markdown
---
**GATE 2: Approach Validation**

Here's the proposed approach:
• **Strategy:** [Primary approach]
• **Major components:** [2-4 parts]
• **Key risk:** [Biggest risk + mitigation]

**Recommended heuristics:** [List 1-2 strategies that apply]

**Confirmation needed:** Does this approach make sense?
- Yes, proceed to PRD
- Adjust approach
- Rethink problem
---
```

### Step 5: Generate PRD
Based on UNDERSTAND and PLAN phases, generate PRD with enhanced structure.

### GATE 3: PRD Review
Before saving, present the draft PRD and confirm:

```markdown
---
**GATE 3: PRD Review**

Here's the draft PRD. Please review:
[Full PRD content]

**Confirmation needed:** Ready to save?
- Yes, save to /tasks/
- Revise [specific changes]
- Major rework needed
---
```

### Step 6: Save PRD
Save as `[n]-prd-[feature-name].md` in `/tasks/` directory.
(n = zero-padded 4-digit sequence: 0001, 0002, etc.)

---

## PRD Structure (Enhanced)

The generated PRD should include:

1. **Introduction/Overview:** Feature description and problem it solves.

2. **Problem Understanding:** *(New section)*
   - Restated problem in your words
   - Key constraints identified
   - Assumptions made (if any)
   - Success criteria

3. **Goals:** Specific, measurable objectives.

4. **Strategic Approach:** *(New section)*
   - Chosen strategy with rationale
   - Major components/phases
   - Recommended implementation heuristics

5. **User Stories:** User narratives describing usage and benefits.

6. **Functional Requirements:** Numbered list of specific functionalities.

7. **Non-Goals (Out of Scope):** What this feature will NOT include.

8. **Design Considerations:** UI/UX requirements, mockups, components.

9. **Technical Considerations:**
   - Dependencies and integrations
   - **Recommended Implementation Strategies** *(Enhanced)*
     - Strategy name
     - Why it applies
     - Suggested approach
     - Watch for (common pitfall)

10. **Success Metrics:** How success will be measured.

11. **Validation Checkpoints:** *(New section)*
    - Key verification points during implementation
    - Derived from success criteria and constraints

12. **Open Questions:** Remaining questions or clarifications needed.

---

## Target Audience

Primary reader: **junior developer**. Requirements must be:
- Explicit and unambiguous
- Avoid jargon where possible
- Include enough detail to understand purpose and core logic
- Include implementation strategy guidance (heuristics)

---

## Output

* **Format:** Markdown (`.md`)
* **Location:** `/tasks/`
* **Filename:** `[n]-prd-[feature-name].md`

---

## Final Instructions

1. Do NOT start implementing the PRD
2. Always assess complexity first and get confirmation
3. Use all 3 validation gates (Understanding, Approach, PRD Review)
4. Include recommended heuristics in Technical Considerations
5. Take user's answers and iterate before finalizing
6. Reference @.claude/skills/polya-planning/SKILL.md for detailed question sets

---

## Quick Reference: Pólya Questions

| Phase | Core Question |
|-------|---------------|
| Understand | "What is the unknown? What would success look like?" |
| Plan | "Have I seen this before? What approach fits?" |
| Execute (Generate) | "Is each section correct? Does it satisfy requirements?" |
| Reflect (Review) | "Does it work? What's missing?" |
