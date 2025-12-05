# فایل‌های مشترک برای پیاده‌سازی - Backend و Frontend

این سند مشخص می‌کند که چه فایل‌های مشترک باید برای backend و frontend ساخته شوند تا معماری مشترک لیست‌ها و فرم‌ها پیاده‌سازی شود.

**نکته مهم**: تمام فایل‌های مشترک در ماژول `shared` قرار می‌گیرند و سایر ماژول‌ها از آن‌ها استفاده می‌کنند.

---

## بخش ۱: فایل‌های Backend مشترک

### ۱.۱ Base View Classes

#### `shared/views/base.py` (بهبود و تکمیل)

**وضعیت**: این فایل **قبلاً وجود دارد** اما باید **بهبود و تکمیل** شود.

**کلاس‌های جدید که باید اضافه شوند**:

1. **`BaseListView`**
   - ارث‌بری از: `LoginRequiredMixin`, `ListView`
   - Attributes:
     - `model` (required)
     - `search_fields = []` (list of field names for search)
     - `filter_fields = []` (list of field names for filtering)
     - `feature_code` (required)
     - `permission_field = 'created_by'` (field name for permission filtering)
     - `default_status_filter = True` (enable/disable status filter)
     - `default_order_by = []` (default ordering)
     - `paginate_by = 50`
   - Methods:
     - `get_queryset()` - apply company filter, search, filters, permissions
     - `get_context_data()` - setup standard context (page_title, breadcrumbs, etc.)
     - `get_breadcrumbs()` - hook method for custom breadcrumbs
     - `get_page_title()` - hook method for custom page title
     - `get_stats()` - hook method for stats calculation
     - `apply_custom_filters(queryset)` - hook method for custom filters
     - `get_prefetch_related()` - hook method for prefetch_related
     - `get_select_related()` - hook method for select_related

2. **`BaseCreateView`**
   - ارث‌بری از: `LoginRequiredMixin`, `CreateView`
   - Attributes:
     - `model` (required)
     - `form_class` (required)
     - `success_url` (required)
     - `feature_code` (required)
     - `auto_set_company = True`
     - `auto_set_created_by = True`
     - `require_active_company = True`
     - `success_message = None` (override in subclass)
   - Methods:
     - `form_valid()` - auto-set company_id, created_by, show success message
     - `get_context_data()` - setup standard context (form_title, breadcrumbs, cancel_url)
     - `get_form_kwargs()` - add company_id to form kwargs
     - `validate_company()` - validate active company exists
     - `get_breadcrumbs()` - hook method
     - `get_form_title()` - hook method

3. **`BaseUpdateView`**
   - ارث‌بری از: `EditLockProtectedMixin`, `LoginRequiredMixin`, `UpdateView`
   - Attributes:
     - `model` (required)
     - `form_class` (required)
     - `success_url` (required)
     - `feature_code` (required)
     - `auto_set_edited_by = True`
     - `success_message = None` (override in subclass)
   - Methods:
     - `form_valid()` - auto-set edited_by, show success message
     - `get_context_data()` - setup standard context
     - `get_form_kwargs()` - add company_id to form kwargs
     - `get_breadcrumbs()` - hook method
     - `get_form_title()` - hook method

4. **`BaseDeleteView`**
   - ارث‌بری از: `LoginRequiredMixin`, `DeleteView`
   - Attributes:
     - `model` (required)
     - `success_url` (required)
     - `feature_code` (required)
     - `template_name = 'shared/generic/generic_confirm_delete.html'`
     - `success_message = None` (override in subclass)
   - Methods:
     - `delete()` - show success message
     - `get_context_data()` - setup standard context (delete_title, confirmation_message, object_details, cancel_url)
     - `get_object_details()` - hook method for custom object details
     - `get_breadcrumbs()` - hook method
     - `validate_deletion()` - hook method for custom validation

5. **`BaseDetailView`**
   - ارث‌بری از: `LoginRequiredMixin`, `DetailView`
   - Attributes:
     - `model` (required)
     - `feature_code` (required)
     - `template_name = 'shared/generic/generic_detail.html'`
   - Methods:
     - `get_queryset()` - apply company filter and permissions
     - `get_context_data()` - setup standard context (page_title, breadcrumbs, list_url, edit_url, can_edit)
     - `get_breadcrumbs()` - hook method
     - `get_page_title()` - hook method
     - `can_edit_object()` - check if object can be edited

