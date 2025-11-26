## Overview

We are designing `invproj`, a modular warehouse and production management platform built with Python and Django. The application targets PostgreSQL as the primary database engine and is expected to run seamlessly on both Linux/Nginx and Windows Server/IIS deployments. Django handles server-side rendering and API endpoints, while the architecture leaves room for eventual SPA or mobile front ends. Initially all modules share a single physical database, but careful schema boundaries and naming conventions (`inventory_`, `production_`, `qc_`, shared `invproj_`) ensure we can migrate modules into their own services or databases as the system scales. Shared/global entities—companies, personnel, users, company units—reside in the `invproj_` namespace and provide consistent tenancy, security, and configuration anchors throughout the platform.

This document presents the production control module database design for the `invproj` platform. The platform itself is a modular Python/Django system targeting PostgreSQL, deployable on both Linux/Nginx and Windows Server/IIS stacks. All modules begin in a single physical database, but strict naming conventions (`production_`, `inventory_`, `qc_`, `invproj_`) ensure that schemas can be separated into dedicated services when scaling demands it. Shared/global entities—companies, users, personnel, company units—reside in the `invproj_` namespace, providing consistent references for every module. The production module builds on these shared entities while remaining decoupled from inventory and QC modules, whose detailed schemas are documented separately.

Within this module we model production bills of materials, routings/process definitions, work-center resource requirements, production orders, order performance tracking, and material transfers from warehouse to line-side. The goal is to provide complete traceability for how each finished product is built, which resources were consumed, and how production outcomes align with planned processes. The schema outlined here is sufficient to understand the production domain independently, while still aligning with the overall project architecture and the companion inventory/QC plans.

Key design principles:

- **Multi-company tenancy**: Every production table stores `company_id` and cached `company_code`, referencing `invproj_company`, to isolate tenant data and enable future sharding.
- **Consistent auditing**: Tables include `is_enabled`, activation timestamps, creation/update metadata, and optional `metadata` (`jsonb`) for extensibility. Boolean semantics use `smallint` (0/1) to align with existing conventions and leverage PostgreSQL performance characteristics.
- **Modular boundaries**: Production tables only reference shared entities or other production tables. Cross-module dependencies occur through shared prefixes or dedicated bridge tables, enabling future database separation.
- **Workflow traceability**: Production processes (work orders, operations, quality checkpoints) require state tracking, linkage to personnel/equipment, and detailed logs for audit and analytics.
- **JSON usage**: Flexible attributes, configuration blobs, and approval payloads leverage PostgreSQL `jsonb` with appropriate indexing strategies for semi-structured data.

The sections below document each table with column-level details, constraints, and implementation notes to guide Django model creation, validation rules, and migration planning. Tables are organized to cover work order management, routing/operations, resource assignments, production reporting, and supporting reference data.

## Database Design Plan

- Define the conceptual and physical schema for the production control module (`production_` tables) plus shared dependencies (`invproj_`).
- Capture decisions about naming conventions, constraints, relationships, and indexing strategies.
- Document JSON usage patterns to leverage PostgreSQL `jsonb` features effectively.
- Track open questions or assumptions that require clarification with product and operations teams.

### Production Module

#### Personnel Management

