# ticketing/views/templates.py - Ticket Template Views (Complete Documentation)

**هدف**: Views برای مدیریت ticket templates در ماژول ticketing

این فایل شامل views برای:
- TicketTemplateListView: فهرست templates
- TicketTemplateCreateView: ایجاد template جدید
- TicketTemplateUpdateView: ویرایش template
- TicketTemplateDetailView: نمایش جزئیات template
- TicketTemplateDeleteView: حذف template

---

## وابستگی‌ها

- `ticketing.models`: `TicketTemplate`, `TicketCategory`, `TicketPriority`
- `ticketing.forms.templates`: `TicketTemplateForm`, `TicketTemplateFieldFormSet`, `TicketTemplatePermissionFormSet`, `TicketTemplateEventFormSet`
- `ticketing.views.base`: `TicketingBaseView`
- `shared.mixins`: `FeaturePermissionRequiredMixin`
- `django.views.generic`: `CreateView`, `DeleteView`, `ListView`, `UpdateView`
- `django.contrib.messages`
- `django.db.transaction`
- `django.db.models.Q`
- `django.urls.reverse_lazy`
- `django.utils.translation.gettext_lazy`

---

## TicketTemplateListView

**Type**: `BaseListView` (از `shared.views.base`)

**Template**: `ticketing/templates_list.html` (extends `shared/generic/generic_list.html`)

**Attributes**:
- `model`: `TicketTemplate`
- `template_name`: `'ticketing/templates_list.html'`
- `context_object_name`: `'object_list'`
- `paginate_by`: `50`
- `feature_code`: `'ticketing.management.templates'`
- `required_action`: `'view_all'`

**متدها**:

#### `get_base_queryset(self) -> QuerySet`
- **Returns**: queryset فیلتر شده بر اساس company
- **Logic**:
  1. دریافت `company_id` از session
  2. اگر موجود باشد: `TicketTemplate.objects.filter(company_id=company_id)`
  3. در غیر این صورت: `TicketTemplate.objects.none()`
  4. بازگشت queryset

#### `get_search_fields(self) -> list`
- **Returns**: لیست fields برای search
- **Logic**:
  - بازگشت `['name', 'template_code', 'description']`

#### `get_queryset(self) -> QuerySet`
- **Returns**: queryset فیلتر شده با search و category filtering
- **Logic**:
  1. دریافت queryset از `super().get_queryset()` (که search را اعمال می‌کند)
  2. **Category filtering** (اگر `category` در query parameter وجود دارد):
     - فیلتر: `queryset.filter(category_id=category_id)`
  3. مرتب‌سازی: `order_by('sort_order', 'template_code', 'name')`
  4. بازگشت queryset

**Query Parameters**:
- `search`: جستجو در name، template_code، description (از base class)
- `category`: فیلتر بر اساس category ID

---

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`
- **Returns**: context با categories
- **Logic**:
  1. دریافت context از `super().get_context_data()`
  2. **اضافه کردن categories**:
     - دریافت `company_id` از session
     - اگر موجود باشد:
       - فیلتر: `TicketCategory.objects.filter(company_id=company_id, is_enabled=1)`
       - مرتب‌سازی: `order_by('name')`
       - اضافه کردن به context
  3. بازگشت context

**URL**: `/ticketing/templates/`

---

## TicketTemplateCreateView

**Type**: `BaseMultipleFormsetCreateView` (از `shared.views.base_additional`)

**Template**: `ticketing/template_form.html` (extends `shared/generic/generic_form.html`)

**Form**: `TicketTemplateForm`

**Formsets**: `TicketTemplateFieldFormSet`, `TicketTemplatePermissionFormSet`, `TicketTemplateEventFormSet`

**Success URL**: `ticketing:templates`

**Attributes**:
- `model`: `TicketTemplate`
- `form_class`: `TicketTemplateForm`
- `template_name`: `'ticketing/template_form.html'`
- `success_url`: `reverse_lazy('ticketing:templates')`
- `feature_code`: `'ticketing.management.templates'`
- `required_action`: `'create'`

**متدها**:

#### `get_form_kwargs(self) -> Dict[str, Any]`

**توضیح**: `request` را به form پاس می‌دهد.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `Dict[str, Any]`: kwargs با `request` اضافه شده

**منطق**:
1. kwargs را از `super().get_form_kwargs()` دریافت می‌کند
2. اضافه کردن `kwargs['request'] = self.request`
3. kwargs را برمی‌گرداند

---

#### `get_formset_kwargs(self, formset_name: str) -> Dict[str, Any]`
- **Parameters**: `formset_name`: نام formset ('fields', 'permissions', 'events')
- **Returns**: kwargs برای formset
- **Logic**:
  1. دریافت kwargs از `super().get_formset_kwargs(formset_name)`
  2. اگر `instance` موجود نباشد:
     - تنظیم `instance = TicketTemplate()` (temporary instance)
  3. بازگشت kwargs

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`
- **Returns**: context با categories و priorities
- **Logic**:
  1. دریافت context از `super().get_context_data()` (که 3 formsets را اضافه می‌کند)
  2. **اضافه کردن categories و priorities**:
     - دریافت `company_id` از session
     - اگر موجود باشد:
       - `categories`: `TicketCategory.objects.filter(company_id=company_id, is_enabled=1).order_by('name')`
       - `priorities`: `TicketPriority.objects.filter(company_id=company_id, is_enabled=1).order_by('priority_level')`
       - اضافه کردن به context
  3. بازگشت context

