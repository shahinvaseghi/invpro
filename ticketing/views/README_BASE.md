# ticketing/views/base.py - Base Views

**هدف**: کلاس‌های پایه برای views ماژول ticketing

---

## Base Classes

### `TicketingBaseView(LoginRequiredMixin)`

**توضیح**: کلاس پایه با context و فیلتر شرکت مشترک برای تمام views ماژول ticketing.

**متدها**:

#### `get_queryset()`

**توضیح**: queryset را بر اساس شرکت فعال فیلتر می‌کند.

**مقدار بازگشتی**:
- `QuerySet`: queryset فیلتر شده بر اساس `active_company_id`

---

#### `get_context_data(**kwargs) -> Dict[str, Any]`

**توضیح**: context مشترک را اضافه می‌کند.

**مقدار بازگشتی**:
- Context با `active_module = 'ticketing'` اضافه شده

---

### `TicketLockProtectedMixin`

**توضیح**: از تغییر ticket های قفل شده جلوگیری می‌کند.

**منطق**: مشابه `DocumentLockProtectedMixin` اما برای tickets.

**Attributes**:
- `lock_redirect_url_name`: نام URL برای redirect
- `lock_error_message`: پیام خطا
- `owner_field`: نام فیلد مالک (default: `'created_by'`)

---

## وابستگی‌ها

- `django.contrib.auth.mixins`: `LoginRequiredMixin`
- `ticketing.models`: تمام مدل‌های ticketing

---

## استفاده در پروژه

```python
from ticketing.views.base import TicketingBaseView, TicketLockProtectedMixin

class TicketListView(TicketingBaseView, ListView):
    model = Ticket
```

---

## نکات مهم

1. **Company Filtering**: تمام views به صورت خودکار بر اساس شرکت فعال فیلتر می‌شوند
2. **Lock Protection**: از `TicketLockProtectedMixin` برای views ویرایش استفاده کنید

