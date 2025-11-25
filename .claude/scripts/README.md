# CLAUDE.md Compression Scripts

This directory contains scripts for optimizing CLAUDE.md by extracting verbose sections to modular files with `@` imports.

## Quick Start

```bash
# Analyze current compression (dry-run)
python .claude/scripts/compress-claude-extract.py tdd --dry-run

# Extract TDD section
python .claude/scripts/compress-claude-extract.py tdd

# Extract all sections
python .claude/scripts/compress-claude-extract.py all

# Run tests
pytest .claude/scripts/test_compress_extract.py -v
```

## Available Sections

1. **tdd** - TDD principles and defensive coding patterns (229 lines)
2. **context-engineering** - Context engineering patterns (145 lines)
3. **tutorial-workflow** - Tutorial development workflow (92 lines)

## How It Works

### Extraction Process

1. **Reads CLAUDE.md** and locates section by markers
2. **Creates backup** in `.claude/instructions/backup/`
3. **Extracts content** to `.claude/instructions/[section].md`
4. **Replaces section** with summary + `@import` statement
5. **Reports metrics** (lines saved, compression %)

### Import Resolution

Claude Code resolves `@` imports at runtime using "just-in-time" loading:

```markdown
**Full Documentation:** @.claude/instructions/tdd-principles.md
```

When Claude Code encounters this import, it loads the content from the referenced file.

## Compression Results

**Current State:**
- CLAUDE.md: 396 lines (down from 717 lines)
- Reduction: 321 lines (44.8%)
- Extracted modules: 466 lines total
- Total with imports: 862 lines (120% of original, but modular)

**Trade-off:** Smaller main file (faster parsing) vs. larger total context when imports loaded.

## Safety Features

- **Automatic backups** before any modification
- **Dry-run mode** to preview changes (`--dry-run`)
- **Section markers** prevent accidental over-extraction
- **Defensive coding** with type hints and input validation

## Testing

Run the test suite to validate extraction logic:

```bash
pytest .claude/scripts/test_compress_extract.py -v
```

**Test Coverage:**
- ✅ Section boundary detection
- ✅ Error handling (missing markers)
- ✅ Section config validation
- ✅ Import path matching
- ✅ Dry-run mode

## Maintenance

### Adding New Sections

To add a new extractable section, update `SECTIONS` dict in `compress-claude-extract.py`:

```python
SECTIONS = {
    "new-section": {
        "start_marker": "## New Section Title",
        "end_marker": "## Next Section Title",
        "summary": """## New Section Title

**Full Documentation:** @.claude/instructions/new-section.md

**Quick Reference:**
1. Key point 1
2. Key point 2

**For full details:** @.claude/instructions/new-section.md
""",
        "target": ".claude/instructions/new-section.md",
        "description": "Brief description of section",
    }
}
```

### Reverting Extraction

To restore original content:

1. Locate backup: `.claude/instructions/backup/CLAUDE.md.backup-[timestamp]`
2. Copy backup to CLAUDE.md: `cp .claude/instructions/backup/CLAUDE.md.backup-20251123-120000 CLAUDE.md`
3. Remove extracted file: `rm .claude/instructions/[section].md`

## Implementation Status

- ✅ **P0 Complete:** Manual TDD extraction (proof of concept)
- ✅ **P0 Complete:** @ import resolution tests
- ✅ **P1 Complete:** Extract action MVP script
- ⏳ **P2 Pending:** Frequency analysis for compression targets
- ⏳ **P3 Pending:** Analyze action (section identification)
- ⏳ **P3 Pending:** Token counting integration

## Related Documentation

- [COMPRESS_CLAUDE_REFLECTION.md](../google-context/COMPRESS_CLAUDE_REFLECTION.md) - Design rationale
- [IMPORT_TEST_RESULTS.md](../.claude/IMPORT_TEST_RESULTS.md) - Import resolution validation
- [compress-claude.md](../commands/compress-claude.md) - Full command specification (667 lines)

## Lessons Learned

From the reflection document (COMPRESS_CLAUDE_REFLECTION.md):

1. **MVP First:** Implemented `extract` action first, defer `analyze`/`validate`/`revert` for later
2. **Proof of Concept:** Manual extraction validated design assumptions before automation
3. **Test Core Assumptions:** Import resolution tests confirmed `@` syntax works as documented
4. **Defensive Coding:** Type hints, input validation, comprehensive error handling throughout

---

**Generated:** 2025-11-23
**Status:** MVP Complete (P1), ready for production use
