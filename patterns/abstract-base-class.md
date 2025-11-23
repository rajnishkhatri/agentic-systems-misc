# Abstract Base Class Pattern

**Pattern Type:** Object-Oriented Programming (OOP)
**Complexity:** ⭐⭐⭐ (High)
**Source:** Lesson 10 - AI-as-Judge Mastery & Production Patterns
**Created:** 2025-11-12
**File References:** `backend/ai_judge_framework.py:64-100`, `backend/ai_judge_framework.py:248-277`

---

## Overview

**Abstract Base Classes (ABCs)** are a design pattern for enforcing interface contracts in object-oriented programming. They define a common interface (methods and properties) that all subclasses must implement, preventing instantiation of incomplete implementations.

**Key Benefits:**
- **Interface enforcement**: Compiler/runtime guarantees that subclasses implement required methods
- **Polymorphism**: Work with base class type while using different concrete implementations
- **Design clarity**: Clearly separates "what" (interface) from "how" (implementation)
- **Code reuse**: Share common functionality in base class while allowing customization
- **Extensibility**: Add new implementations without modifying existing code

**Real-world impact:** In Lesson 10, the `BaseJudge` ABC enabled 3+ judge implementations (DietaryAdherenceJudge, SubstantiationJudge, GenericCriteriaJudge) with shared retry logic, template loading, and validation—eliminating code duplication.

---

## When to Use

