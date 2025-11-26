## Overview

We are designing `invproj`, a modular warehouse and production management platform built with Python and Django. The system targets PostgreSQL as the primary database and must operate in both Linux/Nginx and Windows Server/IIS environments. Front-end delivery is planned through Django's templating (with room for future SPA integration), while RESTful APIs will serve integrations when modules are split into separate services. The architecture keeps a single physical database initially, yet strict naming conventions and schema boundaries (`inventory_`, `production_`, `qc_`, and shared `invproj_` tables) make it possible to migrate modules into dedicated databases or microservices later without heavy refactoring. Shared/global entities—companies, personnel, users, company units—live in the `invproj_` namespace; module-specific tables reference these shared structures to maintain consistent tenancy and access control rules across the platform.

This document presents the inventory module database design for the `invproj` platform. The overall solution is a modular Python/Django system that targets PostgreSQL and must run in both Linux/Nginx and Windows/IIS environments. We deploy all modules inside a single physical database initially, but schema boundaries and naming conventions allow future extraction into separate services. Shared/global entities use the `invproj_` prefix, while inventory-specific tables use `inventory_`; production and QC modules follow similar conventions in their own design documents. Each module is designed to remain self-contained yet interoperable through well-defined references and shared entities.

The inventory module covers master data (item catalogs, warehouses, suppliers), procurement requests, inbound receipts (permanent, temporary, consignment), outbound issues (permanent, consumption, consignment), and stocktaking adjustments (deficit, surplus, record). The module also connects to production workflows through purchase requests and transfer documents to ensure traceability across the manufacturing lifecycle. This document provides enough context to understand the inventory schema independently, while remaining aligned with the broader project architecture described above.

Key design principles:

- **Multi-company tenancy**: Every operational table stores `company_id` and cached `company_code`, referencing `invproj_company`. This keeps data isolated per tenant and eases future sharding.
- **Consistent auditing**: Tables include `is_enabled`, activation timestamps, creation/update metadata, and optional `metadata` (`jsonb`) for extensibility. Boolean semantics use `smallint` (0/1) per performance preference and to align with legacy conventions.
- **Human-readable codes**: Modules expose `public_code` values supplied by users. Composite identifiers (e.g., item codes) cache component segments to simplify downstream logic, reporting, and future migrations.
- **Bridge tables for many-to-many**: Item-to-warehouse, personnel-to-work-line, supplier-to-category/item, and similar relationships use dedicated tables, ensuring clean boundaries when modules scale independently.
- **Rich JSON usage**: Technical specifications, pricing metadata, flexible attributes, and approvals rely on PostgreSQL `jsonb`, enabling indexed queries and schema evolution without disruptive migrations.
- **Item code structure**: `item_code` concatenates digits in the following order to guarantee uniqueness and traceability: `type_public_code (3 digits)` + `category_public_code (3 digits)` + `subcategory_public_code (3 digits)` + `user_segment (2 digits, user-chosen)` + `sequence_segment (5 digits, incremental per type/category/subcategory/user combination)`.
- **Batch numbers & traceability**: Every new item generates a `batch_number` using the pattern `MMYY-XXXXXX` where the four digits represent month and two-digit year of creation and the trailing six digits form a zero-padded sequence that increments per calendar month. Documents use `is_locked` to prevent edits once posted, supporting audit readiness.
- **Lot control**: Items flagged with `has_lot_tracking=1` must maintain unit-level lot codes. Permanent receipts generate unique lot codes using the format `LOT-MMYY-XXXXXX-UUU` (prefix `LOT`, month-year of receipt, the six-digit monthly sequence shared with the batch, and an optional three-digit unit suffix). Outbound consumption/issues must capture the lot codes consumed for traceability.
- **Document taxonomy**: Inventory transactions are grouped into entry, exit, and stocktaking families. Entry documents cover permanent, temporary, and consignment receipts; exit documents cover permanent, consumption, and consignment issues; stocktaking will introduce deficit/surplus/record adjustments. Table designs capture necessary linkage (e.g., permanent receipt referencing temporary receipt) and status control.
- **Temporary receipt workflow**: Items flagged as requiring temporary receipts must pass through QC approval before generating permanent or consignment receipts. Both inbound and outbound documents therefore expose linkage fields to trace transitions across the workflow.
- **Consignment lifecycle**: Consignment receipts and issues maintain ownership state for goods held on behalf of suppliers, enabling conversion to permanent ownership or return to consignors with full traceability.

The sections below document each table with column-level details, constraints, and implementation notes to guide Django model creation, validation rules, and migration planning.

## Database Design Plan

- Draft the conceptual and physical schema for modules: Inventory, Production, QC, Shared.
- Capture decisions about naming conventions, constraints, relationships.
- Record JSON usage patterns to leverage PostgreSQL `jsonb`.
- Track pending questions or assumptions for follow-up.

### Inventory Module

#### Table: `inventory_item_type`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `company_id` | `bigint` | `NOT NULL`, FK to `invproj_company(id)` | Owning company. |
| `company_code` | `varchar(3)` | `NOT NULL`, check numeric | Cached company code. |
| `public_code` | `varchar(3)` | `NOT NULL`, `UNIQUE`, check numeric | User-defined code; first three digits for item `USER_ID` prefix. |
| `name` | `varchar(120)` | `NOT NULL`, `UNIQUE` | Persian/local display name. |
| `name_en` | `varchar(120)` | `NOT NULL`, `UNIQUE` | Latin/English display name. |
| `is_enabled` | `smallint` | `NOT NULL`, default `1`, check in (0,1) | Controls availability of type, maps 1=active, 0=inactive. |
| `sort_order` | `smallint` | `NOT NULL`, default `0` | Optional ordering in UI/reports. |
| `activated_at` | `timestamp with time zone` | nullable | When the type was last enabled. |
| `deactivated_at` | `timestamp with time zone` | nullable | When the type was disabled. |
| `created_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Auto-populated on insert. |
| `edited_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Update audit. |
| `created_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Creator reference. |
| `edited_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Last editor reference. |
| `description` | `varchar(255)` | nullable | Short display description. |
| `notes` | `text` | nullable | Internal notes. |
| `metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Extensible settings per type. |

Additional considerations:

- Add trigger or application logic to maintain `activated_at` / `deactivated_at`.
- Enforce `edited_at` auto-updates via trigger or application-layer `auto_now`.
- Expose a partial unique index to ensure only one active record with a given `public_code` if soft deletes are added later.
- Attach metadata (creator/updater) later if needed via foreign keys to `invproj_user`.
- Add composite index on `(is_enabled, sort_order, public_code)` tailored to query patterns.
- Create separate `inventory_item_type_status_log` if full activation history must be tracked.

#### Table: `inventory_item_category`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `company_id` | `bigint` | `NOT NULL`, FK to `invproj_company(id)` | Owning company. |
| `company_code` | `varchar(3)` | `NOT NULL`, check numeric | Cached company code for reporting. |
| `public_code` | `varchar(3)` | `NOT NULL`, `UNIQUE` within company, check numeric | User-defined category code. |
| `name` | `varchar(120)` | `NOT NULL`, `UNIQUE` within company | Persian/local display name. |
| `name_en` | `varchar(120)` | `NOT NULL`, `UNIQUE` within company | Latin/English display name. |
| `is_enabled` | `smallint` | `NOT NULL`, default `1`, check in (0,1) | Root category availability. |
| `sort_order` | `smallint` | `NOT NULL`, default `0` | Ordering in UI/reports. |
| `activated_at` | `timestamp with time zone` | nullable | Last enable timestamp. |
| `deactivated_at` | `timestamp with time zone` | nullable | Last disable timestamp. |
| `created_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Auto-populated on insert. |
| `edited_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Update audit (trigger/logic). |
| `created_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Creator reference. |
| `edited_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Last editor reference. |
| `description` | `varchar(255)` | nullable | Short description. |
| `notes` | `text` | nullable | Internal notes. |
| `metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Extensible settings per category. |

Additional considerations:

- No parent link here because root categories remain standalone; subcategories will live in their own table referencing this one.
- Mirror index strategy (e.g., `(company_id, is_enabled, sort_order, public_code)` plus unique constraints) to keep lookup patterns consistent.
- Optional status log table if activation history tracking is required.
- Enforce referential integrity so every category row's `company_id` matches the owning company referenced by dependent tables.

#### Table: `inventory_item_subcategory`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `company_id` | `bigint` | `NOT NULL`, FK to `invproj_company(id)` | Owning company. |
| `company_code` | `varchar(3)` | `NOT NULL`, check numeric | Cached company code. |
| `category_id` | `bigint` | `NOT NULL`, FK to `inventory_item_category(id)` | Parent category reference. |
| `public_code` | `varchar(3)` | `NOT NULL`, `UNIQUE` per company+category, check numeric | Subcategory code appended to category prefix. |
| `name` | `varchar(120)` | `NOT NULL` | Persian/local display name. |
| `name_en` | `varchar(120)` | `NOT NULL` | Latin/English display name. |
| `is_enabled` | `smallint` | `NOT NULL`, default `1`, check in (0,1) | Subcategory availability. |
| `sort_order` | `smallint` | `NOT NULL`, default `0` | Ordering within category. |
| `activated_at` | `timestamp with time zone` | nullable | Last enable timestamp. |
| `deactivated_at` | `timestamp with time zone` | nullable | Last disable timestamp. |
| `created_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Auto-populated on insert. |
| `edited_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Update audit (trigger/logic). |
| `created_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Creator reference. |
| `edited_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Last editor reference. |
| `description` | `varchar(255)` | nullable | Short description. |
| `notes` | `text` | nullable | Internal notes. |
| `metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Extensible settings per subcategory. |

Additional considerations:

- Enforce unique constraint on `(company_id, category_id, public_code)` and optionally `(company_id, category_id, name)` to prevent duplicates per category.
- Foreign key should cascade updates but restrict deletes; consider soft-delete or status log pattern similar to higher-level tables.
- If hierarchical subcategories are ever needed, extend with additional relationship table instead of self-referencing.
- Validate at application level that `company_id` matches the parent category's company.

#### Table: `inventory_warehouse`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `company_id` | `bigint` | `NOT NULL`, FK to `invproj_company(id)` | Owning company. |
| `company_code` | `varchar(3)` | `NOT NULL`, check numeric | Cached company code for documents and reporting. |
| `public_code` | `varchar(5)` | `NOT NULL`, `UNIQUE` within company, check numeric | Warehouse human-facing code (e.g., `001`, `1001`). |
| `name` | `varchar(150)` | `NOT NULL`, `UNIQUE` within company | Persian/local warehouse name. |
| `name_en` | `varchar(150)` | `NOT NULL`, `UNIQUE` within company | Latin/English warehouse name. |
| `is_enabled` | `smallint` | `NOT NULL`, default `1`, check in (0,1) | Controls active state. |
| `sort_order` | `smallint` | `NOT NULL`, default `0` | Ordering in UI/reports. |
| `activated_at` | `timestamp with time zone` | nullable | Last enable timestamp. |
| `deactivated_at` | `timestamp with time zone` | nullable | Last disable timestamp. |
| `created_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Auto-populated on insert. |
| `edited_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Update audit (trigger/logic). |
| `created_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Creator reference. |
| `edited_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Last editor reference. |
| `description` | `varchar(255)` | nullable | Short description (purpose/notes). |
| `notes` | `text` | nullable | Operational notes. |
| `metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Extensible settings (e.g., automation flags). |
| `location_label` | `varchar(120)` | nullable | Optional short descriptor (e.g., plant name / zone). |

