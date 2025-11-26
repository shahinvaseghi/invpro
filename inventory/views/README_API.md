# inventory/views/api.py - API Endpoints

**هدف**: JSON API endpoints برای تعاملات دینامیک فرم و فیلتر داده در رابط وب

تمام endpoints JSON برمی‌گردانند و نیاز به authentication دارند.

---

## Authentication

تمام endpoints نیاز دارند:
- کاربر باید logged in باشد (`@login_required` decorator)
- شرکت فعال باید در session تنظیم شده باشد (`active_company_id`)
- کاربر باید به شرکت فعال دسترسی داشته باشد

---

## Endpoints

### `get_item_allowed_units(request: HttpRequest) -> JsonResponse`

**توضیح**: لیست واحدهای مجاز برای یک کالا را برمی‌گرداند (واحد اصلی + واحدهای تبدیل).

**URL**: `GET /fa/inventory/api/item-allowed-units/`

**Query Parameters**:
- `item_id` (required): شناسه کالا

**Response**:
```json
{
  "units": [
    {"value": "EA", "label": "Each"},
    {"value": "1", "label": "Box (10 EA = 1 Box)"}
  ],
  "default_unit": "EA"
}
```

**Status Codes**:
- `200`: Success
- `400`: Bad Request (missing item_id or no active company)
- `401`: Unauthorized
- `404`: Item not found
- `500`: Internal Server Error

**منطق**:
1. کالا را از دیتابیس می‌خواند
2. واحد اصلی و پیش‌فرض را اضافه می‌کند
3. واحدهای تبدیل از `ItemUnit` را اضافه می‌کند
4. به label ها map می‌کند و برمی‌گرداند

---

### `get_filtered_categories(request: HttpRequest) -> JsonResponse`

**توضیح**: دسته‌هایی که کالاهای نوع خاص دارند را برمی‌گرداند.

**URL**: `GET /fa/inventory/api/filtered-categories/`

**Query Parameters**:
- `type_id` (optional): فیلتر بر اساس نوع کالا

**Response**:
```json
{
  "categories": [
    {"value": "1", "label": "Raw Materials"},
    {"value": "2", "label": "Components"}
  ]
}
```

**Status Codes**:
- `200`: Success
- `400`: No active company
- `500`: Internal Server Error

**منطق**:
- اگر `type_id` ارائه شود، فقط دسته‌هایی که کالاهای آن نوع دارند را برمی‌گرداند
- در غیر این صورت، تمام دسته‌هایی که کالا دارند را برمی‌گرداند

---

### `get_filtered_subcategories(request: HttpRequest) -> JsonResponse`

**توضیح**: زیردسته‌ها را بر اساس دسته (و اختیاری نوع) فیلتر می‌کند.

**URL**: `GET /fa/inventory/api/filtered-subcategories/`

**Query Parameters**:
- `category_id` (required): فیلتر بر اساس دسته
- `type_id` (optional): فیلتر اختیاری بر اساس نوع

**Response**:
```json
{
  "subcategories": [
    {"value": "1", "label": "25"},
    {"value": "2", "label": "27"}
  ]
}
```

**Status Codes**:
- `200`: Success
- `400`: No active company or missing category_id
- `500`: Internal Server Error

**نکات مهم**:
- اگر `category_id` ارائه نشود، لیست خالی برمی‌گرداند
- تمام زیردسته‌های دسته را برمی‌گرداند، حتی اگر کالا نداشته باشند

---

### `get_filtered_items(request: HttpRequest) -> JsonResponse`

**توضیح**: کالاها را بر اساس نوع، دسته و/یا زیردسته فیلتر می‌کند.

**URL**: `GET /fa/inventory/api/filtered-items/`

**Query Parameters**:
- `type_id` (optional): فیلتر بر اساس نوع
- `category_id` (optional): فیلتر بر اساس دسته
- `subcategory_id` (optional): فیلتر بر اساس زیردسته

