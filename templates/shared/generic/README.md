# Generic Templates Documentation

این template‌های قابل استفاده مجدد برای کاهش تکرار کد در صفحات مختلف برنامه طراحی شده‌اند.

## فهرست Template‌ها

1. **generic_list.html** - برای صفحات لیست (List/Index Pages)
2. **generic_form.html** - برای صفحات فرم (Form Pages)
3. **generic_confirm_delete.html** - برای صفحات تأیید حذف (Delete Confirmation)
4. **generic_detail.html** - برای صفحات جزئیات (Detail/View Pages)
5. **generic_dashboard.html** - برای صفحات Dashboard
6. **generic_assignment.html** - برای صفحات Assignment/Workflow (Serial Assignment, Selection, Management)
7. **generic_report.html** - برای صفحات Report/Analysis (Inventory Balance, Reports)

---

## 1. generic_list.html

### استفاده:
```django
{% extends "shared/generic/generic_list.html" %}
{% load i18n %}

{% block page_title %}کالاها{% endblock %}
```

### Context Variables مورد نیاز:

#### الزامی:
- `object_list` - لیست اشیاء برای نمایش
- `table_headers` - لیست هدرهای جدول به صورت:
  ```python
  table_headers = [
      {'label': 'کد', 'field': 'item_code', 'type': 'code'},
      {'label': 'نام', 'field': 'name'},
      {'label': 'وضعیت', 'field': 'is_enabled', 'type': 'badge', 'true_label': 'فعال', 'false_label': 'غیرفعال'},
  ]
  ```

#### اختیاری:
- `page_title` - عنوان صفحه (default: "List")
- `breadcrumbs` - لیست breadcrumb به صورت:
  ```python
  breadcrumbs = [
      {'label': 'انبار', 'url': reverse('inventory:items')},
      {'label': 'کالاها'},
  ]
  ```
- `create_url` - URL برای دکمه ایجاد جدید
- `create_button_text` - متن دکمه ایجاد (default: "Create New")
- `show_filters` - نمایش پنل فیلتر (default: True)
- `status_filter` - نمایش فیلتر وضعیت (default: True)
- `search_placeholder` - placeholder برای جستجو
- `show_actions` - نمایش ستون عملیات (default: True)
- `edit_url_name` - نام URL برای ویرایش
- `delete_url_name` - نام URL برای حذف
- `clear_filter_url` - URL برای پاک کردن فیلتر
- `print_enabled` - فعال بودن دکمه چاپ (default: True)
- `empty_state_icon` - آیکون برای حالت خالی
- `empty_state_title` - عنوان برای حالت خالی
- `empty_state_message` - پیام برای حالت خالی

### Blocks قابل Override:
- `breadcrumb_extra` - اضافه کردن breadcrumb اضافی
- `page_actions` - دکمه‌های عملیات صفحه
- `extra_actions` - دکمه‌های اضافی
- `filter_fields` - فیلدهای فیلتر سفارشی
- `table_headers` - هدرهای جدول
- `table_rows` - ردیف‌های جدول (برای سفارشی‌سازی کامل)
- `action_buttons` - دکمه‌های عملیات در هر ردیف
- `before_table` - محتوا قبل از جدول
- `after_table` - محتوا بعد از جدول

### مثال استفاده در View:

```python
from django.shortcuts import render
from django.core.paginator import Paginator

def items_list(request):
    items = Item.objects.all()
    
    # Pagination
    paginator = Paginator(items, 25)
    page_obj = paginator.get_page(request.GET.get('page'))
    
    # Filter
    search = request.GET.get('search', '')
    if search:
        items = items.filter(name__icontains=search)
    
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
            {'label': 'وضعیت', 'field': 'is_enabled', 'type': 'badge', 'true_label': 'فعال', 'false_label': 'غیرفعال'},
        ],
        'create_url': reverse('inventory:item_create'),
        'create_button_text': 'تعریف کالای جدید',
        'edit_url_name': 'inventory:item_edit',
        'delete_url_name': 'inventory:item_delete',
        'show_filters': True,
        'status_filter': True,
    }
    return render(request, 'shared/generic/generic_list.html', context)
```

---

## 2. generic_form.html

