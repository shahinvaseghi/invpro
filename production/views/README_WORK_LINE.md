# production/views/work_line.py - Work Line Views (Complete Documentation)

**هدف**: Views برای مدیریت خطوط کاری در ماژول production

این فایل شامل views برای:
- WorkLineListView: فهرست خطوط کاری
- WorkLineCreateView: ایجاد خط کاری جدید
- WorkLineUpdateView: ویرایش خط کاری
- WorkLineDetailView: نمایش جزئیات خط کاری
- WorkLineDeleteView: حذف خط کاری

---

## وابستگی‌ها

- `shared.mixins`: `FeaturePermissionRequiredMixin`
- `production.forms`: `WorkLineForm`
- `production.models`: `WorkLine`
- `django.views.generic`: `CreateView`, `DeleteView`, `ListView`, `UpdateView`
- `django.contrib.messages`
- `django.http.HttpResponseRedirect`
- `django.urls.reverse_lazy`
- `django.utils.translation.gettext_lazy`

---

## WorkLineListView

**Type**: `BaseListView` (از `shared.views.base`)

**Template**: `production/work_lines.html`

**Attributes**:
- `model`: `WorkLine`
- `template_name`: `'production/work_lines.html'`
- `context_object_name`: `'work_lines'`
- `paginate_by`: `50`
- `feature_code`: `'production.work_lines'`
- `required_action`: `'view_own'`

**متدها**:

#### `get_queryset(self) -> QuerySet`

**توضیح**: queryset را با company filtering، optional select_related، و prefetch_related برمی‌گرداند.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `QuerySet`: queryset فیلتر شده با optimizations

**منطق**:
1. دریافت `active_company_id` از session
2. اگر `active_company_id` وجود ندارد، `WorkLine.objects.none()` برمی‌گرداند
3. فیلتر: `WorkLine.objects.filter(company_id=active_company_id)`
4. **Optional select_related**:
   - تلاش برای `select_related('warehouse')` (با try-except برای جلوگیری از خطا در صورت عدم نصب inventory module)
   - اگر خطا رخ دهد، skip می‌کند
5. **prefetch_related**: `'personnel'`, `'machines'` (ManyToMany relationships)
6. مرتب‌سازی: `order_by('warehouse__name', 'sort_order', 'public_code')`
7. queryset را برمی‌گرداند

**نکات مهم**:
- `select_related('warehouse')` با try-except برای جلوگیری از خطا در صورت عدم نصب inventory module

---

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`

**توضیح**: context variables را برای template اضافه می‌کند.

**پارامترهای ورودی**:
- `**kwargs`: متغیرهای context اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با `active_module`

**Context Variables اضافه شده**:
- `active_module`: `'production'`

**URL**: `/production/work-lines/`

---

## WorkLineCreateView

**Type**: `BaseCreateView` (از `shared.views.base`)

**Template**: `production/work_line_form.html`

**Form**: `WorkLineForm`

**Success URL**: `production:work_lines`

**Attributes**:
- `model`: `WorkLine`
- `form_class`: `WorkLineForm`
- `template_name`: `'production/work_line_form.html'`
- `success_url`: `reverse_lazy('production:work_lines')`
- `feature_code`: `'production.work_lines'`
- `required_action`: `'create'`

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

#### `form_valid(self, form: WorkLineForm) -> HttpResponseRedirect`
- **Parameters**: `form`: فرم معتبر `WorkLineForm`
- **Returns**: redirect به `success_url`
- **Logic**:
  1. فراخوانی `super().form_valid(form)` (ذخیره instance)
  2. **ذخیره M2M relationships**: `form.save_m2m()` (برای `personnel` و `machines`)
  3. بازگشت response

**نکات مهم**:
- `save_m2m()` برای ذخیره ManyToMany relationships (`personnel` و `machines`) فراخوانی می‌شود

---

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`
- **Returns**: context با form_id
- **Logic**:
  1. دریافت context از `super().get_context_data()`
  2. اضافه کردن `form_id = 'work-line-form'`
  3. بازگشت context

**URL**: `/production/work-lines/create/`

---

## WorkLineUpdateView

**Type**: `BaseUpdateView` (از `shared.views.base`)

**Template**: `production/work_line_form.html`

**Form**: `WorkLineForm`

**Success URL**: `production:work_lines`

