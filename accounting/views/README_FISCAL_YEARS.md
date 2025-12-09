# accounting/views/fiscal_years.py - Fiscal Year Views (Complete Documentation)

**هدف**: CRUD views برای مدیریت سال‌های مالی در ماژول accounting

این فایل شامل **5 کلاس view**:
- `FiscalYearListView`: فهرست سال‌های مالی
- `FiscalYearCreateView`: ایجاد سال مالی جدید
- `FiscalYearUpdateView`: ویرایش سال مالی
- `FiscalYearDetailView`: مشاهده جزئیات سال مالی (read-only)
- `FiscalYearDeleteView`: حذف سال مالی

---

## وابستگی‌ها

- `accounting.models`: `FiscalYear`
- `accounting.forms`: `FiscalYearForm`
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

## FiscalYearListView

**Type**: `BaseListView`

**Template**: `shared/generic/generic_list.html`

**توضیح**: فهرست تمام سال‌های مالی برای company فعال

**Attributes**:
- `model`: `FiscalYear`
- `template_name`: `'shared/generic/generic_list.html'`
- `context_object_name`: `'object_list'`
- `paginate_by`: `50`
- `feature_code`: `'accounting.fiscal_years'`
- `required_action`: `'view_all'`
- `active_module`: `'accounting'`
- `default_order_by`: `['-fiscal_year_code']`
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
- `list`: `['fiscal_year_code', 'fiscal_year_name']`

#### `get_page_title(self) -> str`

**توضیح**: عنوان صفحه را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `_('Fiscal Years')`

#### `get_breadcrumbs(self) -> list`

**توضیح**: لیست breadcrumbs را برمی‌گرداند.

**مقدار بازگشتی**:
- `list`: `[{'label': _('Dashboard'), 'url': reverse('ui:dashboard')}, {'label': _('Accounting'), 'url': reverse('accounting:dashboard')}, {'label': _('Fiscal Years'), 'url': None}]`

#### `get_create_url(self) -> str`

**توضیح**: URL برای ایجاد سال مالی جدید را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `reverse('accounting:fiscal_year_create')`

#### `get_create_button_text(self) -> str`

**توضیح**: متن دکمه ایجاد را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `_('Create Fiscal Year')`

#### `get_detail_url_name(self) -> str`

**توضیح**: نام URL برای detail view را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `'accounting:fiscal_year_detail'`

#### `get_edit_url_name(self) -> str`

**توضیح**: نام URL برای edit view را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `'accounting:fiscal_year_edit'`

#### `get_delete_url_name(self) -> str`

**توضیح**: نام URL برای delete view را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `'accounting:fiscal_year_delete'`

#### `get_empty_state_title(self) -> str`

**توضیح**: عنوان empty state را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `_('No Fiscal Years Found')`

#### `get_empty_state_message(self) -> str`

**توضیح**: پیام empty state را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `_('Start by adding your first fiscal year.')`

#### `get_empty_state_icon(self) -> str`

**توضیح**: آیکون empty state را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `'📅'`

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

**Type**: `BaseCreateView`

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
- `active_module`: `'accounting'`
- `success_message`: `_('Fiscal year created successfully.')`

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

**توضیح**: قبل از ذخیره، `created_by` را تنظیم می‌کند.

**پارامترهای ورودی**:
- `form`: فرم معتبر `FiscalYearForm`

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به success_url

**منطق**:
1. `form.instance.created_by` را به `self.request.user` تنظیم می‌کند
2. `super().form_valid(form)` را فراخوانی می‌کند (که پیام موفقیت را نمایش می‌دهد)

#### `get_breadcrumbs(self) -> list`

**توضیح**: لیست breadcrumbs را برمی‌گرداند.

**مقدار بازگشتی**:
- `list`: `[{'label': _('Dashboard'), 'url': reverse('ui:dashboard')}, {'label': _('Accounting'), 'url': reverse('accounting:dashboard')}, {'label': _('Fiscal Years'), 'url': reverse('accounting:fiscal_years')}, {'label': _('Create'), 'url': None}]`

#### `get_cancel_url(self) -> str`

