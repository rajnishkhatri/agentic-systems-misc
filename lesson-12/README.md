# Lesson 12: Hybrid Retrieval & Context Quality

> **Learn to build production-grade RAG systems with hybrid search and optimized chunking**

---

## Quick Start

**Total Time:** 3-4 hours | **Cost:** $0.50 (DEMO mode)

### What You'll Build
1. Hybrid retrieval system combining BM25 and semantic search
2. Chunking optimizer comparing 5 strategies (fixed, semantic, contextual)
3. Context quality evaluator using AI judges

### Prerequisites
- Python 3.8+
- OpenAI API key ($5 credit recommended)
- Completed [Lesson 9](../lesson-9/TUTORIAL_INDEX.md) or [HW4](../homeworks/hw4/TUTORIAL_INDEX.md)

---

## 🚀 Quick Start (5 minutes)

```bash
# 1. Install dependencies
pip install openai faiss-cpu rank-bm25 numpy pandas

# 2. Set API key
export OPENAI_API_KEY="your-key-here"

# 3. Navigate to lesson
cd lesson-12

# 4. Run notebooks in DEMO mode (fast, cheap)
export EXECUTION_MODE="DEMO"
jupyter notebook hybrid_search_comparison.ipynb
```

---

## 📚 Learning Path

### Step 1: Understand the Theory (60 min)
Read concept tutorials in this order:

1. [Embedding-Based Retrieval](embedding_based_retrieval.md) - Vector search fundamentals
2. [Hybrid Search Strategies](hybrid_search_strategies.md) - BM25 + semantic fusion
3. [Context Quality Evaluation](context_quality_evaluation.md) - Chunking optimization

### Step 2: Hands-On Practice (90 min)
Run interactive notebooks:

1. [Hybrid Search Comparison](hybrid_search_comparison.ipynb) - Compare 3 retrieval methods
2. [Chunking Optimization](chunking_optimization.ipynb) - Find optimal chunk size

### Step 3: Review & Apply (30 min)
- Study visual diagrams in `diagrams/` folder
- Review your results in `results/` folder
- Apply learnings to your RAG system

---

## 📖 Tutorials Overview

### Concept Tutorials (Markdown)

| Tutorial | Reading Time | Key Learning |
|----------|--------------|--------------|
| [embedding_based_retrieval.md](embedding_based_retrieval.md) | 20 min | Vector embeddings, FAISS indexing, cosine similarity |
| [hybrid_search_strategies.md](hybrid_search_strategies.md) | 18 min | BM25 vs semantic, Reciprocal Rank Fusion (RRF) |
| [context_quality_evaluation.md](context_quality_evaluation.md) | 20 min | Context precision/recall, chunking trade-offs |

### Interactive Notebooks (Jupyter)

| Notebook | Execution Time | Cost | What You'll Build |
|----------|---------------|------|-------------------|
| [hybrid_search_comparison.ipynb](hybrid_search_comparison.ipynb) | 8 min (DEMO) | $0.30 | Compare BM25, semantic, hybrid on recipe dataset |
| [chunking_optimization.ipynb](chunking_optimization.ipynb) | 5 min (DEMO) | $0.20 | Test 5 chunking strategies, find optimal size |

### Visual Diagrams

- **Hybrid Search Architecture** (`diagrams/hybrid_search_architecture.mmd`) - RRF fusion workflow
- **Chunking Strategies** (`diagrams/chunking_strategies_comparison.png`) - Visual comparison
- **Contextual Retrieval** (`diagrams/contextual_retrieval_anthropic.mmd`) - Anthropic's method

---

## 🎯 Learning Objectives

After completing this lesson, you will:

✅ Understand when to use BM25 vs semantic vs hybrid search
✅ Implement Reciprocal Rank Fusion (RRF) for merging rankings
✅ Optimize chunk size for your domain (150, 200, 400 words)
✅ Measure context precision and recall using AI judges
✅ Apply Anthropic's contextual retrieval technique
✅ Diagnose retrieval failures in your RAG system

---

## 💡 Key Concepts

### Hybrid Retrieval
Combine **lexical** (BM25) and **semantic** (embeddings) search:

```python
# BM25: Exact term matching
bm25_results = bm25_index.get_scores(["lasagna", "cheese"])

# Semantic: Conceptual similarity
semantic_results = semantic_search(query_embedding, vector_index, k=5)

# Hybrid: Best of both worlds (alpha=0.5 = equal weight)
hybrid_results = hybrid_search(query, bm25_index, vector_index, alpha=0.5, k=5)
```

