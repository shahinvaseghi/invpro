# سیستم منوی مرکزی (Centralized Menu System)

این سیستم یک منبع واحد برای تعریف منوهای بالای صفحه و کناری فراهم می‌کند تا از تکرار کد جلوگیری شود و نگهداری راحت‌تر باشد.

## ساختار فایل‌ها

### 1. `ui/menu_config.py`
این فایل شامل تعریف کامل ساختار منوها می‌باشد. تمام موارد منو در این فایل تعریف شده‌اند.

**کلاس‌ها:**
- `MenuItem`: نمایانگر یک مورد منو
- `MenuSection`: نمایانگر یک بخش منو (ماژول)
- `get_menu_structure()`: تابعی که ساختار کامل منوها را برمی‌گرداند

### 2. `ui/context_processors.py`
این فایل شامل context processor `menu_structure` می‌باشد که منوهای فیلتر شده بر اساس دسترسی کاربر را به context اضافه می‌کند.

**تابع:**
- `menu_structure(request)`: منوهای فیلتر شده را به context اضافه می‌کند

### 3. Template Files
- `templates/ui/components/modules_menu.html`: منوی بالای صفحه (Mega Menu)
- `templates/ui/components/sidebar.html`: منوی کناری
- `templates/ui/components/menu_section_mega.html`: Template برای رندر کردن یک بخش در منوی بالای صفحه
- `templates/ui/components/menu_section_sidebar.html`: Template برای رندر کردن یک بخش در منوی کناری
- `templates/ui/components/menu_item_mega.html`: Template برای رندر کردن یک مورد در منوی بالای صفحه
- `templates/ui/components/menu_item_sidebar.html`: Template برای رندر کردن یک مورد در منوی کناری

## نحوه استفاده

### افزودن یک مورد منو جدید

برای افزودن یک مورد منو جدید، باید در فایل `ui/menu_config.py` در تابع `get_menu_structure()` تغییرات لازم را اعمال کنید:

```python
MenuItem(
    name="نام مورد منو",
    url_name="app_name:url_name",
    icon="icon-class",
    permission="feature.permission.name",  # اختیاری
    requires_superuser=False,  # اختیاری
    requires_staff=False,  # اختیاری
    target="_self",  # اختیاری
    children=[...]  # اختیاری - برای زیرمنوها
)
```

### افزودن یک بخش منو جدید

```python
MenuSection(
    name="نام بخش",
    icon="icon-class",
    items=[...],  # لیست MenuItem ها
    permission="feature.permission.name",  # اختیاری
    requires_superuser=False,  # اختیاری
    requires_staff=False  # اختیاری
)
```

## فیلتر کردن بر اساس دسترسی

سیستم به صورت خودکار موارد منو را بر اساس:
- دسترسی‌های کاربر (`user_feature_permissions`)
- وضعیت superuser
- وضعیت staff

فیلتر می‌کند و فقط مواردی که کاربر دسترسی دارد را نمایش می‌دهد.

## مزایا

1. **یک منبع واحد**: تمام منوها از یک فایل (`menu_config.py`) خوانده می‌شوند
2. **نگهداری آسان**: برای تغییر منوها فقط یک فایل نیاز به ویرایش دارد
3. **یکسان بودن**: منوی بالای صفحه و کناری همیشه یکسان هستند
4. **فیلتر خودکار**: دسترسی‌ها به صورت خودکار بررسی می‌شوند
5. **قابلیت توسعه**: افزودن موارد جدید بسیار ساده است

## تنظیمات

Context processor `menu_structure` باید در `config/settings.py` در `TEMPLATES['OPTIONS']['context_processors']` ثبت شده باشد:

```python
'context_processors': [
    # ...
    'ui.context_processors.menu_structure',
],
```

## نکات مهم

1. تمام نام‌های منو باید قابل ترجمه باشند (از `{% trans %}` استفاده می‌شود)
2. URL names باید معتبر باشند و در `urls.py` تعریف شده باشند
3. Icon classes باید در CSS تعریف شده باشند
4. Permission strings باید با سیستم دسترسی‌های موجود هماهنگ باشند

