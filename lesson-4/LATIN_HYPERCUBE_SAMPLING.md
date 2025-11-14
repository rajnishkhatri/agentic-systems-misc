# Latin Hypercube Sampling (LHS) Explained

## Overview

**Latin Hypercube Sampling (LHS)** is a statistical sampling method used to efficiently explore high-dimensional parameter spaces. It's particularly valuable when you need to test or optimize systems with many dimensions but can only afford a limited number of samples.

## The Core Idea

Imagine you have a multi-dimensional space (like a hypercube) and you want to choose sample points that:
1. **Spread evenly** across each dimension
2. **Avoid clustering** (no two samples too close together)
3. **Cover all dimensions** with minimal samples

LHS achieves this by ensuring each dimension value (or sub-interval) is represented exactly once before any value is repeated.

## Why "Latin Hypercube"?

The name comes from combining two concepts:
- **Latin Square**: A mathematical grid where each row and column contains each symbol exactly once (like a Sudoku puzzle)
- **Hypercube**: A generalization to N dimensions

LHS extends the Latin Square concept to N dimensions.

## Visual Intuition (2D Example)

Consider a 2D space (e.g., X and Y axes) where you want to place 5 samples:

### Random Sampling (Poor Coverage)
```
Y
│  ●     ●
│
│           ●
│
│●              ●
│
└──────────────── X
```
Problems: May cluster, gaps in coverage, some values over-represented.

### Grid Sampling (Better, but Limited)
```
Y
│  ●  ●  ●
│  ●  ●  ●
│  ●  ●  ●
└───────────── X
```
Problems: Requires N² samples for N intervals per dimension (expensive in high dimensions).

### Latin Hypercube Sampling (Optimal Balance)
```
Y
│     ●
│  ●
│           ●
│     ●
│              ●
└──────────────── X
```
Benefits: Each row and column has exactly one point, maximum spread with only 5 samples.

## How It Works: Step-by-Step Algorithm

For **N samples** across **D dimensions**:

### Step 1: Divide Each Dimension
Split each dimension into N equal intervals:
- Dimension 1: `[0, 0.2), [0.2, 0.4), [0.4, 0.6), [0.6, 0.8), [0.8, 1.0)`
- Dimension 2: `[0, 0.2), [0.2, 0.4), [0.4, 0.6), [0.6, 0.8), [0.8, 1.0)`
- ... and so on for all D dimensions

### Step 2: Create Permutation Matrix
For each dimension, create a random permutation of `[1, 2, 3, ..., N]`

Example with N=5, D=3:
```
Dimension 1: [3, 1, 5, 2, 4]  ← random permutation
Dimension 2: [2, 4, 1, 5, 3]  ← random permutation  
Dimension 3: [4, 2, 5, 3, 1]  ← random permutation
```

### Step 3: Assign Sample Points
For sample i:
- Dimension 1: Pick a random value from interval `permutation_dim1[i]`
- Dimension 2: Pick a random value from interval `permutation_dim2[i]`
- Dimension 3: Pick a random value from interval `permutation_dim3[i]`
- ... and so on

This ensures:
- Each interval in each dimension is used exactly once
- No interval is repeated until all are used

### Step 4: Map to Discrete Values (for Categorical Dimensions)

For categorical dimensions (like "Vegan", "Italian", "Quick"):
1. Map categories to numbers: `{"Vegan": 1, "Vegetarian": 2, "Keto": 3, ...}`
2. Apply LHS on the numeric mapping
3. Map back to categories

## Python Implementation Example

```python
import numpy as np
from scipy.stats import qmc

def latin_hypercube_sampling(n_samples, n_dims, bounds):
    """
    Generate LHS samples.
    
    Args:
        n_samples: Number of samples to generate
        n_dims: Number of dimensions
        bounds: List of (min, max) tuples for each dimension
        
    Returns:
        Array of shape (n_samples, n_dims)
    """
    sampler = qmc.LatinHypercube(d=n_dims)
    samples = sampler.random(n=n_samples)
    
    # Scale samples to bounds
    scaled = np.zeros_like(samples)
    for i, (low, high) in enumerate(bounds):
        scaled[:, i] = samples[:, i] * (high - low) + low
    
    return scaled

# Example: 10 samples across 2 dimensions [0, 1] x [0, 1]
samples = latin_hypercube_sampling(
    n_samples=10,
    n_dims=2,
    bounds=[(0, 1), (0, 1)]
)
```

## Application: Query Diversity in Test Generation

In the context of test query generation (as used in this codebase), LHS helps when you have many dimensions:

### Dimensions Example:
- **Dietary restrictions**: Vegan, Vegetarian, Keto, Gluten-free, ...
- **Meal types**: Breakfast, Lunch, Dinner, Snack, ...
- **Time constraints**: Quick, Moderate, Standard, Long
- **Cuisine types**: Italian, Mexican, Indian, Thai, ...
- **Query styles**: Natural, Detailed, Short, Ingredient-based

### Challenge:
With 5 dimensions, each with 5-7 possible values, the full combinatorial space is **5×7×4×8×4 = 4,480 combinations**!

Testing all would be:
- **Time-consuming**: 4,480 queries to generate and test
- **Expensive**: If using API calls, very costly
- **Unnecessary**: Many combinations test similar behaviors

### LHS Solution:
Generate **10-20 samples** using LHS that:
- ✅ Cover each dimension value at least once
- ✅ Avoid over-representing any combination
- ✅ Provide diverse coverage with minimal queries

### Example Output (10 queries covering 5 dimensions):

