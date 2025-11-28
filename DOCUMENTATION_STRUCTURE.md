# ساختار مستندسازی پروژه (Documentation Structure)

این فایل ساختار درختی تمام فایل‌های مستندسازی (README) در پروژه را نشان می‌دهد.

---

## 📁 ساختار کلی

```
invproj/
├── 📄 MIGRATIONS_README.md
├── 📄 DOCUMENTATION_STATUS.md
├── 📄 DOCUMENTATION_STRUCTURE.md (این فایل)
│
├── 📁 inventory/
│   ├── 📁 views/
│   │   ├── 📄 README_MASTER_DATA.md
│   │   ├── 📄 README_RECEIPTS.md
│   │   ├── 📄 README_ISSUES.md
│   │   ├── 📄 README_REQUESTS.md
│   │   ├── 📄 README_STOCKTAKING.md
│   │   ├── 📄 README_BALANCE.md
│   │   ├── 📄 README_API.md
│   │   ├── 📄 README_BASE.md
│   │   ├── 📄 README_ITEM_IMPORT.md
│   │   ├── 📄 README_CREATE_ISSUE_FROM_WAREHOUSE_REQUEST.md
│   │   └── 📄 README_ISSUES_FROM_WAREHOUSE_REQUEST.md
│   │
│   ├── 📁 forms/
│   │   ├── 📄 README_MASTER_DATA.md
│   │   ├── 📄 README_RECEIPT.md
│   │   ├── 📄 README_ISSUE.md
│   │   ├── 📄 README_REQUEST.md
│   │   ├── 📄 README_BASE.md
│   │   └── 📄 README_STOCKTAKING.md
│   │
│   ├── 📁 utils/
│   │   ├── 📄 README_CODES.md
│   │   └── 📄 README_JALALI.md
│   │
│   ├── 📁 services/
│   │   └── 📄 README_SERIALS.md
│   │
│   ├── 📁 templatetags/
│   │   └── 📄 README_JALALI_TAGS.md
│   │
│   └── 📁 management/
│       └── 📁 commands/
│           └── 📄 README_CLEANUP_TEST_RECEIPTS.md
│
├── 📁 production/
│   ├── 📁 views/
│   │   ├── 📄 README_BOM.md
│   │   ├── 📄 README_PROCESS.md
│   │   ├── 📄 README_PRODUCT_ORDER.md
│   │   ├── 📄 README_MACHINE.md
│   │   ├── 📄 README_WORK_LINE.md
│   │   ├── 📄 README_PERSONNEL.md
│   │   ├── 📄 README_TRANSFER_TO_LINE.md
│   │   ├── 📄 README_PERFORMANCE_RECORD.md
│   │   └── 📄 README_PLACEHOLDERS.md
│   │
│   └── 📁 forms/
│       ├── 📄 README_BOM.md
│       ├── 📄 README_PROCESS.md
│       ├── 📄 README_PRODUCT_ORDER.md
│       ├── 📄 README_WORK_LINE.md
│       ├── 📄 README_MACHINE.md
│       ├── 📄 README_PERSON.md
│       ├── 📄 README_TRANSFER_TO_LINE.md
│       └── 📄 README_PERFORMANCE_RECORD.md
│
├── 📁 qc/
│   └── 📁 views/
│       └── 📄 README_INSPECTIONS.md
│
├── 📁 ticketing/
│   ├── 📁 views/
│   │   ├── 📄 README_BASE.md
│   │   ├── 📄 README_CATEGORIES.md
│   │   ├── 📄 README_SUBCATEGORIES.md
│   │   ├── 📄 README_TEMPLATES.md
│   │   ├── 📄 README_TICKETS.md
│   │   ├── 📄 README_DEBUG.md
│   │   └── 📄 README_PLACEHOLDERS.md
│   │
│   ├── 📁 forms/
│   │   ├── 📄 README_BASE.md
│   │   ├── 📄 README_CATEGORIES.md
│   │   ├── 📄 README_TEMPLATES.md
│   │   └── 📄 README_TICKETS.md
│   │
│   └── 📁 utils/
│       └── 📄 README_CODES.md
│
├── 📁 shared/
│   ├── 📁 views/
│   │   ├── 📄 README_USERS.md
│   │   ├── 📄 README_COMPANIES.md
│   │   ├── 📄 README_ACCESS_LEVELS.md
│   │   ├── 📄 README_GROUPS.md
│   │   ├── 📄 README_COMPANY_UNITS.md
│   │   ├── 📄 README_AUTH.md
│   │   ├── 📄 README_SMTP_SERVER.md
│   │   └── 📄 README_BASE.md
│   │
│   ├── 📁 forms/
│   │   ├── 📄 README_USERS.md
│   │   ├── 📄 README_COMPANIES.md
│   │   ├── 📄 README_ACCESS_LEVELS.md
│   │   ├── 📄 README_GROUPS.md
│   │   └── 📄 README_SMTP_SERVER.md
│   │
│   ├── 📁 utils/
│   │   ├── 📄 README_PERMISSIONS.md
│   │   ├── 📄 README_MODULES.md
│   │   └── 📄 README_EMAIL.md
│   │
│   ├── 📁 templatetags/
│   │   ├── 📄 README_ACCESS_TAGS.md
│   │   └── 📄 README_JSON_FILTERS.md
│   │
│   └── 📄 README_CONTEXT_PROCESSORS.md
│
├── 📁 accounting/
│   └── 📄 README_VIEWS.md
│
├── 📁 sales/
│   └── 📄 README_VIEWS.md
│
├── 📁 hr/
│   └── 📄 README_VIEWS.md
│
├── 📁 office_automation/
│   └── 📄 README_VIEWS.md
│
├── 📁 transportation/
│   └── 📄 README_VIEWS.md
│
├── 📁 procurement/
│   └── 📄 README_VIEWS.md
│
└── 📁 ui/
    ├── 📄 README.md
    └── 📄 README_CONTEXT_PROCESSORS.md
```

