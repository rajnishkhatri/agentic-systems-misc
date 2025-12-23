"""Horizontal services for dispute chatbot.

This module contains:
- llms.py: Model configuration (adapted from composable_app)
- prompt_service.py: Jinja2 template renderer (reused from composable_app)
- guardrails.py: PCI/PII validation (extends composable_app pattern)
- explainability.py: BlackBox, AgentFacts, PhaseLogger wrappers (from lesson-17)
- save_for_eval.py: Evaluation data collection (reused pattern)
"""
