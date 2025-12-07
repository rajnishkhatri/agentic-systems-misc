/**
 * Dispute Resolution Type Definitions
 * Modeled after Stripe's API-first design patterns
 */

// ============================================================================
// Enums
// ============================================================================

export type DisputeStatus =
  | 'needs_response'
  | 'under_review'
  | 'won'
  | 'lost'
  | 'warning_needs_response'
  | 'warning_under_review'
  | 'warning_closed'
  | 'charge_refunded';

export type DisputeReason =
  | 'credit_not_processed'
  | 'duplicate'
  | 'fraudulent'
  | 'general'
  | 'product_not_received'
  | 'product_unacceptable'
  | 'subscription_canceled'
  | 'unrecognized';

export type CardBrand =
  | 'visa'
  | 'mastercard'
  | 'amex'
  | 'discover'
  | 'diners'
  | 'jcb'
  | 'unionpay';

export type CaseType =
  | 'chargeback'
  | 'inquiry'
  | 'pre_arbitration'
  | 'arbitration'
  | 'compliance';

export type PaymentMethodType =
  | 'card'
  | 'paypal'
  | 'klarna'
  | 'affirm'
  | 'afterpay'
  | 'bank_transfer'
  | 'ach_debit';

export type CardFunding = 'credit' | 'debit' | 'prepaid' | 'unknown';

export type MerchandiseOrServices = 'merchandise' | 'services';

// ============================================================================
// Tokenization Types (PCI DSS Compliance)
// ============================================================================

/**
 * Supported tokenization providers
 * - stripe: Stripe payment tokens
 * - adyen: Adyen tokenization
 * - aws_payment_cryptography: AWS Payment Cryptography service
 * - network: Visa/Mastercard network tokens
 */
export type TokenizationProvider =
  | 'stripe'
  | 'adyen'
  | 'aws_payment_cryptography'
  | 'network'
  | 'internal';

/**
 * Token format types
 * - payment: Reversible by payment gateway for transaction processing
 * - network: Network-level token (Visa Token Service, Mastercard MDES)
 * - internal: One-way hash for internal references only
 */
export type TokenFormat = 'payment' | 'network' | 'internal';

/**
 * Token status for lifecycle management
 */
export type TokenStatus = 'active' | 'suspended' | 'deleted' | 'expired';

export type CE3Status = 'qualified' | 'requires_action' | 'not_qualified';

export type CE3RequiredAction =
  | 'missing_customer_identifiers'
  | 'missing_prior_undisputed_transactions'
  | 'missing_merchandise_or_services'
  | 'missing_disputed_transaction_description'
  | 'missing_customer_email_address'
  | 'missing_customer_purchase_ip'
  | 'transactions_too_recent'
  | 'transactions_too_old';

export type BalanceTransactionType =
  | 'dispute'
  | 'dispute_reversal'
  | 'dispute_fee'
  | 'dispute_fee_refund';

// ============================================================================
// Tokenization Interfaces (PCI DSS Compliance)
// ============================================================================

/**
 * Tokenized card data - replaces raw PAN storage
 * Full PAN is never stored; only tokens and last4 are retained
 *
 * @see compliance/pci-dss-aws-mapping.md for security requirements
 */
export interface TokenizedCardData {
  /**
   * Tokenized PAN - replaces actual card number
   * Format: tok_[a-zA-Z0-9]{24} for payment tokens
   * Pattern: ^tok_[a-zA-Z0-9]{24}$
   */
  pan_token: string;

  /**
   * Last 4 digits of original PAN
   * Not considered CHD when stored in isolation (per PCI DSS)
   * Pattern: ^[0-9]{4}$
   */
  last4: string;

  /**
   * Unique card fingerprint for matching across transactions
   * Generated from PAN hash - irreversible
   * Pattern: ^[a-zA-Z0-9]{32}$
   */
  fingerprint: string;

  /** Tokenization service provider */
  tokenization_provider: TokenizationProvider;

  /** Token format/type */
  token_format: TokenFormat;

  /** Current token status */
  token_status: TokenStatus;

  /** Unix timestamp when token was created */
  tokenized_at: number;

