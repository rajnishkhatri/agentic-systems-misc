#!/usr/bin/env python3
"""
Content Assembler - Utility functions for Assembled Reformat pattern.
Framework-agnostic, invokable by any agent.

Two-phase content creation:
1. ASSEMBLE: Gather facts from trusted sources (DB, OCR, RAG)
2. REFORMAT: Use LLM to present facts appealingly

Usage:
    from content_assembler import AssembledReformatPipeline, DatabaseAssembler
    
    pipeline = AssembledReformatPipeline(
        assembler=DatabaseAssembler(connection),
        reformatter=ContentReformatter(llm_client)
    )
    result = pipeline.execute(query, output_format="product_page")
"""

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Protocol, Union
from enum import Enum


# ============================================================================
# Data Models
# ============================================================================

class FieldRisk(Enum):
    """Risk level for content fields."""
    CRITICAL = "critical"    # Must be verbatim (price, serial #, warnings)
    IMPORTANT = "important"  # Can be rephrased, not invented
    FLEXIBLE = "flexible"    # Can be enhanced/rewritten
    GENERATED = "generated"  # Can be LLM-created


@dataclass
class AssembledField:
    """A field with its value and metadata."""
    name: str
    value: Any
    risk_level: FieldRisk
    source: str  # e.g., "database", "ocr", "rag", "llm"
    confidence: float = 1.0  # 0.0-1.0


@dataclass
class AssembledContent:
    """Container for assembled facts from multiple sources."""
    fields: Dict[str, AssembledField]
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get(self, name: str, default: Any = None) -> Any:
        """Get field value by name."""
        field = self.fields.get(name)
        return field.value if field else default
    
    def get_critical_fields(self) -> Dict[str, AssembledField]:
        """Get all critical-risk fields."""
        return {k: v for k, v in self.fields.items() if v.risk_level == FieldRisk.CRITICAL}
    
    def to_context_string(self) -> str:
        """Format for LLM context."""
        lines = []
        for name, field in self.fields.items():
            if isinstance(field.value, list):
                value_str = ", ".join(str(v) for v in field.value)
            elif isinstance(field.value, dict):
                value_str = json.dumps(field.value, indent=2)
            else:
                value_str = str(field.value)
            lines.append(f"{name}: {value_str}")
        return "\n".join(lines)
    
    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "fields": {k: {
                "value": v.value,
                "risk_level": v.risk_level.value,
                "source": v.source,
                "confidence": v.confidence
            } for k, v in self.fields.items()},
            "metadata": self.metadata
        }


@dataclass
class ReformatResult:
    """Result of content reformatting."""
    success: bool
    content: Optional[str] = None
    error: Optional[str] = None
    validation: Optional[Dict[str, Any]] = None
    source_content: Optional[AssembledContent] = None


@dataclass
class PipelineResult:
    """Complete pipeline result with both phases."""
    success: bool
    assembled: Optional[AssembledContent] = None
    reformatted: Optional[str] = None
    assembly_validation: Optional[Dict[str, Any]] = None
    reformat_validation: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


# ============================================================================
# Assembler Interface and Implementations
# ============================================================================

class DataAssembler(ABC):
    """Base class for data assembly from various sources."""
    
    @abstractmethod
    def assemble(self, query: Dict[str, Any]) -> AssembledContent:
        """Assemble data from source."""
        pass


class DatabaseAssembler(DataAssembler):
    """Assemble from structured database queries."""
    
    def __init__(self, connection, field_mapping: Dict[str, FieldRisk]):
        """
        Args:
            connection: Database connection with execute() method
            field_mapping: Maps field names to risk levels
        """
        self.conn = connection
        self.field_mapping = field_mapping
    
    def assemble(self, query: Dict[str, Any]) -> AssembledContent:
        """
        Assemble from database.
        
        Args:
            query: {"sql": "SELECT ...", "params": [...]} or {"table": ..., "id": ...}
        """
        if "sql" in query:
            result = self.conn.execute(query["sql"], query.get("params", []))
        else:
            # Simple lookup
            table = query.get("table")
            id_field = query.get("id_field", "id")
            id_value = query.get("id")
            result = self.conn.execute(
                f"SELECT * FROM {table} WHERE {id_field} = ?",
                [id_value]
            )
        
        row = result.fetchone()
        if not row:
            return AssembledContent(fields={}, metadata={"error": "No data found"})
        
        fields = {}
        for col_name in row.keys():
            risk = self.field_mapping.get(col_name, FieldRisk.FLEXIBLE)
            fields[col_name] = AssembledField(
                name=col_name,
                value=row[col_name],
                risk_level=risk,
                source="database",
                confidence=1.0  # DB data is high confidence
            )
        
        return AssembledContent(fields=fields)


