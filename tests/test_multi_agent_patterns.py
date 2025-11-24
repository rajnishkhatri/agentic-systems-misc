"""Tests for Multi-Agent Design Patterns (Lesson 14 - Task 5.5).

TDD-RED Phase: Tests for 5 coordination pattern implementations.

Test Naming Convention: test_should_[expected_result]_when_[condition]

Test Coverage:
- MultiAgentPattern abstract base class - 5 tests
- HierarchicalAgent class - 12 tests
- DiamondAgent class - 12 tests
- P2PAgent class - 12 tests
- CollaborativeAgent class - 12 tests
- AdaptiveLoopAgent class - 12 tests

Total: 65 tests

Created: 2025-11-15
Task: 5.5 from tasks-0005-prd-rag-agent-evaluation-tutorial-system.md
Pattern: TDD-RED phase (write tests before implementation)
"""

from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from backend.multi_agent_patterns import (
    AdaptiveLoopAgent,
    CollaborativeAgent,
    DiamondAgent,
    HierarchicalAgent,
    MultiAgentPattern,
    P2PAgent,
)

# =============================================================================
# MultiAgentPattern Abstract Base Class Tests
# =============================================================================


class TestMultiAgentPattern:
    """Test suite for MultiAgentPattern abstract base class."""

    def test_should_raise_error_when_instantiating_base_class(self) -> None:
        """Test that MultiAgentPattern cannot be instantiated directly."""
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            MultiAgentPattern(model="gpt-4o-mini")  # type: ignore

    def test_should_require_execute_method_implementation(self) -> None:
        """Test that subclasses must implement execute() method."""

        class IncompletePattern(MultiAgentPattern):
            """Pattern without execute() implementation."""

            pass

        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            IncompletePattern(model="gpt-4o-mini")  # type: ignore

    def test_should_allow_instantiation_when_execute_implemented(self) -> None:
        """Test that complete subclass can be instantiated."""

        class CompletePattern(MultiAgentPattern):
            """Pattern with execute() implementation."""

            def execute(self, task: dict[str, Any]) -> dict[str, Any]:
                return {"status": "success"}

        pattern = CompletePattern(model="gpt-4o-mini")
        assert pattern.model == "gpt-4o-mini"

    def test_should_raise_error_for_invalid_model_type(self) -> None:
        """Test that MultiAgentPattern validates model type."""

        class CompletePattern(MultiAgentPattern):
            def execute(self, task: dict[str, Any]) -> dict[str, Any]:
                return {"status": "success"}

        with pytest.raises(TypeError, match="model must be a string"):
            CompletePattern(model=123)  # type: ignore

    def test_should_raise_error_for_empty_model_name(self) -> None:
        """Test that MultiAgentPattern rejects empty model names."""

        class CompletePattern(MultiAgentPattern):
            def execute(self, task: dict[str, Any]) -> dict[str, Any]:
                return {"status": "success"}

        with pytest.raises(ValueError, match="model must be non-empty"):
            CompletePattern(model="")


# =============================================================================
# HierarchicalAgent Tests (Manager-Worker Pattern)
# =============================================================================


