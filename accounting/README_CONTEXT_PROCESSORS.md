# accounting/context_processors.py - Context Processors (Complete Documentation)

**هدف**: Context processors برای ماژول accounting

این فایل شامل **1 context processor function** است:
- `active_fiscal_year()`: اضافه کردن اطلاعات سال مالی فعال به context تمام template ها

---

## وابستگی‌ها

- `accounting.models`: `FiscalYear`
- `accounting.utils`: `get_available_fiscal_years`
- `jdatetime`: `datetime as jdatetime` (برای تبدیل تاریخ شمسی)
- `django.contrib.auth`: برای بررسی `request.user.is_authenticated`

---

## Context Processors

### `active_fiscal_year(request) -> Dict[str, Any]`

**توضیح**: اضافه کردن اطلاعات سال مالی فعال به template context

**پارامترهای ورودی**:
- `request` (HttpRequest): درخواست HTTP

**مقدار بازگشتی**:
- `Dict[str, Any]`: Context شامل:
  - `active_fiscal_year`: `FiscalYear` object یا `None`
  - `available_fiscal_years`: لیست `FiscalYear` objects

**منطق**:

1. **Initialize Context**:
   - `active_fiscal_year = None`
   - `available_fiscal_years = []`

2. **Authentication Check**:
   - اگر کاربر authenticated نیست، context خالی برمی‌گرداند

3. **Get Active Company**:
   - دریافت `active_company_id` از session
   - اگر وجود نداشت، context خالی برمی‌گرداند

4. **Get Available Fiscal Years**:
   - فراخوانی `get_available_fiscal_years(active_company_id)`
   - تبدیل به لیست و اضافه به context

5. **Get Active Fiscal Year from Session**:
   - دریافت `active_fiscal_year_id` از session
   - اگر وجود داشت، تلاش برای دریافت از دیتابیس
   - بررسی تعلق به شرکت فعال و `is_enabled=1`

6. **Fallback Logic (اگر active_fiscal_year وجود نداشت)**:
   - **اولویت 1**: سال مالی جاری (`is_current=1`)
   - **اولویت 2**: اولین سال مالی از `available_fiscal_years`
   - **اولویت 3**: هر سال مالی enabled (جدیدترین)
   - **اولویت 4**: ایجاد سال مالی پیش‌فرض برای سال جاری شمسی

7. **Create Default Fiscal Year (در صورت عدم وجود)**:
   - دریافت سال جاری شمسی با `jdatetime.now().year`
   - محاسبه `start_date` و `end_date` برای سال شمسی جاری
   - ایجاد `FiscalYear` با:
     - `fiscal_year_code`: سال شمسی جاری
     - `fiscal_year_name`: `'سال مالی {year}'`
     - `is_current=1`, `is_enabled=1`

8. **Save to Session**:
   - ذخیره `active_fiscal_year_id` در session
   - علامت‌گذاری session به عنوان modified

9. **Return Context**:
   - برگرداندن context با `active_fiscal_year` و `available_fiscal_years`

---

## استفاده در پروژه

### تنظیمات Django

این context processor باید در `settings.py` اضافه شود:

```python
TEMPLATES = [
    {
        # ...
        'OPTIONS': {
            'context_processors': [
                # ...
                'accounting.context_processors.active_fiscal_year',
            ],
        },
    },
]
```

### استفاده در Templates

```django
{% if active_fiscal_year %}
    سال مالی فعال: {{ active_fiscal_year.fiscal_year_code }}
{% endif %}

{% for fy in available_fiscal_years %}
    {{ fy.fiscal_year_code }}
{% endfor %}
```

---

## نکات مهم

1. **Auto-Creation**: اگر هیچ سال مالی وجود نداشته باشد، یک سال مالی پیش‌فرض برای سال شمسی جاری ایجاد می‌شود
2. **Session Management**: سال مالی فعال در session ذخیره می‌شود
3. **Company Scoping**: تمام عملیات بر اساس `active_company_id` از session هستند
4. **Priority Order**: ترتیب اولویت برای انتخاب سال مالی فعال مشخص است
5. **Performance**: از `get_available_fiscal_years()` استفاده می‌کند که فقط سال‌های مالی با اسناد را برمی‌گرداند

---

**Last Updated**: 2025-12-02

