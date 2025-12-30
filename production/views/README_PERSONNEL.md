# production/views/personnel.py - Personnel Views (Complete Documentation)

**هدف**: Views برای مدیریت پرسنل در ماژول production

این فایل شامل views برای:
- PersonnelListView: فهرست پرسنل
- PersonCreateView: ایجاد پرسنل جدید
- PersonUpdateView: ویرایش پرسنل
- PersonDetailView: نمایش جزئیات پرسنل
- PersonDeleteView: حذف پرسنل

---

## وابستگی‌ها

- `shared.mixins`: `FeaturePermissionRequiredMixin`
- `production.forms`: `PersonForm`
- `production.models`: `Person`
- `django.views.generic`: `CreateView`, `DeleteView`, `ListView`, `UpdateView`
- `django.contrib.messages`
- `django.contrib.auth.mixins.LoginRequiredMixin`
- `django.http.HttpResponseRedirect`
- `django.urls.reverse_lazy`
- `django.utils.translation.gettext_lazy`

---

## PersonnelListView

**Type**: `BaseListView` (از `shared.views.base`)

**Template**: `production/personnel.html`

**Attributes**:
- `model`: `Person`
- `template_name`: `'production/personnel.html'`
- `context_object_name`: `'personnel'`
- `paginate_by`: `50`
- `feature_code`: `'production.personnel'`

**متدها**:

#### `get_queryset(self) -> QuerySet`

**توضیح**: queryset را با company filtering، is_enabled filtering، select_related، و prefetch_related برمی‌گرداند.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `QuerySet`: queryset فیلتر شده با optimizations

**منطق**:
1. دریافت `active_company_id` از session
2. اگر `active_company_id` وجود ندارد، `Person.objects.none()` برمی‌گرداند
3. فیلتر: `Person.objects.filter(company_id=active_company_id, is_enabled=1)`
4. **select_related**: `'company'`
5. **prefetch_related**: `'company_units'` (ManyToMany relationship)
6. مرتب‌سازی: `order_by('public_code')`
7. queryset را برمی‌گرداند

---

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`

**توضیح**: context variables را برای template اضافه می‌کند.

**پارامترهای ورودی**:
- `**kwargs`: متغیرهای context اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با `active_module`

**Context Variables اضافه شده**:
- `active_module`: `'production'`

**URL**: `/production/personnel/`

---

## PersonCreateView

**Type**: `BaseCreateView` (از `shared.views.base`)

**Template**: `production/person_form.html`

**Form**: `PersonForm`

**Success URL**: `production:personnel`

**Attributes**:
- `model`: `Person`
- `form_class`: `PersonForm`
- `template_name`: `'production/person_form.html'`
- `success_url`: `reverse_lazy('production:personnel')`
- `feature_code`: `'production.personnel'`
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

#### `form_valid(self, form: PersonForm) -> HttpResponseRedirect`
- **Parameters**: `form`: فرم معتبر `PersonForm`
- **Returns**: redirect به `success_url`
- **Logic**:
  - از base class استفاده می‌کند که منطق ذخیره و پیام موفقیت را مدیریت می‌کند

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`
- **Returns**: context با form_title و breadcrumbs
- **Logic**:
  - از base class استفاده می‌کند که تمام context variables لازم را اضافه می‌کند

**URL**: `/production/personnel/create/`

---

## PersonUpdateView

**Type**: `BaseUpdateView` (از `shared.views.base`)

**Template**: `production/person_form.html`

**Form**: `PersonForm`

**Success URL**: `production:personnel`

**Attributes**:
- `model`: `Person`
- `form_class`: `PersonForm`
- `template_name`: `'production/person_form.html'`
- `success_url`: `reverse_lazy('production:personnel')`
- `feature_code`: `'production.personnel'`
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
2. اگر `active_company_id` وجود ندارد، `Person.objects.none()` برمی‌گرداند
3. فیلتر: `Person.objects.filter(company_id=active_company_id)`
4. queryset را برمی‌گرداند

---

