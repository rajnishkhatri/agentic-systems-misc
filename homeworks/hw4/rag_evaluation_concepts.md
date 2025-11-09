# RAG Evaluation Concepts Tutorial

## Learning Objectives

By completing this tutorial, you will be able to:
- ✅ Understand RAG (Retrieval-Augmented Generation) architecture and components
- ✅ Explain BM25 algorithm intuition (TF-IDF scoring)
- ✅ Identify when to evaluate retrieval separately from generation
- ✅ Distinguish between retrieval vs. generation failure modes
- ✅ Design evaluation strategies for cold-start scenarios
- ✅ Compare synthetic vs. organic query evaluation approaches

## Prerequisites

- Completed [HW2: Error Analysis](../hw2/error_analysis_concepts.md)
- Basic understanding of information retrieval concepts
- Familiarity with LLM prompting

## Estimated Time

**Reading Time:** 20-25 minutes

---

## Concepts

### What is RAG?

**RAG (Retrieval-Augmented Generation)** combines information retrieval with LLM generation to ground responses in factual sources.

**Traditional LLM (Without RAG):**
```
User Query → LLM → Response (from parametric knowledge)
```
**Problem:** Limited to training data, prone to hallucinations

**RAG System:**
```
User Query → Retrieval (find relevant docs) → Context Assembly → LLM + Context → Response
```
**Benefit:** Grounded in retrieved documents, up-to-date information

### RAG Architecture

```
┌─────────────────────────────────────────────────────┐
│               RAG PIPELINE                          │
├─────────────────────────────────────────────────────┤
│                                                     │
│  1. USER QUERY                                      │
│     "What air fryer temperature for crispy          │
│      vegetables?"                                   │
│     ↓                                               │
│                                                     │
│  2. RETRIEVAL (BM25 or Embedding Search)            │
│     Search corpus for relevant recipes              │
│     ↓                                               │
│     Top-5 Most Relevant Recipes:                    │
│     - Air Fryer Brussels Sprouts (score: 12.4)     │
│     - Crispy Air Fryer Broccoli (score: 11.8)      │
│     - Air Fryer Mixed Vegetables (score: 10.2)     │
│     - Roasted Vegetable Medley (score: 9.1)        │
│     - Sheet Pan Vegetables (score: 8.3)            │
│     ↓                                               │
│                                                     │
│  3. CONTEXT ASSEMBLY                                │
│     Combine retrieved recipes into prompt context   │
│     ↓                                               │
│                                                     │
│  4. LLM GENERATION                                  │
│     Prompt: "Based on these recipes, answer:       │
│              [user query]"                          │
│     ↓                                               │
│                                                     │
│  5. RESPONSE                                        │
│     "For crispy air fryer vegetables, use 400°F    │
│      (200°C). Cook for 12-15 minutes, shaking      │
│      halfway through..."                            │
└─────────────────────────────────────────────────────┘
```

**Key Components:**
1. **Query Processing**: Parse and understand user intent
2. **Retrieval**: Find relevant documents from corpus
3. **Ranking**: Order documents by relevance
4. **Context Assembly**: Format retrieved docs for LLM
5. **Generation**: LLM synthesizes response from context

---

## Why Evaluate Retrieval Separately?

### Retrieval Failures Guarantee Bad Outputs

**Critical Insight:** If retrieval fails, generation will fail too.

**Example Failure:**

**Query:** "What air fryer temperature for crispy vegetables?"

**Retrieval Failure:**
- Retrieved: Slow cooker recipes, stovetop methods, oven roasting
- Missing: Air fryer recipes with temperature information

**Generation Result:**
- LLM has no air fryer context to work with
- Either hallucinates temperatures or gives generic answer
- **Guaranteed bad output**, regardless of LLM quality

**Why This Matters:**
- Retrieval failures are the #1 cause of RAG system failures
- Fixing retrieval is often easier than fixing generation
- Retrieval evaluation is cheap (no LLM calls needed)

### Separate Evaluation Benefits

**Benefits of evaluating retrieval independently:**

