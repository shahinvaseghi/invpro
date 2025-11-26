# ui/context_processors.py - UI Context Processors

**هدف**: فراهم کردن متغیرهای context که در تمام templates به صورت global در دسترس هستند

Context processors توابعی هستند که در `config/settings.py` در `TEMPLATES['OPTIONS']['context_processors']` ثبت می‌شوند و در هر render template به صورت خودکار فراخوانی می‌شوند.

---

## تابع `active_module(request)`

**هدف**: تعیین ماژول فعال برای navigation highlighting

**پارامترهای ورودی**:
- `request` (HttpRequest): درخواست HTTP Django

**مقدار بازگشتی**:
```python
{
    "active_module": str  # نام ماژول فعال (مثل "dashboard", "inventory", "production")
}
```

**منطق کار**:
1. از `request.GET.get("module", "dashboard")` استفاده می‌کند
2. اگر پارامتر `module` در query string وجود داشته باشد، آن را برمی‌گرداند
3. در غیر این صورت، `"dashboard"` را به عنوان پیش‌فرض برمی‌گرداند

**مثال استفاده در template**:
```django
{% if active_module == "inventory" %}
    <li class="active">Inventory</li>
{% else %}
    <li>Inventory</li>
{% endif %}
```

---

## وابستگی‌ها

- `django.http.HttpRequest`: برای دسترسی به request object

---

## استفاده در پروژه

این context processor در `config/settings.py` ثبت شده است:

```python
TEMPLATES = [
    {
        'OPTIONS': {
            'context_processors': [
                # ...
                'ui.context_processors.active_module',
            ],
        },
    },
]
```

---

## استفاده در Templates

### در Navigation

```django
<nav>
    <ul>
        <li class="{% if active_module == 'dashboard' %}active{% endif %}">
            <a href="{% url 'ui:dashboard' %}">Dashboard</a>
        </li>
        <li class="{% if active_module == 'inventory' %}active{% endif %}">
            <a href="{% url 'inventory:item_list' %}">Inventory</a>
        </li>
        <li class="{% if active_module == 'production' %}active{% endif %}">
            <a href="{% url 'production:bom_list' %}">Production</a>
        </li>
    </ul>
</nav>
```

### در Sidebar

```django
<div class="sidebar">
    <div class="module-section {% if active_module == 'inventory' %}active{% endif %}">
        <h3>Inventory</h3>
        <ul>
            <li><a href="{% url 'inventory:item_list' %}">Items</a></li>
            <li><a href="{% url 'inventory:receipt_permanent_list' %}">Receipts</a></li>
        </ul>
    </div>
</div>
```

---

## نکات مهم

1. **Static Implementation**: در حال حاضر این تابع static است و از query string استفاده می‌کند
2. **Future Enhancement**: در آینده می‌تواند از URL path یا user preferences استفاده کند
3. **Default Value**: اگر `module` در query string نباشد، `"dashboard"` به عنوان پیش‌فرض استفاده می‌شود
4. **Performance**: این تابع بسیار سریع است و برای هر request اجرا می‌شود

---

## مقادیر ممکن برای `active_module`

- `"dashboard"`: Dashboard (پیش‌فرض)
- `"inventory"`: ماژول Inventory
- `"production"`: ماژول Production
- `"qc"`: ماژول Quality Control
- `"ticketing"`: ماژول Ticketing
- `"shared"`: ماژول Shared

---

## مثال‌های کامل

### Navigation Menu

```django
{% load static %}

<nav class="main-nav">
    <a href="{% url 'ui:dashboard' %}?module=dashboard" 
       class="{% if active_module == 'dashboard' %}active{% endif %}">
        Dashboard
    </a>
    <a href="{% url 'inventory:item_list' %}?module=inventory" 
       class="{% if active_module == 'inventory' %}active{% endif %}">
        Inventory
    </a>
    <a href="{% url 'production:bom_list' %}?module=production" 
       class="{% if active_module == 'production' %}active{% endif %}">
        Production
    </a>
</nav>
```

### CSS Styling

```css
.main-nav a.active {
    background-color: #3b82f6;
    color: white;
    font-weight: bold;
}
```

---

## Future Enhancements

### URL-based Detection

```python
def active_module(request):
    """Determine active module from URL path."""
    path = request.path
    
    if path.startswith('/inventory/'):
        return {'active_module': 'inventory'}
    elif path.startswith('/production/'):
        return {'active_module': 'production'}
    elif path.startswith('/qc/'):
        return {'active_module': 'qc'}
    elif path.startswith('/ticketing/'):
        return {'active_module': 'ticketing'}
    else:
        return {'active_module': 'dashboard'}
```

### User Preferences

```python
def active_module(request):
    """Get active module from user preferences or URL."""
    if request.user.is_authenticated:
        # از user preferences استفاده کنید
        preferred_module = getattr(request.user, 'preferred_module', None)
        if preferred_module:
            return {'active_module': preferred_module}
    
    # Fallback به URL-based detection
    # ...
```

---

## Integration with Other Context Processors

این context processor با سایر context processors (مثل `shared.context_processors.active_company`) کار می‌کند:

```python
# config/settings.py
TEMPLATES = [
    {
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'shared.context_processors.active_company',  # Company context
                'ui.context_processors.active_module',        # Module context
            ],
        },
    },
]
```

در template:
```django
<div class="header">
    <h1>{{ active_company.display_name }}</h1>
    <p>Current Module: {{ active_module }}</p>
</div>
```
