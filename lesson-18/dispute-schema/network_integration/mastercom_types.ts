/**
 * Mastercard Mastercom Integration Types
 * Based on Mastercom API Specifications
 */

import { Dispute } from '../dispute_types';

// ============================================================================
// Mastercom API Request Types
// ============================================================================

export interface MastercomClaimRequest {
  claimType: 'Chargeback' | 'RetrievalRequest';
  clearingTransactionId: string;
  claimAmount: number;
  claimCurrencyCode: string;
  reasonCode: string;
  documentIndicator?: boolean;
  messageText?: string;
  disputeData: MastercomDisputeData;
}

export interface MastercomDisputeData {
  cardholderIdMethod?: string;
  memberMessage?: string;
  chargebackSupportDoc?: string; // File ID reference
  electronicAcceptanceIndicator?: string;
  merchantName?: string;
}

// ============================================================================
// Transformers
// ============================================================================

/**
 * Transforms an internal Dispute object into a Mastercom Claim Request
 */
export function transformToMastercomPayload(dispute: Dispute, clearingTransactionId: string): MastercomClaimRequest {
  return {
    claimType: 'Chargeback',
    clearingTransactionId: clearingTransactionId,
    claimAmount: dispute.amount,
    claimCurrencyCode: dispute.currency.toUpperCase(), // e.g., 'USD' -> '840' usually, but keeping alpha for readablity
    reasonCode: dispute.network_reason_code || '4837',
    documentIndicator: !!dispute.evidence, // True if we are attaching docs
    messageText: dispute.evidence?.uncategorized_text?.substring(0, 100),
    disputeData: {
      memberMessage: dispute.evidence?.duplicate_charge_explanation || dispute.evidence?.refund_refusal_explanation,
      cardholderIdMethod: 'Signature', // Default or dynamic
      merchantName: dispute.evidence?.product_description // Simplified mapping
    }
  };
}
