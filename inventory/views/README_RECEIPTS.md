# inventory/views/receipts.py - Receipt Views

**هدف**: Views برای مدیریت رسیدها (Receipts) در ماژول inventory

این فایل شامل views برای:
- Temporary Receipts (رسیدهای موقت)
- Permanent Receipts (رسیدهای دائم)
- Consignment Receipts (رسیدهای امانی)
- Serial Assignment (اختصاص سریال)

---

## Base Classes

### `DocumentDeleteViewBase`

**توضیح**: کلاس پایه برای delete views با بررسی مجوز.

**Type**: `FeaturePermissionRequiredMixin, DocumentLockProtectedMixin, InventoryBaseView, DeleteView`

**Features**:
- بررسی مجوز delete (own/other)
- بررسی قفل بودن سند
- پیام موفقیت

**متدها**:
- `dispatch(request, *args, **kwargs)`: بررسی مجوز قبل از حذف
- `delete(request, *args, **kwargs)`: نمایش پیام موفقیت

---

### `ReceiptFormMixin`

**توضیح**: Helper mixin مشترک برای receipt create/update views.

**Type**: `InventoryBaseView`

**Attributes**:
- `template_name`: نام template
- `form_title`: عنوان فرم
- `receipt_variant`: نوع رسید ('temporary', 'permanent', 'consignment')
- `list_url_name`: نام URL لیست
- `lock_url_name`: نام URL قفل

**متدها**:
- `get_form_kwargs()`: `company_id` را به form پاس می‌دهد
- `get_context_data(**kwargs)`: context کامل را آماده می‌کند (fieldsets, unit options, lock status)
- `get_fieldsets()`: پیکربندی fieldsets را برمی‌گرداند

---

## Temporary Receipt Views

### `ReceiptTemporaryListView`

**توضیح**: فهرست رسیدهای موقت

**Type**: `InventoryBaseView, ListView`

**Template**: `inventory/receipt_temporary.html`

**Context Variables**:
- `receipts`: queryset رسیدها (paginated)
- `create_url`: URL ایجاد
- `show_qc`: نمایش دکمه QC
- `show_conversion`: نمایش لینک تبدیل

**URL**: `/inventory/receipts/temporary/`

---

### `ReceiptTemporaryCreateView`

**توضیح**: ایجاد رسید موقت جدید

**Type**: `LineFormsetMixin, ReceiptFormMixin, CreateView`

**Template**: `inventory/receipt_form.html`

**Form**: `ReceiptTemporaryForm`

**Formset**: `ReceiptTemporaryLineFormSet`

**Success URL**: `inventory:receipt_temporary`

**متدها**:
- `form_valid(form)`: 
  - `company_id` و `created_by` را تنظیم می‌کند
  - line formset را ذخیره می‌کند

**URL**: `/inventory/receipts/temporary/create/`

---

### `ReceiptTemporaryUpdateView`

**توضیح**: ویرایش رسید موقت

**Type**: `LineFormsetMixin, DocumentLockProtectedMixin, ReceiptFormMixin, UpdateView`

**Template**: `inventory/receipt_form.html`

**Form**: `ReceiptTemporaryForm`

**Formset**: `ReceiptTemporaryLineFormSet`

**Success URL**: `inventory:receipt_temporary`

**متدها**:
- `form_valid(form)`: 
  - `edited_by` را تنظیم می‌کند
  - line formset را ذخیره می‌کند

**URL**: `/inventory/receipts/temporary/<pk>/edit/`

---

### `ReceiptTemporaryDeleteView`

**توضیح**: حذف رسید موقت

**Type**: `DocumentDeleteViewBase`

**Template**: `inventory/receipt_confirm_delete.html`

**Success URL**: `inventory:receipt_temporary`

**Feature Code**: `inventory.receipts.temporary`

**URL**: `/inventory/receipts/temporary/<pk>/delete/`

---

### `ReceiptTemporaryLockView`

**توضیح**: قفل کردن رسید موقت

**Type**: `DocumentLockView`

**Model**: `ReceiptTemporary`

**Success URL**: `inventory:receipt_temporary`

**URL**: `/inventory/receipts/temporary/<pk>/lock/`

---

### `ReceiptTemporarySendToQCView`

**توضیح**: ارسال رسید موقت به QC

