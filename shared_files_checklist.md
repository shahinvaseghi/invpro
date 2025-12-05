# چک‌لیست فایل‌های مشترک - Backend و Frontend

این چک‌لیست برای پیگیری پیشرفت ساخت فایل‌های مشترک استفاده می‌شود.

**نکته**: تمام فایل‌های مشترک در ماژول `shared` قرار می‌گیرند.

---

## بخش ۱: فایل‌های Backend

### ۱.۱ Base View Classes (`shared/views/base.py`)

**وضعیت فایل**: ✅ موجود (بهبود و تکمیل شده)

- [x] **BaseListView**
  - [x] Attributes: model, search_fields, filter_fields, feature_code, permission_field, default_status_filter, default_order_by, paginate_by
  - [x] Method: get_queryset() - apply company filter, search, filters, permissions
  - [x] Method: get_context_data() - setup standard context
  - [x] Hook methods: get_breadcrumbs(), get_page_title(), get_stats(), apply_custom_filters(), get_prefetch_related(), get_select_related()
  - [ ] تست واحد (Unit Tests)

- [x] **BaseCreateView**
  - [x] Attributes: model, form_class, success_url, feature_code, auto_set_company, auto_set_created_by, require_active_company, success_message
  - [x] Method: form_valid() - auto-set company_id, created_by, show success message
  - [x] Method: get_context_data() - setup standard context
  - [x] Method: get_form_kwargs() - add company_id to form kwargs
  - [x] Method: validate_company() - validate active company exists (در AutoSetFieldsMixin)
  - [x] Hook methods: get_breadcrumbs(), get_form_title()
  - [ ] تست واحد

- [x] **BaseUpdateView**
  - [x] Attributes: model, form_class, success_url, feature_code, auto_set_edited_by, success_message
  - [x] Method: form_valid() - auto-set edited_by, show success message
  - [x] Method: get_context_data() - setup standard context
  - [x] Method: get_form_kwargs() - add company_id to form kwargs
  - [x] Hook methods: get_breadcrumbs(), get_form_title()
  - [ ] تست واحد

- [x] **BaseDeleteView**
  - [x] Attributes: model, success_url, feature_code, template_name, success_message
  - [x] Method: delete() - show success message (در SuccessMessageMixin)
  - [x] Method: get_context_data() - setup standard context
  - [x] Hook methods: get_object_details(), get_breadcrumbs(), validate_deletion()
  - [ ] تست واحد

- [x] **BaseDetailView**
  - [x] Attributes: model, feature_code, template_name
  - [x] Method: get_queryset() - apply company filter and permissions
  - [x] Method: get_context_data() - setup standard context
  - [x] Hook methods: get_breadcrumbs(), get_page_title(), can_edit_object()
  - [ ] تست واحد

- [x] **BaseFormsetCreateView**
  - [x] Attributes: formset_class, formset_prefix
  - [x] Method: get_context_data() - add formset to context
  - [x] Method: form_valid() - save formset with main object
  - [x] Method: get_formset_kwargs() - hook method
  - [ ] تست واحد

- [x] **BaseFormsetUpdateView**
  - [x] Attributes: formset_class, formset_prefix
  - [x] Method: get_context_data() - add formset to context
  - [x] Method: form_valid() - save formset with main object
  - [x] Method: get_formset_kwargs() - hook method
  - [ ] تست واحد

- [x] **BaseDocumentListView**
  - [x] Attributes: prefetch_lines, stats_enabled
  - [x] Method: get_queryset() - prefetch lines and related objects (در get_prefetch_related)
  - [x] Method: get_stats() - calculate stats for documents
  - [ ] تست واحد

- [x] **BaseDocumentCreateView**
  - [x] Method: form_valid() - save document header and lines (از BaseFormsetCreateView)
  - [x] Method: save_lines_formset() - hook method
  - [ ] تست واحد

- [x] **BaseDocumentUpdateView**
  - [x] Method: form_valid() - save document header and lines (از BaseFormsetUpdateView)
  - [x] Method: save_lines_formset() - hook method
  - [ ] تست واحد

---

### ۱.۲ Filter Functions (`shared/filters.py`)

