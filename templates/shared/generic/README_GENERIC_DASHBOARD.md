# templates/shared/generic/generic_dashboard.html - Generic Dashboard Template

**هدف**: این template یک صفحه Dashboard قابل استفاده مجدد برای نمایش آمار، کارت‌های اطلاعاتی و لینک‌های سریع است.

این template برای کاهش تکرار کد در صفحات Dashboard مختلف برنامه طراحی شده و می‌تواند برای هر ماژول استفاده شود.

---

## ساختار Template

این template از `base.html` extend می‌کند و شامل بخش‌های زیر است:

1. **Header Section**: Dashboard title + Subtitle
2. **Dashboard Grid**: Grid layout برای کارت‌ها
3. **Cards**: کارت‌های آمار و اطلاعات
4. **JavaScript**: مدیریت dropdown menus و نمایش تاریخ/زمان

---

## Context Variables

### اختیاری

#### `dashboard_title`
- **Type**: `str`
- **Default**: `"Dashboard"`
- **توضیح**: عنوان Dashboard
- **مثال**: `"Dashboard"` یا `"داشبورد انبار"`

#### `dashboard_subtitle`
- **Type**: `str`
- **Default**: `None`
- **توضیح**: زیرعنوان Dashboard
- **مثال**: `"Overview of your inventory management system"`

#### `dashboard_cards`
- **Type**: `list[dict]`
- **Default**: `None`
- **توضیح**: لیست کارت‌های Dashboard
- **ساختار هر card**:
  ```python
  {
      'type': 'stat|info',           # الزامی - نوع کارت
      'value': 150,                  # برای type='stat' - مقدار عددی
      'label': 'Total Items',        # برای type='stat' - برچسب
      'title': 'User Name',          # برای type='info' - عنوان
      'subtitle': 'Company Name',    # برای type='info' - زیرعنوان
      'icon': '📦',                  # اختیاری - آیکون
      'color': 'blue|green|orange|red|purple|info',  # اختیاری - رنگ کارت
      'link_url': 'url_path',        # اختیاری - URL برای لینک
      'link_text': 'More info',      # اختیاری - متن لینک
      'link_items': [                # اختیاری - لیست آیتم‌های dropdown
          {
              'label': 'Item 1',
              'url': 'url_path',
              'count': 10,            # اختیاری - تعداد
          },
      ],
      'show_datetime': True,         # برای type='info' - نمایش تاریخ/زمان
  }
  ```
- **مثال**:
  ```python
  dashboard_cards = [
      {
          'type': 'info',
          'title': user.get_full_name(),
          'subtitle': active_company.display_name,
          'icon': '👤',
          'color': 'info',
          'show_datetime': True,
      },
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

#### `show_datetime`
- **Type**: `bool`
- **Default**: `False`
- **توضیح**: نمایش تاریخ و زمان در JavaScript (برای کارت‌های info)

---

## Blocks قابل Override

### `dashboard_cards`
- **موقعیت**: در dashboard grid
- **استفاده**: سفارشی‌سازی کامل کارت‌ها
- **نکته**: اگر override شود، `dashboard_cards` context variable استفاده نمی‌شود

---

## مثال استفاده در View

```python
from django.shortcuts import render
from django.urls import reverse
from inventory.models import Item, Warehouse
from inventory.utils.permissions import get_user_feature_permissions

def dashboard(request):
    user_permissions = get_user_feature_permissions(request.user, request.session.get('active_company_id'))
    
    dashboard_cards = [
        {
            'type': 'info',
            'title': request.user.get_full_name() or request.user.username,
            'subtitle': request.session.get('active_company_name', ''),
            'icon': '👤',
            'color': 'info',
            'show_datetime': True,
        },
    ]
    
    if user_permissions.get('inventory.master.items'):
        total_items = Item.objects.filter(company_id=request.session.get('active_company_id')).count()
        dashboard_cards.append({
            'type': 'stat',
            'value': total_items,
            'label': 'Total Items',
            'icon': '📦',
            'color': 'blue',
            'link_url': reverse('inventory:items'),
            'link_text': 'More info',
        })
    
    if user_permissions.get('inventory.master.warehouses'):
        total_warehouses = Warehouse.objects.filter(company_id=request.session.get('active_company_id')).count()
        dashboard_cards.append({
            'type': 'stat',
            'value': total_warehouses,
            'label': 'Total Warehouses',
            'icon': '🏢',
            'color': 'green',
            'link_url': reverse('inventory:warehouses'),
        })
    
    context = {
        'dashboard_title': 'Dashboard',
        'dashboard_subtitle': 'Overview of your inventory management system',
        'dashboard_cards': dashboard_cards,
        'show_datetime': True,
    }
    return render(request, 'shared/generic/generic_dashboard.html', context)
```

---

## وابستگی‌ها

### Template Tags
- `{% load i18n %}`: برای ترجمه

### Base Template
- `base.html`: template اصلی که این template از آن extend می‌کند

### CSS Variables
Template از CSS variables زیر استفاده می‌کند (که باید در `base.css` تعریف شده باشند):
- `--color-primary`
- `--color-secondary`
- `--color-text`
- `--color-light`

---

## نکات مهم

1. **Card Types**: دو نوع کارت وجود دارد:
   - `stat`: برای نمایش آمار (عدد + برچسب)
   - `info`: برای نمایش اطلاعات (عنوان + زیرعنوان + تاریخ/زمان)

2. **Link Items**: برای کارت‌های stat، می‌توانید `link_items` تعریف کنید تا dropdown menu نمایش داده شود.

3. **DateTime Display**: برای نمایش تاریخ/زمان، باید `show_datetime=True` در context قرار دهید و در کارت info از `show_datetime=True` استفاده کنید.

4. **Card Colors**: رنگ‌های موجود: `blue`, `green`, `orange`, `red`, `purple`, `info`

5. **Responsive Grid**: Grid به صورت responsive است و کارت‌ها به صورت خودکار در ردیف‌های مختلف قرار می‌گیرند.

---

## استفاده در پروژه

این template برای تمام صفحات Dashboard در برنامه قابل استفاده است:
- Dashboard اصلی (`ui/dashboard.html`)
- Dashboard انبار (`inventory/dashboard.html`)
- Dashboard تولید (`production/dashboard.html`)
- و سایر Dashboard‌ها

با استفاده از این template، کد تکراری کاهش می‌یابد و نگهداری آسان‌تر می‌شود.

