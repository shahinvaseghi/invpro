# templates/shared/generic/generic_list.html - Generic List Template

**هدف**: این template یک صفحه لیست قابل استفاده مجدد برای نمایش لیست اشیاء با قابلیت‌های فیلتر، جستجو، pagination و عملیات CRUD است.

این template برای کاهش تکرار کد در صفحات لیست مختلف برنامه طراحی شده و می‌تواند برای هر نوع entity استفاده شود.

---

## ساختار Template

این template از `base.html` extend می‌کند و شامل بخش‌های زیر است:

1. **Header Section**: Breadcrumb navigation + Page title + Action buttons
2. **Messages Section**: نمایش پیام‌های Django messages
3. **Filter Panel**: پنل فیلتر و جستجو (اختیاری)
4. **Data Table**: جدول داده‌ها با ستون‌های قابل تنظیم
5. **Pagination**: صفحه‌بندی (در صورت نیاز)
6. **Empty State**: حالت خالی برای زمانی که داده‌ای وجود ندارد

---

## Context Variables

### الزامی

#### `object_list`
- **Type**: `QuerySet` یا `list`
- **توضیح**: لیست اشیاء برای نمایش در جدول
- **مثال**: `Item.objects.all()`

#### `table_headers`
- **Type**: `list[dict]`
- **توضیح**: لیست دیکشنری‌های تعریف کننده ستون‌های جدول
- **ساختار هر header**:
  ```python
  {
      'label': 'نام ستون',           # الزامی - برچسب ستون
      'field': 'field_name',         # اختیاری - نام فیلد در object
      'type': 'code|badge|link',     # اختیاری - نوع نمایش
      'true_label': 'فعال',          # برای type='badge' - برچسب برای True
      'false_label': 'غیرفعال',     # برای type='badge' - برچسب برای False
      'url_name': 'app:view_name',   # برای type='link' - نام URL pattern
      'url_field': 'pk',             # برای type='link' - فیلد برای URL
      'custom_content': '...',       # اختیاری - محتوای سفارشی
  }
  ```
- **مثال**:
  ```python
  table_headers = [
      {'label': 'کد', 'field': 'item_code', 'type': 'code'},
      {'label': 'نام', 'field': 'name'},
      {'label': 'وضعیت', 'field': 'is_enabled', 'type': 'badge', 
       'true_label': 'فعال', 'false_label': 'غیرفعال'},
      {'label': 'نوع', 'field': 'type.name'},  # nested attribute
  ]
  ```

### اختیاری

#### `page_title`
- **Type**: `str`
- **Default**: `"List"`
- **توضیح**: عنوان صفحه که در `<h1>` و `<title>` نمایش داده می‌شود
- **مثال**: `"کالاها"`

#### `breadcrumbs`
- **Type**: `list[dict]`
- **Default**: `[]`
- **توضیح**: لیست breadcrumb برای navigation
- **ساختار هر breadcrumb**:
  ```python
  {
      'label': 'نام',      # الزامی
      'url': 'url_path',   # اختیاری - اگر نباشد فقط label نمایش داده می‌شود
  }
  ```
- **مثال**:
  ```python
  breadcrumbs = [
      {'label': 'انبار', 'url': reverse('inventory:items')},
      {'label': 'کالاها'},
  ]
  ```

#### `create_url`
- **Type**: `str` (URL)
- **Default**: `None`
- **توضیح**: URL برای دکمه "ایجاد جدید". اگر تعریف نشود، دکمه نمایش داده نمی‌شود
- **مثال**: `reverse('inventory:item_create')`

#### `create_button_text`
- **Type**: `str`
- **Default**: `"Create New"`
- **توضیح**: متن دکمه ایجاد جدید
- **مثال**: `"تعریف کالای جدید"`

#### `show_filters`
- **Type**: `bool`
- **Default**: `True`
- **توضیح**: نمایش یا عدم نمایش پنل فیلتر

#### `status_filter`
- **Type**: `bool`
- **Default**: `True`
- **توضیح**: نمایش یا عدم نمایش فیلتر وضعیت (فعال/غیرفعال)

#### `search_placeholder`
- **Type**: `str`
- **Default**: `"Search by code or name"`
- **توضیح**: placeholder برای فیلد جستجو

