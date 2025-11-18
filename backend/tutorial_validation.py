"""
Tutorial validation functionality for Claude Skills System.

This module provides functions to validate tutorial structure, including:
- TUTORIAL_INDEX.md structure validation
- Required sections checking
- Learning time and difficulty detection
- Cross-link validation
- Tutorial count analysis
- Notebook execution validation
- Reading time calculation (word count ÷ 200 WPM)
- Validation report generation with ✅/❌ status and recommendations
"""

import re
import subprocess
import time
from pathlib import Path
from typing import Any

# Required sections for TUTORIAL_INDEX.md
REQUIRED_SECTIONS = [
    "Overview",
    "Learning Objectives",
    "Prerequisites",
    "Tutorials",
    "Recommended Learning Path",
    "Key Concepts",
    "Common Pitfalls",
    "Resources",
    "Next Steps",
    "FAQ",
]


def validate_tutorial_index_structure(content: str) -> dict[str, Any]:
    """
    Validate TUTORIAL_INDEX.md structure.

    Args:
        content: Content of TUTORIAL_INDEX.md file

    Returns:
        Validation result dictionary with:
        - valid: Whether all required sections are present
        - missing_sections: List of missing section names
        - found_sections: Number of sections found
        - required_sections: Number of required sections (10)
        - has_learning_time: Whether learning time estimate is present
        - learning_time: Learning time estimate string or None
        - has_difficulty: Whether difficulty level is present
        - difficulty: Difficulty level string or None
        - tutorial_count: Number of tutorials documented
        - has_cross_links: Whether cross-links to other lessons exist
        - cross_link_count: Number of cross-links found

    Raises:
        TypeError: If content is not a string

    Example:
        >>> content = Path("lesson-9/TUTORIAL_INDEX.md").read_text()
        >>> result = validate_tutorial_index_structure(content)
        >>> assert result["valid"] is True
        >>> assert result["found_sections"] == 10
    """
    # Step 1: Type checking (defensive)
    if not isinstance(content, str):
        raise TypeError("content must be a string")

    # Step 2: Initialize result dictionary
    result: dict[str, Any] = {
        "valid": False,
        "missing_sections": [],
        "found_sections": 0,
        "required_sections": len(REQUIRED_SECTIONS),
        "has_learning_time": False,
        "learning_time": None,
        "has_difficulty": False,
        "difficulty": None,
        "tutorial_count": 0,
        "has_cross_links": False,
        "cross_link_count": 0,
    }

    # Step 3: Edge case - Check for empty content
    if not content.strip():
        result["missing_sections"] = REQUIRED_SECTIONS.copy()
        return result

    # Step 4: Find all markdown headers (## Section Name)
    header_pattern = r"^##\s+(.+?)$"
    headers = re.findall(header_pattern, content, re.MULTILINE)

    # Normalize headers (lowercase, strip whitespace)
    normalized_headers = [h.strip().lower() for h in headers]

    # Step 5: Check which required sections are present
    # Also check for **Section Name:** format (used in Overview)
    bold_section_pattern = r"\*\*(.+?):\*\*"
    bold_sections = re.findall(bold_section_pattern, content)
    normalized_bold_sections = [s.strip().lower() for s in bold_sections]

    found_sections = []
    missing_sections = []

    for section in REQUIRED_SECTIONS:
        section_normalized = section.lower()
        # Check both ## headers and **Section:** format
        if section_normalized in normalized_headers or section_normalized in normalized_bold_sections:
            found_sections.append(section)
        else:
            missing_sections.append(section)

    result["found_sections"] = len(found_sections)
    result["missing_sections"] = missing_sections
    result["valid"] = len(missing_sections) == 0

    # Step 6: Check for learning time estimate
    learning_time_pattern = r"\*\*Learning Time:\*\*\s*(.+?)(?:\n|$)"
    learning_time_match = re.search(learning_time_pattern, content, re.IGNORECASE)
    if learning_time_match:
        result["has_learning_time"] = True
        result["learning_time"] = learning_time_match.group(1).strip()

    # Step 7: Check for difficulty level
    difficulty_pattern = r"\*\*Difficulty:\*\*\s*(.+?)(?:\n|$)"
    difficulty_match = re.search(difficulty_pattern, content, re.IGNORECASE)
    if difficulty_match:
        result["has_difficulty"] = True
        result["difficulty"] = difficulty_match.group(1).strip()

    # Step 8: Count documented tutorials (numbered list items in Tutorials section)
    # Look for patterns like "1. [Tutorial Name](path)"
    tutorial_pattern = r"^\d+\.\s+\[.+?\]\(.+?\)"
    tutorial_matches = re.findall(tutorial_pattern, content, re.MULTILINE)
    result["tutorial_count"] = len(tutorial_matches)

    # Step 9: Check for cross-links to other lessons/homeworks
    cross_link_pattern = r"\[.+?\]\(\.\./(?:lesson-\d+|homeworks/hw\d+)/.+?\)"
    cross_link_matches = re.findall(cross_link_pattern, content)
    result["cross_link_count"] = len(cross_link_matches)
    result["has_cross_links"] = len(cross_link_matches) > 0

    # Step 10: Return result
    return result