**Response**:
```json
{
  "items": [
    {
      "value": "123",
      "label": "001-002-003-0001 - Item Name",
      "type_id": "1",
      "category_id": "2",
      "subcategory_id": "3"
    }
  ]
}
```

**Status Codes**:
- `200`: Success
- `400`: No active company
- `500`: Internal Server Error

---

### `get_item_units(request: HttpRequest) -> JsonResponse`

**توضیح**: اطلاعات واحدهای کالا را به صورت تفصیلی برمی‌گرداند (واحد اصلی و واحدهای تبدیل).

**URL**: `GET /fa/inventory/api/item-units/`

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
      "label": "Box (10 EA = 1 Box)",
      "is_base": false,
      "unit_name": "Box"
    }
  ],
  "item_type_id": 1,
  "item_type_name": "Raw Material",
  "category_id": 2,
  "subcategory_id": 3
}
```

**Status Codes**:
- `200`: Success
- `400`: Missing item_id or no active company
- `404`: Item not found
- `500`: Internal Server Error

**نکات مهم**:
- همچنین `item_type_id`, `category_id`, `subcategory_id` را برمی‌گرداند برای auto-filling در فرم‌ها

---

### `get_item_allowed_warehouses(request: HttpRequest) -> JsonResponse`

**توضیح**: لیست انبارهایی که یک کالا می‌تواند در آن‌ها ذخیره شود را برمی‌گرداند (بر اساس `ItemWarehouse`).

**URL**: `GET /fa/inventory/api/item-allowed-warehouses/`

**Query Parameters**:
- `item_id` (required): شناسه کالا

**Response**:
```json
{
  "warehouses": [
    {"value": "1", "label": "00001 - Main Warehouse"},
    {"value": "2", "label": "00002 - Secondary Warehouse"}
  ]
}
```

**Status Codes**:
- `200`: Success
- `400`: Missing item_id or no active company
- `404`: Item not found
- `500`: Internal Server Error

**نکات مهم**:
- اگر هیچ انباری تنظیم نشده باشد، لیست خالی برمی‌گرداند
- این محدودیت سخت انبار را اعمال می‌کند

---

### `get_temporary_receipt_data(request: HttpRequest) -> JsonResponse`

**توضیح**: داده‌های رسید موقت را برای auto-filling ردیف‌های رسید دائم برمی‌گرداند.

**URL**: `GET /fa/inventory/api/temporary-receipt-data/`

**Query Parameters**:
- `temporary_receipt_id` (required): شناسه رسید موقت

**Response**:
```json
{
  "item_id": 123,
  "item_code": "001-002-003-0001",
  "item_name": "Item Name",
  "warehouse_id": 1,
  "warehouse_code": "00001",
  "warehouse_name": "Main Warehouse",
  "quantity": "10.000000",
  "entered_quantity": "10.000000",
  "unit": "EA",
  "entered_unit": "EA",
  "supplier_id": 1,
  "supplier_code": "500001",
  "supplier_name": "Supplier Name"
}
```

**Status Codes**:
- `200`: Success
- `400`: Missing temporary_receipt_id or no active company
- `404`: Temporary receipt not found
- `500`: Internal Server Error

---

### `get_item_available_serials(request: HttpRequest) -> JsonResponse`

**توضیح**: شماره سریال‌های در دسترس برای یک کالا در یک انبار را برمی‌گرداند.

**URL**: `GET /fa/inventory/api/item-available-serials/`

**Query Parameters**:
- `item_id` (required): شناسه کالا
- `warehouse_id` (required): شناسه انبار

**Response**:
```json
{
  "serials": [
    {
      "value": "1",
      "label": "SER-202511-000001",
      "status": "available"
    }
  ],
  "has_lot_tracking": true,
  "count": 1
}
```

**Status Codes**:
- `200`: Success
- `400`: Missing parameters or no active company
- `404`: Item or warehouse not found
- `500`: Internal Server Error

**نکات مهم**:
- فقط سریال‌های با وضعیت `AVAILABLE` را برمی‌گرداند (نه `RESERVED`, `ISSUED`, etc.)
- اگر کالا `has_lot_tracking != 1` باشد، `has_lot_tracking: false` برمی‌گرداند

---

### `update_serial_secondary_code(request: HttpRequest, serial_id: int) -> JsonResponse`

**توضیح**: کد سریال ثانویه را برای یک سریال به‌روزرسانی می‌کند.

**URL**: `POST /fa/inventory/api/serial/<serial_id>/update-secondary/`

**URL Parameters**:
- `serial_id` (required): شناسه سریال

**Request Body**:
```json
{
  "secondary_serial_code": "USER-INPUT-CODE"
}
```

**Response**:
```json
{
  "success": true
}
```

**Error Response**:
```json
{
  "error": "Error message",
  "success": false
}
```

**Status Codes**:
- `200`: Success
- `400`: No active company or invalid request body
- `404`: Serial not found
- `500`: Internal Server Error

---

### `get_warehouse_work_lines(request: HttpRequest) -> JsonResponse`

**توضیح**: خطوط کاری مرتبط با یک انبار را برمی‌گرداند (از ماژول production).

**URL**: `GET /fa/inventory/api/warehouse-work-lines/`

**Query Parameters**:
- `warehouse_id` (required): شناسه انبار

**Response**:
```json
{
  "work_lines": [
    {"value": "1", "label": "00001 · Production Line 1"},
    {"value": "2", "label": "00002 · Production Line 2"}
  ],
  "count": 2
}
```

**Status Codes**:
- `200`: Success
- `400`: Missing warehouse_id or no active company
- `404`: Warehouse not found
- `500`: Internal Server Error

**نکات مهم**:
- اگر ماژول production نصب نباشد، لیست خالی برمی‌گرداند
- از `shared.utils.modules.get_work_line_model()` استفاده می‌کند

---

## Error Handling

تمام endpoints از try-except blocks استفاده می‌کنند و خطاهای مناسب را برمی‌گردانند:

```python
try:
    # Logic
    return JsonResponse({'data': data})
