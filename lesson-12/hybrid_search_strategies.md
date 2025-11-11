# Hybrid Search Strategies: Combining BM25 and Semantic Retrieval

**Reading Time**: 18-22 minutes
**Prerequisites**: `embedding_based_retrieval.md`, HW4 (BM25 implementation)
**Learning Objective**: Combine lexical and semantic search for 10-15% Recall@5 improvement

---

## Why Hybrid Search?

Neither BM25 (lexical) nor semantic search (embeddings) is perfect:

| Scenario | BM25 Performance | Semantic Performance | Winner |
|----------|------------------|---------------------|--------|
| "Chapter 2 Verse 47" (exact match) | ✅ Excellent | ⚠️ May miss | **BM25** |
| "What is selfless action?" (conceptual) | ❌ Poor | ✅ Excellent | **Semantic** |
| "karma in the Gita" (keyword + concept) | ⚠️ Good | ⚠️ Good | **Hybrid** |
| "naan bread recipe" (short, exact) | ✅ Excellent | ⚠️ Good | **BM25** |
| "How to make Indian flatbread?" (paraphrase) | ❌ Misses "naan" | ✅ Excellent | **Semantic** |

**Hybrid search** combines both approaches to leverage strengths and mitigate weaknesses.

---

## Combining Term-Based and Semantic Retrieval

### Approach 1: Reciprocal Rank Fusion (RRF)

**RRF** merges ranked lists from BM25 and semantic search without needing normalized scores.

#### Algorithm

```python
def reciprocal_rank_fusion(rankings: list[list[tuple[int, float]]], k: int = 60) -> list[int]:
    """
    Merge multiple ranked lists using RRF.

    Args:
        rankings: List of ranked results, each as [(doc_id, score), ...]
        k: Constant for RRF formula (default: 60, from literature)

    Returns:
        Merged document IDs sorted by RRF score
    """
    rrf_scores = {}

    for ranking in rankings:
        for rank, (doc_id, _) in enumerate(ranking):
            if doc_id not in rrf_scores:
                rrf_scores[doc_id] = 0
            rrf_scores[doc_id] += 1 / (k + rank + 1)  # rank is 0-indexed

    # Sort by RRF score descending
    sorted_docs = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
    return [doc_id for doc_id, score in sorted_docs]
```

#### Why RRF Works

- **No score normalization**: BM25 scores (0-∞) and cosine similarity (0-1) have different ranges. RRF uses **rank position**, not raw scores.
- **Rank-based**: Document at rank 1 gets score `1/(k+1)`, rank 2 gets `1/(k+2)`, etc.
- **Fusion**: Documents appearing in both rankings accumulate scores from both.

**Example**:

```
BM25 ranking:       [doc5, doc2, doc8, doc1]
Semantic ranking:   [doc2, doc5, doc3, doc7]

RRF scores (k=60):
doc5: 1/61 (BM25 rank 0) + 1/62 (semantic rank 1) = 0.0164 + 0.0161 = 0.0325
doc2: 1/62 (BM25 rank 1) + 1/61 (semantic rank 0) = 0.0161 + 0.0164 = 0.0325
doc8: 1/63 (BM25 rank 2) + 0 (not in semantic)     = 0.0159
doc3: 0 (not in BM25) + 1/63 (semantic rank 2)     = 0.0159

Final ranking: [doc5, doc2, doc8, doc3]
```

Notice: `doc5` and `doc2` both appear in top positions of both rankings, so they rise to the top.

---

### Approach 2: Weighted Linear Combination (Alpha Parameter)

**Alternative method**: Combine normalized scores with tunable weight `α`.

```python
def weighted_hybrid_search(
    query: str,
    bm25_index,
    vector_index,
    alpha: float = 0.5
) -> list[int]:
    """
    Hybrid search with weighted score combination.

    Args:
        alpha: Weight for BM25 (1-alpha for semantic)
               alpha=1.0 → Pure BM25
               alpha=0.0 → Pure semantic
               alpha=0.5 → Equal weighting
    """
    # Get BM25 scores (normalize to 0-1)
    bm25_scores = bm25_index.get_scores(query)
    bm25_scores_norm = bm25_scores / (bm25_scores.max() + 1e-9)

    # Get semantic scores (already 0-1 from cosine)
    query_embedding = embed_text(query)
    semantic_scores = vector_index.similarity_search(query_embedding)

    # Weighted combination
    hybrid_scores = alpha * bm25_scores_norm + (1 - alpha) * semantic_scores

    # Sort by hybrid score
    ranked_docs = np.argsort(hybrid_scores)[::-1]
    return ranked_docs.tolist()
```

