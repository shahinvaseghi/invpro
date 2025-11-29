# production/views/api.py - Production API Views (Complete Documentation)

**هدف**: API endpoints برای ماژول production

این فایل شامل API endpoints برای:
- `get_bom_materials`: دریافت مواد اولیه یک BOM خاص

---

## وابستگی‌ها

- `production.models`: `BOM`, `BOMMaterial`
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
