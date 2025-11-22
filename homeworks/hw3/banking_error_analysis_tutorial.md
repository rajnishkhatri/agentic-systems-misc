# Error Analysis Concepts Tutorial - Banking Domain

## Learning Objectives

By completing this tutorial, you will be able to:
- ✅ Understand qualitative vs. quantitative evaluation for banking AI systems
- ✅ Apply open coding methodology to identify patterns in financial assistant failures
- ✅ Perform axial coding to group observations into structured failure modes
- ✅ Build comprehensive failure mode taxonomies for banking interactions
- ✅ Know when to use error analysis vs. automated metrics
- ✅ Document failure patterns systematically for compliance and audit

## Prerequisites

- Completed HW1: System Prompt Engineering
- Have collected diverse banking assistant test results
- Basic understanding of banking operations and compliance requirements

## Estimated Time

**Reading Time:** 25-30 minutes  
**Hands-on Practice:** 30-45 minutes

---

## Concepts

### Why Error Analysis Matters in Banking

After writing a good system prompt and testing with diverse banking queries, your financial AI assistant **will still fail in critical ways**. Given the regulatory and financial implications, systematic analysis is essential.

**The problem with informal evaluation:**
- 👀 "This transaction explanation seems off" → Not systematic
- 🤷 "I think compliance checking is better now" → Not measurable  
- 🔄 "Let me adjust the prompt" → No understanding of *why* failures occur

**Error analysis provides:**
- 🔍 **Systematic failure identification** - Find patterns in compliance violations or incorrect financial guidance
- 📊 **Categorization and taxonomy** - Organize failures by risk level and regulatory impact
- 📝 **Documentation** - Audit-ready analysis for regulatory review
- 🎯 **Prioritization** - Focus on high-risk, high-frequency failures

### Qualitative vs. Quantitative Evaluation

| Aspect | Qualitative Evaluation | Quantitative Evaluation |
|--------|------------------------|-------------------------|
| **Data** | Text descriptions, compliance notes, user feedback | Accuracy rates, error percentages, response times |
| **Focus** | Understanding *why* incorrect financial advice occurs | Measuring *how often* compliance failures happen |
| **Methods** | Open coding, axial coding, risk categorization | Accuracy, precision/recall, regulatory breach rate |
| **Output** | Failure taxonomies, compliance patterns, risk insights | Statistical metrics, SLA adherence, confidence intervals |
| **When to use** | Early exploration, unknown failure modes | After identifying failure modes, tracking improvements |
| **Example** | "Bot provides outdated interest rates for savings accounts" | "23% of rate queries return information >30 days old" |

**Key Insight:** Start with **qualitative** (HW2) to understand failures, then move to **quantitative** (HW3+) to measure them at scale.

---

## The Error Analysis Process

```
┌─────────────────────────────────────────────────────────┐
│           ERROR ANALYSIS WORKFLOW - BANKING             │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1. COLLECT TRACES                                      │
│     ↓                                                   │
│     Run bot on diverse banking queries (20-50+ traces)  │
│     Record full interactions including compliance checks │
│                                                         │
│  2. OPEN CODING (Exploratory)                           │
│     ↓                                                   │
│     Review traces without preconceived categories       │
│     Note regulatory issues, accuracy problems, UX issues│
│                                                         │
│  3. AXIAL CODING (Organizational)                       │
│     ↓                                                   │
│     Group into: Compliance, Accuracy, Security, UX      │
│     Define risk levels and regulatory implications      │
│                                                         │
│  4. BUILD TAXONOMY                                      │
│     ↓                                                   │
│     Write formal failure definitions with risk levels   │
│     Add regulatory references where applicable          │
│                                                         │
│  5. RISK & FREQUENCY ANALYSIS                           │
│     ↓                                                   │
│     Calculate frequency and severity scores             │
│     Identify patterns requiring immediate remediation   │
│                                                         │
│  6. REMEDIATION PLANNING                                │
│     ↓                                                   │
│     Design guardrails for high-risk failures            │
│     Implement additional validation layers              │
│     Schedule re-testing and compliance review           │
└─────────────────────────────────────────────────────────┘
```

---

## Open Coding Methodology

### What is Open Coding?

**Open coding** is an exploratory analysis technique where you:
- Review interaction traces **without preconceived categories**
- Assign **descriptive labels/notes** to interesting patterns
- Identify potential errors, compliance issues, or security risks
- Avoid forcing observations into predetermined buckets

**Origin:** Borrowed from **Grounded Theory** (qualitative research methodology)

