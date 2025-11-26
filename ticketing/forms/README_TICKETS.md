# ticketing/forms/tickets.py - Ticket Forms (Complete Documentation)

**هدف**: Forms برای مدیریت tickets در ماژول ticketing

این فایل شامل:
- TicketForm: فرم ایجاد/ویرایش ticket
- TicketCreateForm: فرم ایجاد ticket (بدون status و assigned_to)

---

## وابستگی‌ها

- `ticketing.models`: `Ticket`, `TicketTemplate`, `TicketCategory`, `TicketPriority`
- `ticketing.forms.base`: `TicketingBaseForm`, `TicketFormMixin`
- `django.forms`
- `django.utils.translation.gettext_lazy`

---

## TicketForm

**Type**: `TicketFormMixin, TicketingBaseForm`

**Model**: `Ticket`

**Fields**:
- `template`, `title`, `description`, `category`, `priority`, `status`, `assigned_to`

**متدها**:
- `__init__()`: فیلتر `template`, `category`, `priority` بر اساس company و `is_enabled=1`

---

## TicketCreateForm

**Type**: `TicketForm`

**Model**: `Ticket`

**Fields**:
- `template`, `title`, `description`, `category`, `priority` (بدون `status` و `assigned_to`)

**متدها**:
- `__init__()`: حذف `status` و `assigned_to` fields

**نکات مهم**:
- برای create mode استفاده می‌شود
- `status` و `assigned_to` در create mode نمایش داده نمی‌شوند

---

## نکات مهم

1. **Company Filtering**: تمام queryset ها بر اساس company فیلتر می‌شوند
2. **Create vs Update**: `TicketCreateForm` برای create، `TicketForm` برای update استفاده می‌شود
3. **Template Integration**: می‌تواند template انتخاب کند که dynamic fields دارد

