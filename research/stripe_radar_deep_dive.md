# Stripe Radar Deep Dive: From ML-Centric to LLM-Based Classification

## Executive Summary

Stripe Radar represents one of the most sophisticated production fraud classification systems in fintech, processing over $1.4 trillion in payments annually with sub-100ms latency and a 0.1% false positive rate. In May 2025, Stripe announced a paradigm shift: the **Payments Foundation Model**, a transformer-based architecture trained on tens of billions of transactions that treats payment sequences like language tokens. This transition from specialized ML models to a unified foundation model offers a blueprint for transforming any classification system—including Bank of America's dispute resolution pipeline—from traditional ML to LLM-based approaches.

This document provides a deep technical analysis of Stripe Radar's architecture evolution, identifies the key patterns that enabled their ML-to-LLM transition, and presents a research plan for applying these patterns to financial dispute classification systems.

---

## Part 1: Stripe Radar Architecture Deep Dive

### 1.1 System Overview and Performance Metrics

Stripe Radar operates as a real-time fraud classification engine with remarkable performance characteristics that set the benchmark for financial AI systems:

**Core Performance Metrics:**
- Evaluates 1,000+ transaction characteristics per payment
- Decision latency under 100 milliseconds
- False positive rate of 0.1% across billions of legitimate payments
- Fraud occurs in approximately 1 out of every 1,000 payments (0.1% base rate)
- Prevents over $500 million in payment fraud monthly
- Reduces dispute rates by 17% year-over-year (2024)

**Data Scale:**
- Processes payments from millions of businesses globally
- $1.4 trillion in total payment volume in 2024 (equivalent to ~1.3% of global GDP)
- Training data includes tens of billions of historical transactions
- Network-wide signals from partnerships with Visa, Mastercard, American Express, and thousands of banks

### 1.2 Architecture Evolution (2016-2025)

Stripe's architecture has undergone four major evolutionary phases, each representing a paradigm shift in how they approach fraud classification:

**Phase 1: Rule-Based + Logistic Regression (2016-2018)**

The initial system combined hand-crafted rules with statistical models. Feature engineering was manual and labor-intensive, requiring domain experts to hypothesize fraud patterns and encode them as features. While interpretable, this approach couldn't scale to the complexity of modern fraud patterns.

**Phase 2: Gradient Boosting Ensembles (2018-2020)**

Stripe adopted XGBoost as their primary model, leveraging its ability to handle high-dimensional feature spaces and capture non-linear interactions. The "memorization" capability of tree-based models excelled at learning specific fraud patterns from historical data. However, XGBoost's training time scaled linearly with data size, creating bottlenecks as Stripe's transaction volume grew.

**Phase 3: Wide & Deep Architecture (2020-2022)**

Stripe implemented a hybrid ensemble combining XGBoost (the "wide" component for memorization) with Deep Neural Networks (the "deep" component for generalization). This architecture attempted to capture both specific fraud patterns and abstract representations. Key innovation: The DNN component could generalize to novel fraud patterns that XGBoost hadn't seen in training.

**Phase 4: Pure DNN with Multi-Branch Architecture (2022-2024)**

In mid-2022, Stripe made a critical decision: eliminate XGBoost entirely and migrate to a pure DNN-only architecture. This was counterintuitive—removing XGBoost initially caused a 1.5% drop in recall. The breakthrough came from developing a multi-branch DNN architecture inspired by ResNeXt:

```
Input Features (1000+)
    │
    ├── Branch 1 (Specialized: Card Characteristics)
    │       └── Dense → ReLU → Dense
    │
    ├── Branch 2 (Specialized: Device Fingerprinting)  
    │       └── Dense → ReLU → Dense
    │
    ├── Branch 3 (Specialized: Behavioral Patterns)
    │       └── Dense → ReLU → Dense
    │
    ├── Branch N (Specialized: Network Signals)
    │       └── Dense → ReLU → Dense
    │
    └── Aggregation Layer
            └── Concatenate → Dense → Output (Risk Score 0-100)
```

**Benefits of DNN-Only Architecture:**
- Training time reduced by 85% (enabling more frequent model updates)
- Better scaling with additional training data (10x data increase showed significant improvements; 100x experiments ongoing)
- Native compatibility with advanced techniques: transfer learning, embeddings, multi-task learning
- Each data increase produces "outsized improvements in model quality"—unlike XGBoost which showed diminishing returns

**Phase 5: Payments Foundation Model (2025-Present)**

