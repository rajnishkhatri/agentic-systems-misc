# Qualitative Failure Taxonomy: Classification Phase (Optimized Flow)

## Overview
This document analyzes the failure patterns observed during the stress testing of the optimized 3-step classification flow (Network ID -> Category ID -> Code Selection).

## Methodology
- **Test Suite**: `stress_test_classify.py` (20 curated scenarios).
- **Golden Set**: `test_golden_set_classification.py` (100 synthetic cases, mocked LLM).
- **Models**: GPT-4o-mini (via LiteLLM).

## Taxonomy of Failures

### 1. Ambiguity in User Intent (Ambiguity Failure)
*   **Description**: The user's description is too vague to definitively map to a single specific reason code, leading to valid but differing interpretations between the "expected" truth and the model's output.
*   **Example**: `amb_02` ("Charge error").
    *   **Expected**: `10.4` (Fraud/General).
    *   **Actual**: `12.5` (Incorrect Amount).
    *   **Analysis**: "Charge error" is highly ambiguous. It could mean "I was charged the wrong amount" (12.5) or "I shouldn't have been charged at all" (10.4). The model's selection of 12.5 is semantically valid given the phrasing.
*   **Mitigation**: This is an inherent limitation of short, ambiguous inputs. The system should ideally prompt for clarification (e.g., "Do you mean the amount was wrong, or you didn't make this purchase?").

### 2. Network-Specific Code nuances (Precision Failure)
*   **Description**: The model correctly identifies the *category* (e.g., Duplicate) but selects a slightly different specific code within that category than expected.
*   **Example**: `dup_01` & `dup_02`.
    *   **Expected**: `12.6` (Duplicate Processing).
    *   **Actual**: `12.6.1` (Duplicate Processing).
    *   **Analysis**: `12.6.1` is a sub-code of `12.6`. The model was actually *more* precise than the initial test expectation. This was a "false failure" in the test suite, which was corrected by updating the expectation.

### 3. Cross-Network Mapping Complexity (Schema Failure)
*   **Description**: Amex reason codes are often broader than Visa codes. Mapping generic descriptions to specific Amex alpha-numeric codes can be tricky.
*   **Example**: `net_amex_01` ("Hotel overcharged me").
    *   **Expected**: `C08` (Goods/Services Not Received - *Incorrect in original test*).
    *   **Actual**: `P05` (Incorrect Charge Amount).
    *   **Analysis**: The user said "overcharged", which maps perfectly to `P05` (Incorrect Charge Amount). The original test expectation of `C08` (Not Received) was incorrect. The model was right.

## Success Analysis
*   **High Accuracy**: The optimized flow achieved **95% accuracy** (19/20) on the stress test after correcting for test-data errors.
*   **Robustness**: The 3-step funnel effectively prevented "hallucinations" (e.g., inventing codes) by constraining the final selection step to a valid sub-list.
*   **Golden Set**: The 100-case golden set passed 100% when mocking the intermediate steps, validating the orchestrator logic.

## Recommendations
1.  **Ambiguity Handling**: Implement a "Request Clarification" step in the Chatbot UI when confidence is low or the input is very short (like "Charge error").
2.  **Test Data Refinement**: Continuously update test expectations to reflect the *most precise* correct answer, especially for network-specific nuances.
3.  **Prompt Tuning**: Minor tuning of the `DisputeClassifier_identify_category.j2` prompt could help bias "Charge error" towards "Incorrect Amount" vs "Fraud" depending on business risk preference (Fraud is safer default).

