# Agentic RAG: A Critical Evolution in Retrieval-Augmented Generation

**Source:** Google's "Agents Companion" Whitepaper (February 2025)
**Topic Complexity:** ⭐⭐⭐⭐
**Lines:** 287-327 from original document

---

## Overview

Agentic RAG represents a significant advancement in Retrieval-Augmented Generation, introducing **autonomous retrieval agents** that actively refine searches based on iterative reasoning, moving beyond traditional static RAG approaches.

**Key Innovation**: Instead of a single search pass, agents generate multiple query refinements, decompose complex queries, and validate retrieved knowledge before integrating it into responses.

---

## Traditional RAG vs. Agentic RAG

### Traditional RAG Pipeline

**Approach**: Static, single-pass retrieval

**Process**:
```
User Query
    ↓
Embed query into vector
    ↓
Search vector database (single pass)
    ↓
Retrieve top-k documents
    ↓
Feed documents + query to LLM
    ↓
Generate response
```

**Limitations**:
1. **Ambiguous Queries**: Single search may miss relevant documents
2. **Multi-Step Queries**: Can't decompose complex questions
3. **Multi-Perspective Queries**: Doesn't explore different angles
4. **No Validation**: Hallucinations and contradictions not detected

**Example Failure**:
```
Query: "What are the best practices for scaling microservices in cloud environments?"

Traditional RAG:
- Single search: "scaling microservices cloud"
- May miss documents about:
  - Container orchestration (Kubernetes)
  - Service mesh (Istio)
  - Cloud-specific strategies (AWS vs. Azure)
  - Cost optimization
- Result: Incomplete or generic response
```

### Agentic RAG Pipeline

**Approach**: Dynamic, iterative retrieval with autonomous agents

**Process**:
```
User Query
    ↓
Retrieval Agent analyzes query
    ↓
Generate multiple query expansions
    ├── Query 1: Focus on technical implementation
    ├── Query 2: Focus on architectural patterns
    └── Query 3: Focus on cost optimization
    ↓
Multi-step reasoning
    ├── Search for foundational concepts
    ├── Search for specific implementations
    └── Search for case studies
    ↓
Adaptive source selection
    ├── Vector database (for semantic search)
    ├── Relational database (for structured data)
    └── Web search (for recent updates)
    ↓
Evaluator Agent validates results
    ├── Check for hallucinations
    ├── Detect contradictions
    └── Assess completeness
    ↓
Synthesize response
```

**Example Success**:
```
Query: "What are the best practices for scaling microservices in cloud environments?"

Agentic RAG:
- Query Expansion:
  1. "microservices architecture patterns scalability"
  2. "container orchestration Kubernetes autoscaling"
  3. "cloud-native cost optimization AWS Azure"
- Multi-Step Reasoning:
  1. Retrieve foundational patterns
  2. Search for cloud-specific implementations
  3. Find cost-performance trade-offs
- Adaptive Sources:
  1. Internal knowledge base (architectural docs)
  2. Recent blog posts (latest trends)
  3. Case studies (real-world examples)
- Validation:
  1. Cross-check claims across sources
  2. Detect conflicting advice (flag for user)
- Result: Comprehensive, validated, multi-perspective response
```

---

## Four Key Innovations of Agentic RAG

### 1. Context-Aware Query Expansion

**Problem**: User queries are often underspecified or ambiguous.

**Solution**: Agents generate **multiple query refinements** to retrieve more relevant results.

**How It Works**:
```python
# Original query
user_query = "How do I improve my RAG system?"

# Agent generates query expansions
expanded_queries = [
    "RAG retrieval accuracy improvement techniques",
    "chunking strategies for better RAG performance",
    "embedding model fine-tuning for domain-specific RAG",
    "re-ranking methods for RAG search results",
    "RAG evaluation metrics and benchmarks"
]

# Execute all searches, combine results
all_results = []
for query in expanded_queries:
    all_results.extend(vector_search(query, top_k=5))

# Deduplicate and re-rank
final_results = rerank(deduplicate(all_results), top_k=10)
```

