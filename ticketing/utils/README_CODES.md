# ticketing/utils/codes.py - Code Generation Utilities

**هدف**: توابع کمکی برای تولید کدهای متوالی برای ماژول Ticketing

این فایل شامل توابعی برای تولید کدهای متوالی برای مدل‌های Ticketing است. علاوه بر تابع عمومی `generate_sequential_code` (مشابه `inventory/utils/codes.py`)، دو تابع خاص نیز دارد که از تاریخ در کد استفاده می‌کنند.

---

## توابع

### `generate_sequential_code(model, *, company_id, field, width, extra_filters) -> str`

**هدف**: تولید کد متوالی عددی برای یک مدل خاص

**پارامترهای ورودی**:
- `model` (Django Model class): مدلی که می‌خواهیم کد برایش تولید کنیم
- `company_id` (Optional[int]): شناسه شرکت (برای scoping)
- `field` (str, default="public_code"): نام فیلدی که کد در آن ذخیره می‌شود
- `width` (int, default=3): عرض کد (تعداد ارقام، با صفر پر می‌شود)
- `extra_filters` (Optional[Dict], default=None): فیلترهای اضافی برای scoping

**مقدار بازگشتی**:
- `str`: کد متوالی تولید شده (مثل "001", "002", ...)

**منطق کار**:
مشابه `inventory/utils/codes.py` - برای جزئیات کامل به آن فایل مراجعه کنید.

**مثال استفاده**:
```python
from ticketing.utils.codes import generate_sequential_code
from ticketing.models import TicketCategory

code = generate_sequential_code(
    TicketCategory,
    company_id=1,
    field="public_code",
    width=3,
)
```

---

### `generate_template_code(company_id) -> str`

**هدف**: تولید کد template با فرمت `TMP-YYYYMMDD-XXXXXX`

**پارامترهای ورودی**:
- `company_id` (Optional[int]): شناسه شرکت (برای scoping)

**مقدار بازگشتی**:
- `str`: کد template (مثل `TMP-20241126-000001`)

**منطق کار**:
1. تاریخ امروز را به فرمت `YYYYMMDD` می‌گیرد (مثل `20241126`)
2. فیلترها را آماده می‌کند (اگر `company_id` داده شده باشد)
3. در یک transaction atomic:
   - آخرین template code که با `TMP-{date_prefix}-` شروع می‌شود را پیدا می‌کند
   - اگر کد موجود باشد، sequence number را از آخرین کد استخراج می‌کند و 1 به آن اضافه می‌کند
   - اگر کد موجود نباشد، از 1 شروع می‌کند
4. کد کاندید را با فرمت `TMP-{date_prefix}-{sequence}` تولید می‌کند (sequence با 6 رقم و صفر پر می‌شود)
5. یک حلقه while برای اطمینان از یکتایی:
   - بررسی می‌کند که آیا این کد قبلاً استفاده شده یا نه
   - اگر استفاده شده باشد، sequence را افزایش می‌دهد و دوباره بررسی می‌کند
   - تا زمانی که یک کد یکتا پیدا شود

**مثال استفاده**:
```python
from ticketing.utils.codes import generate_template_code

code = generate_template_code(company_id=1)
# نتیجه: "TMP-20241126-000001"
# اگر امروز 26 نوامبر 2024 باشد و اولین template باشد
```

**فرمت کد**:
- `TMP`: prefix ثابت برای templates
- `YYYYMMDD`: تاریخ امروز (8 رقم)
- `XXXXXX`: sequence number (6 رقم با صفر پر شده)

**مثال کدها**:
- `TMP-20241126-000001` (اولین template امروز)
- `TMP-20241126-000002` (دومین template امروز)
- `TMP-20241127-000001` (اولین template فردا)

---

### `generate_ticket_code(company_id) -> str`

**هدف**: تولید کد ticket با فرمت `TKT-YYYYMMDD-XXXXXX`

**پارامترهای ورودی**:
- `company_id` (Optional[int]): شناسه شرکت (برای scoping)

**مقدار بازگشتی**:
- `str`: کد ticket (مثل `TKT-20241126-000001`)

**منطق کار**:
1. تاریخ امروز را به فرمت `YYYYMMDD` می‌گیرد (مثل `20241126`)
2. فیلترها را آماده می‌کند (اگر `company_id` داده شده باشد)
3. در یک transaction atomic:
   - آخرین ticket code که با `TKT-{date_prefix}-` شروع می‌شود را پیدا می‌کند
   - اگر کد موجود باشد، sequence number را از آخرین کد استخراج می‌کند و 1 به آن اضافه می‌کند
   - اگر کد موجود نباشد، از 1 شروع می‌کند