✅ **Use Abstract Base Classes when:**
- **Multiple implementations**: You need 2+ classes that share a common interface but differ in implementation
- **Framework design**: Building a plugin system or framework where users will add their own implementations
- **Polymorphic behavior**: Code needs to work with different implementations through a common interface
- **Shared behavior**: Base class provides common functionality (like logging, validation, retry logic)
- **Contract enforcement**: You want compile-time/runtime guarantees that implementations are complete
- **Memory vs. RAG Systems**: Implementing different memory storage backends or RAG retrievers (see [Context Engineering Terminology](../google-context/TERMINOLOGY.md#2-memory-vs-rag-retrieval-augmented-generation))

❌ **DON'T use Abstract Base Classes when:**
- **Single implementation**: Only one concrete class will ever exist (YAGNI—You Ain't Gonna Need It)
- **Simple inheritance**: Standard inheritance is sufficient (no need to enforce interface)
- **Functional code**: Using functions instead of classes (consider protocols/interfaces instead)
- **Over-abstraction**: Creating ABCs "just in case" without clear need (premature abstraction)

**Context Engineering Example:**
When building context-aware AI systems, ABCs are useful for:
- **Memory Stores**: `BaseMemoryStore` → `LocalMemoryStore`, `VectorMemoryStore`, `SQLMemoryStore`
- **RAG Retrievers**: `BaseRetriever` → `SemanticRetriever`, `ExactMatchRetriever`, `HybridRetriever`
- **Session Managers**: `BaseSessionManager` → `GitaSessionManager`, `MultiTenantSessionManager`
- See [TERMINOLOGY.md](../google-context/TERMINOLOGY.md) for Memory vs. RAG distinction

---

## Core Concepts

### 1. Python `abc` Module

Python's `abc` module provides decorators and base classes for defining ABCs:

```python
from abc import ABC, abstractmethod

class BaseClass(ABC):
    """Abstract base class example."""

    @abstractmethod
    def required_method(self) -> str:
        """All subclasses must implement this."""
        pass

    def optional_method(self) -> str:
        """Subclasses can override or use default."""
        return "default implementation"
```

**Key components:**
- `ABC`: Base class for abstract classes (inherits from)
- `@abstractmethod`: Decorator marking methods that must be implemented by subclasses
- **Instantiation prevention**: Python raises `TypeError` if you try to instantiate a class with unimplemented abstract methods

### 2. Defensive Initialization Pattern

**Problem:** Base class `__init__` should validate inputs shared by all subclasses.

**Solution:** Perform type checking and input validation in base class `__init__`.

```python
from abc import ABC, abstractmethod

class BaseJudge(ABC):
    """Abstract base class for all judge implementations."""

    def __init__(self, model: str, temperature: float = 0.0):
        """Initialize judge with defensive validation.

        Args:
            model: LLM model name
            temperature: Sampling temperature (0.0-2.0)

        Raises:
            TypeError: If model is not a string
            ValueError: If temperature is out of range
        """
        # Step 1: Type checking (defensive)
        if not isinstance(model, str):
            raise TypeError("model must be a string")

        # Step 2: Input validation (defensive)
        if not (0.0 <= temperature <= 2.0):
            raise ValueError("temperature must be between 0.0 and 2.0")

        # Step 3: Initialize instance attributes
        self.model = model
        self.temperature = temperature

    @abstractmethod
    def evaluate(self, query: str, response: str) -> dict:
        """Evaluate query-response pair. Subclasses must implement."""
        pass
```

### 3. Calling `super().__init__()` in Subclasses

**Critical:** Subclasses MUST call `super().__init__()` to execute base class initialization.

```python
class ConcreteJudge(BaseJudge):
    """Concrete implementation of BaseJudge."""

    def __init__(self, model: str, temperature: float = 0.0):
        # ALWAYS call super().__init__() first
        super().__init__(model, temperature)

        # Then add subclass-specific initialization
        self.custom_attribute = "custom value"

    def evaluate(self, query: str, response: str) -> dict:
        """Implement required abstract method."""
        # Implementation here...
        return {"score": 1.0}
```

---

## Code Template: Abstract Base Class with Defensive Init

```python
from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseProcessor(ABC):
    """Abstract base class for all processor implementations.

    Provides common functionality:
    - Input validation
    - Shared configuration
    - Helper methods

    Subclasses must implement:
    - process(): Core processing logic
    """

    def __init__(self, config: Dict[str, Any]):
        """Initialize processor with defensive validation.

        Args:
            config: Configuration dictionary

        Raises:
            TypeError: If config is not a dict
            ValueError: If required keys are missing
        """
        # Step 1: Type checking (defensive)
        if not isinstance(config, dict):
            raise TypeError("config must be a dictionary")

        # Step 2: Input validation (defensive)
        required_keys = ["name", "max_retries"]
        missing = [k for k in required_keys if k not in config]
        if missing:
            raise ValueError(f"Missing required config keys: {missing}")

        if config["max_retries"] < 1:
            raise ValueError("max_retries must be at least 1")

        # Step 3: Initialize shared attributes
        self.config = config
        self.name = config["name"]
        self.max_retries = config["max_retries"]

    @abstractmethod
    def process(self, data: Any) -> Any:
        """Process data. Subclasses must implement.

        Args:
            data: Input data to process

        Returns:
            Processed result
        """
        pass

    def validate_input(self, data: Any) -> bool:
        """Shared validation logic (optional for subclasses to use).

        Args:
            data: Input data to validate

        Returns:
            True if valid, False otherwise
        """
        return data is not None


class ConcreteProcessor(BaseProcessor):
    """Concrete implementation of BaseProcessor."""

    def __init__(self, config: Dict[str, Any], extra_param: str = "default"):
        """Initialize concrete processor.

        Args:
            config: Configuration dictionary
            extra_param: Subclass-specific parameter
        """
        # ALWAYS call super().__init__() first
        super().__init__(config)

        # Add subclass-specific initialization
        self.extra_param = extra_param

    def process(self, data: Any) -> Any:
        """Implement required abstract method.

        Args:
            data: Input data

        Returns:
            Processed data
        """
        if not self.validate_input(data):
            raise ValueError("Invalid input data")

        # Subclass-specific processing
        return f"Processed: {data} with {self.extra_param}"


# Usage
processor = ConcreteProcessor(config={"name": "MyProcessor", "max_retries": 3})
result = processor.process("test data")
```

---

## Real Example from Codebase

**Source:** `backend/ai_judge_framework.py:64-100` (BaseJudge) and `248-277` (DietaryAdherenceJudge)

### Base Class: `BaseJudge`

```python
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional

import litellm
from tenacity import retry, stop_after_attempt, wait_exponential


class BaseJudge(ABC):
    """Abstract base class for all judge implementations.

    Provides common functionality:
    - Prompt template loading
    - LLM API calls with retry logic
    - Input validation
    - Batch processing

    Subclasses must implement:
    - evaluate(): Single evaluation logic
    """

    def __init__(self, model: str, temperature: float = 0.0, max_retries: int = 3):
        """Initialize judge with model configuration.

        Args:
            model: LLM model name (e.g., "gpt-4o-mini", "claude-sonnet")
            temperature: Sampling temperature (0.0-2.0)
            max_retries: Number of retry attempts for API failures

        Raises:
            TypeError: If model is not a string
            ValueError: If temperature is out of range
        """
        # Type checking
        if not isinstance(model, str):
            raise TypeError("model must be a string")

        # Input validation
        if not (0.0 <= temperature <= 2.0):
            raise ValueError("temperature must be between 0.0 and 2.0")

        self.model = model
        self.temperature = temperature
        self.max_retries = max_retries
        self.prompt_template: Optional[str] = None

    def _load_template(self, template_name: str) -> str:
        """Load prompt template from file.

        Args:
            template_name: Name of template file in lesson-10/templates/judge_prompts/

        Returns:
            Template content as string

        Raises:
            FileNotFoundError: If template file doesn't exist
        """
        template_path = (
            Path("lesson-10") / "templates" / "judge_prompts" / template_name
        )

        if not template_path.exists():
            raise FileNotFoundError(f"Template file not found: {template_path}")

        return template_path.read_text(encoding="utf-8")

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def _call_llm(self, prompt: str) -> str:
        """Call LLM API with retry logic.

        Args:
            prompt: Formatted prompt string

        Returns:
            Raw LLM response content

        Raises:
            Exception: If all retry attempts fail
        """
        response = litellm.completion(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.temperature,
        )

        return response.choices[0].message.content

    @abstractmethod
    def evaluate(self, query: str, response: str, **kwargs) -> Dict[str, Any]:
        """Evaluate query-response pair. Subclasses must implement.

        Args:
            query: Input query
            response: Response to evaluate
            **kwargs: Subclass-specific parameters

        Returns:
            Evaluation result dictionary
        """
        pass
```

### Concrete Implementation: `DietaryAdherenceJudge`

```python
class DietaryAdherenceJudge(BaseJudge):
    """Judge for evaluating dietary restriction compliance in recipes.

    Checks whether recipe responses properly adhere to specified dietary
    restrictions (vegan, gluten-free, keto, etc.).
    """

    def __init__(self, model: str, temperature: float = 0.0):
        """Initialize dietary adherence judge.

        Args:
            model: LLM model name
            temperature: Sampling temperature
        """
        # CRITICAL: Call super().__init__() first
        super().__init__(model, temperature)

        # Load subclass-specific prompt template
        self.prompt_template = self._load_template("dietary_adherence_judge.txt")

    def evaluate(
        self, query: str, response: str, dietary_restriction: str
    ) -> Dict[str, Any]:
        """Evaluate dietary adherence.

        Args:
            query: User's recipe query
            response: Recipe response to evaluate
            dietary_restriction: Dietary restriction to check (e.g., "vegan")

        Returns:
            JudgeResult with PASS/FAIL score

        Raises:
            TypeError: If inputs are not strings
            ValueError: If inputs are empty
        """
        # Defensive validation
        if not isinstance(query, str) or not isinstance(response, str):
            raise TypeError("query and response must be strings")
        if not query.strip() or not response.strip():
            raise ValueError("query and response cannot be empty")

        # Format prompt using base class template
        prompt = self.prompt_template.format(
            query=query,
            response=response,
            dietary_restriction=dietary_restriction
        )

        # Call LLM using base class retry logic
        raw_response = self._call_llm(prompt)

        # Parse and return result
        return self._parse_json_response(raw_response)
```

**Why this implementation is excellent:**
1. **Defensive initialization**: Base class validates `model` and `temperature` for all subclasses
2. **Code reuse**: `_load_template()` and `_call_llm()` shared by all judges
3. **Polymorphism**: Can write code like `judge.evaluate(...)` without knowing which judge type
4. **Extensibility**: Adding new judge types requires only implementing `evaluate()`
5. **Type safety**: ABC prevents instantiating incomplete implementations

---

## Integration with Defensive Coding

**Defensive ABC Pattern:**

```python
from abc import ABC, abstractmethod
from typing import Any, Dict


class DefensiveBaseClass(ABC):
    """Abstract base class with defensive coding."""

    def __init__(self, name: str, max_retries: int = 3):
        """Initialize with defensive validation.

        Args:
            name: Instance name
            max_retries: Maximum retry attempts

        Raises:
            TypeError: If types are incorrect
            ValueError: If values are invalid
        """
        # Step 1: Type checking
        if not isinstance(name, str):
            raise TypeError("name must be a string")
        if not isinstance(max_retries, int):
            raise TypeError("max_retries must be an integer")

        # Step 2: Input validation
        if not name.strip():
            raise ValueError("name cannot be empty")
        if max_retries < 1:
            raise ValueError("max_retries must be at least 1")

        # Step 3: Initialize
        self.name = name
        self.max_retries = max_retries

    def _validate_input(self, data: Any) -> None:
        """Shared validation helper.

        Args:
            data: Input data to validate

        Raises:
            ValueError: If validation fails
        """
        if data is None:
            raise ValueError("data cannot be None")

    @abstractmethod
    def process(self, data: Any) -> Any:
        """Abstract method with defensive contract.

        Args:
            data: Input data

        Returns:
            Processed result

        Raises:
            ValueError: If input is invalid
            NotImplementedError: If subclass doesn't implement
        """
        pass


class ConcreteImplementation(DefensiveBaseClass):
    """Concrete implementation with defensive coding."""

    def __init__(self, name: str, max_retries: int = 3, timeout: float = 5.0):
        """Initialize with additional defensive validation."""
        # Call super first
        super().__init__(name, max_retries)

        # Validate subclass-specific parameters
        if not isinstance(timeout, (int, float)):
            raise TypeError("timeout must be a number")
        if timeout <= 0:
            raise ValueError("timeout must be positive")

        self.timeout = timeout

    def process(self, data: Any) -> Any:
        """Implement abstract method with defensive logic."""
        # Use shared validation
        self._validate_input(data)

        # Additional validation
        if not isinstance(data, str):
            raise TypeError("data must be a string")

        # Process
        return f"Processed: {data}"
```

---

## Common Pitfalls

### ❌ Pitfall 1: Forgetting `ABC` Inheritance

```python
# BAD: Missing ABC inheritance
from abc import abstractmethod

class BaseClass:  # Should inherit from ABC
    @abstractmethod
    def required_method(self):
        pass

# No error raised! Can instantiate incomplete class
instance = BaseClass()  # Should fail but doesn't
```

**Fix:** Always inherit from `ABC`.

```python
from abc import ABC, abstractmethod

class BaseClass(ABC):
    @abstractmethod
    def required_method(self):
        pass
```

### ❌ Pitfall 2: Missing `@abstractmethod` Decorator

```python
# BAD: Forgot @abstractmethod decorator
from abc import ABC

class BaseClass(ABC):
    def required_method(self):  # Should be @abstractmethod
        pass

# Subclass can skip implementation!
class ConcreteClass(BaseClass):
    pass

instance = ConcreteClass()  # No error!
```

**Fix:** Use `@abstractmethod` decorator.

### ❌ Pitfall 3: Not Calling `super().__init__()`

```python
# BAD: Subclass doesn't call super().__init__()
class ConcreteJudge(BaseJudge):
    def __init__(self, model: str):
        # Missing: super().__init__(model)
        self.custom_attr = "value"

    def evaluate(self, query: str, response: str) -> dict:
        # self.model doesn't exist! BaseJudge.__init__() never ran
        return {"model": self.model}  # AttributeError!
```

**Fix:** Always call `super().__init__()` first.

### ❌ Pitfall 4: Over-abstraction

```python
# BAD: Creating ABC for single implementation
from abc import ABC, abstractmethod

class BaseDataLoader(ABC):
    @abstractmethod
    def load(self) -> list:
        pass

class JSONDataLoader(BaseDataLoader):  # Only implementation
    def load(self) -> list:
        return []

# No other implementations exist or planned
```

**Why it's bad:** Unnecessary complexity. YAGNI (You Ain't Gonna Need It).

**Fix:** Use simple class until second implementation is needed.

### ❌ Pitfall 5: Abstract Methods with Implementation

```python
# BAD: Abstract method has implementation logic
from abc import ABC, abstractmethod

class BaseClass(ABC):
    @abstractmethod
    def process(self, data: str) -> str:
        # Should be 'pass' or minimal contract documentation
        return data.upper()  # BAD: Implementation in abstract method
```

**Why it's bad:** Abstract methods should define contract, not implementation. Subclasses may not call `super().process()` and miss this logic.

**Fix:** Move shared logic to non-abstract helper method.

```python
class BaseClass(ABC):
    @abstractmethod
    def process(self, data: str) -> str:
        """Process data. Subclasses must implement."""
        pass

    def _uppercase_helper(self, data: str) -> str:
        """Shared helper method (non-abstract)."""
        return data.upper()
```

---

## Design Patterns Using ABCs

### Pattern 1: Strategy Pattern

```python
from abc import ABC, abstractmethod

class CompressionStrategy(ABC):
    """Abstract compression strategy."""

    @abstractmethod
    def compress(self, data: bytes) -> bytes:
        pass

class GzipCompression(CompressionStrategy):
    def compress(self, data: bytes) -> bytes:
        import gzip
        return gzip.compress(data)

class ZlibCompression(CompressionStrategy):
    def compress(self, data: bytes) -> bytes:
        import zlib
        return zlib.compress(data)

# Usage: Swap strategies at runtime
def save_file(data: bytes, strategy: CompressionStrategy):
    compressed = strategy.compress(data)
    # Save compressed data...
```

### Pattern 2: Template Method Pattern

```python
from abc import ABC, abstractmethod

class DataPipeline(ABC):
    """Abstract data pipeline with template method."""

    def run(self) -> None:
        """Template method defining pipeline steps."""
        data = self.load_data()
        processed = self.process_data(data)
        self.save_results(processed)

    @abstractmethod
    def load_data(self) -> Any:
        """Subclasses implement data loading."""
        pass

    @abstractmethod
    def process_data(self, data: Any) -> Any:
        """Subclasses implement processing logic."""
        pass

    def save_results(self, results: Any) -> None:
        """Default save implementation (can be overridden)."""
        print(f"Results: {results}")
```

---

## Summary Checklist

**When implementing Abstract Base Classes:**
- [ ] Inherit from `abc.ABC`
- [ ] Use `@abstractmethod` decorator for required methods
- [ ] Add defensive validation in base class `__init__`
- [ ] Document base class contract clearly (docstrings)
- [ ] Provide shared helper methods (non-abstract) for code reuse
- [ ] Subclasses MUST call `super().__init__()` first
- [ ] Subclasses MUST implement all abstract methods
- [ ] Type hint all methods (args and return types)
- [ ] Raise descriptive exceptions for validation failures
- [ ] Test that abstract class cannot be instantiated
- [ ] Test that subclass without implementation raises `TypeError`

---

## Related Patterns

- **TDD Workflow** (`patterns/tdd-workflow.md`) - Write tests for base class and each subclass
- **Defensive Function Template** (`CLAUDE.md`) - Apply 5-step pattern to `__init__` and abstract methods
- **ThreadPoolExecutor Parallel** (`patterns/threadpool-parallel.md`) - Process multiple implementations in parallel

---

## Further Reading

- Python `abc` module documentation: https://docs.python.org/3/library/abc.html
- Real-world example: `backend/ai_judge_framework.py:64-277`
- Design Patterns: Strategy, Template Method, Factory
- SOLID principles: Open/Closed Principle, Liskov Substitution Principle
- When NOT to use ABCs: YAGNI principle (You Ain't Gonna Need It)