#### `process_formset(self, formset_name: str, formset) -> list`
- **Parameters**: `formset_name`: نام formset, `formset`: formset instance
- **Returns**: لیست instances پردازش شده
- **Logic**:
  1. دریافت `company_id` از session
  2. اگر موجود باشد:
     - `instances = formset.save(commit=False)`
     - برای هر `instance`:
       - `instance.company_id = company_id`
       - اگر `instance.template` موجود باشد و `instance` دارای `template_code` attribute باشد:
         - `instance.template_code = instance.template.template_code`
       - `instance.save()`
     - بازگشت `instances`
  3. در غیر این صورت: بازگشت `None`

---

#### `form_valid(self, form: TicketTemplateForm) -> HttpResponseRedirect`
- **Parameters**: `form`: فرم معتبر `TicketTemplateForm`
- **Returns**: redirect به `success_url`
- **Logic**:
  1. دریافت `company_id` از session
  2. اگر موجود باشد: `form.instance.company_id = company_id`
  3. **ذخیره با base class**:
     - فراخوانی `super().form_valid(form)` که:
       - template را ذخیره می‌کند
       - تمام 3 formsets را validate و save می‌کند
       - برای هر formset، `process_formset()` را فراخوانی می‌کند که `company_id` و `template_code` را تنظیم می‌کند
  4. بازگشت response

**نکات مهم**:
- از `BaseMultipleFormsetCreateView` استفاده می‌کند که تمام formsets را به صورت خودکار مدیریت می‌کند
- `process_formset()` برای هر formset فراخوانی می‌شود که `company_id` و `template_code` را تنظیم می‌کند
- تمام عملیات در یک transaction انجام می‌شود (از base class)

**URL**: `/ticketing/templates/create/`

---

## TicketTemplateUpdateView

**Type**: `BaseMultipleFormsetUpdateView, EditLockProtectedMixin` (از `shared.views.base_additional` و `shared.views.base`)

**Template**: `ticketing/template_form.html` (extends `shared/generic/generic_form.html`)

**Form**: `TicketTemplateForm`

**Formsets**: `TicketTemplateFieldFormSet`, `TicketTemplatePermissionFormSet`, `TicketTemplateEventFormSet`

**Success URL**: `ticketing:templates`

**Attributes**:
- `model`: `TicketTemplate`
- `form_class`: `TicketTemplateForm`
- `template_name`: `'ticketing/template_form.html'`
- `success_url`: `reverse_lazy('ticketing:templates')`
- `feature_code`: `'ticketing.management.templates'`
- `required_action`: `'edit_own'`

**متدها**:

#### `get_form_kwargs(self) -> Dict[str, Any]`

**توضیح**: `request` را به form پاس می‌دهد.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `Dict[str, Any]`: kwargs با `request` اضافه شده

**منطق**:
1. kwargs را از `super().get_form_kwargs()` دریافت می‌کند
2. اضافه کردن `kwargs['request'] = self.request`
3. kwargs را برمی‌گرداند

