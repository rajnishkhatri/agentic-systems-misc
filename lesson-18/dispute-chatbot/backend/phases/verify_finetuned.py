"""Verify Fine-Tuned Model.

This script evaluates the fine-tuned model against the test set.
It calculates accuracy and logs full prediction traces for analysis.
"""

import os
import json
import logging
import asyncio
from pathlib import Path
from typing import Dict, Any, List
import sys

# Load environment variables from .env if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

# Add parent directory to path to import utils
sys.path.append(str(Path(__file__).parent.parent.parent))

from openai import AsyncOpenAI
from utils.prompt_service import render_prompt
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "phases" / "distillation_data"
TEST_FILE = DATA_DIR / "distillation_test.json"
SUBMISSION_LOG = DATA_DIR / "finetuning_submission_log.json"
EVAL_LOG = DATA_DIR / "student_evaluation_log.jsonl"

def extract_json_from_text(content: str) -> Dict[str, Any]:
    """Extract JSON from a response that may include markdown code fences."""
    json_str = content or ""
    if "```json" in json_str:
        json_str = json_str.split("```json", 1)[1].split("```", 1)[0].strip()
    elif "```" in json_str:
        json_str = json_str.split("```", 1)[1].split("```", 1)[0].strip()
    return json.loads(json_str)


def extract_category_and_reasoning(parsed: Dict[str, Any], fallback_raw: str) -> (str, str):
    """Support both legacy {category, reasoning} and v5 ToT schema."""
    category = parsed.get("category") if isinstance(parsed, dict) else None
    if not category:
        category = "PARSE_ERROR"

    # Legacy
    if isinstance(parsed, dict) and isinstance(parsed.get("reasoning"), str):
        return category, parsed["reasoning"]

    # v5 ToT schema (best-effort)
    if isinstance(parsed, dict):
        synthesis = parsed.get("synthesis") if isinstance(parsed.get("synthesis"), dict) else {}
        if isinstance(synthesis.get("reasoning"), str):
            return category, synthesis["reasoning"]
        if isinstance(parsed.get("confidence_rationale"), str):
            return category, parsed["confidence_rationale"]

    return category, fallback_raw


async def verify_model():
    """Run verification on the test set."""
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error("OPENAI_API_KEY environment variable not set.")
        return

    client = AsyncOpenAI(api_key=api_key)

    # 1. Get Model ID
    if not SUBMISSION_LOG.exists():
        logger.error(f"Submission log not found at {SUBMISSION_LOG}")
        return

    model_id = None
    with open(SUBMISSION_LOG, 'r', encoding='utf-8') as f:
        try:
            logs = json.load(f)
            if isinstance(logs, list) and logs:
                # Use the most recent job
                last_job = logs[-1]
                job_id = last_job.get("job_id")
                
                # Check job status to get the fine_tuned_model name
                # (The log only has the job ID initially, we need to fetch the job to get the model name if it's done)
                # However, for this script, we assume the user provides it or we try to fetch it.
                logger.info(f"Checking status for job {job_id}...")
                job = await client.fine_tuning.jobs.retrieve(job_id)
                
                if job.status == "succeeded":
                    model_id = job.fine_tuned_model
                    logger.info(f"Using fine-tuned model: {model_id}")
                else:
                    logger.warning(f"Job {job_id} status is {job.status}. It might not be ready.")
                    # Fallback to base model for demonstration or exit?
                    # The plan says "Once the model is ready..."
                    # We will exit if not ready.
                    logger.error("Model not ready yet. Please wait for fine-tuning to complete.")
                    return
        except Exception as e:
            logger.error(f"Failed to read submission log: {e}")
            return

    if not model_id:
        logger.error("No fine-tuned model ID found.")
        return

    # 2. Load Test Data
    if not TEST_FILE.exists():
        logger.error(f"Test file not found at {TEST_FILE}")
        return

    with open(TEST_FILE, 'r', encoding='utf-8') as f:
        test_examples = json.load(f)

    logger.info(f"Starting evaluation on {len(test_examples)} examples...")

    # Clear eval log
    with open(EVAL_LOG, 'w', encoding='utf-8') as f:
        pass

    correct_count = 0
    total_count = 0

    for example in test_examples:
        dispute_id = example.get('dispute_id')
        description = example.get('description')
        true_category = example.get('category')
        
        # Prepare input
        input_prompt = render_prompt("DisputeClassifier_identify_category_v5_tot.j2", description=description)

        try:
            # Call Fine-Tuned Model
            # The format we trained on was:
            # System: You are a helpful assistant...
            # User: input_prompt
            
            response = await client.chat.completions.create(
                model=model_id,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that classifies disputes."},
                    {"role": "user", "content": input_prompt}
                ],
                temperature=0.0 # Deterministic
            )
            
            content = response.choices[0].message.content
            
            # Parse output
            try:
                pred_data = extract_json_from_text(content)
                pred_category, reasoning = extract_category_and_reasoning(pred_data, content)
            except Exception:
                pred_data = {}
                pred_category = "PARSE_ERROR"
                reasoning = content

            # Evaluate
            is_correct = (pred_category == true_category)
            if is_correct:
                correct_count += 1
            total_count += 1

            # Log
            log_entry = {
                "dispute_id": dispute_id,
                "ground_truth": true_category,
                "predicted": pred_category,
                "is_correct": is_correct,
                "reasoning": reasoning,
                "full_response": content
            }
            
            with open(EVAL_LOG, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + "\n")

            if total_count % 10 == 0:
                print(f"Processed {total_count}/{len(test_examples)} - Current Accuracy: {correct_count/total_count:.2%}")

        except Exception as e:
            logger.error(f"Error processing {dispute_id}: {e}")

    accuracy = correct_count / total_count if total_count > 0 else 0
    logger.info(f"Evaluation Complete.")
    logger.info(f"Final Accuracy: {accuracy:.2%} ({correct_count}/{total_count})")
    logger.info(f"Detailed logs saved to {EVAL_LOG}")

if __name__ == "__main__":
    asyncio.run(verify_model())

