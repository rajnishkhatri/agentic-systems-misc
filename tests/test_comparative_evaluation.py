"""
Tests for backend/comparative_evaluation.py

Following TDD: Write tests FIRST, then implement to make them pass.
Test naming convention: test_should_[result]_when_[condition]

Tests cover:
- EloRanking class: initialization, record_match, get_leaderboard
- BradleyTerryRanking class: initialization, fit, predict, get_leaderboard
- Pairwise comparison generation
- Leaderboard visualization
- Error handling and defensive programming
"""

import pytest
from typing import List, Dict, Any
from unittest.mock import Mock, patch
import numpy as np

# Module under test will be implemented after these tests pass
from backend.comparative_evaluation import (
    EloRanking,
    BradleyTerryRanking,
    generate_pairwise_comparisons,
    visualize_leaderboard,
    calculate_expected_score,
    calculate_win_rate,
)


class TestEloRanking:
    """Test Elo ranking algorithm implementation."""

    def test_should_initialize_with_default_ratings_when_created(self) -> None:
        """Test EloRanking initialization with default parameters."""
        # Given: default parameters
        elo = EloRanking()

        # Then: should have correct default values
        assert elo.initial_rating == 1500
        assert elo.k_factor == 32
        assert len(elo.ratings) == 0

    def test_should_initialize_with_custom_parameters_when_provided(self) -> None:
        """Test EloRanking initialization with custom parameters."""
        # Given: custom parameters
        initial_rating = 1200
        k_factor = 64

        # When: creating EloRanking with custom values
        elo = EloRanking(initial_rating=initial_rating, k_factor=k_factor)

        # Then: should use custom values
        assert elo.initial_rating == 1200
        assert elo.k_factor == 64

    def test_should_raise_error_when_k_factor_is_negative(self) -> None:
        """Test that negative K-factor raises ValueError."""
        with pytest.raises(ValueError, match="k_factor must be positive"):
            EloRanking(k_factor=-10)

    def test_should_raise_error_when_initial_rating_is_negative(self) -> None:
        """Test that negative initial rating raises ValueError."""
        with pytest.raises(ValueError, match="initial_rating must be positive"):
            EloRanking(initial_rating=-100)

    def test_should_assign_initial_rating_when_recording_first_match(self) -> None:
        """Test that new players get initial rating."""
        # Given: Elo system with no players
        elo = EloRanking(initial_rating=1500)

        # When: recording match between new players
        elo.record_match("Model_A", "Model_B", winner="Model_A")

        # Then: both models should have ratings
        assert "Model_A" in elo.ratings
        assert "Model_B" in elo.ratings

    def test_should_increase_winner_rating_when_evenly_matched(self) -> None:
        """Test that winner's rating increases in evenly matched game."""
        # Given: Elo system with two equal players
        elo = EloRanking(initial_rating=1500, k_factor=32)

        # When: Model A beats Model B (both start at 1500)
        elo.record_match("Model_A", "Model_B", winner="Model_A")

        # Then: Model A rating should increase, Model B should decrease
        assert elo.ratings["Model_A"] > 1500
        assert elo.ratings["Model_B"] < 1500

    def test_should_handle_tie_correctly_when_result_is_draw(self) -> None:
        """Test that ties are handled correctly (both ratings move toward each other)."""
        # Given: Elo system with equal players
        elo = EloRanking(initial_rating=1500, k_factor=32)

        # When: recording a tie
        elo.record_match("Model_A", "Model_B", winner="tie")

        # Then: ratings should remain at 1500 for equal strength tie
        assert elo.ratings["Model_A"] == 1500
        assert elo.ratings["Model_B"] == 1500

    def test_should_have_small_rating_change_when_favorite_wins(self) -> None:
        """Test that favorite winning causes small rating change."""
        # Given: Elo system with strong and weak player
        elo = EloRanking(initial_rating=1500, k_factor=32)
        elo.ratings["Strong"] = 1800
        elo.ratings["Weak"] = 1200

        # When: strong player beats weak player
        rating_before = elo.ratings["Strong"]
        elo.record_match("Strong", "Weak", winner="Strong")

        # Then: strong player gains only a few points
        rating_gain = elo.ratings["Strong"] - rating_before
        assert 0 < rating_gain < 5  # Expected win, small gain

    def test_should_have_large_rating_change_when_underdog_wins(self) -> None:
        """Test that underdog winning causes large rating change."""
        # Given: Elo system with strong and weak player
        elo = EloRanking(initial_rating=1500, k_factor=32)
        elo.ratings["Strong"] = 1800
        elo.ratings["Weak"] = 1200

        # When: weak player beats strong player (upset!)
        rating_before = elo.ratings["Weak"]
        elo.record_match("Weak", "Strong", winner="Weak")

        # Then: weak player gains many points
        rating_gain = elo.ratings["Weak"] - rating_before
        assert rating_gain > 25  # Upset win, large gain

    def test_should_preserve_rating_sum_when_no_ties(self) -> None:
        """Test that total Elo points are conserved (zero-sum game)."""
        # Given: Elo system
        elo = EloRanking(initial_rating=1500, k_factor=32)

        # When: recording multiple matches
        elo.record_match("A", "B", winner="A")
        elo.record_match("B", "C", winner="C")
        elo.record_match("A", "C", winner="A")

        # Then: sum of ratings should equal 3 * initial_rating
        total_rating = sum(elo.ratings.values())
        expected_total = 3 * 1500
        assert abs(total_rating - expected_total) < 0.01  # Floating point tolerance

    def test_should_return_leaderboard_sorted_by_rating_when_requested(self) -> None:
        """Test leaderboard returns models sorted by rating (descending)."""
        # Given: Elo system with multiple models
        elo = EloRanking(initial_rating=1500)
        elo.record_match("Model_A", "Model_B", winner="Model_A")
        elo.record_match("Model_A", "Model_C", winner="Model_A")
        elo.record_match("Model_B", "Model_C", winner="Model_B")

        # When: getting leaderboard
        leaderboard = elo.get_leaderboard()

        # Then: should be sorted descending by rating
        assert len(leaderboard) == 3
        assert leaderboard[0]["model"] == "Model_A"  # Most wins
        for i in range(len(leaderboard) - 1):
            assert leaderboard[i]["rating"] >= leaderboard[i + 1]["rating"]

    def test_should_include_match_count_in_leaderboard(self) -> None:
        """Test leaderboard includes number of matches per model."""
        # Given: Elo system with multiple matches
        elo = EloRanking()
        elo.record_match("A", "B", winner="A")
        elo.record_match("A", "C", winner="A")
        elo.record_match("A", "B", winner="tie")

        # When: getting leaderboard
        leaderboard = elo.get_leaderboard()

        # Then: Model A should have 3 matches
        model_a_entry = [entry for entry in leaderboard if entry["model"] == "A"][0]
        assert model_a_entry["matches"] == 3

    def test_should_raise_error_when_winner_not_valid(self) -> None:
        """Test that invalid winner value raises ValueError."""
        elo = EloRanking()

        with pytest.raises(ValueError, match="winner must be"):
            elo.record_match("A", "B", winner="Model_D")

    def test_should_raise_error_when_model_names_are_empty(self) -> None:
        """Test that empty model names raise ValueError."""
        elo = EloRanking()

        with pytest.raises(ValueError, match="model_a cannot be empty"):
            elo.record_match("", "Model_B", winner="Model_B")

        with pytest.raises(ValueError, match="model_b cannot be empty"):
            elo.record_match("Model_A", "", winner="Model_A")


