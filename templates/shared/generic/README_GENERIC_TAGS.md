# shared/templatetags/generic_tags.py - Generic Template Tags

**هدف**: این فایل شامل template tags helper برای استفاده در template‌های generic است.

---

## توابع

### `getattr`

**نوع**: Template Filter

**توضیح**: دریافت attribute از object با پشتیبانی از nested attributes (مثل `type.name`)

**استفاده**:
```django
{% load generic_tags %}

{{ object|getattr:"field_name" }}
{{ object|getattr:"nested.field" }}
{{ object|getattr:"type.name" }}
```

**پارامترها**:
- `obj`: Object که attribute از آن خوانده می‌شود
- `attr`: نام attribute (می‌تواند nested باشد با `.`)

**مقدار بازگشتی**:
- مقدار attribute یا `None` در صورت خطا

**منطق**:
1. بررسی می‌کند که object موجود باشد
2. اگر attribute شامل `.` باشد (nested):
   - attribute را به parts تقسیم می‌کند
   - به صورت recursive از هر part استفاده می‌کند
   - از `hasattr` و `__getitem__` برای dictionary access پشتیبانی می‌کند
3. اگر attribute ساده باشد:
   - از `hasattr` استفاده می‌کند
   - یا از `__getitem__` برای dictionary access

**مثال‌ها**:
```django
{# Simple attribute #}
{{ item|getattr:"name" }}

{# Nested attribute #}
{{ item|getattr:"type.name" }}

{# Dictionary access #}
{{ data|getattr:"key" }}

{# Nested dictionary #}
{{ data|getattr:"parent.child" }}
```

**Error Handling**:
- در صورت خطا (AttributeError, TypeError, KeyError)، `None` برمی‌گرداند
- هیچ exception throw نمی‌کند

---

### `get_field_value`

**نوع**: Template Filter

**توضیح**: Alias برای `getattr` با نام واضح‌تر

**استفاده**:
```django
{% load generic_tags %}

{{ object|get_field_value:"type.name" }}
```

**پارامترها**:
- `obj`: Object
- `field_path`: مسیر فیلد (با dot notation)

**مقدار بازگشتی**:
- مقدار attribute یا `None`

**نکته**: این تابع فقط یک wrapper برای `getattr` است و همان منطق را دارد.

---

## وابستگی‌ها

### Django
- `django.template`: برای تعریف template tags

---

## استفاده در پروژه

این template tags در template‌های generic استفاده می‌شوند:
- `generic_list.html`: برای دسترسی به nested attributes در `table_headers`
- سایر template‌ها که نیاز به دسترسی به nested attributes دارند

**مثال استفاده در generic_list.html**:
```django
{% load generic_tags %}

{% for header in table_headers %}
  {% with value=object|getattr:header.field %}
    {{ value }}
  {% endwith %}
{% endfor %}
```

---

## نکات مهم

1. **Nested Attributes**: برای دسترسی به فیلدهای nested (مثل `type.name`)، از dot notation استفاده کنید.

2. **Dictionary Support**: این تابع از dictionary access نیز پشتیبانی می‌کند.

3. **Error Handling**: در صورت خطا، `None` برمی‌گرداند و exception throw نمی‌کند.

4. **Performance**: برای دسترسی‌های مکرر، بهتر است داده‌ها را در view آماده کنید تا از template tag استفاده نکنید.

---

## استفاده در پروژه

این template tags برای تمام template‌های generic ضروری هستند و باید در template‌هایی که از nested attributes استفاده می‌کنند، load شوند.

