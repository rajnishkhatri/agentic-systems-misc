# ThreadPoolExecutor Parallel Pattern

**Pattern Type:** Concurrency
**Complexity:** ⭐⭐⭐ (High)
**Source:** Lesson 12 - Hybrid Retrieval & Context Quality
**Created:** 2025-11-12
**File References:** `backend/query_rewrite_agent.py:187-208`

---

## Overview

**ThreadPoolExecutor** is Python's built-in concurrency pattern for executing multiple I/O-bound tasks in parallel using threads. This pattern is essential for batch processing operations where tasks are independent and spend most of their time waiting (API calls, database queries, file I/O).

**Key Benefits:**
- **Speed**: Process N tasks in parallel instead of sequentially (up to N× faster for I/O-bound work)
- **Order preservation**: Use `future_to_index` mapping to maintain result order
- **Progress tracking**: Integrate with `tqdm` for real-time progress bars
- **Error isolation**: Individual task failures don't crash the entire batch
- **Simple API**: Built into Python stdlib, no external dependencies

**Real-world impact:** In Lesson 12, this pattern reduced query rewriting time from ~300s (sequential) to ~30s (10 parallel workers) for 100 queries.

---

## When to Use

✅ **Use ThreadPoolExecutor when:**
- **Batch processing**: Processing multiple independent items (API calls, file operations)
- **I/O-bound tasks**: Operations that wait on external resources (LLM APIs, databases, web scraping)
- **Order matters**: You need results in the same order as inputs
- **Progress tracking**: Users need to see real-time progress for long-running batches
- **Failure tolerance**: Some tasks can fail without stopping the entire batch

❌ **DON'T use ThreadPoolExecutor when:**
- **CPU-bound tasks**: Use `ProcessPoolExecutor` instead (GIL prevents true parallelism with threads)
- **Shared state**: Tasks need to modify shared data structures (risk of race conditions)
- **Sequential dependencies**: Task N depends on result of Task N-1 (use async/await or serial processing)
- **Single task**: No need for concurrency overhead
- **Memory constraints**: Each thread consumes memory; 1000 threads = potential OOM

---

## Core Concepts

### 1. `future_to_index` Mapping Pattern

**Problem:** `executor.submit()` returns futures in arbitrary order, but you need results in input order.

**Solution:** Map each future to its original index.

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

queries = ["query1", "query2", "query3"]

with ThreadPoolExecutor(max_workers=3) as executor:
    # Submit all tasks and map future → index
    future_to_index = {
        executor.submit(process_query, query): i
        for i, query in enumerate(queries)
    }

    # Collect results in order
    results = [None] * len(queries)
    for future in as_completed(future_to_index):
        index = future_to_index[future]
        results[index] = future.result()

    # results[0] corresponds to queries[0], etc.
```

### 2. Exception Handling in Thread Workers

**Problem:** Exceptions in worker threads are silent until you call `future.result()`.

**Solution:** Wrap `future.result()` in try/except and provide fallback values.

```python
for future in as_completed(future_to_index):
    index = future_to_index[future]
    try:
        result = future.result()
        results[index] = result
    except Exception as e:
        print(f"Error processing item {index}: {e}")
        # Fallback: keep original input or None
        results[index] = None
```

### 3. Progress Bar Integration with `tqdm`

**Problem:** Long-running batch jobs feel unresponsive without progress feedback.

**Solution:** Wrap `as_completed()` with `tqdm` for live progress updates.

```python
from tqdm import tqdm

for future in tqdm(as_completed(future_to_index), total=len(queries), desc="Processing"):
    index = future_to_index[future]
    results[index] = future.result()
```

---

## Code Template: ThreadPoolExecutor with Order Preservation

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Callable, List

from tqdm import tqdm


def batch_process_parallel(
    items: List[Any],
    process_fn: Callable[[Any], Any],
    max_workers: int = 5,
    desc: str = "Processing"
) -> List[Any]:
    """Process items in parallel using ThreadPoolExecutor.

    Args:
        items: List of items to process
        process_fn: Function to apply to each item
        max_workers: Number of parallel threads (default: 5)
        desc: Progress bar description

    Returns:
        List of results in same order as input items

    Raises:
        TypeError: If items is not a list
        ValueError: If max_workers < 1
    """
    # Step 1: Type checking
    if not isinstance(items, list):
        raise TypeError("items must be a list")
    if not isinstance(max_workers, int) or max_workers < 1:
        raise ValueError("max_workers must be a positive integer")

    # Step 2: Edge case - empty input
    if not items:
        return []

    # Step 3: Initialize result list (preserves order)
    results = [None] * len(items)

    # Step 4: Parallel processing with ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks with index mapping
        future_to_index = {
            executor.submit(process_fn, item): i
            for i, item in enumerate(items)
        }

        # Collect results with progress bar
        for future in tqdm(as_completed(future_to_index), total=len(items), desc=desc):
            index = future_to_index[future]
            try:
                result = future.result()
                results[index] = result
            except Exception as e:
                print(f"Error processing item {index}: {e}")
                # Fallback: keep None or original item
                results[index] = None

    # Step 5: Return results in input order
    return results


# Example usage
def process_query(query: str) -> dict:
    """Process a single query (simulates API call)."""
    import time
    time.sleep(0.1)  # Simulate I/O wait
    return {"query": query, "result": f"processed_{query}"}


queries = ["q1", "q2", "q3", "q4", "q5"]
results = batch_process_parallel(queries, process_query, max_workers=3)
# results[0] corresponds to queries[0], etc.
```

