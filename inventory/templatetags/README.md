# inventory/templatetags/ - Template Tags

این پوشه شامل template tags و filters سفارشی برای ماژول inventory است.

## فایل‌ها

### jalali_tags.py

**هدف**: تبدیل تاریخ میلادی به شمسی برای نمایش در templates

این فایل شامل فیلترهای template برای تبدیل تاریخ‌های میلادی (Gregorian) به تاریخ‌های شمسی (Jalali) است.

---

## Filters

### `@register.filter(name='jalali_date')`

**تابع**: `jalali_date(value, format_str='%Y/%m/%d')`

**توضیح**: تاریخ میلادی را به رشته تاریخ شمسی تبدیل می‌کند.

**پارامترهای ورودی**:
- `value`: تاریخ میلادی (date, datetime, یا رشته ISO)
- `format_str` (optional): فرمت خروجی (default: `'%Y/%m/%d'`)

**مقدار بازگشتی**:
- `str`: رشته تاریخ شمسی (مثل `'1403/09/15'`) یا رشته خالی اگر ورودی None/invalid باشد

**مثال استفاده در template**:
```django
{% load jalali_tags %}

{{ receipt.document_date|jalali_date }}
{# نتیجه: "1403/09/15" #}

{{ receipt.document_date|jalali_date:"%Y-%m-%d" }}
{# نتیجه: "1403-09-15" #}
```

**نکات مهم**:
- به صورت خودکار `datetime` objects را به `date` تبدیل می‌کند
- برای `None` یا تاریخ‌های نامعتبر، رشته خالی برمی‌گرداند
- از کتابخانه `jdatetime` برای تبدیل استفاده می‌کند

---

### `@register.filter(name='jalali_date_short')`

**تابع**: `jalali_date_short(value)`

**توضیح**: تاریخ شمسی را به فرمت کوتاه برمی‌گرداند (معادل `jalali_date` با فرمت پیش‌فرض).

**پارامترهای ورودی**:
- `value`: تاریخ میلادی

**مقدار بازگشتی**:
- `str`: تاریخ شمسی به فرمت `YYYY/MM/DD`

**مثال استفاده در template**:
```django
{% load jalali_tags %}

{{ receipt.document_date|jalali_date_short }}
{# نتیجه: "1403/09/15" #}
```

---

### `@register.filter(name='jalali_date_long')`

**تابع**: `jalali_date_long(value)`

**توضیح**: تاریخ شمسی را به فرمت بلند با نام ماه فارسی برمی‌گرداند.

**پارامترهای ورودی**:
- `value`: تاریخ میلادی

**مقدار بازگشتی**:
- `str`: تاریخ شمسی با نام ماه (مثل `'15 آذر 1403'`)

**مثال استفاده در template**:
```django
{% load jalali_tags %}

{{ receipt.document_date|jalali_date_long }}
{# نتیجه: "15 آذر 1403" #}
```

**نام ماه‌ها**:
- فروردین, اردیبهشت, خرداد, تیر, مرداد, شهریور
- مهر, آبان, آذر, دی, بهمن, اسفند

---

### `@register.filter(name='jalali_datetime')`

**تابع**: `jalali_datetime(value, format_str='%Y/%m/%d %H:%M')`

**توضیح**: datetime میلادی را به رشته datetime شمسی تبدیل می‌کند (شامل زمان).

**پارامترهای ورودی**:
- `value`: datetime میلادی
- `format_str` (optional): فرمت خروجی (default: `'%Y/%m/%d %H:%M'`)

**مقدار بازگشتی**:
- `str`: رشته datetime شمسی (مثل `'1403/09/15 14:30'`)

**مثال استفاده در template**:
```django
{% load jalali_tags %}

{{ serial.created_at|jalali_datetime }}
{# نتیجه: "1403/09/15 14:30" #}

{{ serial.created_at|jalali_datetime:"%Y/%m/%d %H:%M:%S" }}
{# نتیجه: "1403/09/15 14:30:45" #}
```

**نکات مهم**:
- هم date و هم time را استخراج می‌کند
- زمان به صورت 24 ساعته باقی می‌ماند
- اگر value یک date باشد (نه datetime)، فقط قسمت date تبدیل می‌شود

---

## وابستگی‌ها

- `django.template`: برای ثبت filters
- `jdatetime`: برای تبدیل تاریخ شمسی
- `inventory.utils.jalali`: برای توابع تبدیل تاریخ

---

## استفاده در پروژه

این filters در تمام templates استفاده می‌شوند:

```django
{% load jalali_tags %}

<table>
  <tr>
    <td>{{ receipt.document_date|jalali_date_long }}</td>
    <td>{{ receipt.created_at|jalali_datetime }}</td>
  </tr>
</table>
```

---

## نکات مهم

1. **Loading Tags**: باید ابتدا `{% load jalali_tags %}` را در template فراخوانی کنید
2. **Error Handling**: تمام filters در صورت خطا رشته خالی برمی‌گردانند
3. **Performance**: تبدیل تاریخ سریع است و cache نمی‌شود

