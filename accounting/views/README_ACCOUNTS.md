# accounting/views/accounts.py - Account Views (Complete Documentation)

**هدف**: CRUD views برای مدیریت حساب‌ها (Chart of Accounts) در ماژول accounting

این فایل شامل **4 کلاس view**:
- `AccountListView`: فهرست حساب‌ها
- `AccountCreateView`: ایجاد حساب جدید
- `AccountUpdateView`: ویرایش حساب
- `AccountDeleteView`: حذف حساب

---

## وابستگی‌ها

- `accounting.models`: `Account`
- `accounting.forms`: `AccountForm`
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

## AccountListView

**Type**: `FeaturePermissionRequiredMixin`, `AccountingBaseView`, `ListView`

**Template**: `shared/generic/generic_list.html`

**توضیح**: فهرست تمام حساب‌ها برای company فعال

**Attributes**:
- `model`: `Account`
- `template_name`: `'shared/generic/generic_list.html'`
- `context_object_name`: `'object_list'`
- `paginate_by`: `50`
- `feature_code`: `'accounting.accounts'`

**متدها**:

#### `get_queryset(self) -> QuerySet`

**توضیح**: queryset را بر اساس active company، permissions، search، status، account_type و account_level filter می‌کند.

**مقدار بازگشتی**:
- `QuerySet`: queryset فیلتر شده

**منطق**:
1. ابتدا `super().get_queryset()` را فراخوانی می‌کند (company filtering)
2. `filter_queryset_by_permissions()` را با feature code `'accounting.accounts'` فراخوانی می‌کند
3. `search` را از GET parameters می‌گیرد
4. اگر `search` وجود دارد:
   - queryset را بر اساس `account_code`, `account_name`, یا `account_name_en` فیلتر می‌کند (case-insensitive)
5. `status` را از GET parameters می‌گیرد
6. اگر `status` در `('0', '1')` باشد:
   - queryset را بر اساس `is_enabled` فیلتر می‌کند
7. در غیر این صورت (default):
   - فقط حساب‌های فعال (`is_enabled=1`) را نمایش می‌دهد
8. `account_type` را از GET parameters می‌گیرد
9. اگر `account_type` وجود دارد:
   - queryset را بر اساس `account_type` فیلتر می‌کند
10. `account_level` را از GET parameters می‌گیرد
11. اگر `account_level` وجود دارد:
    - queryset را بر اساس `account_level` فیلتر می‌کند
12. queryset را بر اساس `account_code` مرتب می‌کند
13. queryset را برمی‌گرداند

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`

**توضیح**: context variables را برای generic_list template اضافه می‌کند.

**Context Variables اضافه شده**:
- `page_title`: `_('Chart of Accounts')`
- `breadcrumbs`: لیست breadcrumb items (Dashboard → Accounting → Chart of Accounts)
- `create_url`: URL برای ایجاد حساب جدید
- `create_button_text`: `_('Create Account')`
- `show_filters`: `True`
- `status_filter`: `True`
- `search_placeholder`: `_('Search by code or name')`
- `clear_filter_url`: URL برای پاک کردن فیلترها
- `print_enabled`: `True`
- `show_actions`: `True`
- `edit_url_name`: `'accounting:account_edit'`
- `delete_url_name`: `'accounting:account_delete'`
- `table_headers`: لیست header های جدول (CODE, Account Name, Type, Level, Parent, Normal Balance, Current Balance, Status)
- `empty_state_title`: `_('No Accounts Found')`
- `empty_state_message`: `_('Start by adding your first account.')`
- `empty_state_icon`: `'📊'`

**URL**: `/accounting/accounts/`

---

## AccountCreateView

**Type**: `FeaturePermissionRequiredMixin`, `AccountingBaseView`, `CreateView`

**Template**: `shared/generic/generic_form.html`

**Form**: `AccountForm`

**Success URL**: `accounting:accounts`

**Attributes**:
- `model`: `Account`
- `form_class`: `AccountForm`
- `template_name`: `'shared/generic/generic_form.html'`
- `success_url`: `reverse_lazy('accounting:accounts')`
- `feature_code`: `'accounting.accounts'`
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

#### `form_valid(self, form: AccountForm) -> HttpResponseRedirect`

**توضیح**: قبل از ذخیره، `created_by` را تنظیم می‌کند و پیام موفقیت نمایش می‌دهد.

**پارامترهای ورودی**:
- `form`: فرم معتبر `AccountForm`

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به success_url

**منطق**:
1. `form.instance.created_by` را به `self.request.user` تنظیم می‌کند
2. پیام موفقیت را با `messages.success()` نمایش می‌دهد
3. `super().form_valid(form)` را فراخوانی می‌کند

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`

