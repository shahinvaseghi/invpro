# shared/templatetags/ - Template Tags

این پوشه شامل template tags و filters سفارشی برای ماژول shared است که در سراسر پروژه استفاده می‌شوند.

## فایل‌ها

### access_tags.py

**هدف**: بررسی مجوزهای کاربر برای features و actions در templates

---

## Filters

### `@register.filter`

**تابع**: `feature_allowed(user_permissions, args: str) -> bool`

**توضیح**: بررسی می‌کند که آیا کاربر مجوز برای یک feature و action خاص دارد یا نه.

**پارامترهای ورودی**:
- `user_permissions`: دیکشنری مجوزهای کاربر (از context processor `active_company`)
- `args` (str): کد feature با action اختیاری (فرمت: `"feature_code[:action]"`)

**مقدار بازگشتی**:
- `bool`: `True` اگر کاربر مجوز داشته باشد، `False` در غیر این صورت

**فرمت args**:
- `"inventory.receipts.permanent"`: بررسی مجوز view (پیش‌فرض)
- `"inventory.receipts.permanent:create"`: بررسی مجوز create
- `"inventory.receipts.permanent:approve"`: بررسی مجوز approve

**مثال استفاده در template**:
```django
{% load access_tags %}

{# بررسی مجوز view #}
{% if user_feature_permissions|feature_allowed:"inventory.receipts.permanent" %}
  <a href="{% url 'inventory:receipt_permanent_list' %}">رسیدهای دائم</a>
{% endif %}

{# بررسی مجوز create #}
{% if user_feature_permissions|feature_allowed:"inventory.receipts.permanent:create" %}
  <a href="{% url 'inventory:receipt_permanent_create' %}" class="btn btn-primary">
    ایجاد رسید دائم
  </a>
{% endif %}

{# بررسی مجوز approve #}
{% if user_feature_permissions|feature_allowed:"inventory.receipts.permanent:approve" %}
  <button type="submit" class="btn btn-success">تایید</button>
{% endif %}
```

**مقادیر action**:
- `view` (default): بررسی مجوز view
- `view_all`: بررسی مجوز view all
- `view_own`: بررسی مجوز view own
- `create`: بررسی مجوز create
- `edit_own`: بررسی مجوز edit own
- `delete_own`: بررسی مجوز delete own
- `approve`: بررسی مجوز approve
- `lock_own`: بررسی مجوز lock own
- و غیره...

**نکات مهم**:
- کدهای feature از dot notation استفاده می‌کنند (مثل `inventory.receipts.permanent`)
- اگر action حذف شود، به صورت پیش‌فرض `view` استفاده می‌شود
- Superusers به صورت خودکار تمام مجوزها را دارند
- اگر `user_permissions` خالی یا `None` باشد، `False` برمی‌گرداند

---

### json_filters.py

**هدف**: تبدیل اشیاء Python به JSON string برای استفاده در templates (به خصوص JavaScript)

---

## Filters

### `@register.filter(name='to_json')`

**تابع**: `to_json(value)`

**توضیح**: یک شیء Python (dict, list, etc.) را به رشته JSON تبدیل می‌کند.

**پارامترهای ورودی**:
- `value`: شیء Python (dict, list, string, یا None)

**مقدار بازگشتی**:
- `str`: نمایش JSON رشته از شیء

**مثال استفاده در template**:
```django
{% load json_filters %}

{# تبدیل dict به JSON #}
<script>
  const fieldConfig = {{ field_config|to_json }};
  console.log(fieldConfig);
</script>

{# تبدیل list به JSON #}
<script>
  const items = {{ items_list|to_json }};
  items.forEach(item => {
    console.log(item.name);
  });
</script>
```

**رفتار**:
- اگر `value` برابر `None` باشد، `'{}'` برمی‌گرداند
- اگر `value` از قبل یک رشته JSON معتبر باشد، آن را به صورت همان برمی‌گرداند
- اگر `value` یک dict/list باشد، با `ensure_ascii=False` به JSON تبدیل می‌شود (از کاراکترهای فارسی پشتیبانی می‌کند)
- اگر تبدیل ناموفق باشد، `'{}'` برمی‌گرداند

**Error Handling**:
- `TypeError` و `ValueError` را catch می‌کند
- در صورت خطا، JSON object خالی `'{}'` برمی‌گرداند

**مثال کامل در template**:
```django
{% load json_filters %}

<script>
  // Pass Python dict to JavaScript
  const config = {{ ticket_template.field_config|to_json }};
  
  // Use in JavaScript
  if (config.show_date_picker) {
    initializeDatePicker();
  }
</script>
```

---

## وابستگی‌ها

- `django.template`: برای ثبت filters
- `shared.utils.permissions`: `has_feature_permission` برای بررسی مجوزها
- `json`: برای تبدیل به JSON

---

## استفاده در پروژه

این filters در تمام templates استفاده می‌شوند:

```django
{% load access_tags json_filters %}

{# بررسی مجوز #}
{% if user_feature_permissions|feature_allowed:"inventory.receipts.permanent:create" %}
  <button>Create</button>
{% endif %}

{# تبدیل به JSON #}
<script>
  const data = {{ form_data|to_json }};
</script>
```

---

## نکات مهم

1. **Loading Tags**: باید ابتدا `{% load access_tags %}` یا `{% load json_filters %}` را در template فراخوانی کنید
2. **Permission Checks**: بررسی‌های مجوز سریع هستند، اما از nested checks در loops اجتناب کنید
3. **JSON Validation**: خروجی `to_json` را در browser console تست کنید قبل از استفاده در JavaScript
4. **Persian Support**: `to_json` از کاراکترهای فارسی پشتیبانی می‌کند (`ensure_ascii=False`)

