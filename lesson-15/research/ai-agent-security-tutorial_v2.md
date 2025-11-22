# Building Secure AI Agent Systems in Banking: A Hands-On Tutorial for AI Architects

## 🎯 What You'll Learn Today

As an AI architect designing autonomous agent systems for financial services, you'll master the seven essential security layers that protect billions in transactions. This tutorial transforms complex security concepts into practical implementation steps with visual diagrams and real code examples.

**By the end of this tutorial, you'll know how to:**
- Design cryptographic identity systems for AI agents
- Implement zero-trust architectures with mutual authentication
- Build runtime monitoring for autonomous decision-making systems
- Create audit trails that satisfy financial regulators
- Deploy production-ready security patterns used by JPMorgan Chase and Goldman Sachs

---

## 📚 Module 1: Understanding the Challenge - Why Banking AI Agents Need Special Security

### The Stakes Are Different Here

Imagine your AI agent makes a mistake. In most industries, you might lose some efficiency. In banking:
- A fraud detection agent missing patterns = millions in losses
- A compliance agent making errors = regulatory fines and license risks
- A compromised payment agent = direct financial theft

### Visual: The Seven-Layer Security Model

```
┌─────────────────────────────────────────────────┐
│         Your Banking AI Agent System            │
├─────────────────────────────────────────────────┤
│  Layer 7: Compliance Validation                 │
│  ├── Regulatory reporting                       │
│  └── Audit evidence                            │
├─────────────────────────────────────────────────┤
│  Layer 6: Secrets Rotation                      │
│  ├── Automated key management                   │
│  └── Zero-downtime updates                     │
├─────────────────────────────────────────────────┤
│  Layer 5: Audit Logging                         │
│  ├── Immutable records                          │
│  └── Transaction tracing                       │
├─────────────────────────────────────────────────┤
│  Layer 4: Runtime Monitoring                    │
│  ├── Behavioral analysis                        │
│  └── Anomaly detection                         │
├─────────────────────────────────────────────────┤
│  Layer 3: Network Isolation                     │
│  ├── Microsegmentation                          │
│  └── Zero-trust boundaries                     │
├─────────────────────────────────────────────────┤
│  Layer 2: Authorization Scoping                 │
│  ├── Fine-grained permissions                   │
│  └── Time-bound access                         │
├─────────────────────────────────────────────────┤
│  Layer 1: Identity Verification                 │
│  ├── Cryptographic proof                        │
│  └── Multi-authority validation                │
└─────────────────────────────────────────────────┘
```

### Try This Exercise

**Question**: Your fraud detection agent processes 100,000 transactions per second. Which security layer would be most impacted by performance requirements?

**Think about it**: Runtime monitoring (Layer 4) needs to analyze behavior without slowing transactions. This is why banks use lightweight proxies and asynchronous analysis.

---

## 🔐 Module 2: Cryptographic Identity - Your Agent's Digital DNA

### The Concept: Know Your Agent (Like Know Your Customer)

Just as banks must verify customer identities, we need "Know Your Agent" protocols. The AgentFacts framework introduces this concept using Decentralized Identifiers.

### Visual: Agent Identity Architecture

```
┌────────────────────────────────────────┐
│         AI Agent Identity               │
├────────────────────────────────────────┤
│  Decentralized Identifier (DID)        │
│  did:bank:agent:fraud-detector-001     │
├────────────────────────────────────────┤
│  Five Certificate Types:                │
│  1. Transport Certificate               │
│     └── For secure channel setup       │
│  2. Digital Signature Certificate       │
│     └── For request signing            │
│  3. OAuth Access Token                  │
│     └── For API authorization          │
│  4. Callback Certificate                │
│     └── For async responses            │
│  5. Encryption Certificate              │
│     └── For sensitive data protection  │
└────────────────────────────────────────┘
```

### Implementation Pseudocode

