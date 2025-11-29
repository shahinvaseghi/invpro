# shared/utils/notifications.py - Notification Utilities (Complete Documentation)

**هدف**: Helper functions برای مدیریت notifications در ماژول shared

این فایل شامل utility functions برای:
- ایجاد و به‌روزرسانی notifications
- دریافت unread notifications
- شمارش unread notifications
- دریافت recent notifications

---

## وابستگی‌ها

- `shared.models`: `Notification`, `Company`
- `django.utils.timezone`
- `django.db.models`

---

## Functions

### `get_or_create_notification(user, company: Optional[Company], notification_type: str, notification_key: str, message: str, url_name: str, count: int = 1) -> Notification`

**توضیح**: ایجاد یا دریافت یک notification در database

**پارامترهای ورودی**:
- `user`: کاربری که باید notification را دریافت کند
- `company` (Optional[Company]): Company context برای notification
- `notification_type` (str): نوع notification (مثلاً 'approval_pending', 'approved')
- `notification_key` (str): کلید یکتا برای این notification
- `message` (str): متن پیام notification
- `url_name` (str): Django URL name برای redirect
- `count` (int, default=1): تعداد items در این notification

**مقدار بازگشتی**:
- `Notification`: instance notification

**منطق**:
1. **get_or_create**:
   - `Notification.objects.get_or_create(notification_key=notification_key, defaults={...})`
   - **Defaults**:
     - `user`: user
     - `company`: company
     - `notification_type`: notification_type
     - `message`: message
     - `url_name`: url_name
     - `count`: count
     - `is_read`: 0 (unread)
     - `created_by`: user
2. **به‌روزرسانی اگر موجود باشد**:
   - اگر `created = False` (notification از قبل موجود است):
     - بررسی تغییرات: اگر `notification.message != message` یا `notification.count != count`:
       - به‌روزرسانی: `notification.message = message`
       - به‌روزرسانی: `notification.count = count`
       - به‌روزرسانی: `notification.edited_by = user`
       - به‌روزرسانی: `notification.edited_at = timezone.now()`
       - ذخیره: `notification.save(update_fields=['message', 'count', 'edited_by', 'edited_at'])`
3. بازگشت notification instance

**نکات مهم**:
- از `notification_key` برای یکتا بودن استفاده می‌کند
- اگر notification از قبل موجود باشد و message یا count تغییر کرده باشد، به‌روزرسانی می‌شود
- همیشه `is_read=0` (unread) تنظیم می‌شود

---

### `get_unread_notifications(user, company_id: Optional[int]) -> list`

**توضیح**: دریافت unread notifications برای یک user در company context

**پارامترهای ورودی**:
- `user`: کاربری که notifications را دریافت می‌کند
- `company_id` (Optional[int]): Company ID برای فیلتر کردن notifications

**مقدار بازگشتی**:
- `list`: لیست دیکشنری‌های notification برای template context

**منطق**:
1. ساخت queryset:
   - `Notification.objects.filter(user=user, is_read=0).order_by('-created_at')`
2. **فیلتر بر اساس company** (اختیاری):
   - اگر `company_id` موجود باشد:
     - `queryset = queryset.filter(company_id=company_id)`
3. **ساخت notifications list**:
   - برای هر notification در queryset:
     - ساخت dict با:
       - `type`: `notification.notification_type`
       - `key`: `notification.notification_key`
       - `message`: `notification.message`
       - `url`: `notification.url_name`
       - `count`: `notification.count`
       - `id`: `notification.id`
4. بازگشت notifications list

**فرمت هر notification dict**:
```python
{
    'type': str,      # notification_type
    'key': str,       # notification_key
    'message': str,   # message
    'url': str,       # url_name
    'count': int,     # count
    'id': int         # notification.id
}
```

**نکات مهم**:
- فقط unread notifications (`is_read=0`) برگردانده می‌شوند
- مرتب‌سازی: جدیدترین اول (`-created_at`)
- فیلتر company اختیاری است

---

### `get_unread_notification_count(user, company_id: Optional[int]) -> int`

**توضیح**: شمارش unread notifications برای یک user در company context

**پارامترهای ورودی**:
- `user`: کاربری که notifications را شمارش می‌کند
- `company_id` (Optional[int]): Company ID برای فیلتر کردن notifications

**مقدار بازگشتی**:
- `int`: تعداد unread notifications (sum of count fields)

**منطق**:
1. ساخت queryset:
   - `Notification.objects.filter(user=user, is_read=0)`
2. **فیلتر بر اساس company** (اختیاری):
   - اگر `company_id` موجود باشد:
     - `queryset = queryset.filter(company_id=company_id)`
