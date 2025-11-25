#!/usr/bin/env python3
"""
Minimal viable extract action for /compress-claude command.

Usage: python .claude/scripts/compress-claude.py extract [section]
  section: context-engineering | tutorial-workflow | all
"""

import sys
from datetime import datetime
from pathlib import Path

# Section definitions with line ranges and content
SECTIONS = {
    "context-engineering": {
        "start_line": 356,  # Line number in current CLAUDE.md
        "end_line": 589,    # End of Context Engineering section
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
    },
    "tutorial-workflow": {
        "start_line": 592,  # Start of Tutorial Workflow section
        "end_line": 680,    # End of Tutorial Workflow section
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
    },
}


def read_claude_md() -> list[str]:
    """Read CLAUDE.md file.

    Returns:
        List of lines from CLAUDE.md

    Raises:
        FileNotFoundError: If CLAUDE.md doesn't exist
    """
    claude_path = Path("CLAUDE.md")
    if not claude_path.exists():
        raise FileNotFoundError("CLAUDE.md not found in current directory")

    with open(claude_path) as f:
        return f.readlines()


def create_backup() -> Path:
    """Create timestamped backup of CLAUDE.md.

    Returns:
        Path to backup file
    """
    backup_dir = Path(".claude/instructions/backup")
    backup_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_path = backup_dir / f"CLAUDE.md.backup-{timestamp}"

    lines = read_claude_md()
    with open(backup_path, "w") as f:
        f.writelines(lines)

    return backup_path


def extract_section(section_name: str) -> dict[str, int | str]:
    """Extract section from CLAUDE.md to modular file.

    Args:
        section_name: Name of section to extract (context-engineering, tutorial-workflow)

    Returns:
        Dict with extraction statistics

    Raises:
        ValueError: If section_name is unknown
        FileNotFoundError: If CLAUDE.md doesn't exist
    """
    # Step 1: Type checking (defensive)
    if not isinstance(section_name, str):
        raise TypeError("section_name must be a string")

    if section_name not in SECTIONS:
        raise ValueError(
            f"Unknown section '{section_name}'. "
            f"Valid options: {', '.join(SECTIONS.keys())}, all"
        )

    section = SECTIONS[section_name]

    # Step 2: Read CLAUDE.md
    lines = read_claude_md()

    # Step 3: Extract content
    start = section["start_line"] - 1  # Convert to 0-indexed
    end = section["end_line"]
    extracted_content = "".join(lines[start:end])

    # Step 4: Create backup
    backup_path = create_backup()

    # Step 5: Write extracted file
    target_path = Path(section["target"])
    target_path.parent.mkdir(parents=True, exist_ok=True)

    with open(target_path, "w") as f:
        f.write(f"# Extracted from CLAUDE.md - {section_name.replace('-', ' ').title()}\n\n")
        f.write(extracted_content)

    # Step 6: Replace in CLAUDE.md
    new_lines = lines[:start] + [section["summary"] + "\n"] + lines[end:]

    with open("CLAUDE.md", "w") as f:
        f.writelines(new_lines)

    # Step 7: Calculate statistics
    original_lines = end - start
    summary_lines = section["summary"].count("\n") + 1
    lines_saved = original_lines - summary_lines

    return {
        "section": section_name,
        "original_lines": original_lines,
        "summary_lines": summary_lines,
        "lines_saved": lines_saved,
        "compression_ratio": (lines_saved / original_lines) * 100,
        "extracted_file": str(target_path),
        "backup_file": str(backup_path),
    }


def extract_all_sections() -> list[dict[str, int | str]]:
    """Extract all defined sections.

    Returns:
        List of extraction statistics for each section
    """
    results = []
    for section_name in SECTIONS.keys():
        try:
            result = extract_section(section_name)
            results.append(result)
            print(f"✅ Extracted {section_name}")
        except Exception as e:
            print(f"❌ Failed to extract {section_name}: {e}")
            results.append({"section": section_name, "error": str(e)})

    return results


def print_results(result: dict[str, int | str]) -> None:
    """Print extraction results.

    Args:
        result: Dictionary with extraction statistics
    """
    if "error" in result:
        print(f"\n❌ Extraction failed: {result['error']}")
        return

    print("\n" + "=" * 60)
    print(f"✅ Extracted: {result['section']}")
    print("=" * 60)
    print(f"Original: {result['original_lines']} lines")
    print(f"Summary: {result['summary_lines']} lines")
    print(f"Saved: {result['lines_saved']} lines ({result['compression_ratio']:.1f}% reduction)")
    print(f"Extracted to: {result['extracted_file']}")
    print(f"Backup: {result['backup_file']}")
    print("=" * 60)


def main() -> None:
    """Main entry point for compress-claude script."""
    if len(sys.argv) != 3 or sys.argv[1] != "extract":
        print("Usage: python .claude/scripts/compress-claude.py extract [section]")
        print(f"  section: {', '.join(SECTIONS.keys())}, all")
        sys.exit(1)

    section_name = sys.argv[2]

    try:
        if section_name == "all":
            print("Extracting all sections...")
            results = extract_all_sections()

            # Print summary
            total_saved = sum(r.get("lines_saved", 0) for r in results if "error" not in r)
            print(f"\n📊 Total lines saved: {total_saved}")

            for result in results:
                print_results(result)
        else:
            result = extract_section(section_name)
            print_results(result)

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
