# accounting/views/fiscal_years.py - Fiscal Year Views (Complete Documentation)

**هدف**: CRUD views برای مدیریت سال‌های مالی در ماژول accounting

این فایل شامل **4 کلاس view**:
- `FiscalYearListView`: فهرست سال‌های مالی
- `FiscalYearCreateView`: ایجاد سال مالی جدید
- `FiscalYearUpdateView`: ویرایش سال مالی
- `FiscalYearDeleteView`: حذف سال مالی

---

## وابستگی‌ها

- `accounting.models`: `FiscalYear`
- `accounting.forms`: `FiscalYearForm`
- `accounting.views.base`: `AccountingBaseView`
- `shared.mixins`: `FeaturePermissionRequiredMixin`
- `shared.views.base`: `EditLockProtectedMixin`
- `django.views.generic`: `CreateView`, `DeleteView`, `ListView`, `UpdateView`
- `django.contrib`: `messages`
- `django.db.models`: `Q`
- `django.http`: `HttpResponseRedirect`
- `django.urls`: `reverse`, `reverse_lazy`
- `django.utils.translation`: `gettext_lazy`
- `typing`: `Any`, `Dict`

---

## FiscalYearListView

**Type**: `FeaturePermissionRequiredMixin`, `AccountingBaseView`, `ListView`

**Template**: `shared/generic/generic_list.html`

**توضیح**: فهرست تمام سال‌های مالی برای company فعال

**Attributes**:
- `model`: `FiscalYear`
- `template_name`: `'shared/generic/generic_list.html'`
- `context_object_name`: `'object_list'`
- `paginate_by`: `50`
- `feature_code`: `'accounting.fiscal_years'`

**متدها**:

#### `get_queryset(self) -> QuerySet`

**توضیح**: queryset را بر اساس active company، permissions، search و status filter می‌کند.

**مقدار بازگشتی**:
- `QuerySet`: queryset فیلتر شده

**منطق**:
1. ابتدا `super().get_queryset()` را فراخوانی می‌کند (company filtering)
2. `filter_queryset_by_permissions()` را با feature code `'accounting.fiscal_years'` فراخوانی می‌کند
3. `search` را از GET parameters می‌گیرد
4. اگر `search` وجود دارد:
   - queryset را بر اساس `fiscal_year_code` یا `fiscal_year_name` فیلتر می‌کند (case-insensitive)
5. `status` را از GET parameters می‌گیرد
6. اگر `status` در `('0', '1')` باشد:
   - queryset را بر اساس `is_enabled` فیلتر می‌کند
7. در غیر این صورت (default):
   - فقط سال‌های مالی فعال (`is_enabled=1`) را نمایش می‌دهد
