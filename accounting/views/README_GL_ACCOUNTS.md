# accounting/views/gl_accounts.py - GL Account Views (Complete Documentation)

**هدف**: CRUD views برای مدیریت حساب‌های کل (GL Accounts) در ماژول accounting

این فایل شامل **5 کلاس view**:
- `GLAccountListView`: فهرست حساب‌های کل
- `GLAccountCreateView`: ایجاد حساب کل جدید
- `GLAccountUpdateView`: ویرایش حساب کل
- `GLAccountDetailView`: مشاهده جزئیات حساب کل (read-only)
- `GLAccountDeleteView`: حذف حساب کل

---

## وابستگی‌ها

- `accounting.models`: `Account`
- `accounting.forms`: `GLAccountForm`
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

## GLAccountListView

**Type**: `BaseListView`

**Template**: `shared/generic/generic_list.html`

**توضیح**: فهرست تمام حساب‌های کل (level 1) برای company فعال

**Attributes**:
- `model`: `Account`
- `template_name`: `'shared/generic/generic_list.html'`
- `context_object_name`: `'object_list'`
- `paginate_by`: `50`
- `feature_code`: `'accounting.accounts.gl'`
- `required_action`: `'view_all'`
- `active_module`: `'accounting'`
- `default_order_by`: `['account_code']`
- `default_status_filter`: `True`

**متدها**:

#### `get_base_queryset(self) -> QuerySet`

**توضیح**: queryset را بر اساس account_level=1 و permissions filter می‌کند.

**مقدار بازگشتی**:
- `QuerySet`: queryset فیلتر شده

**منطق**:
1. فیلتر کردن بر اساس `account_level=1`: `Account.objects.filter(account_level=1)`
2. ایجاد instance از `AccountingBaseView` و تنظیم `request`
3. فراخوانی `filter_queryset_by_permissions(queryset, self.feature_code)` برای permission filtering
4. return queryset

#### `get_search_fields(self) -> list`

**توضیح**: لیست fields برای search را برمی‌گرداند.

**مقدار بازگشتی**:
- `list`: `['account_code', 'account_name', 'account_name_en']`

#### `get_queryset(self) -> QuerySet`

**توضیح**: queryset را بر اساس account_type filter می‌کند.

**مقدار بازگشتی**:
- `QuerySet`: queryset فیلتر شده

**منطق**:
1. فراخوانی `super().get_queryset()` (که search و status filtering را انجام می‌دهد)
2. دریافت `account_type` از GET parameters
3. اگر `account_type` موجود باشد:
   - `queryset = queryset.filter(account_type=account_type)`
4. return queryset

#### `get_page_title(self) -> str`

**توضیح**: عنوان صفحه را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `_('تعریف حساب کل')`

#### `get_breadcrumbs(self) -> list`

**توضیح**: لیست breadcrumbs را برمی‌گرداند.

**مقدار بازگشتی**:
- `list`: `[{'label': _('Dashboard'), 'url': reverse('ui:dashboard')}, {'label': _('Accounting'), 'url': reverse('accounting:general_ledger')}, {'label': _('تعریف حساب کل'), 'url': None}]`

#### `get_create_url(self) -> str`

**توضیح**: URL برای ایجاد حساب کل جدید را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `reverse('accounting:gl_account_create')`

#### `get_create_button_text(self) -> str`

**توضیح**: متن دکمه ایجاد را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `_('افزودن حساب کل')`

#### `get_detail_url_name(self) -> str`

**توضیح**: نام URL برای detail view را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `'accounting:gl_account_detail'`

#### `get_edit_url_name(self) -> str`

**توضیح**: نام URL برای edit view را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `'accounting:gl_account_edit'`

#### `get_delete_url_name(self) -> str`

**توضیح**: نام URL برای delete view را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `'accounting:gl_account_delete'`

#### `get_empty_state_title(self) -> str`

**توضیح**: عنوان empty state را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `_('هیچ حساب کلی یافت نشد')`

#### `get_empty_state_message(self) -> str`

**توضیح**: پیام empty state را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `_('با افزودن اولین حساب کل شروع کنید.')`

#### `get_empty_state_icon(self) -> str`

**توضیح**: آیکون empty state را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `'📊'`

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

**Type**: `BaseCreateView`

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
- `active_module`: `'accounting'`
- `success_message`: `_('حساب کل با موفقیت ایجاد شد.')`

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

**توضیح**: قبل از ذخیره، `created_by` و `account_level` را تنظیم می‌کند.

**پارامترهای ورودی**:
- `form`: فرم معتبر `GLAccountForm`

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به success_url

