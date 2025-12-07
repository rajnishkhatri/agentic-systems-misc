# Gen AI Dispute Resolution System - AWS Architecture Design

## Executive Summary

A comprehensive Gen AI-based dispute resolution system utilizing AWS ecosystem with event-driven architecture. The system modernizes dispute handling through three parallel tracks:

1. **Conversational AI Intake** - Mobile-first interfaces with intelligent escalation
2. **Intelligent Document Processing** - Converting unstructured evidence to structured case data
3. **ML Fraud Detection & Auto-Adjudication** - Real-time fraud scoring and automated decisions

All connected through event-driven architecture providing real-time visibility and synchronization with core banking and card network systems.

---

## High-Level Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              EVENT-DRIVEN BACKBONE                                       │
│  ┌─────────────────┐    ┌──────────────────┐    ┌─────────────────────────────────────┐ │
│  │ Amazon          │◄──►│ AWS Step         │◄──►│ Amazon Kinesis Data Streams         │ │
│  │ EventBridge     │    │ Functions        │    │ (Real-time event streaming)         │ │
│  └────────┬────────┘    └────────┬─────────┘    └────────────────┬────────────────────┘ │
│           │                      │                               │                       │
└───────────┼──────────────────────┼───────────────────────────────┼───────────────────────┘
            │                      │                               │
┌───────────▼──────────┐ ┌────────▼─────────┐ ┌───────────────────▼────────────────────────┐
│  TRACK 1: INTAKE     │ │ TRACK 2: IDP     │ │ TRACK 3: ML FRAUD/AUTO-ADJUDICATION       │
│  (Conversational AI) │ │ (Document Proc)  │ │                                            │
└──────────────────────┘ └──────────────────┘ └────────────────────────────────────────────┘
```

---

## TRACK 1: Conversational AI Intake & Mobile-First Interfaces

### Components

| Service | Purpose |
|---------|---------|
| **Amazon Connect** | Omnichannel contact center for voice/chat intake |
| **Amazon Lex V2** | Intent recognition, slot filling for dispute categories |
| **Amazon Bedrock Agents** | Orchestrate complex dispute intake with Claude/Titan FMs |
| **Amazon Q in Connect** | Gen AI-powered agent assist during escalations |
| **AWS Amplify** | Mobile-first app framework (iOS/Android/Web) |
| **API Gateway + Lambda** | RESTful & WebSocket APIs for mobile intake |
| **Amazon Cognito** | Authentication with MFA for banking-grade security |

### Intake Flow Architecture

```
Mobile App/Web ──► API Gateway ──► Lambda ──► Bedrock Agent ──► EventBridge
     │                                              │
     │                                              ▼
     │                                    ┌─────────────────┐
     └──────────► Amazon Connect ────────►│  Amazon Lex V2  │
                        │                 │  (Intent: Dispute│
                        │                 │   Category,      │
                        ▼                 │   Transaction ID,│
                 ┌──────────────┐         │   Amount, Date)  │
                 │ Amazon Q in  │         └────────┬─────────┘
                 │ Connect      │                  │
                 │ (Agent Assist)│                 ▼
                 └──────────────┘         ┌─────────────────────┐
                        │                 │ Bedrock Agent       │
                        │                 │ - Gather evidence   │
                        │                 │ - Validate details  │
                        │                 │ - Create case       │
                        │                 │ - Trigger workflow  │
                        ▼                 └─────────┬───────────┘
                 Human Agent (if escalated)         │
                        │                           ▼
                        └────────────────► EventBridge (DisputeCreated)
```

### Escalation Path Design

| Level | Trigger | Target Resolution |
|-------|---------|-------------------|
| **Self-Service** (80% target) | Default path | Bedrock Agent handles full intake |
| **Soft Escalation** | Complexity score > threshold | Gen AI suggests human review |
| **Hard Escalation** | Customer frustration, high-value (>$10K), fraud flags, explicit request | Human agent takeover |

### Bedrock Agent Action Schema

```yaml
actions:
  - name: "createDisputeCase"
    api: POST /disputes
    params: [transactionId, amount, category, description]
    description: "Create new dispute case in system"

  - name: "lookupTransaction"
    api: GET /transactions/{id}
    description: "Retrieve transaction details from core banking"

  - name: "requestDocumentUpload"
    api: POST /documents/presigned-url
    description: "Generate secure upload URL for evidence"

  - name: "escalateToAgent"
    api: POST /escalations
    description: "Handoff with full context to human agent"

  - name: "checkDisputeStatus"
    api: GET /disputes/{id}/status
    description: "Get current case status and timeline"
```

### Amazon Lex V2 Intent Configuration

```json
{
  "intents": [
    {
      "name": "FileDispute",
      "slots": [
        {"name": "TransactionId", "type": "AMAZON.AlphaNumeric"},
        {"name": "DisputeCategory", "type": "DisputeCategoryType"},
        {"name": "DisputeAmount", "type": "AMAZON.Number"},
        {"name": "TransactionDate", "type": "AMAZON.Date"},
        {"name": "MerchantName", "type": "AMAZON.FreeFormInput"}
      ],
      "sampleUtterances": [
        "I want to dispute a charge",
        "There's a fraudulent transaction on my account",
        "I didn't authorize this purchase",
        "I need to report unauthorized activity"
      ]
    },
    {
      "name": "CheckDisputeStatus",
      "slots": [
        {"name": "CaseNumber", "type": "AMAZON.AlphaNumeric"}
      ]
    },
    {
      "name": "SpeakToAgent",
      "description": "Escalation intent for human handoff"
    }
  ],
  "slotTypes": [
    {
      "name": "DisputeCategoryType",
      "values": [
        "fraud", "unauthorized", "duplicate",
        "merchandise_not_received", "merchandise_not_as_described",
        "billing_error", "subscription_cancellation"
      ]
    }
  ]
}
```

---

## TRACK 2: Intelligent Document Processing (IDP)

### Components

| Service | Purpose |
|---------|---------|
| **Amazon Textract** | OCR for receipts, statements, forms |
| **Amazon Textract Queries** | Targeted extraction (transaction date, merchant, amount) |
| **Amazon Comprehend** | Entity extraction, custom classification |
| **Amazon Bedrock (Claude)** | Document summarization, reasoning over evidence |
| **Amazon S3** | Document storage with lifecycle policies |
| **Amazon OpenSearch** | Full-text search across case documents |

### IDP Pipeline Architecture

```
Document Upload ──► S3 (Trigger) ──► Lambda ──► Textract
                                                   │
                    ┌──────────────────────────────┘
                    ▼
             ┌─────────────────┐
             │ Classification  │◄── Comprehend Custom Classifier
             │ (Receipt, Bank  │    (Document Type Model)
             │  Statement,     │
             │  Contract, etc.)│
             └────────┬────────┘
                      │
                      ▼
             ┌─────────────────┐
             │ Extraction      │◄── Textract Queries + Forms/Tables
             │ - Date          │
             │ - Amount        │
             │ - Merchant      │
             │ - Account #     │
             └────────┬────────┘
                      │
                      ▼
             ┌─────────────────┐
             │ Enrichment      │◄── Amazon Bedrock (Claude)
             │ - Summarization │    - Reason over inconsistencies
             │ - Validation    │    - Flag suspicious patterns
             │ - Normalization │    - Generate evidence summary
             └────────┬────────┘
                      │
                      ▼
             EventBridge ──► "DocumentProcessed" event
                      │
                      ▼
             DynamoDB (Structured Case Data) + OpenSearch (Full-text)
