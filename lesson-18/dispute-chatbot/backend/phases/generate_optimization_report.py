import dspy
import json
import os
import asyncio
from typing import List, Literal, Optional, Dict, Any
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- Definitions from optimize_dspy_tot.py ---

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
        self.prog = dspy.ChainOfThought(DisputeToTSignature)
        
    def forward(self, description):
        return self.prog(description=description)

# --- Reporting Logic ---

HTML_TEMPLATE_HEADER = """<!DOCTYPE html>
<html>
<head>
    <title>DSPy Optimization Traces Report</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; color: #333; }
        .container { max-width: 1400px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        h1, h2, h3 { color: #2c3e50; }
        .subtitle { color: #6c757d; font-size: 14px; margin-top: -15px; margin-bottom: 20px; }

        .dashboard { display: flex; gap: 20px; margin-bottom: 30px; flex-wrap: wrap; }
        .card { flex: 1; min-width: 200px; background: #f8f9fa; padding: 20px; border-radius: 6px; border: 1px solid #e9ecef; }
        .card-highlight { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
        .card-highlight .stat-label { color: rgba(255,255,255,0.8); }
        .stat-value { font-size: 24px; font-weight: bold; color: #2c3e50; }
        .card-highlight .stat-value { color: white; }
        .stat-label { color: #6c757d; font-size: 14px; text-transform: uppercase; letter-spacing: 0.5px; }

        table { width: 100%; border-collapse: collapse; margin-top: 20px; font-size: 14px; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #eee; }
        th { background: #f8f9fa; font-weight: 600; color: #495057; position: sticky; top: 0; }

        .status-pass { color: #28a745; font-weight: bold; }
        .status-fail { color: #dc3545; font-weight: bold; }
        .status-error { color: #fd7e14; font-weight: bold; }

        .row-pass { background-color: #f8fff9; }
        .row-fail { background-color: #fff8f8; cursor: pointer; }
        .row-fail:hover { background-color: #ffeef0; }
        
        .trace-detail { display: none; background: #fafafa; padding: 20px; border-top: 1px solid #eee; }

        .branch-analysis { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-bottom: 20px; }
        .branch-card { background: #fff; padding: 15px; border-radius: 6px; border: 1px solid #e9ecef; }
        .branch-card h4 { margin: 0 0 10px 0; font-size: 14px; color: #495057; display: flex; align-items: center; gap: 8px; }
        .branch-icon { width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: bold; color: white; }
        .branch-a { background: #17a2b8; }
        .branch-b { background: #28a745; }
        .branch-c { background: #fd7e14; }
        .branch-conclusion { font-size: 16px; font-weight: bold; color: #2c3e50; margin-bottom: 8px; }
        .branch-evidence { font-size: 12px; color: #6c757d; }

        .synthesis-box { background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); padding: 15px; border-radius: 6px; margin-bottom: 20px; }
        .synthesis-box h4 { margin: 0 0 10px 0; }
        
        .prompt-box, .response-box { background: #fff; padding: 10px; border: 1px solid #eee; border-radius: 4px; font-family: monospace; white-space: pre-wrap; margin-top: 5px; font-size: 12px; max-height: 300px; overflow-y: auto; }
        
        .filter-bar { margin-bottom: 20px; display: flex; gap: 10px; flex-wrap: wrap; }
        .filter-btn { padding: 8px 16px; border: 1px solid #ddd; background: white; border-radius: 20px; cursor: pointer; font-size: 13px; }
        .filter-btn.active { background: #2c3e50; color: white; border-color: #2c3e50; }
    </style>
    <script>
        function toggleTrace(id) {
            const row = document.getElementById('trace-' + id);
            if (row.style.display === 'none') {
                row.style.display = 'table-row';
            } else {
                row.style.display = 'none';
            }
        }

        function filterRows(type) {
            const rows = document.querySelectorAll('.case-row');
            const traceRows = document.querySelectorAll('.trace-detail');
            traceRows.forEach(row => row.style.display = 'none'); // Hide all details when filtering

            rows.forEach(row => {
                if (type === 'all' || row.classList.contains(type)) {
                    row.style.display = 'table-row';
                } else {
                    row.style.display = 'none';
                }
            });

            document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
            document.getElementById('btn-' + type).classList.add('active');
        }
    </script>
</head>
<body>
    <div class="container">
        <h1>DSPy Optimization Traces Report</h1>
        <p class="subtitle">Generated from Optimized Program (MIPROv2)</p>
"""

