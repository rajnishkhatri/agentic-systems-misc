/**
 * PCI DSS Compliance Guardrails for MCP Chat Interface
 *
 * Prevents cardholder data (CHD) from being exposed in chat:
 * - Primary Account Number (PAN)
 * - CVV/CVC/CVV2
 * - PIN
 * - Full Track Data
 *
 * Per PCI DSS v4.0, these must never be stored or transmitted in plaintext
 * outside of the cardholder data environment (CDE).
 */

// ============================================================================
// PAN Detection Patterns
// ============================================================================

const PAN_PATTERNS = [
  // Visa: 13-19 digits starting with 4
  /\b4[0-9]{12}(?:[0-9]{3,6})?\b/g,

  // Mastercard: 16 digits starting with 51-55 or 2221-2720
  /\b(?:5[1-5][0-9]{2}|222[1-9]|22[3-9][0-9]|2[3-6][0-9]{2}|27[01][0-9]|2720)[0-9]{12}\b/g,

  // American Express: 15 digits starting with 34 or 37
  /\b3[47][0-9]{13}\b/g,

  // Discover: 16 digits starting with 6011, 622126-622925, 644-649, 65
  /\b(?:6011|65[0-9]{2}|64[4-9][0-9])[0-9]{12}\b/g,

  // JCB: 16 digits starting with 3528-3589
  /\b35(?:2[89]|[3-8][0-9])[0-9]{12}\b/g,

  // Diners Club: 14-16 digits starting with 36, 38, 300-305
  /\b3(?:0[0-5]|[68][0-9])[0-9]{11,14}\b/g,

  // Generic 16-digit patterns (catch-all for unknown card types)
  /\b[0-9]{4}[\s-]?[0-9]{4}[\s-]?[0-9]{4}[\s-]?[0-9]{4}\b/g,
];

// CVV patterns (3-4 digits, context-sensitive)
const CVV_PATTERNS = [
  /\b(?:cvv|cvc|cvv2|cvc2|cid|csc)[:\s]*([0-9]{3,4})\b/gi,
  /\b(?:security code|card code)[:\s]*([0-9]{3,4})\b/gi,
];

// PIN patterns
const PIN_PATTERNS = [
  /\b(?:pin|pin code|pin number)[:\s]*([0-9]{4,6})\b/gi,
];

// Expiration date patterns
const EXPIRY_PATTERNS = [
  /\b(?:exp(?:iry|iration)?|valid thru)[:\s]*(0[1-9]|1[0-2])[\s\/\-]?([0-9]{2}(?:[0-9]{2})?)\b/gi,
];

// ============================================================================
// Detection Functions
// ============================================================================

export interface SensitiveDataMatch {
  type: 'PAN' | 'CVV' | 'PIN' | 'EXPIRY';
  start: number;
  end: number;
  masked: string;
}

/**
 * Validates a potential PAN using Luhn algorithm
 */
function isValidLuhn(cardNumber: string): boolean {
  const digits = cardNumber.replace(/\D/g, '');
  if (digits.length < 13 || digits.length > 19) return false;

  let sum = 0;
  let isEven = false;

  for (let i = digits.length - 1; i >= 0; i--) {
    let digit = parseInt(digits[i], 10);

    if (isEven) {
      digit *= 2;
      if (digit > 9) digit -= 9;
    }

    sum += digit;
    isEven = !isEven;
  }

  return sum % 10 === 0;
}

/**
 * Detects potential PANs in text
 */
export function detectPAN(text: string): SensitiveDataMatch[] {
  const matches: SensitiveDataMatch[] = [];

  for (const pattern of PAN_PATTERNS) {
    pattern.lastIndex = 0;
    let match;
    while ((match = pattern.exec(text)) !== null) {
      const cardNumber = match[0].replace(/[\s-]/g, '');

      // Validate with Luhn algorithm to reduce false positives
      if (isValidLuhn(cardNumber)) {
        matches.push({
          type: 'PAN',
          start: match.index,
          end: match.index + match[0].length,
          masked: maskPAN(cardNumber),
        });
      }
    }
  }

  return matches;
}

/**
 * Detects CVV/CVC codes in text
 */
export function detectCVV(text: string): SensitiveDataMatch[] {
  const matches: SensitiveDataMatch[] = [];

  for (const pattern of CVV_PATTERNS) {
    pattern.lastIndex = 0;
    let match;
    while ((match = pattern.exec(text)) !== null) {
      matches.push({
        type: 'CVV',
        start: match.index,
        end: match.index + match[0].length,
        masked: match[0].replace(/[0-9]/g, '*'),
      });
    }
  }

  return matches;
}

