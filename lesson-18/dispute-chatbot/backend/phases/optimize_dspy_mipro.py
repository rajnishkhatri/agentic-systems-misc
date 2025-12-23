import dspy
try:
    from dspy.teleprompt import MIPROv2
except ImportError:
    try:
        from dspy.teleprompt import MIPRO
        MIPROv2 = MIPRO
    except ImportError:
        MIPROv2 = None

from dspy.evaluate import Evaluate
import os
import json
from dotenv import load_dotenv

load_dotenv()

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

# Aliases commonly produced by models during optimization
CATEGORY_ALIASES = {
    "fraud": "fraudulent",
    "unauthorized": "fraudulent",
    "authorization": "general",
    "processing_errors": "general",
    "processing_error": "general",
    "duplicate_charge": "duplicate",
    "subscription_cancelled": "subscription_canceled",
    "refund_not_processed": "credit_not_processed",
    "product_not_as_described": "product_unacceptable",
    "unknown": "unrecognized",
}


def normalize_category(raw: str) -> str:
    if not raw:
        return ""
    key = (
        str(raw)
        .strip()
        .lower()
        .replace("-", "_")
        .replace(" ", "_")
    )
    if key in CANONICAL_CATEGORIES:
        return key
    return CATEGORY_ALIASES.get(key, key)


class DisputeCategorySignature(dspy.Signature):
    """Classify the dispute description into the correct category."""
    
    description = dspy.InputField(desc="The customer's description of the dispute.")
    reasoning = dspy.OutputField(desc="Reasoning for the classification.")
    category = dspy.OutputField(
        desc=f"The unified category. Must be one of: {sorted(CANONICAL_CATEGORIES)}"
    )

class DisputeClassifier(dspy.Module):
    def __init__(self):
        super().__init__()
        self.prog = dspy.ChainOfThought(DisputeCategorySignature)
        
    def forward(self, description):
        return self.prog(description=description)

def validate_category(example, pred, trace=None):
    if not pred.category:
        return False
    return normalize_category(example.category) == normalize_category(pred.category)

def export_to_jinja(program, output_path):
    cot = program.prog
    # Identify the predictor holding the demos and signature
    # In newer DSPy, ChainOfThought might be a Module wrapping a Predictor, or inherits.
    # If it has a 'predict' attribute (Module), check that.
    # Or 'predictor' attribute.
    
    candidates = [cot]
    if hasattr(cot, 'predict'):
        candidates.append(cot.predict)
    if hasattr(cot, 'predictor'):
        candidates.append(cot.predictor)
        
    demos = []
    instruction = ""
    
    for cand in candidates:
        d = getattr(cand, 'demos', [])
        if d:
            demos = d
            # If we found demos, this is likely the one
            # Check signature here too
            sig = getattr(cand, 'signature', None) or getattr(cand, 'extended_signature', None)
            if sig:
                instruction = sig.instructions
            break
            
    if not demos:
        print("Warning: No demos found in program. Checking signature only.")
        # Fallback to signature in candidates
        for cand in candidates:
             sig = getattr(cand, 'signature', None) or getattr(cand, 'extended_signature', None)
             if sig:
                 instruction = sig.instructions
                 break
    
    print(f"Exporting {len(demos)} demos...")
    
    # Simple formatting of demos
    demos_text = ""
    for demo in demos:
        if isinstance(demo, dict):
            d_desc = demo.get('description', '')
            d_reas = demo.get('reasoning', '')
            d_cat = demo.get('category', '')
        else:
            d_desc = getattr(demo, 'description', '')
            d_reas = getattr(demo, 'reasoning', '')
            d_cat = getattr(demo, 'category', '')

        demos_text += f"Description: {d_desc}\n"
        demos_text += f"Reasoning: {d_reas}\n"
        demos_text += f"Category: {d_cat}\n\n"
    
    # Jinja2 template with embedded few-shot examples
    # Note: We use double braces {{ }} for Jinja variables, so we need {{{{ }}}} in f-string
    template = f"""{{# DSPy Optimized Prompt (MIPROv2) #}}
{instruction}

Input Field: Description
Output Fields: Reasoning, Category

---

{demos_text}Description: {{{{ description }}}}
Reasoning:"""
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(template)
    print(f"Exported Jinja2 template to {output_path}")

def optimize():
    # Paths
    # Assuming running from workspace root
    base_dir = os.path.join("lesson-18", "dispute-chatbot", "synthetic_data", "phase1", "dspy")
    train_path = os.path.join(base_dir, "train.json")
    dev_path = os.path.join(base_dir, "dev.json")
    
    if not os.path.exists(train_path):
        print(f"Train data not found at {train_path}. Run prepare_data.py first.")
        return

    print("Loading data...")
    with open(train_path, 'r', encoding='utf-8') as f:
        train_data = [dspy.Example(description=x['description'], category=x['category']).with_inputs('description') for x in json.load(f)]
        
    with open(dev_path, 'r', encoding='utf-8') as f:
        dev_data = [dspy.Example(description=x['description'], category=x['category']).with_inputs('description') for x in json.load(f)]
    
    # Setup LM
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("OPENAI_API_KEY not found. Please set it in your environment.")
        return

    print("Configuring LM...")
    lm = dspy.LM("openai/gpt-4o-mini", api_key=api_key)
    dspy.settings.configure(lm=lm)
    
    # Optimizer
    print("Configuring MIPROv2...")
    if MIPROv2:
        teleprompter = MIPROv2(metric=validate_category, auto="light")
        
        print("Compiling (this may take a while)...")
        # Using a smaller subset for demonstration if needed, but we'll try full
        compiled_program = teleprompter.compile(
            DisputeClassifier(),
            trainset=train_data,
            valset=dev_data,
            max_bootstrapped_demos=3,
            max_labeled_demos=3,
            requires_permission_to_run=False
        )
        
        save_path = "lesson-18/dispute-chatbot/backend/phases/dispute_classifier_mipro.json"
        compiled_program.save(save_path)
        print(f"Saved compiled program to {save_path}")
        
        # Evaluate
        print("Evaluating on Dev set...")
        evaluator = Evaluate(devset=dev_data, metric=validate_category, num_threads=4, display_progress=True, display_table=0)
        score = evaluator(compiled_program)
        print(f"Dev Accuracy: {score}")
        
        # Export
        export_path = "composable_app/prompts/DisputeClassifier_identify_category_v3_optimized.j2"
        export_to_jinja(compiled_program, export_path)
        
    else:
        print("MIPROv2 class not found in dspy.teleprompt.")

if __name__ == "__main__":
    optimize()