**توضیح**: URL برای cancel را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `reverse('accounting:fiscal_years')`

#### `get_form_title(self) -> str`

**توضیح**: عنوان فرم را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `_('Create Fiscal Year')`

**URL**: `/accounting/fiscal-years/create/`

---

## FiscalYearUpdateView

**Type**: `BaseUpdateView`, `EditLockProtectedMixin`

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
- `active_module`: `'accounting'`
- `success_message`: `_('Fiscal year updated successfully.')`

**متدها**:

#### `get_form_kwargs(self) -> Dict[str, Any]`

**توضیح**: `company_id` را به form kwargs اضافه می‌کند.

**مقدار بازگشتی**:
- `Dict[str, Any]`: form kwargs با `company_id` اضافه شده

**منطق**: مشابه `FiscalYearCreateView.get_form_kwargs()`

#### `form_valid(self, form: FiscalYearForm) -> HttpResponseRedirect`

**توضیح**: قبل از ذخیره، `edited_by` را تنظیم می‌کند.

**پارامترهای ورودی**:
- `form`: فرم معتبر `FiscalYearForm`

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به success_url

**منطق**:
1. `form.instance.edited_by` را به `self.request.user` تنظیم می‌کند
2. `super().form_valid(form)` را فراخوانی می‌کند (که پیام موفقیت را نمایش می‌دهد)

**نکته**: این view از `EditLockProtectedMixin` استفاده می‌کند که از concurrent editing جلوگیری می‌کند.

#### `get_breadcrumbs(self) -> list`

**توضیح**: لیست breadcrumbs را برمی‌گرداند.

**مقدار بازگشتی**:
- `list`: `[{'label': _('Dashboard'), 'url': reverse('ui:dashboard')}, {'label': _('Accounting'), 'url': reverse('accounting:dashboard')}, {'label': _('Fiscal Years'), 'url': reverse('accounting:fiscal_years')}, {'label': _('Edit'), 'url': None}]`

#### `get_cancel_url(self) -> str`

**توضیح**: URL برای cancel را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `reverse('accounting:fiscal_years')`

#### `get_form_title(self) -> str`

**توضیح**: عنوان فرم را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `_('Edit Fiscal Year')`

**URL**: `/accounting/fiscal-years/<int:pk>/edit/`

---

## FiscalYearDetailView

**Type**: `BaseDetailView`

**Template**: `shared/generic/generic_detail.html`

**توضیح**: مشاهده جزئیات سال مالی (read-only)

**Attributes**:
- `model`: `FiscalYear`
- `template_name`: `'shared/generic/generic_detail.html'`
- `context_object_name`: `'object'`
- `feature_code`: `'accounting.fiscal_years'`
- `required_action`: `'view_own'`
- `active_module`: `'accounting'`

**متدها**:

#### `get_queryset(self) -> QuerySet`

**توضیح**: queryset را بر اساس active company و permissions filter می‌کند و optimize می‌کند.

**مقدار بازگشتی**:
- `QuerySet`: queryset فیلتر شده با `select_related` برای `created_by`, `edited_by`

**منطق**:
1. فراخوانی `super().get_queryset()`
2. ایجاد instance از `AccountingBaseView` و تنظیم `request`
3. فراخوانی `filter_queryset_by_permissions(queryset, self.feature_code)`
4. `select_related('created_by', 'edited_by')` برای optimization
5. return queryset

#### `get_page_title(self) -> str`

**توضیح**: عنوان صفحه را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `_('View Fiscal Year')`

#### `get_context_data(self, **kwargs) -> Dict[str, Any]`

**توضیح**: context variables را برای generic_detail template اضافه می‌کند.

**Context Variables اضافه شده**:
- `detail_title`: `_('View Fiscal Year')`
- `info_banner`: لیست اطلاعات اصلی (Fiscal Year Code, Status, Current)
- `detail_sections`: لیست sections با fields (Basic Information)
- `list_url`: URL برای بازگشت به لیست
- `edit_url`: URL برای ویرایش

