# shared/context_processors.py - Context Processors

**هدف**: فراهم کردن متغیرهای context که در تمام templates به صورت global در دسترس هستند

Context processors توابعی هستند که در `config/settings.py` در `TEMPLATES['OPTIONS']['context_processors']` ثبت می‌شوند و در هر render template به صورت خودکار فراخوانی می‌شوند.

---

## تابع `active_company(request)`

**توضیح**: اطلاعات شرکت فعال و مجوزهای کاربر را به context اضافه می‌کند.

**پارامترهای ورودی**:
- `request` (HttpRequest): درخواست HTTP Django

**مقدار بازگشتی**:
```python
{
    'active_company': Company or None,      # شرکت فعال
    'user_companies': List[Company],        # لیست شرکت‌های قابل دسترسی کاربر
    'user_feature_permissions': Dict,       # مجوزهای کاربر
    'notifications': List[Dict],            # اعلان‌های کاربر
    'notification_count': int              # تعداد اعلان‌ها
}
```

---

### متغیرهای Context

#### `active_company`

**نوع**: `Company` object یا `None`

**توضیح**: شرکت فعال که کاربر انتخاب کرده است.

**منطق انتخاب** (فقط اگر `request.user.is_authenticated`):
1. **مقداردهی اولیه**: `context['active_company'] = None`
2. **دریافت active_company_id از session**: `active_company_id = request.session.get('active_company_id')`
3. **دریافت user_companies**:
   - `UserCompanyAccess.objects.filter(user=request.user, is_enabled=1).select_related('company')`
   - `context['user_companies'] = [access.company for access in user_accesses]`
4. **تنظیم active_company از session**:
   - اگر `active_company_id` موجود است:
     - جستجو در `user_companies` برای پیدا کردن company با `id == active_company_id`
     - استفاده از `next()` با generator expression و fallback به `None`
     - اگر پیدا نشد: `context['active_company'] = None`
5. **Fallback به default company یا اولین company**:
   - اگر `context['active_company']` موجود نیست و `user_companies` خالی نیست:
     - **اول**: بررسی `request.user.default_company`:
       - اگر `hasattr(request.user, 'default_company')` و `request.user.default_company` موجود است:
         - بررسی دسترسی: اگر `default_company in context['user_companies']`:
           - `context['active_company'] = default_company`
     - **دوم**: اگر هنوز active_company موجود نیست:
       - `context['active_company'] = context['user_companies'][0]` (اولین company)
     - **ذخیره در session**:
       - اگر `context['active_company']` موجود است:
         - `request.session['active_company_id'] = context['active_company'].id`
         - `request.session.modified = True` (برای اطمینان از ذخیره session)

**مثال استفاده در template**:
```django
{% if active_company %}
  <h1>{{ active_company.display_name }}</h1>
{% endif %}
```

---

#### `user_companies`

**نوع**: `List[Company]`

**توضیح**: لیست تمام شرکت‌هایی که کاربر به آن‌ها دسترسی دارد.

**منطق**:
- از `UserCompanyAccess.objects.filter(user=request.user, is_enabled=1).select_related('company')` خوانده می‌شود
- فقط شرکت‌هایی که کاربر دسترسی دارد (`is_enabled=1`) را شامل می‌شود
- استفاده از `select_related('company')` برای بهینه‌سازی query

**مثال استفاده در template**:
```django
<select name="company_id">
  {% for company in user_companies %}
    <option value="{{ company.id }}" 
            {% if active_company.id == company.id %}selected{% endif %}>
      {{ company.display_name }}
    </option>
  {% endfor %}
</select>
```

---

#### `user_feature_permissions`

**نوع**: `Dict[str, FeaturePermissionState]`

**توضیح**: دیکشنری مجوزهای کاربر برای features مختلف.

**منطق**:
- دریافت `company_id` از `context['active_company'].id` (اگر موجود باشد) یا `None`
- فراخوانی `get_user_feature_permissions(request.user, company_id)`
- ذخیره در `context['user_feature_permissions']`

