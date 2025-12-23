"""LLM judge implementations for dispute validation.

This module contains:
- base_judge.py: Abstract base judge class
- evidence_quality.py: Quality judge (0.8 threshold, blocking)
- fabrication_detection.py: Fabrication judge (0.95 threshold, blocking)
- dispute_validity.py: Validity judge (0.7 threshold, non-blocking)
- judge_panel.py: Panel orchestrator for parallel execution (like reviewer_panel.py)
"""