#### `show_actions`
- **Type**: `bool`
- **Default**: `True`
- **توضیح**: نمایش یا عدم نمایش ستون "عملیات" در جدول

#### `edit_url_name`
- **Type**: `str` (URL pattern name)
- **Default**: `None`
- **توضیح**: نام URL pattern برای ویرایش. برای هر ردیف، `object.pk` به عنوان argument ارسال می‌شود
- **مثال**: `'inventory:item_edit'`

#### `delete_url_name`
- **Type**: `str` (URL pattern name)
- **Default**: `None`
- **توضیح**: نام URL pattern برای حذف. برای هر ردیف، `object.pk` به عنوان argument ارسال می‌شود
- **مثال**: `'inventory:item_delete'`

#### `clear_filter_url`
- **Type**: `str` (URL)
- **Default**: `None`
- **توضیح**: URL برای دکمه "حذف فیلتر". اگر تعریف نشود، دکمه نمایش داده نمی‌شود
- **مثال**: `reverse('inventory:items')`

#### `print_enabled`
- **Type**: `bool`
- **Default**: `True`
- **توضیح**: نمایش یا عدم نمایش دکمه چاپ

#### `empty_state_icon`
- **Type**: `str` (emoji یا HTML)
- **Default**: `"📋"`
- **توضیح**: آیکون برای حالت خالی

#### `empty_state_title`
- **Type**: `str`
- **Default**: `"No items found"`
- **توضیح**: عنوان برای حالت خالی

#### `empty_state_message`
- **Type**: `str`
- **Default**: `"Start by adding your first item."`
- **توضیح**: پیام برای حالت خالی

#### `is_paginated`
- **Type**: `bool`
- **Default**: `False`
- **توضیح**: آیا pagination فعال است یا نه

#### `page_obj`
- **Type**: `Page` (Django Paginator)
- **Default**: `None`
- **توضیح**: شیء صفحه برای pagination. باید شامل `has_previous`, `has_next`, `number`, `paginator.num_pages` باشد

---

## Blocks قابل Override

### `breadcrumb_extra`
- **موقعیت**: بعد از breadcrumb اصلی
- **استفاده**: اضافه کردن breadcrumb اضافی
- **مثال**:
  ```django
  {% block breadcrumb_extra %}
  <span class="separator">/</span>
  <span>زیرمجموعه</span>
  {% endblock %}
  ```

### `page_actions`
- **موقعیت**: در header، کنار title
- **استفاده**: سفارشی‌سازی کامل دکمه‌های عملیات
- **نکته**: اگر override شود، دکمه‌های پیش‌فرض نمایش داده نمی‌شوند

### `extra_actions`
- **موقعیت**: داخل `page_actions` block
- **استفاده**: اضافه کردن دکمه‌های اضافی به دکمه‌های پیش‌فرض
- **مثال**:
  ```django
  {% block extra_actions %}
  <a href="{% url 'inventory:item_export' %}" class="btn btn-success">خروجی Excel</a>
  {% endblock %}
  ```

### `filter_fields`
- **موقعیت**: داخل پنل فیلتر
- **استفاده**: اضافه کردن فیلدهای فیلتر سفارشی
- **مثال**:
  ```django
  {% block filter_fields %}
  <div class="form-group">
    <label for="type">نوع کالا</label>
    <select name="type" id="type" class="form-control">
      <option value="">-- همه --</option>
      {% for item_type in item_types %}
        <option value="{{ item_type.id }}">{{ item_type.name }}</option>
      {% endfor %}
    </select>
  </div>
  {{ block.super }}  {# نمایش فیلدهای پیش‌فرض #}
  {% endblock %}
  ```

### `table_headers`
- **موقعیت**: در `<thead>` جدول
- **استفاده**: سفارشی‌سازی کامل هدرهای جدول
- **نکته**: اگر override شود، `table_headers` context variable استفاده نمی‌شود

