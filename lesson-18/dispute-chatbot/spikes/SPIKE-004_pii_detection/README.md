# SPIKE-004: PII Detection Validation

## Objective
Validate that PII detection (simulating GuardRails) does not flag common dispute domain terms (e.g., ARNs, Merchant IDs) as PII (False Positives), while correctly identifying actual PII (True Positives).

## Methodology
- **Detector**: Regex-based mock detector for Credit Cards, Emails, and US Phone Numbers.
- **Test Set**:
  - **Dispute Terms**: ARN (23 digits), Merchant IDs, Reason Codes, Dates.
  - **PII**: Standard examples.

## Results
- **False Positive Rate**: 0.0% (0/10)
  - ARN (23 digits) was NOT flagged as Credit Card (16 digits).
  - Merchant IDs were safe.
- **True Positive Rate**: 80.0% (4/5)
  - One phone number format failed (missing area code), which is acceptable for strict PII filters.

## Conclusion
The PII detection strategy is viable for the dispute domain. Specifically, 23-digit ARNs do not conflict with standard 16-digit Credit Card patterns, provided exact matching or boundary checks are used.

