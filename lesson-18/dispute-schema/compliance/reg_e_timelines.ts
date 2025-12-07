/**
 * Regulatory Compliance Timeline Logic
 * Implements US Regulation E (Electronic Fund Transfer Act) and Regulation Z (Truth in Lending Act)
 * timeline requirements for dispute resolution.
 */

import { Dispute } from '../dispute_types';

// ============================================================================
// Types
// ============================================================================

export type RegulationType = 'Reg E' | 'Reg Z' | 'Non-Regulated';

export interface ComplianceDeadline {
  label: string;
  dueDate: number; // Unix timestamp
  daysFromStart: number;
  description: string;
  actionRequired: 'provisional_credit' | 'acknowledgment' | 'resolution' | 'notification';
}

export interface ComplianceState {
  regulation: RegulationType;
  isNewAccount: boolean; // Account < 30 days old
  isForeignTransaction: boolean; // Foreign transaction
  isPosTransaction: boolean; // Point of Sale (vs ATM)
  
  deadlines: ComplianceDeadline[];
  finalResolutionDeadline: number;
}

// ============================================================================
// Constants
// ============================================================================

const SECONDS_IN_DAY = 86400;

// ============================================================================
// Logic
// ============================================================================

/**
 * Determines the applicable regulation and calculates critical deadlines.
 * @param dispute The dispute object
 * @param accountAgeDays Age of the account in days (mocked or passed in)
 */
export function calculateComplianceState(dispute: Dispute, accountAgeDays: number = 100): ComplianceState {
  const funding = dispute.payment_method_details?.card?.funding;
  const created = dispute.created;
  
  // Determine Regulation
  let regulation: RegulationType = 'Non-Regulated';
  if (funding === 'debit' || funding === 'prepaid') {
    regulation = 'Reg E';
  } else if (funding === 'credit') {
    regulation = 'Reg Z';
  }

  // Classify Transaction Attributes (Heuristics)
  const isNewAccount = accountAgeDays < 30;
  const isForeignTransaction = dispute.payment_method_details?.card?.country !== 'US'; // Simplified check
  const isPosTransaction = true; // Default assumption for card disputes (vs ATM)

  const deadlines: ComplianceDeadline[] = [];
  
  if (regulation === 'Reg E') {
    // Rule: 10 Business Days for Provisional Credit
    // (Simplified to 10 calendar days + buffer for business days logic in real implementation)
    deadlines.push({
      label: 'Provisional Credit Deadline',
      daysFromStart: 10,
      dueDate: addDays(created, 10),
      description: 'Must provide provisional credit if investigation is not complete.',
      actionRequired: 'provisional_credit'
    });

    // Rule: Investigation Limits
    // 45 days standard, 90 days for POS, Foreign, or New Accounts
    const investigationDays = (isNewAccount || isForeignTransaction || isPosTransaction) ? 90 : 45;
    
    deadlines.push({
      label: 'Investigation Deadline',
      daysFromStart: investigationDays,
      dueDate: addDays(created, investigationDays),
      description: `Complete investigation within ${investigationDays} days.`,
      actionRequired: 'resolution'
    });

  } else if (regulation === 'Reg Z') {
    // Rule: Acknowledge within 30 days
    deadlines.push({
      label: 'Acknowledgment Deadline',
      daysFromStart: 30,
      dueDate: addDays(created, 30),
      description: 'Must acknowledge receipt of billing error notice.',
      actionRequired: 'acknowledgment'
    });

    // Rule: Resolve within 2 billing cycles (max 90 days)
    deadlines.push({
      label: 'Resolution Deadline',
      daysFromStart: 90,
      dueDate: addDays(created, 90),
      description: 'Must resolve dispute within 2 billing cycles (max 90 days).',
      actionRequired: 'resolution'
    });
  }

  const finalDeadline = deadlines.length > 0 
    ? Math.max(...deadlines.map(d => d.dueDate)) 
    : addDays(created, 30); // Default fallback

  return {
    regulation,
    isNewAccount,
    isForeignTransaction,
    isPosTransaction,
    deadlines,
    finalResolutionDeadline: finalDeadline
  };
}

// ============================================================================
// Helpers
// ============================================================================

function addDays(timestamp: number, days: number): number {
  return timestamp + (days * SECONDS_IN_DAY);
}

/**
 * Checks if the dispute is currently compliant based on current time
 */
export function checkComplianceStatus(state: ComplianceState, currentTimestamp: number = Date.now() / 1000): { compliant: boolean, breachedDeadlines: ComplianceDeadline[] } {
  const breached = state.deadlines.filter(d => d.dueDate < currentTimestamp);
  return {
    compliant: breached.length === 0,
    breachedDeadlines: breached
  };
}
