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
- `type_id` (optional): این پارامتر در حال حاضر استفاده نمی‌شود (برای سازگاری با آینده نگه داشته شده)

**Response**:
```json
{
  "categories": [{"value": "1", "label": "Category Name"}, ...]
}
```

**منطق**:
- دریافت **همه** دسته‌بندی‌های enabled برای company
- دسته‌بندی‌ها مستقل از type هستند (در schema فعلی)
- مرتب‌سازی بر اساس `name`
- **نکته**: `type_id` در حال حاضر نادیده گرفته می‌شود. اگر در آینده نیاز به فیلتر بر اساس type باشد، می‌توان اضافه کرد

**URL**: `/inventory/api/categories/`

---

## get_filtered_subcategories

**Decorators**: `@login_required`

**Method**: `GET`

**Query Parameters**:
- `category_id` (required): شناسه دسته‌بندی - **الزامی است**
- `type_id` (optional): این پارامتر در حال حاضر استفاده نمی‌شود (فقط hint است، strict filter نیست)

**Response**:
```json
{
  "subcategories": [{"value": "1", "label": "Subcategory Name"}, ...]
}
```

**منطق**:
- اگر `category_id` داده نشود، **فوراً empty list برمی‌گرداند** (category الزامی است)
- فیلتر بر اساس `category_id` (required)
- دریافت همه زیردسته‌بندی‌های enabled برای company که به category مربوط هستند
- `type_id` فقط hint است و استفاده نمی‌شود - همه زیردسته‌بندی‌های category برگردانده می‌شوند حتی اگر کالایی نداشته باشند
- مرتب‌سازی بر اساس `name`

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
- `include_item_id` (optional): شامل کردن یک item خاص حتی اگر با فیلترها match نکند (برای formset initial)

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
1. دریافت `company_id` از session
2. شروع با تمام enabled items در company (`is_enabled=1`)
3. `select_related('type', 'category', 'subcategory')` برای بهینه‌سازی
4. **Permission Filtering**:
   - اگر user superuser باشد: بدون فیلتر (می‌تواند همه را ببیند)
   - اگر `view_all` permission داشته باشد: بدون فیلتر
   - اگر فقط `view_own` permission داشته باشد: فیلتر `created_by=request.user`
   - اگر هیچ permission نداشته باشد: empty queryset
5. **include_item_id**: اگر `include_item_id` داده شود و item در queryset نباشد، با `union` اضافه می‌شود (برای formset initial)
6. فیلتر بر اساس type, category, subcategory (optional)
7. جستجو در name, item_code, full_item_code با `Q` (optional)
8. مرتب‌سازی بر اساس `name`
9. ساخت response با `value`, `label`, `type_id`, `category_id`, `subcategory_id`
10. `total_count`: تعداد کل کالاهای پیدا شده (برای debugging)

**نکات مهم**:
- می‌تواند بدون فیلترها فقط search کند
- فقط کالاهای enabled (`is_enabled=1`) را برمی‌گرداند
- `include_item_id` برای مواردی که item در formset initial است اما با فیلترها match نمی‌کند (مثلاً از purchase request)

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
1. دریافت `temporary_receipt_id` از query parameters
2. دریافت `company_id` از session
3. دریافت `ReceiptTemporary` از database
4. **فیلتر خطوط QC-approved**:
   - فقط خطوط با `is_enabled=1`, `is_qc_approved=1`, `qc_approved_quantity__isnull=False`
   - اگر هیچ خط QC-approved وجود نداشته باشد، خطا برمی‌گرداند
5. دریافت supplier از هر خط (هر خط می‌تواند supplier مستقل داشته باشد)
6. ساخت response:
   - داده‌های اولین خط به عنوان داده اصلی (برای backward compatibility)
   - همه خطوط در آرایه `lines` (برای پشتیبانی از چندخطی)
   - استفاده از `qc_approved_quantity` به جای `quantity` اصلی
   - supplier برای هر خط از همان خط خوانده می‌شود (line-level supplier)

**نکات مهم**:
- فقط خطوط QC-approved برگردانده می‌شوند
- اگر هیچ خط QC-approved وجود نداشته باشد، خطا با پیام فارسی برمی‌گرداند
- تأمین‌کننده در سطح خط نگه‌داری می‌شود (هر خط می‌تواند supplier مستقل داشته باشد)
- استفاده از `qc_approved_quantity` به جای `quantity` اصلی (مهم برای QC workflow)

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
1. دریافت `item_id` و `warehouse_id` از query parameters
2. دریافت `company_id` از session
3. دریافت `Item` از database (با `is_enabled=1`)
4. بررسی `has_lot_tracking`: اگر `!= 1` باشد، empty list برمی‌گرداند
5. دریافت `Warehouse` از database (با `is_enabled=1`)
6. دریافت سریال‌های AVAILABLE:
   - فیلتر: `company_id`, `item`, `current_warehouse`, `current_status=AVAILABLE`
   - **نکته**: فقط AVAILABLE (نه RESERVED) - سریال‌های RESERVED برای issues دیگر نمایش داده نمی‌شوند
7. مرتب‌سازی بر اساس `serial_code`
8. ساخت response با `value` (pk), `label` (serial_code), `status`

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
