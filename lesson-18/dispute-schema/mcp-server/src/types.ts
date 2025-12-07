/**
 * MCP Server Types for Bank Dispute Chatbot
 * Maps to the core dispute-schema types
 */

import { z } from 'zod';

// ============================================================================
// Dispute Reason Codes
// ============================================================================

export const DisputeReasonSchema = z.enum([
  'credit_not_processed',
  'duplicate',
  'fraudulent',
  'general',
  'product_not_received',
  'product_unacceptable',
  'subscription_canceled',
  'unrecognized',
]);

export type DisputeReason = z.infer<typeof DisputeReasonSchema>;

// ============================================================================
// Dispute Status
// ============================================================================

export const DisputeStatusSchema = z.enum([
  'needs_response',
  'under_review',
  'won',
  'lost',
  'warning_needs_response',
  'warning_under_review',
  'warning_closed',
  'charge_refunded',
]);

export type DisputeStatus = z.infer<typeof DisputeStatusSchema>;

// ============================================================================
// Card Type (for Reg E/Z determination)
// ============================================================================

export const CardTypeSchema = z.enum(['debit', 'credit', 'prepaid']);
export type CardType = z.infer<typeof CardTypeSchema>;

// ============================================================================
// Tool Input Schemas
// ============================================================================

export const FileDisputeInputSchema = z.object({
  charge_id: z.string().regex(/^ch_[a-zA-Z0-9]{24}$/, 'Invalid charge ID format'),
  reason: DisputeReasonSchema,
  complaint_narrative: z.string().max(5000).optional(),
  amount_cents: z.number().int().positive().optional(),
  merchant_name: z.string().optional(),
});

export type FileDisputeInput = z.infer<typeof FileDisputeInputSchema>;

export const CheckDisputeStatusInputSchema = z.object({
  dispute_id: z.string().regex(/^dp_[a-zA-Z0-9]{24}$/, 'Invalid dispute ID format'),
});

export type CheckDisputeStatusInput = z.infer<typeof CheckDisputeStatusInputSchema>;

export const GetComplianceDeadlineInputSchema = z.object({
  dispute_id: z.string().regex(/^dp_[a-zA-Z0-9]{24}$/).optional(),
  card_type: CardTypeSchema,
  dispute_created_at: z.number().int().positive().optional(), // Unix timestamp
  is_new_account: z.boolean().optional().default(false),
  is_foreign_transaction: z.boolean().optional().default(false),
});

export type GetComplianceDeadlineInput = z.infer<typeof GetComplianceDeadlineInputSchema>;

export const AddEvidenceInputSchema = z.object({
  dispute_id: z.string().regex(/^dp_[a-zA-Z0-9]{24}$/, 'Invalid dispute ID format'),
  evidence_type: z.enum([
    'access_activity_log',
    'billing_address',
    'cancellation_policy_disclosure',
    'cancellation_rebuttal',
    'customer_communication',
    'customer_email_address',
    'customer_name',
    'customer_purchase_ip',
    'duplicate_charge_explanation',
    'product_description',
    'refund_policy_disclosure',
    'refund_refusal_explanation',
    'service_date',
    'shipping_address',
    'shipping_carrier',
    'shipping_date',
    'shipping_tracking_number',
    'uncategorized_text',
  ]),
  content: z.string().max(20000),
  submit_to_network: z.boolean().optional().default(false),
});

export type AddEvidenceInput = z.infer<typeof AddEvidenceInputSchema>;

export const LookupTransactionInputSchema = z.object({
  account_id: z.string().optional(),
  date_from: z.string().optional(), // ISO date
  date_to: z.string().optional(), // ISO date
  amount_cents: z.number().int().optional(),
  amount_tolerance_cents: z.number().int().optional().default(0),
  merchant_name: z.string().optional(),
  limit: z.number().int().min(1).max(50).optional().default(10),
});

export type LookupTransactionInput = z.infer<typeof LookupTransactionInputSchema>;

export const FraudScoreInputSchema = z.object({
  transaction_id: z.string().optional(),
  amount_cents: z.number().int().positive(),
  merchant_category_code: z.string().optional(),
  is_card_present: z.boolean().optional().default(true),
  distance_from_home_miles: z.number().optional().default(0),
  account_age_days: z.number().int().optional().default(365),
  disputes_last_90_days: z.number().int().optional().default(0),
  avg_transaction_amount_cents: z.number().int().optional(),
});

export type FraudScoreInput = z.infer<typeof FraudScoreInputSchema>;

// ============================================================================
// Tool Output Types
// ============================================================================

export interface FileDisputeOutput {
  success: boolean;
  dispute_id: string;
  status: DisputeStatus;
  evidence_due_by: number; // Unix timestamp
  evidence_due_by_human: string; // Human-readable date
  provisional_credit_eligible: boolean;
  provisional_credit_deadline_days: number;
  message: string;
}

export interface CheckDisputeStatusOutput {
  dispute_id: string;
  status: DisputeStatus;
  reason: DisputeReason;
  amount_cents: number;
  currency: string;
  created_at: number;
  evidence_submitted: boolean;
  evidence_due_by: number | null;
  past_due: boolean;
  network_reason_code: string | null;
  resolution_message: string;
}

export interface ComplianceDeadline {
  label: string;
  due_date: number;
  due_date_human: string;
  days_from_now: number;
  action_required: string;
  regulation: 'Reg E' | 'Reg Z' | 'Non-Regulated';
}

export interface GetComplianceDeadlineOutput {
  regulation: 'Reg E' | 'Reg Z' | 'Non-Regulated';
  deadlines: ComplianceDeadline[];
  summary: string;
  urgent_action_required: boolean;
}

export interface AddEvidenceOutput {
  success: boolean;
  dispute_id: string;
  evidence_type: string;
  submission_count: number;
  total_text_characters: number;
  characters_remaining: number;
  submitted_to_network: boolean;
  message: string;
}

export interface Transaction {
  transaction_id: string;
  charge_id: string;
  amount_cents: number;
  currency: string;
  merchant_name: string;
  merchant_category_code: string;
  transaction_date: string;
  is_disputed: boolean;
  existing_dispute_id: string | null;
}

export interface LookupTransactionOutput {
  transactions: Transaction[];
  total_found: number;
  has_more: boolean;
  message: string;
}

export interface FraudScoreOutput {
  fraud_score: number; // 0-100
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  indicators: string[];
  recommendation: 'approve' | 'review' | 'deny';
  explanation: string;
}
