# 06_Security_Architecture

**Version:** 1.0
**Status:** Approved
**Date:** 2025-12-09

---

## 1. Overview

The Security Architecture describes the controls, policies, and mechanisms implemented to protect merchant data, ensure system integrity, and achieve compliance with PCI-DSS v4.0 standards. The chatbot operates as a "Service Provider" in PCI terms, processing but not storing full cardholder data (PAN).

## 2. Compliance & Standards

### 2.1 PCI-DSS v4.0 Mapping

| Requirement | Control Implementation |
|-------------|------------------------|
| **Req 3: Protect Stored Account Data** | **PAN Storage Prohibition**: We do NOT store full Primary Account Numbers (PAN). Only truncated (Last-4) and tokenized references are retained. <br> **Encryption**: AES-256 for all stored PII. |
| **Req 4: Protect Cardholder Data in Transit** | **TLS 1.3**: Mandated for all external and internal HTTP traffic. <br> **Cipher Suites**: Strong ciphers only (e.g., ECDHE-RSA-AES256-GCM-SHA384). |
| **Req 6: Develop Secure Systems** | **Vulnerability Management**: Automated dependencies scanning (Dependabot/Snyk). <br> **Code Review**: Mandatory peer review for all merges. <br> **Input Validation**: GuardRails for all LLM and user inputs. |
| **Req 7: Restrict Access to Cardholder Data** | **RBAC**: Strict Role-Based Access Control. Need-to-know basis. |
| **Req 10: Log and Monitor** | **Audit Trails**: Centralized logging in TimescaleDB (see `07_observability_strategy.md`). <br> **PII Scrubbing**: Automated redaction before logging. |

## 3. Data Protection

### 3.1 Encryption Strategy
- **At Rest**: 
  - Database volumes (PostgreSQL, TimescaleDB, Redis) encrypted via AWS KMS / disk encryption.
  - S3 Buckets encrypted with SSE-S3 or SSE-KMS.
- **In Transit**: 
  - All APIs enforced HTTPS (TLS 1.2+).
  - Internal service-to-service communication encrypted (mTLS where applicable).

### 3.2 Key Management
- Cryptographic keys are managed via a dedicated Key Management Service (e.g., AWS KMS or HashiCorp Vault).
- Key rotation policy: Automatic rotation every 365 days.
- Access to keys is restricted to the application runtime role.

## 4. Authentication & Authorization

### 4.1 Application Authentication
- **Merchants**: Authenticated via Platform Integration (e.g., Stripe/Square OAuth) or secure session tokens.
- **Session Management**: 
  - Redis-backed sessions with 30-minute idle timeout (Reg E/Z compliance recommendation).
  - Secure Cookies: `HttpOnly`, `Secure`, `SameSite=Strict`.

### 4.2 System Authentication
- **Service Accounts**: Used for backend component communication (e.g., API to Database).
- **IAM Roles**: Least-privilege IAM roles for accessing S3, Bedrock/OpenAI APIs.

## 5. Application Security Controls

### 5.1 GuardRails Integration
Integrated into the LLM pipeline (`utils/llm_service.py` hooks) to prevent:
- **PII Leakage**: Detects and redacts PAN, SSN, etc. in outputs.
- **Prompt Injection**: Detects adversarial inputs attempting to jailbreak the bot.
- **Hallucination Checks**: Cross-references outputs with retrieved context.

### 5.2 Network Security
- **WAF (Web Application Firewall)**: Protects against OWASP Top 10 (SQLi, XSS).
- **Rate Limiting**: Implemented in Redis to prevent DoS attacks (e.g., 100 requests/minute per merchant).
- **VPC Isolation**: Database and internal services sit in private subnets, not directly accessible from the internet.

## 6. Secure Development Lifecycle (SDLC)

- **Static Analysis (SAST)**: `ruff` and `mypy` run on every commit.
- **Secret Scanning**: Pre-commit hooks prevent committing `.env` files or API keys.
- **Dependency Scanning**: Weekly reports on CVEs in `requirements.txt`.

## 7. Incident Response
- **Security Event Monitoring**: Alerts triggered on GuardRails violations or WAF blocks.
- **Breach Protocol**:
    1. **Identify**: Confirm scope of potential leak.
    2. **Contain**: Revoke sessions, rotate keys, isolate instances.
    3. **Eradicate**: Patch vulnerability.
    4. **Recover**: Restore data from clean backups.
    5. **Notify**: Stakeholders and regulatory bodies (if PII impacted) within 72 hours.

