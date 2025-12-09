# accounting/views/accounts.py - Account Views (Complete Documentation)

**هدف**: CRUD views برای مدیریت حساب‌ها (Chart of Accounts) در ماژول accounting

این فایل شامل **5 کلاس view**:
- `AccountListView`: فهرست حساب‌ها
- `AccountCreateView`: ایجاد حساب جدید
- `AccountUpdateView`: ویرایش حساب
- `AccountDetailView`: مشاهده جزئیات حساب (read-only)
- `AccountDeleteView`: حذف حساب

---

## وابستگی‌ها

- `accounting.models`: `Account`
- `accounting.forms`: `AccountForm`
- `accounting.views.base`: `AccountingBaseView`
- `shared.mixins`: `FeaturePermissionRequiredMixin`
- `shared.views.base`: `BaseListView`, `BaseCreateView`, `BaseUpdateView`, `BaseDetailView`, `BaseDeleteView`, `EditLockProtectedMixin`
- `django.contrib`: `messages`
- `django.db.models`: `Q`
- `django.http`: `HttpResponseRedirect`
- `django.urls`: `reverse`, `reverse_lazy`
- `django.utils.translation`: `gettext_lazy`
- `typing`: `Any`, `Dict`

---

## AccountListView

**Type**: `BaseListView`

**Template**: `shared/generic/generic_list.html`

**توضیح**: فهرست تمام حساب‌ها برای company فعال

**Attributes**:
- `model`: `Account`
- `template_name`: `'shared/generic/generic_list.html'`
- `context_object_name`: `'object_list'`
- `paginate_by`: `50`
- `feature_code`: `'accounting.accounts'`
- `required_action`: `'view_all'`
- `active_module`: `'accounting'`
- `default_order_by`: `['account_code']`
- `default_status_filter`: `True`

**متدها**:

#### `get_base_queryset(self) -> QuerySet`

**توضیح**: queryset را بر اساس active company و permissions filter می‌کند.

**مقدار بازگشتی**:
- `QuerySet`: queryset فیلتر شده

**منطق**:
1. فراخوانی `super().get_base_queryset()` (company filtering از BaseListView)
2. ایجاد instance از `AccountingBaseView` و تنظیم `request`
3. فراخوانی `filter_queryset_by_permissions(queryset, self.feature_code)` برای permission filtering
4. return queryset

#### `get_search_fields(self) -> list`

**توضیح**: لیست fields برای search را برمی‌گرداند.

**مقدار بازگشتی**:
- `list`: `['account_code', 'account_name', 'account_name_en']`

#### `get_queryset(self) -> QuerySet`

**توضیح**: queryset را بر اساس account_type و account_level filter می‌کند.

**مقدار بازگشتی**:
- `QuerySet`: queryset فیلتر شده

**منطق**:
1. فراخوانی `super().get_queryset()` (که search و status filtering را انجام می‌دهد)
2. دریافت `account_type` از GET parameters
3. اگر `account_type` موجود باشد:
   - `queryset = queryset.filter(account_type=account_type)`
4. دریافت `account_level` از GET parameters
5. اگر `account_level` موجود باشد:
   - `queryset = queryset.filter(account_level=int(account_level))`
6. return queryset

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

**Type**: `BaseCreateView`

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
- `active_module`: `'accounting'`
- `success_message`: `_('Account created successfully.')`

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

**توضیح**: قبل از ذخیره، `created_by` را تنظیم می‌کند.

**پارامترهای ورودی**:
- `form`: فرم معتبر `AccountForm`

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به success_url

**منطق**:
1. `form.instance.created_by` را به `self.request.user` تنظیم می‌کند
2. `super().form_valid(form)` را فراخوانی می‌کند (که پیام موفقیت را نمایش می‌دهد)

#### `get_breadcrumbs(self) -> list`

**توضیح**: لیست breadcrumbs را برمی‌گرداند.

**مقدار بازگشتی**:
- `list`: `[{'label': _('Dashboard'), 'url': reverse('ui:dashboard')}, {'label': _('Accounting'), 'url': reverse('accounting:dashboard')}, {'label': _('Chart of Accounts'), 'url': reverse('accounting:accounts')}, {'label': _('Create'), 'url': None}]`

#### `get_cancel_url(self) -> str`

**توضیح**: URL برای cancel را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `reverse('accounting:accounts')`

#### `get_form_title(self) -> str`

**توضیح**: عنوان فرم را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `_('Create Account')`