def validate_cross_links(file_path: str) -> dict[str, Any]:
    """
    Validate cross-links in tutorial files (verify relative paths resolve correctly).

    Args:
        file_path: Path to the tutorial file (e.g., TUTORIAL_INDEX.md)

    Returns:
        Validation result dictionary with:
        - valid: Whether all cross-links are valid
        - total_links: Total number of relative links found
        - broken_links: Number of broken links
        - invalid_paths: List of broken link details (link, resolved_path, error)
        - error: Error message if file doesn't exist, None otherwise

    Raises:
        TypeError: If file_path is not a string

    Example:
        >>> result = validate_cross_links("lesson-9/TUTORIAL_INDEX.md")
        >>> assert result["valid"] is True
        >>> assert result["broken_links"] == 0
    """
    # Step 1: Type checking (defensive)
    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

    # Step 2: Initialize result dictionary
    result: dict[str, Any] = {
        "valid": False,
        "total_links": 0,
        "broken_links": 0,
        "invalid_paths": [],
        "error": None,
    }

    # Step 3: Check if file exists
    file = Path(file_path)
    if not file.exists():
        result["error"] = f"File not found: {file_path}"
        return result

    # Step 4: Read file content
    try:
        content = file.read_text()
    except Exception as e:
        result["error"] = f"Error reading file: {e}"
        return result

    # Step 5: Extract markdown links [text](path)
    link_pattern = r"\[([^\]]+)\]\(([^)]+)\)"
    links = re.findall(link_pattern, content)

    # Step 6: Filter for relative paths only (skip http://, https://, mailto:, etc.)
    relative_links = []
    for text, path in links:
        # Skip absolute URLs
        if path.startswith(("http://", "https://", "mailto:", "ftp://", "#")):
            continue
        relative_links.append((text, path))

    result["total_links"] = len(relative_links)

    # Step 7: Validate each relative link
    base_dir = file.parent
    invalid_paths = []

    for text, link_path in relative_links:
        # Resolve relative path from the file's directory
        resolved_path = (base_dir / link_path).resolve()

        # Check if resolved path exists
        if not resolved_path.exists():
            invalid_paths.append(
                {
                    "link": link_path,
                    "resolved_path": str(resolved_path),
                    "error": f"File not found: {resolved_path}",
                }
            )

    result["broken_links"] = len(invalid_paths)
    result["invalid_paths"] = invalid_paths
    result["valid"] = len(invalid_paths) == 0

    # Step 8: Return result
    return result


