# shared/templatetags/access_tags.py - Access Control Template Tags

**هدف**: Template tags برای بررسی مجوزهای دسترسی کاربران در templates

این فایل شامل یک فیلتر template برای بررسی اینکه آیا کاربر مجوز دسترسی به یک feature خاص را دارد یا نه.

---

## فیلترها

### `feature_allowed`

**هدف**: بررسی اینکه آیا کاربر مجوز دسترسی به یک feature خاص را دارد

**استفاده در template**:
```django
{% load access_tags %}

{% if user_feature_permissions|feature_allowed:"inventory.receipts.permanent:create" %}
    <a href="{% url 'inventory:receipt_permanent_create' %}">Create Receipt</a>
{% endif %}
```

**پارامترهای ورودی**:
- `user_permissions` (Dict): دیکشنری مجوزهای کاربر (از `user_feature_permissions` context)
- `args` (str): رشته با فرمت `"feature_code[:action]"`

**فرمت `args`**:
- `"feature_code"`: فقط feature code (action پیش‌فرض: `'view'`)
- `"feature_code:action"`: feature code و action (مثل `"inventory.receipts.permanent:create"`)

**مقدار بازگشتی**:
- `bool`: `True` اگر کاربر مجوز داشته باشد، `False` در غیر این صورت

**منطق کار**:
1. اگر `user_permissions` خالی باشد، `False` برمی‌گرداند
2. اگر `args` خالی باشد، `False` برمی‌گرداند
3. اگر `args` شامل `:` باشد:
   - `feature_code` و `action` را از `args` استخراج می‌کند
4. اگر `args` شامل `:` نباشد:
   - `feature_code = args`
   - `action = 'view'` (پیش‌فرض)
5. از `has_feature_permission()` برای بررسی مجوز استفاده می‌کند

**مثال استفاده**:
```django
{% load access_tags %}

{# بررسی مجوز view #}
{% if user_feature_permissions|feature_allowed:"inventory.receipts.permanent" %}
    <a href="{% url 'inventory:receipt_permanent_list' %}">View Receipts</a>
{% endif %}

{# بررسی مجوز create #}
{% if user_feature_permissions|feature_allowed:"inventory.receipts.permanent:create" %}
    <a href="{% url 'inventory:receipt_permanent_create' %}">Create Receipt</a>
{% endif %}

{# بررسی مجوز approve #}
{% if user_feature_permissions|feature_allowed:"inventory.purchase_requests:approve" %}
    <button>Approve Request</button>
{% endif %}
```

---

## وابستگی‌ها

- `django.template`: برای ساخت template tags
- `shared.utils.permissions.has_feature_permission`: برای بررسی مجوز

---

## استفاده در پروژه

### در Navigation

```django
{% load access_tags %}

<nav>
    <ul>
        <li>
            {% if user_feature_permissions|feature_allowed:"inventory.receipts.permanent" %}
                <a href="{% url 'inventory:receipt_permanent_list' %}">Receipts</a>
            {% endif %}
        </li>
        <li>
            {% if user_feature_permissions|feature_allowed:"inventory.issues.permanent" %}
                <a href="{% url 'inventory:issue_permanent_list' %}">Issues</a>
            {% endif %}
        </li>
    </ul>
</nav>
```

### در Action Buttons

```django
{% load access_tags %}

<div class="actions">
    {% if user_feature_permissions|feature_allowed:"inventory.receipts.permanent:create" %}
        <a href="{% url 'inventory:receipt_permanent_create' %}" class="btn btn-primary">
            Create Receipt
        </a>
    {% endif %}
    
    {% if user_feature_permissions|feature_allowed:"inventory.receipts.permanent:update" %}
        <a href="{% url 'inventory:receipt_permanent_update' receipt.pk %}" class="btn btn-secondary">
            Edit
        </a>
    {% endif %}
    
    {% if user_feature_permissions|feature_allowed:"inventory.receipts.permanent:delete" %}
        <a href="{% url 'inventory:receipt_permanent_delete' receipt.pk %}" class="btn btn-danger">
            Delete
        </a>
    {% endif %}
</div>
```

