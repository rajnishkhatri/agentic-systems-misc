"""
TDD-RED Phase: Tests for semantic_retrieval.py

Following TDD workflow from CLAUDE.md:
- Write tests FIRST (RED phase)
- Tests should FAIL initially (no implementation exists yet)
- Test naming: test_should_[result]_when_[condition]
"""

from unittest.mock import Mock, patch

import numpy as np
import pytest


# Test: generate_embeddings function
def test_should_return_embeddings_array_when_given_valid_texts() -> None:
    """Test that generate_embeddings returns numpy array with correct shape."""
    from backend.semantic_retrieval import generate_embeddings

    texts = ["The Bhagavad Gita teaches dharma", "Karma yoga is selfless action"]

    with patch("backend.semantic_retrieval.OpenAI") as mock_openai:
        # Mock OpenAI response
        mock_client = Mock()
        mock_openai.return_value = mock_client

        mock_response = Mock()
        mock_response.data = [
            Mock(embedding=[0.1] * 1536),
            Mock(embedding=[0.2] * 1536),
        ]
        mock_client.embeddings.create.return_value = mock_response

        embeddings = generate_embeddings(texts)

        assert isinstance(embeddings, np.ndarray)
        assert embeddings.shape == (2, 1536)


def test_should_raise_typeerror_when_texts_is_not_list() -> None:
    """Test that generate_embeddings raises TypeError for non-list input."""
    from backend.semantic_retrieval import generate_embeddings

    with pytest.raises(TypeError, match="texts must be a list"):
        generate_embeddings("not a list")


def test_should_raise_valueerror_when_texts_list_is_empty() -> None:
    """Test that generate_embeddings raises ValueError for empty list."""
    from backend.semantic_retrieval import generate_embeddings

    with pytest.raises(ValueError, match="texts list cannot be empty"):
        generate_embeddings([])


def test_should_use_specified_model_when_model_parameter_provided() -> None:
    """Test that generate_embeddings uses specified embedding model."""
    from backend.semantic_retrieval import generate_embeddings

    texts = ["test text"]
    custom_model = "text-embedding-3-large"

    with patch("backend.semantic_retrieval.OpenAI") as mock_openai:
        mock_client = Mock()
        mock_openai.return_value = mock_client

        mock_response = Mock()
        mock_response.data = [Mock(embedding=[0.1] * 3072)]
        mock_client.embeddings.create.return_value = mock_response

        generate_embeddings(texts, model=custom_model)

        mock_client.embeddings.create.assert_called_once()
        call_kwargs = mock_client.embeddings.create.call_args[1]
        assert call_kwargs["model"] == custom_model


# Test: build_vector_index function
def test_should_return_faiss_index_when_given_valid_embeddings() -> None:
    """Test that build_vector_index creates FAISS index."""
    from backend.semantic_retrieval import build_vector_index

    embeddings = np.random.rand(10, 128).astype("float32")
    index = build_vector_index(embeddings)

    assert index is not None
    assert index.ntotal == 10  # FAISS index should contain 10 vectors


def test_should_raise_typeerror_when_embeddings_not_numpy_array() -> None:
    """Test that build_vector_index raises TypeError for non-ndarray input."""
    from backend.semantic_retrieval import build_vector_index

    with pytest.raises(TypeError, match="embeddings must be a numpy array"):
        build_vector_index([[0.1, 0.2], [0.3, 0.4]])


def test_should_raise_valueerror_when_embeddings_array_is_empty() -> None:
    """Test that build_vector_index raises ValueError for empty array."""
    from backend.semantic_retrieval import build_vector_index

    empty_array = np.array([]).reshape(0, 128).astype("float32")

    with pytest.raises(ValueError, match="embeddings array cannot be empty"):
        build_vector_index(empty_array)


def test_should_normalize_embeddings_when_building_index() -> None:
    """Test that build_vector_index normalizes embeddings for cosine similarity."""
    from backend.semantic_retrieval import build_vector_index

    embeddings = np.array([[3.0, 4.0], [1.0, 0.0]]).astype("float32")
    index = build_vector_index(embeddings)

    # After normalization, first vector should be [0.6, 0.8] (3/5, 4/5)
    reconstructed = index.reconstruct(0)
    assert np.isclose(reconstructed[0], 0.6, atol=0.01)
    assert np.isclose(reconstructed[1], 0.8, atol=0.01)


# Test: semantic_search function
def test_should_return_top_k_results_when_searching_index() -> None:
    """Test that semantic_search returns k nearest neighbors."""
    from backend.semantic_retrieval import build_vector_index, semantic_search

    embeddings = np.random.rand(20, 128).astype("float32")
    index = build_vector_index(embeddings)

    query_embedding = np.random.rand(128).astype("float32")
    results = semantic_search(query_embedding, index, k=5)

    assert len(results) == 5
    assert all(isinstance(r, tuple) for r in results)
    assert all(len(r) == 2 for r in results)  # (index, score) tuples


def test_should_raise_typeerror_when_query_embedding_not_numpy_array() -> None:
    """Test that semantic_search raises TypeError for invalid query embedding."""
    from backend.semantic_retrieval import build_vector_index, semantic_search

    embeddings = np.random.rand(10, 128).astype("float32")
    index = build_vector_index(embeddings)

    with pytest.raises(TypeError, match="query_embedding must be a numpy array"):
        semantic_search([0.1, 0.2], index, k=5)


