# production/views/api.py - Production API Views (Complete Documentation)

**هدف**: API endpoints برای ماژول production

این فایل شامل API endpoints برای:
- `get_bom_materials`: دریافت مواد اولیه یک BOM خاص
- `get_order_operations`: دریافت operations موجود برای یک product order
- `get_process_operations`: دریافت operations یک process
- `get_process_details`: دریافت جزئیات یک process
- `get_process_bom_materials`: دریافت BOM materials یک process

---

## وابستگی‌ها

- `production.models`: `BOM`, `BOMMaterial`, `ProductOrder`, `Process`, `ProcessOperation`, `TransferToLine`
- `production.utils.transfer`: `get_available_operations_for_order`, `is_full_order_transferred`
- `django.contrib.auth.decorators.login_required`
- `django.views.decorators.http.require_http_methods`
- `django.http.JsonResponse`, `HttpRequest`
- `django.shortcuts.get_object_or_404`
- `django.utils.translation.gettext_lazy`
- `logging`

---

## API Endpoints

### `get_bom_materials(request: HttpRequest, bom_id: int) -> JsonResponse`

**توضیح**: API endpoint برای دریافت مواد اولیه یک BOM خاص

**Decorators**:
- `@require_http_methods(["GET"])`: فقط GET request مجاز است
- `@login_required`: نیاز به authentication دارد

**پارامترهای ورودی**:
- `request`: HTTP request object
- `bom_id`: شناسه BOM (از URL parameter)

**مقدار بازگشتی**:
- `JsonResponse`: JSON response با مواد اولیه BOM

**منطق**:
1. دریافت `active_company_id` از session
2. اگر `active_company_id` وجود ندارد:
   - بازگشت `JsonResponse({'error': 'No active company'}, status=400)`
3. دریافت BOM:
   - `get_object_or_404(BOM, pk=bom_id, company_id=company_id, is_enabled=1)`
   - اگر BOM پیدا نشود، 404 برمی‌گرداند
4. دریافت مواد اولیه BOM:
   - `BOMMaterial.objects.filter(bom=bom, is_enabled=1)`
   - `select_related('material_item', 'material_type')`
   - `order_by('line_number')`
5. ساخت `materials_data`:
   - برای هر `BOMMaterial`:
     - `id`: شناسه material
     - `material_item_id`: شناسه item
     - `material_item_code`: کد item
     - `material_item_name`: نام item
     - `quantity_per_unit`: مقدار به ازای هر واحد
     - `unit`: واحد اندازه‌گیری
     - `line_number`: شماره خط
     - `description`: توضیحات
6. بازگشت `JsonResponse`:
   - `materials`: لیست materials_data
   - `bom_code`: کد BOM
   - `finished_item_name`: نام محصول نهایی
7. اگر exception رخ دهد:
   - Log error با `logger.error()`
   - بازگشت `JsonResponse({'error': str(e)}, status=500)`

**Response Format**:
```json
{
    "materials": [
        {
            "id": "1",
            "material_item_id": "10",
            "material_item_code": "MAT-001",
            "material_item_name": "Material Name",
            "quantity_per_unit": "2.5",
            "unit": "kg",
            "line_number": 1,
            "description": "Description"
        }
    ],
    "bom_code": "BOM-001",
    "finished_item_name": "Finished Item Name"
}
```

**Error Responses**:
- `400`: No active company
- `404`: BOM not found
- `500`: Internal server error

**URL**: `/production/api/bom/<bom_id>/materials/`

**نکات مهم**:
- فقط BOM های enabled (`is_enabled=1`) قابل دسترسی هستند
- فقط materials enabled (`is_enabled=1`) برگردانده می‌شوند
- مواد اولیه بر اساس `line_number` مرتب می‌شوند
- نیاز به active company در session دارد

---

### `get_order_operations(request: HttpRequest, order_id: int) -> JsonResponse`

**توضیح**: API endpoint برای دریافت operations موجود برای یک product order

**Decorators**:
- `@require_http_methods(["GET"])`: فقط GET request مجاز است
- `@login_required`: نیاز به authentication دارد

**پارامترهای ورودی**:
- `request`: HTTP request object (با query params: `include_scrap_replacement`, `scrap_replacement_mode`)
- `order_id`: شناسه Product Order (از URL parameter)

**Query Parameters**:
- `include_scrap_replacement` (optional): اگر `'true'` باشد، scrap replacement operations را هم شامل می‌شود
- `scrap_replacement_mode` (optional): اگر `'true'` باشد، فقط operations که transfer شده‌اند را برمی‌گرداند

**مقدار بازگشتی**:
- `JsonResponse`: JSON response با operations موجود