---

#### `get_queryset(self) -> QuerySet`

**توضیح**: queryset را با company filtering برمی‌گرداند.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `QuerySet`: queryset فیلتر شده بر اساس company

**منطق**:
1. دریافت `company_id` از session
2. فیلتر: `TicketTemplate.objects.filter(company_id=company_id)`
3. queryset را برمی‌گرداند

---

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`
- **Returns**: context با categories و priorities
- **Logic**:
  1. دریافت context از `super().get_context_data()` (که 3 formsets را اضافه می‌کند)
  2. **اضافه کردن categories و priorities**:
     - دریافت `company_id` از session
     - اگر موجود باشد:
       - `categories`: `TicketCategory.objects.filter(company_id=company_id, is_enabled=1).order_by('name')`
       - `priorities`: `TicketPriority.objects.filter(company_id=company_id, is_enabled=1).order_by('priority_level')`
       - اضافه کردن به context
  3. بازگشت context

#### `process_formset(self, formset_name: str, formset) -> list`
- **Parameters**: `formset_name`: نام formset, `formset`: formset instance
- **Returns**: لیست instances پردازش شده
- **Logic**:
  1. دریافت `company_id` از session
  2. اگر موجود باشد:
     - `instances = formset.save(commit=False)`
     - برای هر `instance`:
       - `instance.company_id = company_id`
       - اگر `instance.template` موجود باشد و `instance` دارای `template_code` attribute باشد:
         - `instance.template_code = instance.template.template_code`
       - `instance.save()`
     - بازگشت `instances`
  3. در غیر این صورت: بازگشت `None`

---

#### `form_valid(self, form: TicketTemplateForm) -> HttpResponseRedirect`
- **Parameters**: `form`: فرم معتبر `TicketTemplateForm`
- **Returns**: redirect به `success_url`
- **Logic**:
  1. **ذخیره با base class**:
     - فراخوانی `super().form_valid(form)` که:
       - template را ذخیره می‌کند
       - تمام 3 formsets را validate و save می‌کند
       - برای هر formset، `process_formset()` را فراخوانی می‌کند که `company_id` و `template_code` را تنظیم می‌کند
  2. بازگشت response

**نکات مهم**:
- از `BaseMultipleFormsetUpdateView` استفاده می‌کند که تمام formsets را به صورت خودکار مدیریت می‌کند
- `process_formset()` برای هر formset فراخوانی می‌شود که `company_id` و `template_code` را تنظیم می‌کند
- تمام عملیات در یک transaction انجام می‌شود (از base class)
- از `@transaction.atomic` استفاده می‌کند

**URL**: `/ticketing/templates/<pk>/edit/`

---

## TicketTemplateDetailView

### `TicketTemplateDetailView`

**توضیح**: نمایش جزئیات Ticket Template (read-only)

**Type**: `BaseDetailView` (از `shared.views.base`)

**Template**: `shared/generic/generic_detail.html`

**Attributes**:
- `model`: `TicketTemplate`
- `template_name`: `'shared/generic/generic_detail.html'`
- `context_object_name`: `'object'`
- `feature_code`: `'ticketing.management.templates'`
- `required_action`: `'view_all'`
- `active_module`: `'ticketing'`

**Context Variables**:
- `object`: TicketTemplate instance
- `detail_title`: `_('View Ticket Template')`
- `info_banner`: لیست اطلاعات اصلی (template_code, status)
- `detail_sections`: لیست sections برای نمایش:
  - Basic Information: name, category (اگر موجود باشد), subcategory (اگر موجود باشد), default_priority (اگر موجود باشد), description (اگر موجود باشد)
  - Template Fields: table با headers (Field Name, Field Type, Required, Order) و data rows
- `list_url`, `edit_url`: URLs برای navigation
- `can_edit_object`: بررسی اینکه آیا Template قفل است یا نه

**متدها**:

#### `get_queryset(self) -> QuerySet`
- **Returns**: queryset بهینه شده با select_related و prefetch_related
- **Logic**:
  1. دریافت `company_id` از session
  2. اگر موجود نباشد: `TicketTemplate.objects.none()`
  3. فیلتر: `TicketTemplate.objects.filter(company_id=company_id)`
  4. اعمال `select_related('category', 'subcategory', 'default_priority', 'created_by', 'edited_by')`
  5. اعمال `prefetch_related('fields', 'permissions')`
  6. بازگشت queryset

#### `get_context_data(self, **kwargs) -> Dict[str, Any]`
- **Returns**: context با detail sections
- **Logic**:
  1. دریافت context از `super().get_context_data()`
  2. ساخت `info_banner`:
     - Template Code (type: 'code')
     - Status (type: 'badge')
  3. ساخت `detail_sections`:
     - **Basic Information**: name, category (اگر موجود باشد), subcategory (اگر موجود باشد), default_priority (اگر موجود باشد), description (اگر موجود باشد)
     - **Template Fields**: اگر `fields.exists()` باشد:
       - ساخت table با headers: Field Name, Field Type, Required, Order
       - ساخت data rows از `fields.all()`
       - اضافه کردن section با type='table'
  4. بازگشت context

#### `get_list_url(self) -> str`
- **Returns**: URL برای لیست Templates

#### `get_edit_url(self) -> str`
- **Returns**: URL برای ویرایش Template

#### `can_edit_object(self, obj=None, feature_code=None) -> bool`
- **Returns**: True اگر Template قفل نباشد
- **Logic**:
  - بررسی `is_locked` attribute
  - اگر `is_locked=True` باشد، return False

**URL**: `/ticketing/templates/<pk>/`

---

## TicketTemplateDeleteView

**Type**: `BaseDeleteView` (از `shared.views.base`)

**Template**: `shared/generic/generic_confirm_delete.html`

**Success URL**: `ticketing:templates`

**Attributes**:
- `model`: `TicketTemplate`
- `template_name`: `'ticketing/template_confirm_delete.html'`
- `success_url`: `reverse_lazy('ticketing:templates')`
- `feature_code`: `'ticketing.management.templates'`
- `required_action`: `'delete_own'`

**متدها**:

#### `get_queryset(self) -> QuerySet`

**توضیح**: queryset را با company filtering برمی‌گرداند.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `QuerySet`: queryset فیلتر شده بر اساس company

**منطق**:
1. دریافت `company_id` از session
2. فیلتر: `TicketTemplate.objects.filter(company_id=company_id)`
3. queryset را برمی‌گرداند

---

#### `delete(self, request, *args, **kwargs) -> HttpResponseRedirect`

**توضیح**: TicketTemplate را حذف می‌کند و پیام موفقیت نمایش می‌دهد.

**پارامترهای ورودی**:
- `request`: HTTP request
- `*args`, `**kwargs`: آرگومان‌های اضافی

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به `success_url`

**منطق**:
1. نمایش پیام موفقیت: "Template deleted successfully."
2. فراخوانی `super().delete(request, *args, **kwargs)` (که TicketTemplate را حذف می‌کند و redirect می‌کند)

---

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`

