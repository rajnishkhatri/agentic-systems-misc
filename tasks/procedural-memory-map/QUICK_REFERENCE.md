# Quick Reference: LLM Evaluation Techniques

**One-page decision matrix for rapid technique selection**

---

## Primary Decision Matrix

| I need to... | Use this technique | Difficulty | Est. Cost | Est. Time | Tutorial |
|--------------|-------------------|------------|-----------|-----------|----------|
| **Validate system prompt quality** | Prompt Engineering + Query Diversity | Beginner | Free | 1-2 hrs | [HW1](../../homeworks/hw1/TUTORIAL_INDEX.md) |
| **Find unknown failure modes** | Open/Axial Coding | Beginner | Free | 2-3 hrs | [HW2](../../homeworks/hw2/TUTORIAL_INDEX.md) |
| **Generate diverse test queries** | Synthetic Query Generation (Dimension Tuples) | Intermediate | $0.05-0.40 | 30 min | [HW2](../../homeworks/hw2/TUTORIAL_INDEX.md) |
| **Automate evaluation at scale** | LLM-as-Judge + Bias Correction | Intermediate | $0.50-2.00 | 2-3 hrs | [HW3](../../homeworks/hw3/TUTORIAL_INDEX.md) |
| **Measure RAG retrieval performance** | BM25 + Recall@k + MRR | Intermediate | $0.05-0.15 | 1-2 hrs | [HW4](../../homeworks/hw4/TUTORIAL_INDEX.md) |
| **Improve retrieval quality** | Query Rewrite Agent | Advanced | $0.50-2.00 | 1-2 hrs | [HW4 Optional](../../homeworks/hw4/TUTORIAL_INDEX.md) |
| **Debug agent pipeline bottlenecks** | Transition Matrix Analysis | Intermediate | Free | 1-2 hrs | [HW5](../../homeworks/hw5/TUTORIAL_INDEX.md) |
| **Verify tool grounding (no hallucinations)** | Substantiation Evaluation | Advanced | $0.50-2.00 | 3-4 hrs | [Lesson 4](../../lesson-4/TUTORIAL_INDEX.md) |
| **Review edge cases manually** | Trace Inspection + CSV Conversion | Beginner | Free | 1-2 hrs | [Lesson 7](../../lesson-7/TUTORIAL_INDEX.md) |
| **Optimize production costs** | Model Cascades (Confidence Thresholding) | Advanced | Varies | 2-3 hrs | [Lesson 8](../../lesson-8/TUTORIAL_INDEX.md) |

---

## Problem-Type Quick Index

### 🎯 System Prompts & Instructions
**Goal**: Ensure prompts produce desired behavior
- **Start**: Prompt Engineering (HW1) → Define role, rules, constraints
- **Test**: Query Diversity (HW1) → Cover dimensions systematically
- **Iterate**: Bulk Testing → Identify failure patterns

### 🔍 Retrieval Systems (RAG)
**Goal**: Measure and improve retrieval accuracy
- **Baseline**: BM25 Retrieval (HW4) → Fast, interpretable
- **Measure**: Recall@k, MRR (HW4) → Standard IR metrics
- **Optimize**: Query Rewrite Agent (HW4 Optional) → Improve hard queries
- **Generate Tests**: Salient Fact Extraction (HW4) → Realistic synthetic queries

### 🤖 Agent Pipelines
**Goal**: Debug multi-step agent workflows
- **Identify Bottlenecks**: Transition Matrix (HW5) → Where failures cluster
- **Verify Tool Use**: Substantiation (Lesson 4) → Prevent fabrication
- **Manual Review**: Trace Inspection (Lesson 7) → Investigate edge cases

### 💬 Response Quality
**Goal**: Evaluate output correctness/appropriateness
- **Objective Criteria**: LLM-as-Judge (HW3) → Automated binary/multi-class
- **Subjective Criteria**: Manual Annotation (Lesson 7) → Human labeling
- **Scale**: Parallel Labeling (Lesson 4) → Process 200+ examples efficiently
- **Rigor**: Bias Correction (HW3) → Account for judge errors

### 💰 Cost Optimization
**Goal**: Reduce production inference costs
- **Pattern**: Model Cascades (Lesson 8) → Cheap model → Expensive model
- **Mechanism**: Confidence Thresholding → Route based on logprobs
- **Target**: 40-70% cost savings while maintaining accuracy

---

## Resource-Constrained Decision Guide

### Limited Budget (<$5)
✅ **Use**:
- Manual labeling (free, time-intensive)
- gpt-4o-mini for judging ($0.10-0.50 per 100 examples)
- BM25 retrieval (no API costs)
- Open coding on small samples (20-30 traces)

