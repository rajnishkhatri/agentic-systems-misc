# Session Summary: Natural Language Stress Testing & Analysis

## Overview
In this session, we shifted from template-based verification to **Natural Language Stress Testing** for the Optimized Classification Flow. The goal was to evaluate how well the 3-step funnel (Network -> Category -> Code) handles realistic, messy, and emotional user inputs compared to clean "textbook" examples.

## Key Activities

1.  **Dataset Generation (`generate_natural_language_dataset.py`)**
    *   Created a script using LLM generation to produce **303 diverse test cases**.
    *   **Structure:** 101 Reason Codes × 3 Personas:
        *   **Emotional:** Angry, urgent, typo-prone (e.g., "FRAUD! FIX NOW!").
        *   **Narrative:** Long, conversational, burying the lead.
        *   **Ambiguous:** Vague, implicit (e.g., "I don't remember this").

2.  **Execution & Validation (`test_natural_language_set.py`)**
    *   Ran the full suite of 303 cases against the current classification logic.
    *   **Result:** **14.2% Overall Pass Rate** (vs ~95% on clean data).
    *   **Breakdown:**
        *   Narrative: 24.8% (Highest)
        *   Emotional: 11.9%
        *   Ambiguous: 5.9% (Lowest)

3.  **Failure Analysis (`natural_language_analysis.md`)**
    *   Identified 3 core failure modes:
        1.  **Implicit Network Failure:** Deterministic regex fails when users don't name the network explicitly (e.g., "my card" vs "my Visa").
        2.  **Perspective Mismatch:** Users describe technical banking issues (e.g., "No Valid Auth") as "Fraud". The model sides with the user, but the test expected the technical code.
        3.  **Ambiguity Gap:** Vague inputs like "something odd" trigger high-confidence (0.85+) classifications instead of asking for clarification.

4.  **Reporting**
    *   Generated a detailed **HTML Report** (`natural_language_report.html`) to visualize the failures and specific examples.

## Key Insights
The low pass rate confirms that while the logic works for clear inputs, it is **brittle** against real-world ambiguity and user phrasing. The system is currently "trigger happy," making confident guesses on vague data rather than admitting uncertainty.

## Next Steps
1.  **Implement Clarification Flow:** Modify the Orchestrator to detect low confidence or ambiguity and ask follow-up questions (e.g., "Are you saying you didn't make this purchase, or is the amount wrong?").
2.  **Relax Network Matching:** Add a fallback step to ask the user for their card network if regex fails.
3.  **Refine Expectations:** Update the "Golden Set" to accept "Fraud" as a valid classification for user-reported unauthorized charges, even if the bank technical code differs.