/**
 * Detects PIN codes in text
 */
export function detectPIN(text: string): SensitiveDataMatch[] {
  const matches: SensitiveDataMatch[] = [];

  for (const pattern of PIN_PATTERNS) {
    pattern.lastIndex = 0;
    let match;
    while ((match = pattern.exec(text)) !== null) {
      matches.push({
        type: 'PIN',
        start: match.index,
        end: match.index + match[0].length,
        masked: match[0].replace(/[0-9]/g, '*'),
      });
    }
  }

  return matches;
}

/**
 * Detects all sensitive cardholder data in text
 */
export function detectSensitiveData(text: string): SensitiveDataMatch[] {
  return [
    ...detectPAN(text),
    ...detectCVV(text),
    ...detectPIN(text),
  ].sort((a, b) => a.start - b.start);
}

// ============================================================================
// Masking Functions
// ============================================================================

/**
 * Masks a PAN showing only last 4 digits (PCI compliant)
 */
export function maskPAN(pan: string): string {
  const digits = pan.replace(/\D/g, '');
  if (digits.length < 4) return '****';
  return '*'.repeat(digits.length - 4) + digits.slice(-4);
}

/**
 * Redacts all sensitive data from text
 */
export function redactSensitiveData(text: string): string {
  const matches = detectSensitiveData(text);

  if (matches.length === 0) return text;

  // Build redacted string from end to start to preserve indices
  let redacted = text;
  for (let i = matches.length - 1; i >= 0; i--) {
    const match = matches[i];
    redacted = redacted.slice(0, match.start) + match.masked + redacted.slice(match.end);
  }

  return redacted;
}

// ============================================================================
// Validation Guards
// ============================================================================

export interface ValidationResult {
  isValid: boolean;
  violations: Array<{
    type: 'PAN' | 'CVV' | 'PIN' | 'EXPIRY';
    message: string;
  }>;
  sanitizedInput?: string;
}

/**
 * Validates input does not contain sensitive cardholder data
 * Returns sanitized input if violations found
 */
export function validateInput(input: string): ValidationResult {
  const matches = detectSensitiveData(input);

  if (matches.length === 0) {
    return { isValid: true, violations: [] };
  }

  const violations = matches.map((match) => ({
    type: match.type,
    message: getViolationMessage(match.type),
  }));

  return {
    isValid: false,
    violations,
    sanitizedInput: redactSensitiveData(input),
  };
}

function getViolationMessage(type: SensitiveDataMatch['type']): string {
  switch (type) {
    case 'PAN':
      return 'Card number detected. For your security, please never share your full card number. Use the last 4 digits only.';
    case 'CVV':
      return 'Security code (CVV/CVC) detected. Please never share this code in chat.';
    case 'PIN':
      return 'PIN detected. Please never share your PIN with anyone.';
    case 'EXPIRY':
      return 'Card expiration date detected. Please be cautious sharing card details.';
    default:
      return 'Sensitive card data detected and redacted for your security.';
  }
}

/**
 * Middleware guard for MCP tool inputs
 * Throws error if sensitive data detected, providing guidance to user
 */
export function guardInput(input: unknown): void {
  if (typeof input !== 'object' || input === null) return;

  const checkValue = (value: unknown, path: string): void => {
    if (typeof value === 'string') {
      const result = validateInput(value);
      if (!result.isValid) {
        const violationTypes = [...new Set(result.violations.map((v) => v.type))];
        throw new Error(
          `Security Alert: Detected ${violationTypes.join(', ')} in ${path}. ` +
            'For your protection, please do not share full card numbers, CVV codes, or PINs. ' +
            'If you need to reference a card, please use only the last 4 digits.'
        );
      }
    } else if (Array.isArray(value)) {
      value.forEach((item, index) => checkValue(item, `${path}[${index}]`));
    } else if (typeof value === 'object' && value !== null) {
      Object.entries(value).forEach(([key, val]) => checkValue(val, `${path}.${key}`));
    }
  };

  checkValue(input, 'input');
}

/**
 * Sanitizes output before sending to chat
 */
export function sanitizeOutput<T>(output: T): T {
  if (typeof output === 'string') {
    return redactSensitiveData(output) as T;
  }

  if (Array.isArray(output)) {
    return output.map((item) => sanitizeOutput(item)) as T;
  }

  if (typeof output === 'object' && output !== null) {
    const sanitized: Record<string, unknown> = {};
    for (const [key, value] of Object.entries(output)) {
      sanitized[key] = sanitizeOutput(value);
    }
    return sanitized as T;
  }

  return output;
}
