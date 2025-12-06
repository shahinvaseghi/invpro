# تحلیل Refactoring فایل‌های HTML

**تاریخ ایجاد**: 2024-12-05  
**آخرین به‌روزرسانی**: 2024-12-06  
**هدف**: شناسایی الگوهای تکراری در فایل‌های HTML/Template و برنامه‌ریزی برای refactoring

---

## 📖 مقدمه و هدف

این سند مکمل فایل `shared_architecture_refactoring.md` است و به **refactoring لایه Presentation (Template/HTML)** می‌پردازد.

### چرا این فایل ایجاد شد؟

پس از تکمیل refactoring لایه View (Django Views) و انتقال کدهای تکراری به Base Classes مشترک، نیاز به **استانداردسازی و refactoring لایه Template** احساس شد.

### چه مشکلی را حل می‌کند؟

1. **کد تکراری در Templateها**: الگوهای یکسان در چندین فایل HTML تکرار شده‌اند
2. **عدم استفاده از Generic Templates**: برخی فایل‌ها از base templates استفاده نمی‌کنند
3. **JavaScript Inline**: کد JavaScript در templateها به صورت inline نوشته شده و تکرار شده
4. **CSS Inline**: استایل‌ها به صورت inline در templateها نوشته شده‌اند
5. **Inline Event Handlers**: استفاده از `onclick` و `onchange` به جای event listeners

### چه کاری می‌خواهیم انجام دهیم؟

1. **Migrate Detail Views**: انتقال تمام Detail Views به `generic_detail.html`
2. **Migrate List/Form Views**: اطمینان از استفاده همه فایل‌ها از generic templates
3. **Refactor JavaScript**: انتقال JavaScript inline به فایل‌های مشترک
4. **Refactor CSS**: انتقال CSS inline به فایل‌های مشترک
5. **استفاده از Partials**: جایگزینی کدهای تکراری با partials مشترک

### ارتباط با `shared_architecture_refactoring.md`

- **`shared_architecture_refactoring.md`**: refactoring لایه **View (Python/Django)**
- **`HTML_REFACTORING_ANALYSIS.md`**: refactoring لایه **Template (HTML/JavaScript/CSS)**

این دو فایل با هم، refactoring کامل لایه‌های Backend و Frontend را پوشش می‌دهند.

### مزایای Refactoring

- ✅ **کاهش کد تکراری**: حذف ~1,200+ خط کد تکراری
- ✅ **بهبود Maintainability**: تغییرات در یک جا اعمال می‌شود
- ✅ **یکنواختی UI**: استفاده از یک الگوی مشترک
- ✅ **بهبود Performance**: استفاده از فایل‌های static cached
- ✅ **سهولت توسعه**: افزودن featureهای جدید سریع‌تر می‌شود

---

## 📚 لیست کامل فایل‌های اشتراکی

این بخش شامل لیست کامل تمام فایل‌های اشتراکی است که در refactoring ماژول‌های مختلف استفاده شده‌اند.

### بخش ۱: فایل‌های Backend (Python/Django)

#### ۱.۱ Base View Classes

**فایل**: `shared/views/base.py`

کلاس‌های پایه برای Viewها:

1. **BaseListView** - لیست viewهای استاندارد
   - پشتیبانی از search, filter, pagination, permissions
   - استفاده از `generic_list.html`

2. **BaseCreateView** - ایجاد viewهای استاندارد
   - auto-set company_id, created_by
   - استفاده از `generic_form.html`

3. **BaseUpdateView** - ویرایش viewهای استاندارد
   - auto-set edited_by
   - استفاده از `generic_form.html`

4. **BaseDeleteView** - حذف viewهای استاندارد
   - validation و success message
   - استفاده از `generic_confirm_delete.html`

5. **BaseDetailView** - مشاهده viewهای استاندارد
   - permission checking
   - استفاده از `generic_detail.html`

6. **BaseFormsetCreateView** - ایجاد view با formset
   - مدیریت formset در create

7. **BaseFormsetUpdateView** - ویرایش view با formset
   - مدیریت formset در update

8. **BaseDocumentListView** - لیست view برای اسناد
   - prefetch lines و stats

9. **BaseDocumentCreateView** - ایجاد view برای اسناد
   - save header و lines

10. **BaseDocumentUpdateView** - ویرایش view برای اسناد
    - update header و lines

11. **BaseNestedFormsetCreateView** - ایجاد view با nested formset
    - مدیریت nested formsets (مثل BOM)

12. **BaseNestedFormsetUpdateView** - ویرایش view با nested formset
    - مدیریت nested formsets در update

#### ۱.۲ Additional Base Classes

**فایل**: `shared/views/base_additional.py`

کلاس‌های پایه برای الگوهای پیچیده:

1. **TransferRequestCreationMixin** - Mixin برای ایجاد transfer request از order
   - استفاده در `ProductOrderCreateView`

2. **BaseMultipleFormsetCreateView** - ایجاد view با چند formset
   - مدیریت چند formset همزمان (مثل TicketTemplate)

3. **BaseMultipleFormsetUpdateView** - ویرایش view با چند formset
   - مدیریت چند formset در update

4. **BaseMultipleDocumentCreateView** - ایجاد view برای چند سند
   - استفاده در `TransferToLineCreateView`

#### ۱.۳ Mixins

**فایل**: `shared/mixins.py` و `shared/views/base.py`

1. **PermissionFilterMixin** - فیلتر queryset بر اساس permissions
2. **CompanyScopedViewMixin** - فیلتر بر اساس active company
3. **AutoSetFieldsMixin** - auto-set company_id, created_by, edited_by
4. **SuccessMessageMixin** - نمایش success message
5. **EditLockProtectedMixin** - محافظت از edit در صورت lock
6. **UserAccessFormsetMixin** - مدیریت company access برای users
7. **AccessLevelPermissionMixin** - مدیریت permissions برای access levels

