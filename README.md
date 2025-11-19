# invproj Platform

`invproj` is a modular warehouse, production, and quality-control management platform built with Django and PostgreSQL. The project is designed with multi-company (multi-tenant) support, rich auditing metadata, and clear module boundaries so that each domain can evolve independently or be split into services in the future.

## Quick Test & Run

```bash
cd invproj
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py test
python manage.py runserver 0.0.0.0:8000
```

This README documents:

- Project architecture and technology stack
- Environment setup and configuration
- Application modules (`shared`, `inventory`, `production`) and their core models
- Testing, linting, and database migration workflows
- Conventions, utilities, and roadmap items

---

## 1. Architecture Overview

### 1.1 Technology Stack

- **Language**: Python 3.12 (via system packages on Ubuntu 24.04)
- **Web framework**: Django 4.2
- **Database**: PostgreSQL (default SQLite for local quick start)
- **Task queue / cache**: Redis (planned)
- **API toolkit**: Django REST Framework, `django-filter`, `django-cors-headers`
- **Environment configuration**: `django-environ`
- **Authentication**: Custom user model extending `AbstractUser`

### 1.2 Module Layout

| Module / App | Purpose | Key Prefix |
| ------------ | ------- | ---------- |
| `shared` | Cross-cutting entities: companies, users, access hierarchy | `invproj_` |
| `inventory` | Master data, suppliers, receipts/issues, stocktaking | `inventory_` |
| `production` | BOM, process definitions, production orders, line transfers, personnel, machines | `production_` |
| `qc` | Quality inspections linked to temporary receipts | `qc_` |
| `ui` | Template-based UI shell, navigation, and dashboards | — |

