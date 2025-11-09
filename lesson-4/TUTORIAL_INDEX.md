# Lesson 4: Tutorial Index

## Overview

Lesson 4 teaches **substantiation evaluation** for AI conversational systems. You'll learn to detect when AI assistants make claims that aren't supported by their available tools, data, or conversation context—a critical quality control metric for production systems. The lesson demonstrates the complete LLM-as-Judge pipeline: data preprocessing, ground truth labeling, and judge evaluation.

**Learning Time:** ~4-5 hours
**Difficulty:** Intermediate to Advanced
**Prerequisites:** Understanding of LLM-as-Judge methodology (HW3), JSON/CSV data processing

---

## Learning Objectives

By completing these tutorials, you will be able to:
- ✅ Define substantiation and why it matters for AI safety
- ✅ Distinguish substantiated claims from hallucinations/fabrications
- ✅ Preprocess raw conversation logs into structured JSON
- ✅ Use parallel LLM processing (ThreadPoolExecutor) for efficient labeling
- ✅ Create ground truth labels with GPT-4o for substantiation
- ✅ Split datasets for train/dev/test evaluation
- ✅ Evaluate cheaper judge models on substantiation detection
- ✅ Measure TPR/TNR for binary classification tasks
- ✅ Apply this pipeline to production conversation logs

---

## Tutorials

### 1. Substantiation Concepts
**File:** `substantiation_concepts.md`
**Reading Time:** 15-20 minutes
**Topics:**
- What is substantiation? Definition and importance
- Substantiation vs. hallucination vs. fabrication
- Tool grounding: How tools provide verifiable evidence
- What counts as substantiated information?
- Verifiability criteria for conversational AI
- When to prioritize substantiation evaluation

**When to use:** Start here to understand the conceptual foundation.

**Key Definition:**
```
A response is SUBSTANTIATED if every factual claim can be verified by:
  1. Information provided by the user in conversation
  2. Tool outputs (results from function calls)
  3. Tool metadata (available tools and parameters)
  4. Information obtainable by calling available tools

A response is UNSUBSTANTIATED if it contains claims
that cannot be verified from these sources.
```

---

### 2. Data Preprocessing Tutorial
**File:** `data_preprocessing_tutorial.md`
**Reading Time:** 15-20 minutes
**Topics:**
- Converting raw CSV logs to structured JSON
- Handling malformed JSON in CSV cells
- Incremental processing for large datasets
- Extracting essential fields (role, content, metadata)
- Filtering incomplete or invalid records
- Generating unique conversation IDs

**When to use:** Before labeling, use this to clean your conversation logs.

**Pipeline:**
```
Raw CSV logs (nurtureboss_logs.csv)
  ↓
clean_logs.py → Parse JSON, Extract fields, Filter invalid
  ↓
Structured JSON (nurtureboss_traces.json)
```

---

### 3. Parallel Labeling Tutorial (Interactive)
**File:** `parallel_labeling_tutorial.ipynb`
**Execution Time:**
- **DEMO MODE** (default): 10-15 seconds | Cost: $0.05-0.10 (5 traces)
- **FULL MODE**: 5-8 minutes | Cost: $0.50-1.00 (~200 traces)

**Topics:**
- Using ThreadPoolExecutor for parallel LLM calls (10-20 workers)
- Rate limiting and API quota management
- Progress tracking with tqdm
- Cost optimization (gpt-4o vs gpt-4o-mini comparison)
- Incremental labeling with checkpoint saving (resume after interruption)
- Structured output with Pydantic models
- Error handling for API failures

**When to use:** After preprocessing, use this to create ground truth labels efficiently.

**Interactive Features:**
- Configurable DEMO vs FULL mode for cost control
- Live parallel LLM labeling demonstration
- Cost estimation calculator (compares models)
- Progress bars for long-running operations
- Checkpoint save/resume capability

**Performance Comparison:**
- Sequential: ~200 traces in 30-40 minutes
- Parallel (10 workers): ~200 traces in 5-8 minutes
- Parallel (20 workers): ~200 traces in 3-5 minutes

**⚠️ Requirements:** API key in `.env`, preprocessed JSON traces from `clean_logs.py`

---

