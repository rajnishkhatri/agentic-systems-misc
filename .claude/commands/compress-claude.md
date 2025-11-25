# /compress-claude Command

**Version:** 1.0.0
**Category:** Project Maintenance & Optimization
**Purpose:** Iteratively compress CLAUDE.md by extracting content to modular files with `@` imports

---

## Overview

The `/compress-claude` command helps optimize CLAUDE.md by identifying verbose sections and extracting them to separate files, replacing them with concise summaries and `@` import references. This reduces context window pressure while maintaining full content accessibility.

**Key Benefits:**
- **Reduced token usage:** 35-50% compression ratio
- **Faster AI parsing:** Smaller main file, just-in-time imports
- **Better maintainability:** Update patterns once, reference everywhere
- **No data loss:** All content preserved in modular files

---

## Usage

```bash
/compress-claude [action] [optional: target]
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| action | string | Yes | One of: `analyze`, `extract`, `validate`, `revert` |
| target | string | No | Specific section to extract (e.g., `tdd`, `context-engineering`) |

---

## Actions

### 1. Analyze

**Command:** `/compress-claude analyze`

**Purpose:** Scan CLAUDE.md for compression opportunities and generate a report.

**What it does:**
1. Read CLAUDE.md and count lines/tokens
2. Identify sections >100 lines
3. Calculate potential compression ratios
4. Generate recommendations ranked by impact

**Output format:**
```
📊 CLAUDE.md Compression Analysis

Current State:
  File: CLAUDE.md
  Lines: 710
  Estimated Tokens: ~14,000
  Context Window Usage: 17.5% (assuming 80K context)

Compression Opportunities:

1. TDD Principles (lines 33-260) [HIGH PRIORITY]
   Current: 227 lines (~4,500 tokens)
   Target: 15 lines (~300 tokens)
   Compression: 93% (212 lines saved)
   Recommendation: Extract to .claude/instructions/tdd-principles.md
   Reason: Detailed methodology, already documented in patterns/tdd-workflow.md

2. Context Engineering (lines 349-583) [HIGH PRIORITY]
   Current: 235 lines (~4,700 tokens)
   Target: 50 lines (~1,000 tokens)
   Compression: 79% (185 lines saved)
   Recommendation: Extract to .claude/instructions/context-engineering.md
   Reason: Duplicate tables from google-context/TERMINOLOGY.md

3. Tutorial Workflow (lines 585-674) [MEDIUM PRIORITY]
   Current: 90 lines (~1,800 tokens)
   Target: 40 lines (~800 tokens)
   Compression: 56% (50 lines saved)
   Recommendation: Extract to .claude/instructions/tutorial-workflow.md
   Reason: Detailed development workflow, can be summarized

Total Potential Savings:
  Lines: 447 saved (63% reduction)
  Tokens: ~9,000 saved (64% reduction)
  Final Size: 263 lines (~5,000 tokens)

Next Steps:
  1. Review recommendations
  2. Run: /compress-claude extract [section-name]
  3. Validate: /compress-claude validate
```

**Implementation:**
- Use regex to identify section boundaries: `^##\s+(.+)$`
- Count lines between sections
- Estimate tokens: `lines × 20` (rough approximation)
- Flag sections >100 lines as compression candidates
- Prioritize by size and duplication

---

### 2. Extract

**Command:** `/compress-claude extract [section]`

**Purpose:** Extract a specific section to a modular file and replace with summary + import.

**Supported sections:**
- `tdd` → TDD Principles (lines 33-260)
- `context-engineering` → Context Engineering Principles (lines 349-583)
- `tutorial-workflow` → Tutorial Workflow (lines 585-674)
- `all` → Extract all recommended sections

**What it does:**
1. Create `.claude/instructions/` directory if not exists
2. Create backup in `.claude/instructions/backup/CLAUDE.md.backup-[timestamp]`
3. Extract section content to new file
4. Generate 3-5 line summary (using section headers + key points)
5. Replace original section with summary + `@` import
6. Update cross-references if needed
7. Report results

