# Task 0.5: Results JSON Schema Template

**Purpose:** Document required JSON schema for `lesson-14/results/*.json` files to ensure memory systems evaluation results integrate with evaluation dashboard.

**Sources:**
- `lesson-14/results/trajectory_eval_results.json` (325 lines)
- `lesson-14/results/multi_agent_pattern_comparison.json` (366 lines)

---

## 1. Standard Results JSON Schema

### 1.1 Required Top-Level Keys

**All results JSON files MUST include:**
```json
{
  "version": "string",           // Format: "X.Y" (e.g., "1.0")
  "created": "string",            // Format: "YYYY-MM-DD" (e.g., "2025-11-14")
  "execution_mode": "string",     // Options: "DEMO", "FULL"
  "summary_statistics": {...},    // Aggregated metrics
  "detailed_results": [...]       // Array of individual test results
}
```

**Optional but Recommended:**
```json
{
  "radar_chart_data": {...},     // For visualization in dashboard
  "experiment_metadata": {...},  // Additional context
  "recommendations": {...}        // Actionable insights (pattern-specific)
}
```

---

### 1.2 `summary_statistics` Schema

**Purpose:** Provide high-level aggregate metrics for dashboard overview.

**Structure:**
```json
"summary_statistics": {
  "[metric_name]": {
    "mean": float,       // Average value across all tests
    "std": float         // Standard deviation (measure of variance)
  },
  // Repeat for each metric
}
```

**Example (Trajectory Evaluation):**
```json
"summary_statistics": {
  "exact_match": {
    "mean": 0.9,
    "std": 0.30779350562554625
  },
  "in_order_match": {
    "mean": 1.0,
    "std": 0.0
  },
  "precision": {
    "mean": 0.975,
    "std": 0.07694837640638655
  },
  "recall": {
    "mean": 1.0,
    "std": 0.0
  }
}
```

**Rules:**
- Metric names use `snake_case`
- Values are floats between 0.0 and 1.0 (percentages as decimals)
- Include `mean` and `std` for every metric
- Minimum 3 metrics, maximum 10 (for radar chart clarity)

---

### 1.3 `radar_chart_data` Schema

**Purpose:** Enable multi-dimensional visualization in dashboard.

**Structure:**
```json
"radar_chart_data": {
  "labels": [
    "metric_1",
    "metric_2",
    "metric_3",
    // ... up to 10 metrics
  ],
  "values": [
    float,    // Value for metric_1
    float,    // Value for metric_2
    float,    // Value for metric_3
    // ... matching order of labels
    float     // Repeat first value to close polygon
  ]
}
```

**Example (Trajectory Evaluation):**
```json
"radar_chart_data": {
  "labels": [
    "exact_match",
    "in_order_match",
    "any_order_match",
    "precision",
    "recall",
    "single_tool_use"
  ],
  "values": [
    0.9,
    1.0,
    1.0,
    0.975,
    1.0,
    0.975,
    0.9    // First value repeated to close polygon
  ]
}
```

**Rules:**
- `labels` must match keys in `summary_statistics`
- `values` array length = `labels` length + 1 (last value repeats first)
- All values between 0.0 and 1.0
- Order matters for visualization (group related metrics)

---

### 1.4 `detailed_results` Schema

**Purpose:** Store individual test results for drill-down analysis.

**Structure:**
```json
"detailed_results": [
  {
    "test_id": "string",          // Unique identifier (e.g., "test_001")
    "reference_id": "string",     // Reference data identifier (optional)
    "[metric_1]": float,          // All metrics from summary_statistics
    "[metric_2]": float,
    // ... all other metrics
    "[dimension_1]": "string",    // Categorical dimensions (e.g., "complexity": "simple")
    "[dimension_2]": "string",    // Additional metadata
    "[custom_field]": any         // Domain-specific fields
  },
  // ... one object per test case
]
```

**Example (Trajectory Evaluation):**
```json
{
  "test_id": "test_001",
  "reference_id": "ref_001",
  "exact_match": 1.0,
  "in_order_match": 1.0,
  "any_order_match": 1.0,
  "precision": 1.0,
  "recall": 1.0,
  "single_tool_use": 1.0,
  "complexity": "simple",
  "domain": "recipe"
}
```

**Rules:**
- **MUST** include all metrics from `summary_statistics` as individual keys
- **MUST** include `test_id` (unique identifier)
- **SHOULD** include categorical dimensions for analysis (complexity, domain, pattern, etc.)
- Metric values must match data types in `summary_statistics`

