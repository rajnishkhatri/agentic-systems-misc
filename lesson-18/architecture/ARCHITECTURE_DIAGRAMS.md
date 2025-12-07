# Dispute Resolution System - Comprehensive Architecture Diagrams

## 1. Overall System Architecture

```mermaid
graph TB
    subgraph "External Systems"
        BankSAML[Bank SAML IdP<br/>Enterprise SSO]
        BankAuthAPI[Bank Auth API<br/>JWT Validation]
        BankCore[Bank Core Systems<br/>Transaction Data]
    end
    
    subgraph "Client Layer"
        WebPortal[Web Portal<br/>React Frontend]
        MobileApp[Mobile App<br/>iOS/Android]
        API[API Gateway<br/>Rate Limiting & Auth]
    end
    
    subgraph "Application Layer - AWS ECS/Fargate"
        FastAPI[FastAPI Backend<br/>REST API Server]
        
        subgraph "Bank Authentication Layer"
            BankAuth[Bank Auth Service<br/>SAML + JWT]
            AuthMiddleware[Auth Middleware<br/>Permission Validation]
            AuditService[Audit Service<br/>Compliance Logging]
        end
        
        subgraph "LangGraph Workflow Engine"
            WorkflowOrchestrator[Workflow Orchestrator<br/>State Management]
            
            subgraph "AI Agent Network"
                IntakeAgent[Intake Agent<br/>Customer Communication]
                AnalysisAgent[Analysis Agent<br/>Dispute Classification]
                EvidenceAgent[Evidence Agent<br/>Data Collection]
                FraudAgent[Fraud Agent<br/>Pattern Analysis]
                DecisionAgent[Decision Agent<br/>Resolution Logic]
                ComplianceAgent[Compliance Agent<br/>Regulatory Check]
                EscalationAgent[Escalation Agent<br/>Human Handoff]
            end
        end
        
        subgraph "MCP Server Integration"
            MCPClient[MCP Client<br/>Multi-Server Manager]
            BankingMCP[Banking MCP Server<br/>Transaction Analysis]
            FraudMCP[Fraud MCP Server<br/>Pattern Detection]
            PaymentMCP[Payment MCP Server<br/>Network Integration]
            ComplianceMCP[Compliance MCP Server<br/>Regulatory Check]
            GeospatialMCP[Geospatial MCP Server<br/>Location Analysis]
        end
    end
    
    subgraph "AWS Infrastructure Layer"
        subgraph "Compute Services"
            ECS[ECS Fargate<br/>Container Orchestration]
            Lambda[Lambda Functions<br/>MCP Servers]
            StepFunctions[Step Functions<br/>Workflow Orchestration]
        end
        
        subgraph "Data Storage"
            RDS[RDS PostgreSQL<br/>Transaction Database]
            DynamoDB[DynamoDB<br/>Customer Metadata]
            S3[S3 Buckets<br/>Evidence Documents]
            ElastiCache[ElastiCache Redis<br/>Session State]
        end
        
        subgraph "AI/ML Services"
            Bedrock[Bedrock<br/>Foundation Models]
            SageMaker[SageMaker<br/>Custom ML Models]
            Textract[Textract<br/>Document Processing]
            Comprehend[Comprehend<br/>Entity Extraction]
        end
        
        subgraph "Security & Compliance"
            SecretsManager[Secrets Manager<br/>API Keys & Credentials]
            KMS[KMS<br/>Encryption Keys]
            CloudTrail[CloudTrail<br/>API Auditing]
            CloudWatch[CloudWatch<br/>Monitoring & Logs]
        end
    end
    
    subgraph "External Integrations"
        PaymentNetworks[Payment Networks<br/>Visa, Mastercard]
        RegulatoryDB[Regulatory Databases<br/>Compliance Data]
        ThirdPartyAPIs[Third-Party APIs<br/>External Services]
    end
    
    %% External to Client
    BankSAML --> WebPortal
    BankSAML --> MobileApp
    
    %% Client to Application
    WebPortal --> API
    MobileApp --> API
    API --> FastAPI
    
    %% Authentication Flow
    FastAPI --> BankAuth
    BankAuth --> BankSAML
    BankAuth --> BankAuthAPI
    BankAuth --> AuthMiddleware
    AuthMiddleware --> AuditService
    
    %% Workflow Flow
    FastAPI --> WorkflowOrchestrator
    WorkflowOrchestrator --> IntakeAgent
    IntakeAgent --> AnalysisAgent
    AnalysisAgent --> EvidenceAgent
    EvidenceAgent --> FraudAgent
    FraudAgent --> DecisionAgent
    DecisionAgent --> ComplianceAgent
    ComplianceAgent --> EscalationAgent
    
    %% MCP Integration
    WorkflowOrchestrator --> MCPClient
    MCPClient --> BankingMCP
    MCPClient --> FraudMCP
    MCPClient --> PaymentMCP
    MCPClient --> ComplianceMCP
    MCPClient --> GeospatialMCP
    
    %% AWS Services
    FastAPI --> ECS
    MCPClient --> Lambda
    WorkflowOrchestrator --> StepFunctions
    
    %% Data Flow
    FastAPI --> RDS
    FastAPI --> DynamoDB
    FastAPI --> S3
    WorkflowOrchestrator --> ElastiCache
    
    %% AI/ML Services
    IntakeAgent --> Bedrock
    AnalysisAgent --> Bedrock
    EvidenceAgent --> Textract
    FraudAgent --> SageMaker
    DecisionAgent --> Bedrock
    ComplianceAgent --> Comprehend
    
    %% Security
    BankAuth --> SecretsManager
    FastAPI --> KMS
    AuditService --> CloudTrail
    FastAPI --> CloudWatch
    
    %% External Integrations
    BankingMCP --> BankCore
    PaymentMCP --> PaymentNetworks
    ComplianceMCP --> RegulatoryDB
    GeospatialMCP --> ThirdPartyAPIs
```