class TestBradleyTerryRanking:
    """Test Bradley-Terry model implementation."""

    def test_should_initialize_with_empty_model_when_created(self) -> None:
        """Test BradleyTerryRanking initialization."""
        # Given: default initialization
        bt = BradleyTerryRanking()

        # Then: should have empty skills
        assert len(bt.skills) == 0
        assert bt.fitted is False

    def test_should_fit_model_when_given_comparison_data(self) -> None:
        """Test fitting Bradley-Terry model to comparison data."""
        # Given: BT ranking system and comparison data
        bt = BradleyTerryRanking()
        comparisons = [
            {"model_a": "A", "model_b": "B", "winner": "A"},
            {"model_a": "B", "model_b": "C", "winner": "B"},
            {"model_a": "A", "model_b": "C", "winner": "A"},
        ]

        # When: fitting model
        bt.fit(comparisons)

        # Then: should have skills for all models
        assert bt.fitted is True
        assert "A" in bt.skills
        assert "B" in bt.skills
        assert "C" in bt.skills

    def test_should_rank_models_correctly_when_fitted(self) -> None:
        """Test that Bradley-Terry correctly ranks models based on win probability."""
        # Given: BT model with clear winner pattern (A > B > C)
        bt = BradleyTerryRanking()
        comparisons = [
            {"model_a": "A", "model_b": "B", "winner": "A"},
            {"model_a": "A", "model_b": "B", "winner": "A"},
            {"model_a": "A", "model_b": "B", "winner": "A"},
            {"model_a": "B", "model_b": "C", "winner": "B"},
            {"model_a": "B", "model_b": "C", "winner": "B"},
            {"model_a": "A", "model_b": "C", "winner": "A"},
            {"model_a": "A", "model_b": "C", "winner": "A"},
        ]

        # When: fitting model
        bt.fit(comparisons)

        # Then: skills should reflect A > B > C
        assert bt.skills["A"] > bt.skills["B"]
        assert bt.skills["B"] > bt.skills["C"]

    def test_should_predict_win_probability_when_given_pair(self) -> None:
        """Test predicting win probability between two models."""
        # Given: fitted BT model
        bt = BradleyTerryRanking()
        comparisons = [
            {"model_a": "Strong", "model_b": "Weak", "winner": "Strong"},
            {"model_a": "Strong", "model_b": "Weak", "winner": "Strong"},
            {"model_a": "Strong", "model_b": "Weak", "winner": "Strong"},
        ]
        bt.fit(comparisons)

        # When: predicting win probability
        prob_strong_wins = bt.predict("Strong", "Weak")

        # Then: probability should be high (>0.5) since Strong dominates
        assert prob_strong_wins > 0.7

    def test_should_predict_50_percent_when_models_equal(self) -> None:
        """Test that equal strength models have 50% win probability."""
        # Given: fitted BT model with tie pattern
        bt = BradleyTerryRanking()
        comparisons = [
            {"model_a": "A", "model_b": "B", "winner": "A"},
            {"model_a": "A", "model_b": "B", "winner": "B"},
            {"model_a": "A", "model_b": "B", "winner": "A"},
            {"model_a": "A", "model_b": "B", "winner": "B"},
        ]
        bt.fit(comparisons)

        # When: predicting win probability
        prob = bt.predict("A", "B")

        # Then: should be close to 50%
        assert 0.45 <= prob <= 0.55

    def test_should_return_leaderboard_sorted_by_skill(self) -> None:
        """Test leaderboard returns models sorted by skill parameter."""
        # Given: fitted BT model
        bt = BradleyTerryRanking()
        comparisons = [
            {"model_a": "A", "model_b": "B", "winner": "A"},
            {"model_a": "B", "model_b": "C", "winner": "B"},
            {"model_a": "A", "model_b": "C", "winner": "A"},
        ]
        bt.fit(comparisons)

        # When: getting leaderboard
        leaderboard = bt.get_leaderboard()

        # Then: should be sorted descending by skill
        assert len(leaderboard) == 3
        for i in range(len(leaderboard) - 1):
            assert leaderboard[i]["skill"] >= leaderboard[i + 1]["skill"]

    def test_should_raise_error_when_predicting_before_fit(self) -> None:
        """Test that predicting before fit raises RuntimeError."""
        bt = BradleyTerryRanking()

        with pytest.raises(RuntimeError, match="Model must be fitted"):
            bt.predict("A", "B")

    def test_should_raise_error_when_predicting_unknown_model(self) -> None:
        """Test that predicting with unknown model raises ValueError."""
        bt = BradleyTerryRanking()
        comparisons = [{"model_a": "A", "model_b": "B", "winner": "A"}]
        bt.fit(comparisons)

        with pytest.raises(ValueError, match="Unknown model"):
            bt.predict("A", "Unknown")

    def test_should_raise_error_when_comparisons_empty(self) -> None:
        """Test that fitting with empty comparisons raises ValueError."""
        bt = BradleyTerryRanking()

        with pytest.raises(ValueError, match="comparisons cannot be empty"):
            bt.fit([])

    def test_should_raise_error_when_comparison_missing_keys(self) -> None:
        """Test that comparisons with missing keys raise ValueError."""
        bt = BradleyTerryRanking()
        invalid_comparisons = [
            {"model_a": "A", "winner": "A"}  # Missing model_b
        ]

        with pytest.raises(ValueError, match="must contain keys"):
            bt.fit(invalid_comparisons)