8. queryset را بر اساس `-fiscal_year_code` مرتب می‌کند (جدیدترین اول)
9. queryset را برمی‌گرداند

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`

**توضیح**: context variables را برای generic_list template اضافه می‌کند.

**پارامترهای ورودی**:
- `**kwargs`: context variables از parent classes

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با تمام متغیرهای لازم برای generic_list template

**Context Variables اضافه شده**:
- `page_title`: `_('Fiscal Years')`
- `breadcrumbs`: لیست breadcrumb items (Dashboard → Accounting → Fiscal Years)
- `create_url`: URL برای ایجاد سال مالی جدید
- `create_button_text`: `_('Create Fiscal Year')`
- `show_filters`: `True`
- `status_filter`: `True`
- `search_placeholder`: `_('Search by code or name')`
- `clear_filter_url`: URL برای پاک کردن فیلترها
- `print_enabled`: `True`
- `show_actions`: `True`
- `edit_url_name`: `'accounting:fiscal_year_edit'`
- `delete_url_name`: `'accounting:fiscal_year_delete'`
- `table_headers`: لیست header های جدول
- `empty_state_title`: `_('No Fiscal Years Found')`
- `empty_state_message`: `_('Start by adding your first fiscal year.')`
- `empty_state_icon`: `'📅'`

**URL**: `/accounting/fiscal-years/`

---

## FiscalYearCreateView

**Type**: `FeaturePermissionRequiredMixin`, `AccountingBaseView`, `CreateView`

**Template**: `shared/generic/generic_form.html`

**Form**: `FiscalYearForm`

**Success URL**: `accounting:fiscal_years`

**Attributes**:
- `model`: `FiscalYear`
- `form_class`: `FiscalYearForm`
- `template_name`: `'shared/generic/generic_form.html'`
- `success_url`: `reverse_lazy('accounting:fiscal_years')`
- `feature_code`: `'accounting.fiscal_years'`
- `required_action`: `'create'`

**متدها**:

#### `get_form_kwargs(self) -> Dict[str, Any]`

**توضیح**: `company_id` را به form kwargs اضافه می‌کند.

**مقدار بازگشتی**:
- `Dict[str, Any]`: form kwargs با `company_id` اضافه شده

**منطق**:
1. `super().get_form_kwargs()` را فراخوانی می‌کند
2. `active_company_id` را از session می‌گیرد
3. `company_id` را به kwargs اضافه می‌کند
4. kwargs را برمی‌گرداند

#### `form_valid(self, form: FiscalYearForm) -> HttpResponseRedirect`

**توضیح**: قبل از ذخیره، `created_by` را تنظیم می‌کند و پیام موفقیت نمایش می‌دهد.

**پارامترهای ورودی**:
- `form`: فرم معتبر `FiscalYearForm`

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به success_url

**منطق**:
1. `form.instance.created_by` را به `self.request.user` تنظیم می‌کند
2. پیام موفقیت را با `messages.success()` نمایش می‌دهد
3. `super().form_valid(form)` را فراخوانی می‌کند

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`

**توضیح**: context variables را برای generic_form template اضافه می‌کند.

**Context Variables اضافه شده**:
- `form_title`: `_('Create Fiscal Year')`
- `breadcrumbs`: لیست breadcrumb items (Dashboard → Accounting → Fiscal Years)
- `cancel_url`: URL برای cancel (بازگشت به لیست)

**URL**: `/accounting/fiscal-years/create/`

---

## FiscalYearUpdateView

**Type**: `EditLockProtectedMixin`, `FeaturePermissionRequiredMixin`, `AccountingBaseView`, `UpdateView`

**Template**: `shared/generic/generic_form.html`

**Form**: `FiscalYearForm`

**Success URL**: `accounting:fiscal_years`

**Attributes**:
- `model`: `FiscalYear`
- `form_class`: `FiscalYearForm`
- `template_name`: `'shared/generic/generic_form.html'`
- `success_url`: `reverse_lazy('accounting:fiscal_years')`
- `feature_code`: `'accounting.fiscal_years'`
- `required_action`: `'edit_own'`

**متدها**:

#### `get_form_kwargs(self) -> Dict[str, Any]`

**توضیح**: `company_id` را به form kwargs اضافه می‌کند.

**مقدار بازگشتی**:
- `Dict[str, Any]`: form kwargs با `company_id` اضافه شده

**منطق**: مشابه `FiscalYearCreateView.get_form_kwargs()`

#### `form_valid(self, form: FiscalYearForm) -> HttpResponseRedirect`

**توضیح**: قبل از ذخیره، `edited_by` را تنظیم می‌کند و پیام موفقیت نمایش می‌دهد.

**پارامترهای ورودی**:
- `form`: فرم معتبر `FiscalYearForm`

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به success_url

**منطق**:
1. `form.instance.edited_by` را به `self.request.user` تنظیم می‌کند
2. پیام موفقیت را با `messages.success()` نمایش می‌دهد
3. `super().form_valid(form)` را فراخوانی می‌کند

