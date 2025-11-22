# /pattern Command

**Version:** 1.0.0
**Category:** Code Pattern Discovery & Application
**Related Skill:** `.claude/skills/pattern-application/SKILL.md`

---

## Purpose

Discover, learn, and apply documented code patterns from the Pattern Library (`patterns/README.md`). This command provides quick access to proven patterns for building robust, maintainable AI evaluation systems.

**Key Features:**
- Browse all available patterns with complexity ratings
- View detailed pattern documentation with real examples
- Apply pattern templates with defensive coding built-in

---

## Usage

```
/pattern [name] [apply]
```

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| name | string | No | - | Pattern name (tdd, threadpool, abc). Omit to list all patterns. |
| apply | flag | No | false | Copy pattern template for inline application |

### Examples

```bash
# List all available patterns
/pattern

# Show TDD Workflow pattern details
/pattern tdd

# Show ThreadPoolExecutor Parallel pattern details
/pattern threadpool

# Show Abstract Base Class pattern details
/pattern abc

# Apply TDD Workflow pattern template
/pattern tdd apply

# Apply ThreadPoolExecutor pattern template
/pattern threadpool apply
```

---

## Commands

### /pattern
**Purpose:** List all available patterns from Pattern Library

**Output format:**
```
📚 Pattern Library

Available patterns from patterns/README.md:

1. TDD Workflow                          ⭐⭐ (Medium)
   Primary use: Testing & development methodology
   File: patterns/tdd-workflow.md
   Source: tests/test_rag_generation_eval.py:1-50

2. ThreadPoolExecutor Parallel           ⭐⭐⭐ (High)
   Primary use: Concurrent batch processing (I/O-bound)
   File: patterns/threadpool-parallel.md
   Source: backend/query_rewrite_agent.py:187-208

3. Abstract Base Class                   ⭐⭐⭐ (High)
   Primary use: OOP interface enforcement & polymorphism
   File: patterns/abstract-base-class.md
   Source: backend/ai_judge_framework.py:64-277

---

Complexity Legend:
⭐ (Low)    - Can be understood and applied in <15 minutes
⭐⭐ (Medium) - Requires 15-30 minutes to understand, practice needed
⭐⭐⭐ (High)  - Requires 30-60 minutes to understand, significant practice needed

Usage:
  /pattern [name]       - Show pattern details
  /pattern [name] apply - Apply pattern template

Full documentation: patterns/README.md
```

**Implementation notes:**
- Read `patterns/README.md` Quick Reference Table
- Extract pattern name, complexity, use case, source file
- Display in numbered list format with clear sections

---

### /pattern [name]
**Purpose:** Show detailed documentation for a specific pattern

**Supported pattern names:**
- `tdd` → TDD Workflow pattern
- `threadpool` → ThreadPoolExecutor Parallel pattern
- `abc` → Abstract Base Class pattern

**Output format for /pattern tdd:**
```
📖 TDD Workflow Pattern

Pattern Type: Development Methodology
Complexity: ⭐⭐ (Medium)
Source: Lesson 13 - RAG Generation & Attribution
Documentation: patterns/tdd-workflow.md

---

## What it is

Test-Driven Development (TDD) methodology where you write tests *before*
implementation code. Follow the RED → GREEN → REFACTOR cycle.

---

## When to use

✅ Use when:
  - Building new features from scratch
  - Refactoring existing code
  - Fixing bugs (write failing test first, then fix)
  - Working with critical business logic

❌ DON'T use when:
  - Exploratory prototyping or proof-of-concepts
  - UI/UX design with highly fluid requirements
  - Spiking on unfamiliar libraries

---

## Key Concepts

1. RED Phase: Write ONE failing test
   - Naming: test_should_[result]_when_[condition]()
   - Run test and confirm it fails
   - ❌ NEVER write implementation code

2. GREEN Phase: Write minimal code to pass test
   - ONLY enough code to make test pass
   - ❌ NEVER modify the test
   - ❌ NO extra features

3. REFACTOR Phase: Improve code quality
   - Apply defensive coding principles
   - Keep all tests passing
   - Run tests after each change

---

## Quick Example

# RED: Write failing test
def test_should_extract_claims_when_response_has_multiple_statements() -> None:
    detector = AttributionDetector()
    response = "The Gita teaches dharma. It was spoken by Krishna."
    claims = detector.extract_claims(response)
    assert len(claims) >= 2

# GREEN: Minimal implementation
class AttributionDetector:
    def extract_claims(self, response: str) -> list[str]:
        if not response:
            return []
        return response.split(". ")

# REFACTOR: Add defensive coding
class AttributionDetector:
    def extract_claims(self, response: str) -> list[str]:
        if not isinstance(response, str):
            raise TypeError("response must be a string")
        if not response.strip():
            return []
        import re
        return [c.strip() for c in re.split(r'[.!?]+', response) if c.strip()]

---

## Real Examples from Codebase

See: tests/test_rag_generation_eval.py:1-50

---

## Common Pitfalls

❌ Writing implementation before test exists
❌ Writing multiple tests at once
❌ Modifying test during GREEN phase
❌ Skipping REFACTOR phase

---

## Next Steps

  /pattern tdd apply    - Copy template for your code
  Full docs: patterns/tdd-workflow.md
  Related: .claude/skills/tdd-methodology/SKILL.md
```

