# shared/utils/email.py - Email Notification Utilities

**هدف**: توابع کمکی برای ارسال ایمیل‌های اعلان از طریق SMTP

این فایل شامل توابعی برای ارسال ایمیل‌های اعلان به کاربران است. از تنظیمات SMTP که در `SMTPServer` مدل ذخیره شده‌اند استفاده می‌کند.

---

## توابع

### `get_active_smtp_server()`

**هدف**: دریافت تنظیمات SMTP فعال (اولین SMTP server که enabled است)

**مقدار بازگشتی**:
- `SMTPServer` object: اگر SMTP server فعالی وجود داشته باشد
- `None`: اگر هیچ SMTP server فعالی وجود نداشته باشد یا خطا رخ دهد

**منطق کار**:
1. از `SMTPServer.objects.filter(is_enabled=1).first()` استفاده می‌کند
2. اولین SMTP server که `is_enabled=1` باشد را برمی‌گرداند
3. اگر خطایی رخ دهد (مثلاً جدول وجود نداشته باشد)، خطا را log می‌کند و `None` برمی‌گرداند

**مثال استفاده**:
```python
from shared.utils.email import get_active_smtp_server

smtp_server = get_active_smtp_server()
if smtp_server:
    print(f"SMTP Host: {smtp_server.host}")
else:
    print("No active SMTP server configured")
```

---

### `send_email_notification(subject, message, recipient_email, recipient_name, html_message) -> bool`

**هدف**: ارسال ایمیل اعلان با استفاده از SMTP server فعال

**پارامترهای ورودی**:
- `subject` (str): موضوع ایمیل
- `message` (str): متن ساده ایمیل
- `recipient_email` (str): آدرس ایمیل گیرنده
- `recipient_name` (Optional[str], default=None): نام گیرنده (اختیاری)
- `html_message` (Optional[str], default=None): متن HTML ایمیل (اختیاری)

**مقدار بازگشتی**:
- `bool`: `True` اگر ایمیل با موفقیت ارسال شود، `False` در غیر این صورت

**منطق کار**:
1. SMTP server فعال را با `get_active_smtp_server()` دریافت می‌کند
2. اگر SMTP server وجود نداشته باشد، warning log می‌کند و `False` برمی‌گرداند
3. اگر `recipient_email` خالی باشد، warning log می‌کند و `False` برمی‌گرداند
4. آدرس فرستنده را آماده می‌کند:
   - اگر `from_name` در SMTP server وجود داشته باشد: `"{from_name} <{from_email}>"`
   - در غیر این صورت: فقط `from_email`
5. یک `MIMEMultipart` message ایجاد می‌کند
6. متن ساده و HTML (اگر وجود داشته باشد) را به message اضافه می‌کند
7. به SMTP server متصل می‌شود:
   - اگر `use_ssl=True`: از `SMTP_SSL` استفاده می‌کند
   - در غیر این صورت: از `SMTP` استفاده می‌کند
8. اگر `use_tls=True` و `use_ssl=False`: `starttls()` را فراخوانی می‌کند
9. اگر username و password وجود داشته باشد: authenticate می‌کند
10. ایمیل را ارسال می‌کند و connection را می‌بندد
11. اگر موفق باشد، info log می‌کند و `True` برمی‌گرداند
12. اگر خطایی رخ دهد، error log می‌کند و `False` برمی‌گرداند

**مثال استفاده**:
```python
from shared.utils.email import send_email_notification

success = send_email_notification(
    subject="Test Email",
    message="This is a test email",
    recipient_email="user@example.com",
    recipient_name="John Doe",
    html_message="<h1>This is a test email</h1>",
)

if success:
    print("Email sent successfully")
else:
    print("Failed to send email")
```

**Error Handling**:
- تمام خطاها catch می‌شوند و در logger ثبت می‌شوند
- در صورت خطا، `False` برمی‌گرداند (fail-safe)

---

### `send_notification_email(notification_type, notification_message, recipient_user, notification_url, company_name) -> bool`

**هدف**: ارسال ایمیل اعلان فرمت‌شده بر اساس نوع اعلان

**پارامترهای ورودی**:
- `notification_type` (str): نوع اعلان (مثل `'approval_pending'`, `'approved'`)
- `notification_message` (str): پیام اعلان
- `recipient_user` (Django User): کاربر گیرنده (باید فیلد `email` داشته باشد)
- `notification_url` (Optional[str], default=None): URL برای لینک در ایمیل (اختیاری)
- `company_name` (Optional[str], default=None): نام شرکت برای context (اختیاری)

**مقدار بازگشتی**:
- `bool`: `True` اگر ایمیل با موفقیت ارسال شود، `False` در غیر این صورت

**منطق کار**:
1. بررسی می‌کند که `recipient_user` و `recipient_user.email` وجود داشته باشند
2. اگر email وجود نداشته باشد، warning log می‌کند و `False` برمی‌گرداند
3. موضوع ایمیل را بر اساس `notification_type` تعیین می‌کند:
   - `'approval_pending'`: "Pending Approval Request"
   - `'approved'`: "Request Approved"
   - سایر موارد: "Notification"
