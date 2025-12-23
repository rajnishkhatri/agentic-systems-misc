# Natural Language Classification Analysis

**Date:** December 13, 2025
**Dataset:** `natural_language_classification.json` (303 cases)

## Executive Summary

To stress-test the Optimized Classification Flow (3-step funnel), we generated a "Natural Language" dataset containing 303 test cases across 3 personas:
1.  **Emotional:** Short, angry, urgent (e.g., "FRAUD! FIX NOW!").
2.  **Narrative:** Long, conversational, detailed (e.g., "So I went to the store...").
3.  **Ambiguous:** Vague, implicit (e.g., "I don't remember this").

The overall pass rate was **14.2%**, significantly lower than the ~95% seen with clean synthetic data. This highlights the gap between "textbook" disputes and real-world user behavior.

## Results by Persona

| Persona | Pass Rate | Key Failure Mode |
| :--- | :--- | :--- |
| **Narrative** | **24.8%** | **Distraction**: Model latches onto minor details (e.g., mentioning a "return" in a fraud story triggers "Credit Not Processed"). |
| **Emotional** | **11.9%** | **Perspective Gap**: Users scream "Fraud" for technical issues (e.g., "Why was I charged?" vs "No Valid Auth"). |
| **Ambiguous** | **5.9%** | **Overconfidence**: Vague inputs like "something odd" trigger specific codes with high confidence (0.85+) instead of asking for clarification. |

## Failure Taxonomy & Insights

### 1. Implicit Network Failure (Regex Limitation)
*   **Issue:** The current `classify.py` uses deterministic regex to identify the network.
*   **Scenario:** User says "my card" or "this charge".
*   **Result:** System defaults to `visa`. If the test case was `amex`, this counts as a FAIL, even if the reason code logic was perfect.
*   **Fix:** We need to prompt the user for the network if it's not explicitly stated.

### 2. User vs. Bank Perspective
*   **Issue:** Mismatch between user language and technical reason codes.
*   **Example:** Amex A02 is "No Valid Authorization" (Technical). A user experiences this as "I didn't authorize this" -> "Fraud" (10.4).
*   **Insight:** The model is arguably *correct* in classifying it as Fraud based on the user's intent. The "Golden Set" expectations for technical codes (like A01, A02) may be unrealistic for a chatbot to predict solely from a user complaint.

### 3. The "Ambiguity Gap"
*   **Issue:** The model is "trigger happy."
*   **Example:** Input: *"I noticed something odd."*
*   **Model:** Selects `10.4 Fraud` or `12.1 Late Presentment` with **0.85 confidence**.
*   **Risk:** We are confidently misclassifying users who just need to ask a question.
*   **Action:** We must implement a **Clarification Flow**. If confidence < 0.7 (or if input is vague), the bot should ask: *"Are you saying you didn't make this purchase, or is the amount wrong?"*

## Recommendations

1.  **Implement Clarification Flow:** Priority #1. The bot must detect ambiguity and ask follow-up questions.
2.  **Relax Network Matching:** If the network isn't found, the bot should ask explicitly: *"Which card is this for? (Visa, Amex, etc.)"* instead of defaulting.
3.  **Refine Golden Set:** For technical codes (A01, A02), the expected behavior should likely be "General/Uncertain" rather than a precise technical prediction, unless the user provides specific technical details.

