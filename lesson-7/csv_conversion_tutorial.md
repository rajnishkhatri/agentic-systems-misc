# CSV Conversion Tutorial: JSON Traces to Spreadsheet Format

## Learning Objectives

- ✅ Convert nested JSON conversation traces to flat CSV format
- ✅ Format messages with role prefixes for readability
- ✅ Summarize tool calls concisely
- ✅ Handle special characters and CSV escaping
- ✅ Preserve essential metadata while reducing clutter

## Prerequisites

- Python basics (`json`, `csv` modules)
- Understanding of JSON trace structure (from HW5 or Lesson 4)

## Estimated Time

**Reading Time:** 12-15 minutes
**Implementation:** 15-20 minutes

---

## Why Convert to CSV?

**The Problem: JSON is Hard to Review Manually**

```json
{
  "trace_id": "trace_042",
  "messages": [
    {"role": "user", "content": "Find vegan recipes"},
    {"role": "assistant", "content": "Searching database..."},
    {"role": "tool", "tool_name": "search_recipes", "output": {...}}
  ],
  "customer_persona": "vegan_family"
}
```

**Human annotators want:**
- ✅ Spreadsheet view (Excel, Google Sheets)
- ✅ One conversation per row
- ✅ Readable messages without JSON syntax
- ✅ Easy filtering and sorting

**Solution: Convert to CSV**

| trace_id | persona | user_query | conversation | tool_calls |
|----------|---------|------------|--------------|------------|
| trace_042 | vegan_family | Find vegan recipes | USER: Find vegan recipes \| AGENT: Searching... | search_recipes(...) |

---

## Conversion Strategy

```
┌──────────────────────────────────────────────────────┐
│        JSON → CSV CONVERSION WORKFLOW                │
├──────────────────────────────────────────────────────┤
│                                                      │
│  Input: JSON traces (nested structure)              │
│  ↓                                                   │
│  1. Extract user query (first user message)         │
│  ↓                                                   │
│  2. Format conversation (USER: | AGENT: | TOOL:)    │
│  ↓                                                   │
│  3. Summarize tool calls (name + args)              │
│  ↓                                                   │
│  4. Flatten to single row per trace                 │
│  ↓                                                   │
│  Output: CSV (flat, spreadsheet-ready)              │
└──────────────────────────────────────────────────────┘
```

---

## Implementation

### Step 1: Format Conversation Messages

**Goal:** Convert message list to readable string

```python
def format_messages(messages: List[Dict[str, Any]]) -> str:
    \"\"\"Format conversation as readable text with role prefixes.\"\"\"
    formatted_parts = []

    for msg in messages:
        role = msg.get('role', 'unknown')
        content = msg.get('content', '')
        tool_name = msg.get('tool_name')

        if role == 'user':
            formatted_parts.append(f\"USER: {content}\")
        elif role == 'agent':
            formatted_parts.append(f\"AGENT: {content}\")
        elif role == 'tool':
            tool_info = f\" ({tool_name})\" if tool_name else \"\"
            formatted_parts.append(f\"TOOL{tool_info}: {content}\")
        else:
            formatted_parts.append(f\"{role.upper()}: {content}\")

    return \" | \".join(formatted_parts)
```

**Example Output:**
```
USER: Find vegan recipes | AGENT: Searching database | TOOL (search_recipes): Found 5 results
```

### Step 2: Extract User Query

**Goal:** Get the initial user message for quick reference

```python
def extract_user_query(messages: List[Dict]) -> str:
    \"\"\"Extract first user message.\"\"\"
    for msg in messages:
        if msg.get('role') == 'user':
            return msg.get('content', '')
    return ''
```

### Step 3: Summarize Tool Calls

**Goal:** Show tool usage without full JSON

```python
def extract_tool_calls(messages: List[Dict]) -> str:
    \"\"\"Summarize tool calls made during conversation.\"\"\"
    tool_calls = []

    for msg in messages:
        if msg.get('role') == 'tool' and msg.get('tool_name'):
            tool_name = msg['tool_name']
            tool_input = msg.get('tool_input', {})
            tool_output = msg.get('tool_output', {})

            # Truncate long values
            input_str = str(tool_input)[:100]
            output_str = str(tool_output)[:100]

            tool_calls.append(
                f\"{tool_name}(in: {input_str}, out: {output_str})\"
            )

    return \" | \".join(tool_calls)
```

**Example Output:**
```
search_recipes(in: {'query': 'vegan pasta'}, out: {'results': [...]}) | get_recipe_details(...)
```

### Step 4: Write CSV

**Complete Conversion Script:**

