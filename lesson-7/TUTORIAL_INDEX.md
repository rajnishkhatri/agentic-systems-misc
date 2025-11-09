# Lesson 7: Tutorial Index

## Overview

Lesson 7 teaches **manual trace inspection** and annotation workflows for conversational AI systems. When automated evaluation isn't sufficient, you need tools to efficiently review conversation traces, identify failure modes, and create labeled datasets for further analysis. This lesson demonstrates converting JSON traces to CSV for easy review and (optionally) building custom annotation interfaces.

**Learning Time:** ~2-3 hours
**Difficulty:** Beginner to Intermediate
**Prerequisites:** Understanding of JSON/CSV formats, basic Python scripting

---

## Learning Objectives

By completing these tutorials, you will be able to:
- ✅ Understand when manual inspection is necessary vs. automated evaluation
- ✅ Convert complex JSON conversation traces to human-readable CSV
- ✅ Format conversation data for spreadsheet-based review
- ✅ Handle nested JSON structures (messages, tool calls)
- ✅ Extract key fields for manual annotation
- ✅ [Optional] Design simple annotation interfaces for bulk labeling
- ✅ Integrate manual annotations with automated analysis pipelines

---

## Tutorials

### 1. Trace Inspection Concepts
**File:** `trace_inspection_concepts.md`
**Reading Time:** 12-15 minutes
**Topics:**
- When human review is necessary (edge cases, ambiguity, safety)
- Manual vs. automated evaluation trade-offs
- Annotation workflow design principles
- Quality control for manual labels (inter-annotator agreement)
- Combining manual and automated evaluation
- Sampling strategies for efficient review

**When to use:** Start here to understand when and why manual inspection matters.

**Key Decision Framework:**
```
Use Manual Inspection When:
  ✅ Evaluation criteria are subjective or ambiguous
  ✅ Edge cases require human judgment
  ✅ Safety-critical applications need human oversight
  ✅ Building initial labeled dataset for LLM-as-Judge
  ✅ Validating automated evaluation quality

Use Automated Evaluation When:
  ✅ Clear, objective criteria exist
  ✅ Large-scale evaluation needed (1000+ examples)
  ✅ Repeatable, consistent judgments required
  ✅ Real-time production monitoring
```

---

### 2. CSV Conversion Tutorial
**File:** `csv_conversion_tutorial.md`
**Reading Time:** 15-18 minutes
**Topics:**
- Converting JSON traces to CSV format
- Flattening nested conversation structures
- Formatting messages with role prefixes (USER:, AGENT:, TOOL:)
- Summarizing tool calls for readability
- Preserving metadata while ensuring CSV compatibility
- Handling special characters and escaping

**When to use:** Before manual review, use this to convert JSON traces to spreadsheet-friendly format.

**Conversion Example:**
```
Input (JSON):
{
  "id": "trace_123",
  "messages": [
    {"role": "user", "content": "Find vegan recipes"},
    {"role": "assistant", "content": "I'll search our database."},
    {"role": "tool", "tool_name": "search_recipes", "output": "..."}
  ],
  "failure_mode": "dietary_violation"
}

Output (CSV):
trace_id | user_query | conversation | tool_calls | failure_mode
---------|------------|--------------|------------|-------------
trace_123| Find vegan...| USER: Find...| search_rec...| dietary_...
```

---

### 3. [Optional] Labeling Tool Tutorial
**File:** `labeling_tool_tutorial.md`
**Reading Time:** 18-22 minutes
**Topics:**
- Designing annotation interfaces (web vs. CLI vs. spreadsheet)
- Building simple Flask/FastHTML labeling UIs
- Annotation task definition and instructions
- Capturing annotator notes and confidence levels
- Exporting labeled data for analysis
- Tracking annotation progress

**When to use:** If you need to label 50+ traces efficiently, consider building a custom tool.

**Note:** The reference implementation includes a `labeling-tool/` directory with a basic web interface example.

---

### 4. Annotation Workflow Diagram (Visual)
**File:** `diagrams/annotation_workflow.mmd` | [PNG version](diagrams/annotation_workflow.png)
**Format:** Mermaid diagram (viewable on GitHub) | High-resolution PNG export available
**Topics:**
- Complete workflow: Export traces → Convert → Annotate → Analyze
- Decision points for sampling vs. exhaustive review
- Integration with automated evaluation pipelines
- Quality control feedback loops

**When to use:** Reference this to understand the end-to-end inspection process.

---

## Recommended Learning Path