## 2. Bank Authentication Flow Sequence Diagram

```mermaid
sequenceDiagram
    participant U as User
    participant WP as Web Portal
    participant API as API Gateway
    participant FA as FastAPI
    participant BA as Bank Auth Service
    participant SAML as Bank SAML IdP
    participant BAA as Bank Auth API
    participant WG as LangGraph Workflow
    participant MCP as MCP Servers
    participant AWS as AWS Services
    
    Note over U,AWS: User Authentication Flow
    
    U->>WP: Access Dispute Portal
    WP->>API: Check Authentication
    API->>FA: Forward Request
    FA->>BA: Validate Session
    BA-->>FA: No Valid Session
    
    FA-->>API: 401 Unauthorized
    API-->>WP: Redirect to Login
    WP->>SAML: Redirect to Bank SSO
    
    Note over U,AWS: SAML Authentication
    
    U->>SAML: Enter Bank Credentials
    SAML->>SAML: Validate Credentials
    SAML->>BA: SAML Assertion
    BA->>BAA: Validate SAML Assertion
    BAA-->>BA: User Profile + JWT
    BA->>BA: Generate Session Token
    BA-->>FA: Authentication Success
    FA-->>API: JWT Token
    API-->>WP: Authenticated Session
    
    Note over U,AWS: Dispute Processing Flow
    
    U->>WP: Submit Dispute
    WP->>API: API Request + JWT
    API->>FA: Forward Request
    FA->>BA: Validate JWT Token
    BA->>BAA: Verify Token
    BAA-->>BA: Token Valid
    BA-->>FA: User Profile
    
    FA->>WG: Start Dispute Workflow
    WG->>MCP: Load Tools
    MCP->>AWS: Access Data Services
    AWS-->>MCP: Return Data
    MCP-->>WG: Tool Results
    WG-->>FA: Workflow Complete
    FA-->>API: Response
    API-->>WP: Dispute Status
    WP-->>U: Show Results
```

