## Overview

We are designing `invproj`, a modular warehouse, production, and quality control platform built with Python and Django. The application targets PostgreSQL as the primary database engine and must operate on both Linux/Nginx and Windows Server/IIS deployments. Django serves server-side UI and API endpoints today, while the architecture leaves room for future SPA or mobile clients. All modules initially share a single physical database, yet consistent naming conventions (`inventory_`, `production_`, `qc_`, `ticketing_`, shared `invproj_`) make it straightforward to migrate each module into its own database or service as the platform scales. Shared/global entities—companies, personnel, users, company units—reside in the `invproj_` namespace and provide consistent tenancy, security, and configuration anchors across the system.

This document presents the ticketing module database design for the `invproj` platform. The ticketing module provides a comprehensive ticket management system with dynamic form builder capabilities. Users with appropriate permissions can create ticket templates (structures) with custom fields (text inputs, dropdowns, radio buttons, file uploads, references to other entities, etc.), define access controls for template/category creation, response, and closure permissions, and manage the complete ticket lifecycle. Tables defined here use the `ticketing_` prefix and reference shared entities to preserve modularity while enabling comprehensive tracking, assignment, and resolution workflows. The schema description is self-contained so it can be read independently, yet it aligns with the overall architecture and the companion inventory, production, and QC design plans.

Key design principles:

- **Multi-company tenancy**: Every ticketing table stores `company_id` and cached `company_code`, referencing `invproj_company`, to isolate tenant data and prepare for future sharding.
- **Consistent auditing**: Tables include `is_enabled`, activation timestamps, creation/update metadata, and optional `metadata` (`jsonb`) for extensibility. Booleans use `smallint` (0/1) for performance and cross-database portability.
- **Dynamic form builder**: Users can create ticket templates with custom field definitions (text, dropdown, radio, file upload, entity references, etc.) arranged in rows.
- **Permission-based access control**: Access permissions (create, respond, close) can be defined at both template and category/subcategory levels for users and groups.
- **Workflow & status tracking**: Tickets follow a defined lifecycle with status transitions, priority management, assignment, and resolution tracking.
- **Flexible JSON usage**: Semi-structured attributes (custom fields, attachments, related entities) leverage PostgreSQL `jsonb` with indexing strategies tuned per table.
- **Modular boundaries**: Ticketing tables reference shared entities or module-specific tables only through well-defined foreign keys, enabling eventual database separation without schema rewrites.

## Database Design Plan

- Define ticketing-specific tables (`ticketing_`) for:
  - Categories and subcategories with hierarchical support
  - Category-level permissions (create, respond, close) for users/groups
  - Ticket templates with dynamic field definitions
  - Template field options (for dropdown/radio fields)
  - Template-level permissions (create, respond, close) for users/groups
  - Tickets with field values
  - Priorities (can be set at both template and ticket levels)
  - Comments, attachments, and related entities
- Document relationships to shared (`invproj_`) entities and cross-module references needed for traceability.
- Capture naming conventions, constraints, and JSON usage for each table.
- Track open questions and assumptions that require validation with operations and support teams.

### Ticketing Module

#### Table: `ticketing_category`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `company_id` | `bigint` | `NOT NULL`, FK to `invproj_company(id)` | Owning company. |
| `company_code` | `varchar(3)` | `NOT NULL`, check numeric | Cached company code for reporting. |
| `public_code` | `varchar(10)` | `NOT NULL`, `UNIQUE` within company | User-defined category code. |
| `name` | `varchar(120)` | `NOT NULL`, `UNIQUE` within company | Category display name. |
| `name_en` | `varchar(120)` | nullable | Optional English display name. |
| `description` | `text` | nullable | Category description. |
| `parent_category_id` | `bigint` | nullable, FK to `ticketing_category(id)` | Parent category for hierarchical categories. |
| `is_enabled` | `smallint` | `NOT NULL`, default `1`, check in (0,1) | Active flag. |
| `sort_order` | `smallint` | `NOT NULL`, default `0` | Ordering in UI/reports. |
| `activated_at` | `timestamp with time zone` | nullable | Last enable timestamp. |
| `deactivated_at` | `timestamp with time zone` | nullable | Last disable timestamp. |
| `created_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Auto-populated on insert. |
| `edited_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Update audit. |
| `created_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Creator reference. |
| `edited_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Last editor reference. |
| `metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Extensible fields (color, icon, SLA settings). |

Additional considerations:

- Support hierarchical categories via `parent_category_id` self-reference.
- Add unique constraint on `(company_id, public_code)`.
- Index on `(company_id, is_enabled, sort_order)` for efficient filtering.
- Categories can be parent categories (subcategories) or child categories (actual categories).

---

#### Table: `ticketing_category_permission`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `company_id` | `bigint` | `NOT NULL`, FK to `invproj_company(id)` | Owning company. |
| `company_code` | `varchar(3)` | `NOT NULL`, check numeric | Cached company code. |
| `category_id` | `bigint` | `NOT NULL`, FK to `ticketing_category(id)` | Category or subcategory. |
| `category_code` | `varchar(10)` | `NOT NULL` | Cached category code. |
| `user_id` | `bigint` | nullable, FK to `invproj_user(id)` | User with permission (mutually exclusive with group_id). |
| `group_id` | `bigint` | nullable, FK to `auth_group(id)` | Group with permission (mutually exclusive with user_id). |
| `can_create` | `smallint` | `NOT NULL`, default `0`, check in (0,1) | Permission to create tickets in this category. |
| `can_respond` | `smallint` | `NOT NULL`, default `0`, check in (0,1) | Permission to respond to tickets in this category. |
| `can_close` | `smallint` | `NOT NULL`, default `0`, check in (0,1) | Permission to close tickets in this category. |
| `is_enabled` | `smallint` | `NOT NULL`, default `1`, check in (0,1) | Active flag. |
| `created_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Auto-populated on insert. |
| `edited_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Update audit. |
| `created_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Creator reference. |
| `edited_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Last editor reference. |
| `metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Extensible fields. |

