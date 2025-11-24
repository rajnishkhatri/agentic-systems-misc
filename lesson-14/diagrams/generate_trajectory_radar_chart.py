"""
Generate trajectory metrics comparison radar chart.

This script creates a radar chart (spider chart) visualizing the 6 trajectory
evaluation metrics for sample agent performance.

Usage:
    python lesson-14/diagrams/generate_trajectory_radar_chart.py

Output:
    lesson-14/diagrams/trajectory_metrics_comparison.png
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def create_trajectory_radar_chart() -> None:
    """Generate radar chart comparing trajectory metrics for two agents."""

    # Define trajectory metrics
    categories = [
        'Exact Match',
        'In-Order Match',
        'Any-Order Match',
        'Precision',
        'Recall',
        'Single-Tool Use'
    ]

    # Sample data for Agent A (High precision, moderate recall)
    agent_a_scores = [0.2, 0.5, 0.6, 0.85, 0.70, 0.9]

    # Sample data for Agent B (Balanced performance)
    agent_b_scores = [0.3, 0.7, 0.8, 0.75, 0.85, 0.8]

    # Number of variables
    N = len(categories)

    # Compute angle for each metric
    angles = [n / float(N) * 2 * np.pi for n in range(N)]

    # Close the plot (repeat first value)
    agent_a_scores += agent_a_scores[:1]
    agent_b_scores += agent_b_scores[:1]
    angles += angles[:1]

    # Initialize figure
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))

    # Plot Agent A
    ax.plot(angles, agent_a_scores, 'o-', linewidth=2, label='Agent A', color='#4A90E2')
    ax.fill(angles, agent_a_scores, alpha=0.25, color='#4A90E2')

    # Plot Agent B
    ax.plot(angles, agent_b_scores, 's-', linewidth=2, label='Agent B', color='#228B22')
    ax.fill(angles, agent_b_scores, alpha=0.25, color='#228B22')

    # Set category labels
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, size=12)

    # Set value range (0-1)
    ax.set_ylim(0, 1)
    ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_yticklabels(['0.2', '0.4', '0.6', '0.8', '1.0'], size=10)

    # Add gridlines
    ax.grid(True, linestyle='--', linewidth=0.5, alpha=0.7)

    # Add legend
    ax.legend(loc='upper right', bbox_to_anchor=(1.2, 1.1), fontsize=12)

    # Add title
    plt.title('Trajectory Evaluation Metrics Comparison\n(Agent A vs. Agent B)',
              size=16, weight='bold', pad=20)

    # Add interpretation text
    interpretation_text = (
        "Agent A: High precision (0.85), moderate recall (0.70) → Focused but incomplete\n"
        "Agent B: Balanced precision (0.75), high recall (0.85) → Comprehensive coverage"
    )
    fig.text(0.5, 0.02, interpretation_text, ha='center', fontsize=10,
             style='italic', color='#555')

    # Save figure
    output_path = Path(__file__).parent / 'trajectory_metrics_comparison.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"✅ Radar chart saved to: {output_path}")

    # Display (optional - comment out for batch processing)
    # plt.show()

    plt.close()


def create_single_agent_radar_chart() -> None:
    """Generate radar chart for a single agent (for tutorial examples)."""

    # Define trajectory metrics
    categories = [
        'Exact Match',
        'In-Order Match',
        'Any-Order Match',
        'Precision',
        'Recall',
        'Single-Tool Use'
    ]

    # Sample data for tutorial example
    scores = [0.2, 0.5, 0.6, 0.85, 0.70, 0.9]

    # Number of variables
    N = len(categories)

    # Compute angle for each metric
    angles = [n / float(N) * 2 * np.pi for n in range(N)]

    # Close the plot
    scores += scores[:1]
    angles += angles[:1]

    # Initialize figure
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))

    # Plot agent
    ax.plot(angles, scores, 'o-', linewidth=2, label='Agent Performance', color='#4A90E2')
    ax.fill(angles, scores, alpha=0.3, color='#4A90E2')

    # Set category labels
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, size=11)

    # Set value range (0-1)
    ax.set_ylim(0, 1)
    ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_yticklabels(['0.2', '0.4', '0.6', '0.8', '1.0'], size=9)

    # Add gridlines
    ax.grid(True, linestyle='--', linewidth=0.5, alpha=0.7)

    # Add legend
    ax.legend(loc='upper right', bbox_to_anchor=(1.15, 1.05), fontsize=11)

    # Add title
    plt.title('Agent Trajectory Evaluation Profile',
              size=14, weight='bold', pad=15)

    # Save figure
    output_path = Path(__file__).parent / 'trajectory_metrics_single_agent.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"✅ Single-agent radar chart saved to: {output_path}")

    plt.close()


def main() -> None:
    """Generate all trajectory radar charts."""
    print("Generating trajectory metrics radar charts...")

    # Primary chart for tutorial
    create_trajectory_radar_chart()

    # Secondary chart for examples
    create_single_agent_radar_chart()

    print("\n✅ All charts generated successfully!")
    print("\nChart Descriptions:")
    print("1. trajectory_metrics_comparison.png: Compare Agent A vs Agent B")
    print("2. trajectory_metrics_single_agent.png: Single agent profile (for tutorial examples)")


if __name__ == "__main__":
    main()