## 3. LangGraph Workflow State Diagram

```mermaid
stateDiagram-v2
    [*] --> NEW: Dispute Created
    
    NEW --> INTAKE: Start Processing
    INTAKE --> ANALYSIS: Basic Info Collected
    INTAKE --> ESCALATED: Complex Case
    
    ANALYSIS --> EVIDENCE: Standard Dispute
    ANALYSIS --> FRAUD_CHECK: High Risk
    ANALYSIS --> ESCALATED: Unclear Case
    
    EVIDENCE --> FRAUD_CHECK: Evidence Collected
    EVIDENCE --> ESCALATED: Evidence Issues
    
    FRAUD_CHECK --> DECISION: No Fraud Detected
    FRAUD_CHECK --> ESCALATED: Fraud Suspected
    
    DECISION --> COMPLIANCE: Decision Made
    DECISION --> ESCALATED: Complex Decision
    
    COMPLIANCE --> RESOLVED: Compliant
    COMPLIANCE --> ESCALATED: Compliance Issues
    
    ESCALATED --> HUMAN_REVIEW: Human Analyst
    HUMAN_REVIEW --> RESOLVED: Human Decision
    HUMAN_REVIEW --> ESCALATED: Further Review
    
    RESOLVED --> [*]
    
    note right of INTAKE
        Intake Agent:
        - Customer Communication
        - Initial Data Collection
        - Risk Assessment
    end note
    
    note right of ANALYSIS
        Analysis Agent:
        - Dispute Classification
        - Pattern Recognition
        - Risk Scoring
    end note
    
    note right of EVIDENCE
        Evidence Agent:
        - Document Collection
        - Data Validation
        - Evidence Processing
    end note
    
    note right of FRAUD_CHECK
        Fraud Agent:
        - Pattern Analysis
        - Anomaly Detection
        - Risk Assessment
    end note
    
    note right of DECISION
        Decision Agent:
        - Resolution Logic
        - Recommendation Engine
        - Outcome Determination
    end note
    
    note right of COMPLIANCE
        Compliance Agent:
        - Regulatory Check
        - Policy Validation
        - Compliance Verification
    end note
```

## 4. MCP Server Integration Architecture

