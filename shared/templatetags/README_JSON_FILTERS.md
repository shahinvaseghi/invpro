# shared/templatetags/json_filters.py - JSON Template Filters

**هدف**: فیلترهای template برای تبدیل Python objects به JSON string

این فایل شامل یک فیلتر template برای تبدیل Python objects (dict, list, etc.) به JSON string است که در templates استفاده می‌شود (مثلاً برای پاس دادن داده‌ها به JavaScript).

---

## فیلترها

### `to_json`

**هدف**: تبدیل یک Python object (dict, list, etc.) به JSON string

**استفاده در template**:
```django
{% load json_filters %}

<script>
    var fieldConfig = {{ field_config|to_json }};
    var options = {{ options|to_json }};
</script>
```

**پارامترهای ورودی**:
- `value`: Python object (dict, list, str, None, etc.)

**مقدار بازگشتی**:
- `str`: JSON string یا `'{}'` اگر ورودی نامعتبر باشد

**منطق کار**:
1. اگر `value` برابر `None` باشد، `'{}'` برمی‌گرداند
2. اگر `value` یک رشته باشد:
   - سعی می‌کند آن را parse کند تا معتبر بودن JSON را بررسی کند
   - اگر معتبر باشد، همان رشته را برمی‌گرداند
   - اگر نامعتبر باشد، `'{}'` برمی‌گرداند
3. اگر `value` یک object دیگر باشد (dict, list, etc.):
   - سعی می‌کند آن را با `json.dumps()` به JSON string تبدیل کند
   - `ensure_ascii=False` برای پشتیبانی از کاراکترهای غیر ASCII (مثل فارسی)
   - اگر خطا بدهد (مثلاً object قابل serialize نباشد)، `'{}'` برمی‌گرداند

**مثال استفاده**:
```django
{% load json_filters %}

{# با dict #}
<script>
    var config = {{ field_config|to_json }};
    // اگر field_config = {'type': 'text', 'label': 'نام'} باشد:
    // نتیجه: var config = {"type": "text", "label": "نام"};
</script>

{# با list #}
<script>
    var items = {{ items|to_json }};
    // اگر items = [1, 2, 3] باشد:
    // نتیجه: var items = [1, 2, 3];
</script>

{# با string (که قبلاً JSON است) #}
<script>
    var data = {{ json_string|to_json }};
    // اگر json_string = '{"key": "value"}' باشد:
    // نتیجه: var data = {"key": "value"};
</script>
```

---

## وابستگی‌ها

- `django.template`: برای ساخت template filters
- `json`: برای تبدیل Python objects به JSON string

---

## استفاده در پروژه

### در Forms (Dynamic Fields)

```django
{% load json_filters %}

<form id="ticket-form">
    <input type="hidden" id="field-config" value="{{ template.field_config|to_json }}">
    
    <script>
        var fieldConfig = JSON.parse(document.getElementById('field-config').value);
        // استفاده از fieldConfig برای ساخت dynamic fields
    </script>
</form>
```

### در JavaScript

```django
{% load json_filters %}

<script>
    // پاس دادن داده‌های Django به JavaScript
    var receiptData = {{ receipt_data|to_json }};
    var itemOptions = {{ item_options|to_json }};
    var warehouseOptions = {{ warehouse_options|to_json }};
    
    // استفاده از داده‌ها
    console.log(receiptData);
    populateSelect('item-select', itemOptions);
    populateSelect('warehouse-select', warehouseOptions);
</script>
```

### در API Responses (Inline)

```django
{% load json_filters %}

<div id="api-data" data-config="{{ api_config|to_json }}"></div>

<script>
    var config = JSON.parse(document.getElementById('api-data').dataset.config);
    // استفاده از config
</script>
```

---

## نکات مهم

1. **Auto-loading**: باید `{% load json_filters %}` در ابتدای template استفاده شود
2. **UTF-8 Support**: با `ensure_ascii=False`، کاراکترهای فارسی و سایر کاراکترهای غیر ASCII به درستی encode می‌شوند
3. **Error Handling**: در صورت خطا، `'{}'` برمی‌گرداند (fail-safe)
4. **String Validation**: اگر ورودی یک رشته باشد، معتبر بودن JSON را بررسی می‌کند
5. **Security**: این فیلتر فقط برای داده‌های trusted استفاده می‌شود. برای داده‌های user input، باید escape شود

---

## مثال‌های کامل

### Dynamic Form Fields

```django
{% load json_filters %}

<div id="dynamic-form">
    <input type="hidden" id="template-config" value="{{ template.field_config|to_json }}">
</div>

<script>
    var templateConfig = JSON.parse(document.getElementById('template-config').value);
    
    // ساخت dynamic fields بر اساس config
    templateConfig.fields.forEach(function(field) {
        var input = document.createElement('input');
        input.type = field.type;
        input.name = field.name;
        input.placeholder = field.label;
        document.getElementById('dynamic-form').appendChild(input);
    });
</script>
```

### Chart Data

```django
{% load json_filters %}

<div id="chart-container"></div>

<script>
    var chartData = {{ chart_data|to_json }};
    
    // استفاده از chartData برای رسم نمودار
    drawChart(chartData);
</script>
```

### Filter Options

```django
{% load json_filters %}

<select id="item-type-select">
    <option value="">همه</option>
</select>

<script>
    var itemTypeOptions = {{ item_type_options|to_json }};
    
    // پر کردن select با options
    itemTypeOptions.forEach(function(option) {
        var opt = document.createElement('option');
        opt.value = option.id;
        opt.text = option.name;
        document.getElementById('item-type-select').appendChild(opt);
    });
</script>
```

---

## Security Considerations

1. **XSS Prevention**: اگر داده‌های user input را به JSON تبدیل می‌کنید، باید escape شوند
2. **Trusted Data**: این فیلتر برای داده‌های trusted (از database یا context) طراحی شده است
3. **JSON Injection**: اگر داده‌های user input را به JSON تبدیل می‌کنید، باید validate شوند

**مثال ناامن** (نباید انجام شود):
```django
{# ❌ ناامن - user input را مستقیماً به JSON تبدیل نکنید #}
<script>
    var userData = {{ user_input|to_json }};
</script>
```

**مثال امن**:
```django
{# ✅ امن - داده‌های trusted از context #}
<script>
    var config = {{ template.field_config|to_json }};
</script>
```

---

## تفاوت با `mark_safe`

اگر می‌خواهید JSON را به صورت raw HTML render کنید (بدون escape)، می‌توانید از `mark_safe` استفاده کنید:

```python
# در view
from django.utils.safestring import mark_safe
import json

context['config_json'] = mark_safe(json.dumps(config, ensure_ascii=False))
```

```django
{# در template #}
<script>
    var config = {{ config_json }};
</script>
```

اما استفاده از `to_json` filter بهتر است چون:
- Consistent است
- Error handling دارد
- در template قابل استفاده است (بدون نیاز به تغییر view)

---

## Performance

- تبدیل JSON سریع است
- برای داده‌های کوچک تا متوسط مناسب است
- برای داده‌های بزرگ (مثلاً لیست‌های طولانی)، بهتر است از AJAX استفاده شود