**فرمت کلید**: Feature code با `.` به `__` تبدیل شده (مثل `inventory__receipts__permanent`)

**فرمت مقدار**: `FeaturePermissionState` object با:
- `view_scope`: `"none"`, `"own"`, یا `"all"`
- `can_view`: `bool`
- `actions`: `Dict[str, bool]` (مثل `{"create": True, "approve": False}`)

**مثال استفاده در template**:
```django
{% load access_tags %}

{% if user_feature_permissions|feature_allowed:"inventory.receipts.permanent:create" %}
  <a href="{% url 'inventory:receipt_permanent_create' %}">Create</a>
{% endif %}
```

---

#### `notifications`

**نوع**: `List[Dict]`

**توضیح**: لیست اعلان‌های کاربر که هنوز خوانده نشده‌اند.

**فرمت هر اعلان**:
```python
{
    'type': str,              # 'approval_pending' یا 'approved'
    'key': str,               # کلید یکتا برای اعلان
    'message': str,           # پیام اعلان
    'url': str,               # URL name برای لینک
    'count': int              # تعداد موارد
}
```

**انواع اعلان‌ها**:

1. **Approval Pending**:
   - درخواست‌های خرید در انتظار تایید
   - درخواست‌های انبار در انتظار تایید
   - اسناد شمارش در انتظار تایید
   - کلید: `approval_pending_{type}_{company_id}`

2. **Approved**:
   - درخواست‌های خرید کاربر که تایید شده‌اند (7 روز اخیر)
   - درخواست‌های انبار کاربر که تایید شده‌اند (7 روز اخیر)
   - کلید: `approved_{type}_{company_id}`

**مثال استفاده در template**:
```django
{% if notification_count > 0 %}
  <div class="notifications">
    {% for notification in notifications %}
      <div class="notification">
        <a href="{% url notification.url %}">{{ notification.message }}</a>
      </div>
    {% endfor %}
  </div>
{% endif %}
```

---

#### `notification_count`

**نوع**: `int`

**توضیح**: تعداد کل اعلان‌های خوانده نشده.

**مثال استفاده در template**:
```django
{% if notification_count > 0 %}
  <span class="badge">{{ notification_count }}</span>
{% endif %}
```

---

### منطق Notifications

**شرایط اجرا**: فقط اگر `request.user.is_authenticated` و `company_id` موجود باشد

**مراحل**:
1. **مقداردهی اولیه**:
   - `context['notifications'] = []`
   - `context['notification_count'] = 0`
   - دریافت `sent_email_notifications` از session (set، fallback به empty set)

2. **Approval Pending Notifications** (3 نوع):

   **a. Purchase Requests**:
   - Query: `PurchaseRequest.objects.filter(company_id=company_id, status=DRAFT, approver=request.user, is_enabled=1).count()`
   - Notification key: `f'approval_pending_purchase_{company_id}'`
   - Message: `f'{count} درخواست خرید در انتظار تایید'`
   - URL name: `'inventory:purchase_requests'`
   - اگر count > 0:
     - `get_or_create_notification()` فراخوانی می‌شود
     - اگر notification_key در `sent_email_notifications` نیست:
       - ساخت notification_url با `request.build_absolute_uri(reverse('inventory:purchase_requests'))`
       - `send_notification_email()` فراخوانی می‌شود
       - اگر موفق بود: notification_key به `sent_email_notifications` اضافه می‌شود
       - `request.session['sent_email_notifications'] = list(sent_email_notifications)` ذخیره می‌شود
       - Error handling: اگر exception رخ دهد، در logger ثبت می‌شود

   **b. Warehouse Requests**:
   - Query: `WarehouseRequest.objects.filter(company_id=company_id, request_status='draft', approver=request.user, is_enabled=1).count()`
   - Notification key: `f'approval_pending_warehouse_{company_id}'`
   - Message: `f'{count} درخواست انبار در انتظار تایید'`
   - URL name: `'inventory:warehouse_requests'`
   - منطق مشابه Purchase Requests

   **c. Stocktaking Records**:
   - Query: `StocktakingRecord.objects.filter(company_id=company_id, approval_status='pending', approver=request.user, is_locked=0, is_enabled=1).count()`
   - Notification key: `f'approval_pending_stocktaking_{company_id}'`
   - Message: `f'{count} سند شمارش در انتظار تایید'`
   - URL name: `'inventory:stocktaking_records'`
   - منطق مشابه Purchase Requests

