import json
import random
import pytest
from pathlib import Path
from backend.phases.classify import classify_dispute

# Load golden set data
DATA_PATH = Path(__file__).parents[1] / "synthetic_data/phase1/golden_set/classification_labels.json"

def load_sampled_test_cases():
    """Load and sample 5 random cases from the golden set."""
    if not DATA_PATH.exists():
        return []
    
    with open(DATA_PATH, "r") as f:
        data = json.load(f)
    
    # Sample 5 cases if we have enough data, otherwise take all
    if len(data) > 5:
        # Use a fixed seed for reproducibility in this session if needed, 
        # but random is fine for "sampling".
        return random.sample(data, 5)
    return data

# Load cases at module level
sampled_cases = load_sampled_test_cases()

@pytest.mark.asyncio
@pytest.mark.parametrize("case", sampled_cases)
async def test_classify_golden_set_live(case):
    """
    Live LLM test for 5 sampled cases from the golden set.
    
    This test DOES NOT MOCK the LLM service. It makes actual API calls.
    It expects the environment to be configured with valid API keys.
    """
    dispute_id = case["dispute_id"]
    description = case["description"]
    expected_reason = case["true_reason_code"]
    expected_network = case["network"]

    task = {"dispute_id": dispute_id, "description": description}
    
    print(f"\n--- Live Test Case: {dispute_id} ---")
    print(f"Description: {description}")
    print(f"Expected: {expected_reason} ({expected_network})")

    # Call real classify_dispute
    try:
        result = await classify_dispute(task)
        
        print(f"Result: {json.dumps(result, indent=2)}")

        # Soft assertions or hard assertions depending on how strict we want to be with the LLM
        # For a test suite, we generally want hard assertions, but LLMs can be non-deterministic.
        # We will stick to hard assertions for now as the classification task should be robust.
        assert result["reason_code"] == expected_reason
        assert result["network"] == expected_network.lower()
        
    except Exception as e:
        pytest.fail(f"Live classification failed for {dispute_id}: {e}")