---

## 📄 فایل‌های مستندسازی

### Root Project

#### `MIGRATIONS_README.md`
مستندسازی کلی تمام migration files در تمام ماژول‌ها (inventory, production, qc, ticketing, shared). شامل توضیحات هر migration و تغییرات schema.

#### `DOCUMENTATION_STATUS.md`
فایل وضعیت مستندسازی که لیست کامل تمام فایل‌های مستندسازی شده و باقی‌مانده را نشان می‌دهد. شامل آمار کلی و اولویت‌بندی.

#### `DOCUMENTATION_STRUCTURE.md`
این فایل - ساختار درختی تمام فایل‌های مستندسازی و مسیرهای آن‌ها.

---

### Inventory Module

#### Views

**`inventory/views/README_MASTER_DATA.md`**
مستندسازی 27 کلاس view برای مدیریت داده‌های پایه: ItemType, ItemCategory, ItemSubcategory, Item, Warehouse, Supplier, SupplierCategory. شامل CRUD operations و ProtectedError handling.

**`inventory/views/README_RECEIPTS.md`**
مستندسازی 27 کلاس view برای مدیریت رسیدها: Temporary, Permanent, Consignment. شامل ایجاد از purchase request، مدیریت serials، و item filtering.

**`inventory/views/README_ISSUES.md`**
مستندسازی 18 کلاس view برای مدیریت حواله‌ها: Permanent, Consumption, Consignment. شامل serial assignment و ایجاد از warehouse request.

**`inventory/views/README_REQUESTS.md`**
مستندسازی 14 کلاس view برای مدیریت درخواست‌ها: Purchase Request و Warehouse Request. شامل multi-line support، approval workflow، و item filtering.

**`inventory/views/README_STOCKTAKING.md`**
مستندسازی 16 کلاس view برای مدیریت شمارش انبار: Deficit, Surplus, Record. شامل lock mechanism و approval workflow.

**`inventory/views/README_BALANCE.md`**
مستندسازی 3 کلاس view برای نمایش موجودی انبار: InventoryBalanceView, InventoryBalanceDetailsView, InventoryBalanceAPIView. شامل محاسبه balance و transaction history.

**`inventory/views/README_API.md`**
مستندسازی 10 function-based view برای API endpoints: filtered items, categories, subcategories, item units, warehouses, serials. شامل JSON responses و dynamic filtering.

**`inventory/views/README_BASE.md`**
مستندسازی 5 کلاس base: InventoryBaseView, DocumentLockProtectedMixin, DocumentLockView, LineFormsetMixin, ItemUnitFormsetMixin. شامل common functionality برای تمام views.

**`inventory/views/README_ITEM_IMPORT.md`**
مستندسازی 2 کلاس view برای import کالاها از Excel: ItemExcelTemplateDownloadView, ItemExcelImportView. شامل Excel parsing، validation، و error handling.

