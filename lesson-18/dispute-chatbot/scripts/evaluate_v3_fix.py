import asyncio
import csv
import logging
from typing import List, Dict, Any
from pathlib import Path
import sys
import os

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from utils.llm_service import get_default_service
from utils.prompt_service import render_prompt
from backend.phases.classify_v2 import CategoryResult

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def _identify_category_v3(description: str) -> CategoryResult:
    """Step 2: Identify the unified category using LLM with v3 prompt."""
    service = get_default_service()
    prompt = render_prompt(
        "DisputeClassifier_identify_category_v3.j2",
        description=description
    )

    return await service.complete_structured(
        messages=[{"role": "user", "content": prompt}],
        response_model=CategoryResult,
        model=service.routing_model,
        temperature=0.0
    )

async def evaluate_v3_fix():
    # Load results
    results_path = project_root / "qualitative" / "phase1" / "natural_language_results.csv"
    
    failures = []
    with open(results_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Focus on failures where expected was general but got fraudulent or unrecognized
            if (row['status'] == 'FAIL' and 
                row['expected_category'] == 'general' and 
                row['actual_category'] in ['fraudulent', 'unrecognized']):
                failures.append(row)
    
    # Select up to 20 cases
    selected_cases = failures[:20]
    
    print(f"Found {len(failures)} matching failures. Testing {len(selected_cases)} cases with V3 prompt...\n")
    print(f"{'ID':<25} | {'Description (truncated)':<50} | {'Expected':<10} | {'V2 Actual':<12} | {'V3 Prediction':<12} | {'Result':<10}")
    print("-" * 130)
    
    passed_count = 0
    
    for case in selected_cases:
        description = case['description']
        v2_actual = case['actual_category']
        expected = case['expected_category']
        
        try:
            result = await _identify_category_v3(description)
            v3_prediction = result.category
            
            is_pass = v3_prediction == expected
            if is_pass:
                passed_count += 1
            
            result_str = "PASS" if is_pass else "FAIL"
            
            # Truncate description for display
            desc_display = (description[:47] + "...") if len(description) > 50 else description
            
            print(f"{case['dispute_id']:<25} | {desc_display:<50} | {expected:<10} | {v2_actual:<12} | {v3_prediction:<12} | {result_str:<10}")
            
        except Exception as e:
            print(f"Error processing {case['dispute_id']}: {e}")

    print("-" * 130)
    print(f"\nResults: {passed_count}/{len(selected_cases)} ({passed_count/len(selected_cases)*100:.1f}%) corrected.")

if __name__ == "__main__":
    asyncio.run(evaluate_v3_fix())