Additional considerations:

- Enforce unique constraint on `(company_id, public_code)` and `(company_id, name)` for clean lookup.
- Index `(is_enabled, sort_order)` for filtered listings.
- For detailed operational policies (shift calendars, storage conditions) extend `metadata` or related tables later.
- Consider dedicated contact table if multiple stakeholders per warehouse are tracked.
- Guard application logic so warehouses cannot be shared across companies; ensure `company_id` consistency in dependent tables.

#### Table: `inventory_work_line`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `company_id` | `bigint` | `NOT NULL`, FK to `invproj_company(id)` | Owning company. |
| `company_code` | `varchar(3)` | `NOT NULL`, check numeric | Cached company code. |
| `public_code` | `varchar(5)` | `NOT NULL`, `UNIQUE` within company, check numeric | Work line code for human reference. |
| `warehouse_id` | `bigint` | `NOT NULL`, FK to `inventory_warehouse(id)` | Owning warehouse. |
| `name` | `varchar(150)` | `NOT NULL` | Persian/local name. |
| `name_en` | `varchar(150)` | `NOT NULL` | Latin/English name. |
| `is_enabled` | `smallint` | `NOT NULL`, default `1`, check in (0,1) | Availability status. |
| `sort_order` | `smallint` | `NOT NULL`, default `0` | Ordering within the warehouse. |
| `activated_at` | `timestamp with time zone` | nullable | Last enable timestamp. |
| `deactivated_at` | `timestamp with time zone` | nullable | Last disable timestamp. |
| `created_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Auto-populated on insert. |
| `edited_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Update audit (trigger/logic). |
| `created_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Creator reference. |
| `edited_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Last editor reference. |
| `description` | `varchar(255)` | nullable | Short description (purpose/area). |
| `notes` | `text` | nullable | Operational notes. |
| `metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Extensible settings (e.g., automation flags). |

Additional considerations:

- Unique constraint on `(company_id, warehouse_id, public_code)` and optionally `(company_id, warehouse_id, name)` to avoid duplicates.
- Reference back to production lines or QC stations can be modeled later via bridge tables.
- If shift schedules or capacity metrics are tracked, consider adjunct tables keyed by `work_line_id`.
- Validate `company_id` consistency between work line and parent warehouse.

#### Table: `inventory_item_spec`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `company_id` | `bigint` | `NOT NULL`, FK to `invproj_company(id)` | Owning company. |
| `company_code` | `varchar(3)` | `NOT NULL`, check numeric | Cached company code to accelerate analytics. |
| `item_id` | `bigint` | `NOT NULL`, FK to `inventory_item(id)` | Linked inventory item. |
| `item_code` | `varchar(30)` | `NOT NULL` | Cached item code for quick lookup/reporting. |
| `supplier_name` | `varchar(180)` | nullable | Optional supplier/manufacturer name. |
| `spec_data` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Flexible technical specs (dimensions, units, material, etc.). |
| `is_enabled` | `smallint` | `NOT NULL`, default `1`, check in (0,1) | Controls visibility/usage. |
| `sort_order` | `smallint` | `NOT NULL`, default `0` | Ordering of multiple specs per item. |
| `activated_at` | `timestamp with time zone` | nullable | Last enable timestamp. |
| `deactivated_at` | `timestamp with time zone` | nullable | Last disable timestamp. |
| `created_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Auto-populated on insert. |
| `edited_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Update audit (trigger/logic). |
| `created_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Creator reference. |
| `edited_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Last editor reference. |
| `description` | `varchar(255)` | nullable | Short description/title (e.g., "Default spec"). |
| `notes` | `text` | nullable | Additional internal notes. |
| `metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Extensible administrative metadata. |

Additional considerations:

- Enforce unique constraint on `(company_id, item_id, sort_order)` or `(company_id, item_id, item_code, supplier_name)` depending on usage.
- `spec_data` structure should be documented (e.g., expected keys for dimensions, units, tolerances) and validated at application layer.
- If multiple suppliers per item with shared specs need tracking, consider separate supplier reference table and join table.
- `item_code` duplicates data for denormalized reporting; keep synchronized via triggers or application logic.
- Enforce through application logic that `company_id` aligns with the parent item's company.

#### Table: `inventory_item_unit`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `company_id` | `bigint` | `NOT NULL`, FK to `invproj_company(id)` | Owning company. |
| `company_code` | `varchar(3)` | `NOT NULL`, check numeric | Cached company code. |
| `public_code` | `varchar(6)` | `NOT NULL`, `UNIQUE` within company, check numeric | Unit definition code for the item. |
| `item_id` | `bigint` | `NOT NULL`, FK to `inventory_item(id)` | Target inventory item. |
| `item_code` | `varchar(30)` | `NOT NULL` | Cached item code for reporting. |
| `from_unit` | `varchar(30)` | `NOT NULL` | Base unit symbol (e.g., `M`, `EA`). |
| `from_quantity` | `numeric(18,6)` | `NOT NULL`, default `1.0` | Quantity in base unit. |
| `to_unit` | `varchar(30)` | `NOT NULL` | Alternate unit symbol (e.g., `KG`, `PACK`). |
| `to_quantity` | `numeric(18,6)` | `NOT NULL` | Equivalent quantity in alternate unit. |
| `is_primary` | `smallint` | `NOT NULL`, default `0`, check in (0,1) | Marks default conversion mapping. |
| `is_enabled` | `smallint` | `NOT NULL`, default `1`, check in (0,1) | Availability of this conversion. |
| `sort_order` | `smallint` | `NOT NULL`, default `0` | Ordering when multiple conversions exist. |
| `activated_at` | `timestamp with time zone` | nullable | Last enable timestamp. |
| `deactivated_at` | `timestamp with time zone` | nullable | Last disable timestamp. |
| `created_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Auto-populated on insert. |
| `edited_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Update audit (trigger/logic). |
| `created_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Creator reference. |
| `edited_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Last editor reference. |
| `description` | `varchar(255)` | nullable | Short description (e.g., "Meter to KG"). |
| `notes` | `text` | nullable | Operational notes or validation remarks. |
| `metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Extensible details (e.g., tolerance, supplier-specific tags). |

Additional considerations:

- Enforce unique constraint on `(company_id, item_id, from_unit, to_unit)` to avoid duplicate conversions.
- `is_primary=1` should be unique per `(company_id, item_id, from_unit)` to mark the default path.
- Application layer should support reciprocal conversion (e.g., KG→M) either via additional rows or computed inverse.
- Validate numeric precision for `from_quantity` and `to_quantity` to accommodate practical ranges (e.g., kgs per pack).
- If organizational unit dictionary is required, create a shared `inventory_unit` lookup table and reference via FK instead of raw strings.
- Ensure `company_id` matches the owning item, especially when conversions are managed via services.

#### Table: `inventory_item_lot`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `company_id` | `bigint` | `NOT NULL`, FK to `invproj_company(id)` | Owning company. |
| `company_code` | `varchar(3)` | `NOT NULL`, check numeric | Cached company code for reporting. |
| `item_id` | `bigint` | `NOT NULL`, FK to `inventory_item(id)` | Item reference. |
| `item_code` | `varchar(16)` | `NOT NULL` | Cached item code. |
| `lot_code` | `varchar(30)` | `NOT NULL`, `UNIQUE` within company | Unit-level lot identifier (format `LOT-MMYY-XXXXXX-UUU`). |
| `batch_number` | `varchar(20)` | `NOT NULL` | Batch number associated with the lot. |
| `quantity` | `numeric(18,6)` | `NOT NULL`, default `1.0` | Quantity represented by the lot record (default 1). |
| `unit` | `varchar(30)` | `NOT NULL` | Unit of measure. |
| `status` | `varchar(20)` | `NOT NULL`, default `'available'` | (`available`, `reserved`, `consumed`, `scrapped`). |
| `receipt_document_id` | `bigint` | `NOT NULL`, FK to `inventory_receipt_permanent(id)` | Source permanent receipt. |
| `receipt_document_code` | `varchar(20)` | `NOT NULL` | Cached permanent receipt document code. |
| `issue_document_type` | `varchar(30)` | nullable | Consuming document type (`inventory_issue_consumption`, etc.). |
| `issue_document_id` | `bigint` | nullable | FK to consuming document header. |
| `issue_document_code` | `varchar(20)` | nullable | Cached consuming document code. |
| `issued_at` | `timestamp with time zone` | nullable | Timestamp when lot was consumed. |
| `metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Extensible attributes (serial numbers, QC data). |
| `created_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Auto-populated on insert. |
| `edited_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Update audit. |
| `created_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Creator reference. |
| `edited_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Last editor reference. |

Additional considerations:

- Unique constraint on `(company_id, lot_code)` ensures uniqueness per company; consider indexing `(item_id, status)` for lookups. |
- Generate `lot_code` per unit when `has_lot_tracking=1` using `LOT-MMYY-XXXXXX-UUU`, where `XXXXXX` matches the batch sequence for the month and `UUU` is a zero-padded unit counter for multi-unit receipts. |
- Enforce that only items requiring lot tracking create lot records; other items bypass the table. |
- Support reversals by updating `status` and clearing `issue_document_*` fields when transactions are voided. |
- Extend with history table if movement between statuses needs full audit logging. |

### Inventory Module (continued)