def validate_mermaid_diagrams(directory_path: str) -> dict[str, Any]:
    """
    Validate Mermaid diagram syntax in .mmd files.

    Args:
        directory_path: Path to directory containing .mmd files

    Returns:
        Validation result dictionary with:
        - valid: Whether all diagrams have valid syntax
        - total_diagrams: Total number of .mmd files found
        - invalid_diagrams: Number of diagrams with syntax errors
        - errors: List of error details (file, error message)
        - error: Error message if directory doesn't exist, None otherwise

    Raises:
        TypeError: If directory_path is not a string

    Example:
        >>> result = validate_mermaid_diagrams("lesson-9")
        >>> assert result["valid"] is True
        >>> assert result["invalid_diagrams"] == 0
    """
    # Step 1: Type checking (defensive)
    if not isinstance(directory_path, str):
        raise TypeError("directory_path must be a string")

    # Step 2: Initialize result dictionary
    result: dict[str, Any] = {
        "valid": True,
        "total_diagrams": 0,
        "invalid_diagrams": 0,
        "errors": [],
        "error": None,
    }

    # Step 3: Check if directory exists
    directory = Path(directory_path)
    if not directory.exists():
        result["valid"] = False

        # Provide actionable error with directory suggestions
        error_msg = f"Directory not found: {directory_path}"

        # Try to find similar directories in current working directory
        try:
            cwd = Path.cwd()
            # Look for lesson-* and homeworks/hw* directories
            lesson_dirs = sorted([d.name for d in cwd.glob("lesson-*") if d.is_dir()])
            homework_dirs = sorted([d.name for d in (cwd / "homeworks").glob("hw*") if d.is_dir()]) if (cwd / "homeworks").exists() else []

            available_dirs = lesson_dirs + [f"homeworks/{hw}" for hw in homework_dirs]

            if available_dirs:
                error_msg += f". Available: {', '.join(available_dirs[:5])}"

                # Fuzzy match suggestion
                dir_name = Path(directory_path).name
                if dir_name.startswith("lesson-"):
                    similar = [d for d in lesson_dirs if d.startswith("lesson-")]
                    if similar:
                        error_msg += f". Did you mean {similar[0]}?"
        except Exception:
            # If directory listing fails, just use basic error message
            pass

        result["error"] = error_msg
        return result

    if not directory.is_dir():
        result["valid"] = False
        result["error"] = f"Path is not a directory: {directory_path}"
        return result

    # Step 4: Find all .mmd files recursively
    try:
        mmd_files = list(directory.rglob("*.mmd"))
    except Exception as e:
        result["valid"] = False
        result["error"] = f"Error searching directory: {e}"
        return result

    result["total_diagrams"] = len(mmd_files)

    # Step 5: If no diagrams found, return success
    if len(mmd_files) == 0:
        return result

    # Step 6: Validate each Mermaid diagram using mmdc CLI
    errors = []

    for mmd_file in mmd_files:
        try:
            # Read file content
            content = mmd_file.read_text()

            # Extract Mermaid content (remove code fence if present)
            mermaid_content = content
            if "```mermaid" in content:
                # Extract content between ```mermaid and ```
                match = re.search(r"```mermaid\s*(.*?)\s*```", content, re.DOTALL)
                if match:
                    mermaid_content = match.group(1)

            # Write content to temporary file for validation
            import tempfile

            with tempfile.NamedTemporaryFile(mode="w", suffix=".mmd", delete=False) as temp_file:
                temp_file.write(mermaid_content)
                temp_path = temp_file.name

            try:
                # Use mmdc CLI to validate syntax
                # Create temporary output file with valid extension
                temp_output = temp_path.replace(".mmd", ".svg")

                process = subprocess.run(
                    ["./node_modules/.bin/mmdc", "-i", temp_path, "-o", temp_output],
                    capture_output=True,
                    timeout=10,
                    text=True,
                )

                # If mmdc returns non-zero, there's a syntax error
                if process.returncode != 0:
                    error_msg = process.stderr if process.stderr else "Unknown syntax error"
                    # Add mermaid.live suggestion
                    error_msg += "\nSuggestion: Validate syntax at https://mermaid.live"
                    errors.append({"file": str(mmd_file), "error": error_msg})

                # Clean up output file if it was created
                Path(temp_output).unlink(missing_ok=True)

            finally:
                # Clean up temporary file
                Path(temp_path).unlink(missing_ok=True)

        except subprocess.TimeoutExpired:
            errors.append({"file": str(mmd_file), "error": "Validation timeout (>10s)"})
        except Exception as e:
            errors.append({"file": str(mmd_file), "error": f"Validation error: {e}"})

    result["invalid_diagrams"] = len(errors)
    result["errors"] = errors
    result["valid"] = len(errors) == 0

    # Step 7: Return result
    return result


