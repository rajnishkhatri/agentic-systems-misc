/**
 * Lambda Function Interfaces for AWS Dispute Management System
 *
 * This file defines TypeScript interfaces for all Lambda functions
 * in the dispute management workflow.
 */

import type {
  Dispute,
  DisputeEvidence,
  DisputeStatus,
  DisputeReason,
  EnhancedEvidence,
  BalanceTransaction,
  CE3Status,
  CE3RequiredAction,
} from '../dispute_types';

// ============================================================================
// Common Types
// ============================================================================

/** Standard Lambda response structure */
export interface LambdaResponse<T = unknown> {
  statusCode: number;
  body: T;
  headers?: Record<string, string>;
}

/** Error response structure */
export interface ErrorResponse {
  error: {
    type: string;
    message: string;
    code?: string;
    details?: Record<string, unknown>;
  };
}

/** Pagination parameters */
export interface PaginationParams {
  limit?: number;
  startingAfter?: string;
  endingBefore?: string;
}

/** Paginated response */
export interface PaginatedResponse<T> {
  object: 'list';
  data: T[];
  has_more: boolean;
  url: string;
}

// ============================================================================
// 1. Dispute Intake Lambda
// ============================================================================

/** POST /disputes - Create a new dispute from network webhook */
export interface DisputeIntakeRequest {
  /** Webhook payload from card network */
  webhookPayload: {
    network: 'visa' | 'mastercard' | 'amex' | 'discover';
    messageType: 'chargeback' | 'inquiry' | 'pre_arbitration';
    chargeId: string;
    amount: number;
    currency: string;
    reasonCode: string;
    cardholderStatement?: string;
    evidenceDeadline: string; // ISO 8601 timestamp
    networkCaseId: string;
    cardDetails?: {
      last4: string;
      brand: string;
      funding: string;
    };
  };
  /** Idempotency key to prevent duplicate processing */
  idempotencyKey?: string;
}

export interface DisputeIntakeResponse {
  dispute: Dispute;
  created: boolean; // false if idempotent duplicate
}

// ============================================================================
// 2. Dispute Validator Lambda
// ============================================================================

/** Validates dispute data against schema and business rules */
export interface DisputeValidatorRequest {
  dispute: Partial<Dispute>;
  validationRules: Array<
    | 'schema'           // JSON schema validation
    | 'network_reason_code' // Valid reason code for network
    | 'amount_positive'  // Amount > 0
    | 'currency_valid'   // Valid ISO 4217 code
    | 'deadline_future'  // Due date in future
  >;
}

export interface DisputeValidatorResponse {
  isValid: boolean;
  errors?: Array<{
    field: string;
    message: string;
    rule: string;
  }>;
  warnings?: Array<{
    field: string;
    message: string;
  }>;
}

// ============================================================================
// 3. CE3 Eligibility Checker Lambda
// ============================================================================

/** Checks Visa Compelling Evidence 3.0 eligibility */
export interface CE3EligibilityRequest {
  disputeId: string;
  customerEmail?: string;
  customerIp?: string;
  customerDeviceFingerprint?: string;
  customerAccountId?: string;
}

export interface CE3EligibilityResponse {
  status: CE3Status;
  required_actions: CE3RequiredAction[];
  priorTransactionsFound: number;
  priorTransactionsEligible: number;
  matchingIdentifiers: string[];
  recommendation?: string;
}

/** Prior transaction for CE3 matching */
export interface PriorTransaction {
  chargeId: string;
  transactionDate: number; // Unix timestamp
  amount: number;
  currency: string;
  customerEmail?: string;
  customerIp?: string;
  customerDeviceFingerprint?: string;
  customerAccountId?: string;
  ageInDays: number;
  disputed: boolean;
}

// ============================================================================
// 4. Evidence Processor Lambda
// ============================================================================

/** Processes uploaded evidence files */
export interface EvidenceProcessorRequest {
  disputeId: string;
  processType: 'textract' | 'comprehend' | 'bedrock';
  fileKeys?: string[]; // S3 keys for file evidence
  textFields?: string[]; // Text evidence field names to process
}