##### Table: `production_person`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `company_id` | `bigint` | `NOT NULL`, FK to `invproj_company(id)` | Tenant company owning the personnel record. |
| `company_code` | `varchar(8)` | `NOT NULL`, check numeric | Cached company code used for cross-module joins. |
| `public_code` | `varchar(8)` | `NOT NULL`, `UNIQUE` within company, check numeric | Internal personnel code; fallback to generated sequence if absent. |
| `username` | `varchar(150)` | `NOT NULL`, `UNIQUE` within company | Personnel login identifier (if tied to authentication). |
| `first_name` | `varchar(120)` | `NOT NULL` | Local script given name. |
| `last_name` | `varchar(120)` | `NOT NULL` | Local script family name. |
| `first_name_en` | `varchar(120)` | nullable | Optional Latin transliteration. |
| `last_name_en` | `varchar(120)` | nullable | Optional Latin transliteration. |
| `national_id` | `varchar(20)` | nullable, `UNIQUE` | National identifier if applicable. |
| `personnel_code` | `varchar(30)` | nullable, `UNIQUE` | HR personnel code. |
| `email` | `varchar(254)` | nullable, `UNIQUE` | Work email address. |
| `phone_number` | `varchar(30)` | nullable | Primary contact number. |
| `mobile_number` | `varchar(30)` | nullable | Secondary/mobile contact. |
| `is_enabled` | `smallint` | `NOT NULL`, default `1`, check in (0,1) | Employment status flag. |
| `sort_order` | `smallint` | `NOT NULL`, default `0` | Ordering for listings. |
| `activated_at` | `timestamp with time zone` | nullable | Last enable timestamp. |
| `deactivated_at` | `timestamp with time zone` | nullable | Last disable timestamp. |
| `created_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Auto-populated on insert. |
| `edited_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Update audit. |
| `created_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Creator reference. |
| `edited_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Last editor reference. |
| `description` | `varchar(255)` | nullable | Short bio or role summary. |
| `notes` | `text` | nullable | HR/operational notes. |
| `metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Extensible attributes (certifications, shifts). |
| `user_id` | `bigint` | nullable, FK to `invproj_user(id)`, OneToOne | Linked user account. |

**Relationships:**
- Many-to-One: `Person` → `Company` (company_id)
- One-to-One: `Person` → `User` (user_id)
- Many-to-Many: `Person` ↔ `CompanyUnit` (via production_person_company_units)

**Additional considerations:**
- Composite unique indexes scoped by `company_id` enforce uniqueness for fields marked "UNIQUE within company".
- Personnel می‌توانند عضو چند واحد سازمانی باشند؛ رابطه‌ی چند-به-چند با جدول `invproj_company_unit` از طریق جدول میانی `production_person_company_units` پیاده‌سازی شده است.
- Validate national ID, phone, and email formats within the application layer.

##### Table: `production_person_assignment`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `company_id` | `bigint` | `NOT NULL`, FK to `invproj_company(id)` | Owning company. |
| `company_code` | `varchar(8)` | `NOT NULL`, check numeric | Cached company code for reporting consistency. |
| `person_id` | `bigint` | `NOT NULL`, FK to `production_person(id)` | Personnel reference. |
| `work_center_id` | `bigint` | `NOT NULL` | References module-specific work centers (inventory/production). |
| `work_center_type` | `varchar(30)` | `NOT NULL` | Indicates originating module (`inventory_work_line`, `production_work_center`, etc.). |
| `is_primary` | `smallint` | `NOT NULL`, default `0`, check in (0,1) | Marks main assignment. |
| `is_enabled` | `smallint` | `NOT NULL`, default `1`, check in (0,1) | Active assignment flag. |
| `assignment_start` | `date` | nullable | Start date for assignment. |
| `assignment_end` | `date` | nullable | End date for assignment. |
| `notes` | `text` | nullable | Additional remarks (shift info, responsibilities). |
| `metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Extensible assignment data (certifications, hourly limits). |
| `created_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Auto-populated on insert. |
| `edited_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Update audit. |
| `created_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Creator reference. |
| `edited_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Last editor reference. |

**Additional considerations:**
- Unique constraint on `(company_id, person_id, work_center_id, work_center_type)` prevents duplicate assignments.
- Ensure only one `is_primary=1` per person per work center type via partial unique index if needed.
- `work_center_type` supports polymorphic references; use enumerations and application logic to resolve to actual tables.
- Track assignment periods for reporting; optional history tables can capture changes over time.
- Validate `company_id` alignment with both person and work center to avoid cross-company assignments.

#### Core Resources