```python
# Agent Identity Creation Pattern
class BankingAgent:
    def __init__(self, agent_name):
        self.identity = self.create_identity(agent_name)
    
    def create_identity(self, name):
        """
        Creates cryptographic identity with multi-layer certificates
        """
        identity = {
            'did': f'did:bank:agent:{name}',
            'certificates': {
                'transport': generate_x509_cert(purpose='mtls'),
                'signature': generate_signing_cert(),
                'oauth': generate_oauth_credentials(),
                'callback': generate_callback_cert(),
                'encryption': generate_encryption_cert()
            },
            'metadata': {
                'capabilities': [],
                'compliance_level': 'platinum',
                'issuer': 'bank-ca-authority',
                'created': timestamp(),
                'expires': timestamp() + days(90)
            }
        }
        return identity
    
    def sign_request(self, request_data):
        """
        Every action must be cryptographically signed
        """
        signature = crypto.sign(
            data=request_data,
            key=self.identity['certificates']['signature']['private_key']
        )
        return {
            'request': request_data,
            'signature': signature,
            'agent_did': self.identity['did']
        }
```

### Real-World Example: JPMorgan Chase Implementation

JPMorgan's system requires each agent to present five different certificates for different purposes. This isn't redundancy - it's separation of concerns:

- **Transport certificates** expire quickly (24 hours) for network security
- **Signature certificates** last longer (30 days) for operational continuity
- **Encryption certificates** rotate quarterly for data protection

---

## 🔒 Module 3: Mutual TLS - Building Trust Between Agents

### The Concept Explained

Mutual TLS (mTLS) means both parties verify each other's identity before communicating. Think of it like a secure handshake where both people show ID cards.

### Visual: How mTLS Works

```
Agent A                     Agent B
   │                           │
   ├──────Hello────────────────►
   │   (with Agent A cert)     │
   │                           │
   ◄──────Hello─────────────────┤
   │   (with Agent B cert)     │
   │                           │
   ├──Verify B's cert──────────►
   ◄──Verify A's cert──────────┤
   │                           │
   ├═══Encrypted Channel═══════►
   ◄═══Encrypted Channel═══════┤
```

### Implementation with Service Mesh

```yaml
# Istio Configuration for Banking Agents
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: banking-agent-mtls
  namespace: ai-agents-prod
spec:
  mtls:
    mode: STRICT  # No plaintext allowed
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: agent-tls-config
data:
  rotation_schedule: |
    high_security_ops: 30d
    standard_ops: 90d
    payment_keys: 180d
  cipher_suites: |
    - TLS_AES_128_GCM_SHA256  # Optimized for performance
    - TLS_AES_256_GCM_SHA384  # Maximum security
```

### Performance Consideration Pattern

```python
class OptimizedTLSConnection:
    """
    Pattern for reducing mTLS overhead in high-frequency operations
    """
    def __init__(self):
        self.connection_pool = {}
        self.session_cache = {}
    
    def get_connection(self, target_agent):
        # Reuse existing connections when possible
        if target_agent in self.connection_pool:
            conn = self.connection_pool[target_agent]
            if conn.is_alive():
                return conn
        
        # Create new connection with optimizations
        conn = self.create_optimized_connection(target_agent)
        self.connection_pool[target_agent] = conn
        return conn
    
    def create_optimized_connection(self, target):
        return Connection(
            target=target,
            tls_version='1.3',  # Faster handshake
            session_resumption=True,  # Skip full handshake
            connection_pooling=True,
            keepalive_timeout=300  # 5 minutes
        )
```

---

## 🎛️ Module 4: Fine-Grained Authorization with OAuth 2.0

### Understanding Scopes for Financial Operations

Instead of giving agents all-or-nothing access, we create specific permission scopes:

### Visual: Authorization Scope Hierarchy

```
┌─────────────────────────────────────────┐
│          Agent Permissions              │
├─────────────────────────────────────────┤
│  Base Scopes:                          │
│  ├── transactions:read                 │
│  ├── transactions:analyze              │
│  └── alerts:create                     │
├─────────────────────────────────────────┤
│  Elevated Scopes (require approval):   │
│  ├── transactions:modify               │
│  ├── payments:execute                  │
│  └── customer:sensitive_data           │
├─────────────────────────────────────────┤
│  Time-Bound Scopes:                    │
│  ├── batch:process (expires: 1hr)      │
│  └── audit:temporary (expires: 24hr)   │
└─────────────────────────────────────────┘
```

### Implementation Pattern

