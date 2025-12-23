# Reason Codes Catalog (Dispute Schema)

**Generated:** `2025-12-12T12:53:08.939243+00:00`
**Scope:** `lesson-18/dispute-schema` (in-repo exhaustive)

## Summary

- **Total codes:** 101
- **Unmapped (non-canonical observed):** 1

### Counts by namespace

| namespace | count |
| --- | --- |
| amex | 29 |
| visa | 25 |
| discover | 23 |
| mastercard | 21 |
| openapi_gateway_response | 2 |
| paypal | 1 |

### Counts by unified category (`DisputeReason`)

| unified_category | count |
| --- | --- |
| general | 45 |
| fraudulent | 23 |
| credit_not_processed | 7 |
| duplicate | 7 |
| product_not_received | 7 |
| product_unacceptable | 6 |
| subscription_canceled | 4 |
| null | 1 |
| unrecognized | 1 |

### Counts by network-family bucket

| network_family | count |
| --- | --- |
| processing_errors | 33 |
| fraud | 23 |
| cardholder_disputes | 20 |
| authorization | 10 |
| consumer_disputes | 9 |
| retrieval_inquiry | 3 |
| other | 2 |
| non_card_dispute | 1 |

## Tables: Unified categories (`DisputeReason`)

### credit_not_processed

| namespace | code | network_family | description | source_type |
| --- | --- | --- | --- | --- |
| amex | C02 | cardholder_disputes | Credit Not Processed | canonical |
| amex | C04 | cardholder_disputes | Goods/Services Returned or Refused | canonical |
| amex | C05 | cardholder_disputes | Goods/Services Cancelled | canonical |
| discover | CR | cardholder_disputes | Cancelled Reservation | canonical |
| discover | RN2 | cardholder_disputes | Credit Not Received | canonical |
| visa | 13.6 | consumer_disputes | Credit Not Processed | canonical |
| visa | 13.7 | consumer_disputes | Cancelled Merchandise/Services | canonical |

### duplicate

| namespace | code | network_family | description | source_type |
| --- | --- | --- | --- | --- |
| amex | C14 | cardholder_disputes | Paid by Other Means | canonical |
| amex | P08 | processing_errors | Duplicate Charge | canonical |
| discover | DP | processing_errors | Duplicate Processing | canonical |
| discover | PM | processing_errors | Paid by Other Means | canonical |
| mastercard | 4834 | cardholder_disputes | Duplicate Processing | canonical |
| visa | 12.6.1 | processing_errors | Duplicate Processing | canonical |
| visa | 12.6.2 | processing_errors | Paid by Other Means | canonical |

### fraudulent

| namespace | code | network_family | description | source_type |
| --- | --- | --- | --- | --- |
| amex | F10 | fraud | Missing Imprint | canonical |
| amex | F14 | fraud | Missing Signature | canonical |
| amex | F24 | fraud | No Cardholder Authorization | canonical |
| amex | F29 | fraud | Card Not Present | canonical |
| amex | F30 | fraud | EMV Counterfeit | canonical |
| amex | F31 | fraud | EMV Lost/Stolen/Non-Received | canonical |
| discover | UA01 | fraud | Fraud - Card Present Transaction | canonical |
| discover | UA02 | fraud | Fraud - Card Not Present Transaction | canonical |
| discover | UA05 | fraud | Fraud - Chip Card Counterfeit Transaction | canonical |
| discover | UA06 | fraud | Fraud - Chip Card Lost/Stolen | canonical |
| mastercard | 4835 | cardholder_disputes | Card Not Present | canonical |
| mastercard | 4837 | fraud | No Cardholder Authorization | canonical |
| mastercard | 4840 | fraud | Fraudulent Processing of Transactions | canonical |
| mastercard | 4849 | fraud | Questionable Merchant Activity | canonical |
| mastercard | 4863 | processing_errors | Cardholder Does Not Recognize - Potential Fraud | canonical |
| mastercard | 4870 | processing_errors | Chip Liability Shift | canonical |
| mastercard | 4871 | processing_errors | Chip/PIN Liability Shift | canonical |
| openapi_gateway_response | UNAUTHORIZED | other |  | observed |
| visa | 10.1 | fraud | EMV Liability Shift Counterfeit Fraud | canonical |
| visa | 10.2 | fraud | EMV Liability Shift Non-Counterfeit Fraud | canonical |
| visa | 10.3 | fraud | Other Fraud - Card Present Environment | canonical |
| visa | 10.4 | fraud | Other Fraud - Card Absent Environment | canonical |
| visa | 10.5 | fraud | Visa Fraud Monitoring Program | canonical |

### general

