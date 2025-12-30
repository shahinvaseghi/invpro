# shared/templatetags/generic_tags.py - Generic Template Tags

**هدف**: Template tags عمومی برای templateهای قابل استفاده مجدد

این فایل شامل template tags زیر است:
- `getattr` filter - دریافت attribute از object با پشتیبانی از nested attributes
- `get_field_value` filter - دریافت field value از object با dot notation

---

## Template Tags

### `getattr` Filter

**نام**: `getattr`

**نوع**: Filter

**توضیح**: دریافت attribute از object، با پشتیبانی از nested attributes

**پارامترهای ورودی**:
- `obj`: Object برای دریافت attribute
- `attr`: نام attribute (می‌تواند nested باشد مثل `"type.name"`)

**مقدار بازگشتی**:
- Attribute value یا `None` اگر پیدا نشود

**منطق**:
1. اگر `obj` وجود نداشته باشد، `None` برمی‌گرداند
2. اگر `attr` شامل `'.'` باشد (nested attribute):
   - `attr` را به parts تقسیم می‌کند
   - برای هر part:
     - اگر object دارای attribute باشد، آن را دریافت می‌کند
     - اگر object دارای `__getitem__` باشد (dictionary-like)، آن را از dictionary دریافت می‌کند
     - اگر `None` باشد، `None` برمی‌گرداند
   - مقدار نهایی را برمی‌گرداند
3. در غیر این صورت (simple attribute):
   - اگر object دارای attribute باشد، آن را دریافت می‌کند
   - اگر object دارای `__getitem__` باشد (dictionary-like)، آن را از dictionary دریافت می‌کند
   - در غیر این صورت، `None` برمی‌گرداند
4. اگر exception رخ دهد (`AttributeError`, `TypeError`, `KeyError`)، `None` برمی‌گرداند

**استفاده در template**:
```django
{{ object|getattr:"field_name" }}
{{ object|getattr:"nested.field" }}
{{ object|getattr:"type.name" }}
```

**مثال**:
```django
{# Simple attribute #}
{{ item|getattr:"name" }}

{# Nested attribute #}
{{ item|getattr:"category.name" }}

{# Dictionary access #}
{{ data|getattr:"key" }}
```

---

### `get_field_value` Filter

**نام**: `get_field_value`

**نوع**: Filter

**توضیح**: دریافت field value از object با dot notation

این filter مشابه `getattr` است اما با error handling بهتر.

**پارامترهای ورودی**:
- `obj`: Object برای دریافت field value
- `field_path`: مسیر field با dot notation (مثلاً `"type.name"`)

**مقدار بازگشتی**:
- Field value یا `None` اگر پیدا نشود

**منطق**:
1. `get_attr()` را با `obj` و `field_path` فراخوانی می‌کند
2. نتیجه را برمی‌گرداند

**استفاده در template**:
```django
{{ object|get_field_value:"type.name" }}
{{ object|get_field_value:"category.parent.name" }}
```

**مثال**:
```django
{# Nested field access #}
{{ item|get_field_value:"type.name" }}

{# Deep nested access #}
{{ item|get_field_value:"category.parent.name" }}
```

---

## وابستگی‌ها

- `django.template`: `template`, `register`

---

## استفاده در پروژه

### استفاده در Templates

```django
{% load generic_tags %}

{# Simple attribute access #}
<div>{{ item|getattr:"name" }}</div>

{# Nested attribute access #}
<div>{{ item|getattr:"category.name" }}</div>
<div>{{ item|get_field_value:"type.category.name" }}</div>

{# Dictionary access #}
<div>{{ data|getattr:"key" }}</div>
<div>{{ config|getattr:"settings.value" }}</div>

{# Safe access with None handling #}
{% if item|getattr:"category.name" %}
    <span>{{ item|getattr:"category.name" }}</span>
{% endif %}
```

### استفاده در Generic Templates

```django
{# Generic list template #}
{% load generic_tags %}

<table>
    <thead>
        <tr>
            <th>Name</th>
            <th>Category</th>
            <th>Type</th>
        </tr>
    </thead>
    <tbody>
        {% for item in object_list %}
            <tr>
                <td>{{ item|getattr:"name" }}</td>
                <td>{{ item|getattr:"category.name" }}</td>
                <td>{{ item|getattr:"type.name" }}</td>
            </tr>
        {% endfor %}
    </tbody>
</table>
```

---

## نکات مهم

1. **Nested Attributes**: هر دو filter از nested attributes با dot notation پشتیبانی می‌کنند (مثلاً `"type.name"`)

2. **Dictionary Support**: هر دو filter از dictionary-like objects پشتیبانی می‌کنند با استفاده از `__getitem__`

3. **Error Handling**: هر دو filter به صورت graceful با exceptions برخورد می‌کنند و `None` برمی‌گردانند

4. **None Safety**: اگر object یا attribute `None` باشد، filter `None` برمی‌گرداند بدون exception

5. **Flexibility**: `getattr` filter می‌تواند برای هر نوع object استفاده شود (models, dictionaries, custom objects)

6. **Template Safety**: استفاده از این filters در templates امن است و باعث crash نمی‌شود

7. **Performance**: این filters برای استفاده در loops مناسب هستند و overhead کمی دارند

8. **Compatibility**: این filters با Django template system کاملاً سازگار هستند
