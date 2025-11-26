# وضعیت مستندسازی پروژه (Documentation Status)

## ⚠️ تذکر بسیار مهم

**از این به بعد، هر فایل جدیدی که در برنامه ساخته می‌شود، باید یک فایل README.md کامل داشته باشد که شامل موارد زیر باشد:**

1. **هدف فایل**: توضیح کلی از اینکه فایل چه کاری انجام می‌دهد
2. **تمام کلاس‌ها**: لیست تمام کلاس‌های موجود در فایل
3. **تمام متدها**: برای هر کلاس، تمام متدها با جزئیات کامل:
   - نام متد
   - پارامترهای ورودی (با نوع و توضیح)
   - مقدار بازگشتی (با نوع و توضیح)
   - منطق و نحوه کارکرد
4. **تمام فیلدها**: برای forms، تمام فیلدها با:
   - نوع فیلد
   - widget
   - label
   - help_text (در صورت وجود)
   - validation rules
5. **وابستگی‌ها**: تمام import ها و وابستگی‌های فایل
6. **استفاده در پروژه**: نحوه استفاده از فایل در پروژه
7. **نکات مهم**: نکات و الگوهای خاص

**این مستندسازی باید به صورت کامل و جامع باشد و هیچ جزئیاتی از قلم نیفتد.**

---

## خلاصه کارهای انجام شده

در این پروژه، یک سیستم مستندسازی کامل برای تمام فایل‌های مهم برنامه ایجاد شده است. هر فایل README شامل:

- توضیح کامل هدف فایل
- لیست تمام کلاس‌ها و توابع
- جزئیات کامل هر متد (پارامترها، return values، منطق)
- جزئیات کامل هر فیلد (برای forms)
- وابستگی‌ها و نحوه استفاده
- نکات مهم و الگوهای خاص

---

## فایل‌های مستندسازی شده (کامل)

### Views

#### ✅ `inventory/views/master_data.py`
- **فایل README**: `inventory/views/README_MASTER_DATA.md`
- **وضعیت**: ✅ کامل
- **توضیحات**: 
  - تمام 27 کلاس view مستندسازی شده
  - تمام متدها با پارامترها و return values
  - تمام context variables
  - تمام URL patterns
  - منطق کامل هر متد

**کلاس‌های مستندسازی شده**:
- `ItemTypeListView`, `ItemTypeCreateView`, `ItemTypeUpdateView`, `ItemTypeDeleteView`
- `ItemCategoryListView`, `ItemCategoryCreateView`, `ItemCategoryUpdateView`, `ItemCategoryDeleteView`
- `ItemSubcategoryListView`, `ItemSubcategoryCreateView`, `ItemSubcategoryUpdateView`, `ItemSubcategoryDeleteView`
- `ItemListView`, `ItemSerialListView`, `ItemCreateView`, `ItemUpdateView`, `ItemDeleteView`
- `WarehouseListView`, `WarehouseCreateView`, `WarehouseUpdateView`, `WarehouseDeleteView`
- `SupplierCategoryListView`, `SupplierCategoryCreateView`, `SupplierCategoryUpdateView`, `SupplierCategoryDeleteView`
- `SupplierListView`, `SupplierCreateView`, `SupplierUpdateView`, `SupplierDeleteView`

---

### Forms

#### ✅ `inventory/forms/master_data.py`
- **فایل README**: `inventory/forms/README_MASTER_DATA.md`
- **وضعیت**: ✅ کامل
- **توضیحات**:
  - تمام helper classes مستندسازی شده (`IntegerCheckboxField`, `IntegerCheckboxInput`)
  - تمام form classes با جزئیات کامل
  - تمام فیلدها با نوع، widget، label
  - تمام متدها (`__init__`, `clean`, etc.)
  - FormSet factory documentation

**کلاس‌های مستندسازی شده**:
- `IntegerCheckboxField` (تمام متدها)
- `IntegerCheckboxInput` (تمام متدها)
- `ItemTypeForm`
- `ItemCategoryForm`
- `ItemSubcategoryForm`
- `WarehouseForm`
- `SupplierForm`
- `SupplierCategoryForm` (با تمام متدهای پیچیده)
- `ItemForm` (با تمام فیلدها و validation)
- `ItemUnitForm`
- `ItemUnitFormSet`

#### ✅ `inventory/forms/receipt.py`
- **فایل README**: `inventory/forms/README_RECEIPT.md`
- **وضعیت**: ✅ کامل
- **توضیحات**:
  - تمام header forms مستندسازی شده (`ReceiptTemporaryForm`, `ReceiptPermanentForm`, `ReceiptConsignmentForm`)
  - تمام line forms با جزئیات کامل (`ReceiptLineBaseForm`, `ReceiptPermanentLineForm`, `ReceiptConsignmentLineForm`, `ReceiptTemporaryLineForm`)
  - تمام متدها با پارامترها و return values
  - تمام فیلدها با نوع، widget، label
  - Formsets documentation
  - Unit conversion logic
  - Price normalization logic
  - Item filtering and search support

**کلاس‌های مستندسازی شده**:
- `ReceiptTemporaryForm` (تمام متدها)
- `ReceiptPermanentForm` (تمام متدها)
- `ReceiptConsignmentForm` (تمام متدها)
- `ReceiptLineBaseForm` (تمام helper methods)
- `ReceiptPermanentLineForm`
- `ReceiptConsignmentLineForm`
- `ReceiptTemporaryLineForm`
- `ReceiptPermanentLineFormSet`
- `ReceiptConsignmentLineFormSet`
- `ReceiptTemporaryLineFormSet`

#### ✅ `inventory/forms/issue.py`
- **فایل README**: `inventory/forms/README_ISSUE.md`
- **وضعیت**: ✅ کامل
- **توضیحات**:
  - تمام header forms مستندسازی شده (`IssuePermanentForm`, `IssueConsumptionForm`, `IssueConsignmentForm`)
  - تمام line forms با جزئیات کامل (`IssueLineBaseForm`, `IssuePermanentLineForm`, `IssueConsumptionLineForm`, `IssueConsignmentLineForm`)
  - Serial assignment form (`IssueLineSerialAssignmentForm`)
  - تمام متدها با پارامترها و return values
  - Inventory balance validation
  - Destination handling logic
  - Production module integration
  - Item filtering and search support

**کلاس‌های مستندسازی شده**:
- `IssuePermanentForm` (تمام متدها)
- `IssueConsumptionForm` (تمام متدها)
- `IssueConsignmentForm` (تمام متدها)
- `IssueLineSerialAssignmentForm` (تمام متدها)
- `IssueLineBaseForm` (تمام helper methods)
- `IssuePermanentLineForm` (با destination handling)
- `IssueConsumptionLineForm` (با destination type choice)
- `IssueConsignmentLineForm` (با consignment receipt)
- `IssuePermanentLineFormSet`
- `IssueConsumptionLineFormSet`
- `IssueConsignmentLineFormSet`

