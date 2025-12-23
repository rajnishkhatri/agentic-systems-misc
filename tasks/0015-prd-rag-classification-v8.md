# PRD: RAG Classification Prototype (V8)

## 1. Introduction
This document defines the requirements for the **RAG Classification Prototype (V8)**. This phase introduces Retrieval-Augmented Generation (RAG) to the dispute classification workflow. Instead of relying solely on the LLM's internal reasoning (as in V5-ToT or V7-Hybrid), V8 retrieves semantically similar historical disputes from a "Golden Set" to provide the model with verified precedents. This "Stripe-inspired" pattern aims to resolve ambiguity and improve consistency by grounding decisions in actual past examples.

## 2. Problem Understanding

### Core Problem
Dispute descriptions are often vague, emotional, or ambiguous. Pure reasoning models (CoT/ToT) sometimes hallucinate or misinterpret these edge cases. Human analysts solve this by looking up "how we handled similar cases before." The current system lacks this "institutional memory."

### Key Constraints
- **Latency:** Retrieval must be fast (<200ms) to not bottleneck the flow.
- **Local Execution:** Must run locally without external vector DB dependencies for this prototype.
- **Model Size:** Embedding model must be lightweight (e.g., `all-MiniLM-L6-v2`).
- **Data Source:** Must use the existing verified "Golden Set" (`natural_language_classification_v2.json`).

### Assumptions
- The Golden Set covers enough diversity to be useful as a knowledge base.
- `sentence-transformers` library is compatible with the current environment.
- Providing 3-5 similar examples fits within the LLM's context window.

### Success Criteria
- **Functional:** System retrieves relevant examples for a given dispute.
- **Performance:** V8 accuracy >= V7-Hybrid on ambiguous cases.
- **Consistency:** Reduced variance in classifying "grey area" disputes.

## 3. Goals
1.  **Implement Vector Search:** Enable semantic search over historical dispute data.
2.  **Augment Prompt:** Inject retrieved "nearest neighbors" into the classification prompt.
3.  **Benchmark:** Compare V8 (RAG) performance against V7 (Hybrid) and V5 (ToT).

## 4. Strategic Approach

### Strategy: Decomposition & Analogy
We are applying the **Analogy** heuristic (solving problems by looking at similar solved problems) literally within the architecture.
We use **Decomposition** to break the feature into:
1.  **Offline:** Vector Store Construction (Embeddings).
2.  **Online:** Retrieval Logic (Query Embedding -> KNN Search).
3.  **Integration:** Prompt augmentation and Phase logic.

### Recommended Heuristics
- **Pre-computation:** Compute embeddings for the knowledge base once (offline) to save runtime latency.
- **K-Nearest Neighbors (KNN):** Simple, effective retrieval for this scale (<10k items).

## 5. User Stories
- **As a Developer**, I want the system to automatically find past disputes that look like the current one, so the LLM has better context.
- **As an Analyst**, I want the AI to cite "similar past cases" as part of its reasoning, so I can trust its decision.

## 6. Functional Requirements

### 6.1 Vector Store Management
- **FR-1:** Script to load `natural_language_classification_v2.json`.
- **FR-2:** Generate embeddings for `description` fields using `all-MiniLM-L6-v2`.
- **FR-3:** Persist embeddings + metadata (Reason Code, Category) to a local file (`vector_store.pkl`).

### 6.2 Retrieval Adapter
- **FR-4:** `RagRetriever` class that loads the vector store on initialization.
- **FR-5:** `retrieve_similar(query, k)` method returning top-k matches with similarity scores.
- **FR-6:** Filter/thresholding (optional) to ignore irrelevant matches (score < 0.4).

### 6.3 Classification Phase (V8)
- **FR-7:** `ClassifyV8Rag` phase inheriting from base phase.
- **FR-8:** Call `RagRetriever` before prompt generation.
- **FR-9:** Inject retrieved examples into the system prompt under `## Similar Historical Cases`.
- **FR-10:** Parse standard classification output (same schema as V7).

## 7. Technical Considerations

### Dependencies
- `sentence-transformers`: For local embedding generation.
- `scikit-learn`: For cosine similarity/KNN (or manual implementation using numpy).
- `pickle`: For simple serialization of the vector store.

### Data Flow
1.  **Build Time:** JSON -> [Embedding Model] -> Vectors -> PKL.
2.  **Run Time:** User Query -> [Embedding Model] -> Query Vector -> [KNN Search vs PKL] -> Top K Examples -> [Prompt Template] -> LLM.

### Watch For
- **Memory Usage:** Loading large embedding models or vector stores into memory. (Mitigation: MiniLM is small; dataset is small).
- **Context Limit:** Retrieving too many long examples might overflow context. (Mitigation: Truncate descriptions, limit k=3).
- **Data Leakage:** Ensure the "query" dispute isn't in the vector store (if testing on Golden Set). For prototype, we accept this risk or handle via cross-validation later.

## 8. Validation Gates

### Gate 1: Embeddings
- Verify `build_vector_store.py` produces a `.pkl` file.
- Verify vectors have correct dimensions (384 for MiniLM).

### Gate 2: Retrieval Quality
- Test `RagRetriever` with a known query.
- Visually confirm retrieved examples are semantically relevant.

### Gate 3: End-to-End Flow
- Run `ClassifyV8Rag` on a sample dispute.
- Check logs to confirm examples were injected into the prompt.
- Verify output follows the JSON schema.

## 9. Success Metrics
- **Retrieval Latency:** < 200ms (p95).
- **Classification Accuracy:** Track against V7 baseline.

## 10. Open Questions
- Should we filter by "Network" (Visa/Amex) strictly, or let the semantic similarity handle it? *Decision: Let semantic similarity handle it for now; mix of networks might be useful.*