#### ۱.۴ Filter Functions

**فایل**: `shared/filters.py`

1. **apply_search(queryset, search_query, fields)** - جستجو در چند فیلد
2. **apply_status_filter(queryset, status_value)** - فیلتر وضعیت
3. **apply_company_filter(queryset, company_id)** - فیلتر شرکت
4. **apply_date_range_filter(queryset, date_from, date_to, field_name)** - فیلتر بازه تاریخ
5. **apply_multi_field_filter(queryset, request, filter_map)** - فیلتر چند فیلد

#### ۱.۵ Base Form Classes

**فایل**: `shared/forms/base.py`

1. **BaseModelForm** - فرم پایه با auto widget styling
2. **BaseFormset** - helper class برای formsets

#### ۱.۶ API View Classes

**فایل**: `shared/views/api.py`

1. **BaseAPIView** - پایه برای API views
2. **BaseListAPIView** - لیست API view
3. **BaseDetailAPIView** - detail API view

#### ۱.۷ Helper Functions

**فایل**: `shared/utils/view_helpers.py`

1. **get_breadcrumbs(module_name, items)** - تولید breadcrumbs
2. **get_success_message(action, model_name)** - تولید success message
3. **validate_active_company(request)** - بررسی active company
4. **get_table_headers(fields)** - تولید table headers

---

### بخش ۲: فایل‌های Frontend

#### ۲.۱ JavaScript Files

**مسیر**: `static/js/`

1. **formset.js** ✅
   - `addFormsetRow(prefix, templateSelector, options)`
   - `removeFormsetRow(button, prefix, options)`
   - `updateFormsetTotal(prefix)`
   - `reindexFormset(prefix)`
   - `initFormset(prefix, templateSelector, options)`

2. **cascading-dropdowns.js** ✅
   - `initCascadingDropdown(parentSelect, childSelect, apiUrl, options)`
   - `updateDropdownOptions(selectElement, options, placeholder, valueField, labelField)`
   - `clearDropdown(selectElement, placeholder)`
   - `initCascadingDropdowns()` - auto-initialize

3. **table-export.js** ✅
   - `exportTableToCSV(tableId, filename, options)`
   - `exportTableToExcel(tableId, filename, options)`
   - `printTable(tableId, options)`

4. **form-helpers.js** ✅
   - `initAutoSubmit(selectElement, options)`
   - `initDatePicker(inputElement, options)`
   - `validateForm(formElement, options)`
   - `showFormErrors(formElement, errors, options)`
   - `clearFormErrors(formElement, options)`

5. **item-filters.js** ✅
   - `filterItemsForRow(rowIndex, itemTypeId, categoryId, subcategoryId)`
   - `loadCategoriesForRow(rowIndex, itemTypeId)`
   - `loadSubcategoriesForRow(rowIndex, categoryId)`
   - `refreshLineUnitOptions(rowIndex, itemId)`
   - `refreshLineWarehouseOptions(rowIndex, itemId)`
   - `initializeItemFiltersForRow(rowIndex)`

6. **formset-table.js** ✅
   - مدیریت grid layout برای formset tables
   - توابع helper برای formset در جداول

#### ۲.۲ CSS Files

**مسیر**: `static/css/`

1. **formset-table.css** ✅
   - استایل‌های layout برای formset tables

#### ۲.۳ Template Partials

**مسیر**: `templates/shared/partials/`

1. **row_actions.html** ✅
   - نمایش دکمه‌های action برای هر row
   - پشتیبانی از permissions و custom actions

2. **filter_panel.html** ✅
   - پنل فیلتر مشترک
   - پشتیبانی از search, status filter, custom filters

3. **stats_cards.html** ✅
   - نمایش کارت‌های آمار
   - responsive grid layout

4. **pagination.html** ✅
   - pagination مشترک
   - حفظ query parameters

5. **empty_state.html** ✅
   - نمایش empty state
   - دکمه Create (اختیاری)

#### ۲.۴ Generic Templates

**مسیر**: `templates/shared/generic/`

1. **generic_list.html** ✅
   - template مشترک برای List Views
   - استفاده از partials: filter_panel, stats_cards, pagination, empty_state, row_actions

2. **generic_form.html** ✅
   - template مشترک برای Create/Update Views
   - responsive design

3. **generic_detail.html** ✅
   - template مشترک برای Detail Views
   - پشتیبانی از info_banner, detail_sections, detail_actions

4. **generic_confirm_delete.html** ✅
   - template مشترک برای Delete Views
   - نمایش object details و confirmation

#### ۲.۵ Template Tags

**فایل**: `shared/templatetags/view_tags.py`

1. **{% get_breadcrumbs module items %}** - تولید breadcrumbs
2. **{% get_table_headers fields %}** - تولید table headers
3. **{% can_action object action feature_code %}** - بررسی permission برای action
4. **{% get_object_actions object feature_code %}** - دریافت actions موجود
5. **{{ dict|get_item:key }}** - دریافت item از dictionary

---

### خلاصه آمار فایل‌های اشتراکی

| دسته | تعداد فایل | وضعیت |
|------|-----------|-------|
| **Backend Base Classes** | 16 کلاس | ✅ تکمیل شده |
| **Backend Mixins** | 7 mixin | ✅ تکمیل شده |
| **Backend Filters** | 5 تابع | ✅ تکمیل شده |
| **Backend Forms** | 2 کلاس | ✅ تکمیل شده |
| **Backend API Views** | 3 کلاس | ✅ تکمیل شده |
| **Backend Helpers** | 4 تابع | ✅ تکمیل شده |
| **JavaScript Files** | 6 فایل | ✅ تکمیل شده |
| **CSS Files** | 1 فایل | ✅ تکمیل شده |
| **Template Partials** | 5 فایل | ✅ تکمیل شده |
| **Generic Templates** | 4 فایل | ✅ تکمیل شده |
| **Template Tags** | 5 tag | ✅ تکمیل شده |
| **جمع کل** | **59 فایل/کلاس/تابع** | ✅ |