**URL**: `/accounting/accounts/create/`

---

## AccountUpdateView

**Type**: `BaseUpdateView`, `EditLockProtectedMixin`

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
- `active_module`: `'accounting'`
- `success_message`: `_('Account updated successfully.')`

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

**توضیح**: قبل از ذخیره، `edited_by` را تنظیم می‌کند.

**پارامترهای ورودی**:
- `form`: فرم معتبر `AccountForm`

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به success_url

**منطق**:
1. `form.instance.edited_by` را به `self.request.user` تنظیم می‌کند
2. `super().form_valid(form)` را فراخوانی می‌کند (که پیام موفقیت را نمایش می‌دهد)

**نکته**: این view از `EditLockProtectedMixin` استفاده می‌کند که از concurrent editing جلوگیری می‌کند.

#### `get_breadcrumbs(self) -> list`

**توضیح**: لیست breadcrumbs را برمی‌گرداند.

**مقدار بازگشتی**:
- `list`: `[{'label': _('Dashboard'), 'url': reverse('ui:dashboard')}, {'label': _('Accounting'), 'url': reverse('accounting:dashboard')}, {'label': _('Chart of Accounts'), 'url': reverse('accounting:accounts')}, {'label': _('Edit'), 'url': None}]`

#### `get_cancel_url(self) -> str`

**توضیح**: URL برای cancel را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `reverse('accounting:accounts')`

#### `get_form_title(self) -> str`

**توضیح**: عنوان فرم را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `_('Edit Account')`

**URL**: `/accounting/accounts/<int:pk>/edit/`

---

## AccountDetailView

**Type**: `BaseDetailView`

**Template**: `shared/generic/generic_detail.html`

**توضیح**: مشاهده جزئیات حساب (read-only)

**Attributes**:
- `model`: `Account`
- `template_name`: `'shared/generic/generic_detail.html'`
- `context_object_name`: `'object'`
- `feature_code`: `'accounting.accounts'`
- `required_action`: `'view_own'`
- `active_module`: `'accounting'`

**متدها**:

#### `get_queryset(self) -> QuerySet`

**توضیح**: queryset را بر اساس active company و permissions filter می‌کند و optimize می‌کند.

**مقدار بازگشتی**:
- `QuerySet`: queryset فیلتر شده با `select_related` برای `parent_account`, `created_by`, `edited_by` و `prefetch_related` برای `child_accounts`

**منطق**:
1. فراخوانی `super().get_queryset()`
2. ایجاد instance از `AccountingBaseView` و تنظیم `request`
3. فراخوانی `filter_queryset_by_permissions(queryset, self.feature_code)`
4. `select_related('parent_account', 'created_by', 'edited_by')` برای optimization
5. `prefetch_related('child_accounts')` برای child accounts
6. return queryset

#### `get_page_title(self) -> str`

**توضیح**: عنوان صفحه را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `_('View Account')`

#### `get_context_data(self, **kwargs) -> Dict[str, Any]`

**توضیح**: context variables را برای generic_detail template اضافه می‌کند.

**Context Variables اضافه شده**:
- `detail_title`: `_('View Account')`
- `info_banner`: لیست اطلاعات اصلی (Account Code, Account Level, Status, Current Balance)
- `detail_sections`: لیست sections با fields (Basic Information, Child Accounts)
- `list_url`: URL برای بازگشت به لیست
- `edit_url`: URL برای ویرایش

**منطق**:
1. `info_banner` شامل:
   - `{'label': _('Account Code'), 'value': account.account_code, 'type': 'code'}`
   - `{'label': _('Account Level'), 'value': str(account.account_level)}`
   - `{'label': _('Status'), 'value': account.is_enabled, 'type': 'badge'}`
   - اگر `account.current_balance`: `{'label': _('Current Balance'), 'value': f"{account.current_balance:.2f}"}`
2. `detail_sections` شامل:
   - Basic Information: `account_name`, `account_name_en` (اگر موجود باشد), `account_type`, `normal_balance`, `parent_account` (اگر موجود باشد), `description` (اگر موجود باشد)
   - Child Accounts: اگر `account.child_accounts.exists()` باشد، نمایش child accounts به صورت HTML با format: `<code>{code}</code> - {name} ({Level} {level})`

#### `get_list_url(self) -> str`

**توضیح**: URL برای بازگشت به لیست را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `reverse_lazy('accounting:accounts')`

#### `get_edit_url(self) -> str`