##### Table: `production_machine`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `company_id` | `bigint` | `NOT NULL`, FK to `invproj_company(id)` | Owning company. |
| `company_code` | `varchar(8)` | `NOT NULL`, check numeric | Cached company code. |
| `public_code` | `varchar(10)` | `NOT NULL`, `UNIQUE` within company, check numeric | Machine identifier code. |
| `name` | `varchar(180)` | `NOT NULL`, `UNIQUE` within company | Machine name (local language). |
| `name_en` | `varchar(180)` | nullable | Machine name in Latin alphabet. |
| `machine_type` | `varchar(30)` | `NOT NULL` | Classification (e.g., `cnc`, `lathe`, `milling`, `assembly`, `packaging`). |
| `work_center_id` | `bigint` | nullable, FK to `production_work_center(id)` | Assigned work center (if applicable). |
| `work_center_code` | `varchar(5)` | nullable | Cached work center code. |
| `manufacturer` | `varchar(120)` | nullable | Machine manufacturer name. |
| `model_number` | `varchar(60)` | nullable | Manufacturer model number. |
| `serial_number` | `varchar(60)` | nullable, `UNIQUE` | Machine serial number. |
| `purchase_date` | `date` | nullable | Date machine was purchased. |
| `installation_date` | `date` | nullable | Date machine was installed. |
| `capacity_specs` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Technical specifications (max load, speed, dimensions, etc.). |
| `maintenance_schedule` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Maintenance intervals and requirements. |
| `last_maintenance_date` | `date` | nullable | Date of last maintenance. |
| `next_maintenance_date` | `date` | nullable | Scheduled next maintenance date. |
| `status` | `varchar(20)` | `NOT NULL`, default `'operational'` | Machine status (`operational`, `maintenance`, `idle`, `broken`, `retired`). |
| `description` | `varchar(255)` | nullable | Short description. |
| `notes` | `text` | nullable | Operational notes. |
| `is_enabled` | `smallint` | `NOT NULL`, default `1`, check in (0,1) | Active flag. |
| `sort_order` | `smallint` | `NOT NULL`, default `0` | Ordering for listings. |
| `activated_at` | `timestamp with time zone` | nullable | Last enable timestamp. |
| `deactivated_at` | `timestamp with time zone` | nullable | Last disable timestamp. |
| `created_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Auto-populated on insert. |
| `edited_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Update audit. |
| `created_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Creator reference. |
| `edited_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Last editor reference. |
| `metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Extensible attributes (warranty info, service contracts). |

**Relationships:**
- Many-to-One: `Machine` → `Company` (company_id)
- Many-to-One: `Machine` → `WorkCenter` (work_center_id, nullable)

**Additional considerations:**
- Unique constraint on `(company_id, public_code)` and `(company_id, name)` ensures uniqueness per company.
- `capacity_specs` can store structured data like `{"max_load_kg": 500, "max_speed_rpm": 3000, "dimensions": {"length": 2000, "width": 1500, "height": 1800}}`.
- `maintenance_schedule` can store intervals like `{"daily": ["lubrication"], "weekly": ["cleaning"], "monthly": ["calibration"]}`.
- Index on `(company_id, status, work_center_id)` for filtering operational machines by work center.
- Consider linking to `ProcessStep` to track which machines are used in which production steps.

#### Table: `production_bom_material`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `company_id` | `bigint` | `NOT NULL`, FK to `invproj_company(id)` | Owning company. |
| `company_code` | `varchar(8)` | `NOT NULL`, check numeric | Cached company code for reporting. |
| `finished_item_id` | `bigint` | `NOT NULL`, FK to `inventory_item(id)` | Final product that will be produced. |
| `finished_item_code` | `varchar(16)` | `NOT NULL` | Cached code for the finished product. |
| `material_item_id` | `bigint` | `NOT NULL`, FK to `inventory_item(id)` | Raw or semi-finished material required. |
| `material_item_code` | `varchar(16)` | `NOT NULL` | Cached code for the required material. |
| `material_type` | `varchar(30)` | `NOT NULL`, default `'raw'` | Classification (`raw`, `semi_finished`, `packaging`, etc.). |
| `quantity_per_unit` | `numeric(18,6)` | `NOT NULL` | Quantity of the material needed to produce one unit of the finished product. |
| `unit` | `varchar(30)` | `NOT NULL` | Unit of measure for `quantity_per_unit`. |
| `scrap_allowance` | `numeric(5,2)` | `NOT NULL`, default `0.00` | Expected scrap percentage (0-100). |
| `sequence_order` | `smallint` | `NOT NULL`, default `0` | Ordering to support assembly steps. |
| `is_optional` | `smallint` | `NOT NULL`, default `0`, check in (0,1) | Marks optional material. |
| `is_enabled` | `smallint` | `NOT NULL`, default `1`, check in (0,1) | Soft-delete flag. |
| `effective_from` | `date` | nullable | Start date when this mapping is valid. |
| `effective_to` | `date` | nullable | End date when this mapping is valid. |
| `notes` | `text` | nullable | Additional instructions for material usage. |
| `metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Extensible attributes (alternate suppliers, quality constraints). |
| `created_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Auto-populated on insert. |
| `edited_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Update audit. |
| `created_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Creator reference. |
| `edited_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Last editor reference. |

Additional considerations:

- Unique constraint on `(company_id, finished_item_id, material_item_id, effective_from)` prevents duplicate material definitions.
- Application logic should ensure `finished_item_id` and `material_item_id` share the same `company_id`.
- Use `sequence_order` to maintain consistent sequencing when presenting materials to operators.
- `metadata` can store routing step references or substitution rules that link to inventory substitute tables.

