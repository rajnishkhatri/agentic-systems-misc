# Labeling Tool Tutorial: Building Annotation Interfaces

## Learning Objectives

- ✅ Understand when to build custom annotation tools vs. using spreadsheets
- ✅ Design effective annotation interfaces (web UI vs. CLI)
- ✅ Implement FastAPI backend for trace serving and label storage
- ✅ Build interactive frontend with JavaScript
- ✅ Track annotation progress and export labeled data
- ✅ Optimize annotation speed with keyboard shortcuts

## Prerequisites

- Python web framework basics (FastAPI or Flask)
- HTML/CSS/JavaScript fundamentals
- Understanding of [Trace Inspection Concepts](trace_inspection_concepts.md)

## Estimated Time

**Reading Time:** 18-22 minutes
**Implementation:** 2-3 hours (if building from scratch)

---

## When to Build a Custom Tool

### Spreadsheet vs. Custom Tool

| Criteria | Spreadsheet (Excel/Sheets) | Custom Web Tool |
|----------|----------------------------|-----------------|
| **Traces to label** | <50 | 50+ |
| **Annotators** | 1-2 | 3+ |
| **Setup time** | 5 minutes | 2-3 hours |
| **Customization** | Limited | Full control |
| **Progress tracking** | Manual | Automatic |
| **Data format** | CSV | JSON/JSONL/DB |

**Use Spreadsheet if:**
- ✅ Small dataset (<50 traces)
- ✅ Solo annotator
- ✅ Simple binary labels

**Build Custom Tool if:**
- ✅ Large dataset (50+ traces)
- ✅ Multiple annotators
- ✅ Complex annotation tasks (multi-class, hierarchical)
- ✅ Need progress tracking
- ✅ Want keyboard shortcuts for speed

---

## Architecture

### System Overview

```
┌────────────────────────────────────────────────────┐
│         ANNOTATION TOOL ARCHITECTURE               │
├────────────────────────────────────────────────────┤
│                                                    │
│  Frontend (HTML/JS)                                │
│  ├─ Display trace                                  │
│  ├─ Annotation form (labels, notes)                │
│  ├─ Keyboard shortcuts                             │
│  └─ Progress tracker                               │
│      ↓ HTTP requests                               │
│  Backend (FastAPI)                                 │
│  ├─ GET /api/traces → Load CSV/JSON                │
│  ├─ POST /api/label → Append to JSONL             │
│  └─ GET /api/progress → Count labeled              │
│      ↓                                             │
│  Data Storage                                      │
│  ├─ traces.csv (input)                             │
│  └─ labeled_traces.jsonl (output)                  │
└────────────────────────────────────────────────────┘
```

---

## Implementation

### Backend: FastAPI Server

**File:** `labeling-tool/main.py`

```python
from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List
import csv
import json
import os

app = FastAPI()

# Paths
data_dir = '../data'
traces_file = f\"{data_dir}/traces.csv\"
labels_file = f\"{data_dir}/labeled_traces.jsonl\"

# Serve frontend
app.mount(\"/static\", StaticFiles(directory=\"static\"), name=\"static\")

class Label(BaseModel):
    trace_id: str
    label: str  # PASS/FAIL
    notes: str
    confidence: str  # HIGH/MEDIUM/LOW

@app.get(\"/\")
async def index():
    return FileResponse(\"static/index.html\")

@app.get(\"/api/traces\")
async def get_traces():
    \"\"\"Load traces from CSV.\"\"\"
    with open(traces_file, 'r') as f:
        reader = csv.DictReader(f)
        traces = list(reader)
    return JSONResponse(content=traces)

@app.post(\"/api/label\")
async def save_label(label: Label):
    \"\"\"Append label to JSONL file.\"\"\"
    with open(labels_file, 'a') as f:
        f.write(json.dumps(label.dict()) + '\\n')
    return JSONResponse(content={\"status\": \"success\"})

@app.get(\"/api/progress\")
async def get_progress():
    \"\"\"Count labeled traces.\"\"\"
    try:
        with open(labels_file, 'r') as f:
            labeled_count = sum(1 for _ in f)
    except FileNotFoundError:
        labeled_count = 0

    with open(traces_file, 'r') as f:
        total_count = sum(1 for _ in f) - 1  # Subtract header

    return JSONResponse(content={
        \"labeled\": labeled_count,
        \"total\": total_count,
        \"percentage\": round(labeled_count / total_count * 100, 1) if total_count else 0
    })

# Run: uvicorn main:app --reload
```

