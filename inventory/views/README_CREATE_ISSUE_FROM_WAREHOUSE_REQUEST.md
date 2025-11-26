# inventory/views/create_issue_from_warehouse_request.py - Create Issue from Warehouse Request (Complete Documentation)

**هدف**: Views برای انتخاب quantity از Warehouse Request قبل از ایجاد Issue documents

این فایل شامل 4 view class:
- CreateIssueFromWarehouseRequestView: Base view برای انتخاب quantity
- CreatePermanentIssueFromWarehouseRequestView: برای permanent issue
- CreateConsumptionIssueFromWarehouseRequestView: برای consumption issue
- CreateConsignmentIssueFromWarehouseRequestView: برای consignment issue

**نکته**: این views یک intermediate step هستند که کاربر می‌تواند quantity را review و adjust کند قبل از ایجاد issue.

---

## وابستگی‌ها

- `inventory.views.base`: `InventoryBaseView`
- `inventory.models`: `WarehouseRequest`
- `shared.mixins`: `FeaturePermissionRequiredMixin`
- `django.views.generic.TemplateView`
- `django.http.HttpResponseRedirect`
- `django.shortcuts.get_object_or_404`
- `django.urls.reverse`
- `django.utils.translation.gettext_lazy`
- `django.contrib.messages`
- `decimal.Decimal`, `InvalidOperation`
- `logging`

---

## CreateIssueFromWarehouseRequestView

**Type**: `FeaturePermissionRequiredMixin, InventoryBaseView, TemplateView`

**Template**: `inventory/create_issue_from_warehouse_request.html`

**Attributes**:
- `issue_type`: `None` (باید در subclass تنظیم شود: `'permanent'`, `'consumption'`, `'consignment'`)
- `template_name`: `'inventory/create_issue_from_warehouse_request.html'`
- `required_action`: `'create_issue_from_warehouse_request'`

**متدها**:

#### `get_warehouse_request(self, pk: int) -> WarehouseRequest`

**توضیح**: دریافت warehouse request و بررسی permissions.

**پارامترهای ورودی**:
- `pk`: شناسه warehouse request

**مقدار بازگشتی**:
- `WarehouseRequest`: warehouse request object

**منطق**:
1. بررسی `active_company_id`
2. دریافت warehouse request با فیلتر:
   - `company_id`
   - `request_status='approved'`
   - `is_enabled=1`

**نکات مهم**:
- فقط approved requests قابل استفاده هستند

---

#### `get_context_data(self, **kwargs: Dict[str, Any]) -> Dict[str, Any]`

**توضیح**: نمایش form برای review warehouse request و adjust quantity.

**Context Variables**:
- `warehouse_request`: warehouse request object
- `issue_type`: نوع issue (`'permanent'`, `'consumption'`, `'consignment'`)
- `issue_type_name`: نام فارسی نوع issue
- `remaining_quantity`: مقدار باقیمانده (quantity_requested - quantity_issued)
- `default_quantity`: مقدار پیش‌فرض (برابر remaining_quantity)

**منطق**:
1. دریافت warehouse request
2. محاسبه remaining quantity
3. تنظیم default quantity

---

#### `post(self, request, *args, **kwargs) -> HttpResponseRedirect`

**توضیح**: پردازش quantity انتخاب شده و redirect به issue creation.

**Request POST Data**:
- `quantity`: مقدار انتخاب شده (required)
- `notes`: یادداشت‌های اختیاری (optional)

**منطق**:
1. دریافت quantity از form
2. Parse کردن به Decimal
3. بررسی quantity > 0
4. بررسی quantity <= remaining_quantity (اگر بیشتر باشد، adjust می‌شود)
5. ذخیره داده‌ها در session:
   - Key: `warehouse_request_{pk}_issue_{issue_type}_data`
   - Data: `{'warehouse_request_id': pk, 'quantity': str(quantity), 'notes': notes}`
6. Redirect به issue creation view

**Redirect URLs**:
- Permanent: `inventory:issue_permanent_create_from_warehouse_request`
- Consumption: `inventory:issue_consumption_create_from_warehouse_request`
- Consignment: `inventory:issue_consignment_create_from_warehouse_request`

**Error Handling**:
- اگر quantity <= 0: error message
- اگر quantity > remaining: warning message و adjust
- اگر parse error: error message

---

## CreatePermanentIssueFromWarehouseRequestView

**Type**: `CreateIssueFromWarehouseRequestView`

**Attributes**:
- `issue_type`: `'permanent'`
- `feature_code`: `'inventory.issues.permanent'`

**توضیحات**: Subclass برای permanent issue

---

## CreateConsumptionIssueFromWarehouseRequestView

**Type**: `CreateIssueFromWarehouseRequestView`

**Attributes**:
- `issue_type`: `'consumption'`
- `feature_code`: `'inventory.issues.consumption'`

**توضیحات**: Subclass برای consumption issue

---

## CreateConsignmentIssueFromWarehouseRequestView

**Type**: `CreateIssueFromWarehouseRequestView`

**Attributes**:
- `issue_type`: `'consignment'`
- `feature_code`: `'inventory.issues.consignment'`

**توضیحات**: Subclass برای consignment issue

---

## نکات مهم

### 1. Session Management
- داده‌ها در session ذخیره می‌شوند
- Session key: `warehouse_request_{pk}_issue_{issue_type}_data`
- Session data شامل: `warehouse_request_id`, `quantity`, `notes`

### 2. Quantity Validation
- Quantity باید > 0 باشد
- Quantity نمی‌تواند بیشتر از remaining_quantity باشد
- اگر بیشتر باشد، به remaining_quantity adjust می‌شود

### 3. Remaining Quantity Calculation
- `remaining_quantity = quantity_requested - quantity_issued`
- اگر `quantity_issued` وجود نداشته باشد، برابر `quantity_requested` است

### 4. Workflow
1. User warehouse request را انتخاب می‌کند
2. User issue type را انتخاب می‌کند
3. User quantity را review و adjust می‌کند
4. User submit می‌کند
5. Data در session ذخیره می‌شود
6. Redirect به issue creation view
7. Issue creation view از session data استفاده می‌کند

### 5. Logging
- Debug logging برای troubleshooting
- Logs شامل: POST data, warehouse request, quantity, session operations

---

## الگوهای مشترک

1. **Permission Checking**: از `FeaturePermissionRequiredMixin` استفاده می‌کند
2. **Company Filtering**: تمام queries بر اساس `active_company_id` فیلتر می‌شوند
3. **Session Storage**: داده‌ها در session ذخیره می‌شوند برای استفاده در مرحله بعد
4. **Error Handling**: خطاها با messages نمایش داده می‌شوند
