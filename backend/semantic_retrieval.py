"""
Semantic Retrieval: Embeddings, Vector Search, and Hybrid Search

This module provides functions for semantic search using embeddings and
hybrid search combining BM25 with semantic retrieval.

Key Functions:
- generate_embeddings: Create embeddings from text using OpenAI API
- build_vector_index: Build FAISS index for fast similarity search
- semantic_search: Find k nearest neighbors in vector space
- hybrid_search: Combine BM25 and semantic search with weighted scoring
- reciprocal_rank_fusion: Merge rankings using RRF algorithm

Implementation follows defensive programming with:
- Type hints for all parameters and return values
- Input validation (type checking, range validation)
- Comprehensive error messages
- Normalized embeddings for cosine similarity
"""

import numpy as np
import faiss
from openai import OpenAI
from typing import Any


def generate_embeddings(
    texts: list[str], model: str = "text-embedding-3-small"
) -> np.ndarray:
    """
    Generate embeddings for list of texts using OpenAI API.

    Args:
        texts: List of text strings to embed
        model: OpenAI embedding model name (default: text-embedding-3-small)

    Returns:
        numpy array of shape (len(texts), embedding_dim)

    Raises:
        TypeError: If texts is not a list
        ValueError: If texts list is empty
    """
    # Step 1: Type checking
    if not isinstance(texts, list):
        raise TypeError("texts must be a list")

    # Step 2: Input validation
    if len(texts) == 0:
        raise ValueError("texts list cannot be empty")

    # Step 3: Generate embeddings via OpenAI API
    client = OpenAI()
    response = client.embeddings.create(model=model, input=texts)

    # Step 4: Convert to numpy array
    embeddings = np.array([e.embedding for e in response.data])

    # Step 5: Return
    return embeddings


def build_vector_index(embeddings: np.ndarray, method: str = "faiss") -> faiss.Index:
    """
    Build FAISS vector index from embeddings.

    Args:
        embeddings: numpy array of shape (n_docs, embedding_dim)
        method: Index method (default: "faiss", uses IndexFlatIP)

    Returns:
        FAISS index ready for similarity search

    Raises:
        TypeError: If embeddings is not a numpy array
        ValueError: If embeddings array is empty
    """
    # Step 1: Type checking
    if not isinstance(embeddings, np.ndarray):
        raise TypeError("embeddings must be a numpy array")

    # Step 2: Input validation
    if embeddings.shape[0] == 0:
        raise ValueError("embeddings array cannot be empty")

    # Step 3: Normalize embeddings for cosine similarity
    embeddings_normalized = embeddings.astype("float32")
    faiss.normalize_L2(embeddings_normalized)

    # Step 4: Build FAISS index (Inner Product = cosine after normalization)
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings_normalized)

    # Step 5: Return
    return index


def semantic_search(
    query_embedding: np.ndarray, index: faiss.Index, k: int = 5
) -> list[tuple[int, float]]:
    """
    Search vector index for k nearest neighbors to query.

    Args:
        query_embedding: Query embedding vector
        index: FAISS index to search
        k: Number of top results to return

    Returns:
        List of (doc_index, similarity_score) tuples sorted by score descending

    Raises:
        TypeError: If query_embedding is not a numpy array
        ValueError: If k exceeds number of indexed vectors
    """
    # Step 1: Type checking
    if not isinstance(query_embedding, np.ndarray):
        raise TypeError("query_embedding must be a numpy array")

    # Step 2: Input validation
    if k > index.ntotal:
        raise ValueError("k cannot exceed number of indexed vectors")

    # Step 3: Normalize query embedding
    query_normalized = query_embedding.astype("float32").reshape(1, -1)
    faiss.normalize_L2(query_normalized)

    # Step 4: Search index
    distances, indices = index.search(query_normalized, k)

    # Step 5: Return as list of (index, score) tuples
    results = [(int(idx), float(score)) for idx, score in zip(indices[0], distances[0])]
    return results


def hybrid_search(
    query: str,
    bm25_index: Any,
    vector_index: faiss.Index,
    alpha: float = 0.5,
    k: int = 10,
) -> list[int]:
    """
    Hybrid search combining BM25 and semantic search.

    Args:
        query: Query string
        bm25_index: BM25Okapi index from rank_bm25
        vector_index: FAISS vector index
        alpha: Weight for BM25 (1-alpha for semantic), range [0, 1]
        k: Number of top results to return

    Returns:
        List of document indices sorted by hybrid score

    Raises:
        TypeError: If alpha is not a float
        ValueError: If alpha is not in [0, 1]
    """
    # Step 1: Type checking
    if not isinstance(alpha, (float, int)):
        raise TypeError("alpha must be a float")
    alpha = float(alpha)

    # Step 2: Input validation
    if not 0 <= alpha <= 1:
        raise ValueError("alpha must be between 0 and 1")

    # Step 3: Get BM25 scores
    tokenized_query = query.lower().split()
    bm25_scores = bm25_index.get_scores(tokenized_query)

    # Normalize BM25 scores to 0-1
    max_bm25 = bm25_scores.max() if bm25_scores.max() > 0 else 1
    bm25_scores_norm = bm25_scores / max_bm25

    # Step 4: Get semantic scores
    query_embedding = generate_embeddings([query])[0]
    semantic_results = semantic_search(query_embedding, vector_index, k=len(bm25_scores))

    # Create semantic scores array
    semantic_scores = np.zeros(len(bm25_scores))
    for idx, score in semantic_results:
        semantic_scores[idx] = score

    # Step 5: Combine scores
    hybrid_scores = alpha * bm25_scores_norm + (1 - alpha) * semantic_scores

    # Sort by hybrid score and return top-k
    ranked_indices = np.argsort(hybrid_scores)[::-1]
    return ranked_indices[:k].tolist()


def reciprocal_rank_fusion(
    rankings: list[list[tuple[int, float]]], k: int = 60
) -> list[int]:
    """
    Merge multiple ranked lists using Reciprocal Rank Fusion (RRF).

    RRF formula: score(d) = Σ 1 / (k + rank(d))
    where rank is 0-indexed position in each ranking.

    Args:
        rankings: List of ranked results, each as [(doc_id, score), ...]
        k: Constant for RRF formula (default: 60 from literature)

    Returns:
        Merged document IDs sorted by RRF score descending

    Raises:
        TypeError: If rankings is not a list
        ValueError: If rankings list is empty
    """
    # Step 1: Type checking
    if not isinstance(rankings, list):
        raise TypeError("rankings must be a list")

    # Step 2: Input validation
    if len(rankings) == 0:
        raise ValueError("rankings list cannot be empty")

    # Step 3: Calculate RRF scores
    rrf_scores: dict[int, float] = {}

    for ranking in rankings:
        for rank, (doc_id, _) in enumerate(ranking):
            if doc_id not in rrf_scores:
                rrf_scores[doc_id] = 0.0
            rrf_scores[doc_id] += 1 / (k + rank + 1)

    # Step 4: Sort by RRF score descending
    sorted_docs = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)

    # Step 5: Return document IDs
    return [doc_id for doc_id, score in sorted_docs]
