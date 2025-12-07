/**
 * Textract Validation Test Suite
 *
 * Comprehensive test cases for validating bank statement extraction
 * accuracy against dispute evidence requirements.
 *
 * Usage:
 * 1. Upload sample bank statements to S3 test bucket
 * 2. Run extraction using Lambda or local Textract client
 * 3. Execute test suite against extraction results
 */

import type {
  TextractTestCase,
  BankStatementData,
  ExpectedExtractionResult,
  AcceptanceCriteria,
} from './textract-types';
import {
  validateBankStatementExtraction,
  validateAgainstExpected,
  runTestCase,
  MIN_EVIDENCE_CONFIDENCE,
} from './textract-validator';

// ============================================================================
// Test Suite Configuration
// ============================================================================

/**
 * Test suite metadata
 */
export const TEST_SUITE_INFO = {
  name: 'Bank Statement Textract Validation',
  version: '1.0.0',
  description: 'Validates Textract extraction accuracy for dispute evidence',
  minimum_tests_required: 10,
  passing_threshold: 0.90, // 90% of tests must pass
};

// ============================================================================
// Standard Test Cases
// ============================================================================

/**
 * Test Case 1: Chase Checking - High Quality PDF
 */
export const TEST_CHASE_CHECKING: TextractTestCase = {
  id: 'TC001',
  name: 'Chase Checking Statement - Standard',
  description: 'High quality Chase checking account PDF statement',
  input: {
    document_type: 'bank_statement',
    bank_name: 'Chase',
    format: 'pdf',
    location: 's3://dispute-evidence-test/bank-statements/chase/chase_checking_sample.pdf',
    characteristics: {
      page_count: 3,
      has_tables: true,
      has_handwriting: false,
      quality: 'high',
      is_scanned: false,
    },
  },
  expected: {
    bank_name: 'Chase',
    transaction_count_min: 15,
    transaction_count_max: 50,
    date_range: {
      start_contains: '2024-10',
      end_contains: '2024-11',
    },
    totals: {
      balance_tolerance: 0.01,
    },
  },
  acceptance_criteria: {
    min_overall_confidence: 90,
    min_field_confidence: 85,
    max_extraction_time_ms: 5000,
    required_fields: ['account_holder_name', 'account_number_masked', 'transactions', 'closing_balance'],
    max_transaction_error_rate: 0.05,
  },
};

/**
 * Test Case 2: Bank of America - Multiple Pages
 */
export const TEST_BOFA_MULTIPAGE: TextractTestCase = {
  id: 'TC002',
  name: 'Bank of America Statement - Multi-Page',
  description: 'Bank of America statement spanning multiple pages',
  input: {
    document_type: 'bank_statement',
    bank_name: 'Bank of America',
    format: 'pdf',
    location: 's3://dispute-evidence-test/bank-statements/bofa/bofa_multipage_sample.pdf',
    characteristics: {
      page_count: 6,
      has_tables: true,
      has_handwriting: false,
      quality: 'high',
      is_scanned: false,
    },
  },
  expected: {
    bank_name: 'Bank of America',
    transaction_count_min: 50,
    transaction_count_max: 150,
  },
  acceptance_criteria: {
    min_overall_confidence: 88,
    min_field_confidence: 82,
    max_extraction_time_ms: 10000,
    required_fields: ['account_holder_name', 'transactions', 'closing_balance'],
    max_transaction_error_rate: 0.07,
  },
};

/**
 * Test Case 3: Wells Fargo - With Check Images
 */
export const TEST_WELLS_FARGO_CHECKS: TextractTestCase = {
  id: 'TC003',
  name: 'Wells Fargo Statement - With Check Images',
  description: 'Wells Fargo statement including deposited check images',
  input: {
    document_type: 'bank_statement',
    bank_name: 'Wells Fargo',
    format: 'pdf',
    location: 's3://dispute-evidence-test/bank-statements/wellsfargo/wf_with_checks_sample.pdf',
    characteristics: {
      page_count: 4,
      has_tables: true,
      has_handwriting: true, // Check signatures
      quality: 'high',
      is_scanned: false,
    },
  },
  expected: {
    bank_name: 'Wells Fargo',
    transaction_count_min: 10,
  },
  acceptance_criteria: {
    min_overall_confidence: 85,
    min_field_confidence: 80,
    max_extraction_time_ms: 7000,
    required_fields: ['account_holder_name', 'transactions'],
    max_transaction_error_rate: 0.08,
  },
};

