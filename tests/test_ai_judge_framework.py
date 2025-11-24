"""
Tests for backend/ai_judge_framework.py

Following TDD: Write tests FIRST, then implement to make them pass.
Test naming convention: test_should_[result]_when_[condition]

Tests cover:
- JudgeResult Pydantic model validation
- BaseJudge abstract class interface
- DietaryAdherenceJudge concrete implementation
- SubstantiationJudge concrete implementation
- GenericCriteriaJudge concrete implementation
- Batch processing with concurrency
- TPR/TNR metric calculations
- Error handling and defensive programming
"""

from unittest.mock import Mock, patch

import pytest

# Module under test will be implemented after these tests pass
from backend.ai_judge_framework import (
    BaseJudge,
    DietaryAdherenceJudge,
    GenericCriteriaJudge,
    JudgeResult,
    SubstantiationJudge,
    calculate_balanced_accuracy,
    calculate_tpr_tnr,
)


class TestJudgeResultModel:
    """Test Pydantic model for judge outputs."""

    def test_should_create_valid_judge_result_when_given_all_fields(self) -> None:
        """Test JudgeResult creation with all required fields."""
        # Given: valid judge result data
        data = {
            "score": "PASS",
            "reasoning": "Recipe adheres to dietary restriction.",
            "confidence": 0.95,
        }

        # When: creating JudgeResult
        result = JudgeResult(**data)

        # Then: all fields should be set correctly
        assert result.score == "PASS"
        assert result.reasoning == "Recipe adheres to dietary restriction."
        assert result.confidence == 0.95

    def test_should_accept_binary_scores(self) -> None:
        """Test that JudgeResult accepts PASS/FAIL scores."""
        pass_result = JudgeResult(score="PASS", reasoning="Good")
        fail_result = JudgeResult(score="FAIL", reasoning="Bad")

        assert pass_result.score == "PASS"
        assert fail_result.score == "FAIL"

    def test_should_accept_numeric_scores(self) -> None:
        """Test that JudgeResult accepts numeric scores (1-5)."""
        result = JudgeResult(score=4, reasoning="Above average quality")

        assert result.score == 4

    def test_should_set_default_confidence_when_not_provided(self) -> None:
        """Test default confidence value."""
        result = JudgeResult(score="PASS", reasoning="Test")

        assert result.confidence == 1.0  # Default confidence

    def test_should_reject_invalid_confidence_when_out_of_range(self) -> None:
        """Test that confidence must be between 0 and 1."""
        with pytest.raises(ValueError, match="confidence"):
            JudgeResult(score="PASS", reasoning="Test", confidence=1.5)

    def test_should_reject_empty_reasoning(self) -> None:
        """Test that reasoning cannot be empty."""
        with pytest.raises(ValueError, match="reasoning"):
            JudgeResult(score="PASS", reasoning="")


class TestBaseJudgeInterface:
    """Test BaseJudge abstract class interface."""

    def test_should_raise_error_when_instantiating_base_judge_directly(self) -> None:
        """Test that BaseJudge cannot be instantiated (abstract class)."""
        with pytest.raises(TypeError):
            BaseJudge(model="gpt-4o-mini", temperature=0.0)

    def test_should_enforce_abstract_methods_in_subclass(self) -> None:
        """Test that subclasses must implement abstract methods."""

        class IncompleteJudge(BaseJudge):
            """Judge that doesn't implement required methods."""

            pass

        with pytest.raises(TypeError):
            IncompleteJudge(model="gpt-4o-mini")


