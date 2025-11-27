# inventory/views/api.py - Inventory API Endpoints (Complete Documentation)

**هدف**: API endpoints برای ماژول inventory (همه JSON response برمی‌گردانند)

این فایل شامل 10 function-based view:
- `get_item_allowed_units`: دریافت واحدهای مجاز برای یک کالا
- `get_filtered_categories`: دریافت دسته‌بندی‌های فیلتر شده
- `get_filtered_subcategories`: دریافت زیردسته‌بندی‌های فیلتر شده
- `get_filtered_items`: دریافت کالاهای فیلتر شده
- `get_item_units`: دریافت واحدهای یک کالا
- `get_item_allowed_warehouses`: دریافت انبارهای مجاز برای یک کالا
- `get_temporary_receipt_data`: دریافت داده‌های receipt موقت
- `get_item_available_serials`: دریافت سریال‌های موجود یک کالا
- `update_serial_secondary_code`: به‌روزرسانی کد ثانویه سریال
- `get_warehouse_work_lines`: دریافت خطوط کار یک انبار

---

## وابستگی‌ها

- `inventory.models`: `Item`, `ItemCategory`, `ItemSubcategory`, `ItemUnit`, `ItemSerial`, `Warehouse`, `ReceiptTemporary`, `ItemWarehouse`
- `inventory.forms`: `UNIT_CHOICES`
- `inventory.services.serials`: `sync_issue_line_serials`
- `shared.utils.modules`: `get_work_line_model`
- `django.contrib.auth.decorators.login_required`
- `django.views.decorators.http.require_http_methods`
- `django.http.JsonResponse`, `HttpRequest`
- `django.shortcuts.get_object_or_404`
- `django.db.models.Q`
- `logging`

---

## get_item_allowed_units

**Decorators**: `@login_required`

**Method**: `GET`

**Query Parameters**:
- `item_id` (required): شناسه کالا

**Response**:
```json
{
  "units": [{"value": "EA", "label": "عدد"}, ...],
  "default_unit": "EA"
}
```

**منطق**:
- دریافت `default_unit` و `primary_unit` از item
- دریافت واحدها از `ItemUnit` conversions
- Map کردن به labels از `UNIT_CHOICES`

**نکات مهم**:
- اگر item با `is_enabled=1` پیدا نشود، بدون filter جستجو می‌کند (برای formset initial)

**URL**: `/inventory/api/item-units/`

---

## get_filtered_categories

**Decorators**: `@require_http_methods(["GET"]), @login_required`

**Method**: `GET`

**Query Parameters**:
- `type_id` (optional): فیلتر بر اساس نوع کالا

**Response**:
```json
{
  "categories": [{"value": "1", "label": "Category Name"}, ...]
}
```

**منطق**:
- دریافت دسته‌بندی‌هایی که حداقل یک کالا دارند
- اگر `type_id` داده شود، فقط دسته‌بندی‌هایی که کالاهای این نوع دارند

**URL**: `/inventory/api/categories/`

---

## get_filtered_subcategories

**Decorators**: `@login_required`

**Method**: `GET`

**Query Parameters**:
- `category_id` (required): شناسه دسته‌بندی
- `type_id` (optional): فیلتر بر اساس نوع کالا

**Response**:
```json
{
  "subcategories": [{"value": "1", "label": "Subcategory Name"}, ...]
}
```

**منطق**:
- اگر `category_id` داده نشود، empty list برمی‌گرداند
- فیلتر بر اساس `category_id` (required)
- `type_id` فقط hint است (strict filter نیست)

**URL**: `/inventory/api/subcategories/`

---

## get_filtered_items

**Decorators**: `@login_required`

**Method**: `GET`

**Query Parameters**:
- `type_id` (optional): فیلتر بر اساس نوع کالا
- `category_id` (optional): فیلتر بر اساس دسته‌بندی
- `subcategory_id` (optional): فیلتر بر اساس زیردسته‌بندی
- `search` (optional): جستجو در name, item_code, full_item_code

**Response**:
```json
{
  "items": [
    {
      "value": "1",
      "label": "Item Name · ITM-001",
      "type_id": "1",
      "category_id": "2",
      "subcategory_id": "3"
    },
    ...
  ],
  "total_count": 16
}
```

