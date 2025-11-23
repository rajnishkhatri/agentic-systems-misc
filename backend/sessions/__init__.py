"""Sessions module for managing multi-turn conversations.

This module provides functionality for:
- Protected context identification
- Context compression with protection
- Session state management for Bhagavad Gita chatbot
"""

from backend.sessions.context_compressor import ContextCompressor
from backend.sessions.gita_session import GitaSession
from backend.sessions.protected_context import identify_protected_context

__all__ = ["identify_protected_context", "ContextCompressor", "GitaSession"]