#### Table: `inventory_item_substitute`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `company_id` | `bigint` | `NOT NULL`, FK to `invproj_company(id)` | Owning company for substitution policy. |
| `company_code` | `varchar(3)` | `NOT NULL`, check numeric | Cached company code to simplify joins. |
| `source_item_id` | `bigint` | `NOT NULL`, FK to `inventory_item(id)` | Item whose demand is being substituted. |
| `source_item_code` | `varchar(30)` | `NOT NULL` | Cached code for reporting. |
| `source_unit` | `varchar(30)` | `NOT NULL` | Base unit for source item (e.g., `EA`, `KG`). |
| `source_quantity` | `numeric(18,6)` | `NOT NULL`, default `1.0` | Quantity of source item being replaced. |
| `target_item_id` | `bigint` | `NOT NULL`, FK to `inventory_item(id)` | Substitute item. |
| `target_item_code` | `varchar(30)` | `NOT NULL` | Cached code for reporting. |
| `target_unit` | `varchar(30)` | `NOT NULL` | Unit for substitute item. |
| `target_quantity` | `numeric(18,6)` | `NOT NULL` | Quantity of substitute item considered equivalent. |
| `is_bidirectional` | `smallint` | `NOT NULL`, default `0`, check in (0,1) | Indicates mutual substitution (A↔B). |
| `is_enabled` | `smallint` | `NOT NULL`, default `1`, check in (0,1) | Availability flag. |
| `sort_order` | `smallint` | `NOT NULL`, default `0` | Ordering when multiple substitutes exist. |
| `activated_at` | `timestamp with time zone` | nullable | Last enable timestamp. |
| `deactivated_at` | `timestamp with time zone` | nullable | Last disable timestamp. |
| `created_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Auto-populated on insert. |
| `edited_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Update audit (trigger/logic). |
| `created_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Creator reference. |
| `edited_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Last editor reference. |
| `description` | `varchar(255)` | nullable | Short context (e.g., "Emergency replacement"). |
| `notes` | `text` | nullable | Operational or approval notes. |
| `metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Extensible details (e.g., quality constraints). |

Additional considerations:

- Enforce unique constraint on `(company_id, source_item_id, target_item_id, source_unit, target_unit)` to prevent duplicate mappings.
- If substitution should be symmetric, either store reciprocal rows or rely on `is_bidirectional` flag with application logic.
- Validate units against defined conversions to ensure compatibility.
- Consider `effective_start` / `effective_end` fields if substitutions are time-bound.
- Ensure both source and target items belong to the same company to maintain tenant isolation.

#### Table: `inventory_item`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `company_id` | `bigint` | `NOT NULL`, FK to `invproj_company(id)` | Owning company. |
| `company_code` | `varchar(3)` | `NOT NULL`, check numeric | Cached company code. |
| `type_id` | `bigint` | `NOT NULL`, FK to `inventory_item_type(id)` | Item type selection. |
| `category_id` | `bigint` | `NOT NULL`, FK to `inventory_item_category(id)` | Category selection. |
| `subcategory_id` | `bigint` | `NOT NULL`, FK to `inventory_item_subcategory(id)` | Subcategory selection. |
| `type_code` | `varchar(3)` | `NOT NULL`, check numeric | Cached type `public_code`. |
| `category_code` | `varchar(3)` | `NOT NULL`, check numeric | Cached category `public_code`. |
| `subcategory_code` | `varchar(3)` | `NOT NULL`, check numeric | Cached subcategory `public_code`. |
| `user_segment` | `varchar(2)` | `NOT NULL`, check numeric | User-selected two-digit segment. |
| `sequence_segment` | `varchar(5)` | `NOT NULL`, check numeric | Auto-incrementing five-digit sequence per `(type_code, category_code, subcategory_code, user_segment)`. |
| `item_code` | `varchar(16)` | `NOT NULL`, `UNIQUE` within company, check numeric | Composite code (3+3+3+2+5 digits). |
| `batch_number` | `varchar(20)` | `NOT NULL` | Generated batch identifier `MMYY-XXXXXX`; sequence resets at the start of each month. |
| `name` | `varchar(180)` | `NOT NULL`, `UNIQUE` | Local item name. |
| `name_en` | `varchar(180)` | `NOT NULL`, `UNIQUE` | Latin/English item name. |
| `is_sellable` | `smallint` | `NOT NULL`, default `0`, check in (0,1) | Indicates if item can be sold. |
| `has_lot_tracking` | `smallint` | `NOT NULL`, default `0`, check in (0,1) | Requires lot number tracking. |
| `requires_temporary_receipt` | `smallint` | `NOT NULL`, default `0`, check in (0,1) | Flags items that must enter via temporary receipt and QC approval before permanent receipt. |
| `tax_id` | `varchar(30)` | nullable | Tax identifier/code. |
| `tax_title` | `varchar(120)` | nullable | Tax scheme title. |
| `min_stock` | `numeric(18,6)` | nullable | Minimum stock threshold. |
| `default_unit` | `varchar(30)` | `NOT NULL` | Primary unit of measure. |
| `default_unit_id` | `bigint` | nullable, FK to `inventory_unit(id)` (if defined) | Optional structured unit reference. |
| `is_enabled` | `smallint` | `NOT NULL`, default `1`, check in (0,1) | Availability flag. |
| `sort_order` | `smallint` | `NOT NULL`, default `0` | Ordering. |
| `activated_at` | `timestamp with time zone` | nullable | Last enable timestamp. |
| `deactivated_at` | `timestamp with time zone` | nullable | Last disable timestamp. |
| `created_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Auto-populated on insert. |
| `edited_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Update audit (trigger/logic). |
| `created_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Creator reference. |
| `edited_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Last editor reference. |
| `description` | `varchar(255)` | nullable | Short description. |
| `notes` | `text` | nullable | Detailed notes/specs. |
| `metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Extensible attributes (e.g., packaging, lifecycle). |
| `primary_unit` | `varchar(30)` | `NOT NULL` | Canonical unit of measure for inventory valuation/reporting. |

Additional considerations:

- Maintain consistency between `type_id/category_id/subcategory_id` and cached codes via triggers or application logic.
- `sequence_segment` should auto-increment per combination of company/type/category/subcategory/user segment; implement with database trigger/sequence table.
- Validate that `subcategory_id` belongs to the chosen `category_id` (referential integrity via application constraint or FK with partial index scoped by company).
- For sellable items, integrate with sales module later to ensure tax info aligns with fiscal requirements.
- Consider `effective_start`/`effective_end` if items can be temporarily disabled without removing history.
- Validate all referenced type/category/subcategory rows share the same `company_id`.
- Consider unique partial index for active `item_code` values scoped by `company_id` if soft deletes are introduced later.
- Enforce application logic so items with `requires_temporary_receipt=1` must pass through QC workflow before permanent receipts are generated.

#### Table: `inventory_item_warehouse`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `company_id` | `bigint` | `NOT NULL`, FK to `invproj_company(id)` | Owning company. |
| `company_code` | `varchar(3)` | `NOT NULL`, check numeric | Cached company code. |
| `item_id` | `bigint` | `NOT NULL`, FK to `inventory_item(id)` | Item reference. |
| `warehouse_id` | `bigint` | `NOT NULL`, FK to `inventory_warehouse(id)` | Allowed warehouse. |
| `is_primary` | `smallint` | `NOT NULL`, default `0`, check in (0,1) | Marks default warehouse for the item. |
| `is_enabled` | `smallint` | `NOT NULL`, default `1`, check in (0,1) | Active flag. |
| `activated_at` | `timestamp with time zone` | nullable | Last enable timestamp. |
| `deactivated_at` | `timestamp with time zone` | nullable | Last disable timestamp. |
| `created_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Auto-populated on insert. |
| `edited_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Update audit (trigger/logic). |
| `created_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Creator reference. |
| `edited_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Last editor reference. |
| `notes` | `text` | nullable | Additional remarks (e.g., storage limits). |
| `metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Extensible assignment info. |

Additional considerations:

- Unique constraint on `(company_id, item_id, warehouse_id)` to avoid duplicates.
- Ensure only one `is_primary=1` per `(company_id, item_id)` through partial unique index.
- If warehouse permissions depend on item type/category, consider default propagation logic.
- Extend with capacity or replenishment policies in related tables if needed.
- Ensure `company_id` matches both the item and warehouse before persisting the assignment.
- واسط کاربری هنگام تعریف کالا فهرست انبارهای مجاز را از کاربر می‌گیرد و اولین انتخاب را `is_primary=1` می‌کند؛ هنگام ویرایش نیز حذف/افزودن انبارها مستقیماً این جدول را همگام‌سازی می‌کند.

#### Table: `inventory_supplier`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `company_id` | `bigint` | `NOT NULL`, FK to `invproj_company(id)` | Owning company for the supplier record. |
| `company_code` | `varchar(3)` | `NOT NULL`, check numeric | Cached company code to support reporting filters. |
| `public_code` | `varchar(6)` | `NOT NULL`, `UNIQUE` within company, check numeric | Supplier reference code. |
| `name` | `varchar(180)` | `NOT NULL`, `UNIQUE` within company | Supplier name (local language). |
| `name_en` | `varchar(180)` | nullable | Supplier name in Latin alphabet. |
| `phone_number` | `varchar(30)` | nullable | Primary contact phone. |
| `mobile_number` | `varchar(30)` | nullable | Secondary/mobile contact. |
| `email` | `varchar(254)` | nullable | Contact email. |
| `address` | `text` | nullable | Mailing/physical address. |
| `city` | `varchar(120)` | nullable | City. |
| `state` | `varchar(120)` | nullable | State/Province. |
| `country` | `varchar(3)` | nullable | ISO alpha-3 code (e.g., `IRN`). |
| `tax_id` | `varchar(30)` | nullable | Supplier tax identifier. |
| `is_enabled` | `smallint` | `NOT NULL`, default `1`, check in (0,1) | Active supplier flag. |
| `sort_order` | `smallint` | `NOT NULL`, default `0` | Ordering in listings. |
| `activated_at` | `timestamp with time zone` | nullable | Last enable timestamp. |
| `deactivated_at` | `timestamp with time zone` | nullable | Last disable timestamp. |
| `created_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Auto-populated on insert. |
| `edited_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Update audit (trigger/logic). |
| `created_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Creator reference. |
| `edited_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Last editor reference. |
| `description` | `varchar(255)` | nullable | Short description/notes. |
| `metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Extensible supplier attributes (certifications, contracts). |

Additional considerations:

- Validate contact info formats (phone/email) at the application layer.
- For suppliers with multiple contact points, extend via related tables (`inventory_supplier_contact`, etc.).
- Track performance metrics, lead times, or compliance data in dedicated tables keyed by `supplier_id`.
- Introduce unique indexes scoped by `company_id` for codes and names to prevent cross-company collisions.
- Ensure supplier records cannot be shared between companies by validating `company_id` in service layer workflows.

#### Table: `inventory_supplier_category`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `company_id` | `bigint` | `NOT NULL`, FK to `invproj_company(id)` | Owning company. |
| `company_code` | `varchar(3)` | `NOT NULL`, check numeric | Cached company code. |
| `supplier_id` | `bigint` | `NOT NULL`, FK to `inventory_supplier(id)` | Supplier reference. |
| `category_id` | `bigint` | `NOT NULL`, FK to `inventory_item_category(id)` | Category supplier can provide. |
| `is_primary` | `smallint` | `NOT NULL`, default `0`, check in (0,1) | Marks primary focus. |
| `is_enabled` | `smallint` | `NOT NULL`, default `1`, check in (0,1) | Active flag. |
| `activated_at` | `timestamp with time zone` | nullable | Last enable timestamp. |
| `deactivated_at` | `timestamp with time zone` | nullable | Last disable timestamp. |
| `created_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Auto-populated on insert. |
| `edited_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Update audit (trigger/logic). |
| `created_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Creator reference. |
| `edited_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Last editor reference. |
| `notes` | `text` | nullable | Additional remarks (e.g., capacity limits). |
| `metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Extensible assignment info. |

Additional considerations:

- Unique constraint on `(company_id, supplier_id, category_id)` to prevent duplicate assignments.
- Enforce at most one `is_primary=1` per `(company_id, supplier_id)` via partial unique index.
- Extend to subcategories or items if finer-grained coverage tracking is required.
- Ensure `company_id` alignment with both supplier and category to maintain tenant boundaries.

#### Table: `inventory_supplier_subcategory`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `company_id` | `bigint` | `NOT NULL`, FK to `invproj_company(id)` | Owning company. |
| `company_code` | `varchar(3)` | `NOT NULL`, check numeric | Cached company code for filtering. |
| `supplier_id` | `bigint` | `NOT NULL`, FK to `inventory_supplier(id)` | Supplier reference. |
| `subcategory_id` | `bigint` | `NOT NULL`, FK to `inventory_item_subcategory(id)` | Subcategory supported. |
| `is_primary` | `smallint` | `NOT NULL`, default `0`, check in (0,1) | Main subcategory focus. |
| `is_enabled` | `smallint` | `NOT NULL`, default `1`, check in (0,1) | Active flag. |
| `activated_at` | `timestamp with time zone` | nullable | Last enable timestamp. |
| `deactivated_at` | `timestamp with time zone` | nullable | Last disable timestamp. |
| `created_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Auto-populated on insert. |
| `edited_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Update audit (trigger/logic). |
| `created_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Creator reference. |
| `edited_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Last editor reference. |
| `notes` | `text` | nullable | Additional remarks. |
| `metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Extensible info (e.g., capacity, lead time). |

