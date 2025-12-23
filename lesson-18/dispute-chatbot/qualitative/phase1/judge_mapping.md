# LLM Judge Mapping (Phase 1)

Based on the [Failure Taxonomy](failure_taxonomy.md), the following mapping defines which LLM Judge is responsible for detecting specific failure modes and the required thresholds.

| Failure Mode Category | Specific Failure | Responsible Judge | Threshold | Blocking? | Rationale |
|-----------------------|------------------|-------------------|-----------|-----------|-----------|
| **Evidence Integrity** | Evidence Fabrication / Hallucination | `FabricationDetectionJudge` | **0.95** | **YES** | Critical severity. Any invented detail invalidates the submission. Requires high precision. |
| **Evidence Quality** | Evidence Contradiction / Incompleteness | `EvidenceQualityJudge` | **0.80** | **YES** | Ensures evidence package is sufficient to win the dispute. Score < 0.8 implies gaps or contradictions. |
| **Classification** | Wrong Reason Code | `DisputeValidityJudge` | **0.70** | NO (Warning) | Checks if the defense strategy makes sense. Warning allows human to override if edge case. |
| **Compliance** | PII / PCI Data Leak | `GuardRails` (Regex/NLP) | **PASS/FAIL** | **YES** | Zero tolerance for PAN/PII in logs or output. |
| **Compliance** | Deadline Miss / Arithmetic Error | `GuardRails` (Logic) | **PASS/FAIL** | **YES** | Regulatory deadlines (14 days) are hard constraints. |

## Implementation Notes

1.  **Fabrication Detection**: This judge compares the Agent's output *strictly* against the provided Context/Evidence. Any claim in Output not supported by Context = Fail.
2.  **Evidence Quality**: This judge evaluates the *strength* of the evidence. "Contradictory evidence" (Failure Mode 2) should result in a low quality score.
3.  **Blocking Behavior**:
    - If `Fabrication` or `GuardRails` fail -> **Hard Block**, automated rejection/retry.
    - If `EvidenceQuality` fails -> **Hard Block**, request more info or escalate.
    - If `DisputeValidity` fails -> **Soft Block**, warn user/agent but allow proceed with caution.