| Query | Dietary | Meal Type | Time | Cuisine | Style |
|-------|---------|-----------|------|---------|-------|
| 1 | Vegan | Breakfast | Quick | Mediterranean | Natural |
| 2 | Vegetarian | Lunch | Moderate | Indian | Detailed |
| 3 | Gluten-free | Dinner | Standard | Italian | Ingredient |
| 4 | Keto | Snack | Quick | American | Short |
| 5 | Paleo | Dessert | Long | Mexican | Natural |
| 6 | None | Appetizer | Moderate | Thai | Detailed |
| 7 | Nut-free | Breakfast | Standard | Chinese | Natural |
| 8 | Vegan | Dinner | Quick | Indian | Short |
| 9 | Vegetarian | Lunch | Long | Italian | Ingredient |
| 10 | Gluten-free | Snack | Moderate | Mediterranean | Natural |

**Notice**:
- Each dietary restriction appears 1-2 times (balanced)
- Each meal type is represented
- Varied time constraints
- Diverse cuisines
- Different query styles

## Advantages of LHS

### 1. **Efficient Coverage**
- Requires only **N samples** to cover N intervals per dimension
- Compared to grid sampling which needs N^D samples

### 2. **Stratification**
- Guarantees each dimension sub-interval is sampled exactly once
- Prevents gaps and clustering

### 3. **Scalability**
- Works well for high-dimensional spaces (10+ dimensions)
- Random sampling struggles in high dimensions (curse of dimensionality)

### 4. **Reproducibility**
- Can be made deterministic with fixed random seed
- Useful for reproducible experiments

### 5. **Better than Random**
- More uniform coverage than purely random sampling
- Fewer samples needed for same quality of exploration

## Limitations

### 1. **Requires Fixed N**
- Must decide sample size upfront
- Adding samples later doesn't maintain LHS properties

### 2. **Categorical Dimensions**
- Needs careful mapping for categorical variables
- May need to handle ordinal vs. nominal differently

### 3. **No Guarantee of Optimal Spread**
- Only ensures stratification, not optimal point distribution
- For optimal spread, use **Maximin LHS** or **Optimal LHS**

### 4. **Correlation Structure**
- Doesn't account for correlations between dimensions
- If dimensions are correlated, may not capture well

## Variants and Improvements

### 1. **Maximin LHS**
Maximizes the minimum distance between sample points:
```python
from scipy.stats import qmc
sampler = qmc.LatinHypercube(d=2, optimization='maximin')
samples = sampler.random(n=10)
```

### 2. **Optimal LHS**
Uses optimization algorithms to find LHS with best space-filling properties.

### 3. **Symmetric LHS**
Ensures symmetry in the sample distribution (useful for symmetric problems).

### 4. **Correlation-Based LHS**
Accounts for known correlations between dimensions.

## Comparison to Other Sampling Methods

| Method | Samples for N intervals | Good for High Dim? | Guaranteed Coverage? |
|--------|----------------------|-------------------|---------------------|
| **Random** | Many (no guarantee) | ❌ Poor | ❌ No |
| **Grid** | N^D | ❌ Exponential | ✅ Yes, but expensive |
| **LHS** | **N** | ✅ Excellent | ✅ Yes |
| **Sobol Sequence** | N | ✅ Excellent | ✅ Yes (better than LHS) |
| **Halton Sequence** | N | ✅ Good | ✅ Yes |

### When to Use LHS vs. Other Methods:

- **Use LHS** when:
  - You have 5-20 dimensions
  - You need ~10-100 samples
  - Dimensions are independent or weakly correlated
  - You want simple, straightforward stratification

- **Use Sobol Sequences** when:
  - You need very high-quality space-filling
  - You can afford slightly more computational complexity
  - You're doing numerical integration or optimization

- **Use Random** when:
  - You need a very large number of samples
  - You're doing Monte Carlo simulation
  - Structure doesn't matter

## Practical Implementation Tips

### For Test Query Generation:

1. **Map Categories to Numbers**
   ```python
   dietary_mapping = {
       0: "vegan", 1: "vegetarian", 2: "keto", 
       3: "gluten-free", 4: "none"
   }
   ```

2. **Apply LHS**
   ```python
   n_samples = 15
   n_dims = len(dimensions)
   lhs_samples = latin_hypercube_sampling(n_samples, n_dims, bounds)
   ```

3. **Map Back to Categories**
   ```python
   for sample in lhs_samples:
       dietary = dietary_mapping[int(sample[0] * len(dietary_mapping))]
       meal_type = meal_mapping[int(sample[1] * len(meal_mapping))]
       # ... etc
   ```

4. **Validate Coverage**
   ```python
   # Check each dimension value appears at least once
   for dim_name, dim_values in dimensions.items():
       assert all(any(s[dim_idx] == val for s in samples) 
                  for val in dim_values)
   ```

## Further Reading

- **Wikipedia**: [Latin Hypercube Sampling](https://en.wikipedia.org/wiki/Latin_hypercube_sampling)
- **Scipy Documentation**: [Quasi-Monte Carlo](https://docs.scipy.org/doc/scipy/reference/stats.qmc.html)
- **Original Paper**: McKay, M. D., Beckman, R. J., & Conover, W. J. (1979). "A Comparison of Three Methods for Selecting Values of Input Variables in the Analysis of Output from a Computer Code." Technometrics, 21(2), 239-245.

## Summary

Latin Hypercube Sampling is a powerful technique for:
- ✅ **Efficiently exploring** high-dimensional parameter spaces
- ✅ **Generating diverse test cases** when you have many dimensions
- ✅ **Ensuring coverage** of each dimension with minimal samples
- ✅ **Avoiding clustering** and ensuring uniform distribution

For test query generation, it's particularly useful when you have multiple dimensions (dietary, meal type, cuisine, etc.) and want to create a small but diverse set of test queries that comprehensively cover the space.

