class TestDietaryAdherenceJudge:
    """Test concrete DietaryAdherenceJudge implementation."""

    @pytest.fixture
    def judge(self) -> DietaryAdherenceJudge:
        """Create a DietaryAdherenceJudge instance for testing."""
        return DietaryAdherenceJudge(model="gpt-4o-mini", temperature=0.0)

    def test_should_initialize_judge_with_model_name(
        self, judge: DietaryAdherenceJudge
    ) -> None:
        """Test judge initialization with model parameter."""
        assert judge.model == "gpt-4o-mini"
        assert judge.temperature == 0.0

    def test_should_load_prompt_template_on_initialization(
        self, judge: DietaryAdherenceJudge
    ) -> None:
        """Test that judge loads prompt template from file."""
        # Judge should have loaded template from lesson-10/templates/judge_prompts/dietary_adherence_judge.txt
        assert judge.prompt_template is not None
        assert len(judge.prompt_template) > 0
        assert "{query}" in judge.prompt_template
        assert "{dietary_restriction}" in judge.prompt_template
        assert "{response}" in judge.prompt_template

    @patch("litellm.completion")
    def test_should_evaluate_single_example_when_called(
        self, mock_completion: Mock, judge: DietaryAdherenceJudge
    ) -> None:
        """Test evaluating a single query-response pair."""
        # Given: mock LLM response
        mock_completion.return_value = Mock(
            choices=[
                Mock(
                    message=Mock(
                        content='{"reasoning": "All ingredients are vegan", "answer": "PASS"}'
                    )
                )
            ]
        )

        # When: evaluating a vegan query
        result = judge.evaluate(
            query="Give me a vegan dinner recipe",
            response="Try this tofu stir-fry with vegetables...",
            dietary_restriction="vegan",
        )

        # Then: should return JudgeResult
        assert isinstance(result, JudgeResult)
        assert result.score == "PASS"
        assert "vegan" in result.reasoning.lower()

    @patch("litellm.completion")
    def test_should_format_prompt_with_placeholders(
        self, mock_completion: Mock, judge: DietaryAdherenceJudge
    ) -> None:
        """Test that judge correctly formats prompt with query/response/restriction."""
        # Given: mock LLM response
        mock_completion.return_value = Mock(
            choices=[
                Mock(message=Mock(content='{"reasoning": "Test", "answer": "PASS"}'))
            ]
        )

        query = "Test query"
        response = "Test response"
        restriction = "vegan"

        # When: evaluating
        judge.evaluate(query=query, response=response, dietary_restriction=restriction)

        # Then: should call LLM with formatted prompt
        call_args = mock_completion.call_args
        prompt = call_args[1]["messages"][0]["content"]

        assert query in prompt
        assert response in prompt
        assert restriction in prompt

    @patch("litellm.completion")
    def test_should_handle_json_parsing_errors_gracefully(
        self, mock_completion: Mock, judge: DietaryAdherenceJudge
    ) -> None:
        """Test error handling when LLM returns invalid JSON."""
        # Given: LLM returns malformed JSON
        mock_completion.return_value = Mock(
            choices=[Mock(message=Mock(content="This is not valid JSON"))]
        )

        # When/Then: should raise appropriate error
        with pytest.raises(ValueError, match="Failed to parse"):
            judge.evaluate(
                query="Test query",
                response="Test response",
                dietary_restriction="vegan",
            )

    @patch("litellm.completion")
    def test_should_retry_on_api_failure(
        self, mock_completion: Mock, judge: DietaryAdherenceJudge
    ) -> None:
        """Test retry logic when API call fails."""
        # Given: API fails twice then succeeds
        mock_completion.side_effect = [
            Exception("API Error"),
            Exception("API Error"),
            Mock(
                choices=[
                    Mock(
                        message=Mock(content='{"reasoning": "Test", "answer": "PASS"}')
                    )
                ]
            ),
        ]

        # When: evaluating (should retry)
        result = judge.evaluate(
            query="Test query", response="Test response", dietary_restriction="vegan"
        )

        # Then: should succeed after retries
        assert result.score == "PASS"
        assert mock_completion.call_count == 3


