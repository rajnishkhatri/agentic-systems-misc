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
from pydantic import BaseModel, Field
from typing import List, Literal, Optional

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


# --- Pydantic Models for ToT Schema ---

class BranchA(BaseModel):
    evidence_for_acknowledgment: List[str] = Field(description="List of phrases showing acknowledgment")
    evidence_against_acknowledgment: List[str] = Field(description="List of phrases showing denial")
    conclusion: Literal["acknowledged", "denied", "unclear"]

class BranchB(BaseModel):
    complaint_type: Literal["amount", "quality", "processing", "unspecified"]
    evidence: List[str] = Field(description="Specific phrases indicating complaint type")

class BranchC(BaseModel):
    persona: Literal["frustrated", "confused", "accusatory", "neutral"]
    evidence: List[str] = Field(description="Phrases indicating persona type")

class Synthesis(BaseModel):
    branch_agreement: float = Field(description="Score between 0.0 and 1.0 indicating how well branches align")
    priority_rule_applied: Optional[str] = Field(description="The specific priority rule applied, if any (e.g., 'Rule 1: Specifics Override Denial')")
    reasoning: str = Field(description="Step-by-step synthesis logic")

class CategoryResultV5ToT(BaseModel):
    branch_a: BranchA
    branch_b: BranchB
    branch_c: BranchC
    synthesis: Synthesis
    category: str = Field(description=f"The unified category. Must be one of: {sorted(CANONICAL_CATEGORIES)}")
    confidence: float
    confidence_rationale: str


class DisputeToTSignature(dspy.Signature):
    """
    Classify the dispute description into the correct category using a Tree-of-Thought approach.
    You must analyze the complaint through three independent branches (Acknowledgment, Complaint Specifics, Persona),
    then synthesize the findings to determine the final category.
    
    IMPORTANT: You must identify the 'Reason Code Group' in your synthesis if applicable.
    """
    
    description = dspy.InputField(desc="The customer's description of the dispute.")
    result: CategoryResultV5ToT = dspy.OutputField(desc="Structured analysis and classification result.")


class DisputeToTModule(dspy.Module):
    def __init__(self):
        super().__init__()
        # Use ChainOfThought to allow for reasoning before the final structured output if needed.
        # In DSPy 3.x, TypedPredictor is often merged into Predict/CoT with typed signatures.
        self.prog = dspy.ChainOfThought(DisputeToTSignature)
        
    def forward(self, description):
        return self.prog(description=description)


def validate_tot_result(example, pred, trace=None):
    """
    Robust metric for ToT classification.
    1. Checks if prediction exists.
    2. Validates schema (implicit via TypedPredictor, but we check if result is populated).
    3. Checks category accuracy with normalization.
    4. Checks for 'Reason Code Group' mention in synthesis (bonus).
    """
    if not pred.result:
        return False
        
    # Check category accuracy
    pred_cat = normalize_category(pred.result.category)
    true_cat = normalize_category(example.category)
    
    is_correct = pred_cat == true_cat
    
    if not is_correct:
        return False
        
    # Bonus check: Reason Code Group in synthesis reasoning
    # This is a soft check, mostly we care about accuracy, but we can return a float score > 1.0 
    # if we want to encourage it, or just use it as a tiebreaker. 
    # For standard accuracy metric, we usually return 0 or 1 (or boolean).
    # If we want to optimize for this, we can return a score.
    # Let's stick to boolean accuracy for now to ensure we optimize for correctness first.
    # Alternatively, MIPRO can optimize for a float score.
    
    # Let's make it a float score: 1.0 for correct category.
    # Add 0.1 if "Reason Code Group" or similar logic is mentioned in synthesis.reasoning
    
    score = 1.0
    
    # synthesis is a Pydantic model in pred.result.synthesis
    if "reason code" in pred.result.synthesis.reasoning.lower():
         score += 0.1
         
    return score