1. **Cheap and Fast**
   - No LLM API calls needed
   - Can evaluate 1000s of queries in seconds
   - Cost: ~$0 vs. $0.50-5.00 for end-to-end evaluation

2. **Clear Attribution**
   - Retrieval failure? → Fix indexing, query processing, ranking
   - Generation failure (with good retrieval)? → Fix prompt, model, context assembly

3. **Targeted Optimization**
   - Identify specific query types that fail retrieval
   - Test retrieval improvements without re-running generation
   - Iterate quickly on retrieval strategies

4. **Baseline Establishment**
   - Know theoretical upper bound (best case with perfect retrieval)
   - Measure retrieval bottleneck vs. generation bottleneck

---

## BM25: Best Matching 25

### What is BM25?

**BM25 (Best Matching 25)** is a probabilistic ranking function for information retrieval.

**Goal:** Score documents by relevance to a query.

### Intuition: TF-IDF Scoring

**Term Frequency (TF):**
- How often do query terms appear in the document?
- More appearances → Higher relevance

**Inverse Document Frequency (IDF):**
- How rare are query terms across the entire corpus?
- Rarer terms → More discriminative → Higher weight

**Document Length Normalization:**
- Longer documents naturally have more term matches
- Normalize to prevent bias toward long documents

### BM25 Formula (Simplified)

For each query term `t` in document `d`:

```
Score(t, d) = IDF(t) × (TF(t, d) × (k1 + 1)) / (TF(t, d) + k1 × (1 - b + b × (len(d) / avg_len)))
```

Where:
- **IDF(t)**: Log((N - df(t) + 0.5) / (df(t) + 0.5))
  - N = total documents
  - df(t) = documents containing term t
- **TF(t, d)**: Raw count of term t in document d
- **k1**: Term frequency saturation parameter (typically 1.2-2.0)
- **b**: Length normalization parameter (typically 0.75)
- **len(d)**: Length of document d
- **avg_len**: Average document length in corpus

**Total document score:** Sum of scores for all query terms.

### Worked Example

**Query:** "air fryer chicken"

**Document 1:** "Air fryer chicken breast recipe with crispy skin. Cook in air fryer at 400°F."

**Document 2:** "Chicken recipes including oven, stovetop, and air fryer methods."

**Scoring for "air fryer":**

**Document 1:**
- TF("air fryer"): 2 occurrences
- IDF: High (assuming "air fryer" is relatively rare in corpus)
- Length: 15 words
- **Score: HIGH** (relevant term appears frequently)

**Document 2:**
- TF("air fryer"): 1 occurrence
- IDF: High (same as above)
- Length: 11 words
- **Score: MEDIUM** (relevant term appears once)

**Scoring for "chicken":**

**Document 1:**
- TF("chicken"): 1 occurrence
- IDF: Low (assuming "chicken" is very common in recipe corpus)
- **Score: LOW** (common term, less discriminative)

**Document 2:**
- TF("chicken"): 1 occurrence
- IDF: Low (same as above)
- **Score: LOW**

**Total Scores:**
- Document 1: HIGH + LOW = **HIGHER TOTAL**
- Document 2: MEDIUM + LOW = **LOWER TOTAL**

**Result:** Document 1 ranks higher (more relevant)

### BM25 vs. Semantic Embeddings

| Aspect | BM25 | Semantic Embeddings (e.g., BERT) |
|--------|------|----------------------------------|
| **Speed** | Very fast (exact term matching) | Slower (neural network inference) |
| **Interpretability** | Explainable (term-level scores) | Black box |
| **Query Type** | Keyword-heavy queries | Natural language questions |
| **Training** | No training needed | Requires training data |
| **Cost** | Free | Compute-intensive |
| **Best For** | Technical queries, exact terms | Semantic similarity, paraphrases |

**For this assignment:** We use BM25 to focus on evaluation methodology (applies to any retriever).

---

## Retrieval vs. Generation Failure Modes

### Retrieval Failure Modes

