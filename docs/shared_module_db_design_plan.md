## Overview

We are designing `invproj`, a modular warehouse, production, and quality control platform built with Python and Django. The application targets PostgreSQL as the primary database engine and must run on both Linux/Nginx and Windows Server/IIS environments. Django currently serves the server-rendered UI and REST APIs, with the architecture leaving room for future SPA or mobile clients. All modules begin in a single physical database, but naming conventions (`inventory_`, `production_`, `qc_`, and shared `invproj_`) ensure we can split modules into their own databases or services when scaling demands it. Shared/global entities—companies, users, personnel, company units—reside in the `invproj_` namespace and provide tenancy, security, and configuration anchors across every module.

This document consolidates the shared (cross-module) database tables, starting with companies and users, plus supporting mappings that control user access to companies. Other shared tables (roles, permissions, configuration) can be added iteratively as requirements solidify. By centralizing these definitions we avoid duplicating shared schemas in the module-specific design documents and keep a single source of truth for core entities.

Key design principles:

- **Multi-company tenancy**: Every shared table stores `company_id` when applicable and/or manages relationships that allow users to access multiple companies safely.
- **Consistent auditing**: Timestamps, activation flags, and metadata columns follow the same conventions used across all modules (`is_enabled`, `activated_at`, `deactivated_at`, `created_at`, `edited_at`, `metadata`).
- **Modular alignment**: All shared tables avoid references to module-specific tables, relying instead on the common identifiers that other modules can consume.
- **Extensibility**: JSONB columns capture flexible attributes (branding, localization, preferences) while keeping the core schema stable.

## Database Design Plan

- Define shared tables under the `invproj_` prefix that are used by multiple modules (companies, users, user-to-company access mapping).
- Document constraints and relationships so that module-specific schemas can reference these entities without ambiguity.
- Capture auditing, metadata patterns, and JSON usage for shared entities to maintain consistency across the platform.
- Track gaps (e.g., role/permission taxonomy) for future iterations.

### Shared Tables

#### Table: `invproj_company`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `public_code` | `varchar(8)` | `NOT NULL`, `UNIQUE`, check numeric | Company identifier shared across modules. |
| `legal_name` | `varchar(180)` | `NOT NULL`, `UNIQUE` | Registered company name. |
| `display_name` | `varchar(180)` | `NOT NULL`, `UNIQUE` | Name shown in UI/documents. |
| `display_name_en` | `varchar(180)` | nullable | Latin/English display name. |
| `registration_number` | `varchar(60)` | nullable, `UNIQUE` | Government registration/license. |
| `tax_id` | `varchar(60)` | nullable, `UNIQUE` | Fiscal identifier. |
| `phone_number` | `varchar(30)` | nullable | Main contact phone. |
| `email` | `varchar(254)` | nullable | Main contact email. |
| `website` | `varchar(255)` | nullable | Website URL. |
| `address` | `text` | nullable | Headquarters address. |
| `city` | `varchar(120)` | nullable | City. |
| `state` | `varchar(120)` | nullable | State/Province. |
| `country` | `varchar(3)` | nullable | ISO alpha-3 code (e.g., `IRN`). |
| `metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Extensible properties (branding, fiscal year). |
| `is_enabled` | `smallint` | `NOT NULL`, default `1`, check in (0,1) | Active flag. |
| `activated_at` | `timestamp with time zone` | nullable | Last enable timestamp. |
| `deactivated_at` | `timestamp with time zone` | nullable | Last disable timestamp. |
| `created_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Auto-populated on insert. |
| `edited_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Update audit. |
| `created_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Creator reference. |
| `edited_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Last editor reference. |

Additional considerations:

- Companies act as tenants; all module tables reference `invproj_company` to support multi-company deployments.
- Enforce logical deletion via `is_enabled` rather than hard deletes; maintain history through metadata or future audit tables.
- Store branding assets or configuration pointers inside `metadata` or related tables.

#### Table: `invproj_user`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `username` | `varchar(150)` | `NOT NULL`, `UNIQUE` | Login identifier. |
| `email` | `varchar(254)` | `NOT NULL`, `UNIQUE` | User email address. |
| `password_hash` | `varchar(255)` | `NOT NULL` | Hashed password (Django-compatible). |
| `first_name` | `varchar(120)` | nullable | Local script given name. |
| `last_name` | `varchar(120)` | nullable | Local script family name. |
| `first_name_en` | `varchar(120)` | nullable | Latin/English given name. |
| `last_name_en` | `varchar(120)` | nullable | Latin/English family name. |
| `phone_number` | `varchar(30)` | nullable | Primary contact number. |
| `mobile_number` | `varchar(30)` | nullable | Secondary/mobile contact. |
| `is_active` | `smallint` | `NOT NULL`, default `1`, check in (0,1) | Active user flag. |
| `is_staff` | `smallint` | `NOT NULL`, default `0`, check in (0,1) | Django-style staff flag. |
| `is_superuser` | `smallint` | `NOT NULL`, default `0`, check in (0,1) | System superuser flag. |
| `last_login_at` | `timestamp with time zone` | nullable | Last successful login timestamp. |
| `metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | User preferences, localization settings. |
| `created_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Auto-populated on insert. |
| `edited_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Update audit. |

