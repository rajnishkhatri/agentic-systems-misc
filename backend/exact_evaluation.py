"""
Exact evaluation methods: perplexity, exact match, fuzzy match, BLEU, semantic similarity.

This module implements evaluation metrics for LLM outputs following defensive coding principles.
All functions include type hints, input validation, and comprehensive error handling.
"""

import os
import re
import math
from typing import List, Tuple
import numpy as np
from Levenshtein import ratio as levenshtein_ratio
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from openai import OpenAI


# ============================================================================
# Perplexity and Cross-Entropy Calculations
# ============================================================================


def calculate_perplexity(cross_entropy_bits: float) -> float:
    """Calculate perplexity from cross-entropy in bits.

    Formula: Perplexity = 2^(cross-entropy)

    Args:
        cross_entropy_bits: Cross-entropy value in bits (base 2 logarithm)

    Returns:
        Perplexity value (lower is better)

    Raises:
        TypeError: If cross_entropy_bits is not a number
        ValueError: If cross_entropy_bits is negative

    Example:
        >>> calculate_perplexity(4.0)
        16.0
        >>> calculate_perplexity(4.88)  # GPT-2 Small on WikiText-2
        29.41
    """
    # Step 1: Type checking
    if not isinstance(cross_entropy_bits, (int, float)):
        raise TypeError(
            f"cross_entropy_bits must be a number, got {type(cross_entropy_bits)}"
        )

    # Step 2: Input validation
    if cross_entropy_bits < 0:
        raise ValueError(f"Cross-entropy cannot be negative, got {cross_entropy_bits}")

    # Step 3: Edge case handling (none for this function)

    # Step 4: Main logic
    perplexity = 2**cross_entropy_bits

    # Step 5: Return
    return perplexity


def calculate_cross_entropy(perplexity: float) -> float:
    """Calculate cross-entropy from perplexity.

    Formula: Cross-Entropy = log₂(perplexity)

    Args:
        perplexity: Perplexity value (must be positive)

    Returns:
        Cross-entropy in bits

    Raises:
        TypeError: If perplexity is not a number
        ValueError: If perplexity is not positive

    Example:
        >>> calculate_cross_entropy(16.0)
        4.0
        >>> calculate_cross_entropy(29.41)  # GPT-2 Small on WikiText-2
        4.88
    """
    # Step 1: Type checking
    if not isinstance(perplexity, (int, float)):
        raise TypeError(f"Perplexity must be a number, got {type(perplexity)}")

    # Step 2: Input validation
    if perplexity <= 0:
        raise ValueError(f"Perplexity must be positive, got {perplexity}")

    # Step 3: Edge case handling (none for this function)

    # Step 4: Main logic
    cross_entropy = math.log2(perplexity)

    # Step 5: Return
    return cross_entropy


# ============================================================================
# Text Normalization
# ============================================================================


def normalize_text(text: str) -> str:
    """Normalize text for comparison: lowercase, remove punctuation, collapse whitespace.

    Args:
        text: Input text string

    Returns:
        Normalized text string

    Raises:
        TypeError: If text is not a string

    Example:
        >>> normalize_text("Hello, World!")
        'hello world'
        >>> normalize_text("  Multiple   Spaces  ")
        'multiple spaces'
    """
    # Step 1: Type checking
    if not isinstance(text, str):
        raise TypeError(f"text must be a string, got {type(text)}")

    # Step 2: Input validation (none for this function)

    # Step 3: Edge case handling
    if not text or not text.strip():
        return ""

    # Step 4: Main logic
    # Convert to lowercase
    text = text.lower()

    # Remove punctuation (keep alphanumeric and whitespace)
    text = re.sub(r"[^\w\s]", "", text)

    # Collapse multiple spaces to single space
    text = re.sub(r"\s+", " ", text)

    # Strip leading/trailing whitespace
    text = text.strip()

    # Step 5: Return
    return text


# ============================================================================
# Exact Match
# ============================================================================