#### Table: `production_process`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `company_id` | `bigint` | `NOT NULL`, FK to `invproj_company(id)` | Owning company. |
| `company_code` | `varchar(8)` | `NOT NULL`, check numeric | Cached company code. |
| `process_code` | `varchar(30)` | `NOT NULL`, `UNIQUE` within company | Human-readable production process identifier. |
| `finished_item_id` | `bigint` | `NOT NULL`, FK to `inventory_item(id)` | Finished/semi-finished item produced by the process. |
| `finished_item_code` | `varchar(16)` | `NOT NULL` | Cached code for the produced item. |
| `bom_code` | `varchar(30)` | `NOT NULL` | Identifier of the BOM definition used (aligns with engineering documentation). |
| `revision` | `varchar(10)` | `NOT NULL` | Process revision (e.g., `A`, `01`). |
| `description` | `varchar(255)` | nullable | Short description of the process. |
| `effective_from` | `date` | nullable | Start date when the process is valid. |
| `effective_to` | `date` | nullable | End date (for scheduled replacement). |
| `is_primary` | `smallint` | `NOT NULL`, default `0`, check in (0,1) | Flags primary process for the item. |
| `approval_status` | `varchar(20)` | `NOT NULL`, default `'draft'` | Workflow state (`draft`, `pending`, `approved`, `archived`). |
| `approved_at` | `timestamp with time zone` | nullable | Timestamp of approval. |
| `approved_by_id` | `bigint` | nullable, FK to `production_person(id)` | Approver reference. |
| `metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Extensible info (documents, routing references). |
| `notes` | `text` | nullable | Additional engineering notes. |
| `is_enabled` | `smallint` | `NOT NULL`, default `1`, check in (0,1) | Soft-delete flag. |
| `activated_at` | `timestamp with time zone` | nullable | Last enable timestamp. |
| `deactivated_at` | `timestamp with time zone` | nullable | Last disable timestamp. |
| `created_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Auto-populated on insert. |
| `edited_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Update audit. |
| `created_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Creator reference. |
| `edited_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Last editor reference. |

Additional considerations:

- Unique constraint on `(company_id, finished_item_id, revision)` to avoid duplicate process revisions.
- Enforce only one `is_primary=1` per `(company_id, finished_item_id)` via partial unique index.
- `bom_code` should correspond to the engineering BOM used; validation can ensure matching entries exist in BOM material definitions.
- Pair with detailed steps (`production_process_step`) to capture work centers and resource requirements.
- Keep `metadata` flexible for storing attachments, routing IDs, or MES integration keys.

#### Table: `production_process_step`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `company_id` | `bigint` | `NOT NULL`, FK to `invproj_company(id)` | Owning company. |
| `company_code` | `varchar(8)` | `NOT NULL`, check numeric | Cached company code. |
| `process_id` | `bigint` | `NOT NULL`, FK to `production_process(id)` | Parent production process. |
| `work_center_id` | `bigint` | `NOT NULL`, FK to `production_work_center(id)` | Selected work center for the step. |
| `work_center_code` | `varchar(20)` | `NOT NULL` | Cached work center code. |
| `machine_id` | `bigint` | nullable, FK to `production_machine(id)` | Required machine for this step (if applicable). |
| `machine_code` | `varchar(10)` | nullable | Cached machine code. |
| `sequence_order` | `smallint` | `NOT NULL` | Execution order of the step. |
| `personnel_requirements` | `jsonb` | `NOT NULL`, default `'[]'::jsonb` | List of required personnel roles/IDs for the work center. |
| `labor_minutes_per_unit` | `numeric(18,6)` | `NOT NULL` | Human labor minutes per finished unit. |
| `machine_minutes_per_unit` | `numeric(18,6)` | `NOT NULL` | Machine runtime minutes per finished unit. |
| `setup_minutes` | `numeric(18,6)` | `NOT NULL`, default `0` | Setup time per batch (optional). |
| `notes` | `text` | nullable | Additional instructions for the step. |
| `metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Extensible attributes (tooling, safety requirements). |
| `is_enabled` | `smallint` | `NOT NULL`, default `1`, check in (0,1) | Soft-delete flag. |
| `activated_at` | `timestamp with time zone` | nullable | Last enable timestamp. |
| `deactivated_at` | `timestamp with time zone` | nullable | Last disable timestamp. |
| `created_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Auto-populated on insert. |
| `edited_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Update audit. |
| `created_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Creator reference. |
| `edited_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Last editor reference. |

Additional considerations:

- Unique constraint on `(company_id, process_id, work_center_id, sequence_order)` maintains ordering and avoids duplicates.
- `personnel_requirements` can store structures like `[{ "role": "Operator", "count": 2 }, { "person_id": ... }]`; enforce format at application layer.
- Validate `work_center_id` and `machine_id` belong to the same company as the process.
- If `machine_id` is specified, validate it belongs to the selected `work_center_id`.
- Use aggregated labor/machine minutes to plan capacity and costing.
- Consider separate table for personnel assignments if explicit references per step are required instead of JSON.

