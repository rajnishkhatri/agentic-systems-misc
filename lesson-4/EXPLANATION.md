# Lesson 4: Evaluating Substantiation in AI Conversations

**📚 [Tutorial Index](TUTORIAL_INDEX.md)** - Comprehensive tutorials, learning paths, and resources for this lesson

---

## Overview

Lesson 4 focuses on detecting a specific failure mode in AI conversational systems: **unsupported or unsubstantiated information**. This is a critical quality control metric that ensures AI assistants only make factual claims that can be verified by their available tools, data, or prior conversation context.

The lesson provides a complete pipeline for:
1. **Data preprocessing**: Converting raw conversation logs into a structured format
2. **Ground truth labeling**: Using LLMs to label conversations for substantiation
3. **Judge evaluation**: Evaluating a cheaper/faster model's ability to detect substantiation failures

## Key Concepts

### What is Substantiation?

A response is **substantiated** if every factual claim made by the AI assistant can be verified by:
- Information provided by the user in the conversation
- Tool outputs (results from function calls)
- Tool metadata (available tools and their parameters)
- Information that could be obtained by calling available tools with arguments derivable from the conversation

A response is **unsubstantiated** if it contains factual claims that cannot be verified from these sources.

**Example of unsubstantiated information:**
- User asks: "Does apartment A11 have a balcony?"
- Assistant responds: "Yes, apartment A11 has a beautiful balcony with a garden view."
- Tool outputs show availability and price for A11, but no mention of balcony features.
- **Verdict**: Unsubstantiated - the assistant claimed balcony details without evidence.

### LLM-as-Judge

This lesson demonstrates the "LLM-as-Judge" evaluation paradigm:
- Use a high-quality LLM (GPT-4.1) to create ground truth labels
- Evaluate a cheaper/faster model's ability to replicate those judgments
- This enables scaling evaluation while maintaining quality standards

## Data Pipeline

### Step 1: Data Preprocessing (`clean_logs.py`)

**Purpose**: Convert raw CSV logs into a structured JSON format suitable for analysis.

**Input**: `nurtureboss_logs.csv`
- Contains conversation logs with JSON-encoded message histories
- Each row has an `input` column with conversation messages
- May include `metadata` column with additional information

**Process**:
1. Reads the CSV file
2. Parses JSON from the `input` and `metadata` columns
3. Extracts only essential fields:
   - `role` and `content` from each message
   - Preserves metadata fields
   - Generates unique IDs for each conversation
4. Filters out malformed or incomplete records

**Output**: `nurtureboss_traces.json`
- Array of conversation records
- Each record contains:
  - `id`: Unique identifier
  - `messages`: List of `{role, content}` dictionaries
  - Additional metadata fields (tools, notes, URLs, etc.)

**Usage**:
```bash
python lesson-4/clean_logs.py
```

### Step 2: Ground Truth Labeling (`label_substantiation.py`)

**Purpose**: Create ground truth labels by having a high-quality LLM judge whether each conversation's assistant responses are fully substantiated.

**Input**: `nurtureboss_traces.json`

**Process**:
1. For each conversation record:
   - Constructs a detailed evaluation prompt including:
     - The full conversation history
     - Tool/metadata information (what facts could be verified)
     - Clear evaluation rubric
   - Calls GPT-4.1 model with structured output format
   - Receives JSON response:
     ```json
     {
       "all_responses_substantiated": true/false,
       "rationale": "explanation of the decision"
     }
     ```
2. Appends these labels to each record
3. Saves the labeled dataset

**Features**:
- **Incremental processing**: Skips records already labeled (allows resuming)
- **Parallel execution**: Uses ThreadPoolExecutor for efficiency (64 workers by default)
- **Structured output**: Uses Pydantic models to ensure consistent JSON responses

**Output**: `nurtureboss_traces_labeled.json`
- Same structure as input, but with added fields:
  - `all_responses_substantiated`: Boolean label
  - `substantiation_rationale`: Explanation for the label

**Usage**:
```bash
python lesson-4/label_substantiation.py
```

**Configuration**:
- Model: `gpt-4.1` (high-quality judge model)
- Workers: Set via `NB_LLM_WORKERS` environment variable (default: 64)

### Step 3: Judge Evaluation (`judge_substantiation.py`)

**Purpose**: Evaluate whether a cheaper model can accurately replicate the ground truth labels created in Step 2.

**Input**: `nurtureboss_traces_labeled.json` (with ground truth labels)

**Process**:
1. **Dataset Splitting**: Creates deterministic train/dev/test splits
   - Uses hash-based splitting (20 train / 30 dev / rest test)
   - Ensures reproducible results across runs
   
2. **Few-shot Example Selection**:
   - Selects balanced examples (pass/fail) from training set
   - Up to 5 examples each for calibration
   
3. **Evaluation**:
   - For each split (train/dev/test):
     - Constructs prompts with few-shot examples
     - Calls the judge model (gpt-4.1) on each conversation
     - Compares predictions to ground truth labels
     - Computes metrics:
       - **TPR (True Positive Rate)**: Correctly identifies substantiated responses
       - **TNR (True Negative Rate)**: Correctly identifies unsubstantiated responses

4. **Analysis**:
   - Reports metrics for each split
   - Identifies false positives (predicted pass but actually fail) for error analysis

