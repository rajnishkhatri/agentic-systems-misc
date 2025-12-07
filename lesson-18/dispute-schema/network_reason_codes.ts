/**
 * Network Reason Code Mappings
 * Maps card network-specific reason codes to unified dispute categories
 */

import { DisputeReason, CardBrand } from './dispute_types';

// ============================================================================
// Visa Reason Codes
// ============================================================================

export const VISA_REASON_CODES: Record<string, { description: string; category: DisputeReason }> = {
  // Fraud (10.x series)
  '10.1': { description: 'EMV Liability Shift Counterfeit Fraud', category: 'fraudulent' },
  '10.2': { description: 'EMV Liability Shift Non-Counterfeit Fraud', category: 'fraudulent' },
  '10.3': { description: 'Other Fraud - Card Present Environment', category: 'fraudulent' },
  '10.4': { description: 'Other Fraud - Card Absent Environment', category: 'fraudulent' },
  '10.5': { description: 'Visa Fraud Monitoring Program', category: 'fraudulent' },

  // Authorization (11.x series)
  '11.1': { description: 'Card Recovery Bulletin', category: 'general' },
  '11.2': { description: 'Declined Authorization', category: 'general' },
  '11.3': { description: 'No Authorization', category: 'general' },

  // Processing Errors (12.x series)
  '12.1': { description: 'Late Presentment', category: 'general' },
  '12.2': { description: 'Incorrect Transaction Code', category: 'general' },
  '12.3': { description: 'Incorrect Currency', category: 'general' },
  '12.4': { description: 'Incorrect Account Number', category: 'general' },
  '12.5': { description: 'Incorrect Amount', category: 'general' },
  '12.6.1': { description: 'Duplicate Processing', category: 'duplicate' },
  '12.6.2': { description: 'Paid by Other Means', category: 'duplicate' },
  '12.7': { description: 'Invalid Data', category: 'general' },

  // Consumer Disputes (13.x series)
  '13.1': { description: 'Merchandise/Services Not Received', category: 'product_not_received' },
  '13.2': { description: 'Cancelled Recurring Transaction', category: 'subscription_canceled' },
  '13.3': { description: 'Not as Described or Defective Merchandise/Services', category: 'product_unacceptable' },
  '13.4': { description: 'Counterfeit Merchandise', category: 'product_unacceptable' },
  '13.5': { description: 'Misrepresentation', category: 'product_unacceptable' },
  '13.6': { description: 'Credit Not Processed', category: 'credit_not_processed' },
  '13.7': { description: 'Cancelled Merchandise/Services', category: 'credit_not_processed' },
  '13.8': { description: 'Original Credit Transaction Not Accepted', category: 'general' },
  '13.9': { description: 'Non-Receipt of Cash or Load Transaction Value', category: 'product_not_received' },
};

// ============================================================================
// Mastercard Reason Codes
// ============================================================================

export const MASTERCARD_REASON_CODES: Record<string, { description: string; category: DisputeReason }> = {
  // Authorization
  '4807': { description: 'Warning Bulletin File', category: 'general' },
  '4808': { description: 'Authorization-Related Chargeback', category: 'general' },
  '4812': { description: 'Account Number Not on File', category: 'general' },

  // Cardholder Disputes
  '4831': { description: 'Transaction Amount Differs', category: 'general' },
  '4834': { description: 'Duplicate Processing', category: 'duplicate' },
  '4835': { description: 'Card Not Present', category: 'fraudulent' },

  // Fraud
  '4837': { description: 'No Cardholder Authorization', category: 'fraudulent' },
  '4840': { description: 'Fraudulent Processing of Transactions', category: 'fraudulent' },
  '4841': { description: 'Cancelled Recurring Transaction', category: 'subscription_canceled' },
  '4842': { description: 'Late Presentment', category: 'general' },
  '4846': { description: 'Correct Transaction Currency Code Not Provided', category: 'general' },
  '4849': { description: 'Questionable Merchant Activity', category: 'fraudulent' },
  '4850': { description: 'Installment Billing Dispute', category: 'general' },
  '4853': { description: 'Cardholder Dispute', category: 'general' },

  // Point of Interaction Errors
  '4854': { description: 'Cardholder Dispute - Not Elsewhere Classified', category: 'general' },
  '4855': { description: 'Goods or Services Not Provided', category: 'product_not_received' },
  '4857': { description: 'Card-Activated Telephone Transaction', category: 'general' },
  '4859': { description: 'Addendum, No-show, or ATM Dispute', category: 'general' },

  // Additional Fraud Codes
  '4863': { description: 'Cardholder Does Not Recognize - Potential Fraud', category: 'fraudulent' },
  '4870': { description: 'Chip Liability Shift', category: 'fraudulent' },
  '4871': { description: 'Chip/PIN Liability Shift', category: 'fraudulent' },
};

