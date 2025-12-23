"""Prepare data for distillation.

Loads the golden set, performs stratified sampling to select 100 examples
representing all categories and networks, and splits into train/test sets.
"""

import json
import logging
from pathlib import Path
import random
from typing import List, Dict, Any
import pandas as pd
from sklearn.model_selection import train_test_split

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent.parent.parent
DATA_DIR = BASE_DIR / "synthetic_data" / "phase1" / "golden_set"
OUTPUT_DIR = BASE_DIR / "backend" / "phases" / "distillation_data"
SOURCE_FILE = DATA_DIR / "natural_language_classification_v2.json"

def prepare_data():
    """Load, stratify, and save distillation data."""
    if not SOURCE_FILE.exists():
        logger.error(f"Source file not found: {SOURCE_FILE}")
        return

    logger.info(f"Loading data from {SOURCE_FILE}")
    with open(SOURCE_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    df = pd.DataFrame(data)
    logger.info(f"Loaded {len(df)} examples")

    # Create a stratification key combining network and category
    df['strat_key'] = df['network'] + "_" + df['category']

    # Filter out rare classes if any (need at least 2 for split usually, but here we want exactly 100 for train)
    # We want 100 examples for training.
    # If we have enough data, we can just sample 100.
    # However, standard train_test_split splits by percentage or absolute number.
    
    # Let's check distribution
    logger.info("Class distribution (top 10):")
    logger.info(df['strat_key'].value_counts().head(10))

    # We want exactly 100 items for the training set (distillation_train.json)
    # The rest go to distillation_test.json
    
    # Handle rare classes that might be fewer than needed for strict stratification if sample size is small,
    # but here we have probably enough.
    
    try:
        train_df, test_df = train_test_split(
            df, 
            train_size=100, 
            stratify=df['strat_key'],
            random_state=42
        )
    except ValueError as e:
        logger.warning(f"Strict stratification failed: {e}. Falling back to random sampling with weights.")
        # Fallback: simple random sample if stratification fails due to singletons
        train_df = df.sample(n=100, random_state=42)
        test_df = df.drop(train_df.index)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    train_data = train_df.to_dict('records')
    test_data = test_df.to_dict('records')
    
    # Remove temporary column
    for item in train_data:
        item.pop('strat_key', None)
    for item in test_data:
        item.pop('strat_key', None)

    train_path = OUTPUT_DIR / "distillation_train.json"
    test_path = OUTPUT_DIR / "distillation_test.json"

    with open(train_path, 'w', encoding='utf-8') as f:
        json.dump(train_data, f, indent=2)
    
    with open(test_path, 'w', encoding='utf-8') as f:
        json.dump(test_data, f, indent=2)

    logger.info(f"Saved {len(train_data)} training examples to {train_path}")
    logger.info(f"Saved {len(test_data)} test examples to {test_path}")

if __name__ == "__main__":
    prepare_data()