Additional considerations:

- Unique constraint on `(company_id, supplier_id, subcategory_id)` to prevent duplicates.
- Ensure consistency with category assignments (subcategory should belong to a category linked to the supplier).
- For each supplier, limit a single primary subcategory via partial unique index on `(company_id, supplier_id)` filtered by `is_primary=1`.
- Validate at persistence time that supplier and subcategory rows share the same `company_id`.

#### Table: `inventory_supplier_item`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `company_id` | `bigint` | `NOT NULL`, FK to `invproj_company(id)` | Owning company for the supplier-item relationship. |
| `company_code` | `varchar(3)` | `NOT NULL`, check numeric | Cached company code. |
| `supplier_id` | `bigint` | `NOT NULL`, FK to `inventory_supplier(id)` | Supplier reference. |
| `item_id` | `bigint` | `NOT NULL`, FK to `inventory_item(id)` | Specific item they can supply. |
| `is_primary` | `smallint` | `NOT NULL`, default `0`, check in (0,1) | Preferred supplier for the item. |
| `is_enabled` | `smallint` | `NOT NULL`, default `1`, check in (0,1) | Active flag. |
| `min_order_quantity` | `numeric(18,6)` | nullable | MOQ or typical order size. |
| `lead_time_days` | `numeric(6,2)` | nullable | Expected lead time. |
| `price_metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Pricing tiers, currency, validity. |
| `activated_at` | `timestamp with time zone` | nullable | Last enable timestamp. |
| `deactivated_at` | `timestamp with time zone` | nullable | Last disable timestamp. |
| `created_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Auto-populated on insert. |
| `edited_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Update audit (trigger/logic). |
| `created_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Creator reference. |
| `edited_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Last editor reference. |
| `notes` | `text` | nullable | Additional remarks (quality agreements, etc.). |
| `metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Extensible supplier-item info. |

Additional considerations:

- Unique constraint on `(company_id, supplier_id, item_id)` to avoid duplicate registrations.
- Ensure only one `is_primary=1` per `(company_id, item_id)` (partial unique index).
- `price_metadata` can store `{"currency": "IRR", "price": 1200000, "valid_until": "...", "tiers": [...]}` allowing flexible pricing updates.
- Extend with historical pricing table if audit trail is required.
- Guard against cross-company relationships by verifying supplier and item `company_id` values match the link row.

### Procurement Requests

#### Table: `inventory_purchase_request`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `company_id` | `bigint` | `NOT NULL`, FK to `invproj_company(id)` | Owning company for the request. |
| `company_code` | `varchar(3)` | `NOT NULL`, check numeric | Cached company code for reporting. |
| `request_code` | `varchar(20)` | `NOT NULL`, `UNIQUE` | Human-readable purchase request identifier. |
| `request_date` | `date` | `NOT NULL` | Request creation date. |
| `requested_by_id` | `bigint` | `NOT NULL`, FK to `invproj_person(id)` | Person submitting the request. |
| `requested_by_code` | `varchar(8)` | `NOT NULL` | Cached personnel public code. |
| `item_id` | `bigint` | `NOT NULL`, FK to `inventory_item(id)` | Item the requester needs. |
| `item_code` | `varchar(16)` | `NOT NULL` | Cached item composite code. |
| `unit` | `varchar(30)` | `NOT NULL` | Unit of measure requested. |
| `quantity_requested` | `numeric(18,6)` | `NOT NULL` | Requested quantity. |
| `quantity_fulfilled` | `numeric(18,6)` | `NOT NULL`, default `0` | Quantity already fulfilled through receipts. |
| `needed_by_date` | `date` | nullable | Desired delivery date. |
| `priority` | `varchar(10)` | `NOT NULL`, default `'normal'` | Priority level (`low`, `normal`, `high`, `urgent`). |
| `status` | `varchar(20)` | `NOT NULL`, default `'draft'` | Workflow state (`draft`, `approved`, `ordered`, `fulfilled`, `cancelled`). |
| `reason_code` | `varchar(30)` | nullable | Reason or category for the request. |
| `reference_document_type` | `varchar(30)` | nullable | Upstream trigger (production order, sales order). |
| `reference_document_id` | `bigint` | nullable | FK to upstream document if tracked. |
| `reference_document_code` | `varchar(30)` | nullable | Cached reference code. |
| `approver_id` | `bigint` | nullable, FK to `invproj_person(id)` | Person approving the request. |
| `approved_at` | `timestamp with time zone` | nullable | Approval timestamp. |
| `approval_notes` | `text` | nullable | Notes from approver. |
| `request_metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Extra info (e.g., supplier suggestions, attachments). |
| `is_locked` | `smallint` | `NOT NULL`, default `0`, check in (0,1) | Locks the request after approval to prevent edits. |
| `notes` | `text` | nullable | Requester notes. |
| `is_enabled` | `smallint` | `NOT NULL`, default `1`, check in (0,1) | Soft-delete flag. |
| `activated_at` | `timestamp with time zone` | nullable | Last enable timestamp. |
| `deactivated_at` | `timestamp with time zone` | nullable | Last disable timestamp. |
| `created_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Auto-populated on insert. |
| `edited_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Update audit. |
| `created_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Creator reference. |
| `edited_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Last editor reference. |
| `metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Extensible attributes (e.g., approval workflow IDs). |

Additional considerations:

- Unique constraint on `(company_id, request_code)` to prevent duplicates.
- `quantity_fulfilled` should be updated via triggers or application logic when receipts are posted.
- Enforce that `item_id` and requester belong to the same `company_id`.
- Consider separate detail table if multiple items per request are needed in future iterations.
- Integrate with procurement workflow (purchase orders) once defined.
- Once `status='approved'`, set `is_locked=1` and expose the request for selection in permanent/consignment receipt forms only in read-only mode.
- **UI Integration**: In the list view (`templates/inventory/purchase_requests.html`), approved requests display three action buttons in the "Actions" column:
  - **"Temporary Receipt"** button (green): Creates a temporary receipt from the purchase request
  - **"Permanent Receipt"** button (blue): Creates a permanent receipt from the purchase request
  - **"Consignment Receipt"** button (purple): Creates a consignment receipt from the purchase request
- These buttons route to intermediate selection views (`CreateReceiptFromPurchaseRequestView`) that allow users to select lines/quantities before creating the final document.

### Inventory Transactions

#### Table: `inventory_receipt_permanent`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `company_id` | `bigint` | `NOT NULL`, FK to `invproj_company(id)` | Owning company for the transaction. |
| `company_code` | `varchar(3)` | `NOT NULL`, check numeric | Cached company code for document numbering and analytics. |
| `document_code` | `varchar(20)` | `NOT NULL`, `UNIQUE` | Human-readable document identifier. |
| `document_date` | `date` | `NOT NULL` | Document issuance date. |
| `item_id` | `bigint` | `NOT NULL`, FK to `inventory_item(id)` | Item reference. |
| `item_code` | `varchar(16)` | `NOT NULL` | Cached item composite code. |
| `warehouse_id` | `bigint` | `NOT NULL`, FK to `inventory_warehouse(id)` | Receiving warehouse. |
| `warehouse_code` | `varchar(5)` | `NOT NULL` | Cached warehouse public code. |
| `unit` | `varchar(30)` | `NOT NULL` | Unit of measure for this receipt. |
| `quantity` | `numeric(18,6)` | `NOT NULL` | Received quantity. |
| `supplier_id` | `bigint` | nullable, FK to `inventory_supplier(id)` | Supplier providing the goods. |
| `supplier_code` | `varchar(6)` | nullable | Cached supplier public code. |
| `unit_price` | `numeric(18,6)` | nullable | Price per unit in document currency. |
| `currency` | `varchar(3)` | nullable | Currency (choices: `IRT`=Toman, `IRR`=Rial, `USD`=US Dollar). |
| `requires_temporary_receipt` | `smallint` | `NOT NULL`, default `0`, check in (0,1) | Flags whether this receipt must reference an approved temporary receipt. |
| `temporary_receipt_id` | `bigint` | nullable, FK to `inventory_receipt_temporary(id)` | Linked temporary receipt document. |
| `temporary_receipt_code` | `varchar(20)` | nullable | Cached temporary receipt document code. |
| `purchase_request_id` | `bigint` | nullable, FK to `inventory_purchase_request(id)` | Purchase request fulfilled by this receipt. |
| `purchase_request_code` | `varchar(20)` | nullable | Cached purchase request code. |
| `warehouse_request_id` | `bigint` | nullable, FK to `inventory_warehouse_request(id)` | Warehouse request that initiated the receipt (internal transfer). |
| `warehouse_request_code` | `varchar(20)` | nullable | Cached warehouse request code. |
| `tax_amount` | `numeric(18,6)` | nullable | Calculated tax amount for the line. |
| `discount_amount` | `numeric(18,6)` | nullable | Applied discount amount. |
| `total_amount` | `numeric(18,6)` | nullable | Total value (quantity * unit_price - discount + tax). |
| `document_metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Additional fields (invoice no., PO, etc.). |
| `notes` | `text` | nullable | Operational notes (e.g., inspection results). |
| `is_enabled` | `smallint` | `NOT NULL`, default `1`, check in (0,1) | Soft-delete flag. |
| `activated_at` | `timestamp with time zone` | nullable | Last enable timestamp. |
| `deactivated_at` | `timestamp with time zone` | nullable | Last disable timestamp. |
| `created_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Auto-populated on insert. |
| `created_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Creator reference. |
| `edited_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Update audit (trigger/logic). |
| `edited_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Last editor reference. |
| `metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Extensible attributes (e.g., approval workflow). |
| `is_locked` | `smallint` | `NOT NULL`, default `0`, check in (0,1) | Prevents edits when set (e.g., after accounting close). |

Additional considerations:

