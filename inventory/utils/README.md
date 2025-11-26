# inventory/utils/ - Utility Functions

این پوشه شامل توابع کمکی (utility functions) برای ماژول inventory است.

## فایل‌ها

### codes.py

**هدف**: تولید کدهای متوالی عددی برای مدل‌های مختلف

#### `generate_sequential_code(model, *, company_id, field="public_code", width=3, extra_filters=None)`

**توضیح**: این تابع کد متوالی عددی بعدی را برای یک مدل برمی‌گرداند. کد بر اساس company و فیلترهای اضافی (مثل category/warehouse) محدود می‌شود.

**پارامترهای ورودی**:
- `model` (Django Model): مدل Django که می‌خواهیم کد برای آن تولید کنیم
- `company_id` (Optional[int]): شناسه شرکت (اگر None باشد، فیلتر شرکت اعمال نمی‌شود)
- `field` (str, default="public_code"): نام فیلدی که کد در آن ذخیره می‌شود
- `width` (int, default=3): عرض کد (تعداد ارقام، با صفر پر می‌شود)
- `extra_filters` (Optional[Dict], default=None): فیلترهای اضافی برای محدود کردن دامنه کد (مثل `{"category_id": 1}`)

**مقدار بازگشتی**:
- `str`: کد متوالی عددی (مثل "001", "002", "123")

**مثال استفاده**:
```python
from inventory.utils.codes import generate_sequential_code
from inventory.models import ItemType

# تولید کد برای ItemType در یک شرکت
code = generate_sequential_code(
    ItemType,
    company_id=1,
    field="public_code",
    width=3
)
# نتیجه: "001" یا "002" یا ...

# تولید کد با فیلتر اضافی
code = generate_sequential_code(
    ItemCategory,
    company_id=1,
    field="public_code",
    width=3,
    extra_filters={"type_id": 1}  # فقط برای یک نوع خاص
)
```

**نکات مهم**:
- از transaction استفاده می‌کند تا از race condition جلوگیری شود
- اگر آخرین کد عددی نباشد، از 1 شروع می‌کند
- اگر کد تکراری باشد، به صورت خودکار عدد بعدی را امتحان می‌کند
- اگر مدل فیلد `company` داشته باشد، به صورت خودکار فیلتر می‌شود

---

### jalali.py

**هدف**: تبدیل تاریخ بین تقویم میلادی (Gregorian) و شمسی (Jalali)

#### `gregorian_to_jalali(gregorian_date, format_str='%Y/%m/%d')`

**توضیح**: تاریخ میلادی را به تاریخ شمسی تبدیل می‌کند.

**پارامترهای ورودی**:
- `gregorian_date` (Union[date, datetime, str, None]): تاریخ میلادی (می‌تواند date، datetime، یا رشته ISO باشد)
- `format_str` (str, default='%Y/%m/%d'): فرمت خروجی (مثل '%Y/%m/%d' برای 1403/09/15)

**مقدار بازگشتی**:
- `Optional[str]`: رشته تاریخ شمسی یا None اگر ورودی نامعتبر باشد

**مثال استفاده**:
```python
from inventory.utils.jalali import gregorian_to_jalali
from datetime import date

# تبدیل تاریخ میلادی به شمسی
jalali_str = gregorian_to_jalali(date(2024, 12, 5))
# نتیجه: "1403/09/15"

# با فرمت سفارشی
jalali_str = gregorian_to_jalali(date(2024, 12, 5), '%Y-%m-%d')
# نتیجه: "1403-09-15"

# از رشته ISO
jalali_str = gregorian_to_jalali('2024-12-05')
# نتیجه: "1403/09/15"
```

---

#### `jalali_to_gregorian(jalali_date, format_str='%Y/%m/%d')`

**توضیح**: تاریخ شمسی را به تاریخ میلادی تبدیل می‌کند.

**پارامترهای ورودی**:
- `jalali_date` (Union[str, None]): رشته تاریخ شمسی (مثل '1403/09/15' یا '1403-09-15')
- `format_str` (str, default='%Y/%m/%d'): فرمت ورودی (در صورت نیاز)

**مقدار بازگشتی**:
- `Optional[date]`: شیء date میلادی یا None اگر ورودی نامعتبر باشد

**مثال استفاده**:
```python
from inventory.utils.jalali import jalali_to_gregorian

# تبدیل تاریخ شمسی به میلادی
gregorian_date = jalali_to_gregorian('1403/09/15')
# نتیجه: date(2024, 12, 5)

# با فرمت مختلف
gregorian_date = jalali_to_gregorian('1403-09-15', '%Y-%m-%d')
# نتیجه: date(2024, 12, 5)
```

**نکات مهم**:
- چندین فرمت را به صورت خودکار امتحان می‌کند
- از `/` و `-` به عنوان جداکننده پشتیبانی می‌کند
- اگر همه فرمت‌ها ناموفق باشند، None برمی‌گرداند

---

#### `get_jalali_date_input_format() -> str`

**توضیح**: فرمت تاریخ شمسی برای ورودی HTML را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: فرمت رشته (همیشه '%Y/%m/%d')

**مثال استفاده**:
```python
from inventory.utils.jalali import get_jalali_date_input_format

format_str = get_jalali_date_input_format()
# نتیجه: "%Y/%m/%d"
```

---

#### `get_jalali_date_display_format() -> str`

**توضیح**: فرمت تاریخ شمسی برای نمایش در templates را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: فرمت رشته (همیشه '%Y/%m/%d')

**مثال استفاده**:
```python
from inventory.utils.jalali import get_jalali_date_display_format

format_str = get_jalali_date_display_format()
# نتیجه: "%Y/%m/%d"
```

---

#### `today_jalali() -> str`

**توضیح**: تاریخ امروز را به صورت رشته شمسی برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: تاریخ امروز به فرمت 'YYYY/MM/DD' (مثل '1403/09/15')

**مثال استفاده**:
```python
from inventory.utils.jalali import today_jalali

today = today_jalali()
# نتیجه: "1403/09/15" (تاریخ امروز)
```

---

#### `today_gregorian() -> date`

**توضیح**: تاریخ امروز را به صورت date میلادی برمی‌گرداند (معادل `date.today()`).

**مقدار بازگشتی**:
- `date`: تاریخ امروز میلادی

**مثال استفاده**:
```python
from inventory.utils.jalali import today_gregorian
from datetime import date

today = today_gregorian()
# نتیجه: date(2024, 12, 5) (تاریخ امروز)
```

---

## وابستگی‌ها

- `jdatetime`: کتابخانه تبدیل تاریخ شمسی (نصب: `pip install jdatetime`)
- `django.db.transaction`: برای atomic transactions در تولید کد

---

## استفاده در پروژه

این توابع در سراسر پروژه استفاده می‌شوند:
- **codes.py**: در `save()` متدهای مدل‌ها برای تولید کدهای خودکار
- **jalali.py**: در forms برای تبدیل تاریخ ورودی کاربر، در templates برای نمایش تاریخ، و در views برای پردازش تاریخ

---

## نکات مهم

1. **Thread Safety**: `generate_sequential_code` از transaction استفاده می‌کند تا از race condition جلوگیری شود
2. **Error Handling**: تمام توابع تاریخ در صورت خطا `None` برمی‌گردانند
3. **Format Support**: توابع تاریخ از چندین فرمت پشتیبانی می‌کنند