**Benefits**:
- Captures multiple interpretations of ambiguous queries
- Ensures comprehensive retrieval (reduces missed relevant documents)
- Adapts to user intent through iterative refinement

**Example**:
```
Query: "Tell me about Apple"

Without Query Expansion:
- Returns: Mix of company info, fruit nutrition, Apple products

With Query Expansion:
Agent asks: "Are you asking about Apple Inc. (company), apple (fruit), or something else?"
User: "The company"
Expanded Queries:
- "Apple Inc. history and products"
- "Apple financial performance and stock"
- "Apple innovation and technology leadership"
```

### 2. Multi-Step Reasoning

**Problem**: Complex queries can't be answered with single retrieval pass.

**Solution**: Agents **decompose queries** into logical steps, retrieving information sequentially.

**How It Works**:
```python
# Complex query requiring multi-step reasoning
query = "Compare the environmental impact of electric vs. gasoline cars, considering manufacturing and lifecycle."

# Agent decomposes into steps
step_1 = "Retrieve data on electric car manufacturing emissions"
step_2 = "Retrieve data on gasoline car manufacturing emissions"
step_3 = "Retrieve data on electric car lifecycle emissions (battery production, electricity source)"
step_4 = "Retrieve data on gasoline car lifecycle emissions (fuel extraction, combustion)"
step_5 = "Compare and synthesize findings"

# Execute steps sequentially, each informing the next
results = []
for step in [step_1, step_2, step_3, step_4]:
    results.append(execute_search(step))
    # Agent reviews results, refines next search based on findings

final_answer = synthesize(results, context=step_5)
```

**Benefits**:
- Handles complex, multi-faceted questions
- Builds knowledge incrementally (like human research)
- Each step informs the next (adaptive retrieval)

**Example**:
```
Query: "What caused the 2008 financial crisis and how were similar issues addressed in the 2020s?"

Multi-Step Reasoning:
1. Retrieve causes of 2008 financial crisis
   ↓ (Agent learns: subprime mortgages, lack of regulation)
2. Retrieve regulatory changes post-2008
   ↓ (Agent learns: Dodd-Frank Act, stress tests)
3. Retrieve financial events in 2020s
   ↓ (Agent learns: COVID-19 economic impact, bank runs)
4. Retrieve regulatory responses in 2020s
   ↓ (Agent learns: emergency measures, updated regulations)
5. Compare and contrast approaches
```

### 3. Adaptive Source Selection

**Problem**: Not all queries should use the same knowledge source.

**Solution**: Agents **dynamically select best knowledge sources** based on context.

**How It Works**:
```python
# Agent evaluates query characteristics
query_analysis = {
    "domain": "healthcare",
    "recency_required": True,  # Latest medical research
    "structure_type": "unstructured",  # Research papers, not tables
    "authoritative_source": True  # Peer-reviewed only
}

# Agent selects appropriate sources
if query_analysis["recency_required"]:
    sources = ["pubmed_recent", "arxiv_medical"]
else:
    sources = ["pubmed_archive", "medical_textbooks"]

if query_analysis["structure_type"] == "structured":
    sources.append("clinical_trials_database")  # Structured data
else:
    sources.append("research_papers_vector_db")  # Unstructured

# Execute searches across selected sources
results = multi_source_search(query, sources)
```

**Source Types**:
- **Vector databases**: Semantic search (unstructured text)
- **Relational databases**: Structured queries (SQL)
- **Web search**: Recent updates, external sources
- **Knowledge graphs**: Relationship-based retrieval
- **Document stores**: Full-text search

**Benefits**:
- Optimizes retrieval based on query type
- Leverages best source for each use case
- Reduces irrelevant results (precision improvement)