```python
import json
import csv
from pathlib import Path
from typing import List, Dict, Any

def convert_traces_to_csv(
    input_file: str,
    output_file: str
) -> None:
    \"\"\"Convert JSON traces to CSV format.\"\"\"

    # Load JSON
    with open(input_file, 'r') as f:
        data = json.load(f)

    traces = data if isinstance(data, list) else data.get('traces', [])
    print(f\"Loaded {len(traces)} traces\")

    # Define CSV columns
    fieldnames = [
        'trace_id',
        'customer_persona',
        'user_query',
        'conversation_messages',
        'tool_calls'
    ]

    # Write CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for trace in traces:
            messages = trace.get('messages', [])

            row = {
                'trace_id': trace.get('trace_id', trace.get('id', '')),
                'customer_persona': trace.get('customer_persona', ''),
                'user_query': extract_user_query(messages),
                'conversation_messages': format_messages(messages),
                'tool_calls': extract_tool_calls(messages)
            }

            writer.writerow(row)

    print(f\"✓ Wrote {len(traces)} rows to {output_file}\")

# Usage
convert_traces_to_csv(
    \"homeworks/hw5/data/labeled_traces.json\",
    \"lesson-7/data/traces.csv\"
)
```

**Output CSV:**
```csv
trace_id,customer_persona,user_query,conversation_messages,tool_calls
trace_001,vegan_family,"Find recipes","USER: Find recipes | AGENT: Searching...",search_recipes(...)
trace_002,gluten_free_athlete,"Quick protein","USER: Quick protein | AGENT: Let me search...",search_recipes(...)
```

---

## Handling Edge Cases

### Long Content Truncation

```python
def truncate(text: str, max_len: int = 200) -> str:
    \"\"\"Truncate long strings for CSV readability.\"\"\"
    return text if len(text) <= max_len else text[:max_len] + \"...\"

# Usage
content = truncate(msg['content'], max_len=150)
```

### Special Characters (Commas, Quotes)

**CSV escaping is automatic with csv.DictWriter!**

```python
# These are handled correctly:
content = "Contains, commas"       # → Quoted automatically
content = 'Contains "quotes"'      # → Escaped automatically
content = "Line\nBreaks"           # → Preserved in quotes
```

### Missing Fields

```python
# Safe field access with defaults
trace_id = trace.get('trace_id', trace.get('id', 'unknown'))
persona = trace.get('customer_persona', 'N/A')
```

---

## Validation and Quality Checks

**After conversion, verify:**

```python
import pandas as pd

# Load converted CSV
df = pd.read_csv('lesson-7/data/traces.csv')

print(f\"Total rows: {len(df)}\")
print(f\"Columns: {list(df.columns)}\")
print(f\"Missing trace_id: {df['trace_id'].isna().sum()}\")
print(f\"Empty conversations: {(df['conversation_messages'] == '').sum()}\")

# Preview
print(\"\\nFirst 3 rows:\")
print(df.head(3))
```

---

## Using the CSV for Annotation

### Spreadsheet Workflow

1. **Open CSV** in Excel/Google Sheets
2. **Add annotation columns:**
   - `label` (PASS/FAIL)
   - `notes` (annotator comments)
   - `confidence` (HIGH/MEDIUM/LOW)
3. **Review and label** each row
4. **Export CSV** with annotations
5. **Convert back to JSON** if needed

**Example Annotated CSV:**

| trace_id | conversation | label | notes | confidence |
|----------|--------------|-------|-------|------------|
| trace_001 | USER: Find... | PASS | All substantiated | HIGH |
| trace_002 | USER: Tell... | FAIL | Claims not in tools | HIGH |

### Filter and Sort

```python
# In Python (after annotation)
df = pd.read_csv('annotated_traces.csv')

# Filter failures only
failures = df[df['label'] == 'FAIL']

# Sort by confidence
uncertain = df.sort_values('confidence')

# Export subsets
failures.to_csv('failures_only.csv', index=False)
```

---

## Key Takeaways

- ✅ **CSV enables spreadsheet-based review** - Excel/Sheets are familiar to annotators
- ✅ **Flatten nested structures** - One conversation per row
- ✅ **Use role prefixes** - USER:/AGENT:/TOOL: improves readability
- ✅ **Truncate long fields** - Keep cells manageable
- ✅ **CSV escaping is automatic** - csv.DictWriter handles special chars
- ✅ **Add annotation columns** - label, notes, confidence for manual review

**Next Steps:**
- Use CSV for manual annotation
- See [Labeling Tool Tutorial](labeling_tool_tutorial.md) for web-based alternatives
- See [Trace Inspection Concepts](trace_inspection_concepts.md) for annotation best practices

---

## Further Reading

- [Trace Inspection Concepts](trace_inspection_concepts.md) - When and how to manually review
- [Labeling Tool Tutorial](labeling_tool_tutorial.md) - Build web UIs for annotation
- [scripts/convert_traces_to_csv.py](scripts/convert_traces_to_csv.py) - Full reference implementation

---

**Tutorial Status:** ✅ Complete
**Last Updated:** 2025-10-30
**Maintainer:** AI Evaluation Course Team