class TestHelperFunctions:
    """Test utility functions for comparative evaluation."""

    def test_should_calculate_expected_score_correctly(self) -> None:
        """Test Elo expected score calculation."""
        # Given: equal ratings
        rating_a = 1500
        rating_b = 1500

        # When: calculating expected score
        expected = calculate_expected_score(rating_a, rating_b)

        # Then: should be 0.5 (50% win probability)
        assert abs(expected - 0.5) < 0.01

    def test_should_calculate_high_expected_score_when_strong_vs_weak(self) -> None:
        """Test expected score when favorite plays underdog."""
        # Given: strong player (1800) vs weak player (1200)
        rating_a = 1800
        rating_b = 1200

        # When: calculating expected score
        expected = calculate_expected_score(rating_a, rating_b)

        # Then: should be high (>0.9)
        assert expected > 0.9

    def test_should_calculate_win_rate_correctly(self) -> None:
        """Test win rate calculation from comparison history."""
        # Given: comparison results for a model
        comparisons = [
            {"model_a": "A", "model_b": "B", "winner": "A"},
            {"model_a": "A", "model_b": "C", "winner": "A"},
            {"model_a": "A", "model_b": "B", "winner": "B"},
            {"model_a": "C", "model_b": "A", "winner": "A"},
        ]

        # When: calculating win rate for Model A
        win_rate = calculate_win_rate(comparisons, "A")

        # Then: should be 75% (3 wins out of 4 matches)
        assert abs(win_rate - 0.75) < 0.01

    def test_should_handle_zero_matches_when_calculating_win_rate(self) -> None:
        """Test win rate calculation when model has no matches."""
        # Given: comparisons not involving target model
        comparisons = [{"model_a": "B", "model_b": "C", "winner": "B"}]

        # When: calculating win rate for Model A
        win_rate = calculate_win_rate(comparisons, "A")

        # Then: should return 0.0
        assert win_rate == 0.0