```mermaid
graph TB
    subgraph "LangGraph Workflow"
        WG[Workflow Orchestrator]
        IA[Intake Agent]
        AA[Analysis Agent]
        EA[Evidence Agent]
        FA[Fraud Agent]
        DA[Decision Agent]
        CA[Compliance Agent]
    end
    
    subgraph "MCP Client Layer"
        MCPClient[MCP Client Manager<br/>Multi-Server Connection]
        ToolLoader[Tool Loader<br/>Dynamic Tool Registration]
        AuthManager[Auth Manager<br/>Bank Auth Headers]
    end
    
    subgraph "MCP Server Layer - AWS Lambda"
        BankingMCP[Banking MCP Server<br/>Lambda Function]
        FraudMCP[Fraud MCP Server<br/>Lambda Function]
        PaymentMCP[Payment MCP Server<br/>Lambda Function]
        ComplianceMCP[Compliance MCP Server<br/>Lambda Function]
        GeospatialMCP[Geospatial MCP Server<br/>Lambda Function]
    end
    
    subgraph "Banking MCP Tools"
        GetTxHistory[get_transaction_history]
        GetCustomerProfile[get_customer_profile]
        AnalyzeTx[analyze_transaction]
        GetDisputeHistory[get_dispute_history]
        ValidateAccount[validate_account]
    end
    
    subgraph "Fraud MCP Tools"
        DetectPatterns[detect_fraud_patterns]
        AnalyzeBehavior[analyze_behavior]
        RiskAssessment[risk_assessment]
        PatternMatching[pattern_matching]
    end
    
    subgraph "Payment MCP Tools"
        ValidatePayment[validate_payment]
        ProcessRefund[process_refund]
        CheckNetwork[check_payment_network]
        GetProcessorData[get_processor_data]
    end
    
    subgraph "Compliance MCP Tools"
        CheckRegulations[check_regulations]
        ValidateCompliance[validate_compliance]
        GetPolicyData[get_policy_data]
        AuditTrail[audit_trail]
    end
    
    subgraph "AWS Data Services"
        RDS[(RDS PostgreSQL<br/>Transaction Data)]
        DynamoDB[(DynamoDB<br/>Customer Data)]
        S3[(S3 Buckets<br/>Documents)]
        SageMaker[SageMaker<br/>ML Models]
        Bedrock[Bedrock<br/>AI Models]
    end
    
    %% Workflow to MCP Client
    WG --> MCPClient
    IA --> MCPClient
    AA --> MCPClient
    EA --> MCPClient
    FA --> MCPClient
    DA --> MCPClient
    CA --> MCPClient
    
    %% MCP Client to Servers
    MCPClient --> BankingMCP
    MCPClient --> FraudMCP
    MCPClient --> PaymentMCP
    MCPClient --> ComplianceMCP
    MCPClient --> GeospatialMCP
    
    %% Tool Registration
    ToolLoader --> BankingMCP
    ToolLoader --> FraudMCP
    ToolLoader --> PaymentMCP
    ToolLoader --> ComplianceMCP
    ToolLoader --> GeospatialMCP
    
    %% Auth Integration
    AuthManager --> BankingMCP
    AuthManager --> FraudMCP
    AuthManager --> PaymentMCP
    AuthManager --> ComplianceMCP
    AuthManager --> GeospatialMCP
    
    %% Banking MCP Tools
    BankingMCP --> GetTxHistory
    BankingMCP --> GetCustomerProfile
    BankingMCP --> AnalyzeTx
    BankingMCP --> GetDisputeHistory
    BankingMCP --> ValidateAccount
    
    %% Fraud MCP Tools
    FraudMCP --> DetectPatterns
    FraudMCP --> AnalyzeBehavior
    FraudMCP --> RiskAssessment
    FraudMCP --> PatternMatching
    
    %% Payment MCP Tools
    PaymentMCP --> ValidatePayment
    PaymentMCP --> ProcessRefund
    PaymentMCP --> CheckNetwork
    PaymentMCP --> GetProcessorData
    
    %% Compliance MCP Tools
    ComplianceMCP --> CheckRegulations
    ComplianceMCP --> ValidateCompliance
    ComplianceMCP --> GetPolicyData
    ComplianceMCP --> AuditTrail
    
    %% Data Connections
    BankingMCP --> RDS
    BankingMCP --> DynamoDB
    FraudMCP --> SageMaker
    FraudMCP --> Bedrock
    PaymentMCP --> RDS
    ComplianceMCP --> S3
    GeospatialMCP --> Bedrock
```