### Frontend: HTML Interface

**File:** `labeling-tool/static/index.html`

```html
<!DOCTYPE html>
<html>
<head>
    <title>Trace Annotation Tool</title>
    <style>
        body { font-family: Arial; max-width: 1200px; margin: 0 auto; padding: 20px; }
        .trace { background: #f5f5f5; padding: 20px; margin: 20px 0; border-radius: 8px; }
        .conversation { white-space: pre-wrap; background: white; padding: 15px; margin: 10px 0; }
        .controls { margin: 20px 0; }
        button { padding: 10px 20px; margin: 5px; cursor: pointer; font-size: 16px; }
        .pass-btn { background: #4caf50; color: white; }
        .fail-btn { background: #f44336; color: white; }
        textarea { width: 100%; height: 80px; }
        .progress { background: #2196f3; color: white; padding: 10px; text-align: center; }
        .shortcut-hint { color: #666; font-size: 14px; }
    </style>
</head>
<body>
    <div class="progress" id="progress">Loading...</div>

    <div id="trace-container"></div>

    <div class="controls">
        <h3>Annotate This Trace:</h3>
        <button class="pass-btn" onclick="label('PASS')">✓ PASS (P)</button>
        <button class="fail-btn" onclick="label('FAIL')">✗ FAIL (F)</button>
        <br><br>
        <label>Notes:</label>
        <textarea id="notes" placeholder="Optional notes..."></textarea>
        <br>
        <label>Confidence:</label>
        <select id="confidence">
            <option value="HIGH">High</option>
            <option value="MEDIUM">Medium</option>
            <option value="LOW">Low</option>
        </select>
        <br><br>
        <button onclick="skip()">⏭️ Skip (S)</button>
        <p class="shortcut-hint">Keyboard: P=Pass, F=Fail, S=Skip, N=Notes</p>
    </div>

    <script src="script.js"></script>
</body>
</html>
```

### Frontend: JavaScript Logic

**File:** `labeling-tool/static/script.js`

```javascript
let traces = [];
let currentIndex = 0;
let labeledIds = new Set();

// Load traces on page load
async function init() {
    const response = await fetch('/api/traces');
    traces = await response.json();
    updateProgress();
    displayTrace();
}

// Display current trace
function displayTrace() {
    if (currentIndex >= traces.length) {
        alert('All traces reviewed!');
        return;
    }

    const trace = traces[currentIndex];
    const container = document.getElementById('trace-container');

    container.innerHTML = `
        <div class=\"trace\">
            <h2>Trace ${currentIndex + 1} / ${traces.length}</h2>
            <p><strong>ID:</strong> ${trace.trace_id}</p>
            <p><strong>Persona:</strong> ${trace.customer_persona}</p>
            <p><strong>User Query:</strong> ${trace.user_query}</p>
            <div class=\"conversation\">${trace.conversation_messages}</div>
            <p><strong>Tool Calls:</strong> ${trace.tool_calls}</p>
        </div>
    `;
}

// Submit label
async function label(decision) {
    const trace = traces[currentIndex];
    const notes = document.getElementById('notes').value;
    const confidence = document.getElementById('confidence').value;

    const labelData = {
        trace_id: trace.trace_id,
        label: decision,
        notes: notes,
        confidence: confidence
    };

    await fetch('/api/label', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(labelData)
    });

    labeledIds.add(trace.trace_id);
    nextTrace();
}

// Skip to next trace
function skip() {
    nextTrace();
}

// Move to next trace
function nextTrace() {
    document.getElementById('notes').value = '';
    currentIndex++;
    updateProgress();
    displayTrace();
}

// Update progress bar
async function updateProgress() {
    const response = await fetch('/api/progress');
    const progress = await response.json();
    document.getElementById('progress').innerText =
        `Progress: ${progress.labeled} / ${progress.total} (${progress.percentage}%)`;
}

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    if (e.target.tagName === 'TEXTAREA') return;  // Don't trigger in notes field

    if (e.key === 'p' || e.key === 'P') label('PASS');
    if (e.key === 'f' || e.key === 'F') label('FAIL');
    if (e.key === 's' || e.key === 'S') skip();
    if (e.key === 'n' || e.key === 'N') document.getElementById('notes').focus();
});

// Initialize on load
init();
```