**منطق**:
1. `info_banner` شامل:
   - `{'label': _('Fiscal Year Code'), 'value': fiscal_year.fiscal_year_code, 'type': 'code'}`
   - `{'label': _('Status'), 'value': fiscal_year.is_enabled, 'type': 'badge'}`
   - اگر `fiscal_year.is_current`: `{'label': _('Current'), 'value': True, 'type': 'badge', 'true_label': _('Yes')}`
2. `detail_sections` شامل:
   - Basic Information: `fiscal_year_name`, `start_date`, `end_date`, `description` (اگر موجود باشد)

#### `get_list_url(self) -> str`

**توضیح**: URL برای بازگشت به لیست را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `reverse_lazy('accounting:fiscal_years')`

#### `get_edit_url(self) -> str`

**توضیح**: URL برای ویرایش را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `reverse_lazy('accounting:fiscal_year_edit', kwargs={'pk': self.object.pk})`

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

**URL**: `/accounting/fiscal-years/<int:pk>/`

---

## FiscalYearDeleteView

**Type**: `BaseDeleteView`

**Template**: `shared/generic/generic_confirm_delete.html`

**Success URL**: `accounting:fiscal_years`

**Attributes**:
- `model`: `FiscalYear`
- `success_url`: `reverse_lazy('accounting:fiscal_years')`
- `template_name`: `'shared/generic/generic_confirm_delete.html'`
- `feature_code`: `'accounting.fiscal_years'`
- `required_action`: `'delete_own'`
- `active_module`: `'accounting'`
- `success_message`: `_('Fiscal year deleted successfully.')`

**متدها**:

#### `get_delete_title(self) -> str`

**توضیح**: عنوان صفحه حذف را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `_('Delete Fiscal Year')`

#### `get_confirmation_message(self) -> str`

**توضیح**: پیام تایید حذف را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `_('Do you really want to delete this fiscal year?')`

#### `get_object_details(self) -> list`

**توضیح**: لیست جزئیات object برای نمایش در صفحه حذف را برمی‌گرداند.

**مقدار بازگشتی**:
- `list`: `[{'label': _('Code'), 'value': self.object.fiscal_year_code, 'type': 'code'}, {'label': _('Name'), 'value': self.object.fiscal_year_name}, {'label': _('Start Date'), 'value': self.object.start_date}, {'label': _('End Date'), 'value': self.object.end_date}]`

#### `get_breadcrumbs(self) -> list`

**توضیح**: لیست breadcrumbs را برمی‌گرداند.

**مقدار بازگشتی**:
- `list`: `[{'label': _('Dashboard'), 'url': reverse('ui:dashboard')}, {'label': _('Accounting'), 'url': reverse('accounting:dashboard')}, {'label': _('Fiscal Years'), 'url': reverse('accounting:fiscal_years')}, {'label': _('Delete'), 'url': None}]`

**URL**: `/accounting/fiscal-years/<int:pk>/delete/`

---

## استفاده در پروژه

### URL Patterns
```python
path('fiscal-years/', FiscalYearListView.as_view(), name='fiscal_years'),
path('fiscal-years/create/', FiscalYearCreateView.as_view(), name='fiscal_year_create'),
path('fiscal-years/<int:pk>/', FiscalYearDetailView.as_view(), name='fiscal_year_detail'),
path('fiscal-years/<int:pk>/edit/', FiscalYearUpdateView.as_view(), name='fiscal_year_edit'),
path('fiscal-years/<int:pk>/delete/', FiscalYearDeleteView.as_view(), name='fiscal_year_delete'),
```

### Permission Checking
تمام views از `FeaturePermissionRequiredMixin` استفاده می‌کنند و feature code `'accounting.fiscal_years'` را دارند.

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
3. **Search Support**: جستجو بر اساس `fiscal_year_code` و `fiscal_year_name`
4. **Status Filter**: فیلتر بر اساس `is_enabled` (default: فقط فعال‌ها)
5. **Edit Lock**: `FiscalYearUpdateView` از `EditLockProtectedMixin` استفاده می‌کند
6. **Auto User Setting**: `created_by` و `edited_by` به صورت خودکار تنظیم می‌شوند
7. **Success Messages**: تمام عملیات پیام موفقیت نمایش می‌دهند

---

**Last Updated**: 2025-12-01