def test_should_raise_valueerror_when_k_exceeds_index_size() -> None:
    """Test that semantic_search raises ValueError when k > index size."""
    from backend.semantic_retrieval import build_vector_index, semantic_search

    embeddings = np.random.rand(5, 128).astype("float32")
    index = build_vector_index(embeddings)
    query_embedding = np.random.rand(128).astype("float32")

    with pytest.raises(ValueError, match="k cannot exceed number of indexed vectors"):
        semantic_search(query_embedding, index, k=10)


def test_should_return_sorted_results_by_similarity_descending() -> None:
    """Test that semantic_search returns results sorted by similarity (highest first)."""
    from backend.semantic_retrieval import build_vector_index, semantic_search

    embeddings = np.random.rand(10, 128).astype("float32")
    index = build_vector_index(embeddings)
    query_embedding = np.random.rand(128).astype("float32")

    results = semantic_search(query_embedding, index, k=5)

    # Scores should be in descending order (higher similarity first)
    scores = [score for _, score in results]
    assert scores == sorted(scores, reverse=True)


# Test: hybrid_search function
def test_should_combine_bm25_and_semantic_results_when_hybrid_searching() -> None:
    """Test that hybrid_search merges BM25 and semantic results."""
    from backend.semantic_retrieval import hybrid_search

    with patch("backend.semantic_retrieval.generate_embeddings") as mock_embed:
        with patch("backend.semantic_retrieval.semantic_search") as mock_semantic:
            # Mock embeddings and semantic search
            mock_embed.return_value = np.random.rand(128).astype("float32")
            mock_semantic.return_value = [(0, 0.9), (1, 0.8), (2, 0.7)]

            # Mock BM25 index
            mock_bm25 = Mock()
            mock_bm25.get_scores.return_value = np.array([10.5, 8.3, 6.2, 4.1, 2.0])

            # Mock vector index
            mock_vector_index = Mock()

            query = "What is karma yoga?"
            results = hybrid_search(query, mock_bm25, mock_vector_index, alpha=0.5, k=3)

            assert isinstance(results, list)
            assert len(results) <= 3  # Should return top-k results


def test_should_raise_typeerror_when_alpha_not_float() -> None:
    """Test that hybrid_search raises TypeError for invalid alpha."""
    from backend.semantic_retrieval import hybrid_search

    with pytest.raises(TypeError, match="alpha must be a float"):
        hybrid_search("query", Mock(), Mock(), alpha="not_a_float")


def test_should_raise_valueerror_when_alpha_out_of_range() -> None:
    """Test that hybrid_search raises ValueError when alpha not in [0, 1]."""
    from backend.semantic_retrieval import hybrid_search

    with pytest.raises(ValueError, match="alpha must be between 0 and 1"):
        hybrid_search("query", Mock(), Mock(), alpha=1.5)


# Test: reciprocal_rank_fusion function
def test_should_merge_rankings_using_rrf_formula() -> None:
    """Test that RRF correctly merges multiple rankings."""
    from backend.semantic_retrieval import reciprocal_rank_fusion

    rankings = [
        [(5, 10.0), (2, 8.0), (8, 6.0)],  # BM25 ranking
        [(2, 0.9), (5, 0.85), (3, 0.8)],  # Semantic ranking
    ]

    results = reciprocal_rank_fusion(rankings, k=60)

    assert isinstance(results, list)
    # doc2 and doc5 appear in both rankings, should rank higher
    assert 2 in results[:2]  # doc2 should be in top 2
    assert 5 in results[:2]  # doc5 should be in top 2


def test_should_raise_typeerror_when_rankings_not_list() -> None:
    """Test that RRF raises TypeError for invalid rankings input."""
    from backend.semantic_retrieval import reciprocal_rank_fusion

    with pytest.raises(TypeError, match="rankings must be a list"):
        reciprocal_rank_fusion("not a list")


def test_should_raise_valueerror_when_rankings_list_empty() -> None:
    """Test that RRF raises ValueError for empty rankings list."""
    from backend.semantic_retrieval import reciprocal_rank_fusion

    with pytest.raises(ValueError, match="rankings list cannot be empty"):
        reciprocal_rank_fusion([])


def test_should_handle_single_ranking_list() -> None:
    """Test that RRF handles single ranking (degenerates to identity)."""
    from backend.semantic_retrieval import reciprocal_rank_fusion

    rankings = [[(5, 10.0), (2, 8.0), (8, 6.0)]]

    results = reciprocal_rank_fusion(rankings)

    assert results == [5, 2, 8]  # Should preserve original order


def test_should_use_default_k_value_60_when_not_specified() -> None:
    """Test that RRF uses k=60 by default (from literature)."""
    from backend.semantic_retrieval import reciprocal_rank_fusion

    rankings = [[(1, 10.0), (2, 8.0)], [(2, 0.9), (1, 0.8)]]

    # This test verifies the formula uses k=60
    # doc1 rank 0 in list1: 1/(60+0+1) = 1/61 = 0.01639
    # doc1 rank 1 in list2: 1/(60+1+1) = 1/62 = 0.01613
    # doc1 total: 0.01639 + 0.01613 = 0.03252
    #
    # doc2 rank 1 in list1: 1/(60+1+1) = 1/62 = 0.01613
    # doc2 rank 0 in list2: 1/(60+0+1) = 1/61 = 0.01639
    # doc2 total: 0.01613 + 0.01639 = 0.03252

    results = reciprocal_rank_fusion(rankings)

    # Both should have similar scores (order may vary due to floating point)
    assert set(results[:2]) == {1, 2}
