# GenAI Reliability Patterns Skill

## Overview

This skill provides systematic guidance for applying four foundational reliability patterns to GenAI codebases:

1. **LLM-as-Judge** — Systematic evaluation using LLMs with custom scoring rubrics
2. **Reflection** — Iterative self-critique and refinement loops
3. **Dependency Injection** — Mockable, testable LLM pipeline components
4. **Prompt Optimization** — Systematic prompt refinement across input distributions

These patterns address the core reliability challenges of GenAI systems: nondeterminism, inconsistency, hallucinations, and brittle prompts.

---

## When to Apply This Skill

Trigger this skill when:

- Building or refactoring GenAI pipelines with multiple LLM calls
- Implementing evaluation systems for LLM outputs
- Creating agentic workflows that require quality gates
- Setting up testing infrastructure for LLM-based applications
- Migrating between LLM providers or model versions
- Debugging inconsistent or low-quality LLM outputs

---

## Pattern 1: LLM-as-Judge

### Detection Heuristics

Apply LLM-as-Judge when you see:

- Manual "vibe checking" of outputs
- Hardcoded quality thresholds without justification
- Evaluation functions returning simple pass/fail without criteria
- Comments like `# TODO: add proper evaluation`
- RAG systems without relevance scoring
- Content generation without quality gates

### Implementation Strategy

#### Step 1: Define Structured Scoring Rubric

```python
from pydantic import BaseModel, Field
from typing import List

class EvaluationRubric(BaseModel):
    """Define explicit criteria with calibration anchors."""
    
    factual_accuracy: int = Field(
        ...,
        ge=1, le=5,
        description="""
        1: Contains fabricated information or misrepresents source
        3: Mostly accurate with minor omissions
        5: All statements grounded in provided context
        """
    )
    completeness: int = Field(
        ...,
        ge=1, le=5,
        description="""
        1: Missing critical information
        3: Covers main points adequately
        5: Comprehensive coverage with appropriate depth
        """
    )
    relevance: int = Field(
        ...,
        ge=1, le=5,
        description="""
        1: Off-topic or tangential
        3: Addresses query but includes unnecessary content
        5: Precisely addresses the query with no extraneous content
        """
    )
    justification: str = Field(
        ...,
        description="Brief explanation for each score"
    )
```

#### Step 2: Create Judge Function

```python
from typing import Protocol, TypeVar

T = TypeVar('T', bound=BaseModel)

class JudgeProtocol(Protocol[T]):
    """Protocol for judge implementations enabling DI."""
    
    def evaluate(self, content: str, context: str | None = None) -> T:
        ...

class LLMJudge:
    """Production judge implementation."""
    
    def __init__(
        self,
        model: str = "claude-sonnet-4-20250514",
        temperature: float = 0.0,  # Critical for consistency
        rubric_class: type[BaseModel] = EvaluationRubric
    ):
        self.model = model
        self.temperature = temperature
        self.rubric_class = rubric_class
    
    def evaluate(self, content: str, context: str | None = None) -> BaseModel:
        prompt = self._build_evaluation_prompt(content, context)
        # Use structured output to ensure schema compliance
        response = self._call_llm_structured(prompt, self.rubric_class)
        return response
    
    def _build_evaluation_prompt(self, content: str, context: str | None) -> str:
        return f"""Evaluate the following content against the scoring rubric.
        
{"**Context**:" + context if context else ""}

**Content to Evaluate**:
{content}

Provide scores with calibrated justifications. Be rigorous—avoid leniency bias.
Compare against what an ideal response would contain."""
```

#### Step 3: Address Common Biases

