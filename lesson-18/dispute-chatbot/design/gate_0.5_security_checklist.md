# Gate 0.5 Validation Checklist: Security Review

**Gate ID:** 0.5
**Document Under Review:** `design/06_security_architecture.md`
**Reviewer Role:** Security Engineer
**Date:** _______________
**Reviewer Name:** _______________

---

## 1. Compliance Requirements

### 1.1 PCI-DSS v4.0 Alignment
| Requirement | Status | Verification Method | Notes |
|-------------|--------|---------------------|-------|
| **No PAN Storage** | [ ] | Architecture Review | Verify DB schema has no PAN columns |
| **Tokenization** | [ ] | Code/Design Review | Verify use of last-4 + token only |
| **Encryption at Rest** | [ ] | Infra Review | Confirm KMS integration for DB/S3 |
| **Encryption in Transit** | [ ] | Config Review | TLS 1.3 enforcement checked |

### 1.2 PII Handling (GDPR/CCPA)
| Requirement | Status | Verification Method | Notes |
|-------------|--------|---------------------|-------|
| **Data Minimization** | [ ] | Schema Review | Only collecting necessary fields? |
| **Right to Erasure** | [ ] | Process Review | Is there a mechanism to delete merchant PII? |
| **GuardRails Redaction** | [ ] | Design Review | Is PII scrubbing strictly enforced before logging? |

## 2. Threat Modeling

### 2.1 Attack Surface Analysis
| Risk Scenario | Mitigation | Status | Notes |
|---------------|------------|--------|-------|
| **Prompt Injection** | GuardRails input filters | [ ] | |
| **DoS / API Spam** | Redis Rate Limiting | [ ] | |
| **Broken Auth** | Session mgmt + Secure Cookies | [ ] | |
| **Insecure Dependencies** | Automated scanning (Snyk/Dependabot) | [ ] | |

## 3. Infrastructure Security

| Component | Check | Status | Notes |
|-----------|-------|--------|-------|
| **Network** | VPC Isolation (DBs in private subnets) | [ ] | |
| **IAM** | Least Privilege Roles defined | [ ] | |
| **Secrets** | No hardcoded secrets (Env vars / Secrets Manager) | [ ] | |
| **Logging** | Security events logged to separate stream | [ ] | |

## 4. Sign-Off Decision

- [ ] **APPROVED** - Security architecture meets requirements.
- [ ] **APPROVED WITH CONDITIONS** - Minor remediation needed before Prod.
- [ ] **NOT APPROVED** - Critical vulnerabilities identified.

**Security Engineer Signature:** _______________________
**Date:** _______________________