def calculate_reading_time(file_path: str, wpm: int = 200) -> dict[str, Any]:
    """
    Calculate reading time for a tutorial file based on word count.

    Args:
        file_path: Path to the tutorial file (.md or .ipynb)
        wpm: Words per minute reading speed (default: 200)

    Returns:
        Calculation result dictionary with:
        - word_count: Total number of words in the file
        - reading_time_minutes: Estimated reading time in minutes
        - within_target: Whether reading time is within 15-30 min target
        - status: "optimal", "too_short", or "too_long"
        - error: Error message if file doesn't exist, None otherwise

    Raises:
        TypeError: If file_path is not a string or wpm is not an integer
        ValueError: If wpm is not positive

    Example:
        >>> result = calculate_reading_time("lesson-9/evaluation_fundamentals.md")
        >>> assert result["word_count"] > 0
        >>> assert result["reading_time_minutes"] >= 15
        >>> assert result["reading_time_minutes"] <= 30
    """
    # Step 1: Type checking (defensive)
    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")

    if not isinstance(wpm, int):
        raise TypeError("wpm must be an integer")

    if wpm <= 0:
        raise ValueError("wpm must be positive")

    # Step 2: Initialize result dictionary
    result: dict[str, Any] = {
        "word_count": 0,
        "reading_time_minutes": 0.0,
        "within_target": False,
        "status": "error",
        "error": None,
    }

    # Step 3: Check if file exists
    file = Path(file_path)
    if not file.exists():
        result["error"] = f"File not found: {file_path}"
        return result

    # Step 4: Read file content based on file type
    try:
        if file.suffix == ".ipynb":
            # For Jupyter notebooks, extract markdown and code cells
            import json

            content = file.read_text()
            notebook_data = json.loads(content)

            # Extract text from all cells
            text_content = []
            for cell in notebook_data.get("cells", []):
                cell_type = cell.get("cell_type", "")
                source = cell.get("source", [])

                # Convert source to string (it can be list or string)
                if isinstance(source, list):
                    cell_text = "".join(source)
                else:
                    cell_text = source

                # Include markdown cells and code cells (code is also reading material)
                if cell_type in ["markdown", "code"]:
                    text_content.append(cell_text)

            content_text = "\n".join(text_content)

        elif file.suffix == ".md":
            # For markdown files, read directly
            content_text = file.read_text()

        else:
            result["error"] = f"Unsupported file type: {file.suffix}. Only .md and .ipynb supported."
            return result

    except json.JSONDecodeError as e:
        result["error"] = f"Invalid JSON in notebook file: {e}"
        return result
    except Exception as e:
        result["error"] = f"Error reading file: {e}"
        return result

    # Step 5: Count words
    # Remove markdown syntax and code blocks for more accurate word count
    # Remove code blocks (```...```)
    content_text = re.sub(r"```.*?```", "", content_text, flags=re.DOTALL)
    # Remove inline code (`...`)
    content_text = re.sub(r"`[^`]+`", "", content_text)
    # Remove URLs
    content_text = re.sub(r"http[s]?://[^\s]+", "", content_text)
    # Remove markdown links but keep text
    content_text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", content_text)
    # Remove markdown headers (#, ##, etc.)
    content_text = re.sub(r"^#+\s+", "", content_text, flags=re.MULTILINE)
    # Remove markdown formatting (**, *, _, etc.)
    content_text = re.sub(r"[*_]+", "", content_text)

    # Split on whitespace and count non-empty words
    words = content_text.split()
    word_count = len([w for w in words if w.strip()])

    result["word_count"] = word_count

    # Step 6: Calculate reading time in minutes
    reading_time_minutes = word_count / wpm
    result["reading_time_minutes"] = round(reading_time_minutes, 1)

    # Step 7: Check if within target range (15-30 minutes)
    if 15 <= reading_time_minutes <= 30:
        result["within_target"] = True
        result["status"] = "optimal"
    elif reading_time_minutes < 15:
        result["within_target"] = False
        result["status"] = "too_short"
    else:  # reading_time_minutes > 30
        result["within_target"] = False
        result["status"] = "too_long"

    # Step 8: Return result
    return result