**When to use each:**
- **BM25:** Exact matches (product IDs, names, codes)
- **Semantic:** Conceptual queries ("comfort food", "healthy dinner")
- **Hybrid:** Production default (handles all query types)

### Chunking Strategies

| Strategy | Chunk Size | Best For | Trade-off |
|----------|-----------|----------|-----------|
| **Fixed-100** | 100 words | High precision retrieval | May lose context |
| **Fixed-200** | 200 words | **Balanced (recommended)** | General purpose |
| **Fixed-400** | 400 words | QA requiring broad context | Lower precision |
| **Semantic** | Variable | Natural reading flow | Inconsistent sizes |
| **Contextual** | 200 words + metadata | Cross-document retrieval | Higher embedding cost |

**Recommendation:** Start with **200-word fixed chunks with 50-word overlap**.

### Context Quality Metrics

- **Context Precision:** `(# relevant chunks in top-k) / k`
- **Context Recall:** `(# relevant passages retrieved) / (# total relevant)`
- **Diversity:** `(# unique documents in top-k) / k`

---

## 🛠️ Implementation Guide

### Backend Modules

**`backend/semantic_retrieval.py`** - Core retrieval functions:
```python
from backend.semantic_retrieval import (
    generate_embeddings,        # OpenAI embeddings
    build_vector_index,          # FAISS index
    semantic_search,             # Top-k similarity search
    hybrid_search,               # BM25 + semantic fusion
    reciprocal_rank_fusion       # RRF algorithm
)
```

**`backend/context_judges.py`** - AI-based evaluation:
```python
from backend.context_judges import ContextPrecisionJudge, ContextRecallJudge

judge = ContextPrecisionJudge()
result = judge.evaluate(query, retrieved_chunks)
print(f"Precision: {result['precision']:.2f}")
```

### Running Tests

```bash
# Test semantic retrieval module (20 tests)
pytest tests/test_semantic_retrieval.py -v

# Test context judges (14 tests)
pytest tests/test_context_judges.py -v

# Run all Lesson 12 tests
pytest tests/test_semantic_retrieval.py tests/test_context_judges.py -v
```

**Expected:** All 34 tests pass in ~5 seconds.

---

## 📊 Expected Results

### Hybrid Search Comparison (DEMO mode)

**Query:** "creamy pasta with cheese"

| Method | Precision@5 | Top-1 Result |
|--------|-------------|--------------|
| BM25 | 0.80 | "5 cheese crab lasagna..." |
| Semantic | 0.60 | "Alfredo pasta recipe..." |
| **Hybrid** | **1.00** | "5 cheese crab lasagna..." |

**Insight:** Hybrid excels by combining BM25's exact match ("cheese") with semantic's conceptual understanding ("creamy").

### Chunking Optimization (DEMO mode)

| Strategy | Avg Precision | Avg Diversity | Notes |
|----------|--------------|---------------|-------|
| Fixed-100 | 0.72 | 0.40 | Too granular, low diversity |
| **Fixed-200** | **0.85** | **0.68** | **Best balance** |
| Fixed-400 | 0.78 | 0.82 | Loses precision, but high diversity |
| Semantic-300 | 0.83 | 0.70 | Variable chunk sizes |
| Contextual-200 | 0.88 | 0.72 | +3% precision from metadata |

**Recommendation:** Use **Fixed-200** or **Contextual-200** for production.

---

## 🚨 Common Issues

### Issue 1: "OpenAI API key not found"
**Solution:**
```bash
export OPENAI_API_KEY="sk-..."
# Or create .env file:
echo "OPENAI_API_KEY=sk-..." > .env
```

### Issue 2: "FAISS import error"
**Solution:**
```bash
# For CPU-only systems:
pip install faiss-cpu

# For GPU systems:
pip install faiss-gpu
```

### Issue 3: Notebooks run too slowly (>10 min)
**Solution:** Use DEMO mode for quick testing:
```python
MODE = "DEMO"  # In notebook cell 1
# Or set environment variable:
export EXECUTION_MODE="DEMO"
```

### Issue 4: Low precision scores (<0.5)
**Causes:**
- Query-document mismatch (e.g., searching recipes for legal terms)
- Chunk size too large (includes irrelevant content)
- Need more data (DEMO uses only 50 documents)