  /** Unix timestamp when token expires (if applicable) */
  token_expires_at?: number;

  /**
   * Token vault reference for provider-specific lookups
   * Used for detokenization requests (payment processing only)
   */
  vault_reference?: string;
}

/**
 * Network token details for Visa Token Service (VTS) or Mastercard MDES
 */
export interface NetworkTokenDetails {
  /** Network-assigned token (DPAN format) */
  network_token: string;

  /** Token requestor ID assigned by network */
  token_requestor_id: string;

  /** Token reference ID for network calls */
  token_reference_id: string;

  /** Network token status */
  status: 'active' | 'inactive' | 'suspended' | 'deleted';

  /** Token expiration (may differ from card expiration) */
  token_exp_month?: number;
  token_exp_year?: number;

  /** Cryptogram for transaction authorization (not stored) */
  cryptogram_type?: 'TAVV' | 'DTVV';
}

/**
 * Tokenization audit record for compliance logging
 */
export interface TokenizationAuditRecord {
  /** Unique audit record ID */
  audit_id: string;

  /** Action performed */
  action: 'tokenize' | 'detokenize' | 'delete' | 'suspend' | 'reactivate';

  /** Token reference (not the actual token) */
  token_fingerprint: string;

  /** Unix timestamp of action */
  timestamp: number;

  /** Actor performing the action */
  actor: {
    type: 'system' | 'user' | 'service';
    id: string;
    ip_address?: string;
  };

  /** Reason for action (required for compliance) */
  reason: string;

  /** Result of action */
  result: 'success' | 'failure';

  /** Error details if failed */
  error_code?: string;
}

// ============================================================================
// Address
// ============================================================================

export interface Address {
  line1?: string;
  line2?: string;
  city?: string;
  state?: string;
  postal_code?: string;
  country?: string; // ISO 3166-1 alpha-2
}

// ============================================================================
// Balance Transaction
// ============================================================================

export interface BalanceTransaction {
  id: string;
  amount: number;
  currency: string;
  type: BalanceTransactionType;
  created: number;
  fee: number;
  net: number;
  description?: string;
}

// ============================================================================
// Evidence (27 fields - text and file)
// ============================================================================

export interface DisputeEvidence {
  // Text fields (150,000 character combined limit)
  access_activity_log?: string;
  billing_address?: string;
  cancellation_policy_disclosure?: string;
  cancellation_rebuttal?: string;
  customer_email_address?: string;
  customer_name?: string;
  customer_purchase_ip?: string;
  duplicate_charge_explanation?: string;
  duplicate_charge_id?: string;
  product_description?: string;
  refund_policy_disclosure?: string;
  refund_refusal_explanation?: string;
  service_date?: string;
  shipping_address?: string;
  shipping_carrier?: string;
  shipping_date?: string;
  shipping_tracking_number?: string;
  uncategorized_text?: string;

  // File fields (4.5 MB combined limit)
  cancellation_policy?: string; // File ID
  customer_communication?: string;
  customer_signature?: string;
  duplicate_charge_documentation?: string;
  receipt?: string;
  refund_policy?: string;
  service_documentation?: string;
  shipping_documentation?: string;
  uncategorized_file?: string;
}

// ============================================================================
// Enhanced Eligibility
// ============================================================================

export interface VisaCompellingEvidence3Eligibility {
  status: CE3Status;
  required_actions?: CE3RequiredAction[];
  partner_rejected_details?: Record<string, unknown> | null;
}

export interface VisaComplianceEligibility {
  status: 'fee_acknowledged' | 'fee_pending';
  fee_amount?: number;
}

export interface MastercardArbitrationEligibility {
  status: 'eligible' | 'not_eligible' | 'pending';
}

export interface EnhancedEligibility {
  visa_compelling_evidence_3?: VisaCompellingEvidence3Eligibility;
  visa_compliance?: VisaComplianceEligibility;
  mastercard_arbitration?: MastercardArbitrationEligibility;
}

// ============================================================================
// Evidence Details
// ============================================================================

export interface EvidenceDetails {
  due_by: number | null;
  has_evidence: boolean;
  past_due: boolean;
  submission_count: number;
  enhanced_eligibility?: EnhancedEligibility;
}