class TestHierarchicalAgent:
    """Test suite for HierarchicalAgent (Manager-Worker coordination)."""

    def test_should_create_instance_with_valid_workers(self) -> None:
        """Test that HierarchicalAgent initializes with worker agents."""
        workers = {"financial": MagicMock(), "market": MagicMock()}
        agent = HierarchicalAgent(model="gpt-4o-mini", workers=workers)
        assert agent.model == "gpt-4o-mini"
        assert agent.workers == workers

    def test_should_raise_error_when_workers_not_dict(self) -> None:
        """Test that HierarchicalAgent validates workers type."""
        with pytest.raises(TypeError, match="workers must be a dict"):
            HierarchicalAgent(model="gpt-4o-mini", workers=[])  # type: ignore

    def test_should_raise_error_when_workers_empty(self) -> None:
        """Test that HierarchicalAgent requires at least one worker."""
        with pytest.raises(ValueError, match="must have at least one worker"):
            HierarchicalAgent(model="gpt-4o-mini", workers={})

    @patch("backend.multi_agent_patterns.litellm.completion")
    def test_should_delegate_task_to_workers_in_parallel(
        self, mock_completion: MagicMock
    ) -> None:
        """Test that manager delegates to workers using ThreadPoolExecutor."""
        # Mock LLM responses
        mock_completion.side_effect = [
            MagicMock(
                choices=[MagicMock(message=MagicMock(content="delegation strategy"))]
            ),  # Manager plan
            MagicMock(
                choices=[MagicMock(message=MagicMock(content="financial data"))]
            ),  # Worker 1
            MagicMock(
                choices=[MagicMock(message=MagicMock(content="market trends"))]
            ),  # Worker 2
            MagicMock(
                choices=[MagicMock(message=MagicMock(content="final synthesis"))]
            ),  # Manager synthesis
        ]

        worker1 = MagicMock()
        worker1.process.return_value = {"result": "financial data"}
        worker2 = MagicMock()
        worker2.process.return_value = {"result": "market trends"}

        agent = HierarchicalAgent(
            model="gpt-4o-mini", workers={"financial": worker1, "market": worker2}
        )
        result = agent.execute({"query": "Should I invest in Tesla?"})

        assert result["status"] == "success"
        assert "synthesis" in result
        worker1.process.assert_called_once()
        worker2.process.assert_called_once()

    @patch("backend.multi_agent_patterns.litellm.completion")
    def test_should_synthesize_worker_results_when_all_complete(
        self, mock_completion: MagicMock
    ) -> None:
        """Test that manager synthesizes results from all workers."""
        mock_completion.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="synthesized response"))]
        )

        worker1 = MagicMock()
        worker1.process.return_value = {"result": "data 1"}
        worker2 = MagicMock()
        worker2.process.return_value = {"result": "data 2"}

        agent = HierarchicalAgent(
            model="gpt-4o-mini", workers={"w1": worker1, "w2": worker2}
        )
        result = agent.execute({"query": "test"})

        assert "synthesis" in result
        assert result["worker_count"] == 2

    def test_should_handle_worker_failure_gracefully(self) -> None:
        """Test that system handles worker failures without crashing."""
        worker1 = MagicMock()
        worker1.process.side_effect = Exception("Worker 1 failed")
        worker2 = MagicMock()
        worker2.process.return_value = {"result": "data 2"}

        agent = HierarchicalAgent(
            model="gpt-4o-mini", workers={"w1": worker1, "w2": worker2}
        )
        result = agent.execute({"query": "test"})

        assert result["status"] == "partial_success"
        assert "w1" in result["failures"]
        assert result["successful_workers"] == 1

    def test_should_raise_error_when_all_workers_fail(self) -> None:
        """Test that agent raises error when all workers fail."""
        worker1 = MagicMock()
        worker1.process.side_effect = Exception("Failed")
        worker2 = MagicMock()
        worker2.process.side_effect = Exception("Failed")

        agent = HierarchicalAgent(
            model="gpt-4o-mini", workers={"w1": worker1, "w2": worker2}
        )

        with pytest.raises(RuntimeError, match="All workers failed"):
            agent.execute({"query": "test"})

    def test_should_raise_error_for_invalid_task_type(self) -> None:
        """Test that execute() validates task type."""
        agent = HierarchicalAgent(
            model="gpt-4o-mini", workers={"w1": MagicMock()}
        )

        with pytest.raises(TypeError, match="task must be a dict"):
            agent.execute("not a dict")  # type: ignore

    def test_should_raise_error_for_empty_task(self) -> None:
        """Test that execute() rejects empty tasks."""
        agent = HierarchicalAgent(
            model="gpt-4o-mini", workers={"w1": MagicMock()}
        )

        with pytest.raises(ValueError, match="task must contain 'query'"):
            agent.execute({})

    def test_should_track_execution_metrics(self) -> None:
        """Test that agent tracks latency and cost metrics."""
        worker1 = MagicMock()
        worker1.process.return_value = {"result": "data"}

        agent = HierarchicalAgent(
            model="gpt-4o-mini", workers={"w1": worker1}
        )
        result = agent.execute({"query": "test"})

        assert "metrics" in result
        assert "latency" in result["metrics"]
        assert "worker_latencies" in result["metrics"]
        assert result["metrics"]["latency"] > 0

    def test_should_use_max_workers_parameter(self) -> None:
        """Test that ThreadPoolExecutor respects max_workers limit."""
        workers = {f"w{i}": MagicMock() for i in range(10)}
        for w in workers.values():
            w.process.return_value = {"result": "data"}

        agent = HierarchicalAgent(
            model="gpt-4o-mini", workers=workers, max_workers=3
        )
        result = agent.execute({"query": "test"})

        assert result["status"] == "success"
        assert result["worker_count"] == 10


# =============================================================================
# DiamondAgent Tests (Competitive + Selection Pattern)
# =============================================================================


