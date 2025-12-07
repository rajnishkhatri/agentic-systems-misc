# Assembled Reformat (Pattern 30)

Separate content creation into two low-risk phases: (1) assemble facts deterministically, (2) reformat with LLM. Reduces hallucination risk while maintaining presentation quality.

## When to Use

- Content must be factually accurate (product specs, legal, medical)
- Presentation must be appealing (SEO, marketing, catalogs)
- Too many variations for Template Generation
- Source data exists in structured form (DB, documents, APIs)

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    PHASE 1: ASSEMBLE (Low Risk)                 │
├─────────────────────────────────────────────────────────────────┤
│  Database Query │ Document OCR │ RAG Retrieval │ Tool Calling   │
│                        ↓                                        │
│              Structured Data (verified facts)                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    PHASE 2: REFORMAT (Low Risk)                 │
├─────────────────────────────────────────────────────────────────┤
│  LLM Rewrite │ Summarize │ Rephrase │ Style Transfer            │
│                        ↓                                        │
│              Fluent Output (grounded in Phase 1 facts)          │
└─────────────────────────────────────────────────────────────────┘
```

## Key Insight

Reformatting tasks (rewrite, summarize, rephrase) have significantly lower hallucination rates than generation-from-scratch because the facts are already provided in context.

## Implementation

### Step 1: Define Assembled Content Schema

```python
from dataclasses import dataclass, field
from typing import List, Optional
from pydantic import BaseModel, Field

class AssembledContent(BaseModel):
    """Schema for assembled facts - all high-risk fields grounded."""
    
    # Critical fields (must be extracted, never generated)
    product_id: str = Field(description="Unique identifier from database")
    product_name: str = Field(description="Official product name")
    price: str = Field(description="Current price with currency")
    specifications: dict = Field(description="Technical specifications")
    
    # Medium-risk fields (extracted with validation)
    description: str = Field(description="Product description from source")
    warnings: List[str] = Field(description="Safety/regulatory warnings")
    
    # Low-risk fields (can be generated/enhanced)
    seo_keywords: Optional[List[str]] = None
    target_audience: Optional[str] = None
```

### Step 2: Assembly Functions

```python
from typing import Protocol, Any

class DataAssembler(Protocol):
    """Interface for data assembly sources."""
    def assemble(self, query: dict) -> AssembledContent: ...

class DatabaseAssembler:
    """Assemble from structured database."""
    def __init__(self, connection):
        self.conn = connection
    
    def assemble(self, query: dict) -> AssembledContent:
        row = self.conn.execute(
            "SELECT * FROM products WHERE id = ?", 
            [query["product_id"]]
        ).fetchone()
        return AssembledContent(
            product_id=row["id"],
            product_name=row["name"],
            price=f"${row['price']:.2f}",
            specifications=json.loads(row["specs"]),
            description=row["description"],
            warnings=json.loads(row["warnings"])
        )

class DocumentAssembler:
    """Assemble from documents using low-temperature extraction."""
    def __init__(self, llm_client, temperature: float = 0.0):
        self.llm = llm_client
        self.temp = temperature  # Low temp = lower hallucination
    
    def assemble(self, document: str) -> AssembledContent:
        prompt = f"""
Extract the following fields from this document.
Return ONLY information explicitly stated. Use "NOT_FOUND" if missing.

Document:
{document}

Extract:
- product_id
- product_name  
- price
- specifications (as JSON)
- description
- warnings (as list)
"""
        response = self.llm.complete(prompt, temperature=self.temp)
        return self._parse_response(response)

class RAGAssembler:
    """Assemble from RAG-retrieved chunks."""
    def __init__(self, retriever, llm_client):
        self.retriever = retriever
        self.llm = llm_client
    
    def assemble(self, query: str) -> AssembledContent:
        chunks = self.retriever.retrieve(query, top_k=5)
        # Combine chunks and extract with low temp
        combined = "\n---\n".join([c.text for c in chunks])
        return DocumentAssembler(self.llm, temperature=0.0).assemble(combined)
