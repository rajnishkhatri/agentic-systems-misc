/**
 * Textract Module - Bank Statement Processing for Dispute Evidence
 *
 * This module provides:
 * - Type definitions for Textract extraction
 * - Validation functions for extracted data
 * - Test suite for validating extraction accuracy
 *
 * @module textract
 */

// Types
export * from './textract-types';

// Validation functions
export {
  validateBankStatementExtraction,
  validateAgainstExpected,
  runTestCase,
  calculateAverageTransactionConfidence,
  MIN_EVIDENCE_CONFIDENCE,
  REQUIRED_DISPUTE_FIELDS,
  MAX_STATEMENT_AGE_DAYS,
  BALANCE_TOLERANCE,
} from './textract-validator';

// Test suite
export {
  TEST_SUITE_INFO,
  ALL_TEST_CASES,
  runTestSuite,
  runSingleTest,
  getTestCasesByCategory,
  createMockExtractionFunction,
  // Individual test cases for selective testing
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
} from './textract-test-suite';
