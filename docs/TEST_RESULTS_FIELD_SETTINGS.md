# نتایج تست Field-Specific Settings UI

تاریخ تست: 2025-01-XX

## ✅ تست‌های ساختاری (Static Analysis)

### 1. بررسی Model
- ✅ فیلد `field_config` در `TicketTemplateField` تعریف شده (JSONField, default=dict, blank=True)
- ✅ فیلد `validation_rules` در `TicketTemplateField` تعریف شده (JSONField, default=dict, blank=True)
- ✅ Model از نظر ساختار صحیح است

### 2. بررسی Form
- ✅ `TicketTemplateFieldForm` شامل `field_config` و `validation_rules` است
- ✅ Widget برای `field_config` تعریف شده (Textarea)
- ✅ Widget برای `validation_rules` تعریف شده (Textarea)

### 3. بررسی Template
- ✅ Hidden input برای `field_config` در template موجود است (`field-config-json-input`)
- ✅ Container برای تنظیمات پویا موجود است (`.field-settings-panel`)
- ✅ Container برای تنظیمات خاص فیلد موجود است (`.field-specific-settings`)
- ✅ دکمه Settings موجود است (`.toggle-field-settings`)

### 4. بررسی JavaScript
- ✅ `FIELD_SETTINGS_CONFIG` تعریف شده با تمام 25 نوع فیلد
- ✅ `generateFieldSettingsHTML()` function تعریف شده
- ✅ `updateFieldSettings()` function تعریف شده
- ✅ `saveFieldSettingsToConfig()` function تعریف شده
- ✅ `toggleOptionsSourcePanels()` function تعریف شده
- ✅ Event listeners تعریف شده‌اند:
  - Change listener برای field_type
  - Change listener برای settings changes
  - Submit listener برای ذخیره نهایی
  - Click listener برای toggle settings panel
- ✅ `initializeFieldSettings()` function برای initialize در page load

## ⚠️ تست‌های عملی (Functional Testing)

**نکته**: برای انجام تست‌های عملی، باید:
1. Django سرور اجرا شود
2. به صفحه `/ticketing/templates/create/` یا `/ticketing/templates/<id>/edit/` بروید
3. یک فیلد اضافه کنید
4. Settings را باز کنید
5. نوع فیلد را تغییر دهید
6. تنظیمات را تغییر دهید
7. فرم را ذخیره کنید

### چک‌لیست تست عملی:

#### تست 1: نمایش تنظیمات برای فیلدهای ساده
- [ ] فیلد `short_text` → باید پیام "No special settings required" نمایش دهد
- [ ] فیلد `email` → باید پیام "No special settings required" نمایش دهد
- [ ] فیلد `url` → باید پیام "No special settings required" نمایش دهد

#### تست 2: نمایش تنظیمات برای فیلدهای Options
- [ ] فیلد `dropdown` → باید dropdown برای انتخاب Manual/Entity Reference نمایش دهد
- [ ] انتخاب "Manual" → باید پیام "Options can be managed after saving" نمایش دهد
- [ ] انتخاب "Entity Reference" → باید فیلدهای entity_reference, value_field, label_field نمایش دهد
- [ ] تغییر بین Manual و Entity Reference → باید پنل‌ها به درستی toggle شوند

#### تست 3: نمایش تنظیمات برای فیلدهای تاریخ/زمان
- [ ] فیلد `date` → باید checkbox "Auto-fill with current date" نمایش دهد
- [ ] فیلد `time` → باید checkbox "Auto-fill with current time" نمایش دهد
- [ ] فیلد `datetime` → باید checkbox "Auto-fill with current date and time" نمایش دهد

#### تست 4: نمایش تنظیمات برای فیلدهای عددی
- [ ] فیلد `number` → باید checkbox "Use thousands separator" نمایش دهد
- [ ] فیلد `rating` → باید فیلدهای Minimum/Maximum Value نمایش دهد
- [ ] فیلد `slider` → باید فیلدهای Minimum/Maximum/Step Value نمایش دهد

#### تست 5: نمایش تنظیمات برای فیلد محاسباتی
- [ ] فیلد `calculation` → باید textarea برای Formula نمایش دهد

#### تست 6: تغییر نوع فیلد
- [ ] تغییر از `short_text` به `dropdown` → باید تنظیمات Options نمایش دهد
- [ ] تغییر از `date` به `number` → باید تنظیمات Number نمایش دهد
- [ ] تنظیمات قبلی باید به درستی ذخیره شوند

#### تست 7: ذخیره تنظیمات
- [ ] تنظیمات باید در `field_config` به صورت JSON ذخیره شوند
- [ ] JSON باید ساختار صحیح داشته باشد
- [ ] تنظیمات باید در ویرایش مجدد فرم بازگردانده شوند

#### تست 8: Initialize برای فیلدهای موجود
- [ ] در صفحه ویرایش، تنظیمات فیلدهای موجود باید به درستی نمایش داده شوند
- [ ] مقادیر `field_config` باید از JSON به UI تبدیل شوند

## 📝 یادداشت‌ها

- تمام کدهای JavaScript در یک `<script>` tag قرار دارند و در `DOMContentLoaded` اجرا می‌شوند
- تنظیمات به صورت خودکار در `field_config` (hidden input) ذخیره می‌شوند
- JSON structure برای هر نوع فیلد:
  - Options: `{options_source: "manual|entity_reference", entity_reference?: "...", value_field?: "...", label_field?: "..."}`
  - Auto-fill: `{auto_fill_date?: true|false, auto_fill_time?: true|false, auto_fill_datetime?: true|false}`
  - Number: `{thousands_separator: true|false}`
  - Range: `{min_rating?: number, max_rating?: number, min_value?: number, max_value?: number, step_value?: number}`
  - Formula: `{formula: "..."}`
  - None: `{}`

## ✅ نتیجه نهایی

از نظر ساختار کد، تمام موارد به درستی پیاده‌سازی شده‌اند. برای تست کامل عملکرد، نیاز به اجرای سرور Django و تست دستی است.