Additional considerations:

- Ensure either `user_id` or `group_id` is set (not both, not neither).
- Add unique constraint on `(category_id, user_id)` and `(category_id, group_id)` to prevent duplicates.
- Index on `(category_id, can_create)`, `(category_id, can_respond)`, `(category_id, can_close)` for permission queries.
- Index on `(user_id, can_create)`, `(user_id, can_respond)`, `(user_id, can_close)` for user permission lookups.
- Index on `(group_id, can_create)`, `(group_id, can_respond)`, `(group_id, can_close)` for group permission lookups.

---

#### Table: `ticketing_priority`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `company_id` | `bigint` | `NOT NULL`, FK to `invproj_company(id)` | Owning company. |
| `company_code` | `varchar(3)` | `NOT NULL`, check numeric | Cached company code. |
| `public_code` | `varchar(10)` | `NOT NULL`, `UNIQUE` within company | User-defined priority code. |
| `name` | `varchar(120)` | `NOT NULL`, `UNIQUE` within company | Priority display name (e.g., "Low", "Medium", "High", "Critical"). |
| `name_en` | `varchar(120)` | nullable | Optional English display name. |
| `priority_level` | `smallint` | `NOT NULL`, default `3` | Numeric level (1=highest, 5=lowest) for sorting. |
| `color` | `varchar(7)` | nullable | Hex color code for UI display (e.g., "#ff0000"). |
| `sla_hours` | `integer` | nullable | Service Level Agreement hours for response time. |
| `is_enabled` | `smallint` | `NOT NULL`, default `1`, check in (0,1) | Active flag. |
| `sort_order` | `smallint` | `NOT NULL`, default `0` | Ordering in UI/reports. |
| `activated_at` | `timestamp with time zone` | nullable | Last enable timestamp. |
| `deactivated_at` | `timestamp with time zone` | nullable | Last disable timestamp. |
| `created_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Auto-populated on insert. |
| `edited_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Update audit. |
| `created_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Creator reference. |
| `edited_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Last editor reference. |
| `metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Extensible fields. |

Additional considerations:

- Ensure `priority_level` is unique within company for consistent ordering.
- Index on `(company_id, priority_level)` for efficient sorting.

---

#### Table: `ticketing_template`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `company_id` | `bigint` | `NOT NULL`, FK to `invproj_company(id)` | Owning company. |
| `company_code` | `varchar(3)` | `NOT NULL`, check numeric | Cached company code. |
| `template_code` | `varchar(30)` | `NOT NULL`, `UNIQUE` within company | Auto-generated template identifier (format: TMP-YYYYMMDD-XXXXXX). |
| `name` | `varchar(255)` | `NOT NULL` | Template name. |
| `description` | `text` | nullable | Template description. |
| `category_id` | `bigint` | nullable, FK to `ticketing_category(id)` | Associated category/subcategory. |
| `category_code` | `varchar(10)` | nullable | Cached category code. |
| `default_priority_id` | `bigint` | nullable, FK to `ticketing_priority(id)` | Default priority for tickets created from this template. |
| `default_priority_code` | `varchar(10)` | nullable | Cached default priority code. |
| `is_enabled` | `smallint` | `NOT NULL`, default `1`, check in (0,1) | Active flag. |
| `sort_order` | `smallint` | `NOT NULL`, default `0` | Ordering in UI/reports. |
| `activated_at` | `timestamp with time zone` | nullable | Last enable timestamp. |
| `deactivated_at` | `timestamp with time zone` | nullable | Last disable timestamp. |
| `created_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Auto-populated on insert. |
| `edited_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Update audit. |
| `created_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Creator reference. |
| `edited_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Last editor reference. |
| `metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Extensible fields. |

Additional considerations:

- Auto-generate `template_code` using sequential code generation (format: TMP-YYYYMMDD-XXXXXX).
- Add unique constraint on `(company_id, template_code)`.
- Index on `(company_id, category_id, is_enabled, sort_order)` for template filtering.

---