**Attributes**:
- `model`: `WorkLine`
- `form_class`: `WorkLineForm`
- `template_name`: `'production/work_line_form.html'`
- `success_url`: `reverse_lazy('production:work_lines')`
- `feature_code`: `'production.work_lines'`
- `required_action`: `'edit_own'`

**متدها**:

#### `get_form_kwargs(self) -> Dict[str, Any]`

**توضیح**: `company_id` را به form پاس می‌دهد.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `Dict[str, Any]`: kwargs با `company_id` از `object.company_id`

**منطق**:
1. kwargs را از `super().get_form_kwargs()` دریافت می‌کند
2. `company_id` را از `self.object.company_id` اضافه می‌کند
3. kwargs را برمی‌گرداند

---

#### `get_queryset(self) -> QuerySet`

**توضیح**: queryset را با company filtering برمی‌گرداند.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `QuerySet`: queryset فیلتر شده بر اساس company

**منطق**:
1. دریافت `active_company_id` از session
2. اگر `active_company_id` وجود ندارد، `WorkLine.objects.none()` برمی‌گرداند
3. فیلتر: `WorkLine.objects.filter(company_id=active_company_id)`
4. queryset را برمی‌گرداند

---

#### `form_valid(self, form: WorkLineForm) -> HttpResponseRedirect`
- **Parameters**: `form`: فرم معتبر `WorkLineForm`
- **Returns**: redirect به `success_url`
- **Logic**:
  1. فراخوانی `super().form_valid(form)` (ذخیره instance)
  2. **ذخیره M2M relationships**: `form.save_m2m()` (برای `personnel` و `machines`)
  3. بازگشت response

**نکات مهم**:
- `save_m2m()` برای ذخیره ManyToMany relationships (`personnel` و `machines`) فراخوانی می‌شود

---

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`
- **Returns**: context با form_id
- **Logic**:
  1. دریافت context از `super().get_context_data()`
  2. اضافه کردن `form_id = 'work-line-form'`
  3. بازگشت context

**URL**: `/production/work-lines/<pk>/edit/`

---

## WorkLineDetailView

### `WorkLineDetailView`

**توضیح**: نمایش جزئیات Work Line (read-only)

**Type**: `BaseDetailView` (از `shared.views.base`)

**Template**: `shared/generic/generic_detail.html`

**Attributes**:
- `model`: `WorkLine`
- `template_name`: `'shared/generic/generic_detail.html'`
- `context_object_name`: `'object'`
- `feature_code`: `'production.work_lines'`
- `required_action`: `'view_own'`
- `active_module`: `'production'`

**Context Variables**:
- `object`: WorkLine instance
- `detail_title`: `_('View Work Line')`
- `info_banner`: لیست اطلاعات اصلی (code, status)
- `detail_sections`: لیست sections برای نمایش:
  - Basic Information: name, name_en (اگر موجود باشد), warehouse (اگر موجود باشد), description (اگر موجود باشد)
  - Assigned Personnel: اگر personnel موجود باشد (comma-separated list)
  - Assigned Machines: اگر machines موجود باشد (comma-separated list)
  - Notes: اگر notes موجود باشد
- `list_url`, `edit_url`: URLs برای navigation
- `can_edit_object`: بررسی اینکه آیا Work Line قفل است یا نه

**متدها**:

#### `get_queryset(self) -> QuerySet`
- **Returns**: queryset بهینه شده با select_related و prefetch_related
- **Logic**:
  1. دریافت queryset از `super().get_queryset()`
  2. **Optional select_related**:
     - تلاش برای `select_related('warehouse', 'created_by', 'edited_by')`
     - اگر خطا رخ دهد (مثلاً warehouse field موجود نباشد): `select_related('created_by', 'edited_by')`
  3. اعمال `prefetch_related('personnel', 'machines')`
  4. بازگشت queryset

#### `get_context_data(self, **kwargs) -> Dict[str, Any]`
- **Returns**: context با detail sections
- **Logic**:
  1. دریافت context از `super().get_context_data()`
  2. ساخت `info_banner`:
     - Code (type: 'code')
     - Status (type: 'badge')
  3. ساخت `detail_sections`:
     - **Basic Information**: name, name_en (اگر موجود باشد), warehouse (اگر موجود باشد), description (اگر موجود باشد)
     - **Assigned Personnel**: اگر `personnel.exists()` باشد:
       - ساخت comma-separated text از `first_name last_name` برای هر person
       - اضافه کردن section
     - **Assigned Machines**: اگر `machines.exists()` باشد:
       - ساخت comma-separated text از `machine.name` برای هر machine
       - اضافه کردن section
     - **Notes**: اگر notes موجود باشد
  4. بازگشت context

#### `get_list_url(self) -> str`
- **Returns**: URL برای لیست Work Lines

#### `get_edit_url(self) -> str`
- **Returns**: URL برای ویرایش Work Line

#### `can_edit_object(self, obj=None, feature_code=None) -> bool`
- **Returns**: True اگر Work Line قفل نباشد
- **Logic**:
  - بررسی `is_locked` attribute
  - اگر `is_locked=True` باشد، return False

**URL**: `/production/work-lines/<pk>/`

---

## WorkLineDeleteView

**Type**: `BaseDeleteView` (از `shared.views.base`)

**Template**: `shared/generic/generic_confirm_delete.html`

**Success URL**: `production:work_lines`

**Attributes**:
- `model`: `WorkLine`
- `template_name`: `'shared/generic/generic_confirm_delete.html'`
- `success_url`: `reverse_lazy('production:work_lines')`
- `feature_code`: `'production.work_lines'`
- `required_action`: `'delete_own'`

**متدها**:

#### `get_queryset(self) -> QuerySet`
- **Returns**: queryset بهینه شده با optional select_related
- **Logic**:
  1. دریافت queryset از `super().get_queryset()`
  2. **Optional select_related**:
     - تلاش برای `select_related('warehouse')`
     - اگر خطا رخ دهد، skip می‌کند
  3. بازگشت queryset

#### `delete(self, request: Any, *args: Any, **kwargs: Any) -> HttpResponseRedirect`
- **Parameters**: `request`, `*args`, `**kwargs`
- **Returns**: redirect به `success_url`
- **Logic**:
  - فراخوانی `super().delete()` که WorkLine را حذف می‌کند و پیام موفقیت نمایش می‌دهد

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`
- **Returns**: context با delete title، confirmation message، object details، و breadcrumbs
- **Logic**:
  - از base class استفاده می‌کند که تمام context variables لازم را اضافه می‌کند