**Example**:
```
Query 1: "What is the capital of France?" (factual, static)
→ Agent selects: Knowledge graph (fast, structured)

Query 2: "What are the latest developments in quantum computing?" (recent, exploratory)
→ Agent selects: Web search + arXiv vector database (recency)

Query 3: "Show me sales data for Q3 2024 by region" (structured, analytical)
→ Agent selects: SQL database (relational data)
```

### 4. Validation and Correction

**Problem**: Retrieved knowledge may contain hallucinations or contradictions.

**Solution**: **Evaluator agents** cross-check knowledge before integrating into response.

**How It Works**:
```python
# Retrieve potential answers from multiple sources
retrieved_docs = [
    {"source": "Doc A", "claim": "The Eiffel Tower is 330 meters tall"},
    {"source": "Doc B", "claim": "The Eiffel Tower is 324 meters tall"},
    {"source": "Doc C", "claim": "The Eiffel Tower was completed in 1889"}
]

# Evaluator Agent checks for contradictions
contradictions = detect_contradictions(retrieved_docs)
# Result: Height mismatch between Doc A and Doc B

# Evaluator Agent validates against authoritative source
validated = cross_check_authority(contradictions, authoritative_source="official_eiffel_tower_site")
# Result: Doc B is correct (324 meters to antenna, 330 meters with flagpole)

# Filter hallucinations
filtered_docs = remove_hallucinations(retrieved_docs, validated_facts)

# Integrate into response
response = synthesize(filtered_docs)
```

**Validation Techniques**:
- **Cross-source verification**: Check if multiple sources agree
- **Authority checking**: Prefer authoritative sources (official docs, peer-reviewed)
- **Logical consistency**: Detect contradictory statements
- **Grounding validation**: Ensure claims are supported by retrieved text

**Benefits**:
- Reduces hallucinations in final response
- Increases trustworthiness (citations to validated sources)
- Detects and resolves contradictions

**Example**:
```
Query: "What is the recommended dosage of aspirin for heart disease prevention?"

Retrieved Docs:
- Doc A (Blog): "Take 500mg aspirin daily"
- Doc B (Medical Journal): "Take 81mg aspirin daily, consult physician"
- Doc C (Outdated Guideline): "Take 325mg aspirin daily"

Evaluator Agent:
1. Detects contradiction (dosages vary widely)
2. Checks source authority:
   - Doc A: Low authority (blog)
   - Doc B: High authority (peer-reviewed, recent)
   - Doc C: Medium authority (outdated)
3. Cross-checks with latest clinical guidelines
4. Validates: Doc B aligns with current medical consensus

Final Response:
"The recommended dosage is 81mg daily, but consult your physician for personalized advice. [Source: Recent medical journal, 2024]"
```

---

## Advantages of Agentic RAG Over Traditional RAG

| Aspect | Traditional RAG | Agentic RAG | Benefit |
|--------|----------------|-------------|---------|
| **Accuracy** | Single-pass retrieval may miss relevant docs | Multi-pass, validated retrieval | ✅ Higher precision and recall |
| **Contextual Understanding** | Static query embedding | Context-aware query expansion | ✅ Better captures user intent |
| **Adaptability** | Fixed knowledge source (vector DB) | Dynamic source selection | ✅ Optimal source per query type |
| **Validation** | No built-in validation | Evaluator agents cross-check | ✅ Reduces hallucinations, increases trust |
| **Complex Queries** | Struggles with multi-step reasoning | Decomposes into logical steps | ✅ Handles complexity like human research |

---

## When to Use Agentic RAG

### High-Value Use Cases

#### 1. Legal Research
**Why**: Queries require multi-step reasoning, authoritative sources, and contradiction detection.

**Example**:
```
Query: "What are the legal precedents for data privacy violations in healthcare under HIPAA?"

Agentic RAG:
1. Retrieve HIPAA regulations
2. Search for relevant case law
3. Identify precedents from authoritative courts
4. Cross-check for conflicting interpretations
5. Synthesize findings with citations
```