- Unique constraint on `(document_code)` ensures no duplicate permanent receipt numbers.
- Derive `total_amount` and update inventory balances via triggers or service layer logic.
- Maintain referential integrity when linking to temporary receipts; enforce state transition validation in application layer.
- For multi-line documents, consider parent document table (`inventory_receipt_header`) with line items referencing it.
- Verify all referenced entities (item, warehouse, supplier, temporary receipt) belong to the same `company_id` before committing.
- Enforce that receipts flagged with `requires_temporary_receipt=1` are created only when a linked temporary receipt exists and has passed QC (if applicable).
- When `purchase_request_id` is provided, update `quantity_fulfilled` on the purchase request and ensure company alignment.
- When `warehouse_request_id` is provided, ensure the request is `status='approved'`, `is_locked=1`, and matches both item and warehouse before allowing linkage.
- For items with `has_lot_tracking=1`, generate unit-level lot codes in `inventory_item_lot` at lock time; prevent locking unless sufficient sequential lot codes are produced.
- زیرفرایند رابط کاربری کد سند (`PRM-YYYYMM-XXXXXX`) و تاریخ را هنگام ایجاد تولید می‌کند و پیش از ذخیره مقدار/واحد و قیمت را به مقیاس واحد اصلی کالا تبدیل می‌کند تا فیلدهای `quantity` و `unit_price` همواره به واحد پایه نگه‌داری شوند.
- برای حفظ مقادیر خام کاربر، فیلدهای `entered_unit`, `entered_quantity`, `entered_unit_price` نگه داشته می‌شوند تا در رابط کاربری نمایش داده شوند و با مقدار نرمال‌شده مقایسه گردند.

#### Table: `inventory_item_serial`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `company_id` | `bigint` | `NOT NULL`, FK to `invproj_company(id)` | Company scope. |
| `company_code` | `varchar(8)` | `NOT NULL`, cached | Cached company public code. |
| `item_id` | `bigint` | `NOT NULL`, FK to `inventory_item(id)` | Item this serial belongs to. |
| `item_code` | `varchar(16)` | `NOT NULL` | Cached item code. |
| `lot_id` | `bigint` | nullable, FK to `inventory_item_lot(id)` | Optional link to lot/batch. |
| `lot_code` | `varchar(30)` | nullable | Cached lot code. |
| `serial_code` | `varchar(50)` | `NOT NULL`, `UNIQUE` | Human-readable/scanable serial. |
| `receipt_document_id` | `bigint` | `NOT NULL`, FK to `inventory_receipt_permanent(id)` | Origin receipt. |
| `receipt_document_code` | `varchar(20)` | `NOT NULL` | Cached receipt code. |
| `receipt_line_reference` | `varchar(30)` | nullable | Optional external reference/line number. |
| `current_status` | `varchar(20)` | `NOT NULL` | Enum `available/reserved/issued/consumed/returned/damaged`. |
| `current_warehouse_id` | `bigint` | nullable, FK to `inventory_warehouse(id)` | Where the serial currently resides. |
| `current_warehouse_code` | `varchar(5)` | nullable | Cached warehouse code. |
| `current_company_unit_id` | `bigint` | nullable, FK to `shared_companyunit(id)` | Department holding the serial when not in warehouse. |
| `current_company_unit_code` | `varchar(8)` | nullable | Cached unit code. |
| `current_document_type` | `varchar(30)` | nullable | Document currently reserving/holding serial. |
| `current_document_id` | `bigint` | nullable | Document PK reference. |
| `current_document_code` | `varchar(30)` | nullable | Human readable document code. |
| `last_moved_at` | `timestamp with time zone` | nullable | Last inventory movement timestamp. |
| `metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Extensible attributes (warranty, notes, asset tags). |
| `is_enabled` | `smallint` | `NOT NULL`, default `1` | Soft delete. |
| `enabled_at` / `enabled_by_id` | timestamp / bigint | nullable | Latest enable audit. |
| `disabled_at` / `disabled_by_id` | timestamp / bigint | nullable | Disable audit. |
| `created_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Creation timestamp. |
| `created_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Creator reference. |
| `edited_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Last modification timestamp. |
| `edited_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Last editor reference. |

Indexes & constraints:

- Unique constraint on `(company_id, serial_code)`.
- Index on `(company_id, item_id, current_status)` for availability lookups.
- Index on `(company_id, receipt_document_id)` for traceability.

Workflow notes:

- Serial records are auto-generated when permanent receipts for serial-tracked items are locked.
- During issue creation, selected serials are set to `reserved`; on document lock they transition to `issued` or `consumed`.
- Returning or adjusting serials toggles status and keeps full audit trail via history table.

#### Table: `inventory_item_serial_history`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `company_id` | `bigint` | `NOT NULL`, FK to `invproj_company(id)` | Company scope. |
| `company_code` | `varchar(8)` | `NOT NULL` | Cached company code. |
| `serial_id` | `bigint` | `NOT NULL`, FK to `inventory_item_serial(id)` | Serial reference. |
| `item_id` | `bigint` | `NOT NULL`, FK to `inventory_item(id)` | Item reference. |
| `item_code` | `varchar(16)` | `NOT NULL` | Cached item code. |
| `event_type` | `varchar(30)` | `NOT NULL` | Enum: `created/reserved/released/issued/consumed/returned/adjusted`. |
| `event_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | When the event occurred. |
| `from_status` | `varchar(20)` | nullable | Status before change. |
| `to_status` | `varchar(20)` | nullable | Status after change. |
| `reference_document_type` | `varchar(30)` | nullable | Document causing the change. |
| `reference_document_id` | `bigint` | nullable | Document PK. |
| `reference_document_code` | `varchar(30)` | nullable | Human readable code. |
| `from_warehouse_code` | `varchar(5)` | nullable | Previous warehouse code. |
| `to_warehouse_code` | `varchar(5)` | nullable | New warehouse code. |
| `from_company_unit_code` | `varchar(8)` | nullable | Previous company unit. |
| `to_company_unit_code` | `varchar(8)` | nullable | New company unit. |
| `notes` | `text` | nullable | Free-form comments. |
| `metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Additional structured info. |
| `created_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Creation timestamp. |
| `created_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Event actor. |
| `edited_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Last modification timestamp. |
| `edited_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Last editor. |

Usage:

- Append a row for every serial lifecycle change (creation, reservation, release, issue, consumption, return).
- Acts as immutable audit log to reconstruct serial trajectory and support regulatory/compliance audits.

#### Table: `inventory_receipt_temporary`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `company_id` | `bigint` | `NOT NULL`, FK to `invproj_company(id)` | Owning company for the transaction. |
| `company_code` | `varchar(3)` | `NOT NULL`, check numeric | Cached company code for reporting. |
| `document_code` | `varchar(20)` | `NOT NULL`, `UNIQUE` | Human-readable temporary receipt identifier. |
| `document_date` | `date` | `NOT NULL` | Document creation date (goods arrival). |
| `item_id` | `bigint` | `NOT NULL`, FK to `inventory_item(id)` | Item being received temporarily. |
| `item_code` | `varchar(16)` | `NOT NULL` | Cached item composite code. |
| `warehouse_id` | `bigint` | `NOT NULL`, FK to `inventory_warehouse(id)` | Destination warehouse (quarantine/staging). |
| `warehouse_code` | `varchar(5)` | `NOT NULL` | Cached warehouse public code. |
| `unit` | `varchar(30)` | `NOT NULL` | Unit of measure for the temporary receipt. |
| `quantity` | `numeric(18,6)` | `NOT NULL` | Quantity received pending inspection. |
| `entered_unit` | `varchar(30)` | nullable | Unit selected by the end-user; used for display while `unit` stores the normalized base unit. |
| `entered_quantity` | `numeric(18,6)` | nullable | Quantity entered by the user before unit normalization. |
| `expected_receipt_date` | `date` | nullable | Planned date for conversion to permanent receipt. |
| `supplier_id` | `bigint` | nullable, FK to `inventory_supplier(id)` | Supplier providing the shipment. |
| `supplier_code` | `varchar(6)` | nullable | Cached supplier public code. |
| `source_document_type` | `varchar(60)` | nullable | Originating document type (e.g., PO, transfer). |
| `source_document_code` | `varchar(30)` | nullable | Human-readable reference to originating document. |
| `status` | `smallint` | `NOT NULL`, default `0`, check in (0,1,2) | Workflow state (0=draft, 1=awaiting inspection, 2=closed/cancelled). |
| `inspection_result` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Holds QC findings, measured values, approvals. |
| `document_metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Additional contextual fields (carrier, seal numbers). |
| `notes` | `text` | nullable | Operational notes. |
| `qc_approved_by_id` | `bigint` | nullable, FK to `invproj_user(id)` | QC approver when inspection passes. |
| `qc_approved_at` | `timestamp with time zone` | nullable | Timestamp of QC approval. |
| `qc_approval_notes` | `text` | nullable | Additional comments from QC approver. |
| `is_converted` | `smallint` | `NOT NULL`, default `0`, check in (0,1) | Flags whether a permanent receipt has been generated. |
| `converted_receipt_id` | `bigint` | nullable, FK to `inventory_receipt_permanent(id)` | Linked permanent receipt. |
| `converted_receipt_code` | `varchar(20)` | nullable | Cached permanent receipt document code. |
| `is_locked` | `smallint` | `NOT NULL`, default `0`, check in (0,1) | Prevents edits after QC approval. |
| `is_enabled` | `smallint` | `NOT NULL`, default `1`, check in (0,1) | Soft-delete flag. |
| `activated_at` | `timestamp with time zone` | nullable | Last enable timestamp. |
| `deactivated_at` | `timestamp with time zone` | nullable | Last disable timestamp. |
| `created_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Auto-populated on insert. |
| `edited_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Update audit (trigger/logic). |
| `created_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Creator reference. |
| `edited_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Last editor reference. |
| `metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Extensible attributes (e.g., inspection checklist ids). |

Additional considerations:

- Unique constraint on `(company_id, document_code)` to avoid duplicate temporary receipt numbers.
- Maintain referential integrity when converting temporary receipts to permanent receipts (`converted_receipt_id`).
- Enforce application logic so `item_id`, `warehouse_id`, and `supplier_id` belong to the same `company_id`.
- Track inspection workflow transitions by updating `status`, `inspection_result`, and `is_locked` together.
- Require QC approval (`qc_approved_by_id`, `qc_approved_at`) before allowing conversion to a permanent receipt.
- Consider adding line-item detail table if temporary receipts can bundle multiple items.
- کد سند (`TMP-YYYYMM-XXXXXX`) و تاریخ در لایه‌ی کاربردی به صورت خودکار تعیین می‌شود و مقدار/واحد واردشده توسط کاربر از طریق منطق فرم به واحد اصلی کالا تبدیل و ذخیره می‌شود.
- مقادیر خام کاربر در فیلدهای `entered_unit` و `entered_quantity` نگه داشته می‌شوند تا در رابط کاربری نمایش داده شوند یا برای ممیزی قابل استفاده باشند.

#### Table: `inventory_receipt_consignment`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `company_id` | `bigint` | `NOT NULL`, FK to `invproj_company(id)` | Owning company for the consignment receipt. |
| `company_code` | `varchar(3)` | `NOT NULL`, check numeric | Cached company code for reporting and numbering. |
| `document_code` | `varchar(20)` | `NOT NULL`, `UNIQUE` | Human-readable consignment receipt identifier. |
| `document_date` | `date` | `NOT NULL` | Document creation/arrival date. |
| `item_id` | `bigint` | `NOT NULL`, FK to `inventory_item(id)` | Consigned item reference. |
| `item_code` | `varchar(16)` | `NOT NULL` | Cached item composite code. |
| `warehouse_id` | `bigint` | `NOT NULL`, FK to `inventory_warehouse(id)` | Warehouse holding the consigned goods (often dedicated consignment zone). |
| `warehouse_code` | `varchar(5)` | `NOT NULL` | Cached warehouse public code. |
| `unit` | `varchar(30)` | `NOT NULL` | Unit of measure for the consigned goods. |
| `quantity` | `numeric(18,6)` | `NOT NULL` | Quantity received on consignment. |
| `entered_unit` | `varchar(30)` | nullable | User-entered unit before normalization. |
| `entered_quantity` | `numeric(18,6)` | nullable | User-entered quantity prior to conversion. |
| `entered_unit_price` | `numeric(18,6)` | nullable | User-entered price (before normalization to base unit). |
| `supplier_id` | `bigint` | `NOT NULL`, FK to `inventory_supplier(id)` | Consignor/supplier reference. |
| `supplier_code` | `varchar(6)` | `NOT NULL` | Cached supplier public code. |
| `consignment_contract_code` | `varchar(30)` | nullable | Contract or agreement identifier governing the consignment. |
| `expected_return_date` | `date` | nullable | Planned date to return or convert consigned goods. |
| `valuation_method` | `varchar(30)` | nullable | Method for valuing consigned stock (e.g., zero, estimated). |
| `unit_price_estimate` | `numeric(18,6)` | nullable | Estimated price for reporting (not yet invoiced). |
| `currency` | `varchar(3)` | nullable | Currency (choices: `IRT`=Toman, `IRR`=Rial, `USD`=US Dollar). |
| `requires_temporary_receipt` | `smallint` | `NOT NULL`, default `0`, check in (0,1) | Indicates if this consignment entry must route through a temporary receipt workflow before activation. |
| `temporary_receipt_id` | `bigint` | nullable, FK to `inventory_receipt_temporary(id)` | Linked temporary receipt if QC process required. |
| `temporary_receipt_code` | `varchar(20)` | nullable | Cached temporary receipt code. |
| `purchase_request_id` | `bigint` | nullable, FK to `inventory_purchase_request(id)` | Purchase request that initiated the consignment. |
| `purchase_request_code` | `varchar(20)` | nullable | Cached purchase request code. |
| `warehouse_request_id` | `bigint` | nullable, FK to `inventory_warehouse_request(id)` | Internal warehouse request that supplied the consignment. |
| `warehouse_request_code` | `varchar(20)` | nullable | Cached warehouse request code. |
| `ownership_status` | `varchar(30)` | `NOT NULL`, default `'consigned'` | Ownership state (`consigned`, `converted`, `returned`). |
| `conversion_receipt_id` | `bigint` | nullable, FK to `inventory_receipt_permanent(id)` | Permanent receipt generated when ownership transfers. |
| `conversion_receipt_code` | `varchar(20)` | nullable | Cached permanent receipt document code. |
| `conversion_date` | `date` | nullable | Date ownership transferred to the company. |
| `return_document_id` | `bigint` | nullable | Reference to outbound document when consigned goods are returned (placeholder for future module). |
| `document_metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Additional context (carrier, responsibility clauses). |
| `notes` | `text` | nullable | Operational notes. |
| `is_locked` | `smallint` | `NOT NULL`, default `0`, check in (0,1) | Prevents edits after conversion or return. |
| `is_enabled` | `smallint` | `NOT NULL`, default `1`, check in (0,1) | Soft-delete flag. |
| `activated_at` | `timestamp with time zone` | nullable | Last enable timestamp. |
| `deactivated_at` | `timestamp with time zone` | nullable | Last disable timestamp. |
| `created_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Auto-populated on insert. |
| `edited_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Update audit (trigger/logic). |
| `created_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Creator reference. |
| `edited_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Last editor reference. |
| `metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Extensible fields (insurance, storage conditions). |

Additional considerations:

- Unique constraint on `(company_id, document_code)` to avoid duplicate consignment receipt numbers.
- For items with `requires_temporary_receipt=1`, enforce linkage to `inventory_receipt_temporary` before updating `ownership_status` to `consigned`.
- Ensure `item_id`, `warehouse_id`, and `supplier_id` belong to the same `company_id`; consigned stock must remain tenant-isolated.
- When ownership converts (`conversion_receipt_id`), update `ownership_status` and lock the consignment record.
- Track returns via `return_document_id` once the outbound/return module is defined.
- Consider line-item table if consignment receipts can bundle multiple SKUs per document.
- If linked to a purchase request, synchronize fulfillment quantities and approval trails.
- If linked to a warehouse request, validate that the request is approved/locked and matches both item and warehouse before allowing the relationship.
- مانند سایر رسیدها، کد سند (`CON-YYYYMM-XXXXXX`) و تاریخ به صورت خودکار تولید می‌شود و مقدار/قیمت واردشده در صورت استفاده از واحد جایگزین به واحد اصلی کالا تبدیل می‌گردد تا گزارش مالی امانی با موجودی دائمی قابل مقایسه باشد.
- مقادیر ورودی کاربر در فیلدهای `entered_unit`, `entered_quantity`, `entered_unit_price` ذخیره می‌شوند تا برای نمایش و ممیزی در دسترس باشند.

### Inventory Issues (Outbound Transactions)

#### Table: `inventory_issue_permanent`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `company_id` | `bigint` | `NOT NULL`, FK to `invproj_company(id)` | Owning company for the outbound document. |
| `company_code` | `varchar(3)` | `NOT NULL`, check numeric | Cached company code for numbering and reporting. |
| `document_code` | `varchar(20)` | `NOT NULL`, `UNIQUE` | Human-readable permanent issue identifier. |
| `document_date` | `date` | `NOT NULL` | Document issuance date. |
| `item_id` | `bigint` | `NOT NULL`, FK to `inventory_item(id)` | Item being issued from inventory. |
| `item_code` | `varchar(16)` | `NOT NULL` | Cached item composite code. |
| `warehouse_id` | `bigint` | `NOT NULL`, FK to `inventory_warehouse(id)` | Warehouse shipping the goods. |
| `warehouse_code` | `varchar(5)` | `NOT NULL` | Cached warehouse public code. |
| `unit` | `varchar(30)` | `NOT NULL` | Unit of measure for the issue. |
| `quantity` | `numeric(18,6)` | `NOT NULL` | Quantity being issued. |
| `entered_unit` | `varchar(30)` | nullable | Unit selected by the operator prior to normalization. |
| `entered_quantity` | `numeric(18,6)` | nullable | Quantity entered by the operator prior to normalization. |
| `entered_unit_price` | `numeric(18,6)` | nullable | Original unit price entered by the operator. |
| `destination_type` | `varchar(30)` | `NOT NULL` | Target entity classification (`customer`, `production`, `transfer`, etc.). |
| `destination_id` | `bigint` | nullable | Reference to downstream entity (customer order, production batch). |
| `destination_code` | `varchar(30)` | nullable | Cached code for destination reference. |
| `reason_code` | `varchar(30)` | nullable | Reason for issue (e.g., sales order, scrap). |
| `department_unit_id` | `bigint` | nullable, FK to `shared_companyunit(id)` | Optional organizational unit receiving the goods. |
| `department_unit_code` | `varchar(8)` | nullable | Cached company unit code for reporting. |
| `unit_price` | `numeric(18,6)` | nullable | Valuation per unit at time of issue. |
| `currency` | `varchar(3)` | nullable | Currency of valuation (choices: `IRT`=Toman, `IRR`=Rial, `USD`=US Dollar). |
| `tax_amount` | `numeric(18,6)` | nullable | Tax associated with the issue (if applicable). |
| `discount_amount` | `numeric(18,6)` | nullable | Applied discount. |
| `total_amount` | `numeric(18,6)` | nullable | Total value (quantity * unit_price - discount + tax). |
| `issue_metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Additional fields (sales order references, shipment details). |
| `notes` | `text` | nullable | Operational notes. |
| `is_locked` | `smallint` | `NOT NULL`, default `0`, check in (0,1) | Prevents edits after posting/finalization. |
| `is_enabled` | `smallint` | `NOT NULL`, default `1`, check in (0,1)` | Soft-delete flag. |
| `activated_at` | `timestamp with time zone` | nullable | Last enable timestamp. |
| `deactivated_at` | `timestamp with time zone` | nullable | Last disable timestamp. |
| `created_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Auto-populated on insert. |
| `created_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Creator reference. |
| `edited_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Update audit. |
| `edited_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Last editor reference. |
| `metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Extensible attributes (approvals, carrier info). |