### 4. Judge Evaluation Pipeline Tutorial (Interactive)
**File:** `judge_evaluation_pipeline_tutorial.ipynb`
**Execution Time:** 30-60 seconds (DEMO: 20 traces) | Cost: $0.10-0.30
**Full Evaluation:** 5-10 minutes (150 traces) | Cost: $1.00-2.00

**Topics:**
- Deterministic train/dev/test splitting (hash-based, reproducible)
- Balanced few-shot example selection (1 PASS : 1 FAIL)
- Evaluating judge models on binary classification (substantiation)
- TPR/TNR calculation with automated validation
- False positive/negative analysis
- Bias interpretation (too strict vs too lenient)
- When substantiation judges work well vs. poorly

**When to use:** After labeling, use this to evaluate if a cheaper model (gpt-4o-mini) can replace GPT-4o.

**Interactive Features:**
- Cost warning with demo mode (limits to 20 traces by default)
- Dataset splitting with reproducible seeds
- Few-shot prompt construction
- Live judge evaluation on test set with progress indicators
- Automated TPR/TNR metric validation (0-1 range checks)
- Bias analysis output

**⚠️ Requirements:** API key in `.env`, labeled JSON traces from parallel_labeling_tutorial
- Error analysis notebooks

---

### 5. Substantiation Pipeline Diagram (Visual)
**File:** `diagrams/substantiation_pipeline.mmd` | [PNG version](diagrams/substantiation_pipeline.png)
**Format:** Mermaid diagram (viewable on GitHub) | High-resolution PNG export available
**Topics:**
- Complete 3-step pipeline visualization
- Data flow: Raw logs → Clean → Labeled → Evaluated
- Decision points and quality gates
- Iteration loops for prompt refinement

**When to use:** Reference this to understand how all pieces connect.

---

## Recommended Learning Path

```
┌────────────────────────────────────────────────────────┐
│      Lesson 4: Substantiation Evaluation Workflow      │
├────────────────────────────────────────────────────────┤
│                                                        │
│  STEP 1: Understand Substantiation                    │
│  ┌──────────────────────────────────────────────────┐ │
│  │ 1. Read EXPLANATION.md (comprehensive overview)   │ │
│  │ 2. Complete "Substantiation Concepts" tutorial    │ │
│  │ 3. Review example conversations with tool outputs │ │
│  └──────────────────────────────────────────────────┘ │
│                                                        │
│  STEP 2: Data Preprocessing                           │
│  ┌──────────────────────────────────────────────────┐ │
│  │ 4. Complete "Data Preprocessing" tutorial         │ │
│  │ 5. Run clean_logs.py on nurtureboss_logs.csv     │ │
│  │    → Generates nurtureboss_traces.json            │ │
│  │ 6. Inspect cleaned data structure                 │ │
│  └──────────────────────────────────────────────────┘ │
│                                                        │
│  STEP 3: Ground Truth Labeling                        │
│  ┌──────────────────────────────────────────────────┐ │
│  │ 7. Complete "Parallel Labeling" tutorial          │ │
│  │ 8. Run label_substantiation.py                    │ │
│  │    → Uses GPT-4o to label ~200 conversations     │ │
│  │    → Generates nurtureboss_traces_labeled.json   │ │
│  │ 9. Review labeling quality (spot check 10-20)    │ │
│  └──────────────────────────────────────────────────┘ │
│                                                        │
│  STEP 4: Judge Evaluation                             │
│  ┌──────────────────────────────────────────────────┐ │
│  │ 10. Complete "Judge Evaluation Pipeline" tutorial│ │
│  │ 11. Run judge_substantiation.py                  │ │
│  │     → Splits data (train/dev/test)               │ │
│  │     → Selects few-shot examples                  │ │
│  │     → Evaluates judge on each split              │ │
│  │ 12. Analyze TPR/TNR metrics                       │ │
│  │ 13. Identify false positive/negative patterns    │ │
│  └──────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────┘
```

---

## Key Concepts

### Substantiation vs. Hallucination
**Substantiation** focuses on verifiability:
- ✅ **Substantiated:** "Apartment A11 is available and costs $1200/month" (from tool output)
- ❌ **Unsubstantiated:** "Apartment A11 has a beautiful balcony" (not in tool output)

