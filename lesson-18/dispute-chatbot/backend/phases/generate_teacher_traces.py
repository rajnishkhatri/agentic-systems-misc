"""Generate Teacher Traces using Claude (teacher model).

This script uses a Claude teacher model to generate high-quality reasoning traces
for the dispute classification task. It enforces the inclusion of
'reason_code_group' in the reasoning to teach network-specific logic.
"""

import os
import json
import csv
import logging
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import sys

# Load environment variables from .env if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

# Add parent directory to path to import utils
sys.path.append(str(Path(__file__).parent.parent.parent))

from anthropic import AsyncAnthropic
from utils.prompt_service import render_prompt
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "phases" / "distillation_data"
CATALOG_PATH = Path(__file__).parent.parent.parent / "dispute-schema" / "reason_codes_catalog.csv"
OUTPUT_FILE = DATA_DIR / "fine_tuning_dataset.jsonl"
LOG_FILE = DATA_DIR / "teacher_trace_log.jsonl"

# Mapping from (network, code) to group
CodeGroupMap = Dict[str, str]

def load_catalog_groups() -> CodeGroupMap:
    """Load reason code groups from catalog."""
    mapping = {}
    if not CATALOG_PATH.exists():
        logger.error(f"Catalog not found at {CATALOG_PATH}")
        return mapping

    with open(CATALOG_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            network = row.get('Network', '').lower() or row.get('network', '').lower()
            code = row.get('reason_code', '')
            group = row.get('reason_code_group', '')
            
            if network and code and group:
                mapping[(network, code)] = group
    
    logger.info(f"Loaded {len(mapping)} code group mappings")
    return mapping

class CategoryResult(BaseModel):
    category: str
    reasoning: str


# Canonical category vocabulary (must match prompt templates + training labels)
CANONICAL_CATEGORIES = {
    "fraudulent",
    "general",
    "product_not_received",
    "duplicate",
    "subscription_canceled",
    "product_unacceptable",
    "credit_not_processed",
    "unrecognized",
}

# Common teacher/model aliases -> canonical categories
CATEGORY_ALIASES = {
    # Fraud
    "fraud": "fraudulent",
    "fraudulent_transaction": "fraudulent",
    "unauthorized": "fraudulent",
    "unauthorized_transaction": "fraudulent",
    "card_stolen": "fraudulent",
    "stolen_card": "fraudulent",
    # General / auth issues
    "authorization": "general",
    "auth": "general",
    "processing_error": "general",
    "processing_errors": "general",
    "charge_amount_dispute": "general",
    "amount_dispute": "general",
    # Not received
    "not_received": "product_not_received",
    "product_not_delivered": "product_not_received",
    "services_not_rendered": "product_not_received",
    "goods_not_received": "product_not_received",
    # Duplicate
    "duplicated": "duplicate",
    "duplicate_charge": "duplicate",
    "charged_twice": "duplicate",
    # Subscription canceled
    "subscription_cancelled": "subscription_canceled",
    "recurring_canceled": "subscription_canceled",
    "recurring_cancelled": "subscription_canceled",
    "canceled_subscription": "subscription_canceled",
    # Product unacceptable
    "product_not_as_described": "product_unacceptable",
    "not_as_described": "product_unacceptable",
    "defective": "product_unacceptable",
    "damaged": "product_unacceptable",
    "counterfeit": "product_unacceptable",
    # Credit not processed
    "refund_not_processed": "credit_not_processed",
    "credit_not_received": "credit_not_processed",
    "refund_missing": "credit_not_processed",
    "returned_not_refunded": "credit_not_processed",
    "cancelled_but_charged": "credit_not_processed",
    # Unrecognized
    "unknown": "unrecognized",
    "unknown_charge": "unrecognized",
    "not_recognized": "unrecognized",
    "dont_recognize": "unrecognized",
}

CANONICAL_REASON_CODE_GROUPS = {
    "authorization",
    "cardholder_disputes",
    "processing_errors",
    "fraud",
}


def _normalize_token(s: str) -> str:
    return (
        (s or "")
        .strip()
        .lower()
        .replace("-", "_")
        .replace(" ", "_")
    )


def normalize_category(raw_category: Optional[str]) -> Optional[str]:
    """Normalize raw category output to canonical labels (or None if missing)."""
    if not raw_category or not isinstance(raw_category, str):
        return None
    key = _normalize_token(raw_category)
    key = key.replace("__", "_")
    if key in CANONICAL_CATEGORIES:
        return key
    if key in CATEGORY_ALIASES:
        return CATEGORY_ALIASES[key]
    return key  # return normalized token for better debug logs


def extract_json_from_text(content: str) -> Optional[Dict[str, Any]]:
    """Extract and parse JSON object from a model response that may include code fences."""
    if not content or not isinstance(content, str):
        return None
    json_str = content
    if "```json" in content:
        json_str = content.split("```json", 1)[1].split("```", 1)[0].strip()
    elif "```" in content:
        json_str = content.split("```", 1)[1].split("```", 1)[0].strip()
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        return None


def contains_expected_group(output_obj: Dict[str, Any], expected_group: Optional[str]) -> Tuple[bool, Optional[str]]:
    """Check whether teacher output explicitly mentions a reason code group.

    Returns (ok, found_group_token). If expected_group is provided, ok means it matches.
    """
    haystack = json.dumps(output_obj, ensure_ascii=False).lower()

    # Strong signal: "Reason Code Group: <group>"
    found = None
    marker = "reason code group"
    if marker in haystack:
        # naive extraction window
        idx = haystack.find(marker)
        window = haystack[idx: idx + 120]
        for g in CANONICAL_REASON_CODE_GROUPS:
            if g.replace("_", " ") in window or g in window:
                found = g
                break

    normalized_expected = _normalize_token(expected_group) if expected_group else None
    if normalized_expected:
        # allow either exact token or space form
        ok = (
            normalized_expected in haystack
            or normalized_expected.replace("_", " ") in haystack
            or (found == normalized_expected)
        )
        return ok, found

    # If we don't know expected group, require at least *some* group mention.
    ok_any = any(
        (g in haystack) or (g.replace("_", " ") in haystack)
        for g in CANONICAL_REASON_CODE_GROUPS
    )
    return ok_any, found

async def generate_traces():
    """Generate traces using the configured teacher model."""
    
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        logger.error("ANTHROPIC_API_KEY environment variable not set.")
        return

    client = AsyncAnthropic(api_key=api_key)
    
    # Load training data
    train_file = DATA_DIR / "distillation_train.json"
    if not train_file.exists():
        logger.error(f"Train file not found at {train_file}")
        return

    with open(train_file, 'r', encoding='utf-8') as f:
        examples = json.load(f)

    # Load catalog mapping
    group_mapping = load_catalog_groups()

    valid_traces = []
    
    # Clear log file
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        pass

    logger.info(f"Starting trace generation for {len(examples)} examples...")

    for i, example in enumerate(examples):
        dispute_id = example.get('dispute_id')
        description = example.get('description')
        true_category = example.get('category')
        true_code = example.get('true_reason_code')
        network = example.get('network', '').lower()

        # Determine expected group
        expected_group = group_mapping.get((network, true_code))
        
        # Prepare the input prompt (Student's input)
        # Use v5 ToT prompt template for better reasoning and stronger output schema
        input_prompt = render_prompt("DisputeClassifier_identify_category_v5_tot.j2", description=description)

        # Prepare Teacher Prompt
        # We ask Claude to act as the expert and output JSON following the student's schema,
        # while forcing canonical category labels + explicit Reason Code Group mention.
        teacher_system_prompt = (
            "You are an expert Payment Dispute Classifier.\n"
            "Your job: follow the user's requested JSON schema exactly and classify the dispute.\n\n"
            "CRITICAL OUTPUT CONSTRAINTS:\n"
            f"- The final category MUST be EXACTLY one of: {sorted(CANONICAL_CATEGORIES)}\n"
            "- You MUST explicitly identify the Reason Code Group first, then decide the category.\n"
            f"- Reason Code Group MUST be exactly one of: {sorted(CANONICAL_REASON_CODE_GROUPS)}\n"
            "- You MUST include the exact phrase 'Reason Code Group: <group>' inside your output JSON "
            "(recommended location: synthesis.reasoning).\n"
            "- Output ONLY valid JSON. No markdown, no extra text."
        )

        teacher_user_prompt = (
            f"Payment network: {network}\n\n"
            f"{input_prompt}\n\n"
            "Reminder: Include 'Reason Code Group: <group>' inside the JSON."
        )

        try:
            response = await client.messages.create(
                model="claude-opus-4-5-20251101",
                max_tokens=1000,
                system=teacher_system_prompt,
                messages=[{"role": "user", "content": teacher_user_prompt}]
            )
            
            content = response.content[0].text

            # Parse JSON from response (Claude might wrap in code fences)
            result_dict = extract_json_from_text(content)
            if not result_dict:
                logger.warning(f"Failed to parse JSON for {dispute_id}")
                log_entry = {
                    "dispute_id": dispute_id,
                    "status": "parse_error",
                    "raw_response": content
                }
                with open(LOG_FILE, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(log_entry) + "\n")
                continue

            raw_category = result_dict.get("category")
            normalized_category = normalize_category(raw_category)

            # Validation
            is_valid = True
            rejection_reasons = []

            # Category validation (normalize teacher output)
            if normalized_category != true_category:
                is_valid = False
                rejection_reasons.append(
                    f"Category mismatch: Got {raw_category} (normalized={normalized_category}), Expected {true_category}"
                )

            group_ok, found_group = contains_expected_group(result_dict, expected_group)
            if not group_ok:
                is_valid = False
                if expected_group:
                    rejection_reasons.append(f"Missing/incorrect group in output: Expected '{expected_group}' (found={found_group})")
                else:
                    rejection_reasons.append("Missing Reason Code Group in output JSON")

            log_entry = {
                "dispute_id": dispute_id,
                "status": "accepted" if is_valid else "rejected",
                "rejection_reasons": rejection_reasons,
                "teacher_output": result_dict,
                "ground_truth": {
                    "category": true_category,
                    "group": expected_group
                }
            }
            
            with open(LOG_FILE, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + "\n")

            if is_valid:
                # Format for OpenAI Fine-tuning
                # OpenAI Chat Fine-tuning format requires "messages" list.
                # Since classify_v2 uses structured output, we should train the model 
                # to produce the JSON directly from the User prompt.
                # The `input_prompt` already contains the full schema + constraints (v5 ToT).
                
                ft_example = {
                    "messages": [
                        {"role": "system", "content": "You are a helpful assistant that classifies disputes."},
                        {"role": "user", "content": input_prompt},
                        {"role": "assistant", "content": json.dumps(result_dict)}
                    ]
                }
                valid_traces.append(ft_example)
                print(f"Accepted {dispute_id}")
            else:
                print(f"Rejected {dispute_id}: {rejection_reasons}")

        except Exception as e:
            logger.error(f"Error processing {dispute_id}: {e}")

    # Save Fine-Tuning Dataset
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        for item in valid_traces:
            f.write(json.dumps(item) + "\n")

    logger.info(f"Generated {len(valid_traces)} valid traces out of {len(examples)}")

if __name__ == "__main__":
    asyncio.run(generate_traces())

