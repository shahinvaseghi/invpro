# inventory/utils/jalali.py - Jalali Date Utilities

**هدف**: توابع کمکی برای تبدیل تاریخ بین تقویم میلادی (Gregorian) و تقویم شمسی (Jalali)

تمام تاریخ‌ها در دیتابیس به صورت میلادی ذخیره می‌شوند، اما در UI به صورت شمسی نمایش داده می‌شوند و کاربران تاریخ را به صورت شمسی وارد می‌کنند.

---

## توابع

### `gregorian_to_jalali(gregorian_date, format_str) -> Optional[str]`

**هدف**: تبدیل تاریخ میلادی به تاریخ شمسی (رشته)

**پارامترهای ورودی**:
- `gregorian_date` (Union[date, datetime, str, None]): تاریخ میلادی
  - می‌تواند `date` object باشد
  - می‌تواند `datetime` object باشد (فقط قسمت date استفاده می‌شود)
  - می‌تواند رشته به فرمت ISO (`YYYY-MM-DD`) باشد
  - می‌تواند `None` باشد
- `format_str` (str, default='%Y/%m/%d'): فرمت خروجی (پیش‌فرض: `1403/09/15`)

**مقدار بازگشتی**:
- `Optional[str]`: تاریخ شمسی به صورت رشته یا `None` اگر ورودی نامعتبر باشد

**منطق کار**:
1. اگر ورودی `None` یا خالی باشد، `None` برمی‌گرداند
2. اگر ورودی رشته باشد، سعی می‌کند آن را به `date` تبدیل کند (با `date.fromisoformat()`)
3. اگر ورودی `datetime` باشد، فقط قسمت `date` را استخراج می‌کند
4. با استفاده از `jdatetime.date.fromgregorian()` تاریخ میلادی را به شمسی تبدیل می‌کند
5. با `strftime(format_str)` تاریخ شمسی را به رشته تبدیل می‌کند

**مثال استفاده**:
```python
from inventory.utils.jalali import gregorian_to_jalali
from datetime import date, datetime

# با date object
result = gregorian_to_jalali(date(2024, 12, 5))
# نتیجه: "1403/09/15"

# با datetime object
result = gregorian_to_jalali(datetime(2024, 12, 5, 10, 30))
# نتیجه: "1403/09/15"

# با رشته ISO
result = gregorian_to_jalali("2024-12-05")
# نتیجه: "1403/09/15"

# با فرمت سفارشی
result = gregorian_to_jalali(date(2024, 12, 5), format_str='%Y-%m-%d')
# نتیجه: "1403-09-15"

# با None
result = gregorian_to_jalali(None)
# نتیجه: None
```

**Error Handling**:
- اگر رشته ورودی فرمت ISO نداشته باشد، `None` برمی‌گرداند
- اگر تبدیل تاریخ نامعتبر باشد، `None` برمی‌گرداند

---

### `jalali_to_gregorian(jalali_date, format_str) -> Optional[date]`

**هدف**: تبدیل تاریخ شمسی (رشته) به تاریخ میلادی (date object)

**پارامترهای ورودی**:
- `jalali_date` (Union[str, None]): تاریخ شمسی به صورت رشته (مثل `'1403/09/15'` یا `'1403-09-15'`)
- `format_str` (str, default='%Y/%m/%d'): فرمت ورودی (پیش‌فرض: `%Y/%m/%d`)

**مقدار بازگشتی**:
- `Optional[date]`: تاریخ میلادی به صورت `date` object یا `None` اگر ورودی نامعتبر باشد

**منطق کار**:
1. اگر ورودی `None` یا خالی باشد، `None` برمی‌گرداند
2. ورودی را strip می‌کند (فاصله‌های اضافی را حذف می‌کند)
3. لیستی از فرمت‌های ممکن را امتحان می‌کند:
   - `%Y/%m/%d` (1403/09/15)
   - `%Y-%m-%d` (1403-09-15)
   - `%Y/%-m/%-d` (1403/9/5 - بدون صفر در ابتدا)
   - `%Y-%-m-%-d` (1403-9-5)
4. اگر ورودی شامل `/` باشد، فرمت‌های با `/` را اول امتحان می‌کند
5. اگر ورودی شامل `-` باشد، فرمت‌های با `-` را اول امتحان می‌کند
6. برای هر فرمت، سعی می‌کند با `jdatetime.datetime.strptime()` parse کند
7. اگر موفق شد، با `togregorian().date()` به تاریخ میلادی تبدیل می‌کند
8. اگر همه فرمت‌ها ناموفق بودند، با `format_str` پیش‌فرض یک بار دیگر امتحان می‌کند

**مثال استفاده**:
```python
from inventory.utils.jalali import jalali_to_gregorian
from datetime import date

# با فرمت پیش‌فرض
result = jalali_to_gregorian('1403/09/15')
# نتیجه: date(2024, 12, 5)

# با فرمت dash
result = jalali_to_gregorian('1403-09-15', '%Y-%m-%d')
# نتیجه: date(2024, 12, 5)

# با اعداد بدون صفر
result = jalali_to_gregorian('1403/9/5')
# نتیجه: date(2024, 12, 5)

# با None
result = jalali_to_gregorian(None)
# نتیجه: None
```

