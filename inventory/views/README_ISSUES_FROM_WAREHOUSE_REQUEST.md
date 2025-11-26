# inventory/views/issues_from_warehouse_request.py - Issue Creation from Warehouse Request

**هدف**: Views برای ایجاد مستقیم حواله از درخواست انبار (بدون صفحه انتخاب)

این فایل شامل views برای:
- ایجاد مستقیم حواله دائم از درخواست انبار
- ایجاد مستقیم حواله مصرف از درخواست انبار
- ایجاد مستقیم حواله امانی از درخواست انبار

---

## Views

### `IssuePermanentCreateFromWarehouseRequestView`

**توضیح**: ایجاد مستقیم حواله دائم از درخواست انبار

**Type**: `FeaturePermissionRequiredMixin, LineFormsetMixin, ReceiptFormMixin, CreateView`

**Form**: `IssuePermanentForm`

**Formset**: `IssuePermanentLineFormSet`

**منطق**:
1. درخواست انبار را می‌خواند
2. فرم را با داده‌های درخواست pre-fill می‌کند
3. ردیف‌های درخواست را به ردیف‌های حواله تبدیل می‌کند
4. حواله را ایجاد می‌کند

**URL**: `/inventory/issues/permanent/create-from-warehouse-request/<warehouse_request_id>/`

---

### `IssueConsumptionCreateFromWarehouseRequestView`

**توضیح**: ایجاد مستقیم حواله مصرف از درخواست انبار

**Type**: `FeaturePermissionRequiredMixin, LineFormsetMixin, ReceiptFormMixin, CreateView`

**Form**: `IssueConsumptionForm`

**Formset**: `IssueConsumptionLineFormSet`

**URL**: `/inventory/issues/consumption/create-from-warehouse-request/<warehouse_request_id>/`

---

### `IssueConsignmentCreateFromWarehouseRequestView`

**توضیح**: ایجاد مستقیم حواله امانی از درخواست انبار

**Type**: `FeaturePermissionRequiredMixin, LineFormsetMixin, ReceiptFormMixin, CreateView`

**Form**: `IssueConsignmentForm`

**Formset**: `IssueConsignmentLineFormSet`

**URL**: `/inventory/issues/consignment/create-from-warehouse-request/<warehouse_request_id>/`

---

## نکات مهم

1. **Direct Creation**: این views حواله را مستقیماً ایجاد می‌کنند (بدون صفحه انتخاب)
2. **Auto-fill**: فرم‌ها به صورت خودکار با داده‌های درخواست پر می‌شوند
3. **Line Mapping**: ردیف‌های درخواست به ردیف‌های حواله map می‌شوند

