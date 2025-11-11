# Embedding-Based Retrieval: Semantic Search Fundamentals

**Reading Time**: 20-25 minutes
**Prerequisites**: HW4 (BM25 Retrieval), basic understanding of vector spaces
**Learning Objective**: Understand semantic search with embeddings and when it outperforms lexical retrieval

---

## Introduction

Traditional keyword-based retrieval (like BM25) matches documents based on **exact term overlap**. If a user searches for "how to make bread" and a document says "baking dough instructions," BM25 might miss it entirely because no words match.

**Semantic search** solves this by representing text as dense vectors (embeddings) that capture **meaning**, not just words. Documents about bread-making cluster together in vector space, even with different vocabulary.

---

## Embeddings vs Lexical Search

### Lexical Search (BM25)
- **Matching**: Exact term overlap with TF-IDF weighting
- **Strengths**: Fast, interpretable, works well for exact matches
- **Weaknesses**: Vocabulary mismatch (synonyms, paraphrasing), no semantic understanding

**Example**: Query "car" won't match document with "automobile" unless both terms appear.

### Semantic Search (Embeddings)
- **Matching**: Cosine similarity in high-dimensional vector space
- **Strengths**: Handles synonyms, paraphrases, and conceptual similarity
- **Weaknesses**: Slower (vector operations), harder to debug, requires embedding model

**Example**: Query "car" embedding is close to "automobile," "vehicle," "sedan" embeddings.

---

## How Embeddings Work

### 1. Text → Vector Transformation

An **embedding model** (e.g., OpenAI's `text-embedding-3-small`, Cohere's `embed-english-v3.0`) maps text to a fixed-size vector:

```python
# Input: "The Bhagavad Gita teaches dharma"
# Output: [0.023, -0.145, 0.891, ..., 0.102]  # 1536 dimensions for OpenAI
```

**Key Properties**:
- **Dimensionality**: Typically 384-1536 dimensions
- **Dense vectors**: Most values are non-zero (unlike sparse TF-IDF)
- **Semantic proximity**: Similar texts have similar vectors

### 2. Similarity Measurement

**Cosine Similarity** measures angle between vectors:

```
similarity(A, B) = (A · B) / (||A|| × ||B||)
```

- **Range**: -1 (opposite) to +1 (identical)
- **Typical relevant docs**: 0.7-0.9 similarity
- **Irrelevant docs**: <0.5 similarity

**Example**:
```python
query = "What is karma?"
doc1 = "Karma means action and its consequences"  # similarity: 0.85
doc2 = "How to make chocolate cake"              # similarity: 0.21
```

---

## Vector Databases and Similarity Search

### The Challenge: Scale

For 10,000 documents, comparing query to all docs requires 10,000 similarity calculations. At scale (millions of docs), this is too slow.

### Solution 1: Exact k-NN (Brute Force)

**k-Nearest Neighbors (k-NN)**: Find k documents with highest similarity.

```python
# Pseudocode for exact k-NN
similarities = []
for doc_embedding in all_docs:
    sim = cosine_similarity(query_embedding, doc_embedding)
    similarities.append((doc_id, sim))

top_k = sorted(similarities, reverse=True)[:k]
```

**Pros**: Guaranteed optimal results
**Cons**: O(N) time complexity—too slow for large datasets

### Solution 2: Approximate Nearest Neighbors (ANN)

**ANN algorithms** trade accuracy for speed using indexing structures:

#### FAISS (Facebook AI Similarity Search)
- **Index types**: Flat (exact), IVF (inverted file), HNSW (graph-based)
- **Performance**: 100x-1000x faster than brute force
- **Accuracy**: 95-99% recall@k with proper tuning
- **Use case**: Production systems with millions of vectors

#### HNSW (Hierarchical Navigable Small Worlds)
- **Structure**: Multi-layer proximity graph
- **Query time**: O(log N) with high-dimensional data
- **Memory**: Higher than IVF, but faster queries
- **Best for**: Real-time retrieval (<100ms latency)

#### LSH (Locality Sensitive Hashing)
- **Approach**: Hash similar vectors to same buckets
- **Speed**: Very fast, but lower recall than HNSW
- **Best for**: Ultra-low latency requirements

#### Annoy (Approximate Nearest Neighbors Oh Yeah)
- **Structure**: Binary trees with random projections
- **Pros**: Simple, memory-efficient
- **Cons**: Slower than HNSW for high-dimensional vectors

---

## Popular Vector Search Methods Comparison

| Method | Speed | Accuracy | Memory | Best Use Case |
|--------|-------|----------|--------|---------------|
| **Exact k-NN** | Slow (O(N)) | 100% | Low | Small datasets (<10K docs) |
| **FAISS-IVF** | Fast | 95-98% | Medium | Balanced performance |
| **FAISS-HNSW** | Very Fast | 97-99% | High | Real-time search |
| **LSH** | Ultra-Fast | 85-95% | Low | Latency-critical apps |
| **Annoy** | Fast | 90-95% | Low | Memory-constrained systems |

**Recommendation for this course**: Use **FAISS-HNSW** for accuracy and speed balance.

---

## When Semantic Retrieval Outperforms BM25

### Semantic Search Wins

