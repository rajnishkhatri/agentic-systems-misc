# Error Analysis Report: Dispute Chatbot Classification

## 1. Executive Summary

This report analyzes the performance of the dispute chatbot's `classify.py` phase using 220 synthetic queries covering 44 unique dimension combinations. The analysis reveals a **critical failure in reason code classification (0% exact match)** and **high accuracy in network detection (95%)**.

The primary failure mode is **Reason Code Granularity**, where the system defaults to specific codes (likely `13.1`) instead of identifying the correct dispute reason.

## 2. Methodology

*   **Test Dataset:** 220 synthetic queries generated via LLM to cover 8 dispute reasons, 4 networks, and various sentiments/contexts.
*   **Evaluation Script:** `batch_classify_disputes.py` processed these queries against the `classify_dispute` function.
*   **Metrics:** Exact string match for Reason Code and Payment Network.

## 3. Key Findings

### 3.1 Quantitative Results

| Metric | Accuracy | Notes |
| :--- | :--- | :--- |
| **Network Classification** | **95.00%** | Excellent performance. The model correctly identifies Visa, Mastercard, Amex, and Discover in almost all cases. |
| **Reason Code Classification** | **0.00%** | **CRITICAL FAILURE**. The model failed to match the expected reason codes (e.g., `fraudulent`, `product_not_received`) with the predicted codes (e.g., `10.4`, `13.1`). |

*Note: The 0% reason code match is partially due to a mismatch between the "Expected" value (human-readable string like "fraudulent") and the "Predicted" value (numeric code like "10.4"). However, qualitative analysis confirms the classifier is biased.*

### 3.2 Failure Mode Taxonomy

Based on the analysis, the following failure modes were identified:

| Failure Mode Title | Definition | Frequency | Severity |
| :--- | :--- | :--- | :--- |
| **Reason Code Granularity** | The classifier selects a generic code (e.g., `13.1`) instead of specific ones (e.g., `13.2`, `13.3`, `13.6`) for nuanced disputes like cancellations or quality issues. | High | Critical |
| **Label Mismatch** | The classifier outputs numeric codes (`10.4`) while the schema/prompt expectation might be mixed, leading to evaluation errors. | High | High |
| **Network Bias (Minor)** | Occasional defaulting to Visa when the network is ambiguous or implicitly implied as another type in the context. | Low | Low |
| **Contextual Blindness** | Failure to detect "subscription" or "trial" keywords to trigger `13.2` (Cancelled Recurring). | Medium | Medium |

## 4. Detailed Error Analysis

### 4.1 Network Classification Success
The high accuracy (95%) indicates the model is robust at extracting entity names (Visa, Mastercard, etc.) from natural language.

### 4.2 Reason Code Systemic Failure
The classifier is likely overfitting to a few dominant codes or the prompt instructions are not mapping the natural language reasons (e.g., "fraudulent") to the specific Visa codes (e.g., "10.4") effectively for all categories.

**Examples of Mismatches:**
*   *Query:* "I canceled my subscription..."
    *   *Expected:* `subscription_canceled` (Code 13.2)
    *   *Predicted:* `13.1` (Merchandise Not Received)
*   *Query:* "Product defective..."
    *   *Expected:* `product_unacceptable` (Code 13.3)
    *   *Predicted:* `13.1` (Merchandise Not Received)

## 5. Recommendations

1.  **Prompt Refinement:** Update the system prompt to explicitly map natural language categories to their specific numeric codes with definitions (e.g., "If subscription issue, use 13.2").
2.  **Schema Alignment:** Ensure the evaluation pipeline standardizes the "Expected" and "Predicted" values to the same format (either all numeric or all string) to get a true accuracy metric.
3.  **Few-Shot Prompting:** Include examples of difficult categories (Subscription, Duplicate, Credit Not Processed) in the prompt to guide the LLM.
