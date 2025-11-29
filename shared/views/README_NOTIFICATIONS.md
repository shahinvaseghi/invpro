# shared/views/notifications.py - Notification Views (Complete Documentation)

**هدف**: Views برای مدیریت notifications در ماژول shared

این فایل شامل views برای:
- NotificationListView: فهرست notifications کاربر با فیلتر read/unread

---

## وابستگی‌ها

- `shared.models`: `Notification`
- `django.contrib.auth.mixins`: `LoginRequiredMixin`
- `django.views.generic`: `ListView`
- `django.utils.translation`: `gettext_lazy`

---

## NotificationListView

**Type**: `LoginRequiredMixin, ListView`

**Template**: `shared/notifications.html`

**Attributes**:
- `model`: `Notification`
- `template_name`: `'shared/notifications.html'`
- `context_object_name`: `'notifications'`
- `paginate_by`: `50`

**متدها**:

### `get_queryset(self) -> QuerySet`

**توضیح**: فیلتر کردن notifications بر اساس user، company، و read status

**مقدار بازگشتی**:
- `QuerySet`: queryset مرتب شده با `-created_at`

**منطق**:
1. دریافت base queryset: `super().get_queryset()`
2. **فیلتر بر اساس user**:
   - `queryset = queryset.filter(user=self.request.user)`
3. **فیلتر بر اساس company** (اختیاری):
   - دریافت `active_company_id` از session: `self.request.session.get('active_company_id')`
   - اگر `company_id` موجود باشد:
     - `queryset = queryset.filter(company_id=company_id)`
4. **فیلتر بر اساس read status**:
   - دریافت `read_filter` از GET parameter: `self.request.GET.get('read', 'all')`
   - اگر `read_filter == 'read'`:
     - `queryset = queryset.filter(is_read=1)`
   - اگر `read_filter == 'unread'`:
     - `queryset = queryset.filter(is_read=0)`
   - اگر `read_filter == 'all'` (default):
     - هیچ فیلتر اضافی اعمال نمی‌شود (همه notifications)
5. مرتب‌سازی: `queryset.order_by('-created_at')` (جدیدترین اول)

**نکات مهم**:
- نیاز به authentication دارد (`LoginRequiredMixin`)
- فقط notifications کاربر فعلی نمایش داده می‌شوند
- فیلتر company اختیاری است (اگر active_company_id در session موجود باشد)
- فیلتر read status از GET parameter: `?read=read`, `?read=unread`, یا `?read=all`

**URL**: `/shared/notifications/`

---

### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`

**توضیح**: اضافه کردن context variables برای template

**پارامترهای ورودی**:
- `**kwargs`: متغیرهای context اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با `read_filter`, `unread_count`, `read_count`

**Context Variables اضافه شده**:
- `read_filter`: مقدار فیلتر read از GET parameter (default: 'all')
- `unread_count`: تعداد notifications خوانده نشده
- `read_count`: تعداد notifications خوانده شده

**منطق**:
1. دریافت `read_filter` از GET parameter: `self.request.GET.get('read', 'all')`
2. اضافه کردن `read_filter` به context
3. **محاسبه counts** (بدون فیلتر read):
   - دریافت base queryset: `super().get_queryset()`
   - فیلتر بر اساس user: `base_queryset.filter(user=self.request.user)`
   - فیلتر بر اساس company (اگر موجود باشد):
     - دریافت `active_company_id` از session
     - اگر موجود باشد: `base_queryset.filter(company_id=company_id)`
   - `unread_count = base_queryset.filter(is_read=0).count()`
   - `read_count = base_queryset.filter(is_read=1).count()`
4. اضافه کردن counts به context

**نکات مهم**:
- Counts بر اساس base queryset (بدون فیلتر read) محاسبه می‌شوند
- این به template اجازه می‌دهد که تعداد کل unread/read را نمایش دهد حتی اگر فیلتر read اعمال شده باشد

---

## نکات مهم

1. **Authentication**: نیاز به login دارد (`LoginRequiredMixin`)
2. **User Filtering**: فقط notifications کاربر فعلی نمایش داده می‌شوند
3. **Company Filtering**: اختیاری - اگر active_company_id در session موجود باشد
4. **Read Status Filter**: از GET parameter `?read=read|unread|all`
5. **Pagination**: 50 item per page
6. **Ordering**: جدیدترین notifications اول (`-created_at`)

---

## الگوهای مشترک

1. **Base View**: از `LoginRequiredMixin` و `ListView` استفاده می‌کند
2. **Session Dependency**: از `active_company_id` در session استفاده می‌کند
3. **GET Parameter Filtering**: از `read` GET parameter برای فیلتر کردن استفاده می‌کند

---

## استفاده در Template

```django
{% for notification in notifications %}
    <div class="notification {% if not notification.is_read %}unread{% endif %}">
        {{ notification.message }}
        <span class="date">{{ notification.created_at|date:"Y-m-d H:i" }}</span>
    </div>
{% endfor %}

<div class="filters">
    <a href="?read=all">All ({{ unread_count|add:read_count }})</a>
    <a href="?read=unread">Unread ({{ unread_count }})</a>
    <a href="?read=read">Read ({{ read_count }})</a>
</div>
```

---

## URL Configuration

```python
from django.urls import path
from shared.views.notifications import NotificationListView

urlpatterns = [
    path('notifications/', NotificationListView.as_view(), name='notification_list'),
]
```
