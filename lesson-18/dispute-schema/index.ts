/**
 * Dispute Resolution Schema
 * A comprehensive API-first dispute management system modeled after Stripe's design patterns
 *
 * Features:
 * - 50+ data fields in a single JSON payload
 * - Support for multiple payment methods (card, PayPal, Klarna, etc.)
 * - Network-specific reason codes (Visa, Mastercard, Amex, Discover)
 * - Enhanced evidence for Visa Compelling Evidence 3.0
 * - 27 evidence fields (18 text, 9 file) with 150K char / 4.5 MB limits
 * - Comprehensive eligibility detection and required actions
 */

// Core types
export * from './dispute_types';

// Network reason codes
export * from './network_reason_codes';

// Re-export validation constants
export {
  EVIDENCE_TEXT_LIMIT,
  EVIDENCE_FILE_SIZE_LIMIT,
  MASTERCARD_PAGE_LIMIT,
  CE3_TRANSACTION_MIN_AGE_DAYS,
  CE3_TRANSACTION_MAX_AGE_DAYS,
  CE3_MIN_PRIOR_TRANSACTIONS,
  calculateEvidenceTextLength,
  validateEvidenceTextLimit,
  validateCE3TransactionAge,
  isVisaCE3Eligible,
  // Tokenization validation
  TOKEN_PATTERN,
  FINGERPRINT_PATTERN,
  LAST4_PATTERN,
  validateTokenFormat,
  validateFingerprintFormat,
  validateLast4Format,
  isTokenValid,
  containsSensitiveCardData,
  maskToken,
} from './dispute_types';

// Re-export reason code utilities
export {
  lookupReasonCode,
  getReasonCodesByCategory,
  getRecommendedEvidence,
  isVisaCE3ReasonCode,
} from './network_reason_codes';
