# First Principles Teaching Skill

**When to apply:** Creating tutorials, documentation, or explanations for complex systems.

---

## 8 Core Principles

### 1. Problem Before Solution
Start with the pain point, not the abstraction.

```markdown
## Why [Technology] Exists

### The Problem: [Concrete Pain Point]
- Specific failure mode 1
- Specific failure mode 2

**Without [technology]**, you're [vivid description of problem].

### The Solution: [High-Level Concept]
[One sentence describing what it does, not how]
```

### 2. Real-World Analogies
Map abstract concepts to familiar physical experiences.

```markdown
Think of [technology] like **[familiar system]**:

| [Familiar System] | [Technology] |
|-------------------|--------------|
| [Physical thing 1] | `[code_element_1]` - [what it does] |
| [Physical thing 2] | `[code_element_2]` - [what it does] |
```

### 3. Concrete Before Abstract
Show real data before explaining code that processes it.

**Sequence:** Raw data → What happens → Code that does it

### 4. Explain Prerequisites
Don't assume knowledge. For each prerequisite:

| Section | Content |
|---------|---------|
| **One-liner** | What this concept does |
| **Problem it solves** | Code showing what breaks without it |
| **Solution** | Code showing how it fixes it |
| **Usage in system** | Where it appears in codebase |

### 5. Single Responsibility Decomposition
Break complex systems into atomic, single-purpose components.

```markdown
There are **[N] core [things]** you need to understand:

[Component 1] → [One thing it does]
[Component 2] → [One thing it does]

Each component does **one thing**.
```

### 6. Show Data Flow
Follow one piece of data through all transformations.

```
┌─────────────────────────────────────────┐
│ STEP 1: [Action]                        │
├─────────────────────────────────────────┤
│   [code or description]                 │
└───────────────────┬─────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│ STEP 2: [Action]                        │
└─────────────────────────────────────────┘
```

### 7. Why Before How
Every pattern/decision includes its purpose.

```markdown
| Pattern | Where | **Why It's Needed** |
|---------|-------|---------------------|
| [Pattern 1] | `file.py` | [Problem it solves] |
```

### 8. Build Complexity Incrementally
Each example adds exactly one new concept.

```markdown
### Example 1: [Simplest Case] - one concept
### Example 2: [Add One Thing] - previous + one new
### Example 3: [Add Another] - previous + one new
### Example 4: [Full Integration] - all together
```

---

## Character-by-Character Template

For regex, syntax, or symbolic notation:

```
Pattern: \b\d{3}-\d{2}-\d{4}\b
         ^^ ^^^ ^  ^^  ^^^^  ^^
         |  |   |  |   |     |
         |  |   |  |   |     └─ Word boundary (end)
         |  |   |  |   └─────── Exactly 4 digits
         |  |   |  └─────────── Exactly 2 digits
         |  |   └────────────── Literal hyphen
         |  └────────────────── Exactly 3 digits
         └───────────────────── Word boundary (start)
```

---

## Problem → Solution Template

```markdown
**The problem:**
```python
# Hard-coded/brittle/unsafe approach
def bad_example():
    pass  # What's wrong
```

**The solution:**
```python
# Better approach using [concept]
def good_example():
    pass  # Why this is better
```

**Why this matters:**
| Benefit | How It Helps |
|---------|--------------|
| [Benefit 1] | [Concrete example] |
```

---

## Quality Checklist

Before publishing, verify:

- [ ] **Problem first**: Section 1 explains WHY before WHAT
- [ ] **Analogy present**: Real-world comparison included
- [ ] **Prerequisites covered**: All assumed concepts explained
- [ ] **Data before code**: Examples show data before processing code
- [ ] **Single responsibility**: Each component does ONE thing
- [ ] **Flow diagram**: Visual showing data flow
- [ ] **Why documented**: Every pattern includes purpose
- [ ] **Incremental examples**: Examples build on each other
- [ ] **Skip links**: Experts can skip prerequisite sections

---

## Anti-Patterns to Avoid

| Anti-Pattern | Better Approach |
|--------------|-----------------|
| Starting with class hierarchy | Start with the problem |
| "See the code for details" | Explain inline |
| Assuming prerequisite knowledge | Add "Fundamentals" section |
| Listing patterns without why | Always explain purpose |
| One giant example | Build incrementally |
| Abstract before concrete | Show data first |

---

*Source: patterns/first-principles-teaching.md*