The most revolutionary shift occurred in May 2025 when Stripe announced their Payments Foundation Model—a transformer-based architecture that treats payment sequences as token streams. This represents a fundamental reconceptualization: instead of classifying individual transactions with extracted features, the model learns the "language of payments" from raw transaction sequences.

### 1.3 The Payments Foundation Model: Technical Architecture

The Payments Foundation Model represents Stripe's application of LLM principles to financial data. According to Gautam Kedia (Head of Applied ML at Stripe), the team wasn't certain this approach would work for payments:

> "It wasn't obvious that it would—payments [are] like language in some ways (structural patterns similar to syntax and semantics, temporally sequential) and extremely unlike language in others (fewer distinct 'tokens', contextual sparsity, fewer organizing principles akin to grammatical rules)."

**Core Architecture Principles:**

1. **Transaction-as-Token Representation**: Each transaction is encoded as a sequence of tokens representing its characteristics. The model processes these sequences using self-attention mechanisms to capture relationships across transaction histories.

2. **Embedding-Based Classification**: Rather than discrete features, the model produces dense embeddings for each transaction that capture "hundreds of subtle signals that no human—and no previous model—could track on their own."

3. **Sequence-Level Reasoning**: The transformer architecture enables the model to reason about patterns across sequences of transactions, detecting fraud that only becomes apparent when viewing multiple related transactions together.

**Tokenization Strategy (Inferred):**

```python
# Conceptual transaction tokenization
transaction_tokens = [
    BIN_TOKEN,           # Card issuer identification
    AMOUNT_BUCKET,       # Discretized transaction amount
    MERCHANT_CATEGORY,   # MCC code
    DEVICE_FINGERPRINT,  # Hashed device identifier
    GEO_TOKEN,           # Location encoding
    TIME_BUCKET,         # Time-of-day/day-of-week
    VELOCITY_TOKEN,      # Transaction frequency encoding
    # ... additional attribute tokens
]

# Sequence represents transaction history
sequence = [tx_tokens_t1, tx_tokens_t2, ..., tx_tokens_tn, CURRENT_TX]
```

**Performance Results:**

The foundation model's impact was immediate and dramatic. For card testing attacks (where fraudsters test stolen cards with small transactions):
- Previous specialized models: 80% reduction achieved over 2 years of incremental improvements
- Foundation model: Detection rate increased from 59% to 97% "overnight" for attacks on large businesses

**Why Transformers Work for Payments:**

The key insight is that payment sequences share structural properties with natural language:

| Property | Natural Language | Payment Sequences |
|----------|-----------------|-------------------|
| Sequential Structure | Words follow grammatical patterns | Transactions follow behavioral patterns |
| Contextual Meaning | Word meaning depends on surrounding words | Transaction risk depends on surrounding transactions |
| Long-Range Dependencies | Pronouns reference earlier nouns | Current transaction patterns relate to historical behavior |
| Compositionality | Phrases combine to form sentences | Transaction characteristics combine to form risk profiles |

### 1.4 Feature Engineering: The 1,000+ Characteristics

Stripe's feature engineering represents years of accumulated domain knowledge. Understanding these features is critical for mapping to other classification domains.

**Feature Categories:**

1. **Card Characteristics**
   - BIN (Bank Identification Number) patterns
   - Card type (credit, debit, prepaid)
   - Card country of issuance
   - Card brand (Visa, Mastercard, Amex, Discover)
   - Card expiration proximity

2. **Device Fingerprinting**
   - Browser characteristics and version
   - Screen resolution and color depth
   - Timezone and language settings
   - Canvas fingerprinting signals
   - WebGL renderer information
   - Installed fonts and plugins

3. **Behavioral Signals**
   - Mouse movement patterns during checkout
   - Typing cadence and keystroke dynamics
   - Time spent on checkout page
   - Navigation patterns through site
   - Copy-paste detection for form fields

4. **Network Intelligence**
   - IP geolocation and ISP information
   - VPN/proxy detection
   - IP reputation from network-wide data
   - Historical activity from same IP across Stripe network
   - TOR exit node detection

5. **Transaction Characteristics**
   - Amount and currency
   - Merchant category code (MCC)
   - Transaction type (card-present vs. card-not-present)
   - Recurring vs. one-time payment
   - Cross-border transaction flag

6. **Velocity and Frequency Metrics**
   - Cards per email (hourly/daily/weekly)
   - Transactions per IP address
   - Failed attempts per card
   - Amount velocity (spending rate)
   - New account velocity

7. **Identity Verification Signals**
   - AVS (Address Verification System) match
   - CVV verification result
   - Cardholder name to email correlation
   - Shipping to billing address match
   - Email domain reputation (disposable email detection)

