# End-to-End RAG Evaluation

**Reading Time:** 18-22 minutes
**Prerequisites:** [HW4: RAG Evaluation](../homeworks/hw4/TUTORIAL_INDEX.md), [Attribution Evaluation](./attribution_evaluation.md), [Hallucination Detection](./hallucination_detection_rag.md)
**Next Steps:** [Attribution Detection Notebook](./attribution_detection.ipynb), [Context Utilization Notebook](./context_utilization.ipynb)

---

## Table of Contents

1. [Introduction](#introduction)
2. [The RAG Evaluation Challenge](#the-rag-evaluation-challenge)
3. [Component-Wise vs End-to-End Evaluation](#component-wise-vs-end-to-end-evaluation)
4. [RAG Failure Mode Taxonomy](#rag-failure-mode-taxonomy)
5. [Context Utilization Measurement](#context-utilization-measurement)
6. [Answer Correctness vs Answer Quality](#answer-correctness-vs-answer-quality)
7. [Holistic RAG Metrics](#holistic-rag-metrics)
8. [Production Monitoring Strategies](#production-monitoring-strategies)
9. [Building a RAG Evaluation Pipeline](#building-a-rag-evaluation-pipeline)
10. [Real-World RAG Evaluation](#real-world-rag-evaluation)

---

## Introduction

Evaluating RAG systems is uniquely challenging because **performance depends on two interdependent stages**:

1. **Retrieval:** Finding relevant documents
2. **Generation:** Producing accurate, faithful responses

A failure in either stage (or the interaction between them) causes poor final answers. Traditional evaluation focuses on individual components, but **what matters is end-to-end performance**.

In this tutorial, you'll learn:
- How to evaluate RAG systems holistically (retrieval + generation)
- The taxonomy of RAG failure modes and their root causes
- Techniques for measuring context utilization (which docs LLM actually uses)
- The difference between answer correctness and answer quality
- Production monitoring strategies for deployed RAG systems
- How to build automated RAG evaluation pipelines

---

## The RAG Evaluation Challenge

### The Multi-Stage Problem

```
┌─────────┐      ┌──────────┐      ┌────────────┐
│  Query  │ ───> │ Retrieval│ ───> │ Generation │ ───> Response
└─────────┘      └──────────┘      └────────────┘
                      ↓                    ↓
                 Context Quality      Faithfulness
                 (Recall@k, MRR)     (Attribution, Hallucination)
```

**Problem:** Good retrieval doesn't guarantee good responses.

**Examples:**

| Retrieval Quality | Generation Quality | Final Response |
|------------------|-------------------|----------------|
| ✅ High (Recall@5=100%) | ✅ High (Faithful) | ✅ GOOD |
| ✅ High (Recall@5=100%) | ❌ Low (Hallucination) | ❌ BAD |
| ❌ Low (Recall@5=20%) | ✅ High (Faithful) | ❌ BAD (limited info) |
| ❌ Low (Recall@5=20%) | ❌ Low (Ignores context) | ❌ VERY BAD |

**Key Insight:** Optimizing components independently can hurt end-to-end performance.

---

### Example: Retrieval-Generation Trade-Off

**Scenario:** Recipe Q&A System

**Query:** "How do I make gluten-free carbonara?"

**Retrieval Settings:**

**Option A: High Precision (Top-3)**
- Retrieves 3 highly relevant documents (all mention "gluten-free pasta")
- Recall@3 = 60% (misses some relevant docs)
- **Generation Result:** Accurate but incomplete (missing tips)

**Option B: High Recall (Top-10)**
- Retrieves 10 documents (includes some tangentially related)
- Recall@10 = 100% (gets all relevant docs)
- **Generation Result:** Response includes irrelevant info (distracted by off-topic docs)

**Trade-Off:**
- More context → Better retrieval recall, but harder for LLM to synthesize
- Less context → Clearer for LLM, but might miss important information

**Optimal Strategy:** Balance retrieval coverage with generation capacity.

---

## Component-Wise vs End-to-End Evaluation

### Component-Wise Evaluation (Traditional)

**Evaluate retrieval and generation separately:**

```python
# Retrieval metrics (from HW4)
retrieval_metrics = {
    "recall@3": 0.85,
    "recall@5": 0.92,
    "MRR": 0.78,
    "precision@3": 0.67
}

# Generation metrics (from Lesson 13)
generation_metrics = {
    "attribution_rate": 0.88,
    "faithfulness_score": 0.91,
    "hallucination_rate": 0.09
}
```

**Advantages:**
- Easy to debug (isolate failures)
- Can optimize each stage independently
- Clear performance baselines

**Disadvantages:**
- Doesn't measure end-to-end quality
- Misses interaction effects
- Component improvements may not improve final answers

---

### End-to-End Evaluation (Holistic)

**Evaluate the complete RAG pipeline:**

```python
# End-to-end metrics
e2e_metrics = {
    "answer_correctness": 0.82,  # vs gold standard
    "answer_completeness": 0.76,  # covers all aspects
    "answer_relevance": 0.89,  # addresses query
    "context_utilization": 0.71,  # % retrieved docs used
    "response_time": 2.3,  # seconds
    "cost_per_query": 0.012  # USD
}
```

**Advantages:**
- Measures what users care about (final answer quality)
- Captures interaction effects between stages
- Reflects production performance

**Disadvantages:**
- Harder to debug failures
- Requires gold standard answers
- More expensive to evaluate

---

### Hybrid Approach: Component + E2E

**Best Practice:** Evaluate both dimensions.

```
Evaluation Strategy:
1. Component Metrics (fast, cheap):
   - Retrieval: Recall@k, MRR, nDCG
   - Generation: Attribution rate, faithfulness

2. End-to-End Metrics (slower, comprehensive):
   - Answer correctness (vs gold labels)
   - Answer quality (AI-as-judge)
   - User satisfaction (human eval)

3. Correlation Analysis:
   - Which component metrics predict E2E quality?
   - When do retrieval improvements help generation?
```

**Example Analysis:**

```
Correlation Study (500 queries):

Retrieval Recall@5 vs Answer Correctness: r=0.62 (moderate)
Attribution Rate vs Answer Correctness: r=0.81 (strong)
Context Utilization vs Answer Quality: r=0.74 (strong)

Insight: Generation quality matters more than retrieval
coverage for this domain.
```

---

## RAG Failure Mode Taxonomy

### The Four Categories of RAG Failures

```
┌────────────────────────────────────────────────┐
│             RAG Failure Modes                  │
├────────────────────────────────────────────────┤
│                                                │
│  1. RETRIEVAL FAILURES                         │
│     ├─ Missing Relevant Docs (Low Recall)     │
│     ├─ Irrelevant Docs Retrieved (Low Precision)│
│     └─ Incorrect Ranking (Low MRR)            │
│                                                │
│  2. GENERATION FAILURES                        │
│     ├─ Hallucination (Intrinsic/Extrinsic)   │
│     ├─ Context Ignored (Low Utilization)      │
│     └─ Poor Synthesis (Doesn't combine docs)  │
│                                                │
│  3. INTERACTION FAILURES                       │
│     ├─ Context Overwhelm (Too many docs)      │
│     ├─ Context Conflict (Contradictory docs)  │
│     └─ Context Truncation (Exceeds token limit)│
│                                                │
│  4. QUERY UNDERSTANDING FAILURES               │
│     ├─ Ambiguous Query (Multiple interpretations)│
│     ├─ Multi-Hop Query (Needs multiple sources)│
│     └─ Out-of-Distribution Query (No relevant docs)│
│                                                │
└────────────────────────────────────────────────┘
```

---

### Failure Mode 1: Retrieval Failures

**Symptom:** Response is incomplete or wrong due to missing information.

**Example:**
```
Query: "What temperature should I bake carbonara at?"
(Note: Carbonara is not baked, it's a pasta dish)

Retrieved Docs: [Various baked pasta casserole recipes]

Response: "Bake carbonara at 375°F for 30 minutes."

Failure: RETRIEVAL (retrieved wrong type of dish)
Root Cause: Query misunderstood as "baked pasta" instead of "carbonara"
```

**Detection:**
```python
# Check if retrieved docs contain query keywords
def detect_retrieval_failure(query: str, retrieved_docs: list[str]) -> dict:
    query_keywords = extract_keywords(query)
    doc_keywords = [extract_keywords(doc) for doc in retrieved_docs]

    overlap = [
        len(set(query_keywords) & set(doc_kw)) / len(query_keywords)
        for doc_kw in doc_keywords
    ]

    avg_overlap = sum(overlap) / len(overlap) if overlap else 0.0

    return {
        "likely_retrieval_failure": avg_overlap < 0.3,
        "avg_keyword_overlap": avg_overlap,
        "recommendation": "Improve query rewriting or retrieval strategy"
    }
```

---

### Failure Mode 2: Generation Failures

**Symptom:** Retrieval is good, but LLM generates poor response.

**Example:**
```
Query: "How long to cook pasta for carbonara?"

Retrieved Docs:
[Doc 1]: "Cook pasta 7-9 minutes until al dente."
[Doc 2]: "Carbonara uses spaghetti or rigatoni."

Response: "Cook pasta for 12-15 minutes until fully soft. Carbonara
traditionally uses penne pasta."

Failure: GENERATION
- Intrinsic Hallucination: "12-15 minutes" contradicts "7-9 minutes"
- Intrinsic Hallucination: "penne" contradicts "spaghetti or rigatoni"
Root Cause: LLM ignored context, used parametric knowledge
```

**Detection:**
```python
def detect_generation_failure(response: str, context: list[str]) -> dict:
    # Check for hallucinations
    hallucination_result = detect_hallucination(response, context)

    # Check for context utilization
    utilization_result = measure_context_utilization(response, context)

    return {
        "likely_generation_failure": (
            hallucination_result["has_hallucination"]
            or utilization_result["utilization_rate"] < 0.5
        ),
        "hallucination_detected": hallucination_result,
        "context_utilization": utilization_result,
        "recommendation": "Improve generation prompt or model"
    }
```

---

### Failure Mode 3: Interaction Failures

**Symptom:** Both retrieval and generation work in isolation, but fail when combined.

**Example: Context Overwhelm**
```
Query: "Summarize the Bhagavad Gita's main teachings"

Retrieved Docs: [All 18 chapter summaries, 50 verses, 20 commentaries]
(Total: 15,000 tokens)

Response: "The Bhagavad Gita teaches dharma, karma, and yoga. It
is a conversation between Arjuna and Krishna..."

Failure: INTERACTION (too much context, LLM summarizes poorly)
Root Cause: Retrieved too many docs, exceeds LLM synthesis capacity
```

**Detection:**
```python
def detect_interaction_failure(
    query: str,
    context: list[str],
    response: str,
    max_context_tokens: int = 8000
) -> dict:
    total_context_tokens = sum(count_tokens(doc) for doc in context)

    # Check for contradictory context
    contradictions = find_contradictions_in_context(context)

    # Check for context truncation
    was_truncated = total_context_tokens > max_context_tokens

    return {
        "likely_interaction_failure": (
            total_context_tokens > max_context_tokens * 0.8
            or len(contradictions) > 0
        ),
        "context_tokens": total_context_tokens,
        "context_truncated": was_truncated,
        "contradictions_in_context": contradictions,
        "recommendation": "Reduce context or implement reranking"
    }
```

---

### Failure Mode 4: Query Understanding Failures

**Symptom:** System misinterprets query intent.

**Example: Ambiguous Query**
```
Query: "How do I use salt in cooking?"

Interpretation 1: Techniques for salting food
Interpretation 2: How much salt to use
Interpretation 3: Types of salt (kosher, sea salt, etc.)

Retrieved Docs: Mix of all three interpretations

Response: Confused answer mixing all three topics

Failure: QUERY UNDERSTANDING (ambiguous intent)
Root Cause: System doesn't ask for clarification
```

**Detection:**
```python
def detect_query_failure(query: str, response: str, context: list[str]) -> dict:
    # Check query specificity
    specificity_score = calculate_query_specificity(query)

    # Check if response addresses query
    relevance_score = calculate_response_relevance(query, response)

    # Check for multi-hop requirement
    requires_multi_hop = detect_multi_hop_query(query)

    return {
        "likely_query_failure": (
            specificity_score < 0.4
            or relevance_score < 0.5
        ),
        "query_specificity": specificity_score,
        "response_relevance": relevance_score,
        "requires_multi_hop": requires_multi_hop,
        "recommendation": "Implement query classification or clarification"
    }
```

---

## Context Utilization Measurement

**Definition:** Context utilization measures **which retrieved documents the LLM actually uses** in its response.

### Why Measure Context Utilization?

**Problem:** Retrieval returns 5 documents, but LLM only uses 1.

**Implications:**
- Wasted retrieval effort (4 irrelevant docs fetched)
- Wasted cost (processed but unused context)
- Potential distraction (irrelevant docs confuse LLM)

**Goal:** Maximize context utilization (use all relevant docs) while minimizing noise.

---

### Measuring Context Utilization

#### Method 1: Semantic Similarity

```python
def measure_context_utilization_semantic(
    response: str,
    retrieved_docs: list[str]
) -> dict:
    """
    Measure which docs LLM used based on semantic similarity.

    Strategy: If response is highly similar to a doc, LLM likely used it.
    """
    response_embedding = get_embedding(response)

    utilization = []
    for i, doc in enumerate(retrieved_docs):
        doc_embedding = get_embedding(doc)
        similarity = cosine_similarity(response_embedding, doc_embedding)

        # Threshold: similarity > 0.6 indicates usage
        utilization.append({
            "doc_id": i,
            "similarity": similarity,
            "likely_used": similarity > 0.6
        })

    utilization_rate = sum(1 for u in utilization if u["likely_used"]) / len(retrieved_docs)

    return {
        "utilization_rate": utilization_rate,
        "docs_used": [u["doc_id"] for u in utilization if u["likely_used"]],
        "docs_ignored": [u["doc_id"] for u in utilization if not u["likely_used"]],
        "details": utilization
    }
```

**Interpretation:**
- **Utilization Rate > 0.7:** LLM effectively synthesizes multiple docs
- **Utilization Rate 0.3-0.7:** LLM selectively uses some docs
- **Utilization Rate < 0.3:** LLM ignores most retrieved docs (problem!)

---

#### Method 2: Lexical Overlap

```python
def measure_context_utilization_lexical(
    response: str,
    retrieved_docs: list[str]
) -> dict:
    """
    Measure utilization based on n-gram overlap.
    """
    response_ngrams = extract_ngrams(response, n=3)

    utilization = []
    for i, doc in enumerate(retrieved_docs):
        doc_ngrams = extract_ngrams(doc, n=3)

        # Calculate Jaccard similarity
        overlap = len(response_ngrams & doc_ngrams)
        jaccard = overlap / len(response_ngrams | doc_ngrams)

        utilization.append({
            "doc_id": i,
            "jaccard_similarity": jaccard,
            "likely_used": jaccard > 0.1
        })

    return {
        "utilization_rate": sum(1 for u in utilization if u["likely_used"]) / len(retrieved_docs),
        "details": utilization
    }
```

---

#### Method 3: LLM-as-Judge

```python
def measure_context_utilization_judge(
    response: str,
    retrieved_docs: list[str]
) -> dict:
    """
    Use LLM to determine which docs were actually used.
    """
    prompt = f"""
You are an expert at identifying source usage in generated text.

Retrieved Documents:
{format_docs_with_ids(retrieved_docs)}

Generated Response:
{response}

For each document, determine if the response uses information from it.
Answer YES if response contains facts/ideas from the document.
Answer NO if document wasn't referenced.

Output JSON:
{{
    "doc_usage": [
        {{"doc_id": 0, "used": true/false, "evidence": "quote from response"}},
        ...
    ]
}}
"""

    result = llm_call(prompt, temperature=0.0)
    parsed = json.loads(result)

    utilization_rate = sum(1 for d in parsed["doc_usage"] if d["used"]) / len(retrieved_docs)

    return {
        "utilization_rate": utilization_rate,
        "docs_used": [d["doc_id"] for d in parsed["doc_usage"] if d["used"]],
        "details": parsed["doc_usage"]
    }
```

**Accuracy:** LLM-as-judge is most accurate but also most expensive.

---

### Visualizing Context Utilization

**Context Utilization Heatmap:**

```
Query: "How to make carbonara?"

Retrieved Docs:      Utilization Score:
┌─────────────────┐  ┌─────────┐
│ [Doc 1] Recipe  │  │ █████   │ 0.92 ✅ USED
│ [Doc 2] History │  │ ██      │ 0.15 ❌ IGNORED
│ [Doc 3] Variants│  │ ████    │ 0.67 ✅ USED
│ [Doc 4] Nutrition│ │ █       │ 0.08 ❌ IGNORED
│ [Doc 5] Tips    │  │ ██████  │ 0.88 ✅ USED
└─────────────────┘  └─────────┘

Utilization Rate: 60% (3/5 docs used)

Recommendation: Docs 2 and 4 are irrelevant. Improve retrieval precision.
```

---

## Answer Correctness vs Answer Quality

### The Distinction

**Answer Correctness:** Factual accuracy compared to gold standard.

**Answer Quality:** Broader assessment including completeness, clarity, helpfulness.

---

### Answer Correctness (Objective)

**Requires:** Gold standard reference answers.

**Metrics:**
- **Exact Match:** Response matches reference exactly (strict)
- **Fuzzy Match:** Response substantially matches reference (flexible)
- **BLEU/ROUGE:** N-gram overlap (from machine translation)
- **Semantic Equivalence:** Embeddings similarity (captures paraphrasing)

**Example:**
```
Query: "How many chapters in the Bhagavad Gita?"

Reference Answer: "The Bhagavad Gita has 18 chapters."

Response A: "The Bhagavad Gita has 18 chapters."
Correctness: 100% (exact match)

Response B: "It contains 18 chapters."
Correctness: 95% (semantically equivalent, missing subject)

Response C: "The Gita has 16 chapters."
Correctness: 0% (factually wrong)
```

---

### Answer Quality (Subjective)

**Evaluation Dimensions:**

1. **Completeness:** Does response cover all aspects of query?
2. **Relevance:** Does response directly address query?
3. **Clarity:** Is response easy to understand?
4. **Conciseness:** Response not overly verbose?
5. **Helpfulness:** Does response provide actionable information?

**Example:**
```
Query: "How do I make gluten-free carbonara?"

Response A: "Use gluten-free pasta."
- Correctness: ✅ TRUE
- Completeness: ❌ LOW (missing cooking steps)
- Quality Score: 40/100

Response B: "To make gluten-free carbonara, use gluten-free pasta
(spaghetti or rigatoni). Cook pasta al dente, then combine with
guanciale, eggs, Pecorino, and pepper. The gluten-free pasta texture
may differ slightly, so adjust cooking time by 1-2 minutes."
- Correctness: ✅ TRUE
- Completeness: ✅ HIGH (covers pasta choice, steps, tips)
- Quality Score: 92/100
```

---

### Measuring Answer Quality

```python
def evaluate_answer_quality(
    query: str,
    response: str,
    reference: str = None
) -> dict:
    """
    Evaluate answer quality using LLM-as-judge.
    """
    prompt = f"""
Query: {query}
Response: {response}
{f'Reference Answer: {reference}' if reference else ''}

Evaluate the response on these dimensions (score 1-5):

1. **Relevance**: Does response address the query?
2. **Completeness**: Does response cover all aspects?
3. **Clarity**: Is response easy to understand?
4. **Accuracy**: Is response factually correct?
5. **Conciseness**: Response not overly verbose?

Output JSON:
{{
    "relevance": 1-5,
    "completeness": 1-5,
    "clarity": 1-5,
    "accuracy": 1-5,
    "conciseness": 1-5,
    "overall_score": 1-5,
    "strengths": ["strength 1", ...],
    "weaknesses": ["weakness 1", ...],
    "explanation": "brief justification"
}}
"""

    result = llm_call(prompt, model="gpt-4o", temperature=0.0)
    return json.loads(result)
```

---

## Holistic RAG Metrics

### The RAG Scorecard

Comprehensive evaluation across all dimensions:

```python
class RAGEvaluator:
    def evaluate(self, query: str, response: str, context: list[str], reference: str = None) -> dict:
        """
        Comprehensive RAG evaluation.

        Returns scorecard with retrieval, generation, and E2E metrics.
        """
        return {
            # Retrieval Metrics (from HW4)
            "retrieval": {
                "recall@5": self.calculate_recall(context, reference_docs),
                "precision@5": self.calculate_precision(context, reference_docs),
                "MRR": self.calculate_mrr(context, reference_docs)
            },

            # Generation Metrics (from Lesson 13)
            "generation": {
                "attribution_rate": self.calculate_attribution(response, context),
                "faithfulness_score": self.calculate_faithfulness(response, context),
                "hallucination_detected": self.detect_hallucination(response, context)
            },

            # Context Utilization
            "context_utilization": {
                "utilization_rate": self.measure_utilization(response, context),
                "docs_used": self.get_used_docs(response, context)
            },

            # End-to-End Metrics
            "answer_quality": {
                "correctness": self.evaluate_correctness(response, reference),
                "completeness": self.evaluate_completeness(response, query),
                "relevance": self.evaluate_relevance(response, query),
                "overall_score": self.evaluate_overall(response, query, reference)
            },

            # Efficiency Metrics
            "efficiency": {
                "latency_ms": self.measure_latency(),
                "cost_usd": self.calculate_cost(),
                "tokens_used": self.count_tokens()
            },

            # Overall Verdict
            "overall_verdict": self.determine_verdict(all_metrics),
            "failure_mode": self.diagnose_failure(all_metrics) if failure else None
        }
```

### Example Scorecard

```json
{
  "retrieval": {
    "recall@5": 0.88,
    "precision@5": 0.72,
    "MRR": 0.81
  },
  "generation": {
    "attribution_rate": 0.91,
    "faithfulness_score": 0.94,
    "hallucination_detected": false
  },
  "context_utilization": {
    "utilization_rate": 0.68,
    "docs_used": [0, 2, 3]
  },
  "answer_quality": {
    "correctness": 0.89,
    "completeness": 0.82,
    "relevance": 0.95,
    "overall_score": 0.87
  },
  "efficiency": {
    "latency_ms": 2340,
    "cost_usd": 0.014,
    "tokens_used": 3200
  },
  "overall_verdict": "GOOD",
  "failure_mode": null
}
```

**Interpretation:**
- Retrieval: Good (Recall@5=0.88)
- Generation: Excellent (Faithfulness=0.94, no hallucination)
- Utilization: Moderate (68%, some docs ignored)
- Quality: Good (87% overall)
- **Recommendation:** Improve retrieval precision (72% → 80%+) to reduce wasted docs

---

## Production Monitoring Strategies

### Real-Time Monitoring

**Key Metrics to Track:**

1. **Latency P50/P95/P99:** Response time distribution
2. **Error Rate:** % of queries that fail
3. **Hallucination Rate:** % of responses with detected hallucinations
4. **Attribution Rate:** % of responses properly attributed
5. **User Satisfaction:** Thumbs up/down feedback

```python
# Monitoring dashboard queries
SELECT
    DATE(timestamp) as date,
    AVG(latency_ms) as avg_latency,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY latency_ms) as p95_latency,
    AVG(attribution_rate) as avg_attribution,
    AVG(faithfulness_score) as avg_faithfulness,
    SUM(CASE WHEN hallucination_detected THEN 1 ELSE 0 END) / COUNT(*) as hallucination_rate
FROM rag_evaluations
WHERE timestamp >= NOW() - INTERVAL '7 days'
GROUP BY DATE(timestamp)
ORDER BY date DESC;
```

---

### Alerting Rules

**Set thresholds for automatic alerts:**

```yaml
alerts:
  - name: "High Hallucination Rate"
    condition: "hallucination_rate > 0.10"
    severity: "HIGH"
    action: "Disable system, notify on-call"

  - name: "Low Attribution Rate"
    condition: "attribution_rate < 0.75"
    severity: "MEDIUM"
    action: "Notify team, investigate"

  - name: "High Latency"
    condition: "p95_latency > 5000ms"
    severity: "MEDIUM"
    action: "Check retrieval performance"

  - name: "Low Retrieval Recall"
    condition: "recall@5 < 0.70"
    severity: "MEDIUM"
    action: "Refresh vector index, check embeddings"
```

---

### Continuous Evaluation

**Evaluate random sample of production queries:**

```python
# Hourly evaluation job
def continuous_evaluation_job():
    # Sample 100 random queries from last hour
    queries = sample_recent_queries(n=100)

    results = []
    for query in queries:
        # Re-run RAG pipeline
        context = retrieval(query)
        response = generation(query, context)

        # Evaluate
        eval_result = rag_evaluator.evaluate(query, response, context)
        results.append(eval_result)

    # Aggregate metrics
    avg_metrics = aggregate(results)

    # Log to monitoring system
    log_metrics(avg_metrics, timestamp=now())

    # Check for degradation
    if avg_metrics["faithfulness_score"] < 0.80:
        send_alert("Faithfulness degradation detected")
```

---

## Building a RAG Evaluation Pipeline

### End-to-End Implementation

```python
from typing import List, Dict, Any

class RAGPipelineEvaluator:
    """
    Comprehensive RAG pipeline evaluator.

    Integrates:
    - Retrieval metrics (from HW4)
    - Generation metrics (from Lesson 13)
    - Context utilization measurement
    - Answer quality evaluation
    """

    def __init__(self, retrieval_fn, generation_fn):
        self.retrieval_fn = retrieval_fn
        self.generation_fn = generation_fn

        # Initialize component evaluators
        self.attribution_detector = AttributionDetector()
        self.hallucination_detector = HallucinationDetector()
        self.quality_evaluator = AnswerQualityEvaluator()

    def evaluate_query(
        self,
        query: str,
        reference_answer: str = None,
        reference_docs: List[str] = None
    ) -> Dict[str, Any]:
        """
        Evaluate RAG pipeline on single query.
        """
        # Step 1: Retrieval
        start_time = time.time()
        retrieved_docs = self.retrieval_fn(query, k=5)
        retrieval_time = time.time() - start_time

        # Step 2: Generation
        start_time = time.time()
        response = self.generation_fn(query, retrieved_docs)
        generation_time = time.time() - start_time

        # Step 3: Evaluate Retrieval (if reference docs available)
        retrieval_metrics = {}
        if reference_docs:
            retrieval_metrics = self._evaluate_retrieval(
                retrieved_docs, reference_docs
            )

        # Step 4: Evaluate Generation
        attribution_result = self.attribution_detector.verify_attribution(
            self.attribution_detector.extract_claims(response),
            retrieved_docs
        )

        hallucination_result = self.hallucination_detector.detect(
            response, retrieved_docs
        )

        # Step 5: Measure Context Utilization
        utilization_result = self._measure_utilization(response, retrieved_docs)

        # Step 6: Evaluate Answer Quality
        quality_result = self.quality_evaluator.evaluate(
            query, response, reference_answer
        )

        # Step 7: Diagnose Failures
        failure_mode = self._diagnose_failure({
            "retrieval": retrieval_metrics,
            "generation": {
                "attribution": attribution_result,
                "hallucination": hallucination_result
            },
            "utilization": utilization_result,
            "quality": quality_result
        })

        return {
            "query": query,
            "response": response,
            "retrieval_metrics": retrieval_metrics,
            "generation_metrics": {
                "attribution_rate": attribution_result["attribution_rate"],
                "faithfulness_score": 1.0 - hallucination_result.get("hallucination_rate", 0.0),
                "hallucination_detected": hallucination_result["has_hallucination"]
            },
            "context_utilization": utilization_result,
            "answer_quality": quality_result,
            "timing": {
                "retrieval_ms": retrieval_time * 1000,
                "generation_ms": generation_time * 1000,
                "total_ms": (retrieval_time + generation_time) * 1000
            },
            "failure_mode": failure_mode,
            "overall_verdict": self._determine_verdict(quality_result, hallucination_result)
        }

    def _diagnose_failure(self, metrics: Dict) -> str:
        """Identify root cause of failures."""
        # Check retrieval quality
        if metrics.get("retrieval", {}).get("recall@5", 1.0) < 0.5:
            return "RETRIEVAL_FAILURE"

        # Check hallucination
        if metrics["generation"]["hallucination"]["has_hallucination"]:
            return "GENERATION_FAILURE_HALLUCINATION"

        # Check context utilization
        if metrics["utilization"]["utilization_rate"] < 0.3:
            return "GENERATION_FAILURE_CONTEXT_IGNORED"

        # Check answer quality
        if metrics["quality"]["overall_score"] < 0.6:
            return "ANSWER_QUALITY_POOR"

        return None  # No failure detected

    def _determine_verdict(self, quality_result: Dict, hallucination_result: Dict) -> str:
        """Overall system verdict."""
        if hallucination_result["has_hallucination"]:
            return "FAIL"

        score = quality_result["overall_score"]
        if score >= 0.8:
            return "EXCELLENT"
        elif score >= 0.6:
            return "GOOD"
        elif score >= 0.4:
            return "FAIR"
        else:
            return "POOR"
```

---

## Real-World RAG Evaluation

### Case Study: Bhagavad Gita Q&A System

**Evaluation Setup:**
- **Dataset:** 200 Q&A pairs from `/Gita/Bhagavad-Gita-QA/English/english.csv`
- **Retrieval:** Semantic search over 737 verses
- **Generation:** GPT-4o with retrieved verses as context

**Results:**

```
Evaluation Summary (200 queries):

Retrieval Metrics:
- Recall@5: 0.87 ✅ Good coverage
- Precision@5: 0.68 ⚠️ Some irrelevant docs
- MRR: 0.79 ✅ Relevant docs ranked high

Generation Metrics:
- Attribution Rate: 0.92 ✅ Excellent grounding
- Faithfulness Score: 0.94 ✅ Minimal hallucination
- Hallucination Rate: 0.06 ✅ Low

Context Utilization:
- Average Utilization: 0.71 ✅ Uses most docs
- Docs Ignored: 1.5 per query ⚠️ Some waste

Answer Quality:
- Correctness: 0.84 ✅ High accuracy
- Completeness: 0.78 ⚠️ Sometimes incomplete
- Overall Score: 0.85 ✅ Good quality

Failure Analysis:
- Retrieval Failures: 8% (missed relevant verses)
- Generation Failures: 5% (hallucination or context ignored)
- Interaction Failures: 3% (too much context, poor synthesis)
- Query Failures: 4% (ambiguous philosophical questions)

Overall Verdict: PRODUCTION READY
```

**Recommendations:**
1. Improve retrieval precision (68% → 80%+) to reduce irrelevant docs
2. Implement query clarification for ambiguous philosophical queries
3. Add completeness checking to ensure all aspects of query addressed

---

## Practical Exercise

**Task:** Evaluate the recipe chatbot's RAG pipeline end-to-end.

**Dataset:** 50 recipe queries from `homeworks/hw4/data/processed_recipes.json`

**Steps:**
1. Run RAG pipeline on 50 queries
2. Measure retrieval quality (Recall@5, Precision@5, MRR)
3. Measure generation quality (attribution, faithfulness, hallucination)
4. Measure context utilization (which docs used?)
5. Evaluate answer quality (AI-as-judge)
6. Diagnose failure modes
7. Generate evaluation report

**Success Criteria:**
- Retrieval Recall@5 > 0.80
- Attribution Rate > 0.85
- Faithfulness Score > 0.90
- Answer Quality > 0.80
- Failure Rate < 10%

---

## Summary

**Key Takeaways:**

1. **RAG is Multi-Stage:** Evaluate retrieval + generation + interaction

2. **Component Metrics Don't Guarantee E2E Quality:** Optimize for final answer quality, not just retrieval recall

3. **Failure Mode Taxonomy:** Retrieval, Generation, Interaction, Query Understanding

4. **Context Utilization Matters:** If LLM ignores docs, retrieval effort is wasted

5. **Answer Correctness ≠ Answer Quality:** Correctness is objective (vs reference), quality is subjective (completeness, clarity, helpfulness)

6. **Holistic Evaluation:** Combine retrieval metrics, generation metrics, utilization, quality, efficiency

7. **Production Monitoring:** Track hallucination rate, attribution rate, latency, user satisfaction

**Next Steps:**
- [Attribution Detection Notebook](./attribution_detection.ipynb): Hands-on claim extraction and verification
- [Context Utilization Notebook](./context_utilization.ipynb): Measure which docs LLM uses
- [RAG Dashboard](../lesson-9-11/evaluation_dashboard.py): Visualize metrics across all lessons

---

**Further Reading:**

- [RAGAS: RAG Assessment Framework](https://docs.ragas.io/en/latest/)
- [TruLens: LLM Application Evaluation](https://www.trulens.org/)
- [LlamaIndex Evaluation Guide](https://docs.llamaindex.ai/en/stable/optimizing/evaluation/evaluation.html)
- [LangSmith: LLM Observability](https://docs.smith.langchain.com/)

---

*Tutorial maintained as part of [Lesson 13: RAG Generation & Attribution](./TUTORIAL_INDEX.md)*