#### Table: `ticketing_template_field`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `company_id` | `bigint` | `NOT NULL`, FK to `invproj_company(id)` | Owning company. |
| `company_code` | `varchar(3)` | `NOT NULL`, check numeric | Cached company code. |
| `template_id` | `bigint` | `NOT NULL`, FK to `ticketing_template(id)` | Parent template. |
| `template_code` | `varchar(30)` | `NOT NULL` | Cached template code. |
| `field_name` | `varchar(255)` | `NOT NULL` | Field label/name for display. |
| `field_type` | `varchar(30)` | `NOT NULL` | Field type: `short_text`, `long_text`, `radio`, `dropdown`, `file_upload`, `reference`, `checkbox`, `date`, `time`, `datetime`, `number`, `email`, `url`, `phone`, `multi_select`, `tags`, `rich_text`, `color`, `rating`, `slider`, `currency`, `signature`, `location`, `section`, `calculation`, etc. |
| `field_key` | `varchar(100)` | `NOT NULL` | Unique identifier for the field within template (e.g., "item_code", "description"). |
| `is_required` | `smallint` | `NOT NULL`, default `0`, check in (0,1) | Whether field is required (mandatory). |
| `default_value` | `text` | nullable | Default value for the field (optional). |
| `field_order` | `smallint` | `NOT NULL`, default `0` | Display order (row position) in the form. |
| `help_text` | `text` | nullable | Help text/description for the field. |
| `validation_rules` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Validation rules (min/max length, regex patterns, etc.). |
| `field_config` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Field-specific configuration (e.g., for reference fields: entity types, for file upload: allowed types, max size). |
| `is_enabled` | `smallint` | `NOT NULL`, default `1`, check in (0,1) | Active flag. |
| `created_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Auto-populated on insert. |
| `edited_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Update audit. |
| `created_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Creator reference. |
| `edited_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Last editor reference. |
| `metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Extensible fields. |

Additional considerations:

- Add unique constraint on `(template_id, field_key)` to ensure unique field keys per template.
- Index on `(template_id, field_order)` for ordered field retrieval.
- For `reference` field type, `field_config` should store allowed entity types (e.g., `["inventory.item", "production.order"]`).
- For `file_upload` field type, `field_config` should store allowed file types and max size.
- Support field ordering via `field_order` to allow users to arrange fields in rows.

---

#### Table: `ticketing_template_field_option`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `company_id` | `bigint` | `NOT NULL`, FK to `invproj_company(id)` | Owning company. |
| `company_code` | `varchar(3)` | `NOT NULL`, check numeric | Cached company code. |
| `template_field_id` | `bigint` | `NOT NULL`, FK to `ticketing_template_field(id)` | Parent field (for radio/dropdown types). |
| `template_id` | `bigint` | `NOT NULL`, FK to `ticketing_template(id)` | Cached template reference. |
| `option_value` | `varchar(255)` | `NOT NULL` | Option value (stored value). |
| `option_label` | `varchar(255)` | `NOT NULL` | Option label (displayed text). |
| `option_order` | `smallint` | `NOT NULL`, default `0` | Display order in dropdown/radio list. |
| `is_default` | `smallint` | `NOT NULL`, default `0`, check in (0,1) | Whether this option is the default selection. |
| `is_enabled` | `smallint` | `NOT NULL`, default `1`, check in (0,1) | Active flag. |
| `created_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Auto-populated on insert. |
| `edited_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Update audit. |
| `created_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Creator reference. |
| `edited_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Last editor reference. |
| `metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Extensible fields. |

Additional considerations:

- Only applicable for `field_type` = `radio`, `dropdown`, or `multi_select`.
- For `multi_select`, multiple options can be selected and stored as array in ticket field values.
- Add unique constraint on `(template_field_id, option_value)` to prevent duplicate values.
- Index on `(template_field_id, option_order)` for ordered option retrieval.
- Only one option per field should have `is_default = 1` (enforce via application logic or trigger).

---