Additional considerations:

- Use Django’s password hashing utilities; align with the project’s authentication backend.
- Store profile-level settings in `metadata` (locale, notification preferences, API tokens). |
- For audit trails (login attempts, password changes), consider supplementary tables.

#### Table: `invproj_user_company_access`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `user_id` | `bigint` | `NOT NULL`, FK to `invproj_user(id)` | User reference. |
| `company_id` | `bigint` | `NOT NULL`, FK to `invproj_company(id)` | Company the user can access. |
| `access_level_id` | `bigint` | `NOT NULL`, FK to `invproj_access_level(id)` | Role/access level assigned to the user for this company. |
| `is_primary` | `smallint` | `NOT NULL`, default `0`, check in (0,1) | Marks default company context. |
| `is_enabled` | `smallint` | `NOT NULL`, default `1`, check in (0,1) | Soft-delete flag. |
| `activated_at` | `timestamp with time zone` | nullable | Last enable timestamp. |
| `deactivated_at` | `timestamp with time zone` | nullable | Last disable timestamp. |
| `created_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Auto-populated on insert. |
| `edited_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Update audit. |
| `metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Extensible fields (delegation rules, approval scopes). |

Additional considerations:

- Unique constraint on `(user_id, company_id)` prevents duplicate assignments. |
- Enforce only one `is_primary=1` per user via partial unique index. |
- Use `metadata` to store contextual permissions (e.g., allowed warehouses, modules). |

#### Table: `invproj_access_level`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `code` | `varchar(30)` | `NOT NULL`, `UNIQUE` | Role/access level code (e.g., `inventory_manager`). |
| `name` | `varchar(120)` | `NOT NULL` | Human-readable name. |
| `description` | `text` | nullable | Summary of responsibilities. |
| `is_global` | `smallint` | `NOT NULL`, default `0`, check in (0,1) | If 1, role can span multiple companies. |
| `is_enabled` | `smallint` | `NOT NULL`, default `1`, check in (0,1) | Soft-delete flag. |
| `created_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Auto-populated on insert. |
| `edited_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Update audit. |
| `metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Extensible configuration (e.g., default dashboards). |

Additional considerations:

- Populate with seed roles during deployment; allow admins to create custom roles through UI. |
- `is_global=1` roles may bypass per-company restrictions; enforce at application layer. |

