"""Multi-Agent Design Patterns for Lesson 14 (Task 5.6).

TDD-GREEN Phase: Implementation of 5 coordination pattern classes.

Pattern Implementations:
1. MultiAgentPattern - Abstract base class
2. HierarchicalAgent - Manager-Worker delegation pattern
3. DiamondAgent - Competitive broadcast + selection pattern
4. P2PAgent - Peer-to-peer handoff with context transfer
5. CollaborativeAgent - Shared workspace with peer review
6. AdaptiveLoopAgent - Iterative refinement with quality threshold

Created: 2025-11-15
Task: 5.6 from tasks-0005-prd-rag-agent-evaluation-tutorial-system.md
Pattern: TDD-GREEN phase (minimal implementation to pass tests)
"""

import logging
import time
from abc import ABC, abstractmethod
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import wraps
from typing import Any, Callable, TypeVar

import litellm

# Configure logging
logger = logging.getLogger(__name__)

# =============================================================================
# Module-Level Constants
# =============================================================================

# Token estimation for context size management
TOKEN_ESTIMATION_CHARS_PER_TOKEN = 4

# Query refinement parameters
QUERY_REDUCTION_RATIO = 2 / 3  # Keep 2/3 of words when simplifying queries

# Retry configuration for LiteLLM calls
LITELLM_MAX_RETRIES = 3
LITELLM_RETRY_DELAYS = [1.0, 2.0, 4.0]  # Exponential backoff (seconds)


# =============================================================================
# Retry Decorator for LiteLLM Calls
# =============================================================================

T = TypeVar("T")