/**
 * Test Case 4: Citi Credit Card Statement
 */
export const TEST_CITI_CREDIT: TextractTestCase = {
  id: 'TC004',
  name: 'Citi Credit Card Statement',
  description: 'Citi credit card statement with rewards and payment summary',
  input: {
    document_type: 'credit_card_statement',
    bank_name: 'Citi',
    format: 'pdf',
    location: 's3://dispute-evidence-test/bank-statements/citi/citi_credit_sample.pdf',
    characteristics: {
      page_count: 5,
      has_tables: true,
      has_handwriting: false,
      quality: 'high',
      is_scanned: false,
    },
  },
  expected: {
    bank_name: 'Citi',
    transaction_count_min: 20,
  },
  acceptance_criteria: {
    min_overall_confidence: 88,
    min_field_confidence: 82,
    max_extraction_time_ms: 8000,
    required_fields: ['account_holder_name', 'account_number_masked', 'transactions', 'closing_balance'],
    max_transaction_error_rate: 0.06,
  },
};

/**
 * Test Case 5: Scanned Statement - Low Quality
 */
export const TEST_SCANNED_LOW_QUALITY: TextractTestCase = {
  id: 'TC005',
  name: 'Scanned Statement - Low Quality',
  description: 'Scanned paper statement with poor image quality',
  input: {
    document_type: 'bank_statement',
    bank_name: 'Generic',
    format: 'png',
    location: 's3://dispute-evidence-test/bank-statements/scanned/scanned_low_quality.png',
    characteristics: {
      page_count: 2,
      has_tables: true,
      has_handwriting: true,
      quality: 'low',
      is_scanned: true,
    },
  },
  expected: {
    transaction_count_min: 5,
  },
  acceptance_criteria: {
    min_overall_confidence: 65,
    min_field_confidence: 55,
    max_extraction_time_ms: 15000,
    required_fields: ['transactions'],
    max_transaction_error_rate: 0.20,
  },
};

/**
 * Test Case 6: Scanned Statement - Medium Quality
 */
export const TEST_SCANNED_MEDIUM_QUALITY: TextractTestCase = {
  id: 'TC006',
  name: 'Scanned Statement - Medium Quality',
  description: 'Scanned paper statement with acceptable image quality',
  input: {
    document_type: 'bank_statement',
    bank_name: 'Generic',
    format: 'jpg',
    location: 's3://dispute-evidence-test/bank-statements/scanned/scanned_medium_quality.jpg',
    characteristics: {
      page_count: 2,
      has_tables: true,
      has_handwriting: false,
      quality: 'medium',
      is_scanned: true,
    },
  },
  expected: {
    transaction_count_min: 8,
  },
  acceptance_criteria: {
    min_overall_confidence: 75,
    min_field_confidence: 70,
    max_extraction_time_ms: 12000,
    required_fields: ['account_holder_name', 'transactions'],
    max_transaction_error_rate: 0.12,
  },
};

/**
 * Test Case 7: HSBC UK Statement (International)
 */
export const TEST_HSBC_UK: TextractTestCase = {
  id: 'TC007',
  name: 'HSBC UK Statement - International Format',
  description: 'UK bank statement with different date and currency format',
  input: {
    document_type: 'bank_statement',
    bank_name: 'HSBC',
    format: 'pdf',
    location: 's3://dispute-evidence-test/bank-statements/international/hsbc_uk_sample.pdf',
    characteristics: {
      page_count: 3,
      has_tables: true,
      has_handwriting: false,
      quality: 'high',
      is_scanned: false,
    },
  },
  expected: {
    bank_name: 'HSBC',
    transaction_count_min: 10,
  },
  acceptance_criteria: {
    min_overall_confidence: 82,
    min_field_confidence: 78,
    max_extraction_time_ms: 6000,
    required_fields: ['account_holder_name', 'transactions'],
    max_transaction_error_rate: 0.10,
  },
};

/**
 * Test Case 8: Capital One 360 - Online Statement
 */
export const TEST_CAPITAL_ONE: TextractTestCase = {
  id: 'TC008',
  name: 'Capital One 360 Statement',
  description: 'Capital One online banking statement',
  input: {
    document_type: 'bank_statement',
    bank_name: 'Capital One',
    format: 'pdf',
    location: 's3://dispute-evidence-test/bank-statements/capitalone/cap1_sample.pdf',
    characteristics: {
      page_count: 2,
      has_tables: true,
      has_handwriting: false,
      quality: 'high',
      is_scanned: false,
    },
  },
  expected: {
    bank_name: 'Capital One',
    transaction_count_min: 10,
  },
  acceptance_criteria: {
    min_overall_confidence: 90,
    min_field_confidence: 85,
    max_extraction_time_ms: 4000,
    required_fields: ['account_holder_name', 'account_number_masked', 'transactions', 'closing_balance'],
    max_transaction_error_rate: 0.05,
  },
};

