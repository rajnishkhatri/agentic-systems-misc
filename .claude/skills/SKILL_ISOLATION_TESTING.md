# Skill Isolation Testing Workflow

This document defines the systematic workflow for testing skills in isolation before enabling them in production.

## Purpose

Testing skills in isolation ensures:
- Each skill activates correctly on intended triggers
- No unintended activations occur
- Guidance is accurate and references are valid
- Skills don't interfere with normal Claude Code operation

## Isolation Testing Principles

1. **One Skill at a Time**: Test each skill independently before combining
2. **Clean Environment**: Start fresh Claude session for each test
3. **Documented Results**: Record all test outcomes in TESTING_SCENARIOS.md
4. **Pass Criteria**: All test scenarios must pass before moving to next skill
5. **Rollback Ready**: Know how to disable skill if issues arise

## Testing Workflow

### Phase 1: Pre-Test Setup

#### Step 1.1: Prepare Skill Directory
```bash
# Ensure skill has all required components
ls -la .claude/skills/[skill-name]/
# Should contain:
# - SKILL.md (with valid YAML frontmatter)
# - references/ directory (with all referenced files)
# - examples/ directory (with all example files)
```

#### Step 1.2: Validate YAML Frontmatter
```bash
# Parse YAML to check for syntax errors
python3 << 'EOF'
import yaml
import sys

skill_file = '.claude/skills/[skill-name]/SKILL.md'
try:
    with open(skill_file, 'r') as f:
        content = f.read()
        # Extract YAML frontmatter (between first two ---)
        parts = content.split('---')
        if len(parts) >= 3:
            yaml_content = parts[1]
            data = yaml.safe_load(yaml_content)

            # Check required fields
            required = ['name', 'version', 'description', 'activation_context']
            missing = [f for f in required if f not in data]

            if missing:
                print(f"❌ Missing required fields: {missing}")
                sys.exit(1)

            print(f"✅ YAML valid for skill: {data['name']}")
            print(f"   Version: {data['version']}")
            print(f"   Activation contexts: {len(data['activation_context'])}")
        else:
            print("❌ No YAML frontmatter found")
            sys.exit(1)
except Exception as e:
    print(f"❌ YAML validation failed: {e}")
    sys.exit(1)
EOF
```

#### Step 1.3: Validate Reference Paths
```bash
# Check all reference paths exist
python3 << 'EOF'
import yaml
import os

skill_file = '.claude/skills/[skill-name]/SKILL.md'
with open(skill_file, 'r') as f:
    content = f.read()
    yaml_content = content.split('---')[1]
    data = yaml.safe_load(yaml_content)

    references = data.get('references', [])
    missing = []

    for ref in references:
        path = ref['path']
        # Handle paths with anchors (e.g., CLAUDE.md#tdd-mode)
        file_path = path.split('#')[0]

        if not os.path.exists(file_path):
            missing.append(file_path)

    if missing:
        print(f"❌ Missing reference files: {missing}")
    else:
        print(f"✅ All {len(references)} reference paths valid")
EOF
```

#### Step 1.4: Validate Example Paths
```bash
# Check all example paths exist
python3 << 'EOF'
import yaml
import os

skill_file = '.claude/skills/[skill-name]/SKILL.md'
with open(skill_file, 'r') as f:
    content = f.read()
    yaml_content = content.split('---')[1]
    data = yaml.safe_load(yaml_content)

    examples = data.get('examples', [])
    missing = []

    skill_dir = os.path.dirname(skill_file)
    for ex in examples:
        path = ex['path']
        full_path = os.path.join(skill_dir, path)

        if not os.path.exists(full_path):
            missing.append(path)

    if missing:
        print(f"❌ Missing example files: {missing}")
    else:
        print(f"✅ All {len(examples)} example paths valid")
EOF
```

### Phase 2: Isolation Testing

#### Step 2.1: Disable All Other Skills
```bash
# Temporarily disable other skills to ensure isolation
# Move skills to _DISABLED_ prefix (they won't activate)
cd .claude/skills/

# Disable all except the one being tested
for skill in */; do
    if [ "$skill" != "[skill-name]/" ] && [ ! -f "${skill}_DISABLED" ]; then
        mv "$skill" "_DISABLED_$skill"
        echo "Disabled: $skill"
    fi
done
```

#### Step 2.2: Start Clean Claude Session
```
1. Close all existing Claude Code sessions
2. Open new terminal/IDE window
3. Start fresh Claude Code session
4. Verify skill directory state: ls .claude/skills/
```

#### Step 2.3: Run Test Scenarios

**For each test scenario in TESTING_SCENARIOS.md:**

1. **Execute Test Input**
   - Type the exact user input from test scenario
   - Observe Claude's response

2. **Verify Activation**
   - [ ] Did skill activate? (Yes/No)
   - [ ] Was activation expected? (Yes/No)
   - [ ] Match expected behavior? (Yes/No/Partial)

3. **Verify Guidance**
   - [ ] Correct guidance provided?
   - [ ] All expected references shown?
   - [ ] All expected examples provided?
   - [ ] No content duplication from CLAUDE.md?

4. **Document Results**
   - Update TESTING_SCENARIOS.md with actual behavior
   - Mark test as Pass/Fail/Partial
   - Add notes on any issues or observations

5. **Record Issues**
   - If test fails, document:
     - What went wrong
     - Expected vs. actual behavior
     - Possible causes
     - Fix needed

#### Step 2.4: Test Negative Cases

**Run queries that should NOT activate the skill:**

```
Test queries that don't match activation context:
- [List 3-5 queries unrelated to this skill]

Expected: Skill should NOT activate
Actual: [Record behavior]
```

#### Step 2.5: Test Edge Cases

**Run queries with overlapping keywords:**

