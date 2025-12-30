# production/views/machine.py - Machine Views (Complete Documentation)

**هدف**: Views برای مدیریت ماشین‌آلات در ماژول production

این فایل شامل views برای:
- MachineListView: فهرست ماشین‌آلات
- MachineCreateView: ایجاد ماشین جدید
- MachineUpdateView: ویرایش ماشین
- MachineDetailView: نمایش جزئیات ماشین
- MachineDeleteView: حذف ماشین

---

## وابستگی‌ها

- `shared.mixins`: `FeaturePermissionRequiredMixin`
- `production.forms`: `MachineForm`
- `production.models`: `Machine`
- `django.views.generic`: `CreateView`, `DeleteView`, `ListView`, `UpdateView`
- `django.contrib.messages`
- `django.http.HttpResponseRedirect`
- `django.urls.reverse_lazy`
- `django.utils.translation.gettext_lazy`

---

## MachineListView

**Type**: `BaseListView` (از `shared.views.base`)

**Template**: `production/machines.html` (extends `shared/generic/generic_list.html`)

**Attributes**:
- `model`: `Machine`
- `template_name`: `'production/machines.html'`
- `context_object_name`: `'object_list'`
- `paginate_by`: `50`
- `feature_code`: `'production.machines'`

**متدها**:

#### `get_queryset(self) -> QuerySet`

**توضیح**: queryset را با company filtering، is_enabled filtering، و optional select_related برمی‌گرداند.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `QuerySet`: queryset فیلتر شده با optimizations

**منطق**:
1. دریافت `active_company_id` از session
2. اگر `active_company_id` وجود ندارد، `Machine.objects.none()` برمی‌گرداند
3. فیلتر: `Machine.objects.filter(company_id=active_company_id, is_enabled=1)`
4. **Optional select_related**:
   - تلاش برای `select_related('work_center')` (با try-except برای جلوگیری از خطا در صورت عدم وجود field)
   - اگر خطا رخ دهد، skip می‌کند
5. مرتب‌سازی: `order_by('public_code')`
6. queryset را برمی‌گرداند

**نکات مهم**:
- `select_related('work_center')` با try-except برای جلوگیری از خطا در صورت عدم وجود field

---

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`
- **Returns**: context با work_centers برای filter
- **Logic**:
  1. دریافت context از `super().get_context_data()`
  2. اضافه کردن `print_enabled = True`
  3. **اضافه کردن work_centers** (برای filter dropdown):
     - دریافت `active_company_id` از session
     - اگر موجود باشد:
       - فیلتر `WorkCenter.objects.filter(company_id=active_company_id).order_by('name')`
       - اضافه کردن به context
  4. بازگشت context

**URL**: `/production/machines/`

---

## MachineCreateView

**Type**: `BaseCreateView` (از `shared.views.base`)

**Template**: `production/machine_form.html` (extends `shared/generic/generic_form.html`)

**Form**: `MachineForm`

**Success URL**: `production:machines`

**Attributes**:
- `model`: `Machine`
- `form_class`: `MachineForm`
- `template_name`: `'production/machine_form.html'`
- `success_url`: `reverse_lazy('production:machines')`
- `feature_code`: `'production.machines'`
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

#### `form_valid(self, form: MachineForm) -> HttpResponseRedirect`
- **Parameters**: `form`: فرم معتبر `MachineForm`
- **Returns**: redirect به `success_url`
- **Logic**:
  - از base class استفاده می‌کند که منطق ذخیره و پیام موفقیت را مدیریت می‌کند

---

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`
- **Returns**: context با form_title و breadcrumbs
- **Logic**:
  - از base class استفاده می‌کند که تمام context variables لازم را اضافه می‌کند

**URL**: `/production/machines/create/`

---

## MachineUpdateView

**Type**: `BaseUpdateView` (از `shared.views.base`)

**Template**: `production/machine_form.html` (extends `shared/generic/generic_form.html`)

**Form**: `MachineForm`

**Success URL**: `production:machines`

**Attributes**:
- `model`: `Machine`
- `form_class`: `MachineForm`
- `template_name`: `'production/machine_form.html'`
- `success_url`: `reverse_lazy('production:machines')`
- `feature_code`: `'production.machines'`
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
2. اگر `active_company_id` وجود ندارد، `Machine.objects.none()` برمی‌گرداند
3. فیلتر: `Machine.objects.filter(company_id=active_company_id)`
4. queryset را برمی‌گرداند

---

#### `form_valid(self, form: MachineForm) -> HttpResponseRedirect`
- **Parameters**: `form`: فرم معتبر `MachineForm`
- **Returns**: redirect به `success_url`
- **Logic**:
  - از base class استفاده می‌کند که منطق ذخیره و پیام موفقیت را مدیریت می‌کند