6. **`BaseFormsetCreateView`**
   - ارث‌بری از: `BaseCreateView`
   - Attributes:
     - `formset_class` (required)
     - `formset_prefix = 'formset'`
   - Methods:
     - `get_context_data()` - add formset to context
     - `form_valid()` - save formset with main object
     - `get_formset_kwargs()` - hook method for formset kwargs

7. **`BaseFormsetUpdateView`**
   - ارث‌بری از: `BaseUpdateView`
   - Attributes:
     - `formset_class` (required)
     - `formset_prefix = 'formset'`
   - Methods:
     - `get_context_data()` - add formset to context
     - `form_valid()` - save formset with main object
     - `get_formset_kwargs()` - hook method for formset kwargs

8. **`BaseDocumentListView`** (برای اسناد با lines)
   - ارث‌بری از: `BaseListView`
   - Attributes:
     - `prefetch_lines = True`
     - `stats_enabled = True`
   - Methods:
     - `get_queryset()` - prefetch lines and related objects
     - `get_stats()` - calculate stats for documents

9. **`BaseDocumentCreateView`** (برای اسناد با lines)
   - ارث‌بری از: `BaseFormsetCreateView`
   - Methods:
     - `form_valid()` - save document header and lines
     - `save_lines_formset()` - hook method for saving lines

10. **`BaseDocumentUpdateView`** (برای اسناد با lines)
    - ارث‌بری از: `BaseFormsetUpdateView`
    - Methods:
      - `form_valid()` - save document header and lines
      - `save_lines_formset()` - hook method for saving lines

---

#### `shared/filters.py` (جدید)

**وضعیت**: این فایل **باید ساخته شود**.

**توابع مشترک**:

1. **`apply_search(queryset, search_query, fields)`**
   - Apply search across multiple fields using Q objects
   - Parameters:
     - `queryset`: Django queryset
     - `search_query`: string search query
     - `fields`: list of field names to search in
   - Returns: filtered queryset

2. **`apply_status_filter(queryset, status_value)`**
   - Apply status filter (active/inactive)
   - Parameters:
     - `queryset`: Django queryset
     - `status_value`: '0' or '1' or empty string
   - Returns: filtered queryset

3. **`apply_company_filter(queryset, company_id)`**
   - Apply company filter
   - Parameters:
     - `queryset`: Django queryset
     - `company_id`: company ID from session
   - Returns: filtered queryset

4. **`apply_date_range_filter(queryset, date_from, date_to, field_name='created_at')`**
   - Apply date range filter
   - Parameters:
     - `queryset`: Django queryset
     - `date_from`: start date
     - `date_to`: end date
     - `field_name`: field name to filter on
   - Returns: filtered queryset

5. **`apply_multi_field_filter(queryset, request, filter_map)`**
   - Apply multiple filters based on request.GET
   - Parameters:
     - `queryset`: Django queryset
     - `request`: Django request object
     - `filter_map`: dict mapping GET param names to field names
   - Returns: filtered queryset

---

#### `shared/mixins.py` (بهبود و تکمیل)

**وضعیت**: این فایل **قبلاً وجود دارد** اما باید **بهبود** شود.

**Mixinهای جدید که باید اضافه شوند**:

1. **`PermissionFilterMixin`**
   - Method: `filter_queryset_by_permissions(queryset, feature_code, owner_field='created_by')`
   - Logic: filter based on view_all, view_own, view_same_group permissions
   - Use: در BaseListView

2. **`CompanyScopedViewMixin`** (بهبود)
   - Method: `get_queryset()` - filter by active_company_id
   - Method: `get_context_data()` - add active_module
   - Use: در تمام Base views

3. **`AutoSetFieldsMixin`**
   - Method: `form_valid()` - auto-set company_id, created_by, edited_by
   - Use: در BaseCreateView و BaseUpdateView

