---
name: "Pólya Planning"
version: "1.0.0"
description: "Guide structured problem-solving through Pólya's 5-phase workflow with adaptive questioning and validation gates"
activation_context:
  - "create PRD"
  - "write PRD"
  - "product requirements"
  - "Pólya"
  - "structured planning"
  - "understand problem"
  - "break down problem"
references:
  - path: "ai-dev-tasks/polya-analysis.md"
    description: "Complete Pólya methodology research and synthesis"
  - path: "tasks/0013-prd-polya-enhanced-prd-creation.md"
    description: "PRD for this skill enhancement"
---

# Pólya Planning Skill

## Purpose

This skill guides Claude through structured problem-solving using George Pólya's methodology when creating PRDs or tackling complex tasks. It provides:
- Adaptive questioning based on problem complexity
- Explicit validation gates requiring user confirmation
- Heuristic strategy recommendations for implementation

## When This Skill Activates

- User asks to "create PRD" or "write product requirements"
- User mentions "Pólya" or "structured planning"
- User asks to "understand" or "break down" a problem
- User requests help with complex feature planning

---

## The 5-Phase Workflow

```
UNDERSTAND → PLAN → TASKS → EXECUTE → REFLECT
    ↓          ↓       ↓        ↓         ↓
 [GATE 1]  [GATE 2]   ---   [GATE 3]    ---
```

### Phase Mapping from Pólya's "How to Solve It"

| Phase | Pólya Original | Core Question | Primary Output |
|-------|----------------|---------------|----------------|
| Understand | Understanding the Problem | "What is the unknown?" | Problem definition |
| Plan | Devising a Plan (Strategy) | "Have I seen this before?" | Strategic approach |
| Tasks | Devising a Plan (Tactics) | "What are the steps?" | Task breakdown |
| Execute | Carrying Out the Plan | "Is each step correct?" | Working solution |
| Reflect | Looking Back | "Can I check the result?" | Validated output |

---

## Phase 1: UNDERSTAND

**Core Principle:** *"It is foolish to answer a question that you do not understand."* — Pólya

### Complexity Assessment (Do This First)

Before asking questions, assess complexity:

| Complexity | Indicators | Question Depth |
|------------|------------|----------------|
| **Simple** | Single component, clear outcome, <2 days | 3-4 focused questions |
| **Medium** | Multiple components, some ambiguity, 1-2 weeks | 5-7 grouped questions |
| **Complex** | System-level, significant ambiguity, multi-week | 8-10+ with sub-questions |

**Template:**
```
This appears to be a [SIMPLE/MEDIUM/COMPLEX] request because:
• [Reason 1]
• [Reason 2]

Do you agree? (Yes / Adjust to [other level])
```

### Question Sets by Complexity

#### Simple (3-4 questions)
1. What specific outcome do you want?
2. What constraints should I know about?
3. What does success look like?
4. Anything explicitly out of scope?

#### Medium (5-7 questions)
**Core Problem:**
1. What problem does this solve for users?
2. What can users do after that they can't do now?

**Constraints:**
3. Technical constraints? (performance, integrations, security)
4. Business constraints? (timeline, team, budget)

**Clarity:**
5. Have you seen this implemented elsewhere?
6. What would make this "done"?
7. What should this explicitly NOT do?

#### Complex (8-10+ questions)
**Understanding the Unknown:**
1. What is the desired end state? Paint the picture.
2. Who are the primary users? Secondary?
3. What's the trigger that starts this feature?
4. What's the output/outcome when complete?

**Understanding the Data:**
5. What information is given/available?
6. What information needs to be gathered?
7. What systems must this integrate with?

**Understanding Constraints:**
8. Performance requirements? (latency, throughput, scale)
9. Security/compliance requirements?
10. Timeline and team constraints?

**Checking Understanding:**
11. Can you describe a day-in-the-life scenario?
12. What's the simplest version that would be valuable?
13. What's explicitly out of scope?

### GATE 1: Understanding Validation

