# Ticketing Module Implementation

این مستند تغییرات و پیاده‌سازی‌های انجام شده در ماژول Ticketing را مستند می‌کند.

## خلاصه پیاده‌سازی

### جداول Events

#### `ticketing_template_event`
- رویدادهای مربوط به Template (مثلاً `on_open`, `on_close`, `on_respond`)
- هر رویداد می‌تواند یک `action_reference` داشته باشد (Entity Reference System)
- رویدادها می‌توانند شرایطی داشته باشند (`condition_rules`)

#### `ticketing_template_field_event`
- رویدادهای مربوط به فیلدهای Template (مثلاً `on_change`, `on_set`, `on_clear`)
- هر رویداد می‌تواند یک `action_reference` داشته باشد
- رویدادها می‌توانند بر اساس مقدار فیلد شرطی باشند

### Forms

#### `ticketing/forms/templates.py`
- `TicketTemplateForm`: فرم اصلی Template
- `TicketTemplateFieldForm`: فرم فیلدها با فیلدهای `field_config` و `validation_rules`
- `TicketTemplatePermissionForm`: فرم دسترسی‌ها
- `TicketTemplateEventForm`: فرم رویدادهای Template
- Formsets: `TicketTemplateFieldFormSet`, `TicketTemplatePermissionFormSet`, `TicketTemplateEventFormSet`

### Views

#### `ticketing/views/templates.py`
- `TicketTemplateListView`: لیست تمپلیت‌ها
- `TicketTemplateCreateView`: ایجاد تمپلیت جدید
- `TicketTemplateUpdateView`: ویرایش تمپلیت
- `TicketTemplateDeleteView`: حذف تمپلیت

### Templates

#### `templates/ticketing/templates_list.html`
- لیست تمپلیت‌ها با فیلتر و جستجو

#### `templates/ticketing/template_form.html`
- فرم ایجاد/ویرایش تمپلیت با:
  - بخش Fields: جدول فیلدها با امکان اضافه/حذف دینامیک
  - بخش Permissions: جدول دسترسی‌ها
  - بخش Events: جدول رویدادهای Template
- JavaScript برای مدیریت دینامیک ردیف‌ها (Add/Remove)
- پنل تنظیمات فیلدها (Settings Panel) که با دکمه Settings باز/بسته می‌شود
- دکمه "Remove" برای حذف ردیف‌های جدید (قبل از ذخیره)

### JavaScript Features

1. **Dynamic Formset Management**:
   - اضافه کردن ردیف جدید با استفاده از `<template>` tag
   - حذف ردیف‌های جدید (Remove button)
   - حذف ردیف‌های موجود (DELETE checkbox)
   - به‌روزرسانی `TOTAL_FORMS` به‌صورت خودکار

2. **Field Settings Panel**:
   - پنل تنظیمات برای هر فیلد
   - باز/بسته شدن با دکمه Settings
   - نمایش/مخفی کردن با JavaScript

### تغییرات PurchaseRequest و WarehouseRequest

#### PurchaseRequest
- `notes` field: فیلد متنی برای یادداشت‌ها
- `attachments`: فیلد JSON برای فایل‌های پیوست
- `request_metadata`: فیلد JSON برای اطلاعات اضافی

#### WarehouseRequest
- `notes` field: فیلد متنی برای یادداشت‌ها
- `attachments`: فیلد JSON برای فایل‌های پیوست (default=list)
- `request_metadata`: فیلد JSON برای اطلاعات اضافی (default=dict)
- `is_locked`: فیلد برای قفل کردن درخواست

## Field-Specific Settings UI - پیاده‌سازی شده

### ✅ پیاده‌سازی کامل

سیستم تنظیمات پویا بر اساس نوع فیلد پیاده‌سازی شده است. برای جزئیات کامل، به `docs/ticketing_field_settings_specification.md` مراجعه کنید.

### ویژگی‌های پیاده‌سازی شده:

1. **نمایش پویای تنظیمات**: بر اساس `field_type` انتخاب شده، تنظیمات مناسب نمایش داده می‌شود
2. **پشتیبانی از تمام 25 نوع فیلد**: هر نوع فیلد تنظیمات خاص خود را دارد
3. **ذخیره خودکار**: تنظیمات به‌صورت خودکار در فیلد `field_config` (JSON) ذخیره می‌شوند
4. **تغییر پویا**: با تغییر `field_type`، تنظیمات به‌صورت خودکار به‌روزرسانی می‌شود

### انواع فیلدها و تنظیمات:

#### فیلدهای بدون تنظیمات خاص:
- `short_text`, `long_text`, `rich_text`, `email`, `url`, `phone`, `file_upload`, `color`, `currency`, `signature`, `location`, `section`, `tags`

#### فیلدهای Options (radio, dropdown, checkbox, multi_select):
- انتخاب منبع: Manual یا Entity Reference
- در صورت Manual: مدیریت Options (بعد از ذخیره Template)
- در صورت Entity Reference: تنظیمات `entity_reference`, `value_field`, `label_field`

#### فیلدهای تاریخ/زمان (date, time, datetime):
- گزینه Auto-fill با تاریخ/زمان فعلی

#### فیلدهای عددی:
- `number`: Thousands separator (3 رقم 3 رقم)
- `rating`: Minimum/Maximum rating
- `slider`: Minimum/Maximum/Step value