**منطق**:
1. دریافت `active_company_id` از session (اگر وجود نداشته باشد، return error 400)
2. دریافت query parameters:
   - `include_scrap_replacement = request.GET.get('include_scrap_replacement', 'false').lower() == 'true'`
   - `scrap_replacement_mode = request.GET.get('scrap_replacement_mode', 'false').lower() == 'true'`
3. دریافت Product Order:
   - `get_object_or_404(ProductOrder, pk=order_id, company_id=company_id, is_enabled=1)`
4. بررسی process:
   - اگر order.process موجود نباشد:
     - بازگشت `JsonResponse` با `operations: []`, `has_process: False`, و message
5. دریافت available operations:
   - فراخوانی `get_available_operations_for_order(order, include_scrap_replacement, scrap_replacement_mode)`
6. ساخت `operations_data`:
   - برای هر operation:
     - `id`: شناسه operation
     - `name`: نام operation
     - `sequence_order`: ترتیب sequence
     - `requires_qc`: آیا نیاز به QC دارد
     - `is_transferred`: آیا transfer شده است (از `is_full_order_transferred()`)
7. بازگشت `JsonResponse`:
   - `operations`: لیست operations_data
   - `has_process`: True
   - `is_full_order_transferred`: نتیجه `is_full_order_transferred(order)`
8. اگر exception رخ دهد:
   - Log error با `logger.error()`
   - بازگشت `JsonResponse({'error': str(e)}, status=500)`

**Response Format**:
```json
{
    "operations": [
        {
            "id": "1",
            "name": "Operation Name",
            "sequence_order": 1,
            "requires_qc": true,
            "is_transferred": false
        }
    ],
    "has_process": true,
    "is_full_order_transferred": false
}
```

**Error Responses**:
- `400`: No active company
- `404`: Order not found
- `500`: Internal server error

**URL**: `/production/api/order/<order_id>/operations/`

**نکات مهم**:
- فقط orders enabled (`is_enabled=1`) قابل دسترسی هستند
- اگر order process نداشته باشد، operations خالی برمی‌گرداند
- `scrap_replacement_mode` برای فیلتر کردن operations که transfer شده‌اند استفاده می‌شود

---

### `get_process_operations(request: HttpRequest, process_id: int) -> JsonResponse`

**توضیح**: API endpoint برای دریافت operations یک process

**Decorators**:
- `@require_http_methods(["GET"])`: فقط GET request مجاز است
- `@login_required`: نیاز به authentication دارد

**پارامترهای ورودی**:
- `request`: HTTP request object
- `process_id`: شناسه Process (از URL parameter)

**مقدار بازگشتی**:
- `JsonResponse`: JSON response با operations process

**منطق**:
1. دریافت `active_company_id` از session (اگر وجود نداشته باشد، return error 400)
2. دریافت Process:
   - `get_object_or_404(Process, pk=process_id, company_id=company_id, is_enabled=1)`
3. دریافت operations:
   - `ProcessOperation.objects.filter(process=process, is_enabled=1).order_by('sequence_order')`
   - `select_related('work_center')`
4. ساخت `operations_data`:
   - برای هر operation:
     - `id`: شناسه operation
     - `name`: نام operation
     - `sequence_order`: ترتیب sequence
     - `work_center_id`: شناسه work center (اگر موجود باشد)
     - `work_center_name`: نام work center (اگر موجود باشد)
     - `requires_qc`: آیا نیاز به QC دارد
5. بازگشت `JsonResponse`:
   - `operations`: لیست operations_data
   - `process_code`: کد process
6. اگر exception رخ دهد:
   - Log error با `logger.error()`
   - بازگشت `JsonResponse({'error': str(e)}, status=500)`

**Response Format**:
```json
{
    "operations": [
        {
            "id": "1",
            "name": "Operation Name",
            "sequence_order": 1,
            "work_center_id": "5",
            "work_center_name": "Work Center Name",
            "requires_qc": true
        }
    ],
    "process_code": "PROC-001"
}
```

**Error Responses**:
- `400`: No active company
- `404`: Process not found
- `500`: Internal server error

**URL**: `/production/api/process/<process_id>/operations/`

**نکات مهم**:
- فقط processes enabled (`is_enabled=1`) قابل دسترسی هستند
- فقط operations enabled (`is_enabled=1`) برگردانده می‌شوند
- operations بر اساس `sequence_order` مرتب می‌شوند

---

### `get_process_details(request: HttpRequest, process_id: int) -> JsonResponse`

**توضیح**: API endpoint برای دریافت جزئیات یک process

**Decorators**:
- `@require_http_methods(["GET"])`: فقط GET request مجاز است
- `@login_required`: نیاز به authentication دارد