```python
class BiasAwareLLMJudge(LLMJudge):
    """Judge with bias mitigation strategies."""
    
    def __init__(self, *args, use_different_model: bool = True, **kwargs):
        super().__init__(*args, **kwargs)
        # Mitigate self-bias by using different model for evaluation
        if use_different_model:
            self.model = self._select_alternative_model()
    
    def evaluate_pairwise(
        self, 
        content_a: str, 
        content_b: str,
        randomize_order: bool = True  # Mitigate position bias
    ) -> dict:
        """Pairwise comparison reduces leniency bias."""
        if randomize_order and random.random() > 0.5:
            content_a, content_b = content_b, content_a
            swapped = True
        else:
            swapped = False
        
        result = self._compare(content_a, content_b)
        
        if swapped:
            result = self._swap_result(result)
        return result
    
    def evaluate_with_polling(
        self,
        content: str,
        num_judges: int = 3,
        models: list[str] | None = None
    ) -> dict:
        """LLM-as-jury approach for high-stakes evaluations."""
        models = models or ["claude-sonnet-4-20250514", "gpt-4o", "gemini-2.0-flash"]
        
        scores = []
        for model in models[:num_judges]:
            judge = LLMJudge(model=model)
            scores.append(judge.evaluate(content))
        
        return self._aggregate_scores(scores)
```

### Anti-Patterns to Avoid

```python
# ❌ WRONG: Single aggregate score without criteria
def bad_evaluate(content: str) -> float:
    return llm.call(f"Rate this 1-10: {content}")

# ❌ WRONG: Fine-grained scores increase inconsistency
class BadRubric(BaseModel):
    score: int = Field(ge=1, le=100)  # Too granular

# ❌ WRONG: Same model evaluating its own output (self-bias)
def bad_self_evaluate(content: str, generator_model: str) -> float:
    return LLMJudge(model=generator_model).evaluate(content)

# ✅ CORRECT: Coarse scores (1-5), multiple criteria, different evaluator model
```

---

## Pattern 2: Reflection

### Detection Heuristics

Apply Reflection when you see:

- Single-shot LLM calls for complex tasks
- High error rates in generated content
- User feedback loops that could be automated
- Code generation without validation
- Content that requires iterative refinement
- Agentic workflows without quality gates

### Implementation Strategy

#### Step 1: Define Reflection Loop Structure

```python
from dataclasses import dataclass
from typing import Callable, Generic, TypeVar

T = TypeVar('T')

@dataclass
class ReflectionResult(Generic[T]):
    """Container for reflection loop output."""
    final_output: T
    iterations: int
    critiques: list[str]
    scores: list[float]
    converged: bool

class ReflectionLoop(Generic[T]):
    """Generic reflection loop with configurable components."""
    
    def __init__(
        self,
        generator: Callable[[str], T],
        evaluator: Callable[[T], tuple[float, str]],  # (score, critique)
        refiner: Callable[[T, str], str],  # (output, critique) -> new_prompt
        max_iterations: int = 3,
        score_threshold: float = 0.8,
        use_best_of_n: bool = False,  # Alternative: generate N, pick best
        n_candidates: int = 3
    ):
        self.generator = generator
        self.evaluator = evaluator
        self.refiner = refiner
        self.max_iterations = max_iterations
        self.score_threshold = score_threshold
        self.use_best_of_n = use_best_of_n
        self.n_candidates = n_candidates
    
    def run(self, initial_prompt: str) -> ReflectionResult[T]:
        critiques = []
        scores = []
        current_prompt = initial_prompt
        
        for iteration in range(self.max_iterations):
            # Generate
            if self.use_best_of_n:
                output = self._generate_best_of_n(current_prompt)
            else:
                output = self.generator(current_prompt)
            
            # Evaluate
            score, critique = self.evaluator(output)
            scores.append(score)
            critiques.append(critique)
            
            # Check convergence
            if score >= self.score_threshold:
                return ReflectionResult(
                    final_output=output,
                    iterations=iteration + 1,
                    critiques=critiques,
                    scores=scores,
                    converged=True
                )
            
            # Refine prompt for next iteration
            current_prompt = self.refiner(output, critique)
        
        # Return best attempt if didn't converge
        best_idx = scores.index(max(scores))
        return ReflectionResult(
            final_output=output,  # Last output (could track all)
            iterations=self.max_iterations,
            critiques=critiques,
            scores=scores,
            converged=False
        )
    
    def _generate_best_of_n(self, prompt: str) -> T:
        candidates = [self.generator(prompt) for _ in range(self.n_candidates)]
        scored = [(c, self.evaluator(c)[0]) for c in candidates]
        return max(scored, key=lambda x: x[1])[0]
```

