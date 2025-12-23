# Hierarchical Classification Pipelines for Financial Dispute Resolution

LLM-based hierarchical classification systems can achieve **85-95% accuracy** on production taxonomies when combining retrieval-augmented prompting, structured outputs, and confidence-based routing. The most effective architecture for mapping natural language disputes to reason codes like your Visa 13.1 or Mastercard 4837 follows a three-stage pipeline: embedding-based candidate retrieval, chain-of-thought hierarchical classification, and self-consistency validation with human-in-the-loop fallbacks.

Production implementations at Stripe, Shopify, and healthcare coding systems demonstrate that hybrid approaches—combining fast embedding retrieval with LLM reasoning—outperform pure LLM classification while maintaining sub-100ms latency requirements. The key breakthrough enabling these systems is OpenAI's and Anthropic's structured output capabilities, which guarantee valid JSON schema compliance and eliminate parsing failures that plagued earlier implementations.

## E-commerce taxonomy architectures reveal proven patterns

Amazon's product classification system processes over **10,000 categories** using a dual-expert approach that directly applies to dispute classification. Their architecture combines a domain-specific fine-tuned model that generates top-K candidate categories with an LLM-based expert that uses prompting to analyze nuanced differences between candidates and select the optimal classification. This two-stage approach achieved breakthrough performance on e-commerce datasets by leveraging the strengths of both systems—the fine-tuned model's domain knowledge and the LLM's reasoning capabilities.

Shopify's evolution from TF-IDF logistic regression in 2018 to Vision Language Models in 2023 provides a roadmap for classification system maturation. Their current system processes **30 million predictions daily** with an **85% acceptance rate** for predicted categories, representing a 2x improvement in hierarchical precision over their previous neural network approach. Critical to their success was multi-LLM annotation for training data, using multiple models to annotate independently with an arbitration system for conflicting annotations and a human validation layer for edge cases.

