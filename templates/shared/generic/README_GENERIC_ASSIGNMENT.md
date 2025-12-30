# templates/shared/generic/generic_assignment.html - Generic Assignment/Workflow Template

**هدف**: این template یک صفحه Assignment/Workflow قابل استفاده مجدد برای صفحاتی که نیاز به ویرایش inline در جدول دارند (مثل serial assignment، selection، management) است.

این template برای کاهش تکرار کد در صفحات Assignment، Selection، و Management مختلف برنامه طراحی شده است.

---

## ساختار Template

این template از `base.html` extend می‌کند و شامل بخش‌های زیر است:

1. **Header Section**: Breadcrumb navigation + Page title
2. **Info Banner**: نمایش اطلاعات مهم
3. **Action Bar**: دکمه‌های عملیات (Back, Edit, Lock, و غیره)
4. **Editable Table**: جدول با فیلدهای قابل ویرایش
5. **Summary Info**: اطلاعات خلاصه
6. **Form Actions**: دکمه‌های Save و Cancel

---

## Context Variables

### اختیاری

#### `assignment_title`
- **Type**: `str`
- **Default**: `"Assignment"`
- **توضیح**: عنوان صفحه
- **مثال**: `"Receipt Serials"` یا `"QC Line Selection"`

#### `breadcrumbs`
- **Type**: `list[dict]`
- **Default**: `[]`
- **توضیح**: لیست breadcrumb برای navigation

#### `info_banner`
- **Type**: `list[dict]`
- **Default**: `None`
- **توضیح**: اطلاعات مهم برای نمایش در banner
- **ساختار**: مشابه `generic_detail.html`

#### `action_bar_buttons`
- **Type**: `list[dict]`
- **Default**: `None`
- **توضیح**: لیست دکمه‌های action bar
- **ساختار هر button**:
  ```python
  {
      'type': 'link|form|button',    # الزامی
      'label': 'Back to List',       # الزامی
      'url': 'url_path',             # برای type='link' یا 'form'
      'color': 'secondary',          # اختیاری - رنگ دکمه
      'onclick': 'function()',      # برای type='button'
  }
  ```
- **مثال**:
  ```python
  action_bar_buttons = [
      {'type': 'link', 'label': 'Back to List', 'url': reverse('inventory:receipt_temporary'), 'color': 'secondary'},
      {'type': 'link', 'label': 'Edit Document', 'url': reverse('inventory:receipt_temporary_edit', args=[receipt.pk]), 'color': 'secondary'},
      {'type': 'form', 'label': 'Lock Document', 'url': reverse('inventory:receipt_temporary_lock', args=[receipt.pk]), 'color': 'warning'},
  ]
  ```

#### `editable_table`
- **Type**: `bool`
- **Default**: `False`
- **توضیح**: آیا جدول editable است یا نه

#### `form_description`
- **Type**: `str`
- **Default**: `None`
- **توضیح**: توضیحات فرم که بالای جدول نمایش داده می‌شود

#### `table_headers`
- **Type**: `list[str]`
- **Default**: `None`
- **توضیح**: لیست هدرهای جدول
- **مثال**: `['Serial', 'Secondary Serial', 'Lot', 'Status', 'Actions']`

#### `table_data`
- **Type**: `list[dict]`
- **Default**: `None`
- **توضیح**: لیست ردیف‌های جدول
- **ساختار هر row**:
  ```python
  {
      'row_id': 'pk',              # اختیاری - ID ردیف
      'cells': [                    # الزامی - لیست سلول‌ها
          {
              'type': 'input|textarea|select|checkbox|code|badge|button|text',
              'name': 'field_name',  # برای input, textarea, select, checkbox
              'value': 'value',      # مقدار
              'input_type': 'text|number',  # برای type='input'
              'placeholder': '...',  # برای input, textarea
              'required': True,      # برای input, textarea, select
              'readonly': False,    # برای input
              'min': 0,             # برای input type='number'
              'max': 100,           # برای input type='number'
              'step': 0.001,        # برای input type='number'
              'rows': 2,            # برای textarea
              'options': [          # برای select
                  {'value': '1', 'label': 'Option 1', 'selected': False},
              ],
              'checked': False,     # برای checkbox
              'label': 'Save',      # برای button
              'color': 'primary',   # برای button
              'onclick': '...',     # برای button
              'data_attr': {'name': 'serial-id', 'value': '123'},  # برای button
          },
      ],
  }
  ```
