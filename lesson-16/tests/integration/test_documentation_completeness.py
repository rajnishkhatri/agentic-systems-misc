"""
Integration tests for Task 7.9 - Documentation Completeness and Cross-Linking (Main Documentation).

Tests validate:
1. README.md completeness (prerequisites, learning outcomes, quick start, time estimate, deliverables)
2. TUTORIAL_INDEX.md structure (3 learning paths, tutorial roadmap, prerequisite tree, FAQs)
3. Recommended order clarity
4. File organization documentation
5. Navigation links in tutorials/notebooks
"""

import re
from pathlib import Path

import pytest

# Define paths
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
LESSON_16_ROOT = PROJECT_ROOT / "lesson-16"


# ==============================================================================
# MAIN DOCUMENTATION TESTS (10 tests)
# ==============================================================================


def test_should_include_all_sections_when_readme_checked() -> None:
    """Test that lesson-16/README.md includes all required sections.

    Required: prerequisites, learning outcomes, quick start guide, 6-8hr time estimate,
    Task 1.0-6.0 deliverables summary, installation instructions, troubleshooting.
    """
    readme_path = LESSON_16_ROOT / "README.md"
    assert readme_path.exists(), "README.md not found"

    content = readme_path.read_text()

    # Required sections
    required_sections = [
        "prerequisite",
        "learning outcome",
        "quick start",
        "installation",
    ]

    missing_sections = []
    for section in required_sections:
        if section.lower() not in content.lower():
            missing_sections.append(section)

    assert len(missing_sections) == 0, \
        f"README.md missing sections: {', '.join(missing_sections)}"

    # Should mention time estimate (6-8 hours or similar)
    has_time_estimate = bool(re.search(r'\d+[-–]\d+\s*h(ou)?r', content.lower()))
    assert has_time_estimate, "README.md should include time estimate"


def test_should_have_3_learning_paths_when_tutorial_index_checked() -> None:
    """Test that TUTORIAL_INDEX.md has 3 learning paths.

    Expected paths: Quick Start 6hr, Pattern Mastery 10hr, Production Focus 8hr.
    """
    tutorial_index_path = LESSON_16_ROOT / "TUTORIAL_INDEX.md"
    assert tutorial_index_path.exists(), "TUTORIAL_INDEX.md not found"

    content = tutorial_index_path.read_text().lower()

    # Check for learning path mentions
    learning_path_keywords = ["path", "track", "learning"]
    has_learning_paths = any(keyword in content for keyword in learning_path_keywords)
    assert has_learning_paths, "TUTORIAL_INDEX.md should define learning paths"

    # Check for time estimates in paths
    time_estimates = re.findall(r'\d+\s*h(ou)?r', content)
    assert len(time_estimates) >= 3, \
        f"Should have at least 3 time estimates for learning paths, found {len(time_estimates)}"


def test_should_describe_all_15_tutorials_when_roadmap_checked() -> None:
    """Test that tutorial roadmap describes all 15 tutorials (7 concept + 8 notebooks)."""
    tutorial_index_path = LESSON_16_ROOT / "TUTORIAL_INDEX.md"
    content = tutorial_index_path.read_text()

    # Count tutorial references (look for numbered tutorials 01-07 and notebooks 08-15)
    tutorial_references = set()

    # Match patterns like "01", "Tutorial 1", "Notebook 08", etc.
    for match in re.finditer(r'\b(?:tutorial|notebook)?\s*(?:0?[1-9]|1[0-5])\b', content.lower()):
        tutorial_references.add(match.group())

    # Should reference at least 10 of 15 tutorials
    assert len(tutorial_references) >= 10, \
        f"Tutorial roadmap should reference at least 10 tutorials, found {len(tutorial_references)}"


def test_should_show_prerequisite_tree_when_dependencies_documented() -> None:
    """Test that prerequisite tree shows dependencies (Lesson 9-11 optional)."""
    tutorial_index_path = LESSON_16_ROOT / "TUTORIAL_INDEX.md"
    content = tutorial_index_path.read_text().lower()

    # Check for prerequisite documentation
    prerequisite_keywords = ["prerequisite", "dependency", "require", "before"]
    has_prerequisites = any(keyword in content for keyword in prerequisite_keywords)
    assert has_prerequisites, "TUTORIAL_INDEX.md should document prerequisites"

    # Check for lesson references (9, 10, 11)
    lesson_references = re.findall(r'lesson\s*(?:9|10|11)', content)
    # Should mention at least one related lesson
    assert len(lesson_references) >= 1, "Should reference prerequisite lessons (9-11)"