**وضعیت فایل**: ✅ ساخته شده

- [x] **apply_search(queryset, search_query, fields)**
  - [x] Apply search across multiple fields using Q objects
  - [x] Handle empty search query
  - [ ] تست واحد

- [x] **apply_status_filter(queryset, status_value)**
  - [x] Apply status filter (active/inactive)
  - [x] Handle empty status value
  - [ ] تست واحد

- [x] **apply_company_filter(queryset, company_id)**
  - [x] Apply company filter
  - [x] Handle None company_id
  - [ ] تست واحد

- [x] **apply_date_range_filter(queryset, date_from, date_to, field_name)**
  - [x] Apply date range filter
  - [x] Handle None dates
  - [ ] تست واحد

- [x] **apply_multi_field_filter(queryset, request, filter_map)**
  - [x] Apply multiple filters based on request.GET
  - [x] Handle missing filter_map entries
  - [ ] تست واحد

---

### ۱.۳ View Mixins (`shared/mixins.py`)

**وضعیت فایل**: ✅ موجود (بهبود یافته)

- [x] **PermissionFilterMixin**
  - [x] Method: filter_queryset_by_permissions(queryset, feature_code, owner_field)
  - [x] Logic: filter based on view_all, view_own, view_same_group permissions
  - [x] Handle superuser case
  - [ ] تست واحد

- [x] **CompanyScopedViewMixin** (بهبود)
  - [x] Method: get_queryset() - filter by active_company_id
  - [x] Method: get_context_data() - add active_module
  - [ ] تست واحد

- [x] **AutoSetFieldsMixin**
  - [x] Method: form_valid() - auto-set company_id, created_by, edited_by
  - [x] Handle optional fields
  - [ ] تست واحد

- [x] **SuccessMessageMixin** (بهبود)
  - [x] Method: form_valid() - show success message
  - [x] Method: delete() - show success message
  - [ ] تست واحد

---

### ۱.۴ Base Form Classes (`shared/forms/base.py`)

**وضعیت فایل**: ✅ ساخته شده

- [x] **BaseModelForm**
  - [x] Method: __init__() - apply default widget styling automatically
  - [x] Logic: Checkbox inputs → form-check-input class
  - [x] Logic: Other inputs → form-control class
  - [ ] تست واحد

- [x] **BaseFormset** (helper class)
  - [x] Method: __init__() - set request on all forms
  - [x] Method: save_with_company(company_id) - save all forms with company_id
  - [ ] تست واحد

---

### ۱.۵ API View Classes (`shared/views/api.py`)

**وضعیت فایل**: ✅ موجود (تکمیل شده)

- [x] **BaseAPIView**
  - [x] Method: get_company_id() - get active company from session
  - [x] Method: json_response(data, status) - return JsonResponse
  - [x] Method: error_response(message, status) - return error JsonResponse
  - [x] Method: success_response(message, data) - return success JsonResponse
  - [x] Method: validate_company() - validate active company exists
  - [x] Method: get_user() - get current user
  - [ ] تست واحد

- [x] **BaseListAPIView**
  - [x] Method: get(request) - return list of objects as JSON
  - [x] Method: filter_queryset(queryset) - apply filters
  - [x] Method: serialize_object(obj) - serialize single object
  - [x] Method: get_queryset() - get queryset
  - [x] Support pagination
  - [ ] تست واحد

- [x] **BaseDetailAPIView**
  - [x] Method: get(request, pk) - return single object as JSON
  - [x] Method: get_object(**kwargs) - get object instance
  - [x] Method: serialize_object(obj) - serialize object
  - [x] Support custom lookup fields
  - [ ] تست واحد

---

### ۱.۶ View Helper Functions (`shared/utils/view_helpers.py`)

**وضعیت فایل**: ✅ موجود (تکمیل شده)

- [x] **get_breadcrumbs(module_name, items)**
  - [x] Generate breadcrumbs list
  - [x] Handle empty items
  - [x] Add Dashboard link automatically
  - [ ] تست واحد

