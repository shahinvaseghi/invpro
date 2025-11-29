# templates/shared/generic/generic_detail.html - Generic Detail/View Template

**هدف**: این template یک صفحه جزئیات قابل استفاده مجدد برای نمایش اطلاعات کامل یک شیء با پشتیبانی از sections مختلف، tables، و action buttons است.

این template برای کاهش تکرار کد در صفحات جزئیات مختلف برنامه طراحی شده و می‌تواند برای هر نوع entity استفاده شود.

---

## ساختار Template

این template از `base.html` extend می‌کند و شامل بخش‌های زیر است:

1. **Header Section**: Breadcrumb navigation + Page title
2. **Info Banner**: نمایش اطلاعات مهم در بالای صفحه
3. **Alert Message**: پیام‌های هشدار یا اطلاع‌رسانی (اختیاری)
4. **Detail Sections**: بخش‌های مختلف (fields, tables, custom)
5. **Action Buttons**: دکمه‌های بازگشت، ویرایش، حذف

---

## Context Variables

### اختیاری

#### `detail_title`
- **Type**: `str`
- **Default**: `"Details"`
- **توضیح**: عنوان صفحه که در `<h1>` و `<title>` نمایش داده می‌شود
- **مثال**: `"جزئیات کالا"`

#### `breadcrumbs`
- **Type**: `list[dict]`
- **Default**: `[]`
- **توضیح**: لیست breadcrumb برای navigation
- **ساختار هر breadcrumb**:
  ```python
  {
      'label': 'نام',      # الزامی
      'url': 'url_path',   # اختیاری
  }
  ```
- **مثال**:
  ```python
  breadcrumbs = [
      {'label': 'انبار', 'url': reverse('inventory:items')},
      {'label': 'کالاها', 'url': reverse('inventory:items')},
      {'label': 'جزئیات'},
  ]
  ```

#### `info_banner`
- **Type**: `list[dict]`
- **Default**: `None`
- **توضیح**: اطلاعات مهم برای نمایش در banner بالای صفحه
- **ساختار هر item**:
  ```python
  {
      'label': 'برچسب',           # الزامی
      'value': value,             # الزامی - مقدار
      'type': 'code|badge|date',  # اختیاری - نوع نمایش
      'true_label': 'فعال',       # برای type='badge' - برچسب برای True
      'false_label': 'غیرفعال',  # برای type='badge' - برچسب برای False
  }
  ```
- **مثال**:
  ```python
  info_banner = [
      {'label': 'کد سند', 'value': receipt.document_code, 'type': 'code'},
      {'label': 'تاریخ سند', 'value': receipt.document_date, 'type': 'date'},
      {'label': 'وضعیت', 'value': receipt.is_locked, 'type': 'badge', 
       'true_label': 'قفل شده', 'false_label': 'قابل ویرایش'},
  ]
  ```

#### `alert_message`
- **Type**: `str`
- **Default**: `None`
- **توضیح**: پیام alert برای نمایش (مثلاً هشدار قفل بودن سند)
- **مثال**: `"این سند قفل شده است و قابل ویرایش نیست."`

#### `alert_type`
- **Type**: `str`
- **Default**: `'info'`
- **مقادیر ممکن**: `'info'`, `'warning'`, `'danger'`
- **توضیح**: نوع alert (رنگ و استایل)

#### `detail_sections`
- **Type**: `list[dict]`
- **Default**: `None`
- **توضیح**: لیست sections برای نمایش جزئیات
- **ساختار هر section**:
  ```python
  {
      'title': 'عنوان بخش',      # الزامی
      'type': 'fields|table|custom',  # الزامی - نوع section
      # برای type='fields':
      'fields': [                 # لیست فیلدها
          {
              'label': 'برچسب',
              'value': value,
              'type': 'code|badge|link',  # اختیاری
              'url': 'url_path',           # برای type='link'
              'true_label': 'فعال',        # برای type='badge'
              'false_label': 'غیرفعال',   # برای type='badge'
          },
      ],
      # برای type='table':
      'headers': ['ستون 1', 'ستون 2', ...],  # لیست هدرها
      'data': [                               # لیست ردیف‌ها
          ['مقدار 1', 'مقدار 2', ...],
          ['مقدار 3', 'مقدار 4', ...],
      ],
      # برای type='custom':
      'content': '<div>...</div>',  # HTML سفارشی
  }
  ```