#### ✅ `inventory/forms/request.py`
- **فایل README**: `inventory/forms/README_REQUEST.md`
- **وضعیت**: ✅ کامل
- **توضیحات**:
  - تمام forms مستندسازی شده (`PurchaseRequestForm`, `PurchaseRequestLineForm`, `WarehouseRequestForm`, `WarehouseRequestLineForm`, `WarehouseRequestLineFormSet`)
  - تمام متدها با پارامترها و return values
  - تمام فیلدها با نوع، widget، label
  - Item filtering and search support (بر اساس `request.GET`)
  - Approver validation
  - Unit conversion logic

**کلاس‌های مستندسازی شده**:
- `PurchaseRequestForm` (تمام متدها)
- `PurchaseRequestLineForm` (با item filtering)
- `PurchaseRequestLineFormSet`
- `WarehouseRequestForm` (header-only form)
- `WarehouseRequestLineForm` (تمام متدها با item filtering و warehouse validation)
- `WarehouseRequestLineFormSet` (formset factory)

---

## فایل‌های مستندسازی شده (کامل)

### Views

#### ✅ `inventory/views/receipts.py`
- **فایل README**: `inventory/views/README_RECEIPTS.md`
- **وضعیت**: ✅ کامل
- **توضیحات**:
  - تمام 27 کلاس view مستندسازی شده
  - DocumentDeleteViewBase و ReceiptFormMixin با تمام متدها
  - 15 Receipt Views (5 برای هر نوع: Temporary, Permanent, Consignment)
  - 3 Create from Purchase Request Views
  - 6 Serial Assignment Views (2 base + 4 subclass)
  - تمام متدها با پارامترها و return values
  - تمام context variables
  - Fieldsets documentation
  - Lock mechanism documentation
  - Session management documentation
- Serial assignment documentation
- Item filtering and search documentation

**کلاس‌های مستندسازی شده**:
- Base Classes: `DocumentDeleteViewBase`, `ReceiptFormMixin`
- Temporary Receipt Views: `ReceiptTemporaryListView`, `ReceiptTemporaryCreateView`, `ReceiptTemporaryUpdateView`, `ReceiptTemporaryDeleteView`, `ReceiptTemporaryLockView`, `ReceiptTemporarySendToQCView`, `ReceiptTemporaryCreateFromPurchaseRequestView`
- Permanent Receipt Views: `ReceiptPermanentListView`, `ReceiptPermanentCreateView`, `ReceiptPermanentUpdateView`, `ReceiptPermanentDeleteView`, `ReceiptPermanentLockView`, `ReceiptPermanentCreateFromPurchaseRequestView`
- Consignment Receipt Views: `ReceiptConsignmentListView`, `ReceiptConsignmentCreateView`, `ReceiptConsignmentUpdateView`, `ReceiptConsignmentDeleteView`, `ReceiptConsignmentLockView`, `ReceiptConsignmentCreateFromPurchaseRequestView`
- Serial Assignment Views: `ReceiptSerialAssignmentBaseView`, `ReceiptPermanentSerialAssignmentView`, `ReceiptConsignmentSerialAssignmentView`, `ReceiptLineSerialAssignmentBaseView`, `ReceiptPermanentLineSerialAssignmentView`, `ReceiptConsignmentLineSerialAssignmentView`

---

## فایل‌های نیازمند مستندسازی (باقی‌مانده)

### Views

#### ✅ `inventory/views/issues.py`
- **فایل README**: `inventory/views/README_ISSUES.md`
- **وضعیت**: ✅ کامل
- **توضیحات**:
  - تمام 18 کلاس view مستندسازی شده
  - تمام متدها با پارامترها و return values
  - تمام context variables
  - تمام URL patterns
  - منطق کامل هر متد
  - Serial management documentation
  - Item filtering and search support

**کلاس‌های مستندسازی شده**:
- Permanent Issue Views: `IssuePermanentListView`, `IssuePermanentCreateView`, `IssuePermanentUpdateView`, `IssuePermanentDeleteView`, `IssuePermanentLockView`
- Consumption Issue Views: `IssueConsumptionListView`, `IssueConsumptionCreateView`, `IssueConsumptionUpdateView`, `IssueConsumptionDeleteView`, `IssueConsumptionLockView`
- Consignment Issue Views: `IssueConsignmentListView`, `IssueConsignmentCreateView`, `IssueConsignmentUpdateView`, `IssueConsignmentDeleteView`, `IssueConsignmentLockView`
- Serial Assignment Views: `IssueLineSerialAssignmentBaseView`, `IssuePermanentLineSerialAssignmentView`, `IssueConsumptionLineSerialAssignmentView`, `IssueConsignmentLineSerialAssignmentView`

#### ✅ `inventory/views/requests.py`
- **فایل README**: `inventory/views/README_REQUESTS.md`
- **وضعیت**: ✅ کامل
- **توضیحات**:
  - تمام 14 کلاس view مستندسازی شده
  - PurchaseRequestFormMixin و WarehouseRequestFormMixin با تمام متدها
  - 5 Purchase Request Views (List, Create, Update, Approve)
  - 4 Warehouse Request Views (List, Create با formset, Update با formset, Approve)
  - 4 Create Receipt from Purchase Request Views (1 base + 3 subclasses)
  - تمام متدها با پارامترها و return values
  - تمام context variables
  - Legacy fields documentation
  - Session management documentation
  - Item filtering and search documentation

**کلاس‌های مستندسازی شده**:
- `PurchaseRequestFormMixin` (base mixin)
- `WarehouseRequestFormMixin` (base mixin)
- Purchase Request Views: `PurchaseRequestListView`, `PurchaseRequestCreateView`, `PurchaseRequestUpdateView`, `PurchaseRequestApproveView`
- Warehouse Request Views: `WarehouseRequestListView`, `WarehouseRequestCreateView` (با formset), `WarehouseRequestUpdateView` (با formset), `WarehouseRequestApproveView`
- Create Receipt Views: `CreateReceiptFromPurchaseRequestView` (base), `CreateTemporaryReceiptFromPurchaseRequestView`, `CreatePermanentReceiptFromPurchaseRequestView`, `CreateConsignmentReceiptFromPurchaseRequestView`

#### ✅ `inventory/views/stocktaking.py`
- **فایل README**: `inventory/views/README_STOCKTAKING.md`
- **وضعیت**: ✅ کامل
- **توضیحات**:
  - تمام 16 کلاس view مستندسازی شده
  - StocktakingFormMixin با تمام متدها
  - 3 نوع document (Deficit, Surplus, Record) با 5 view برای هر کدام
  - تمام متدها با پارامترها و return values
  - تمام context variables
  - Fieldsets documentation
  - Lock mechanism documentation