#### Step 2: Implement Domain-Specific Reflection

```python
class CodeReflectionLoop:
    """Specialized reflection for code generation."""
    
    def __init__(self, llm_client, sandbox_executor):
        self.llm = llm_client
        self.sandbox = sandbox_executor
    
    def generate_with_reflection(
        self,
        task: str,
        test_cases: list[dict] | None = None
    ) -> ReflectionResult[str]:
        
        def generator(prompt: str) -> str:
            return self.llm.generate(prompt)
        
        def evaluator(code: str) -> tuple[float, str]:
            critiques = []
            score = 1.0
            
            # Syntax check
            syntax_result = self._check_syntax(code)
            if not syntax_result.valid:
                critiques.append(f"Syntax error: {syntax_result.error}")
                score -= 0.3
            
            # Execution check
            if test_cases:
                exec_result = self.sandbox.run(code, test_cases)
                if not exec_result.all_passed:
                    critiques.append(f"Failed tests: {exec_result.failures}")
                    score -= 0.2 * len(exec_result.failures)
            
            # Style/quality check via LLM
            quality = self._llm_quality_check(code)
            critiques.append(quality.feedback)
            score -= (1 - quality.score) * 0.2
            
            return max(0, score), "\n".join(critiques)
        
        def refiner(code: str, critique: str) -> str:
            return f"""The following code has issues:

```python
{code}
```

**Issues identified**:
{critique}

Please fix these issues and return corrected code."""
        
        loop = ReflectionLoop(
            generator=generator,
            evaluator=evaluator,
            refiner=refiner,
            max_iterations=3,
            score_threshold=0.9
        )
        
        return loop.run(task)
```

#### Step 3: Conversational Reflection Pattern

```python
class ConversationalReflection:
    """Reflection using conversation history for multi-agent systems."""
    
    def __init__(self, agents: dict[str, Agent]):
        self.agents = agents
        self.conversation_history: list[Message] = []
    
    async def reflect_with_critic(
        self,
        task: str,
        generator_role: str = "generator",
        critic_role: str = "critic"
    ) -> str:
        generator = self.agents[generator_role]
        critic = self.agents[critic_role]
        
        # Initial generation
        response = await generator.run(task)
        self.conversation_history.append(
            Message(role=generator_role, content=response)
        )
        
        for _ in range(self.max_iterations):
            # Critic reviews with full history
            critique = await critic.run(
                f"Review this response: {response}",
                history=self.conversation_history
            )
            self.conversation_history.append(
                Message(role=critic_role, content=critique)
            )
            
            if self._is_approved(critique):
                break
            
            # Generator improves based on critique
            response = await generator.run(
                f"Improve based on feedback: {critique}",
                history=self.conversation_history
            )
            self.conversation_history.append(
                Message(role=generator_role, content=response)
            )
        
        return response
```

### Anti-Patterns to Avoid

```python
# ❌ WRONG: No maximum iterations (infinite loop risk)
while score < threshold:
    output = generate(prompt)
    score = evaluate(output)

# ❌ WRONG: Same model for generation and critique (self-bias)
critique = generator_model.call(f"Critique your response: {response}")

# ❌ WRONG: Not preserving critique history
for i in range(max_iter):
    output = generate(prompt)  # Loses context from previous critiques

# ✅ CORRECT: Bounded iterations, different critic, cumulative context
```

---

## Pattern 3: Dependency Injection

### Detection Heuristics

Apply Dependency Injection when you see:

