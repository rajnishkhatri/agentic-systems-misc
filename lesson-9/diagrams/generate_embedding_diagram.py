"""Generate visualization for embedding similarity concept.

Creates a 2D projection showing how semantic similarity works with cosine distance.
"""

import matplotlib.pyplot as plt
import numpy as np

# Set style
plt.style.use("seaborn-v0_8-darkgrid")

# Create figure
fig, ax = plt.subplots(figsize=(10, 8))

# Define example embeddings (2D for visualization)
embeddings = {
    "chocolate cookies": np.array([0.8, 0.6]),
    "sugar cookies": np.array([0.85, 0.55]),
    "oatmeal cookies": np.array([0.75, 0.65]),
    "chicken soup": np.array([0.2, 0.9]),
    "vegetable soup": np.array([0.15, 0.85]),
    "pasta carbonara": np.array([0.5, 0.3]),
}

# Plot embeddings
colors = ["#FF6B6B", "#FF6B6B", "#FF6B6B", "#4ECDC4", "#4ECDC4", "#95E1D3"]
for (name, vec), color in zip(embeddings.items(), colors):
    ax.arrow(
        0, 0, vec[0], vec[1], head_width=0.05, head_length=0.05, fc=color, ec=color, linewidth=2, alpha=0.7, label=name
    )
    ax.text(vec[0] * 1.1, vec[1] * 1.1, name, fontsize=11, ha="center", weight="bold")

# Draw similarity arc between "chocolate cookies" and "sugar cookies"
vec1 = embeddings["chocolate cookies"]
vec2 = embeddings["sugar cookies"]
angle1 = np.arctan2(vec1[1], vec1[0])
angle2 = np.arctan2(vec2[1], vec2[0])
angles = np.linspace(angle1, angle2, 50)
arc_radius = 0.3
arc_x = arc_radius * np.cos(angles)
arc_y = arc_radius * np.sin(angles)
ax.plot(arc_x, arc_y, "k--", linewidth=2, alpha=0.5)

# Add cosine similarity formula
ax.text(
    0.5,
    -0.15,
    r"$\mathrm{cosine\ similarity}(A, B) = \frac{A \cdot B}{||A|| \cdot ||B||}$",
    fontsize=14,
    ha="center",
    bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5),
)

# Add example calculation
ax.text(
    0.5,
    -0.3,
    'Example: similarity("chocolate cookies", "sugar cookies") ≈ 0.97\n'
    'Example: similarity("chocolate cookies", "chicken soup") ≈ 0.62',
    fontsize=10,
    ha="center",
    style="italic",
    bbox=dict(boxstyle="round", facecolor="lightblue", alpha=0.3),
)

# Configure axes
ax.set_xlim(-0.1, 1.0)
ax.set_ylim(-0.4, 1.0)
ax.set_xlabel("Embedding Dimension 1", fontsize=12)
ax.set_ylabel("Embedding Dimension 2", fontsize=12)
ax.set_title("Semantic Similarity via Cosine Distance\n(2D Projection of Embeddings)", fontsize=14, weight="bold")
ax.grid(True, alpha=0.3)
ax.axhline(y=0, color="k", linewidth=0.5, alpha=0.3)
ax.axvline(x=0, color="k", linewidth=0.5, alpha=0.3)

# Add legend
ax.legend(loc="upper right", framealpha=0.9, fontsize=9)

# Add annotations
ax.annotate(
    "High similarity\n(small angle)",
    xy=(0.4, 0.25),
    xytext=(0.3, 0.15),
    arrowprops=dict(arrowstyle="->", color="black", lw=1.5),
    fontsize=10,
    ha="center",
)

ax.annotate(
    "Low similarity\n(large angle)",
    xy=(0.5, 0.6),
    xytext=(0.2, 0.5),
    arrowprops=dict(arrowstyle="->", color="black", lw=1.5),
    fontsize=10,
    ha="center",
)

# Save figure
plt.tight_layout()
plt.savefig("lesson-9/diagrams/embedding_similarity_concept.png", dpi=150, bbox_inches="tight")
print("✓ Generated embedding_similarity_concept.png")