**`inventory/views/README_CREATE_ISSUE_FROM_WAREHOUSE_REQUEST.md`**
مستندسازی 4 کلاس view برای ایجاد issue از warehouse request: base class و 3 subclass برای Permanent, Consumption, Consignment. شامل quantity selection و session management.

**`inventory/views/README_ISSUES_FROM_WAREHOUSE_REQUEST.md`**
مستندسازی 3 کلاس view برای ایجاد مستقیم issue از warehouse request. شامل pre-population از warehouse request و به‌روزرسانی quantity_issued.

#### Forms

**`inventory/forms/README_MASTER_DATA.md`**
مستندسازی forms برای داده‌های پایه: ItemTypeForm, ItemCategoryForm, ItemSubcategoryForm, ItemForm, WarehouseForm, SupplierForm. شامل validation و code generation.

**`inventory/forms/README_RECEIPT.md`**
مستندسازی forms برای رسیدها: ReceiptTemporaryForm, ReceiptPermanentForm, ReceiptConsignmentForm و line forms. شامل multi-line support، serial management، و unit conversion.

**`inventory/forms/README_ISSUE.md`**
مستندسازی forms برای حواله‌ها: IssuePermanentForm, IssueConsumptionForm, IssueConsignmentForm و line forms. شامل serial assignment و warehouse validation.

**`inventory/forms/README_REQUEST.md`**
مستندسازی forms برای درخواست‌ها: PurchaseRequestForm, PurchaseRequestLineForm, WarehouseRequestForm, WarehouseRequestLineForm. شامل multi-line support و item filtering.

**`inventory/forms/README_BASE.md`**
مستندسازی base forms و helper functions: ReceiptBaseForm, IssueBaseForm, StocktakingBaseForm, BaseLineFormSet. شامل UNIT_CHOICES و code generation helpers.

**`inventory/forms/README_STOCKTAKING.md`**
مستندسازی forms برای شمارش انبار: StocktakingDeficitForm, StocktakingSurplusForm, StocktakingRecordForm. شامل document code generation و approval handling.

#### Utils

**`inventory/utils/README_CODES.md`**
مستندسازی تابع `generate_sequential_code` برای تولید کدهای متوالی عددی. شامل company scoping، extra filters، و transaction safety.

**`inventory/utils/README_JALALI.md`**
مستندسازی توابع تبدیل تاریخ میلادی به شمسی: gregorian_to_jalali, jalali_to_gregorian, today_jalali, today_gregorian. شامل format handling و error handling.

#### Services

**`inventory/services/README_SERIALS.md`**
مستندسازی service برای مدیریت serial tracking: generate_receipt_serials, sync_issue_serials, finalize_issue_serials. شامل receipt-based و line-based functions برای multi-line support.

#### Template Tags

**`inventory/templatetags/README_JALALI_TAGS.md`**
مستندسازی template filters برای نمایش تاریخ شمسی: jalali_date, jalali_date_short, jalali_date_long, jalali_datetime. شامل format options و type safety.

#### Management Commands

**`inventory/management/commands/README_CLEANUP_TEST_RECEIPTS.md`**
مستندسازی management command برای حذف یا نمایش test receipts. شامل `--show` flag و safe deletion.

---

### Production Module

#### Views

**`production/views/README_BOM.md`**
مستندسازی 4 کلاس view برای مدیریت BOM: List, Create, Update, Delete. شامل finished item filtering و material line management.

**`production/views/README_PROCESS.md`**
مستندسازی 4 کلاس view برای مدیریت Process: List, Create, Update, Delete. شامل work line management و M2M saving.

**`production/views/README_PRODUCT_ORDER.md`**
مستندسازی 4 کلاس view برای مدیریت Product Order: List, Create, Update, Delete. شامل transfer request creation و permission checks.

**`production/views/README_MACHINE.md`**
مستندسازی 4 کلاس view برای مدیریت Machine: List, Create, Update, Delete. شامل work center filtering.

**`production/views/README_WORK_LINE.md`**
مستندسازی 4 کلاس view برای مدیریت Work Line: List, Create, Update, Delete. شامل personnel و machines M2M management.

**`production/views/README_PERSONNEL.md`**
مستندسازی 4 کلاس view برای مدیریت Personnel: List, Create, Update, Delete. شامل company units prefetching.

**`production/views/README_TRANSFER_TO_LINE.md`**
مستندسازی 6 کلاس view برای مدیریت Transfer to Line: List, Create, Update, Delete, Approve, Reject. شامل approval workflow و BOM items handling.