class DocumentAssembler(DataAssembler):
    """Assemble from documents using low-temperature LLM extraction."""
    
    def __init__(
        self,
        llm_client,
        extraction_schema: Dict[str, FieldRisk],
        temperature: float = 0.0
    ):
        """
        Args:
            llm_client: LLM client with complete() method
            extraction_schema: Fields to extract and their risk levels
            temperature: LLM temperature (lower = less hallucination)
        """
        self.llm = llm_client
        self.schema = extraction_schema
        self.temperature = temperature
    
    def assemble(self, query: Dict[str, Any]) -> AssembledContent:
        """
        Extract structured data from document.
        
        Args:
            query: {"document": "document text content"}
        """
        document = query.get("document", "")
        
        schema_desc = "\n".join([
            f"- {name}: (required)" if risk == FieldRisk.CRITICAL else f"- {name}: (optional)"
            for name, risk in self.schema.items()
        ])
        
        prompt = f"""
Extract the following fields from this document.
Return ONLY information explicitly stated. Use "NOT_FOUND" for missing fields.
Return as valid JSON.

Fields to extract:
{schema_desc}

Document:
{document}

JSON output:
"""
        
        response = self.llm.complete(prompt, temperature=self.temperature)
        
        try:
            extracted = json.loads(response.strip())
        except json.JSONDecodeError:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{[^{}]*\}', response, re.DOTALL)
            if json_match:
                extracted = json.loads(json_match.group())
            else:
                return AssembledContent(
                    fields={},
                    metadata={"error": "Failed to parse extraction result"}
                )
        
        fields = {}
        for name, risk in self.schema.items():
            value = extracted.get(name, "NOT_FOUND")
            fields[name] = AssembledField(
                name=name,
                value=value,
                risk_level=risk,
                source="document_extraction",
                confidence=0.9 if value != "NOT_FOUND" else 0.0
            )
        
        return AssembledContent(fields=fields)


class RAGAssembler(DataAssembler):
    """Assemble from RAG-retrieved chunks."""
    
    def __init__(self, retriever, llm_client, extraction_schema: Dict[str, FieldRisk]):
        """
        Args:
            retriever: Retriever with retrieve(query, top_k) method
            llm_client: LLM client for extraction
            extraction_schema: Fields to extract
        """
        self.retriever = retriever
        self.llm = llm_client
        self.schema = extraction_schema
    
    def assemble(self, query: Dict[str, Any]) -> AssembledContent:
        """
        Retrieve and extract from RAG chunks.
        
        Args:
            query: {"query": "search query", "top_k": 5}
        """
        search_query = query.get("query", "")
        top_k = query.get("top_k", 5)
        
        chunks = self.retriever.retrieve(search_query, top_k=top_k)
        combined = "\n---\n".join([c.text for c in chunks])
        
        # Use DocumentAssembler for extraction
        doc_assembler = DocumentAssembler(
            self.llm,
            self.schema,
            temperature=0.0
        )
        
        result = doc_assembler.assemble({"document": combined})
        
        # Update source to reflect RAG
        for field in result.fields.values():
            field.source = "rag_extraction"
        
        return result


class CompositeAssembler(DataAssembler):
    """Combine multiple assemblers with field prioritization."""
    
    def __init__(self, assemblers: List[tuple]):
        """
        Args:
            assemblers: List of (assembler, fields_to_use) tuples
                        e.g., [(db_assembler, ["id", "price"]), (doc_assembler, ["description"])]
        """
        self.assemblers = assemblers
    
    def assemble(self, query: Dict[str, Any]) -> AssembledContent:
        """Assemble from multiple sources with field routing."""
        all_fields = {}
        
        for assembler, field_names in self.assemblers:
            result = assembler.assemble(query)
            for name in field_names:
                if name in result.fields:
                    all_fields[name] = result.fields[name]
        
        return AssembledContent(fields=all_fields)


