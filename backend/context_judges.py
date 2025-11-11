"""
Context Quality Judges: AI-based evaluation of retrieval precision and recall

This module provides AI judges to evaluate the quality of retrieved context
in RAG systems, measuring context precision and context recall.

Classes:
- ContextPrecisionJudge: Evaluates % of retrieved chunks that are relevant
- ContextRecallJudge: Evaluates % of relevant passages that were retrieved
"""

from openai import OpenAI
import json
from typing import Any


class ContextPrecisionJudge:
    """
    AI judge to evaluate context precision: % of retrieved chunks that are relevant.

    Context Precision = (# relevant chunks in top-k) / k

    Uses GPT-4o-mini to classify each retrieved chunk as RELEVANT or IRRELEVANT.
    """

    def __init__(self, model: str = "gpt-4o-mini"):
        """
        Initialize ContextPrecisionJudge.

        Args:
            model: OpenAI model to use for judging (default: gpt-4o-mini)
        """
        self.model = model
        self.client = None  # Lazy initialization

    def evaluate(self, query: str, chunks: list[str]) -> dict[str, Any]:
        """
        Evaluate context precision for retrieved chunks.

        Args:
            query: User query
            chunks: List of retrieved text chunks

        Returns:
            dict with:
                - precision: float (0-1)
                - labels: dict mapping chunk_N to RELEVANT/IRRELEVANT

        Raises:
            TypeError: If query is not string or chunks is not list
            ValueError: If chunks list is empty
        """
        # Step 1: Type checking
        if not isinstance(query, str):
            raise TypeError("query must be a string")
        if not isinstance(chunks, list):
            raise TypeError("chunks must be a list")

        # Step 2: Input validation
        if len(chunks) == 0:
            raise ValueError("chunks list cannot be empty")

        # Step 3: Build prompt
        chunks_formatted = "\n".join([f"{i+1}. {chunk}" for i, chunk in enumerate(chunks)])

        prompt = f"""Query: {query}

Retrieved Chunks:
{chunks_formatted}

Task: For each chunk, classify as RELEVANT (contains information to answer query) or IRRELEVANT (unrelated).

Output JSON:
{{
    "chunk_1": "RELEVANT" or "IRRELEVANT",
    "chunk_2": "RELEVANT" or "IRRELEVANT",
    ...
}}"""

        # Step 4: Initialize client if needed (lazy initialization)
        if self.client is None:
            self.client = OpenAI()

        # Call LLM judge
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            response_format={"type": "json_object"},
        )

        # Step 5: Parse response and calculate precision
        labels = json.loads(response.choices[0].message.content)
        relevant_count = sum(1 for v in labels.values() if v == "RELEVANT")
        precision = relevant_count / len(chunks)

        return {"precision": precision, "labels": labels}


class ContextRecallJudge:
    """
    AI judge to evaluate context recall: % of relevant passages that were retrieved.

    Context Recall = (# relevant passages retrieved) / (# total relevant passages)

    Requires ground-truth relevant passages for comparison.
    """

    def __init__(self, model: str = "gpt-4o-mini"):
        """
        Initialize ContextRecallJudge.

        Args:
            model: OpenAI model to use for judging (default: gpt-4o-mini)
        """
        self.model = model
        self.client = None  # Lazy initialization

    def evaluate(
        self, query: str, retrieved_chunks: list[str], relevant_passages: list[str]
    ) -> dict[str, Any]:
        """
        Evaluate context recall by comparing retrieved chunks to ground truth.

        Args:
            query: User query
            retrieved_chunks: List of retrieved text chunks
            relevant_passages: Ground-truth relevant passages (manual annotation)

        Returns:
            dict with:
                - recall: float (0-1)
                - covered_passages: list of passage numbers that were retrieved

        Raises:
            TypeError: If inputs are not correct types
            ValueError: If lists are empty
        """
        # Step 1: Type checking
        if not isinstance(query, str):
            raise TypeError("query must be a string")
        if not isinstance(retrieved_chunks, list):
            raise TypeError("retrieved_chunks must be a list")
        if not isinstance(relevant_passages, list):
            raise TypeError("relevant_passages must be a list")

        # Step 2: Input validation
        if len(retrieved_chunks) == 0:
            raise ValueError("retrieved_chunks list cannot be empty")
        if len(relevant_passages) == 0:
            raise ValueError("relevant_passages list cannot be empty")

        # Step 3: Build prompt
        retrieved_formatted = "\n".join(
            [f"{i+1}. {chunk}" for i, chunk in enumerate(retrieved_chunks)]
        )
        relevant_formatted = "\n".join(
            [f"{i+1}. {passage}" for i, passage in enumerate(relevant_passages)]
        )

        prompt = f"""Query: {query}

Retrieved Chunks:
{retrieved_formatted}

Ground-Truth Relevant Passages:
{relevant_formatted}

Task: Count how many of the ground-truth relevant passages are covered by the retrieved chunks (exact or paraphrased).

Output JSON:
{{
    "covered_passages": [list of passage numbers],
    "recall": <number of covered passages> / <total relevant passages>
}}"""

        # Step 4: Initialize client if needed (lazy initialization)
        if self.client is None:
            self.client = OpenAI()

        # Call LLM judge
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            response_format={"type": "json_object"},
        )

        # Step 5: Parse response and normalize recall value
        result = json.loads(response.choices[0].message.content)

        # Handle recall as string fraction (e.g., "1/2", "1 / 2") or float
        recall_value = result.get("recall")
        if isinstance(recall_value, str):
            # Parse string fraction like "1/2" or "1 / 2"
            parts = recall_value.replace(" ", "").split("/")
            if len(parts) == 2:
                numerator = float(parts[0])
                denominator = float(parts[1])
                result["recall"] = numerator / denominator if denominator > 0 else 0.0
            else:
                # Try to parse as float string
                result["recall"] = float(recall_value)
        elif isinstance(recall_value, (int, float)):
            result["recall"] = float(recall_value)
        else:
            # Default to 0.0 if unable to parse
            result["recall"] = 0.0

        return result
