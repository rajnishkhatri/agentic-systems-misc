# PCI DSS v4.0 Compliance Mapping for AWS Dispute Management System

## Overview

This document maps Payment Card Industry Data Security Standard (PCI DSS) v4.0 requirements to AWS services and controls used in the dispute management system. The system handles cardholder data (CHD) including PANs, and must maintain PCI DSS compliance.

---

## Scope Definition

### In-Scope Data Elements

| Data Element | PCI DSS Classification | Storage Location | Protection Required |
|-------------|------------------------|------------------|---------------------|
| Primary Account Number (PAN) | Cardholder Data (CHD) | Never stored in full | Tokenization required |
| Last 4 digits | Not CHD (truncated) | DynamoDB | Standard encryption |
| Card expiration | CHD (with PAN) | Not stored | N/A |
| Cardholder name | CHD (with PAN) | Not stored | N/A |
| Service code | CHD | Not stored | N/A |
| CVV/CVC | Sensitive Auth Data | Never stored | Prohibited |
| PIN/PIN block | Sensitive Auth Data | Never stored | Prohibited |

### Cardholder Data Environment (CDE)

```
┌─────────────────────────────────────────────────────────────────────┐
│                    AWS Cardholder Data Environment                   │
├─────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐  │
│  │   API Gateway   │───▶│  Lambda (CDE)   │───▶│    DynamoDB     │  │
│  │  (TLS 1.2+)     │    │  Tokenization   │    │  (Encrypted)    │  │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘  │
│           │                     │                      │            │
│           ▼                     ▼                      ▼            │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐  │
│  │   WAF Rules     │    │   KMS Keys      │    │  S3 Evidence    │  │
│  │  (Rate limit)   │    │  (CMK)          │    │  (SSE-KMS)      │  │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## PCI DSS v4.0 Requirements Mapping

### Requirement 1: Network Security Controls

| Sub-Req | Requirement | AWS Service | Implementation |
|---------|-------------|-------------|----------------|
| 1.2.1 | Network segmentation | VPC | Private subnets for Lambda, DynamoDB VPC endpoints |
| 1.2.5 | Restrict inbound traffic | Security Groups | Allow only HTTPS (443) to API Gateway |
| 1.3.1 | Restrict outbound traffic | Security Groups | Egress rules limited to required AWS services |
| 1.4.2 | Wireless security | N/A | No wireless in cloud infrastructure |

**AWS Controls:**
```hcl
# VPC Endpoint for DynamoDB (keeps traffic within AWS network)
resource "aws_vpc_endpoint" "dynamodb" {
  vpc_id       = aws_vpc.dispute_cde.id
  service_name = "com.amazonaws.${var.region}.dynamodb"
  vpc_endpoint_type = "Gateway"
  route_table_ids = [aws_route_table.private.id]
}

# Security Group for Lambda in CDE
resource "aws_security_group" "lambda_cde" {
  name_prefix = "dispute-lambda-cde-"
  vpc_id      = aws_vpc.dispute_cde.id

  egress {
    description = "HTTPS to VPC endpoints"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    prefix_list_ids = [aws_vpc_endpoint.dynamodb.prefix_list_id]
  }
}
```

---

### Requirement 2: Secure Configurations

| Sub-Req | Requirement | AWS Service | Implementation |
|---------|-------------|-------------|----------------|
| 2.2.1 | Configuration standards | AWS Config | Conformance packs for CDE resources |
| 2.2.2 | Vendor defaults changed | IAM | No default credentials; IAM roles only |
| 2.2.5 | Remove unnecessary services | Lambda | Minimal runtime dependencies |
| 2.2.7 | Encrypt non-console admin | Systems Manager | Session Manager with encryption |

**AWS Config Rules:**
```yaml
# PCI DSS Conformance Pack
ConformancePackName: PCI-DSS-v4-Dispute-System
TemplateBody:
  Resources:
    DynamoDBEncryptionEnabled:
      Type: AWS::Config::ConfigRule
      Properties:
        ConfigRuleName: dynamodb-table-encrypted-kms
        Source:
          Owner: AWS
          SourceIdentifier: DYNAMODB_TABLE_ENCRYPTED_KMS

    LambdaInVPC:
      Type: AWS::Config::ConfigRule
      Properties:
        ConfigRuleName: lambda-inside-vpc
        Source:
          Owner: AWS
          SourceIdentifier: LAMBDA_INSIDE_VPC
