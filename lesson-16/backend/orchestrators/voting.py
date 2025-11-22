"""Voting/Ensemble Orchestration Pattern (FR3.5).

This module implements multi-agent voting with consensus for high-stakes decisions.
Multiple agents execute in parallel and their outputs are aggregated through voting.

Features:
- Async parallel execution using ThreadPoolExecutor pattern
- Majority vote consensus strategy
- Weighted confidence consensus strategy
- Outlier rejection for extreme predictions
- Cost tracking for multi-agent execution
- Error isolation (agent failures don't crash orchestrator)

Use Cases:
- High-stakes fraud detection (transactions >$10K)
- Medical diagnosis with multiple expert agents
- Critical decision-making requiring consensus
- Reliability improvement through redundancy

Example:
    >>> orchestrator = VotingOrchestrator(
    ...     name="fraud_voting",
    ...     num_agents=5,
    ...     consensus_strategy="weighted_average"
    ... )
    >>> for i in range(5):
    ...     orchestrator.register_agent(f"fraud_agent_{i}", agent)
    >>> result = await orchestrator.execute({"task_id": "TXN-12345"})
"""

from __future__ import annotations

import asyncio
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

from backend.orchestrators.base import Orchestrator


class VotingOrchestrator(Orchestrator):
    """Voting/Ensemble orchestration pattern with multi-agent consensus.

    Executes multiple agents in parallel and aggregates their outputs using
    consensus strategies (majority vote or weighted average). Includes outlier
    rejection and cost tracking.

    Attributes:
        name: Orchestrator instance name
        num_agents: Expected number of agents for voting
        consensus_strategy: Strategy for aggregating votes ("majority_vote" or "weighted_average")
        outlier_rejection: Whether to reject statistical outliers
        cost_tracker: Optional dictionary for tracking execution costs
    """

    def __init__(
        self,
        name: str,
        num_agents: int = 5,
        consensus_strategy: str = "majority_vote",
        outlier_rejection: bool = False,
        cost_tracker: dict[str, Any] | None = None,
        max_retries: int = 3,
        circuit_breaker_threshold: int = 3,
    ) -> None:
        """Initialize voting orchestrator.

        Args:
            name: Orchestrator instance name
            num_agents: Expected number of agents for voting (default: 5)
            consensus_strategy: "majority_vote" or "weighted_average"
            outlier_rejection: Whether to reject statistical outliers
            cost_tracker: Optional dictionary for cost tracking
            max_retries: Maximum retry attempts for failed agent calls
            circuit_breaker_threshold: Number of failures before circuit breaker opens

        Raises:
            TypeError: If num_agents is not an integer
            ValueError: If num_agents < 1 or consensus_strategy invalid
        """
        # Call parent constructor
        super().__init__(
            name=name,
            max_retries=max_retries,
            circuit_breaker_threshold=circuit_breaker_threshold,
        )

        # Type checking
        if not isinstance(num_agents, int):
            raise TypeError("num_agents must be an integer")

        # Input validation
        if num_agents < 1:
            raise ValueError("num_agents must be at least 1")

        if consensus_strategy not in ["majority_vote", "weighted_average"]:
            raise ValueError("consensus_strategy must be 'majority_vote' or 'weighted_average'")

        # Store configuration
        self.num_agents = num_agents
        self.consensus_strategy = consensus_strategy
        self.outlier_rejection = outlier_rejection
        self.cost_tracker = cost_tracker if cost_tracker is not None else {}

    async def _execute(self, task: dict[str, Any]) -> dict[str, Any]:
        """Execute multiple agents in parallel and aggregate votes.

        Implements parallel voting pattern where all agents execute concurrently
        using ThreadPoolExecutor. Results are aggregated using consensus strategy.

        Workflow:
        1. Validate sufficient agents registered
        2. Execute all agents in parallel with error isolation
        3. Detect and reject outliers if enabled
        4. Aggregate votes using consensus strategy
        5. Track costs (5× single agent cost for 5 agents)
        6. Return consensus decision

        Args:
            task: Task dictionary with task_id and input_data

        Returns:
            Dictionary containing:
                - status: "success" or "partial_success"
                - agent_votes: List of all agent predictions (in registration order)
                - consensus_decision: Aggregated decision from votes
                - outliers_rejected: List of rejected outlier agents (if enabled)
                - errors: List of agent execution errors
                - cost_summary: Cost tracking information

        Raises:
            ValueError: If insufficient agents registered
        """
        # Step 1: Validate agents registered
        if len(self.agents) != self.num_agents:
            raise ValueError(f"Expected {self.num_agents} agents, but only {len(self.agents)} registered")

        # Step 2: Execute all agents in parallel using ThreadPoolExecutor pattern
        # Reference: /patterns/threadpool-parallel.md
        agent_votes = []
        errors = []
        agent_names = list(self.agents.keys())  # Preserve registration order

        # Create index mapping for result ordering
        future_to_index = {}

        with ThreadPoolExecutor(max_workers=self.num_agents) as executor:
            # Submit all agent tasks
            for idx, agent_name in enumerate(agent_names):
                agent = self.agents[agent_name]
                # Wrap coroutine in asyncio.run for ThreadPoolExecutor
                future = executor.submit(asyncio.run, self._execute_agent_with_isolation(agent_name, agent, task))
                future_to_index[future] = (idx, agent_name)

            # Collect results as they complete, preserve order using index
            results_by_index: dict[int, dict[str, Any]] = {}

            for future in as_completed(future_to_index):
                idx, agent_name = future_to_index[future]

                try:
                    vote = future.result()
                    # Add agent name to vote for tracking
                    vote["agent_name"] = agent_name
                    results_by_index[idx] = vote

                except Exception as e:
                    # Error isolation - agent failure doesn't crash orchestrator
                    error_msg = f"Agent {agent_name} failed: {str(e)}"
                    errors.append(error_msg)
                    self.log_step(step=agent_name, status="failure", output={"error": str(e)})

        # Reconstruct agent_votes in registration order
        for idx in sorted(results_by_index.keys()):
            agent_votes.append(results_by_index[idx])

        # Log execution
        self.log_step(
            step="parallel_voting",
            status="success" if len(agent_votes) > 0 else "failure",
            output={"votes_collected": len(agent_votes), "errors": len(errors)},
        )

        # Step 3: Detect and reject outliers if enabled
        outliers_rejected = []
        if self.outlier_rejection and len(agent_votes) >= 3:
            agent_votes, outliers_rejected = self._reject_outliers(agent_votes)

        # Step 4: Aggregate votes using consensus strategy
        consensus_decision = self._aggregate_votes(agent_votes)

        # Step 5: Track costs
        cost_summary = self._track_costs(len(agent_votes))

        # Step 6: Determine final status
        status = "success" if len(errors) == 0 else "partial_success"

        # Return result
        return {
            "status": status,
            "agent_votes": agent_votes,
            "consensus_decision": consensus_decision,
            "outliers_rejected": outliers_rejected,
            "errors": errors,
            "cost_summary": cost_summary,
        }

    async def _execute_agent_with_isolation(
        self, agent_name: str, agent: Any, task: dict[str, Any]
    ) -> dict[str, Any]:
        """Execute single agent with error isolation.

        Args:
            agent_name: Name of agent being executed
            agent: Agent callable
            task: Task dictionary

        Returns:
            Agent output dictionary

        Raises:
            RuntimeError: If agent execution fails
        """
        # Execute agent
        result = await agent(task)

        # Log successful execution
        self.log_step(step=agent_name, status="success", output=result)

        return result

    def _reject_outliers(self, votes: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[str]]:
        """Reject statistical outliers from voting.

        Uses Z-score method to detect outliers based on fraud_score.
        Outliers are predictions that deviate >2 standard deviations from mean.

        Args:
            votes: List of agent vote dictionaries

        Returns:
            Tuple of (filtered_votes, rejected_agent_names)
        """
        # Extract fraud scores for outlier detection
        fraud_scores = []
        vote_to_score = {}

        for vote in votes:
            if "fraud_score" in vote and isinstance(vote["fraud_score"], (int, float)):
                fraud_scores.append(vote["fraud_score"])
                vote_to_score[vote["agent_name"]] = vote["fraud_score"]

        # Need at least 3 votes for outlier detection
        if len(fraud_scores) < 3:
            return votes, []

        # Calculate mean and standard deviation
        mean_score = statistics.mean(fraud_scores)

        # Handle case where all scores are identical (stdev = 0)
        if len(set(fraud_scores)) == 1:
            return votes, []

        stdev_score = statistics.stdev(fraud_scores)

        # Outliers are values with |z-score| > 1.5
        # z-score = (value - mean) / stdev
        # Using 1.5 instead of 2.0 for more sensitive outlier detection
        filtered_votes = []
        rejected = []

        for vote in votes:
            fraud_score = vote.get("fraud_score")

            if fraud_score is None or not isinstance(fraud_score, (int, float)):
                # Keep votes without fraud_score
                filtered_votes.append(vote)
            else:
                # Calculate z-score
                z_score = abs((fraud_score - mean_score) / stdev_score)

                if z_score <= 1.5:
                    # Keep votes within 1.5 standard deviations
                    filtered_votes.append(vote)
                else:
                    # Reject outliers (|z| > 1.5)
                    rejected.append(vote["agent_name"])

        return filtered_votes, rejected

    def _aggregate_votes(self, votes: list[dict[str, Any]]) -> dict[str, Any]:
        """Aggregate agent votes using consensus strategy.

        Args:
            votes: List of agent vote dictionaries

        Returns:
            Consensus decision dictionary
        """
        if len(votes) == 0:
            # No votes to aggregate
            return {
                "is_fraud": False,
                "confidence": 0.0,
                "vote_count": {},
            }

        if self.consensus_strategy == "majority_vote":
            return self._majority_vote_consensus(votes)
        elif self.consensus_strategy == "weighted_average":
            return self._weighted_average_consensus(votes)
        else:
            # Fallback to majority vote
            return self._majority_vote_consensus(votes)

    def _majority_vote_consensus(self, votes: list[dict[str, Any]]) -> dict[str, Any]:
        """Aggregate votes using majority vote.

        Args:
            votes: List of agent vote dictionaries

        Returns:
            Majority vote consensus decision
        """
        # Count votes for is_fraud
        vote_count = {"True": 0, "False": 0}

        for vote in votes:
            is_fraud = vote.get("is_fraud", False)
            key = "True" if is_fraud else "False"
            vote_count[key] += 1

        # Determine majority
        majority_is_fraud = vote_count["True"] > vote_count["False"]
        confidence = max(vote_count.values()) / len(votes)

        return {
            "is_fraud": majority_is_fraud,
            "confidence": confidence,
            "vote_count": vote_count,
        }

    def _weighted_average_consensus(self, votes: list[dict[str, Any]]) -> dict[str, Any]:
        """Aggregate votes using weighted average by confidence.

        High confidence predictions have more influence on final score.

        Args:
            votes: List of agent vote dictionaries

        Returns:
            Weighted average consensus decision
        """
        # Calculate weighted fraud score
        total_weight = 0.0
        weighted_sum = 0.0

        for vote in votes:
            fraud_score = vote.get("fraud_score", 0.0)
            confidence = vote.get("confidence", 1.0)

            if isinstance(fraud_score, (int, float)) and isinstance(confidence, (int, float)):
                weighted_sum += fraud_score * confidence
                total_weight += confidence

        # Calculate weighted average
        if total_weight > 0:
            weighted_fraud_score = weighted_sum / total_weight
        else:
            weighted_fraud_score = 0.0

        # Determine is_fraud based on threshold (0.5)
        is_fraud = weighted_fraud_score >= 0.5

        return {
            "is_fraud": is_fraud,
            "weighted_fraud_score": weighted_fraud_score,
            "confidence": total_weight / len(votes) if len(votes) > 0 else 0.0,
        }

    def _track_costs(self, num_successful_votes: int) -> dict[str, Any]:
        """Track costs for multi-agent execution.

        Args:
            num_successful_votes: Number of agents that successfully executed

        Returns:
            Cost summary dictionary
        """
        # Update cost tracker
        if self.cost_tracker is not None:
            self.cost_tracker["total_calls"] = self.cost_tracker.get("total_calls", 0) + num_successful_votes

        # Calculate cost multiplier (5 agents = 5× cost of single agent)
        cost_multiplier = float(num_successful_votes)

        return {
            "total_calls": num_successful_votes,
            "cost_multiplier": cost_multiplier,
        }