**Key Principle:** Let the patterns emerge from the data, rather than imposing structure upfront.

### The Open Coding Process for Banking

#### Step 1: Collect Traces

Run your banking assistant on diverse queries and record:
- User query (input)
- Bot response (output)
- Transaction type/category
- Compliance requirements triggered
- Risk level assessment

**Query Categories to Test:**
- Transaction inquiries
- Account balance checks  
- Loan eligibility questions
- Fee explanations
- Regulatory compliance queries
- Fraud reporting
- International transfers
- Investment advice
- Credit card applications

**How many traces?** Start with 20-50. Look for **saturation** - the point where you stop seeing new patterns.

#### Step 2: Initial Review

Read through each trace carefully:
- Don't judge or categorize yet
- Note accuracy of financial information
- Check for compliance issues
- Identify security considerations
- Observe customer experience aspects

**Mindset:** Think like an auditor - curious but thorough.

#### Step 3: Descriptive Labeling

**Example Trace:**
```
Query: "Quick way to transfer $15,000 to my friend's account"

Response:
You can transfer $15,000 to your friend through our online banking platform.

**Steps:**
1. Log into online banking
2. Navigate to "Transfers"
3. Select "External Transfer"
4. Add your friend's account details
5. Enter $15,000 as the amount
6. Confirm and submit

The transfer typically processes within 1-2 business days.
```

**Open Codes (Observations):**
- `missing_daily_limit_warning` → No mention of daily transfer limits ($10,000)
- `no_fraud_prevention_mention` → Large transfer without security verification mention
- `missing_fee_disclosure` → No mention of wire transfer fees
- `no_tax_reporting_note` → Transfers >$10,000 require CTR reporting
- `missing_alternative_options` → Doesn't suggest wire transfer for large amounts
- `no_beneficiary_verification` → No mention of verifying recipient details
- `good_step_structure` → [Positive] Clear step-by-step instructions
- `appropriate_timeline` → [Positive] Accurate processing time mentioned

#### Step 4: Pattern Identification

After coding 20 traces, you might see:
- `missing_regulatory_disclosure` appears in **16 traces** (80%)
- `incorrect_limit_information` appears in **9 traces** (45%)
- `no_fee_disclosure` appears in **14 traces** (70%)
- `missing_security_verification` appears in **11 traces** (55%)

**Insight:** Regulatory disclosures and fee transparency are critical gaps requiring immediate attention.

---

## Axial Coding: Building Banking Taxonomies

### What is Axial Coding?

**Axial coding** takes your open codes and organizes them into **structured failure mode taxonomies** specific to banking operations.

**Goal:** Group related observations into broader categories that:
- Are **risk-aligned** (map to operational/regulatory risk frameworks)
- Have **clear compliance implications**
- Enable **targeted remediation**

### From Open Codes to Failure Modes

#### Example: Grouping Open Codes

**Open codes observed:**
- `missing_daily_limit_warning`
- `no_aml_disclosure`
- `missing_ctr_requirement`
- `no_ofac_screening_mention`

**Axial grouping:** **"Regulatory Compliance Gaps"**

**Another set:**
- `outdated_rate_information`
- `wrong_account_minimum`
- `incorrect_penalty_calculation`
- `misquoted_apr`

**Axial grouping:** **"Inaccurate Financial Information"**

### Banking Bot Failure Taxonomy Structure

Each failure mode should include:

1. **Title** - Specific failure category
2. **Definition** - One-sentence explanation
3. **Risk Level** - Critical/High/Medium/Low
4. **Regulatory Impact** - Applicable regulations (Reg E, Reg Z, BSA, TILA, etc.)
5. **Examples** - 2-3 concrete instances from traces
6. **Remediation Priority** - Immediate/High/Medium/Low

### Complete Banking Bot Failure Taxonomy

#### Failure Mode 1: Missing Regulatory Disclosures

**Definition:** Bot fails to provide required regulatory disclosures for financial transactions or products.

**Risk Level:** High

**Regulatory Impact:** TILA, Reg Z, Reg DD, UDAAP

**Examples:**
1. *Query*: "How do I open a CD account?"
   *Issue*: No mention of early withdrawal penalties, FDIC insurance coverage, or APY disclosure

2. *Query*: "Transfer $25,000 internationally"
   *Issue*: Missing OFAC screening requirements, IRS Form 8300 reporting, and BSA obligations

3. *Query*: "Apply for home equity line of credit"
   *Issue*: No mention of right to rescission, variable rate disclosures, or closing costs

**Remediation Priority:** Immediate

