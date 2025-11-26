# inventory/views/receipts.py - Receipt Views (Complete Documentation)

**هدف**: Views برای مدیریت رسیدها (Receipts) در ماژول inventory

این فایل شامل **27 کلاس view**:
- **2 Base Classes**: `DocumentDeleteViewBase`, `ReceiptFormMixin`
- **15 Receipt Views**: 5 برای هر نوع (Temporary, Permanent, Consignment)
- **3 Create from Purchase Request Views**: برای هر نوع receipt
- **6 Serial Assignment Views**: 2 base + 4 subclass

---

## وابستگی‌ها

- `inventory.views.base`: `InventoryBaseView`, `DocumentLockProtectedMixin`, `DocumentLockView`, `LineFormsetMixin`
- `inventory.models`: تمام مدل‌های receipt و line
- `inventory.forms`: تمام form و formset classes
- `inventory.services.serials`: `generate_receipt_serials`, `generate_receipt_line_serials`
- `shared.mixins`: `FeaturePermissionRequiredMixin`
- `shared.utils.permissions`: `get_user_feature_permissions`, `has_feature_permission`
- `django.views.generic`: `ListView`, `CreateView`, `UpdateView`, `DeleteView`, `View`
- `django.http`: `HttpResponseRedirect`
- `django.urls`: `reverse`, `reverse_lazy`
- `django.shortcuts`: `get_object_or_404`, `render`
- `django.utils`: `timezone`
- `django.utils.translation`: `gettext_lazy`
- `django.utils.safestring`: `mark_safe`
- `django.core.exceptions`: `PermissionDenied`
- `django.contrib.messages`
- `decimal.Decimal`, `InvalidOperation`
- `json`
- `logging`

---

## Base Classes

### DocumentDeleteViewBase

**Type**: `FeaturePermissionRequiredMixin, DocumentLockProtectedMixin, InventoryBaseView, DeleteView`

**Attributes**:
- `owner_field`: `None` (owner check disabled)
- `success_message`: `_('سند با موفقیت حذف شد.')`

**متدها**:
- `dispatch()`: بررسی permissions (delete_own/delete_other) قبل از delete
- `delete()`: نمایش پیام موفقیت
- `get_context_data()`: اضافه کردن `active_module`

**منطق**:
- Superuser bypass
- بررسی `is_owner` و `can_delete_own` / `can_delete_other`
- `PermissionDenied` اگر permission نداشته باشد

---

### ReceiptFormMixin

**Type**: `InventoryBaseView`

**Attributes**:
- `template_name`: `'inventory/receipt_form.html'`
- `form_title`: `''` (override در subclasses)
- `receipt_variant`: `''` (override در subclasses)
- `list_url_name`: `''` (override در subclasses)
- `lock_url_name`: `''` (override در subclasses)

**متدها**:

#### `get_form_kwargs() -> Dict[str, Any]`
- اضافه کردن `company_id` به form

#### `get_context_data(**kwargs) -> Dict[str, Any]`
**Context Variables**:
- `form_title`, `receipt_variant`, `fieldsets`, `used_fields`, `list_url`, `is_edit`
- `unit_options_json`: JSON map از item_id به allowed units
- `unit_placeholder`: placeholder برای unit field
- `item_types`, `item_categories`, `item_subcategories`: برای فیلتر
- `current_item_type`, `current_category`, `current_subcategory`, `current_item_search`: مقادیر فعلی فیلتر
- `document_instance`, `document_status_display`, `document_is_locked`, `lock_url`

#### `get_fieldsets() -> list`
- باید در subclasses override شود

---

## Temporary Receipt Views

### ReceiptTemporaryListView

**Type**: `InventoryBaseView, ListView`

**Template**: `inventory/receipt_temporary.html`

**Attributes**:
- `model`: `ReceiptTemporary`
- `context_object_name`: `'receipts'`
- `paginate_by`: `50`