3. **Approved Notifications** (2 نوع - فقط 7 روز اخیر):

   **a. Approved Purchase Requests**:
   - `week_ago = timezone.now() - timezone.timedelta(days=7)`
   - Query: `PurchaseRequest.objects.filter(company_id=company_id, requested_by=request.user, status=APPROVED, approved_at__gte=week_ago, is_enabled=1).count()`
   - Notification key: `f'approved_purchase_{company_id}'`
   - Message: `f'{count} درخواست خرید شما تایید شد'`
   - URL name: `'inventory:purchase_requests'`
   - منطق مشابه Approval Pending (با email notification)

   **b. Approved Warehouse Requests**:
   - Query: `WarehouseRequest.objects.filter(company_id=company_id, requester=request.user, request_status='approved', approved_at__gte=week_ago, is_enabled=1).count()`
   - Notification key: `f'approved_warehouse_{company_id}'`
   - Message: `f'{count} درخواست انبار شما تایید شد'`
   - URL name: `'inventory:warehouse_requests'`
   - منطق مشابه Approved Purchase Requests

4. **دریافت Recent Notifications از Database**:
   - `context['notifications'] = get_recent_notifications(request.user, company_id, limit=10)`
   - `context['notification_count'] = get_unread_notification_count(request.user, company_id)`

#### ایمیل‌های ارسال شده (Sent Email Notifications)

- در `request.session['sent_email_notifications']` ذخیره می‌شوند
- Set از کلیدهای اعلان‌ها (strings)
- برای جلوگیری از ارسال ایمیل تکراری استفاده می‌شود
- فقط یک بار برای هر اعلان ایمیل ارسال می‌شود
- اگر session value یک set نیست، به empty set تبدیل می‌شود
- بعد از ارسال موفق، به list تبدیل شده و در session ذخیره می‌شود

#### ارسال ایمیل

- به صورت خودکار برای اعلان‌های approval pending و approved ارسال می‌شود
- از `shared.utils.email.send_notification_email()` استفاده می‌کند
- Parameters:
  - `notification_type`: `'approval_pending'` یا `'approved'`
  - `notification_message`: پیام اعلان
  - `recipient_user`: `request.user`
  - `notification_url`: absolute URL ساخته شده با `request.build_absolute_uri()`
  - `company_name`: `context['active_company'].display_name` (اگر موجود باشد)
- Error handling: اگر exception رخ دهد، در logger ثبت می‌شود (با `exc_info=True`)

---

### Session Storage

Context processor از session برای ذخیره اطلاعات استفاده می‌کند:

- `active_company_id`: شناسه شرکت فعال
- `read_notifications`: لیست کلیدهای اعلان‌های خوانده شده
- `sent_email_notifications`: Set کلیدهای اعلان‌هایی که ایمیل ارسال شده

---

## وابستگی‌ها

- `shared.models`: `UserCompanyAccess`, `Company`
- `shared.utils.permissions`: `get_user_feature_permissions`
- `shared.utils.email`: `send_notification_email`
- `inventory.models`: برای اعلان‌های approval

---

## استفاده در پروژه

این context processor در `config/settings.py` ثبت شده است:

```python
TEMPLATES = [
    {
        'OPTIONS': {
            'context_processors': [
                # ...
                'shared.context_processors.active_company',
            ],
        },
    },
]
```

---

## نکات مهم

1. **Performance**: این تابع برای هر request اجرا می‌شود، بنابراین باید بهینه باشد
2. **Caching**: Notifications در session cache می‌شوند
3. **Email Rate Limiting**: ایمیل‌ها فقط یک بار برای هر اعلان ارسال می‌شوند
4. **Permission Resolution**: مجوزها برای هر request حل می‌شوند (cached نیستند)

