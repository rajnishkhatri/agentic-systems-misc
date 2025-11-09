# Lesson 11: Comparative Evaluation & Leaderboards

## Overview

This lesson covers comparative evaluation methodologies and leaderboard ranking systems for LLM evaluation. You'll learn when comparative evaluation outperforms pointwise scoring, how to implement ranking algorithms, and how to build robust model leaderboards.

---

## Prerequisites

- Completion of Lesson 10
- Basic understanding of probability and statistics
- Python 3.10+ with Jupyter notebook support
- **No API key required** - all notebooks use simulation-based data

---

## Learning Time

**Total:** ~3-4 hours
- Reading: 20-25 minutes (1 comprehensive guide)
- Hands-on: 12 minutes (3 interactive notebooks)
- Exercises: 2-3 hours (optional)

---

## Setup

### 1. Install Dependencies

```bash
# Ensure you're in the project root
pip install -r requirements.txt

# Verify statistical packages
python -c "import scipy; import numpy; print('Statistical packages installed')"
```

### 2. No API Keys Required!

All notebooks in this lesson use **simulation-based data** or **pre-generated comparisons**. No OpenAI API calls needed.

```bash
# Verify dataset exists
ls -lh lesson-11/data/pairwise_comparisons.json
```

### 3. Optional: Generate Fresh Comparisons

If you want to generate new pairwise comparisons (requires OpenAI API key):

```bash
# Run comparison generation script
python lesson-11/scripts/generate_pairwise_comparisons.py --num_comparisons 100 --output lesson-11/data/pairwise_comparisons.json
```

---

## Cost Estimate

| Notebook | API Calls | Estimated Cost |
|----------|-----------|----------------|
| Elo Ranking | 0 (simulation) | $0.00 |
| Bradley-Terry Ranking | 0 (simulation) | $0.00 |
| A/B Testing vs Comparative | 0 (simulation) | $0.00 |

**Total:** $0.00 ✨

**Optional:** Generating new comparisons with `generate_pairwise_comparisons.py`:
- 100 comparisons × GPT-4o: ~$2.00-3.00
- 100 comparisons × GPT-4o-mini: ~$0.30-0.50

---

## Quick Start

### Recommended Learning Path

1. **Start here:** Read [`TUTORIAL_INDEX.md`](TUTORIAL_INDEX.md) for navigation and learning objectives
2. **Concept tutorial:** Read `comparative_evaluation_guide.md` (20-25 min)
3. **Hands-on practice:** Run all 3 notebooks (no API keys needed):
   - `elo_ranking_tutorial.ipynb` (<5 min)
   - `bradley_terry_ranking_tutorial.ipynb` (<4 min)
   - `ab_testing_vs_comparative_eval.ipynb` (<3 min)
4. **Apply learnings:** Generate pairwise comparisons for your models
5. **Build leaderboard:** Implement Elo or Bradley-Terry ranking for your use case

---

## Files in This Lesson

### Tutorials
- `TUTORIAL_INDEX.md` - Navigation hub
- `comparative_evaluation_guide.md` - Comprehensive guide to comparative evaluation

### Notebooks
- `elo_ranking_tutorial.ipynb` - Elo algorithm implementation and leaderboard visualization
- `bradley_terry_ranking_tutorial.ipynb` - Bradley-Terry model with MLE estimation
- `ab_testing_vs_comparative_eval.ipynb` - Sample efficiency comparison

### Data
- `data/pairwise_comparisons.json` - 100 pre-generated pairwise comparisons (4 dimensions)

### Scripts
- `scripts/generate_pairwise_comparisons.py` - Generate new comparison datasets

### Diagrams
- `diagrams/ranking_algorithm_comparison.mmd` - Algorithm decision flowchart (will be generated)
- `diagrams/comparative_eval_workflow.png` - End-to-end pipeline (will be generated)

---

## Key Learning Outcomes

After completing this lesson, you will:
- ✅ Understand when comparative evaluation is more reliable than pointwise
- ✅ Implement Elo ranking algorithm for dynamic leaderboards
- ✅ Implement Bradley-Terry model for static ranking analysis
- ✅ Analyze transitivity violations in pairwise comparisons
- ✅ Compare A/B testing vs comparative evaluation for sample efficiency
- ✅ Generate high-quality pairwise comparison datasets

---

## Pairwise Comparison Dataset

### Pre-Generated Dataset

This lesson includes **100 pairwise comparisons** in `data/pairwise_comparisons.json`:

**Format:**
```json
{
  "query": "How do I make gluten-free pasta from scratch?",
  "response_a": "Mix rice flour with xanthan gum...",
  "response_b": "Use store-bought gluten-free flour blend...",
  "winner": "A",
  "rationale": "Response A provides more detailed ingredient ratios and addresses common pitfalls.",
  "dimension": "helpfulness"
}
```

**Dimensions:**
- **Helpfulness:** 30 comparisons
- **Correctness:** 30 comparisons
- **Conciseness:** 20 comparisons
- **Safety:** 20 comparisons

