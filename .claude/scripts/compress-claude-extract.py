#!/usr/bin/env python3
"""
Minimal viable extract action for /compress-claude command.

Usage: python .claude/scripts/compress-claude-extract.py [section]
  section: tdd | context-engineering | tutorial-workflow | all

Example:
  python .claude/scripts/compress-claude-extract.py tdd
  python .claude/scripts/compress-claude-extract.py all
"""

import os
import sys
from datetime import datetime
from typing import Any

# Section configurations (already extracted, but this allows re-extraction or new sections)
SECTIONS: dict[str, dict[str, Any]] = {
    "tdd": {
        "start_marker": "## Development Principles",
        "end_marker": "## Pattern Library",
        "summary": """## Development Principles

**TDD & Defensive Coding:** @.claude/instructions/tdd-principles.md

**Quick Reference:**
1. **TDD Always:** Follow RED → GREEN → REFACTOR cycle
2. **Defensive Function Template:** Type checking → Input validation → Edge cases → Main logic → Return
3. **Test Naming:** `test_should_[expected_result]_when_[condition]()`

**For full TDD & defensive coding details:** @.claude/instructions/tdd-principles.md
""",
        "target": ".claude/instructions/tdd-principles.md",
        "description": "TDD principles and defensive coding patterns",
    },
    "context-engineering": {
        "start_marker": "## Context Engineering Principles",
        "end_marker": "## Tutorial Workflow",
        "summary": """## Context Engineering Principles

**Full Documentation:** @.claude/instructions/context-engineering.md

**Core Thesis:** Intelligence emerges from orchestration, not just bigger models.

**Quick Reference:**
1. **Session History vs. Context Window:** Full conversation log (50K) vs. curated subset (8K)
2. **Memory vs. RAG:** User-specific facts vs. general knowledge retrieval
3. **Protected Context:** Turn 0, constraints, auth checkpoints must survive compression
4. **Memory Provenance:** Track source_session_id, confidence_score, validation_status
5. **PII Redaction:** Redact identifiers, preserve domain-specific terms (whitelist)

**Implementation Checklist:**
- [ ] Sessions pattern: Compress at 95% threshold, protect turn 0
- [ ] Memory provenance: Full lineage tracking with confidence evolution
- [ ] PII redaction: Email, phone, names → preserve Gita characters
- [ ] Token efficiency: Target 6x reduction (50K → 8K)
- [ ] Test coverage: ≥90% for sessions and memory modules

**For full context engineering details:** @.claude/instructions/context-engineering.md
""",
        "target": ".claude/instructions/context-engineering.md",
        "description": "Context engineering patterns and memory management",
    },
    "tutorial-workflow": {
        "start_marker": "## Tutorial Workflow",
        "end_marker": "## Working with GitHub",
        "summary": """## Tutorial Workflow

**Full Documentation:** @.claude/instructions/tutorial-workflow.md

**Quick Reference:**
Each homework/lesson has `TUTORIAL_INDEX.md` with learning objectives, recommended paths, and troubleshooting.

**Available Tutorials:**
- Homeworks: HW1-5 (Prompt Engineering → Agent Failure Analysis)
- Lessons: 4, 7-11 (Substantiation → Comparative Evaluation)
- Dashboard: `python lesson-9-11/evaluation_dashboard.py`

**Tutorial Quality Standards:**
- Reading time: 15-30 min per tutorial
- Execution time: <5 min for notebooks
- Real course datasets, not toy data

**For full tutorial workflow and development guidelines:** @.claude/instructions/tutorial-workflow.md
""",
        "target": ".claude/instructions/tutorial-workflow.md",
        "description": "Tutorial development and navigation workflow",
    },
}


def find_section_boundaries(lines: list[str], start_marker: str, end_marker: str) -> tuple[int, int]:
    """Find line numbers for section boundaries.

    Args:
        lines: List of lines from CLAUDE.md
        start_marker: String marking section start
        end_marker: String marking section end

    Returns:
        Tuple of (start_line, end_line)

    Raises:
        ValueError: If markers not found
    """
    start_line = -1
    end_line = -1

    for i, line in enumerate(lines):
        if start_marker in line and start_line == -1:
            start_line = i
        if end_marker in line and start_line != -1 and end_line == -1:
            end_line = i
            break

    if start_line == -1:
        raise ValueError(f"Start marker not found: {start_marker}")
    if end_line == -1:
        raise ValueError(f"End marker not found: {end_marker}")

    return start_line, end_line


