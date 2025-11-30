"""Multi-Agent Workflow Traces Generator for BlackBoxRecorder demonstrations.

Generates 5 complete workflow traces following the BlackBoxRecorder schema:
1. Invoice Processing (3 agents) - Cascade failure example
2. Fraud Detection (2 agents) - Success
3. Research Workflow (4 agents) - Success
4. Healthcare Diagnosis (5 agents) - Human approval required
5. Contract Review (3 agents) - Manual review

Each trace includes:
- TaskPlan with steps and dependencies
- AgentInfo collaborator list with join/leave timestamps
- ParameterSubstitutions with justifications
- ExecutionTrace with 8 event types
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from . import BaseGenerator


class WorkflowTracesGenerator(BaseGenerator):
    """Generator for multi-agent workflow execution traces.

    Creates realistic workflow traces for debugging and audit demonstrations.
    """

    def generate(self, count: int = 5) -> list[dict[str, Any]]:
        """Generate workflow traces.

        Args:
            count: Number of workflows to generate (max 5 predefined)

        Returns:
            List of workflow trace dictionaries
        """
        workflows = [
            self._generate_invoice_processing_trace(),
            self._generate_fraud_detection_trace(),
            self._generate_research_workflow_trace(),
            self._generate_healthcare_diagnosis_trace(),
            self._generate_contract_review_trace(),
        ]

        return workflows[:count]

    def _generate_invoice_processing_trace(self) -> dict[str, Any]:
        """Generate invoice processing workflow with cascade failure.

        Scenario: 3-agent workflow where parameter change causes cascade failure.
        Extractor changes confidence threshold → Validator crashes → Approver never starts.
        """
        workflow_id = "invoice-processing-001"
        start_time = datetime(2025, 11, 27, 14, 0, 0, tzinfo=UTC)

        # Define agents
        agents = [
            {
                "agent_id": "invoice-extractor-v2",
                "agent_name": "Invoice Extractor",
                "role": "extraction",
                "capabilities": ["extract_vendor", "extract_line_items"],
            },
            {
                "agent_id": "invoice-validator-v1",
                "agent_name": "Amount Validator",
                "role": "validation",
                "capabilities": ["validate_amount", "check_duplicates"],
            },
            {
                "agent_id": "invoice-approver-v1",
                "agent_name": "Invoice Approver",
                "role": "approval",
                "capabilities": ["approve_invoice", "escalate_to_manager"],
            },
        ]

        # Task plan
        task_plan = {
            "plan_id": f"plan-{workflow_id}",
            "task_id": workflow_id,
            "created_at": start_time.isoformat(),
            "steps": [
                {
                    "step_id": "extract_vendor",
                    "description": "Extract vendor and amount from invoice",
                    "agent_id": "invoice-extractor-v2",
                    "expected_inputs": ["invoice_text", "invoice_image"],
                    "expected_outputs": ["vendor_name", "amount", "confidence"],
                    "timeout_seconds": 60,
                    "is_critical": True,
                    "order": 1,
                },
                {
                    "step_id": "validate_amount",
                    "description": "Validate extracted amount against database",
                    "agent_id": "invoice-validator-v1",
                    "expected_inputs": ["vendor_name", "amount", "confidence"],
                    "expected_outputs": ["validation_result", "vendor_id"],
                    "timeout_seconds": 30,
                    "is_critical": True,
                    "order": 2,
                },
                {
                    "step_id": "approve_invoice",
                    "description": "Final approval for payment processing",
                    "agent_id": "invoice-approver-v1",
                    "expected_inputs": ["validation_result", "vendor_id"],
                    "expected_outputs": ["approval_status", "payment_reference"],
                    "timeout_seconds": 120,
                    "is_critical": True,
                    "order": 3,
                },
            ],
            "dependencies": {
                "validate_amount": ["extract_vendor"],
                "approve_invoice": ["validate_amount"],
            },
            "rollback_points": ["extract_vendor"],
            "metadata": {"invoice_id": "INV-2024-1234", "vendor": "Acme Corp"},
        }

        # Collaborators with join/leave timestamps
        collaborators = [
            {
                "agent_id": "invoice-extractor-v2",
                "agent_name": "Invoice Extractor",
                "role": "extraction",
                "joined_at": start_time.isoformat(),
                "left_at": (start_time + timedelta(seconds=12)).isoformat(),
            },
            {
                "agent_id": "invoice-validator-v1",
                "agent_name": "Amount Validator",
                "role": "validation",
                "joined_at": (start_time + timedelta(seconds=12)).isoformat(),
                "left_at": (start_time + timedelta(seconds=18)).isoformat(),
            },
            # Approver never joins due to cascade failure
        ]

        # Parameter substitutions - this causes the cascade failure
        parameter_substitutions = [
            {
                "substitution_id": "param-001",
                "timestamp": (start_time + timedelta(seconds=10)).isoformat(),
                "parameter_name": "confidence_threshold",
                "old_value": 0.8,
                "new_value": 0.95,
                "justification": "Reduce false positives per compliance team request",
                "changed_by": "invoice-extractor-v2",
                "workflow_id": workflow_id,
            }
        ]

        # Execution events
        events = [
            {
                "event_id": "evt-001",
                "event_type": "step_start",
                "step_id": "extract_vendor",
                "timestamp": start_time.isoformat(),
                "agent_id": "invoice-extractor-v2",
                "metadata": {},
            },
            {
                "event_id": "evt-002",
                "event_type": "collaborator_join",
                "step_id": "extract_vendor",
                "timestamp": start_time.isoformat(),
                "agent_id": "invoice-extractor-v2",
                "metadata": {"role": "extraction"},
            },
            {
                "event_id": "evt-003",
                "event_type": "decision",
                "step_id": "extract_vendor",
                "timestamp": (start_time + timedelta(seconds=5)).isoformat(),
                "agent_id": "invoice-extractor-v2",
                "metadata": {
                    "decision": "Use GPT-4 for OCR correction",
                    "alternatives": ["GPT-3.5", "Claude", "Rule-based"],
                    "rationale": "Higher accuracy needed for noisy scans",
                },
            },
            {
                "event_id": "evt-004",
                "event_type": "parameter_change",
                "step_id": "extract_vendor",
                "timestamp": (start_time + timedelta(seconds=10)).isoformat(),
                "agent_id": "invoice-extractor-v2",
                "metadata": {
                    "parameter": "confidence_threshold",
                    "old_value": 0.8,
                    "new_value": 0.95,
                },
            },
            {
                "event_id": "evt-005",
                "event_type": "checkpoint",
                "step_id": "extract_vendor",
                "timestamp": (start_time + timedelta(seconds=11)).isoformat(),
                "agent_id": "invoice-extractor-v2",
                "metadata": {
                    "checkpoint_id": "chk-001",
                    "state": {"vendor_name": "Acme Corp", "amount": 4523.50},
                },
            },
            {
                "event_id": "evt-006",
                "event_type": "step_end",
                "step_id": "extract_vendor",
                "timestamp": (start_time + timedelta(seconds=12)).isoformat(),
                "agent_id": "invoice-extractor-v2",
                "duration_ms": 12000,
                "metadata": {"success": True, "confidence": 0.92},
            },
            {
                "event_id": "evt-007",
                "event_type": "collaborator_leave",
                "step_id": "extract_vendor",
                "timestamp": (start_time + timedelta(seconds=12)).isoformat(),
                "agent_id": "invoice-extractor-v2",
                "metadata": {},
            },
            {
                "event_id": "evt-008",
                "event_type": "step_start",
                "step_id": "validate_amount",
                "timestamp": (start_time + timedelta(seconds=12)).isoformat(),
                "agent_id": "invoice-validator-v1",
                "metadata": {},
            },
            {
                "event_id": "evt-009",
                "event_type": "collaborator_join",
                "step_id": "validate_amount",
                "timestamp": (start_time + timedelta(seconds=12)).isoformat(),
                "agent_id": "invoice-validator-v1",
                "metadata": {"role": "validation"},
            },
            {
                "event_id": "evt-010",
                "event_type": "error",
                "step_id": "validate_amount",
                "timestamp": (start_time + timedelta(seconds=15)).isoformat(),
                "agent_id": "invoice-validator-v1",
                "metadata": {
                    "error_message": "Confidence threshold too high (0.95) - no valid results",
                    "error_type": "ValidationError",
                    "is_recoverable": False,
                    "stack_trace": "ValidationError: All results below threshold 0.95...",
                },
            },
            {
                "event_id": "evt-011",
                "event_type": "step_end",
                "step_id": "validate_amount",
                "timestamp": (start_time + timedelta(seconds=18)).isoformat(),
                "agent_id": "invoice-validator-v1",
                "duration_ms": 6000,
                "metadata": {"success": False, "failure_reason": "threshold_exceeded"},
            },
            {
                "event_id": "evt-012",
                "event_type": "collaborator_leave",
                "step_id": "validate_amount",
                "timestamp": (start_time + timedelta(seconds=18)).isoformat(),
                "agent_id": "invoice-validator-v1",
                "metadata": {},
            },
        ]

        execution_trace = {
            "trace_id": f"trace-{workflow_id}",
            "task_id": workflow_id,
            "events": events,
            "start_time": start_time.isoformat(),
            "end_time": (start_time + timedelta(seconds=18)).isoformat(),
            "total_duration_ms": 18000,
        }

        return {
            "workflow_id": workflow_id,
            "workflow_name": "Invoice Processing Workflow",
            "workflow_type": "invoice_processing",
            "task_plan": task_plan,
            "collaborators": collaborators,
            "parameter_substitutions": parameter_substitutions,
            "execution_trace": execution_trace,
            "outcome": {
                "status": "failed",
                "reason": "Cascade failure: validator crashed after parameter change",
                "root_cause": "Parameter substitution (confidence_threshold: 0.8 → 0.95) caused empty validation results",
                "steps_completed": 1,
                "steps_failed": 1,
                "steps_skipped": 1,
            },
            "metadata": {
                "invoice_id": "INV-2024-1234",
                "vendor": "Acme Corp",
                "amount": 4523.50,
            },
        }

    def _generate_fraud_detection_trace(self) -> dict[str, Any]:
        """Generate fraud detection workflow - successful execution."""
        workflow_id = "fraud-detection-001"
        start_time = datetime(2025, 11, 27, 15, 30, 0, tzinfo=UTC)

        task_plan = {
            "plan_id": f"plan-{workflow_id}",
            "task_id": workflow_id,
            "created_at": start_time.isoformat(),
            "steps": [
                {
                    "step_id": "score_transaction",
                    "description": "Calculate fraud risk score",
                    "agent_id": "fraud-detector-v2",
                    "expected_inputs": ["transaction_id", "amount", "merchant"],
                    "expected_outputs": ["fraud_score", "risk_level"],
                    "timeout_seconds": 10,
                    "is_critical": True,
                    "order": 1,
                },
                {
                    "step_id": "escalate_if_needed",
                    "description": "Escalate high-risk transactions",
                    "agent_id": "fraud-escalator-v1",
                    "expected_inputs": ["fraud_score", "risk_level"],
                    "expected_outputs": ["escalation_status", "reviewer_assigned"],
                    "timeout_seconds": 5,
                    "is_critical": False,
                    "order": 2,
                },
            ],
            "dependencies": {"escalate_if_needed": ["score_transaction"]},
            "rollback_points": [],
            "metadata": {"transaction_id": "TXN-2024-56789"},
        }

        collaborators = [
            {
                "agent_id": "fraud-detector-v2",
                "agent_name": "Transaction Fraud Detector",
                "role": "scoring",
                "joined_at": start_time.isoformat(),
                "left_at": (start_time + timedelta(milliseconds=350)).isoformat(),
            },
            {
                "agent_id": "fraud-escalator-v1",
                "agent_name": "Fraud Escalation Agent",
                "role": "escalation",
                "joined_at": (start_time + timedelta(milliseconds=350)).isoformat(),
                "left_at": (start_time + timedelta(milliseconds=500)).isoformat(),
            },
        ]

        events = [
            {
                "event_id": "evt-001",
                "event_type": "step_start",
                "step_id": "score_transaction",
                "timestamp": start_time.isoformat(),
                "agent_id": "fraud-detector-v2",
                "metadata": {},
            },
            {
                "event_id": "evt-002",
                "event_type": "collaborator_join",
                "step_id": "score_transaction",
                "timestamp": start_time.isoformat(),
                "agent_id": "fraud-detector-v2",
                "metadata": {"role": "scoring"},
            },
            {
                "event_id": "evt-003",
                "event_type": "decision",
                "step_id": "score_transaction",
                "timestamp": (start_time + timedelta(milliseconds=200)).isoformat(),
                "agent_id": "fraud-detector-v2",
                "metadata": {
                    "decision": "Apply ML model v2.3",
                    "alternatives": ["Rule-based only", "ML model v2.2", "ML model v2.3"],
                    "rationale": "Latest model has 2% higher accuracy",
                },
            },
            {
                "event_id": "evt-004",
                "event_type": "step_end",
                "step_id": "score_transaction",
                "timestamp": (start_time + timedelta(milliseconds=350)).isoformat(),
                "agent_id": "fraud-detector-v2",
                "duration_ms": 350,
                "metadata": {"success": True, "fraud_score": 0.23, "risk_level": "low"},
            },
            {
                "event_id": "evt-005",
                "event_type": "collaborator_leave",
                "step_id": "score_transaction",
                "timestamp": (start_time + timedelta(milliseconds=350)).isoformat(),
                "agent_id": "fraud-detector-v2",
                "metadata": {},
            },
            {
                "event_id": "evt-006",
                "event_type": "step_start",
                "step_id": "escalate_if_needed",
                "timestamp": (start_time + timedelta(milliseconds=350)).isoformat(),
                "agent_id": "fraud-escalator-v1",
                "metadata": {},
            },
            {
                "event_id": "evt-007",
                "event_type": "collaborator_join",
                "step_id": "escalate_if_needed",
                "timestamp": (start_time + timedelta(milliseconds=350)).isoformat(),
                "agent_id": "fraud-escalator-v1",
                "metadata": {"role": "escalation"},
            },
            {
                "event_id": "evt-008",
                "event_type": "decision",
                "step_id": "escalate_if_needed",
                "timestamp": (start_time + timedelta(milliseconds=400)).isoformat(),
                "agent_id": "fraud-escalator-v1",
                "metadata": {
                    "decision": "No escalation needed",
                    "alternatives": ["Escalate to L1", "Escalate to L2", "No escalation"],
                    "rationale": "Risk level 'low' (score 0.23) below threshold 0.7",
                },
            },
            {
                "event_id": "evt-009",
                "event_type": "step_end",
                "step_id": "escalate_if_needed",
                "timestamp": (start_time + timedelta(milliseconds=500)).isoformat(),
                "agent_id": "fraud-escalator-v1",
                "duration_ms": 150,
                "metadata": {"success": True, "escalation_status": "not_required"},
            },
            {
                "event_id": "evt-010",
                "event_type": "collaborator_leave",
                "step_id": "escalate_if_needed",
                "timestamp": (start_time + timedelta(milliseconds=500)).isoformat(),
                "agent_id": "fraud-escalator-v1",
                "metadata": {},
            },
        ]

        execution_trace = {
            "trace_id": f"trace-{workflow_id}",
            "task_id": workflow_id,
            "events": events,
            "start_time": start_time.isoformat(),
            "end_time": (start_time + timedelta(milliseconds=500)).isoformat(),
            "total_duration_ms": 500,
        }

        return {
            "workflow_id": workflow_id,
            "workflow_name": "Fraud Detection Pipeline",
            "workflow_type": "fraud_detection",
            "task_plan": task_plan,
            "collaborators": collaborators,
            "parameter_substitutions": [],
            "execution_trace": execution_trace,
            "outcome": {
                "status": "success",
                "reason": "Transaction scored and processed without escalation",
                "root_cause": None,
                "steps_completed": 2,
                "steps_failed": 0,
                "steps_skipped": 0,
            },
            "metadata": {
                "transaction_id": "TXN-2024-56789",
                "fraud_score": 0.23,
                "risk_level": "low",
            },
        }

    def _generate_research_workflow_trace(self) -> dict[str, Any]:
        """Generate research workflow - successful multi-agent collaboration."""
        workflow_id = "research-workflow-001"
        start_time = datetime(2025, 11, 27, 10, 0, 0, tzinfo=UTC)

        task_plan = {
            "plan_id": f"plan-{workflow_id}",
            "task_id": workflow_id,
            "created_at": start_time.isoformat(),
            "steps": [
                {
                    "step_id": "search_literature",
                    "description": "Search academic databases for relevant papers",
                    "agent_id": "research-assistant-v2",
                    "expected_inputs": ["query", "databases", "date_range"],
                    "expected_outputs": ["papers", "total_found"],
                    "timeout_seconds": 60,
                    "is_critical": True,
                    "order": 1,
                },
                {
                    "step_id": "summarize_papers",
                    "description": "Generate summaries of found papers",
                    "agent_id": "summarizer-v1",
                    "expected_inputs": ["papers"],
                    "expected_outputs": ["summaries", "key_findings"],
                    "timeout_seconds": 120,
                    "is_critical": True,
                    "order": 2,
                },
                {
                    "step_id": "synthesize_findings",
                    "description": "Synthesize findings into coherent narrative",
                    "agent_id": "synthesizer-v1",
                    "expected_inputs": ["summaries", "key_findings"],
                    "expected_outputs": ["synthesis", "recommendations"],
                    "timeout_seconds": 180,
                    "is_critical": True,
                    "order": 3,
                },
                {
                    "step_id": "review_output",
                    "description": "Review and validate synthesis quality",
                    "agent_id": "reviewer-v1",
                    "expected_inputs": ["synthesis"],
                    "expected_outputs": ["review_score", "suggestions"],
                    "timeout_seconds": 60,
                    "is_critical": False,
                    "order": 4,
                },
            ],
            "dependencies": {
                "summarize_papers": ["search_literature"],
                "synthesize_findings": ["summarize_papers"],
                "review_output": ["synthesize_findings"],
            },
            "rollback_points": ["search_literature", "summarize_papers"],
            "metadata": {"research_topic": "Agent reliability in multi-step workflows"},
        }

        collaborators = [
            {
                "agent_id": "research-assistant-v2",
                "agent_name": "Academic Research Assistant",
                "role": "search",
                "joined_at": start_time.isoformat(),
                "left_at": (start_time + timedelta(seconds=45)).isoformat(),
            },
            {
                "agent_id": "summarizer-v1",
                "agent_name": "Paper Summarizer",
                "role": "summarization",
                "joined_at": (start_time + timedelta(seconds=45)).isoformat(),
                "left_at": (start_time + timedelta(seconds=150)).isoformat(),
            },
            {
                "agent_id": "synthesizer-v1",
                "agent_name": "Research Synthesizer",
                "role": "synthesis",
                "joined_at": (start_time + timedelta(seconds=150)).isoformat(),
                "left_at": (start_time + timedelta(seconds=280)).isoformat(),
            },
            {
                "agent_id": "reviewer-v1",
                "agent_name": "Quality Reviewer",
                "role": "review",
                "joined_at": (start_time + timedelta(seconds=280)).isoformat(),
                "left_at": (start_time + timedelta(seconds=320)).isoformat(),
            },
        ]

        events = [
            {
                "event_id": "evt-001",
                "event_type": "step_start",
                "step_id": "search_literature",
                "timestamp": start_time.isoformat(),
                "agent_id": "research-assistant-v2",
                "metadata": {},
            },
            {
                "event_id": "evt-002",
                "event_type": "collaborator_join",
                "step_id": "search_literature",
                "timestamp": start_time.isoformat(),
                "agent_id": "research-assistant-v2",
                "metadata": {"role": "search"},
            },
            {
                "event_id": "evt-003",
                "event_type": "decision",
                "step_id": "search_literature",
                "timestamp": (start_time + timedelta(seconds=5)).isoformat(),
                "agent_id": "research-assistant-v2",
                "metadata": {
                    "decision": "Search PubMed, ArXiv, and Semantic Scholar",
                    "alternatives": ["PubMed only", "Google Scholar", "All databases"],
                    "rationale": "Balance of medical and CS papers needed for topic",
                },
            },
            {
                "event_id": "evt-004",
                "event_type": "checkpoint",
                "step_id": "search_literature",
                "timestamp": (start_time + timedelta(seconds=40)).isoformat(),
                "agent_id": "research-assistant-v2",
                "metadata": {
                    "checkpoint_id": "chk-001",
                    "state": {"papers_found": 47, "databases_searched": 3},
                },
            },
            {
                "event_id": "evt-005",
                "event_type": "step_end",
                "step_id": "search_literature",
                "timestamp": (start_time + timedelta(seconds=45)).isoformat(),
                "agent_id": "research-assistant-v2",
                "duration_ms": 45000,
                "metadata": {"success": True, "papers_found": 47},
            },
            # Summarization step
            {
                "event_id": "evt-006",
                "event_type": "step_start",
                "step_id": "summarize_papers",
                "timestamp": (start_time + timedelta(seconds=45)).isoformat(),
                "agent_id": "summarizer-v1",
                "metadata": {},
            },
            {
                "event_id": "evt-007",
                "event_type": "collaborator_join",
                "step_id": "summarize_papers",
                "timestamp": (start_time + timedelta(seconds=45)).isoformat(),
                "agent_id": "summarizer-v1",
                "metadata": {"role": "summarization"},
            },
            {
                "event_id": "evt-008",
                "event_type": "step_end",
                "step_id": "summarize_papers",
                "timestamp": (start_time + timedelta(seconds=150)).isoformat(),
                "agent_id": "summarizer-v1",
                "duration_ms": 105000,
                "metadata": {"success": True, "summaries_generated": 47, "key_findings": 12},
            },
            # Synthesis step
            {
                "event_id": "evt-009",
                "event_type": "step_start",
                "step_id": "synthesize_findings",
                "timestamp": (start_time + timedelta(seconds=150)).isoformat(),
                "agent_id": "synthesizer-v1",
                "metadata": {},
            },
            {
                "event_id": "evt-010",
                "event_type": "collaborator_join",
                "step_id": "synthesize_findings",
                "timestamp": (start_time + timedelta(seconds=150)).isoformat(),
                "agent_id": "synthesizer-v1",
                "metadata": {"role": "synthesis"},
            },
            {
                "event_id": "evt-011",
                "event_type": "decision",
                "step_id": "synthesize_findings",
                "timestamp": (start_time + timedelta(seconds=160)).isoformat(),
                "agent_id": "synthesizer-v1",
                "metadata": {
                    "decision": "Use thematic organization",
                    "alternatives": ["Chronological", "By source", "Thematic"],
                    "rationale": "Themes better highlight cross-paper patterns",
                },
            },
            {
                "event_id": "evt-012",
                "event_type": "step_end",
                "step_id": "synthesize_findings",
                "timestamp": (start_time + timedelta(seconds=280)).isoformat(),
                "agent_id": "synthesizer-v1",
                "duration_ms": 130000,
                "metadata": {"success": True, "word_count": 3500, "themes_identified": 5},
            },
            # Review step
            {
                "event_id": "evt-013",
                "event_type": "step_start",
                "step_id": "review_output",
                "timestamp": (start_time + timedelta(seconds=280)).isoformat(),
                "agent_id": "reviewer-v1",
                "metadata": {},
            },
            {
                "event_id": "evt-014",
                "event_type": "collaborator_join",
                "step_id": "review_output",
                "timestamp": (start_time + timedelta(seconds=280)).isoformat(),
                "agent_id": "reviewer-v1",
                "metadata": {"role": "review"},
            },
            {
                "event_id": "evt-015",
                "event_type": "step_end",
                "step_id": "review_output",
                "timestamp": (start_time + timedelta(seconds=320)).isoformat(),
                "agent_id": "reviewer-v1",
                "duration_ms": 40000,
                "metadata": {"success": True, "review_score": 0.89, "suggestions_count": 3},
            },
        ]

        execution_trace = {
            "trace_id": f"trace-{workflow_id}",
            "task_id": workflow_id,
            "events": events,
            "start_time": start_time.isoformat(),
            "end_time": (start_time + timedelta(seconds=320)).isoformat(),
            "total_duration_ms": 320000,
        }

        return {
            "workflow_id": workflow_id,
            "workflow_name": "Research Literature Review",
            "workflow_type": "research_workflow",
            "task_plan": task_plan,
            "collaborators": collaborators,
            "parameter_substitutions": [],
            "execution_trace": execution_trace,
            "outcome": {
                "status": "success",
                "reason": "Literature review completed with high quality score",
                "root_cause": None,
                "steps_completed": 4,
                "steps_failed": 0,
                "steps_skipped": 0,
            },
            "metadata": {
                "research_topic": "Agent reliability in multi-step workflows",
                "papers_reviewed": 47,
                "synthesis_quality": 0.89,
            },
        }

    def _generate_healthcare_diagnosis_trace(self) -> dict[str, Any]:
        """Generate healthcare diagnosis workflow - requires human approval."""
        workflow_id = "healthcare-diagnosis-001"
        start_time = datetime(2025, 11, 27, 9, 0, 0, tzinfo=UTC)

        task_plan = {
            "plan_id": f"plan-{workflow_id}",
            "task_id": workflow_id,
            "created_at": start_time.isoformat(),
            "steps": [
                {
                    "step_id": "analyze_symptoms",
                    "description": "Analyze patient symptoms",
                    "agent_id": "symptom-analyzer-v1",
                    "expected_inputs": ["patient_id", "symptoms", "duration"],
                    "expected_outputs": ["symptom_analysis", "severity_score"],
                    "timeout_seconds": 30,
                    "is_critical": True,
                    "order": 1,
                },
                {
                    "step_id": "interpret_labs",
                    "description": "Interpret laboratory results",
                    "agent_id": "lab-interpreter-v1",
                    "expected_inputs": ["patient_id", "lab_results"],
                    "expected_outputs": ["lab_interpretation", "abnormal_flags"],
                    "timeout_seconds": 45,
                    "is_critical": True,
                    "order": 2,
                },
                {
                    "step_id": "generate_diagnosis",
                    "description": "Generate differential diagnosis",
                    "agent_id": "diagnosis-generator-v1",
                    "expected_inputs": ["symptom_analysis", "lab_interpretation"],
                    "expected_outputs": ["diagnoses", "confidence_scores"],
                    "timeout_seconds": 60,
                    "is_critical": True,
                    "order": 3,
                },
                {
                    "step_id": "recommend_treatment",
                    "description": "Recommend treatment options",
                    "agent_id": "treatment-recommender-v1",
                    "expected_inputs": ["diagnoses", "patient_history"],
                    "expected_outputs": ["treatments", "contraindications"],
                    "timeout_seconds": 45,
                    "is_critical": True,
                    "order": 4,
                },
                {
                    "step_id": "physician_approval",
                    "description": "Await physician approval",
                    "agent_id": "human-approver",
                    "expected_inputs": ["diagnoses", "treatments"],
                    "expected_outputs": ["approval_status", "modifications"],
                    "timeout_seconds": 86400,
                    "is_critical": True,
                    "order": 5,
                },
            ],
            "dependencies": {
                "interpret_labs": ["analyze_symptoms"],
                "generate_diagnosis": ["analyze_symptoms", "interpret_labs"],
                "recommend_treatment": ["generate_diagnosis"],
                "physician_approval": ["recommend_treatment"],
            },
            "rollback_points": ["analyze_symptoms"],
            "metadata": {"patient_id": "PATIENT-ANON-001", "case_type": "routine"},
        }

        collaborators = [
            {
                "agent_id": "symptom-analyzer-v1",
                "agent_name": "Symptom Analysis Agent",
                "role": "symptom_analysis",
                "joined_at": start_time.isoformat(),
                "left_at": (start_time + timedelta(seconds=25)).isoformat(),
            },
            {
                "agent_id": "lab-interpreter-v1",
                "agent_name": "Lab Interpretation Agent",
                "role": "lab_analysis",
                "joined_at": (start_time + timedelta(seconds=25)).isoformat(),
                "left_at": (start_time + timedelta(seconds=60)).isoformat(),
            },
            {
                "agent_id": "diagnosis-generator-v1",
                "agent_name": "Medical Diagnosis Assistant",
                "role": "diagnosis",
                "joined_at": (start_time + timedelta(seconds=60)).isoformat(),
                "left_at": (start_time + timedelta(seconds=110)).isoformat(),
            },
            {
                "agent_id": "treatment-recommender-v1",
                "agent_name": "Treatment Recommendation Agent",
                "role": "treatment",
                "joined_at": (start_time + timedelta(seconds=110)).isoformat(),
                "left_at": (start_time + timedelta(seconds=145)).isoformat(),
            },
            {
                "agent_id": "human-approver",
                "agent_name": "Physician Approver",
                "role": "approval",
                "joined_at": (start_time + timedelta(seconds=145)).isoformat(),
                "left_at": None,  # Still pending
            },
        ]

        events = [
            {
                "event_id": "evt-001",
                "event_type": "step_start",
                "step_id": "analyze_symptoms",
                "timestamp": start_time.isoformat(),
                "agent_id": "symptom-analyzer-v1",
                "metadata": {},
            },
            {
                "event_id": "evt-002",
                "event_type": "collaborator_join",
                "step_id": "analyze_symptoms",
                "timestamp": start_time.isoformat(),
                "agent_id": "symptom-analyzer-v1",
                "metadata": {"role": "symptom_analysis"},
            },
            {
                "event_id": "evt-003",
                "event_type": "step_end",
                "step_id": "analyze_symptoms",
                "timestamp": (start_time + timedelta(seconds=25)).isoformat(),
                "agent_id": "symptom-analyzer-v1",
                "duration_ms": 25000,
                "metadata": {"success": True, "severity_score": 0.65},
            },
            {
                "event_id": "evt-004",
                "event_type": "step_start",
                "step_id": "interpret_labs",
                "timestamp": (start_time + timedelta(seconds=25)).isoformat(),
                "agent_id": "lab-interpreter-v1",
                "metadata": {},
            },
            {
                "event_id": "evt-005",
                "event_type": "step_end",
                "step_id": "interpret_labs",
                "timestamp": (start_time + timedelta(seconds=60)).isoformat(),
                "agent_id": "lab-interpreter-v1",
                "duration_ms": 35000,
                "metadata": {"success": True, "abnormal_values": 3},
            },
            {
                "event_id": "evt-006",
                "event_type": "step_start",
                "step_id": "generate_diagnosis",
                "timestamp": (start_time + timedelta(seconds=60)).isoformat(),
                "agent_id": "diagnosis-generator-v1",
                "metadata": {},
            },
            {
                "event_id": "evt-007",
                "event_type": "collaborator_join",
                "step_id": "generate_diagnosis",
                "timestamp": (start_time + timedelta(seconds=60)).isoformat(),
                "agent_id": "diagnosis-generator-v1",
                "metadata": {"role": "diagnosis"},
            },
            {
                "event_id": "evt-008",
                "event_type": "decision",
                "step_id": "generate_diagnosis",
                "timestamp": (start_time + timedelta(seconds=80)).isoformat(),
                "agent_id": "diagnosis-generator-v1",
                "metadata": {
                    "decision": "Primary diagnosis: Poorly controlled Type 2 Diabetes",
                    "alternatives": [
                        "Type 2 Diabetes",
                        "Thyroid disorder",
                        "Metabolic syndrome",
                    ],
                    "rationale": "Lab results show elevated HbA1c (7.2%) and fasting glucose (145)",
                    "confidence": 0.92,
                },
            },
            {
                "event_id": "evt-009",
                "event_type": "step_end",
                "step_id": "generate_diagnosis",
                "timestamp": (start_time + timedelta(seconds=110)).isoformat(),
                "agent_id": "diagnosis-generator-v1",
                "duration_ms": 50000,
                "metadata": {"success": True, "diagnosis_confidence": 0.92, "requires_approval": True},
            },
            {
                "event_id": "evt-010",
                "event_type": "step_start",
                "step_id": "recommend_treatment",
                "timestamp": (start_time + timedelta(seconds=110)).isoformat(),
                "agent_id": "treatment-recommender-v1",
                "metadata": {},
            },
            {
                "event_id": "evt-011",
                "event_type": "step_end",
                "step_id": "recommend_treatment",
                "timestamp": (start_time + timedelta(seconds=145)).isoformat(),
                "agent_id": "treatment-recommender-v1",
                "duration_ms": 35000,
                "metadata": {"success": True, "treatments_suggested": 3},
            },
            {
                "event_id": "evt-012",
                "event_type": "step_start",
                "step_id": "physician_approval",
                "timestamp": (start_time + timedelta(seconds=145)).isoformat(),
                "agent_id": "human-approver",
                "metadata": {"awaiting_human": True},
            },
        ]

        execution_trace = {
            "trace_id": f"trace-{workflow_id}",
            "task_id": workflow_id,
            "events": events,
            "start_time": start_time.isoformat(),
            "end_time": None,  # Still pending
            "total_duration_ms": None,
        }

        return {
            "workflow_id": workflow_id,
            "workflow_name": "Healthcare Diagnosis Workflow",
            "workflow_type": "healthcare_diagnosis",
            "task_plan": task_plan,
            "collaborators": collaborators,
            "parameter_substitutions": [],
            "execution_trace": execution_trace,
            "outcome": {
                "status": "pending_approval",
                "reason": "Awaiting physician approval for diagnosis and treatment",
                "root_cause": None,
                "steps_completed": 4,
                "steps_failed": 0,
                "steps_skipped": 0,
                "steps_pending": 1,
            },
            "metadata": {
                "patient_id": "PATIENT-ANON-001",
                "primary_diagnosis": "Poorly controlled Type 2 Diabetes",
                "diagnosis_confidence": 0.92,
                "requires_approval": True,
            },
        }

    def _generate_contract_review_trace(self) -> dict[str, Any]:
        """Generate contract review workflow - manual review required."""
        workflow_id = "contract-review-001"
        start_time = datetime(2025, 11, 27, 11, 0, 0, tzinfo=UTC)

        task_plan = {
            "plan_id": f"plan-{workflow_id}",
            "task_id": workflow_id,
            "created_at": start_time.isoformat(),
            "steps": [
                {
                    "step_id": "extract_clauses",
                    "description": "Extract and categorize contract clauses",
                    "agent_id": "contract-reviewer-v1",
                    "expected_inputs": ["contract_text", "contract_type"],
                    "expected_outputs": ["clauses", "clause_count"],
                    "timeout_seconds": 120,
                    "is_critical": True,
                    "order": 1,
                },
                {
                    "step_id": "assess_risk",
                    "description": "Evaluate legal risk of contract terms",
                    "agent_id": "risk-assessor-v1",
                    "expected_inputs": ["clauses", "jurisdiction"],
                    "expected_outputs": ["risk_assessment", "flagged_clauses"],
                    "timeout_seconds": 90,
                    "is_critical": True,
                    "order": 2,
                },
                {
                    "step_id": "compliance_check",
                    "description": "Check regulatory compliance",
                    "agent_id": "compliance-checker-v1",
                    "expected_inputs": ["clauses", "risk_assessment"],
                    "expected_outputs": ["compliance_status", "violations"],
                    "timeout_seconds": 60,
                    "is_critical": True,
                    "order": 3,
                },
            ],
            "dependencies": {
                "assess_risk": ["extract_clauses"],
                "compliance_check": ["assess_risk"],
            },
            "rollback_points": ["extract_clauses"],
            "metadata": {"contract_id": "CONTRACT-001", "contract_type": "employment"},
        }

        collaborators = [
            {
                "agent_id": "contract-reviewer-v1",
                "agent_name": "Legal Contract Analyzer",
                "role": "extraction",
                "joined_at": start_time.isoformat(),
                "left_at": (start_time + timedelta(seconds=95)).isoformat(),
            },
            {
                "agent_id": "risk-assessor-v1",
                "agent_name": "Risk Assessment Agent",
                "role": "risk_assessment",
                "joined_at": (start_time + timedelta(seconds=95)).isoformat(),
                "left_at": (start_time + timedelta(seconds=165)).isoformat(),
            },
            {
                "agent_id": "compliance-checker-v1",
                "agent_name": "Compliance Checker",
                "role": "compliance",
                "joined_at": (start_time + timedelta(seconds=165)).isoformat(),
                "left_at": (start_time + timedelta(seconds=210)).isoformat(),
            },
        ]

        events = [
            {
                "event_id": "evt-001",
                "event_type": "step_start",
                "step_id": "extract_clauses",
                "timestamp": start_time.isoformat(),
                "agent_id": "contract-reviewer-v1",
                "metadata": {},
            },
            {
                "event_id": "evt-002",
                "event_type": "collaborator_join",
                "step_id": "extract_clauses",
                "timestamp": start_time.isoformat(),
                "agent_id": "contract-reviewer-v1",
                "metadata": {"role": "extraction"},
            },
            {
                "event_id": "evt-003",
                "event_type": "decision",
                "step_id": "extract_clauses",
                "timestamp": (start_time + timedelta(seconds=30)).isoformat(),
                "agent_id": "contract-reviewer-v1",
                "metadata": {
                    "decision": "Use employment contract template",
                    "alternatives": ["Generic template", "Employment template", "NDA template"],
                    "rationale": "Contract type specified as employment agreement",
                },
            },
            {
                "event_id": "evt-004",
                "event_type": "step_end",
                "step_id": "extract_clauses",
                "timestamp": (start_time + timedelta(seconds=95)).isoformat(),
                "agent_id": "contract-reviewer-v1",
                "duration_ms": 95000,
                "metadata": {"success": True, "clauses_extracted": 8},
            },
            {
                "event_id": "evt-005",
                "event_type": "step_start",
                "step_id": "assess_risk",
                "timestamp": (start_time + timedelta(seconds=95)).isoformat(),
                "agent_id": "risk-assessor-v1",
                "metadata": {},
            },
            {
                "event_id": "evt-006",
                "event_type": "collaborator_join",
                "step_id": "assess_risk",
                "timestamp": (start_time + timedelta(seconds=95)).isoformat(),
                "agent_id": "risk-assessor-v1",
                "metadata": {"role": "risk_assessment"},
            },
            {
                "event_id": "evt-007",
                "event_type": "decision",
                "step_id": "assess_risk",
                "timestamp": (start_time + timedelta(seconds=130)).isoformat(),
                "agent_id": "risk-assessor-v1",
                "metadata": {
                    "decision": "Flag non-compete clause for manual review",
                    "alternatives": ["Auto-approve", "Flag for review", "Reject"],
                    "rationale": "Non-compete clause may be unenforceable in California",
                    "risk_level": "high",
                },
            },
            {
                "event_id": "evt-008",
                "event_type": "step_end",
                "step_id": "assess_risk",
                "timestamp": (start_time + timedelta(seconds=165)).isoformat(),
                "agent_id": "risk-assessor-v1",
                "duration_ms": 70000,
                "metadata": {"success": True, "high_risk_clauses": 1, "overall_risk": "high"},
            },
            {
                "event_id": "evt-009",
                "event_type": "step_start",
                "step_id": "compliance_check",
                "timestamp": (start_time + timedelta(seconds=165)).isoformat(),
                "agent_id": "compliance-checker-v1",
                "metadata": {},
            },
            {
                "event_id": "evt-010",
                "event_type": "collaborator_join",
                "step_id": "compliance_check",
                "timestamp": (start_time + timedelta(seconds=165)).isoformat(),
                "agent_id": "compliance-checker-v1",
                "metadata": {"role": "compliance"},
            },
            {
                "event_id": "evt-011",
                "event_type": "step_end",
                "step_id": "compliance_check",
                "timestamp": (start_time + timedelta(seconds=210)).isoformat(),
                "agent_id": "compliance-checker-v1",
                "duration_ms": 45000,
                "metadata": {"success": True, "violations_found": 0, "warnings": 1},
            },
        ]

        execution_trace = {
            "trace_id": f"trace-{workflow_id}",
            "task_id": workflow_id,
            "events": events,
            "start_time": start_time.isoformat(),
            "end_time": (start_time + timedelta(seconds=210)).isoformat(),
            "total_duration_ms": 210000,
        }

        return {
            "workflow_id": workflow_id,
            "workflow_name": "Legal Contract Review",
            "workflow_type": "contract_review",
            "task_plan": task_plan,
            "collaborators": collaborators,
            "parameter_substitutions": [],
            "execution_trace": execution_trace,
            "outcome": {
                "status": "manual_review_required",
                "reason": "High-risk non-compete clause detected - requires legal counsel review",
                "root_cause": None,
                "steps_completed": 3,
                "steps_failed": 0,
                "steps_skipped": 0,
            },
            "metadata": {
                "contract_id": "CONTRACT-001",
                "contract_type": "employment",
                "clauses_extracted": 8,
                "high_risk_clauses": 1,
                "flagged_clause_type": "non_compete",
            },
        }


def generate_workflow_traces(count: int = 5, seed: int = 42) -> list[dict[str, Any]]:
    """Generate workflow trace dataset.

    Args:
        count: Number of workflows to generate
        seed: Random seed for reproducibility

    Returns:
        List of workflow trace dictionaries
    """
    generator = WorkflowTracesGenerator(seed=seed)
    return generator.generate(count)

