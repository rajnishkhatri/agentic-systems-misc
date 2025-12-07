/**
 * AWS Textract Types for Bank Statement Processing
 *
 * Defines interfaces for extracting dispute-relevant data from bank statements
 * using Amazon Textract's Analyze Document and Analyze Expense APIs.
 */

// ============================================================================
// Textract Configuration
// ============================================================================

/**
 * Supported document types for Textract processing
 */
export type DocumentType =
  | 'bank_statement'
  | 'credit_card_statement'
  | 'receipt'
  | 'invoice'
  | 'shipping_document'
  | 'customer_communication';

/**
 * Textract feature types to enable
 */
export type TextractFeature = 'TABLES' | 'FORMS' | 'QUERIES' | 'SIGNATURES' | 'LAYOUT';

/**
 * Configuration for Textract processing
 */
export interface TextractConfig {
  /** Document type for specialized processing */
  document_type: DocumentType;

  /** Textract features to enable */
  features: TextractFeature[];

  /** Custom queries for targeted extraction */
  queries?: TextractQuery[];

  /** Minimum confidence threshold (0-100) */
  min_confidence: number;

  /** Enable human review for low-confidence results */
  enable_human_review: boolean;

  /** A2I workflow ARN for human review */
  a2i_workflow_arn?: string;
}

/**
 * Custom query for targeted data extraction
 */
export interface TextractQuery {
  /** Query text */
  text: string;

  /** Query alias for response mapping */
  alias: string;

  /** Pages to query (empty for all) */
  pages?: number[];
}

// ============================================================================
// Bank Statement Extraction
// ============================================================================

/**
 * Extracted bank statement data
 */
export interface BankStatementData {
  /** Extraction metadata */
  extraction_id: string;
  extracted_at: number;
  source_document: string;
  overall_confidence: number;

  /** Account information */
  account: BankAccountInfo;

  /** Statement period */
  statement_period: StatementPeriod;

  /** Transactions */
  transactions: ExtractedTransaction[];

  /** Summary totals */
  summary: StatementSummary;

  /** Raw extraction blocks for audit */
  raw_blocks?: TextractBlock[];
}

/**
 * Bank account information extracted from statement
 */
export interface BankAccountInfo {
  /** Account holder name */
  account_holder_name?: string;
  confidence_account_holder: number;

  /** Account number (masked) */
  account_number_masked?: string;
  confidence_account_number: number;

  /** Routing number */
  routing_number?: string;
  confidence_routing: number;

  /** Bank name */
  bank_name?: string;
  confidence_bank_name: number;

  /** Account type */
  account_type?: 'checking' | 'savings' | 'credit' | 'unknown';
  confidence_account_type: number;
}

/**
 * Statement period information
 */
export interface StatementPeriod {
  /** Start date (ISO 8601) */
  start_date?: string;
  confidence_start: number;

  /** End date (ISO 8601) */
  end_date?: string;
  confidence_end: number;

  /** Statement date */
  statement_date?: string;
  confidence_statement_date: number;
}

/**
 * Individual transaction extracted from statement
 */
export interface ExtractedTransaction {
  /** Transaction date */
  date?: string;
  confidence_date: number;

  /** Transaction description */
  description?: string;
  confidence_description: number;

  /** Transaction amount */
  amount?: number;
  confidence_amount: number;

  /** Transaction type */
  type: 'debit' | 'credit' | 'unknown';
  confidence_type: number;

  /** Running balance after transaction */
  balance?: number;
  confidence_balance: number;

  /** Reference/check number */
  reference?: string;
  confidence_reference: number;

  /** Category (if extractable) */
  category?: string;
  confidence_category: number;

  /** Merchant name (if identifiable) */
  merchant?: string;
  confidence_merchant: number;

  /** Row number in source table */
  source_row?: number;

  /** Page number in document */
  source_page?: number;
}

/**
 * Statement summary totals
 */
export interface StatementSummary {
  /** Opening balance */
  opening_balance?: number;
  confidence_opening: number;

  /** Closing balance */
  closing_balance?: number;
  confidence_closing: number;

  /** Total credits */
  total_credits?: number;
  confidence_credits: number;

  /** Total debits */
  total_debits?: number;
  confidence_debits: number;

  /** Number of transactions */
  transaction_count?: number;
}

// ============================================================================
// Textract Response Types
// ============================================================================

/**
 * Textract block from API response
 */
export interface TextractBlock {
  /** Block type */
  block_type:
    | 'PAGE'
    | 'LINE'
    | 'WORD'
    | 'TABLE'
    | 'CELL'
    | 'KEY_VALUE_SET'
    | 'SELECTION_ELEMENT'
    | 'QUERY'
    | 'QUERY_RESULT';

  /** Block ID */
  id: string;

  /** Confidence score (0-100) */
  confidence: number;

  /** Text content */
  text?: string;

