# production/views/bom.py - BOM Views (Complete Documentation)

**هدف**: Views برای مدیریت BOM (Bill of Materials) در ماژول production

این فایل شامل views برای:
- BOMListView: فهرست BOM ها
- BOMCreateView: ایجاد BOM جدید
- BOMUpdateView: ویرایش BOM
- BOMDeleteView: حذف BOM

---

## وابستگی‌ها

- `shared.mixins`: `FeaturePermissionRequiredMixin`
- `production.forms`: `BOMForm`, `BOMMaterialLineFormSet`
- `production.models`: `BOM`, `BOMMaterial`
- `django.views.generic`: `CreateView`, `DeleteView`, `ListView`, `UpdateView`
- `django.contrib.messages`
- `django.http.HttpResponseRedirect`
- `django.shortcuts.redirect`
- `django.urls.reverse_lazy`
- `django.utils.translation.gettext_lazy`

---

## BOMListView

### `BOMListView`

**توضیح**: فهرست تمام BOM های شرکت فعال

**Type**: `FeaturePermissionRequiredMixin, ListView`

**Template**: `production/bom_list.html` (extends `shared/generic/generic_list.html`)

**Attributes**:
- `model`: `BOM`
- `template_name`: `'production/bom_list.html'`
- `context_object_name`: `'object_list'`
- `paginate_by`: `50`
- `feature_code`: `'production.bom'`

**Context Variables**:
- `object_list`: queryset BOM ها (paginated)
- `page_title`: `_('BOM (Bill of Materials)')`
- `breadcrumbs`: لیست breadcrumbs
- `create_url`, `create_button_text`: برای دکمه ایجاد
- `show_filters`: `True` برای نمایش فیلترها
- `finished_items`: لیست محصولات نهایی برای فیلتر dropdown
- `show_actions`, `edit_url_name`, `delete_url_name`: برای دکمه‌های action
- `empty_state_*`: پیام‌های empty state
- `print_enabled`: `True` برای فعال‌سازی print

**متدها**:

#### `get_queryset(self) -> QuerySet`

**توضیح**: queryset را با company filtering و optional finished_item filtering برمی‌گرداند.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `QuerySet`: queryset فیلتر شده

**منطق**:
1. `active_company_id` را از session دریافت می‌کند
2. اگر `active_company_id` وجود ندارد، `BOM.objects.none()` برمی‌گرداند
3. queryset را فیلتر می‌کند (بر اساس company و `is_enabled=1`)
4. `select_related('finished_item', 'company')` و `prefetch_related('materials')` را اعمال می‌کند
5. مرتب می‌کند بر اساس `finished_item__item_code`, `-version`
6. اگر `finished_item` در query parameter وجود دارد، فیلتر می‌کند
7. queryset را برمی‌گرداند

**Query Parameters**:
- `finished_item`: فیلتر بر اساس محصول نهایی

---

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`

**توضیح**: context variables را برای template اضافه می‌کند.

**پارامترهای ورودی**:
- `**kwargs`: متغیرهای context اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با تمام متغیرهای لازم

**Context Variables اضافه شده**:
- `active_module`: `'production'`
- `finished_items`: لیست dictionaries با `id`, `code`, `name` برای فیلتر dropdown

**URL**: `/production/bom/`

---

## BOMCreateView

### `BOMCreateView`

**توضیح**: ایجاد BOM جدید با مواد اولیه (multi-line)

**Type**: `BaseNestedFormsetCreateView` (از `shared.views.base`)

**Template**: `production/bom_form.html`

**Form**: `BOMForm`

**Formset**: `BOMMaterialLineFormSet`

**Success URL**: `production:bom_list`

**Attributes**:
- `model`: `BOM`
- `form_class`: `BOMForm`
- `template_name`: `'production/bom_form.html'`
- `success_url`: `reverse_lazy('production:bom_list')`
- `feature_code`: `'production.bom'`
- `required_action`: `'create'`

**Context Variables**:
- `form`: instance فرم `BOMForm`
- `formset`: instance formset `BOMMaterialLineFormSet`
- `active_module`: `'production'`
- `form_title`: `_('Create BOM')`

**متدها**:

#### `get_form_kwargs(self) -> Dict[str, Any]`

**توضیح**: `company_id` را به form پاس می‌دهد.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `Dict[str, Any]`: kwargs با `company_id` اضافه شده

**منطق**:
1. kwargs را از `super().get_form_kwargs()` دریافت می‌کند
2. `company_id` را از `request.session.get('active_company_id')` اضافه می‌کند
3. kwargs را برمی‌گرداند

---

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`