- LLM calls hardcoded inside business logic
- Tests that make real API calls
- Difficulty testing individual pipeline steps
- Monolithic functions combining multiple LLM operations
- No way to swap models without code changes
- Flaky tests due to LLM nondeterminism

### Implementation Strategy

#### Step 1: Define Protocols/Interfaces

```python
from typing import Protocol, TypeVar, Generic
from abc import ABC, abstractmethod

T_Input = TypeVar('T_Input')
T_Output = TypeVar('T_Output')

class LLMProvider(Protocol):
    """Protocol for LLM providers enabling swappable backends."""
    
    def complete(self, prompt: str, **kwargs) -> str:
        ...
    
    def complete_structured(
        self, 
        prompt: str, 
        response_model: type[BaseModel],
        **kwargs
    ) -> BaseModel:
        ...

class PipelineStep(Protocol[T_Input, T_Output]):
    """Protocol for pipeline steps enabling mocking."""
    
    def __call__(self, input: T_Input) -> T_Output:
        ...

class EvaluatorProtocol(Protocol):
    """Protocol for evaluators enabling test doubles."""
    
    def evaluate(self, content: str) -> float:
        ...
```

#### Step 2: Implement Injectable Pipeline

```python
from dataclasses import dataclass, field
from typing import Callable

@dataclass
class PipelineConfig:
    """Configuration for injectable pipeline components."""
    llm_provider: LLMProvider
    evaluator: EvaluatorProtocol
    tools: dict[str, Callable] = field(default_factory=dict)

class InjectablePipeline:
    """Pipeline with fully injectable dependencies."""
    
    def __init__(
        self,
        config: PipelineConfig,
        # Allow injection of individual steps
        extract_fn: PipelineStep | None = None,
        transform_fn: PipelineStep | None = None,
        validate_fn: PipelineStep | None = None
    ):
        self.config = config
        self.extract = extract_fn or self._default_extract
        self.transform = transform_fn or self._default_transform
        self.validate = validate_fn or self._default_validate
    
    def run(self, input_data: str) -> PipelineResult:
        # Each step can be independently mocked
        extracted = self.extract(input_data)
        transformed = self.transform(extracted)
        validated = self.validate(transformed)
        return validated
    
    def _default_extract(self, data: str) -> ExtractedData:
        return self.config.llm_provider.complete_structured(
            f"Extract structured data from: {data}",
            response_model=ExtractedData
        )
    
    # ... other default implementations

# Factory for different environments
class PipelineFactory:
    """Factory for creating pipelines with appropriate dependencies."""
    
    @staticmethod
    def create_production() -> InjectablePipeline:
        return InjectablePipeline(
            config=PipelineConfig(
                llm_provider=AnthropicProvider(model="claude-sonnet-4-20250514"),
                evaluator=LLMJudge()
            )
        )
    
    @staticmethod
    def create_testing() -> InjectablePipeline:
        return InjectablePipeline(
            config=PipelineConfig(
                llm_provider=MockLLMProvider(),
                evaluator=MockEvaluator()
            )
        )
    
    @staticmethod
    def create_with_mocked_step(
        step_name: str,
        mock_fn: Callable
    ) -> InjectablePipeline:
        """Create pipeline with single step mocked."""
        kwargs = {f"{step_name}_fn": mock_fn}
        return InjectablePipeline(
            config=PipelineConfig(
                llm_provider=AnthropicProvider(),
                evaluator=LLMJudge()
            ),
            **kwargs
        )
```

#### Step 3: Create Test Doubles

