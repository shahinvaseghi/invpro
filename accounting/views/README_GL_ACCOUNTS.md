# accounting/views/gl_accounts.py - GL Account Views (Complete Documentation)

**هدف**: CRUD views برای مدیریت حساب‌های کل (GL Accounts) در ماژول accounting

این فایل شامل **4 کلاس view**:
- `GLAccountListView`: فهرست حساب‌های کل
- `GLAccountCreateView`: ایجاد حساب کل جدید
- `GLAccountUpdateView`: ویرایش حساب کل
- `GLAccountDeleteView`: حذف حساب کل

---

## وابستگی‌ها

- `accounting.models`: `Account`
- `accounting.forms`: `GLAccountForm`
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

## GLAccountListView

**Type**: `FeaturePermissionRequiredMixin`, `AccountingBaseView`, `ListView`

**Template**: `shared/generic/generic_list.html`

**توضیح**: فهرست تمام حساب‌های کل (level 1) برای company فعال

**Attributes**:
- `model`: `Account`
- `template_name`: `'shared/generic/generic_list.html'`
- `context_object_name`: `'object_list'`
- `paginate_by`: `50`
- `feature_code`: `'accounting.accounts.gl'`

**متدها**:

#### `get_queryset(self) -> QuerySet`

**توضیح**: queryset را بر اساس active company، permissions، search، status و account_type filter می‌کند.

**مقدار بازگشتی**:
- `QuerySet`: queryset فیلتر شده

**منطق**:
1. فیلتر کردن بر اساس `account_level=1` (حساب کل)
2. فراخوانی `filter_queryset_by_permissions()` با feature code `'accounting.accounts.gl'`
3. دریافت `search` از GET parameters
4. اگر `search` وجود دارد:
   - فیلتر بر اساس `account_code`, `account_name`, یا `account_name_en` (case-insensitive)
5. دریافت `status` از GET parameters
6. اگر `status` در `('0', '1')` باشد:
   - فیلتر بر اساس `is_enabled`
7. در غیر این صورت (default):
   - فقط حساب‌های فعال (`is_enabled=1`) را نمایش می‌دهد
8. دریافت `account_type` از GET parameters
9. اگر `account_type` وجود دارد:
   - فیلتر بر اساس `account_type`
10. مرتب‌سازی بر اساس `account_code`
11. برگرداندن queryset

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`

**توضیح**: context variables را برای generic_list template اضافه می‌کند.

**Context Variables اضافه شده**:
- `page_title`: `_('تعریف حساب کل')`
- `breadcrumbs`: لیست breadcrumb items (Dashboard → Accounting → تعریف حساب کل)
- `create_url`: URL برای ایجاد حساب کل جدید
- `create_button_text`: `_('افزودن حساب کل')`
- `show_filters`: `True`
- `status_filter`: `True`
- `search_placeholder`: `_('جستجو بر اساس کد یا نام')`
- `clear_filter_url`: URL برای پاک کردن فیلترها
- `print_enabled`: `True`
- `show_actions`: `True`
- `edit_url_name`: `'accounting:gl_account_edit'`
- `delete_url_name`: `'accounting:gl_account_delete'`
- `table_headers`: لیست header های جدول (کد کل، نام کل، نوع حساب، طرف تراز، مانده جاری، وضعیت)
- `empty_state_title`: `_('هیچ حساب کلی یافت نشد')`
- `empty_state_message`: `_('با افزودن اولین حساب کل شروع کنید.')`
- `empty_state_icon`: `'📊'`

**URL**: `/accounting/accounts/gl/`

---

## GLAccountCreateView

**Type**: `FeaturePermissionRequiredMixin`, `AccountingBaseView`, `CreateView`

**Template**: `shared/generic/generic_form.html`

**Form**: `GLAccountForm`

**Success URL**: `accounting:gl_accounts`

**Attributes**:
- `model`: `Account`
- `form_class`: `GLAccountForm`
- `template_name`: `'shared/generic/generic_form.html'`
- `success_url`: `reverse_lazy('accounting:gl_accounts')`
- `feature_code`: `'accounting.accounts.gl'`
- `required_action`: `'create'`

**متدها**:

#### `get_form_kwargs(self) -> Dict[str, Any]`

**توضیح**: `company_id` را به form kwargs اضافه می‌کند.

**مقدار بازگشتی**:
- `Dict[str, Any]`: form kwargs با `company_id` اضافه شده

**منطق**:
1. فراخوانی `super().get_form_kwargs()`
2. دریافت `active_company_id` از session
3. اضافه کردن `company_id` به kwargs
4. برگرداندن kwargs

#### `form_valid(self, form: GLAccountForm) -> HttpResponseRedirect`

**توضیح**: قبل از ذخیره، `created_by` و `account_level` را تنظیم می‌کند و پیام موفقیت نمایش می‌دهد.

**پارامترهای ورودی**:
- `form`: فرم معتبر `GLAccountForm`

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به success_url

**منطق**:
1. تنظیم `form.instance.created_by` به `self.request.user`
2. تنظیم `form.instance.account_level = 1` (حساب کل)
3. نمایش پیام موفقیت با `messages.success()`
4. فراخوانی `super().form_valid(form)`

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`