def extract_section(section_name: str, dry_run: bool = False) -> None:
    """Extract section from CLAUDE.md to modular file.

    Args:
        section_name: Name of section to extract (e.g., 'tdd', 'context-engineering')
        dry_run: If True, show changes without applying them

    Raises:
        TypeError: If section_name is not a string
        ValueError: If section_name is unknown
    """
    # Step 1: Type checking (defensive)
    if not isinstance(section_name, str):
        raise TypeError("section_name must be a string")

    if section_name not in SECTIONS:
        raise ValueError(
            f"Unknown section '{section_name}'. Valid options: {', '.join(SECTIONS.keys())}, all"
        )

    section = SECTIONS[section_name]

    print(f"\n{'[DRY RUN] ' if dry_run else ''}Extracting section: {section_name}")
    print(f"Description: {section['description']}")

    # Step 2: Read CLAUDE.md
    claude_md_path = "CLAUDE.md"
    if not os.path.exists(claude_md_path):
        raise FileNotFoundError(f"CLAUDE.md not found at {claude_md_path}")

    with open(claude_md_path, encoding="utf-8") as f:
        lines = f.readlines()

    # Step 3: Find section boundaries
    try:
        start_line, end_line = find_section_boundaries(lines, section["start_marker"], section["end_marker"])
    except ValueError as e:
        print(f"❌ Error: {e}")
        return

    # Step 4: Extract content
    extracted_content = "".join(lines[start_line:end_line])
    original_lines = end_line - start_line
    summary_lines = section["summary"].count("\n")

    print("\nSection boundaries:")
    print(f"  Start: Line {start_line + 1} ({section['start_marker']})")
    print(f"  End: Line {end_line + 1} ({section['end_marker']})")
    print(f"  Original: {original_lines} lines")
    print(f"  Summary: {summary_lines} lines")
    print(f"  Saved: {original_lines - summary_lines} lines ({(1 - summary_lines/original_lines)*100:.1f}%)")

    if dry_run:
        print(f"\n[DRY RUN] Would create: {section['target']}")
        print(f"[DRY RUN] Would update: {claude_md_path}")
        print("[DRY RUN] Would create backup in: .claude/instructions/backup/")
        return

    # Step 5: Create backup
    os.makedirs(".claude/instructions/backup", exist_ok=True)
    backup_path = f".claude/instructions/backup/CLAUDE.md.backup-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    with open(backup_path, "w", encoding="utf-8") as f:
        f.writelines(lines)
    print(f"\n✅ Backup created: {backup_path}")

    # Step 6: Write extracted file
    os.makedirs(os.path.dirname(section["target"]), exist_ok=True)
    with open(section["target"], "w", encoding="utf-8") as f:
        f.write(f"# Extracted from CLAUDE.md - {section['description'].title()}\n\n")
        f.write(extracted_content)
    print(f"✅ Extracted content to: {section['target']}")

    # Step 7: Replace in CLAUDE.md
    new_lines = lines[:start_line] + [section["summary"] + "\n"] + lines[end_line:]
    with open(claude_md_path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)
    print("✅ Updated CLAUDE.md with summary and import")

    # Step 8: Report final stats
    print("\n📊 Compression complete:")
    print(f"   CLAUDE.md: {len(lines)} → {len(new_lines)} lines ({len(lines) - len(new_lines)} lines removed)")
    print(f"   Extracted: {section['target']} ({len(extracted_content.splitlines())} lines)")


def extract_all(dry_run: bool = False) -> None:
    """Extract all sections from CLAUDE.md.

    Args:
        dry_run: If True, show changes without applying them
    """
    print("Extracting all sections...")
    for section_name in SECTIONS.keys():
        try:
            extract_section(section_name, dry_run=dry_run)
        except Exception as e:
            print(f"❌ Error extracting {section_name}: {e}")
            continue


def main() -> None:
    """Main entry point for compress-claude-extract script."""
    if len(sys.argv) < 2:
        print("Usage: python .claude/scripts/compress-claude-extract.py [section] [--dry-run]")
        print(f"  section: {', '.join(SECTIONS.keys())}, all")
        print("  --dry-run: Show changes without applying them")
        sys.exit(1)

    section_name = sys.argv[1]
    dry_run = "--dry-run" in sys.argv

    try:
        if section_name == "all":
            extract_all(dry_run=dry_run)
        else:
            extract_section(section_name, dry_run=dry_run)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
