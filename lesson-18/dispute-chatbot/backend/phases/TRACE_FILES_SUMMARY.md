# DSPy Distillation & Prompt Tuning Trace Files

This document summarizes the JSONL trace files created during DSPy distillation and prompt tuning.

## Location

All trace files are located in: `lesson-18/dispute-chatbot/backend/phases/distillation_data/`

## Available Trace Files

### 1. `teacher_trace_log.jsonl`
**Purpose**: Logs all teacher model (Claude) traces during distillation data generation.

**Format**:
```json
{
  "dispute_id": "gen_discover_UA06_narrative",
  "status": "accepted" | "rejected" | "parse_error",
  "rejection_reasons": ["reason1", "reason2"],
  "teacher_output": {
    "branch_a": {...},
    "branch_b": {...},
    "branch_c": {...},
    "synthesis": {
      "reasoning": "...",
      "priority_rule_applied": "..."
    },
    "category": "fraudulent",
    "confidence": 0.85,
    "confidence_rationale": "..."
  },
  "ground_truth": {
    "category": "fraudulent",
    "group": "fraud"
  }
}
```

**Key Fields**:
- `status`: Whether the trace was accepted for fine-tuning
- `teacher_output`: Full ToT (Tree-of-Thought) reasoning from Claude
- `rejection_reasons`: Why a trace was rejected (category mismatch, missing reason code group, etc.)

**Usage**:
```bash
# Show statistics
python search_traces.py --file teacher --stats

# Find accepted traces
python search_traces.py --file teacher --status accepted

# Find traces with specific category
python search_traces.py --file teacher --category fraudulent

# Search for "Reason Code Group" mentions
python search_traces.py --file teacher --search "Reason Code Group"
```

---

### 2. `fine_tuning_dataset.jsonl`
**Purpose**: OpenAI fine-tuning format dataset containing only accepted teacher traces.

**Format** (OpenAI Chat Completion format):
```json
{
  "messages": [
    {
      "role": "system",
      "content": "You are a helpful assistant that classifies disputes."
    },
    {
      "role": "user",
      "content": "<full v5 ToT prompt template>"
    },
    {
      "role": "assistant",
      "content": "<JSON output from teacher model>"
    }
  ]
}
```

**Key Points**:
- Only contains traces that passed validation (status="accepted")
- Used directly for OpenAI fine-tuning
- Each example includes the full prompt template + teacher's reasoning

**Usage**:
```bash
# Show statistics
python search_traces.py --file fine_tuning --stats

# Find examples for specific category
python search_traces.py --file fine_tuning --category fraudulent
```

---

### 3. `student_evaluation_log.jsonl`
**Purpose**: Evaluation logs from testing the fine-tuned student model.

**Format**:
```json
{
  "dispute_id": "gen_amex_F31_ambiguous",
  "ground_truth": "fraudulent",
  "predicted": "fraudulent",
  "is_correct": true,
  "reasoning": "...",
  "full_response": "..."
}
```

**Key Fields**:
- `is_correct`: Whether the prediction matches ground truth
- `predicted`: Category predicted by fine-tuned model
- `ground_truth`: True category from training data

**Usage**:
```bash
# Show accuracy statistics
python search_traces.py --file student_eval --stats

# Find incorrect predictions
python search_traces.py --file student_eval --search '"is_correct": false'
```

---

## Search Tool

Use `search_traces.py` to explore these files:

```bash
# Basic usage
python search_traces.py --file <teacher|fine_tuning|student_eval> [options]

# Options:
--status <accepted|rejected|parse_error>  # Filter by status (teacher only)
--category <category_name>                 # Filter by category
--search <text>                           # Search for text in traces
--stats                                    # Show statistics
--limit <n>                                # Limit results (default: 10)
--all                                      # Show all results
```

## Example Queries

### Find all accepted traces with "Reason Code Group" mentioned:
```bash
python search_traces.py --file teacher --status accepted --search "Reason Code Group" --limit 5
```

### Find rejected traces and see why:
```bash
python search_traces.py --file teacher --status rejected --limit 10
```

### Check fine-tuning dataset quality:
```bash
python search_traces.py --file fine_tuning --stats
```

### Analyze student model errors:
```bash
python search_traces.py --file student_eval --search '"is_correct": false' --limit 20
```

## Related Files

- **DSPy Optimization Script**: `optimize_dspy_tot.py`
  - Uses MIPROv2 optimizer
  - Generates optimized prompts from v5 ToT template
  - Saves compiled program to: `dispute_classifier_tot_mipro.json`

- **Teacher Trace Generation**: `generate_teacher_traces.py`
  - Generates `teacher_trace_log.jsonl` and `fine_tuning_dataset.jsonl`

- **Student Evaluation**: `verify_finetuned.py`
  - Generates `student_evaluation_log.jsonl`

## Current Status

Based on `DISTILLATION_CHECKPOINT.md`:
- **Teacher Traces**: 100 total, 43 accepted (43% acceptance rate)
- **Issue**: Low yield due to strict "Reason Code Group" validation
- **Current Model**: Using `claude-opus-4-5-20251101` (upgraded from haiku)

