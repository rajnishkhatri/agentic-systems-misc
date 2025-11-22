# Pattern Decision Tree

**Purpose:** Quick reference guide for selecting the right pattern based on your use case

**Last Updated:** 2025-11-18

---

## Decision Flowchart

```
START: What are you trying to do?
│
├─ "I need to write tests or build a new feature"
│  └─→ Use: TDD Workflow Pattern
│      Complexity: ⭐⭐ (Medium)
│      File: patterns/tdd-workflow.md
│      Why: Ensures code quality through test-first development
│
├─ "I need to process multiple items in parallel (API calls, file I/O, database queries)"
│  │
│  ├─ Are tasks I/O-bound (waiting on external resources)?
│  │  ├─ YES → Use: ThreadPoolExecutor Parallel Pattern
│  │  │         Complexity: ⭐⭐⭐ (High)
│  │  │         File: patterns/threadpool-parallel.md
│  │  │         Why: Efficient parallel I/O with order preservation
│  │  │
│  │  └─ NO (CPU-bound) → Use: ProcessPoolExecutor (not yet documented)
│  │                      Why: True parallelism for CPU tasks
│  │
│  └─ Do tasks have sequential dependencies (Task N needs output of Task N-1)?
│     └─ YES → DON'T use parallel patterns
│               Why: Sequential dependencies require serial execution
│
├─ "I need multiple implementations of the same interface (judges, agents, strategies)"
│  └─→ Use: Abstract Base Class Pattern
│      Complexity: ⭐⭐⭐ (High)
│      File: patterns/abstract-base-class.md
│      Why: Enforces interface contracts, enables polymorphism
│
├─ "I need to refactor existing code"
│  └─→ Use: TDD Workflow Pattern (REFACTOR phase)
│      Complexity: ⭐⭐ (Medium)
│      File: patterns/tdd-workflow.md
│      Why: Ensures refactoring doesn't break existing behavior
│
└─ "I'm exploring a new library or prototyping"
   └─→ DON'T use patterns yet
       Why: Patterns add structure; exploration needs flexibility
       Next step: Once prototype works, apply TDD to productionize
```

---

## Quick Lookup Table

| Your Goal | Pattern to Use | Complexity | Key Benefit |
|-----------|---------------|-----------|-------------|
| Write tests for new feature | TDD Workflow | ⭐⭐ | Test-first development |
| Build new feature | TDD Workflow | ⭐⭐ | Quality through tests |
| Fix bug | TDD Workflow | ⭐⭐ | Regression prevention |
| Refactor code | TDD Workflow | ⭐⭐ | Safety net during changes |
| Batch API calls | ThreadPoolExecutor Parallel | ⭐⭐⭐ | 10× speedup for I/O |
| Parallel file processing | ThreadPoolExecutor Parallel | ⭐⭐⭐ | Order preservation |
| Concurrent database queries | ThreadPoolExecutor Parallel | ⭐⭐⭐ | Exception handling |
| Multiple judge implementations | Abstract Base Class | ⭐⭐⭐ | Interface enforcement |
| Plugin system | Abstract Base Class | ⭐⭐⭐ | Polymorphic behavior |
| Framework with shared logic | Abstract Base Class | ⭐⭐⭐ | Code reuse |

---

## Use Case → Pattern Mapping

### Testing & Development

**Use Case:** "I want to add a query classification feature"
- **Pattern:** TDD Workflow
- **Why:** Build features test-first for quality
- **Steps:**
  1. RED: Write failing test for classifier
  2. GREEN: Implement minimal classifier
  3. REFACTOR: Add defensive coding, improve logic

**Use Case:** "This function has a bug - it crashes on empty input"
- **Pattern:** TDD Workflow
- **Why:** Write test that reproduces bug, then fix
- **Steps:**
  1. RED: Write test that triggers the bug
  2. GREEN: Fix bug to make test pass
  3. REFACTOR: Add validation for edge cases

---

### Concurrency & Batch Processing

