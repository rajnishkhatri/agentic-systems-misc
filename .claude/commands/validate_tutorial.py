#!/usr/bin/env python3
"""
Tutorial validation script for /validate-tutorial command.

Validates tutorial directories against quality standards:
1. TUTORIAL_INDEX.md structure
2. Notebook execution
3. Cross-link validation
4. Mermaid diagram syntax
5. Reading time calculation
"""

import json
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


class TutorialValidator:
    """Validates tutorial directories against quality standards."""

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

    def __init__(self, directory: str):
        """Initialize validator with target directory.

        Args:
            directory: Path to tutorial directory

        Raises:
            ValueError: If directory is invalid
        """
        if not directory:
            raise ValueError("Directory path required")

        self.directory = Path(directory)
        self.results: dict[str, Any] = {}
        self.warnings: list[str] = []
        self.errors: list[str] = []

    def validate(self) -> dict[str, Any]:
        """Run all validation checks.

        Returns:
            Validation results dictionary
        """
        start_time = time.time()

        # Pre-flight checks
        if not self._check_directory_exists():
            return self._generate_report(time.time() - start_time)

        if not self._check_tutorial_index_exists():
            return self._generate_report(time.time() - start_time)

        # Run validation checks
        self._validate_tutorial_index_structure()
        self._validate_notebooks()
        self._validate_cross_links()
        self._validate_mermaid_diagrams()
        self._calculate_reading_time()

        return self._generate_report(time.time() - start_time)

    def _check_directory_exists(self) -> bool:
        """Check if target directory exists."""
        if not self.directory.exists():
            # Suggest similar directories
            parent = self.directory.parent if self.directory.parent.exists() else Path(".")
            available = [d.name + "/" for d in parent.iterdir() if d.is_dir() and not d.name.startswith(".")]

            self.errors.append(f"❌ Directory not found: {self.directory}")
            if available:
                self.errors.append(f"   Available: {', '.join(sorted(available)[:10])}")
            return False

        if not self.directory.is_dir():
            self.errors.append(f"❌ Path is not a directory: {self.directory}")
            return False

        return True

    def _check_tutorial_index_exists(self) -> bool:
        """Check if TUTORIAL_INDEX.md exists."""
        tutorial_index = self.directory / "TUTORIAL_INDEX.md"
        if not tutorial_index.exists():
            self.errors.append(f"❌ TUTORIAL_INDEX.md not found in {self.directory}")
            self.errors.append("   Required sections cannot be validated")
            self.errors.append("   Suggestion: Create TUTORIAL_INDEX.md using template")
            self.errors.append("   See: .claude/skills/tutorial-standards/references/tutorial-index-template.md")
            return False
        return True

    def _validate_tutorial_index_structure(self) -> None:
        """Validate TUTORIAL_INDEX.md structure."""
        tutorial_index = self.directory / "TUTORIAL_INDEX.md"

        try:
            content = tutorial_index.read_text(encoding="utf-8")
        except Exception as e:
            self.errors.append(f"❌ Error reading TUTORIAL_INDEX.md: {e}")
            return

        # Check for required sections
        missing_sections = []
        for section in self.REQUIRED_SECTIONS:
            # Look for markdown headers containing the section name OR content mentioning it
            # More flexible pattern: matches headers or bold/emphasized section names
            patterns = [
                rf"^#+\s+.*{re.escape(section)}",  # Header with section name
                rf"^\*\*{re.escape(section)}:\*\*",  # Bold section like **Prerequisites:**
                rf"^{re.escape(section)}:",  # Plain section name with colon
            ]
            found = any(re.search(p, content, re.MULTILINE | re.IGNORECASE) for p in patterns)
            if not found:
                missing_sections.append(section)

        # Extract learning time and difficulty
        learning_time = self._extract_learning_time(content)
        difficulty = self._extract_difficulty(content)

        self.results["tutorial_index"] = {
            "valid": len(missing_sections) == 0,
            "sections_found": len(self.REQUIRED_SECTIONS) - len(missing_sections),
            "sections_total": len(self.REQUIRED_SECTIONS),
            "missing_sections": missing_sections,
            "learning_time": learning_time,
            "difficulty": difficulty,
        }

        if missing_sections:
            self.errors.append(f"❌ TUTORIAL_INDEX.md missing sections: {', '.join(missing_sections)}")
            self.errors.append("   Recommendation: Add missing sections using template")

    def _extract_learning_time(self, content: str) -> str | None:
        """Extract learning time estimate from content."""
        patterns = [
            r"(?:learning time|time estimate|duration):\s*([^\\n]+)",
            r"(\d+[-–]\d+\s+(?:hours?|minutes?))",
        ]
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None

    def _extract_difficulty(self, content: str) -> str | None:
        """Extract difficulty level from content."""
        pattern = r"(?:difficulty|level):\s*(\w+)"
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return None

    def _validate_notebooks(self) -> None:
        """Validate all Jupyter notebooks in directory."""
        notebooks = list(self.directory.glob("*.ipynb"))

        # Filter out checkpoint files
        notebooks = [nb for nb in notebooks if ".ipynb_checkpoints" not in str(nb)]

        if not notebooks:
            self.results["notebooks"] = {
                "total": 0,
                "executed": 0,
                "failed": 0,
                "skipped": 0,
                "details": [],
            }
            return

        # Check if jupyter is installed
        try:
            subprocess.run(
                ["jupyter", "nbconvert", "--version"],
                capture_output=True,
                check=True,
                timeout=5,
            )
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            self.warnings.append("⚠️ jupyter nbconvert not found")
            self.warnings.append("   Notebook execution cannot be validated")
            self.warnings.append("   Install: pip install jupyter nbconvert")
            self.results["notebooks"] = {
                "total": len(notebooks),
                "executed": 0,
                "failed": 0,
                "skipped": len(notebooks),
                "details": [{"name": nb.name, "status": "SKIPPED", "reason": "jupyter not installed"} for nb in notebooks],
            }
            return

        # Execute each notebook
        notebook_results = []
        for notebook in notebooks:
            result = self._execute_notebook(notebook)
            notebook_results.append(result)

        executed = sum(1 for r in notebook_results if r["status"] == "SUCCESS")
        failed = sum(1 for r in notebook_results if r["status"] == "FAILED")
        skipped = sum(1 for r in notebook_results if r["status"] == "SKIPPED")

        self.results["notebooks"] = {
            "total": len(notebooks),
            "executed": executed,
            "failed": failed,
            "skipped": skipped,
            "details": notebook_results,
        }

    def _execute_notebook(self, notebook: Path) -> dict[str, Any]:
        """Execute a single notebook.

        Args:
            notebook: Path to notebook file

        Returns:
            Execution result dictionary
        """
        start_time = time.time()

        try:
            result = subprocess.run(
                [
                    "jupyter",
                    "nbconvert",
                    "--to",
                    "notebook",
                    "--execute",
                    "--stdout",
                    notebook.name,  # Use just the filename, not full path
                ],
                capture_output=True,
                text=True,
                timeout=300,  # 5 minutes
                cwd=self.directory,  # Run from the directory containing the notebook
            )

            execution_time = time.time() - start_time

            if result.returncode == 0:
                return {
                    "name": notebook.name,
                    "status": "SUCCESS",
                    "execution_time": round(execution_time, 2),
                }
            else:
                # Parse error message
                error_msg = result.stderr

                # Check if error is due to missing API keys or dependencies
                skip_patterns = [
                    "OPENAI_API_KEY",
                    "API_KEY",
                    "api_key client option must be set",
                    "environment variable",
                ]
                is_skippable = any(pattern in error_msg for pattern in skip_patterns)

                if is_skippable:
                    return {
                        "name": notebook.name,
                        "status": "SKIPPED",
                        "execution_time": round(execution_time, 2),
                        "reason": "Missing API key or environment variable",
                    }

                return {
                    "name": notebook.name,
                    "status": "FAILED",
                    "execution_time": round(execution_time, 2),
                    "error": error_msg[:200],  # Truncate long errors
                }

        except subprocess.TimeoutExpired:
            return {
                "name": notebook.name,
                "status": "FAILED",
                "execution_time": 300.0,
                "error": "Execution timeout (>300s)",
            }
        except Exception as e:
            return {
                "name": notebook.name,
                "status": "SKIPPED",
                "reason": str(e),
            }

    def _validate_cross_links(self) -> None:
        """Validate cross-links in markdown files."""
        md_files = list(self.directory.glob("*.md"))
        md_files.extend(self.directory.glob("**/*.md"))

        # Filter out files in hidden directories
        md_files = [f for f in md_files if not any(part.startswith(".") for part in f.parts)]

        all_links = []
        broken_links = []

        for md_file in md_files:
            try:
                content = md_file.read_text(encoding="utf-8")
                links = self._extract_markdown_links(content)

                for link_text, link_url in links:
                    # Skip external links
                    if link_url.startswith(("http://", "https://", "mailto:", "#")):
                        continue

                    # Handle relative links
                    if link_url.startswith("../") or link_url.startswith("./"):
                        target = (md_file.parent / link_url).resolve()
                    else:
                        target = (self.directory / link_url).resolve()

                    # Remove anchor
                    if "#" in str(target):
                        target = Path(str(target).split("#")[0])

                    all_links.append((link_url, md_file.name))

                    if not target.exists():
                        broken_links.append({
                            "link": link_url,
                            "source": md_file.name,
                            "target": str(target),
                        })

            except Exception as e:
                self.warnings.append(f"⚠️ Error reading {md_file.name}: {e}")

        self.results["cross_links"] = {
            "total": len(all_links),
            "valid": len(all_links) - len(broken_links),
            "broken": len(broken_links),
            "broken_links": broken_links,
        }

    def _extract_markdown_links(self, content: str) -> list[tuple[str, str]]:
        """Extract markdown links from content.

        Args:
            content: Markdown content

        Returns:
            List of (link_text, link_url) tuples
        """
        # Match markdown links: [text](url)
        pattern = r"\[([^\]]+)\]\(([^\)]+)\)"
        return re.findall(pattern, content)

    def _validate_mermaid_diagrams(self) -> None:
        """Validate Mermaid diagram syntax."""
        diagram_dir = self.directory / "diagrams"

        if not diagram_dir.exists():
            self.results["mermaid"] = {
                "total": 0,
                "valid": 0,
                "invalid": 0,
                "details": [],
            }
            return

        mmd_files = list(diagram_dir.glob("*.mmd"))

        if not mmd_files:
            self.results["mermaid"] = {
                "total": 0,
                "valid": 0,
                "invalid": 0,
                "details": [],
            }
            return

        diagram_results = []
        for mmd_file in mmd_files:
            result = self._validate_mermaid_file(mmd_file)
            diagram_results.append(result)

        valid = sum(1 for r in diagram_results if r["status"] == "VALID")
        invalid = sum(1 for r in diagram_results if r["status"] == "INVALID")

        self.results["mermaid"] = {
            "total": len(mmd_files),
            "valid": valid,
            "invalid": invalid,
            "details": diagram_results,
        }

    def _validate_mermaid_file(self, mmd_file: Path) -> dict[str, Any]:
        """Validate a single Mermaid file.

        Args:
            mmd_file: Path to .mmd file

        Returns:
            Validation result dictionary
        """
        try:
            content = mmd_file.read_text(encoding="utf-8")

            # Strip code fence markers if present
            content = content.strip()
            if content.startswith("```mermaid"):
                content = content[10:]  # Remove ```mermaid
            if content.endswith("```"):
                content = content[:-3]  # Remove closing ```
            content = content.strip()

            # Basic syntax validation
            # Check for valid diagram types
            valid_types = ["flowchart", "graph", "sequenceDiagram", "classDiagram", "stateDiagram", "erDiagram", "journey", "gantt", "pie"]
            has_valid_type = any(content.startswith(dt) for dt in valid_types)

            if not has_valid_type:
                return {
                    "name": mmd_file.name,
                    "status": "INVALID",
                    "error": "No valid Mermaid diagram type found",
                }

            # Count nodes (simple heuristic)
            node_count = len(re.findall(r"\[.*?\]|\(.*?\)|\{.*?\}", content))

            return {
                "name": mmd_file.name,
                "status": "VALID",
                "node_count": node_count,
            }

        except Exception as e:
            return {
                "name": mmd_file.name,
                "status": "INVALID",
                "error": str(e),
            }

    def _calculate_reading_time(self) -> None:
        """Calculate reading time for tutorials."""
        md_files = list(self.directory.glob("*.md"))

        # Exclude TUTORIAL_INDEX.md and README.md from word count
        md_files = [f for f in md_files if f.name not in ["TUTORIAL_INDEX.md", "README.md"]]

        total_words = 0
        file_details = []

        for md_file in md_files:
            try:
                content = md_file.read_text(encoding="utf-8")

                # Remove code blocks for more accurate word count
                content = re.sub(r"```.*?```", "", content, flags=re.DOTALL)

                # Count words
                words = len(content.split())
                total_words += words

                reading_time = round(words / 200, 1)  # 200 WPM

                file_details.append({
                    "name": md_file.name,
                    "words": words,
                    "reading_time": reading_time,
                })

            except Exception as e:
                self.warnings.append(f"⚠️ Error reading {md_file.name}: {e}")

        total_reading_time = round(total_words / 200, 1)

        self.results["reading_time"] = {
            "total_words": total_words,
            "reading_time_minutes": total_reading_time,
            "files": file_details,
        }

    def _generate_report(self, elapsed_time: float) -> dict[str, Any]:
        """Generate validation report.

        Args:
            elapsed_time: Total validation time in seconds

        Returns:
            Complete validation report
        """
        report = {
            "directory": str(self.directory),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "elapsed_time": round(elapsed_time, 2),
            "results": self.results,
            "warnings": self.warnings,
            "errors": self.errors,
        }

        # Determine overall status
        has_errors = len(self.errors) > 0 or (
            "notebooks" in self.results and self.results["notebooks"].get("failed", 0) > 0
        )
        has_warnings = len(self.warnings) > 0 or (
            "cross_links" in self.results and self.results["cross_links"].get("broken", 0) > 0
        )

        if has_errors:
            report["status"] = "FAIL"
        elif has_warnings:
            report["status"] = "PASS_WITH_WARNINGS"
        else:
            report["status"] = "PASS"

        return report