- [x] **get_success_message(action, model_name)**
  - [x] Generate success message
  - [x] Support i18n
  - [x] Support created/updated/deleted actions
  - [ ] تست واحد

- [x] **validate_active_company(request)**
  - [x] Validate active company exists
  - [x] Return (is_valid, error_message)
  - [ ] تست واحد

- [x] **get_table_headers(fields)**
  - [x] Generate table headers list
  - [x] Handle different field formats (string, dict)
  - [ ] تست واحد

---

## بخش ۲: فایل‌های Frontend

### ۲.۱ JavaScript Files

#### `static/js/formset.js`

**وضعیت فایل**: ✅ موجود (تکمیل شده)

- [x] **addFormsetRow(prefix, templateSelector, options)**
  - [x] Clone template row
  - [x] Update form indices
  - [x] Increment TOTAL_FORMS
  - [x] Reindex all rows
  - [x] Handle errors
  - [x] Handle minRows/maxRows limits
  - [ ] تست (Manual testing)

- [x] **removeFormsetRow(button, prefix, options)**
  - [x] Remove row from formset
  - [x] Update TOTAL_FORMS
  - [x] Reindex all rows
  - [x] Handle minimum rows requirement
  - [x] Handle DELETE field
  - [ ] تست

- [x] **updateFormsetTotal(prefix)**
  - [x] Update TOTAL_FORMS hidden input
  - [x] Handle missing TOTAL_FORMS input
  - [x] Count visible rows
  - [ ] تست

- [x] **reindexFormset(prefix)**
  - [x] Reindex all formset rows
  - [x] Update all field names and IDs
  - [x] Update line numbers
  - [ ] تست

- [x] **initFormset(prefix, templateSelector, options)**
  - [x] Initialize formset with event handlers
  - [x] Handle minRows requirement
  - [x] Handle maxRows limit
  - [x] Attach event listeners
  - [x] Support custom button selectors
  - [ ] تست

---

#### `static/js/cascading-dropdowns.js`

**وضعیت فایل**: ✅ موجود (تکمیل شده)

- [x] **initCascadingDropdown(parentSelect, childSelect, apiUrl, options)**
  - [x] Listen to parent change event
  - [x] Fetch options from API
  - [x] Populate child dropdown
  - [x] Trigger onChange callback
  - [x] Handle API errors
  - [x] Handle loading state
  - [x] Support different response formats (array, results, data)
  - [x] Initial load if parent has value
  - [ ] تست

- [x] **updateDropdownOptions(selectElement, options, placeholder, valueField, labelField)**
  - [x] Clear existing options
  - [x] Add placeholder option
  - [x] Add options from array
  - [x] Handle different option formats (string, object)
  - [ ] تست

- [x] **clearDropdown(selectElement, placeholder)**
  - [x] Clear all options
  - [x] Add placeholder option
  - [ ] تست

- [x] **initCascadingDropdowns()**
  - [x] Auto-initialize from data attributes
  - [x] Support data-cascading-parent attribute
  - [ ] تست

---

#### `static/js/table-export.js`

**وضعیت فایل**: ✅ موجود (تکمیل شده)

- [x] **exportTableToCSV(tableId, filename, options)**
  - [x] Extract table data
  - [x] Convert to CSV format
  - [x] Handle special characters
  - [x] Trigger download
  - [x] Support UTF-8 BOM for Persian/Arabic characters
  - [x] Support configurable delimiter
  - [x] Skip hidden columns option
  - [ ] تست

- [x] **exportTableToExcel(tableId, filename, options)**
  - [x] Extract table data
  - [x] Convert to Excel format (CSV with .xlsx extension)
  - [x] Handle formatting
  - [x] Trigger download
  - [x] Note: For advanced Excel features, integrate SheetJS library
  - [ ] تست

- [x] **printTable(tableId, options)**
  - [x] Open print dialog with table content
  - [x] Handle print styling
  - [x] Support custom title and date
  - [x] Remove action buttons and hidden columns
  - [ ] تست

---

#### `static/js/form-helpers.js`

**وضعیت فایل**: ✅ موجود (تکمیل شده)

