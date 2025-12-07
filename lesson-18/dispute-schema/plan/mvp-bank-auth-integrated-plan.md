# Integrated MVP Plan: Bank Auth + Agentic Dispute Chatbot

## Document Status
| Field | Value |
|-------|-------|
| **Version** | 1.0 |
| **Created** | December 2024 |
| **Phase** | Planning Complete → Design Phase Next |
| **Source Documents** | `mvp-agentic-chatbot-synthesized-plan.md`, `Bank_Authentication_System_Integration_Summary.md` |

---

## Executive Summary

| Metric | Value |
|--------|-------|
| **Timeline** | 8 weeks (unchanged) |
| **Backend Readiness** | 70% (leverage existing `dispute-schema`) |
| **Auth System** | Bank SAML SSO (replaces Cognito) |
| **JWT Algorithm** | RS256 (enterprise-grade, replaces HS256) |
| **Critical Path** | Bank Auth → MCP Tools → PCI Guardrails → Dialogue → Integration |

---

## Integration Analysis

### Problem Definition (Polya Framework)

**What is the unknown?**
- How to integrate Bank SAML SSO authentication into the MVP Agentic Chatbot architecture

**What are the data?**
- MVP Plan: 8-week timeline, 4 MCP tools, Cognito auth (current), DynamoDB sessions, PCI guardrails
- Bank Auth: SAML SSO, RS256 JWT, minimal 4-file change approach, LangGraph validation

**Is the condition sufficient?**
- Yes: Both plans use JWT-based auth and DynamoDB sessions
- Integration point: Replace Cognito with Bank SAML SSO at the gateway layer

**Compatibility Assessment:**
- ✅ Both use JWT-based authentication
- ✅ Both use DynamoDB for sessions
- ✅ Both target minimal disruption
- ⚠️ Key difference: Cognito (HS256) → Bank SAML SSO (RS256)

---

## Architecture Changes

### Original Architecture (Cognito)
```
┌─────────────────────────────────────────────────────────────────────┐
│                        CHAT GATEWAY (API Gateway)                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────────┐  │
│  │   Cognito   │  │ Rate Limit  │  │     PCI INPUT FILTER        │  │
│  │   (Auth)    │  │  (100/min)  │  │  (Luhn + Regex + Block)     │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

### Integrated Architecture (Bank SAML SSO)
```
┌──────────────────────────────────────────────────────────────────────┐
│                     CHAT GATEWAY (API Gateway)                        │
│  ┌──────────────────┐  ┌─────────────┐  ┌────────────────────────┐  │
│  │  BANK SAML SSO   │  │ Rate Limit  │  │    PCI INPUT FILTER    │  │
│  │  ┌────────────┐  │  │  (100/min)  │  │  (Luhn + Regex + Block)│  │
│  │  │ RS256 JWT  │  │  │             │  │                        │  │
│  │  │ Validation │  │  │             │  │                        │  │
│  │  └────────────┘  │  │             │  │                        │  │
│  └────────┬─────────┘  └─────────────┘  └────────────────────────┘  │
└───────────┼──────────────────────────────────────────────────────────┘
            │ BankUserContext
            ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    LLM ORCHESTRATOR (Lambda)                          │
│                                                                       │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────┐  │
│  │  Claude API     │  │  Dialogue State │  │  Session Store      │  │
│  │  (Bedrock or    │◄─┤  Manager        │◄─┤  (DynamoDB)         │  │
│  │   Direct)       │  │                 │  │  +bankUserId        │  │
│  │                 │  │                 │  │  +jwtSubject        │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────────┘  │
│           │                                                          │
│           │ Tool Calls + BankUserContext                             │
│           ▼                                                          │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                      MCP TOOL LAYER                            │  │
│  │                                                                │  │
│  │  ┌────────────────┐  ┌────────────────┐                       │  │
│  │  │  file_dispute  │  │  check_status  │   MVP: 4 Tools        │  │
│  │  │  +userContext  │  │  +userContext  │   (all auth-aware)    │  │
│  │  └───────┬────────┘  └───────┬────────┘                       │  │
│  │  ┌───────┴────────┐  ┌───────┴────────┐                       │  │
│  │  │  add_evidence  │  │ get_deadline   │                       │  │
│  │  │  +userContext  │  │ (Reg E/Z)      │                       │  │
│  │  └───────┬────────┘  └───────┬────────┘                       │  │
│  └──────────┼───────────────────┼────────────────────────────────┘  │
└─────────────┼───────────────────┼────────────────────────────────────┘
              │                   │
              ▼                   ▼