**Error Handling**:
- اگر هیچ فرمتی کار نکند، `None` برمی‌گرداند
- اگر تاریخ نامعتبر باشد (مثل 1403/13/32)، `None` برمی‌گرداند

---

### `get_jalali_date_input_format() -> str`

**هدف**: دریافت فرمت رشته برای input تاریخ شمسی در HTML

**مقدار بازگشتی**:
- `str`: فرمت پیش‌فرض `'%Y/%m/%d'`

**استفاده**:
```python
from inventory.utils.jalali import get_jalali_date_input_format

format_str = get_jalali_date_input_format()
# نتیجه: '%Y/%m/%d'
```

---

### `get_jalali_date_display_format() -> str`

**هدف**: دریافت فرمت رشته برای نمایش تاریخ شمسی در templates

**مقدار بازگشتی**:
- `str`: فرمت پیش‌فرض `'%Y/%m/%d'`

**استفاده**:
```python
from inventory.utils.jalali import get_jalali_date_display_format

format_str = get_jalali_date_display_format()
# نتیجه: '%Y/%m/%d'
```

---

### `today_jalali() -> str`

**هدف**: دریافت تاریخ امروز به صورت شمسی (رشته)

**مقدار بازگشتی**:
- `str`: تاریخ امروز به فرمت `'%Y/%m/%d'` (مثل `'1403/09/15'`)

**منطق کار**:
1. با `jdatetime.date.today()` تاریخ امروز شمسی را می‌گیرد
2. با `strftime('%Y/%m/%d')` به رشته تبدیل می‌کند

**مثال استفاده**:
```python
from inventory.utils.jalali import today_jalali

today = today_jalali()
# نتیجه: '1403/09/15' (بسته به تاریخ امروز)
```

---

### `today_gregorian() -> date`

**هدف**: دریافت تاریخ امروز به صورت میلادی (date object)

**مقدار بازگشتی**:
- `date`: تاریخ امروز میلادی (مثل `date(2024, 12, 5)`)

**منطق کار**:
1. با `jdatetime.date.today()` تاریخ امروز شمسی را می‌گیرد
2. با `togregorian()` به تاریخ میلادی تبدیل می‌کند

**مثال استفاده**:
```python
from inventory.utils.jalali import today_gregorian
from datetime import date

today = today_gregorian()
# نتیجه: date(2024, 12, 5) (بسته به تاریخ امروز)
# معادل با date.today() است
```

---

## وابستگی‌ها

- `jdatetime`: کتابخانه تبدیل تاریخ میلادی به شمسی
- `datetime`: برای type hints و date/datetime objects
- `typing`: برای type hints (Optional, Union)

---

## استفاده در پروژه

### در Forms

```python
from inventory.utils.jalali import jalali_to_gregorian

class ReceiptForm(forms.ModelForm):
    receipt_date = forms.CharField(label='تاریخ رسید')
    
    def clean_receipt_date(self):
        jalali_date = self.cleaned_data['receipt_date']
        gregorian_date = jalali_to_gregorian(jalali_date)
        if not gregorian_date:
            raise forms.ValidationError('تاریخ نامعتبر است')
        return gregorian_date
```

### در Templates

```django
{% load jalali_tags %}

{{ receipt.receipt_date|jalali_date }}
{# نتیجه: 1403/09/15 #}
```

### در Models

```python
from inventory.utils.jalali import gregorian_to_jalali

class Receipt(models.Model):
    receipt_date = models.DateField()
    
    def get_jalali_date(self):
        return gregorian_to_jalali(self.receipt_date)
```

---

## نکات مهم

1. **Database Storage**: تمام تاریخ‌ها در دیتابیس به صورت میلادی ذخیره می‌شوند
2. **UI Display**: تمام تاریخ‌ها در UI به صورت شمسی نمایش داده می‌شوند
3. **Input Handling**: کاربران تاریخ را به صورت شمسی وارد می‌کنند و باید به میلادی تبدیل شود
4. **Format Consistency**: فرمت پیش‌فرض `%Y/%m/%d` است (1403/09/15)
5. **Error Handling**: تمام توابع در صورت خطا `None` برمی‌گردانند (fail-safe)

---

## فرمت‌های پشتیبانی شده

- `%Y/%m/%d`: 1403/09/15 (پیش‌فرض)
- `%Y-%m-%d`: 1403-09-15
- `%Y/%-m/%-d`: 1403/9/5 (بدون صفر در ابتدا)
- `%Y-%-m-%-d`: 1403-9-5

**نکته**: `%-m` و `%-d` برای حذف صفرهای ابتدایی در ماه و روز است (در برخی سیستم‌عامل‌ها ممکن است کار نکند).

