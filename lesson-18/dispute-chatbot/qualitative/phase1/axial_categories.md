# Axial Coding Categories (Phase 1)

Based on open coding of synthetic conversation traces (`error_recovery_dialogues.json`, `escalation_dialogues.json`, `happy_path_dialogues.json`).

## Category 1: Network & System Reliability
**Codes:** `tool_timeout`, `retry_mechanism`, `recovery_success`
**Description:** Issues related to tool execution latency, network timeouts, and the system's ability to recover from transient failures.
**Observation:** The system demonstrates resilience via retry mechanisms, but timeouts are a frequent "failure" mode in the raw logs.

## Category 2: Evidence Complexity & Quality
**Codes:** `contradictory_evidence`, `complex_case_identification`
**Description:** Scenarios where gathered evidence is inconsistent, incomplete, or ambiguous, requiring higher-level reasoning or human intervention.
**Observation:** The agent correctly identifies when evidence doesn't add up (e.g., "contradictory"), triggering safeguards.

## Category 3: Escalation Workflow
**Codes:** `human_escalation`, `user_escalation_request`
**Description:** Patterns where the agent hands off control to a human, either due to user request or internal complexity thresholds.
**Observation:** Escalation is a "graceful failure" or "safety valve" rather than a catastrophic error.

## Category 4: Classification Accuracy
**Codes:** `successful_classification`, `successful_submission` (and potential `wrong_reason_code` implied)
**Description:** The correctness of assigning the dispute reason code (e.g., Fraud vs. PNR).
**Observation:** High success rate in "happy path" data; failures here would be critical blockers.

## Category 5: Fabrication & Hallucination (Anticipated)
**Codes:** (None observed in current sample, but critical for taxonomy)
**Description:** Agent generating details not present in source data.
**Observation:** Must be tracked as a zero-tolerance failure mode despite absence in current "well-behaved" synthetic traces.