```

### Document Types & Extraction Targets

| Document Type | Key Fields Extracted | Textract Feature |
|---------------|---------------------|------------------|
| Bank Statement | Transaction date, description, amount, balance | Tables + Queries |
| Receipt | Merchant name, date, items, total, payment method | Analyze Expense |
| Shipping Confirmation | Carrier, tracking #, delivery date, signature | Queries |
| Contract/Terms | Refund policy, terms, dates | Forms + Queries |
| Correspondence | Date, parties, key claims | Forms |
| ID Documents | Name, address, ID number | Analyze ID |

### Textract Query Examples

```python
DISPUTE_DOCUMENT_QUERIES = [
    {"Text": "What is the transaction date?", "Alias": "TRANSACTION_DATE"},
    {"Text": "What is the transaction amount?", "Alias": "TRANSACTION_AMOUNT"},
    {"Text": "What is the merchant name?", "Alias": "MERCHANT_NAME"},
    {"Text": "What is the card number (last 4 digits)?", "Alias": "CARD_LAST_FOUR"},
    {"Text": "What is the authorization code?", "Alias": "AUTH_CODE"},
    {"Text": "What is the delivery date?", "Alias": "DELIVERY_DATE"},
    {"Text": "What is the tracking number?", "Alias": "TRACKING_NUMBER"},
    {"Text": "What is the refund policy?", "Alias": "REFUND_POLICY"}
]
```

### Bedrock Document Processing Prompts

```python
# Evidence summarization prompt
EVIDENCE_SUMMARY_PROMPT = """
Analyze the following extracted document data for a dispute case:

Document Type: {document_type}
Extracted Data:
{extracted_data}

Provide a JSON response with:
{{
  "summary": "2-3 sentence summary of key evidence",
  "relevance_score": 1-10 (how relevant to the dispute claim),
  "key_facts": ["fact1", "fact2", ...],
  "inconsistencies": ["any contradictions or red flags"],
  "missing_information": ["what additional docs might help"],
  "authenticity_concerns": ["any signs of tampering or forgery"]
}}
"""

# Cross-document reasoning prompt
CROSS_DOCUMENT_ANALYSIS_PROMPT = """
Given multiple evidence documents for dispute case {case_id}:

Customer Claim: {claim_description}
Disputed Amount: {amount}
Dispute Category: {category}

Documents:
{documents_json}

Analyze and determine:
{{
  "claim_supported": true/false,
  "confidence_level": "high" | "medium" | "low",
  "supporting_evidence": ["list of supporting facts"],
  "contradicting_evidence": ["list of contradictions"],
  "timeline_analysis": "narrative of events based on documents",
  "recommendation": "approve" | "deny" | "need_more_info",
  "reasoning": "explanation of recommendation"
}}
"""
```

### Comprehend Custom Classifier Training

```python
# Document classification categories
DOCUMENT_CATEGORIES = [
    "BANK_STATEMENT",
    "CREDIT_CARD_STATEMENT",
    "RECEIPT",
    "INVOICE",
    "SHIPPING_CONFIRMATION",
    "DELIVERY_PROOF",
    "CONTRACT",
    "TERMS_OF_SERVICE",
    "EMAIL_CORRESPONDENCE",
    "CHAT_TRANSCRIPT",
    "PHOTO_EVIDENCE",
    "ID_DOCUMENT",
    "OTHER"
]

# Training data format (CSV)
# document_text, category
# "Transaction Date: 01/15/2024...", BANK_STATEMENT
# "Thank you for your purchase at...", RECEIPT
```

---

## TRACK 3: ML Fraud Detection & Auto-Adjudication

### Components

| Service | Purpose |
|---------|---------|
| **Amazon SageMaker** | Train/deploy fraud models, XGBoost/Neural Nets |
| **SageMaker Real-time Inference** | Sub-100ms fraud scoring |
| **SageMaker Feature Store** | Centralized feature repository |
| **Amazon A2I** | Human-in-the-loop for uncertain predictions |
| **Amazon Bedrock** | Explainable decision generation |

### Fraud Detection Architecture

```
Transaction Event ──► API Gateway ──► Lambda ──► SageMaker Endpoint
                                                        │
        ┌───────────────────────────────────────────────┘
        │
        ▼
┌───────────────────┐
│ Feature Store     │◄── Historical features
│ - Velocity        │    (customer behavior,
│ - Amount patterns │     merchant patterns,
│ - Device signals  │     device fingerprints)
│ - Merchant risk   │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│ Fraud Score       │
│ (0.0 - 1.0)       │
└────────┬──────────┘
         │
         ├─── Score < 0.3 ──► Auto-approve (legitimate)
         │
         ├─── 0.3 ≤ Score < 0.7 ──► Human Review Queue (A2I)
         │
         └─── Score ≥ 0.7 ──► Auto-flag + Investigation