#### 2. Scientific Discovery
**Why**: Constantly evolving knowledge, need for recent updates, cross-validation critical.

**Example**:
```
Query: "What are the latest findings on mRNA vaccine efficacy against COVID-19 variants?"

Agentic RAG:
1. Search recent peer-reviewed studies (last 6 months)
2. Retrieve clinical trial data
3. Cross-check findings across multiple studies
4. Identify consensus and outliers
5. Validate against authoritative health organizations (CDC, WHO)
```

#### 3. Business Intelligence
**Why**: Multi-source data (structured + unstructured), recency matters, validation needed.

**Example**:
```
Query: "Compare our sales performance to competitors in Q3 2024"

Agentic RAG:
1. Retrieve internal sales data (SQL database)
2. Search competitor financial reports (document store)
3. Fetch industry benchmarks (web search)
4. Cross-validate metrics for consistency
5. Synthesize comparative analysis
```

### When Traditional RAG Is Sufficient

**Use Traditional RAG when**:
- Queries are simple and factual ("What is X?")
- Single knowledge source is adequate
- Low-stakes applications (no critical decisions)
- Speed is prioritized over validation
- Budget constraints (agentic RAG is more expensive)

**Example**: FAQ chatbot for product documentation.

---

## Better Search, Better RAG

### Optimize Search BEFORE Adding Agents

**Key Insight**: Improving underlying search quality provides more value than adding agents to poor search.

**Optimization Techniques** (in order of impact):

#### 1. Parse and Chunk Documents

**Problem**: Generic chunking (fixed 512 tokens) loses semantic coherence.

**Solution**: **Vertex AI Layout Parser** for semantic chunking.

**Features**:
- Handles complex document layouts (multi-column, embedded tables)
- Extracts embedded images (charts, diagrams)
- Semantic chunker keeps chunks on-topic
- Hierarchy of headings preserves structure

**Example**:
```
# Bad Chunking (Fixed Size)
Chunk 1: "...end of section on budgets. 3.2 Risk Management Risk management is critical..."
→ Mixes two topics, low coherence

# Good Chunking (Semantic)
Chunk 1: "3.1 Budget Planning [complete section, 400 tokens]"
Chunk 2: "3.2 Risk Management [complete section, 600 tokens]"
→ Each chunk is coherent and self-contained
```

#### 2. Add Metadata to Chunks

**Problem**: Vector search alone can't filter by attributes (date, author, category).

**Solution**: Enrich chunks with metadata for boosting, burying, and filtering.

**Metadata Examples**:
- **Synonyms**: "LLM" → "Large Language Model", "GPT"
- **Keywords**: "Machine Learning", "Natural Language Processing"
- **Authors**: "Yann LeCun", "Andrew Ng"
- **Dates**: "2024-11-14"
- **Tags**: "research", "tutorial", "case-study"
- **Categories**: "Healthcare", "Finance", "Legal"

**Benefits**:
- **Boost**: Prioritize recent documents or authoritative authors
- **Bury**: Deprioritize outdated or low-quality sources
- **Filter**: Restrict search to specific categories or date ranges
- **User/Agent Control**: Allow filtering in query ("Show recent papers on topic X")

**Example**:
```python
chunk_with_metadata = {
    "text": "Agentic RAG improves retrieval accuracy...",
    "metadata": {
        "author": "Google Research",
        "date": "2025-02-01",
        "keywords": ["RAG", "agents", "retrieval"],
        "category": "AI Research",
        "authority_score": 0.95  # High-quality source
    }
}

# Search with metadata filtering
results = vector_search(
    query="Agentic RAG",
    filters={"date": {"gte": "2024-01-01"}, "authority_score": {"gte": 0.9}}
)
```

#### 3. Fine-Tune Embedding Model or Add Search Adaptor

**Problem**: General-purpose embeddings may not capture domain-specific semantics.

