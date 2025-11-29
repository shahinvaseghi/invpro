# templates/shared/generic/generic_report.html - Generic Report/Analysis Template

**هدف**: این template یک صفحه Report/Analysis قابل استفاده مجدد برای نمایش گزارش‌ها و تحلیل‌ها با فیلتر، آمار خلاصه و جدول داده است.

این template برای کاهش تکرار کد در صفحات Report و Analysis مختلف برنامه طراحی شده است.

---

## ساختار Template

این template از `base.html` extend می‌کند و شامل بخش‌های زیر است:

1. **Header Section**: Breadcrumb navigation + Page title + Action buttons (Print, Export)
2. **Filter Panel**: پنل فیلتر برای محدود کردن داده‌ها
3. **Stats Summary**: کارت‌های آمار خلاصه
4. **Data Table**: جدول داده‌های گزارش
5. **Empty State**: حالت خالی برای زمانی که داده‌ای وجود ندارد

---

## Context Variables

### اختیاری

#### `report_title`
- **Type**: `str`
- **Default**: `"Report"`
- **توضیح**: عنوان گزارش
- **مثال**: `"Inventory Balance"` یا `"موجودی انبار"`

#### `breadcrumbs`
- **Type**: `list[dict]`
- **Default**: `[]`
- **توضیح**: لیست breadcrumb برای navigation

#### `print_enabled`
- **Type**: `bool`
- **Default**: `True`
- **توضیح**: نمایش یا عدم نمایش دکمه Print

#### `export_enabled`
- **Type**: `bool`
- **Default**: `True`
- **توضیح**: نمایش یا عدم نمایش دکمه Export Excel

#### `export_function`
- **Type**: `str` (JavaScript function name)
- **Default**: `"exportToExcel()"`
- **توضیح**: نام تابع JavaScript برای export (می‌توانید override کنید)

#### `export_filename`
- **Type**: `str`
- **Default**: `"report"`
- **توضیح**: نام فایل export

#### `show_filters`
- **Type**: `bool`
- **Default**: `True`
- **توضیح**: نمایش یا عدم نمایش پنل فیلتر

#### `filter_fields`
- **Type**: `list[dict]`
- **Default**: `None`
- **توضیح**: لیست فیلدهای فیلتر
- **ساختار هر field**:
  ```python
  {
      'id': 'warehouse_id',         # الزامی - ID فیلد
      'name': 'warehouse_id',       # الزامی - name فیلد
      'label': 'Select Warehouse',  # الزامی - برچسب
      'type': 'select|date|text',   # الزامی - نوع فیلد
      'required': True,              # اختیاری - آیا required است
      'placeholder': '...',         # اختیاری - placeholder
      'value': '1',                 # اختیاری - مقدار پیش‌فرض
      'options': [                  # برای type='select'
          {'value': '1', 'label': 'Warehouse 1', 'selected': False},
      ],
  }
  ```
- **مثال**:
  ```python
  filter_fields = [
      {
          'id': 'warehouse_id',
          'name': 'warehouse_id',
          'label': 'Select Warehouse',
          'type': 'select',
          'required': True,
          'options': [
              {'value': str(w.id), 'label': f'{w.public_code} - {w.name}', 
               'selected': str(w.id) == selected_warehouse_id}
              for w in warehouses
          ],
      },
      {
          'id': 'item_type_id',
          'name': 'item_type_id',
          'label': 'Select Item Type',
          'type': 'select',
          'required': False,
          'options': [
              {'value': str(t.id), 'label': f'{t.public_code} - {t.name}', 
               'selected': str(t.id) == selected_item_type_id}
              for t in item_types
          ],
      },
  ]
  ```

#### `filter_submit_text`
- **Type**: `str`
- **Default**: `"اعمال فیلتر"`
- **توضیح**: متن دکمه Submit فیلتر

#### `stats_summary`
- **Type**: `list[dict]`
- **Default**: `None`
- **توضیح**: لیست کارت‌های آمار خلاصه
- **ساختار هر stat**:
  ```python
  {
      'label': 'Total Items',       # الزامی
      'value': 150,                 # الزامی - مقدار اصلی
      'sub_value': 'Last updated: ...',  # اختیاری - مقدار فرعی
      'color': 'blue|green|orange|red',  # اختیاری - رنگ کارت
  }
  ```
- **مثال**:
  ```python
  stats_summary = [
      {'label': 'Total Items', 'value': total_items, 'color': 'blue'},
      {'label': 'Total Balance', 'value': f'{total_balance:.2f}', 'color': 'green'},
      {'label': 'Last Calculated', 'value': as_of_date.strftime('%Y-%m-%d'), 'color': 'orange'},
  ]
  ```

#### `table_id`
- **Type**: `str`
- **Default**: `"reportTable"`
- **توضیح**: ID برای جدول (برای استفاده در JavaScript export)