| namespace | code | network_family | description | source_type |
| --- | --- | --- | --- | --- |
| amex | A01 | authorization | Charge Amount Exceeds Authorization Amount | canonical |
| amex | A02 | authorization | No Valid Authorization | canonical |
| amex | A08 | authorization | Authorization Approval Expired | canonical |
| amex | C18 | cardholder_disputes | Request for Copy Unfulfilled | canonical |
| amex | M01 | retrieval_inquiry | Chargeback Authorization | canonical |
| amex | P01 | processing_errors | Unassigned Card Number | canonical |
| amex | P03 | processing_errors | Credit Processed as Charge | canonical |
| amex | P04 | processing_errors | Charge Processed as Credit | canonical |
| amex | P05 | processing_errors | Incorrect Charge Amount | canonical |
| amex | P07 | processing_errors | Late Submission | canonical |
| amex | P22 | processing_errors | Non-Matching Card Number | canonical |
| amex | P23 | processing_errors | Currency Discrepancy | canonical |
| amex | R03 | retrieval_inquiry | Insufficient Reply | canonical |
| amex | R13 | retrieval_inquiry | No Reply | canonical |
| discover | AT | authorization | Authorization Noncompliance | canonical |
| discover | AW | cardholder_disputes | Altered Amount | canonical |
| discover | CD | cardholder_disputes | Credit/Debit Posted Incorrectly | canonical |
| discover | DA | cardholder_disputes | Declined Authorization | canonical |
| discover | EX | processing_errors | Expired Card | canonical |
| discover | IC | processing_errors | Illegible Card Number | canonical |
| discover | IN | processing_errors | Invalid Card Number | canonical |
| discover | LP | processing_errors | Late Presentment | canonical |
| discover | NA | processing_errors | No Authorization | canonical |
| discover | NC | processing_errors | Not Classified | canonical |
| mastercard | 4807 | authorization | Warning Bulletin File | canonical |
| mastercard | 4808 | authorization | Authorization-Related Chargeback | canonical |
| mastercard | 4812 | authorization | Account Number Not on File | canonical |
| mastercard | 4831 | cardholder_disputes | Transaction Amount Differs | canonical |
| mastercard | 4842 | fraud | Late Presentment | canonical |
| mastercard | 4846 | fraud | Correct Transaction Currency Code Not Provided | canonical |
| mastercard | 4850 | fraud | Installment Billing Dispute | canonical |
| mastercard | 4853 | fraud | Cardholder Dispute | canonical |
| mastercard | 4854 | processing_errors | Cardholder Dispute - Not Elsewhere Classified | canonical |
| mastercard | 4857 | processing_errors | Card-Activated Telephone Transaction | canonical |
| mastercard | 4859 | processing_errors | Addendum, No-show, or ATM Dispute | canonical |
| visa | 11.1 | authorization | Card Recovery Bulletin | canonical |
| visa | 11.2 | authorization | Declined Authorization | canonical |
| visa | 11.3 | authorization | No Authorization | canonical |
| visa | 12.1 | processing_errors | Late Presentment | canonical |
| visa | 12.2 | processing_errors | Incorrect Transaction Code | canonical |
| visa | 12.3 | processing_errors | Incorrect Currency | canonical |
| visa | 12.4 | processing_errors | Incorrect Account Number | canonical |
| visa | 12.5 | processing_errors | Incorrect Amount | canonical |
| visa | 12.7 | processing_errors | Invalid Data | canonical |
| visa | 13.8 | consumer_disputes | Original Credit Transaction Not Accepted | canonical |

### product_not_received

| namespace | code | network_family | description | source_type |
| --- | --- | --- | --- | --- |
| amex | C08 | cardholder_disputes | Goods/Services Not Received or Only Partially Received | canonical |
| discover | NF | cardholder_disputes | Non-Receipt of Cash from ATM | canonical |
| discover | RG | processing_errors | Non-Receipt of Goods or Services | canonical |
| mastercard | 4855 | processing_errors | Goods or Services Not Provided | canonical |
| paypal | ITEM_NOT_RECEIVED | non_card_dispute |  | observed |
| visa | 13.1 | consumer_disputes | Merchandise/Services Not Received | canonical |
| visa | 13.9 | consumer_disputes | Non-Receipt of Cash or Load Transaction Value | canonical |

### product_unacceptable

| namespace | code | network_family | description | source_type |
| --- | --- | --- | --- | --- |
| amex | C31 | cardholder_disputes | Goods/Services Not as Described | canonical |
| amex | C32 | cardholder_disputes | Goods/Services Damaged or Defective | canonical |
| discover | RM | processing_errors | Quality Discrepancy | canonical |
| visa | 13.3 | consumer_disputes | Not as Described or Defective Merchandise/Services | canonical |
| visa | 13.4 | consumer_disputes | Counterfeit Merchandise | canonical |
| visa | 13.5 | consumer_disputes | Misrepresentation | canonical |