**کلاس‌های مستندسازی شده**:
- `StocktakingFormMixin` (base mixin)
- Deficit Views: `StocktakingDeficitListView`, `StocktakingDeficitCreateView`, `StocktakingDeficitUpdateView`, `StocktakingDeficitDeleteView`, `StocktakingDeficitLockView`
- Surplus Views: `StocktakingSurplusListView`, `StocktakingSurplusCreateView`, `StocktakingSurplusUpdateView`, `StocktakingSurplusDeleteView`, `StocktakingSurplusLockView`
- Record Views: `StocktakingRecordListView`, `StocktakingRecordCreateView`, `StocktakingRecordUpdateView`, `StocktakingRecordDeleteView`, `StocktakingRecordLockView`

#### ✅ `inventory/views/balance.py`
- **فایل README**: `inventory/views/README_BALANCE.md`
- **وضعیت**: ✅ کامل
- **توضیحات**:
  - تمام 3 view class مستندسازی شده
  - InventoryBalanceView با فیلترها و محاسبه موجودی
  - InventoryBalanceDetailsView با تاریخچه تراکنش‌ها
  - InventoryBalanceAPIView با JSON API endpoint
  - تمام متدها با پارامترها و return values
  - Date parsing (Gregorian و Jalali)
  - Transaction types documentation

**کلاس‌های مستندسازی شده**:
- `InventoryBalanceView` - نمایش موجودی با فیلترها
- `InventoryBalanceDetailsView` - جزئیات تراکنش‌های یک کالا
- `InventoryBalanceAPIView` - API endpoint برای محاسبه موجودی

#### ✅ `inventory/views/api.py`
- **فایل README**: `inventory/views/README_API.md`
- **وضعیت**: ✅ کامل
- **توضیحات**:
  - تمام 10 function-based view مستندسازی شده
  - تمام endpoints با query parameters و response format
  - Error handling documentation
  - Authentication و authorization
  - Company filtering

**Function-based Views مستندسازی شده**:
- `get_item_allowed_units` - دریافت واحدهای مجاز
- `get_filtered_categories` - دریافت دسته‌بندی‌های فیلتر شده
- `get_filtered_subcategories` - دریافت زیردسته‌بندی‌های فیلتر شده
- `get_filtered_items` - دریافت کالاهای فیلتر شده
- `get_item_units` - دریافت واحدهای یک کالا
- `get_item_allowed_warehouses` - دریافت انبارهای مجاز
- `get_temporary_receipt_data` - دریافت داده‌های receipt موقت
- `get_item_available_serials` - دریافت سریال‌های موجود
- `update_serial_secondary_code` - به‌روزرسانی کد ثانویه سریال
- `get_warehouse_work_lines` - دریافت خطوط کار یک انبار

#### ✅ `inventory/views/base.py`
- **فایل README**: `inventory/views/README_BASE.md`
- **وضعیت**: ✅ کامل
- **توضیحات**:
  - تمام 5 کلاس مستندسازی شده
  - InventoryBaseView با company filtering و permission helpers
  - DocumentLockProtectedMixin با lock protection
  - DocumentLockView با lock mechanism
  - LineFormsetMixin با formset management
  - ItemUnitFormsetMixin با unit formset management
  - تمام متدها با پارامترها و return values
  - Serial management documentation

**کلاس‌های مستندسازی شده**:
- `InventoryBaseView` - Base view با context مشترک
- `DocumentLockProtectedMixin` - محافظت از سندهای قفل شده
- `DocumentLockView` - View برای lock کردن سندها
- `LineFormsetMixin` - Mixin برای مدیریت line formsets
- `ItemUnitFormsetMixin` - Mixin برای مدیریت item unit formsets

#### ✅ `inventory/views/item_import.py`
- **فایل README**: `inventory/views/README_ITEM_IMPORT.md`
- **وضعیت**: ✅ کامل
- **توضیحات**:
  - تمام 2 view class مستندسازی شده
  - ItemExcelTemplateDownloadView با Excel generation logic
  - ItemExcelImportView با parsing, validation, و creation logic
  - تمام helper methods مستندسازی شده
  - Excel columns documentation
  - Error handling documentation

**کلاس‌های مستندسازی شده**:
- `ItemExcelTemplateDownloadView` - دانلود قالب Excel
- `ItemExcelImportView` - Import از Excel با تمام helper methods

#### ✅ `inventory/views/create_issue_from_warehouse_request.py`
- **فایل README**: `inventory/views/README_CREATE_ISSUE_FROM_WAREHOUSE_REQUEST.md`
- **وضعیت**: ✅ کامل
- **توضیحات**:
  - تمام 4 view class مستندسازی شده
  - CreateIssueFromWarehouseRequestView (base) با تمام متدها
  - 3 subclass برای permanent, consumption, consignment
  - Session management documentation
  - Quantity validation documentation

**کلاس‌های مستندسازی شده**:
- `CreateIssueFromWarehouseRequestView` (base)
- `CreatePermanentIssueFromWarehouseRequestView`
- `CreateConsumptionIssueFromWarehouseRequestView`
- `CreateConsignmentIssueFromWarehouseRequestView`

#### ✅ `inventory/views/issues_from_warehouse_request.py`
- **فایل README**: `inventory/views/README_ISSUES_FROM_WAREHOUSE_REQUEST.md`
- **وضعیت**: ✅ کامل
- **توضیحات**:
  - تمام 3 view class مستندسازی شده
  - IssuePermanentCreateFromWarehouseRequestView
  - IssueConsumptionCreateFromWarehouseRequestView
  - IssueConsignmentCreateFromWarehouseRequestView
  - تمام متدها با پارامترها و return values
  - Session data usage documentation
  - Formset handling documentation

**کلاس‌های مستندسازی شده**:
- `IssuePermanentCreateFromWarehouseRequestView`
- `IssueConsumptionCreateFromWarehouseRequestView`
- `IssueConsignmentCreateFromWarehouseRequestView`

---

### Forms

#### ✅ `inventory/forms/receipt.py`
- **وضعیت**: ✅ کامل (به بخش بالا مراجعه کنید)

#### ✅ `inventory/forms/issue.py`
- **وضعیت**: ✅ کامل (به بخش بالا مراجعه کنید)

#### ✅ `inventory/forms/request.py`
- **وضعیت**: ✅ کامل (به بخش بالا مراجعه کنید)

#### ✅ `inventory/forms/stocktaking.py`
- **فایل README**: `inventory/forms/README_STOCKTAKING.md`
- **وضعیت**: ✅ کامل
- **توضیحات**:
  - تمام 3 form class مستندسازی شده
  - تمام فیلدها با نوع، widget، label
  - تمام متدها با منطق کامل
  - Document code generation
  - Approval workflow documentation
  - Quantity calculation logic

**کلاس‌های مستندسازی شده**:
- `StocktakingDeficitForm` (با quantity calculation)
- `StocktakingSurplusForm` (با quantity calculation)
- `StocktakingRecordForm` (با approval workflow)

