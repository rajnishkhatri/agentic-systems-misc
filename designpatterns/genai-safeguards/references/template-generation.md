# Template Generation (Pattern 29)

Reduce review burden by pre-generating templates that undergo one-time human review. Inference becomes deterministic string replacement.

## When to Use

- High-volume customer communications (thousands/day)
- Brand risk from hallucinated/toxic content is unacceptable
- Variations are enumerable (destinations × packages × languages)
- Human review per-item is cost-prohibitive

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    PREGENERATION PHASE (Offline)                │
├─────────────────────────────────────────────────────────────────┤
│  Enumerate Variations → LLM Generate → Human Review → Store DB  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    INFERENCE PHASE (Runtime)                    │
├─────────────────────────────────────────────────────────────────┤
│  Retrieve Template → Replace Placeholders → Send (No LLM call)  │
└─────────────────────────────────────────────────────────────────┘
```

## Implementation

### Step 1: Define Variation Dimensions

```python
from itertools import product
from dataclasses import dataclass
from typing import List

@dataclass
class TemplateVariation:
    dimensions: dict  # e.g., {"destination": [...], "package": [...], "lang": [...]}
    
    def enumerate(self) -> List[dict]:
        keys = self.dimensions.keys()
        values = self.dimensions.values()
        return [dict(zip(keys, combo)) for combo in product(*values)]
    
    @property
    def total_count(self) -> int:
        count = 1
        for v in self.dimensions.values():
            count *= len(v)
        return count
```

### Step 2: Generate Templates with Placeholders

```python
def create_template_prompt(variation: dict, placeholders: List[str]) -> str:
    """Generate prompt for template creation."""
    placeholder_instructions = "\n".join([
        f"- Use [{p}] to indicate where {p.lower().replace('_', ' ')} will be inserted"
        for p in placeholders
    ])
    
    return f"""
You are creating a template for a {variation.get('type', 'communication')}.
Context: {variation}

Requirements:
1. Write in {variation.get('language', 'English')}
2. Sound professional and on-brand
3. Include these placeholders exactly as shown:
{placeholder_instructions}

Generate the template content:
"""
```

### Step 3: Human Review Interface

```python
@dataclass
class ReviewableTemplate:
    variation: dict
    generated_content: str
    status: str = "pending"  # pending, approved, rejected, edited
    reviewed_content: str = None
    reviewer_notes: str = None
    
    def approve(self, edited_content: str = None, notes: str = None):
        self.status = "approved"
        self.reviewed_content = edited_content or self.generated_content
        self.reviewer_notes = notes
    
    def reject(self, notes: str):
        self.status = "rejected"
        self.reviewer_notes = notes
```

### Step 4: Inference-Time Replacement

```python
import re
from typing import Dict

class TemplateEngine:
    def __init__(self, template_store):
        self.store = template_store
    
    def render(self, variation_key: dict, replacements: Dict[str, str]) -> str:
        """Deterministic template rendering - no LLM call."""
        template = self.store.retrieve(variation_key)
        if not template:
            raise ValueError(f"No template for variation: {variation_key}")
        
        result = template.reviewed_content
        for placeholder, value in replacements.items():
            pattern = f"[{placeholder}]"
            if pattern not in result:
                raise ValueError(f"Placeholder {pattern} not found in template")
            result = result.replace(pattern, value)
        
        # Validate no unreplaced placeholders remain
        remaining = re.findall(r'\[([A-Z_]+)\]', result)
        if remaining:
            raise ValueError(f"Unreplaced placeholders: {remaining}")
        
        return result
```

## Placeholder Conventions

| Type | Pattern | Example |
|------|---------|---------|
| Names | `[CUSTOMER_NAME]`, `[AGENT_NAME]` | "Dear [CUSTOMER_NAME]" |
| Dates | `[DATE]`, `[DEADLINE]` | "by [DEADLINE]" |
| Amounts | `[AMOUNT]`, `[BALANCE]` | "$[AMOUNT]" |
| References | `[CASE_ID]`, `[ORDER_NUMBER]` | "Reference: [CASE_ID]" |

## Quality Checklist for Generated Templates

Before human review, auto-validate:

```python
def validate_template(template: str, required_placeholders: List[str]) -> List[str]:
    """Return list of validation errors."""
    errors = []
    
    # Check all required placeholders present
    for ph in required_placeholders:
        if f"[{ph}]" not in template:
            errors.append(f"Missing required placeholder: [{ph}]")
    
    # Check for common issues
    if len(template) < 100:
        errors.append("Template too short (< 100 chars)")
    if len(template) > 5000:
        errors.append("Template too long (> 5000 chars)")
    
    # Check for LLM artifacts
    artifacts = ["As an AI", "I cannot", "I'm sorry", "```"]
    for artifact in artifacts:
        if artifact in template:
            errors.append(f"Contains LLM artifact: '{artifact}'")
    
    return errors
```

## Scaling Considerations

| Templates | Human Review Time | Storage | Recommendation |
|-----------|-------------------|---------|----------------|
| < 100 | Hours | Minimal | Direct DB storage |
| 100-1000 | Days | ~1MB | Batch review workflows |
| 1000-10000 | Weeks | ~10MB | Tiered review (sample + ML assist) |
| > 10000 | Infeasible | Large | Consider Assembled Reformat instead |

## Multi-Language Support

```python
# Gender/grammatical considerations
LANGUAGE_CONFIG = {
    "Polish": {
        "has_grammatical_gender": True,
        "formal_variants": ["Szanowny Panie", "Szanowna Pani", "Szanowni Państwo"],
        "note": "Verb forms depend on speaker gender"
    },
    "German": {
        "has_grammatical_gender": True,
        "formal_variants": ["Sehr geehrter Herr", "Sehr geehrte Frau"],
        "note": "Sie/du distinction"
    },
    "English": {
        "has_grammatical_gender": False,
        "formal_variants": ["Dear"],
        "note": "Gender-neutral by default"
    }
}
```

## Error Handling

```python
class TemplateError(Exception):
    """Base exception for template operations."""
    pass

class TemplateNotFoundError(TemplateError):
    """Raised when template variation doesn't exist."""
    pass

class PlaceholderError(TemplateError):
    """Raised when placeholder replacement fails."""
    pass

class ValidationError(TemplateError):
    """Raised when template fails validation."""
    pass
```

## Integration with Dispute Resolution Systems

For financial services workflows (e.g., Bank of America dispute resolution):

```python
# Dispute-specific template dimensions
DISPUTE_TEMPLATES = {
    "dimensions": {
        "dispute_type": ["unauthorized_charge", "duplicate_charge", "merchandise_not_received"],
        "resolution": ["approved", "denied", "partial", "pending_info"],
        "channel": ["email", "sms", "letter"],
        "language": ["en", "es"]
    },
    "required_placeholders": [
        "CUSTOMER_NAME", "DISPUTE_ID", "AMOUNT", "MERCHANT_NAME", 
        "RESOLUTION_DATE", "NEXT_STEPS"
    ]
}
```