---

## 2. Experiment Metadata Schema

### 2.1 `experiment_metadata` Structure

**Purpose:** Provide execution context and reproducibility information.

**Structure:**
```json
"experiment_metadata": {
  "mode": "string",                  // "DEMO" or "FULL"
  "num_scenarios": int,              // Number of unique test scenarios
  "num_patterns": int,               // Number of patterns/conditions tested (optional)
  "total_executions": int,           // Total tests run (scenarios × patterns)
  "simulation_type": "string",       // "theoretical", "live", "hybrid"
  "timestamp": "string"              // Format: "YYYY-MM-DD HH:MM:SS"
}
```

**Example (Multi-Agent Pattern Comparison):**
```json
"experiment_metadata": {
  "mode": "DEMO",
  "num_scenarios": 5,
  "num_patterns": 5,
  "total_executions": 25,
  "simulation_type": "theoretical",
  "timestamp": "2025-11-15 09:25:04"
}
```

**Rules:**
- `mode` must match top-level `execution_mode`
- `total_executions` should equal `len(detailed_results)`
- `timestamp` uses ISO 8601 format (or "YYYY-MM-DD HH:MM:SS")

---

## 3. Pattern-Specific Extensions

### 3.1 Complexity Breakdown (Trajectory Evaluation Pattern)

**Purpose:** Show metric performance by test complexity level.

**Structure:**
```json
"complexity_breakdown": {
  "[metric_name]": {
    "simple": float,
    "medium": float,
    "complex": float
  },
  // Repeat for each metric
}
```

**Example:**
```json
"complexity_breakdown": {
  "exact_match": {
    "complex": 1.0,
    "medium": 1.0,
    "simple": 0.833
  },
  "precision": {
    "complex": 1.0,
    "medium": 1.0,
    "simple": 0.958
  }
}
```

**When to Use:**
- Evaluation involves categorized test cases (simple/medium/complex)
- Want to identify performance gaps by difficulty level
- Need to visualize performance degradation trends

---

### 3.2 Pattern Metrics (Multi-Agent Comparison Pattern)

**Purpose:** Compare aggregate metrics across different patterns/approaches.

**Structure:**
```json
"pattern_metrics": {
  "[pattern_name]": {
    "avg_latency": float,
    "avg_cost": float,
    "avg_quality": float,
    "avg_agents": float    // Or other pattern-specific metric
  },
  // Repeat for each pattern
}
```

**Example:**
```json
"pattern_metrics": {
  "hierarchical": {
    "avg_latency": 14.077611602197498,
    "avg_cost": 0.25588956265398316,
    "avg_quality": 0.9339999999999999,
    "avg_agents": 5.0
  },
  "diamond": {
    "avg_latency": 6.625707054901061,
    "avg_cost": 0.23244103654387235,
    "avg_quality": 0.9640000000000001,
    "avg_agents": 3.0
  }
}
```

**When to Use:**
- Comparing multiple implementations/approaches
- Benchmark studies (A/B testing patterns)
- Trade-off analysis (latency vs cost vs quality)

---

### 3.3 Pattern Rankings (Winner Summary)

**Purpose:** Quickly identify best performer per dimension.

**Structure:**
```json
"pattern_rankings": {
  "fastest": "string",           // Pattern with lowest avg_latency
  "cheapest": "string",          // Pattern with lowest avg_cost
  "highest_quality": "string"    // Pattern with highest avg_quality
}
```

**Example:**
```json
"pattern_rankings": {
  "fastest": "diamond",
  "cheapest": "collaborative",
  "highest_quality": "adaptive_loop"
}
```

**When to Use:**
- Multi-pattern comparison studies
- Executive summaries (non-technical stakeholders)
- Quick decision-making support

---

### 3.4 Recommendations (Actionable Insights)

**Purpose:** Provide guidance on when to use each pattern/approach.

**Structure:**
```json
"recommendations": {
  "[pattern_name]": {
    "description": "string",
    "use_when": ["string", "string", ...],
    "avoid_when": ["string", "string", ...]
  },
  // Repeat for each pattern
}
```

**Example:**
```json
"recommendations": {
  "hierarchical": {
    "description": "Complex tasks with clear subtask decomposition. Trade higher latency for better quality and coordination.",
    "use_when": [
      "Task can be broken into independent subtasks",
      "Need specialist expertise",
      "Quality matters more than speed"
    ],
    "avoid_when": [
      "Real-time response required",
      "Simple tasks",
      "Limited budget"
    ]
  }
}
```

