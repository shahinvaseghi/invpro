## Overview

We are designing `invproj`, a modular warehouse, production, and quality control platform built with Python and Django. The application targets PostgreSQL as the primary database engine and must operate on both Linux/Nginx and Windows Server/IIS deployments. Django serves server-side UI and API endpoints today, while the architecture leaves room for future SPA or mobile clients. All modules initially share a single physical database, yet consistent naming conventions (`inventory_`, `production_`, `qc_`, shared `invproj_`) make it straightforward to migrate each module into its own database or service as the platform scales. Shared/global entities—companies, personnel, users, company units—reside in the `invproj_` namespace and provide consistent tenancy, security, and configuration anchors across the system.

This document captures the quality control (QC) module database design. The QC module integrates tightly with inventory and production flows by tracking inspections, sampling plans, nonconformities, corrective actions, and certification records. Tables defined here use the `qc_` prefix and reference shared entities to preserve modularity while enabling comprehensive traceability from incoming materials through in-process checks to final product release. The schema description is self-contained so it can be read independently, yet it aligns with the overall architecture and the companion inventory and production design plans.

Key design principles:

- **Multi-company tenancy**: Every QC table stores `company_id` and cached `company_code`, referencing `invproj_company`, to isolate tenant data and prepare for future sharding.
- **Consistent auditing**: Tables include `is_enabled`, activation timestamps, creation/update metadata, and optional `metadata` (`jsonb`) for extensibility. Booleans use `smallint` (0/1) for performance and cross-database portability.
- **Traceability & containment**: QC data links to inventory lots, production orders, and personnel to provide end-to-end visibility for inspections, issues, and approvals.
- **Flexible JSON usage**: Semi-structured attributes (inspection results, measurement data, CAPA details) leverage PostgreSQL `jsonb` with indexing strategies tuned per table.
- **Modular boundaries**: QC tables reference shared entities or module-specific tables only through well-defined foreign keys, enabling eventual database separation without schema rewrites.

## Database Design Plan

- Define QC-specific tables (`qc_`) for inspections, sampling plans, nonconformity reports, corrective actions, certifications, and supporting reference data.
- Document relationships to shared (`invproj_`) entities and cross-module references (inventory lots, production orders) needed for traceability.
- Capture naming conventions, constraints, and JSON usage for each table.
- Track open questions and assumptions that require validation with operations and quality teams.

### QC Module

#### Table: `qc_receipt_inspection`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `company_id` | `bigint` | `NOT NULL`, FK to `invproj_company(id)` | Owning company. |
| `company_code` | `varchar(8)` | `NOT NULL`, check numeric | Cached company code for reporting. |
| `temporary_receipt_id` | `bigint` | `NOT NULL`, FK to `inventory_receipt_temporary(id)` | Temporary warehouse receipt awaiting QC. |
| `temporary_receipt_code` | `varchar(20)` | `NOT NULL` | Cached temporary receipt code. |
| `inspection_code` | `varchar(30)` | `NOT NULL`, `UNIQUE` within company | QC inspection document identifier. |
| `inspection_date` | `timestamp with time zone` | `NOT NULL`, default `now()` | When the inspection occurred. |
| `inspection_status` | `varchar(20)` | `NOT NULL`, default `'in_progress'` | Workflow state (`in_progress`, `passed`, `failed`, `rework`, `cancelled`). |
| `inspector_id` | `bigint` | `NOT NULL`, FK to `invproj_person(id)` | Lead inspector. |
| `inspector_code` | `varchar(8)` | `NOT NULL` | Cached personnel code for the inspector. |
| `inspection_summary` | `text` | nullable | Narrative summary of findings. |
| `inspection_results` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Structured measurements/checklist outcomes. |
| `nonconformity_flag` | `smallint` | `NOT NULL`, default `0`, check in (0,1) | Indicates whether issues were found. |
| `nonconformity_report_id` | `bigint` | nullable | Placeholder FK to future NC/CAPA table. |
| `approval_decision` | `varchar(20)` | `NOT NULL`, default `'pending'` | Decision (`pending`, `approved`, `approved_with_deviation`, `rejected`). |
| `approved_at` | `timestamp with time zone` | nullable | Timestamp when inspection was approved. |
| `approved_by_id` | `bigint` | nullable, FK to `invproj_person(id)` | Approver (can differ from inspector). |
| `approval_notes` | `text` | nullable | Additional comments about the decision. |
| `attachments` | `jsonb` | `NOT NULL`, default `'[]'::jsonb` | Array of files/photos tied to the inspection. |
| `metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Extensible fields (sampling plan info, instrument IDs). |
| `is_enabled` | `smallint` | `NOT NULL`, default `1`, check in (0,1) | Soft-delete flag. |
| `activated_at` | `timestamp with time zone` | nullable | Last enable timestamp. |
| `deactivated_at` | `timestamp with time zone` | nullable | Last disable timestamp. |
| `created_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Auto-populated on insert. |
| `edited_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Update audit. |
| `created_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Creator reference. |
| `edited_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Last editor reference. |

Additional considerations:

- Unique constraint on `(company_id, temporary_receipt_id)` ensures one active QC inspection per temporary receipt; reuse old records by toggling `is_enabled` if reinspection is required.
- Integrate with `inventory_receipt_temporary` workflow so that `approval_decision='approved'` (or `'approved_with_deviation'`) is mandatory before converting to a permanent receipt.
- Use `inspection_results` JSON to capture measurement data, sampling sizes, and acceptance criteria; index key fields as necessary for reporting.
- Link nonconformities and CAPA records once those tables are defined, using `nonconformity_report_id` or a join table.
- Ensure `inspector_id` and any approver references belong to the same company and have appropriate QC roles.

### Shared Considerations

- Reuse existing shared entities (`invproj_company`, `invproj_person`, `invproj_user`, `invproj_company_unit`) for tenancy, personnel, and unit references.
- Coordinate status enumerations with inventory and production modules to simplify reporting and workflow integrations.
- Plan for API endpoints and service hooks that synchronize QC outcomes with inventory availability and production release processes.
- Ensure migrations keep compatibility with future database separation by avoiding QC-specific schema changes in shared tables without formal coordination.

## Open Questions

- Finalize the scope of QC processes in the first release (incoming inspection, in-process inspection, final release, certifications).
- Define integration points with inventory lot tracking, production order checkpoints, and external laboratory systems if applicable.
- Determine reporting and analytics requirements for compliance (e.g., ISO, FDA) to design indexes and retention policies.