Additional considerations:

- Unique constraint on `(company_id, document_code)` to prevent duplicates.
- Ensure `item_id`, `warehouse_id`, and destination references align with company boundaries.
- Consider child table for multiple line items per document.
- Locking should sync with inventory valuation and accounting.
- If the issued item has `has_lot_tracking=1`, require selection of lot codes from `inventory_item_lot` and update their status to `consumed` or `reserved` accordingly.
- در صورت ثبت واحد سازمانی، هماهنگی کد (`department_unit_code`) با رکورد انتخابی باید توسط برنامه تضمین شود تا گزارش‌ها سازگار باقی بمانند.

#### Table: `inventory_issue_consumption`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `company_id` | `bigint` | `NOT NULL`, FK to `invproj_company(id)` | Owning company. |
| `company_code` | `varchar(3)` | `NOT NULL`, check numeric | Cached company code. |
| `document_code` | `varchar(20)` | `NOT NULL`, `UNIQUE` | Human-readable consumption issue identifier. |
| `document_date` | `date` | `NOT NULL` | Date of consumption. |
| `item_id` | `bigint` | `NOT NULL`, FK to `inventory_item(id)` | Item consumed. |
| `item_code` | `varchar(16)` | `NOT NULL` | Cached item code. |
| `warehouse_id` | `bigint` | `NOT NULL`, FK to `inventory_warehouse(id)` | Warehouse consuming the item. |
| `warehouse_code` | `varchar(5)` | `NOT NULL` | Cached warehouse code. |
| `unit` | `varchar(30)` | `NOT NULL` | Unit of measure. |
| `quantity` | `numeric(18,6)` | `NOT NULL` | Quantity consumed. |
| `consumption_type` | `varchar(30)` | `NOT NULL` | Classification (e.g., production WIP, maintenance, scrap). |
| `department_unit_id` | `bigint` | nullable, FK to `shared_companyunit(id)` | Optional department/unit requesting the material. |
| `department_unit_code` | `varchar(8)` | nullable | Cached company unit code. |
| `work_line_id` | `bigint` | nullable, FK to `inventory_workline(id)` | Optional production/work line reference. |
| `work_line_code` | `varchar(5)` | nullable | Cached work line public code. |
| `reference_document_type` | `varchar(30)` | nullable | Upstream reference (work order, maintenance order). |
| `reference_document_id` | `bigint` | nullable | FK to upstream document if tracked. |
| `reference_document_code` | `varchar(30)` | nullable | Cached code for upstream reference. |
| `production_transfer_id` | `bigint` | nullable, FK to `production_transfer_to_line(id)` | Linked transfer document that supplied materials to the line. |
| `production_transfer_code` | `varchar(30)` | nullable | Cached transfer document code. |
| `unit_cost` | `numeric(18,6)` | nullable | Cost per unit at time of consumption. |
| `total_cost` | `numeric(18,6)` | nullable | Aggregate cost. |
| `cost_center_code` | `varchar(30)` | nullable | Cost center assignment. |
| `issue_metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Additional fields (shift, machine, batch). |
| `notes` | `text` | nullable | Operational notes. |
| `is_locked` | `smallint` | `NOT NULL`, default `0`, check in (0,1) | Locks the document once finalized. |
| `is_enabled` | `smallint` | `NOT NULL`, default `1`, check in (0,1) | Soft-delete flag. |
| `activated_at` | `timestamp with time zone` | nullable | Last enable timestamp. |
| `deactivated_at` | `timestamp with time zone` | nullable | Last disable timestamp. |
| `created_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Auto-populated on insert. |
| `created_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Creator reference. |
| `edited_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Update audit. |
| `edited_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Last editor reference. |
| `metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Extensible attributes. |