```

### Feature Engineering

```python
# SageMaker Feature Store - Feature Groups
CUSTOMER_FEATURES = {
    "feature_group_name": "dispute-customer-features",
    "features": [
        {"name": "customer_id", "type": "String"},
        {"name": "account_age_days", "type": "Integral"},
        {"name": "total_disputes_lifetime", "type": "Integral"},
        {"name": "disputes_last_30_days", "type": "Integral"},
        {"name": "disputes_last_90_days", "type": "Integral"},
        {"name": "dispute_win_rate", "type": "Fractional"},
        {"name": "avg_dispute_amount", "type": "Fractional"},
        {"name": "account_balance_avg_30d", "type": "Fractional"},
        {"name": "transaction_frequency_30d", "type": "Integral"},
        {"name": "unique_merchants_30d", "type": "Integral"}
    ]
}

TRANSACTION_FEATURES = {
    "feature_group_name": "dispute-transaction-features",
    "features": [
        {"name": "transaction_id", "type": "String"},
        {"name": "amount", "type": "Fractional"},
        {"name": "merchant_category_code", "type": "String"},
        {"name": "merchant_risk_score", "type": "Fractional"},
        {"name": "is_card_present", "type": "Integral"},
        {"name": "is_recurring", "type": "Integral"},
        {"name": "days_since_transaction", "type": "Integral"},
        {"name": "hour_of_day", "type": "Integral"},
        {"name": "day_of_week", "type": "Integral"},
        {"name": "distance_from_home", "type": "Fractional"},
        {"name": "device_fingerprint_match", "type": "Integral"}
    ]
}
```

### ML Model Portfolio

| Model | Algorithm | Purpose | Latency Target | Training Data |
|-------|-----------|---------|----------------|---------------|
| Fraud Scorer | XGBoost/LightGBM | Real-time fraud probability | <50ms | Historical disputes with outcomes |
| Transaction Classifier | Neural Network | Dispute category prediction | <100ms | Labeled dispute categories |
| Document Authenticity | CNN/Vision | Detect doctored evidence | <500ms | Authentic vs. manipulated docs |
| Claim Validator | Bedrock Claude | Cross-reference evidence | <2s | Case summaries + decisions |

### Auto-Adjudication Decision Engine

```
                    ┌─────────────────────────────────────┐
                    │         DECISION ORCHESTRATOR       │
                    │         (Step Functions)            │
                    └───────────────┬─────────────────────┘
                                    │
         ┌──────────────────────────┼──────────────────────────┐
         ▼                          ▼                          ▼
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│ FRAUD SCORE     │      │ POLICY ENGINE   │      │ DOCUMENT        │
│ (SageMaker)     │      │ (Lambda/Rules)  │      │ EVIDENCE SCORE  │
│                 │      │                 │      │ (Bedrock)       │
│ - Transaction   │      │ - Reg E limits  │      │                 │
│   anomaly       │      │ - Visa/MC rules │      │ - Evidence      │
│ - Behavior      │      │ - Bank policies │      │   completeness  │
│   deviation     │      │ - Amount thresh │      │ - Consistency   │
└────────┬────────┘      └────────┬────────┘      └────────┬────────┘
         │                        │                        │
         └────────────────────────┼────────────────────────┘
                                  ▼
                    ┌─────────────────────────────────────┐
                    │      DECISION MATRIX                │
                    └───────────────┬─────────────────────┘
                                    │
                                    ▼
                    ┌─────────────────────────────────────┐
                    │  BEDROCK: Generate Explanation     │
                    │  (Customer-facing decision letter) │
                    └─────────────────────────────────────┘