**Solution**: Fine-tune embedding model or add search adaptor to adjust embedding space.

**Approach**:
- **Fine-Tuning**: Train embedding model on domain-specific data (medical, legal, financial)
- **Search Adaptor**: Layer on top of embeddings that transforms space for better domain alignment

**Benefits**:
- Domain-specific terms better represented (e.g., "hedging" in finance vs. gardening)
- Improved semantic similarity for specialized vocabularies
- Higher retrieval precision for domain queries

**Example**:
```
Query: "What are the implications of Basel III for risk-weighted assets?"

Generic Embedding:
- May confuse "Basel" (city) with "Basel III" (financial regulation)
- Result: Irrelevant documents about Switzerland

Fine-Tuned Financial Embedding:
- Understands "Basel III" is a banking regulation
- Result: Highly relevant documents on capital requirements
```

#### 4. Use Faster Vector Database

**Problem**: Slow vector search increases latency, limits top-k retrieval.

**Solution**: Upgrade to **Vertex AI Vector Search** for ultra-fast, high-quality retrieval.

**Trade-off**:
- Vector search uses approximate nearest neighbor (ANN)
- Speed vs. accuracy trade-off (faster = less accurate)
- **Vertex AI Vector Search**: Optimizes both speed AND accuracy

**Benefits**:
- Lower latency (sub-100ms for millions of vectors)
- Higher top-k (retrieve 100+ candidates for re-ranking)
- Better quality (more accurate ANN algorithms)

#### 5. Use a Ranker

**Problem**: Vector searches are fast but approximate; top results may not be best.

**Solution**: **Re-rank** top-k results with more sophisticated model.

**How It Works**:
```
1. Vector Search: Retrieve top-100 candidates (fast, approximate)
    ↓
2. Ranker: Re-rank top-100 to find best 10 (slower, more accurate)
    ↓
3. Return top-10 after re-ranking
```

**Ranker Types**:
- **Cross-encoder**: Scores query-document pairs (more accurate, slower)
- **LLM-based ranker**: Uses LLM to score relevance
- **Learning-to-rank**: Trained on click data or human feedback

**Benefits**:
- Top results are highest quality (precision improvement)
- Compensates for approximation errors in vector search
- Can incorporate additional signals (freshness, authority)

**Example**:
```
Query: "How to deploy Kubernetes on AWS?"

Vector Search (Top 5):
1. "AWS EKS Tutorial" (score: 0.89)
2. "Kubernetes Architecture Overview" (score: 0.87)
3. "Deploying Kubernetes on Azure" (score: 0.85)
4. "AWS vs. Azure for Kubernetes" (score: 0.84)
5. "Kubernetes Security Best Practices" (score: 0.83)

After Re-Ranking (Cross-Encoder):
1. "AWS EKS Tutorial" (score: 0.95) ← Still #1, higher confidence
2. "AWS vs. Azure for Kubernetes" (score: 0.91) ← Jumped from #4
3. "Kubernetes Architecture Overview" (score: 0.78) ← Dropped to #3
...
```

#### 6. Implement Check Grounding

**Problem**: LLM may generate text not supported by retrieved documents (hallucination).

**Solution**: **Grounding check** ensures each phrase is citable.

**How It Works**:
```python
generated_response = "The Eiffel Tower is 324 meters tall and was completed in 1889."

# Check grounding for each claim
claims = [
    "The Eiffel Tower is 324 meters tall",
    "The Eiffel Tower was completed in 1889"
]

for claim in claims:
    is_grounded = check_if_supported_by_chunks(claim, retrieved_chunks)
    if not is_grounded:
        flag_as_ungrounded(claim)

# Result: Both claims are grounded in retrieved documents ✅
```

**Benefits**:
- Prevents hallucinations in generated responses
- Increases trust (all claims are cited)
- Enables fact-checking (show sources for each claim)

---

## Google Tools for Search Optimization

### Vertex AI Search