# ============================================================================
# Reformatter
# ============================================================================

class ContentReformatter:
    """Reformat assembled content for various output formats."""
    
    def __init__(self, llm_client, temperature: float = 0.3):
        self.llm = llm_client
        self.temperature = temperature
    
    def reformat(
        self,
        content: AssembledContent,
        output_format: str,
        custom_instructions: Optional[str] = None
    ) -> ReformatResult:
        """
        Reformat content for specified output format.
        
        Args:
            content: AssembledContent with facts to include
            output_format: One of "product_page", "email", "summary", "comparison", "custom"
            custom_instructions: Required if output_format is "custom"
        """
        # Build constraint instructions for critical fields
        critical_fields = content.get_critical_fields()
        constraints = []
        for name, field in critical_fields.items():
            constraints.append(f"- {name} must appear exactly as: {field.value}")
        
        constraint_text = ""
        if constraints:
            constraint_text = f"""
CRITICAL: These values must appear EXACTLY as shown (do not modify):
{chr(10).join(constraints)}
"""
        
        # Get format-specific prompt
        format_prompts = {
            "product_page": self._product_page_prompt,
            "email": self._email_prompt,
            "summary": self._summary_prompt,
            "comparison": self._comparison_prompt,
        }
        
        if output_format == "custom":
            if not custom_instructions:
                return ReformatResult(
                    success=False,
                    error="custom_instructions required for custom format"
                )
            prompt = self._custom_prompt(content, custom_instructions, constraint_text)
        elif output_format in format_prompts:
            prompt = format_prompts[output_format](content, constraint_text)
        else:
            return ReformatResult(
                success=False,
                error=f"Unknown output format: {output_format}"
            )
        
        reformatted = self.llm.complete(prompt, temperature=self.temperature)
        
        # Validate critical fields preserved
        validation = self._validate_preservation(content, reformatted)
        
        return ReformatResult(
            success=validation["is_valid"],
            content=reformatted,
            validation=validation,
            source_content=content,
            error=None if validation["is_valid"] else "Critical fields not preserved"
        )
    
    def _product_page_prompt(self, content: AssembledContent, constraints: str) -> str:
        return f"""
Reformat this product information into an SEO-optimized product page.
Use ONLY the facts provided - do not add any information not present.

{constraints}

Product Information:
{content.to_context_string()}

Requirements:
- Write compelling copy that highlights benefits
- Include all specifications exactly as provided
- Include all warnings verbatim
- Use markdown formatting
- Optimize for search engines

Output the product page:
"""
    
    def _email_prompt(self, content: AssembledContent, constraints: str) -> str:
        return f"""
Write a professional email incorporating this information.
Use ONLY the facts provided - do not add any information.

{constraints}

Information:
{content.to_context_string()}

Requirements:
- Professional tone
- Clear and concise
- Include all relevant details from the source

Output the email:
"""
    
    def _summary_prompt(self, content: AssembledContent, constraints: str) -> str:
        return f"""
Write a concise summary of this information.
Use ONLY the facts provided.

{constraints}

Information:
{content.to_context_string()}

Output a clear, factual summary:
"""
    
    def _comparison_prompt(self, content: AssembledContent, constraints: str) -> str:
        return f"""
Create a comparison or analysis of this information.
Use ONLY the facts provided.

{constraints}

Information:
{content.to_context_string()}

Output a structured comparison:
"""
    
    def _custom_prompt(
        self,
        content: AssembledContent,
        instructions: str,
        constraints: str
    ) -> str:
        return f"""
{instructions}

Use ONLY the facts provided - do not add any information.

{constraints}

Information:
{content.to_context_string()}

Output:
"""
    
    def _validate_preservation(
        self,
        source: AssembledContent,
        output: str
    ) -> Dict[str, Any]:
        """Validate critical fields are preserved in output."""
        checks = []
        
        for name, field in source.get_critical_fields().items():
            value_str = str(field.value)
            if value_str in output:
                checks.append({"field": name, "status": "preserved"})
            else:
                checks.append({"field": name, "status": "missing", "expected": value_str})
        
        is_valid = all(c["status"] == "preserved" for c in checks)
        return {"is_valid": is_valid, "checks": checks}