---

## 📊 خلاصه وضعیت فعلی

### ✅ فایل‌های که از Generic Templates استفاده می‌کنند

#### List Views (72 فایل)
- اکثر فایل‌های list از `shared/generic/generic_list.html` extend می‌کنند ✅
- فقط `table_headers` و `table_rows` را override می‌کنند ✅
- استفاده از `row_actions.html` partial در برخی فایل‌ها ✅

#### Form Views (30+ فایل)
- اکثر فایل‌های form از `shared/generic/generic_form.html` extend می‌کنند ✅
- فقط `form_sections` را override می‌کنند ✅

#### Delete Views
- از `shared/generic/generic_confirm_delete.html` استفاده می‌شود ✅

---

## ⚠️ مشکلات و الگوهای تکراری شناسایی شده

### 1. **Detail Views - عدم استفاده از Generic Template**

**مشکل**: اکثر فایل‌های `*_detail.html` از `shared/base.html` یا `inventory/base.html` extend می‌کنند به جای `shared/generic/generic_detail.html`

**فایل‌های نیازمند Refactor** (حدود 40+ فایل):

#### ماژول `inventory` (12 فایل):
- `inventory/itemtype_detail.html` → باید از `generic_detail.html` extend کند
- `inventory/itemcategory_detail.html` → باید از `generic_detail.html` extend کند
- `inventory/itemsubcategory_detail.html` → باید از `generic_detail.html` extend کند
- `inventory/item_detail.html` → باید از `generic_detail.html` extend کند
- `inventory/warehouse_detail.html` → باید از `generic_detail.html` extend کند
- `inventory/supplier_detail.html` → باید از `generic_detail.html` extend کند
- `inventory/suppliercategory_detail.html` → باید از `generic_detail.html` extend کند
- `inventory/purchase_request_detail.html` → باید از `generic_detail.html` extend کند
- `inventory/warehouse_request_detail.html` → باید از `generic_detail.html` extend کند
- `inventory/stocktaking_deficit_detail.html` → باید از `generic_detail.html` extend کند
- `inventory/stocktaking_surplus_detail.html` → باید از `generic_detail.html` extend کند
- `inventory/stocktaking_record_detail.html` → باید از `generic_detail.html` extend کند
- `inventory/receipt_detail.html` → باید از `generic_detail.html` extend کند
- `inventory/issue_detail.html` → باید از `generic_detail.html` extend کند
- `inventory/issue_warehouse_transfer_detail.html` → باید از `generic_detail.html` extend کند

#### ماژول `production` (8 فایل):
- `production/person_detail.html` → باید از `generic_detail.html` extend کند
- `production/machine_detail.html` → باید از `generic_detail.html` extend کند
- `production/work_line_detail.html` → باید از `generic_detail.html` extend کند
- `production/process_detail.html` → باید از `generic_detail.html` extend کند
- `production/bom_detail.html` → باید از `generic_detail.html` extend کند
- `production/product_order_detail.html` → باید از `generic_detail.html` extend کند
- `production/transfer_to_line_detail.html` → باید از `generic_detail.html` extend کند
- `production/performance_record_detail.html` → باید از `generic_detail.html` extend کند

#### ماژول `accounting` (6 فایل):
- `accounting/account_detail.html` → باید از `generic_detail.html` extend کند
- `accounting/fiscal_year_detail.html` → باید از `generic_detail.html` extend کند
- `accounting/gl_account_detail.html` → باید از `generic_detail.html` extend کند
- `accounting/sub_account_detail.html` → باید از `generic_detail.html` extend کند
- `accounting/tafsili_account_detail.html` → باید از `generic_detail.html` extend کند
- `accounting/tafsili_hierarchy_detail.html` → باید از `generic_detail.html` extend کند

#### ماژول `ticketing` (4 فایل):
- `ticketing/category_detail.html` → باید از `generic_detail.html` extend کند
- `ticketing/subcategory_detail.html` → باید از `generic_detail.html` extend کند
- `ticketing/template_detail.html` → باید از `generic_detail.html` extend کند
- `ticketing/ticket_detail.html` → باید از `generic_detail.html` extend کند

#### ماژول `shared` (6 فایل):
- `shared/user_detail.html` → باید از `generic_detail.html` extend کند
- `shared/company_detail.html` → باید از `generic_detail.html` extend کند
- `shared/company_unit_detail.html` → باید از `generic_detail.html` extend کند
- `shared/group_detail.html` → باید از `generic_detail.html` extend کند
- `shared/access_level_detail.html` → باید از `generic_detail.html` extend کند
- `shared/smtp_server_detail.html` → باید از `generic_detail.html` extend کند

**جمع کل**: **39 فایل Detail View** نیازمند refactor
- **inventory**: 15 فایل
- **production**: 8 فایل
- **accounting**: 6 فایل
- **ticketing**: 4 فایل
- **shared**: 6 فایل

---

### 2. **Row Actions - عدم استفاده از Partial**

**مشکل**: برخی فایل‌های list، row actions را inline می‌نویسند به جای استفاده از `shared/partials/row_actions.html`

**فایل‌های نیازمند Refactor**:
- `inventory/item_types.html` - row actions inline نوشته شده
- `inventory/item_categories.html` - row actions inline نوشته شده
- `production/machines.html` - row actions inline نوشته شده
- و سایر فایل‌های list که از `row_actions.html` استفاده نمی‌کنند

