# Retrieval Metrics Tutorial: Recall@k and MRR Explained

## Learning Objectives

By completing this tutorial, you will be able to:
- ✅ Calculate and interpret Recall@1, Recall@3, Recall@5, and Recall@10
- ✅ Understand Mean Reciprocal Rank (MRR) and its use cases
- ✅ Interpret metric trade-offs and choose appropriate thresholds
- ✅ Establish reasonable baselines for different tasks
- ✅ Identify when to use each metric
- ✅ Analyze which query types succeed vs. fail

## Prerequisites

- Completed [RAG Evaluation Concepts](rag_evaluation_concepts.md)
- Understanding of information retrieval basics
- Have generated synthetic queries

## Estimated Time

**Reading Time:** 15-20 minutes

---

## Concepts

### Why Standard Metrics Matter

**Problem without metrics:**
- "Retrieval seems pretty good"
- "Most queries work"
- Can't measure improvements objectively

**Solution with metrics:**
- Recall@5 = 0.73 → 73% of queries succeed
- After optimization → Recall@5 = 0.81 → +8% improvement
- Clear, comparable, actionable

---

## Recall@k

### Definition

**Recall@k** measures what fraction of queries successfully retrieve the target document within the top-k results.

```
Recall@k = (Number of queries with target in top-k) / (Total queries)
```

**Binary metric:** For each query, either the target is in top-k (success) or it isn't (failure).

### Example Calculation

**Evaluation dataset:** 100 queries, each linked to a target recipe

**Query 1:** "What air fryer temperature for crispy vegetables?"
- Target recipe: "Air Fryer Mixed Vegetables" (ID: 42)
- Retrieved top-5: [ID: 42, ID: 18, ID: 91, ID: 3, ID: 55]
- Position: #1
- **Recall@1: ✅ Success (1)**
- **Recall@3: ✅ Success (1)**
- **Recall@5: ✅ Success (1)**

**Query 2:** "How long to marinate Korean bulgogi?"
- Target recipe: "Korean Beef Bulgogi" (ID: 127)
- Retrieved top-5: [ID: 88, ID: 33, ID: 127, ID: 204, ID: 5]
- Position: #3
- **Recall@1: ❌ Failure (0)**
- **Recall@3: ✅ Success (1)**
- **Recall@5: ✅ Success (1)**

