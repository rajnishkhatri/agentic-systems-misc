import json
import pickle
import os
import sys
from pathlib import Path
from sentence_transformers import SentenceTransformer
import numpy as np

# Setup paths
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
GOLDEN_SET_PATH = PROJECT_ROOT / "synthetic_data/phase1/golden_set/natural_language_classification_v2.json"
OUTPUT_PATH = PROJECT_ROOT / "backend/data/vector_store.pkl"

def load_data(path: Path):
    """Load the golden set JSON."""
    if not path.exists():
        raise FileNotFoundError(f"Golden set not found at {path}")
    
    with open(path, "r") as f:
        data = json.load(f)
    print(f"Loaded {len(data)} items from golden set.")
    return data

def build_vector_store():
    """Build and save the vector store."""
    print("Initializing embedding model (all-MiniLM-L6-v2)...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    data = load_data(GOLDEN_SET_PATH)
    
    # Extract texts
    descriptions = [item["description"] for item in data]
    
    print("Generating embeddings...")
    embeddings = model.encode(descriptions, show_progress_bar=True)
    
    # Structure the artifact
    vector_store = {
        "embeddings": embeddings,
        "metadata": data,  # store full item as metadata
        "model_name": "all-MiniLM-L6-v2"
    }
    
    print(f"Saving vector store to {OUTPUT_PATH}...")
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    with open(OUTPUT_PATH, "wb") as f:
        pickle.dump(vector_store, f)
        
    print("Done!")

if __name__ == "__main__":
    build_vector_store()