8. **Network-Wide Signals**
   - TC40 reports (Visa fraud reports)
   - SAFE reports (Mastercard fraud reports)
   - Early dispute notifications from issuers
   - Cross-merchant fraud patterns
   - Card-seen-before-on-Stripe signals

### 1.5 Risk Insights: Explainability Infrastructure

Stripe invested heavily in explainability—a critical requirement for financial services. The Risk Insights feature provides:

**Feature Attribution Table:**
- Lists features that most increased the risk score
- Lists features that most decreased the risk score
- Provides context for why each feature matters

**Example Risk Insights Output:**
```
Risk Score: 78 (Elevated)

Factors Increasing Risk:
├── IP address associated with 15 different cards in past hour (+25)
├── Card country (RU) differs from IP country (US) (+18)
├── Disposable email domain detected (+12)
└── Transaction amount 3.2x higher than merchant average (+8)

Factors Decreasing Risk:
├── Card previously used successfully on Stripe network (-15)
├── Device fingerprint matches previous legitimate purchase (-10)
└── Email domain has 5+ year history (-5)
```

**Implementation Challenges:**
- DNNs are inherently black boxes—harder to explain than tree-based models
- Stripe developed specialized tooling to extract feature contributions from neural networks
- Trade-off accepted: Better model performance justified reduced interpretability

### 1.6 Radar Assistant: LLM-Powered Rule Creation

Stripe's Radar Assistant demonstrates a parallel use of LLMs—translating natural language to fraud rules:

**Natural Language Input:**
"Review payments where the card and IP countries are different and the amount is over $500"

**Generated Rule:**
```
Review if :card_country: != :ip_country: and :amount_in_usd: > 500
```

**Supported Capabilities:**
- Natural language to rule syntax translation
- Backtesting integration (see rule impact before deployment)
- Support for 100+ attributes in rule conditions
- Rule combination and logic optimization

This represents a different LLM application pattern: using language models as interfaces to structured systems rather than as the classification engine itself.

---

## Part 2: ML-to-LLM Transformation Patterns

### 2.1 Key Patterns from Stripe's Transition

Analyzing Stripe's evolution reveals several patterns applicable to any ML-to-LLM transformation:

**Pattern 1: Staged Migration with Fallback**

Stripe didn't replace XGBoost overnight. They maintained the ensemble (Wide & Deep) while developing the pure DNN architecture, only switching when they'd recovered the performance gap. Similarly, the foundation model augments rather than replaces specialized models.

**Pattern 2: Architecture Simplification Enables Scaling**

Counterintuitively, moving to a simpler architecture (pure DNN instead of ensemble) enabled better scaling with data. The 85% reduction in training time allowed more frequent updates and larger training datasets.

**Pattern 3: From Features to Embeddings**

The shift from hand-crafted features to learned embeddings is the core transformation. Instead of encoding domain knowledge as explicit features, the foundation model learns representations that capture patterns humans can't articulate.

**Pattern 4: Sequence-Level Reasoning**

Traditional ML classified individual transactions in isolation. The foundation model reasons about sequences of transactions, enabling detection of patterns that only emerge across multiple events.

**Pattern 5: Task-Agnostic Representations**

The foundation model produces embeddings that can be used for multiple downstream tasks: fraud detection, authorization optimization, merchant risk assessment. This multi-task capability is a hallmark of foundation model approaches.

### 2.2 Mapping ML Components to LLM Equivalents

| ML-Centric Component | LLM-Based Equivalent | Stripe Implementation |
|---------------------|---------------------|----------------------|
| Feature Engineering | Embedding Layer | Transaction-to-token encoding |
| XGBoost/Random Forest | Transformer Blocks | Self-attention over sequences |
| Rule-Based Filters | Prompt-Based Classification | Radar Assistant |
| Ensemble Voting | Attention-Weighted Aggregation | Multi-branch output fusion |
| Threshold Tuning | Confidence Calibration | Risk score normalization |
| Feature Store | Vector Database | Transaction embedding storage |
| Model Retraining | Incremental Learning | Continuous embedding updates |
| Explainability (SHAP) | Attention Visualization | Risk Insights feature |

### 2.3 Hybrid Architecture Patterns

The most successful production systems combine ML and LLM approaches:

**Pattern A: Embedding + Classifier**
```
Transaction Data → Foundation Model → Embedding → Specialized Classifier → Decision
```
Uses the foundation model for representation learning, but a lightweight classifier for final decisions. Benefits: Fast inference, interpretable final layer.

