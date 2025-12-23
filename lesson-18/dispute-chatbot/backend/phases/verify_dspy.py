import dspy
from dspy.evaluate import Evaluate
import os
import json
from dotenv import load_dotenv
# Add current dir to path to import optimize_dspy_mipro if needed, but since we run from root...
# We will assume running as python -m ... or similar, or just path hacking.
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from optimize_dspy_mipro import DisputeClassifier, DisputeCategorySignature, validate_category

load_dotenv()

def verify():
    # Paths relative to workspace root
    base_dir = os.path.join("lesson-18", "dispute-chatbot", "synthetic_data", "phase1", "dspy")
    test_path = os.path.join(base_dir, "test.json")
    program_path = "lesson-18/dispute-chatbot/backend/phases/dispute_classifier_mipro.json"
    
    if not os.path.exists(test_path):
        print(f"Test data not found at {test_path}")
        return
    
    if not os.path.exists(program_path):
        print(f"Compiled program not found at {program_path}")
        return
        
    print("Loading test data...")
    with open(test_path, 'r', encoding='utf-8') as f:
        test_data = [dspy.Example(description=x['description'], category=x['category']).with_inputs('description') for x in json.load(f)]
        
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("OPENAI_API_KEY not found.")
        return

    lm = dspy.LM("openai/gpt-4o-mini", api_key=api_key)
    dspy.settings.configure(lm=lm)
    
    print(f"Loading program from {program_path}...")
    loaded_program = DisputeClassifier()
    loaded_program.load(program_path)
    
    print("Evaluating on Test set...")
    # display_table=True allows us to see failures
    evaluator = Evaluate(devset=test_data, metric=validate_category, num_threads=4, display_progress=True, display_table=True)
    score = evaluator(loaded_program)
    print(f"Test Accuracy: {score}")

if __name__ == "__main__":
    verify()