### subscription_canceled

| namespace | code | network_family | description | source_type |
| --- | --- | --- | --- | --- |
| amex | C28 | cardholder_disputes | Cancelled Recurring Billing | canonical |
| discover | AP | cardholder_disputes | Cancelled Recurring Transaction | canonical |
| mastercard | 4841 | fraud | Cancelled Recurring Transaction | canonical |
| visa | 13.2 | consumer_disputes | Cancelled Recurring Transaction | canonical |

### unrecognized

| namespace | code | network_family | description | source_type |
| --- | --- | --- | --- | --- |
| discover | AA | cardholder_disputes | Does Not Recognize | canonical |

## Tables: Network-family buckets

### authorization

| namespace | code | unified_category | description | unmapped |
| --- | --- | --- | --- | --- |
| amex | A01 | general | Charge Amount Exceeds Authorization Amount | false |
| amex | A02 | general | No Valid Authorization | false |
| amex | A08 | general | Authorization Approval Expired | false |
| discover | AT | general | Authorization Noncompliance | false |
| mastercard | 4807 | general | Warning Bulletin File | false |
| mastercard | 4808 | general | Authorization-Related Chargeback | false |
| mastercard | 4812 | general | Account Number Not on File | false |
| visa | 11.1 | general | Card Recovery Bulletin | false |
| visa | 11.2 | general | Declined Authorization | false |
| visa | 11.3 | general | No Authorization | false |

### cardholder_disputes

| namespace | code | unified_category | description | unmapped |
| --- | --- | --- | --- | --- |
| amex | C02 | credit_not_processed | Credit Not Processed | false |
| amex | C04 | credit_not_processed | Goods/Services Returned or Refused | false |
| amex | C05 | credit_not_processed | Goods/Services Cancelled | false |
| amex | C08 | product_not_received | Goods/Services Not Received or Only Partially Received | false |
| amex | C14 | duplicate | Paid by Other Means | false |
| amex | C18 | general | Request for Copy Unfulfilled | false |
| amex | C28 | subscription_canceled | Cancelled Recurring Billing | false |
| amex | C31 | product_unacceptable | Goods/Services Not as Described | false |
| amex | C32 | product_unacceptable | Goods/Services Damaged or Defective | false |
| discover | AA | unrecognized | Does Not Recognize | false |
| discover | AP | subscription_canceled | Cancelled Recurring Transaction | false |
| discover | AW | general | Altered Amount | false |
| discover | CD | general | Credit/Debit Posted Incorrectly | false |
| discover | CR | credit_not_processed | Cancelled Reservation | false |
| discover | DA | general | Declined Authorization | false |
| discover | NF | product_not_received | Non-Receipt of Cash from ATM | false |
| discover | RN2 | credit_not_processed | Credit Not Received | false |
| mastercard | 4831 | general | Transaction Amount Differs | false |
| mastercard | 4834 | duplicate | Duplicate Processing | false |
| mastercard | 4835 | fraudulent | Card Not Present | false |

### consumer_disputes

| namespace | code | unified_category | description | unmapped |
| --- | --- | --- | --- | --- |
| visa | 13.1 | product_not_received | Merchandise/Services Not Received | false |
| visa | 13.2 | subscription_canceled | Cancelled Recurring Transaction | false |
| visa | 13.3 | product_unacceptable | Not as Described or Defective Merchandise/Services | false |
| visa | 13.4 | product_unacceptable | Counterfeit Merchandise | false |
| visa | 13.5 | product_unacceptable | Misrepresentation | false |
| visa | 13.6 | credit_not_processed | Credit Not Processed | false |
| visa | 13.7 | credit_not_processed | Cancelled Merchandise/Services | false |
| visa | 13.8 | general | Original Credit Transaction Not Accepted | false |
| visa | 13.9 | product_not_received | Non-Receipt of Cash or Load Transaction Value | false |

### fraud