#### Table: `invproj_access_level_permission`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `access_level_id` | `bigint` | `NOT NULL`, FK to `invproj_access_level(id)` | Role being granted permissions. |
| `module_code` | `varchar(30)` | `NOT NULL` | Module identifier (`inventory`, `production`, `qc`, `shared`). |
| `resource_type` | `varchar(40)` | `NOT NULL` | Category of resource (`document`, `master_data`, `report`). |
| `resource_code` | `varchar(60)` | `NOT NULL` | Specific document or entity code (e.g., `inventory_issue_consumption`). |
| `can_view` | `smallint` | `NOT NULL`, default `0`, check in (0,1) | View permission. |
| `can_create` | `smallint` | `NOT NULL`, default `0`, check in (0,1) | Create permission. |
| `can_edit` | `smallint` | `NOT NULL`, default `0`, check in (0,1) | Edit/update permission. |
| `can_delete` | `smallint` | `NOT NULL`, default `0`, check in (0,1) | Delete permission (where applicable). |
| `can_approve` | `smallint` | `NOT NULL`, default `0`, check in (0,1) | Approval/closeout permission. |
| `metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Extensible flags (e.g., field-level restrictions). |

Additional considerations:

- Unique constraint on `(access_level_id, module_code, resource_code)` prevents duplicate permission rows. |
- Use enumerations to standardize `module_code`, `resource_type`, and `resource_code` values across modules. |
- Application layer should aggregate these permissions when authorizing user actions. |
- آکشن‌های جدید (مانند `view_own` در مقابل `view_all`, `lock`/`unlock`, `approve`, `reject`, `cancel`) در `metadata` ذخیره می‌شوند به‌صورت ساختار JSON که از `shared.permissions.PermissionAction` پیروی می‌کند، تا زمانی که در یک نسخه‌ی بعدی اسکیمای صریح‌تری برای هر اکشن ایجاد شود. |
- Future enhancements can add time-bound permissions or scope limits (warehouses, work centers) via `metadata` or companion tables. |

##### Permission Action Catalog

- ماژول `shared/permissions.py` یک کاتالوگ رسمی از ویژگی‌ها (`FeaturePermission`) و اکشن‌های پشتیبانی‌شده (`PermissionAction`) نگه می‌دارد.
- هر ویژگی با `code` یکتا (مثل `inventory.receipts.permanent`) توصیف می‌شود و لیست اکشن‌هایی که این ویژگی پوشش می‌دهد شامل موارد زیر است:
  - `VIEW_OWN`, `VIEW_ALL`
  - `CREATE`
  - `EDIT_OWN`, `EDIT_OTHER`
  - `DELETE_OWN`, `DELETE_OTHER`
  - `LOCK_OWN`, `LOCK_OTHER`
  - `UNLOCK_OWN`, `UNLOCK_OTHER`
  - `APPROVE`, `REJECT`, `CANCEL`
- **نکته مهم**: `DELETE_OTHER` به تمام اسناد (receipts، issues، requests، stocktaking) اضافه شده است تا امکان حذف اسناد سایر کاربران برای کاربران با دسترسی مناسب فراهم شود.
- `APPROVE` برای stocktaking records نیز اضافه شده است تا فرایند تایید اسناد شمارش امکان‌پذیر باشد.
- هنگام ساخت رکوردهای `AccessLevelPermission`، فیلد `metadata` اکشن‌های فعال را به‌صورت دیکشنری ذخیره می‌کند، مثال:
  ```json
  {
    "allow": ["view_own", "create", "lock_own"],
    "view_scope": "own"
  }
  ```
- ساختار فوق امکان توسعه‌ی آتی (افزودن اکشن‌های جدید، تعیین محدوده‌ی مشاهده یا قفل‌کردن) را بدون تغییر اسکیمای اصلی فراهم می‌کند و در لایه‌ی اپلیکیشن با استفاده از Enum های تعریف‌شده تفسیر می‌شود.

#### Table: `invproj_group_profile`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-generated |
| `group_id` | `bigint` | `NOT NULL`, `UNIQUE`, FK به `auth_group(id)` | نگاشت یک‌به‌یک به گروه Django |
| `description` | `varchar(255)` | nullable | توضیح فارسی/انگلیسی |
| `is_enabled` | `smallint` | `NOT NULL`, default `1`, check in (0,1) | وضعیت فعال/غیرفعال گروه |
| `metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | داده‌های توسعه‌پذیر (تنظیمات نمایشی، برچسب‌ها) |
| `created_at` | `timestamptz` | `NOT NULL`, default `now()` | ثبت زمان ایجاد |
| `edited_at` | `timestamptz` | `NOT NULL`, default `now()` | ثبت زمان بروزرسانی |