```python
class MockLLMProvider:
    """Mock LLM for deterministic testing."""
    
    def __init__(self, responses: dict[str, str] | None = None):
        self.responses = responses or {}
        self.call_history: list[str] = []
    
    def complete(self, prompt: str, **kwargs) -> str:
        self.call_history.append(prompt)
        
        # Return canned response if available
        for pattern, response in self.responses.items():
            if pattern in prompt:
                return response
        
        # Default response
        return "Mock response for testing"
    
    def complete_structured(
        self, 
        prompt: str, 
        response_model: type[BaseModel],
        **kwargs
    ) -> BaseModel:
        self.call_history.append(prompt)
        # Return valid instance with default values
        return self._create_default_instance(response_model)

class RecordingLLMProvider:
    """Wrapper that records calls for replay testing."""
    
    def __init__(self, real_provider: LLMProvider, record_path: str):
        self.real_provider = real_provider
        self.record_path = record_path
        self.recordings: list[dict] = []
    
    def complete(self, prompt: str, **kwargs) -> str:
        response = self.real_provider.complete(prompt, **kwargs)
        self.recordings.append({
            "prompt": prompt,
            "response": response,
            "kwargs": kwargs
        })
        return response
    
    def save_recordings(self):
        with open(self.record_path, 'w') as f:
            json.dump(self.recordings, f)

class ReplayLLMProvider:
    """Replay recorded LLM responses for deterministic tests."""
    
    def __init__(self, record_path: str):
        with open(record_path) as f:
            self.recordings = json.load(f)
        self.replay_index = 0
    
    def complete(self, prompt: str, **kwargs) -> str:
        if self.replay_index >= len(self.recordings):
            raise ValueError("Replay exhausted")
        
        recording = self.recordings[self.replay_index]
        self.replay_index += 1
        
        # Optionally verify prompt matches
        assert prompt == recording["prompt"], "Prompt mismatch in replay"
        return recording["response"]
```

#### Step 4: Write Testable Tests

```python
import pytest

class TestPipelineWithDI:
    """Test suite demonstrating DI patterns."""
    
    def test_extraction_step_isolation(self):
        """Test extraction step independently."""
        mock_llm = MockLLMProvider(responses={
            "Extract": '{"field1": "value1", "field2": "value2"}'
        })
        
        pipeline = PipelineFactory.create_testing()
        pipeline.config.llm_provider = mock_llm
        
        result = pipeline.extract("test input")
        
        assert result.field1 == "value1"
        assert len(mock_llm.call_history) == 1
    
    def test_transform_with_mocked_extraction(self):
        """Test transform step with mocked predecessor."""
        mock_extract = lambda x: ExtractedData(field1="test", field2="data")
        
        pipeline = PipelineFactory.create_with_mocked_step(
            "extract", mock_extract
        )
        
        result = pipeline.run("any input")
        
        # Transform step uses real LLM but extraction is mocked
        assert result is not None
    
    def test_deterministic_with_replay(self):
        """Use recorded responses for deterministic testing."""
        replay_provider = ReplayLLMProvider("fixtures/recorded_calls.json")
        
        pipeline = InjectablePipeline(
            config=PipelineConfig(
                llm_provider=replay_provider,
                evaluator=MockEvaluator(fixed_score=0.9)
            )
        )
        
        result = pipeline.run("test input")
        
        # Results are deterministic from recorded responses
        assert result.confidence > 0.8
    
    @pytest.mark.integration
    def test_full_pipeline_integration(self):
        """Integration test with real LLM (marked for selective running)."""
        pipeline = PipelineFactory.create_production()
        result = pipeline.run("real test input")
        assert_pipeline_result(result)
```

### Anti-Patterns to Avoid

```python
# ❌ WRONG: Hardcoded LLM client inside function
def process_data(data: str) -> str:
    client = anthropic.Anthropic()  # Hardcoded, untestable
    return client.messages.create(...)

# ❌ WRONG: Global state for configuration
LLM_MODEL = "claude-sonnet-4-20250514"  # Can't swap for tests

def process(data):
    return call_llm(LLM_MODEL, data)

# ❌ WRONG: Tests that hit real APIs
def test_extraction():
    result = extract_with_real_llm("test")  # Slow, flaky, costly
    assert result is not None

# ✅ CORRECT: Injectable dependencies, mockable interfaces, factory pattern
```

---

## Pattern 4: Prompt Optimization