**Pattern B: RAG-Enhanced Classification**
```
Input → Embedding → Retrieve Similar Cases → LLM Reasoning → Classification
```
Retrieves relevant historical cases to augment LLM context. Benefits: Handles edge cases, provides precedent-based explanations.

**Pattern C: LLM as Orchestrator**
```
Input → LLM Router → {Specialized Model A, Model B, Model C} → LLM Aggregator → Decision
```
LLM decides which specialized models to invoke and how to combine their outputs. Benefits: Dynamic routing, handles diverse input types.

---

## Part 3: Research Plan for Dispute Classification Transformation

### 3.1 Problem Statement

Transform the Bank of America Money Movement Division's dispute classification system from an ML-centric approach to an LLM-based architecture, applying lessons from Stripe Radar's evolution. The goal is to map natural language dispute descriptions from chatbot interactions to the hierarchical reason code taxonomy:

```
Network (Visa, Mastercard, Amex, Discover, PayPal)
    └── reason_code_group (8 groups)
        └── unified_category (8 categories)
            └── specific_code (~100 codes)
```

### 3.2 Research Phase 1: Architecture Analysis (Weeks 1-2)

**Objective:** Map Stripe's architecture patterns to dispute classification requirements

**Research Questions:**
1. What is the equivalent of "transaction characteristics" for dispute text?
2. How should dispute sequences be tokenized (word-level vs. semantic chunks)?
3. What is the optimal embedding dimension for dispute representations?
4. How does the hierarchical taxonomy map to multi-task learning heads?

**Deliverables:**
- Architecture comparison document (Stripe Radar vs. proposed dispute system)
- Feature mapping table (1,000 Stripe features → dispute feature equivalents)
- Preliminary system design diagram

**Key Experiments:**
```python
# Experiment 1.1: Tokenization Strategy Comparison
tokenization_strategies = [
    "word_level",           # Standard tokenization
    "subword_bpe",          # Byte-pair encoding
    "semantic_chunks",      # Sentence-level chunks
    "hybrid_structured"     # Combine structured fields + free text
]

# Experiment 1.2: Embedding Model Selection
embedding_models = [
    "all-MiniLM-L6-v2",     # Fast, general purpose
    "gte-large",            # High quality, larger
    "financial-bert",       # Domain-adapted
    "custom-finetuned"      # Fine-tuned on dispute data
]

# Evaluate: Classification accuracy, inference latency, embedding quality
```

### 3.3 Research Phase 2: Foundation Model Development (Weeks 3-6)

**Objective:** Develop a dispute-domain foundation model following Stripe's approach

**Research Questions:**
1. Can transformer architecture learn the "language of disputes" from historical data?
2. What pre-training objective works best (masked language modeling, contrastive learning)?
3. How much historical data is required for effective pre-training?
4. What is the optimal model size vs. performance trade-off?

**Pre-training Approaches to Evaluate:**

**Approach A: Masked Dispute Modeling (MDM)**
```python
# Mask dispute components and predict them
input: "Customer claims [MASK] was not received for order #12345"
target: "merchandise"

# Mask reason codes and predict from description
input: "Subscription was canceled but charges continued [MASK_CODE]"  
target: "13.2" (Visa Cancelled Recurring Transaction)
```

**Approach B: Contrastive Learning**
```python
# Learn embeddings where similar disputes cluster
anchor = "Item arrived damaged, requesting refund"
positive = "Product was broken upon delivery"  # Same category
negative = "Charged twice for same purchase"    # Different category

# Train with triplet loss or InfoNCE
```

**Approach C: Multi-Task Pre-training**
```python
class DisputeFoundationModel(nn.Module):
    def __init__(self):
        self.encoder = TransformerEncoder(...)
        
        # Multi-task heads (like Stripe's multi-branch)
        self.network_head = nn.Linear(768, 5)      # 5 networks
        self.group_head = nn.Linear(768, 8)        # 8 reason_code_groups
        self.category_head = nn.Linear(768, 8)    # 8 unified_categories
        self.code_head = nn.Linear(768, 100)       # ~100 specific codes
```

**Deliverables:**
- Pre-trained dispute foundation model
- Embedding quality benchmarks
- Training data requirements analysis
- Model architecture documentation

### 3.4 Research Phase 3: Prompt Engineering Pipeline (Weeks 7-10)

**Objective:** Develop production-ready prompt engineering approaches that don't require fine-tuning

**Research Focus Areas:**

**3.4.1 Hierarchical Classification Prompts**

Develop prompts that leverage the taxonomy structure:

