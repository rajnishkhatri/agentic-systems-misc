# Lesson 9: Evaluation Fundamentals & Exact Methods

## Overview

This lesson introduces the foundational principles of LLM evaluation and exact measurement techniques. You'll learn why evaluating foundation models is challenging, how to interpret language modeling metrics, and when to use different similarity measurements.

---

## Prerequisites

- Completion of HW1 and HW2
- Basic understanding of probability and information theory (entropy, cross-entropy)
- Python 3.10+ with Jupyter notebook support
- OpenAI API key (for semantic similarity notebook)

---

## Learning Time

**Total:** ~3-4 hours
- Reading: 50-60 minutes (3 concept tutorials)
- Hands-on: 8 minutes (2 interactive notebooks)
- Exercises: 1-2 hours (optional)

---

## Setup

### 1. Install Dependencies

```bash
# Ensure you're in the project root
pip install -r requirements.txt

# Additional dependencies for Lesson 9
pip install nltk python-Levenshtein
```

### 2. Configure Environment

```bash
# Copy environment template if not already done
cp env.example .env

# Add your OpenAI API key to .env
# Required for semantic similarity notebook
OPENAI_API_KEY=sk-...
```

### 3. Download NLTK Data

```python
# Run in Python or first notebook cell
import nltk
nltk.download('punkt')
nltk.download('wordnet')
```

---

## Cost Estimate

| Notebook | Mode | API Calls | Estimated Cost |
|----------|------|-----------|----------------|
| Perplexity Calculation | N/A | 0 (offline) | $0.00 |
| Similarity Measurements | DEMO | 10 queries × embeddings | $0.20-0.50 |
| Similarity Measurements | FULL | 50 queries × embeddings | $0.80-1.20 |

**Total (DEMO mode):** <$0.50
**Total (FULL mode):** <$1.50

---

## Quick Start

### Recommended Learning Path

1. **Start here:** Read [`TUTORIAL_INDEX.md`](TUTORIAL_INDEX.md) for navigation and learning objectives
2. **Concept tutorials:** Read all 3 markdown tutorials in order:
   - `evaluation_fundamentals.md` (20-25 min)
   - `language_modeling_metrics.md` (15-20 min)
   - `exact_evaluation_methods.md` (20-25 min)
3. **Hands-on practice:** Run both notebooks:
   - `perplexity_calculation_tutorial.ipynb` (<3 min)
   - `similarity_measurements_tutorial.ipynb` (<5 min, requires API key)
4. **Apply learnings:** Complete practical exercises in TUTORIAL_INDEX.md

---

## Files in This Lesson

### Tutorials
- `TUTORIAL_INDEX.md` - Navigation hub
- `evaluation_fundamentals.md` - Challenges of evaluating foundation models
- `language_modeling_metrics.md` - Perplexity, cross-entropy, BPC/BPB
- `exact_evaluation_methods.md` - Exact match, BLEU, semantic similarity

### Notebooks
- `perplexity_calculation_tutorial.ipynb` - Perplexity calculation and contamination detection
- `similarity_measurements_tutorial.ipynb` - Exact, fuzzy, BLEU, semantic similarity

### Data
- `data/sample_perplexity_results.json` - Pre-calculated perplexity values (GPT-2 variants)

### Diagrams
- `diagrams/evaluation_taxonomy.mmd` - Evaluation method decision tree
- `diagrams/embedding_similarity_concept.png` - Cosine similarity visualization (will be generated)

---

## Key Learning Outcomes

After completing this lesson, you will:
- ✅ Understand unique challenges of LLM evaluation (open-ended outputs, benchmark saturation)
- ✅ Interpret perplexity and know when it's misleading
- ✅ Choose appropriate similarity metrics based on task requirements
- ✅ Implement exact match, fuzzy match, BLEU, and semantic similarity
- ✅ Debug evaluation failures using systematic approaches

---

## Testing Your Understanding

### Self-Check Questions

1. When is perplexity a misleading metric for model quality?
2. Why is exact match inappropriate for most natural language evaluation?
3. What's the difference between lexical and semantic similarity?
4. When should you use BLEU vs semantic similarity for recipe bot evaluation?

**Answers:** See FAQ in TUTORIAL_INDEX.md

---

## Next Steps

After completing Lesson 9:
- ✅ **Move to Lesson 10:** Learn AI-as-Judge evaluation patterns
- ✅ **Apply to your project:** Choose appropriate metrics for your evaluation task
- ✅ **Explore dashboard:** See unified metrics across lessons 9-11

👉 [Lesson 10: AI-as-Judge Mastery](../lesson-10/README.md)
👉 [Evaluation Dashboard](../lesson-9-11/README.md)

---

## Troubleshooting

### Common Issues

**"ModuleNotFoundError: No module named 'nltk'"**
```bash
pip install nltk
```

**"OpenAI API key not found"**
```bash
# Ensure .env file exists in project root
# Verify OPENAI_API_KEY is set correctly
cat .env | grep OPENAI_API_KEY
```

**"Resource punkt not found"**
```python
import nltk
nltk.download('punkt')
```

**Notebooks won't execute**
```bash
# Ensure Jupyter is installed
pip install jupyter ipykernel

# Launch Jupyter
jupyter notebook
```

---

## Support

- **Questions?** See FAQ in [TUTORIAL_INDEX.md](TUTORIAL_INDEX.md)
- **Issues?** Check troubleshooting section above
- **Feedback?** Open an issue in the project repository

---

**Last Updated:** 2025-11-09
**Estimated Completion Time:** 3-4 hours
**Difficulty:** Intermediate