class TestPairwiseComparisonGeneration:
    """Test pairwise comparison dataset generation."""

    @patch("backend.comparative_evaluation.GenericCriteriaJudge")
    def test_should_generate_comparisons_when_called(self, mock_judge: Mock) -> None:
        """Test generating pairwise comparisons."""
        # Given: mock judge that returns results
        mock_judge_instance = Mock()
        mock_judge.return_value = mock_judge_instance
        mock_judge_instance.evaluate.return_value = Mock(
            score="A", reasoning="Response A is better"
        )

        # When: generating comparisons
        queries = ["Query 1", "Query 2"]
        responses_a = ["Response A1", "Response A2"]
        responses_b = ["Response B1", "Response B2"]

        comparisons = generate_pairwise_comparisons(
            queries=queries,
            responses_a=responses_a,
            responses_b=responses_b,
            dimension="helpfulness",
        )

        # Then: should generate 2 comparisons
        assert len(comparisons) == 2
        assert all(
            key in comparisons[0]
            for key in ["query", "response_a", "response_b", "winner", "rationale"]
        )

    def test_should_raise_error_when_input_lists_different_length(self) -> None:
        """Test that mismatched input lengths raise ValueError."""
        with pytest.raises(ValueError, match="must have same length"):
            generate_pairwise_comparisons(
                queries=["Q1", "Q2"],
                responses_a=["R1"],  # Length mismatch
                responses_b=["R1", "R2"],
                dimension="helpfulness",
            )


class TestLeaderboardVisualization:
    """Test leaderboard visualization functions."""

    @patch("matplotlib.pyplot.show")
    def test_should_create_visualization_when_called(self, mock_show: Mock) -> None:
        """Test leaderboard visualization creation."""
        # Given: leaderboard data
        leaderboard = [
            {"model": "Model_A", "rating": 1650, "matches": 10},
            {"model": "Model_B", "rating": 1500, "matches": 8},
            {"model": "Model_C", "rating": 1450, "matches": 12},
        ]

        # When: visualizing leaderboard
        visualize_leaderboard(leaderboard, title="Test Leaderboard")

        # Then: should call plt.show() (plot was created)
        # Note: We're just testing it doesn't crash; visual validation is manual

    def test_should_raise_error_when_leaderboard_empty(self) -> None:
        """Test that empty leaderboard raises ValueError."""
        with pytest.raises(ValueError, match="leaderboard cannot be empty"):
            visualize_leaderboard([])

    def test_should_raise_error_when_leaderboard_not_list(self) -> None:
        """Test that non-list leaderboard raises TypeError."""
        with pytest.raises(TypeError, match="leaderboard must be a list"):
            visualize_leaderboard("not a list")


