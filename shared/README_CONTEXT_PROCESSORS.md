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

**منطق انتخاب**:
1. ابتدا از `request.session['active_company_id']` خوانده می‌شود
2. اگر در session نباشد، از `user.default_company` استفاده می‌شود
3. اگر default company هم نباشد، اولین شرکت از `user_companies` استفاده می‌شود
4. اگر شرکت فعال پیدا شود، در session ذخیره می‌شود

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
- از `UserCompanyAccess` با `is_enabled=1` خوانده می‌شود
- فقط شرکت‌هایی که کاربر دسترسی دارد را شامل می‌شود

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

#### خوانده شده‌ها (Read Notifications)

- در `request.session['read_notifications']` ذخیره می‌شوند
- لیستی از کلیدهای اعلان‌ها (strings)
- وقتی کاربر روی اعلان کلیک می‌کند، کلید به این لیست اضافه می‌شود

#### ایمیل‌های ارسال شده (Sent Email Notifications)

- در `request.session['sent_email_notifications']` ذخیره می‌شوند
- Set از کلیدهای اعلان‌ها
- برای جلوگیری از ارسال ایمیل تکراری استفاده می‌شود
- فقط یک بار برای هر اعلان ایمیل ارسال می‌شود

#### ارسال ایمیل

- به صورت خودکار برای اعلان‌های pending approval ارسال می‌شود
- از `shared.utils.email.send_notification_email()` استفاده می‌کند
- فقط اگر کاربر فیلد `email` داشته باشد
- فقط یک بار برای هر اعلان (بر اساس کلید)

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