**توضیح**: URL برای ویرایش را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `reverse_lazy('accounting:account_edit', kwargs={'pk': self.object.pk})`

#### `can_edit_object(self, obj=None, feature_code=None) -> bool`

**توضیح**: بررسی می‌کند که آیا object قابل ویرایش است یا نه.

**پارامترهای ورودی**:
- `obj` (optional): Object برای بررسی (default: `self.object`)
- `feature_code` (optional): Feature code (استفاده نمی‌شود)

**مقدار بازگشتی**:
- `bool`: `True` اگر object قفل نباشد، `False` در غیر این صورت

**منطق**:
1. اگر `obj` موجود نباشد، از `self.object` استفاده می‌کند
2. اگر object دارای `is_locked` attribute باشد:
   - return `not bool(obj.is_locked)`
3. در غیر این صورت: return `True`

**URL**: `/accounting/accounts/<int:pk>/`

---

## AccountDeleteView

**Type**: `BaseDeleteView`

**Template**: `shared/generic/generic_confirm_delete.html`

**Success URL**: `accounting:accounts`

**Attributes**:
- `model`: `Account`
- `success_url`: `reverse_lazy('accounting:accounts')`
- `template_name`: `'shared/generic/generic_confirm_delete.html'`
- `feature_code`: `'accounting.accounts'`
- `required_action`: `'delete_own'`
- `active_module`: `'accounting'`
- `success_message`: `_('Account deleted successfully.')`

**متدها**:

#### `validate_deletion(self) -> tuple[bool, Optional[str]]`

**توضیح**: بررسی می‌کند که آیا حساب قابل حذف است یا نه.

**مقدار بازگشتی**:
- `tuple[bool, Optional[str]]`: `(True, None)` اگر قابل حذف باشد، `(False, error_message)` در غیر این صورت

**منطق**:
1. دریافت object با `self.get_object()`
2. بررسی `is_system_account`:
   - اگر `obj.is_system_account` باشد: return `(False, _('System accounts cannot be deleted.'))`
3. بررسی child accounts:
   - اگر `obj.child_accounts.exists()` باشد: return `(False, _('Cannot delete account with child accounts.'))`
4. return `(True, None)`

**نکته**: System accounts و حساب‌های دارای child accounts قابل حذف نیستند. BaseDeleteView از این متد برای validation استفاده می‌کند.

#### `get_delete_title(self) -> str`

**توضیح**: عنوان صفحه حذف را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `_('Delete Account')`

#### `get_confirmation_message(self) -> str`

**توضیح**: پیام تایید حذف را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `_('Do you really want to delete this account?')`

#### `get_object_details(self) -> list`

**توضیح**: لیست جزئیات object برای نمایش در صفحه حذف را برمی‌گرداند.

**مقدار بازگشتی**:
- `list`: `[{'label': _('Code'), 'value': self.object.account_code, 'type': 'code'}, {'label': _('Name'), 'value': self.object.account_name}, {'label': _('Type'), 'value': self.object.get_account_type_display()}, {'label': _('Level'), 'value': self.object.get_account_level_display()}]`

#### `get_breadcrumbs(self) -> list`

**توضیح**: لیست breadcrumbs را برمی‌گرداند.

**مقدار بازگشتی**:
- `list`: `[{'label': _('Dashboard'), 'url': reverse('ui:dashboard')}, {'label': _('Accounting'), 'url': reverse('accounting:dashboard')}, {'label': _('Chart of Accounts'), 'url': reverse('accounting:accounts')}, {'label': _('Delete'), 'url': None}]`

**URL**: `/accounting/accounts/<int:pk>/delete/`

---

## استفاده در پروژه

### URL Patterns
```python
path('accounts/', AccountListView.as_view(), name='accounts'),
path('accounts/create/', AccountCreateView.as_view(), name='account_create'),
path('accounts/<int:pk>/', AccountDetailView.as_view(), name='account_detail'),
path('accounts/<int:pk>/edit/', AccountUpdateView.as_view(), name='account_edit'),
path('accounts/<int:pk>/delete/', AccountDeleteView.as_view(), name='account_delete'),
```

### Permission Checking
تمام views از `FeaturePermissionRequiredMixin` استفاده می‌کنند و feature code `'accounting.accounts'` را دارند.

### Generic Templates
تمام views از تمپلیت‌های generic استفاده می‌کنند:
- List: `shared/generic/generic_list.html`
- Form: `shared/generic/generic_form.html`
- Detail: `shared/generic/generic_detail.html`
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

