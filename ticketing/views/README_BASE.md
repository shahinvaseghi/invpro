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

**توضیح**: از تغییر ticket های قفل شده و ticket هایی که کاربر مالک آن‌ها نیست جلوگیری می‌کند.

**Attributes**:
- `lock_redirect_url_name`: نام URL برای redirect (اختیاری)
- `lock_error_message`: پیام خطا برای locked tickets (default: `_("Ticket is locked and cannot be modified.")`)
- `owner_field`: نام فیلد مالک (default: `'reported_by'`)
- `owner_error_message`: پیام خطا برای owner check (default: `_("Only the ticket creator can modify this ticket.")`)
- `protected_methods`: tuple از HTTP methods که باید protected باشند (default: `('get', 'post', 'put', 'patch', 'delete')`)

**متدها**:

#### `dispatch(self, request, *args, **kwargs) -> HttpResponse`

**توضیح**: بررسی lock و owner قبل از اجرای view.

**منطق**:
1. اگر request method در `protected_methods` باشد:
   - دریافت object با `get_object()`
   - بررسی `is_locked`:
     - اگر `is_locked == 1`: نمایش error message و redirect
   - بررسی owner:
     - اگر `owner_field` تنظیم شده باشد:
       - دریافت owner از object
       - اگر owner موجود باشد و `owner.id != request.user.id`:
         - نمایش error message و redirect
2. فراخوانی `super().dispatch()` برای ادامه

---

#### `_get_lock_redirect_url(self) -> str`

**توضیح**: دریافت URL برای redirect در صورت lock یا owner mismatch.

**مقدار بازگشتی**:
- `str`: URL برای redirect

**منطق**:
1. اگر `lock_redirect_url_name` تنظیم شده باشد:
   - استفاده از `reverse(lock_redirect_url_name)`
2. اگر `list_url_name` attribute موجود باشد:
   - استفاده از `reverse(list_url_name)`
3. Fallback: `reverse('ticketing:ticket_list')`

**نکات مهم**:
- فقط ticket creator می‌تواند ticket را ویرایش کند (بر اساس `owner_field`)
- Locked tickets قابل ویرایش نیستند
- از `dispatch` method برای intercept کردن requests استفاده می‌کند

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

