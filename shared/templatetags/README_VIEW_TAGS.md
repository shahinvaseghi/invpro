# shared/templatetags/view_tags.py - View Template Tags

**هدف**: Template tags برای عملیات مربوط به view

این فایل شامل template tags زیر است:
- `get_breadcrumbs` tag - تولید لیست breadcrumbs
- `get_table_headers` tag - تولید لیست table headers
- `can_action` tag - بررسی اینکه آیا کاربر می‌تواند action را انجام دهد
- `get_object_actions` tag - دریافت actions موجود برای object
- `get_item` filter - دریافت item از dictionary با key

---

## Template Tags

### `get_breadcrumbs` Tag

**نام**: `get_breadcrumbs`

**نوع**: Simple tag

**takes_context**: `False`

**توضیح**: تولید لیست breadcrumbs با prefix ماژول

**پارامترهای ورودی**:
- `module_name`: نام ماژول (مثلاً `'inventory'`, `'production'`)
- `items`: لیست dictionaries با کلیدهای `'label'` و `'url'`

**مقدار بازگشتی**:
- `List[Dict[str, Optional[str]]]`: لیست breadcrumb dictionaries با کلیدهای `'label'` و `'url'`

**منطق**:
1. `get_breadcrumbs_helper()` را از `shared.utils.view_helpers` فراخوانی می‌کند
2. نتیجه را برمی‌گرداند

**استفاده در template**:
```django
{% load view_tags %}

{% get_breadcrumbs 'inventory' breadcrumb_items as breadcrumbs %}
{% for crumb in breadcrumbs %}
    {% if crumb.url %}
        <a href="{{ crumb.url }}">{{ crumb.label }}</a>
    {% else %}
        <span>{{ crumb.label }}</span>
    {% endif %}
{% endfor %}
```

---

### `get_table_headers` Tag

**نام**: `get_table_headers`

**نوع**: Simple tag

**takes_context**: `False`

**توضیح**: تولید لیست table headers از field definitions

**پارامترهای ورودی**:
- `fields`: لیست field names یا dictionaries با کلیدهای `'label'` و `'field'`

**مقدار بازگشتی**:
- `List[Dict[str, Any]]`: لیست header dictionaries با کلیدهای `'label'` و `'field'`

**منطق**:
1. `get_table_headers_helper()` را از `shared.utils.view_helpers` فراخوانی می‌کند
2. نتیجه را برمی‌گرداند

**استفاده در template**:
```django
{% load view_tags %}

{% get_table_headers table_fields as headers %}
<table>
    <thead>
        <tr>
            {% for header in headers %}
                <th>{{ header.label }}</th>
            {% endfor %}
        </tr>
    </thead>
    <tbody>
        {% for item in object_list %}
            <tr>
                {% for header in headers %}
                    <td>{{ item|getattr:header.field }}</td>
                {% endfor %}
            </tr>
        {% endfor %}
    </tbody>
</table>
```

---

### `can_action` Tag

**نام**: `can_action`

**نوع**: Simple tag

**takes_context**: `True`

**توضیح**: بررسی اینکه آیا کاربر می‌تواند action را روی object انجام دهد

**پارامترهای ورودی**:
- `object`: Model instance
- `action`: نام action (`'view'`, `'edit'`, `'delete'`, `'add'`, etc.)
- `feature_code`: Feature code برای permission check (اختیاری)

**مقدار بازگشتی**:
- `bool`: `True` اگر action مجاز باشد، در غیر این صورت `False`

**منطق**:
1. `request` را از context دریافت می‌کند
2. اگر `request` یا `request.user` وجود نداشته باشد، `False` برمی‌گرداند
3. اگر کاربر superuser باشد، `True` برمی‌گرداند
4. اگر object دارای `get_available_actions()` method باشد:
   - available actions را دریافت می‌کند
   - بررسی می‌کند که action در available actions باشد
5. اگر `feature_code` ارائه شده باشد:
   - user permissions را با `get_user_feature_permissions()` دریافت می‌کند
   - action name را به permission action map می‌کند:
     - `'view'` → `'view_own'`
     - `'edit'` → `'edit_own'`
     - `'delete'` → `'delete_own'`
     - `'add'` → `'create'`
   - resource owner را از object دریافت می‌کند (`created_by`, `owner`, یا `user`)
   - permission را با `has_feature_permission()` بررسی می‌کند
6. در غیر این صورت (fallback):
   - Django permissions را بررسی می‌کند
   - permission name را از app_label و model_name ایجاد می‌کند
   - `user.has_perm()` را بررسی می‌کند
7. نتیجه را برمی‌گرداند

**استفاده در template**:
```django
{% load view_tags %}

{% can_action object 'edit' feature_code as can_edit %}
{% if can_edit %}
    <a href="{% url 'inventory:item_edit' object.pk %}">Edit</a>
{% endif %}

{% can_action object 'delete' feature_code as can_delete %}
{% if can_delete %}
    <a href="{% url 'inventory:item_delete' object.pk %}">Delete</a>
{% endif %}
```

---

### `get_object_actions` Tag

**نام**: `get_object_actions`