// ============================================================================
// American Express Reason Codes
// ============================================================================

export const AMEX_REASON_CODES: Record<string, { description: string; category: DisputeReason }> = {
  // Fraud
  'F10': { description: 'Missing Imprint', category: 'fraudulent' },
  'F14': { description: 'Missing Signature', category: 'fraudulent' },
  'F24': { description: 'No Cardholder Authorization', category: 'fraudulent' },
  'F29': { description: 'Card Not Present', category: 'fraudulent' },
  'F30': { description: 'EMV Counterfeit', category: 'fraudulent' },
  'F31': { description: 'EMV Lost/Stolen/Non-Received', category: 'fraudulent' },

  // Authorization
  'A01': { description: 'Charge Amount Exceeds Authorization Amount', category: 'general' },
  'A02': { description: 'No Valid Authorization', category: 'general' },
  'A08': { description: 'Authorization Approval Expired', category: 'general' },

  // Processing Errors
  'P01': { description: 'Unassigned Card Number', category: 'general' },
  'P03': { description: 'Credit Processed as Charge', category: 'general' },
  'P04': { description: 'Charge Processed as Credit', category: 'general' },
  'P05': { description: 'Incorrect Charge Amount', category: 'general' },
  'P07': { description: 'Late Submission', category: 'general' },
  'P08': { description: 'Duplicate Charge', category: 'duplicate' },
  'P22': { description: 'Non-Matching Card Number', category: 'general' },
  'P23': { description: 'Currency Discrepancy', category: 'general' },

  // Cardholder Disputes
  'C02': { description: 'Credit Not Processed', category: 'credit_not_processed' },
  'C04': { description: 'Goods/Services Returned or Refused', category: 'credit_not_processed' },
  'C05': { description: 'Goods/Services Cancelled', category: 'credit_not_processed' },
  'C08': { description: 'Goods/Services Not Received or Only Partially Received', category: 'product_not_received' },
  'C14': { description: 'Paid by Other Means', category: 'duplicate' },
  'C18': { description: 'Request for Copy Unfulfilled', category: 'general' },
  'C28': { description: 'Cancelled Recurring Billing', category: 'subscription_canceled' },
  'C31': { description: 'Goods/Services Not as Described', category: 'product_unacceptable' },
  'C32': { description: 'Goods/Services Damaged or Defective', category: 'product_unacceptable' },

  // Inquiry/Retrieval
  'R03': { description: 'Insufficient Reply', category: 'general' },
  'R13': { description: 'No Reply', category: 'general' },
  'M01': { description: 'Chargeback Authorization', category: 'general' },
};

// ============================================================================
// Discover Reason Codes
// ============================================================================

export const DISCOVER_REASON_CODES: Record<string, { description: string; category: DisputeReason }> = {
  // Fraud
  'UA01': { description: 'Fraud - Card Present Transaction', category: 'fraudulent' },
  'UA02': { description: 'Fraud - Card Not Present Transaction', category: 'fraudulent' },
  'UA05': { description: 'Fraud - Chip Card Counterfeit Transaction', category: 'fraudulent' },
  'UA06': { description: 'Fraud - Chip Card Lost/Stolen', category: 'fraudulent' },

  // Authorization
  'AT': { description: 'Authorization Noncompliance', category: 'general' },

  // Processing Errors
  'DP': { description: 'Duplicate Processing', category: 'duplicate' },
  'EX': { description: 'Expired Card', category: 'general' },
  'IC': { description: 'Illegible Card Number', category: 'general' },
  'IN': { description: 'Invalid Card Number', category: 'general' },
  'LP': { description: 'Late Presentment', category: 'general' },
  'NA': { description: 'No Authorization', category: 'general' },
  'NC': { description: 'Not Classified', category: 'general' },
  'PM': { description: 'Paid by Other Means', category: 'duplicate' },
  'RG': { description: 'Non-Receipt of Goods or Services', category: 'product_not_received' },
  'RM': { description: 'Quality Discrepancy', category: 'product_unacceptable' },

  // Cardholder Disputes
  'AA': { description: 'Does Not Recognize', category: 'unrecognized' },
  'AP': { description: 'Cancelled Recurring Transaction', category: 'subscription_canceled' },
  'AW': { description: 'Altered Amount', category: 'general' },
  'CD': { description: 'Credit/Debit Posted Incorrectly', category: 'general' },
  'CR': { description: 'Cancelled Reservation', category: 'credit_not_processed' },
  'DA': { description: 'Declined Authorization', category: 'general' },
  'NF': { description: 'Non-Receipt of Cash from ATM', category: 'product_not_received' },
  'RN2': { description: 'Credit Not Received', category: 'credit_not_processed' },
};