**توضیح**: formset را به context اضافه می‌کند.

**پارامترهای ورودی**:
- `**kwargs`: متغیرهای context اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با `formset` اضافه شده

**منطق**:
1. context را از `super().get_context_data()` دریافت می‌کند
2. `active_module` و `form_title` را اضافه می‌کند
3. اگر `request.POST` وجود دارد:
   - formset را از POST data می‌سازد (بدون instance)
   - اگر form خطا دارد، خطاها را نمایش می‌دهد
4. اگر `request.POST` وجود ندارد:
   - formset خالی می‌سازد
5. context را برمی‌گرداند

---

#### `get_formset_kwargs(self) -> Dict[str, Any]`
- **Returns**: kwargs برای formset
- **Logic**:
  - اضافه کردن `form_kwargs` با `company_id` از session

#### `get_nested_formset_kwargs(self, parent_instance) -> Dict[str, Any]`
- **Parameters**: `parent_instance`: BOMMaterial instance
- **Returns**: kwargs برای nested formset
- **Logic**:
  - اضافه کردن `form_kwargs` با `company_id` و `bom_material_id`

#### `process_formset_instance(self, instance) -> Optional[BOMMaterial]`
- **Parameters**: `instance`: BOMMaterial instance
- **Returns**: instance پردازش شده یا None (اگر validation fail شود)
- **Logic**:
  1. **Validation**: بررسی `material_item` و `unit` (اگر وجود ندارد، return None)
  2. Initialize `_line_number` counter (از 1 شروع می‌شود)
  3. تنظیم `instance.bom = self.object`
  4. تنظیم `instance.line_number = self._line_number` (sequential)
  5. تنظیم `instance.company_id = active_company_id`
  6. تنظیم `instance.created_by = request.user`
  7. **Auto-fill `material_item_code`**: `instance.material_item_code = instance.material_item.item_code`
  8. **Auto-set `material_type`**:
     - اگر `material_type` تنظیم نشده باشد
     - از `instance.material_item.type` استفاده می‌کند
     - اگر type وجود ندارد: error message و return None
  9. افزایش `self._line_number` برای instance بعدی
  10. بازگشت instance

#### `form_valid(self, form: BOMForm) -> HttpResponseRedirect`
- **Parameters**: `form`: فرم معتبر `BOMForm`
- **Returns**: redirect به `success_url`
- **Logic**:
  1. دریافت `active_company_id` از session
  2. اگر `active_company_id` وجود ندارد:
     - error message: "Please select a company first."
     - return `self.form_invalid(form)`
  3. تنظیم `form.instance.company_id = active_company_id`
  4. تنظیم `form.instance.created_by = request.user`
  5. تنظیم `form.instance.is_enabled = 1` (اگر تنظیم نشده باشد)
  6. Initialize `self._line_number = 1` (برای `process_formset_instance`)
  7. **فراخوانی `super().form_valid(form)`**:
     - base class (`BaseNestedFormsetCreateView`) منطق formset و nested formsets را مدیریت می‌کند
     - از `process_formset_instance` برای هر instance استفاده می‌کند
  8. **Count saved instances**: `saved_count = self.object.materials.count()`
  9. **پیام‌ها**:
     - اگر `saved_count == 0`: warning: "BOM created but no material lines were saved. Please check the form data."
     - در غیر این صورت: success: "BOM created successfully with {count} material line(s)."
  10. بازگشت response

**نکات مهم**:
- از `BaseNestedFormsetCreateView` استفاده می‌کند که منطق formset را خودکار مدیریت می‌کند
- `process_formset_instance` برای هر material line فراخوانی می‌شود
- `line_number` به صورت sequential تنظیم می‌شود
- `material_item_code` و `material_type` به صورت خودکار populate می‌شوند