**توضیح**: context variables را برای generic_form template اضافه می‌کند.

**Context Variables اضافه شده**:
- `form_title`: `_('افزودن حساب کل')`
- `breadcrumbs`: لیست breadcrumb items (Dashboard → Accounting → تعریف حساب کل → افزودن)
- `cancel_url`: URL برای لغو (بازگشت به لیست)

**URL**: `/accounting/accounts/gl/create/`

---

## GLAccountUpdateView

**Type**: `EditLockProtectedMixin`, `FeaturePermissionRequiredMixin`, `AccountingBaseView`, `UpdateView`

**Template**: `shared/generic/generic_form.html`

**Form**: `GLAccountForm`

**Success URL**: `accounting:gl_accounts`

**Attributes**:
- `model`: `Account`
- `form_class`: `GLAccountForm`
- `template_name`: `'shared/generic/generic_form.html'`
- `success_url`: `reverse_lazy('accounting:gl_accounts')`
- `feature_code`: `'accounting.accounts.gl'`
- `required_action`: `'edit_own'`

**متدها**:

#### `get_queryset(self) -> QuerySet`

**توضیح**: فقط حساب‌های کل (level 1) را برای ویرایش مجاز می‌کند.

**مقدار بازگشتی**:
- `QuerySet`: queryset فیلتر شده بر اساس `account_level=1`

**منطق**:
1. فراخوانی `super().get_queryset()`
2. فیلتر کردن بر اساس `account_level=1`
3. برگرداندن queryset

#### `get_form_kwargs(self) -> Dict[str, Any]`

**توضیح**: `company_id` را به form kwargs اضافه می‌کند.

**مقدار بازگشتی**:
- `Dict[str, Any]`: form kwargs با `company_id` اضافه شده

**منطق**:
1. فراخوانی `super().get_form_kwargs()`
2. دریافت `active_company_id` از session
3. اضافه کردن `company_id` به kwargs
4. برگرداندن kwargs

#### `form_valid(self, form: GLAccountForm) -> HttpResponseRedirect`

**توضیح**: قبل از ذخیره، `edited_by` را تنظیم می‌کند و پیام موفقیت نمایش می‌دهد.

**پارامترهای ورودی**:
- `form`: فرم معتبر `GLAccountForm`

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به success_url