```python
class AgentAuthorizationManager:
    """
    Manages OAuth 2.0 scopes for banking agents
    """
    
    def request_token(self, agent_id, requested_scopes):
        # Validate agent credentials
        if not self.validate_agent(agent_id):
            raise UnauthorizedError()
        
        # Apply principle of least privilege
        approved_scopes = self.evaluate_scopes(
            agent_id, 
            requested_scopes
        )
        
        # Generate time-bound token
        token = {
            'access_token': generate_jwt({
                'sub': agent_id,
                'scopes': approved_scopes,
                'exp': time() + 3600,  # 1 hour
                'iat': time(),
                'iss': 'bank-auth-server'
            }),
            'token_type': 'Bearer',
            'expires_in': 3600,
            'scope': ' '.join(approved_scopes)
        }
        
        # Bind token to mTLS certificate (sender-constrained)
        token['cnf'] = {
            'x5t#S256': agent_certificate_thumbprint
        }
        
        return token
    
    def evaluate_scopes(self, agent_id, requested):
        """
        Risk-based scope evaluation
        """
        agent_profile = self.get_agent_profile(agent_id)
        
        approved = []
        for scope in requested:
            risk_level = self.calculate_risk(scope)
            
            if risk_level == 'LOW':
                approved.append(scope)
            elif risk_level == 'MEDIUM':
                if agent_profile['trust_score'] > 0.8:
                    approved.append(scope)
                    self.log_elevated_permission(agent_id, scope)
            elif risk_level == 'HIGH':
                # Requires human approval
                if self.has_human_approval(agent_id, scope):
                    approved.append(scope)
                    self.alert_security_team(agent_id, scope)
        
        return approved
```

---

## 🛡️ Module 5: Runtime Behavioral Monitoring

### The Challenge: Detecting Compromised Agents

An agent might have valid credentials but exhibit malicious behavior. We need runtime detection.

### Visual: Behavioral Baseline System

```
Normal Behavior Profile          Current Behavior
┌────────────────────┐           ┌────────────────────┐
│ API Calls: 100/min │           │ API Calls: 850/min │ ← ALERT!
│ Data Read: 1GB/hr  │           │ Data Read: 1GB/min │ ← ALERT!
│ Patterns: Sequential│           │ Patterns: Random   │ ← WARNING
│ Timing: Business hrs│           │ Timing: 3 AM       │ ← WARNING
└────────────────────┘           └────────────────────┘
                    ↓
         Anomaly Score: 0.92 (Threshold: 0.7)
                    ↓
            SECURITY RESPONSE TRIGGERED
```

### Implementation with Falco

```yaml
# Falco Rules for AI Agent Monitoring
- rule: Agent Excessive API Calls
  desc: Detect when agent exceeds normal API call rate
  condition: >
    container and 
    container.name contains "ai-agent" and
    evt.type = syscall and
    evt.dir = > and
    count(evt.time) > 1000 in last 60s
  output: >
    High API call rate detected 
    (agent=%container.name rate=%evt.count/min)
  priority: WARNING

- rule: Agent Accessing Unauthorized Data
  desc: Detect agent accessing data outside scope
  condition: >
    container and
    container.name contains "ai-agent" and
    (fd.name contains "/sensitive/" or 
     fd.name contains "/pii/") and
    not agent_has_permission
  output: >
    Unauthorized data access attempt
    (agent=%container.name file=%fd.name)
  priority: CRITICAL
```

### Behavioral Analysis Pattern

```python
class AgentBehaviorMonitor:
    """
    Real-time behavioral analysis for banking agents
    """
    
    def __init__(self):
        self.baselines = {}
        self.ml_model = load_model('agent_anomaly_detector.pkl')
    
    def analyze_behavior(self, agent_id, action):
        # Extract features
        features = self.extract_features(action)
        
        # Compare to baseline
        baseline = self.baselines.get(agent_id)
        if not baseline:
            self.create_baseline(agent_id)
            return  # Learning phase
        
        # Calculate anomaly score
        anomaly_score = self.ml_model.predict_proba([features])[0][1]
        
        # Risk-based response
        if anomaly_score > 0.9:
            self.immediate_containment(agent_id)
            self.alert_soc_team(agent_id, action, anomaly_score)
        elif anomaly_score > 0.7:
            self.rate_limit_agent(agent_id)
            self.enhanced_monitoring(agent_id)
        elif anomaly_score > 0.5:
            self.log_suspicious_activity(agent_id, action)
    
    def extract_features(self, action):
        return [
            action['api_calls_per_minute'],
            action['data_volume_mb'],
            action['unique_endpoints_accessed'],
            action['time_of_day_deviation'],
            action['geographic_anomaly_score'],
            action['pattern_similarity_score']
        ]
    
    def immediate_containment(self, agent_id):
        """
        Emergency response for high-risk behavior
        """
        # Revoke all tokens
        self.revoke_agent_tokens(agent_id)
        
        # Isolate network
        self.apply_network_policy(agent_id, 'DENY_ALL')
        
        # Preserve evidence
        self.capture_forensic_snapshot(agent_id)
        
        # Initiate incident response
        incident_id = self.create_incident(agent_id)
        return incident_id
```