**راه حل**: همه باید از `{% include 'shared/partials/row_actions.html' %}` استفاده کنند

---

### 3. **Pagination - عدم استفاده از Partial**

**مشکل**: برخی فایل‌های list، pagination را override می‌کنند به جای استفاده از `shared/partials/pagination.html`

**فایل‌های نیازمند Refactor**:
- `production/machines.html` - pagination block override شده
- سایر فایل‌هایی که pagination را override می‌کنند

**راه حل**: همه باید از `shared/partials/pagination.html` استفاده کنند

---

### 4. **List Views - فایل‌هایی که از Generic List استفاده نمی‌کنند**

**فایل‌های نیازمند Refactor**:

#### ماژول `accounting` (6 فایل):
- `accounting/treasury/accounts.html` → باید از `generic_list.html` extend کند
- `accounting/parties/accounts.html` → باید از `generic_list.html` extend کند
- `accounting/parties/list.html` → باید از `generic_list.html` extend کند
- `accounting/income_expense/categories.html` → باید از `generic_list.html` extend کند
- `accounting/income_expense/cost_centers.html` → باید از `generic_list.html` extend کند
- `accounting/attachments/list.html` → باید از `generic_list.html` extend کند

#### ماژول `ticketing` (2 فایل):
- `ticketing/categories.html` → باید از `generic_list.html` extend کند (placeholder است)
- `ticketing/subcategories.html` → باید از `generic_list.html` extend کند (placeholder است)

**جمع کل**: حدود **8 فایل List View** نیازمند refactor

---

### 5. **Form Views - فایل‌هایی که از Generic Form استفاده نمی‌کنند**

**فایل‌های نیازمند Refactor**:

#### ماژول `accounting` (4 فایل):
- `accounting/attachments/upload.html` → باید از `generic_form.html` extend کند
- سایر formهای accounting که از `base.html` extend می‌کنند

**جمع کل**: حدود **4-5 فایل Form View** نیازمند refactor

---

### 6. **JavaScript Inline - عدم استفاده از فایل‌های مشترک**

**مشکل**: JavaScript برای مدیریت formset، cascading dropdowns، table export و سایر عملکردها در چندین template به صورت inline نوشته شده است:

#### 6.1 Formset Management JavaScript
**فایل‌های نیازمند Refactor** (18+ فایل):

**ماژول `production`** (5 فایل):
- `production/bom_form.html` - JavaScript inline برای formset management (~200 خط)
- `production/process_form.html` - JavaScript inline برای formset management
- `production/performance_record_form.html` - JavaScript inline برای formset management
- `production/transfer_to_line_form.html` - JavaScript inline برای formset management
- `production/rework_document_form.html` - JavaScript inline برای formset management

**ماژول `inventory`** (5 فایل):
- `inventory/item_form.html` - JavaScript inline برای unit formset management
- `inventory/receipt_form.html` - JavaScript inline برای line formset management
- `inventory/issue_form.html` - JavaScript inline برای line formset management
- `inventory/stocktaking_form.html` - JavaScript inline برای formset management
- `inventory/purchase_request_form.html` - JavaScript inline برای formset management
- `inventory/warehouse_request_form.html` - استفاده از `formset.js` ✅ (مثال خوب)

**ماژول `ticketing`** (3 فایل):
- `ticketing/category_form.html` - JavaScript inline برای permission formset management
- `ticketing/subcategory_form.html` - JavaScript inline برای permission formset management
- `ticketing/template_form.html` - JavaScript inline برای multiple formsets management

**ماژول `shared`** (1 فایل):
- `shared/user_form.html` - JavaScript inline برای company access formset management

**ماژول `accounting`** (2 فایل):
- `accounting/treasury/account_form.html` - JavaScript inline برای formset management
- `accounting/parties/party_form.html` - JavaScript inline برای formset management

**سایر فایل‌ها** (2+ فایل):
- `inventory/create_receipt_from_purchase_request.html` - JavaScript inline برای formset management
- `inventory/create_issue_from_warehouse_request.html` - JavaScript inline برای formset management

**راه حل**: استفاده از `static/js/formset.js` و `static/js/formset-table.js`

**صرفه‌جویی**: حذف ~500 خط کد JavaScript تکراری

#### 6.2 Cascading Dropdowns JavaScript
**فایل‌های نیازمند Refactor** (10+ فایل):

**ماژول `production`** (3 فایل):
- `production/bom_form.html` - JavaScript inline برای cascading (Type → Category → Subcategory → Item) (~300 خط)
- `production/process_form.html` - JavaScript inline برای cascading dropdowns
- `production/transfer_to_line_form.html` - JavaScript inline برای cascading dropdowns

**ماژول `inventory`** (5 فایل):
- `inventory/item_form.html` - JavaScript inline برای cascading (Category → Subcategory) (~100 خط)
- `inventory/receipt_form.html` - JavaScript inline برای cascading (Item → Unit, Warehouse)
- `inventory/issue_form.html` - JavaScript inline برای cascading (Item → Unit, Warehouse)
- `inventory/purchase_request_form.html` - JavaScript inline برای cascading dropdowns
- `inventory/warehouse_request_form.html` - استفاده از `cascading-dropdowns.js` ✅ (مثال خوب)

**ماژول `accounting`** (1 فایل):
- `accounting/parties/party_account_form.html` - JavaScript inline برای cascading dropdowns

**سایر فایل‌ها** (1+ فایل):
- `inventory/create_receipt_from_purchase_request.html` - JavaScript inline برای cascading dropdowns

**راه حل**: استفاده از `static/js/cascading-dropdowns.js`

**صرفه‌جویی**: حذف ~300 خط کد JavaScript تکراری

