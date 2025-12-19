import pickle
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import numpy as np
import torch
from sentence_transformers import SentenceTransformer, util

logger = logging.getLogger(__name__)

class RagRetriever:
    """
    Retrieves similar historical disputes using vector similarity search.
    """
    
    def __init__(self, vector_store_path: Optional[str] = None):
        """
        Initialize the retriever.
        
        Args:
            vector_store_path: Path to the pickled vector store. 
                               If None, defaults to backend/data/vector_store.pkl
        """
        if vector_store_path is None:
            # Default path relative to project root (assuming this runs from project root or similar)
            # We try to find the backend/data/vector_store.pkl
            base_path = Path(__file__).resolve().parent.parent.parent
            vector_store_path = base_path / "backend" / "data" / "vector_store.pkl"
            
        self.vector_store_path = Path(vector_store_path)
        self.embeddings = None
        self.metadata = None
        self.model = None
        self.model_name = "all-MiniLM-L6-v2" # Default
        
        self._load_vector_store()
        self._load_model()
        
    def _load_vector_store(self):
        """Load the vector store from disk."""
        if not self.vector_store_path.exists():
            logger.error(f"Vector store not found at {self.vector_store_path}")
            raise FileNotFoundError(f"Vector store not found at {self.vector_store_path}")
            
        try:
            with open(self.vector_store_path, "rb") as f:
                data = pickle.load(f)
                
            self.embeddings = data.get("embeddings")
            self.metadata = data.get("metadata")
            self.model_name = data.get("model_name", self.model_name)
            
            logger.info(f"Loaded vector store with {len(self.metadata)} items.")
        except Exception as e:
            logger.error(f"Failed to load vector store: {e}")
            raise
            
    def _load_model(self):
        """Load the sentence transformer model."""
        try:
            logger.info(f"Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise

    def retrieve_similar(self, query: str, k: int = 3, threshold: float = 0.0) -> List[Dict[str, Any]]:
        """
        Retrieve k most similar disputes for the given query.
        
        Args:
            query: The dispute description text.
            k: Number of results to return.
            threshold: Minimum similarity score (0.0 to 1.0).
            
        Returns:
            List of dictionaries containing metadata and similarity score.
        """
        if not query:
            return []
            
        # Encode query
        query_embedding = self.model.encode(query, convert_to_tensor=True)
        
        # Ensure embeddings are on the same device as the query embedding
        if not isinstance(self.embeddings, torch.Tensor):
            self.embeddings = torch.tensor(self.embeddings)
            
        if self.embeddings.device != query_embedding.device:
            self.embeddings = self.embeddings.to(query_embedding.device)
            
        # Compute cosine similarities
        # util.cos_sim returns a tensor of shape (1, N)
        scores = util.cos_sim(query_embedding, self.embeddings)[0]
        
        # Find top k
        # torch.topk returns (values, indices)
        # We can use torch.topk for efficiency if N is large, but sorting is fine for small N
        top_scores, top_indices = torch.topk(scores, k=min(k, len(scores)))
        
        # Convert to list
        top_scores = top_scores.cpu().tolist()
        top_indices = top_indices.cpu().tolist()
        
        results = []
        for score, idx in zip(top_scores, top_indices):
            if score < threshold:
                continue
                
            item = self.metadata[idx].copy()
            item["similarity_score"] = score
            results.append(item)
            
        return results

if __name__ == "__main__":
    # Simple test
    logging.basicConfig(level=logging.INFO)
    try:
        retriever = RagRetriever()
        query = "I didn't authorize this transaction"
        results = retriever.retrieve_similar(query, k=2)
        print(f"Query: {query}")
        for res in results:
            print(f"Match ({res['similarity_score']:.3f}): {res['description'][:100]}...")
    except Exception as e:
        print(f"Error: {e}")