class TestSubstantiationJudge:
    """Test SubstantiationJudge implementation."""

    @pytest.fixture
    def judge(self) -> SubstantiationJudge:
        """Create a SubstantiationJudge instance."""
        return SubstantiationJudge(model="gpt-4o-mini", temperature=0.0)

    def test_should_load_substantiation_template(
        self, judge: SubstantiationJudge
    ) -> None:
        """Test that substantiation judge loads correct template."""
        assert judge.prompt_template is not None
        assert "{context}" in judge.prompt_template
        assert "{query}" in judge.prompt_template
        assert "{response}" in judge.prompt_template

    @patch("litellm.completion")
    def test_should_evaluate_with_context(
        self, mock_completion: Mock, judge: SubstantiationJudge
    ) -> None:
        """Test evaluating response against provided context."""
        # Given: mock LLM response
        mock_completion.return_value = Mock(
            choices=[
                Mock(
                    message=Mock(
                        content='{"reasoning": "All claims verified", "all_responses_substantiated": true, "answer": "PASS"}'
                    )
                )
            ]
        )

        # When: evaluating with context
        result = judge.evaluate(
            query="What's in the recipe?",
            response="The recipe contains flour and eggs.",
            context={"ingredients": ["flour", "eggs", "sugar"]},
        )

        # Then: should return substantiation result
        assert isinstance(result, JudgeResult)
        assert result.score == "PASS"

    @patch("litellm.completion")
    def test_should_detect_unsubstantiated_claims(
        self, mock_completion: Mock, judge: SubstantiationJudge
    ) -> None:
        """Test detection of fabricated information."""
        # Given: LLM detects hallucination
        mock_completion.return_value = Mock(
            choices=[
                Mock(
                    message=Mock(
                        content='{"reasoning": "Recipe mentions chocolate not in context", "all_responses_substantiated": false, "answer": "FAIL"}'
                    )
                )
            ]
        )

        # When: evaluating response with fabricated claim
        result = judge.evaluate(
            query="What's in the recipe?",
            response="The recipe contains chocolate and vanilla.",
            context={"ingredients": ["flour", "eggs"]},  # No chocolate!
        )

        # Then: should fail
        assert result.score == "FAIL"


class TestGenericCriteriaJudge:
    """Test GenericCriteriaJudge implementation."""

    @pytest.fixture
    def judge(self) -> GenericCriteriaJudge:
        """Create a GenericCriteriaJudge with custom criteria."""
        return GenericCriteriaJudge(
            model="gpt-4o-mini",
            temperature=0.0,
            criteria="helpfulness",
            criteria_description="Response provides actionable, useful information",
        )

    def test_should_initialize_with_custom_criteria(
        self, judge: GenericCriteriaJudge
    ) -> None:
        """Test initialization with custom evaluation criteria."""
        assert judge.criteria == "helpfulness"
        assert "actionable" in judge.criteria_description

    def test_should_build_prompt_from_criteria(
        self, judge: GenericCriteriaJudge
    ) -> None:
        """Test dynamic prompt building based on criteria."""
        prompt = judge._build_prompt(
            query="How do I bake cookies?", response="Bake at 350°F for 12 minutes."
        )

        assert "helpfulness" in prompt.lower()
        assert "actionable" in prompt.lower()
        assert "How do I bake cookies?" in prompt
        assert "350°F" in prompt

    @patch("litellm.completion")
    def test_should_evaluate_custom_criteria(
        self, mock_completion: Mock, judge: GenericCriteriaJudge
    ) -> None:
        """Test evaluation using custom criteria."""
        # Given: mock evaluation
        mock_completion.return_value = Mock(
            choices=[
                Mock(
                    message=Mock(
                        content='{"reasoning": "Response is helpful and actionable", "answer": "PASS"}'
                    )
                )
            ]
        )

        # When: evaluating
        result = judge.evaluate(
            query="Quick dinner idea?",
            response="Try a 15-minute stir-fry: heat oil, add protein and veggies, season with soy sauce.",
        )

        # Then: should evaluate based on custom criteria
        assert result.score == "PASS"
        assert (
            "helpful" in result.reasoning.lower()
            or "actionable" in result.reasoning.lower()
        )

    def test_should_support_multiple_criteria_types(self) -> None:
        """Test creating judges for different criteria."""
        judges = [
            GenericCriteriaJudge(
                model="gpt-4o-mini",
                criteria="coherence",
                criteria_description="Logical flow",
            ),
            GenericCriteriaJudge(
                model="gpt-4o-mini",
                criteria="toxicity",
                criteria_description="Harmful content",
            ),
            GenericCriteriaJudge(
                model="gpt-4o-mini",
                criteria="creativity",
                criteria_description="Novel ideas",
            ),
        ]

        for judge in judges:
            assert judge.criteria in ["coherence", "toxicity", "creativity"]