#### Table: `ticketing_template_permission`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `company_id` | `bigint` | `NOT NULL`, FK to `invproj_company(id)` | Owning company. |
| `company_code` | `varchar(3)` | `NOT NULL`, check numeric | Cached company code. |
| `template_id` | `bigint` | `NOT NULL`, FK to `ticketing_template(id)` | Template. |
| `template_code` | `varchar(30)` | `NOT NULL` | Cached template code. |
| `user_id` | `bigint` | nullable, FK to `invproj_user(id)` | User with permission (mutually exclusive with group_id). |
| `group_id` | `bigint` | nullable, FK to `auth_group(id)` | Group with permission (mutually exclusive with user_id). |
| `can_create` | `smallint` | `NOT NULL`, default `0`, check in (0,1) | Permission to create tickets using this template. |
| `can_respond` | `smallint` | `NOT NULL`, default `0`, check in (0,1) | Permission to respond to tickets created from this template. |
| `can_close` | `smallint` | `NOT NULL`, default `0`, check in (0,1) | Permission to close tickets created from this template. |
| `is_enabled` | `smallint` | `NOT NULL`, default `1`, check in (0,1) | Active flag. |
| `created_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Auto-populated on insert. |
| `edited_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Update audit. |
| `created_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Creator reference. |
| `edited_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Last editor reference. |
| `metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Extensible fields. |

Additional considerations:

- Ensure either `user_id` or `group_id` is set (not both, not neither).
- Add unique constraint on `(template_id, user_id)` and `(template_id, group_id)` to prevent duplicates.
- Index on `(template_id, can_create)`, `(template_id, can_respond)`, `(template_id, can_close)` for permission queries.
- Index on `(user_id, can_create)`, `(user_id, can_respond)`, `(user_id, can_close)` for user permission lookups.
- Index on `(group_id, can_create)`, `(group_id, can_respond)`, `(group_id, can_close)` for group permission lookups.

---

#### Table: `ticketing_ticket`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `company_id` | `bigint` | `NOT NULL`, FK to `invproj_company(id)` | Owning company. |
| `company_code` | `varchar(3)` | `NOT NULL`, check numeric | Cached company code for reporting. |
| `ticket_code` | `varchar(30)` | `NOT NULL`, `UNIQUE` within company | Auto-generated ticket identifier (format: TKT-YYYYMMDD-XXXXXX). |
| `template_id` | `bigint` | `NOT NULL`, FK to `ticketing_template(id)` | Template used to create this ticket. |
| `template_code` | `varchar(30)` | `NOT NULL` | Cached template code. |
| `title` | `varchar(255)` | `NOT NULL` | Ticket title/subject. |
| `description` | `text` | nullable | Detailed ticket description (may come from template fields). |
| `category_id` | `bigint` | nullable, FK to `ticketing_category(id)` | Ticket category/subcategory. |
| `category_code` | `varchar(10)` | nullable | Cached category code. |
| `priority_id` | `bigint` | nullable, FK to `ticketing_priority(id)` | Ticket priority (user-selected or from template default). |
| `priority_code` | `varchar(10)` | nullable | Cached priority code. |
| `status` | `varchar(20)` | `NOT NULL`, default `'open'` | Ticket status (`open`, `in_progress`, `assigned`, `pending`, `resolved`, `closed`, `cancelled`). |
| `reported_by_id` | `bigint` | `NOT NULL`, FK to `invproj_user(id)` | User who reported/created the ticket. |
| `reported_by_username` | `varchar(150)` | `NOT NULL` | Cached reporter username. |
| `assigned_to_id` | `bigint` | nullable, FK to `invproj_user(id)` | User assigned to handle the ticket. |
| `assigned_to_username` | `varchar(150)` | nullable | Cached assignee username. |
| `assigned_at` | `timestamp with time zone` | nullable | When the ticket was assigned. |
| `opened_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | When the ticket was opened. |
| `first_response_at` | `timestamp with time zone` | nullable | When the first response was provided. |
| `resolved_at` | `timestamp with time zone` | nullable | When the ticket was resolved. |
| `resolved_by_id` | `bigint` | nullable, FK to `invproj_user(id)` | User who resolved the ticket. |
| `closed_at` | `timestamp with time zone` | nullable | When the ticket was closed. |
| `closed_by_id` | `bigint` | nullable, FK to `invproj_user(id)` | User who closed the ticket. |
| `resolution_notes` | `text` | nullable | Resolution description/summary. |
| `related_entity_type` | `varchar(50)` | nullable | Type of related entity (e.g., 'inventory.item', 'production.order', 'qc.inspection'). |
| `related_entity_id` | `bigint` | nullable | ID of related entity (polymorphic reference). |
| `related_entity_code` | `varchar(100)` | nullable | Cached related entity code. |
| `attachments` | `jsonb` | `NOT NULL`, default `'[]'::jsonb` | Array of file attachments with metadata. |
| `metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Extensible fields (custom fields, tags, internal notes). |
| `is_enabled` | `smallint` | `NOT NULL`, default `1`, check in (0,1) | Soft-delete flag. |
| `is_locked` | `smallint` | `NOT NULL`, default `0`, check in (0,1) | Lock flag to prevent modifications when resolved/closed. |
| `activated_at` | `timestamp with time zone` | nullable | Last enable timestamp. |
| `deactivated_at` | `timestamp with time zone` | nullable | Last disable timestamp. |
| `created_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Auto-populated on insert. |
| `edited_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Update audit. |
| `created_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Creator reference. |
| `edited_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Last editor reference. |

Additional considerations:

- Auto-generate `ticket_code` using sequential code generation (format: TKT-YYYYMMDD-XXXXXX).
- Add indexes on:
  - `(company_id, status, created_at)` for dashboard queries.
  - `(company_id, assigned_to_id, status)` for user assignment queries.
  - `(company_id, category_id, status)` for category filtering.
  - `(related_entity_type, related_entity_id)` for entity linking.
- Track SLA compliance via `first_response_at` and priority `sla_hours`.
- Support status transitions via workflow validation.
- Use `is_locked` to prevent edits after resolution/closure.
- Every ticket must be created from a template (`template_id` is required).

---

#### Table: `ticketing_ticket_field_value`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `company_id` | `bigint` | `NOT NULL`, FK to `invproj_company(id)` | Owning company. |
| `company_code` | `varchar(3)` | `NOT NULL`, check numeric | Cached company code. |
| `ticket_id` | `bigint` | `NOT NULL`, FK to `ticketing_ticket(id)` | Parent ticket. |
| `ticket_code` | `varchar(30)` | `NOT NULL` | Cached ticket code. |
| `template_field_id` | `bigint` | `NOT NULL`, FK to `ticketing_template_field(id)` | Template field definition. |
| `template_field_key` | `varchar(100)` | `NOT NULL` | Cached field key for quick lookup. |
| `field_value` | `text` | nullable | Field value (text representation, JSON for complex types). |
| `field_value_json` | `jsonb` | nullable | Structured field value (for reference fields, file uploads, etc.). |
| `created_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Auto-populated on insert. |
| `edited_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Update audit. |
| `created_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Creator reference. |
| `edited_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Last editor reference. |
| `metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Extensible fields. |

