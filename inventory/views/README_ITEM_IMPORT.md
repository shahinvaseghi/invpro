# inventory/views/item_import.py - Item Import Views (Complete Documentation)

**هدف**: Views برای import/export کالاها از/به فایل Excel در ماژول inventory

این فایل شامل 2 view class:
- ItemExcelTemplateDownloadView: دانلود قالب Excel برای import
- ItemExcelImportView: import کالاها از فایل Excel

---

## وابستگی‌ها

- `inventory.views.base`: `InventoryBaseView`
- `inventory.models`: `Item`, `ItemType`, `ItemCategory`, `ItemSubcategory`, `Warehouse`
- `inventory.forms.base`: `UNIT_CHOICES`
- `openpyxl`: `Workbook`, `load_workbook`, `Font`, `PatternFill`, `Alignment` (optional)
- `django.views.generic`: `View`, `TemplateView`
- `django.http`: `HttpResponse`, `HttpResponseRedirect`
- `django.urls.reverse_lazy`
- `django.utils.translation.gettext_lazy`
- `django.contrib.messages`
- `decimal.Decimal`, `InvalidOperation`
- `io`
- `typing`: `Dict`, `Any`, `List`, `Tuple`

---

## ItemExcelTemplateDownloadView

**Type**: `InventoryBaseView, View`

**Method**: `GET`

**متدها**:

#### `get(self, request, *args, **kwargs) -> HttpResponse`

**توضیح**: ایجاد و دانلود قالب Excel برای import کالاها.

**پارامترهای ورودی**:
- `request`: HTTP request
- `*args`, `**kwargs`: آرگومان‌های اضافی

**مقدار بازگشتی**:
- `HttpResponse`: Excel file با content-type `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`

**منطق**:
1. بررسی نصب بودن `openpyxl`
2. بررسی `active_company_id`
3. ایجاد workbook با 2 sheet:
   - Sheet 1: "کالاها" - قالب اصلی با headers و example row
   - Sheet 2: "راهنما" - داده‌های مرجع (types, categories, subcategories, warehouses, units)
4. تنظیم styles برای headers (fill, font, alignment)
5. تنظیم column widths
6. بازگشت Excel file به عنوان attachment

**Excel Columns (19 ستون)**:
1. نوع کالا (کد یا نام)
2. دسته‌بندی (کد یا نام)
3. زیردسته (کد یا نام)
4. کد کاربری (2 رقم)
5. نام (فارسی)
6. نام (انگلیسی)
7. بچ نامبر ثانویه
8. قابل فروش (1=بله، 0=خیر)
9. رهگیری لات (1=بله، 0=خیر)
10. رسید موقت (1=بله، 0=خیر)
11. شناسه مالیاتی
12. عنوان مالیاتی
13. حداقل موجودی
14. واحد اصلی
15. واحد گزارش
16. توضیح کوتاه
17. یادداشت‌ها
18. ترتیب نمایش
19. فعال (1=بله، 0=خیر)
20. انبارهای مجاز (کدها با کاما جدا شوند)

**Reference Sheet شامل**:
- انواع کالا (کد، نام)
- دسته‌بندی‌ها (کد، نام)
- زیردسته‌بندی‌ها (کد، نام، دسته‌بندی)
- انبارها (کد، نام)
- واحدها (کد، نام)

**URL**: `/inventory/items/import/template/`

---

## ItemExcelImportView

**Type**: `InventoryBaseView, TemplateView`

**Template**: `inventory/item_import_result.html`

**Method**: `POST`

**Attributes**:
- `template_name`: `'inventory/item_import_result.html'`

**متدها**:

#### `post(self, request, *args, **kwargs) -> HttpResponse`

**توضیح**: پردازش فایل Excel آپلود شده و import کالاها.

**Request**:
- `excel_file`: فایل Excel (.xlsx یا .xls)

**Context Variables**:
- `success_count`: تعداد کالاهای موفق
- `error_count`: تعداد خطاها
- `duplicate_count`: تعداد تکراری‌ها
- `errors`: لیست خطاها با row number و error messages
- `total_rows`: تعداد کل ردیف‌ها

**منطق**:
1. بررسی نصب بودن `openpyxl`
2. بررسی `active_company_id`
3. بررسی وجود فایل و format
4. Load workbook
5. برای هر row (از row 2):
   - Parse row data
   - Validate data
   - Create item
   - ثبت خطاها
6. نمایش نتایج

---

#### `_parse_row(self, row: Tuple, company_id: int, row_num: int) -> Dict[str, Any]`

**توضیح**: Parse کردن یک row از Excel به dictionary.

**پارامترهای ورودی**:
- `row`: tuple از مقادیر row
- `company_id`: شناسه شرکت
- `row_num`: شماره row (برای error messages)

