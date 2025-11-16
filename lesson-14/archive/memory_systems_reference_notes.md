# Memory Systems Reference Notes

Working notebook for Task 1.0 to keep canonical citations, metrics, and integration hooks before drafting `memory_systems_fundamentals.md`.

## 1. `agents_memory.txt` Highlights

### 1.1 Key Terminology

| Memory Type | Definition (summarized) | Example(s) | Citation |
| --- | --- | --- | --- |
| Working | Short-term buffer that persists recent turns across calls, essentially stored chat history. | Conversation window reused across user/assistant turns. | `agents_memory.txt` lines 22-23 |
| Episodic | Records specific past events/actions and their outcomes. | Remembering last execution step or user feedback. | lines 26-28 |
| Semantic | World knowledge pulled from external stores (e.g., Wikipedia, product docs). | Codebase lookup for coding agent. | lines 29-31 |
| Procedural | Know-how for how to act; often lives in parameters/system prompt. | Python coding habits, tool invocation sequences. | lines 32-33 |
| Parametric | Inherent model weights that store facts without explicit memory modules. | Remembering “Paris is capital of France”. | lines 38-39 |

### 1.2 Short-Term vs. Long-Term Distinctions

- Short-term memory = current conversation history / context window; limited capacity, no persistence, requires trimming or summarization once token budget exceeded. `agents_memory.txt` lines 42-82.
- Long-term memory = external stores (vector DB, knowledge graphs, archives) for episodic, semantic, procedural recall; persists beyond session but adds retrieval latency (50-200 ms) and complexity. lines 83-105.

### 1.3 Context Engineering References

- Defines context engineering as optimizing total context, not just prompt, to maximize output quality. `agents_memory.txt` lines 194-217.
- Highlights million-token contexts (Gemini 1.5) but warns against “context rot”; quality beats stuffing. lines 218-236.
- Frames context engineering as architectural balance: choose right info, format, ordering; references techniques like MemoryBank & Search-o1 as enablers. lines 236-242.

### 1.4 Concrete Examples to Cite

- Flamingo preference example illustrates why chat history must be explicitly replayed; short-term memory fails otherwise. lines 44-48.
- Context window overflow scenario (Figures 4-7 to 4-9) demonstrates need for trimming/summary. lines 50-71.
- Search-o1 walkthrough shows Reason-in-Documents compression and flamingo diet example for long-term retrieval. lines 176-192.
- Context-as-specification section emphasizes PLAN.md, REQUIREMENTS.md as part of agent memory. lines 245-312.

## 2. `compass_artifact_wf-cb8f6aa3-09f0-42eb-a1e8-141e989476d2_text_markdown.md` Metrics

### 2.1 Vector Database Benchmarks

| DB | Deployment & Features | P95 Latency / QPS (1M vectors, 768-dim) | Cost per 1M vectors & 1K q/day | Citation |
| --- | --- | --- | --- | --- |
| Pinecone | Fully managed, auto-scaling, 99.9% SLA. | 100 ms @ 1000 QPS | \$150-200/month (managed) | lines 59-65 |
| Weaviate | OSS + cloud, hybrid search, GDPR-friendly. | 120 ms @ 900 QPS | \$100-150 cloud, \$50-80 self-host | lines 59-65 |
| Chroma | OSS, embeddable, Python-native prototyping. | 150 ms @ 500 QPS | Free-\$50 | lines 59-65 |
| Qdrant | OSS/cloud, complex filtering, payload indexing. | 90 ms @ 1100 QPS | \$80-120 | lines 59-65 |
| Milvus | OSS, distributed, peak throughput. | 80 ms @ 1500 QPS | \$100-200 | lines 59-65 |
| pgvector | PostgreSQL extension leveraging existing infra. | Depends on Postgres (not benchmarked) | Infra costs only | lines 59-65 |

### 2.2 Cost / ROI Anchors

- Token cost progression example (GPT-4 8K context, 100 turns): no management = \$24; 50% compression = \$12; selective retrieval (20% context) = \$4.80 (80% savings). Recommendation: summarize first (40-60%), add selective retrieval later, multi-agent isolation only when needed (15× cost). line 77.
- Same scenario reiterated under context window management best practices. line 339.

### 2.3 Memory Implementation Considerations

- Short-term memory strategies: circular buffers, sliding windows, Redis TTL; zero retrieval latency but bounded capacity & rising token costs. lines 49-51.
- Long-term memory strategies: summarization, vector DBs, knowledge graphs, archives; unlimited capacity but adds 50-200 ms retrieval latency and higher ops cost. lines 51-55.
- Redis Agent Memory Server pattern hits <5 ms for hot data vs. 50-200 ms for vector retrieval, highlighting hybrid approach. line 55.

### 2.4 Latency & Pipeline Benchmarks

- Typical RAG latency stack: embeddings 20-50 ms, vector search 50-200 ms, retrieval 10-30 ms, reranking 50-100 ms, LLM generation 500-2000 ms for total 630 ms–2.4 s; caching and streaming recommended. line 89.
- Parallel tool execution (ReWOO) cuts latency 50-70% when tools are independent. line 209.

### 2.5 Production Deployment & Safety Insights

- Three-layer guardrail architecture (pre-training filters, in-model RLHF/Constitutional AI, post-processing rules/LLM) with 15-50 ms overhead on final stage. lines 237-243.
- Monitoring stack recommendation: LangSmith/Langfuse (qualitative traces) + Prometheus (quant metrics) + Grafana (visualization) with alerts on 2σ deviations. lines 261-269.
- Key metrics to track: performance, quality, safety, business ROI; ensures notebook outputs map cleanly to dashboard schema later. lines 253-269.

## 3. `04_Agentic_RAG.md` Integration Notes

- Structure: Overview + Traditional vs Agentic RAG (lines 9-114), “When to Use Agentic RAG” (lines 348-406), “Better Search, Better RAG” optimization checklist (lines 410-598). Forward reference to memory tutorial should slot near the “When Traditional RAG Is Sufficient” concluding bullets (lines 399-406) or immediately before “Better Search, Better RAG” to maintain narrative flow.
- Cross-reference style: uses inline Markdown links plus descriptive sentences (e.g., “Example:” blocks). Mirror this when adding “Deep Dive: Memory Systems Implementation” later.
- Key recap targets for Section 1.3: highlight differences between single-pass RAG and agentic loops (lines 17-214), mention Evaluator Agent validation (lines 271-333), and route readers back here via `See also: lesson-14/04_Agentic_RAG.md` text.