Additional considerations:

- Store one record per ticket field.
- Add unique constraint on `(ticket_id, template_field_id)` to ensure one value per field per ticket.
- Index on `(ticket_id)` for efficient ticket field value retrieval.
- Index on `(template_field_id)` for field value queries across tickets.
- For `short_text`/`long_text` fields: store in `field_value`.
- For `radio`/`dropdown` fields: store selected option value in `field_value`.
- For `multi_select` fields: store array of selected option values in `field_value_json`.
- For `file_upload`/`signature` fields: store file attachment IDs or paths in `field_value_json`.
- For `reference` fields: store entity type, ID, and code in `field_value_json` (e.g., `{"entity_type": "inventory.item", "entity_id": 123, "entity_code": "001002003010001"}`).
- For `checkbox` fields: store boolean value in `field_value` ("1" or "0").
- For `date` fields: store ISO date string (YYYY-MM-DD) in `field_value`.
- For `time` fields: store time string (HH:MM or HH:MM:SS) in `field_value`.
- For `datetime` fields: store ISO datetime string (YYYY-MM-DDTHH:MM:SS) in `field_value`.
- For `number`/`rating`/`slider` fields: store numeric value as string in `field_value`.
- For `email`/`url`/`phone` fields: store validated string in `field_value`.
- For `tags` fields: store array of tag strings in `field_value_json`.
- For `currency` fields: store amount and currency code in `field_value_json`.
- For `location` fields: store latitude, longitude, and optional address in `field_value_json`.
- For `rich_text` fields: store HTML content in `field_value`.
- For `color` fields: store hex color code in `field_value`.
- For `calculation` fields: store calculated result as string in `field_value`.
- For `section` fields: `field_value` is NULL (display-only, no input).

---

#### Table: `ticketing_comment`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `company_id` | `bigint` | `NOT NULL`, FK to `invproj_company(id)` | Owning company. |
| `company_code` | `varchar(3)` | `NOT NULL`, check numeric | Cached company code. |
| `ticket_id` | `bigint` | `NOT NULL`, FK to `ticketing_ticket(id)` | Parent ticket. |
| `ticket_code` | `varchar(30)` | `NOT NULL` | Cached ticket code. |
| `comment_text` | `text` | `NOT NULL` | Comment content. |
| `comment_type` | `varchar(20)` | `NOT NULL`, default `'comment'` | Comment type (`comment`, `internal_note`, `status_change`, `assignment`). |
| `author_id` | `bigint` | `NOT NULL`, FK to `invproj_user(id)` | Comment author. |
| `author_username` | `varchar(150)` | `NOT NULL` | Cached author username. |
| `is_internal` | `smallint` | `NOT NULL`, default `0`, check in (0,1) | Internal note flag (visible only to staff). |
| `attachments` | `jsonb` | `NOT NULL`, default `'[]'::jsonb` | Array of file attachments with metadata. |
| `created_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Auto-populated on insert. |
| `edited_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Update audit. |
| `edited_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Last editor reference. |
| `is_enabled` | `smallint` | `NOT NULL`, default `1`, check in (0,1) | Soft-delete flag. |
| `metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Extensible fields. |

Additional considerations:

- Add index on `(ticket_id, created_at)` for efficient ticket comment retrieval.
- Support comment editing with `edited_at` and `edited_by_id` tracking.
- Filter internal notes based on user permissions.

---

#### Table: `ticketing_attachment`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `company_id` | `bigint` | `NOT NULL`, FK to `invproj_company(id)` | Owning company. |
| `company_code` | `varchar(3)` | `NOT NULL`, check numeric | Cached company code. |
| `ticket_id` | `bigint` | nullable, FK to `ticketing_ticket(id)` | Parent ticket (if attached to ticket). |
| `comment_id` | `bigint` | nullable, FK to `ticketing_comment(id)` | Parent comment (if attached to comment). |
| `file_name` | `varchar(255)` | `NOT NULL` | Original file name. |
| `file_path` | `varchar(500)` | `NOT NULL` | Storage path relative to media root. |
| `file_size` | `bigint` | `NOT NULL` | File size in bytes. |
| `mime_type` | `varchar(100)` | nullable | MIME type (e.g., 'image/jpeg', 'application/pdf'). |
| `uploaded_by_id` | `bigint` | `NOT NULL`, FK to `invproj_user(id)` | User who uploaded the file. |
| `uploaded_by_username` | `varchar(150)` | `NOT NULL` | Cached uploader username. |
| `uploaded_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Upload timestamp. |
| `is_enabled` | `smallint` | `NOT NULL`, default `1`, check in (0,1) | Soft-delete flag. |
| `metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Extensible fields (thumbnail path, dimensions, etc.). |