#### ✅ `inventory/forms/base.py`
- **فایل README**: `inventory/forms/README_BASE.md`
- **وضعیت**: ✅ کامل
- **توضیحات**:
  - Constants (UNIT_CHOICES)
  - Helper functions (get_feature_approvers, generate_document_code, get_purchase_request_approvers)
  - Base form classes (ReceiptBaseForm, IssueBaseForm, StocktakingBaseForm)
  - Base formset class (BaseLineFormSet)
  - تمام متدها با جزئیات کامل
  - Unit conversion logic
  - Company filtering logic

**کلاس‌های مستندسازی شده**:
- Helper Functions: `get_feature_approvers`, `generate_document_code`, `get_purchase_request_approvers`
- Base Forms: `ReceiptBaseForm`, `IssueBaseForm`, `StocktakingBaseForm`
- Base Formset: `BaseLineFormSet`

---

### Other Modules

#### ✅ `production/views/*.py`
- **وضعیت**: ✅ کامل (9 فایل README جداگانه)
- **فایل‌های README موجود**:
  - ✅ `production/views/README_BOM.md` - کامل
  - ✅ `production/views/README_PROCESS.md` - کامل
  - ✅ `production/views/README_PRODUCT_ORDER.md` - کامل
  - ✅ `production/views/README_MACHINE.md` - کامل
  - ✅ `production/views/README_WORK_LINE.md` - کامل
  - ✅ `production/views/README_PERSONNEL.md` - کامل
  - ✅ `production/views/README_PERFORMANCE_RECORD.md` - کامل
  - ✅ `production/views/README_TRANSFER_TO_LINE.md` - کامل
  - ✅ `production/views/README_PLACEHOLDERS.md` - کامل
- **فایل README کلی**: `production/views/README.md` (نیاز به بررسی و تکمیل)

#### ✅ `production/forms/*.py`
- **وضعیت**: ✅ کامل (8 فایل README جداگانه)
- **فایل‌های README موجود**:
  - ✅ `production/forms/README_BOM.md` - کامل
  - ✅ `production/forms/README_PROCESS.md` - کامل
  - ✅ `production/forms/README_PRODUCT_ORDER.md` - کامل
  - ✅ `production/forms/README_WORK_LINE.md` - کامل
  - ✅ `production/forms/README_MACHINE.md` - کامل
  - ✅ `production/forms/README_PERSON.md` - کامل
  - ✅ `production/forms/README_TRANSFER_TO_LINE.md` - کامل
  - ✅ `production/forms/README_PERFORMANCE_RECORD.md` - کامل
- **فایل README کلی**: `production/forms/README.md` (نیاز به بررسی و تکمیل)

#### ✅ `qc/views/inspections.py`
- **فایل README**: `qc/views/README_INSPECTIONS.md`
- **وضعیت**: ✅ کامل
- **توضیحات**:
  - تمام 3 کلاس view مستندسازی شده
  - TemporaryReceiptQCListView با queryset filtering
  - TemporaryReceiptQCApproveView با approval workflow
  - TemporaryReceiptQCRejectView با rejection workflow
  - تمام متدها با پارامترها و return values
  - Transaction safety documentation
  - Lock mechanism documentation

**کلاس‌های مستندسازی شده**:
- `TemporaryReceiptQCListView` - فهرست رسیدهای در انتظار بازرسی
- `TemporaryReceiptQCApproveView` - تایید بازرسی
- `TemporaryReceiptQCRejectView` - رد بازرسی

#### ✅ `qc/views/base.py`
- **فایل README**: `qc/views/README_BASE.md`
- **وضعیت**: ✅ کامل (موجود از قبل)

#### ✅ `ticketing/views/*.py`
- **وضعیت**: ✅ کامل (7 فایل README جداگانه)
- **فایل‌های README موجود**:
  - ✅ `ticketing/views/README_BASE.md` - کامل (موجود از قبل)
  - ✅ `ticketing/views/README_CATEGORIES.md` - کامل
  - ✅ `ticketing/views/README_SUBCATEGORIES.md` - کامل
  - ✅ `ticketing/views/README_TEMPLATES.md` - کامل
  - ✅ `ticketing/views/README_TICKETS.md` - کامل
  - ✅ `ticketing/views/README_DEBUG.md` - کامل
  - ✅ `ticketing/views/README_PLACEHOLDERS.md` - کامل
- **فایل README کلی**: `ticketing/views/README.md` (نیاز به بررسی و تکمیل)

#### ✅ `ticketing/forms/*.py`
- **وضعیت**: ✅ کامل (4 فایل README جداگانه)
- **فایل‌های README موجود**:
  - ✅ `ticketing/forms/README_BASE.md` - کامل
  - ✅ `ticketing/forms/README_CATEGORIES.md` - کامل
  - ✅ `ticketing/forms/README_TEMPLATES.md` - کامل
  - ✅ `ticketing/forms/README_TICKETS.md` - کامل
- **فایل README کلی**: `ticketing/forms/README.md` (نیاز به بررسی و تکمیل)

#### ✅ `shared/views/users.py`
- **فایل README**: `shared/views/README_USERS.md`
- **وضعیت**: ✅ کامل
- **توضیحات**:
  - تمام 4 کلاس view مستندسازی شده
  - UserListView با search و status filtering
  - UserCreateView با UserCompanyAccess formset
  - UserUpdateView با UserCompanyAccess formset
  - UserDeleteView
  - تمام متدها با پارامترها و return values
  - Transaction safety documentation
  - Formset management documentation

**کلاس‌های مستندسازی شده**:
- `UserListView` - فهرست کاربران
- `UserCreateView` - ایجاد کاربر
- `UserUpdateView` - ویرایش کاربر
- `UserDeleteView` - حذف کاربر

#### ✅ `shared/views/companies.py`
- **فایل README**: `shared/views/README_COMPANIES.md`
- **وضعیت**: ✅ کامل
- **توضیحات**:
  - تمام 4 کلاس view مستندسازی شده
  - CompanyListView با user access filtering
  - CompanyCreateView با auto UserCompanyAccess creation
  - CompanyUpdateView
  - CompanyDeleteView
  - تمام متدها با پارامترها و return values
  - Auto access creation documentation

**کلاس‌های مستندسازی شده**:
- `CompanyListView` - فهرست شرکت‌ها (بر اساس دسترسی کاربر)
- `CompanyCreateView` - ایجاد شرکت (با auto access creation)
- `CompanyUpdateView` - ویرایش شرکت
- `CompanyDeleteView` - حذف شرکت

#### ✅ `shared/views/base.py`
- **فایل README**: `shared/views/README_BASE.md`
- **وضعیت**: ✅ کامل (موجود از قبل)

#### ✅ `shared/views/access_levels.py`
- **فایل README**: `shared/views/README_ACCESS_LEVELS.md`
- **وضعیت**: ✅ کامل
- **توضیحات**:
  - تمام 4 کلاس view مستندسازی شده
  - AccessLevelListView با search و status filtering
  - AccessLevelCreateView با AccessLevelPermissionMixin و permission management
  - AccessLevelUpdateView با permission management
  - AccessLevelDeleteView
  - تمام متدها با پارامترها و return values
  - AccessLevelPermissionMixin documentation (_prepare_feature_context, _save_permissions)