---

#### Failure Mode 2: Incorrect Transaction Limits

**Definition:** Bot provides incorrect information about daily, monthly, or per-transaction limits.

**Risk Level:** Medium-High

**Regulatory Impact:** Reg D, Reg E, internal policy violations

**Examples:**
1. *Query*: "What's my daily ATM withdrawal limit?"
   *Issue*: States $1,000 when actual limit is $500, causing customer transaction failures

2. *Query*: "Maximum wire transfer amount?"
   *Issue*: Doesn't differentiate between domestic ($100,000) and international ($50,000) limits

3. *Query*: "Savings account withdrawal rules"
   *Issue*: Doesn't mention 6-withdrawal monthly limit per Reg D

**Remediation Priority:** High

---

#### Failure Mode 3: Security Protocol Omissions

**Definition:** Bot fails to mention required security steps, authentication procedures, or fraud prevention measures.

**Risk Level:** Critical

**Regulatory Impact:** Reg E, FFIEC guidelines, data protection regulations

**Examples:**
1. *Query*: "Change my account password"
   *Issue*: Doesn't mention two-factor authentication requirement or password complexity rules

2. *Query*: "Report unauthorized transaction"
   *Issue*: No mention of 60-day reporting window for liability protection under Reg E

3. *Query*: "Add new payee for bill payment"
   *Issue*: Doesn't mention verification process or cooling-off period for new payees

**Remediation Priority:** Immediate

---

#### Failure Mode 4: Outdated Product Information

**Definition:** Bot provides interest rates, fees, or terms that don't match current offerings.

**Risk Level:** Medium

**Regulatory Impact:** UDAAP, Truth in Advertising

**Examples:**
1. *Query*: "Current mortgage rates?"
   *Issue*: Quotes rates from last quarter, 0.75% lower than current

2. *Query*: "Checking account monthly fees"
   *Issue*: Lists old fee structure, missing recent $2 increase

**Remediation Priority:** Medium

---

#### Failure Mode 5: Inadequate Risk Warnings

**Definition:** Bot fails to provide appropriate warnings about financial risks or product suitability.

**Risk Level:** High

**Regulatory Impact:** FINRA rules, suitability requirements, fiduciary duty

**Examples:**
1. *Query*: "Should I invest my emergency fund in stocks?"
   *Issue*: Doesn't warn about liquidity needs or market volatility risks

2. *Query*: "Reverse mortgage information"
   *Issue*: No mention of risks to heirs or impact on government benefits

**Remediation Priority:** High

---

#### Failure Mode 6: Missing Authentication Steps

**Definition:** Bot provides account-specific information without verifying user identity.

**Risk Level:** Critical

**Regulatory Impact:** GLBA, privacy regulations, FFIEC authentication guidance

**Examples:**
1. *Query*: "What's my account balance?"
   *Issue*: Attempts to provide balance without authentication verification

2. *Query*: "List my recent transactions"
   *Issue*: Would display transaction history without security questions

**Remediation Priority:** Immediate

---

#### Failure Mode 7: Incomplete Fee Disclosures

**Definition:** Bot fails to mention all applicable fees or charges for services.

**Risk Level:** Medium-High

**Regulatory Impact:** Reg DD, TISA, UDAAP

**Examples:**
1. *Query*: "Wire transfer to Europe"
   *Issue*: Mentions wire fee but not foreign exchange markup or correspondent bank fees

2. *Query*: "Overdraft protection options"
   *Issue*: Doesn't disclose transfer fees or daily overdraft charges

**Remediation Priority:** High

---

#### Failure Mode 8: Non-compliant Investment Guidance

**Definition:** Bot provides investment advice without proper disclaimers or suitability assessment.

**Risk Level:** High

**Regulatory Impact:** SEC regulations, FINRA rules, fiduciary standards

**Examples:**
1. *Query*: "Best mutual funds for retirement"
   *Issue*: Recommends specific funds without risk assessment or disclaimers

2. *Query*: "Should I buy cryptocurrency?"
   *Issue*: Provides advice without volatility warnings or regulatory status

**Remediation Priority:** High

---

## Optional: Spreadsheet Analysis

### Spreadsheet Structure for Banking