**When to Use:**
- Educational/tutorial notebooks
- Pattern selection guides
- Production deployment decision support

---

## 4. Memory Systems Evaluation Schema (Task 5.0 Implementation)

### 4.1 Proposed Schema for Memory Evaluation Results

**File:** `lesson-14/results/memory_systems_evaluation.json`

**Structure:**
```json
{
  "version": "1.0",
  "created": "2025-11-15",
  "execution_mode": "DEMO",
  "num_evaluations": 30,
  "summary_statistics": {
    "context_compression_ratio": {
      "mean": 0.72,
      "std": 0.15
    },
    "retrieval_accuracy": {
      "mean": 0.94,
      "std": 0.08
    },
    "token_efficiency": {
      "mean": 0.85,
      "std": 0.12
    },
    "memory_retention": {
      "mean": 0.91,
      "std": 0.09
    },
    "cost_reduction": {
      "mean": 0.78,
      "std": 0.14
    }
  },
  "radar_chart_data": {
    "labels": [
      "context_compression_ratio",
      "retrieval_accuracy",
      "token_efficiency",
      "memory_retention",
      "cost_reduction"
    ],
    "values": [
      0.72,
      0.94,
      0.85,
      0.91,
      0.78,
      0.72
    ]
  },
  "memory_pattern_metrics": {
    "fifo_trimming": {
      "avg_compression": 0.60,
      "avg_accuracy": 0.82,
      "avg_cost_reduction": 0.55
    },
    "rolling_summarization": {
      "avg_compression": 0.75,
      "avg_accuracy": 0.92,
      "avg_cost_reduction": 0.68
    },
    "memorybank": {
      "avg_compression": 0.80,
      "avg_accuracy": 0.96,
      "avg_cost_reduction": 0.75
    },
    "a_mem": {
      "avg_compression": 0.82,
      "avg_accuracy": 0.97,
      "avg_cost_reduction": 0.77
    },
    "search_o1": {
      "avg_compression": 0.85,
      "avg_accuracy": 0.98,
      "avg_cost_reduction": 0.80
    }
  },
  "detailed_results": [
    {
      "test_id": "mem_001",
      "memory_pattern": "fifo_trimming",
      "conversation_length": 10,
      "context_compression_ratio": 0.58,
      "retrieval_accuracy": 0.80,
      "token_efficiency": 0.65,
      "memory_retention": 0.75,
      "cost_reduction": 0.50,
      "use_case": "short_conversation"
    },
    // ... more detailed results
  ],
  "pattern_rankings": {
    "highest_compression": "search_o1",
    "highest_accuracy": "search_o1",
    "best_cost_reduction": "search_o1"
  },
  "recommendations": {
    "fifo_trimming": {
      "description": "Simple FIFO trimming for short conversations. Low complexity, moderate performance.",
      "use_when": [
        "Conversation length < 20 turns",
        "Simple chatbot use case",
        "Minimal implementation time"
      ],
      "avoid_when": [
        "Critical information in early turns",
        "Long conversations (>20 turns)",
        "High accuracy requirements"
      ]
    },
    "rolling_summarization": {
      "description": "LLM-based summarization for balanced quality and cost. Good default choice.",
      "use_when": [
        "Conversation length 20-100 turns",
        "Need to preserve semantic meaning",
        "Moderate budget for LLM calls"
      ],
      "avoid_when": [
        "Zero-cost requirement",
        "Real-time performance critical",
        "Simple conversations (use FIFO)"
      ]
    },
    "memorybank": {
      "description": "Adaptive memory with forgetting curve. Best for long-term chatbot relationships.",
      "use_when": [
        "Chatbot with returning users",
        "Conversations span weeks/months",
        "User personalization important"
      ],
      "avoid_when": [
        "One-time interactions",
        "High implementation complexity unacceptable",
        "No vector database available"
      ]
    },
    "a_mem": {
      "description": "Zettelkasten-inspired interconnected memories. Ideal for knowledge management.",
      "use_when": [
        "Research assistant use case",
        "Interconnected concepts",
        "Long-running projects"
      ],
      "avoid_when": [
        "Simple Q&A chatbot",
        "Real-time response required",
        "No graph database infrastructure"
      ]
    },
    "search_o1": {
      "description": "RAG during reasoning for highest quality. Variable latency, highest accuracy.",
      "use_when": [
        "Complex reasoning tasks",
        "External knowledge required",
        "Quality matters more than speed"
      ],
      "avoid_when": [
        "Fixed latency requirement",
        "Simple factual queries",
        "No external knowledge sources"
      ]
    }
  }
}
```

