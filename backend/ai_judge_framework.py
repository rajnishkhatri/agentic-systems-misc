"""
AI Judge Framework: Reusable abstractions for LLM-based evaluation.

This module provides:
- JudgeResult: Pydantic model for structured judge outputs
- BaseJudge: Abstract base class for all judges
- DietaryAdherenceJudge: Evaluates dietary restriction compliance
- SubstantiationJudge: Detects unsubstantiated claims
- GenericCriteriaJudge: Flexible judge for custom criteria
- Utility functions: TPR/TNR calculation, batch processing

All code follows defensive programming:
- Type hints on all functions
- Input validation with descriptive errors
- Proper error handling with retries
- Async support for batch operations
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Any, Optional
import json
import asyncio
from concurrent.futures import ThreadPoolExecutor
from pydantic import BaseModel, Field, field_validator
from tenacity import retry, stop_after_attempt, wait_exponential
import litellm  # type: ignore


# ============================================================================
# Pydantic Models
# ============================================================================


class JudgeResult(BaseModel):
    """Structured output from a judge evaluation.

    Attributes:
        score: Binary (PASS/FAIL) or numeric (1-5) score
        reasoning: Detailed explanation of the judgment
        confidence: Judge's confidence in the decision (0.0-1.0)
    """

    score: str | int = Field(..., description="PASS/FAIL or numeric score 1-5")
    reasoning: str = Field(..., min_length=1, description="Explanation of judgment")
    confidence: float = Field(
        default=1.0, ge=0.0, le=1.0, description="Confidence score"
    )

    @field_validator("reasoning")
    @classmethod
    def reasoning_not_empty(cls, v: str) -> str:
        """Validate that reasoning is not empty."""
        if not v or not v.strip():
            raise ValueError("reasoning cannot be empty")
        return v


# ============================================================================
# Base Judge Abstract Class
# ============================================================================


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

    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """Parse JSON from LLM response with error handling.

        Args:
            response: Raw LLM response

        Returns:
            Parsed JSON as dictionary

        Raises:
            ValueError: If response is not valid JSON
        """
        # Handle responses wrapped in markdown code blocks
        if "```json" in response:
            json_start = response.find("```json") + 7
            json_end = response.find("```", json_start)
            json_text = response[json_start:json_end].strip()
        elif "{" in response and "}" in response:
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            json_text = response[json_start:json_end]
        else:
            json_text = response

        try:
            return json.loads(json_text)
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Failed to parse JSON response: {e}. Response: {response[:200]}"
            )

    def _validate_inputs(self, **kwargs: Any) -> None:
        """Validate common inputs (query, response).

        Args:
            **kwargs: Input parameters to validate

        Raises:
            ValueError: If inputs are empty or invalid
        """
        if "query" in kwargs and not kwargs["query"].strip():
            raise ValueError("query cannot be empty")

        if "response" in kwargs and not kwargs["response"].strip():
            raise ValueError("response cannot be empty")

    @abstractmethod
    def evaluate(self, **kwargs: Any) -> JudgeResult:
        """Evaluate a single query-response pair.

        Must be implemented by subclasses.

        Args:
            **kwargs: Evaluation parameters (query, response, context, etc.)

        Returns:
            JudgeResult with score and reasoning
        """
        pass

    async def evaluate_batch(
        self, examples: List[Dict[str, Any]], max_workers: int = 50
    ) -> List[JudgeResult]:
        """Evaluate multiple examples in parallel.

        Args:
            examples: List of dicts with evaluation parameters
            max_workers: Maximum concurrent evaluations

        Returns:
            List of JudgeResults (same order as examples)

        Raises:
            ValueError: If examples list is empty
        """
        if not examples:
            raise ValueError("examples list cannot be empty")

        # Use ThreadPoolExecutor for parallel evaluation
        def evaluate_single(example: Dict[str, Any]) -> JudgeResult:
            try:
                return self.evaluate(**example)
            except Exception as e:
                # Return error result instead of failing entire batch
                return JudgeResult(
                    score="ERROR",
                    reasoning=f"Evaluation failed: {str(e)}",
                    confidence=0.0,
                )

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(evaluate_single, ex) for ex in examples]
            results = [f.result() for f in futures]

        return results


# ============================================================================
# Concrete Judge Implementations
# ============================================================================


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
        super().__init__(model, temperature)
        self.prompt_template = self._load_template("dietary_adherence_judge.txt")

    def evaluate(
        self, query: str, response: str, dietary_restriction: str
    ) -> JudgeResult:
        """Evaluate dietary adherence.

        Args:
            query: User's recipe query
            response: Recipe response to evaluate
            dietary_restriction: Dietary restriction to check (e.g., "vegan")

        Returns:
            JudgeResult with PASS/FAIL score

        Raises:
            ValueError: If inputs are invalid
        """
        # Input validation
        self._validate_inputs(query=query, response=response)
        if not dietary_restriction.strip():
            raise ValueError("dietary_restriction cannot be empty")

        # Format prompt
        prompt = self.prompt_template.replace("{query}", query)
        prompt = prompt.replace("{dietary_restriction}", dietary_restriction)
        prompt = prompt.replace("{response}", response)

        # Call LLM and parse response
        raw_response = self._call_llm(prompt)
        parsed = self._parse_json_response(raw_response)

        # Convert to JudgeResult
        return JudgeResult(
            score=parsed.get("answer", "ERROR"),
            reasoning=parsed.get("reasoning", "No reasoning provided"),
            confidence=1.0,
        )


class SubstantiationJudge(BaseJudge):
    """Judge for detecting unsubstantiated claims.

    Verifies that all factual claims in responses are supported by
    provided context (tool outputs, metadata, or common knowledge).
    """

    def __init__(self, model: str, temperature: float = 0.0):
        """Initialize substantiation judge.

        Args:
            model: LLM model name
            temperature: Sampling temperature
        """
        super().__init__(model, temperature)
        self.prompt_template = self._load_template("substantiation_judge.txt")

    def evaluate(
        self, query: str, response: str, context: Dict[str, Any] | None = None
    ) -> JudgeResult:
        """Evaluate substantiation of claims.

        Args:
            query: User's query
            response: Response to evaluate
            context: Tool outputs or metadata for verification

        Returns:
            JudgeResult with PASS (substantiated) or FAIL (hallucination)

        Raises:
            ValueError: If inputs are invalid
        """
        # Input validation
        self._validate_inputs(query=query, response=response)

        # Format context
        context_str = json.dumps(context, indent=2) if context else "{}"

        # Format prompt
        prompt = self.prompt_template.replace("{context}", context_str)
        prompt = prompt.replace("{query}", query)
        prompt = prompt.replace("{response}", response)

        # Call LLM and parse response
        raw_response = self._call_llm(prompt)
        parsed = self._parse_json_response(raw_response)

        # Convert to JudgeResult
        return JudgeResult(
            score=parsed.get("answer", "ERROR"),
            reasoning=parsed.get("reasoning", "No reasoning provided"),
            confidence=1.0,
        )


class GenericCriteriaJudge(BaseJudge):
    """Flexible judge for custom evaluation criteria.

    Dynamically builds prompts based on provided criteria (helpfulness,
    coherence, toxicity, creativity, etc.).
    """

    def __init__(
        self,
        model: str,
        criteria: str,
        criteria_description: str,
        temperature: float = 0.0,
    ):
        """Initialize generic criteria judge.

        Args:
            model: LLM model name
            criteria: Criterion name (e.g., "helpfulness", "coherence")
            criteria_description: Detailed description of the criterion
            temperature: Sampling temperature

        Raises:
            ValueError: If criteria or description is empty
        """
        super().__init__(model, temperature)

        if not criteria.strip():
            raise ValueError("criteria cannot be empty")
        if not criteria_description.strip():
            raise ValueError("criteria_description cannot be empty")

        self.criteria = criteria
        self.criteria_description = criteria_description

    def _build_prompt(self, query: str, response: str) -> str:
        """Build evaluation prompt dynamically from criteria.

        Args:
            query: User's query
            response: Response to evaluate

        Returns:
            Formatted prompt string
        """
        prompt = f"""You are an expert evaluator assessing responses based on: {self.criteria}