---

## 📝 Module 6: Audit Logging for Regulatory Compliance

### The Requirement: Complete Transaction Attribution

Financial regulators require you to prove:
- Who (which agent) did what
- When it happened
- Why it was authorized
- What data was accessed

### Visual: Immutable Audit Trail Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Agent Action  │────►│  Audit Logger   │────►│ Immutable Store │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         │                       │                        │
         │                       ├── Hash Chain          │
         │                       ├── Timestamp           ├── Blockchain
         │                       ├── Digital Signature   ├── WORM Storage
         │                       └── Encryption          └── SIEM Archive
         │
    ┌────▼────────────────────────────────────┐
    │  Structured Audit Entry:                │
    │  {                                      │
    │    "agent_id": "did:bank:agent:001",   │
    │    "action": "fraud_check",            │
    │    "timestamp": "2024-01-15T10:23:45Z", │
    │    "transaction_id": "tx-789456",      │
    │    "data_accessed": ["account_history"], │
    │    "decision": "flagged_suspicious",    │
    │    "confidence": 0.92,                 │
    │    "hash_prev": "sha256:abc...",        │
    │    "signature": "sig:xyz..."            │
    │  }                                      │
    └──────────────────────────────────────┘
```

### Implementation Pattern

```python
class ImmutableAuditLogger:
    """
    Creates tamper-proof audit trails for regulatory compliance
    """
    
    def __init__(self):
        self.hash_chain = []
        self.storage = WORMStorage()  # Write-Once-Read-Many
        
    def log_agent_action(self, agent_id, action):
        # Create structured entry
        entry = {
            'id': generate_uuid(),
            'agent_id': agent_id,
            'timestamp': datetime.utcnow().isoformat(),
            'action': action['type'],
            'details': action['details'],
            'transaction_id': action.get('transaction_id'),
            'data_accessed': action.get('data_accessed', []),
            'decision': action.get('decision'),
            'confidence': action.get('confidence')
        }
        
        # Add hash chain for tamper detection
        if self.hash_chain:
            entry['hash_prev'] = self.hash_chain[-1]
        else:
            entry['hash_prev'] = 'genesis'
        
        # Calculate current hash
        entry_bytes = json.dumps(entry, sort_keys=True).encode()
        entry['hash'] = hashlib.sha256(entry_bytes).hexdigest()
        
        # Digital signature
        entry['signature'] = self.sign_entry(entry)
        
        # Store immutably
        self.storage.write(entry)
        self.hash_chain.append(entry['hash'])
        
        # Real-time streaming to SIEM
        self.stream_to_siem(entry)
        
        return entry['id']
    
    def verify_audit_trail(self, start_date, end_date):
        """
        Validates integrity of audit trail for compliance
        """
        entries = self.storage.read_range(start_date, end_date)
        
        for i, entry in enumerate(entries):
            # Verify signature
            if not self.verify_signature(entry):
                raise TamperDetectedException(f"Entry {entry['id']}")
            
            # Verify hash chain
            if i > 0:
                if entry['hash_prev'] != entries[i-1]['hash']:
                    raise ChainBrokenException(f"At entry {entry['id']}")
            
            # Verify timestamp sequence
            if i > 0:
                if entry['timestamp'] < entries[i-1]['timestamp']:
                    raise TimeSequenceException(f"At entry {entry['id']}")
        
        return True
```

---

## 🔄 Module 7: Secrets Management and Rotation

### The Challenge: Zero-Downtime Key Rotation

Banking systems can't stop for maintenance. We need to rotate secrets while running.

### Visual: Blue-Green Secret Rotation

```
Time T0: Initial State
┌──────────────┐
│ Active: Key A │ ← All agents using
│ Backup: None  │
└──────────────┘