┌──────────────────────────────────────────────────────────────────────┐
│                  EXISTING DISPUTE-SCHEMA BACKEND                      │
│                                                                       │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────────────────┐  │
│  │  REST API    │  │  Step        │  │  reg_e_timelines.ts       │  │
│  │  (OpenAPI)   │  │  Functions   │  │  (Compliance Calculator)  │  │
│  └──────────────┘  └──────────────┘  └───────────────────────────┘  │
│                                                                       │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────────────────┐  │
│  │  DynamoDB    │  │  fraud_      │  │  dispute_classifier.py    │  │
│  │  (Disputes)  │  │  detector.py │  │  (NLP Classification)     │  │
│  └──────────────┘  └──────────────┘  └───────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Authentication Flow (Bank SAML SSO)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    BANK SAML SSO AUTHENTICATION FLOW                     │
└─────────────────────────────────────────────────────────────────────────┘

    User              Frontend           Bank Auth         Bank SAML        LangGraph
     │                   │               Service              IdP           Backend
     │                   │                  │                  │               │
     │  Access App       │                  │                  │               │
     │──────────────────>│                  │                  │               │
     │                   │  Check Session   │                  │               │
     │                   │─────────────────>│                  │               │
     │                   │  No Session      │                  │               │
     │                   │<─────────────────│                  │               │
     │                   │                  │                  │               │
     │  Click Bank SSO   │                  │                  │               │
     │──────────────────>│                  │                  │               │
     │                   │  initiateSAML()  │                  │               │
     │                   │─────────────────>│                  │               │
     │                   │                  │  SAML Request    │               │
     │                   │                  │─────────────────>│               │
     │                   │                  │                  │               │
     │                   │        Redirect to Bank Login       │               │
     │<────────────────────────────────────────────────────────│               │
     │                   │                  │                  │               │
     │  Enter Bank Credentials             │                  │               │
     │────────────────────────────────────────────────────────>│               │
     │                   │                  │                  │               │
     │                   │                  │  SAML Assertion  │               │
     │                   │                  │<─────────────────│               │
     │                   │                  │                  │               │
     │                   │                  │  Validate +      │               │
     │                   │                  │  Generate RS256  │               │
     │                   │                  │  JWT             │               │
     │                   │                  │                  │               │
     │                   │  JWT + UserData  │                  │               │
     │                   │<─────────────────│                  │               │
     │                   │                  │                  │               │
     │  Show Chat UI     │                  │                  │               │
     │<──────────────────│                  │                  │               │
     │                   │                  │                  │               │
     │  Send Message     │                  │                  │               │
     │──────────────────>│                  │                  │               │
     │                   │  API + JWT                          │               │
     │                   │────────────────────────────────────────────────────>│
     │                   │                  │                  │               │
     │                   │                  │  Validate JWT    │               │
     │                   │                  │<─────────────────────────────────│
     │                   │                  │  User Verified   │               │
     │                   │                  │─────────────────────────────────>│
     │                   │                  │                  │               │
     │                   │  Chat Response                      │               │
     │                   │<────────────────────────────────────────────────────│
     │  Display Response │                  │                  │               │
     │<──────────────────│                  │                  │               │
     │                   │                  │                  │               │
```

---

## New Components to Add

### 1. Bank Auth Integration Layer
```
mcp-server/src/auth/
├── bank-auth-service.ts    # SAML assertion handler
├── jwt-validator.ts        # RS256 public key validation
└── user-context.ts         # Extract bank user from JWT
```

### 2. Bank User Context (passed to all MCP tools)
```typescript
interface BankUserContext {
  bankUserId: string;        // From SAML NameID
  accountAccess: string[];   // Accounts user can file disputes for
  roles: string[];           // customer | employee | supervisor
  sessionBound: boolean;     // Prevent session hijacking
  jwtExpiry: number;         // Token expiration timestamp
}
```

### 3. Modified Session Schema (DynamoDB)
```typescript
// chatbot-sessions table schema
interface ChatbotSession {
  // Existing fields
  sessionId: string;          // PK: UUID
  timestamp: number;          // SK
  conversationHistory: Message[];
  currentDisputeId?: string;
  slotFillingState: object;
  TTL: number;                // 24 hours