#### `form_valid(self, form: PersonForm) -> HttpResponseRedirect`
- **Parameters**: `form`: فرم معتبر `PersonForm`
- **Returns**: redirect به `success_url`
- **Logic**:
  - از base class استفاده می‌کند که منطق ذخیره و پیام موفقیت را مدیریت می‌کند

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`
- **Returns**: context با form_title و breadcrumbs
- **Logic**:
  - از base class استفاده می‌کند که تمام context variables لازم را اضافه می‌کند

**URL**: `/production/personnel/<pk>/edit/`

---

## PersonDetailView

### `PersonDetailView`

**توضیح**: نمایش جزئیات Person (read-only)

**Type**: `BaseDetailView` (از `shared.views.base`)

**Template**: `shared/generic/generic_detail.html`

**Attributes**:
- `model`: `Person`
- `template_name`: `'shared/generic/generic_detail.html'`
- `context_object_name`: `'object'`
- `feature_code`: `'production.personnel'`
- `required_action`: `'view_own'`
- `active_module`: `'production'`

**Context Variables**:
- `object`: Person instance
- `detail_title`: `_('View Person')`
- `info_banner`: لیست اطلاعات اصلی (code, status)
- `detail_sections`: لیست sections برای نمایش:
  - Personal Information: first_name, last_name, national_id (اگر موجود باشد), email (اگر موجود باشد), phone_number (اگر موجود باشد), mobile_number (اگر موجود باشد), username (اگر موجود باشد), personnel_code (اگر موجود باشد), linked_user (اگر موجود باشد)
  - Company Units: اگر company_units موجود باشد (comma-separated list)
  - Description: اگر description موجود باشد
  - Notes: اگر notes موجود باشد
- `list_url`, `edit_url`: URLs برای navigation
- `can_edit_object`: بررسی اینکه آیا Person قفل است یا نه

**متدها**:

#### `get_queryset(self) -> QuerySet`
- **Returns**: queryset بهینه شده با select_related و prefetch_related
- **Logic**:
  1. دریافت queryset از `super().get_queryset()`
  2. اعمال `select_related('user', 'created_by', 'edited_by')`
  3. اعمال `prefetch_related('company_units')`
  4. بازگشت queryset

#### `get_context_data(self, **kwargs) -> Dict[str, Any]`
- **Returns**: context با detail sections
- **Logic**:
  1. دریافت context از `super().get_context_data()`
  2. ساخت `info_banner`:
     - Code (type: 'code')
     - Status (type: 'badge')
  3. ساخت `detail_sections`:
     - **Personal Information**: first_name, last_name, national_id (اگر موجود باشد), email (اگر موجود باشد), phone_number (اگر موجود باشد), mobile_number (اگر موجود باشد), username (اگر موجود باشد), personnel_code (اگر موجود باشد), linked_user (اگر موجود باشد - با `get_full_name()` یا `username`)
     - **Company Units**: اگر `company_units.exists()` باشد:
       - ساخت comma-separated text از `unit.name` برای هر unit
       - اضافه کردن section
     - **Description**: اگر description موجود باشد
     - **Notes**: اگر notes موجود باشد
  4. بازگشت context

#### `get_list_url(self) -> str`
- **Returns**: URL برای لیست Personnel

#### `get_edit_url(self) -> str`
- **Returns**: URL برای ویرایش Person

#### `can_edit_object(self, obj=None, feature_code=None) -> bool`
- **Returns**: True اگر Person قفل نباشد
- **Logic**:
  - بررسی `is_locked` attribute
  - اگر `is_locked=True` باشد، return False

**URL**: `/production/personnel/<pk>/`

---

## PersonDeleteView

**Type**: `BaseDeleteView` (از `shared.views.base`)

**Template**: `shared/generic/generic_confirm_delete.html`

**Success URL**: `production:personnel`

**Attributes**:
- `model`: `Person`
- `template_name`: `'shared/generic/generic_confirm_delete.html'`
- `success_url`: `reverse_lazy('production:personnel')`
- `feature_code`: `'production.personnel'`
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
  - فراخوانی `super().delete()` که Person را حذف می‌کند و پیام موفقیت نمایش می‌دهد

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`
- **Returns**: context با delete title، confirmation message، object details، و breadcrumbs
- **Logic**:
  - از base class استفاده می‌کند که تمام context variables لازم را اضافه می‌کند

**URL**: `/production/personnel/<pk>/delete/`

---

## Generic Templates

تمام templates به generic templates منتقل شده‌اند:

### Personnel List
- **Template**: `production/personnel.html` extends `shared/generic/generic_list.html`
- **Blocks Overridden**: 
  - `page_actions`: اضافه کردن Print button
  - `filter_fields`: Search field
  - `table_rows`: نمایش personnel با Code, Name, National ID, Company Units, Status, Actions
- **Context Variables**:
  - `page_title`: "Personnel"
  - `breadcrumbs`: Production > Personnel
  - `create_url`: URL برای ایجاد Person جدید
  - `search_placeholder`: "Search by code, name, or national ID..."
  - `status_filter`: True (enable status dropdown)
  - `table_headers`: لیست هدرهای جدول
  - `show_actions`: True
  - `edit_url_name`: 'production:person_edit'
  - `delete_url_name`: 'production:person_delete'
  - `empty_state_title`: "No Personnel Found"
  - `empty_state_message`: "Create your first person to get started."
  - `empty_state_icon`: "👤"
  - `print_enabled`: True

### Person Form
- **Template**: `production/person_form.html` extends `shared/generic/generic_form.html`
- **Blocks Overridden**: 
  - `breadcrumb_extra`: مسیر breadcrumb
  - `form_sections`: فیلدهای form (organizational units, basic info, contact info)
  - `extra_styles`: CSS برای checkbox list
  - `form_scripts`: JavaScript برای sync username با personnel code

### Person Delete
- **Template**: `shared/generic/generic_confirm_delete.html`
- **Context Variables**:
  - `delete_title`: عنوان حذف
  - `confirmation_message`: پیام تایید
  - `object_details`: جزئیات شخص (code, name, company units)
  - `cancel_url`: URL برای لغو
  - `breadcrumbs`: مسیر breadcrumb

---

## الگوهای مشترک

1. **Company Filtering**: تمام queryset ها بر اساس `active_company_id` فیلتر می‌شوند
2. **Permission Checking**: تمام views از `FeaturePermissionRequiredMixin` استفاده می‌کنند
3. **ManyToMany Handling**: `company_units` با `prefetch_related` در list view نمایش داده می‌شود

