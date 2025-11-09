# Homework 4: Tutorial Index

## Overview

Homework 4 focuses on **retrieval evaluation** for RAG (Retrieval-Augmented Generation) systems. You'll build a BM25-based retrieval engine, generate synthetic queries using salient fact extraction, and measure performance using standard information retrieval metrics (Recall@k, MRR). The optional advanced section explores query rewrite agents for retrieval enhancement.

**Learning Time:** ~6-7 hours (basic) + 2-3 hours (optional agent)
**Difficulty:** Intermediate to Advanced
**Prerequisites:** Completion of HW2 (synthetic query generation), HW3 (LLM usage)

---

## Learning Objectives

By completing these tutorials, you will be able to:
- ✅ Understand RAG architecture and when retrieval evaluation matters
- ✅ Implement BM25 retrieval using `rank-bm25` library
- ✅ Generate realistic synthetic queries using salient fact extraction
- ✅ Calculate and interpret Recall@k and MRR metrics
- ✅ Identify query types that work well vs. poorly for retrieval
- ✅ [Optional] Build and evaluate query rewrite agents for retrieval enhancement
- ✅ Analyze bottlenecks in retrieval pipelines
- ✅ Design evaluation datasets that stress-test retrieval systems

---

## Tutorials

### 1. RAG Evaluation Concepts
**File:** `rag_evaluation_concepts.md`
**Reading Time:** 20-25 minutes
**Topics:**
- RAG architecture overview (query → retrieval → generation)
- BM25 intuition: Term frequency and inverse document frequency
- When to evaluate retrieval separately from generation
- Retrieval vs. generation failure modes
- Synthetic vs. organic query evaluation
- Cold-start evaluation strategies

**When to use:** Start here to understand why retrieval evaluation is critical for RAG systems.

---

### 2. Synthetic Query Generation Tutorial (Interactive)
**File:** `synthetic_query_generation_tutorial.ipynb`
**Execution Time:**
- **DEMO MODE** (default): 1-2 minutes | Cost: $0.05-0.15 (10 recipes)
- **FULL MODE**: 3-5 minutes | Cost: $1.50-2.00 (100 recipes)

**Topics:**
- Salient fact extraction from recipe documents
- Two-step LLM prompting: facts → queries for better quality
- Parallel processing with ThreadPoolExecutor (10 workers)
- Automated query quality validation (length, diversity)
- Generating 100+ queries efficiently at scale
- Cost optimization for large-scale generation

**When to use:** After processing recipe data, use this to create your evaluation dataset.

**Interactive Features:**
- Configurable DEMO vs FULL mode for cost control
- Live salient fact extraction with gpt-4o-mini
- Natural language query generation
- Automated quality metrics (diversity rate, avg length)
- Cost estimation calculator
- Export to JSON and CSV for evaluation

**⚠️ Requirements:** API key in `.env`, processed recipes from `scripts/process_recipes.py`

---

### 3. Retrieval Metrics Tutorial
**File:** `retrieval_metrics_tutorial.md`
**Reading Time:** 15-20 minutes
**Topics:**
- **Recall@1:** Target recipe appears as top result
- **Recall@3:** Target recipe in top 3 results
- **Recall@5:** Target recipe in top 5 results
- **MRR (Mean Reciprocal Rank):** Average quality of ranking
- Interpreting metric trade-offs
- Baseline setting and performance expectations
- When to use each metric

**When to use:** Before implementing evaluation, understand what you're measuring.

**Key Formulas:**
```
Recall@k = (# queries with target in top k) / (total queries)

MRR = (1/N) × Σ(1 / rank_i)
  where rank_i = position of target for query i

Example: Target at rank 1 → RR = 1.0
        Target at rank 3 → RR = 0.33
        Target not in top-k → RR = 0.0
```

---