Time T1: Introduce New Key
┌──────────────┐
│ Active: Key A │ ← Existing connections
│ Backup: Key B │ ← New connections start here
└──────────────┘

Time T2: Transition Phase
┌──────────────┐
│ Active: Key B │ ← Primary for new
│ Backup: Key A │ ← Still valid for old
└──────────────┘

Time T3: Complete Rotation
┌──────────────┐
│ Active: Key B │ ← All agents migrated
│ Backup: None  │ ← Key A revoked
└──────────────┘
```

### Implementation with HashiCorp Vault

```python
class SecretRotationManager:
    """
    Manages zero-downtime secret rotation for banking agents
    """
    
    def __init__(self):
        self.vault = hvac.Client(url='https://vault.bank.internal')
        self.rotation_schedule = {
            'high_security': timedelta(days=30),
            'standard': timedelta(days=90),
            'payment_keys': timedelta(days=180)
        }
    
    def rotate_secret(self, secret_path, classification='standard'):
        """
        Performs blue-green rotation without downtime
        """
        # Phase 1: Generate new secret
        new_secret = self.generate_secret()
        new_version = self.vault.write(
            f"{secret_path}/staging",
            value=new_secret
        )
        
        # Phase 2: Dual-key operation
        self.enable_dual_keys(secret_path)
        
        # Phase 3: Gradual migration
        agents = self.get_agents_using_secret(secret_path)
        batch_size = max(1, len(agents) // 10)  # 10% at a time
        
        for batch in chunks(agents, batch_size):
            self.migrate_batch(batch, secret_path, new_version)
            self.monitor_health(batch)
            time.sleep(60)  # Monitor for issues
        
        # Phase 4: Validate migration
        if self.validate_all_migrated(secret_path):
            self.promote_staging_to_active(secret_path)
            self.schedule_old_key_deletion(secret_path, delay_hours=24)
        else:
            self.rollback(secret_path)
            raise RotationFailedException()
    
    def monitor_health(self, agents):
        """
        Ensures agents remain healthy during rotation
        """
        for agent in agents:
            metrics = self.get_agent_metrics(agent)
            if metrics['error_rate'] > 0.01:  # 1% error threshold
                self.pause_rotation()
                self.investigate_issues(agent)
                
    def enable_dual_keys(self, path):
        """
        Allows both old and new keys during transition
        """
        config = {
            'accept_old_key': True,
            'accept_new_key': True,
            'prefer_new_key': True,
            'transition_period': '2h'
        }
        self.vault.write(f"{path}/config", **config)
```

---

## 🚨 Module 8: Incident Response for Compromised Agents

### The 36-Hour Rule

U.S. banking regulations require notification to federal regulators within 36 hours of determining an incident occurred.

### Visual: Incident Response Timeline

```
Hour 0-1: Detection & Containment
├── Anomaly detected by monitoring
├── Automatic containment triggered
└── Incident response team alerted

Hour 1-4: Assessment
├── Scope determination
├── Impact analysis
├── Evidence preservation
└── Initial containment validation

Hour 4-8: Decision Point
├── Classify severity (Critical/High/Medium/Low)
├── Determine if "notification incident"
└── If yes → Start 36-hour clock

Hour 8-24: Response & Investigation
├── Full forensic analysis
├── Root cause identification
├── Expanded containment if needed
└── Prepare regulatory notification

Hour 24-36: Notification & Recovery
├── Submit regulatory notifications
├── Implement fixes
├── Begin recovery procedures
└── Document lessons learned
```

### Incident Response Playbook

```python
class AgentIncidentResponse:
    """
    Automated incident response for compromised banking agents
    """
    
    def __init__(self):
        self.notification_threshold = timedelta(hours=36)
        self.regulators = {
            'fdic': 'notification@fdic.gov',
            'occ': 'incidents@occ.treas.gov',
            'federal_reserve': 'cyber@federalreserve.gov'
        }
    
    def handle_incident(self, alert):
        incident = self.create_incident(alert)
        
        # Immediate containment
        with self.emergency_response() as response:
            response.isolate_agent(alert['agent_id'])
            response.preserve_evidence()
            response.stop_bleeding()
        
        # Assessment phase
        impact = self.assess_impact(incident)
        
        # Determine notification requirement
        if self.is_notification_incident(impact):
            self.start_notification_timer(incident)
            
        # Parallel workstreams
        tasks = [
            self.forensic_analysis(incident),
            self.impact_assessment(incident),
            self.containment_validation(incident),
            self.recovery_planning(incident)
        ]
        
        results = asyncio.gather(*tasks)
        
        # Decision checkpoint
        if self.notification_timer_active(incident):
            self.prepare_regulatory_notification(incident, results)
            
        return incident
    
    def is_notification_incident(self, impact):
        """
        Determines if incident requires regulatory notification
        """
        triggers = [
            impact['service_disruption_hours'] >= 4,
            impact['customers_affected'] > 0,
            impact['data_breach_confirmed'],
            impact['financial_loss'] > 100000,
            impact['system_integrity_compromised']
        ]
        return any(triggers)
    
    def prepare_regulatory_notification(self, incident, analysis):
        notification = {
            'incident_id': incident['id'],
            'detection_time': incident['detected_at'],
            'determination_time': incident['determined_at'],
            'affected_systems': analysis['systems'],
            'impact_summary': analysis['impact'],
            'remediation_status': analysis['remediation'],
            'contact': incident['response_lead']
        }
        
        # Validate we're within 36-hour window
        elapsed = datetime.now() - incident['determined_at']
        if elapsed > self.notification_threshold:
            raise ComplianceViolationException("36-hour deadline exceeded")
            
        return notification
```

---

## 🏗️ Module 9: Production Architecture Pattern

### The Complete Security Stack

Here's how leading banks structure their AI agent infrastructure:

### Visual: Reference Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   External Traffic                       │
└─────────────────┬───────────────────────────────────────┘
                  │
        ┌─────────▼─────────┐
        │   Load Balancer   │
        │  (TLS Termination)│
        └─────────┬─────────┘
                  │
        ┌─────────▼─────────┐
        │  Istio Gateway    │
        │  ├── mTLS         │
        │  ├── JWT Valid    │
        │  └── WAF Rules    │
        └─────────┬─────────┘
                  │
    ┌─────────────┼─────────────┬──────────────┐
    │             │             │              │
┌───▼──┐    ┌────▼───┐    ┌────▼───┐    ┌────▼───┐
│Zone A│    │Zone B  │    │Zone C  │    │Monitor │
├──────┤    ├────────┤    ├────────┤    ├────────┤
│Agent │    │Agent   │    │Agent   │    │Falco   │
│Pods  │    │Pods    │    │Pods    │    │Sysdig  │
│      │    │        │    │        │    │Datadog │
├──────┤    ├────────┤    ├────────┤    ├────────┤
│Istio │    │Istio   │    │Istio   │    │SIEM    │
│Sidecar│   │Sidecar │    │Sidecar │    │Connect │
└──────┘    └────────┘    └────────┘    └────────┘
    │             │             │              │
    └─────────────┼─────────────┼──────────────┘
                  │             │
        ┌─────────▼─────────────▼─────────┐
        │     Shared Services             │
        ├──────────────────────────────────┤
        │ ├── HashiCorp Vault (Secrets)   │
        │ ├── PostgreSQL (Audit Logs)     │
        │ ├── Elasticsearch (Search)      │
        │ └── Kafka (Event Streaming)     │
        └──────────────────────────────────┘
```

### Kubernetes Configuration

```yaml
# Production-Ready Agent Deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fraud-detection-agent
  namespace: ai-agents-prod
spec:
  replicas: 3
  selector:
    matchLabels:
      app: fraud-agent
  template:
    metadata:
      labels:
        app: fraud-agent
        version: v2.1.0
      annotations:
        sidecar.istio.io/inject: "true"
        vault.hashicorp.com/agent-inject: "true"
    spec:
      serviceAccountName: fraud-agent-sa
      securityContext:
        runAsNonRoot: true
        runAsUser: 10001
        fsGroup: 10001
      
      containers:
      - name: agent
        image: registry.bank.com/fraud-agent:2.1.0-signed
        
        securityContext:
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          capabilities:
            drop:
            - ALL
        
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
        
        env:
        - name: AGENT_ID
          value: "fraud-detector-001"
        - name: LOG_LEVEL
          value: "INFO"
        - name: VAULT_ADDR
          value: "https://vault.bank.internal:8200"
        
        volumeMounts:
        - name: tmp
          mountPath: /tmp
        - name: cache
          mountPath: /app/cache
        
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
      
      volumes:
      - name: tmp
        emptyDir: {}
      - name: cache
        emptyDir: {}
      
      affinity:
        podAntiAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
          - labelSelector:
              matchExpressions:
              - key: app
                operator: In
                values:
                - fraud-agent
            topologyKey: kubernetes.io/hostname
```

---

## 🎓 Module 10: Practical Exercises

### Exercise 1: Design Your First Secure Agent

**Scenario**: You're building a payment fraud detection agent that needs to:
- Analyze 50,000 transactions per minute
- Access customer payment history
- Flag suspicious patterns
- Trigger payment blocks

**Your Task**: 
1. Define the OAuth scopes needed
2. Identify the certificates required
3. Design the monitoring rules
4. Plan the rotation schedule

### Exercise 2: Incident Response Simulation

**Scenario**: Your monitoring system detects:
- Agent "payment-analyzer-003" is accessing 10x normal data
- Requests coming from unusual IP range
- Pattern matches known attack signature

**Your Task**:
1. Write the containment steps (in order)
2. Determine if this triggers 36-hour notification
3. Design the forensic evidence collection
4. Plan the recovery process

### Exercise 3: Performance vs Security Trade-off

**Challenge**: Your fraud detection must process transactions in <100ms but also needs:
- mTLS authentication
- Request signing
- Audit logging
- Behavioral monitoring

**Your Task**:
1. Calculate the overhead of each security layer
2. Design optimizations that maintain security
3. Create a caching strategy
4. Build a connection pooling pattern

---

## 🚀 Next Steps: Your 90-Day Implementation Plan

### Days 1-30: Foundation
- [ ] Inventory existing AI agents
- [ ] Implement unique identities for each agent
- [ ] Deploy runtime monitoring (Falco or equivalent)
- [ ] Establish basic audit logging
- [ ] Create incident response procedures

### Days 31-60: Security Hardening
- [ ] Deploy service mesh with mTLS
- [ ] Implement OAuth 2.0 authorization
- [ ] Set up behavioral baselines
- [ ] Configure automated secret rotation
- [ ] Integrate with Security Operations Center

### Days 61-90: Production Readiness
- [ ] Conduct security assessment
- [ ] Run tabletop exercises
- [ ] Validate compliance requirements
- [ ] Performance tune security controls
- [ ] Document all procedures

---

## 💡 Key Takeaways for AI Architects

1. **Defense in Depth is Non-Negotiable**: Each security layer protects against different threats. Missing even one creates vulnerability.

2. **Automation is Essential**: Manual security can't match agent speed. Automate certificate rotation, monitoring, and response.

3. **Compliance Drives Architecture**: The 36-hour rule and audit requirements shape your entire design.

4. **Performance and Security Balance**: Smart optimizations (connection pooling, session caching) maintain both.

5. **Behavioral Monitoring is Your Last Line**: Even with perfect credentials, runtime behavior reveals compromises.

---

## 🔗 Resources for Continued Learning

### Essential Tools
- **Istio/Linkerd**: Service mesh for mTLS
- **HashiCorp Vault**: Secrets management
- **Falco/Sysdig**: Runtime security
- **Kyverno/OPA**: Policy enforcement
- **Elasticsearch/Splunk**: SIEM integration

### Standards to Study
- **AgentFacts**: Know Your Agent framework
- **FAPI**: Financial-grade API specifications
- **PCI-DSS v4.0**: Payment card security
- **NIST AI Risk Management**: Comprehensive framework

### Real-World References
- JPMorgan Chase's five-certificate model
- Goldman Sachs' container security
- Monzo's Linkerd implementation
- PayPal's microservice security

---

## 🤝 Let's Connect!

Found this tutorial helpful? I regularly share practical AI architecture insights from real banking implementations. Follow for more hands-on tutorials that transform complex security concepts into actionable patterns.

**What security challenge are you tackling in your AI agent deployment? Share in the comments - let's learn from each other's experiences!**

---

*Remember: Security isn't a feature - it's the foundation that enables everything else. Build it right from the start.*

#AIArchitecture #BankingTechnology #CyberSecurity #EnterpriseAI #MachineLearning #FinancialServices #CloudSecurity #DevSecOps #AIAgents #TechnicalTutorial