/**
 * Test Case 9: PNC Bank - Business Account
 */
export const TEST_PNC_BUSINESS: TextractTestCase = {
  id: 'TC009',
  name: 'PNC Business Account Statement',
  description: 'PNC business checking account with more complex layout',
  input: {
    document_type: 'bank_statement',
    bank_name: 'PNC',
    format: 'pdf',
    location: 's3://dispute-evidence-test/bank-statements/pnc/pnc_business_sample.pdf',
    characteristics: {
      page_count: 5,
      has_tables: true,
      has_handwriting: false,
      quality: 'high',
      is_scanned: false,
    },
  },
  expected: {
    bank_name: 'PNC',
    transaction_count_min: 30,
  },
  acceptance_criteria: {
    min_overall_confidence: 85,
    min_field_confidence: 80,
    max_extraction_time_ms: 8000,
    required_fields: ['account_holder_name', 'transactions', 'closing_balance'],
    max_transaction_error_rate: 0.08,
  },
};

/**
 * Test Case 10: TD Bank - Combined Statement
 */
export const TEST_TD_COMBINED: TextractTestCase = {
  id: 'TC010',
  name: 'TD Bank Combined Statement',
  description: 'TD Bank statement with checking and savings combined',
  input: {
    document_type: 'bank_statement',
    bank_name: 'TD Bank',
    format: 'pdf',
    location: 's3://dispute-evidence-test/bank-statements/td/td_combined_sample.pdf',
    characteristics: {
      page_count: 4,
      has_tables: true,
      has_handwriting: false,
      quality: 'high',
      is_scanned: false,
    },
  },
  expected: {
    bank_name: 'TD',
    transaction_count_min: 15,
  },
  acceptance_criteria: {
    min_overall_confidence: 85,
    min_field_confidence: 80,
    max_extraction_time_ms: 7000,
    required_fields: ['account_holder_name', 'transactions'],
    max_transaction_error_rate: 0.08,
  },
};

// ============================================================================
// Edge Case Test Cases
// ============================================================================

/**
 * Test Case 11: Empty Statement (No Transactions)
 */
export const TEST_EMPTY_STATEMENT: TextractTestCase = {
  id: 'TC011',
  name: 'Empty Statement - No Transactions',
  description: 'Statement period with no transactions (edge case)',
  input: {
    document_type: 'bank_statement',
    bank_name: 'Generic',
    format: 'pdf',
    location: 's3://dispute-evidence-test/bank-statements/edge-cases/empty_statement.pdf',
    characteristics: {
      page_count: 1,
      has_tables: false,
      has_handwriting: false,
      quality: 'high',
      is_scanned: false,
    },
  },
  expected: {
    transaction_count_min: 0,
    transaction_count_max: 0,
  },
  acceptance_criteria: {
    min_overall_confidence: 80,
    min_field_confidence: 75,
    max_extraction_time_ms: 3000,
    required_fields: ['account_holder_name', 'closing_balance'],
    max_transaction_error_rate: 0.0,
  },
};

/**
 * Test Case 12: Multi-Currency Statement
 */
export const TEST_MULTI_CURRENCY: TextractTestCase = {
  id: 'TC012',
  name: 'Multi-Currency Statement',
  description: 'Statement with transactions in multiple currencies',
  input: {
    document_type: 'bank_statement',
    bank_name: 'HSBC',
    format: 'pdf',
    location: 's3://dispute-evidence-test/bank-statements/edge-cases/multi_currency.pdf',
    characteristics: {
      page_count: 3,
      has_tables: true,
      has_handwriting: false,
      quality: 'high',
      is_scanned: false,
    },
  },
  expected: {
    transaction_count_min: 10,
  },
  acceptance_criteria: {
    min_overall_confidence: 80,
    min_field_confidence: 75,
    max_extraction_time_ms: 8000,
    required_fields: ['transactions'],
    max_transaction_error_rate: 0.12,
  },
};

// ============================================================================
// All Test Cases Collection
// ============================================================================