```

---

### Requirement 3: Protect Stored Account Data

| Sub-Req | Requirement | AWS Service | Implementation |
|---------|-------------|-------------|----------------|
| 3.1.1 | Minimize CHD storage | Architecture | Only store tokens, never full PAN |
| 3.2.1 | No SAD after auth | Lambda | Validation rejects CVV/PIN fields |
| 3.3.1 | Mask PAN display | Application | Show only last 4 digits |
| 3.4.1 | Render PAN unreadable | KMS + Tokenization | Format-preserving tokenization |
| 3.5.1 | Protect cryptographic keys | KMS | AWS-managed HSM-backed keys |
| 3.6.1 | Key management procedures | KMS | Automatic key rotation enabled |

**Tokenization Strategy:**

```typescript
// Token format: tok_<random_24_chars>
// Maps to PAN in isolated tokenization service (out of CDE scope)

interface TokenizedCardData {
  /** Tokenized PAN - format: tok_[a-zA-Z0-9]{24} */
  pan_token: string;

  /** Last 4 digits (not considered CHD when isolated) */
  last4: string;

  /** Card fingerprint for matching without PAN */
  fingerprint: string;

  /** Token provider reference */
  tokenization_provider: 'stripe' | 'adyen' | 'aws_payment_cryptography';

  /** Token creation timestamp */
  tokenized_at: number;
}
```

**KMS Key Policy:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowDisputeLambdaDecrypt",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::ACCOUNT:role/dispute-lambda-role"
      },
      "Action": [
        "kms:Decrypt",
        "kms:GenerateDataKey"
      ],
      "Resource": "*",
      "Condition": {
        "StringEquals": {
          "kms:ViaService": "dynamodb.us-east-1.amazonaws.com"
        }
      }
    }
  ]
}
```

---

### Requirement 4: Protect Data in Transit

| Sub-Req | Requirement | AWS Service | Implementation |
|---------|-------------|-------------|----------------|
| 4.2.1 | Strong cryptography for transmission | API Gateway, ALB | TLS 1.2+ enforced |
| 4.2.1.1 | Trusted certificates | ACM | AWS Certificate Manager certs |
| 4.2.2 | Secure wireless | N/A | No wireless in scope |

**API Gateway TLS Configuration:**
```yaml
# OpenAPI security scheme
securityDefinitions:
  api_key:
    type: apiKey
    name: x-api-key
    in: header

x-amazon-apigateway-minimum-compression-size: 1024

# TLS 1.2 minimum via API Gateway settings
x-amazon-apigateway-endpoint-configuration:
  types:
    - REGIONAL
  # TLS 1.2 is default minimum for API Gateway
```

---

### Requirement 5: Protect Against Malware

| Sub-Req | Requirement | AWS Service | Implementation |
|---------|-------------|-------------|----------------|
| 5.2.1 | Anti-malware deployed | GuardDuty | Malware protection for S3 evidence bucket |
| 5.2.2 | Periodic scans | Inspector | Lambda vulnerability scanning |
| 5.3.1 | Anti-malware active | GuardDuty | Continuous monitoring enabled |

**GuardDuty Configuration:**
```hcl
resource "aws_guardduty_detector" "dispute_cde" {
  enable = true

  datasources {
    s3_logs {
      enable = true
    }
    malware_protection {
      scan_ec2_instance_with_findings {
        ebs_volumes {
          enable = true
        }
      }
    }
  }
}
```

---

### Requirement 6: Secure Systems and Software

| Sub-Req | Requirement | AWS Service | Implementation |
|---------|-------------|-------------|----------------|
| 6.2.1 | Bespoke software security | CodeGuru | Automated code review |
| 6.2.3 | Code review before production | CodePipeline | PR gates with security checks |
| 6.3.1 | Vulnerabilities identified | ECR, Inspector | Image and Lambda scanning |
| 6.4.1 | Public-facing app protection | WAF | OWASP Top 10 rules |
| 6.4.2 | Automated attack detection | WAF + Shield | Rate limiting, DDoS protection |

**WAF Rules for Dispute API:**
```json
{
  "Name": "DisputeAPIPCIProtection",
  "Rules": [
    {
      "Name": "AWSManagedRulesCommonRuleSet",
      "Priority": 1,
      "OverrideAction": { "None": {} },
      "Statement": {
        "ManagedRuleGroupStatement": {
          "VendorName": "AWS",
          "Name": "AWSManagedRulesCommonRuleSet"
        }
      },
      "VisibilityConfig": {
        "SampledRequestsEnabled": true,
        "CloudWatchMetricsEnabled": true,
        "MetricName": "CommonRuleSet"
      }
    },
    {
      "Name": "RateLimitDisputeAPI",
      "Priority": 2,
      "Action": { "Block": {} },
      "Statement": {
        "RateBasedStatement": {
          "Limit": 1000,
          "AggregateKeyType": "IP"
        }
      }
    },
    {
      "Name": "BlockPANInQueryString",
      "Priority": 3,
      "Action": { "Block": {} },
      "Statement": {
        "RegexPatternSetReferenceStatement": {
          "ARN": "arn:aws:wafv2:REGION:ACCOUNT:regional/regexpatternset/pan-pattern/ID",
          "FieldToMatch": { "QueryString": {} },
          "TextTransformations": [{ "Priority": 0, "Type": "URL_DECODE" }]
        }
      }
    }
  ]
}
```

