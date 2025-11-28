# shared/forms/smtp_server.py - SMTP Server Forms (Complete Documentation)

**هدف**: Forms برای مدیریت SMTP Server configurations در ماژول shared

این فایل شامل **1 Form Class**:
- `SMTPServerForm`: Form برای ایجاد و ویرایش SMTP server configurations

---

## وابستگی‌ها

- `shared.models`: `SMTPServer`
- `django.forms`
- `django.utils.translation`: `gettext_lazy`

---

## SMTPServerForm

**Type**: `forms.ModelForm`

**Model**: `SMTPServer`

**توضیح**: Form برای ایجاد و ویرایش SMTP server configurations.

**Fields**:
- `name`: نام server
- `host`: SMTP host (hostname یا IP)
- `port`: SMTP port (1-65535)
- `use_tls`: استفاده از TLS encryption
- `use_ssl`: استفاده از SSL encryption
- `username`: نام کاربری SMTP
- `password`: رمز عبور SMTP
- `from_email`: آدرس ایمیل پیش‌فرض sender
- `from_name`: نام پیش‌فرض sender
- `timeout`: timeout اتصال (1-300 seconds)
- `description`: توضیحات
- `is_enabled`: وضعیت

**Widgets**:
- Text inputs برای name, host, username, from_email, from_name
- NumberInput برای port (min: 1, max: 65535) و timeout (min: 1, max: 300)
- Select برای use_tls, use_ssl, is_enabled
- PasswordInput برای password (autocomplete: new-password)
- Textarea برای description (3 rows)

**Labels**:
- تمام labels با `gettext_lazy` ترجمه شده‌اند

**Help Texts**:
- Help texts برای تمام fields با `gettext_lazy` ترجمه شده‌اند
- شامل توضیحات مفصل برای هر field

**متدها**:

#### `__init__(self, *args, **kwargs)`

**توضیح**: Initialize form و make password optional برای updates.

**منطق**:
- اگر instance موجود باشد (editing):
  - تنظیم `password.required = False`

**نکات مهم**:
- Password در create mode الزامی است
- Password در update mode optional است (اگر تغییر نکند، حفظ می‌شود)

---

#### `clean(self) -> dict`

**توضیح**: Validate form data.

**مقدار بازگشتی**:
- `dict`: cleaned_data

**منطق**:
1. فراخوانی `super().clean()` برای validation اولیه
2. **TLS/SSL validation**:
   - دریافت `use_tls` و `use_ssl` از cleaned_data
   - اگر `use_tls == 1` و `use_ssl == 1`:
     - raise `ValidationError(_('Cannot use both TLS and SSL. Choose one.'))`
   - نمی‌توان همزمان از TLS و SSL استفاده کرد
3. **Password validation**:
   - اگر instance جدید است (`not self.instance.pk`) و password موجود نیست:
     - Add error به `password` field: `_('Password is required for new SMTP server configurations.')`
   - Password برای new instances الزامی است
4. بازگشت cleaned_data

**نکات مهم**:
- TLS و SSL نمی‌توانند همزمان enabled باشند
- Password برای new instances الزامی است
- Password برای updates optional است (در view level handle می‌شود)

---

## نکات مهم

### 1. Password Handling
- در create: password الزامی است
- در update: password optional است
- اگر password در update خالی باشد، password موجود حفظ می‌شود (در view level)

### 2. TLS/SSL Validation
- نمی‌توان همزمان از TLS و SSL استفاده کرد
- معمولاً TLS برای port 587 و SSL برای port 465 استفاده می‌شود

### 3. Port Ranges
- Port: 1-65535
- Timeout: 1-300 seconds

### 4. Help Texts
- Help texts مفصل برای تمام fields
- شامل مثال‌ها و توضیحات (مثلاً port numbers)

---

## استفاده در پروژه

### در Views
```python
from shared.forms import SMTPServerForm

form = SMTPServerForm(request.POST, instance=smtp_server)
if form.is_valid():
    smtp_server = form.save()
    # Password handling در view level انجام می‌شود
```

---

## ارتباط با سایر ماژول‌ها

### Shared Models
- از `SMTPServer` model استفاده می‌کند

### Shared Views
- در `shared/views/smtp_server.py` استفاده می‌شود
- Password handling در `SMTPServerUpdateView` انجام می‌شود

### Shared Utils
- SMTP servers در `shared.utils.email` برای ارسال email استفاده می‌شوند

