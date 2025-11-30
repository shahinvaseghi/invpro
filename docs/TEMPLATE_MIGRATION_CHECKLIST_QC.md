# چک‌لیست Migration Templates ماژول QC

این فایل شامل لیست template های ماژول QC است که باید به generic templates migrate شوند.

---

## فاز 1: List Templates

### ✅ Temporary Receipts QC List
- [x] `TemporaryReceiptQCListView` → `shared/generic/generic_list.html`
  - Template: `qc/temporary_receipts.html` (extends `shared/generic/generic_list.html`)
  - View: `qc/views/inspections.py:TemporaryReceiptQCListView`
  - Context: `object_list` (changed from `receipts`), `stats`, `page_title`, `breadcrumbs`, `table_headers`, `show_actions`, `empty_state_title`, `empty_state_message`, `empty_state_icon`, `print_enabled`, `show_filters`
  - Overridden Blocks:
    - `breadcrumb_extra`: QC > Temporary Receipts
    - `before_table`: Stats cards (Awaiting QC, Approved, Rejected, Total) and custom styles
    - `table_headers`: Document Code, Document Date, Items, Quantity, Warehouses, Supplier, Created By, Status, Actions
    - `table_rows`: Display receipt details with status badges and conditional action buttons
  - Special Features:
    - Stats cards (Awaiting QC, Approved, Rejected, Total)
    - Status badges (Awaiting QC, QC Approved, QC Rejected, Locked)
    - Action buttons (Approve Lines, Reject, Manage Rejection Reasons) based on lock status
    - Display multiple lines per receipt

---

## فاز 2: Special Pages (نیازی به migration ندارند)

### ❌ Temporary Receipt Line Selection
- [ ] `TemporaryReceiptQCLineSelectionView` - TemplateView با ساختار خاص برای انتخاب خطوط و مقادیر

### ❌ Temporary Receipt Rejection Management
- [ ] `TemporaryReceiptQCRejectionManagementView` - TemplateView با ساختار خاص برای مدیریت دلایل رد

### ❌ Approval/Reject Actions
- [ ] `TemporaryReceiptQCApproveView` - View برای approve (POST only)
- [ ] `TemporaryReceiptQCRejectView` - View برای reject (POST only)
- [ ] `TemporaryReceiptQCRejectionManagementSaveView` - View برای save rejection reasons (POST only)

**نکته**: این صفحات خاص هستند و ساختار منحصر به فرد دارند. آنها از `TemplateView` یا `View` استفاده می‌کنند و نمی‌توانند به `generic_list.html` یا `generic_form.html` migrate شوند.

---

**پیشرفت کلی:**
- **انجام شده:** 1 template از ~1 (100%) ✅
  - List templates: 1 ✅ (Temporary Receipts QC List)
- **باقی مانده:** 
  - Special Pages - صفحات خاص با ساختار منحصر به فرد که نیاز به migration ندارند:
    - `TemporaryReceiptQCLineSelectionView` (TemplateView)
    - `TemporaryReceiptQCRejectionManagementView` (TemplateView)
    - Approval/Reject Actions (POST-only Views)

**آخرین به‌روزرسانی:** 
- ✅ Temporary Receipts QC List به `shared/generic/generic_list.html` migrate شد
- ✅ Context variable از `receipts` به `object_list` تغییر یافت
- ✅ Template blocks به درستی override شدند
- ✅ README views به‌روزرسانی شد با اطلاعات migration
- ✅ ماژول QC 100% تکمیل شد 

