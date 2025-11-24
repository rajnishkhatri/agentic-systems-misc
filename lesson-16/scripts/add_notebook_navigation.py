#!/usr/bin/env python3
"""Add prev/next navigation to lesson-16 notebooks.

This script adds navigation markdown cells to the beginning and end of each notebook
for easier navigation between related tutorials.
"""

import json
from pathlib import Path
from typing import Any

# Notebook sequence with prev/next references
NOTEBOOK_SEQUENCE = [
    {
        "file": "08_sequential_orchestration_baseline.ipynb",
        "title": "Sequential Orchestration Baseline",
        "prev": None,
        "prev_title": None,
        "next": "09_hierarchical_delegation_pattern.ipynb",
        "next_title": "Hierarchical Delegation Pattern",
    },
    {
        "file": "09_hierarchical_delegation_pattern.ipynb",
        "title": "Hierarchical Delegation Pattern",
        "prev": "08_sequential_orchestration_baseline.ipynb",
        "prev_title": "Sequential Orchestration Baseline",
        "next": "10_iterative_refinement_react.ipynb",
        "next_title": "Iterative Refinement (ReAct/Reflexion)",
    },
    {
        "file": "10_iterative_refinement_react.ipynb",
        "title": "Iterative Refinement (ReAct/Reflexion)",
        "prev": "09_hierarchical_delegation_pattern.ipynb",
        "prev_title": "Hierarchical Delegation Pattern",
        "next": "11_state_machine_orchestration.ipynb",
        "next_title": "State Machine Orchestration",
    },
    {
        "file": "11_state_machine_orchestration.ipynb",
        "title": "State Machine Orchestration",
        "prev": "10_iterative_refinement_react.ipynb",
        "prev_title": "Iterative Refinement (ReAct/Reflexion)",
        "next": "12_voting_ensemble_pattern.ipynb",
        "next_title": "Voting/Ensemble Pattern",
    },
    {
        "file": "12_voting_ensemble_pattern.ipynb",
        "title": "Voting/Ensemble Pattern",
        "prev": "11_state_machine_orchestration.ipynb",
        "prev_title": "State Machine Orchestration",
        "next": "13_reliability_framework_implementation.ipynb",
        "next_title": "Reliability Framework Implementation",
    },
    {
        "file": "13_reliability_framework_implementation.ipynb",
        "title": "Reliability Framework Implementation",
        "prev": "12_voting_ensemble_pattern.ipynb",
        "prev_title": "Voting/Ensemble Pattern",
        "next": "14_agentarch_benchmark_reproduction.ipynb",
        "next_title": "AgentArch Benchmark Reproduction",
    },
    {
        "file": "14_agentarch_benchmark_reproduction.ipynb",
        "title": "AgentArch Benchmark Reproduction",
        "prev": "13_reliability_framework_implementation.ipynb",
        "prev_title": "Reliability Framework Implementation",
        "next": "15_production_deployment_tutorial.ipynb",
        "next_title": "Production Deployment Tutorial",
    },
    {
        "file": "15_production_deployment_tutorial.ipynb",
        "title": "Production Deployment Tutorial",
        "prev": "14_agentarch_benchmark_reproduction.ipynb",
        "prev_title": "AgentArch Benchmark Reproduction",
        "next": None,
        "next_title": None,
    },
]


def create_navigation_header(nb_info: dict[str, Any]) -> str:
    """Create navigation header markdown for notebook."""
    nav_parts = []

    # Add "🏠 Index" link
    nav_parts.append("[🏠 Tutorial Index](../TUTORIAL_INDEX.md)")

    # Add prev link if exists
    if nb_info["prev"]:
        nav_parts.append(f"[⬅️ Previous: {nb_info['prev_title']}]({nb_info['prev']})")

    # Add next link if exists
    if nb_info["next"]:
        nav_parts.append(f"[➡️ Next: {nb_info['next_title']}]({nb_info['next']})")

    separator = " | "
    return f"**Navigation:** {separator.join(nav_parts)}\n\n---"