4. کد کاندید را با فرمت `TKT-{date_prefix}-{sequence}` تولید می‌کند (sequence با 6 رقم و صفر پر می‌شود)
5. یک حلقه while برای اطمینان از یکتایی:
   - بررسی می‌کند که آیا این کد قبلاً استفاده شده یا نه
   - اگر استفاده شده باشد، sequence را افزایش می‌دهد و دوباره بررسی می‌کند
   - تا زمانی که یک کد یکتا پیدا شود

**مثال استفاده**:
```python
from ticketing.utils.codes import generate_ticket_code

code = generate_ticket_code(company_id=1)
# نتیجه: "TKT-20241126-000001"
# اگر امروز 26 نوامبر 2024 باشد و اولین ticket باشد
```

**فرمت کد**:
- `TKT`: prefix ثابت برای tickets
- `YYYYMMDD`: تاریخ امروز (8 رقم)
- `XXXXXX`: sequence number (6 رقم با صفر پر شده)

**مثال کدها**:
- `TKT-20241126-000001` (اولین ticket امروز)
- `TKT-20241126-000002` (دومین ticket امروز)
- `TKT-20241127-000001` (اولین ticket فردا)

---

## وابستگی‌ها

- `datetime.datetime`: برای دریافت تاریخ امروز
- `django.db.transaction`: برای atomic transactions
- `typing`: برای type hints (Dict, Optional)
- `ticketing.models.TicketTemplate`: برای بررسی کدهای موجود
- `ticketing.models.Ticket`: برای بررسی کدهای موجود

---

## استفاده در پروژه

### در Models

```python
from ticketing.utils.codes import generate_template_code

class TicketTemplate(models.Model):
    template_code = models.CharField(max_length=20, unique=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    
    def save(self, *args, **kwargs):
        if not self.template_code:
            self.template_code = generate_template_code(
                company_id=self.company_id
            )
        super().save(*args, **kwargs)
```

```python
from ticketing.utils.codes import generate_ticket_code

class Ticket(models.Model):
    ticket_code = models.CharField(max_length=20, unique=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    
    def save(self, *args, **kwargs):
        if not self.ticket_code:
            self.ticket_code = generate_ticket_code(
                company_id=self.company_id
            )
        super().save(*args, **kwargs)
```

### در Forms

```python
from ticketing.utils.codes import generate_template_code

class TicketTemplateForm(forms.ModelForm):
    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.template_code:
            instance.template_code = generate_template_code(
                company_id=instance.company_id
            )
        if commit:
            instance.save()
        return instance
```

---

## تفاوت با `inventory/utils/codes.py`

### شباهت‌ها
- هر دو فایل تابع `generate_sequential_code` دارند که منطق یکسانی دارد

### تفاوت‌ها
- `inventory/utils/codes.py`: فقط `generate_sequential_code` دارد (کدهای عددی ساده)
- `ticketing/utils/codes.py`: علاوه بر `generate_sequential_code`، دو تابع خاص نیز دارد:
  - `generate_template_code()`: کدهای template با تاریخ
  - `generate_ticket_code()`: کدهای ticket با تاریخ

### چرا از تاریخ در کد استفاده می‌شود؟
- **قابلیت ردیابی**: می‌توان به راحتی فهمید که یک template یا ticket در چه تاریخی ایجاد شده
- **سازماندهی**: کدها بر اساس تاریخ سازماندهی می‌شوند
- **یکتایی**: با ترکیب تاریخ و sequence، یکتایی کدها تضمین می‌شود

---

## نکات مهم

1. **Transaction Safety**: تمام توابع از `transaction.atomic()` استفاده می‌کنند تا از race condition جلوگیری شود
2. **Date-based Codes**: کدهای template و ticket شامل تاریخ هستند و هر روز از 1 شروع می‌شوند
3. **Uniqueness**: حلقه while اطمینان می‌دهد که کدهای تولید شده یکتا هستند
4. **Company Scoping**: تمام کدها بر اساس `company_id` scope می‌شوند
5. **Zero Padding**: sequence numbers با صفر پر می‌شوند (6 رقم)

---

## فرمت کدها

### Template Code
```
TMP-YYYYMMDD-XXXXXX
```

مثال:
- `TMP-20241126-000001`
- `TMP-20241126-000002`
- `TMP-20241127-000001`

### Ticket Code
```
TKT-YYYYMMDD-XXXXXX
```

مثال:
- `TKT-20241126-000001`
- `TKT-20241126-000002`
- `TKT-20241127-000001`

---

## Performance Considerations

1. **Query Optimization**: Query برای پیدا کردن آخرین کد بهینه است (فقط یک record برمی‌گرداند)
2. **Indexing**: برای عملکرد بهتر، باید index روی `template_code` و `ticket_code` وجود داشته باشد
3. **Transaction Overhead**: استفاده از `transaction.atomic()` ممکن است کمی overhead داشته باشد، اما برای thread safety ضروری است

