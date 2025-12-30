# ticketing/views/tickets.py - Ticket Views (Complete Documentation)

**هدف**: Views برای مدیریت tickets در ماژول ticketing

این فایل شامل views برای:
- TicketListView: فهرست tickets
- TicketCreateView: ایجاد ticket جدید
- TicketDetailView: نمایش جزئیات ticket
- TicketEditView: ویرایش ticket

---

## وابستگی‌ها

- `ticketing.models`: `Ticket`
- `ticketing.views.base`: `TicketingBaseView`
- `django.views.generic`: `ListView`, `CreateView`, `UpdateView`
- `django.contrib.messages`
- `django.shortcuts.get_object_or_404`
- `django.urls.reverse_lazy`
- `django.utils.translation.gettext_lazy`

---

## TicketListView

**Type**: `BaseListView` (از `shared.views.base`)

**Template**: `ticketing/ticket_list.html`

**Attributes**:
- `model`: `Ticket`
- `template_name`: `'ticketing/ticket_list.html'`
- `context_object_name`: `'tickets'`
- `paginate_by`: `50`

**متدها**:

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`

**توضیح**: context variables را برای template اضافه می‌کند.

**پارامترهای ورودی**:
- `**kwargs`: متغیرهای context اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با `page_title`

**Context Variables اضافه شده**:
- `page_title`: `_('Tickets')`

**نکات مهم**:
- از `BaseListView` استفاده می‌کند که permission checking را مدیریت می‌کند

**URL**: `/ticketing/tickets/`

---

## TicketCreateView

**Type**: `BaseCreateView` (از `shared.views.base`)

**Template**: `ticketing/ticket_create.html`

**Fields**: `["template", "title", "description", "category", "priority"]`

**Attributes**:
- `model`: `Ticket`
- `template_name`: `'ticketing/ticket_create.html'`
- `fields`: `["template", "title", "description", "category", "priority"]`

**متدها**:

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`

**توضیح**: اضافه کردن context برای template selection یا form display.

**Context Variables**:
- `page_title`: `_('Create Ticket')`
- `selected_template`: `TicketTemplate` instance (اگر `template_id` در GET باشد)
- `template_fields`: لیست fields با options (اگر template انتخاب شده باشد)
- `available_templates`: لیست templates قابل دسترس برای user (اگر template انتخاب نشده باشد)

**منطق**:
1. اضافه کردن `page_title = _('Create Ticket')`
2. بررسی `template_id` از GET parameter:
   - اگر `template_id` موجود است:
     - **دریافت template**:
       - `get_object_or_404(TicketTemplate, pk=template_id, company_id=active_company_id, is_enabled=1)`
       - اگر template پیدا نشود: exception و error message
     - **بررسی permission**:
       - اگر `user.is_superuser`: `has_permission = True`
       - در غیر این صورت:
         - دریافت permissions: `template.permissions.filter(is_enabled=1, can_create=1)`
         - برای هر permission:
           - اگر `perm.user_id == user.id`: `has_permission = True` و break
           - اگر `perm.group_id` و `user.groups.filter(id=perm.group_id).exists()`: `has_permission = True` و break
     - **اگر permission دارد**:
       - دریافت fields: `template.fields.filter(is_enabled=1).prefetch_related('options').order_by('field_order')`
       - **پردازش fields برای extract کردن options**:
         - برای هر field:
           - اگر `field_type` در `['dropdown', 'radio', 'checkbox', 'multi_select']`:
             - **Debug logging**: Log field_name، field_type، field_config، options_source
             - **Manual options** (اولویت اول):
               - اگر `field_config.get('options_source') == 'manual'` و `field_config.get('options')`:
                 - برای هر option در `field_config['options']`:
                   - اگر `isinstance(opt, dict)` و `'value'` و `'label'` موجود است:
                     - اضافه کردن به `field_data['options']` با `value`, `label`, `is_default`
                 - **Debug logging**: Log manual options count
             - **Fallback: options بدون options_source**:
               - اگر `field_config.get('options')` (بدون options_source):
                 - برای هر option: اضافه کردن به `field_data['options']`
             - **Fallback: TicketTemplateFieldOption model**:
               - اگر options در field_config نیست:
                 - برای هر `opt` در `field.options.all()`:
                   - اگر `opt.is_enabled == 1`:
                     - اضافه کردن به `field_data['options']` با `option_value`, `option_label`, `is_default`
                 - **Debug logging**: Log options from model
             - **Debug logging**: Log final options count
           - اضافه کردن `field_data` به `fields_with_options`
       - اضافه کردن `selected_template` و `template_fields` به context
     - **اگر permission ندارد**:
       - خطا: "You don't have permission to create tickets with this template."
       - `selected_template = None`
   - اگر `template_id` موجود نیست:
     - `selected_template = None`
     - **دریافت available templates**:
       - دریافت `company_id` از session
       - اگر `company_id` موجود است:
         - دریافت تمام enabled templates: `TicketTemplate.objects.filter(company_id=company_id, is_enabled=1).order_by('sort_order', 'name')`
         - **فیلتر کردن بر اساس user permissions**:
           - برای هر template:
             - بررسی permission (مشابه بالا)
             - اگر permission دارد: اضافه به `available_templates`
         - اضافه کردن `available_templates` به context