export const ALL_TEST_CASES: TextractTestCase[] = [
  TEST_CHASE_CHECKING,
  TEST_BOFA_MULTIPAGE,
  TEST_WELLS_FARGO_CHECKS,
  TEST_CITI_CREDIT,
  TEST_SCANNED_LOW_QUALITY,
  TEST_SCANNED_MEDIUM_QUALITY,
  TEST_HSBC_UK,
  TEST_CAPITAL_ONE,
  TEST_PNC_BUSINESS,
  TEST_TD_COMBINED,
  TEST_EMPTY_STATEMENT,
  TEST_MULTI_CURRENCY,
];

// ============================================================================
// Test Runner Types
// ============================================================================

/**
 * Test execution result
 */
export interface TestExecutionResult {
  test_case: TextractTestCase;
  passed: boolean;
  validation_result: ReturnType<typeof validateBankStatementExtraction>;
  expected_result: ReturnType<typeof validateAgainstExpected>;
  execution_time_ms: number;
  error?: string;
}

/**
 * Test suite execution summary
 */
export interface TestSuiteSummary {
  suite_name: string;
  total_tests: number;
  passed: number;
  failed: number;
  skipped: number;
  pass_rate: number;
  execution_time_ms: number;
  results: TestExecutionResult[];
  recommendations: string[];
}

// ============================================================================
// Test Runner Functions
// ============================================================================

/**
 * Run all test cases in the suite
 *
 * @param extractionFunction - Function that extracts data from documents
 * @param testCases - Test cases to run (defaults to ALL_TEST_CASES)
 */
export async function runTestSuite(
  extractionFunction: (location: string) => Promise<BankStatementData>,
  testCases: TextractTestCase[] = ALL_TEST_CASES
): Promise<TestSuiteSummary> {
  const startTime = Date.now();
  const results: TestExecutionResult[] = [];
  let passed = 0;
  let failed = 0;
  let skipped = 0;

  for (const testCase of testCases) {
    const testStart = Date.now();

    try {
      // Extract data from document
      const extractedData = await extractionFunction(testCase.input.location);

      // Run test case
      const testResult = runTestCase(testCase, extractedData);

      const result: TestExecutionResult = {
        test_case: testCase,
        passed: testResult.passed,
        validation_result: testResult.validation_result,
        expected_result: testResult.expected_result,
        execution_time_ms: Date.now() - testStart,
      };

      results.push(result);

      if (testResult.passed) {
        passed++;
      } else {
        failed++;
      }
    } catch (error) {
      results.push({
        test_case: testCase,
        passed: false,
        validation_result: {
          is_valid: false,
          meets_confidence_threshold: false,
          has_required_fields: false,
          consistency_checks_passed: false,
          field_validations: [],
          warnings: [],
          errors: [
            {
              code: 'EXTRACTION_ERROR',
              message: error instanceof Error ? error.message : 'Unknown error',
              recoverable: false,
            },
          ],
          requires_human_review: true,
          human_review_reasons: ['Extraction failed'],
        },
        expected_result: {
          is_valid: false,
          meets_confidence_threshold: false,
          has_required_fields: false,
          consistency_checks_passed: false,
          field_validations: [],
          warnings: [],
          errors: [],
          requires_human_review: true,
          human_review_reasons: [],
        },
        execution_time_ms: Date.now() - testStart,
        error: error instanceof Error ? error.message : 'Unknown error',
      });
      failed++;
    }
  }

  const totalTime = Date.now() - startTime;
  const passRate = testCases.length > 0 ? passed / testCases.length : 0;

  // Generate recommendations
  const recommendations = generateRecommendations(results, passRate);

  return {
    suite_name: TEST_SUITE_INFO.name,
    total_tests: testCases.length,
    passed,
    failed,
    skipped,
    pass_rate: passRate,
    execution_time_ms: totalTime,
    results,
    recommendations,
  };
}

/**
 * Generate recommendations based on test results
 */