**URL**: `/production/work-lines/<pk>/delete/`

---

## Generic Templates

تمام templates به generic templates منتقل شده‌اند:

### Work Line List
- **Template**: `production/work_lines.html` extends `shared/generic/generic_list.html`
- **Blocks Overridden**: 
  - `table_headers`: Code, Name, Warehouse, Personnel, Machines, Status
  - `table_rows`: نمایش work lines با Code, Name, Warehouse, Personnel (limited to 3), Machines (limited to 3), Status, Actions
  - `empty_state_title`, `empty_state_message`, `empty_state_icon`: override برای empty state
- **Context Variables**:
  - `page_title`: "Work Lines"
  - `breadcrumbs`: Production > Work Lines
  - `create_url`: URL برای ایجاد Work Line جدید
  - `table_headers`: [] (overridden in template)
  - `show_actions`: True
  - `edit_url_name`: 'production:work_line_edit'
  - `delete_url_name`: 'production:work_line_delete'
  - `empty_state_title`: "No Work Lines Found"
  - `empty_state_message`: "Start by creating your first work line."
  - `empty_state_icon`: "🏭"

### Work Line Form
- **Template**: `production/work_line_form.html` extends `shared/generic/generic_form.html`
- **Blocks Overridden**: 
  - `breadcrumb_extra`: مسیر breadcrumb
  - `before_form`: Info banner برای نمایش code
  - `form_sections`: فیلدهای form (warehouse, name, description, notes, sort_order, is_enabled, personnel, machines)

### Work Line Delete
- **Template**: `shared/generic/generic_confirm_delete.html`
- **Context Variables**:
  - `delete_title`: عنوان حذف
  - `confirmation_message`: پیام تایید
  - `object_details`: جزئیات خط کاری (code, name, warehouse)
  - `cancel_url`: URL برای لغو
  - `breadcrumbs`: مسیر breadcrumb

---

## الگوهای مشترک

1. **Company Filtering**: تمام queryset ها بر اساس `active_company_id` فیلتر می‌شوند
2. **Permission Checking**: تمام views از `FeaturePermissionRequiredMixin` استفاده می‌کنند
3. **ManyToMany Handling**: `personnel` و `machines` با `save_m2m()` ذخیره می‌شوند
4. **Optional select_related**: `select_related('warehouse')` با try-except برای جلوگیری از خطا (اگر inventory module نصب نباشد)