except Exception as e:
    logger.error(f"Error: {e}", exc_info=True)
    return JsonResponse({'error': str(e)}, status=500)
```

---

## Logging

تمام endpoints از logger استفاده می‌کنند:

```python
logger = logging.getLogger('inventory.views.api')
```

---

## وابستگی‌ها

- `django.contrib.auth.decorators`: `login_required`
- `django.views.decorators.http`: `require_http_methods`
- `django.http`: `JsonResponse`, `HttpRequest`
- `django.shortcuts`: `get_object_or_404`
- `inventory.models`: تمام مدل‌های inventory
- `inventory.forms`: `UNIT_CHOICES`
- `shared.utils.modules`: برای بررسی نصب ماژول production

---

## استفاده در پروژه

این endpoints در JavaScript برای:
- Cascading dropdowns (type → category → subcategory → items)
- Dynamic unit selection
- Warehouse filtering
- Serial assignment
- Auto-filling forms

**مثال JavaScript**:
```javascript
// Get categories when type is selected
fetch(`/fa/inventory/api/filtered-categories/?type_id=${typeId}`)
  .then(response => response.json())
  .then(data => {
    // Populate category dropdown
  });
```

---

## نکات مهم

1. **Authentication**: تمام endpoints نیاز به login دارند
2. **Company Scoping**: تمام queries بر اساس `active_company_id` فیلتر می‌شوند
3. **Error Handling**: تمام خطاها catch می‌شوند و JSON error response برمی‌گردانند
4. **Logging**: خطاها log می‌شوند برای debugging
5. **Performance**: Queries بهینه شده‌اند با `select_related` و `prefetch_related`

---

## مستندات کامل

برای مستندات کامل API endpoints، به [API Documentation](../../docs/API_DOCUMENTATION.md) مراجعه کنید.

