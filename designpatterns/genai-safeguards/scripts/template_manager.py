#!/usr/bin/env python3
"""
Template Manager - Utility functions for Template Generation pattern.
Framework-agnostic, invokable by any agent.

Usage:
    from template_manager import TemplateManager
    
    manager = TemplateManager(storage_backend)
    template = manager.create(variation, placeholders, llm_client)
    rendered = manager.render(variation_key, replacements)
"""

import re
import json
import hashlib
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Protocol
from itertools import product


# ============================================================================
# Data Models
# ============================================================================

@dataclass
class TemplateVariation:
    """Defines dimensions for template enumeration."""
    dimensions: Dict[str, List[str]]
    
    def enumerate(self) -> List[Dict[str, str]]:
        """Generate all combinations of dimensions."""
        keys = list(self.dimensions.keys())
        values = [self.dimensions[k] for k in keys]
        return [dict(zip(keys, combo)) for combo in product(*values)]
    
    @property
    def total_count(self) -> int:
        """Total number of template variations."""
        count = 1
        for v in self.dimensions.values():
            count *= len(v)
        return count
    
    def to_key(self, variation: Dict[str, str]) -> str:
        """Generate unique key for a variation."""
        sorted_items = sorted(variation.items())
        return hashlib.md5(json.dumps(sorted_items).encode()).hexdigest()[:12]


@dataclass
class Template:
    """A reviewable template with metadata."""
    variation_key: str
    variation: Dict[str, str]
    generated_content: str
    placeholders: List[str]
    status: str = "pending"  # pending, approved, rejected, edited
    reviewed_content: Optional[str] = None
    reviewer_notes: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    reviewed_at: Optional[datetime] = None
    
    @property
    def content(self) -> str:
        """Return reviewed content if available, else generated."""
        return self.reviewed_content or self.generated_content
    
    def approve(self, edited_content: Optional[str] = None, notes: Optional[str] = None):
        """Mark template as approved."""
        self.status = "approved"
        self.reviewed_content = edited_content or self.generated_content
        self.reviewer_notes = notes
        self.reviewed_at = datetime.utcnow()
    
    def reject(self, notes: str):
        """Mark template as rejected."""
        self.status = "rejected"
        self.reviewer_notes = notes
        self.reviewed_at = datetime.utcnow()
    
    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "variation_key": self.variation_key,
            "variation": self.variation,
            "generated_content": self.generated_content,
            "placeholders": self.placeholders,
            "status": self.status,
            "reviewed_content": self.reviewed_content,
            "reviewer_notes": self.reviewer_notes,
            "created_at": self.created_at.isoformat(),
            "reviewed_at": self.reviewed_at.isoformat() if self.reviewed_at else None,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Template":
        """Deserialize from dictionary."""
        data["created_at"] = datetime.fromisoformat(data["created_at"])
        if data.get("reviewed_at"):
            data["reviewed_at"] = datetime.fromisoformat(data["reviewed_at"])
        return cls(**data)


@dataclass
class RenderResult:
    """Result of template rendering."""
    success: bool
    content: Optional[str] = None
    error: Optional[str] = None
    template_key: Optional[str] = None
    replacements_applied: Optional[Dict[str, str]] = None


# ============================================================================
# Storage Backends (Protocol for dependency injection)
# ============================================================================

class StorageBackend(Protocol):
    """Interface for template storage."""
    
    def save(self, template: Template) -> None: ...
    def get(self, variation_key: str) -> Optional[Template]: ...
    def list_all(self) -> List[Template]: ...
    def delete(self, variation_key: str) -> bool: ...


class InMemoryStorage:
    """Simple in-memory storage for testing."""
    
    def __init__(self):
        self._templates: Dict[str, Template] = {}
    
    def save(self, template: Template) -> None:
        self._templates[template.variation_key] = template
    
    def get(self, variation_key: str) -> Optional[Template]:
        return self._templates.get(variation_key)
    
    def list_all(self) -> List[Template]:
        return list(self._templates.values())
    
    def delete(self, variation_key: str) -> bool:
        if variation_key in self._templates:
            del self._templates[variation_key]
            return True
        return False