**1. No Relevant Documents Found**
- Query: "air fryer temperature for crispy vegetables"
- Top-5: Oven recipes, stovetop methods, slow cooker
- **Root cause:** Vocabulary mismatch, sparse corpus, poor indexing

**2. Relevant Documents Ranked Too Low**
- Query: "gluten-free bread recipe"
- Target recipe exists but ranked #47
- Top-5: Regular bread recipes
- **Root cause:** Weak ranking signal, ambiguous query

**3. Query Misunderstanding**
- Query: "quick dinner ideas"
- Retrieved: Appetizers, desserts, breakfast recipes
- **Root cause:** Ambiguous intent, poor query processing

### Generation Failure Modes (with Good Retrieval)

**1. Hallucination Despite Context**
- Retrieved: 5 relevant recipes with temperatures
- LLM response: Made-up temperature not in any recipe
- **Root cause:** LLM not grounding in context

**2. Context Misinterpretation**
- Retrieved: Recipe says "bake at 350°F"
- LLM response: "Use 350°C" (wrong unit conversion)
- **Root cause:** LLM error, not retrieval error

**3. Incomplete Synthesis**
- Retrieved: Multiple recipes with different approaches
- LLM response: Only uses first recipe, ignores others
- **Root cause:** Poor context assembly or LLM limitation

### Attribution Strategy

**When evaluating end-to-end RAG:**

1. **Identify failure** (wrong answer, hallucination, missing info)
2. **Check retrieved documents**:
   - Does target information exist in retrieved docs?
   - Yes → Generation failure
   - No → Retrieval failure
3. **Apply appropriate fix**:
   - Retrieval failure → Improve indexing, ranking, query processing
   - Generation failure → Improve prompt, context format, model

---

## Synthetic vs. Organic Query Evaluation

### Synthetic Queries

**Definition:** Queries generated programmatically or via LLM, designed to test specific scenarios.

**Creation Process:**
1. Extract salient facts from documents ("air fryer, 400°F, 15 minutes")
2. Generate natural language query ("What temperature and time for air fryer cooking?")
3. Link query to source document (ground truth for evaluation)

**Pros:**
- ✅ Control over difficulty and coverage
- ✅ Known ground truth (source document)
- ✅ Can test edge cases systematically
- ✅ Easy to scale (generate 100s of queries)

**Cons:**
- ❌ May not reflect real user queries
- ❌ Can be unrealistically easy or hard
- ❌ LLM-generated queries may have patterns

**Best for:**
- Initial evaluation and development
- Testing specific capabilities
- Stress-testing edge cases
- Cold-start scenarios (no user data yet)

### Organic Queries

**Definition:** Real user queries collected from production or user studies.

**Pros:**
- ✅ Realistic query distribution
- ✅ Captures real user intent and vocabulary
- ✅ Includes typos, ambiguity, context
- ✅ Directly measures user-facing performance

**Cons:**
- ❌ Hard to obtain (requires users)
- ❌ Labeling ground truth is expensive
- ❌ May not cover edge cases
- ❌ Privacy considerations

**Best for:**
- Production evaluation
- A/B testing
- Measuring real-world performance
- Final validation before deployment

### Cold-Start Evaluation Strategy

**Problem:** No users yet, need to evaluate before launch.

**Solution:** Hybrid approach

**Phase 1: Synthetic Evaluation (Pre-Launch)**
1. Generate 100-200 synthetic queries covering:
   - Common query types (appliance, timing, technique, ingredient)
   - Edge cases (ambiguous queries, rare ingredients)
   - Failure modes (vocabulary mismatch, multi-hop reasoning)
2. Evaluate retrieval with Recall@k and MRR
3. Identify weaknesses and optimize

**Phase 2: Pilot Testing (Limited Launch)**
1. Launch to small user group (10-50 users)
2. Collect first 50-100 organic queries
3. Compare synthetic vs. organic performance
4. Adjust based on real usage patterns

**Phase 3: Production Evaluation (Post-Launch)**
1. Continuously collect organic queries
2. Sample 50-100 per month for manual evaluation
3. Track Recall@k over time
4. Detect performance regressions