class TestBatchProcessing:
    """Test batch evaluation with concurrency."""

    @pytest.fixture
    def judge(self) -> DietaryAdherenceJudge:
        """Create judge for batch testing."""
        return DietaryAdherenceJudge(model="gpt-4o-mini", temperature=0.0)

    @patch("litellm.completion")
    async def test_should_evaluate_batch_in_parallel(
        self, mock_completion: Mock, judge: DietaryAdherenceJudge
    ) -> None:
        """Test parallel batch evaluation."""
        # Given: multiple examples
        examples = [
            {
                "query": "Vegan recipe 1",
                "response": "Tofu dish",
                "dietary_restriction": "vegan",
            },
            {
                "query": "Vegan recipe 2",
                "response": "Bean salad",
                "dietary_restriction": "vegan",
            },
            {
                "query": "Vegan recipe 3",
                "response": "Vegetable soup",
                "dietary_restriction": "vegan",
            },
        ]

        mock_completion.return_value = Mock(
            choices=[
                Mock(message=Mock(content='{"reasoning": "Test", "answer": "PASS"}'))
            ]
        )

        # When: batch evaluating
        results = await judge.evaluate_batch(examples, max_workers=3)

        # Then: should return results for all examples
        assert len(results) == 3
        assert all(isinstance(r, JudgeResult) for r in results)
        assert mock_completion.call_count == 3

    @patch("litellm.completion")
    async def test_should_handle_partial_failures_in_batch(
        self, mock_completion: Mock, judge: DietaryAdherenceJudge
    ) -> None:
        """Test batch processing handles individual failures gracefully."""
        # Given: some API calls fail
        examples = [
            {"query": "Q1", "response": "R1", "dietary_restriction": "vegan"},
            {"query": "Q2", "response": "R2", "dietary_restriction": "vegan"},
            {"query": "Q3", "response": "R3", "dietary_restriction": "vegan"},
        ]

        mock_completion.side_effect = [
            Mock(
                choices=[
                    Mock(
                        message=Mock(content='{"reasoning": "Test", "answer": "PASS"}')
                    )
                ]
            ),
            Exception("API Error"),  # Second call fails
            Mock(
                choices=[
                    Mock(
                        message=Mock(content='{"reasoning": "Test", "answer": "PASS"}')
                    )
                ]
            ),
        ]

        # When: batch evaluating
        results = await judge.evaluate_batch(examples, max_workers=3)

        # Then: should return results for successful evaluations
        # Failed ones should be marked or handled
        assert len(results) >= 2  # At least 2 successful


class TestTPRTNRCalculations:
    """Test True Positive Rate and True Negative Rate calculations."""

    def test_should_calculate_perfect_tpr_when_all_failures_caught(self) -> None:
        """Test TPR calculation when judge catches all failures."""
        # Given: perfect judge performance
        y_true = [True, True, False, False]  # True = PASS, False = FAIL
        y_pred = [True, True, False, False]  # Perfect match

        # When: calculating TPR/TNR
        tpr, tnr = calculate_tpr_tnr(y_true, y_pred)

        # Then: both should be 100%
        assert tpr == 1.0, f"Expected TPR=1.0, got {tpr}"
        assert tnr == 1.0, f"Expected TNR=1.0, got {tnr}"

    def test_should_calculate_tpr_when_some_failures_missed(self) -> None:
        """Test TPR when judge misses some failures."""
        # Given: 2 true failures, judge catches only 1
        y_true = [True, True, False, False]  # 2 PASS, 2 FAIL
        y_pred = [True, True, True, False]  # Missed one FAIL (false negative)

        # When: calculating TPR
        tpr, tnr = calculate_tpr_tnr(y_true, y_pred)

        # Then: TPR = 1/2 = 0.5 (caught 1 of 2 failures)
        assert tpr == 0.5, f"Expected TPR=0.5, got {tpr}"
        # TNR = 2/2 = 1.0 (correctly identified both passes)
        assert tnr == 1.0, f"Expected TNR=1.0, got {tnr}"

    def test_should_calculate_tnr_when_false_alarms_occur(self) -> None:
        """Test TNR when judge has false positives."""
        # Given: judge incorrectly flags successes as failures
        y_true = [True, True, False, False]  # 2 PASS, 2 FAIL
        y_pred = [False, True, False, False]  # One false positive

        # When: calculating TNR
        tpr, tnr = calculate_tpr_tnr(y_true, y_pred)

        # Then: TNR = 1/2 = 0.5 (correct on 1 of 2 passes)
        assert tnr == 0.5, f"Expected TNR=0.5, got {tnr}"
        # TPR = 2/2 = 1.0 (caught both failures)
        assert tpr == 1.0, f"Expected TPR=1.0, got {tpr}"

    def test_should_calculate_balanced_accuracy_correctly(self) -> None:
        """Test balanced accuracy calculation."""
        # Given: TPR = 0.8, TNR = 0.9
        y_true = [True] * 10 + [False] * 10  # 10 PASS, 10 FAIL
        y_pred = [True] * 9 + [False] * 1 + [False] * 8 + [True] * 2
        # TPR = 8/10 = 0.8, TNR = 9/10 = 0.9

        # When: calculating balanced accuracy
        balanced_acc = calculate_balanced_accuracy(y_true, y_pred)

        # Then: balanced accuracy = (0.8 + 0.9) / 2 = 0.85
        expected = (0.8 + 0.9) / 2
        assert abs(balanced_acc - expected) < 0.01, (
            f"Expected {expected}, got {balanced_acc}"
        )

    def test_should_handle_edge_case_when_no_positives(self) -> None:
        """Test handling edge case with no positive examples."""
        # Given: all failures (no passes)
        y_true = [False, False, False]
        y_pred = [False, False, False]

        # When: calculating TPR/TNR
        tpr, tnr = calculate_tpr_tnr(y_true, y_pred)

        # Then: should handle gracefully (TNR undefined, TPR=1.0)
        assert tpr == 1.0  # All failures caught
        # TNR is undefined (no true positives), should handle gracefully