#### 6.3 Table Export JavaScript
**فایل‌های نیازمند Refactor** (5+ فایل):
- `shared/generic/generic_report.html` - JavaScript inline برای `exportToExcel()` (~50 خط)
- `inventory/inventory_balance.html` - JavaScript inline برای `exportToExcel()` (~50 خط)
- `inventory/inventory_balance_details.html` - JavaScript inline برای `exportToExcel()`
- `inventory/item_serials.html` - JavaScript inline برای `exportToExcel()`
- `inventory/purchase_requests.html` - JavaScript inline برای `exportToExcel()`
- `inventory/receipt_temporary.html` - JavaScript inline برای `exportToExcel()`
- `inventory/receipt_permanent.html` - JavaScript inline برای `exportToExcel()`
- `inventory/receipt_consignment.html` - JavaScript inline برای `exportToExcel()`
- `inventory/issue_permanent.html` - JavaScript inline برای `exportToExcel()`
- `inventory/issue_consumption.html` - JavaScript inline برای `exportToExcel()`
- `inventory/issue_consignment.html` - JavaScript inline برای `exportToExcel()`
- `inventory/warehouse_requests.html` - JavaScript inline برای `exportToExcel()`
- `inventory/stocktaking_deficit.html` - JavaScript inline برای `exportToExcel()`
- `inventory/stocktaking_surplus.html` - JavaScript inline برای `exportToExcel()`
- `inventory/stocktaking_records.html` - JavaScript inline برای `exportToExcel()`
- `production/performance_record_list.html` - JavaScript inline برای `exportToExcel()`
- `production/transfer_to_line_list.html` - JavaScript inline برای `exportToExcel()`

**راه حل**: استفاده از `static/js/table-export.js`

**صرفه‌جویی**: حذف ~100 خط کد JavaScript تکراری

#### 6.4 Approval/Reject Functions JavaScript
**فایل‌های نیازمند Refactor** (3+ فایل):
- `production/rework_document_list.html` - JavaScript inline برای `approveDocument()`, `rejectDocument()` (~50 خط)
- `production/qc_operations_list.html` - JavaScript inline برای `approveOperation()`, `rejectOperation()` (~80 خط)
- `production/rework_operations_list.html` - JavaScript inline برای `showNotes()` (~20 خط)

**راه حل**: ایجاد `static/js/approval-actions.js` با توابع مشترک

**صرفه‌جویی**: حذف ~150 خط کد JavaScript تکراری

#### 6.5 Modal Dialogs JavaScript
**فایل‌های نیازمند Refactor** (3+ فایل):
- `production/rework.html` - JavaScript inline برای `showNotes()` modal
- `production/qc_operations_list.html` - JavaScript inline برای `showNotes()` modal
- `production/rework_operations_list.html` - JavaScript inline برای `showNotes()` modal

**راه حل**: ایجاد `static/js/modal-dialogs.js` با توابع مشترک

**صرفه‌جویی**: حذف ~50 خط کد JavaScript تکراری

**جمع کل JavaScript**: حدود **30+ فایل** نیازمند refactor

---

### 7. **Inline Event Handlers - عدم استفاده از Event Listeners**

**مشکل**: استفاده از inline event handlers (`onclick`, `onchange`) به جای event listeners:

**فایل‌های نیازمند Refactor**:
- `inventory/purchase_requests.html` - `onclick="window.print()"`
- `inventory/receipt_temporary.html` - `onclick="window.print()"`, `onclick="return confirm(...)"`
- `inventory/items.html` - `onclick="window.print()"`, `onclick="document.getElementById(...).style.display='...'"`
- `inventory/warehouse_requests.html` - `onclick="window.print()"`
- `shared/partials/row_actions.html` - `onclick="return confirm(...)"`
- `shared/generic/generic_list.html` - `onclick="window.print()"`

**راه حل**: 
- ایجاد `static/js/common-actions.js` با توابع مشترک:
  - `printPage()` - برای print functionality
  - `confirmAction(message, callback)` - برای confirmation dialogs
  - `toggleElementVisibility(elementId)` - برای show/hide elements

**صرفه‌جویی**: حذف ~50 خط کد تکراری و بهبود maintainability

---

### 8. **Inline CSS Styles - عدم استفاده از CSS Classes**

**مشکل**: استفاده از inline styles و `<style>` tags در templateها:

**فایل‌های نیازمند Refactor** (20+ فایل):

**ماژول `production`** (5 فایل):
- `production/bom_form.html` - `<style>` tag با CSS inline (~50 خط) + inline `style="..."` attributes
- `production/process_form.html` - `<style>` tag + inline `style="..."` attributes
- `production/performance_record_form.html` - `<style>` tag + inline `style="..."` attributes
- `production/transfer_to_line_form.html` - `<style>` tag + inline `style="..."` attributes
- `production/rework_document_form.html` - `<style>` tag + inline `style="..."` attributes

**ماژول `inventory`** (10 فایل):
- `inventory/purchase_requests.html` - `<style>` tag + inline `style="..."` attributes
- `inventory/receipt_temporary.html` - `<style>` tag + inline `style="..."` attributes
- `inventory/receipt_permanent.html` - `<style>` tag + inline `style="..."` attributes
- `inventory/receipt_consignment.html` - `<style>` tag + inline `style="..."` attributes
- `inventory/warehouse_requests.html` - `<style>` tag + inline `style="..."` attributes
- `inventory/issue_permanent.html` - `<style>` tag + inline `style="..."` attributes
- `inventory/issue_consumption.html` - `<style>` tag + inline `style="..."` attributes
- `inventory/issue_consignment.html` - `<style>` tag + inline `style="..."` attributes
- `inventory/stocktaking_deficit.html` - `<style>` tag + inline `style="..."` attributes
- `inventory/stocktaking_surplus.html` - `<style>` tag + inline `style="..."` attributes
- `inventory/stocktaking_records.html` - `<style>` tag + inline `style="..."` attributes
- `inventory/item_form.html` - inline `style="..."` attributes
- `inventory/receipt_form.html` - inline `style="..."` attributes
- `inventory/issue_form.html` - inline `style="..."` attributes
- `inventory/inventory_balance.html` - `<style>` tag + inline `style="..."` attributes
- `inventory/inventory_balance_details.html` - `<style>` tag + inline `style="..."` attributes