**Example: `/compress-claude extract tdd`**

**Before (CLAUDE.md lines 33-260):**
```markdown
## Development Principles

1. **TDD Always**:
# TDD Mode: RED → GREEN → REFACTOR

## You MUST follow Test-Driven Development strictly:

### TDD Rules:
**RED**: Write ONE failing test
- Create test for single behavior
[... 200+ lines of detailed TDD methodology ...]
```

**After (CLAUDE.md lines 33-48):**
```markdown
## Development Principles

**TDD & Defensive Coding:** See @.claude/instructions/tdd-principles.md

**Quick Reference:**
1. **TDD Always:** Follow RED → GREEN → REFACTOR cycle
   - RED: Write ONE failing test (`test_should_[result]_when_[condition]`)
   - GREEN: Minimal code to pass
   - REFACTOR: Apply defensive coding

2. **Defensive Function Template:**
   - Type checking → Input validation → Edge cases → Main logic → Return
   - Mandatory: Type hints, docstrings, error handling

3. **Test Naming:** `test_should_[expected_result]_when_[condition]()`

**For full details:** @.claude/instructions/tdd-principles.md
```

**New file (.claude/instructions/tdd-principles.md):**
```markdown
# TDD Principles & Defensive Coding

**Source:** Extracted from CLAUDE.md (lines 33-260)
**Last Updated:** 2025-11-23

[... Full 227 lines of TDD methodology preserved ...]
```

**Output format:**
```
✅ Section Extracted Successfully

Action: extract tdd
Source: CLAUDE.md (lines 33-260)
Target: .claude/instructions/tdd-principles.md
Backup: .claude/instructions/backup/CLAUDE.md.backup-20251123-143022

Changes:
  Original: 227 lines
  Summary: 15 lines
  Extracted: 227 lines (preserved)
  Savings: 212 lines (93% compression)

CLAUDE.md updated with:
  - 15-line summary with quick reference
  - @.claude/instructions/tdd-principles.md import

Next Steps:
  1. Review: .claude/instructions/tdd-principles.md
  2. Test import: Read CLAUDE.md and verify content loads
  3. Validate: /compress-claude validate
```

**Safety Features:**
- Always create backup before modification
- Preserve 100% of content (no data loss)
- Atomic operation (revert if any step fails)
- Git-aware (warn if uncommitted changes in CLAUDE.md)

**Dry-run mode:**
```bash
/compress-claude extract tdd --dry-run
```
Shows what changes would be made without applying them.

---

### 3. Validate

**Command:** `/compress-claude validate`

**Purpose:** Verify all `@` imports resolve correctly and check for issues.

**What it does:**
1. Scan CLAUDE.md for all `@` import statements
2. Attempt to read each imported file
3. Check for circular imports (A imports B imports A)
4. Verify import depth ≤5 hops (Claude Code limit)
5. Test relative path resolution
6. Calculate total context size (main + imports)
7. Report any broken references

**Output format:**
```
🔍 CLAUDE.md Import Validation

Import Analysis:

✅ @.claude/instructions/tdd-principles.md
   Status: OK
   Size: 227 lines (~4,500 tokens)
   Depth: 1 hop
   Nested Imports: None

✅ @.claude/instructions/context-engineering.md
   Status: OK
   Size: 235 lines (~4,700 tokens)
   Depth: 1 hop
   Nested Imports:
     → @google-context/TERMINOLOGY.md (depth 2, OK)
     → @patterns/context-engineering-sessions.md (depth 2, OK)

✅ @.claude/instructions/tutorial-workflow.md
   Status: OK
   Size: 90 lines (~1,800 tokens)
   Depth: 1 hop
   Nested Imports: None

Total Context Size:
  CLAUDE.md: 263 lines (~5,000 tokens)
  Imports: 552 lines (~11,000 tokens)
  Total: 815 lines (~16,000 tokens)
  Max Depth: 2 hops (limit: 5)

✅ All imports valid
✅ No circular dependencies
✅ No broken references
✅ Within depth limit

Compression Summary:
  Original CLAUDE.md: 710 lines (~14,000 tokens)
  Compressed CLAUDE.md: 263 lines (~5,000 tokens)
  Reduction: 63% (447 lines saved)

  With imports loaded: 815 lines (~16,000 tokens)
  Net change: +105 lines (+2,000 tokens)

Note: Imports are loaded just-in-time. Not all imports are always
loaded simultaneously. Effective context depends on AI's current task.
```