class TestDiamondAgent:
    """Test suite for DiamondAgent (Broadcast → Parallel → Select Best)."""

    def test_should_create_instance_with_valid_agents(self) -> None:
        """Test that DiamondAgent initializes with multiple agents."""
        agents = [MagicMock(), MagicMock(), MagicMock()]
        agent = DiamondAgent(model="gpt-4o-mini", agents=agents)
        assert agent.model == "gpt-4o-mini"
        assert len(agent.agents) == 3

    def test_should_raise_error_when_agents_not_list(self) -> None:
        """Test that DiamondAgent validates agents type."""
        with pytest.raises(TypeError, match="agents must be a list"):
            DiamondAgent(model="gpt-4o-mini", agents={})  # type: ignore

    def test_should_raise_error_when_agents_less_than_two(self) -> None:
        """Test that DiamondAgent requires at least 2 agents."""
        with pytest.raises(ValueError, match="must have at least 2 agents"):
            DiamondAgent(model="gpt-4o-mini", agents=[MagicMock()])

    @patch("backend.multi_agent_patterns.litellm.completion")
    def test_should_broadcast_query_to_all_agents_in_parallel(
        self, mock_completion: MagicMock
    ) -> None:
        """Test that query is broadcast to all agents simultaneously."""
        agent1 = MagicMock()
        agent1.process.return_value = {"response": "Answer 1", "confidence": 0.8}
        agent2 = MagicMock()
        agent2.process.return_value = {"response": "Answer 2", "confidence": 0.9}
        agent3 = MagicMock()
        agent3.process.return_value = {"response": "Answer 3", "confidence": 0.7}

        mock_completion.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="Best answer: Answer 2"))]
        )

        diamond = DiamondAgent(model="gpt-4o-mini", agents=[agent1, agent2, agent3])
        result = diamond.execute({"query": "test query"})

        agent1.process.assert_called_once()
        agent2.process.assert_called_once()
        agent3.process.assert_called_once()
        assert result["broadcast_count"] == 3

    @patch("backend.multi_agent_patterns.litellm.completion")
    def test_should_select_best_response_when_multiple_available(
        self, mock_completion: MagicMock
    ) -> None:
        """Test that moderator selects highest-quality response."""
        agent1 = MagicMock()
        agent1.process.return_value = {"response": "Answer 1", "confidence": 0.6}
        agent2 = MagicMock()
        agent2.process.return_value = {"response": "Answer 2", "confidence": 0.95}
        agent3 = MagicMock()
        agent3.process.return_value = {"response": "Answer 3", "confidence": 0.7}

        mock_completion.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="Answer 2"))]
        )

        diamond = DiamondAgent(model="gpt-4o-mini", agents=[agent1, agent2, agent3])
        result = diamond.execute({"query": "test"})

        assert result["selected_response"] == "Answer 2"
        assert result["selection_reason"] == "highest_confidence"

    def test_should_evaluate_on_quality_criteria(self) -> None:
        """Test that moderator uses quality criteria for selection."""
        agent1 = MagicMock()
        agent1.process.return_value = {
            "response": "Answer 1",
            "confidence": 0.8,
            "accuracy": 0.7,
        }
        agent2 = MagicMock()
        agent2.process.return_value = {
            "response": "Answer 2",
            "confidence": 0.9,
            "accuracy": 0.95,
        }

        diamond = DiamondAgent(
            model="gpt-4o-mini",
            agents=[agent1, agent2],
            selection_criteria=["confidence", "accuracy"],
        )
        result = diamond.execute({"query": "test"})

        assert result["selected_agent"] == 1  # Agent 2 has higher combined score

    def test_should_handle_all_agents_failing(self) -> None:
        """Test that diamond pattern handles complete failure gracefully."""
        agent1 = MagicMock()
        agent1.process.side_effect = Exception("Failed")
        agent2 = MagicMock()
        agent2.process.side_effect = Exception("Failed")

        diamond = DiamondAgent(model="gpt-4o-mini", agents=[agent1, agent2])

        with pytest.raises(RuntimeError, match="All agents failed"):
            diamond.execute({"query": "test"})

    def test_should_handle_partial_agent_failures(self) -> None:
        """Test that system works when some agents fail."""
        agent1 = MagicMock()
        agent1.process.side_effect = Exception("Failed")
        agent2 = MagicMock()
        agent2.process.return_value = {"response": "Answer 2", "confidence": 0.9}

        diamond = DiamondAgent(model="gpt-4o-mini", agents=[agent1, agent2])
        result = diamond.execute({"query": "test"})

        assert result["status"] == "partial_success"
        assert result["successful_agents"] == 1
        assert result["selected_response"] == "Answer 2"

    def test_should_merge_responses_when_mode_is_merge(self) -> None:
        """Test response merging instead of selection."""
        agent1 = MagicMock()
        agent1.process.return_value = {"response": "Point A"}
        agent2 = MagicMock()
        agent2.process.return_value = {"response": "Point B"}

        diamond = DiamondAgent(
            model="gpt-4o-mini", agents=[agent1, agent2], mode="merge"
        )
        result = diamond.execute({"query": "test"})

        assert "merged_response" in result
        assert "Point A" in str(result["merged_response"])
        assert "Point B" in str(result["merged_response"])

    def test_should_use_majority_voting_when_configured(self) -> None:
        """Test majority voting for categorical outputs."""
        agent1 = MagicMock()
        agent1.process.return_value = {"response": "Category A"}
        agent2 = MagicMock()
        agent2.process.return_value = {"response": "Category A"}
        agent3 = MagicMock()
        agent3.process.return_value = {"response": "Category B"}

        diamond = DiamondAgent(
            model="gpt-4o-mini", agents=[agent1, agent2, agent3], mode="voting"
        )
        result = diamond.execute({"query": "test"})

        assert result["selected_response"] == "Category A"
        assert result["vote_count"] == 2

    def test_should_track_parallel_execution_metrics(self) -> None:
        """Test that diamond tracks latency for parallel execution."""
        agents = [MagicMock() for _ in range(3)]
        for a in agents:
            a.process.return_value = {"response": "Answer", "confidence": 0.8}

        diamond = DiamondAgent(model="gpt-4o-mini", agents=agents)
        result = diamond.execute({"query": "test"})

        assert "metrics" in result
        assert "total_latency" in result["metrics"]
        assert "agent_latencies" in result["metrics"]
        assert len(result["metrics"]["agent_latencies"]) == 3

    def test_should_raise_error_for_invalid_task_type(self) -> None:
        """Test that execute() validates task type."""
        diamond = DiamondAgent(
            model="gpt-4o-mini", agents=[MagicMock(), MagicMock()]
        )

        with pytest.raises(TypeError, match="task must be a dict"):
            diamond.execute("not a dict")  # type: ignore

    def test_should_handle_identical_responses(self) -> None:
        """Test handling when all agents return same response."""
        agents = [MagicMock() for _ in range(3)]
        for a in agents:
            a.process.return_value = {"response": "Same answer", "confidence": 0.8}

        diamond = DiamondAgent(model="gpt-4o-mini", agents=agents)
        result = diamond.execute({"query": "test"})

        assert result["status"] == "success"
        assert result["all_identical"] is True