**URL**: `/production/bom/create/`

---

## BOMUpdateView

### `BOMUpdateView`

**توضیح**: ویرایش BOM موجود

**Type**: `BaseNestedFormsetUpdateView, EditLockProtectedMixin` (از `shared.views.base`)

**Template**: `production/bom_form.html`

**Form**: `BOMForm`

**Formset**: `BOMMaterialLineFormSet`

**Success URL**: `production:bom_list`

**Attributes**:
- `model`: `BOM`
- `form_class`: `BOMForm`
- `template_name`: `'production/bom_form.html'`
- `success_url`: `reverse_lazy('production:bom_list')`
- `feature_code`: `'production.bom'`
- `required_action`: `'edit_own'`

**Context Variables**:
- مشابه `BOMCreateView` اما با `form_title = _('Edit BOM')` و `object`

**متدها**:

#### `get_form_kwargs(self) -> Dict[str, Any]`

**توضیح**: `company_id` را به form پاس می‌دهد.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `Dict[str, Any]`: kwargs با `company_id` از `object.company_id`

**منطق**:
- `company_id` را از `self.object.company_id` اضافه می‌کند

---

#### `get_queryset(self) -> QuerySet`

**توضیح**: queryset را با company filtering برمی‌گرداند.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `QuerySet`: queryset فیلتر شده بر اساس company

**منطق**:
- queryset را بر اساس `active_company_id` فیلتر می‌کند

