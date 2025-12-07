/**
 * Textract Validation Functions for Bank Statement Processing
 *
 * Provides validation logic for extracted bank statement data
 * to ensure accuracy meets dispute evidence requirements.
 */

import type {
  BankStatementData,
  ExtractedTransaction,
  ValidationResult,
  ValidationWarning,
  ValidationError,
  FieldValidation,
  AcceptanceCriteria,
  ExpectedExtractionResult,
  TextractTestCase,
} from './textract-types';

// ============================================================================
// Validation Constants
// ============================================================================

/** Minimum acceptable confidence for dispute evidence */
export const MIN_EVIDENCE_CONFIDENCE = 85;

/** Fields required for dispute evidence */
export const REQUIRED_DISPUTE_FIELDS = [
  'account_holder_name',
  'account_number_masked',
  'statement_period',
  'transactions',
  'closing_balance',
];

/** Maximum age of statement for dispute evidence (days) */
export const MAX_STATEMENT_AGE_DAYS = 90;

/** Tolerance for balance verification (currency units) */
export const BALANCE_TOLERANCE = 0.01;

// ============================================================================
// Core Validation Functions
// ============================================================================

/**
 * Validate extracted bank statement data against acceptance criteria
 */
export function validateBankStatementExtraction(
  data: BankStatementData,
  criteria: AcceptanceCriteria
): ValidationResult {
  const fieldValidations: FieldValidation[] = [];
  const warnings: ValidationWarning[] = [];
  const errors: ValidationError[] = [];
  const humanReviewReasons: string[] = [];

  // Validate overall confidence
  const meetsConfidenceThreshold = data.overall_confidence >= criteria.min_overall_confidence;
  if (!meetsConfidenceThreshold) {
    warnings.push({
      code: 'LOW_OVERALL_CONFIDENCE',
      message: `Overall confidence ${data.overall_confidence}% below threshold ${criteria.min_overall_confidence}%`,
      suggestion: 'Consider manual review or re-scanning document',
    });
    humanReviewReasons.push('Low overall confidence score');
  }

  // Validate required fields
  const missingFields = validateRequiredFields(data, criteria.required_fields, fieldValidations);
  const hasRequiredFields = missingFields.length === 0;
  if (!hasRequiredFields) {
    errors.push({
      code: 'MISSING_REQUIRED_FIELDS',
      message: `Missing required fields: ${missingFields.join(', ')}`,
      recoverable: false,
    });
  }

  // Validate field-level confidence
  validateFieldConfidence(data, criteria.min_field_confidence, fieldValidations, warnings);

  // Validate data consistency
  const consistencyResult = validateDataConsistency(data, errors, warnings);

  // Validate transactions
  validateTransactions(data.transactions, criteria, fieldValidations, warnings, errors);

  // Check if human review is needed
  const requiresHumanReview =
    !meetsConfidenceThreshold ||
    !hasRequiredFields ||
    !consistencyResult ||
    humanReviewReasons.length > 0;

  return {
    is_valid: hasRequiredFields && consistencyResult && errors.filter((e) => !e.recoverable).length === 0,
    meets_confidence_threshold: meetsConfidenceThreshold,
    has_required_fields: hasRequiredFields,
    consistency_checks_passed: consistencyResult,
    field_validations: fieldValidations,
    warnings,
    errors,
    requires_human_review: requiresHumanReview,
    human_review_reasons: humanReviewReasons,
  };
}

/**
 * Validate required fields are present and have acceptable confidence
 */
function validateRequiredFields(
  data: BankStatementData,
  requiredFields: string[],
  validations: FieldValidation[]
): string[] {
  const missingFields: string[] = [];

  for (const field of requiredFields) {
    const validation = checkFieldPresence(data, field);
    validations.push(validation);
    if (!validation.is_valid) {
      missingFields.push(field);
    }
  }

  return missingFields;
}

/**
 * Check if a specific field is present in the data
 */
