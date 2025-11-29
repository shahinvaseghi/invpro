# templates/shared/generic/generic_confirm_delete.html - Generic Delete Confirmation Template

**هدف**: این template یک صفحه تأیید حذف قابل استفاده مجدد برای نمایش هشدار و جزئیات شیء قبل از حذف است.

این template برای کاهش تکرار کد در صفحات تأیید حذف مختلف برنامه طراحی شده و می‌تواند برای هر نوع entity استفاده شود.

---

## ساختار Template

این template از `base.html` extend می‌کند و شامل بخش‌های زیر است:

1. **Header Section**: Breadcrumb navigation + Page title
2. **Warning Section**: پیام هشدار و سوال تأیید
3. **Object Details**: نمایش جزئیات شیء برای حذف
4. **Form Section**: فرم POST برای تأیید حذف
5. **Action Buttons**: دکمه‌های "بله، حذف شود" و "لغو"

---

## Context Variables

### الزامی

#### `object`
- **Type**: Model instance
- **توضیح**: شیء که باید حذف شود
- **مثال**: `Item.objects.get(pk=pk)`

### اختیاری

#### `delete_title`
- **Type**: `str`
- **Default**: `"Delete"`
- **توضیح**: عنوان صفحه که در `<h1>` و `<title>` نمایش داده می‌شود
- **مثال**: `"حذف کالا"`

#### `confirmation_message`
- **Type**: `str`
- **Default**: `"Do you really want to delete this item?"`
- **توضیح**: پیام تأیید که زیر سوال "آیا مطمئن هستید؟" نمایش داده می‌شود
- **مثال**: `"آیا واقعاً می‌خواهید این کالا را حذف کنید؟"`

#### `warning_message`
- **Type**: `str`
- **Default**: `"This action cannot be undone."`
- **توضیح**: پیام هشدار که در انتهای جزئیات نمایش داده می‌شود
- **مثال**: `"این عملیات قابل بازگشت نیست. تمام ردیف‌های مرتبط نیز حذف خواهند شد."`

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
      {'label': 'حذف'},
  ]
  ```

#### `cancel_url`
- **Type**: `str` (URL)
- **Default**: `request.META.HTTP_REFERER` یا `'/'`
- **توضیح**: URL برای دکمه Cancel. اگر تعریف نشود، از HTTP_REFERER استفاده می‌شود
- **مثال**: `reverse('inventory:items')`

#### `object_details`
- **Type**: `list[dict]`
- **Default**: `None`
- **توضیح**: لیست جزئیات سفارشی برای نمایش. اگر تعریف نشود، از `object.public_code` و `object.name` استفاده می‌شود
- **ساختار هر detail**:
  ```python
  {
      'label': 'برچسب',           # الزامی
      'value': value,             # الزامی - مقدار
      'type': 'code|badge',       # اختیاری - نوع نمایش
      'true_label': 'فعال',       # برای type='badge' - برچسب برای True
      'false_label': 'غیرفعال',  # برای type='badge' - برچسب برای False
  }
  ```
- **مثال**:
  ```python
  object_details = [
      {'label': 'کد کالا', 'value': item.item_code, 'type': 'code'},
      {'label': 'نام کالا', 'value': item.name},
      {'label': 'نوع', 'value': item.type.name},
      {'label': 'وضعیت', 'value': item.is_enabled, 'type': 'badge', 
       'true_label': 'فعال', 'false_label': 'غیرفعال'},
  ]
  ```

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

### `delete_details_extra`
- **موقعیت**: داخل delete-details، بعد از جزئیات پیش‌فرض
- **استفاده**: اضافه کردن جزئیات اضافی
- **مثال**:
  ```django
  {% block delete_details_extra %}
  <p><strong>تاریخ ایجاد:</strong> {{ object.created_at|date:"Y-m-d" }}</p>
  <p><strong>تعداد ردیف‌های مرتبط:</strong> {{ object.lines.count }}</p>
  {% endblock %}
  ```

### `delete_form_extra`
- **موقعیت**: داخل فرم، بعد از `{% csrf_token %}`
- **استفاده**: اضافه کردن فیلدهای hidden یا سایر محتوا به فرم
- **مثال**:
  ```django
  {% block delete_form_extra %}
  <input type="hidden" name="force_delete" value="1">
  {% endblock %}
  ```

---

## انواع نمایش در object_details

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

### نوع پیش‌فرض
- **استفاده**: برای نمایش مقادیر عادی
- **مثال**:
  ```python
  {'label': 'نام', 'value': object.name}
  ```

---

## مثال استفاده در View

### مثال 1: حذف ساده

```python
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from inventory.models import Item

def item_delete(request, pk):
    item = get_object_or_404(Item, pk=pk)
    
    if request.method == 'POST':
        item.delete()
        messages.success(request, 'کالا با موفقیت حذف شد.')
        return redirect('inventory:items')
    
    context = {
        'object': item,
        'delete_title': 'حذف کالا',
        'confirmation_message': 'آیا واقعاً می‌خواهید این کالا را حذف کنید؟',
        'breadcrumbs': [
            {'label': 'انبار', 'url': reverse('inventory:items')},
            {'label': 'کالاها', 'url': reverse('inventory:items')},
            {'label': 'حذف'},
        ],
        'cancel_url': reverse('inventory:items'),
    }
    return render(request, 'shared/generic/generic_confirm_delete.html', context)
```

### مثال 2: حذف با جزئیات سفارشی

```python
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from production.models import BOM