| Column Name | Purpose | Example |
|-------------|---------|---------|
| `Trace_ID` | Unique identifier | B001, B002 |
| `Query_Type` | Transaction category | Transfer, Balance, Loan |
| `User_Query` | Original query | "transfer $15,000" |
| `Bot_Response_Summary` | Brief summary | "Steps provided, no limits mentioned" |
| `Open_Code_Notes` | Observations | "missing_limit, no_ctr_mention" |
| `Compliance_Gap` | Binary (0 or 1) | 1 |
| `Security_Issue` | Binary (0 or 1) | 0 |
| `Incorrect_Info` | Binary (0 or 1) | 0 |
| `Risk_Level` | Critical/High/Medium/Low | High |
| `Regulatory_Impact` | Regulations affected | "BSA, Reg D" |

### Analyzing Banking-Specific Metrics

```python
import pandas as pd

df = pd.read_csv('banking_error_analysis.csv')

# Calculate risk distribution
risk_distribution = df['Risk_Level'].value_counts()

# Identify high-risk failure combinations
high_risk = df[(df['Risk_Level'].isin(['Critical', 'High']))]
print(f"High-risk failures: {len(high_risk)}/{len(df)} ({100*len(high_risk)/len(df):.1f}%)")

# Regulatory impact analysis
regulatory_failures = df[df['Compliance_Gap'] == 1]
print(f"Compliance failures: {len(regulatory_failures)}/{len(df)}")
```

---

## From Taxonomy to Action

### Banking-Specific Prioritization Matrix

| Failure Mode | Frequency | Risk Level | Regulatory Impact | Priority |
|--------------|-----------|------------|-------------------|----------|
| Security Protocol Omissions | 15% | Critical | High (BSA, Reg E) | **Immediate** |
| Missing Regulatory Disclosures | 80% | High | High (Multiple) | **Immediate** |
| Missing Authentication Steps | 10% | Critical | High (GLBA) | **Immediate** |
| Incorrect Transaction Limits | 45% | Medium-High | Medium (Reg D) | **High** |
| Inadequate Risk Warnings | 35% | High | High (FINRA) | **High** |
| Incomplete Fee Disclosures | 70% | Medium-High | Medium (Reg DD) | **High** |
| Outdated Product Information | 60% | Medium | Low | **Medium** |

### Designing Banking Interventions

#### For "Missing Regulatory Disclosures"

**1. Update system prompt:**
```python
BANKING_COMPLIANCE_PROMPT = """
For ALL financial product discussions, you MUST include:
- FDIC insurance status and coverage limits
- APY/APR with calculation method
- All fees (monthly, transaction, penalty)
- Early withdrawal penalties for time deposits
- Reg Z disclosures for credit products
- BSA/AML requirements for transactions >$10,000

Format disclosures clearly:
**Required Disclosures:**
- [Specific disclosure points]
"""
```

**2. Add compliance validation layer:**
```python
def validate_compliance(query, response):
    compliance_checks = {
        'transfer': ['daily_limit', 'fee', 'processing_time'],
        'loan': ['apr', 'fees', 'payment_schedule'],
        'investment': ['risk_disclaimer', 'not_fdic_insured'],
        'international': ['ofac', 'reporting_requirement']
    }
    
    query_type = categorize_query(query)
    required_elements = compliance_checks.get(query_type, [])
    
    missing = []
    for element in required_elements:
        if element not in response.lower():
            missing.append(element)
    
    if missing:
        return f"WARNING: Missing required elements: {missing}"
    return "PASS"
```

**3. Implement multi-layer guardrails:**

```python
class BankingGuardrails:
    def __init__(self):
        self.regulatory_keywords = {
            'BSA': ['$10,000', 'currency transaction'],
            'Reg_E': ['unauthorized', 'dispute', 'fraud'],
            'Reg_Z': ['credit', 'loan', 'apr', 'finance charge'],
            'OFAC': ['international', 'wire', 'foreign']
        }
    
    def check_triggers(self, query):
        """Identify which regulations apply to this query"""
        triggered_regs = []
        for reg, keywords in self.regulatory_keywords.items():
            if any(kw in query.lower() for kw in keywords):
                triggered_regs.append(reg)
        return triggered_regs
    
    def get_required_disclosures(self, regulations):
        """Return required disclosures for triggered regulations"""
        disclosure_map = {
            'BSA': "Currency Transaction Report (CTR) required for cash transactions over $10,000",
            'Reg_E': "Report unauthorized transactions within 60 days for liability protection",
            'Reg_Z': "See Truth in Lending disclosures including APR and total finance charges",
            'OFAC': "International transfers subject to OFAC screening and may be delayed"
        }
        return [disclosure_map[reg] for reg in regulations]
```

### Measuring Improvement

**Pre/Post Intervention Metrics:**