**نوع**: Simple tag

**takes_context**: `True`

**توضیح**: دریافت actions موجود برای object

**پارامترهای ورودی**:
- `object`: Model instance
- `feature_code`: Feature code برای permission check (اختیاری)

**مقدار بازگشتی**:
- `List[Dict[str, Any]]`: لیست action dictionaries با کلیدهای `'name'`, `'label'`, `'url'`, `'class'`

**منطق**:
1. `request` را از context دریافت می‌کند
2. اگر `request` یا `request.user` وجود نداشته باشد، لیست خالی برمی‌گرداند
3. اگر object دارای `get_available_actions()` method باشد:
   - available action names را دریافت می‌کند
   - برای هر action name:
     - action info dictionary را ایجاد می‌کند
     - URL را از common URL patterns پیدا می‌کند
     - action را به لیست اضافه می‌کند
   - لیست actions را برمی‌گرداند
4. در غیر این صورت (default actions):
   - default actions را تعریف می‌کند: `[('view', ...), ('edit', ...), ('delete', ...)]`
   - برای هر action:
     - permission را با `can_action()` بررسی می‌کند
     - اگر مجاز باشد، URL را پیدا می‌کند و action را اضافه می‌کند
   - لیست actions را برمی‌گرداند

**استفاده در template**:
```django
{% load view_tags %}

{% get_object_actions object feature_code as actions %}
{% for action in actions %}
    <a href="{{ action.url }}" class="{{ action.class }}">
        {{ action.label }}
    </a>
{% endfor %}
```

---

### `get_item` Filter

**نام**: `get_item`

**نوع**: Filter

**توضیح**: دریافت item از dictionary با key

**پارامترهای ورودی**:
- `dictionary`: Dictionary برای دریافت item
- `key`: Key برای lookup

**مقدار بازگشتی**:
- Value از dictionary یا `None`

**منطق**:
1. اگر `dictionary` یک dictionary نباشد، `None` برمی‌گرداند
2. `dictionary.get(key)` را برمی‌گرداند

**استفاده در template**:
```django
{% load view_tags %}

{{ stats_labels|get_item:'total' }}
{{ config|get_item:'setting' }}
```

---

## وابستگی‌ها

- `django.template`: `template`, `register`
- `django.urls`: `reverse`
- `django.utils.translation`: `gettext_lazy as _`
- `shared.utils.view_helpers`: `get_breadcrumbs`, `get_table_headers`
- `shared.utils.permissions`: `get_user_feature_permissions`, `has_feature_permission`
- `typing`: `List`, `Dict`, `Any`, `Optional`

---

## استفاده در پروژه

### استفاده در Generic Templates

```django
{% load view_tags %}

{# Breadcrumbs #}
{% get_breadcrumbs 'inventory' breadcrumb_items as breadcrumbs %}
<nav>
    {% for crumb in breadcrumbs %}
        {% if crumb.url %}
            <a href="{{ crumb.url }}">{{ crumb.label }}</a>
        {% else %}
            <span>{{ crumb.label }}</span>
        {% endif %}
    {% endfor %}
</nav>

{# Table headers #}
{% get_table_headers table_fields as headers %}
<table>
    <thead>
        <tr>
            {% for header in headers %}
                <th>{{ header.label }}</th>
            {% endfor %}
        </tr>
    </thead>
</table>

{# Permission checks #}
{% can_action object 'edit' feature_code as can_edit %}
{% if can_edit %}
    <a href="{% url 'app:edit' object.pk %}">Edit</a>
{% endif %}

{# Object actions #}
{% get_object_actions object feature_code as actions %}
<div class="actions">
    {% for action in actions %}
        <a href="{{ action.url }}" class="btn {{ action.class }}">
            {{ action.label }}
        </a>
    {% endfor %}
</div>

{# Dictionary access #}
{{ stats|get_item:'total' }}
```

---

## نکات مهم

1. **Context Access**: `can_action` و `get_object_actions` از `takes_context=True` استفاده می‌کنند تا به `request` دسترسی داشته باشند

2. **Permission System**: این tags از سیستم permission پروژه استفاده می‌کنند (`get_user_feature_permissions`, `has_feature_permission`)

3. **Superuser Bypass**: اگر کاربر superuser باشد، تمام actions مجاز هستند

4. **URL Pattern Matching**: `get_object_actions` سعی می‌کند URL را از common URL patterns پیدا کند

5. **Fallback Permissions**: اگر `feature_code` ارائه نشود، از Django permissions استفاده می‌شود

6. **Action Mapping**: `can_action` action names را به permission actions map می‌کند (`'view'` → `'view_own'`, etc.)

7. **Resource Owner**: `can_action` resource owner را از object دریافت می‌کند (`created_by`, `owner`, یا `user`)

8. **Helper Functions**: `get_breadcrumbs` و `get_table_headers` از helper functions در `shared.utils.view_helpers` استفاده می‌کنند

9. **Error Handling**: تمام tags به صورت graceful با missing data برخورد می‌کنند

10. **Template Safety**: استفاده از این tags در templates امن است و باعث crash نمی‌شود
