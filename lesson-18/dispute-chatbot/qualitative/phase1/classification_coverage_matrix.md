# Classification Coverage Matrix

**Total Test Cases:** 101

## Network: Amex

### Group: Authorization

| Reason Code | Category | Test Description Sample |
|---|---|---|
| **A01** | general | This transaction is incorrect. (Network: Amex) |
| **A02** | general | I am disputing this charge: No Valid Authorization (Network:... |
| **A08** | general | There is an issue with this payment. (Network: Amex) |


### Group: Cardholder Disputes

| Reason Code | Category | Test Description Sample |
|---|---|---|
| **C02** | credit_not_processed | Merchant promised a refund but I don't see it. (Network: Ame... |
| **C04** | credit_not_processed | Merchant promised a refund but I don't see it. (Network: Ame... |
| **C05** | credit_not_processed | Where is my credit? (Network: Amex) |
| **C08** | product_not_received | It's been weeks and I still haven't gotten my order. (Networ... |
| **C14** | duplicate | I was charged twice for the same thing. (Paid by Other Means... |
| **C18** | general | This transaction is incorrect. (Network: Amex) |
| **C28** | subscription_canceled | Recurring billing should have stopped. (Network: Amex) |
| **C31** | product_unacceptable | This is not what I ordered. (Network: Amex) |
| **C32** | product_unacceptable | The quality is terrible and I want a refund. (Network: Amex) |


### Group: Fraud

| Reason Code | Category | Test Description Sample |
|---|---|---|
| **F10** | fraudulent | I did not make this transaction. It is fraud. (Missing Impri... |
| **F14** | fraudulent | Unauthorized transaction on my account. (Network: Amex) |
| **F24** | fraudulent | My card was stolen and used for this charge. (Network: Amex) |
| **F29** | fraudulent | I don't recognize this charge at all. (Network: Amex) |
| **F30** | fraudulent | I don't recognize this charge at all. (Network: Amex) |
| **F31** | fraudulent | My card was stolen and used for this charge. (Network: Amex) |


### Group: Processing Errors

| Reason Code | Category | Test Description Sample |
|---|---|---|
| **P01** | general | This transaction is incorrect. (Network: Amex) |
| **P03** | general | I am disputing this charge: Credit Processed as Charge (Netw... |
| **P04** | general | This transaction is incorrect. (Network: Amex) |
| **P05** | general | I am disputing this charge: Incorrect Charge Amount (Network... |
| **P07** | general | I am disputing this charge: Late Submission (Network: Amex) |
| **P08** | duplicate | This is a duplicate charge. (Network: Amex) |
| **P22** | general | I am disputing this charge: Non-Matching Card Number (Networ... |
| **P23** | general | This transaction is incorrect. (Network: Amex) |


### Group: Retrieval Inquiry

| Reason Code | Category | Test Description Sample |
|---|---|---|
| **M01** | general | I am disputing this charge: Chargeback Authorization (Networ... |
| **R03** | general | There is an issue with this payment. (Network: Amex) |
| **R13** | general | I am disputing this charge: No Reply (Network: Amex) |


## Network: Discover

### Group: Authorization

| Reason Code | Category | Test Description Sample |
|---|---|---|
| **AT** | general | There is an issue with this payment. (Network: Discover) |


### Group: Cardholder Disputes

| Reason Code | Category | Test Description Sample |
|---|---|---|
| **AA** | unrecognized | I need more information about this. (Network: Discover) |
| **AP** | subscription_canceled | I ended my membership last month. (Network: Discover) |
| **AW** | general | This transaction is incorrect. (Network: Discover) |
| **CD** | general | This transaction is incorrect. (Network: Discover) |
| **CR** | credit_not_processed | Where is my credit? (Network: Discover) |
| **DA** | general | There is an issue with this payment. (Network: Discover) |
| **NF** | product_not_received | It's been weeks and I still haven't gotten my order. (Networ... |
| **RN2** | credit_not_processed | Merchant promised a refund but I don't see it. (Network: Dis... |


### Group: Fraud

| Reason Code | Category | Test Description Sample |
|---|---|---|
| **UA01** | fraudulent | I did not make this transaction. It is fraud. (Fraud - Card ... |
| **UA02** | fraudulent | My card was stolen and used for this charge. (Network: Disco... |
| **UA05** | fraudulent | Unauthorized transaction on my account. (Network: Discover) |
| **UA06** | fraudulent | I did not make this transaction. It is fraud. (Fraud - Chip ... |


### Group: Processing Errors

| Reason Code | Category | Test Description Sample |
|---|---|---|
| **DP** | duplicate | I see two identical transactions on my statement. (Network: ... |
| **EX** | general | I am disputing this charge: Expired Card (Network: Discover) |
| **IC** | general | This transaction is incorrect. (Network: Discover) |
| **IN** | general | There is an issue with this payment. (Network: Discover) |
| **LP** | general | There is an issue with this payment. (Network: Discover) |
| **NA** | general | There is an issue with this payment. (Network: Discover) |
| **NC** | general | There is an issue with this payment. (Network: Discover) |
| **PM** | duplicate | This is a duplicate charge. (Network: Discover) |
| **RG** | product_not_received | The package never arrived. (Network: Discover) |
| **RM** | product_unacceptable | It arrived broken. (Network: Discover) |


## Network: Mastercard

### Group: Authorization

| Reason Code | Category | Test Description Sample |
|---|---|---|
| **4807** | general | I am disputing this charge: Warning Bulletin File (Network: ... |
| **4808** | general | There is an issue with this payment. (Network: Mastercard) |
| **4812** | general | I am disputing this charge: Account Number Not on File (Netw... |


### Group: Cardholder Disputes

| Reason Code | Category | Test Description Sample |
|---|---|---|
| **4831** | general | This transaction is incorrect. (Network: Mastercard) |
| **4834** | duplicate | I see two identical transactions on my statement. (Network: ... |
| **4835** | fraudulent | I don't recognize this charge at all. (Network: Mastercard) |


### Group: Fraud

| Reason Code | Category | Test Description Sample |
|---|---|---|
| **4837** | fraudulent | Unauthorized transaction on my account. (Network: Mastercard... |
| **4840** | fraudulent | I don't recognize this charge at all. (Network: Mastercard) |
| **4841** | subscription_canceled | Recurring billing should have stopped. (Network: Mastercard) |
| **4842** | general | There is an issue with this payment. (Network: Mastercard) |
| **4846** | general | There is an issue with this payment. (Network: Mastercard) |
| **4849** | fraudulent | My card was stolen and used for this charge. (Network: Maste... |
| **4850** | general | This transaction is incorrect. (Network: Mastercard) |
| **4853** | general | This transaction is incorrect. (Network: Mastercard) |


### Group: Processing Errors

| Reason Code | Category | Test Description Sample |
|---|---|---|
| **4854** | general | This transaction is incorrect. (Network: Mastercard) |
| **4855** | product_not_received | The package never arrived. (Network: Mastercard) |
| **4857** | general | I am disputing this charge: Card-Activated Telephone Transac... |
| **4859** | general | There is an issue with this payment. (Network: Mastercard) |
| **4863** | fraudulent | My card was stolen and used for this charge. (Network: Maste... |
| **4870** | fraudulent | I don't recognize this charge at all. (Network: Mastercard) |
| **4871** | fraudulent | My card was stolen and used for this charge. (Network: Maste... |


## Network: Openapi_Gateway_Response

### Group: Other

| Reason Code | Category | Test Description Sample |
|---|---|---|
| **QUOTA_EXCEEDED** |  | I am disputing this charge:  (Network: Openapi_Gateway_Respo... |
| **UNAUTHORIZED** | fraudulent | I don't recognize this charge at all. (Network: Openapi_Gate... |


## Network: Paypal

### Group: Non Card Dispute

| Reason Code | Category | Test Description Sample |
|---|---|---|
| **ITEM_NOT_RECEIVED** | product_not_received | Tracking says delivered but I don't have it. (Network: Paypa... |


## Network: Visa

### Group: Authorization

| Reason Code | Category | Test Description Sample |
|---|---|---|
| **11.1** | general | This transaction is incorrect. (Network: Visa) |
| **11.2** | general | There is an issue with this payment. (Network: Visa) |
| **11.3** | general | There is an issue with this payment. (Network: Visa) |


### Group: Consumer Disputes

| Reason Code | Category | Test Description Sample |
|---|---|---|
| **13.1** | product_not_received | It's been weeks and I still haven't gotten my order. (Networ... |
| **13.2** | subscription_canceled | I ended my membership last month. (Network: Visa) |
| **13.3** | product_unacceptable | It arrived broken. (Network: Visa) |
| **13.4** | product_unacceptable | It arrived broken. (Network: Visa) |
| **13.5** | product_unacceptable | The quality is terrible and I want a refund. (Network: Visa) |
| **13.6** | credit_not_processed | I returned the item but haven't received my refund. (Credit ... |
| **13.7** | credit_not_processed | Merchant promised a refund but I don't see it. (Network: Vis... |
| **13.8** | general | This transaction is incorrect. (Network: Visa) |
| **13.9** | product_not_received | Tracking says delivered but I don't have it. (Network: Visa) |


### Group: Fraud

| Reason Code | Category | Test Description Sample |
|---|---|---|
| **10.1** | fraudulent | I did not make this transaction. It is fraud. (EMV Liability... |
| **10.2** | fraudulent | Unauthorized transaction on my account. (Network: Visa) |
| **10.3** | fraudulent | Unauthorized transaction on my account. (Network: Visa) |
| **10.4** | fraudulent | My card was stolen and used for this charge. (Network: Visa) |
| **10.5** | fraudulent | Unauthorized transaction on my account. (Network: Visa) |


### Group: Processing Errors

| Reason Code | Category | Test Description Sample |
|---|---|---|
| **12.1** | general | This transaction is incorrect. (Network: Visa) |
| **12.2** | general | There is an issue with this payment. (Network: Visa) |
| **12.3** | general | This transaction is incorrect. (Network: Visa) |
| **12.4** | general | This transaction is incorrect. (Network: Visa) |
| **12.5** | general | I am disputing this charge: Incorrect Amount (Network: Visa) |
| **12.6.1** | duplicate | I was charged twice for the same thing. (Duplicate Processin... |
| **12.6.2** | duplicate | This is a duplicate charge. (Network: Visa) |
| **12.7** | general | This transaction is incorrect. (Network: Visa) |