Relationship:

- `ManyToMany(group_profile.access_levels ↔ invproj_access_level)`: تعیین می‌کند هر گروه از چه سطوح دسترسی تشکیل شده است. جدول میانی توسط Django تولید می‌شود (`group_profile_access_levels`).
- حذف گروه (`auth_group`) باعث حذف خودکار پروفایل می‌شود (`on_delete=CASCADE`).

کاربرد:

- رابط کاربری «Groups» در ماژول Shared این جدول را می‌نویسد/می‌خواند؛ اعضای گروه همچنان از طریق `auth_user_groups` مدیریت می‌شوند.
- فیلد `is_enabled` برای غیرفعال کردن گروه بدون حذف کردن آن استفاده می‌شود (مطابق الگوی ActivatableModel).
- می‌توان از `metadata` برای نگهداری پیکربندی‌های اختصاصی (مانند ترتیب نمایش یا محدودیت‌های سفارشی) استفاده کرد.

#### Table: `invproj_company_unit`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `company_id` | `bigint` | `NOT NULL`, FK to `invproj_company(id)` | Owning company for the business unit. |
| `company_code` | `varchar(8)` | `NOT NULL`, check numeric | Cached company code. |
| `public_code` | `varchar(6)` | `NOT NULL`, `UNIQUE` within company, check numeric | Human-readable unit code. |
| `name` | `varchar(180)` | `NOT NULL`, `UNIQUE` within company | Unit name (local language). |
| `name_en` | `varchar(180)` | nullable | Unit name in Latin alphabet. |
| `unit_type` | `varchar(30)` | `NOT NULL` | Classification (`department`, `plant`, `cost_center`, etc.). |
| `parent_unit_id` | `bigint` | nullable, FK to `invproj_company_unit(id)` | Optional hierarchical parent. |
| `is_enabled` | `smallint` | `NOT NULL`, default `1`, check in (0,1) | Active flag. |
| `activated_at` | `timestamp with time zone` | nullable | Last enable timestamp. |
| `deactivated_at` | `timestamp with time zone` | nullable | Last disable timestamp. |
| `created_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Auto-populated on insert. |
| `edited_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Update audit. |
| `created_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Creator reference. |
| `edited_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Last editor reference. |
| `description` | `varchar(255)` | nullable | Short description or responsibilities. |
| `notes` | `text` | nullable | Additional operational notes. |
| `metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Extensible attributes (cost center codes, contact details). |

Additional considerations:

- Unique constraints scoped by `(company_id, public_code)` and `(company_id, name)` maintain unit uniqueness per company. |
- Use `parent_unit_id` to model hierarchy; enforce company alignment between parent and child units. |
- Integrate with production scheduling or cost allocation by referencing units where needed. |
- Consider separate tables for unit-to-warehouse or unit-to-cost-center mappings when more complex relationships emerge. |

#### Table: `invproj_section_registry`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `section_code` | `varchar(6)` | `NOT NULL`, `UNIQUE`, check numeric | 6-digit section code (XXYYZZ format: module + menu + submenu). |
| `nickname` | `varchar(50)` | `NOT NULL`, `UNIQUE` | Unique nickname for the section (e.g., "users", "purchase_requests", "inspections"). |
| `module_code` | `varchar(2)` | `NOT NULL`, check numeric | Module number (00=dashboard, 01=shared, 02=inventory, 03=production, 04=qc, etc.). |
| `menu_number` | `varchar(2)` | `NOT NULL`, check numeric | Menu number within module (2 digits). |
| `submenu_number` | `varchar(2)` | nullable, check numeric | Submenu number (2 digits, NULL if no submenu). |
| `name` | `varchar(180)` | `NOT NULL` | Display name (local language). |
| `name_en` | `varchar(180)` | nullable | Display name in English/Latin. |
| `description` | `text` | nullable | Section description. |
| `module` | `varchar(30)` | `NOT NULL` | Module identifier (e.g., "shared", "inventory", "production", "qc"). |
| `app_label` | `varchar(30)` | `NOT NULL` | Django app label (e.g., "shared", "inventory", "production", "qc"). |
| `list_url_name` | `varchar(100)` | nullable | URL name for list view (e.g., "inventory:items", "shared:users"). |
| `detail_url_name` | `varchar(100)` | nullable | URL name for detail/edit view (e.g., "inventory:item_edit", "shared:user_edit"). |
| `is_enabled` | `smallint` | `NOT NULL`, default `1`, check in (0,1) | Active flag. |
| `sort_order` | `smallint` | `NOT NULL`, default `0` | Display order in registry/list. |
| `activated_at` | `timestamp with time zone` | nullable | Last enable timestamp. |
| `deactivated_at` | `timestamp with time zone` | nullable | Last disable timestamp. |
| `created_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Auto-populated on insert. |
| `edited_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Update audit. |
| `created_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Creator reference. |
| `edited_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Last editor reference. |
| `metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Extensible fields (future: action definitions, parameters, permissions). |