export interface EvidenceProcessorResponse {
  disputeId: string;
  processType: string;
  results: {
    /** Textract results */
    extractedText?: string;
    extractedTables?: Array<{
      name: string;
      rows: string[][];
    }>;
    extractionConfidence?: number;

    /** Comprehend results */
    sentiment?: {
      overall: 'POSITIVE' | 'NEGATIVE' | 'NEUTRAL' | 'MIXED';
      scores: {
        positive: number;
        negative: number;
        neutral: number;
        mixed: number;
      };
    };
    entities?: Array<{
      text: string;
      type: string;
      score: number;
    }>;
    keyPhrases?: string[];

    /** Bedrock results */
    summary?: string;
    suggestedResponse?: string;
  };
}

// ============================================================================
// 5. Fraud Scorer Lambda
// ============================================================================

/** Scores dispute for fraud likelihood using SageMaker */
export interface FraudScorerRequest {
  disputeId: string;
  features?: {
    transactionAmount: number;
    transactionDate: number;
    disputeReason: DisputeReason;
    networkReasonCode: string;
    cardFunding?: string;
    cardCountry?: string;
    customerIp?: string;
    previousDisputeCount?: number;
    accountAge?: number;
  };
}

export interface FraudScorerResponse {
  disputeId: string;
  fraudScore: number; // 0.0 - 1.0
  riskLevel: 'low' | 'medium' | 'high' | 'critical';
  factors: Array<{
    name: string;
    contribution: number;
    description: string;
  }>;
  recommendation: 'auto_approve' | 'auto_deny' | 'human_review';
  modelVersion: string;
  latencyMs: number;
}

// ============================================================================
// 6. Deadline Calculator Lambda
// ============================================================================

/** Calculates evidence submission deadlines based on regulations */
export interface DeadlineCalculatorRequest {
  disputeId: string;
  reason: DisputeReason;
  networkReasonCode: string;
  created: number; // Unix timestamp
  paymentMethod?: 'card' | 'ach_debit' | 'paypal';
  cardBrand?: string;
}

export interface DeadlineCalculatorResponse {
  disputeId: string;
  dueBy: number; // Unix timestamp
  dueByISO: string; // ISO 8601 for Step Functions Wait
  regulationType: 'reg_e' | 'reg_z' | 'network_specific';
  timelineType: 'initial' | 'extended' | 'provisional_credit';
  businessDays: number;
  calendarDays: number;
  warnings?: Array<{
    type: 'approaching_deadline' | 'weekend_deadline' | 'holiday_deadline';
    message: string;
  }>;
}

// ============================================================================
// 7. Network Submitter Lambda
// ============================================================================

/** Submits dispute response to card network */
export interface NetworkSubmitterRequest {
  disputeId: string;
  network: 'visa' | 'mastercard' | 'amex' | 'discover';
  evidence: DisputeEvidence;
  enhancedEvidence?: EnhancedEvidence;
  action: 'accept' | 'challenge';
}

export interface NetworkSubmitterResponse {
  disputeId: string;
  submissionId: string;
  network: string;
  status: 'submitted' | 'pending' | 'failed';
  networkCaseId: string;
  submittedAt: string; // ISO 8601
  acknowledgementId?: string;
  nextSteps?: string;
}

/** Network-specific submission payload */
export interface VisaVROLPayload {
  caseNumber: string;
  acquirerReferenceNumber: string;
  evidenceCategory: string;
  documentData: Array<{
    documentType: string;
    base64Content: string;
    description: string;
  }>;
  compellingEvidence3?: {
    disputedTransaction: Record<string, unknown>;
    priorTransactions: Array<Record<string, unknown>>;
  };
}

export interface MastercomPayload {
  caseId: string;
  responseCode: string;
  documents: Array<{
    type: string;
    content: string;
    pages: number;
  }>;
  narrative: string;
}

// ============================================================================
// 8. Balance Transaction Creator Lambda
// ============================================================================

/** Creates balance transactions for financial impact tracking */
export interface BalanceTransactionCreatorRequest {
  disputeId: string;
  transactionType: 'dispute' | 'dispute_reversal' | 'dispute_fee' | 'dispute_fee_refund';
  amount: number;
  currency: string;
  feeAmount?: number;
  description?: string;
}

export interface BalanceTransactionCreatorResponse {
  transactionId: string;
  balanceTransaction: BalanceTransaction;
}

// ============================================================================
// 9. Dispute Error Handler Lambda
// ============================================================================

/** Handles errors in the dispute workflow */
export interface DisputeErrorHandlerRequest {
  disputeId: string;
  errorType:
    | 'VALIDATION_ERROR'
    | 'NETWORK_SUBMISSION_ERROR'
    | 'NETWORK_TIMEOUT'
    | 'PROCESSING_ERROR'
    | 'ESCALATION_TIMEOUT';
  errorDetails: Record<string, unknown>;
  executionArn?: string;
  stateName?: string;
}