## 5. AWS Infrastructure Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        Web[Web Portal]
        Mobile[Mobile App]
        API[API Gateway]
    end
    
    subgraph "Application Layer - ECS Fargate"
        FastAPI[FastAPI Application]
        LangGraph[LangGraph Workflow Engine]
        Agents[AI Agent Network]
    end
    
    subgraph "MCP Server Layer - Lambda"
        BankingLambda[Banking MCP Lambda]
        FraudLambda[Fraud MCP Lambda]
        PaymentLambda[Payment MCP Lambda]
        ComplianceLambda[Compliance MCP Lambda]
        GeospatialLambda[Geospatial MCP Lambda]
    end
    
    subgraph "Data Layer"
        RDS[(RDS PostgreSQL<br/>Transaction Database)]
        DynamoDB[(DynamoDB<br/>Customer Metadata)]
        S3[(S3 Buckets<br/>Evidence Storage)]
        ElastiCache[(ElastiCache Redis<br/>Session State)]
        DocumentDB[(DocumentDB<br/>Fraud Patterns)]
    end
    
    subgraph "AI/ML Services"
        Bedrock[Bedrock<br/>Foundation Models]
        SageMaker[SageMaker<br/>Custom Models]
        Textract[Textract<br/>Document Processing]
        Comprehend[Comprehend<br/>Entity Extraction]
        OpenSearch[OpenSearch<br/>Vector Search]
    end
    
    subgraph "Security & Compliance"
        SecretsManager[Secrets Manager<br/>Credentials]
        KMS[KMS<br/>Encryption]
        CloudTrail[CloudTrail<br/>Audit Logs]
        CloudWatch[CloudWatch<br/>Monitoring]
        XRay[X-Ray<br/>Tracing]
    end
    
    subgraph "External Integrations"
        BankSAML[Bank SAML IdP]
        BankAuthAPI[Bank Auth API]
        PaymentNetworks[Payment Networks]
        RegulatoryDB[Regulatory Databases]
    end
    
    %% Client to Application
    Web --> API
    Mobile --> API
    API --> FastAPI
    
    %% Application Layer
    FastAPI --> LangGraph
    LangGraph --> Agents
    
    %% MCP Integration
    LangGraph --> BankingLambda
    LangGraph --> FraudLambda
    LangGraph --> PaymentLambda
    LangGraph --> ComplianceLambda
    LangGraph --> GeospatialLambda
    
    %% Data Connections
    FastAPI --> RDS
    FastAPI --> DynamoDB
    FastAPI --> S3
    LangGraph --> ElastiCache
    
    BankingLambda --> RDS
    BankingLambda --> DynamoDB
    FraudLambda --> DocumentDB
    FraudLambda --> SageMaker
    PaymentLambda --> RDS
    ComplianceLambda --> S3
    GeospatialLambda --> OpenSearch
    
    %% AI/ML Services
    Agents --> Bedrock
    Agents --> Textract
    Agents --> Comprehend
    FraudLambda --> SageMaker
    GeospatialLambda --> Bedrock
    
    %% Security
    FastAPI --> SecretsManager
    FastAPI --> KMS
    FastAPI --> CloudTrail
    FastAPI --> CloudWatch
    LangGraph --> XRay
    
    %% External Auth
    FastAPI --> BankSAML
    FastAPI --> BankAuthAPI
    
    %% External Data
    BankingLambda --> PaymentNetworks
    ComplianceLambda --> RegulatoryDB
```

## 6. Bank Authentication Integration Flow

```mermaid
flowchart TD
    Start([User Access]) --> CheckAuth{Authenticated?}
    
    CheckAuth -->|No| BankSSO[Bank SAML SSO]
    CheckAuth -->|Yes| ValidateToken[Validate JWT Token]
    
    BankSSO --> SAMLFlow[SAML Authentication Flow]
    SAMLFlow --> SAMLAssertion[SAML Assertion Received]
    SAMLAssertion --> ValidateSAML[Validate SAML with Bank Auth API]
    
    ValidateSAML -->|Valid| GenerateJWT[Generate Bank JWT Token]
    ValidateSAML -->|Invalid| AuthError[Authentication Error]
    
    GenerateJWT --> StoreSession[Store Session in Redis]
    StoreSession --> SetUserContext[Set User Context]
    
    ValidateToken -->|Valid| SetUserContext
    ValidateToken -->|Invalid| RefreshToken[Try Token Refresh]
    RefreshToken -->|Success| SetUserContext
    RefreshToken -->|Failed| BankSSO
    
    SetUserContext --> CheckPermissions[Check User Permissions]
    CheckPermissions -->|Authorized| ProcessRequest[Process API Request]
    CheckPermissions -->|Unauthorized| PermissionError[Permission Denied]
    
    ProcessRequest --> LogAction[Log User Action]
    LogAction --> ExecuteWorkflow[Execute LangGraph Workflow]
    
    ExecuteWorkflow --> MCPAuth[Add Bank Auth Headers to MCP]
    MCPAuth --> CallMCPServers[Call MCP Servers]
    CallMCPServers --> ProcessResponse[Process Response]
    ProcessResponse --> AuditLog[Audit Log Entry]
    AuditLog --> ReturnResponse[Return Response to Client]
    
    AuthError --> End([End])
    PermissionError --> End
    ReturnResponse --> End
    
    %% Styling
    classDef authNode fill:#e1f5fe
    classDef errorNode fill:#ffebee
    classDef processNode fill:#f3e5f5
    classDef dataNode fill:#e8f5e8
    
    class BankSSO,SAMLFlow,SAMLAssertion,ValidateSAML,GenerateJWT,ValidateToken,RefreshToken,CheckPermissions authNode
    class AuthError,PermissionError errorNode
    class ProcessRequest,ExecuteWorkflow,CallMCPServers,ProcessResponse processNode
    class StoreSession,SetUserContext,LogAction,AuditLog dataNode
