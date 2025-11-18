#!/bin/bash

# Skill Quality Validation Script
# Usage: ./validate_skill.sh <skill-name>

if [ -z "$1" ]; then
    echo "Usage: ./validate_skill.sh <skill-name>"
    echo "Example: ./validate_skill.sh tutorial-standards"
    exit 1
fi

SKILL_NAME="$1"
SKILL_DIR=".claude/skills/$SKILL_NAME"
SKILL_FILE="$SKILL_DIR/SKILL.md"

echo "============================================"
echo "Quality Validation: $SKILL_NAME"
echo "============================================"

# Check if skill exists
if [ ! -f "$SKILL_FILE" ]; then
    echo "❌ Skill not found: $SKILL_FILE"
    exit 1
fi

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