class JSONFileStorage:
    """File-based JSON storage."""
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        self._load()
    
    def _load(self):
        try:
            with open(self.filepath, 'r') as f:
                data = json.load(f)
                self._templates = {k: Template.from_dict(v) for k, v in data.items()}
        except FileNotFoundError:
            self._templates = {}
    
    def _persist(self):
        with open(self.filepath, 'w') as f:
            json.dump({k: v.to_dict() for k, v in self._templates.items()}, f, indent=2)
    
    def save(self, template: Template) -> None:
        self._templates[template.variation_key] = template
        self._persist()
    
    def get(self, variation_key: str) -> Optional[Template]:
        return self._templates.get(variation_key)
    
    def list_all(self) -> List[Template]:
        return list(self._templates.values())
    
    def delete(self, variation_key: str) -> bool:
        if variation_key in self._templates:
            del self._templates[variation_key]
            self._persist()
            return True
        return False


# ============================================================================
# LLM Interface (Protocol for dependency injection)
# ============================================================================

class LLMClient(Protocol):
    """Interface for LLM calls."""
    
    def complete(self, prompt: str, **kwargs) -> str: ...


# ============================================================================
# Template Manager
# ============================================================================

class TemplateManager:
    """
    Main interface for Template Generation pattern.
    
    Usage:
        storage = JSONFileStorage("templates.json")
        manager = TemplateManager(storage)
        
        # Create template
        template = manager.create(
            variation={"lang": "English", "type": "welcome"},
            placeholders=["CUSTOMER_NAME", "PRODUCT"],
            llm_client=my_llm,
            prompt_template="Write a {type} email in {lang}..."
        )
        
        # After human review
        manager.approve(template.variation_key)
        
        # Render at inference time
        result = manager.render(
            variation_key=template.variation_key,
            replacements={"CUSTOMER_NAME": "John", "PRODUCT": "Widget"}
        )
    """
    
    def __init__(self, storage: StorageBackend):
        self.storage = storage
    
    def create(
        self,
        variation: Dict[str, str],
        placeholders: List[str],
        llm_client: LLMClient,
        prompt_template: Optional[str] = None,
        **llm_kwargs
    ) -> Template:
        """
        Generate a new template using LLM.
        
        Args:
            variation: Dict of dimension values (e.g., {"lang": "English", "type": "welcome"})
            placeholders: List of placeholder names (e.g., ["CUSTOMER_NAME"])
            llm_client: LLM client implementing complete() method
            prompt_template: Optional custom prompt (uses default if not provided)
            **llm_kwargs: Additional arguments passed to LLM
        
        Returns:
            Template object (status="pending" until reviewed)
        """
        prompt = prompt_template or self._default_prompt(variation, placeholders)
        generated_content = llm_client.complete(prompt, **llm_kwargs)
        
        # Validate generated content
        validation = self.validate(generated_content, placeholders)
        if validation["errors"]:
            # Still create but with warning
            generated_content = f"[VALIDATION WARNINGS: {validation['errors']}]\n\n{generated_content}"
        
        variation_def = TemplateVariation(dimensions={k: [v] for k, v in variation.items()})
        key = variation_def.to_key(variation)
        
        template = Template(
            variation_key=key,
            variation=variation,
            generated_content=generated_content,
            placeholders=placeholders,
        )
        
        self.storage.save(template)
        return template
    
    def _default_prompt(self, variation: Dict[str, str], placeholders: List[str]) -> str:
        """Generate default prompt for template creation."""
        placeholder_instructions = "\n".join([
            f"- Use [{p}] exactly where {p.lower().replace('_', ' ')} should be inserted"
            for p in placeholders
        ])
        
        context = ", ".join([f"{k}={v}" for k, v in variation.items()])
        
        return f"""
Create a template with the following context: {context}

Requirements:
1. Write professional, on-brand content
2. Include these placeholders exactly as shown:
{placeholder_instructions}

3. Do not include any AI assistant phrases like "As an AI" or "I cannot"
4. Keep the tone appropriate for the context

Generate the template:
"""
    
    def validate(self, content: str, required_placeholders: List[str]) -> Dict[str, Any]:
        """
        Validate template content.
        
        Returns:
            {"is_valid": bool, "errors": List[str], "warnings": List[str]}
        """
        errors = []
        warnings = []
        
        # Check required placeholders
        for ph in required_placeholders:
            pattern = f"[{ph}]"
            count = content.count(pattern)
            if count == 0:
                errors.append(f"Missing required placeholder: {pattern}")
            elif count > 1:
                warnings.append(f"Placeholder {pattern} appears {count} times")
        
        # Check length
        if len(content) < 50:
            errors.append("Template too short (< 50 chars)")
        if len(content) > 10000:
            warnings.append("Template is very long (> 10000 chars)")
        
        # Check for LLM artifacts
        artifacts = [
            "As an AI", "As a language model", "I cannot", "I'm sorry",
            "```", "###", "I'd be happy to"
        ]
        for artifact in artifacts:
            if artifact.lower() in content.lower():
                errors.append(f"Contains LLM artifact: '{artifact}'")
        
        # Check for unreplaced test data
        test_patterns = [r"John Doe", r"Jane Doe", r"example\.com", r"123-456-7890"]
        for pattern in test_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                warnings.append(f"Contains possible test data matching: {pattern}")
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    def approve(
        self,
        variation_key: str,
        edited_content: Optional[str] = None,
        notes: Optional[str] = None
    ) -> bool:
        """Approve a template after human review."""
        template = self.storage.get(variation_key)
        if not template:
            return False
        
        template.approve(edited_content, notes)
        self.storage.save(template)
        return True
    
    def reject(self, variation_key: str, notes: str) -> bool:
        """Reject a template."""
        template = self.storage.get(variation_key)
        if not template:
            return False
        
        template.reject(notes)
        self.storage.save(template)
        return True
    
    def render(
        self,
        variation_key: str,
        replacements: Dict[str, str],
        strict: bool = True
    ) -> RenderResult:
        """
        Render a template with placeholder replacements.
        
        This is the inference-time operation - NO LLM CALLS.
        
        Args:
            variation_key: Key identifying the template variation
            replacements: Dict mapping placeholder names to values
            strict: If True, fail on unreplaced placeholders
        
        Returns:
            RenderResult with success status and content
        """
        template = self.storage.get(variation_key)
        
        if not template:
            return RenderResult(
                success=False,
                error=f"Template not found: {variation_key}"
            )
        
        if template.status != "approved":
            return RenderResult(
                success=False,
                error=f"Template not approved (status={template.status})"
            )
        
        content = template.content
        applied = {}
        
        # Replace placeholders
        for placeholder, value in replacements.items():
            pattern = f"[{placeholder}]"
            if pattern in content:
                content = content.replace(pattern, str(value))
                applied[placeholder] = value
        
        # Check for unreplaced placeholders
        remaining = re.findall(r'\[([A-Z_]+)\]', content)
        
        if remaining and strict:
            return RenderResult(
                success=False,
                error=f"Unreplaced placeholders: {remaining}",
                template_key=variation_key
            )
        
        return RenderResult(
            success=True,
            content=content,
            template_key=variation_key,
            replacements_applied=applied
        )
    
    def bulk_create(
        self,
        variations: TemplateVariation,
        placeholders: List[str],
        llm_client: LLMClient,
        prompt_template: Optional[str] = None,
        progress_callback: Optional[callable] = None
    ) -> Dict[str, Template]:
        """
        Generate templates for all variation combinations.
        
        Args:
            variations: TemplateVariation defining all dimensions
            placeholders: Common placeholders for all templates
            llm_client: LLM client
            prompt_template: Custom prompt template
            progress_callback: Optional callback(current, total, template)
        
        Returns:
            Dict mapping variation_key -> Template
        """
        all_variations = variations.enumerate()
        total = len(all_variations)
        results = {}
        
        for i, variation in enumerate(all_variations):
            template = self.create(
                variation=variation,
                placeholders=placeholders,
                llm_client=llm_client,
                prompt_template=prompt_template
            )
            results[template.variation_key] = template
            
            if progress_callback:
                progress_callback(i + 1, total, template)
        
        return results
    
    def get_review_queue(self) -> List[Template]:
        """Get all templates pending review."""
        return [t for t in self.storage.list_all() if t.status == "pending"]
    
    def get_stats(self) -> Dict[str, int]:
        """Get template statistics."""
        templates = self.storage.list_all()
        return {
            "total": len(templates),
            "pending": sum(1 for t in templates if t.status == "pending"),
            "approved": sum(1 for t in templates if t.status == "approved"),
            "rejected": sum(1 for t in templates if t.status == "rejected"),
        }


# ============================================================================
# Convenience Functions
# ============================================================================

def quick_render(template_content: str, replacements: Dict[str, str]) -> str:
    """
    Quick template rendering without storage.
    
    Usage:
        result = quick_render(
            "Hello [NAME], your order [ORDER_ID] is ready.",
            {"NAME": "Alice", "ORDER_ID": "12345"}
        )
    """
    content = template_content
    for placeholder, value in replacements.items():
        content = content.replace(f"[{placeholder}]", str(value))
    return content


if __name__ == "__main__":
    # Example usage
    storage = InMemoryStorage()
    manager = TemplateManager(storage)
    
    print("Template Manager initialized.")
    print("Use manager.create(), manager.approve(), manager.render()")