**Query 3:** "Best gluten-free bread recipe?"
- Target recipe: "Gluten-Free Artisan Bread" (ID: 201)
- Retrieved top-5: [ID: 12, ID: 45, ID: 78, ID: 99, ID: 134]
- Position: Not in top-5 (ranked #23)
- **Recall@1: ❌ Failure (0)**
- **Recall@3: ❌ Failure (0)**
- **Recall@5: ❌ Failure (0)**

**After 100 queries:**
- Recall@1: 52 successes / 100 queries = **0.52 (52%)**
- Recall@3: 71 successes / 100 queries = **0.71 (71%)**
- Recall@5: 83 successes / 100 queries = **0.83 (83%)**

### Interpretation

**Recall@1 = 0.52 (52%)**
- 52% of users find their answer as the #1 result
- No scrolling required
- Best user experience

**Recall@3 = 0.71 (71%)**
- 71% of users find their answer in top 3
- Minimal scrolling
- Good user experience

**Recall@5 = 0.83 (83%)**
- 83% of users find their answer in top 5
- Some scrolling required
- Acceptable user experience

**Recall@10 = 0.91 (91%)**
- 91% of users eventually find their answer
- Significant scrolling
- Marginal user experience

### Typical Ranges for Well-Designed Systems

| Metric | Poor | Acceptable | Good | Excellent |
|--------|------|------------|------|-----------|
| Recall@1 | <30% | 40-50% | 50-60% | >65% |
| Recall@3 | <50% | 60-70% | 70-80% | >85% |
| Recall@5 | <60% | 70-80% | 80-90% | >90% |
| Recall@10 | <70% | 80-85% | 85-95% | >95% |

**Important:** Ranges depend heavily on:
- Query difficulty (specific vs. ambiguous)
- Corpus size (200 recipes vs. 200,000)
- Domain complexity (cooking vs. legal documents)

### Why Multiple k Values?

**Recall@1** - User Experience Quality
- Measures "instant gratification"
- Critical for mobile/voice interfaces
- Highest bar

**Recall@3** - Practical Performance
- Most users scan top 3
- Balances quality and coverage
- Common target for optimization

**Recall@5** - Comprehensive Coverage
- Standard evaluation metric
- Most users willing to check top 5
- Captures retrieval capability

**Recall@10** - Upper Bound
- Shows maximum retrieval potential
- Users rarely go beyond 10
- Diagnostic for ranking issues

**Gap analysis example:**
- Recall@1: 45%
- Recall@5: 78%
- Recall@10: 85%

**Interpretation:**
- Target document is being retrieved (85% in top-10)
- Ranking is the problem (only 45% at #1)
- **Action:** Improve ranking algorithm, not retrieval coverage

---

## Mean Reciprocal Rank (MRR)

### Definition

**MRR** measures the average quality of ranking across all queries.

```
MRR = (1/N) × Σ(1 / rank_i)
```

Where:
- **N** = total number of queries
- **rank_i** = position of target for query i
- **1/rank** = reciprocal rank (higher rank → lower score)

**Key insight:** MRR heavily weights top positions.

### Worked Example

**Query 1:** Target at rank 1 → RR = 1/1 = **1.00**
**Query 2:** Target at rank 2 → RR = 1/2 = **0.50**
**Query 3:** Target at rank 3 → RR = 1/3 = **0.33**
**Query 4:** Target at rank 5 → RR = 1/5 = **0.20**
**Query 5:** Target at rank 10 → RR = 1/10 = **0.10**
**Query 6:** Target not in top-10 → RR = **0.00**

```
MRR = (1.00 + 0.50 + 0.33 + 0.20 + 0.10 + 0.00) / 6
    = 2.13 / 6
    = 0.355 (35.5%)
```

### Interpretation

**MRR = 1.00**: Perfect! All targets at rank #1
**MRR = 0.50**: Average rank is #2
**MRR = 0.33**: Average rank is #3
**MRR = 0.20**: Average rank is #5
**MRR = 0.10**: Average rank is #10

**General interpretation:**
```
MRR ≈ 1 / (average rank of target)
```

### MRR vs. Recall@k

**Recall@5** only cares if target is in top-5 (binary: yes/no)

**MRR** cares about **where** in top-5 the target appears:
- Target at #1 → MRR contribution: 1.00
- Target at #5 → MRR contribution: 0.20
- **5x difference!**

**Example scenario:**

**System A:**
- 80% of targets at rank #1
- 20% of targets at rank #10
- **Recall@5:** 80%
- **MRR:** (80 × 1.00 + 20 × 0.10) / 100 = **0.82**

**System B:**
- 80% of targets at rank #5
- 20% of targets at rank #10
- **Recall@5:** 80% (same as System A!)
- **MRR:** (80 × 0.20 + 20 × 0.10) / 100 = **0.18**

**Conclusion:** System A is much better, but Recall@5 doesn't show it. MRR does!

### When to Use MRR

✅ **Use MRR when:**
- Ranking quality matters (position #1 vs. #5)
- Optimizing for user experience
- Measuring ranking algorithm improvements
- Comparing retrieval systems

❌ **Don't rely solely on MRR when:**
- Coverage matters more than ranking
- Binary success/failure is sufficient
- Target is often missing from top-k entirely (MRR = 0 doesn't distinguish rank #11 from #100)

---

## Metric Trade-offs

### Recall@1 vs. Recall@5 vs. MRR

| Scenario | Recall@1 | Recall@5 | MRR | Interpretation |
|----------|----------|----------|-----|----------------|
| **Perfect system** | 1.00 | 1.00 | 1.00 | All targets at #1 |
| **Good ranking** | 0.60 | 0.85 | 0.70 | Most at top, few scattered |
| **Poor ranking** | 0.30 | 0.85 | 0.40 | Targets found but ranked low |
| **Retrieval failure** | 0.15 | 0.25 | 0.18 | Targets missing entirely |

**Diagnostic guidelines:**

**High Recall@5, Low Recall@1:** Ranking problem
- Target is retrieved but ranked poorly
- Fix: Improve ranking algorithm (BM25 params, embeddings)

**Low Recall@5, Low Recall@1:** Retrieval problem
- Target not being retrieved at all
- Fix: Improve coverage (indexing, query processing, vocabulary)

**High MRR, Moderate Recall@5:** Quality over quantity
- System prioritizes precision
- Good for expert users, may frustrate beginners

**Moderate MRR, High Recall@5:** Quantity over quality
- System prioritizes recall
- More tolerant, potentially noisy results

---

## Baseline Establishment

### Why Baselines Matter

**Problem:** "Recall@5 is 73%. Is that good?"

**Answer:** Depends on the baseline!
- Random retrieval: ~2.5% (for 200 docs)
- Title-only search: ~45%
- Full-text BM25: ~70%
- **73% is good relative to full-text BM25 baseline**

### Computing Random Baseline

```
Random Recall@k = k / N

Where:
- k = number of results returned
- N = total documents in corpus
```

**Example: 200 recipes in corpus**
- Random Recall@1 = 1/200 = **0.5%**
- Random Recall@5 = 5/200 = **2.5%**
- Random Recall@10 = 10/200 = **5.0%**

**Interpretation:** Any retrieval system scoring below this is worse than random!

### Establishing Your Baseline

**Step 1: Simple Baseline (Title-Only BM25)**
- Index only recipe titles
- Run evaluation
- Typical: Recall@5 ≈ 40-50%

**Step 2: Your Implementation (Full-Text BM25)**
- Index full recipe (ingredients + steps + title)
- Run evaluation
- Target: Recall@5 ≈ 70-85%

**Step 3: Advanced (Optional)**
- Semantic embeddings
- Query rewrite agent
- Target: Recall@5 ≈ 85-95%

**Report improvements:**
```
Title-Only BM25: Recall@5 = 48%
Full-Text BM25:  Recall@5 = 73% (+25 pp improvement)
With Agent:      Recall@5 = 81% (+8 pp improvement)
```

---

## Query Type Analysis

### Why Segment by Query Type?

**Aggregate metrics hide patterns:**
- Overall Recall@5: 73%
- But which query types succeed? Which fail?

**Segmented analysis reveals:**
- Appliance queries: Recall@5 = 85% ✅
- Timing queries: Recall@5 = 78% ✅
- Technique queries: Recall@5 = 65% ⚠️
- Ingredient substitution: Recall@5 = 42% ❌

**Action:** Focus on improving ingredient substitution retrieval.

### Example Segmentation

**By query category:**
- Appliance settings (e.g., "air fryer temperature")
- Timing specifics (e.g., "how long to marinate")
- Techniques (e.g., "how to get crispy skin")
- Ingredients (e.g., "substitute for buttermilk")

**By query complexity:**
- Simple (1-2 constraints): Recall@5 = 88%
- Medium (3-4 constraints): Recall@5 = 72%
- Complex (5+ constraints): Recall@5 = 51%

**By query length:**
- Short (<8 words): Recall@5 = 68%
- Medium (8-15 words): Recall@5 = 76%
- Long (>15 words): Recall@5 = 81%

**Insight:** Longer, more specific queries retrieve better!

---

## Implementation Example

### Python Code for Metrics

```python
def recall_at_k(retrieved_ids: List[int], target_id: int, k: int) -> int:
    """Calculate Recall@k for a single query."""
    top_k = retrieved_ids[:k]
    return 1 if target_id in top_k else 0

def reciprocal_rank(retrieved_ids: List[int], target_id: int) -> float:
    """Calculate reciprocal rank for a single query."""
    try:
        rank = retrieved_ids.index(target_id) + 1  # 1-indexed
        return 1.0 / rank
    except ValueError:
        return 0.0  # Target not found

def evaluate_retrieval(queries: List[Dict], retriever) -> Dict:
    """Evaluate retrieval system on query set."""
    results = []

    for query_data in queries:
        query = query_data['query']
        target_id = query_data['source_recipe_id']

        # Retrieve top-10
        retrieved = retriever.retrieve(query, top_k=10)
        retrieved_ids = [r['id'] for r in retrieved]

        # Calculate metrics
        result = {
            'query': query,
            'target_id': target_id,
            'recall_1': recall_at_k(retrieved_ids, target_id, 1),
            'recall_3': recall_at_k(retrieved_ids, target_id, 3),
            'recall_5': recall_at_k(retrieved_ids, target_id, 5),
            'recall_10': recall_at_k(retrieved_ids, target_id, 10),
            'reciprocal_rank': reciprocal_rank(retrieved_ids, target_id),
            'target_rank': retrieved_ids.index(target_id) + 1 if target_id in retrieved_ids else None
        }

        results.append(result)

    # Aggregate
    metrics = {
        'recall_at_1': sum(r['recall_1'] for r in results) / len(results),
        'recall_at_3': sum(r['recall_3'] for r in results) / len(results),
        'recall_at_5': sum(r['recall_5'] for r in results) / len(results),
        'recall_at_10': sum(r['recall_10'] for r in results) / len(results),
        'mrr': sum(r['reciprocal_rank'] for r in results) / len(results),
        'total_queries': len(results)
    }

    return metrics, results
```

---

## Common Pitfalls

### Pitfall 1: Only Reporting Recall@1

**❌ Problem:** "System achieves 45% accuracy"

**Why it's incomplete:**
- Missing Recall@5 context (might be 80%!)
- Missing MRR (ranking quality unknown)
- Can't diagnose retrieval vs. ranking issues

**✅ Solution:** Always report Recall@1, @3, @5, and MRR

### Pitfall 2: No Baseline Comparison

**❌ Problem:** "Recall@5: 68%"

**Why it's meaningless:**
- Is 68% good or bad?
- Better than what?

**✅ Solution:** Report improvement over baseline
```
Baseline (Title-Only): Recall@5 = 45%
Your System: Recall@5 = 68% (+23 pp improvement)
```

### Pitfall 3: Ignoring Query Segmentation

**❌ Problem:** Only report aggregate metrics

**Why it's limiting:**
- Hides query-type-specific failures
- Miss optimization opportunities

**✅ Solution:** Segment by query category and analyze separately

### Pitfall 4: Comparing Across Different Datasets

**❌ Problem:** "My Recall@5 (73%) beats your Recall@5 (68%)"

**Why it's invalid:**
- Different query difficulty
- Different corpus size
- Different domains

**✅ Solution:** Only compare systems on **same dataset**

---

## Key Takeaways

- ✅ **Recall@k measures retrieval success** - Binary: target in top-k or not
- ✅ **MRR measures ranking quality** - Weights position heavily
- ✅ **Multiple metrics tell full story** - Use Recall@1, @3, @5, and MRR together
- ✅ **Baselines provide context** - Know what "good" means for your task
- ✅ **Segment by query type** - Identify specific failure patterns
- ✅ **Gap analysis reveals root cause** - Recall@5 high + Recall@1 low = ranking problem

---

## Further Reading

### Related Tutorials
- [RAG Evaluation Concepts](rag_evaluation_concepts.md) - Foundation concepts
- [Synthetic Query Generation](synthetic_query_generation_tutorial.ipynb) - Build evaluation datasets
- [Query Rewrite Agent](query_rewrite_agent_tutorial.ipynb) - Improve metrics with query optimization

### Code References
- [scripts/evaluate_retrieval.py](scripts/evaluate_retrieval.py) - Reference implementation
- [backend/retrieval.py](../../backend/retrieval.py) - BM25 retriever

### External Resources
- Manning, Raghavan, Schütze (2008): "Introduction to Information Retrieval" - Chapter 8
- Voorhees & Harman (2005): "TREC: Experiment and Evaluation in Information Retrieval"

---

**Tutorial Status:** ✅ Complete
**Last Updated:** 2025-10-29
**Maintainer:** AI Evaluation Course Team