**توضیح**: context variables را برای generic_form template اضافه می‌کند.

**Context Variables اضافه شده**:
- `form_title`: `_('Create Account')`
- `breadcrumbs`: لیست breadcrumb items (Dashboard → Accounting → Chart of Accounts)
- `cancel_url`: URL برای cancel (بازگشت به لیست)

**URL**: `/accounting/accounts/create/`

---

## AccountUpdateView

**Type**: `EditLockProtectedMixin`, `FeaturePermissionRequiredMixin`, `AccountingBaseView`, `UpdateView`

**Template**: `shared/generic/generic_form.html`

**Form**: `AccountForm`

**Success URL**: `accounting:accounts`

**Attributes**:
- `model`: `Account`
- `form_class`: `AccountForm`
- `template_name`: `'shared/generic/generic_form.html'`
- `success_url`: `reverse_lazy('accounting:accounts')`
- `feature_code`: `'accounting.accounts'`
- `required_action`: `'edit_own'`

**متدها**:

#### `get_form_kwargs(self) -> Dict[str, Any]`

**توضیح**: `company_id` و `exclude_account_id` را به form kwargs اضافه می‌کند.

**مقدار بازگشتی**:
- `Dict[str, Any]`: form kwargs با `company_id` و `exclude_account_id` اضافه شده

**منطق**:
1. `super().get_form_kwargs()` را فراخوانی می‌کند
2. `active_company_id` را از session می‌گیرد
3. `company_id` را به kwargs اضافه می‌کند
4. اگر `self.object` وجود دارد:
   - `exclude_account_id` را به kwargs اضافه می‌کند (برای جلوگیری از circular references در parent_account)
5. kwargs را برمی‌گرداند

**نکته**: `exclude_account_id` برای جلوگیری از انتخاب حساب فعلی به عنوان parent account استفاده می‌شود.

#### `form_valid(self, form: AccountForm) -> HttpResponseRedirect`

**توضیح**: قبل از ذخیره، `edited_by` را تنظیم می‌کند و پیام موفقیت نمایش می‌دهد.

**پارامترهای ورودی**:
- `form`: فرم معتبر `AccountForm`

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
- `form_title`: `_('Edit Account')`
- `breadcrumbs`: لیست breadcrumb items (Dashboard → Accounting → Chart of Accounts)
- `cancel_url`: URL برای cancel (بازگشت به لیست)

**URL**: `/accounting/accounts/<int:pk>/edit/`

---

## AccountDeleteView

**Type**: `FeaturePermissionRequiredMixin`, `AccountingBaseView`, `DeleteView`

**Template**: `shared/generic/generic_confirm_delete.html`

**Success URL**: `accounting:accounts`

**Attributes**:
- `model`: `Account`
- `success_url`: `reverse_lazy('accounting:accounts')`
- `template_name`: `'shared/generic/generic_confirm_delete.html'`
- `feature_code`: `'accounting.accounts'`
- `required_action`: `'delete_own'`

**متدها**:

#### `delete(self, request: Any, *args: Any, **kwargs: Any) -> HttpResponseRedirect`

