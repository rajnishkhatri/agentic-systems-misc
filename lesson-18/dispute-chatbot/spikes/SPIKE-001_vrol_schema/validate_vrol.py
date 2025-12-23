import yaml
import json
from openapi_schema_validator import validate
import sys
from copy import deepcopy

import os

# Resolve path relative to this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SPEC_PATH = os.path.abspath(os.path.join(SCRIPT_DIR, "../../design/04_api_specifications/network_payloads.yaml"))

def load_spec(path):
    with open(path, 'r') as f:
        return yaml.safe_load(f)

def validate_payload(payload, schema, spec):
    try:
        # Resolve references if necessary, but openapi-schema-validator handles many cases.
        # We might need a resolver if simple validation fails due to refs.
        # For this spike, we'll rely on the validator's capability or manual ref resolution if needed.
        # However, openapi-schema-validator usually requires a full resolved schema or a resolver.
        # Let's try basic validation against the specific component schema first.
        
        # A simple trick for local ref resolution in this context:
        # Since we are validating against a component, we need to pass the full spec as the resolver source
        # or inline the refs. 
        # For simplicity in this script, we will assume the validator can handle local refs if we pass the whole spec context
        # but standard `validate` usually takes (instance, schema). 
        # We might need to use a library that handles $ref resolution like prance or jsonref if this fails,
        # but let's try mapping the schema manually or using a library that supports it.
        
        # Actually, let's use a simpler approach: strict checks on generated data structure matching the expectations.
        # But the goal is to use the schema.
        
        # Let's use `jsonschema` library features if `openapi-schema-validator` acts up, but `openapi-schema-validator` is standard.
        # We need to constructing a valid schema object that includes components.
        
        full_schema = deepcopy(spec)
        # We want to validate against VROLRepresentmentRequest
        # We can construct a schema wrapper.
        
        validation_schema = {
            "components": full_schema.get("components", {}),
            "$ref": "#/components/schemas/VROLRepresentmentRequest"
        }
        
        validate(payload, validation_schema)
        return True, "Valid"
    except Exception as e:
        return False, str(e)

def run_tests():
    print("Loading OpenAPI Spec...")
    try:
        spec = load_spec(SPEC_PATH)
    except FileNotFoundError:
        print(f"Error: Could not find spec at {SPEC_PATH}")
        sys.exit(1)

    print("Spec loaded successfully.")
    
    # 1. Validate Existing Examples
    print("\n--- Validating Embedded Examples ---")
    examples = spec['components']['examples']
    for name, example in examples.items():
        print(f"Validating {name}...", end=" ")
        is_valid, msg = validate_payload(example['value'], None, spec)
        if is_valid:
            print("PASS")
        else:
            print(f"FAIL: {msg}")

    # 2. Generate and Validate Test Cases
    print("\n--- Running Generated Test Cases ---")
    
    base_fraud = examples['Fraud104CE3Example']['value']
    base_pnr = examples['PNR131PODExample']['value']

    test_cases = []

    # Case 1: Boundary - Max Length Strings (Narrative)
    case_1 = deepcopy(base_fraud)
    case_1['representment_rights']['defense_narrative'] = "A" * 2000
    test_cases.append(("Boundary: Max Length Narrative", case_1, True))

    # Case 2: Boundary - Min Amount
    case_2 = deepcopy(base_fraud)
    case_2['dispute_header']['dispute_amount'] = 0.01
    test_cases.append(("Boundary: Min Amount", case_2, True))
    
    # Case 3: Invalid - Amount too small
    case_3 = deepcopy(base_fraud)
    case_3['dispute_header']['dispute_amount'] = 0.00
    test_cases.append(("Invalid: Amount Zero", case_3, False))

    # Case 4: Optionality - Required Fields Only (Fraud)
    # Removing optional fields
    case_4 = deepcopy(base_fraud)
    if 'supporting_documents' in case_4:
        del case_4['supporting_documents']
    # Merchant info optional fields? All seem required in schema except maybe some patterns.
    # checking schema... all merchant_info props are required? Yes.
    test_cases.append(("Optionality: Required Only", case_4, True))

    # Case 5: Polymorphism - Valid Fraud
    # Already covered by base_fraud, but let's ensure structure is correct.
    case_5 = deepcopy(base_fraud)
    case_5['evidence']['evidence_type'] = 'fraud_ce3'
    test_cases.append(("Polymorphism: Valid Fraud", case_5, True))

    # Case 6: Polymorphism - Invalid Mismatch (Fraud header, Shipping evidence)
    case_6 = deepcopy(base_fraud)
    case_6['dispute_header']['reason_code'] = '10.4' # Fraud
    # Inject shipping evidence but keep type as fraud_ce3 to test schema validation on content
    # OR change type to shipping_pnr to test discriminator logic if we had cross-validation
    # The schema uses oneOf based on evidence_type. 
    # If we put shipping evidence but say it's fraud_ce3, it should fail validation of fraud_ce3 schema.
    case_6['evidence']['evidence_type'] = 'fraud_ce3'
    case_6['evidence']['shipping_evidence'] = base_pnr['evidence']['shipping_evidence'] # Inject shipping
    if 'ce3_evidence' in case_6['evidence']:
        del case_6['evidence']['ce3_evidence']
    test_cases.append(("Invalid: Fraud Type with Shipping Evidence", case_6, False))

    # Case 7: Invalid - Missing Required Field (ARN)
    case_7 = deepcopy(base_fraud)
    del case_7['dispute_header']['arn']
    test_cases.append(("Invalid: Missing ARN", case_7, False))

    # Case 8: Boundary - Invalid Enum
    case_8 = deepcopy(base_fraud)
    case_8['dispute_header']['reason_code'] = "99.9"
    test_cases.append(("Invalid: Bad Reason Code", case_8, False))

    results = []
    for name, payload, should_pass in test_cases:
        print(f"Testing {name}...", end=" ")
        is_valid, msg = validate_payload(payload, None, spec)
        
        if is_valid == should_pass:
            print("PASS")
            results.append(True)
        else:
            print(f"FAIL (Expected {'Valid' if should_pass else 'Invalid'}, got {'Valid' if is_valid else 'Invalid'})")
            if not is_valid:
                print(f"  Error: {msg}")
            results.append(False)

    print(f"\nSummary: {sum(results)}/{len(results)} tests passed.")
    if all(results):
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    run_tests()

