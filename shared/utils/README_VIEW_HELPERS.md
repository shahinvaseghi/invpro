# shared/utils/view_helpers.py - View Helper Functions

**هدف**: توابع کمکی برای عملیات مشترک viewها

این فایل شامل توابع کمکی زیر است:
- `get_breadcrumbs()` - تولید لیست breadcrumbs با prefix ماژول
- `get_success_message()` - تولید پیام موفقیت برای actions مشترک
- `validate_active_company()` - اعتبارسنجی اینکه شرکت فعال در session وجود دارد
- `get_table_headers()` - تولید لیست table headers از field definitions

---

## توابع

### `get_breadcrumbs(module_name: str, items: List[Dict[str, Optional[str]]]) -> List[Dict[str, Optional[str]]]`

**توضیح**: تولید لیست breadcrumbs با prefix ماژول

**پارامترهای ورودی**:
- `module_name`: نام ماژول (مثلاً `'inventory'`, `'production'`)
- `items`: لیست dictionaries با کلیدهای `'label'` و `'url'`

**مقدار بازگشتی**:
- `List[Dict[str, Optional[str]]]`: لیست breadcrumb dictionaries با کلیدهای `'label'` و `'url'`

**منطق**:
1. لیست `breadcrumbs` را با `{'label': _('Dashboard'), 'url': reverse('ui:dashboard')}` شروع می‌کند
2. اگر `items` وجود داشته باشد، آن‌ها را به breadcrumbs اضافه می‌کند
3. لیست breadcrumbs را برمی‌گرداند

**مثال**:
```python
from shared.utils.view_helpers import get_breadcrumbs
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

breadcrumbs = get_breadcrumbs('inventory', [
    {'label': _('Item Types'), 'url': reverse('inventory:item_types')},
    {'label': _('Create'), 'url': None},
])
# Returns: [
#     {'label': 'Dashboard', 'url': '/dashboard/'},
#     {'label': 'Item Types', 'url': '/inventory/item-types/'},
#     {'label': 'Create', 'url': None},
# ]
```

---

### `get_success_message(action: str, model_name: str) -> str`

**توضیح**: تولید پیام موفقیت برای actions مشترک

**پارامترهای ورودی**:
- `action`: نام action (`'created'`, `'updated'`, `'deleted'`)
- `model_name`: نام verbose model

**مقدار بازگشتی**:
- `str`: پیام موفقیت ترجمه شده

**منطق**:
1. `action_messages` dictionary را با mapping actions به templates ایجاد می‌کند:
   - `'created'`: `_('{model} created successfully.')`
   - `'updated'`: `_('{model} updated successfully.')`
   - `'deleted'`: `_('{model} deleted successfully.')`
2. template را از dictionary دریافت می‌کند
3. اگر action در dictionary وجود نداشته باشد، template پیش‌فرض را استفاده می‌کند: `_('{model} {action} successfully.')`
4. template را با `model` و `action` format می‌کند
5. پیام را برمی‌گرداند

**مثال**:
```python
from shared.utils.view_helpers import get_success_message

message = get_success_message('created', 'Item Type')
# Returns: "Item Type created successfully."

message = get_success_message('updated', 'Product Order')
# Returns: "Product Order updated successfully."
```

---

### `validate_active_company(request: HttpRequest) -> Tuple[bool, Optional[str]]`

**توضیح**: اعتبارسنجی اینکه شرکت فعال در session وجود دارد

**پارامترهای ورودی**:
- `request`: Django request object

**مقدار بازگشتی**:
- `Tuple[bool, Optional[str]]`: Tuple شامل (is_valid, error_message)

**منطق**:
1. `active_company_id` را از `request.session` دریافت می‌کند
2. اگر `active_company_id` وجود نداشته باشد:
   - `(False, _('Please select a company first.'))` را برمی‌گرداند
3. در غیر این صورت:
   - `(True, None)` را برمی‌گرداند

**مثال**:
```python
from shared.utils.view_helpers import validate_active_company
from django.contrib import messages
from django.shortcuts import redirect

def my_view(request):
    is_valid, error = validate_active_company(request)
    if not is_valid:
        messages.error(request, error)
        return redirect('shared:select_company')
    # Continue with view logic...
```