# ============================================================================
# Pipeline
# ============================================================================

class AssembledReformatPipeline:
    """
    Complete two-phase pipeline: Assemble → Reformat.
    
    Usage:
        pipeline = AssembledReformatPipeline(
            assembler=DatabaseAssembler(conn, field_mapping),
            reformatter=ContentReformatter(llm_client)
        )
        result = pipeline.execute(
            query={"table": "products", "id": 123},
            output_format="product_page"
        )
    """
    
    def __init__(self, assembler: DataAssembler, reformatter: ContentReformatter):
        self.assembler = assembler
        self.reformatter = reformatter
    
    def execute(
        self,
        query: Dict[str, Any],
        output_format: str,
        custom_instructions: Optional[str] = None,
        skip_reformat: bool = False
    ) -> PipelineResult:
        """
        Execute the two-phase pipeline.
        
        Args:
            query: Query for the assembler
            output_format: Format for reformatter
            custom_instructions: Custom instructions if format is "custom"
            skip_reformat: If True, return only assembled content
        
        Returns:
            PipelineResult with assembled and reformatted content
        """
        # Phase 1: Assemble
        try:
            assembled = self.assembler.assemble(query)
        except Exception as e:
            return PipelineResult(
                success=False,
                error=f"Assembly failed: {str(e)}"
            )
        
        # Validate assembly
        assembly_validation = self._validate_assembly(assembled)
        if not assembly_validation["is_valid"]:
            return PipelineResult(
                success=False,
                assembled=assembled,
                assembly_validation=assembly_validation,
                error="Assembly validation failed"
            )
        
        if skip_reformat:
            return PipelineResult(
                success=True,
                assembled=assembled,
                assembly_validation=assembly_validation
            )
        
        # Phase 2: Reformat
        reformat_result = self.reformatter.reformat(
            assembled,
            output_format,
            custom_instructions
        )
        
        return PipelineResult(
            success=reformat_result.success,
            assembled=assembled,
            reformatted=reformat_result.content,
            assembly_validation=assembly_validation,
            reformat_validation=reformat_result.validation,
            error=reformat_result.error
        )
    
    def _validate_assembly(self, content: AssembledContent) -> Dict[str, Any]:
        """Validate assembled content completeness."""
        errors = []
        warnings = []
        
        for name, field in content.fields.items():
            if field.risk_level == FieldRisk.CRITICAL:
                if field.value == "NOT_FOUND" or field.value is None:
                    errors.append(f"Missing critical field: {name}")
                elif field.confidence < 0.8:
                    warnings.append(f"Low confidence on critical field {name}: {field.confidence}")
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }


# ============================================================================
# Convenience Functions
# ============================================================================

def quick_assemble_reformat(
    data: Dict[str, Any],
    critical_fields: List[str],
    output_format: str,
    llm_client,
    custom_instructions: Optional[str] = None
) -> str:
    """
    Quick assembly and reformat without full pipeline setup.
    
    Usage:
        result = quick_assemble_reformat(
            data={"name": "Widget", "price": "$99", "description": "A great widget"},
            critical_fields=["price"],
            output_format="product_page",
            llm_client=my_llm
        )
    """
    # Build assembled content
    fields = {}
    for name, value in data.items():
        risk = FieldRisk.CRITICAL if name in critical_fields else FieldRisk.FLEXIBLE
        fields[name] = AssembledField(
            name=name,
            value=value,
            risk_level=risk,
            source="direct_input"
        )
    
    assembled = AssembledContent(fields=fields)
    reformatter = ContentReformatter(llm_client)
    
    result = reformatter.reformat(assembled, output_format, custom_instructions)
    return result.content if result.success else f"Error: {result.error}"


if __name__ == "__main__":
    print("Content Assembler initialized.")
    print("Use AssembledReformatPipeline or quick_assemble_reformat()")
