# shared/views/companies.py - Company Management Views (Complete Documentation)

**هدف**: Views برای مدیریت شرکت‌ها (CRUD operations) در ماژول shared

این فایل شامل **4 کلاس view**:
- `CompanyListView`: فهرست شرکت‌هایی که کاربر به آن‌ها دسترسی دارد
- `CompanyCreateView`: ایجاد شرکت جدید
- `CompanyUpdateView`: ویرایش شرکت موجود
- `CompanyDeleteView`: حذف شرکت

---

## وابستگی‌ها

- `shared.models`: `Company`, `UserCompanyAccess`
- `shared.forms`: `CompanyForm`
- `shared.mixins`: `FeaturePermissionRequiredMixin`
- `django.views.generic`: `ListView`, `CreateView`, `UpdateView`, `DeleteView`
- `django.http`: `HttpResponseRedirect`
- `django.urls`: `reverse_lazy`
- `django.utils.translation`: `gettext_lazy`
- `django.contrib.messages`
- `typing`: `Any`, `Dict`

---

## CompanyListView

**Type**: `FeaturePermissionRequiredMixin, ListView`

**Template**: `shared/companies.html`

**Attributes**:
- `model`: `Company`
- `template_name`: `'shared/companies.html'`
- `context_object_name`: `'companies'`
- `paginate_by`: `50`
- `feature_code`: `'shared.companies'`

**متدها**:

#### `get_queryset() -> QuerySet`

**توضیح**: فیلتر کردن شرکت‌ها بر اساس دسترسی کاربر.

**مقدار بازگشتی**:
- `QuerySet`: queryset شرکت‌هایی که کاربر به آن‌ها دسترسی دارد

**منطق**:
1. دریافت company IDs از `UserCompanyAccess` برای کاربر فعلی
2. فیلتر `UserCompanyAccess` بر اساس:
   - `user = self.request.user`
   - `is_enabled = 1`
3. استخراج `company_id` values
4. فیلتر `Company` بر اساس:
   - `id__in=user_company_ids`
   - `is_enabled = 1`
5. مرتب‌سازی بر اساس `public_code`

**نکات مهم**:
- فقط شرکت‌هایی نمایش داده می‌شوند که کاربر به آن‌ها دسترسی دارد
- از `UserCompanyAccess` برای تعیین دسترسی استفاده می‌شود

---

#### `get_context_data(**kwargs) -> Dict[str, Any]`

**توضیح**: اضافه کردن active module به context.

**Context Variables**:
- `companies`: queryset شرکت‌ها (paginated)
- `active_module`: `'shared'`

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با active_module

**URL**: `/shared/companies/`

---

## CompanyCreateView

**Type**: `FeaturePermissionRequiredMixin, CreateView`

**Template**: `shared/company_form.html`

**Form**: `CompanyForm`

**Success URL**: `shared:companies`

**Attributes**:
- `feature_code`: `'shared.companies'`
- `required_action`: `'create'`

**متدها**:

#### `form_valid(self, form: CompanyForm) -> HttpResponseRedirect`

**توضیح**: تنظیم خودکار `created_by` و ایجاد `UserCompanyAccess` برای creator.

**پارامترهای ورودی**:
- `form`: `CompanyForm` validated

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به success URL

**منطق**:
1. تنظیم `form.instance.created_by = self.request.user`
2. فراخوانی `super().form_valid(form)` برای ذخیره company
3. ایجاد `UserCompanyAccess` برای creator:
   - `user = self.request.user`
   - `company = self.object`
   - `access_level_id = 1` (ADMIN level)
   - `is_primary = 1` (primary company)
   - `is_enabled = 1`
4. نمایش پیام موفقیت
5. بازگشت response

**نکات مهم**:
- بعد از ایجاد company، creator به صورت خودکار ADMIN access دریافت می‌کند
- Company به عنوان primary company برای creator تنظیم می‌شود

---

#### `get_context_data(**kwargs) -> Dict[str, Any]`

**توضیح**: اضافه کردن active module و form title به context.

**Context Variables**:
- `form`: `CompanyForm`
- `active_module`: `'shared'`
- `form_title`: `_('Create Company')`

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با form_title

**URL**: `/shared/companies/create/`

---

## CompanyUpdateView

**Type**: `FeaturePermissionRequiredMixin, UpdateView`

**Template**: `shared/company_form.html`

**Form**: `CompanyForm`

**Success URL**: `shared:companies`

**Attributes**:
- `feature_code`: `'shared.companies'`
- `required_action`: `'edit_own'`

**متدها**:

#### `form_valid(self, form: CompanyForm) -> HttpResponseRedirect`

**توضیح**: تنظیم خودکار `edited_by`.

**پارامترهای ورودی**:
- `form`: `CompanyForm` validated

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به success URL

**منطق**:
1. تنظیم `form.instance.edited_by = self.request.user`
2. نمایش پیام موفقیت
3. فراخوانی `super().form_valid(form)` برای ذخیره

---

#### `get_context_data(**kwargs) -> Dict[str, Any]`

**توضیح**: اضافه کردن active module و form title به context.

**Context Variables**:
- `form`: `CompanyForm`
- `company`: company object (از `get_object()`)
- `active_module`: `'shared'`
- `form_title`: `_('Edit Company')`

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با form_title

**URL**: `/shared/companies/<pk>/edit/`

---

## CompanyDeleteView

**Type**: `FeaturePermissionRequiredMixin, DeleteView`

**Template**: `shared/company_confirm_delete.html`

**Success URL**: `shared:companies`

**Attributes**:
- `feature_code`: `'shared.companies'`
- `required_action`: `'delete_own'`

**متدها**:

#### `delete(self, request: Any, *args: Any, **kwargs: Any) -> HttpResponseRedirect`

**توضیح**: حذف company و نمایش پیام موفقیت.

**پارامترهای ورودی**:
- `request`: HTTP request
- `*args`, `**kwargs`: آرگومان‌های اضافی

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به success URL

**منطق**:
1. نمایش پیام موفقیت
2. فراخوانی `super().delete()` برای حذف company

---

#### `get_context_data(**kwargs) -> Dict[str, Any]`

**توضیح**: اضافه کردن active module به context.

**Context Variables**:
- `company`: company object (از `get_object()`)
- `active_module`: `'shared'`

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با active_module

**URL**: `/shared/companies/<pk>/delete/`

---

## نکات مهم

### 1. User Access Filtering
- `CompanyListView` فقط شرکت‌هایی را نمایش می‌دهد که کاربر به آن‌ها دسترسی دارد
- دسترسی از طریق `UserCompanyAccess` تعیین می‌شود
- از `values_list('company_id', flat=True)` برای استخراج IDs استفاده می‌شود

### 2. Auto Access Creation
- بعد از ایجاد company، creator به صورت خودکار ADMIN access دریافت می‌کند
- `access_level_id = 1` (ADMIN level)
- `is_primary = 1` (primary company برای creator)

### 3. Permission Checking
- از `FeaturePermissionRequiredMixin` استفاده می‌کند
- `feature_code = 'shared.companies'`
- Actions: `'view'`, `'create'`, `'edit_own'`, `'delete_own'`

### 4. Ordering
- Companies بر اساس `public_code` مرتب می‌شوند

### 5. Enabled Filtering
- فقط companies با `is_enabled = 1` نمایش داده می‌شوند
- فقط `UserCompanyAccess` با `is_enabled = 1` در نظر گرفته می‌شوند

### 6. Auto Field Setting
- `created_by` در `CompanyCreateView` به صورت خودکار تنظیم می‌شود
- `edited_by` در `CompanyUpdateView` به صورت خودکار تنظیم می‌شود

---

## الگوهای مشترک

1. **Permission Checking**: از `FeaturePermissionRequiredMixin` استفاده می‌کند
2. **Access Filtering**: از `UserCompanyAccess` برای فیلتر کردن دسترسی استفاده می‌کند
3. **Auto Field Setting**: `created_by` و `edited_by` به صورت خودکار تنظیم می‌شوند
4. **Error Handling**: خطاها با messages نمایش داده می‌شوند
5. **Context Management**: `active_module` در تمام views اضافه می‌شود

---

## استفاده در پروژه

این views در URLs ماژول shared ثبت شده‌اند:

```python
# shared/urls.py
path('companies/', CompanyListView.as_view(), name='companies'),
path('companies/create/', CompanyCreateView.as_view(), name='company_create'),
path('companies/<int:pk>/edit/', CompanyUpdateView.as_view(), name='company_edit'),
path('companies/<int:pk>/delete/', CompanyDeleteView.as_view(), name='company_delete'),
```

---

## ارتباط با سایر ماژول‌ها

### Shared Models
- از `Company` model استفاده می‌کند
- از `UserCompanyAccess` برای مدیریت دسترسی استفاده می‌کند

### Shared Forms
- از `CompanyForm` برای create و update استفاده می‌کند

### Shared Mixins
- از `FeaturePermissionRequiredMixin` برای permission checking استفاده می‌کند