### Detection Heuristics

Apply Prompt Optimization when you see:

- Prompts embedded as string literals in code
- Frequent prompt tweaking after model updates
- Inconsistent output quality across input variations
- Manual A/B testing of prompt variations
- Comments like `# This prompt works better for some reason`
- Prompts with magic numbers or unexplained instructions

### Implementation Strategy

#### Step 1: Externalize Prompts with Metadata

```python
from dataclasses import dataclass, field
from typing import Any
import yaml

@dataclass
class PromptTemplate:
    """Versioned, optimizable prompt template."""
    
    name: str
    template: str
    version: str
    variables: list[str]
    metadata: dict[str, Any] = field(default_factory=dict)
    performance_history: list[dict] = field(default_factory=list)
    
    def render(self, **kwargs) -> str:
        return self.template.format(**kwargs)
    
    def record_performance(self, score: float, input_hash: str):
        self.performance_history.append({
            "score": score,
            "input_hash": input_hash,
            "timestamp": datetime.now().isoformat()
        })

class PromptRegistry:
    """Central registry for prompt management."""
    
    def __init__(self, config_path: str = "prompts.yaml"):
        self.config_path = config_path
        self.prompts: dict[str, PromptTemplate] = {}
        self._load_prompts()
    
    def _load_prompts(self):
        with open(self.config_path) as f:
            config = yaml.safe_load(f)
        
        for name, data in config["prompts"].items():
            self.prompts[name] = PromptTemplate(
                name=name,
                template=data["template"],
                version=data.get("version", "1.0.0"),
                variables=data.get("variables", []),
                metadata=data.get("metadata", {})
            )
    
    def get(self, name: str) -> PromptTemplate:
        return self.prompts[name]
    
    def update(self, name: str, new_template: str, new_version: str):
        """Update prompt with new version."""
        old = self.prompts[name]
        self.prompts[name] = PromptTemplate(
            name=name,
            template=new_template,
            version=new_version,
            variables=old.variables,
            metadata=old.metadata,
            performance_history=old.performance_history
        )
        self._save_prompts()
```

#### Step 2: Implement DSPy-Style Optimization