---

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`

**توضیح**: formset را به context اضافه می‌کند.

**پارامترهای ورودی**:
- `**kwargs`: متغیرهای context اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با `formset` اضافه شده

**منطق**:
- مشابه `BOMCreateView.get_context_data()` اما با instance موجود

---

#### `get_formset_kwargs(self) -> Dict[str, Any]`
- **Returns**: kwargs برای formset
- **Logic**:
  - اضافه کردن `form_kwargs` با `company_id` از `self.object.company_id`

#### `get_nested_formset_kwargs(self, parent_instance) -> Dict[str, Any]`
- **Parameters**: `parent_instance`: BOMMaterial instance
- **Returns**: kwargs برای nested formset
- **Logic**:
  - اضافه کردن `form_kwargs` با `company_id` و `bom_material_id`

#### `process_formset_instance(self, instance) -> Optional[BOMMaterial]`
- **Parameters**: `instance`: BOMMaterial instance
- **Returns**: instance پردازش شده یا None (اگر validation fail شود)
- **Logic**:
  1. **Validation**: بررسی `material_item` و `unit` (اگر وجود ندارد، return None)
  2. Initialize `_line_number` counter:
     - اگر قبلاً initialize نشده باشد
     - دریافت max `line_number` از existing materials
     - `self._line_number = existing_max + 1`
  3. تنظیم `instance.bom = self.object`
  4. تنظیم `instance.line_number = self._line_number` (sequential)
  5. تنظیم `instance.edited_by = request.user`
  6. **Auto-fill `material_item_code`**: `instance.material_item_code = instance.material_item.item_code`
  7. **Auto-set `material_type`**:
     - اگر `material_type` تنظیم نشده باشد
     - از `instance.material_item.type` استفاده می‌کند
     - اگر type وجود ندارد: error message و return None
  8. افزایش `self._line_number` برای instance بعدی
  9. بازگشت instance

#### `form_valid(self, form: BOMForm) -> HttpResponseRedirect`
- **Parameters**: `form`: فرم معتبر `BOMForm`
- **Returns**: redirect به `success_url`
- **Logic**:
  1. تنظیم `form.instance.edited_by = request.user`
  2. Initialize `self._line_number = 1` (برای `process_formset_instance`)
  3. **فراخوانی `super().form_valid(form)`**:
     - base class (`BaseNestedFormsetUpdateView`) منطق formset و nested formsets را مدیریت می‌کند
     - از `process_formset_instance` برای هر instance استفاده می‌کند
  4. **Count saved instances**: `saved_count = self.object.materials.count()`
  5. **پیام‌ها**:
     - اگر `saved_count == 0`: warning: "BOM updated but no material lines were saved. Please check the form data."
     - در غیر این صورت: success: "BOM updated successfully with {count} material line(s)."
  6. بازگشت response

**نکات مهم**:
- از `BaseNestedFormsetUpdateView` استفاده می‌کند که منطق formset را خودکار مدیریت می‌کند
- `process_formset_instance` برای هر material line فراخوانی می‌شود
- `line_number` برای instances جدید از max existing + 1 شروع می‌شود
- `material_item_code` و `material_type` به صورت خودکار populate می‌شوند

**URL**: `/production/bom/<pk>/edit/`

---

## BOMDetailView

### `BOMDetailView`

**توضیح**: نمایش جزئیات BOM (read-only)

**Type**: `BaseDetailView` (از `shared.views.base`)

**Template**: `shared/generic/generic_detail.html`

**Attributes**:
- `model`: `BOM`
- `template_name`: `'shared/generic/generic_detail.html'`
- `context_object_name`: `'object'`
- `feature_code`: `'production.bom'`
- `required_action`: `'view_own'`
- `active_module`: `'production'`

**Context Variables**:
- `object`: BOM instance
- `detail_title`: `_('View BOM')`
- `info_banner`: لیست اطلاعات اصلی (bom_code, version, status)
- `detail_sections`: لیست sections برای نمایش:
  - Basic Information: finished_item, description
  - Material Lines: جدول materials با headers و data
  - Notes: اگر notes موجود باشد
- `list_url`, `edit_url`: URLs برای navigation
- `can_edit_object`: بررسی اینکه آیا BOM قفل است یا نه

**متدها**:

#### `get_queryset(self) -> QuerySet`
- **Returns**: queryset بهینه شده با select_related و prefetch_related
- **Logic**:
  1. دریافت queryset از `super().get_queryset()`
  2. اعمال `select_related('finished_item', 'created_by', 'edited_by')`
  3. اعمال `prefetch_related('materials__material_item', 'materials__material_type')`
  4. بازگشت queryset

#### `get_context_data(self, **kwargs) -> Dict[str, Any]`
- **Returns**: context با detail sections
- **Logic**:
  1. دریافت context از `super().get_context_data()`
  2. ساخت `info_banner`:
     - BOM Code (type: 'code')
     - Version
     - Status (type: 'badge')
  3. ساخت `detail_sections`:
     - **Basic Information**: finished_item (name + code), description (اگر موجود باشد)
     - **Material Lines** (table):
       - بررسی `has_description` برای اضافه کردن column
       - Headers: Line, Material Item, Material Type, Quantity per Unit, Unit, Scrap Allowance, Optional, Description (optional)
       - Data: برای هر material، row با تمام اطلاعات
     - **Notes**: اگر notes موجود باشد
  4. بازگشت context

#### `get_list_url(self) -> str`
- **Returns**: URL برای لیست BOM ها

#### `get_edit_url(self) -> str`
- **Returns**: URL برای ویرایش BOM

#### `can_edit_object(self, obj=None, feature_code=None) -> bool`
- **Returns**: True اگر BOM قفل نباشد
- **Logic**:
  - بررسی `is_locked` attribute
  - اگر `is_locked=True` باشد، return False

**URL**: `/production/bom/<pk>/`

---

## BOMDeleteView

### `BOMDeleteView`

**توضیح**: حذف BOM

**Type**: `FeaturePermissionRequiredMixin, DeleteView`

**Template**: `shared/generic/generic_confirm_delete.html`

**Success URL**: `production:bom_list`

**Attributes**:
- `model`: `BOM`
- `template_name`: `'shared/generic/generic_confirm_delete.html'`
- `success_url`: `reverse_lazy('production:bom_list')`
- `feature_code`: `'production.bom'`
- `required_action`: `'delete_own'`

**Context Variables**:
- `delete_title`: `_('Delete BOM')`
- `confirmation_message`: پیام تأیید حذف
- `object_details`: جزئیات BOM برای نمایش
- `warning_message`: هشدار در مورد material lines (اگر وجود داشته باشند)
- `cancel_url`: URL برای cancel
- `breadcrumbs`: لیست breadcrumbs

**متدها**:

#### `get_queryset(self) -> QuerySet`
- **Returns**: queryset فیلتر شده بر اساس company
- **Logic**:
  1. دریافت `active_company_id` از session
  2. اگر `active_company_id` وجود ندارد، `BOM.objects.none()` برمی‌گرداند
  3. فیلتر: `BOM.objects.filter(company_id=active_company_id)`
  4. بازگشت queryset

---

#### `delete(self, request: Any, *args: Any, **kwargs: Any) -> HttpResponseRedirect`
- **Parameters**: `request`, `*args`, `**kwargs`
- **Returns**: redirect به `success_url`
- **Logic**:
  - فراخوانی `super().delete()` که BOM را حذف می‌کند و پیام موفقیت نمایش می‌دهد

---

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`