**منطق**:
1. تنظیم `form.instance.created_by` به `self.request.user`
2. تنظیم `form.instance.account_level = 1` (حساب کل)
3. فراخوانی `super().form_valid(form)` (که پیام موفقیت را نمایش می‌دهد)

#### `get_breadcrumbs(self) -> list`

**توضیح**: لیست breadcrumbs را برمی‌گرداند.

**مقدار بازگشتی**:
- `list`: `[{'label': _('Dashboard'), 'url': reverse('ui:dashboard')}, {'label': _('Accounting'), 'url': reverse('accounting:general_ledger')}, {'label': _('تعریف حساب کل'), 'url': reverse('accounting:gl_accounts')}, {'label': _('افزودن'), 'url': None}]`

#### `get_cancel_url(self) -> str`

**توضیح**: URL برای cancel را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `reverse('accounting:gl_accounts')`

#### `get_form_title(self) -> str`

**توضیح**: عنوان فرم را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `_('افزودن حساب کل')`

**URL**: `/accounting/accounts/gl/create/`

---

## GLAccountUpdateView

**Type**: `BaseUpdateView`, `EditLockProtectedMixin`

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
- `active_module`: `'accounting'`
- `success_message`: `_('حساب کل با موفقیت به‌روزرسانی شد.')`

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

**توضیح**: قبل از ذخیره، `edited_by` را تنظیم می‌کند.

**پارامترهای ورودی**:
- `form`: فرم معتبر `GLAccountForm`

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به success_url

**منطق**:
1. تنظیم `form.instance.edited_by` به `self.request.user`
2. فراخوانی `super().form_valid(form)` (که پیام موفقیت را نمایش می‌دهد)

**نکته**: این view از `EditLockProtectedMixin` استفاده می‌کند که از concurrent editing جلوگیری می‌کند.

#### `get_breadcrumbs(self) -> list`

**توضیح**: لیست breadcrumbs را برمی‌گرداند.

**مقدار بازگشتی**:
- `list`: `[{'label': _('Dashboard'), 'url': reverse('ui:dashboard')}, {'label': _('Accounting'), 'url': reverse('accounting:general_ledger')}, {'label': _('تعریف حساب کل'), 'url': reverse('accounting:gl_accounts')}, {'label': _('ویرایش'), 'url': None}]`

#### `get_cancel_url(self) -> str`

**توضیح**: URL برای cancel را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `reverse('accounting:gl_accounts')`

#### `get_form_title(self) -> str`

**توضیح**: عنوان فرم را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `_('ویرایش حساب کل')`

**URL**: `/accounting/accounts/gl/<int:pk>/edit/`

---

## GLAccountDetailView

**Type**: `BaseDetailView`

**Template**: `shared/generic/generic_detail.html`

**توضیح**: مشاهده جزئیات حساب کل (read-only)

**Attributes**:
- `model`: `Account`
- `template_name`: `'shared/generic/generic_detail.html'`
- `context_object_name`: `'object'`
- `feature_code`: `'accounting.accounts.gl'`
- `required_action`: `'view_own'`
- `active_module`: `'accounting'`

**متدها**:

#### `get_queryset(self) -> QuerySet`

**توضیح**: queryset را بر اساس account_level=1 و permissions filter می‌کند و optimize می‌کند.

**مقدار بازگشتی**:
- `QuerySet`: queryset فیلتر شده با `select_related` برای `created_by`, `edited_by` و `prefetch_related` برای `child_accounts`

**منطق**:
1. فیلتر کردن بر اساس `account_level=1`: `Account.objects.filter(account_level=1)`
2. ایجاد instance از `AccountingBaseView` و تنظیم `request`
3. فراخوانی `filter_queryset_by_permissions(queryset, self.feature_code)`
4. `select_related('created_by', 'edited_by')` برای optimization
5. `prefetch_related('child_accounts')` برای child accounts (sub accounts)
6. return queryset

#### `get_page_title(self) -> str`

**توضیح**: عنوان صفحه را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `_('View GL Account')`

#### `get_context_data(self, **kwargs) -> Dict[str, Any]`

**توضیح**: context variables را برای generic_detail template اضافه می‌کند.

**Context Variables اضافه شده**:
- `detail_title`: `_('View GL Account')`
- `info_banner`: لیست اطلاعات اصلی (Account Code, Status, Current Balance)
- `detail_sections`: لیست sections با fields (Basic Information, Child Accounts)
- `list_url`: URL برای بازگشت به لیست
- `edit_url`: URL برای ویرایش

**منطق**:
1. `info_banner` شامل:
   - `{'label': _('Account Code'), 'value': account.account_code, 'type': 'code'}`
   - `{'label': _('Status'), 'value': account.is_enabled, 'type': 'badge'}`
   - اگر `account.current_balance`: `{'label': _('Current Balance'), 'value': f"{account.current_balance:.2f}"}`