**Error examples:**
```
❌ Import Validation Failed

✅ @.claude/instructions/tdd-principles.md (OK)
❌ @.claude/instructions/missing-file.md
   Error: File not found
   Fix: Check file path, ensure file exists

✅ @.claude/instructions/context-engineering.md (OK)
⚠️  @patterns/circular-import.md
   Warning: Circular import detected
   Chain: CLAUDE.md → circular-import.md → CLAUDE.md
   Fix: Remove circular reference

Summary: 2 OK, 1 ERROR, 1 WARNING
Fix issues before proceeding.
```

---

### 4. Revert

**Command:** `/compress-claude revert [section|all]`

**Purpose:** Undo extraction and restore original content to CLAUDE.md.

**Options:**
- `/compress-claude revert tdd` → Restore only TDD section
- `/compress-claude revert all` → Restore all extracted sections
- `/compress-claude revert --from-backup [timestamp]` → Restore from specific backup

**What it does:**
1. Read extracted content from `.claude/instructions/[section].md`
2. Locate import statement in CLAUDE.md
3. Replace import + summary with original full content
4. Delete extracted file (optional, prompt user)
5. Create restore backup (safety)
6. Report results

**Output format:**
```
🔄 Section Restored

Action: revert tdd
Source: .claude/instructions/tdd-principles.md
Target: CLAUDE.md (lines 33-48 expanded)
Backup: .claude/instructions/backup/CLAUDE.md.backup-20251123-150022

Changes:
  Summary: 15 lines (removed)
  Restored: 227 lines
  Net change: +212 lines

CLAUDE.md updated:
  - Import @.claude/instructions/tdd-principles.md removed
  - Full TDD principles restored inline

Extracted file:
  .claude/instructions/tdd-principles.md preserved (use --delete to remove)

Next Steps:
  1. Review: CLAUDE.md (verify content restored)
  2. Clean up: rm .claude/instructions/tdd-principles.md (optional)
```

**Safety Features:**
- Always create backup before revert
- Preserve extracted file by default (use `--delete` flag to remove)
- Atomic operation (revert if any step fails)

---

## Compression Strategy

### Target Sections

| Section | Lines | Compression | Extracted To |
|---------|-------|-------------|--------------|
| TDD Principles | 227 → 15 | 93% | `.claude/instructions/tdd-principles.md` |
| Context Engineering | 235 → 50 | 79% | `.claude/instructions/context-engineering.md` |
| Tutorial Workflow | 90 → 40 | 56% | `.claude/instructions/tutorial-workflow.md` |

### What to Extract

**Candidates for extraction (>100 lines):**
- ✅ Detailed methodologies (TDD workflow)
- ✅ Duplicate content (Context Engineering tables from TERMINOLOGY.md)
- ✅ Procedural workflows (Tutorial development)
- ✅ Extended examples (Defensive function templates)

**Keep inline (<100 lines, frequently referenced):**
- ❌ Project Philosophy (concise)
- ❌ Available Workflows (quick reference)
- ❌ Pattern Library table (already compressed)
- ❌ Quality Standards (brief)
- ❌ Bhagavad Gita guidelines (domain-specific)

### Resulting CLAUDE.md Structure