  /** Page number */
  page: number;

  /** Bounding box geometry */
  geometry?: {
    bounding_box: {
      width: number;
      height: number;
      left: number;
      top: number;
    };
  };

  /** Relationship to other blocks */
  relationships?: Array<{
    type: 'CHILD' | 'VALUE' | 'ANSWER';
    ids: string[];
  }>;

  /** Entity type for KEY_VALUE_SET */
  entity_type?: 'KEY' | 'VALUE';

  /** Row/column index for cells */
  row_index?: number;
  column_index?: number;
}

// ============================================================================
// Validation Types
// ============================================================================

/**
 * Validation result for extracted data
 */
export interface ValidationResult {
  /** Overall validation status */
  is_valid: boolean;

  /** Confidence meets threshold */
  meets_confidence_threshold: boolean;

  /** All required fields present */
  has_required_fields: boolean;

  /** Data consistency checks passed */
  consistency_checks_passed: boolean;

  /** Individual field validations */
  field_validations: FieldValidation[];

  /** Validation warnings */
  warnings: ValidationWarning[];

  /** Validation errors */
  errors: ValidationError[];

  /** Recommendation for human review */
  requires_human_review: boolean;
  human_review_reasons: string[];
}

/**
 * Individual field validation result
 */
export interface FieldValidation {
  /** Field name */
  field: string;

  /** Is field valid */
  is_valid: boolean;

  /** Confidence score */
  confidence: number;

  /** Validation message */
  message?: string;
}

/**
 * Validation warning
 */
export interface ValidationWarning {
  /** Warning code */
  code: string;

  /** Warning message */
  message: string;

  /** Affected field */
  field?: string;

  /** Suggested action */
  suggestion?: string;
}

/**
 * Validation error
 */
export interface ValidationError {
  /** Error code */
  code: string;

  /** Error message */
  message: string;

  /** Affected field */
  field?: string;

  /** Is error recoverable */
  recoverable: boolean;
}

// ============================================================================
// Test Configuration Types
// ============================================================================

/**
 * Test case for Textract validation
 */
export interface TextractTestCase {
  /** Test case ID */
  id: string;

  /** Test case name */
  name: string;

  /** Description */
  description: string;

  /** Input document configuration */
  input: TestDocumentConfig;

  /** Expected extraction results */
  expected: ExpectedExtractionResult;

  /** Acceptance criteria */
  acceptance_criteria: AcceptanceCriteria;
}

/**
 * Test document configuration
 */
export interface TestDocumentConfig {
  /** Document type */
  document_type: DocumentType;

  /** Bank name for bank statements */
  bank_name?: string;

  /** File format */
  format: 'pdf' | 'png' | 'jpg' | 'tiff';

  /** S3 location or local path */
  location: string;

  /** Document characteristics */
  characteristics: {
    /** Number of pages */
    page_count: number;

    /** Has tables */
    has_tables: boolean;

    /** Has handwriting */
    has_handwriting: boolean;

    /** Document quality */
    quality: 'high' | 'medium' | 'low';

    /** Is scanned */
    is_scanned: boolean;
  };
}

/**
 * Expected extraction results for test validation
 */
export interface ExpectedExtractionResult {
  /** Expected account holder (partial match OK) */
  account_holder_contains?: string;

  /** Expected bank name */
  bank_name?: string;

  /** Expected transaction count range */
  transaction_count_min?: number;
  transaction_count_max?: number;

  /** Expected date range */
  date_range?: {
    start_contains?: string;
    end_contains?: string;
  };

  /** Sample transactions to validate */
  sample_transactions?: Array<{
    date_contains?: string;
    description_contains?: string;
    amount?: number;
    amount_tolerance?: number;
  }>;

  /** Expected totals */
  totals?: {
    opening_balance?: number;
    closing_balance?: number;
    balance_tolerance?: number;
  };
}

/**
 * Acceptance criteria for test case
 */
export interface AcceptanceCriteria {
  /** Minimum overall confidence */
  min_overall_confidence: number;

  /** Minimum field-level confidence */
  min_field_confidence: number;

  /** Maximum extraction time (ms) */
  max_extraction_time_ms: number;

  /** Required fields that must be extracted */
  required_fields: string[];

  /** Acceptable error rate for transactions */
  max_transaction_error_rate: number;
}

// ============================================================================
// Sample Bank Statement Configurations
// ============================================================================

/**
 * Pre-configured test cases for common bank statement formats
 */