// ============================================================================
// Enhanced Evidence (Visa CE 3.0)
// ============================================================================

export interface CE3DisputedTransaction {
  customer_account_id?: string;
  customer_device_fingerprint?: string;
  customer_device_id?: string;
  customer_email_address?: string;
  customer_purchase_ip?: string;
  merchandise_or_services?: MerchandiseOrServices;
  product_description?: string;
  shipping_address?: Address;
}

export interface CE3PriorTransaction {
  charge: string;
  customer_account_id?: string;
  customer_device_fingerprint?: string;
  customer_device_id?: string;
  customer_email_address?: string;
  customer_purchase_ip?: string;
  product_description?: string;
  shipping_address?: Address;
}

export interface VisaCompellingEvidence3 {
  disputed_transaction?: CE3DisputedTransaction;
  prior_undisputed_transactions?: CE3PriorTransaction[]; // Min 2, 120-365 days old
}

export interface EnhancedEvidence {
  visa_compelling_evidence_3?: VisaCompellingEvidence3;
}

// ============================================================================
// Payment Method Details
// ============================================================================

export interface CardDetails {
  brand: CardBrand;
  case_type?: CaseType;
  network_reason_code?: string;

  /**
   * Last 4 digits of card number
   * This is the ONLY portion of PAN stored (PCI DSS compliant)
   * Pattern: ^[0-9]{4}$
   */
  last4?: string;

  exp_month?: number;
  exp_year?: number;

  /**
   * Unique card fingerprint for matching without storing PAN
   * Generated via one-way hash - cannot be reversed to PAN
   * Pattern: ^[a-zA-Z0-9]{32}$
   */
  fingerprint?: string;

  funding?: CardFunding;
  country?: string;
  issuer?: string;

  /**
   * Tokenized card data for secure PAN handling
   * Full PAN is NEVER stored; only the token reference
   * @see TokenizedCardData
   */
  tokenized_data?: TokenizedCardData;

  /**
   * Network token details (Visa Token Service / Mastercard MDES)
   * Used for network-level tokenization when available
   * @see NetworkTokenDetails
   */
  network_token?: NetworkTokenDetails;
}

export interface PayPalDetails {
  case_id?: string;
  dispute_type?: 'inquiry' | 'chargeback' | 'unauthorized';
  reason_code?: string;
}

export interface KlarnaDetails {
  reason_code?: string;
}

export interface PaymentMethodDetails {
  type: PaymentMethodType;
  card?: CardDetails;
  paypal?: PayPalDetails;
  klarna?: KlarnaDetails;
}

// ============================================================================
// Main Dispute Object
// ============================================================================

export interface Dispute {
  id: string;
  object: 'dispute';
  amount: number;
  balance_transactions?: BalanceTransaction[];
  charge: string;
  created: number;
  currency: string;
  evidence?: DisputeEvidence;
  evidence_details?: EvidenceDetails;
  enhanced_evidence?: EnhancedEvidence;
  is_charge_refundable?: boolean;
  livemode: boolean;
  metadata?: Record<string, string>;
  network_reason_code?: string;
  payment_intent?: string | null;
  payment_method_details?: PaymentMethodDetails;
  reason: DisputeReason;
  status: DisputeStatus;
  transaction_amount?: number;
  transaction_date?: number;
}

// ============================================================================
// API Response Types
// ============================================================================

export interface DisputeList {
  object: 'list';
  data: Dispute[];
  has_more: boolean;
  url: string;
}

export interface DisputeUpdateParams {
  evidence?: Partial<DisputeEvidence>;
  enhanced_evidence?: EnhancedEvidence;
  metadata?: Record<string, string>;
  submit?: boolean;
}

// ============================================================================
// Validation Helpers
// ============================================================================

export const EVIDENCE_TEXT_LIMIT = 150_000;
export const EVIDENCE_FILE_SIZE_LIMIT = 4_500_000; // 4.5 MB
export const MASTERCARD_PAGE_LIMIT = 19;

export const CE3_TRANSACTION_MIN_AGE_DAYS = 120;
export const CE3_TRANSACTION_MAX_AGE_DAYS = 365;
export const CE3_MIN_PRIOR_TRANSACTIONS = 2;