4. **`SuccessMessageMixin`** (بهبود Django's mixin)
   - Method: `form_valid()` - show success message
   - Method: `delete()` - show success message
   - Use: در BaseCreateView, BaseUpdateView, BaseDeleteView

---

#### `shared/views/api.py` (جدید)

**وضعیت**: این فایل **باید ساخته شود**.

**کلاس‌های جدید**:

1. **`BaseAPIView`**
   - ارث‌بری از: `LoginRequiredMixin`, `View`
   - Methods:
     - `get_company_id()` - get active company from session
     - `json_response(data, status=200)` - return JsonResponse
     - `error_response(message, status=400)` - return error JsonResponse
     - `validate_company()` - validate active company exists
     - `get_user()` - get current user

2. **`BaseListAPIView`**
   - ارث‌بری از: `BaseAPIView`
   - Methods:
     - `get(request)` - return list of objects as JSON
     - `filter_queryset(queryset)` - apply filters
     - `serialize_object(obj)` - serialize single object

3. **`BaseDetailAPIView`**
   - ارث‌بری از: `BaseAPIView`
   - Methods:
     - `get(request, pk)` - return single object as JSON
     - `serialize_object(obj)` - serialize object

---

### ۱.۲ Base Form Classes

#### `shared/forms/base.py` (بهبود و تکمیل)

**وضعیت**: این فایل **قبلاً وجود دارد** اما باید **بهبود** شود.

**کلاس‌های جدید که باید اضافه شوند**:

1. **`BaseModelForm`**
   - ارث‌بری از: `forms.ModelForm`
   - Method: `__init__()` - apply default widget styling automatically
   - Logic:
     - Checkbox inputs → `form-check-input` class
     - Other inputs → `form-control` class
   - Use: تمام form classes باید از این ارث‌بری کنند

2. **`BaseFormset`** (helper class)
   - Method: `__init__()` - set request on all forms
   - Method: `save_with_company(company_id)` - save all forms with company_id

---

### ۱.۳ Utility Functions

#### `shared/utils/view_helpers.py` (جدید)

**وضعیت**: این فایل **باید ساخته شود**.

**توابع مشترک**:

1. **`get_breadcrumbs(module_name, items)`**
   - Generate breadcrumbs list
   - Parameters:
     - `module_name`: module name (e.g., 'inventory')
     - `items`: list of dicts with 'label' and 'url'
   - Returns: list of breadcrumb dicts

2. **`get_success_message(action, model_name)`**
   - Generate success message
   - Parameters:
     - `action`: 'created', 'updated', 'deleted'
     - `model_name`: model name for message
   - Returns: translated success message

3. **`validate_active_company(request)`**
   - Validate active company exists
   - Parameters:
     - `request`: Django request object
   - Returns: (is_valid, error_message)

4. **`get_table_headers(fields)`**
   - Generate table headers list
   - Parameters:
     - `fields`: list of field names or dicts with 'label' and 'field'
   - Returns: list of header dicts

---

## بخش ۲: فایل‌های Frontend مشترک

### ۲.۱ JavaScript Files

#### `static/js/formset.js` (جدید)

**وضعیت**: این فایل **باید ساخته شود**.

**توابع مشترک**:

1. **`addFormsetRow(prefix, templateSelector)`**
   - Add new row to formset
   - Parameters:
     - `prefix`: formset prefix (e.g., 'formset')
     - `templateSelector`: CSS selector for template row
   - Logic:
     - Clone template row
     - Update form indices
     - Increment TOTAL_FORMS
     - Reindex all rows

2. **`removeFormsetRow(button, prefix)`**
   - Remove row from formset
   - Parameters:
     - `button`: remove button element
     - `prefix`: formset prefix
   - Logic:
     - Remove row
     - Update TOTAL_FORMS
     - Reindex all rows

3. **`updateFormsetTotal(prefix)`**
   - Update TOTAL_FORMS hidden input
   - Parameters:
     - `prefix`: formset prefix

4. **`reindexFormset(prefix)`**
   - Reindex all formset rows
   - Parameters:
     - `prefix`: formset prefix
   - Logic:
     - Update all field names and IDs
     - Update line numbers

5. **`initFormset(prefix, templateSelector, minRows=1, maxRows=null)`**
   - Initialize formset with event handlers
   - Parameters:
     - `prefix`: formset prefix
     - `templateSelector`: CSS selector for template row
     - `minRows`: minimum number of rows
     - `maxRows`: maximum number of rows (null = unlimited)

---

#### `static/js/cascading-dropdowns.js` (جدید)

**وضعیت**: این فایل **باید ساخته شود**.

**توابع مشترک**:

1. **`initCascadingDropdown(parentSelect, childSelect, apiUrl, options)`**
   - Initialize cascading dropdown
   - Parameters:
     - `parentSelect`: parent dropdown element or selector
     - `childSelect`: child dropdown element or selector
     - `apiUrl`: API endpoint URL (e.g., '/api/categories/')
     - `options`: configuration object
       - `parentField`: parent field name for API (e.g., 'item_type_id')
       - `placeholder`: placeholder text for child dropdown
       - `valueField`: field name for option value (default: 'id')
       - `labelField`: field name for option label (default: 'name')
       - `onChange`: callback function when child changes
   - Logic:
     - Listen to parent change event
     - Fetch options from API
     - Populate child dropdown
     - Trigger onChange callback

2. **`updateDropdownOptions(selectElement, options, placeholder)`**
   - Update dropdown options
   - Parameters:
     - `selectElement`: select element
     - `options`: array of {value, label} objects
     - `placeholder`: placeholder option text

3. **`clearDropdown(selectElement, placeholder)`**
   - Clear dropdown options
   - Parameters:
     - `selectElement`: select element
     - `placeholder`: placeholder option text

---

#### `static/js/table-export.js` (جدید)

**وضعیت**: این فایل **باید ساخته شود**.

**توابع مشترک**:

1. **`exportTableToCSV(tableId, filename)`**
   - Export table to CSV file
   - Parameters:
     - `tableId`: table element ID
     - `filename`: output filename (optional)
   - Logic:
     - Extract table data
     - Convert to CSV format
     - Trigger download

2. **`exportTableToExcel(tableId, filename)`**
   - Export table to Excel file (using SheetJS or similar)
   - Parameters:
     - `tableId`: table element ID
     - `filename`: output filename (optional)

3. **`printTable(tableId)`**
   - Print table
   - Parameters:
     - `tableId`: table element ID
   - Logic:
     - Open print dialog with table content

---

#### `static/js/form-helpers.js` (جدید)

**وضعیت**: این فایل **باید ساخته شود**.

**توابع مشترک**:

1. **`initAutoSubmit(selectElement)`**
   - Auto-submit form when select changes
   - Parameters:
     - `selectElement`: select element

2. **`initDatePicker(inputElement, options)`**
   - Initialize date picker (Jalali or Gregorian)
   - Parameters:
     - `inputElement`: input element
     - `options`: date picker options

3. **`validateForm(formElement)`**
   - Validate form before submission
   - Parameters:
     - `formElement`: form element
   - Returns: boolean (is valid)

4. **`showFormErrors(formElement, errors)`**
   - Display form errors
   - Parameters:
     - `formElement`: form element
     - `errors`: dict of field errors

---

### ۲.۲ Template Partials

#### `templates/shared/partials/row_actions.html` (بهبود)

**وضعیت**: این فایل **قبلاً وجود دارد** اما باید **بهبود** شود.

**بهبودها**:
- پشتیبانی از `get_available_actions()` method در model
- نمایش دکمه‌ها بر اساس permissions
- پشتیبانی از custom actions
- Styling یکپارچه

**Context Variables**:
- `object`: model instance
- `view_url_name`: URL name for view action
- `edit_url_name`: URL name for edit action
- `delete_url_name`: URL name for delete action
- `feature_code`: feature code for permission check
- `can_view`, `can_edit`, `can_delete`: boolean flags

---

#### `templates/shared/partials/filter_panel.html` (جدید)

**وضعیت**: این فایل **باید ساخته شود**.

**Purpose**: نمایش پنل فیلتر مشترک

**Blocks**:
- `filter_fields`: برای فیلترهای اختصاصی
- `extra_filters`: برای فیلترهای اضافی

**Context Variables**:
- `show_filters`: boolean
- `status_filter`: boolean
- `search_placeholder`: string
- `clear_filter_url`: URL
- `request.GET`: برای حفظ فیلترهای فعلی

---

#### `templates/shared/partials/stats_cards.html` (جدید)

**وضعیت**: این فایل **باید ساخته شود**.

**Purpose**: نمایش کارت‌های آمار (stats cards)

**Context Variables**:
- `stats`: dict of stat values
  - Example: `{'total': 100, 'draft': 20, 'approved': 80}`
- `stats_labels`: dict of stat labels
  - Example: `{'total': 'Total', 'draft': 'Draft', 'approved': 'Approved'}`

---

#### `templates/shared/partials/pagination.html` (بهبود)

**وضعیت**: این فایل **ممکن است وجود داشته باشد** اما باید **بهبود** شود.

**Purpose**: نمایش pagination مشترک

**Context Variables**:
- `is_paginated`: boolean
- `page_obj`: paginator page object
- `request.GET`: برای حفظ query parameters

---

#### `templates/shared/partials/empty_state.html` (جدید)

**وضعیت**: این فایل **باید ساخته شود**.

**Purpose**: نمایش empty state مشترک

**Context Variables**:
- `empty_state_title`: string
- `empty_state_message`: string
- `empty_state_icon`: string (emoji or icon class)
- `create_url`: URL for create button (optional)

---

### ۲.۳ Template Tags

#### `shared/templatetags/view_tags.py` (جدید)

**وضعیت**: این فایل **باید ساخته شود**.

**Template Tags**:

1. **`{% get_breadcrumbs module items %}`**
   - Generate breadcrumbs
   - Usage: `{% get_breadcrumbs 'inventory' items as breadcrumbs %}`

2. **`{% get_table_headers fields %}`**
   - Generate table headers
   - Usage: `{% get_table_headers fields as headers %}`

3. **`{% can_action object action feature_code %}`**
   - Check if user can perform action
   - Usage: `{% can_action object 'edit' 'inventory.items' as can_edit %}`

4. **`{% get_object_actions object feature_code %}`**
   - Get available actions for object
   - Usage: `{% get_object_actions object 'inventory.items' as actions %}`

---

## بخش ۳: ساختار فایل‌ها

### ۳.۱ ساختار Backend

```
shared/
├── views/
│   ├── base.py          # Base view classes (بهبود)
│   └── api.py           # Base API view classes (جدید)
├── forms/
│   └── base.py          # Base form classes (بهبود)
├── mixins.py            # View mixins (بهبود)
├── filters.py            # Filter functions (جدید)
└── utils/
    └── view_helpers.py   # View helper functions (جدید)
```

### ۳.۲ ساختار Frontend

```
static/
└── js/
    ├── formset.js              # Formset management (جدید)
    ├── cascading-dropdowns.js   # Cascading dropdowns (جدید)
    ├── table-export.js         # Table export (جدید)
    └── form-helpers.js         # Form helpers (جدید)

templates/
└── shared/
    ├── generic/
    │   ├── generic_list.html      # موجود (بهبود)
    │   ├── generic_form.html      # موجود (بهبود)
    │   ├── generic_detail.html    # موجود (بهبود)
    │   └── generic_confirm_delete.html  # موجود (بهبود)
    └── partials/
        ├── row_actions.html       # موجود (بهبود)
        ├── filter_panel.html      # جدید
        ├── stats_cards.html       # جدید
        ├── pagination.html        # جدید یا بهبود
        └── empty_state.html       # جدید

shared/
└── templatetags/
    └── view_tags.py              # Template tags (جدید)
```

---

## بخش ۴: اولویت‌بندی پیاده‌سازی

### فاز ۱: Backend Core (اولویت بالا)

1. ✅ `shared/views/base.py` - BaseListView, BaseCreateView, BaseUpdateView, BaseDeleteView
2. ✅ `shared/filters.py` - Filter functions
3. ✅ `shared/mixins.py` - PermissionFilterMixin, CompanyScopedViewMixin
4. ✅ `shared/forms/base.py` - BaseModelForm

### فاز ۲: Frontend Core (اولویت بالا)

1. ✅ `static/js/formset.js` - Formset management
2. ✅ `templates/shared/partials/row_actions.html` - بهبود
3. ✅ `templates/shared/partials/filter_panel.html` - جدید
4. ✅ `templates/shared/partials/empty_state.html` - جدید

### فاز ۳: Backend Advanced (اولویت متوسط)

1. ✅ `shared/views/base.py` - BaseDetailView, BaseFormsetCreateView, BaseFormsetUpdateView
2. ✅ `shared/views/api.py` - BaseAPIView
3. ✅ `shared/utils/view_helpers.py` - Helper functions

### فاز ۴: Frontend Advanced (اولویت متوسط)

1. ✅ `static/js/cascading-dropdowns.js` - Cascading dropdowns
2. ✅ `static/js/table-export.js` - Table export
3. ✅ `static/js/form-helpers.js` - Form helpers
4. ✅ `templates/shared/partials/stats_cards.html` - جدید
5. ✅ `templates/shared/partials/pagination.html` - بهبود
6. ✅ `shared/templatetags/view_tags.py` - Template tags

### فاز ۵: Document Views (اولویت پایین)

1. ✅ `shared/views/base.py` - BaseDocumentListView, BaseDocumentCreateView, BaseDocumentUpdateView

---

## بخش ۵: مثال استفاده

### مثال ۱: استفاده از BaseListView

```python
# inventory/views/master_data.py
from shared.views.base import BaseListView
from .models import ItemType

class ItemTypeListView(BaseListView):
    model = ItemType
    search_fields = ['name', 'public_code', 'name_en']
    filter_fields = ['is_enabled']
    feature_code = 'inventory.master.item_types'
    default_order_by = ['public_code']
    
    def get_breadcrumbs(self):
        return [
            {'label': _('Inventory'), 'url': None},
            {'label': _('Master Data'), 'url': None},
            {'label': _('Item Types'), 'url': None},
        ]
    
    def get_page_title(self):
        return _('Item Types')
```

### مثال ۲: استفاده از BaseCreateView

```python
# inventory/views/master_data.py
from shared.views.base import BaseCreateView
from .models import ItemType
from .forms import ItemTypeForm

class ItemTypeCreateView(BaseCreateView):
    model = ItemType
    form_class = ItemTypeForm
    success_url = reverse_lazy('inventory:item_types')
    feature_code = 'inventory.master.item_types'
    success_message = _('Item type created successfully.')
    
    def get_breadcrumbs(self):
        return [
            {'label': _('Inventory'), 'url': None},
            {'label': _('Item Types'), 'url': reverse_lazy('inventory:item_types')},
            {'label': _('Create'), 'url': None},
        ]
```

### مثال ۳: استفاده از JavaScript Formset

```html
<!-- templates/inventory/receipt_form.html -->
<script src="{% static 'js/formset.js' %}"></script>
<script>
document.addEventListener('DOMContentLoaded', function() {
    initFormset('formset', '#formset-template-row', minRows=1);
});
</script>
```

### مثال ۴: استفاده از Cascading Dropdowns

```html
<!-- templates/inventory/item_form.html -->
<script src="{% static 'js/cascading-dropdowns.js' %}"></script>
<script>
document.addEventListener('DOMContentLoaded', function() {
    initCascadingDropdown(
        '#id_item_type',
        '#id_item_category',
        '/api/categories/',
        {
            parentField: 'item_type_id',
            placeholder: '--- Select Category ---',
            onChange: function() {
                // Custom logic when category changes
            }
        }
    );
});
</script>
```

---

## بخش ۶: چک‌لیست پیاده‌سازی

### Backend Files

- [ ] `shared/views/base.py` - BaseListView
- [ ] `shared/views/base.py` - BaseCreateView
- [ ] `shared/views/base.py` - BaseUpdateView
- [ ] `shared/views/base.py` - BaseDeleteView
- [ ] `shared/views/base.py` - BaseDetailView
- [ ] `shared/views/base.py` - BaseFormsetCreateView
- [ ] `shared/views/base.py` - BaseFormsetUpdateView
- [ ] `shared/views/base.py` - BaseDocumentListView
- [ ] `shared/views/base.py` - BaseDocumentCreateView
- [ ] `shared/views/base.py` - BaseDocumentUpdateView
- [ ] `shared/filters.py` - تمام توابع فیلتر
- [ ] `shared/mixins.py` - PermissionFilterMixin
- [ ] `shared/mixins.py` - CompanyScopedViewMixin (بهبود)
- [ ] `shared/mixins.py` - AutoSetFieldsMixin
- [ ] `shared/forms/base.py` - BaseModelForm
- [ ] `shared/views/api.py` - BaseAPIView
- [ ] `shared/views/api.py` - BaseListAPIView
- [ ] `shared/views/api.py` - BaseDetailAPIView
- [ ] `shared/utils/view_helpers.py` - تمام helper functions

### Frontend Files

- [ ] `static/js/formset.js` - تمام توابع formset
- [ ] `static/js/cascading-dropdowns.js` - تمام توابع cascading
- [ ] `static/js/table-export.js` - تمام توابع export
- [ ] `static/js/form-helpers.js` - تمام توابع form helpers
- [ ] `templates/shared/partials/row_actions.html` - بهبود
- [ ] `templates/shared/partials/filter_panel.html` - جدید
- [ ] `templates/shared/partials/stats_cards.html` - جدید
- [ ] `templates/shared/partials/pagination.html` - بهبود
- [ ] `templates/shared/partials/empty_state.html` - جدید
- [ ] `shared/templatetags/view_tags.py` - تمام template tags

---

**تاریخ ایجاد**: 2024  
**آخرین به‌روزرسانی**: 2024  
**وضعیت**: آماده برای پیاده‌سازی

