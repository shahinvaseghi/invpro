# پیاده‌سازی Entity Reference برای Options در Ticketing

## وضعیت فعلی

### ✅ پیاده‌سازی شده:

1. **UI برای Entity Reference Configuration**:
   - فیلد Entity Reference (مثلاً: `users:list`, `inventory.items:list`)
   - فیلد Value Field (مثلاً: `id`)
   - فیلد Label Field (مثلاً: `name`)
   - این فیلدها در تنظیمات فیلدهای `dropdown`, `radio`, `checkbox`, `multi_select` نمایش داده می‌شوند

2. **ذخیره تنظیمات**:
   - تنظیمات Entity Reference در `field_config` به صورت JSON ذخیره می‌شوند:
     ```json
     {
       "options_source": "entity_reference",
       "entity_reference": "users:list",
       "value_field": "id",
       "label_field": "username"
     }
     ```

### ⚠️ نیاز به پیاده‌سازی:

1. **API/View برای دریافت Options**:
   - نیاز به یک endpoint برای دریافت لیست Options بر اساس Entity Reference
   - این endpoint باید Entity Reference را parse کند و داده‌های مربوطه را از دیتابیس برگرداند

2. **JavaScript برای بارگذاری Options**:
   - در زمان ایجاد/ویرایش Ticket، باید Options را از API بگیرد
   - Options باید به صورت دینامیک در dropdown/radio/checkbox نمایش داده شوند

## نحوه کار Entity Reference

### ساختار Entity Reference:

```
<section_nickname>:<action>:<parameters>
```

مثال‌ها:
- `users:list` - لیست تمام کاربران
- `users:show:gp=superuser` - کاربران با گروه superuser
- `inventory.items:list` - لیست تمام کالاها
- `inventory.warehouses:list` - لیست تمام انبارها

### Section Registry:

Entity Reference System از Section Registry استفاده می‌کند که در `shared/models.py` تعریف شده:
- `SectionRegistry`: ثبت بخش‌های برنامه با کد 6 رقمی و nickname
- `ActionRegistry`: ثبت Action‌های هر بخش

برای جزئیات کامل، به `docs/ENTITY_REFERENCE_SYSTEM.md` مراجعه کنید.

## نیازهای پیاده‌سازی

### 1. API Endpoint برای دریافت Options

```python
# ticketing/views/entity_reference.py

from django.http import JsonResponse
from django.views.decorators.http import require_GET
from shared.models import SectionRegistry, ActionRegistry
from django.db import models

@require_GET
def get_entity_reference_options(request):
    """
    دریافت لیست Options بر اساس Entity Reference
    
    Parameters:
    - entity_reference: مثلاً "users:list"
    - value_field: فیلد به عنوان value (مثلاً "id")
    - label_field: فیلد به عنوان label (مثلاً "username")
    - filters: فیلترهای اضافی (JSON)
    """
    entity_ref = request.GET.get('entity_reference')
    value_field = request.GET.get('value_field', 'id')
    label_field = request.GET.get('label_field', 'name')
    
    # Parse entity reference
    # مثال: "users:list" -> section="users", action="list"
    
    # Find section from SectionRegistry
    # Find action from ActionRegistry
    
    # Get model based on section
    # Execute query based on action and filters
    
    # Return JSON: [{"value": ..., "label": ...}, ...]
    
    return JsonResponse({"options": []})
```

### 2. JavaScript برای بارگذاری Options

```javascript
// در template_form.html یا ticket_form.html

function loadOptionsFromEntityReference(fieldConfig) {
    if (fieldConfig.options_source === 'entity_reference') {
        const entityRef = fieldConfig.entity_reference;
        const valueField = fieldConfig.value_field || 'id';
        const labelField = fieldConfig.label_field || 'name';
        
        // Call API
        fetch(`/ticketing/api/entity-reference-options/?entity_reference=${entityRef}&value_field=${valueField}&label_field=${labelField}`)
            .then(response => response.json())
            .then(data => {
                // Populate dropdown/radio/checkbox with options
                populateFieldOptions(data.options);
            });
    }
}
```

### 3. Mapping Section Nickname به Model

```python
# ticketing/utils/entity_reference_mapper.py

ENTITY_REFERENCE_MODEL_MAP = {
    'users': 'shared.User',
    'items': 'inventory.Item',
    'warehouses': 'inventory.Warehouse',
    'suppliers': 'inventory.Supplier',
    # ...
}
```

## مثال‌های Entity Reference برای Options

### مثال 1: کاربران

```json
{
  "options_source": "entity_reference",
  "entity_reference": "users:list",
  "value_field": "id",
  "label_field": "username"
}
```

### مثال 2: کالاها

```json
{
  "options_source": "entity_reference",
  "entity_reference": "inventory.items:list",
  "value_field": "id",
  "label_field": "item_code"
}
```

### مثال 3: انبارها

```json
{
  "options_source": "entity_reference",
  "entity_reference": "inventory.warehouses:list",
  "value_field": "id",
  "label_field": "name"
}
```

## مراحل پیاده‌سازی پیشنهادی

1. ✅ UI برای Entity Reference Configuration (انجام شده)
2. ⚠️ API Endpoint برای دریافت Options
3. ⚠️ JavaScript برای بارگذاری Options در زمان ایجاد Ticket
4. ⚠️ تست با Entity Reference های مختلف

## فایل‌های مرتبط

- `docs/ENTITY_REFERENCE_SYSTEM.md`: مستندات کامل Entity Reference System
- `docs/ticketing_field_settings_specification.md`: مشخصات فیلدهای Options
- `templates/ticketing/template_form.html`: UI برای Entity Reference Configuration
- `shared/models.py`: `SectionRegistry` و `ActionRegistry`