```

### Decision Matrix Rules

```python
DECISION_RULES = {
    "auto_approve": {
        "conditions": [
            "fraud_score < 0.3",
            "evidence_score > 0.8",
            "amount <= 500",
            "first_dispute_in_30_days == True",
            "customer_tenure_days > 365",
            "dispute_category in ['merchandise_not_received', 'duplicate_charge']"
        ],
        "action": "AUTO_APPROVE",
        "provisional_credit": True,
        "sla_days": 1
    },
    "auto_deny": {
        "conditions": [
            "fraud_score > 0.85",
            "evidence_contradicts_claim == True",
            "known_fraud_pattern == True"
        ],
        "action": "AUTO_DENY",
        "requires_explanation": True,
        "appeal_eligible": True
    },
    "human_review": {
        "conditions": [
            "0.3 <= fraud_score <= 0.85",
            "amount > 500",
            "evidence_incomplete == True",
            "complex_dispute_category == True"
        ],
        "action": "ROUTE_TO_HUMAN",
        "priority": "calculated_from_amount_and_sla",
        "sla_days": 10
    }
}
```

### Amazon A2I Human Review Workflow

```json
{
  "HumanLoopConfig": {
    "WorkteamArn": "arn:aws:sagemaker:us-east-1:123456789:workteam/dispute-reviewers",
    "HumanTaskUiArn": "arn:aws:sagemaker:us-east-1:123456789:human-task-ui/dispute-review-ui",
    "TaskTitle": "Review Dispute Case",
    "TaskDescription": "Review dispute evidence and make adjudication decision",
    "TaskCount": 1,
    "TaskTimeLimitInSeconds": 3600,
    "TaskAvailabilityLifetimeInSeconds": 86400
  },
  "HumanLoopActivationConditions": {
    "Conditions": [
      {
        "ConditionType": "ConfidenceThreshold",
        "ConditionParameters": {
          "ConfidenceThreshold": 0.7
        }
      }
    ]
  }
}
```

---

## EVENT-DRIVEN ARCHITECTURE BACKBONE

### Amazon EventBridge Event Schemas

```json
{
  "DisputeCreated": {
    "source": "dispute.intake",
    "detail-type": "NewDispute",
    "detail": {
      "disputeId": "string",
      "customerId": "string",
      "transactionId": "string",
      "amount": "number",
      "category": "enum[fraud, service, quality, billing, unauthorized]",
      "channel": "enum[mobile, web, voice, chat]",
      "priority": "enum[high, medium, low]",
      "createdAt": "ISO8601 timestamp",
      "metadata": {
        "deviceId": "string",
        "ipAddress": "string",
        "userAgent": "string"
      }
    }
  },

  "DocumentProcessed": {
    "source": "dispute.idp",
    "detail-type": "DocumentReady",
    "detail": {
      "disputeId": "string",
      "documentId": "string",
      "documentType": "string",
      "s3Location": "string",
      "extractedData": "object",
      "confidenceScore": "number",
      "processingTimeMs": "number"
    }
  },

  "FraudScoreCalculated": {
    "source": "dispute.fraud",
    "detail-type": "FraudAssessment",
    "detail": {
      "disputeId": "string",
      "fraudScore": "number",
      "riskFactors": ["array of risk indicators"],
      "recommendation": "enum[approve, review, deny]",
      "modelVersion": "string",
      "featureImportance": "object"
    }
  },

  "DecisionRendered": {
    "source": "dispute.adjudication",
    "detail-type": "CaseDecision",
    "detail": {
      "disputeId": "string",
      "decision": "enum[approved, denied, partial, pending]",
      "creditAmount": "number",
      "reason": "string",
      "automatedDecision": "boolean",
      "reviewerId": "string (if human)",
      "regulatoryBasis": "string"
    }
  },

  "NetworkSubmissionCompleted": {
    "source": "dispute.network",
    "detail-type": "ChargebackSubmitted",
    "detail": {
      "disputeId": "string",
      "network": "enum[visa, mastercard, amex, discover]",
      "chargebackId": "string",
      "reasonCode": "string",
      "submissionStatus": "string",
      "representmentDeadline": "ISO8601 timestamp"
    }
  }
}
```

### EventBridge Rules Configuration

```json
{
  "Rules": [
    {
      "Name": "route-new-disputes-to-workflow",
      "EventPattern": {
        "source": ["dispute.intake"],
        "detail-type": ["NewDispute"]
      },
      "Targets": [
        {
          "Id": "dispute-workflow-sfn",
          "Arn": "arn:aws:states:us-east-1:123456789:stateMachine:DisputeWorkflow"
        }
      ]
    },
    {
      "Name": "high-value-dispute-alert",
      "EventPattern": {
        "source": ["dispute.intake"],
        "detail-type": ["NewDispute"],
        "detail": {
          "amount": [{"numeric": [">=", 10000]}]
        }
      },
      "Targets": [
        {
          "Id": "alert-sns",
          "Arn": "arn:aws:sns:us-east-1:123456789:high-value-disputes"
        }
      ]
    },
    {
      "Name": "document-to-idp-pipeline",
      "EventPattern": {
        "source": ["aws.s3"],
        "detail-type": ["Object Created"],
        "detail": {
          "bucket": {"name": ["dispute-evidence-bucket"]}
        }
      },
      "Targets": [
        {
          "Id": "idp-lambda",
          "Arn": "arn:aws:lambda:us-east-1:123456789:function:IDPProcessor"
        }
      ]
    }
  ]
}
```

### AWS Step Functions Workflow Definition (ASL)

```json
{
  "Comment": "Dispute Resolution Workflow",
  "StartAt": "ValidateIntake",
  "States": {
    "ValidateIntake": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:us-east-1:123456789:function:ValidateDispute",
      "Next": "ParallelProcessing",
      "Catch": [
        {
          "ErrorEquals": ["ValidationError"],
          "Next": "RejectInvalidDispute"
        }
      ]
    },

    "ParallelProcessing": {
      "Type": "Parallel",
      "Branches": [
        {
          "StartAt": "ProcessDocuments",
          "States": {
            "ProcessDocuments": {
              "Type": "Task",
              "Resource": "arn:aws:lambda:us-east-1:123456789:function:IDPOrchestrator",
              "End": true
            }
          }
        },
        {
          "StartAt": "CalculateFraudScore",
          "States": {
            "CalculateFraudScore": {
              "Type": "Task",
              "Resource": "arn:aws:sagemaker:us-east-1:123456789:endpoint/fraud-scorer",
              "End": true
            }
          }
        },
        {
          "StartAt": "LookupCustomerHistory",
          "States": {
            "LookupCustomerHistory": {
              "Type": "Task",
              "Resource": "arn:aws:lambda:us-east-1:123456789:function:CustomerHistoryLookup",
              "End": true
            }
          }
        }
      ],
      "Next": "AggregateResults"
    },

    "AggregateResults": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:us-east-1:123456789:function:AggregateDecisionInputs",
      "Next": "MakeDecision"
    },

    "MakeDecision": {
      "Type": "Choice",
      "Choices": [
        {
          "Variable": "$.recommendation",
          "StringEquals": "AUTO_APPROVE",
          "Next": "AutoApprove"
        },
        {
          "Variable": "$.recommendation",
          "StringEquals": "AUTO_DENY",
          "Next": "AutoDeny"
        }
      ],
      "Default": "HumanReview"
    },

    "AutoApprove": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:us-east-1:123456789:function:ProcessApproval",
      "Next": "IssueProvisionalCredit"
    },

    "IssueProvisionalCredit": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:us-east-1:123456789:function:IssueCredit",
      "Next": "SubmitToNetwork"
    },

    "AutoDeny": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:us-east-1:123456789:function:ProcessDenial",
      "Next": "GenerateExplanation"
    },

    "HumanReview": {
      "Type": "Task",
      "Resource": "arn:aws:states:::sagemaker:createHumanLoop.waitForTaskToken",
      "Parameters": {
        "HumanLoopName.$": "$.disputeId",
        "FlowDefinitionArn": "arn:aws:sagemaker:us-east-1:123456789:flow-definition/dispute-review",
        "HumanLoopInput": {
          "InputContent.$": "States.JsonToString($)"
        }
      },
      "Next": "ProcessHumanDecision"
    },

    "ProcessHumanDecision": {
      "Type": "Choice",
      "Choices": [
        {
          "Variable": "$.humanDecision",
          "StringEquals": "APPROVE",
          "Next": "IssueProvisionalCredit"
        },
        {
          "Variable": "$.humanDecision",
          "StringEquals": "DENY",
          "Next": "AutoDeny"
        }
      ],
      "Default": "RequestMoreInfo"
    },

    "RequestMoreInfo": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:us-east-1:123456789:function:RequestAdditionalEvidence",
      "Next": "WaitForEvidence"
    },

    "WaitForEvidence": {
      "Type": "Wait",
      "Seconds": 259200,
      "Next": "CheckEvidenceReceived"
    },

    "CheckEvidenceReceived": {
      "Type": "Choice",
      "Choices": [
        {
          "Variable": "$.evidenceReceived",
          "BooleanEquals": true,
          "Next": "ParallelProcessing"
        }
      ],
      "Default": "AutoDeny"
    },

    "GenerateExplanation": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:us-east-1:123456789:function:GenerateDecisionLetter",
      "Next": "NotifyCustomer"
    },

    "SubmitToNetwork": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:us-east-1:123456789:function:SubmitChargeback",
      "Next": "MonitorRepresentment"
    },

    "MonitorRepresentment": {
      "Type": "Wait",
      "Seconds": 2592000,
      "Next": "CheckRepresentmentStatus"
    },

    "CheckRepresentmentStatus": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:us-east-1:123456789:function:CheckChargebackStatus",
      "Next": "FinalizeCase"
    },

    "NotifyCustomer": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:us-east-1:123456789:function:SendNotification",
      "Next": "FinalizeCase"
    },

    "FinalizeCase": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:us-east-1:123456789:function:CloseCase",
      "End": true
    },

    "RejectInvalidDispute": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:us-east-1:123456789:function:RejectDispute",
      "End": true
    }
  }
}
```

---

## CORE BANKING & CARD NETWORK INTEGRATION

### Integration Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      AWS CLOUD                                  │
│                                                                 │
│  ┌───────────────┐     ┌───────────────┐     ┌───────────────┐ │
│  │ EventBridge   │────►│ Lambda        │────►│ Amazon MQ     │ │
│  │ (Events)      │     │ (Transform)   │     │ (ActiveMQ)    │ │
│  └───────────────┘     └───────────────┘     └───────┬───────┘ │
│                                                      │         │
│  ┌───────────────┐     ┌───────────────┐            │         │
│  │ API Gateway   │────►│ Lambda        │            │         │
│  │ (REST/WS)     │     │ (Adapter)     │            │         │
│  └───────────────┘     └───────────────┘            │         │
│                                                      │         │
└──────────────────────────────────────────────────────┼─────────┘
                                                       │
                            VPN / Direct Connect       │
                                                       │
┌──────────────────────────────────────────────────────┼─────────┐
│                 ON-PREMISES / PARTNER                │         │
│                                                      ▼         │
│  ┌───────────────┐     ┌───────────────┐     ┌───────────────┐ │
│  │ Core Banking  │◄───►│ IBM MQ /      │◄────│ MQ Bridge     │ │
│  │ (Mainframe)   │     │ Message Bus   │     │               │ │
│  └───────────────┘     └───────────────┘     └───────────────┘ │
│                                                                 │
│  ┌───────────────┐     ┌───────────────┐                       │
│  │ Card Network  │◄───►│ VROL / MC     │                       │
│  │ Gateways      │     │ Mastercom     │                       │
│  └───────────────┘     └───────────────┘                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Card Network Integration Points

| Network | System | Integration Method | Key Operations |
|---------|--------|-------------------|----------------|
| **Visa** | VROL (Resolve Online) | XML/API | TC40 fraud reporting, chargebacks |
| **Mastercard** | Mastercom | Processing Dispute APIs | SAFE data, chargebacks |
| **Core Banking** | Transaction Ledger | IBM MQ / Amazon MQ | Credits, debits, holds |
| **Card Processor** | Authorization | ISO 8583 / REST | Transaction lookup |

### Message Transformation Lambda

```python
import json
import boto3
from datetime import datetime

