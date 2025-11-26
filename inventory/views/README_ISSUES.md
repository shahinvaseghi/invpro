# inventory/views/issues.py - Issue Views

**هدف**: Views برای مدیریت حواله‌ها (Issues) در ماژول inventory

این فایل شامل views برای:
- Permanent Issues (حواله‌های دائم)
- Consumption Issues (حواله‌های مصرف)
- Consignment Issues (حواله‌های امانی)
- Serial Assignment (اختصاص سریال)

---

## Permanent Issue Views

### `IssuePermanentListView`
- **Type**: `InventoryBaseView, ListView`
- **Template**: `inventory/issue_permanent.html`
- **URL**: `/inventory/issues/permanent/`

### `IssuePermanentCreateView`
- **Type**: `LineFormsetMixin, ReceiptFormMixin, CreateView`
- **Form**: `IssuePermanentForm`
- **Formset**: `IssuePermanentLineFormSet`
- **URL**: `/inventory/issues/permanent/create/`

### `IssuePermanentUpdateView`
- **Type**: `LineFormsetMixin, DocumentLockProtectedMixin, ReceiptFormMixin, UpdateView`
- **URL**: `/inventory/issues/permanent/<pk>/edit/`

### `IssuePermanentDeleteView`
- **Type**: `DocumentDeleteViewBase`
- **Feature Code**: `inventory.issues.permanent`
- **URL**: `/inventory/issues/permanent/<pk>/delete/`

### `IssuePermanentLockView`
- **Type**: `DocumentLockView`
- **Model**: `IssuePermanent`
- **Hooks**: `after_lock()` - سریال‌ها را finalize می‌کند
- **URL**: `/inventory/issues/permanent/<pk>/lock/`

---

## Consumption Issue Views

### `IssueConsumptionListView`
- **Type**: `InventoryBaseView, ListView`
- **Template**: `inventory/issue_consumption.html`
- **URL**: `/inventory/issues/consumption/`

### `IssueConsumptionCreateView`
- **Type**: `LineFormsetMixin, ReceiptFormMixin, CreateView`
- **Form**: `IssueConsumptionForm`
- **Formset**: `IssueConsumptionLineFormSet`
- **URL**: `/inventory/issues/consumption/create/`

### `IssueConsumptionUpdateView`
- **Type**: `LineFormsetMixin, DocumentLockProtectedMixin, ReceiptFormMixin, UpdateView`
- **URL**: `/inventory/issues/consumption/<pk>/edit/`

### `IssueConsumptionDeleteView`
- **Type**: `DocumentDeleteViewBase`
- **Feature Code**: `inventory.issues.consumption`
- **URL**: `/inventory/issues/consumption/<pk>/delete/`

### `IssueConsumptionLockView`
- **Type**: `DocumentLockView`
- **Model**: `IssueConsumption`
- **Hooks**: `after_lock()` - سریال‌ها را به `CONSUMED` تغییر می‌دهد
- **URL**: `/inventory/issues/consumption/<pk>/lock/`

---

## Consignment Issue Views

### `IssueConsignmentListView`
- **Type**: `InventoryBaseView, ListView`
- **Template**: `inventory/issue_consignment.html`
- **URL**: `/inventory/issues/consignment/`

### `IssueConsignmentCreateView`
- **Type**: `LineFormsetMixin, ReceiptFormMixin, CreateView`
- **Form**: `IssueConsignmentForm`
- **Formset**: `IssueConsignmentLineFormSet`
- **URL**: `/inventory/issues/consignment/create/`

### `IssueConsignmentUpdateView`
- **Type**: `LineFormsetMixin, DocumentLockProtectedMixin, ReceiptFormMixin, UpdateView`
- **URL**: `/inventory/issues/consignment/<pk>/edit/`

### `IssueConsignmentDeleteView`
- **Type**: `DocumentDeleteViewBase`
- **Feature Code**: `inventory.issues.consignment`
- **URL**: `/inventory/issues/consignment/<pk>/delete/`

### `IssueConsignmentLockView`
- **Type**: `DocumentLockView`
- **Model**: `IssueConsignment`
- **URL**: `/inventory/issues/consignment/<pk>/lock/`

---

## Serial Assignment Views

### `IssueLineSerialAssignmentBaseView`
- **Type**: `FeaturePermissionRequiredMixin, FormView`
- **توضیح**: کلاس پایه برای اختصاص سریال به ردیف حواله

### `IssuePermanentLineSerialAssignmentView`
- **Type**: `IssueLineSerialAssignmentBaseView`
- **URL**: `/inventory/issues/permanent/line/<line_id>/assign-serials/`

### `IssueConsumptionLineSerialAssignmentView`
- **Type**: `IssueLineSerialAssignmentBaseView`
- **URL**: `/inventory/issues/consumption/line/<line_id>/assign-serials/`

### `IssueConsignmentLineSerialAssignmentView`
- **Type**: `IssueLineSerialAssignmentBaseView`
- **URL**: `/inventory/issues/consignment/line/<line_id>/assign-serials/`

---

## نکات مهم

1. **Serial Management**: تمام issue views از serial service برای مدیریت سریال‌ها استفاده می‌کنند
2. **Lock Hooks**: Lock views در `after_lock()` سریال‌ها را finalize می‌کنند
3. **Status Changes**: Consumption issues سریال‌ها را به `CONSUMED` تغییر می‌دهند
4. **Multi-line Support**: تمام views از `LineFormsetMixin` استفاده می‌کنند

