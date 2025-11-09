"""
Comparative evaluation methods: Elo ranking, Bradley-Terry model, pairwise comparisons.

This module implements ranking algorithms for LLM evaluation following defensive coding principles.
All functions include type hints, input validation, and comprehensive error handling.
"""

from typing import List, Dict, Any, Tuple
import math
from collections import defaultdict
import numpy as np
from scipy.optimize import minimize
import matplotlib.pyplot as plt
from backend.ai_judge_framework import GenericCriteriaJudge


# ============================================================================
# Helper Functions
# ============================================================================


def calculate_expected_score(rating_a: float, rating_b: float) -> float:
    """Calculate expected win probability for player A using Elo formula.

    Formula: E_A = 1 / (1 + 10^((R_B - R_A) / 400))

    Args:
        rating_a: Elo rating for player A
        rating_b: Elo rating for player B

    Returns:
        Expected score (win probability) for player A (0.0 to 1.0)

    Raises:
        TypeError: If ratings are not numbers

    Example:
        >>> calculate_expected_score(1500, 1500)
        0.5
        >>> calculate_expected_score(1800, 1200)
        0.97
    """
    # Step 1: Type checking
    if not isinstance(rating_a, (int, float)):
        raise TypeError(f"rating_a must be a number, got {type(rating_a)}")
    if not isinstance(rating_b, (int, float)):
        raise TypeError(f"rating_b must be a number, got {type(rating_b)}")

    # Step 2: Input validation (none needed - all ratings valid)

    # Step 3: Edge case handling (none)

    # Step 4: Main logic
    expected = 1.0 / (1.0 + 10 ** ((rating_b - rating_a) / 400))

    # Step 5: Return
    return expected


def calculate_win_rate(comparisons: List[Dict[str, Any]], model_name: str) -> float:
    """Calculate win rate for a model from comparison history.

    Args:
        comparisons: List of comparison dicts with 'model_a', 'model_b', 'winner'
        model_name: Name of model to calculate win rate for

    Returns:
        Win rate (0.0 to 1.0)

    Raises:
        TypeError: If comparisons is not a list
        ValueError: If comparisons is empty

    Example:
        >>> comparisons = [
        ...     {"model_a": "A", "model_b": "B", "winner": "A"},
        ...     {"model_a": "A", "model_b": "C", "winner": "C"}
        ... ]
        >>> calculate_win_rate(comparisons, "A")
        0.5
    """
    # Step 1: Type checking
    if not isinstance(comparisons, list):
        raise TypeError(f"comparisons must be a list, got {type(comparisons)}")

    # Step 2: Input validation
    if not comparisons:
        raise ValueError("comparisons cannot be empty")

    # Step 3: Edge case handling
    matches = 0
    wins = 0

    # Step 4: Main logic
    for comp in comparisons:
        # Check if model participated in this comparison
        if comp.get("model_a") == model_name or comp.get("model_b") == model_name:
            matches += 1
            if comp.get("winner") == model_name:
                wins += 1

    # Handle case where model has no matches
    if matches == 0:
        return 0.0

    win_rate = wins / matches

    # Step 5: Return
    return win_rate


# ============================================================================
# Elo Ranking System
# ============================================================================