### استفاده:
```django
{% extends "shared/generic/generic_form.html" %}
{% load i18n %}
```

### Context Variables مورد نیاز:

#### الزامی:
- `form` - Django Form instance

#### اختیاری:
- `form_title` - عنوان فرم (default: "Form")
- `breadcrumbs` - لیست breadcrumb
- `cancel_url` - URL برای دکمه لغو
- `form_id` - ID برای فرم (برای JavaScript)
- `enctype` - enctype برای فرم (برای file upload)
- `fieldsets` - گروه‌بندی فیلدها به صورت:
  ```python
  fieldsets = [
      ('اطلاعات اولیه', [form['name'], form['code']]),
      ('اطلاعات تکمیلی', [form['description'], form['notes']]),
  ]
  ```

### Blocks قابل Override:
- `breadcrumb_extra` - breadcrumb اضافی
- `info_banner_extra` - اطلاعات اضافی در banner
- `form_sections` - بخش‌های فرم
- `form_extra` - محتوای اضافی در فرم
- `form_actions_extra` - دکمه‌های اضافی
- `form_scripts` - اسکریپت‌های JavaScript

### مثال استفاده:

```python
def item_create(request):
    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('inventory:items')
    else:
        form = ItemForm()
    
    context = {
        'form': form,
        'form_title': 'تعریف کالای جدید',
        'breadcrumbs': [
            {'label': 'انبار', 'url': reverse('inventory:items')},
            {'label': 'کالاها', 'url': reverse('inventory:items')},
            {'label': 'ایجاد'},
        ],
        'cancel_url': reverse('inventory:items'),
    }
    return render(request, 'shared/generic/generic_form.html', context)
```

---

## 3. generic_confirm_delete.html

### استفاده:
```django
{% extends "shared/generic/generic_confirm_delete.html" %}
{% load i18n %}
```

### Context Variables مورد نیاز:

#### الزامی:
- `object` - شیء برای حذف

#### اختیاری:
- `delete_title` - عنوان صفحه (default: "Delete")
- `confirmation_message` - پیام تأیید (default: "Do you really want to delete this item?")
- `warning_message` - پیام هشدار (default: "This action cannot be undone.")
- `breadcrumbs` - لیست breadcrumb
- `cancel_url` - URL برای دکمه لغو
- `object_details` - جزئیات شیء به صورت:
  ```python
  object_details = [
      {'label': 'کد', 'value': object.public_code, 'type': 'code'},
      {'label': 'نام', 'value': object.name},
      {'label': 'وضعیت', 'value': object.is_enabled, 'type': 'badge', 'true_label': 'فعال', 'false_label': 'غیرفعال'},
  ]
  ```

### Blocks قابل Override:
- `breadcrumb_extra` - breadcrumb اضافی
- `delete_details_extra` - جزئیات اضافی
- `delete_form_extra` - فیلدهای اضافی در فرم

### مثال استفاده:

```python
def item_delete(request, pk):
    item = get_object_or_404(Item, pk=pk)
    
    if request.method == 'POST':
        item.delete()
        return redirect('inventory:items')
    
    context = {
        'object': item,
        'delete_title': 'حذف کالا',
        'breadcrumbs': [
            {'label': 'انبار', 'url': reverse('inventory:items')},
            {'label': 'کالاها', 'url': reverse('inventory:items')},
            {'label': 'حذف'},
        ],
        'object_details': [
            {'label': 'کد کالا', 'value': item.item_code, 'type': 'code'},
            {'label': 'نام کالا', 'value': item.name},
        ],
        'cancel_url': reverse('inventory:items'),
    }
    return render(request, 'shared/generic/generic_confirm_delete.html', context)
```

---

## 4. generic_detail.html

### استفاده:
```django
{% extends "shared/generic/generic_detail.html" %}
{% load i18n %}
```

### Context Variables مورد نیاز:

#### اختیاری:
- `detail_title` - عنوان صفحه (default: "Details")
- `breadcrumbs` - لیست breadcrumb
- `info_banner` - اطلاعات در banner به صورت:
  ```python
  info_banner = [
      {'label': 'کد', 'value': object.code, 'type': 'code'},
      {'label': 'تاریخ', 'value': object.date, 'type': 'date'},
      {'label': 'وضعیت', 'value': object.is_active, 'type': 'badge'},
  ]
  ```