**Template:**
```markdown
---
**GATE 1: Understanding Validation**

Here's my understanding of the problem:
• **Goal:** [Restated goal]
• **Users:** [Who benefits]
• **Key constraint:** [Most important constraint]
• **Success looks like:** [Measurable outcome]
• **Assumptions:** [Any assumptions made]

**Confirmation needed:** Does this accurately capture the problem?
- ✅ **Yes, proceed** to planning
- 🔄 **Adjust** — Tell me what's different
- ⬅️ **Clarify more** — Ask me more questions
---
```

---

## Phase 2: PLAN

**Core Principle:** *"We have a plan when we know which calculations, computations, or constructions we have to perform."* — Pólya

### Strategic Questions

1. **Analogy:** Have we solved something similar before? Can we use that approach?
2. **Decomposition:** Can this be broken into independent parts?
3. **Approach:** What are 2-3 possible approaches? Which is most promising?
4. **Risk:** What could go wrong? How would we mitigate?
5. **Dependencies:** What must exist before this can work?

### Heuristic Strategy Selection

When planning, recommend applicable strategies:

#### Strategy: Decomposition
**When to use:** Problem is too large or complex to solve directly
**Method:**
1. Identify natural boundaries (user-facing vs backend, read vs write)
2. Define interfaces between components
3. Solve each component independently
4. Plan integration points
**Watch for:** Losing sight of integration requirements; over-decomposing simple problems

#### Strategy: Analogy
**When to use:** Problem seems unfamiliar
**Method:**
1. Identify the type of output (what kind of thing is the answer?)
2. Search for problems with similar structure
3. Adapt the method from the analogous problem
**Watch for:** Surface similarity hiding structural differences

#### Strategy: Working Backward
**When to use:** Goal is clear but path from start is not
**Method:**
1. Start from desired end state
2. Ask: What's the immediate predecessor state?
3. Recurse until reaching current state
4. Reverse the sequence for forward plan
**Watch for:** Steps that aren't reversible in practice

#### Strategy: Simplification
**When to use:** Problem has too many constraints
**Method:**
1. Identify which constraints can be temporarily relaxed
2. Solve the simplified version
3. Incrementally add constraints back
4. Adjust solution for each constraint
**Watch for:** Relaxing constraints that are actually essential

#### Strategy: Auxiliary Problem
**When to use:** Stuck on main problem
**Method:**
1. Identify what capability would unblock progress
2. Formulate a subproblem that develops that capability
3. Solve the auxiliary problem first
4. Apply the result to the main problem
**Watch for:** Getting lost in auxiliary work; scope creep

### GATE 2: Approach Validation

**Template:**
```markdown
---
**GATE 2: Approach Validation**

Here's the proposed approach:
• **Strategy:** [Primary strategy, e.g., Decomposition]
• **Major components:** [List 2-4 major parts]
• **Key risk:** [Biggest risk and mitigation]
• **Dependencies:** [What must exist first]

**Recommended heuristics for implementation:**
1. **[Strategy Name]:** [Why it applies] → [How to use it]
2. **[Strategy Name]:** [Why it applies] → [How to use it]

**Confirmation needed:** Does this approach make sense?
- ✅ **Yes, proceed** to requirements
- 🔄 **Adjust** — Different approach preferred
- ⬅️ **Rethink** — Return to understanding phase
---
```

---

## Phase 3: TASKS

**Core Principle:** *"Decompose the whole into its parts."* — Pólya

### Task Specification Template

For each major task:
```
Task [N]: [Clear name]
• Objective: [What this accomplishes]
• Input: [What it needs]
• Output: [What it produces]
• Method: [How to accomplish]
• Verification: [How to confirm success]
• Dependencies: [What must complete first]
```

### Task Breakdown Questions

1. What are the specific, concrete steps?
2. For each step: What's input? Output? Tool/action?
3. What's the correct order? What depends on what?
4. Are there parallel opportunities?
5. What are the checkpoint/validation points?

---

## Phase 4: EXECUTE

**Core Principle:** *"Check each step. Can you see clearly that the step is correct?"* — Pólya