❌ **Avoid**:
- GPT-4o for bulk labeling ($5-10 per 200 examples)
- Expensive models for simple tasks
- Large-scale automated evaluation

### Limited Time (<2 hours)
✅ **Use**:
- Parallel processing (ThreadPoolExecutor)
- DEMO modes in notebooks (5-10 examples)
- Baseline metrics only (skip advanced analysis)
- Sampling (100 examples, not 1000)

❌ **Avoid**:
- Manual labeling at scale
- Complex multi-stage pipelines
- Exhaustive hyperparameter tuning

### Limited Labeled Data (<50 examples)
✅ **Use**:
- Manual annotation workflows
- Synthetic query generation for expansion
- Unsupervised methods (clustering, simple heuristics)
- Qualitative analysis (open/axial coding)

❌ **Avoid**:
- Train/dev/test splitting (insufficient data)
- LLM-as-Judge (needs 100+ for reliable evaluation)
- Complex statistical methods

---

## Accuracy Requirement Guide

### Exploratory (80-90% is fine)
**Goal**: Quick insights, hypothesis generation
- Simple baselines, manual review of failures
- **Techniques**: Open Coding, Basic Metrics, Heuristic Rules

### Production (95%+ required)
**Goal**: Reliable automated system
- Rigorous evaluation with confidence intervals
- **Techniques**: LLM-as-Judge, Bias Correction, Multi-tier Validation

### Safety-Critical (99%+ with human oversight)
**Goal**: Prevent dangerous failures
- Human-in-the-loop required
- **Techniques**: Manual Annotation, Automated Pre-screening, Expert Review, Substantiation Checks

---

## Technique Family Quick Reference

| Family | When to Use | Key Techniques | Time Investment |
|--------|-------------|----------------|----------------|
| **Qualitative Methods** | Initial exploration, unknown failures | Open Coding, Axial Coding, Taxonomy Building | 2-4 hrs |
| **Quantitative Metrics** | Known criteria, need benchmarks | Recall@k, MRR, TPR/TNR, Confidence Intervals | 1-2 hrs |
| **Automated Evaluation** | Scale evaluation, objective criteria | LLM-as-Judge, Substantiation, Parallel Labeling | 3-5 hrs |
| **Optimization Techniques** | Production deployment, cost constraints | Model Cascades, Query Rewrite, Cost-Accuracy Trade-offs | 2-3 hrs |
| **Debugging Methods** | System has known issues, need root cause | Transition Matrices, Error Pattern Coding, Trace Inspection | 1-3 hrs |

---

## Library Quick Index

| Library | Primary Use | Enables Techniques | Installation |
|---------|-------------|-------------------|--------------|
| **litellm** | Multi-provider LLM API | LLM-as-Judge, Synthetic Generation, Parallel Labeling | `pip install litellm` |
| **judgy** | Statistical bias correction | Confidence Intervals, Corrected Success Rates | `pip install judgy` |
| **rank-bm25** | Fast keyword retrieval | RAG Evaluation, Recall@k | `pip install rank-bm25` |
| **pandas** | Data manipulation | All analysis workflows | `pip install pandas` |
| **pydantic** | Structured LLM outputs | Judge Development, Validation | `pip install pydantic` |
| **seaborn** | Heatmap visualization | Transition Matrices, Confusion Matrices | `pip install seaborn` |
| **ThreadPoolExecutor** | Parallel LLM calls | Bulk Labeling, Query Generation | Built-in (concurrent.futures) |
| **tqdm** | Progress tracking | Long-running operations | `pip install tqdm` |

---

## Common Workflow Sequences

### Workflow 1: New System Evaluation (Cold Start)
```
1. Define system prompt (HW1: Prompt Engineering)
2. Create diverse test queries (HW1: Query Diversity)
3. Run bulk test (scripts/bulk_test.py)
4. Analyze failures (HW2: Open/Axial Coding)
5. Build failure taxonomy (HW2: Taxonomy)
6. Generate targeted tests (HW2: Synthetic Queries)
```

### Workflow 2: Automated Quality Monitoring
```
1. Collect conversation traces (production logs)
2. Create ground truth labels (HW3: Manual labeling or GPT-4o)
3. Split dataset (HW3: Train/Dev/Test 15%/40%/45%)
4. Develop judge prompt (HW3: Few-shot engineering)
5. Evaluate judge (HW3: Measure TPR/TNR)
6. Deploy with bias correction (HW3: judgy library)
```

### Workflow 3: RAG System Evaluation
```
1. Process documents (HW4: Extract recipes/docs)
2. Build retrieval index (HW4: BM25 implementation)
3. Generate synthetic queries (HW4: Salient fact extraction)
4. Measure baseline performance (HW4: Recall@k, MRR)
5. (Optional) Implement query rewrite (HW4: Agent enhancement)
6. Compare metrics (Baseline vs. Enhanced)
```