  // NEW: Bank Auth fields (replaces customerId)
  bankUserId: string;         // From SAML NameID
  bankEmployeeId?: string;    // For internal users
  jwtSubject: string;         // Bind session to JWT sub claim
  jwtIssuer: string;          // Bank IdP issuer for validation
  ipAddress: string;          // Additional session binding
}
```

### 4. JWT Validation Configuration
```typescript
interface BankJWTConfig {
  algorithm: 'RS256';                    // Enterprise standard
  issuer: string;                        // Bank IdP URL
  audience: string;                      // Chatbot client ID
  publicKeyEndpoint: string;             // JWKS endpoint
  clockTolerance: 30;                    // seconds
  maxAge: '8h';                          // Token lifetime
}
```

---

## Revised Timeline (8 Weeks - Unchanged Duration)

| Week | Original Scope | + Bank Auth Integration |
|------|----------------|-------------------------|
| **1-2** | MCP Tool Layer Foundation | + `user-context.ts` extraction from JWT |
| **3-4** | PCI Guardrails + Sessions | + **Bank Auth Service, RS256 validation, SAML callback handler** |
| **5-6** | Dialogue Engine + NLG | (unchanged - auth already integrated) |
| **7** | Integration + E2E Testing | + Bank Auth API validation, JWT refresh flow testing |
| **8** | Security Review + Launch | + SAML penetration test, RS256 key rotation test |

### Week 3-4 Detailed (Bank Auth Focus)
```
Priority: CRITICAL (Compliance + Auth)
Deliverables:
├── Bank Auth Integration
│   ├── chatbot/services/BankAuthService.ts
│   │   ├── initiateSAMLFlow()
│   │   ├── handleSAMLCallback()
│   │   ├── validateAssertion()
│   │   └── generateSession()
│   │
│   ├── mcp-server/src/auth/jwt-validator.ts
│   │   ├── RS256 signature validation
│   │   ├── JWKS public key fetching
│   │   ├── Claims validation (iss, aud, exp)
│   │   └── Token refresh handling
│   │
│   └── mcp-server/src/auth/user-context.ts
│       ├── extractBankUser(jwt: string)
│       ├── validateAccountAccess(userId, accountId)
│       └── buildToolContext(user, session)
│
├── PCI Compliance Layer (unchanged)
│   └── ...
│
├── Session Management (DynamoDB) - MODIFIED
│   ├── Table: chatbot-sessions
│   │   ├── PK: sessionId (UUID)
│   │   ├── SK: timestamp
│   │   ├── bankUserId: string        # NEW
│   │   ├── jwtSubject: string        # NEW
│   │   ├── jwtIssuer: string         # NEW
│   │   ├── ipAddress: string         # NEW
│   │   ├── conversationHistory: Message[]
│   │   ├── currentDisputeId: string?
│   │   ├── slotFillingState: object
│   │   └── TTL: 24 hours
```

---

## MCP Tool Specifications (Updated with Auth Context)

### Tool 1: `file_dispute` (Updated)
```typescript
// Input - now includes auth context
interface FileDisputeInput {
  // Auth context (injected by orchestrator)
  _userContext: BankUserContext;        // NEW: Required

  // Existing fields
  charge_id?: string;
  amount_cents?: number;
  merchant_name?: string;
  transaction_date?: string;
  reason: DisputeReason;
  complaint_narrative?: string;
}

