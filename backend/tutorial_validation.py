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
        result["error"] = f"Directory not found: {directory_path}"
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
        result["error"] = f"jupyter nbconvert not available: {e}"
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
        result["error"] = f"Notebook execution exceeded timeout ({timeout}s)"

    except Exception as e:
        execution_time = time.time() - start_time
        result["execution_time"] = execution_time
        result["executed"] = False
        result["status"] = "error"
        result["error"] = f"Unexpected error during execution: {e}"

    # Step 6: Return result
    return result
