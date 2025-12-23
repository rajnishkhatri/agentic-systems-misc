import asyncio
import csv
import logging
import json
import sys
import os
from typing import List, Dict, Any, Tuple
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from utils.llm_service import get_default_service
from utils.prompt_service import render_prompt
from backend.phases.classify_v2 import CategoryResult

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def _identify_category_v3_trace(description: str) -> Tuple[CategoryResult, Dict[str, Any]]:
    """Step 2: Identify the unified category using LLM with v3 prompt (traced)."""
    service = get_default_service()
    prompt = render_prompt(
        "DisputeClassifier_identify_category_v3.j2",
        description=description
    )

    # Use complete() to get raw response for tracing
    completion = await service.complete(
        messages=[{"role": "user", "content": prompt}],
        model=service.routing_model,
        temperature=0.0
    )
    
    # Parse manually
    try:
        content = completion.content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()
            
        result = CategoryResult.model_validate_json(content)
    except Exception as e:
        logger.error(f"Failed to parse category result: {e}")
        raise ValueError(f"Failed to parse output: {content}") from e

    trace = {
        "step": "identify_category",
        "prompt": prompt,
        "llm_response": completion.content,
        "parsed_output": result.model_dump(),
        "model": service.routing_model
    }

    return result, trace

async def evaluate_v3_fix_trace():
    # Load results
    results_path = project_root / "qualitative" / "phase1" / "natural_language_results.csv"
    output_json_path = project_root / "qualitative" / "phase1" / "natural_language_trace_results_v3_fix.json"
    
    failures = []
    with open(results_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if (row['status'] == 'FAIL' and 
                row['expected_category'] == 'general' and 
                row['actual_category'] in ['fraudulent', 'unrecognized']):
                failures.append(row)
    
    selected_cases = failures[:20]
    trace_results = []
    
    print(f"Testing {len(selected_cases)} cases with V3 prompt and capturing traces...\n")
    
    for case in selected_cases:
        description = case['description']
        expected = case['expected_category']
        
        try:
            result, trace = await _identify_category_v3_trace(description)
            v3_prediction = result.category
            
            is_pass = v3_prediction == expected
            status = "PASS" if is_pass else "FAIL"
            
            trace_entry = {
                "case": case,
                "result": {
                    "category": v3_prediction,
                    "reasoning": result.reasoning
                },
                "trace": {
                    "steps": [trace]
                },
                "status": status
            }
            trace_results.append(trace_entry)
            
            print(f"Processed {case['dispute_id']}: {status}")
            
        except Exception as e:
            print(f"Error processing {case['dispute_id']}: {e}")

    # Save to JSON
    with open(output_json_path, 'w') as f:
        json.dump(trace_results, f, indent=2)
    
    print(f"\nTrace results saved to {output_json_path}")

if __name__ == "__main__":
    asyncio.run(evaluate_v3_fix_trace())