def transform_dispute_to_core_banking(event):
    """Transform EventBridge dispute event to IBM MQ format"""
    detail = event['detail']

    return {
        "MSG_TYPE": "DISPUTE_CREATE",
        "MSG_VERSION": "1.0",
        "TRAN_ID": detail["transactionId"],
        "CUST_ID": detail["customerId"],
        "AMOUNT": str(detail["amount"]),
        "CURRENCY": "USD",
        "DISPUTE_CODE": map_category_to_code(detail["category"]),
        "DISPUTE_ID": detail["disputeId"],
        "CHANNEL": detail["channel"],
        "TIMESTAMP": datetime.utcnow().strftime("%Y%m%d%H%M%S"),
        "PRIORITY": map_priority(detail["priority"])
    }

def map_category_to_code(category):
    """Map dispute category to core banking codes"""
    mapping = {
        "fraud": "FRD01",
        "unauthorized": "UNA01",
        "duplicate": "DUP01",
        "merchandise_not_received": "MNR01",
        "merchandise_not_as_described": "MND01",
        "billing_error": "BIL01",
        "subscription_cancellation": "SUB01"
    }
    return mapping.get(category, "OTH01")

def transform_to_vrol_inquiry(dispute):
    """Generate VROL XML inquiry for Visa"""
    return f"""<?xml version="1.0" encoding="UTF-8"?>
    <VisaInquiry xmlns="http://visa.com/dispute/v1">
        <Header>
            <MessageType>InquiryRequest</MessageType>
            <Version>2.0</Version>
            <Timestamp>{datetime.utcnow().isoformat()}</Timestamp>
        </Header>
        <InquiryDetails>
            <TransactionId>{dispute['transaction_id']}</TransactionId>
            <AcquirerBIN>{dispute['acquirer_bin']}</AcquirerBIN>
            <DisputeAmount>{dispute['amount']}</DisputeAmount>
            <CurrencyCode>840</CurrencyCode>
            <ReasonCode>{dispute['visa_reason_code']}</ReasonCode>
            <TransactionDate>{dispute['transaction_date']}</TransactionDate>
            <CardNumberMasked>{dispute['card_last_four']}</CardNumberMasked>
        </InquiryDetails>
    </VisaInquiry>
    """

def transform_to_mastercom_request(dispute):
    """Generate Mastercom API request for Mastercard"""
    return {
        "disputeType": "CHARGEBACK",
        "transactionId": dispute['transaction_id'],
        "ica": dispute['issuer_ica'],
        "amount": {
            "value": dispute['amount'],
            "currency": "USD"
        },
        "reasonCode": dispute['mc_reason_code'],
        "messageText": dispute['description'][:500],
        "documentIndicator": "Y" if dispute['has_documents'] else "N"
    }
