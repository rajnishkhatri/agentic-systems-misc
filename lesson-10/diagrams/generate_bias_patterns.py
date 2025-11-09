"""
Generate visualization of common judge biases for Lesson 10.

Creates a 3-subplot figure showing:
1. Self-preference bias (judges favor own model)
2. Position bias (judges favor first or second position)
3. Verbosity bias (judges favor longer responses)
"""

import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# Set style
plt.style.use('seaborn-v0_8-darkgrid')

# Create figure with 3 subplots
fig, axes = plt.subplots(1, 3, figsize=(18, 5))
fig.suptitle('Common AI Judge Biases', fontsize=16, fontweight='bold')

# ============================================================================
# Subplot 1: Self-Preference Bias
# ============================================================================
ax1 = axes[0]

models = ['GPT-4o\njudging\nGPT-4o', 'GPT-4o\njudging\nClaude', 'Claude\njudging\nClaude', 'Claude\njudging\nGPT-4o']
win_rates = [73, 58, 71, 54]  # Judges favor own model
colors = ['#FF6B6B', '#4ECDC4', '#FF6B6B', '#4ECDC4']

bars1 = ax1.bar(models, win_rates, color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)
ax1.axhline(y=50, color='gray', linestyle='--', linewidth=2, label='Expected (no bias): 50%')
ax1.set_ylabel('Approval Rate (%)', fontsize=12, fontweight='bold')
ax1.set_title('Self-Preference Bias', fontsize=14, fontweight='bold')
ax1.set_ylim(0, 100)
ax1.legend(loc='upper right')
ax1.grid(axis='y', alpha=0.3)

# Add value labels on bars
for bar in bars1:
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height + 2,
             f'{int(height)}%', ha='center', va='bottom', fontsize=11, fontweight='bold')

# Add bias magnitude annotation
ax1.text(0.5, 0.95, 'Bias: 14-18pp from baseline',
         transform=ax1.transAxes, ha='center', va='top',
         bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.3),
         fontsize=10)

# ============================================================================
# Subplot 2: Position Bias
# ============================================================================
ax2 = axes[1]

# Simulate position bias data
positions = ['Position A\n(shown first)', 'Position B\n(shown second)']
win_rates_pos = [62, 38]  # Primacy bias (favor first position)

bars2 = ax2.bar(positions, win_rates_pos, color=['#95E1D3', '#F38181'], alpha=0.7, edgecolor='black', linewidth=1.5)
ax2.axhline(y=50, color='gray', linestyle='--', linewidth=2, label='Expected (no bias): 50%')
ax2.set_ylabel('Win Rate (%)', fontsize=12, fontweight='bold')
ax2.set_title('Position Bias (Primacy Effect)', fontsize=14, fontweight='bold')
ax2.set_ylim(0, 100)
ax2.legend(loc='upper right')
ax2.grid(axis='y', alpha=0.3)

# Add value labels on bars
for bar in bars2:
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height + 2,
             f'{int(height)}%', ha='center', va='bottom', fontsize=11, fontweight='bold')

# Add consistency metric
ax2.text(0.5, 0.95, 'Consistency (position swap): 71%\nShould be >90%',
         transform=ax2.transAxes, ha='center', va='top',
         bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.3),
         fontsize=10)

# ============================================================================
# Subplot 3: Verbosity Bias
# ============================================================================
ax3 = axes[2]

# Correlation between response length and judge score
np.random.seed(42)
response_lengths = np.linspace(10, 500, 50)
scores = 2.5 + 0.005 * response_lengths + np.random.normal(0, 0.3, 50)
scores = np.clip(scores, 1, 5)  # Clip to 1-5 range

# Scatter plot
scatter = ax3.scatter(response_lengths, scores, alpha=0.6, s=100, c=scores, cmap='RdYlGn', edgecolors='black')

# Trend line
z = np.polyfit(response_lengths, scores, 1)
p = np.poly1d(z)
ax3.plot(response_lengths, p(response_lengths), "r--", linewidth=2, label=f'Trend: r=0.47 (moderate bias)')

ax3.set_xlabel('Response Length (words)', fontsize=12, fontweight='bold')
ax3.set_ylabel('Judge Score (1-5)', fontsize=12, fontweight='bold')
ax3.set_title('Verbosity Bias', fontsize=14, fontweight='bold')
ax3.set_ylim(0.5, 5.5)
ax3.legend(loc='lower right')
ax3.grid(alpha=0.3)

# Add colorbar
cbar = plt.colorbar(scatter, ax=ax3)
cbar.set_label('Judge Score', rotation=270, labelpad=20, fontsize=10)

# Add annotation
ax3.text(0.5, 0.95, 'Judges favor longer responses\nregardless of quality',
         transform=ax3.transAxes, ha='center', va='top',
         bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.3),
         fontsize=10)

# ============================================================================
# Save figure
# ============================================================================
plt.tight_layout()

output_path = Path(__file__).parent / "judge_bias_patterns.png"
plt.savefig(output_path, dpi=150, bbox_inches='tight')
print(f"✅ Saved: {output_path}")

plt.close()