class TestErrorHandlingAndDefensiveProgramming:
    """Test defensive coding practices."""

    def test_should_raise_type_error_for_invalid_model_type(self) -> None:
        """Test type checking for model parameter."""
        with pytest.raises(TypeError, match="model"):
            DietaryAdherenceJudge(model=12345, temperature=0.0)  # type: ignore

    def test_should_raise_value_error_for_negative_temperature(self) -> None:
        """Test input validation for temperature."""
        with pytest.raises(ValueError, match="temperature"):
            DietaryAdherenceJudge(model="gpt-4o-mini", temperature=-0.5)

    def test_should_raise_value_error_for_temperature_above_two(self) -> None:
        """Test input validation for temperature upper bound."""
        with pytest.raises(ValueError, match="temperature"):
            DietaryAdherenceJudge(model="gpt-4o-mini", temperature=2.5)

    def test_should_raise_error_for_missing_template_file(self) -> None:
        """Test handling of missing prompt template file."""

        class BrokenJudge(BaseJudge):
            def __init__(self, model: str, temperature: float = 0.0):
                super().__init__(model, temperature)
                # Try to load non-existent template
                self.prompt_template = self._load_template("nonexistent_template.txt")

            def evaluate(self, **kwargs):
                pass

        with pytest.raises(FileNotFoundError):
            BrokenJudge(model="gpt-4o-mini")

    def test_should_validate_empty_query(self) -> None:
        """Test that empty queries are rejected."""
        judge = DietaryAdherenceJudge(model="gpt-4o-mini")

        with pytest.raises(ValueError, match="query"):
            judge.evaluate(query="", response="Test", dietary_restriction="vegan")

    def test_should_validate_empty_response(self) -> None:
        """Test that empty responses are rejected."""
        judge = DietaryAdherenceJudge(model="gpt-4o-mini")

        with pytest.raises(ValueError, match="response"):
            judge.evaluate(query="Test", response="", dietary_restriction="vegan")

    def test_should_have_type_hints_on_all_public_methods(self) -> None:
        """Test that all public methods have type hints."""
        import inspect

        for judge_class in [
            DietaryAdherenceJudge,
            SubstantiationJudge,
            GenericCriteriaJudge,
        ]:
            for name, method in inspect.getmembers(
                judge_class, predicate=inspect.isfunction
            ):
                if not name.startswith("_"):  # Public methods
                    annotations = method.__annotations__
                    assert "return" in annotations, (
                        f"{judge_class.__name__}.{name} missing return type hint"
                    )
