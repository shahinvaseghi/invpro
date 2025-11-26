# inventory/views/item_import.py - Item Import Views

**هدف**: Views برای import کالاها از فایل Excel

این فایل شامل views برای:
- Excel Template Download (دانلود قالب Excel)
- Excel Import (import از Excel)

---

## Views

### `ItemExcelTemplateDownloadView`

**توضیح**: دانلود قالب Excel برای import کالاها

**Type**: `InventoryBaseView, View`

**منطق**:
1. یک فایل Excel با ستون‌های مورد نیاز ایجاد می‌کند
2. نمونه داده‌ها را اضافه می‌کند
3. فایل را به عنوان attachment دانلود می‌کند

**ستون‌های Excel**:
- `item_code`: کد کالا
- `name`: نام کالا
- `type_id`: شناسه نوع کالا
- `category_id`: شناسه دسته کالا
- `subcategory_id`: شناسه زیردسته کالا
- `default_unit`: واحد پیش‌فرض
- `primary_unit`: واحد اصلی
- `has_lot_tracking`: ردیابی سریال (0 یا 1)
- `warehouse_ids`: شناسه‌های انبار (comma-separated)

**URL**: `/inventory/items/import/template/`

---

### `ItemExcelImportView`

**توضیح**: import کالاها از فایل Excel

**Type**: `InventoryBaseView, TemplateView`

**Template**: `inventory/item_import.html`

**منطق**:
1. فایل Excel را از کاربر دریافت می‌کند
2. هر ردیف را parse می‌کند
3. کالاها را ایجاد یا به‌روزرسانی می‌کند
4. نتایج (موفق/خطا) را نمایش می‌دهد

**Context Variables**:
- `import_results`: لیست نتایج import (موفق/خطا)
- `success_count`: تعداد کالاهای موفق
- `error_count`: تعداد خطاها

**URL**: `/inventory/items/import/`

---

## نکات مهم

1. **Validation**: تمام داده‌ها قبل از import validate می‌شوند
2. **Error Handling**: خطاها ثبت می‌شوند و به کاربر نمایش داده می‌شوند
3. **Company Scoping**: تمام کالاها به شرکت فعال اختصاص داده می‌شوند

