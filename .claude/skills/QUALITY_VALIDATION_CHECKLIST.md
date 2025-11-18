# Quality Validation Checklist for Skills

This checklist ensures all skills meet quality standards before deployment. Use this for both initial creation and ongoing maintenance.

## Overview

Each skill MUST pass all quality checks before:
- Initial deployment to `.claude/skills/`
- Integration testing with other skills
- Production use in Claude Code sessions

## Quality Standards

### 1. YAML Frontmatter Validity

**Requirement:** All SKILL.md files must have valid YAML frontmatter with required fields.

**Validation Steps:**

1. **Parse YAML Syntax**
   ```bash
   python3 << 'EOF'
   import yaml
   import sys

   skill_file = '.claude/skills/[skill-name]/SKILL.md'
   try:
       with open(skill_file, 'r') as f:
           content = f.read()
           parts = content.split('---')
           if len(parts) < 3:
               print("❌ No YAML frontmatter found")
               sys.exit(1)
           yaml_content = parts[1]
           data = yaml.safe_load(yaml_content)
           print(f"✅ YAML syntax valid")
   except yaml.YAMLError as e:
       print(f"❌ YAML parse error: {e}")
       sys.exit(1)
   except Exception as e:
       print(f"❌ Error: {e}")
       sys.exit(1)
   EOF
   ```

2. **Check Required Fields**
   ```bash
   python3 << 'EOF'
   import yaml
   import sys

   skill_file = '.claude/skills/[skill-name]/SKILL.md'
   with open(skill_file, 'r') as f:
       content = f.read()
       data = yaml.safe_load(content.split('---')[1])

       required = ['name', 'version', 'description', 'activation_context']
       missing = [f for f in required if f not in data]

       if missing:
           print(f"❌ Missing required fields: {missing}")
           sys.exit(1)

       print(f"✅ All required fields present")
       for field in required:
           print(f"   - {field}: {data[field]}")
   EOF
   ```

3. **Validate Field Types**
   ```bash
   python3 << 'EOF'
   import yaml
   import sys

   skill_file = '.claude/skills/[skill-name]/SKILL.md'
   with open(skill_file, 'r') as f:
       content = f.read()
       data = yaml.safe_load(content.split('---')[1])

       errors = []

       # name, version, description must be strings
       for field in ['name', 'version', 'description']:
           if not isinstance(data.get(field), str):
               errors.append(f"{field} must be string")

       # activation_context must be list
       if not isinstance(data.get('activation_context'), list):
           errors.append("activation_context must be list")

       # references must be list (if present)
       if 'references' in data and not isinstance(data['references'], list):
           errors.append("references must be list")

       # examples must be list (if present)
       if 'examples' in data and not isinstance(data['examples'], list):
           errors.append("examples must be list")

       if errors:
           print(f"❌ Field type errors: {errors}")
           sys.exit(1)

       print(f"✅ All field types valid")
   EOF
   ```

4. **Validate Semantic Versioning**
   ```bash
   python3 << 'EOF'
   import yaml
   import re
   import sys

   skill_file = '.claude/skills/[skill-name]/SKILL.md'
   with open(skill_file, 'r') as f:
       content = f.read()
       data = yaml.safe_load(content.split('---')[1])

       version = data.get('version', '')
       # Semantic versioning: MAJOR.MINOR.PATCH
       pattern = r'^\d+\.\d+\.\d+$'

       if not re.match(pattern, version):
           print(f"❌ Version '{version}' doesn't follow semantic versioning (X.Y.Z)")
           sys.exit(1)

       print(f"✅ Version format valid: {version}")
   EOF
   ```

**Checklist:**
- [ ] YAML syntax valid (parses without errors)
- [ ] All required fields present (name, version, description, activation_context)
- [ ] Field types correct (strings, lists as expected)
- [ ] Version follows semantic versioning (X.Y.Z)
- [ ] Description is concise (<120 characters)
- [ ] Activation context has ≥3 triggers

---

### 2. Reference Existence & Validity

**Requirement:** All referenced files must exist and be accessible.

**Validation Steps:**

1. **Check Reference Paths**
   ```bash
   python3 << 'EOF'
   import yaml
   import os
   import sys

   skill_file = '.claude/skills/[skill-name]/SKILL.md'
   with open(skill_file, 'r') as f:
       content = f.read()
       data = yaml.safe_load(content.split('---')[1])

       references = data.get('references', [])
       missing = []

       for ref in references:
           path = ref.get('path', '')
           # Handle paths with anchors (e.g., CLAUDE.md#tdd-mode)
           file_path = path.split('#')[0]

           if not os.path.exists(file_path):
               missing.append(file_path)

       if missing:
           print(f"❌ Missing reference files ({len(missing)}):")
           for path in missing:
               print(f"   - {path}")
           sys.exit(1)

       print(f"✅ All {len(references)} reference paths valid")
   EOF
   ```

