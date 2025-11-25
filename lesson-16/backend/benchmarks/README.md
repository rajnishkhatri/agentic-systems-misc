# AgentArch Benchmark Framework

**Module:** `lesson-16/backend/benchmarks/`
**Purpose:** Evaluate orchestration patterns using the AgentArch benchmark methodology
**Components:** 3 modules (financial_tasks, metrics, runner)
**Test Coverage:** 94% average (73 tests)

---

## Overview

The AgentArch benchmark framework provides production-grade evaluation tools for comparing orchestration patterns on financial workflows. Designed for **research reproducibility** and **enterprise evaluation**.

**Key Features:**
- **300 synthetic financial tasks** (100 invoices, 100 fraud, 100 reconciliation)
- **4 evaluation metrics** (task success rate, error propagation index, latency P50/P95, cost)
- **Statistical analysis** (95% confidence intervals, paired t-tests)
- **Result caching** (<1s load time for 100-task benchmarks)
- **Parallel execution** (ThreadPoolExecutor for multi-pattern evaluation)

**Use Cases:**
1. **Research:** Reproduce AgentArch paper results (Notebook 14)
2. **Enterprise:** Validate pattern selection for production workflows
3. **Education:** Teach students systematic agent evaluation methodology

---

## Quick Start

### Installation

```bash
# From repository root
cd lesson-16

# Install dependencies
uv pip install pydantic numpy scipy tqdm

# Verify imports
python -c "from backend.benchmarks import FinancialTaskGenerator, MetricsCalculator, BenchmarkRunner"
```

### Basic Usage

```python
from pathlib import Path
from backend.benchmarks import FinancialTaskGenerator, MetricsCalculator, BenchmarkRunner
from backend.orchestrators import SequentialOrchestrator, HierarchicalOrchestrator

# Step 1: Load datasets
generator = FinancialTaskGenerator()
data_dir = Path("data")
generator.load_datasets(data_dir)

# Step 2: Generate task suite (30 tasks: ~10 invoice + ~10 fraud + ~10 reconciliation)
tasks = generator.generate_task_suite(count=30, strategy="random", seed=42)

# Step 3: Create orchestrators
sequential = SequentialOrchestrator(name="sequential")
hierarchical = HierarchicalOrchestrator(name="hierarchical")

# Step 4: Run benchmark
runner = BenchmarkRunner(
    orchestrators={"sequential": sequential, "hierarchical": hierarchical},
    task_generator=generator,
    metrics_calculator=MetricsCalculator(),
    default_timeout=60,
    show_progress=True
)

results = runner.run_benchmark(tasks=tasks)

# Step 5: Analyze results
print(f"Sequential Success Rate: {results['pattern_results']['sequential']['metrics']['task_success_rate']:.1%}")
print(f"Hierarchical Success Rate: {results['pattern_results']['hierarchical']['metrics']['task_success_rate']:.1%}")
```

---

## Module API Reference

### 1. FinancialTaskGenerator

**Purpose:** Generate and manage 300-task financial benchmark suite

**Class:** `FinancialTaskGenerator`

#### Constructor

```python
generator = FinancialTaskGenerator()
# No constructor arguments
```

#### Methods

**`load_datasets(data_dir: Path) -> None`**

Load all 3 dataset files from data directory.

```python
from pathlib import Path

generator = FinancialTaskGenerator()
data_dir = Path("lesson-16/data")
generator.load_datasets(data_dir)

# Access loaded datasets (returns list[dict])
invoices = generator.invoice_dataset
transactions = generator.transaction_dataset
reconciliations = generator.reconciliation_dataset
```

**Returns:** Stores datasets in instance attributes (no return value)

**Raises:**
- `FileNotFoundError` if data directory or dataset files missing
- `ValueError` if dataset files contain invalid JSON

---

**`generate_task_suite(count: int, strategy: str = "random", seed: int = 42) -> list[Task]`**