#### Table: `production_product_order`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `company_id` | `bigint` | `NOT NULL`, FK to `invproj_company(id)` | Owning company. |
| `company_code` | `varchar(8)` | `NOT NULL`, check numeric | Cached company code. |
| `order_code` | `varchar(30)` | `NOT NULL`, `UNIQUE` within company | Human-readable production order identifier (auto-generated 10-digit code). |
| `order_date` | `date` | `NOT NULL`, default `now()` | Date the order is created. |
| `due_date` | `date` | nullable | Target completion date (Jalali calendar). |
| `finished_item_id` | `bigint` | `NOT NULL`, FK to `inventory_item(id)` | Item to be produced (auto-populated from BOM). |
| `finished_item_code` | `varchar(16)` | `NOT NULL` | Cached code for the produced item. |
| `bom_id` | `bigint` | `NOT NULL`, FK to `production_bom(id)` | BOM to use for material requirements (required). |
| `bom_code` | `varchar(30)` | `NOT NULL` | Cached BOM code for traceability. |
| `process_id` | `bigint` | nullable, FK to `production_process(id)` | Production process governing execution (optional). |
| `process_code` | `varchar(30)` | nullable | Cached process code for traceability. |
| `quantity_planned` | `numeric(18,6)` | `NOT NULL` | Planned quantity to produce. |
| `unit` | `varchar(30)` | `NOT NULL` | Unit of measure for the quantity (auto-populated from finished item). |
| `status` | `varchar(20)` | `NOT NULL`, default `'planned'` | Workflow state (`planned`, `released`, `in_progress`, `completed`, `cancelled`). |
| `priority` | `varchar(10)` | `NOT NULL`, default `'normal'` | Priority level (`low`, `normal`, `high`, `urgent`). |
| `approved_by_id` | `bigint` | nullable, FK to `invproj_user(id)` | User who can approve this order (filtered by APPROVE permission). |
| `customer_reference` | `varchar(60)` | nullable | Optional customer or project reference. |
| `notes` | `text` | nullable | Additional instructions or remarks. |
| `metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Extensible attributes (attachments, scheduling info). |
| `created_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Auto-populated on insert. |
| `edited_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Update audit. |
| `created_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Creator reference. |
| `edited_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Last editor reference. |
| `is_enabled` | `smallint` | `NOT NULL`, default `1`, check in (0,1) | Soft-delete flag. |
| `activated_at` | `timestamp with time zone` | nullable | Last enable timestamp. |
| `deactivated_at` | `timestamp with time zone` | nullable | Last disable timestamp. |

Additional considerations:

- Unique constraint on `(company_id, order_code)` ensures order codes are unique per company.
- Auto-generated `order_code` using sequential code generation (10 digits).
- `bom_id` is required; `process_id` is optional.
- `finished_item_id` and `finished_item_code` are auto-populated from selected BOM.
- `unit` is auto-populated from finished item's primary unit.
- `approved_by_id` filters to show only users with APPROVE permission for `production.product_orders`.
- Users with `create_transfer_from_order` permission can optionally create transfer requests directly from the order form.
- Integrate order status transitions with inventory reservations (materials) and production tracking events.

#### Table: `production_order_performance`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `company_id` | `bigint` | `NOT NULL`, FK to `invproj_company(id)` | Owning company. |
| `company_code` | `varchar(8)` | `NOT NULL`, check numeric | Cached company code. |
| `order_id` | `bigint` | `NOT NULL`, FK to `production_product_order(id)` | Production order being reported. |
| `order_code` | `varchar(30)` | `NOT NULL` | Cached production order code. |
| `finished_item_id` | `bigint` | `NOT NULL`, FK to `inventory_item(id)` | Produced item. |
| `finished_item_code` | `varchar(16)` | `NOT NULL` | Cached produced item code. |
| `report_date` | `date` | `NOT NULL` | Date of performance report (can be daily or per run). |
| `quantity_produced` | `numeric(18,6)` | `NOT NULL`, default `0` | Good units completed. |
| `quantity_received` | `numeric(18,6)` | `NOT NULL`, default `0` | Quantity transferred/received into inventory. |
| `quantity_scrapped` | `numeric(18,6)` | `NOT NULL`, default `0` | Units scrapped. |
| `unit_cycle_minutes` | `numeric(18,6)` | `NOT NULL`, default `0` | Cycle time per unit (minutes). |
| `total_run_minutes` | `numeric(18,6)` | `NOT NULL`, default `0` | Total production runtime for this report. |
| `labor_usage` | `jsonb` | `NOT NULL`, default `'[]'::jsonb` | Array of personnel usage per work center (e.g., `{work_center_id, person_id/role, minutes}`). |
| `material_scrap` | `jsonb` | `NOT NULL`, default `'[]'::jsonb` | Array of scrapped materials with quantity/unit. |
| `machine_usage_minutes` | `numeric(18,6)` | `NOT NULL`, default `0` | Aggregate machine time consumed. |
| `shift_id` | `bigint` | nullable, FK to `production_shift(id)` | Shift context if applicable. |
| `notes` | `text` | nullable | Additional remarks (issues, downtime). |
| `metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Extensible fields (downtime breakdown, quality data). |
| `created_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Auto-populated on insert. |
| `edited_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Update audit. |
| `created_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Reporter reference. |
| `edited_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Last editor reference. |
| `is_enabled` | `smallint` | `NOT NULL`, default `1`, check in (0,1) | Soft-delete flag. |

Additional considerations:

- Unique constraint on `(company_id, order_id, report_date)` if only one report per order/day is allowed; otherwise allow multiples with sequence field.
- `labor_usage` and `material_scrap` JSON structures should follow a documented schema; consider normalizing into child tables if granular reporting is required.
- `quantity_received` may differ from `quantity_produced` when goods await QC; integrate with inventory receipt processes.
- Use `total_run_minutes` and `quantity_produced` to compute actual cycle time, compare against planned values from process steps.
- Store downtime, yield, and efficiency metrics in `metadata` or companion analytics tables as needed.

**Note**: The `production_order_performance` table design above is a legacy design. The current implementation uses a normalized structure with separate tables for materials, personnel, and machines. See `production_performance_record` tables below.