**Description**: Google-quality search for your enterprise data.

**Features**:
- All 6 optimization techniques built-in (no development time)
- Semantic chunking, metadata enrichment, fast vector search, rankers, grounding checks
- Automatic data refresh, access control, scalability

**Use Case**: Enterprises wanting production-ready search without building from scratch.

**Reference**: https://cloud.google.com/enterprise-search

### Search Builder APIs

**Description**: Standalone APIs for developers building custom search engines.

**Components**:
- Layout Parser API
- Embedding API (with fine-tuning)
- Vector Search API
- Ranker API
- Grounding Check API

**Use Case**: Developers who want control over each component.

**Reference**: https://cloud.google.com/generative-ai-app-builder/docs/builder-apis

### RAG Engine

**Description**: LlamaIndex-like Python interface for orchestrating RAG pipelines.

**Features**:
- Python-based API for chaining components
- Integrates with Vertex AI Search and Builder APIs
- Supports custom retrieval logic

**Use Case**: Data scientists and ML engineers building experimental RAG systems.

**Reference**: https://cloud.google.com/vertex-ai/generative-ai/docs/rag-overview

---

## Implementation Roadmap

### Stage 1: Optimize Traditional RAG
1. ✅ Implement semantic chunking (Vertex AI Layout Parser)
2. ✅ Add metadata to chunks (keywords, dates, categories)
3. ✅ Fine-tune embeddings for domain (if needed)
4. ✅ Upgrade to fast vector database (Vertex AI Vector Search)
5. ✅ Add re-ranker for top-k results
6. ✅ Implement grounding checks

**Goal**: Achieve high baseline RAG performance before adding agents.

### Stage 2: Add Agentic Capabilities
1. ✅ Implement query expansion (retrieval agent generates multiple queries)
2. ✅ Add multi-step reasoning (decompose complex queries)
3. ✅ Implement adaptive source selection (vector DB, SQL, web search)
4. ✅ Add evaluator agent (validate retrieved knowledge)

**Goal**: Handle complex, ambiguous, multi-step queries with validation.

### Stage 3: Production Deployment
1. ✅ Instrument observability (see Topic 1: AgentOps)
2. ✅ Set up evaluation (trajectory + response, see Topic 2)
3. ✅ Human-in-the-loop validation
4. ✅ A/B test against baseline RAG

**Goal**: Ensure agentic RAG provides measurable improvement over baseline.

---

## Key Takeaways

1. **Agentic RAG** introduces autonomous retrieval agents for iterative, validated search
2. **Four innovations**: Query expansion, multi-step reasoning, adaptive sources, validation
3. **Optimize search first**: Semantic chunking, metadata, rankers before adding agents
4. **Use cases**: Legal, scientific, business intelligence (complex, high-stakes queries)
5. **Google tools**: Vertex AI Search (turnkey), Builder APIs (custom), RAG Engine (orchestration)
6. **Implementation**: Baseline RAG → Agentic capabilities → Production (with eval and observability)

---

## Related Topics

- **Topic 1**: AgentOps & Operations (observability for agentic RAG)
- **Topic 2**: Agent Evaluation Methodology (evaluating retrieval quality)
- **Topic 3**: Multi-Agent Architectures (retriever agents as part of multi-agent systems)
- **Topic 5**: Enterprise Applications (Google Agentspace uses agentic RAG)

---

## References

- Figure 9: Agentic RAG diagram from Vectorize.io
- Figure 10: RAG and search components (Vertex AI Search, RAG Engine)
- Vectorize blog: "How I finally got agentic RAG to work right"
- Vertex AI Search: https://cloud.google.com/enterprise-search
- Search Builder APIs: https://cloud.google.com/generative-ai-app-builder/docs/builder-apis
- RAG Engine: https://cloud.google.com/vertex-ai/generative-ai/docs/rag-overview

---

**Next Topic**: [Enterprise Applications](05_Enterprise_Applications.md)
