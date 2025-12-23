# DSPy Distillation Trace Report Guide

## Overview

The HTML trace report provides an interactive visualization of JSONL traces from DSPy distillation and prompt tuning, similar to the format used in `natural_language_report_v6_tot_trace.html`.

## Generating Reports

### Teacher Traces Report

```bash
cd lesson-18/dispute-chatbot/backend/phases
python generate_trace_report.py --file teacher --output distillation_data/teacher_trace_report.html
```

This generates a comprehensive report showing:
- **Dashboard Statistics**: Acceptance rate, counts by status
- **Filterable Table**: All traces with status, category, branches, confidence
- **Expandable Details**: Click any row to see full branch analysis

## Report Features

### 1. Dashboard Cards
- **Acceptance Rate**: Percentage of traces accepted for fine-tuning
- **Status Counts**: Accepted, Rejected, Parse Errors

### 2. Interactive Filters
- Filter by status: All, Accepted, Rejected, Parse Errors
- Click filter buttons to show/hide traces

### 3. Trace Details
Each trace row can be expanded to show:

#### Tree-of-Thought Branch Analysis
- **Branch A**: Transaction Acknowledgment (Acknowledged/Denied/Unclear)
- **Branch B**: Complaint Specifics (Amount/Quality/Processing/Unspecified)
- **Branch C**: User Persona (Frustrated/Confused/Accusatory/Neutral)

#### Branch Synthesis
- **Agreement Score**: Visual bar showing branch alignment (0.0-1.0)
- **Priority Rule Applied**: Which rule was used to resolve conflicts
- **Reasoning**: Full synthesis logic from teacher model

#### Comparison
- **Ground Truth**: Expected category and reason code group
- **Teacher Output**: Predicted category, confidence, rationale
- **Match/Mismatch**: Visual indicators for category correctness

### 4. Status Indicators
- 🟢 **Green (Accepted)**: Trace passed validation
- 🔴 **Red (Rejected)**: Trace failed validation (shows rejection reasons)
- 🟠 **Orange (Parse Error)**: JSON parsing failed

## File Locations

- **Generated Report**: `distillation_data/teacher_trace_report.html`
- **Source Data**: `distillation_data/teacher_trace_log.jsonl`
- **Script**: `generate_trace_report.py`

## Viewing the Report

Simply open the HTML file in any web browser:

```bash
open distillation_data/teacher_trace_report.html  # macOS
xdg-open distillation_data/teacher_trace_report.html  # Linux
start distillation_data/teacher_trace_report.html  # Windows
```

Or use a local web server:

```bash
cd distillation_data
python -m http.server 8000
# Then open http://localhost:8000/teacher_trace_report.html
```

## Report Structure

The report follows the same structure as the reference report:

1. **Header**: Title, subtitle, generation timestamp
2. **Dashboard**: Key statistics in card format
3. **Legend**: Branch color coding
4. **Filters**: Status-based filtering buttons
5. **Table**: Main trace listing with expandable rows
6. **Details**: Full branch analysis, synthesis, and comparisons

## Example Usage

### View All Accepted Traces
1. Open the HTML report
2. Click "Accepted" filter button
3. Only accepted traces are shown

### Analyze Rejection Patterns
1. Click "Rejected" filter button
2. Expand rejected traces to see rejection reasons
3. Look for common patterns in rejection reasons

### Compare Categories
1. Use browser search (Cmd/Ctrl+F) to find specific categories
2. Expand traces to see branch analysis
3. Compare synthesis reasoning across similar cases

## Future Enhancements

The script can be extended to support:
- Fine-tuning dataset reports
- Student evaluation reports
- Category-based filtering
- Persona-based filtering
- Export to PDF
- Search functionality

## Related Tools

- `search_traces.py`: Command-line search tool for JSONL files
- `TRACE_FILES_SUMMARY.md`: Documentation of trace file formats