4. اگر `company_name` وجود داشته باشد، به ابتدای subject اضافه می‌کند: `"[{company_name}] {subject}"`
5. یک HTML email body ایجاد می‌کند با:
   - Header با رنگ آبی
   - Content area با پیام
   - دکمه "View Details" (اگر `notification_url` وجود داشته باشد)
   - Footer با پیام خودکار
6. یک plain text version نیز ایجاد می‌کند
7. `send_email_notification()` را فراخوانی می‌کند

**مثال استفاده**:
```python
from shared.utils.email import send_notification_email
from django.contrib.auth.models import User

user = User.objects.get(username='john')
success = send_notification_email(
    notification_type='approval_pending',
    notification_message='5 درخواست خرید در انتظار تایید',
    recipient_user=user,
    notification_url='https://example.com/requests',
    company_name='شرکت نمونه',
)

if success:
    print("Notification email sent")
```

**انواع اعلان‌های پشتیبانی شده**:
- `'approval_pending'`: برای درخواست‌های در انتظار تایید
- `'approved'`: برای درخواست‌های تایید شده

**HTML Template**:
ایمیل HTML شامل:
- Header با پس‌زمینه آبی و عنوان
- Content area با پس‌زمینه خاکستری روشن
- Message box با border آبی
- دکمه "View Details" (اگر URL وجود داشته باشد)
- Footer با پیام خودکار

---

## وابستگی‌ها

- `logging`: برای log کردن خطاها و اطلاعات
- `django.core.mail.EmailMessage`: برای ساخت email message (استفاده نشده، اما import شده)
- `django.conf.settings`: برای تنظیمات Django
- `django.utils.translation.gettext_lazy`: برای ترجمه متن‌ها
- `smtplib`: برای اتصال به SMTP server
- `email.mime.text.MIMEText`: برای ساخت MIME message
- `email.mime.multipart.MIMEMultipart`: برای ساخت multipart message
- `shared.models.SMTPServer`: برای دریافت تنظیمات SMTP

---

## استفاده در پروژه

### در Context Processors

```python
from shared.utils.email import send_notification_email

# در shared/context_processors.py
if pending_approvals > 0:
    send_notification_email(
        notification_type='approval_pending',
        notification_message=f'{pending_approvals} درخواست در انتظار تایید',
        recipient_user=request.user,
        notification_url=reverse('inventory:purchase_requests'),
        company_name=active_company.display_name,
    )
```

### در Views

```python
from shared.utils.email import send_notification_email

class PurchaseRequestApproveView(View):
    def post(self, request, *args, **kwargs):
        # ... approve logic ...
        
        send_notification_email(
            notification_type='approved',
            notification_message='درخواست خرید شما تایید شد',
            recipient_user=request.user,
            notification_url=reverse('inventory:purchase_requests'),
        )
```

---

## نکات مهم

1. **SMTP Configuration**: قبل از استفاده، باید یک `SMTPServer` با `is_enabled=1` در دیتابیس وجود داشته باشد
2. **Error Handling**: تمام خطاها catch می‌شوند و در logger ثبت می‌شوند (fail-safe)
3. **HTML Support**: ایمیل‌ها می‌توانند هم plain text و هم HTML داشته باشند
4. **UTF-8 Encoding**: تمام متن‌ها با encoding UTF-8 ارسال می‌شوند
5. **Rate Limiting**: در context processor، ایمیل‌ها فقط یک بار برای هر اعلان ارسال می‌شوند (بر اساس session)
6. **TLS/SSL Support**: از TLS و SSL پشتیبانی می‌کند (بر اساس تنظیمات SMTP server)

---

## تنظیمات SMTP

برای استفاده از این توابع، باید یک `SMTPServer` در دیتابیس ایجاد کنید:

```python
from shared.models import SMTPServer

smtp = SMTPServer.objects.create(
    name="Gmail SMTP",
    host="smtp.gmail.com",
    port=587,
    username="your-email@gmail.com",
    password="your-password",
    use_tls=True,
    use_ssl=False,
    from_email="your-email@gmail.com",
    from_name="Your Name",
    is_enabled=1,
)
```

**فیلدهای مهم**:
- `host`: آدرس SMTP server
- `port`: پورت SMTP (معمولاً 587 برای TLS، 465 برای SSL)
- `username`: نام کاربری SMTP
- `password`: رمز عبور SMTP
- `use_tls`: استفاده از TLS (برای پورت 587)
- `use_ssl`: استفاده از SSL (برای پورت 465)
- `from_email`: آدرس ایمیل فرستنده
- `from_name`: نام فرستنده (اختیاری)
- `is_enabled`: فعال بودن (1 = فعال، 0 = غیرفعال)

---

## Troubleshooting

### ایمیل ارسال نمی‌شود
1. بررسی کنید که `SMTPServer` با `is_enabled=1` وجود داشته باشد
2. بررسی کنید که `recipient_user.email` خالی نباشد
3. بررسی logs برای خطاهای SMTP
4. بررسی کنید که تنظیمات SMTP (host, port, username, password) درست باشند

### خطای Authentication
- بررسی کنید که username و password درست باشند
- برای Gmail، ممکن است نیاز به "App Password" داشته باشید

### خطای Connection
- بررسی کنید که host و port درست باشند
- بررسی کنید که firewall اجازه اتصال به SMTP server را بدهد
- بررسی کنید که TLS/SSL settings درست باشند