---

### Requirement 7: Restrict Access by Need to Know

| Sub-Req | Requirement | AWS Service | Implementation |
|---------|-------------|-------------|----------------|
| 7.2.1 | Access control model defined | IAM | Role-based access with least privilege |
| 7.2.2 | Access based on job function | IAM | Separate roles per Lambda function |
| 7.2.3 | Deny by default | IAM | Explicit allow required |

**IAM Role Structure:**
```
dispute-system-roles/
├── dispute-intake-lambda-role        # Can write to DynamoDB, publish events
├── dispute-evidence-processor-role   # Can read S3, invoke Textract
├── dispute-network-submitter-role    # Can invoke external APIs
├── dispute-fraud-scorer-role         # Can invoke SageMaker endpoint
├── dispute-readonly-role             # Read-only for support staff
└── dispute-admin-role                # Full access (MFA required)
```

**Least Privilege Example:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DynamoDBDisputeTable",
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:UpdateItem",
        "dynamodb:Query"
      ],
      "Resource": [
        "arn:aws:dynamodb:*:*:table/Disputes",
        "arn:aws:dynamodb:*:*:table/Disputes/index/*"
      ],
      "Condition": {
        "ForAllValues:StringEquals": {
          "dynamodb:LeadingKeys": ["DISPUTE#*"]
        }
      }
    }
  ]
}
```

---

### Requirement 8: Identify Users and Authenticate Access

| Sub-Req | Requirement | AWS Service | Implementation |
|---------|-------------|-------------|----------------|
| 8.2.1 | Unique user IDs | IAM | Individual IAM users, no shared accounts |
| 8.3.1 | MFA for CDE access | IAM | MFA required for console and CLI |
| 8.3.4 | Password complexity | IAM | Password policy enforced |
| 8.3.6 | Password history | IAM | 24 password memory |
| 8.4.2 | MFA for remote access | SSO | AWS SSO with MFA |
| 8.6.1 | System/service accounts | IAM Roles | No long-term credentials |

**IAM Password Policy:**
```hcl
resource "aws_iam_account_password_policy" "pci_dss" {
  minimum_password_length        = 12
  require_lowercase_characters   = true
  require_uppercase_characters   = true
  require_numbers                = true
  require_symbols                = true
  allow_users_to_change_password = true
  max_password_age               = 90
  password_reuse_prevention      = 24
}
```

---

### Requirement 9: Restrict Physical Access

| Sub-Req | Requirement | AWS Service | Implementation |
|---------|-------------|-------------|----------------|
| 9.1.1 | Physical access controls | AWS Data Centers | AWS SOC 2 Type II attestation |
| 9.4.1 | Media protection | S3, EBS | Encryption at rest |

**AWS Shared Responsibility:**
- Physical security: AWS responsibility (covered by AWS Artifact compliance reports)
- Logical access: Customer responsibility (covered by IAM and other controls above)

---

### Requirement 10: Log and Monitor All Access

| Sub-Req | Requirement | AWS Service | Implementation |
|---------|-------------|-------------|----------------|
| 10.2.1 | Audit log capture | CloudTrail | All API calls logged |
| 10.2.1.1 | User access to CHD | CloudTrail + CloudWatch | DynamoDB access logged |
| 10.2.1.2 | Admin actions | CloudTrail | Management events captured |
| 10.3.1 | Log protection | S3 + KMS | Immutable, encrypted logs |
| 10.4.1 | Log review | CloudWatch | Automated alerts for anomalies |
| 10.5.1 | Log retention | S3 Lifecycle | 12-month minimum retention |
| 10.7.1 | Log failure alerts | CloudWatch Alarms | Alert on logging failures |

**CloudTrail Configuration:**
```hcl
resource "aws_cloudtrail" "dispute_cde" {
  name                          = "dispute-cde-trail"
  s3_bucket_name                = aws_s3_bucket.audit_logs.id
  include_global_service_events = true
  is_multi_region_trail         = true
  enable_log_file_validation    = true
  kms_key_id                    = aws_kms_key.audit_logs.arn

  event_selector {
    read_write_type           = "All"
    include_management_events = true

    data_resource {
      type   = "AWS::DynamoDB::Table"
      values = ["arn:aws:dynamodb:*:*:table/Disputes"]
    }

    data_resource {
      type   = "AWS::S3::Object"
      values = ["arn:aws:s3:::dispute-evidence-bucket/*"]
    }
  }
}
```

**CloudWatch Alarms for PCI DSS:**
```yaml
Alarms:
  - Name: UnauthorizedAPIAccess
    Metric: UnauthorizedAttemptCount
    Threshold: 5
    Period: 300
    Action: SNS notification to security team

  - Name: RootAccountUsage
    Metric: RootAccountUsageCount
    Threshold: 1
    Period: 60
    Action: Immediate SNS + PagerDuty

  - Name: DynamoDBHighReadLatency
    Metric: SuccessfulRequestLatency
    Threshold: 1000 # ms
    Period: 300
    Action: SNS notification