**Metrics Explained**:
- **TPR (True Positive Rate / Sensitivity)**: Of all truly substantiated responses, what percentage did the judge correctly identify?
  - Formula: `TP / (TP + FN)`
  - High TPR = judge rarely misses substantiated responses
  
- **TNR (True Negative Rate / Specificity)**: Of all truly unsubstantiated responses, what percentage did the judge correctly identify?
  - Formula: `TN / (TN + FP)`
  - High TNR = judge rarely misses unsubstantiated responses (hallucinations)

**Output**: Console metrics report, e.g.:
```
TRAIN — size  20 | TPR: 95.00% | TNR: 90.00%
DEV   — size  30 | TPR: 93.33% | TNR: 88.89%
TEST  — size 150 | TPR: 94.67% | TNR: 91.33%
```

**Usage**:
```bash
python lesson-4/judge_substantiation.py
```

**Requirements**: Requires `OPENAI_API_KEY` environment variable

## Evaluation Prompt Design

Both scripts use carefully crafted prompts that:

1. **Define the failure mode clearly**: Unsupported/unsubstantiated information
2. **Provide explicit decision rules**:
   - Courtesy statements don't need evidence
   - Information from tools/metadata counts as substantiated
   - Only mark false when a specific claim lacks support
   - When uncertain, default to substantiated (lenient approach)
   - Descriptive qualifiers must appear verbatim
3. **Include context**: Full conversation history, tool outputs, and metadata
4. **Use structured output**: JSON format with Pydantic validation

### Key Decision Rules

The prompts include these critical rules for consistency:

1. **Courtesy statements** (greetings, confirmations) are always substantiated
2. **Paraphrasing/citing** tool outputs counts as substantiated
3. **Specific claims without evidence** = unsubstantiated
4. **When uncertain**: Default to substantiated (conservative approach)
5. **Descriptive qualifiers** must appear verbatim in sources

## Workflow Summary

```mermaid
graph LR
    A[Raw CSV Logs] -->|clean_logs.py| B[Structured JSON]
    B -->|label_substantiation.py| C[Labeled Dataset]
    C -->|judge_substantiation.py| D[Evaluation Metrics]
```

### Complete Pipeline:

```bash
# Step 1: Preprocess data
python lesson-4/clean_logs.py

# Step 2: Create ground truth labels
python lesson-4/label_substantiation.py

# Step 3: Evaluate judge model
python lesson-4/judge_substantiation.py
```

## Data Structures

### Input CSV Format
- `input`: JSON string array of messages `[{role: str, content: str}, ...]`
- `metadata`: JSON object with tool information and additional context
- `name`: Optional identifier

### Trace JSON Format
```json
{
  "id": "unique-identifier",
  "messages": [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."}
  ],
  "tools": [...],
  "Notes": "...",
  "lsmith_id": "...",
  "lsmith_url": "..."
}
```

### Labeled Trace Format
Adds:
```json
{
  "all_responses_substantiated": true,
  "substantiation_rationale": "All claims verified in tool outputs."
}
```

## Technical Details

### Parallel Processing
Both labeling and judging scripts use `ThreadPoolExecutor` for parallel LLM API calls:
- Default: 64 workers (configurable via `NB_LLM_WORKERS`)
- Significantly speeds up processing large datasets
- Uses `tqdm` for progress tracking (gracefully handles missing dependency)

### Deterministic Splitting
The judge evaluation uses hash-based dataset splitting:
- Creates reproducible train/dev/test splits
- Ensures same examples in each split across runs
- Based on SHA-256 hash of record `id`

### Structured Output
- Uses Pydantic `BaseModel` for type-safe JSON parsing
- Ensures consistent response format from LLMs
- Validates responses before use

### Error Handling
- Graceful handling of malformed JSON in CSV
- Skips invalid records rather than crashing
- Incremental processing (can resume labeling)

## Use Cases

This pipeline is useful for:

1. **Quality Control**: Automated detection of hallucination/unsubstantiated claims
2. **Model Evaluation**: Benchmarking judge models on a specific failure mode
3. **Dataset Analysis**: Understanding the prevalence of substantiation issues
4. **Continuous Monitoring**: Running this pipeline on production logs to track quality

## Extending the Pipeline

Potential enhancements:

1. **Multi-class labels**: Distinguish types of unsubstantiation (hallucination vs. outdated info)
2. **Confidence scores**: Add probability estimates to judge outputs
3. **Calibration**: Adjust judge thresholds based on desired precision/recall tradeoff
4. **Human evaluation**: Compare LLM labels to human annotations
5. **Inter-annotator agreement**: Evaluate consistency between multiple judge models

## Key Takeaways

1. **Substantiation is a critical failure mode**: AI assistants must only state verifiable facts
2. **LLM-as-Judge enables scaling**: High-quality models can create labels for evaluation
3. **Structured evaluation**: Clear rubrics and prompts ensure consistent judgments
4. **Incremental processing**: Important for large datasets that may take time to process
5. **Metrics matter**: TPR and TNR give different insights than simple accuracy

## Related Concepts

- **Hallucination detection**: Similar to substantiation evaluation
- **Fact-checking**: Verifying claims against sources
- **Tool grounding**: Ensuring responses are based on function call results
- **Retrieval-Augmented Generation (RAG) evaluation**: Similar principles for verifying claims