export const BANK_STATEMENT_TEST_CONFIGS: Record<string, Partial<TextractTestCase>> = {
  chase_checking: {
    name: 'Chase Checking Statement',
    description: 'Standard Chase Bank checking account statement',
    input: {
      document_type: 'bank_statement',
      bank_name: 'Chase',
      format: 'pdf',
      location: 's3://dispute-evidence-test/bank-statements/chase/',
      characteristics: {
        page_count: 3,
        has_tables: true,
        has_handwriting: false,
        quality: 'high',
        is_scanned: false,
      },
    },
    acceptance_criteria: {
      min_overall_confidence: 90,
      min_field_confidence: 85,
      max_extraction_time_ms: 5000,
      required_fields: ['account_holder_name', 'account_number_masked', 'transactions', 'closing_balance'],
      max_transaction_error_rate: 0.05,
    },
  },

  bofa_checking: {
    name: 'Bank of America Checking Statement',
    description: 'Standard Bank of America checking account statement',
    input: {
      document_type: 'bank_statement',
      bank_name: 'Bank of America',
      format: 'pdf',
      location: 's3://dispute-evidence-test/bank-statements/bofa/',
      characteristics: {
        page_count: 4,
        has_tables: true,
        has_handwriting: false,
        quality: 'high',
        is_scanned: false,
      },
    },
    acceptance_criteria: {
      min_overall_confidence: 90,
      min_field_confidence: 85,
      max_extraction_time_ms: 6000,
      required_fields: ['account_holder_name', 'account_number_masked', 'transactions', 'closing_balance'],
      max_transaction_error_rate: 0.05,
    },
  },

  wells_fargo_checking: {
    name: 'Wells Fargo Checking Statement',
    description: 'Standard Wells Fargo checking account statement',
    input: {
      document_type: 'bank_statement',
      bank_name: 'Wells Fargo',
      format: 'pdf',
      location: 's3://dispute-evidence-test/bank-statements/wellsfargo/',
      characteristics: {
        page_count: 2,
        has_tables: true,
        has_handwriting: false,
        quality: 'high',
        is_scanned: false,
      },
    },
    acceptance_criteria: {
      min_overall_confidence: 90,
      min_field_confidence: 85,
      max_extraction_time_ms: 4000,
      required_fields: ['account_holder_name', 'account_number_masked', 'transactions', 'closing_balance'],
      max_transaction_error_rate: 0.05,
    },
  },

  citi_credit: {
    name: 'Citi Credit Card Statement',
    description: 'Citi credit card statement with rewards summary',
    input: {
      document_type: 'credit_card_statement',
      bank_name: 'Citi',
      format: 'pdf',
      location: 's3://dispute-evidence-test/bank-statements/citi/',
      characteristics: {
        page_count: 5,
        has_tables: true,
        has_handwriting: false,
        quality: 'high',
        is_scanned: false,
      },
    },
    acceptance_criteria: {
      min_overall_confidence: 88,
      min_field_confidence: 82,
      max_extraction_time_ms: 7000,
      required_fields: ['account_holder_name', 'account_number_masked', 'transactions', 'closing_balance', 'minimum_payment'],
      max_transaction_error_rate: 0.05,
    },
  },

  scanned_statement: {
    name: 'Scanned Bank Statement (Low Quality)',
    description: 'Scanned paper statement with lower image quality',
    input: {
      document_type: 'bank_statement',
      bank_name: 'Generic',
      format: 'png',
      location: 's3://dispute-evidence-test/bank-statements/scanned/',
      characteristics: {
        page_count: 2,
        has_tables: true,
        has_handwriting: true,
        quality: 'low',
        is_scanned: true,
      },
    },
    acceptance_criteria: {
      min_overall_confidence: 70,
      min_field_confidence: 60,
      max_extraction_time_ms: 10000,
      required_fields: ['transactions'],
      max_transaction_error_rate: 0.15,
    },
  },

  international_statement: {
    name: 'International Bank Statement',
    description: 'Non-US bank statement with different format',
    input: {
      document_type: 'bank_statement',
      bank_name: 'HSBC UK',
      format: 'pdf',
      location: 's3://dispute-evidence-test/bank-statements/international/',
      characteristics: {
        page_count: 3,
        has_tables: true,
        has_handwriting: false,
        quality: 'high',
        is_scanned: false,
      },
    },
    acceptance_criteria: {
      min_overall_confidence: 85,
      min_field_confidence: 80,
      max_extraction_time_ms: 6000,
      required_fields: ['account_holder_name', 'transactions'],
      max_transaction_error_rate: 0.08,
    },
  },
};

/**
 * Default Textract queries for bank statement extraction
 */
export const BANK_STATEMENT_QUERIES: TextractQuery[] = [
  { text: 'What is the account holder name?', alias: 'account_holder_name' },
  { text: 'What is the account number?', alias: 'account_number' },
  { text: 'What is the statement period start date?', alias: 'period_start' },
  { text: 'What is the statement period end date?', alias: 'period_end' },
  { text: 'What is the opening balance?', alias: 'opening_balance' },
  { text: 'What is the closing balance?', alias: 'closing_balance' },
  { text: 'What is the total deposits?', alias: 'total_deposits' },
  { text: 'What is the total withdrawals?', alias: 'total_withdrawals' },
];
