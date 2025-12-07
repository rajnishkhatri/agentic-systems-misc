---
name: rag-knowledge
description: Comprehensive RAG (Retrieval-Augmented Generation) system design and implementation patterns. Use when building knowledge retrieval systems, implementing document indexing, designing semantic search, handling embeddings, chunking strategies, or any task involving grounding LLM responses with external knowledge sources. Covers Basic RAG, Semantic Indexing, and Indexing at Scale patterns.
license: Educational reference derived from "LLM Patterns" by Lakshmanan, Robinson & Munn (O'Reilly, 2025)
---

# RAG Knowledge Skill

This skill provides comprehensive guidance for designing and implementing Retrieval-Augmented Generation systems.

## Knowledge Map

```
RAG SYSTEM ARCHITECTURE
═══════════════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────────────┐
│                           KNOWLEDGE SOURCES                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │   Text   │  │  Tables  │  │  Images  │  │  Videos  │  │ Private  │      │
│  │Documents │  │   Data   │  │   OCR    │  │Keyframes │  │   Data   │      │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘      │
└───────┼─────────────┼─────────────┼─────────────┼─────────────┼────────────┘
        │             │             │             │             │
        └─────────────┴──────┬──────┴─────────────┴─────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        INDEXING PIPELINE (Batch)                             │
│                                                                              │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐         │
│  │   CHUNKING      │───▶│   EMBEDDING     │───▶│   STORAGE       │         │
│  │                 │    │                 │    │                 │         │
│  │ • Length-based  │    │ • Text vectors  │    │ • Vector store  │         │
│  │ • Sentence      │    │ • Image vectors │    │ • Document store│         │
│  │ • Paragraph     │    │ • Multimodal    │    │ • Metadata      │         │
│  │ • Semantic      │    │                 │    │                 │         │
│  │ • Hierarchical  │    │                 │    │                 │         │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘         │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        DOCUMENT STORE                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Chunks + Embeddings + Metadata (source, timestamp, domain, etc.)   │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    QUESTION-ANSWERING PIPELINE (Runtime)                     │
│                                                                              │
│  ┌──────────┐    ┌─────────────────┐    ┌─────────────────┐                 │
│  │  QUERY   │───▶│   RETRIEVAL     │───▶│   GENERATION    │                 │
│  │          │    │                 │    │                 │                 │
│  │          │    │ • BM25 keyword  │    │ • Prompt with   │                 │
│  │          │    │ • Semantic      │    │   context       │                 │
│  │          │    │ • Hybrid        │    │ • LLM response  │                 │
│  │          │    │ • Filtered      │    │ • Citations     │                 │
│  └──────────┘    └─────────────────┘    └─────────────────┘                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Pattern Progression Map

```
PATTERN SOPHISTICATION LADDER
═════════════════════════════════════════════════════════════════════════════

    ┌─────────────────────────────────────────────────────────────────────┐
    │  Pattern 12: Deep Search           [Complex multi-step research]    │
    └───────────────────────────────────────────┬─────────────────────────┘
                                                │ Need iterative refinement
    ┌───────────────────────────────────────────▼─────────────────────────┐
    │  Pattern 11: Trustworthy Generation    [Hallucination reduction]    │
    └───────────────────────────────────────────┬─────────────────────────┘
                                                │ Need citation verification
    ┌───────────────────────────────────────────▼─────────────────────────┐
    │  Pattern 10: Node Postprocessing       [Reranking, filtering]       │
    └───────────────────────────────────────────┬─────────────────────────┘
                                                │ Need result refinement
    ┌───────────────────────────────────────────▼─────────────────────────┐
    │  Pattern 9: Index-Aware Retrieval      [Query understanding]        │
    └───────────────────────────────────────────┬─────────────────────────┘
                                                │ Need query enhancement
    ┌───────────────────────────────────────────▼─────────────────────────┐
    │  Pattern 8: Indexing at Scale          [Metadata, freshness]        │◀─┐
    └───────────────────────────────────────────┬─────────────────────────┘  │
                                                │ Need production handling   │
    ┌───────────────────────────────────────────▼─────────────────────────┐  │
    │  Pattern 7: Semantic Indexing          [Embeddings, meaning]        │──┘
    └───────────────────────────────────────────┬─────────────────────────┘
                                                │ Need synonym handling
    ┌───────────────────────────────────────────▼─────────────────────────┐
    │  Pattern 6: Basic RAG                  [BM25, keyword matching]     │
    └─────────────────────────────────────────────────────────────────────┘

    Legend:
    ─────────────────────────────────────────────────────────────────────────
    DEMO/POC:        Pattern 6 (Basic RAG)
    INTERNAL TOOLS:  Patterns 6-8 (+ Semantic Indexing, Scale handling)
    EXTERNAL PRODUCTS: Patterns 6-12 (Full sophistication ladder)
```

## Core Concepts

### Why RAG Exists

RAG addresses five fundamental LLM limitations:

| Limitation | Problem | RAG Solution |
|------------|---------|--------------|
| Static knowledge cutoff | Cannot access post-training information | Runtime knowledge injection |
| Model capacity limits | Lossy compression of training data | External knowledge expansion |
| Private data access | No confidential/proprietary data | Runtime document retrieval |
| Hallucinations | Plausible but incorrect outputs | Grounded generation |
| No citations | Cannot attribute sources | Retrieved chunk attribution |

### Grounding Mechanism

LLMs preferentially use information present in the prompt. This enables two techniques:

**Priming**: Context influences token generation direction
```
Context: "The best food in France is found in Lyon."
Query: "Suggest three small cities to visit in Europe."
Result: Foodie-oriented city recommendations (Lyon influence)
```

**Override**: Recent context supersedes training data
```
Context: "Geno Smith traded to Raiders."
Query: "Who does Geno Smith play for?"
Result: "Raiders" (overrides training data showing Seahawks)
```

## Decision Matrices

### Retrieval Method Selection

| Scenario | Use BM25 (Keyword) | Use Semantic | Use Hybrid |
|----------|-------------------|--------------|------------|
| Exact product codes/IDs | ✅ Primary | ❌ Poor | ✅ BM25-weighted |
| Technical terminology | ✅ Good | ✅ Good | ✅ Balanced |
| Natural language queries | ❌ Poor | ✅ Primary | ✅ Semantic-weighted |
| Synonym-heavy domain | ❌ Poor | ✅ Primary | ✅ Semantic-weighted |
| Multilingual content | ❌ Fails | ✅ Primary | ✅ Semantic-only |
| Factual equipment manuals | ✅ Primary | ✅ Good | ✅ Balanced |

### Chunking Strategy Selection

| Document Type | Recommended Strategy | Rationale |
|---------------|---------------------|-----------|
| Technical manuals | Sentence-based with overlap | Preserve complete instructions |
| Legal contracts | Paragraph-based | Maintain clause integrity |
| Research papers | Hierarchical (RAPTOR) | Multi-level abstraction needed |
| Product catalogs | Row-based (tables) | Semantically independent items |
| Time series data | Column-based (tables) | Preserve temporal relationships |
| Markdown/HTML docs | Document-structure | Use native hierarchy |
| Chat transcripts | Semantic shift detection | Topic-coherent segments |

### When to Use RAG vs. Large Context Window

| Factor | Use RAG | Use Full Document in Context |
|--------|---------|------------------------------|
| Document size | > 500 pages | < 500 pages |
| Query frequency | High (many queries) | Low (few queries) |
| Knowledge base size | Multiple documents | Single document |
| Update frequency | Frequent updates | Rarely changes |
| Cost sensitivity | High (optimize tokens) | Low (can afford full context) |
| Precision requirements | Need specific chunks | Need holistic understanding |

### Embedding Model Selection

| Requirement | Recommendation |
|-------------|----------------|
| General purpose, best quality | Gemini embeddings |
| Open weights, high quality | Qwen2 (Alibaba) |
| Multilingual | Specialized multilingual models |
| Domain-specific (medical/legal) | Domain-pretrained models |
| Production stability | Open weights (control lifecycle) |
| Lowest latency | Smaller dimensionality models |

## Design Patterns

### Pattern 6: Basic RAG

**When to use**: Starting point for all RAG systems; factual content retrieval

**Architecture**:
```python
# Indexing Pipeline
document = Document(text=content, metadata={"source": url, "date": timestamp})
node_parser = SentenceSplitter(chunk_size=200, chunk_overlap=20)
nodes = node_parser.get_nodes_from_documents([document])
docstore = SimpleDocumentStore()
docstore.add_documents(nodes)

# Retrieval Pipeline
retriever = BM25Retriever.from_defaults(docstore=docstore, similarity_top_k=5)
retrieved_nodes = retriever.retrieve(query)

# Generation Pipeline
messages = [
    ChatMessage(role="system", content="Use the following text to answer the query."),
    *[ChatMessage(role="system", content=node.text) for node in retrieved_nodes],
    ChatMessage(role="user", content=query)
]
response = llm.chat(messages)
```

**Limitations**:
- Requires exact keyword matches
- Misses synonyms ("broken" vs "ruptured")
- Fixed chunk size tradeoffs

---

### Pattern 7: Semantic Indexing

**When to use**: Natural language queries, synonym handling, multimodal content

**Key Technique**: Embed chunks as vectors capturing semantic meaning

```python
# Embedding generation
model = SentenceTransformer('all-MiniLM-L6-v2')
embeddings = model.encode(chunks)

# Query matching
query_embedding = model.encode([query])[0]
# Use cosine similarity to find nearest neighbors
```

**Chunking Strategies**:

1. **Length-based with overlap**: Fixed size, preserve boundary context
2. **Sentence-based**: Complete sentences until threshold
3. **Paragraph-based**: Natural document breaks
4. **Document-structure**: Use Markdown/HTML hierarchy
5. **Semantic shift detection**: Topic modeling to find boundaries

**Contextual Retrieval Enhancement**:
```
Prompt to LLM:
<document>{{WHOLE_DOCUMENT}}</document>
<chunk>{{CHUNK_CONTENT}}</chunk>
Give succinct context to situate this chunk within the overall document
for improving search retrieval.
```
Result: 67% reduction in incorrect retrieval rates (Anthropic benchmark)

**Multimodal Handling**:

| Media Type | Processing Approach |
|------------|---------------------|
| Images | OCR → text description OR multimodal embedding |
| Videos | Transcribe audio + sample keyframes → embed |
| Tables | Preserve structure + embed with headers |

**Table Chunking Options**:
- Table-based: Embed entire small tables
- Sliding window: Large tables with header preservation
- Row-based: Semantically independent rows
- Column-based: Time series / related measurements

**Hybrid Embedding for Tables**:
```python
def create_hybrid_embeddings(text_embeddings, numeric_data, boolean_data):
    # Normalize numeric data to 0-1 scale
    scaler = StandardScaler()
    normalized_numeric = scaler.fit_transform(numeric_data)
    
    # Concatenate all representations
    combined = np.concatenate([
        text_embeddings[i],
        normalized_numeric[i],
        boolean_data[i]
    ])
    return combined
```

**Limitations**:
- Fixed-dimensional compression loses nuance
- Chunking can break semantic coherence
- Vector DB scalability requires ANN approximations
- No temporal understanding
- Text/image vectors may misalign

---

### Pattern 8: Indexing at Scale

**When to use**: Production systems with freshness, contradiction, and lifecycle requirements

**Problem Categories**:

| Issue | Example | Impact |
|-------|---------|--------|
| Disambiguation | "Fluid" in physics vs. common usage | Wrong context retrieved |
| Data freshness | CDC COVID guidelines changing | Outdated recommendations |
| Contradictions | 2017 vs 2022 hypertension definitions | Conflicting medical advice |
| Model deprecation | Embedding API version changes | Full reindex required |

**Metadata-Based Solutions**:

```python
# Attach metadata during indexing
metadata = {
    'source': 'National Health Guidelines',
    'publication_date': '2023-03-15',
    'domain': 'Treatment protocols',
    'citation': 'Journal of Medical Practice, Vol 45'
}

# Filter during retrieval
where_conditions = [
    {'publication_date': {'$gte': '2024-01-01'}},
    {'domain': 'Treatment protocols'}
]
results = collection.query(
    query_embeddings=[query_embedding],
    where={"$and": where_conditions}
)
```

**Freshness Handling Strategies**:

| Strategy | When to Use | Tradeoff |
|----------|-------------|----------|
| Retrieval filtering | Query-time freshness | Slower queries |
| Document store pruning | Batch maintenance | May lose valid old content |
| Result reranking | Post-retrieval boost | More compute per query |

**Contradiction Resolution**:
- Use timestamp to prefer newer information
- Use source authority ranking
- Use domain categorization for context

**Model Lifecycle Management**:
- Prefer open-weights models (Qwen2) for lifecycle control
- Plan for full reindex when switching models
- Monitor MTEB leaderboard for model comparisons

**When to Switch Embedding Models**:
- 25%+ efficiency gain in dimensionality
- Need for updated world knowledge
- Domain-specific model becomes available

---

### Advanced Techniques Reference

#### Hierarchical Chunking (RAPTOR)

For long documents requiring multi-level understanding:

```
Processing Phase:
Document → Chunks → Embed → Cluster → Summarize → Embed → Cluster → ...
                                                              ↓
                                                         Root Summary

Inference Phase:
Query → Match L1 nodes → Match L2 children → ... → Final chunks
```

Benefits: High-level + mid-level + specific detail retrieval

#### Industry Jargon Handling

| Approach | Pros | Cons |
|----------|------|------|
| Manual glossary | Precise control | High maintenance |
| Cooccurrence analysis | Automatic discovery | May miss rare terms |
| LLM expansion | Comprehensive | Hallucination risk |

**Directionality Warning**: ETF → index fund (one-way synonym)

#### Synonym Expansion

Apply to queries AND/OR documents:
```
Original: "What was the timeline for discovery in federal court?"
Expanded: "What was the timeline for discovery|disclosure|deposition in federal court?"
```

## Implementation Checklist

### Basic RAG Setup
- [ ] Convert documents to text (handle images/tables separately)
- [ ] Implement chunking with appropriate strategy
- [ ] Add overlap between chunks (10-20% of chunk size)
- [ ] Attach metadata (source, timestamp, domain)
- [ ] Set up document store (SimpleDocumentStore → production DB)
- [ ] Implement BM25 retriever
- [ ] Create generation prompt template
- [ ] Return citations with response

### Semantic Indexing Addition
- [ ] Select embedding model (check MTEB)
- [ ] Generate embeddings for all chunks
- [ ] Set up vector store (ChromaDB, Pinecone, etc.)
- [ ] Implement semantic retriever
- [ ] Consider hybrid retrieval (BM25 + semantic)
- [ ] Handle multimodal content if present
- [ ] Implement contextual retrieval if needed

### Production Scale Requirements
- [ ] Design metadata schema for filtering
- [ ] Implement freshness handling strategy
- [ ] Plan contradiction resolution approach
- [ ] Set up incremental indexing pipeline
- [ ] Monitor for model deprecation
- [ ] Establish reindexing procedures
- [ ] Implement query-time filtering

## Anti-Patterns to Avoid

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| Embedding-only retrieval | Misses exact product codes | Add BM25 hybrid |
| No chunk overlap | Loses boundary context | 10-20% overlap |
| Ignoring metadata | Can't filter by date/source | Always attach metadata |
| Single embedding model | Vendor lock-in | Plan for model lifecycle |
| Huge chunks | Diluted semantic signal | Right-size to content type |
| Tiny chunks | Lost context | Use hierarchical if needed |
| No citation tracking | Unverifiable responses | Preserve source in metadata |

## Performance Benchmarks Reference

| Technique | Improvement | Source |
|-----------|-------------|--------|
| Contextual retrieval | 67% reduction in incorrect retrieval | Anthropic |
| Hybrid retrieval (BM25 + semantic) | Better than either alone | General consensus |
| Domain-specific embeddings | 20-40% precision improvement | Varies by domain |

## Code Patterns Library

### Document Loading with Metadata
```python
document = Document(
    text=re.sub(r'\n{3,}', '\n\n', content.strip()),
    metadata={
        "source": url,
        "filename": filename,
        "date_loaded": time.strftime("%Y-%m-%d %H:%M:%S")
    }
)
```

### Hybrid Search Setup
```python
# BM25 for keywords
bm25_retriever = BM25Retriever.from_defaults(docstore=docstore, similarity_top_k=5)

# Semantic for meaning
semantic_retriever = VectorIndexRetriever(index=vector_index, similarity_top_k=5)

# Combine results with score fusion
```

### Metadata Filtering Query
```python
where_conditions = []
for key, value in filters.items():
    where_conditions.append({key: value})

where = {"$and": where_conditions} if len(where_conditions) > 1 else where_conditions[0]

results = collection.query(
    query_embeddings=[query_embedding.tolist()],
    where=where,
    n_results=top_k
)
```

### Generation Prompt Template
```python
messages = [
    ChatMessage(role="system", content="""
        Use the following trustworthy information to answer the query.
        If no relevant information is found, say so.
        Cite sources using [Source: X] format.
    """),
    *[ChatMessage(role="system", content=f"[Source: {node.metadata['source']}]\n{node.text}") 
      for node in retrieved_nodes],
    ChatMessage(role="user", content=query)
]
```

## References

### Source Material
- Lakshmanan, Robinson & Munn. "LLM Patterns" (O'Reilly, 2025). Chapters 3-4: Adding Knowledge.

### Canonical Papers
- Lewis et al. (2020). "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks" - Original RAG paper
- Gao et al. (2024). RAG variants review and evaluation framework
- Khan (2025). Comparison of 18 RAG variants

### Technical Resources
- MTEB Leaderboard: Embedding model rankings
- Anthropic: Contextual retrieval benchmarks
- AWS: Real-world RAG lessons
- Mercado Libre: Production RAG insights

### Embedding Research
- Bengio et al. (2000). Introduction of embeddings concept
- Olah (2014). Visual explanation of embeddings
- Schwaber-Cohen & Patel (2025). Chunking in LLM applications (Pinecone)

### Advanced Techniques
- RAPTOR: Recursive Abstractive Processing for Tree-Organized Retrieval
- Chen, Zhang & Choi (2022). Calibrating models for chunk conflict diagnosis
- Wang et al. (2025). Ambiguity, misinformation, and noise dataset
