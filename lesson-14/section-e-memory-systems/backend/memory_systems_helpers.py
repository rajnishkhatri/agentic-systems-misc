"""
Helper functions for memory_systems_implementation.ipynb

These functions will be imported and used in the Jupyter notebook.
Following defensive coding principles: type hints, input validation, error handling.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import tiktoken


def validate_execution_mode(mode: str, raise_on_invalid: bool = False) -> bool:
    """Validate that execution mode is DEMO or FULL.

    Args:
        mode: Execution mode string to validate
        raise_on_invalid: If True, raise ValueError on invalid mode

    Returns:
        True if mode is valid, False otherwise

    Raises:
        ValueError: If raise_on_invalid=True and mode is invalid
    """
    # Step 1: Type checking
    if not isinstance(mode, str):
        raise TypeError("mode must be a string")

    # Step 2: Validation
    valid_modes = {"DEMO", "FULL"}
    is_valid = mode in valid_modes

    # Step 3: Error handling
    if not is_valid and raise_on_invalid:
        raise ValueError(f"EXECUTION_MODE must be 'DEMO' or 'FULL', got '{mode}'")

    # Step 4: Return
    return is_valid


def calculate_mmr_score(
    relevance: float,
    max_redundancy: float,
    lambda_param: float,
) -> float:
    """Calculate Maximum Marginal Relevance (MMR) score.

    MMR = (1 - λ) * relevance - λ * max_redundancy

    Where λ=0 gives pure relevance, λ=1 gives pure diversity.

    Args:
        relevance: Relevance score in [0, 1]
        max_redundancy: Maximum redundancy with already selected docs in [0, 1]
        lambda_param: Trade-off parameter in [0, 1] (0=pure relevance, 1=pure diversity)

    Returns:
        MMR score (higher is better)

    Raises:
        TypeError: If inputs are not numeric
        ValueError: If lambda_param not in [0, 1] or scores not in [0, 1]
    """
    # Step 1: Type checking
    if not all(isinstance(x, (int, float)) for x in [relevance, max_redundancy, lambda_param]):
        raise TypeError("All inputs must be numeric")

    # Step 2: Input validation
    if not 0 <= lambda_param <= 1:
        raise ValueError(f"lambda_param must be in range [0, 1], got {lambda_param}")
    if not 0 <= relevance <= 1:
        raise ValueError(f"relevance must be in range [0, 1], got {relevance}")
    if not 0 <= max_redundancy <= 1:
        raise ValueError(f"max_redundancy must be in range [0, 1], got {max_redundancy}")

    # Step 3: Main logic - MMR formula
    # When lambda=0: pure relevance (1.0 * relevance - 0.0 * redundancy = relevance)
    # When lambda=1: pure diversity (0.0 * relevance - 1.0 * redundancy = -redundancy)
    mmr = (1 - lambda_param) * relevance - lambda_param * max_redundancy

    # Step 4: Return
    return mmr


def select_documents_mmr(
    query_embedding: list[float],
    doc_embeddings: list[list[float]],
    k: int,
    lambda_param: float,
) -> list[int]:
    """Select top-k documents using Maximum Marginal Relevance.

    Args:
        query_embedding: Query embedding vector
        doc_embeddings: List of document embedding vectors
        k: Number of documents to select
        lambda_param: MMR trade-off parameter in [0, 1]

    Returns:
        List of selected document indices

    Raises:
        TypeError: If inputs have wrong types
        ValueError: If k > num_documents or documents empty
    """
    # Step 1: Type checking
    if not isinstance(query_embedding, list):
        raise TypeError("query_embedding must be a list")
    if not isinstance(doc_embeddings, list):
        raise TypeError("doc_embeddings must be a list")
    if not isinstance(k, int):
        raise TypeError("k must be an integer")

    # Step 2: Input validation
    if len(doc_embeddings) == 0:
        raise ValueError("documents cannot be empty")
    if k > len(doc_embeddings):
        raise ValueError(f"k cannot exceed number of documents ({k} > {len(doc_embeddings)})")
    if k <= 0:
        raise ValueError("k must be positive")

    # Step 3: Main logic - MMR selection
    query_vec = np.array(query_embedding)
    doc_vecs = np.array(doc_embeddings)

    # Calculate relevance scores (cosine similarity)
    relevance_scores = np.dot(doc_vecs, query_vec) / (
        np.linalg.norm(doc_vecs, axis=1) * np.linalg.norm(query_vec)
    )

    selected_indices = []
    selected_vecs = []

    for _ in range(k):
        mmr_scores = []

        for idx in range(len(doc_embeddings)):
            if idx in selected_indices:
                mmr_scores.append(-float("inf"))  # Skip already selected
                continue

            relevance = relevance_scores[idx]

            # Calculate max redundancy with selected docs
            if len(selected_vecs) == 0:
                max_redundancy = 0.0
            else:
                selected_array = np.array(selected_vecs)
                doc_vec = doc_vecs[idx]
                redundancies = np.dot(selected_array, doc_vec) / (
                    np.linalg.norm(selected_array, axis=1) * np.linalg.norm(doc_vec)
                )
                max_redundancy = np.max(redundancies)

            mmr = calculate_mmr_score(float(relevance), float(max_redundancy), lambda_param)
            mmr_scores.append(mmr)

        # Select document with highest MMR
        best_idx = int(np.argmax(mmr_scores))
        selected_indices.append(best_idx)
        selected_vecs.append(doc_embeddings[best_idx])

    # Step 4: Return
    return selected_indices


def count_tokens(text: str, encoding_name: str = "cl100k_base") -> int:
    """Count tokens in text using tiktoken.

    Args:
        text: Input text to tokenize
        encoding_name: Tiktoken encoding name (default: cl100k_base for GPT-4)

    Returns:
        Number of tokens

    Raises:
        TypeError: If text is not a string
    """
    # Step 1: Type checking
    if not isinstance(text, str):
        raise TypeError("text must be a string")

    # Step 2: Edge case - empty string
    if len(text) == 0:
        return 0

    # Step 3: Main logic
    encoding = tiktoken.get_encoding(encoding_name)
    tokens = encoding.encode(text)

    # Step 4: Return
    return len(tokens)


def trim_conversation_history(
    messages: list[dict[str, str]],
    max_tokens: int,
) -> list[dict[str, str]]:
    """Trim conversation history to fit within max_tokens budget.

    Uses FIFO (First In, First Out) strategy - removes oldest messages first.

    Args:
        messages: List of message dicts with 'role' and 'content' keys
        max_tokens: Maximum total tokens allowed

    Returns:
        Trimmed message list (most recent messages preserved)

    Raises:
        TypeError: If inputs have wrong types
        ValueError: If max_tokens negative or messages empty
    """
    # Step 1: Type checking
    if not isinstance(messages, list):
        raise TypeError("messages must be a list")
    if not isinstance(max_tokens, int):
        raise TypeError("max_tokens must be an integer")

    # Step 2: Input validation
    if len(messages) == 0:
        raise ValueError("messages cannot be empty")
    if max_tokens <= 0:
        raise ValueError("max_tokens must be positive")

    # Step 3: Main logic - FIFO trimming
    trimmed = []
    total_tokens = 0

    # Start from most recent and work backwards
    for msg in reversed(messages):
        msg_tokens = count_tokens(msg["content"])
        if total_tokens + msg_tokens <= max_tokens:
            trimmed.insert(0, msg)  # Insert at beginning to maintain order
            total_tokens += msg_tokens
        else:
            break  # Exceeded budget

    # Step 4: Return
    return trimmed


def simulate_summarization(
    messages: list[dict[str, str]],
    compression_ratio: float,
) -> tuple[dict[str, str], int, int]:
    """Simulate conversation summarization with compression.

    Args:
        messages: List of message dicts to summarize
        compression_ratio: Target compression ratio in (0, 1) (e.g., 0.5 = 50% of original)

    Returns:
        Tuple of (summary_message, original_tokens, summary_tokens)

    Raises:
        TypeError: If inputs have wrong types
        ValueError: If compression_ratio not in (0, 1) or messages empty
    """
    # Step 1: Type checking
    if not isinstance(messages, list):
        raise TypeError("messages must be a list")
    if not isinstance(compression_ratio, (int, float)):
        raise TypeError("compression_ratio must be numeric")

    # Step 2: Input validation
    if len(messages) == 0:
        raise ValueError("messages cannot be empty")
    if not 0 < compression_ratio < 1:
        raise ValueError(f"compression_ratio must be in range (0, 1), got {compression_ratio}")

    # Step 3: Main logic
    # Calculate original tokens
    original_tokens = sum(count_tokens(msg["content"]) for msg in messages)

    # Calculate target summary tokens
    target_tokens = int(original_tokens * compression_ratio)

    # Create mock summary with approximately target tokens
    # Use a repeating pattern to reach target length
    base_content = f"[Summary of {len(messages)} messages] "

    # Estimate words needed (roughly 0.75 tokens per word)
    words_needed = int(target_tokens / 0.75)
    padding = " ".join(["summary"] * words_needed)
    summary_content = base_content + padding

    # Trim or extend to match target tokens more closely
    actual_tokens = count_tokens(summary_content)
    while actual_tokens > target_tokens and len(summary_content) > len(base_content):
        # Remove words from the end
        summary_content = " ".join(summary_content.split()[:-1])
        actual_tokens = count_tokens(summary_content)

    while actual_tokens < target_tokens - 2:  # Allow 2 token tolerance
        summary_content += " summary"
        actual_tokens = count_tokens(summary_content)

    summary_message = {
        "role": "system",
        "content": summary_content,
    }

    # Step 4: Return
    return summary_message, original_tokens, actual_tokens


def calculate_search_o1_overhead(
    search_tokens: int,
    retrieval_tokens: int,
    condensation_tokens: int,
    baseline_tokens: int | None = None,
) -> dict[str, Any]:
    """Calculate Search-o1 pattern overhead metrics.

    Args:
        search_tokens: Tokens used for search queries
        retrieval_tokens: Tokens used for retrieved documents
        condensation_tokens: Tokens used in Reason-in-Documents condensation
        baseline_tokens: Optional baseline tokens for comparison

    Returns:
        Dict with overhead metrics (total_overhead, overhead_percentage, etc.)

    Raises:
        ValueError: If any token count is negative
    """
    # Step 1: Type checking
    if not all(isinstance(x, int) for x in [search_tokens, retrieval_tokens, condensation_tokens]):
        raise TypeError("Token counts must be integers")

    # Step 2: Input validation
    if any(x < 0 for x in [search_tokens, retrieval_tokens, condensation_tokens]):
        raise ValueError("Token counts must be non-negative")
    if baseline_tokens is not None and baseline_tokens < 0:
        raise ValueError("baseline_tokens must be non-negative")

    # Step 3: Main logic
    total_overhead = search_tokens + retrieval_tokens + condensation_tokens

    metrics = {
        "search_tokens": search_tokens,
        "retrieval_tokens": retrieval_tokens,
        "condensation_tokens": condensation_tokens,
        "total_overhead": total_overhead,
    }

    if baseline_tokens is not None and baseline_tokens > 0:
        overhead_pct = (total_overhead / baseline_tokens) * 100
        metrics["overhead_percentage"] = overhead_pct

    # Step 4: Return
    return metrics


def calculate_compression_roi(
    original_tokens: int,
    compressed_tokens: int,
    cost_per_1k_tokens: float,
) -> dict[str, float]:
    """Calculate ROI for context compression.

    Args:
        original_tokens: Original token count before compression
        compressed_tokens: Token count after compression
        cost_per_1k_tokens: API cost per 1000 tokens (e.g., $0.03)

    Returns:
        Dict with ROI metrics (original_cost, compressed_cost, cost_savings, compression_ratio)

    Raises:
        ValueError: If compressed_tokens > original_tokens or negative values
    """
    # Step 1: Type checking
    if not isinstance(original_tokens, int) or not isinstance(compressed_tokens, int):
        raise TypeError("Token counts must be integers")
    if not isinstance(cost_per_1k_tokens, (int, float)):
        raise TypeError("cost_per_1k_tokens must be numeric")

    # Step 2: Input validation
    if original_tokens < 0 or compressed_tokens < 0:
        raise ValueError("Token counts must be non-negative")
    if compressed_tokens > original_tokens:
        raise ValueError("compressed_tokens cannot exceed original_tokens")
    if cost_per_1k_tokens < 0:
        raise ValueError("cost_per_1k_tokens must be non-negative")

    # Step 3: Main logic
    original_cost = (original_tokens / 1000) * cost_per_1k_tokens
    compressed_cost = (compressed_tokens / 1000) * cost_per_1k_tokens
    cost_savings = original_cost - compressed_cost
    compression_ratio = compressed_tokens / original_tokens if original_tokens > 0 else 0.0

    # Step 4: Return
    return {
        "original_cost": original_cost,
        "compressed_cost": compressed_cost,
        "cost_savings": cost_savings,
        "compression_ratio": compression_ratio,
    }


def export_results_json(
    output_path: Path,
    summary_statistics: dict[str, dict[str, float]],
    radar_chart_data: dict[str, list],
    detailed_results: list[dict[str, Any]],
    execution_mode: str,
) -> None:
    """Export evaluation results to JSON matching dashboard schema.

    Args:
        output_path: Path to output JSON file
        summary_statistics: Dict of metric_name -> {mean, std}
        radar_chart_data: Dict with 'labels' and 'values' keys
        detailed_results: List of per-test result dicts
        execution_mode: Either 'DEMO' or 'FULL'

    Raises:
        ValueError: If summary_statistics missing mean/std or invalid structure
        OSError: If output path cannot be written
    """
    # Step 1: Type checking
    if not isinstance(output_path, Path):
        raise TypeError("output_path must be a Path object")
    if not isinstance(summary_statistics, dict):
        raise TypeError("summary_statistics must be a dict")
    if not isinstance(radar_chart_data, dict):
        raise TypeError("radar_chart_data must be a dict")
    if not isinstance(detailed_results, list):
        raise TypeError("detailed_results must be a list")
    if not isinstance(execution_mode, str):
        raise TypeError("execution_mode must be a string")

    # Step 2: Input validation
    validate_execution_mode(execution_mode, raise_on_invalid=True)

    # Validate summary_statistics structure
    for metric_name, stats in summary_statistics.items():
        if not isinstance(stats, dict):
            raise ValueError(f"summary_statistics['{metric_name}'] must be a dict")
        if "mean" not in stats or "std" not in stats:
            raise ValueError(
                f"summary_statistics['{metric_name}'] must contain 'mean' and 'std' keys"
            )

    # Validate radar_chart_data structure
    if "labels" not in radar_chart_data or "values" not in radar_chart_data:
        raise ValueError("radar_chart_data must contain 'labels' and 'values' keys")

    # Step 3: Main logic - Build JSON structure
    output_data = {
        "version": "1.0",
        "created": datetime.now().strftime("%Y-%m-%d"),
        "execution_mode": execution_mode,
        "num_trajectories": len(detailed_results),
        "summary_statistics": summary_statistics,
        "radar_chart_data": radar_chart_data,
        "detailed_results": detailed_results,
    }

    # Step 4: Write to file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(output_data, f, indent=2)