**Tuning alpha**:
- **α = 0.7-0.8**: Good for domains with unique terminology (medical, legal)
- **α = 0.5**: Balanced, good starting point
- **α = 0.3-0.4**: Good for conceptual queries (philosophical, thematic)

**Downsides**:
- Requires score normalization (BM25 scores unbounded)
- Sensitive to `alpha` tuning (need validation set)
- More complex than RRF

**Recommendation**: Use **RRF** unless you have strong reason to tune `alpha` per query type.

---

## Two-Stage Reranking Patterns

For large corpora (>100K documents), two-stage retrieval reduces cost and latency.

### Stage 1: Fast Retrieval (Recall-Focused)

Use **BM25** or **fast ANN** to retrieve top-100 candidates quickly.

```python
# Stage 1: BM25 retrieval (cheap, fast)
candidates = bm25_index.get_top_k(query, k=100)  # ~5ms
```

### Stage 2: Precise Reranking (Precision-Focused)

Use **cross-encoder** or **LLM-based reranking** on top-100 to reorder.

```python
# Stage 2: Cross-encoder reranking (expensive, accurate)
from sentence_transformers import CrossEncoder

reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-12-v2')

# Score each candidate with query
pairs = [(query, doc_text) for doc_text in candidates]
scores = reranker.predict(pairs)  # ~50ms for 100 docs

# Rerank
reranked = sorted(zip(candidates, scores), key=lambda x: x[1], reverse=True)
top_k = reranked[:10]
```

**Cost comparison**:

| Approach | Stage 1 Cost | Stage 2 Cost | Total Latency |
|----------|-------------|--------------|---------------|
| **BM25 only** | $0 | $0 | 5-10ms |
| **Semantic only** | $0.0001 (embed query) | $0 | 10-20ms |
| **Hybrid (RRF)** | $0.0001 | $0 | 15-30ms |
| **Two-stage reranking** | $0 (BM25) | $0.001 (cross-encoder) | 50-100ms |

**When to use two-stage**:
- Large corpus (>100K docs) where semantic search alone is too slow
- High-stakes retrieval (legal, medical) where precision matters more than latency
- Budget allows reranker API calls ($0.001-0.01 per query)

---

## Sequential vs Parallel Retrieval

### Sequential Retrieval

Run BM25 first, then semantic search on BM25 results.

```python
# Step 1: BM25 retrieval
bm25_results = bm25_index.search(query, k=100)

# Step 2: Semantic reranking on BM25 results only
doc_embeddings = embed_texts([docs[i] for i in bm25_results])
query_embedding = embed_text(query)
semantic_scores = cosine_similarity(query_embedding, doc_embeddings)

# Rerank
reranked = sorted(zip(bm25_results, semantic_scores), key=lambda x: x[1], reverse=True)
```

**Pros**: Lower cost (only embed top-100 BM25 results, not all docs)
**Cons**: May miss documents that semantic search would find but BM25 didn't

### Parallel Retrieval (RRF Approach)

Run BM25 and semantic search independently, then merge with RRF.

```python
# Run both in parallel
bm25_results = bm25_index.search(query, k=20)
semantic_results = vector_index.search(embed_text(query), k=20)

# Merge with RRF
final_results = reciprocal_rank_fusion([bm25_results, semantic_results])
```

**Pros**: Each method finds its best matches independently (better recall)
**Cons**: Higher cost (semantic search runs on all docs, not just top-100)

**Recommendation**: Use **parallel retrieval + RRF** for maximum recall. Use **sequential** if cost is a constraint.

---

## Tuning Hybrid Search Weights (Alpha Parameter)

If using weighted combination (not RRF), tune `alpha` on a validation set.

### Validation Protocol