### Execution Checklist (Per Step)

- [ ] Am I executing the right task in the right order?
- [ ] Do I have everything needed?
- [ ] Is the output correct? How do I know?
- [ ] Did anything unexpected happen?
- [ ] Am I still on track toward the overall goal?

### When to Revise Plan

Return to earlier phase if:
- Current approach clearly isn't working after reasonable effort
- New information fundamentally changes the problem
- A simpler path becomes apparent
- Unexpected dependency or constraint discovered

### GATE 3: Output Validation

**Template:**
```markdown
---
**GATE 3: Output Validation**

Here's the draft [PRD/solution/deliverable]:
[Summary or full content]

**Verification:**
• Addresses original goal: [Yes/Partially/No]
• Covers all discussed requirements: [List]
• Follows agreed approach: [Yes/Adjusted because...]

**Confirmation needed:** Ready to finalize?
- ✅ **Yes, save/commit**
- 🔄 **Revise** — [Specific changes needed]
- ⬅️ **Major rework** — Return to [phase]
---
```

---

## Phase 5: REFLECT

**Core Principle:** *"By looking back, they could consolidate their knowledge and develop their ability to solve problems."* — Pólya

### Reflection Questions

1. Does the output satisfy all original requirements?
2. Can I verify correctness through an independent method?
3. What worked well? What was inefficient?
4. What would I do differently next time?
5. Can this solution or method generalize?

### Reflection Template (for PRD)

```markdown
## Validation Checkpoints

During implementation, verify:
1. [ ] [Checkpoint from requirements]
2. [ ] [Checkpoint from constraints]
3. [ ] [Checkpoint from success criteria]

## Lessons for Similar Problems

• **Pattern identified:** [Reusable approach]
• **When to apply:** [Trigger conditions]
• **Pitfall to avoid:** [What went wrong or almost went wrong]
```

---

## Error Handling

### Handling Ambiguity

1. Identify specifically what is ambiguous
2. Generate 2-3 reasonable interpretations
3. State chosen interpretation explicitly
4. Ask user to confirm or correct

**Template:**
```
I'm unclear about [specific ambiguity]. It could mean:
a) [Interpretation 1]
b) [Interpretation 2]
c) [Interpretation 3]

I'll proceed with (a) unless you indicate otherwise.
```

### Handling Being Stuck

*"If you cannot solve the proposed problem, try to solve first some related problem."* — Pólya

1. **Diagnose:** Is this a task failure, plan failure, or understanding failure?
2. **Simplify:** Can I solve a simpler version first?
3. **Auxiliary:** What subproblem would unblock this?
4. **Ask:** What specific information would help?

### Handling Uncertainty

- Express uncertainty explicitly: "I'm confident about X but uncertain about Y"
- Identify which assumptions are most critical
- Design verification to test high-risk assumptions first

---

## Quick Reference Card

### Complexity → Question Depth
| Level | Questions | Gates |
|-------|-----------|-------|
| Simple | 3-4 | All 3 gates |
| Medium | 5-7 | All 3 gates |
| Complex | 8-10+ | All 3 gates + possible iteration |

### Phase → Primary Question
| Phase | Ask Yourself |
|-------|--------------|
| Understand | "What is the unknown? What would success look like?" |
| Plan | "Have I seen this before? What approach fits?" |
| Tasks | "What are the concrete steps? What depends on what?" |
| Execute | "Is each step correct? Am I still on track?" |
| Reflect | "Does it work? What would I do differently?" |

### Heuristic → Trigger
| Heuristic | Use When |
|-----------|----------|
| Decomposition | Too large to solve directly |
| Analogy | Seems unfamiliar |
| Working Backward | Goal clear, path unclear |
| Simplification | Too many constraints |
| Auxiliary Problem | Stuck on main problem |

---

**Version:** 1.0.0
**Based on:** George Pólya, "How to Solve It" (1945) and modern extensions (Schoenfeld, Mason et al.)
**See also:** [ai-dev-tasks/polya-analysis.md](../../ai-dev-tasks/polya-analysis.md)