**منطق**:
- فیلتر بر اساس type, category, subcategory (optional)
- جستجو در name, item_code, full_item_code (optional)
- می‌تواند بدون فیلترها فقط search کند
- فقط کالاهای enabled (`is_enabled=1`) را برمی‌گرداند
- `total_count`: تعداد کل کالاهای پیدا شده (برای debugging)

**Logging**:
- لاگ‌های `get_filtered_items: Found X items` و `get_filtered_items: Returning X items` در ترمینال نمایش داده می‌شوند

**URL**: `/inventory/api/filtered-items/`

---

## get_item_units

**Decorators**: `@login_required`

**Method**: `GET`

**Query Parameters**:
- `item_id` (required): شناسه کالا

**Response**:
```json
{
  "units": [
    {
      "value": "base_EA",
      "label": "EA (واحد اصلی)",
      "is_base": true,
      "unit_name": "EA"
    },
    {
      "value": "1",
      "label": "KG (10 EA = 1 KG)",
      "is_base": false,
      "unit_name": "KG"
    }
  ],
  "item_type_id": 1,
  "item_type_name": "Type Name",
  "category_id": 2,
  "subcategory_id": 3
}
```

**منطق**:
- دریافت primary unit (base unit)
- دریافت conversion units از `ItemUnit`
- شامل اطلاعات type, category, subcategory برای auto-setting

**URL**: `/inventory/api/item-units/`

---

## get_item_allowed_warehouses

**Decorators**: `@login_required`

**Method**: `GET`

**Query Parameters**:
- `item_id` (required): شناسه کالا

**Response**:
```json
{
  "warehouses": [{"value": "1", "label": "WH-001 - Warehouse Name"}, ...]
}
```

**منطق**:
- دریافت انبارهای مجاز از `ItemWarehouse` relations
- فقط انبارهای enabled
- اگر هیچ انباری تنظیم نشده باشد، empty list (enforces strict restrictions)

**نکات مهم**:
- اگر item با `is_enabled=1` پیدا نشود، بدون filter جستجو می‌کند

**URL**: `/inventory/api/item-warehouses/`

---

## get_temporary_receipt_data

**Decorators**: `@require_http_methods(["GET"]), @login_required`

**Method**: `GET`

**Query Parameters**:
- `temporary_receipt_id` (required): شناسه receipt موقت

**Response** (Success):
```json
{
  "item_id": 1,
  "item_code": "ITM-001",
  "item_name": "Item Name",
  "warehouse_id": 1,
  "warehouse_code": "WH-001",
  "warehouse_name": "Warehouse Name",
  "quantity": "100.00",
  "entered_quantity": "100.00",
  "unit": "EA",
  "entered_unit": "EA",
  "supplier_id": 1,
  "supplier_code": "SUP-001",
  "supplier_name": "Supplier Name",
  "lines": [
    {
      "item_id": 1,
      "item_code": "ITM-001",
      "item_name": "Item Name",
      "warehouse_id": 1,
      "warehouse_code": "WH-001",
      "warehouse_name": "Warehouse Name",
      "quantity": "100.00",
      "entered_quantity": "100.00",
      "unit": "EA",
      "entered_unit": "EA",
      "supplier_id": 1,
      "supplier_code": "SUP-001",
      "supplier_name": "Supplier Name"
    },
    ...
  ]
}
```

**Response** (Error):
```json
{
  "error": "Temporary receipt has no lines",
  "message": "رسید موقت انتخاب شده هیچ خطی ندارد. لطفاً یک رسید موقت معتبر با حداقل یک خط انتخاب کنید."
}
```

**منطق**:
- دریافت داده‌های receipt موقت برای auto-filling permanent receipt
- اقلام و انبارها از `ReceiptTemporaryLine` خوانده می‌شوند؛ اطلاعات تأمین‌کننده همیشه از خود `ReceiptTemporary` گرفته می‌شود (چون خطوط فیلد supplier ندارند)
- داده‌های اولین خط به عنوان داده اصلی برگردانده می‌شود (برای backward compatibility)
- همه خطوط در آرایه `lines` برگردانده می‌شوند (برای پشتیبانی از چندخطی)
- اگر رسید موقت هیچ خطی نداشته باشد، خطا برمی‌گرداند