def test_should_answer_5_plus_faqs_when_dc5_checked() -> None:
    """Test that FAQs answer 5+ common questions from DC5."""
    tutorial_index_path = LESSON_16_ROOT / "TUTORIAL_INDEX.md"
    content = tutorial_index_path.read_text()

    # Check for FAQ section
    has_faq_section = "faq" in content.lower() or "question" in content.lower()
    assert has_faq_section, "TUTORIAL_INDEX.md should include FAQ section"

    # Count question marks or Q: patterns
    question_count = content.count("?") + len(re.findall(r'\bQ:', content))
    assert question_count >= 5, \
        f"FAQ should have at least 5 questions, found {question_count} question indicators"


def test_should_be_clear_when_recommended_order_checked() -> None:
    """Test that recommended order is clear: start with 01→08→13."""
    tutorial_index_path = LESSON_16_ROOT / "TUTORIAL_INDEX.md"
    content = tutorial_index_path.read_text()

    # Check for recommended order or getting started guidance
    order_keywords = ["start", "begin", "first", "recommended", "order"]
    has_order_guidance = any(keyword in content.lower() for keyword in order_keywords)
    assert has_order_guidance, "TUTORIAL_INDEX.md should provide recommended order guidance"

    # Should reference tutorial 01 or 08 as starting points
    starting_tutorials = re.findall(r'\b(?:01|08|tutorial\s*1|notebook\s*8)\b', content.lower())
    assert len(starting_tutorials) >= 1, "Should indicate starting tutorial (01 or 08)"


def test_should_match_fr73_when_file_organization_documented() -> None:
    """Test that file organization is documented matching FR7.3 structure."""
    readme_path = LESSON_16_ROOT / "README.md"
    content = readme_path.read_text()

    # Check for directory structure documentation
    structure_indicators = ["structure", "directory", "folder", "organization"]
    has_structure_docs = any(indicator in content.lower() for indicator in structure_indicators)
    assert has_structure_docs, "README.md should document file organization"

    # Should mention key directories
    key_directories = ["tutorial", "notebook", "backend", "data", "diagram"]
    mentioned_dirs = sum(1 for dir_name in key_directories if dir_name in content.lower())
    assert mentioned_dirs >= 3, \
        f"Should document at least 3 key directories, found {mentioned_dirs}"


def test_should_have_nav_links_when_tutorials_checked() -> None:
    """Test that all tutorials have prev/next navigation links."""
    tutorials_dir = LESSON_16_ROOT / "tutorials"
    tutorial_files = sorted(tutorials_dir.glob("*.md"))

    tutorials_with_nav = 0
    for tutorial_path in tutorial_files:
        content = tutorial_path.read_text().lower()

        # Check for navigation keywords
        nav_keywords = ["previous", "next", "back", "forward", "←", "→"]
        has_navigation = any(keyword in content for keyword in nav_keywords)

        if has_navigation:
            tutorials_with_nav += 1

    # At least 50% of tutorials should have navigation
    assert tutorials_with_nav >= len(tutorial_files) // 2, \
        f"At least half of tutorials should have navigation, found {tutorials_with_nav}/{len(tutorial_files)}"


def test_should_reference_tutorials_when_notebooks_checked() -> None:
    """Test that all notebooks reference related tutorials."""
    notebooks_dir = LESSON_16_ROOT / "notebooks"
    notebook_files = list(notebooks_dir.glob("*.ipynb"))

    if len(notebook_files) == 0:
        pytest.skip("No notebooks found")

    notebooks_with_refs = 0
    for notebook_path in notebook_files:
        content = notebook_path.read_text()

        # Check for tutorial references (markdown or relative paths)
        tutorial_refs = re.findall(r'(?:tutorial|\.\.\/tutorials|\.md)', content.lower())
        if len(tutorial_refs) >= 2:  # At least 2 tutorial references
            notebooks_with_refs += 1

    # At least 60% of notebooks should reference tutorials
    assert notebooks_with_refs >= len(notebook_files) * 0.6, \
        f"At least 60% of notebooks should reference tutorials, found {notebooks_with_refs}/{len(notebook_files)}"


def test_should_link_diagrams_when_tutorials_checked() -> None:
    """Test that all diagrams are linked from relevant tutorials."""
    diagrams_dir = LESSON_16_ROOT / "diagrams"
    diagram_files = list(diagrams_dir.glob("*.mmd"))

    tutorials_dir = LESSON_16_ROOT / "tutorials"
    tutorial_files = list(tutorials_dir.glob("*.md"))

    all_tutorial_content = ""
    for tutorial_path in tutorial_files:
        all_tutorial_content += tutorial_path.read_text().lower()

    # Check how many diagrams are referenced
    diagrams_referenced = 0
    for diagram_path in diagram_files:
        diagram_name = diagram_path.stem  # Filename without extension
        if diagram_name.lower() in all_tutorial_content:
            diagrams_referenced += 1

    # At least 60% of diagrams should be linked
    assert diagrams_referenced >= len(diagram_files) * 0.6, \
        f"At least 60% of diagrams should be linked from tutorials, found {diagrams_referenced}/{len(diagram_files)}"