```python
HIERARCHICAL_CLASSIFICATION_PROMPT = """
You are a financial dispute classification expert. Classify the following dispute
through the hierarchy:

TAXONOMY:
- reason_code_groups: authorization, fraud, processing_errors, cardholder_disputes, 
  consumer_disputes, retrieval_inquiry, non_card_dispute, other
- unified_categories: fraudulent, product_not_received, duplicate, subscription_canceled,
  credit_not_processed, product_unacceptable, unrecognized, general

DISPUTE TEXT:
{dispute_text}

CLASSIFICATION PROCESS:
1. First, identify the primary issue type
2. Determine the appropriate reason_code_group
3. Select the unified_category within that group
4. Match to specific network code based on {network}

OUTPUT (JSON):
{
  "reasoning": "step-by-step explanation",
  "reason_code_group": "...",
  "unified_category": "...",
  "specific_code": "...",
  "confidence": 0.0-1.0
}
"""
```

**3.4.2 Few-Shot Classification with Dynamic Examples**

```python
class DynamicFewShotClassifier:
    def __init__(self, embedding_model, example_store):
        self.embedding_model = embedding_model
        self.example_store = example_store  # Vector DB of classified disputes
    
    def classify(self, dispute_text: str, num_examples: int = 5):
        # Retrieve most similar historical disputes
        embedding = self.embedding_model.encode(dispute_text)
        similar_examples = self.example_store.search(embedding, k=num_examples)
        
        # Build few-shot prompt
        prompt = self.build_prompt(dispute_text, similar_examples)
        
        # Get classification from LLM
        return self.llm.classify(prompt)
```

**3.4.3 Chain-of-Thought for Ambiguous Cases**

```python
COT_PROMPT = """
Analyze this dispute step by step:

DISPUTE: "{dispute_text}"

STEP 1 - Extract Key Information:
- What happened? (the complaint)
- When did it happen?
- What does the customer want?
- What evidence is mentioned?

STEP 2 - Initial Category Assessment:
- Is this fraud-related? (unauthorized transactions, stolen card)
- Is this merchandise-related? (not received, damaged, wrong item)
- Is this billing-related? (duplicate charge, wrong amount, subscription)
- Is this service-related? (quality issues, cancellation problems)

STEP 3 - Network-Specific Code Matching:
Given network: {network}
Available codes for this category: {relevant_codes}
Match to the most specific code that applies.

STEP 4 - Confidence Assessment:
- How clear is the dispute description?
- Are there multiple possible classifications?
- What additional information would help?

FINAL CLASSIFICATION:
"""
```

**3.4.4 Self-Consistency Voting**

```python
class SelfConsistencyClassifier:
    def classify(self, dispute_text: str, num_samples: int = 5):
        classifications = []
        
        for _ in range(num_samples):
            # Run classification with temperature > 0
            result = self.llm.classify(
                dispute_text, 
                temperature=0.7
            )
            classifications.append(result)
        
        # Majority voting
        final_classification = self.majority_vote(classifications)
        
        # Confidence from consistency
        consistency_score = self.calculate_consistency(classifications)
        
        return {
            "classification": final_classification,
            "confidence": consistency_score,
            "all_predictions": classifications
        }
```

**Deliverables:**
- Prompt templates library
- Few-shot example selection algorithm
- Self-consistency implementation
- Benchmark results across prompt strategies

### 3.5 Research Phase 4: RAG-Enhanced Classification (Weeks 11-14)

**Objective:** Build retrieval-augmented classification following Stripe's network intelligence pattern

**Architecture Design:**

```
┌─────────────────────────────────────────────────────────────┐
│                    RAG Classification Pipeline               │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Dispute Text ──┬──► Embedding ──► Vector Search ──────┐    │
│                 │                                       │    │
│                 │    ┌─────────────────────────────────┐│    │
│                 │    │     Retrieved Context           ││    │
│                 │    │  ┌─────────────────────────┐   ││    │
│                 │    │  │ Similar Past Disputes   │   ││    │
│                 │    │  │ (with classifications)  │   ││    │
│                 │    │  └─────────────────────────┘   ││    │
│                 │    │  ┌─────────────────────────┐   ││    │
│                 │    │  │ Taxonomy Definitions    │   ││    │
│                 │    │  │ (code descriptions)     │   ││    │
│                 │    │  └─────────────────────────┘   ││    │
│                 │    │  ┌─────────────────────────┐   ││    │
│                 │    │  │ Network Rules           │   ││    │
│                 │    │  │ (Visa/MC/Amex specs)    │   ││    │
│                 │    │  └─────────────────────────┘   ││    │
│                 │    └─────────────────────────────────┘│    │
│                 │                                       │    │
│                 └──────────────────────────────────────┬┘    │
│                                                        │     │
│                 ┌──────────────────────────────────────▼──┐  │
│                 │           Classification LLM            │  │
│                 │  (Dispute + Retrieved Context → Code)   │  │
│                 └──────────────────────────────────────┬──┘  │
│                                                        │     │
│                 ┌──────────────────────────────────────▼──┐  │
│                 │         Output + Explanation            │  │
│                 │  reason_code_group: cardholder_disputes │  │
│                 │  unified_category: product_not_received │  │
│                 │  specific_code: visa_13.1               │  │
│                 │  confidence: 0.92                       │  │
│                 │  reasoning: "Customer states item..."   │  │
│                 └─────────────────────────────────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Vector Database Design:**

```python
# Collection 1: Historical Disputes
historical_disputes_schema = {
    "id": "uuid",
    "dispute_text": "string",
    "embedding": "vector[768]",
    "network": "string",
    "reason_code_group": "string",
    "unified_category": "string",
    "specific_code": "string",
    "resolution": "string",
    "created_at": "datetime"
}