#### `table_headers`
- **Type**: `list[str]`
- **Default**: `None`
- **توضیح**: لیست هدرهای جدول
- **مثال**: `['Item Code', 'Item Name', 'Balance', 'Actions']`

#### `table_data`
- **Type**: `list[list[dict]]`
- **Default**: `None`
- **توضیح**: لیست ردیف‌های جدول
- **ساختار هر cell**:
  ```python
  {
      'type': 'code|badge|link|number|color_number|text',
      'value': value,               # الزامی - مقدار
      'label': '...',               # برای badge - برچسب
      'url': 'url_path',            # برای link - URL
      'color': '#10b981',           # برای color_number - رنگ
      'decimals': 2,                 # برای number - تعداد اعشار
      'badge_type': 'active',       # برای badge - نوع badge
      'true_label': 'Active',       # برای badge - برچسب True
      'false_label': 'Inactive',    # برای badge - برچسب False
  }
  ```
- **مثال**:
  ```python
  table_data = [
      [
          {'type': 'code', 'value': balance.item_code},
          {'type': 'text', 'value': balance.item_name},
          {'type': 'number', 'value': balance.baseline_quantity, 'decimals': 2},
          {'type': 'color_number', 'value': balance.receipts_total, 'color': '#10b981', 'decimals': 2},
          {'type': 'color_number', 'value': balance.issues_total, 'color': '#ef4444', 'decimals': 2},
          {'type': 'color_number', 'value': balance.current_balance, 
           'color': '#10b981' if balance.current_balance > 0 else '#ef4444', 'decimals': 2},
          {
              'type': 'link',
              'value': 'Details',
              'url': reverse('inventory:balance_details', args=[balance.item_id, balance.warehouse_id]),
          },
      ],
      # ... more rows
  ]
  ```

#### `empty_state_icon`
- **Type**: `str`
- **Default**: `"📊"`
- **توضیح**: آیکون برای حالت خالی

#### `empty_state_title`
- **Type**: `str`
- **Default**: `"No data found"`
- **توضیح**: عنوان برای حالت خالی

#### `empty_state_message`
- **Type**: `str`
- **Default**: `None`
- **توضیح**: پیام برای حالت خالی

---

## Blocks قابل Override

### `breadcrumb_extra`
- **موقعیت**: بعد از breadcrumb اصلی
- **استفاده**: اضافه کردن breadcrumb اضافی

### `page_actions`
- **موقعیت**: در header، کنار title
- **استفاده**: سفارشی‌سازی کامل دکمه‌های عملیات

### `extra_actions`
- **موقعیت**: داخل `page_actions` block
- **استفاده**: اضافه کردن دکمه‌های اضافی

### `filter_fields`
- **موقعیت**: داخل پنل فیلتر
- **استفاده**: اضافه کردن فیلدهای فیلتر سفارشی

### `before_table`
- **موقعیت**: قبل از جدول
- **استفاده**: اضافه کردن محتوای اضافی

### `table_headers`
- **موقعیت**: در `<thead>` جدول
- **استفاده**: سفارشی‌سازی کامل هدرهای جدول

### `table_rows`
- **موقعیت**: در `<tbody>` جدول
- **استفاده**: سفارشی‌سازی کامل ردیف‌های جدول

### `after_table`
- **موقعیت**: بعد از جدول
- **استفاده**: اضافه کردن محتوای اضافی

### `report_scripts`
- **موقعیت**: در انتهای template
- **استفاده**: اضافه کردن JavaScript (مثل export function سفارشی)

---

## انواع نمایش در table_data

### `code`
- **استفاده**: برای نمایش کدها با استایل `<code>`
- **مثال**: `{'type': 'code', 'value': '1400001'}`

### `badge`
- **استفاده**: برای نمایش badge
- **پارامترها**: `value` (boolean), `label`, `badge_type`, `true_label`, `false_label`

### `link`
- **استفاده**: برای نمایش لینک
- **پارامترها**: `value`, `url`

### `number`
- **استفاده**: برای نمایش اعداد با format
- **پارامترها**: `value`, `decimals`

### `color_number`
- **استفاده**: برای نمایش اعداد با رنگ (مثلاً سبز برای مثبت، قرمز برای منفی)
- **پارامترها**: `value`, `color`, `decimals`

### `text`
- **استفاده**: برای نمایش متن عادی
- **پارامترها**: `value`

---

## مثال استفاده در View