```

### Step 3: Reformat Functions

```python
class ContentReformatter:
    """Reformat assembled content for various purposes."""
    
    def __init__(self, llm_client):
        self.llm = llm_client
    
    def to_product_page(self, content: AssembledContent) -> str:
        """Reformat for SEO-optimized product page."""
        prompt = f"""
Reformat this product information into an SEO-optimized product page.
Use ONLY the facts provided - do not add any information.

Product Information:
{content.model_dump_json(indent=2)}

Requirements:
- Write compelling copy that highlights benefits
- Include all specifications exactly as provided
- Include all warnings verbatim
- Optimize for search engines
- Use markdown formatting

Output the product page:
"""
        return self.llm.complete(prompt, temperature=0.3)
    
    def to_comparison(self, contents: List[AssembledContent]) -> str:
        """Reformat multiple products into comparison table."""
        prompt = f"""
Create a comparison table for these products.
Use ONLY the facts provided - do not add any information.

Products:
{[c.model_dump_json(indent=2) for c in contents]}

Output a markdown comparison table:
"""
        return self.llm.complete(prompt, temperature=0.2)
    
    def to_email(self, content: AssembledContent, tone: str = "professional") -> str:
        """Reformat for email communication."""
        prompt = f"""
Write a {tone} email about this product.
Use ONLY the facts provided - do not add any information.

Product Information:
{content.model_dump_json(indent=2)}

Output the email:
"""
        return self.llm.complete(prompt, temperature=0.4)
```

### Step 4: Validation Pipeline

```python
class AssembledReformatPipeline:
    """Full pipeline with validation at each step."""
    
    def __init__(self, assembler: DataAssembler, reformatter: ContentReformatter):
        self.assembler = assembler
        self.reformatter = reformatter
    
    def execute(self, query: dict, output_format: str) -> dict:
        # Phase 1: Assemble
        assembled = self.assembler.assemble(query)
        assembly_validation = self._validate_assembly(assembled)
        
        if not assembly_validation["is_valid"]:
            return {"error": "Assembly failed", "details": assembly_validation}
        
        # Phase 2: Reformat
        if output_format == "product_page":
            output = self.reformatter.to_product_page(assembled)
        elif output_format == "email":
            output = self.reformatter.to_email(assembled)
        else:
            raise ValueError(f"Unknown format: {output_format}")
        
        # Validation: Check critical facts preserved
        reformat_validation = self._validate_reformat(assembled, output)
        
        return {
            "assembled": assembled.model_dump(),
            "output": output,
            "validation": {
                "assembly": assembly_validation,
                "reformat": reformat_validation
            }
        }
    
    def _validate_assembly(self, content: AssembledContent) -> dict:
        """Validate assembled content completeness."""
        errors = []
        if content.product_id == "NOT_FOUND":
            errors.append("Missing product_id")
        if content.price == "NOT_FOUND":
            errors.append("Missing price")
        return {"is_valid": len(errors) == 0, "errors": errors}
    
    def _validate_reformat(self, source: AssembledContent, output: str) -> dict:
        """Validate critical facts preserved in output."""
        checks = []
        
        # Price must appear exactly
        if source.price not in output:
            checks.append({"field": "price", "status": "missing"})
        else:
            checks.append({"field": "price", "status": "present"})
        
        # All warnings must appear
        for warning in source.warnings:
            if warning not in output:
                checks.append({"field": f"warning:{warning[:20]}", "status": "missing"})
        
        is_valid = all(c["status"] == "present" for c in checks)
        return {"is_valid": is_valid, "checks": checks}
```

## Risk Matrix by Field Type

| Field Type | Assembly Method | Reformat Freedom | Example |
|------------|-----------------|------------------|---------|
| **Critical** | DB/OCR only | None (verbatim) | Price, serial #, warnings |
| **Important** | DB/OCR + validation | Rephrase only | Specs, descriptions |
| **Flexible** | RAG/extraction | Full rewrite | Marketing copy |
| **Generated** | Can be LLM-created | Full freedom | SEO keywords |

## Example: Product Catalog

```python
# Catalog content for paper machine parts
class CatalogContent(BaseModel):
    part_name: str = Field(description="Common name of part")
    part_id: str = Field(description="Unique part id in catalog")
    part_description: str = Field(description="One paragraph description")
    failure_modes: List[str] = Field(description="Common reasons for replacement")
    warranty_period: int = Field(description="Years under warranty")
    price: str = Field(description="Price of part")

# Assembly from multiple sources
assembled = CatalogContent(
    part_name="wet_end",
    part_id="X34521PL",  # From database
    part_description="The wet end of a paper machine is...",  # From manual
    failure_modes=["Web breaks", "Uneven sheet formation", "Poor drainage"],  # From manual
    warranty_period=3,  # From database
    price="$23,295"  # From database
)

# Reformat constrains failure modes to only these three
# LLM cannot hallucinate additional failure modes
```

## When to Choose Assembled Reformat vs Template Generation

| Factor | Template Generation | Assembled Reformat |
|--------|---------------------|-------------------|
| Variation count | < 10,000 | Any |
| Human review | Required (one-time) | Optional |
| Runtime LLM calls | None | One (reformat) |
| Accuracy guarantee | Template-level | Validation-dependent |
| Presentation flexibility | Fixed | Dynamic |