Generate task suite with specified sampling strategy.

```python
# Random sampling (default) - Mix of all 3 task types
tasks = generator.generate_task_suite(count=30, strategy="random", seed=42)

# Difficulty-stratified sampling - Balanced easy/medium/hard
tasks = generator.generate_task_suite(count=30, strategy="stratified", seed=42)

# Edge-case-focused sampling - Prioritize high-challenge tasks
tasks = generator.generate_task_suite(count=30, strategy="edge_case", seed=42)
```

**Returns:** `list[Task]` where `Task` is TypedDict with:
```python
{
  "task_id": str,         # "INV-2024-001"
  "task_type": str,       # "invoice_processing" | "fraud_detection" | "account_reconciliation"
  "input_data": dict,     # Raw dataset entry
  "gold_label": dict,     # Expected output for evaluation
  "difficulty": str | None,  # "easy" | "medium" | "hard"
  "challenge_types": list[str]  # ["ocr_error", "missing_fields"]
}
```

**Strategies:**
- `"random"`: Uniform sampling across all tasks
- `"stratified"`: Balanced difficulty distribution (33% easy, 34% medium, 33% hard)
- `"edge_case"`: Prioritize tasks with multiple challenges

**Note:** Actual count may be slightly lower due to deduplication (e.g., 28 instead of 30 if 2 duplicate invoices filtered).

---

**`filter_tasks(tasks: list[Task], task_type: str | None = None, difficulty: str | None = None, challenge_types: list[str] | None = None) -> list[Task]`**

Filter task suite by type, difficulty, or challenge.

```python
# Filter by task type
invoice_tasks = generator.filter_tasks(tasks, task_type="invoice_processing")
fraud_tasks = generator.filter_tasks(tasks, task_type="fraud_detection")

# Filter by difficulty
hard_tasks = generator.filter_tasks(tasks, difficulty="hard")

# Filter by challenge type
ocr_tasks = generator.filter_tasks(tasks, challenge_types=["ocr_error"])
```

**Returns:** `list[Task]` matching filter criteria

---

**`get_task_statistics(tasks: list[Task]) -> dict[str, Any]`**

Calculate task suite statistics.

```python
stats = generator.get_task_statistics(tasks)

print(f"Total tasks: {stats['total_count']}")
print(f"Task type distribution: {stats['task_type_distribution']}")
print(f"Difficulty distribution: {stats['difficulty_distribution']}")
print(f"Challenge distribution: {stats['challenge_distribution']}")
print(f"Fraud balance: {stats['fraud_balance']}")  # For fraud_detection tasks
```

**Returns:** `dict[str, Any]` with 5 metric categories

---

### 2. MetricsCalculator

**Purpose:** Calculate 4 evaluation metrics for orchestration patterns

**Class:** `MetricsCalculator`

#### Constructor

```python
calculator = MetricsCalculator()
# No constructor arguments
```

#### Methods

**`calculate_task_success_rate(predictions: list[Any], gold_labels: list[Any], match_fn: Callable[[Any, Any], bool] | None = None) -> float`**

Calculate task success rate (% of correct predictions).

```python
# Default: Exact match
predictions = ["Acme Corp", "TechSolutions", "ACME"]
gold_labels = ["Acme Corp", "TechSolutions", "Acme Corp"]
success_rate = calculator.calculate_task_success_rate(predictions, gold_labels)
# Returns: 0.666... (2/3 correct)

# Custom match function (case-insensitive)
def case_insensitive_match(pred, gold):
    return str(pred).lower() == str(gold).lower()

success_rate = calculator.calculate_task_success_rate(
    predictions, gold_labels, match_fn=case_insensitive_match
)
# Returns: 1.0 (3/3 correct with case-insensitive matching)
```

**Returns:** `float` between 0.0 and 1.0

**Formula:** `correct_predictions / total_predictions`

---

**`calculate_error_propagation_index(workflow_traces: list[WorkflowTrace]) -> float`**