Each app directory includes its own `README.md` with a deeper breakdown of files and classes. See [Documentation Files](#14-documentation-files) for a complete list of all documentation files.

Common mixins (timestamps, activation flags, metadata, sort order, multi-company scoping) are located in `shared.models` and reused across every module to ensure consistent auditing and tenancy rules.

---

## 2. Installation & Setup

### 2.1 Prerequisites

Ensure the following system packages are installed (Ubuntu 24.04 examples shown):

```bash
sudo apt update
sudo apt install python3-venv python3-pip python3-dev build-essential \
     libpq-dev redis-server postgresql postgresql-contrib
```

If you need to target Python 3.12 explicitly, install `python3.12-venv` and `python3.12-dev`.

### 2.2 Project Initialization

```bash
git clone <repo-url> invproj
cd invproj

# (optional) set up .env based on env.sample
cp env.sample .env

# create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# upgrade pip and install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

Environment variables (see `env.sample`):

| Variable | Required | Description |
| -------- | -------- | ----------- |
| `DJANGO_SECRET_KEY` | ✅ | Django secret key (change for production) |
| `DJANGO_DEBUG` | optional | Enables Django debug mode (`True` by default) |
| `DJANGO_ALLOWED_HOSTS` | optional | Comma-separated hostnames |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | optional | Comma-separated origins for CSRF |
| `DJANGO_TIME_ZONE` | optional | Default timezone (`UTC`) |
| `DJANGO_CORS_ALLOW_ALL` | optional | Allow all CORS origins (default `True`) |
| `DATABASE_URL` | optional | PostgreSQL connection string; falls back to SQLite |

### 2.3 Database Setup

1. Configure your `DATABASE_URL` (PostgreSQL recommended). Example:

   ```
   DATABASE_URL=postgres://invproj_user:STRONG_PASSWORD@localhost:5432/invproj_db
   ```

2. Run migrations:

   ```bash
   source .venv/bin/activate
   python manage.py migrate
   ```

3. Create a superuser if needed:

   ```bash
   python manage.py createsuperuser
   ```

4. Start the development server:

   ```bash
   python manage.py runserver
   ```

   برای دسترسی از دیگر دستگاه‌های شبکه محلی، سرور را روی تمام اینترفیس‌ها اجرا کنید:

   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```

   (در حالت Debug اگر `DJANGO_ALLOWED_HOSTS` خالی باشد به طور خودکار روی `*` تنظیم می‌شود.)

5. ساخت حساب ادمین (در صورتی که حسابی ندارید):

   ```bash
   python manage.py createsuperuser
   ```

6. ورود به داشبورد:
   - مرورگر → `http://<server-ip>:8000/`
   - ابتدا از فرم لاگین (پیش‌فرض Django) استفاده کنید؛ پس از ورود داشبورد UI نمایش داده می‌شود.

---

## 3. Repository Structure

```
invproj/
├── config/                 # Django project settings & URLs
├── shared/                 # Multi-company base entities
├── inventory/              # Inventory module (master data, suppliers, receipts, issues)
├── production/             # Production/BOM/work-center logic
├── qc/                     # Quality-inspection logic
├── ui/                     # Template-based UI shell (views, templates, static)
├── templates/              # Global templates (base, dashboard, components)
├── static/                 # CSS assets
├── requirements.txt        # Python dependencies
├── env.sample              # Environment variable template
└── README.md               # This guide (see app-specific README files)
```

### Key Files

| File/Directory              | Description |
|----------------------------|-------------|
| `config/settings.py`       | Environment-aware settings, app registration, DRF/CORS configs, `AUTH_USER_MODEL`. |
| `config/urls.py`           | Routes admin + root → `ui.urls`. |
| `shared/models.py`         | Base mixins + shared entities (companies, users, access). |
| `inventory/models.py`      | Inventory-specific models following design document. |
| `production/models.py`     | BOM, processes, orders, transfer entities. |
| `qc/models.py`             | Temporary receipt inspection model. |
| `ui/views.py`, `ui/urls.py`| Dashboard view and URL mapping. |
| `templates/base.html`      | Base layout including sidebar & header. |
| `templates/ui/dashboard.html`| Landing page cards summarising modules. |
| `static/css/base.css`      | Styling for layout/typography/cards. |
| `<app>/migrations/`        | Auto-generated migrations mirroring design specs. |
| `<app>/admin.py`           | Admin registrations for quick data inspection. |
| `<app>/tests.py`           | Unit tests verifying key behaviours/code generation. |

---

## 3. Application Modules

### 3.1 Shared (`shared`)

This module hosts cross-cutting entities and mixins.

- **Mixins**:
  - `TimeStampedModel`, `ActivatableModel`, `MetadataModel`, `SortableModel`
  - `CompanyScopedModel`: ensures every record carries a `company` foreign key and `company_code`
- **Models**:
  - `User`: custom auth user (`AUTH_USER_MODEL = 'shared.User'`)
  - `Company`: tenants with auditing fields
  - `CompanyUnit`: hierarchical units per company
  - `AccessLevel`, `AccessLevelPermission`: role/permission matrix
  - `UserCompanyAccess`: mapping users to companies with access levels
- **Permissions Catalog**: `shared/permissions.py` exposes a central `FEATURE_PERMISSION_MAP` that enumerates menu-level features (رسیدها، حواله‌ها، درخواست‌ها) همراه با اکشن‌های دقیق مثل `view_own`, `view_all`, `create`, `edit_own`, `edit_other`, `delete_own`, `delete_other`, `lock_*`, `unlock_*`, `approve`, `reject`, `cancel`. این نقشه مستقیماً برای ساخت `AccessLevelPermission` و کنترل نمایش منوها استفاده خواهد شد. **نکته**: `DELETE_OTHER` به تمام اسناد اضافه شده است تا امکان حذف اسناد سایر کاربران فراهم شود و `APPROVE` برای stocktaking records نیز پشتیبانی می‌شود.
- **Document Deletion**: قابلیت حذف برای تمام انواع اسناد (رسیدها، حواله‌ها، شمارش موجودی) پیاده‌سازی شده است. دکمه‌های حذف به صورت شرطی بر اساس دسترسی کاربر (`DELETE_OWN` و `DELETE_OTHER`) نمایش داده می‌شوند. اسناد قفل‌شده قابل حذف نیستند. کلاس پایه `DocumentDeleteViewBase` برای پیاده‌سازی یکپارچه استفاده می‌شود.
- **User & Access Management**: مسیرهای `/shared/users/`, `/shared/groups/`, `/shared/access-levels/` اکنون صفحات کامل لیست/ایجاد/ویرایش/حذف دارند؛ شامل فرم‌ست دسترسی شرکت برای کاربران، نگاشت گروه‌ها به `AccessLevel` و ماتریس اکشن‌ها بر اساس `FEATURE_PERMISSION_MAP`.

Each model includes constraints to enforce per-company uniqueness of codes and names. JSON fields (`metadata`, `metadata`, etc.) allow flexible extensions without schema changes.

### 3.2 Inventory (`inventory`)

Implements master data, suppliers, documents, and stock adjustments.

- **Master Data**: `ItemType`, `ItemCategory`, `ItemSubcategory`, `Warehouse`, `WorkLine`
- **Items**: `Item` (auto-generates composite `item_code`, `batch_number`), `ItemSpec`, `ItemUnit`, `ItemWarehouse`, `ItemSubstitute`
- **Suppliers**: `Supplier`, `SupplierCategory`, `SupplierSubcategory`, `SupplierItem`
- **Requests & Receipts**:
  - `PurchaseRequest`
  - `WarehouseRequest`
  - `ReceiptTemporary`, `ReceiptPermanent`, `ReceiptConsignment`
  - `ItemLot`: generates `LOT-MMYY-XXXXXX` codes to track traceable inventory
- **Issues**: `IssuePermanent`, `IssueConsumption`, `IssueConsignment`
- **Stocktaking**: `StocktakingDeficit`, `StocktakingSurplus`, `StocktakingRecord`

Key behaviours:
- Codes and sequences are auto-populated in `save()` overrides (e.g., `Item`, `ItemLot`, `PurchaseRequest`).
- Purchase and warehouse requests have dedicated create/edit/approve pages, enforce approver permissions, lock after approval, and only expose approved/locked requests for selection in permanent/consignment receipts.
- **IMPORTANT**: Approval workflows use Django `User` accounts for ALL requester and approver fields (never `Person`). The `Person` model is ONLY used in Production module for workforce management. Refer to `docs/approval_workflow.md` for the end-to-end flow.
- All models inherit auditing and multi-company mixins.
- Django admin dashboards are set up for quick data verification (`inventory/admin.py`).
- **Warehouse Restrictions**: Items can only be received/issued in warehouses explicitly configured in `ItemWarehouse` relationship. Strict validation enforced in forms (server-side and client-side).
- **Date Display**: All dates displayed in Jalali (Persian) format in UI while stored in Gregorian format in database.

### 3.3 Production (`production`)

Implements manufacturing definitions and order tracking.

- **Resources**: `WorkCenter`, `Machine` (production machines/equipment)
- **Personnel**: `Person`, `PersonAssignment` (personnel directory and work-center assignments)
- **BOM**: `BOMMaterial` (links finished items to materials with scrap allowance)
- **Process Definition**: `Process`, `ProcessStep` (with labor/machine minutes, personnel requirements)
- **Orders**: `ProductOrder` (tracks revisions, BOM references, status), `OrderPerformance`
- **Material Transfer**: `TransferToLine`, `TransferToLineItem` (staging materials from inventory to production lines)

Behaviours:
- Cross-module FK references to `inventory.Item` and `inventory.Warehouse` with cached codes.
- Unique constraints enforce one primary process per item revision and prevent duplicate transfer lines.
- Admin registrations provide immediate CRUD interfaces for manufacturing teams.

### 3.4 Quality Control (`qc`)
- **UI**: Consumes inspection data for dashboards (see `ui` module)
- Future enhancements (see roadmap) will add CAPA linkage and richer inspection result schema.

### 3.5 UI (`ui`)

Provides the initial UI foundation, base layout, and navigation scaffolding.

- **Views**: `DashboardView` (login-protected) renders platform overview content.
- **Routing**: Root URL includes `ui.urls`, mapping `/` to the dashboard.
- **Templates**:
  - `templates/base.html`: global shell with header, sidebar, and content container.
  - `templates/ui/components/sidebar.html`: modular navigation شامل بخش «Shared» (Companies، Users، Groups، Access Levels) و زیرمنوهای Inventory/Production (شامل Personnel و Machines)/QC؛ آماده برای اعمال محدودیت سطح دسترسی مبتنی بر `FEATURE_PERMISSION_MAP`.
  - `templates/ui/dashboard.html`: highlights module capabilities and next actions.
- **Context Processors**: `ui.context_processors.active_module` exposes `active_module` placeholder.
- **Static Assets**: `static/css/base.css` contains baseline typography, layout grid, and card styling.

Subsequent UI work can focus on rendering real metrics, integrating forms, and honoring role-based visibility.

---

Captures inspection data connected to temporary inventory receipts.

- **Inspections**: `ReceiptInspection`
  - One-to-one with `inventory.ReceiptTemporary`
  - Tracks inspector, inspection status, decisions, attachments, and optional nonconformity references
  - Auto-populates cached codes (`temporary_receipt_code`, `inspector_code`) on save
- **Admin Support**: `ReceiptInspectionAdmin` exposes filters for status, decision, nonconformity

Future enhancements (see roadmap) will add CAPA linkage and richer inspection result schema.

---

## 4. Running Tests & Checks

### 4.1 Unit Tests

```bash
source .venv/bin/activate
python manage.py test shared inventory production qc
```

Tests cover:
- Shared module string representations and `company_code` propagation
- Inventory generation of item codes, purchase request codes, lot numbering
- Production BOM/process/order logic
- QC inspections auto-filling codes and approval linkage

### 4.2 Static Analysis (Planned)

Add linting tools in the future:
- `flake8`, `black`, `isort`
- `pre-commit` hooks

---

## 5. Database & Migration Workflow

1. Create/update models within the corresponding app.
2. Generate migrations:

   ```bash
   python manage.py makemigrations <app_name>
   ```

3. Review the migration files, ensuring constraints and defaults align with the design docs.
4. Apply migrations locally `python manage.py migrate`.
5. For deployments, collect migrations per module and apply in order (shared → inventory → production → qc).

SQLite is used for sanity checks. Switch to PostgreSQL for advanced JSON/GIN indexing and performance.

---

## 6. Development Conventions

- **Language**: Persian for discussions, English for code, docstrings, and commit messages.
- **Coding Style**: PEP 8; place shared mixins in `shared/models.py`.
- **JSON Fields**: Always default to `dict` or `list` and set `blank=True`.
- **Multi-company**: Every business model extends `CompanyScopedModel` to guarantee tenant isolation.
- **Activation Flags**: `is_enabled`, `activated_at`, `deactivated_at` unify soft-disable semantics.
- **Metadata**: Use JSON fields to store extensible configuration or audit context.

---

## 7. Admin Access & Data Seeding

To experiment with the domain:

1. Create superuser as described earlier.
2. Populate base data via Django admin:
   - `Company`, `User`, `UserCompanyAccess`
   - `ItemType`, `ItemCategory`, `Item`, `Supplier`
   - `WorkCenter`, `Machine`, `Person`, `Process` definitions
3. Record transactions:
   - Temporary → Permanent receipt flow
   - Production order creation and performance tracking

For automated seeding, consider writing Django fixtures or custom management commands in `shared/management/commands`.

---

## 8. Deployment Checklist

Refer to `docs/system_requirements.md` for a comprehensive deployment guide. Highlights:

- Configure HTTPS (Nginx reverse proxy or IIS proxy depending on OS)
- Set up Gunicorn (Linux) or Waitress / wfastcgi (Windows)
- Configure background workers (Celery with Redis) for asynchronous tasks (future)
- Collect static files: `python manage.py collectstatic`
- Apply database migrations during deployment
- Set up monitoring (Prometheus, ELK stack, Sentry) and backups (pg_dump / wal-g)

---

## 9. Multi-Company Architecture & Company Switching

### 9.1 Company Context

The platform uses session-based company context to ensure all operations are scoped to the active company:

1. **Company Selector**: Located in the header next to the language switcher
2. **Session Storage**: Active company ID stored in `request.session['active_company_id']`
3. **Context Processor**: `shared.context_processors.active_company` provides:
   - `active_company`: Currently selected company object
   - `user_companies`: List of all companies user has access to

### 9.2 Switching Companies

Users switch companies via the dropdown in the header:
- POST to `/shared/set-company/` with `company_id` parameter
- System verifies user has access via `UserCompanyAccess`
- Session updated and page reloaded
- All subsequent queries automatically filtered by active company

### 9.3 View Integration

All inventory views extend `InventoryBaseView` which:
- Automatically filters queryset by `active_company_id`
- Provides company context to templates
- Ensures data isolation between companies

```python
# Example: Views automatically filter by active company
class ItemListView(InventoryBaseView, ListView):
    model = Item  # Automatically filtered by company_id
```

### 9.4 Adding New Views

When creating new views:
1. Extend appropriate base view (`InventoryBaseView`, etc.)
2. Use `get_queryset()` override if custom filtering needed
3. Access company via `request.session.get('active_company_id')`

---

## 10. UI Components & Templates

### 10.1 Template Structure

```
templates/
├── base.html                    # Global layout with company/language switcher
├── ui/
│   ├── dashboard.html           # Platform overview
│   └── components/
│       └── sidebar.html         # Navigation menu
└── inventory/
    ├── base.html                # Inventory module base
    ├── inventory_balance.html   # Balance calculation view
    ├── items.html               # Item catalog + links to create/edit
    ├── item_form.html           # Dedicated create/edit form with unit conversions
    ├── warehouse_requests.html  # Warehouse request management
    ├── purchase_requests.html   # Purchase request management
    ├── receipt_*.html           # Receipt documents (temporary, permanent, consignment)
    ├── issue_*.html             # Issue documents (permanent, consumption, consignment)
    └── stocktaking_*.html       # Stocktaking documents

```

### 10.2 Shared Components

All templates use:
- **Filter panels**: Collapsible filters with form controls
- **Data tables**: Sortable, paginated tables with action buttons
- **Status badges**: Color-coded status indicators
- **Empty states**: User-friendly messages when no data exists
- **Stats cards**: KPI summary cards
- **Breadcrumbs**: Navigation trail
- صفحات جدید کالا و تأمین‌کننده از همین الگو پیروی می‌کنند اما فرم اصلی و فرم‌ست‌های مرتبط را در بالای جدول نمایش می‌دهند. در صفحات رسید، تا زمان تکمیل صفحات اختصاصی‌تر، دکمه‌های ایجاد به فرم‌های ادمین متصل شده‌اند تا فرایند ثبت قطع نشود.

### 10.2.1 Dedicated Forms
- `inventory/item_form.html` یک فرم کامل برای تعریف/ویرایش کالا است و در همان صفحه امکان تعریف واحدهای ثانویه (`ItemUnit`) را می‌دهد.
- `templates/inventory/supplier_form.html` و `suppliercategory_form.html` (symlink به قالب جنریک) اکنون از طریق ویوهای `SupplierCreateView` و `SupplierCategoryCreateView` قابل دسترسی هستند.
- Receipt templates (`receipt_temporary/permanent/consignment.html`) دکمه‌های ایجاد را به مسیرهای ادمین هدایت می‌کنند تا کاربر بتواند ساده‌تر سند جدید ثبت کند.
- در بخش Shared نیز صفحه جدید «واحدها» (`shared/company_units.html`) برای مدیریت واحدهای سازمانی شرکت فعال اضافه شده است.

### 10.3 Styling

CSS classes defined in `static/css/base.css`:
- `.data-table-container`: Wrapper for data tables
- `.filter-panel`: Filter form container
- `.badge-*`: Status badges (draft, pending, approved, rejected, active, inactive)
- `.btn-*`: Button styles (primary, secondary, success)
- `.stat-card`: KPI card styling
- `.empty-state`: Empty state placeholder

### 10.4 Internationalization

The platform supports Persian (Farsi) and English with full RTL/LTR support:
- **Default language**: Persian (`LANGUAGE_CODE = 'fa'`) - application opens in Persian by default
- **Language switcher**: Available in header for instant language switching
- All templates use Django i18n:
  - `{% load i18n %}` at top of each template
  - `{% trans "Text" %}` for translatable strings
  - `locale/fa/LC_MESSAGES/django.po` contains Persian translations
  - Automatic RTL support via `dir="{{ LANGUAGE_CODE }}"` on `<html>`
- **Complete translations**: All UI elements, messages, form labels, and error messages are fully translated to Persian

### 10.5 Date Handling (Jalali/Gregorian)

The system displays dates in Jalali (Persian) format in the UI while storing them in Gregorian format in the database:

- **Storage**: All dates stored as Gregorian in database (`DateField`, `DateTimeField`)
- **Display**: Converted to Jalali format using `{% load jalali_tags %}` and `{{ date|jalali_date }}` template tag
- **Input**: Custom `JalaliDateInput` widget converts Jalali input to Gregorian before saving
- **Forms**: All document forms (`ReceiptPermanentForm`, `IssuePermanentForm`, etc.) use `JalaliDateField`
- **Benefits**: Users see familiar Jalali calendar, database maintains standard format, no dual date fields needed

For details, see `inventory/widgets.py`, `inventory/fields.py`, and `inventory/templatetags/jalali_tags.py`.

---

## 11. Inventory Balance Calculation

### 11.1 Calculation Logic

Inventory balances are calculated on-demand (not stored):

**Starting Point**: Last approved stocktaking record
- Query `StocktakingRecord` for most recent approved entry
- Use referenced surplus/deficit documents as baseline

**Incremental Updates**:
```
Current Balance = Baseline Balance
                + Sum(Permanent Receipts after baseline)
                + Sum(Surplus Adjustments after baseline)
                - Sum(Permanent Issues after baseline)
                - Sum(Consumption Issues after baseline)
                - Sum(Deficit Adjustments after baseline)
```

### 11.2 Implementation

Module: `inventory/inventory_balance.py`

Key Functions:
- `get_last_stocktaking_baseline()`: Retrieve baseline from last stocktaking
- `calculate_movements_after_baseline()`: Sum receipts and issues
- `calculate_item_balance()`: Complete balance for single item
- `calculate_warehouse_balances()`: Balances for all items in warehouse

### 11.3 Performance Considerations

- Calculations cached per request
- Index on `(company_id, warehouse_id, item_id, document_date, is_locked)`
- Consider materialized views for large datasets
- Export functionality for offline analysis

---

## 12. Warehouse Requests

New feature (added after initial design):

### 12.1 Purpose

Internal requests for material issuance from warehouse to departments/production.

### 12.2 Workflow

1. **Draft**: Created by requester
2. **Submitted**: Ready for approval
3. **Approved**: Approved by warehouse manager
4. **Issued**: Material issued (linked to issue document)
5. **Rejected/Cancelled**: Request denied or cancelled

### 12.3 Model

Table: `inventory_warehouse_request`
- Auto-generates request code: `WRQ-YYYYMM-XXXXXX`
- Links to item, warehouse, requester
- Supports priority levels (low, normal, high, urgent)
- Tracks approval chain and issue document linkage

---

## 13. Roadmap

- **QC Module Enhancements**: Extend inspections with CAPA integration, multiple inspectors, deviation workflows
- **API Layer**: Expose REST endpoints for major flows (items, purchase requests, receipts, production orders)
- **Access Control**: Enforce `AccessLevel` and `AccessLevelPermission` checks in views/API
- **Reporting**: Add analytics dashboards and export features
- **Task Queue**: Integrate Celery for heavy tasks (report generation, syncing to external ERPs)
- **SPA Integration**: Evaluate React/Vue for high-interactivity screens (e.g., production monitoring)
- **Mobile App**: Progressive Web App for warehouse scanning tasks

---

## 14. Documentation Files

This project includes comprehensive documentation organized by module and purpose:

### 14.1 Main Documentation

| File | Description |
|------|-------------|
| `README.md` | This file - platform overview, setup, and architecture guide |
| `docs/CHANGELOG.md` | Version history and release notes |
| `docs/UI_UX_CHANGELOG.md` | **Detailed UI/UX design improvements and changelog** |
| `docs/FEATURES.md` | Feature list and capabilities |
| `docs/DEVELOPMENT.md` | Development guidelines and workflows |
| `docs/DATABASE_DOCUMENTATION.md` | Database schema and relationships |
| `docs/system_requirements.md` | System requirements and deployment guide |
| `docs/ui_guidelines.md` | UI/UX guidelines and component documentation |
| `docs/approval_workflow.md` | Approval workflow reference for purchase/warehouse/stocktaking |

### 14.2 Module Design Plans

| File | Description |
|------|-------------|
| `docs/shared_module_db_design_plan.md` | Shared module database design specifications |
| `docs/inventory_module_db_design_plan.md` | Inventory module database design specifications |
| `docs/production_module_db_design_plan.md` | Production module database design specifications |
| `docs/qc_module_db_design_plan.md` | Quality Control module database design specifications |

### 14.3 Module README Files

| File | Description |
|------|-------------|
| `shared/README.md` | Shared module overview, models, and utilities |
| `shared/README_FORMS.md` | Shared module forms documentation |
| `inventory/README.md` | Inventory module overview and models |
| `inventory/README_FORMS.md` | Inventory module forms documentation |
| `inventory/README_BALANCE.md` | Inventory balance calculation logic |
| `production/README.md` | Production module overview and models (includes Personnel and Machines) |
| `qc/README.md` | Quality Control module overview |
| `ui/README.md` | UI module templates and components |
| `templates/inventory/README.md` | Inventory template documentation |

### 14.4 Documentation Structure

- **Main README** (`README.md`): Start here for platform overview and quick start
- **Module READMEs**: Each app directory contains detailed module documentation
- **Design Plans**: Database design specifications for each module
- **Form Documentation**: Detailed form documentation for complex modules
- **Template Documentation**: UI template structure and usage

For developers new to the project, start with `README.md` and then explore module-specific READMEs based on your area of work.

---

## 15. Maintainer Notes

- Always run `python manage.py test shared inventory production qc` before pushing changes.
- Maintain coverage for critical logic (code generation, workflow transitions, balance calculations).
- Document any new environment variables in both `env.sample` and this README.
- For significant schema changes, update the module design plan markdown files to keep documentation current.
- When adding new views, extend appropriate base class to maintain company filtering.
- Update locale files when adding new translatable strings: `python manage.py makemessages -l fa`

### Testing Company Switching

1. Create multiple companies in admin
2. Assign user access via `UserCompanyAccess`
3. Test company switcher in header
4. Verify data isolation between companies
5. Check that all queries respect `active_company_id`

### Debugging Tips

- Check `request.session['active_company_id']` in views
- Use Django Debug Toolbar to inspect queries
- Verify company_id filter in all querysets
- Test with users having access to multiple companies

Happy building! 🎯

