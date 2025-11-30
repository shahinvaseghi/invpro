# shared/views/company_units.py - Company Unit Management Views (Complete Documentation)

**هدف**: Views برای مدیریت Company Units (واحدهای سازمانی) در ماژول shared

این فایل شامل **4 کلاس view**:
- `CompanyUnitListView`: فهرست واحدهای سازمانی شرکت فعال
- `CompanyUnitCreateView`: ایجاد واحد سازمانی جدید
- `CompanyUnitUpdateView`: ویرایش واحد سازمانی موجود
- `CompanyUnitDeleteView`: حذف واحد سازمانی

---

## وابستگی‌ها

- `shared.models`: `CompanyUnit`
- `shared.forms`: `CompanyUnitForm`
- `shared.mixins`: `FeaturePermissionRequiredMixin`
- `django.views.generic`: `ListView`, `CreateView`, `UpdateView`, `DeleteView`
- `django.http`: `HttpResponseRedirect`
- `django.urls`: `reverse_lazy`
- `django.utils.translation`: `gettext_lazy`
- `django.contrib.messages`
- `django.db.models`: `Q`
- `typing`: `Any`, `Dict`, `Optional`

---

## CompanyUnitListView

**Type**: `FeaturePermissionRequiredMixin, ListView`

**Template**: `shared/company_units.html` (extends `shared/generic/generic_list.html`)

**Attributes**:
- `model`: `CompanyUnit`
- `template_name`: `'shared/company_units.html'`
- `context_object_name`: `'object_list'`
- `paginate_by`: `50`
- `feature_code`: `'shared.company_units'`

**متدها**:

#### `get_queryset() -> QuerySet`

**توضیح**: فیلتر کردن company units بر اساس شرکت فعال و search/filter criteria.

**مقدار بازگشتی**:
- `QuerySet`: queryset company units فیلتر شده

**منطق**:
1. دریافت `active_company_id` از session
2. اگر `active_company_id` موجود نباشد، return empty queryset
3. فیلتر بر اساس `company_id = active_company_id`
4. `select_related('parent_unit')` برای بهینه‌سازی
5. مرتب‌سازی بر اساس `public_code`
6. فیلتر بر اساس `search` (در `public_code` یا `name`)
7. فیلتر بر اساس `status` ('0' یا '1' برای `is_enabled`)

**Query Parameters**:
- `search`: جستجو در public_code و name
- `status`: '0' (inactive) یا '1' (active)

**نکات مهم**:
- فقط units شرکت فعال نمایش داده می‌شوند
- اگر شرکت فعال وجود نداشته باشد، empty queryset return می‌شود

---

#### `get_context_data(**kwargs) -> Dict[str, Any]`

**توضیح**: اضافه کردن active module و filters به context.

**Context Variables**:
- `units`: queryset company units (paginated)
- `active_module`: `'shared'`
- `filters`: dictionary با `search` و `status` values

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با filters

**URL**: `/shared/company-units/`

---

## CompanyUnitCreateView

**Type**: `FeaturePermissionRequiredMixin, CreateView`

**Template**: `shared/company_unit_form.html` (extends `shared/generic/generic_form.html`)

**Form**: `CompanyUnitForm`

**Success URL**: `shared:company_units`

**Attributes**:
- `feature_code`: `'shared.company_units'`
- `required_action`: `'create'`

**متدها**:

#### `get_form_kwargs() -> Dict[str, Any]`

**توضیح**: اضافه کردن `company_id` به form kwargs.

**مقدار بازگشتی**:
- `Dict[str, Any]`: form kwargs با `company_id`

**منطق**:
- دریافت `active_company_id` از session
- اضافه کردن به form kwargs

---

#### `form_valid(self, form: CompanyUnitForm) -> HttpResponseRedirect`

**توضیح**: تنظیم `company_id` و نمایش پیام موفقیت.

**پارامترهای ورودی**:
- `form`: `CompanyUnitForm` validated

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به success URL

**منطق**:
1. دریافت `active_company_id` از session
2. بررسی وجود `active_company_id`
3. اگر موجود نباشد: error message و return `form_invalid`
4. تنظیم `form.instance.company_id = active_company_id`
5. نمایش پیام موفقیت
6. فراخوانی `super().form_valid(form)` برای ذخیره

**Error Handling**:
- اگر `active_company_id` موجود نباشد: error message

---

#### `get_context_data(**kwargs) -> Dict[str, Any]`

**توضیح**: اضافه کردن active module و form title به context.

**Context Variables**:
- `form`: `CompanyUnitForm`
- `active_module`: `'shared'`
- `form_title`: `_('Create Company Unit')`
- `breadcrumbs`: لیست breadcrumbs برای navigation
- `cancel_url`: URL برای cancel (back to company units list)

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با form_title

**URL**: `/shared/company-units/create/`

---

## CompanyUnitUpdateView

**Type**: `FeaturePermissionRequiredMixin, UpdateView`

**Template**: `shared/company_unit_form.html` (extends `shared/generic/generic_form.html`)

**Form**: `CompanyUnitForm`

**Success URL**: `shared:company_units`

**Attributes**:
- `feature_code`: `'shared.company_units'`
- `required_action`: `'edit_own'`

**متدها**:

#### `get_form_kwargs() -> Dict[str, Any]`

**توضیح**: اضافه کردن `company_id` به form kwargs.

**مقدار بازگشتی**:
- `Dict[str, Any]`: form kwargs با `company_id`

**منطق**:
- استفاده از `self.object.company_id` (از existing unit)

---

#### `form_valid(self, form: CompanyUnitForm) -> HttpResponseRedirect`

**توضیح**: نمایش پیام موفقیت.