---

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`
- **Returns**: context با form_title و breadcrumbs
- **Logic**:
  - از base class استفاده می‌کند که تمام context variables لازم را اضافه می‌کند

**URL**: `/production/machines/<pk>/edit/`

---

## MachineDetailView

### `MachineDetailView`

**توضیح**: نمایش جزئیات Machine (read-only)

**Type**: `BaseDetailView` (از `shared.views.base`)

**Template**: `shared/generic/generic_detail.html`

**Attributes**:
- `model`: `Machine`
- `template_name`: `'shared/generic/generic_detail.html'`
- `context_object_name`: `'object'`
- `feature_code`: `'production.machines'`
- `required_action`: `'view_own'`
- `active_module`: `'production'`

**Context Variables**:
- `object`: Machine instance
- `detail_title`: `_('View Machine')`
- `info_banner`: لیست اطلاعات اصلی (code, status, machine_status)
- `detail_sections`: لیست sections برای نمایش:
  - Basic Information: name, name_en (اگر موجود باشد), machine_type, work_center (اگر موجود باشد), manufacturer (اگر موجود باشد), model_number (اگر موجود باشد), serial_number (اگر موجود باشد), description (اگر موجود باشد)
  - Notes: اگر notes موجود باشد
- `list_url`, `edit_url`: URLs برای navigation
- `can_edit_object`: بررسی اینکه آیا Machine قفل است یا نه

**متدها**:

#### `get_queryset(self) -> QuerySet`
- **Returns**: queryset بهینه شده با select_related
- **Logic**:
  1. دریافت queryset از `super().get_queryset()`
  2. اعمال `select_related('work_center', 'created_by', 'edited_by')`
  3. بازگشت queryset

#### `get_context_data(self, **kwargs) -> Dict[str, Any]`
- **Returns**: context با detail sections
- **Logic**:
  1. دریافت context از `super().get_context_data()`
  2. ساخت `info_banner`:
     - Code (type: 'code')
     - Status (type: 'badge')
     - Machine Status
  3. ساخت `detail_sections`:
     - **Basic Information**: name, name_en (اگر موجود باشد), machine_type, work_center (اگر موجود باشد), manufacturer (اگر موجود باشد), model_number (اگر موجود باشد), serial_number (اگر موجود باشد), description (اگر موجود باشد)
     - **Notes**: اگر notes موجود باشد
  4. بازگشت context

#### `get_list_url(self) -> str`
- **Returns**: URL برای لیست Machines

#### `get_edit_url(self) -> str`
- **Returns**: URL برای ویرایش Machine

#### `can_edit_object(self, obj=None, feature_code=None) -> bool`
- **Returns**: True اگر Machine قفل نباشد
- **Logic**:
  - بررسی `is_locked` attribute
  - اگر `is_locked=True` باشد، return False

**URL**: `/production/machines/<pk>/`

---

## MachineDeleteView

**Type**: `BaseDeleteView` (از `shared.views.base`)

**Template**: `shared/generic/generic_confirm_delete.html`

**Success URL**: `production:machines`

**Attributes**:
- `model`: `Machine`
- `template_name`: `'shared/generic/generic_confirm_delete.html'`
- `success_url`: `reverse_lazy('production:machines')`
- `feature_code`: `'production.machines'`
- `required_action`: `'delete_own'`

**متدها**:

#### `get_queryset(self) -> QuerySet`
- **Returns**: queryset فیلتر شده بر اساس company
- **Logic**:
  - از base class استفاده می‌کند که company filtering را مدیریت می‌کند

#### `delete(self, request: Any, *args: Any, **kwargs: Any) -> HttpResponseRedirect`
- **Parameters**: `request`, `*args`, `**kwargs`
- **Returns**: redirect به `success_url`
- **Logic**:
  - فراخوانی `super().delete()` که Machine را حذف می‌کند و پیام موفقیت نمایش می‌دهد

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`
- **Returns**: context با delete title، confirmation message، object details، و breadcrumbs
- **Logic**:
  - از base class استفاده می‌کند که تمام context variables لازم را اضافه می‌کند

**URL**: `/production/machines/<pk>/delete/`

---

## الگوهای مشترک

1. **Company Filtering**: تمام queryset ها بر اساس `active_company_id` فیلتر می‌شوند
2. **Permission Checking**: تمام views از `FeaturePermissionRequiredMixin` استفاده می‌کنند
3. **Optional select_related**: `select_related('work_center')` با try-except برای جلوگیری از خطا
4. **Generic Templates**: تمام templates به generic templates منتقل شده‌اند:
   - Machine List از `shared/generic/generic_list.html` extends می‌کند
   - Machine Form از `shared/generic/generic_form.html` extends می‌کند
   - Machine Delete از `shared/generic/generic_confirm_delete.html` استفاده می‌کند