**منطق**:
1. تنظیم `form.instance.edited_by` به `self.request.user`
2. نمایش پیام موفقیت با `messages.success()`
3. فراخوانی `super().form_valid(form)`

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`

**توضیح**: context variables را برای generic_form template اضافه می‌کند.

**Context Variables اضافه شده**:
- `form_title`: `_('ویرایش حساب کل')`
- `breadcrumbs`: لیست breadcrumb items (Dashboard → Accounting → تعریف حساب کل → ویرایش)
- `cancel_url`: URL برای لغو (بازگشت به لیست)

**URL**: `/accounting/accounts/gl/<id>/edit/`

---

## GLAccountDeleteView

**Type**: `FeaturePermissionRequiredMixin`, `AccountingBaseView`, `DeleteView`

**Template**: `shared/generic/generic_confirm_delete.html`

**Success URL**: `accounting:gl_accounts`

**Attributes**:
- `model`: `Account`
- `success_url`: `reverse_lazy('accounting:gl_accounts')`
- `template_name`: `'shared/generic/generic_confirm_delete.html'`
- `feature_code`: `'accounting.accounts.gl'`
- `required_action`: `'delete_own'`

**متدها**:

#### `get_queryset(self) -> QuerySet`

**توضیح**: فقط حساب‌های کل (level 1) را برای حذف مجاز می‌کند.

**مقدار بازگشتی**:
- `QuerySet`: queryset فیلتر شده بر اساس `account_level=1`

**منطق**:
1. فراخوانی `super().get_queryset()`
2. فیلتر کردن بر اساس `account_level=1`
3. برگرداندن queryset

#### `delete(self, request: Any, *args: Any, **kwargs: Any) -> HttpResponseRedirect`

**توضیح**: حذف حساب کل با بررسی محدودیت‌ها

**پارامترهای ورودی**:
- `request`: درخواست HTTP
- `*args`: Positional arguments
- `**kwargs`: Keyword arguments

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به success_url

**منطق**:
1. دریافت object از `self.get_object()`
2. بررسی اینکه حساب سیستم است (`is_system_account`):
   - اگر باشد: نمایش پیام خطا و redirect (بدون حذف)
3. بررسی اینکه حساب دارای حساب معین (child accounts) است:
   - اگر باشد: نمایش پیام خطا و redirect (بدون حذف)
4. نمایش پیام موفقیت
5. فراخوانی `super().delete()` برای حذف

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`

**توضیح**: context variables را برای generic_confirm_delete template اضافه می‌کند.

**Context Variables اضافه شده**:
- `delete_title`: `_('حذف حساب کل')`
- `confirmation_message`: `_('آیا مطمئن هستید که می‌خواهید این حساب کل را حذف کنید؟')`
- `breadcrumbs`: لیست breadcrumb items (Dashboard → Accounting → تعریف حساب کل → حذف)
- `object_details`: لیست جزئیات object برای نمایش (کد کل، نام کل، نوع حساب)
- `cancel_url`: URL برای لغو (بازگشت به لیست)

**URL**: `/accounting/accounts/gl/<id>/delete/`

---

## استفاده در پروژه

### Import Views

```python
from accounting.views.gl_accounts import (
    GLAccountListView,
    GLAccountCreateView,
    GLAccountUpdateView,
    GLAccountDeleteView,
)
```

### URL Patterns

```python
path('accounts/gl/', GLAccountListView.as_view(), name='gl_accounts'),
path('accounts/gl/create/', GLAccountCreateView.as_view(), name='gl_account_create'),
path('accounts/gl/<int:pk>/edit/', GLAccountUpdateView.as_view(), name='gl_account_edit'),
path('accounts/gl/<int:pk>/delete/', GLAccountDeleteView.as_view(), name='gl_account_delete'),
```

---

## نکات مهم

1. **Account Level**: همه views فقط با حساب‌های کل (level 1) کار می‌کنند
2. **Permission Filtering**: تمام views از `filter_queryset_by_permissions()` استفاده می‌کنند
3. **Company Scoping**: تمام queryset ها بر اساس `active_company_id` فیلتر می‌شوند
4. **Edit Lock**: `GLAccountUpdateView` از `EditLockProtectedMixin` استفاده می‌کند
5. **Delete Protection**: `GLAccountDeleteView` حساب‌های سیستم و حساب‌های دارای child accounts را محافظت می‌کند

---

**Last Updated**: 2025-12-02

