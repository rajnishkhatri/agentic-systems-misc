#!/usr/bin/env python3
"""
Build Vector Store (V8 RAG Prototype)

Loads the Golden Set (natural_language_classification_v2.json),
generates embeddings using sentence-transformers, and saves the result
to backend/data/vector_store.pkl.

Usage:
    python scripts/build_vector_store.py
"""

import sys
import os
import json
import pickle
import logging
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
MODEL_NAME = "all-MiniLM-L6-v2"
# Adjust path to match the verified location
DATA_PATH = Path("lesson-18/dispute-chatbot/synthetic_data/phase1/golden_set/natural_language_classification_v2.json")
OUTPUT_PATH = Path("backend/data/vector_store.pkl")

def load_data(path: Path) -> List[Dict[str, Any]]:
    """Load the golden set JSON data."""
    if not path.exists():
        # Fallback for running from different root
        # Try finding it relative to the script if the direct path fails
        root_dir = Path(__file__).resolve().parent.parent
        fallback_path = root_dir / "synthetic_data/phase1/golden_set/natural_language_classification_v2.json"
        if fallback_path.exists():
            path = fallback_path
        else:
            raise FileNotFoundError(f"Could not find data file at {path} or {fallback_path}")
    
    logger.info(f"Loading data from {path}")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    logger.info(f"Loaded {len(data)} items")
    return data

def build_vector_store():
    """Main execution flow."""
    try:
        # 1. Load Data
        data = load_data(DATA_PATH)
        
        # 2. Extract Descriptions
        descriptions = [item["description"] for item in data]
        logger.info(f"Extracted {len(descriptions)} descriptions for embedding")
        
        # 3. Load Model
        logger.info(f"Loading model: {MODEL_NAME}...")
        model = SentenceTransformer(MODEL_NAME)
        
        # 4. Generate Embeddings
        logger.info("Generating embeddings (this may take a moment)...")
        embeddings = model.encode(descriptions, convert_to_numpy=True, show_progress_bar=True)
        
        # 5. Verify Shape
        logger.info(f"Embeddings shape: {embeddings.shape}")
        if embeddings.shape[0] != len(data) or embeddings.shape[1] != 384:
             logger.warning(f"Unexpected shape! Expected ({len(data)}, 384), got {embeddings.shape}")

        # 6. Save Artifact
        artifact = {
            "embeddings": embeddings,
            "data": data,
            "model_name": MODEL_NAME
        }
        
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(OUTPUT_PATH, "wb") as f:
            pickle.dump(artifact, f)
            
        logger.info(f"Successfully saved vector store to {OUTPUT_PATH}")
        logger.info(f"File size: {OUTPUT_PATH.stat().st_size / 1024:.2f} KB")

    except Exception as e:
        logger.error(f"Failed to build vector store: {e}")
        sys.exit(1)

if __name__ == "__main__":
    build_vector_store()

