# ADR-003: Dual-Layer Evidence Storage

## Status
Accepted

## Context
Disputes involve structured data (transaction details, amounts) and unstructured files (PDFs, images).

## Decision
We will use a **Dual-Layer Strategy**:
1. **Object Storage (S3)**: For file artifacts (Proof of Delivery, Signature Images).
2. **Document Store / JSON**: For metadata, structured evidence fields, and references to S3 URLs.

## Rationale
- **Performance**: Databases are poor at storing large blobs.
- **Compliance**: S3 allows specific retention policies and access controls for documents.
- **VROL Alignment**: VROL requires uploading documents separately and linking them via ID/URL.

## Consequences
- Requires managing two data stores and keeping them in sync (e.g., if a file upload fails, the metadata record shouldn't reference it).