```python
from django.shortcuts import render
from django.urls import reverse
from inventory.models import Item, Warehouse
from inventory.inventory_balance import calculate_warehouse_balances

def inventory_balance(request):
    # دریافت فیلترها
    warehouse_id = request.GET.get('warehouse_id')
    item_type_id = request.GET.get('item_type_id')
    as_of_date = request.GET.get('as_of_date') or timezone.now().date()
    
    # محاسبه موجودی
    balances = []
    stats = {'total_items': 0, 'total_balance': 0}
    
    if warehouse_id:
        balances_data = calculate_warehouse_balances(int(warehouse_id), as_of_date)
        stats['total_items'] = len(balances_data)
        stats['total_balance'] = sum(b['current_balance'] for b in balances_data)
        
        # آماده‌سازی table data
        table_data = []
        for balance in balances_data:
            table_data.append([
                {'type': 'code', 'value': balance['item_code']},
                {'type': 'text', 'value': balance['item_name']},
                {'type': 'text', 'value': balance['baseline_date'] or '-'},
                {'type': 'number', 'value': balance['baseline_quantity'], 'decimals': 2},
                {'type': 'color_number', 'value': balance['receipts_total'], 'color': '#10b981', 'decimals': 2},
                {'type': 'color_number', 'value': balance['issues_total'], 'color': '#ef4444', 'decimals': 2},
                {
                    'type': 'color_number',
                    'value': balance['current_balance'],
                    'color': '#10b981' if balance['current_balance'] > 0 else '#ef4444' if balance['current_balance'] < 0 else '#6b7280',
                    'decimals': 2,
                },
                {
                    'type': 'link',
                    'value': 'Details',
                    'url': reverse('inventory:balance_details', args=[balance['item_id'], balance['warehouse_id']]) + f'?as_of_date={as_of_date}',
                },
            ])
    
    context = {
        'report_title': 'Inventory Balance',
        'breadcrumbs': [
            {'label': 'انبار', 'url': reverse('inventory:items')},
            {'label': 'موجودی انبار'},
        ],
        'show_filters': True,
        'filter_fields': [
            {
                'id': 'warehouse_id',
                'name': 'warehouse_id',
                'label': 'Select Warehouse',
                'type': 'select',
                'required': True,
                'options': [
                    {'value': str(w.id), 'label': f'{w.public_code} - {w.name}', 
                     'selected': str(w.id) == warehouse_id}
                    for w in Warehouse.objects.filter(company_id=request.session.get('active_company_id'))
                ],
            },
            {
                'id': 'item_type_id',
                'name': 'item_type_id',
                'label': 'Select Item Type',
                'type': 'select',
                'required': False,
                'options': [
                    {'value': str(t.id), 'label': f'{t.public_code} - {t.name}', 
                     'selected': str(t.id) == item_type_id}
                    for t in ItemType.objects.all()
                ],
            },
        ],
        'stats_summary': [
            {'label': 'Total Items', 'value': stats['total_items'], 'color': 'blue'},
            {'label': 'Total Balance', 'value': f'{stats["total_balance"]:.2f}', 'color': 'green'},
            {'label': 'Last Calculated', 'value': as_of_date.strftime('%Y-%m-%d'), 'color': 'orange'},
        ],
        'table_id': 'balanceTable',
        'table_headers': ['Item Code', 'Item Name', 'Baseline Date', 'Baseline Quantity', 
                         'Receipts Total', 'Issues Total', 'Current Balance', 'Actions'],
        'table_data': table_data if warehouse_id else None,
        'empty_state_message': 'لطفاً انبار را انتخاب کنید' if not warehouse_id else 'داده‌ای یافت نشد',
        'export_enabled': True,
        'export_filename': f'inventory_balance_{as_of_date}',
    }
    return render(request, 'shared/generic/generic_report.html', context)
```

---

## وابستگی‌ها

### Template Tags
- `{% load i18n %}`: برای ترجمه

### Base Template
- `base.html`: template اصلی که این template از آن extend می‌کند

### JavaScript Export
Template شامل یک تابع JavaScript پیش‌فرض `exportToExcel()` است که جدول را به CSV تبدیل می‌کند. می‌توانید با override کردن block `report_scripts` تابع سفارشی خود را اضافه کنید.

---

## نکات مهم

1. **Filter Form**: فرم فیلتر به صورت GET ارسال می‌شود و باید در view پردازش شود.

2. **Export Function**: تابع پیش‌فرض `exportToExcel()` جدول را به CSV تبدیل می‌کند. برای Excel واقعی، باید تابع سفارشی بنویسید.

3. **Table ID**: برای استفاده از export function، باید `table_id` را تعریف کنید.

4. **Color Numbers**: برای نمایش اعداد با رنگ (مثلاً سبز برای مثبت، قرمز برای منفی)، از `type='color_number'` استفاده کنید.

5. **Stats Summary**: کارت‌های آمار به صورت grid responsive نمایش داده می‌شوند.

---

## استفاده در پروژه

این template برای صفحات زیر قابل استفاده است:
- Inventory Balance (`inventory/inventory_balance.html`)
- Performance Records (`production/performance_records.html`)
- و سایر صفحات Report/Analysis

با استفاده از این template، کد تکراری کاهش می‌یابد و نگهداری آسان‌تر می‌شود.