---

### `get_table_headers(fields: List[Any]) -> List[Dict[str, Any]]`

**توضیح**: تولید لیست table headers از field definitions

**پارامترهای ورودی**:
- `fields`: لیست field names یا dictionaries با کلیدهای `'label'` و `'field'`

**مقدار بازگشتی**:
- `List[Dict[str, Any]]`: لیست header dictionaries با کلیدهای `'label'` و `'field'`

**منطق**:
1. لیست `headers` را ایجاد می‌کند
2. برای هر field در `fields`:
   - اگر field یک string باشد:
     - label را از field name با replace `'_'` به `' '` و title() ایجاد می‌کند
     - `{'label': label, 'field': field}` را اضافه می‌کند
   - اگر field یک dictionary باشد:
     - آن را به صورت مستقیم اضافه می‌کند
   - در غیر این صورت:
     - skip می‌کند
3. لیست headers را برمی‌گرداند

**مثال**:
```python
from shared.utils.view_helpers import get_table_headers
from django.utils.translation import gettext_lazy as _

# Simple format
headers = get_table_headers(['name', 'code', 'is_enabled'])
# Returns: [
#     {'label': 'Name', 'field': 'name'},
#     {'label': 'Code', 'field': 'code'},
#     {'label': 'Is Enabled', 'field': 'is_enabled'},
# ]

# Custom format
headers = get_table_headers([
    {'label': _('Name'), 'field': 'name'},
    {'label': _('Code'), 'field': 'public_code', 'type': 'code'},
])
# Returns: [
#     {'label': 'Name', 'field': 'name'},
#     {'label': 'Code', 'field': 'public_code', 'type': 'code'},
# ]
```

---

## وابستگی‌ها

- `django.http`: `HttpRequest`
- `django.urls`: `reverse`
- `django.utils.translation`: `gettext_lazy as _`
- `typing`: `List`, `Dict`, `Any`, `Optional`, `Tuple`

---

## استفاده در پروژه

### استفاده در Views

```python
from shared.utils.view_helpers import (
    get_breadcrumbs,
    get_success_message,
    validate_active_company,
    get_table_headers,
)
from django.contrib import messages
from django.shortcuts import redirect

class MyListView(BaseListView):
    def get_breadcrumbs(self):
        return get_breadcrumbs('inventory', [
            {'label': _('Items'), 'url': None},
        ])
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['table_headers'] = get_table_headers([
            'name', 'code', 'is_enabled'
        ])
        return context

class MyCreateView(BaseCreateView):
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            get_success_message('created', 'Item')
        )
        return response
    
    def dispatch(self, request, *args, **kwargs):
        is_valid, error = validate_active_company(request)
        if not is_valid:
            messages.error(request, error)
            return redirect('shared:select_company')
        return super().dispatch(request, *args, **kwargs)
```

---

## نکات مهم

1. **Breadcrumbs**: `get_breadcrumbs()` همیشه Dashboard را به عنوان اولین breadcrumb اضافه می‌کند

2. **Success Messages**: `get_success_message()` از translation system استفاده می‌کند و پیام‌ها را ترجمه می‌کند

3. **Company Validation**: `validate_active_company()` برای استفاده در `dispatch()` یا قبل از پردازش request مناسب است

4. **Table Headers**: `get_table_headers()` از دو format پشتیبانی می‌کند:
   - Simple string format: field name به صورت خودکار به label تبدیل می‌شود
   - Dictionary format: label و field به صورت دستی تعریف می‌شوند

5. **Translation**: تمام توابع از `gettext_lazy` استفاده می‌کنند برای پشتیبانی از چندزبانه

6. **Type Hints**: تمام توابع دارای type hints هستند برای بهتر شدن IDE support و code clarity

7. **Error Handling**: `validate_active_company()` error message را برمی‌گرداند که می‌تواند در messages framework استفاده شود

8. **Flexibility**: `get_table_headers()` از custom fields با attributes اضافی (مثل `'type'`) پشتیبانی می‌کند