**Hallucination** is a broader term for factually incorrect outputs.
**Substantiation** specifically asks: "Can we verify this claim from available sources?"

### Tool Grounding
**Tool grounding** means using function call results as the source of truth:

**Example Conversation:**
```
User: "Does apartment A11 have a balcony?"
Tool Call: get_apartment_details(id="A11")
Tool Output: {"id": "A11", "price": 1200, "available": true}

✅ SUBSTANTIATED: "Apartment A11 is available for $1200/month"
❌ UNSUBSTANTIATED: "Yes, A11 has a balcony with garden views"
```

The tool output doesn't mention balconies, so claiming balcony details is unsubstantiated.

### Parallel Processing with ThreadPoolExecutor
**Why parallel processing?**
- Labeling 200 conversations sequentially: ~40 minutes
- Labeling 200 conversations with 64 workers: ~5 minutes

**Pattern:**
```python
from concurrent.futures import ThreadPoolExecutor

def label_one_conversation(record):
    # Call LLM API to get label
    return labeled_record

with ThreadPoolExecutor(max_workers=64) as executor:
    results = list(executor.map(label_one_conversation, records))
```

**Considerations:**
- API rate limits (may need to reduce workers)
- Cost (64 parallel calls = faster but same total cost)
- Error handling (what if one conversation fails?)

### Hash-Based Dataset Splitting
**Deterministic splitting** ensures reproducible train/dev/test sets:

```python
import hashlib

def split_category(record_id, train_pct=20, dev_pct=30):
    hash_val = int(hashlib.sha256(record_id.encode()).hexdigest(), 16)
    bucket = hash_val % 100

    if bucket < train_pct:
        return "train"
    elif bucket < train_pct + dev_pct:
        return "dev"
    else:
        return "test"
```

**Benefit:** Same split every time, enables reproducible experiments.

---

## Practical Exercises

After completing the tutorials, try these exercises:

1. **Substantiation Judgment Practice**
   - Read 10 conversation traces with tool outputs
   - For each, decide if the assistant's response is substantiated
   - Compare your judgments to GPT-4o labels
   - Identify cases where you disagree and why

2. **Prompt Engineering Exercise**
   - Modify the substantiation prompt in label_substantiation.py
   - Add clearer decision rules or examples
   - Re-label 20 conversations with your new prompt
   - Compare labels to original—did clarity improve?

3. **Judge Error Analysis**
   - Identify all false positives from judge_substantiation.py output
   - Read the conversation, tool outputs, and judge reasoning
   - Group errors into categories (e.g., "missed subtle claims", "tool output misread")
   - Propose prompt improvements for each category

---

## Common Pitfalls

### Conceptual Misunderstandings
- ❌ **Too strict:** Marking courtesy phrases ("How can I help?") as unsubstantiated
- ❌ **Too lenient:** Accepting paraphrases that add new information not in tools
- ❌ **Ignoring tool metadata:** Forgetting that knowing available tools counts
- ❌ **Binary thinking:** Not recognizing partially substantiated responses

### Data Processing
- ❌ **No validation:** Not checking if JSON parsing succeeded
- ❌ **Missing error handling:** One malformed record crashes entire pipeline
- ❌ **No incremental processing:** Starting over after 190/200 conversations due to API error
- ❌ **Ignoring data quality:** Proceeding with incomplete tool output fields

### Labeling & Evaluation
- ❌ **Wrong model for ground truth:** Using GPT-3.5 instead of GPT-4o
- ❌ **No spot-checking:** Trusting automated labels without human review
- ❌ **Imbalanced splits:** Train set has only "pass" examples
- ❌ **Poor few-shot selection:** Examples don't represent edge cases

---

## Reference Files

### Assignment Materials
- [`EXPLANATION.md`](EXPLANATION.md) - Comprehensive lesson overview (read this first!)
- [`nurtureboss_logs.csv`](nurtureboss_logs.csv) - Raw conversation logs (2MB)
- [`nurtureboss_traces.json`](nurtureboss_traces.json) - Cleaned traces
- [`nurtureboss_traces_labeled.json`](nurtureboss_traces_labeled.json) - With ground truth labels