CRITERIA DEFINITION:
{self.criteria_description}

EVALUATION TASK:
Evaluate whether the following response meets the criterion.

Query: {query}
Response: {response}

Provide your evaluation in JSON format:
{{
    "reasoning": "Detailed explanation of your assessment",
    "answer": "PASS" or "FAIL"
}}
"""
        return prompt

    def evaluate(self, query: str, response: str, **kwargs: Any) -> JudgeResult:
        """Evaluate response against custom criteria.

        Args:
            query: User's query
            response: Response to evaluate
            **kwargs: Additional context (optional)

        Returns:
            JudgeResult with PASS/FAIL score

        Raises:
            ValueError: If inputs are invalid
        """
        # Input validation
        self._validate_inputs(query=query, response=response)

        # Build prompt
        prompt = self._build_prompt(query, response)

        # Call LLM and parse response
        raw_response = self._call_llm(prompt)
        parsed = self._parse_json_response(raw_response)

        # Convert to JudgeResult
        return JudgeResult(
            score=parsed.get("answer", "ERROR"),
            reasoning=parsed.get("reasoning", "No reasoning provided"),
            confidence=1.0,
        )


# ============================================================================
# Utility Functions: TPR/TNR Calculations
# ============================================================================


def calculate_tpr_tnr(y_true: List[bool], y_pred: List[bool]) -> tuple[float, float]:
    """Calculate True Positive Rate (TPR) and True Negative Rate (TNR).

    TPR (Recall/Sensitivity):
        Percentage of actual failures correctly identified by judge.
        TPR = TP / (TP + FN)

    TNR (Specificity):
        Percentage of actual successes correctly identified by judge.
        TNR = TN / (TN + FP)

    Args:
        y_true: Ground truth labels (True = PASS, False = FAIL)
        y_pred: Judge predictions (True = PASS, False = FAIL)

    Returns:
        Tuple of (TPR, TNR)

    Raises:
        ValueError: If lists have different lengths or are empty
    """
    # Input validation
    if not y_true or not y_pred:
        raise ValueError("y_true and y_pred cannot be empty")
    if len(y_true) != len(y_pred):
        raise ValueError("y_true and y_pred must have same length")

    # Calculate confusion matrix components
    tp = sum(
        1 for true, pred in zip(y_true, y_pred) if not true and not pred
    )  # True failures correctly identified
    fn = sum(
        1 for true, pred in zip(y_true, y_pred) if not true and pred
    )  # True failures missed
    tn = sum(
        1 for true, pred in zip(y_true, y_pred) if true and pred
    )  # True successes correctly identified
    fp = sum(
        1 for true, pred in zip(y_true, y_pred) if true and not pred
    )  # False alarms

    # Calculate TPR and TNR with edge case handling
    tpr = tp / (tp + fn) if (tp + fn) > 0 else 1.0  # No failures -> perfect TPR
    tnr = tn / (tn + fp) if (tn + fp) > 0 else 1.0  # No successes -> perfect TNR

    return tpr, tnr


def calculate_balanced_accuracy(y_true: List[bool], y_pred: List[bool]) -> float:
    """Calculate balanced accuracy for imbalanced datasets.

    Balanced Accuracy = (TPR + TNR) / 2

    This metric is preferred over regular accuracy when classes are
    imbalanced (e.g., 90% PASS, 10% FAIL).

    Args:
        y_true: Ground truth labels (True = PASS, False = FAIL)
        y_pred: Judge predictions (True = PASS, False = FAIL)

    Returns:
        Balanced accuracy (0.0 to 1.0)

    Raises:
        ValueError: If inputs are invalid
    """
    tpr, tnr = calculate_tpr_tnr(y_true, y_pred)
    return (tpr + tnr) / 2.0
