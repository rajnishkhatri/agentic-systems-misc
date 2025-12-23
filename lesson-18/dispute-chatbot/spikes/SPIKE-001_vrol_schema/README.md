# SPIKE-001: VROL Schema Validation

**Date:** 2025-12-08
**Status:** Completed

## Purpose
Validate the `network_payloads.yaml` OpenAPI specification against generated edge cases and compare it with known VROL structures (`visa_vrol_types.ts`) to identify gaps.

## Validation Results
The validation script `validate_vrol.py` ran successfully with 8/8 tests passed.

| Test Case | Result | Notes |
|-----------|--------|-------|
| Boundary: Max Length Narrative | PASS | 2000 chars handled correctly |
| Boundary: Min Amount | PASS | 0.01 accepted |
| Invalid: Amount Zero | PASS | 0.00 rejected |
| Optionality: Required Only | PASS | Minimal payload accepted |
| Polymorphism: Valid Fraud | PASS | `fraud_ce3` type accepted |
| Invalid: Fraud Type + Shipping | PASS | Rejected due to schema mismatch |
| Invalid: Missing ARN | PASS | Rejected |
| Invalid: Bad Reason Code | PASS | Rejected |

## Gap Analysis (YAML vs. Internal TS Types)

Comparing `design/04_api_specifications/network_payloads.yaml` with `lesson-18/dispute-schema/network_integration/visa_vrol_types.ts`:

### 1. Questionnaire Structure
- **TS Types**: Includes explicit `VisaFraudQuestionnaire` (e.g., `cardInPossession`, `policeReportFiled`) and `VisaConsumerQuestionnaire`.
- **YAML**: These specific questionnaire fields are missing. The YAML focuses on `evidence` and `representment_rights`.
- **Recommendation**: Add a `questionnaire` object to `VROLRepresentmentRequest` to capture these specific VROL inputs, as they are often mandatory for certain reason codes.

### 2. Cardholder Information
- **TS Types**: Includes `cardholderInfo` (account number, name).
- **YAML**: Missing top-level cardholder info. While VROL has the card number from the dispute, providing `cardholder_name` is often required for validation.
- **Recommendation**: Add optional `cardholder_info` to schema.

### 3. Naming Conventions
- **TS Types**: Uses `memberMessageText`.
- **YAML**: Uses `defense_narrative`.
- **Recommendation**: Keep `defense_narrative` as it is more descriptive for the LLM/Agent context, but ensure the Adapter (`visa_vrol.py`) maps this to `MemberMessageText` in the actual VROL SOAP/JSON call.

## Action Plan
1.  **Update `network_payloads.yaml`**:
    -   Add `questionnaire` object (polymorphic based on reason code).
    -   Add `cardholder_info` object.
2.  **Verify**: Re-run validation script to ensure changes are valid.

