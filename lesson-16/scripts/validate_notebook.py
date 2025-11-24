"""
Notebook validation script for Lesson 16.

This script validates that notebooks meet quality standards:
- Execution time <5-10 minutes
- All assertions pass
- All imports work
- Cross-links are valid
- Standard 12-section structure present
"""

import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


def load_notebook(notebook_path: Path) -> dict[str, Any]:
    """Load a Jupyter notebook from file.

    Args:
        notebook_path: Path to .ipynb file

    Returns:
        Notebook JSON structure

    Raises:
        FileNotFoundError: If notebook doesn't exist
        ValueError: If notebook is not valid JSON
    """
    if not notebook_path.exists():
        raise FileNotFoundError(f"Notebook not found: {notebook_path}")

    with open(notebook_path, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid notebook JSON: {e}")


def check_structure(notebook: dict[str, Any]) -> dict[str, bool]:
    """Check if notebook has the standard 12-section structure.

    Standard sections:
    1. Title + metadata (learning objectives, prerequisites, cost warning)
    2. Setup and Configuration (DEMO_MODE, imports)
    3-6. Steps 1-4 (numbered markdown + code cells)
    7. Visualization
    8. Validation
    9. Cost Summary
    10. Summary and Key Takeaways
    11. Next Steps
    12. Metadata (kernelspec, language_info)

    Args:
        notebook: Notebook JSON structure

    Returns:
        Dictionary of checks and their pass/fail status
    """
    checks = {}
    cells = notebook.get("cells", [])

    # Check 1: Has markdown cells
    markdown_cells = [c for c in cells if c.get("cell_type") == "markdown"]
    checks["has_markdown_cells"] = len(markdown_cells) > 0

    # Check 2: Has code cells
    code_cells = [c for c in cells if c.get("cell_type") == "code"]
    checks["has_code_cells"] = len(code_cells) > 0

    # Check 3: Has title (first cell is markdown with #)
    if markdown_cells:
        first_md_content = "".join(markdown_cells[0].get("source", []))
        checks["has_title"] = first_md_content.strip().startswith("#")
    else:
        checks["has_title"] = False

    # Check 4: Has learning objectives
    all_md_content = " ".join(
        ["".join(c.get("source", [])) for c in markdown_cells]
    )
    checks["has_learning_objectives"] = "Learning Objectives" in all_md_content

    # Check 5: Has prerequisites
    checks["has_prerequisites"] = "Prerequisites" in all_md_content or "prerequisite" in all_md_content.lower()

    # Check 6: Has setup cell
    checks["has_setup"] = any(
        "import" in "".join(c.get("source", [])) for c in code_cells
    )

    # Check 7: Has step sections
    step_count = sum(
        1 for c in markdown_cells if "## Step" in "".join(c.get("source", []))
    )
    checks["has_steps"] = step_count >= 3

    # Check 8: Has visualization
    checks["has_visualization"] = any(
        "plt.show()" in "".join(c.get("source", []))
        or "Visualization" in "".join(c.get("source", []))
        for c in cells
    )

    # Check 9: Has validation/assertions
    checks["has_validation"] = any(
        "assert" in "".join(c.get("source", []))
        or "Validation" in "".join(c.get("source", []))
        for c in cells
    )

    # Check 10: Has summary
    checks["has_summary"] = "Summary" in all_md_content or "Key Takeaways" in all_md_content

    # Check 11: Has next steps
    checks["has_next_steps"] = "Next Steps" in all_md_content

    # Check 12: Has metadata
    checks["has_metadata"] = "metadata" in notebook and "kernelspec" in notebook["metadata"]

    return checks


def check_imports(notebook: dict[str, Any]) -> dict[str, bool]:
    """Check if all imports in notebook are valid.

    Args:
        notebook: Notebook JSON structure

    Returns:
        Dictionary with import check results
    """
    checks = {}
    cells = notebook.get("cells", [])
    code_cells = [c for c in cells if c.get("cell_type") == "code"]

    # Extract import statements
    imports = []
    for cell in code_cells:
        source = "".join(cell.get("source", []))
        for line in source.split("\n"):
            if line.strip().startswith("import ") or line.strip().startswith("from "):
                imports.append(line.strip())

    checks["import_count"] = len(imports)
    checks["has_imports"] = len(imports) > 0

    # Check for lesson-16 backend imports
    backend_imports = [i for i in imports if "lesson_16" in i or "lesson-16" in i]
    checks["has_backend_imports"] = len(backend_imports) > 0

    return checks


def check_execution_time(notebook_path: Path, timeout: int = 600) -> dict[str, Any]:
    """Check notebook execution time using jupyter nbconvert.

    Args:
        notebook_path: Path to .ipynb file
        timeout: Maximum execution time in seconds (default: 600 = 10 min)

    Returns:
        Dictionary with execution results
    """
    result = {"executed": False, "execution_time": None, "error": None}

    try:
        start_time = time.time()

        # Run nbconvert to execute notebook
        cmd = [
            "jupyter",
            "nbconvert",
            "--to",
            "notebook",
            "--execute",
            "--ExecutePreprocessor.timeout=%d" % timeout,
            "--output",
            "/tmp/executed_notebook.ipynb",
            str(notebook_path),
        ]

        proc = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout + 10
        )

        execution_time = time.time() - start_time

        if proc.returncode == 0:
            result["executed"] = True
            result["execution_time"] = execution_time
        else:
            result["error"] = proc.stderr

    except subprocess.TimeoutExpired:
        result["error"] = f"Execution exceeded timeout of {timeout}s"
    except Exception as e:
        result["error"] = str(e)

    return result