---

## Real Example from Codebase

**Source:** `backend/query_rewrite_agent.py:187-208`

```python
def batch_process_queries(self, queries: List[str], strategy: str = "conciseness") -> List[Dict[str, str]]:
    """Process multiple queries in parallel with order preservation.

    Args:
        queries: List of input queries
        strategy: Rewrite strategy ("conciseness", "specificity", "stepback")

    Returns:
        List of results in same order as input queries
    """
    results = [None] * len(queries)

    with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
        # Submit all tasks
        future_to_index = {
            executor.submit(self._process_query_with_retry, query, strategy): i
            for i, query in enumerate(queries)
        }

        # Collect results with progress bar
        for future in tqdm(as_completed(future_to_index), total=len(queries), desc=f"Processing {strategy}"):
            index = future_to_index[future]
            try:
                result = future.result()
                results[index] = result
            except Exception as e:
                print(f"Error processing query {index}: {e}")
                # Fallback result
                results[index] = {
                    "original_query": queries[index],
                    "processed_query": queries[index],
                    "strategy": strategy
                }

    return results
```

**Why this implementation is excellent:**
1. **Order preservation**: `future_to_index` maps futures to original indices
2. **Progress feedback**: `tqdm` shows real-time progress with descriptive label
3. **Error handling**: Try/except catches individual failures without crashing batch
4. **Graceful degradation**: Failed queries return original query as fallback
5. **Configurable parallelism**: `self.max_workers` allows tuning based on API rate limits

---

## Trade-offs and Performance Considerations

### 1. Choosing `max_workers`

**Rule of thumb:**
- **I/O-bound tasks**: `max_workers = 5-20` (depends on API rate limits)
- **CPU-bound tasks**: Use `ProcessPoolExecutor` with `max_workers = cpu_count()`
- **API rate limits**: Never exceed provider limits (e.g., OpenAI: 3,500 RPM → max_workers ≈ 10)

```python
import os
from multiprocessing import cpu_count

# For I/O-bound tasks (API calls)
max_workers = int(os.getenv("MAX_WORKERS", 10))

# For CPU-bound tasks (use ProcessPoolExecutor instead)
max_workers = cpu_count()
```

### 2. Memory Usage

**Problem:** Each thread holds its own stack and local variables. 1000 threads = significant memory overhead.

**Solution:** Limit `max_workers` and process in batches if needed.

```python
def batch_process_large_dataset(items: List[Any], process_fn: Callable, batch_size: int = 100):
    """Process large dataset in batches to limit memory usage."""
    all_results = []
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        results = batch_process_parallel(batch, process_fn, max_workers=10)
        all_results.extend(results)
    return all_results
```

### 3. Python GIL Limitations

**Python's Global Interpreter Lock (GIL)** prevents true parallelism for CPU-bound tasks in threads.

**Impact:**
- ✅ **I/O-bound tasks**: Full speedup (threads can run while waiting for I/O)
- ❌ **CPU-bound tasks**: No speedup (GIL serializes execution)

**Solution for CPU-bound tasks:** Use `ProcessPoolExecutor` instead.

```python
from concurrent.futures import ProcessPoolExecutor

# CPU-bound task (e.g., image processing, heavy computation)
with ProcessPoolExecutor(max_workers=cpu_count()) as executor:
    results = list(executor.map(cpu_intensive_function, items))
```

---

## Common Pitfalls

### ❌ Pitfall 1: Not Preserving Order

```python
# BAD: Results in arbitrary order
results = []
with ThreadPoolExecutor(max_workers=5) as executor:
    futures = [executor.submit(process, item) for item in items]
    for future in as_completed(futures):
        results.append(future.result())
# results[0] might correspond to items[4]!
```

**Fix:** Use `future_to_index` mapping.

### ❌ Pitfall 2: Ignoring Exceptions

```python
# BAD: Silent failures
for future in as_completed(future_to_index):
    index = future_to_index[future]
    results[index] = future.result()  # Raises exception, crashes loop
```

**Fix:** Wrap in try/except with fallback.

### ❌ Pitfall 3: Blocking Main Thread

```python
# BAD: Blocks until all tasks complete before showing any results
with ThreadPoolExecutor(max_workers=5) as executor:
    futures = [executor.submit(process, item) for item in items]
    results = [f.result() for f in futures]  # Blocks in order
```

