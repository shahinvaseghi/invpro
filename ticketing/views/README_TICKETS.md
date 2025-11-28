# ticketing/views/tickets.py - Ticket Views (Complete Documentation)

**هدف**: Views برای مدیریت tickets در ماژول ticketing

این فایل شامل views برای:
- TicketListView: فهرست tickets
- TicketCreateView: ایجاد ticket جدید
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

**Type**: `TicketingBaseView, ListView`

**Template**: `ticketing/ticket_list.html`

**Attributes**:
- `model`: `Ticket`
- `template_name`: `'ticketing/ticket_list.html'`
- `context_object_name`: `'tickets'`
- `paginate_by`: `50`

**متدها**:
- `get_context_data()`: اضافه کردن `page_title`

**نکات مهم**:
- از `FeaturePermissionRequiredMixin` استفاده نمی‌کند (فقط `TicketingBaseView`)

**URL**: `/ticketing/tickets/`

---

## TicketCreateView

**Type**: `TicketingBaseView, CreateView`

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
1. بررسی `template_id` از GET parameter:
   - اگر `template_id` وجود داشته باشد:
     - دریافت template از database
     - بررسی permission:
       - Superuser: همیشه دسترسی دارد
       - سایر users: بررسی `template.permissions` (user یا group-based)
     - اگر permission دارد:
       - دریافت fields از template (فقط enabled ones)
       - پردازش fields برای extract کردن options:
         - برای dropdown/radio/checkbox/multi_select:
           - اول از `field_config.options` (manual options)
           - سپس از `TicketTemplateFieldOption` model
       - ساخت `fields_with_options` list
       - اضافه کردن `selected_template` و `template_fields` به context
     - اگر permission ندارد:
       - نمایش error message
       - `selected_template = None`
   - اگر `template_id` وجود نداشته باشد:
     - دریافت تمام enabled templates برای company
     - فیلتر کردن بر اساس user permissions
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

**توضیح**: ذخیره ticket با تنظیم `reported_by` و `company_id`.

**پارامترهای ورودی**:
- `form`: فرم معتبر

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به success URL

**منطق**:
1. تنظیم `company_id` از session
2. تنظیم `reported_by = request.user`
3. نمایش پیام موفقیت
4. فراخوانی `super().form_valid(form)`

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

## TicketEditView

**Type**: `TicketingBaseView, UpdateView`

**Template**: `ticketing/ticket_edit.html`

**Fields**: `["title", "description", "category", "priority", "status", "assigned_to"]`

**Attributes**:
- `model`: `Ticket`
- `template_name`: `'ticketing/ticket_edit.html'`
- `fields`: `["title", "description", "category", "priority", "status", "assigned_to"]`

**متدها**:

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`

**توضیح**: اضافه کردن context برای template.

**Context Variables**:
- `page_title`: `_('Edit Ticket')`
- `object`: Ticket instance

---

#### `form_valid(self, form) -> HttpResponseRedirect`

**توضیح**: ذخیره ticket و نمایش پیام موفقیت.

**پارامترهای ورودی**:
- `form`: فرم معتبر

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به success URL

**منطق**:
1. نمایش پیام موفقیت
2. فراخوانی `super().form_valid(form)`

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

1. **Permission Mixin**: این views از `FeaturePermissionRequiredMixin` استفاده نمی‌کنند (فقط `TicketingBaseView`)
2. **Reported By**: در create mode، `reported_by` به صورت خودکار تنظیم می‌شود
3. **Fields**: در create mode، `status` و `assigned_to` نمایش داده نمی‌شوند

---

## الگوهای مشترک

1. **Base View**: از `TicketingBaseView` استفاده می‌کنند
2. **Success URL**: همه به `ticketing:ticket_list` redirect می‌کنند