1. **Conceptual queries**: "What does the Gita say about duty?" (matches verses with "dharma," "responsibility," "obligation")
2. **Synonym-heavy domains**: Medical (disease/illness), legal (statute/law), recipes (sauté/fry)
3. **Paraphrased content**: User asks "how to fix broken authentication," doc says "troubleshooting login issues"
4. **Cross-lingual**: Query in English, docs in Hindi (with multilingual embeddings)

### BM25 Wins

1. **Exact matches**: "Chapter 2 Verse 47" (BM25 instantly finds the verse number)
2. **Rare terms**: "Arjuna" (unique term, no synonym confusion)
3. **Short queries**: "recipe for naan" (few words, exact match sufficient)
4. **Factual lookups**: "population of India 2024" (specific entities and numbers)

### Best Approach: **Hybrid Search** (Lesson 12, Part 2)

Combine BM25 (lexical) + semantic search for **10-15% Recall@5 improvement** (coming next).

---

## Cost and Latency Considerations

### Embedding Generation Costs

| Provider | Model | Dimensions | Cost per 1M tokens | Latency |
|----------|-------|------------|-------------------|---------|
| **OpenAI** | `text-embedding-3-small` | 1536 | $0.02 | 50-100ms |
| **OpenAI** | `text-embedding-3-large` | 3072 | $0.13 | 100-200ms |
| **Cohere** | `embed-english-v3.0` | 1024 | $0.10 | 80-150ms |
| **Cohere** | `embed-multilingual-v3.0` | 1024 | $0.10 | 100-200ms |

**For 10,000 recipe documents (avg 200 tokens each)**:
- Total tokens: 10,000 × 200 = 2M tokens
- Cost with OpenAI small: $0.04 (one-time, can cache embeddings)

### Vector Search Latency

- **FAISS exact k-NN**: 10-50ms for 10K docs
- **FAISS-HNSW**: 5-20ms for 1M docs
- **Network latency (API call)**: 50-200ms dominates total time

**Production tip**: Pre-compute and cache document embeddings. Only embed queries at runtime.

---

## Practical Implementation Example

```python
from openai import OpenAI
import numpy as np
import faiss

client = OpenAI()

# Step 1: Generate embeddings for documents
def embed_texts(texts: list[str]) -> np.ndarray:
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=texts
    )
    return np.array([e.embedding for e in response.data])

documents = [
    "The Bhagavad Gita teaches the path of dharma.",
    "Karma yoga is the yoga of selfless action.",
    "How to make naan bread in a tandoor oven."
]

doc_embeddings = embed_texts(documents)  # Shape: (3, 1536)

# Step 2: Build FAISS index
dimension = doc_embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)  # L2 distance (cosine after normalization)
faiss.normalize_L2(doc_embeddings)    # Normalize for cosine similarity
index.add(doc_embeddings)

# Step 3: Query
query = "What is selfless action?"
query_embedding = embed_texts([query])[0]
faiss.normalize_L2(query_embedding.reshape(1, -1))

# Step 4: Search top-k
k = 2
distances, indices = index.search(query_embedding.reshape(1, -1), k)

print(f"Top-{k} results:")
for i, idx in enumerate(indices[0]):
    similarity = 1 - distances[0][i]  # Convert L2 distance to similarity
    print(f"{i+1}. Document {idx}: {documents[idx]} (similarity: {similarity:.3f})")
```

**Expected Output**:
```
Top-2 results:
1. Document 1: Karma yoga is the yoga of selfless action. (similarity: 0.872)
2. Document 0: The Bhagavad Gita teaches the path of dharma. (similarity: 0.691)
```

Notice: Document 1 ranks first despite no word overlap with "selfless action" (embeddings capture meaning).

---

## Common Pitfalls

1. **Not normalizing embeddings**: Always normalize vectors before cosine similarity or use `IndexFlatIP` (inner product) in FAISS.
2. **Mixing embedding models**: Query and documents must use the same embedding model (dimension mismatch otherwise).
3. **Over-reliance on semantic search**: Some queries need exact matches (use hybrid search).
4. **Ignoring embedding costs**: Batch API calls (100 texts per request) to reduce latency and cost.
5. **Stale embeddings**: Re-embed documents when content changes (track with versioning).

---

## Next Steps

1. **Hands-on**: Complete `lesson-12/hybrid_search_comparison.ipynb` to compare BM25 vs semantic vs hybrid retrieval.
2. **Deep dive**: Read `lesson-12/hybrid_search_strategies.md` to learn Reciprocal Rank Fusion (RRF).
3. **Optimization**: Explore `lesson-12/chunking_optimization.ipynb` to test chunking strategies for better retrieval.

---

## Key Takeaways

✅ **Semantic search uses embeddings** to capture meaning, not just keywords
✅ **FAISS-HNSW** provides 100x speedup with 97-99% accuracy for ANN search
✅ **Use semantic search** for conceptual queries, synonyms, and paraphrasing
✅ **Use BM25** for exact matches, rare terms, and short queries
✅ **Hybrid search** (next tutorial) combines both for best results
✅ **Cost**: ~$0.02 per 1M tokens with OpenAI embeddings (cache for reuse)

---

## Further Reading

- [OpenAI Embeddings Guide](https://platform.openai.com/docs/guides/embeddings)
- [FAISS Documentation](https://faiss.ai/)
- [Cohere Semantic Search Tutorial](https://docs.cohere.com/docs/semantic-search)
- Anthropic's "Contextual Retrieval" (covered in `context_quality_evaluation.md`)