def bom_delete(request, pk):
    bom = get_object_or_404(BOM, pk=pk)
    
    if request.method == 'POST':
        bom.delete()
        messages.success(request, 'BOM با موفقیت حذف شد.')
        return redirect('production:bom_list')
    
    context = {
        'object': bom,
        'delete_title': 'حذف BOM',
        'confirmation_message': 'آیا واقعاً می‌خواهید این BOM را حذف کنید؟',
        'warning_message': 'این عمل غیر قابل بازگشت است. تمام ردیف‌های ماده نیز حذف خواهند شد.',
        'object_details': [
            {'label': 'کد BOM', 'value': bom.bom_code, 'type': 'code'},
            {'label': 'محصول نهایی', 'value': f'{bom.finished_item.item_code} - {bom.finished_item.name}'},
            {'label': 'نسخه', 'value': bom.version},
            {'label': 'تعداد مواد', 'value': bom.materials.count()},
            {'label': 'وضعیت', 'value': bom.is_active, 'type': 'badge', 
             'true_label': 'فعال', 'false_label': 'غیرفعال'},
        ],
        'breadcrumbs': [
            {'label': 'تولید', 'url': reverse('production:bom_list')},
            {'label': 'BOM', 'url': reverse('production:bom_list')},
            {'label': 'حذف'},
        ],
        'cancel_url': reverse('production:bom_list'),
    }
    return render(request, 'shared/generic/generic_confirm_delete.html', context)
```

### مثال 3: حذف با بررسی وابستگی‌ها

```python
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.db.models import ProtectedError
from inventory.models import Item

def item_delete(request, pk):
    item = get_object_or_404(Item, pk=pk)
    
    if request.method == 'POST':
        try:
            item.delete()
            messages.success(request, 'کالا با موفقیت حذف شد.')
            return redirect('inventory:items')
        except ProtectedError as e:
            messages.error(request, 
                f'نمی‌توان این کالا را حذف کرد زیرا در {len(e.protected_objects)} مورد استفاده شده است.')
            return redirect('inventory:item_delete', pk=pk)
    
    # بررسی وابستگی‌ها
    related_count = item.receipt_lines.count() + item.issue_lines.count()
    
    context = {
        'object': item,
        'delete_title': 'حذف کالا',
        'confirmation_message': 'آیا واقعاً می‌خواهید این کالا را حذف کنید؟',
        'warning_message': f'این عملیات قابل بازگشت نیست. این کالا در {related_count} سند استفاده شده است.',
        'object_details': [
            {'label': 'کد کالا', 'value': item.item_code, 'type': 'code'},
            {'label': 'نام کالا', 'value': item.name},
            {'label': 'نوع', 'value': item.type.name},
            {'label': 'تعداد استفاده', 'value': related_count},
        ],
        'breadcrumbs': [
            {'label': 'انبار', 'url': reverse('inventory:items')},
            {'label': 'کالاها', 'url': reverse('inventory:items')},
            {'label': 'حذف'},
        ],
        'cancel_url': reverse('inventory:items'),
    }
    return render(request, 'shared/generic/generic_confirm_delete.html', context)
```

---

## مثال استفاده در Template (Override)

```django
{% extends "shared/generic/generic_confirm_delete.html" %}
{% load i18n %}

{% block delete_title %}حذف کالا{% endblock %}

{% block delete_details_extra %}
<p><strong>تاریخ ایجاد:</strong> {{ object.created_at|date:"Y-m-d H:i" }}</p>
<p><strong>ایجاد کننده:</strong> {{ object.created_by.username }}</p>
<p><strong>تعداد رسیدها:</strong> {{ object.receipt_lines.count }}</p>
<p><strong>تعداد حواله‌ها:</strong> {{ object.issue_lines.count }}</p>
{% endblock %}

{% block delete_form_extra %}
<input type="hidden" name="force_delete" value="1">
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
- `.delete-warning`
- `.delete-details`
- `.warning-text`
- `.form-actions`
- `.btn`, `.btn-danger`, `.btn-secondary`
- `.badge`, `.badge-active`, `.badge-inactive`

---

## نکات مهم

1. **Object Details**: اگر `object_details` تعریف نشود، template به صورت خودکار `object.public_code` و `object.name` را نمایش می‌دهد (اگر موجود باشند).

2. **Warning Message**: پیام هشدار به صورت قرمز و bold نمایش داده می‌شود.

3. **Form Method**: فرم به صورت POST ارسال می‌شود و باید در view پردازش شود.

4. **Cancel URL**: اگر `cancel_url` تعریف نشود، از `request.META.HTTP_REFERER` استفاده می‌شود.

5. **ProtectedError**: برای entity هایی که ممکن است وابستگی داشته باشند، باید در view از try-except استفاده کنید.

6. **Badge Display**: برای نمایش badge، مقدار باید boolean باشد. برای مقادیر دیگر، از نوع پیش‌فرض استفاده کنید.

7. **Code Display**: برای نمایش کد، از `type='code'` استفاده کنید تا با استایل `<code>` نمایش داده شود.

---

## استفاده در پروژه

این template برای تمام صفحات تأیید حذف در برنامه قابل استفاده است:
- حذف کالا (`inventory/item_delete.html`)
- حذف انبار (`inventory/warehouse_delete.html`)
- حذف BOM (`production/bom_delete.html`)
- حذف واحدهای سازمانی (`shared/company_unit_delete.html`)
- و سایر صفحات حذف

با استفاده از این template، کد تکراری کاهش می‌یابد و نگهداری آسان‌تر می‌شود.