Additional considerations:

- **Unique constraints**:
  - `section_code` must be unique across all sections
  - `nickname` must be unique across all sections
  - Ensure `section_code` matches format: `module_code` (2) + `menu_number` (2) + `submenu_number` (2) or `00` if no submenu
- **Code validation**: `section_code` should match pattern: `^\d{6}$` (exactly 6 digits)
- **Registry seeding**: Sections should be populated via data migration or initial fixture during deployment. **IMPORTANT**: When adding new menu items or sections, they MUST be registered in this table via data migration.
- **Module mapping**: `module` field maps to module name (shared, inventory, production, qc), while `module_code` is numeric (01, 02, 03, 04)
- **Menu numbering**: The `menu_number` field must reflect the **actual order in the sidebar**, not arbitrary numbers. Count menu items sequentially starting from 01.
- **Maintenance**: See [Entity Reference System Documentation](../ENTITY_REFERENCE_SYSTEM.md) for detailed instructions on adding new sections and actions.
- **Index strategy**:
  - Index on `section_code` for fast lookups by code
  - Index on `nickname` for fast lookups by nickname
  - Index on `(module_code, is_enabled, sort_order)` for module-based queries
- **Future extension**: The `metadata` field can later store action definitions, parameter schemas, and permission requirements when action registry is implemented

