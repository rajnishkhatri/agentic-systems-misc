import asyncio
import csv
import logging
import json
import sys
import os
# Disable LLM caching to avoid missing dependency errors
os.environ["LLM_CACHE_TYPE"] = "disabled"

from typing import List, Dict, Any, Tuple
from pathlib import Path
from pydantic import BaseModel, Field

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from utils.llm_service import get_default_service
from utils.prompt_service import render_prompt

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CategoryResultV4(BaseModel):
    """Structured output for category identification V4."""
    analysis: str = Field(description="Step-by-step reasoning")
    category: str = Field(description="Selected standardized category")

async def _identify_category_v4_trace(description: str) -> Tuple[CategoryResultV4, Dict[str, Any]]:
    """Step 2: Identify the unified category using LLM with v4 prompt (traced)."""
    service = get_default_service()
    prompt = render_prompt(
        "DisputeClassifier_identify_category_v4.j2",
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
            
        result = CategoryResultV4.model_validate_json(content)
    except Exception as e:
        logger.error(f"Failed to parse category result: {e}")
        # Attempt to handle partial json or other issues if needed, or just fail
        raise ValueError(f"Failed to parse output: {content}") from e

    trace = {
        "step": "identify_category_v4",
        "prompt": prompt,
        "llm_response": completion.content,
        "parsed_output": result.model_dump(),
        "model": service.routing_model
    }

    return result, trace

async def evaluate_v4_trace():
    # Load results
    results_path = project_root / "qualitative" / "phase1" / "natural_language_results.csv"
    output_json_path = project_root / "qualitative" / "phase1" / "natural_language_trace_results_v4.json"
    
    failures = []
    try:
        with open(results_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['status'] == 'FAIL':
                    failures.append(row)
    except FileNotFoundError:
        logger.error(f"Could not find results file at {results_path}")
        return

    # Select first 50 failures
    selected_cases = failures[:50]
    trace_results = []
    
    print(f"Testing {len(selected_cases)} failed cases with V4 prompt and capturing traces...\n")
    
    for i, case in enumerate(selected_cases):
        description = case['description']
        expected = case['expected_category']
        
        try:
            result, trace = await _identify_category_v4_trace(description)
            v4_prediction = result.category
            
            is_pass = v4_prediction == expected
            status = "PASS" if is_pass else "FAIL"
            
            trace_entry = {
                "case": case,
                "result": {
                    "category": v4_prediction,
                    "reasoning": result.analysis  # Mapping analysis to reasoning for report compatibility
                },
                "trace": {
                    "steps": [trace]
                },
                "status": status
            }
            trace_results.append(trace_entry)
            
            print(f"[{i+1}/{len(selected_cases)}] {case['dispute_id']}: {status} (Exp: {expected}, Got: {v4_prediction})")
            
        except Exception as e:
            print(f"Error processing {case['dispute_id']}: {e}")

    # Save to JSON
    with open(output_json_path, 'w') as f:
        json.dump(trace_results, f, indent=2)
    
    # Calculate stats
    passed = sum(1 for r in trace_results if r['status'] == 'PASS')
    total = len(trace_results)
    print(f"\nEvaluation Complete.")
    print(f"Fixed: {passed}/{total} ({passed/total*100:.1f}%)")
    print(f"Trace results saved to {output_json_path}")

if __name__ == "__main__":
    asyncio.run(evaluate_v4_trace())