| Failure Mode | Baseline | Week 1 | Week 4 | Target | Status |
|--------------|----------|--------|--------|--------|--------|
| Security Protocol Omissions | 15% | 8% | 2% | <1% | 🟡 Near target |
| Missing Regulatory Disclosures | 80% | 45% | 12% | <5% | 🟡 Improving |
| Missing Authentication | 10% | 0% | 0% | 0% | ✅ Resolved |
| Incorrect Transaction Limits | 45% | 20% | 8% | <5% | 🟡 Near target |
| Inadequate Risk Warnings | 35% | 25% | 15% | <10% | 🟡 Improving |

**Continuous Monitoring Dashboard:**
- Daily failure rate tracking
- Regulatory breach alerts
- Customer complaint correlation
- Audit trail maintenance

---

## Common Pitfalls - Banking Context

### Banking-Specific Open Coding Pitfalls

#### 1. Ignoring Regulatory Nuance
**❌ Problem:** Coding "wrong information" without specifying regulatory implications

**✅ Solution:** Always note which regulation or policy is affected

#### 2. Missing Risk Gradation
**❌ Problem:** Treating all failures equally without risk assessment

**✅ Solution:** Always assign risk levels (Critical/High/Medium/Low)

#### 3. Overlooking Cascading Failures
**❌ Problem:** Not noting when one failure could trigger others

**Example:** Missing authentication → Privacy violation → Regulatory breach

**✅ Solution:** Document failure chains and dependencies

### Banking Taxonomy Pitfalls

#### 1. Regulation-Agnostic Categories
**❌ Problem:** Categories like "Wrong Information" without regulatory context

**✅ Solution:** Categories should map to regulatory frameworks:
- "Reg E Non-Compliance"
- "BSA Reporting Failures"
- "TILA Disclosure Gaps"

#### 2. Ignoring Customer Impact
**❌ Problem:** Focus only on compliance without considering customer harm

**✅ Solution:** Include customer impact in risk assessment:
- Financial loss potential
- Privacy breach risk
- Service disruption impact

---

## Key Takeaways for Banking AI

- ✅ **Regulatory compliance is paramount** - Every failure has potential regulatory implications
- ✅ **Risk-based prioritization** - Critical security/compliance issues before UX improvements
- ✅ **Documentation for audit** - Maintain detailed traces for regulatory review
- ✅ **Multi-layer validation** - Combine prompt engineering, guardrails, and post-processing
- ✅ **Continuous monitoring** - Banking regulations change; re-evaluate regularly
- ✅ **Cross-functional review** - Involve compliance, legal, and risk teams in taxonomy validation
- ✅ **Customer protection focus** - Balance compliance with customer experience and protection
- ✅ **Proactive risk management** - Identify and remediate issues before regulatory findings

---

## Implementation Checklist

### Immediate Actions (Week 1)
- [ ] Identify all Critical risk failures
- [ ] Implement authentication checks
- [ ] Add basic regulatory disclosures
- [ ] Create incident response plan

### Short-term (Month 1)
- [ ] Complete full taxonomy development
- [ ] Implement compliance validation layer
- [ ] Deploy guardrails for high-risk scenarios
- [ ] Establish monitoring dashboard

### Ongoing
- [ ] Weekly failure rate reviews
- [ ] Monthly regulatory update checks
- [ ] Quarterly taxonomy refinement
- [ ] Annual comprehensive audit

---

## Resources and References

### Regulatory Guidelines
- **FFIEC Examination Procedures** - Authentication and security requirements
- **BSA/AML Examination Manual** - Transaction monitoring requirements
- **Regulation E (Electronic Fund Transfers)** - Error resolution and liability
- **Regulation Z (Truth in Lending)** - Disclosure requirements
- **UDAAP Guidelines** - Unfair, deceptive, or abusive practices

### Industry Best Practices
- **ISO 27001** - Information security management
- **PCI DSS** - Payment card security standards
- **COBIT** - IT governance framework
- **NIST Cybersecurity Framework** - Risk management approach

### Internal Documentation Templates
- Failure Mode Tracking Spreadsheet
- Regulatory Compliance Checklist
- Risk Assessment Matrix
- Remediation Planning Template

---

**Document Status:** ✅ Complete  
**Last Updated:** 2024-11-20  
**Next Review:** Quarterly  
**Owner:** AI Risk Management Team  

**Regulatory Note:** This document provides general guidance. Always consult current regulations and your institution's compliance team for specific requirements in your jurisdiction.

**Confidentiality:** This document contains sensitive information about system vulnerabilities and should be handled according to your institution's information security policies.