3. **Aggregation**:
   - `queryset.aggregate(total_count=Sum('count'))`
   - بازگشت `result['total_count'] or 0` (اگر None باشد، 0 برمی‌گرداند)

**نکات مهم**:
- از `Sum('count')` استفاده می‌کند (نه `count()`)
- این به این معنی است که اگر یک notification با `count=5` داشته باشیم، 5 شمارش می‌شود (نه 1)
- فیلتر company اختیاری است

---

### `get_recent_notifications(user, company_id: Optional[int], limit: int = 10) -> list`

**توضیح**: دریافت recent notifications (هم read و هم unread) برای یک user در company context

**پارامترهای ورودی**:
- `user`: کاربری که notifications را دریافت می‌کند
- `company_id` (Optional[int]): Company ID برای فیلتر کردن notifications
- `limit` (int, default=10): حداکثر تعداد notifications برای بازگشت

**مقدار بازگشتی**:
- `list`: لیست دیکشنری‌های notification برای template context

**منطق**:
1. ساخت queryset:
   - `Notification.objects.filter(user=user)`
   - **نکته**: فیلتر `is_read` اعمال نمی‌شود (هم read و هم unread)
2. **فیلتر بر اساس company** (اختیاری):
   - اگر `company_id` موجود باشد:
     - `queryset = queryset.filter(company_id=company_id)`
3. **مرتب‌سازی و محدود کردن**:
   - `queryset = queryset.order_by('-created_at')[:limit]`
4. **ساخت notifications list**:
   - برای هر notification در queryset:
     - ساخت dict با:
       - `type`: `notification.notification_type`
       - `key`: `notification.notification_key`
       - `message`: `notification.message`
       - `url`: `notification.url_name`
       - `count`: `notification.count`
       - `id`: `notification.id`
       - `is_read`: `notification.is_read` (1 یا 0)
5. بازگشت notifications list

**فرمت هر notification dict**:
```python
{
    'type': str,      # notification_type
    'key': str,       # notification_key
    'message': str,   # message
    'url': str,       # url_name
    'count': int,     # count
    'id': int,        # notification.id
    'is_read': int    # is_read (1 یا 0)
}
```

**نکات مهم**:
- هم read و هم unread notifications برگردانده می‌شوند
- مرتب‌سازی: جدیدترین اول (`-created_at`)
- محدود به `limit` (default: 10)
- فیلتر company اختیاری است
- شامل `is_read` field (برخلاف `get_unread_notifications`)

---

## تفاوت‌های کلیدی

| Function | Read Status Filter | Returns is_read | Use Case |
|----------|-------------------|-----------------|----------|
| `get_unread_notifications` | فقط unread (`is_read=0`) | ❌ | نمایش فقط unread notifications |
| `get_unread_notification_count` | فقط unread (`is_read=0`) | ❌ | شمارش unread notifications (با sum) |
| `get_recent_notifications` | همه (read + unread) | ✅ | نمایش recent notifications (با read status) |

---

## استفاده در Context Processors

این functions در `shared/context_processors.py` استفاده می‌شوند:
- `get_recent_notifications()`: برای `context['notifications']`
- `get_unread_notification_count()`: برای `context['notification_count']`

---

## نکات مهم

1. **Company Filtering**: تمام functions از `company_id` برای فیلتر کردن استفاده می‌کنند (اختیاری)
2. **Ordering**: تمام functions از `-created_at` برای مرتب‌سازی استفاده می‌کنند (جدیدترین اول)
3. **Count vs Count()**: `get_unread_notification_count` از `Sum('count')` استفاده می‌کند (نه `count()`)
4. **Update Logic**: `get_or_create_notification` notification موجود را به‌روزرسانی می‌کند اگر message یا count تغییر کرده باشد

---

## مثال استفاده

```python
from shared.utils.notifications import (
    get_or_create_notification,
    get_unread_notifications,
    get_unread_notification_count,
    get_recent_notifications
)

# ایجاد notification
notification = get_or_create_notification(
    user=request.user,
    company=company,
    notification_type='approval_pending',
    notification_key=f'approval_pending_purchase_{company_id}',
    message='5 درخواست خرید در انتظار تایید',
    url_name='inventory:purchase_requests',
    count=5
)

# دریافت unread notifications
unread = get_unread_notifications(request.user, company_id)

# شمارش unread notifications
count = get_unread_notification_count(request.user, company_id)

# دریافت recent notifications
recent = get_recent_notifications(request.user, company_id, limit=10)
```