```

## 7. LangGraph Workflow Detailed Flow

```mermaid
graph TD
    Start([Dispute Created]) --> IntakeAgent[Intake Agent]
    
    IntakeAgent --> IntakeProcess[Process Customer Communication]
    IntakeProcess --> IntakeDecision{Basic Info Complete?}
    
    IntakeDecision -->|No| IntakeAgent
    IntakeDecision -->|Yes| IntakeRisk{Risk Score > 0.8?}
    
    IntakeRisk -->|Yes| FraudAgent[Fraud Agent]
    IntakeRisk -->|No| AnalysisAgent[Analysis Agent]
    
    AnalysisAgent --> AnalysisProcess[Classify Dispute Type]
    AnalysisProcess --> AnalysisDecision{Dispute Type?}
    
    AnalysisDecision -->|Fraud/Chargeback| EvidenceAgent[Evidence Agent]
    AnalysisDecision -->|Other| FraudAgent
    
    EvidenceAgent --> EvidenceProcess[Collect Evidence]
    EvidenceProcess --> EvidenceDecision{Evidence Complete?}
    
    EvidenceDecision -->|No| EvidenceAgent
    EvidenceDecision -->|Yes| FraudAgent
    
    FraudAgent --> FraudProcess[Detect Fraud Patterns]
    FraudProcess --> FraudDecision{Fraud Detected?}
    
    FraudDecision -->|Yes| EscalationAgent[Escalation Agent]
    FraudDecision -->|No| DecisionAgent[Decision Agent]
    
    DecisionAgent --> DecisionProcess[Make Resolution Decision]
    DecisionProcess --> DecisionResult{Decision Made?}
    
    DecisionResult -->|Escalate| EscalationAgent
    DecisionResult -->|Resolve| ComplianceAgent[Compliance Agent]
    
    ComplianceAgent --> ComplianceProcess[Check Regulatory Compliance]
    ComplianceProcess --> ComplianceDecision{Compliant?}
    
    ComplianceDecision -->|No| EscalationAgent
    ComplianceDecision -->|Yes| Resolved[Dispute Resolved]
    
    EscalationAgent --> HumanReview[Human Analyst Review]
    HumanReview --> HumanDecision{Human Decision}
    
    HumanDecision -->|Resolve| Resolved
    HumanDecision -->|Further Review| EscalationAgent
    
    Resolved --> End([End])
    
    %% MCP Tool Calls
    IntakeAgent -.-> MCPTools1[MCP: get_customer_profile]
    AnalysisAgent -.-> MCPTools2[MCP: analyze_transaction]
    EvidenceAgent -.-> MCPTools3[MCP: get_transaction_history]
    FraudAgent -.-> MCPTools4[MCP: detect_fraud_patterns]
    DecisionAgent -.-> MCPTools5[MCP: get_dispute_history]
    ComplianceAgent -.-> MCPTools6[MCP: check_regulations]
    
    %% State Management
    IntakeAgent -.-> RedisState[Redis State Management]
    AnalysisAgent -.-> RedisState
    EvidenceAgent -.-> RedisState
    FraudAgent -.-> RedisState
    DecisionAgent -.-> RedisState
    ComplianceAgent -.-> RedisState
    EscalationAgent -.-> RedisState
