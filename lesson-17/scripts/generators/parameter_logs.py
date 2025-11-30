"""Parameter Substitution Logs Generator for debugging demonstrations.

Generates 20 parameter change events following the ParameterSubstitution schema:
- Parameter types: confidence_threshold, model_version, temperature, max_tokens, retry_attempts
- Before/after values with justifications
- Impact analysis (success rate changes, latency impact)

Shows how parameter changes affect workflow outcomes for debugging aid.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from . import BaseGenerator


class ParameterLogsGenerator(BaseGenerator):
    """Generator for parameter substitution events.

    Creates realistic parameter change logs for debugging and audit demonstrations.
    """

    # Parameter definitions with realistic values
    PARAMETER_DEFINITIONS = [
        {
            "parameter_name": "confidence_threshold",
            "description": "Minimum confidence score for accepting model outputs",
            "value_type": "float",
            "value_range": (0.5, 0.99),
            "common_changes": [
                {"old": 0.8, "new": 0.95, "reason": "Reduce false positives", "impact": "negative"},
                {"old": 0.9, "new": 0.75, "reason": "Increase recall", "impact": "positive"},
                {"old": 0.85, "new": 0.9, "reason": "Compliance requirement", "impact": "neutral"},
            ],
        },
        {
            "parameter_name": "model_version",
            "description": "LLM model version used for inference",
            "value_type": "string",
            "value_range": None,
            "common_changes": [
                {"old": "gpt-3.5-turbo", "new": "gpt-4", "reason": "Improve accuracy", "impact": "positive"},
                {"old": "gpt-4", "new": "gpt-4-turbo", "reason": "Reduce latency", "impact": "positive"},
                {"old": "claude-2", "new": "claude-3-sonnet", "reason": "Model upgrade", "impact": "positive"},
                {"old": "gpt-4", "new": "gpt-3.5-turbo", "reason": "Cost reduction", "impact": "neutral"},
            ],
        },
        {
            "parameter_name": "temperature",
            "description": "Sampling temperature for model outputs",
            "value_type": "float",
            "value_range": (0.0, 2.0),
            "common_changes": [
                {"old": 0.7, "new": 0.3, "reason": "More deterministic outputs", "impact": "positive"},
                {"old": 0.5, "new": 1.0, "reason": "Increase creativity", "impact": "neutral"},
                {"old": 1.2, "new": 0.7, "reason": "Reduce hallucinations", "impact": "positive"},
            ],
        },
        {
            "parameter_name": "max_tokens",
            "description": "Maximum tokens in model response",
            "value_type": "int",
            "value_range": (100, 8192),
            "common_changes": [
                {"old": 512, "new": 1024, "reason": "Support longer responses", "impact": "positive"},
                {"old": 2048, "new": 512, "reason": "Cost optimization", "impact": "negative"},
                {"old": 1024, "new": 4096, "reason": "Handle complex queries", "impact": "positive"},
            ],
        },
        {
            "parameter_name": "retry_attempts",
            "description": "Number of retry attempts on failure",
            "value_type": "int",
            "value_range": (1, 10),
            "common_changes": [
                {"old": 3, "new": 5, "reason": "Improve reliability", "impact": "positive"},
                {"old": 5, "new": 3, "reason": "Reduce latency", "impact": "negative"},
                {"old": 2, "new": 4, "reason": "Handle transient failures", "impact": "positive"},
            ],
        },
        {
            "parameter_name": "timeout_seconds",
            "description": "Request timeout in seconds",
            "value_type": "int",
            "value_range": (5, 300),
            "common_changes": [
                {"old": 30, "new": 60, "reason": "Allow complex processing", "impact": "positive"},
                {"old": 60, "new": 30, "reason": "Fail fast for responsiveness", "impact": "neutral"},
                {"old": 120, "new": 60, "reason": "Resource efficiency", "impact": "neutral"},
            ],
        },
        {
            "parameter_name": "batch_size",
            "description": "Number of items processed per batch",
            "value_type": "int",
            "value_range": (1, 256),
            "common_changes": [
                {"old": 32, "new": 64, "reason": "Improve throughput", "impact": "positive"},
                {"old": 128, "new": 32, "reason": "Memory constraints", "impact": "negative"},
                {"old": 16, "new": 64, "reason": "Optimize GPU utilization", "impact": "positive"},
            ],
        },
        {
            "parameter_name": "fraud_threshold",
            "description": "Threshold for flagging transactions as fraudulent",
            "value_type": "float",
            "value_range": (0.5, 0.99),
            "common_changes": [
                {"old": 0.75, "new": 0.85, "reason": "Reduce false positives (SOX audit)", "impact": "negative"},
                {"old": 0.9, "new": 0.8, "reason": "Catch more fraud", "impact": "positive"},
                {"old": 0.7, "new": 0.85, "reason": "Compliance requirement", "impact": "negative"},
            ],
        },
    ]

    # Workflow contexts
    WORKFLOW_CONTEXTS = [
        {"workflow_type": "fraud_detection", "workflow_prefix": "fraud-pipeline"},
        {"workflow_type": "invoice_processing", "workflow_prefix": "invoice-workflow"},
        {"workflow_type": "diagnosis_generation", "workflow_prefix": "healthcare-diagnosis"},
        {"workflow_type": "contract_review", "workflow_prefix": "legal-review"},
        {"workflow_type": "research_synthesis", "workflow_prefix": "research-workflow"},
    ]

    # Users/agents that can make changes
    CHANGE_ACTORS = [
        {"id": "user_admin", "type": "human", "role": "administrator"},
        {"id": "compliance_team", "type": "team", "role": "compliance"},
        {"id": "ml_engineer", "type": "human", "role": "engineer"},
        {"id": "auto_tuner", "type": "system", "role": "automated"},
        {"id": "devops_bot", "type": "system", "role": "operations"},
    ]

    def generate(self, count: int = 20) -> list[dict[str, Any]]:
        """Generate parameter substitution logs.

        Args:
            count: Number of parameter changes to generate (default: 20)

        Returns:
            List of parameter substitution dictionaries
        """
        logs: list[dict[str, Any]] = []

        for i in range(count):
            log = self._generate_parameter_change(i)
            logs.append(log)

        # Sort by timestamp
        logs.sort(key=lambda x: x["timestamp"])

        return logs

    def _generate_parameter_change(self, index: int) -> dict[str, Any]:
        """Generate a single parameter change event.

        Args:
            index: Sequential index for ID generation

        Returns:
            Parameter substitution dictionary with impact analysis
        """
        # Select parameter definition
        param_def = self.random_choice(self.PARAMETER_DEFINITIONS)
        change = self.random_choice(param_def["common_changes"])

        # Select workflow context
        context = self.random_choice(self.WORKFLOW_CONTEXTS)
        workflow_id = f"{context['workflow_prefix']}-{self.random_int(1, 100):03d}"

        # Select actor
        actor = self.random_choice(self.CHANGE_ACTORS)

        # Generate timestamp (within last 30 days)
        timestamp = self.random_datetime(
            start=datetime.now(UTC) - timedelta(days=30),
            end=datetime.now(UTC),
        )

        # Generate impact metrics
        impact = self._generate_impact_metrics(change["impact"], param_def["parameter_name"])

        return {
            "substitution_id": f"param-sub-{index + 1:03d}",
            "workflow_id": workflow_id,
            "workflow_type": context["workflow_type"],
            "timestamp": timestamp.isoformat(),
            "parameter_name": param_def["parameter_name"],
            "parameter_description": param_def["description"],
            "old_value": change["old"],
            "new_value": change["new"],
            "value_type": param_def["value_type"],
            "justification": change["reason"],
            "changed_by": actor["id"],
            "changed_by_type": actor["type"],
            "change_reason_category": self._categorize_reason(change["reason"]),
            "impact": impact,
            "rollback_available": True,
            "requires_approval": actor["type"] == "human",
            "metadata": {
                "source": "parameter_tuning" if actor["type"] == "system" else "manual_override",
                "environment": self.random_choice(["production", "staging", "canary"]),
                "affected_steps": self._get_affected_steps(param_def["parameter_name"]),
            },
        }

    def _generate_impact_metrics(
        self, impact_type: str, parameter_name: str
    ) -> dict[str, Any]:
        """Generate realistic impact metrics for a parameter change.

        Args:
            impact_type: Type of impact (positive, negative, neutral)
            parameter_name: Name of the parameter changed

        Returns:
            Impact metrics dictionary
        """
        base_success_rate = self.random_float(0.88, 0.96)
        base_latency = self.random_int(200, 800)
        base_cost = self.random_float(0.005, 0.02)

        if impact_type == "positive":
            success_delta = self.random_float(0.01, 0.05)
            latency_delta = self.random_int(-100, 50)
            cost_delta = self.random_float(-0.002, 0.005)
        elif impact_type == "negative":
            success_delta = self.random_float(-0.08, -0.02)
            latency_delta = self.random_int(-50, 200)
            cost_delta = self.random_float(-0.001, 0.003)
        else:  # neutral
            success_delta = self.random_float(-0.02, 0.02)
            latency_delta = self.random_int(-50, 50)
            cost_delta = self.random_float(-0.002, 0.002)

        workflows_affected = self.random_int(50, 500)

        return {
            "workflows_affected": workflows_affected,
            "success_rate_before": round(base_success_rate, 3),
            "success_rate_after": round(base_success_rate + success_delta, 3),
            "success_rate_delta": round(success_delta, 3),
            "latency_p50_before_ms": base_latency,
            "latency_p50_after_ms": base_latency + latency_delta,
            "latency_delta_ms": latency_delta,
            "cost_per_call_before": round(base_cost, 4),
            "cost_per_call_after": round(base_cost + cost_delta, 4),
            "estimated_daily_cost_impact": round(workflows_affected * cost_delta * 24, 2),
            "root_cause_correlation": self._get_root_cause(
                parameter_name, impact_type
            ),
            "recommendation": self._get_recommendation(parameter_name, impact_type),
        }

    def _categorize_reason(self, reason: str) -> str:
        """Categorize the change reason.

        Args:
            reason: Justification text

        Returns:
            Category string
        """
        reason_lower = reason.lower()
        if any(term in reason_lower for term in ["compliance", "sox", "audit", "requirement"]):
            return "compliance_requirement"
        elif any(term in reason_lower for term in ["cost", "budget", "efficiency"]):
            return "cost_optimization"
        elif any(term in reason_lower for term in ["accuracy", "improve", "quality"]):
            return "quality_improvement"
        elif any(term in reason_lower for term in ["latency", "speed", "fast"]):
            return "performance_optimization"
        elif any(term in reason_lower for term in ["reliability", "retry", "failure"]):
            return "reliability_improvement"
        else:
            return "general_tuning"

    def _get_affected_steps(self, parameter_name: str) -> list[str]:
        """Get workflow steps affected by parameter change.

        Args:
            parameter_name: Name of the parameter

        Returns:
            List of affected step names
        """
        step_mappings = {
            "confidence_threshold": ["validation", "output_filtering", "decision"],
            "model_version": ["inference", "generation", "scoring"],
            "temperature": ["generation", "sampling"],
            "max_tokens": ["generation", "summarization"],
            "retry_attempts": ["api_call", "external_service"],
            "timeout_seconds": ["api_call", "processing", "external_service"],
            "batch_size": ["data_loading", "inference", "processing"],
            "fraud_threshold": ["scoring", "decision", "escalation"],
        }
        return step_mappings.get(parameter_name, ["processing"])

    def _get_root_cause(self, parameter_name: str, impact_type: str) -> str | None:
        """Get root cause explanation for negative impacts.

        Args:
            parameter_name: Name of the parameter
            impact_type: Type of impact

        Returns:
            Root cause explanation or None
        """
        if impact_type != "negative":
            return None

        root_causes = {
            "confidence_threshold": "Threshold too high → empty results → cascade failures",
            "model_version": "Downgraded model → reduced accuracy → more retries needed",
            "temperature": "Increased randomness → inconsistent outputs → validation failures",
            "max_tokens": "Truncated responses → incomplete data → downstream errors",
            "retry_attempts": "Fewer retries → unrecovered transient failures",
            "timeout_seconds": "Shorter timeout → premature failures on slow requests",
            "batch_size": "Larger batches → memory pressure → OOM errors",
            "fraud_threshold": "Higher threshold → missed fraud cases or more false negatives",
        }
        return root_causes.get(parameter_name)

    def _get_recommendation(self, parameter_name: str, impact_type: str) -> str:
        """Get recommendation based on impact.

        Args:
            parameter_name: Name of the parameter
            impact_type: Type of impact

        Returns:
            Recommendation string
        """
        if impact_type == "positive":
            return "Monitor for sustained improvement; consider applying to all environments"
        elif impact_type == "negative":
            recommendations = {
                "confidence_threshold": "Add GuardRail for threshold bounds (0.5-0.9)",
                "model_version": "Consider cost-benefit analysis before further downgrades",
                "temperature": "Use lower temperature for tasks requiring consistency",
                "max_tokens": "Increase token limit for complex response scenarios",
                "retry_attempts": "Increase retries for critical paths; add circuit breaker",
                "timeout_seconds": "Profile slow requests; consider async processing",
                "batch_size": "Reduce batch size; implement memory monitoring",
                "fraud_threshold": "Review threshold with compliance team; consider tiered approach",
            }
            return recommendations.get(parameter_name, "Review change and consider rollback")
        else:
            return "Continue monitoring; no immediate action required"


def generate_parameter_logs(count: int = 20, seed: int = 42) -> list[dict[str, Any]]:
    """Generate parameter substitution logs dataset.

    Args:
        count: Number of parameter changes to generate
        seed: Random seed for reproducibility

    Returns:
        List of parameter substitution dictionaries
    """
    generator = ParameterLogsGenerator(seed=seed)
    return generator.generate(count)