The browse node structure used by Amazon, eBay, and Walmart shares common architectural principles with dispute reason code hierarchies. Products traverse from general to specific classifications (Shoes → Women's Shoes → Athletic Shoes → Running Shoes), mirroring your Network → reason_code_group → unified_category → specific_code structure. Multi-category assignment is supported—products can belong to multiple browse nodes simultaneously—which may be relevant for disputes that span fraud and processing error categories.

## Prompt engineering for hierarchical classification requires staged reasoning

Few-shot prompting research consistently shows that **the first 8 examples have the most impact**, with diminishing returns beyond 10 examples per class. For hierarchical systems, the optimal approach includes 1-3 examples per leaf-level category with additional examples demonstrating parent-child relationships. Quality matters more than quantity: algorithmic data curation to select diverse, representative examples outperforms random sampling.

Chain-of-thought prompting transforms classification accuracy for ambiguous cases. The technique works by requiring the model to reason through each hierarchy level before committing to a final classification. A dispute stating "I was charged for a subscription I canceled months ago" requires reasoning about whether this is fraud (unauthorized transaction), a consumer dispute (service not provided), or a processing error (failed cancellation). Zero-shot chain-of-thought prompting—simply adding "Let's work through this step-by-step" to the prompt—improves performance on complex classification tasks, though the technique works best with models containing **100B+ parameters**.

The most effective hierarchical classification structure uses top-down prompt chaining across three stages. Stage one extracts key information (complaint type, financial impact, entities involved) into structured JSON. Stage two assigns the Level 1 category using the extracted information plus retrieved context. Stage three determines the specific classification code given the established hierarchy path. This approach improves transparency and debuggability, allows each stage to be optimized independently, and reduces error propagation by validating at each step. Research on legal document classification showed prompt chaining surpassed ChatGPT zero-shot performance using smaller models.

## Retrieval-augmented classification scales to large taxonomies

RAG-based classification addresses a fundamental limitation of pure prompting: context window constraints when taxonomies contain hundreds of codes with detailed descriptions. The architecture embeds both the incoming dispute and all taxonomy entries (code descriptions, classification criteria, historical examples) into a vector database. At classification time, the system retrieves the top-5 most similar taxonomy codes plus 3 similar historical disputes, then augments the classification prompt with this retrieved context.

The Class-RAG approach from academic research retrieves both positive and negative examples—similar disputes that received the candidate classification alongside similar disputes that were classified differently. This contrastive context helps models distinguish between close categories, critical for differentiating between Visa reason codes 13.1 (merchandise/services not received) and 13.3 (merchandise/services not as described).

Implementation follows a clear pattern: index taxonomy entries and historical classified disputes using sentence transformers (all-MiniLM-L6-v2 or similar), store in a vector database (Pinecone for managed scalability, ChromaDB for local deployment), retrieve top-K candidates at classification time, then construct an augmented prompt that includes the relevant taxonomy definitions and similar past disputes. Benefits include dynamic taxonomy updates without retraining, handling of new dispute types by similarity to existing patterns, and transparency about which examples influenced the decision.

## Production systems reveal critical architecture decisions

Stripe's Radar fraud detection system provides the most detailed public documentation of financial classification at scale. Their architecture processes **1,000+ transaction characteristics** with decision latency under **100 milliseconds** and a false positive rate of only **0.1%**. Key architectural decisions included migrating from a Wide & Deep ensemble (XGBoost + DNN) to a pure DNN-only architecture using multi-branch design inspired by ResNeXt. Removing XGBoost would have caused a 1.5% drop in recall, but finding the right DNN architecture recovered this performance while reducing training time by **85%**.

Stripe's risk insights feature demonstrates the importance of explainability in financial classification. They built a secondary model specifically to explain decisions to users—for disputes, this translates to showing which factors drove the classification (transaction amount, merchant category, customer history, timing patterns). This creates audit trails essential for regulatory compliance and dispute resolution.

Healthcare ICD-10 coding systems face remarkably similar challenges to dispute classification: mapping unstructured clinical notes to hierarchical code taxonomies with thousands of leaf codes. The LLM Tree-Search method navigates the ICD-10 hierarchical structure without task-specific training by having the LLM select relevant branches at each decision point based on text descriptions, recursively traversing until candidate paths are exhausted. This approach achieved better performance on rare codes compared to prompt-based approaches—highly relevant for infrequent dispute reason codes.

Customer service classification systems from Zendesk and Intercom report **up to 45% reduction in response times** with AI-powered ticket classification and resolution rates of **66%+** for AI agents. Salesforce Einstein Case Classification retrains models every **30 days** automatically, a cadence worth considering for dispute classification systems where patterns evolve with fraud trends and regulatory changes.

## Structured outputs eliminate parsing failures in classification pipelines

OpenAI's structured outputs feature, launched in August 2024, guarantees **100% schema compliance**—up from 35% with prompting alone. For classification pipelines, this eliminates an entire category of production failures where models return malformed JSON or invalid category codes. The implementation uses Pydantic models with the `response_format` parameter:

```python
class DisputeClassification(BaseModel):
    network: Literal["visa", "mastercard", "amex", "discover", "paypal"]
    reason_code_group: str
    unified_category: str
    specific_code: str
    confidence: float
    reasoning: str
```

Setting `strict: True` and using enums to constrain categories ensures the model can only output valid taxonomy codes. This approach requires models `gpt-4o-mini` or `gpt-4o-2024-08-06` or later.

Anthropic's Claude uses XML tags for structured classification with similar effectiveness. The pattern uses `<task>`, `<categories>`, `<rules>`, and `<examples>` tags to organize classification prompts, with prefilling the assistant response (`"assistant": "Category: "`) to constrain output format. For complex classification requiring reasoning, Claude's pattern wraps thinking in `<thinking>` tags followed by `<classification>` tags for the final output.

LangChain's `with_structured_output()` method provides framework-agnostic structured classification across OpenAI, Anthropic, and open-source models. DSPy offers automatic prompt optimization through BootstrapFewShot, which algorithmically selects optimal few-shot examples from training data—particularly valuable when you have historical classified disputes but limited prompt engineering resources.

## Confidence scoring requires calibration and multi-tier routing

Raw LLM confidence scores are systematically **overconfident** and require calibration before use in production routing decisions. The most reliable confidence estimation uses token-level log probabilities (logprobs) rather than asking the model to self-report confidence. Self-consistency—running the same classification prompt multiple times with temperature > 0 and using majority voting—provides both the final classification and a consistency-based confidence score.

Implementation follows a three-tier routing pattern based on calibrated confidence. High confidence (>0.85) classifications are auto-approved. Medium confidence (0.5-0.85) routes to a human review queue with model reasoning displayed. Low confidence (<0.5) triggers escalation with the sample flagged for active learning. The specific thresholds should be tuned using precision-recall curves on held-out validation data, considering the business costs of false positives versus false negatives—for disputes, missing a legitimate dispute (false negative) typically carries higher regulatory and customer satisfaction costs.

Post-hoc calibration using isotonic regression on validation data significantly improves confidence reliability. The process involves collecting confidence scores and correctness labels on a validation set, training an isotonic regression model to map raw confidences to calibrated probabilities, then applying this transformation to production predictions. This approach addresses the systematic overconfidence that makes uncalibrated LLM scores unreliable for routing decisions.

## Human-in-the-loop patterns optimize accuracy and labeling efficiency

Active learning from human corrections follows uncertainty sampling as the dominant strategy: select samples with lowest model confidence for human review. This approach maximizes information gained per labeled sample. The ActiveLab method from Cleanlab research achieved **90% accuracy at 35% of standard labeling cost** by intelligently selecting which samples to label.

The practical workflow deploys the initial classifier, routes low-confidence samples to a review queue, has humans annotate selected samples, retrains with new labels, monitors accuracy on a validation set, and stops when marginal accuracy gains diminish below 1%. Review queue design should prioritize by uncertainty, display model reasoning, batch similar items for efficient review, and track inter-annotator agreement to flag cases where multiple reviewers disagree.

Escalation triggers should include confidence below category-specific thresholds, disagreement between primary and secondary classification attempts, input length or complexity anomalies, and high-stakes categories requiring regulatory compliance (certain fraud classifications may have legal implications). The human-in-the-loop component creates the audit trail essential for financial services compliance and enables continuous improvement as new dispute patterns emerge.

## Evaluation metrics must account for hierarchical structure

Standard classification metrics treat all errors equally, but hierarchical systems should penalize predicting "fraud" when the true label is "authorization error" more heavily than predicting the wrong specific fraud code within the fraud category. Hierarchical precision, recall, and F1 metrics account for partial credit when predictions match ancestors in the taxonomy—predicting the correct reason_code_group even when missing the exact specific_code represents partial success.

Level-wise metrics computed separately at each hierarchy level identify where the model struggles. A system might achieve 95% accuracy at the Network level but only 78% at the specific_code level, indicating that finer-grained training data or more detailed classification prompts are needed at lower hierarchy levels. Category distance metrics measure the shortest path between predicted and true classes in the hierarchy tree, providing a continuous measure of error severity.

Benchmarking should maintain a "golden" test set with consensus labels from multiple subject matter experts, use stratified sampling preserving hierarchy distribution, test on held-out categories to assess generalization to new reason codes, and track per-category performance separately to catch degradation in specific dispute types before overall metrics decline.

## Prompt versioning and monitoring prevent production regressions

Production classification systems require prompt versioning with A/B testing capability. Tools like Langfuse, PromptLayer, and Braintrust provide version control for prompts with performance tracking across versions. The implementation pattern labels prompt versions (prod-a, prod-b), randomly assigns traffic, and tracks classification accuracy, latency, and cost per version. Starting with 20-50 representative test cases covering common scenarios and edge cases provides sufficient signal for prompt iteration.

Monitoring classification drift requires tracking the distribution of predictions over time, confidence score trends (declining average confidence signals drift), escalation rate changes (sudden increases in human review needs), and category-specific accuracy. Alerting thresholds should flag when category distribution shifts more than 10% from baseline or when the "other" category growth rate exceeds historical norms—high "other" rates above 15-20% indicate taxonomy gaps requiring review.

## Recommended architecture for financial dispute classification

The optimal architecture combines the patterns from this research into a four-stage pipeline:

**Stage 1 - Information Extraction**: A structured output prompt extracts complaint type, entities, amounts, dates, and key phrases from the raw dispute text into JSON format.

**Stage 2 - RAG Retrieval**: The dispute embedding retrieves top-5 similar taxonomy codes plus 3 similar historical disputes from the vector database.

**Stage 3 - Hierarchical Classification**: A chain-of-thought prompt classifies top-down through Network → reason_code_group → unified_category → specific_code, including retrieved context and requiring step-by-step reasoning.

**Stage 4 - Validation and Routing**: Self-consistency validation runs classification 3-5 times, calculates consistency as confidence, and routes based on three-tier thresholds to auto-approval, human review, or escalation.

This architecture handles your complete taxonomy from Networks (Visa, Mastercard, Amex, Discover, PayPal) through reason_code_groups (authorization, fraud, processing_errors, cardholder_disputes) to unified_categories (fraudulent, product_not_received, duplicate) to specific codes (visa 13.1, mastercard 4837, amex C02). The embedding retrieval stage ensures scalability as your taxonomy grows, while structured outputs guarantee valid code assignments and the human-in-the-loop component provides the audit trail required for financial services compliance.

## Conclusion

Building production-grade hierarchical classification for dispute resolution requires moving beyond simple prompting to orchestrated pipelines. The dual-expert pattern from Amazon—combining retrieval-based candidate generation with LLM reasoning—directly applies to mapping customer complaints to reason codes. Structured outputs from OpenAI and Anthropic solve the parsing reliability problem that blocked earlier implementations. Confidence calibration and three-tier routing balance automation efficiency with accuracy requirements.

The critical implementation decisions are threshold tuning based on business costs (false negative costs typically exceed false positive costs in dispute handling), prompt versioning with rollback capability, and active learning infrastructure to capture value from human corrections. Systems achieving 85%+ accuracy in production combine these elements with monitoring that catches drift before customers notice degradation. Start with the staged pipeline architecture, instrument confidence distributions from day one, and plan for quarterly taxonomy reviews based on clustering of "other" classifications.