```

## 8. Data Flow Architecture

```mermaid
graph LR
    subgraph "Input Sources"
        Customer[Customer Input]
        BankData[Bank Transaction Data]
        ExternalAPIs[External APIs]
        Documents[Evidence Documents]
    end
    
    subgraph "Processing Layer"
        FastAPI[FastAPI Backend]
        LangGraph[LangGraph Workflow]
        MCPClient[MCP Client]
        Agents[AI Agents]
    end
    
    subgraph "MCP Servers"
        BankingMCP[Banking MCP]
        FraudMCP[Fraud MCP]
        PaymentMCP[Payment MCP]
        ComplianceMCP[Compliance MCP]
    end
    
    subgraph "AWS Data Services"
        RDS[(RDS PostgreSQL)]
        DynamoDB[(DynamoDB)]
        S3[(S3 Storage)]
        ElastiCache[(Redis Cache)]
    end
    
    subgraph "AI/ML Services"
        Bedrock[Bedrock AI]
        SageMaker[SageMaker ML]
        Textract[Textract OCR]
        Comprehend[Comprehend NLP]
    end
    
    subgraph "Output Destinations"
        CustomerResponse[Customer Response]
        AuditLogs[Audit Logs]
        ComplianceReports[Compliance Reports]
        EscalationQueue[Human Escalation]
    end
    
    %% Input Flow
    Customer --> FastAPI
    BankData --> BankingMCP
    ExternalAPIs --> PaymentMCP
    Documents --> S3
    
    %% Processing Flow
    FastAPI --> LangGraph
    LangGraph --> MCPClient
    MCPClient --> BankingMCP
    MCPClient --> FraudMCP
    MCPClient --> PaymentMCP
    MCPClient --> ComplianceMCP
    
    %% Data Storage
    FastAPI --> RDS
    FastAPI --> DynamoDB
    FastAPI --> ElastiCache
    BankingMCP --> RDS
    FraudMCP --> DynamoDB
    ComplianceMCP --> S3
    
    %% AI Processing
    LangGraph --> Bedrock
    FraudMCP --> SageMaker
    Documents --> Textract
    LangGraph --> Comprehend
    
    %% Output Flow
    LangGraph --> CustomerResponse
    FastAPI --> AuditLogs
    ComplianceMCP --> ComplianceReports
    LangGraph --> EscalationQueue
```

## 9. Security and Compliance Architecture

```mermaid
graph TB
    subgraph "Authentication Layer"
        BankSAML[Bank SAML IdP]
        BankAuthAPI[Bank Auth API]
        JWTValidator[JWT Token Validator]
        SessionManager[Session Manager]
    end
    
    subgraph "Authorization Layer"
        RoleManager[Role Manager]
        PermissionEngine[Permission Engine]
        AccessController[Access Controller]
    end
    
    subgraph "Data Protection"
        Encryption[Data Encryption]
        KMS[AWS KMS]
        SecretsManager[Secrets Manager]
        DataMasking[Data Masking]
    end
    
    subgraph "Audit and Compliance"
        AuditLogger[Audit Logger]
        CloudTrail[CloudTrail]
        ComplianceEngine[Compliance Engine]
        ReportGenerator[Report Generator]
    end
    
    subgraph "Monitoring and Alerting"
        CloudWatch[CloudWatch]
        XRay[X-Ray Tracing]
        SecurityHub[Security Hub]
        AlertManager[Alert Manager]
    end
    
    subgraph "Regulatory Compliance"
        SOX[SOX Compliance]
        PCIDSS[PCI DSS]
        FFIEC[FFIEC Guidelines]
        GDPR[GDPR Compliance]
    end
    
    %% Authentication Flow
    BankSAML --> BankAuthAPI
    BankAuthAPI --> JWTValidator
    JWTValidator --> SessionManager
    
    %% Authorization Flow
    SessionManager --> RoleManager
    RoleManager --> PermissionEngine
    PermissionEngine --> AccessController
    
    %% Data Protection
    AccessController --> Encryption
    Encryption --> KMS
    KMS --> SecretsManager
    SecretsManager --> DataMasking
    
    %% Audit Flow
    AccessController --> AuditLogger
    AuditLogger --> CloudTrail
    CloudTrail --> ComplianceEngine
    ComplianceEngine --> ReportGenerator
    
    %% Monitoring
    AuditLogger --> CloudWatch
    CloudWatch --> XRay
    XRay --> SecurityHub
    SecurityHub --> AlertManager
    
    %% Compliance
    ComplianceEngine --> SOX
    ComplianceEngine --> PCIDSS
    ComplianceEngine --> FFIEC
    ComplianceEngine --> GDPR
