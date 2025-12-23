# Dispute Chatbot Failure Mode Taxonomy

| Failure Mode Title | Definition | Illustrative Examples |
| :--- | :--- | :--- |
| **Network Bias** | The classifier incorrectly identifies the payment network, often defaulting to a specific network (e.g., Visa) regardless of the user's input. | User input: "My **Mastercard** shows a transaction I didn't make." -> Classified as **Visa**. |
| **Reason Code Granularity** | The classifier selects a broad or incorrect reason code instead of a more specific one that better matches the dispute description. | User input: "I canceled my gym membership... but you guys keep charging me." -> Classified as **13.1 (Merchandise Not Received)** instead of **13.2 (Cancelled Recurring)**. |
| **Ambiguity Misclassification** | Vague or ambiguous queries are confidently classified into specific categories instead of reflecting low confidence or asking for clarification. | User input: "Charge error." -> Classified as **13.1 (Merchandise Not Received)** with high confidence. |
| **Sentiment Ignored** | The classifier fails to account for customer sentiment (e.g., frustration, confusion) which might imply different dispute urgencies or types, although this is secondary to the reason code. | (Hypothetical) Urgent fraud report treated with same priority/flow as a minor billing error. |
| **Contextual Blindness** | The classifier misses key context clues like "subscription", "recurring", or "trial" that should trigger specific reason codes. | User input: "This was supposed to be a free **trial**." -> Misses the "trial" context for specific reason codes. |

