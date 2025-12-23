"""Dispute Chatbot - AI-powered merchant dispute resolution assistant.

This package provides an intelligent chatbot for guiding merchants through
the Visa dispute resolution process, including evidence gathering,
validation, and submission.

Architecture follows composable_app patterns:
- agents/: Core agent implementations (classifier, specialists)
- orchestrators/: State machine workflow management
- phases/: Phase handlers (classify, gather, validate, submit, monitor)
- judges/: LLM judge implementations for quality assurance
- utils/: Horizontal services (prompts, guardrails, explainability)
- chainlit/: UI components and visualization
- adapters/: Network protocol adapters (Visa VROL)
- schemas/: Pydantic domain models
"""

__version__ = "0.1.0"