**متدها**:
- `get_queryset()`: `prefetch_related('lines__item', 'lines__warehouse')`, `select_related('created_by', 'converted_receipt')`
- `get_context_data()`: اضافه کردن URLs و delete permissions

**URL**: `/inventory/receipts/temporary/`

---

### ReceiptTemporaryCreateView

**Type**: `LineFormsetMixin, ReceiptFormMixin, CreateView`

**Form**: `ReceiptTemporaryForm`

**Formset**: `ReceiptTemporaryLineFormSet`

**Success URL**: `inventory:receipt_temporary`

**Attributes**:
- `form_title`: `_('ایجاد رسید موقت')`
- `receipt_variant`: `'temporary'`

**متدها**:
- `form_valid()`: تنظیم `company_id`, `created_by`, `status = AWAITING_INSPECTION`، ذخیره formset
- `get_fieldsets()`: `[(_('Document Info'), ['expected_receipt_date', 'supplier', 'source_document_type', 'source_document_code', 'qc_approval_notes'])]`

**نکات مهم**:
- Status به `AWAITING_INSPECTION` تنظیم می‌شود (برای QC)
- اگر formset invalid باشد، document حذف می‌شود
- باید حداقل یک valid line وجود داشته باشد

**URL**: `/inventory/receipts/temporary/create/`

---

### ReceiptTemporaryUpdateView

**Type**: `LineFormsetMixin, DocumentLockProtectedMixin, ReceiptFormMixin, UpdateView`

**Form**: `ReceiptTemporaryForm`

**Formset**: `ReceiptTemporaryLineFormSet`

**Success URL**: `inventory:receipt_temporary`

**متدها**:
- `form_valid()`: تنظیم `edited_by`، ذخیره formset
- `get_fieldsets()`: مشابه CreateView

**نکات مهم**:
- از `DocumentLockProtectedMixin` استفاده می‌کند

**URL**: `/inventory/receipts/temporary/<pk>/edit/`

---

### ReceiptTemporaryDeleteView

**Type**: `DocumentDeleteViewBase`

**Template**: `inventory/receipt_temporary_confirm_delete.html`

**Success URL**: `inventory:receipt_temporary`

**Attributes**:
- `feature_code`: `'inventory.receipts.temporary'`
- `required_action`: `'delete_own'`
- `allow_own_scope`: `True`
- `success_message`: `_('رسید موقت با موفقیت حذف شد.')`

**URL**: `/inventory/receipts/temporary/<pk>/delete/`

---

### ReceiptTemporaryLockView

**Type**: `DocumentLockView`

**Attributes**:
- `model`: `ReceiptTemporary`
- `success_url_name`: `'inventory:receipt_temporary'`
- `success_message`: `_('رسید موقت قفل شد و دیگر قابل ویرایش نیست.')`

**URL**: `/inventory/receipts/temporary/<pk>/lock/`

---

### ReceiptTemporarySendToQCView

**Type**: `FeaturePermissionRequiredMixin, InventoryBaseView, View`

**Method**: `POST`

**Attributes**:
- `feature_code`: `'inventory.receipts.temporary'`
- `required_action`: `'edit_own'`
- `allow_own_scope`: `True`

**متدها**:
- `post()`: بررسی lock و conversion، تنظیم `status = AWAITING_INSPECTION`

**نکات مهم**:
- فقط اگر قفل نشده و convert نشده باشد
- اگر قبلاً `AWAITING_INSPECTION` باشد، info message

**URL**: `/inventory/receipts/temporary/<pk>/send-to-qc/`

---

### ReceiptTemporaryCreateFromPurchaseRequestView

**Type**: `ReceiptTemporaryCreateView`

**متدها**:
- `get_purchase_request()`: دریافت purchase request از URL
- `get_context_data()`: دریافت selected lines از session، populate formset با initial data
- `form_valid()`: ذخیره receipt، به‌روزرسانی `quantity_fulfilled` در purchase request lines، پاک کردن session

