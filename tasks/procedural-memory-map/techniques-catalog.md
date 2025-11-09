# LLM Evaluation Techniques Catalog

**Human-readable guide to all evaluation techniques**

> **For machine-readable format**: See [techniques-catalog.yaml](techniques-catalog.yaml)

---

## Table of Contents

- [How to Use This Catalog](#how-to-use-this-catalog)
- [Technique Families](#technique-families)
- [All Techniques (Alphabetical)](#all-techniques-alphabetical)
- [Techniques by Use Case](#techniques-by-use-case)
- [Techniques by Difficulty](#techniques-by-difficulty)

---

## How to Use This Catalog

### For AI Assistants

```python
# Query pattern
user_problem = "Need to evaluate RAG retrieval"

# 1. Search catalog by keywords
matching_techniques = search("retrieval", "RAG")
# → Returns: bm25_retrieval, recall_at_k, mrr_calculation

# 2. Check prerequisites
for technique in matching_techniques:
    check_prerequisites(technique)

# 3. Return recommendation with reasoning
recommend_technique_with_context()
```

### For Developers

1. **Find your problem**: Search this page with Ctrl+F
2. **Check prerequisites**: Ensure you have required knowledge/tools/data
3. **Follow tutorial**: Click source_tutorial link
4. **Use patterns**: Reference [patterns.md](patterns.md) for common implementations

---

## Technique Families

### 1. Qualitative Methods
**When to use**: Initial exploration, unknown failure modes, building taxonomies

| Technique | Difficulty | Time | Cost |
|-----------|------------|------|------|
| [Prompt Engineering](#prompt-engineering) | Beginner | 1-2 hrs | Free |
| [Query Diversity](#query-diversity-testing) | Beginner | 30-60 min | Free |
| [Open Coding](#open-coding-qualitative-analysis) | Beginner | 2-3 hrs | Free |
| [Axial Coding](#axial-coding-pattern-grouping) | Beginner | 1-2 hrs | Free |
| [Failure Taxonomy](#failure-taxonomy-construction) | Intermediate | 1-2 hrs | Free |
| [Manual Annotation](#manual-annotation-workflow) | Beginner | 2-5 min/trace | Free |

### 2. Quantitative Metrics
**When to use**: Known evaluation criteria, need numeric benchmarks

| Technique | Difficulty | Time | Cost |
|-----------|------------|------|------|
| [TPR/TNR Measurement](#tpr-tnr-measurement) | Intermediate | 10-15 min | Free |
| [Recall@k](#recall-at-k-measurement) | Intermediate | 15-30 min | Free |
| [MRR Calculation](#mean-reciprocal-rank-mrr-calculation) | Intermediate | 15-30 min | Free |

### 3. Automated Evaluation
**When to use**: Scale evaluation (100+ examples), objective criteria exist

| Technique | Difficulty | Time | Cost |
|-----------|------------|------|------|
| [Ground Truth Labeling](#ground-truth-labeling) | Intermediate | 15-30 min | $0.50-1.00 |
| [Dataset Splitting](#train-dev-test-dataset-splitting) | Beginner | 5-10 min | Free |
| [LLM-as-Judge](#llm-as-judge-evaluation) | Intermediate | 2-3 hrs | $0.03-0.05 per 100 |
| [Bias Correction](#statistical-bias-correction-judgy-library) | Advanced | 10-15 min | Free |
| [Synthetic Query Generation](#synthetic-query-generation-dimension-tuples) | Intermediate | 30-60 min | $0.05-0.40 |
| [Salient Fact Extraction](#salient-fact-extraction-for-query-generation) | Intermediate | 1-5 min | $0.05-2.00 |
| [Parallel Labeling](#parallel-llm-labeling-threadpoolexecutor) | Advanced | 5-8 min | $0.50-1.00 per 200 |
| [Substantiation Evaluation](#substantiation-evaluation-tool-grounding) | Advanced | 3-4 hrs | $0.50-2.00 |

### 4. Optimization Techniques
**When to use**: Production deployment, cost constraints, performance improvement

| Technique | Difficulty | Time | Cost |
|-----------|------------|------|------|
| [BM25 Retrieval](#bm25-retrieval-implementation) | Intermediate | 30-60 min | Free |
| [Query Rewrite Agent](#query-rewrite-agent-retrieval-enhancement) | Advanced | 1-2 hrs | $0.50-2.00 |
| [Logprob Extraction](#log-probability-extraction-confidence-scores) | Intermediate | 30 min | Free |
| [Confidence Thresholding](#confidence-thresholding-routing-logic) | Intermediate | 1-2 hrs | Free |
| [Model Cascades](#model-cascades-cost-accuracy-optimization) | Advanced | 2-3 hrs | Varies |
| [Cost-Accuracy Optimization](#cost-accuracy-trade-off-analysis) | Intermediate | 1-2 hrs | Free |

### 5. Debugging Methods
**When to use**: System has known issues, need root cause analysis

| Technique | Difficulty | Time | Cost |
|-----------|------------|------|------|
| [Data Preprocessing](#conversation-log-preprocessing) | Beginner | 30-60 min | Free |
| [CSV Conversion](#trace-to-csv-conversion-manual-review) | Beginner | 15-30 min | Free |
| [State-Based Modeling](#state-based-agent-modeling) | Intermediate | 30-60 min | Free |
| [Transition Matrix Analysis](#transition-matrix-analysis-failure-patterns) | Intermediate | 1-2 hrs | Free |
| [Bottleneck Identification](#agent-bottleneck-identification) | Intermediate | 30-60 min | Free |

---

## All Techniques (Alphabetical)

### Agent Bottleneck Identification
**ID**: `bottleneck_identification` | **Family**: Debugging Methods | **Difficulty**: Intermediate

**When to use**:
- After transition matrix analysis
- Want to prioritize which states to fix first
- Need to explain findings to team

**Prerequisites**: Transition matrix with failure frequencies

**Key insight**: Sum column totals in transition matrix to find states that fail most often. Distinguish LLM failures (argument generation) from tool failures (execution errors) to propose targeted fixes.

**Tutorial**: [HW5](../../homeworks/hw5/TUTORIAL_INDEX.md)

---

### Axial Coding (Pattern Grouping)
**ID**: `axial_coding` | **Family**: Qualitative Methods | **Difficulty**: Beginner

**When to use**:
- After open coding, need to organize findings
- Want to group observations into categories
- Building structured failure taxonomy

**Prerequisites**: Open codes from previous analysis

**Key steps**: Group open codes into 3-7 top-level categories, ensure mutual exclusivity, define relationships between failure modes.

**Anti-pattern**: ❌ Creating too many categories (20+) dilutes focus

**Tutorial**: [HW2](../../homeworks/hw2/TUTORIAL_INDEX.md)

---

### Bias Correction → Statistical Bias Correction (judgy library)
**ID**: `bias_correction` | **Family**: Automated Evaluation | **Difficulty**: Advanced

**When to use**:
- Judge has known TPR/TNR measured on test set
- Reporting corrected success rates for production
- Want to account for systematic judge errors

**When NOT to use**:
- Judge TPR/TNR unknown or unreliable
- Perfect judge (TPR=TNR=1.0, no correction needed)
- Test set too small (<30 examples)

**Formula**: `θ̂ = (p_obs + TNR - 1) / (TPR + TNR - 1)`

**Why it matters**: A judge with 90% TPR and 95% TNR reporting 85% pass rate might indicate a **true** rate of 92%±5%. Bias correction accounts for systematic judge errors.

**Tutorial**: [HW3](../../homeworks/hw3/TUTORIAL_INDEX.md)

---

### BM25 Retrieval Implementation
**ID**: `bm25_retrieval` | **Family**: Optimization Techniques | **Difficulty**: Intermediate

**When to use**:
- Building RAG system with keyword-based retrieval
- Want fast, interpretable retrieval (no embeddings)
- Avoiding API costs

**When NOT to use**:
- Need semantic similarity (use embeddings instead)
- Queries and documents use very different vocabulary (semantic gap)

**Key implementation pattern**:
```python
from rank_bm25 import BM25Okapi
import pickle

# Build index
tokenized_docs = [doc.lower().split() for doc in documents]
bm25 = BM25Okapi(tokenized_docs)

# Save for reuse
with open('bm25_index.pkl', 'wb') as f:
    pickle.dump(bm25, f)

# Query
query_tokens = query.lower().split()
top_k_indices = bm25.get_top_n(query_tokens, range(len(documents)), n=5)
```

**Tutorial**: [HW4](../../homeworks/hw4/TUTORIAL_INDEX.md)

---

### Confidence Thresholding (Routing Logic)
**ID**: `confidence_thresholding` | **Family**: Optimization Techniques | **Difficulty**: Intermediate

**When to use**:
- Have confidence scores from cheap model
- Want to route uncertain queries to expensive model
- Building cascade system

**Threshold selection guide**:
- **0.70**: Routes 95% to cheap → Lower accuracy, max cost savings
- **0.90**: Routes 85% to cheap → Good balance ✅
- **0.95**: Routes 70% to cheap → Higher accuracy, moderate savings
- **0.99**: Routes 40% to cheap → Highest accuracy, minimal savings

**Decision logic**:
```python
if cheap_model_confidence >= threshold:
    return cheap_model_answer  # High confidence
else:
    return expensive_model_answer  # Low confidence, needs expert
```

**Tutorial**: [Lesson 8](../../lesson-8/TUTORIAL_INDEX.md)

---

### Conversation Log Preprocessing
**ID**: `data_preprocessing` | **Family**: Debugging Methods | **Difficulty**: Beginner

**When to use**:
- Have raw CSV logs from production
- Logs contain malformed JSON in cells
- Need structured JSON for analysis

**Common issues handled**:
- Escaped quotes in JSON strings
- Nested JSON structures
- Missing or incomplete fields
- Encoding problems

**Tutorial**: [Lesson 4](../../lesson-4/TUTORIAL_INDEX.md)

---

### Cost-Accuracy Trade-off Analysis
**ID**: `cost_accuracy_optimization` | **Family**: Optimization Techniques | **Difficulty**: Intermediate

**When to use**:
- Multiple model options with different costs/quality
- Need to justify model selection to stakeholders
- Balancing accuracy targets with budget constraints

**Analysis approach**:
1. Measure accuracy for each model on same test set
2. Calculate cost per 1000 queries
3. Plot accuracy vs cost
4. Identify pareto frontier (efficient models)
5. Select model or cascade strategy based on requirements

**Tutorial**: [Lesson 8](../../lesson-8/TUTORIAL_INDEX.md)

---

### CSV Conversion → Trace-to-CSV Conversion (Manual Review)
**ID**: `csv_conversion` | **Family**: Debugging Methods | **Difficulty**: Beginner

**When to use**:
- Need to manually review conversation traces
- Want to use spreadsheet software for annotation
- JSON traces too complex to read directly

**Flattening pattern**:
```python
conversation_text = "\n".join([
    f"{msg['role'].upper()}: {msg['content']}"
    for msg in messages
])
```

**CSV columns typically include**:
- `trace_id`: Unique identifier
- `user_query`: Initial user message
- `conversation`: Formatted message history
- `tool_calls`: Summarized tool usage
- `failure_mode`: (if labeled)

**Tutorial**: [Lesson 7](../../lesson-7/TUTORIAL_INDEX.md)

---

### Dataset Splitting → Train/Dev/Test Dataset Splitting
**ID**: `dataset_splitting` | **Family**: Automated Evaluation | **Difficulty**: Beginner

**When to use**:
- Building any ML-style evaluation system
- Want to avoid overfitting to test data
- Have 100+ labeled examples

**Standard split ratios**: 15% train / 40% dev / 45% test

**Why these ratios?**
- **Train (15%)**: Few-shot examples for judge prompt (need 5-10 examples)
- **Dev (40%)**: Iterate on judge prompt without test set contamination
- **Test (45%)**: Final evaluation to measure true performance

**Hash-based deterministic splitting** (reproducible):
```python
import hashlib

def get_split(record_id):
    hash_val = int(hashlib.sha256(record_id.encode()).hexdigest(), 16)
    bucket = hash_val % 100
    if bucket < 15: return "train"
    elif bucket < 55: return "dev"
    else: return "test"
```

**Tutorial**: [HW3](../../homeworks/hw3/TUTORIAL_INDEX.md)

---

### Failure Taxonomy Construction
**ID**: `failure_taxonomy` | **Family**: Qualitative Methods | **Difficulty**: Intermediate

**When to use**:
- After axial coding, need formal documentation
- Want to communicate failure modes to team
- Building reference for future evaluation

**Template for each failure mode**:
```markdown
### Failure Mode: [Title]

**Definition:** [One sentence describing when this failure occurs]

**Examples:**
1. [Real example from trace X with context]
2. [Real or hypothetical example]

**Frequency:** [Common / Occasional / Rare]
**Severity:** [High / Medium / Low]
**Proposed Fix:** [Brief suggestion]
```

**Tutorial**: [HW2](../../homeworks/hw2/TUTORIAL_INDEX.md)

---

### Ground Truth Labeling
**ID**: `ground_truth_labeling` | **Family**: Automated Evaluation | **Difficulty**: Intermediate

**When to use**:
- Building LLM-as-Judge system
- Need labeled dataset for evaluation
- Criteria are objective and clearly defined

**Model selection for ground truth**:
- ✅ **Use**: GPT-4o, Claude Sonnet (highest quality)
- ❌ **Avoid**: gpt-4o-mini, GPT-3.5 (for ground truth)

**Why**: Ground truth quality directly impacts judge development. Using cheap models here saves $0.50 but compromises entire evaluation system.

**Validation**: Spot-check 10-20% of labels manually to verify quality

**Tutorial**: [HW3](../../homeworks/hw3/TUTORIAL_INDEX.md)

---

### LLM-as-Judge Evaluation
**ID**: `llm_as_judge` | **Family**: Automated Evaluation | **Difficulty**: Intermediate

**When to use**:
- ✅ Clear, objective evaluation criteria exist
- ✅ Need to evaluate 100+ examples at scale
- ✅ Repeatable, consistent judgments required

**When NOT to use**:
- ❌ Highly subjective criteria (e.g., "Is this funny?")
- ❌ Safety-critical applications requiring human review
- ❌ Very small datasets (<50 examples)

**Complete workflow**:
1. Create ground truth labels (150 examples with GPT-4o)
2. Split dataset (15% train, 40% dev, 45% test)
3. Engineer judge prompt with clear criteria
4. Select few-shot examples from train set (1 PASS : 3 FAIL ratio recommended)
5. Iterate on dev set to improve TPR/TNR
6. **Final evaluation on test set (ONCE ONLY)**
7. Report metrics with confidence intervals

**Expected performance**: TPR/TNR >90% is excellent, 80-90% is acceptable, <80% needs prompt refinement.

**Tutorial**: [HW3](../../homeworks/hw3/TUTORIAL_INDEX.md)

---

### Logprob Extraction → Log Probability Extraction (Confidence Scores)
**ID**: `logprob_extraction` | **Family**: Optimization Techniques | **Difficulty**: Intermediate

**When to use**:
- Building model cascade
- Need confidence scores for routing decisions
- Binary or multi-class classification tasks

**Implementation**:
```python
import litellm
import math

response = litellm.completion(
    model="gpt-4o-mini",
    messages=[...],
    logprobs=True,
    max_tokens=1
)

# Extract logprobs for answer tokens
logprobs_dict = response.choices[0].logprobs.content[0].top_logprobs

# Convert to probabilities
probs = {token: math.exp(data.logprob) for token, data in logprobs_dict.items()}

# Normalize
total = sum(probs.values())
normalized = {k: v/total for k, v in probs.items()}

# Get confidence for predicted answer
confidence = normalized[predicted_answer]
```

**Tutorial**: [Lesson 8](../../lesson-8/TUTORIAL_INDEX.md)

---

### Manual Annotation Workflow
**ID**: `manual_annotation` | **Family**: Qualitative Methods | **Difficulty**: Beginner

**When to use**:
- Evaluation criteria are subjective
- Building initial labeled dataset (<100 examples)
- Validating automated labels
- Safety-critical applications

**Annotation best practices**:
1. **Define criteria clearly** (write 1-page guide)
2. **Provide 3-5 examples** (pass and fail cases)
3. **Track uncertain cases** (separate column)
4. **Measure inter-annotator agreement** (if multiple annotators)
5. **Document edge cases** (for future reference)

**Time estimates**: 2-5 minutes per trace (simple binary), 5-10 minutes (complex multi-class)

**Tutorial**: [Lesson 7](../../lesson-7/TUTORIAL_INDEX.md)

---

### Mean Reciprocal Rank (MRR) Calculation
**ID**: `mrr_calculation` | **Family**: Quantitative Metrics | **Difficulty**: Intermediate

**When to use**:
- Want to measure ranking quality (not just top-k)
- Care about position of target document
- Comparing multiple retrieval strategies

**Formula**: `MRR = (1/N) × Σ(1 / rank_i)`

**Example**:
```
Query 1: Target at rank 1 → RR = 1.0
Query 2: Target at rank 3 → RR = 0.33
Query 3: Target at rank 2 → RR = 0.5
Query 4: Target not found → RR = 0.0

MRR = (1.0 + 0.33 + 0.5 + 0.0) / 4 = 0.46
```

**Interpretation**: MRR = 0.46 means target averages around rank 2-3.

**Tutorial**: [HW4](../../homeworks/hw4/TUTORIAL_INDEX.md)

---

### Model Cascades (Cost-Accuracy Optimization)
**ID**: `model_cascades` | **Family**: Optimization Techniques | **Difficulty**: Advanced

**When to use**:
- Production costs too high
- Many queries are "easy" (can use cheap model)
- Can accept sequential latency overhead

**Requirements for success**:
- Cheap model must have ≥80% accuracy (baseline)
- Confidence scores must be reliable
- At least 60% of queries should route to cheap model (for meaningful savings)

**Expected results**:
- **Cost Savings**: 40-70% vs expensive-only
- **Accuracy**: Matches expensive model on aggregate
- **Latency**: Slight increase (sequential calls)

**Example**:
```
Baseline (expensive only): 99.2% accuracy, $5.00 per 1000 queries
Cheap only: 96.5% accuracy, $0.50 per 1000 queries

Cascade (threshold=0.90):
  → 87% routed to cheap model
  → 13% routed to expensive model
  → Final accuracy: 99.1%
  → Cost: (870 × $0.0005) + (130 × $0.005) = $1.09
  → Savings: 78% vs expensive-only
```

**Tutorial**: [Lesson 8](../../lesson-8/TUTORIAL_INDEX.md)

---

### Open Coding (Qualitative Analysis)
**ID**: `open_coding` | **Family**: Qualitative Methods | **Difficulty**: Beginner

**When to use**:
- Unknown failure modes - exploring patterns
- Initial error analysis on conversation traces
- Building labeled dataset from scratch

**Methodology** (from Grounded Theory):
- Review traces **without** preconceived categories
- Assign descriptive labels to interesting patterns
- Take detailed notes on observations
- Look for recurring themes
- Avoid forcing observations into predetermined buckets

**Example codes**:
```
Trace 42: Bot suggested honey for vegan recipe
  → Code: "Dietary restriction violation"
  → Code: "Knowledge gap: honey classification"

Trace 58: Bot provided 15-ingredient recipe for "quick meal"
  → Code: "Misalignment with user intent"
  → Code: "No time constraint interpretation"
```

**Tutorial**: [HW2](../../homeworks/hw2/TUTORIAL_INDEX.md)

---

### Parallel LLM Labeling (ThreadPoolExecutor)
**ID**: `parallel_labeling` | **Family**: Automated Evaluation | **Difficulty**: Advanced

**When to use**:
- Need to label 200+ examples with LLM
- Want to reduce labeling time from 40min to 5min
- Have API rate limit headroom

**Performance**:
- Sequential: ~200 traces in 30-40 minutes
- Parallel (10 workers): ~200 traces in 5-8 minutes
- Parallel (64 workers): ~200 traces in 3-5 minutes (if API permits)

**Implementation pattern**:
```python
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

def label_one_trace(trace):
    # Call LLM API to label
    return labeled_trace

with ThreadPoolExecutor(max_workers=64) as executor:
    results = list(tqdm(
        executor.map(label_one_trace, traces),
        total=len(traces),
        desc="Labeling"
    ))
```

**Important**: Same total cost, just faster. Start with 10 workers and increase if no rate limit errors.

**Tutorial**: [Lesson 4](../../lesson-4/TUTORIAL_INDEX.md)

---

### Prompt Engineering
**ID**: `prompt_engineering` | **Family**: Qualitative Methods | **Difficulty**: Beginner

**When to use**:
- Building new conversational AI system
- Need to define bot behavior and constraints
- Controlling LLM creativity and output format

**Key components**:
1. **Role definition**: "You are a [specific role] specializing in [domain]"
2. **Behavioral rules**: "Always [X]. Never [Y]."
3. **Output format**: "Structure responses using Markdown with sections"
4. **Safety clauses**: "If asked to [harmful action], politely decline"
5. **Agency control**: "Do not [unauthorized action] without user confirmation"

**Length guideline**: 100-300 words. Long enough to be specific, short enough to be clear.

**Tutorial**: [HW1](../../homeworks/hw1/TUTORIAL_INDEX.md)

---

### Query Diversity Testing
**ID**: `query_diversity` | **Family**: Qualitative Methods | **Difficulty**: Beginner

**When to use**:
- Need systematic test coverage
- Want to stress-test system across dimensions
- Building initial evaluation dataset

**Dimension identification** (Recipe chatbot example):
- Cuisine: Italian, Thai, Mexican, Indian, French
- Dietary: Vegan, vegetarian, gluten-free, keto, paleo
- Meal Type: Breakfast, lunch, dinner, snack, dessert
- Cooking Time: <15min, 15-30min, 30-60min, >60min
- Skill Level: Beginner, intermediate, advanced

**Coverage calculation**: 5 × 5 × 5 × 4 × 3 = 1500 possible combinations → Select 10-20 representative ones

**Tutorial**: [HW1](../../homeworks/hw1/TUTORIAL_INDEX.md)

---

### Query Rewrite Agent (Retrieval Enhancement)
**ID**: `query_rewrite_agent` | **Family**: Optimization Techniques | **Difficulty**: Advanced

**When to use**:
- Baseline retrieval performance is insufficient (<70% Recall@5)
- Want to improve hard queries
- Have budget for additional LLM calls

**Three strategies**:
1. **Keywords extraction**: Extract key terms for better matching
2. **Query rewriting**: Rephrase query in document vocabulary
3. **Query expansion**: Add synonyms and related terms

**Expected improvement**: 5-15% Recall@5 increase

**Cost consideration**: Adds one LLM call per query. Calculate ROI: (% improvement) vs (additional cost)

**Tutorial**: [HW4 Optional](../../homeworks/hw4/TUTORIAL_INDEX.md)

---

### Recall@k Measurement
**ID**: `recall_at_k` | **Family**: Quantitative Metrics | **Difficulty**: Intermediate

**When to use**:
- Evaluating retrieval system performance
- Have queries with known relevant documents
- Want standard IR metric

**Formula**: `Recall@k = (# queries with target in top-k) / (total queries)`

**Typical ranges for well-designed systems**:
- Recall@1: 40-60%
- Recall@3: 60-80%
- Recall@5: 70-90%

**What counts as "good"**: Depends on domain and query difficulty. For well-formed queries with clear targets: 70-85% Recall@5 is solid.

**Tutorial**: [HW4](../../homeworks/hw4/TUTORIAL_INDEX.md)

---

### Salient Fact Extraction (for Query Generation)
**ID**: `salient_fact_extraction` | **Family**: Automated Evaluation | **Difficulty**: Intermediate

**When to use**:
- Need realistic synthetic queries for RAG evaluation
- Want queries that reflect document content
- Cold-start evaluation (no organic queries yet)

**Two-step process**:
1. **Extract facts**: "What are 3-5 salient facts from this document?"
2. **Generate queries**: "Convert each fact into a natural language question"

**Why two-step?** Produces higher quality queries than direct "generate questions" prompts.

**Tutorial**: [HW4](../../homeworks/hw4/TUTORIAL_INDEX.md)

---

### State-Based Agent Modeling
**ID**: `state_based_modeling` | **Family**: Debugging Methods | **Difficulty**: Intermediate

**When to use**:
- Agent has multi-step workflow
- Need to identify where failures occur
- Want to visualize agent pipeline

**Example states** (Recipe agent):
```
1. ParseRequest → Interpret user message
2. PlanToolCalls → Decide which tools to invoke
3. GenRecipeArgs → Construct recipe search arguments
4. GetRecipes → Execute recipe search tool
5. ComposeResponse → Draft final answer
6. DeliverResponse → Send to user
```

**State types**: LLM (argument generation) vs Tool (execution)

**Tutorial**: [HW5](../../homeworks/hw5/TUTORIAL_INDEX.md)

---

### Substantiation Evaluation (Tool Grounding)
**ID**: `substantiation_evaluation` | **Family**: Automated Evaluation | **Difficulty**: Advanced

**When to use**:
- Agent uses tools and might fabricate information
- Need to verify claims are grounded in tool outputs
- Preventing hallucinations in production

**Definition**: A response is SUBSTANTIATED if every factual claim can be verified by:
1. Information provided by user in conversation
2. Tool outputs (results from function calls)
3. Tool metadata (available tools and parameters)
4. Information obtainable by calling available tools

**Example**:
```
Tool Output: {"id": "A11", "price": 1200, "available": true}

✅ SUBSTANTIATED: "Apartment A11 is available for $1200/month"
❌ UNSUBSTANTIATED: "A11 has a beautiful balcony with garden views"
  (Balcony not mentioned in tool output)
```

**Tutorial**: [Lesson 4](../../lesson-4/TUTORIAL_INDEX.md)

---

### Synthetic Query Generation (Dimension Tuples)
**ID**: `synthetic_query_generation` | **Family**: Automated Evaluation | **Difficulty**: Intermediate

**When to use**:
- Need to test specific failure modes systematically
- Want to expand test coverage beyond manual queries
- Cold-start evaluation (no organic queries yet)

**Process**:
1. Identify dimensions (e.g., cuisine, dietary, meal_type)
2. Use LLM to generate dimension tuples
3. Convert tuples to natural language queries
4. Validate quality and diversity

**Example**:
```
Tuple: (Thai, vegan, dinner, <30min)
Query: "Can you suggest a quick Thai vegan dinner recipe that takes less than 30 minutes?"
```

**Tutorial**: [HW2](../../homeworks/hw2/TUTORIAL_INDEX.md)

---

### TPR/TNR Measurement
**ID**: `tpr_tnr_measurement` | **Family**: Quantitative Metrics | **Difficulty**: Intermediate

**When to use**:
- Evaluating binary classifier (including LLM-as-Judge)
- Need to understand false positive vs false negative rates
- Preparing for bias correction

**Formulas**:
- **TPR** (True Positive Rate / Sensitivity): `TP / (TP + FN)`
- **TNR** (True Negative Rate / Specificity): `TN / (TN + FP)`

**Interpretation**:
- **High TPR (95%)**: Judge rarely misses passing examples
- **High TNR (90%)**: Judge rarely misses failing examples
- **Imbalance**: TPR=95%, TNR=70% → Judge is too lenient (false positives)

**Tutorial**: [HW3](../../homeworks/hw3/TUTORIAL_INDEX.md)

---

### Transition Matrix Analysis (Failure Patterns)
**ID**: `transition_matrix_analysis` | **Family**: Debugging Methods | **Difficulty**: Intermediate

**When to use**:
- Have labeled failure traces (100+ examples)
- Want to identify bottlenecks in agent pipeline
- Need data-driven prioritization for fixes

**What it shows**:
- **Rows**: Last successful state (where it worked)
- **Columns**: First failing state (where it broke)
- **Cell values**: Frequency of that transition

**Example insight**:
```
High frequency: GenRecipeArgs → GetRecipes (22 failures)
Interpretation: Recipe search tool fails frequently
Root cause: Invalid search arguments or tool API issues
Action: Improve argument validation or tool error handling
```

**Tutorial**: [HW5](../../homeworks/hw5/TUTORIAL_INDEX.md)

---

## Techniques by Use Case

### I need to evaluate...

#### System Prompts
→ [Prompt Engineering](#prompt-engineering) + [Query Diversity](#query-diversity-testing)

#### Retrieval (RAG)
→ [BM25 Retrieval](#bm25-retrieval-implementation) + [Recall@k](#recall-at-k-measurement) + [MRR](#mean-reciprocal-rank-mrr-calculation)

#### Agent Pipeline Bottlenecks
→ [State-Based Modeling](#state-based-agent-modeling) + [Transition Matrix](#transition-matrix-analysis-failure-patterns)

#### Response Quality (Objective Criteria)
→ [LLM-as-Judge](#llm-as-judge-evaluation) + [Bias Correction](#statistical-bias-correction-judgy-library)

#### Response Quality (Subjective Criteria)
→ [Manual Annotation](#manual-annotation-workflow)

#### Tool Grounding (Prevent Hallucinations)
→ [Substantiation Evaluation](#substantiation-evaluation-tool-grounding)

#### Production Costs
→ [Model Cascades](#model-cascades-cost-accuracy-optimization)

---

## Techniques by Difficulty

### Beginner
Start here if new to LLM evaluation:
- [Prompt Engineering](#prompt-engineering)
- [Query Diversity](#query-diversity-testing)
- [Open Coding](#open-coding-qualitative-analysis)
- [Axial Coding](#axial-coding-pattern-grouping)
- [Dataset Splitting](#train-dev-test-dataset-splitting)
- [CSV Conversion](#trace-to-csv-conversion-manual-review)
- [Manual Annotation](#manual-annotation-workflow)
- [Data Preprocessing](#conversation-log-preprocessing)

### Intermediate
After mastering beginner techniques:
- [Failure Taxonomy](#failure-taxonomy-construction)
- [Synthetic Query Generation](#synthetic-query-generation-dimension-tuples)
- [Ground Truth Labeling](#ground-truth-labeling)
- [LLM-as-Judge](#llm-as-judge-evaluation)
- [TPR/TNR Measurement](#tpr-tnr-measurement)
- [BM25 Retrieval](#bm25-retrieval-implementation)
- [Recall@k](#recall-at-k-measurement)
- [MRR Calculation](#mean-reciprocal-rank-mrr-calculation)
- [Salient Fact Extraction](#salient-fact-extraction-for-query-generation)
- [State-Based Modeling](#state-based-agent-modeling)
- [Transition Matrix](#transition-matrix-analysis-failure-patterns)
- [Bottleneck Identification](#agent-bottleneck-identification)
- [Logprob Extraction](#log-probability-extraction-confidence-scores)
- [Confidence Thresholding](#confidence-thresholding-routing-logic)
- [Cost-Accuracy Optimization](#cost-accuracy-trade-off-analysis)

### Advanced
For production-scale systems:
- [Bias Correction](#statistical-bias-correction-judgy-library)
- [Query Rewrite Agent](#query-rewrite-agent-retrieval-enhancement)
- [Parallel Labeling](#parallel-llm-labeling-threadpoolexecutor)
- [Substantiation Evaluation](#substantiation-evaluation-tool-grounding)
- [Model Cascades](#model-cascades-cost-accuracy-optimization)

---

## Next Steps

**After selecting a technique**:
1. Review complete YAML entry: [techniques-catalog.yaml](techniques-catalog.yaml)
2. Check implementation patterns: [patterns.md](patterns.md)
3. Verify tool requirements: [tools-index.yaml](tools-index.yaml)
4. Follow source tutorial for detailed walkthrough

**For decision support**: See [decision-trees.md](decision-trees.md)
**For quick reference**: See [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