```

### Visa Reason Codes Mapping

```python
VISA_REASON_CODES = {
    "fraud": {
        "10.1": "EMV Liability Shift Counterfeit Fraud",
        "10.2": "EMV Liability Shift Non-Counterfeit Fraud",
        "10.3": "Other Fraud - Card-Present Environment",
        "10.4": "Other Fraud - Card-Absent Environment",
        "10.5": "Visa Fraud Monitoring Program"
    },
    "authorization": {
        "11.1": "Card Recovery Bulletin",
        "11.2": "Declined Authorization",
        "11.3": "No Authorization"
    },
    "processing_errors": {
        "12.1": "Late Presentment",
        "12.2": "Incorrect Transaction Code",
        "12.3": "Incorrect Currency",
        "12.4": "Incorrect Account Number",
        "12.5": "Incorrect Amount",
        "12.6": "Duplicate Processing/Paid by Other Means",
        "12.7": "Invalid Data"
    },
    "consumer_disputes": {
        "13.1": "Merchandise/Services Not Received",
        "13.2": "Cancelled Recurring Transaction",
        "13.3": "Not as Described or Defective Merchandise/Services",
        "13.4": "Counterfeit Merchandise",
        "13.5": "Misrepresentation",
        "13.6": "Credit Not Processed",
        "13.7": "Cancelled Merchandise/Services"
    }
}
```

---

## REAL-TIME VISIBILITY & DASHBOARD

### Architecture

```
┌──────────────────────────────────────────────────────────────────────────┐
│                          REAL-TIME DASHBOARD                              │
│                                                                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │ Case Status │  │ SLA Metrics │  │ Volume      │  │ Decision    │     │
│  │ Tracker     │  │ Monitor     │  │ Analytics   │  │ Breakdown   │     │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘     │
│         │                │                │                │             │
└─────────┼────────────────┼────────────────┼────────────────┼─────────────┘
          │                │                │                │
          └────────────────┼────────────────┼────────────────┘
                           │                │
                    ┌──────▼────────────────▼──────┐
                    │     AWS AppSync              │
                    │     (GraphQL + WebSocket)    │
                    └──────────────┬───────────────┘
                                   │
          ┌────────────────────────┼────────────────────────┐
          ▼                        ▼                        ▼
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│ Kinesis Data    │      │ DynamoDB        │      │ Timestream      │
│ Streams         │      │ (Case State)    │      │ (Metrics)       │
│ (Event Stream)  │      │                 │      │                 │
└────────┬────────┘      └─────────────────┘      └────────┬────────┘
         │                                                  │
         │              ┌─────────────────┐                │
         └─────────────►│ Lambda          │◄───────────────┘
                        │ (Aggregator)    │
                        └─────────────────┘
```

### AppSync GraphQL Schema

```graphql
type Dispute {
  disputeId: ID!
  customerId: String!
  transactionId: String!
  amount: Float!
  category: DisputeCategory!
  status: DisputeStatus!
  priority: Priority!
  createdAt: AWSDateTime!
  updatedAt: AWSDateTime!
  slaDeadline: AWSDateTime!
  assignedTo: String
  fraudScore: Float
  evidenceScore: Float
  decision: Decision
  timeline: [TimelineEvent!]!
}

enum DisputeCategory {
  FRAUD
  UNAUTHORIZED
  DUPLICATE
  MERCHANDISE_NOT_RECEIVED
  MERCHANDISE_NOT_AS_DESCRIBED
  BILLING_ERROR
  SUBSCRIPTION_CANCELLATION
}

enum DisputeStatus {
  INTAKE
  DOCUMENT_PROCESSING
  FRAUD_ANALYSIS
  PENDING_REVIEW
  HUMAN_REVIEW
  DECISION_RENDERED
  NETWORK_SUBMISSION
  AWAITING_REPRESENTMENT
  CLOSED
}

enum Priority {
  HIGH
  MEDIUM
  LOW
}

type Decision {
  outcome: DecisionOutcome!
  amount: Float!
  reason: String!
  automated: Boolean!
  decidedAt: AWSDateTime!
  decidedBy: String
}

enum DecisionOutcome {
  APPROVED
  DENIED
  PARTIAL
  PENDING
}

type TimelineEvent {
  timestamp: AWSDateTime!
  event: String!
  actor: String!
  details: String
}

type DashboardMetrics {
  totalDisputes: Int!
  openDisputes: Int!
  avgResolutionTimeHours: Float!
  autoAdjudicationRate: Float!
  approvalRate: Float!
  slaComplianceRate: Float!
  totalLiabilityExposure: Float!
  volumeByCategory: [CategoryVolume!]!
  volumeByChannel: [ChannelVolume!]!
}

type CategoryVolume {
  category: DisputeCategory!
  count: Int!
  amount: Float!
}

type ChannelVolume {
  channel: String!
  count: Int!
}

type Query {
  getDispute(disputeId: ID!): Dispute
  listDisputes(status: DisputeStatus, limit: Int, nextToken: String): DisputeConnection!
  getDashboardMetrics(timeRange: TimeRange!): DashboardMetrics!
  getSLAAlerts: [SLAAlert!]!
}

type Mutation {
  updateDisputeStatus(disputeId: ID!, status: DisputeStatus!): Dispute
  assignDispute(disputeId: ID!, assignee: String!): Dispute
  renderDecision(disputeId: ID!, decision: DecisionInput!): Dispute
}

type Subscription {
  onDisputeCreated: Dispute
    @aws_subscribe(mutations: ["createDispute"])
  onDisputeUpdated(disputeId: ID): Dispute
    @aws_subscribe(mutations: ["updateDisputeStatus", "assignDispute", "renderDecision"])
  onMetricsUpdated: DashboardMetrics
    @aws_subscribe(mutations: ["updateMetrics"])
}

input TimeRange {
  start: AWSDateTime!
  end: AWSDateTime!
}

input DecisionInput {
  outcome: DecisionOutcome!
  amount: Float!
  reason: String!
}

type DisputeConnection {
  items: [Dispute!]!
  nextToken: String
}