**ماژول `shared`** (3 فایل):
- `shared/generic/generic_detail.html` - `<style>` tag + inline `style="..."` attributes
- `shared/generic/generic_list.html` - `<style>` tag + inline `style="..."` attributes
- `shared/generic/generic_form.html` - inline `style="..."` attributes
- `shared/partials/row_actions.html` - inline `style="..."` attributes
- `shared/partials/stats_cards.html` - inline `style="..."` attributes
- `shared/partials/filter_panel.html` - inline `style="..."` attributes

**ماژول `ticketing`** (2 فایل):
- `ticketing/template_form.html` - `<style>` tag + inline `style="..."` attributes
- `ticketing/category_form.html` - inline `style="..."` attributes

**ماژول `accounting`** (2 فایل):
- `accounting/treasury/account_form.html` - inline `style="..."` attributes
- `accounting/parties/party_form.html` - inline `style="..."` attributes

**ماژول `qc`** (1 فایل):
- `qc/temporary_receipt_rejection_management.html` - `<style>` tag + inline `style="..."` attributes

**سایر فایل‌ها** (3+ فایل):
- `inventory/create_receipt_from_purchase_request.html` - inline `style="..."` attributes
- `inventory/create_issue_from_warehouse_request.html` - inline `style="..."` attributes
- `base.html` - inline `style="..."` attributes

**راه حل**: 
- انتقال CSS به فایل‌های مشترک در `static/css/`
- ایجاد CSS classes مشترک برای الگوهای تکراری
- استفاده از utility classes

**صرفه‌جویی**: حذف ~200 خط CSS تکراری و بهبود maintainability

---

## 📋 لیست کامل فایل‌های نیازمند Refactor

### دسته‌بندی بر اساس نوع

#### 1. Detail Views (39 فایل)
- **inventory**: 15 فایل
- **production**: 8 فایل
- **accounting**: 6 فایل
- **ticketing**: 4 فایل
- **shared**: 6 فایل

#### 2. List Views (8 فایل)
- **accounting**: 6 فایل
- **ticketing**: 2 فایل

#### 3. Form Views (4-5 فایل)
- **accounting**: 4-5 فایل

#### 4. Row Actions (10+ فایل)
- فایل‌های list که row actions را inline می‌نویسند

#### 5. Pagination (5+ فایل)
- فایل‌های list که pagination را override می‌کنند

#### 6. JavaScript Inline (40+ فایل)
- **Formset Management**: 18+ فایل (لیست کامل در بخش 6.1)
- **Cascading Dropdowns**: 10+ فایل (لیست کامل در بخش 6.2)
- **Table Export**: 17+ فایل (لیست کامل در بخش 6.3)
- **Approval/Reject Functions**: 3+ فایل
- **Modal Dialogs**: 3+ فایل

#### 7. Inline Event Handlers (10+ فایل)
- فایل‌های با `onclick`, `onchange` inline handlers

#### 8. Inline CSS Styles (25+ فایل)
- فایل‌های با `<style>` tags و inline `style="..."` attributes (لیست کامل در بخش 8)

---

## 🎯 الگوهای تکراری شناسایی شده

### 1. **Detail View Pattern**
```django
{% extends "shared/base.html" %}
<div class="container-fluid">
  <nav aria-label="breadcrumb">...</nav>
  <div class="card">
    <div class="card-header"><h2>...</h2></div>
    <div class="card-body">
      <div class="info-banner">...</div>
      <div class="form-section">
        <h3>Basic Information</h3>
        <div class="row">
          <div class="col-md-6">
            <div class="form-group">
              <label>...</label>
              <div class="readonly-field">...</div>
            </div>
          </div>
        </div>
      </div>
      <div class="form-section">
        <h3>Audit Information</h3>
        ...
      </div>
      <div class="form-actions">
        <a href="{{ list_url }}" class="btn btn-secondary">Back to List</a>
        <a href="{{ edit_url }}" class="btn btn-primary">Edit</a>
      </div>
    </div>
  </div>
</div>
```

**این الگو در 39 فایل تکرار شده است!**

### 2. **Row Actions Pattern**
```django
{% if show_actions %}
<td>
  <a href="{% url edit_url_name object.pk %}" class="btn btn-secondary">Edit</a>
  <a href="{% url delete_url_name object.pk %}" class="btn btn-primary">Delete</a>
</td>
{% endif %}
```

**این الگو در 10+ فایل تکرار شده است!**

### 3. **Pagination Pattern**
```django
{% if is_paginated %}
<div class="pagination">
  {% if page_obj.has_previous %}
    <a href="?page=1&...">First</a>
    <a href="?page={{ page_obj.previous_page_number }}&...">Previous</a>
  {% endif %}
  <span>Page {{ page_obj.number }} of {{ page_obj.paginator.num_pages }}</span>
  {% if page_obj.has_next %}
    <a href="?page={{ page_obj.next_page_number }}&...">Next</a>
    <a href="?page={{ page_obj.paginator.num_pages }}&...">Last</a>
  {% endif %}
</div>
{% endif %}
```

**این الگو در 5+ فایل تکرار شده است!**

---

## 💡 پیشنهادات Refactoring