```python
class PromptOptimizer:
    """Systematic prompt optimization framework."""
    
    def __init__(
        self,
        llm_provider: LLMProvider,
        evaluator: EvaluatorProtocol,
        optimization_strategy: str = "few_shot_bootstrap"
    ):
        self.llm = llm_provider
        self.evaluator = evaluator
        self.strategy = optimization_strategy
    
    def optimize(
        self,
        base_prompt: PromptTemplate,
        dataset: list[dict],  # List of {input: ..., expected: ...}
        num_iterations: int = 10
    ) -> PromptTemplate:
        """Optimize prompt on dataset."""
        
        if self.strategy == "best_of_n":
            return self._best_of_n_optimize(base_prompt, dataset, num_iterations)
        elif self.strategy == "few_shot_bootstrap":
            return self._bootstrap_optimize(base_prompt, dataset)
        elif self.strategy == "instruction_evolution":
            return self._evolve_instructions(base_prompt, dataset, num_iterations)
        else:
            raise ValueError(f"Unknown strategy: {self.strategy}")
    
    def _best_of_n_optimize(
        self,
        base_prompt: PromptTemplate,
        dataset: list[dict],
        n: int
    ) -> PromptTemplate:
        """Generate N variations, evaluate, return best."""
        
        variations = [base_prompt]
        
        # Generate variations
        for _ in range(n - 1):
            variation = self._generate_variation(base_prompt)
            variations.append(variation)
        
        # Evaluate each on dataset
        scores = []
        for prompt in variations:
            total_score = 0
            for example in dataset:
                output = self.llm.complete(
                    prompt.render(**example["input"])
                )
                score = self.evaluator.evaluate(output, example.get("expected"))
                total_score += score
            scores.append(total_score / len(dataset))
        
        # Return best performing
        best_idx = scores.index(max(scores))
        return variations[best_idx]
    
    def _bootstrap_optimize(
        self,
        base_prompt: PromptTemplate,
        dataset: list[dict]
    ) -> PromptTemplate:
        """Few-shot bootstrap optimization (DSPy-style)."""
        
        # Split dataset
        train_set = dataset[:int(len(dataset) * 0.7)]
        eval_set = dataset[int(len(dataset) * 0.7):]
        
        best_examples = []
        best_score = 0
        
        # Try different example combinations
        for _ in range(10):  # Number of bootstrap iterations
            # Sample examples for few-shot
            sampled = random.sample(train_set, min(3, len(train_set)))
            
            # Create few-shot prompt
            few_shot_prompt = self._add_examples_to_prompt(
                base_prompt, sampled
            )
            
            # Evaluate on held-out set
            score = self._evaluate_on_dataset(few_shot_prompt, eval_set)
            
            if score > best_score:
                best_score = score
                best_examples = sampled
        
        return self._add_examples_to_prompt(base_prompt, best_examples)
    
    def _evolve_instructions(
        self,
        base_prompt: PromptTemplate,
        dataset: list[dict],
        num_iterations: int
    ) -> PromptTemplate:
        """Evolutionary optimization of prompt instructions."""
        
        current_prompt = base_prompt
        current_score = self._evaluate_on_dataset(current_prompt, dataset)
        
        for _ in range(num_iterations):
            # Generate mutation
            mutated = self._mutate_prompt(current_prompt)
            mutated_score = self._evaluate_on_dataset(mutated, dataset)
            
            # Keep if better (greedy)
            if mutated_score > current_score:
                current_prompt = mutated
                current_score = mutated_score
        
        return current_prompt
    
    def _generate_variation(self, prompt: PromptTemplate) -> PromptTemplate:
        """Use LLM to generate prompt variation."""
        
        variation_prompt = f"""Generate a variation of this prompt that might perform better.
Keep the same variables: {prompt.variables}
Maintain the same intent but try different:
- Instruction phrasing
- Example formatting
- Constraint specification

Original prompt:
{prompt.template}

New variation:"""
        
        new_template = self.llm.complete(variation_prompt)
        
        return PromptTemplate(
            name=f"{prompt.name}_variation",
            template=new_template,
            version=f"{prompt.version}-var",
            variables=prompt.variables
        )
```

#### Step 3: Integrate with CI/CD

```python
class PromptOptimizationPipeline:
    """CI/CD integration for prompt optimization."""
    
    def __init__(
        self,
        registry: PromptRegistry,
        optimizer: PromptOptimizer,
        dataset_path: str,
        performance_threshold: float = 0.8
    ):
        self.registry = registry
        self.optimizer = optimizer
        self.dataset = self._load_dataset(dataset_path)
        self.threshold = performance_threshold
    
    def run_optimization_check(self) -> dict:
        """Run as part of CI/CD when model version changes."""
        
        results = {}
        
        for name, prompt in self.registry.prompts.items():
            # Evaluate current prompt
            current_score = self._evaluate_prompt(prompt)
            
            if current_score < self.threshold:
                # Optimize underperforming prompts
                optimized = self.optimizer.optimize(
                    prompt, 
                    self.dataset,
                    num_iterations=20
                )
                optimized_score = self._evaluate_prompt(optimized)
                
                results[name] = {
                    "original_score": current_score,
                    "optimized_score": optimized_score,
                    "improved": optimized_score > current_score,
                    "new_prompt": optimized if optimized_score > current_score else None
                }
            else:
                results[name] = {
                    "original_score": current_score,
                    "status": "above_threshold"
                }
        
        return results
    
    def auto_update_prompts(self, results: dict):
        """Automatically update prompts that improved."""
        
        for name, result in results.items():
            if result.get("improved") and result.get("new_prompt"):
                new_prompt = result["new_prompt"]
                self.registry.update(
                    name,
                    new_prompt.template,
                    self._increment_version(new_prompt.version)
                )
                
                print(f"Updated {name}: {result['original_score']:.2f} -> {result['optimized_score']:.2f}")
```