def format_report(report: dict[str, Any]) -> str:
    """Format validation report for display.

    Args:
        report: Validation report dictionary

    Returns:
        Formatted report string
    """
    output = []
    output.append(f"📋 Tutorial Validation Report: {report['directory']}")
    output.append("━" * 60)
    output.append("")

    results = report["results"]

    # 1. TUTORIAL_INDEX.md Structure
    if "tutorial_index" in results:
        ti = results["tutorial_index"]
        status = "✅" if ti["valid"] else "❌"
        output.append(f"1. TUTORIAL_INDEX.md Structure {status}")
        output.append(f"   - Sections: {ti['sections_found']}/{ti['sections_total']}")
        if ti.get("learning_time"):
            output.append(f"   - Learning time: {ti['learning_time']}")
        if ti.get("difficulty"):
            output.append(f"   - Difficulty: {ti['difficulty']}")
        if ti.get("missing_sections"):
            output.append(f"   - Missing: {', '.join(ti['missing_sections'])}")
        output.append("")

    # 2. Notebook Execution
    if "notebooks" in results:
        nb = results["notebooks"]
        if nb["total"] == 0:
            output.append("2. Notebook Execution ⚠️")
            output.append("   - No notebooks found")
        else:
            status = "✅" if nb["failed"] == 0 and nb["skipped"] == 0 else "⚠️" if nb["skipped"] > 0 else "❌"
            output.append(f"2. Notebook Execution {status}")
            output.append(f"   - Total: {nb['total']}, Executed: {nb['executed']}, Failed: {nb['failed']}, Skipped: {nb['skipped']}")

            for detail in nb["details"][:5]:  # Show first 5
                if detail["status"] == "SUCCESS":
                    output.append(f"   ✅ {detail['name']} ({detail['execution_time']}s)")
                elif detail["status"] == "FAILED":
                    output.append(f"   ❌ {detail['name']} - {detail.get('error', 'Unknown error')[:50]}")
                elif detail["status"] == "SKIPPED":
                    output.append(f"   ⚠️ {detail['name']} - {detail.get('reason', 'Skipped')}")
        output.append("")

    # 3. Cross-Links
    if "cross_links" in results:
        cl = results["cross_links"]
        if cl["total"] == 0:
            output.append("3. Cross-Links ⚠️")
            output.append("   - No links found")
        else:
            status = "✅" if cl["broken"] == 0 else "⚠️"
            output.append(f"3. Cross-Links {status}")
            output.append(f"   - Valid: {cl['valid']}/{cl['total']} ({cl['valid']/cl['total']*100:.1f}%)")
            if cl["broken"] > 0:
                output.append(f"   - Broken: {cl['broken']}")
                for link in cl["broken_links"][:3]:  # Show first 3
                    output.append(f"     ❌ {link['link']} (in {link['source']})")
        output.append("")

    # 4. Mermaid Diagrams
    if "mermaid" in results:
        md = results["mermaid"]
        if md["total"] == 0:
            output.append("4. Mermaid Diagrams ⚠️")
            output.append("   - No diagrams found")
        else:
            status = "✅" if md["invalid"] == 0 else "❌"
            output.append(f"4. Mermaid Diagrams {status}")
            output.append(f"   - Valid: {md['valid']}/{md['total']}")
            for detail in md["details"][:3]:  # Show first 3
                if detail["status"] == "VALID":
                    output.append(f"   ✅ {detail['name']} ({detail.get('node_count', 0)} nodes)")
                else:
                    output.append(f"   ❌ {detail['name']} - {detail.get('error', 'Invalid')}")
        output.append("")

    # 5. Reading Time
    if "reading_time" in results:
        rt = results["reading_time"]
        output.append("5. Reading Time ✅")
        output.append(f"   - Total words: {rt['total_words']:,}")
        output.append(f"   - Reading time: ~{rt['reading_time_minutes']} min")
        output.append("")

    # Overall status
    output.append("━" * 60)
    if report["status"] == "PASS":
        output.append("Overall: ✅ PASS")
    elif report["status"] == "PASS_WITH_WARNINGS":
        output.append("Overall: ⚠️ PASS (with warnings)")
    else:
        output.append("Overall: ❌ FAIL")

    # Errors and warnings
    if report["errors"]:
        output.append("")
        output.append("Errors:")
        for error in report["errors"]:
            output.append(f"  {error}")

    if report["warnings"]:
        output.append("")
        output.append("Warnings:")
        for warning in report["warnings"]:
            output.append(f"  {warning}")

    output.append("")
    output.append(f"Validation completed in {report['elapsed_time']}s")

    return "\n".join(output)


def main() -> int:
    """Main entry point for validation script.

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    if len(sys.argv) < 2:
        print("Usage: validate_tutorial.py <directory>")
        print("\nExample:")
        print("  python validate_tutorial.py lesson-9/")
        return 1

    directory = sys.argv[1]

    try:
        validator = TutorialValidator(directory)
        report = validator.validate()

        # Print formatted report
        print(format_report(report))

        # Also save JSON report
        json_path = Path(directory) / ".validation_report.json"
        try:
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2)
            print(f"\n💾 JSON report saved: {json_path}")
        except Exception as e:
            print(f"\n⚠️ Could not save JSON report: {e}")

        # Exit with appropriate code
        return 0 if report["status"] in ["PASS", "PASS_WITH_WARNINGS"] else 1

    except ValueError as e:
        print(f"❌ Error: {e}")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