```
┌────────────────────────────────────────────────────────┐
│     Lesson 7: Trace Inspection Workflow                │
├────────────────────────────────────────────────────────┤
│                                                        │
│  STEP 1: Understand Manual Inspection                 │
│  ┌──────────────────────────────────────────────────┐ │
│  │ 1. Complete "Trace Inspection Concepts" tutorial │ │
│  │ 2. Decide which traces need manual review        │ │
│  │ 3. Determine sampling strategy (random, edge, etc)│ │
│  └──────────────────────────────────────────────────┘ │
│                                                        │
│  STEP 2: Convert Traces for Review                    │
│  ┌──────────────────────────────────────────────────┐ │
│  │ 4. Complete "CSV Conversion" tutorial            │ │
│  │ 5. Run scripts/convert_traces_to_csv.py          │ │
│  │    → Input: homeworks/hw5/data/synthetic_traces.json│ │
│  │    → Output: data/traces.csv                      │ │
│  │ 6. Open traces.csv in Excel/Google Sheets        │ │
│  └──────────────────────────────────────────────────┘ │
│                                                        │
│  STEP 3A: Manual Review (Simple)                       │
│  ┌──────────────────────────────────────────────────┐ │
│  │ 7. Review traces in spreadsheet                  │ │
│  │ 8. Add annotation columns (notes, labels)        │ │
│  │ 9. Export annotated CSV                          │ │
│  └──────────────────────────────────────────────────┘ │
│                                                        │
│  STEP 3B: Annotation Interface (Advanced, Optional)   │
│  ┌──────────────────────────────────────────────────┐ │
│  │ 7. Complete "Labeling Tool" tutorial             │ │
│  │ 8. Set up labeling-tool/ web interface           │ │
│  │ 9. Annotate traces through UI                    │ │
│  │ 10. Export results to JSON                       │ │
│  └──────────────────────────────────────────────────┘ │
│                                                        │
│  STEP 4: Analysis Integration                         │
│  ┌──────────────────────────────────────────────────┐ │
│  │ 11. Load annotated data into analysis scripts    │ │
│  │ 12. Combine with automated metrics (if applicable)│ │
│  │ 13. Report findings and patterns                 │ │
│  └──────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────┘
```

---

## Key Concepts

### Manual Inspection Use Cases
**When to inspect manually:**

1. **Initial Dataset Creation**
   - Creating ground truth for LLM-as-Judge (HW3, Lesson 4)
   - Labeling examples for few-shot prompts
   - Discovering unknown failure modes (HW2 open coding)

2. **Edge Case Investigation**
   - Traces where automated evaluation is uncertain
   - Safety-critical failures requiring human review
   - Contradictory or ambiguous user queries

3. **Quality Validation**
   - Spot-checking automated labels (Lesson 4)
   - Verifying inter-annotator agreement
   - Auditing production system failures

### CSV Conversion Patterns
**Flattening conversations:**

```python
# Nested JSON structure
messages = [
    {"role": "user", "content": "Find recipes"},
    {"role": "assistant", "content": "Searching..."},
    {"role": "tool", "name": "search", "output": "{...}"}
]

# Flattened for CSV
conversation_text = """
USER: Find recipes
AGENT: Searching...
TOOL (search): {...}
"""
```

**Benefits:**
- ✅ Easy to read in spreadsheets
- ✅ Searchable with Ctrl+F
- ✅ Compatible with Excel, Google Sheets, etc.
- ✅ Preserves conversation flow

### Annotation Best Practices
**Guidelines for quality labeling:**

1. **Clear Instructions**
   - Define criteria explicitly before starting
   - Provide 3-5 example annotations
   - Include edge case guidance