// ============================================================================
// Unified Lookup
// ============================================================================

export interface ReasonCodeInfo {
  network: CardBrand;
  code: string;
  description: string;
  category: DisputeReason;
}

/**
 * Look up reason code information by network and code
 */
export function lookupReasonCode(network: CardBrand, code: string): ReasonCodeInfo | null {
  let codeMap: Record<string, { description: string; category: DisputeReason }> | null = null;

  switch (network) {
    case 'visa':
      codeMap = VISA_REASON_CODES;
      break;
    case 'mastercard':
      codeMap = MASTERCARD_REASON_CODES;
      break;
    case 'amex':
      codeMap = AMEX_REASON_CODES;
      break;
    case 'discover':
      codeMap = DISCOVER_REASON_CODES;
      break;
    default:
      return null;
  }

  const info = codeMap[code];
  if (!info) return null;

  return {
    network,
    code,
    description: info.description,
    category: info.category,
  };
}

/**
 * Get all reason codes for a specific category
 */
export function getReasonCodesByCategory(category: DisputeReason): ReasonCodeInfo[] {
  const results: ReasonCodeInfo[] = [];

  const networks: { brand: CardBrand; codes: Record<string, { description: string; category: DisputeReason }> }[] = [
    { brand: 'visa', codes: VISA_REASON_CODES },
    { brand: 'mastercard', codes: MASTERCARD_REASON_CODES },
    { brand: 'amex', codes: AMEX_REASON_CODES },
    { brand: 'discover', codes: DISCOVER_REASON_CODES },
  ];

  for (const { brand, codes } of networks) {
    for (const [code, info] of Object.entries(codes)) {
      if (info.category === category) {
        results.push({
          network: brand,
          code,
          description: info.description,
          category: info.category,
        });
      }
    }
  }

  return results;
}

/**
 * Get the recommended evidence fields for a dispute category
 */
export function getRecommendedEvidence(category: DisputeReason): string[] {
  const evidenceMap: Record<DisputeReason, string[]> = {
    fraudulent: [
      'customer_purchase_ip',
      'customer_email_address',
      'customer_signature',
      'access_activity_log',
      'receipt',
      'shipping_documentation',
      'shipping_tracking_number',
    ],
    product_not_received: [
      'shipping_documentation',
      'shipping_tracking_number',
      'shipping_carrier',
      'shipping_date',
      'shipping_address',
      'customer_communication',
    ],
    product_unacceptable: [
      'product_description',
      'customer_communication',
      'refund_policy',
      'refund_policy_disclosure',
      'receipt',
    ],
    duplicate: [
      'duplicate_charge_id',
      'duplicate_charge_explanation',
      'duplicate_charge_documentation',
      'receipt',
    ],
    subscription_canceled: [
      'cancellation_policy',
      'cancellation_policy_disclosure',
      'cancellation_rebuttal',
      'customer_communication',
      'access_activity_log',
    ],
    credit_not_processed: [
      'refund_policy',
      'refund_policy_disclosure',
      'refund_refusal_explanation',
      'customer_communication',
    ],
    general: [
      'receipt',
      'customer_communication',
      'product_description',
      'uncategorized_text',
      'uncategorized_file',
    ],
    unrecognized: [
      'receipt',
      'customer_email_address',
      'billing_address',
      'customer_communication',
      'shipping_documentation',
    ],
  };

  return evidenceMap[category] || evidenceMap.general;
}

/**
 * Check if a dispute qualifies for Visa Compelling Evidence 3.0
 */
export function isVisaCE3ReasonCode(code: string): boolean {
  return code === '10.4';
}
