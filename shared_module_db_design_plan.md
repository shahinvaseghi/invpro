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

#### Table: `invproj_person`

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

Additional considerations:

- Composite unique indexes scoped by `company_id` enforce uniqueness for fields marked “UNIQUE within company”. |
- Determine how this table integrates with Django’s `AUTH_USER_MODEL`; either link via `user_id` or consolidate accounts. |
- Add employment lifecycle fields (`hire_date`, `termination_date`) or status history tables if required. |
- Validate national ID, phone, and email formats within the application layer. |
- Personnel می‌توانند عضو چند واحد سازمانی باشند؛ رابطه‌ی چند-به-چند با جدول `invproj_company_unit` از طریق جدول میانی `invproj_person_company_units` پیاده‌سازی شده است.

##### Pivot Table: `invproj_person_company_units`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-generated surrogate key. |
| `person_id` | `bigint` | `NOT NULL`, FK به `invproj_person(id)` | مرجع پرسنل. |
| `companyunit_id` | `bigint` | `NOT NULL`, FK به `invproj_company_unit(id)` | مرجع واحد سازمانی. |
| `UNIQUE(person_id, companyunit_id)` | constraint | جلوگیری از ثبت تکراری. | رابطه‌ی چند-به-چند استاندارد Django. |

#### Table: `invproj_person_assignment`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `company_id` | `bigint` | `NOT NULL`, FK to `invproj_company(id)` | Owning company. |
| `company_code` | `varchar(8)` | `NOT NULL`, check numeric | Cached company code for reporting consistency. |
| `person_id` | `bigint` | `NOT NULL`, FK to `invproj_person(id)` | Personnel reference. |
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

Additional considerations:

- Unique constraint on `(company_id, person_id, work_center_id, work_center_type)` prevents duplicate assignments. |
- Ensure only one `is_primary=1` per person per work center type via partial unique index if needed. |
- `work_center_type` supports polymorphic references; use enumerations and application logic to resolve to actual tables. |
- Track assignment periods for reporting; optional history tables can capture changes over time. |
- Validate `company_id` alignment with both person and work center to avoid cross-company assignments. |

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
- Integrate with personnel assignments, production scheduling, or cost allocation by referencing units where needed. |
- Consider separate tables for unit-to-warehouse or unit-to-cost-center mappings when more complex relationships emerge. |

### Shared Considerations

- Coordinate shared tables’ changes with module owners to avoid breaking dependencies. |
- Introduce additional role/permission granularity (e.g., field-level controls) if required by compliance. |
- Provide database views or service-layer APIs that consolidate user/company access for module consumption. |

## Open Questions

- Define canonical list of modules/resources to seed into `invproj_access_level_permission`. |
- Determine how company-specific configurations (e.g., fiscal calendars, localization) should be modeled beyond the current `metadata` usage. |
- Clarify audit/compliance requirements (e.g., need for immutable audit logs or soft-delete retention). |