**Permission Checking Logic**:
- بررسی `template.permissions.filter(is_enabled=1, can_create=1)`
- Match کردن با `user.id` یا `user.groups`

---

#### `get_initial(self) -> Dict[str, Any]`

**توضیح**: تنظیم initial values برای form.

**مقدار بازگشتی**:
- `Dict[str, Any]`: initial data با `template` (اگر `template_id` در GET باشد)

**منطق**:
- اگر `template_id` در GET parameter وجود داشته باشد:
  - تنظیم `initial['template'] = template_id`

---

#### `form_valid(self, form) -> HttpResponseRedirect`

**توضیح**: Ticket را ذخیره می‌کند با تنظیم `reported_by` و `company_id`.

**پارامترهای ورودی**:
- `form`: فرم معتبر

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به success URL

**منطق**:
1. دریافت `company_id` از session
2. اگر `company_id` موجود است:
   - تنظیم `form.instance.company_id = company_id`
3. تنظیم `form.instance.reported_by = request.user`
4. نمایش پیام موفقیت: "Ticket created successfully."
5. فراخوانی `super().form_valid(form)` (ذخیره و redirect)

---

#### `get_success_url(self) -> str`

**توضیح**: بازگشت URL برای redirect بعد از successful creation.

**مقدار بازگشتی**:
- `str`: URL برای `ticketing:ticket_list`

**نکات مهم**:
- `reported_by` به صورت خودکار از `request.user` تنظیم می‌شود
- `status` و `assigned_to` در create mode نمایش داده نمی‌شوند
- Template selection: کاربر می‌تواند template را از لیست انتخاب کند یا مستقیماً با `template_id` در URL
- Permission-based template filtering: فقط templates با permission نمایش داده می‌شوند

**URL**: `/ticketing/tickets/create/`

---

## TicketDetailView

### `TicketDetailView`

**توضیح**: نمایش جزئیات Ticket (read-only)

**Type**: `BaseDetailView` (از `shared.views.base`)

**Template**: `shared/generic/generic_detail.html`

**Attributes**:
- `model`: `Ticket`
- `template_name`: `'shared/generic/generic_detail.html'`
- `context_object_name`: `'object'`
- `feature_code`: `'ticketing.tickets'`
- `required_action`: `'view_all'`
- `active_module`: `'ticketing'`

**Context Variables**:
- `object`: Ticket instance
- `detail_title`: `_('View Ticket')`
- `info_banner`: لیست اطلاعات اصلی (ticket_code, status, priority (اگر موجود باشد))
- `detail_sections`: لیست sections برای نمایش:
  - Basic Information: title, description (اگر موجود باشد), template (اگر موجود باشد), category (اگر موجود باشد), subcategory (اگر موجود باشد)
  - Assignment Information: reported_by (اگر موجود باشد), assigned_to (اگر موجود باشد)
- `list_url`, `edit_url`: URLs برای navigation
- `can_edit_object`: بررسی اینکه آیا Ticket قفل است یا نه

**متدها**:

#### `get_queryset(self) -> QuerySet`
- **Returns**: queryset بهینه شده با select_related
- **Logic**:
  1. دریافت `company_id` از session
  2. اگر موجود نباشد: `Ticket.objects.none()`
  3. فیلتر: `Ticket.objects.filter(company_id=company_id)`
  4. اعمال `select_related('template', 'category', 'subcategory', 'priority', 'reported_by', 'assigned_to', 'created_by', 'edited_by')`
  5. بازگشت queryset