#### فیلد محاسباتی (calculation):
- تعریف Formula با استفاده از `{field_key}` برای ارجاع به فیلدهای دیگر

### فایل‌های مرتبط:

- `templates/ticketing/template_form.html`: JavaScript پیاده‌سازی
- `docs/ticketing_field_settings_specification.md`: مشخصات کامل

## Field Options Management UI - پیاده‌سازی شده

### ✅ پیاده‌سازی کامل

سیستم مدیریت Options برای فیلدهای `radio`, `dropdown`, `checkbox`, و `multi_select` پیاده‌سازی شده است.

### ویژگی‌های پیاده‌سازی شده:

1. **جدول مدیریت Options**: جدول تعاملی برای نمایش و مدیریت Options با ستون‌های:
   - Order: ترتیب نمایش Option
   - Value: مقدار Option (ذخیره می‌شود)
   - Label: برچسب Option (نمایش داده می‌شود)
   - Default: چک‌باکس برای انتخاب Option پیش‌فرض
   - Actions: دکمه حذف

2. **افزودن Option**: دکمه "Add Option" برای افزودن Option جدید به جدول

3. **حذف Option**: دکمه "Remove" برای حذف Option از جدول

4. **ذخیره خودکار**: Options به‌صورت خودکار در فیلد `field_config` به صورت JSON ذخیره می‌شوند:
   ```json
   {
     "options_source": "manual",
     "options": [
       {"value": "opt1", "label": "Option 1", "order": 0, "is_default": false},
       {"value": "opt2", "label": "Option 2", "order": 1, "is_default": true}
     ]
   }
   ```

5. **بارگذاری Options**: Options موجود از `field_config` خوانده می‌شوند و در جدول نمایش داده می‌شوند
   - استفاده از `json_filters` template tag library برای تبدیل dict به JSON string
   - تبدیل `field_config` dict از دیتابیس به JSON string در template
   - Parse کردن JSON string در JavaScript و نمایش Options در جدول
   - بارگذاری خودکار Options هنگام باز شدن Settings panel

6. **اعتبارسنجی Default**: فقط یک Option می‌تواند به عنوان Default انتخاب شود

7. **به‌روزرسانی Order**: شماره‌های ترتیب به‌صورت خودکار پس از افزودن/حذف Option به‌روزرسانی می‌شوند

8. **یکپارچه‌سازی با Options Source**: Manual Options Panel فقط زمانی نمایش داده می‌شود که "Manual" به عنوان منبع انتخاب شده باشد

### JavaScript Functions:

- `addOptionRow()`: افزودن ردیف جدید به جدول Options
- `updateOptionOrders()`: به‌روزرسانی شماره‌های ترتیب Options
- `updateFieldSettings()`: به‌روزرسانی Settings panel و بارگذاری Options از `field_config`
- `saveFieldSettingsToConfig()`: ذخیره Options در `field_config` JSON
- `initializeFieldSettings()`: بارگذاری اولیه Options هنگام لود صفحه
- ذخیره خودکار Options در `saveFieldSettingsToConfig()` هنگام تغییر
- مدیریت رویدادها برای auto-save

### تکنیک‌های پیاده‌سازی:

1. **JSON Serialization در Django Form**:
   - تبدیل `field_config` dict به JSON string در `TicketTemplateFieldForm.__init__()`
   - استفاده از `json_filters.to_json` template filter برای نمایش در template
   - تبدیل dict به JSON string قبل از قرار دادن در hidden input

2. **JavaScript JSON Parsing**:
   - Parse کردن JSON string از hidden input
   - تبدیل dict (اگر به صورت Python dict representation باشد) به JSON string
   - مدیریت خطاهای parse با fallback به object خالی

3. **Auto-loading Options**:
   - بارگذاری Options در `initializeFieldSettings()` هنگام لود صفحه
   - بارگذاری مجدد Options در `updateFieldSettings()` هنگام باز شدن Settings panel
   - بررسی `options_source` و نمایش Manual Options Panel فقط برای Manual

### فایل‌های مرتبط:

- `templates/ticketing/template_form.html`: JavaScript پیاده‌سازی
- `ticketing/forms/templates.py`: Form initialization با JSON serialization
- `ticketing/views/templates.py`: Logging برای debugging
- `shared/templatetags/json_filters.py`: Template filter برای JSON conversion
- `docs/ticketing_field_settings_specification.md`: مشخصات کامل

## Migration History

- `ticketing/migrations/0001_initial.py`: جداول اولیه
- `ticketing/migrations/0002_add_template_events.py`: جداول Events

## URLs

- `/ticketing/templates/`: لیست تمپلیت‌ها
- `/ticketing/templates/create/`: ایجاد تمپلیت جدید
- `/ticketing/templates/<id>/edit/`: ویرایش تمپلیت
- `/ticketing/templates/<id>/delete/`: حذف تمپلیت

## Permissions

- `ticketing.templates`: مدیریت تمپلیت‌ها
  - `view_own`, `view_all`
  - `create`
  - `edit_own`, `edit_other`
  - `delete_own`, `delete_other`

## Notes

- ✅ Field Options Management UI: پیاده‌سازی شده - Options می‌توانند در همان صفحه Template اضافه/حذف شوند و در `field_config` ذخیره می‌شوند
- Field Events در صفحه ویرایش فیلد اضافه می‌شود (بعد از ذخیره Template)
- ✅ تنظیمات فیلد بر اساس نوع: پیاده‌سازی شده