### `table_rows`
- **موقعیت**: در `<tbody>` جدول
- **استفاده**: سفارشی‌سازی کامل ردیف‌های جدول
- **نکته**: اگر override شود، منطق پیش‌فرض استفاده نمی‌شود
- **مثال**:
  ```django
  {% block table_rows %}
  {% for item in object_list %}
  <tr>
    <td>{{ item.code }}</td>
    <td>{{ item.name }}</td>
    <td>
      <a href="{% url 'inventory:item_detail' item.pk %}">مشاهده</a>
    </td>
  </tr>
  {% endfor %}
  {% endblock %}
  ```

### `action_buttons`
- **موقعیت**: در ستون "عملیات" هر ردیف
- **استفاده**: سفارشی‌سازی دکمه‌های عملیات
- **مثال**:
  ```django
  {% block action_buttons %}
  <a href="{% url 'inventory:item_detail' object.pk %}" class="btn btn-info">جزئیات</a>
  {{ block.super }}  {# نمایش دکمه‌های پیش‌فرض #}
  {% endblock %}
  ```

### `before_table`
- **موقعیت**: قبل از جدول
- **استفاده**: اضافه کردن محتوای اضافی قبل از جدول
- **مثال**: نمایش آمار، نمودار، و غیره

### `after_table`
- **موقعیت**: بعد از جدول و pagination
- **استفاده**: اضافه کردن محتوای اضافی بعد از جدول

---

## انواع نمایش در table_headers

### نوع `code`
- **استفاده**: برای نمایش کدها با استایل `<code>`
- **مثال**:
  ```python
  {'label': 'کد', 'field': 'item_code', 'type': 'code'}
  ```

### نوع `badge`
- **استفاده**: برای نمایش وضعیت با badge (فعال/غیرفعال)
- **پارامترهای اضافی**:
  - `true_label`: برچسب برای مقدار `True` (default: "Active")
  - `false_label`: برچسب برای مقدار `False` (default: "Inactive")
- **مثال**:
  ```python
  {
      'label': 'وضعیت', 
      'field': 'is_enabled', 
      'type': 'badge',
      'true_label': 'فعال',
      'false_label': 'غیرفعال'
  }
  ```

### نوع `link`
- **استفاده**: برای نمایش لینک به صفحه جزئیات
- **پارامترهای اضافی**:
  - `url_name`: نام URL pattern
  - `url_field`: فیلد object برای استفاده در URL (default: 'pk')
- **مثال**:
  ```python
  {
      'label': 'نام', 
      'field': 'name', 
      'type': 'link',
      'url_name': 'inventory:item_detail',
      'url_field': 'pk'
  }
  ```

### Nested Attributes
- **استفاده**: برای دسترسی به فیلدهای nested (مثل `type.name`)
- **مثال**:
  ```python
  {'label': 'نوع', 'field': 'type.name'}
  ```
- **نکته**: نیاز به template tag `getattr` دارد که در `generic_tags.py` تعریف شده

---

## مثال استفاده در View

```python
from django.shortcuts import render
from django.core.paginator import Paginator
from django.urls import reverse
from inventory.models import Item

def items_list(request):
    # دریافت داده‌ها
    items = Item.objects.select_related('type', 'category').all()
    
    # فیلتر بر اساس جستجو
    search = request.GET.get('search', '')
    if search:
        items = items.filter(
            models.Q(name__icontains=search) | 
            models.Q(item_code__icontains=search)
        )
    
    # فیلتر بر اساس وضعیت
    status = request.GET.get('status')
    if status == '1':
        items = items.filter(is_enabled=True)
    elif status == '0':
        items = items.filter(is_enabled=False)
    
    # Pagination
    paginator = Paginator(items, 25)
    page_obj = paginator.get_page(request.GET.get('page'))
    
    # آماده‌سازی context
    context = {
        'object_list': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'page_title': 'کالاها',
        'breadcrumbs': [
            {'label': 'انبار', 'url': reverse('inventory:items')},
            {'label': 'کالاها'},
        ],
        'table_headers': [
            {'label': 'کد کالا', 'field': 'item_code', 'type': 'code'},
            {'label': 'نام کالا', 'field': 'name'},
            {'label': 'نوع', 'field': 'type.name'},
            {'label': 'دسته‌بندی', 'field': 'category.name'},
            {'label': 'وضعیت', 'field': 'is_enabled', 'type': 'badge', 
             'true_label': 'فعال', 'false_label': 'غیرفعال'},
        ],
        'create_url': reverse('inventory:item_create'),
        'create_button_text': 'تعریف کالای جدید',
        'edit_url_name': 'inventory:item_edit',
        'delete_url_name': 'inventory:item_delete',
        'clear_filter_url': reverse('inventory:items'),
        'show_filters': True,
        'status_filter': True,
        'search_placeholder': 'جستجو بر اساس کد یا نام کالا',
        'empty_state_icon': '📦',
        'empty_state_title': 'هیچ کالایی ثبت نشده است',
        'empty_state_message': 'برای شروع، یک کالای جدید تعریف کنید.',
    }
    
    return render(request, 'shared/generic/generic_list.html', context)
```

