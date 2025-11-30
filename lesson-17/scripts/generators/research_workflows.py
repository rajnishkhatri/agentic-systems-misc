"""Research Workflow Artifacts Generator for PhaseLogger demonstrations.

Generates 10 research workflow artifacts following the PhaseLogger schema:
- Phases: PLANNING, LITERATURE_REVIEW, DATA_COLLECTION, EXPERIMENT, VALIDATION, REPORTING
- Decisions with alternatives, rationale, and confidence scores
- Artifacts with metadata (size, format, location)
- Mix of success (7) and failure (3) outcomes

Each workflow simulates a realistic research paper generation process.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from . import BaseGenerator


class ResearchWorkflowsGenerator(BaseGenerator):
    """Generator for research workflow artifacts.

    Creates realistic research workflows for PhaseLogger demonstrations.
    """

    # Research topics for variety
    RESEARCH_TOPICS = [
        "Agent reliability in multi-step workflows",
        "LLM scaling laws and emergent abilities",
        "RAG optimization for domain-specific knowledge",
        "Multi-agent coordination protocols",
        "Explainability in autonomous systems",
        "Prompt engineering best practices",
        "Fine-tuning strategies for specialized tasks",
        "Knowledge graph augmented LLMs",
        "Hallucination detection and mitigation",
        "Cost-effective inference optimization",
    ]

    # Model options for decisions
    MODEL_OPTIONS = [
        ("GPT-4", "Highest accuracy, highest cost"),
        ("GPT-3.5-Turbo", "Good balance of cost and performance"),
        ("Claude Sonnet", "Best for long-context tasks"),
        ("Claude Opus", "Highest reasoning capability"),
        ("Gemini Pro", "Good multimodal capabilities"),
        ("Llama 3", "Best open-source option"),
    ]

    # Database options for literature review
    DATABASE_OPTIONS = [
        "PubMed",
        "ArXiv",
        "Semantic Scholar",
        "Google Scholar",
        "IEEE Xplore",
        "ACM Digital Library",
    ]

    # Artifact types
    ARTIFACT_TYPES = {
        "planning": [
            ("Research proposal", "document", "md", 15),
            ("Methodology outline", "document", "md", 8),
        ],
        "literature_review": [
            ("Literature review summary", "document", "md", 125),
            ("Citation database", "data", "json", 45),
            ("Key findings matrix", "data", "csv", 12),
        ],
        "data_collection": [
            ("Raw dataset", "data", "parquet", 1024),
            ("Data dictionary", "document", "md", 5),
            ("Collection logs", "data", "json", 35),
        ],
        "experiment": [
            ("Trained model checkpoint", "model", "safetensors", 2048),
            ("Training logs", "data", "json", 250),
            ("Hyperparameter config", "config", "yaml", 2),
        ],
        "validation": [
            ("Evaluation results", "data", "json", 85),
            ("Confusion matrix", "visualization", "png", 150),
            ("ROC curves", "visualization", "png", 120),
        ],
        "reporting": [
            ("Final paper draft", "document", "md", 180),
            ("Figures and tables", "visualization", "zip", 450),
            ("Supplementary materials", "document", "pdf", 320),
        ],
    }

    # Error scenarios for failed workflows
    ERROR_SCENARIOS = [
        {
            "phase": "experiment",
            "error": "CUDA out of memory: tried to allocate 20.00 GiB",
            "is_recoverable": False,
            "reason": "Model training crashed due to insufficient GPU memory",
        },
        {
            "phase": "data_collection",
            "error": "API rate limit exceeded (429 Too Many Requests)",
            "is_recoverable": True,
            "reason": "Data collection interrupted by API throttling",
        },
        {
            "phase": "validation",
            "error": "Validation accuracy below threshold (0.65 < 0.70)",
            "is_recoverable": False,
            "reason": "Model failed to meet minimum performance requirements",
        },
    ]

    def generate(self, count: int = 10) -> list[dict[str, Any]]:
        """Generate research workflow artifacts.

        Args:
            count: Number of workflows to generate (default: 10)

        Returns:
            List of research workflow dictionaries
        """
        workflows: list[dict[str, Any]] = []

        # Generate workflows with mix of success/failure
        # 7 successful, 3 failed (indices 2, 5, 8 will fail)
        fail_indices = {2, 5, 8}

        for i in range(count):
            topic = self.RESEARCH_TOPICS[i % len(self.RESEARCH_TOPICS)]
            should_fail = i in fail_indices
            error_scenario = self.random_choice(self.ERROR_SCENARIOS) if should_fail else None

            workflow = self._generate_workflow(
                workflow_id=f"research-workflow-{i + 1:03d}",
                topic=topic,
                error_scenario=error_scenario,
            )
            workflows.append(workflow)

        return workflows

    def _generate_workflow(
        self,
        workflow_id: str,
        topic: str,
        error_scenario: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Generate a single research workflow.

        Args:
            workflow_id: Unique workflow identifier
            topic: Research topic
            error_scenario: Optional error scenario for failed workflow

        Returns:
            Complete workflow dictionary
        """
        # Generate realistic start time (past 30 days)
        start_time = self.random_datetime(
            start=datetime.now(UTC) - timedelta(days=30),
            end=datetime.now(UTC) - timedelta(days=1),
        )

        # Phase sequence (standard research workflow)
        phase_sequence = [
            "planning",
            "literature_review",
            "data_collection",
            "experiment",
            "validation",
            "reporting",
        ]

        # Determine which phases complete based on error scenario
        if error_scenario:
            fail_phase = error_scenario["phase"]
            fail_index = phase_sequence.index(fail_phase)
            completed_phases = phase_sequence[: fail_index + 1]
            final_status = "failed"
        else:
            completed_phases = phase_sequence
            final_status = "completed"

        # Generate phases
        phases: list[dict[str, Any]] = []
        current_time = start_time
        total_duration_hours = 0

        for phase_name in completed_phases:
            phase_duration_hours = self._get_phase_duration(phase_name)
            phase_end_time = current_time + timedelta(hours=phase_duration_hours)

            # Determine phase outcome
            is_failed_phase = (
                error_scenario and phase_name == error_scenario["phase"]
            )
            phase_status = "failed" if is_failed_phase else "success"

            phase = {
                "phase_id": f"{workflow_id}-{phase_name}",
                "phase_type": phase_name.upper(),
                "start_time": current_time.isoformat(),
                "end_time": phase_end_time.isoformat(),
                "duration_hours": phase_duration_hours,
                "outcome": {
                    "status": phase_status,
                    "summary": self._get_phase_summary(phase_name, phase_status, topic),
                },
            }

            # Add error details if this is the failed phase
            if is_failed_phase:
                phase["outcome"]["error"] = {
                    "message": error_scenario["error"],
                    "is_recoverable": error_scenario["is_recoverable"],
                }

            phases.append(phase)

            total_duration_hours += phase_duration_hours
            current_time = phase_end_time

        # Generate decisions (2-4 per phase)
        decisions: list[dict[str, Any]] = []
        for phase in phases:
            phase_decisions = self._generate_phase_decisions(
                workflow_id, phase["phase_type"].lower(), topic
            )
            decisions.extend(phase_decisions)

        # Generate artifacts for completed successful phases
        artifacts: list[dict[str, Any]] = []
        for phase in phases:
            if phase["outcome"]["status"] == "success":
                phase_artifacts = self._generate_phase_artifacts(
                    workflow_id, phase["phase_type"].lower()
                )
                artifacts.extend(phase_artifacts)

        # Build workflow summary
        end_time = current_time if final_status == "completed" else phases[-1]["end_time"]

        workflow = {
            "workflow_id": workflow_id,
            "workflow_type": "research_paper_generation",
            "research_topic": topic,
            "start_time": start_time.isoformat(),
            "end_time": end_time if isinstance(end_time, str) else end_time.isoformat(),
            "total_duration_hours": round(total_duration_hours, 1),
            "phases": phases,
            "decisions": decisions,
            "artifacts": artifacts,
            "final_status": final_status,
            "failure_reason": error_scenario["reason"] if error_scenario else None,
            "metadata": {
                "topic_category": self._get_topic_category(topic),
                "primary_model": self.random_choice(self.MODEL_OPTIONS)[0],
                "databases_used": self.random_sample(
                    self.DATABASE_OPTIONS, k=self.random_int(2, 4)
                ),
            },
        }

        return workflow

    def _get_phase_duration(self, phase_name: str) -> float:
        """Get realistic duration for a phase in hours.

        Args:
            phase_name: Name of the phase

        Returns:
            Duration in hours
        """
        durations = {
            "planning": (4.0, 8.0),
            "literature_review": (40.0, 80.0),
            "data_collection": (20.0, 60.0),
            "experiment": (30.0, 100.0),
            "validation": (10.0, 30.0),
            "reporting": (20.0, 50.0),
        }
        min_hours, max_hours = durations.get(phase_name, (5.0, 20.0))
        return round(self.random_float(min_hours, max_hours), 1)

    def _get_phase_summary(self, phase_name: str, status: str, topic: str) -> str:
        """Generate summary text for a phase.

        Args:
            phase_name: Name of the phase
            status: Phase outcome status
            topic: Research topic

        Returns:
            Summary text
        """
        if status == "failed":
            return f"Phase failed during {phase_name.replace('_', ' ')}"

        summaries = {
            "planning": f"Research question and methodology defined for '{topic}'",
            "literature_review": f"{self.random_int(30, 60)} papers reviewed, {self.random_int(8, 15)} key findings identified",
            "data_collection": f"Collected {self.random_int(1000, 10000)} samples from {self.random_int(2, 5)} sources",
            "experiment": f"Model trained for {self.random_int(3, 10)} epochs, best accuracy: {self.random_float(0.75, 0.95):.2f}",
            "validation": f"Cross-validation completed, F1 score: {self.random_float(0.70, 0.92):.2f}",
            "reporting": "Final paper draft completed with figures and supplementary materials",
        }
        return summaries.get(phase_name, f"{phase_name} completed successfully")

    def _generate_phase_decisions(
        self, workflow_id: str, phase_name: str, topic: str
    ) -> list[dict[str, Any]]:
        """Generate decisions for a phase.

        Args:
            workflow_id: Workflow identifier
            phase_name: Name of the phase
            topic: Research topic

        Returns:
            List of decision dictionaries
        """
        decisions: list[dict[str, Any]] = []
        decision_templates = self._get_decision_templates(phase_name, topic)

        num_decisions = self.random_int(2, 4)
        selected_templates = self.random_sample(
            decision_templates, k=min(num_decisions, len(decision_templates))
        )

        for i, template in enumerate(selected_templates):
            decision = {
                "decision_id": f"{workflow_id}-{phase_name}-dec-{i + 1:02d}",
                "timestamp": datetime.now(UTC).isoformat(),  # Will be adjusted
                "phase": phase_name.upper(),
                "description": template["description"],
                "alternatives": template["alternatives"],
                "selected": template["selected"],
                "rationale": template["rationale"],
                "confidence": round(self.random_float(0.7, 0.95), 2),
            }
            decisions.append(decision)

        return decisions

    def _get_decision_templates(
        self, phase_name: str, topic: str
    ) -> list[dict[str, Any]]:
        """Get decision templates for a phase.

        Args:
            phase_name: Name of the phase
            topic: Research topic

        Returns:
            List of decision template dictionaries
        """
        templates = {
            "planning": [
                {
                    "description": "Select research question focus",
                    "alternatives": [
                        f"Focus on {topic} - theoretical foundations",
                        f"Focus on {topic} - practical applications",
                        f"Focus on {topic} - benchmark comparisons",
                    ],
                    "selected": f"Focus on {topic} - practical applications",
                    "rationale": "High industry demand, clear evaluation metrics available",
                },
                {
                    "description": "Choose research methodology",
                    "alternatives": [
                        "Experimental study with controlled trials",
                        "Observational study with existing datasets",
                        "Mixed methods combining both approaches",
                    ],
                    "selected": "Mixed methods combining both approaches",
                    "rationale": "Provides both quantitative rigor and qualitative insights",
                },
            ],
            "literature_review": [
                {
                    "description": "Select academic databases to search",
                    "alternatives": self.DATABASE_OPTIONS[:4],
                    "selected": "ArXiv, Semantic Scholar, ACM Digital Library",
                    "rationale": "Best coverage for AI/ML research topics",
                },
                {
                    "description": "Define inclusion criteria for papers",
                    "alternatives": [
                        "Last 2 years only, peer-reviewed",
                        "Last 5 years, including preprints",
                        "No time limit, highly cited only",
                    ],
                    "selected": "Last 5 years, including preprints",
                    "rationale": "Captures recent advances while maintaining relevance",
                },
            ],
            "data_collection": [
                {
                    "description": "Select data source for experiments",
                    "alternatives": [
                        "Public benchmark datasets",
                        "Synthetic data generation",
                        "Custom data collection",
                    ],
                    "selected": "Public benchmark datasets",
                    "rationale": "Enables reproducibility and comparison with prior work",
                },
                {
                    "description": "Choose data preprocessing strategy",
                    "alternatives": [
                        "Minimal preprocessing (preserve original)",
                        "Standard normalization pipeline",
                        "Custom augmentation with synthetic examples",
                    ],
                    "selected": "Standard normalization pipeline",
                    "rationale": "Balance between data quality and processing overhead",
                },
            ],
            "experiment": [
                {
                    "description": "Select primary language model",
                    "alternatives": [m[0] for m in self.MODEL_OPTIONS[:4]],
                    "selected": self.random_choice(self.MODEL_OPTIONS[:4])[0],
                    "rationale": "Best cost/performance ratio for our context window requirements",
                },
                {
                    "description": "Choose hyperparameter tuning strategy",
                    "alternatives": [
                        "Grid search with cross-validation",
                        "Bayesian optimization",
                        "Manual tuning with domain knowledge",
                    ],
                    "selected": "Bayesian optimization",
                    "rationale": "More efficient than grid search for high-dimensional spaces",
                },
                {
                    "description": "Select training batch size",
                    "alternatives": ["32", "64", "128", "256"],
                    "selected": "64",
                    "rationale": "Optimal for available GPU memory and convergence speed",
                },
            ],
            "validation": [
                {
                    "description": "Choose evaluation metrics",
                    "alternatives": [
                        "Accuracy only",
                        "F1 + Precision + Recall",
                        "Full suite (F1, AUC-ROC, confusion matrix)",
                    ],
                    "selected": "Full suite (F1, AUC-ROC, confusion matrix)",
                    "rationale": "Comprehensive evaluation for publication requirements",
                },
                {
                    "description": "Select baseline comparison models",
                    "alternatives": [
                        "State-of-the-art only",
                        "Classical ML + recent deep learning",
                        "All available baselines",
                    ],
                    "selected": "Classical ML + recent deep learning",
                    "rationale": "Shows improvement over both traditional and modern approaches",
                },
            ],
            "reporting": [
                {
                    "description": "Choose paper structure",
                    "alternatives": [
                        "Standard ML paper format",
                        "Systems paper format",
                        "Position paper format",
                    ],
                    "selected": "Standard ML paper format",
                    "rationale": "Best fit for experimental results presentation",
                },
                {
                    "description": "Select visualization style",
                    "alternatives": [
                        "Minimal (tables only)",
                        "Standard (figures + tables)",
                        "Rich (interactive + static)",
                    ],
                    "selected": "Standard (figures + tables)",
                    "rationale": "Clear communication without overwhelming complexity",
                },
            ],
        }
        return templates.get(phase_name, [])

    def _generate_phase_artifacts(
        self, workflow_id: str, phase_name: str
    ) -> list[dict[str, Any]]:
        """Generate artifacts for a phase.

        Args:
            workflow_id: Workflow identifier
            phase_name: Name of the phase

        Returns:
            List of artifact dictionaries
        """
        artifacts: list[dict[str, Any]] = []
        artifact_templates = self.ARTIFACT_TYPES.get(phase_name, [])

        for i, (name, artifact_type, fmt, size_kb) in enumerate(artifact_templates):
            # Add some randomness to size
            actual_size = size_kb + self.random_int(-size_kb // 4, size_kb // 4)
            actual_size = max(1, actual_size)

            artifact = {
                "artifact_id": f"{workflow_id}-{phase_name}-art-{i + 1:02d}",
                "artifact_type": artifact_type,
                "phase": phase_name.upper(),
                "description": name,
                "metadata": {
                    "format": fmt,
                    "size_kb": actual_size,
                },
                "location": f"artifacts/{workflow_id}/{phase_name}/{name.lower().replace(' ', '_')}.{fmt}",
                "created_at": datetime.now(UTC).isoformat(),
            }

            # Add type-specific metadata
            if artifact_type == "model":
                artifact["metadata"]["architecture"] = self.random_choice(
                    ["GPT-3.5-turbo-ft", "BERT-base", "T5-small", "DistilBERT"]
                )
                artifact["metadata"]["accuracy"] = round(self.random_float(0.75, 0.95), 2)
                artifact["metadata"]["training_epochs"] = self.random_int(3, 10)
            elif artifact_type == "data":
                artifact["metadata"]["rows"] = self.random_int(100, 10000)
                artifact["metadata"]["columns"] = self.random_int(5, 50)
            elif artifact_type == "document":
                artifact["metadata"]["word_count"] = actual_size * 150  # ~150 words per KB
                artifact["metadata"]["pages"] = actual_size // 3  # ~3KB per page

            artifacts.append(artifact)

        return artifacts

    def _get_topic_category(self, topic: str) -> str:
        """Categorize research topic.

        Args:
            topic: Research topic string

        Returns:
            Category string
        """
        if any(term in topic.lower() for term in ["agent", "multi-agent", "autonomous"]):
            return "agent_systems"
        elif any(term in topic.lower() for term in ["llm", "scaling", "prompt"]):
            return "large_language_models"
        elif any(term in topic.lower() for term in ["rag", "knowledge"]):
            return "retrieval_augmented"
        elif any(term in topic.lower() for term in ["fine-tuning", "training"]):
            return "model_training"
        else:
            return "general_ml"


def generate_research_workflows(
    count: int = 10, seed: int = 42
) -> list[dict[str, Any]]:
    """Generate research workflow dataset.

    Args:
        count: Number of workflows to generate
        seed: Random seed for reproducibility

    Returns:
        List of research workflow dictionaries
    """
    generator = ResearchWorkflowsGenerator(seed=seed)
    return generator.generate(count)

