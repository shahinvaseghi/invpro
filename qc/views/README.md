# qc/views/ - Views Documentation

این پوشه شامل تمام views ماژول QC است.

## فایل‌ها

### base.py
- **README**: [README_BASE.md](README_BASE.md)
- **توضیح**: کلاس پایه (QCBaseView)

### inspections.py
- **README**: [README_INSPECTIONS.md](README_INSPECTIONS.md)
- **Views**: 
  - TemporaryReceiptQCListView: فهرست رسیدهای موقت در انتظار بازرسی
  - TemporaryReceiptQCLineSelectionView: انتخاب خطوط و مقادیر برای تایید QC
  - TemporaryReceiptQCApproveView: تایید بازرسی رسید موقت
  - TemporaryReceiptQCRejectView: رد بازرسی رسید موقت
  - TemporaryReceiptQCRejectionManagementView: مدیریت دلایل رد
  - TemporaryReceiptQCRejectionManagementSaveView: ذخیره دلایل رد
- **توضیح**: Views برای مدیریت بازرسی‌های QC

#### Template Migration Status

**Generic Templates**:
- **TemporaryReceiptQCListView**: 
  - Template: `qc/temporary_receipts.html` extends `shared/generic/generic_list.html` ✅
  - Context variable: `object_list` (changed from `receipts`)
  - Overridden blocks: `breadcrumb_extra`, `before_table`, `table_headers`, `table_rows`

**Special Pages** (نیازی به migration ندارند):
- `TemporaryReceiptQCLineSelectionView`: TemplateView با ساختار خاص برای انتخاب خطوط
- `TemporaryReceiptQCRejectionManagementView`: TemplateView با ساختار خاص برای مدیریت دلایل رد
- Approval/Reject Actions: View های POST-only که نیاز به template ندارند

---

## الگوهای مشترک

تمام views از الگوهای مشترک زیر پیروی می‌کنند:

1. **Base Class**: از `QCBaseView` استفاده می‌کنند
2. **Company Filtering**: به صورت خودکار بر اساس `active_company_id` فیلتر می‌شوند
3. **Permission Checking**: از `FeaturePermissionRequiredMixin` برای بررسی مجوزها استفاده می‌کنند
4. **Workflow**: Approve/Reject views workflow تایید/رد دارند
5. **Generic Templates**: List views از `shared/generic/generic_list.html` استفاده می‌کنند

---

## مستندات کامل

برای جزئیات کامل هر view، به کد منبع مراجعه کنید.