**Fix:** Use `as_completed()` to process results as they finish.

### ❌ Pitfall 4: Unbounded Parallelism

```python
# BAD: Creates 10,000 threads (kills performance)
with ThreadPoolExecutor(max_workers=10000) as executor:
    futures = [executor.submit(process, item) for item in huge_list]
```

**Fix:** Limit `max_workers` to reasonable value (5-20 for I/O tasks).

### ❌ Pitfall 5: Shared State Without Locks

```python
# BAD: Race condition (counter increments get lost)
counter = 0

def increment():
    global counter
    counter += 1

with ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(increment) for _ in range(100)]
    for f in as_completed(futures):
        f.result()
# counter != 100 (race condition)
```

**Fix:** Use thread-safe data structures or locks.

```python
from threading import Lock

counter = 0
lock = Lock()

def increment():
    global counter
    with lock:
        counter += 1
```

---

## Integration with Defensive Coding

**Defensive ThreadPoolExecutor Pattern:**

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Callable, List

from tqdm import tqdm


def batch_process_defensive(
    items: List[Any],
    process_fn: Callable[[Any], Any],
    max_workers: int = 5,
    desc: str = "Processing",
    fallback_fn: Callable[[Any, Exception], Any] = None
) -> List[Any]:
    """Defensively process items in parallel.

    Args:
        items: Items to process
        process_fn: Processing function
        max_workers: Number of threads
        desc: Progress description
        fallback_fn: Called on errors with (item, exception)

    Returns:
        List of results in input order

    Raises:
        TypeError: If items not a list or max_workers not int
        ValueError: If max_workers < 1
    """
    # Step 1: Type checking
    if not isinstance(items, list):
        raise TypeError("items must be a list")
    if not isinstance(max_workers, int):
        raise TypeError("max_workers must be an integer")

    # Step 2: Input validation
    if max_workers < 1:
        raise ValueError("max_workers must be positive")
    if max_workers > 50:
        import warnings
        warnings.warn("max_workers > 50 may cause performance issues")

    # Step 3: Edge case handling
    if not items:
        return []

    # Step 4: Main logic
    results = [None] * len(items)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_index = {
            executor.submit(process_fn, item): i
            for i, item in enumerate(items)
        }

        for future in tqdm(as_completed(future_to_index), total=len(items), desc=desc):
            index = future_to_index[future]
            try:
                result = future.result(timeout=60)  # Timeout for hung tasks
                results[index] = result
            except Exception as e:
                if fallback_fn:
                    results[index] = fallback_fn(items[index], e)
                else:
                    print(f"Error processing item {index}: {e}")
                    results[index] = None

    # Step 5: Return
    return results
```

---

## Performance Benchmarks (Real Project Data)

**Task:** Rewrite 100 queries using LLM API (OpenAI GPT-4)

| Approach | Time | Speedup |
|----------|------|---------|
| Sequential (no parallelism) | ~300s | 1× |
| ThreadPoolExecutor (max_workers=5) | ~60s | 5× |
| ThreadPoolExecutor (max_workers=10) | ~30s | 10× |
| ThreadPoolExecutor (max_workers=20) | ~32s | 9.4× |

**Observations:**
- Optimal `max_workers=10` for OpenAI API (rate limit consideration)
- Diminishing returns beyond 10 workers (API rate limits become bottleneck)
- Memory usage: ~500MB (10 workers) vs ~150MB (sequential)

---

## Summary Checklist

**When implementing ThreadPoolExecutor:**
- [ ] Use `future_to_index` mapping to preserve result order
- [ ] Wrap `future.result()` in try/except for error handling
- [ ] Provide fallback values for failed tasks
- [ ] Integrate `tqdm` for progress tracking
- [ ] Choose appropriate `max_workers` (5-20 for I/O tasks)
- [ ] Consider memory usage for large batches
- [ ] Use `ProcessPoolExecutor` for CPU-bound tasks
- [ ] Avoid shared state or use locks
- [ ] Set timeouts for `future.result()` to prevent hangs
- [ ] Add defensive validation (type checking, input validation)

---

## Related Patterns

- **TDD Workflow** (`patterns/tdd-workflow.md`) - Test parallel code carefully; use mocks for deterministic tests
- **Defensive Function Template** (`CLAUDE.md`) - Apply 5-step pattern to batch processing functions
- **Abstract Base Class** (`patterns/abstract-base-class.md`) - Create base class for different processing strategies

---

## Further Reading

- Python `concurrent.futures` documentation: https://docs.python.org/3/library/concurrent.futures.html
- Real-world example: `backend/query_rewrite_agent.py:187-208`
- Testing parallel code: `tests/test_generate_test_queries.py` (uses mocks for determinism)
- When to use threads vs processes: https://realpython.com/python-concurrency/
