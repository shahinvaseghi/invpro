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
- `get_context_data()`: اضافه کردن `page_title`
- `form_valid()`: تنظیم `reported_by = request.user`، نمایش پیام موفقیت
- `get_success_url()`: redirect به `ticketing:ticket_list`

**نکات مهم**:
- `reported_by` به صورت خودکار از `request.user` تنظیم می‌شود
- `status` و `assigned_to` در create mode نمایش داده نمی‌شوند

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
- `get_context_data()`: اضافه کردن `page_title`
- `form_valid()`: نمایش پیام موفقیت
- `get_success_url()`: redirect به `ticketing:ticket_list`

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

