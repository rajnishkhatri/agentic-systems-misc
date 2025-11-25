# Bank Dispute Transaction Sequence

Reference use case: Jordan contacts the bank’s AI assistant to dispute a suspicious $450 charge from “Metro Electronics.” This file narrates the 19 interactions represented in `context_engineering_sequence.mmd`, grounded in a regulated dispute-workflow.

1. **Customer submission** – Jordan opens a secure chat, describing the unauthorized debit and attaching a screenshot of the statement.
2. **Session logging** – The session service appends the turn to the immutable event log and updates scratchpad fields such as `dispute_amount=450` and `merchant="Metro Electronics"`.
3. **State handoff** – It shares the refreshed event/state snapshot with the context orchestrator so downstream components see the latest facts.
4. **Session slicing** – The orchestrator retrieves the protected slices of conversation (initial complaint, authentication confirmation, compliance notices) needed for prompt assembly.
5. **Memory request** – In parallel, it asks the retrieval engine for Jordan-specific memories (previous disputes, travel history, communication preferences).
6. **Store query** – The retrieval engine runs semantic and graph searches against the long-term memory store.
7. **Candidate memories** – The store returns items such as “Filed fraud claim in 2024,” “Card has travel restrictions,” “Prefers SMS follow-ups.”
8. **Filtering** – Retrieval keeps only the most relevant memories (recent fraud history, SMS preference) based on relevance, recency, and importance.
9. **Policy enrichment** – The orchestrator fetches RAG snippets (latest dispute procedures, Metro Electronics risk bulletin) and merges any required tool outputs.
10. **LLM invocation** – With curated session turns, injected memories, and policy excerpts, the orchestrator calls the LLM/tool stack.
11. **Reasoning + tool calls** – The LLM checks internal fraud services (merchant risk score, device fingerprint) and drafts a personalized response outlining temporary credit and card-freeze options.
12. **Customer response** – The orchestrator delivers the plan to Jordan, confirming that a provisional credit is in place and next steps are underway.
13. **Session persistence** – It logs the outgoing message and updates session state (`case_id=FD-88341`, `temporary_credit=true`, `notified_channel=SMS`).
14. **Memory trigger** – Because fraud cases mandate archival, the orchestrator signals the memory manager to start the extraction/consolidation pipeline.
15. **Context fetch for memory** – The memory manager retrieves the relevant conversation slice and state deltas from the session service.
16. **Extraction** – It isolates new insights: “Metro Electronics repeatedly disputed,” “Customer insists on SMS confirmations,” “Automatic credits reduce frustration.”
17. **Consolidation** – These insights merge with prior memories, updating confidence on existing fraud-related entries and removing stale contradicting data if needed.
18. **Upsert** – The refined memories, along with provenance pointing to case `FD-88341`, are stored in the vector/graph memory database.
19. **Next-turn readiness** – During Jordan’s next interaction (e.g., status check), the retrieval engine can instantly surface these memories so the assistant proactively addresses loyalty, fraud, and notification expectations.

This narrative mirrors the numbered lifelines in the sequence diagram, offering compliance teams and product stakeholders a readable story that traces how context, memory, and orchestration collaborate during a sensitive dispute workflow.