def create_navigation_footer(nb_info: dict[str, Any]) -> str:
    """Create navigation footer markdown for notebook."""
    footer = "\n---\n\n## Navigation\n\n"

    if nb_info["prev"]:
        footer += f"⬅️ **Previous:** [{nb_info['prev_title']}]({nb_info['prev']})\n\n"

    if nb_info["next"]:
        footer += f"➡️ **Next:** [{nb_info['next_title']}]({nb_info['next']})\n\n"

    footer += "🏠 **Tutorial Index:** [Lesson 16 TUTORIAL_INDEX.md](../TUTORIAL_INDEX.md)"

    return footer


def add_navigation_to_notebook(notebook_path: Path, nb_info: dict[str, Any]) -> None:
    """Add navigation cells to a notebook.

    Args:
        notebook_path: Path to notebook file
        nb_info: Notebook metadata with prev/next links
    """
    print(f"Processing {notebook_path.name}...")

    # Load notebook
    with open(notebook_path, "r", encoding="utf-8") as f:
        notebook = json.load(f)

    cells = notebook.get("cells", [])

    # Create navigation cells
    nav_header_cell = {
        "cell_type": "markdown",
        "metadata": {},
        "source": [create_navigation_header(nb_info)]
    }

    nav_footer_cell = {
        "cell_type": "markdown",
        "metadata": {},
        "source": [create_navigation_footer(nb_info)]
    }

    # Check if navigation already exists
    has_header_nav = False
    has_footer_nav = False

    if cells and cells[0].get("cell_type") == "markdown":
        first_cell_source = "".join(cells[0].get("source", []))
        if "**Navigation:**" in first_cell_source or "🏠 Tutorial Index" in first_cell_source:
            has_header_nav = True
            print(f"  ⚠️ Header navigation already exists, replacing...")
            cells[0] = nav_header_cell

    if cells and cells[-1].get("cell_type") == "markdown":
        last_cell_source = "".join(cells[-1].get("source", []))
        if "## Navigation" in last_cell_source or "🏠 **Tutorial Index:**" in last_cell_source:
            has_footer_nav = True
            print(f"  ⚠️ Footer navigation already exists, replacing...")
            cells[-1] = nav_footer_cell

    # Add navigation if not exists
    if not has_header_nav:
        cells.insert(0, nav_header_cell)
        print(f"  ✅ Added header navigation")

    if not has_footer_nav:
        cells.append(nav_footer_cell)
        print(f"  ✅ Added footer navigation")

    # Update notebook
    notebook["cells"] = cells

    # Save notebook
    with open(notebook_path, "w", encoding="utf-8") as f:
        json.dump(notebook, f, indent=1, ensure_ascii=False)

    print(f"  ✅ Saved {notebook_path.name}\n")


def main() -> None:
    """Add navigation to all lesson-16 notebooks."""
    notebooks_dir = Path(__file__).parent.parent / "notebooks"

    if not notebooks_dir.exists():
        print(f"❌ Notebooks directory not found: {notebooks_dir}")
        return

    print("Adding navigation to Lesson 16 notebooks...\n")
    print("=" * 80)

    for nb_info in NOTEBOOK_SEQUENCE:
        notebook_path = notebooks_dir / nb_info["file"]

        if not notebook_path.exists():
            print(f"⚠️ Notebook not found: {nb_info['file']}, skipping...")
            continue

        add_navigation_to_notebook(notebook_path, nb_info)

    print("=" * 80)
    print(f"\n🎉 Navigation added to {len(NOTEBOOK_SEQUENCE)} notebooks!")
    print("\nVerify changes:")
    print("  1. Open notebooks in JupyterLab/VS Code")
    print("  2. Check first cell has 'Navigation: 🏠 | ⬅️ | ➡️'")
    print("  3. Check last cell has '## Navigation' section")
    print("  4. Test links work in rendered markdown")


if __name__ == "__main__":
    main()