**پارامترهای ورودی**:
- `request`: HTTP request object
- `process_id`: شناسه Process (از URL parameter)

**مقدار بازگشتی**:
- `JsonResponse`: JSON response با جزئیات process

**منطق**:
1. دریافت `active_company_id` از session (اگر وجود نداشته باشد، return error 400)
2. دریافت Process:
   - `get_object_or_404(Process, pk=process_id, company_id=company_id, is_enabled=1)`
   - `select_related('finished_item', 'bom', 'bom__finished_item')`
3. ساخت `process_data`:
   - `id`: شناسه process
   - `process_code`: کد process
   - `name`: نام process
   - `finished_item_id`: شناسه finished item (اگر موجود باشد)
   - `finished_item_code`: کد finished item (اگر موجود باشد)
   - `finished_item_name`: نام finished item (اگر موجود باشد)
   - `bom_id`: شناسه BOM (اگر موجود باشد)
   - `bom_code`: کد BOM (اگر موجود باشد)
4. بازگشت `JsonResponse`:
   - `process`: process_data
5. اگر exception رخ دهد:
   - Log error با `logger.error()`
   - بازگشت `JsonResponse({'error': str(e)}, status=500)`

**Response Format**:
```json
{
    "process": {
        "id": "1",
        "process_code": "PROC-001",
        "name": "Process Name",
        "finished_item_id": "10",
        "finished_item_code": "ITEM-001",
        "finished_item_name": "Finished Item Name",
        "bom_id": "5",
        "bom_code": "BOM-001"
    }
}
```

**Error Responses**:
- `400`: No active company
- `404`: Process not found
- `500`: Internal server error

**URL**: `/production/api/process/<process_id>/details/`

**نکات مهم**:
- فقط processes enabled (`is_enabled=1`) قابل دسترسی هستند
- finished_item و bom با select_related بهینه شده‌اند

---

### `get_process_bom_materials(request: HttpRequest, process_id: int) -> JsonResponse`

**توضیح**: API endpoint برای دریافت BOM materials یک process

**Decorators**:
- `@require_http_methods(["GET"])`: فقط GET request مجاز است
- `@login_required`: نیاز به authentication دارد

**پارامترهای ورودی**:
- `request`: HTTP request object
- `process_id`: شناسه Process (از URL parameter)

**مقدار بازگشتی**:
- `JsonResponse`: JSON response با BOM materials

**منطق**:
1. دریافت `active_company_id` از session (اگر وجود نداشته باشد، return error 400)
2. دریافت Process:
   - `get_object_or_404(Process, pk=process_id, company_id=company_id, is_enabled=1)`
   - `select_related('bom')`
3. بررسی BOM:
   - اگر process.bom موجود نباشد:
     - بازگشت `JsonResponse` با `materials: []`, `has_bom: False`, و message
4. دریافت BOM materials:
   - `BOMMaterial.objects.filter(bom=process.bom, is_enabled=1).order_by('line_number')`
   - `select_related('material_item', 'material_type')`
5. ساخت `materials_data`:
   - برای هر `BOMMaterial`:
     - `id`: شناسه material
     - `material_item_id`: شناسه item
     - `material_item_code`: کد item
     - `material_item_name`: نام item
     - `quantity_per_unit`: مقدار به ازای هر واحد
     - `unit`: واحد اندازه‌گیری
     - `line_number`: شماره خط
     - `description`: توضیحات
6. بازگشت `JsonResponse`:
   - `materials`: لیست materials_data
   - `has_bom`: True
   - `bom_code`: کد BOM
   - `finished_item_name`: نام محصول نهایی
7. اگر exception رخ دهد:
   - Log error با `logger.error()`
   - بازگشت `JsonResponse({'error': str(e)}, status=500)`

**Response Format**:
```json
{
    "materials": [
        {
            "id": "1",
            "material_item_id": "10",
            "material_item_code": "MAT-001",
            "material_item_name": "Material Name",
            "quantity_per_unit": "2.5",
            "unit": "kg",
            "line_number": 1,
            "description": "Description"
        }
    ],
    "has_bom": true,
    "bom_code": "BOM-001",
    "finished_item_name": "Finished Item Name"
}
```

**Error Responses**:
- `400`: No active company
- `404`: Process not found
- `500`: Internal server error

**URL**: `/production/api/process/<process_id>/bom-materials/`

**نکات مهم**:
- فقط processes enabled (`is_enabled=1`) قابل دسترسی هستند
- اگر process BOM نداشته باشد، materials خالی برمی‌گرداند
- فقط materials enabled (`is_enabled=1`) برگردانده می‌شوند
- مواد اولیه بر اساس `line_number` مرتب می‌شوند