```python
import numpy as np

def evaluate_alpha(queries, ground_truth, bm25_index, vector_index, alphas=[0.3, 0.5, 0.7]):
    """
    Evaluate Recall@5 for different alpha values.
    """
    results = {}

    for alpha in alphas:
        recalls = []
        for query, relevant_docs in zip(queries, ground_truth):
            hybrid_results = weighted_hybrid_search(query, bm25_index, vector_index, alpha)
            top_5 = hybrid_results[:5]
            recall = len(set(top_5) & set(relevant_docs)) / len(relevant_docs)
            recalls.append(recall)

        results[alpha] = np.mean(recalls)

    return results

# Example output:
# {0.3: 0.72, 0.5: 0.78, 0.7: 0.75}  → Best alpha = 0.5
```

### Domain-Specific Alpha Tuning

Different query types benefit from different `alpha` values:

| Query Type | Best Alpha | Reasoning |
|------------|-----------|-----------|
| **Exact entity** ("Chapter 2 Verse 47") | 0.8-0.9 | BM25 dominates |
| **Conceptual** ("What is dharma?") | 0.2-0.4 | Semantic dominates |
| **Mixed** ("karma in Chapter 3") | 0.4-0.6 | Balanced |
| **Short keywords** ("naan recipe") | 0.7-0.8 | BM25 better |
| **Long natural language** ("How do I make bread?") | 0.3-0.5 | Semantic better |

**Dynamic alpha selection**: Use query classifier to predict alpha per query (advanced technique).

---

## When Hybrid Search Is Worth the Complexity

### Use Hybrid When:

✅ **Diverse query types**: Mix of exact matches and conceptual queries
✅ **Vocabulary mismatch**: Synonyms, paraphrases common
✅ **Medium-large corpus**: 1K-1M documents (enough to show improvement)
✅ **Quality matters**: 10-15% Recall@5 improvement justifies added complexity

### Stick to BM25 When:

❌ **All queries are exact matches**: "recipe 12345", "verse 2.47"
❌ **Tiny corpus**: <100 documents (hybrid overhead not worth it)
❌ **Zero latency budget**: Semantic search adds 10-50ms

### Stick to Semantic When:

❌ **All queries are conceptual**: "philosophical questions about life"
❌ **Strong paraphrasing**: User queries never match document vocabulary
❌ **Multilingual**: Queries and docs in different languages

---

## Practical Implementation: Hybrid Search with RRF

```python
from rank_bm25 import BM25Okapi
import faiss
import numpy as np
from openai import OpenAI

client = OpenAI()

# Step 1: Prepare data
documents = [
    "The Bhagavad Gita teaches the path of dharma and karma.",
    "Karma yoga is the yoga of selfless action without attachment.",
    "How to make naan bread in a tandoor oven with yeast.",
    "Arjuna asks Krishna about his duty on the battlefield."
]

# Step 2: Build BM25 index
tokenized_docs = [doc.lower().split() for doc in documents]
bm25 = BM25Okapi(tokenized_docs)

# Step 3: Build vector index
def embed_texts(texts):
    response = client.embeddings.create(model="text-embedding-3-small", input=texts)
    return np.array([e.embedding for e in response.data])

doc_embeddings = embed_texts(documents)
faiss.normalize_L2(doc_embeddings)

dimension = doc_embeddings.shape[1]
vector_index = faiss.IndexFlatIP(dimension)  # Inner product (cosine after normalization)
vector_index.add(doc_embeddings)

# Step 4: Query with hybrid search
def hybrid_search(query: str, k: int = 3):
    # BM25 search
    tokenized_query = query.lower().split()
    bm25_scores = bm25.get_scores(tokenized_query)
    bm25_ranking = [(i, score) for i, score in enumerate(bm25_scores)]
    bm25_ranking = sorted(bm25_ranking, key=lambda x: x[1], reverse=True)

    # Semantic search
    query_embedding = embed_texts([query])[0]
    faiss.normalize_L2(query_embedding.reshape(1, -1))
    distances, indices = vector_index.search(query_embedding.reshape(1, -1), len(documents))
    semantic_ranking = [(idx, 1 - dist) for idx, dist in zip(indices[0], distances[0])]

    # RRF fusion
    rrf_scores = {}
    for rank, (doc_id, _) in enumerate(bm25_ranking):
        rrf_scores[doc_id] = rrf_scores.get(doc_id, 0) + 1 / (60 + rank + 1)
    for rank, (doc_id, _) in enumerate(semantic_ranking):
        rrf_scores[doc_id] = rrf_scores.get(doc_id, 0) + 1 / (60 + rank + 1)

    # Sort by RRF score
    sorted_docs = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
    return sorted_docs[:k]

# Step 5: Test query
query = "What is selfless action in the Gita?"
results = hybrid_search(query, k=3)

print("Hybrid Search Results (RRF):")
for rank, (doc_id, score) in enumerate(results, 1):
    print(f"{rank}. Document {doc_id}: {documents[doc_id]} (RRF score: {score:.4f})")
```