**`production/views/README_PERFORMANCE_RECORD.md`**
مستندسازی 7 کلاس view برای مدیریت Performance Record: List, Create, Update, Delete, Approve, Reject, Create Receipt. شامل formsets برای materials, persons, machines.

**`production/views/README_PLACEHOLDERS.md`**
مستندسازی placeholder views که در حال حاضر خالی هستند و برای آینده طراحی شده‌اند.

#### Forms

**`production/forms/README_BOM.md`**
مستندسازی BOMForm, BOMMaterialLineForm, BOMMaterialLineFormSetBase. شامل finished item filtering و material validation.

**`production/forms/README_PROCESS.md`**
مستندسازی ProcessForm با work_lines به عنوان ModelMultipleChoiceField. شامل BOM filtering و approved_by permission-based filtering.

**`production/forms/README_PRODUCT_ORDER.md`**
مستندسازی ProductOrderForm با create_transfer_request boolean field. شامل BOM validation و conditional transfer_approved_by validation.

**`production/forms/README_WORK_LINE.md`**
مستندسازی WorkLineForm با personnel و machines M2M fields. شامل warehouse filtering و M2M saving.

**`production/forms/README_MACHINE.md`**
مستندسازی MachineForm با work_center ForeignKey. شامل company filtering برای work center.

**`production/forms/README_PERSON.md`**
مستندسازی PersonForm با company_units M2M و use_personnel_code_as_username boolean. شامل username logic و unit validation.

**`production/forms/README_TRANSFER_TO_LINE.md`**
مستندسازی TransferToLineForm, TransferToLineItemForm, TransferToLineItemFormSet. شامل material filtering و BOM items handling.

**`production/forms/README_PERFORMANCE_RECORD.md`**
مستندسازی PerformanceRecordForm و 3 form class دیگر برای materials, persons, machines. شامل formsets و process-specific work line filtering.

---

### QC Module

#### Views

**`qc/views/README_INSPECTIONS.md`**
مستندسازی 3 کلاس view برای QC inspections: TemporaryReceiptQCListView, TemporaryReceiptQCApproveView, TemporaryReceiptQCRejectView. شامل status filtering و transaction handling.

---

### Ticketing Module

#### Views

**`ticketing/views/README_BASE.md`**
مستندسازی TicketingBaseView که base class برای تمام ticketing views است. شامل common context و queryset filtering.

**`ticketing/views/README_CATEGORIES.md`**
مستندسازی 4 کلاس view برای مدیریت Ticket Categories: List, Create, Update, Delete. شامل permission formsets و parent category handling.

**`ticketing/views/README_SUBCATEGORIES.md`**
مستندسازی 4 کلاس view برای مدیریت Ticket Subcategories: List, Create, Update, Delete. شامل parent category validation.

**`ticketing/views/README_TEMPLATES.md`**
مستندسازی 4 کلاس view برای مدیریت Ticket Templates: List, Create, Update, Delete. شامل multiple formsets برای fields, permissions, events.

**`ticketing/views/README_TICKETS.md`**
مستندسازی 3 کلاس view برای مدیریت Tickets: List, Create, Edit. شامل reported_by auto-setting و success URL redirection.

**`ticketing/views/README_DEBUG.md`**
مستندسازی debug_log_view function که API endpoint برای دریافت و log کردن debug messages از browser است.

**`ticketing/views/README_PLACEHOLDERS.md`**
مستندسازی placeholder views که در حال حاضر خالی هستند و برای آینده طراحی شده‌اند.

#### Forms

**`ticketing/forms/README_BASE.md`**
مستندسازی TicketingBaseForm و TicketFormMixin. شامل company context و cross-field validation.

**`ticketing/forms/README_CATEGORIES.md`**
مستندسازی TicketCategoryForm, TicketCategoryPermissionForm, TicketCategoryPermissionFormSet. شامل parent filtering و read-only public code.

**`ticketing/forms/README_TEMPLATES.md`**
مستندسازی TicketTemplateForm و 5 form class دیگر برای dynamic fields, permissions, events. شامل JSON config handling و validation.

**`ticketing/forms/README_TICKETS.md`**
مستندسازی TicketForm و TicketCreateForm. شامل queryset filtering و status/assigned_to removal در create mode.

#### Utils

**`ticketing/utils/README_CODES.md`**
مستندسازی توابع code generation برای ticketing: generate_sequential_code, generate_template_code, generate_ticket_code. شامل date-based codes با فرمت TMP-YYYYMMDD-XXXXXX و TKT-YYYYMMDD-XXXXXX.

