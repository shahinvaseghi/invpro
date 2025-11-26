# qc/views/inspections.py - QC Inspection Views (Complete Documentation)

**هدف**: Views برای مدیریت بازرسی‌های QC (Quality Control) رسیدهای موقت

این فایل شامل **3 کلاس view**:
- `TemporaryReceiptQCListView`: فهرست رسیدهای موقت در انتظار بازرسی
- `TemporaryReceiptQCApproveView`: تایید بازرسی رسید موقت
- `TemporaryReceiptQCRejectView`: رد بازرسی رسید موقت

---

## وابستگی‌ها

- `qc.views.base`: `QCBaseView`
- `inventory.models`: `ReceiptTemporary`
- `shared.mixins`: `FeaturePermissionRequiredMixin`
- `django.views.generic`: `ListView`, `View`
- `django.http`: `HttpResponseRedirect`, `HttpRequest`
- `django.urls`: `reverse`
- `django.shortcuts`: `get_object_or_404`
- `django.utils`: `timezone`
- `django.utils.translation`: `gettext_lazy`
- `django.db`: `transaction`
- `typing`: `Dict`, `Any`

---

## TemporaryReceiptQCListView

**Type**: `FeaturePermissionRequiredMixin, QCBaseView, ListView`

**Template**: `qc/temporary_receipts.html`

**Attributes**:
- `model`: `ReceiptTemporary`
- `template_name`: `'qc/temporary_receipts.html'`
- `context_object_name`: `'receipts'`
- `paginate_by`: `50`
- `feature_code`: `'qc.inspections'`
- `required_action`: `'view'`

**متدها**:

#### `get_queryset() -> QuerySet`

**توضیح**: فیلتر کردن queryset برای نمایش فقط رسیدهای در انتظار بازرسی و قفل نشده.

**مقدار بازگشتی**:
- `QuerySet`: queryset فیلتر شده

**منطق**:
1. فیلتر بر اساس:
   - `status = AWAITING_INSPECTION`
   - `is_locked = 0`
   - `is_enabled = 1`
2. `select_related('supplier', 'created_by')` برای بهینه‌سازی query

**نکات مهم**:
- `ReceiptTemporary` یک header-only model است
- `item` و `warehouse` در `ReceiptTemporaryLine` هستند، نه در `ReceiptTemporary`
- نمی‌توان از `select_related('item', 'warehouse')` استفاده کرد

---

#### `get_context_data(**kwargs) -> Dict[str, Any]`

**توضیح**: اضافه کردن عنوان صفحه به context.

**Context Variables**:
- `receipts`: queryset رسیدها (paginated)
- `page_title`: `_('Temporary Receipts - QC Inspection')`

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با `page_title` اضافه شده

**URL**: `/qc/temporary-receipts/`

---

## TemporaryReceiptQCApproveView

**Type**: `FeaturePermissionRequiredMixin, QCBaseView, View`

**Method**: `POST`

**Attributes**:
- `feature_code`: `'qc.inspections'`
- `required_action`: `'approve'`

**متدها**:

#### `post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponseRedirect`

**توضیح**: تایید یک رسید موقت برای QC.

**Request POST Data**:
- `approval_notes`: یادداشت‌های تایید (optional)

**منطق**:
1. دریافت receipt از `kwargs['pk']`
2. بررسی `company_id`
3. بررسی `is_locked` (نباید قفل شده باشد)
4. بررسی `is_converted` (نباید convert شده باشد)
5. دریافت `approval_notes` از POST
6. در `transaction.atomic()`:
   - تنظیم `qc_approved_by = request.user`
   - تنظیم `qc_approved_at = timezone.now()`
   - تنظیم `qc_approval_notes = approval_notes`
   - تنظیم `status = AWAITING_INSPECTION` (ثابت می‌ماند)
   - تنظیم `is_locked = 1`
   - ذخیره receipt
7. نمایش پیام موفقیت
8. Redirect به `qc:temporary_receipts`

**Error Handling**:
- اگر قفل شده باشد: error message
- اگر convert شده باشد: error message

**نکات مهم**:
- بعد از approve، receipt قفل می‌شود
- Status به `AWAITING_INSPECTION` باقی می‌ماند (برای tracking)
- می‌تواند به permanent receipt تبدیل شود

**URL**: `/qc/temporary-receipts/<pk>/approve/`

---

## TemporaryReceiptQCRejectView

**Type**: `FeaturePermissionRequiredMixin, QCBaseView, View`

**Method**: `POST`

**Attributes**:
- `feature_code`: `'qc.inspections'`
- `required_action`: `'reject'`

**متدها**:

#### `post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponseRedirect`

**توضیح**: رد یک رسید موقت برای QC.

