# RAG Troubleshooting Guide

Common problems and their solutions when building RAG systems.

## Retrieval Issues

### Problem: Relevant chunks not being retrieved

**Symptoms**: Correct answer exists in knowledge base but not found

**Diagnosis Checklist**:
1. Is the query using different terminology than the documents?
2. Are chunks too small to contain enough context?
3. Is the retriever returning too few results (low top_k)?

**Solutions**:

| Root Cause | Fix |
|------------|-----|
| Vocabulary mismatch | Add semantic retrieval or synonym expansion |
| Chunk too small | Increase chunk size or add contextual retrieval |
| Low top_k | Increase similarity_top_k from 5 to 10-20 |
| BM25-only | Add hybrid retrieval with embeddings |

### Problem: Irrelevant chunks being retrieved

**Symptoms**: Retrieved chunks don't answer the question

**Diagnosis**:
1. Check if query is ambiguous
2. Verify embedding model quality
3. Check if chunks contain off-topic content

**Solutions**:
- Implement reranking post-retrieval
- Add metadata filtering
- Improve chunking strategy
- Use query expansion/clarification

### Problem: Exact matches failing

**Symptoms**: Searching for "SKU-12345" returns nothing

**Root Cause**: Semantic embeddings don't handle codes well

**Solution**: Always include BM25 in hybrid retrieval for exact match capability

```python
# Hybrid approach
bm25_results = bm25_retriever.retrieve(query)
semantic_results = semantic_retriever.retrieve(query)
# Merge and deduplicate
```

## Generation Issues

### Problem: Hallucinations despite good retrieval

**Symptoms**: Retrieved chunks are correct but LLM invents facts

**Solutions**:
1. Add explicit instruction: "Only use information from the provided context"
2. Add fallback instruction: "If the context doesn't contain the answer, say so"
3. Lower temperature (0.1-0.3 for factual tasks)
4. Implement citation verification

**Prompt Template Fix**:
```
Use ONLY the following information to answer. 
If the answer is not in the provided text, respond with "I don't have that information."
Do not use prior knowledge.

Context:
{retrieved_chunks}

Question: {query}
```

### Problem: Contradictory information in response

**Symptoms**: Answer includes conflicting statements

**Root Cause**: Retrieved chunks from different time periods or sources

**Solutions**:
1. Add timestamp metadata and prefer recent
2. Implement source authority ranking
3. Add explicit contradiction detection in prompt

### Problem: Response ignores some retrieved chunks

**Symptoms**: Answer only uses first few chunks

**Root Cause**: Context too long, attention degradation

**Solutions**:
- Reduce number of chunks
- Reorder: most relevant chunks in middle
- Summarize chunks before adding to context
- Use iterative retrieval-generation

## Indexing Issues

### Problem: Indexing pipeline too slow

**Causes and Fixes**:

| Cause | Solution |
|-------|----------|
| Large documents | Parallel processing |
| Embedding API latency | Batch embeddings |
| Single-threaded | Use async operations |
| Re-indexing everything | Implement incremental indexing |

### Problem: Vector store running out of memory

**Solutions**:
1. Use disk-backed vector store (FAISS with disk index)
2. Implement ANN (approximate nearest neighbor)
3. Reduce embedding dimensionality
4. Shard across multiple stores

### Problem: Embeddings incompatible after model update

**Prevention**:
- Use open-weights models for lifecycle control
- Track model version in metadata
- Plan for full reindex in production schedules

**Recovery**:
- Full reindex required (no shortcut)
- Keep old index running during reindex
- Blue-green deployment for cutover

## Performance Issues

### Problem: Query latency too high

**Breakdown typical RAG query**:
- Embedding query: 50-200ms
- Vector search: 10-100ms
- LLM generation: 500-3000ms

**Optimizations**:

| Component | Optimization |
|-----------|--------------|
| Embedding | Use smaller model, cache common queries |
| Vector search | Add ANN index (HNSW), reduce top_k |
| Generation | Reduce context size, use smaller LLM |
| Overall | Add response caching for common queries |

### Problem: Costs too high

**Cost Breakdown**:
- Embedding generation (indexing): One-time
- Embedding queries: Per query
- LLM tokens: Per query (context + response)

**Optimizations**:
1. Cache embeddings and responses
2. Use smaller embedding models
3. Reduce chunk count per query
4. Implement prompt caching for repeated context

## Quality Measurement

### Metrics to Track

| Metric | Measures | How to Compute |
|--------|----------|----------------|
| Recall@k | Are correct chunks in top k? | Manual labeling + evaluation |
| MRR | How high is first correct chunk? | 1/rank of first relevant result |
| Answer accuracy | Is final answer correct? | Human evaluation or LLM-as-judge |
| Faithfulness | Does answer stick to context? | Check for hallucination |
| Latency p50/p95 | Speed | Log query times |

### Quick Health Check

```python
def rag_health_check(rag_system, test_cases):
    """
    test_cases: list of (query, expected_chunk_ids)
    """
    results = {
        'recall_at_5': [],
        'recall_at_10': [],
        'latency': []
    }
    
    for query, expected_ids in test_cases:
        start = time.time()
        retrieved = rag_system.retrieve(query, top_k=10)
        latency = time.time() - start
        
        retrieved_ids = [r.id for r in retrieved]
        
        recall_5 = len(set(expected_ids) & set(retrieved_ids[:5])) / len(expected_ids)
        recall_10 = len(set(expected_ids) & set(retrieved_ids)) / len(expected_ids)
        
        results['recall_at_5'].append(recall_5)
        results['recall_at_10'].append(recall_10)
        results['latency'].append(latency)
    
    return {k: sum(v)/len(v) for k, v in results.items()}
```

## Common Anti-Patterns

| Anti-Pattern | Why It's Bad | Better Approach |
|--------------|--------------|-----------------|
| No evaluation set | Can't measure improvements | Create 50+ test queries with labels |
| Optimizing blindly | Might make things worse | A/B test changes |
| One-size-fits-all chunks | Different content needs different treatment | Content-aware chunking |
| Ignoring metadata | Lose filtering capability | Always preserve source info |
| No monitoring | Issues go undetected | Log retrieval scores, latency |