**نکته**: این view از `EditLockProtectedMixin` استفاده می‌کند که از concurrent editing جلوگیری می‌کند.

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`

**توضیح**: context variables را برای generic_form template اضافه می‌کند.

**Context Variables اضافه شده**:
- `form_title`: `_('Edit Fiscal Year')`
- `breadcrumbs`: لیست breadcrumb items (Dashboard → Accounting → Fiscal Years)
- `cancel_url`: URL برای cancel (بازگشت به لیست)

**URL**: `/accounting/fiscal-years/<int:pk>/edit/`

---

## FiscalYearDeleteView

**Type**: `FeaturePermissionRequiredMixin`, `AccountingBaseView`, `DeleteView`

**Template**: `shared/generic/generic_confirm_delete.html`

**Success URL**: `accounting:fiscal_years`

**Attributes**:
- `model`: `FiscalYear`
- `success_url`: `reverse_lazy('accounting:fiscal_years')`
- `template_name`: `'shared/generic/generic_confirm_delete.html'`
- `feature_code`: `'accounting.fiscal_years'`
- `required_action`: `'delete_own'`

**متدها**:

#### `delete(self, request: Any, *args: Any, **kwargs: Any) -> HttpResponseRedirect`

**توضیح**: سال مالی را حذف می‌کند و پیام موفقیت نمایش می‌دهد.

**پارامترهای ورودی**:
- `request`: HttpRequest
- `*args`: Additional arguments
- `**kwargs`: Additional keyword arguments

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به success_url

**منطق**:
1. پیام موفقیت را با `messages.success()` نمایش می‌دهد
2. `super().delete(request, *args, **kwargs)` را فراخوانی می‌کند

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`

**توضیح**: context variables را برای generic_confirm_delete template اضافه می‌کند.

**Context Variables اضافه شده**:
- `delete_title`: `_('Delete Fiscal Year')`
- `confirmation_message`: `_('Do you really want to delete this fiscal year?')`
- `breadcrumbs`: لیست breadcrumb items (Dashboard → Accounting → Fiscal Years → Delete)
- `object_details`: لیست جزئیات object برای نمایش در صفحه حذف
- `cancel_url`: URL برای cancel (بازگشت به لیست)

**Object Details**:
- Code: `self.object.fiscal_year_code`
- Name: `self.object.fiscal_year_name`
- Start Date: `self.object.start_date`
- End Date: `self.object.end_date`

**URL**: `/accounting/fiscal-years/<int:pk>/delete/`

---

## استفاده در پروژه

### URL Patterns
```python
path('fiscal-years/', FiscalYearListView.as_view(), name='fiscal_years'),
path('fiscal-years/create/', FiscalYearCreateView.as_view(), name='fiscal_year_create'),
path('fiscal-years/<int:pk>/edit/', FiscalYearUpdateView.as_view(), name='fiscal_year_edit'),
path('fiscal-years/<int:pk>/delete/', FiscalYearDeleteView.as_view(), name='fiscal_year_delete'),
```

### Permission Checking
تمام views از `FeaturePermissionRequiredMixin` استفاده می‌کنند و feature code `'accounting.fiscal_years'` را دارند.

### Generic Templates
تمام views از تمپلیت‌های generic استفاده می‌کنند:
- List: `shared/generic/generic_list.html`
- Form: `shared/generic/generic_form.html`
- Delete: `shared/generic/generic_confirm_delete.html`

---

## نکات مهم

1. **Company Filtering**: تمام queryset ها به صورت خودکار بر اساس active company فیلتر می‌شوند
2. **Permission Filtering**: `filter_queryset_by_permissions` برای کنترل دسترسی استفاده می‌شود
3. **Search Support**: جستجو بر اساس `fiscal_year_code` و `fiscal_year_name`
4. **Status Filter**: فیلتر بر اساس `is_enabled` (default: فقط فعال‌ها)
5. **Edit Lock**: `FiscalYearUpdateView` از `EditLockProtectedMixin` استفاده می‌کند
6. **Auto User Setting**: `created_by` و `edited_by` به صورت خودکار تنظیم می‌شوند
7. **Success Messages**: تمام عملیات پیام موفقیت نمایش می‌دهند

---

**Last Updated**: 2025-12-01

