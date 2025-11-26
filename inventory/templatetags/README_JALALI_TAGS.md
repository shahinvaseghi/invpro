# inventory/templatetags/jalali_tags.py - Jalali Date Template Tags

**هدف**: Template tags برای نمایش تاریخ‌های شمسی (Jalali) در templates

این فایل شامل فیلترهای template برای تبدیل و نمایش تاریخ‌های میلادی به شمسی در templates است.

---

## فیلترها

### `jalali_date`

**هدف**: تبدیل تاریخ میلادی به تاریخ شمسی (رشته)

**استفاده در template**:
```django
{% load jalali_tags %}

{{ receipt.document_date|jalali_date }}
{{ receipt.document_date|jalali_date:"%Y/%m/%d" }}
{{ receipt.document_date|jalali_date:"%d %B %Y" }}
```

**پارامترهای ورودی**:
- `value`: تاریخ میلادی (date یا datetime object)
- `format_str` (optional, default='%Y/%m/%d'): فرمت خروجی

**مقدار بازگشتی**:
- `str`: تاریخ شمسی به صورت رشته یا رشته خالی اگر ورودی نامعتبر باشد

**منطق کار**:
1. اگر `value` خالی باشد، رشته خالی برمی‌گرداند
2. اگر `value` یک `datetime` باشد، فقط قسمت `date` را استخراج می‌کند
3. اگر `value` یک `date` نباشد، همان مقدار را برمی‌گرداند (بدون تغییر)
4. از `gregorian_to_jalali()` برای تبدیل استفاده می‌کند
5. اگر تبدیل موفق باشد، رشته شمسی را برمی‌گرداند، در غیر این صورت رشته خالی

**مثال استفاده**:
```django
{% load jalali_tags %}

<p>تاریخ رسید: {{ receipt.document_date|jalali_date }}</p>
{# نتیجه: تاریخ رسید: 1403/09/15 #}

<p>تاریخ با فرمت سفارشی: {{ receipt.document_date|jalali_date:"%Y-%m-%d" }}</p>
{# نتیجه: تاریخ با فرمت سفارشی: 1403-09-15 #}
```

---

### `jalali_date_short`

**هدف**: نمایش تاریخ شمسی با فرمت کوتاه (1403/09/15)

**استفاده در template**:
```django
{% load jalali_tags %}

{{ receipt.document_date|jalali_date_short }}
```

**پارامترهای ورودی**:
- `value`: تاریخ میلادی (date یا datetime object)

**مقدار بازگشتی**:
- `str`: تاریخ شمسی با فرمت `%Y/%m/%d` (مثل `1403/09/15`)

**منطق کار**:
- یک wrapper برای `jalali_date` با فرمت پیش‌فرض `%Y/%m/%d`

**مثال استفاده**:
```django
{% load jalali_tags %}

<p>تاریخ: {{ receipt.document_date|jalali_date_short }}</p>
{# نتیجه: تاریخ: 1403/09/15 #}
```

---

### `jalali_date_long`

**هدف**: نمایش تاریخ شمسی با فرمت بلند (15 آذر 1403)

**استفاده در template**:
```django
{% load jalali_tags %}

{{ receipt.document_date|jalali_date_long }}
```

**پارامترهای ورودی**:
- `value`: تاریخ میلادی (date یا datetime object)

**مقدار بازگشتی**:
- `str`: تاریخ شمسی با فرمت بلند (مثل `15 آذر 1403`)

**منطق کار**:
1. اگر `value` خالی باشد، رشته خالی برمی‌گرداند
2. اگر `value` یک `datetime` باشد، فقط قسمت `date` را استخراج می‌کند
3. اگر `value` یک `date` نباشد، همان مقدار را برمی‌گرداند
4. تاریخ میلادی را به شمسی تبدیل می‌کند
5. نام ماه شمسی را از لیست فارسی استخراج می‌کند
6. فرمت نهایی: `{day} {month_name} {year}`

**لیست نام ماه‌های شمسی**:
```python
['', 'فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور',
 'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند']
```

**مثال استفاده**:
```django
{% load jalali_tags %}

<p>تاریخ: {{ receipt.document_date|jalali_date_long }}</p>
{# نتیجه: تاریخ: 15 آذر 1403 #}
```

**Error Handling**:
- اگر تبدیل تاریخ خطا بدهد، تاریخ شمسی با فرمت کوتاه را برمی‌گرداند

---

### `jalali_datetime`

**هدف**: تبدیل datetime میلادی به datetime شمسی (با زمان)

**استفاده در template**:
```django
{% load jalali_tags %}

{{ serial.created_at|jalali_datetime }}
{{ serial.created_at|jalali_datetime:"%Y/%m/%d %H:%M:%S" }}
```

**پارامترهای ورودی**:
- `value`: datetime میلادی (datetime object)
- `format_str` (optional, default='%Y/%m/%d %H:%M'): فرمت خروجی