### Workflow 4: Agent Debugging
```
1. Collect failure traces (production logs)
2. Label failure states (HW5: Manual annotation)
3. Build transition matrix (HW5: State-based analysis)
4. Identify bottlenecks (HW5: High-frequency transitions)
5. Verify tool grounding (Lesson 4: Substantiation)
6. Manual deep-dive (Lesson 7: Trace inspection)
```

---

## Cost Estimation Formulas

### LLM API Costs (Approximate)
```
gpt-4o-mini:  $0.00015 per 1K input tokens, $0.00060 per 1K output tokens
gpt-4o:       $0.00250 per 1K input tokens, $0.01000 per 1K output tokens

Typical call: 500 input + 200 output tokens

gpt-4o-mini call: (500 × $0.00015 + 200 × $0.00060) / 1000 = $0.00020
gpt-4o call:      (500 × $0.00250 + 200 × $0.01000) / 1000 = $0.00325

For 100 evaluations:
  gpt-4o-mini: $0.02
  gpt-4o:      $0.33
```

### Common Task Costs
| Task | Quantity | Model | Cost |
|------|----------|-------|------|
| Ground truth labeling | 150 examples | gpt-4o | $0.50-1.00 |
| Judge evaluation | 150 examples | gpt-4o-mini | $0.03-0.05 |
| Synthetic query generation | 100 queries | gpt-4o-mini | $0.05-0.15 |
| Salient fact extraction | 100 documents | gpt-4o-mini | $0.05-0.15 |
| Substantiation labeling | 200 traces | gpt-4o | $0.65-1.30 |

---

## Anti-Patterns to Avoid

❌ **Using LLM-as-Judge for highly subjective tasks** (e.g., "Is this response funny?")
→ Use manual annotation instead

❌ **Skipping train/dev/test splits** (overfitting judge to test data)
→ Always split before judge development

❌ **Testing only "happy path" queries** (insufficient diversity)
→ Use dimension-based systematic generation

❌ **Ignoring cost-accuracy trade-offs** (using GPT-4o for everything)
→ Test cheaper models first, cascade if needed

❌ **No error analysis** (measuring metrics without understanding failures)
→ Always investigate why systems fail

❌ **Over-engineering** (building complex tools for 20 examples)
→ Use spreadsheets for small-scale annotation

---

## When to Escalate to Advanced Techniques

### Start Simple → Escalate as Needed

**Level 1: Beginner (HW1)**
- Manual testing with 10-20 queries
- Spot-checking outputs
- **Escalate when**: Need systematic coverage, finding many failures

**Level 2: Intermediate (HW2-4)**
- Structured error analysis (coding)
- Automated metrics (Recall@k, basic accuracy)
- **Escalate when**: Need scale (100+ examples), production deployment

**Level 3: Advanced (HW3, HW5, Lessons)**
- LLM-as-Judge with bias correction
- State-based failure analysis
- Cost optimization (cascades)
- **Escalate when**: Production monitoring, need rigor, cost constraints

---

## Quick Decision Flowchart

```
START: What do you need to evaluate?

├─ System Prompts?
│  └─> HW1 (Prompt Engineering + Query Diversity)
│
├─ Retrieval (RAG)?
│  └─> HW4 (BM25 + Recall@k + MRR)
│
├─ Agent Pipeline?
│  ├─ Finding bottlenecks? └─> HW5 (Transition Matrix)
│  ├─ Verifying tool use? └─> Lesson 4 (Substantiation)
│  └─ Manual review? └─> Lesson 7 (Trace Inspection)
│
├─ Response Quality?
│  ├─ Objective criteria? └─> HW3 (LLM-as-Judge)
│  └─ Subjective criteria? └─> Lesson 7 (Manual Annotation)
│
└─ Production Costs Too High?
   └─> Lesson 8 (Model Cascades)
```

---

## Next Steps

After choosing your technique from this reference:
1. **Review detailed guide**: See [techniques-catalog.md](techniques-catalog.md)
2. **Check prerequisites**: Ensure you have required tools/data
3. **Follow tutorial**: Navigate to source tutorial (linked in table above)
4. **Implement**: Use patterns from [patterns.md](patterns.md) for common tasks
5. **Validate**: Check your results match expected outputs

---

**For comprehensive decision logic**: See [decision-trees.md](decision-trees.md)
**For implementation patterns**: See [patterns.md](patterns.md)
**For all techniques**: See [techniques-catalog.md](techniques-catalog.md)