2. **Check Example Paths**
   ```bash
   python3 << 'EOF'
   import yaml
   import os
   import sys

   skill_file = '.claude/skills/[skill-name]/SKILL.md'
   with open(skill_file, 'r') as f:
       content = f.read()
       data = yaml.safe_load(content.split('---')[1])

       examples = data.get('examples', [])
       missing = []

       skill_dir = os.path.dirname(skill_file)
       for ex in examples:
           path = ex.get('path', '')
           full_path = os.path.join(skill_dir, path)

           if not os.path.exists(full_path):
               missing.append(path)

       if missing:
           print(f"❌ Missing example files ({len(missing)}):")
           for path in missing:
               print(f"   - {path}")
           sys.exit(1)

       print(f"✅ All {len(examples)} example paths valid")
   EOF
   ```

3. **Validate Reference Descriptions**
   ```bash
   python3 << 'EOF'
   import yaml
   import sys

   skill_file = '.claude/skills/[skill-name]/SKILL.md'
   with open(skill_file, 'r') as f:
       content = f.read()
       data = yaml.safe_load(content.split('---')[1])

       references = data.get('references', [])
       errors = []

       for i, ref in enumerate(references):
           if 'path' not in ref:
               errors.append(f"Reference {i+1} missing 'path' field")
           if 'description' not in ref:
               errors.append(f"Reference {i+1} missing 'description' field")
           elif len(ref['description']) < 10:
               errors.append(f"Reference {i+1} description too short (<10 chars)")

       if errors:
           print(f"❌ Reference validation errors:")
           for err in errors:
               print(f"   - {err}")
           sys.exit(1)

       print(f"✅ All reference descriptions valid")
   EOF
   ```