```
Test queries with keywords from multiple skills:
- [List 2-3 queries with ambiguous context]

Expected: [Which skill should activate, if any]
Actual: [Record behavior]
```

### Phase 3: Pass/Fail Criteria

#### Passing Criteria (All must be true)

- ✅ All positive test scenarios activate correctly
- ✅ All negative test scenarios do NOT activate
- ✅ Guidance matches expected behavior (100% or with acceptable deviations documented)
- ✅ All references are valid and accessible
- ✅ All examples exist and are relevant
- ✅ No content duplication detected
- ✅ No unintended activations observed
- ✅ Skill does not interfere with normal Claude operation

#### Failing Criteria (Any one fails the test)

- ❌ Skill fails to activate on intended trigger
- ❌ Skill activates on unintended trigger
- ❌ Guidance is incorrect or misleading
- ❌ References are broken or missing
- ❌ Examples are broken or missing
- ❌ Content is duplicated from CLAUDE.md
- ❌ Skill interferes with normal operation

### Phase 4: Issue Resolution

#### If Test Fails:

1. **Document the Issue**
   - What failed?
   - Which test scenario?
   - What was expected vs. actual?

2. **Identify Root Cause**
   - YAML frontmatter error?
   - Activation context too broad/narrow?
   - Missing/broken references?
   - Content duplication?
   - Guidance incorrect?

3. **Fix the Issue**
   - Edit SKILL.md
   - Update references
   - Refine activation context
   - Remove duplicated content

4. **Re-Run Tests**
   - Start from Phase 1 (validation)
   - Re-run all test scenarios
   - Document new results

5. **Iterate Until Passing**
   - Repeat fix-test cycle
   - Document all changes
   - Update version in YAML if significant changes

### Phase 5: Re-Enable Other Skills

#### Once Skill Passes All Tests:

```bash
# Re-enable previously disabled skills
cd .claude/skills/

for skill in _DISABLED_*/; do
    new_name="${skill/_DISABLED_/}"
    mv "$skill" "$new_name"
    echo "Re-enabled: $new_name"
done
```

### Phase 6: Documentation

#### Update Test Execution Log

In TESTING_SCENARIOS.md, update:

```markdown
### Phase 1: Individual Skill Testing

| Skill | Date Tested | Tests Passed | Tests Failed | Status |
|-------|-------------|--------------|--------------|--------|
| [Skill Name] | 2025-11-18 | 4/4 | 0/4 | ✅ Passed |
```

#### Create Test Report

Create `.claude/skills/[skill-name]/TEST_REPORT.md`:

```markdown
# Test Report: [Skill Name]

**Test Date:** 2025-11-18
**Tester:** [Your name or "Automated"]
**Status:** ✅ Passed / ❌ Failed

## Summary

- Total test scenarios: X
- Passed: X
- Failed: X
- Partial: X

## Test Results

### Positive Tests (Should Activate)
- Test 1.1: ✅ Passed
- Test 1.2: ✅ Passed
[...]

### Negative Tests (Should NOT Activate)
- Test 1.4: ✅ Passed (correctly did not activate)
[...]

## Issues Found

[List any issues discovered during testing]

## Fixes Applied

[List any fixes made to resolve issues]

## Notes

[Any observations or recommendations]

## Sign-off

This skill has passed isolation testing and is ready for integration testing.

Tested by: [Name]
Date: 2025-11-18
```

## Testing Checklist Template

Use this checklist for each skill:

```markdown
## [Skill Name] Isolation Testing Checklist

### Pre-Test Validation
- [ ] YAML frontmatter valid
- [ ] All required fields present
- [ ] All reference paths exist
- [ ] All example paths exist
- [ ] Version follows semantic versioning

### Environment Setup
- [ ] All other skills disabled
- [ ] Fresh Claude session started
- [ ] Skill directory verified

### Test Execution
- [ ] All positive test scenarios run
- [ ] All negative test scenarios run
- [ ] Edge cases tested
- [ ] Results documented in TESTING_SCENARIOS.md

### Pass Criteria
- [ ] All positive tests activate correctly
- [ ] All negative tests do NOT activate
- [ ] Guidance is accurate
- [ ] References are valid
- [ ] No content duplication
- [ ] No unintended activations

### Documentation
- [ ] Test execution log updated
- [ ] TEST_REPORT.md created
- [ ] Issues documented (if any)
- [ ] Fixes documented (if any)

### Sign-off
- [ ] Skill passed all tests
- [ ] Ready for integration testing
- [ ] Other skills re-enabled

**Status:** [ ] Passed / [ ] Failed
**Date:** YYYY-MM-DD
```

## Quick Command Reference

### Disable Single Skill
```bash
mv .claude/skills/skill-name .claude/skills/_DISABLED_skill-name
```

### Enable Single Skill
```bash
mv .claude/skills/_DISABLED_skill-name .claude/skills/skill-name
```

### Validate All Skills
```bash
cd .claude/skills/
for skill in */SKILL.md; do
    echo "Validating: $skill"
    python3 << EOF
import yaml
with open('$skill', 'r') as f:
    yaml.safe_load(f.read().split('---')[1])
print("✅ Valid")
EOF
done
```

### List Active Skills
```bash
ls -d .claude/skills/*/ | grep -v "_DISABLED_"
```

### List Disabled Skills
```bash
ls -d .claude/skills/_DISABLED_*/ 2>/dev/null || echo "No disabled skills"
```

## Next Steps

After a skill passes isolation testing:
1. Move to **Integration Testing** (Phase 2 in TESTING_SCENARIOS.md)
2. Test with other skills enabled
3. Verify no conflicts or contradictory guidance
4. Document multi-skill activation behavior

---

**Last Updated:** 2025-11-18
**Used For:** All skills before production deployment