# =============================================================================
# P2PAgent Tests (Peer-to-Peer Handoff Pattern)
# =============================================================================


class TestP2PAgent:
    """Test suite for P2PAgent (Peer-to-Peer Handoff with Context Transfer)."""

    def test_should_create_instance_with_specialists(self) -> None:
        """Test that P2PAgent initializes with specialist agents."""
        specialists = {"finance": MagicMock(), "weather": MagicMock()}
        agent = P2PAgent(model="gpt-4o-mini", specialists=specialists)
        assert agent.model == "gpt-4o-mini"
        assert agent.specialists == specialists

    def test_should_raise_error_when_specialists_not_dict(self) -> None:
        """Test that P2PAgent validates specialists type."""
        with pytest.raises(TypeError, match="specialists must be a dict"):
            P2PAgent(model="gpt-4o-mini", specialists=[])  # type: ignore

    def test_should_raise_error_when_specialists_empty(self) -> None:
        """Test that P2PAgent requires at least one specialist."""
        with pytest.raises(ValueError, match="must have at least one specialist"):
            P2PAgent(model="gpt-4o-mini", specialists={})

    @patch("backend.multi_agent_patterns.litellm.completion")
    def test_should_classify_domain_when_processing_query(
        self, mock_completion: MagicMock
    ) -> None:
        """Test that agent classifies query domain."""
        mock_completion.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="finance"))]
        )

        specialists = {"finance": MagicMock(), "weather": MagicMock()}
        agent = P2PAgent(model="gpt-4o-mini", specialists=specialists)
        result = agent.execute({"query": "What's the stock price?"})

        assert result["classified_domain"] == "finance"

    @patch("backend.multi_agent_patterns.litellm.completion")
    def test_should_package_context_when_handing_off(
        self, mock_completion: MagicMock
    ) -> None:
        """Test that context is properly packaged for handoff."""
        mock_completion.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="finance"))]
        )

        finance_agent = MagicMock()
        finance_agent.process.return_value = {"response": "Stock answer"}

        agent = P2PAgent(
            model="gpt-4o-mini",
            specialists={"finance": finance_agent},
            context_history=[
                {"role": "user", "content": "Previous question"},
                {"role": "assistant", "content": "Previous answer"},
            ],
        )
        result = agent.execute({"query": "Stock question"})

        # Check that context was passed
        assert "context_package" in result
        assert "conversation_history" in result["context_package"]
        assert len(result["context_package"]["conversation_history"]) >= 2

    def test_should_route_to_specialist_when_domain_detected(self) -> None:
        """Test that query is routed to correct specialist."""
        finance_agent = MagicMock()
        finance_agent.process.return_value = {"response": "Finance answer"}
        weather_agent = MagicMock()

        agent = P2PAgent(
            model="gpt-4o-mini",
            specialists={"finance": finance_agent, "weather": weather_agent},
        )

        # Mock domain classification
        with patch.object(agent, "_classify_domain", return_value="finance"):
            result = agent.execute({"query": "Stock question"})

        finance_agent.process.assert_called_once()
        weather_agent.process.assert_not_called()
        assert result["routed_to"] == "finance"

    def test_should_maintain_conversation_history_across_handoffs(self) -> None:
        """Test that conversation history is preserved across handoffs."""
        finance_agent = MagicMock()
        finance_agent.process.return_value = {"response": "Finance answer"}

        agent = P2PAgent(
            model="gpt-4o-mini",
            specialists={"finance": finance_agent},
            max_history_turns=10,
        )

        # First handoff
        with patch.object(agent, "_classify_domain", return_value="finance"):
            result1 = agent.execute({"query": "First question"})

        # Second handoff
        with patch.object(agent, "_classify_domain", return_value="finance"):
            result2 = agent.execute({"query": "Second question"})

        assert len(agent.context_history) == 4  # 2 turns × 2 messages

    def test_should_handoff_back_when_domain_changes(self) -> None:
        """Test bidirectional handoff when domain changes."""
        finance_agent = MagicMock()
        finance_agent.process.return_value = {"response": "Finance answer"}
        weather_agent = MagicMock()
        weather_agent.process.return_value = {"response": "Weather answer"}

        agent = P2PAgent(
            model="gpt-4o-mini",
            specialists={"finance": finance_agent, "weather": weather_agent},
        )

        # Handoff to finance
        with patch.object(agent, "_classify_domain", return_value="finance"):
            result1 = agent.execute({"query": "Stock question"})

        # Handoff to weather (domain change)
        with patch.object(agent, "_classify_domain", return_value="weather"):
            result2 = agent.execute({"query": "Weather question"})

        assert result1["routed_to"] == "finance"
        assert result2["routed_to"] == "weather"
        assert result2["handoff_type"] == "domain_change"

    def test_should_raise_error_when_context_too_large(self) -> None:
        """Test that agent raises error when context exceeds token limit."""
        finance_agent = MagicMock()

        agent = P2PAgent(
            model="gpt-4o-mini",
            specialists={"finance": finance_agent},
            max_context_tokens=100,
        )

        # Create very large history
        agent.context_history = [
            {"role": "user", "content": "x" * 10000},
            {"role": "assistant", "content": "y" * 10000},
        ]

        with pytest.raises(ValueError, match="Context exceeds token limit"):
            agent.execute({"query": "New question"})

    def test_should_handle_unknown_domain(self) -> None:
        """Test fallback when domain cannot be classified."""
        agent = P2PAgent(
            model="gpt-4o-mini",
            specialists={"finance": MagicMock()},
        )

        with patch.object(agent, "_classify_domain", return_value="unknown"):
            result = agent.execute({"query": "Unclear question"})

        assert result["status"] == "fallback"
        assert result["routed_to"] == "general"

    def test_should_prevent_circular_handoffs(self) -> None:
        """Test that agent prevents infinite handoff loops."""
        finance_agent = MagicMock()
        finance_agent.process.return_value = {"response": "Answer"}

        agent = P2PAgent(
            model="gpt-4o-mini",
            specialists={"finance": finance_agent},
            max_handoffs=3,
        )

        # Simulate multiple handoffs
        for _ in range(4):
            with patch.object(agent, "_classify_domain", return_value="finance"):
                try:
                    agent.execute({"query": "Question"})
                except RuntimeError as e:
                    assert "Max handoffs exceeded" in str(e)
                    break

    def test_should_track_handoff_metrics(self) -> None:
        """Test that agent tracks handoff latency and count."""
        finance_agent = MagicMock()
        finance_agent.process.return_value = {"response": "Answer"}

        agent = P2PAgent(
            model="gpt-4o-mini",
            specialists={"finance": finance_agent},
        )

        with patch.object(agent, "_classify_domain", return_value="finance"):
            result = agent.execute({"query": "Question"})

        assert "metrics" in result
        assert "handoff_latency" in result["metrics"]
        assert "total_handoffs" in result["metrics"]
        assert result["metrics"]["total_handoffs"] == 1

    def test_should_raise_error_for_invalid_task_type(self) -> None:
        """Test that execute() validates task type."""
        agent = P2PAgent(model="gpt-4o-mini", specialists={"finance": MagicMock()})

        with pytest.raises(TypeError, match="task must be a dict"):
            agent.execute("not a dict")  # type: ignore


