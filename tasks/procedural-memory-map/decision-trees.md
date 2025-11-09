# Decision Trees: Use Case → Technique Mapping

**Purpose**: Help AI assistants select appropriate evaluation techniques based on problem type, resource constraints, and accuracy requirements.

---

## Table of Contents

1. [By Problem Type](#by-problem-type)
2. [By Resource Constraints](#by-resource-constraints)
3. [By Accuracy Requirements](#by-accuracy-requirements)
4. [By Development Stage](#by-development-stage)
5. [By Scale](#by-scale)

---

## By Problem Type

### 🎯 Evaluating System Prompts & Instructions

**Goal**: Ensure system prompts produce desired bot behavior

#### Decision Path

**START**: You need to evaluate system prompt effectiveness

**Q1: Do you have an existing system prompt?**
- **No** → Start with **Prompt Engineering** (HW1)
  - Define bot role and objective clearly
  - Set behavioral rules (always/never instructions)
  - Control LLM agency and creativity levels
  - Structure output format (Markdown, JSON, etc.)
  - **Output**: Well-crafted system prompt
  - **Tutorial**: [HW1 System Prompt Engineering](../homeworks/hw1/TUTORIAL_INDEX.md)

- **Yes** → Continue to Q2

**Q2: Do you have test queries to evaluate the prompt?**
- **No** → Use **Query Diversity** (HW1)
  - Identify key dimensions (e.g., cuisine, dietary restrictions, meal type)
  - Create dimension value matrices
  - Generate representative combinations (10-20 queries)
  - **Output**: Diverse test query set
  - **Tutorial**: [HW1 Query Diversity](../homeworks/hw1/TUTORIAL_INDEX.md)

- **Yes** → Continue to Q3

**Q3: Have you run bulk testing?**
- **No** → Run **Bulk Test Execution**
  - Use scripts/bulk_test.py or equivalent
  - Collect 20-50 conversation traces
  - **Output**: Initial failure data
  - **Next**: Error analysis (HW2)

- **Yes** → Continue to Q4

**Q4: Do you know what types of failures are occurring?**
- **No** → Use **Open/Axial Coding** (HW2)
  - Perform qualitative analysis on traces
  - Build failure taxonomy
  - **Tutorial**: [HW2 Error Analysis](../homeworks/hw2/TUTORIAL_INDEX.md)

- **Yes** → Use **Synthetic Query Generation** (HW2)
  - Generate targeted test cases for known failure modes
  - Validate prompt improvements
  - **Tutorial**: [HW2 Dimension Generation](../homeworks/hw2/TUTORIAL_INDEX.md)

---

### 🔍 Evaluating Retrieval Systems (RAG)

**Goal**: Measure and improve retrieval accuracy before generation

#### Decision Path

**START**: You have a RAG system and need to evaluate retrieval

**Q1: Do you have a retrieval implementation?**
- **No** → Implement **BM25 Retrieval** (HW4)
  - Fast, interpretable keyword-based retrieval
  - No embedding costs
  - **Library**: rank-bm25
  - **Tutorial**: [HW4 RAG Evaluation](../homeworks/hw4/TUTORIAL_INDEX.md)

- **Yes** → Continue to Q2

**Q2: Do you have test queries with known relevant documents?**
- **No** → Generate **Synthetic Queries** (HW4)
  - Extract salient facts from documents
  - Use LLM to generate natural language queries
  - Create query → document pairs
  - **Cost**: $0.05-0.15 for 100 queries (gpt-4o-mini)
  - **Tutorial**: [HW4 Synthetic Query Generation](../homeworks/hw4/TUTORIAL_INDEX.md)

- **Yes** → Continue to Q3

**Q3: Have you measured baseline retrieval performance?**
- **No** → Calculate **Recall@k and MRR** (HW4)
  - Recall@1: Target in top result
  - Recall@3: Target in top 3
  - Recall@5: Target in top 5
  - MRR: Average quality of ranking
  - **Baseline Expectations**: Recall@5 = 70-85%
  - **Tutorial**: [HW4 Retrieval Metrics](../homeworks/hw4/TUTORIAL_INDEX.md)

- **Yes** → Continue to Q4

**Q4: Is baseline performance sufficient (>80% Recall@5)?**
- **Yes** → Done! Monitor in production
  - Consider: Error analysis on failures
  - Track: Query types that fail

- **No** → Implement **Query Rewrite Agent** (HW4 Optional)
  - Keywords extraction strategy
  - Query rewriting strategy
  - Query expansion strategy
  - **Expected Improvement**: 5-15% Recall@5
  - **Cost**: Additional LLM calls per query
  - **Tutorial**: [HW4 Query Rewrite Agent](../homeworks/hw4/TUTORIAL_INDEX.md)

---

### 🤖 Evaluating Agent Pipelines

**Goal**: Debug multi-step agent workflows and identify bottlenecks

#### Decision Path

**START**: You have a multi-step agent system with failures

**Q1: Do you know where in the pipeline failures occur?**
- **No** → Use **Transition Matrix Analysis** (HW5)
  - Model agent as state machine
  - Identify last successful state → first failing state
  - Build frequency heatmap
  - **Prerequisites**: Labeled failure traces (100+ examples)
  - **Output**: Bottleneck identification (which states fail most)
  - **Tutorial**: [HW5 Transition Matrix Analysis](../homeworks/hw5/TUTORIAL_INDEX.md)

- **Yes** → Continue to Q2

**Q2: Are failures related to tool usage?**
- **Yes** → Use **Substantiation Evaluation** (Lesson 4)
  - Verify agent responses are grounded in tool outputs
  - Detect hallucinations / fabrications
  - **Cost**: $0.50-1.00 for 200 traces (gpt-4o labeling)
  - **Output**: % of responses that are substantiated
  - **Tutorial**: [Lesson 4 Substantiation](../lesson-4/TUTORIAL_INDEX.md)

- **No** → Continue to Q3

**Q3: Do you need to manually investigate edge cases?**
- **Yes** → Use **Trace Inspection** (Lesson 7)
  - Convert JSON traces to human-readable CSV
  - Manual review in spreadsheets
  - Annotate patterns and hypotheses
  - **Cost**: Free (time-intensive)
  - **Tutorial**: [Lesson 7 Trace Inspection](../lesson-7/TUTORIAL_INDEX.md)

- **No** → Consider **Open/Axial Coding** (HW2)
  - Systematic qualitative analysis
  - Build failure taxonomy
  - **Tutorial**: [HW2 Error Analysis](../homeworks/hw2/TUTORIAL_INDEX.md)

---

### 💬 Evaluating Response Quality

**Goal**: Assess correctness, appropriateness, or safety of generated responses

#### Decision Path

**START**: You need to evaluate response quality

**Q1: Are your evaluation criteria objective and clearly defined?**

**Examples of OBJECTIVE criteria:**
- Dietary adherence (vegan recipe contains no animal products)
- Substantiation (claims are backed by tool outputs)
- Format compliance (response follows specified structure)
- Factual accuracy (answer matches ground truth)

**Examples of SUBJECTIVE criteria:**
- Humor quality
- Conversational tone
- Creativity
- User satisfaction

**Answer: OBJECTIVE** → Continue to Q2

**Answer: SUBJECTIVE** → Use **Manual Annotation** (Lesson 7)
- Human reviewers required for subjective judgments
- Create annotation interface (web UI or spreadsheets)
- Measure inter-annotator agreement
- **Cost**: Free (human time)
- **Tutorial**: [Lesson 7 Manual Annotation](../lesson-7/TUTORIAL_INDEX.md)

**Q2: How many examples do you need to evaluate?**
- **<50 examples** → **Manual Labeling**
  - Too few for train/dev/test split
  - Human review is fastest
  - **Cost**: Free (time)

- **50-200 examples** → **LLM-as-Judge (Small Scale)**
  - Create ground truth labels manually or with GPT-4o
  - Build judge with gpt-4o-mini
  - Measure TPR/TNR
  - **Cost**: $0.50-2.00
  - **Tutorial**: [HW3 LLM-as-Judge](../homeworks/hw3/TUTORIAL_INDEX.md)

- **200+ examples** → **LLM-as-Judge (Production Scale)**
  - Use **Parallel Labeling** (Lesson 4) for ground truth
  - Develop judge on train/dev sets
  - Apply bias correction (judgy library)
  - Deploy for production monitoring
  - **Cost**: $2-8 depending on scale
  - **Tutorial**: [HW3 LLM-as-Judge](../homeworks/hw3/TUTORIAL_INDEX.md) + [Lesson 4 Parallel Labeling](../lesson-4/TUTORIAL_INDEX.md)

**Q3: Is this for one-time analysis or ongoing monitoring?**
- **One-time** → Standard LLM-as-Judge workflow (HW3)
- **Ongoing** → Add **Bias Correction** (HW3)
  - Measure judge TPR/TNR on held-out test set
  - Apply statistical correction using judgy library
  - Report corrected success rates with 95% CI
  - **Why**: Accounts for systematic judge errors over time
  - **Tutorial**: [HW3 Bias Correction](../homeworks/hw3/TUTORIAL_INDEX.md)

---

### 💰 Optimizing Production Costs

**Goal**: Reduce inference costs while maintaining quality

#### Decision Path

**START**: Your production system is too expensive

**Q1: Can you use a cheaper model for some queries?**

**Requirements for cascading:**
- Cheap model must provide confidence scores (logprobs)
- Expensive model must handle hard cases well
- At least 60% of queries should be "easy"

**Answer: No** → Consider:
- Caching frequent queries
- Batch processing
- Prompt optimization (shorter prompts)
- Alternative providers

**Answer: Yes** → Use **Model Cascades** (Lesson 8)

**Q2: What is your accuracy target?**
- **95%+** → Set high confidence threshold (0.95-0.99)
  - Routes 40-60% to cheap model
  - Savings: 40-50%

- **99%+** → Set very high threshold (0.99)
  - Routes 20-40% to cheap model
  - Savings: 20-30%
  - **Note**: Diminishing returns at very high accuracy

**Q3: Implement cascade workflow:**

1. **Baseline Measurement**
   - Measure cheap model accuracy (gpt-4o-mini)
   - Measure expensive model accuracy (gpt-4o)
   - Calculate cost per 1000 queries for each

2. **Confidence Extraction**
   - Get logprobs from cheap model
   - Normalize to confidence scores
   - **Library**: litellm with logprobs=True

3. **Threshold Optimization**
   - Test thresholds: 0.70, 0.80, 0.90, 0.95, 0.99
   - For each, measure:
     - % routed to cheap model
     - Final cascade accuracy
     - Total cost
   - Select threshold meeting accuracy target with max savings

4. **Production Deployment**
   - Implement routing logic
   - Monitor: accuracy drift, cost savings, latency
   - Adjust threshold as needed

**Expected Results**:
- **Cost Savings**: 40-70% vs. expensive-only
- **Accuracy**: Matches expensive model on aggregate
- **Latency**: Slight increase (sequential calls)

**Tutorial**: [Lesson 8 Model Cascades](../lesson-8/TUTORIAL_INDEX.md)

---

## By Resource Constraints

### 💸 Limited Budget (<$5 total)

**Constraint**: Minimal API costs acceptable

#### Recommended Techniques

**FREE (Time-intensive):**
- ✅ Manual labeling and annotation
- ✅ Open/Axial coding (HW2)
- ✅ BM25 retrieval (no API costs)
- ✅ Transition matrix analysis (HW5)
- ✅ Trace inspection (Lesson 7)

**LOW COST ($0.10-0.50):**
- ✅ gpt-4o-mini as judge (HW3: $0.03-0.05 per 100 examples)
- ✅ Synthetic query generation with gpt-4o-mini (HW2/HW4: $0.05-0.15 per 100 queries)
- ✅ DEMO modes in notebooks (5-10 examples only)

**AVOID:**
- ❌ GPT-4o for bulk labeling ($0.50-1.00 per 150 examples)
- ❌ Large-scale parallel labeling (Lesson 4: $2-8 for 200+ traces)
- ❌ Expensive query rewrite agents (HW4 Optional)

#### Decision Logic

```
If budget < $1:
  → Use manual methods exclusively
  → Test with <20 examples
  → Use DEMO modes

If budget $1-5:
  → Use gpt-4o-mini for automated tasks
  → Limit evaluation to 100-200 examples
  → Use sampling instead of exhaustive evaluation
```

---

### ⏱️ Limited Time (<2 hours)

**Constraint**: Need quick insights

#### Recommended Techniques

**FAST (15-30 minutes):**
- ✅ Baseline metrics (simple accuracy, Recall@1)
- ✅ DEMO modes in notebooks
- ✅ Parallel processing (ThreadPoolExecutor)
- ✅ Sampling (100 examples, not 1000)

**MODERATE (30-60 minutes):**
- ✅ Query diversity analysis (HW1)
- ✅ BM25 + Recall@k (HW4)
- ✅ Transition matrix (HW5, if traces ready)

**AVOID:**
- ❌ Manual labeling at scale (200+ examples = several hours)
- ❌ Complex multi-stage pipelines
- ❌ Exhaustive hyperparameter tuning
- ❌ Building custom annotation tools

#### Decision Logic

```
If time < 30 minutes:
  → Use DEMO modes
  → Calculate baseline metrics only
  → Sample 20-50 examples max

If time 30min - 2hrs:
  → Use parallel processing
  → Focus on one technique
  → Skip advanced analysis (e.g., bias correction)
```

---

### 📊 Limited Labeled Data (<50 examples)

**Constraint**: Insufficient data for train/dev/test split

#### Recommended Techniques

**WORK WITH SMALL DATA:**
- ✅ Manual annotation workflows
- ✅ Qualitative analysis (open/axial coding)
- ✅ Simple heuristic rules
- ✅ Synthetic query generation for expansion (HW2/HW4)
- ✅ Unsupervised methods (clustering, anomaly detection)

**AVOID:**
- ❌ Train/dev/test splitting (need 100+ examples)
- ❌ LLM-as-Judge (unreliable TPR/TNR with <50 examples)
- ❌ Statistical bias correction (requires larger test set)
- ❌ Complex ML-based evaluation

#### Decision Logic

```
If labeled_data < 50:
  → Use qualitative methods (HW2 open coding)
  → Generate synthetic data to expand (HW2/HW4)
  → Manual review with simple heuristics

If labeled_data 50-100:
  → Consider LLM-as-Judge but with caution
  → Use smaller splits (20/30/50 instead of 15%/40%/45%)
  → Report confidence intervals (wider with less data)

If labeled_data > 100:
  → Full LLM-as-Judge workflow (HW3)
  → Parallel labeling for scale (Lesson 4)
```

---

## By Accuracy Requirements

### 🔬 Exploratory (80-90% accuracy acceptable)

**Goal**: Quick insights, hypothesis generation

#### Approach
- Simple baselines
- Manual review of failures
- Identify patterns informally

#### Recommended Techniques
- **Prompt Engineering** (HW1): Trial and error acceptable
- **Query Diversity** (HW1): Rough dimension coverage
- **Open Coding** (HW2): Informal note-taking on failures
- **Basic Metrics** (HW4): Recall@1 only, skip MRR
- **Heuristic Rules**: "If query contains X, expect Y"

#### Avoid
- Rigorous statistical methods
- Extensive labeling efforts
- Bias correction
- Production-grade tooling

---

### 🏭 Production (95%+ accuracy required)

**Goal**: Reliable automated system

#### Approach
- Rigorous evaluation methodology
- Confidence intervals
- Multi-tier validation

#### Recommended Techniques
- **LLM-as-Judge** (HW3) with proper train/dev/test splits
- **Bias Correction** (HW3) using judgy library
- **Substantiation Evaluation** (Lesson 4) for agent systems
- **Transition Matrix Analysis** (HW5) for bottleneck identification
- **Parallel Labeling** (Lesson 4) for scale

#### Requirements
- 100+ labeled examples
- Test set held out until final evaluation
- Confidence intervals reported (95% CI)
- Error analysis on all failure modes

---

### 🚨 Safety-Critical (99%+ accuracy, human oversight)

**Goal**: Prevent dangerous failures

#### Approach
- Human-in-the-loop required
- Multiple validation layers
- Conservative thresholds

#### Recommended Techniques
- **Manual Annotation** (Lesson 7) for ground truth
- **LLM-as-Judge** (HW3) for pre-screening only
- **Substantiation** (Lesson 4) to prevent fabrication
- **Expert Review** for edge cases
- **Conservative Cascades** (Lesson 8) with threshold=0.99

#### Requirements
- Human expert review for all high-risk outputs
- Regular audit of automated judges
- Fail-safe mechanisms (e.g., "I don't know" responses)
- Incident logging and post-mortem analysis

---

## By Development Stage

### 🌱 Stage 1: Initial Development

**Status**: Building first prototype

**Focus**: Rapid iteration, learning what works

#### Recommended Path
1. **Prompt Engineering** (HW1) → Define system behavior
2. **Query Diversity** (HW1) → Create 10-20 test queries
3. **Manual Testing** → Spot-check responses
4. **Iterate** → Refine prompt based on observations

**Avoid**: Premature automation, extensive labeling

---

### 🌿 Stage 2: Known Failure Modes

**Status**: System works sometimes, fails in specific cases

**Focus**: Systematically identify and categorize failures

#### Recommended Path
1. **Bulk Testing** → Generate 50-100 conversation traces
2. **Open/Axial Coding** (HW2) → Qualitative failure analysis
3. **Failure Taxonomy** (HW2) → Document failure modes
4. **Synthetic Query Generation** (HW2) → Test specific failure modes
5. **Iterate** → Fix failures, expand test coverage

---

### 🌳 Stage 3: Pre-Production

**Status**: System mostly works, need rigorous validation

**Focus**: Quantify performance, ensure reliability

#### Recommended Path
1. **Ground Truth Creation** (HW3 or Lesson 4) → Label 100-200 examples
2. **LLM-as-Judge Development** (HW3) → Automate evaluation
3. **Bias Correction** (HW3) → Statistical rigor
4. **Metrics Measurement**:
   - **For RAG**: Recall@k, MRR (HW4)
   - **For Agents**: Transition matrix (HW5), substantiation (Lesson 4)
5. **Error Analysis** → Investigate remaining failures
6. **Report** → Document performance with confidence intervals

---

### 🌲 Stage 4: Production Monitoring

**Status**: System deployed, need ongoing quality assurance

**Focus**: Cost optimization, drift detection, incident response

#### Recommended Path
1. **Automated Evaluation** (HW3) → LLM-as-Judge on sample of traffic
2. **Cost Optimization** (Lesson 8) → Model cascades
3. **Drift Detection** → Monitor metrics over time
4. **Incident Response**:
   - **Trace Inspection** (Lesson 7) for debugging
   - **Transition Matrix** (HW5) for pattern changes
   - **Substantiation** (Lesson 4) for fabrication detection
5. **Periodic Re-validation** → Re-measure TPR/TNR quarterly

---

## By Scale

### 🔬 Small Scale (<100 examples)

**Approach**: Manual or semi-automated

**Techniques**:
- Manual labeling
- Spreadsheet-based analysis
- Simple heuristics
- Qualitative methods (HW2 coding)

---

### 🏢 Medium Scale (100-1000 examples)

**Approach**: Automated with human validation

**Techniques**:
- LLM-as-Judge (HW3)
- Parallel labeling with sampling (Lesson 4)
- Statistical metrics with confidence intervals
- Spot-checking (10-20% human review)

---

### 🏭 Large Scale (1000+ examples)

**Approach**: Fully automated with monitoring

**Techniques**:
- Production LLM-as-Judge with bias correction
- Model cascades for cost optimization (Lesson 8)
- Automated drift detection
- Sampling for periodic human audit

---

## Decision Tree Summary

### Quick Routing Logic

```python
def recommend_technique(problem, budget, time, data_size, accuracy_target):
    # Problem type routing
    if problem == "system_prompts":
        return "HW1: Prompt Engineering + Query Diversity"

    elif problem == "retrieval":
        return "HW4: BM25 + Recall@k + MRR"

    elif problem == "agent_pipeline":
        if "bottleneck" in context:
            return "HW5: Transition Matrix Analysis"
        elif "tool_grounding" in context:
            return "Lesson 4: Substantiation Evaluation"
        else:
            return "Lesson 7: Trace Inspection"

    elif problem == "response_quality":
        if criteria_objective and data_size >= 100:
            return "HW3: LLM-as-Judge"
        else:
            return "Lesson 7: Manual Annotation"

    elif problem == "cost_optimization":
        return "Lesson 8: Model Cascades"

    # Resource constraint overrides
    if budget < 1:
        return "Use manual methods or DEMO modes only"

    if time < 30:
        return "Use baseline metrics, DEMO modes, sampling"

    if data_size < 50:
        return "HW2: Open/Axial Coding (qualitative)"

    # Accuracy requirement overrides
    if accuracy_target >= 0.99:
        return "Manual annotation + LLM-as-Judge pre-screening"

    # Default for medium scale, production
    return "HW3: LLM-as-Judge with bias correction"
```

---

## Next Steps

After using these decision trees:
1. **Validate choice**: Review [techniques-catalog.md](techniques-catalog.md) for detailed prerequisites
2. **Check resources**: See [tools-index.yaml](tools-index.yaml) for required libraries
3. **Follow tutorial**: Navigate to source tutorial (linked throughout)
4. **Use patterns**: Consult [patterns.md](patterns.md) for implementation details

---

**For quick overview**: See [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
**For all techniques**: See [techniques-catalog.md](techniques-catalog.md)
**For methodology families**: See [families/](families/) directory