**Session Key**: `purchase_request_{pk}_receipt_temporary_lines`

**نکات مهم**:
- از session برای انتقال selected lines استفاده می‌کند
- `quantity_fulfilled` در purchase request lines به‌روزرسانی می‌شود
- Session بعد از successful creation پاک می‌شود

**URL**: `/inventory/receipts/temporary/create-from-purchase-request/<pk>/`

---

## Permanent Receipt Views

### ReceiptPermanentListView

**Type**: `InventoryBaseView, ListView`

**Template**: `inventory/receipt_permanent.html`

**Attributes**:
- `model`: `ReceiptPermanent`
- `context_object_name`: `'receipts'`
- `paginate_by`: `50`

**متدها**:
- `get_queryset()`: `prefetch_related('lines__item', 'lines__warehouse', 'lines__supplier')`, `select_related('created_by', 'temporary_receipt', 'purchase_request')`
- `get_context_data()`: اضافه کردن URLs و delete permissions

**URL**: `/inventory/receipts/permanent/`

---

### ReceiptPermanentCreateView

**Type**: `LineFormsetMixin, ReceiptFormMixin, CreateView`

**Form**: `ReceiptPermanentForm`

**Formset**: `ReceiptPermanentLineFormSet`

**Success URL**: `inventory:receipt_permanent`

**Attributes**:
- `form_title`: `_('ایجاد رسید دائم')`
- `receipt_variant`: `'permanent'`

**متدها**:
- `form_valid()`: تنظیم `company_id`, `created_by`، ذخیره formset
- `get_fieldsets()`: `[(_('Document Info'), ['document_code', 'document_date', 'requires_temporary_receipt', 'temporary_receipt', 'purchase_request', 'warehouse_request'])]`

**URL**: `/inventory/receipts/permanent/create/`

---

### ReceiptPermanentUpdateView

**Type**: `LineFormsetMixin, DocumentLockProtectedMixin, ReceiptFormMixin, UpdateView`

**Form**: `ReceiptPermanentForm`

**Formset**: `ReceiptPermanentLineFormSet`

**Success URL**: `inventory:receipt_permanent`

**متدها**: مشابه `ReceiptTemporaryUpdateView`

**URL**: `/inventory/receipts/permanent/<pk>/edit/`

---

### ReceiptPermanentDeleteView

**Type**: `DocumentDeleteViewBase`

**Template**: `inventory/receipt_permanent_confirm_delete.html`

**Success URL**: `inventory:receipt_permanent`

**Attributes**:
- `feature_code`: `'inventory.receipts.permanent'`
- `required_action`: `'delete_own'`
- `allow_own_scope`: `True`
- `success_message`: `_('رسید دائم با موفقیت حذف شد.')`

**URL**: `/inventory/receipts/permanent/<pk>/delete/`

---

### ReceiptPermanentLockView

**Type**: `DocumentLockView`

**Attributes**:
- `model`: `ReceiptPermanent`
- `success_url_name`: `'inventory:receipt_permanent'`
- `success_message`: `_('رسید دائم قفل شد و دیگر قابل ویرایش نیست.')`

**Hooks**:
- `after_lock()`: تولید سریال‌ها برای lines (اگر نیاز باشد)

**URL**: `/inventory/receipts/permanent/<pk>/lock/`

---

### ReceiptPermanentCreateFromPurchaseRequestView

**Type**: `ReceiptPermanentCreateView`

**متدها**: مشابه `ReceiptTemporaryCreateFromPurchaseRequestView`

**Session Key**: `purchase_request_{pk}_receipt_permanent_lines`

**URL**: `/inventory/receipts/permanent/create-from-purchase-request/<pk>/`

---

## Consignment Receipt Views

### ReceiptConsignmentListView

**Type**: `InventoryBaseView, ListView`

**Template**: `inventory/receipt_consignment.html`

**Attributes**:
- `model`: `ReceiptConsignment`
- `context_object_name`: `'receipts'`
- `paginate_by`: `50`

