#!/usr/bin/env python3
"""Validate all cross-references in Lesson 14 memory systems tutorials.

This script:
1. Extracts all markdown links from tutorial files
2. Validates relative path links (file existence)
3. Validates internal anchor links (section existence)
4. Generates validation report with findings

Usage:
    python lesson-14/scripts/validate_cross_references.py
"""

import re
from pathlib import Path
from typing import NamedTuple


class LinkReference(NamedTuple):
    """Represents a link found in a markdown file."""

    source_file: str
    link_text: str
    target: str
    line_number: int
    link_type: str  # "relative_path", "internal_anchor", "external_url", "code_reference"


def extract_links_from_markdown(file_path: Path) -> list[LinkReference]:
    """Extract all markdown links from a file.

    Args:
        file_path: Path to markdown file

    Returns:
        List of LinkReference objects

    Raises:
        FileNotFoundError: If file does not exist
        TypeError: If file_path is not a Path object
    """
    if not isinstance(file_path, Path):
        raise TypeError("file_path must be a Path object")
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    links: list[LinkReference] = []

    # Regex patterns for different link types
    markdown_link_pattern = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")

    # Resolve to absolute path for consistent handling
    file_path = file_path.resolve()

    # Track if we're inside a code block
    in_code_block = False

    with open(file_path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            # Check for code block delimiters
            if line.strip().startswith("```"):
                in_code_block = not in_code_block
                continue

            # Skip lines inside code blocks
            if in_code_block:
                continue

            # Find all markdown links in line
            for match in markdown_link_pattern.finditer(line):
                link_text = match.group(1)
                target = match.group(2)

                # Classify link type
                if target.startswith("http://") or target.startswith("https://"):
                    link_type = "external_url"
                elif target.startswith("#"):
                    link_type = "internal_anchor"
                elif ":" in target and not target.startswith("../") and not target.startswith("./"):
                    # File path with line number (e.g., "file.py:123")
                    link_type = "code_reference"
                else:
                    link_type = "relative_path"

                links.append(
                    LinkReference(
                        source_file=str(file_path.relative_to(Path.cwd().resolve())),
                        link_text=link_text,
                        target=target,
                        line_number=line_num,
                        link_type=link_type,
                    )
                )

    return links


def validate_relative_path_link(source_file: Path, target: str) -> tuple[bool, str]:
    """Validate a relative path link exists.

    Args:
        source_file: Source file containing the link
        target: Target path (may include anchor)

    Returns:
        Tuple of (is_valid, message)

    Raises:
        TypeError: If inputs are invalid types
    """
    if not isinstance(source_file, Path):
        raise TypeError("source_file must be a Path object")
    if not isinstance(target, str):
        raise TypeError("target must be a string")

    # Split target into path and anchor
    if "#" in target:
        path_part, anchor_part = target.split("#", 1)
    else:
        path_part = target
        anchor_part = None

    # Resolve relative path
    source_dir = source_file.parent
    target_path = (source_dir / path_part).resolve()

    if not target_path.exists():
        return False, f"File not found: {target_path}"

    if target_path.is_dir():
        return False, f"Target is a directory, not a file: {target_path}"

    # If anchor specified, validate it exists in target file
    if anchor_part:
        is_valid, msg = validate_anchor_in_file(target_path, anchor_part)
        if not is_valid:
            return False, f"Anchor validation failed: {msg}"

    return True, "Valid"


def validate_anchor_in_file(file_path: Path, anchor: str) -> tuple[bool, str]:
    """Validate an anchor exists in a markdown file.

    Args:
        file_path: Path to markdown file
        anchor: Anchor name (without #)

    Returns:
        Tuple of (is_valid, message)

    Raises:
        TypeError: If inputs are invalid types
        FileNotFoundError: If file does not exist
    """
    if not isinstance(file_path, Path):
        raise TypeError("file_path must be a Path object")
    if not isinstance(anchor, str):
        raise TypeError("anchor must be a string")
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    # Convert anchor to expected heading format
    # GitHub anchor format: lowercase, replace spaces with hyphens, remove special chars
    def normalize_anchor(text: str) -> str:
        """Normalize heading to GitHub anchor format."""
        # Lowercase
        text = text.lower()
        # Replace spaces with hyphens
        text = text.replace(" ", "-")
        # Remove special characters except hyphens
        text = re.sub(r"[^a-z0-9\-]", "", text)
        # Remove duplicate hyphens
        text = re.sub(r"-+", "-", text)
        return text

    # Extract all headings from file
    heading_pattern = re.compile(r"^#+\s+(.+)$")
    headings = []

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            match = heading_pattern.match(line.strip())
            if match:
                heading_text = match.group(1)
                # Remove markdown formatting from heading
                heading_text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", heading_text)  # Remove links
                heading_text = re.sub(r"[*_`]", "", heading_text)  # Remove emphasis
                headings.append(normalize_anchor(heading_text))

    # Normalize target anchor
    normalized_anchor = normalize_anchor(anchor)

    if normalized_anchor in headings:
        return True, "Anchor found"

    return False, f"Anchor '{anchor}' not found. Available anchors: {', '.join(headings[:10])}"


def validate_internal_anchor(source_file: Path, anchor: str) -> tuple[bool, str]:
    """Validate an internal anchor exists in the source file.

    Args:
        source_file: Source file containing the link
        anchor: Anchor name (without #)

    Returns:
        Tuple of (is_valid, message)

    Raises:
        TypeError: If inputs are invalid types
    """
    if not isinstance(source_file, Path):
        raise TypeError("source_file must be a Path object")
    if not isinstance(anchor, str):
        raise TypeError("anchor must be a string")

    return validate_anchor_in_file(source_file, anchor)


def main() -> None:
    """Main validation function."""
    # Define tutorial files to validate
    lesson_14_dir = Path("lesson-14")
    tutorial_files = [
        lesson_14_dir / "memory_systems_fundamentals.md",
        lesson_14_dir / "context_engineering_guide.md",
        lesson_14_dir / "TUTORIAL_INDEX.md",
        lesson_14_dir / "04_Agentic_RAG.md",
        lesson_14_dir / "multi_agent_fundamentals.md",
    ]

    # Validate files exist
    missing_files = [f for f in tutorial_files if not f.exists()]
    if missing_files:
        print(f"ERROR: Missing tutorial files: {missing_files}")
        return

    print("=" * 80)
    print("Lesson 14 Cross-Reference Validation Report")
    print("=" * 80)
    print()

    # Extract all links
    all_links: list[LinkReference] = []
    for tutorial_file in tutorial_files:
        links = extract_links_from_markdown(tutorial_file)
        all_links.extend(links)
        print(f"Extracted {len(links)} links from {tutorial_file.name}")

    print(f"\nTotal links extracted: {len(all_links)}")
    print()

    # Group links by type
    links_by_type: dict[str, list[LinkReference]] = {}
    for link in all_links:
        if link.link_type not in links_by_type:
            links_by_type[link.link_type] = []
        links_by_type[link.link_type].append(link)

    print("Links by type:")
    for link_type, links in sorted(links_by_type.items()):
        print(f"  {link_type}: {len(links)}")
    print()

    # Validate relative path links
    print("=" * 80)
    print("Validating Relative Path Links")
    print("=" * 80)
    print()

    relative_links = links_by_type.get("relative_path", [])
    if not relative_links:
        print("No relative path links found.")
    else:
        valid_count = 0
        invalid_count = 0

        for link in relative_links:
            source_path = Path(link.source_file)
            is_valid, message = validate_relative_path_link(source_path, link.target)

            if is_valid:
                valid_count += 1
                print(f"✅ {link.source_file}:{link.line_number} -> {link.target}")
            else:
                invalid_count += 1
                print(f"❌ {link.source_file}:{link.line_number} -> {link.target}")
                print(f"   Error: {message}")
                print()

        print(f"\nRelative Path Links: {valid_count}/{len(relative_links)} valid")
        print()

    # Validate internal anchor links
    print("=" * 80)
    print("Validating Internal Anchor Links")
    print("=" * 80)
    print()

    internal_links = links_by_type.get("internal_anchor", [])
    if not internal_links:
        print("No internal anchor links found.")
    else:
        valid_count = 0
        invalid_count = 0

        for link in internal_links:
            source_path = Path(link.source_file)
            anchor = link.target[1:]  # Remove leading #
            is_valid, message = validate_internal_anchor(source_path, anchor)

            if is_valid:
                valid_count += 1
                print(f"✅ {link.source_file}:{link.line_number} -> {link.target}")
            else:
                invalid_count += 1
                print(f"❌ {link.source_file}:{link.line_number} -> {link.target}")
                print(f"   Error: {message}")
                print()

        print(f"\nInternal Anchor Links: {valid_count}/{len(internal_links)} valid")
        print()

    # Summary statistics
    print("=" * 80)
    print("Summary")
    print("=" * 80)
    print()

    total_validatable = len(relative_links) + len(internal_links)
    total_valid = sum(
        1
        for link in relative_links
        if validate_relative_path_link(Path(link.source_file), link.target)[0]
    )
    total_valid += sum(
        1
        for link in internal_links
        if validate_internal_anchor(Path(link.source_file), link.target[1:])[0]
    )

    print(f"Total cross-references validated: {total_validatable}")
    print(f"Valid: {total_valid}")
    print(f"Invalid: {total_validatable - total_valid}")
    print(f"Success rate: {100 * total_valid / total_validatable if total_validatable > 0 else 0:.1f}%")
    print()

    # External URLs (not validated)
    external_links = links_by_type.get("external_url", [])
    print(f"External URLs (not validated): {len(external_links)}")

    # Code references (not validated)
    code_refs = links_by_type.get("code_reference", [])
    print(f"Code references (not validated): {len(code_refs)}")
    print()

    print("=" * 80)
    print("Validation Complete")
    print("=" * 80)


if __name__ == "__main__":
    main()
