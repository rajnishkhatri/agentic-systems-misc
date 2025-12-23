"""UI-Aware Orchestrator for Chainlit Integration (FR6).

Extends the standard DisputeOrchestrator to provide real-time visualization
of state transitions and phase execution using Chainlit's Step API.
"""

from __future__ import annotations

from typing import Any, Callable, cast

import chainlit as cl
from backend.orchestrators.dispute_orchestrator import DisputeOrchestrator
from backend.orchestrators.dispute_state import DisputeState
from backend.phases.classify_v8_rag import classify_dispute_v8_rag


class UIOrchestrator(DisputeOrchestrator):
    """UI-aware version of DisputeOrchestrator that visualizes phases in Chainlit.

    Overrides internal execution methods to wrap handlers in cl.Step contexts.
    """

    def __init__(self, *args, **kwargs) -> None:
        """Initialize and register V8 RAG handler."""
        super().__init__(*args, **kwargs)
        # Override CLASSIFY handler with V8 RAG pipeline
        self.register_state_handler(DisputeState.CLASSIFY.value, classify_dispute_v8_rag)

    async def _execute_state_handler(
        self,
        handler: Callable[..., Any],
        state_task: dict[str, Any],
        state_name: str,
    ) -> dict[str, Any]:
        """Execute state handler wrapped in a Chainlit Step.

        Args:
            handler: State handler callable
            state_task: Task dictionary for handler
            state_name: Name of current state

        Returns:
            Handler output dictionary
        """
        # Create a step for the current phase
        async with cl.Step(name=state_name, type="process") as step:
            step.input = state_task

            # Execute handler
            output = await handler(state_task)

            # If this is the CLASSIFY phase, visualize the reasoning traces
            if state_name == DisputeState.CLASSIFY.value:
                # Extract V8 RAG specific fields
                reasoning = output.get("classification_reasoning", "No reasoning available")
                confidence = output.get("classification_confidence", 0.0)
                branch_a = output.get("branch_a_conclusion", "N/A")
                branch_b = output.get("branch_b_complaint", "N/A")
                branch_c = output.get("branch_c_persona", "N/A")
                agreement = output.get("branch_agreement", 0.0)
                
                trace_content = f"""### 🧠 Classification Reasoning (V8 RAG)
**Confidence:** {confidence:.2f}

**Synthesis:**
{reasoning}

**Branch Analysis:**
* **Acknowledgment:** {branch_a}
* **Complaint Type:** {branch_b}
* **Persona:** {branch_c}

**Agreement Score:** {agreement}
"""
                await cl.Message(content=trace_content, author="Reasoning Trace").send()

            # Update step output
            step.output = output

            # Log successful execution via parent logger (optional, already handled by base)
            # But here we ensure the UI updates

            return cast(dict[str, Any], output)

    def _log_audit_trail(
        self,
        workflow_state: dict[str, Any],
        current_state: str,
        handler_output: dict[str, Any],
    ) -> None:
        """Log state transition in audit trail and update UI sidebars if needed.

        Args:
            workflow_state: Workflow state dictionary
            current_state: Current state name
            handler_output: Output from state handler
        """
        super()._log_audit_trail(workflow_state, current_state, handler_output)

        # Could update sidebar elements here if needed
        # e.g., if accumulated data has evidence, update the evidence list sidebar