### در Forms

```django
{% load access_tags %}

<form method="post">
    {% csrf_token %}
    {{ form.as_p }}
    
    {% if user_feature_permissions|feature_allowed:"inventory.purchase_requests:approve" %}
        <button type="submit" name="action" value="approve">Approve</button>
    {% endif %}
    
    {% if user_feature_permissions|feature_allowed:"inventory.purchase_requests:reject" %}
        <button type="submit" name="action" value="reject">Reject</button>
    {% endif %}
</form>
```

---

## Feature Codes

Feature codes با فرمت `module.resource.action` هستند:

### Inventory Module
- `inventory.receipts.temporary`: Temporary Receipts
- `inventory.receipts.permanent`: Permanent Receipts
- `inventory.receipts.consignment`: Consignment Receipts
- `inventory.issues.permanent`: Permanent Issues
- `inventory.issues.consumption`: Consumption Issues
- `inventory.issues.consignment`: Consignment Issues
- `inventory.purchase_requests`: Purchase Requests
- `inventory.warehouse_requests`: Warehouse Requests

### Actions
- `view`: مشاهده (پیش‌فرض)
- `create`: ایجاد
- `update`: ویرایش
- `delete`: حذف
- `approve`: تایید
- `reject`: رد
- `lock`: قفل کردن
- `unlock`: باز کردن قفل

---

## نکات مهم

1. **Context Variable**: `user_feature_permissions` باید از context processor (`shared.context_processors.active_company`) به template پاس داده شود
2. **Default Action**: اگر action مشخص نشود، پیش‌فرض `'view'` است
3. **Feature Code Format**: Feature codes باید با فرمت `module.resource.action` باشند
4. **Performance**: بررسی مجوز سریع است و برای استفاده در templates مناسب است
5. **Security**: این فیلتر فقط برای نمایش UI استفاده می‌شود. بررسی مجوز واقعی باید در views انجام شود

---

## مثال‌های کامل

```django
{% load access_tags %}

<div class="dashboard">
    <div class="card">
        <h3>Receipts</h3>
        <div class="actions">
            {% if user_feature_permissions|feature_allowed:"inventory.receipts.permanent:view" %}
                <a href="{% url 'inventory:receipt_permanent_list' %}">View All</a>
            {% endif %}
            
            {% if user_feature_permissions|feature_allowed:"inventory.receipts.permanent:create" %}
                <a href="{% url 'inventory:receipt_permanent_create' %}">Create New</a>
            {% endif %}
        </div>
    </div>
    
    <div class="card">
        <h3>Purchase Requests</h3>
        <div class="actions">
            {% if user_feature_permissions|feature_allowed:"inventory.purchase_requests:view" %}
                <a href="{% url 'inventory:purchase_requests' %}">View All</a>
            {% endif %}
            
            {% if user_feature_permissions|feature_allowed:"inventory.purchase_requests:create" %}
                <a href="{% url 'inventory:purchase_request_create' %}">Create New</a>
            {% endif %}
            
            {% if user_feature_permissions|feature_allowed:"inventory.purchase_requests:approve" %}
                <a href="{% url 'inventory:purchase_requests' %}?status=draft">Pending Approvals</a>
            {% endif %}
        </div>
    </div>
</div>
```

---

## Integration with Context Processor

این فیلتر با `shared.context_processors.active_company` کار می‌کند که `user_feature_permissions` را به context اضافه می‌کند:

```python
# shared/context_processors.py
def active_company(request):
    # ...
    context['user_feature_permissions'] = get_user_feature_permissions(
        request.user, 
        company_id
    )
    return context
```

در template:
```django
{% load access_tags %}

{% if user_feature_permissions|feature_allowed:"inventory.receipts.permanent:create" %}
    <!-- Show create button -->
{% endif %}
```