- [x] **initAutoSubmit(selectElement, options)**
  - [x] Auto-submit form when select changes
  - [x] Handle form validation
  - [x] Support configurable delay
  - [x] Support validation before submit option
  - [ ] تست

- [x] **initDatePicker(inputElement, options)**
  - [x] Initialize date picker (Jalali or Gregorian)
  - [x] Handle date format
  - [x] Handle locale
  - [x] Support minDate/maxDate
  - [x] Support time picker option
  - [x] Note: Requires integration with date picker library
  - [ ] تست

- [x] **validateForm(formElement, options)**
  - [x] Validate form before submission
  - [x] Show validation errors
  - [x] Return boolean (is valid)
  - [x] Focus first error field
  - [x] Use HTML5 validation API
  - [ ] تست

- [x] **showFormErrors(formElement, errors, options)**
  - [x] Display form errors
  - [x] Clear previous errors
  - [x] Handle field-specific errors
  - [x] Support form-level errors
  - [x] Configurable CSS classes
  - [ ] تست

- [x] **clearFormErrors(formElement, options)**
  - [x] Clear all form errors
  - [x] Remove error classes
  - [x] Hide error messages
  - [ ] تست

---

### ۲.۲ Template Partials

#### `templates/shared/partials/row_actions.html`

**وضعیت فایل**: ✅ موجود (تکمیل شده)

- [x] پشتیبانی از `get_available_actions()` method در model
- [x] نمایش دکمه‌ها بر اساس permissions
- [x] پشتیبانی از custom actions
- [x] Styling یکپارچه
- [x] Handle missing URL names
- [x] پشتیبانی از EditLockProtectedMixin (is_locked)
- [x] پشتیبانی از show_icons option
- [x] Block: row_actions_extra برای actions اضافی
- [ ] تست (Manual testing)

---

#### `templates/shared/partials/filter_panel.html`

**وضعیت فایل**: ✅ موجود (تکمیل شده)

- [x] نمایش پنل فیلتر مشترک
- [x] Block: filter_fields - برای فیلترهای اختصاصی
- [x] Block: extra_filters - برای فیلترهای اضافی
- [x] نمایش search input
- [x] نمایش status filter (اگر enabled باشد)
- [x] دکمه Apply Filter
- [x] دکمه Clear Filter
- [x] حفظ فیلترهای فعلی در URL
- [x] Responsive design
- [ ] تست

---

#### `templates/shared/partials/stats_cards.html`

**وضعیت فایل**: ✅ موجود (تکمیل شده)

- [x] نمایش کارت‌های آمار (stats cards)
- [x] پشتیبانی از stats dict
- [x] پشتیبانی از stats_labels dict
- [x] پشتیبانی از stats_icons (اختیاری)
- [x] Styling یکپارچه
- [x] Handle missing stats
- [x] Responsive grid layout
- [ ] تست

---

#### `templates/shared/partials/pagination.html`

**وضعیت فایل**: ✅ موجود (تکمیل شده)

- [x] نمایش pagination مشترک
- [x] حفظ query parameters در pagination links
- [x] نمایش page numbers
- [x] دکمه Previous/Next
- [x] نمایش اطلاعات pagination (مثلاً "صفحه 1 از 10")
- [x] Handle RTL layout
- [x] Smart page number display (ellipsis for large ranges)
- [x] Disabled state for Previous/Next when not available
- [ ] تست

---

#### `templates/shared/partials/empty_state.html`

**وضعیت فایل**: ✅ موجود (تکمیل شده)

- [x] نمایش empty state مشترک
- [x] نمایش icon (emoji or icon class)
- [x] نمایش title
- [x] نمایش message
- [x] دکمه Create (اگر create_url موجود باشد)
- [x] Block: empty_state_extra برای محتوای اضافی
- [x] Styling یکپارچه
- [ ] تست

---

### ۲.۳ Template Tags

#### `shared/templatetags/view_tags.py`

**وضعیت فایل**: ✅ موجود (تکمیل شده)

- [x] **{% get_breadcrumbs module items %}**
  - [x] Generate breadcrumbs list
  - [x] Handle empty items
  - [x] Uses view_helpers.get_breadcrumbs
  - [ ] تست