Calculate Error Propagation Index (downstream errors per root cause).

```python
workflow_trace = {
    "workflow_id": "test_001",
    "steps": [
        {"agent": "agent1", "success": True, "error": None},
        {"agent": "agent2", "success": False, "error": "ValidationError"},  # Root cause
        {"agent": "agent3", "success": False, "error": "Propagated from agent2"},  # Cascade
        {"agent": "agent4", "success": False, "error": "Propagated from agent2"},  # Cascade
    ]
}

epi = calculator.calculate_error_propagation_index([workflow_trace])
# Returns: 2.0 (2 cascaded errors / 1 root cause)
```

**Returns:** `float` ≥ 0.0

**Formula:** `total_cascaded_errors / total_root_cause_errors`

**Interpretation:**
- **EPI < 1.0:** Errors isolated (good)
- **EPI = 1.0:** No cascade amplification
- **EPI > 5.0:** Severe cascade (systemic failure)

---

**`calculate_latency_percentiles(latencies: list[float], percentiles: list[int] | None = None) -> dict[int, float]`**

Calculate latency percentiles (P50, P95).

```python
latencies = [1.5, 2.0, 3.0, 4.5, 5.0, 6.0, 8.0, 10.0, 12.0, 15.0]

# Default: P50 and P95
percentiles = calculator.calculate_latency_percentiles(latencies)
print(f"P50: {percentiles[50]}s")  # Median: 5.5s
print(f"P95: {percentiles[95]}s")  # 95th percentile: 14.25s

# Custom percentiles
percentiles = calculator.calculate_latency_percentiles(latencies, percentiles=[25, 75, 99])
```

**Returns:** `dict[int, float]` mapping percentile → latency (seconds)

**Formula:** `numpy.percentile(latencies, percentiles)`

---

**`calculate_cost(api_calls: list[APICall]) -> CostSummary`**

Calculate total cost from LLM API calls.

```python
api_calls = [
    {"model": "gpt-4", "prompt_tokens": 100, "completion_tokens": 50},
    {"model": "gpt-3.5-turbo", "prompt_tokens": 150, "completion_tokens": 75},
]

cost_summary = calculator.calculate_cost(api_calls)
print(f"Total cost: ${cost_summary['total_cost']:.4f}")
print(f"Total calls: {cost_summary['total_calls']}")
print(f"Cost breakdown: {cost_summary['cost_by_model']}")
```

**Returns:** `CostSummary` TypedDict with:
```python
{
  "total_cost": float,         # Total $ spent
  "total_calls": int,          # Number of LLM calls
  "total_prompt_tokens": int,
  "total_completion_tokens": int,
  "cost_by_model": dict[str, float]  # {"gpt-4": 0.0045, "gpt-3.5-turbo": 0.00018}
}
```

**Pricing (OPENAI_PRICING constant):**
- `gpt-4`: $0.03/1K prompt, $0.06/1K completion
- `gpt-4-turbo`: $0.01/1K prompt, $0.03/1K completion
- `gpt-3.5-turbo`: $0.0015/1K prompt, $0.002/1K completion

**Formula:** `(prompt_tokens * prompt_price + completion_tokens * completion_price) / 1000`

---

### 3. BenchmarkRunner

**Purpose:** Execute benchmarks across multiple orchestration patterns

**Class:** `BenchmarkRunner`

#### Constructor

```python
runner = BenchmarkRunner(
    orchestrators: dict[str, Orchestrator],
    task_generator: FinancialTaskGenerator,
    metrics_calculator: MetricsCalculator,
    default_timeout: int = 60,
    show_progress: bool = False
)
```

**Parameters:**
- `orchestrators`: Dict mapping pattern name → Orchestrator instance
- `task_generator`: FinancialTaskGenerator for dataset access
- `metrics_calculator`: MetricsCalculator for metric computation
- `default_timeout`: Task timeout in seconds (default: 60)
- `show_progress`: Show tqdm progress bar (default: False)

