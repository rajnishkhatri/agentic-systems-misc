# SKILL.md File Format Specification

This document defines the standard format for Claude Skills configuration files.

## File Structure

Each skill MUST have a `SKILL.md` file with:
1. **YAML Frontmatter** - Metadata and activation configuration
2. **Skill Description** - What the skill does and when it activates
3. **References Section** - Links to supporting documentation
4. **Examples Section** - Real usage examples from codebase

## YAML Frontmatter Format

```yaml
---
name: "Skill Name"
version: "1.0.0"
description: "Brief one-line description of what this skill does"
activation_context:
  - "keyword1"
  - "phrase to match"
  - "another trigger"
references:
  - path: "relative/path/to/doc.md"
    description: "What this reference provides"
  - path: "another/reference.md"
    description: "Purpose of this reference"
examples:
  - path: "examples/example1.md"
    description: "Example scenario"
---
```

## Field Definitions

### Required Fields

#### `name` (string)
- Human-readable skill name
- Use Title Case
- Example: `"Tutorial Standards"`, `"TDD Methodology"`

#### `version` (string)
- Semantic versioning: `MAJOR.MINOR.PATCH`
- `MAJOR`: Breaking changes to activation context
- `MINOR`: New references or examples added
- `PATCH`: Bug fixes or documentation clarifications
- Example: `"1.0.0"`, `"1.2.3"`

#### `description` (string)
- One-line summary of skill purpose
- Max 120 characters
- Example: `"Enforce tutorial quality standards and provide TUTORIAL_INDEX template"`

#### `activation_context` (array of strings)
- Keywords/phrases that trigger skill activation
- Case-insensitive matching
- Can include single words or multi-word phrases
- Examples:
  - `["create tutorial", "TUTORIAL_INDEX", "add notebook"]`
  - `["write test", "implement function", "TDD", "refactor"]`
  - `["parallel processing", "batch", "concurrent", "ThreadPoolExecutor"]`

### Optional Fields

#### `references` (array of objects)
- Links to existing documentation (preferred over duplication)
- Each reference has:
  - `path` (string): Relative path from project root
  - `description` (string): Purpose of this reference

#### `examples` (array of objects)
- Links to example files in `examples/` subdirectory
- Each example has:
  - `path` (string): Relative path from skill directory
  - `description` (string): Scenario this example demonstrates

## Example SKILL.md File

```markdown
---
name: "Tutorial Standards"
version: "1.0.0"
description: "Enforce tutorial quality standards and provide TUTORIAL_INDEX template"
activation_context:
  - "create tutorial"
  - "TUTORIAL_INDEX"
  - "add notebook"
  - "write lesson"
  - "tutorial structure"
references:
  - path: "CLAUDE.md#tutorial-workflow"
    description: "Tutorial creation workflow and quality standards"
  - path: ".claude/skills/tutorial-standards/references/tutorial-index-template.md"
    description: "Required sections for TUTORIAL_INDEX.md"
  - path: ".claude/skills/tutorial-standards/references/notebook-standards.md"
    description: "Jupyter notebook quality requirements"
examples:
  - path: "examples/lesson-9-tutorial-index.md"
    description: "Reference implementation from lesson-9/"
---

# Tutorial Standards Skill

## Purpose

This skill activates when you're creating or updating tutorials to ensure:
- TUTORIAL_INDEX.md contains all required sections
- Notebooks execute in <5 minutes
- Cross-links use relative paths
- Diagrams are understandable without reading code
- Reading time is 15-30 minutes

## When This Skill Activates

- User says "create tutorial" or "add tutorial"
- User mentions "TUTORIAL_INDEX"
- User asks to "add notebook" or "create notebook"
- User asks "how to structure a lesson"

## Guidance Provided

When activated, this skill will:

1. **TUTORIAL_INDEX.md Structure**
   - Remind about required sections (objectives, prerequisites, learning paths, FAQs)
   - Reference template: `.claude/skills/tutorial-standards/references/tutorial-index-template.md`
   - Point to example: `lesson-9/TUTORIAL_INDEX.md`

2. **Notebook Standards**
   - Setup cell requirements (imports, constants)
   - Cost warning for API calls
   - Execution time <5 minutes
   - Validation assertions
   - Reference: `.claude/skills/tutorial-standards/references/notebook-standards.md`

3. **Cross-Linking Rules**
   - Use relative paths (not absolute)
   - Link related tutorials
   - Reference: `.claude/skills/tutorial-standards/references/cross-linking-rules.md`

## References

See YAML frontmatter for complete reference list.

## Examples

- **Lesson 9 TUTORIAL_INDEX**: Gold standard example with all required sections
- **Path**: `lesson-9/TUTORIAL_INDEX.md`
- **Local copy**: `examples/lesson-9-tutorial-index.md`
```

## Validation Checklist

Before committing a SKILL.md file, verify:

- [ ] YAML frontmatter is valid (parse with YAML parser)
- [ ] All required fields present (`name`, `version`, `description`, `activation_context`)
- [ ] Version follows semantic versioning (X.Y.Z)
- [ ] Activation context has at least 3 keywords/phrases
- [ ] All reference paths exist (validate with file system check)
- [ ] All example paths exist in `examples/` subdirectory
- [ ] Description is <120 characters
- [ ] No content duplication (references existing docs instead)
- [ ] File:line references for code examples (where applicable)

## Anti-Patterns to Avoid

❌ **Don't duplicate content from CLAUDE.md or other docs**
```yaml
# BAD: Including full TDD rules in skill description
# Instead: Reference CLAUDE.md#tdd-mode
```

✅ **Do reference existing documentation**
```yaml
references:
  - path: "CLAUDE.md#tdd-mode"
    description: "Complete TDD workflow rules"
```

❌ **Don't use vague activation contexts**
```yaml
activation_context:
  - "help"  # Too broad
  - "code"  # Too generic
```

✅ **Do use specific, meaningful triggers**
```yaml
activation_context:
  - "write test"
  - "implement function"
  - "TDD workflow"
  - "failing test"
```

❌ **Don't create overlapping activation contexts across skills**
```yaml
# BAD: Both skills activate on "test"
# tutorial-standards: ["test execution"]
# tdd-methodology: ["write test"]
```

✅ **Do use distinct activation contexts**
```yaml
# GOOD: Clear separation
# tutorial-standards: ["notebook execution", "tutorial test"]
# tdd-methodology: ["write test", "unit test", "TDD"]
```

## Testing Activation

After creating a SKILL.md file, test activation with:

1. Manual test scenarios (see `.claude/skills/TESTING_SCENARIOS.md`)
2. YAML validation: `python -c "import yaml; yaml.safe_load(open('SKILL.md').read().split('---')[1])"`
3. Reference validation: Check all paths exist
4. Activation test: Start Claude session with trigger phrases

---

**Last Updated:** 2025-11-18
**Used By:** All skills in `.claude/skills/` directory