class EloRanking:
    """Elo ranking system for dynamic leaderboards.

    Implements the classic Elo rating algorithm used in chess and adapted for
    LLM comparisons. Supports online updates and tie handling.

    Attributes:
        initial_rating: Starting rating for new models (default: 1500)
        k_factor: Learning rate for rating updates (default: 32)
        ratings: Current ratings for all models
        match_history: Number of matches per model
    """

    def __init__(self, initial_rating: float = 1500, k_factor: float = 32):
        """Initialize Elo ranking system.

        Args:
            initial_rating: Starting rating for new models
            k_factor: Learning rate (higher = faster adaptation, more volatile)

        Raises:
            TypeError: If parameters are not numbers
            ValueError: If parameters are invalid (negative values)

        Example:
            >>> elo = EloRanking(initial_rating=1500, k_factor=32)
        """
        # Step 1: Type checking
        if not isinstance(initial_rating, (int, float)):
            raise TypeError(
                f"initial_rating must be a number, got {type(initial_rating)}"
            )
        if not isinstance(k_factor, (int, float)):
            raise TypeError(f"k_factor must be a number, got {type(k_factor)}")

        # Step 2: Input validation
        if initial_rating < 0:
            raise ValueError(f"initial_rating must be positive, got {initial_rating}")
        if k_factor <= 0:
            raise ValueError(f"k_factor must be positive, got {k_factor}")

        # Step 3: Edge case handling (none)

        # Step 4: Initialize state
        self.initial_rating = initial_rating
        self.k_factor = k_factor
        self.ratings: Dict[str, float] = {}
        self.match_history: Dict[str, int] = defaultdict(int)

    def _get_rating(self, model_name: str) -> float:
        """Get current rating for a model, initializing if new.

        Args:
            model_name: Name of the model

        Returns:
            Current rating for the model
        """
        if model_name not in self.ratings:
            self.ratings[model_name] = self.initial_rating
        return self.ratings[model_name]

    def record_match(self, model_a: str, model_b: str, winner: str) -> None:
        """Record a match result and update ratings.

        Args:
            model_a: Name of first model
            model_b: Name of second model
            winner: Winner of the match (model_a, model_b, or "tie")

        Raises:
            TypeError: If model names are not strings
            ValueError: If model names are empty or winner is invalid

        Example:
            >>> elo = EloRanking()
            >>> elo.record_match("GPT-4", "GPT-3.5", winner="GPT-4")
        """
        # Step 1: Type checking
        if not isinstance(model_a, str):
            raise TypeError(f"model_a must be a string, got {type(model_a)}")
        if not isinstance(model_b, str):
            raise TypeError(f"model_b must be a string, got {type(model_b)}")
        if not isinstance(winner, str):
            raise TypeError(f"winner must be a string, got {type(winner)}")

        # Step 2: Input validation
        if not model_a.strip():
            raise ValueError("model_a cannot be empty")
        if not model_b.strip():
            raise ValueError("model_b cannot be empty")
        if winner not in [model_a, model_b, "tie"]:
            raise ValueError(
                f"winner must be '{model_a}', '{model_b}', or 'tie', got '{winner}'"
            )

        # Step 3: Edge case handling (none)

        # Step 4: Main logic - Update Elo ratings
        # Get current ratings
        rating_a = self._get_rating(model_a)
        rating_b = self._get_rating(model_b)

        # Calculate expected scores
        expected_a = calculate_expected_score(rating_a, rating_b)
        expected_b = 1.0 - expected_a

        # Determine actual scores
        if winner == model_a:
            actual_a, actual_b = 1.0, 0.0
        elif winner == model_b:
            actual_a, actual_b = 0.0, 1.0
        else:  # tie
            actual_a, actual_b = 0.5, 0.5

        # Update ratings
        self.ratings[model_a] = rating_a + self.k_factor * (actual_a - expected_a)
        self.ratings[model_b] = rating_b + self.k_factor * (actual_b - expected_b)

        # Update match history
        self.match_history[model_a] += 1
        self.match_history[model_b] += 1

        # Step 5: Return (void function)

    def get_leaderboard(self) -> List[Dict[str, Any]]:
        """Get current leaderboard sorted by rating.

        Returns:
            List of dicts with 'model', 'rating', 'matches' keys, sorted descending by rating

        Example:
            >>> elo = EloRanking()
            >>> elo.record_match("A", "B", winner="A")
            >>> leaderboard = elo.get_leaderboard()
            >>> leaderboard[0]['model']
            'A'
        """
        # Step 1: Type checking (none - no args)

        # Step 2: Input validation (none)

        # Step 3: Edge case handling
        if not self.ratings:
            return []

        # Step 4: Main logic
        leaderboard = [
            {"model": model, "rating": rating, "matches": self.match_history[model]}
            for model, rating in self.ratings.items()
        ]

        # Sort by rating descending
        leaderboard.sort(key=lambda x: x["rating"], reverse=True)

        # Step 5: Return
        return leaderboard


