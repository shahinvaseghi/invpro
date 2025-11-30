# production/views/personnel.py - Personnel Views (Complete Documentation)

**هدف**: Views برای مدیریت پرسنل در ماژول production

این فایل شامل views برای:
- PersonnelListView: فهرست پرسنل
- PersonCreateView: ایجاد پرسنل جدید
- PersonUpdateView: ویرایش پرسنل
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

**Type**: `FeaturePermissionRequiredMixin, ListView`

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

**Type**: `FeaturePermissionRequiredMixin, CreateView`

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

**توضیح**: Person را ذخیره می‌کند و پیام موفقیت نمایش می‌دهد.

**پارامترهای ورودی**:
- `form`: فرم معتبر `PersonForm`

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به `success_url`

**منطق**:
1. دریافت `active_company_id` از session
2. اگر `active_company_id` وجود ندارد:
   - خطا: "Please select a company first."
   - `form_invalid()` برمی‌گرداند
3. تنظیم `form.instance.company_id = active_company_id`
4. تنظیم `form.instance.created_by = request.user`
5. نمایش پیام موفقیت: "Person created successfully."
6. فراخوانی `super().form_valid(form)` (ذخیره و redirect)

---

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`

**توضیح**: context variables را برای template اضافه می‌کند.

**پارامترهای ورودی**:
- `**kwargs`: متغیرهای context اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با `active_module` و `form_title`

**Context Variables اضافه شده**:
- `active_module`: `'production'`
- `form_title`: `_('Create Person')`

**URL**: `/production/personnel/create/`

---

## PersonUpdateView

**Type**: `FeaturePermissionRequiredMixin, UpdateView`

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

**توضیح**: Person را ذخیره می‌کند و پیام موفقیت نمایش می‌دهد.

**پارامترهای ورودی**:
- `form`: فرم معتبر `PersonForm`

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به `success_url`

**منطق**:
1. تنظیم `form.instance.edited_by = request.user`
2. نمایش پیام موفقیت: "Person updated successfully."
3. فراخوانی `super().form_valid(form)` (ذخیره و redirect)

---

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`

**توضیح**: context variables را برای template اضافه می‌کند.

**پارامترهای ورودی**:
- `**kwargs`: متغیرهای context اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با `active_module` و `form_title`

**Context Variables اضافه شده**:
- `active_module`: `'production'`
- `form_title`: `_('Edit Person')`

**URL**: `/production/personnel/<pk>/edit/`

---

## PersonDeleteView

**Type**: `FeaturePermissionRequiredMixin, DeleteView`

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

#### `delete(self, request: Any, *args: Any, **kwargs: Any) -> HttpResponseRedirect`

**توضیح**: Person را حذف می‌کند و پیام موفقیت نمایش می‌دهد.

**پارامترهای ورودی**:
- `request`: HTTP request
- `*args`, `**kwargs`: آرگومان‌های اضافی

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به `success_url`

**منطق**:
1. نمایش پیام موفقیت: "Person deleted successfully."
2. فراخوانی `super().delete(request, *args, **kwargs)` (که Person را حذف می‌کند و redirect می‌کند)

---

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`

**توضیح**: context variables را برای template اضافه می‌کند.

**پارامترهای ورودی**:
- `**kwargs`: متغیرهای context اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با `active_module`

**Context Variables اضافه شده**:
- `active_module`: `'production'`

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

