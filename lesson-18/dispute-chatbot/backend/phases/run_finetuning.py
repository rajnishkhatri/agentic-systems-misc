"""Submit OpenAI Fine-Tuning Job.

This script uploads the teacher-generated dataset to OpenAI and initiates a
fine-tuning job for gpt-4o-mini. It logs the submission details for tracking.
"""

import os
import json
import logging
from pathlib import Path
from datetime import datetime

# Load environment variables from .env if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

# Import OpenAI client
try:
    from openai import OpenAI
except ImportError:
    logging.error("OpenAI library not found. Please install with `pip install openai`")
    exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "phases" / "distillation_data"
DATASET_FILE = DATA_DIR / "fine_tuning_dataset.jsonl"
LOG_FILE = DATA_DIR / "finetuning_submission_log.json"

def submit_finetuning():
    """Submit the fine-tuning job."""
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error("OPENAI_API_KEY environment variable not set.")
        return

    client = OpenAI(api_key=api_key)

    if not DATASET_FILE.exists():
        logger.error(f"Dataset file not found at {DATASET_FILE}")
        return

    logger.info(f"Uploading file: {DATASET_FILE}")
    
    try:
        # 1. Upload File
        with open(DATASET_FILE, "rb") as f:
            response = client.files.create(
                file=f,
                purpose="fine-tune"
            )
        
        file_id = response.id
        logger.info(f"File uploaded successfully. ID: {file_id}")

        # 2. Create Fine-Tuning Job
        logger.info("Starting fine-tuning job for gpt-4o-mini...")
        
        job = client.fine_tuning.jobs.create(
            training_file=file_id,
            model="gpt-4o-mini-2024-07-18",
            hyperparameters={
                "n_epochs": 3  # Start with standard 3 epochs
            },
            suffix="dispute_classifier_v2"
        )
        
        job_id = job.id
        logger.info(f"Fine-tuning job created. ID: {job_id}")
        logger.info(f"Status: {job.status}")

        # 3. Log Details
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "job_id": job_id,
            "file_id": file_id,
            "model": "gpt-4o-mini-2024-07-18",
            "dataset": str(DATASET_FILE),
            "status": job.status
        }

        # Append to log list or create new
        logs = []
        if LOG_FILE.exists():
            with open(LOG_FILE, 'r', encoding='utf-8') as f:
                try:
                    content = f.read()
                    if content:
                        logs = json.loads(content)
                        if isinstance(logs, dict): # Handle legacy format if any
                            logs = [logs]
                except json.JSONDecodeError:
                    pass
        
        logs.append(log_entry)
        
        with open(LOG_FILE, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=2)
            
        logger.info(f"Submission details logged to {LOG_FILE}")

    except Exception as e:
        logger.error(f"Failed to submit fine-tuning job: {e}")

if __name__ == "__main__":
    submit_finetuning()