**مقدار بازگشتی**:
- `Dict[str, Any]`: dictionary با داده‌های parsed

**منطق**:
- Map کردن columns به field names
- Parse کردن boolean values
- Parse کردن decimal values
- Strip کردن strings

---

#### `_parse_bool(self, value, default=0) -> int`

**توضیح**: Parse کردن boolean value از Excel.

**پارامترهای ورودی**:
- `value`: مقدار از Excel
- `default`: مقدار پیش‌فرض

**مقدار بازگشتی**:
- `int`: `1` یا `0`

**منطق**:
- پشتیبانی از: `1`, `0`, `yes`, `no`, `true`, `false`, `بله`, `y`

---

#### `_parse_decimal(self, value) -> Decimal`

**توضیح**: Parse کردن decimal value از Excel.

**پارامترهای ورودی**:
- `value`: مقدار از Excel

**مقدار بازگشتی**:
- `Decimal`: مقدار decimal یا `None`

---

#### `_validate_item_data(self, data: Dict[str, Any], company_id: int, existing_items: set, existing_item_codes: set) -> List[str]`

**توضیح**: Validate کردن داده‌های item و بازگشت لیست خطاها.

**پارامترهای ورودی**:
- `data`: داده‌های item
- `company_id`: شناسه شرکت
- `existing_items`: set از نام‌های موجود
- `existing_item_codes`: set از کدهای موجود

**مقدار بازگشتی**:
- `List[str]`: لیست پیام‌های خطا

**Validation Rules**:
- Required fields: type, category, subcategory, user_segment (2 digits), name, name_en, default_unit, primary_unit
- Duplicate check: name
- Unit validation: باید در `UNIT_CHOICES` باشد
- Min stock: نمی‌تواند منفی باشد

---

#### `_create_item(self, data: Dict[str, Any], company_id: int, user) -> models.Item`

**توضیح**: ایجاد item از داده‌های validated.

**پارامترهای ورودی**:
- `data`: داده‌های validated
- `company_id`: شناسه شرکت
- `user`: user object

**مقدار بازگشتی**:
- `models.Item`: item ایجاد شده

**منطق**:
1. Resolve کردن type, category, subcategory (از code یا name)
2. Resolve کردن warehouses (از codes)
3. ایجاد item
4. ذخیره برای generate کردن codes
5. اضافه کردن warehouses

---

#### `_resolve_item_type(self, code_or_name: str, company_id: int) -> ItemType`

**توضیح**: پیدا کردن ItemType از code یا name.

**منطق**:
1. جستجو بر اساس `public_code`
2. اگر پیدا نشد، جستجو بر اساس `name`

---

#### `_resolve_category(self, code_or_name: str, company_id: int) -> ItemCategory`

**توضیح**: پیدا کردن ItemCategory از code یا name.

**منطق**: مشابه `_resolve_item_type`

---

#### `_resolve_subcategory(self, code_or_name: str, category_id: int, company_id: int) -> ItemSubcategory`

**توضیح**: پیدا کردن ItemSubcategory از code یا name.

**منطق**:
1. جستجو بر اساس `public_code` (با فیلتر category اگر داده شده باشد)
2. اگر پیدا نشد، جستجو بر اساس `name`

---

## نکات مهم

### 1. OpenPyXL Dependency
- `openpyxl` باید نصب باشد
- اگر نصب نباشد، error message نمایش داده می‌شود

### 2. Excel Format
- فقط `.xlsx` و `.xls` پشتیبانی می‌شوند
- `data_only=True` برای load کردن values (نه formulas)

### 3. Row Processing
- Header row (row 1) skip می‌شود
- Empty rows skip می‌شوند
- هر row به صورت مستقل پردازش می‌شود

### 4. Error Handling
- خطاها برای هر row ثبت می‌شوند
- خطاها در context نمایش داده می‌شوند
- Success count و error count نمایش داده می‌شوند

### 5. Duplicate Prevention
- بررسی duplicate name در همان import
- بررسی duplicate name در database

### 6. Code/Name Resolution
- Type, category, subcategory می‌توانند با code یا name مشخص شوند
- اول code جستجو می‌شود، سپس name

### 7. Warehouse Assignment
- Warehouses از comma-separated codes resolve می‌شوند
- اولین warehouse به عنوان primary تنظیم می‌شود

---

## الگوهای مشترک

1. **Company Filtering**: تمام queries بر اساس `active_company_id` فیلتر می‌شوند
2. **Error Collection**: خطاها در list جمع‌آوری و نمایش داده می‌شوند
3. **Validation**: تمام داده‌ها قبل از create validate می‌شوند
4. **Code Generation**: Item codes به صورت خودکار generate می‌شوند