# ============================================================================
# Bradley-Terry Model
# ============================================================================


class BradleyTerryRanking:
    """Bradley-Terry model for probabilistic skill estimation.

    Implements maximum likelihood estimation of skill parameters from pairwise
    comparison data. Provides uncertainty estimates and order-independent ranking.

    Attributes:
        skills: Estimated skill parameters for each model
        fitted: Whether the model has been fitted to data
    """

    def __init__(self):
        """Initialize Bradley-Terry ranking system.

        Example:
            >>> bt = BradleyTerryRanking()
        """
        # Step 1-3: No validation needed for parameterless init

        # Step 4: Initialize state
        self.skills: Dict[str, float] = {}
        self.fitted: bool = False

    def fit(self, comparisons: List[Dict[str, Any]]) -> None:
        """Fit Bradley-Terry model to comparison data using MLE.

        Args:
            comparisons: List of dicts with 'model_a', 'model_b', 'winner' keys

        Raises:
            TypeError: If comparisons is not a list
            ValueError: If comparisons is empty or missing required keys

        Example:
            >>> bt = BradleyTerryRanking()
            >>> comparisons = [{"model_a": "A", "model_b": "B", "winner": "A"}]
            >>> bt.fit(comparisons)
        """
        # Step 1: Type checking
        if not isinstance(comparisons, list):
            raise TypeError(f"comparisons must be a list, got {type(comparisons)}")

        # Step 2: Input validation
        if not comparisons:
            raise ValueError("comparisons cannot be empty")

        # Validate each comparison has required keys
        required_keys = {"model_a", "model_b", "winner"}
        for i, comp in enumerate(comparisons):
            if not isinstance(comp, dict):
                raise ValueError(f"Comparison {i} must be a dict, got {type(comp)}")
            if not required_keys.issubset(comp.keys()):
                missing = required_keys - comp.keys()
                raise ValueError(
                    f"Comparison {i} must contain keys {required_keys}, missing: {missing}"
                )

        # Step 3: Edge case handling - Get unique models
        models = set()
        for comp in comparisons:
            models.add(comp["model_a"])
            models.add(comp["model_b"])
        models = sorted(models)  # Consistent ordering

        if len(models) < 2:
            raise ValueError("Need at least 2 models to fit Bradley-Terry model")

        # Step 4: Main logic - Maximum likelihood estimation
        # Create win matrix: wins[i][j] = number of times i beat j
        model_to_idx = {model: i for i, model in enumerate(models)}
        n_models = len(models)
        wins = np.zeros((n_models, n_models))

        for comp in comparisons:
            i = model_to_idx[comp["model_a"]]
            j = model_to_idx[comp["model_b"]]
            winner = comp["winner"]

            if winner == comp["model_a"]:
                wins[i][j] += 1
            elif winner == comp["model_b"]:
                wins[j][i] += 1
            else:  # tie
                wins[i][j] += 0.5
                wins[j][i] += 0.5

        # Define negative log-likelihood for optimization
        def neg_log_likelihood(skills: np.ndarray) -> float:
            """Negative log-likelihood of Bradley-Terry model."""
            nll = 0.0
            for i in range(n_models):
                for j in range(n_models):
                    if i != j and (wins[i][j] + wins[j][i]) > 0:
                        # P(i beats j) = exp(skill_i) / (exp(skill_i) + exp(skill_j))
                        # Use log-sum-exp trick for numerical stability
                        log_prob_i_wins = skills[i] - np.logaddexp(skills[i], skills[j])
                        nll -= wins[i][j] * log_prob_i_wins

            return nll

        # Optimize using L-BFGS-B (constrained optimization)
        # Fix first model's skill to 0 to break symmetry (skills are relative)
        initial_skills = np.zeros(n_models)

        # Use scipy.optimize.minimize
        result = minimize(
            neg_log_likelihood,
            initial_skills,
            method="L-BFGS-B",
            options={"maxiter": 1000},
        )

        # Extract optimized skills
        optimized_skills = result.x

        # Center skills around 0 (convention)
        optimized_skills -= np.mean(optimized_skills)

        # Store skills in dict
        self.skills = {
            model: float(optimized_skills[i]) for i, model in enumerate(models)
        }
        self.fitted = True

        # Step 5: Return (void function)

    def predict(self, model_a: str, model_b: str) -> float:
        """Predict win probability for model_a vs model_b.

        Args:
            model_a: First model name
            model_b: Second model name

        Returns:
            Probability that model_a beats model_b (0.0 to 1.0)

        Raises:
            RuntimeError: If model not fitted yet
            ValueError: If model names are unknown

        Example:
            >>> bt = BradleyTerryRanking()
            >>> bt.fit([{"model_a": "A", "model_b": "B", "winner": "A"}])
            >>> bt.predict("A", "B")
            0.73
        """
        # Step 1: Type checking
        if not isinstance(model_a, str):
            raise TypeError(f"model_a must be a string, got {type(model_a)}")
        if not isinstance(model_b, str):
            raise TypeError(f"model_b must be a string, got {type(model_b)}")

        # Step 2: Input validation
        if not self.fitted:
            raise RuntimeError(
                "Model must be fitted before prediction. Call fit() first."
            )

        if model_a not in self.skills:
            raise ValueError(
                f"Unknown model: {model_a}. Available: {list(self.skills.keys())}"
            )
        if model_b not in self.skills:
            raise ValueError(
                f"Unknown model: {model_b}. Available: {list(self.skills.keys())}"
            )

        # Step 3: Edge case handling (none)

        # Step 4: Main logic
        # P(A beats B) = exp(skill_a) / (exp(skill_a) + exp(skill_b))
        #              = 1 / (1 + exp(skill_b - skill_a))
        skill_a = self.skills[model_a]
        skill_b = self.skills[model_b]

        prob = 1.0 / (1.0 + np.exp(skill_b - skill_a))

        # Step 5: Return
        return float(prob)

    def get_leaderboard(self) -> List[Dict[str, Any]]:
        """Get current leaderboard sorted by skill parameter.

        Returns:
            List of dicts with 'model', 'skill' keys, sorted descending by skill

        Example:
            >>> bt = BradleyTerryRanking()
            >>> bt.fit([{"model_a": "A", "model_b": "B", "winner": "A"}])
            >>> leaderboard = bt.get_leaderboard()
        """
        # Step 1: Type checking (none - no args)

        # Step 2: Input validation (none)

        # Step 3: Edge case handling
        if not self.skills:
            return []

        # Step 4: Main logic
        leaderboard = [
            {"model": model, "skill": skill} for model, skill in self.skills.items()
        ]

        # Sort by skill descending
        leaderboard.sort(key=lambda x: x["skill"], reverse=True)

        # Step 5: Return
        return leaderboard