class TestAdditionalTypeChecks:
    """Additional tests for type checking and edge cases to improve coverage."""

    def test_should_raise_error_when_rating_not_number(self) -> None:
        """Test calculate_expected_score with invalid types."""
        with pytest.raises(TypeError, match="rating_a must be a number"):
            calculate_expected_score("1500", 1500)

        with pytest.raises(TypeError, match="rating_b must be a number"):
            calculate_expected_score(1500, "1500")

    def test_should_raise_error_when_comparisons_not_list(self) -> None:
        """Test calculate_win_rate with invalid types."""
        with pytest.raises(TypeError, match="comparisons must be a list"):
            calculate_win_rate("not a list", "A")

    def test_should_raise_error_when_k_factor_not_number(self) -> None:
        """Test EloRanking initialization with wrong types."""
        with pytest.raises(TypeError, match="k_factor must be a number"):
            EloRanking(k_factor="32")

    def test_should_raise_error_when_initial_rating_not_number(self) -> None:
        """Test EloRanking initialization with wrong types."""
        with pytest.raises(TypeError, match="initial_rating must be a number"):
            EloRanking(initial_rating="1500")

    def test_should_raise_error_when_model_names_not_string(self) -> None:
        """Test EloRanking.record_match with non-string model names."""
        elo = EloRanking()

        with pytest.raises(TypeError, match="model_a must be a string"):
            elo.record_match(123, "B", winner="B")

        with pytest.raises(TypeError, match="model_b must be a string"):
            elo.record_match("A", 123, winner="A")

        with pytest.raises(TypeError, match="winner must be a string"):
            elo.record_match("A", "B", winner=123)

    def test_should_raise_error_when_bradley_terry_comparisons_not_list(self) -> None:
        """Test BradleyTerryRanking.fit with invalid types."""
        bt = BradleyTerryRanking()

        with pytest.raises(TypeError, match="comparisons must be a list"):
            bt.fit("not a list")

    def test_should_raise_error_when_bradley_terry_comparison_not_dict(self) -> None:
        """Test BradleyTerryRanking.fit with non-dict comparisons."""
        bt = BradleyTerryRanking()

        with pytest.raises(ValueError, match="must be a dict"):
            bt.fit(["not a dict"])

    def test_should_raise_error_when_bradley_terry_needs_min_2_models(self) -> None:
        """Test BradleyTerryRanking.fit with only 1 model."""
        bt = BradleyTerryRanking()
        comparisons = [
            {"model_a": "A", "model_b": "A", "winner": "A"}  # Same model vs itself
        ]

        with pytest.raises(ValueError, match="at least 2 models"):
            bt.fit(comparisons)

    def test_should_raise_error_when_bradley_terry_predict_with_wrong_types(
        self,
    ) -> None:
        """Test BradleyTerryRanking.predict with invalid types."""
        bt = BradleyTerryRanking()
        comparisons = [{"model_a": "A", "model_b": "B", "winner": "A"}]
        bt.fit(comparisons)

        with pytest.raises(TypeError, match="model_a must be a string"):
            bt.predict(123, "B")

        with pytest.raises(TypeError, match="model_b must be a string"):
            bt.predict("A", 123)

    def test_should_raise_error_when_generate_comparisons_wrong_types(self) -> None:
        """Test generate_pairwise_comparisons with invalid types."""
        with pytest.raises(TypeError, match="queries must be a list"):
            generate_pairwise_comparisons(
                queries="not a list",
                responses_a=["R1"],
                responses_b=["R2"],
                dimension="helpfulness",
            )

        with pytest.raises(TypeError, match="responses_a must be a list"):
            generate_pairwise_comparisons(
                queries=["Q1"],
                responses_a="not a list",
                responses_b=["R2"],
                dimension="helpfulness",
            )

        with pytest.raises(TypeError, match="responses_b must be a list"):
            generate_pairwise_comparisons(
                queries=["Q1"],
                responses_a=["R1"],
                responses_b="not a list",
                dimension="helpfulness",
            )

        with pytest.raises(TypeError, match="dimension must be a string"):
            generate_pairwise_comparisons(
                queries=["Q1"], responses_a=["R1"], responses_b=["R2"], dimension=123
            )

    def test_should_raise_error_when_generate_comparisons_empty_queries(self) -> None:
        """Test generate_pairwise_comparisons with empty query list."""
        with pytest.raises(ValueError, match="queries cannot be empty"):
            generate_pairwise_comparisons(
                queries=[], responses_a=[], responses_b=[], dimension="helpfulness"
            )

    @patch("backend.comparative_evaluation.GenericCriteriaJudge")
    def test_should_handle_judge_exception_gracefully(self, mock_judge: Mock) -> None:
        """Test that generate_pairwise_comparisons handles judge failures."""
        # Given: mock judge that raises exception
        mock_judge_instance = Mock()
        mock_judge.return_value = mock_judge_instance
        mock_judge_instance.evaluate.side_effect = Exception("API error")

        # When: generating comparisons
        comparisons = generate_pairwise_comparisons(
            queries=["Q1"],
            responses_a=["R1"],
            responses_b=["R2"],
            dimension="helpfulness",
        )

        # Then: should handle gracefully and return comparison with error
        assert len(comparisons) == 1
        assert "Evaluation failed" in comparisons[0]["rationale"]
