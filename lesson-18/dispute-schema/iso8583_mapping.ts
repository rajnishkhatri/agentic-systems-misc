/**
 * ISO 8583 Data Element Mapping for Dispute Processing
 * Maps internal Dispute Schema fields to standard ISO 8583-1987 Data Elements
 */

import { Dispute } from './dispute_types';

export interface Iso8583Mapping {
  field: string;
  dataElement: number;
  description: string;
  format: string; // e.g., "n 12", "an 40"
  transform?: (value: any) => string;
}

export const DISPUTE_TO_ISO8583_MAP: Record<string, Iso8583Mapping> = {
  // Primary Account Number (PAN) - sensitive, usually tokenized in internal systems
  'payment_method_details.card.last4': {
    field: 'payment_method_details.card.last4',
    dataElement: 2,
    description: 'Primary Account Number (PAN)',
    format: 'n..19',
    transform: (val) => `************${val}` // Placeholder for detokenization logic
  },

  // Processing Code - varies by transaction type (Dispute/Chargeback often specific codes)
  'object': {
    field: 'object',
    dataElement: 3,
    description: 'Processing Code',
    format: 'n 6',
    transform: () => '200000' // Example: Refund/Return
  },

  // Amount, Transaction
  'amount': {
    field: 'amount',
    dataElement: 4,
    description: 'Amount, Transaction',
    format: 'n 12',
    transform: (val: number) => val.toString().padStart(12, '0')
  },

  // Transmission Date & Time
  'created': {
    field: 'created',
    dataElement: 7,
    description: 'Transmission Date & Time',
    format: 'MMDDhhmmss',
    transform: (val: number) => new Date(val * 1000).toISOString().replace(/[-T:]/g, '').slice(4, 14)
  },

  // System Trace Audit Number (STAN) - usually generated per request, but mapped if tracked
  'id': {
    field: 'id',
    dataElement: 11,
    description: 'System Trace Audit Number (STAN)',
    format: 'n 6',
    transform: (val: string) => parseInt(val.slice(-6), 16).toString().slice(-6) // Mock generation from ID
  },

  // Date, Expiration
  'payment_method_details.card.exp_year': {
    field: 'payment_method_details.card.exp_year',
    dataElement: 14,
    description: 'Date, Expiration',
    format: 'YYMM',
    // Requires combination with exp_month
  },

  // Function Code (e.g., 450 for First Chargeback)
  'status': {
    field: 'status',
    dataElement: 24,
    description: 'Function Code',
    format: 'n 3',
    transform: (val: string) => {
       // Simplified mapping
       if (val === 'needs_response') return '450'; // First Chargeback
       if (val === 'won') return '205'; // Second Presentment / Representment
       return '000';
    }
  },

  // Message Reason Code
  'network_reason_code': {
    field: 'network_reason_code',
    dataElement: 25,
    description: 'Message Reason Code',
    format: 'n 4',
    transform: (val: string) => val ? val.replace('.', '').padStart(4, '0') : '0000'
  },

  // Amount, Transaction Fee (if applicable)
  'balance_transactions[0].fee': {
    field: 'balance_transactions[0].fee',
    dataElement: 28,
    description: 'Amount, Transaction Fee',
    format: 'x+n 8',
    transform: (val: number) => `D${val.toString().padStart(8, '0')}` // Debit indicator
  },

  // Retrieval Reference Number (RRN) - critical for matching
  'charge': {
    field: 'charge',
    dataElement: 37,
    description: 'Retrieval Reference Number',
    format: 'an 12',
    // Usually derived from the original transaction reference
  },

  // Authorization Identification Response
  'payment_intent': {
    field: 'payment_intent',
    dataElement: 38,
    description: 'Authorization Identification Response',
    format: 'an 6',
  },

  // Card Acceptor Terminal Identification
  'payment_method_details.card.fingerprint': {
    field: 'payment_method_details.card.fingerprint',
    dataElement: 41,
    description: 'Card Acceptor Terminal Identification',
    format: 'ans 8',
  },

  // Card Acceptor Name/Location
  'evidence.product_description': {
    field: 'evidence.product_description',
    dataElement: 43,
    description: 'Card Acceptor Name/Location',
    format: 'ans 40',
    transform: (val: string) => val.substring(0, 40)
  },

  // Additional Data - Private
  'evidence.uncategorized_text': {
    field: 'evidence.uncategorized_text',
    dataElement: 48,
    description: 'Additional Data - Private',
    format: 'ans 999',
  },

  // Transaction Currency Code
  'currency': {
    field: 'currency',
    dataElement: 49,
    description: 'Transaction Currency Code',
    format: 'n 3',
    transform: (val: string) => {
      const map: Record<string, string> = { 'usd': '840', 'eur': '978', 'gbp': '826' };
      return map[val] || '000';
    }
  },

  // Original Data Elements (for reversals/chargebacks)
  'transaction_date': {
    field: 'transaction_date',
    dataElement: 90,
    description: 'Original Data Elements',
    format: 'n 42',
    // Complex field usually containing original MTI, STAN, Date/Time, Acquiring Inst, Fwd Inst
  }
};

/**
 * Helper to generate a partial ISO message debug string from a Dispute
 */
export function generateIsoDebugString(dispute: Dispute): string {
  const lines: string[] = [];
  lines.push(`--- ISO 8583 MAPPING DEBUG FOR DISPUTE ${dispute.id} ---`);

  for (const [key, map] of Object.entries(DISPUTE_TO_ISO8583_MAP)) {
    let value: any = undefined;
    
    // Simple deep get for demonstration
    const parts = key.split('.');
    let current: any = dispute;
    for (const part of parts) {
        if (key.includes('[0]')) {
             // simplified array handling for specific example
             const [arrayName, indexStr] = part.split('[');
             const index = parseInt(indexStr.replace(']', ''));
             current = current[arrayName] ? current[arrayName][index] : undefined;
        } else {
             current = current ? current[part] : undefined;
        }
    }
    value = current;

    if (value !== undefined) {
        const transformed = map.transform ? map.transform(value) : value;
        lines.push(`DE ${map.dataElement.toString().padStart(3, '0')} [${map.description}]: ${transformed}`);
    }
  }
  
  return lines.join('\n');
}
