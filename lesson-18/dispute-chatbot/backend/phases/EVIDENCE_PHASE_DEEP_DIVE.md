# Evidence Gathering Phase (Phase 2) Implementation Deep Dive

This document captures the implementation details, architectural decisions, and visual explanations for the Evidence Gathering Phase of the Dispute Chatbot.

## 1. Overview

The Evidence Gathering Phase (Phase 2) is responsible for autonomously collecting relevant data from various internal systems (Transaction History, Customer Profiles, Shipping/Logistics) based on the dispute reason code. It uses a **Planner-Executor-Aggregator** pattern to decouple decision-making from execution.

## 2. Data Architecture (Class Diagram)

The system relies on strict Pydantic models to ensure data integrity. The `EvidencePackage` serves as the root container.

```mermaid
classDiagram
    %% Root Container
    class EvidencePackage {
        +String dispute_id
        +String reason_code
        +Float completeness_score
        +String gathered_at
    }

    %% Planning
    class EvidencePlan {
        +String strategy
        +List~EvidenceType~ required_evidence
    }

    %% Base Result Class
    class SpecialistResult {
        +SpecialistType specialist
        +Boolean success
        +String timestamp
        +String error
    }

    %% Concrete Evidence Types
    class TransactionEvidence {
        +List~TransactionInfo~ transactions
        +Integer total_found
    }
    class CustomerEvidence {
        +CustomerSignal signal
    }
    class ShippingEvidence {
        +String tracking_number
        +String status
        +String pod_url
    }

    %% Derived Logic / Validation
    class CE3QualificationResult {
        +Boolean qualified
        +String reason
        +Integer matching_signal_count
    }

    %% Relationships
    EvidencePackage *-- EvidencePlan : contains
    EvidencePackage *-- TransactionEvidence : optional
    EvidencePackage *-- CustomerEvidence : optional
    EvidencePackage *-- ShippingEvidence : optional
    EvidencePackage *-- CE3QualificationResult : optional

    %% Inheritance
    SpecialistResult <|-- TransactionEvidence
    SpecialistResult <|-- CustomerEvidence
    SpecialistResult <|-- ShippingEvidence
```

### Key Components

*   **`EvidencePlan`**: The blueprint. Defines *what* to fetch (e.g., "Strategy: CE 3.0").
*   **`SpecialistResult`**: The polymorphic base class for all agent outputs. Ensures every result has `success` and `error` fields.
*   **`CE3QualificationResult`**: Encapsulates the specific business logic for "Compelling Evidence 3.0" (Visa rule), keeping raw data separate from derived insights.

## 3. Execution Flow (Sequence Diagram)

The orchestration logic in `gather_evidence.py` follows this sequence:

```mermaid
sequenceDiagram
    participant User/Orchestrator
    participant GatherEvidence as gather_evidence()
    participant Planner as EvidencePlanner
    participant TxSpec as TransactionSpecialist
    participant CustSpec as CustomerSpecialist
    participant ShipSpec as ShippingSpecialist
    participant Validator as validate_ce3_eligibility

    User/Orchestrator->>GatherEvidence: Call with task (reason_code="10.4")
    
    %% Step 1: Planning
    GatherEvidence->>Planner: create_plan(reason_code)
    Planner-->>GatherEvidence: Returns EvidencePlan (Strategy: CE_3_0)
    
    %% Step 2: Parallel Execution
    Note over GatherEvidence, ShipSpec: Parallel Execution (asyncio.gather)
    
    par Fetch Transaction History
        GatherEvidence->>TxSpec: get_history(account_id)
        TxSpec-->>GatherEvidence: TransactionEvidence (List of Tx)
    and Fetch Customer Signals
        GatherEvidence->>CustSpec: get_signals(customer_id)
        CustSpec-->>GatherEvidence: CustomerEvidence (IP, Device)
    and Fetch Shipping Info (If needed)
        GatherEvidence->>ShipSpec: get_tracking(tracking_num)
        ShipSpec-->>GatherEvidence: ShippingEvidence
    end

    %% Step 3: Post-Processing Logic
    opt If Strategy == CE_3_0_QUALIFICATION
        GatherEvidence->>Validator: validate(TxEvidence, CustEvidence)
        Note right of Validator: Checks 2+ historic tx<br/>Checks 2+ matching signals
        Validator-->>GatherEvidence: CE3QualificationResult
    end

    %% Step 4: Aggregation
    GatherEvidence->>GatherEvidence: Calculate Completeness Score
    GatherEvidence->>GatherEvidence: Build EvidencePackage

    GatherEvidence-->>User/Orchestrator: Returns EvidencePackage
```

### Flow Highlights

1.  **Planning First:** The system first consults `EvidencePlanner`. This makes it easy to add new strategies (e.g., for different reason codes) without changing the execution engine.
2.  **Async/Parallel Execution:** Calls to `TransactionSpecialist`, `CustomerSpecialist`, etc., happen simultaneously using `asyncio.gather`.
3.  **Post-Processing:** Specific logic (like CE 3.0 validation) is applied *after* data collection but *before* returning the final package.

## 4. Implementation Files

*   **Models:** `lesson-18/dispute-chatbot/backend/phases/evidence_models.py`
*   **Adapters (Mocks):** `lesson-18/dispute-chatbot/backend/adapters/specialists.py`
*   **Orchestrator:** `lesson-18/dispute-chatbot/backend/phases/gather_evidence.py`
*   **Tests:** `lesson-18/dispute-chatbot/tests/test_gather_evidence.py`

## 5. Next Steps

*   Integrate `LLMService` into the Planner for more dynamic, context-aware planning (currently rule-based).
*   Connect the `EvidencePackage` to the Phase 3 (Argument Builder) input.