### 1. **Migrate Detail Views به Generic Template**

**قبل**:
```django
{% extends "shared/base.html" %}
<div class="container-fluid">
  <nav aria-label="breadcrumb">...</nav>
  <div class="card">...</div>
</div>
```

**بعد**:
```django
{% extends "shared/generic/generic_detail.html" %}
{% block detail_sections %}
<div class="detail-section">
  <h3>Basic Information</h3>
  <div class="detail-field">
    <label>Name</label>
    <div class="readonly-field">{{ object.name }}</div>
  </div>
</div>
{% endblock %}
```

### 2. **استفاده از Row Actions Partial**

**قبل**:
```django
<td>
  <a href="{% url edit_url_name object.pk %}" class="btn btn-secondary">Edit</a>
  <a href="{% url delete_url_name object.pk %}" class="btn btn-primary">Delete</a>
</td>
```

**بعد**:
```django
{% include 'shared/partials/row_actions.html' with object=object feature_code=feature_code detail_url_name=detail_url_name edit_url_name=edit_url_name delete_url_name=delete_url_name %}
```

### 3. **استفاده از Pagination Partial**

**قبل**: Override کردن `pagination` block

**بعد**: استفاده از `shared/partials/pagination.html` که به صورت خودکار query parameters را حفظ می‌کند

---

## 📊 خلاصه آماری

| نوع Refactor | تعداد فایل | اولویت |
|-------------|-----------|--------|
| Detail Views → Generic | 39 | 🔴 بالا |
| JavaScript Inline → Shared Files | 40+ | 🔴 بالا |
| List Views → Generic | 8 | 🟡 متوسط |
| Form Views → Generic | 4-5 | 🟡 متوسط |
| Inline CSS → Shared CSS | 25+ | 🟡 متوسط |
| Inline Event Handlers → JS Files | 10+ | 🟡 متوسط |
| Row Actions → Partial | 10+ | 🟢 پایین |
| Pagination → Partial | 5+ | 🟢 پایین |
| **جمع کل** | **110+ فایل** | |

---

## 🚀 برنامه Refactoring پیشنهادی

### فاز 1: Detail Views (اولویت بالا)
1. Refactor تمام Detail Views در ماژول `inventory` (15 فایل)
2. Refactor تمام Detail Views در ماژول `production` (8 فایل)
3. Refactor تمام Detail Views در ماژول `accounting` (6 فایل)
4. Refactor تمام Detail Views در ماژول `ticketing` (4 فایل)
5. Refactor تمام Detail Views در ماژول `shared` (6 فایل)

**جمع کل**: 39 فایل Detail View

### فاز 2: List Views (اولویت متوسط)
1. Refactor List Views در ماژول `accounting` (6 فایل)
2. Refactor List Views در ماژول `ticketing` (2 فایل)

### فاز 3: Form Views (اولویت متوسط)
1. Refactor Form Views در ماژول `accounting` (4-5 فایل)

### فاز 4: JavaScript Refactoring (اولویت بالا)
1. Refactor Formset Management JavaScript (18+ فایل)
   - استفاده از `static/js/formset.js` و `static/js/formset-table.js`
   - لیست کامل: `production/bom_form.html`, `production/process_form.html`, `production/performance_record_form.html`, `production/transfer_to_line_form.html`, `production/rework_document_form.html`, `inventory/item_form.html`, `inventory/receipt_form.html`, `inventory/issue_form.html`, `inventory/stocktaking_form.html`, `inventory/purchase_request_form.html`, `ticketing/category_form.html`, `ticketing/subcategory_form.html`, `ticketing/template_form.html`, `shared/user_form.html`, `accounting/treasury/account_form.html`, `accounting/parties/party_form.html`, `inventory/create_receipt_from_purchase_request.html`, `inventory/create_issue_from_warehouse_request.html`
2. Refactor Cascading Dropdowns JavaScript (10+ فایل)
   - استفاده از `static/js/cascading-dropdowns.js`
   - لیست کامل: `production/bom_form.html`, `production/process_form.html`, `production/transfer_to_line_form.html`, `inventory/item_form.html`, `inventory/receipt_form.html`, `inventory/issue_form.html`, `inventory/purchase_request_form.html`, `accounting/parties/party_account_form.html`, `inventory/create_receipt_from_purchase_request.html`
3. Refactor Table Export JavaScript (17+ فایل)
   - استفاده از `static/js/table-export.js`
   - لیست کامل: `shared/generic/generic_report.html`, `inventory/inventory_balance.html`, `inventory/inventory_balance_details.html`, `inventory/item_serials.html`, `inventory/purchase_requests.html`, `inventory/receipt_temporary.html`, `inventory/receipt_permanent.html`, `inventory/receipt_consignment.html`, `inventory/warehouse_requests.html`, `inventory/issue_permanent.html`, `inventory/issue_consumption.html`, `inventory/issue_consignment.html`, `inventory/stocktaking_deficit.html`, `inventory/stocktaking_surplus.html`, `inventory/stocktaking_records.html`, `production/performance_record_list.html`, `production/transfer_to_line_list.html`
4. Refactor Approval/Reject Functions (3+ فایل)
   - ایجاد `static/js/approval-actions.js`
   - لیست کامل: `production/rework_document_list.html`, `production/qc_operations_list.html`, `production/rework_operations_list.html`
5. Refactor Modal Dialogs (3+ فایل)
   - ایجاد `static/js/modal-dialogs.js`
   - لیست کامل: `production/rework.html`, `production/qc_operations_list.html`, `production/rework_operations_list.html`

**جمع کل**: 40+ فایل JavaScript Inline