# =============================================================================
# CollaborativeAgent Tests (Shared Workspace Pattern)
# =============================================================================


class TestCollaborativeAgent:
    """Test suite for CollaborativeAgent (Shared Workspace + Peer Review)."""

    def test_should_create_instance_with_collaborators(self) -> None:
        """Test that CollaborativeAgent initializes with collaborator agents."""
        collaborators = [MagicMock(), MagicMock(), MagicMock()]
        agent = CollaborativeAgent(model="gpt-4o-mini", collaborators=collaborators)
        assert agent.model == "gpt-4o-mini"
        assert len(agent.collaborators) == 3

    def test_should_raise_error_when_collaborators_not_list(self) -> None:
        """Test that CollaborativeAgent validates collaborators type."""
        with pytest.raises(TypeError, match="collaborators must be a list"):
            CollaborativeAgent(model="gpt-4o-mini", collaborators={})  # type: ignore

    def test_should_raise_error_when_collaborators_less_than_two(self) -> None:
        """Test that CollaborativeAgent requires at least 2 collaborators."""
        with pytest.raises(
            ValueError, match="must have at least 2 collaborators for collaboration"
        ):
            CollaborativeAgent(model="gpt-4o-mini", collaborators=[MagicMock()])

    def test_should_create_shared_workspace_when_executing(self) -> None:
        """Test that shared workspace is created for collaboration."""
        collab1 = MagicMock()
        collab1.contribute.return_value = {"content": "Contribution 1", "confidence": 0.8}

        agent = CollaborativeAgent(
            model="gpt-4o-mini", collaborators=[collab1], _defer_validation=True
        )

        # Mock to allow single collaborator for testing workspace creation
        agent._min_collaborators = 1

        result = agent.execute({"query": "test"})

        assert "workspace" in result
        assert "contributions" in result["workspace"]

    def test_should_collect_contributions_from_all_agents(self) -> None:
        """Test that all collaborators contribute to shared workspace."""
        collab1 = MagicMock()
        collab1.contribute.return_value = {"content": "Contribution 1", "confidence": 0.8}
        collab2 = MagicMock()
        collab2.contribute.return_value = {"content": "Contribution 2", "confidence": 0.9}
        collab3 = MagicMock()
        collab3.contribute.return_value = {"content": "Contribution 3", "confidence": 0.7}

        agent = CollaborativeAgent(
            model="gpt-4o-mini", collaborators=[collab1, collab2, collab3]
        )
        result = agent.execute({"query": "test", "max_rounds": 1})

        assert len(result["workspace"]["contributions"]) == 3
        collab1.contribute.assert_called_once()
        collab2.contribute.assert_called_once()
        collab3.contribute.assert_called_once()

    def test_should_enable_peer_review_in_second_round(self) -> None:
        """Test that agents perform peer review in subsequent rounds."""
        collab1 = MagicMock()
        collab1.contribute.return_value = {"content": "Contribution 1", "confidence": 0.8}
        collab1.review.return_value = {"feedback": "Looks good"}

        collab2 = MagicMock()
        collab2.contribute.return_value = {"content": "Contribution 2", "confidence": 0.9}
        collab2.review.return_value = {"feedback": "Add more detail"}

        agent = CollaborativeAgent(
            model="gpt-4o-mini", collaborators=[collab1, collab2], max_rounds=2
        )
        result = agent.execute({"query": "test"})

        # Check that review was called in round 2
        collab1.review.assert_called()
        collab2.review.assert_called()
        assert "peer_reviews" in result["workspace"]

    def test_should_build_consensus_when_agents_agree(self) -> None:
        """Test consensus building when all agents agree."""
        collab1 = MagicMock()
        collab1.contribute.return_value = {
            "content": "Point A is correct",
            "confidence": 0.9,
        }
        collab2 = MagicMock()
        collab2.contribute.return_value = {
            "content": "Point A is correct",
            "confidence": 0.85,
        }

        agent = CollaborativeAgent(
            model="gpt-4o-mini", collaborators=[collab1, collab2]
        )
        result = agent.execute({"query": "test"})

        assert "consensus" in result
        assert result["consensus"]["agreement_level"] == "high"

    def test_should_handle_disagreements_gracefully(self) -> None:
        """Test handling when agents disagree."""
        collab1 = MagicMock()
        collab1.contribute.return_value = {"content": "Answer A", "confidence": 0.8}
        collab2 = MagicMock()
        collab2.contribute.return_value = {"content": "Answer B", "confidence": 0.9}

        agent = CollaborativeAgent(
            model="gpt-4o-mini", collaborators=[collab1, collab2]
        )
        result = agent.execute({"query": "test"})

        assert "consensus" in result
        assert result["consensus"]["agreement_level"] == "low"
        assert "disagreements" in result["consensus"]

    def test_should_handle_empty_contributions(self) -> None:
        """Test handling when agents return empty contributions."""
        collab1 = MagicMock()
        collab1.contribute.return_value = None  # Empty contribution
        collab2 = MagicMock()
        collab2.contribute.return_value = {"content": "Valid contribution", "confidence": 0.9}

        agent = CollaborativeAgent(
            model="gpt-4o-mini", collaborators=[collab1, collab2]
        )
        result = agent.execute({"query": "test"})

        assert result["status"] == "partial_success"
        assert len(result["workspace"]["contributions"]) == 1  # Only valid contribution

    def test_should_stop_when_max_rounds_exceeded(self) -> None:
        """Test that collaboration stops after max rounds."""
        collab1 = MagicMock()
        collab1.contribute.return_value = {"content": "Contribution", "confidence": 0.8}

        agent = CollaborativeAgent(
            model="gpt-4o-mini", collaborators=[collab1], max_rounds=3, _defer_validation=True
        )
        agent._min_collaborators = 1

        result = agent.execute({"query": "test"})

        assert result["rounds_completed"] == 3
        assert collab1.contribute.call_count == 3

    def test_should_synthesize_contributions_into_coherent_response(self) -> None:
        """Test that Response Mixer synthesizes all contributions."""
        collab1 = MagicMock()
        collab1.contribute.return_value = {"content": "Point A", "confidence": 0.9}
        collab2 = MagicMock()
        collab2.contribute.return_value = {"content": "Point B", "confidence": 0.85}

        agent = CollaborativeAgent(
            model="gpt-4o-mini", collaborators=[collab1, collab2]
        )
        result = agent.execute({"query": "test"})

        assert "synthesized_response" in result
        assert "Point A" in str(result["synthesized_response"])
        assert "Point B" in str(result["synthesized_response"])

    def test_should_track_collaboration_metrics(self) -> None:
        """Test that agent tracks rounds, contributions, and latency."""
        collab1 = MagicMock()
        collab1.contribute.return_value = {"content": "Contribution", "confidence": 0.8}

        agent = CollaborativeAgent(
            model="gpt-4o-mini", collaborators=[collab1], max_rounds=2, _defer_validation=True
        )
        agent._min_collaborators = 1

        result = agent.execute({"query": "test"})

        assert "metrics" in result
        assert "total_rounds" in result["metrics"]
        assert "total_contributions" in result["metrics"]
        assert "collaboration_latency" in result["metrics"]

    def test_should_raise_error_for_invalid_task_type(self) -> None:
        """Test that execute() validates task type."""
        agent = CollaborativeAgent(
            model="gpt-4o-mini", collaborators=[MagicMock(), MagicMock()]
        )

        with pytest.raises(TypeError, match="task must be a dict"):
            agent.execute("not a dict")  # type: ignore

    def test_should_handle_conflicting_feedback(self) -> None:
        """Test handling when peer reviews conflict."""
        collab1 = MagicMock()
        collab1.contribute.return_value = {"content": "Contribution 1", "confidence": 0.8}
        collab1.review.return_value = {"feedback": "✅ Good"}

        collab2 = MagicMock()
        collab2.contribute.return_value = {"content": "Contribution 2", "confidence": 0.9}
        collab2.review.return_value = {"feedback": "⚠️ Needs improvement"}

        agent = CollaborativeAgent(
            model="gpt-4o-mini", collaborators=[collab1, collab2], max_rounds=2
        )
        result = agent.execute({"query": "test"})

        assert "conflicting_reviews" in result
        assert len(result["conflicting_reviews"]) > 0