**Use Case:** "I need to call OpenAI API for 100 queries"
- **Pattern:** ThreadPoolExecutor Parallel
- **Why:** I/O-bound task, API calls spend time waiting
- **Key concepts:**
  - `max_workers=10` (respect rate limits)
  - `future_to_index` for order preservation
  - Exception handling per query (don't crash batch)
  - `tqdm` progress bar

**Use Case:** "I need to read 500 JSON files and process them"
- **Pattern:** ThreadPoolExecutor Parallel
- **Why:** I/O-bound file reading, can parallelize
- **Key concepts:**
  - `max_workers=20` (I/O can handle more threads)
  - Process results in original file order
  - Handle missing/corrupted files gracefully

**Use Case:** "I need to calculate embeddings for 1000 texts"
- **Pattern:** Depends on embedding source
- **Decision tree:**
  - API-based (OpenAI)? → ThreadPoolExecutor (I/O-bound)
  - Local model (sentence-transformers)? → Consider batch processing instead
  - GPU acceleration? → Use model's built-in batching

**DON'T use ThreadPoolExecutor when:**
- ❌ Tasks are CPU-bound (use ProcessPoolExecutor)
- ❌ Tasks have dependencies (use sequential processing)
- ❌ Modifying shared state (risk of race conditions)
- ❌ Memory constraints (each thread consumes memory)

---

### Object-Oriented Design

**Use Case:** "I need 5 different judge implementations (dietary, safety, faithfulness, etc.)"
- **Pattern:** Abstract Base Class
- **Why:** Common interface, shared retry logic
- **Key concepts:**
  - Base class: `BaseJudge(ABC)` with `@abstractmethod evaluate()`
  - Shared: `_call_llm()`, retry logic, validation
  - Subclasses: `DietaryJudge`, `SafetyJudge`, etc.

**Use Case:** "I need a plugin system for custom retrievers"
- **Pattern:** Abstract Base Class
- **Why:** Enforce interface, enable polymorphism
- **Key concepts:**
  - Base class: `BaseRetriever(ABC)` with `@abstractmethod retrieve()`
  - Plugins implement required methods
  - Main code works with base class type

**Use Case:** "I have one function that needs improvement"
- **Pattern:** DON'T use Abstract Base Class
- **Why:** YAGNI (You Ain't Gonna Need It) - premature abstraction
- **Instead:** Write defensive function with TDD

**DON'T use Abstract Base Class when:**
- ❌ Only one implementation (YAGNI principle)
- ❌ Simple inheritance is sufficient
- ❌ Working with functional code (use protocols instead)
- ❌ No clear shared functionality

---

## Combining Patterns

Patterns work together - use multiple patterns in same codebase:

### Pattern Combination 1: TDD + ThreadPoolExecutor

**Scenario:** Implementing parallel batch processing

**Workflow:**
1. **RED**: Write test for batch processing function
   ```python
   def test_should_process_100_queries_in_parallel() -> None:
       queries = ["q1", "q2", ..., "q100"]
       results = batch_process(queries)
       assert len(results) == 100
       assert all(r is not None for r in results)
   ```

2. **GREEN**: Implement using ThreadPoolExecutor template
   ```python
   def batch_process(queries: list[str]) -> list[dict]:
       # ThreadPoolExecutor pattern implementation
       ...
   ```

3. **REFACTOR**: Add defensive coding, progress bars, error handling

### Pattern Combination 2: TDD + Abstract Base Class

**Scenario:** Building judge framework

**Workflow:**
1. **RED**: Write test for base class contract
   ```python
   def test_should_raise_error_when_subclass_missing_evaluate() -> None:
       with pytest.raises(TypeError):
           IncompleteJudge()  # Missing evaluate() implementation
   ```

2. **GREEN**: Implement ABC with `@abstractmethod`
   ```python
   class BaseJudge(ABC):
       @abstractmethod
       def evaluate(self, query: str, response: str) -> dict:
           pass
   ```

3. **REFACTOR**: Add shared functionality, defensive validation

### Pattern Combination 3: All Three Patterns

**Scenario:** Batch processing with multiple judge implementations

**Patterns used:**
- **TDD**: Test-first for all implementations
- **Abstract Base Class**: Common judge interface
- **ThreadPoolExecutor**: Parallel judge evaluation

**Implementation:**
1. Use TDD to build `BaseJudge` ABC
2. Use TDD to build concrete judges (subclasses)
3. Use TDD to build batch evaluator with ThreadPoolExecutor
4. Result: Tested, polymorphic, parallel judge system

---

## Anti-Patterns (What NOT to Do)

### ❌ Anti-Pattern 1: Parallel Processing for Sequential Dependencies

**Bad:**
```python
# Task 2 needs output of Task 1 - CANNOT parallelize
future1 = executor.submit(extract_entities, text)
future2 = executor.submit(link_entities, future1.result())  # Blocks!
```

**Good:**
```python
# Sequential processing for dependent tasks
entities = extract_entities(text)
linked = link_entities(entities)
```

### ❌ Anti-Pattern 2: Premature Abstraction

**Bad:**
```python
# Only one implementation - ABC is overkill
class BaseCalculator(ABC):
    @abstractmethod
    def calculate(self, x: int) -> int:
        pass

class SimpleCalculator(BaseCalculator):  # Only implementation!
    def calculate(self, x: int) -> int:
        return x * 2
```

**Good:**
```python
# Wait until you have 2+ implementations
def calculate(x: int) -> int:
    if not isinstance(x, int):
        raise TypeError("x must be int")
    return x * 2
```

### ❌ Anti-Pattern 3: Skipping Tests in Prototype Phase

**Bad:**
```python
# Write exploratory code, skip tests, move to production
def new_feature():
    # No tests, production code
    ...
```

**Good:**
```python
# Prototype without tests, then apply TDD when productionizing
def prototype():
    # Exploratory code

# When ready for production:
# 1. Write tests (TDD)
# 2. Refactor prototype into tested code
# 3. Add defensive coding
```

---

## Decision Checklist

Before applying a pattern, verify:

### For TDD Workflow:
- [ ] Am I building a feature (not just exploring)?
- [ ] Can I define test cases for expected behavior?
- [ ] Am I willing to write tests BEFORE implementation?

### For ThreadPoolExecutor Parallel:
- [ ] Are tasks I/O-bound (API calls, file I/O, database)?
- [ ] Are tasks independent (no sequential dependencies)?
- [ ] Do I need result order preservation?
- [ ] Can I handle exceptions per-task without crashing batch?

### For Abstract Base Class:
- [ ] Do I have 2+ implementations of same interface?
- [ ] Is there shared functionality (retry logic, validation)?
- [ ] Do I need polymorphic behavior (code works with base type)?
- [ ] Can I clearly define the interface contract?

**If you answer "NO" to any checklist item, reconsider pattern choice.**

---

## Further Reading

- **Pattern Library:** `patterns/README.md`
- **TDD Workflow:** `patterns/tdd-workflow.md`
- **ThreadPoolExecutor Parallel:** `patterns/threadpool-parallel.md`
- **Abstract Base Class:** `patterns/abstract-base-class.md`
- **Integration Checklist:** `integration-checklist.md` (step-by-step application)

---

**Last Updated:** 2025-11-18
**Pattern Count:** 3 (TDD Workflow, ThreadPoolExecutor Parallel, Abstract Base Class)