```

## 10. Deployment Architecture

```mermaid
graph TB
    subgraph "Development Environment"
        DevECS[ECS Dev Cluster]
        DevLambda[Lambda Dev Functions]
        DevRDS[Dev RDS Instance]
        DevRedis[Dev ElastiCache]
    end
    
    subgraph "Staging Environment"
        StagingECS[ECS Staging Cluster]
        StagingLambda[Lambda Staging Functions]
        StagingRDS[Staging RDS Instance]
        StagingRedis[Staging ElastiCache]
    end
    
    subgraph "Production Environment"
        ProdECS[ECS Production Cluster]
        ProdLambda[Lambda Production Functions]
        ProdRDS[Production RDS Cluster]
        ProdRedis[Production ElastiCache]
    end
    
    subgraph "CI/CD Pipeline"
        GitHub[GitHub Repository]
        GitHubActions[GitHub Actions]
        DockerHub[Docker Hub]
        ECR[Amazon ECR]
    end
    
    subgraph "Infrastructure as Code"
        CDK[AWS CDK]
        Terraform[Terraform]
        CloudFormation[CloudFormation]
    end
    
    subgraph "Monitoring and Observability"
        CloudWatch[CloudWatch]
        XRay[X-Ray]
        Prometheus[Prometheus]
        Grafana[Grafana]
    end
    
    %% CI/CD Flow
    GitHub --> GitHubActions
    GitHubActions --> DockerHub
    DockerActions --> ECR
    
    %% Infrastructure
    CDK --> DevECS
    CDK --> StagingECS
    CDK --> ProdECS
    
    Terraform --> DevLambda
    Terraform --> StagingLambda
    Terraform --> ProdLambda
    
    %% Deployment
    ECR --> DevECS
    ECR --> StagingECS
    ECR --> ProdECS
    
    %% Monitoring
    DevECS --> CloudWatch
    StagingECS --> CloudWatch
    ProdECS --> CloudWatch
    
    CloudWatch --> XRay
    XRay --> Prometheus
    Prometheus --> Grafana
```

This comprehensive architecture documentation covers all aspects of the dispute resolution system with bank authentication integration, including:

1. **Overall System Architecture** - Complete system overview
2. **Bank Authentication Flow** - Detailed SAML SSO and JWT validation
3. **LangGraph Workflow** - State management and agent coordination
4. **MCP Server Integration** - Tool integration architecture
5. **AWS Infrastructure** - Cloud services and data layer
6. **Bank Auth Integration** - Authentication and authorization flow
7. **LangGraph Workflow Details** - Step-by-step workflow processing
8. **Data Flow Architecture** - Data movement and processing
9. **Security and Compliance** - Banking-grade security implementation
10. **Deployment Architecture** - CI/CD and infrastructure management

Each diagram provides a different perspective on the system, ensuring comprehensive coverage of all architectural aspects while maintaining clarity and detail.





