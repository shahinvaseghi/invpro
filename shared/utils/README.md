# shared/utils/ - Utility Functions

این پوشه شامل توابع کمکی (utility functions) برای ماژول shared است که در سراسر پروژه استفاده می‌شوند.

## فایل‌ها

### modules.py

**هدف**: بررسی نصب بودن ماژول‌های اختیاری و دریافت مدل‌های آن‌ها

#### `is_production_installed() -> bool`

**توضیح**: بررسی می‌کند که آیا ماژول production نصب شده است یا نه.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `bool`: `True` اگر ماژول production نصب باشد، `False` در غیر این صورت

**مثال استفاده**:
```python
from shared.utils.modules import is_production_installed

if is_production_installed():
    # کد مربوط به production
    pass
```

---

#### `is_qc_installed() -> bool`

**توضیح**: بررسی می‌کند که آیا ماژول QC نصب شده است یا نه.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `bool`: `True` اگر ماژول QC نصب باشد، `False` در غیر این صورت

**مثال استفاده**:
```python
from shared.utils.modules import is_qc_installed

if is_qc_installed():
    # کد مربوط به QC
    pass
```

---

#### `get_work_line_model()`

**توضیح**: مدل `WorkLine` را از ماژول production برمی‌گرداند (اگر نصب باشد).

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `WorkLine` (Model class): کلاس مدل WorkLine اگر production نصب باشد
- `None`: اگر production نصب نباشد یا import خطا دهد

**مثال استفاده**:
```python
from shared.utils.modules import get_work_line_model

WorkLine = get_work_line_model()
if WorkLine:
    work_lines = WorkLine.objects.filter(company_id=1)
```

---

#### `get_person_model()`

**توضیح**: مدل `Person` را از ماژول production برمی‌گرداند (اگر نصب باشد).

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `Person` (Model class): کلاس مدل Person اگر production نصب باشد
- `None`: اگر production نصب نباشد یا import خطا دهد

**مثال استفاده**:
```python
from shared.utils.modules import get_person_model

Person = get_person_model()
if Person:
    persons = Person.objects.filter(company_id=1)
```

---

### permissions.py

**هدف**: توابع کمکی برای بررسی و حل مجوزهای کاربر

این فایل شامل توابع پیچیده‌ای است که مجوزهای کاربر را بر اساس AccessLevel و AccessLevelPermission حل می‌کند. برای جزئیات کامل، به مستندات `shared/permissions.py` و `docs/BASE_CLASSES_MIXINS.md` مراجعه کنید.

**توابع اصلی**:
- `get_user_feature_permissions(user, company_id)`: مجوزهای کاربر را برمی‌گرداند
- `has_feature_permission(permissions, feature_code, action)`: بررسی می‌کند که آیا کاربر مجوز دارد یا نه

---

### email.py

**هدف**: توابع ارسال ایمیل از طریق SMTP

#### `get_active_smtp_server()`

**توضیح**: اولین سرور SMTP فعال را برمی‌گرداند.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `SMTPServer` (Model instance): اولین سرور SMTP با `is_enabled=1`
- `None`: اگر هیچ سرور فعالی وجود نداشته باشد

**مثال استفاده**:
```python
from shared.utils.email import get_active_smtp_server

smtp = get_active_smtp_server()
if smtp:
    print(f"Using SMTP: {smtp.host}")
```

---

#### `send_email_notification(subject, message, recipient_email, recipient_name=None, html_message=None) -> bool`

**توضیح**: یک ایمیل اعلان را از طریق سرور SMTP فعال ارسال می‌کند.

**پارامترهای ورودی**:
- `subject` (str): موضوع ایمیل
- `message` (str): متن ساده ایمیل
- `recipient_email` (str): آدرس ایمیل گیرنده
- `recipient_name` (Optional[str], default=None): نام گیرنده (اختیاری)
- `html_message` (Optional[str], default=None): متن HTML ایمیل (اختیاری)

**مقدار بازگشتی**:
- `bool`: `True` اگر ایمیل با موفقیت ارسال شود، `False` در غیر این صورت

**مثال استفاده**:
```python
from shared.utils.email import send_email_notification

success = send_email_notification(
    subject="تایید درخواست",
    message="درخواست شما تایید شد.",
    recipient_email="user@example.com",
    recipient_name="کاربر",
    html_message="<h1>درخواست شما تایید شد.</h1>"
)
```

**نکات مهم**:
- اگر سرور SMTP فعالی وجود نداشته باشد، `False` برمی‌گرداند
- از SSL/TLS پشتیبانی می‌کند
- اگر `html_message` ارائه شود، ایمیل به صورت HTML ارسال می‌شود

---

#### `send_notification_email(notification_type, notification_message, recipient_user, notification_url=None, company_name=None) -> bool`

**توضیح**: یک ایمیل اعلان فرمت‌شده را بر اساس نوع اعلان ارسال می‌کند.

**پارامترهای ورودی**:
- `notification_type` (str): نوع اعلان (مثل 'approval_pending', 'approved')
- `notification_message` (str): پیام اعلان
- `recipient_user` (User): شیء کاربر Django (باید فیلد email داشته باشد)
- `notification_url` (Optional[str], default=None): لینک به صفحه مربوطه (اختیاری)
- `company_name` (Optional[str], default=None): نام شرکت برای اضافه کردن به موضوع (اختیاری)

**مقدار بازگشتی**:
- `bool`: `True` اگر ایمیل با موفقیت ارسال شود، `False` در غیر این صورت

**مثال استفاده**:
```python
from shared.utils.email import send_notification_email
from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.get(username='testuser')

success = send_notification_email(
    notification_type='approval_pending',
    notification_message='3 درخواست خرید در انتظار تایید',
    recipient_user=user,
    notification_url='https://example.com/requests/',
    company_name='شرکت نمونه'
)
```

**نکات مهم**:
- اگر کاربر فیلد `email` نداشته باشد، `False` برمی‌گرداند
- ایمیل به صورت HTML و Plain Text ارسال می‌شود
- موضوع ایمیل بر اساس `notification_type` تعیین می‌شود

---

## وابستگی‌ها

- `django.apps.apps`: برای بررسی نصب بودن ماژول‌ها
- `django.core.mail`: برای ارسال ایمیل
- `smtplib`: برای اتصال به سرور SMTP
- `jdatetime`: برای تاریخ شمسی (در برخی موارد)

---

## استفاده در پروژه

این توابع در سراسر پروژه استفاده می‌شوند:
- **modules.py**: در views و forms برای بررسی نصب بودن ماژول‌های اختیاری
- **permissions.py**: در context processors و template tags برای بررسی مجوزها
- **email.py**: در context processors برای ارسال اعلان‌های ایمیل

---

## نکات مهم

1. **Optional Dependencies**: توابع `modules.py` برای ماژول‌های اختیاری طراحی شده‌اند
2. **Error Handling**: تمام توابع ایمیل در صورت خطا `False` برمی‌گردانند و خطا را log می‌کنند
3. **SMTP Configuration**: سرور SMTP باید از طریق مدل `SMTPServer` پیکربندی شود