2. `detail_sections` شامل:
   - Basic Information: `account_name`, `account_name_en` (اگر موجود باشد), `account_type`, `normal_balance`, `description` (اگر موجود باشد)
   - Child Accounts: اگر `account.child_accounts.exists()` باشد، نمایش child accounts (sub accounts) به صورت HTML با format: `<code>{code}</code> - {name}` و title: `_('Child Accounts') + ' (' + _('Sub Accounts') + ')'`

#### `get_list_url(self) -> str`

**توضیح**: URL برای بازگشت به لیست را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `reverse_lazy('accounting:gl_accounts')`

#### `get_edit_url(self) -> str`

**توضیح**: URL برای ویرایش را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `reverse_lazy('accounting:gl_account_edit', kwargs={'pk': self.object.pk})`

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

**URL**: `/accounting/accounts/gl/<int:pk>/`

---

## GLAccountDeleteView

**Type**: `BaseDeleteView`

**Template**: `shared/generic/generic_confirm_delete.html`

**Success URL**: `accounting:gl_accounts`

**Attributes**:
- `model`: `Account`
- `success_url`: `reverse_lazy('accounting:gl_accounts')`
- `template_name`: `'shared/generic/generic_confirm_delete.html'`
- `feature_code`: `'accounting.accounts.gl'`
- `required_action`: `'delete_own'`
- `active_module`: `'accounting'`
- `success_message`: `_('حساب کل با موفقیت حذف شد.')`

**متدها**:

#### `get_queryset(self) -> QuerySet`

**توضیح**: فقط حساب‌های کل (level 1) را برای حذف مجاز می‌کند.

**مقدار بازگشتی**:
- `QuerySet`: queryset فیلتر شده بر اساس `account_level=1`

**منطق**:
1. فراخوانی `super().get_queryset()`
2. فیلتر کردن بر اساس `account_level=1`
3. return queryset

#### `validate_deletion(self) -> tuple[bool, Optional[str]]`

**توضیح**: بررسی می‌کند که آیا حساب کل قابل حذف است یا نه.

**مقدار بازگشتی**:
- `tuple[bool, Optional[str]]`: `(True, None)` اگر قابل حذف باشد، `(False, error_message)` در غیر این صورت

**منطق**:
1. دریافت object با `self.get_object()`
2. بررسی `is_system_account`:
   - اگر `obj.is_system_account` باشد: return `(False, _('حساب‌های سیستمی قابل حذف نیستند.'))`
3. بررسی child accounts (معین):
   - اگر `obj.child_accounts.exists()` باشد: return `(False, _('نمی‌توان حساب کلی که دارای حساب معین است را حذف کرد.'))`
4. return `(True, None)`

**نکته**: System accounts و حساب‌های کل دارای child accounts (معین) قابل حذف نیستند. BaseDeleteView از این متد برای validation استفاده می‌کند.

#### `get_delete_title(self) -> str`

**توضیح**: عنوان صفحه حذف را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `_('حذف حساب کل')`

#### `get_confirmation_message(self) -> str`

**توضیح**: پیام تایید حذف را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `_('آیا مطمئن هستید که می‌خواهید این حساب کل را حذف کنید؟')`

#### `get_object_details(self) -> list`

**توضیح**: لیست جزئیات object برای نمایش در صفحه حذف را برمی‌گرداند.

**مقدار بازگشتی**:
- `list`: `[{'label': _('کد کل'), 'value': self.object.account_code, 'type': 'code'}, {'label': _('نام کل'), 'value': self.object.account_name}, {'label': _('نوع حساب'), 'value': self.object.get_account_type_display()}]`

#### `get_breadcrumbs(self) -> list`

**توضیح**: لیست breadcrumbs را برمی‌گرداند.

**مقدار بازگشتی**:
- `list`: `[{'label': _('Dashboard'), 'url': reverse('ui:dashboard')}, {'label': _('Accounting'), 'url': reverse('accounting:general_ledger')}, {'label': _('تعریف حساب کل'), 'url': reverse('accounting:gl_accounts')}, {'label': _('حذف'), 'url': None}]`

**URL**: `/accounting/accounts/gl/<id>/delete/`

---

## استفاده در پروژه

### URL Patterns
```python
path('accounts/gl/', GLAccountListView.as_view(), name='gl_accounts'),
path('accounts/gl/create/', GLAccountCreateView.as_view(), name='gl_account_create'),
path('accounts/gl/<int:pk>/', GLAccountDetailView.as_view(), name='gl_account_detail'),
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

