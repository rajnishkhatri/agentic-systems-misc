# /polya - Structured Problem-Solving with Pólya's Methodology

Use this command to activate structured problem-solving using George Pólya's 5-phase workflow. Ideal for creating PRDs, planning complex features, or tackling ambiguous problems.

## Usage
```
/polya [mode] [optional: problem description]
```

## Modes

### PRD Mode (Default)
```
/polya prd [feature description]
```
Creates a Product Requirements Document using the full Pólya workflow:
- Complexity assessment
- Adaptive questioning (3-10 questions based on complexity)
- 3 validation gates
- 12-section PRD with heuristic recommendations

### Plan Mode
```
/polya plan [problem description]
```
Strategic planning without full PRD generation:
- UNDERSTAND phase with validation gate
- PLAN phase with heuristic selection
- Task breakdown recommendations

### Analyze Mode
```
/polya analyze [problem description]
```
Problem analysis only:
- Complexity assessment
- Clarifying questions
- Understanding validation
- No implementation planning

## The 5-Phase Workflow

```
UNDERSTAND → PLAN → TASKS → EXECUTE → REFLECT
    ↓          ↓       ↓        ↓         ↓
 [GATE 1]  [GATE 2]   ---   [GATE 3]    ---
```

| Phase | Core Question | Output |
|-------|---------------|--------|
| Understand | "What is the unknown?" | Problem definition |
| Plan | "Have I seen this before?" | Strategic approach |
| Tasks | "What are the steps?" | Task breakdown |
| Execute | "Is each step correct?" | Working solution |
| Reflect | "Can I check the result?" | Validated output |

## Heuristic Strategies

The workflow recommends applicable strategies:

| Strategy | Use When |
|----------|----------|
| **Decomposition** | Problem too large to solve directly |
| **Analogy** | Problem seems unfamiliar |
| **Working Backward** | Goal clear, path unclear |
| **Simplification** | Too many constraints |
| **Auxiliary Problem** | Stuck on main problem |

## Validation Gates

All modes include validation gates requiring explicit user confirmation:

- **GATE 1**: Understanding Validation - "Does this capture the problem?"
- **GATE 2**: Approach Validation - "Does this approach make sense?"
- **GATE 3**: Output Validation - "Ready to finalize?"

## Examples

### Create a PRD
```
/polya prd user authentication with OAuth
```

### Plan a complex feature
```
/polya plan migrate database from PostgreSQL to MongoDB
```

### Analyze an ambiguous problem
```
/polya analyze improve application performance
```

## References

- **Skill Definition**: @.claude/skills/polya-planning/SKILL.md
- **PRD Workflow**: @.claude/create-prd.md
- **Methodology Research**: @ai-dev-tasks/polya-analysis.md

---

ARGUMENTS: $ARGUMENTS

When this command is invoked:

1. Parse the mode from arguments (default: prd)
2. Load the Pólya Planning skill from @.claude/skills/polya-planning/SKILL.md
3. Begin with complexity assessment
4. Follow the appropriate workflow for the selected mode
5. Use validation gates at each phase transition
6. For PRD mode, save output to /tasks/ directory following naming convention