def generate_report():
    # 1. Setup
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        print("Error: OPENAI_API_KEY not found.")
        return

    lm = dspy.LM("openai/gpt-4o-mini", api_key=openai_api_key)
    dspy.settings.configure(lm=lm)

    # 2. Load Program
    program_path = "lesson-18/dispute-chatbot/backend/phases/dispute_classifier_tot_mipro.json"
    if not os.path.exists(program_path):
        print(f"Error: Program not found at {program_path}")
        return

    print("Loading compiled program...")
    loaded_program = DisputeToTModule()
    loaded_program.load(program_path)

    # 3. Load Test Data
    test_path = "lesson-18/dispute-chatbot/backend/phases/distillation_data/distillation_test.json"
    if not os.path.exists(test_path):
        print(f"Error: Test data not found at {test_path}")
        return

    with open(test_path, 'r', encoding='utf-8') as f:
        test_data = json.load(f)

    print(f"Evaluating {len(test_data)} examples...")
    
    results = []
    correct_count = 0
    
    for i, example in enumerate(test_data):
        description = example['description']
        true_category = normalize_category(example['category'])
        
        try:
            pred = loaded_program(description=description)
            # Pred output 'result' might be a Pydantic object or dict depending on how dspy handled it
            # Since we used ChainOfThought(Signature), the output field 'result' contains the parsed object/dict
            
            # ChainOfThought might return a Prediction object where attributes are accessed directly
            result_obj = pred.result
            
            # If it's a Pydantic model, dump to dict
            if isinstance(result_obj, BaseModel):
                result_dict = result_obj.model_dump()
            elif isinstance(result_obj, str):
                # Fallback if it failed to parse and returned raw string (unlikely with TypedPredictor concepts but possible)
                # Try to parse JSON from string
                try:
                    # Clean markdown code blocks if present
                    clean_str = result_obj.replace("```json", "").replace("```", "")
                    result_dict = json.loads(clean_str)
                except:
                    result_dict = {"category": "error", "synthesis": {"reasoning": f"Failed to parse: {result_obj}"}}
            else:
                result_dict = result_obj # Assume dict
                
            pred_category = normalize_category(result_dict.get('category', 'unknown'))
            is_correct = pred_category == true_category
            if is_correct:
                correct_count += 1
                
            results.append({
                "id": i,
                "description": description,
                "true_category": true_category,
                "pred_category": pred_category,
                "is_correct": is_correct,
                "trace": result_dict,
                "raw_reasoning": pred.reasoning if hasattr(pred, 'reasoning') else ""
            })
            
            print(f"[{i+1}/{len(test_data)}] {'PASS' if is_correct else 'FAIL'} | True: {true_category} | Pred: {pred_category}")
            
        except Exception as e:
            print(f"[{i+1}/{len(test_data)}] ERROR: {e}")
            results.append({
                "id": i,
                "description": description,
                "true_category": true_category,
                "pred_category": "error",
                "is_correct": False,
                "trace": {},
                "error": str(e)
            })

    accuracy = (correct_count / len(test_data)) * 100
    print(f"Final Accuracy: {accuracy:.2f}%")

    # 4. Generate HTML
    print("Generating HTML report...")
    
    html = HTML_TEMPLATE_HEADER
    
    # Dashboard
    html += f"""
        <div class="dashboard">
            <div class="card card-highlight">
                <div class="stat-label">Accuracy</div>
                <div class="stat-value">{accuracy:.1f}%</div>
            </div>
            <div class="card">
                <div class="stat-label">Total Examples</div>
                <div class="stat-value">{len(test_data)}</div>
            </div>
            <div class="card">
                <div class="stat-label">Correct</div>
                <div class="stat-value" style="color: #28a745">{correct_count}</div>
            </div>
            <div class="card">
                <div class="stat-label">Incorrect</div>
                <div class="stat-value" style="color: #dc3545">{len(test_data) - correct_count}</div>
            </div>
        </div>

        <div class="filter-bar">
            <button id="btn-all" class="filter-btn active" onclick="filterRows('all')">All Cases</button>
            <button id="btn-row-pass" class="filter-btn" onclick="filterRows('row-pass')">Passed</button>
            <button id="btn-row-fail" class="filter-btn" onclick="filterRows('row-fail')">Failed</button>
        </div>

        <table>
            <thead>
                <tr>
                    <th style="width: 5%">ID</th>
                    <th style="width: 40%">Description</th>
                    <th style="width: 15%">Predicted</th>
                    <th style="width: 15%">Actual</th>
                    <th style="width: 10%">Status</th>
                    <th style="width: 15%">Confidence</th>
                </tr>
            </thead>
            <tbody>
    """
    
    for res in results:
        row_class = "row-pass" if res['is_correct'] else "row-fail"
        status_class = "status-pass" if res['is_correct'] else "status-fail"
        status_text = "PASS" if res['is_correct'] else "FAIL"
        
        trace = res.get('trace', {})
        conf = trace.get('confidence', 0.0)
        
        # Branch Data
        ba = trace.get('branch_a', {})
        bb = trace.get('branch_b', {})
        bc = trace.get('branch_c', {})
        synth = trace.get('synthesis', {})
        
        html += f"""
            <tr class="case-row {row_class}" onclick="toggleTrace({res['id']})">
                <td>{res['id']}</td>
                <td style="max-width: 500px;">{res['description']}</td>
                <td><span class="category-badge" style="background: #2c3e50; color: #fff;">{res['pred_category']}</span></td>
                <td><span class="category-badge" style="background: #6c757d; color: #fff;">{res['true_category']}</span></td>
                <td class="{status_class}">{status_text}</td>
                <td>{conf:.2f}</td>
            </tr>
            <tr id="trace-{res['id']}" class="trace-detail">
                <td colspan="6">
                    <div class="trace-content">
                        <h3>Tree-of-Thought Analysis</h3>
                        
                        <div class="branch-analysis">
                            <div class="branch-card">
                                <h4><div class="branch-icon branch-a">A</div> Acknowledgment</h4>
                                <div class="branch-conclusion">{ba.get('conclusion', 'N/A')}</div>
                                <div class="branch-evidence">
                                    <strong>For:</strong> {', '.join(ba.get('evidence_for_acknowledgment', []))}<br>
                                    <strong>Against:</strong> {', '.join(ba.get('evidence_against_acknowledgment', []))}
                                </div>
                            </div>
                            <div class="branch-card">
                                <h4><div class="branch-icon branch-b">B</div> Complaint Specifics</h4>
                                <div class="branch-conclusion">{bb.get('complaint_type', 'N/A')}</div>
                                <div class="branch-evidence">
                                    <strong>Evidence:</strong> {', '.join(bb.get('evidence', []))}
                                </div>
                            </div>
                            <div class="branch-card">
                                <h4><div class="branch-icon branch-c">C</div> Persona</h4>
                                <div class="branch-conclusion">{bc.get('persona', 'N/A')}</div>
                                <div class="branch-evidence">
                                    <strong>Evidence:</strong> {', '.join(bc.get('evidence', []))}
                                </div>
                            </div>
                        </div>

                        <div class="synthesis-box">
                            <h4>Synthesis & Classification</h4>
                            <p><strong>Reasoning:</strong> {synth.get('reasoning', 'N/A')}</p>
                            <p><strong>Agreement Score:</strong> {synth.get('branch_agreement', 'N/A')}</p>
                            <p><strong>Priority Rule:</strong> {synth.get('priority_rule_applied', 'None')}</p>
                            <hr style="border: 0; border-top: 1px solid #ddd; margin: 10px 0;">
                            <p><strong>Final Confidence Rationale:</strong> {trace.get('confidence_rationale', 'N/A')}</p>
                        </div>

                        <div class="prompt-box">
                            <div class="label">Full Description:</div>
                            {res['description']}
                        </div>
                    </div>
                </td>
            </tr>
        """
        
    html += """
            </tbody>
        </table>
    </div>
</body>
</html>
    """
    
    output_path = "lesson-18/dispute-chatbot/backend/phases/miprov2optimization_report.html"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
        
    print(f"Report generated at: {output_path}")

if __name__ == "__main__":
    generate_report()

