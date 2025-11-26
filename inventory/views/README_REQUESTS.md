# inventory/views/requests.py - Request Views

**هدف**: Views برای مدیریت درخواست‌ها (Requests) در ماژول inventory

این فایل شامل views برای:
- Purchase Requests (درخواست‌های خرید)
- Warehouse Requests (درخواست‌های انبار)
- Receipt Creation from Purchase Requests

---

## Purchase Request Views

### `PurchaseRequestListView`
- **Type**: `InventoryBaseView, ListView`
- **Template**: `inventory/purchase_request.html`
- **URL**: `/inventory/requests/purchase/`

### `PurchaseRequestCreateView`
- **Type**: `LineFormsetMixin, PurchaseRequestFormMixin, CreateView`
- **Form**: `PurchaseRequestForm`
- **Formset**: `PurchaseRequestLineFormSet`
- **URL**: `/inventory/requests/purchase/create/`

### `PurchaseRequestUpdateView`
- **Type**: `LineFormsetMixin, PurchaseRequestFormMixin, UpdateView`
- **URL**: `/inventory/requests/purchase/<pk>/edit/`

### `PurchaseRequestApproveView`
- **Type**: `InventoryBaseView, View`
- **منطق**: درخواست را تایید می‌کند (`status = APPROVED`)
- **URL**: `/inventory/requests/purchase/<pk>/approve/`

---

## Warehouse Request Views

### `WarehouseRequestListView`
- **Type**: `InventoryBaseView, ListView`
- **Template**: `inventory/warehouse_request.html`
- **URL**: `/inventory/requests/warehouse/`

### `WarehouseRequestCreateView`
- **Type**: `WarehouseRequestFormMixin, CreateView`
- **Form**: `WarehouseRequestForm`
- **URL**: `/inventory/requests/warehouse/create/`

### `WarehouseRequestUpdateView`
- **Type**: `WarehouseRequestFormMixin, UpdateView`
- **URL**: `/inventory/requests/warehouse/<pk>/edit/`

### `WarehouseRequestApproveView`
- **Type**: `InventoryBaseView, View`
- **منطق**: درخواست را تایید می‌کند
- **URL**: `/inventory/requests/warehouse/<pk>/approve/`

---

## Receipt Creation Views

### `CreateReceiptFromPurchaseRequestView`
- **Type**: `FeaturePermissionRequiredMixin, InventoryBaseView, TemplateView`
- **Template**: `inventory/create_receipt_from_purchase_request.html`
- **منطق**: صفحه انتخاب نوع رسید (temporary/permanent/consignment)
- **URL**: `/inventory/requests/purchase/<purchase_request_id>/create-receipt/`

### `CreateTemporaryReceiptFromPurchaseRequestView`
- **Type**: `CreateReceiptFromPurchaseRequestView` (inherits)
- **منطق**: ایجاد رسید موقت از درخواست خرید

### `CreatePermanentReceiptFromPurchaseRequestView`
- **Type**: `CreateReceiptFromPurchaseRequestView` (inherits)
- **منطق**: ایجاد رسید دائم از درخواست خرید

### `CreateConsignmentReceiptFromPurchaseRequestView`
- **Type**: `CreateReceiptFromPurchaseRequestView` (inherits)
- **منطق**: ایجاد رسید امانی از درخواست خرید

---

## نکات مهم

1. **Approval Workflow**: درخواست‌ها باید تایید شوند قبل از تبدیل به رسید
2. **Line Conversion**: ردیف‌های درخواست خرید به ردیف‌های رسید تبدیل می‌شوند
3. **Status Management**: درخواست‌ها می‌توانند `DRAFT` یا `APPROVED` باشند