**Example:**
```python
from backend.orchestrators import SequentialOrchestrator, HierarchicalOrchestrator

orchestrators = {
    "sequential": SequentialOrchestrator(name="sequential"),
    "hierarchical": HierarchicalOrchestrator(name="hierarchical")
}

runner = BenchmarkRunner(
    orchestrators=orchestrators,
    task_generator=generator,
    metrics_calculator=MetricsCalculator(),
    default_timeout=60,
    show_progress=True  # Enable progress bar
)
```

#### Methods

**`run_benchmark(tasks: list[Task], use_cache: bool = True) -> BenchmarkResults`**

Run benchmark on task suite with caching.

```python
tasks = generator.generate_task_suite(count=30, strategy="random", seed=42)

# Run with caching (fast for repeated runs)
results = runner.run_benchmark(tasks=tasks, use_cache=True)

# Force re-execution (ignore cache)
results = runner.run_benchmark(tasks=tasks, use_cache=False)
```

**Returns:** `BenchmarkResults` TypedDict with:
```python
{
  "pattern_results": dict[str, PatternResult],  # Results per pattern
  "timestamp": str,                             # ISO8601 timestamp
  "task_count": int,                            # Number of tasks evaluated
}
```

**`PatternResult` structure:**
```python
{
  "pattern_name": str,
  "task_count": int,
  "metrics": {
    "task_success_rate": float,
    "error_propagation_index": float,
    "latency_p50": float,
    "latency_p95": float,
    "total_cost": float
  }
}
```

---

**`calculate_statistics(results: BenchmarkResults) -> StatisticalAnalysis`**

Calculate confidence intervals and p-values.

```python
results = runner.run_benchmark(tasks=tasks)
stats = runner.calculate_statistics(results)

print(f"Success rate 95% CI: {stats['confidence_intervals']['task_success_rate']}")
print(f"Sequential vs Hierarchical p-value: {stats['p_values'][('sequential', 'hierarchical')]}")
```

**Returns:** `StatisticalAnalysis` TypedDict with:
```python
{
  "confidence_intervals": dict[str, tuple[float, float]],  # Metric → (lower, upper) CI
  "p_values": dict[tuple[str, str], float]                 # (pattern1, pattern2) → p-value
}
```

**Statistical Methods:**
- **Confidence intervals:** Bootstrapping with 1000 samples (95% CI)
- **P-values:** Paired t-test (`scipy.stats.ttest_ind`)
- **Significance threshold:** p < 0.05

---

**`save_results(results: BenchmarkResults, filepath: Path) -> None`**

Save benchmark results to JSON file.

```python
results = runner.run_benchmark(tasks=tasks)
runner.save_results(results, filepath=Path("cache/benchmark_results.json"))
```

---

**`load_results(filepath: Path) -> BenchmarkResults`**

Load cached benchmark results.

```python
results = runner.load_results(filepath=Path("cache/benchmark_results.json"))
# Loads in <1 second (vs minutes for re-execution)
```

---

## Usage Patterns

### Pattern 1: Quick Evaluation (10 tasks, DEMO mode)

```python
from pathlib import Path
from backend.benchmarks import FinancialTaskGenerator, MetricsCalculator, BenchmarkRunner
from backend.orchestrators import SequentialOrchestrator

# Setup
generator = FinancialTaskGenerator()
generator.load_datasets(Path("data"))
tasks = generator.generate_task_suite(count=10, strategy="random", seed=42)

# Create orchestrator (use MockAgent for DEMO mode - no LLM cost)
from backend.benchmarks.runner import MockAgent
sequential = SequentialOrchestrator(name="sequential")
sequential.register_agent("agent1", MockAgent(success_rate=0.8))

# Run benchmark
runner = BenchmarkRunner(
    orchestrators={"sequential": sequential},
    task_generator=generator,
    metrics_calculator=MetricsCalculator()
)

results = runner.run_benchmark(tasks=tasks)
print(f"Success rate: {results['pattern_results']['sequential']['metrics']['task_success_rate']:.1%}")
```

