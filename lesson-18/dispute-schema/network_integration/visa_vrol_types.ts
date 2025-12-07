/**
 * Visa VROL (Visa Resolve Online) Integration Types
 * Based on Visa Disputes API specifications (approximate structures)
 */

import { Dispute } from '../dispute_types';

// ============================================================================
// Visa API Request Types
// ============================================================================

export interface VisaDisputeRequest {
  disputeInfo: {
    transactionId: string; // The 15-digit transaction ID from Visa
    disputeAmount: number;
    disputeCurrency: string;
    disputeCategory: string; // Corresponds to reason codes (e.g., "Fraud")
    disputeCondition: string; // e.g., "10.4 - Other Fraud - Card Absent"
    memberMessageText?: string;
  };
  cardholderInfo?: {
    accountNumber: string; // Tokenized or encrypted
    name?: string;
  };
  questionnaire?: VisaFraudQuestionnaire | VisaConsumerQuestionnaire;
}

export interface VisaFraudQuestionnaire {
  type: 'Fraud';
  purchaseDate: string;
  discoveryDate: string;
  cardInPossession: boolean;
  transactionUnrecognized: boolean;
  policeReportFiled?: boolean;
  policeReportNumber?: string;
  compellingEvidence?: VisaCompellingEvidence3Payload;
}

export interface VisaConsumerQuestionnaire {
  type: 'Consumer';
  expectedDate?: string;
  merchandiseReceived?: boolean;
  merchandiseReturned?: boolean;
  returnDate?: string;
  cancellationDate?: string;
  cancellationReason?: string;
  attemptedToResolve?: boolean;
  merchantResponse?: string;
}

// Compelling Evidence 3.0 Payload
export interface VisaCompellingEvidence3Payload {
  version: '3.0';
  qualificationStatus: 'Qualified' | 'NotQualified';
  undisputedTransactions: Array<{
    transactionId: string;
    date: string;
    merchantName: string;
    amount: number;
    currency: string;
    ipAddress?: string;
    deviceId?: string;
    shippingAddress?: string;
  }>;
  disputedTransactionData: {
    ipAddress?: string;
    deviceId?: string;
    shippingAddress?: string;
    accountLogin?: string;
  };
}

// ============================================================================
// Transformers
// ============================================================================

/**
 * Transforms an internal Dispute object into a Visa VROL Dispute Request
 */
export function transformToVisaVrolPayload(dispute: Dispute, visaTransactionId: string): VisaDisputeRequest {
  const isFraud = dispute.reason === 'fraudulent';
  
  const payload: VisaDisputeRequest = {
    disputeInfo: {
      transactionId: visaTransactionId,
      disputeAmount: dispute.amount,
      disputeCurrency: dispute.currency.toUpperCase(),
      disputeCategory: mapReasonToCategory(dispute.reason),
      disputeCondition: dispute.network_reason_code || 'Unknown',
      memberMessageText: dispute.evidence?.uncategorized_text?.substring(0, 500)
    },
    cardholderInfo: {
      accountNumber: dispute.payment_method_details?.card?.last4 || '', // Placeholder
      name: dispute.evidence?.customer_name
    }
  };

  if (isFraud) {
    payload.questionnaire = {
      type: 'Fraud',
      purchaseDate: new Date((dispute.transaction_date || 0) * 1000).toISOString().split('T')[0],
      discoveryDate: new Date(dispute.created * 1000).toISOString().split('T')[0],
      cardInPossession: dispute.payment_method_details?.card?.funding !== 'credit', // Heuristic
      transactionUnrecognized: dispute.reason === 'unrecognized',
      compellingEvidence: transformCompellingEvidence(dispute)
    };
  } else {
    payload.questionnaire = {
      type: 'Consumer',
      expectedDate: dispute.evidence?.service_date,
      merchandiseReceived: dispute.reason === 'product_unacceptable',
      attemptedToResolve: !!dispute.evidence?.customer_communication
    };
  }

  return payload;
}

function mapReasonToCategory(reason: string): string {
  const map: Record<string, string> = {
    'fraudulent': 'Fraud',
    'product_not_received': 'Processing Errors', // or Consumer Disputes depending on specific code
    'product_unacceptable': 'Consumer Disputes',
    'subscription_canceled': 'Consumer Disputes',
    'general': 'Authorization'
  };
  return map[reason] || 'Consumer Disputes';
}

function transformCompellingEvidence(dispute: Dispute): VisaCompellingEvidence3Payload | undefined {
  const ce3 = dispute.enhanced_evidence?.visa_compelling_evidence_3;
  
  if (!ce3 || !ce3.prior_undisputed_transactions) return undefined;

  return {
    version: '3.0',
    qualificationStatus: 'Qualified', // Should be validated by logic
    undisputedTransactions: ce3.prior_undisputed_transactions.map(tx => ({
      transactionId: tx.charge, // Assuming charge ID maps to network ID for this example
      date: '2023-01-01', // Needs lookup
      merchantName: 'My Merchant',
      amount: 0, // Needs lookup
      currency: 'USD', // Needs lookup
      ipAddress: tx.customer_purchase_ip,
      deviceId: tx.customer_device_id,
      shippingAddress: JSON.stringify(tx.shipping_address)
    })),
    disputedTransactionData: {
      ipAddress: ce3.disputed_transaction?.customer_purchase_ip,
      deviceId: ce3.disputed_transaction?.customer_device_id,
      shippingAddress: JSON.stringify(ce3.disputed_transaction?.shipping_address)
    }
  };
}