**Request POST Data**:
- `rejection_notes`: یادداشت‌های رد (required)

**منطق**:
1. دریافت receipt از `kwargs['pk']`
2. بررسی `company_id`
3. بررسی `is_locked` (نباید قفل شده باشد)
4. دریافت `rejection_notes` از POST
5. بررسی `rejection_notes` (باید وجود داشته باشد)
6. در `transaction.atomic()`:
   - پاک کردن approval: `qc_approved_by = None`, `qc_approved_at = None`
   - تنظیم `qc_approval_notes = rejection_notes`
   - تنظیم `status = CLOSED` (رد شده)
   - تنظیم `is_locked = 1`
   - ذخیره receipt
7. نمایش پیام موفقیت
8. Redirect به `qc:temporary_receipts`

**Error Handling**:
- اگر قفل شده باشد: error message
- اگر `rejection_notes` خالی باشد: error message

**نکات مهم**:
- `rejection_notes` الزامی است
- بعد از reject، receipt قفل می‌شود
- Status به `CLOSED` تغییر می‌کند
- نمی‌تواند به permanent receipt تبدیل شود

**URL**: `/qc/temporary-receipts/<pk>/reject/`

---

## نکات مهم

### 1. ReceiptTemporary Model Structure
- `ReceiptTemporary` یک header-only model است
- `item` و `warehouse` در `ReceiptTemporaryLine` هستند
- برای دسترسی به items و warehouses باید از `receipt.lines.all()` استفاده کرد

### 2. Status Workflow
- **AWAITING_INSPECTION**: رسید در انتظار بازرسی است
- **CLOSED**: رسید رد شده است (بعد از reject)
- بعد از approve، status به `AWAITING_INSPECTION` باقی می‌ماند

### 3. Lock Mechanism
- بعد از approve یا reject، receipt قفل می‌شود (`is_locked = 1`)
- قفل شده‌ها در لیست نمایش داده نمی‌شوند

### 4. Conversion
- فقط approved receipts می‌توانند به permanent receipt تبدیل شوند
- Rejected receipts نمی‌توانند convert شوند

### 5. Transaction Safety
- تمام تغییرات در `transaction.atomic()` انجام می‌شوند
- در صورت خطا، تغییرات rollback می‌شوند

### 6. Permission Checking
- از `FeaturePermissionRequiredMixin` استفاده می‌کند
- `feature_code = 'qc.inspections'`
- Actions: `'view'`, `'approve'`, `'reject'`

### 7. Company Filtering
- تمام queries بر اساس `active_company_id` فیلتر می‌شوند
- از `QCBaseView` برای company filtering استفاده می‌شود

---

## الگوهای مشترک

1. **Base Class**: از `QCBaseView` استفاده می‌کنند
2. **Permission Checking**: از `FeaturePermissionRequiredMixin` استفاده می‌کنند
3. **Company Filtering**: به صورت خودکار بر اساس `active_company_id` فیلتر می‌شوند
4. **Transaction Safety**: تمام تغییرات در `transaction.atomic()` انجام می‌شوند
5. **Error Handling**: خطاها با messages نمایش داده می‌شوند
6. **Lock Protection**: بررسی `is_locked` قبل از approve/reject

---

## Workflow

### Approve Flow
1. User رسید را در لیست می‌بیند
2. User approve می‌کند (با optional notes)
3. Receipt approved می‌شود و قفل می‌شود
4. Receipt می‌تواند به permanent receipt تبدیل شود

### Reject Flow
1. User رسید را در لیست می‌بیند
2. User reject می‌کند (با required notes)
3. Receipt rejected می‌شود و قفل می‌شود
4. Receipt نمی‌تواند به permanent receipt تبدیل شود

---

## استفاده در پروژه

این views در URLs ماژول QC ثبت شده‌اند:

```python
# qc/urls.py
path('temporary-receipts/', TemporaryReceiptQCListView.as_view(), name='temporary_receipts'),
path('temporary-receipts/<int:pk>/approve/', TemporaryReceiptQCApproveView.as_view(), name='temporary_receipt_approve'),
path('temporary-receipts/<int:pk>/reject/', TemporaryReceiptQCRejectView.as_view(), name='temporary_receipt_reject'),
```

---

## ارتباط با سایر ماژول‌ها

### Inventory Module
- از `inventory.models.ReceiptTemporary` استفاده می‌کند
- بعد از approve، receipt می‌تواند به `ReceiptPermanent` تبدیل شود
- از `inventory.views.receipts.ReceiptTemporarySendToQCView` برای ارسال به QC استفاده می‌شود

### Shared Module
- از `shared.mixins.FeaturePermissionRequiredMixin` برای permission checking استفاده می‌کند