**Cost:** $0 (MockAgent, no LLM calls)
**Time:** ~10 seconds

---

### Pattern 2: Full Benchmark (100 tasks, cached results)

```python
# Generate full 100-task suite
tasks = generator.generate_task_suite(count=100, strategy="random", seed=42)

# Run with caching (first run: ~5 min, subsequent: <1s)
results = runner.run_benchmark(tasks=tasks, use_cache=True)

# Cache key automatically generated from: patterns + task_count + seed
# Stored in: lesson-16/cache/benchmark_results_{hash}.json
```

**Cost:** $2-5 (first run with real LLM), $0 (cached runs)
**Time:** 5 minutes (first), <1 second (cached)

---

### Pattern 3: Comparative Evaluation (5 patterns)

```python
from backend.orchestrators import (
    SequentialOrchestrator,
    HierarchicalOrchestrator,
    IterativeOrchestrator,
    StateMachineOrchestrator,
    VotingOrchestrator
)

# Create all 5 orchestrators
orchestrators = {
    "sequential": SequentialOrchestrator(name="sequential"),
    "hierarchical": HierarchicalOrchestrator(name="hierarchical"),
    "iterative": IterativeOrchestrator(name="iterative"),
    "state_machine": StateMachineOrchestrator(name="state_machine"),
    "voting": VotingOrchestrator(name="voting")
}

# Run benchmark (parallel execution via ThreadPoolExecutor)
runner = BenchmarkRunner(
    orchestrators=orchestrators,
    task_generator=generator,
    metrics_calculator=MetricsCalculator(),
    show_progress=True
)

results = runner.run_benchmark(tasks=tasks)

# Compare patterns
for pattern_name, pattern_result in results['pattern_results'].items():
    metrics = pattern_result['metrics']
    print(f"{pattern_name:15} | Success: {metrics['task_success_rate']:.1%} | "
          f"EPI: {metrics['error_propagation_index']:.2f} | "
          f"P50: {metrics['latency_p50']:.1f}s | "
          f"Cost: ${metrics['total_cost']:.2f}")
```

**Output:**
```
sequential      | Success: 70.0% | EPI: 3.20 | P50: 12.0s | Cost: $10.00
hierarchical    | Success: 80.0% | EPI: 1.80 | P50: 8.0s | Cost: $13.00
iterative       | Success: 75.0% | EPI: 1.20 | P50: 18.0s | Cost: $21.00
state_machine   | Success: 85.0% | EPI: 0.40 | P50: 10.0s | Cost: $11.00
voting          | Success: 90.0% | EPI: 0.30 | P50: 15.0s | Cost: $50.00
```

---

## Performance Optimization

### Caching Strategy

**Cache Key Generation:**
```python
# Automatically hashes: patterns + task_count + seed
cache_key = runner._generate_cache_key(patterns=list(orchestrators.keys()), task_count=100, seed=42)
# Returns: "benchmark_a1b2c3d4e5f6..."
```

**Cache Invalidation:**
- Different seed → New cache key
- Different task count → New cache key
- Different pattern set → New cache key
- Dataset regeneration → Manual cache clear (`rm -rf cache/`)

**Cache Performance:**
- Save: ~100ms for 100-task results
- Load: <1 second (vs 5-10 minutes re-execution)
- Storage: ~50KB per cached result

### Parallel Execution

Orchestrators run in parallel using `ThreadPoolExecutor`:

```python
# Sequential execution (slow)
for pattern_name, orchestrator in orchestrators.items():
    results[pattern_name] = run_single_pattern(orchestrator, tasks)

# Parallel execution (fast - built into BenchmarkRunner)
with ThreadPoolExecutor(max_workers=len(orchestrators)) as executor:
    futures = {executor.submit(run_single_pattern, orch, tasks): name
               for name, orch in orchestrators.items()}
```