/**
 * Calculate total character count of text evidence fields
 */
export function calculateEvidenceTextLength(evidence: DisputeEvidence): number {
  const textFields: (keyof DisputeEvidence)[] = [
    'access_activity_log',
    'billing_address',
    'cancellation_policy_disclosure',
    'cancellation_rebuttal',
    'customer_email_address',
    'customer_name',
    'customer_purchase_ip',
    'duplicate_charge_explanation',
    'duplicate_charge_id',
    'product_description',
    'refund_policy_disclosure',
    'refund_refusal_explanation',
    'service_date',
    'shipping_address',
    'shipping_carrier',
    'shipping_date',
    'shipping_tracking_number',
    'uncategorized_text',
  ];

  return textFields.reduce((total, field) => {
    const value = evidence[field];
    return total + (typeof value === 'string' ? value.length : 0);
  }, 0);
}

/**
 * Validate evidence text length is within limits
 */
export function validateEvidenceTextLimit(evidence: DisputeEvidence): boolean {
  return calculateEvidenceTextLength(evidence) <= EVIDENCE_TEXT_LIMIT;
}

/**
 * Check if prior transactions meet CE 3.0 age requirements
 */
export function validateCE3TransactionAge(transactionDate: number, disputeDate: number): boolean {
  const daysDiff = (disputeDate - transactionDate) / (1000 * 60 * 60 * 24);
  return daysDiff >= CE3_TRANSACTION_MIN_AGE_DAYS && daysDiff <= CE3_TRANSACTION_MAX_AGE_DAYS;
}

/**
 * Check if dispute is eligible for Visa CE 3.0 based on reason code
 */
export function isVisaCE3Eligible(dispute: Dispute): boolean {
  return (
    dispute.payment_method_details?.type === 'card' &&
    dispute.payment_method_details?.card?.brand === 'visa' &&
    dispute.payment_method_details?.card?.network_reason_code === '10.4' &&
    dispute.reason === 'fraudulent'
  );
}

// ============================================================================
// Tokenization Validation Helpers
// ============================================================================

/** Regex pattern for payment tokens */
export const TOKEN_PATTERN = /^tok_[a-zA-Z0-9]{24}$/;

/** Regex pattern for card fingerprints */
export const FINGERPRINT_PATTERN = /^[a-zA-Z0-9]{32}$/;

/** Regex pattern for last 4 digits */
export const LAST4_PATTERN = /^[0-9]{4}$/;

/**
 * Validate token format
 */
export function validateTokenFormat(token: string): boolean {
  return TOKEN_PATTERN.test(token);
}

/**
 * Validate fingerprint format
 */
export function validateFingerprintFormat(fingerprint: string): boolean {
  return FINGERPRINT_PATTERN.test(fingerprint);
}

/**
 * Validate last4 format
 */
export function validateLast4Format(last4: string): boolean {
  return LAST4_PATTERN.test(last4);
}

/**
 * Check if tokenized card data is valid and active
 */
export function isTokenValid(tokenData: TokenizedCardData): boolean {
  return (
    validateTokenFormat(tokenData.pan_token) &&
    validateFingerprintFormat(tokenData.fingerprint) &&
    validateLast4Format(tokenData.last4) &&
    tokenData.token_status === 'active' &&
    (tokenData.token_expires_at === undefined || tokenData.token_expires_at > Date.now())
  );
}

/**
 * Check if card details contain sensitive data that should not be stored
 * Returns true if sensitive data is detected (CVV, full PAN, PIN)
 */
export function containsSensitiveCardData(data: Record<string, unknown>): boolean {
  const sensitiveFields = ['cvv', 'cvc', 'cvv2', 'cvc2', 'pin', 'pin_block', 'full_pan', 'pan'];
  const keys = Object.keys(data).map((k) => k.toLowerCase());
  return sensitiveFields.some((field) => keys.includes(field));
}

/**
 * Mask a token for logging (show first and last 4 characters)
 */
export function maskToken(token: string): string {
  if (token.length <= 8) return '****';
  return `${token.slice(0, 4)}...${token.slice(-4)}`;
}