```markdown
# Claude Code Instructions

## 📚 Quick Navigation
- [TDD & Defensive Coding](#development-principles) → @.claude/instructions/tdd-principles.md
- [Context Engineering](#context-engineering-principles) → @.claude/instructions/context-engineering.md
- [Tutorial Workflow](#tutorial-workflow) → @.claude/instructions/tutorial-workflow.md
- [Pattern Library](#pattern-library) → Use /pattern command
- [Bhagavad Gita Chatbot](#bhagavad-gita-chatbot-specific-guidelines) → Inline

---

## Project Philosophy
[Keep inline: 10 lines]

## Available Workflows
[Keep inline: 20 lines]

## Development Principles
**See:** @.claude/instructions/tdd-principles.md
**Quick Reference:** [3-5 bullet points]

## Pattern Library
[Keep inline: 44 lines - already optimized]

## Context Engineering Principles
**See:** @.claude/instructions/context-engineering.md
**Quick Reference:** [Core thesis + 5 bullet points]

## Tutorial Workflow
**See:** @.claude/instructions/tutorial-workflow.md
**Quick Links:** [3 learning paths as bullets]

## Bhagavad Gita Chatbot
[Keep inline: domain-specific, frequently referenced]
```

---

## Best Practices

### When to Compress

**Triggers:**
- CLAUDE.md exceeds 500 lines
- Sections duplicated across files
- AI assistants take >5s to parse instructions
- Frequently referenced content buried in verbose sections

**Process:**
1. Run `/compress-claude analyze` to identify opportunities
2. Review recommendations (prioritize HIGH impact)
3. Extract one section at a time (`/compress-claude extract [section]`)
4. Validate after each extraction (`/compress-claude validate`)
5. Test AI assistant behavior (does it still find info quickly?)
6. Commit changes with clear message

### When NOT to Compress

**Anti-patterns:**
- ❌ Extracting frequently-used quick references
- ❌ Creating deep import chains (>3 hops)
- ❌ Splitting related content across multiple files
- ❌ Compressing sections <50 lines (overhead not worth it)

### Maintenance

**Periodic reviews:**
- Monthly: Run `/compress-claude analyze` to check for new opportunities
- After major features: Check if new sections need extraction
- When AI asks repeated questions: Missing context → restore or improve summary

**Update triggers:**
- Adding new major sections (>100 lines) → Consider extraction
- Refactoring patterns → Update imports
- Removing features → Clean up extracted files

---

## Examples

### Example 1: First-time compression

```bash
# Step 1: Analyze
/compress-claude analyze

# Output shows 3 high-priority sections
# Recommendation: Extract tdd (227 lines, 93% compression)

# Step 2: Extract TDD section
/compress-claude extract tdd

# Output: 212 lines saved, backup created

# Step 3: Validate
/compress-claude validate

# Output: All imports OK, 63% compression achieved

# Step 4: Test
# Read CLAUDE.md - verify you can still understand TDD principles
# AI should auto-load @.claude/instructions/tdd-principles.md when needed

# Step 5: Commit
git add CLAUDE.md .claude/instructions/
git commit -m "docs: compress CLAUDE.md TDD section (93% reduction)"
```

### Example 2: Extract all recommended sections

```bash
# Extract all high-priority sections at once
/compress-claude extract all

# Output:
#   - tdd → .claude/instructions/tdd-principles.md (212 lines saved)
#   - context-engineering → .claude/instructions/context-engineering.md (185 lines saved)
#   - tutorial-workflow → .claude/instructions/tutorial-workflow.md (50 lines saved)
# Total: 447 lines saved (63% reduction)

# Validate
/compress-claude validate

# Output: All imports OK, no circular dependencies
```

### Example 3: Revert if issues found

```bash
# Extract section
/compress-claude extract tdd

# Test - AI can't find TDD info quickly
# Revert to inline

/compress-claude revert tdd

# Output: Content restored, extraction undone

# Alternative: Improve summary instead of reverting
# Edit CLAUDE.md summary to add more detail
```

### Example 4: Dry-run before applying