**پارامترهای ورودی**:
- `form`: `CompanyUnitForm` validated

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به success URL

**منطق**:
1. نمایش پیام موفقیت
2. فراخوانی `super().form_valid(form)` برای ذخیره

---

#### `get_context_data(**kwargs) -> Dict[str, Any]`

**توضیح**: اضافه کردن active module و form title به context.

**Context Variables**:
- `form`: `CompanyUnitForm`
- `object`: company unit object (از `get_object()`)
- `active_module`: `'shared'`
- `form_title`: `_('Edit Company Unit')`
- `breadcrumbs`: لیست breadcrumbs برای navigation
- `cancel_url`: URL برای cancel (back to company units list)

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با form_title

**URL**: `/shared/company-units/<pk>/edit/`

---

## CompanyUnitDeleteView

**Type**: `FeaturePermissionRequiredMixin, DeleteView`

**Template**: `shared/generic/generic_confirm_delete.html`

**Success URL**: `shared:company_units`

**Attributes**:
- `feature_code`: `'shared.company_units'`
- `required_action`: `'delete_own'`

**متدها**:

#### `delete(self, request: Any, *args: Any, **kwargs: Any) -> HttpResponseRedirect`

**توضیح**: حذف company unit و نمایش پیام موفقیت.

**پارامترهای ورودی**:
- `request`: HTTP request
- `*args`, `**kwargs`: آرگومان‌های اضافی

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به success URL

**منطق**:
1. نمایش پیام موفقیت
2. فراخوانی `super().delete()` برای حذف unit

---

#### `get_context_data(**kwargs) -> Dict[str, Any]`

**توضیح**: اضافه کردن active module به context.

**Context Variables**:
- `object`: company unit object (از `get_object()`)
- `active_module`: `'shared'`
- `delete_title`: `_('Delete Company Unit')`
- `confirmation_message`: پیام تایید حذف با unit name
- `breadcrumbs`: لیست breadcrumbs برای navigation
- `object_details`: لیست جزئیات unit برای نمایش (code, name, parent_unit)
- `cancel_url`: URL برای cancel (back to company units list)

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با active_module

**URL**: `/shared/company-units/<pk>/delete/`

---

## نکات مهم

### 1. Company Scoping
- تمام units بر اساس `active_company_id` فیلتر می‌شوند
- اگر شرکت فعال وجود نداشته باشد، empty queryset return می‌شود
- `company_id` به صورت خودکار در create تنظیم می‌شود

### 2. Parent Unit Relationship
- Units می‌توانند `parent_unit` داشته باشند (hierarchical structure)
- از `select_related('parent_unit')` برای بهینه‌سازی استفاده می‌شود

### 3. Permission Checking
- از `FeaturePermissionRequiredMixin` استفاده می‌کند
- `feature_code = 'shared.company_units'`
- Actions: `'view'`, `'create'`, `'edit_own'`, `'delete_own'`

### 4. Search and Filter
- Search در `public_code` و `name`
- Status filter: '0' (inactive) یا '1' (active)

### 5. Form Company ID
- `company_id` از session به form پاس داده می‌شود
- در create: از `active_company_id` از session
- در update: از `self.object.company_id`

### 6. Error Handling
- اگر `active_company_id` در create موجود نباشد: error message

---

## الگوهای مشترک

1. **Permission Checking**: از `FeaturePermissionRequiredMixin` استفاده می‌کند
2. **Company Filtering**: تمام queries بر اساس `active_company_id` فیلتر می‌شوند
3. **Error Handling**: خطاها با messages نمایش داده می‌شوند
4. **Context Management**: `active_module` در تمام views اضافه می‌شود

---

## استفاده در پروژه

این views در URLs ماژول shared ثبت شده‌اند:

```python
# shared/urls.py
path('company-units/', CompanyUnitListView.as_view(), name='company_units'),
path('company-units/create/', CompanyUnitCreateView.as_view(), name='company_unit_create'),
path('company-units/<int:pk>/edit/', CompanyUnitUpdateView.as_view(), name='company_unit_edit'),
path('company-units/<int:pk>/delete/', CompanyUnitDeleteView.as_view(), name='company_unit_delete'),
```

---

## ارتباط با سایر ماژول‌ها

### Shared Models
- از `CompanyUnit` model استفاده می‌کند
- Units می‌توانند `parent_unit` داشته باشند (hierarchical)

### Shared Forms
- از `CompanyUnitForm` برای create و update استفاده می‌کند

### Inventory Module
- Company units در issue destinations استفاده می‌شوند
- در warehouse requests و issues برای destination استفاده می‌شوند

---

## Migration to Generic Templates

این views در migration به template های generic منتقل شده‌اند:

### List Template
- **Template**: `shared/company_units.html` (extends `shared/generic/generic_list.html`)
- **Note**: این template قبلاً از generic_list استفاده می‌کرد

### Form Template
- **Template**: `shared/company_unit_form.html` (extends `shared/generic/generic_form.html`)
- **Changes**:
  - Template از `base.html` به `generic_form.html` منتقل شد
  - Blocks override شده: `form_sections`, `form_actions_extra`
  - Context variables اضافه شد: `breadcrumbs`, `cancel_url`, `form_title`
  - متن‌های فارسی به انگلیسی با `_()` تبدیل شد

### Delete Template
- **Template**: `shared/generic/generic_confirm_delete.html` (مستقیم استفاده می‌شود)
- **Changes**:
  - Template اختصاصی حذف شد
  - `get_context_data` به‌روزرسانی شد تا context variables مناسب را ارسال کند
  - پیام موفقیت از فارسی به انگلیسی با `_()` تبدیل شد