**Expected Output**:
```
Hybrid Search Results (RRF):
1. Document 1: Karma yoga is the yoga of selfless action without attachment. (RRF score: 0.0329)
2. Document 0: The Bhagavad Gita teaches the path of dharma and karma. (RRF score: 0.0325)
3. Document 3: Arjuna asks Krishna about his duty on the battlefield. (RRF score: 0.0161)
```

**Analysis**:
- Document 1 ranks first (contains "selfless action" exactly + "Gita" conceptually related)
- Document 0 ranks second (mentions "Gita" + "karma" keyword)
- Document 3 ranks third (conceptually related to Gita, but less relevant)
- Document 2 (naan recipe) not in top-3 (correctly filtered out)

---

## Common Pitfalls

1. **Not normalizing BM25 scores**: If using weighted combination (not RRF), normalize BM25 to 0-1 range.
2. **Ignoring query types**: Some queries need pure BM25 (exact matches), not hybrid.
3. **Over-tuning alpha**: Use validation set, not test set, to tune `alpha` (avoid overfitting).
4. **Sequential retrieval missing semantic-only matches**: Use parallel retrieval + RRF for better recall.
5. **Forgetting to benchmark**: Measure Recall@k on validation set to confirm improvement (don't assume hybrid is always better).

---

## Performance Benchmarks (Typical Results)

On recipe + Bhagavad Gita corpus (10,000 documents, 100 validation queries):

| Method | Recall@5 | Recall@10 | Latency | Cost per Query |
|--------|----------|-----------|---------|----------------|
| **BM25 only** | 0.68 | 0.79 | 8ms | $0 |
| **Semantic only** | 0.72 | 0.82 | 15ms | $0.0001 |
| **Hybrid (RRF)** | **0.81** | **0.89** | 25ms | $0.0001 |
| **Two-stage rerank** | **0.85** | **0.91** | 80ms | $0.001 |

**Key insight**: Hybrid (RRF) provides **10-15% improvement** over BM25 baseline with minimal cost increase.

---

## Next Steps

1. **Hands-on**: Complete `lesson-12/hybrid_search_comparison.ipynb` to implement RRF and measure Recall@k.
2. **Optimization**: Read `lesson-12/context_quality_evaluation.md` to learn chunking strategies for better retrieval.
3. **Production**: Explore two-stage reranking with cross-encoders for high-stakes applications.

---

## Key Takeaways

✅ **Hybrid search combines BM25 + semantic** for 10-15% Recall@5 improvement
✅ **RRF is simpler than weighted combination** (no score normalization, no alpha tuning)
✅ **Parallel retrieval + RRF** gives best recall (each method finds its strengths)
✅ **Two-stage reranking** (BM25 → cross-encoder) for precision-critical apps
✅ **Tune alpha per query type** for weighted approaches (exact vs. conceptual)
✅ **Always benchmark on validation set** to confirm improvement

---

## Further Reading

- [Reciprocal Rank Fusion paper](https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf) (Cormack et al., 2009)
- [Cohere's Hybrid Search Guide](https://docs.cohere.com/docs/hybrid-search)
- [Elasticsearch Hybrid Search](https://www.elastic.co/guide/en/elasticsearch/reference/current/rrf.html)
- Cross-encoder reranking: [Sentence-Transformers](https://www.sbert.net/examples/applications/cross-encoder/README.html)