- [x] **{% get_table_headers fields %}**
  - [x] Generate table headers
  - [x] Handle different field formats
  - [x] Uses view_helpers.get_table_headers
  - [ ] تست

- [x] **{% can_action object action feature_code %}**
  - [x] Check if user can perform action
  - [x] Handle missing permissions
  - [x] Support get_available_actions method
  - [x] Support feature_code permissions
  - [x] Support model-level permissions
  - [ ] تست

- [x] **{% get_object_actions object feature_code %}**
  - [x] Get available actions for object
  - [x] Return list of actions
  - [x] Support get_available_actions method
  - [x] Auto-generate URLs for common patterns
  - [x] Filter by permissions
  - [ ] تست

- [x] **{{ dict|get_item:key }}**
  - [x] Get item from dictionary
  - [x] Handle missing keys
  - [ ] تست

---

## بخش ۳: بهبود Templateهای موجود

### `templates/shared/generic/generic_list.html`

**وضعیت فایل**: ✅ موجود (بهبود یافته)

- [x] استفاده از `filter_panel.html` partial
- [x] استفاده از `stats_cards.html` partial (اگر stats موجود باشد)
- [x] استفاده از `pagination.html` partial
- [x] استفاده از `empty_state.html` partial
- [x] استفاده از `row_actions.html` partial
- [x] بهبود responsive design
- [ ] تست

---

### `templates/shared/generic/generic_form.html`

**وضعیت فایل**: ✅ موجود (بهبود یافته)

- [x] بهبود form styling
- [x] بهبود error display (error-message class, is-invalid class)
- [x] بهبود responsive design (mobile-friendly)
- [x] بهبود form-actions layout
- [ ] تست

---

### `templates/shared/generic/generic_detail.html`

**وضعیت فایل**: ✅ موجود (بهبود یافته)

- [x] بهبود detail display
- [x] بهبود responsive design (mobile-friendly)
- [x] بهبود info-banner layout
- [x] بهبود form-actions layout
- [ ] تست

---

### `templates/shared/generic/generic_confirm_delete.html`

**وضعیت فایل**: ✅ موجود (بهبود یافته)

- [x] بهبود confirmation display
- [x] بهبود object_details display
- [x] بهبود responsive design (mobile-friendly)
- [x] بهبود form-actions layout
- [ ] تست

---

## بخش ۴: تست‌ها

### Unit Tests

- [ ] تست تمام Base View Classes
- [ ] تست تمام Filter Functions
- [ ] تست تمام Mixins
- [ ] تست تمام Form Base Classes
- [ ] تست تمام API View Classes
- [ ] تست تمام Helper Functions
- [ ] تست تمام Template Tags

### Integration Tests

- [ ] تست استفاده از BaseListView در یک ماژول واقعی
- [ ] تست استفاده از BaseCreateView در یک ماژول واقعی
- [ ] تست استفاده از BaseFormsetCreateView در یک ماژول واقعی
- [ ] تست JavaScript formset در یک template واقعی
- [ ] تست JavaScript cascading dropdowns در یک template واقعی

### Manual Testing

- [ ] تست UI/UX تمام templateهای بهبود یافته
- [ ] تست JavaScript functions در مرورگر
- [ ] تست responsive design
- [ ] تست RTL layout

---

## بخش ۵: مستندسازی

- [ ] مستندسازی تمام Base View Classes
- [ ] مستندسازی تمام Filter Functions
- [ ] مستندسازی تمام Mixins
- [ ] مستندسازی تمام JavaScript Functions
- [ ] مستندسازی تمام Template Partials
- [ ] مستندسازی تمام Template Tags
- [ ] ایجاد مثال‌های استفاده (Usage Examples)
- [ ] ایجاد راهنمای Migration (Migration Guide)

---

## خلاصه پیشرفت

### Backend Files

- **کل فایل‌ها**: 6 فایل
- **فایل‌های موجود (بهبود یافته)**: 3 فایل
- [x] `shared/views/base.py` - 10 کلاس ✅
- [x] `shared/mixins.py` - 4 mixin ✅
- [x] `shared/forms/base.py` - 2 کلاس ✅
- **فایل‌های جدید**: 3 فایل
- [x] `shared/filters.py` - 5 تابع ✅
- [x] `shared/views/api.py` - 3 کلاس ✅
- [x] `shared/utils/view_helpers.py` - 4 تابع ✅