export interface DisputeErrorHandlerResponse {
  disputeId: string;
  errorId: string;
  handled: boolean;
  action: 'retry' | 'escalate' | 'close' | 'manual_review';
  notificationsSent: string[];
}

// ============================================================================
// 10. Evidence Upload URL Generator Lambda
// ============================================================================

/** Generates pre-signed S3 URLs for evidence upload */
export interface EvidenceUploadUrlRequest {
  disputeId: string;
  filename: string;
  contentType: string;
  fieldName: keyof DisputeEvidence;
  fileSizeBytes?: number;
}

export interface EvidenceUploadUrlResponse {
  uploadUrl: string;
  fileId: string;
  expiresAt: string; // ISO 8601
  maxFileSizeBytes: number;
  allowedContentTypes: string[];
}

// ============================================================================
// API Gateway Integration Types
// ============================================================================

/** GET /disputes - List disputes */
export interface ListDisputesRequest extends PaginationParams {
  status?: DisputeStatus;
  reason?: DisputeReason;
  charge?: string;
  payment_intent?: string;
  created?: {
    gte?: number;
    lte?: number;
    gt?: number;
    lt?: number;
  };
}

export type ListDisputesResponse = PaginatedResponse<Dispute>;

/** GET /disputes/:id - Get dispute */
export interface GetDisputeRequest {
  id: string;
  expand?: Array<'evidence' | 'balance_transactions' | 'enhanced_evidence'>;
}

export type GetDisputeResponse = Dispute;

/** PATCH /disputes/:id - Update dispute */
export interface UpdateDisputeRequest {
  id: string;
  metadata?: Record<string, string>;
  evidence?: Partial<DisputeEvidence>;
  enhanced_evidence?: Partial<EnhancedEvidence>;
  submit?: boolean; // true to submit evidence to network
}

export type UpdateDisputeResponse = Dispute;

/** POST /disputes/:id/close - Close dispute (accept loss) */
export interface CloseDisputeRequest {
  id: string;
}

export type CloseDisputeResponse = Dispute;

// ============================================================================
// DynamoDB Stream Handler Types
// ============================================================================

/** DynamoDB Stream event for dispute changes */
export interface DisputeStreamRecord {
  eventID: string;
  eventName: 'INSERT' | 'MODIFY' | 'REMOVE';
  eventSource: 'aws:dynamodb';
  dynamodb: {
    Keys: {
      PK: { S: string };
      SK: { S: string };
    };
    NewImage?: Record<string, unknown>;
    OldImage?: Record<string, unknown>;
    StreamViewType: 'NEW_AND_OLD_IMAGES';
  };
}

/** Handler for DynamoDB stream events */
export interface StreamHandlerRequest {
  Records: DisputeStreamRecord[];
}

export interface StreamHandlerResponse {
  batchItemFailures: Array<{
    itemIdentifier: string;
  }>;
}

// ============================================================================
// Utility Types
// ============================================================================

/** Environment configuration */
export interface LambdaEnvironment {
  DISPUTES_TABLE: string;
  PRIOR_TRANSACTIONS_TABLE: string;
  EVIDENCE_BUCKET: string;
  EVENT_BUS_NAME: string;
  SAGEMAKER_ENDPOINT: string;
  VISA_API_URL: string;
  MASTERCOM_API_URL: string;
  ENVIRONMENT: 'dev' | 'staging' | 'prod';
}

/** Lambda context extension for dispute functions */
export interface DisputeLambdaContext {
  functionName: string;
  functionVersion: string;
  invokedFunctionArn: string;
  memoryLimitInMB: string;
  awsRequestId: string;
  logGroupName: string;
  logStreamName: string;
  getRemainingTimeInMillis(): number;
}

// ============================================================================
// Webhook Handler Types
// ============================================================================

/** Network webhook verification */
export interface WebhookVerificationRequest {
  signature: string;
  timestamp: string;
  payload: string;
  network: 'visa' | 'mastercard' | 'amex' | 'discover';
}

export interface WebhookVerificationResponse {
  valid: boolean;
  error?: string;
}

/** Network response webhook (dispute outcome) */
export interface NetworkResponseWebhook {
  network: string;
  caseId: string;
  outcome: 'won' | 'lost';
  outcomeReason?: string;
  finalAmount?: number;
  networkMessage?: string;
  timestamp: string;
}