**کلاس‌های مستندسازی شده**:
- `AccessLevelListView` - فهرست access levels
- `AccessLevelCreateView` - ایجاد access level (با permission management)
- `AccessLevelUpdateView` - ویرایش access level (با permission management)
- `AccessLevelDeleteView` - حذف access level

#### ✅ `shared/views/groups.py`
- **فایل README**: `shared/views/README_GROUPS.md`
- **وضعیت**: ✅ کامل
- **توضیحات**:
  - تمام 4 کلاس view مستندسازی شده
  - GroupListView با search و status filtering (از GroupProfile)
  - GroupCreateView
  - GroupUpdateView
  - GroupDeleteView
  - تمام متدها با پارامترها و return values
  - Django Group model integration

**کلاس‌های مستندسازی شده**:
- `GroupListView` - فهرست groups
- `GroupCreateView` - ایجاد group
- `GroupUpdateView` - ویرایش group
- `GroupDeleteView` - حذف group

#### ✅ `shared/views/company_units.py`
- **فایل README**: `shared/views/README_COMPANY_UNITS.md`
- **وضعیت**: ✅ کامل
- **توضیحات**:
  - تمام 4 کلاس view مستندسازی شده
  - CompanyUnitListView با company filtering و search
  - CompanyUnitCreateView با auto company_id setting
  - CompanyUnitUpdateView
  - CompanyUnitDeleteView
  - تمام متدها با پارامترها و return values
  - Company scoping documentation

**کلاس‌های مستندسازی شده**:
- `CompanyUnitListView` - فهرست واحدهای سازمانی (بر اساس شرکت فعال)
- `CompanyUnitCreateView` - ایجاد واحد سازمانی
- `CompanyUnitUpdateView` - ویرایش واحد سازمانی
- `CompanyUnitDeleteView` - حذف واحد سازمانی

#### ✅ `shared/views/auth.py`
- **فایل README**: `shared/views/README_AUTH.md`
- **وضعیت**: ✅ کامل
- **توضیحات**:
  - تمام 3 function-based view مستندسازی شده
  - set_active_company با access verification
  - custom_login با authentication
  - mark_notification_read با session management
  - تمام پارامترها و return values
  - Session management documentation

**Function-based Views مستندسازی شده**:
- `set_active_company` - تنظیم شرکت فعال در session
- `custom_login` - صفحه login سفارشی
- `mark_notification_read` - علامت‌گذاری notification به عنوان خوانده شده

#### ✅ `shared/views/smtp_server.py`
- **فایل README**: `shared/views/README_SMTP_SERVER.md`
- **وضعیت**: ✅ کامل
- **توضیحات**:
  - تمام 4 کلاس view مستندسازی شده
  - SMTPServerListView
  - SMTPServerCreateView با auto field setting
  - SMTPServerUpdateView با password handling
  - SMTPServerDeleteView
  - تمام متدها با پارامترها و return values
  - Password handling documentation

**کلاس‌های مستندسازی شده**:
- `SMTPServerListView` - فهرست SMTP server configurations
- `SMTPServerCreateView` - ایجاد SMTP server configuration
- `SMTPServerUpdateView` - ویرایش SMTP server configuration (با password handling)
- `SMTPServerDeleteView` - حذف SMTP server configuration

#### ✅ `shared/forms/users.py`
- **فایل README**: `shared/forms/README_USERS.md`
- **وضعیت**: ✅ کامل
- **توضیحات**:
  - تمام 3 form class مستندسازی شده (UserBaseForm, UserCreateForm, UserUpdateForm)
  - UserCompanyAccessForm و BaseUserCompanyAccessFormSet مستندسازی شده
  - UserCompanyAccessFormSet factory مستندسازی شده
  - تمام متدها با پارامترها و return values
  - Groups management documentation
  - Password handling documentation
  - Formset validation documentation

**کلاس‌های مستندسازی شده**:
- `UserBaseForm` - Base form برای user creation/update
- `UserCreateForm` - Form برای ایجاد کاربر (با password)
- `UserUpdateForm` - Form برای ویرایش کاربر (با optional password change)
- `UserCompanyAccessForm` - Form برای company access (در formset)
- `BaseUserCompanyAccessFormSet` - Formset با validation (یک primary company)
- `UserCompanyAccessFormSet` - Formset factory

#### ✅ `shared/forms/companies.py`
- **فایل README**: `shared/forms/README_COMPANIES.md`
- **وضعیت**: ✅ کامل
- **توضیحات**:
  - تمام 2 form class مستندسازی شده
  - CompanyForm با تمام fields
  - CompanyUnitForm با company filtering و parent unit validation
  - تمام متدها با پارامترها و return values
  - Company scoping documentation
  - Hierarchical structure documentation

**کلاس‌های مستندسازی شده**:
- `CompanyForm` - Form برای ایجاد/ویرایش شرکت
- `CompanyUnitForm` - Form برای ایجاد/ویرایش واحد سازمانی (با parent unit validation)

#### ✅ `shared/forms/access_levels.py`
- **فایل README**: `shared/forms/README_ACCESS_LEVELS.md`
- **وضعیت**: ✅ کامل
- **توضیحات**:
  - AccessLevelForm مستندسازی شده
  - Auto-generated code field documentation
  - Read-only code field در edit mode
  - تمام متدها با پارامترها و return values

**کلاس‌های مستندسازی شده**:
- `AccessLevelForm` - Form برای ایجاد/ویرایش access level (با read-only code در edit)

#### ✅ `shared/forms/groups.py`
- **فایل README**: `shared/forms/README_GROUPS.md`
- **وضعیت**: ✅ کامل
- **توضیحات**:
  - GroupForm مستندسازی شده
  - GroupProfile integration documentation
  - Access levels M2M management
  - تمام متدها با پارامترها و return values
  - Save logic documentation

**کلاس‌های مستندسازی شده**:
- `GroupForm` - Form برای ایجاد/ویرایش group (با GroupProfile integration)

#### ✅ `shared/forms/smtp_server.py`
- **فایل README**: `shared/forms/README_SMTP_SERVER.md`
- **وضعیت**: ✅ کامل
- **توضیحات**:
  - SMTPServerForm مستندسازی شده
  - Password handling documentation (optional در update)
  - TLS/SSL validation documentation
  - تمام متدها با پارامترها و return values
  - Help texts documentation

**کلاس‌های مستندسازی شده**:
- `SMTPServerForm` - Form برای ایجاد/ویرایش SMTP server configuration (با TLS/SSL validation)

---

### Utilities

#### ✅ `inventory/utils/codes.py`
- **فایل README**: `inventory/utils/README_CODES.md`
- **وضعیت**: ✅ کامل

#### ✅ `inventory/utils/jalali.py`
- **فایل README**: `inventory/utils/README_JALALI.md`
- **وضعیت**: ✅ کامل