#### Table: `production_performance_record`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `company_id` | `bigint` | `NOT NULL`, FK to `invproj_company(id)` | Owning company. |
| `company_code` | `varchar(8)` | `NOT NULL`, check numeric | Cached company code. |
| `performance_code` | `varchar(30)` | `NOT NULL`, `UNIQUE` within company | Auto-generated code with "PR-" prefix and 8-digit sequential number. |
| `order_id` | `bigint` | `NOT NULL`, FK to `production_product_order(id)` | Production order being reported (must have a process). |
| `order_code` | `varchar(30)` | `NOT NULL` | Cached production order code. |
| `transfer_id` | `bigint` | nullable, FK to `production_transfer_to_line(id)` | Optional transfer request reference (for auto-populating materials). |
| `report_date` | `date` | `NOT NULL`, default `now()` | Date of performance report (Jalali calendar). |
| `quantity_planned` | `numeric(18,6)` | `NOT NULL` | Planned quantity from order (auto-populated). |
| `quantity_actual` | `numeric(18,6)` | `NOT NULL` | Actual quantity produced (user-entered, cannot exceed planned). |
| `unit` | `varchar(30)` | `NOT NULL` | Unit of measure (auto-populated from order). |
| `status` | `varchar(20)` | `NOT NULL`, default `'pending_approval'` | Workflow state (`pending_approval`, `approved`, `rejected`). |
| `approved_by_id` | `bigint` | nullable, FK to `invproj_user(id)` | User who can approve this performance record (filtered by APPROVE permission). |
| `is_locked` | `smallint` | `NOT NULL`, default `0`, check in (0,1) | Lock flag (inherited from LockableModel). |
| `locked_at` | `timestamp with time zone` | nullable | Timestamp when document was locked. |
| `locked_by_id` | `bigint` | nullable, FK to `invproj_user(id)` | User who locked the document. |
| `unlocked_at` | `timestamp with time zone` | nullable | Timestamp when document was unlocked. |
| `unlocked_by_id` | `bigint` | nullable, FK to `invproj_user(id)` | User who unlocked the document. |
| `notes` | `text` | nullable | Additional remarks (issues, downtime). |
| `metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Extensible attributes (downtime breakdown, quality data). |
| `created_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Auto-populated on insert. |
| `edited_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Update audit. |
| `created_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Creator reference. |
| `edited_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Last editor reference. |
| `is_enabled` | `smallint` | `NOT NULL`, default `1`, check in (0,1) | Soft-delete flag. |

Additional considerations:

- Unique constraint on `(company_id, order_id, report_date)` ensures one performance record per order per day.
- Auto-generated `performance_code` using sequential code generation (8 digits with "PR-" prefix).
- `order_id` must reference a `ProductOrder` with a process assigned (validated in form).
- `transfer_id` is optional - if selected, materials are auto-populated from transfer document.
- `quantity_actual` cannot exceed `quantity_planned` (validated in form).
- `approved_by_id` filters to show only users with APPROVE permission for `production.performance_records`.
- Inherits from `LockableModel` - documents are locked after approval.
- Use companion detail tables (`production_performance_record_material`, `production_performance_record_person`, `production_performance_record_machine`) for granular tracking.
- Can create permanent or temporary receipts from approved performance records (requires `CREATE_RECEIPT` permission).
- Receipt type determined by `finished_item.requires_temporary_receipt`:
  - If `requires_temporary_receipt = 1`: Only temporary receipt can be created
  - If `requires_temporary_receipt = 0`: User can choose permanent or temporary receipt

#### Table: `production_performance_record_material`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `company_id` | `bigint` | `NOT NULL`, FK to `invproj_company(id)` | Owning company. |
| `company_code` | `varchar(8)` | `NOT NULL`, check numeric | Cached company code. |
| `performance_record_id` | `bigint` | `NOT NULL`, FK to `production_performance_record(id)` | Parent performance record. |
| `transfer_item_id` | `bigint` | nullable, FK to `production_transfer_to_line_item(id)` | Reference to transfer item (if material came from transfer). |
| `material_item_id` | `bigint` | `NOT NULL`, FK to `inventory_item(id)` | Material item. |
| `material_item_code` | `varchar(16)` | `NOT NULL` | Cached material item code. |
| `quantity_issued` | `numeric(18,6)` | `NOT NULL` | Quantity issued from transfer (read-only). |
| `quantity_wasted` | `numeric(18,6)` | `NOT NULL`, default `0` | Quantity wasted (user-entered). |
| `unit` | `varchar(30)` | `NOT NULL` | Unit of measure (auto-populated from item). |
| `notes` | `text` | nullable | Line-specific notes. |
| `created_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Auto-populated on insert. |
| `edited_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Update audit. |
| `created_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Creator reference. |
| `edited_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Last editor reference. |
| `is_enabled` | `smallint` | `NOT NULL`, default `1`, check in (0,1) | Soft-delete flag. |

Additional considerations:

- Unique constraint on `(company_id, performance_record_id, material_item_id)` prevents duplicate materials.
- Materials are auto-populated from transfer request items (if transfer is selected).
- `quantity_issued` is read-only (copied from transfer item).
- `quantity_wasted` can be updated by user (cannot exceed `quantity_issued`).
- Material items cannot be edited after creation (read-only).

#### Table: `production_performance_record_person`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `company_id` | `bigint` | `NOT NULL`, FK to `invproj_company(id)` | Owning company. |
| `company_code` | `varchar(8)` | `NOT NULL`, check numeric | Cached company code. |
| `performance_record_id` | `bigint` | `NOT NULL`, FK to `production_performance_record(id)` | Parent performance record. |
| `person_id` | `bigint` | `NOT NULL`, FK to `production_person(id)` | Personnel who worked on the order. |
| `person_code` | `varchar(8)` | `NOT NULL` | Cached person code. |
| `work_line_id` | `bigint` | nullable, FK to `production_work_line(id)` | Work line assignment (optional). |
| `work_line_code` | `varchar(5)` | nullable | Cached work line code. |
| `minutes_worked` | `numeric(10,2)` | `NOT NULL` | Work minutes for this person (user-entered). |
| `notes` | `text` | nullable | Line-specific notes. |
| `created_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Auto-populated on insert. |
| `edited_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Update audit. |
| `created_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Creator reference. |
| `edited_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Last editor reference. |
| `is_enabled` | `smallint` | `NOT NULL`, default `1`, check in (0,1) | Soft-delete flag. |

Additional considerations:

- Unique constraint on `(company_id, performance_record_id, person_id)` prevents duplicate personnel entries.
- Personnel filtered by process work lines (only personnel assigned to work lines in the order's process).
- `work_line_id` is optional but helps track which work line the person was assigned to.
- `minutes_worked` tracks labor time for analytics and cost calculation.

#### Table: `production_performance_record_machine`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `company_id` | `bigint` | `NOT NULL`, FK to `invproj_company(id)` | Owning company. |
| `company_code` | `varchar(8)` | `NOT NULL`, check numeric | Cached company code. |
| `performance_record_id` | `bigint` | `NOT NULL`, FK to `production_performance_record(id)` | Parent performance record. |
| `machine_id` | `bigint` | `NOT NULL`, FK to `production_machine(id)` | Machine used in the order. |
| `machine_code` | `varchar(10)` | `NOT NULL` | Cached machine code. |
| `work_line_id` | `bigint` | nullable, FK to `production_work_line(id)` | Work line assignment (optional). |
| `work_line_code` | `varchar(5)` | nullable | Cached work line code. |
| `minutes_worked` | `numeric(10,2)` | `NOT NULL` | Work minutes for this machine (user-entered). |
| `notes` | `text` | nullable | Line-specific notes. |
| `created_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Auto-populated on insert. |
| `edited_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Update audit. |
| `created_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Creator reference. |
| `edited_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Last editor reference. |
| `is_enabled` | `smallint` | `NOT NULL`, default `1`, check in (0,1) | Soft-delete flag. |

Additional considerations:

- Unique constraint on `(company_id, performance_record_id, machine_id)` prevents duplicate machine entries.
- Machines filtered by process work lines (only machines assigned to work lines in the order's process).
- `work_line_id` is optional but helps track which work line the machine was assigned to.
- `minutes_worked` tracks machine usage time for analytics and cost calculation.

#### Table: `production_transfer_to_line`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `company_id` | `bigint` | `NOT NULL`, FK to `invproj_company(id)` | Owning company. |
| `company_code` | `varchar(8)` | `NOT NULL`, check numeric | Cached company code. |
| `transfer_code` | `varchar(30)` | `NOT NULL`, `UNIQUE` within company | Human-readable transfer document identifier (auto-generated 8-digit code with "TR" prefix). |
| `order_id` | `bigint` | `NOT NULL`, FK to `production_product_order(id)` | Production order requiring materials (must have a BOM). |
| `order_code` | `varchar(30)` | `NOT NULL` | Cached production order code. |
| `transfer_date` | `date` | `NOT NULL`, default `now()` | Date of the transfer (Jalali calendar). |
| `status` | `varchar(20)` | `NOT NULL`, default `'pending_approval'` | Workflow state (`pending_approval`, `approved`, `rejected`). |
| `approved_by_id` | `bigint` | nullable, FK to `invproj_user(id)` | User who can approve this transfer request (filtered by APPROVE permission). |
| `is_locked` | `smallint` | `NOT NULL`, default `0`, check in (0,1) | Lock flag (inherited from LockableModel). |
| `locked_at` | `timestamp with time zone` | nullable | Timestamp when document was locked. |
| `locked_by_id` | `bigint` | nullable, FK to `invproj_user(id)` | User who locked the document. |
| `unlocked_at` | `timestamp with time zone` | nullable | Timestamp when document was unlocked. |
| `unlocked_by_id` | `bigint` | nullable, FK to `invproj_user(id)` | User who unlocked the document. |
| `notes` | `text` | nullable | Additional comments or instructions. |
| `metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Extensible attributes (signatures, attachments). |
| `created_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Auto-populated on insert. |
| `edited_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Update audit. |
| `created_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Creator reference. |
| `edited_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Last editor reference. |
| `is_enabled` | `smallint` | `NOT NULL`, default `1`, check in (0,1) | Soft-delete flag. |