Additional considerations:

- Ensure either `ticket_id` or `comment_id` is set (mutually exclusive).
- Add index on `(ticket_id)` and `(comment_id)` for efficient attachment retrieval.
- Store files in organized directory structure (e.g., `ticketing/<company_id>/<ticket_id>/<filename>`).
- Implement file cleanup when ticket/comment is soft-deleted.

---

## Relationships Summary

- `ticketing_category` → `ticketing_category` (self-reference for hierarchy/subcategories)
- `ticketing_category_permission` → `ticketing_category` (permission assignment)
- `ticketing_category_permission` → `invproj_user` (user permission)
- `ticketing_category_permission` → `auth_group` (group permission)
- `ticketing_template` → `ticketing_category` (category association)
- `ticketing_template` → `ticketing_priority` (default priority)
- `ticketing_template_field` → `ticketing_template` (field definition)
- `ticketing_template_field_option` → `ticketing_template_field` (option for radio/dropdown)
- `ticketing_template_permission` → `ticketing_template` (permission assignment)
- `ticketing_template_permission` → `invproj_user` (user permission)
- `ticketing_template_permission` → `auth_group` (group permission)
- `ticketing_ticket` → `ticketing_template` (template used for creation)
- `ticketing_ticket` → `ticketing_category` (category/subcategory assignment)
- `ticketing_ticket` → `ticketing_priority` (priority assignment)
- `ticketing_ticket` → `invproj_user` (reported_by, assigned_to, resolved_by, closed_by)
- `ticketing_ticket_field_value` → `ticketing_ticket` (ticket field values)
- `ticketing_ticket_field_value` → `ticketing_template_field` (field definition reference)
- `ticketing_comment` → `ticketing_ticket` (parent ticket)
- `ticketing_comment` → `invproj_user` (author)
- `ticketing_attachment` → `ticketing_ticket` (optional parent ticket)
- `ticketing_attachment` → `ticketing_comment` (optional parent comment)
- `ticketing_attachment` → `invproj_user` (uploader)

## Index Strategy

### Master Data Tables

- **Category lookups**: Index on `(company_id, is_enabled, sort_order)` for category/subcategory filtering.
- **Priority lookups**: Index on `(company_id, priority_level)` for priority sorting.
- **Template lookups**: Index on `(company_id, category_id, is_enabled, sort_order)` for template filtering by category.

### Permission Tables

- **Category permissions**: 
  - Index on `(category_id, can_create)`, `(category_id, can_respond)`, `(category_id, can_close)` for permission queries.
  - Index on `(user_id, can_create)`, `(user_id, can_respond)`, `(user_id, can_close)` for user permission lookups.
  - Index on `(group_id, can_create)`, `(group_id, can_respond)`, `(group_id, can_close)` for group permission lookups.
- **Template permissions**: Same indexing strategy as category permissions.

### Template & Field Tables

- **Template fields**: Index on `(template_id, field_order)` for ordered field retrieval.
- **Field options**: Index on `(template_field_id, option_order)` for ordered option retrieval.

### Ticket Tables

- **Ticket filtering**: Composite indexes on:
  - `(company_id, status, created_at)` for dashboard queries.
  - `(company_id, assigned_to_id, status)` for user assignment queries.
  - `(company_id, category_id, status)` for category filtering.
  - `(company_id, template_id, status)` for template-based filtering.
  - `(company_id, priority_id, status)` for priority filtering.
- **Ticket search**: Full-text search index on `(title, description)` or use PostgreSQL full-text search.
- **Ticket field values**: Index on `(ticket_id)` for efficient ticket field value retrieval.

### Comment & Attachment Tables

- **Comment retrieval**: Index on `(ticket_id, created_at)` for chronological comment display.
- **Attachment retrieval**: Index on `(ticket_id)` and `(comment_id)` for efficient attachment retrieval.

### Cross-Module References

- **Entity linking**: Index on `(related_entity_type, related_entity_id)` for cross-module ticket relationships.

## Field Type Reference

This section documents the supported field types and how they are stored in `ticketing_ticket_field_value`:

### Field Types

1. **`short_text`**: Single-line text input
   - Stored in: `field_value` (text)
   - Example: `"Sample text"`

2. **`long_text`**: Multi-line textarea
   - Stored in: `field_value` (text)
   - Example: `"Long description\nwith multiple lines"`

3. **`radio`**: Radio button group (single selection)
   - Stored in: `field_value` (selected option value)
   - Options defined in: `ticketing_template_field_option`
   - Example: `"option_value_1"`

4. **`dropdown`**: Dropdown select (single selection)
   - Stored in: `field_value` (selected option value)
   - Options defined in: `ticketing_template_field_option`
   - Example: `"option_value_2"`

5. **`checkbox`**: Checkbox (boolean)
   - Stored in: `field_value` ("1" for checked, "0" for unchecked)
   - Example: `"1"`

6. **`number`**: Numeric input
   - Stored in: `field_value` (numeric string)
   - Example: `"123.45"`

7. **`date`**: Date picker
   - Stored in: `field_value` (ISO date string: YYYY-MM-DD)
   - Example: `"2025-01-15"`

