# ticketing/utils/ - Utility Functions

این پوشه شامل توابع کمکی (utility functions) برای ماژول ticketing است.

## فایل‌ها

### codes.py

**هدف**: تولید کدهای متوالی برای template و ticket در ماژول ticketing

#### `generate_sequential_code(model, *, company_id, field="public_code", width=3, extra_filters=None) -> str`

**توضیح**: این تابع کد متوالی عددی بعدی را برای یک مدل برمی‌گرداند. مشابه تابع در `inventory/utils/codes.py` است.

**پارامترهای ورودی**:
- `model` (Django Model): مدل Django که می‌خواهیم کد برای آن تولید کنیم
- `company_id` (Optional[int]): شناسه شرکت
- `field` (str, default="public_code"): نام فیلدی که کد در آن ذخیره می‌شود
- `width` (int, default=3): عرض کد (تعداد ارقام)
- `extra_filters` (Optional[Dict], default=None): فیلترهای اضافی

**مقدار بازگشتی**:
- `str`: کد متوالی عددی

**مثال استفاده**:
```python
from ticketing.utils.codes import generate_sequential_code
from ticketing.models import TicketCategory

code = generate_sequential_code(
    TicketCategory,
    company_id=1,
    field="public_code",
    width=3
)
```

---

#### `generate_template_code(company_id: Optional[int]) -> str`

**توضیح**: کد template را به فرمت `TMP-YYYYMMDD-XXXXXX` تولید می‌کند.

**پارامترهای ورودی**:
- `company_id` (Optional[int]): شناسه شرکت (اگر None باشد، فیلتر شرکت اعمال نمی‌شود)

**مقدار بازگشتی**:
- `str`: کد template (مثل `TMP-20241121-000001`)

**فرمت کد**:
- `TMP`: پیشوند ثابت
- `YYYYMMDD`: تاریخ امروز (میلادی)
- `XXXXXX`: شماره متوالی 6 رقمی

**مثال استفاده**:
```python
from ticketing.utils.codes import generate_template_code

template_code = generate_template_code(company_id=1)
# نتیجه: "TMP-20241121-000001"
```

**نکات مهم**:
- از transaction استفاده می‌کند
- کدها بر اساس تاریخ و شرکت محدود می‌شوند
- اگر کد تکراری باشد، شماره بعدی را امتحان می‌کند

---

#### `generate_ticket_code(company_id: Optional[int]) -> str`

**توضیح**: کد ticket را به فرمت `TKT-YYYYMMDD-XXXXXX` تولید می‌کند.

**پارامترهای ورودی**:
- `company_id` (Optional[int]): شناسه شرکت (اگر None باشد، فیلتر شرکت اعمال نمی‌شود)

**مقدار بازگشتی**:
- `str`: کد ticket (مثل `TKT-20241121-000001`)

**فرمت کد**:
- `TKT`: پیشوند ثابت
- `YYYYMMDD`: تاریخ امروز (میلادی)
- `XXXXXX`: شماره متوالی 6 رقمی

**مثال استفاده**:
```python
from ticketing.utils.codes import generate_ticket_code

ticket_code = generate_ticket_code(company_id=1)
# نتیجه: "TKT-20241121-000001"
```

**نکات مهم**:
- از transaction استفاده می‌کند
- کدها بر اساس تاریخ و شرکت محدود می‌شوند
- اگر کد تکراری باشد، شماره بعدی را امتحان می‌کند

---

## وابستگی‌ها

- `django.db.transaction`: برای atomic transactions
- `datetime`: برای تاریخ امروز
- `ticketing.models`: برای مدل‌های TicketTemplate و Ticket

---

## استفاده در پروژه

این توابع در `save()` متدهای مدل‌های `TicketTemplate` و `Ticket` استفاده می‌شوند تا کدهای خودکار تولید شوند.

---

## نکات مهم

1. **Thread Safety**: تمام توابع از transaction استفاده می‌کنند
2. **Date-based Codes**: کدهای template و ticket بر اساس تاریخ هستند
3. **Uniqueness**: اگر کد تکراری باشد، به صورت خودکار شماره بعدی را امتحان می‌کند