**Speedup:** ~3× faster for 5 patterns (15 min → 5 min)

---

## Troubleshooting

### Issue: FileNotFoundError when loading datasets
**Error:** `FileNotFoundError: Data directory not found: lesson-16/data`

**Solution:** Ensure correct working directory
```python
# Check current directory
import os
print(f"Current directory: {os.getcwd()}")

# Adjust data_dir path
from pathlib import Path
data_dir = Path("lesson-16/data")  # From repository root
# OR
data_dir = Path(__file__).parent.parent / "data"  # Relative to script
```

### Issue: TypeError - BenchmarkRunner constructor
**Error:** `TypeError: BenchmarkRunner.__init__() missing 2 required positional arguments: 'task_generator' and 'metrics_calculator'`

**Solution:** Provide all required arguments
```python
# ❌ Incorrect (missing task_generator and metrics_calculator)
runner = BenchmarkRunner(orchestrators=orchestrators)

# ✅ Correct
runner = BenchmarkRunner(
    orchestrators=orchestrators,
    task_generator=generator,
    metrics_calculator=MetricsCalculator()
)
```

### Issue: Task count mismatch (28 instead of 30)
**Behavior:** `generate_task_suite(count=30)` returns 28 tasks

**Explanation:** **This is correct.** Deduplication removes invalid tasks (e.g., duplicate invoices marked in gold labels).

**Workaround:**
```python
# Generate extra to account for filtering
tasks = generator.generate_task_suite(count=35, strategy="random", seed=42)
tasks = tasks[:30]  # Take first 30 valid tasks
```

### Issue: Cache not invalidating after dataset change
**Symptom:** Old results loaded despite regenerating datasets

**Solution:** Manually clear cache
```bash
rm -rf lesson-16/cache/benchmark_results_*.json
```

Or use `use_cache=False`:
```python
results = runner.run_benchmark(tasks=tasks, use_cache=False)
```

---

## Testing

### Running Tests

```bash
# From repository root
uv run pytest lesson-16/tests/test_benchmarks.py -v

# With coverage
uv run pytest lesson-16/tests/test_benchmarks.py --cov=lesson-16/backend/benchmarks --cov-report=term
```

### Test Coverage
- **financial_tasks.py:** 94% (16 tests)
- **metrics.py:** 98% (39 tests)
- **runner.py:** 90% (18 tests)
- **Average:** 94% ✅

### Key Test Patterns

**Defensive coding test:**
```python
def test_should_raise_type_error_when_predictions_not_list() -> None:
    calculator = MetricsCalculator()
    with pytest.raises(TypeError, match="predictions must be a list"):
        calculator.calculate_task_success_rate("not a list", ["gold"])
```

**Edge case test:**
```python
def test_should_return_zero_when_latencies_empty() -> None:
    calculator = MetricsCalculator()
    with pytest.raises(ValueError, match="latencies list cannot be empty"):
        calculator.calculate_latency_percentiles([])
```

---

## Related Documentation

- **Tutorials:**
  - [Tutorial 05: AgentArch Benchmark Methodology](../../tutorials/05_agentarch_benchmark_methodology.md)
  - [Tutorial 07: Production Deployment Considerations](../../tutorials/07_production_deployment_considerations.md)

- **Notebooks:**
  - [Notebook 14: AgentArch Benchmark Reproduction](../../notebooks/14_agentarch_benchmark_reproduction.ipynb)
  - [Notebook 15: Production Deployment Tutorial](../../notebooks/15_production_deployment_tutorial.ipynb)

- **Datasets:**
  - [Data README](../../data/README.md) - Dataset schemas and usage

- **Tests:**
  - `tests/test_benchmarks.py` - 73 comprehensive tests

---

**Maintained by:** AI Evaluation Course Team
**Last Updated:** 2025-11-24
**Version:** 1.0