**Models compared:**
- Model A: GPT-4o with detailed prompts
- Model B: GPT-4o-mini with concise prompts
- Model C: GPT-3.5-turbo baseline

### Generating Your Own Comparisons

```bash
# Generate 50 comparisons for your models
python lesson-11/scripts/generate_pairwise_comparisons.py \
  --num_comparisons 50 \
  --dimension helpfulness \
  --output my_comparisons.json \
  --model gpt-4o-mini
```

---

## Ranking Algorithms Quick Reference

### Elo Rating

**Best for:** Dynamic leaderboards with continuous updates (e.g., Chatbot Arena)

**Formula:**
```python
expected_score = 1 / (1 + 10**((rating_b - rating_a) / 400))
new_rating = rating_a + K * (actual_score - expected_score)
```

**Pros:** Simple, online updates, well-understood
**Cons:** Order-dependent, requires K-factor tuning

---

### Bradley-Terry Model

**Best for:** Static analysis of fixed model set

**Formula:**
```python
P(A beats B) = exp(skill_a) / (exp(skill_a) + exp(skill_b))
# Skills estimated via maximum likelihood
```

**Pros:** Order-independent, uncertainty estimates, statistically principled
**Cons:** Batch-only (no incremental updates), more complex

---

## Testing Your Understanding

### Self-Check Questions

1. Why does comparative evaluation require fewer samples than A/B testing for the same statistical power?
2. When should you use Elo vs Bradley-Terry?
3. What does it mean if 15% of comparison triplets violate transitivity?
4. How do you choose the K-factor in Elo ranking?

**Answers:** See FAQ in TUTORIAL_INDEX.md

---

## Real-World Examples

### Chatbot Arena
- **URL:** https://chat.lmsys.org/?leaderboard
- **Method:** Elo ranking from 100K+ human votes
- **Models:** 50+ LLMs compared side-by-side
- **Update frequency:** Continuous (live leaderboard)

### AlpacaEval
- **URL:** https://tatsu-lab.github.io/alpaca_eval/
- **Method:** Win-rate calculation with GPT-4 judge
- **Models:** 100+ instruction-following models
- **Focus:** Single-turn instruction following

### Open LLM Leaderboard
- **URL:** https://huggingface.co/spaces/HuggingFaceH4/open_llm_leaderboard
- **Method:** Pointwise benchmarks (MMLU, HellaSwag, etc.)
- **Note:** Not comparative - included for contrast

---

## Next Steps

After completing Lesson 11:
- ✅ **Explore Dashboard:** View unified metrics across Lessons 9-11
- ✅ **Build your leaderboard:** Implement Elo or Bradley-Terry for your models
- ✅ **Generate comparisons:** Create pairwise datasets for your evaluation tasks
- ✅ **Analyze transitivity:** Investigate cycles in your comparison data

👉 [Evaluation Dashboard](../lesson-9-11/README.md)
👉 [Back to Lesson 9](../lesson-9/README.md)
👉 [Back to Lesson 10](../lesson-10/README.md)

---

## Troubleshooting

### Common Issues

**"FileNotFoundError: pairwise_comparisons.json"**
```bash
# Verify file exists
ls -lh lesson-11/data/pairwise_comparisons.json

# If missing, generate it
python lesson-11/scripts/generate_pairwise_comparisons.py
```

**"Elo ratings converge slowly"**
```python
# Increase K-factor for faster convergence
elo = EloRanking(initial_rating=1500, k_factor=64)  # Default is 32
```

**"Bradley-Terry model doesn't converge"**
```python
# Check for disconnected components (models never compared)
# Add comparisons to connect all models
# Or fit separate models for each component
```

**"High transitivity violation rate (>15%)"**
- Check for ties that were forced to wins/losses
- Investigate query-dependent preferences (some models better on certain topics)
- Re-evaluate suspicious triplets manually
- Consider using TrueSkill instead (handles uncertainty better)

**"Elo ratings unstable"**
- Reduce K-factor for established models
- Require minimum comparisons (20-30) before displaying ratings
- Add confidence intervals to communicate uncertainty

---

## Support

- **Questions?** See FAQ in [TUTORIAL_INDEX.md](TUTORIAL_INDEX.md)
- **Issues?** Check troubleshooting section above
- **Dataset issues?** Regenerate comparisons with `generate_pairwise_comparisons.py`
- **Feedback?** Open an issue in the project repository

---

## 💡 Key Insights

1. **Comparative evaluation is ~3x more sample-efficient than A/B testing** for detecting win-rate differences
2. **Elo for dynamic, Bradley-Terry for static** ranking scenarios
3. **Some transitivity violations are expected** (<10% is normal due to noise)
4. **Pairwise comparisons scale as O(n²)** - be strategic about which pairs to compare
5. **Position bias is real** - always evaluate both orderings and aggregate

---

**Last Updated:** 2025-11-09
**Estimated Completion Time:** 3-4 hours
**Difficulty:** Intermediate
**Cost:** $0.00 (simulation-based)