# ============================================================================
# Pairwise Comparison Generation
# ============================================================================


def generate_pairwise_comparisons(
    queries: List[str],
    responses_a: List[str],
    responses_b: List[str],
    dimension: str,
    model: str = "gpt-4o-mini",
) -> List[Dict[str, Any]]:
    """Generate pairwise comparisons using AI judge.

    Args:
        queries: List of query strings
        responses_a: List of responses from model A
        responses_b: List of responses from model B
        dimension: Evaluation dimension (e.g., "helpfulness", "correctness")
        model: Judge model to use (default: gpt-4o-mini)

    Returns:
        List of comparison dicts with 'query', 'response_a', 'response_b', 'winner', 'rationale'

    Raises:
        TypeError: If inputs are not lists or strings
        ValueError: If input lists have different lengths

    Example:
        >>> comparisons = generate_pairwise_comparisons(
        ...     queries=["How to cook pasta?"],
        ...     responses_a=["Boil water, add pasta..."],
        ...     responses_b=["Use a pot..."],
        ...     dimension="helpfulness"
        ... )
    """
    # Step 1: Type checking
    if not isinstance(queries, list):
        raise TypeError(f"queries must be a list, got {type(queries)}")
    if not isinstance(responses_a, list):
        raise TypeError(f"responses_a must be a list, got {type(responses_a)}")
    if not isinstance(responses_b, list):
        raise TypeError(f"responses_b must be a list, got {type(responses_b)}")
    if not isinstance(dimension, str):
        raise TypeError(f"dimension must be a string, got {type(dimension)}")

    # Step 2: Input validation
    if not (len(queries) == len(responses_a) == len(responses_b)):
        raise ValueError(
            f"queries, responses_a, responses_b must have same length. "
            f"Got {len(queries)}, {len(responses_a)}, {len(responses_b)}"
        )

    if not queries:
        raise ValueError("queries cannot be empty")

    # Step 3: Edge case handling (none)

    # Step 4: Main logic
    # Create judge for comparative evaluation
    criteria_description = f"""
    Compare two responses based on {dimension}.
    Respond with JSON containing:
    - "winner": "A" or "B" (which response is better)
    - "reasoning": Brief explanation of your choice
    """

    judge = GenericCriteriaJudge(
        model=model,
        criteria=f"comparative_{dimension}",
        criteria_description=criteria_description,
    )

    comparisons = []
    for query, resp_a, resp_b in zip(queries, responses_a, responses_b):
        # Create combined prompt for judge
        combined_query = f"""
Query: {query}

Response A: {resp_a}

Response B: {resp_b}

Which response is better for {dimension}?
"""

        # Evaluate
        try:
            result = judge.evaluate(query=combined_query, response="")

            # Parse winner from result
            winner = result.score if result.score in ["A", "B"] else "A"

            comparisons.append(
                {
                    "query": query,
                    "response_a": resp_a,
                    "response_b": resp_b,
                    "winner": winner,
                    "rationale": result.reasoning,
                    "dimension": dimension,
                }
            )
        except Exception as e:
            # Handle evaluation failures gracefully
            comparisons.append(
                {
                    "query": query,
                    "response_a": resp_a,
                    "response_b": resp_b,
                    "winner": "A",  # Default
                    "rationale": f"Evaluation failed: {str(e)}",
                    "dimension": dimension,
                }
            )

    # Step 5: Return
    return comparisons