# =============================================================================
# AdaptiveLoopAgent Tests (Iterative Refinement Pattern)
# =============================================================================


class TestAdaptiveLoopAgent:
    """Test suite for AdaptiveLoopAgent (Iterative Refinement with Quality Threshold)."""

    def test_should_create_instance_with_quality_threshold(self) -> None:
        """Test that AdaptiveLoopAgent initializes with quality threshold."""
        agent = AdaptiveLoopAgent(
            model="gpt-4o-mini", quality_threshold=0.7, max_loops=4
        )
        assert agent.model == "gpt-4o-mini"
        assert agent.quality_threshold == 0.7
        assert agent.max_loops == 4

    def test_should_raise_error_when_threshold_out_of_range(self) -> None:
        """Test that quality_threshold must be between 0 and 1."""
        with pytest.raises(ValueError, match="quality_threshold must be between 0 and 1"):
            AdaptiveLoopAgent(model="gpt-4o-mini", quality_threshold=1.5)

        with pytest.raises(ValueError, match="quality_threshold must be between 0 and 1"):
            AdaptiveLoopAgent(model="gpt-4o-mini", quality_threshold=-0.1)

    def test_should_raise_error_when_max_loops_invalid(self) -> None:
        """Test that max_loops must be positive integer."""
        with pytest.raises(ValueError, match="max_loops must be positive"):
            AdaptiveLoopAgent(model="gpt-4o-mini", max_loops=0)

    def test_should_iterate_until_quality_threshold_met(self) -> None:
        """Test that agent iterates until quality threshold is reached."""
        agent = AdaptiveLoopAgent(model="gpt-4o-mini", quality_threshold=0.8, max_loops=5)

        # Mock quality scores: [0.5, 0.6, 0.85] - threshold met on loop 3
        with patch.object(
            agent, "_execute_search", side_effect=[
                {"results": ["A"], "quality": 0.5},
                {"results": ["A", "B"], "quality": 0.6},
                {"results": ["A", "B", "C"], "quality": 0.85},
            ]
        ):
            result = agent.execute({"query": "test"})

        assert result["loops_executed"] == 3
        assert result["final_quality"] >= 0.8
        assert result["status"] == "success"

    def test_should_refine_query_progressively_when_results_insufficient(
        self,
    ) -> None:
        """Test that agent applies progressive query refinement."""
        agent = AdaptiveLoopAgent(model="gpt-4o-mini", quality_threshold=0.8)

        # Track refinement strategies
        refinements = []

        def mock_refine(query: str, loop: int) -> str:
            refined = f"refined_{loop}"
            refinements.append(refined)
            return refined

        with patch.object(agent, "_refine_query", side_effect=mock_refine):
            with patch.object(
                agent, "_execute_search", return_value={"results": ["A"], "quality": 0.5}
            ):
                agent.execute({"query": "original"})

        assert len(refinements) > 1
        assert refinements[0] != refinements[1]  # Different refinements each loop

    def test_should_terminate_early_when_threshold_met(self) -> None:
        """Test that loop terminates early when quality threshold is met."""
        agent = AdaptiveLoopAgent(model="gpt-4o-mini", quality_threshold=0.7, max_loops=5)

        # First search already meets threshold
        with patch.object(
            agent, "_execute_search", return_value={"results": ["A", "B", "C"], "quality": 0.9}
        ):
            result = agent.execute({"query": "test"})

        assert result["loops_executed"] == 1  # Terminated early
        assert result["early_termination"] is True

    def test_should_apply_fallback_when_max_loops_exceeded(self) -> None:
        """Test fallback strategy when all loops fail."""
        agent = AdaptiveLoopAgent(model="gpt-4o-mini", quality_threshold=0.9, max_loops=3)

        # All searches fail to meet threshold
        with patch.object(
            agent, "_execute_search", return_value={"results": ["A"], "quality": 0.5}
        ):
            result = agent.execute({"query": "test"})

        assert result["loops_executed"] == 3
        assert result["status"] == "fallback"
        assert "fallback_strategy" in result

    def test_should_track_quality_metrics_per_loop(self) -> None:
        """Test that quality metrics are tracked for each loop."""
        agent = AdaptiveLoopAgent(model="gpt-4o-mini", quality_threshold=0.8, max_loops=4)

        with patch.object(
            agent, "_execute_search", side_effect=[
                {"results": ["A"], "quality": 0.5},
                {"results": ["A", "B"], "quality": 0.65},
                {"results": ["A", "B", "C"], "quality": 0.85},
            ]
        ):
            result = agent.execute({"query": "test"})

        assert "quality_per_loop" in result
        assert len(result["quality_per_loop"]) == 3
        assert result["quality_per_loop"][0] == 0.5
        assert result["quality_per_loop"][2] == 0.85

    def test_should_use_synonym_expansion_in_refinement(self) -> None:
        """Test that refinement includes synonym expansion."""
        agent = AdaptiveLoopAgent(model="gpt-4o-mini", quality_threshold=0.8)

        original_query = "vegan restaurants"
        with patch.object(
            agent, "_execute_search", return_value={"results": [], "quality": 0.0}
        ):
            # Check that refinement expands synonyms
            refined = agent._refine_query(original_query, loop=1)

        assert "vegetarian" in refined.lower() or "plant-based" in refined.lower()

    def test_should_remove_constraints_progressively(self) -> None:
        """Test that constraints are removed in later loops."""
        agent = AdaptiveLoopAgent(model="gpt-4o-mini", quality_threshold=0.8)

        original_query = "Italian vegan restaurants with parking"

        # Loop 1: Keep most constraints
        refined_1 = agent._refine_query(original_query, loop=1)
        # Loop 3: Remove more constraints
        refined_3 = agent._refine_query(original_query, loop=3)

        assert len(refined_3.split()) < len(refined_1.split())  # Simpler query

    def test_should_handle_immediate_success(self) -> None:
        """Test handling when first loop already succeeds."""
        agent = AdaptiveLoopAgent(model="gpt-4o-mini", quality_threshold=0.5)

        with patch.object(
            agent, "_execute_search", return_value={"results": ["A", "B", "C"], "quality": 0.9}
        ):
            result = agent.execute({"query": "test"})

        assert result["loops_executed"] == 1
        assert result["status"] == "success"

    def test_should_track_latency_per_loop(self) -> None:
        """Test that latency is tracked for each loop."""
        agent = AdaptiveLoopAgent(model="gpt-4o-mini", quality_threshold=0.9, max_loops=3)

        with patch.object(
            agent, "_execute_search", return_value={"results": ["A"], "quality": 0.5}
        ):
            result = agent.execute({"query": "test"})

        assert "metrics" in result
        assert "latency_per_loop" in result["metrics"]
        assert len(result["metrics"]["latency_per_loop"]) == 3

    def test_should_raise_error_for_invalid_task_type(self) -> None:
        """Test that execute() validates task type."""
        agent = AdaptiveLoopAgent(model="gpt-4o-mini", quality_threshold=0.7)

        with pytest.raises(TypeError, match="task must be a dict"):
            agent.execute("not a dict")  # type: ignore

    def test_should_prevent_quality_degradation(self) -> None:
        """Test that agent returns best loop if quality degrades."""
        agent = AdaptiveLoopAgent(model="gpt-4o-mini", quality_threshold=0.9, max_loops=4)

        # Quality: 0.7 → 0.75 → 0.5 (degradation) → stop
        with patch.object(
            agent, "_execute_search", side_effect=[
                {"results": ["A", "B"], "quality": 0.7},
                {"results": ["A", "B", "C"], "quality": 0.75},
                {"results": ["A"], "quality": 0.5},  # Degradation
            ]
        ):
            result = agent.execute({"query": "test"})

        assert result["best_loop"] == 2  # Loop 2 had highest quality (0.75)
        assert result["final_quality"] == 0.75