- **مثال**:
  ```python
  detail_sections = [
      {
          'title': 'اطلاعات اولیه',
          'type': 'fields',
          'fields': [
              {'label': 'کد کالا', 'value': item.item_code, 'type': 'code'},
              {'label': 'نام کالا', 'value': item.name},
              {'label': 'نوع', 'value': item.type.name},
              {'label': 'وضعیت', 'value': item.is_enabled, 'type': 'badge', 
               'true_label': 'فعال', 'false_label': 'غیرفعال'},
          ],
      },
      {
          'title': 'ردیف‌های سند',
          'type': 'table',
          'headers': ['ردیف', 'کالا', 'تعداد', 'واحد'],
          'data': [
              ['1', 'کالای 1', '10', 'عدد'],
              ['2', 'کالای 2', '20', 'کیلوگرم'],
          ],
      },
  ]
  ```

#### `list_url`
- **Type**: `str` (URL)
- **Default**: `None`
- **توضیح**: URL برای دکمه "بازگشت به لیست"
- **مثال**: `reverse('inventory:items')`

#### `edit_url`
- **Type**: `str` (URL)
- **Default**: `None`
- **توضیح**: URL برای دکمه "ویرایش"
- **مثال**: `reverse('inventory:item_edit', args=[item.pk])`

#### `delete_url`
- **Type**: `str` (URL)
- **Default**: `None`
- **توضیح**: URL برای دکمه "حذف"
- **مثال**: `reverse('inventory:item_delete', args=[item.pk])`

#### `can_edit`
- **Type**: `bool`
- **Default**: `True`
- **توضیح**: آیا دکمه ویرایش نمایش داده شود یا نه (مثلاً برای سندهای قفل شده)

#### `can_delete`
- **Type**: `bool`
- **Default**: `True`
- **توضیح**: آیا دکمه حذف نمایش داده شود یا نه

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

### `info_banner_extra`
- **موقعیت**: داخل info banner
- **استفاده**: اضافه کردن اطلاعات اضافی در banner
- **مثال**:
  ```django
  {% block info_banner_extra %}
  <div><strong>قفل شده توسط:</strong> {{ object.locked_by.username }}</div>
  {% endblock %}
  ```

### `detail_sections`
- **موقعیت**: بخش اصلی جزئیات
- **استفاده**: سفارشی‌سازی کامل sections
- **نکته**: اگر override شود، `detail_sections` context variable استفاده نمی‌شود
- **مثال**:
  ```django
  {% block detail_sections %}
  <div class="form-section">
    <h3>اطلاعات اولیه</h3>
    <div class="form-row">
      <div class="form-field">
        <label>کد کالا</label>
        <div class="readonly-field">
          <code>{{ item.item_code }}</code>
        </div>
      </div>
    </div>
  </div>
  {% endblock %}
  ```

### `detail_actions_extra`
- **موقعیت**: در بخش action buttons، بعد از دکمه‌های پیش‌فرض
- **استفاده**: اضافه کردن دکمه‌های اضافی
- **مثال**:
  ```django
  {% block detail_actions_extra %}
  <a href="{% url 'inventory:item_print' item.pk %}" class="btn btn-info">
    چاپ
  </a>
  {% endblock %}
  ```

---

## انواع نمایش در info_banner و detail_sections

### نوع `code`
- **استفاده**: برای نمایش کدها با استایل `<code>`
- **مثال**:
  ```python
  {'label': 'کد', 'value': object.public_code, 'type': 'code'}
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
      'value': object.is_enabled, 
      'type': 'badge',
      'true_label': 'فعال',
      'false_label': 'غیرفعال'
  }
  ```

### نوع `date`
- **استفاده**: برای نمایش تاریخ (فقط در info_banner)
- **مثال**:
  ```python
  {'label': 'تاریخ', 'value': object.date, 'type': 'date'}
  ```

### نوع `link`
- **استفاده**: برای نمایش لینک (فقط در detail_sections fields)
- **پارامترهای اضافی**:
  - `url`: URL برای لینک
- **مثال**:
  ```python
  {
      'label': 'تامین‌کننده', 
      'value': object.supplier.name, 
      'type': 'link',
      'url': reverse('inventory:supplier_detail', args=[object.supplier.pk])
  }
  ```

### نوع `table`
- **استفاده**: برای نمایش جدول داده‌ها
- **ساختار**:
  ```python
  {
      'title': 'عنوان',
      'type': 'table',
      'headers': ['ستون 1', 'ستون 2'],
      'data': [
          ['مقدار 1', 'مقدار 2'],
          ['مقدار 3', 'مقدار 4'],
      ],
  }
  ```