def retry_litellm_call(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator to retry LiteLLM calls with exponential backoff.

    Retries transient failures (rate limits, timeouts, connection errors)
    up to LITELLM_MAX_RETRIES times with exponential backoff.

    Args:
        func: Function that makes LiteLLM API calls

    Returns:
        Wrapped function with retry logic
    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        last_exception = None

        for attempt in range(LITELLM_MAX_RETRIES):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                # Check if error is retryable (rate limit, timeout, connection)
                error_str = str(e).lower()
                is_retryable = any(
                    keyword in error_str
                    for keyword in ["rate limit", "timeout", "connection", "503", "429"]
                )

                if not is_retryable or attempt == LITELLM_MAX_RETRIES - 1:
                    # Non-retryable error or final attempt - raise immediately
                    raise

                # Wait before retry (exponential backoff)
                delay = LITELLM_RETRY_DELAYS[
                    min(attempt, len(LITELLM_RETRY_DELAYS) - 1)
                ]
                logger.info(
                    f"Retrying {func.__name__} after {delay}s (attempt {attempt + 1}/{LITELLM_MAX_RETRIES}): {e}"
                )
                time.sleep(delay)

        # Should never reach here, but satisfy type checker
        if last_exception:
            raise last_exception
        raise RuntimeError("Retry logic failed unexpectedly")

    return wrapper


# =============================================================================
# Abstract Base Class
# =============================================================================


class MultiAgentPattern(ABC):
    """Abstract base class for multi-agent coordination patterns.

    All pattern implementations must:
    1. Call super().__init__(model) in their constructor
    2. Implement the execute() method
    3. Return dict results with consistent structure
    """

    def __init__(self, model: str) -> None:
        """Initialize multi-agent pattern.

        Args:
            model: LLM model identifier (e.g., "gpt-4o-mini")

        Raises:
            TypeError: If model is not a string
            ValueError: If model is empty string
        """
        # Step 1: Type checking
        if not isinstance(model, str):
            raise TypeError("model must be a string")

        # Step 2: Input validation
        if not model:
            raise ValueError("model must be non-empty")

        # Step 3: Set attribute
        self.model = model

    @abstractmethod
    def execute(self, task: dict[str, Any]) -> dict[str, Any]:
        """Execute the multi-agent pattern on a task.

        Args:
            task: Task specification dictionary

        Returns:
            Result dictionary with pattern-specific structure
        """
        pass


# =============================================================================
# HierarchicalAgent - Manager-Worker Pattern
# =============================================================================


class HierarchicalAgent(MultiAgentPattern):
    """Manager-Worker coordination pattern.

    A manager agent delegates subtasks to specialized worker agents in parallel,
    then synthesizes their results into a coherent response.
    """

    def __init__(
        self,
        model: str,
        workers: dict[str, Any],
        max_workers: int | None = None,
    ) -> None:
        """Initialize hierarchical agent.

        Args:
            model: LLM model identifier
            workers: Dictionary mapping worker names to worker agents
            max_workers: Maximum parallel workers (default: number of workers)

        Raises:
            TypeError: If workers is not a dict
            ValueError: If workers is empty
        """
        super().__init__(model)

        # Step 1: Type checking
        if not isinstance(workers, dict):
            raise TypeError("workers must be a dict")

        # Step 2: Input validation
        if not workers:
            raise ValueError("must have at least one worker")

        # Step 3: Set attributes
        self.workers = workers
        self.max_workers = max_workers if max_workers else len(workers)

    def execute(self, task: dict[str, Any]) -> dict[str, Any]:
        """Execute hierarchical delegation pattern.

        The manager delegates subtasks to workers in parallel using ThreadPoolExecutor,
        then synthesizes their results into a coherent response.

        Args:
            task: Task with 'query' key

        Returns:
            Result with synthesis, worker_count, status, metrics

        Raises:
            TypeError: If task is not a dict
            ValueError: If task missing 'query'
            RuntimeError: If all workers fail

        Example:
            >>> from unittest.mock import MagicMock
            >>> # Create specialized workers
            >>> financial_worker = MagicMock()
            >>> financial_worker.process.return_value = {"result": "Stock price: $150"}
            >>> market_worker = MagicMock()
            >>> market_worker.process.return_value = {"result": "Market trend: bullish"}
            >>> # Create hierarchical agent
            >>> agent = HierarchicalAgent(
            ...     model="gpt-4o-mini",
            ...     workers={"financial": financial_worker, "market": market_worker}
            ... )
            >>> # Execute task
            >>> result = agent.execute({"query": "Should I invest in Tesla?"})
            >>> result["status"]
            'success'
            >>> result["worker_count"]
            2
        """
        start_time = time.time()

        # Step 1: Type checking
        if not isinstance(task, dict):
            raise TypeError("task must be a dict")

        # Step 2: Input validation
        if "query" not in task:
            raise ValueError("task must contain 'query'")

        # Step 3: Delegate to workers in parallel
        worker_results = []
        worker_latencies = {}
        failures = {}

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all worker tasks
            future_to_worker = {
                executor.submit(worker.process, task): name
                for name, worker in self.workers.items()
            }

            # Collect results as they complete
            for future in as_completed(future_to_worker):
                worker_name = future_to_worker[future]
                worker_start = time.time()

                try:
                    result = future.result()
                    worker_results.append(result)
                    worker_latencies[worker_name] = time.time() - worker_start
                except Exception as e:
                    logger.error(
                        f"Worker '{worker_name}' failed in HierarchicalAgent: "
                        f"{type(e).__name__}: {e}"
                    )
                    failures[worker_name] = str(e)

        # Step 4: Handle failures
        if not worker_results:
            raise RuntimeError("All workers failed")

        # Step 5: Synthesize results
        synthesis = self._synthesize_worker_results(worker_results)

        # Step 6: Prepare result
        total_latency = time.time() - start_time

        result = {
            "status": "partial_success" if failures else "success",
            "synthesis": synthesis,
            "worker_count": len(self.workers),
            "successful_workers": len(worker_results),
            "metrics": {
                "latency": total_latency,
                "worker_latencies": worker_latencies,
            },
        }

        if failures:
            result["failures"] = failures

        return result

    def _synthesize_worker_results(self, worker_results: list[dict[str, Any]]) -> str:
        """Synthesize worker results using LLM.

        NOTE: This method has fallback logic, so @retry_litellm_call is not used.
        For methods without fallbacks, apply @retry_litellm_call decorator.

        Args:
            worker_results: List of worker result dictionaries

        Returns:
            Synthesized response string
        """
        # Use LiteLLM to synthesize results
        synthesis_prompt = f"""Synthesize the following worker results into a coherent response:

Worker Results:
{worker_results}

Provide a comprehensive synthesis that combines insights from all workers."""

        try:
            response = litellm.completion(
                model=self.model,
                messages=[{"role": "user", "content": synthesis_prompt}],
            )
            return response.choices[0].message.content
        except Exception as e:
            # Fallback: concatenate worker results if LLM synthesis fails
            logger.warning(
                f"LLM synthesis failed in HierarchicalAgent: {type(e).__name__}: {e}. "
                "Using fallback concatenation."
            )
            return " | ".join(
                [str(result.get("result", "")) for result in worker_results]
            )


# =============================================================================
# DiamondAgent - Competitive Broadcast + Selection Pattern
# =============================================================================


class DiamondAgent(MultiAgentPattern):
    """Competitive broadcast + selection pattern.

    Broadcasts query to multiple agents in parallel, then selects the best
    response based on quality criteria (confidence, accuracy, etc.).
    """

    def __init__(
        self,
        model: str,
        agents: list[Any],
        selection_criteria: list[str] | None = None,
        mode: str = "select",
    ) -> None:
        """Initialize diamond agent.

        Args:
            model: LLM model identifier
            agents: List of candidate agents
            selection_criteria: List of quality criteria for selection
            mode: Selection mode ("select", "merge", "voting")

        Raises:
            TypeError: If agents is not a list
            ValueError: If agents has less than 2 items
        """
        super().__init__(model)

        # Step 1: Type checking
        if not isinstance(agents, list):
            raise TypeError("agents must be a list")

        # Step 2: Input validation
        if len(agents) < 2:
            raise ValueError("must have at least 2 agents")

        # Step 3: Set attributes
        self.agents = agents
        self.selection_criteria = selection_criteria or ["confidence"]
        self.mode = mode

    def execute(self, task: dict[str, Any]) -> dict[str, Any]:
        """Execute diamond broadcast + selection pattern.

        Broadcasts query to all agents in parallel, then selects the best response
        based on configured selection criteria (confidence, accuracy, etc.).

        Args:
            task: Task with 'query' key

        Returns:
            Result with selected_response, broadcast_count, status, metrics

        Raises:
            TypeError: If task is not a dict
            RuntimeError: If all agents fail

        Example:
            >>> from unittest.mock import MagicMock
            >>> # Create competing agents
            >>> agent1 = MagicMock()
            >>> agent1.process.return_value = {"response": "Answer A", "confidence": 0.8}
            >>> agent2 = MagicMock()
            >>> agent2.process.return_value = {"response": "Answer B", "confidence": 0.95}
            >>> # Create diamond agent with selection mode
            >>> diamond = DiamondAgent(
            ...     model="gpt-4o-mini",
            ...     agents=[agent1, agent2],
            ...     selection_criteria=["confidence"]
            ... )
            >>> # Execute task
            >>> result = diamond.execute({"query": "What's the best approach?"})
            >>> result["selected_response"]  # Highest confidence wins
            'Answer B'
            >>> result["selection_reason"]
            'highest_confidence'
        """
        start_time = time.time()

        # Step 1: Type checking
        if not isinstance(task, dict):
            raise TypeError("task must be a dict")

        # Step 2: Broadcast to all agents in parallel
        agent_responses = []
        agent_latencies = []
        failures = 0

        with ThreadPoolExecutor(max_workers=len(self.agents)) as executor:
            future_to_agent = {
                executor.submit(agent.process, task): idx
                for idx, agent in enumerate(self.agents)
            }

            for future in as_completed(future_to_agent):
                agent_idx = future_to_agent[future]
                agent_start = time.time()

                try:
                    result = future.result()
                    agent_responses.append(result)
                    agent_latencies.append(time.time() - agent_start)
                except Exception as e:
                    logger.error(
                        f"Agent {agent_idx} failed in DiamondAgent: "
                        f"{type(e).__name__}: {e}"
                    )
                    failures += 1

        # Step 3: Handle complete failure
        if not agent_responses:
            raise RuntimeError("All agents failed")

        # Step 4: Select best response based on mode
        if self.mode == "merge":
            final_response = self._merge_responses(agent_responses)
            result = {
                "status": "partial_success" if failures else "success",
                "broadcast_count": len(self.agents),
                "merged_response": final_response,
                "successful_agents": len(agent_responses),
                "metrics": {
                    "total_latency": time.time() - start_time,
                    "agent_latencies": agent_latencies,
                },
            }
        elif self.mode == "voting":
            selected, vote_count = self._majority_voting(agent_responses)
            result = {
                "status": "partial_success" if failures else "success",
                "broadcast_count": len(self.agents),
                "selected_response": selected,
                "vote_count": vote_count,
                "successful_agents": len(agent_responses),
                "metrics": {
                    "total_latency": time.time() - start_time,
                    "agent_latencies": agent_latencies,
                },
            }
        else:  # mode == "select"
            best_idx, best_response, reason = self._select_best_response(
                agent_responses
            )
            result = {
                "status": "partial_success" if failures else "success",
                "broadcast_count": len(self.agents),
                "selected_response": best_response,
                "selected_agent": best_idx,
                "selection_reason": reason,
                "successful_agents": len(agent_responses),
                "all_identical": self._check_all_identical(agent_responses),
                "metrics": {
                    "total_latency": time.time() - start_time,
                    "agent_latencies": agent_latencies,
                },
            }

        return result

    def _select_best_response(
        self, responses: list[dict[str, Any]]
    ) -> tuple[int, str, str]:
        """Select best response based on selection criteria.

        Args:
            responses: List of agent response dictionaries

        Returns:
            Tuple of (best_agent_index, best_response, selection_reason)
        """
        # Calculate score for each response based on criteria
        best_score = -1
        best_idx = 0
        best_response = responses[0].get("response", "")

        for idx, resp in enumerate(responses):
            score = 0
            for criterion in self.selection_criteria:
                score += resp.get(criterion, 0)

            if score > best_score:
                best_score = score
                best_idx = idx
                best_response = resp.get("response", "")

        reason = (
            "highest_confidence"
            if "confidence" in self.selection_criteria
            else "highest_score"
        )

        return best_idx, best_response, reason

    def _merge_responses(self, responses: list[dict[str, Any]]) -> str:
        """Merge all responses into single comprehensive response.

        Args:
            responses: List of agent response dictionaries

        Returns:
            Merged response string
        """
        merged_content = "\n\n".join([resp.get("response", "") for resp in responses])
        return merged_content

    def _majority_voting(self, responses: list[dict[str, Any]]) -> tuple[str, int]:
        """Select response by majority voting.

        Args:
            responses: List of agent response dictionaries

        Returns:
            Tuple of (majority_response, vote_count)
        """
        response_texts = [resp.get("response", "") for resp in responses]
        counter = Counter(response_texts)
        majority_response, vote_count = counter.most_common(1)[0]
        return majority_response, vote_count

    def _check_all_identical(self, responses: list[dict[str, Any]]) -> bool:
        """Check if all responses are identical.

        Args:
            responses: List of agent response dictionaries

        Returns:
            True if all responses are identical, False otherwise
        """
        if not responses:
            return True

        first_response = responses[0].get("response", "")
        return all(resp.get("response", "") == first_response for resp in responses)


# =============================================================================
# P2PAgent - Peer-to-Peer Handoff Pattern
# =============================================================================


class P2PAgent(MultiAgentPattern):
    """Peer-to-peer handoff with context transfer.

    Routes queries to specialized agents based on domain classification,
    maintaining conversation history across handoffs.
    """

    def __init__(
        self,
        model: str,
        specialists: dict[str, Any],
        context_history: list[dict[str, str]] | None = None,
        max_history_turns: int = 10,
        max_context_tokens: int = 4000,
        max_handoffs: int = 10,
    ) -> None:
        """Initialize P2P agent.

        Args:
            model: LLM model identifier
            specialists: Dictionary mapping domain names to specialist agents
            context_history: Initial conversation history
            max_history_turns: Maximum conversation turns to keep
            max_context_tokens: Maximum context size in tokens
            max_handoffs: Maximum handoffs to prevent loops

        Raises:
            TypeError: If specialists is not a dict
            ValueError: If specialists is empty
        """
        super().__init__(model)

        # Step 1: Type checking
        if not isinstance(specialists, dict):
            raise TypeError("specialists must be a dict")

        # Step 2: Input validation
        if not specialists:
            raise ValueError("must have at least one specialist")

        # Step 3: Set attributes
        self.specialists = specialists
        self.context_history = context_history or []
        self.max_history_turns = max_history_turns
        self.max_context_tokens = max_context_tokens
        self.max_handoffs = max_handoffs
        self._handoff_count = 0
        self._last_domain: str | None = None

    def execute(self, task: dict[str, Any]) -> dict[str, Any]:
        """Execute P2P handoff pattern.

        Routes queries to specialized agents based on domain classification,
        maintaining conversation history across handoffs for context continuity.

        Args:
            task: Task with 'query' key

        Returns:
            Result with routed_to, classified_domain, context_package, metrics

        Raises:
            TypeError: If task is not a dict or query is not a string
            ValueError: If context exceeds token limit or query is empty
            RuntimeError: If max handoffs exceeded

        Example:
            >>> from unittest.mock import MagicMock, patch
            >>> # Create domain specialists
            >>> finance_agent = MagicMock()
            >>> finance_agent.process.return_value = {"response": "Stock data here"}
            >>> weather_agent = MagicMock()
            >>> weather_agent.process.return_value = {"response": "Forecast here"}
            >>> # Create P2P agent
            >>> p2p = P2PAgent(
            ...     model="gpt-4o-mini",
            ...     specialists={"finance": finance_agent, "weather": weather_agent}
            ... )
            >>> # Simulate domain classification
            >>> with patch.object(p2p, '_classify_domain', return_value='finance'):
            ...     result = p2p.execute({"query": "Tesla stock price?"})
            >>> result["routed_to"]
            'finance'
            >>> "conversation_history" in result["context_package"]
            True
        """
        start_time = time.time()

        # Step 1: Type checking
        if not isinstance(task, dict):
            raise TypeError("task must be a dict")

        # Step 2: Query validation
        query = task.get("query")
        if not isinstance(query, str):
            raise TypeError("task['query'] must be a string")
        if not query:
            raise ValueError("task['query'] must be non-empty")

        # Step 3: Check context size
        context_tokens = self._estimate_context_tokens()
        if context_tokens > self.max_context_tokens:
            raise ValueError("Context exceeds token limit")

        # Step 4: Check handoff limit
        if self._handoff_count >= self.max_handoffs:
            raise RuntimeError("Max handoffs exceeded")

        # Step 5: Classify domain
        domain = self._classify_domain(query)

        # Step 6: Route to specialist
        if domain in self.specialists:
            specialist = self.specialists[domain]
            response = specialist.process(task)
            routed_to = domain
            status = "success"
        else:
            # Fallback for unknown domain
            response = {"response": "Unable to classify domain"}
            routed_to = "general"
            status = "fallback"
            domain = "unknown"

        # Step 7: Package context for handoff
        context_package = {
            "conversation_history": self.context_history.copy(),
            "current_query": query,
            "current_domain": domain,
        }

        # Step 8: Update conversation history
        self.context_history.append({"role": "user", "content": query})
        self.context_history.append(
            {"role": "assistant", "content": response.get("response", "")}
        )

        # Trim history if needed
        if len(self.context_history) > self.max_history_turns * 2:
            self.context_history = self.context_history[-self.max_history_turns * 2 :]

        # Step 9: Track handoff
        self._handoff_count += 1
        handoff_type = (
            "domain_change"
            if self._last_domain and self._last_domain != domain
            else "same_domain"
        )
        self._last_domain = domain

        # Step 10: Prepare result
        result = {
            "status": status,
            "routed_to": routed_to,
            "classified_domain": domain,
            "context_package": context_package,
            "handoff_type": handoff_type,
            "metrics": {
                "handoff_latency": time.time() - start_time,
                "total_handoffs": self._handoff_count,
            },
        }

        return result

    def _classify_domain(self, query: str) -> str:
        """Classify query domain using LLM.

        Args:
            query: User query string

        Returns:
            Classified domain name
        """
        # Use LiteLLM to classify domain
        classification_prompt = f"""Classify the domain of this query.
Available domains: {list(self.specialists.keys())}

Query: {query}

Respond with ONLY the domain name (one word)."""

        try:
            response = litellm.completion(
                model=self.model,
                messages=[{"role": "user", "content": classification_prompt}],
            )
            domain = response.choices[0].message.content.strip().lower()
            return domain
        except Exception as e:
            # Fallback: return "unknown" if classification fails
            logger.warning(
                f"LLM domain classification failed in P2PAgent: {type(e).__name__}: {e}. "
                "Returning 'unknown' domain."
            )
            return "unknown"

    def _estimate_context_tokens(self) -> int:
        """Estimate token count for current context.

        Returns:
            Estimated token count
        """
        # Use module-level constant for token estimation
        total_chars = sum(len(msg.get("content", "")) for msg in self.context_history)
        return total_chars // TOKEN_ESTIMATION_CHARS_PER_TOKEN


# =============================================================================
# CollaborativeAgent - Shared Workspace Pattern
# =============================================================================


class CollaborativeAgent(MultiAgentPattern):
    """Shared workspace with peer review.

    Multiple agents collaborate on a task by contributing to a shared workspace,
    reviewing each other's work, and building consensus.
    """

    def __init__(
        self,
        model: str,
        collaborators: list[Any],
        max_rounds: int = 1,
        _defer_validation: bool = False,
    ) -> None:
        """Initialize collaborative agent.

        Args:
            model: LLM model identifier
            collaborators: List of collaborator agents
            max_rounds: Maximum collaboration rounds
            _defer_validation: **INTERNAL USE ONLY** - Defer validation for unit tests.
                               DO NOT use in production code.

        Raises:
            TypeError: If collaborators is not a list
            ValueError: If collaborators has less than 2 items (unless deferred)

        Note:
            The _defer_validation and _min_collaborators attributes are testing hooks
            to allow unit tests to verify workspace creation logic in isolation.
            Production code should NEVER use these parameters.
        """
        super().__init__(model)

        # Step 1: Type checking
        if not isinstance(collaborators, list):
            raise TypeError("collaborators must be a list")

        # Step 2: Set attributes
        self.collaborators = collaborators
        self.max_rounds = max_rounds
        self._min_collaborators = 2  # TESTING HOOK: Can be overridden in unit tests

        # Step 3: Validate collaborator count (unless deferred for testing)
        if not _defer_validation and len(collaborators) < self._min_collaborators:
            raise ValueError("must have at least 2 collaborators for collaboration")

    def execute(self, task: dict[str, Any]) -> dict[str, Any]:
        """Execute collaborative pattern with shared workspace.

        Args:
            task: Task with 'query' key

        Returns:
            Result with workspace, consensus, synthesized_response, metrics

        Raises:
            TypeError: If task is not a dict
            ValueError: If collaborators count less than minimum
        """
        start_time = time.time()

        # Step 1: Type checking
        if not isinstance(task, dict):
            raise TypeError("task must be a dict")

        # Step 2: Validate collaborator count (allows test override of _min_collaborators)
        if len(self.collaborators) < self._min_collaborators:
            raise ValueError("must have at least 2 collaborators for collaboration")

        # Step 3: Get max_rounds from task if provided
        max_rounds = task.get("max_rounds", self.max_rounds)

        # Step 4: Create shared workspace
        workspace = {
            "contributions": [],
            "peer_reviews": [],
        }

        # Step 5: Execute collaboration rounds
        rounds_completed = 0
        for round_num in range(max_rounds):
            rounds_completed += 1

            # Round 1: Collect contributions
            round_contributions = []
            for idx, collab in enumerate(self.collaborators):
                try:
                    contribution = collab.contribute(task)
                    if contribution:
                        round_contributions.append(contribution)
                except Exception as e:
                    logger.warning(
                        f"Collaborator {idx} failed to contribute in round {round_num + 1}: "
                        f"{type(e).__name__}: {e}"
                    )

            workspace["contributions"].extend(round_contributions)

            # Round 2+: Peer review
            if round_num > 0:
                round_reviews = []
                for idx, collab in enumerate(self.collaborators):
                    try:
                        review = collab.review(workspace["contributions"])
                        if review:
                            round_reviews.append(review)
                    except Exception as e:
                        logger.warning(
                            f"Collaborator {idx} failed to review in round {round_num + 1}: "
                            f"{type(e).__name__}: {e}"
                        )

                workspace["peer_reviews"].extend(round_reviews)

        # Step 6: Build consensus
        consensus = self._build_consensus(workspace["contributions"])

        # Step 7: Synthesize contributions
        synthesized_response = self._synthesize_contributions(
            workspace["contributions"]
        )

        # Step 8: Check for conflicting reviews
        conflicting_reviews = self._find_conflicting_reviews(workspace["peer_reviews"])

        # Step 9: Prepare result
        result = {
            "status": "partial_success"
            if len(workspace["contributions"]) < len(self.collaborators)
            else "success",
            "workspace": workspace,
            "consensus": consensus,
            "synthesized_response": synthesized_response,
            "rounds_completed": rounds_completed,
            "metrics": {
                "total_rounds": rounds_completed,
                "total_contributions": len(workspace["contributions"]),
                "collaboration_latency": time.time() - start_time,
            },
        }

        if conflicting_reviews:
            result["conflicting_reviews"] = conflicting_reviews

        return result

    def _build_consensus(self, contributions: list[dict[str, Any]]) -> dict[str, Any]:
        """Build consensus from contributions.

        Args:
            contributions: List of contribution dictionaries

        Returns:
            Consensus dictionary with agreement_level
        """
        if not contributions:
            return {"agreement_level": "none"}

        # Check agreement by comparing contribution content
        contents = [c.get("content", "") for c in contributions]
        unique_contents = set(contents)

        if len(unique_contents) == 1:
            agreement_level = "high"
            disagreements = []
        elif len(unique_contents) == len(contents):
            agreement_level = "low"
            disagreements = [
                {
                    "agents": list(range(len(contributions))),
                    "issue": "complete_disagreement",
                }
            ]
        else:
            agreement_level = "medium"
            disagreements = []

        return {
            "agreement_level": agreement_level,
            "disagreements": disagreements,
        }

    def _synthesize_contributions(self, contributions: list[dict[str, Any]]) -> str:
        """Synthesize all contributions into coherent response.

        Args:
            contributions: List of contribution dictionaries

        Returns:
            Synthesized response string
        """
        if not contributions:
            return ""

        # Combine all contributions
        all_content = []
        for contrib in contributions:
            content = contrib.get("content", "")
            if content:
                all_content.append(content)

        return " | ".join(all_content)

    def _find_conflicting_reviews(
        self, reviews: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Find conflicting peer reviews.

        Args:
            reviews: List of review dictionaries

        Returns:
            List of conflicting review pairs
        """
        conflicting = []

        for i, review1 in enumerate(reviews):
            for review2 in reviews[i + 1 :]:
                feedback1 = review1.get("feedback", "")
                feedback2 = review2.get("feedback", "")

                # Simple conflict detection: one positive, one negative
                if ("✅" in feedback1 and "⚠️" in feedback2) or (
                    "⚠️" in feedback1 and "✅" in feedback2
                ):
                    conflicting.append({"review1": feedback1, "review2": feedback2})

        return conflicting


# =============================================================================
# AdaptiveLoopAgent - Iterative Refinement Pattern
# =============================================================================


class AdaptiveLoopAgent(MultiAgentPattern):
    """Iterative refinement with quality threshold.

    Executes search queries iteratively, refining the query after each loop
    until quality threshold is met or max loops exceeded.
    """

    def __init__(
        self,
        model: str,
        quality_threshold: float = 0.8,
        max_loops: int = 5,
    ) -> None:
        """Initialize adaptive loop agent.

        Args:
            model: LLM model identifier
            quality_threshold: Quality threshold to reach (0.0-1.0)
            max_loops: Maximum refinement loops

        Raises:
            ValueError: If quality_threshold not in [0, 1]
            ValueError: If max_loops not positive
        """
        super().__init__(model)

        # Step 1: Input validation
        if not (0 <= quality_threshold <= 1):
            raise ValueError("quality_threshold must be between 0 and 1")

        if max_loops <= 0:
            raise ValueError("max_loops must be positive")

        # Step 2: Set attributes
        self.quality_threshold = quality_threshold
        self.max_loops = max_loops

    def execute(self, task: dict[str, Any]) -> dict[str, Any]:
        """Execute adaptive loop refinement pattern.

        Args:
            task: Task with 'query' key

        Returns:
            Result with loops_executed, final_quality, status, metrics

        Raises:
            TypeError: If task is not a dict
        """
        # Note: start_time would be used here for total execution time tracking
        # Currently not returned in result, but kept for future metrics

        # Step 1: Type checking
        if not isinstance(task, dict):
            raise TypeError("task must be a dict")

        # Step 2: Initialize tracking
        current_query = task["query"]
        quality_per_loop = []
        latency_per_loop = []
        best_quality = 0.0
        best_loop = 0
        # Note: best_results tracked but not currently used in result
        # Kept for potential future use (e.g., returning actual best results)
        previous_quality = 0.0

        # Step 3: Execute refinement loops
        for loop in range(1, self.max_loops + 1):
            loop_start = time.time()

            # Execute search
            search_result = self._execute_search(current_query)
            quality = search_result["quality"]
            quality_per_loop.append(quality)
            latency_per_loop.append(time.time() - loop_start)

            # Track best result
            if quality > best_quality:
                best_quality = quality
                best_loop = loop
                _ = search_result  # Track for future use (unused currently)

            # Check if threshold met
            if quality >= self.quality_threshold:
                # Early termination
                result = {
                    "status": "success",
                    "loops_executed": loop,
                    "final_quality": quality,
                    "early_termination": True,
                    "best_loop": loop,
                    "quality_per_loop": quality_per_loop,
                    "metrics": {
                        "latency_per_loop": latency_per_loop,
                    },
                }
                return result

            # Check for quality degradation (after first loop)
            if loop > 1 and quality < previous_quality:
                # Quality degraded - return best loop
                result = {
                    "status": "fallback",
                    "loops_executed": loop,
                    "final_quality": best_quality,
                    "best_loop": best_loop,
                    "fallback_strategy": "return_best_loop",
                    "quality_per_loop": quality_per_loop,
                    "metrics": {
                        "latency_per_loop": latency_per_loop,
                    },
                }
                return result

            previous_quality = quality

            # Refine query for next loop (only if not last loop)
            if loop < self.max_loops:
                current_query = self._refine_query(task["query"], loop)

        # Step 4: Max loops exceeded - return fallback
        result = {
            "status": "fallback",
            "loops_executed": self.max_loops,
            "final_quality": best_quality,
            "best_loop": best_loop,
            "fallback_strategy": "return_best_loop",
            "quality_per_loop": quality_per_loop,
            "metrics": {
                "latency_per_loop": latency_per_loop,
            },
        }

        return result

    def _execute_search(self, query: str) -> dict[str, Any]:
        """Execute search and return results with quality score.

        NOTE: This is a configurable mock for tutorial purposes.
        In production, this would integrate with actual search systems
        (e.g., semantic_retrieval.py from Lesson 12).

        Args:
            query: Search query string

        Returns:
            Dictionary with results and quality score (0.0-1.0)

        Mock Behavior:
            - Quality increases with query specificity (word count)
            - Simulates progressive refinement benefits
            - For production: replace with actual search + quality scoring
        """
        # Mock quality based on query length (simulates refinement improving quality)
        word_count = len(query.split())

        # Quality improves with more specific queries (more words)
        # But degrades if query gets too long (over-constrained)
        if word_count <= 2:
            quality = 0.4
        elif word_count <= 4:
            quality = 0.6
        elif word_count <= 6:
            quality = 0.75
        elif word_count <= 8:
            quality = 0.85
        else:
            # Over-constrained queries degrade quality
            quality = max(0.3, 0.9 - (word_count - 8) * 0.1)

        # Generate mock results
        num_results = min(10, max(1, int(quality * 10)))
        results = [f"Result {i + 1}" for i in range(num_results)]

        return {
            "results": results,
            "quality": quality,
        }

    def _refine_query(self, original_query: str, loop: int) -> str:
        """Refine query based on loop iteration.

        Args:
            original_query: Original user query
            loop: Current loop iteration number

        Returns:
            Refined query string
        """
        # Progressive refinement strategies
        if loop == 1:
            # Loop 1: Add synonyms and related terms
            if "vegan" in original_query.lower():
                return original_query + " OR vegetarian OR plant-based"
            else:
                return original_query + " related terms"
        elif loop == 2:
            # Loop 2: Broaden search
            return original_query.replace(" with ", " ")
        else:
            # Loop 3+: Remove constraints progressively
            words = original_query.split()
            # Keep only first portion of words (using QUERY_REDUCTION_RATIO)
            reduced_count = max(1, int(len(words) * QUERY_REDUCTION_RATIO))
            reduced_words = words[:reduced_count]
            return " ".join(reduced_words)