type SLAAlert {
  disputeId: ID!
  slaType: String!
  deadline: AWSDateTime!
  hoursRemaining: Int!
  priority: Priority!
}
```

### Key Dashboard Metrics

| Category | Metrics | Data Source |
|----------|---------|-------------|
| **Volume** | Disputes/hour, by channel, by category | Kinesis → Timestream |
| **SLA** | Intake-to-decision time, Reg E compliance countdown | DynamoDB + Timestream |
| **Quality** | Auto-adjudication rate, overturn rate, accuracy | Timestream |
| **Financial** | Liability exposure, recovery rate, cost-per-dispute | DynamoDB + Timestream |
| **Operations** | Queue depth, agent utilization, backlog age | CloudWatch + Timestream |

---

## SECURITY & COMPLIANCE

### PCI DSS Compliance Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        PCI DSS BOUNDARY                                  │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    TOKENIZATION LAYER                            │   │
│  │                                                                  │   │
│  │   Raw PAN ──► Token Service (Thales/PCI Vault) ──► Token        │   │
│  │                                                                  │   │
│  │   All downstream systems only see tokens                        │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐        │
│  │ AWS KMS         │  │ Secrets Manager │  │ CloudTrail      │        │
│  │ (Encryption)    │  │ (Credentials)   │  │ (Audit Logging) │        │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘        │
│                                                                         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐        │
│  │ VPC + Private   │  │ WAF + Shield    │  │ IAM + Cognito   │        │
│  │ Subnets         │  │ (DDoS/Attacks)  │  │ (Access Ctrl)   │        │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘        │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Security Services Matrix

| Security Domain | AWS Service | Purpose |
|-----------------|-------------|---------|
| **Encryption at Rest** | KMS, S3 SSE-KMS | AES-256 encryption for all data |
| **Encryption in Transit** | ACM, TLS 1.3 | Certificate management |
| **Tokenization** | Partner (Thales/PCI Vault) | Replace PANs with tokens |
| **Access Control** | IAM, Cognito | Role-based access, MFA |
| **Network Security** | VPC, Security Groups, WAF | Segmentation, DDoS protection |
| **Audit Logging** | CloudTrail, CloudWatch Logs | Compliance audit trail |
| **Secrets Management** | Secrets Manager | API keys, DB credentials |
| **Threat Detection** | GuardDuty, Security Hub | Anomaly detection |
| **Compliance Monitoring** | AWS Config, Security Hub | PCI DSS rule evaluation |

### Regulation E Compliance Features

| Requirement | Timeline | Implementation |
|-------------|----------|----------------|
| **Acknowledge Receipt** | Within 10 business days | EventBridge → Lambda → SES notification |
| **Provisional Credit** | Within 10 business days | Step Functions timer + auto-credit |
| **Investigation Complete** | Within 45 days (90 for certain cases) | SLA countdown in Timestream |
| **Final Resolution Notice** | Within 3 business days of decision | Bedrock-generated letters via SES |
| **Audit Trail** | Indefinite retention | CloudTrail + DynamoDB event sourcing |

### Reg E Timeline State Machine

```python
REG_E_TIMELINES = {
    "acknowledgment": {
        "deadline_business_days": 10,
        "action": "SEND_ACKNOWLEDGMENT",
        "notification_days_before": [3, 1]
    },
    "provisional_credit": {
        "deadline_business_days": 10,
        "action": "ISSUE_PROVISIONAL_CREDIT",
        "conditions": ["investigation_not_complete"]
    },
    "standard_investigation": {
        "deadline_calendar_days": 45,
        "action": "COMPLETE_INVESTIGATION",
        "notification_days_before": [10, 5, 1]
    },
    "extended_investigation": {
        "deadline_calendar_days": 90,
        "applies_to": [
            "new_account_less_than_30_days",
            "pos_debit_transaction",
            "foreign_transaction"
        ],
        "requires": "provisional_credit_issued"
    },
    "final_notice": {
        "deadline_business_days": 3,
        "trigger": "decision_rendered",
        "action": "SEND_FINAL_NOTICE"
    }
}
```

---

## DATA ARCHITECTURE

### DynamoDB Table Designs

```yaml
# Disputes Table
DisputesTable:
  TableName: "disputes"
  KeySchema:
    - AttributeName: "PK"  # DISPUTE#{disputeId}
      KeyType: "HASH"
    - AttributeName: "SK"  # META | DOCUMENT#{docId} | EVENT#{timestamp}
      KeyType: "RANGE"
  GlobalSecondaryIndexes:
    - IndexName: "GSI1-CustomerDisputes"
      KeySchema:
        - AttributeName: "GSI1PK"  # CUSTOMER#{customerId}
          KeyType: "HASH"
        - AttributeName: "GSI1SK"  # {createdAt}
          KeyType: "RANGE"
    - IndexName: "GSI2-StatusIndex"
      KeySchema:
        - AttributeName: "GSI2PK"  # STATUS#{status}
          KeyType: "HASH"
        - AttributeName: "GSI2SK"  # {priority}#{createdAt}
          KeyType: "RANGE"
    - IndexName: "GSI3-SLAIndex"
      KeySchema:
        - AttributeName: "GSI3PK"  # SLA#{slaType}
          KeyType: "HASH"
        - AttributeName: "GSI3SK"  # {deadline}
          KeyType: "RANGE"

# Transactions Cache Table
TransactionsTable:
  TableName: "transaction-cache"
  KeySchema:
    - AttributeName: "transactionId"
      KeyType: "HASH"
  TTL:
    AttributeName: "expiresAt"
    Enabled: true
```

### S3 Bucket Structure

```
dispute-evidence-bucket/
├── raw/
│   └── {disputeId}/
│       └── {documentId}/
│           └── original.{ext}
├── processed/
│   └── {disputeId}/
│       └── {documentId}/
│           ├── textract-output.json
│           ├── comprehend-output.json
│           └── bedrock-analysis.json
├── exports/
│   └── {date}/
│       └── regulatory-reports/
└── archive/
    └── {year}/{month}/
        └── {disputeId}.tar.gz
```

### Timestream Schema

```sql
-- Dispute Metrics Time Series
CREATE TABLE dispute_metrics (
  time TIMESTAMP,
  dispute_id VARCHAR,
  customer_id VARCHAR,
  category VARCHAR,
  channel VARCHAR,
  amount DOUBLE,
  status VARCHAR,
  fraud_score DOUBLE,
  evidence_score DOUBLE,
  processing_time_ms BIGINT,
  decision VARCHAR,
  automated BOOLEAN
)
WITH (
  memory_store_retention_hours = 24,
  magnetic_store_retention_days = 365
);

-- SLA Tracking
CREATE TABLE sla_events (
  time TIMESTAMP,
  dispute_id VARCHAR,
  sla_type VARCHAR,
  deadline TIMESTAMP,
  status VARCHAR,  -- on_track, at_risk, breached
  hours_remaining INT
);