Additional considerations:

- Unique constraint on `(company_id, transfer_code)` ensures document uniqueness.
- Auto-generated `transfer_code` using sequential code generation (8 digits with "TR" prefix).
- `order_id` must reference a `ProductOrder` with a BOM.
- `approved_by_id` filters to show only users with APPROVE permission for `production.transfer_requests`.
- Inherits from `LockableModel` - documents are locked after approval.
- Use companion detail table (`production_transfer_to_line_item`) to store line-by-line materials, quantities, and warehouse movements.
- BOM items are automatically populated when order is selected.
- Extra items (not in BOM) can be added by users (only editable before lock).
- Integrate workflow with inventory reservations/issues to maintain stock accuracy.
- Can create consumption issues from approved transfer requests (requires `CREATE_ISSUE_FROM_TRANSFER` permission).

#### Table: `production_transfer_to_line_item`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `company_id` | `bigint` | `NOT NULL`, FK to `invproj_company(id)` | Owning company. |
| `company_code` | `varchar(8)` | `NOT NULL`, check numeric | Cached company code. |
| `transfer_id` | `bigint` | `NOT NULL`, FK to `production_transfer_to_line(id)` | Parent transfer document. |
| `material_item_id` | `bigint` | `NOT NULL`, FK to `inventory_item(id)` | Material being moved. |
| `material_item_code` | `varchar(16)` | `NOT NULL` | Cached material item code. |
| `quantity_required` | `numeric(18,6)` | `NOT NULL` | Quantity needed per BOM * order quantity (for BOM items) or user-entered (for extra items). |
| `quantity_transferred` | `numeric(18,6)` | `NOT NULL`, default `0` | Actual quantity transferred. |
| `unit` | `varchar(30)` | `NOT NULL` | Unit of measure (auto-populated from BOM or item). |
| `source_warehouse_id` | `bigint` | nullable, FK to `inventory_warehouse(id)` | Warehouse issuing the material (auto-selected from ItemWarehouse for BOM items). |
| `source_warehouse_code` | `varchar(5)` | nullable | Cached source warehouse code. |
| `destination_work_center_id` | `bigint` | nullable, FK to `production_work_center(id)` | Work center receiving the material (optional). |
| `destination_location_code` | `varchar(30)` | nullable | Optional location or bin at line side. |
| `material_scrap_allowance` | `numeric(5,2)` | `NOT NULL`, default `0.00` | Scrap percentage considered for transfer (copied from BOM for BOM items). |
| `is_extra` | `smallint` | `NOT NULL`, default `0`, check in (0,1) | Flag to distinguish BOM items (0) from extra request items (1). |
| `notes` | `text` | nullable | Line-specific instructions. |
| `metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Extensible attributes (batch/lot requirements). |
| `created_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Auto-populated on insert. |
| `edited_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Update audit. |
| `created_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Creator reference. |
| `edited_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Last editor reference. |
| `is_enabled` | `smallint` | `NOT NULL`, default `1`, check in (0,1) | Soft-delete flag. |

Additional considerations:

- Unique constraint on `(company_id, transfer_id, material_item_id, is_extra)` to prevent duplicate lines (allows same item as BOM and extra).
- For BOM items (`is_extra=0`):
  - `quantity_required` = `order.quantity_planned × bom_material.quantity_per_unit`
  - `source_warehouse_id` auto-selected from ItemWarehouse (first allowed warehouse)
  - `material_scrap_allowance` copied from BOM material
  - Not editable after document creation (read-only)
- For extra items (`is_extra=1`):
  - `quantity_required` user-entered
  - `source_warehouse_id` user-selected
  - `material_scrap_allowance` user-entered
  - Editable before document is locked
- `destination_work_center_id` is optional (nullable).
- Validate warehouse IDs and work centers belong to the same company; enforce permitted source-destination mappings.
- Extend with lot/serial tracking if materials require traceability.
- Integrate with inventory issue transactions to update stock levels upon transfer execution.
- Cascading filters (Material Type → Category → Subcategory → Item) for extra item selection.

### Shared Considerations

- Reuse existing shared entities (`invproj_company`, `invproj_person`, `invproj_user`, `invproj_company_unit`) for tenancy, personnel, and unit references.
- Align enumerations (statuses, priorities) across modules to simplify reporting.
- Plan for potential cross-module synchronization events (e.g., inventory reservations triggered by production work orders) via service-layer contracts instead of direct foreign keys when possible.
- Ensure migrations maintain forward compatibility with eventual database splits by avoiding module-specific schema changes in shared tables without coordination.

## Open Questions

- Finalize the list of production processes to support in the initial release (discrete manufacturing vs. process manufacturing specifics).
- Confirm integration points with inventory (material issuance, finished goods receipt) and QC (in-process checks, final inspection).
- Determine reporting and analytics requirements to size indexing and historical data retention strategies.