#### ✅ `shared/utils/permissions.py`
- **فایل README**: `shared/utils/README_PERMISSIONS.md`
- **وضعیت**: ✅ کامل
- **توضیحات**:
  - FeaturePermissionState dataclass مستندسازی شده
  - تمام 5 function مستندسازی شده (3 helper + 2 public)
  - _collect_access_level_ids_for_user با company و group access
  - _resolve_feature_permissions با scope priority و legacy support
  - get_user_feature_permissions با superuser bypass
  - has_feature_permission با own scope fallback
  - تمام پارامترها و return values
  - Permission resolution flow documentation

**کلاس‌ها و Functions مستندسازی شده**:
- `FeaturePermissionState` (dataclass)
- `_feature_key` (helper)
- `_collect_access_level_ids_for_user` (helper)
- `_resolve_feature_permissions` (helper)
- `get_user_feature_permissions` (public)
- `has_feature_permission` (public)

#### ✅ `shared/utils/modules.py`
- **فایل README**: `shared/utils/README_MODULES.md`
- **وضعیت**: ✅ کامل

#### ✅ `shared/utils/email.py`
- **فایل README**: `shared/utils/README_EMAIL.md`
- **وضعیت**: ✅ کامل

#### ✅ `ticketing/utils/codes.py`
- **فایل README**: `ticketing/utils/README_CODES.md`
- **وضعیت**: ✅ کامل

---

### Services

#### ✅ `inventory/services/serials.py`
- **فایل README**: `inventory/services/README_SERIALS.md`
- **وضعیت**: ✅ کامل

---

### Template Tags

#### ✅ `inventory/templatetags/jalali_tags.py`
- **فایل README**: `inventory/templatetags/README_JALALI_TAGS.md`
- **وضعیت**: ✅ کامل

#### ✅ `shared/templatetags/access_tags.py`
- **فایل README**: `shared/templatetags/README_ACCESS_TAGS.md`
- **وضعیت**: ✅ کامل

#### ✅ `shared/templatetags/json_filters.py`
- **فایل README**: `shared/templatetags/README_JSON_FILTERS.md`
- **وضعیت**: ✅ کامل

---

### Context Processors

#### ✅ `shared/context_processors.py`
- **فایل README**: `shared/README_CONTEXT_PROCESSORS.md`
- **وضعیت**: ✅ کامل

#### ✅ `ui/context_processors.py`
- **فایل README**: `ui/README_CONTEXT_PROCESSORS.md`
- **وضعیت**: ✅ کامل

---

### Management Commands

#### ✅ `inventory/management/commands/cleanup_test_receipts.py`
- **فایل README**: `inventory/management/commands/README_CLEANUP_TEST_RECEIPTS.md`
- **وضعیت**: ✅ کامل

---

### Migrations

**نکته**: برای migrations، یک فایل README کلی در root پروژه ایجاد می‌شود که تمام migrations تمام ماژول‌ها را پوشش می‌دهد.

#### ✅ `MIGRATIONS_README.md` (در root پروژه)
- **فایل README**: `MIGRATIONS_README.md`
- **وضعیت**: ✅ کامل
- **توضیحات**: فایل README کلی که تمام migration files تمام ماژول‌ها را مستندسازی می‌کند
- **ماژول‌های شامل**:
  - `inventory/migrations/*.py` (~32 migration files)
  - `production/migrations/*.py` (~21 migration files)
  - `qc/migrations/*.py` (~5 migration files)
  - `ticketing/migrations/*.py` (~2 migration files)
  - `shared/migrations/*.py` (~12 migration files)
  - **نکته**: `ui/migrations` migration file ندارد (فقط `__init__.py`)

---

## آمار کلی

### ✅ کامل شده
- **Views**: 36 فایل
  - Inventory: 11 فایل (`master_data.py`, `issues.py`, `stocktaking.py`, `balance.py`, `api.py`, `base.py`, `item_import.py`, `create_issue_from_warehouse_request.py`, `issues_from_warehouse_request.py`, `receipts.py`, `requests.py`)
  - Production: 9 فایل README جداگانه (`bom.py`, `process.py`, `product_order.py`, `machine.py`, `work_line.py`, `personnel.py`, `transfer_to_line.py`, `performance_record.py`, `placeholders.py`)
  - QC: 1 فایل (`inspections.py`)
  - Ticketing: 7 فایل README جداگانه (`base.py`, `categories.py`, `subcategories.py`, `templates.py`, `tickets.py`, `debug.py`, `placeholders.py`)
  - Shared: 8 فایل (`users.py`, `companies.py`, `access_levels.py`, `groups.py`, `company_units.py`, `auth.py`, `smtp_server.py`, `base.py`)
- **Forms**: 24 فایل
  - Inventory: 6 فایل (`master_data.py`, `receipt.py`, `issue.py`, `request.py`, `base.py`, `stocktaking.py`)
  - Production: 8 فایل README جداگانه (`bom.py`, `process.py`, `product_order.py`, `work_line.py`, `machine.py`, `person.py`, `transfer_to_line.py`, `performance_record.py`)
  - Ticketing: 4 فایل README جداگانه (`base.py`, `categories.py`, `templates.py`, `tickets.py`)
  - Shared: 5 فایل (`users.py`, `companies.py`, `access_levels.py`, `groups.py`, `smtp_server.py`)
- **Utils**: 6 فایل (`shared/utils/permissions.py`, `inventory/utils/codes.py`, `inventory/utils/jalali.py`, `shared/utils/modules.py`, `shared/utils/email.py`, `ticketing/utils/codes.py`)
- **Services**: 1 فایل (`inventory/services/serials.py`)
- **Template Tags**: 3 فایل (`inventory/templatetags/jalali_tags.py`, `shared/templatetags/access_tags.py`, `shared/templatetags/json_filters.py`)
- **Context Processors**: 2 فایل (`shared/context_processors.py`, `ui/context_processors.py`)
- **Management Commands**: 1 فایل (`inventory/management/commands/cleanup_test_receipts.py`)
- **Migrations**: 1 فایل README کلی (`MIGRATIONS_README.md`)
- **جمع**: 74 فایل کامل

### ❌ نیازمند مستندسازی

#### ✅ Utilities (5 فایل)
- ✅ `inventory/utils/codes.py` → README_CODES.md
- ✅ `inventory/utils/jalali.py` → README_JALALI.md
- ✅ `shared/utils/modules.py` → README_MODULES.md
- ✅ `shared/utils/email.py` → README_EMAIL.md
- ✅ `ticketing/utils/codes.py` → README_CODES.md

#### ✅ Services (1 فایل)
- ✅ `inventory/services/serials.py` → README_SERIALS.md

#### ✅ Template Tags (3 فایل)
- ✅ `inventory/templatetags/jalali_tags.py` → README_JALALI_TAGS.md
- ✅ `shared/templatetags/access_tags.py` → README_ACCESS_TAGS.md
- ✅ `shared/templatetags/json_filters.py` → README_JSON_FILTERS.md

