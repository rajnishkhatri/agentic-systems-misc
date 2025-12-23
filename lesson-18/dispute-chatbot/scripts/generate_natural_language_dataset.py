import asyncio
import csv
import json
import logging
import os
import sys
from pathlib import Path
from typing import List, Dict, Any

from pydantic import BaseModel, Field

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(ROOT_DIR))

from utils.llm_service import get_default_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CATALOG_PATH = ROOT_DIR / "lesson-18/dispute-schema/reason_codes_catalog.csv"
OUTPUT_PATH = ROOT_DIR / "lesson-18/dispute-chatbot/synthetic_data/phase1/golden_set/natural_language_classification.json"

class DisputeVariations(BaseModel):
    """Container for different persona-based dispute descriptions."""
    emotional: str = Field(description="Short, angry, urgent, possibly with typos")
    narrative: str = Field(description="Long, detailed, storytelling style, burying the lead")
    ambiguous: str = Field(description="Vague, implicit, missing standard keywords")

async def generate_variations(network: str, code: str, category: str, description: str) -> DisputeVariations:
    """Generate 3 variations of a dispute description using LLM."""
    service = get_default_service()
    
    prompt = f"""
    You are a customer simulating a credit card dispute.
    
    Context:
    - Network: {network}
    - Reason Code: {code}
    - Standard Description: {description}
    - Category: {category}
    
    Task: Generate 3 distinct user complaints mapping to this dispute type.
    
    1. Emotional/Urgent: Short (<20 words), angry, demands action, may contain typos or caps.
    2. Narrative: Long (>40 words), conversational, includes irrelevant details (e.g., about their day), polite but confused.
    3. Ambiguous: Vague, does NOT use standard keywords like 'fraud', 'subscription', or 'not received'. Implies the issue through context.
    
    Ensure the "Ambiguous" case is tricky but still logically maps to this specific reason code.
    """
    
    try:
        return await service.complete_structured(
            messages=[{"role": "user", "content": prompt}],
            response_model=DisputeVariations,
            model="gpt-4o" # Use high quality model for generation
        )
    except Exception as e:
        logger.error(f"Failed to generate variations for {code}: {e}")
        # Return fallback if LLM fails
        return DisputeVariations(
            emotional=f"Fix this NOW! {description}",
            narrative=f"I was just looking at my statement and I noticed {description} and I'm not sure what to do.",
            ambiguous=f"Something is wrong with this charge."
        )

async def main():
    if not CATALOG_PATH.exists():
        logger.error(f"Catalog not found at {CATALOG_PATH}")
        return

    # Read catalog
    rows = []
    with open(CATALOG_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('reason_code') and row.get('Network'):
                rows.append(row)

    logger.info(f"Loaded {len(rows)} reason codes from catalog.")
    
    # Generate variations
    test_cases = []
    sem = asyncio.Semaphore(5) # Limit concurrency
    
    async def process_row(row):
        async with sem:
            network = row['Network']
            code = row['reason_code']
            category = row['unified_category']
            desc = row['description']
            
            logger.info(f"Generating for {network} - {code}...")
            variations = await generate_variations(network, code, category, desc)
            
            # Create 3 test cases from the variations
            base_case = {
                "true_reason_code": code,
                "network": network.lower(),
                "category": category,
                "is_fraud": category == "fraudulent",
            }
            
            # 1. Emotional
            test_cases.append({
                **base_case,
                "dispute_id": f"gen_{network}_{code}_emotional",
                "description": variations.emotional,
                "variation_type": "emotional",
                "expected_confidence": 0.85 # High confidence expected even if angry
            })
            
            # 2. Narrative
            test_cases.append({
                **base_case,
                "dispute_id": f"gen_{network}_{code}_narrative",
                "description": variations.narrative,
                "variation_type": "narrative",
                "expected_confidence": 0.80 # Slightly lower due to noise
            })
            
            # 3. Ambiguous
            test_cases.append({
                **base_case,
                "dispute_id": f"gen_{network}_{code}_ambiguous",
                "description": variations.ambiguous,
                "variation_type": "ambiguous",
                "expected_confidence": 0.60 # Lower confidence expected
            })

    # Run in batches to avoid rate limits
    tasks = [process_row(row) for row in rows]
    # For testing purposes, let's limit to first 10 rows if needed, but for full set:
    # tasks = [process_row(row) for row in rows[:5]] # Uncomment to test with subset
    
    await asyncio.gather(*tasks)
    
    # Save output
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(test_cases, f, indent=2)
        
    logger.info(f"Successfully generated {len(test_cases)} natural language test cases.")
    logger.info(f"Saved to: {OUTPUT_PATH}")

if __name__ == "__main__":
    asyncio.run(main())


