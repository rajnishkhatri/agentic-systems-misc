"""
Multi-Agent Framework: Planner-Validator-Executor (PVE) orchestration pattern.

This module provides:
- BaseAgent: Abstract base class for all agents
- PlannerAgent: Generates execution plans using LLM
- ValidatorAgent: Validates plans before execution
- ExecutorAgent: Executes validated plans
- MemoryManager: Shared memory for agent communication
- MultiAgentOrchestrator: Coordinates PVE workflow

All code follows defensive programming:
- Type hints on all functions
- Input validation with descriptive errors
- Proper error handling
- Abstract Base Class pattern for extensibility

Pattern: Planner-Validator-Executor (PVE)
Source: lesson-14/multi_agent_orchestration.md
"""

import json
import time
from abc import ABC, abstractmethod
from typing import Any

import litellm  # type: ignore


# =============================================================================
# Base Agent Abstract Class
# =============================================================================


class BaseAgent(ABC):
    """Abstract base class for all agent implementations.

    Provides common functionality:
    - Model configuration
    - Input validation
    - Abstract process() method that subclasses must implement

    Subclasses must implement:
    - process(input_data: dict) -> dict: Core agent logic
    """

    def __init__(self, model: str):
        """Initialize agent with model configuration.

        Args:
            model: LLM model name (e.g., "gpt-4o-mini", "claude-sonnet")

        Raises:
            TypeError: If model is not a string
        """
        # Step 1: Type checking (defensive)
        if not isinstance(model, str):
            raise TypeError("model must be a string")

        # Step 2: Initialize attributes
        self.model = model

    @abstractmethod
    def process(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Process input data. Subclasses must implement.

        Args:
            input_data: Input data dictionary

        Returns:
            Result dictionary

        Raises:
            NotImplementedError: If subclass doesn't implement
        """
        pass


# =============================================================================
# Concrete Agent Implementations
# =============================================================================


class PlannerAgent(BaseAgent):
    """Generates execution plans for user queries.

    Uses LLM to create structured plans with steps and tool calls.
    """

    def process(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Generate execution plan from query.

        Args:
            input_data: Dict with keys:
                - query (str): User query
                - tools (list): Available tools
                - context (dict): Conversation context

        Returns:
            Dict with keys:
                - plan (dict): Generated plan with goal and steps
                - timestamp (float): Plan generation timestamp

        Raises:
            TypeError: If input_data is not a dict
            ValueError: If query is missing or empty
            ValueError: If LLM response parsing fails
        """
        # Step 1: Type checking
        if not isinstance(input_data, dict):
            raise TypeError("input_data must be a dictionary")

        # Step 2: Input validation
        if "query" not in input_data:
            raise ValueError("input_data must have 'query' field")

        query = input_data["query"]
        if not query or not query.strip():
            raise ValueError("query cannot be empty")

        tools = input_data.get("tools", [])
        context = input_data.get("context", {})

        # Step 3: Main logic - Generate plan using LLM
        prompt = f"""You are a planning agent. Generate a step-by-step plan to answer this query.

Query: {query}

Available Tools:
{json.dumps(tools, indent=2)}

Context:
{json.dumps(context, indent=2)}

Generate a plan with these components:
1. What information do we need?
2. Which tools to call and in what order?
3. How to synthesize results into final answer?

Output format (JSON):
{{
  "goal": "brief goal description",
  "steps": [
    {{"step": 1, "tool": "tool_name", "args": {{}}, "rationale": "why"}},
    ...
  ]
}}

Plan:"""

        # Call LLM
        response = self._call_llm(prompt)

        # Parse JSON response
        try:
            plan = json.loads(response)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse LLM response as JSON: {e}")

        # Step 4: Return result
        return {"plan": plan, "timestamp": time.time()}

    def _call_llm(self, prompt: str) -> str:
        """Call LLM API.

        Args:
            prompt: Formatted prompt

        Returns:
            Raw LLM response content
        """
        response = litellm.completion(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
        )
        return response.choices[0].message.content


class ValidatorAgent(BaseAgent):
    """Validates execution plans before running.

    Checks plan correctness, goal alignment, and efficiency.
    """

    def process(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Validate plan correctness.

        Args:
            input_data: Dict with keys:
                - plan (dict): Plan to validate
                - tools (list): Available tools
                - goal (str): User's objective

        Returns:
            Dict with keys:
                - status (str): "APPROVED" or "REJECTED"
                - feedback (str): Validation feedback
                - timestamp (float): Validation timestamp
                - issues (list, optional): List of issues if rejected

        Raises:
            TypeError: If input_data or plan is not a dict
            ValueError: If plan field is missing
        """
        # Step 1: Type checking
        if not isinstance(input_data, dict):
            raise TypeError("input_data must be a dictionary")

        # Step 2: Input validation
        if "plan" not in input_data:
            raise ValueError("input_data must have 'plan' field")

        plan = input_data["plan"]
        if not isinstance(plan, dict):
            raise TypeError("plan must be a dictionary")

        tools = input_data.get("tools", [])
        goal = input_data.get("goal", "")

        # Step 3: Main logic - Validate plan using LLM
        prompt = f"""You are a validation agent. Validate this execution plan.

Goal: {goal}

Plan:
{json.dumps(plan, indent=2)}

Available Tools:
{json.dumps(tools, indent=2)}

Validate the plan against these criteria:
1. Will executing this plan achieve the goal?
2. Are all tool calls valid (correct tools and arguments)?
3. Are the steps in the correct order?
4. Are there any missing steps?
5. Are there any unnecessary or redundant steps?

Response format (JSON):
{{
  "status": "APPROVED" or "REJECTED",
  "feedback": "detailed explanation",
  "issues": ["issue1", "issue2"] (only if REJECTED)
}}

Validation:"""

        # Call LLM
        response = self._call_llm(prompt)

        # Parse JSON response
        try:
            result = json.loads(response)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse LLM response as JSON: {e}")

        # Step 4: Return result with timestamp
        result["timestamp"] = time.time()
        return result

    def _call_llm(self, prompt: str) -> str:
        """Call LLM API.

        Args:
            prompt: Formatted prompt

        Returns:
            Raw LLM response content
        """
        response = litellm.completion(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
        )
        return response.choices[0].message.content


class ExecutorAgent(BaseAgent):
    """Executes validated plans.

    Runs plan steps sequentially and returns results.
    """

    def process(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Execute validated plan.

        Args:
            input_data: Dict with keys:
                - plan (dict): Validated plan to execute

        Returns:
            Dict with keys:
                - success (bool): Whether execution succeeded
                - results (list): Results for each step
                - timestamp (float): Execution timestamp

        Raises:
            TypeError: If input_data is not a dict
            ValueError: If plan field is missing
        """
        # Step 1: Type checking
        if not isinstance(input_data, dict):
            raise TypeError("input_data must be a dictionary")

        # Step 2: Input validation
        if "plan" not in input_data:
            raise ValueError("input_data must have 'plan' field")

        plan = input_data["plan"]
        steps = plan.get("steps", [])

        # Step 3: Main logic - Execute plan steps
        results = []

        for step in steps:
            # For now, we just simulate execution
            # In real implementation, this would call actual tool functions
            step_result = {
                "step": step.get("step", 0),
                "status": "success",
                "tool": step.get("tool", ""),
                "result": f"Simulated execution of {step.get('tool', '')}",
            }
            results.append(step_result)

        # Determine overall success
        success = all(r["status"] == "success" for r in results)

        # Step 4: Return result
        return {"success": success, "results": results, "timestamp": time.time()}


# =============================================================================
# Memory Manager
# =============================================================================


class MemoryManager:
    """Shared memory for multi-agent communication.

    Provides simple key-value store for agents to share data.
    """

    def __init__(self):
        """Initialize empty memory store."""
        self._memory: dict[str, Any] = {}

    def store(self, key: str, value: Any) -> None:
        """Store value in memory.

        Args:
            key: Memory key
            value: Value to store
        """
        self._memory[key] = value

    def get(self, key: str) -> Any:
        """Retrieve value from memory.

        Args:
            key: Memory key

        Returns:
            Stored value or None if key doesn't exist
        """
        return self._memory.get(key)

    def get_all(self) -> dict[str, Any]:
        """Get all memory contents.

        Returns:
            Dictionary of all stored key-value pairs
        """
        return self._memory.copy()

    def clear(self) -> None:
        """Clear all memory contents."""
        self._memory.clear()


# =============================================================================
# Multi-Agent Orchestrator
# =============================================================================


class MultiAgentOrchestrator:
    """Orchestrates Planner-Validator-Executor (PVE) workflow.

    Coordinates specialized agents to execute complex tasks:
    1. Planner generates execution plan
    2. Validator checks plan quality
    3. Executor runs validated plan
    """

    def __init__(
        self,
        planner: PlannerAgent,
        validator: ValidatorAgent,
        executor: ExecutorAgent,
        max_retries: int = 2,
    ):
        """Initialize orchestrator with agents.

        Args:
            planner: Planning agent
            validator: Validation agent
            executor: Execution agent
            max_retries: Maximum planning retries on rejection

        Raises:
            ValueError: If max_retries < 1
        """
        # Step 1: Input validation
        if max_retries < 1:
            raise ValueError("max_retries must be at least 1")

        # Step 2: Initialize attributes
        self.planner = planner
        self.validator = validator
        self.executor = executor
        self.max_retries = max_retries
        self.memory = MemoryManager()

    def run(
        self, query: str, tools: list[dict], context: dict[str, Any]
    ) -> dict[str, Any]:
        """Run PVE workflow.

        Args:
            query: User query
            tools: Available tools
            context: Conversation context

        Returns:
            Dict with keys:
                - success (bool): Whether workflow succeeded
                - plan (dict): Final plan
                - validation (dict): Validation result
                - execution (dict): Execution result
                - memory (dict): Memory state
                - error (str, optional): Error message if failed

        Raises:
            ValueError: If query is empty or None
        """
        # Step 1: Input validation
        if not query or (isinstance(query, str) and not query.strip()):
            raise ValueError("query cannot be empty")

        # Step 2: Planning loop with validation retry
        attempt = 0
        plan = None
        validation = None

        while attempt < self.max_retries:
            # Generate plan
            plan_result = self.planner.process(
                {"query": query, "tools": tools, "context": context}
            )
            plan = plan_result["plan"]
            self.memory.store("plan", plan)

            # Validate plan
            validation = self.validator.process(
                {"plan": plan, "tools": tools, "goal": query}
            )
            self.memory.store("validation", validation)

            if validation["status"] == "APPROVED":
                break  # Plan approved, proceed to execution

            # Plan rejected, update context with feedback for retry
            context["validation_feedback"] = validation.get("feedback", "")
            attempt += 1

        # Step 3: Check if validation failed after all retries
        if validation and validation["status"] == "REJECTED":
            return {
                "success": False,
                "error": "Plan validation failed after max retries",
                "plan": plan,
                "validation": validation,
                "memory": self.memory.get_all(),
            }

        # Step 4: Execute approved plan
        execution = self.executor.process({"plan": plan})
        self.memory.store("execution", execution)

        # Step 5: Return final result
        return {
            "success": execution["success"],
            "plan": plan,
            "validation": validation,
            "execution": execution,
            "memory": self.memory.get_all(),
        }
