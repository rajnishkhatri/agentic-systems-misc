# Critical Review of API Specifications

## Executive Summary
The API specifications are well-structured and comprehensive, covering the core domains of the Dispute Resolution Chatbot (Conversation, Network, Internal Events, and MCP Tools). However, there is significant **schema duplication** between `mcp_tools.yaml` and `common_schemas.yaml`, particularly regarding evidence structures. This creates a risk of schema drift where the internal tool definitions might diverge from the shared domain model.

## detailed Findings

### 1. Schema Duplication & Drift Risk
*   **Issue**: `mcp_tools.yaml` redefines several schemas that conceptually belong in `common_schemas.yaml` or are already partially defined there.
    *   *Examples*: `DeviceFingerprint`, `IPGeolocation`, `EmailVerification`, `TrackingInfo`, `ProofOfDelivery`, `DeliveryPhoto`, `CE3Eligibility`, `EvidenceGap`.
*   **Impact**: If a field changes in the domain model (e.g., adding a `confidence` score to `IPGeolocation`), it must be updated in multiple places.
*   **Recommendation**: Move all evidence-related sub-schemas to `common_schemas.yaml` and reference them in `mcp_tools.yaml`.

### 2. Polymorphism in Network Payloads
*   **Issue**: `network_payloads.yaml` uses a loose structure for `VROLEvidence`. It implicitly relies on the `reason_code` to know which evidence fields (CE 3.0 vs. Shipping) to populate, but strict validation is missing.
*   **Impact**: It is syntactically valid to submit a Fraud 10.4 dispute with Shipping Evidence, which VROL would reject.
*   **Recommendation**: Use OpenAPI `oneOf` with a `discriminator` (based on `reason_code` or a dedicated type field) to enforce that `10.4` requests *must* contain `ce3_evidence` and `13.1` requests *must* contain `shipping_evidence`.

### 3. Event Schema Consistency
*   **Issue**: `internal_events.yaml` defines its own `EvidencePackage` structure (line 249) which might differ slightly from `common_schemas.yaml` or `mcp_tools.yaml`.
*   **Impact**: Inconsistent event payloads can break downstream consumers like the Explainability Layer.
*   **Recommendation**: Standardize `EvidencePackage` in `common_schemas.yaml` and use it strictly in `internal_events.yaml`.

### 4. Conversation Protocol Rigidity
*   **Issue**: The 5-turn flow is documented in comments but not enforced by the schema.
*   **Impact**: The UI or backend might drift from the PRD's 5-turn requirement without schema violations.
*   **Recommendation**: While hard to enforce in YAML, adding a `turn_limit` or `expected_turn_sequence` to the `ProtocolConstants` or `ConversationSession` schema would provide runtime validation hints.

## Improvement Plan

The following improvements were applied on 2025-12-08:

### Step 1: Centralize Domain Models ✅ COMPLETED
**Target**: `lesson-18/dispute-chatbot/design/04_api_specifications/common_schemas.yaml`
*   **Action**: Moved the following definitions from `mcp_tools.yaml` to `common_schemas.yaml`:
    *   `DeviceFingerprint`
    *   `IPGeolocation`
    *   `EmailVerification`
    *   `TrackingInfo`
    *   `ProofOfDelivery`
    *   `DeliveryPhoto`
    *   `EvidenceGap`
    *   `RemediationAction`
*   **Result**: 14 schemas now centralized in `common_schemas.yaml`

### Step 2: Refactor MCP Tools ✅ COMPLETED
**Target**: `lesson-18/dispute-chatbot/design/04_api_specifications/mcp_tools.yaml`
*   **Action**: Replaced inline schema definitions with `$ref: 'common_schemas.yaml#/components/schemas/...'`.
*   **Action**: Updated `EvidencePackage` to reference 12 common schemas.
*   **Result**: 18 schemas (6 local + 12 refs)

### Step 3: Refactor Internal Events ✅ COMPLETED
**Target**: `lesson-18/dispute-chatbot/design/04_api_specifications/internal_events.yaml`
*   **Action**: Updated `EvidencePackage`, `PriorTransaction`, `ShippingEvidence`, `CustomerSignals`, `CE3Qualification`, `ReasonCode` to reference `common_schemas.yaml`.
*   **Result**: 6 schemas now point to common definitions

### Step 4: Enforce Network Type Safety ✅ COMPLETED
**Target**: `lesson-18/dispute-chatbot/design/04_api_specifications/network_payloads.yaml`
*   **Action**: Refactored `VROLEvidence` to use `oneOf` polymorphism with discriminator:
    *   `FraudVROLEvidence` (evidence_type: "fraud_ce3") for 10.4 disputes
    *   `ShippingVROLEvidence` (evidence_type: "shipping_pnr") for 13.1 disputes
*   **Result**: Type-safe evidence validation preventing invalid combinations

### Step 5: Verification ✅ COMPLETED
*   **Action**: Validated all YAML files against OpenAPI 3.0 specification.
*   **Result**: All 4 files pass YAML syntax and OpenAPI structure validation
    *   `common_schemas.yaml`: 14 schemas
    *   `mcp_tools.yaml`: 18 schemas
    *   `internal_events.yaml`: 24 schemas
    *   `network_payloads.yaml`: 19 schemas