def exact_match(candidate: str, reference: str, normalize: bool = True) -> bool:
    """Check if candidate exactly matches reference.

    Args:
        candidate: Generated text to evaluate
        reference: Ground truth reference text
        normalize: Whether to normalize before comparison (lowercase, remove punctuation)

    Returns:
        True if strings match exactly (after normalization if enabled), False otherwise

    Raises:
        TypeError: If candidate or reference is not a string

    Example:
        >>> exact_match("Hello, World!", "hello world", normalize=True)
        True
        >>> exact_match("Hello", "hello", normalize=False)
        False
    """
    # Step 1: Type checking
    if not isinstance(candidate, str):
        raise TypeError(
            f"Both inputs must be strings, got candidate: {type(candidate)}"
        )
    if not isinstance(reference, str):
        raise TypeError(
            f"Both inputs must be strings, got reference: {type(reference)}"
        )

    # Step 2: Input validation (none additional)

    # Step 3: Edge case handling
    if not candidate and not reference:
        return True  # Both empty = match

    # Step 4: Main logic
    if normalize:
        candidate = normalize_text(candidate)
        reference = normalize_text(reference)

    # Step 5: Return
    return candidate == reference


# ============================================================================
# Fuzzy Match (Levenshtein Distance)
# ============================================================================


def fuzzy_match(
    candidate: str, reference: str, threshold: float = 0.8
) -> Tuple[bool, float]:
    """Check fuzzy match using Levenshtein similarity ratio.

    Args:
        candidate: Generated text to evaluate
        reference: Ground truth reference text
        threshold: Similarity threshold (0.0 to 1.0, default 0.8)

    Returns:
        Tuple of (matches: bool, similarity: float)
        - matches: True if similarity >= threshold
        - similarity: Levenshtein similarity ratio (0.0 to 1.0)

    Raises:
        TypeError: If candidate or reference is not a string
        ValueError: If threshold is not between 0 and 1

    Example:
        >>> fuzzy_match("tomato", "tomatoe", threshold=0.8)
        (True, 0.857)
        >>> fuzzy_match("tomato", "banana", threshold=0.8)
        (False, 0.143)
    """
    # Step 1: Type checking
    if not isinstance(candidate, str):
        raise TypeError(f"candidate must be a string, got {type(candidate)}")
    if not isinstance(reference, str):
        raise TypeError(f"reference must be a string, got {type(reference)}")
    if not isinstance(threshold, (int, float)):
        raise TypeError(f"threshold must be a number, got {type(threshold)}")

    # Step 2: Input validation
    if not (0 <= threshold <= 1):
        raise ValueError(f"Threshold must be between 0 and 1, got {threshold}")

    # Step 3: Edge case handling
    if not candidate and not reference:
        return (True, 1.0)  # Both empty = perfect match

    if not candidate or not reference:
        return (False, 0.0)  # One empty = no match

    # Step 4: Main logic
    # Normalize both strings
    candidate_norm = normalize_text(candidate)
    reference_norm = normalize_text(reference)

    # Calculate Levenshtein similarity ratio
    similarity = levenshtein_ratio(candidate_norm, reference_norm)

    # Check if similarity meets threshold
    matches = similarity >= threshold

    # Step 5: Return
    return (matches, similarity)


# ============================================================================
# BLEU Score
# ============================================================================


def bleu_score(candidate: str, reference: str) -> float:
    """Calculate BLEU score (Bilingual Evaluation Understudy) for text similarity.

    Uses BLEU-4 (up to 4-grams) with smoothing for short sequences.

    Args:
        candidate: Generated text to evaluate
        reference: Ground truth reference text

    Returns:
        BLEU score (0.0 to 1.0, higher is better)

    Raises:
        TypeError: If candidate or reference is not a string

    Example:
        >>> bleu_score("The cat sat on the mat", "The cat sat on the mat")
        1.0
        >>> bleu_score("The cat is on the mat", "The cat sat on the mat")
        0.72
    """
    # Step 1: Type checking
    if not isinstance(candidate, str):
        raise TypeError(f"candidate must be a string, got {type(candidate)}")
    if not isinstance(reference, str):
        raise TypeError(f"reference must be a string, got {type(reference)}")

    # Step 2: Input validation (none additional)

    # Step 3: Edge case handling
    if not candidate:
        return 0.0  # Empty candidate = zero BLEU

    if not reference:
        return 0.0  # Empty reference = zero BLEU

    # Step 4: Main logic
    # Normalize and tokenize
    candidate_tokens = normalize_text(candidate).split()
    reference_tokens = normalize_text(reference).split()

    # Handle case where normalization results in empty tokens
    if not candidate_tokens:
        return 0.0

    if not reference_tokens:
        return 0.0

    # Use smoothing function for short sequences (avoids zero scores)
    smoothing = SmoothingFunction().method1

    # Calculate BLEU-4 score (up to 4-grams)
    try:
        score = sentence_bleu(
            [reference_tokens],  # Reference is a list of token lists
            candidate_tokens,
            smoothing_function=smoothing,
        )
    except ZeroDivisionError:
        # Fallback for edge cases
        score = 0.0

    # Step 5: Return
    return score