function checkFieldPresence(data: BankStatementData, field: string): FieldValidation {
  switch (field) {
    case 'account_holder_name':
      return {
        field,
        is_valid: !!data.account?.account_holder_name,
        confidence: data.account?.confidence_account_holder ?? 0,
        message: data.account?.account_holder_name ? undefined : 'Account holder name not extracted',
      };

    case 'account_number_masked':
      return {
        field,
        is_valid: !!data.account?.account_number_masked,
        confidence: data.account?.confidence_account_number ?? 0,
        message: data.account?.account_number_masked ? undefined : 'Account number not extracted',
      };

    case 'statement_period':
      return {
        field,
        is_valid: !!(data.statement_period?.start_date && data.statement_period?.end_date),
        confidence: Math.min(
          data.statement_period?.confidence_start ?? 0,
          data.statement_period?.confidence_end ?? 0
        ),
        message:
          data.statement_period?.start_date && data.statement_period?.end_date
            ? undefined
            : 'Statement period not fully extracted',
      };

    case 'transactions':
      return {
        field,
        is_valid: data.transactions.length > 0,
        confidence: calculateAverageTransactionConfidence(data.transactions),
        message: data.transactions.length > 0 ? undefined : 'No transactions extracted',
      };

    case 'closing_balance':
      return {
        field,
        is_valid: data.summary?.closing_balance !== undefined,
        confidence: data.summary?.confidence_closing ?? 0,
        message: data.summary?.closing_balance !== undefined ? undefined : 'Closing balance not extracted',
      };

    case 'opening_balance':
      return {
        field,
        is_valid: data.summary?.opening_balance !== undefined,
        confidence: data.summary?.confidence_opening ?? 0,
        message: data.summary?.opening_balance !== undefined ? undefined : 'Opening balance not extracted',
      };

    case 'minimum_payment':
      // Credit card specific
      return {
        field,
        is_valid: true, // Optional for most statements
        confidence: 100,
      };

    default:
      return {
        field,
        is_valid: true,
        confidence: 0,
        message: `Unknown field: ${field}`,
      };
  }
}

/**
 * Validate field-level confidence scores
 */
function validateFieldConfidence(
  data: BankStatementData,
  minConfidence: number,
  validations: FieldValidation[],
  warnings: ValidationWarning[]
): void {
  const lowConfidenceFields: string[] = [];

  // Check account fields
  if (data.account) {
    if (data.account.confidence_account_holder < minConfidence) {
      lowConfidenceFields.push('account_holder_name');
    }
    if (data.account.confidence_account_number < minConfidence) {
      lowConfidenceFields.push('account_number');
    }
  }

  // Check summary fields
  if (data.summary) {
    if (data.summary.confidence_opening < minConfidence) {
      lowConfidenceFields.push('opening_balance');
    }
    if (data.summary.confidence_closing < minConfidence) {
      lowConfidenceFields.push('closing_balance');
    }
  }

  if (lowConfidenceFields.length > 0) {
    warnings.push({
      code: 'LOW_FIELD_CONFIDENCE',
      message: `Fields below confidence threshold: ${lowConfidenceFields.join(', ')}`,
      suggestion: 'Review these fields manually for accuracy',
    });
  }
}

/**
 * Validate data consistency (balances, dates, etc.)
 */
function validateDataConsistency(
  data: BankStatementData,
  errors: ValidationError[],
  warnings: ValidationWarning[]
): boolean {
  let isConsistent = true;

  // Validate balance calculation
  if (data.summary?.opening_balance !== undefined && data.summary?.closing_balance !== undefined) {
    const calculatedClosing = calculateExpectedClosingBalance(
      data.summary.opening_balance,
      data.transactions
    );

    if (calculatedClosing !== null) {
      const difference = Math.abs(calculatedClosing - data.summary.closing_balance);
      if (difference > BALANCE_TOLERANCE) {
        warnings.push({
          code: 'BALANCE_MISMATCH',
          message: `Calculated closing balance (${calculatedClosing.toFixed(2)}) differs from extracted (${data.summary.closing_balance.toFixed(2)})`,
          suggestion: 'Verify transaction amounts are correctly extracted',
        });
        // Don't fail validation for small mismatches, but flag for review
        if (difference > 1.0) {
          isConsistent = false;
        }
      }
    }
  }

  // Validate date sequence
  if (data.statement_period?.start_date && data.statement_period?.end_date) {
    const start = new Date(data.statement_period.start_date);
    const end = new Date(data.statement_period.end_date);

    if (start > end) {
      errors.push({
        code: 'INVALID_DATE_RANGE',
        message: 'Statement start date is after end date',
        recoverable: false,
      });
      isConsistent = false;
    }

    // Check statement age
    const now = new Date();
    const ageInDays = Math.floor((now.getTime() - end.getTime()) / (1000 * 60 * 60 * 24));
    if (ageInDays > MAX_STATEMENT_AGE_DAYS) {
      warnings.push({
        code: 'STATEMENT_TOO_OLD',
        message: `Statement is ${ageInDays} days old (max ${MAX_STATEMENT_AGE_DAYS} days for evidence)`,
        suggestion: 'Request a more recent statement',
      });
    }
  }

  // Validate transaction dates are within statement period
  if (data.statement_period?.start_date && data.statement_period?.end_date) {
    const start = new Date(data.statement_period.start_date);
    const end = new Date(data.statement_period.end_date);

    const outOfRangeTransactions = data.transactions.filter((t) => {
      if (!t.date) return false;
      const txDate = new Date(t.date);
      return txDate < start || txDate > end;
    });

    if (outOfRangeTransactions.length > 0) {
      warnings.push({
        code: 'TRANSACTIONS_OUTSIDE_PERIOD',
        message: `${outOfRangeTransactions.length} transaction(s) have dates outside statement period`,
        suggestion: 'Verify transaction date extraction',
      });
    }
  }

  return isConsistent;
}