**Checklist:**
- [ ] All reference file paths exist
- [ ] All example file paths exist
- [ ] All references have 'path' field
- [ ] All references have 'description' field
- [ ] Reference descriptions are meaningful (≥10 characters)
- [ ] Anchors in paths are valid (e.g., #tdd-mode exists in target file)

---

### 3. No Content Duplication

**Requirement:** Skills must REFERENCE existing documentation, not duplicate it.

**Validation Steps:**

1. **Manual Review: Check for Duplication**

   Open the SKILL.md file and review for:

   ❌ **Anti-Pattern: Duplicated Content**
   ```markdown
   ## TDD Rules

   1. RED phase: Write failing test first
   2. GREEN phase: Minimal code to pass
   3. REFACTOR phase: Improve code quality

   [Full TDD workflow copied from CLAUDE.md]
   ```

   ✅ **Best Practice: Reference Existing Docs**
   ```markdown
   ## TDD Rules

   See [CLAUDE.md#tdd-mode](../../CLAUDE.md#tdd-mode) for complete TDD workflow.

   **Quick reminder:**
   - RED → GREEN → REFACTOR
   - Test naming: `test_should_[result]_when_[condition]()`
   ```

2. **Search for Common Duplication Patterns**
   ```bash
   # Check if SKILL.md contains large blocks from CLAUDE.md
   skill_file=".claude/skills/[skill-name]/SKILL.md"

   # Extract common phrases from CLAUDE.md
   grep -o "RED → GREEN → REFACTOR" CLAUDE.md > /dev/null
   if grep -q "RED → GREEN → REFACTOR" "$skill_file"; then
       echo "⚠️  Warning: Found TDD phase text - check if duplicated from CLAUDE.md"
   fi

   # Check for pattern library duplication
   if grep -q "ThreadPoolExecutor" "$skill_file"; then
       echo "⚠️  Warning: Found ThreadPoolExecutor - check if duplicated from patterns/"
   fi

   # Check for tutorial workflow duplication
   if grep -q "TUTORIAL_INDEX.md" "$skill_file"; then
       echo "⚠️  Warning: Found TUTORIAL_INDEX - check if duplicated from CLAUDE.md"
   fi
   ```

3. **Verify References Instead of Duplication**

   For each section in SKILL.md, verify:
   - [ ] Does this content exist in CLAUDE.md or patterns/?
   - [ ] If yes, is there a reference link instead of full duplication?
   - [ ] Is only a brief summary/reminder provided (≤3 sentences)?

**Checklist:**
- [ ] No large blocks duplicated from CLAUDE.md (manual review)
- [ ] No code templates duplicated from patterns/ (manual review)
- [ ] No tutorial guidelines duplicated from CLAUDE.md#tutorial-workflow
- [ ] Skill provides references/links instead of full content
- [ ] Brief summaries/reminders are ≤3 sentences
- [ ] All detailed content referenced from source docs

---

### 4. Activation Context Quality

**Requirement:** Activation contexts must be specific, meaningful, and non-overlapping.

**Validation Steps:**

1. **Check Activation Context Count**
   ```bash
   python3 << 'EOF'
   import yaml
   import sys

   skill_file = '.claude/skills/[skill-name]/SKILL.md'
   with open(skill_file, 'r') as f:
       content = f.read()
       data = yaml.safe_load(content.split('---')[1])

       contexts = data.get('activation_context', [])

       if len(contexts) < 3:
           print(f"❌ Too few activation contexts ({len(contexts)}), need ≥3")
           sys.exit(1)

       print(f"✅ Activation contexts: {len(contexts)}")
       for ctx in contexts:
           print(f"   - '{ctx}'")
   EOF
   ```

2. **Check for Vague/Generic Triggers**

   ❌ **Avoid Generic Triggers:**
   - "help"
   - "code"
   - "test" (too broad)
   - "create"
   - "implement"

   ✅ **Use Specific Triggers:**
   - "create tutorial"
   - "write test for"
   - "TUTORIAL_INDEX"
   - "parallel processing"
   - "TDD workflow"

3. **Check for Overlaps with Other Skills**
   ```bash
   # List all activation contexts across skills
   for skill in .claude/skills/*/SKILL.md; do
       echo "=== $(basename $(dirname $skill)) ==="
       python3 << EOF
import yaml
with open('$skill', 'r') as f:
    data = yaml.safe_load(f.read().split('---')[1])
    for ctx in data.get('activation_context', []):
        print(f"  - {ctx}")
EOF
   done
   ```

   Review output for overlapping triggers that could cause conflicts.

**Checklist:**
- [ ] ≥3 activation contexts defined
- [ ] No generic/vague triggers (help, code, test)
- [ ] All triggers are specific and meaningful
- [ ] No significant overlaps with other skills (check manually)
- [ ] Multi-word phrases used where appropriate

---

### 5. File Structure & Organization

**Requirement:** Skill directories must follow standard structure.

**Validation Steps:**

1. **Check Directory Structure**
   ```bash
   skill_dir=".claude/skills/[skill-name]"

   # Required files/directories
   required=(
       "$skill_dir/SKILL.md"
       "$skill_dir/references"
       "$skill_dir/examples"
   )

   missing=()
   for item in "${required[@]}"; do
       if [ ! -e "$item" ]; then
           missing+=("$item")
       fi
   done

   if [ ${#missing[@]} -gt 0 ]; then
       echo "❌ Missing required files/directories:"
       printf '   - %s\n' "${missing[@]}"
       exit 1
   fi

   echo "✅ Directory structure valid"
   ```

2. **Verify Reference Files Exist**
   ```bash
   skill_dir=".claude/skills/[skill-name]"

   if [ ! "$(ls -A $skill_dir/references/ 2>/dev/null)" ]; then
       echo "⚠️  Warning: references/ directory is empty"
   else
       echo "✅ Reference files present:"
       ls -1 "$skill_dir/references/"
   fi
   ```

3. **Verify Example Files Exist**
   ```bash
   skill_dir=".claude/skills/[skill-name]"

   if [ ! "$(ls -A $skill_dir/examples/ 2>/dev/null)" ]; then
       echo "⚠️  Warning: examples/ directory is empty"
   else
       echo "✅ Example files present:"
       ls -1 "$skill_dir/examples/"
   fi
   ```

**Checklist:**
- [ ] SKILL.md exists
- [ ] references/ directory exists
- [ ] examples/ directory exists
- [ ] At least 1 reference file present
- [ ] At least 1 example file present (if examples defined in YAML)
- [ ] No extraneous files (follow naming conventions)

---

### 6. Documentation Quality

**Requirement:** SKILL.md must be well-documented with clear purpose and guidance.

**Manual Review Checklist:**

- [ ] **Purpose Section**: Clearly explains what the skill does
- [ ] **Activation Section**: Describes when skill activates
- [ ] **Guidance Section**: Lists what guidance is provided
- [ ] **Examples Section**: Provides real usage examples
- [ ] **Markdown Quality**:
  - [ ] Headers follow hierarchy (H1 > H2 > H3)
  - [ ] Code blocks have language tags
  - [ ] Links are valid and use relative paths
  - [ ] Lists are properly formatted
- [ ] **Readability**:
  - [ ] Clear, concise language
  - [ ] No jargon without explanation
  - [ ] Actionable guidance (not just theory)
- [ ] **Completeness**:
  - [ ] All activation contexts explained
  - [ ] All references justified (why each is needed)
  - [ ] Examples demonstrate key scenarios

---

## Complete Validation Script

**Run all validation checks:**

```bash
#!/bin/bash

SKILL_NAME="[skill-name]"
SKILL_DIR=".claude/skills/$SKILL_NAME"
SKILL_FILE="$SKILL_DIR/SKILL.md"

echo "============================================"
echo "Quality Validation: $SKILL_NAME"
echo "============================================"

# 1. YAML Validation
echo -e "\n[1/6] YAML Frontmatter Validation"
python3 << EOF
import yaml
import sys
import re

with open('$SKILL_FILE', 'r') as f:
    content = f.read()
    parts = content.split('---')

    if len(parts) < 3:
        print("❌ No YAML frontmatter found")
        sys.exit(1)

    try:
        data = yaml.safe_load(parts[1])
    except yaml.YAMLError as e:
        print(f"❌ YAML parse error: {e}")
        sys.exit(1)

    # Check required fields
    required = ['name', 'version', 'description', 'activation_context']
    missing = [f for f in required if f not in data]
    if missing:
        print(f"❌ Missing fields: {missing}")
        sys.exit(1)

    # Check version format
    if not re.match(r'^\d+\.\d+\.\d+$', data['version']):
        print(f"❌ Invalid version format: {data['version']}")
        sys.exit(1)

    # Check activation context count
    if len(data.get('activation_context', [])) < 3:
        print(f"❌ Too few activation contexts: {len(data['activation_context'])}")
        sys.exit(1)

    print(f"✅ YAML valid - {data['name']} v{data['version']}")
    print(f"   Activation contexts: {len(data['activation_context'])}")
EOF

if [ $? -ne 0 ]; then
    echo "FAILED: YAML validation"
    exit 1
fi

# 2. Reference Validation
echo -e "\n[2/6] Reference Existence Validation"
python3 << EOF
import yaml
import os
import sys

with open('$SKILL_FILE', 'r') as f:
    content = f.read()
    data = yaml.safe_load(content.split('---')[1])

    references = data.get('references', [])
    missing = []

    for ref in references:
        path = ref.get('path', '').split('#')[0]
        if path and not os.path.exists(path):
            missing.append(path)

    if missing:
        print(f"❌ Missing reference files: {missing}")
        sys.exit(1)

    print(f"✅ All {len(references)} references valid")
EOF

if [ $? -ne 0 ]; then
    echo "FAILED: Reference validation"
    exit 1
fi

# 3. Example Validation
echo -e "\n[3/6] Example File Validation"
python3 << EOF
import yaml
import os
import sys

with open('$SKILL_FILE', 'r') as f:
    content = f.read()
    data = yaml.safe_load(content.split('---')[1])

    examples = data.get('examples', [])
    missing = []

    for ex in examples:
        path = ex.get('path', '')
        full_path = os.path.join('$SKILL_DIR', path)
        if path and not os.path.exists(full_path):
            missing.append(path)

    if missing:
        print(f"❌ Missing example files: {missing}")
        sys.exit(1)

    print(f"✅ All {len(examples)} examples valid")
EOF

if [ $? -ne 0 ]; then
    echo "FAILED: Example validation"
    exit 1
fi

# 4. Directory Structure
echo -e "\n[4/6] Directory Structure Validation"
if [ ! -d "$SKILL_DIR/references" ]; then
    echo "❌ Missing references/ directory"
    exit 1
fi
if [ ! -d "$SKILL_DIR/examples" ]; then
    echo "❌ Missing examples/ directory"
    exit 1
fi
echo "✅ Directory structure valid"

# 5. Content Duplication Check (manual review reminder)
echo -e "\n[5/6] Content Duplication Check"
echo "⚠️  Manual review required:"
echo "   - Check for duplicated content from CLAUDE.md"
echo "   - Check for duplicated content from patterns/"
echo "   - Verify references used instead of full content"

# 6. Documentation Quality (manual review reminder)
echo -e "\n[6/6] Documentation Quality Check"
echo "⚠️  Manual review required:"
echo "   - Purpose section clear"
echo "   - Activation contexts explained"
echo "   - Guidance is actionable"
echo "   - Examples are relevant"

echo -e "\n============================================"
echo "Automated checks: ✅ PASSED"
echo "Manual review: Required (see warnings above)"
echo "============================================"
```

**Save as:** `.claude/skills/validate_skill.sh`

**Usage:**
```bash
chmod +x .claude/skills/validate_skill.sh
./.claude/skills/validate_skill.sh
```

---

## Quality Gate Summary

### Before Moving to Integration Testing:

- [ ] **All automated checks pass** (YAML, references, examples, structure)
- [ ] **Manual review complete** (no duplication, good documentation)
- [ ] **Isolation testing passed** (see SKILL_ISOLATION_TESTING.md)
- [ ] **Test report created** (TEST_REPORT.md in skill directory)

### Before Production Deployment:

- [ ] All quality validation checks pass
- [ ] Isolation testing complete
- [ ] Integration testing complete
- [ ] All test scenarios documented
- [ ] Version number finalized
- [ ] CHANGELOG updated (if skill directory has one)

---

**Last Updated:** 2025-11-18
**Used For:** All skills before deployment