# Collection 2: Taxonomy Definitions
taxonomy_schema = {
    "code": "string",           # e.g., "visa_13.1"
    "description": "string",
    "embedding": "vector[768]",
    "network": "string",
    "reason_code_group": "string",
    "unified_category": "string",
    "examples": ["string"],
    "keywords": ["string"]
}

# Collection 3: Network Regulations
regulations_schema = {
    "network": "string",
    "code": "string",
    "regulation_text": "string",
    "embedding": "vector[768]",
    "time_limits": "string",
    "required_evidence": ["string"]
}
```

**Retrieval Strategy:**

```python
class HybridRetriever:
    def retrieve(self, dispute_text: str, network: str):
        embedding = self.encode(dispute_text)
        
        # Retrieve similar disputes (semantic search)
        similar_disputes = self.dispute_collection.search(
            embedding, 
            k=5,
            filter={"network": network}
        )
        
        # Retrieve relevant taxonomy codes (semantic + keyword)
        relevant_codes = self.taxonomy_collection.hybrid_search(
            embedding=embedding,
            keywords=self.extract_keywords(dispute_text),
            k=10,
            filter={"network": network}
        )
        
        # Retrieve network regulations
        regulations = self.regulation_collection.search(
            embedding,
            k=3,
            filter={"network": network}
        )
        
        return {
            "similar_disputes": similar_disputes,
            "relevant_codes": relevant_codes,
            "regulations": regulations
        }
```

**Deliverables:**
- Vector database schema and implementation
- Retrieval strategy benchmarks
- RAG pipeline integration
- A/B test framework for retrieval variations

### 3.6 Research Phase 5: Confidence Calibration & Human-in-the-Loop (Weeks 15-18)

**Objective:** Implement production-grade confidence scoring and escalation following Stripe's three-tier routing

**Confidence Calibration Approaches:**

**Approach 1: Verbalized Confidence**
```python
CONFIDENCE_PROMPT = """
After classifying the dispute, rate your confidence:
- HIGH (>90%): Clear dispute description, unambiguous category match
- MEDIUM (70-90%): Good match but some ambiguity
- LOW (<70%): Multiple possible categories, unclear description

Classification: {classification}
Confidence Level: {verbalized_confidence}
Confidence Score: {numeric_score}
Reasoning: {why_this_confidence}
"""
```

**Approach 2: Self-Consistency Confidence**
```python
def calculate_consistency_confidence(predictions: List[Dict]) -> float:
    """
    Run classification N times with temperature > 0
    Confidence = agreement rate among predictions
    """
    codes = [p['specific_code'] for p in predictions]
    most_common = Counter(codes).most_common(1)[0]
    return most_common[1] / len(predictions)
```

**Approach 3: Calibrated Logprobs**
```python
def calibrated_confidence(logprobs: List[float], calibration_model) -> float:
    """
    Apply isotonic regression calibration to raw logprobs
    """
    raw_confidence = np.exp(np.mean(logprobs))
    calibrated = calibration_model.predict([[raw_confidence]])[0]
    return calibrated