# ============================================================================
# Semantic Similarity (Embeddings)
# ============================================================================


def get_embedding(text: str, model: str = "text-embedding-3-small") -> List[float]:
    """Get embedding vector from OpenAI API.

    Args:
        text: Text to embed
        model: OpenAI embedding model name

    Returns:
        Embedding vector as list of floats

    Raises:
        TypeError: If text is not a string
        ValueError: If OPENAI_API_KEY environment variable is not set
        Exception: If OpenAI API call fails

    Example:
        >>> emb = get_embedding("The cat sat on the mat")
        >>> len(emb)
        1536  # text-embedding-3-small dimension
    """
    # Step 1: Type checking
    if not isinstance(text, str):
        raise TypeError(f"text must be a string, got {type(text)}")

    # Step 2: Input validation
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable must be set")

    # Step 3: Edge case handling
    if not text.strip():
        raise ValueError("text cannot be empty")

    # Step 4: Main logic
    try:
        client = OpenAI(api_key=api_key)
        response = client.embeddings.create(input=text, model=model)
        embedding = response.data[0].embedding
    except Exception as e:
        raise Exception(f"OpenAI API call failed: {str(e)}") from e

    # Step 5: Return
    return embedding


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Calculate cosine similarity between two vectors.

    Formula: cosine_similarity(A, B) = (A · B) / (||A|| × ||B||)

    Args:
        vec1: First embedding vector
        vec2: Second embedding vector

    Returns:
        Cosine similarity (-1.0 to 1.0, higher means more similar)

    Raises:
        TypeError: If vec1 or vec2 is not a list
        ValueError: If vectors have different dimensions or are empty

    Example:
        >>> cosine_similarity([1, 0, 0], [1, 0, 0])
        1.0
        >>> cosine_similarity([1, 0, 0], [0, 1, 0])
        0.0
    """
    # Step 1: Type checking
    if not isinstance(vec1, list):
        raise TypeError(f"vec1 must be a list, got {type(vec1)}")
    if not isinstance(vec2, list):
        raise TypeError(f"vec2 must be a list, got {type(vec2)}")

    # Step 2: Input validation
    if len(vec1) == 0 or len(vec2) == 0:
        raise ValueError("Vectors cannot be empty")

    if len(vec1) != len(vec2):
        raise ValueError(
            f"Vectors must have same dimension: {len(vec1)} != {len(vec2)}"
        )

    # Step 3: Edge case handling (none additional)

    # Step 4: Main logic
    # Convert to numpy arrays for efficient computation
    v1 = np.array(vec1)
    v2 = np.array(vec2)

    # Calculate dot product
    dot_product = np.dot(v1, v2)

    # Calculate magnitudes (L2 norms)
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)

    # Avoid division by zero
    if norm1 == 0 or norm2 == 0:
        return 0.0

    # Calculate cosine similarity
    similarity = dot_product / (norm1 * norm2)

    # Step 5: Return
    return float(similarity)


def semantic_similarity(
    candidate: str, reference: str, model: str = "text-embedding-3-small"
) -> float:
    """Calculate semantic similarity using embeddings.

    Args:
        candidate: Generated text to evaluate
        reference: Ground truth reference text
        model: OpenAI embedding model name

    Returns:
        Semantic similarity (0.0 to 1.0, higher means more semantically similar)

    Raises:
        TypeError: If candidate or reference is not a string
        ValueError: If OPENAI_API_KEY is not set or texts are empty
        Exception: If OpenAI API call fails

    Example:
        >>> semantic_similarity("The cat sat", "A feline rested")
        0.87  # High similarity despite different words
        >>> semantic_similarity("The cat sat", "I like pizza")
        0.23  # Low similarity, different topics
    """
    # Step 1: Type checking
    if not isinstance(candidate, str):
        raise TypeError(f"candidate must be a string, got {type(candidate)}")
    if not isinstance(reference, str):
        raise TypeError(f"reference must be a string, got {type(reference)}")

    # Step 2: Input validation
    if not candidate.strip():
        raise ValueError("candidate cannot be empty")
    if not reference.strip():
        raise ValueError("reference cannot be empty")

    # Step 3: Edge case handling (none additional)

    # Step 4: Main logic
    # Get embeddings for both texts
    embedding1 = get_embedding(candidate, model=model)
    embedding2 = get_embedding(reference, model=model)

    # Calculate cosine similarity
    similarity = cosine_similarity(embedding1, embedding2)

    # Step 5: Return
    return similarity
