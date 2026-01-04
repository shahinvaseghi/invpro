# راهنمای توسعه - Development Guide

**تاریخ ایجاد**: 2024-12-06  
**آخرین به‌روزرسانی**: 2024-12-23  
**وضعیت**: ✅ فعال - الزامی برای تمام توسعه‌دهندگان

---

## 📋 فهرست مطالب

1. [مقدمه و هدف](#مقدمه-و-هدف)
2. [خلاصه کارهای انجام شده](#خلاصه-کارهای-انجام-شده)
3. [لیست کامل فایل‌های Refactor شده](#لیست-کامل-فایلها-refactor-شده)
4. [قوانین اجباری](#قوانین-اجباری)
5. [فایل‌های اشتراکی موجود](#فایلهای-اشتراکی-موجود)
6. [نحوه استفاده از Base Classes](#نحوه-استفاده-از-base-classes)
7. [نحوه استفاده از JavaScript مشترک](#نحوه-استفاده-از-javascript-مشترک)
8. [نحوه استفاده از Templateهای مشترک](#نحوه-استفاده-از-templateهای-مشترک)
9. [استانداردهای کدنویسی](#استانداردهای-کدنویسی)
10. [استانداردهای Testing](#استانداردهای-testing)
11. [استانداردهای امنیتی](#استانداردهای-امنیتی)
12. [استانداردهای API](#استانداردهای-api)
13. [راهنمای Database & Migration](#راهنمای-database--migration)
14. [Error Handling & Logging](#error-handling--logging)
15. [Git Workflow](#git-workflow)
16. [Performance & Optimization](#performance--optimization)
17. [استانداردهای مستندسازی](#استانداردهای-مستندسازی)
18. [راهنمای Code Review](#راهنمای-code-review)
19. [مدیریت Environment](#مدیریت-environment)
20. [چک‌لیست قبل از Commit](#چکلیست-قبل-از-commit)
21. [مثال‌های عملی](#مثالهای-عملی)

---

## 🎯 مقدمه و هدف

این راهنما شامل **قوانین اجباری** و **استانداردهای توسعه** برای پروژه ERP است. هدف اصلی:

- ✅ **کاهش تکرار کد**: استفاده از فایل‌های اشتراکی به جای نوشتن کد تکراری
- ✅ **یکپارچگی**: تمام ماژول‌ها از الگوهای مشترک استفاده می‌کنند
- ✅ **نگهداری آسان**: تغییرات فقط در یک جا اعمال می‌شوند
- ✅ **توسعه سریع**: ایجاد feature جدید با استفاده از Base Classes بسیار سریع‌تر است
- ✅ **کیفیت بالا**: استانداردهای Testing, Security, Performance
- ✅ **همکاری بهتر**: Git workflow و Code review guidelines

**⚠️ مهم**: تمام توسعه‌دهندگان **باید** این راهنما را مطالعه کنند و از قوانین آن پیروی کنند.

### 🆕 موارد جدید در نسخه 2.0

این نسخه شامل استانداردهای جامع‌تری است:

1. **🧪 Testing Standards** - استانداردهای کامل برای نوشتن Unit, Integration و Functional Tests
2. **🔒 Security Standards** - راهنمای امنیتی شامل SQL Injection, XSS, CSRF Prevention
3. **🌐 API Standards** - فرمت استاندارد Response, Error Handling, Versioning
4. **💾 Database & Migration** - بهترین روش‌های Migration و Query Optimization
5. **📊 Error Handling & Logging** - استراتژی Logging و Error Handling
6. **🔄 Git Workflow** - Branching Strategy و Commit Message Convention
7. **⚡ Performance & Optimization** - بهینه‌سازی Query, Caching, Background Tasks
8. **📖 Documentation Standards** - Docstring format و inline comments
9. **👁️ Code Review Guidelines** - چک‌لیست کامل Code Review
10. **🔧 Environment Management** - مدیریت Environment Variables و Settings

---

## 📊 خلاصه کارهای انجام شده

### ✅ معماری مشترک (Shared Architecture)

پروژه به طور کامل refactor شده و معماری مشترک پیاده‌سازی شده است:

#### Backend Refactoring
- ✅ **13 Base View Class** در `shared/views/base.py`:
  - `BaseListView` - برای List Views
  - `BaseCreateView` - برای Create Views
  - `BaseUpdateView` - برای Update Views
  - `BaseDeleteView` - برای Delete Views
  - `BaseDetailView` - برای Detail Views
  - `BaseFormsetCreateView` - برای Views با Formset
  - `BaseFormsetUpdateView` - برای Update Views با Formset
  - `BaseDocumentListView` - برای Document List Views
  - `BaseDocumentCreateView` - برای Document Create Views
  - `BaseDocumentUpdateView` - برای Document Update Views
  - `BaseNestedFormsetCreateView` - برای Nested Formsets
  - `BaseNestedFormsetUpdateView` - برای Nested Formsets در Update
  - `BaseMultipleFormsetCreateView` - برای Multiple Formsets

- ✅ **5 Filter Function** در `shared/filters.py`:
  - `apply_search()` - جستجو در چند فیلد
  - `apply_status_filter()` - فیلتر وضعیت
  - `apply_company_filter()` - فیلتر شرکت
  - `apply_date_range_filter()` - فیلتر بازه تاریخ
  - `apply_multi_field_filter()` - فیلتر چند فیلد

- ✅ **5 Mixin** در `shared/mixins.py`:
  - `PermissionFilterMixin` - فیلتر بر اساس permissions
  - `CompanyScopedViewMixin` - فیلتر بر اساس active company
  - `AutoSetFieldsMixin` - auto-set company_id, created_by, edited_by
  - `SuccessMessageMixin` - نمایش success message
  - `FeaturePermissionRequiredMixin` - بررسی permissions

- ✅ **2 Base Form Class** در `shared/forms/base.py`:
  - `BaseModelForm` - فرم پایه با auto widget styling
  - `BaseFormset` - helper class برای formsets

- ✅ **3 API View Class** در `shared/views/api.py`:
  - `BaseAPIView` - پایه برای API views
  - `BaseListAPIView` - لیست API view
  - `BaseDetailAPIView` - detail API view

- ✅ **4 Helper Function** در `shared/utils/view_helpers.py`:
  - `get_breadcrumbs()` - تولید breadcrumbs
  - `get_success_message()` - تولید success message
  - `validate_active_company()` - بررسی active company
  - `get_table_headers()` - تولید table headers

#### Frontend Refactoring
- ✅ **9 فایل JavaScript مشترک** در `static/js/`:
  - `formset.js` - مدیریت formsets (add/remove rows, reindex)
  - `cascading-dropdowns.js` - مدیریت cascading dropdowns
  - `table-export.js` - export جدول به CSV/Excel/Print
  - `form-helpers.js` - توابع helper برای فرم‌ها
  - `item-filters.js` - فیلترهای item (category, subcategory)
  - `formset-table.js` - مدیریت formset در جداول
  - `approval-actions.js` - توابع approve/reject مشترک
  - `modal-dialogs.js` - مدیریت modal dialogs
  - `common-actions.js` - توابع مشترک (print, confirm, toggle)

- ✅ **1 فایل CSS مشترک** در `static/css/`:
  - `shared.css` - استایل‌های مشترک (تمام inline styles حذف شده)

- ✅ **5 Template Partial** در `templates/shared/partials/`:
  - `row_actions.html` - نمایش دکمه‌های action برای هر row
  - `filter_panel.html` - پنل فیلتر مشترک
  - `stats_cards.html` - نمایش کارت‌های آمار
  - `pagination.html` - pagination مشترک
  - `empty_state.html` - نمایش empty state

- ✅ **4 Generic Template** در `templates/shared/generic/`:
  - `generic_list.html` - template مشترک برای List Views
  - `generic_form.html` - template مشترک برای Create/Update Views
  - `generic_detail.html` - template مشترک برای Detail Views
  - `generic_confirm_delete.html` - template مشترک برای Delete Views

- ✅ **5 Template Tag** در `shared/templatetags/view_tags.py`:
  - `{% get_breadcrumbs %}` - تولید breadcrumbs
  - `{% get_table_headers %}` - تولید table headers
  - `{% can_action %}` - بررسی permission برای action
  - `{% get_object_actions %}` - دریافت actions موجود
  - `{{ dict|get_item:key }}` - دریافت item از dictionary

#### Migration Status
- ✅ **ماژول `shared`**: 25/25 view تکمیل شده (100%)
- ✅ **ماژول `inventory`**: 89/89 view تکمیل شده (100%)
- ✅ **ماژول `production`**: 48/68 view تکمیل شده (20 view خاص)
- ✅ **ماژول `accounting`**: 31/34 view تکمیل شده (3 view خاص)
- ✅ **ماژول `ticketing`**: 19/22 view تکمیل شده (7 view خاص)
- ✅ **ماژول `qc`**: 6/6 view تکمیل شده (100%)

**جمع کل**: **218 view از 244 view** تکمیل شده (89%)

---

## 📁 لیست کامل فایل‌های Refactor شده

این بخش شامل لیست کامل تمام فایل‌هایی است که refactor شده‌اند و از فایل‌های اشتراکی استفاده می‌کنند.

### ماژول `shared` (25/25 view - 100% تکمیل شده)

#### Backend Views

| فایل | View | Base Class | Template | وضعیت |
|------|------|------------|----------|--------|
| `shared/views/companies.py` | `CompanyListView` | `BaseListView` | `generic_list.html` | ✅ |
| `shared/views/companies.py` | `CompanyCreateView` | `BaseCreateView` | `generic_form.html` | ✅ |
| `shared/views/companies.py` | `CompanyUpdateView` | `BaseUpdateView` | `generic_form.html` | ✅ |
| `shared/views/companies.py` | `CompanyDetailView` | `BaseDetailView` | `generic_detail.html` | ✅ |
| `shared/views/companies.py` | `CompanyDeleteView` | `BaseDeleteView` | `generic_confirm_delete.html` | ✅ |
| `shared/views/access_levels.py` | `AccessLevelListView` | `BaseListView` | `generic_list.html` | ✅ |
| `shared/views/access_levels.py` | `AccessLevelCreateView` | `BaseCreateView` + `AccessLevelPermissionMixin` | `generic_form.html` | ✅ |
| `shared/views/access_levels.py` | `AccessLevelUpdateView` | `BaseUpdateView` + `AccessLevelPermissionMixin` | `generic_form.html` | ✅ |
| `shared/views/access_levels.py` | `AccessLevelDetailView` | `BaseDetailView` | `generic_detail.html` | ✅ |
| `shared/views/access_levels.py` | `AccessLevelDeleteView` | `BaseDeleteView` | `generic_confirm_delete.html` | ✅ |
| `shared/views/groups.py` | `GroupListView` | `BaseListView` | `generic_list.html` | ✅ |
| `shared/views/groups.py` | `GroupCreateView` | `BaseCreateView` | `generic_form.html` | ✅ |
| `shared/views/groups.py` | `GroupUpdateView` | `BaseUpdateView` | `generic_form.html` | ✅ |
| `shared/views/groups.py` | `GroupDetailView` | `BaseDetailView` | `generic_detail.html` | ✅ |
| `shared/views/groups.py` | `GroupDeleteView` | `BaseDeleteView` | `generic_confirm_delete.html` | ✅ |
| `shared/views/users.py` | `UserListView` | `BaseListView` | `generic_list.html` | ✅ |
| `shared/views/users.py` | `UserCreateView` | `BaseCreateView` + `UserAccessFormsetMixin` | `generic_form.html` | ✅ |
| `shared/views/users.py` | `UserUpdateView` | `BaseUpdateView` + `UserAccessFormsetMixin` | `generic_form.html` | ✅ |
| `shared/views/users.py` | `UserDetailView` | `BaseDetailView` | `generic_detail.html` | ✅ |
| `shared/views/users.py` | `UserDeleteView` | `BaseDeleteView` | `generic_confirm_delete.html` | ✅ |
| `shared/views/company_units.py` | `CompanyUnitListView` | `BaseListView` | `generic_list.html` | ✅ |
| `shared/views/company_units.py` | `CompanyUnitCreateView` | `BaseCreateView` | `generic_form.html` | ✅ |
| `shared/views/company_units.py` | `CompanyUnitUpdateView` | `BaseUpdateView` | `generic_form.html` | ✅ |
| `shared/views/company_units.py` | `CompanyUnitDetailView` | `BaseDetailView` | `generic_detail.html` | ✅ |
| `shared/views/company_units.py` | `CompanyUnitDeleteView` | `BaseDeleteView` | `generic_confirm_delete.html` | ✅ |

#### Frontend Templates

| فایل Template | Generic Template | Partials استفاده شده | JavaScript استفاده شده | وضعیت |
|---------------|------------------|---------------------|----------------------|--------|
| `shared/company_detail.html` | `generic_detail.html` | - | - | ✅ |
| `shared/user_detail.html` | `generic_detail.html` | - | `formset.js` | ✅ |
| `shared/company_unit_detail.html` | `generic_detail.html` | - | - | ✅ |
| `shared/group_detail.html` | `generic_detail.html` | - | - | ✅ |
| `shared/access_level_detail.html` | `generic_detail.html` | - | - | ✅ |
| `shared/user_form.html` | `generic_form.html` | - | `formset.js` | ✅ |

---

### ماژول `inventory` (89/89 view - 100% تکمیل شده)

#### Backend Views - Master Data

| فایل | View | Base Class | Template | وضعیت |
|------|------|------------|----------|--------|
| `inventory/views/master_data.py` | `ItemTypeListView` | `BaseListView` | `generic_list.html` | ✅ |
| `inventory/views/master_data.py` | `ItemTypeCreateView` | `BaseCreateView` | `generic_form.html` | ✅ |
| `inventory/views/master_data.py` | `ItemTypeUpdateView` | `BaseUpdateView` | `generic_form.html` | ✅ |
| `inventory/views/master_data.py` | `ItemTypeDetailView` | `BaseDetailView` | `generic_detail.html` | ✅ |
| `inventory/views/master_data.py` | `ItemTypeDeleteView` | `BaseDeleteView` | `generic_confirm_delete.html` | ✅ |
| `inventory/views/master_data.py` | `ItemCategoryListView` | `BaseListView` | `generic_list.html` | ✅ |
| `inventory/views/master_data.py` | `ItemCategoryCreateView` | `BaseCreateView` | `generic_form.html` | ✅ |
| `inventory/views/master_data.py` | `ItemCategoryUpdateView` | `BaseUpdateView` | `generic_form.html` | ✅ |
| `inventory/views/master_data.py` | `ItemCategoryDetailView` | `BaseDetailView` | `generic_detail.html` | ✅ |
| `inventory/views/master_data.py` | `ItemCategoryDeleteView` | `BaseDeleteView` | `generic_confirm_delete.html` | ✅ |
| `inventory/views/master_data.py` | `ItemSubcategoryListView` | `BaseListView` | `generic_list.html` | ✅ |
| `inventory/views/master_data.py` | `ItemSubcategoryCreateView` | `BaseCreateView` | `generic_form.html` | ✅ |
| `inventory/views/master_data.py` | `ItemSubcategoryUpdateView` | `BaseUpdateView` | `generic_form.html` | ✅ |
| `inventory/views/master_data.py` | `ItemSubcategoryDetailView` | `BaseDetailView` | `generic_detail.html` | ✅ |
| `inventory/views/master_data.py` | `ItemSubcategoryDeleteView` | `BaseDeleteView` | `generic_confirm_delete.html` | ✅ |
| `inventory/views/master_data.py` | `ItemListView` | `BaseListView` | `generic_list.html` | ✅ |
| `inventory/views/master_data.py` | `ItemCreateView` | `BaseCreateView` | `generic_form.html` | ✅ |
| `inventory/views/master_data.py` | `ItemUpdateView` | `BaseFormsetUpdateView` | `generic_form.html` | ✅ |
| `inventory/views/master_data.py` | `ItemDetailView` | `BaseDetailView` | `generic_detail.html` | ✅ |
| `inventory/views/master_data.py` | `ItemDeleteView` | `BaseDeleteView` | `generic_confirm_delete.html` | ✅ |
| `inventory/views/master_data.py` | `WarehouseListView` | `BaseListView` | `generic_list.html` | ✅ |
| `inventory/views/master_data.py` | `WarehouseCreateView` | `BaseCreateView` | `generic_form.html` | ✅ |
| `inventory/views/master_data.py` | `WarehouseUpdateView` | `BaseUpdateView` | `generic_form.html` | ✅ |
| `inventory/views/master_data.py` | `WarehouseDetailView` | `BaseDetailView` | `generic_detail.html` | ✅ |
| `inventory/views/master_data.py` | `WarehouseDeleteView` | `BaseDeleteView` | `generic_confirm_delete.html` | ✅ |
| `inventory/views/master_data.py` | `SupplierCategoryListView` | `BaseListView` | `generic_list.html` | ✅ |
| `inventory/views/master_data.py` | `SupplierCategoryCreateView` | `BaseCreateView` | `generic_form.html` | ✅ |
| `inventory/views/master_data.py` | `SupplierCategoryUpdateView` | `BaseUpdateView` | `generic_form.html` | ✅ |
| `inventory/views/master_data.py` | `SupplierCategoryDetailView` | `BaseDetailView` | `generic_detail.html` | ✅ |
| `inventory/views/master_data.py` | `SupplierCategoryDeleteView` | `BaseDeleteView` | `generic_confirm_delete.html` | ✅ |
| `inventory/views/master_data.py` | `SupplierListView` | `BaseListView` | `generic_list.html` | ✅ |
| `inventory/views/master_data.py` | `SupplierCreateView` | `BaseCreateView` | `generic_form.html` | ✅ |
| `inventory/views/master_data.py` | `SupplierUpdateView` | `BaseUpdateView` | `generic_form.html` | ✅ |
| `inventory/views/master_data.py` | `SupplierDetailView` | `BaseDetailView` | `generic_detail.html` | ✅ |
| `inventory/views/master_data.py` | `SupplierDeleteView` | `BaseDeleteView` | `generic_confirm_delete.html` | ✅ |

#### Backend Views - Receipts

| فایل | View | Base Class | Template | وضعیت |
|------|------|------------|----------|--------|
| `inventory/views/receipts.py` | `ReceiptTemporaryListView` | `BaseDocumentListView` | `generic_list.html` | ✅ |
| `inventory/views/receipts.py` | `ReceiptTemporaryCreateView` | `BaseDocumentCreateView` + `LineFormsetMixin` | `generic_form.html` | ✅ |
| `inventory/views/receipts.py` | `ReceiptTemporaryUpdateView` | `BaseDocumentUpdateView` + `LineFormsetMixin` | `generic_form.html` | ✅ |
| `inventory/views/receipts.py` | `ReceiptTemporaryDetailView` | `BaseDetailView` | `generic_detail.html` | ✅ |
| `inventory/views/receipts.py` | `ReceiptTemporaryDeleteView` | `BaseDeleteView` + `DocumentLockProtectedMixin` | `generic_confirm_delete.html` | ✅ |
| `inventory/views/receipts.py` | `ReceiptPermanentListView` | `BaseDocumentListView` | `generic_list.html` | ✅ |
| `inventory/views/receipts.py` | `ReceiptPermanentCreateView` | `BaseDocumentCreateView` + `LineFormsetMixin` | `generic_form.html` | ✅ |
| `inventory/views/receipts.py` | `ReceiptPermanentUpdateView` | `BaseDocumentUpdateView` + `LineFormsetMixin` | `generic_form.html` | ✅ |
| `inventory/views/receipts.py` | `ReceiptPermanentDetailView` | `BaseDetailView` | `generic_detail.html` | ✅ |
| `inventory/views/receipts.py` | `ReceiptPermanentDeleteView` | `BaseDeleteView` + `DocumentLockProtectedMixin` | `generic_confirm_delete.html` | ✅ |
| `inventory/views/receipts.py` | `ReceiptConsignmentListView` | `BaseDocumentListView` | `generic_list.html` | ✅ |
| `inventory/views/receipts.py` | `ReceiptConsignmentCreateView` | `BaseDocumentCreateView` + `LineFormsetMixin` | `generic_form.html` | ✅ |
| `inventory/views/receipts.py` | `ReceiptConsignmentUpdateView` | `BaseDocumentUpdateView` + `LineFormsetMixin` | `generic_form.html` | ✅ |
| `inventory/views/receipts.py` | `ReceiptConsignmentDetailView` | `BaseDetailView` | `generic_detail.html` | ✅ |
| `inventory/views/receipts.py` | `ReceiptConsignmentDeleteView` | `BaseDeleteView` + `DocumentLockProtectedMixin` | `generic_confirm_delete.html` | ✅ |

#### Backend Views - Issues

| فایل | View | Base Class | Template | وضعیت |
|------|------|------------|----------|--------|
| `inventory/views/issues.py` | `IssuePermanentListView` | `BaseDocumentListView` | `generic_list.html` | ✅ |
| `inventory/views/issues.py` | `IssuePermanentCreateView` | `BaseDocumentCreateView` + `LineFormsetMixin` | `generic_form.html` | ✅ |
| `inventory/views/issues.py` | `IssuePermanentUpdateView` | `BaseDocumentUpdateView` + `LineFormsetMixin` | `generic_form.html` | ✅ |
| `inventory/views/issues.py` | `IssuePermanentDetailView` | `BaseDetailView` | `generic_detail.html` | ✅ |
| `inventory/views/issues.py` | `IssuePermanentDeleteView` | `BaseDeleteView` + `DocumentLockProtectedMixin` | `generic_confirm_delete.html` | ✅ |
| `inventory/views/issues.py` | `IssueConsumptionListView` | `BaseDocumentListView` | `generic_list.html` | ✅ |
| `inventory/views/issues.py` | `IssueConsumptionCreateView` | `BaseDocumentCreateView` + `LineFormsetMixin` | `generic_form.html` | ✅ |
| `inventory/views/issues.py` | `IssueConsumptionUpdateView` | `BaseDocumentUpdateView` + `LineFormsetMixin` | `generic_form.html` | ✅ |
| `inventory/views/issues.py` | `IssueConsumptionDetailView` | `BaseDetailView` | `generic_detail.html` | ✅ |
| `inventory/views/issues.py` | `IssueConsumptionDeleteView` | `BaseDeleteView` + `DocumentLockProtectedMixin` | `generic_confirm_delete.html` | ✅ |
| `inventory/views/issues.py` | `IssueConsignmentListView` | `BaseDocumentListView` | `generic_list.html` | ✅ |
| `inventory/views/issues.py` | `IssueConsignmentCreateView` | `BaseDocumentCreateView` + `LineFormsetMixin` | `generic_form.html` | ✅ |
| `inventory/views/issues.py` | `IssueConsignmentUpdateView` | `BaseDocumentUpdateView` + `LineFormsetMixin` | `generic_form.html` | ✅ |
| `inventory/views/issues.py` | `IssueConsignmentDetailView` | `BaseDetailView` | `generic_detail.html` | ✅ |
| `inventory/views/issues.py` | `IssueConsignmentDeleteView` | `BaseDeleteView` + `DocumentLockProtectedMixin` | `generic_confirm_delete.html` | ✅ |
| `inventory/views/issues.py` | `IssueWarehouseTransferListView` | `BaseDocumentListView` | `generic_list.html` | ✅ |
| `inventory/views/issues.py` | `IssueWarehouseTransferCreateView` | `BaseDocumentCreateView` + `LineFormsetMixin` | `generic_form.html` | ✅ |
| `inventory/views/issues.py` | `IssueWarehouseTransferUpdateView` | `BaseDocumentUpdateView` + `LineFormsetMixin` | `generic_form.html` | ✅ |
| `inventory/views/issues.py` | `IssueWarehouseTransferDetailView` | `BaseDetailView` | `generic_detail.html` | ✅ |

#### Backend Views - Requests

| فایل | View | Base Class | Template | وضعیت |
|------|------|------------|----------|--------|
| `inventory/views/requests.py` | `PurchaseRequestListView` | `BaseListView` | `generic_list.html` | ✅ |
| `inventory/views/requests.py` | `PurchaseRequestCreateView` | `BaseCreateView` | `generic_form.html` | ✅ |
| `inventory/views/requests.py` | `PurchaseRequestUpdateView` | `BaseFormsetUpdateView` | `generic_form.html` | ✅ |
| `inventory/views/requests.py` | `PurchaseRequestDetailView` | `BaseDetailView` | `generic_detail.html` | ✅ |
| `inventory/views/requests.py` | `WarehouseRequestListView` | `BaseListView` | `generic_list.html` | ✅ |
| `inventory/views/requests.py` | `WarehouseRequestCreateView` | `BaseFormsetCreateView` | `generic_form.html` | ✅ |
| `inventory/views/requests.py` | `WarehouseRequestUpdateView` | `BaseFormsetUpdateView` | `generic_form.html` | ✅ |
| `inventory/views/requests.py` | `WarehouseRequestDetailView` | `BaseDetailView` | `generic_detail.html` | ✅ |

#### Backend Views - Stocktaking

| فایل | View | Base Class | Template | وضعیت |
|------|------|------------|----------|--------|
| `inventory/views/stocktaking.py` | `StocktakingDeficitListView` | `BaseDocumentListView` | `generic_list.html` | ✅ |
| `inventory/views/stocktaking.py` | `StocktakingDeficitCreateView` | `BaseDocumentCreateView` | `generic_form.html` | ✅ |
| `inventory/views/stocktaking.py` | `StocktakingDeficitUpdateView` | `BaseDocumentUpdateView` | `generic_form.html` | ✅ |
| `inventory/views/stocktaking.py` | `StocktakingDeficitDetailView` | `BaseDetailView` | `generic_detail.html` | ✅ |
| `inventory/views/stocktaking.py` | `StocktakingDeficitDeleteView` | `BaseDeleteView` | `generic_confirm_delete.html` | ✅ |
| `inventory/views/stocktaking.py` | `StocktakingSurplusListView` | `BaseDocumentListView` | `generic_list.html` | ✅ |
| `inventory/views/stocktaking.py` | `StocktakingSurplusCreateView` | `BaseDocumentCreateView` | `generic_form.html` | ✅ |
| `inventory/views/stocktaking.py` | `StocktakingSurplusUpdateView` | `BaseDocumentUpdateView` | `generic_form.html` | ✅ |
| `inventory/views/stocktaking.py` | `StocktakingSurplusDetailView` | `BaseDetailView` | `generic_detail.html` | ✅ |
| `inventory/views/stocktaking.py` | `StocktakingSurplusDeleteView` | `BaseDeleteView` | `generic_confirm_delete.html` | ✅ |
| `inventory/views/stocktaking.py` | `StocktakingRecordListView` | `BaseListView` | `generic_list.html` | ✅ |
| `inventory/views/stocktaking.py` | `StocktakingRecordCreateView` | `BaseCreateView` | `generic_form.html` | ✅ |
| `inventory/views/stocktaking.py` | `StocktakingRecordUpdateView` | `BaseUpdateView` | `generic_form.html` | ✅ |
| `inventory/views/stocktaking.py` | `StocktakingRecordDetailView` | `BaseDetailView` | `generic_detail.html` | ✅ |
| `inventory/views/stocktaking.py` | `StocktakingRecordDeleteView` | `BaseDeleteView` | `generic_confirm_delete.html` | ✅ |

#### Frontend Templates - Detail Views

| فایل Template | Generic Template | JavaScript استفاده شده | وضعیت |
|---------------|------------------|----------------------|--------|
| `inventory/itemtype_detail.html` | `generic_detail.html` | - | ✅ |
| `inventory/itemcategory_detail.html` | `generic_detail.html` | - | ✅ |
| `inventory/itemsubcategory_detail.html` | `generic_detail.html` | - | ✅ |
| `inventory/item_detail.html` | `generic_detail.html` | - | ✅ |
| `inventory/warehouse_detail.html` | `generic_detail.html` | - | ✅ |
| `inventory/supplier_detail.html` | `generic_detail.html` | - | ✅ |
| `inventory/suppliercategory_detail.html` | `generic_detail.html` | - | ✅ |
| `inventory/purchase_request_detail.html` | `generic_detail.html` | - | ✅ |
| `inventory/warehouse_request_detail.html` | `generic_detail.html` | - | ✅ |
| `inventory/receipt_detail.html` | `generic_detail.html` | - | ✅ |
| `inventory/issue_detail.html` | `generic_detail.html` | - | ✅ |
| `inventory/stocktaking_deficit_detail.html` | `generic_detail.html` | - | ✅ |
| `inventory/stocktaking_surplus_detail.html` | `generic_detail.html` | - | ✅ |
| `inventory/stocktaking_record_detail.html` | `generic_detail.html` | - | ✅ |
| `inventory/issue_warehouse_transfer_detail.html` | `generic_detail.html` | - | ✅ |

#### Frontend Templates - List Views

| فایل Template | Generic Template | Partials استفاده شده | JavaScript استفاده شده | وضعیت |
|---------------|------------------|---------------------|----------------------|--------|
| `inventory/item_types.html` | `generic_list.html` | `row_actions.html` | `table-export.js` | ✅ |
| `inventory/item_categories.html` | `generic_list.html` | `row_actions.html` | `table-export.js` | ✅ |
| `inventory/item_subcategories.html` | `generic_list.html` | `row_actions.html` | `table-export.js` | ✅ |
| `inventory/suppliers.html` | `generic_list.html` | `row_actions.html` | `table-export.js` | ✅ |
| `inventory/supplier_categories.html` | `generic_list.html` | `row_actions.html` | `table-export.js` | ✅ |
| `inventory/purchase_requests.html` | `generic_list.html` | `row_actions.html` | `table-export.js` | ✅ |

#### Frontend Templates - Form Views

| فایل Template | Generic Template | JavaScript استفاده شده | وضعیت |
|---------------|------------------|----------------------|--------|
| `inventory/item_form.html` | `generic_form.html` | `formset.js`, `cascading-dropdowns.js` | ✅ |
| `inventory/receipt_form.html` | `generic_form.html` | `formset.js`, `cascading-dropdowns.js` | ✅ |
| `inventory/purchase_request_form.html` | `generic_form.html` | `formset.js`, `item-filters.js`, `formset-table.js` | ✅ |
| `inventory/warehouse_request_form.html` | `generic_form.html` | `formset.js`, `item-filters.js` | ✅ |

---

### ماژول `production` (48/68 view - 71% تکمیل شده)

#### Backend Views

| فایل | View | Base Class | Template | وضعیت |
|------|------|------------|----------|--------|
| `production/views/personnel.py` | `PersonnelListView` | `BaseListView` | `generic_list.html` | ✅ |
| `production/views/personnel.py` | `PersonCreateView` | `BaseCreateView` | `generic_form.html` | ✅ |
| `production/views/personnel.py` | `PersonUpdateView` | `BaseUpdateView` | `generic_form.html` | ✅ |
| `production/views/personnel.py` | `PersonDetailView` | `BaseDetailView` | `generic_detail.html` | ✅ |
| `production/views/personnel.py` | `PersonDeleteView` | `BaseDeleteView` | `generic_confirm_delete.html` | ✅ |
| `production/views/machine.py` | `MachineListView` | `BaseListView` | `generic_list.html` | ✅ |
| `production/views/machine.py` | `MachineCreateView` | `BaseCreateView` | `generic_form.html` | ✅ |
| `production/views/machine.py` | `MachineUpdateView` | `BaseUpdateView` | `generic_form.html` | ✅ |
| `production/views/machine.py` | `MachineDetailView` | `BaseDetailView` | `generic_detail.html` | ✅ |
| `production/views/machine.py` | `MachineDeleteView` | `BaseDeleteView` | `generic_confirm_delete.html` | ✅ |
| `production/views/work_line.py` | `WorkLineListView` | `BaseListView` | `generic_list.html` | ✅ |
| `production/views/work_line.py` | `WorkLineCreateView` | `BaseCreateView` | `generic_form.html` | ✅ |
| `production/views/work_line.py` | `WorkLineUpdateView` | `BaseUpdateView` | `generic_form.html` | ✅ |
| `production/views/work_line.py` | `WorkLineDetailView` | `BaseDetailView` | `generic_detail.html` | ✅ |
| `production/views/work_line.py` | `WorkLineDeleteView` | `BaseDeleteView` | `generic_confirm_delete.html` | ✅ |
| `production/views/process.py` | `ProcessListView` | `BaseListView` | `generic_list.html` | ✅ |
| `production/views/process.py` | `ProcessCreateView` | `BaseFormsetCreateView` | `generic_form.html` | ✅ |
| `production/views/process.py` | `ProcessUpdateView` | `BaseFormsetUpdateView` | `generic_form.html` | ✅ |
| `production/views/process.py` | `ProcessDetailView` | `BaseDetailView` | `generic_detail.html` | ✅ |
| `production/views/process.py` | `ProcessDeleteView` | `BaseDeleteView` | `generic_confirm_delete.html` | ✅ |
| `production/views/bom.py` | `BOMListView` | `BaseListView` | `generic_list.html` | ✅ |
| `production/views/bom.py` | `BOMCreateView` | `BaseNestedFormsetCreateView` | `generic_form.html` | ✅ |
| `production/views/bom.py` | `BOMUpdateView` | `BaseNestedFormsetUpdateView` | `generic_form.html` | ✅ |
| `production/views/bom.py` | `BOMDetailView` | `BaseDetailView` | `generic_detail.html` | ✅ |
| `production/views/bom.py` | `BOMDeleteView` | `BaseDeleteView` | `generic_confirm_delete.html` | ✅ |
| `production/views/product_order.py` | `ProductOrderListView` | `BaseListView` | `generic_list.html` | ✅ |
| `production/views/product_order.py` | `ProductOrderCreateView` | `BaseCreateView` + `TransferRequestCreationMixin` | `generic_form.html` | ✅ |
| `production/views/product_order.py` | `ProductOrderUpdateView` | `BaseUpdateView` + `TransferRequestCreationMixin` | `generic_form.html` | ✅ |
| `production/views/product_order.py` | `ProductOrderDetailView` | `BaseDetailView` | `generic_detail.html` | ✅ |
| `production/views/product_order.py` | `ProductOrderDeleteView` | `BaseDeleteView` | `generic_confirm_delete.html` | ✅ |
| `production/views/transfer_to_line.py` | `TransferToLineListView` | `BaseDocumentListView` | `generic_list.html` | ✅ |
| `production/views/transfer_to_line.py` | `TransferToLineCreateView` | `BaseMultipleDocumentCreateView` | `generic_form.html` | ✅ |
| `production/views/transfer_to_line.py` | `TransferToLineUpdateView` | `BaseFormsetUpdateView` | `generic_form.html` | ✅ |
| `production/views/transfer_to_line.py` | `TransferToLineDetailView` | `BaseDetailView` | `generic_detail.html` | ✅ |
| `production/views/transfer_to_line.py` | `TransferToLineDeleteView` | `BaseDeleteView` | `generic_confirm_delete.html` | ✅ |
| `production/views/performance_record.py` | `PerformanceRecordListView` | `BaseDocumentListView` | `generic_list.html` | ✅ |
| `production/views/performance_record.py` | `PerformanceRecordCreateView` | `BaseMultipleFormsetCreateView` | `generic_form.html` | ✅ |
| `production/views/performance_record.py` | `PerformanceRecordUpdateView` | `BaseMultipleFormsetUpdateView` | `generic_form.html` | ✅ |
| `production/views/performance_record.py` | `PerformanceRecordDetailView` | `BaseDetailView` | `generic_detail.html` | ✅ |
| `production/views/performance_record.py` | `PerformanceRecordDeleteView` | `BaseDeleteView` | `generic_confirm_delete.html` | ✅ |
| `production/views/rework.py` | `ReworkDocumentListView` | `BaseDocumentListView` | `generic_list.html` | ✅ |
| `production/views/rework.py` | `ReworkDocumentCreateView` | `BaseCreateView` | `generic_form.html` | ✅ |
| `production/views/rework.py` | `ReworkDocumentUpdateView` | `BaseUpdateView` | `generic_form.html` | ✅ |
| `production/views/rework.py` | `ReworkDocumentDetailView` | `BaseDetailView` | `generic_detail.html` | ✅ |
| `production/views/rework.py` | `ReworkDocumentDeleteView` | `BaseDeleteView` | `generic_confirm_delete.html` | ✅ |
| `production/views/qc_operations.py` | `QCOperationsListView` | `BaseListView` | `generic_list.html` | ✅ |

#### Frontend Templates - Detail Views

| فایل Template | Generic Template | وضعیت |
|---------------|------------------|--------|
| `production/person_detail.html` | `generic_detail.html` | ✅ |
| `production/machine_detail.html` | `generic_detail.html` | ✅ |
| `production/work_line_detail.html` | `generic_detail.html` | ✅ |
| `production/process_detail.html` | `generic_detail.html` | ✅ |
| `production/bom_detail.html` | `generic_detail.html` | ✅ |
| `production/product_order_detail.html` | `generic_detail.html` | ✅ |
| `production/transfer_to_line_detail.html` | `generic_detail.html` | ✅ |
| `production/performance_record_detail.html` | `generic_detail.html` | ✅ |

#### Frontend Templates - List Views

| فایل Template | Generic Template | Partials استفاده شده | JavaScript استفاده شده | وضعیت |
|---------------|------------------|---------------------|----------------------|--------|
| `production/machines.html` | `generic_list.html` | `pagination.html` | `table-export.js` | ✅ |
| `production/bom_list.html` | `generic_list.html` | `pagination.html` | `table-export.js` | ✅ |
| `production/transfer_to_line_list.html` | `generic_list.html` | `pagination.html` | `approval-actions.js` | ✅ |
| `production/performance_record_list.html` | `generic_list.html` | - | `approval-actions.js` | ✅ |
| `production/rework_document_list.html` | `generic_list.html` | - | `approval-actions.js` | ✅ |
| `production/qc_operations_list.html` | `generic_list.html` | - | `approval-actions.js`, `modal-dialogs.js` | ✅ |

#### Frontend Templates - Form Views

| فایل Template | Generic Template | JavaScript استفاده شده | وضعیت |
|---------------|------------------|----------------------|--------|
| `production/bom_form.html` | `generic_form.html` | `formset.js`, `cascading-dropdowns.js`, `item-filters.js` | ✅ |
| `production/process_form.html` | `generic_form.html` | `formset.js` | ✅ |
| `production/performance_record_form.html` | `generic_form.html` | `formset.js` | ✅ |
| `production/transfer_to_line_form.html` | `generic_form.html` | `formset.js`, `cascading-dropdowns.js` | ✅ |
| `production/rework_document_form.html` | `generic_form.html` | - | ✅ |

---

### ماژول `accounting` (31/34 view - 91% تکمیل شده)

#### Backend Views

| فایل | View | Base Class | Template | وضعیت |
|------|------|------------|----------|--------|
| `accounting/views/accounts.py` | `AccountListView` | `BaseListView` | `generic_list.html` | ✅ |
| `accounting/views/accounts.py` | `AccountCreateView` | `BaseCreateView` | `generic_form.html` | ✅ |
| `accounting/views/accounts.py` | `AccountUpdateView` | `BaseUpdateView` | `generic_form.html` | ✅ |
| `accounting/views/accounts.py` | `AccountDetailView` | `BaseDetailView` | `generic_detail.html` | ✅ |
| `accounting/views/accounts.py` | `AccountDeleteView` | `BaseDeleteView` | `generic_confirm_delete.html` | ✅ |
| `accounting/views/fiscal_years.py` | `FiscalYearListView` | `BaseListView` | `generic_list.html` | ✅ |
| `accounting/views/fiscal_years.py` | `FiscalYearCreateView` | `BaseCreateView` | `generic_form.html` | ✅ |
| `accounting/views/fiscal_years.py` | `FiscalYearUpdateView` | `BaseUpdateView` | `generic_form.html` | ✅ |
| `accounting/views/fiscal_years.py` | `FiscalYearDetailView` | `BaseDetailView` | `generic_detail.html` | ✅ |
| `accounting/views/fiscal_years.py` | `FiscalYearDeleteView` | `BaseDeleteView` | `generic_confirm_delete.html` | ✅ |
| `accounting/views/tafsili_accounts.py` | `TafsiliAccountListView` | `BaseListView` | `generic_list.html` | ✅ |
| `accounting/views/tafsili_accounts.py` | `TafsiliAccountCreateView` | `BaseCreateView` | `generic_form.html` | ✅ |
| `accounting/views/tafsili_accounts.py` | `TafsiliAccountUpdateView` | `BaseUpdateView` | `generic_form.html` | ✅ |
| `accounting/views/tafsili_accounts.py` | `TafsiliAccountDetailView` | `BaseDetailView` | `generic_detail.html` | ✅ |
| `accounting/views/tafsili_accounts.py` | `TafsiliAccountDeleteView` | `BaseDeleteView` | `generic_confirm_delete.html` | ✅ |
| `accounting/views/sub_accounts.py` | `SubAccountListView` | `BaseListView` | `generic_list.html` | ✅ |
| `accounting/views/sub_accounts.py` | `SubAccountCreateView` | `BaseCreateView` | `generic_form.html` | ✅ |
| `accounting/views/sub_accounts.py` | `SubAccountUpdateView` | `BaseUpdateView` | `generic_form.html` | ✅ |
| `accounting/views/sub_accounts.py` | `SubAccountDetailView` | `BaseDetailView` | `generic_detail.html` | ✅ |
| `accounting/views/sub_accounts.py` | `SubAccountDeleteView` | `BaseDeleteView` | `generic_confirm_delete.html` | ✅ |
| `accounting/views/gl_accounts.py` | `GLAccountListView` | `BaseListView` | `generic_list.html` | ✅ |
| `accounting/views/gl_accounts.py` | `GLAccountCreateView` | `BaseCreateView` | `generic_form.html` | ✅ |
| `accounting/views/gl_accounts.py` | `GLAccountUpdateView` | `BaseUpdateView` | `generic_form.html` | ✅ |
| `accounting/views/gl_accounts.py` | `GLAccountDetailView` | `BaseDetailView` | `generic_detail.html` | ✅ |
| `accounting/views/gl_accounts.py` | `GLAccountDeleteView` | `BaseDeleteView` | `generic_confirm_delete.html` | ✅ |
| `accounting/views/document_attachments.py` | `DocumentAttachmentListView` | `BaseListView` | `generic_list.html` | ✅ |

#### Frontend Templates - Detail Views

| فایل Template | Generic Template | وضعیت |
|---------------|------------------|--------|
| `accounting/account_detail.html` | `generic_detail.html` | ✅ |
| `accounting/fiscal_year_detail.html` | `generic_detail.html` | ✅ |
| `accounting/gl_account_detail.html` | `generic_detail.html` | ✅ |
| `accounting/sub_account_detail.html` | `generic_detail.html` | ✅ |
| `accounting/tafsili_account_detail.html` | `generic_detail.html` | ✅ |

#### Frontend Templates - List Views

| فایل Template | Generic Template | وضعیت |
|---------------|------------------|--------|
| `accounting/treasury/accounts.html` | `generic_list.html` | ✅ |
| `accounting/parties/accounts.html` | `generic_list.html` | ✅ |
| `accounting/parties/list.html` | `generic_list.html` | ✅ |
| `accounting/income_expense/categories.html` | `generic_list.html` | ✅ |
| `accounting/income_expense/cost_centers.html` | `generic_list.html` | ✅ |
| `accounting/attachments/list.html` | `generic_list.html` | ✅ |

#### Frontend Templates - Form Views

| فایل Template | Generic Template | وضعیت |
|---------------|------------------|--------|
| `accounting/treasury/account_form.html` | `generic_form.html` | ✅ |
| `accounting/parties/party_form.html` | `generic_form.html` | ✅ |
| `accounting/parties/party_account_form.html` | `generic_form.html` | ✅ |
| `accounting/income_expense/category_form.html` | `generic_form.html` | ✅ |
| `accounting/income_expense/cost_center_form.html` | `generic_form.html` | ✅ |
| `accounting/attachments/upload.html` | `generic_form.html` | ✅ |

---

### ماژول `ticketing` (19/22 view - 86% تکمیل شده)

#### Backend Views

| فایل | View | Base Class | Template | وضعیت |
|------|------|------------|----------|--------|
| `ticketing/views/categories.py` | `TicketCategoryListView` | `BaseListView` | `generic_list.html` | ✅ |
| `ticketing/views/categories.py` | `TicketCategoryCreateView` | `BaseFormsetCreateView` | `generic_form.html` | ✅ |
| `ticketing/views/categories.py` | `TicketCategoryUpdateView` | `BaseFormsetUpdateView` | `generic_form.html` | ✅ |
| `ticketing/views/categories.py` | `TicketCategoryDetailView` | `BaseDetailView` | `generic_detail.html` | ✅ |
| `ticketing/views/categories.py` | `TicketCategoryDeleteView` | `BaseDeleteView` | `generic_confirm_delete.html` | ✅ |
| `ticketing/views/subcategories.py` | `TicketSubcategoryListView` | `BaseListView` | `generic_list.html` | ✅ |
| `ticketing/views/subcategories.py` | `TicketSubcategoryCreateView` | `BaseFormsetCreateView` | `generic_form.html` | ✅ |
| `ticketing/views/subcategories.py` | `TicketSubcategoryUpdateView` | `BaseFormsetUpdateView` | `generic_form.html` | ✅ |
| `ticketing/views/subcategories.py` | `TicketSubcategoryDetailView` | `BaseDetailView` | `generic_detail.html` | ✅ |
| `ticketing/views/subcategories.py` | `TicketSubcategoryDeleteView` | `BaseDeleteView` | `generic_confirm_delete.html` | ✅ |
| `ticketing/views/templates.py` | `TicketTemplateListView` | `BaseListView` | `generic_list.html` | ✅ |
| `ticketing/views/templates.py` | `TicketTemplateCreateView` | `BaseMultipleFormsetCreateView` | `generic_form.html` | ✅ |
| `ticketing/views/templates.py` | `TicketTemplateUpdateView` | `BaseMultipleFormsetUpdateView` | `generic_form.html` | ✅ |
| `ticketing/views/templates.py` | `TicketTemplateDetailView` | `BaseDetailView` | `generic_detail.html` | ✅ |
| `ticketing/views/templates.py` | `TicketTemplateDeleteView` | `BaseDeleteView` | `generic_confirm_delete.html` | ✅ |
| `ticketing/views/tickets.py` | `TicketListView` | `BaseListView` | `generic_list.html` | ✅ |
| `ticketing/views/tickets.py` | `TicketCreateView` | `BaseCreateView` | `generic_form.html` | ✅ |
| `ticketing/views/tickets.py` | `TicketDetailView` | `BaseDetailView` | `generic_detail.html` | ✅ |
| `ticketing/views/tickets.py` | `TicketEditView` | `BaseUpdateView` | `generic_form.html` | ✅ |

#### Frontend Templates - Detail Views

| فایل Template | Generic Template | وضعیت |
|---------------|------------------|--------|
| `ticketing/category_detail.html` | `generic_detail.html` | ✅ |
| `ticketing/subcategory_detail.html` | `generic_detail.html` | ✅ |
| `ticketing/template_detail.html` | `generic_detail.html` | ✅ |
| `ticketing/ticket_detail.html` | `generic_detail.html` | ✅ |

#### Frontend Templates - List Views

| فایل Template | Generic Template | Partials استفاده شده | JavaScript استفاده شده | وضعیت |
|---------------|------------------|---------------------|----------------------|--------|
| `ticketing/templates_list.html` | `generic_list.html` | `row_actions.html`, `pagination.html` | - | ✅ |
| `ticketing/categories_list.html` | `generic_list.html` | `row_actions.html`, `pagination.html` | - | ✅ |
| `ticketing/subcategories_list.html` | `generic_list.html` | `row_actions.html`, `pagination.html` | - | ✅ |

#### Frontend Templates - Form Views

| فایل Template | Generic Template | JavaScript استفاده شده | وضعیت |
|---------------|------------------|----------------------|--------|
| `ticketing/template_form.html` | `generic_form.html` | `formset.js` | ✅ |
| `ticketing/subcategory_form.html` | `generic_form.html` | `formset.js` | ✅ |

---

### ماژول `qc` (6/6 view - 100% تکمیل شده)

#### Backend Views

| فایل | View | Base Class | Template | وضعیت |
|------|------|------------|----------|--------|
| `qc/views/inspections.py` | `TemporaryReceiptQCListView` | `BaseListView` | `generic_list.html` | ✅ |

---

## 📊 خلاصه Refactoring بر اساس نوع

### Backend Refactoring

| نوع Refactoring | تعداد فایل | مثال |
|-----------------|-----------|------|
| **ListView → BaseListView** | 50+ | `ItemTypeListView(BaseListView)` |
| **CreateView → BaseCreateView** | 30+ | `ItemTypeCreateView(BaseCreateView)` |
| **UpdateView → BaseUpdateView** | 30+ | `ItemTypeUpdateView(BaseUpdateView)` |
| **DeleteView → BaseDeleteView** | 30+ | `ItemTypeDeleteView(BaseDeleteView)` |
| **DetailView → BaseDetailView** | 39+ | `ItemTypeDetailView(BaseDetailView)` |
| **Formset Views → BaseFormsetCreateView/UpdateView** | 10+ | `BOMCreateView(BaseFormsetCreateView)` |
| **Document Views → BaseDocumentListView/CreateView/UpdateView** | 20+ | `ReceiptListView(BaseDocumentListView)` |
| **Nested Formset Views → BaseNestedFormsetCreateView/UpdateView** | 2 | `BOMCreateView(BaseNestedFormsetCreateView)` |
| **Multiple Formset Views → BaseMultipleFormsetCreateView/UpdateView** | 3 | `TicketTemplateCreateView(BaseMultipleFormsetCreateView)` |

### Frontend Refactoring

| نوع Refactoring | تعداد فایل | مثال |
|-----------------|-----------|------|
| **Detail Templates → generic_detail.html** | 39 | `itemtype_detail.html` extends `generic_detail.html` |
| **List Templates → generic_list.html** | 72+ | `item_types.html` extends `generic_list.html` |
| **Form Templates → generic_form.html** | 30+ | `item_form.html` extends `generic_form.html` |
| **Delete Templates → generic_confirm_delete.html** | 30+ | استفاده خودکار از `generic_confirm_delete.html` |
| **Row Actions → row_actions.html partial** | 9 | استفاده از `{% include 'shared/partials/row_actions.html' %}` |
| **Pagination → pagination.html partial** | 6 | استفاده از `{% include 'shared/partials/pagination.html' %}` |
| **JavaScript Formset → formset.js** | 10 | استفاده از `formset.js` به جای inline JavaScript |
| **JavaScript Cascading → cascading-dropdowns.js** | 7 | استفاده از `cascading-dropdowns.js` |
| **JavaScript Table Export → table-export.js** | 17+ | استفاده از `table-export.js` |
| **JavaScript Approval → approval-actions.js** | 4 | استفاده از `approval-actions.js` |
| **JavaScript Modal → modal-dialogs.js** | 3 | استفاده از `modal-dialogs.js` |
| **CSS Inline → shared.css** | 30+ | حذف inline styles و استفاده از `shared.css` |

---

## ⚠️ قوانین اجباری

### 🔴 قانون 1: استفاده از Base Classes

**❌ ممنوع**: نوشتن ListView, CreateView, UpdateView, DeleteView, DetailView از صفر

**✅ الزامی**: استفاده از Base Classes موجود در `shared/views/base.py`

```python
# ❌ اشتباه
class ItemTypeListView(ListView):
    def get_queryset(self):
        # 50+ خط کد تکراری
    def get_context_data(self, **kwargs):
        # 50+ خط کد تکراری

# ✅ درست
from shared.views.base import BaseListView

class ItemTypeListView(BaseListView):
    model = ItemType
    search_fields = ['name', 'public_code']
    filter_fields = ['is_enabled']
    feature_code = 'inventory.master.item_types'
```

### 🔴 قانون 2: استفاده از Generic Templates

**❌ ممنوع**: نوشتن template جدید برای List/Form/Detail/Delete Views

**✅ الزامی**: استفاده از Generic Templates موجود

```django
{# ❌ اشتباه #}
{% extends "shared/base.html" %}
<div class="container-fluid">
  <!-- 200+ خط کد تکراری -->
</div>

{# ✅ درست #}
{% extends "shared/generic/generic_list.html" %}
{% block table_headers %}
  <!-- فقط headers را override می‌کنیم -->
{% endblock %}
```

### 🔴 قانون 3: استفاده از JavaScript مشترک

**❌ ممنوع**: نوشتن JavaScript inline برای formset, cascading dropdowns, table export

**✅ الزامی**: استفاده از فایل‌های JavaScript مشترک

```html
<!-- ❌ اشتباه -->
<script>
function addFormsetRow(prefix) {
  // 50+ خط کد تکراری
}
</script>

<!-- ✅ درست -->
{% load static %}
<script src="{% static 'js/formset.js' %}"></script>
<script>
document.addEventListener('DOMContentLoaded', function() {
  initFormset('formset', '#formset-template-row');
});
</script>
```

### 🔴 قانون 4: استفاده از CSS مشترک

**❌ ممنوع**: استفاده از inline styles یا `<style>` tags در templates

**✅ الزامی**: استفاده از CSS classes از `shared.css`

```html
<!-- ❌ اشتباه -->
<div style="padding: 20px; margin: 10px;">
<style>
.custom-class { ... }
</style>

<!-- ✅ درست -->
<div class="container-fluid">
<!-- استفاده از classes موجود در shared.css -->
```

### 🔴 قانون 5: استفاده از Filter Functions

**❌ ممنوع**: نوشتن منطق فیلتر و جستجو در هر view

**✅ الزامی**: استفاده از توابع موجود در `shared/filters.py`

```python
# ❌ اشتباه
def get_queryset(self):
    queryset = super().get_queryset()
    search = self.request.GET.get('search', '').strip()
    if search:
        queryset = queryset.filter(Q(name__icontains=search))
    # ...

# ✅ درست
from shared.filters import apply_search

def get_queryset(self):
    queryset = super().get_queryset()
    queryset = apply_search(queryset, self.request.GET.get('search', ''), ['name'])
    return queryset
```

### 🔴 قانون 6: استفاده از Template Partials

**❌ ممنوع**: نوشتن row actions, pagination, filter panel در هر template

**✅ الزامی**: استفاده از Partials موجود

```django
{# ❌ اشتباه #}
<td>
  <a href="{% url 'edit' object.pk %}">Edit</a>
  <a href="{% url 'delete' object.pk %}">Delete</a>
</td>

{# ✅ درست #}
{% include 'shared/partials/row_actions.html' with object=object feature_code=feature_code %}
```

---

## 📚 فایل‌های اشتراکی موجود

### Backend Files

#### 1. Base View Classes (`shared/views/base.py`)

| کلاس | استفاده | مثال |
|------|---------|------|
| `BaseListView` | List Views | `ItemTypeListView(BaseListView)` |
| `BaseCreateView` | Create Views | `ItemTypeCreateView(BaseCreateView)` |
| `BaseUpdateView` | Update Views | `ItemTypeUpdateView(BaseUpdateView)` |
| `BaseDeleteView` | Delete Views | `ItemTypeDeleteView(BaseDeleteView)` |
| `BaseDetailView` | Detail Views | `ItemTypeDetailView(BaseDetailView)` |
| `BaseFormsetCreateView` | Create با Formset | `BOMCreateView(BaseFormsetCreateView)` |
| `BaseFormsetUpdateView` | Update با Formset | `BOMUpdateView(BaseFormsetUpdateView)` |
| `BaseDocumentListView` | Document List Views | `ReceiptListView(BaseDocumentListView)` |
| `BaseDocumentCreateView` | Document Create Views | `ReceiptCreateView(BaseDocumentCreateView)` |
| `BaseDocumentUpdateView` | Document Update Views | `ReceiptUpdateView(BaseDocumentUpdateView)` |
| `BaseNestedFormsetCreateView` | Nested Formsets | `BOMCreateView(BaseNestedFormsetCreateView)` |
| `BaseNestedFormsetUpdateView` | Nested Formsets Update | `BOMUpdateView(BaseNestedFormsetUpdateView)` |
| `BaseMultipleFormsetCreateView` | Multiple Formsets | `TicketTemplateCreateView(BaseMultipleFormsetCreateView)` |

#### 2. Filter Functions (`shared/filters.py`)

| تابع | استفاده |
|------|---------|
| `apply_search(queryset, search_query, fields)` | جستجو در چند فیلد |
| `apply_status_filter(queryset, status_value)` | فیلتر وضعیت |
| `apply_company_filter(queryset, company_id)` | فیلتر شرکت |
| `apply_date_range_filter(queryset, date_from, date_to, field_name)` | فیلتر بازه تاریخ |
| `apply_multi_field_filter(queryset, request, filter_map)` | فیلتر چند فیلد |

#### 3. Mixins (`shared/mixins.py`)

| Mixin | استفاده |
|------|---------|
| `PermissionFilterMixin` | فیلتر queryset بر اساس permissions |
| `CompanyScopedViewMixin` | فیلتر بر اساس active company |
| `AutoSetFieldsMixin` | auto-set company_id, created_by, edited_by |
| `SuccessMessageMixin` | نمایش success message |
| `FeaturePermissionRequiredMixin` | بررسی permissions |

#### 4. Base Form Classes (`shared/forms/base.py`)

| کلاس | استفاده |
|------|---------|
| `BaseModelForm` | فرم پایه با auto widget styling |
| `BaseFormset` | helper class برای formsets |

### Frontend Files

#### 1. JavaScript Files (`static/js/`)

| فایل | توابع اصلی | استفاده |
|------|-----------|---------|
| `formset.js` | `addFormsetRow()`, `removeFormsetRow()`, `initFormset()` | مدیریت formsets |
| `cascading-dropdowns.js` | `initCascadingDropdown()` | cascading dropdowns |
| `table-export.js` | `exportTableToCSV()`, `exportTableToExcel()`, `printTable()` | export جدول |
| `form-helpers.js` | `initAutoSubmit()`, `validateForm()` | helper functions |
| `item-filters.js` | `filterItemsForRow()`, `loadCategoriesForRow()` | فیلترهای item |
| `formset-table.js` | مدیریت grid layout | formset tables |
| `approval-actions.js` | `approveObject()`, `rejectObject()` | approve/reject |
| `modal-dialogs.js` | `showModal()`, `showNotes()` | modal dialogs |
| `common-actions.js` | `printPage()`, `confirmAction()` | actions مشترک |

#### 2. CSS Files (`static/css/`)

| فایل | استفاده |
|------|---------|
| `shared.css` | تمام استایل‌های مشترک (بدون inline styles) |

#### 3. Template Partials (`templates/shared/partials/`)

| فایل | استفاده |
|------|---------|
| `row_actions.html` | نمایش دکمه‌های action برای هر row |
| `filter_panel.html` | پنل فیلتر مشترک |
| `stats_cards.html` | نمایش کارت‌های آمار |
| `pagination.html` | pagination مشترک |
| `empty_state.html` | نمایش empty state |

#### 4. Generic Templates (`templates/shared/generic/`)

| فایل | استفاده |
|------|---------|
| `generic_list.html` | template مشترک برای List Views |
| `generic_form.html` | template مشترک برای Create/Update Views |
| `generic_detail.html` | template مشترک برای Detail Views |
| `generic_confirm_delete.html` | template مشترک برای Delete Views |

---

## 📖 نحوه استفاده از Base Classes

### مثال 1: ListView ساده

```python
from shared.views.base import BaseListView
from inventory.models import ItemType

class ItemTypeListView(BaseListView):
    model = ItemType
    search_fields = ['name', 'public_code']  # فیلدهای قابل جستجو
    filter_fields = ['is_enabled']  # فیلدهای قابل فیلتر
    feature_code = 'inventory.master.item_types'  # برای permissions
    default_order_by = 'public_code'  # مرتب‌سازی پیش‌فرض
    
    def get_breadcrumbs(self):
        return [
            {'label': _('Inventory'), 'url': None},
            {'label': _('Item Types'), 'url': None},
        ]
```

**نکات مهم**:
- فقط `model`, `search_fields`, `filter_fields`, `feature_code` را مشخص می‌کنیم
- BaseListView به صورت خودکار:
  - فیلتر بر اساس `active_company_id`
  - اعمال search و filters
  - تنظیم context (breadcrumbs, page_title, create_url, etc.)
  - pagination
  - permission checking

### مثال 2: CreateView ساده

```python
from shared.views.base import BaseCreateView
from inventory.models import ItemType
from inventory.forms import ItemTypeForm

class ItemTypeCreateView(BaseCreateView):
    model = ItemType
    form_class = ItemTypeForm
    success_url = reverse_lazy('inventory:item_types')
    feature_code = 'inventory.master.item_types'
    success_message = _('Item type created successfully.')
    
    def get_breadcrumbs(self):
        return [
            {'label': _('Inventory'), 'url': reverse('inventory:item_types')},
            {'label': _('Create Item Type'), 'url': None},
        ]
```

**نکات مهم**:
- BaseCreateView به صورت خودکار:
  - تنظیم `company_id` از `active_company_id`
  - تنظیم `created_by` از `request.user`
  - نمایش success message
  - تنظیم context (breadcrumbs, form_title, cancel_url)

### مثال 3: ListView با Formset

```python
from shared.views.base import BaseFormsetCreateView
from production.models import BOM
from production.forms import BOMForm, BOMMaterialLineFormSet

class BOMCreateView(BaseFormsetCreateView):
    model = BOM
    form_class = BOMForm
    formset_class = BOMMaterialLineFormSet
    formset_prefix = 'materials'
    success_url = reverse_lazy('production:bom_list')
    feature_code = 'production.bom'
    
    def get_formset_kwargs(self):
        kwargs = super().get_formset_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        return kwargs
```

**نکات مهم**:
- BaseFormsetCreateView به صورت خودکار:
  - مدیریت formset در context
  - ذخیره formset با main object
  - Transaction safety
  - Error handling

### مثال 4: Document ListView (با Stats)

```python
from shared.views.base import BaseDocumentListView
from inventory.models import ReceiptPermanent

class ReceiptPermanentListView(BaseDocumentListView):
    model = ReceiptPermanent
    feature_code = 'inventory.receipts.permanent'
    prefetch_lines = True  # prefetch lines برای performance
    stats_enabled = True  # فعال کردن stats
    
    def get_stats(self):
        """Override برای stats سفارشی"""
        company_id = self.request.session.get('active_company_id')
        if not company_id:
            return {}
        
        base_qs = self.model.objects.filter(company_id=company_id)
        return {
            'total': base_qs.count(),
            'draft': base_qs.filter(status='draft').count(),
            'confirmed': base_qs.filter(status='confirmed').count(),
        }
```

### مثال 5: Hook Methods

Base Classes از hook methods پشتیبانی می‌کنند که می‌توانید override کنید:

```python
class CustomListView(BaseListView):
    model = MyModel
    
    # Override برای queryset سفارشی
    def get_queryset(self):
        queryset = super().get_queryset()
        # منطق سفارشی
        return queryset
    
    # Override برای prefetch_related
    def get_prefetch_related(self):
        return ['related_field', 'another_field']
    
    # Override برای select_related
    def get_select_related(self):
        return ['foreign_key_field']
    
    # Override برای فیلترهای سفارشی
    def apply_custom_filters(self, queryset):
        # منطق فیلتر سفارشی
        return queryset
    
    # Override برای breadcrumbs
    def get_breadcrumbs(self):
        return [...]
    
    # Override برای page title
    def get_page_title(self):
        return _('Custom Title')
    
    # Override برای stats
    def get_stats(self):
        return {'total': 100}
```

---

## 💻 نحوه استفاده از JavaScript مشترک

### مثال 1: Formset Management

```html
{% load static %}
<script src="{% static 'js/formset.js' %}"></script>
<script>
document.addEventListener('DOMContentLoaded', function() {
    // Initialize formset
    initFormset('materials', '#material-template-row', {
        minRows: 1,
        maxRows: 100,
        onAddRow: function(row) {
            // Custom logic after adding row
            console.log('Row added:', row);
        },
        onRemoveRow: function(row) {
            // Custom logic after removing row
            console.log('Row removed:', row);
        }
    });
});
</script>
```

### مثال 2: Cascading Dropdowns

```html
{% load static %}
<script src="{% static 'js/cascading-dropdowns.js' %}"></script>
<script>
document.addEventListener('DOMContentLoaded', function() {
    // Initialize cascading dropdown
    initCascadingDropdown(
        '#id_item_type',  // Parent select
        '#id_item_category',  // Child select
        '/inventory/api/filtered-categories/',  // API URL
        {
            parentField: 'type_id',  // Query parameter name
            placeholder: '--- Select Category ---',
            onChange: function(selectedValue) {
                // Custom logic after change
                console.log('Category selected:', selectedValue);
            }
        }
    );
});
</script>
```

### مثال 3: Table Export

```html
{% load static %}
<script src="{% static 'js/table-export.js' %}"></script>
<script>
// Export to CSV
document.getElementById('export-csv-btn').addEventListener('click', function() {
    exportTableToCSV('data-table', 'export.csv', {
        skipHiddenColumns: true
    });
});

// Export to Excel
document.getElementById('export-excel-btn').addEventListener('click', function() {
    exportTableToExcel('data-table', 'export.xlsx');
});

// Print table
document.getElementById('print-btn').addEventListener('click', function() {
    printTable('data-table', {
        title: 'Report Title',
        showDate: true
    });
});
</script>
```

### مثال 4: Approval Actions

```html
{% load static %}
<script src="{% static 'js/approval-actions.js' %}"></script>
<script>
document.addEventListener('DOMContentLoaded', function() {
    // Approve button
    document.querySelectorAll('.approve-btn').forEach(function(btn) {
        btn.addEventListener('click', function() {
            const objectId = this.dataset.objectId;
            approveObject(objectId, '/api/approve/', {
                onSuccess: function() {
                    location.reload();
                }
            });
        });
    });
    
    // Reject button
    document.querySelectorAll('.reject-btn').forEach(function(btn) {
        btn.addEventListener('click', function() {
            const objectId = this.dataset.objectId;
            rejectObject(objectId, '/api/reject/', {
                requireNotes: true,
                onSuccess: function() {
                    location.reload();
                }
            });
        });
    });
});
</script>
```

---

## 🎨 نحوه استفاده از Templateهای مشترک

### مثال 1: List View Template

```django
{% extends "shared/generic/generic_list.html" %}

{% block table_headers %}
<th>Name</th>
<th>Code</th>
<th>Status</th>
<th>Actions</th>
{% endblock %}

{% block table_rows %}
{% for object in object_list %}
<tr>
    <td>{{ object.name }}</td>
    <td>{{ object.public_code }}</td>
    <td>
        {% if object.is_enabled %}
            <span class="badge badge-success">Active</span>
        {% else %}
            <span class="badge badge-danger">Inactive</span>
        {% endif %}
    </td>
    <td>
        {% include 'shared/partials/row_actions.html' with object=object feature_code=feature_code %}
    </td>
</tr>
{% endfor %}
{% endblock %}
```

**نکات مهم**:
- فقط `table_headers` و `table_rows` را override می‌کنیم
- بقیه (filter panel, pagination, empty state) به صورت خودکار از generic template استفاده می‌شود

### مثال 2: Form View Template

```django
{% extends "shared/generic/generic_form.html" %}

{% block form_sections %}
<div class="form-section">
    <h3>Basic Information</h3>
    <div class="row">
        <div class="col-md-6">
            <div class="form-group">
                {{ form.name.label_tag }}
                {{ form.name }}
                {{ form.name.errors }}
            </div>
        </div>
        <div class="col-md-6">
            <div class="form-group">
                {{ form.public_code.label_tag }}
                {{ form.public_code }}
                {{ form.public_code.errors }}
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

**نکات مهم**:
- فقط `form_sections` را override می‌کنیم
- بقیه (breadcrumbs, form actions, error display) به صورت خودکار از generic template استفاده می‌شود

### مثال 3: Detail View Template

```django
{% extends "shared/generic/generic_detail.html" %}

{% block detail_sections %}
<div class="detail-section">
    <h3>Basic Information</h3>
    <div class="detail-field">
        <label>Name</label>
        <div class="readonly-field">{{ object.name }}</div>
    </div>
    <div class="detail-field">
        <label>Code</label>
        <div class="readonly-field">{{ object.public_code }}</div>
    </div>
</div>

<div class="detail-section">
    <h3>Audit Information</h3>
    <div class="detail-field">
        <label>Created By</label>
        <div class="readonly-field">{{ object.created_by }}</div>
    </div>
    <div class="detail-field">
        <label>Created At</label>
        <div class="readonly-field">{{ object.created_at|date:"Y-m-d H:i" }}</div>
    </div>
</div>
{% endblock %}
```

**نکات مهم**:
- فقط `detail_sections` را override می‌کنیم
- بقیه (breadcrumbs, info banner, action buttons) به صورت خودکار از generic template استفاده می‌شود

---

## 📝 استانداردهای کدنویسی

### 1. نام‌گذاری متغیرها

**✅ درست**: نام‌های واضح و قابل فهم
```python
item_type_list = ItemType.objects.all()
user_permissions = get_user_feature_permissions(user, company_id)
```

**❌ اشتباه**: نام‌های مبهم یا مخفف
```python
itl = ItemType.objects.all()
up = get_user_feature_permissions(user, company_id)
```

### 2. استفاده از Best Practices

**✅ درست**: استفاده از Django best practices
```python
# استفاده از select_related برای foreign keys
queryset = Item.objects.select_related('category', 'subcategory')

# استفاده از prefetch_related برای many-to-many
queryset = Receipt.objects.prefetch_related('lines')
```

**❌ اشتباه**: N+1 queries
```python
# این باعث N+1 query می‌شود
for item in Item.objects.all():
    print(item.category.name)  # Query برای هر item!
```

### 3. Error Handling

**✅ درست**: مدیریت خطاها به درستی
```python
def get_queryset(self):
    try:
        queryset = super().get_queryset()
        return queryset
    except Exception as e:
        logger.error(f"Error in get_queryset: {e}")
        return self.model.objects.none()
```

**❌ اشتباه**: نادیده گرفتن خطاها
```python
def get_queryset(self):
    queryset = super().get_queryset()  # اگر خطا بدهد، crash می‌کند
    return queryset
```

### 4. Comments و Documentation

**✅ درست**: توضیح منطق پیچیده
```python
def get_stats(self):
    """
    Calculate statistics for summary cards.
    
    Returns:
        dict: Dictionary with stats keys and values
    """
    # Filter by active company for security
    company_id = self.request.session.get('active_company_id')
    if not company_id:
        return {}
    
    # Calculate stats efficiently using aggregation
    base_qs = self.model.objects.filter(company_id=company_id)
    return {
        'total': base_qs.count(),
        'draft': base_qs.filter(status='draft').count(),
    }
```

**❌ اشتباه**: عدم توضیح منطق پیچیده
```python
def get_stats(self):
    company_id = self.request.session.get('active_company_id')
    if not company_id:
        return {}
    base_qs = self.model.objects.filter(company_id=company_id)
    return {'total': base_qs.count(), 'draft': base_qs.filter(status='draft').count()}
```

---

## 🧪 استانداردهای Testing

### فلسفه Testing در پروژه

تست‌نویسی **الزامی** برای تمام feature های جدید و تغییرات مهم است. هدف:
- ✅ اطمینان از صحت عملکرد کد
- ✅ جلوگیری از Regression Bugs
- ✅ مستندسازی رفتار مورد انتظار
- ✅ Refactoring ایمن

### 1. انواع تست‌ها

#### Unit Tests

تست واحدهای کوچک و مستقل کد (Models, Forms, Utilities)

```python
# tests/test_models.py
from django.test import TestCase
from inventory.models import ItemType
from shared.models import Company

class ItemTypeModelTest(TestCase):
    """Test suite for ItemType model"""
    
    def setUp(self):
        """Setup test data before each test"""
        self.company = Company.objects.create(
            name='Test Company',
            public_code='TC001'
        )
        
    def test_item_type_creation(self):
        """Test creating an item type successfully"""
        item_type = ItemType.objects.create(
            name='Raw Material',
            public_code='RM001',
            company=self.company
        )
        
        self.assertEqual(item_type.name, 'Raw Material')
        self.assertEqual(item_type.public_code, 'RM001')
        self.assertTrue(item_type.is_enabled)
    
    def test_item_type_str_representation(self):
        """Test string representation of ItemType"""
        item_type = ItemType.objects.create(
            name='Raw Material',
            public_code='RM001',
            company=self.company
        )
        
        self.assertEqual(str(item_type), 'Raw Material (RM001)')
    
    def test_unique_code_per_company(self):
        """Test that public_code must be unique per company"""
        ItemType.objects.create(
            name='Type 1',
            public_code='T001',
            company=self.company
        )
        
        # Should raise IntegrityError
        with self.assertRaises(Exception):
            ItemType.objects.create(
                name='Type 2',
                public_code='T001',  # Duplicate code
                company=self.company
            )
```

#### Integration Tests

تست تعامل بین اجزای مختلف (Views, Forms, Database)

```python
# tests/test_views.py
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from inventory.models import ItemType
from shared.models import Company

User = get_user_model()

class ItemTypeViewTest(TestCase):
    """Test suite for ItemType views"""
    
    def setUp(self):
        """Setup test environment"""
        self.client = Client()
        
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        
        # Create test company
        self.company = Company.objects.create(
            name='Test Company',
            public_code='TC001'
        )
        
        # Login user
        self.client.login(username='testuser', password='testpass123')
        
        # Set active company in session
        session = self.client.session
        session['active_company_id'] = self.company.id
        session.save()
    
    def test_item_type_list_view_requires_login(self):
        """Test that list view requires authentication"""
        self.client.logout()
        
        response = self.client.get(reverse('inventory:item_types'))
        
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_item_type_list_view_displays_items(self):
        """Test that list view displays item types"""
        # Create test data
        ItemType.objects.create(
            name='Type 1',
            public_code='T001',
            company=self.company
        )
        ItemType.objects.create(
            name='Type 2',
            public_code='T002',
            company=self.company
        )
        
        response = self.client.get(reverse('inventory:item_types'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Type 1')
        self.assertContains(response, 'Type 2')
    
    def test_item_type_create_view_success(self):
        """Test creating item type through view"""
        data = {
            'name': 'New Type',
            'public_code': 'NT001',
            'is_enabled': True
        }
        
        response = self.client.post(
            reverse('inventory:item_type_create'),
            data=data
        )
        
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertTrue(
            ItemType.objects.filter(public_code='NT001').exists()
        )
    
    def test_item_type_search_functionality(self):
        """Test search in list view"""
        ItemType.objects.create(
            name='Search Test Type',
            public_code='ST001',
            company=self.company
        )
        
        response = self.client.get(
            reverse('inventory:item_types') + '?search=Search'
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Search Test Type')
```

#### Functional Tests

تست سناریوهای کامل از دیدگاه کاربر

```python
# tests/test_functional.py
from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class ItemTypeWorkflowTest(LiveServerTestCase):
    """End-to-end test for item type management workflow"""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium = webdriver.Chrome()
        cls.selenium.implicitly_wait(10)
    
    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()
    
    def test_complete_item_type_crud_workflow(self):
        """Test complete CRUD workflow for item types"""
        # Login
        self.selenium.get(f'{self.live_server_url}/login/')
        username_input = self.selenium.find_element(By.NAME, 'username')
        password_input = self.selenium.find_element(By.NAME, 'password')
        
        username_input.send_keys('testuser')
        password_input.send_keys('testpass123')
        
        self.selenium.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        
        # Navigate to item types
        self.selenium.get(f'{self.live_server_url}/inventory/item-types/')
        
        # Click create button
        create_btn = self.selenium.find_element(By.ID, 'create-btn')
        create_btn.click()
        
        # Fill form
        name_input = self.selenium.find_element(By.NAME, 'name')
        code_input = self.selenium.find_element(By.NAME, 'public_code')
        
        name_input.send_keys('Test Type')
        code_input.send_keys('TT001')
        
        # Submit
        submit_btn = self.selenium.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        submit_btn.click()
        
        # Verify success message
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'alert-success'))
        )
```

### 2. استانداردهای نوشتن تست

#### نام‌گذاری

```python
# ✅ درست: نام واضح که بیان می‌کند چه چیزی تست می‌شود
def test_item_type_creation_with_valid_data_should_succeed(self):
    pass

def test_item_type_creation_without_company_should_fail(self):
    pass

def test_search_returns_only_matching_items(self):
    pass

# ❌ اشتباه: نام مبهم
def test_item_type(self):
    pass

def test_1(self):
    pass
```

#### ساختار تست (AAA Pattern)

```python
def test_example(self):
    # Arrange - آماده‌سازی
    company = Company.objects.create(name='Test')
    
    # Act - اجرا
    item_type = ItemType.objects.create(
        name='Type',
        public_code='T001',
        company=company
    )
    
    # Assert - بررسی
    self.assertEqual(item_type.name, 'Type')
    self.assertTrue(item_type.is_enabled)
```

### 3. Test Coverage

**حداقل Coverage مورد انتظار**: 80%

```bash
# Run tests with coverage
python manage.py test --with-coverage

# Generate coverage report
coverage run --source='.' manage.py test
coverage report
coverage html  # HTML report در htmlcov/
```

### 4. Test Data Management

#### استفاده از Fixtures

```python
# fixtures/test_data.json
[
  {
    "model": "shared.company",
    "pk": 1,
    "fields": {
      "name": "Test Company",
      "public_code": "TC001"
    }
  }
]

# در تست
class MyTest(TestCase):
    fixtures = ['test_data.json']
```

#### استفاده از Factory Pattern

```python
# tests/factories.py
import factory
from factory.django import DjangoModelFactory
from inventory.models import ItemType
from shared.models import Company

class CompanyFactory(DjangoModelFactory):
    class Meta:
        model = Company
    
    name = factory.Sequence(lambda n: f'Company {n}')
    public_code = factory.Sequence(lambda n: f'C{n:03d}')

class ItemTypeFactory(DjangoModelFactory):
    class Meta:
        model = ItemType
    
    name = factory.Sequence(lambda n: f'Type {n}')
    public_code = factory.Sequence(lambda n: f'T{n:03d}')
    company = factory.SubFactory(CompanyFactory)
    is_enabled = True

# استفاده در تست
def test_with_factory(self):
    item_type = ItemTypeFactory.create()
    self.assertIsNotNone(item_type.id)
```

### 5. اجرای تست‌ها

```bash
# همه تست‌ها
python manage.py test

# تست‌های یک app خاص
python manage.py test inventory

# تست‌های یک فایل خاص
python manage.py test inventory.tests.test_models

# تست خاص
python manage.py test inventory.tests.test_models.ItemTypeModelTest.test_item_type_creation

# با verbose output
python manage.py test --verbosity=2

# فقط تست‌های failed را دوباره اجرا کن
python manage.py test --failed
```

### 6. Mocking و Test Doubles

```python
from unittest.mock import Mock, patch, MagicMock

class ExternalAPITest(TestCase):
    """Test interactions with external APIs"""
    
    @patch('inventory.services.external_api_call')
    def test_fetch_item_data_from_external_api(self, mock_api):
        """Test fetching item data with mocked external API"""
        # Setup mock
        mock_api.return_value = {
            'name': 'External Item',
            'code': 'EXT001'
        }
        
        # Call function
        result = fetch_item_from_external_source('EXT001')
        
        # Verify
        self.assertEqual(result['name'], 'External Item')
        mock_api.assert_called_once_with('EXT001')
```

### 7. Testing Best Practices

- ✅ **هر تست باید مستقل باشد** - وابستگی به ترتیب اجرا نداشته باشد
- ✅ **تست‌ها باید سریع باشند** - از in-memory database استفاده کنید
- ✅ **یک assertion در هر تست** - ترجیحاً یک concept را تست کنید
- ✅ **از setUp و tearDown استفاده کنید** - برای cleanup
- ✅ **تست failure scenarios** - نه فقط happy path
- ❌ **وابستگی به external services** - از mock استفاده کنید
- ❌ **تست‌های شکننده** - که با تغییرات جزئی fail می‌شوند

---

## 🔒 استانداردهای امنیتی

### 1. SQL Injection Prevention

#### ✅ استفاده امن از ORM

```python
# ✅ درست - استفاده از ORM
user_input = request.GET.get('search')
items = Item.objects.filter(name__icontains=user_input)

# ✅ درست - استفاده از parameterized queries
from django.db import connection
cursor = connection.cursor()
cursor.execute("SELECT * FROM items WHERE name = %s", [user_input])

# ❌ اشتباه - NEVER concatenate user input
cursor.execute(f"SELECT * FROM items WHERE name = '{user_input}'")  # UNSAFE!
```

### 2. XSS (Cross-Site Scripting) Prevention

#### استفاده صحیح از Templates

```django
{# ✅ درست - auto-escape فعال است #}
<p>{{ user_input }}</p>

{# ⚠️ فقط در صورت اطمینان کامل #}
<p>{{ trusted_html|safe }}</p>

{# ✅ درست - escape در JavaScript #}
<script>
var userName = "{{ user.name|escapejs }}";
</script>

{# ❌ اشتباه - NEVER این کار را انجام ندهید #}
<script>
var data = {{ user_data|safe }};  // UNSAFE!
</script>
```

#### Sanitize User Input

```python
from django.utils.html import escape, strip_tags

def process_user_input(user_input):
    """Sanitize user input before processing"""
    # Remove HTML tags
    clean_input = strip_tags(user_input)
    
    # Escape special characters
    safe_input = escape(clean_input)
    
    return safe_input
```

### 3. CSRF Protection

```python
# ✅ الزامی - همیشه از csrf_token استفاده کنید
```

```django
<form method="post">
    {% csrf_token %}
    <!-- form fields -->
</form>
```

```python
# برای AJAX requests
# در settings.py
CSRF_COOKIE_HTTPONLY = False  # اگر نیاز به access از JavaScript دارید

# در JavaScript
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

// در AJAX request
fetch('/api/endpoint/', {
    method: 'POST',
    headers: {
        'X-CSRFToken': csrftoken,
        'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
});
```

### 4. Authentication & Authorization

#### Password Security

```python
# settings.py

# ✅ استفاده از password validators
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# ✅ Password hashing algorithm
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
]
```

#### Permission Checking

```python
from django.contrib.auth.decorators import login_required, permission_required
from shared.decorators import feature_permission_required

# ✅ درست - بررسی authentication
@login_required
def my_view(request):
    pass

# ✅ درست - بررسی permission
@feature_permission_required('inventory.master.item_types', action='view')
def item_type_list(request):
    pass

# ✅ درست - بررسی در view
from shared.views.base import BaseListView

class ItemTypeListView(BaseListView):
    feature_code = 'inventory.master.item_types'  # Auto permission check
    
    def get_queryset(self):
        # فیلتر بر اساس company برای data isolation
        queryset = super().get_queryset()
        company_id = self.request.session.get('active_company_id')
        return queryset.filter(company_id=company_id)
```

### 5. Sensitive Data Protection

#### Environment Variables

```python
# ✅ درست - استفاده از environment variables
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')
DATABASE_PASSWORD = os.getenv('DB_PASSWORD')
API_KEY = os.getenv('EXTERNAL_API_KEY')

# ❌ اشتباه - NEVER hardcode secrets
SECRET_KEY = 'my-secret-key-123'  # NEVER!
```

#### Logging Sensitive Data

```python
import logging

logger = logging.getLogger(__name__)

# ✅ درست - فیلتر اطلاعات حساس
def process_payment(card_number, amount):
    masked_card = f"****-****-****-{card_number[-4:]}"
    logger.info(f"Processing payment: {masked_card}, amount: {amount}")
    
# ❌ اشتباه - NEVER log sensitive data
def process_payment(card_number, amount):
    logger.info(f"Payment: {card_number}, {amount}")  # NEVER!
```

### 6. File Upload Security

```python
from django.core.exceptions import ValidationError
import os

ALLOWED_EXTENSIONS = ['.pdf', '.jpg', '.jpeg', '.png', '.xlsx', '.docx']
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def validate_file_upload(uploaded_file):
    """Validate uploaded file"""
    # Check file size
    if uploaded_file.size > MAX_FILE_SIZE:
        raise ValidationError('File size exceeds 5MB limit')
    
    # Check file extension
    ext = os.path.splitext(uploaded_file.name)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValidationError(f'File type {ext} is not allowed')
    
    # Check actual file content (magic bytes)
    # بررسی واقعی نوع فایل، نه فقط extension
    import magic
    file_type = magic.from_buffer(uploaded_file.read(1024), mime=True)
    uploaded_file.seek(0)  # Reset file pointer
    
    allowed_mimes = ['image/jpeg', 'image/png', 'application/pdf']
    if file_type not in allowed_mimes:
        raise ValidationError('Invalid file type')
    
    return True
```

### 7. Security Headers

```python
# settings.py

# ✅ HTTPS enforcement
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# ✅ Security headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# ✅ HSTS (HTTP Strict Transport Security)
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

### 8. Rate Limiting

```python
from django.core.cache import cache
from django.http import HttpResponseForbidden

def rate_limit(max_requests=100, window=3600):
    """
    Rate limiting decorator
    
    Args:
        max_requests: Maximum number of requests
        window: Time window in seconds
    """
    def decorator(view_func):
        def wrapped_view(request, *args, **kwargs):
            # Get client IP
            ip = request.META.get('REMOTE_ADDR')
            cache_key = f'rate_limit_{ip}'
            
            # Get current request count
            count = cache.get(cache_key, 0)
            
            if count >= max_requests:
                return HttpResponseForbidden('Rate limit exceeded')
            
            # Increment counter
            cache.set(cache_key, count + 1, window)
            
            return view_func(request, *args, **kwargs)
        
        return wrapped_view
    return decorator

# استفاده
@rate_limit(max_requests=50, window=3600)
def api_endpoint(request):
    pass
```

### 9. Security Checklist

- [ ] همه user inputs را validate و sanitize کنید
- [ ] از ORM برای database queries استفاده کنید
- [ ] CSRF token در همه forms
- [ ] همیشه authentication و authorization را بررسی کنید
- [ ] secrets را در environment variables ذخیره کنید
- [ ] file uploads را validate کنید
- [ ] sensitive data را log نکنید
- [ ] HTTPS را enforce کنید
- [ ] security headers را تنظیم کنید
- [ ] rate limiting را پیاده‌سازی کنید
- [ ] dependencies را به‌روز نگه دارید
- [ ] security audit منظم انجام دهید

---

## 🌐 استانداردهای API

### 1. API Structure

#### URL Naming Convention

```python
# ✅ درست - استفاده از kebab-case و resource-oriented
/api/v1/item-types/
/api/v1/item-types/{id}/
/api/v1/inventory/items/
/api/v1/inventory/items/{id}/stock-level/

# ❌ اشتباه
/api/get_item_types/  # فعل در URL
/api/ItemTypes/  # PascalCase
/api/item_types/  # snake_case
```

#### HTTP Methods

```python
GET     /api/v1/items/          # List all items
GET     /api/v1/items/{id}/     # Get single item
POST    /api/v1/items/          # Create new item
PUT     /api/v1/items/{id}/     # Full update
PATCH   /api/v1/items/{id}/     # Partial update
DELETE  /api/v1/items/{id}/     # Delete item
```

### 2. Response Format

#### Success Response

```python
# List Response
{
    "status": "success",
    "data": {
        "items": [
            {
                "id": 1,
                "name": "Item 1",
                "code": "I001"
            },
            {
                "id": 2,
                "name": "Item 2",
                "code": "I002"
            }
        ],
        "pagination": {
            "total": 100,
            "page": 1,
            "per_page": 20,
            "total_pages": 5
        }
    },
    "message": "Items retrieved successfully"
}

# Single Resource Response
{
    "status": "success",
    "data": {
        "id": 1,
        "name": "Item 1",
        "code": "I001",
        "created_at": "2024-12-23T10:30:00Z"
    },
    "message": "Item retrieved successfully"
}

# Create/Update Response
{
    "status": "success",
    "data": {
        "id": 1,
        "name": "New Item",
        "code": "NI001"
    },
    "message": "Item created successfully"
}
```

#### Error Response

```python
# Validation Error (400)
{
    "status": "error",
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Validation failed",
        "details": {
            "name": ["This field is required"],
            "code": ["This code already exists"]
        }
    }
}

# Not Found (404)
{
    "status": "error",
    "error": {
        "code": "NOT_FOUND",
        "message": "Item with id 123 not found"
    }
}

# Unauthorized (401)
{
    "status": "error",
    "error": {
        "code": "UNAUTHORIZED",
        "message": "Authentication credentials were not provided"
    }
}

# Forbidden (403)
{
    "status": "error",
    "error": {
        "code": "FORBIDDEN",
        "message": "You don't have permission to perform this action"
    }
}

# Server Error (500)
{
    "status": "error",
    "error": {
        "code": "INTERNAL_SERVER_ERROR",
        "message": "An unexpected error occurred",
        "request_id": "abc-123-def"  # برای tracking
    }
}
```

### 3. HTTP Status Codes

```python
# Success
200 OK              # GET, PUT, PATCH successful
201 Created         # POST successful
204 No Content      # DELETE successful

# Client Errors
400 Bad Request     # Validation error
401 Unauthorized    # Authentication required
403 Forbidden       # Permission denied
404 Not Found       # Resource not found
409 Conflict        # Duplicate resource
422 Unprocessable   # Semantic error

# Server Errors
500 Internal Error  # Server error
503 Service Unavailable  # Temporary unavailable
```

### 4. API Base Classes

```python
# shared/views/api.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.paginator import Paginator

class BaseAPIView(APIView):
    """Base API view with common functionality"""
    
    def success_response(self, data, message="Success", status_code=status.HTTP_200_OK):
        """Standard success response"""
        return Response({
            'status': 'success',
            'data': data,
            'message': message
        }, status=status_code)
    
    def error_response(self, message, code="ERROR", details=None, status_code=status.HTTP_400_BAD_REQUEST):
        """Standard error response"""
        error_data = {
            'status': 'error',
            'error': {
                'code': code,
                'message': message
            }
        }
        
        if details:
            error_data['error']['details'] = details
        
        return Response(error_data, status=status_code)

class BaseListAPIView(BaseAPIView):
    """Base list API view with pagination"""
    
    model = None
    serializer_class = None
    paginate_by = 20
    
    def get_queryset(self):
        """Get base queryset"""
        company_id = self.request.session.get('active_company_id')
        if not company_id:
            return self.model.objects.none()
        
        return self.model.objects.filter(company_id=company_id)
    
    def get(self, request):
        """Handle GET request"""
        try:
            queryset = self.get_queryset()
            
            # Pagination
            page_number = request.GET.get('page', 1)
            paginator = Paginator(queryset, self.paginate_by)
            page_obj = paginator.get_page(page_number)
            
            # Serialize
            serializer = self.serializer_class(page_obj, many=True)
            
            return self.success_response({
                'items': serializer.data,
                'pagination': {
                    'total': paginator.count,
                    'page': page_obj.number,
                    'per_page': self.paginate_by,
                    'total_pages': paginator.num_pages
                }
            })
        except Exception as e:
            return self.error_response(
                message=str(e),
                code='INTERNAL_ERROR',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
```

### 5. Versioning

```python
# urls.py
from django.urls import path, include

urlpatterns = [
    path('api/v1/', include('api.v1.urls')),
    # در آینده:
    # path('api/v2/', include('api.v2.urls')),
]

# api/v1/urls.py
urlpatterns = [
    path('items/', ItemListAPIView.as_view(), name='api_item_list'),
    path('items/<int:pk>/', ItemDetailAPIView.as_view(), name='api_item_detail'),
]
```

### 6. Authentication

```python
# Token-based authentication
from rest_framework.authtoken.models import Token

# در view
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

class ItemAPIView(BaseAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # user authenticated
        pass
```

### 7. Filtering & Search

```python
class ItemListAPIView(BaseListAPIView):
    model = Item
    serializer_class = ItemSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Search
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(name__icontains=search)
        
        # Filter by category
        category_id = self.request.GET.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        # Sort
        sort_by = self.request.GET.get('sort', 'name')
        queryset = queryset.order_by(sort_by)
        
        return queryset
```

### 8. API Documentation

استفاده از drf-spectacular برای auto-generated documentation:

```python
# settings.py
INSTALLED_APPS = [
    ...
    'drf_spectacular',
]

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'ERP API',
    'DESCRIPTION': 'ERP System API Documentation',
    'VERSION': '1.0.0',
}

# urls.py
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
```

---

## 💾 راهنمای Database & Migration

### 1. Migration Best Practices

#### ایجاد Migration

```bash
# ایجاد migration جدید
python manage.py makemigrations

# ایجاد migration با نام مشخص
python manage.py makemigrations --name add_item_code_field

# بررسی migrations بدون اعمال
python manage.py migrate --plan

# اعمال migrations
python manage.py migrate

# اعمال migration خاص
python manage.py migrate inventory 0005
```

#### نوشتن Migration ایمن

```python
# ✅ درست - Migration با قابلیت reverse
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('inventory', '0004_previous_migration'),
    ]
    
    operations = [
        migrations.AddField(
            model_name='item',
            name='sku',
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
    ]

# ✅ درست - Data migration با reverse
from django.db import migrations

def populate_sku(apps, schema_editor):
    """Forward data migration"""
    Item = apps.get_model('inventory', 'Item')
    for item in Item.objects.all():
        item.sku = f"SKU-{item.id:06d}"
        item.save()

def reverse_populate_sku(apps, schema_editor):
    """Reverse data migration"""
    Item = apps.get_model('inventory', 'Item')
    Item.objects.all().update(sku=None)

class Migration(migrations.Migration):
    dependencies = [
        ('inventory', '0005_add_sku_field'),
    ]
    
    operations = [
        migrations.RunPython(populate_sku, reverse_populate_sku),
    ]
```

### 2. Database Design Standards

#### Naming Conventions

```python
# ✅ درست
class ItemType(models.Model):
    public_code = models.CharField(max_length=20)
    is_enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'inventory_item_type'  # snake_case
        indexes = [
            models.Index(fields=['public_code']),
        ]

# ❌ اشتباه
class itemType(models.Model):  # نام کلاس باید PascalCase باشد
    publicCode = models.CharField()  # فیلد باید snake_case باشد
    IsEnabled = models.BooleanField()  # PascalCase
```

#### Index Strategy

```python
class Item(models.Model):
    name = models.CharField(max_length=200)
    public_code = models.CharField(max_length=50)
    category = models.ForeignKey(ItemCategory, on_delete=models.PROTECT)
    is_enabled = models.BooleanField(default=True)
    
    class Meta:
        # Single-column indexes
        indexes = [
            models.Index(fields=['public_code']),
            models.Index(fields=['is_enabled']),
            models.Index(fields=['created_at']),
            
            # Multi-column indexes (برای queries رایج)
            models.Index(fields=['category', 'is_enabled']),
            models.Index(fields=['company', 'public_code']),
        ]
        
        # Unique constraints
        constraints = [
            models.UniqueConstraint(
                fields=['company', 'public_code'],
                name='unique_item_code_per_company'
            ),
        ]
```

### 3. Query Optimization

#### استفاده صحیح از select_related و prefetch_related

```python
# ✅ درست - جلوگیری از N+1 queries
# select_related برای ForeignKey و OneToOne
items = Item.objects.select_related(
    'category',
    'subcategory',
    'type',
    'created_by'
).all()

# prefetch_related برای ManyToMany و Reverse ForeignKey
receipts = Receipt.objects.prefetch_related(
    'lines',
    'lines__item',
    'lines__item__category'
).all()

# ❌ اشتباه - N+1 queries
items = Item.objects.all()
for item in items:
    print(item.category.name)  # Query اضافی برای هر item!
```

#### استفاده از only() و defer()

```python
# فقط فیلدهای مورد نیاز را بارگذاری کن
items = Item.objects.only('id', 'name', 'public_code')

# همه فیلدها به جز فیلدهای سنگین
items = Item.objects.defer('description', 'specifications')
```

#### Aggregation

```python
from django.db.models import Count, Sum, Avg, Max, Min

# آمار items بر اساس category
stats = Item.objects.values('category__name').annotate(
    count=Count('id'),
    avg_price=Avg('unit_price')
)

# جمع موجودی
total_stock = ItemBalance.objects.aggregate(
    total_quantity=Sum('quantity'),
    total_value=Sum('quantity' * 'unit_price')
)
```

### 4. Database Constraints

```python
class Item(models.Model):
    name = models.CharField(max_length=200)
    public_code = models.CharField(max_length=50)
    unit_price = models.DecimalField(max_digits=15, decimal_places=2)
    company = models.ForeignKey(Company, on_delete=models.PROTECT)
    
    class Meta:
        constraints = [
            # Unique constraint
            models.UniqueConstraint(
                fields=['company', 'public_code'],
                name='unique_item_code_per_company'
            ),
            
            # Check constraint
            models.CheckConstraint(
                check=models.Q(unit_price__gte=0),
                name='unit_price_must_be_positive'
            ),
        ]
```

### 5. Migration در Production

#### قبل از Deploy

```bash
# 1. بررسی migrations
python manage.py showmigrations

# 2. Test migration در محیط staging
python manage.py migrate --plan
python manage.py migrate

# 3. Backup database
pg_dump database_name > backup_$(date +%Y%m%d_%H%M%S).sql
```

#### Migration Strategy

```python
# ✅ استراتژی ایمن برای تغییرات breaking:

# مرحله 1: اضافه کردن فیلد جدید (nullable)
class Migration(migrations.Migration):
    operations = [
        migrations.AddField(
            model_name='item',
            name='new_code',
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
    ]

# مرحله 2: Populate data
# Deploy code که از هر دو فیلد (قدیم و جدید) استفاده می‌کند

# مرحله 3: Migration برای populate
class Migration(migrations.Migration):
    operations = [
        migrations.RunPython(populate_new_code),
    ]

# مرحله 4: فیلد جدید را required کن
class Migration(migrations.Migration):
    operations = [
        migrations.AlterField(
            model_name='item',
            name='new_code',
            field=models.CharField(max_length=50),
        ),
    ]

# مرحله 5: حذف فیلد قدیم
class Migration(migrations.Migration):
    operations = [
        migrations.RemoveField(
            model_name='item',
            name='old_code',
        ),
    ]
```

---

## 📊 Error Handling & Logging

### 1. Logging Configuration

```python
# settings.py
import os

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'django.log'),
            'maxBytes': 1024 * 1024 * 15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'errors.log'),
            'maxBytes': 1024 * 1024 * 15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'filters': ['require_debug_false'],
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['error_file', 'mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'inventory': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'production': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
}
```

### 2. استفاده از Logger

```python
import logging

logger = logging.getLogger(__name__)

class ItemTypeListView(BaseListView):
    model = ItemType
    
    def get_queryset(self):
        try:
            company_id = self.request.session.get('active_company_id')
            
            # INFO level - اطلاعات عمومی
            logger.info(f"User {self.request.user.username} accessing item types for company {company_id}")
            
            queryset = super().get_queryset()
            
            # DEBUG level - اطلاعات دیباگ
            logger.debug(f"Query: {queryset.query}")
            
            return queryset
            
        except Exception as e:
            # ERROR level - خطاها
            logger.error(
                f"Error in ItemTypeListView.get_queryset: {str(e)}",
                exc_info=True,  # شامل stack trace
                extra={
                    'user': self.request.user.username,
                    'company_id': company_id,
                }
            )
            return self.model.objects.none()
```

### 3. Logging Levels

```python
import logging

logger = logging.getLogger(__name__)

# DEBUG - اطلاعات تکنیکال برای debugging
logger.debug(f"Processing item: {item_id}, category: {category_id}")

# INFO - اطلاعات کلی operation
logger.info(f"User {user.username} created new item: {item.name}")

# WARNING - مسائل قابل توجه ولی غیر خطرناک
logger.warning(f"Stock level for item {item.code} is below minimum: {quantity}")

# ERROR - خطاهای قابل بازیابی
logger.error(f"Failed to update item {item_id}: {error_message}")

# CRITICAL - خطاهای جدی که نیاز به توجه فوری دارند
logger.critical(f"Database connection lost: {error}")
```

### 4. Error Handling Patterns

#### View Level

```python
from django.views.generic import ListView
from django.contrib import messages
from django.http import Http404
import logging

logger = logging.getLogger(__name__)

class ItemTypeListView(BaseListView):
    model = ItemType
    
    def get_queryset(self):
        try:
            queryset = super().get_queryset()
            return queryset
        except Exception as e:
            logger.error(f"Error fetching item types: {e}", exc_info=True)
            messages.error(self.request, 'خطا در دریافت اطلاعات. لطفاً دوباره تلاش کنید.')
            return self.model.objects.none()
    
    def get(self, request, *args, **kwargs):
        try:
            return super().get(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Unexpected error in ItemTypeListView: {e}", exc_info=True)
            messages.error(request, 'خطای غیرمنتظره رخ داده است.')
            return redirect('dashboard')
```

#### Form Level

```python
from django import forms
import logging

logger = logging.getLogger(__name__)

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['name', 'public_code', 'category']
    
    def clean_public_code(self):
        """Validate public_code"""
        code = self.cleaned_data.get('public_code')
        
        try:
            # Check for duplicates
            company_id = self.initial.get('company_id')
            existing = Item.objects.filter(
                company_id=company_id,
                public_code=code
            ).exclude(pk=self.instance.pk)
            
            if existing.exists():
                logger.warning(
                    f"Duplicate code attempt: {code} for company {company_id}"
                )
                raise forms.ValidationError('این کد قبلاً استفاده شده است.')
            
            return code
            
        except forms.ValidationError:
            raise
        except Exception as e:
            logger.error(f"Error in code validation: {e}", exc_info=True)
            raise forms.ValidationError('خطا در بررسی کد.')
```

#### Service Level

```python
# services/inventory_service.py
import logging
from django.db import transaction

logger = logging.getLogger(__name__)

class InventoryService:
    """Business logic for inventory operations"""
    
    @transaction.atomic
    def create_receipt(self, receipt_data, lines_data):
        """
        Create receipt with lines
        
        Args:
            receipt_data: Dict with receipt information
            lines_data: List of dicts with line information
        
        Returns:
            Receipt object
        
        Raises:
            ValueError: If data is invalid
            DatabaseError: If database operation fails
        """
        try:
            # Validate data
            if not receipt_data.get('warehouse_id'):
                raise ValueError('Warehouse is required')
            
            if not lines_data:
                raise ValueError('At least one line is required')
            
            # Create receipt
            receipt = Receipt.objects.create(**receipt_data)
            logger.info(f"Receipt created: {receipt.document_number}")
            
            # Create lines
            for line_data in lines_data:
                ReceiptLine.objects.create(
                    receipt=receipt,
                    **line_data
                )
            
            logger.info(f"Receipt {receipt.document_number} created with {len(lines_data)} lines")
            
            return receipt
            
        except ValueError as e:
            logger.warning(f"Validation error in create_receipt: {e}")
            raise
        except Exception as e:
            logger.error(f"Error creating receipt: {e}", exc_info=True)
            raise
```

### 5. Custom Exception Classes

```python
# shared/exceptions.py

class BusinessLogicError(Exception):
    """Base exception for business logic errors"""
    pass

class InsufficientStockError(BusinessLogicError):
    """Raised when there's not enough stock for an operation"""
    def __init__(self, item, required, available):
        self.item = item
        self.required = required
        self.available = available
        super().__init__(
            f"Insufficient stock for {item.name}: required {required}, available {available}"
        )

class DocumentLockError(BusinessLogicError):
    """Raised when trying to modify a locked document"""
    def __init__(self, document):
        self.document = document
        super().__init__(f"Document {document.document_number} is locked and cannot be modified")

# استفاده
from shared.exceptions import InsufficientStockError

def issue_items(items):
    for item_data in items:
        item = item_data['item']
        quantity = item_data['quantity']
        available = get_available_stock(item)
        
        if quantity > available:
            raise InsufficientStockError(item, quantity, available)
```

---

## 🔄 Git Workflow

### 1. Branching Strategy

```bash
# Main branches
main/master     # Production-ready code
develop         # Integration branch

# Supporting branches
feature/*       # New features
bugfix/*        # Bug fixes
hotfix/*        # Production hotfixes
release/*       # Release preparation
```

### 2. Feature Development Workflow

```bash
# 1. شروع feature جدید از develop
git checkout develop
git pull origin develop
git checkout -b feature/add-item-barcode

# 2. کار روی feature
# ... ایجاد تغییرات ...
git add .
git commit -m "feat: add barcode field to Item model"

# 3. Push به remote
git push origin feature/add-item-barcode

# 4. ایجاد Pull Request
# از feature/add-item-barcode به develop

# 5. بعد از merge، پاکسازی branch
git checkout develop
git pull origin develop
git branch -d feature/add-item-barcode
```

### 3. Commit Message Convention

#### Format

```bash
<type>(<scope>): <subject>

<body>

<footer>
```

#### Types

```bash
feat:     # Feature جدید
fix:      # Bug fix
docs:     # تغییرات Documentation
style:    # تغییرات فرمت (formatting, spacing)
refactor: # Refactoring کد (نه feature و نه fix)
perf:     # بهبود Performance
test:     # اضافه کردن یا تغییر tests
chore:    # تغییرات build, dependencies

# مثال‌ها:
feat(inventory): add barcode scanning support
fix(production): resolve BOM calculation error
docs(api): update authentication documentation
refactor(shared): extract common validation logic
perf(inventory): optimize stock calculation query
test(accounting): add tests for fiscal year validation
```

#### مثال‌های خوب

```bash
# ✅ Feature جدید
feat(inventory): add multi-warehouse support

Added ability to manage items across multiple warehouses:
- New Warehouse model with location tracking
- Transfer between warehouses functionality
- Stock level per warehouse

Closes #123

# ✅ Bug fix
fix(production): correct BOM cost calculation

Fixed issue where indirect costs were not included in total cost.
Updated calculation logic to include:
- Material costs
- Labor costs
- Overhead allocation

Fixes #456

# ✅ Breaking change
feat(api)!: update API response format

BREAKING CHANGE: API response structure has changed.
Old format: { items: [] }
New format: { status: "success", data: { items: [] } }

Migration guide in docs/api-migration.md
```

#### مثال‌های بد

```bash
# ❌ غیرواضح
fix: fixed bug

# ❌ خیلی کلی
update: changes

# ❌ بدون context
added new file
```

### 4. Pull Request Guidelines

#### Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Related Issues
Closes #123, #456

## Changes Made
- Added barcode field to Item model
- Created migration for database changes
- Updated ItemForm to include barcode
- Added barcode validation

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Screenshots (if applicable)
[Add screenshots here]

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] Tests added/updated
- [ ] All tests passing
```

### 5. Code Review Process

#### Reviewer Checklist

- [ ] **Functionality**: آیا کد کار می‌کند؟
- [ ] **Tests**: آیا test کافی دارد؟
- [ ] **Standards**: آیا از استانداردهای پروژه پیروی می‌کند؟
- [ ] **Security**: آیا مشکل امنیتی دارد؟
- [ ] **Performance**: آیا مشکل performance دارد؟
- [ ] **Readability**: آیا کد قابل فهم است؟
- [ ] **Documentation**: آیا documentation به‌روز شده؟

### 6. Git Best Practices

```bash
# ✅ commit های کوچک و متمرکز
git commit -m "feat(inventory): add Item model"
git commit -m "feat(inventory): add ItemForm"
git commit -m "feat(inventory): add ItemListView"

# ❌ commit های بزرگ و نامشخص
git commit -m "added everything"

# ✅ pull قبل از push
git pull origin develop
git push origin feature/my-feature

# ✅ استفاده از .gitignore
# نگه نکردن فایل‌های غیرضروری

# ❌ commit کردن secrets
git commit -m "added config"  # با SECRET_KEY!

# ✅ استفاده از git stash
git stash
git checkout develop
git pull
git checkout feature/my-feature
git stash pop
```

---

## ⚡ Performance & Optimization

### 1. Database Query Optimization

```python
# ✅ استفاده از select_related برای ForeignKey
items = Item.objects.select_related(
    'category',
    'subcategory',
    'type'
).all()

# ✅ استفاده از prefetch_related برای reverse relations
receipts = Receipt.objects.prefetch_related(
    'lines',
    'lines__item'
).all()

# ✅ استفاده از only() برای فیلدهای خاص
items = Item.objects.only('id', 'name', 'code')

# ✅ استفاده از values() برای dictionary
items = Item.objects.values('id', 'name', 'price')

# ❌ N+1 Query Problem
for item in Item.objects.all():
    print(item.category.name)  # Query جداگانه!
```

### 2. Caching Strategy

```python
# settings.py
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'erp',
        'TIMEOUT': 300,  # 5 minutes
    }
}

# استفاده از cache
from django.core.cache import cache

def get_active_categories():
    """Get active categories with caching"""
    cache_key = 'active_categories'
    categories = cache.get(cache_key)
    
    if categories is None:
        categories = list(
            ItemCategory.objects.filter(is_enabled=True)
            .values('id', 'name')
        )
        cache.set(cache_key, categories, 3600)  # 1 hour
    
    return categories

# Cache invalidation
def save_category(category):
    category.save()
    cache.delete('active_categories')
```

### 3. Template Optimization

```django
{# ✅ استفاده از with برای متغیرهای تکراری #}
{% with total=items.count %}
    <p>Total: {{ total }}</p>
    <p>Showing {{ total }} items</p>
{% endwith %}

{# ✅ استفاده از regroup برای grouping #}
{% regroup items by category as grouped_items %}
{% for group in grouped_items %}
    <h3>{{ group.grouper }}</h3>
    {% for item in group.list %}
        <p>{{ item.name }}</p>
    {% endfor %}
{% endfor %}

{# ❌ queries تکراری در template #}
{% for item in items %}
    {{ item.category.name }}  {# N+1 query! #}
{% endfor %}
```

### 4. Static Files Optimization

```python
# settings.py

# در production
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Compression
MIDDLEWARE = [
    'django.middleware.gzip.GZipMiddleware',
    # ...
]
```

### 5. Pagination

```python
from django.core.paginator import Paginator

class ItemListView(BaseListView):
    paginate_by = 20  # تعداد items در هر صفحه
    
    def get_queryset(self):
        # فقط 20 item بارگذاری می‌شود، نه همه
        return super().get_queryset()
```

### 6. Background Tasks

```python
# استفاده از Celery برای taskهای سنگین
from celery import shared_task

@shared_task
def generate_monthly_report(company_id, month, year):
    """Generate monthly report in background"""
    # محاسبات سنگین
    report = calculate_report(company_id, month, year)
    
    # ذخیره نتیجه
    save_report(report)
    
    # ارسال ایمیل
    send_email_notification(company_id, report)

# استفاده در view
def request_monthly_report(request):
    generate_monthly_report.delay(
        company_id=request.session['active_company_id'],
        month=12,
        year=2024
    )
    messages.success(request, 'گزارش در حال تولید است و به زودی ارسال می‌شود.')
```

---

## 📖 استانداردهای مستندسازی

### 1. Docstring Format

```python
def calculate_total_cost(item_id, quantity, include_tax=True):
    """
    Calculate total cost for an item with given quantity.
    
    This function calculates the total cost including unit price,
    quantity, and optionally tax.
    
    Args:
        item_id (int): ID of the item
        quantity (Decimal): Quantity to calculate for
        include_tax (bool, optional): Whether to include tax. Defaults to True.
    
    Returns:
        Decimal: Total cost calculated
    
    Raises:
        ValueError: If item_id is invalid
        InsufficientStockError: If quantity exceeds available stock
    
    Example:
        >>> calculate_total_cost(item_id=1, quantity=Decimal('10'))
        Decimal('1150.00')
    """
    try:
        item = Item.objects.get(id=item_id)
    except Item.DoesNotExist:
        raise ValueError(f"Item with id {item_id} not found")
    
    base_cost = item.unit_price * quantity
    
    if include_tax:
        tax_amount = base_cost * item.tax_rate
        return base_cost + tax_amount
    
    return base_cost
```

### 2. README Structure

```markdown
# Module Name

Brief description of the module

## Features

- Feature 1
- Feature 2
- Feature 3

## Installation

\`\`\`bash
pip install -r requirements.txt
python manage.py migrate
\`\`\`

## Usage

\`\`\`python
from module import function
result = function(param)
\`\`\`

## API Reference

### Function Name

Description

**Parameters:**
- param1 (type): description
- param2 (type): description

**Returns:**
- type: description

**Example:**
\`\`\`python
example_code()
\`\`\`

## Contributing

Guidelines for contributing

## License

License information
```

### 3. Inline Comments

```python
# ✅ توضیح منطق پیچیده
def complex_calculation(data):
    # Apply weighted average formula
    # Formula: Σ(value * weight) / Σ(weight)
    weighted_sum = sum(item['value'] * item['weight'] for item in data)
    total_weight = sum(item['weight'] for item in data)
    
    return weighted_sum / total_weight if total_weight > 0 else 0

# ✅ توضیح تصمیمات مهم
# Using select_related here to avoid N+1 queries
# This is critical for performance with large datasets
items = Item.objects.select_related('category', 'subcategory')

# ❌ توضیح واضحات
x = x + 1  # increment x by 1
```

---

## 👁️ راهنمای Code Review

### Code Review Checklist

#### ✅ Functionality
- [ ] کد درست کار می‌کند؟
- [ ] همه edge cases پوشش داده شده؟
- [ ] error handling مناسب است؟

#### ✅ Testing
- [ ] unit tests وجود دارد؟
- [ ] tests کافی هستند؟
- [ ] همه tests پاس می‌شوند؟

#### ✅ Code Quality
- [ ] کد از استانداردهای پروژه پیروی می‌کند؟
- [ ] نام‌گذاری واضح است؟
- [ ] duplicated code وجود ندارد؟
- [ ] از base classes استفاده شده؟

#### ✅ Security
- [ ] input validation وجود دارد؟
- [ ] SQL injection امکان‌پذیر نیست؟
- [ ] XSS prevention رعایت شده؟
- [ ] sensitive data log نمی‌شود؟

#### ✅ Performance
- [ ] N+1 query وجود ندارد؟
- [ ] indexها مناسب هستند؟
- [ ] caching در جای مناسب استفاده شده؟

#### ✅ Documentation
- [ ] docstrings وجود دارد؟
- [ ] complex logic توضیح داده شده؟
- [ ] README به‌روز است؟

---

## 🔧 مدیریت Environment

### 1. Environment Variables

```python
# .env
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://user:pass@localhost/dbname
REDIS_URL=redis://localhost:6379/1

ALLOWED_HOSTS=localhost,127.0.0.1

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-password

# External APIs
EXTERNAL_API_KEY=your-api-key
EXTERNAL_API_URL=https://api.example.com
```

### 2. Settings per Environment

```python
# settings/base.py - تنظیمات مشترک
# settings/development.py - تنظیمات محیط توسعه
# settings/production.py - تنظیمات production

# settings/development.py
from .base import *

DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# settings/production.py
from .base import *

DEBUG = False
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

### 3. استفاده

```bash
# Development
export DJANGO_SETTINGS_MODULE=config.settings.development
python manage.py runserver

# Production
export DJANGO_SETTINGS_MODULE=config.settings.production
gunicorn config.wsgi:application
```

---

## ✅ چک‌لیست قبل از Commit

قبل از commit کردن کد جدید، این چک‌لیست را بررسی کنید:

### Backend Checklist

- [ ] آیا از Base Classes استفاده کرده‌ام؟ (`BaseListView`, `BaseCreateView`, etc.)
- [ ] آیا از Filter Functions استفاده کرده‌ام؟ (`apply_search`, `apply_status_filter`, etc.)
- [ ] آیا از Mixins استفاده کرده‌ام؟ (`PermissionFilterMixin`, `AutoSetFieldsMixin`, etc.)
- [ ] آیا `feature_code` را به درستی تنظیم کرده‌ام؟
- [ ] آیا `search_fields` و `filter_fields` را مشخص کرده‌ام؟
- [ ] آیا از `select_related` و `prefetch_related` برای بهینه‌سازی استفاده کرده‌ام؟
- [ ] آیا success message را تنظیم کرده‌ام؟
- [ ] آیا breadcrumbs را override کرده‌ام؟
- [ ] آیا permission checking را درست پیاده‌سازی کرده‌ام؟

### Frontend Checklist

- [ ] آیا از Generic Templates استفاده کرده‌ام؟ (`generic_list.html`, `generic_form.html`, etc.)
- [ ] آیا از Template Partials استفاده کرده‌ام؟ (`row_actions.html`, `pagination.html`, etc.)
- [ ] آیا از JavaScript مشترک استفاده کرده‌ام؟ (`formset.js`, `cascading-dropdowns.js`, etc.)
- [ ] آیا inline JavaScript نوشته‌ام؟ (باید حذف شود)
- [ ] آیا inline CSS نوشته‌ام؟ (باید حذف شود)
- [ ] آیا از `shared.css` استفاده کرده‌ام؟
- [ ] آیا event handlers را به درستی پیاده‌سازی کرده‌ام؟ (نه inline onclick)

### General Checklist

- [ ] آیا نام متغیرها واضح و قابل فهم است؟
- [ ] آیا از Django best practices استفاده کرده‌ام؟
- [ ] آیا error handling را درست پیاده‌سازی کرده‌ام؟
- [ ] آیا comments برای منطق پیچیده نوشته‌ام؟
- [ ] آیا کد را تست کرده‌ام؟
- [ ] آیا backward compatibility را حفظ کرده‌ام؟

---

## 💡 مثال‌های عملی

### مثال کامل: ایجاد یک ListView جدید

#### 1. View (`views.py`)

```python
from shared.views.base import BaseListView
from inventory.models import ItemType
from django.utils.translation import gettext_lazy as _

class ItemTypeListView(BaseListView):
    model = ItemType
    search_fields = ['name', 'public_code']
    filter_fields = ['is_enabled']
    feature_code = 'inventory.master.item_types'
    default_order_by = 'public_code'
    paginate_by = 20
    
    def get_breadcrumbs(self):
        return [
            {'label': _('Inventory'), 'url': reverse('inventory:dashboard')},
            {'label': _('Item Types'), 'url': None},
        ]
    
    def get_page_title(self):
        return _('Item Types')
```

#### 2. Template (`item_types.html`)

```django
{% extends "shared/generic/generic_list.html" %}
{% load i18n %}

{% block table_headers %}
<th>{% trans "Name" %}</th>
<th>{% trans "Code" %}</th>
<th>{% trans "Status" %}</th>
<th>{% trans "Actions" %}</th>
{% endblock %}

{% block table_rows %}
{% for object in object_list %}
<tr>
    <td>{{ object.name }}</td>
    <td>{{ object.public_code }}</td>
    <td>
        {% if object.is_enabled %}
            <span class="badge badge-success">{% trans "Active" %}</span>
        {% else %}
            <span class="badge badge-danger">{% trans "Inactive" %}</span>
        {% endif %}
    </td>
    <td>
        {% include 'shared/partials/row_actions.html' with object=object feature_code=feature_code %}
    </td>
</tr>
{% endfor %}
{% endblock %}
```

#### 3. URL (`urls.py`)

```python
from django.urls import path
from inventory.views.master_data import ItemTypeListView

urlpatterns = [
    path('item-types/', ItemTypeListView.as_view(), name='item_types'),
]
```

**نتیجه**: فقط ~30 خط کد به جای ~150 خط کد تکراری!

---

### مثال کامل: ایجاد یک CreateView با Formset

#### 1. View (`views.py`)

```python
from shared.views.base import BaseFormsetCreateView
from production.models import BOM
from production.forms import BOMForm, BOMMaterialLineFormSet
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

class BOMCreateView(BaseFormsetCreateView):
    model = BOM
    form_class = BOMForm
    formset_class = BOMMaterialLineFormSet
    formset_prefix = 'materials'
    success_url = reverse_lazy('production:bom_list')
    feature_code = 'production.bom'
    success_message = _('BOM created successfully.')
    
    def get_breadcrumbs(self):
        return [
            {'label': _('Production'), 'url': reverse('production:dashboard')},
            {'label': _('BOMs'), 'url': reverse('production:bom_list')},
            {'label': _('Create BOM'), 'url': None},
        ]
    
    def get_formset_kwargs(self):
        kwargs = super().get_formset_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        return kwargs
```

#### 2. Template (`bom_form.html`)

```django
{% extends "shared/generic/generic_form.html" %}
{% load static %}

{% block form_sections %}
<div class="form-section">
    <h3>BOM Information</h3>
    <div class="row">
        <div class="col-md-6">
            <div class="form-group">
                {{ form.finished_item.label_tag }}
                {{ form.finished_item }}
                {{ form.finished_item.errors }}
            </div>
        </div>
    </div>
</div>

<div class="form-section">
    <h3>Materials</h3>
    <table id="materials-formset" class="table">
        <thead>
            <tr>
                <th>Material</th>
                <th>Quantity</th>
                <th>Unit</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody>
            {% for form in formset %}
            <tr class="formset-row">
                <td>{{ form.material }}</td>
                <td>{{ form.quantity }}</td>
                <td>{{ form.unit }}</td>
                <td>
                    {% if form.DELETE %}
                        <button type="button" class="btn btn-danger remove-row">Remove</button>
                    {% endif %}
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
    
    <button type="button" id="add-material-btn" class="btn btn-primary">Add Material</button>
    
    {{ formset.management_form }}
</div>
{% endblock %}

{% block extra_js %}
<script src="{% static 'js/formset.js' %}"></script>
<script>
document.addEventListener('DOMContentLoaded', function() {
    initFormset('materials', '#material-template-row', {
        minRows: 1,
        maxRows: 100
    });
});
</script>
{% endblock %}
```

**نتیجه**: فقط ~50 خط کد به جای ~200 خط کد تکراری!

---

## 📚 منابع و مستندات

### مستندات مرتبط

1. **`shared_architecture_refactoring.md`**: مستند کامل معماری مشترک (Backend)
2. **`HTML_REFACTORING_ANALYSIS.md`**: مستند کامل refactoring Frontend
3. **`shared_files_checklist.md`**: چک‌لیست فایل‌های اشتراکی
4. **`shared_files_verification_report.md`**: گزارش تأیید فایل‌های اشتراکی

### لینک‌های مفید

- Django Class-Based Views: https://docs.djangoproject.com/en/stable/topics/class-based-views/
- Django Formsets: https://docs.djangoproject.com/en/stable/topics/forms/formsets/

---

## ❓ سوالات متداول

### Q1: آیا می‌توانم Base Class را override کنم؟

**A**: بله، اما فقط hook methods را override کنید. متدهای اصلی (`get_queryset`, `get_context_data`) را override نکنید مگر اینکه واقعاً نیاز باشد.

### Q2: اگر منطق خاصی دارم که در Base Class نیست چه کنم؟

**A**: از hook methods استفاده کنید (`apply_custom_filters`, `get_prefetch_related`, etc.) یا یک Mixin جدید ایجاد کنید.

### Q3: آیا می‌توانم template جدید بنویسم؟

**A**: فقط در موارد خاص. در 99% موارد باید از Generic Templates استفاده کنید.

### Q4: اگر JavaScript خاصی نیاز دارم چه کنم؟

**A**: ابتدا بررسی کنید که آیا می‌توانید از JavaScript مشترک استفاده کنید. اگر نه، فایل JavaScript جدید ایجاد کنید و در `static/js/` قرار دهید.

### Q5: چگونه می‌توانم فایل اشتراکی جدید اضافه کنم؟

**A**: ابتدا با تیم هماهنگ کنید. اگر مورد تأیید قرار گرفت، فایل را در `shared/` ایجاد کنید و مستندسازی کنید.

---

## 📞 تماس و پشتیبانی

اگر سوالی دارید یا مشکلی پیش آمد:

1. ابتدا این راهنما را کامل مطالعه کنید
2. مستندات مرتبط را بررسی کنید
3. با تیم هماهنگ کنید

---

## 📋 Quick Reference

### چک‌لیست روزانه توسعه‌دهنده

```bash
# صبح - شروع کار
git checkout develop
git pull origin develop
git checkout -b feature/my-new-feature

# حین توسعه
# ✅ از Base Classes استفاده کن
# ✅ از Generic Templates استفاده کن  
# ✅ از JavaScript مشترک استفاده کن
# ✅ تست بنویس
# ✅ Security را رعایت کن
# ✅ Performance را در نظر بگیر

# قبل از Commit
# ✅ تست‌ها را اجرا کن
python manage.py test

# ✅ Code را review کن
# ✅ Documentation را به‌روز کن

# Commit با format صحیح
git add .
git commit -m "feat(inventory): add barcode support"

# Push و PR
git push origin feature/my-new-feature
# ایجاد Pull Request در GitHub/GitLab
```

### دستورات مفید

```bash
# Testing
python manage.py test                          # همه تست‌ها
python manage.py test inventory                # تست‌های یک app
python manage.py test --with-coverage         # با coverage

# Migration
python manage.py makemigrations               # ایجاد migration
python manage.py migrate                      # اعمال migrations
python manage.py migrate --plan              # پیش‌نمایش

# Development Server
python manage.py runserver                    # اجرا

# Shell
python manage.py shell                        # Django shell
python manage.py dbshell                      # Database shell

# Static Files
python manage.py collectstatic               # جمع‌آوری static files

# Database
python manage.py dumpdata > backup.json      # Backup
python manage.py loaddata backup.json        # Restore
```

### فایل‌های کلیدی

```
shared/views/base.py              # Base View Classes
shared/filters.py                 # Filter Functions
shared/mixins.py                  # Mixins
shared/forms/base.py              # Base Forms
shared/exceptions.py              # Custom Exceptions

static/js/formset.js              # Formset Management
static/js/cascading-dropdowns.js  # Cascading Dropdowns
static/js/table-export.js         # Table Export
static/css/shared.css             # Shared Styles

templates/shared/generic/         # Generic Templates
templates/shared/partials/        # Template Partials

tests/                           # Test Files
```

### لینک‌های مفید

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Testing in Django](https://docs.djangoproject.com/en/stable/topics/testing/)
- [Git Commit Convention](https://www.conventionalcommits.org/)

---

**⚠️ یادآوری مهم**: این راهنما **الزامی** است و تمام توسعه‌دهندگان باید از آن پیروی کنند. کدهای جدید که از این استانداردها پیروی نمی‌کنند، reject می‌شوند.

---

**آخرین به‌روزرسانی**: 2024-12-23  
**نسخه**: 2.0

**Contributors**: تیم توسعه ERP  
**License**: Internal Use Only