**توضیح**: context variables را برای generic delete template اضافه می‌کند.

**پارامترهای ورودی**:
- `**kwargs`: متغیرهای context اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با تمام متغیرهای لازم برای generic template

**Context Variables اضافه شده**:
- `delete_title`: `_('Delete BOM')`
- `confirmation_message`: پیام تأیید حذف
- `object_details`: لیست جزئیات BOM (bom_code, finished_product, version)
- `warning_message`: هشدار در مورد material lines (اگر وجود داشته باشند)
- `cancel_url`: URL برای cancel
- `breadcrumbs`: لیست breadcrumbs

**URL**: `/production/bom/<pk>/delete/`

---

## استفاده در پروژه

### URL Patterns
```python
path('bom/', BOMListView.as_view(), name='bom_list'),
path('bom/create/', BOMCreateView.as_view(), name='bom_create'),
path('bom/<int:pk>/', BOMDetailView.as_view(), name='bom_detail'),
path('bom/<int:pk>/edit/', BOMUpdateView.as_view(), name='bom_edit'),
path('bom/<int:pk>/delete/', BOMDeleteView.as_view(), name='bom_delete'),
```

---

## نکات مهم

### 1. Formset Handling
- از `BaseNestedFormsetCreateView` و `BaseNestedFormsetUpdateView` استفاده می‌کند
- منطق formset و nested formsets به صورت خودکار مدیریت می‌شود
- `process_formset_instance` برای هر material line فراخوانی می‌شود
- در `BOMUpdateView`، خطوط marked for deletion حذف می‌شوند

### 2. Line Number Management
- `line_number` به صورت sequential (1, 2, 3, ...) تنظیم می‌شود
- برای هر خط معتبر (با `material_item`) تنظیم می‌شود

### 3. Auto-population
- `material_item_code` از `material_item.item_code` auto-fill می‌شود
- `material_type` از `material_item.type` auto-set می‌شود (اگر تنظیم نشده باشد)

### 4. Error Handling
- خطاهای formset به صورت prominent نمایش داده می‌شوند
- خطاهای هر خط به صورت جداگانه نمایش داده می‌شوند (با شماره خط)

### 5. Company Filtering
- تمام queryset ها بر اساس `active_company_id` فیلتر می‌شوند

### 6. Generic Templates
- **BOM List**: از `shared/generic/generic_list.html` extends می‌کند (با expandable rows برای نمایش materials)
- **BOM Delete**: از `shared/generic/generic_confirm_delete.html` استفاده می‌کند
- **BOM Form**: هنوز از template اختصاصی استفاده می‌کند (به دلیل پیچیدگی formset و JavaScript)

---

## الگوهای مشترک

1. **Company Filtering**: تمام queryset ها بر اساس `active_company_id` فیلتر می‌شوند
2. **Permission Checking**: تمام views از `FeaturePermissionRequiredMixin` استفاده می‌کنند
3. **Formset Management**: Create و Update views از formset برای مدیریت خطوط استفاده می‌کنند
4. **Error Display**: خطاها به صورت user-friendly نمایش داده می‌شوند

