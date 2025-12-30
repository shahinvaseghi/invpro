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

- `inventory.views.base`: `BaseCreateDocumentFromRequestView`, `InventoryBaseView`
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

**Inheritance**: `BaseCreateDocumentFromRequestView`

**Type**: `FeaturePermissionRequiredMixin, InventoryBaseView, TemplateView`

**Template**: `inventory/create_issue_from_warehouse_request.html`

**Attributes** (از BaseCreateDocumentFromRequestView):
- `document_type`: `'issue'`
- `document_subtype`: باید در subclass تنظیم شود (`'permanent'`, `'consumption'`, `'consignment'`)
- `request_model`: `models.WarehouseRequest`
- `is_multi_line`: `False` (WarehouseRequest تک خط است)
- `template_name`: `'inventory/create_issue_from_warehouse_request.html'`
- `required_action`: `'create_issue_from_warehouse_request'`

**نکته مهم**: این view از `BaseCreateDocumentFromRequestView` استفاده می‌کند که تمام منطق دریافت request، پردازش POST، و redirect را handle می‌کند. فقط `get_context_data()` override شده است.

**متدها**:

#### `get_context_data(self, **kwargs: Dict[str, Any]) -> Dict[str, Any]`

**توضیح**: Override از `BaseCreateDocumentFromRequestView.get_context_data()` برای اضافه کردن متغیرهای context برای backward compatibility با templates.

**Context Variables** (از base class):
- `warehouse_request`: warehouse request object
- `issue_type`: نوع issue (از `document_subtype`)
- `issue_type_name`: نام فارسی نوع issue (از `get_type_name()`)
- `remaining_quantity`: مقدار باقیمانده (quantity_requested - quantity_issued)
- `default_quantity`: مقدار پیش‌فرض (برابر remaining_quantity)

**منطق**:
1. فراخوانی `super().get_context_data(**kwargs)` که تمام منطق base class را اجرا می‌کند
2. اضافه کردن `issue_type` و `issue_type_name` برای backward compatibility با templates قدیمی

**نکات مهم**:
- منطق اصلی در `BaseCreateDocumentFromRequestView` است
- `get_request_object()` از base class استفاده می‌کند که request را با فیلتر `request_status='approved'` دریافت می‌کند
- `post()` از base class استفاده می‌کند که `process_single_line_post()` را فراخوانی می‌کند
- Session key: `warehouse_request_{pk}_issue_{document_subtype}_data`
- Redirect URLs از `get_redirect_url()` در base class استفاده می‌کنند

---

## CreatePermanentIssueFromWarehouseRequestView

**Inheritance**: `CreateIssueFromWarehouseRequestView`

**Attributes**:
- `document_subtype`: `'permanent'`
- `feature_code`: `'inventory.issues.permanent'`

**توضیحات**: Subclass برای permanent issue. فقط `document_subtype` و `feature_code` را تنظیم می‌کند.

---

## CreateConsumptionIssueFromWarehouseRequestView

**Inheritance**: `CreateIssueFromWarehouseRequestView`

**Attributes**:
- `document_subtype`: `'consumption'`
- `feature_code`: `'inventory.issues.consumption'`

**توضیحات**: Subclass برای consumption issue. فقط `document_subtype` و `feature_code` را تنظیم می‌کند.

---

## CreateConsignmentIssueFromWarehouseRequestView

**Inheritance**: `CreateIssueFromWarehouseRequestView`

**Attributes**:
- `document_subtype`: `'consignment'`
- `feature_code`: `'inventory.issues.consignment'`

**توضیحات**: Subclass برای consignment issue. فقط `document_subtype` و `feature_code` را تنظیم می‌کند.

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
2. User issue type را انتخاب می‌کند (permanent/consumption/consignment)
3. `BaseCreateDocumentFromRequestView.get_context_data()` فرم را نمایش می‌دهد
4. User quantity را review و adjust می‌کند
5. User submit می‌کند
6. `BaseCreateDocumentFromRequestView.post()` فراخوانی می‌شود
7. `process_single_line_post()` quantity را پردازش می‌کند
8. Data در session ذخیره می‌شود (key: `warehouse_request_{pk}_issue_{subtype}_data`)
9. Redirect به issue creation view (از `get_redirect_url()`)
10. Issue creation view از session data استفاده می‌کند

### 5. Logging
- Debug logging برای troubleshooting
- Logs شامل: POST data, warehouse request, quantity, session operations

---

## الگوهای مشترک

1. **Permission Checking**: از `FeaturePermissionRequiredMixin` استفاده می‌کند
2. **Company Filtering**: تمام queries بر اساس `active_company_id` فیلتر می‌شوند
3. **Session Storage**: داده‌ها در session ذخیره می‌شوند برای استفاده در مرحله بعد
4. **Error Handling**: خطاها با messages نمایش داده می‌شوند