**متدها**: مشابه `ReceiptPermanentListView`

**URL**: `/inventory/receipts/consignment/`

---

### ReceiptConsignmentCreateView

**Type**: `LineFormsetMixin, ReceiptFormMixin, CreateView`

**Form**: `ReceiptConsignmentForm`

**Formset**: `ReceiptConsignmentLineFormSet`

**Success URL**: `inventory:receipt_consignment`

**Attributes**:
- `form_title`: `_('ایجاد رسید امانی')`
- `receipt_variant`: `'consignment'`

**متدها**: مشابه `ReceiptPermanentCreateView`

**URL**: `/inventory/receipts/consignment/create/`

---

### ReceiptConsignmentUpdateView

**Type**: `LineFormsetMixin, DocumentLockProtectedMixin, ReceiptFormMixin, UpdateView`

**Form**: `ReceiptConsignmentForm`

**Formset**: `ReceiptConsignmentLineFormSet`

**Success URL**: `inventory:receipt_consignment`

**متدها**: مشابه `ReceiptPermanentUpdateView`

**Fieldsets**: شامل fields بیشتر (consignment_contract_code, expected_return_date, valuation_method, ownership_status, conversion_receipt, conversion_date, return_document_id)

**URL**: `/inventory/receipts/consignment/<pk>/edit/`

---

### ReceiptConsignmentDeleteView

**Type**: `DocumentDeleteViewBase`

**Template**: `inventory/receipt_consignment_confirm_delete.html`

**Success URL**: `inventory:receipt_consignment`

**Attributes**:
- `feature_code`: `'inventory.receipts.consignment'`
- `required_action`: `'delete_own'`
- `allow_own_scope`: `True`
- `success_message`: `_('رسید امانی با موفقیت حذف شد.')`

**URL**: `/inventory/receipts/consignment/<pk>/delete/`

---

### ReceiptConsignmentLockView

**Type**: `DocumentLockView`

**Attributes**:
- `model`: `ReceiptConsignment`
- `success_url_name`: `'inventory:receipt_consignment'`
- `success_message`: `_('رسید امانی قفل شد و دیگر قابل ویرایش نیست.')`

**URL**: `/inventory/receipts/consignment/<pk>/lock/`

---

### ReceiptConsignmentCreateFromPurchaseRequestView

**Type**: `ReceiptConsignmentCreateView`

**متدها**: مشابه `ReceiptPermanentCreateFromPurchaseRequestView`

**Session Key**: `purchase_request_{pk}_receipt_consignment_lines`

**نکات مهم**:
- Supplier از `SupplierItem` resolve می‌شود

**URL**: `/inventory/receipts/consignment/create-from-purchase-request/<pk>/`

---

## Serial Assignment Views

### ReceiptSerialAssignmentBaseView (Legacy)

**Type**: `FeaturePermissionRequiredMixin, View`

**Template**: `inventory/receipt_serial_assignment.html`

**Attributes**:
- `model`: `None` (باید در subclass تنظیم شود)
- `feature_code`: `None` (باید در subclass تنظیم شود)
- `serial_url_name`, `list_url_name`, `edit_url_name`, `lock_url_name`: باید در subclass تنظیم شوند

**متدها**:
- `dispatch()`: بررسی `has_lot_tracking`
- `get_receipt()`: دریافت receipt object
- `get_required_serials()`: محاسبه تعداد required serials
- `get_context_data()`: context برای serial assignment page
- `get()`: نمایش صفحه
- `post()`: تولید serials با `generate_receipt_serials()`

**نکات مهم**:
- Legacy support برای single-line receipts
- Serial tracking فقط برای `has_lot_tracking=1`

---

### ReceiptPermanentSerialAssignmentView

**Type**: `ReceiptSerialAssignmentBaseView`

**Attributes**:
- `model`: `ReceiptPermanent`
- `feature_code`: `'inventory.receipts.permanent'`