| namespace | code | unified_category | description | unmapped |
| --- | --- | --- | --- | --- |
| amex | F10 | fraudulent | Missing Imprint | false |
| amex | F14 | fraudulent | Missing Signature | false |
| amex | F24 | fraudulent | No Cardholder Authorization | false |
| amex | F29 | fraudulent | Card Not Present | false |
| amex | F30 | fraudulent | EMV Counterfeit | false |
| amex | F31 | fraudulent | EMV Lost/Stolen/Non-Received | false |
| discover | UA01 | fraudulent | Fraud - Card Present Transaction | false |
| discover | UA02 | fraudulent | Fraud - Card Not Present Transaction | false |
| discover | UA05 | fraudulent | Fraud - Chip Card Counterfeit Transaction | false |
| discover | UA06 | fraudulent | Fraud - Chip Card Lost/Stolen | false |
| mastercard | 4837 | fraudulent | No Cardholder Authorization | false |
| mastercard | 4840 | fraudulent | Fraudulent Processing of Transactions | false |
| mastercard | 4841 | subscription_canceled | Cancelled Recurring Transaction | false |
| mastercard | 4842 | general | Late Presentment | false |
| mastercard | 4846 | general | Correct Transaction Currency Code Not Provided | false |
| mastercard | 4849 | fraudulent | Questionable Merchant Activity | false |
| mastercard | 4850 | general | Installment Billing Dispute | false |
| mastercard | 4853 | general | Cardholder Dispute | false |
| visa | 10.1 | fraudulent | EMV Liability Shift Counterfeit Fraud | false |
| visa | 10.2 | fraudulent | EMV Liability Shift Non-Counterfeit Fraud | false |
| visa | 10.3 | fraudulent | Other Fraud - Card Present Environment | false |
| visa | 10.4 | fraudulent | Other Fraud - Card Absent Environment | false |
| visa | 10.5 | fraudulent | Visa Fraud Monitoring Program | false |

### non_card_dispute

| namespace | code | unified_category | description | unmapped |
| --- | --- | --- | --- | --- |
| paypal | ITEM_NOT_RECEIVED | product_not_received |  | false |

### other

| namespace | code | unified_category | description | unmapped |
| --- | --- | --- | --- | --- |
| openapi_gateway_response | QUOTA_EXCEEDED |  |  | true |
| openapi_gateway_response | UNAUTHORIZED | fraudulent |  | false |

### processing_errors

| namespace | code | unified_category | description | unmapped |
| --- | --- | --- | --- | --- |
| amex | P01 | general | Unassigned Card Number | false |
| amex | P03 | general | Credit Processed as Charge | false |
| amex | P04 | general | Charge Processed as Credit | false |
| amex | P05 | general | Incorrect Charge Amount | false |
| amex | P07 | general | Late Submission | false |
| amex | P08 | duplicate | Duplicate Charge | false |
| amex | P22 | general | Non-Matching Card Number | false |
| amex | P23 | general | Currency Discrepancy | false |
| discover | DP | duplicate | Duplicate Processing | false |
| discover | EX | general | Expired Card | false |
| discover | IC | general | Illegible Card Number | false |
| discover | IN | general | Invalid Card Number | false |
| discover | LP | general | Late Presentment | false |
| discover | NA | general | No Authorization | false |
| discover | NC | general | Not Classified | false |
| discover | PM | duplicate | Paid by Other Means | false |
| discover | RG | product_not_received | Non-Receipt of Goods or Services | false |
| discover | RM | product_unacceptable | Quality Discrepancy | false |
| mastercard | 4854 | general | Cardholder Dispute - Not Elsewhere Classified | false |
| mastercard | 4855 | product_not_received | Goods or Services Not Provided | false |
| mastercard | 4857 | general | Card-Activated Telephone Transaction | false |
| mastercard | 4859 | general | Addendum, No-show, or ATM Dispute | false |
| mastercard | 4863 | fraudulent | Cardholder Does Not Recognize - Potential Fraud | false |
| mastercard | 4870 | fraudulent | Chip Liability Shift | false |
| mastercard | 4871 | fraudulent | Chip/PIN Liability Shift | false |
| visa | 12.1 | general | Late Presentment | false |
| visa | 12.2 | general | Incorrect Transaction Code | false |
| visa | 12.3 | general | Incorrect Currency | false |
| visa | 12.4 | general | Incorrect Account Number | false |
| visa | 12.5 | general | Incorrect Amount | false |
| visa | 12.6.1 | duplicate | Duplicate Processing | false |
| visa | 12.6.2 | duplicate | Paid by Other Means | false |
| visa | 12.7 | general | Invalid Data | false |

### retrieval_inquiry

| namespace | code | unified_category | description | unmapped |
| --- | --- | --- | --- | --- |
| amex | M01 | general | Chargeback Authorization | false |
| amex | R03 | general | Insufficient Reply | false |
| amex | R13 | general | No Reply | false |

## Observed-only codes needing mapping

| namespace | code | network_family | description | sources |
| --- | --- | --- | --- | --- |
| openapi_gateway_response | QUOTA_EXCEEDED | other |  | lesson-18/dispute-schema/aws-integration/openapi.yaml |