**Type**: `FeaturePermissionRequiredMixin, InventoryBaseView, View`

**Feature Code**: `inventory.receipts.temporary`

**منطق**:
- وضعیت رسید را به `AWAITING_INSPECTION` تغییر می‌دهد
- یک رکورد `ReceiptInspection` ایجاد می‌کند

**URL**: `/inventory/receipts/temporary/<pk>/send-to-qc/`

---

### `ReceiptTemporaryCreateFromPurchaseRequestView`

**توضیح**: ایجاد رسید موقت از درخواست خرید

**Type**: `ReceiptTemporaryCreateView` (inherits)

**منطق**:
- داده‌های درخواست خرید را auto-fill می‌کند
- ردیف‌های درخواست را به ردیف‌های رسید تبدیل می‌کند

**URL**: `/inventory/receipts/temporary/create-from-purchase-request/<purchase_request_id>/`

---

## Permanent Receipt Views

### `ReceiptPermanentListView`

**توضیح**: فهرست رسیدهای دائم

**Type**: `InventoryBaseView, ListView`

**Template**: `inventory/receipt_permanent.html`

**Context Variables**:
- `receipts`: queryset رسیدها (paginated)

**URL**: `/inventory/receipts/permanent/`

---

### `ReceiptPermanentCreateView`

**توضیح**: ایجاد رسید دائم جدید

**Type**: `LineFormsetMixin, ReceiptFormMixin, CreateView`

**Template**: `inventory/receipt_form.html`

**Form**: `ReceiptPermanentForm`

**Formset**: `ReceiptPermanentLineFormSet`

**Success URL**: `inventory:receipt_permanent`

**متدها**:
- `form_valid(form)`: 
  - `company_id` و `created_by` را تنظیم می‌کند
  - line formset را ذخیره می‌کند

**URL**: `/inventory/receipts/permanent/create/`

---

### `ReceiptPermanentUpdateView`

**توضیح**: ویرایش رسید دائم

**Type**: `LineFormsetMixin, DocumentLockProtectedMixin, ReceiptFormMixin, UpdateView`

**Template**: `inventory/receipt_form.html`

**Form**: `ReceiptPermanentForm`

**Formset**: `ReceiptPermanentLineFormSet`

**Success URL**: `inventory:receipt_permanent`

**URL**: `/inventory/receipts/permanent/<pk>/edit/`

---

### `ReceiptPermanentDeleteView`

**توضیح**: حذف رسید دائم

**Type**: `DocumentDeleteViewBase`

**Template**: `inventory/receipt_confirm_delete.html`

**Success URL**: `inventory:receipt_permanent`

**Feature Code**: `inventory.receipts.permanent`

**URL**: `/inventory/receipts/permanent/<pk>/delete/`

---

### `ReceiptPermanentLockView`

**توضیح**: قفل کردن رسید دائم

**Type**: `DocumentLockView`

**Model**: `ReceiptPermanent`

**Success URL**: `inventory:receipt_permanent`

**Hooks**:
- `after_lock()`: سریال‌ها را برای ردیف‌ها تولید می‌کند

**URL**: `/inventory/receipts/permanent/<pk>/lock/`

---

### `ReceiptPermanentCreateFromPurchaseRequestView`

**توضیح**: ایجاد رسید دائم از درخواست خرید

**Type**: `ReceiptPermanentCreateView` (inherits)

**URL**: `/inventory/receipts/permanent/create-from-purchase-request/<purchase_request_id>/`

---

## Consignment Receipt Views

### `ReceiptConsignmentListView`

**توضیح**: فهرست رسیدهای امانی

**Type**: `InventoryBaseView, ListView`

**Template**: `inventory/receipt_consignment.html`

**URL**: `/inventory/receipts/consignment/`

---

### `ReceiptConsignmentCreateView`

**توضیح**: ایجاد رسید امانی جدید

**Type**: `LineFormsetMixin, ReceiptFormMixin, CreateView`

**Template**: `inventory/receipt_form.html`

**Form**: `ReceiptConsignmentForm`

**Formset**: `ReceiptConsignmentLineFormSet`

**URL**: `/inventory/receipts/consignment/create/`

---

### `ReceiptConsignmentUpdateView`

**توضیح**: ویرایش رسید امانی

