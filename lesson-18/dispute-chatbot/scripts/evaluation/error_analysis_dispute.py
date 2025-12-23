import asyncio
import pandas as pd
import json
import sys
import os
from tqdm import tqdm
from datetime import datetime

# Adjust path to include the project root
current_dir = os.path.dirname(os.path.abspath(__file__))
# Navigate up to 'lesson-18/dispute-chatbot'
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(project_root)

# Import backend modules
try:
    from backend.phases.classify import classify_dispute
    from utils.llm_service import get_default_service
except ImportError as e:
    print(f"Error importing modules: {e}")
    # Debug info
    print(f"Sys path: {sys.path}")
    sys.exit(1)

INPUT_CSV = os.path.join(current_dir, "synthetic_dispute_queries.csv")
OUTPUT_CSV = os.path.join(current_dir, "error_analysis_results.csv")

async def process_query(row):
    """Process a single query through the classification phase."""
    query_id = row['id']
    query_text = row['query']
    
    task_input = {
        "dispute_id": f"trace_{query_id}",
        "description": query_text,
        "current_date": "2023-10-27"
    }
    
    trace_summary = ""
    result_json = {}
    
    try:
        result = await classify_dispute(task_input)
        result_json = result
        trace_summary = f"Classified as: Reason={result.get('reason_code')}, Network={result.get('network')}. Confidence={result.get('classification_confidence')}. Reasoning: {result.get('classification_reasoning')}"
    except Exception as e:
        trace_summary = f"Error: {str(e)}"
    
    # Parse dimension tuple to check for expected values (rough check)
    dims = json.loads(row['dimension_tuple_json'])
    
    # Initialize failure modes (0 by default)
    failures = {
        "Failure_Mode_Network_Bias": 0,
        "Failure_Mode_Reason_Code_Granularity": 0,
        "Failure_Mode_Ambiguity_Misclassification": 0,
        "Failure_Mode_Contextual_Blindness": 0
    }
    
    # Simple heuristic checks for failure modes (can be refined manually later)
    # 1. Network Bias: If input mentions a network but output is different (usually defaulting to Visa)
    input_network = dims.get('PaymentNetwork', '').lower()
    output_network = result_json.get('network', '').lower()
    if input_network in ['mastercard', 'amex', 'discover'] and output_network == 'visa':
        failures["Failure_Mode_Network_Bias"] = 1
        
    # 2. Reason Code Granularity: If reason is subscription/duplicate but code is 13.1 (merchandise not received)
    input_reason = dims.get('DisputeReason', '').lower()
    output_code = result_json.get('reason_code', '')
    
    if input_reason == 'subscription_canceled' and output_code == '13.1':
        failures["Failure_Mode_Reason_Code_Granularity"] = 1
    elif input_reason == 'duplicate' and output_code == '13.1':
        failures["Failure_Mode_Reason_Code_Granularity"] = 1
    elif input_reason == 'product_unacceptable' and output_code == '13.1': # Should be 13.3
        failures["Failure_Mode_Reason_Code_Granularity"] = 1

    return {
        "Trace_ID": f"TRACE_{query_id}",
        "User_Query": query_text,
        "Dimension_Tuple_JSON": row['dimension_tuple_json'],
        "Full_Bot_Trace_Summary": trace_summary,
        "Open_Code_Notes": "", # To be filled manually
        **failures,
        "Actual_Reason_Code": output_code,
        "Actual_Network": output_network
    }

async def main():
    if not os.path.exists(INPUT_CSV):
        print(f"Input file not found: {INPUT_CSV}")
        return

    df = pd.read_csv(INPUT_CSV)
    print(f"Processing {len(df)} queries...")
    
    results = []
    # Process in batches to avoid rate limits if needed, but for local/mock it's fine
    # Using semaphore in classify.py helps, but here we run sequentially or small batches
    
    for _, row in tqdm(df.iterrows(), total=len(df)):
        result_row = await process_query(row)
        results.append(result_row)
        
    results_df = pd.DataFrame(results)
    results_df.to_csv(OUTPUT_CSV, index=False)
    print(f"Results saved to {OUTPUT_CSV}")

if __name__ == "__main__":
    asyncio.run(main())