### نوع `custom`
- **استفاده**: برای نمایش HTML سفارشی
- **ساختار**:
  ```python
  {
      'title': 'عنوان',
      'type': 'custom',
      'content': '<div>HTML سفارشی</div>',
  }
  ```
- **نکته**: محتوا با `|safe` filter render می‌شود

---

## مثال استفاده در View

### مثال 1: جزئیات ساده

```python
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from inventory.models import Item

def item_detail(request, pk):
    item = get_object_or_404(Item, pk=pk)
    
    context = {
        'detail_title': f'جزئیات کالا: {item.name}',
        'breadcrumbs': [
            {'label': 'انبار', 'url': reverse('inventory:items')},
            {'label': 'کالاها', 'url': reverse('inventory:items')},
            {'label': 'جزئیات'},
        ],
        'info_banner': [
            {'label': 'کد کالا', 'value': item.item_code, 'type': 'code'},
            {'label': 'وضعیت', 'value': item.is_enabled, 'type': 'badge', 
             'true_label': 'فعال', 'false_label': 'غیرفعال'},
        ],
        'detail_sections': [
            {
                'title': 'اطلاعات اولیه',
                'type': 'fields',
                'fields': [
                    {'label': 'نام کالا', 'value': item.name},
                    {'label': 'نام انگلیسی', 'value': item.name_en},
                    {'label': 'نوع', 'value': item.type.name},
                    {'label': 'دسته‌بندی', 'value': item.category.name},
                ],
            },
            {
                'title': 'اطلاعات تکمیلی',
                'type': 'fields',
                'fields': [
                    {'label': 'توضیحات', 'value': item.description or '-'},
                    {'label': 'یادداشت‌ها', 'value': item.notes or '-'},
                ],
            },
        ],
        'list_url': reverse('inventory:items'),
        'edit_url': reverse('inventory:item_edit', args=[item.pk]),
        'delete_url': reverse('inventory:item_delete', args=[item.pk]),
        'can_edit': True,
        'can_delete': True,
    }
    return render(request, 'shared/generic/generic_detail.html', context)
```

### مثال 2: جزئیات با جدول

```python
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from inventory.models import ReceiptTemporary

def receipt_detail(request, pk):
    receipt = get_object_or_404(ReceiptTemporary, pk=pk)
    
    # آماده‌سازی داده‌های جدول
    table_data = []
    for line in receipt.lines.all():
        table_data.append([
            str(line.line_number),
            f'{line.item.item_code} - {line.item.name}',
            str(line.quantity),
            line.unit,
            line.warehouse.name,
        ])
    
    context = {
        'detail_title': f'جزئیات رسید: {receipt.document_code}',
        'breadcrumbs': [
            {'label': 'انبار', 'url': reverse('inventory:receipt_temporary')},
            {'label': 'رسیدهای موقت', 'url': reverse('inventory:receipt_temporary')},
            {'label': 'جزئیات'},
        ],
        'info_banner': [
            {'label': 'کد سند', 'value': receipt.document_code, 'type': 'code'},
            {'label': 'تاریخ سند', 'value': receipt.document_date, 'type': 'date'},
            {'label': 'وضعیت قفل', 'value': receipt.is_locked, 'type': 'badge', 
             'true_label': 'قفل شده', 'false_label': 'قابل ویرایش'},
        ],
        'alert_message': 'این سند قفل شده است و قابل ویرایش نیست.' if receipt.is_locked else None,
        'alert_type': 'warning' if receipt.is_locked else None,
        'detail_sections': [
            {
                'title': 'اطلاعات سند',
                'type': 'fields',
                'fields': [
                    {'label': 'تامین‌کننده', 'value': receipt.supplier.name if receipt.supplier else '-'},
                    {'label': 'تاریخ مورد انتظار', 'value': receipt.expected_receipt_date or '-'},
                ],
            },
            {
                'title': 'ردیف‌های سند',
                'type': 'table',
                'headers': ['ردیف', 'کالا', 'تعداد', 'واحد', 'انبار'],
                'data': table_data,
            },
        ],
        'list_url': reverse('inventory:receipt_temporary'),
        'edit_url': reverse('inventory:receipt_temporary_edit', args=[receipt.pk]) if not receipt.is_locked else None,
        'delete_url': reverse('inventory:receipt_temporary_delete', args=[receipt.pk]) if not receipt.is_locked else None,
        'can_edit': not receipt.is_locked,
        'can_delete': not receipt.is_locked,
    }
    return render(request, 'shared/generic/generic_detail.html', context)
```