---

## Running the Tool

### Setup

```bash
cd lesson-7/labeling-tool

# Install dependencies
pip install fastapi uvicorn pydantic

# Run server
python main.py
# or: uvicorn main:app --reload

# Open in browser
# http://localhost:8000
```

### Annotation Workflow

1. Server loads traces from `data/traces.csv`
2. Frontend displays first trace
3. Annotator reviews conversation
4. Presses **P** (Pass) or **F** (Fail)
5. Optionally adds notes and confidence
6. Label appended to `data/labeled_traces.jsonl`
7. Next trace loads automatically
8. Progress bar updates

**Speed:** ~30-60 seconds per trace with keyboard shortcuts

---

## Best Practices

### UI Design

**1. Minimize Clicks**
```
✅ Keyboard shortcuts (P/F/S)
✅ Auto-advance after label
❌ Multi-step confirmation dialogs
```

**2. Show All Context**
```
✅ Full conversation visible
✅ Tool outputs displayed
✅ Metadata (persona, query) highlighted
❌ Truncated messages requiring scroll
```

**3. Progress Feedback**
```
✅ \"15 / 200 (7.5%)\" progress bar
✅ Estimated time remaining
❌ No indication of how many left
```

### Data Export

**JSONL format for easy processing:**

```jsonl
{\"trace_id\": \"trace_001\", \"label\": \"PASS\", \"notes\": \"\", \"confidence\": \"HIGH\"}
{\"trace_id\": \"trace_002\", \"label\": \"FAIL\", \"notes\": \"Missing tool output\", \"confidence\": \"MEDIUM\"}
```

**Convert to DataFrame:**
```python
import pandas as pd
labels = pd.read_json('labeled_traces.jsonl', lines=True)
```

---

## Advanced Features

### Multi-Annotator Support

**Track annotator ID:**
```python
class Label(BaseModel):
    annotator_id: str  # Added field
    trace_id: str
    label: str
    # ...

# Frontend: Store annotator in localStorage
const annotatorId = localStorage.getItem('annotator_id') || prompt('Your name?');
```

### Resume Capability

**Skip already-labeled traces:**
```javascript
async function loadLabeled() {
    const response = await fetch('/api/labeled_ids');
    labeledIds = new Set(await response.json());
}

function displayTrace() {
    // Skip already labeled
    while (currentIndex < traces.length &&
           labeledIds.has(traces[currentIndex].trace_id)) {
        currentIndex++;
    }
    // ... display logic
}
```

---

## Key Takeaways

- ✅ **Build custom tools for 50+ traces** - Spreadsheets become unwieldy
- ✅ **FastAPI + static HTML = simple stack** - No complex frameworks needed
- ✅ **Keyboard shortcuts save time** - 2-3x faster than mouse clicks
- ✅ **JSONL for incremental saves** - No data loss if browser crashes
- ✅ **Progress tracking motivates** - Annotators see advancement
- ✅ **Multi-annotator mode for quality** - Track who labeled what

**Next Steps:**
- Deploy tool for team annotation
- Calculate inter-annotator agreement
- Use labels for LLM-as-Judge training

---

## Further Reading

- [Trace Inspection Concepts](trace_inspection_concepts.md) - When and why to annotate
- [CSV Conversion Tutorial](csv_conversion_tutorial.md) - Prepare input data
- [FastAPI Documentation](https://fastapi.tiangolo.com/) - Framework reference

---

**Tutorial Status:** ✅ Complete
**Last Updated:** 2025-10-30
**Maintainer:** AI Evaluation Course Team