-- Volume Aggregates (pre-computed)
CREATE TABLE volume_aggregates (
  time TIMESTAMP,
  period VARCHAR,  -- minute, hour, day
  category VARCHAR,
  channel VARCHAR,
  count BIGINT,
  total_amount DOUBLE,
  avg_processing_time DOUBLE
);
```

---

## AWS SERVICES SUMMARY

### Complete Service Inventory

| Category | Services |
|----------|----------|
| **Intake & Conversational AI** | Amazon Connect, Amazon Lex V2, Amazon Bedrock (Agents), AWS Amplify, API Gateway, Amazon Cognito, Amazon Q in Connect |
| **Document Processing** | Amazon Textract, Amazon Comprehend, Amazon Bedrock (Claude), Amazon S3, Amazon OpenSearch |
| **ML & Fraud Detection** | Amazon SageMaker, SageMaker Feature Store, Amazon A2I, Amazon Bedrock |
| **Event-Driven Backbone** | Amazon EventBridge, AWS Step Functions, Amazon Kinesis Data Streams, AWS AppSync |
| **Integration** | Amazon MQ, AWS Lambda, API Gateway, AWS Direct Connect |
| **Data Storage** | Amazon DynamoDB, Amazon Aurora, Amazon S3, Amazon Timestream |
| **Real-time Dashboard** | AWS AppSync, Amazon Kinesis, Amazon Timestream, Amazon QuickSight |
| **Security & Compliance** | AWS KMS, AWS Secrets Manager, AWS WAF, AWS Shield, AWS CloudTrail, Amazon GuardDuty, AWS Security Hub, AWS Config |
| **Notifications** | Amazon SES, Amazon SNS, Amazon Pinpoint |
| **Monitoring** | Amazon CloudWatch, AWS X-Ray |

### Cost Optimization Strategies

| Strategy | Services | Expected Savings |
|----------|----------|------------------|
| **Serverless-first** | Lambda, Step Functions, DynamoDB | Pay-per-use, no idle costs |
| **Tiered storage** | S3 Intelligent-Tiering | 40% on evidence storage |
| **Spot instances** | SageMaker Training | 70-90% on ML training |
| **Provisioned throughput** | Bedrock Provisioned | Predictable costs at scale |
| **Reserved capacity** | DynamoDB Reserved | 50-75% on predictable workloads |
| **Data lifecycle** | S3 Lifecycle, DynamoDB TTL | Automatic archival/deletion |

---

## IMPLEMENTATION ROADMAP

### Phase 1: Foundation (Weeks 1-10)

| Week | Focus | Deliverables |
|------|-------|--------------|
| 1-2 | Infrastructure | VPC, networking, IAM roles, KMS keys |
| 3-4 | Event backbone | EventBridge bus, schemas, Step Functions skeleton |
| 5-6 | Data layer | DynamoDB tables, S3 buckets, OpenSearch domain |
| 7-8 | Intake MVP | Lex bot, basic Bedrock agent, Connect instance |
| 9-10 | Integration testing | End-to-end intake flow, event propagation |

### Phase 2: Document Processing (Weeks 11-18)

| Week | Focus | Deliverables |
|------|-------|--------------|
| 11-12 | Textract pipeline | Document upload, OCR, structured extraction |
| 13-14 | Comprehend integration | Document classification, entity extraction |
| 15-16 | Bedrock enrichment | Summarization, cross-document analysis |
| 17-18 | IDP integration | Connect IDP to main workflow, evidence scoring |

### Phase 3: ML & Auto-Adjudication (Weeks 19-28)

| Week | Focus | Deliverables |
|------|-------|--------------|
| 19-20 | Feature engineering | Feature Store setup, historical feature backfill |
| 21-23 | Model development | Fraud model training, validation, tuning |
| 24-25 | Inference pipeline | Real-time endpoints, A2I workflows |
| 26-28 | Decision engine | Auto-adjudication rules, Bedrock explanations |

### Phase 4: Integration & Dashboard (Weeks 29-36)

| Week | Focus | Deliverables |
|------|-------|--------------|
| 29-30 | Core banking | Amazon MQ bridge, transaction sync |
| 31-32 | Card networks | VROL/Mastercom adapters, chargeback submission |
| 33-34 | Real-time dashboard | AppSync API, Timestream metrics, UI |
| 35-36 | Compliance hardening | Audit logging, Reg E automation, PCI validation |

### Phase 5: Production Readiness (Weeks 37-40)

| Week | Focus | Deliverables |
|------|-------|--------------|
| 37 | Performance testing | Load testing, latency optimization |
| 38 | Security review | Penetration testing, compliance audit |
| 39 | Disaster recovery | Multi-region failover, backup verification |
| 40 | Go-live | Phased rollout, monitoring, runbooks |

---

## APPENDIX

### A. Bedrock Model Selection Guide

| Use Case | Recommended Model | Rationale |
|----------|-------------------|-----------|
| Dispute intake conversation | Claude 3 Sonnet | Balance of speed and reasoning |
| Document summarization | Claude 3 Haiku | Fast, cost-effective for volume |
| Complex evidence analysis | Claude 3.5 Sonnet | Superior reasoning for edge cases |
| Decision letter generation | Claude 3 Sonnet | Professional tone, compliance-aware |

### B. SageMaker Instance Recommendations

| Workload | Instance Type | Use Case |
|----------|---------------|----------|
| Training (fraud model) | ml.p3.2xlarge | GPU for neural network training |
| Training (XGBoost) | ml.m5.4xlarge | CPU-optimized for tree models |
| Real-time inference | ml.c6i.xlarge | Low-latency predictions |
| Batch inference | ml.m5.2xlarge | Cost-effective batch processing |

### C. Monitoring & Alerting Thresholds

| Metric | Warning | Critical | Action |
|--------|---------|----------|--------|
| Intake latency (P99) | >3s | >5s | Scale Lambda, check Bedrock |
| IDP processing time | >30s | >60s | Check Textract quotas |
| Fraud score latency | >100ms | >200ms | Scale SageMaker endpoint |
| SLA breach risk | <24h remaining | <8h remaining | Alert supervisor |
| Error rate | >1% | >5% | Page on-call |
| Queue depth | >100 | >500 | Scale consumers |

---

## Document Information

| Field | Value |
|-------|-------|
| **Version** | 1.0 |
| **Created** | December 2024 |
| **Last Updated** | December 2024 |
| **Author** | Architecture Team |
| **Status** | Draft |

---

*This architecture document provides a comprehensive blueprint for implementing a Gen AI-powered dispute resolution system on AWS. Individual components should be validated against current AWS service limits and pricing before implementation.*