- **مثال**:
  ```python
  table_data = [
      {
          'row_id': serial.pk,
          'cells': [
              {'type': 'code', 'value': serial.serial_code},
              {
                  'type': 'input',
                  'name': f'secondary_serial_{serial.pk}',
                  'value': serial.secondary_serial_code or '',
                  'placeholder': 'Enter secondary serial',
              },
              {'type': 'code', 'value': serial.lot_code or '-'},
              {'type': 'text', 'value': serial.get_current_status_display()},
              {
                  'type': 'button',
                  'label': 'Save',
                  'color': 'primary',
                  'onclick': f'saveSerial({serial.pk})',
                  'data_attr': {'name': 'serial-id', 'value': serial.pk},
              },
          ],
      },
  ]
  ```

#### `summary_info`
- **Type**: `list[dict]`
- **Default**: `None`
- **توضیح**: اطلاعات خلاصه برای نمایش
- **ساختار**:
  ```python
  [
      {'label': 'Serials Generated', 'value': 150},
      {'label': 'Remaining', 'value': 10},
  ]
  ```

#### `form_id`
- **Type**: `str`
- **Default**: `None`
- **توضیح**: ID برای فرم

#### `submit_button_text`
- **Type**: `str`
- **Default**: `"Save"`
- **توضیح**: متن دکمه Submit

#### `cancel_url`
- **Type**: `str` (URL)
- **Default**: `request.META.HTTP_REFERER` یا `'/'`
- **توضیح**: URL برای دکمه Cancel

---

## Blocks قابل Override

### `breadcrumb_extra`
- **موقعیت**: بعد از breadcrumb اصلی
- **استفاده**: اضافه کردن breadcrumb اضافی

### `info_banner_extra`
- **موقعیت**: داخل info banner
- **استفاده**: اضافه کردن اطلاعات اضافی

### `action_bar`
- **موقعیت**: action bar
- **استفاده**: سفارشی‌سازی کامل action bar

### `action_bar_extra`
- **موقعیت**: داخل action bar
- **استفاده**: اضافه کردن دکمه‌های اضافی

### `assignment_content`
- **موقعیت**: بخش اصلی محتوا
- **استفاده**: سفارشی‌سازی کامل محتوا

### `editable_table_rows`
- **موقعیت**: در `<tbody>` جدول
- **استفاده**: سفارشی‌سازی ردیف‌های جدول

### `static_content`
- **موقعیت**: وقتی `editable_table=False`
- **استفاده**: محتوای static (مثل نمایش read-only)

### `form_actions_extra`
- **موقعیت**: در form actions
- **استفاده**: اضافه کردن دکمه‌های اضافی

### `assignment_scripts`
- **موقعیت**: در انتهای template
- **استفاده**: اضافه کردن JavaScript

---

## انواع سلول‌ها در table_data

### `input`
- **پارامترها**: `name`, `value`, `input_type` (text/number), `placeholder`, `required`, `readonly`, `min`, `max`, `step`

### `textarea`
- **پارامترها**: `name`, `value`, `rows`, `placeholder`, `required`

### `select`
- **پارامترها**: `name`, `options` (list of {value, label, selected}), `required`, `placeholder`

### `checkbox`
- **پارامترها**: `name`, `value`, `checked`

### `code`
- **پارامترها**: `value`

### `badge`
- **پارامترها**: `value` (boolean), `true_label`, `false_label`, `badge_type`