**توضیح**: حساب را حذف می‌کند با بررسی‌های امنیتی.

**پارامترهای ورودی**:
- `request`: HttpRequest
- `*args`: Additional arguments
- `**kwargs`: Additional keyword arguments

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به success_url

**منطق**:
1. `self.get_object()` را فراخوانی می‌کند تا object را بگیرد
2. بررسی می‌کند که آیا حساب system account است (`is_system_account`):
   - اگر باشد، پیام خطا نمایش می‌دهد و redirect می‌کند (بدون حذف)
3. بررسی می‌کند که آیا حساب دارای child accounts است (`child_accounts.exists()`):
   - اگر باشد، پیام خطا نمایش می‌دهد و redirect می‌کند (بدون حذف)
4. اگر همه بررسی‌ها پاس شدند:
   - پیام موفقیت را با `messages.success()` نمایش می‌دهد
   - `super().delete(request, *args, **kwargs)` را فراخوانی می‌کند

**نکته**: System accounts و حساب‌های دارای child accounts قابل حذف نیستند.

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`

**توضیح**: context variables را برای generic_confirm_delete template اضافه می‌کند.

**Context Variables اضافه شده**:
- `delete_title`: `_('Delete Account')`
- `confirmation_message`: `_('Do you really want to delete this account?')`
- `breadcrumbs`: لیست breadcrumb items (Dashboard → Accounting → Chart of Accounts → Delete)
- `object_details`: لیست جزئیات object برای نمایش در صفحه حذف
- `cancel_url`: URL برای cancel (بازگشت به لیست)

**Object Details**:
- Code: `self.object.account_code`
- Name: `self.object.account_name`
- Type: `self.object.get_account_type_display()`
- Level: `self.object.get_account_level_display()`

**URL**: `/accounting/accounts/<int:pk>/delete/`

---

## استفاده در پروژه

### URL Patterns
```python
path('accounts/', AccountListView.as_view(), name='accounts'),
path('accounts/create/', AccountCreateView.as_view(), name='account_create'),
path('accounts/<int:pk>/edit/', AccountUpdateView.as_view(), name='account_edit'),
path('accounts/<int:pk>/delete/', AccountDeleteView.as_view(), name='account_delete'),
```

### Permission Checking
تمام views از `FeaturePermissionRequiredMixin` استفاده می‌کنند و feature code `'accounting.accounts'` را دارند.

### Generic Templates
تمام views از تمپلیت‌های generic استفاده می‌کنند:
- List: `shared/generic/generic_list.html`
- Form: `shared/generic/generic_form.html`
- Delete: `shared/generic/generic_confirm_delete.html`

---

## نکات مهم

1. **Company Filtering**: تمام queryset ها به صورت خودکار بر اساس active company فیلتر می‌شوند
2. **Permission Filtering**: `filter_queryset_by_permissions` برای کنترل دسترسی استفاده می‌شود
3. **Search Support**: جستجو بر اساس `account_code`, `account_name`, و `account_name_en`
4. **Status Filter**: فیلتر بر اساس `is_enabled` (default: فقط فعال‌ها)
5. **Account Type Filter**: فیلتر اختیاری بر اساس `account_type`
6. **Account Level Filter**: فیلتر اختیاری بر اساس `account_level`
7. **Edit Lock**: `AccountUpdateView` از `EditLockProtectedMixin` استفاده می‌کند
8. **Circular Reference Prevention**: در `UpdateView`, حساب فعلی از parent choices حذف می‌شود
9. **Delete Protection**: System accounts و حساب‌های دارای child accounts قابل حذف نیستند
10. **Auto User Setting**: `created_by` و `edited_by` به صورت خودکار تنظیم می‌شوند
11. **Success Messages**: تمام عملیات پیام موفقیت نمایش می‌دهند

---

**Last Updated**: 2025-12-01