8. **`file_upload`**: File upload field
   - Stored in: `field_value_json` (JSON with file metadata)
   - Example: `{"file_id": 123, "file_name": "document.pdf", "file_path": "ticketing/1/123/document.pdf"}`
   - File stored via `ticketing_attachment` table

9. **`reference`**: Reference to other entities (inventory items, orders, etc.)
   - Stored in: `field_value_json` (JSON with entity info)
   - Example: `{"entity_type": "inventory.item", "entity_id": 456, "entity_code": "001002003010001", "entity_name": "Sample Item", "entity_url": "/inventory/items/456/edit/"}`
   - Allowed entity types configured in `field_config` JSON
   - **For implementation details, see [Entity Reference System Documentation](ENTITY_REFERENCE_SYSTEM.md) (pending requirements)**

10. **`time`**: Time picker (hours and minutes)
    - Stored in: `field_value` (time string: HH:MM or HH:MM:SS)
    - Example: `"14:30"` or `"14:30:00"`

11. **`datetime`**: Date and time picker (combined)
    - Stored in: `field_value` (ISO datetime string: YYYY-MM-DDTHH:MM:SS)
    - Example: `"2025-01-15T14:30:00"`

12. **`email`**: Email address input (with email format validation)
    - Stored in: `field_value` (email address string)
    - Example: `"user@example.com"`

13. **`url`**: URL/Web link input (with URL format validation)
    - Stored in: `field_value` (URL string)
    - Example: `"https://www.example.com/page"`

14. **`phone`**: Phone number input (with phone format validation)
    - Stored in: `field_value` (phone number string)
    - Example: `"+98-21-12345678"` or `"09123456789"`

15. **`multi_select`**: Multiple selection (checkbox group)
    - Stored in: `field_value_json` (array of selected option values)
    - Options defined in: `ticketing_template_field_option`
    - Example: `["option_value_1", "option_value_3", "option_value_5"]`

16. **`tags`**: Tags input (multiple tags, user can add custom tags)
    - Stored in: `field_value_json` (array of tag strings)
    - Example: `["urgent", "bug", "frontend", "user-report"]`

17. **`rich_text`**: Rich text editor (WYSIWYG HTML editor)
    - Stored in: `field_value` (HTML content)
    - Example: `"<p>This is <strong>bold</strong> text with <em>formatting</em>.</p>"`

18. **`color`**: Color picker
    - Stored in: `field_value` (hex color code)
    - Example: `"#ff0000"` or `"#3b82f6"`

19. **`rating`**: Rating/Star rating (1-5 stars or 1-10 scale)
    - Stored in: `field_value` (numeric string representing rating)
    - Config in: `field_config` (max_rating: 5 or 10)
    - Example: `"4"` (for 4 out of 5 stars)

20. **`slider`**: Number slider/range input
    - Stored in: `field_value` (numeric string)
    - Config in: `field_config` (min, max, step values)
    - Example: `"75"` (value between min and max)

21. **`currency`**: Currency/money amount input
    - Stored in: `field_value_json` (JSON with amount and currency code)
    - Example: `{"amount": "1500000.00", "currency": "IRR"}` or `{"amount": "100.50", "currency": "USD"}`

22. **`signature`**: Digital signature field
    - Stored in: `field_value_json` (JSON with signature image data or file reference)
    - Example: `{"file_id": 456, "file_path": "ticketing/1/123/signature.png", "signed_at": "2025-01-15T10:30:00"}`
    - Signature stored as image file via `ticketing_attachment` table

23. **`location`**: Geographic location/GPS coordinates
    - Stored in: `field_value_json` (JSON with latitude, longitude, and optional address)
    - Example: `{"lat": "35.6892", "lng": "51.3890", "address": "Tehran, Iran"}`

24. **`section`**: Section divider/header (display-only, no input)
    - Stored in: `field_value` is NULL (section has no value, used for form organization)
    - Used for visual separation and grouping of fields
    - Can have label and help text for display purposes

25. **`calculation`**: Calculated field (auto-calculated based on formula)
    - Stored in: `field_value` (calculated result as string)
    - Config in: `field_config` (formula expression referencing other fields)
    - Example: `"1500"` (result of formula calculation)
    - Formula can reference other field values by their `field_key`

### Field Configuration Examples

**Reference Field Config:**
```json
{
  "allowed_entity_types": ["inventory.item", "production.order"],
  "allow_multiple": false
}
```

**File Upload Field Config:**
```json
{
  "allowed_file_types": ["image/jpeg", "image/png", "application/pdf"],
  "max_file_size": 10485760,
  "max_files": 5
}
```

**Validation Rules Example:**
```json
{
  "min_length": 5,
  "max_length": 100,
  "pattern": "^[A-Za-z0-9]+$"
}
```

**Time Field Config:**
```json
{
  "format": "HH:MM",
  "time_24h": true
}
```

**DateTime Field Config:**
```json
{
  "format": "YYYY-MM-DDTHH:MM:SS",
  "timezone": "Asia/Tehran"
}
```

**Rating Field Config:**
```json
{
  "max_rating": 5,
  "show_labels": true,
  "labels": ["Poor", "Fair", "Good", "Very Good", "Excellent"]
}
```