- `detail_sections` - بخش‌های جزئیات به صورت:
  ```python
  detail_sections = [
      {
          'title': 'اطلاعات اولیه',
          'type': 'fields',
          'fields': [
              {'label': 'نام', 'value': object.name},
              {'label': 'کد', 'value': object.code, 'type': 'code'},
          ]
      },
      {
          'title': 'ردیف‌ها',
          'type': 'table',
          'headers': ['ردیف', 'کالا', 'تعداد'],
          'data': [
              ['1', 'کالای 1', '10'],
              ['2', 'کالای 2', '20'],
          ]
      }
  ]
  ```
- `list_url` - URL برای بازگشت به لیست
- `edit_url` - URL برای ویرایش
- `delete_url` - URL برای حذف
- `can_edit` - امکان ویرایش (default: True)
- `can_delete` - امکان حذف (default: True)
- `alert_message` - پیام alert
- `alert_type` - نوع alert (info, warning, danger)

### Blocks قابل Override:
- `breadcrumb_extra` - breadcrumb اضافی
- `info_banner_extra` - اطلاعات اضافی در banner
- `detail_sections` - بخش‌های جزئیات
- `detail_actions_extra` - دکمه‌های اضافی

---

## 5. generic_dashboard.html

### استفاده:
```django
{% extends "shared/generic/generic_dashboard.html" %}
{% load i18n %}
```

### Context Variables مورد نیاز:

#### اختیاری:
- `dashboard_title` - عنوان dashboard (default: "Dashboard")
- `dashboard_subtitle` - زیرعنوان
- `dashboard_cards` - کارت‌های dashboard به صورت:
  ```python
  dashboard_cards = [
      {
          'type': 'stat',
          'value': 150,
          'label': 'Total Items',
          'icon': '📦',
          'color': 'blue',
          'link_url': reverse('inventory:items'),
          'link_text': 'More info',
      },
      {
          'type': 'info',
          'title': 'User Name',
          'subtitle': 'Company Name',
          'icon': '👤',
          'color': 'info',
          'show_datetime': True,
      },
      {
          'type': 'stat',
          'value': 25,
          'label': 'Pending Requests',
          'icon': '📋',
          'color': 'orange',
          'link_items': [
              {'label': 'Purchase Requests', 'url': reverse('inventory:purchase_requests'), 'count': 10},
              {'label': 'Warehouse Requests', 'url': reverse('inventory:warehouse_requests'), 'count': 15},
          ],
      },
  ]
  ```
- `show_datetime` - نمایش تاریخ و زمان (default: False)

### Blocks قابل Override:
- `dashboard_cards` - کارت‌های dashboard

---

## 6. generic_assignment.html

برای صفحات Assignment/Workflow که نیاز به ویرایش inline در جدول دارند (مثل Serial Assignment، Line Selection، Rejection Management).

مستندات کامل: [README_GENERIC_ASSIGNMENT.md](README_GENERIC_ASSIGNMENT.md)

---

## 7. generic_report.html

برای صفحات Report/Analysis با فیلتر، آمار خلاصه و جدول داده (مثل Inventory Balance، Performance Records).

مستندات کامل: [README_GENERIC_REPORT.md](README_GENERIC_REPORT.md)

---

## Template Tags

Template tags helper در `shared/templatetags/generic_tags.py` تعریف شده‌اند:

- `getattr`: دریافت attribute از object با پشتیبانی از nested attributes
- `get_field_value`: Alias برای `getattr`

برای استفاده:
```django
{% load generic_tags %}
{{ object|getattr:"type.name" }}
```

مستندات کامل: [README_GENERIC_TAGS.md](README_GENERIC_TAGS.md)

---

## نکات مهم

1. همه template‌ها از `base.html` extend می‌کنند
2. برای استفاده از nested attributes در `table_headers`، از template tag `getattr` استفاده کنید
3. می‌توانید blocks را override کنید برای سفارشی‌سازی بیشتر
4. همه template‌ها از i18n پشتیبانی می‌کنند
5. استایل‌ها inline هستند اما می‌توانید آنها را به فایل CSS جداگانه منتقل کنید