---

### Shared Module

#### Views

**`shared/views/README_USERS.md`**
مستندسازی 4 کلاس view برای مدیریت Users: List, Create, Update, Delete. شامل UserCompanyAccess formset و atomic transactions.

**`shared/views/README_COMPANIES.md`**
مستندسازی 4 کلاس view برای مدیریت Companies: List, Create, Update, Delete. شامل auto UserCompanyAccess creation.

**`shared/views/README_ACCESS_LEVELS.md`**
مستندسازی 4 کلاس view برای مدیریت Access Levels: List, Create, Update, Delete. شامل AccessLevelPermissionMixin و permissions context.

**`shared/views/README_GROUPS.md`**
مستندسازی 4 کلاس view برای مدیریت Groups: List, Create, Update, Delete. شامل Django Group integration و prefetching.

**`shared/views/README_COMPANY_UNITS.md`**
مستندسازی 4 کلاس view برای مدیریت Company Units: List, Create, Update, Delete. شامل company filtering و parent unit validation.

**`shared/views/README_AUTH.md`**
مستندسازی 3 function-based view: set_active_company, custom_login, mark_notification_read. شامل session management و redirection logic.

**`shared/views/README_SMTP_SERVER.md`**
مستندسازی 4 کلاس view برای مدیریت SMTP Servers: List, Create, Update, Delete. شامل password handling و TLS/SSL validation.

**`shared/views/README_BASE.md`**
مستندسازی base classes و mixins برای shared views. شامل common functionality و permission checks.

#### Forms

**`shared/forms/README_USERS.md`**
مستندسازی UserBaseForm, UserCreateForm, UserUpdateForm, UserCompanyAccessForm, UserCompanyAccessFormSet. شامل password handling و primary company validation.

**`shared/forms/README_COMPANIES.md`**
مستندسازی CompanyForm و CompanyUnitForm. شامل company details و company unit hierarchy validation.

**`shared/forms/README_ACCESS_LEVELS.md`**
مستندسازی AccessLevelForm. شامل auto-generated code و read-only code field در edit mode.

**`shared/forms/README_GROUPS.md`**
مستندسازی GroupForm. شامل GroupProfile integration و access levels M2M management.

**`shared/forms/README_SMTP_SERVER.md`**
مستندسازی SMTPServerForm. شامل SMTP configuration fields، password handling (optional on update)، و TLS/SSL validation.

#### Utils

**`shared/utils/README_PERMISSIONS.md`**
مستندسازی FeaturePermissionState dataclass و 5 function برای permission resolution: _feature_key, _collect_access_level_ids_for_user, _resolve_feature_permissions, get_user_feature_permissions, has_feature_permission. شامل company/group-based access و superuser bypass.

**`shared/utils/README_MODULES.md`**
مستندسازی توابع برای بررسی نصب بودن ماژول‌های اختیاری: is_production_installed, is_qc_installed, get_work_line_model, get_person_model. شامل lazy import و error handling.

**`shared/utils/README_EMAIL.md`**
مستندسازی توابع برای ارسال ایمیل: get_active_smtp_server, send_email_notification, send_notification_email. شامل SMTP configuration، HTML email support، و error handling.

#### Template Tags

**`shared/templatetags/README_ACCESS_TAGS.md`**
مستندسازی feature_allowed filter برای بررسی مجوزهای دسترسی در templates. شامل feature code و action parsing.

**`shared/templatetags/README_JSON_FILTERS.md`**
مستندسازی to_json filter برای تبدیل Python objects به JSON string. شامل UTF-8 support و error handling.

#### Context Processors

**`shared/README_CONTEXT_PROCESSORS.md`**
مستندسازی active_company context processor که active_company, user_companies, user_feature_permissions, notifications را به context اضافه می‌کند. شامل session management و email notifications.

---

### UI Module

**`ui/README.md`**
مستندسازی کلی UI module شامل DashboardView, templates, navigation, multi-company integration, i18n support. شامل base.html و sidebar structure.

**`ui/README_CONTEXT_PROCESSORS.md`**
مستندسازی active_module context processor که active_module را از query string می‌گیرد. شامل navigation highlighting و future enhancements.

---

### Accounting Module

#### Views

**`accounting/README_VIEWS.md`**
مستندسازی 12 کلاس view برای ماژول حسابداری: Dashboard, General Ledger, Subsidiary Ledger, Detail Ledger, Accounting Documents (Entry/Exit), Treasury (Expense/Income), Payroll (Document, Decrees, Decree Groups, Decree Subgroups). شامل FeaturePermissionRequiredMixin و placeholder views.

