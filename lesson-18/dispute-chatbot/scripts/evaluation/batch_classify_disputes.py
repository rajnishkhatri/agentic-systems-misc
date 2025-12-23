import asyncio
import sys
import os
import json
import logging
import pandas as pd
from typing import List, Dict, Any
from tqdm import tqdm

# Adjust path to include the project root
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
sys.path.append(project_root)

# Import backend modules
try:
    from lesson_18.dispute_chatbot.backend.phases.classify import classify_dispute
    from lesson_18.dispute_chatbot.utils.llm_service import get_default_service
except ImportError:
    # Fallback to standard import if running from root
    try:
        from backend.phases.classify import classify_dispute
        from utils.llm_service import get_default_service
    except ImportError as e:
        print(f"Error importing modules: {e}")
        sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

INPUT_CSV_PATH = os.path.join(current_dir, "synthetic_dispute_queries.csv")
OUTPUT_CSV_PATH = os.path.join(current_dir, "classification_results.csv")

async def process_batch(queries: List[Dict[str, Any]], batch_size: int = 5):
    """Process a batch of queries concurrently."""
    results = []
    
    semaphore = asyncio.Semaphore(batch_size)
    
    async def process_single(query_row):
        async with semaphore:
            try:
                task_input = {
                    "dispute_id": query_row["id"],
                    "description": query_row["query"],
                    "current_date": "2023-10-27"
                }
                
                result = await classify_dispute(task_input)
                
                # Parse dimension tuple JSON
                dim_tuple = json.loads(query_row["dimension_tuple_json"])
                
                return {
                    "Trace_ID": query_row["id"],
                    "User_Query": query_row["query"],
                    "Expected_Reason": dim_tuple.get("DisputeReason"),
                    "Predicted_Reason": result["reason_code"],
                    "Expected_Network": dim_tuple.get("PaymentNetwork"),
                    "Predicted_Network": result["network"],
                    "Confidence": result["classification_confidence"],
                    "Reasoning": result["classification_reasoning"],
                    "Dimension_Tuple": query_row["dimension_tuple_json"]
                }
            except Exception as e:
                logger.error(f"Error processing {query_row['id']}: {e}")
                return {
                    "Trace_ID": query_row["id"],
                    "User_Query": query_row["query"],
                    "Error": str(e)
                }

    tasks = [process_single(row) for row in queries]
    
    for f in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc="Classifying Disputes"):
        result = await f
        results.append(result)
        
    return results

async def main():
    print(f"Reading queries from {INPUT_CSV_PATH}")
    try:
        df = pd.read_csv(INPUT_CSV_PATH)
    except FileNotFoundError:
        print(f"Error: Could not find {INPUT_CSV_PATH}")
        return

    queries = df.to_dict('records')
    print(f"Processing {len(queries)} queries...")
    
    results = await process_batch(queries)
    
    # Save results
    results_df = pd.DataFrame(results)
    
    # Add simple exact match columns
    results_df["Reason_Match"] = results_df.apply(
        lambda x: 1 if str(x.get("Expected_Reason")).lower() == str(x.get("Predicted_Reason")).lower() else 0, axis=1
    )
    results_df["Network_Match"] = results_df.apply(
        lambda x: 1 if str(x.get("Expected_Network")).lower() == str(x.get("Predicted_Network")).lower() else 0, axis=1
    )
    
    results_df.to_csv(OUTPUT_CSV_PATH, index=False)
    print(f"\nClassification complete. Results saved to {OUTPUT_CSV_PATH}")
    
    # Print simple stats
    print("\nInitial Analysis:")
    print(f"Total Rows: {len(results_df)}")
    if "Reason_Match" in results_df.columns:
        print(f"Reason Code Match Rate: {results_df['Reason_Match'].mean():.2%}")
    if "Network_Match" in results_df.columns:
        print(f"Network Match Rate: {results_df['Network_Match'].mean():.2%}")

if __name__ == "__main__":
    asyncio.run(main())