**مقدار بازگشتی**:
- `str`: datetime شمسی به صورت رشته (مثل `1403/09/15 14:30`)

**منطق کار**:
1. اگر `value` خالی باشد، رشته خالی برمی‌گرداند
2. اگر `value` یک `datetime` باشد:
   - قسمت `date` را استخراج می‌کند و به شمسی تبدیل می‌کند
   - قسمت `time` را استخراج می‌کند و با فرمت `%H:%M` نمایش می‌دهد
   - نتیجه: `{jalali_date} {time}`
3. اگر `value` یک `date` باشد، فقط قسمت تاریخ را تبدیل می‌کند
4. در غیر این صورت، همان مقدار را برمی‌گرداند

**مثال استفاده**:
```django
{% load jalali_tags %}

<p>زمان ایجاد: {{ serial.created_at|jalali_datetime }}</p>
{# نتیجه: زمان ایجاد: 1403/09/15 14:30 #}

<p>زمان با ثانیه: {{ serial.created_at|jalali_datetime:"%Y/%m/%d %H:%M:%S" }}</p>
{# نتیجه: زمان با ثانیه: 1403/09/15 14:30:45 #}
```

---

## وابستگی‌ها

- `django.template`: برای ساخت template tags
- `datetime.date`, `datetime.datetime`: برای type checking
- `inventory.utils.jalali.gregorian_to_jalali`: برای تبدیل تاریخ
- `jdatetime`: برای تبدیل تاریخ (در `jalali_date_long`)

---

## استفاده در پروژه

### در Templates

```django
{% load jalali_tags %}

<div class="receipt-details">
    <h2>جزئیات رسید</h2>
    <p><strong>کد رسید:</strong> {{ receipt.document_code }}</p>
    <p><strong>تاریخ رسید:</strong> {{ receipt.document_date|jalali_date }}</p>
    <p><strong>تاریخ بلند:</strong> {{ receipt.document_date|jalali_date_long }}</p>
    <p><strong>زمان ایجاد:</strong> {{ receipt.created_at|jalali_datetime }}</p>
</div>
```

### در List Views

```django
{% load jalali_tags %}

<table>
    <thead>
        <tr>
            <th>کد</th>
            <th>تاریخ</th>
            <th>زمان ایجاد</th>
        </tr>
    </thead>
    <tbody>
        {% for receipt in receipts %}
        <tr>
            <td>{{ receipt.document_code }}</td>
            <td>{{ receipt.document_date|jalali_date_short }}</td>
            <td>{{ receipt.created_at|jalali_datetime }}</td>
        </tr>
        {% endfor %}
    </tbody>
</table>
```

---

## فرمت‌های پشتیبانی شده

### فرمت تاریخ
- `%Y/%m/%d`: 1403/09/15 (پیش‌فرض)
- `%Y-%m-%d`: 1403-09-15
- `%d %B %Y`: 15 آذر 1403 (فقط در `jalali_date_long`)

### فرمت زمان
- `%H:%M`: 14:30 (پیش‌فرض در `jalali_datetime`)
- `%H:%M:%S`: 14:30:45

---

## نکات مهم

1. **Auto-loading**: باید `{% load jalali_tags %}` در ابتدای template استفاده شود
2. **Type Safety**: فیلترها type checking انجام می‌دهند و در صورت خطا، مقدار اصلی را برمی‌گردانند
3. **Null Handling**: تمام فیلترها با `None` یا خالی به درستی کار می‌کنند (رشته خالی برمی‌گردانند)
4. **Performance**: تبدیل تاریخ سریع است و برای استفاده در templates مناسب است
5. **Consistency**: تمام فیلترها از `gregorian_to_jalali()` استفاده می‌کنند برای consistency

---

## تفاوت بین فیلترها

| فیلتر | فرمت خروجی | مثال |
|-------|------------|------|
| `jalali_date` | قابل تنظیم (پیش‌فرض: `%Y/%m/%d`) | `1403/09/15` |
| `jalali_date_short` | `%Y/%m/%d` | `1403/09/15` |
| `jalali_date_long` | `{day} {month_name} {year}` | `15 آذر 1403` |
| `jalali_datetime` | `{date} {time}` | `1403/09/15 14:30` |

---

## مثال‌های کامل

```django
{% load jalali_tags %}

<div class="document-card">
    <h3>{{ document.document_code }}</h3>
    
    <div class="dates">
        <p>
            <span class="label">تاریخ سند:</span>
            <span class="value">{{ document.document_date|jalali_date_long }}</span>
        </p>
        
        <p>
            <span class="label">تاریخ ایجاد:</span>
            <span class="value">{{ document.created_at|jalali_datetime }}</span>
        </p>
        
        {% if document.edited_at %}
        <p>
            <span class="label">آخرین ویرایش:</span>
            <span class="value">{{ document.edited_at|jalali_datetime }}</span>
        </p>
        {% endif %}
    </div>
</div>
```