2. **Consistency Checks**
   - Have 2+ annotators label same 20 traces
   - Calculate inter-annotator agreement (Cohen's kappa)
   - Discuss disagreements and refine criteria

3. **Progress Tracking**
   - Mark traces as "reviewed", "pending", "uncertain"
   - Track time per trace (identify difficult cases)
   - Save intermediate progress regularly

---

## Practical Exercises

After completing the tutorials, try these exercises:

1. **Conversion Practice**
   - Take 10 traces from HW5 or Lesson 4
   - Write a custom CSV converter with your preferred columns
   - Open in a spreadsheet and verify readability
   - Add 2-3 annotation columns

2. **Manual Annotation Exercise**
   - Select 20 conversation traces
   - Define a binary labeling task (e.g., "polite vs. rude")
   - Annotate all 20 traces in a spreadsheet
   - Track time and any ambiguous cases

3. **Inter-Annotator Agreement**
   - Have a friend/colleague label the same 20 traces
   - Compare your labels to theirs
   - Calculate agreement percentage
   - Discuss disagreements to refine criteria

---

## Common Pitfalls

### Conversion Errors
- ❌ **Lost information:** Dropping metadata or tool outputs
- ❌ **Unreadable formatting:** No line breaks in long conversations
- ❌ **CSV escaping issues:** Quotes or commas break parsing
- ❌ **Too many columns:** 20+ columns make spreadsheet unusable

### Manual Annotation
- ❌ **Vague criteria:** "Good vs. bad" isn't specific enough
- ❌ **No examples:** Annotators guess what you want
- ❌ **Fatigue:** Reviewing 100 traces at once reduces quality
- ❌ **No validation:** Trusting single annotator without checks

### Tool Design (Optional)
- ❌ **Over-engineering:** Building complex UI for 20 traces
- ❌ **No keyboard shortcuts:** Slows down annotation significantly
- ❌ **Missing undo:** Can't fix accidental mis-clicks
- ❌ **No progress saving:** Losing work after browser crash

---

## Reference Files

### Assignment Materials
- [`README.md`](README.md) - Lesson overview (note: calls itself "Lesson 6")
- [`requirements.txt`](requirements.txt) - Python dependencies

### Scripts (You'll Run These)
- [`scripts/convert_traces_to_csv.py`](scripts/convert_traces_to_csv.py) - JSON to CSV converter

### Data Files
- [`data/traces.csv`](data/traces.csv) - Output CSV (generated by script)
- [`data/inspection_results.json`](data/inspection_results.json) - Future: Manual annotation results

### Optional: Labeling Tool
- [`labeling-tool/`](labeling-tool/) - Web-based annotation interface (if available)

---

## Tools & Libraries

**Required:**
- `pandas` - CSV manipulation
- `json` - JSON parsing (built-in)
- Any spreadsheet software (Excel, Google Sheets, LibreOffice)

**Optional (for annotation tool):**
- `flask` or `fasthtml` - Web interface frameworks
- `streamlit` - Quick annotation UIs

**Installation:**
```bash
cd lesson-7
pip install -r requirements.txt
```

---

## Expected Outputs

After completing Lesson 7, you should have:
- ✅ Converted CSV file from JSON traces (data/traces.csv)
- ✅ Annotated traces with manual labels (if applicable)
- ✅ Understanding of when manual inspection is valuable
- ✅ Workflow for integrating manual labels with automated evaluation

**Example CSV Output:**
```csv
trace_id,customer_persona,failure_mode,user_query,conversation_messages,tool_calls
trace_001,gluten_free_family,wrong_recipe,"Find gf pasta","USER: Find gf pasta\nAGENT: Here's...",search_recipes(...)
trace_002,vegan_athlete,dietary_violation,"Quick protein","USER: Quick protein\nAGENT: Try...",get_recipes(...)
...
```

---

## Real-World Applications

Manual trace inspection is critical for:
- **Production debugging:** Investigating user-reported issues
- **Safety monitoring:** Reviewing flagged conversations for violations
- **Training data creation:** Building datasets for supervised learning
- **Product improvement:** Identifying usability issues through conversation analysis

**Example Workflow:**
```
User reports: "Bot suggested non-vegan recipe for vegan query"
  ↓
1. Export that trace to CSV
2. Manual review confirms bug
3. Find similar traces (automated search)
4. Review sample of similar traces manually
5. Implement fix and validate
```

---

## Connection to Other Lessons

| Lesson/HW | Manual Inspection Role |
|-----------|------------------------|
| **HW2** | Open coding requires manual trace review |
| **HW3** | Creating ground truth labels for judge evaluation |
| **HW5** | Validating synthetic failure labels are realistic |
| **Lesson 4** | Spot-checking automated substantiation labels |

**Key Insight:** Even highly automated evaluation systems need manual inspection for quality control and edge case handling.

---

## Next Steps

After completing Lesson 7, you'll have:
- ✅ Skills to convert traces for manual review
- ✅ Understanding of annotation workflows
- ✅ Ability to integrate manual and automated evaluation

**Explore related lessons:**

👉 [Lesson 4: Substantiation Evaluation](../lesson-4/TUTORIAL_INDEX.md) (uses manual spot-checking)
👉 [Lesson 8: Model Cascades](../lesson-8/TUTORIAL_INDEX.md)

---

## FAQ

**Q: How many traces should I review manually?**
A: Depends on task. For ground truth: 100-200. For spot-checking: 10-20. For debugging: As many as needed to find the pattern.

**Q: Should I build a custom annotation tool?**
A: Only if labeling 50+ traces. For smaller sets, spreadsheets are faster.

**Q: What if annotators disagree on labels?**
A: Discuss disagreements to refine criteria. If disagreement persists, the task may be too subjective for reliable evaluation.

**Q: Can I automate the CSV conversion?**
A: Yes! The provided convert_traces_to_csv.py script automates this. Customize it for your trace format.

**Q: How do I handle very long conversations in CSV?**
A: Truncate or summarize. Alternatively, use JSON for storage and CSV only for high-level metadata.

**Q: Should I annotate all traces or just a sample?**
A: For most purposes, a well-chosen sample is sufficient. Random sampling works for general quality; stratified sampling (by failure type, user persona, etc.) is better for targeted analysis.

---

**Tutorial Status:** ⏳ In Development
**Last Updated:** 2025-10-29
**Maintainer:** AI Evaluation Course Team