**URL**: `/inventory/receipts/permanent/<pk>/serials/`

---

### ReceiptConsignmentSerialAssignmentView

**Type**: `ReceiptSerialAssignmentBaseView`

**Attributes**:
- `model`: `ReceiptConsignment`
- `feature_code`: `'inventory.receipts.consignment'`

**URL**: `/inventory/receipts/consignment/<pk>/serials/`

---

### ReceiptLineSerialAssignmentBaseView (Multi-line)

**Type**: `FeaturePermissionRequiredMixin, View`

**Template**: `inventory/receipt_serial_assignment.html`

**Attributes**:
- `line_model`: `None` (باید در subclass تنظیم شود)
- `document_model`: `None` (باید در subclass تنظیم شود)
- `feature_code`: `None` (باید در subclass تنظیم شود)
- `serial_url_name`, `list_url_name`, `edit_url_name`, `lock_url_name`: باید در subclass تنظیم شوند

**متدها**:
- `dispatch()`: بررسی `has_lot_tracking`
- `get_document()`: دریافت document object
- `get_line()`: دریافت line object
- `get_required_serials()`: محاسبه تعداد required serials
- `get_context_data()`: context برای serial assignment page
- `get()`: نمایش صفحه
- `post()`: تولید serials با `generate_receipt_line_serials()`

**نکات مهم**:
- Multi-line support
- Serial tracking per line

---

### ReceiptPermanentLineSerialAssignmentView

**Type**: `ReceiptLineSerialAssignmentBaseView`

**Attributes**:
- `line_model`: `ReceiptPermanentLine`
- `document_model`: `ReceiptPermanent`
- `feature_code`: `'inventory.receipts.permanent'`

**URL**: `/inventory/receipts/permanent/<pk>/line/<line_id>/serials/`

---

### ReceiptConsignmentLineSerialAssignmentView

**Type**: `ReceiptLineSerialAssignmentBaseView`

**Attributes**:
- `line_model`: `ReceiptConsignmentLine`
- `document_model`: `ReceiptConsignment`
- `feature_code`: `'inventory.receipts.consignment'`

**URL**: `/inventory/receipts/consignment/<pk>/line/<line_id>/serials/`

---

## نکات مهم

### 1. Multi-line Support
- تمام receipt views از `LineFormsetMixin` استفاده می‌کنند
- باید حداقل یک valid line وجود داشته باشد

### 2. Lock Mechanism
- Update/Delete views از `DocumentLockProtectedMixin` استفاده می‌کنند
- Lock views از `DocumentLockView` استفاده می‌کنند

### 3. Permission Checking
- Delete views مجوزهای `delete_own`/`delete_other` را بررسی می‌کنند
- Superuser bypass

### 4. Purchase Request Integration
- Views برای ایجاد receipt از purchase request موجود هستند
- از session برای انتقال selected lines استفاده می‌کنند
- `quantity_fulfilled` در purchase request lines به‌روزرسانی می‌شود

### 5. Serial Management
- Legacy views برای single-line receipts
- Line views برای multi-line receipts
- Serial tracking فقط برای `has_lot_tracking=1`

### 6. Item Filtering and Search
- تمام receipt forms از فیلتر و جستجو پشتیبانی می‌کنند
- فیلترها: `item_type`, `category`, `subcategory`
- جستجو: `item_search` (در name و item_code)

### 7. QC Integration
- Temporary receipts به `AWAITING_INSPECTION` تنظیم می‌شوند
- `ReceiptTemporarySendToQCView` برای ارسال به QC

---

## الگوهای مشترک

1. **Company Filtering**: تمام queryset ها بر اساس `active_company_id` فیلتر می‌شوند
2. **Formset Management**: از `LineFormsetMixin` برای مدیریت formsets استفاده می‌شود
3. **Error Handling**: خطاها با messages نمایش داده می‌شوند
4. **Session Management**: از session برای انتقال data استفاده می‌شود