#### Table: `invproj_action_registry`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `section_id` | `bigint` | FK to `invproj_section_registry(id)`, `NOT NULL` | Reference to the section that owns this action. |
| `action_name` | `varchar(50)` | `NOT NULL` | Action identifier (e.g., "show", "approve", "reject", "lock", "delete", "create"). |
| `action_label` | `varchar(180)` | `NOT NULL` | Human-readable label for the action (local language). |
| `action_label_en` | `varchar(180)` | nullable | Human-readable label in English. |
| `description` | `text` | nullable | Detailed description of what this action does. |
| `handler_function` | `varchar(200)` | nullable | Fully qualified path to the handler function/class (e.g., "inventory.views.requests.PurchaseRequestApproveView"). |
| `url_name` | `varchar(100)` | nullable | Django URL name for this action (e.g., "inventory:purchase_request_approve"). |
| `parameter_schema` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | JSON schema defining required/optional parameters. Example: `{"code": {"type": "string", "required": true, "description": "Document code"}}`. |
| `permission_required` | `varchar(100)` | nullable | Feature permission code required for this action (e.g., "inventory.requests.purchase:approve"). |
| `requires_confirmation` | `smallint` | `NOT NULL`, default `0`, check in (0,1) | Whether this action requires user confirmation before execution. |
| `is_destructive` | `smallint` | `NOT NULL`, default `0`, check in (0,1) | Flag indicating if this is a destructive action (delete, disable, etc.). |
| `is_enabled` | `smallint` | `NOT NULL`, default `1`, check in (0,1) | Active flag. |
| `sort_order` | `smallint` | `NOT NULL`, default `0` | Display order for actions within the same section. |
| `created_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Auto-populated on insert. |
| `edited_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Update audit. |
| `created_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Creator reference. |
| `edited_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Last editor reference. |
| `metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Extensible fields for additional configuration. |

Additional considerations:

- **Unique constraints**:
  - `(section_id, action_name)` must be unique (each section can have only one action with the same name)
- **Parameter schema format**: JSON schema following JSON Schema Draft 7 specification for parameter validation
- **Handler resolution**: The system will attempt to resolve `handler_function` dynamically, falling back to URL routing if handler is not found
- **Permission integration**: `permission_required` should reference the actual permission system in use (e.g., feature permissions)
- **Index strategy**:
  - Index on `(section_id, is_enabled, sort_order)` for fast queries of enabled actions per section
  - Index on `action_name` for lookups by action name across sections
  - Index on `url_name` for reverse URL resolution
- **Action naming conventions**: Use lowercase with underscores (snake_case) for action names
- **Common actions**: Standard actions include:
  - `show`: Display/list items
  - `showown`: Show own items
  - `create`: Create new item
  - `edit`: Edit existing item
  - `delete`: Delete item
  - `approve`: Approve document/request
  - `reject`: Reject document/request
  - `lock`: Lock document (prevent further edits)
  - `unlock`: Unlock document
  - `send_to_qc`: Send temporary receipt to QC
- **Data seeding**: Actions should be populated via data migration during deployment based on actual views and URL patterns. **IMPORTANT**: When adding new actions to a section (e.g., approve, reject, create_receipt_from), they MUST be registered in this table via data migration.
- **Special workflow actions**: Actions like `create_receipt_from_purchase_request` and `create_issue_from_warehouse_request` enable automated workflows between related modules. These actions typically open intermediate selection pages for user input before executing the final action.
- **Maintenance**: See [Entity Reference System Documentation](../ENTITY_REFERENCE_SYSTEM.md) for detailed instructions on adding new sections and actions.

### Registry Maintenance and Adding New Sections

**CRITICAL**: Whenever a new menu item or section is added to the application, it **MUST** be registered in the Entity Reference System.

#### Process for Adding a New Section:

1. **Determine Section Code**:
   - Format: `XXYYZZ` (6 digits)
   - `XX` = Module number (2 digits: 00=Dashboard, 01=Shared, 02=Inventory, etc.)
   - `YY` = Menu number (2 digits): **Must match the order in sidebar** (sequential: 01, 02, 03...)
   - `ZZ` = Submenu number (2 digits): Sequential if part of submenu (01, 02, 03...), or `00`/`NULL` if no submenu

2. **Create Data Migration**:
   - Create new migration file: `shared/migrations/XXXX_add_new_section.py`
   - Add section entry to `SectionRegistry` table
   - Add all actions for the section to `ActionRegistry` table

3. **Required Information for Section**:
   - `section_code`: 6-digit unique code
   - `nickname`: Unique snake_case identifier
   - `module_code`, `menu_number`, `submenu_number`: Based on sidebar position
   - `name`, `name_en`: Display names (local language and English)
   - `module`, `app_label`: Django module/app names
   - `list_url_name`, `detail_url_name`: Django URL names

4. **Required Information for Actions**:
   - `action_name`: Unique identifier within section (e.g., `show`, `add`, `edit`, `approve`)
   - `action_label`, `action_label_en`: Human-readable labels
   - `url_name`: Django URL name for the action
   - `parameter_schema`: JSON schema defining parameters (if any)
   - `permission_required`: Feature permission code (e.g., `inventory.requests.purchase:approve`)
   - `requires_confirmation`: Whether user confirmation is needed
   - `is_destructive`: Whether this is a destructive action (delete, disable, etc.)

5. **Special Workflow Actions**:
   
   **For Purchase Requests → Receipts**:
   - Action: `create_receipt_from`
   - Parameters: `id=<request_id>`, `type=<temporary|permanent|consignment>`
   - Description: Creates receipt documents from approved purchase requests
   - Permission: `inventory.receipts.*:create_receipt_from_purchase_request`
   - Behavior: Opens intermediate selection page for quantity adjustment and notes

   **For Warehouse Requests → Issues**:
   - Action: `create_issue_from`
   - Parameters: `id=<request_id>`, `type=<permanent|consumption|consignment>`
   - Description: Creates issue documents from approved warehouse requests
   - Permission: `inventory.issues.*:create_issue_from_warehouse_request`
   - Behavior: Opens intermediate selection page for quantity adjustment and notes

6. **Configure Access Level Permissions**:
   - **CRITICAL**: After creating a new section, permissions MUST be configured in Access Levels
   - Go to `/shared/access-levels/` in the application
   - Create or edit Access Levels that should have access to the new section
   - Configure all applicable permissions:
     - View (view_own / view_all)
     - Create
     - Edit (edit_own / edit_other)
     - Delete (delete_own / delete_other)
     - Approve/Reject (if applicable)
     - Lock/Unlock (if applicable)
     - Any custom actions specific to the section
   - Assign the configured Access Levels to appropriate users or groups
   - **Without completing this step, users will not be able to access the new section, even if it appears in the sidebar**

7. **Update Documentation**:
   - Update `docs/ENTITY_REFERENCE_SYSTEM.md` with new section details
   - Document all actions for the section
   - Add to appropriate module registry table

8. **Run Migration**:
   - Ensure migration runs during deployment
   - Verify data in `SectionRegistry` and `ActionRegistry` tables

**Example Migration Structure**:
```python
def populate_new_section(apps, schema_editor):
    SectionRegistry = apps.get_model('shared', 'SectionRegistry')
    ActionRegistry = apps.get_model('shared', 'ActionRegistry')
    
    # Add section
    section = SectionRegistry.objects.get_or_create(
        section_code='020901',
        defaults={
            'nickname': 'new_feature',
            'module_code': '02',
            'menu_number': '09',  # 9th menu item in sidebar
            # ... other fields
        }
    )
    
    # Add actions
    ActionRegistry.objects.get_or_create(
        section=section,
        action_name='show',
        defaults={
            'action_label': 'مشاهده',
            'url_name': 'inventory:new_feature_list',
            # ... other fields
        }
    )
```

**For detailed step-by-step instructions, see**: [Entity Reference System Documentation](../ENTITY_REFERENCE_SYSTEM.md#adding-new-sections-and-actions)

### Shared Considerations

- Coordinate shared tables' changes with module owners to avoid breaking dependencies. |
- Introduce additional role/permission granularity (e.g., field-level controls) if required by compliance. |
- Provide database views or service-layer APIs that consolidate user/company access for module consumption. |
- **Entity Reference System**: All sections and actions must be registered in `SectionRegistry` and `ActionRegistry` tables for cross-module automation and workflow integration. |

## Open Questions

- Define canonical list of modules/resources to seed into `invproj_access_level_permission`. |
- Determine how company-specific configurations (e.g., fiscal calendars, localization) should be modeled beyond the current `metadata` usage. |
- Clarify audit/compliance requirements (e.g., need for immutable audit logs or soft-delete retention). |