---

## Common Pitfalls

### Pitfall 1: Evaluating Only End-to-End

**❌ Problem:** Only measure final response quality, not retrieval

**Why it fails:**
- Can't attribute failures to retrieval vs. generation
- Expensive (LLM calls for every evaluation)
- Slow iteration (must re-generate for every test)

**✅ Solution:** Evaluate retrieval separately first, then end-to-end

### Pitfall 2: Unrealistic Synthetic Queries

**❌ Problem:** Queries directly copy recipe titles

**Example:**
- Query: "Air Fryer Brussels Sprouts with Balsamic Glaze"
- Target: Recipe titled "Air Fryer Brussels Sprouts with Balsamic Glaze"
- Recall@1: 100% (trivial match!)

**✅ Solution:** Generate queries that require semantic matching, not exact title match

### Pitfall 3: Ignoring Query Distribution

**❌ Problem:** Evaluate on rare edge cases only

**Example:**
- 90% of queries test obscure techniques
- 10% of queries test common requests
- Optimization focuses on edge cases

**✅ Solution:** Weight evaluation by expected query frequency

### Pitfall 4: No Baseline Comparison

**❌ Problem:** Report "Recall@5: 73%" without context

**Why it fails:**
- Is 73% good or bad?
- Depends on query difficulty, corpus size, task complexity

**✅ Solution:** Establish baselines
- Random retrieval: ~5% Recall@5 (for 200 documents)
- Title-only BM25: ~40-50% Recall@5
- Full-text BM25: ~60-75% Recall@5 (your implementation)

---

## Key Takeaways

- ✅ **RAG combines retrieval + generation** - Retrieval finds docs, LLM synthesizes response
- ✅ **Retrieval failures guarantee bad outputs** - Can't generate good answers without good context
- ✅ **Evaluate retrieval separately** - Cheap, fast, enables targeted optimization
- ✅ **BM25 uses TF-IDF scoring** - Term frequency × inverse document frequency × length normalization
- ✅ **Attribution is critical** - Distinguish retrieval vs. generation failures
- ✅ **Synthetic queries enable cold-start evaluation** - Generate queries before having real users
- ✅ **Organic queries reflect reality** - Use real user queries for final validation
- ✅ **Establish baselines** - Know what "good" performance looks like for your task

---

## Further Reading

### Related Tutorials
- [Synthetic Query Generation Tutorial](synthetic_query_generation_tutorial.ipynb) - Generate evaluation queries
- [Retrieval Metrics Tutorial](retrieval_metrics_tutorial.md) - Recall@k and MRR explained
- [Query Rewrite Agent Tutorial](query_rewrite_agent_tutorial.ipynb) - Improve retrieval with query optimization

### Methodological Background
- Robertson & Zaragoza (2009): "The Probabilistic Relevance Framework: BM25 and Beyond"
- Majumder et al. (2019): "Generating Personalized Recipes" (dataset source)
- Lewis et al. (2020): "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks"

### Course Materials
- [AI Evaluation Complete Guide](../../AI_EVALUATION_COMPLETE_GUIDE.md) - Section 5: RAG Evaluation
- [HW4 Assignment README](README.md) - Full homework instructions
- [HW4 Tutorial Index](TUTORIAL_INDEX.md) - All HW4 learning resources

### Code References
- [scripts/process_recipes.py](scripts/process_recipes.py) - Dataset processing
- [scripts/generate_queries.py](scripts/generate_queries.py) - Synthetic query generation
- [scripts/evaluate_retrieval.py](scripts/evaluate_retrieval.py) - BM25 evaluation

### External Resources
- [rank-bm25 documentation](https://pypi.org/project/rank-bm25/) - Python BM25 implementation
- [Information Retrieval textbook](https://nlp.stanford.edu/IR-book/) - Manning, Raghavan, Schütze

---

**Tutorial Status:** ✅ Complete
**Last Updated:** 2025-10-29
**Maintainer:** AI Evaluation Course Team