```

**Three-Tier Routing System:**

```python
class DisputeRouter:
    def __init__(self, thresholds):
        self.high_confidence_threshold = thresholds.get('high', 0.85)
        self.low_confidence_threshold = thresholds.get('low', 0.50)
    
    def route(self, classification_result: Dict) -> str:
        confidence = classification_result['confidence']
        
        if confidence >= self.high_confidence_threshold:
            # Auto-approve: 73%+ of cases (target)
            return self.auto_approve(classification_result)
        
        elif confidence >= self.low_confidence_threshold:
            # Human review queue: 20% of cases
            return self.queue_for_review(classification_result)
        
        else:
            # Escalation: 7% of cases
            return self.escalate(classification_result)
    
    def auto_approve(self, result):
        # Log for audit trail
        self.audit_log.record(result, action="auto_approved")
        return {"action": "approved", "classification": result}
    
    def queue_for_review(self, result):
        # Add to review queue with reasoning displayed
        review_item = {
            "classification": result,
            "reasoning": result['reasoning'],
            "similar_cases": result.get('similar_disputes', []),
            "alternative_codes": result.get('alternative_classifications', [])
        }
        self.review_queue.add(review_item)
        return {"action": "queued", "queue_id": review_item['id']}
    
    def escalate(self, result):
        # Flag for specialist review + active learning
        self.escalation_queue.add(result)
        self.active_learning_candidates.add(result)
        return {"action": "escalated", "reason": "low_confidence"}
```

**Active Learning Pipeline:**

```python
class ActiveLearningPipeline:
    def select_samples(self, unlabeled_pool: List, strategy: str = "uncertainty"):
        if strategy == "uncertainty":
            # Select lowest confidence samples
            return sorted(unlabeled_pool, key=lambda x: x['confidence'])[:100]
        
        elif strategy == "diversity":
            # Select diverse samples using clustering
            embeddings = [self.embed(x['text']) for x in unlabeled_pool]
            clusters = self.cluster(embeddings, n_clusters=100)
            return [unlabeled_pool[self.get_centroid_idx(c)] for c in clusters]
        
        elif strategy == "hybrid":
            # Combine uncertainty and diversity
            uncertain = self.select_samples(unlabeled_pool, "uncertainty")
            diverse = self.select_samples(unlabeled_pool, "diversity")
            return self.merge_strategies(uncertain, diverse)
    
    def update_system(self, labeled_samples: List):
        # Add to vector database
        self.add_to_training_data(labeled_samples)
        
        # Update few-shot example pool
        self.update_example_pool(labeled_samples)
        
        # Recalibrate confidence model
        self.recalibrate_confidence()
        
        # Log improvement metrics
        self.track_improvement(labeled_samples)
```

**Deliverables:**
- Calibrated confidence scoring system
- Three-tier routing implementation
- Active learning pipeline
- Human review interface design
- Escalation workflow documentation

### 3.7 Research Phase 6: Evaluation & Benchmarking (Weeks 19-22)

**Objective:** Comprehensive evaluation framework matching Stripe's rigor

**Evaluation Metrics:**

1. **Hierarchical Metrics:**
   - Hierarchical Precision/Recall/F1 (partial credit for correct ancestors)
   - Level-wise accuracy (Network, Group, Category, Code)
   - Category distance (path length between predicted and true)

2. **Business Metrics:**
   - Auto-approval rate (target: 73%+)
   - False positive rate at reason_code_group level
   - Average processing time reduction
   - Human review queue volume

3. **Operational Metrics:**
   - Inference latency (target: <500ms)
   - Throughput (disputes/second)
   - Cost per classification

**Benchmark Dataset Design:**

```python
benchmark_dataset = {
    "train": {
        "size": 50000,
        "distribution": "stratified by reason_code_group",
        "time_range": "2022-2024"
    },
    "validation": {
        "size": 5000,
        "distribution": "stratified",
        "time_range": "2024 H1"
    },
    "test": {
        "size": 5000,
        "distribution": "stratified",
        "time_range": "2024 H2"
    },
    "edge_cases": {
        "size": 1000,
        "categories": [
            "ambiguous_descriptions",
            "multi_category_disputes",
            "rare_codes",
            "network_specific_edge_cases"
        ]
    }
}
```

**A/B Testing Framework:**

```python
class ClassificationABTest:
    def __init__(self, control_model, treatment_model):
        self.control = control_model      # Current ML-based system
        self.treatment = treatment_model  # LLM-based system
    
    def run_test(self, test_disputes: List, traffic_split: float = 0.5):
        results = {"control": [], "treatment": []}
        
        for dispute in test_disputes:
            if random.random() < traffic_split:
                result = self.treatment.classify(dispute)
                results["treatment"].append(result)
            else:
                result = self.control.classify(dispute)
                results["control"].append(result)
        
        return self.analyze_results(results)
    
    def analyze_results(self, results):
        return {
            "accuracy_improvement": self.calc_accuracy_delta(results),
            "latency_comparison": self.calc_latency_delta(results),
            "confidence_calibration": self.calc_calibration(results),
            "statistical_significance": self.calc_significance(results)
        }