#### ✅ Context Processors (2 فایل)
- ✅ `shared/context_processors.py` → README_CONTEXT_PROCESSORS.md
- ✅ `ui/context_processors.py` → README_CONTEXT_PROCESSORS.md

#### ✅ Management Commands (1 فایل)
- ✅ `inventory/management/commands/cleanup_test_receipts.py` → README_CLEANUP_TEST_RECEIPTS.md

#### ✅ Migrations (1 فایل README کلی)
- ✅ `MIGRATIONS_README.md` (فایل README کلی در root پروژه که تمام migrations تمام ماژول‌ها را مستندسازی می‌کند)
  - شامل: inventory, production, qc, ticketing, shared migrations
  - **نکته**: `ui/migrations` migration file ندارد (فقط `__init__.py`)

**جمع کل**: ✅ تمام فایل‌ها مستندسازی شده‌اند (0 فایل باقی‌مانده)

---

## استاندارد مستندسازی

هر فایل README باید شامل موارد زیر باشد:

### 1. Header
```markdown
# [module]/[type]/[filename].py - [Description]

**هدف**: [توضیح کلی]

این فایل شامل [توضیح محتوا]:
- [Item 1]
- [Item 2]
```

### 2. برای هر کلاس/تابع
```markdown
### `ClassName`

**توضیح**: [توضیح کامل]

**Type**: `[Base Classes]`

**Attributes**:
- `attr1`: [توضیح]

**متدها**:

#### `method_name(self, param1: Type) -> ReturnType`

**توضیح**: [توضیح کامل]

**پارامترهای ورودی**:
- `param1` (Type): [توضیح]

**مقدار بازگشتی**:
- `ReturnType`: [توضیح]

**منطق**:
1. [Step 1]
2. [Step 2]
```

### 3. برای Forms
```markdown
### `FormName(forms.ModelForm)`

**توضیح**: [توضیح]

**Model**: `ModelName`

**Fields**:
- `field_name` (FieldType): [توضیح]
  - Widget: `WidgetType`
  - Label: `'Label'`
  - Required: `True/False`

**متدها**:
[مشابه بالا]
```

### 4. وابستگی‌ها
```markdown
## وابستگی‌ها

- `module.class`: `ClassName`
- `django.module`: `Item`
```

### 5. استفاده در پروژه
```markdown
## استفاده در پروژه

[توضیح نحوه استفاده]
```

### 6. نکات مهم
```markdown
## نکات مهم

1. **نکته 1**: [توضیح]
2. **نکته 2**: [توضیح]
```

---

## اولویت‌بندی

### اولویت بالا (باید زودتر انجام شود)
1. ✅ `inventory/views/master_data.py` - **کامل شده**
2. ✅ `inventory/forms/master_data.py` - **کامل شده**
3. ✅ `inventory/forms/receipt.py` - **کامل شده**
4. ✅ `inventory/forms/issue.py` - **کامل شده**
5. ✅ `inventory/forms/request.py` - **کامل شده**
6. ✅ `inventory/views/issues.py` - **کامل شده**
7. ✅ `inventory/forms/base.py` - **کامل شده**
8. ✅ `inventory/forms/stocktaking.py` - **کامل شده**
9. ✅ `inventory/views/receipts.py` - **کامل شده**
10. ✅ `inventory/views/requests.py` - **کامل شده**

### اولویت متوسط
11. ✅ `inventory/views/stocktaking.py` - **کامل شده**

### ✅ تکمیل شده (تمام فایل‌ها)

#### ✅ Utilities (5 فایل)
12. ✅ `inventory/utils/codes.py` - README_CODES.md
13. ✅ `inventory/utils/jalali.py` - README_JALALI.md
14. ✅ `shared/utils/modules.py` - README_MODULES.md
15. ✅ `shared/utils/email.py` - README_EMAIL.md
16. ✅ `ticketing/utils/codes.py` - README_CODES.md

#### ✅ Services (1 فایل)
17. ✅ `inventory/services/serials.py` - README_SERIALS.md

#### ✅ Template Tags (3 فایل)
18. ✅ `inventory/templatetags/jalali_tags.py` - README_JALALI_TAGS.md
19. ✅ `shared/templatetags/access_tags.py` - README_ACCESS_TAGS.md
20. ✅ `shared/templatetags/json_filters.py` - README_JSON_FILTERS.md

#### ✅ Context Processors (2 فایل)
21. ✅ `shared/context_processors.py` - README_CONTEXT_PROCESSORS.md
22. ✅ `ui/context_processors.py` - README_CONTEXT_PROCESSORS.md

#### ✅ Management Commands (1 فایل)
23. ✅ `inventory/management/commands/cleanup_test_receipts.py` - README_CLEANUP_TEST_RECEIPTS.md

#### ✅ Migrations (1 فایل README کلی)
24. ✅ `MIGRATIONS_README.md` - فایل README کلی در root پروژه که تمام migrations تمام ماژول‌ها را مستندسازی می‌کند
   - شامل: inventory, production, qc, ticketing, shared migrations
   - **نکته**: `ui/migrations` migration file ندارد

---

## نحوه کار

برای تکمیل مستندسازی:

1. **خواندن فایل**: ابتدا فایل را به صورت کامل می‌خوانیم
2. **تحلیل ساختار**: کلاس‌ها، متدها، و توابع را شناسایی می‌کنیم
3. **مستندسازی**: برای هر بخش README کامل می‌نویسیم
4. **بررسی**: مطمئن می‌شویم که هیچ جزئیاتی از قلم نیفتاده

---

## آخرین به‌روزرسانی

**تاریخ**: 26 نوامبر 2024
**وضعیت**: ✅ تکمیل شده
**پیشرفت**: 74 فایل کامل (Views: 36, Forms: 24, Utils: 5, Services: 1, Template Tags: 3, Context Processors: 2, Management Commands: 1, Migrations: 1, Other: 1)، 0 فایل ناقص، 0 فایل باقی‌مانده

**فایل‌های تکمیل شده در این مرحله**:
- ✅ Utilities: 5 فایل (codes.py, jalali.py, modules.py, email.py, codes.py)
- ✅ Services: 1 فایل (serials.py)
- ✅ Template Tags: 3 فایل (jalali_tags.py, access_tags.py, json_filters.py)
- ✅ Context Processors: 2 فایل (shared و ui)
- ✅ Management Commands: 1 فایل (cleanup_test_receipts.py)
- ✅ Migrations: 1 فایل README کلی (`MIGRATIONS_README.md` در root پروژه)