---

## مثال استفاده در Template (Override)

```django
{% extends "shared/generic/generic_list.html" %}
{% load i18n %}

{% block page_title %}کالاها{% endblock %}

{% block filter_fields %}
{{ block.super }}  {# فیلدهای پیش‌فرض #}
<div class="form-group">
  <label for="type">نوع کالا</label>
  <select name="type" id="type" class="form-control">
    <option value="">-- همه انواع --</option>
    {% for item_type in item_types %}
      <option value="{{ item_type.id }}" 
              {% if request.GET.type == item_type.id|stringformat:"s" %}selected{% endif %}>
        {{ item_type.name }}
      </option>
    {% endfor %}
  </select>
</div>
{% endblock %}

{% block extra_actions %}
<a href="{% url 'inventory:item_export' %}" class="btn btn-success">
  📥 خروجی Excel
</a>
{% endblock %}
```

---

## وابستگی‌ها

### Template Tags
- `{% load i18n %}`: برای ترجمه
- `{% load generic_tags %}`: برای استفاده از `getattr` filter

### Base Template
- `base.html`: template اصلی که این template از آن extend می‌کند

### CSS Classes
Template از کلاس‌های CSS زیر استفاده می‌کند (که باید در `base.css` تعریف شده باشند):
- `.inventory-module`
- `.module-header`
- `.breadcrumb`
- `.page-title`
- `.page-actions`
- `.btn`, `.btn-primary`, `.btn-secondary`
- `.filter-panel`
- `.data-table-container`
- `.data-table`
- `.pagination`
- `.empty-state`
- `.badge`, `.badge-active`, `.badge-inactive`

---

## نکات مهم

1. **Nested Attributes**: برای دسترسی به فیلدهای nested (مثل `type.name`)، باید template tag `generic_tags` را load کنید:
   ```django
   {% load generic_tags %}
   ```

2. **Pagination**: اگر از pagination استفاده می‌کنید، باید `is_paginated` و `page_obj` را در context قرار دهید.

3. **Empty State**: اگر `object_list` خالی باشد، empty state نمایش داده می‌شود.

4. **Filter Form**: فرم فیلتر به صورت GET ارسال می‌شود و باید در view پردازش شود.

5. **Action Buttons**: دکمه‌های Edit و Delete فقط در صورتی نمایش داده می‌شوند که `edit_url_name` و `delete_url_name` تعریف شده باشند.

6. **Custom Content**: می‌توانید در `table_headers` از `custom_content` استفاده کنید برای نمایش محتوای ثابت:
   ```python
   {'label': 'عملیات', 'custom_content': 'سفارشی'}
   ```

7. **URL Patterns**: برای `edit_url_name` و `delete_url_name`، URL pattern باید یک argument `pk` بپذیرد:
   ```python
   path('items/<int:pk>/edit/', ItemUpdateView.as_view(), name='item_edit'),
   path('items/<int:pk>/delete/', ItemDeleteView.as_view(), name='item_delete'),
   ```

---

## استفاده در پروژه

این template برای تمام صفحات لیست در برنامه قابل استفاده است:
- لیست کالاها (`inventory/items.html`)
- لیست انبارها (`inventory/warehouses.html`)
- لیست پرسنل (`production/personnel.html`)
- لیست واحدهای سازمانی (`shared/company_units.html`)
- و سایر صفحات لیست

با استفاده از این template، کد تکراری کاهش می‌یابد و نگهداری آسان‌تر می‌شود.