### Anti-Patterns to Avoid

```python
# ❌ WRONG: Hardcoded prompts scattered in code
def analyze(text):
    return llm.call(f"Analyze this text and identify key themes: {text}")

# ❌ WRONG: Manual prompt versioning via comments
# v3 - added "step by step" - seems to work better
PROMPT = "Think step by step and analyze..."

# ❌ WRONG: No evaluation dataset
def optimize_prompt(prompt):
    return llm.call(f"Make this prompt better: {prompt}")  # No objective measure

# ✅ CORRECT: Externalized prompts, systematic optimization, evaluation dataset
```

---

## Integration Checklist

When applying these patterns to a codebase:

### Initial Assessment

- [ ] Identify all LLM call sites in the codebase
- [ ] Map data flow between LLM calls (pipeline structure)
- [ ] Inventory existing evaluation mechanisms
- [ ] Document current prompt management approach
- [ ] Identify testing gaps for LLM components

### Pattern Application Order

1. **Dependency Injection** (Foundation)
   - Refactor LLM calls to use injectable providers
   - Create protocol/interface definitions
   - Implement mock providers for testing

2. **LLM-as-Judge** (Evaluation)
   - Define domain-specific scoring rubrics
   - Implement judge classes with bias mitigation
   - Create evaluation datasets

3. **Reflection** (Quality)
   - Identify steps that benefit from iteration
   - Implement reflection loops with max iterations
   - Connect evaluators to reflection feedback

4. **Prompt Optimization** (Maintenance)
   - Externalize prompts to registry
   - Set up optimization pipeline
   - Integrate with CI/CD for model updates

### Validation

- [ ] All LLM calls are mockable
- [ ] Tests run without real API calls (unit tests)
- [ ] Integration tests are marked and run separately
- [ ] Evaluation metrics are defined and tracked
- [ ] Prompts are versioned and optimizable
- [ ] Reflection loops have bounded iterations

---

## Framework-Specific Notes

### DSPy

```python
# DSPy native signatures map directly to these patterns
import dspy

class MySignature(dspy.Signature):
    """DSPy handles structured I/O natively."""
    input_text: str = dspy.InputField()
    output: MyOutputClass = dspy.OutputField()

# Use dspy.ChainOfThought for reflection-like behavior
# Use dspy.BootstrapFewShot for prompt optimization
```

### LangChain/LangGraph

```python
# Use RunnablePassthrough for DI-friendly chains
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

# Inject evaluator as a step
chain = (
    RunnablePassthrough()
    | generate_step
    | RunnableLambda(lambda x: evaluator.evaluate(x))
    | conditional_retry
)
```

### PydanticAI

```python
# PydanticAI agents support dependency injection natively
from pydantic_ai import Agent

agent = Agent(
    model,
    deps_type=MyDependencies,  # Injectable dependencies
    result_type=MyResult       # Structured output
)
```

---

## Performance Considerations

| Pattern | Latency Impact | Cost Impact | When to Skip |
|---------|---------------|-------------|--------------|
| LLM-as-Judge | +1 LLM call | +50-100% | Low-stakes outputs |
| Reflection | +N LLM calls | +100-300% | Real-time requirements |
| Dependency Injection | Minimal | None | Prototype/POC stage |
| Prompt Optimization | Build-time only | Build-time cost | Stable prompts |

---

## References

- Bai et al. (2023) - Language-Model-as-an-Examiner
- Shinn et al. (2023) - Reflexion: Language Agents with Verbal Reinforcement Learning
- Madaan et al. (2023) - Self-Refine: Iterative Refinement with Self-Feedback
- Khattab et al. (2023) - DSPy: Compiling Declarative Language Model Calls
- Fowler (2024) - Dependency Injection patterns
