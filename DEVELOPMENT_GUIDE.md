# راهنمای توسعه - Development Guide

**تاریخ ایجاد**: 2024-12-06  
**آخرین به‌روزرسانی**: 2024-12-06  
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
10. [چک‌لیست قبل از Commit](#چکلیست-قبل-از-commit)
11. [مثال‌های عملی](#مثالهای-عملی)

---

## 🎯 مقدمه و هدف

این راهنما شامل **قوانین اجباری** و **استانداردهای توسعه** برای پروژه ERP است. هدف اصلی:

- ✅ **کاهش تکرار کد**: استفاده از فایل‌های اشتراکی به جای نوشتن کد تکراری
- ✅ **یکپارچگی**: تمام ماژول‌ها از الگوهای مشترک استفاده می‌کنند
- ✅ **نگهداری آسان**: تغییرات فقط در یک جا اعمال می‌شوند
- ✅ **توسعه سریع**: ایجاد feature جدید با استفاده از Base Classes بسیار سریع‌تر است

**⚠️ مهم**: تمام توسعه‌دهندگان **باید** این راهنما را مطالعه کنند و از قوانین آن پیروی کنند.

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
| `accounting/views/tafsili_hierarchy.py` | `TafsiliHierarchyListView` | `BaseListView` | `generic_list.html` | ✅ |
| `accounting/views/tafsili_hierarchy.py` | `TafsiliHierarchyCreateView` | `BaseCreateView` | `generic_form.html` | ✅ |
| `accounting/views/tafsili_hierarchy.py` | `TafsiliHierarchyUpdateView` | `BaseUpdateView` | `generic_form.html` | ✅ |
| `accounting/views/tafsili_hierarchy.py` | `TafsiliHierarchyDetailView` | `BaseDetailView` | `generic_detail.html` | ✅ |
| `accounting/views/tafsili_hierarchy.py` | `TafsiliHierarchyDeleteView` | `BaseDeleteView` | `generic_confirm_delete.html` | ✅ |
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
| `accounting/tafsili_hierarchy_detail.html` | `generic_detail.html` | ✅ |

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

**⚠️ یادآوری مهم**: این راهنما **الزامی** است و تمام توسعه‌دهندگان باید از آن پیروی کنند. کدهای جدید که از این استانداردها پیروی نمی‌کنند، reject می‌شوند.

---

**آخرین به‌روزرسانی**: 2024-12-06  
**نسخه**: 1.0