/**
 * Validate individual transactions
 */
function validateTransactions(
  transactions: ExtractedTransaction[],
  criteria: AcceptanceCriteria,
  validations: FieldValidation[],
  warnings: ValidationWarning[],
  errors: ValidationError[]
): void {
  if (transactions.length === 0) {
    return;
  }

  let lowConfidenceCount = 0;
  let missingDateCount = 0;
  let missingAmountCount = 0;

  for (const tx of transactions) {
    if (tx.confidence_date < criteria.min_field_confidence) {
      lowConfidenceCount++;
    }
    if (!tx.date) {
      missingDateCount++;
    }
    if (tx.amount === undefined) {
      missingAmountCount++;
    }
  }

  const errorRate = (lowConfidenceCount + missingDateCount + missingAmountCount) / transactions.length;

  if (errorRate > criteria.max_transaction_error_rate) {
    warnings.push({
      code: 'HIGH_TRANSACTION_ERROR_RATE',
      message: `Transaction error rate ${(errorRate * 100).toFixed(1)}% exceeds threshold ${(criteria.max_transaction_error_rate * 100).toFixed(1)}%`,
      suggestion: 'Manual review of transactions recommended',
    });
  }

  validations.push({
    field: 'transaction_quality',
    is_valid: errorRate <= criteria.max_transaction_error_rate,
    confidence: (1 - errorRate) * 100,
    message:
      errorRate <= criteria.max_transaction_error_rate
        ? undefined
        : `${lowConfidenceCount} low confidence, ${missingDateCount} missing dates, ${missingAmountCount} missing amounts`,
  });
}

// ============================================================================
// Helper Functions
// ============================================================================

/**
 * Calculate expected closing balance from opening + transactions
 */
function calculateExpectedClosingBalance(
  openingBalance: number,
  transactions: ExtractedTransaction[]
): number | null {
  if (transactions.length === 0) {
    return null;
  }

  let balance = openingBalance;
  for (const tx of transactions) {
    if (tx.amount !== undefined) {
      if (tx.type === 'credit') {
        balance += tx.amount;
      } else if (tx.type === 'debit') {
        balance -= tx.amount;
      }
    }
  }

  return Math.round(balance * 100) / 100; // Round to 2 decimal places
}

/**
 * Calculate average confidence across transactions
 */
function calculateAverageTransactionConfidence(transactions: ExtractedTransaction[]): number {
  if (transactions.length === 0) {
    return 0;
  }

  const totalConfidence = transactions.reduce((sum, tx) => {
    return (
      sum +
      (tx.confidence_date +
        tx.confidence_description +
        tx.confidence_amount +
        tx.confidence_type) /
        4
    );
  }, 0);

  return totalConfidence / transactions.length;
}

// ============================================================================
// Test Validation Functions
// ============================================================================

/**
 * Validate extraction results against expected values
 */