---

### Sales Module

#### Views

**`sales/README_VIEWS.md`**
مستندسازی 2 کلاس view برای ماژول فروش: Dashboard و Sales Invoice Create. شامل FeaturePermissionRequiredMixin و placeholder views.

---

### Human Resources (HR) Module

#### Views

**`hr/README_VIEWS.md`**
مستندسازی 12 کلاس view برای ماژول منابع انسانی: Dashboard, Personnel (Create, Decree Assignment, Form, Form Groups, Form Subgroups), Requests (Leave, Sick Leave, Loan), Loans (Management, Scheduling, Savings Fund). شامل FeaturePermissionRequiredMixin و placeholder views.

---

### Office Automation Module

#### Views

**`office_automation/README_VIEWS.md`**
مستندسازی 7 کلاس view برای ماژول اتوماسیون اداری: Dashboard, Inbox (Incoming Letters, Write Letter, Fill Form), Processes (Engine, Form Connection), Forms (Builder). شامل FeaturePermissionRequiredMixin و placeholder views.

---

### Transportation Module

#### Views

**`transportation/README_VIEWS.md`**
مستندسازی 1 کلاس view برای ماژول حمل و نقل: Dashboard. شامل FeaturePermissionRequiredMixin و placeholder view.

---

### Procurement Module

#### Views

**`procurement/README_VIEWS.md`**
مستندسازی 4 کلاس view برای ماژول تدارکات: Dashboard, Purchases, Buyers (List, Create, Assignment). شامل FeaturePermissionRequiredMixin و placeholder views.

---

## 📊 آمار کلی

- **جمع کل فایل‌های README**: 120 فایل
- **Root/Docs**: 3 فایل (README.md, DOCUMENTATION_STRUCTURE.md, DOCUMENTATION_STATUS.md, docs/README.md, docs/ENTITY_REFERENCE_SYSTEM.md, docs/MIGRATIONS_README.md)
- **Module Main**: 13 فایل (README.md برای هر ماژول + README_FORMS.md, README_BALANCE.md, README_BOM.md)
- **Views**: 42 فایل
- **Forms**: 24 فایل
- **Utils**: 6 فایل
- **Services**: 1 فایل
- **Template Tags**: 3 فایل
- **Context Processors**: 2 فایل
- **Management Commands**: 1 فایل
- **Migrations**: 5 فایل README (هر ماژول)
- **Templates**: 1 فایل (templates/inventory/README.md)
- **Other**: 19 فایل (README.md در پوشه‌های مختلف)

**ماژول‌های جدید:**
- Accounting: 1 فایل README (README_VIEWS.md)
- Sales: 1 فایل README (README_VIEWS.md)
- HR: 1 فایل README (README_VIEWS.md)
- Office Automation: 1 فایل README (README_VIEWS.md)
- Transportation: 1 فایل README (README_VIEWS.md)
- Procurement: 1 فایل README (README_VIEWS.md)

---

## 🔍 نحوه استفاده

برای پیدا کردن مستندسازی یک فایل:

1. **Views**: `{module}/views/README_{FILENAME}.md`
2. **Forms**: `{module}/forms/README_{FILENAME}.md`
3. **Utils**: `{module}/utils/README_{FILENAME}.md`
4. **Services**: `{module}/services/README_{FILENAME}.md`
5. **Template Tags**: `{module}/templatetags/README_{FILENAME}.md`
6. **Context Processors**: `{module}/README_CONTEXT_PROCESSORS.md` یا `ui/README_CONTEXT_PROCESSORS.md`
7. **Management Commands**: `{module}/management/commands/README_{COMMAND}.md`

---

## 📝 استاندارد نام‌گذاری

- فایل‌های README با فرمت `README_{FILENAME}.md` نام‌گذاری می‌شوند
- برای فایل‌های چند کلمه‌ای، از underscore استفاده می‌شود (مثل `README_MASTER_DATA.md`)
- برای base classes، از `README_BASE.md` استفاده می‌شود
- برای context processors، از `README_CONTEXT_PROCESSORS.md` استفاده می‌شود

---

## ✅ وضعیت

**تمام فایل‌های مهم پروژه مستندسازی شده‌اند.**

برای جزئیات بیشتر، به `DOCUMENTATION_STATUS.md` مراجعه کنید.