def export_to_jinja(program, output_path):
    # This needs to handle ChainOfThought and TypedPredictor behavior
    # We want to extract the optimized instruction and demos
    
    predictor = program.prog
    
    # In DSPy 3.x ChainOfThought might not hold demos directly if it wraps a Predict
    demos = getattr(predictor, 'demos', [])
    instruction = ""
    
    # If not found, check sub-predictors
    if not demos and hasattr(predictor, 'predictors'):
        sub_preds = predictor.predictors()
        if sub_preds:
            # Usually the first one is the main predictor
            main_pred = sub_preds[0]
            demos = getattr(main_pred, 'demos', [])
            if hasattr(main_pred, 'signature') and hasattr(main_pred.signature, 'instructions'):
                instruction = main_pred.signature.instructions
            elif hasattr(main_pred, 'extended_signature') and hasattr(main_pred.extended_signature, 'instructions'):
                instruction = main_pred.extended_signature.instructions

    # Fallback to direct signature check if instruction is still empty
    if not instruction:
        if hasattr(predictor, 'signature') and hasattr(predictor.signature, 'instructions'):
            instruction = predictor.signature.instructions
        elif hasattr(predictor, 'extended_signature') and hasattr(predictor.extended_signature, 'instructions'):
             instruction = predictor.extended_signature.instructions

    print(f"Exporting {len(demos)} demos...")
    
    demos_text = ""
    for demo in demos:
        # demo is a dspy.Example
        d_desc = getattr(demo, 'description', '')
        
        # The output in the demo for TypedPredictor is likely the 'result' object
        d_res = getattr(demo, 'result', None)
        
        # We need to serialize the result back to JSON for the template
        if d_res and isinstance(d_res, BaseModel):
            d_json = d_res.model_dump_json(indent=2)
        elif d_res:
             d_json = str(d_res)
        else:
            d_json = "{}"

        demos_text += f"Description: {d_desc}\n"
        demos_text += f"Result: {d_json}\n\n"
    
    # Jinja2 template
    template = f"""{{# DSPy Optimized Prompt (MIPROv2) - ToT #}}
{instruction}

Input Field: Description
Output Field: Result (JSON)

---

{demos_text}Description: {{{{ description }}}}
Result:"""
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(template)
    print(f"Exported Jinja2 template to {output_path}")


def optimize():
    # Paths
    base_dir = os.path.join("lesson-18", "dispute-chatbot", "backend", "phases", "distillation_data")
    train_path = os.path.join(base_dir, "distillation_train.json")
    dev_path = os.path.join(base_dir, "distillation_test.json")
    
    if not os.path.exists(train_path):
        print(f"Train data not found at {train_path}.")
        return

    print("Loading data...")
    # Adjust loading based on JSON structure. 
    # Usually list of dicts with 'description' and 'category'.
    with open(train_path, 'r', encoding='utf-8') as f:
        raw_train = json.load(f)
        train_data = [dspy.Example(description=x['description'], category=x['category']).with_inputs('description') for x in raw_train]
        
    with open(dev_path, 'r', encoding='utf-8') as f:
        raw_dev = json.load(f)
        dev_data = [dspy.Example(description=x['description'], category=x['category']).with_inputs('description') for x in raw_dev]
    
    # Setup LM
    openai_api_key = os.getenv("OPENAI_API_KEY")
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not openai_api_key:
        print("OPENAI_API_KEY not found.")
        return
        
    if not anthropic_api_key:
        print("ANTHROPIC_API_KEY not found.")
        # Proceeding might fail if Teacher needs it
    
    print("Configuring LMs...")
    # Student: GPT-4o-mini
    student_lm = dspy.LM("openai/gpt-4o-mini", api_key=openai_api_key)
    
    # Teacher: GPT-4o
    # Using dspy.LM with provider prefix if supported or dspy.Anthropic
    # dspy.LM supports "anthropic/..."
    teacher_lm = dspy.LM("openai/gpt-4o", api_key=openai_api_key)
    
    dspy.settings.configure(lm=student_lm)
    
    # Optimizer
    print("Configuring MIPROv2...")
    if MIPROv2:
        # Use teacher for instruction generation
        teleprompter = MIPROv2(
            metric=validate_tot_result, 
            auto=None,
            prompt_model=teacher_lm,
            task_model=student_lm,
            teacher_settings=dict(lm=teacher_lm),
            num_candidates=7,
            num_threads=3
        )
        
        print("Compiling (this may take a while)...")
        compiled_program = teleprompter.compile(
            DisputeToTModule(),
            trainset=train_data,
            valset=dev_data,
            max_bootstrapped_demos=3,
            max_labeled_demos=3,
            requires_permission_to_run=False,
            num_trials=12
        )
        
        save_path = "lesson-18/dispute-chatbot/backend/phases/dispute_classifier_tot_mipro.json"
        compiled_program.save(save_path)
        print(f"Saved compiled program to {save_path}")
        
        # Evaluate
        print("Evaluating on Dev set...")
        evaluator = Evaluate(devset=dev_data, metric=validate_tot_result, num_threads=3, display_progress=True, display_table=0)
        score = evaluator(compiled_program)
        print(f"Dev Accuracy (Score): {score}")
        
        # Export
        export_path = "lesson-18/dispute-chatbot/prompts/DisputeClassifier_identify_category_v6_mipro.j2"
        export_to_jinja(compiled_program, export_path)
        
    else:
        print("MIPROv2 class not found in dspy.teleprompt.")

if __name__ == "__main__":
    optimize()