**Type**: `LineFormsetMixin, DocumentLockProtectedMixin, ReceiptFormMixin, UpdateView`

**URL**: `/inventory/receipts/consignment/<pk>/edit/`

---

### `ReceiptConsignmentDeleteView`

**توضیح**: حذف رسید امانی

**Type**: `DocumentDeleteViewBase`

**Feature Code**: `inventory.receipts.consignment`

**URL**: `/inventory/receipts/consignment/<pk>/delete/`

---

### `ReceiptConsignmentLockView`

**توضیح**: قفل کردن رسید امانی

**Type**: `DocumentLockView`

**Model**: `ReceiptConsignment`

**URL**: `/inventory/receipts/consignment/<pk>/lock/`

---

### `ReceiptConsignmentCreateFromPurchaseRequestView`

**توضیح**: ایجاد رسید امانی از درخواست خرید

**Type**: `ReceiptConsignmentCreateView` (inherits)

**URL**: `/inventory/receipts/consignment/create-from-purchase-request/<purchase_request_id>/`

---

## Serial Assignment Views

### `ReceiptSerialAssignmentBaseView`

**توضیح**: کلاس پایه برای اختصاص سریال به رسید (single-item receipts - قدیمی)

**Type**: `FeaturePermissionRequiredMixin, View`

**متدها**:
- `get(request, *args, **kwargs)`: صفحه اختصاص سریال را نمایش می‌دهد
- `post(request, *args, **kwargs)`: سریال‌های انتخاب شده را ذخیره می‌کند

---

### `ReceiptPermanentSerialAssignmentView`

**توضیح**: اختصاص سریال به رسید دائم (single-item)

**Type**: `ReceiptSerialAssignmentBaseView`

**URL**: `/inventory/receipts/permanent/<pk>/assign-serials/`

---

### `ReceiptConsignmentSerialAssignmentView`

**توضیح**: اختصاص سریال به رسید امانی (single-item)

**Type**: `ReceiptSerialAssignmentBaseView`

**URL**: `/inventory/receipts/consignment/<pk>/assign-serials/`

---

### `ReceiptLineSerialAssignmentBaseView`

**توضیح**: کلاس پایه برای اختصاص سریال به ردیف رسید (multi-line receipts - جدید)

**Type**: `FeaturePermissionRequiredMixin, View`

**متدها**:
- `get(request, *args, **kwargs)`: صفحه اختصاص سریال را نمایش می‌دهد
- `post(request, *args, **kwargs)`: سریال‌های انتخاب شده را به ردیف اختصاص می‌دهد

---

### `ReceiptPermanentLineSerialAssignmentView`

**توضیح**: اختصاص سریال به ردیف رسید دائم

**Type**: `ReceiptLineSerialAssignmentBaseView`

**URL**: `/inventory/receipts/permanent/line/<line_id>/assign-serials/`

---

### `ReceiptConsignmentLineSerialAssignmentView`

**توضیح**: اختصاص سریال به ردیف رسید امانی

**Type**: `ReceiptLineSerialAssignmentBaseView`

**URL**: `/inventory/receipts/consignment/line/<line_id>/assign-serials/`

---

## وابستگی‌ها

- `inventory.views.base`: `InventoryBaseView`, `DocumentLockProtectedMixin`, `DocumentLockView`, `LineFormsetMixin`
- `shared.mixins`: `FeaturePermissionRequiredMixin`
- `inventory.models`: تمام مدل‌های receipt
- `inventory.forms`: تمام form و formset classes
- `inventory.services.serials`: برای مدیریت سریال‌ها

---

## استفاده در پروژه

این views در URLs ماژول inventory ثبت شده‌اند و از طریق sidebar navigation قابل دسترسی هستند.

---

## نکات مهم

1. **Multi-line Support**: تمام receipt views از `LineFormsetMixin` برای پشتیبانی multi-line استفاده می‌کنند
2. **Serial Management**: Serial assignment views برای کالاهای قابل ردیابی (`has_lot_tracking=1`) استفاده می‌شوند
3. **Lock Protection**: Update/Delete views از `DocumentLockProtectedMixin` استفاده می‌کنند
4. **Permission Checking**: Delete views مجوزهای delete_own/delete_other را بررسی می‌کنند
5. **Purchase Request Integration**: Views برای ایجاد رسید از درخواست خرید موجود هستند