```

---

### Requirement 11: Test Security Regularly

| Sub-Req | Requirement | AWS Service | Implementation |
|---------|-------------|-------------|----------------|
| 11.2.1 | Vulnerability scans | Inspector | Weekly Lambda and container scans |
| 11.3.1 | Penetration testing | Third-party + AWS | Annual pen test with AWS pre-approval |
| 11.4.1 | IDS/IPS | GuardDuty | Network and API anomaly detection |
| 11.5.1 | Change detection | AWS Config | Configuration change monitoring |
| 11.6.1 | File integrity monitoring | CloudTrail + Config | S3 object integrity, config drift |

**Inspector Scan Configuration:**
```hcl
resource "aws_inspector2_enabler" "dispute_cde" {
  account_ids    = [data.aws_caller_identity.current.account_id]
  resource_types = ["LAMBDA", "ECR"]
}

# Automated findings export to Security Hub
resource "aws_securityhub_standards_subscription" "pci_dss" {
  standards_arn = "arn:aws:securityhub:${var.region}::standards/pci-dss/v/3.2.1"
}
```

---

### Requirement 12: Support Information Security Policies

| Sub-Req | Requirement | AWS Service | Implementation |
|---------|-------------|-------------|----------------|
| 12.1.1 | Security policy | Documentation | Maintained in this document |
| 12.3.1 | Risk assessment | Security Hub | Automated findings aggregation |
| 12.6.1 | Security awareness | AWS Training | Team completes AWS security training |
| 12.10.1 | Incident response plan | Runbook | Documented in incident-response.md |

---

## AWS Artifact Compliance Reports

The following AWS compliance reports should be downloaded from AWS Artifact annually:

| Report | Purpose | Frequency |
|--------|---------|-----------|
| SOC 2 Type II | Service organization controls | Annual |
| PCI DSS AOC | AWS PCI compliance attestation | Annual |
| ISO 27001 | Information security management | Annual |
| CSA STAR | Cloud security controls | Annual |

---

## Tokenization Architecture

### Token Flow

```
┌─────────────┐     ┌─────────────────────────┐     ┌─────────────┐
│   Payment   │     │   Token Service         │     │   Dispute   │
│   Gateway   │────▶│   (AWS Payment          │────▶│   System    │
│             │     │    Cryptography)        │     │  (DynamoDB) │
└─────────────┘     └─────────────────────────┘     └─────────────┘
      │                        │                          │
      │  PAN: 4111...1111     │  Token: tok_abc123       │  Token stored
      │  ─────────────────▶   │  ────────────────▶       │  (never PAN)
```

### Token Types

| Token Type | Format | Use Case | Reversible |
|------------|--------|----------|------------|
| Payment Token | `tok_[a-zA-Z0-9]{24}` | Transaction processing | By payment gateway only |
| Network Token | Visa/MC format | Network submissions | By issuer only |
| Internal Token | `int_[a-zA-Z0-9]{24}` | Internal references | Never (one-way hash) |

---

## Compliance Checklist

### Pre-Production

- [ ] VPC endpoints configured for DynamoDB and S3
- [ ] KMS CMK created with appropriate key policy
- [ ] CloudTrail enabled with log file validation
- [ ] WAF rules deployed on API Gateway
- [ ] IAM roles follow least privilege principle
- [ ] Password policy meets PCI DSS requirements
- [ ] GuardDuty enabled with S3 malware protection
- [ ] Security Hub enabled with PCI DSS standard
- [ ] Inspector scanning enabled for Lambda

### Ongoing

- [ ] Monthly access review for IAM users/roles
- [ ] Quarterly vulnerability scan review
- [ ] Annual penetration test (with AWS pre-approval)
- [ ] Annual security awareness training
- [ ] Annual risk assessment update
- [ ] Annual AWS Artifact report download

---

## Related Documents

- [Schema Explanation](../SCHEMA_EXPLANATION.md)
- [Tokenization Types](../dispute_types.ts) - `TokenizedCardData` interface
- [Lambda Interfaces](./lambda-interfaces.ts)
- [DynamoDB Schema](./dynamodb-schema.md)
- [Reg E Timelines](./reg_e_timelines.ts)

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2024-12-04 | System | Initial PCI DSS v4.0 mapping |