### Frontend Files

- **JavaScript Files**: 4 فایل
- [x] `static/js/formset.js` - 5 تابع ✅
- [x] `static/js/cascading-dropdowns.js` - 3 تابع + initCascadingDropdowns ✅
- [x] `static/js/table-export.js` - 3 تابع ✅
- [x] `static/js/form-helpers.js` - 5 تابع ✅

- **Template Partials**: 5 فایل
- [x] `templates/shared/partials/row_actions.html` - بهبود ✅
- [x] `templates/shared/partials/filter_panel.html` - جدید ✅
- [x] `templates/shared/partials/stats_cards.html` - جدید ✅
- [x] `templates/shared/partials/pagination.html` - بهبود ✅
- [x] `templates/shared/partials/empty_state.html` - جدید ✅

- **Template Tags**: 1 فایل
- [x] `shared/templatetags/view_tags.py` - 5 tags ✅

- **Templateهای موجود (بهبود یافته)**: 4 فایل
- [x] `templates/shared/generic/generic_list.html` ✅
- [x] `templates/shared/generic/generic_form.html` ✅
- [x] `templates/shared/generic/generic_detail.html` ✅
- [x] `templates/shared/generic/generic_confirm_delete.html` ✅

---

**مجموع فایل‌ها**: 20 فایل
- **Backend**: 6 فایل (3 موجود + 3 جدید)
- **Frontend**: 14 فایل (4 JS + 5 partials + 1 template tags + 4 templates)

---

**تاریخ ایجاد**: 2024  
**آخرین به‌روزرسانی**: 2024  
**وضعیت**: در حال پیاده‌سازی

---

## پیشرفت فعلی

### ✅ کارهای انجام شده (Backend Core):

1. ✅ `shared/filters.py` - تمام توابع فیلتر ساخته شد
2. ✅ `shared/mixins.py` - 4 mixin جدید اضافه شد
3. ✅ `shared/forms/base.py` - BaseModelForm و BaseFormset ساخته شد
4. ✅ `shared/views/base.py` - تمام 10 Base View Class ساخته شد:
   - BaseListView
   - BaseCreateView
   - BaseUpdateView
   - BaseDeleteView
   - BaseDetailView
   - BaseFormsetCreateView
   - BaseFormsetUpdateView
   - BaseDocumentListView
   - BaseDocumentCreateView
   - BaseDocumentUpdateView
5. ✅ `shared/views/api.py` - تمام 3 Base API View Class ساخته شد:
   - BaseAPIView
   - BaseListAPIView
   - BaseDetailAPIView
6. ✅ `shared/utils/view_helpers.py` - تمام 4 Helper Function ساخته شد

### ✅ کارهای انجام شده (Frontend Core):

1. ✅ `static/js/formset.js` - تمام 5 تابع ساخته شد
2. ✅ `static/js/cascading-dropdowns.js` - تمام توابع ساخته شد

### ✅ کارهای انجام شده (Frontend Core):

1. ✅ `static/js/formset.js` - تمام 5 تابع ساخته شد
2. ✅ `static/js/cascading-dropdowns.js` - تمام توابع ساخته شد
3. ✅ `static/js/table-export.js` - تمام 3 تابع ساخته شد
4. ✅ `static/js/form-helpers.js` - تمام 5 تابع ساخته شد
5. ✅ Template partials - تمام 4 partial ساخته شد:
   - filter_panel.html
   - stats_cards.html
   - pagination.html
   - empty_state.html
6. ✅ Template tags - `view_tags.py` با 5 tag ساخته شد

### ⏳ کارهای باقی‌مانده:

**Frontend:**
- [x] بهبود `templates/shared/partials/row_actions.html` ✅
- [x] بهبود templateهای generic موجود ✅
- [ ] تست‌های manual برای JavaScript functions
- [ ] تست‌های manual برای template partials