### 4. [Optional Advanced] Query Rewrite Agent Tutorial (Interactive)
**File:** `query_rewrite_agent_tutorial.ipynb`
**Execution Time:** 25-35 minutes
**Topics:**
- Query optimization strategies: keywords, rewrite, expansion
- Building an LLM-powered rewrite agent
- Parallel batch processing for efficiency
- Measuring retrieval improvement
- Strategy comparison and selection
- Cost-benefit analysis of query enhancement

**When to use:** After baseline retrieval evaluation, use this to explore retrieval enhancement.

**Interactive Features:**
- Test 3 rewrite strategies on your queries
- Side-by-side baseline vs. enhanced comparison
- Performance timing and cost tracking
- Query rescue/degradation analysis

**Expected Results:**
- 5-15% Recall@5 improvement
- Keywords strategy: Best for technical queries
- Rewrite strategy: Best overall performance
- Expansion strategy: Helps with sparse matches

---

### 5. RAG Architecture Diagram (Visual)
**File:** `diagrams/rag_architecture.mmd`
**Format:** Mermaid diagram (viewable on GitHub)
**Topics:**
- End-to-end RAG pipeline visualization
- Query → Retrieval → Context → Generation → Response flow
- Where retrieval evaluation fits in the pipeline
- Bottleneck identification points

**When to use:** Reference this to understand how retrieval connects to generation.

---

## Recommended Learning Path

```
┌──────────────────────────────────────────────────────────┐
│         HW4 RAG Retrieval Evaluation Workflow            │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  PART 1: Dataset Preparation                            │
│  ┌────────────────────────────────────────────────────┐ │
│  │ 1. Process recipe data (scripts/process_recipes.py)│ │
│  │    → Creates processed_recipes.json (200 recipes)  │ │
│  │                                                     │ │
│  │ 2. Build BM25 retrieval engine                     │ │
│  │    → Implement backend/retrieval.py                │ │
│  │    → Save index for fast reuse                     │ │
│  │                                                     │ │
│  │ 3. Complete "Synthetic Query Generation" tutorial  │ │
│  │    → Generate 100+ realistic queries               │ │
│  │    → Save to data/synthetic_queries.json           │ │
│  └────────────────────────────────────────────────────┘ │
│                                                          │
│  PART 2: Retrieval Evaluation                           │
│  ┌────────────────────────────────────────────────────┐ │
│  │ 4. Complete "RAG Evaluation Concepts" tutorial     │ │
│  │                                                     │ │
│  │ 5. Complete "Retrieval Metrics" tutorial           │ │
│  │                                                     │ │
│  │ 6. Implement evaluation                            │ │
│  │    → Create scripts/evaluate_retrieval.py          │ │
│  │    → Calculate Recall@1/3/5 and MRR                │ │
│  │    → Save results to JSON                          │ │
│  │                                                     │ │
│  │ 7. Analyze results                                 │ │
│  │    → What query types work well vs. poorly?        │ │
│  │    → Identify retrieval failure patterns           │ │
│  └────────────────────────────────────────────────────┘ │
│                                                          │
│  PART 3: [Optional] Query Enhancement                   │
│  ┌────────────────────────────────────────────────────┐ │
│  │ 8. Complete "Query Rewrite Agent" tutorial         │ │
│  │                                                     │ │
│  │ 9. Implement agent (backend/query_rewrite_agent.py)│ │
│  │    → Keywords extraction                           │ │
│  │    → Query rewriting                               │ │
│  │    → Query expansion                               │ │
│  │                                                     │ │
│  │ 10. Evaluate with agent enhancement                │ │
│  │     → Compare baseline vs. enhanced performance    │ │
│  │     → Identify best strategy                       │ │
│  │     → Analyze query rescue cases                   │ │
│  └────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────┘
```

---

## Key Concepts

### RAG (Retrieval-Augmented Generation)
**RAG** systems combine retrieval with generation to ground LLM responses in factual sources:

1. **Query:** User asks "What air fryer temperature for crispy vegetables?"
2. **Retrieval:** BM25 finds top-5 most relevant recipes
3. **Context:** Retrieved recipes passed to LLM as context
4. **Generation:** LLM generates answer grounded in retrieved recipes