function generateRecommendations(results: TestExecutionResult[], passRate: number): string[] {
  const recommendations: string[] = [];

  if (passRate < TEST_SUITE_INFO.passing_threshold) {
    recommendations.push(
      `Pass rate ${(passRate * 100).toFixed(1)}% is below threshold ${(TEST_SUITE_INFO.passing_threshold * 100).toFixed(1)}%`
    );
  }

  // Check for common failure patterns
  const lowConfidenceFailures = results.filter(
    (r) => !r.passed && !r.validation_result.meets_confidence_threshold
  );
  if (lowConfidenceFailures.length > 0) {
    recommendations.push(
      `${lowConfidenceFailures.length} tests failed due to low confidence. Consider adjusting Textract settings or document quality.`
    );
  }

  const missingFieldFailures = results.filter(
    (r) => !r.passed && !r.validation_result.has_required_fields
  );
  if (missingFieldFailures.length > 0) {
    recommendations.push(
      `${missingFieldFailures.length} tests failed due to missing required fields. Review Textract query configuration.`
    );
  }

  const scannedDocFailures = results.filter(
    (r) => !r.passed && r.test_case.input.characteristics.is_scanned
  );
  if (scannedDocFailures.length > 0) {
    recommendations.push(
      `${scannedDocFailures.length} scanned document tests failed. Consider implementing A2I human review for scanned documents.`
    );
  }

  const slowTests = results.filter(
    (r) => r.execution_time_ms > r.test_case.acceptance_criteria.max_extraction_time_ms
  );
  if (slowTests.length > 0) {
    recommendations.push(
      `${slowTests.length} tests exceeded time limits. Consider async processing for large documents.`
    );
  }

  if (recommendations.length === 0) {
    recommendations.push('All tests passed within acceptable parameters. No immediate action required.');
  }

  return recommendations;
}

/**
 * Run a single test case (for debugging)
 */
export async function runSingleTest(
  testCase: TextractTestCase,
  extractionFunction: (location: string) => Promise<BankStatementData>
): Promise<TestExecutionResult> {
  const summary = await runTestSuite(extractionFunction, [testCase]);
  return summary.results[0];
}

/**
 * Get test cases by category
 */
export function getTestCasesByCategory(category: 'standard' | 'edge_case' | 'scanned'): TextractTestCase[] {
  switch (category) {
    case 'standard':
      return ALL_TEST_CASES.filter(
        (tc) => !tc.input.characteristics.is_scanned && !tc.id.startsWith('TC01')
      );
    case 'scanned':
      return ALL_TEST_CASES.filter((tc) => tc.input.characteristics.is_scanned);
    case 'edge_case':
      return ALL_TEST_CASES.filter((tc) => tc.id.startsWith('TC01'));
    default:
      return ALL_TEST_CASES;
  }
}

// ============================================================================
// Mock Extraction Function (for testing without AWS)
// ============================================================================

/**
 * Mock extraction function for local testing
 * Returns synthetic data matching test case expectations
 */
export function createMockExtractionFunction(): (location: string) => Promise<BankStatementData> {
  return async (location: string): Promise<BankStatementData> => {
    // Simulate extraction delay
    await new Promise((resolve) => setTimeout(resolve, 100));

    // Generate mock data based on location
    const mockData: BankStatementData = {
      extraction_id: `ext_${Date.now()}`,
      extracted_at: Date.now(),
      source_document: location,
      overall_confidence: 92,
      account: {
        account_holder_name: 'John Doe',
        confidence_account_holder: 95,
        account_number_masked: '****1234',
        confidence_account_number: 98,
        routing_number: '021000021',
        confidence_routing: 90,
        bank_name: location.includes('chase') ? 'Chase' : 'Generic Bank',
        confidence_bank_name: 88,
        account_type: 'checking',
        confidence_account_type: 85,
      },
      statement_period: {
        start_date: '2024-10-01',
        confidence_start: 95,
        end_date: '2024-10-31',
        confidence_end: 95,
        statement_date: '2024-11-01',
        confidence_statement_date: 90,
      },
      transactions: Array.from({ length: 20 }, (_, i) => ({
        date: `2024-10-${String(i + 1).padStart(2, '0')}`,
        confidence_date: 90,
        description: `Transaction ${i + 1}`,
        confidence_description: 88,
        amount: Math.round(Math.random() * 10000) / 100,
        confidence_amount: 92,
        type: i % 2 === 0 ? 'debit' : 'credit',
        confidence_type: 95,
        balance: 1000 + i * 10,
        confidence_balance: 85,
        reference: `REF${i}`,
        confidence_reference: 80,
        category: 'general',
        confidence_category: 70,
        merchant: `Merchant ${i}`,
        confidence_merchant: 75,
        source_row: i + 1,
        source_page: 1,
      })),
      summary: {
        opening_balance: 1000.0,
        confidence_opening: 95,
        closing_balance: 1200.0,
        confidence_closing: 95,
        total_credits: 500.0,
        confidence_credits: 90,
        total_debits: 300.0,
        confidence_debits: 90,
        transaction_count: 20,
      },
    };

    return mockData;
  };
}