```bash
# See what would happen without making changes
/compress-claude extract context-engineering --dry-run

# Output:
#   Would extract: lines 349-583 (235 lines)
#   Would create: .claude/instructions/context-engineering.md
#   Would replace with: 50-line summary
#   Savings: 185 lines (79%)
#   [Shows exact diff preview]

# If satisfied, run without --dry-run
/compress-claude extract context-engineering
```

---

## Troubleshooting

### "Import not loading content"

**Symptom:** AI says "I don't see TDD instructions" after extraction

**Diagnosis:**
1. Check import syntax: `@.claude/instructions/tdd-principles.md` (no spaces)
2. Verify file exists: `ls .claude/instructions/tdd-principles.md`
3. Check file permissions: `chmod 644 .claude/instructions/tdd-principles.md`
4. Validate imports: `/compress-claude validate`

**Fix:**
- Ensure `@` import is not inside code block
- Use relative path from repo root
- Check max depth (must be ≤5 hops)

### "Circular import detected"

**Symptom:** `/compress-claude validate` reports circular dependency

**Diagnosis:**
- CLAUDE.md imports A.md
- A.md imports B.md
- B.md imports CLAUDE.md (circular!)

**Fix:**
- Break circular chain: Remove import from B.md
- Restructure: Create shared C.md imported by both A and B
- Inline content: If small, duplicate content instead of importing

### "Too many nested imports (depth >5)"

**Symptom:** Claude Code stops resolving imports after 5 hops

**Diagnosis:**
- Import chain too deep: CLAUDE.md → A → B → C → D → E → F (6 hops)

**Fix:**
- Flatten structure: Merge intermediate files
- Direct imports: Import F directly from CLAUDE.md
- Reduce nesting: Aim for ≤3 hops

### "Context still too large after compression"

**Symptom:** CLAUDE.md + imports exceed 20K tokens

**Diagnosis:**
- Summaries too verbose
- Too many imports loaded simultaneously
- Extracted files still large

**Fix:**
- Shorten summaries (5 lines max)
- Split extracted files further (tdd-principles.md → tdd-red-phase.md, tdd-green-phase.md)
- Use lazy loading: Only import when needed (not at top of CLAUDE.md)

---

## Integration with Other Commands

**Complementary commands:**
- `/pattern` - Manage Pattern Library (alternative to inline patterns)
- `/docs` - Generate documentation (can extract to docs/ instead of .claude/instructions/)
- `/review` - Code review finds duplication → suggests compression
- `/reflect` - Post-implementation analysis → updates CLAUDE.md

**Workflow:**
1. Build feature with `/work`
2. Update CLAUDE.md with new guidelines
3. Run `/compress-claude analyze` to check if CLAUDE.md growing too large
4. Extract verbose sections with `/compress-claude extract`
5. Commit with `/reflect` for changelog

---

## Technical Implementation

### File Structure

```
.claude/
├── commands/
│   └── compress-claude.md (this file)
├── instructions/ (created by extract action)
│   ├── backup/
│   │   └── CLAUDE.md.backup-20251123-143022
│   ├── tdd-principles.md
│   ├── context-engineering.md
│   └── tutorial-workflow.md
└── CLAUDE.md (compressed)
```

### Import Syntax

**Valid:**
```markdown
See @.claude/instructions/tdd-principles.md
@patterns/tdd-workflow.md
@~/.claude/personal-preferences.md (user home directory)
```

**Invalid:**
```markdown
See @ .claude/instructions/tdd-principles.md (space after @)
@.claude/instructions/tdd-principles.md inside `code block` (ignored)
```

### Token Estimation

**Approximation:**
- 1 line ≈ 20 tokens (varies by content)
- 100 lines ≈ 2,000 tokens
- 500 lines ≈ 10,000 tokens

**Accurate:**
- Use Claude's token counting API
- Command uses approximation for speed

---

## Version History

**1.0.0** (2025-11-23)
- Initial implementation
- Support for analyze, extract, validate, revert actions
- Safety features: backups, dry-run mode, git-awareness
- Compression strategy for TDD, Context Engineering, Tutorial Workflow sections
- Integration with @ import syntax (max-depth: 5 hops)