export function validateAgainstExpected(
  data: BankStatementData,
  expected: ExpectedExtractionResult
): ValidationResult {
  const fieldValidations: FieldValidation[] = [];
  const warnings: ValidationWarning[] = [];
  const errors: ValidationError[] = [];

  // Validate account holder
  if (expected.account_holder_contains) {
    const matches = data.account?.account_holder_name
      ?.toLowerCase()
      .includes(expected.account_holder_contains.toLowerCase());
    fieldValidations.push({
      field: 'account_holder_name',
      is_valid: !!matches,
      confidence: data.account?.confidence_account_holder ?? 0,
      message: matches ? undefined : `Expected to contain "${expected.account_holder_contains}"`,
    });
  }

  // Validate bank name
  if (expected.bank_name) {
    const matches = data.account?.bank_name
      ?.toLowerCase()
      .includes(expected.bank_name.toLowerCase());
    fieldValidations.push({
      field: 'bank_name',
      is_valid: !!matches,
      confidence: data.account?.confidence_bank_name ?? 0,
      message: matches ? undefined : `Expected bank name "${expected.bank_name}"`,
    });
  }

  // Validate transaction count
  if (expected.transaction_count_min !== undefined || expected.transaction_count_max !== undefined) {
    const count = data.transactions.length;
    const minOk = expected.transaction_count_min === undefined || count >= expected.transaction_count_min;
    const maxOk = expected.transaction_count_max === undefined || count <= expected.transaction_count_max;

    fieldValidations.push({
      field: 'transaction_count',
      is_valid: minOk && maxOk,
      confidence: 100,
      message:
        minOk && maxOk
          ? undefined
          : `Transaction count ${count} outside expected range [${expected.transaction_count_min ?? 0}-${expected.transaction_count_max ?? '∞'}]`,
    });
  }

  // Validate totals
  if (expected.totals) {
    const tolerance = expected.totals.balance_tolerance ?? BALANCE_TOLERANCE;

    if (expected.totals.opening_balance !== undefined) {
      const diff = Math.abs((data.summary?.opening_balance ?? 0) - expected.totals.opening_balance);
      fieldValidations.push({
        field: 'opening_balance',
        is_valid: diff <= tolerance,
        confidence: data.summary?.confidence_opening ?? 0,
        message: diff <= tolerance ? undefined : `Opening balance off by ${diff.toFixed(2)}`,
      });
    }

    if (expected.totals.closing_balance !== undefined) {
      const diff = Math.abs((data.summary?.closing_balance ?? 0) - expected.totals.closing_balance);
      fieldValidations.push({
        field: 'closing_balance',
        is_valid: diff <= tolerance,
        confidence: data.summary?.confidence_closing ?? 0,
        message: diff <= tolerance ? undefined : `Closing balance off by ${diff.toFixed(2)}`,
      });
    }
  }

  // Validate sample transactions
  if (expected.sample_transactions) {
    for (let i = 0; i < expected.sample_transactions.length; i++) {
      const expectedTx = expected.sample_transactions[i];
      const found = data.transactions.some((tx) => {
        const dateMatch =
          !expectedTx.date_contains || tx.date?.includes(expectedTx.date_contains);
        const descMatch =
          !expectedTx.description_contains ||
          tx.description?.toLowerCase().includes(expectedTx.description_contains.toLowerCase());
        const amountMatch =
          expectedTx.amount === undefined ||
          (tx.amount !== undefined &&
            Math.abs(tx.amount - expectedTx.amount) <= (expectedTx.amount_tolerance ?? 0.01));

        return dateMatch && descMatch && amountMatch;
      });

      fieldValidations.push({
        field: `sample_transaction_${i + 1}`,
        is_valid: found,
        confidence: found ? 100 : 0,
        message: found ? undefined : `Expected transaction not found: ${JSON.stringify(expectedTx)}`,
      });
    }
  }

  const allValid = fieldValidations.every((v) => v.is_valid);

  return {
    is_valid: allValid,
    meets_confidence_threshold: true,
    has_required_fields: true,
    consistency_checks_passed: allValid,
    field_validations: fieldValidations,
    warnings,
    errors,
    requires_human_review: !allValid,
    human_review_reasons: allValid ? [] : ['Expected values did not match'],
  };
}

/**
 * Run a complete test case
 */
export function runTestCase(
  testCase: TextractTestCase,
  extractedData: BankStatementData
): {
  test_id: string;
  passed: boolean;
  validation_result: ValidationResult;
  expected_result: ValidationResult;
  execution_time_ms?: number;
} {
  // Validate against acceptance criteria
  const validationResult = validateBankStatementExtraction(
    extractedData,
    testCase.acceptance_criteria
  );

  // Validate against expected results
  const expectedResult = validateAgainstExpected(extractedData, testCase.expected);

  const passed = validationResult.is_valid && expectedResult.is_valid;

  return {
    test_id: testCase.id,
    passed,
    validation_result: validationResult,
    expected_result: expectedResult,
  };
}

// ============================================================================
// Exports
// ============================================================================

export {
  calculateExpectedClosingBalance,
  calculateAverageTransactionConfidence,
};