**نکات مهم**:
- رسید موقت باید حداقل یک خط داشته باشد
- تأمین‌کننده فقط در سطح هدر نگه‌داری می‌شود و برای هر خط همان مقدار تکرار می‌شود
- برای رسیدهای موقت قدیمی که خط ندارند، خطا برمی‌گرداند

**استفاده در Frontend**:
- این API توسط JavaScript در فرم ایجاد رسید دائم استفاده می‌شود
- هنگام انتخاب temporary receipt در dropdown، یک event listener تغییر را trigger می‌کند
- داده‌های دریافت شده برای populate کردن خطوط formset استفاده می‌شوند:
  - برای هر خط، یک فرم جدید ایجاد می‌شود
  - item، warehouse، quantity، unit و supplier به‌صورت خودکار set می‌شوند
  - units و warehouses با استفاده از `Promise.all` به‌صورت موازی لود می‌شوند
  - بعد از لود شدن options، مقادیر set می‌شوند
- اگر temporary receipt انتخاب نشود، خطوط پاک می‌شوند

**URL**: `/inventory/api/temporary-receipt-data/`

---

## get_item_available_serials

**Decorators**: `@require_http_methods(["GET"]), @login_required`

**Method**: `GET`

**Query Parameters**:
- `item_id` (required): شناسه کالا
- `warehouse_id` (required): شناسه انبار

**Response**:
```json
{
  "serials": [
    {
      "value": "1",
      "label": "SERIAL-001",
      "status": "AVAILABLE"
    },
    ...
  ],
  "has_lot_tracking": true,
  "count": 5
}
```

**منطق**:
- بررسی `has_lot_tracking` برای item
- دریافت سریال‌های AVAILABLE (نه RESERVED)
- فیلتر بر اساس company, item, warehouse, status

**URL**: `/inventory/api/item-serials/`

---

## update_serial_secondary_code

**Decorators**: `@require_http_methods(["POST"]), @login_required`

**Method**: `POST`

**URL Parameters**:
- `serial_id`: شناسه سریال

**Request Body (JSON)**:
```json
{
  "secondary_serial_code": "SEC-001"
}
```

**Response**:
```json
{
  "success": true
}
```

**منطق**:
- به‌روزرسانی `secondary_serial_code` برای یک سریال

**URL**: `/inventory/api/serial/<serial_id>/update-secondary-code/`

---

## get_warehouse_work_lines

**Decorators**: `@require_http_methods(["GET"]), @login_required`

**Method**: `GET`

**Query Parameters**:
- `warehouse_id` (required): شناسه انبار

**Response**:
```json
{
  "work_lines": [
    {
      "value": "1",
      "label": "WL-001 · Work Line Name"
    },
    ...
  ],
  "count": 5
}
```

**منطق**:
- دریافت خطوط کار از production module
- اگر production module نصب نباشد، empty list
- فیلتر بر اساس company, warehouse, enabled

**URL**: `/inventory/api/warehouse-work-lines/`

---

## نکات مهم

### 1. Authentication
- تمام endpoints از `@login_required` استفاده می‌کنند
- برخی از `@require_http_methods` استفاده می‌کنند

### 2. Company Filtering
- تمام endpoints بر اساس `active_company_id` فیلتر می‌کنند

### 3. Error Handling
- خطاها در JSON response با status code مناسب برمی‌گردند
- Logging برای خطاها

### 4. Item Enabled Check
- برخی endpoints اگر item با `is_enabled=1` پیدا نشود، بدون filter جستجو می‌کنند (برای formset initial)

---

## الگوهای مشترک

1. **JSON Response**: تمام endpoints JSON response برمی‌گردانند
2. **Company Filtering**: تمام queryset ها بر اساس `active_company_id` فیلتر می‌شوند
3. **Error Handling**: خطاها در JSON با status code مناسب
4. **Logging**: استفاده از logger برای خطاها