### مثال 3: جزئیات با محتوای سفارشی

```python
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.utils.safestring import mark_safe
from inventory.models import Item

def item_detail(request, pk):
    item = get_object_or_404(Item, pk=pk)
    
    # محتوای سفارشی برای نمودار
    chart_html = f'''
    <div id="item-chart" data-item-id="{item.pk}">
        <canvas id="chart-canvas"></canvas>
    </div>
    <script>
        // Chart initialization code
    </script>
    '''
    
    context = {
        'detail_title': f'جزئیات کالا: {item.name}',
        'breadcrumbs': [
            {'label': 'انبار', 'url': reverse('inventory:items')},
            {'label': 'کالاها', 'url': reverse('inventory:items')},
            {'label': 'جزئیات'},
        ],
        'info_banner': [
            {'label': 'کد کالا', 'value': item.item_code, 'type': 'code'},
        ],
        'detail_sections': [
            {
                'title': 'اطلاعات اولیه',
                'type': 'fields',
                'fields': [
                    {'label': 'نام', 'value': item.name},
                    {'label': 'نوع', 'value': item.type.name},
                ],
            },
            {
                'title': 'نمودار موجودی',
                'type': 'custom',
                'content': mark_safe(chart_html),
            },
        ],
        'list_url': reverse('inventory:items'),
        'edit_url': reverse('inventory:item_edit', args=[item.pk]),
    }
    return render(request, 'shared/generic/generic_detail.html', context)
```

---

## مثال استفاده در Template (Override)

```django
{% extends "shared/generic/generic_detail.html" %}
{% load i18n %}

{% block detail_title %}جزئیات کالا{% endblock %}

{% block info_banner_extra %}
<div><strong>تاریخ ایجاد:</strong> {{ item.created_at|date:"Y-m-d H:i" }}</div>
<div><strong>ایجاد کننده:</strong> {{ item.created_by.username }}</div>
{% endblock %}

{% block detail_actions_extra %}
<a href="{% url 'inventory:item_print' item.pk %}" class="btn btn-info">
  چاپ
</a>
<a href="{% url 'inventory:item_history' item.pk %}" class="btn btn-secondary">
  تاریخچه
</a>
{% endblock %}
```

---

## وابستگی‌ها

### Template Tags
- `{% load i18n %}`: برای ترجمه

### Base Template
- `base.html`: template اصلی که این template از آن extend می‌کند

### CSS Classes
Template از کلاس‌های CSS زیر استفاده می‌کند:
- `.inventory-module`
- `.module-header`
- `.breadcrumb`
- `.page-title`
- `.form-container`
- `.info-banner`
- `.form-section`
- `.form-row`
- `.form-field`
- `.readonly-field`
- `.data-table-container`
- `.data-table`
- `.alert`, `.alert-info`, `.alert-warning`, `.alert-danger`
- `.form-actions`
- `.btn`, `.btn-primary`, `.btn-secondary`, `.btn-danger`
- `.badge`, `.badge-active`, `.badge-inactive`

---

## نکات مهم

1. **Empty Data**: اگر `detail_sections` تعریف نشود یا خالی باشد، هیچ section نمایش داده نمی‌شود.

2. **Table Data**: برای sections با `type='table'`، اگر `data` خالی باشد، پیام "No data available." نمایش داده می‌شود.

3. **Custom Content**: برای sections با `type='custom'`، محتوا با `|safe` filter render می‌شود. باید از `mark_safe()` در view استفاده کنید.

4. **Link Fields**: برای fields با `type='link'`، باید `url` تعریف شود.

5. **Date Format**: برای `type='date'` در info_banner، تاریخ با فرمت `Y-m-d` نمایش داده می‌شود.

6. **Action Buttons**: دکمه‌ها فقط در صورتی نمایش داده می‌شوند که URL مربوطه تعریف شده باشد و permission موجود باشد (`can_edit`, `can_delete`).

7. **Alert Message**: اگر `alert_message` تعریف شود، با نوع `alert_type` نمایش داده می‌شود.

---

## استفاده در پروژه

این template برای تمام صفحات جزئیات در برنامه قابل استفاده است:
- جزئیات کالا (`inventory/item_detail.html`)
- جزئیات رسید (`inventory/receipt_detail.html`)
- جزئیات حواله (`inventory/issue_detail.html`)
- و سایر صفحات جزئیات

با استفاده از این template، کد تکراری کاهش می‌یابد و نگهداری آسان‌تر می‌شود.

