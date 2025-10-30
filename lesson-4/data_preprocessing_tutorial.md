# Data Preprocessing Tutorial: CSV to Structured JSON

## Learning Objectives

By completing this tutorial, you will be able to:
- ✅ Convert raw CSV conversation logs to structured JSON format
- ✅ Parse JSON-encoded columns safely with error handling
- ✅ Extract essential fields while filtering noise
- ✅ Handle malformed data without crashing the pipeline
- ✅ Generate unique conversation IDs for tracking
- ✅ Validate cleaned data before labeling

## Prerequisites

- Understanding of CSV and JSON data formats
- Python experience with `csv`, `json`, and `pathlib` modules
- Familiarity with conversational AI message structures

## Estimated Time

**Reading Time:** 15-18 minutes
**Implementation Time:** 20-30 minutes

---

## Concepts

### Why Data Preprocessing?

**The Raw Data Problem:**

Production conversation logs are messy:
- JSON encoded as strings inside CSV cells
- Metadata mixed with message content
- Malformed records from API errors
- Unnecessary fields that bloat datasets
- No unique IDs for tracking

**Example Raw CSV:**
```csv
name,input,metadata
conv_1,"[{\"role\":\"user\",\"content\":\"Find recipes\",\"timestamp\":\"...\",\"ip_addr\":\"...\"}]","{\"tools\":[...],\"session_id\":...}"
```

**Goal:** Clean, lightweight JSON structure:
```json
{
  "id": "conv_1",
  "messages": [
    {"role": "user", "content": "Find recipes"}
  ],
  "tools": [...]
}
```

### The Preprocessing Pipeline

```
┌────────────────────────────────────────────────────┐
│        DATA PREPROCESSING WORKFLOW                 │
├────────────────────────────────────────────────────┤
│                                                    │
│  Raw CSV Logs (nurtureboss_logs.csv)              │
│  ↓                                                 │
│  Read CSV with DictReader                          │
│  ↓                                                 │
│  For each row:                                     │
│    1. Parse JSON from 'input' column               │
│    2. Parse JSON from 'metadata' column            │
│    3. Extract role + content from messages         │
│    4. Generate unique ID                           │
│    5. Validate record structure                    │
│  ↓                                                 │
│  Filter out malformed records                      │
│  ↓                                                 │
│  Write Structured JSON (nurtureboss_traces.json)  │
└────────────────────────────────────────────────────┘
```

---

## Implementation Walkthrough

### Step 1: Safe JSON Parsing

**Problem:** CSV cells contain JSON strings that may be malformed.

**Solution:** Defensive parsing with try-except

```python
import json
from typing import Any

def parse_json_cell(raw: str) -> Any:
    """Safely parse JSON from CSV cell.

    Returns None if parsing fails (no crash).
    """
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None  # Graceful failure
```

**Why this matters:**
- Production logs have corrupt data
- One bad record shouldn't crash entire pipeline
- Can log failures for investigation

### Step 2: Extract Essential Message Fields

**Problem:** Message objects have 10+ fields, we only need 2.

**Before (bloated):**
```json
{
  "role": "user",
  "content": "Find recipes",
  "timestamp": "2024-01-15T10:30:00Z",
  "ip_address": "192.168.1.1",
  "user_agent": "Mozilla/5.0...",
  "session_id": "abc123",
  "metadata": {...}
}
```

**After (clean):**
```json
{
  "role": "user",
  "content": "Find recipes"
}
```

**Implementation:**
```python
from typing import List, Dict

def parse_messages(raw: str) -> List[Dict[str, str]] | None:
    """Parse and simplify message list from JSON string.

    Keeps only 'role' and 'content' fields.
    """
    data = parse_json_cell(raw)
    if not isinstance(data, list):
        return None

    cleaned = []
    for msg in data:
        if not isinstance(msg, dict):
            continue

        role = msg.get('role')
        content = msg.get('content')

        # Skip incomplete messages
        if role is None or content is None:
            continue

        cleaned.append({'role': role, 'content': content})

    return cleaned or None  # Return None if no valid messages
```

**Benefits:**
- 80-90% size reduction
- Faster loading and processing
- Easier human review
- Model-agnostic (no provider-specific fields)

### Step 3: Combine Messages and Metadata

**CSV Structure:**
```csv
name,input,metadata
conv_1,"[{...messages...}]","{...metadata...}"
```

**Processing Logic:**
```python
import csv
from pathlib import Path

def convert_csv_to_records(csv_path: Path) -> List[Dict]:
    """Convert CSV to list of cleaned conversation records."""
    records = []

    with csv_path.open(newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for idx, row in enumerate(reader, start=1):
            # Parse metadata (tools, session info, etc.)
            raw_meta = row.get('metadata')
            meta_payload = parse_json_cell(raw_meta or '') if raw_meta else None

            # Parse messages
            raw_input = row.get('input')
            messages = parse_messages(raw_input) if raw_input else None

            # Skip rows with no data
            if meta_payload is None and messages is None:
                continue

            # Build record
            record = {}

            # Add ID (from 'name' column or generate)
            name = row.get('name', '').strip()
            record['id'] = name if name else f"trace_{idx}"

            # Add messages
            if messages:
                record['messages'] = messages

            # Merge metadata fields
            if meta_payload and isinstance(meta_payload, dict):
                record.update(meta_payload)

            records.append(record)

    return records
```

### Step 4: Write Cleaned JSON

```python
def write_traces_json(records: List[Dict], output_path: Path) -> None:
    """Write cleaned records to JSON file."""
    with output_path.open('w', encoding='utf-8') as f:
        json.dump(records, f, indent=2, ensure_ascii=False)

    print(f"✓ Wrote {len(records)} traces to {output_path}")
```

