"""LLM model configuration for dispute-chatbot.

Adapted from composable_app/utils/llms.py for dispute resolution use case.
Uses OpenAI models via pydantic-ai for structured outputs.
"""

import os
from typing import Literal

from dotenv import load_dotenv

load_dotenv()

# Model configuration
# BEST_MODEL: High-quality reasoning for classification, judges, complex tasks
# SMALL_MODEL: Fast responses for simple tasks, evidence extraction
# EMBEDDING_MODEL: For semantic similarity in evidence matching

ModelType = Literal["best", "small", "embedding"]

# OpenAI model identifiers
BEST_MODEL = "gpt-4o"  # High-quality reasoning
SMALL_MODEL = "gpt-4o-mini"  # Fast, cost-effective
EMBEDDING_MODEL = "text-embedding-3-small"  # Embeddings

# Model selection by task type
MODEL_MAPPING = {
    "dispute_classifier": BEST_MODEL,  # Classification requires reasoning
    "evidence_specialists": SMALL_MODEL,  # Extraction is simpler
    "evidence_quality_judge": BEST_MODEL,  # Judges need high quality
    "fabrication_detection_judge": BEST_MODEL,  # Critical safety check
    "dispute_validity_judge": SMALL_MODEL,  # Advisory, non-blocking
    "default": SMALL_MODEL,
}


def get_model(task: str | None = None) -> str:
    """Get the appropriate model for a given task.

    Args:
        task: Task identifier (e.g., 'dispute_classifier', 'evidence_quality_judge')

    Returns:
        Model identifier string (e.g., 'gpt-4o')
    """
    if task is None:
        return MODEL_MAPPING["default"]
    return MODEL_MAPPING.get(task, MODEL_MAPPING["default"])


def get_api_key() -> str:
    """Get OpenAI API key from environment.

    Returns:
        API key string

    Raises:
        ValueError: If OPENAI_API_KEY not set
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")
    return api_key