**Why evaluate retrieval separately?**
- Retrieval failures → LLM has no context → guaranteed bad output
- Cheap to evaluate (no LLM calls needed)
- Enables targeted optimization

### BM25 (Best Matching 25)
**BM25** is a probabilistic ranking function:
- **TF (Term Frequency):** How often query terms appear in document
- **IDF (Inverse Document Frequency):** How rare/important query terms are
- **Document length normalization:** Prevents bias toward long documents

**Intuition:**
```
Score = Σ(IDF_term × TF_normalized_term)

High score when:
  - Query terms appear frequently in document (high TF)
  - Query terms are rare across corpus (high IDF)
  - Document length is appropriate (normalization)
```

### Recall@k
**Recall@k** measures what fraction of queries successfully retrieve the target document in the top-k results:

```
Recall@1 = 0.60 → 60% of queries find target as #1 result
Recall@5 = 0.85 → 85% of queries find target in top 5
```

**Typical ranges for well-designed systems:**
- Recall@1: 40-60%
- Recall@3: 60-80%
- Recall@5: 70-90%

### Mean Reciprocal Rank (MRR)
**MRR** measures the average quality of ranking across all queries:

```
MRR = average(1/rank_of_target)

Query 1: Target at rank 1 → RR = 1.0
Query 2: Target at rank 3 → RR = 0.33
Query 3: Target at rank 2 → RR = 0.5
MRR = (1.0 + 0.33 + 0.5) / 3 = 0.61
```

**Interpretation:**
- MRR = 1.0: Perfect (all targets at rank 1)
- MRR = 0.5: Target averages rank 2
- MRR = 0.33: Target averages rank 3

---

## Practical Exercises

After completing the tutorials, try these exercises:

1. **Query Type Analysis**
   - Categorize your queries by type (appliance, timing, technique, ingredient)
   - Calculate Recall@5 for each category separately
   - Identify which types work well vs. poorly
   - Hypothesize why certain types fail

2. **Failure Mode Investigation**
   - Find all queries with Recall@5 = 0 (complete failures)
   - Read the target recipe and the query
   - Identify vocabulary mismatch patterns
   - Propose query rewrite strategies

3. **Salient Fact Quality**
   - Generate salient facts from 10 recipes
   - Rate each fact's usefulness for query generation
   - Identify what makes a "good" salient fact
   - Refine your fact extraction prompt

---

## Common Pitfalls

### Dataset Creation
- ❌ **Too easy:** Queries directly copy recipe titles
- ❌ **Too hard:** Queries require multi-hop reasoning
- ❌ **Unrealistic:** No real user would ask that way
- ❌ **Insufficient diversity:** All queries test same property

### BM25 Implementation
- ❌ **No preprocessing:** Case sensitivity, punctuation issues
- ❌ **Tokenization mismatch:** Splitting "air-fryer" vs. "air fryer"
- ❌ **Index not saved:** Rebuilding index every run is slow
- ❌ **No chunking:** Using entire recipes can dilute relevance

### Evaluation
- ❌ **Only Recall@1:** Missing insight from Recall@5 and MRR
- ❌ **No error analysis:** Not investigating why retrieval fails
- ❌ **Ignoring baseline:** Don't know if 60% Recall@5 is good or bad
- ❌ **Overfitting to evaluation set:** Queries too similar to recipes

### Query Rewrite Agent (Optional)
- ❌ **Over-engineering:** Complex rewrites that hurt performance
- ❌ **No cost analysis:** Spending $5 in LLM calls for 2% improvement
- ❌ **Not measuring latency:** Agent adds 500ms per query
- ❌ **Only testing one strategy:** Keywords might beat rewrite for your use case

---

## Reference Files

### Assignment Materials
- [`README.md`](README.md) - Assignment instructions
- [`hw4_walkthrough.py`](hw4_walkthrough.py) - Marimo notebook walkthrough
- [`data/processed_recipes.json`](data/processed_recipes.json) - 200 longest recipes