**توضیح**: context variables را برای template اضافه می‌کند.

**پارامترهای ورودی**:
- `**kwargs`: متغیرهای context اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با `page_title`

**Context Variables اضافه شده**:
- `delete_title`: `_('Delete Template')`
- `confirmation_message`: پیام تأیید حذف
- `object_details`: جزئیات template برای نمایش
- `warning_message`: هشدار در مورد حذف fields, permissions, events
- `cancel_url`: URL برای cancel
- `breadcrumbs`: لیست breadcrumbs

**URL**: `/ticketing/templates/<pk>/delete/`

---

## نکات مهم

1. **Multi-formset Management**: 3 formsets مدیریت می‌شوند (fields, permissions, events)
2. **Template Code**: `template_code` برای fields, permissions, events به صورت خودکار تنظیم می‌شود
3. **Transaction Management**: از `@transaction.atomic` استفاده می‌شود
4. **Generic Templates**: تمام templates به generic templates منتقل شده‌اند

---

## الگوهای مشترک

1. **Company Filtering**: تمام queryset ها بر اساس `active_company_id` فیلتر می‌شوند
2. **Permission Checking**: تمام views از `FeaturePermissionRequiredMixin` استفاده می‌کنند
3. **Formset Management**: 3 formsets در create و update views مدیریت می‌شوند