### `button`
- **پارامترها**: `label`, `color`, `onclick`, `data_attr`

### `text`
- **پارامترها**: `value`

---

## مثال استفاده در View

```python
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from inventory.models import ReceiptTemporary

def receipt_serial_assignment(request, pk):
    receipt = get_object_or_404(ReceiptTemporary, pk=pk)
    serials = receipt.serials.all()
    
    # آماده‌سازی table data
    table_data = []
    for serial in serials:
        table_data.append({
            'row_id': serial.pk,
            'cells': [
                {'type': 'code', 'value': serial.serial_code},
                {
                    'type': 'input',
                    'name': f'secondary_serial_{serial.pk}',
                    'value': serial.secondary_serial_code or '',
                    'placeholder': 'Enter secondary serial',
                },
                {'type': 'code', 'value': serial.lot_code or '-'},
                {'type': 'text', 'value': serial.get_current_status_display()},
                {
                    'type': 'button',
                    'label': 'Save',
                    'color': 'primary',
                    'onclick': f'saveSecondarySerial({serial.pk})',
                    'data_attr': {'name': 'serial-id', 'value': serial.pk},
                },
            ],
        })
    
    context = {
        'assignment_title': 'Receipt Serials',
        'breadcrumbs': [
            {'label': 'انبار', 'url': reverse('inventory:receipt_temporary')},
            {'label': 'رسیدهای موقت', 'url': reverse('inventory:receipt_temporary')},
            {'label': 'Serials'},
        ],
        'info_banner': [
            {'label': 'Document', 'value': receipt.document_code, 'type': 'code'},
            {'label': 'Item', 'value': f'{receipt.item.name} ({receipt.item.item_code})'},
            {'label': 'Quantity', 'value': f'{receipt.quantity} {receipt.unit}'},
        ],
        'action_bar_buttons': [
            {'type': 'link', 'label': 'Back to List', 'url': reverse('inventory:receipt_temporary'), 'color': 'secondary'},
            {'type': 'link', 'label': 'Edit Document', 'url': reverse('inventory:receipt_temporary_edit', args=[receipt.pk]), 'color': 'secondary'},
        ],
        'editable_table': True,
        'table_headers': ['Serial', 'Secondary Serial', 'Lot', 'Status', 'Actions'],
        'table_data': table_data,
        'summary_info': [
            {'label': 'Serials Generated', 'value': serials.count()},
            {'label': 'Remaining', 'value': receipt.quantity - serials.count()},
        ],
        'form_id': 'serial-assignment-form',
        'cancel_url': reverse('inventory:receipt_temporary'),
    }
    return render(request, 'shared/generic/generic_assignment.html', context)
```

---

## وابستگی‌ها

### Template Tags
- `{% load i18n %}`: برای ترجمه

### Base Template
- `base.html`: template اصلی که این template از آن extend می‌کند

---

## نکات مهم

1. **Editable Table**: برای جدول‌های editable، باید `editable_table=True` و `table_data` را تعریف کنید.

2. **Form Submission**: فرم به صورت POST ارسال می‌شود و باید در view پردازش شود.

3. **JavaScript**: برای تعاملات پیچیده (مثل save inline، add/remove rows)، باید از block `assignment_scripts` استفاده کنید.

4. **Static Content**: اگر `editable_table=False` باشد، می‌توانید از block `static_content` برای نمایش محتوای read-only استفاده کنید.

---

## استفاده در پروژه

این template برای صفحات زیر قابل استفاده است:
- Serial Assignment (`inventory/receipt_serial_assignment.html`)
- Line Selection (`qc/temporary_receipt_line_selection.html`)
- Rejection Management (`qc/temporary_receipt_rejection_management.html`)
- Buyer Assignment (`procurement/buyer_assignment.html`)
- و سایر صفحات Assignment/Workflow

با استفاده از این template، کد تکراری کاهش می‌یابد و نگهداری آسان‌تر می‌شود.

