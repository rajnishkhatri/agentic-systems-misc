"""Agent Metadata Generator for AgentFacts demonstration.

Generates 10 diverse agent profiles following the AgentFacts schema
from lesson-17/backend/explainability/agent_facts.py.

Agent types covered:
- Invoice Extractor (OCR + field extraction)
- Fraud Detector (ML model + rule-based)
- Diagnosis Generator (multi-modal LLM)
- Contract Reviewer (legal entity recognition)
- Research Assistant (literature search + summarization)
- Data Validator (schema validation)
- Report Generator (document synthesis)
- Anomaly Detector (time-series analysis)
- Sentiment Analyzer (NLP classification)
- Recommendation Engine (collaborative filtering)

Each agent includes:
- Capabilities with input/output schemas, latency SLAs, cost estimates
- Policies (rate limits, approval requirements, data access controls)
- Cryptographic signatures (SHA256)
- Version history
"""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime, timedelta
from typing import Any

from . import COMPANY_NAMES, BaseGenerator


class AgentMetadataGenerator(BaseGenerator):
    """Generator for AgentFacts metadata records.

    Creates realistic agent profiles for governance and audit demonstrations.
    """

    # Agent definitions with capabilities and policies
    AGENT_DEFINITIONS = [
        {
            "agent_id": "invoice-extractor-v2",
            "agent_name": "Invoice Data Extractor",
            "owner": "finance-team",
            "description": "Extracts structured data from invoice documents using OCR and NLP",
            "capabilities": [
                {
                    "name": "extract_vendor",
                    "description": "Extracts vendor name and address from invoice header",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "invoice_text": {"type": "string"},
                            "invoice_image": {"type": "string", "format": "base64"},
                        },
                        "required": ["invoice_text"],
                    },
                    "output_schema": {
                        "type": "object",
                        "properties": {
                            "vendor_name": {"type": "string"},
                            "vendor_address": {"type": "string"},
                            "confidence": {"type": "number"},
                        },
                    },
                    "estimated_latency_ms": 500,
                    "cost_per_call": 0.005,
                    "requires_approval": False,
                    "tags": ["extraction", "ocr", "vendor"],
                },
                {
                    "name": "extract_line_items",
                    "description": "Extracts line items with quantities and amounts",
                    "input_schema": {
                        "type": "object",
                        "properties": {"invoice_text": {"type": "string"}},
                    },
                    "output_schema": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "description": {"type": "string"},
                                "quantity": {"type": "integer"},
                                "unit_price": {"type": "number"},
                                "total": {"type": "number"},
                            },
                        },
                    },
                    "estimated_latency_ms": 800,
                    "cost_per_call": 0.008,
                    "requires_approval": False,
                    "tags": ["extraction", "line_items", "financial"],
                },
            ],
            "policies": [
                {
                    "policy_type": "rate_limit",
                    "name": "API Rate Limit",
                    "description": "Limits API calls to prevent abuse",
                    "constraints": {
                        "max_calls_per_minute": 100,
                        "max_calls_per_hour": 2000,
                        "burst_limit": 25,
                    },
                },
                {
                    "policy_type": "data_access",
                    "name": "Invoice Data Access",
                    "description": "Controls access to invoice data fields",
                    "constraints": {
                        "allowed_fields": ["vendor_name", "invoice_number", "amount", "date"],
                        "restricted_fields": ["bank_account", "routing_number"],
                        "requires_encryption": True,
                    },
                },
            ],
        },
        {
            "agent_id": "fraud-detector-v2",
            "agent_name": "Transaction Fraud Detector",
            "owner": "security-team",
            "description": "Analyzes transaction patterns for fraud indicators using ML models",
            "capabilities": [
                {
                    "name": "score_transaction",
                    "description": "Calculates fraud risk score for a transaction",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "transaction_id": {"type": "string"},
                            "amount": {"type": "number"},
                            "merchant": {"type": "string"},
                            "timestamp": {"type": "string", "format": "date-time"},
                            "user_id": {"type": "string"},
                        },
                        "required": ["transaction_id", "amount"],
                    },
                    "output_schema": {
                        "type": "object",
                        "properties": {
                            "fraud_score": {"type": "number", "minimum": 0, "maximum": 1},
                            "risk_level": {"type": "string", "enum": ["low", "medium", "high"]},
                            "flags": {"type": "array", "items": {"type": "string"}},
                        },
                    },
                    "estimated_latency_ms": 350,
                    "cost_per_call": 0.01,
                    "requires_approval": False,
                    "tags": ["fraud", "ml", "real-time"],
                },
                {
                    "name": "explain_score",
                    "description": "Provides explanation for fraud score decision",
                    "input_schema": {
                        "type": "object",
                        "properties": {"transaction_id": {"type": "string"}},
                    },
                    "output_schema": {
                        "type": "object",
                        "properties": {
                            "reasoning": {"type": "string"},
                            "top_factors": {"type": "array", "items": {"type": "string"}},
                            "similar_cases": {"type": "integer"},
                        },
                    },
                    "estimated_latency_ms": 500,
                    "cost_per_call": 0.015,
                    "requires_approval": False,
                    "tags": ["explainability", "fraud"],
                },
            ],
            "policies": [
                {
                    "policy_type": "rate_limit",
                    "name": "High-Volume Rate Limit",
                    "description": "Supports high transaction volume",
                    "constraints": {
                        "max_calls_per_minute": 1000,
                        "max_calls_per_hour": 50000,
                        "burst_limit": 100,
                    },
                },
                {
                    "policy_type": "approval_required",
                    "name": "High-Risk Approval",
                    "description": "Requires human approval for blocking high-value transactions",
                    "constraints": {
                        "threshold_amount": 10000,
                        "auto_approve_below": 1000,
                        "escalation_timeout_minutes": 30,
                    },
                },
            ],
        },
        {
            "agent_id": "diagnosis-generator-v1",
            "agent_name": "Medical Diagnosis Assistant",
            "owner": "healthcare-ai-team",
            "description": "Generates preliminary diagnosis suggestions from patient symptoms and lab results",
            "capabilities": [
                {
                    "name": "analyze_symptoms",
                    "description": "Analyzes patient symptoms for potential conditions",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "patient_id": {"type": "string"},
                            "symptoms": {"type": "array", "items": {"type": "string"}},
                            "duration_days": {"type": "integer"},
                            "severity": {"type": "string", "enum": ["mild", "moderate", "severe"]},
                        },
                        "required": ["symptoms"],
                    },
                    "output_schema": {
                        "type": "object",
                        "properties": {
                            "differential_diagnoses": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "condition": {"type": "string"},
                                        "probability": {"type": "number"},
                                    },
                                },
                            },
                            "recommended_tests": {"type": "array", "items": {"type": "string"}},
                        },
                    },
                    "estimated_latency_ms": 2000,
                    "cost_per_call": 0.05,
                    "requires_approval": True,
                    "tags": ["healthcare", "diagnosis", "llm"],
                },
                {
                    "name": "interpret_labs",
                    "description": "Interprets laboratory results in clinical context",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "lab_results": {"type": "object"},
                            "reference_ranges": {"type": "object"},
                        },
                    },
                    "output_schema": {
                        "type": "object",
                        "properties": {
                            "abnormal_values": {"type": "array"},
                            "clinical_significance": {"type": "string"},
                            "follow_up_recommendations": {"type": "array"},
                        },
                    },
                    "estimated_latency_ms": 1500,
                    "cost_per_call": 0.03,
                    "requires_approval": True,
                    "tags": ["healthcare", "labs", "interpretation"],
                },
            ],
            "policies": [
                {
                    "policy_type": "data_access",
                    "name": "HIPAA Compliance",
                    "description": "Ensures HIPAA-compliant data handling",
                    "constraints": {
                        "allowed_data_sources": ["patient_db"],
                        "pii_handling_mode": "redact",
                        "audit_all_access": True,
                        "data_retention_days": 365,
                    },
                },
                {
                    "policy_type": "approval_required",
                    "name": "Physician Approval",
                    "description": "All diagnoses require physician review",
                    "constraints": {
                        "approval_role": "physician",
                        "max_pending_hours": 24,
                        "auto_escalate": True,
                    },
                },
            ],
        },
        {
            "agent_id": "contract-reviewer-v1",
            "agent_name": "Legal Contract Analyzer",
            "owner": "legal-tech-team",
            "description": "Extracts clauses and assesses risk in legal contracts",
            "capabilities": [
                {
                    "name": "extract_clauses",
                    "description": "Identifies and categorizes contract clauses",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "contract_text": {"type": "string"},
                            "contract_type": {
                                "type": "string",
                                "enum": ["employment", "nda", "service", "lease", "partnership"],
                            },
                        },
                        "required": ["contract_text"],
                    },
                    "output_schema": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "clause_id": {"type": "string"},
                                "clause_type": {"type": "string"},
                                "text": {"type": "string"},
                                "page": {"type": "integer"},
                            },
                        },
                    },
                    "estimated_latency_ms": 3000,
                    "cost_per_call": 0.02,
                    "requires_approval": False,
                    "tags": ["legal", "extraction", "contracts"],
                },
                {
                    "name": "assess_risk",
                    "description": "Evaluates legal risk of contract terms",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "clauses": {"type": "array"},
                            "jurisdiction": {"type": "string"},
                        },
                    },
                    "output_schema": {
                        "type": "object",
                        "properties": {
                            "overall_risk": {"type": "string", "enum": ["low", "medium", "high"]},
                            "flagged_clauses": {"type": "array"},
                            "recommendations": {"type": "array"},
                        },
                    },
                    "estimated_latency_ms": 2500,
                    "cost_per_call": 0.025,
                    "requires_approval": False,
                    "tags": ["legal", "risk", "compliance"],
                },
            ],
            "policies": [
                {
                    "policy_type": "rate_limit",
                    "name": "Document Processing Limit",
                    "description": "Limits concurrent document processing",
                    "constraints": {
                        "max_calls_per_minute": 20,
                        "max_calls_per_hour": 200,
                        "max_document_size_mb": 50,
                    },
                },
            ],
        },
        {
            "agent_id": "research-assistant-v2",
            "agent_name": "Academic Research Assistant",
            "owner": "research-team",
            "description": "Searches literature and synthesizes research findings",
            "capabilities": [
                {
                    "name": "search_literature",
                    "description": "Searches academic databases for relevant papers",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string"},
                            "databases": {
                                "type": "array",
                                "items": {"type": "string"},
                                "default": ["pubmed", "arxiv", "semantic_scholar"],
                            },
                            "date_range": {"type": "object"},
                            "max_results": {"type": "integer", "default": 50},
                        },
                        "required": ["query"],
                    },
                    "output_schema": {
                        "type": "object",
                        "properties": {
                            "papers": {"type": "array"},
                            "total_found": {"type": "integer"},
                            "query_expansion": {"type": "array"},
                        },
                    },
                    "estimated_latency_ms": 5000,
                    "cost_per_call": 0.01,
                    "requires_approval": False,
                    "tags": ["research", "search", "literature"],
                },
                {
                    "name": "summarize_papers",
                    "description": "Generates summaries of research papers",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "paper_ids": {"type": "array", "items": {"type": "string"}},
                            "summary_type": {
                                "type": "string",
                                "enum": ["abstract", "detailed", "comparison"],
                            },
                        },
                    },
                    "output_schema": {
                        "type": "object",
                        "properties": {
                            "summaries": {"type": "array"},
                            "key_findings": {"type": "array"},
                            "citations": {"type": "array"},
                        },
                    },
                    "estimated_latency_ms": 8000,
                    "cost_per_call": 0.05,
                    "requires_approval": False,
                    "tags": ["research", "summarization", "llm"],
                },
            ],
            "policies": [
                {
                    "policy_type": "rate_limit",
                    "name": "API Rate Limit",
                    "description": "Standard rate limiting",
                    "constraints": {
                        "max_calls_per_minute": 30,
                        "max_calls_per_hour": 500,
                    },
                },
            ],
        },
        {
            "agent_id": "data-validator-v1",
            "agent_name": "Schema Validation Agent",
            "owner": "data-engineering-team",
            "description": "Validates data against schemas and business rules",
            "capabilities": [
                {
                    "name": "validate_schema",
                    "description": "Validates data structure against JSON schema",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "data": {"type": "object"},
                            "schema": {"type": "object"},
                        },
                        "required": ["data", "schema"],
                    },
                    "output_schema": {
                        "type": "object",
                        "properties": {
                            "is_valid": {"type": "boolean"},
                            "errors": {"type": "array"},
                            "warnings": {"type": "array"},
                        },
                    },
                    "estimated_latency_ms": 100,
                    "cost_per_call": 0.001,
                    "requires_approval": False,
                    "tags": ["validation", "schema", "data-quality"],
                },
            ],
            "policies": [
                {
                    "policy_type": "rate_limit",
                    "name": "High-Volume Validation",
                    "description": "Supports batch validation",
                    "constraints": {
                        "max_calls_per_minute": 5000,
                        "max_batch_size": 1000,
                    },
                },
            ],
        },
        {
            "agent_id": "report-generator-v1",
            "agent_name": "Business Report Generator",
            "owner": "analytics-team",
            "description": "Generates formatted reports from data and templates",
            "capabilities": [
                {
                    "name": "generate_report",
                    "description": "Creates formatted report from data",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "data_source": {"type": "string"},
                            "template_id": {"type": "string"},
                            "parameters": {"type": "object"},
                            "format": {"type": "string", "enum": ["pdf", "html", "markdown"]},
                        },
                        "required": ["data_source", "template_id"],
                    },
                    "output_schema": {
                        "type": "object",
                        "properties": {
                            "report_url": {"type": "string"},
                            "page_count": {"type": "integer"},
                            "generated_at": {"type": "string", "format": "date-time"},
                        },
                    },
                    "estimated_latency_ms": 15000,
                    "cost_per_call": 0.02,
                    "requires_approval": False,
                    "tags": ["reporting", "documents", "analytics"],
                },
            ],
            "policies": [
                {
                    "policy_type": "rate_limit",
                    "name": "Report Generation Limit",
                    "description": "Limits concurrent report generation",
                    "constraints": {
                        "max_calls_per_minute": 10,
                        "max_concurrent": 5,
                    },
                },
            ],
        },
        {
            "agent_id": "anomaly-detector-v1",
            "agent_name": "Time-Series Anomaly Detector",
            "owner": "monitoring-team",
            "description": "Detects anomalies in time-series data using statistical methods",
            "capabilities": [
                {
                    "name": "detect_anomalies",
                    "description": "Identifies anomalies in time-series data",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "series_id": {"type": "string"},
                            "data_points": {"type": "array"},
                            "sensitivity": {"type": "number", "minimum": 0, "maximum": 1},
                        },
                        "required": ["data_points"],
                    },
                    "output_schema": {
                        "type": "object",
                        "properties": {
                            "anomalies": {"type": "array"},
                            "baseline": {"type": "object"},
                            "confidence": {"type": "number"},
                        },
                    },
                    "estimated_latency_ms": 200,
                    "cost_per_call": 0.002,
                    "requires_approval": False,
                    "tags": ["monitoring", "anomaly", "time-series"],
                },
            ],
            "policies": [
                {
                    "policy_type": "rate_limit",
                    "name": "Streaming Rate Limit",
                    "description": "Supports streaming data analysis",
                    "constraints": {
                        "max_calls_per_minute": 3000,
                        "max_points_per_call": 10000,
                    },
                },
            ],
        },
        {
            "agent_id": "sentiment-analyzer-v1",
            "agent_name": "Customer Sentiment Analyzer",
            "owner": "customer-success-team",
            "description": "Analyzes sentiment in customer feedback and communications",
            "capabilities": [
                {
                    "name": "analyze_sentiment",
                    "description": "Determines sentiment polarity of text",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "text": {"type": "string"},
                            "language": {"type": "string", "default": "en"},
                        },
                        "required": ["text"],
                    },
                    "output_schema": {
                        "type": "object",
                        "properties": {
                            "sentiment": {"type": "string", "enum": ["positive", "negative", "neutral"]},
                            "confidence": {"type": "number"},
                            "aspects": {"type": "array"},
                        },
                    },
                    "estimated_latency_ms": 150,
                    "cost_per_call": 0.003,
                    "requires_approval": False,
                    "tags": ["nlp", "sentiment", "customer"],
                },
            ],
            "policies": [
                {
                    "policy_type": "rate_limit",
                    "name": "NLP Rate Limit",
                    "description": "Standard NLP processing limit",
                    "constraints": {
                        "max_calls_per_minute": 500,
                        "max_text_length": 10000,
                    },
                },
            ],
        },
        {
            "agent_id": "recommendation-engine-v1",
            "agent_name": "Product Recommendation Engine",
            "owner": "personalization-team",
            "description": "Generates personalized product recommendations using collaborative filtering",
            "capabilities": [
                {
                    "name": "get_recommendations",
                    "description": "Returns personalized product recommendations",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "user_id": {"type": "string"},
                            "context": {"type": "object"},
                            "count": {"type": "integer", "default": 10},
                            "exclude_purchased": {"type": "boolean", "default": True},
                        },
                        "required": ["user_id"],
                    },
                    "output_schema": {
                        "type": "object",
                        "properties": {
                            "recommendations": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "product_id": {"type": "string"},
                                        "score": {"type": "number"},
                                        "reason": {"type": "string"},
                                    },
                                },
                            },
                            "model_version": {"type": "string"},
                        },
                    },
                    "estimated_latency_ms": 50,
                    "cost_per_call": 0.001,
                    "requires_approval": False,
                    "tags": ["recommendations", "personalization", "ml"],
                },
            ],
            "policies": [
                {
                    "policy_type": "rate_limit",
                    "name": "Real-time Recommendation Limit",
                    "description": "Supports real-time recommendation requests",
                    "constraints": {
                        "max_calls_per_minute": 10000,
                        "p99_latency_ms": 100,
                    },
                },
                {
                    "policy_type": "data_access",
                    "name": "User Data Access",
                    "description": "Controls access to user behavior data",
                    "constraints": {
                        "allowed_data_sources": ["user_behavior_db", "product_catalog"],
                        "pii_handling_mode": "anonymize",
                    },
                },
            ],
        },
    ]

    def generate(self, count: int = 10) -> list[dict[str, Any]]:
        """Generate agent metadata records.

        Args:
            count: Number of agents to generate (max 10)

        Returns:
            List of AgentFacts-compatible dictionaries
        """
        agents: list[dict[str, Any]] = []
        definitions = self.AGENT_DEFINITIONS[:count]

        for defn in definitions:
            agent = self._create_agent_facts(defn)
            agents.append(agent)

        return agents

    def _create_agent_facts(self, definition: dict[str, Any]) -> dict[str, Any]:
        """Create a complete AgentFacts record from definition.

        Args:
            definition: Agent definition dictionary

        Returns:
            Complete AgentFacts-compatible dictionary
        """
        # Generate timestamps
        created_at = self.random_datetime(
            start=datetime.now(UTC) - timedelta(days=365),
            end=datetime.now(UTC) - timedelta(days=30),
        )
        updated_at = self.random_datetime(
            start=created_at,
            end=datetime.now(UTC),
        )

        # Generate version
        major = self.random_int(1, 2)
        minor = self.random_int(0, 5)
        patch = self.random_int(0, 10)
        version = f"{major}.{minor}.{patch}"

        # Build capabilities with full schema
        capabilities = []
        for cap_def in definition["capabilities"]:
            capability = {
                "name": cap_def["name"],
                "description": cap_def["description"],
                "input_schema": cap_def.get("input_schema", {}),
                "output_schema": cap_def.get("output_schema", {}),
                "estimated_latency_ms": cap_def.get("estimated_latency_ms", 1000),
                "cost_per_call": cap_def.get("cost_per_call"),
                "requires_approval": cap_def.get("requires_approval", False),
                "tags": cap_def.get("tags", []),
            }
            capabilities.append(capability)

        # Build policies with full schema
        policies = []
        for i, pol_def in enumerate(definition.get("policies", [])):
            effective_from = created_at
            effective_until = None
            if pol_def["policy_type"] == "data_access":
                # Data access policies may have expiry
                effective_until = created_at + timedelta(days=self.random_int(180, 365))

            policy = {
                "policy_id": f"{definition['agent_id']}-policy-{i + 1:03d}",
                "name": pol_def["name"],
                "description": pol_def["description"],
                "policy_type": pol_def["policy_type"],
                "constraints": pol_def["constraints"],
                "effective_from": effective_from.isoformat(),
                "effective_until": effective_until.isoformat() if effective_until else None,
                "is_active": True,
            }
            policies.append(policy)

        # Build the agent facts record
        agent_facts = {
            "agent_id": definition["agent_id"],
            "agent_name": definition["agent_name"],
            "owner": definition["owner"],
            "version": version,
            "description": definition["description"],
            "capabilities": capabilities,
            "policies": policies,
            "created_at": created_at.isoformat(),
            "updated_at": updated_at.isoformat(),
            "signature_hash": "",  # Will be computed
            "parent_agent_id": None,
            "metadata": {
                "deployment_environment": self.random_choice(["production", "staging"]),
                "model_version": self.random_choice(["gpt-4", "gpt-3.5-turbo", "claude-3-sonnet"]),
                "last_health_check": updated_at.isoformat(),
            },
        }

        # Compute signature hash
        agent_facts["signature_hash"] = self._compute_signature(agent_facts)

        return agent_facts

    def _compute_signature(self, agent_facts: dict[str, Any]) -> str:
        """Compute SHA256 signature hash for agent facts.

        Args:
            agent_facts: Agent facts dictionary (without signature_hash)

        Returns:
            SHA256 hash string
        """
        # Create copy without signature_hash for hashing
        facts_for_hash = {k: v for k, v in agent_facts.items() if k != "signature_hash"}

        # Serialize deterministically
        import json

        content = json.dumps(facts_for_hash, sort_keys=True, default=str)

        return hashlib.sha256(content.encode()).hexdigest()


def generate_agent_metadata(count: int = 10, seed: int = 42) -> list[dict[str, Any]]:
    """Generate agent metadata dataset.

    Args:
        count: Number of agents to generate
        seed: Random seed for reproducibility

    Returns:
        List of AgentFacts-compatible dictionaries
    """
    generator = AgentMetadataGenerator(seed=seed)
    return generator.generate(count)