**Solution:** Run FULL mode with 200+ documents, tune chunk size to 150-200 words.

---

## 💰 Cost Breakdown

### DEMO Mode (Recommended for Learning)
- **Hybrid Search Notebook:** $0.30 (50 docs, 3 queries)
- **Chunking Notebook:** $0.20 (30 docs, 3 strategies)
- **Total:** $0.50

### FULL Mode (Comprehensive Evaluation)
- **Hybrid Search Notebook:** $1.50 (200 docs, 6 queries)
- **Chunking Notebook:** $1.00 (100 docs, 5 strategies)
- **Total:** $2.50

**Model:** `text-embedding-3-small` ($0.02 per 1M tokens)

---

## 🎓 Exercises

### Exercise 1: Tune Alpha Parameter (20 min)
**Goal:** Find optimal BM25/semantic weight for your domain

1. Modify `hybrid_search_comparison.ipynb`
2. Test alpha ∈ {0.3, 0.5, 0.7}
3. Plot precision vs alpha
4. Identify best alpha for your query types

**Expected:** Exact-match queries favor higher alpha (0.7), semantic queries favor lower alpha (0.3).

### Exercise 2: Implement Recursive Chunking (30 min)
**Goal:** Handle hierarchical documents (sections → paragraphs)

1. Load a long document (e.g., Bhagavad Gita chapter)
2. Split by sections (### headers), then paragraphs
3. Compare precision with fixed-size chunking
4. Measure context preservation

**Hint:** Use regex to detect section boundaries.

### Exercise 3: Query Type Classifier (45 min)
**Goal:** Route queries to optimal retrieval method

1. Label 50 queries as "exact", "semantic", or "mixed"
2. Extract features: keyword count, named entities, query length
3. Train logistic regression classifier
4. Predict optimal method for new queries

**Expected Accuracy:** 75-85% on held-out test set.

---

## 📈 Next Steps

### After Completing Lesson 12

1. **Lesson 13: RAG Generation & Attribution** ([TUTORIAL_INDEX](../lesson-13/TUTORIAL_INDEX.md))
   - Evaluate answer quality, not just retrieval
   - Detect hallucinations with AI judges
   - Measure context utilization

2. **Lesson 14: Agent Planning & Orchestration** ([TUTORIAL_INDEX](../lesson-14/TUTORIAL_INDEX.md))
   - Apply retrieval optimization to multi-agent systems
   - Plan validation and tool call accuracy

3. **Evaluation Dashboard**
   ```bash
   python lesson-9-11/evaluation_dashboard.py
   # View results from Lessons 9-12
   ```

4. **Advanced Topics**
   - Query expansion with LLMs
   - Re-ranking with cross-encoders
   - Anthropic's Contextual Retrieval [paper](https://www.anthropic.com/news/contextual-retrieval)

---

## 📚 Additional Resources

### Papers
- [Reciprocal Rank Fusion (RRF)](https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf) - Original RRF paper
- [Anthropic Contextual Retrieval](https://www.anthropic.com/news/contextual-retrieval) - Chunk augmentation technique

### Code Examples
- [LangChain RecursiveCharacterTextSplitter](https://python.langchain.com/docs/modules/data_connection/document_transformers/text_splitters/recursive_text_splitter) - Advanced chunking
- [HW4 RAG Implementation](../homeworks/hw4/) - Production RAG patterns

### Tools
- [FAISS Documentation](https://github.com/facebookresearch/faiss) - Vector indexing
- [rank-bm25 Library](https://github.com/dorianbrown/rank_bm25) - BM25 implementation

---

## 🤝 Contributing

Found an issue or have suggestions?

1. Check existing issues in repository
2. Open a new issue with:
   - Tutorial name (e.g., "Lesson 12: Hybrid Search")
   - Problem description
   - Expected vs actual behavior
   - Environment (Python version, OS)

---

## 📝 Changelog

**2025-11-11:** Initial release
- 3 concept tutorials (60 min reading time)
- 2 interactive notebooks (13 min execution time)
- 3 visual diagrams
- 34 unit tests (100% pass rate)
- Full DEMO/FULL mode support

---

**Questions?** See [TUTORIAL_INDEX.md](TUTORIAL_INDEX.md) for comprehensive FAQ and troubleshooting.

**Ready to start?** Open [hybrid_search_comparison.ipynb](hybrid_search_comparison.ipynb) and run your first hybrid search experiment!