**Slider Field Config:**
```json
{
  "min": 0,
  "max": 100,
  "step": 1,
  "show_ticks": true
}
```

**Currency Field Config:**
```json
{
  "currency": "IRR",
  "default_currency": "IRR",
  "show_currency_selector": false,
  "decimal_places": 2
}
```

**Tags Field Config:**
```json
{
  "allow_custom_tags": true,
  "suggested_tags": ["urgent", "bug", "feature", "documentation"],
  "max_tags": 10
}
```

**Rich Text Field Config:**
```json
{
  "toolbar": ["bold", "italic", "underline", "list", "link", "image"],
  "allowed_html_tags": ["p", "strong", "em", "ul", "ol", "li", "a", "img"],
  "max_length": 5000
}
```

**Location Field Config:**
```json
{
  "allow_map_picker": true,
  "require_address": false,
  "default_map_center": {"lat": 35.6892, "lng": 51.3890}
}
```

**Calculation Field Config:**
```json
{
  "formula": "field1 + field2 * 0.1",
  "field_references": ["quantity", "unit_price"],
  "result_type": "number",
  "decimal_places": 2
}
```

**Multi-Select Field Config:**
```json
{
  "min_selections": 1,
  "max_selections": 5,
  "display_type": "checkbox" // or "multi_dropdown"
}
```

**Section Field Config:**
```json
{
  "display_style": "header", // "header", "divider", "card"
  "collapsible": false,
  "default_collapsed": false
}
```

## Implementation Status

- [x] Database models (TicketTemplate, TicketTemplateField, TicketTemplatePermission, TicketTemplateEvent, TicketTemplateFieldEvent)
- [x] Forms (TicketTemplateForm, TicketTemplateFieldForm, TicketTemplatePermissionForm, TicketTemplateEventForm)
- [x] Views (List, Create, Update, Delete for Templates)
- [x] Templates (templates_list.html, template_form.html, template_confirm_delete.html)
- [x] Dynamic formset management (JavaScript for adding/removing field rows)
- [x] Field settings panel (collapsible settings for each field)
- [x] Field-specific settings UI (time, date, reference, file upload, etc.) - ✅ پیاده‌سازی شده
- [x] Field options management (for radio/dropdown fields) - ✅ پیاده‌سازی شده (با قابلیت ذخیره و بارگذاری options)
- [ ] Field events management (for field-specific events) - **Pending**
- [ ] Ticket creation from templates - **Pending**
- [ ] Ticket field value storage - **Pending**
- [ ] Ticket workflow and status management - **Pending**

See [TICKETING_IMPLEMENTATION.md](TICKETING_IMPLEMENTATION.md) for detailed implementation notes.

## Open Questions / Future Enhancements

## پیاده‌سازی انجام شده
- [x] Ticket templates with dynamic field definitions (implemented).
- [x] Template Events (on_open, on_close, on_respond) - implemented.

## اولویت 1: الزامی برای کارکردن Basic Ticketing (فعلاً در حال پیاده‌سازی)
- [x] **Field-specific settings UI for all 25 field types** - ✅ پیاده‌سازی شده (با `ticketing_field_settings_specification.md`)
- [x] **Field options management UI for radio/dropdown/multi_select/checkbox fields** - ✅ پیاده‌سازی شده (مدیریت Options به صورت Manual)
- [ ] **Field validation at ticket creation time** - الزامی برای اطمینان از صحت داده‌های وارد شده

## اولویت 2: برای کامل کردن Core Features (بعد از اولویت 1)
- [ ] **Reference field implementation details** - استفاده از Entity Reference System در dropdown/multi_select (در specification مشخص شده)
- [ ] **Field events management UI for field-specific events** - مدیریت رویدادهای فیلدها (on_change, on_set, on_clear)
- [ ] **Field value history/audit trail** - تاریخچه تغییرات مقادیر فیلدها

## اولویت 3: Features پیشرفته (بعد از اولویت 2)
- [ ] **SLA tracking and escalation rules** - پیگیری SLA و قوانین escalation برای تیکت‌های تأخیردار
- [ ] **Ticket watchers/subscribers** - کاربرانی که به‌روزرسانی‌های تیکت را دریافت می‌کنند
- [ ] **Ticket tags/labels** - برچسب‌های اضافی برای دسته‌بندی انعطاف‌پذیرتر
- [ ] **Time tracking for ticket resolution** - پیگیری زمان صرف شده برای حل تیکت

## اولویت 4: یکپارچه‌سازی‌ها (بعد از اولویت 3)
- [ ] **Integration with inventory/production modules** - ایجاد تیکت از مسائل کالا/سفارش
- [ ] **Email integration** - ایجاد تیکت از ایمیل و ارسال نوتیفیکیشن

## اولویت 5: Optional/Advanced Features
- [ ] **Knowledge base integration** - اتصال تیکت‌ها به مقالات پایگاه دانش
- [ ] **Ticket merging and splitting functionality** - ادغام و تقسیم تیکت‌ها
- [ ] **Mobile app support considerations** - ملاحظات برای اپلیکیشن موبایل