# ============================================================================
# Visualization
# ============================================================================


def visualize_leaderboard(
    leaderboard: List[Dict[str, Any]],
    title: str = "Model Leaderboard",
    rating_key: str = "rating",
) -> None:
    """Visualize leaderboard as horizontal bar chart.

    Args:
        leaderboard: List of dicts with 'model' and rating_key
        title: Chart title
        rating_key: Key to use for rating values (default: "rating")

    Raises:
        ValueError: If leaderboard is empty

    Example:
        >>> leaderboard = [{"model": "A", "rating": 1600}, {"model": "B", "rating": 1500}]
        >>> visualize_leaderboard(leaderboard)
    """
    # Step 1: Type checking
    if not isinstance(leaderboard, list):
        raise TypeError(f"leaderboard must be a list, got {type(leaderboard)}")

    # Step 2: Input validation
    if not leaderboard:
        raise ValueError("leaderboard cannot be empty")

    # Step 3: Edge case handling (none)

    # Step 4: Main logic
    models = [entry["model"] for entry in leaderboard]
    ratings = [entry[rating_key] for entry in leaderboard]

    # Create horizontal bar chart
    fig, ax = plt.subplots(figsize=(10, max(6, len(models) * 0.4)))
    y_pos = np.arange(len(models))

    ax.barh(y_pos, ratings, align="center")
    ax.set_yticks(y_pos)
    ax.set_yticklabels(models)
    ax.invert_yaxis()  # Highest rating at top
    ax.set_xlabel("Rating")
    ax.set_title(title)
    ax.grid(axis="x", alpha=0.3)

    # Add rating labels on bars
    for i, rating in enumerate(ratings):
        ax.text(rating, i, f" {rating:.0f}", va="center")

    plt.tight_layout()
    plt.show()

    # Step 5: Return (void function)