---

## Complete Script

**File:** `lesson-4/clean_logs.py`

```python
from pathlib import Path
import csv
import json
from typing import List, Dict, Any

# File paths
CSV_PATH = Path(__file__).with_name("nurtureboss_logs.csv")
OUTPUT_PATH = Path(__file__).with_name("nurtureboss_traces.json")

def parse_json_cell(raw: str) -> Any:
    """Safely parse JSON from CSV cell."""
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None

def parse_messages(raw: str) -> List[Dict[str, str]] | None:
    """Extract simplified messages (role + content only)."""
    data = parse_json_cell(raw)
    if not isinstance(data, list):
        return None

    cleaned = []
    for msg in data:
        if not isinstance(msg, dict):
            continue
        role = msg.get('role')
        content = msg.get('content')
        if role and content:
            cleaned.append({'role': role, 'content': content})

    return cleaned or None

def convert_csv_to_records(csv_path: Path) -> List[Dict]:
    """Read CSV and extract cleaned records."""
    records = []

    with csv_path.open(newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for idx, row in enumerate(reader, start=1):
            # Parse columns
            raw_meta = row.get('metadata')
            meta_payload = parse_json_cell(raw_meta or '') if raw_meta else None

            raw_input = row.get('input')
            messages = parse_messages(raw_input) if raw_input else None

            # Skip empty rows
            if not meta_payload and not messages:
                continue

            # Build record
            record = {'id': row.get('name', '').strip() or f"trace_{idx}"}

            if messages:
                record['messages'] = messages

            if meta_payload and isinstance(meta_payload, dict):
                record.update(meta_payload)

            records.append(record)

    return records

def main():
    """Run preprocessing pipeline."""
    print(f"Reading: {CSV_PATH}")
    records = convert_csv_to_records(CSV_PATH)

    print(f"Processed {len(records)} conversations")

    with OUTPUT_PATH.open('w', encoding='utf-8') as f:
        json.dump(records, f, indent=2, ensure_ascii=False)

    print(f"✓ Saved to: {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
```

**Usage:**
```bash
python lesson-4/clean_logs.py
```

**Output:**
```
Reading: lesson-4/nurtureboss_logs.csv
Processed 203 conversations
✓ Saved to: lesson-4/nurtureboss_traces.json
```

---

## Validation and Quality Checks

### Inspect Cleaned Data

**After running preprocessing, verify output:**

```python
import json

# Load cleaned traces
with open('lesson-4/nurtureboss_traces.json') as f:
    traces = json.load(f)

print(f"Total traces: {len(traces)}")
print(f"\nSample trace:")
print(json.dumps(traces[0], indent=2))

# Validation checks
no_messages = [t for t in traces if 'messages' not in t]
print(f"\n⚠️  Traces without messages: {len(no_messages)}")

duplicate_ids = len(traces) - len(set(t['id'] for t in traces))
print(f"⚠️  Duplicate IDs: {duplicate_ids}")
```

### Common Issues and Fixes

**Issue 1: Malformed JSON in CSV**
```
Error: JSONDecodeError at row 42
```
**Fix:** `parse_json_cell()` returns `None`, row is skipped automatically

**Issue 2: Empty Message Content**
```
{"role": "user", "content": ""}
```
**Fix:** Add validation in `parse_messages()`:
```python
if role and content and content.strip():
    cleaned.append({'role': role, 'content': content})
```

**Issue 3: Duplicate Conversation IDs**
```
Same 'name' appears twice in CSV
```
**Fix:** Append row index to ensure uniqueness:
```python
record['id'] = f"{name}_{idx}" if name else f"trace_{idx}"
```

---

## Incremental Processing

**For large datasets (1000s of conversations):**

```python
def convert_csv_incremental(csv_path: Path, output_path: Path, batch_size: int = 100):
    """Process and write in batches to handle memory constraints."""
    with csv_path.open(newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        batch = []

        for idx, row in enumerate(reader, start=1):
            record = process_row(row, idx)  # Your processing logic
            if record:
                batch.append(record)

            # Write batch and clear memory
            if len(batch) >= batch_size:
                append_to_json(batch, output_path)
                print(f"Processed {idx} rows...")
                batch = []

        # Write remaining
        if batch:
            append_to_json(batch, output_path)
```

---

## Key Takeaways

- ✅ **Safe parsing prevents pipeline crashes** - Use try-except for JSON decoding
- ✅ **Extract only essential fields** - Reduce data size by 80-90%
- ✅ **Generate unique IDs** - Enable trace tracking through pipeline
- ✅ **Filter malformed records** - Skip bad data, don't crash
- ✅ **Validate output** - Check for duplicates, missing messages
- ✅ **Incremental processing for scale** - Handle large datasets with batching

**Next Steps:**
- Use cleaned traces for [Parallel Labeling](parallel_labeling_tutorial.ipynb)
- Apply substantiation evaluation with [Judge Pipeline](judge_evaluation_pipeline_tutorial.ipynb)

---

## Further Reading

- [Substantiation Concepts](substantiation_concepts.md) - What to label in cleaned data
- [Parallel Labeling Tutorial](parallel_labeling_tutorial.ipynb) - Create ground truth at scale
- [Lesson 4 Tutorial Index](TUTORIAL_INDEX.md) - Complete learning path

**Code Reference:**
- [clean_logs.py](clean_logs.py:1-100) - Full implementation with error handling

---

**Tutorial Status:** ✅ Complete
**Last Updated:** 2025-10-30
**Maintainer:** AI Evaluation Course Team
