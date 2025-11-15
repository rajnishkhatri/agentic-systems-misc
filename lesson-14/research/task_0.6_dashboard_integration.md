# Task 0.6: Dashboard Integration Requirements

**Purpose:** Document `lesson-9-11/evaluation_dashboard.py` data loading requirements to ensure memory systems evaluation results integrate seamlessly with existing dashboard.

**Source:** `lesson-9-11/evaluation_dashboard.py` (expected functionality based on existing results/*.json integration)

---

## 1. Dashboard Data Loading Workflow

### 1.1 Expected File Discovery Pattern

**Dashboard scans:**
```
lesson-9-11/evaluation_dashboard.py
    ↓
Scans: lesson-14/results/*.json
    ↓
Loads all JSON files matching expected schema
    ↓
Validates required fields
    ↓
Displays in dashboard tabs/sections
```

**File Naming Convention:**
- Use descriptive `snake_case` names: `memory_systems_evaluation.json`
- Avoid spaces, special characters, or uppercase
- End with `.json` extension
- Store in `lesson-14/results/` directory

---

### 1.2 Status Codes

**Dashboard returns one of four statuses per file:**

| Status Code | Meaning | User Feedback |
|-------------|---------|---------------|
| `"ok"` | Valid JSON with all required fields | ✅ Data loaded, visualization rendered |
| `"no_data"` | File exists but empty or missing key fields | ⚠️ "No evaluation data found" |
| `"invalid"` | JSON parse error or schema validation failure | ❌ "Invalid JSON format" |
| `"error"` | File not found or I/O error | ❌ "File not found: [filename]" |

**Implementation Checklist:**
- [ ] Return `"ok"` when all required fields present and valid
- [ ] Return `"no_data"` when file is empty or missing `summary_statistics`
- [ ] Return `"invalid"` when JSON parse fails or schema mismatch
- [ ] Return `"error"` when file doesn't exist or can't be read

---

## 2. Required Fields for Dashboard Integration

### 2.1 Minimum Required Schema

**For status = `"ok"`, JSON MUST contain:**
```json
{
  "version": "string",
  "created": "string",
  "execution_mode": "string",
  "summary_statistics": {
    "[metric_name]": {
      "mean": float,
      "std": float
    }
    // At least 1 metric required
  },
  "detailed_results": [
    // At least 1 result object required
  ]
}
```

**Validation Logic:**
```python
def validate_results_json(data: dict) -> str:
    """Validate results JSON for dashboard integration.

    Returns:
        Status code: "ok", "no_data", "invalid", "error"
    """
    # Check required top-level keys
    required_keys = ["version", "created", "execution_mode", "summary_statistics", "detailed_results"]
    if not all(key in data for key in required_keys):
        return "invalid"

    # Check summary_statistics not empty
    if not data["summary_statistics"]:
        return "no_data"

    # Check detailed_results not empty
    if not data["detailed_results"]:
        return "no_data"

    # Validate metric consistency (all summary metrics in detailed results)
    summary_metrics = set(data["summary_statistics"].keys())
    if data["detailed_results"]:
        detailed_metrics = set(data["detailed_results"][0].keys())
        if not summary_metrics.issubset(detailed_metrics):
            return "invalid"

    return "ok"
```

---

### 2.2 Optional Fields for Enhanced Visualization

**Recommended for better dashboard experience:**
```json
{
  "radar_chart_data": {
    "labels": [...],
    "values": [...]
  },
  "experiment_metadata": {
    "mode": "string",
    "timestamp": "string",
    ...
  },
  "pattern_rankings": {
    "fastest": "string",
    "cheapest": "string",
    ...
  }
}
```

**Benefits:**
- `radar_chart_data`: Enables multi-dimensional visualization
- `experiment_metadata`: Provides execution context in dashboard header
- `pattern_rankings`: Quick summary cards for top performers

---

## 3. Dashboard Visualization Requirements

### 3.1 Summary Statistics Display

**Dashboard expects:**
- Metrics displayed as mean ± std
- Values formatted as percentages (0.95 → "95.0%")
- Color coding: >0.9 = green, 0.7-0.9 = yellow, <0.7 = red

**Example Display:**
```
Metric Name          | Value
---------------------|-------------
Exact Match          | 90.0% ± 30.8%
In-Order Match       | 100.0% ± 0.0%
Precision            | 97.5% ± 7.7%
```

**Implementation Requirement:**
- All metric values must be floats between 0.0 and 1.0
- `std` of 0.0 is valid (perfect consistency)
- Missing `std` field will cause validation failure

---

### 3.2 Radar Chart Visualization

**Dashboard renders radar chart if `radar_chart_data` present:**
```javascript
// Simplified visualization logic
const radarData = {
  labels: data.radar_chart_data.labels,
  datasets: [{
    label: data.execution_mode,
    data: data.radar_chart_data.values,
    fill: true,
    backgroundColor: 'rgba(54, 162, 235, 0.2)',
    borderColor: 'rgb(54, 162, 235)',
    pointBackgroundColor: 'rgb(54, 162, 235)'
  }]
};
```

**Requirements:**
- `labels` array: 3-10 metric names (optimal: 5-7)
- `values` array: Length = `labels` length + 1 (last value repeats first)
- All values between 0.0 and 1.0
- Labels use human-readable format (replace `_` with spaces, title case)

**Validation:**
```python
def validate_radar_chart_data(radar_data: dict) -> bool:
    """Validate radar chart data structure."""
    if "labels" not in radar_data or "values" not in radar_data:
        return False

    labels = radar_data["labels"]
    values = radar_data["values"]

    # Check length: values should be labels + 1
    if len(values) != len(labels) + 1:
        return False

    # Check polygon closure: last value == first value
    if values[-1] != values[0]:
        return False

    # Check value range
    if not all(0.0 <= v <= 1.0 for v in values):
        return False

    return True
```

---

### 3.3 Detailed Results Table

**Dashboard displays tabular view of `detailed_results`:**
```
Test ID    | Metric 1 | Metric 2 | ... | Complexity | Domain
-----------|----------|----------|-----|------------|-------
test_001   | 1.00     | 1.00     | ... | simple     | recipe
test_002   | 1.00     | 1.00     | ... | simple     | gita
```

**Requirements:**
- Each result object must have `test_id` (unique identifier)
- All metrics from `summary_statistics` must appear as columns
- Categorical dimensions (complexity, domain, pattern) displayed as filter options
- Sortable by any column
- Filterable by categorical dimensions

**Implementation:**
```python
def format_detailed_results(results: list[dict]) -> pd.DataFrame:
    """Convert detailed results to pandas DataFrame for display."""
    df = pd.DataFrame(results)

    # Format metric columns as percentages
    metric_columns = [col for col in df.columns if col not in ["test_id", "reference_id", "complexity", "domain", "pattern"]]
    for col in metric_columns:
        df[col] = df[col].apply(lambda x: f"{x*100:.1f}%")

    return df
```

---

## 4. Error Handling and Validation

### 4.1 Common Error Scenarios

**Scenario 1: File Not Found**
```python
try:
    with open(filepath, "r") as f:
        data = json.load(f)
except FileNotFoundError:
    return {"status": "error", "message": f"File not found: {filepath}"}
```

**Scenario 2: Invalid JSON**
```python
try:
    data = json.load(f)
except json.JSONDecodeError as e:
    return {"status": "invalid", "message": f"JSON parse error: {e}"}
```

**Scenario 3: Missing Required Fields**
```python
required_keys = ["version", "created", "execution_mode", "summary_statistics", "detailed_results"]
missing_keys = [key for key in required_keys if key not in data]
if missing_keys:
    return {"status": "invalid", "message": f"Missing required fields: {missing_keys}"}
```

**Scenario 4: Empty Data**
```python
if not data["summary_statistics"] or not data["detailed_results"]:
    return {"status": "no_data", "message": "No evaluation results found"}
```

---

### 4.2 Defensive Validation Template

```python
def load_and_validate_results(filepath: str) -> dict[str, Any]:
    """Load and validate evaluation results JSON for dashboard.

    Args:
        filepath: Path to results JSON file

    Returns:
        Dictionary with keys:
        - status: "ok", "no_data", "invalid", "error"
        - data: Parsed JSON data (if status == "ok")
        - message: Error message (if status != "ok")

    Raises:
        None (all errors handled gracefully)
    """
    # Step 1: File existence check
    if not os.path.exists(filepath):
        return {"status": "error", "message": f"File not found: {filepath}"}

    # Step 2: JSON parsing
    try:
        with open(filepath, "r") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return {"status": "invalid", "message": f"JSON parse error: {e}"}
    except Exception as e:
        return {"status": "error", "message": f"I/O error: {e}"}

    # Step 3: Required field validation
    required_keys = ["version", "created", "execution_mode", "summary_statistics", "detailed_results"]
    missing_keys = [key for key in required_keys if key not in data]
    if missing_keys:
        return {"status": "invalid", "message": f"Missing required fields: {missing_keys}"}

    # Step 4: Empty data check
    if not data["summary_statistics"]:
        return {"status": "no_data", "message": "No summary statistics found"}
    if not data["detailed_results"]:
        return {"status": "no_data", "message": "No detailed results found"}

    # Step 5: Metric consistency check
    summary_metrics = set(data["summary_statistics"].keys())
    if data["detailed_results"]:
        detailed_metrics = set(data["detailed_results"][0].keys())
        missing_in_detailed = summary_metrics - detailed_metrics
        if missing_in_detailed:
            return {"status": "invalid", "message": f"Metrics in summary but not in detailed results: {missing_in_detailed}"}

    # Step 6: Radar chart validation (optional but recommended)
    if "radar_chart_data" in data:
        if not validate_radar_chart_data(data["radar_chart_data"]):
            # Non-fatal: log warning but don't fail
            print(f"Warning: Invalid radar chart data in {filepath}")

    # All checks passed
    return {"status": "ok", "data": data}
```

---

## 5. Memory Systems Integration Checklist

**For Task 5.0 implementation (`memory_systems_evaluation.json`):**

### 5.1 Pre-Implementation Checklist

- [ ] Confirm file will be saved to `lesson-14/results/memory_systems_evaluation.json`
- [ ] Schema includes all required top-level keys (version, created, execution_mode, summary_statistics, detailed_results)
- [ ] At least 5 metrics defined in `summary_statistics` (for meaningful radar chart)
- [ ] Each metric has `mean` and `std` values between 0.0 and 1.0

### 5.2 Schema Validation Checklist

- [ ] `radar_chart_data.values` length = `labels` length + 1
- [ ] `radar_chart_data.values[0]` == `radar_chart_data.values[-1]` (polygon closed)
- [ ] All metrics in `summary_statistics` appear in every `detailed_results` object
- [ ] `test_id` unique for each entry in `detailed_results`
- [ ] Categorical dimensions included (e.g., `memory_pattern`, `use_case`, `conversation_length`)

### 5.3 Dashboard Integration Testing

**Manual Testing Steps:**
1. Save `memory_systems_evaluation.json` to `lesson-14/results/`
2. Run dashboard: `python lesson-9-11/evaluation_dashboard.py`
3. Verify file appears in dashboard file list
4. Verify status = `"ok"` (not `"invalid"`, `"no_data"`, or `"error"`)
5. Check summary statistics display correctly (mean ± std format)
6. Verify radar chart renders (if included)
7. Check detailed results table displays all columns
8. Test filtering by categorical dimensions

**Automated Testing (pytest):**
```python
def test_memory_systems_json_valid():
    """Test memory systems evaluation JSON is valid for dashboard."""
    filepath = "lesson-14/results/memory_systems_evaluation.json"
    result = load_and_validate_results(filepath)
    assert result["status"] == "ok", f"Validation failed: {result.get('message')}"

def test_memory_systems_radar_chart():
    """Test radar chart data is valid."""
    with open("lesson-14/results/memory_systems_evaluation.json", "r") as f:
        data = json.load(f)

    assert "radar_chart_data" in data
    assert validate_radar_chart_data(data["radar_chart_data"])

def test_memory_systems_metric_consistency():
    """Test metrics consistent across summary and detailed results."""
    with open("lesson-14/results/memory_systems_evaluation.json", "r") as f:
        data = json.load(f)

    summary_metrics = set(data["summary_statistics"].keys())
    detailed_metrics = set(data["detailed_results"][0].keys())

    # All summary metrics must appear in detailed results
    assert summary_metrics.issubset(detailed_metrics)
```

---

## 6. Performance Considerations

### 6.1 File Size Guidelines

**Dashboard loading performance:**
- **Optimal:** <100 KB per JSON file
- **Acceptable:** 100-500 KB
- **Slow:** 500 KB - 1 MB (consider pagination)
- **Very Slow:** >1 MB (dashboard may lag)

**Memory systems evaluation file estimate:**
- DEMO mode (30 tests): ~20-40 KB
- FULL mode (150 tests): ~80-150 KB

**Optimization Tips:**
- Use compact JSON (no pretty printing)
- Remove unnecessary fields from `detailed_results`
- Use abbreviations for categorical values (e.g., "S" instead of "simple")

---

### 6.2 Lazy Loading Pattern (Optional)

**For large datasets (>1 MB):**
```python
# Instead of loading all detailed_results at once
"detailed_results_preview": [
    # First 100 results for preview
],
"detailed_results_full_path": "lesson-14/results/memory_systems_detailed_full.json"
```

**Dashboard loads:**
1. Summary statistics + preview (fast initial load)
2. Full detailed results on demand (when user clicks "View All")

---

## 7. Dashboard UI/UX Expectations

### 7.1 Expected Dashboard Tabs/Sections

**Lesson 14 Results Section:**
```
┌─────────────────────────────────────────┐
│  Lesson 14: Agent Evaluation Results    │
├─────────────────────────────────────────┤
│  📊 Trajectory Evaluation               │
│  📊 Multi-Agent Pattern Comparison      │
│  📊 Autorater Calibration               │
│  📊 Benchmark Results                   │
│  🆕 Memory Systems Evaluation           │  ← New entry
└─────────────────────────────────────────┘
```

**Each result displays:**
- File name (clickable)
- Execution mode badge (DEMO / FULL)
- Creation date
- Number of tests
- Summary metrics (mean ± std)
- Radar chart (if available)
- Detailed results table (expandable)

---

### 7.2 User Interaction Flow

**Step 1: File Selection**
- User sees list of all `*.json` files in `lesson-14/results/`
- Status indicator (✅ ok, ⚠️ no_data, ❌ invalid)

**Step 2: Summary View**
- High-level metrics displayed as cards
- Radar chart visualization
- Pattern rankings (if available)

**Step 3: Detailed Analysis**
- Expandable table with all `detailed_results`
- Sortable columns
- Filterable by categorical dimensions
- Export to CSV option

**Step 4: Comparison (Optional)**
- Select multiple result files
- Side-by-side comparison
- Overlayed radar charts

---

## 8. Final Integration Checklist

**Before committing `memory_systems_evaluation.json`:**

**File Validation:**
- [ ] JSON syntax valid (test with `python -m json.tool`)
- [ ] All required fields present
- [ ] File size <100 KB (DEMO) or <500 KB (FULL)
- [ ] Saved to correct path: `lesson-14/results/memory_systems_evaluation.json`

**Schema Validation:**
- [ ] `version`, `created`, `execution_mode` present
- [ ] `summary_statistics` has 5-7 metrics with `mean` and `std`
- [ ] `detailed_results` has 20+ entries (DEMO) or 100+ (FULL)
- [ ] `radar_chart_data` valid (polygon closed, values in range)

**Dashboard Integration:**
- [ ] File appears in dashboard file list
- [ ] Status = `"ok"` (not error/invalid/no_data)
- [ ] Summary metrics display correctly
- [ ] Radar chart renders
- [ ] Detailed results table loads
- [ ] Filters work (pattern, use_case, etc.)

**Documentation:**
- [ ] Update `lesson-14/TUTORIAL_INDEX.md` with memory evaluation notebook
- [ ] Add interpretation guide in notebook markdown cells
- [ ] Document how to run evaluation in README

---

**Document Status:** ✅ Complete
**Validation Functions Provided:** 3 (validate_results_json, validate_radar_chart_data, load_and_validate_results)
**Integration Checklists:** 3 (Pre-Implementation, Schema Validation, Dashboard Integration)
**Testing Strategies:** 2 (Manual + Automated pytest examples)
**Next Step:** Begin Phase 2 - Validate Task 1.0 Against Research