#### `get_context_data(self, **kwargs) -> Dict[str, Any]`
- **Returns**: context با detail sections
- **Logic**:
  1. دریافت context از `super().get_context_data()`
  2. ساخت `info_banner`:
     - Ticket Code (type: 'code')
     - Status (از `get_status_display()`)
     - Priority (اگر موجود باشد)
  3. ساخت `detail_sections`:
     - **Basic Information**: title, description (اگر موجود باشد), template (اگر موجود باشد), category (اگر موجود باشد), subcategory (اگر موجود باشد)
     - **Assignment Information**: اگر `reported_by` یا `assigned_to` موجود باشد:
       - reported_by (از `get_full_name()` یا `username`)
       - assigned_to (از `get_full_name()` یا `username`)
       - اضافه کردن section
  4. بازگشت context

#### `get_list_url(self) -> str`
- **Returns**: URL برای لیست Tickets

#### `get_edit_url(self) -> str`
- **Returns**: URL برای ویرایش Ticket

#### `can_edit_object(self, obj=None, feature_code=None) -> bool`
- **Returns**: True اگر Ticket قفل نباشد
- **Logic**:
  - بررسی `is_locked` attribute
  - اگر `is_locked=True` باشد، return False

**URL**: `/ticketing/tickets/<pk>/`

---

## TicketEditView

**Type**: `BaseUpdateView, EditLockProtectedMixin` (از `shared.views.base`)

**Template**: `ticketing/ticket_edit.html`

**Fields**: `["title", "description", "category", "priority", "status", "assigned_to"]`

**Attributes**:
- `model`: `Ticket`
- `template_name`: `'ticketing/ticket_edit.html'`
- `fields`: `["title", "description", "category", "priority", "status", "assigned_to"]`

**متدها**:

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`

**توضیح**: context variables را برای template اضافه می‌کند.

**پارامترهای ورودی**:
- `**kwargs`: متغیرهای context اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با `page_title`

**Context Variables اضافه شده**:
- `page_title`: `_('Edit Ticket')`
- `object`: Ticket instance (از UpdateView)

---

#### `form_valid(self, form) -> HttpResponseRedirect`

**توضیح**: Ticket را ذخیره می‌کند و پیام موفقیت نمایش می‌دهد.

**پارامترهای ورودی**:
- `form`: فرم معتبر

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به success URL

**منطق**:
1. نمایش پیام موفقیت: "Ticket updated successfully."
2. فراخوانی `super().form_valid(form)` (ذخیره و redirect)

---

#### `get_success_url(self) -> str`

**توضیح**: بازگشت URL برای redirect بعد از successful update.

**مقدار بازگشتی**:
- `str`: URL برای `ticketing:ticket_list`

**نکات مهم**:
- `status` و `assigned_to` در edit mode نمایش داده می‌شوند

**URL**: `/ticketing/tickets/<pk>/edit/`

---

## نکات مهم

1. **Base Classes**: تمام views از base classes استفاده می‌کنند (`BaseListView`, `BaseCreateView`, `BaseUpdateView`, `BaseDetailView`)
2. **Reported By**: در create mode، `reported_by` به صورت خودکار از `request.user` تنظیم می‌شود
3. **Fields**: در create mode، `status` و `assigned_to` نمایش داده نمی‌شوند (فقط در edit mode)
4. **Template Selection**: کاربر می‌تواند template را از لیست انتخاب کند یا مستقیماً با `template_id` در URL
5. **Permission-based Template Filtering**: فقط templates با permission نمایش داده می‌شوند
6. **Options Extraction**: برای dropdown/radio/checkbox/multi_select fields، options از `field_config` (manual) یا `TicketTemplateFieldOption` model استخراج می‌شوند

---

## الگوهای مشترک

1. **Base View**: از base classes استفاده می‌کنند (`BaseListView`, `BaseCreateView`, `BaseUpdateView`, `BaseDetailView`)
2. **Success URL**: همه به `ticketing:ticket_list` redirect می‌کنند
3. **Company Filtering**: تمام queryset ها بر اساس `active_company_id` فیلتر می‌شوند

