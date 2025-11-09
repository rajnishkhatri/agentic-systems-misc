# Optimization Techniques Family

**When to use this family**: Production deployment, cost constraints, performance improvement, latency requirements

---

## Overview

Optimization techniques improve **cost, speed, or quality** of LLM systems. Use when:
- ✅ Production costs are too high
- ✅ Need faster response times
- ✅ Want to improve retrieval/generation quality
- ✅ Have working baseline to optimize

---

## Techniques in This Family

### 1. BM25 Retrieval (HW4)
**Purpose**: Fast, interpretable keyword-based retrieval

**When to use**:
- Building RAG system
- Want zero API costs for retrieval
- Queries and documents share vocabulary

**Advantages**:
- ✅ No embedding costs
- ✅ Fast (milliseconds for 1000 documents)
- ✅ Interpretable (can see why documents matched)

**Limitations**:
- ❌ Poor with semantic gap (query "car" won't match "automobile")
- ❌ No understanding of synonyms

**Typical performance**: 70-85% Recall@5 for well-matched datasets

---

### 2. Query Rewrite Agent (HW4)
**Purpose**: Improve retrieval by optimizing query formulation

**Three strategies**:

**A. Keywords Extraction**
```
Query: "What air fryer temperature for crispy vegetables?"
Keywords: "air fryer temperature vegetables crispy"
→ Better match for recipe instructions
```

**B. Query Rewriting**
```
Query: "Quick healthy breakfast ideas"
Rewrite: "easy breakfast recipes under 15 minutes healthy"
→ Uses document vocabulary
```

**C. Query Expansion**
```
Query: "vegan protein sources"
Expanded: "vegan protein sources tofu tempeh lentils beans"
→ Adds related terms
```

**Expected improvement**: 5-15% Recall@5 increase

**Cost**: +1 LLM call per query ($0.0002 with gpt-4o-mini)

---

### 3. Model Cascades (Lesson 8)
**Purpose**: Reduce costs by routing easy queries to cheap model

**Architecture**:
```
Query → Cheap Model (gpt-4o-mini)
          ↓
    Confidence >= threshold?
          ↙          ↘
        Yes           No
         ↓             ↓
    Return answer  Expensive Model (gpt-4o)
                        ↓
                    Return answer
```

**Requirements**:
- Cheap model ≥80% accuracy
- Confidence scores available (logprobs)
- ≥60% of queries route to cheap model

**Expected savings**: 40-70% cost reduction

---

### 4. Confidence Thresholding (Lesson 8)
**Purpose**: Decision logic for routing in cascades

**Threshold selection**:

| Threshold | % to Cheap | Accuracy | Use Case |
|-----------|------------|----------|----------|
| 0.70 | 95% | 98% | Exploratory, low stakes |
| 0.80 | 90% | 98.5% | Good balance |
| 0.90 | 85% | 99% | Production (recommended) ✅ |
| 0.95 | 70% | 99.3% | High accuracy needs |
| 0.99 | 40% | 99.7% | Safety-critical |

**Optimization approach**:
1. Test multiple thresholds on validation set
2. Plot threshold vs (accuracy, cost)
3. Select threshold meeting accuracy target with max savings

---

### 5. Logprob Extraction (Lesson 8)
**Purpose**: Get confidence scores for routing

**Implementation**:
```python
import litellm
import math

response = litellm.completion(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Is this spam? Yes or No"}],
    logprobs=True,
    max_tokens=1
)

# Extract logprobs
logprobs_dict = response.choices[0].logprobs.content[0].top_logprobs

# Convert to probabilities
probs = {
    token: math.exp(data.logprob)
    for token, data in logprobs_dict.items()
}

# Normalize
total = sum(probs.values())
confidence = probs["Yes"] / total  # e.g., 0.95

# Routing decision
if confidence >= 0.90:
    return "Yes"  # High confidence
else:
    # Route to expensive model
    ...
```

---

### 6. Cost-Accuracy Trade-off Analysis (Lesson 8)
**Purpose**: Justify model selection decisions

**Analysis steps**:
1. List model options with costs
2. Measure accuracy on same test set
3. Plot accuracy vs cost
4. Identify pareto frontier
5. Select based on requirements

**Example**:
```
Model              | Accuracy | Cost/1K queries
-------------------|----------|----------------
gpt-4o-mini        | 96.5%    | $0.50
gpt-4o             | 99.2%    | $5.00
Cascade (0.90)     | 99.1%    | $1.15
```

**Decision**: Cascade offers 99.1% accuracy (matching GPT-4o) at 77% lower cost.

---

## Optimization Workflow

### Stage 1: Establish Baseline
```
1. Implement simplest approach (e.g., BM25, cheap model only)
2. Measure performance (accuracy, cost, latency)
3. Identify bottlenecks
```

### Stage 2: Targeted Optimization
```
If retrieval is bottleneck:
  → Try query rewrite agent (HW4)

If generation cost is bottleneck:
  → Try model cascades (Lesson 8)

If latency is bottleneck:
  → Implement caching, batch processing
```

### Stage 3: Validate Improvement
```
1. Measure optimized system on same test set
2. Calculate improvement: Δaccuracy, Δcost, Δlatency
3. Statistical significance test (paired t-test)
4. Deploy if improvement justifies complexity
```

---

## Cost Optimization Strategies

### 1. Model Selection
```
Task: Spam classification

Option A: GPT-4o only
Cost: $5.00 per 1000
Accuracy: 99.2%

Option B: gpt-4o-mini only
Cost: $0.50 per 1000
Accuracy: 96.5%

Option C: Cascade (threshold=0.90)
Cost: $1.15 per 1000
Accuracy: 99.1%
→ Winner: 77% savings vs A, 2.6pp better than B
```

### 2. Prompt Optimization
- **Before**: 1000 token prompt
- **After**: 300 token prompt (remove examples, compress)
- **Savings**: 70% on input tokens

### 3. Caching
```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_llm_response(prompt: str) -> str:
    return litellm.completion(...)

# Repeated queries → cached responses (free)
```

### 4. Batch Processing
```python
# Instead of 100 sequential calls
for query in queries:
    response = llm_call(query)  # 100 calls

# Batch 10 queries per call
batches = [queries[i:i+10] for i in range(0, len(queries), 10)]
for batch in batches:
    responses = llm_call_batch(batch)  # 10 calls
```

---

## Performance Optimization Strategies

### 1. Retrieval Improvement
**Baseline**: BM25, 70% Recall@5

**Optimizations**:
- Query rewrite (+8pp) → 78%
- Hybrid (BM25 + embeddings) (+12pp) → 82%
- Reranker on top-20 (+5pp) → 87%

### 2. Response Quality
**Baseline**: Single-shot generation, 85% quality

**Optimizations**:
- Few-shot examples (+5pp) → 90%
- Chain-of-thought prompting (+3pp) → 93%
- Self-consistency (3 samples, vote) (+2pp) → 95%

---

## Latency Optimization

### Sequential vs Parallel
```python
# Sequential (slow)
retrieval_results = retrieve(query)  # 100ms
llm_response = generate(retrieval_results)  # 2000ms
Total: 2100ms

# Parallel (faster, but wastes work)
import asyncio

async def pipeline(query):
    retrieval_task = asyncio.create_task(retrieve(query))
    quick_gen_task = asyncio.create_task(generate_without_retrieval(query))

    retrieval_results = await retrieval_task

    # Cancel quick gen if we have retrieval results
    if retrieval_results:
        quick_gen_task.cancel()
        return await generate(retrieval_results)
    else:
        return await quick_gen_task

Total: 100ms (if retrieval fast) or 2000ms (if retrieval slow)
```

---

## Complexity-Benefit Analysis

### When to Optimize

**Don't optimize if**:
- ❌ System not in production yet
- ❌ Cost/latency acceptable for current scale
- ❌ Optimization adds significant complexity

**Do optimize if**:
- ✅ Production costs >$1000/month (ROI justifies effort)
- ✅ User-facing latency issues (>3s response time)
- ✅ Scaling to 10x traffic soon

### ROI Calculation
```
Optimization effort: 20 engineer-hours
Engineer cost: $100/hour = $2000

Cost savings: $5000/month → $10,000/month
Monthly savings: $5000

ROI: Break-even in 0.4 months (12 days) ✅
```

---

## Anti-Patterns

### ❌ Premature Optimization
**Problem**: Optimizing before understanding baseline performance

**Solution**: Always establish baseline first, measure bottlenecks, then optimize

### ❌ Over-Engineering
**Problem**: Building complex cascade with 5 models for 2% improvement

**Solution**: Diminishing returns after 2-3 tiers. Keep it simple.

### ❌ Ignoring Maintenance Cost
**Problem**: Cascade saves $1000/month but requires 5 hours/month maintenance ($500)

**Solution**: Factor in ongoing maintenance when calculating ROI

### ❌ Sacrificing Quality for Cost
**Problem**: 96% accuracy acceptable for production? Usually no.

**Solution**: Define minimum acceptable quality first, optimize within that constraint

---

## Integration with Other Families

### Automated Evaluation → Optimization
1. LLM-as-Judge (HW3) establishes accuracy baseline
2. Model cascades (Lesson 8) reduce costs while maintaining accuracy
3. Monitor with bias-corrected metrics

### Quantitative Metrics → Optimization
1. Recall@k (HW4) measures retrieval baseline
2. Query rewrite improves Recall@k
3. MRR tracks ranking quality

---

## Real-World Example

**Scenario**: Spam classification system, 100K queries/day

### Baseline
```
Model: GPT-4o
Accuracy: 99.2%
Cost: $5.00 per 1K = $500/day = $15K/month
```

### Optimization Experiment
```
Test 1: gpt-4o-mini only
Accuracy: 96.5% (❌ too low for production)
Cost: $0.50 per 1K = $50/day

Test 2: Cascade (threshold=0.90)
- 85% routed to gpt-4o-mini
- 15% routed to GPT-4o
Accuracy: 99.1% (✅ acceptable)
Cost: $1.15 per 1K = $115/day = $3,450/month
```

### Decision
```
Deploy cascade:
- Saves: $11,550/month (77% reduction)
- Maintains: 99.1% accuracy (only 0.1pp drop)
- Adds latency: ~50ms (sequential calls)
- Implementation: 1 engineer-week ($4K)
- Break-even: 10 days

Result: Approved ✅
```

---

## Further Reading

**From tutorials**:
- [HW4: BM25 + Query Rewrite](../../homeworks/hw4/TUTORIAL_INDEX.md)
- [Lesson 8: Model Cascades](../../lesson-8/TUTORIAL_INDEX.md)

**Research**:
- "FrugalGPT: Cost-Effective LLM Usage" (Chen et al., 2023)
- "Optimizing Retrieval for RAG" (Lewis et al., 2020)
