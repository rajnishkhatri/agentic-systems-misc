# SPIKE-003: CE 3.0 Transaction Matching

## Objective

Validate that the CE 3.0 (Compelling Evidence 3.0) matching algorithm correctly identifies qualifying prior transactions for fraud disputes under Visa rules.

## CE 3.0 Eligibility Criteria

For a fraud dispute (reason code 10.4) to qualify for CE 3.0 defense:

1. **Prior Transaction Count**: At least 2 prior undisputed transactions
2. **Time Window**: Within 120 days prior to the disputed transaction
3. **Matching Signals**: At least 2 of 4 signals must match:
   - IP Address
   - Device ID
   - Email Address
   - Shipping Address

## Test Results

| Metric | Result | Requirement | Status |
|--------|--------|-------------|--------|
| Match Rate | 100% | >95% | PASS |
| Test Cases | 50/50 | 50 cases | PASS |

### Test Case Distribution

| Case Type | Count | Expected Eligible | Description |
|-----------|-------|-------------------|-------------|
| Perfect Match | 10 | YES | 3+ txns, all 4 signals match |
| Partial Match | 10 | YES | 2+ txns, 2 signals match (IP + Device) |
| No History | 10 | NO | 0 prior transactions |
| Insufficient Signals | 10 | NO | 3 txns, only 1 signal matches |
| Expired Window | 10 | NO | 3 txns >120 days old |

## Implementation

### CE3Matcher Class

```python
class CE3Matcher:
    def match(self, disputed_txn: Transaction, history: List[Transaction]) -> Dict[str, Any]:
        """
        Returns:
            {
                "eligible": bool,
                "qualifying_transactions": [...],
                "count": int
            }
        """
```

### Matching Logic

1. Filter history to undisputed transactions only
2. Filter to transactions within 120-day window
3. Count matching signals between each historical transaction and disputed transaction
4. Require ≥2 matching signals per qualifying transaction
5. Require ≥2 total qualifying transactions for eligibility

## Usage

```bash
cd lesson-18/dispute-chatbot/spikes/SPIKE-003_ce3_matching
python match_ce3.py
```

### Sample Output

```
Running 50 synthetic test cases...

Match Rate: 100.0% (50/50)
SUCCESS: Match rate > 95%
```

## Files

- `match_ce3.py` - CE3Matcher implementation and test harness
- `README.md` - This documentation

## Integration Notes

The CE3Matcher should be integrated into the evidence gathering phase:

```python
# In workflow.py (EVIDENCE_GATHERING phase)
from spikes.SPIKE_003_ce3_matching.match_ce3 import CE3Matcher, Transaction

matcher = CE3Matcher()
result = matcher.match(
    disputed_txn=Transaction(...),
    history=fetch_transaction_history(merchant_id, cardholder_id)
)

if result["eligible"]:
    evidence_package["ce3_evidence"] = {
        "qualifying_transactions": result["qualifying_transactions"],
        "matching_signal_count": len(result["qualifying_transactions"][0]["matching_signals"])
    }
```

## Related

- [SPIKE-001: VROL Schema Validation](../SPIKE-001_vrol_schema/README.md) - Network payload structure
- [ADR-004: Network Translation Layer](../../design/ADRs/ADR-004_Network_Translation.md) - Adapter pattern for Visa/MC