### فاز 5: CSS و Event Handlers (اولویت متوسط)
1. انتقال Inline CSS به فایل‌های مشترک (25+ فایل)
   - لیست کامل: `production/bom_form.html`, `production/process_form.html`, `production/performance_record_form.html`, `production/transfer_to_line_form.html`, `production/rework_document_form.html`, `inventory/purchase_requests.html`, `inventory/receipt_temporary.html`, `inventory/receipt_permanent.html`, `inventory/receipt_consignment.html`, `inventory/warehouse_requests.html`, `inventory/issue_permanent.html`, `inventory/issue_consumption.html`, `inventory/issue_consignment.html`, `inventory/stocktaking_deficit.html`, `inventory/stocktaking_surplus.html`, `inventory/stocktaking_records.html`, `inventory/item_form.html`, `inventory/receipt_form.html`, `inventory/issue_form.html`, `inventory/inventory_balance.html`, `inventory/inventory_balance_details.html`, `shared/generic/generic_detail.html`, `shared/generic/generic_list.html`, `shared/generic/generic_form.html`, `shared/partials/row_actions.html`, `shared/partials/stats_cards.html`, `shared/partials/filter_panel.html`, `ticketing/template_form.html`, `ticketing/category_form.html`, `accounting/treasury/account_form.html`, `accounting/parties/party_form.html`, `qc/temporary_receipt_rejection_management.html`, `inventory/create_receipt_from_purchase_request.html`, `inventory/create_issue_from_warehouse_request.html`, `base.html`
2. جایگزینی Inline Event Handlers با Event Listeners (10+ فایل)
   - ایجاد `static/js/common-actions.js`
   - لیست کامل: `inventory/purchase_requests.html`, `inventory/receipt_temporary.html`, `inventory/items.html`, `inventory/warehouse_requests.html`, `shared/partials/row_actions.html`, `shared/generic/generic_list.html`

### فاز 6: Partials (اولویت پایین)
1. جایگزینی Row Actions inline با partial
2. جایگزینی Pagination override با partial

---

## 📝 نکات مهم

1. **Generic Detail Template**: باید blockهای زیر را پشتیبانی کند:
   - `detail_sections` - برای sections اصلی
   - `info_banner` - برای banner اطلاعات
   - `detail_actions` - برای action buttons

2. **Partials**: باید query parameters را به صورت خودکار حفظ کنند

3. **Backward Compatibility**: باید مطمئن شویم که تغییرات backward compatible هستند

4. **Testing**: باید تمام صفحات را بعد از refactor تست کنیم

---

---

## 📝 JavaScript Refactoring Details

### فایل‌های JavaScript مشترک موجود

✅ **فایل‌های ساخته شده**:
- `static/js/formset.js` - مدیریت formsets (add/remove rows, update indices)
- `static/js/cascading-dropdowns.js` - مدیریت cascading dropdowns
- `static/js/table-export.js` - export جدول به CSV/Excel
- `static/js/formset-table.js` - مدیریت formset در جداول

⏳ **فایل‌های نیازمند ساخت**:
- `static/js/approval-actions.js` - توابع approve/reject مشترک
- `static/js/modal-dialogs.js` - مدیریت modal dialogs
- `static/js/common-actions.js` - توابع مشترک (print, confirm, toggle visibility)

### مثال Refactoring JavaScript

#### قبل (Inline JavaScript):
```javascript
<script>
function addFormsetRow(prefix) {
  const totalForms = document.getElementById(`id_${prefix}-TOTAL_FORMS`);
  const formCount = parseInt(totalForms.value);
  // ... 50+ خط کد تکراری
}
</script>
```

#### بعد (استفاده از فایل مشترک):
```django
{% load static %}
<script src="{% static 'js/formset.js' %}"></script>
<script>
document.addEventListener('DOMContentLoaded', function() {
  // فقط initialization code
  const addButton = document.getElementById('add-row-btn');
  addButton.addEventListener('click', function() {
    addFormsetRow('formset', '#formset-template-row');
  });
});
</script>
```

### مثال Refactoring Cascading Dropdowns

#### قبل (Inline JavaScript):
```javascript
<script>
itemTypeSelect.addEventListener('change', function() {
  const selectedType = this.value;
  fetch('/inventory/api/filtered-categories/?type_id=' + selectedType)
    .then(response => response.json())
    .then(data => {
      // ... 30+ خط کد تکراری
    });
});
</script>
```

#### بعد (استفاده از فایل مشترک):
```django
{% load static %}
<script src="{% static 'js/cascading-dropdowns.js' %}"></script>
<script>
document.addEventListener('DOMContentLoaded', function() {
  initCascadingDropdown(
    '#id_item_type',
    '#id_item_category',
    '/inventory/api/filtered-categories/',
    { parentField: 'type_id' }
  );
});
</script>
```

---

## 📝 CSS Refactoring Details

### الگوهای CSS تکراری

**مشکل**: CSS inline در templateها:
- `<style>` tags در templateها
- Inline `style="..."` attributes
- CSS تکراری برای buttons، cards، tables

**راه حل**:
- انتقال CSS به `static/css/`
- ایجاد utility classes
- استفاده از CSS variables برای colors و spacing

### مثال Refactoring CSS

#### قبل (Inline CSS):
```django
<style>
.item-filters input[type="text"] {
  outline: none;
  border-color: #2563eb;
  background-color: #ffffff;
}
</style>
```

#### بعد (CSS مشترک):
```django
{% load static %}
<link rel="stylesheet" href="{% static 'css/forms.css' %}">
<!-- استفاده از classهای مشترک -->
```

---

**آخرین به‌روزرسانی**: 2024-12-06  
**تکمیل شده**: ✅ لیست کامل فایل‌های Detail Views (39 فایل)، JavaScript Inline (40+ فایل)، و CSS Inline (25+ فایل) اضافه شد