Additional considerations:

- Unique constraint on `(company_id, document_code)` to ensure uniqueness.
- Consumption documents often reduce WIP or expense accounts; coordinate with accounting.
- If multiple items per document are expected, model header/line structure.
- Tie to production orders or maintenance tasks for traceability.
- Enforce lot selection for items with `has_lot_tracking=1`; validations must confirm lot availability and update `inventory_item_lot` status and `issue_document_*` fields.
- When `production_transfer_id` is provided, enforce company alignment and reconcile consumed quantities against the transfer document for audit.
- اگر `work_line_id` مقدار داشته باشد، سیستم باید مطمئن شود خط انتخاب‌شده متعلق به همان انبار است و در صورت تغییر انبار، گزینه‌های خط فیلتر شوند.

#### Table: `inventory_issue_consignment`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `company_id` | `bigint` | `NOT NULL`, FK to `invproj_company(id)` | Owning company. |
| `company_code` | `varchar(3)` | `NOT NULL`, check numeric | Cached company code. |
| `document_code` | `varchar(20)` | `NOT NULL`, `UNIQUE` | Human-readable consignment issue identifier. |
| `document_date` | `date` | `NOT NULL` | Document date. |
| `item_id` | `bigint` | `NOT NULL`, FK to `inventory_item(id)` | Consigned item being shipped out. |
| `item_code` | `varchar(16)` | `NOT NULL` | Cached item code. |
| `warehouse_id` | `bigint` | `NOT NULL`, FK to `inventory_warehouse(id)` | Warehouse dispatching the consigned goods. |
| `warehouse_code` | `varchar(5)` | `NOT NULL` | Cached warehouse code. |
| `unit` | `varchar(30)` | `NOT NULL` | Unit of measure. |
| `quantity` | `numeric(18,6)` | `NOT NULL` | Quantity issued. |
| `consignment_receipt_id` | `bigint` | `NOT NULL`, FK to `inventory_receipt_consignment(id)` | Links back to the consignment receipt. |
| `consignment_receipt_code` | `varchar(20)` | `NOT NULL` | Cached consignment receipt code. |
| `destination_type` | `varchar(30)` | `NOT NULL` | Receiving entity classification (e.g., "customer_return", "supplier_return"). |
| `destination_id` | `bigint` | nullable | Reference to downstream entity. |
| `destination_code` | `varchar(30)` | nullable | Cached downstream reference code. |
| `reason_code` | `varchar(30)` | nullable | Reason for consignment issue (return, usage). |
| `department_unit_id` | `bigint` | nullable, FK to `shared_companyunit(id)` | Optional organizational unit receiving the consigned goods. |
| `department_unit_code` | `varchar(8)` | nullable | Cached unit code for reporting. |
| `issue_metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Additional fields (carrier, authorizations). |
| `notes` | `text` | nullable | Operational notes. |
| `is_locked` | `smallint` | `NOT NULL`, default `0`, check in (0,1) | Locks after completion. |
| `is_enabled` | `smallint` | `NOT NULL`, default `1`, check in (0,1)` | Soft-delete flag. |
| `activated_at` | `timestamp with time zone` | nullable | Last enable timestamp. |
| `deactivated_at` | `timestamp with time zone` | nullable | Last disable timestamp. |
| `created_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Auto-populated on insert. |
| `edited_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Update audit. |
| `created_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Creator reference. |
| `edited_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Last editor reference. |
| `metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Extensible attributes. |

Additional considerations:

- Unique constraint on `(company_id, document_code)` to avoid duplicates.
- Link to consignment receipt ensures traceability and ownership updates.
- Ensure consignment issue updates ownership status and locks related receipt if goods are returned or consumed.
- Consider line structure for multiple items per issue document.
- اگر مقصد داخلی انتخاب شود، `department_unit_id` باید با شرکت فعال همسان باشد؛ فرانت‌اند باید کد واحد را نیز در فیلد `department_unit_code` همگام کند.

### Inventory Stocktaking Adjustments

#### Table: `inventory_stocktaking_deficit`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `company_id` | `bigint` | `NOT NULL`, FK to `invproj_company(id)` | Owning company. |
| `company_code` | `varchar(3)` | `NOT NULL`, check numeric | Cached company code. |
| `document_code` | `varchar(20)` | `NOT NULL`, `UNIQUE` | Human-readable deficit adjustment identifier. |
| `document_date` | `date` | `NOT NULL` | Date of adjustment. |
| `stocktaking_session_id` | `bigint` | nullable | Reference to stocktaking campaign/session table (to be defined). |
| `item_id` | `bigint` | `NOT NULL`, FK to `inventory_item(id)` | Item with measured deficit. |
| `item_code` | `varchar(16)` | `NOT NULL` | Cached item code. |
| `warehouse_id` | `bigint` | `NOT NULL`, FK to `inventory_warehouse(id)` | Warehouse where deficit was observed. |
| `warehouse_code` | `varchar(5)` | `NOT NULL` | Cached warehouse code. |
| `unit` | `varchar(30)` | `NOT NULL` | Unit of measure. |
| `quantity_expected` | `numeric(18,6)` | `NOT NULL` | Quantity per book balance. |
| `quantity_counted` | `numeric(18,6)` | `NOT NULL` | Physical counted quantity. |
| `quantity_adjusted` | `numeric(18,6)` | `NOT NULL` | Adjustment quantity (expected - counted). |
| `valuation_method` | `varchar(30)` | nullable | Method used for cost valuation. |
| `unit_cost` | `numeric(18,6)` | nullable | Cost per unit for adjustment. |
| `total_cost` | `numeric(18,6)` | nullable | Total cost impact (quantity_adjusted * unit_cost). |
| `reason_code` | `varchar(30)` | nullable | Reason classification (e.g., shrinkage, damage). |
| `investigation_reference` | `varchar(30)` | nullable | Link to investigation or incident report. |
| `adjustment_metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Extra info (count team, shift, notes). |
| `notes` | `text` | nullable | Additional comments. |
| `is_locked` | `smallint` | `NOT NULL`, default `0`, check in (0,1)` | Lock flag after confirmation. |
| `is_enabled` | `smallint` | `NOT NULL`, default `1`, check in (0,1)` | Soft-delete flag. |
| `activated_at` | `timestamp with time zone` | nullable | Last enable timestamp. |
| `deactivated_at` | `timestamp with time zone` | nullable | Last disable timestamp. |
| `created_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Auto-populated on insert. |
| `created_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Creator reference. |
| `edited_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Update audit. |
| `edited_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Last editor reference. |
| `metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Extensible attributes (approvals, attachments). |

Additional considerations:

- Unique constraint on `(company_id, document_code)` ensures unique deficit documents per company.
- `quantity_adjusted` should be validated as `quantity_expected - quantity_counted`; application logic can enforce sign/precision.
- Lock actions should update inventory balances and record accounting impact.
- Consider linking to audit trails or incident management for investigation of losses.
- Introduce header/line structure if multiple items are adjusted per document.

#### Table: `inventory_stocktaking_surplus`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `company_id` | `bigint` | `NOT NULL`, FK to `invproj_company(id)` | Owning company. |
| `company_code` | `varchar(3)` | `NOT NULL`, check numeric | Cached company code. |
| `document_code` | `varchar(20)` | `NOT NULL`, `UNIQUE` | Human-readable surplus adjustment identifier. |
| `document_date` | `date` | `NOT NULL` | Date of adjustment. |
| `stocktaking_session_id` | `bigint` | nullable | Reference to stocktaking session. |
| `item_id` | `bigint` | `NOT NULL`, FK to `inventory_item(id)` | Item with surplus. |
| `item_code` | `varchar(16)` | `NOT NULL` | Cached item code. |
| `warehouse_id` | `bigint` | `NOT NULL`, FK to `inventory_warehouse(id)` | Warehouse where surplus observed. |
| `warehouse_code` | `varchar(5)` | `NOT NULL` | Cached warehouse code. |
| `unit` | `varchar(30)` | `NOT NULL` | Unit of measure. |
| `quantity_expected` | `numeric(18,6)` | `NOT NULL` | Book quantity. |
| `quantity_counted` | `numeric(18,6)` | `NOT NULL` | Physical count quantity. |
| `quantity_adjusted` | `numeric(18,6)` | `NOT NULL` | Adjustment quantity (counted - expected). |
| `valuation_method` | `varchar(30)` | nullable | Cost valuation method. |
| `unit_cost` | `numeric(18,6)` | nullable | Cost per unit used for valuation. |
| `total_cost` | `numeric(18,6)` | nullable | Total valuation impact. |
| `reason_code` | `varchar(30)` | nullable | Reason classification (e.g., counting error, unrecorded receipt). |
| `investigation_reference` | `varchar(30)` | nullable | Link to investigation or corrective action. |
| `adjustment_metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Additional info (count team, remarks). |
| `notes` | `text` | nullable | Additional comments. |
| `is_locked` | `smallint` | `NOT NULL`, default `0`, check in (0,1)` | Locks after confirmation. |
| `is_enabled` | `smallint` | `NOT NULL`, default `1`, check in (0,1)` | Soft-delete flag. |
| `activated_at` | `timestamp with time zone` | nullable | Last enable timestamp. |
| `deactivated_at` | `timestamp with time zone` | nullable | Last disable timestamp. |
| `created_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Auto-populated on insert. |
| `created_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Creator reference. |
| `edited_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Update audit. |
| `edited_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Last editor reference. |
| `metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Extensible attributes (approvals, attachments). |

Additional considerations:

- Unique constraint on `(company_id, document_code)` ensures unique surplus documents per company.
- `quantity_adjusted` should be validated as `quantity_counted - quantity_expected`; positive quantities increase inventory.
- Integrate with accounting/valuation when posting to recognize inventory gains.
- Should tie back to stocktaking sessions for auditability.
- Explore header/line split if needed for multi-item adjustments.

#### Table: `inventory_stocktaking_record`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `company_id` | `bigint` | `NOT NULL`, FK to `invproj_company(id)` | Owning company. |
| `company_code` | `varchar(3)` | `NOT NULL`, check numeric | Cached company code. |
| `document_code` | `varchar(20)` | `NOT NULL`, `UNIQUE` | Human-readable stocktaking confirmation identifier. |
| `document_date` | `date` | `NOT NULL` | Date of confirmation after stocktaking. |
| `stocktaking_session_id` | `bigint` | `NOT NULL` | Reference to the stocktaking campaign/session being certified. |
| `inventory_snapshot_time` | `timestamp with time zone` | `NOT NULL` | Timestamp when the system inventory snapshot was validated. |
| `confirmed_by_id` | `bigint` | `NOT NULL`, FK to `invproj_person(id)` | Person approving the accuracy of the counts. |
| `confirmed_by_code` | `varchar(8)` | `NOT NULL` | Cached personnel public code. |
| `confirmation_notes` | `text` | nullable | Remarks about the confirmation. |
| `variance_document_ids` | `jsonb` | `NOT NULL`, default `'[]'::jsonb` | Array of deficit/surplus document IDs tied to this session. |
| `variance_document_codes` | `jsonb` | `NOT NULL`, default `'[]'::jsonb` | Array of human-readable codes for traceability. |
| `final_inventory_value` | `numeric(20,4)` | nullable | Valuation of inventory at the time of confirmation. |
| `approval_status` | `varchar(20)` | `NOT NULL`, default `'pending'` | Workflow state (`pending`, `approved`, `rejected`). |
| `approved_at` | `timestamp with time zone` | nullable | Timestamp when confirmation was approved. |
| `approver_id` | `bigint` | nullable, FK to `invproj_person(id)` | Higher-level approver if required. |
| `approver_notes` | `text` | nullable | Notes from approver. |
| `record_metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Additional attributes (sign-off attachments, audit references). |
| `is_locked` | `smallint` | `NOT NULL`, default `0`, check in (0,1) | Prevents edits after approval. |
| `is_enabled` | `smallint` | `NOT NULL`, default `1`, check in (0,1) | Soft-delete flag. |
| `activated_at` | `timestamp with time zone` | nullable | Last enable timestamp. |
| `deactivated_at` | `timestamp with time zone` | nullable | Last disable timestamp. |
| `created_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Auto-populated on insert. |
| `edited_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Update audit. |
| `created_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Creator reference. |
| `edited_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Last editor reference. |
| `metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Extensible attributes. |

Additional considerations:

- Unique constraint on `(company_id, document_code)` ensures unique confirmations.
- `stocktaking_session_id` should link to session header capturing scope, schedule, and participants.
- `variance_document_ids` / `variance_document_codes` provide audit trail tying deficits/surplus adjustments to the sign-off; maintain referential integrity where possible.
- Workflow should require all variance documents to be resolved before approval.
- Once approved, freeze relevant inventory balances in reporting to match certified counts.

#### Table: `inventory_warehouse_request`

|| Column | Type | Constraints | Notes |
|| --- | --- | --- | --- |
|| `id` | `bigserial` | PK | Auto-increment surrogate key. |
|| `company_id` | `bigint` | `NOT NULL`, FK to `invproj_company(id)` | Owning company. |
|| `company_code` | `varchar(3)` | `NOT NULL`, check numeric | Cached company code. |
|| `request_code` | `varchar(20)` | `NOT NULL`, `UNIQUE` | Human-readable request identifier (auto-generated). |
|| `request_date` | `date` | `NOT NULL` | Date when the request was created. |
|| `item_id` | `bigint` | `NOT NULL`, FK to `inventory_item(id)` | Item being requested. |
|| `item_code` | `varchar(16)` | `NOT NULL` | Cached item code for reporting. |
|| `quantity_requested` | `numeric(15,3)` | `NOT NULL`, check `> 0` | Quantity requested from warehouse. |
|| `unit` | `varchar(20)` | `NOT NULL` | Unit of measure (must match item unit). |
|| `warehouse_id` | `bigint` | `NOT NULL`, FK to `inventory_warehouse(id)` | Source warehouse. |
|| `warehouse_code` | `varchar(8)` | `NOT NULL` | Cached warehouse code. |
|| `requester_id` | `bigint` | `NOT NULL`, FK to `invproj_person(id)` | Person making the request. |
|| `requester_code` | `varchar(8)` | `NOT NULL` | Cached requester personnel code. |
|| `approver_id` | `bigint` | nullable, FK to `invproj_person(id)` | Intended approver responsible for confirming the request. |
|| `approver_code` | `varchar(8)` | nullable | Cached approver personnel code. |
|| `department_unit_id` | `bigint` | nullable, FK to `invproj_company_unit(id)` | Department/unit requesting material. |
|| `department_unit_code` | `varchar(8)` | nullable | Cached department code. |
|| `priority` | `varchar(20)` | `NOT NULL`, default `'normal'` | Priority level (`low`, `normal`, `high`, `urgent`). |
|| `needed_by_date` | `date` | nullable | Date when material is needed. |
|| `purpose` | `text` | nullable | Reason/purpose for the request (maintenance, production support, etc.). |
|| `request_status` | `varchar(20)` | `NOT NULL`, default `'draft'` | Workflow state (`draft`, `submitted`, `approved`, `issued`, `rejected`, `cancelled`). |
|| `submitted_at` | `timestamp with time zone` | nullable | When request moved from draft to submitted. |
|| `approved_at` | `timestamp with time zone` | nullable | When request was approved. |
|| `approved_by_id` | `bigint` | nullable, FK to `invproj_person(id)` | Approver reference. |
|| `approved_by_code` | `varchar(8)` | nullable | Cached approver personnel code. |
|| `approval_notes` | `text` | nullable | Comments from approver. |
|| `rejected_at` | `timestamp with time zone` | nullable | When request was rejected. |
|| `rejected_by_id` | `bigint` | nullable, FK to `invproj_person(id)` | Rejector reference. |
|| `rejection_reason` | `text` | nullable | Reason for rejection. |
|| `issued_at` | `timestamp with time zone` | nullable | When material was issued from warehouse. |
|| `issue_document_id` | `bigint` | nullable, FK to `inventory_issue_permanent(id)` or similar | Link to the issue document fulfilling this request. |
|| `issue_document_code` | `varchar(20)` | nullable | Cached issue document code. |
|| `quantity_issued` | `numeric(15,3)` | nullable, check `>= 0` | Actual quantity issued (may differ from requested). |
|| `cancelled_at` | `timestamp with time zone` | nullable | When request was cancelled. |
|| `cancelled_by_id` | `bigint` | nullable, FK to `invproj_person(id)` | Person who cancelled. |
|| `cancellation_reason` | `text` | nullable | Reason for cancellation. |
|| `notes` | `text` | nullable | Additional notes/instructions. |
|| `attachments` | `jsonb` | `NOT NULL`, default `'[]'::jsonb` | Array of file metadata (URLs, descriptions). |
|| `request_metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Extensible attributes (cost center, project code, etc.). |
|| `is_locked` | `smallint` | `NOT NULL`, default `0`, check in (0,1) | Prevents edits after issuance. |
|| `is_enabled` | `smallint` | `NOT NULL`, default `1`, check in (0,1) | Soft-delete flag. |
|| `activated_at` | `timestamp with time zone` | nullable | Last enable timestamp. |
|| `deactivated_at` | `timestamp with time zone` | nullable | Last disable timestamp. |
|| `created_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Auto-populated on insert. |
|| `edited_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Update audit. |
|| `created_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Creator reference. |
|| `edited_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Last editor reference. |
|| `metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Extensible attributes. |

Additional considerations:

- Unique constraint on `(company_id, request_code)` ensures unique request identifiers per company.
- `request_code` follows pattern: `WRQ-YYYYMM-XXXXXX` (Warehouse Request - Year/Month - Sequence).
- Generate sequence via Django model `save()` override or database trigger.
- Status transitions: `draft` → `submitted` → `approved` → `issued` (or `rejected`/`cancelled` at any stage before issued).
- Track approval chain via `approved_by_id` and timestamps; multi-level approval can be handled via separate approval log table if needed.
- Link to issue documents via `issue_document_id` for full traceability.
- Support partial fulfillment by comparing `quantity_requested` vs `quantity_issued`.
- Index on `(company_id, request_status, needed_by_date)` for pending requests dashboard.
- Add triggers to auto-populate cached codes (`item_code`, `warehouse_code`, `requester_code`, etc.) on save.
- Integrate with notification system to alert approvers and requesters of status changes.
- Consider line-item support (header/detail split) if requests commonly include multiple items; current design assumes one item per request for simplicity.
- When approved, set `is_locked=1` to freeze the request and expose it to permanent/consignment receipt forms while preventing further edits.
- **UI Integration**: In the list view (`templates/inventory/warehouse_requests.html`), approved requests display three action buttons in the "Actions" column:
  - **"Permanent Issue"** button (blue): Creates a permanent issue document from the warehouse request
  - **"Consumption Issue"** button (green): Creates a consumption issue document from the warehouse request
  - **"Consignment Issue"** button (purple): Creates a consignment issue document from the warehouse request
- **UI Integration**: In the purchase request list view (`templates/inventory/purchase_requests.html`), approved requests display three action buttons in the "Actions" column:
  - **"Temporary Receipt"** button (green): Creates a temporary receipt from the purchase request
  - **"Permanent Receipt"** button (blue): Creates a permanent receipt from the purchase request
  - **"Consignment Receipt"** button (purple): Creates a consignment receipt from the purchase request
- These buttons route to intermediate selection views (`CreateReceiptFromPurchaseRequestView`, `CreateIssueFromWarehouseRequestView`) that allow users to select lines/quantities before creating the final document.

---

### Inventory Balance Calculation Logic

The system does not maintain a separate `inventory_balance` table. Instead, inventory balances are calculated on-demand using the following logic:

#### Starting Point: Last Stocktaking Record
- Query `inventory_stocktaking_record` for the most recent approved record for each `(company, warehouse, item)` combination
- Use `final_inventory_value` or referenced surplus/deficit documents as the baseline quantity
- If no stocktaking record exists, start from zero

#### Incremental Calculation
After identifying the baseline date from stocktaking:

**Add (Positive Movements):**
- `inventory_receipt_permanent` where `is_locked=1` and `document_date > baseline_date`
- `inventory_stocktaking_surplus` where `is_locked=1` and `document_date > baseline_date`

**Subtract (Negative Movements):**
- `inventory_issue_permanent` where `is_locked=1` and `document_date > baseline_date`
- `inventory_issue_consumption` where `is_locked=1` and `document_date > baseline_date`
- `inventory_stocktaking_deficit` where `is_locked=1` and `document_date > baseline_date`

**Formula:**
```
Current Balance = Baseline Balance (from last stocktaking)
                + Sum(Permanent Receipts)
                + Sum(Surplus Adjustments)
                - Sum(Permanent Issues)
                - Sum(Consumption Issues)
                - Sum(Deficit Adjustments)
```

#### Implementation Notes:
- Create a materialized view or Django database view for performance if inventory grows large
- Index on `(company_id, warehouse_id, item_id, document_date, is_locked)` across all document tables
- Consignment receipts/issues do NOT affect owned inventory balance (track separately if needed)
- Temporary receipts are excluded until converted to permanent
- Consider caching results with cache invalidation on document posting
- Provide UI filters for: company, warehouse, item type/category, date-as-of
- Support exporting balance snapshot to Excel/CSV for audit purposes

#### API/View Response Format:
```json
{
  "company_code": "C001",
  "warehouse_code": "WH01",
  "item_code": "001002003010001",
  "item_name": "Sample Item",
  "baseline_date": "2025-01-15",
  "baseline_quantity": 1000.0,
  "receipts_total": 250.0,
  "issues_total": 180.0,
  "adjustments_net": -20.0,
  "current_balance": 1050.0,
  "last_calculated_at": "2025-11-09T10:30:00Z"
}
```