```

**Deliverables:**
- Comprehensive evaluation report
- Benchmark dataset
- A/B test results
- Performance comparison (ML vs. LLM approaches)
- ROI analysis

### 3.8 Research Timeline Summary

| Phase | Weeks | Focus | Key Deliverables |
|-------|-------|-------|------------------|
| 1 | 1-2 | Architecture Analysis | Design docs, feature mapping |
| 2 | 3-6 | Foundation Model Dev | Pre-trained model, benchmarks |
| 3 | 7-10 | Prompt Engineering | Prompt library, few-shot system |
| 4 | 11-14 | RAG Implementation | Vector DB, retrieval pipeline |
| 5 | 15-18 | Confidence & HITL | Routing system, active learning |
| 6 | 19-22 | Evaluation | Benchmarks, A/B tests, ROI |

**Total Duration:** 22 weeks (~5.5 months)

---

## Part 4: Implementation Recommendations

### 4.1 Quick Wins (Implementable in 2-4 Weeks)

1. **Radar Assistant Pattern for Dispute Rules**
   - Implement natural language to rule translation
   - Allow analysts to create classification rules via prompts
   - Backtest rules against historical disputes

2. **RAG-Enhanced Classification Prototype**
   - Index existing classified disputes in vector database
   - Implement basic semantic retrieval
   - Add retrieved examples to classification prompts

3. **Confidence-Based Routing**
   - Implement self-consistency scoring
   - Create three-tier routing logic
   - Set up human review queue

### 4.2 Medium-Term Investments (2-3 Months)

1. **Dispute Foundation Model Training**
   - Collect and prepare training data
   - Implement contrastive learning pre-training
   - Evaluate embedding quality

2. **Production RAG Pipeline**
   - Full vector database implementation
   - Hybrid retrieval (semantic + keyword)
   - Integration with classification prompts

3. **Active Learning Infrastructure**
   - Sample selection algorithms
   - Human review interface
   - Feedback loop to model updates

### 4.3 Strategic Initiatives (6+ Months)

1. **End-to-End Foundation Model**
   - Full transformer architecture for dispute understanding
   - Multi-task learning across classification levels
   - Transfer learning from pre-trained models

2. **Real-Time Processing Pipeline**
   - Sub-500ms inference latency
   - Streaming classification for chat interfaces
   - Horizontal scaling infrastructure

3. **Cross-Network Generalization**
   - Single model handling all networks
   - Network-specific fine-tuning heads
   - Zero-shot classification for new codes

---

## Part 5: Key Takeaways from Stripe Radar Analysis

### 5.1 Architecture Lessons

1. **Simplification enables scaling.** Stripe's move from ensemble to pure DNN reduced training time by 85% while improving model quality. Don't assume complexity is necessary.

2. **Foundation models learn representations humans can't specify.** The Payments Foundation Model captures "hundreds of subtle signals" that feature engineering couldn't encode. Trust learned representations.

3. **Sequence-level reasoning unlocks new capabilities.** Treating transactions as sequences enabled detection of patterns invisible to individual-transaction classification.

### 5.2 Operational Lessons

1. **Explainability is non-negotiable in financial services.** Stripe built Risk Insights despite DNNs being harder to interpret. Plan for explainability from day one.

2. **Model freshness matters.** Stripe releases models multiple times per month. Build infrastructure for rapid iteration.

3. **Human-in-the-loop improves models over time.** Manual review creates labeled data for continuous improvement.

### 5.3 Strategic Lessons

1. **Domain-specific foundation models are emerging.** Stripe proved transformers work for payments; the same approach applies to disputes, claims, and other financial text.

2. **LLMs as interfaces AND engines.** Radar Assistant uses LLMs for rule creation while the foundation model uses transformers for classification. Both patterns are valuable.

3. **Hybrid approaches win.** The best systems combine embedding retrieval, LLM reasoning, and specialized classifiers.

---

## References

1. Stripe Engineering Blog: "How we built it: Stripe Radar" (March 2023)
2. Stripe Sessions 2024: "A Blueprint for AI Acceleration"
3. Stripe Sessions 2025: Payments Foundation Model Announcement
4. Stripe Documentation: Radar Risk Evaluation, Rules Reference
5. Gautam Kedia (Stripe Applied ML Lead): Twitter thread on Foundation Model architecture
6. Chris Skinner: "Moving from ML to LLM GPT in payments, Stripe sets the standard"
7. Stripe Blog: "Using AI to optimize payments performance with the Payments Intelligence Suite"