// Implementation validates user can access the account
async function fileDispute(input: FileDisputeInput): Promise<FileDisputeOutput> {
  // Validate user has access to file dispute for this account
  const account = await lookupAccountForCharge(input.charge_id);
  if (!input._userContext.accountAccess.includes(account.id)) {
    throw new UnauthorizedError('User cannot file disputes for this account');
  }

  // Proceed with dispute filing...
}
```

### Tool 2-4: Similar Auth Context Pattern
All tools receive `_userContext` and validate access before proceeding.

---

## Security Comparison

| Aspect | Original (Cognito) | Integrated (Bank SAML) |
|--------|-------------------|------------------------|
| **Algorithm** | HS256 | RS256 (stronger) |
| **Key Management** | AWS managed | Bank HSM-managed |
| **Identity Source** | Cognito User Pool | Corporate Active Directory |
| **Session Binding** | Cognito session | JWT subject + IP |
| **Compliance** | SOC 2 | SOX + PCI DSS + FFIEC |
| **SSO** | Cognito Hosted UI | Bank SAML IdP |

---

## Updated Risk Mitigation

| Risk | Likelihood | Impact | Original Mitigation | Integrated Mitigation |
|------|------------|--------|---------------------|----------------------|
| Session hijacking | Low | High | Cognito auth, session binding | **Bank JWT binding + IP validation + jwtSubject match** |
| PCI data leak | Low | Critical | Multi-layer guardrails | (unchanged) |
| SAML assertion replay | Low | High | N/A | **Assertion timestamp validation + one-time use** |
| RS256 key compromise | Very Low | Critical | N/A | **Bank HSM-managed keys + rotation policy** |
| Token refresh failure | Low | Medium | N/A | **Graceful re-authentication flow** |

---

## File Structure (Updated)

```
dispute-schema/
├── mcp-server/
│   ├── package.json
│   ├── tsconfig.json
│   ├── src/
│   │   ├── index.ts
│   │   ├── tools/
│   │   │   ├── file-dispute.ts          # Week 1 (+ auth context)
│   │   │   ├── check-status.ts          # Week 1 (+ auth context)
│   │   │   ├── add-evidence.ts          # Week 2 (+ auth context)
│   │   │   └── compliance-deadline.ts   # Week 2
│   │   ├── guardrails/
│   │   │   └── pci-compliance.ts        # Week 3
│   │   └── auth/                        # NEW
│   │       ├── bank-auth-service.ts     # Week 3-4
│   │       ├── jwt-validator.ts         # Week 3-4
│   │       └── user-context.ts          # Week 1-2
│   └── tests/
│       ├── tools.test.ts
│       ├── pci-guardrails.test.ts
│       └── bank-auth.test.ts            # NEW
│
├── chatbot/
│   ├── services/                        # NEW
│   │   └── BankAuthService.ts           # Week 3-4
│   ├── contexts/
│   │   └── AuthContext.ts               # MODIFIED for Bank JWT
│   ├── dialogue/
│   │   ├── state-manager.ts             # Week 5
│   │   └── slot-filling.ts              # Week 5
│   ├── nlg/
│   │   └── templates/                   # Week 6
│   │       ├── dispute-filed.md
│   │       ├── status-update.md
│   │       └── deadline-explanation.md
│   └── session/
│       └── dynamodb-store.ts            # Week 4 (+ Bank fields)
│
├── src/security/                        # Backend (LangGraph)
│   └── auth.py                          # MODIFIED for RS256 validation
│
├── compliance/                          # EXISTING (reuse)
│   └── reg_e_timelines.ts
│
├── ai-ml/                               # EXISTING (reuse)
│   └── classification/
│       └── dispute_classifier.py
│
└── aws-integration/                     # EXISTING (reuse)
    ├── openapi.yaml
    └── step-functions.asl.json
```

---

## Files Changed Summary

### New Files (5)
1. `mcp-server/src/auth/bank-auth-service.ts` - SAML flow handler
2. `mcp-server/src/auth/jwt-validator.ts` - RS256 validation
3. `mcp-server/src/auth/user-context.ts` - Extract bank user from JWT
4. `chatbot/services/BankAuthService.ts` - Frontend auth service
5. `mcp-server/tests/bank-auth.test.ts` - Auth tests

### Modified Files (4)
1. `chatbot/contexts/AuthContext.ts` - Use Bank JWT instead of Cognito
2. `chatbot/App.tsx` - Bank SSO login button
3. `src/security/auth.py` - RS256 JWT validation (LangGraph)
4. `chatbot/session/dynamodb-store.ts` - Bank user fields

### Unchanged Files
- All MCP tools (receive auth context, no internal changes)
- All chat components (Chat.js, ChatSidebar.js, ProfileMenu.js)
- Chat context (ChatContext.js)
- Thread management (useThreadManager.js)
- LangGraph backend (graph.py, state.py, configuration.py)
- All NLG templates
- All compliance code

---

## Next Phase: Design

### Design Phase Deliverables
1. **API Contract Design** - Bank Auth API endpoints specification
2. **Sequence Diagrams** - Detailed flow for each auth scenario
3. **Error Handling Design** - Auth failure recovery flows
4. **Database Schema** - Final DynamoDB session table design
5. **Security Design Review** - Bank security team approval

### Design Phase Questions to Answer
- [ ] Bank SAML IdP endpoint URLs and certificates
- [ ] JWKS endpoint for RS256 public keys
- [ ] Token lifetime and refresh policy
- [ ] Account access mapping (which accounts can user dispute?)
- [ ] Employee vs Customer authentication differences
- [ ] Session timeout and re-authentication UX

---

*Document Version: 1.0*
*Created: December 2024*
*Status: Planning Complete - Ready for Design Phase*
*Related Documents:*
- `mvp-agentic-chatbot-synthesized-plan.md`
- `Bank_Authentication_System_Integration_Summary.md`
- `agentic_chatbot_implementation_plan.md`
- `banking-transaction-dispute-resolution-system.plan.md`