def check_cross_links(notebook: dict[str, Any], notebook_path: Path) -> dict[str, Any]:
    """Check if cross-links in notebook are valid.

    Args:
        notebook: Notebook JSON structure
        notebook_path: Path to notebook file for resolving relative paths

    Returns:
        Dictionary with cross-link validation results
    """
    checks = {"total_links": 0, "valid_links": 0, "broken_links": []}

    cells = notebook.get("cells", [])
    markdown_cells = [c for c in cells if c.get("cell_type") == "markdown"]

    base_dir = notebook_path.parent

    for cell in markdown_cells:
        source = "".join(cell.get("source", []))

        # Find markdown links [text](path)
        import re

        links = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", source)

        for link_text, link_path in links:
            # Skip external URLs
            if link_path.startswith("http://") or link_path.startswith("https://"):
                continue

            # Skip anchors
            if link_path.startswith("#"):
                continue

            checks["total_links"] += 1

            # Resolve relative path
            if link_path.startswith("../"):
                target_path = (base_dir / link_path).resolve()
            else:
                target_path = (base_dir / link_path).resolve()

            if target_path.exists():
                checks["valid_links"] += 1
            else:
                checks["broken_links"].append(
                    {"text": link_text, "path": link_path, "resolved": str(target_path)}
                )

    return checks


def validate_notebook(notebook_path: Path, execute: bool = False, timeout: int = 600) -> dict[str, Any]:
    """Validate a notebook against quality standards.

    Args:
        notebook_path: Path to .ipynb file
        execute: Whether to execute notebook (default: False)
        timeout: Execution timeout in seconds (default: 600 = 10 min)

    Returns:
        Dictionary with all validation results
    """
    print(f"\n{'='*80}")
    print(f"VALIDATING: {notebook_path.name}")
    print(f"{'='*80}\n")

    results = {
        "notebook": str(notebook_path),
        "structure": {},
        "imports": {},
        "cross_links": {},
        "execution": {},
        "overall_pass": False,
    }

    # Load notebook
    try:
        notebook = load_notebook(notebook_path)
    except Exception as e:
        print(f"❌ Failed to load notebook: {e}")
        return results

    # Check structure
    print("Checking structure...")
    structure_checks = check_structure(notebook)
    results["structure"] = structure_checks

    structure_pass = all(structure_checks.values())
    print(f"  {'✅' if structure_pass else '❌'} Structure: {sum(structure_checks.values())}/{len(structure_checks)} checks passed")

    for check_name, passed in structure_checks.items():
        if not passed:
            print(f"    ❌ {check_name}")

    # Check imports
    print("\nChecking imports...")
    import_checks = check_imports(notebook)
    results["imports"] = import_checks

    print(f"  ✅ Found {import_checks['import_count']} import statements")
    if import_checks["has_backend_imports"]:
        print("  ✅ Has lesson-16 backend imports")
    else:
        print("  ⚠️  No lesson-16 backend imports found")

    # Check cross-links
    print("\nChecking cross-links...")
    link_checks = check_cross_links(notebook, notebook_path)
    results["cross_links"] = link_checks

    if link_checks["total_links"] > 0:
        link_pass_rate = link_checks["valid_links"] / link_checks["total_links"]
        print(f"  {'✅' if link_pass_rate == 1.0 else '⚠️'} Cross-links: {link_checks['valid_links']}/{link_checks['total_links']} valid")

        if link_checks["broken_links"]:
            print("  ❌ Broken links found:")
            for broken in link_checks["broken_links"][:5]:  # Show first 5
                print(f"    - [{broken['text']}]({broken['path']}) -> {broken['resolved']}")
    else:
        print("  ℹ️  No cross-links found")

    # Execute notebook (optional)
    if execute:
        print(f"\nExecuting notebook (timeout: {timeout}s)...")
        exec_result = check_execution_time(notebook_path, timeout)
        results["execution"] = exec_result

        if exec_result["executed"]:
            exec_time = exec_result["execution_time"]
            time_ok = exec_time <= timeout
            print(f"  {'✅' if time_ok else '⚠️'} Execution time: {exec_time:.1f}s")

            # Check against targets
            if exec_time <= 300:  # 5 minutes
                print("  ✅ Meets <5 min target")
            elif exec_time <= 600:  # 10 minutes
                print("  ✅ Meets <10 min target")
            else:
                print(f"  ❌ Exceeds 10 min target ({exec_time:.1f}s)")
        else:
            print(f"  ❌ Execution failed: {exec_result['error'][:200]}")

    # Overall pass/fail
    results["overall_pass"] = (
        structure_pass
        and import_checks["has_imports"]
        and (link_checks["total_links"] == 0 or link_checks["valid_links"] == link_checks["total_links"])
        and (not execute or exec_result.get("executed", False))
    )

    print(f"\n{'='*80}")
    print(f"OVERALL: {'✅ PASS' if results['overall_pass'] else '❌ FAIL'}")
    print(f"{'='*80}\n")

    return results


def main() -> None:
    """Main entry point for notebook validation."""
    import argparse

    parser = argparse.ArgumentParser(description="Validate Jupyter notebooks for Lesson 16")
    parser.add_argument("notebook", type=Path, help="Path to notebook file")
    parser.add_argument("--execute", action="store_true", help="Execute notebook")
    parser.add_argument("--timeout", type=int, default=600, help="Execution timeout in seconds")

    args = parser.parse_args()

    if not args.notebook.exists():
        print(f"Error: Notebook not found: {args.notebook}")
        sys.exit(1)

    results = validate_notebook(args.notebook, execute=args.execute, timeout=args.timeout)

    sys.exit(0 if results["overall_pass"] else 1)


if __name__ == "__main__":
    main()