def generate_validation_report(
    directory: str,
    tutorial_index_result: dict[str, Any] | None = None,
    notebook_results: list[dict[str, Any]] | None = None,
    cross_link_result: dict[str, Any] | None = None,
    mermaid_result: dict[str, Any] | None = None,
    reading_time_results: list[dict[str, Any]] | None = None,
    validation_time: float = 0.0,
) -> str:
    """
    Generate a formatted validation report with ✅/❌ status and actionable suggestions.

    Args:
        directory: Path to the tutorial directory being validated
        tutorial_index_result: Result from validate_tutorial_index_structure()
        notebook_results: List of results from validate_notebook_execution()
        cross_link_result: Result from validate_cross_links()
        mermaid_result: Result from validate_mermaid_diagrams()
        reading_time_results: List of results from calculate_reading_time()
        validation_time: Total validation time in seconds

    Returns:
        Formatted report string with status symbols and recommendations

    Raises:
        TypeError: If directory is not a string

    Example:
        >>> report = generate_validation_report("lesson-9/", tutorial_index_result={...})
        >>> print(report)
        📋 Tutorial Validation Report: lesson-9/
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        ...
    """
    # Step 1: Type checking (defensive)
    if not isinstance(directory, str):
        raise TypeError("directory must be a string")

    # Step 2: Initialize report components
    lines = []
    warnings = []
    errors = []
    overall_status = "✅ PASS"

    # Step 3: Header
    lines.append(f"📋 Tutorial Validation Report: {directory}")
    lines.append("━" * 60)
    lines.append("")

    # Step 4: TUTORIAL_INDEX.md Structure Validation
    if tutorial_index_result:
        lines.append("1. TUTORIAL_INDEX.md Structure")
        if tutorial_index_result.get("valid"):
            lines.append("   ✅ All required sections present (10/10)")
            if tutorial_index_result.get("has_learning_time"):
                lines.append(f"   - Learning time: {tutorial_index_result['learning_time']}")
            if tutorial_index_result.get("has_difficulty"):
                lines.append(f"   - Difficulty: {tutorial_index_result['difficulty']}")
            if tutorial_index_result.get("tutorial_count", 0) > 0:
                lines.append(f"   - {tutorial_index_result['tutorial_count']} tutorials documented")
        else:
            overall_status = "❌ FAIL"
            missing = tutorial_index_result.get("missing_sections", [])
            lines.append(f"   ❌ Missing sections: {', '.join(missing)}")
            errors.append("Add missing TUTORIAL_INDEX.md sections")
            lines.append("   💡 Recommendation: Add missing sections using template")
            lines.append("      See: .claude/skills/tutorial-standards/references/tutorial-index-template.md")
        lines.append("")

    # Step 5: Notebook Execution Validation
    if notebook_results:
        lines.append("2. Notebook Execution")
        successful = sum(1 for r in notebook_results if r.get("executed"))
        total = len(notebook_results)

        if successful == total:
            lines.append(f"   ✅ All notebooks executed ({successful}/{total})")
        else:
            overall_status = "⚠️ PASS (with warnings)" if overall_status == "✅ PASS" else overall_status
            lines.append(f"   ⚠️ {successful}/{total} notebooks executed")

        for result in notebook_results:
            nb_name = Path(result["notebook_path"]).name
            if result.get("executed"):
                exec_time = result.get("execution_time", 0)
                lines.append(f"   ✅ {nb_name} ({exec_time:.2f}s)")
            else:
                status = result.get("status", "error")
                error = result.get("error", "Unknown error")
                if status == "timeout":
                    lines.append(f"   ⏱️ {nb_name} (exceeded timeout)")
                    warnings.append(f"Optimize {nb_name} or increase timeout")
                else:
                    lines.append(f"   ❌ {nb_name}")
                    lines.append(f"      Error: {error[:100]}")
                    errors.append(f"Fix execution error in {nb_name}")
        lines.append("")

    # Step 6: Cross-Link Validation
    if cross_link_result:
        lines.append("3. Cross-Links")
        total_links = cross_link_result.get("total_links", 0)
        broken_links = cross_link_result.get("broken_links", 0)
        valid_links = total_links - broken_links

        if cross_link_result.get("valid"):
            if total_links > 0:
                lines.append(f"   ✅ All links valid ({total_links}/{total_links})")
            else:
                lines.append("   ✅ No cross-links to validate")
        else:
            overall_status = "⚠️ PASS (with warnings)" if overall_status == "✅ PASS" else overall_status
            percentage = (valid_links / total_links * 100) if total_links > 0 else 0
            lines.append(f"   ⚠️ {valid_links}/{total_links} links valid ({percentage:.1f}%)")

            for invalid in cross_link_result.get("invalid_paths", [])[:3]:  # Show first 3
                link = invalid["link"]
                lines.append(f"      ❌ {link}")
                warnings.append(f"Fix broken link: {link}")

            if broken_links > 3:
                lines.append(f"      ... and {broken_links - 3} more broken links")
        lines.append("")

    # Step 7: Mermaid Diagram Validation
    if mermaid_result:
        lines.append("4. Mermaid Diagrams")
        total_diagrams = mermaid_result.get("total_diagrams", 0)
        invalid_diagrams = mermaid_result.get("invalid_diagrams", 0)

        if total_diagrams == 0:
            lines.append("   ℹ️ No Mermaid diagrams to validate")
        elif mermaid_result.get("valid"):
            lines.append(f"   ✅ All diagrams valid ({total_diagrams}/{total_diagrams})")
        else:
            overall_status = "❌ FAIL" if invalid_diagrams == total_diagrams else "⚠️ PASS (with warnings)"
            lines.append(f"   ❌ {total_diagrams - invalid_diagrams}/{total_diagrams} diagrams valid")

            for error in mermaid_result.get("errors", [])[:2]:  # Show first 2
                file = Path(error["file"]).name
                lines.append(f"      ❌ {file}")
                lines.append(f"         {error['error'][:80]}")
                errors.append(f"Fix Mermaid syntax in {file}")
                lines.append("         💡 Validate at: https://mermaid.live")
        lines.append("")

    # Step 8: Reading Time Calculation
    if reading_time_results:
        lines.append("5. Reading Time")
        total_words = sum(r.get("word_count", 0) for r in reading_time_results)
        total_minutes = sum(r.get("reading_time_minutes", 0) for r in reading_time_results)

        too_long = [r for r in reading_time_results if r.get("status") == "too_long"]
        optimal = [r for r in reading_time_results if r.get("status") == "optimal"]

        if too_long:
            overall_status = "⚠️ PASS (with warnings)" if overall_status == "✅ PASS" else overall_status
            lines.append(f"   ⚠️ Total reading time: ~{total_minutes:.0f} min ({total_words:,} words)")
            for result in too_long[:2]:  # Show first 2
                time = result["reading_time_minutes"]
                lines.append(f"      ⚠️ File exceeds 30 min target ({time:.0f} min)")
                warnings.append("Consider splitting long tutorials")
        else:
            lines.append(f"   ✅ Reading time within range (~{total_minutes:.0f} min, {total_words:,} words)")
        lines.append("")

    # Step 9: Overall Status and Recommendations
    lines.append("━" * 60)
    lines.append(f"Overall: {overall_status}")
    lines.append("")

    if warnings or errors:
        lines.append("Recommendations:")
        for i, error in enumerate(errors[:5], 1):
            lines.append(f"  {i}. {error}")
        for i, warning in enumerate(warnings[:3], len(errors) + 1):
            lines.append(f"  {i}. {warning}")
        lines.append("")

    if validation_time > 0:
        lines.append(f"Validation completed in {validation_time:.1f}s")

    # Step 10: Return formatted report
    return "\n".join(lines)


