# V4 Prompt Evaluation Analysis

## Session Goal
Evaluate the V4 prompt on 50 failure cases identified from the V2 run, focusing on improving the distinction between "General" (Detail Disputes) and "Fraudulent" (Existence Disputes).

## Results Overview
- **Total Cases Tested**: 50 (all previously failed cases)
- **Fixed Cases**: 28
- **Success Rate**: 56% improvement on the failure set

## What Worked
1.  **Emotional "High Bill" Inputs**:
    - The V4 prompt successfully corrected cases where users were shouting about high bills (e.g., `gen_amex_A01_emotional`).
    - The **Chain of Thought (CoT)** reasoning correctly prioritized "High bill" implies participation, effectively overriding the emotional "I didn't authorize this" language.

2.  **Ambiguous General Disputes**:
    - The CoT step helped the model reason through ambiguous statements (e.g., `gen_amex_A02_ambiguous`), correctly identifying them as `general` disputes rather than defaulting to `unrecognized`.

3.  **Explicit Fraud**:
    - Cases with clear "never went to store" or "stolen card" language (e.g., `gen_amex_F10_emotional`) were correctly classified as `fraudulent`.

## What Didn't Work (Remaining Failures)
1.  **"Unrecognized" vs "Fraud" Confusion**:
    - **Issue**: Several `fraudulent` cases were misclassified as `unrecognized` or `general` (e.g., `gen_amex_F10_narrative`, `gen_amex_F29_narrative`).
    - **Reason**: The CoT sometimes over-analyzed phrases like "I don't recall authorizing" as "uncertainty" (leading to `unrecognized`) rather than a denial of participation.
    - **Trace Insight**: The model reasoned, *"The phrase 'I don't recall authorizing' suggests they may recognize the transaction but are unsure about the details... this indicates a detail dispute..."*. This is too conservative for fraud detection.

2.  **"Subscription Canceled" vs "Credit Not Processed"**:
    - **Issue**: Bidirectional confusion between `subscription_canceled` and `credit_not_processed` (e.g., `gen_amex_C05_emotional`, `gen_amex_C05_narrative`).
    - **Reason**: The model struggles to distinguish between "cancelled a service (recurring)" and "cancelled an order (one-time)". The prompt's definitions might be too rigid, or the CoT focuses on the "cancellation" aspect rather than the "recurring" nature.

3.  **"Duplicate" vs "General"**:
    - **Issue**: Some `duplicate` disputes are classified as `general` (e.g., `gen_amex_C14_narrative`).
    - **Reason**: When users say "I see something odd... looks like a double charge", the model sometimes categorizes the "oddness" as `general` instead of catching the specific `duplicate` signal.

## Recommendations for V5
1.  **Refine "Unrecognized" Definition**: Explicitly state that "I don't recall" + "I didn't authorize" should lean towards `fraudulent` if no other details (like amount) are disputed.
2.  **Clarify Subscription vs. Credit**: Add a specific rule or CoT step to check for "recurring" vs "one-time" to split `subscription_canceled` and `credit_not_processed`.
3.  **Strengthen Duplicate Detection**: Add examples where "odd statement" + "double charge" = `duplicate`.