### Scripts (You'll Create)
- [`scripts/process_recipes.py`](scripts/process_recipes.py) - Dataset processing
- [`scripts/generate_queries.py`](scripts/generate_queries.py) - Synthetic query generation
- [`scripts/evaluate_retrieval.py`](scripts/evaluate_retrieval.py) - Basic evaluation
- [`scripts/evaluate_retrieval_with_agent.py`](scripts/evaluate_retrieval_with_agent.py) - Agent comparison (optional)

### Backend Code (You'll Create)
- [`backend/retrieval.py`](../../backend/retrieval.py) - BM25 implementation
- [`backend/query_rewrite_agent.py`](../../backend/query_rewrite_agent.py) - Query optimization (optional)

### Video Walkthroughs
- [HW4 Solution Walkthrough](https://youtu.be/GMShL5iC8aY)

---

## Tools & Libraries

**Required:**
- `rank-bm25` - Fast BM25 implementation
- `litellm` - LLM integration for query generation
- `pandas` - Data manipulation
- `concurrent.futures` - Parallel processing

**Optional (for Part 3):**
- `tqdm` - Progress bars for long operations

**Installation:**
```bash
pip install rank-bm25 litellm pandas tqdm
```

---

## Expected Outputs

After completing HW4, you should have:
- ✅ Processed recipe dataset (~200 recipes in JSON)
- ✅ Synthetic query evaluation dataset (100+ queries)
- ✅ BM25 retrieval implementation with saved index
- ✅ Evaluation results with Recall@1/3/5 and MRR
- ✅ Brief analysis (1-2 paragraphs):
  - What query types work well vs. poorly?
  - How would you build an agent around this retriever?
  - Ideas for improving retrieval performance?

**Example Results:**
```
Baseline Retrieval Performance:
  Recall@1: 0.52 (52%)
  Recall@3: 0.71 (71%)
  Recall@5: 0.83 (83%)
  MRR: 0.62

Query Rewrite Agent Performance (Optional):
  Recall@5: 0.91 (91%) [+8% improvement]
  Best strategy: Query Rewriting
  Processing time: 15s for 100 queries
```

---

## Connection to Industry

This assignment mirrors real-world RAG evaluation:
- **E-commerce:** Product search evaluation
- **Customer support:** Knowledge base retrieval
- **Legal tech:** Case law retrieval
- **Healthcare:** Medical literature search

**Key Insight:** Poor retrieval is the #1 cause of RAG system failures. Measure it separately!

---

## Next Steps

After completing HW4, you'll have:
- ✅ RAG evaluation pipeline
- ✅ Synthetic query generation capabilities
- ✅ Understanding of retrieval metrics
- ✅ (Optional) Query enhancement techniques

**Move on to Homework 5** to learn agent failure analysis with transition matrices.

👉 [Homework 5 Tutorial Index](../hw5/TUTORIAL_INDEX.md)

---

## FAQ

**Q: Why use BM25 instead of semantic embeddings?**
A: BM25 is fast, interpretable, and works well for keyword-heavy queries. This assignment focuses on evaluation methodology, which applies to any retriever.

**Q: How many recipes should I process?**
A: The reference uses 200 longest recipes. You can use more, but evaluation gets slower.

**Q: What's a good Recall@5?**
A: For well-formed queries with clear targets: 70-85%. Depends on query difficulty and corpus size.

**Q: Should I do the optional query rewrite agent?**
A: If you have time, yes! It teaches important patterns for RAG enhancement. But not required.

**Q: How do I know if my synthetic queries are realistic?**
A: Read them aloud. Would a real user ask this? Does it require only the target recipe to answer?

**Q: Can I use a different dataset?**
A: Yes, but recipes work well because they have clear structure (ingredients, steps) and realistic query patterns.

---

**Tutorial Status:** ⏳ In Development
**Last Updated:** 2025-10-29
**Maintainer:** AI Evaluation Course Team