---

## 5. Validation Checklist for Task 5.0

When creating `memory_systems_evaluation.json`:

**Required Fields:**
- [ ] `version` (string, format "X.Y")
- [ ] `created` (string, format "YYYY-MM-DD")
- [ ] `execution_mode` ("DEMO" or "FULL")
- [ ] `summary_statistics` (dict with mean/std for each metric)
- [ ] `detailed_results` (array of test results)

**Recommended Fields:**
- [ ] `radar_chart_data` (for dashboard visualization)
- [ ] `memory_pattern_metrics` (aggregate by pattern type)
- [ ] `pattern_rankings` (winner summary)
- [ ] `recommendations` (actionable guidance)

**Data Quality:**
- [ ] All metric values are floats between 0.0 and 1.0
- [ ] `radar_chart_data.values` length = `labels` length + 1
- [ ] `detailed_results` count matches `num_evaluations`
- [ ] All metrics in `summary_statistics` appear in `detailed_results`

**Dashboard Integration:**
- [ ] Metric names use `snake_case`
- [ ] No special characters in keys (use `_` not `-` or spaces)
- [ ] JSON is valid (use `jsonlint` or `python -m json.tool`)
- [ ] File saved to `lesson-14/results/memory_systems_evaluation.json`

---

## 6. Common Pitfalls to Avoid

**1. Mismatched Metric Names:**
```json
// ❌ BAD: Inconsistent naming
"summary_statistics": {
  "exact_match": {...}
},
"detailed_results": [{
  "exactMatch": 1.0  // Different name!
}]

// ✅ GOOD: Consistent snake_case
"summary_statistics": {
  "exact_match": {...}
},
"detailed_results": [{
  "exact_match": 1.0
}]
```

**2. Incorrect Radar Chart Polygon Closure:**
```json
// ❌ BAD: Missing repeated first value
"radar_chart_data": {
  "labels": ["metric1", "metric2", "metric3"],
  "values": [0.9, 0.8, 0.85]  // Polygon not closed!
}

// ✅ GOOD: First value repeated to close polygon
"radar_chart_data": {
  "labels": ["metric1", "metric2", "metric3"],
  "values": [0.9, 0.8, 0.85, 0.9]  // Closed polygon
}
```

**3. Missing Required Fields in `detailed_results`:**
```json
// ❌ BAD: Missing metrics from summary
{
  "test_id": "test_001",
  "metric1": 0.9
  // Where are metric2 and metric3?
}

// ✅ GOOD: All metrics included
{
  "test_id": "test_001",
  "metric1": 0.9,
  "metric2": 0.8,
  "metric3": 0.85
}
```

**4. Values Outside 0.0-1.0 Range:**
```json
// ❌ BAD: Percentage as integer
"summary_statistics": {
  "accuracy": {
    "mean": 95,  // Should be 0.95!
    "std": 5
  }
}

// ✅ GOOD: Decimal representation
"summary_statistics": {
  "accuracy": {
    "mean": 0.95,
    "std": 0.05
  }
}
```

---

## 7. Dashboard Integration Points (Task 0.6 Cross-Reference)

**Dashboard File:** `lesson-9-11/evaluation_dashboard.py`

**Expected Status Codes:**
- `"ok"` - Valid JSON with all required fields
- `"no_data"` - File exists but empty or missing key fields
- `"invalid"` - JSON parse error or schema validation failure
- `"error"` - File not found or I/O error

**Validation Logic (from Task 0.6 findings):**
1. Load JSON file
2. Check for required keys: `version`, `created`, `execution_mode`, `summary_statistics`, `detailed_results`
3. Validate `radar_chart_data` structure if present
4. Verify metric consistency between `summary_statistics` and `detailed_results`
5. Return status code + validated data

**Integration Checklist:**
- [ ] JSON file loads without parse errors
- [ ] All required top-level keys present
- [ ] `radar_chart_data` format correct (if used)
- [ ] Metric names consistent across sections
- [ ] Values in valid range (0.0-1.0 for percentages)

---

**Document Status:** ✅ Complete
**Schema Patterns Documented:** 2 (Trajectory Evaluation, Multi-Agent Comparison)
**Proposed Memory Schema:** Ready for Task 5.0 implementation
**Validation Checklists:** 2 (Required Fields, Data Quality)
**Next Step:** Proceed to Task 0.6 (Dashboard data loading validation)