### Scripts (You'll Run These)
- [`clean_logs.py`](clean_logs.py) - Step 1: Data preprocessing
- [`label_substantiation.py`](label_substantiation.py) - Step 2: Ground truth labeling
- [`judge_substantiation.py`](judge_substantiation.py) - Step 3: Judge evaluation

---

## Tools & Libraries

**Required:**
- `pandas` - CSV/JSON manipulation
- `pydantic` - Structured LLM outputs
- `litellm` - Multi-provider LLM API (OpenAI for GPT-4o)
- `concurrent.futures` - Parallel processing (built-in)
- `tqdm` - Progress bars (optional but recommended)

**Installation:**
```bash
pip install pandas pydantic litellm tqdm
```

**Environment:**
```bash
# Add to .env file
OPENAI_API_KEY=your_key_here
NB_LLM_WORKERS=64  # Adjust based on API rate limits
```

---

## Expected Outputs

After completing Lesson 4, you should have:
- ✅ Cleaned conversation dataset (nurtureboss_traces.json)
- ✅ Labeled dataset with ~200 substantiation judgments
- ✅ Judge evaluation metrics (TPR/TNR on train/dev/test)
- ✅ Understanding of when substantiation evaluation is critical

**Example Metrics:**
```
TRAIN — size  20 | TPR: 95.00% | TNR: 90.00%
DEV   — size  30 | TPR: 93.33% | TNR: 88.89%
TEST  — size 150 | TPR: 94.67% | TNR: 91.33%

Interpretation: The judge successfully identifies most
substantiation violations (91% TNR) with few false alarms.
This enables automated monitoring of production logs.
```

---

## Real-World Applications

This pipeline is used for:
- **Customer support bots:** Ensuring agents don't fabricate product details
- **Medical AI:** Verifying all claims are from approved medical literature
- **Legal assistants:** Confirming all citations are from actual case law
- **Financial advisors:** Ensuring advice is based on user's actual portfolio data

**Key Insight:** Substantiation evaluation prevents the most dangerous AI failure mode—confidently stating incorrect information.

---

## Connection to HW3

Lesson 4 extends the LLM-as-Judge methodology from HW3:

| Aspect | HW3 | Lesson 4 |
|--------|-----|----------|
| **Task** | Dietary adherence | Substantiation |
| **Data** | Recipe bot traces | Customer support traces |
| **Complexity** | Binary (pass/fail) | Binary (substantiated/not) |
| **Unique Challenge** | Dietary definitions | Tool grounding verification |
| **Scale** | 100-200 labels | 200+ labels with parallel processing |

**New Concepts in Lesson 4:**
- Tool grounding and metadata
- Parallel LLM processing at scale
- Production log preprocessing

---

## Next Steps

After completing Lesson 4, you'll have:
- ✅ Production-ready substantiation evaluation pipeline
- ✅ Parallel processing skills for large-scale labeling
- ✅ Understanding of tool grounding for AI safety

**Explore related lessons:**

👉 [Lesson 7: Trace Inspection Tools](../lesson-7/TUTORIAL_INDEX.md)
👉 [Lesson 8: Model Cascades](../lesson-8/TUTORIAL_INDEX.md)

---

## FAQ

**Q: Can I use this pipeline on my own conversation logs?**
A: Yes! Replace nurtureboss_logs.csv with your data (same format), then run the 3 scripts.

**Q: What if I don't have tool outputs in my conversations?**
A: You can still evaluate substantiation against user-provided context, but tool grounding is most powerful.

**Q: Is 64 workers too many for OpenAI API?**
A: Depends on your API tier. Start with 10-20 workers and increase if no rate limit errors.

**Q: Should I manually review all automated labels?**
A: Spot-check 10-20%. If quality is good, trust the rest. If not, refine prompt and re-label.

**Q: Can I use Claude or Gemini instead of GPT-4o?**
A: Yes! litellm supports multiple providers. GPT-4o was used in reference implementation.

**Q: What's a good TPR/TNR for substantiation judges?**
A: >90% for both is excellent. 80-90% is acceptable. <80% needs prompt refinement.

---

**Tutorial Status:** ⏳ In Development
**Last Updated:** 2025-10-29
**Maintainer:** AI Evaluation Course Team