**تغییرات اخیر**:
- ✅ به‌روزرسانی `DOCUMENTATION_STATUS.md` - لیست کامل فایل‌های باقی‌مانده و ساختار migrations (یک README کلی برای تمام migrations در root پروژه)
- ✅ تکمیل `shared/forms/smtp_server.py` - README کامل با SMTPServerForm (TLS/SSL validation, password handling)
- ✅ تکمیل `shared/forms/groups.py` - README کامل با GroupForm (GroupProfile integration, access levels M2M)
- ✅ تکمیل `shared/forms/access_levels.py` - README کامل با AccessLevelForm (auto-generated code, read-only field)
- ✅ تکمیل `shared/forms/companies.py` - README کامل با CompanyForm و CompanyUnitForm (company scoping, parent unit validation)
- ✅ تکمیل `shared/forms/users.py` - README کامل با UserBaseForm, UserCreateForm, UserUpdateForm, UserCompanyAccessFormSet
- ✅ تکمیل `shared/views/smtp_server.py` - README کامل با 4 کلاس view (List, Create, Update, Delete) و password handling
- ✅ تکمیل `shared/views/auth.py` - README کامل با 3 function-based view (set_active_company, custom_login, mark_notification_read)
- ✅ تکمیل `shared/views/company_units.py` - README کامل با 4 کلاس view (List, Create, Update, Delete) و company scoping
- ✅ تکمیل `shared/views/groups.py` - README کامل با 4 کلاس view (List, Create, Update, Delete) و Django Group integration
- ✅ تکمیل `shared/views/access_levels.py` - README کامل با 4 کلاس view (List, Create, Update, Delete) و AccessLevelPermissionMixin
- ✅ تکمیل `qc/views/inspections.py` - README کامل با 3 کلاس view (List, Approve, Reject)
- ✅ تکمیل `shared/views/users.py` - README کامل با 4 کلاس view (List, Create, Update, Delete) و UserCompanyAccess formset
- ✅ تکمیل `shared/views/companies.py` - README کامل با 4 کلاس view (List, Create, Update, Delete) و auto access creation
- ✅ تکمیل `shared/utils/permissions.py` - README کامل با 1 dataclass و 5 function (permission resolution utilities)
- ✅ تکمیل `inventory/views/receipts.py` - README کامل با 27 کلاس view (2 base + 15 receipt views + 3 create from purchase request + 6 serial assignment)
- ✅ تکمیل `inventory/views/requests.py` - README کامل با 14 کلاس view (2 base mixins + 5 purchase request + 4 warehouse request + 4 create receipt)
- ✅ تکمیل `inventory/views/item_import.py` - README کامل با 2 view class و تمام helper methods
- ✅ تکمیل `inventory/views/create_issue_from_warehouse_request.py` - README کامل با 4 view class (1 base + 3 subclasses)
- ✅ تکمیل `inventory/views/issues_from_warehouse_request.py` - README کامل با 3 view class
- ✅ تکمیل `inventory/views/api.py` - README کامل با 10 function-based view (API endpoints)
- ✅ تکمیل `inventory/views/base.py` - README کامل با 5 کلاس (InventoryBaseView, DocumentLockProtectedMixin, DocumentLockView, LineFormsetMixin, ItemUnitFormsetMixin)
- ✅ تکمیل `inventory/views/stocktaking.py` - README کامل با تمام 16 کلاس view (1 Mixin + 15 view classes)
  - StocktakingFormMixin با تمام متدها
  - 3 نوع document (Deficit, Surplus, Record) با 5 view برای هر کدام
  - Fieldsets documentation
  - Lock mechanism documentation
- ✅ تکمیل `ticketing/forms/*.py` - 4 فایل README جداگانه برای تمام form classes
  - `README_BASE.md` - TicketingBaseForm, TicketFormMixin
  - `README_CATEGORIES.md` - TicketCategoryForm, TicketCategoryPermissionForm
  - `README_TEMPLATES.md` - TicketTemplateForm و 5 form class دیگر + 4 formset
  - `README_TICKETS.md` - TicketForm, TicketCreateForm
- ✅ تکمیل `ticketing/views/*.py` - 7 فایل README جداگانه برای تمام view classes
  - `README_CATEGORIES.md` - 4 view class
  - `README_SUBCATEGORIES.md` - 4 view class
  - `README_TEMPLATES.md` - 4 view class
  - `README_TICKETS.md` - 3 view class
  - `README_DEBUG.md` - debug_log_view function
  - `README_PLACEHOLDERS.md` - 4 placeholder view class
- ✅ تکمیل `production/views/*.py` - 9 فایل README جداگانه برای تمام view classes
  - `README_BOM.md`, `README_PROCESS.md`, `README_PRODUCT_ORDER.md`
  - `README_MACHINE.md`, `README_WORK_LINE.md`, `README_PERSONNEL.md`
  - `README_TRANSFER_TO_LINE.md`, `README_PERFORMANCE_RECORD.md`, `README_PLACEHOLDERS.md`
- ✅ تکمیل `production/forms/*.py` - 8 فایل README جداگانه برای تمام form classes
  - `README_BOM.md` - BOMForm, BOMMaterialLineForm, BOMMaterialLineFormSetBase
  - `README_PROCESS.md` - ProcessForm
  - `README_PRODUCT_ORDER.md` - ProductOrderForm
  - `README_WORK_LINE.md` - WorkLineForm
  - `README_MACHINE.md` - MachineForm
  - `README_PERSON.md` - PersonForm
  - `README_TRANSFER_TO_LINE.md` - TransferToLineForm, TransferToLineItemForm
  - `README_PERFORMANCE_RECORD.md` - PerformanceRecordForm و 3 form class دیگر
- ✅ تکمیل `production/views/*.py` - 3 فایل README جداگانه
  - `README_BOM.md` - BOMListView, BOMCreateView, BOMUpdateView, BOMDeleteView
  - `README_PROCESS.md` - ProcessListView, ProcessCreateView, ProcessUpdateView, ProcessDeleteView
  - `README_PRODUCT_ORDER.md` - ProductOrderListView, ProductOrderCreateView, ProductOrderUpdateView, ProductOrderDeleteView
- ✅ تکمیل `inventory/views/issues.py` - README کامل با تمام 18 کلاس view و متدها
- ✅ تکمیل `inventory/forms/base.py` - README کامل با helper functions و base classes
- ✅ تکمیل `inventory/forms/stocktaking.py` - README کامل با تمام 3 form class
- ✅ تکمیل `inventory/forms/receipt.py` - README کامل با تمام کلاس‌ها و متدها
- ✅ تکمیل `inventory/forms/issue.py` - README کامل با تمام کلاس‌ها و متدها
- ✅ تکمیل `inventory/forms/request.py` - README کامل با تمام کلاس‌ها و متدها
- ⚠️ به‌روزرسانی `inventory/views/receipts.py` - اضافه شدن توضیحات Item Filtering and Search
- ⚠️ به‌روزرسانی `inventory/views/requests.py` - اضافه شدن توضیحات Base Mixins و Item Filtering and Search

---

## یادداشت‌ها

- تمام مستندسازی‌ها به زبان فارسی نوشته می‌شوند (به جز کد و نام کلاس‌ها)
- کدها و نام کلاس‌ها به زبان انگلیسی باقی می‌مانند
- مستندسازی باید کامل و جامع باشد
- هیچ جزئیاتی نباید از قلم بیفتد