**Implementation notes:**
- Map pattern names to files: `tdd` → `patterns/tdd-workflow.md`
- Extract key sections from pattern documentation:
  - Overview ("What it is")
  - When to Use (✅ Use when / ❌ DON'T use when)
  - Key Concepts
  - Quick Example code
  - Real Examples from Codebase
  - Common Pitfalls
- Format with clear sections and emoji markers
- Include links to full documentation and related files

**Output format for /pattern threadpool:**
```
📖 ThreadPoolExecutor Parallel Pattern

Pattern Type: Concurrency
Complexity: ⭐⭐⭐ (High)
Source: Lesson 12 - Hybrid Retrieval & Context Quality
Documentation: patterns/threadpool-parallel.md

---

## What it is

Python's built-in pattern for executing multiple I/O-bound tasks in parallel
using threads, with order preservation and progress tracking.

---

## When to use

✅ Use when:
  - Batch processing (API calls, file I/O, database queries)
  - I/O-bound tasks that spend time waiting on external resources
  - Need to preserve result order matching input order
  - Users need real-time progress feedback

❌ DON'T use when:
  - CPU-bound tasks (use ProcessPoolExecutor instead)
  - Shared state modifications (risk of race conditions)
  - Sequential dependencies (Task N depends on Task N-1)
  - Memory constraints (each thread consumes memory)

---

## Key Concepts

1. future_to_index mapping: Preserve result order
2. Exception handling: Catch failures without crashing batch
3. Progress tracking: Integrate tqdm with as_completed()
4. max_workers tuning: 5-20 for I/O tasks, consider API rate limits

---

## Quick Example

from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

queries = ["q1", "q2", "q3"]
results = [None] * len(queries)

with ThreadPoolExecutor(max_workers=5) as executor:
    # Submit with index mapping
    future_to_index = {
        executor.submit(process_query, query): i
        for i, query in enumerate(queries)
    }

    # Collect with progress bar
    for future in tqdm(as_completed(future_to_index), total=len(queries)):
        index = future_to_index[future]
        try:
            results[index] = future.result()
        except Exception as e:
            print(f"Error processing query {index}: {e}")
            results[index] = None  # Fallback

---

## Real Examples from Codebase

See: backend/query_rewrite_agent.py:187-208

Real-world performance:
  Sequential: ~300s for 100 API calls
  Parallel (max_workers=10): ~30s (10× speedup)

---

## Common Pitfalls

❌ Not preserving result order (missing future_to_index)
❌ Ignoring exceptions (batch crashes on single failure)
❌ Wrong max_workers (too high causes rate limit errors)
❌ Using for CPU-bound tasks (no speedup, use multiprocessing)

---

## Next Steps

  /pattern threadpool apply - Copy template for your code
  Full docs: patterns/threadpool-parallel.md
  Related: .claude/skills/pattern-application/SKILL.md
```

**Output format for /pattern abc:**
```
📖 Abstract Base Class Pattern

Pattern Type: Object-Oriented Programming (OOP)
Complexity: ⭐⭐⭐ (High)
Source: Lesson 10 - AI-as-Judge Mastery & Production Patterns
Documentation: patterns/abstract-base-class.md

---

## What it is

Design pattern for enforcing interface contracts in OOP. Define common interface
that all subclasses must implement, preventing instantiation of incomplete
implementations.

---

## When to use

✅ Use when:
  - Multiple implementations sharing a common interface
  - Building frameworks or plugin systems
  - Need polymorphic behavior (code works with base class type)
  - Shared functionality across implementations (retry logic, validation)

❌ DON'T use when:
  - Single implementation (YAGNI principle)
  - Simple inheritance is sufficient
  - Functional code (use protocols/interfaces instead)
  - Premature abstraction without clear need

---

## Key Concepts

1. ABC inheritance: Base class for abstract classes
2. @abstractmethod decorator: Mark methods that must be implemented
3. Defensive initialization: Validate inputs in base class __init__
4. super().__init__() call: Subclasses MUST call parent initializer

---

## Quick Example

from abc import ABC, abstractmethod

class BaseJudge(ABC):
    """Abstract base class for all judge implementations."""

    def __init__(self, model: str, temperature: float = 0.0):
        # Defensive validation
        if not isinstance(model, str):
            raise TypeError("model must be a string")
        if not (0.0 <= temperature <= 2.0):
            raise ValueError("temperature must be between 0.0 and 2.0")

        self.model = model
        self.temperature = temperature

    @abstractmethod
    def evaluate(self, query: str, response: str) -> dict:
        """Subclasses must implement."""
        pass

    def _call_llm(self, prompt: str) -> str:
        """Shared helper method."""
        # Retry logic, API calls, etc.
        pass


class DietaryAdherenceJudge(BaseJudge):
    """Concrete implementation."""

    def __init__(self, model: str, temperature: float = 0.0):
        super().__init__(model, temperature)  # CRITICAL: Call parent
        self.prompt_template = self._load_template("dietary.txt")

    def evaluate(self, query: str, response: str) -> dict:
        """Implement required method."""
        prompt = self.prompt_template.format(query=query, response=response)
        raw = self._call_llm(prompt)  # Use shared helper
        return {"score": 1.0, "reasoning": raw}

---

## Real Examples from Codebase

See: backend/ai_judge_framework.py:64-277

---

## Common Pitfalls

❌ Forgetting super().__init__() in subclass (parent not initialized)
❌ Not marking abstract methods with @abstractmethod
❌ Trying to instantiate abstract base class
❌ Overcomplicating with unnecessary abstraction

---

## Next Steps

  /pattern abc apply - Copy template for your code
  Full docs: patterns/abstract-base-class.md
  Related: .claude/skills/pattern-application/SKILL.md
```

**Error handling:**
- If pattern name not recognized, show:
  ```
  ❌ Pattern not found: "unknown-pattern"

  Available patterns: tdd, threadpool, abc

  Use /pattern to list all patterns.
  ```

---

### /pattern [name] apply
**Purpose:** Copy pattern template for inline application with defensive coding

**Supported pattern names:**
- `tdd apply` → TDD Workflow template
- `threadpool apply` → ThreadPoolExecutor template
- `abc apply` → Abstract Base Class template

**Output format for /pattern tdd apply:**
```
✅ TDD Workflow Template

Copy this template to start using TDD pattern:

---

# RED Phase: Write failing test
def test_should_[expected_result]_when_[condition]() -> None:
    """Test description.

    This test validates that [function_name] returns [expected_result]
    when given [condition].
    """
    # Arrange: Set up test data
    input_data = ...
    expected_output = ...

    # Act: Call function under test
    actual_output = your_function(input_data)

    # Assert: Verify behavior
    assert actual_output == expected_output


# GREEN Phase: Minimal implementation
def your_function(arg: Type) -> ReturnType:
    """Minimal implementation to pass test."""
    # Just enough code to make test pass
    return result


# REFACTOR Phase: Apply defensive coding
def your_function(arg: Type | None) -> ReturnType:
    """Full description.

    Args:
        arg: Description of argument

    Returns:
        Description of return value

    Raises:
        TypeError: When type validation fails
        ValueError: When value validation fails
    """
    # Step 1: Type checking
    if not isinstance(arg, ExpectedType):
        raise TypeError("arg must be ExpectedType")

    # Step 2: Input validation
    if not arg:
        raise ValueError("arg cannot be empty")

    # Step 3: Edge case handling
    if len(arg) == 0:
        return default_value

    # Step 4: Main logic
    result = process(arg)

    # Step 5: Return
    return result

---

Next steps:
1. Replace placeholders: [expected_result], [condition], your_function
2. Write RED test first, run pytest to verify it fails
3. Write GREEN minimal implementation, run pytest to verify it passes
4. REFACTOR with defensive coding, run pytest after each change

Full documentation: patterns/tdd-workflow.md
Related skill: .claude/skills/tdd-methodology/SKILL.md
```

**Output format for /pattern threadpool apply:**
```
✅ ThreadPoolExecutor Parallel Template

Copy this template for parallel batch processing:

---

from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm


def process_batch_parallel(
    items: list[Any],
    process_func: callable,
    max_workers: int = 10,
    show_progress: bool = True
) -> list[Any]:
    """Process items in parallel using ThreadPoolExecutor.

    Args:
        items: List of items to process
        process_func: Function to apply to each item
        max_workers: Number of parallel workers (5-20 for I/O tasks)
        show_progress: Whether to show tqdm progress bar

    Returns:
        List of results in same order as input items

    Raises:
        TypeError: If items is not a list or process_func is not callable
        ValueError: If items is empty or max_workers is invalid
    """
    # Step 1: Type checking
    if not isinstance(items, list):
        raise TypeError("items must be a list")
    if not callable(process_func):
        raise TypeError("process_func must be callable")

    # Step 2: Input validation
    if not items:
        raise ValueError("items cannot be empty")
    if not (1 <= max_workers <= 50):
        raise ValueError("max_workers must be between 1 and 50")

    # Step 3: Initialize results with None (preserves order)
    results = [None] * len(items)

    # Step 4: Submit tasks with index mapping
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Map futures to original indices
        future_to_index = {
            executor.submit(process_func, item): i
            for i, item in enumerate(items)
        }

        # Step 5: Collect results with progress tracking
        iterator = as_completed(future_to_index)
        if show_progress:
            iterator = tqdm(iterator, total=len(items), desc="Processing")

        for future in iterator:
            index = future_to_index[future]
            try:
                results[index] = future.result()
            except Exception as e:
                print(f"Error processing item {index}: {e}")
                results[index] = None  # Fallback: preserve order

    # Step 6: Return results in original order
    return results


# Example usage:
def process_single_item(item: str) -> dict:
    """Process a single item (I/O-bound task)."""
    # Your processing logic here (API call, file I/O, etc.)
    return {"item": item, "result": "processed"}


# Process batch in parallel
items = ["item1", "item2", "item3"]
results = process_batch_parallel(items, process_single_item, max_workers=10)

---

Next steps:
1. Replace process_single_item with your actual processing function
2. Tune max_workers based on:
   - I/O-bound: 5-20 workers
   - API rate limits: Lower (e.g., 5)
   - Memory constraints: Lower
3. Add defensive coding to process_single_item
4. Test with TDD pattern (patterns/tdd-workflow.md)

Performance expectations:
  Sequential: ~N × processing_time
  Parallel: ~(N / max_workers) × processing_time

Full documentation: patterns/threadpool-parallel.md
Related skill: .claude/skills/pattern-application/SKILL.md
```

**Output format for /pattern abc apply:**
```
✅ Abstract Base Class Template

Copy this template for OOP interface enforcement:

---

from abc import ABC, abstractmethod


class BaseYourClass(ABC):
    """Abstract base class for [purpose].

    All subclasses must implement abstract methods and call super().__init__().
    """

    def __init__(self, common_param: str, optional_param: float = 0.0):
        """Initialize base class with defensive validation.

        Args:
            common_param: Description of parameter
            optional_param: Description of optional parameter

        Raises:
            TypeError: If parameters have wrong type
            ValueError: If parameters have invalid values
        """
        # Step 1: Type checking
        if not isinstance(common_param, str):
            raise TypeError("common_param must be a string")
        if not isinstance(optional_param, (int, float)):
            raise TypeError("optional_param must be numeric")

        # Step 2: Input validation
        if not common_param.strip():
            raise ValueError("common_param cannot be empty")
        if optional_param < 0:
            raise ValueError("optional_param must be non-negative")

        # Step 3: Store attributes
        self.common_param = common_param
        self.optional_param = optional_param

    @abstractmethod
    def required_method(self, arg: str) -> dict:
        """Abstract method that subclasses MUST implement.

        Args:
            arg: Description of argument

        Returns:
            Description of return value
        """
        pass

    def shared_helper_method(self, data: Any) -> Any:
        """Concrete method shared by all subclasses.

        This method is available to all subclasses and implements
        common functionality like retry logic, validation, etc.
        """
        # Shared logic here (retry, logging, validation, etc.)
        return processed_data


class ConcreteImplementation(BaseYourClass):
    """Concrete implementation of BaseYourClass.

    Implements all abstract methods and extends base functionality.
    """

    def __init__(self, common_param: str, optional_param: float = 0.0,
                 specific_param: int = 0):
        """Initialize concrete class.

        Args:
            common_param: Passed to base class
            optional_param: Passed to base class
            specific_param: Specific to this implementation

        Raises:
            TypeError: If parameters have wrong type
            ValueError: If parameters have invalid values
        """
        # CRITICAL: Call parent __init__ first
        super().__init__(common_param, optional_param)

        # Validate implementation-specific parameters
        if not isinstance(specific_param, int):
            raise TypeError("specific_param must be an integer")

        self.specific_param = specific_param

    def required_method(self, arg: str) -> dict:
        """Implement required abstract method.

        Args:
            arg: Description of argument

        Returns:
            Dictionary with results
        """
        # Step 1: Validate input
        if not isinstance(arg, str):
            raise TypeError("arg must be a string")

        # Step 2: Use shared helper
        processed = self.shared_helper_method(arg)

        # Step 3: Implementation-specific logic
        result = {"input": arg, "processed": processed}

        return result


# Example usage:
# Cannot instantiate abstract base class
# base = BaseYourClass("param", 1.0)  # Raises TypeError

# Can instantiate concrete implementation
concrete = ConcreteImplementation("param", 1.0, specific_param=42)
result = concrete.required_method("test")

# Polymorphic usage (code works with base class type)
def process_with_base_class(obj: BaseYourClass, data: str) -> dict:
    """Function accepts any subclass of BaseYourClass."""
    return obj.required_method(data)

---

Next steps:
1. Replace BaseYourClass with meaningful name (e.g., BaseJudge, BaseRetriever)
2. Define abstract methods that all implementations must provide
3. Add shared functionality in concrete methods
4. Create concrete implementations inheriting from base
5. CRITICAL: Always call super().__init__() in subclass __init__
6. Test with TDD pattern (patterns/tdd-workflow.md)

Common use cases:
  - Multiple judge implementations (faithfulness, relevance, tone)
  - Multiple retrieval strategies (semantic, hybrid, keyword)
  - Plugin systems with common interface

Full documentation: patterns/abstract-base-class.md
Related skill: .claude/skills/pattern-application/SKILL.md
```

**Implementation notes:**
- Provide complete, copy-paste ready templates
- Include defensive coding in all templates (type hints, validation, error handling)
- Add inline comments explaining critical steps
- Include "Next steps" guidance for customization
- Reference full documentation and related skills

---

## Integration with Pattern Application Skill

**Command Role (Manual Discovery):**
- You invoke `/pattern` or `/pattern [name]` manually to browse patterns
- Displays pattern catalog and documentation
- Provides templates for copy-paste application
- Does NOT automatically apply patterns

**Skill Role (Automatic Application):**
- Activates automatically when you implement features
- Suggests patterns based on context (e.g., "batch processing" → ThreadPoolExecutor)
- Enforces pattern usage for consistency
- See `.claude/skills/pattern-application/SKILL.md` for details

**When to use command vs. skill:**
- Use `/pattern` when you want to explore available patterns or copy a template
- Skill activates automatically when you say "batch processing", "parallel", "abstract base class", etc.
- Both work together: command for discovery, skill for application guidance

---

## Pattern Name Aliases

For convenience, the following aliases are supported:

| Alias | Full Pattern Name |
|-------|------------------|
| tdd | TDD Workflow |
| test | TDD Workflow |
| threadpool | ThreadPoolExecutor Parallel |
| parallel | ThreadPoolExecutor Parallel |
| concurrent | ThreadPoolExecutor Parallel |
| abc | Abstract Base Class |
| base-class | Abstract Base Class |
| interface | Abstract Base Class |

---

## Best Practices

### 1. Explore patterns before implementing
When starting a new feature:
```bash
/pattern  # List all patterns
# Read descriptions, identify relevant pattern
/pattern tdd  # View TDD pattern details
```

### 2. Use apply for template scaffolding
When ready to implement:
```bash
/pattern threadpool apply  # Copy template
# Paste template into your code
# Customize placeholders
# Test with TDD
```

### 3. Reference pattern documentation
For deeper understanding:
```bash
# Command shows summary, but read full docs for:
# - Common pitfalls
# - Real codebase examples
# - Integration with other patterns
```

### 4. Combine patterns
Many features benefit from multiple patterns:
```bash
# Example: Batch processing with tests
/pattern threadpool apply  # Parallel processing template
/pattern tdd apply         # Test template
# Write TDD tests for ThreadPoolExecutor code
```

---

## Common Scenarios

### Starting a new feature
```bash
/pattern  # What patterns are available?
/pattern tdd  # How should I structure tests?
/pattern tdd apply  # Copy TDD template
```

### Batch processing task
```bash
/pattern threadpool  # View parallel processing pattern
/pattern threadpool apply  # Copy template
# Customize process_func, tune max_workers
```

### Creating framework with multiple implementations
```bash
/pattern abc  # View Abstract Base Class pattern
/pattern abc apply  # Copy template
# Define abstract methods, create concrete implementations
```

### Learning pattern library
```bash
/pattern  # Browse all patterns
/pattern tdd  # Study first pattern
/pattern threadpool  # Study second pattern
/pattern abc  # Study third pattern
# Read full docs: patterns/README.md
```

---

## Troubleshooting

### "I don't know which pattern to use"
```bash
/pattern  # List all patterns with use cases
# Read "Primary use" column
# Check patterns/README.md "When to Use" sections
```

### "Pattern template doesn't fit my use case"
- Pattern templates are starting points, not rigid rules
- Customize template to fit your specific requirements
- Keep defensive coding principles (type hints, validation, error handling)
- If pattern doesn't fit, you may not need it (YAGNI principle)

### "How do I combine patterns?"
Common combinations:
- **TDD + ThreadPoolExecutor**: Write tests for parallel processing code
- **TDD + Abstract Base Class**: Test-driven development of OOP frameworks
- **All three**: Test-driven development of parallel judge implementations

---

## References

- **Pattern Library:** `patterns/README.md` (catalog of all patterns)
- **Pattern Application Skill:** `.claude/skills/pattern-application/SKILL.md` (automatic application)
- **TDD Pattern:** `patterns/tdd-workflow.md` (full documentation)
- **ThreadPoolExecutor Pattern:** `patterns/threadpool-parallel.md` (full documentation)
- **Abstract Base Class Pattern:** `patterns/abstract-base-class.md` (full documentation)
- **CLAUDE.md:** CLAUDE.md:33-115 (TDD mode), CLAUDE.md:276-295 (Pattern Library section)

---

## Version History

**1.0.0** (2025-11-22)
- Initial implementation
- Support for 3 core patterns (TDD, ThreadPoolExecutor, Abstract Base Class)
- Pattern listing, details, and template application
- Integration with Pattern Application Skill
- Pattern name aliases for convenience