def validate_notebook_execution(notebook_path: str, timeout: int = 300) -> dict[str, Any]:
    """
    Validate notebook execution using jupyter nbconvert.

    Args:
        notebook_path: Path to .ipynb file
        timeout: Maximum execution time in seconds (default: 300)

    Returns:
        Validation result dictionary with:
        - executed: Whether notebook executed successfully
        - execution_time: Time taken to execute in seconds
        - status: "success", "error", or "timeout"
        - error: Error message if execution failed, None otherwise
        - notebook_path: Path to the notebook

    Raises:
        TypeError: If notebook_path is not a string
        ValueError: If timeout is not positive

    Example:
        >>> result = validate_notebook_execution("lesson-9/tutorial.ipynb", timeout=300)
        >>> assert result["executed"] is True
        >>> assert result["execution_time"] < 300
    """
    # Step 1: Type checking (defensive)
    if not isinstance(notebook_path, str):
        raise TypeError("notebook_path must be a string")

    if timeout <= 0:
        raise ValueError("timeout must be positive")

    # Step 2: Initialize result dictionary
    result: dict[str, Any] = {
        "executed": False,
        "execution_time": 0.0,
        "status": "error",
        "error": None,
        "notebook_path": notebook_path,
    }

    # Step 3: Check if notebook file exists
    notebook_file = Path(notebook_path)
    if not notebook_file.exists():
        result["error"] = f"Notebook not found: {notebook_path}"
        return result

    # Step 4: Check if jupyter nbconvert is available
    try:
        subprocess.run(
            ["jupyter", "nbconvert", "--version"],
            capture_output=True,
            check=True,
            timeout=5,
        )
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError) as e:
        result["error"] = (
            f"jupyter nbconvert not available: {e}. "
            f"Install with: pip install jupyter nbconvert"
        )
        return result

    # Step 5: Execute notebook with timeout
    start_time = time.time()

    try:
        # Run jupyter nbconvert --execute with timeout
        # Use --stdout to avoid writing output file
        process = subprocess.run(
            [
                "jupyter",
                "nbconvert",
                "--to",
                "notebook",
                "--execute",
                "--stdout",
                str(notebook_file),
            ],
            capture_output=True,
            timeout=timeout,
            text=True,
        )

        execution_time = time.time() - start_time
        result["execution_time"] = execution_time

        # Check if execution was successful
        if process.returncode == 0:
            result["executed"] = True
            result["status"] = "success"
        else:
            result["executed"] = False
            result["status"] = "error"
            result["error"] = process.stderr if process.stderr else "Unknown execution error"

    except subprocess.TimeoutExpired:
        execution_time = time.time() - start_time
        result["execution_time"] = execution_time
        result["executed"] = False
        result["status"] = "timeout"
        result["error"] = (
            f"Notebook execution exceeded timeout ({timeout}s). "
            f"Suggestion: Optimize notebook to run faster or increase timeout threshold."
        )

    except Exception as e:
        execution_time = time.time() - start_time
        result["execution_time"] = execution_time
        result["executed"] = False
        result["status"] = "error"
        result["error"] = f"Unexpected error during execution: {e}"

    # Step 6: Return result
    return result
