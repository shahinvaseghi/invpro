# inventory/views/create_issue_from_warehouse_request.py - Create Issue from Warehouse Request

**هدف**: Views برای ایجاد حواله از درخواست انبار

این فایل شامل views برای:
- انتخاب نوع حواله (permanent/consumption/consignment)
- ایجاد حواله از درخواست انبار

---

## Views

### `CreateIssueFromWarehouseRequestView`

**توضیح**: صفحه انتخاب نوع حواله برای ایجاد از درخواست انبار

**Type**: `FeaturePermissionRequiredMixin, InventoryBaseView, TemplateView`

**Template**: `inventory/create_issue_from_warehouse_request.html`

**Context Variables**:
- `warehouse_request`: شیء درخواست انبار
- `request_lines`: ردیف‌های درخواست

**URL**: `/inventory/requests/warehouse/<warehouse_request_id>/create-issue/`

---

### `CreatePermanentIssueFromWarehouseRequestView`

**توضیح**: ایجاد حواله دائم از درخواست انبار

**Type**: `CreateIssueFromWarehouseRequestView` (inherits)

**منطق**: داده‌های درخواست را به حواله دائم تبدیل می‌کند

---

### `CreateConsumptionIssueFromWarehouseRequestView`

**توضیح**: ایجاد حواله مصرف از درخواست انبار

**Type**: `CreateIssueFromWarehouseRequestView` (inherits)

**منطق**: داده‌های درخواست را به حواله مصرف تبدیل می‌کند

---

### `CreateConsignmentIssueFromWarehouseRequestView`

**توضیح**: ایجاد حواله امانی از درخواست انبار

**Type**: `CreateIssueFromWarehouseRequestView` (inherits)

**منطق**: داده‌های درخواست را به حواله امانی تبدیل می‌کند

---

## نکات مهم

1. **Approval Required**: درخواست انبار باید تایید شده باشد
2. **Line Conversion**: ردیف‌های درخواست به ردیف‌های حواله تبدیل می‌شوند
3. **Status Update**: درخواست انبار به `FULFILLED` تغییر می‌کند

