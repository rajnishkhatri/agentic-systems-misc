"""Agent implementations for dispute resolution.

This module contains:
- dispute.py: Pydantic models (Dispute, Evidence, Submission)
- dispute_classifier.py: Routes disputes by reason code (like task_assigner.py)
- evidence_specialists.py: ABC + Factory + Enum pattern (like generic_writer_agent.py)
- judge_panel.py: Parallel judge execution (like reviewer_panel.py)
"""
